# Decision Tree

Map an answer set to a recommendation. The recommendation is a
starting point; the human adjusts it.

## Archetype

The decision tree walks the following priority order:

1. **First**, check if `full-sdd-project` or `knowledge-digestion`
   applies (the heaviest two archetypes).
2. **Then**, fall back to one of the nine base archetypes.
3. **Otherwise**, use H0 only with project-specific overrides.

### Heaviest archetypes

| Pattern | Trigger |
|---|---|
| `full-sdd-project` | Q1 ≥ c (medium/large/complex) AND Q18 = d or e (full SDD) |
| `knowledge-digestion` | Q11 selects any ingestion stage AND Q1 ≥ b (small+) |

### Base archetypes

| Pattern | Trigger |
|---|---|
| `scientific-research` | Q2 = a AND Q5 = c AND Q4 = b or c |
| `computational-science` | Q2 = b or d AND Q6 = c |
| `computational-chemistry` | Q2 = b AND Q5 = c AND chemistry-specific tooling available |
| `literature-review` | Q2 = a AND Q3 = a AND Q5 = c AND Q4 = c |
| `knowledge-base` | Q2 = c AND Q4 = c AND Q8 = c or d |
| `data-analysis` | Q2 = d AND Q3 = c |
| `software-development` | Q2 = b AND Q3 = d |
| `document-production` | Q2 = a AND Q5 = a or b |
| `grant-project-proposal` | Q2 = a AND Q21 = c OR (Q2 = a AND deadline) |

If none matches, the project uses H0 only with project-specific
overrides.

## Capabilities (22-entry vocabulary)

Map each answer to one or more capabilities from
`core/universal.yaml`:

| Trigger | Capability |
|---|---|
| Q1 ≥ c | `long-running-orchestration` |
| Q1 = e | `subagent-orchestration` (if Q23 = c) |
| Q4 ≥ b | `state-continuity` |
| Q4 = c | `checkpoint-handoff` (if Q15 = b or c) |
| Q5 = c or d | `scientific-evidence` |
| Q5 = b or higher | `specification` (if Q18 = d or e) |
| Q6 = b or higher | `computational-execution` |
| Q8 ≥ b | `source-ingestion` |
| Q8 ≥ b AND Q11 = a | `normalization` |
| Q8 = c or d | `cataloging` |
| Q9 = a or c | `lexical-retrieval` |
| Q9 = b or c | `semantic-retrieval` |
| Q10 = Yes | `graph-retrieval` (record the recurring query type) |
| Q11 = b | `context-compression` |
| Q11 includes c or d | `knowledge-digestion-pipeline` |
| Q12 ≥ b OR Q15 ≥ b | `independent-review` |
| Q15 = c | `subagent-orchestration` |
| Q16 = b or c | `specification` (forced for brownfield re-construction) |
| Q18 = d or e | `sdd-workflow` |
| Q21 = c | `external-write`, `publication` |
| Q24 ≥ b | `discovery`, `artifact-production` |

## Tool contracts to bind

Tool contracts live in `contracts/tools/`. Bind per Q-answers:

| Trigger | Tool contract |
|---|---|
| Q1 ≥ d | `check-invariants` |
| Q5 ≥ c OR Q23 ≥ b | `verify-artifact` |
| Q6 = b or c | `lock-drift-check`, `diff-harness` |
| Q8 ≥ b AND Q11 = a | `markitdown-normalize` |
| Q11 = b | `caveman-compress` |
| Q11 = c | `graphify-build` |
| Q11 = d | `obsidian-interface` |
| Q11 = e | `notebooklm-explore` |
| Q15 = b or c | `list-events` |
| Q18 = d or e | `scaffold-project` |
| Q24 ≥ b | `sensor-trend` |

## Sensors (eval catalog)

Apply from `evals/catalog.md`:

| Trigger | Sensors |
|---|---|
| Q5 = c | EVAL-001, EVAL-003, EVAL-005 |
| Q5 = d | EVAL-004, plus regulatory-specific |
| Q8 ≥ b | EVAL-002 |
| Q10 = Yes | EVAL-009 |
| Q4 = c AND Q15 ≥ b | EVAL-007 |
| Q12 ≥ b | EVAL-008 |
| Q21 = b or c | EVAL-006 (artifact generation) |
| Any project | EVAL-010 (failure recovery) if Q23 ≥ b |

## Schemas to instantiate

Schemas live in `core/schemas/extension/`. Instantiate per:

| Trigger | Schemas |
|---|---|
| Q4 ≥ b | `state` |
| Q5 = b | `decisions` |
| Q5 ≥ b | `evidence-ledger` |
| Q7 ≥ c | `failure-registry` |
| Q12 ≥ b | `permission-profile` |
| Q15 ≥ b | `observability-run` |
| Q18 = d or e | `acceptance-criterion`, `test-case` |
| Q20 = b | `change-request` |
| Q21 ≥ c | `tool-contract` (for any agent-invokable tools) |
| Any project with running evals | `eval-result` (records per-eval outcomes) |

## Agent topology

`docs/agent-topology.md` levels A–E.

| Trigger | Topology |
|---|---|
| Q12 = a | A (single agent + tools) |
| Q12 = b | B (agent + independent reviewer) |
| Q12 = c | C (orchestrator + one specialist) |
| Q12 = d | D or E (E if Q23 = c OR Q7 ≥ c) |

Record the level, label, and justification in
`harness.lock.yaml` under `topology`.

## Autonomy

`docs/autonomy-levels.md` levels L0–L5.

| Trigger | Default autonomy |
|---|---|
| Q14 = a | L0–L1 everywhere |
| Q14 = b | defaults from `core/universal.yaml` |
| Q14 = c | defaults may be raised per capability with a recorded decision |

## Permissions

`core/universal.yaml` permissions + `permission-profile.schema.json`.

| Trigger | Permission adjustment |
|---|---|
| Q21 = a | universal defaults (most deny) |
| Q21 = b | network: read; rest unchanged |
| Q21 = c | expanded capabilities per Q21, each recorded in a decision |

## State continuity and handoff

| Trigger | State shape |
|---|---|
| Q15 = a | single-session state only |
| Q15 = b | state + checkpoint-handoff (state.current.md per session) |
| Q15 = c | state + checkpoint-handoff + observability-run + multi-agent sub-state per role |

## Brownfield protocol

When Q16 = b or c, the project must adopt:

- Characterization tests **before** any refactor (Q17 = b).
- Legacy Code Change Algorithm from `docs/brownfield.md`:
  identify change points → find seams → break dependencies →
  write characterization tests → change → refactor.
- Sprout / Wrap techniques when inserting new logic into
  untested existing code.
- Brownfield safety checklist before merging agent changes.

## SDD workflow

When Q18 = d or e, instantiate:

- The five specs from `docs/sdd.md` (Charter, Requirements,
  Architecture, Validation, Deliverable).
- The REQ→AC→Test→Impl traceability schemas.
- Context Packs and Subagent Reports templates.
- Handoffs at session boundaries.
- Gates A–D: Specification Ready, Architecture Ready,
  Implementation Ready, Done.

If Q18 = e (full SDD + named subagents), activate the role
vocabulary (Research, Domain Expert, Data Auditor,
Implementation, QA, Red-Team).

## ADR / decision log

When Q19 ≥ b, every material decision is recorded using
`docs/adr-template.md` and tracked in `docs/DECISIONS.md`. The
existing project decision log uses the schema in
`decisions.schema.json`; ADRs are recorded in addition, not as
a replacement.

## Change protocol

When Q20 = b, any change to a requirement, acceptance
criterion, or test is preceded by a `change-request` record
(CR-NNNN, schema in `change-request.schema.json`). The
pipeline is: CR → update REQ → update AC → update/add TEST →
modify implementation → regression suite → record decision.

## Independent review

| Trigger | Review shape |
|---|---|
| Q23 = a | producer self-critique (default) |
| Q23 = b | independent reviewer on material artifacts; reviewer receives spec + artifact + evidence + acceptance criteria, not the producer's reasoning chain |
| Q23 = c | independent reviewer plus Red-Team adversary at every gate |

## Open questions to surface

Any UNKNOWN answer must appear in the output template under
"Open questions". Do not guess.