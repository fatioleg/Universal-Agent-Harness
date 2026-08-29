# Acceptance Criteria — <Project>

Each requirement (`REQ-NNNN`) has one or more acceptance
criteria (`AC-NNNN-NN`). Each criterion has a verification
strategy and, when executable, a linked test
(`TEST-NNNN-NN`).

## Requirements index

| REQ-ID | Description | Priority | Status |
|---|---|---|---|
| REQ-0001 | <one-line summary> | MUST | proposed |
| REQ-0002 | <one-line summary> | SHOULD | proposed |

## Acceptance criteria

### REQ-0001 — <description>

- **AC-0001-01** — <observable behavior>.
  - Verification: <executable-test | manual-checklist | human-judgment | sensor-id>
  - Test: TEST-NNNN-NN (or `n/a` if manual)
  - Priority: MUST
  - Status: proposed

- **AC-0001-02** — <error case>.
  - Verification: ...
  - Test: ...
  - Priority: MUST
  - Status: proposed

### REQ-0002 — <description>

- **AC-0002-01** — ...

## Coverage matrix

| REQ | ACs | Tests | Status |
|---|---|---|---|
| REQ-0001 | AC-0001-01, AC-0001-02 | TEST-0001-01, TEST-0001-02 | all green |
| REQ-0002 | AC-0002-01 | TEST-0002-01 | one red |

## Notes

- AC IDs use the pattern `AC-<requirement-number>-<NN>`.
- Test IDs use the pattern `TEST-<NNNN>-<NN>` matching the AC.
- A criterion without a test is a *manual* verification; do not
  silently leave it untested.
- Priority OUT explicitly rejects the requirement so it does
  not reappear later.