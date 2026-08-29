# Core Principles

Nine human-readable principle statements that explain the reasoning
behind the universal invariants in `core/invariants.yaml`. Each principle
maps to one or more invariant IDs. Principles are not enforcement
mechanisms; they are the rationale agents and humans should consult
when interpreting the invariants.

## When to read this

- When bootstrapping a new project and selecting capabilities.
- When proposing an override of a locked invariant.
- When reviewing why a sensor or eval exists.
- When writing a new archetype or capability overlay.

## Principle index

1. [Preserve sources](./01-preserve-sources.md) — INV-001
2. [Maintain provenance](./02-maintain-provenance.md) — INV-002
3. [Least privilege](./03-least-privilege.md) — INV-005, INV-006
4. [Verify critical outputs](./04-verify-critical-outputs.md) — INV-008
5. [Expose failures](./05-expose-failures.md) — INV-009
6. [Maintain state](./06-maintain-state.md) — INV-003, INV-004
7. [Progressive disclosure](./07-progressive-disclosure.md) — INV-007
8. [Prefer deterministic](./08-prefer-deterministic.md) — INV-008
9. [Reproducibility](./09-reproducibility.md) — INV-003, INV-012
10. [Proportional design](./10-proportional-design.md) — INV-011