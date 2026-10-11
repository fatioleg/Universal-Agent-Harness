#!/usr/bin/env python3
"""UAH-lite guard — hook do Claude Code (PreToolUse, SessionStart, Stop).

Lê a política compilada em `.uah/policy.json` e decide por ferramenta.
Somente biblioteca padrão: precisa rodar em qualquer máquina sem venv.

Ordem de decisão (PreToolUse):
  1. bash_deny (H0..H3)                 -> deny
  2. escrita em immutable_paths         -> deny
  3. bash_ask com locked=true           -> ask (nenhuma concessão pula)
  4. gate de plano (G1) não satisfeito  -> deny para ação material
  5. concessão temporária H3 válida     -> allow (só se TODOS os segmentos do comando casam inteiros)
  6. bash_ask / protected_paths         -> ask
  7. nada casou                         -> sem opinião (fluxo normal)

Qualquer erro interno em PreToolUse vira deny (fail-closed).

Limite conhecido: a análise de Bash é heurística (defesa em profundidade
contra deriva do agente, não contra um adversário determinado). As regras
`permissions` do settings.json compiladas pelo uah.py são a segunda camada.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

GUARD_VERSION = "0.9.0"

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
MUTATING_ALL_ARGS = {"rm", "rmdir", "unlink", "shred", "truncate", "chmod", "chown", "touch", "tee", "mv"}
MUTATING_LAST_ARG = {"cp", "rsync", "ln", "install"}
TARGET_DIR_CMDS = {"cp", "mv", "ln", "install"}       # aceitam -t DIR / --target-directory=DIR
TRUSTED_BIN_DIRS = {"/usr/bin", "/bin", "/usr/local/bin", "/usr/sbin", "/sbin"}
# Exceção de bootstrap quando a política está ausente: só subcomandos que não ampliam permissões.
BOOTSTRAP_UAH_SUBCOMMANDS = {"compile", "init", "preflight", "status", "explain"}
IN_PLACE_EDITORS = {"sed", "perl"}
GIT_MUTATING = {"rm", "mv", "checkout", "restore", "clean"}
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
PUNCT = ";&|<>()\n"
WRAPPERS = {"sudo", "env", "nohup", "time", "command", "exec", "nice", "xargs"}
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?(?:^|\n)\s*\2[ \t]*(?=\n|$)", re.S)


# --------------------------------------------------------------------- util

def project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(os.path.realpath(env))
    return Path(os.path.realpath(Path(__file__).parents[2]))


def load_policy(root: Path) -> dict | None:
    try:
        data = json.loads((root / ".uah" / "policy.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            rest = text[end + 4:]
            return text[4:end], rest[1:] if rest.startswith("\n") else rest
    return "", text


def parse_flat_yaml(block: str) -> dict:
    out = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "#", "-")):
            key, value = line.split(":", 1)
            value = value.strip()
            if value.startswith('"'):
                try:
                    value = json.loads(value)
                except ValueError:
                    value = value.strip('"')
            else:
                value = value.strip("'")
            out[key.strip()] = value
    return out


def plan_body_sha(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    _, body = split_frontmatter(text)
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()


def plan_status(root: Path) -> tuple[str, str]:
    """Retorna (approved|pending|modified|missing, revisão curta)."""
    plan = root / "plan" / "approved.md"
    if not plan.is_file():
        return "missing", ""
    try:
        lock = json.loads((root / ".uah" / "plan.lock.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "pending", ""
    current = plan_body_sha(plan)
    if not (current and lock.get("sha256") == current):
        return "modified", str(lock.get("sha256", ""))[:12]
    # Fatias: depois da primeira, a execução exige fatia ativa, aprovada e inalterada.
    try:
        slices = json.loads((root / ".uah" / "slices.lock.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "approved", current[:12]
    if not isinstance(slices, dict) or not slices.get("mode"):
        return "approved", current[:12]
    active = slices.get("active")
    if not active:
        return "no-slice", current[:12]
    entry = (slices.get("approved") or {}).get(str(active))
    slice_sha = plan_body_sha(root / "plan" / "slices" / f"slice-{active}.md")
    if not entry:
        return "slice-pending", str(active)
    if entry.get("sha256") != slice_sha:
        return "slice-modified", str(active)
    return "approved", f"{current[:12]} · fatia {active}"


def glob_to_regex(glob: str) -> re.Pattern:
    glob = glob[2:] if glob.startswith("./") else glob
    glob = glob.rstrip("/") or glob
    out, i = "", 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif glob.startswith("**", i):
            out += ".*"
            i += 2
        elif glob[i] == "*":
            out += "[^/]*"
            i += 1
        elif glob[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(glob[i])
            i += 1
    if glob.endswith("/**"):
        out = f"(?:{out}|{re.escape(glob[:-3])})"
    elif not any(ch in glob for ch in "*?["):
        out = f"{out}(?:/.*)?"  # diretório literal protege o conteúdo
    return re.compile(f"^{out}$")


def matches_any(rel: str, globs: list[str]) -> str | None:
    for glob in globs:
        if glob_to_regex(glob).match(rel):
            return glob
    return None


def to_rel(root: Path, raw: str, cwd: Path) -> str | None:
    if not raw:
        return None
    raw = os.path.expanduser(os.path.expandvars(raw))
    path = Path(raw)
    if not path.is_absolute():
        path = cwd / path
    real = Path(os.path.realpath(path))
    try:
        return real.relative_to(root).as_posix() or "."
    except ValueError:
        return None


def now_utc() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def parse_time(value: str) -> _dt.datetime | None:
    try:
        parsed = _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    return parsed


def emit(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"[UAH-lite] {reason}",
        }
    }, ensure_ascii=False))
    sys.exit(0)


# --------------------------------------------------------------- bash parse

def lex(command: str) -> list[str] | None:
    """Tokens com operadores/redirecionamentos reconhecidos só fora de aspas; None se ilegível."""
    command = HEREDOC_RE.sub(lambda m: m.group(0).split("\n", 1)[0], command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars=PUNCT)
    lexer.whitespace = " \t\r"
    lexer.commenters = ""
    lexer.wordchars += ":#@%+,{}[]^!$`~"
    try:
        return list(lexer)
    except ValueError:
        return None


def normalized(command: str) -> str | None:
    """Comando reconstruído a partir dos tokens do shell: remove aspas e escapes que fragmentam palavras
    (a''pprove, g\\it, "cu"rl), para as regras regex enxergarem o que o shell executará."""
    toks = lex(command)
    if toks is None:
        return None
    return " ".join(toks)


def rule_views(command: str) -> list[str]:
    views = [command]
    norm = normalized(command)
    if norm is not None and norm != command:
        views.append(norm)
    return views


def is_punct(tok: str) -> bool:
    return bool(tok) and all(ch in PUNCT for ch in tok)


def parse(command: str) -> list[dict] | None:
    """Segmentos: {'args': [...], 'redirects': [alvos]}; None se o comando não pôde ser lido."""
    toks = lex(command)
    if toks is None:
        return None
    segs, cur = [], {"args": [], "redirects": []}
    i = 0
    while i < len(toks):
        tok = toks[i]
        if is_punct(tok) and ">" in tok:
            nxt = toks[i + 1] if i + 1 < len(toks) else ""
            if cur["args"] and cur["args"][-1].isdigit():
                cur["args"].pop()  # descritor (2>…)
            if tok.endswith("&") and (nxt.isdigit() or nxt == "-"):
                i += 2  # duplicação de descritor (>&2)
                continue
            if nxt and not is_punct(nxt):
                cur["redirects"].append(nxt)
                i += 2
                continue
            i += 1
            continue
        if is_punct(tok) and "<" in tok:
            i += 2  # entrada / heredoc: o operando não é escrito
            continue
        if is_punct(tok):
            if cur["args"] or cur["redirects"]:
                segs.append(cur)
            cur = {"args": [], "redirects": []}
            i += 1
            continue
        cur["args"].append(tok)
        i += 1
    if cur["args"] or cur["redirects"]:
        segs.append(cur)
    for seg in segs:
        args = seg["args"]
        while args and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", args[0]):
            args.pop(0)
        while args and args[0] in WRAPPERS:
            args.pop(0)
            while args and args[0].startswith("-"):
                args.pop(0)
    return segs


def segment_texts(command: str) -> list[str] | None:
    segs = parse(command)
    if segs is None:
        return None
    return [" ".join(s["args"]) for s in segs if s["args"]]


def trusted_exe(tok: str) -> str | None:
    """Nome do executável só se for um comando do PATH (sem barra) ou um caminho em diretório de sistema.
    `./cat` ou `scripts/cat` não são o `cat` do sistema."""
    if "/" not in tok:
        return tok
    real = os.path.realpath(os.path.expanduser(tok))
    return os.path.basename(real) if os.path.dirname(real) in TRUSTED_BIN_DIRS else None


def target_dirs(toks: list[str]) -> list[str]:
    out = []
    for j, t in enumerate(toks[1:], 1):
        if (t == "--target-directory" or re.fullmatch(r"-[A-Za-z]*t", t)) and j + 1 < len(toks):
            out.append(toks[j + 1])  # -t DIR, -st DIR, --target-directory DIR
        elif t.startswith("--target-directory="):
            out.append(t.split("=", 1)[1])
        elif re.match(r"^-[A-Za-z]*t.+", t) and not t.startswith("--"):
            out.append(t[t.index("t") + 1:])
    return out


def git_subcommand(args: list[str]) -> tuple[str, list[str]]:
    i = 1
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_GLOBAL_WITH_VALUE else 1
    return (args[i], args[i + 1:]) if i < len(args) else ("", [])


def write_targets(seg: dict) -> list[str]:
    targets = list(seg["redirects"])
    toks = seg["args"]
    if not toks:
        return targets
    cmd = os.path.basename(toks[0])
    args = [t for t in toks[1:] if not t.startswith("-")]
    if cmd in TARGET_DIR_CMDS:
        tdirs = target_dirs(toks)
        if tdirs:
            targets += tdirs
            values = set(tdirs)
            args = [a for a in args if a not in values]
            if cmd == "mv":
                targets += args  # mv -t DIR origem…: as origens também são removidas
            return [t for t in targets if t and t != "/dev/null"]
    if cmd in MUTATING_ALL_ARGS:
        targets += args
    elif cmd in MUTATING_LAST_ARG and args:
        targets.append(args[-1])
    elif cmd in IN_PLACE_EDITORS and any(re.match(r"-[A-Za-z]*i", t) or t.startswith("--in-place") for t in toks[1:]):
        targets += args
    elif cmd == "sort":
        for j, t in enumerate(toks):
            if t == "-o" and j + 1 < len(toks):
                targets.append(toks[j + 1])
            elif t.startswith("--output="):
                targets.append(t.split("=", 1)[1])
            elif t.startswith("-o") and len(t) > 2:
                targets.append(t[2:])
    elif cmd == "git":
        sub, rest = git_subcommand(toks)
        if sub in GIT_MUTATING:
            targets += [t for t in rest if not t.startswith("-")]
    elif cmd == "find" and any(t in {"-delete", "-exec", "-execdir"} for t in toks):
        targets += args[:1]
    return [t for t in targets if t and t != "/dev/null"]


def is_uah_cli(token: str, root: Path) -> bool:
    try:
        real = Path(os.path.realpath(os.path.expanduser(token)))
    except (OSError, ValueError):
        return False
    allowed = {Path(os.path.realpath(root / ".uah" / "uah.py")),
               Path(os.path.realpath(Path.home() / ".claude" / "skills" / "uah-init" / "uah.py"))}
    return real in allowed or (not os.path.isabs(token) and Path(os.path.realpath(root / token)) in allowed)


def gate_cli_allowed(script: str, subcommand: str, policy: dict, root: Path) -> bool:
    """O script precisa estar DENTRO da pasta da skill instalada e verificada da integração — não basta o nome."""
    real = Path(os.path.realpath(os.path.expanduser(script if os.path.isabs(script) or script.startswith("~")
                                                     else str(root / script))))
    installed = {i.get("id"): i for i in policy.get("integrations", [])}
    for g in policy.get("gate_cli", []):
        if real.name != g.get("script") or subcommand not in g.get("subcommands", []):
            continue
        item = installed.get(g.get("integration")) or {}
        base = item.get("path")
        if not base or not item.get("verified"):
            continue
        try:
            real.relative_to(Path(os.path.realpath(base)))
            return True
        except ValueError:
            continue
    return False


def uah_subcommand(args: list[str]) -> str | None:
    i = 2
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] == "--root" else 1
    return args[i] if i < len(args) else None


def is_readonly(command: str, policy: dict, root: Path) -> bool:
    if "$(" in command or "`" in command:
        return False
    segs = parse(command)
    if segs is None:
        return False
    simple = set(policy.get("readonly_bash", []))
    subs = policy.get("readonly_bash_subcommands", {})
    for seg in segs:
        if write_targets(seg):
            return False
        toks = seg["args"]
        if not toks:
            continue
        cmd = trusted_exe(toks[0])
        if cmd is None:
            return False
        if cmd in simple or cmd in {"cd", "pushd", "popd", "true"}:
            continue
        if cmd == "sed" and not any(re.match(r"-[A-Za-z]*i", t) or t.startswith("--in-place") for t in toks[1:]):
            continue
        if cmd == "awk" and not any("system" in t or ">" in t or "|" in t for t in toks[1:]):
            continue
        if cmd == "find":
            if any(t in {"-delete", "-exec", "-execdir", "-ok", "-fprint", "-fprintf", "-fls"} for t in toks):
                return False
            continue
        if cmd == "git":
            sub, rest = git_subcommand(toks)
            if sub not in subs.get("git", []):
                return False
            if sub == "branch" and any(t.split("=")[0] in {"-d", "-D", "-m", "-M", "-c", "-C", "--delete",
                                                            "--move", "--copy", "-f", "--force", "-u",
                                                            "--set-upstream-to", "--unset-upstream"} for t in rest):
                return False
            if sub == "branch" and [t for t in rest if not t.startswith("-")] and "--list" not in rest \
                    and not any(t in {"-a", "-r", "-v", "-vv", "--all", "--remotes", "--show-current",
                                      "--contains", "--merged", "--no-merged"} for t in rest):
                return False  # `git branch nome` cria branch
            if sub == "remote" and rest and rest[0] not in {"-v", "--verbose", "show", "get-url"}:
                return False
            continue
        if cmd.startswith("python") and len(toks) > 1 and is_uah_cli(toks[1], root):
            continue
        if cmd.startswith("python") and len(toks) > 2 and gate_cli_allowed(toks[1], toks[2], policy, root):
            continue  # CLI de planejamento/leitura de integração ativa, instalada e de origem verificada
        return False
    return True


GATE_MESSAGES = {
    "missing": "não há plan/approved.md",
    "pending": "o plano ainda não foi aprovado",
    "modified": "o plano mudou depois da aprovação",
    "no-slice": "o projeto usa fatias e nenhuma está ativa (aprove a próxima: `uah.py approve --slice N`)",
    "slice-pending": "a fatia ativa ainda não foi aprovada",
    "slice-modified": "a fatia ativa mudou depois da aprovação",
}


# --------------------------------------------------------------- decisions

def regex_hit(rules: list[dict], command: str) -> dict | None:
    """Testa as regras no texto bruto E na forma normalizada pelo shell (sem aspas/escapes)."""
    views = rule_views(command)
    for rule in rules:
        try:
            if any(re.search(rule["pattern"], view) for view in views):
                return rule
        except re.error:
            continue
    return None


def valid_grants(policy: dict) -> list[dict]:
    out = []
    for grant in policy.get("temporary_grants", []):
        expires = parse_time(grant.get("expires_at", ""))
        if expires and expires > now_utc():
            out.append(grant)
    return out


def grant_covering(policy: dict, command: str) -> dict | None:
    """A concessão só vale se cada segmento do comando casa por inteiro com alguma concessão."""
    grants = valid_grants(policy)
    texts = segment_texts(command)
    if not grants or not texts or "$(" in command or "`" in command:
        return None
    used = None
    for text in texts:
        hit = None
        for grant in grants:
            try:
                if re.fullmatch(grant["pattern"].lstrip("^").rstrip("$"), text):
                    hit = grant
                    break
            except re.error:
                continue
        if hit is None:
            return None
        used = used or hit
    return used


def attempts_blocked(root: Path) -> str | None:
    """Id da tarefa travada pelo limite de tentativas falhas (state/current.md), ou None."""
    try:
        fm, _ = split_frontmatter((root / "state" / "current.md").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    meta = parse_flat_yaml(fm)
    if str(meta.get("blocked_by_attempts", "")).lower() == "true":
        return str(meta.get("task_id") or "?")
    return None


def outside_allowed(raw: str, cwd: Path) -> bool:
    """Fora do projeto, só a área temporária do sistema fica sem confirmação."""
    import tempfile
    path = Path(os.path.expanduser(raw))
    real = Path(os.path.realpath(path if path.is_absolute() else cwd / path))
    for base in {tempfile.gettempdir(), "/tmp"}:
        try:
            real.relative_to(Path(os.path.realpath(base)))
            return True
        except ValueError:
            continue
    return False


def bash_write_rels(command: str, root: Path, cwd: Path) -> list[str] | None:
    segs = parse(command)
    if segs is None:
        return None
    rels, here = [], cwd
    for seg in segs:
        toks = seg["args"]
        if toks and toks[0] == "cd":
            dest = toks[1] if len(toks) > 1 else str(Path.home())
            dest = os.path.expanduser(dest)
            here = Path(dest) if os.path.isabs(dest) else here / dest
            continue
        for target in write_targets(seg):
            rel = to_rel(root, target, here)
            if rel:
                rels.append(rel)
    return rels


def pre_tool_use(payload: dict) -> None:
    root = project_root()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or root)
    policy = load_policy(root)
    command = tool_input.get("command", "") if tool == "Bash" else ""

    if policy is None:
        segs = parse(command) if command else None
        if tool == "Bash" and segs and "$(" not in command and "`" not in command and all(
                s["args"] and (trusted_exe(s["args"][0]) or "").startswith("python") and len(s["args"]) > 1
                and is_uah_cli(s["args"][1], root) and uah_subcommand(s["args"]) in BOOTSTRAP_UAH_SUBCOMMANDS
                and not s["redirects"] for s in segs):
            sys.exit(0)
        if tool == "Bash" or tool in WRITE_TOOLS:
            emit("deny", "política .uah/policy.json ausente ou inválida; rode `python3 .uah/uah.py compile`.")
        sys.exit(0)

    immutable = policy.get("immutable_paths", [])
    protected = policy.get("protected_paths", [])
    gate_on = bool(policy.get("plan_gate"))
    plan_state = plan_status(root)[0] if gate_on else "approved"
    gate_msg = GATE_MESSAGES.get(plan_state, "")
    stuck = attempts_blocked(root)
    stuck_msg = (f"tarefa {stuck} BLOQUEADA após o limite de tentativas falhas — pare e peça ao humano para decidir "
                 "(`uah.py checkpoint --task … --reset-attempts`)") if stuck else ""

    if tool == "Bash":
        hit = regex_hit(policy.get("bash_deny", []), command)
        if hit:
            emit("deny", f"{hit['id']}: {hit.get('reason', 'bloqueado por política')}.")
        rels = bash_write_rels(command, root, cwd)
        for rel in rels or []:
            if matches_any(rel, immutable):
                emit("deny", f"`{rel}` é imutável por política (escrita/remoção bloqueada).")
        locked = [r for r in policy.get("bash_ask", []) if r.get("locked")]
        hit = regex_hit(locked, command)
        if hit:
            emit("ask", f"{hit['id']}: {hit.get('reason', 'confirmação humana exigida')}.")
        if plan_state != "approved" and not is_readonly(command, policy, root):
            emit("deny", f"gate G1: {gate_msg}. Só leitura e comandos do uah.py até a aprovação "
                         "(`/uah-init approve`).")
        if stuck and not is_readonly(command, policy, root):
            emit("deny", stuck_msg + ". Só leitura, edição do plano e comandos do uah.py.")
        if rels is None:
            emit("ask", "comando não pôde ser analisado (aspas desbalanceadas?); confirme.")
        grant = grant_covering(policy, command)
        if grant:
            emit("allow", f"concessão temporária H3 `{grant['id']}` válida até {grant['expires_at']}.")
        hit = regex_hit(policy.get("bash_ask", []), command)
        if hit:
            emit("ask", f"{hit['id']}: {hit.get('reason', 'confirmação exigida')}.")
        for rel in rels:
            if matches_any(rel, protected):
                emit("ask", f"`{rel}` é protegido; confirme a alteração.")
        sys.exit(0)

    if tool in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        rel = to_rel(root, raw, cwd)
        if rel is None:
            if not raw:
                emit("deny", "ferramenta de escrita sem caminho de arquivo (fail-closed).")
            if outside_allowed(raw, cwd):
                sys.exit(0)
            if plan_state != "approved":
                emit("deny", f"gate G1: {gate_msg}. Escrita fora do projeto bloqueada até a aprovação: {raw}")
            emit("ask", f"escrita FORA do projeto ({raw}); confirme.")
        if matches_any(rel, immutable):
            emit("deny", f"`{rel}` é imutável por política. Para mudar regras, edite project.yaml e rode compile.")
        if stuck and not matches_any(rel, policy.get("plan_gate_paths", [])):
            emit("deny", stuck_msg + f". Só é permitido editar {', '.join(policy.get('plan_gate_paths', []))}.")
        if plan_state != "approved" and not matches_any(rel, policy.get("plan_gate_paths", [])):
            emit("deny", f"gate G1: {gate_msg}. Antes da aprovação só é permitido editar "
                         f"{', '.join(policy.get('plan_gate_paths', []))}.")
        if matches_any(rel, protected):
            emit("ask", f"`{rel}` é protegido; confirme a alteração.")
    sys.exit(0)


# ------------------------------------------------------------ session start

def session_start(_payload: dict) -> None:
    root = project_root()
    policy = load_policy(root)
    lines = []
    if policy is None:
        print("[UAH-lite] ATENÇÃO: .uah/policy.json ausente ou inválida. Rode `python3 .uah/uah.py compile`.")
        return
    meta = policy.get("project", {})
    lines.append(f"[UAH-lite {GUARD_VERSION}] projeto `{meta.get('id', '?')}` · risco {policy.get('risk', '?')} · "
                 f"política {str(policy.get('resolution_hash', ''))[:12]}")
    state, rev = plan_status(root)
    label = {"approved": f"APROVADO (rev {rev})", "pending": "PENDENTE de aprovação",
             "modified": f"MODIFICADO após a aprovação (aprovado: {rev}) — reaprovar",
             "missing": "inexistente",
             "no-slice": f"geral aprovado (rev {rev}); NENHUMA fatia ativa",
             "slice-pending": f"geral aprovado; fatia {rev} PENDENTE de aprovação",
             "slice-modified": f"geral aprovado; fatia {rev} MODIFICADA após a aprovação — reaprovar"}[state]
    gate = " · gate G1 ativo" if policy.get("plan_gate") and state != "approved" else ""
    lines.append(f"Plano: {label}{gate}")
    try:
        fm, _ = split_frontmatter((root / "state" / "current.md").read_text(encoding="utf-8"))
        st = parse_flat_yaml(fm)
        lines.append(f"Estado: tarefa {st.get('task_id') or '-'}"
                     + (f" · fatia {st.get('slice')}" if st.get("slice") else "")
                     + f" · {st.get('status') or '-'} · "
                     f"próximo: {st.get('next_action') or '-'} · bloqueios: {st.get('blockers') or 'nenhum'} · "
                     f"atualizado {st.get('updated_at') or '-'}")
    except (OSError, ValueError):
        lines.append("Estado: state/current.md ausente ou ilegível.")
    if attempts_blocked(root):
        lines.append(f"PARE: a tarefa {attempts_blocked(root)} atingiu o limite de tentativas falhas; alterações materiais "
                     "bloqueadas até um humano decidir (`checkpoint --reset-attempts`).")
    warnings = []
    for key, rel in (("H2", "project.yaml"), ("H3", ".uah/task.yaml")):
        recorded = (policy.get("sources", {}).get(key) or {}).get("sha256")
        current = sha256_file(root / rel)
        if recorded != current:
            warnings.append(f"`{rel}` mudou desde o último compile → rode `python3 .uah/uah.py compile`")
    for grant in policy.get("temporary_grants", []):
        if grant not in valid_grants(policy):
            warnings.append(f"concessão H3 `{grant['id']}` expirada (inativa)")
    for item in policy.get("integrations", []):
        installed = item.get("installed")
        lines.append(f"Integração `{item.get('id')}` ({'instalada' if installed else 'NÃO instalada'}) — "
                     f"{item.get('stage')}: {item.get('when')} Como: {item.get('how')}")
        if not installed:
            warnings.append(f"integração {item.get('id')} ativa mas não instalada (`uah.py integrations install {item.get('id')}`)")
    if warnings:
        lines.append("Avisos: " + "; ".join(warnings))
    lines.append("Antes de agir: leia state/current.md e plan/approved.md. Fonte de verdade = arquivos "
                 "versionados > plano aprovado > memórias (Claude/OMC/ai-memory).")
    print("\n".join(lines))


# --------------------------------------------------------------------- stop

STOP_IGNORED = ("state/", ".uah/", ".omc/", ".claude/")


def porcelain_entries(root: Path) -> list[tuple[str, str]] | None:
    """[(status XY, caminho)] via `git status --porcelain -z` (sem aspas, aceita acentos)."""
    try:
        out = subprocess.run(["git", "-c", "core.quotePath=false", "status", "--porcelain", "-z"], cwd=root,
                             capture_output=True, timeout=10, check=True).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError):
        return None
    parts = out.split("\0")
    entries, i = [], 0
    while i < len(parts):
        item = parts[i]
        if len(item) > 3:
            xy, path = item[:2], item[3:]
            entries.append((xy, path))
            if "R" in xy or "C" in xy:
                i += 1  # caminho de origem do rename
        i += 1
    return entries


def git_ok(root: Path) -> bool:
    try:
        return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True,
                              timeout=10).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def committed_since(root: Path, since: float) -> tuple[set[str], float]:
    """Arquivos alterados em commits feitos depois de `since` (epoch) e o instante do commit mais novo."""
    try:
        out = subprocess.run(["git", "-c", "core.quotePath=false", "log", f"--since=@{int(since)}",
                              "--name-only", "--format=@@%ct"], cwd=root, capture_output=True, timeout=15,
                             check=True).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError):
        return set(), 0.0
    files, newest = set(), 0.0
    for line in out.splitlines():
        if line.startswith("@@"):
            newest = max(newest, float(line[2:] or 0))
        elif line.strip():
            files.add(line.strip())
    return files, newest


def newest_change(root: Path, state_mtime: float) -> float:
    """Instante da alteração mais nova fora de state/.uah/.omc/.claude — inclui o que já foi commitado."""
    newest = 0.0
    if git_ok(root):
        changed = {rel for _xy, rel in (porcelain_entries(root) or [])}
        commits, commit_time = committed_since(root, state_mtime)
        for rel in changed | commits:
            if rel.startswith(STOP_IGNORED):
                continue
            try:
                newest = max(newest, (root / rel).stat().st_mtime)
            except OSError:  # removido: vale o instante do commit (ou agora, se não commitado)
                newest = max(newest, commit_time if rel in commits else now_utc().timestamp())
        return newest
    # Sem git: varre o projeto (limitado) — G4 não pode simplesmente liberar.
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d != ".git" and not (os.path.normpath(os.path.join(rel_dir, d)) + "/").startswith(STOP_IGNORED)]
        for name in filenames:
            count += 1
            if count > 20000:
                return now_utc().timestamp()  # projeto grande demais para varrer: exige checkpoint
            try:
                newest = max(newest, os.stat(os.path.join(dirpath, name)).st_mtime)
            except OSError:
                continue
    return newest


def stop(payload: dict) -> None:
    root = project_root()
    policy = load_policy(root)
    if not policy or policy.get("g4_checkpoint") != "block" or payload.get("stop_hook_active"):
        return
    try:
        state_mtime = (root / "state" / "current.md").stat().st_mtime
    except OSError:
        state_mtime = 0.0
    newest = newest_change(root, state_mtime)
    if not newest or state_mtime >= newest:
        return
    print(json.dumps({
        "decision": "block",
        "reason": "[UAH-lite] G4: há alterações (inclusive já commitadas) mais novas que state/current.md. "
                  "Antes de encerrar, rode `python3 .uah/uah.py checkpoint --task <T-xxx> --status "
                  "<active|paused|blocked|done> --next \"<próxima ação>\"` (e --blocker se houver).",
    }, ensure_ascii=False))


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            if event == "pre-tool-use":
                emit("deny", "entrada do hook ilegível (fail-closed).")
            payload = {}
        if event == "pre-tool-use":
            pre_tool_use(payload)
        elif event == "session-start":
            session_start(payload)
        elif event == "stop":
            stop(payload)
        else:
            print(f"uso: {Path(__file__).name} pre-tool-use|session-start|stop", file=sys.stderr)
            sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:  # fail-closed: erro interno nunca libera a ferramenta
        if event == "pre-tool-use":
            emit("deny", f"erro interno do guard ({type(exc).__name__}: {exc}); corrija antes de prosseguir.")
        print(f"[UAH-lite] erro interno no hook {event}: {type(exc).__name__}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
