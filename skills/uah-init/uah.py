#!/usr/bin/env python3
"""UAH-lite — configurador e fiscal mínimo de projetos com agentes.

Comandos:
  init         cria os arquivos mínimos e vendoriza o runtime em .uah/ (idempotente; também atualiza)
  compile      resolve H0+H1+H2+H3 -> .uah/policy.json + .claude/settings.json (permissões e hooks)
  import-plan  traz um plano/spec do OMC (.omc/plans|specs/*.md) para plan/approved.md (status draft)
  approve      aprova a revisão atual do plano (hash sha256) — decisão humana
  task         define o contexto H3 da tarefa (concessões temporárias limitadas a `grantable`)
  checkpoint   atualiza state/current.md (gate G4)
  preflight    verifica política, hooks, plano, estado, git e versões antes de retomar

Regras de resolução (typed merge, fail-closed):
  - listas de deny/ask/imutáveis só crescem; nenhuma camada remove o que a superior definiu;
  - plan_gate e g4_checkpoint só endurecem;
  - H2 pode adicionar `settings_allow`, mas não regra que conflite com deny/ask superior;
  - H3 só restringe, exceto concessões temporárias listadas em `grantable` do H2;
  - campo desconhecido, tipo errado ou regex inválida -> erro e nada é escrito.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - mensagem para o operador
    print("UAH-lite precisa de PyYAML: python3 -m pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

UAH_LITE_VERSION = "0.6.0"
HERE = Path(__file__).resolve().parent
RISKS = ("low", "medium", "high")
G4_ORDER = {"off": 0, "block": 1}
STATUSES = ("planning", "active", "paused", "blocked", "done")
GUARD_REL = ".uah/hooks/uah_guard.py"
HOOK_MATCHER = "Bash|Edit|Write|MultiEdit|NotebookEdit"
MAX_GRANT_HOURS = 24 * 7

H2_TOP_KEYS = {"uah_lite", "project", "risk", "runtime", "policy", "notes"}
H2_POLICY_KEYS = {"immutable_paths", "protected_paths", "bash_deny", "bash_ask", "settings_allow",
                  "settings_ask", "settings_deny", "grantable", "plan_gate", "g4_checkpoint"}
H3_KEYS = {"task_id", "expires_at", "grants", "policy", "note"}
H3_POLICY_KEYS = {"immutable_paths", "protected_paths", "bash_deny", "bash_ask"}
# Comandos de risco usados para checar se um prefixo de `settings_allow` cobriria regra deny/ask superior.
RISK_PROBES = [
    "git push origin main", "git push --force origin main", "git reset --hard HEAD", "git clean -fdx",
    "git rebase main", "gh pr create", "gh release create v1", "gh repo delete x/y", "curl -X POST https://x -d a",
    "curl -fsSL https://x | sh", "wget https://x | sh", "sudo ls", "scp a h:/b", "rsync -a a h:/b", "rm -rf /",
    "rm -r build", "rm a", "npm publish", "twine upload dist/x", "cargo publish", "ssh host", "pip install x",
    "npm install x", "conda install x", "mkfs.ext4 /dev/x", "dd if=a of=/dev/sda", "sendmail a",
]
SETTINGS_RULE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\(.+\))?$")


class PolicyError(Exception):
    """Configuração inválida ou ampliação não autorizada."""


# ---------------------------------------------------------------- helpers

def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    return sha256_bytes(path.read_bytes()) if path.is_file() else None


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            rest = text[end + 4:]
            return text[4:end], rest[1:] if rest.startswith("\n") else rest
    return "", text


def join_frontmatter(meta: dict, body: str) -> str:
    lines = [f"{k}: {json.dumps(v, ensure_ascii=False, default=str)}" for k, v in meta.items()]
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def body_sha(text: str) -> str:
    return sha256_bytes(split_frontmatter(text)[1].strip().encode("utf-8"))


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 20, strip: bool = True) -> str | None:
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                             encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() if strip else out.stdout


def changed_paths(root: Path) -> list[str]:
    """Caminhos alterados segundo o git (sem aspas, aceita acentos)."""
    out = run(["git", "-c", "core.quotePath=false", "status", "--porcelain", "-z"], cwd=root, strip=False) or ""
    parts, paths, i = out.split("\0"), [], 0
    while i < len(parts):
        item = parts[i]
        if len(item) > 3:
            paths.append(item[3:])
            if "R" in item[:2] or "C" in item[:2]:
                i += 1
        i += 1
    return paths


def render(template: str, values: dict) -> str:
    """`{{x}}` = texto cru; `{{x_q}}` = valor citado (JSON é YAML válido)."""
    for key, value in values.items():
        template = template.replace("{{" + key + "_q}}", json.dumps(str(value), ensure_ascii=False))
        template = template.replace("{{" + key + "}}", str(value))
    return template


def runtime_dir(root: Path) -> Path:
    return root / ".uah"


def source_dir(root: Path) -> Path:
    """Perfis/templates fixados no projeto (.uah/) têm precedência sobre os da skill."""
    vendored = runtime_dir(root)
    return vendored if (vendored / "profiles").is_dir() else HERE


# ------------------------------------------------------------- resolution

def _expect(cond: bool, msg: str) -> None:
    if not cond:
        raise PolicyError(msg)


def _str_list(value, where: str) -> list[str]:
    _expect(isinstance(value, list) and all(isinstance(v, str) and v for v in value),
            f"{where}: esperado lista de strings")
    return list(value)


def _rules(value, where: str, layer: str) -> list[dict]:
    _expect(isinstance(value, list), f"{where}: esperado lista")
    out = []
    for i, item in enumerate(value, 1):
        if isinstance(item, str):
            item = {"id": f"{layer}-{where.split('.')[-1]}-{i}", "pattern": item, "reason": f"regra {layer}"}
        _expect(isinstance(item, dict) and set(item) <= {"id", "pattern", "reason", "locked"}
                and isinstance(item.get("pattern"), str), f"{where}[{i}]: regra inválida {item!r}")
        if item.get("locked") and layer not in ("H0", "H1"):
            raise PolicyError(f"{where}[{i}]: só H0/H1 podem declarar regra locked")
        try:
            re.compile(item["pattern"])
        except re.error as exc:
            raise PolicyError(f"{where}[{i}]: regex inválida ({exc})") from exc
        item.setdefault("id", f"{layer}-{where.split('.')[-1]}-{i}")
        item.setdefault("reason", f"regra {layer}")
        out.append(item)
    return out


def _paths(value, where: str) -> list[str]:
    """Normaliza globs: tira `./` e `/` final; diretório literal passa a proteger o conteúdo."""
    out = []
    for item in _str_list(value, where):
        item = item[2:] if item.startswith("./") else item
        item = item.rstrip("/") or item
        _expect(not item.startswith("../") and item not in ("**", "*", "."), f"{where}: caminho amplo ou fora do projeto {item!r}")
        if not any(ch in item for ch in "*?["):
            out += [item, f"{item}/**"]
        else:
            out.append(item)
    return out


def _settings_rules(value, where: str) -> list[str]:
    rules = _str_list(value, where)
    for rule in rules:
        _expect(bool(SETTINGS_RULE_RE.match(rule)), f"{where}: regra de permissão malformada {rule!r}")
    return rules


def _bash_prefix(rule: str) -> str | None:
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    if not m:
        return None
    return re.sub(r"(:\*| \*|\*)$", "", m.group(1)).strip()


def load_profile(root: Path, name: str) -> dict:
    path = source_dir(root) / "profiles" / f"{name}.json"
    data = read_json(path)
    if data is None:
        raise PolicyError(f"perfil {name} ausente ou inválido em {path}")
    return data


def load_h2(root: Path) -> dict:
    path = root / "project.yaml"
    _expect(path.is_file(), "project.yaml não encontrado (rode init)")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _expect(isinstance(data, dict), "project.yaml: esperado mapeamento")
    unknown = set(data) - H2_TOP_KEYS
    _expect(not unknown, f"project.yaml: campos desconhecidos {sorted(unknown)}")
    _expect(data.get("risk") in RISKS, f"project.yaml: risk deve ser um de {RISKS}")
    project = data.get("project") or {}
    _expect(isinstance(project, dict) and isinstance(project.get("id"), str) and project["id"],
            "project.yaml: project.id obrigatório")
    policy = data.get("policy") or {}
    _expect(isinstance(policy, dict), "project.yaml: policy deve ser mapeamento")
    unknown = set(policy) - H2_POLICY_KEYS
    _expect(not unknown, f"project.yaml: policy com campos desconhecidos {sorted(unknown)}")
    return data


def load_h3(root: Path) -> dict | None:
    path = runtime_dir(root) / "task.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _expect(isinstance(data, dict), ".uah/task.yaml: esperado mapeamento")
    unknown = set(data) - H3_KEYS
    _expect(not unknown, f".uah/task.yaml: campos desconhecidos {sorted(unknown)}")
    policy = data.get("policy") or {}
    _expect(isinstance(policy, dict), ".uah/task.yaml: policy deve ser mapeamento")
    unknown = set(policy) - H3_POLICY_KEYS
    _expect(not unknown, f".uah/task.yaml: H3 só pode restringir; campos não permitidos {sorted(unknown)}")
    return data


def resolve(root: Path) -> dict:
    h0 = load_profile(root, "h0")
    h2 = load_h2(root)
    risk = h2["risk"]
    h1 = load_profile(root, f"risk-{risk}")
    h3 = load_h3(root)
    p2 = h2.get("policy") or {}

    resolved = {
        "uah_policy_version": "1",
        "uah_lite_version": UAH_LITE_VERSION,
        "project": {"id": h2["project"]["id"], "title": h2["project"].get("title", "")},
        "risk": risk,
        "immutable_paths": [],
        "protected_paths": [],
        "bash_deny": [],
        "bash_ask": [],
        "settings": {"allow": [], "ask": [], "deny": []},
        "plan_gate": False,
        "plan_gate_paths": _str_list(h0.get("plan_gate_paths", []), "H0.plan_gate_paths"),
        "readonly_bash": _str_list(h0.get("readonly_bash", []), "H0.readonly_bash"),
        "readonly_bash_subcommands": h0.get("readonly_bash_subcommands", {}),
        "g4_checkpoint": "off",
        "temporary_grants": [],
        "task": None,
    }

    def add_unique(target: list, items: list, key=None):
        seen = {(i[key] if key else i) for i in target}
        for item in items:
            k = item[key] if key else item
            if k not in seen:
                target.append(item)
                seen.add(k)

    for layer, data in (("H0", h0), ("H1", h1)):
        add_unique(resolved["immutable_paths"], _paths(data.get("immutable_paths", []), f"{layer}.immutable_paths"))
        add_unique(resolved["protected_paths"], _paths(data.get("protected_paths", []), f"{layer}.protected_paths"))
        add_unique(resolved["bash_deny"], _rules(data.get("bash_deny", []), f"{layer}.bash_deny", layer), "id")
        add_unique(resolved["bash_ask"], _rules(data.get("bash_ask", []), f"{layer}.bash_ask", layer), "id")
        for kind in ("allow", "ask", "deny"):
            add_unique(resolved["settings"][kind],
                       _settings_rules(data.get("settings", {}).get(kind, []), f"{layer}.settings.{kind}"))
        resolved["plan_gate"] = resolved["plan_gate"] or bool(data.get("plan_gate"))
        g4 = data.get("g4_checkpoint", "off")
        _expect(g4 in G4_ORDER, f"{layer}.g4_checkpoint inválido")
        if G4_ORDER[g4] > G4_ORDER[resolved["g4_checkpoint"]]:
            resolved["g4_checkpoint"] = g4

    upper_deny = list(resolved["bash_deny"])
    upper_ask = list(resolved["bash_ask"])
    upper_settings = {k: list(v) for k, v in resolved["settings"].items()}

    # H2 — projeto
    add_unique(resolved["immutable_paths"], _paths(p2.get("immutable_paths", []), "H2.immutable_paths"))
    add_unique(resolved["protected_paths"], _paths(p2.get("protected_paths", []), "H2.protected_paths"))
    add_unique(resolved["bash_deny"], _rules(p2.get("bash_deny", []), "H2.bash_deny", "H2"), "id")
    add_unique(resolved["bash_ask"], _rules(p2.get("bash_ask", []), "H2.bash_ask", "H2"), "id")
    add_unique(resolved["settings"]["deny"], _settings_rules(p2.get("settings_deny", []), "H2.settings_deny"))
    add_unique(resolved["settings"]["ask"], _settings_rules(p2.get("settings_ask", []), "H2.settings_ask"))
    allow = _settings_rules(p2.get("settings_allow", []), "H2.settings_allow")
    for rule in allow:
        broad = re.fullmatch(r"(Bash|Edit|Write|MultiEdit|NotebookEdit)(\((\.?/)?(\*\*|\*|:\*|)\))?", rule)
        _expect(not broad, f"H2.settings_allow: regra ampla demais {rule!r}")
        _expect(rule not in upper_settings["deny"] + upper_settings["ask"],
                f"H2.settings_allow: {rule!r} conflita com deny/ask de camada superior")
        prefix = _bash_prefix(rule)
        if prefix is not None:
            _expect(bool(prefix), f"H2.settings_allow: regra ampla demais {rule!r}")
            probes = [prefix] + [p for p in RISK_PROBES if p == prefix or p.startswith(prefix + " ")]
            for r in upper_deny + upper_ask:
                if any(re.search(r["pattern"], probe) for probe in probes):
                    raise PolicyError(f"H2.settings_allow: {rule!r} amplia permissão coberta por {r['id']}")
    add_unique(resolved["settings"]["allow"], allow)
    if "plan_gate" in p2:
        _expect(isinstance(p2["plan_gate"], bool), "H2.plan_gate deve ser booleano")
        _expect(p2["plan_gate"] or not resolved["plan_gate"],
                f"H2.plan_gate=false tenta desligar o gate exigido pelo risco {risk}")
        resolved["plan_gate"] = resolved["plan_gate"] or p2["plan_gate"]
    if "g4_checkpoint" in p2:
        g4 = p2["g4_checkpoint"]
        _expect(g4 in G4_ORDER, "H2.g4_checkpoint deve ser off|block")
        _expect(G4_ORDER[g4] >= G4_ORDER[resolved["g4_checkpoint"]],
                f"H2.g4_checkpoint={g4} afrouxa o exigido pelo risco {risk}")
        resolved["g4_checkpoint"] = g4
    grantable = _rules(p2.get("grantable", []), "H2.grantable", "H2")
    ids = [g["id"] for g in grantable]
    _expect(len(ids) == len(set(ids)), "H2.grantable: ids duplicados")

    # H3 — tarefa
    if h3 is not None:
        p3 = h3.get("policy") or {}
        add_unique(resolved["immutable_paths"], _paths(p3.get("immutable_paths", []), "H3.immutable_paths"))
        add_unique(resolved["protected_paths"], _paths(p3.get("protected_paths", []), "H3.protected_paths"))
        add_unique(resolved["bash_deny"], _rules(p3.get("bash_deny", []), "H3.bash_deny", "H3"), "id")
        add_unique(resolved["bash_ask"], _rules(p3.get("bash_ask", []), "H3.bash_ask", "H3"), "id")
        grants = _str_list(h3.get("grants") or [], "H3.grants") if h3.get("grants") else []
        if grants:
            expires = h3.get("expires_at")
            try:
                exp = _dt.datetime.fromisoformat(str(expires).replace("Z", "+00:00")) if expires else None
            except ValueError as exc:
                raise PolicyError(f"H3: expires_at inválido {expires!r}") from exc
            _expect(exp is not None, "H3: concessões exigem expires_at")
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=_dt.timezone.utc)
            horizon = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=MAX_GRANT_HOURS)
            _expect(exp <= horizon, f"H3: expires_at além do limite de {MAX_GRANT_HOURS} h")
            by_id = {g["id"]: g for g in grantable}
            for gid in grants:
                _expect(gid in by_id, f"H3: concessão {gid!r} não está em project.yaml policy.grantable")
                g = by_id[gid]
                resolved["temporary_grants"].append({
                    "id": gid, "tool": "Bash", "pattern": g["pattern"], "reason": g["reason"],
                    "expires_at": exp.astimezone(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                })
        resolved["task"] = {"task_id": h3.get("task_id"), "note": h3.get("note")}

    resolved["sources"] = {
        "H0": {"ref": f"uah-lite@{UAH_LITE_VERSION}:h0",
               "sha256": sha256_file(source_dir(root) / "profiles" / "h0.json")},
        "H1": {"ref": f"risk-{risk}", "sha256": sha256_file(source_dir(root) / "profiles" / f"risk-{risk}.json")},
        "H2": {"ref": "project.yaml", "sha256": sha256_file(root / "project.yaml")},
        "H3": {"ref": ".uah/task.yaml", "sha256": sha256_file(runtime_dir(root) / "task.yaml")},
    }
    resolved["python"] = (h2.get("runtime") or {}).get("python", "python3")
    resolved["resolution_hash"] = sha256_bytes(canonical(resolved))
    return resolved


# ------------------------------------------------------------ settings.json

def settings_entries(policy: dict) -> tuple[dict, dict]:
    """Regras de permissão e hooks gerenciados pelo UAH-lite."""
    py = policy.get("python", "python3")
    guard = f'{py} "$CLAUDE_PROJECT_DIR/{GUARD_REL}"'
    perms = {k: list(v) for k, v in policy["settings"].items()}
    for glob in policy["immutable_paths"]:
        rule = f"Edit(./{glob})"
        if rule not in perms["deny"]:
            perms["deny"].append(rule)
    hooks = {
        "PreToolUse": [{"matcher": HOOK_MATCHER,
                        "hooks": [{"type": "command", "command": f"{guard} pre-tool-use", "timeout": 15}]}],
        "SessionStart": [{"hooks": [{"type": "command", "command": f"{guard} session-start", "timeout": 15}]}],
    }
    if policy.get("g4_checkpoint") == "block":
        hooks["Stop"] = [{"hooks": [{"type": "command", "command": f"{guard} stop", "timeout": 15}]}]
    return perms, hooks


def merge_settings(root: Path, policy: dict) -> Path:
    path = root / ".claude" / "settings.json"
    settings = {}
    if path.exists():
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise PolicyError(f".claude/settings.json inválido ({exc}); corrija antes — nada foi alterado") from exc
    if not isinstance(settings, dict):
        raise PolicyError(".claude/settings.json não é um objeto JSON")
    managed_path = runtime_dir(root) / "managed-settings.json"
    managed = read_json(managed_path, {}) or {}
    perms, hooks = settings_entries(policy)

    current = settings.setdefault("permissions", {})
    owned = {}
    for kind in ("allow", "ask", "deny"):
        previous = set((managed.get("owned") or managed.get("permissions") or {}).get(kind, []))
        kept = [r for r in current.get(kind, []) if r not in previous]  # regras do usuário
        owned[kind] = [r for r in perms[kind] if r not in kept]          # só as que o UAH acrescenta
        merged = kept + owned[kind]
        if merged:
            current[kind] = merged
        else:
            current.pop(kind, None)
    if not current:
        settings.pop("permissions")

    all_hooks = settings.setdefault("hooks", {})
    for event in list(all_hooks):
        entries = []
        for entry in all_hooks[event]:
            hooks_left = [h for h in entry.get("hooks", []) if GUARD_REL not in h.get("command", "")]
            if hooks_left:
                entries.append(dict(entry, hooks=hooks_left))
        if entries:
            all_hooks[event] = entries
        else:
            del all_hooks[event]
    for event, entries in hooks.items():
        all_hooks.setdefault(event, []).extend(entries)

    write_json(path, settings)
    write_json(managed_path, {"owned": owned, "hook_events": sorted(hooks), "updated_at": now_iso()})
    return path


# ------------------------------------------------------------------ cmds

def cmd_compile(root: Path, quiet: bool = False) -> dict:
    policy = resolve(root)
    stamped = dict(policy, compiled_at=now_iso())
    write_json(runtime_dir(root) / "policy.json", stamped)
    merge_settings(root, policy)
    if not quiet:
        print(f"compile: risco {policy['risk']} · gate G1 {'on' if policy['plan_gate'] else 'off'} · "
              f"G4 {policy['g4_checkpoint']} · {len(policy['bash_deny'])} deny / {len(policy['bash_ask'])} ask · "
              f"{len(policy['temporary_grants'])} concessões H3 · hash {policy['resolution_hash'][:12]}")
    return policy


def upsert_block(path: Path, block: str, header: str) -> str:
    begin, end = "<!-- UAH:BEGIN", "<!-- UAH:END -->"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if begin in text and end in text:
            start = text.index(begin)
            stop = text.index(end) + len(end)
            new = text[:start] + block.strip() + text[stop:]
            action = "atualizado"
        else:
            new = text.rstrip() + "\n\n" + block.strip() + "\n"
            action = "bloco acrescentado"
    else:
        new = header + "\n\n" + block.strip() + "\n"
        action = "criado"
    path.write_text(new, encoding="utf-8")
    return action


def vendor_runtime(root: Path) -> None:
    dest = runtime_dir(root)
    if HERE.resolve() == dest.resolve():
        return
    for sub in ("profiles", "templates", "hooks"):
        (dest / sub).mkdir(parents=True, exist_ok=True)
        for item in (HERE / sub).iterdir():
            if item.is_file():
                shutil.copy2(item, dest / sub / item.name)
    shutil.copy2(HERE / "uah.py", dest / "uah.py")
    (dest / "hooks" / "uah_guard.py").chmod(0o755)


def probes_enabled() -> bool:
    return os.environ.get("UAH_SKIP_VERSION_PROBE") != "1"


def record_versions(root: Path) -> dict:
    if not probes_enabled():
        versions = {"uah_lite": UAH_LITE_VERSION, "claude_code": None, "omc": None, "recorded_at": now_iso()}
        write_json(runtime_dir(root) / "versions.json", versions)
        return versions
    versions = {
        "uah_lite": UAH_LITE_VERSION,
        "claude_code": run(["claude", "--version"]),
        "omc": run(["omc", "--version"]),
        "python": sys.version.split()[0],
        "recorded_at": now_iso(),
    }
    lock = runtime_dir(root) / "omc-capabilities.lock.json"
    if versions["omc"] and run(["omc", "capabilities", "lock", "--lockfile", str(lock)], cwd=root, timeout=60) is not None:
        versions["omc_capabilities_lock"] = lock.name
    write_json(runtime_dir(root) / "versions.json", versions)
    return versions


def cmd_init(root: Path, project_id: str | None, title: str | None, risk: str, python_cmd: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    project_id = project_id or re.sub(r"[^a-z0-9-]+", "-", root.name.lower()).strip("-") or "projeto"
    values = {"project_id": project_id, "title": title or root.name, "risk": risk,
              "python": python_cmd, "now": now_iso()}
    vendor_runtime(root)
    tpl = source_dir(root) / "templates"
    created = []
    for rel, name in (("project.yaml", "project.yaml"), ("plan/approved.md", "plan.md"),
                      ("state/current.md", "state.md")):
        target = root / rel
        if target.exists():
            created.append(f"{rel} (mantido)")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render((tpl / name).read_text(encoding="utf-8"), values), encoding="utf-8")
        created.append(f"{rel} (criado)")
    try:
        h2 = yaml.safe_load((root / "project.yaml").read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise PolicyError(f"project.yaml inválido ({exc})") from exc
    block = render((tpl / "entrypoint-block.md").read_text(encoding="utf-8"), dict(values, risk=h2.get("risk", risk)))
    created.append("CLAUDE.md (" + upsert_block(root / "CLAUDE.md", block, "# CLAUDE.md") + ")")
    created.append("AGENTS.md (" + upsert_block(root / "AGENTS.md", block, "# AGENTS.md") + ")")
    versions = record_versions(root)
    policy = cmd_compile(root, quiet=True)
    _update_state(root, {}, f"init/atualização UAH-lite {UAH_LITE_VERSION}")  # estado mais novo que os arquivos gerados
    print(f"UAH-lite {UAH_LITE_VERSION} em {root}")
    for line in created:
        print(f"  - {line}")
    print(f"  - .uah/ (runtime, política {policy['resolution_hash'][:12]}) · .claude/settings.json (hooks + permissões)")
    print(f"  claude={versions['claude_code']} · omc={versions['omc']}")
    print(f"Risco {policy['risk']}: gate G1 {'ATIVO — aprove o plano antes de alterar arquivos' if policy['plan_gate'] else 'desligado'}.")
    if not (root / ".git").exists():
        print("Aviso: projeto sem git. Estado canônico e retomada entre máquinas pressupõem `git init` + remoto.")


def cmd_import_plan(root: Path, src: Path) -> None:
    _expect(src.is_file(), f"arquivo não encontrado: {src}")
    text = src.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    home = str(Path.home())
    body = body.replace(home, "~")
    plan = root / "plan" / "approved.md"
    project_id = (load_h2(root).get("project") or {}).get("id", "")
    try:
        rel = src.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = src.name
    meta = {"status": "draft", "project_id": project_id, "source": rel, "imported_at": now_iso()}
    header = (f"> Importado de `{rel}`. Revise e complete (escopo, entregáveis com aceite, tarefas T-xxx) "
              "antes de aprovar.\n\n")
    was_approved = (runtime_dir(root) / "plan.lock.json").is_file()
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(join_frontmatter(meta, header + body.strip() + "\n"), encoding="utf-8")
    print(f"import-plan: {rel} -> plan/approved.md (draft)")
    if was_approved:
        print("Atenção: havia plano aprovado; o novo conteúdo reabre o gate G1 até nova aprovação.")


PLAN_REQUIRED = {
    "escopo/objetivo": r"(?im)^#+.*\b(escopo|scope|objetivo|goal|requisitos|requirements)\b",
    "critérios de aceite": r"(?i)\b(aceite|acceptance|pronto quando|definition of done|done when)\b",
}


def cmd_approve(root: Path, by: str | None, allow_incomplete: bool) -> None:
    plan = root / "plan" / "approved.md"
    _expect(plan.is_file(), "plan/approved.md não existe")
    text = plan.read_text(encoding="utf-8")
    meta_raw, body = split_frontmatter(text)
    _expect(len(body.strip()) > 40, "plano vazio")
    missing = [name for name, rx in PLAN_REQUIRED.items() if not re.search(rx, body)]
    if missing and not allow_incomplete:
        raise PolicyError(f"plano incompleto: falta {', '.join(missing)} (use --allow-incomplete para registrar a exceção)")
    digest = body_sha(text)
    by = by or run(["git", "config", "user.name"], cwd=root) or os.environ.get("USER", "desconhecido")
    lock = {"sha256": digest, "approved_by": by, "approved_at": now_iso(), "plan_path": "plan/approved.md",
            "uah_lite_version": UAH_LITE_VERSION, "warnings": [f"incompleto: {m}" for m in missing]}
    try:
        meta = yaml.safe_load(meta_raw) if meta_raw else {}
    except yaml.YAMLError:
        meta = {}
    meta = meta if isinstance(meta, dict) else {}
    meta.update({"status": "approved", "approved_by": by, "approved_at": lock["approved_at"], "revision": digest[:12]})
    plan.write_text(join_frontmatter(meta, body), encoding="utf-8")
    _expect(body_sha(plan.read_text(encoding="utf-8")) == digest, "falha ao regravar o plano sem alterar o corpo")
    _update_state(root, {"plan_revision": digest[:12]}, f"plano aprovado por {by} (rev {digest[:12]})")
    write_json(runtime_dir(root) / "plan.lock.json", lock)  # por último: só libera o gate se tudo acima deu certo
    print(f"approve: plano rev {digest[:12]} aprovado por {by}. Gate G1 liberado para esta revisão.")


def cmd_task(root: Path, task_id: str | None, hours: float, grants: list[str], clear: bool) -> None:
    path = runtime_dir(root) / "task.yaml"
    if clear:
        if path.exists():
            path.unlink()
        cmd_compile(root)
        print("task: contexto H3 removido.")
        return
    data = {"task_id": task_id}
    if grants:
        _expect(0 < hours <= MAX_GRANT_HOURS, f"--hours deve estar em (0, {MAX_GRANT_HOURS}]")
        exp = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=hours)
        data["expires_at"] = exp.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        data["grants"] = grants
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    try:
        cmd_compile(root)
    except PolicyError:
        if previous is None:
            path.unlink()
        else:
            path.write_text(previous, encoding="utf-8")
        raise
    if task_id:
        _update_state(root, {"task_id": task_id}, f"contexto H3 {task_id}")


def _workspace_commit(root: Path) -> str:
    head = run(["git", "rev-parse", "--short=12", "HEAD"], cwd=root)
    if not head:
        return ""
    dirty = [p for p in changed_paths(root) if not p.startswith(("state/", ".uah/", ".omc/"))]
    return head + ("-dirty" if dirty else "")


def _update_state(root: Path, fields: dict, log: str) -> None:
    path = root / "state" / "current.md"
    if not path.is_file():
        return
    meta_raw, body = split_frontmatter(path.read_text(encoding="utf-8"))
    try:
        meta = yaml.safe_load(meta_raw) if meta_raw else {}
    except yaml.YAMLError as exc:
        raise PolicyError(f"state/current.md com metadados YAML inválidos ({exc})") from exc
    meta = meta if isinstance(meta, dict) else {}
    meta.update({k: v for k, v in fields.items() if v is not None})
    meta["updated_at"] = now_iso()
    line = f"- {meta['updated_at']} · {log}"
    body = body.rstrip() + "\n" + line + "\n" if "## Registro" in body else body.rstrip() + "\n\n## Registro\n" + line + "\n"
    path.write_text(join_frontmatter(meta, body), encoding="utf-8")


def cmd_checkpoint(root: Path, task: str | None, status: str, next_action: str, blockers: list[str], note: str | None) -> None:
    lock = read_json(runtime_dir(root) / "plan.lock.json", {}) or {}
    operator = run(["git", "config", "user.name"], cwd=root) or os.environ.get("USER", "")
    fields = {
        "task_id": task,
        "status": status,
        "next_action": next_action,
        "blockers": "; ".join(blockers),
        "operator": operator,
        "workspace_commit": _workspace_commit(root),
        "plan_revision": str(lock.get("sha256", ""))[:12],
    }
    log = f"{task or '-'} · {status} · próximo: {next_action}" + (f" · {note}" if note else "")
    _update_state(root, fields, log)
    print(f"checkpoint: {task or '-'} {status} · commit {fields['workspace_commit'] or '(sem git)'}")


def cmd_preflight(root: Path) -> int:
    results: list[tuple[str, str]] = []

    def add(level: str, msg: str):
        results.append((level, msg))

    policy = read_json(runtime_dir(root) / "policy.json")
    if policy is None:
        add("FAIL", ".uah/policy.json ausente/inválida — rode compile")
    else:
        try:
            fresh = resolve(root)
            if fresh["resolution_hash"] != policy.get("resolution_hash"):
                add("WARN", "configuração mudou desde o último compile — rode compile")
            else:
                add("OK", f"política {policy['resolution_hash'][:12]} em dia (risco {policy['risk']})")
        except PolicyError as exc:
            add("FAIL", f"configuração inválida: {exc}")
    settings = read_json(root / ".claude" / "settings.json", {}) or {}
    commands = [h.get("command", "") for entries in (settings.get("hooks") or {}).values()
                for e in entries for h in e.get("hooks", [])]
    if any(GUARD_REL in c and "pre-tool-use" in c for c in commands):
        add("OK", "hook PreToolUse do UAH registrado em .claude/settings.json")
    else:
        add("FAIL", "hook PreToolUse ausente em .claude/settings.json — rode compile")
    guard = runtime_dir(root) / "hooks" / "uah_guard.py"
    gv = re.search(r'GUARD_VERSION = "([^"]+)"', guard.read_text(encoding="utf-8")) if guard.is_file() else None
    if not gv:
        add("FAIL", "guard .uah/hooks/uah_guard.py ausente — rode init")
    elif gv.group(1) != UAH_LITE_VERSION:
        add("WARN", f"guard {gv.group(1)} ≠ uah.py {UAH_LITE_VERSION} — rode init para atualizar o runtime")

    plan = root / "plan" / "approved.md"
    lock = read_json(runtime_dir(root) / "plan.lock.json")
    gate = bool(policy and policy.get("plan_gate"))
    if not plan.is_file():
        add("WARN", "plan/approved.md ausente")
    elif lock is None:
        add("WARN" if gate else "OK", "plano não aprovado" + (" — gate G1 bloqueia alterações materiais" if gate else ""))
    elif lock.get("sha256") != body_sha(plan.read_text(encoding="utf-8")):
        add("WARN", "plano modificado após aprovação — reaprovar")
    else:
        add("OK", f"plano aprovado rev {lock['sha256'][:12]} por {lock.get('approved_by')} em {lock.get('approved_at')}")

    state = root / "state" / "current.md"
    if state.is_file():
        try:
            meta = yaml.safe_load(split_frontmatter(state.read_text(encoding="utf-8"))[0]) or {}
        except yaml.YAMLError:
            meta = {}
            add("WARN", "state/current.md com metadados YAML inválidos")
        add("OK", f"estado: tarefa {meta.get('task_id') or '-'} · {meta.get('status')} · próximo: {meta.get('next_action')}")
        recorded = str(meta.get("workspace_commit") or "")
        head = run(["git", "rev-parse", "--short=12", "HEAD"], cwd=root)
        if head and recorded and not recorded.startswith(head):
            add("WARN", f"último checkpoint em {recorded}, HEAD atual {head} — confira o que mudou")
    else:
        add("WARN", "state/current.md ausente")

    inside = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root)
    branch = (run(["git", "branch", "--show-current"], cwd=root) or "(sem commits)") if inside == "true" else None
    if branch is None:
        add("WARN", "sem repositório git — retomada entre máquinas depende de git + remoto")
    else:
        dirty = len(changed_paths(root))
        add("OK", f"git: branch {branch} · {dirty} arquivo(s) alterado(s)")

    versions = read_json(runtime_dir(root) / "versions.json", {}) or {}
    probes = (("claude_code", ["claude", "--version"]), ("omc", ["omc", "--version"])) if probes_enabled() else ()
    for key, cmd in probes:
        now = run(cmd)
        if versions.get(key) and now and now != versions[key]:
            add("WARN", f"{key}: registrado {versions[key]}, instalado {now} — revalidar e rodar init")
    caps = runtime_dir(root) / "omc-capabilities.lock.json"
    if caps.is_file() and probes_enabled() and run(["omc", "--version"]):
        out = run(["omc", "capabilities", "check", "--json", "--lockfile", str(caps)], cwd=root, timeout=60)
        failures = (json.loads(out).get("failures") if out else None)
        if failures is None:
            add("WARN", "omc capabilities check falhou ao executar")
        elif failures:
            add("WARN", f"superfície do OMC mudou: {len(failures)} divergência(s) — revalidar")
        else:
            add("OK", "superfície do OMC igual ao lock")
    for grant in (policy or {}).get("temporary_grants", []):
        exp = _dt.datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
        if exp <= _dt.datetime.now(_dt.timezone.utc):
            add("INFO", f"concessão H3 {grant['id']} expirada")

    for level, msg in results:
        print(f"[{level}] {msg}")
    return 1 if any(level == "FAIL" for level, _ in results) else 0


# ------------------------------------------------------------------ main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uah.py", description="UAH-lite: configurador e fiscal mínimo de projetos.")
    parser.add_argument("--root", default=".", help="raiz do projeto (padrão: diretório atual)")
    parser.add_argument("--version", action="version", version=f"UAH-lite {UAH_LITE_VERSION}")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="cria/atualiza os arquivos mínimos e o runtime .uah/")
    p.add_argument("--project-id")
    p.add_argument("--title")
    p.add_argument("--risk", choices=RISKS, default="medium")
    p.add_argument("--python", default="python3", help="comando python usado pelos hooks")
    sub.add_parser("compile", help="resolve H0–H3 e escreve policy.json + settings.json")
    p = sub.add_parser("import-plan", help="importa plano/spec do OMC")
    p.add_argument("source")
    p = sub.add_parser("approve", help="aprova a revisão atual do plano (decisão humana)")
    p.add_argument("--by")
    p.add_argument("--allow-incomplete", action="store_true")
    p = sub.add_parser("task", help="define contexto H3")
    p.add_argument("--id", dest="task_id")
    p.add_argument("--grant", action="append", default=[])
    p.add_argument("--hours", type=float, default=4.0)
    p.add_argument("--clear", action="store_true")
    p = sub.add_parser("checkpoint", help="atualiza state/current.md (G4)")
    p.add_argument("--task")
    p.add_argument("--status", choices=STATUSES, required=True)
    p.add_argument("--next", dest="next_action", required=True)
    p.add_argument("--blocker", action="append", default=[])
    p.add_argument("--note")
    sub.add_parser("preflight", help="verificações antes de retomar")
    sub.add_parser("status", help="alias de preflight")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.cmd == "init":
            cmd_init(root, args.project_id, args.title, args.risk, args.python)
        elif args.cmd == "compile":
            cmd_compile(root)
        elif args.cmd == "import-plan":
            cmd_import_plan(root, Path(args.source))
        elif args.cmd == "approve":
            cmd_approve(root, args.by, args.allow_incomplete)
        elif args.cmd == "task":
            cmd_task(root, args.task_id, args.hours, args.grant, args.clear)
        elif args.cmd == "checkpoint":
            cmd_checkpoint(root, args.task, args.status, args.next_action, args.blocker, args.note)
        elif args.cmd in ("preflight", "status"):
            return cmd_preflight(root)
    except PolicyError as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 3
    except yaml.YAMLError as exc:
        print(f"BLOQUEADO: YAML inválido ({exc})", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
