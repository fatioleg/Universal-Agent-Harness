# Autonomy Levels

Autonomy is capability-specific and bounded. A project can be L4 on
"rename files" and L0 on "submit manuscript". The universal default
is low autonomy; the project may raise it per capability with a
human gate.

## Levels

| Level | Name | Meaning |
|---|---|---|
| L0 | Suggest only | The agent proposes an action; a human approves before any execution. |
| L1 | Execute with approval | The agent executes the action after a human signs off once. |
| L2 | Execute and validate | The agent executes and runs a sensor; the sensor decides. |
| L3 | Execute, validate, repair | The agent executes, the sensor decides, and the agent retries once on a known failure. |
| L4 | Execute, validate, repair, integrate | The agent executes, repairs, and integrates the result into the project state. |
| L5 | Autonomous bounded workflow | The agent runs a multi-step workflow within declared scope, validators, retries, and escalation. |

## Default per capability

The universal defaults from `core/universal.yaml` are conservative:

- Read: L4 (file scope, no external effect)
- Write new files: L2 (within declared scaffold)
- Modify existing files: L1 (per-file human ack)
- Delete: L0 (always human)
- Execute declared tools: L2
- Network: L0 default, L2 task-justified
- Install: L0
- Publish: L0
- Send: L0
- Spend: L0
- Merge: L0

## Per-archetype overrides

Archetypes may suggest higher defaults where the risk profile is
well-understood:

- `software-development` archetype: L3 for "run tests" (execute,
  validate, repair).
- `computational-chemistry` archetype: L2 for "validate SMILES" (a
  computational sensor is deterministic and reversible).
- `literature-review` archetype: L1 for "ingest citation" (every
  citation enters the evidence ledger, but review gates
  inclusion/exclusion).

These are **suggestions**. A project's `harness.lock.yaml` may lower
or raise them with a recorded decision.

## Bounded autonomy

Autonomy is bounded by:

- **Scope**: which paths, which tools, which capabilities.
- **Validators**: which sensors must pass before the action is
  considered done.
- **Retries**: how many times the agent may repair before
  escalating.
- **Rollback points**: where the project reverts to if a retry
  fails.
- **Escalation conditions**: when the agent must stop and request a
  human gate.

## Cross-references

- `HARNESS.md` §Permissions and autonomy (terse canonical).
- `core/invariants.yaml` INV-012 (bounded_autonomy, locked).
- `core/schemas/extension/permission-profile.schema.json` for the
  data shape.
- `core/policies/override-protocol.md` for raising autonomy beyond
  defaults.

## Source references

- Anthropic — Managed agents (capability-specific autonomy,
  structural isolation of credentials).
- OpenAI — Harness engineering (autonomy matched to task criticality).
- Mitchell Hashimoto — My AI adoption journey (autonomy earned, not
  granted).