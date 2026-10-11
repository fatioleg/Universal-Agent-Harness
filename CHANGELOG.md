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

## 0.4.0 — 2026-08-29

- added `archetypes/full-sdd-project.md` (Spec-Driven Development lifecycle, named subagent roles, persistent memory, gates, handoffs);
- added `archetypes/knowledge-digestion.md` (caveman + MarkItDown + Graphify + Obsidian + optional NotebookLM pipeline as capability bundle);
- added `docs/sdd.md` with SPEC-00 through SPEC-04, Context Pack, Subagent Report, Handoff, Issues, Decisions, Gates, Completion checklist;
- added `docs/knowledge-digestion.md` describing the five-stage pipeline with role, when-to-use, and tradeoffs per stage;
- added `contracts/tools/caveman-compress.yaml`, `markitdown-normalize.yaml`, `graphify-build.yaml`, `obsidian-interface.yaml`, `notebooklm-explore.yaml` (12 tool contracts total);
- added capabilities `knowledge-digestion-pipeline`, `sdd-workflow`, `subagent-orchestration`, `checkpoint-handoff` to `core/universal.yaml`;
- documented AD-011 recording the v0.4.0 scope.

## 0.5.0 — 2026-08-29

- added `docs/tdd.md` — TDD red-green-refactor (Kent Beck / Fowler), test pyramid (Fowler / Ham Vocke), agent testing pyramid (LangWatch), mutation testing and approved scenarios (Böckeler), characterization tests (Feathers), test discipline rules and Definition of Done;
- added `docs/brownfield.md` — Legacy Code Change Algorithm (Feathers), characterization tests, seams, Sprout / Wrap techniques, agent-specific brownfield cautions (Hashimoto), safety checklist;
- added `docs/adr-template.md` — canonical ADR format (Context / Decision / Alternatives / Consequences) per AWS, Microsoft Azure, adr.github.io, with worked example;
- added 3 extension schemas: `acceptance-criterion.schema.json`, `test-case.schema.json`, `change-request.schema.json` (REQ→AC→Test→Impl traceability IDs);
- added `core/principles/10-proportional-design.md` — the smallest sufficient architecture satisfies the actual risks and constraints;
- added 3 project templates: `acceptance-criteria.template.md`, `test-cases.template.md`, `task-plan.template.md`;
- updated `docs/sdd.md` with requirement traceability, change protocol, prohibitions, Gate A–D, Definition of Done for tasks;
- updated `archetypes/full-sdd-project.md` and `archetypes/software-development.md` with cross-references to the new docs;
- updated `docs/references.md` with primary sources for TDD, test pyramid, brownfield, SDD enterprise practice, and ADRs;
- documented AD-012 recording the v0.5.0 scope.

## 0.5.1 — 2026-08-29

- added `docs/assets/harness-analogy.png` illustrating the
  energy-vs-intelligence parallel that motivates the harness
  concept, surfaced in `README.md` directly under the title;
- expanded `skills/classify-project/` from 15 to 24 questions
  across 6 groups, covering all 11 archetypes, 22 capabilities,
  12 tool contracts, and 11 schemas. Skill description and
  coverage section updated;
- fixed `eval-result` schema trigger missing from
  decision-tree.md (any project with running evals);
- deduped `AD-009` in `docs/DECISIONS.md` (renamed GitHub
  distribution decision to AD-013);
- heavy 3-pass audit (validator + static checks + spec-to-code
  compliance) executed; report at
  `docs/superpowers/audits/2026-08-29-v050-audit.md`. Result:
  PASS-WITH-NOTES, 0 critical, 0 important, 6 minor all
  AD-documented.

## 0.6.0 — 2026-10-11

- fixed CI: `actions/setup-python` cache now points to `requirements-dev.txt`; CI also runs behavioral tests;
- single product version: `VERSION` is the only release version; `core/universal.yaml` no longer declares
  `harness.version`; lock template pins `universal-agent-harness@0.6.0`; validator enforces consistency;
- bootstrap cases moved to the `BEVAL-*` namespace (`EVAL-*` stays the universal catalog);
- added UAH-lite (`skills/uah-init/`): `uah.py` (init, compile, import-plan, approve, task, checkpoint, preflight),
  stdlib-only Claude Code hook `uah_guard.py` (PreToolUse, SessionStart, Stop), H0 and risk H1 profiles, templates;
- deterministic fail-closed H0–H3 resolver compiled to `.claude/settings.json` permissions and hooks;
- plan approval bound to the sha256 of the plan body (G1); checkpoint/resume state in `state/current.md` (G4);
- OMC bound by artifacts (`.omc/plans`, `.omc/specs`) and pinned with `omc capabilities lock/check`;
- added `tests/test_uah_lite.py` (30 behavioral tests: AT-01/02/03/05/07/09/14 plus 14 regressions from an independent review — grant scope, fail-closed guard, quote-aware shell parsing, literal-directory protection, YAML-safe init, G4 with accented paths) and `docs/uah-lite.md`;
- documented AD-014.

## 0.1.0 — 2026-08-29

- created the initial declarative bootstrap;
- defined universal invariants, typed merge rules, schemas, and bootstrap evals;
- established dry-run before materialization and minimum sufficient topology.

