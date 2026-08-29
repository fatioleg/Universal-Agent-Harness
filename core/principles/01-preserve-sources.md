# Principle 01: Preserve Sources

## Statement

Original user sources must never be overwritten, silently transformed,
or deleted by any agent action.

## Why this is a principle

Sources are epistemologically authoritative. A derived representation
(markdown summary, embedding, graph node) can be regenerated; a
destroyed source cannot. Anthropic managed-agents makes the same
distinction: "Sources are immutable. Representations are derived.
Summaries are disposable. Graphs are interpretations. Evidence remains
authoritative."

## What it requires

- All agent writes target derived locations (`canonical/`, `derived/`,
  `summaries/`) explicitly named in the project layout.
- The original source directory (`source/`, `inputs/`, or equivalent)
  is read-only by configuration and by permission profile.
- A copy of the original must exist before any transformation begins.

## When this can be overridden

Never. The override protocol (`core/policies/override-protocol.md`)
classifies this principle as non-overridable. The source is the ground
truth; without it, evidence provenance collapses.

## How to verify

- INV-001 lock check in `core/invariants.yaml`.
- Permission profile declares `read` only for the source directory.
- The Bash sensor (planned tool contract `lock-drift-check`) verifies
  no write events target immutable paths.

## Failure mode if ignored

The agent's claim cannot be traced. The evidence ledger records a
pointer to a path that no longer exists. The project cannot survive
a model upgrade, a re-run, or a peer-review challenge.