# Classification Output

Fill this template with the answer set and the recommendations
from the decision tree. Present to the human as a recommendation,
not a decision.

```yaml
classification:
  project_summary: |
    <one-paragraph description in the human's preferred language>
  answers:
    Q1: <a|b|c|d>
    Q2: <a|b|c|d|e>
    Q3: <a|b|c>
    Q4: <a|b|c|d>
    Q5: <a|b|c>
    Q6: <a|b|c|d>
    Q7: <a|b|c>
    Q8: <a|b|c>
    Q9: <Yes|No>
    Q10: <a|b|c|d>
    Q11: <a|b>
    Q12: <a|b|c>
    Q13: <a|b|c>
    Q14: <a|b|c>
    Q15: <a|b|c>

  recommended_archetype: <name from archetypes/>
  recommended_capabilities:
    - <capability-id from core/universal.yaml>
    - ...

  recommended_tool_contracts:
    - <tool-id from contracts/tools/>

  recommended_sensors:
    - EVAL-NNN from evals/catalog.md
    - ...

  schemas_to_instantiate:
    - state
    - evidence-ledger
    - ...

  topology_default:
    level: <A|B|C|D|E>
    label: <from agent-topology.md>
    justification: <one sentence>

  autonomy_defaults: <per docs/autonomy-levels.md>

  permissions_summary: <per core/universal.yaml and overrides>

  open_questions:
    - <anything UNKNOWN or genuinely unresolved>

  next_step: |
    Run bootstrap/BOOTSTRAP.md using this classification as input.
    Produce the Bootstrap Report. End with APPROVE, REVISE, or
    BLOCK.
```