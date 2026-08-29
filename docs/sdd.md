# Spec-Driven Development (SDD)

This document describes the full SDD workflow supported by the
`full-sdd-project` archetype. It exists so that projects needing
multi-agent, multi-week, multi-spec work have a concrete
template. Projects that do not need this machinery should pick a
narrower archetype.

The five specs (SPEC-00 through SPEC-04) below are **canonical
shapes**, not exhaustive templates. Each project adapts them to
its domain while preserving the structural fields.

## SPEC-00 — Project Charter

Purpose: explain *why* the project exists before any work begins.

```
PROJECT
OBJECTIVE
BACKGROUND
DELIVERABLE
SCOPE
OUT OF SCOPE
CONSTRAINTS
ASSUMPTIONS
INPUTS
OUTPUTS
STAKEHOLDERS
SUCCESS CRITERIA
RISKS
```

`OUT OF SCOPE` is as important as `SCOPE`. Without it, scope
creep is inevitable.

## SPEC-01 — Requirements

Purpose: list what the deliverable must do. Each requirement is
individually traceable.

```
REQ-ID
Description
Source
Priority      ← MUST / SHOULD / COULD / OUT
Acceptance criteria
Dependencies
Status         ← proposed / approved / implemented / verified / retired
```

**MUST** requirements gate completion. **SHOULD** requirements
are recorded but do not gate. **COULD** requirements are
considered if budget allows. **OUT** requirements are explicitly
rejected so they do not reappear later.

## SPEC-02 — Architecture

Purpose: how the work decomposes into modules, agents,
interfaces, and gates.

Contents:

- Module breakdown (one entry per module: ID, objective, inputs,
  outputs, dependencies, responsible agent, tools, acceptance
  criteria, status)
- Interface contracts between modules
- Dependency graph
- Subagent role assignments (research, domain expert, data
  auditor, implementation, QA, red-team)
- Information flow (where state, evidence, decisions, handoffs
  live)
- Intermediate artifacts (what each module produces)
- Gate sequence

A module should be small enough that an agent can execute it
without receiving the full project context.

## SPEC-03 — Validation

Purpose: define what "correct" means *before* producing the
deliverable.

Applicable validation criteria (pick the relevant subset):

- factual correctness
- scientific correctness
- logical consistency
- numerical accuracy
- code quality (lint, type-check, tests, mutation)
- completeness
- traceability
- documentation consistency
- visual quality
- normative compliance
- security
- performance
- reproducibility

For each chosen criterion, name the **sensor** that enforces it
(see `evals/catalog.md` and `archetypes/<chosen>.md`).

## SPEC-04 — Deliverable

Purpose: exactly what is shipped.

```
FORMAT
STRUCTURE
REQUIRED CONTENT
OPTIONAL CONTENT
QUALITY STANDARD
STYLE
VERSIONING
ACCEPTANCE TEST
```

`ACCEPTANCE TEST` must be executable (by a sensor or by a human
with a checklist).

## Context Pack template

For each substantial task dispatched to a subagent, generate a
**Context Pack**:

```markdown
# CONTEXT PACK — TASK-ID

## Objective
<one sentence>

## Relevant background
<the minimum the subagent must know>

## Inputs
<files, data, prior results>

## Files
<paths the subagent may read; paths it may write>

## Current decisions
<decisions that constrain this task>

## Constraints
<hard limits: time, scope, permissions>

## Dependencies
<other tasks whose outputs this task consumes>

## Expected output
<exact deliverable shape>

## Acceptance criteria
<what "done" means for this task>
```

The Context Pack is the **contract of context**. The subagent
receives only this — not the whole project.

## Subagent Report template

Every subagent returns a **Subagent Report**:

```markdown
# SUBAGENT REPORT

## Task
TASK-ID

## Status
PASS | PASS WITH WARNINGS | BLOCKED | FAIL

## Work completed
<condensed>

## Key findings
<2-5 bullets>

## Issues discovered
<ISSUE-IDs or "none">

## Decisions required
<DEC-IDs or "none">

## Evidence
<pointer to evidence ledger entries>

## Files created or modified
<paths>

## Dependencies affected
<other tasks now unblocked or blocked>

## Recommended next action
<one sentence>
```

The orchestrator consumes **only the report**, not the full
subagent transcript. Full details are reached only on demand.

## Handoff template

At session end (or before compaction), produce a **Handoff**:

```markdown
# HANDOFF

## Project
## Current objective
## Current state
## Last completed milestone
## Decisions already made
## Important files
## Active specifications
## Open issues
## Risks
## Tasks in progress
## Next recommended task
## Exact restart instructions
```

A new session resumes by reading, in order:

1. Project State
2. Handoff
3. Relevant Spec
4. Relevant Context Pack

…and **not** the whole prior history.

## Issue tracking

Each material problem gets an `ISSUE-NNN`:

```
ISSUE-ID
DESCRIPTION
SEVERITY     ← CRITICAL / MAJOR / MODERATE / MINOR / INFORMATIONAL
SOURCE
IMPACT
OWNER
STATUS
RESOLUTION
```

Do not hide issues to make a phase look finished.

## Decision log

Each material decision gets a `DEC-NNN` (schema in
`core/schemas/extension/decisions.schema.json`):

```
DECISION-ID
DATE
QUESTION
OPTIONS
DECISION
RATIONALE
EVIDENCE
CONSEQUENCES
REVERSIBLE?
```

`REVERSIBLE?` flags whether the decision can be undone cheaply.
Irreversible decisions require a human gate.

## Memory shape

The orchestrator's session-start read is exactly:

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

Do not store chat transcripts as memory.

## Context budget rule

> **Persist → Summarize → Reference → Reload only when
> necessary.**

When the orchestrator's context grows, persist to `state/`,
`summarize` into a handoff, reference the artifacts by path,
and reload only what the next task needs.

## Compaction protocol

Before discarding context:

1. Update `state/`.
2. Update `decisions/`.
3. Update `issues/`.
4. Create a checkpoint.
5. Update the handoff.
6. Confirm modified files.
7. Register the exact next step.

Only then allow compaction.

## Gates

Default sequence (adapt per project):

```
GATE-01 Requirements
GATE-02 Architecture
GATE-03 Evidence
GATE-04 Implementation
GATE-05 QA
GATE-06 Final Acceptance
```

Each gate produces:

```
PASS
PASS WITH RESTRICTIONS
FAIL
```

Do not advance silently after a FAIL. Resolve or document the
exception explicitly.

## Model routing

Reserve expensive models for material decisions:

- **HIGH** — planning, conflicts, scientific synthesis, red-team.
- **MID** — extraction, classification, comparison, conventional
  implementation, first review.
- **LOW** — grep, parse, file renames, deterministic checks,
  small edits.

Any low- or mid-model output that drives a critical decision
must be supervised or validated by a higher-capability model.

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
- [ ] Final artifact rendered or tested.
- [ ] Memory updated.
- [ ] Final checkpoint created.
- [ ] Final handoff created.
- [ ] Deliverables clearly identified.

## Gate D — Done

A task is not done when the code runs. A task is done when, as
applicable:

- Requirement satisfied.
- Acceptance criteria verified (test green or manual check
  recorded with reason).
- Tests added at the right pyramid layer (see `docs/tdd.md`).
- No regressions introduced (regression suite green).
- Integration validated where applicable.
- Errors handled (or explicit "no error path needed" with
  reason).
- Documentation updated (spec / ADR / inline comment).
- No critical hypothesis remains hidden.
- State updated (schema in
  `core/schemas/extension/state.schema.json`).

## Requirement traceability

Maintain identifiers through the chain:

```text
REQ-NNNN
  └── AC-NNNN-NN      (one or more acceptance criteria)
        └── TEST-NNNN-NN  (one or more executable checks)
              └── implementation
```

Schemas:

- `core/schemas/extension/acceptance-criterion.schema.json`
  (AC records).
- `core/schemas/extension/test-case.schema.json` (TEST records).

The harness answers two questions at any moment:

> "What proves that REQ-0003 is implemented?"
> AC-0003-01 → TEST-0003-01 → green.

> "Why does component X exist?"
> REQ-0003 → AC-0003-01 → component X.

If a component has no upstream requirement, it is dead code. If
an acceptance criterion has no test, it is unverified (or
explicitly manual).

## Change protocol

When a requirement changes:

```text
Change request (CR-NNNN)
  ↓
Update affected REQ
  ↓
Update affected AC
  ↓
Update or add TEST
  ↓
Modify implementation
  ↓
Run regression suite
  ↓
Record decision (DEC-NNNN) + ADR if hard to reverse
```

Schema: `core/schemas/extension/change-request.schema.json`.

Do not modify code and then update the spec to fit. The spec is
the **intent**; the code is the **current behavior**. When
they diverge, the diff is itself a change request.

## Prohibitions

Following established engineering practice:

- Do not implement before understanding the problem.
- Do not add unspecified features.
- Do not label work "TDD" when tests were written after the
  implementation.
- Do not consider code without tests automatically correct.
- Do not change tests to make a defective implementation pass.
- Do not remove validations to silence failures.
- Do not mask errors.
- Do not ignore broken tests.
- Do not create excessively sophisticated architecture.
- Do not introduce dependencies without need.
- Do not create fictitious documentation.
- Do not claim success without running or verifying the
  validation mechanisms available.

## Change Protocol — Gate A–D

Use these task-level gates inside the SDD lifecycle:

- **Gate A — Specification Ready**: objective understood,
  scope defined, MUST requirements identified, acceptance
  criteria sufficient.
- **Gate B — Architecture Ready**: components defined,
  responsibilities clear, architectural risks assessed.
- **Gate C — Implementation Ready**: per task, requirement
  identified, expected behavior known, test strategy chosen.
- **Gate D — Done**: implemented, tested, criteria verified,
  documentation updated.

These gates do not require explicit human approval at each
crossing. When the agent has autonomy, it verifies internally
and records briefly. Stop and ask only on material ambiguity
that cannot be resolved safely from available information.

## Cross-references

- `archetypes/full-sdd-project.md` — the archetype that bundles
  this workflow.
- `core/schemas/extension/state.schema.json` — project state.
- `core/schemas/extension/decisions.schema.json` — decisions.
- `core/schemas/extension/permission-profile.schema.json` —
  per-role permissions.
- `docs/agent-topology.md` — Levels A–E.
- `docs/autonomy-levels.md` — L0–L5.
- `docs/tdd.md` — TDD red-green-refactor and the test pyramid.
- `docs/brownfield.md` — working with existing codebases.
- `docs/adr-template.md` — ADR format for significant decisions.