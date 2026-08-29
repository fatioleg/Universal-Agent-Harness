# Task Plan — <Project>

A task plan decomposes work into small, independently
verifiable units. Each unit links to a requirement, an
acceptance criterion, expected tests, and an implementation
gate.

## Pre-implementation output

Before implementation begins, present:

```text
1. Problem understanding
2. Scope / non-goals
3. Requirements (REQ-IDs)
4. Key constraints
5. Proposed architecture
6. Acceptance criteria (AC-IDs)
7. Testing strategy (pyramid layer per task)
8. Implementation plan (the tasks below)
9. Main risks / uncertainties
```

Do not turn this into bureaucracy. Depth follows complexity
(see `core/principles/10-proportional-design.md`).

## Tasks

Priority order: risks → dependencies → interfaces → essential
behavior → secondary features.

### TASK-0001 — <name>

- **Related requirement**: REQ-0001
- **Acceptance criterion**: AC-0001-01
- **Expected tests**: TEST-0001-01
- **Pyramid layer**: unit
- **Approach**: tdd (red-green-refactor)
- **Implementation**: <one-paragraph plan>
- **Validation**: <how the agent confirms the task is done>
- **Dependencies**: <none | TASK-XXXX>
- **Status**: proposed / in-progress / done / blocked

### TASK-0002 — <name>

- **Related requirement**: REQ-0001
- **Acceptance criterion**: AC-0001-02
- **Expected tests**: TEST-0001-02
- **Pyramid layer**: unit
- **Approach**: tdd
- **Implementation**: ...
- **Validation**: ...
- **Dependencies**: TASK-0001
- **Status**: proposed

## Gate D — Done

A task is done when, as applicable:

- [ ] Requirement satisfied.
- [ ] Acceptance criterion verified (test green or manual
      check recorded).
- [ ] Test added at the right pyramid layer.
- [ ] No regressions (existing suite still green).
- [ ] Integration validated where applicable.
- [ ] Errors handled (or explicit "no error path needed" with
      reason).
- [ ] Documentation updated (spec / ADR / inline comment).
- [ ] No critical hypothesis hidden.

## Notes

- A task should be small enough that the agent can execute it
  without the whole project context.
- Use Context Pack and Subagent Report templates from
  `docs/sdd.md` when delegating.
- Update `state.json` (schema in `core/schemas/extension/`)
  after each task.