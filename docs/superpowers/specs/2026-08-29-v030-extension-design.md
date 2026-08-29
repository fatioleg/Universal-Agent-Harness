# Universal Agent Harness — v0.3.0 Extension Design

**Status:** design approved, pending spec review.
**Date:** 2026-08-29
**Target version:** 0.3.0 (from 0.2.0)
**Repository:** `AAAAMyArchitetures/Universal-Agent-Harness/`

## Context

The repository at v0.2.0 already implements:

- canonical `HARNESS.md` contract shared by Codex and Claude Code
  through thin entrypoints (`AGENTS.md`, `CLAUDE.md`);
- 12 locked invariants in `core/invariants.yaml`;
- typed merge policy in `core/merge-policy.yaml`;
- project-input and resolved-harness JSON Schemas;
- bootstrap protocol (`bootstrap/BOOTSTRAP.md`) with dry-run gate;
- project materialization templates;
- platform adapters (`platforms/CODEX.md`, `platforms/CLAUDE-CODE.md`);
- architecture docs and decision log;
- 8 representative bootstrap eval cases;
- deterministic repository validation (`scripts/validate_repo.py`) and
  GitHub Actions CI.

What v0.2.0 does NOT yet have, and what the cross-document analysis
(transfer doc §1–§39) identified as missing or under-developed:

1. **Archetype catalog.** No reference patterns for recurring scientific
   or computational workflows. Agents have no curated vocabulary to draw
   on when classifying a project.
2. **Extended runtime schemas.** Only project-input and resolved-harness
   schemas exist. State, evidence ledger, decisions, tool contracts,
   permission profiles, failure registry, eval results, and
   observability runs have no formal shape.
3. **Principles in human-readable form.** Invariants are in YAML only.
   Reasoning behind them is not documented for agents to consult.
4. **Override protocol.** No documented way to deviate from H0
   invariants deliberately.
5. **Operational concept docs.** Agent topology levels and autonomy
   levels live in `HARNESS.md` but lack dedicated references that
   projects can extend.
6. **Glossary and references.** No shared vocabulary list, no bibliography
   of the sources informing the design.
7. **Eval catalog beyond bootstrap cases.** The 10 universal eval
   categories from transfer §24 are not catalogued for projects to
   select from.
8. **Worked example.** No concrete instance showing how a project
   resolves through the harness.

## Goal of v0.3.0

Extend v0.2.0 with the above without breaking compatibility and without
introducing executable resolers, vector stores, graphs, or any premature
infrastructure. v0.3.0 stays declarative and markdown-only.

Additionally, v0.3.0 adds three deliverables driven by the cross-source
audit (OpenAI, Hashimoto, Anthropic managed-agents, Anthropic
long-running apps, Böckeler/Fowler):

- an interactive classification **skill** that walks a human through
  structured questions to pick tools, capabilities, and an archetype
  reference for a new project;
- **tool contracts** in YAML format describing agent-invokable tools
  (no executable code; deferred per AD-003);
- an expanded **references** list citing all five primary sources.

## Non-goals

- No executable bootstrap resolver (deferred per AD-003).
- No new mandatory dependencies in `requirements-dev.txt`.
- No executable tool scripts. Tool **contracts** are added; tool
  **implementations** are deferred to v0.4.0 per AD-003. AD-009 will
  record this distinction.
- No mutation of the 12 locked invariants in `core/invariants.yaml`.
  Their IDs and statements remain stable.
- No promotion of any `archetypes/` entry to an H1 package. Archetypes
  ship as **reference patterns only**, not as merge-policy inputs.
- No breaking changes to existing schemas. New schemas are additive.
- No platform-specific adapter changes (Codex/Claude Code files
  unchanged).

## Design

### 1. archetypes/ — reference patterns, not H1 packages

New directory: `archetypes/` with `archetypes/README.md` and 9 archetype
stubs.

**`archetypes/README.md`** (~60 lines) declares:

- archetypes are **reference patterns**, observed from prior projects
  and from cross-document analysis;
- they are NOT H1 packages and cannot be referenced by
  `source_versions.H1` in `harness.lock.yaml`;
- they cannot be merged via `core/merge-policy.yaml`;
- an agent reading this repo may use them as classification and
  configuration guidance;
- promotion to an H1 package requires:
  1. at least two completed real projects demonstrating the workflow;
  2. a promoted YAML overlay following the `merge-policy.yaml` field
     policies;
  3. a recorded AD (Architecture Decision) in `docs/DECISIONS.md`;
  4. an added eval case in `evals/bootstrap-cases.yaml`.

**9 archetype stubs**, each in its own file:

- `scientific-research.md`
- `computational-science.md`
- `computational-chemistry.md`
- `literature-review.md`
- `knowledge-base.md`
- `data-analysis.md`
- `software-development.md`
- `document-production.md`
- `grant-project-proposal.md`

Each stub uses the same template:

```
# Archetype: <name>

## When to use
<signals>

## Inherits from
- core/ (universal invariants, schemas, evals)
- bootstrap/ workflow

## Differs from base by
- Knowledge strategy
- Default sensors
- Permission defaults
- Required scaffolds

## Required sensors (from core/evals)
<list>

## Typical tool profile
<list by capability>

## Evidence & provenance requirements
<archetype-specific rules>

## Agent topology default
Level A/B/C/D/E with justification

## Autonomy defaults
Per-task L0-L5 recommendations

## Open questions / not-yet-defined
<honest list of unknowns>

## Example instantiation
<2-3 sentence sketch, no full worked example>
```

### 2. core/schemas/extension/ — 8 new schemas

New directory: `core/schemas/extension/` to keep the two base schemas
(`project-input.schema.json`, `resolved-harness.schema.json`) at the
canonical `schemas/` path that the validator already references.

Schemas added (all draft 2020-12, additive only):

1. **`state.schema.json`** — current project phase, active agents,
   pending gates, blockers, next action.
2. **`evidence-ledger.schema.json`** — claim_id, source_id,
   source_location, evidence_type, confidence, status, used_in,
   validation_status. Maps to transfer §8.
3. **`decisions.schema.json`** — decision_id, context, options,
   decision, rationale, decided_by, supersedes. Maps to transfer §15.
4. **`tool-contract.schema.json`** — tool_id, capability,
   input/output schemas, permissions_required, side_effects,
   failure_modes, cost, latency, validation_method, eval_status.
   Maps to transfer §19.
5. **`permission-profile.schema.json`** — profile_id, agent_role,
   capabilities map (read/write/modify/delete/execute/network/install/
   publish/send/spend/merge), duration, granted_by. Maps to
   transfer §20.
6. **`failure-registry.schema.json`** — failure_id, pattern,
   root_cause, harness_patch, regression_sensor, status, linked_eval.
   Maps to transfer on Hashimoto / §25.
7. **`eval-result.schema.json`** — eval_id, category, input, expected,
   actual, passed, metrics (tokens, cost, latency, tool_failures,
   human_interventions), harness_version, model_id, timestamp.
   Maps to transfer §24.
8. **`observability-run.schema.json`** — run_id, task_id, agent_id,
   model_id, harness_version, started_at, ended_at, tools_used,
   inputs_hash, outputs_hash, tokens, cost, retries, sensor_results,
   failures, final_status. Maps to transfer §22.

All schemas:

- live under `core/schemas/extension/`;
- are added to `scripts/validate_repo.py` as files that must exist
  and parse as valid JSON Schema (using `Draft202012Validator.check_schema`);
- do NOT extend `project-input.schema.json` or
  `resolved-harness.schema.json`;
- are blueprints; example data instances are NOT shipped in v0.3.0.

### 3. core/principles/ — human-readable rationale

New directory: `core/principles/` with 9 markdown files. Each maps to
one of the 12 invariants in `core/invariants.yaml` where overlap
exists; the 3 extras (INV-010 no_silent_weakening, INV-011 minimality,
INV-012 bounded_autonomy) are subsumed into the existing principles.

Mapping (1 principle file may reference multiple invariants):

| File | Source invariants |
|---|---|
| `01-preserve-sources.md` | INV-001 |
| `02-maintain-provenance.md` | INV-002 |
| `03-least-privilege.md` | INV-005, INV-006 |
| `04-verify-critical-outputs.md` | INV-008 |
| `05-expose-failures.md` | INV-009 |
| `06-maintain-state.md` | INV-003, INV-004 |
| `07-progressive-disclosure.md` | INV-007 |
| `08-prefer-deterministic.md` | INV-008 |
| `09-reproducibility.md` | INV-003, INV-012 |

Each file ~50 lines, structure:

```
# Principle NN: <name>

## Statement
<one-sentence>

## Why this is a principle
<reasoning, traced to source>

## What it requires
<concrete behaviors / files / schemas>

## When this can be overridden
<conditions>

## How to verify
<which sensor / eval / check>

## Failure mode if ignored
<concrete bad outcome>
```

### 4. core/policies/override-protocol.md

New file. ~70 lines. Documents:

- which of the 9 principles can be deviated from and which cannot;
- required fields in a deviation record (which principle, why,
  compensating control, human approval);
- the 3 principles that cannot be overridden (preserve-sources,
  maintain-provenance, expose-failures) and why;
- how deviations appear in `decisions.json` (when projects use the
  extension schema).

### 5. docs/agent-topology.md

Extract and expand the topology table currently in `HARNESS.md` §Agent
topology. ~80 lines. Includes:

- Levels A–E definitions;
- decision criteria for escalation;
- example triggers per level;
- when NOT to escalate (premature multi-agent cost).

### 6. docs/autonomy-levels.md

New file. ~80 lines. L0–L5 definitions, capability-specific autonomy,
default autonomy profiles per archetype (cross-link to
`archetypes/` entries).

### 7. docs/glossary.md

New file. ~80 lines. Definitions of harness, archetype, sensor,
computational sensor, inferential sensor, evidence ledger, claim,
provenance, H0–H3 layers, lock file, Bootstrap Report. The full
bibliography of source documents informing the design is recorded
in section 16 (`docs/references.md`).

### 8. evals/catalog.md

New file at `evals/catalog.md` (sibling to the existing
`evals/bootstrap-cases.yaml`). ~80 lines. The 10 universal eval
categories from transfer §24:

- EVAL-001 literature retrieval;
- EVAL-002 document ingestion;
- EVAL-003 structured extraction;
- EVAL-004 numerical audit;
- EVAL-005 citation verification;
- EVAL-006 artifact generation;
- EVAL-007 handoff/restart;
- EVAL-008 agent coordination;
- EVAL-009 conflicting-source resolution;
- EVAL-010 failure recovery.

Each entry: purpose, input fixture type, expected behavior, metrics.
Archetypes reference which subset applies to them.

This file coexists with the existing `evals/bootstrap-cases.yaml`
which contains eval **cases** (specific test inputs and expected
outcomes for bootstrap-level behavior). The catalog is the **menu**;
the cases file is the **specific test set**.

### 9. examples/

New directory with placeholder structure:

- `examples/README.md` — what examples are for, when to add one;
- `examples/literature-review/` — a single worked example deferred
  to v0.3.1 per user choice (folder structure only, no files yet).

Per the user's prior answer, the example is deferred. The folder
exists to commit to the intent.

### 10. scripts/validate_repo.py updates

Extend the validator without changing its public interface:

- add the new required files (9 archetypes, 8 schemas in extension,
  9 principles, override-protocol, agent-topology, autonomy-levels,
  references, glossary, eval-catalog at `evals/catalog.md`,
  `skills/classify-project/SKILL.md`, `contracts/tools/README.md`
  and 7 tool contracts) to `REQUIRED_FILES`;
- add JSON Schema parse check for the 8 new schemas using
  `Draft202012Validator.check_schema`;
- add YAML parse check for the 7 tool contracts (must conform to
  `tool-contract.schema.json`);
- add a check that `archetypes/README.md` contains the
  "reference patterns, not H1 packages" disclaimer;
- add a check that `skills/classify-project/SKILL.md` has valid
  YAML frontmatter with `name` and `description` fields;
- keep all existing checks unchanged.

### 11. CHANGELOG.md

Append a 0.3.0 entry summarising the additions.

### 12. docs/DECISIONS.md

Add two ADs:

- **AD-008** records the v0.3.0 scope and rationale (initial draft).
- **AD-009** records the audit outcome: tool **contracts** ship in
  v0.3.0; tool **implementations** remain deferred per AD-003.
  Tool implementations require pilots demonstrating stable
  classifiers per the merged-policy `minimality` rule.

## Directory tree after v0.3.0

```text
Universal-Agent-Harness/
├── README.md                       # unchanged
├── AGENTS.md                       # unchanged (Codex entrypoint)
├── CLAUDE.md                       # unchanged (Claude Code entrypoint)
├── HARNESS.md                      # unchanged (canonical contract)
├── VERSION                         # bump to 0.3.0
├── CHANGELOG.md                    # + 0.3.0 entry
├── LICENSE                         # unchanged (if present)
├── requirements-dev.txt            # unchanged
│
├── core/
│   ├── universal.yaml              # unchanged
│   ├── invariants.yaml             # unchanged (12 invariants preserved)
│   ├── merge-policy.yaml           # unchanged
│   ├── principles/                 # NEW: 9 markdown files
│   ├── policies/
│   │   └── override-protocol.md    # NEW
│   ├── schemas/extension/          # NEW: 8 schemas
│   └── evals/                       # empty placeholder; eval catalog lives at evals/catalog.md
│
├── archetypes/                     # NEW: 9 stubs + README
│   ├── README.md
│   ├── scientific-research.md
│   ├── computational-science.md
│   ├── computational-chemistry.md
│   ├── literature-review.md
│   ├── knowledge-base.md
│   ├── data-analysis.md
│   ├── software-development.md
│   ├── document-production.md
│   └── grant-project-proposal.md
│
├── skills/
│   └── classify-project/           # NEW: interactive classification skill
│       ├── SKILL.md
│       ├── questions.md
│       ├── decision-tree.md
│       └── output-template.md
│
├── contracts/
│   └── tools/                      # NEW: tool contracts (no impl per AD-003)
│       ├── README.md
│       ├── check-invariants.yaml
│       ├── diff-harness.yaml
│       ├── verify-artifact.yaml
│       ├── list-events.yaml
│       ├── sensor-trend.yaml
│       ├── lock-drift-check.yaml
│       └── scaffold-project.yaml
│
├── schemas/                        # unchanged: base schemas
│   ├── project-input.schema.json
│   └── resolved-harness.schema.json
│
├── bootstrap/                      # unchanged
│   ├── BOOTSTRAP.md
│   ├── NEW-PROJECT.md
│   └── project-input.example.yaml
│
├── templates/project/              # unchanged
│   ├── AGENTS.md.template
│   ├── CLAUDE.md.template
│   ├── project.yaml.template
│   └── harness.lock.yaml.template
│
├── platforms/                      # unchanged
│   ├── CODEX.md
│   └── CLAUDE-CODE.md
│
├── docs/                           # extended
│   ├── ARCHITECTURE.md             # unchanged
│   ├── DECISIONS.md                # + AD-008
│   ├── agent-topology.md           # NEW
│   ├── autonomy-levels.md          # NEW
│   ├── references.md               # NEW
│   └── glossary.md                 # NEW
│
├── evals/
│   ├── bootstrap-cases.yaml        # unchanged
│   └── catalog.md                  # NEW: universal eval categories
│
├── examples/                       # NEW (deferred content)
│   └── README.md
│
├── scripts/
│   └── validate_repo.py            # extended
│
└── .github/workflows/
    └── validate.yml                # unchanged
```

### 13. skills/classify-project/ — interactive classification skill

New directory: `skills/classify-project/` containing a single skill
that walks a human through structured questions to recommend:

- which `archetypes/` entry best matches the project;
- which capabilities from `core/universal.yaml` to enable;
- which tool contracts to bind (from `contracts/tools/`);
- which sensors from `evals/catalog.md` to apply;
- which extension schemas to instantiate (state, evidence-ledger,
  decisions, etc.).

**File layout:**

```text
skills/classify-project/
├── SKILL.md              # frontmatter + instructions (Claude Code format)
├── questions.md          # 15 questions with branch logic
├── decision-tree.md      # decision tree mapping answers → archetype
└── output-template.md    # format for the human-facing summary
```

**`SKILL.md`** uses the Claude Code skill frontmatter:

```yaml
---
name: classify-project
description: Use when starting a new project with this harness — walks the human through 15 structured questions to recommend an archetype, capabilities, tool contracts, and sensors for the project before any Bootstrap Report is produced.
---
```

The skill body instructs the agent to:

1. read `skills/classify-project/questions.md` and present each
   question one at a time;
2. follow branch logic in `questions.md` based on prior answers;
3. once complete, consult `decision-tree.md` to map the answer set to
   a recommended archetype and capability profile;
4. fill in `output-template.md` and present to the human;
5. NOT modify the target project. Classification is a precursor to
   the Bootstrap Report.

**`questions.md`** is structured as 15 questions across categories:

- Q1–Q3: primary deliverable, source of truth, lifecycle duration
  (drives archetype selection);
- Q4–Q6: evidence burden, reproducibility requirement, risk level
  (drives sensor selection);
- Q7–Q9: knowledge scale, retrieval need, graph need (drives
  knowledge plane capabilities);
- Q10–Q12: coordination need, parallelism, autonomy tolerance
  (drives topology selection);
- Q13–Q15: external actions, human-gate frequency, observability
  need (drives permission profile and assurance floor).

Each question has 3–5 multiple-choice options. Branch logic skips
irrelevant later questions.

**`decision-tree.md`** maps answer patterns to recommendations:

```
Q1 = literature  + Q3 = long-running + Q4 = scientific
  → archetype: literature-review
  → capabilities: scientific-evidence, lexical-retrieval, semantic-retrieval, independent-review
  → sensors: EVAL-001, EVAL-005, EVAL-009
  → schemas: state, evidence-ledger, decisions
  → topology: A or B
```

**`output-template.md`** is the human-facing summary format
containing: project summary, recommended archetype, recommended
capabilities, recommended tool contracts, recommended sensors, schemas
to instantiate, topology default, autonomy defaults, open questions,
next step (run the Bootstrap Report).

**Codex compatibility:** Codex discovers skills via
`.codex/agent-configuration/skills/<name>/SKILL.md` or reads the
file when the path appears in its discovered instruction chain. The
`SKILL.md` frontmatter uses standard YAML; Codex treats the body as
instructions. No platform-specific adapter needed in v0.3.0.

### 14. contracts/tools/ — tool contracts in YAML

New directory: `contracts/tools/` containing tool contract
descriptions, not implementations. Each contract is a single YAML
file with the same shape as `tool-contract.schema.json` (planned
in v0.3.0).

This delivers the "what tools exist" knowledge to the agent without
violating AD-003 (which defers implementations, not specifications).

**Initial contracts (7)**, each with: capability, input/output
schema reference, permissions_required, side_effects, failure_modes,
eval_status: `untested`.

1. `check-invariants.yaml` — verify a project's `harness.lock.yaml`
   honors all locked invariants. Source: Hashimoto.
2. `diff-harness.yaml` — show changes between current and target
   upstream H0 version. Source: repo's migration rule.
3. `verify-artifact.yaml` — generic artifact verifier with
   configurable sensor profile. Source: Hashimoto, Böckeler.
4. `list-events.yaml` — read event log / state for debugging.
   Source: Anthropic managed-agents.
5. `sensor-trend.yaml` — aggregate sensor pass/fail trends across
   runs. Source: Böckeler (sensors-cli pattern).
6. `lock-drift-check.yaml` — verify project's pinned upstream commit
   matches actual upstream. Source: repo INV-010.
7. `scaffold-project.yaml` — generate project-specific harness from
   input. Source: OpenAI templates.

Each contract also references the `tools/` MCP or `skills/` it would
call once implementations exist (forward references, not executed).

### 15. docs/references.md — full bibliography

The v0.3.0 plan includes `docs/references.md`. Updated list now
includes the five primary sources audited for this design:

- OpenAI — Harness engineering: leveraging Codex in an
  agent-first world. https://openai.com/index/harness-engineering/
- Mitchell Hashimoto — My AI adoption journey.
  https://mitchellh.com/writing/my-ai-adoption-journey
- Anthropic — Managed agents.
  https://www.anthropic.com/engineering/managed-agents
- Anthropic — Harness design for long-running apps.
  https://www.anthropic.com/engineering/harness-design-long-running-apps
- Birgitta Böckeler — Sensors for coding agents.
  https://martinfowler.com/articles/sensors-for-coding-agents.html
- Related tooling: Birgitta's `sensors-cli`
  (https://github.com/birgitta410/sensors-cli), Vlad Khononov's
  Modularity Skills, Factory's ESLint plugin, Pi custom harness
  extension.
- Codex AGENTS.md documentation, Claude Code memory and hooks
  documentation (already in v0.2.0 references).

Each contract YAML file ships alongside `contracts/tools/README.md`
explaining the distinction between contracts and implementations, the
promotion path, and what an agent can and cannot infer from a
contract alone.

## Compatibility and migration

- No schema in `schemas/` is modified. v0.2.0 project-input and
  resolved-harness stay byte-identical.
- `core/invariants.yaml` is unchanged. All 12 invariants remain locked.
- `core/universal.yaml` is unchanged.
- `core/merge-policy.yaml` is unchanged. New archetypes are not
  added as merge inputs.
- Existing `harness.lock.yaml.template` is unchanged. v0.3.0 does not
  introduce a new lock field.
- The validator's output gains more `PASS:` lines; existing
  `PASS:` lines remain.

A project at v0.2.0 with a lock referencing
`universal-agent-harness@0.2.0` continues to validate against v0.3.0.
To adopt v0.3.0 additions, a project must re-pin to
`universal-agent-harness@0.3.0`, regenerate the lock, and add an
explicit eval run (per `core/merge-policy.yaml` `versioning.migration`
rule).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Archetypes are mistaken for H1 packages | `archetypes/README.md` disclaimer + validator check for the disclaimer string |
| Schema explosion (8 new schemas) | All under `core/schemas/extension/`; base `schemas/` path preserved |
| Validator becomes slow | New checks are file existence + small JSON parse; no extra deps |
| Doc proliferation | 4 new docs only; each <100 lines |
| Bloat from 9 archetype stubs | Each stub <80 lines; total ~700 lines markdown |
| Skill not discovered by one platform | Use standard YAML frontmatter; Codex and Claude Code both read; validator checks frontmatter shape |
| Tool contracts drift from schema | Validator parses contracts against `tool-contract.schema.json` |
| User confusion between contracts vs implementations | `contracts/tools/README.md` explains the distinction; AD-003 referenced |

## Validation plan

1. Run `python scripts/validate_repo.py` after each file batch.
2. CI on GitHub Actions must remain green.
3. Confirm all 9 archetype files exist and contain the section
   headers from the template.
4. Confirm all 8 extension schemas parse as JSON Schema draft 2020-12.
5. Confirm `archetypes/README.md` contains the "reference patterns,
   not H1 packages" disclaimer.

## Implementation order

1. Bump `VERSION` to `0.3.0`; add `CHANGELOG.md` entry.
2. Add `docs/DECISIONS.md` AD-008.
3. Add `core/principles/` (9 files).
4. Add `core/policies/override-protocol.md`.
5. Add `core/schemas/extension/` (8 schemas).
6. Add `evals/catalog.md`.
7. Add `archetypes/` (README + 9 stubs).
8. Add `skills/classify-project/` (SKILL.md + 3 supporting files).
9. Add `contracts/tools/` (README + 7 tool contracts).
10. Add `docs/agent-topology.md`, `docs/autonomy-levels.md`,
    `docs/references.md` (with all 5 sources), `docs/glossary.md`.
11. Add `examples/README.md`.
12. Extend `scripts/validate_repo.py`.
13. Run validator locally; ensure CI-equivalent green.