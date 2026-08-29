# Archetype: full-sdd-project

## When to use

- The project is complex enough that a written specification must
  precede substantial work.
- The project requires multiagent orchestration with named
  specialized roles.
- The project needs structured handoffs between sessions or
  between agents.
- The user accepts the overhead of running the full Spec-Driven
  Development lifecycle (Project Charter → Requirements →
  Architecture → Validation → Deliverable).
- Persistent memory, decision logs, issue tracking, gates, and
  completion criteria are expected.

This is the **heaviest** archetype in v0.3.x. Reach for it when
smaller archetypes (scientific-research, literature-review,
software-development) are insufficient because the project is
multi-domain, multi-week, or multi-agent by design.

## Inherits from

- `core/` (universal invariants, schemas, evals)
- `bootstrap/` workflow
- All nine base archetypes as *potential* sub-workflows inside
  a single project

## Differs from base by

- **Knowledge strategy**: hybrid by default; full pipeline (caveman
  + MarkItDown + Graphify + Obsidian) if the project ingests
  non-trivial sources.
- **Default sensors**: EVAL-006 (artifact generation), EVAL-008
  (coordination), plus per-subagent sensors.
- **Permission defaults**: read/write inside project; subagent
  roles get scoped profiles per `permission-profile.schema.json`.
- **Required scaffolds**: `specs/`, `tasks/`, `contexts/`,
  `memory/`, `checkpoints/`, `qa/`, `decisions/`, `issues/`,
  `artifacts/`, `archive/`, `handoffs/`.

## Spec-Driven Development (SDD) lifecycle

| Spec | Purpose | Required content |
|---|---|---|
| SPEC-00 Project Charter | Why we are doing this | PROJECT, OBJECTIVE, BACKGROUND, DELIVERABLE, SCOPE, OUT OF SCOPE, CONSTRAINTS, ASSUMPTIONS, INPUTS, OUTPUTS, STAKEHOLDERS, SUCCESS CRITERIA, RISKS |
| SPEC-01 Requirements | What the deliverable must do | REQ-ID, Description, Source, Priority (MUST/SHOULD/COULD/OUT), Acceptance criteria, Dependencies, Status |
| SPEC-02 Architecture | How the work decomposes | modules, interfaces, dependencies, responsible agents, information flow, intermediate artifacts, gates |
| SPEC-03 Validation | What "correct" means | applicable criteria (factual, scientific, logical, numerical, code quality, tests, completeness, traceability, documentation, visual, normative, security, performance, reproducibility) |
| SPEC-04 Deliverable | What we ship | FORMAT, STRUCTURE, REQUIRED CONTENT, OPTIONAL CONTENT, QUALITY STANDARD, STYLE, VERSIONING, ACCEPTANCE TEST |

`docs/sdd.md` in this repo explains each spec with template
content.

## Named subagent roles

The full-sdd-project archetype uses the following role taxonomy.
**Activate only the roles the project actually needs.** A project
does not spawn all six by default.

- **Research Agent** — literature, sources, external docs, state
  of the art.
- **Domain Expert** — specialized conceptual analysis,
  methodology, theory.
- **Data / Numerical Auditor** — calculations, tables, units,
  statistics, independent reproduction.
- **Implementation Agent** — code, documents, scripts,
  configurations, product construction.
- **QA Agent** — tests, inspection, consistency, validation
  against specs.
- **Red-Team Reviewer** — independent reviewer that tries to
  find errors, fragile assumptions, inconsistencies, regressions,
  unaddressed requirements.

Each role gets a `permission-profile` (schema in
`core/schemas/extension/permission-profile.schema.json`).

## Context Packs and Subagent Reports

Each task delivered to a subagent is preceded by a **Context
Pack** (template in `docs/sdd.md`). Each subagent returns a
**Subagent Report**:

```
# SUBAGENT REPORT

## Task
TASK-ID

## Status
PASS | PASS WITH WARNINGS | BLOCKED | FAIL

## Work completed
## Key findings
## Issues discovered
## Decisions required
## Evidence
## Files created or modified
## Dependencies affected
## Recommended next action
```

The orchestrator consumes the **condensed report only**, never
the full subagent context.

## Required sensors (from evals/catalog.md)

- EVAL-006 artifact generation
- EVAL-007 handoff/restart
- EVAL-008 agent coordination
- EVAL-009 conflicting-source resolution (when sources diverge)
- EVAL-010 failure recovery

## Typical tool profile

- All `contracts/tools/*.yaml` that bind to the activated
  subagent roles.
- File-based state (`state.json`) per
  `core/schemas/extension/state.schema.json`.
- Decision log per `decisions.schema.json`.
- Issue tracker per `issues/` (see `docs/sdd.md`).
- Optional: caveman + MarkItDown + Graphify + Obsidian if
  scientific/technical corpus ingestion is needed.

## Evidence & provenance requirements

- Every material claim has a `CLAIM-NNNN` in the evidence ledger.
- Every spec change is recorded in `decisions.json`.
- Every subagent result includes an evidence section.
- Every gate crossing is logged.

## Agent topology default

Level C or D. Orchestrator plus one or more specialists. The
orchestrator is responsible for project state and handoff
artifacts. Subagents are stateless within their context window.

## Autonomy defaults

- Mechanical task execution: L4 (run a sensor, format a doc).
- Update a context pack: L2.
- Update a spec: L1.
- Change a requirement: L0.
- Approve a gate crossing: L0.
- Submit a deliverable: L0.

## Memory shape

The full-sdd-project memory lives in `state/` and
`memory/`. The orchestrator reads at session start:

```
PROJECT
CURRENT STATE
LAST COMPLETED STEP
CURRENT SPEC
DECISIONS
OPEN ISSUES
RISKS
DEPENDENCIES
FILES
ARTIFACTS
ACTIVE TASKS
NEXT ACTION
```

Each session begins by reading these (progressive disclosure).

## Context budget

Rule: **Persist → Summarize → Reference → Reload only when
necessary**. When the orchestrator's context grows, the project
state, decision log, and handoff artifact are persisted, and the
session continues from the persisted state.

## Compaction protocol

Before allowing context to be discarded:

1. Update `state/`.
2. Update `decisions/`.
3. Update `issues/`.
4. Create a checkpoint.
5. Update the handoff artifact.
6. Confirm modified files.
7. Register the exact next step.

Only then allow compaction.

## Gates

Default gate sequence (adapt per project):

```
GATE-01 Requirements
GATE-02 Architecture
GATE-03 Evidence
GATE-04 Implementation
GATE-05 QA
GATE-06 Final Acceptance
```

Each gate produces `PASS`, `PASS WITH RESTRICTIONS`, or `FAIL`.
Do not advance past a `FAIL` silently; resolve or record an
explicit exception.

## Issue tracking

Each material problem gets an `ISSUE-NNN` with severity
(`CRITICAL`/`MAJOR`/`MODERATE`/`MINOR`/`INFORMATIONAL`), source,
impact, owner, status, and resolution.

## Completion criteria

Before declaring the project complete:

- [ ] Objective satisfied.
- [ ] MUST requirements satisfied.
- [ ] Specs updated.
- [ ] Sources preserved.
- [ ] Outputs versioned.
- [ ] Critical issues resolved.
- [ ] Decisions logged.
- [ ] Validation executed.
- [ ] QA executed.
- [ ] Independent review performed.
- [ ] Final artifact rendered/tested.
- [ ] Memory updated.
- [ ] Final checkpoint created.
- [ ] Final handoff created.
- [ ] Deliverables clearly identified.

## Open questions / not-yet-defined

- How to balance explicit subagent role counts against the
  principle "simplest sufficient agent topology".
- Whether to make this archetype a default for any project
  classified as `risk: high` or `duration: long-running`.

## Example instantiation

A 6-month cross-domain research project combining plant biology,
computational chemistry, and a regulatory submission. SDD
workflow with one orchestrator, three domain specialists, and
one independent Red-Team reviewer. Pipeline ingestion via
caveman + MarkItDown + Graphify + Obsidian. Gates at every
phase boundary.

## Related archetypes

- `scientific-research` — narrower, evidence-ledger heavy.
- `literature-review` — narrower, retrieval + citation heavy.
- `software-development` — narrower, tests + CI heavy.

Pick `full-sdd-project` when the project genuinely needs the
whole machinery. Pick a narrower archetype when it does not.

## Cross-references

- `docs/sdd.md` — full Spec-Driven Development workflow, REQ→AC
  →Test→Impl traceability, Gate A–D.
- `docs/tdd.md` — TDD red-green-refactor and the test pyramid.
- `docs/brownfield.md` — working with existing codebases.
- `docs/adr-template.md` — ADR format for significant decisions.
- `templates/project/task-plan.template.md` — per-task plan.
- `templates/project/acceptance-criteria.template.md` — AC
  coverage matrix.
- `templates/project/test-cases.template.md` — test pyramid mix.
- `core/schemas/extension/acceptance-criterion.schema.json`.
- `core/schemas/extension/test-case.schema.json`.
- `core/schemas/extension/change-request.schema.json`.