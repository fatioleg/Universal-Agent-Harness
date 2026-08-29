#!/usr/bin/env python3
"""Validate the Universal Agent Harness repository deterministically."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    print("Missing validation dependency. Run: python -m pip install -r requirements-dev.txt")
    raise SystemExit(2) from exc


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "HARNESS.md",
    "VERSION",
    "CHANGELOG.md",
    "requirements-dev.txt",
    "core/universal.yaml",
    "core/invariants.yaml",
    "core/merge-policy.yaml",
    "schemas/project-input.schema.json",
    "schemas/resolved-harness.schema.json",
    "bootstrap/BOOTSTRAP.md",
    "bootstrap/NEW-PROJECT.md",
    "bootstrap/project-input.example.yaml",
    "platforms/CODEX.md",
    "platforms/CLAUDE-CODE.md",
    "templates/project/AGENTS.md.template",
    "templates/project/CLAUDE.md.template",
    "templates/project/project.yaml.template",
    "templates/project/harness.lock.yaml.template",
    "evals/bootstrap-cases.yaml",
    ".github/workflows/validate.yml",
    # v0.3.0 additions
    "core/policies/override-protocol.md",
    "core/principles/README.md",
    "core/principles/01-preserve-sources.md",
    "core/principles/02-maintain-provenance.md",
    "core/principles/03-least-privilege.md",
    "core/principles/04-verify-critical-outputs.md",
    "core/principles/05-expose-failures.md",
    "core/principles/06-maintain-state.md",
    "core/principles/07-progressive-disclosure.md",
    "core/principles/08-prefer-deterministic.md",
    "core/principles/09-reproducibility.md",
    "core/schemas/extension/state.schema.json",
    "core/schemas/extension/evidence-ledger.schema.json",
    "core/schemas/extension/decisions.schema.json",
    "core/schemas/extension/tool-contract.schema.json",
    "core/schemas/extension/permission-profile.schema.json",
    "core/schemas/extension/failure-registry.schema.json",
    "core/schemas/extension/eval-result.schema.json",
    "core/schemas/extension/observability-run.schema.json",
    "evals/catalog.md",
    "archetypes/README.md",
    "archetypes/scientific-research.md",
    "archetypes/computational-science.md",
    "archetypes/computational-chemistry.md",
    "archetypes/literature-review.md",
    "archetypes/knowledge-base.md",
    "archetypes/data-analysis.md",
    "archetypes/software-development.md",
    "archetypes/document-production.md",
    "archetypes/grant-project-proposal.md",
    "skills/classify-project/SKILL.md",
    "skills/classify-project/questions.md",
    "skills/classify-project/decision-tree.md",
    "skills/classify-project/output-template.md",
    "contracts/tools/README.md",
    "contracts/tools/check-invariants.yaml",
    "contracts/tools/diff-harness.yaml",
    "contracts/tools/verify-artifact.yaml",
    "contracts/tools/list-events.yaml",
    "contracts/tools/sensor-trend.yaml",
    "contracts/tools/lock-drift-check.yaml",
    "contracts/tools/scaffold-project.yaml",
    "examples/README.md",
    "docs/agent-topology.md",
    "docs/autonomy-levels.md",
    "docs/glossary.md",
    "docs/references.md",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_yaml(relative: str):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(relative: str):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def require_unique(items: list[dict], key: str, label: str) -> None:
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        fail(f"duplicate {label}: {values}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {missing}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(
        r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version
    ):
        fail(f"VERSION is not semantic versioning: {version!r}")

    yaml_paths = [
        "core/universal.yaml",
        "core/invariants.yaml",
        "core/merge-policy.yaml",
        "bootstrap/project-input.example.yaml",
        "evals/bootstrap-cases.yaml",
        "templates/project/project.yaml.template",
        "templates/project/harness.lock.yaml.template",
    ]
    yaml_docs = {path: load_yaml(path) for path in yaml_paths}

    project_schema = load_json("schemas/project-input.schema.json")
    resolved_schema = load_json("schemas/resolved-harness.schema.json")
    Draft202012Validator.check_schema(project_schema)
    Draft202012Validator.check_schema(resolved_schema)

    project_example = yaml_docs["bootstrap/project-input.example.yaml"]
    Draft202012Validator(
        project_schema, format_checker=FormatChecker()
    ).validate(project_example)
    project_template = yaml_docs["templates/project/project.yaml.template"]
    Draft202012Validator(
        project_schema, format_checker=FormatChecker()
    ).validate(project_template)
    lock_template = yaml_docs["templates/project/harness.lock.yaml.template"]
    Draft202012Validator(resolved_schema).validate(lock_template)

    invariants = yaml_docs["core/invariants.yaml"]["invariants"]
    require_unique(invariants, "id", "invariant IDs")
    unlocked = [item["id"] for item in invariants if item.get("enforcement") != "locked"]
    if unlocked:
        fail(f"unlocked universal invariants: {unlocked}")

    cases = yaml_docs["evals/bootstrap-cases.yaml"]["cases"]
    require_unique(cases, "id", "eval IDs")

    for entrypoint in ("AGENTS.md", "CLAUDE.md"):
        size = (ROOT / entrypoint).stat().st_size
        if size > 8192:
            fail(f"{entrypoint} is {size} bytes; keep platform entrypoints under 8 KiB")

    for entrypoint in ("AGENTS.md", "CLAUDE.md"):
        text = (ROOT / entrypoint).read_text(encoding="utf-8")
        for reference in ("HARNESS.md", "bootstrap/BOOTSTRAP.md"):
            if reference not in text or not (ROOT / reference).exists():
                fail(f"{entrypoint} does not route to existing {reference}")

    # v0.3.0 additions
    extension_schemas = [
        "core/schemas/extension/state.schema.json",
        "core/schemas/extension/evidence-ledger.schema.json",
        "core/schemas/extension/decisions.schema.json",
        "core/schemas/extension/tool-contract.schema.json",
        "core/schemas/extension/permission-profile.schema.json",
        "core/schemas/extension/failure-registry.schema.json",
        "core/schemas/extension/eval-result.schema.json",
        "core/schemas/extension/observability-run.schema.json",
    ]
    for relative in extension_schemas:
        schema = load_json(relative)
        Draft202012Validator.check_schema(schema)

    archetypes_readme = (ROOT / "archetypes" / "README.md").read_text(
        encoding="utf-8"
    )
    if "not H1 packages" not in archetypes_readme:
        fail("archetypes/README.md missing 'not H1 packages' disclaimer")

    skill_text = (ROOT / "skills" / "classify-project" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    import re as _re
    fm_match = _re.match(r"^---\n(.*?)\n---", skill_text, _re.DOTALL)
    if not fm_match:
        fail("skills/classify-project/SKILL.md missing YAML frontmatter")
    fm = fm_match.group(1)
    if "name: classify-project" not in fm:
        fail("skills/classify-project/SKILL.md frontmatter missing 'name'")
    if "description:" not in fm:
        fail("skills/classify-project/SKILL.md frontmatter missing 'description'")

    tool_contract_schema = load_json(
        "core/schemas/extension/tool-contract.schema.json"
    )
    tool_contract_paths = sorted((ROOT / "contracts" / "tools").glob("*.yaml"))
    tool_contracts = []
    for path in tool_contract_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        Draft202012Validator(tool_contract_schema).validate(data)
        tool_contracts.append(data)
    require_unique(
        [{"tool_id": c["tool_id"]} for c in tool_contracts],
        "tool_id",
        "tool contract IDs",
    )

    print(f"PASS: Universal Agent Harness {version}")
    print(f"PASS: {len(REQUIRED_FILES)} required files")
    print(f"PASS: {len(invariants)} locked invariants")
    print(f"PASS: {len(cases)} bootstrap eval cases")
    print(f"PASS: {len(extension_schemas)} extension schemas")
    print(f"PASS: {len(tool_contracts)} tool contracts")


if __name__ == "__main__":
    main()
