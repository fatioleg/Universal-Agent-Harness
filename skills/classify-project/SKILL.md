---
name: classify-project
description: Use when starting a new project with the Universal Agent Harness — walks the human through 24 structured questions (across 6 groups: complexity, evidence, knowledge, coordination, development discipline, observability) to recommend an archetype, capabilities, tool contracts, schemas, sensors, topology, autonomy, permissions, and SDD/TDD/brownfield/ADR/change-protocol configurations before any Bootstrap Report is produced. Triggered by phrases like "start a new project", "bootstrap a project", "classify this project", "qual arquitetura de harness", "qual harness usar".
---

# Skill: classify-project

This skill runs BEFORE `bootstrap/BOOTSTRAP.md`. It produces a
classification summary that the agent then uses to draft the
Bootstrap Report.

## Coverage of the 24 questions

The questions cover every significant capability, archetype,
tool contract, schema, sensor, and workflow in the harness:

- **11 archetypes**: scientific-research, computational-
  science, computational-chemistry, literature-review,
  knowledge-base, data-analysis, software-development,
  document-production, grant-project-proposal, full-sdd-
  project, knowledge-digestion.
- **22 capabilities**: discovery, specification, state-
  continuity, source-ingestion, normalization, cataloging,
  lexical-retrieval, semantic-retrieval, graph-retrieval,
  context-compression, scientific-evidence, computational-
  execution, data-analysis, artifact-production, independent-
  review, external-write, publication, long-running-
  orchestration, knowledge-digestion-pipeline, sdd-workflow,
  subagent-orchestration, checkpoint-handoff.
- **12 tool contracts**: check-invariants, diff-harness,
  verify-artifact, list-events, sensor-trend, lock-drift-
  check, scaffold-project, caveman-compress, markitdown-
  normalize, graphify-build, obsidian-interface, notebooklm-
  explore.
- **11 extension schemas**: state, evidence-ledger, decisions,
  tool-contract, permission-profile, failure-registry,
  eval-result, observability-run, acceptance-criterion,
  test-case, change-request.
- **10 eval categories** from `evals/catalog.md`.
- **Topologies A–E** and **autonomy levels L0–L5**.
- **Workflows**: proportional design (complexity
  classification), brownfield protocol, TDD test strategies,
  ADR format, change protocol, state continuity, independent
  review.

## Where this skill lives

This skill ships **inside the Universal Agent Harness repository**
itself, at `skills/classify-project/SKILL.md`. When an agent is
pointed at this repository (via submodule, pinned clone, or remote
URL), it discovers the skill automatically:

- **Claude Code** discovers skills under
  `skills/<name>/SKILL.md` in the workspace, or under
  `.claude/skills/<name>/SKILL.md`.
- **Codex** discovers skills under
  `.codex/agent-configuration/skills/<name>/SKILL.md`.

To make the skill available in a project, either:

- add this repository as a submodule at `.harness/upstream` (the
  skill becomes visible at `.harness/upstream/skills/classify-project/SKILL.md`);
- copy `skills/classify-project/` into the project's own
  `.claude/skills/` or `.codex/agent-configuration/skills/`
  directory; or
- symlink the directory into the project's skills folder.

The README.md of this repository also references the skill so an
agent reading the repo top-down finds it.

## When to use

- The human has just declared a new project.
- The human wants to know which archetype, capabilities, and tools
  apply.
- The agent is preparing a Bootstrap Report and needs the
  classification as input.
- The human asks, in any language, "which harness / which
  architecture / qual arquitetura / como estruturar este projeto".

## When NOT to use

- The project already has a `project.yaml` and a `harness.lock.yaml`.
- The classification has already been recorded.
- The project is being maintained, not bootstrapped.

## How to run

1. Read `skills/classify-project/questions.md`.
2. Ask the questions one at a time, in order, following the branch
   logic. Group questions (1–3 deliverable/source/duration;
   4–6 evidence/reproducibility/risk; 7–9 knowledge/retrieval/graph;
   10–12 coordination/parallelism/autonomy; 13–15 external/gates/
   observability).
3. Skip questions whose branch logic says to skip based on prior
   answers (notably Q9 skips graph when relational queries are
   absent).
4. When all required questions are answered, read
   `skills/classify-project/decision-tree.md`.
5. Map the answer set to a recommendation using the decision tree.
6. Fill in `skills/classify-project/output-template.md`.
7. Present the filled template to the human as a recommendation,
   not a decision. The human decides.

## Rules

- **Do not modify the target project.** Classification is read-only
  with respect to the project workspace.
- **Do not produce a Bootstrap Report yet.** That comes after the
  human accepts the classification.
- **One question at a time.** Do not dump all 24 questions.
- **Allow UNKNOWN.** Some questions may legitimately be unknown
  at classification time. Record UNKNOWN in the output rather than
  guess.
- **Stay language-aware.** The user prefers Portuguese for
  explanatory text; technical IDs and YAML keys stay English.
- **Adapt the question phrasing to the user's language.** The
  YAML structure of the answer set stays fixed; the natural
  language around it does not.

## Outputs

The filled `output-template.md` becomes part of the project's
`project.yaml` and feeds the Bootstrap Report.

## Cross-references

- `bootstrap/BOOTSTRAP.md` (next step after classification).
- `bootstrap/project-input.example.yaml` (target shape).
- `archetypes/README.md` (the 9 reference patterns).
- `core/schemas/extension/*.json` (data shapes the classification
  recommends instantiating).
- `contracts/tools/README.md` (the tool contract menu).
- `evals/catalog.md` (the sensor menu).
- `docs/agent-topology.md` (Levels A–E for the topology output).
- `docs/autonomy-levels.md` (L0–L5 for the autonomy output).