# Classification Output

Fill this template with the answer set and the recommendations
from the decision tree. Present to the human as a recommendation,
not a decision.

```yaml
classification:
  project_summary: |
    <one-paragraph description in the human's preferred language>
  answers:
    Q1: <a|b|c|d|e>          # complexity
    Q2: <a|b|c|d|e>          # primary deliverable type
    Q3: <a|b|c|d|e>          # source of truth
    Q4: <a|b|c>              # duration
    Q5: <a|b|c|d>            # evidence burden
    Q6: <a|b|c>              # reproducibility
    Q7: <a|b|c|d>            # material risk
    Q8: <a|b|c|d>            # knowledge scale
    Q9: <a|b|c>              # retrieval need
    Q10: <Yes|No>            # relational queries
    Q11: <a|b|c|d|e|f|list>  # ingestion pipeline (multi-select)
    Q12: <a|b|c|d>           # coordination need
    Q13: <a|b>               # parallelism
    Q14: <a|b|c>             # autonomy tolerance
    Q15: <a|b|c>             # state continuity / handoff
    Q16: <a|b|c>             # brownfield vs greenfield
    Q17: <a|b|c|d|e|list>    # test strategy (multi-select)
    Q18: <a|b|c|d|e>         # SDD workflow scope
    Q19: <a|b|c>             # ADR / decision log
    Q20: <a|b>               # change protocol
    Q21: <a|b|c>             # external actions
    Q22: <a|b|c>             # human-gate frequency
    Q23: <a|b|c>             # independent review / red-team
    Q24: <a|b|c>             # observability depth

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

  sdd_workflow: <None | charter | light | full | full+subagents>

  brownfield_protocol:
    applicable: <Yes|No>
    legacy_code_change_algorithm: <Yes|No>
    characterization_tests_required: <Yes|No>

  test_strategy: <TDD | characterization | approval | mutation | mixed>

  adr_log:
    enabled: <Yes|No>
    supersession_chain: <Yes|No>

  change_protocol:
    enabled: <Yes|No>
    workflow: <CR-NNNN>

  state_continuity:
    mode: <single-session | multi-session | multi-agent>
    handoff_artifacts: <Yes|No>
    compaction_required: <Yes|No>

  independent_review:
    level: <none | reviewer | reviewer+red-team>

  open_questions:
    - <anything UNKNOWN or genuinely unresolved>

  next_step: |
    Run bootstrap/BOOTSTRAP.md using this classification as input.
    Produce the Bootstrap Report. End with APPROVE, REVISE, or
    BLOCK.
```