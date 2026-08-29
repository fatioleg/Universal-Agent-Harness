# Changelog

## 0.2.0 — 2026-08-29

- added separate, thin entrypoints for Codex and Claude Code;
- moved shared behavior to the canonical `HARNESS.md`;
- documented Codex, Codex Cloud, and Claude Code discovery behavior;
- added a reusable new-project request;
- added minimal project materialization templates;
- added deterministic repository validation and GitHub Actions;
- added target-platform fields to project input and resolved harness schemas.

## 0.3.0 — 2026-08-29

- added `archetypes/` with README and 9 reference-pattern stubs;
- added `core/principles/` with 9 markdown rationale files;
- added `core/policies/override-protocol.md`;
- added `core/schemas/extension/` with 8 JSON Schemas (state, evidence-ledger, decisions, tool-contract, permission-profile, failure-registry, eval-result, observability-run);
- added `evals/catalog.md` listing 10 universal eval categories;
- added `skills/classify-project/` with SKILL.md and supporting files for interactive classification;
- added `contracts/tools/` with README and 7 tool contract YAMLs (no implementations per AD-003);
- added `docs/agent-topology.md`, `docs/autonomy-levels.md`, `docs/references.md`, `docs/glossary.md`;
- added `examples/` placeholder;
- extended `scripts/validate_repo.py` with new required-file checks and schema/contract validation;
- documented AD-008 and AD-009 in `docs/DECISIONS.md`.

## 0.1.0 — 2026-08-29

- created the initial declarative bootstrap;
- defined universal invariants, typed merge rules, schemas, and bootstrap evals;
- established dry-run before materialization and minimum sufficient topology.

