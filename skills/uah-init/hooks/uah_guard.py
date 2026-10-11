#!/usr/bin/env python3
"""UAH-lite guard — hook do Claude Code (PreToolUse, SessionStart, Stop).

Lê a política compilada em `.uah/policy.json` e decide por ferramenta.
Somente biblioteca padrão: precisa rodar em qualquer máquina sem venv.

Ordem de decisão (PreToolUse):
  1. bash_deny (H0..H3)                 -> deny
  2. escrita em immutable_paths         -> deny
  3. bash_ask com locked=true           -> ask (nenhuma concessão pula)
  4. gate de plano (G1) não satisfeito  -> deny para ação material
  5. concessão temporária H3 válida     -> allow
  6. bash_ask / protected_paths         -> ask
  7. nada casou                         -> sem opinião (fluxo normal)

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

GUARD_VERSION = "0.6.0"

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
MUTATING_ALL_ARGS = {"rm", "rmdir", "unlink", "shred", "truncate", "chmod", "chown", "touch", "tee", "mv"}
MUTATING_LAST_ARG = {"cp", "rsync", "ln", "install"}
IN_PLACE_EDITORS = {"sed", "perl"}
GIT_MUTATING = {"rm", "mv", "checkout", "restore", "clean"}
REDIRECT_RE = re.compile(r"(?<![0-9&<>])(?:[0-9]?>{1,2}|&>)\s*(?!&)([^\s;&|]+)")


# --------------------------------------------------------------------- util

def project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


def load_policy(root: Path) -> dict | None:
    try:
        return json.loads((root / ".uah" / "policy.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


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
            out[key.strip()] = value.strip().strip("'\"")
    return out


def plan_body_sha(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
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
    if lock.get("sha256") and lock.get("sha256") == current:
        return "approved", current[:12]
    return "modified", str(lock.get("sha256", ""))[:12]


def glob_to_regex(glob: str) -> re.Pattern:
    glob = glob[2:] if glob.startswith("./") else glob
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
    base = ""
    if glob.endswith("/**"):
        base = "|" + re.escape(glob[:-3])
    return re.compile(f"^(?:{out}{base})$")


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
    try:
        path = Path(os.path.normpath(str(path)))
        return path.relative_to(root).as_posix() or "."
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

def segments(command: str) -> list[str]:
    return [s.strip() for s in re.split(r"&&|\|\||;|\||\n", command) if s.strip()]


def tokens_of(segment: str) -> list[str]:
    try:
        toks = shlex.split(segment, comments=False, posix=True)
    except ValueError:
        toks = segment.split()
    while toks and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", toks[0]):
        toks = toks[1:]
    while toks and toks[0] in {"sudo", "env", "nohup", "time", "command", "exec"}:
        toks = toks[1:]
    return toks


def write_targets(segment: str) -> list[str]:
    targets = [m.group(1) for m in REDIRECT_RE.finditer(segment)]
    toks = tokens_of(REDIRECT_RE.sub(" ", segment))
    if not toks:
        return targets
    cmd = os.path.basename(toks[0])
    args = [t for t in toks[1:] if not t.startswith("-")]
    if cmd in MUTATING_ALL_ARGS:
        targets += args
    elif cmd in MUTATING_LAST_ARG and args:
        targets.append(args[-1])
    elif cmd in IN_PLACE_EDITORS and any(t.startswith("-i") or t == "--in-place" for t in toks[1:]):
        targets += args
    elif cmd == "git" and len(toks) > 1 and toks[1] in GIT_MUTATING:
        targets += [t for t in toks[2:] if not t.startswith("-")]
    elif cmd == "find" and any(t in {"-delete", "-exec", "-execdir"} for t in toks):
        targets += [t for t in toks[1:] if not t.startswith("-")][:1]
    return [t for t in targets if t and t != "/dev/null"]


def is_readonly(command: str, policy: dict) -> bool:
    simple = set(policy.get("readonly_bash", []))
    subs = policy.get("readonly_bash_subcommands", {})
    for seg in segments(command):
        if [t for t in write_targets(seg)]:
            return False
        toks = tokens_of(seg)
        if not toks:
            continue
        cmd = os.path.basename(toks[0])
        if cmd in simple:
            continue
        if cmd == "find" and "find" in subs:
            if any(t in {"-delete", "-exec", "-execdir", "-fprint", "-fprintf", "-fls"} for t in toks):
                return False
            continue
        if cmd in subs and len(toks) > 1:
            allowed = subs[cmd]
            if cmd.startswith("python"):
                if toks[1].endswith("uah.py"):
                    continue
                return False
            if toks[1] in allowed:
                continue
        return False
    return True


# --------------------------------------------------------------- decisions

def regex_hit(rules: list[dict], command: str) -> dict | None:
    for rule in rules:
        try:
            if re.search(rule["pattern"], command):
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


def pre_tool_use(payload: dict) -> None:
    root = project_root()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or root)
    policy = load_policy(root)
    command = tool_input.get("command", "") if tool == "Bash" else ""

    if policy is None:
        if tool == "Bash" and "uah.py" in command:
            sys.exit(0)
        if tool == "Bash" or tool in WRITE_TOOLS:
            emit("deny", "política .uah/policy.json ausente ou inválida; rode `python3 .uah/uah.py compile`.")
        sys.exit(0)

    immutable = policy.get("immutable_paths", [])
    protected = policy.get("protected_paths", [])
    gate_on = bool(policy.get("plan_gate"))
    plan_state = plan_status(root)[0] if gate_on else "approved"
    gate_msg = {
        "missing": "não há plan/approved.md",
        "pending": "o plano ainda não foi aprovado",
        "modified": "o plano mudou depois da aprovação",
    }.get(plan_state, "")

    if tool == "Bash":
        hit = regex_hit(policy.get("bash_deny", []), command)
        if hit:
            emit("deny", f"{hit['id']}: {hit.get('reason', 'bloqueado por política')}.")
        for seg in segments(command):
            for target in write_targets(seg):
                rel = to_rel(root, target, cwd)
                if rel and matches_any(rel, immutable):
                    emit("deny", f"`{rel}` é imutável por política (escrita/remoção bloqueada).")
        locked = [r for r in policy.get("bash_ask", []) if r.get("locked")]
        hit = regex_hit(locked, command)
        if hit:
            emit("ask", f"{hit['id']}: {hit.get('reason', 'confirmação humana exigida')}.")
        if plan_state != "approved" and not is_readonly(command, policy):
            emit("deny", f"gate G1: {gate_msg}. Só leitura e comandos do uah.py até a aprovação "
                         "(`/uah-init approve`).")
        grant = regex_hit(valid_grants(policy), command)
        if grant:
            emit("allow", f"concessão temporária H3 `{grant['id']}` válida até {grant['expires_at']}.")
        hit = regex_hit(policy.get("bash_ask", []), command)
        if hit:
            emit("ask", f"{hit['id']}: {hit.get('reason', 'confirmação exigida')}.")
        for seg in segments(command):
            for target in write_targets(seg):
                rel = to_rel(root, target, cwd)
                if rel and matches_any(rel, protected):
                    emit("ask", f"`{rel}` é protegido; confirme a alteração.")
        sys.exit(0)

    if tool in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        rel = to_rel(root, raw, cwd)
        if rel is None:
            sys.exit(0)
        if matches_any(rel, immutable):
            emit("deny", f"`{rel}` é imutável por política. Para mudar regras, edite project.yaml e rode compile.")
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
             "missing": "inexistente"}[state]
    gate = " · gate G1 ativo" if policy.get("plan_gate") and state != "approved" else ""
    lines.append(f"Plano: {label}{gate}")
    try:
        fm, _ = split_frontmatter((root / "state" / "current.md").read_text(encoding="utf-8"))
        st = parse_flat_yaml(fm)
        lines.append(f"Estado: tarefa {st.get('task_id') or '-'} · {st.get('status') or '-'} · "
                     f"próximo: {st.get('next_action') or '-'} · bloqueios: {st.get('blockers') or 'nenhum'} · "
                     f"atualizado {st.get('updated_at') or '-'}")
    except OSError:
        lines.append("Estado: state/current.md ausente.")
    warnings = []
    for key, rel in (("H2", "project.yaml"), ("H3", ".uah/task.yaml")):
        recorded = (policy.get("sources", {}).get(key) or {}).get("sha256")
        current = sha256_file(root / rel)
        if recorded != current:
            warnings.append(f"`{rel}` mudou desde o último compile → rode `python3 .uah/uah.py compile`")
    for grant in policy.get("temporary_grants", []):
        if grant not in valid_grants(policy):
            warnings.append(f"concessão H3 `{grant['id']}` expirada (inativa)")
    if warnings:
        lines.append("Avisos: " + "; ".join(warnings))
    lines.append("Antes de agir: leia state/current.md e plan/approved.md. Fonte de verdade = arquivos "
                 "versionados > plano aprovado > memórias (Claude/OMC/ai-memory).")
    print("\n".join(lines))


# --------------------------------------------------------------------- stop

def stop(payload: dict) -> None:
    root = project_root()
    policy = load_policy(root)
    if not policy or policy.get("g4_checkpoint") != "block" or payload.get("stop_hook_active"):
        return
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True,
                             text=True, timeout=10, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return
    newest = 0.0
    for line in out.splitlines():
        rel = line[3:].strip().split(" -> ")[-1].strip('"')
        if rel.startswith(("state/", ".uah/", ".omc/")):
            continue
        try:
            newest = max(newest, (root / rel).stat().st_mtime)
        except OSError:
            continue
    if not newest:
        return
    try:
        state_mtime = (root / "state" / "current.md").stat().st_mtime
    except OSError:
        state_mtime = 0.0
    if state_mtime >= newest:
        return
    print(json.dumps({
        "decision": "block",
        "reason": "[UAH-lite] G4: há alterações mais novas que state/current.md. Antes de encerrar, rode "
                  "`python3 .uah/uah.py checkpoint --task <T-xxx> --status <active|paused|blocked|done> "
                  "--next \"<próxima ação>\"` (e --blocker se houver).",
    }, ensure_ascii=False))


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
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


if __name__ == "__main__":
    main()
