# Agent Topology

This document expands the topology table in `HARNESS.md` §Agent
topology. A project starts at Level A and escalates only when a
trigger justifies the coordination cost.

## Levels

| Level | Name | When to use |
|---|---|---|
| A | Single agent plus tools | The default. Tools and deterministic checks are sufficient for the task. |
| B | Agent plus independent reviewer | Material results need a second perspective; reviewer does not modify the producer's artifact. |
| C | Orchestrator plus one specialist | One distinct specialty or context boundary is required (e.g., computational chemistry domain pack). |
| D | Parallel specialists | Subtasks are genuinely independent and parallelizable. Coordination contract is explicit. |
| E | Multiagent team plus independent verification | High risk, broad decomposition, multiple specialties, independent verification per task. |

## Escalation triggers

Move from one level to the next when ANY of these is true:

- **A → B**: the result drives a material decision and a single agent's
  self-critique is insufficient (per Anthropic long-running-apps,
  "tuning a standalone evaluator to be skeptical turns out to be
  far more tractable than making a generator critical of its own
  work").
- **B → C**: one specialty or context boundary is distinct enough
  to deserve its own instructions, tools, and review contract.
- **C → D**: subtasks are independent enough to run in parallel
  with separate contracts.
- **D → E**: risk, breadth, or specialty count makes a coordinator
  plus independent verification cheaper than the loss of
  accountability from a flat team.

## When NOT to escalate

- More agents are coordination cost, not evidence of maturity
  (Hashimoto: "don't run agents for the sake of running agents").
- For slam-dunk tasks, run agents one at a time, not in parallel.
- Multiagent is not a default. It is an earned structure.

## Recording the topology

Record the topology level, the level label, and the justification in
the project's `harness.lock.yaml` under `topology`. See the
`resolved-harness.schema.json` for the exact shape.

## Cross-references

- `HARNESS.md` §Agent topology (canonical, terse).
- `core/schemas/extension/tool-contract.schema.json` for the tools
  each agent role is bound to.
- `docs/autonomy-levels.md` for per-capability autonomy that
  complements topology.

## Source references

- Anthropic — Harness design for long-running apps (generator /
  evaluator GAN pattern).
- OpenAI — Harness engineering blog post (default to one agent
  plus tools; escalate only with a recorded trigger).
- Mitchell Hashimoto — My AI adoption journey (avoid running agents
  for the sake of running agents).