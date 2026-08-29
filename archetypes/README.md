# Archetypes

Reference patterns for recurring scientific and engineering workflows.
These are **not H1 packages**. They are documentation that informs
classification, capability selection, and sensor choice during the
Bootstrap Report. They cannot be referenced by
`source_versions.H1` in `harness.lock.yaml` and they cannot be merged
via `core/merge-policy.yaml`.

## Promotion to H1

A reference pattern becomes an H1 package only when:

1. At least two completed real projects have used the pattern.
2. The pattern's workflow, sensors, and bindings can be expressed as
   a YAML overlay that obeys `core/merge-policy.yaml` field policies.
3. An Architecture Decision (`docs/DECISIONS.md`) records the
   promotion.
4. An eval case in `evals/bootstrap-cases.yaml` exercises the
   promoted pattern.

Until all four are satisfied, the pattern remains a reference here.

## The 11 reference patterns

| Pattern | When to reach for it |
|---|---|
| scientific-research | Empirical investigation; high evidence burden; hypothesis-driven |
| computational-science | Simulation or numerical analysis; reproducibility is core |
| computational-chemistry | Subset of computational-science with chemistry domain sensors |
| literature-review | High-recall retrieval; citation verification; PRISMA-style inclusion/exclusion |
| knowledge-base | Long-running curation; high evidence churn; hybrid retrieval |
| data-analysis | Dataset-centered; statistical sensors; visualization checks |
| software-development | Code-centered; tests/linters as primary sensors; CI gates |
| document-production | Template-driven; formatting validators; review cycles |
| grant-project-proposal | Deadline-aware; funder-specific sensors; budget computation |
| full-sdd-project | Complex multi-week/multi-agent project needing full SDD lifecycle, named subagent roles, persistent memory, gates, handoffs |
| knowledge-digestion | Project whose primary capability is ingesting a corpus through caveman + MarkItDown + Graphify + Obsidian (+ optional NotebookLM) |

## How to read a stub

Each stub below uses the same template:

- When to use
- Inherits from
- Differs from base by
- Required sensors (from evals/catalog.md)
- Typical tool profile
- Evidence & provenance requirements
- Agent topology default
- Autonomy defaults
- Open questions / not-yet-defined
- Example instantiation

The "Open questions" section is deliberate. Each stub is honest
about what is not yet known or what needs empirical evidence.

## What this directory does NOT contain

- Executable tools or scripts.
- Vector or graph database schemas.
- A prescribed agent team.
- A binding default for any project.

A project that needs none of these patterns may still build a
project-specific harness from H0 alone.