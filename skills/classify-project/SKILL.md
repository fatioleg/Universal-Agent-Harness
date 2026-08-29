---
name: classify-project
description: Use when starting a new project with this harness — walks the human through 15 structured questions to recommend an archetype, capabilities, tool contracts, and sensors for the project before any Bootstrap Report is produced.
---

# Skill: classify-project

This skill runs BEFORE `bootstrap/BOOTSTRAP.md`. It produces a
classification summary that the agent then uses to draft the
Bootstrap Report.

## When to use

- The human has just declared a new project.
- The human wants to know which archetype, capabilities, and tools
  apply.
- The agent is preparing a Bootstrap Report and needs the
  classification as input.

## When NOT to use

- The project already has a `project.yaml` and a `harness.lock.yaml`.
- The classification has already been recorded.
- The project is being maintained, not bootstrapped.

## How to run

1. Read `skills/classify-project/questions.md`.
2. Ask the questions one at a time, in order, following the branch
   logic.
3. Skip questions whose branch logic says to skip based on prior
   answers.
4. When all required questions are answered, read
   `skills/classify-project/decision-tree.md`.
5. Map the answer set to a recommendation.
6. Fill in `skills/classify-project/output-template.md`.
7. Present the filled template to the human as a recommendation,
   not a decision. The human decides.

## Rules

- **Do not modify the target project.** Classification is read-only
  with respect to the project workspace.
- **Do not produce a Bootstrap Report yet.** That comes after the
  human accepts the classification.
- **One question at a time.** Do not dump all 15 questions.
- **Allow UNKNOWN.** Some questions may legitimately be unknown
  at classification time. Record UNKNOWN in the output rather than
  guess.
- **Stay language-aware.** The user prefers Portuguese for
  explanatory text; technical IDs and YAML keys stay English.

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