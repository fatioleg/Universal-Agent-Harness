# Architecture

## Architectural thesis

The Universal Agent Harness is a meta-specification that helps an agent compile
project conditions into a project-specific harness. The universal layer stores
invariants, defaults, composition rules, schemas, and representative evals. It
does not execute every project and does not prescribe a fixed agent team.

Codex/Codex Cloud and Claude Code use separate thin entrypoints (`AGENTS.md` and
`CLAUDE.md`) that route to the same canonical `HARNESS.md`. Shared behavior is
never maintained independently in the two platform files.

```text
Project input
  → read-only discovery
  → classification
  → capability selection
  → H0–H3 resolution
  → dry-run report
  → human gate
  → minimal materialization
  → validation and lock
```

## Four planes

The planes are responsibility lenses, not mandatory services or symmetric
directories.

| Plane | Responsibility |
|---|---|
| Control | intent, specification, routing, permissions, budgets, gates, state transitions |
| Knowledge | sources, representations, retrieval, context assembly, evidence, provenance |
| Execution | agents, models, skills, tools, code, compute, external services |
| Assurance | guides, sensors, validators, evals, observability, review, recovery |

Assurance observes the other planes. A small project can have a trivial
Knowledge Plane and no orchestration service.

## Configuration hierarchy

```text
H0: universal invariants, defaults, schemas
H1: optional lifecycle profile + capability overlays + domain packs
H2: project configuration and bindings
H3: short-lived task restrictions and context
```

Resolution is typed and pinned:

```text
Resolved Harness = resolve(H0, H1, H2, H3)
```

This is not string concatenation or generic YAML merge. Locked invariants cannot
be removed; permissions can be restricted but not silently expanded; project
instances pin exact versions and migrate by explicit diff and validation.

## H1 taxonomy

The architecture separates three concepts that are commonly mixed:

- lifecycle profile: recurring project workflow;
- capability overlay: cross-cutting behavior such as scientific evidence;
- domain pack: terminology, tools, sensors, and practices for a domain.

No H1 packages ship in v0.2.0. A package should be promoted only after real
projects demonstrate repeated workflow, sensors, or bindings that cannot be
expressed cleanly by H0 plus project configuration.

## Context and knowledge

Sources are immutable. Representations are derived. Summaries are disposable.
Graphs are interpretations. Evidence remains authoritative.

Complexity ladder:

```text
files + lexical search
  → source manifest
  → semantic retrieval
  → evidence-linked graph
  → compression of retrieved context
```

## Evolution

Failures improve the harness only when they are systemic:

```text
failure → root cause → local/systemic → repair
        → harness patch → regression case → eval → release
```

The first pilot should reveal which declarative rules require mechanical
enforcement in a future resolver CLI.

## Upstream use from projects

The universal repository is referenced, not copied. A project pins an upstream
tag and commit in `harness.lock.yaml`, then materializes only its own platform
entrypoints, configuration, and triggered artifacts. Migration to a newer H0
requires an explicit diff, validation, eval run, and new lock.
