# Project Bootstrap Protocol

## Purpose

Analyze a new project and propose the smallest sufficient project-specific
harness for its declared agent platforms. This protocol compiles project
conditions into a reviewed plan before creating files.

## Phase A — Dry-run

### 1. Understand

Read the user's objective, domain, inputs, workspace, deliverables, constraints,
risks, deadline, target agents, and special requirements. Convert known
information to the project-input schema. Ask only questions whose answers
materially change scope, risk, permissions, architecture, or deliverables.

### 2. Discover — read-only

Inventory the target workspace. Identify authoritative sources, existing
instructions, formats, duplicates, generated artifacts, state, tools, external
dependencies, and available deterministic validators. Do not modify files.

### 3. Classify

Classify:

- primary lifecycle;
- domain and specialist requirements;
- one-off, short, or long-running duration;
- evidence burden;
- computational execution;
- deliverable complexity;
- external effects and irreversibility;
- scientific, operational, uncertainty, and cost risk.

State assumptions and confidence. Do not invent an archetype merely to label a
domain or output format.

### 4. Select capabilities

Choose only capabilities triggered by the project. Bind a tool or skill only
when available and appropriate. Record an explicit blocker when a required
binding is unavailable.

### 5. Configure topology

Start at A. Escalate only when independence, specialization, parallel work, or
risk justifies coordination cost. Record the trigger and consolidation contract
for levels B–E.

### 6. Configure knowledge and context

Start with files and lexical retrieval. Add a source manifest for provenance,
semantic retrieval for corpus-scale paraphrase search, and a graph only for
repeated relational questions with evidence pointers. Retrieve before compacting.

### 7. Configure permissions and autonomy

Resolve effective capabilities with least privilege. List read, write, modify,
delete, execute, network, install, publish, send, spend, and merge explicitly
when relevant. Expansion beyond universal defaults requires a human gate.

### 8. Configure assurance and recovery

Define acceptance criteria, deterministic validators, inferential review,
independent review, retry limits, rollback points, and escalation conditions.
Keep validation, QA, and eval distinct.

### 9. Resolve H0–H3

Apply `core/merge-policy.yaml`. More specific layers can specialize allowed
fields but cannot remove locked invariants or silently expand permissions.
Record versions, decisions, warnings, and field provenance.
Pin the upstream harness version and commit. Do not resolve only against an
unversioned branch name.

### 10. Produce Bootstrap Report

Return the 12-section report required by `AGENTS.md`. Include the exact proposed
directory tree and a list mapping every non-base file to its trigger. End with
`APPROVE`, `REVISE`, or `BLOCK`.

## Human gate

Approval of a broad objective is not approval for every external or irreversible
action. Obtain explicit approval for material choices listed in the report.

## Phase B — Materialize

After approval:

1. create `project.yaml` from the accepted input;
2. create a short platform entrypoint for each selected target agent;
3. create a resolved `harness.lock.yaml` with upstream version and commit;
4. create only conditionally triggered artifacts;
5. validate schemas, links, invariants, permissions, bindings, and minimality;
6. run the relevant bootstrap eval fixtures;
7. report `BOOTSTRAP PASS` or a visible blocking failure;
8. start project execution only after pass.

## Default generated files

```text
AGENTS.md          # Codex/Codex Cloud target
CLAUDE.md          # Claude Code target
project.yaml
harness.lock.yaml
```

At least one platform entrypoint is required. Generate both only when both
platform families are declared targets.

## Conditional triggers

| Artifact | Create when |
|---|---|
| `state/current.md` | work is long-running, interruptible, or needs restart |
| `sources/manifest.jsonl` | provenance/citation/evidence burden is material |
| `decisions/` | alternatives and consequences must be retained |
| `evals/` | behavior is repeated or a regression is plausible |
| reviewer instructions | independence is required by risk |
| specialist instructions | expertise or context isolation is distinct |
| semantic index | lexical retrieval has demonstrated limitations |
| evidence-linked graph | relational queries recur and improve materially |

## Recovery

```text
PLAN → PRECHECK → EXECUTE → OBSERVE → SENSE
                                      ├─ PASS → COMMIT
                                      └─ FAIL → CLASSIFY
                                                  ├─ REPAIR → REVALIDATE
                                                  └─ ROLLBACK / ESCALATE
```
