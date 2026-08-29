# Architecture Decision Record (ADR) Template

This document defines the canonical ADR format used by this
harness, aligned with mainstream practice (AWS, Microsoft
Azure Well-Architected Framework, [adr.github.io](https://adr.github.io/)).

Use ADRs to record **significant, hard-to-reverse** decisions.
Skip them for trivial choices.

## When to write an ADR

Per AWS and Microsoft guidance:

- The decision has significant impact on system structure,
  scalability, or cross-cutting concerns.
- Future contributors will need to understand the reasoning,
  not just the outcome.
- The decision is **hard or expensive to reverse**.

Do not write an ADR for:

- Routine library choices inside an already-decided stack.
- Naming conventions.
- Bug fixes.
- Trivial refactors.

The harness already records architecture decisions in
`docs/DECISIONS.md` as `AD-XXX` entries. This template is the
**shape** each entry should follow. Existing AD-001 through
AD-012 may be retro-fitted to this format.

## The ADR format

```markdown
# ADR-NNNN — <Short descriptive title>

- Status: <proposed | accepted | deprecated | superseded>
- Date: <ISO date>
- Deciders: <human(s) and/or agent(s)>

## Context

What is the issue or decision at hand? What forces are at play?
What constraints exist?

Cite requirements, prior ADRs, or external sources where
relevant.

## Decision

What is the change being made, in one or two sentences?

State the decision as a positive commitment. Avoid hedging.

## Alternatives considered

What other options were considered? For each:

- **<Option name>** — <one-sentence description>.
  - Pros: ...
  - Cons: ...

## Consequences

What becomes easier? What becomes harder? What risks are
introduced?

Positive consequences first, then negative consequences, then
risks. Each is one or two sentences.

## Compliance

Links to relevant standards, policies, invariants, or other
ADRs.

## Notes (optional)

Any additional context that does not fit the fields above.
```

## Naming convention

- File: `NNNN-<kebab-case-title>.md`.
- Stored in `docs/adr/` (recommended) or appended to
  `docs/DECISIONS.md` for compactness.
- Status transitions: `proposed` → `accepted` → (`deprecated` or
  `superseded by ADR-NNNN`).

## Worked example

```markdown
# ADR-0013 — Use SAX over DOM for ingestion of large XML corpora

- Status: accepted
- Date: 2026-08-29
- Deciders: human:owner + agent:literature-reviewer

## Context

The literature-review archetype ingests XML corpora up to ~2 GB.
DOM parsing loads the entire tree into memory, peaking at ~6x
the file size. The current ingest path is OOM-killing on
edge devices (4 GB RAM). The legacy parser uses DOM.

## Decision

Replace the DOM parser with a SAX-style streaming parser for
ingest. The SAX parser emits incremental events consumed by
the existing canonical-Markdown writer.

## Alternatives considered

- **DOM with disk-backed tree** — Pros: simpler API. Cons:
  disk I/O adds 30–40% latency on cold cache; still
  vulnerable to malformed input blowing up the tree.
- **Pull parser (e.g., lxml.iterparse)** — Pros: hybrid
  model, retains parent context. Cons: introduces a new
  dependency; team has no muscle memory for it.

## Consequences

- **Easier**: ingest on 4 GB edge devices. Predictable memory
  ceiling.
- **Harder**: parser code is more complex. Event handlers
  must handle partial state.
- **Risks**: if a handler forgets to release state, the
  parser leaks across events. Mitigation: a single
  per-document handler instance, plus a characterization
  test suite (EVAL-002 ingestion).

## Compliance

- INV-001 preserve-sources
- INV-005 least-privilege
- `evals/catalog.md` EVAL-002

## Notes

This decision was driven by a failure observed in pilot #2
(see `failure-registry.json` FAIL-0014).
```

## Cross-references

- AWS — [Master ADRs best practices](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)
- Microsoft — [Maintain an ADR](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record)
- [adr.github.io](https://adr.github.io/)
- Existing entries: `docs/DECISIONS.md` (AD-001 through AD-012).