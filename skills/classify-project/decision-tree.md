# Decision Tree

Map an answer set to a recommendation. The recommendation is a
starting point; the human adjusts it.

## Archetype

| Pattern | Trigger |
|---|---|
| scientific-research | Q1=a + Q4=c + Q3=b or c |
| computational-science | Q1=b or d + Q5=c |
| computational-chemistry | Q1=b + Q4=c + chemistry-specific tooling available |
| literature-review | Q1=a + Q2=a + Q4=c + Q3=c |
| knowledge-base | Q1=c + Q3=c + Q7=c |
| data-analysis | Q1=d + Q2=c |
| software-development | Q1=b + Q2=d |
| document-production | Q1=a + Q4=a or b |
| grant-project-proposal | Q1=a + Q13=c (or budget) + deadline |

If no pattern fits, the project uses H0 only with project-specific
overrides.

## Capabilities

- Q4=c or d → capability: scientific-evidence
- Q8=b → capability: semantic-retrieval
- Q8=c → capability: semantic-retrieval + lexical-retrieval
- Q9=Yes → capability: graph-retrieval (record the recurring query)
- Q6=c or d → capability: independent-review (required)
- Q10=b, c, or d → capability: independent-review
- Q11=Yes → capability: long-running-orchestration

## Tool contracts to bind

- Q5=b or c → tool-contract: `lock-drift-check`, `diff-harness`
- Q6=b or higher → tool-contract: `check-invariants`,
  `verify-artifact`
- Q3=b or c → tool-contract: `list-events`
- Q15=b or c → tool-contract: `sensor-trend`
- Q10=b or higher → tool-contract: `verify-artifact`

## Sensors to apply

- Q4=c → EVAL-001, EVAL-003, EVAL-005
- Q4=d → EVAL-004 (numerical audit), plus regulatory-specific
- Q9=Yes → EVAL-009
- Q3=c → EVAL-007 (handoff/restart)
- Q10 ≥ b → EVAL-008 (coordination)

## Schemas to instantiate

- Q4 ≥ b → evidence-ledger
- Q3 ≥ b → state, decisions
- Q10 ≥ c → permission-profile
- Q15 ≥ b → observability-run
- Q6 ≥ c → failure-registry

## Topology

- Q10=a → A
- Q10=b → B
- Q10=c → C
- Q10=d → D or E (E if Q6 ≥ c)

Record the level, label, and justification in
`harness.lock.yaml` under `topology`.

## Autonomy

- Q12=a → default L0–L1 everywhere
- Q12=b → defaults from `core/universal.yaml`
- Q12=c → defaults may be raised per capability with a recorded
  decision

## Permissions

- Q13=a → universal defaults (most deny)
- Q13=b → network: read; rest unchanged
- Q13=c → expanded capabilities per Q13, each recorded in a
  decision

## Open questions to surface

Any UNKNOWN answer must appear in the output template under
"Open questions". Do not guess.