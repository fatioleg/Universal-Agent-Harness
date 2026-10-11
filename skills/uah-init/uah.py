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
  explain      mostra, em linguagem simples, as regras efetivas e de que camada vêm
  integrations lista/instala/ativa ferramentas externas do fluxo (workflow-digestion, specboard, calcboard)
  slice        fatias de MVP (SDD incremental): list | new N | activate N | done N
  setup-env    prepara a máquina: verifica tudo e, com --install, instala sem sudo (versões fixas,
               checksum conferido) Quarto, D2, skills do catálogo e o venv do sci-figures; para OMC,
               molar_vis e pacotes de sistema imprime os comandos exatos

Fatias: plan/approved.md é o plano geral (aprovado uma vez); plan/slices/slice-N.md são fatias
aprovadas uma a uma (`approve --slice N`). Depois da primeira fatia, o gate G1 só libera
execução com uma fatia ATIVA e aprovada (e sem mudanças desde a aprovação).

Regras de resolução (typed merge, fail-closed):
  - listas de deny/ask/imutáveis só crescem; nenhuma camada remove o que a superior definiu;
  - plan_gate e g4_checkpoint só endurecem;
  - H2 pode adicionar `settings_allow`, mas não regra que conflite com deny/ask superior;
  - H3 só restringe, exceto concessões temporárias listadas em `grantable` do H2;
  - campo desconhecido, tipo errado ou regex inválida -> erro e nada é escrito.
"""

from __future__ import annotations

import argparse
import difflib
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

UAH_LITE_VERSION = "0.9.0"
HERE = Path(__file__).resolve().parent
RISKS = ("low", "medium", "high")
G4_ORDER = {"off": 0, "block": 1}
STATUSES = ("planning", "active", "paused", "blocked", "done")
GUARD_REL = ".uah/hooks/uah_guard.py"
HOOK_MATCHER = "Bash|Edit|Write|MultiEdit|NotebookEdit"
MAX_GRANT_HOURS = 24 * 7

H2_TOP_KEYS = {"uah_lite", "project", "risk", "runtime", "integrations", "policy", "notes"}
PROJECT_KEYS = {"id", "title", "domains"}
RUNTIME_KEYS = {"python"}
INTEGRATION_POLICY_KEYS = {"immutable_paths", "protected_paths", "bash_deny", "bash_ask", "plan_gate_paths", "gate_cli"}
H2_POLICY_KEYS = {"immutable_paths", "protected_paths", "bash_deny", "bash_ask", "settings_allow",
                  "settings_ask", "settings_deny", "grantable", "plan_gate", "g4_checkpoint", "max_attempts"}
LEVELS = ("leve", "padrão", "crítico")
LEDGER_REL = "state/tarefas.jsonl"
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


def write_json_atomic(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


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


def _unknown(found, allowed: set, where: str) -> None:
    """Campo desconhecido -> erro com sugestão da grafia mais próxima."""
    unknown = sorted(set(found) - allowed)
    if unknown:
        hints = []
        for key in unknown:
            close = difflib.get_close_matches(str(key), sorted(allowed), n=1, cutoff=0.6)
            hints.append(f"{key!r}" + (f" (quis dizer {close[0]!r}?)" if close else ""))
        raise PolicyError(f"{where}: campo(s) desconhecido(s) {', '.join(hints)}; válidos: {', '.join(sorted(allowed))}")


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
    _unknown(data, H2_TOP_KEYS, "project.yaml")
    _expect(data.get("risk") in RISKS, f"project.yaml: risk deve ser um de {', '.join(RISKS)} (atual: {data.get('risk')!r})")
    project = data.get("project") or {}
    _expect(isinstance(project, dict) and isinstance(project.get("id"), str) and project["id"],
            "project.yaml: project.id obrigatório")
    _unknown(project, PROJECT_KEYS, "project.yaml → project")
    if project.get("domains") is not None:
        _expect(isinstance(project["domains"], list), "project.yaml → project.domains: esperado lista")
        if project["domains"]:
            _str_list(project["domains"], "project.yaml → project.domains")
    runtime = data.get("runtime") or {}
    _expect(isinstance(runtime, dict), "project.yaml: runtime deve ser mapeamento")
    _unknown(runtime, RUNTIME_KEYS, "project.yaml → runtime")
    integrations = data.get("integrations")
    _expect(integrations is None or isinstance(integrations, list), "project.yaml → integrations: esperado lista")
    if integrations:
        _str_list(integrations, "project.yaml → integrations")
    policy = data.get("policy") or {}
    _expect(isinstance(policy, dict), "project.yaml: policy deve ser mapeamento")
    _unknown(policy, H2_POLICY_KEYS, "project.yaml → policy")
    return data


def load_h3(root: Path) -> dict | None:
    path = runtime_dir(root) / "task.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _expect(isinstance(data, dict), ".uah/task.yaml: esperado mapeamento")
    _unknown(data, H3_KEYS, ".uah/task.yaml")
    policy = data.get("policy") or {}
    _expect(isinstance(policy, dict), ".uah/task.yaml: policy deve ser mapeamento")
    _unknown(policy, H3_POLICY_KEYS, ".uah/task.yaml → policy (H3 só pode restringir)")
    return data


# ----------------------------------------------------------- integrations

def catalog(root: Path) -> dict[str, dict]:
    """Catálogo de integrações fixado no projeto (.uah/integrations) ou o da skill."""
    out = {}
    for base in (HERE / "integrations", runtime_dir(root) / "integrations"):
        if base.is_dir():
            for path in sorted(base.glob("*.json")):
                data = read_json(path)
                if isinstance(data, dict) and data.get("id"):
                    out[data["id"]] = data
    return out


def skills_dir() -> Path:
    return Path.home() / ".claude" / "skills"


def find_skill(skill_name: str) -> Path | None:
    """Pasta da skill instalada cujo SKILL.md declara `name: <skill_name>`."""
    base = skills_dir()
    if not base.is_dir():
        return None
    for skill_md in sorted(base.glob("*/SKILL.md")):
        try:
            head = skill_md.read_text(encoding="utf-8")[:2000]
        except (OSError, ValueError):
            continue
        if re.search(rf"(?m)^name:\s*['\"]?{re.escape(skill_name)}['\"]?\s*$", head):
            return skill_md.parent
    return None


def repo_key(url: str | None) -> str:
    """github.com/dono/repo, igual para SSH e HTTPS (com ou sem .git)."""
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r"^git@([^:]+):", r"\1/", url)
    url = re.sub(r"^(https?|ssh|git)://([^@/]+@)?", "", url)
    return re.sub(r"\.git$", "", url).rstrip("/")


def integration_status(entry: dict) -> dict:
    """Instalada = SKILL.md com o `name`; verificada = repositório git cujo remoto é o do catálogo;
    fixada = commit instalado igual ao `ref` do catálogo (quando houver)."""
    path = find_skill(entry["skill_name"])
    commit, verified, pinned = None, False, None
    if path is not None:
        real = str(Path(os.path.realpath(path)))
        commit = run(["git", "-C", real, "rev-parse", "HEAD"])
        remote = run(["git", "-C", real, "remote", "get-url", "origin"])
        verified = bool(commit) and repo_key(remote) == repo_key(entry.get("repo"))
        if entry.get("ref") and commit:
            pinned = commit.startswith(str(entry["ref"]))
    return {"installed": path is not None, "path": str(path) if path else None,
            "commit": commit[:12] if commit else None, "verified": verified, "pinned": pinned}


def _integration_overlay(entry: dict) -> dict:
    policy = entry.get("policy") or {}
    _unknown(policy, INTEGRATION_POLICY_KEYS, f"integração {entry['id']}")
    for item in policy.get("gate_cli", []):
        _expect(isinstance(item, dict) and isinstance(item.get("script"), str)
                and isinstance(item.get("subcommands"), list), f"integração {entry['id']}: gate_cli inválido")
    return policy


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
        "max_attempts": 5,
        "gate_cli": [],
        "integrations": [],
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
        if "max_attempts" in data:
            _expect(isinstance(data["max_attempts"], int) and data["max_attempts"] >= 1, f"{layer}.max_attempts inválido")
            resolved["max_attempts"] = min(resolved["max_attempts"], data["max_attempts"])

    # Integrações ativas (catálogo confiável, nível H1): só acrescentam restrições,
    # caminhos de planejamento e CLIs de planejamento/leitura liberados antes da aprovação.
    known = catalog(root)
    enabled = list(dict.fromkeys(h2.get("integrations") or []))
    for iid in enabled:
        if iid not in known:
            close = difflib.get_close_matches(iid, sorted(known), n=1, cutoff=0.5)
            raise PolicyError(f"project.yaml → integrations: {iid!r} não está no catálogo"
                              + (f" (quis dizer {close[0]!r}?)" if close else "")
                              + f"; disponíveis: {', '.join(sorted(known)) or 'nenhuma'}")
        entry = known[iid]
        overlay = _integration_overlay(entry)
        layer = f"INT:{iid}"
        add_unique(resolved["immutable_paths"], _paths(overlay.get("immutable_paths", []), f"{layer}.immutable_paths"))
        add_unique(resolved["protected_paths"], _paths(overlay.get("protected_paths", []), f"{layer}.protected_paths"))
        add_unique(resolved["bash_deny"], _rules(overlay.get("bash_deny", []), f"{layer}.bash_deny", "H1"), "id")
        add_unique(resolved["bash_ask"], _rules(overlay.get("bash_ask", []), f"{layer}.bash_ask", "H1"), "id")
        add_unique(resolved["plan_gate_paths"], _str_list(overlay.get("plan_gate_paths", []), f"{layer}.plan_gate_paths"))
        for item in overlay.get("gate_cli", []):
            resolved["gate_cli"].append({"integration": iid, "script": item["script"],
                                         "subcommands": list(item["subcommands"])})
        resolved["integrations"].append({k: entry.get(k) for k in ("id", "title", "skill_name", "stage", "when", "how", "repo")})

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
    if "max_attempts" in p2:
        ma = p2["max_attempts"]
        _expect(isinstance(ma, int) and ma >= 1, "H2.max_attempts deve ser inteiro ≥ 1")
        _expect(ma <= resolved["max_attempts"], f"H2.max_attempts={ma} afrouxa o limite do risco {risk} "
                                                f"({resolved['max_attempts']}); só pode reduzir")
        resolved["max_attempts"] = ma
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
    # Situação da instalação depende da máquina: fica fora do hash.
    for item in resolved["integrations"]:
        item.update(integration_status(known[item["id"]]))
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


def merge_settings(root: Path, policy: dict, write: bool = True) -> tuple[dict, dict]:
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

    managed_new = {"owned": owned, "hook_events": sorted(hooks), "updated_at": now_iso()}
    if write:
        write_json_atomic(path, settings)
        write_json_atomic(managed_path, managed_new)
    return settings, managed_new


# ------------------------------------------------------------------ cmds

def cmd_compile(root: Path, quiet: bool = False) -> dict:
    policy = resolve(root)
    stamped = dict(policy, compiled_at=now_iso())
    # Prepara tudo antes de gravar: settings.json inválido aborta sem tocar em policy.json.
    settings, managed = merge_settings(root, policy, write=False)
    write_json_atomic(root / ".claude" / "settings.json", settings)
    write_json_atomic(runtime_dir(root) / "managed-settings.json", managed)
    write_json_atomic(runtime_dir(root) / "policy.json", stamped)
    if not quiet:
        print(f"compile: risco {policy['risk']} · gate G1 {'on' if policy['plan_gate'] else 'off'} · "
              f"G4 {policy['g4_checkpoint']} · {len(policy['bash_deny'])} deny / {len(policy['bash_ask'])} ask · "
              f"{len(policy['temporary_grants'])} concessões H3 · hash {policy['resolution_hash'][:12]}")
        for item in policy["integrations"]:
            state = "instalada" if item["installed"] else "NÃO INSTALADA → python3 .uah/uah.py integrations install " + item["id"]
            print(f"  integração {item['id']}: {state}")
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
    for sub in ("profiles", "templates", "hooks", "integrations"):
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


def cmd_init(root: Path, project_id: str | None, title: str | None, risk: str, python_cmd: str,
             domains: list[str] | None = None, integrations: list[str] | None = None) -> None:
    root.mkdir(parents=True, exist_ok=True)
    project_id = project_id or re.sub(r"[^a-z0-9-]+", "-", root.name.lower()).strip("-") or "projeto"
    known = catalog(root)
    for iid in integrations or []:
        _expect(iid in known, f"integração desconhecida {iid!r}; disponíveis: {', '.join(sorted(known))}")
    values = {"project_id": project_id, "title": title or root.name, "risk": risk,
              "python": python_cmd, "now": now_iso()}
    list_values = {"domains": json.dumps(domains or [], ensure_ascii=False),
                   "integrations": json.dumps(integrations or [], ensure_ascii=False)}
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
        text = render((tpl / name).read_text(encoding="utf-8"), values)
        for key, value in list_values.items():
            text = text.replace("{{" + key + "_list}}", value)
        target.write_text(text, encoding="utf-8")
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
    for item in policy["integrations"]:
        print(f"  integração {item['id']}: {'instalada' if item['installed'] else 'NÃO INSTALADA (uah.py integrations install ' + item['id'] + ')'}")
    recs = [e["id"] for e in recommend(root, policy) if e["id"] not in {i["id"] for i in policy["integrations"]}]
    if recs:
        print(f"Sugestão: para este tipo de projeto, considere `uah.py integrations enable {' '.join(recs)}`.")
    if not (root / ".git").exists():
        print("Aviso: projeto sem git. Estado canônico e retomada entre máquinas pressupõem `git init` + remoto.")


RISK_RANK = {"low": 0, "medium": 1, "high": 2}


def recommend(root: Path, policy: dict | None = None) -> list[dict]:
    """Integrações cujo domínio casa com project.domains e cujo risco mínimo é atendido."""
    try:
        h2 = load_h2(root)
    except (PolicyError, yaml.YAMLError):
        return []
    domains = {d.lower() for d in ((h2.get("project") or {}).get("domains") or [])}
    risk = h2.get("risk", "low")
    out = []
    for entry in catalog(root).values():
        if RISK_RANK.get(entry.get("risk_min", "low"), 0) > RISK_RANK.get(risk, 0):
            continue
        if domains & {d.lower() for d in entry.get("domains", [])}:
            out.append(entry)
    return out


INTEGRATIONS_LINE = re.compile(r"(?m)^integrations:[^\n]*\n(?:[ \t]+-[^\n]*\n)*")


def _write_integrations(root: Path, ids: list[str]) -> None:
    path = root / "project.yaml"
    text = path.read_text(encoding="utf-8")
    line = f"integrations: {json.dumps(ids, ensure_ascii=False)}   # veja: python3 .uah/uah.py integrations\n"
    if INTEGRATIONS_LINE.search(text):
        new = INTEGRATIONS_LINE.sub(lambda _m: line, text, count=1)
    elif re.search(r"(?m)^policy:", text):
        new = re.sub(r"(?m)^policy:", line.rstrip("\n") + "\npolicy:", text, count=1)
    else:
        new = text.rstrip("\n") + "\n" + line
    path.write_text(new, encoding="utf-8")
    try:
        cmd_compile(root)
    except PolicyError:
        path.write_text(text, encoding="utf-8")
        raise


def cmd_integrations(root: Path, action: str, ids: list[str]) -> None:
    known = catalog(root)
    for iid in ids:
        _expect(iid in known, f"integração desconhecida {iid!r}; disponíveis: {', '.join(sorted(known))}")
    try:
        enabled = list(load_h2(root).get("integrations") or [])
    except PolicyError:
        enabled = []
    if action == "list":
        recs = {e["id"] for e in recommend(root)}
        for iid, entry in sorted(known.items()):
            st = integration_status(entry)
            flags = ["ATIVA" if iid in enabled else "inativa",
                     "instalada" if st["installed"] else "não instalada"]
            if iid in recs and iid not in enabled:
                flags.append("RECOMENDADA para este projeto")
            print(f"{iid} — {entry.get('title')} [{', '.join(flags)}]")
            print(f"  etapa: {entry.get('stage')} · quando: {entry.get('when')}")
            print(f"  não usar: {entry.get('not_when')}")
            print(f"  como: {entry.get('how')}")
            print(f"  repo: {entry.get('repo')}" + (f" @ {st['commit']}" if st.get("commit") else ""))
        return
    if action == "install":
        for iid in ids:
            entry = known[iid]
            st = integration_status(entry)
            if st["installed"]:
                origin = "origem verificada" if st["verified"] else "ORIGEM NÃO VERIFICADA (remoto ≠ catálogo)"
                pin = "" if st["pinned"] is None else (" · commit fixado" if st["pinned"] else
                                                       f" · commit {st['commit']} ≠ ref {str(entry['ref'])[:12]}")
                print(f"{iid}: já instalada em {st['path']} ({origin}{pin})")
                continue
            repo_name = entry["repo"].rstrip("/").rsplit("/", 1)[-1]
            dest = Path.home() / ".claude" / "tools" / repo_name
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                out = subprocess.run(["git", "clone", entry["repo"], str(dest)], capture_output=True, text=True,
                                     timeout=600)
                _expect(out.returncode == 0, f"{iid}: git clone falhou: {out.stderr.strip()[:300]}")
            _expect(repo_key(run(["git", "-C", str(dest), "remote", "get-url", "origin"])) == repo_key(entry["repo"]),
                    f"{iid}: {dest} existe mas não é um clone de {entry['repo']}; resolva manualmente")
            if entry.get("ref"):
                out = subprocess.run(["git", "-C", str(dest), "checkout", "-q", str(entry["ref"])],
                                     capture_output=True, text=True, timeout=120)
                _expect(out.returncode == 0, f"{iid}: commit fixado {entry['ref']} indisponível: {out.stderr.strip()[:200]}")
            skill_src = (dest / entry.get("skill_subdir", ".")).resolve()
            _expect((skill_src / "SKILL.md").is_file(), f"{iid}: SKILL.md não encontrado em {skill_src}")
            link = skills_dir() / entry["skill_name"]
            _expect(not link.exists(), f"{iid}: {link} já existe e não é a skill esperada; resolva manualmente")
            skills_dir().mkdir(parents=True, exist_ok=True)
            link.symlink_to(skill_src, target_is_directory=True)
            commit = run(["git", "-C", str(dest), "rev-parse", "--short=12", "HEAD"])
            print(f"{iid}: instalada em {link} -> {skill_src} @ {commit}. Reinicie o Claude Code para a skill aparecer.")
            for req in entry.get("requires", []):
                print(f"  requisito: {req}")
        return
    if action in ("enable", "disable"):
        _expect(bool(ids), f"informe a(s) integração(ões) para {action}")
        new = list(enabled)
        for iid in ids:
            if action == "enable" and iid not in new:
                new.append(iid)
            if action == "disable" and iid in new:
                new.remove(iid)
        _write_integrations(root, new)
        for iid in ids:
            entry = known[iid]
            if action == "enable":
                st = integration_status(entry)
                print(f"{iid}: ativa" + ("" if st["installed"] else " — NÃO INSTALADA: rode `uah.py integrations install " + iid + "`"))
                for tip in entry.get("advice", []):
                    print(f"  dica: {tip}")
            else:
                print(f"{iid}: desativada")
        return
    raise PolicyError(f"ação desconhecida {action!r}")


def cmd_explain(root: Path) -> None:
    pol = resolve(root)
    yes = lambda b: "sim" if b else "não"  # noqa: E731
    print(f"Projeto `{pol['project']['id']}` — {pol['project'].get('title') or ''}".rstrip(" —"))
    print(f"Risco: {pol['risk']} · gate de plano (G1): {yes(pol['plan_gate'])} · checkpoint obrigatório (G4): "
          f"{yes(pol['g4_checkpoint'] == 'block')} · parada após {pol['max_attempts']} tentativa(s) falha(s)")
    state = "aprovado" if master_approved(root) else "não aprovado"
    sl = slices_lock(root)
    if pol["plan_gate"]:
        print(f"  Plano geral {state}. Antes da aprovação o agente só lê e edita: {', '.join(pol['plan_gate_paths'])}")
        if sl["mode"]:
            act = sl["active"]
            print(f"  Modo fatias: a execução exige fatia ativa e aprovada. Ativa: "
                  + (f"{act} ({_slice_state(root, act, sl)})" if act else "nenhuma — gate fechado"))
        if pol["gate_cli"]:
            print("  CLIs liberadas antes da aprovação: " + "; ".join(
                f"{g['script']} {'/'.join(g['subcommands'])} ({g['integration']})" for g in pol["gate_cli"]))
    print("\nNunca alterar (imutáveis): " + (", ".join(p for p in pol["immutable_paths"] if not p.endswith("/**") or p[:-3] not in pol["immutable_paths"]) or "—"))
    print("Alterar só com confirmação: " + (", ".join(p for p in pol["protected_paths"] if not p.endswith("/**") or p[:-3] not in pol["protected_paths"]) or "—"))
    print("\nBloqueado (deny):")
    for r in pol["bash_deny"]:
        print(f"  [{r['id']}] {r['reason']}")
    print("Pede confirmação (ask):")
    for r in pol["bash_ask"]:
        print(f"  [{r['id']}] {r['reason']}" + (" — sempre humano" if r.get("locked") else ""))
    allow = pol["settings"]["allow"]
    print("\nLiberado sem perguntar (settings_allow): " + (", ".join(allow) or "—"))
    if pol["temporary_grants"]:
        print("Concessões temporárias ativas: " + ", ".join(f"{g['id']} até {g['expires_at']}" for g in pol["temporary_grants"]))
    if pol["integrations"]:
        print("\nIntegrações ativas:")
        for item in pol["integrations"]:
            print(f"  {item['id']} ({'instalada' if item['installed'] else 'NÃO instalada'}) — {item['stage']}: {item['when']}")
            print(f"    como: {item['how']}")
    print("\nPrefixos dos ids: H0 universal · H1M/H1H risco · INT-* integração · H2 projeto · H3 tarefa.")


SLICE_RE = re.compile(r"^[0-9]+[a-z]?$")
EMPTY_SLICES = {"mode": False, "active": None, "approved": {}, "done": []}


def slice_path(root: Path, n: str) -> Path:
    return root / "plan" / "slices" / f"slice-{n}.md"


def slices_lock(root: Path) -> dict:
    data = read_json(runtime_dir(root) / "slices.lock.json", None)
    if not isinstance(data, dict):
        return json.loads(json.dumps(EMPTY_SLICES))
    for key, value in EMPTY_SLICES.items():
        data.setdefault(key, json.loads(json.dumps(value)))
    return data


def write_slices_lock(root: Path, data: dict) -> None:
    write_json(runtime_dir(root) / "slices.lock.json", data)


def _check_slice_id(n: str) -> str:
    n = str(n).strip()
    _expect(bool(SLICE_RE.match(n)), f"id de fatia inválido {n!r} (use 1, 2, 3a…)")
    return n


def _slice_state(root: Path, n: str, lock: dict) -> str:
    path = slice_path(root, n)
    if not path.is_file():
        return "ausente"
    entry = lock["approved"].get(n)
    if not entry:
        return "rascunho"
    if entry.get("sha256") != body_sha(path.read_text(encoding="utf-8")):
        return "modificada após aprovação"
    return "concluída" if n in lock["done"] else "aprovada"


def master_approved(root: Path) -> bool:
    plan = root / "plan" / "approved.md"
    lock = read_json(runtime_dir(root) / "plan.lock.json")
    return bool(lock and plan.is_file() and lock.get("sha256") == body_sha(plan.read_text(encoding="utf-8")))


def cmd_import_plan(root: Path, src: Path, slice_id: str | None = None) -> None:
    _expect(src.is_file(), f"arquivo não encontrado: {src}")
    text = src.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    home = str(Path.home())
    body = body.replace(home, "~")
    project_id = (load_h2(root).get("project") or {}).get("id", "")
    try:
        rel = src.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = src.name
    meta = {"status": "draft", "project_id": project_id, "source": rel, "imported_at": now_iso()}
    if slice_id is not None:
        n = _check_slice_id(slice_id)
        target = slice_path(root, n)
        meta["slice"] = n
        header = (f"> Fatia {n} importada de `{rel}`. Revise (requisitos REQ, aceite AC, fora do escopo, "
                  "critério de abandono) antes de `approve --slice`.\n\n")
        lock = slices_lock(root)
        was_approved = n in lock["approved"]
        lock["mode"] = True
        write_slices_lock(root, lock)
    else:
        target = root / "plan" / "approved.md"
        header = (f"> Importado de `{rel}`. Revise e complete (escopo, entregáveis com aceite, tarefas T-xxx) "
                  "antes de aprovar.\n\n")
        was_approved = (runtime_dir(root) / "plan.lock.json").is_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(join_frontmatter(meta, header + body.strip() + "\n"), encoding="utf-8")
    dest = target.relative_to(root).as_posix()
    print(f"import-plan: {rel} -> {dest} (draft)")
    if was_approved:
        print("Atenção: havia versão aprovada; o novo conteúdo reabre o gate G1 até nova aprovação.")


PLAN_REQUIRED = {
    "escopo/objetivo": r"(?im)^#+.*\b(escopo|scope|objetivo|goal|requisitos|requirements)\b",
    "critérios de aceite": r"(?i)\b(aceite|acceptance|pronto quando|definition of done|done when)\b",
}


def _approve_file(path: Path, allow_incomplete: bool, by: str, extra_meta: dict, label: str) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    meta_raw, body = split_frontmatter(text)
    _expect(len(body.strip()) > 40, f"{label} vazio")
    missing = [name for name, rx in PLAN_REQUIRED.items() if not re.search(rx, body)]
    if missing and not allow_incomplete:
        raise PolicyError(f"{label} incompleto: falta {', '.join(missing)} "
                          "(use --allow-incomplete para registrar a exceção)")
    digest = body_sha(text)
    try:
        meta = yaml.safe_load(meta_raw) if meta_raw else {}
    except yaml.YAMLError:
        meta = {}
    meta = meta if isinstance(meta, dict) else {}
    meta.update({"status": "approved", "approved_by": by, "approved_at": now_iso(), "revision": digest[:12]}, **extra_meta)
    path.write_text(join_frontmatter(meta, body), encoding="utf-8")
    _expect(body_sha(path.read_text(encoding="utf-8")) == digest, "falha ao regravar sem alterar o corpo")
    return digest, missing


def cmd_approve(root: Path, by: str | None, allow_incomplete: bool, slice_id: str | None = None) -> None:
    by = by or run(["git", "config", "user.name"], cwd=root) or os.environ.get("USER", "desconhecido")
    if slice_id is not None:
        n = _check_slice_id(slice_id)
        path = slice_path(root, n)
        _expect(path.is_file(), f"{path.relative_to(root)} não existe (import-plan --slice {n} ou slice new {n})")
        _expect(master_approved(root), "aprove (ou reaprove) o plano geral plan/approved.md antes das fatias")
        digest, missing = _approve_file(path, allow_incomplete, by, {}, f"fatia {n}")
        lock = slices_lock(root)
        lock["mode"] = True
        lock["approved"][n] = {"sha256": digest, "approved_by": by, "approved_at": now_iso(),
                               "path": path.relative_to(root).as_posix(),
                               "warnings": [f"incompleto: {m}" for m in missing]}
        lock["active"] = n
        if n in lock["done"]:
            lock["done"].remove(n)
        _update_state(root, {"slice": n}, f"fatia {n} aprovada por {by} (rev {digest[:12]}) e ativa")
        write_slices_lock(root, lock)  # por último
        print(f"approve: fatia {n} rev {digest[:12]} aprovada por {by} e ATIVA. Gate G1 liberado para esta fatia.")
        return
    plan = root / "plan" / "approved.md"
    _expect(plan.is_file(), "plan/approved.md não existe")
    digest, missing = _approve_file(plan, allow_incomplete, by, {}, "plano")
    lock = {"sha256": digest, "approved_by": by, "approved_at": now_iso(), "plan_path": "plan/approved.md",
            "uah_lite_version": UAH_LITE_VERSION, "warnings": [f"incompleto: {m}" for m in missing]}
    _update_state(root, {"plan_revision": digest[:12]}, f"plano aprovado por {by} (rev {digest[:12]})")
    write_json(runtime_dir(root) / "plan.lock.json", lock)  # por último: só libera o gate se tudo acima deu certo
    note = " (o projeto usa fatias: a execução segue a fatia ativa)" if slices_lock(root)["mode"] else ""
    print(f"approve: plano geral rev {digest[:12]} aprovado por {by}.{note}")


def cmd_slice(root: Path, action: str, n: str | None, title: str | None) -> None:
    lock = slices_lock(root)
    if action == "list":
        folder = root / "plan" / "slices"
        ids = sorted({p.stem.split("slice-", 1)[1] for p in folder.glob("slice-*.md")} | set(lock["approved"]),
                     key=lambda x: (int(re.match(r"\d+", x).group()), x))
        print(f"Plano geral: {'aprovado' if master_approved(root) else 'NÃO aprovado'} · modo fatias: "
              f"{'sim' if lock['mode'] else 'não'} · ativa: {lock['active'] or 'nenhuma'}")
        for i in ids:
            mark = "▶" if i == lock["active"] else " "
            print(f" {mark} fatia {i}: {_slice_state(root, i, lock)}")
        if not ids:
            print("  (nenhuma fatia; crie com `slice new N` ou `import-plan <arquivo> --slice N`)")
        return
    _expect(n is not None, f"informe o número da fatia para `slice {action}`")
    n = _check_slice_id(n)
    if action == "new":
        path = slice_path(root, n)
        _expect(not path.exists(), f"{path.relative_to(root)} já existe")
        tpl = (source_dir(root) / "templates" / "slice.md").read_text(encoding="utf-8")
        project_id = (load_h2(root).get("project") or {}).get("id", "")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(tpl, {"slice": n, "title": title or f"Fatia {n}", "project_id": project_id}),
                        encoding="utf-8")
        lock["mode"] = True
        write_slices_lock(root, lock)
        print(f"slice new: {path.relative_to(root)} criada (rascunho). Preencha e aprove com `approve --slice {n}`.")
        return
    if action == "activate":
        state = _slice_state(root, n, lock)
        _expect(state != "ausente", f"fatia {n} não existe")
        lock["mode"] = True
        lock["active"] = n
        write_slices_lock(root, lock)
        _update_state(root, {"slice": n}, f"fatia {n} ativa ({state})")
        gate = "liberado" if state == "aprovada" else "FECHADO até aprovar (`approve --slice " + n + "`)"
        print(f"slice activate: fatia {n} ({state}) ativa; gate G1 {gate}.")
        return
    if action == "done":
        _expect(n in lock["approved"], f"fatia {n} não foi aprovada; não pode ser concluída")
        if n not in lock["done"]:
            lock["done"].append(n)
        if lock["active"] == n:
            lock["active"] = None
        write_slices_lock(root, lock)
        _update_state(root, {"slice": ""}, f"fatia {n} concluída")
        print(f"slice done: fatia {n} concluída. Nenhuma fatia ativa: o gate G1 fica fechado até a próxima "
              "ser aprovada (planeje-a com omc-plan e `import-plan … --slice N`).")
        return
    raise PolicyError(f"ação desconhecida {action!r}")


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


def _state_meta(root: Path) -> dict:
    path = root / "state" / "current.md"
    if not path.is_file():
        return {}
    try:
        meta = yaml.safe_load(split_frontmatter(path.read_text(encoding="utf-8"))[0]) or {}
    except yaml.YAMLError:
        return {}
    return meta if isinstance(meta, dict) else {}


def _ledger_append(root: Path, record: dict) -> None:
    path = root / LEDGER_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": now_iso(), **record}, ensure_ascii=False) + "\n")


def ledger_summary(root: Path) -> dict | None:
    """Custo por tarefa CONCLUÍDA E VALIDADA (status done), não tokens brutos."""
    path = root / LEDGER_REL
    if not path.is_file():
        return None
    done, failed = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("event") == "done":
            done.append(rec)
        elif rec.get("event") == "failed":
            failed += 1
    costs = [r["cost"] for r in done if isinstance(r.get("cost"), (int, float))]
    tokens = [r["tokens"] for r in done if isinstance(r.get("tokens"), int)]
    attempts = [r.get("attempts", 1) for r in done]
    by_level: dict[str, list[float]] = {}
    for r in done:
        if isinstance(r.get("cost"), (int, float)):
            by_level.setdefault(r.get("level") or "?", []).append(r["cost"])
    return {"done": len(done), "failed_attempts": failed,
            "cost_total": round(sum(costs), 4) if costs else None,
            "cost_per_validated": round(sum(costs) / len(costs), 4) if costs else None,
            "tokens_per_validated": int(sum(tokens) / len(tokens)) if tokens else None,
            "attempts_mean": round(sum(attempts) / len(attempts), 2) if attempts else None,
            "cost_by_level": {k: round(sum(v) / len(v), 4) for k, v in by_level.items()}}


def cmd_checkpoint(root: Path, task: str | None, status: str, next_action: str, blockers: list[str], note: str | None,
                   failed: str | None = None, reset_attempts: bool = False, cost: float | None = None,
                   tokens: int | None = None, level: str | None = None) -> None:
    _expect(level is None or level in LEVELS, f"--level deve ser {', '.join(LEVELS)}")
    lock = read_json(runtime_dir(root) / "plan.lock.json", {}) or {}
    policy = read_json(runtime_dir(root) / "policy.json", {}) or {}
    max_attempts = int(policy.get("max_attempts", 5))
    prev = _state_meta(root)
    same_task = bool(task) and str(prev.get("task_id") or "") == str(task)
    attempts = int(prev.get("failed_attempts") or 0) if same_task else 0
    locked = bool(prev.get("blocked_by_attempts")) and same_task
    if locked and not reset_attempts:
        raise PolicyError(f"tarefa {task} BLOQUEADA após {attempts} tentativa(s) falha(s) (limite {max_attempts}). "
                          "Um humano precisa decidir e rodar `checkpoint --task … --reset-attempts` "
                          "(replanejar, mudar o nível ou aceitar o bloqueio).")
    if reset_attempts:
        attempts, locked = 0, False
    if failed:
        attempts += 1
        _ledger_append(root, {"event": "failed", "task": task, "attempt": attempts, "reason": failed, "level": level})
        if attempts >= max_attempts:
            locked = True
            status = "blocked"
            blockers = [*blockers, f"{attempts} tentativas falharam (limite {max_attempts}): {failed}"]
            next_action = "PARAR: humano decide (replanejar, subir o nível de raciocínio ou abandonar a tarefa)"
    if status == "done" and task:
        _ledger_append(root, {"event": "done", "task": task, "attempts": attempts + 1, "level": level,
                              "cost": cost, "tokens": tokens})
        attempts = 0
    fields = {
        "task_id": task,
        "status": status,
        "next_action": next_action,
        "blockers": "; ".join(blockers),
        "operator": run(["git", "config", "user.name"], cwd=root) or os.environ.get("USER", ""),
        "workspace_commit": _workspace_commit(root),
        "plan_revision": str(lock.get("sha256", ""))[:12],
        "failed_attempts": attempts,
        "blocked_by_attempts": locked,
    }
    active = slices_lock(root)["active"]
    if active:
        fields["slice"] = active
    log = f"{task or '-'} · {status} · próximo: {next_action}" + (f" · fatia {active}" if active else "") \
        + (f" · falha {attempts}/{max_attempts}: {failed}" if failed else "") + (f" · {note}" if note else "")
    _update_state(root, fields, log)
    print(f"checkpoint: {task or '-'} {status} · commit {fields['workspace_commit'] or '(sem git)'}"
          + (f" · fatia {active}" if active else "")
          + (f" · tentativas falhas {attempts}/{max_attempts}" if attempts else ""))
    if locked:
        print(f"PARE: {attempts} tentativas falharam. Alterações materiais ficam bloqueadas até um humano rodar "
              f"`python3 .uah/uah.py checkpoint --task {task} --status active --next \"…\" --reset-attempts`.")
    if any(i.get("id") == "specboard" for i in policy.get("integrations", [])):
        print("specboard: atualize o painel para refletir este checkpoint — "
              "`python <specboard.py> validate && python <specboard.py> build` (etapas → executado + evidência).")


# --------------------------------------------------------------- setup-env

# Ferramentas instaláveis sem sudo: versão fixa + checksum publicado pelo projeto.
SETUP_TOOLS = {
    "quarto": {"version": "1.10.19", "check": ["quarto", "--version"],
               "base": "https://github.com/quarto-dev/quarto-cli/releases/download/v{v}/",
               "asset": "quarto-{v}-{plat}.tar.gz", "sums": "quarto-{v}-checksums.txt", "bin": "bin/quarto",
               "plats": {("Linux", "amd64"): "linux-amd64", ("Linux", "arm64"): "linux-arm64",
                         ("Darwin", "amd64"): "macos", ("Darwin", "arm64"): "macos"},
               "for": "publish-documents", "docs": "https://quarto.org/docs/get-started/"},
    "d2": {"version": "0.9.0", "check": ["d2", "--version"],
           "base": "https://github.com/terrastruct/d2/releases/download/v{v}/",
           "asset": "d2-v{v}-{plat}.tar.gz", "sums": "SHA256SUMS", "bin": "bin/d2",
           "plats": {("Linux", "amd64"): "linux-amd64", ("Linux", "arm64"): "linux-arm64",
                     ("Darwin", "amd64"): "macos-amd64", ("Darwin", "arm64"): "macos-arm64"},
           "for": "sci-figures", "docs": "https://d2lang.com/tour/install"},
}
OMC_STEPS = ("No Claude Code: `/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode`, "
             "`/plugin install oh-my-claudecode` e depois `/omc-setup` (CLI opcional: `npm i -g oh-my-claude-sisyphus@latest`)")
MOLAR_VIS_STEPS = ("requer Rust: `git clone https://github.com/yesint/molar_vis && cd molar_vis && "
                   "~/.local/share/sci-figures/venv/bin/pip install maturin numpy && cd crates/molar_vis_py && "
                   "VIRTUAL_ENV=~/.local/share/sci-figures/venv maturin develop --release`")
SYSTEM_PACKAGES = [  # (comando verificado, pacote apt, para quê)
    ("xelatex", "texlive-xetex texlive-lang-portuguese", "PDF de artigo (journal-scientific)"),
    ("soffice", "libreoffice-writer", "prévia do DOCX e SVG→PDF"),
    ("pdftoppm", "poppler-utils", "verificação e prévia de PDF"),
    ("rsvg-convert", "librsvg2-bin", "SVG→PDF mais fiel (opcional)"),
]


def _platform() -> tuple[str, str]:
    import platform
    machine = platform.machine().lower()
    arch = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine, machine)
    return platform.system(), arch


def _fetch(url: str, dest: Path) -> None:
    import urllib.request
    with urllib.request.urlopen(url, timeout=120) as resp, open(dest, "wb") as fh:  # noqa: S310 (URLs fixas)
        shutil.copyfileobj(resp, fh)


def install_tool(name: str) -> str:
    """Baixa a versão fixa, confere o SHA-256 no arquivo de checksums do projeto e liga em ~/.local/bin."""
    import tarfile
    import tempfile
    spec = SETUP_TOOLS[name]
    plat = spec["plats"].get(_platform())
    _expect(plat is not None, f"{name}: plataforma {_platform()} sem binário automático — veja {spec['docs']}")
    version = spec["version"]
    base = os.environ.get("UAH_SETUP_BASE_URL", "").rstrip("/")
    base = f"{base}/{name}/" if base else spec["base"].format(v=version)
    asset = spec["asset"].format(v=version, plat=plat)
    with tempfile.TemporaryDirectory() as tmp:
        tarball, sums = Path(tmp) / asset, Path(tmp) / "sums.txt"
        _fetch(base + asset, tarball)
        _fetch(base + spec["sums"].format(v=version), sums)
        expected = next((ln.split()[0] for ln in sums.read_text(encoding="utf-8").splitlines()
                         if ln.strip().endswith(asset)), None)
        _expect(expected is not None, f"{name}: {asset} não consta do arquivo de checksums")
        got = sha256_bytes(tarball.read_bytes())
        _expect(got == expected, f"{name}: checksum NÃO confere ({got[:12]} ≠ {expected[:12]}) — nada instalado")
        dest = Path.home() / ".local" / "opt" / f"{name}-{version}"
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        with tarfile.open(tarball) as tf:
            members = tf.getmembers()
            top = {m.name.split("/", 1)[0] for m in members if m.name.strip("/")}
            strip = len(top) == 1 and all("/" in m.name or m.isdir() for m in members)
            keep = []
            for m in members:
                rel = m.name.split("/", 1)[1] if strip and "/" in m.name else ("" if strip else m.name)
                if rel:
                    m.name = rel
                    keep.append(m)
            # filtro "data": recusa caminhos absolutos, `..` e links que escapem do destino
            tf.extractall(dest, members=keep, filter="data")
    binary = dest / spec["bin"]
    _expect(binary.is_file(), f"{name}: {spec['bin']} não encontrado no pacote")
    binary.chmod(0o755)
    link = Path.home() / ".local" / "bin" / name
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(binary)
    return f"{name} {version} instalado em {dest} (checksum conferido) → {link}"


def cmd_setup_env(root: Path, install: bool, wanted: list[str] | None) -> int:
    rows: list[tuple[str, str, str]] = []
    add = lambda level, item, msg: rows.append((level, item, msg))  # noqa: E731
    known = catalog(root)
    if wanted == ["all"]:
        selected = sorted(known)
    elif wanted:
        bad = [w for w in wanted if w not in known]
        _expect(not bad, f"integração desconhecida: {', '.join(bad)}; disponíveis: {', '.join(sorted(known))}")
        selected = wanted
    else:
        try:
            selected = list(load_h2(root).get("integrations") or [])
        except (PolicyError, yaml.YAMLError):
            selected = []
    add("INFO", "seleção", f"integrações: {', '.join(selected) or 'nenhuma'} "
                           f"(use --integrations id1,id2 ou all; padrão = as ativas no project.yaml)")

    local_bin = str(Path.home() / ".local" / "bin")
    add("OK" if local_bin in os.environ.get("PATH", "").split(os.pathsep) else "WARN", "PATH",
        f"{local_bin} {'está' if local_bin in os.environ.get('PATH', '') else 'NÃO está'} no PATH"
        + ("" if local_bin in os.environ.get("PATH", "") else " — acrescente `export PATH=\"$HOME/.local/bin:$PATH\"` ao ~/.bashrc"))
    add("OK" if shutil.which("git") else "MISSING", "git", "presente" if shutil.which("git") else "ausente — instale o git")

    link = skills_dir() / "uah-init"
    if link.exists():
        add("OK", "skill uah-init", f"em {link}")
    elif install and (HERE / "SKILL.md").is_file() and HERE.resolve() != runtime_dir(root).resolve():
        skills_dir().mkdir(parents=True, exist_ok=True)
        link.symlink_to(HERE, target_is_directory=True)
        add("DONE", "skill uah-init", f"ligada: {link} → {HERE}")
    else:
        add("MISSING", "skill uah-init", f"`ln -s <clone>/skills/uah-init {link}`")

    omc = run(["omc", "--version"]) or (Path.home() / ".claude" / "plugins" / "cache" / "omc").is_dir()
    add("OK" if omc else "MANUAL", "OMC", "presente" if omc else f"recomendado (entrevista e planejamento). {OMC_STEPS}")

    for iid in selected:
        entry = known[iid]
        st = integration_status(entry)
        if st["installed"]:
            note = "origem verificada" if st["verified"] else "ORIGEM NÃO VERIFICADA"
            if st["pinned"] is False:
                note += f", commit {st['commit']} ≠ fixado {str(entry.get('ref'))[:12]}"
            add("OK" if st["verified"] else "WARN", f"skill {iid}", f"{st['path']} ({note})")
        elif install:
            cmd_integrations(root, "install", [iid])
            add("DONE", f"skill {iid}", "instalada no commit fixado (reinicie o Claude Code)")
        else:
            add("MISSING", f"skill {iid}", f"`uah.py integrations install {iid}` (ou setup-env --install)")

    needed_tools = {name for name, spec in SETUP_TOOLS.items() if spec["for"] in selected}
    for name, spec in SETUP_TOOLS.items():
        present = run(spec["check"])
        if present:
            add("OK", name, present.splitlines()[0])
        elif name not in needed_tools:
            add("INFO", name, f"ausente (só necessário para {spec['for']})")
        elif install:
            add("DONE", name, install_tool(name))
        else:
            add("MISSING", name, f"necessário para {spec['for']} — `setup-env --install` instala a versão {spec['version']}")

    if "sci-figures" in selected:
        st = integration_status(known["sci-figures"])
        venv_py = Path(os.environ.get("SCI_FIGURES_VENV", Path.home() / ".local/share/sci-figures/venv")) / "bin" / "python"
        stack_ok = venv_py.is_file() and run([str(venv_py), "-c", "import rdkit, ase, matplotlib, cairosvg"]) is not None
        if stack_ok:
            add("OK", "venv sci-figures", str(venv_py.parent.parent))
        elif install and st["installed"]:
            out = subprocess.run([sys.executable, str(Path(st["path"]) / "scripts" / "figs.py"), "setup"],
                                 capture_output=True, text=True, timeout=3600)
            add("DONE" if out.returncode == 0 else "MISSING", "venv sci-figures",
                (out.stdout or out.stderr).strip().splitlines()[-1] if (out.stdout or out.stderr).strip() else "")
        else:
            add("MISSING", "venv sci-figures", "`figs.py setup` (RDKit, ASE, matplotlib, cairosvg)")
        has_mv = venv_py.is_file() and run([str(venv_py), "-c", "import molar_vis"]) is not None
        add("OK" if has_mv else "MANUAL", "molar_vis", "presente" if has_mv else f"opcional (molecule-3d), {MOLAR_VIS_STEPS}")

    missing_pkgs = [(c, pkg, why) for c, pkg, why in SYSTEM_PACKAGES if not shutil.which(c)]
    if "publish-documents" in selected or wanted == ["all"]:
        for c, pkg, why in missing_pkgs:
            add("MANUAL", c, f"{why} — pacote {pkg}")
        if missing_pkgs:
            add("MANUAL", "sudo", "Debian/Ubuntu: `sudo apt install " + " ".join(p for _, p, _ in missing_pkgs) + "`")

    for level, item, msg in rows:
        print(f"[{level}] {item}: {msg}")
    if not install and any(level == "MISSING" for level, _, _ in rows):
        print("Para instalar o que é automático: `python3 .uah/uah.py setup-env --install` (pede confirmação no Claude Code).")
    return 1 if any(level == "MISSING" for level, _, _ in rows) else 0


def cmd_preflight(root: Path) -> int:
    results: list[tuple[str, str]] = []

    def add(level: str, msg: str):
        results.append((level, msg))

    policy = read_json(runtime_dir(root) / "policy.json")
    fresh: dict | None = None
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

    sl = slices_lock(root)
    if sl["mode"]:
        active = sl["active"]
        if not active:
            add("WARN", "modo fatias: nenhuma fatia ativa — gate G1 fechado (aprove a próxima com `approve --slice N`)")
        else:
            st = _slice_state(root, active, sl)
            add("OK" if st == "aprovada" else "WARN", f"fatia ativa {active}: {st}")
    meta_now = _state_meta(root)
    if meta_now.get("blocked_by_attempts"):
        add("FAIL", f"tarefa {meta_now.get('task_id')} bloqueada após {meta_now.get('failed_attempts')} tentativa(s) "
                    "falha(s): humano decide e roda `checkpoint --reset-attempts`")
    summary = ledger_summary(root)
    if summary and summary["done"]:
        cost = (f" · custo por tarefa validada {summary['cost_per_validated']}" if summary["cost_per_validated"] is not None
                else " · custo não registrado (use --cost ao concluir)")
        add("OK", f"tarefas validadas: {summary['done']} · tentativas médias {summary['attempts_mean']}"
                  f" · falhas registradas {summary['failed_attempts']}{cost}")
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
    for item in (fresh or {}).get("integrations", []):
        if item["installed"]:
            add("OK", f"integração {item['id']} instalada" + (f" @ {item['commit']}" if item.get("commit") else ""))
        else:
            add("WARN", f"integração {item['id']} ativa mas não instalada — `uah.py integrations install {item['id']}`")
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
    p.add_argument("--domains", default="", help="rótulos separados por vírgula, ex.: literatura,quimica-computacional")
    p.add_argument("--integrations", default="", help="ids separados por vírgula, ex.: specboard,calcboard")
    p = sub.add_parser("integrations", help="lista, instala, ativa ou desativa integrações externas")
    p.add_argument("action", nargs="?", default="list", choices=("list", "install", "enable", "disable"))
    p.add_argument("ids", nargs="*")
    sub.add_parser("explain", help="explica as regras efetivas em linguagem simples")
    p = sub.add_parser("setup-env", help="verifica a máquina e, com --install, instala o que dá sem sudo")
    p.add_argument("--install", action="store_true", help="instala de fato (sem isso, só o relatório)")
    p.add_argument("--integrations", default="", help="ids separados por vírgula, ou `all` (padrão: ativas no projeto)")
    p = sub.add_parser("slice", help="fatias de MVP: list | new N | activate N | done N")
    p.add_argument("action", nargs="?", default="list", choices=("list", "new", "activate", "done"))
    p.add_argument("n", nargs="?")
    p.add_argument("--title")
    sub.add_parser("compile", help="resolve H0–H3 e escreve policy.json + settings.json")
    p = sub.add_parser("import-plan", help="importa plano/spec do OMC")
    p.add_argument("source")
    p.add_argument("--slice", dest="slice_id", help="importa como fatia N (plan/slices/slice-N.md)")
    p = sub.add_parser("approve", help="aprova a revisão atual do plano (decisão humana)")
    p.add_argument("--by")
    p.add_argument("--allow-incomplete", action="store_true")
    p.add_argument("--slice", dest="slice_id", help="aprova a fatia N em vez do plano geral")
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
    p.add_argument("--failed", metavar="MOTIVO", help="registra uma tentativa falha (verify/teste reprovou)")
    p.add_argument("--reset-attempts", action="store_true", help="desbloqueia após o limite de tentativas (humano)")
    p.add_argument("--level", choices=LEVELS, help="nível de raciocínio da tarefa (leve|padrão|crítico)")
    p.add_argument("--cost", type=float, help="custo da tarefa (ex.: USD do /cost do Claude Code) ao concluir")
    p.add_argument("--tokens", type=int, help="tokens da tarefa ao concluir")
    sub.add_parser("preflight", help="verificações antes de retomar")
    sub.add_parser("status", help="alias de preflight")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.cmd == "init":
            split = lambda v: [x.strip() for x in v.split(",") if x.strip()]  # noqa: E731
            cmd_init(root, args.project_id, args.title, args.risk, args.python, split(args.domains), split(args.integrations))
        elif args.cmd == "integrations":
            cmd_integrations(root, args.action, args.ids)
        elif args.cmd == "setup-env":
            ids = [x.strip() for x in args.integrations.split(",") if x.strip()] or None
            return cmd_setup_env(root, args.install, ids)
        elif args.cmd == "explain":
            cmd_explain(root)
        elif args.cmd == "compile":
            cmd_compile(root)
        elif args.cmd == "import-plan":
            cmd_import_plan(root, Path(args.source), args.slice_id)
        elif args.cmd == "approve":
            cmd_approve(root, args.by, args.allow_incomplete, args.slice_id)
        elif args.cmd == "slice":
            cmd_slice(root, args.action, args.n, args.title)
        elif args.cmd == "task":
            cmd_task(root, args.task_id, args.hours, args.grant, args.clear)
        elif args.cmd == "checkpoint":
            cmd_checkpoint(root, args.task, args.status, args.next_action, args.blocker, args.note,
                           args.failed, args.reset_attempts, args.cost, args.tokens, args.level)
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
