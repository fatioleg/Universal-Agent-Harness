# Canonical Harness Contract

This file contains platform-neutral behavior shared by Codex, Codex Cloud, and
Claude Code. Platform entrypoints route here instead of duplicating the rules.

## Mission

Configure the smallest robust harness required for the current project. A good
harness makes correct behavior easy to perform and verify, while making incorrect
behavior visible, recoverable, traceable, or impossible to pass through gates.

## State machine

```text
INITIAL → DISCOVERED → PROPOSED → APPROVED → MATERIALIZED → VALIDATED
```

Every new project starts in `dry-run`. Do not move from `PROPOSED` to
`MATERIALIZED` without approval when the proposal contains material scientific,
strategic, external, irreversible, permission, publication, or cost decisions.

## Universal defaults

- One agent plus tools.
- Progressive disclosure and just-in-time retrieval.
- Workspace/repository as the operational system of record.
- Original sources preserved; derived representations never replace them.
- Deterministic checks before inferential review.
- Least privilege and bounded autonomy.
- Visible assumptions, uncertainty, missing bindings, failures, and retries.
- Infrastructure only when triggered by a requirement, risk, or recurring failure.

Locked rules are defined in `core/invariants.yaml` and cannot be silently
weakened by a more specific configuration.

## Read order

1. Platform entrypoint.
2. This canonical contract.
3. `bootstrap/BOOTSTRAP.md`.
4. Target project state and input.
5. Relevant core rules, schemas, evidence, and tools on demand.

Do not preload the entire upstream repository or target workspace.

## Discovery

- Read-only until the Bootstrap Report is approved.
- Inventory existing files before proposing a directory tree.
- Identify authoritative sources, generated artifacts, duplicates, stale state,
  constraints, available tools, and deterministic verification opportunities.
- Preserve user organization and sharing state unless change is requested.
- Do not infer that access to a workspace authorizes adjacent or external writes.

## Classification

Classify the project by:

- primary lifecycle;
- domain and specialist burden;
- duration and restartability;
- evidence and provenance burden;
- computational execution;
- deliverable complexity;
- external effects and irreversibility;
- scientific, operational, uncertainty, security, and cost risk;
- target agent platforms.

State assumptions and confidence. Ask only questions that materially change the
harness, permissions, risk, or deliverables.

## H0–H3 configuration

```text
H0: universal invariants, defaults, schemas
H1: optional lifecycle profile + capability overlays + domain packs
H2: project configuration and bindings
H3: short-lived task restrictions and context
```

Resolve configuration using `core/merge-policy.yaml`. This is typed resolution,
not prompt concatenation or generic YAML merge.

Do not confuse:

- lifecycle profile: recurring workflow;
- capability overlay: cross-cutting behavior;
- domain pack: domain terminology, tools, and sensors.

Promote an H1 package only after repeated projects demonstrate a common lifecycle,
capability bundle, or domain contract.

## Agent topology

| Level | Use when |
|---|---|
| A | cohesive task; tools and deterministic checks are sufficient |
| B | material result requires independent review |
| C | one distinct specialist or context boundary is required |
| D | subtasks are genuinely independent and parallelizable |
| E | high risk, broad decomposition, several specialties, independent verification |

Record the trigger for any topology above A. More agents are coordination cost,
not evidence of maturity.

## Knowledge and context

Escalate only as needed:

1. filesystem, naming, lexical search;
2. source manifest and provenance;
3. semantic retrieval;
4. evidence-linked graph;
5. compression of retrieved context.

```text
Task context = Compress(Retrieve(Knowledge, Task))
```

Sources are immutable. Representations are derived. Summaries are disposable.
Graphs are interpretations. Evidence remains authoritative.

## Permissions and autonomy

Resolve effective read, write, modify, delete, execute, network, install,
publish, send, spend, and merge capabilities when relevant. Project/task layers
may restrict permissions. Expansion beyond universal defaults requires explicit
approval and must appear in the lock.

Autonomy is capability-specific and bounded by scope, validators, retry limits,
rollback points, and escalation conditions.

## Assurance

Keep the questions separate:

- validation: is this execution/result correct?
- QA: does the artifact satisfy its requirements?
- eval: does the harness still perform across representative cases?

Use computational sensors for deterministic properties. Use inferential or
human review for scientific meaning, ambiguity, and material judgment. An
independent reviewer receives the specification, artifact, evidence, and
acceptance criteria rather than unnecessary producer context.

## Materialization

Create only files listed in the approved report. At least one platform entrypoint
plus `project.yaml` and `harness.lock.yaml` are required. Both entrypoints are
created when both platforms are targets.

Conditional artifacts require explicit triggers:

- `state/current.md`: long-running, interruptible, or restartable work;
- `sources/manifest.jsonl`: material evidence/provenance burden;
- `decisions/`: alternatives and consequences must persist;
- `evals/`: repeated behavior or regression risk;
- specialist/reviewer instructions: justified topology above A;
- semantic index or graph: demonstrated retrieval need.

After materialization, validate schemas, links, permissions, invariants, tool
bindings, minimality, and lock reproducibility.

## Recovery and learning

```text
PLAN → PRECHECK → EXECUTE → OBSERVE → SENSE
                                      ├─ PASS → COMMIT
                                      └─ FAIL → CLASSIFY
                                                  ├─ REPAIR → REVALIDATE
                                                  └─ ROLLBACK / ESCALATE
```

Promote a failure into this upstream harness only when it is systemic and has a
regression case. Do not turn every local incident into a universal rule.

## Dry-run output

Produce a `BOOTSTRAP REPORT` containing:

1. project understanding;
2. discovery inventory;
3. classification, assumptions, and risk;
4. selected capabilities;
5. proposed H0–H3 resolution;
6. topology and justification;
7. knowledge and context strategy;
8. permissions, autonomy, and human gates;
9. validation, QA, eval, observability, and recovery;
10. exact files to create and their triggers;
11. warnings, blockers, and open decisions;
12. recommendation: `APPROVE`, `REVISE`, or `BLOCK`.

