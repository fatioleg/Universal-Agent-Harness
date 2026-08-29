# Principle 10: Proportional Design

## Statement

The architecture must be the **smallest sufficient architecture**
that satisfies the actual requirements, risks, and constraints
of the project. Overengineering is a defect. Underengineering is
also a defect when safety, auditability, or reproducibility are
at stake.

## Why this is a principle

Per Fowler's *Practical Test Pyramid*, test infrastructure must
match reality, not ambition. Per Hashimoto's adoption story,
agents "for the sake of running agents" waste time and add
coordination cost. Per Anthropic's long-running harness work,
"every component in a harness encodes an assumption about
what the model can't do on its own, and those assumptions are
worth stress testing" — including the assumption that you need
a component.

The default failure mode in agentic projects is **upward
complexity drift**: a small project ends up with microservices,
a vector store, a graph database, and a five-agent topology
because the template offered them. The reverse failure mode —
underengineering a critical project — is rarer but real.

## What it requires

Classify the project on a scale from **trivial** to **complex
/ critical**:

- **trivial** — single deliverable, no integration, no external
  action, no reproducibility requirement. Single agent +
  tools. No specs beyond a paragraph.
- **small** — short timeline, one domain, one or two
  deliverables. Single agent + optional reviewer. SDD
  recommended.
- **medium** — multi-week, multi-deliverable, possibly
  multi-domain. SDD required; named subagent roles
  selectively.
- **large** — multi-month, multi-agent justified, evidence
  burden material, scientific or regulatory. Full SDD
  archetype; structured handoffs; gates; gates; gates.
- **complex / critical** — life, safety, large budget,
  regulatory, clinical. Add independent review at every
  gate; characterise brownfield before refactoring; full
  traceability REQ→AC→TEST→IMPL.

For each classification, **only the capabilities and
sensors justified by the risks and constraints apply**. A
trivial project does not need `archetypes/full-sdd-project.md`.

## When this can be overridden

The principle itself is non-overridable (analogous to preserve-
sources). The classification is overridable per project when a
specific risk justifies more or less infrastructure, recorded
in `decisions.json` with a compensating control.

## How to verify

- The Bootstrap Report includes an explicit complexity
  classification.
- The chosen archetype matches the classification.
- The selected capabilities map to documented risks, not
  template defaults.
- INV-011 (minimality) lock check.

## Failure mode if ignored

Two failure modes:

- **Overengineering**: small project carries infrastructure
  cost without benefit. Agents waste time coordinating.
  Maintenance debt accrues. Simple changes become multi-day
  exercises.
- **Underengineering**: complex project lacks the gates,
  reviews, or sensors it needs. A single failure passes
  through gates that should have caught it.

The discipline is to pick the smallest sufficient design that
**also** satisfies the actual risk profile.

## Cross-references

- `core/invariants.yaml` INV-011 minimality.
- `archetypes/full-sdd-project.md` — when classification is
  large / complex.
- `docs/sdd.md` — scale classification inputs.
- Martin Fowler — *Practical Test Pyramid* (shape follows
  economics).
- Mitchell Hashimoto — *My AI adoption journey* (don't run
  agents for the sake of running agents).