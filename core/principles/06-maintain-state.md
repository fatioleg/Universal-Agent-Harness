# Principle 06: Maintain State

## Statement

Critical project state, decisions, and evidence must return to the
project workspace. Conversation history and informal summaries are
not authoritative project memory.

## Why this is a principle

Anthropic managed-agents: store context outside Claude's context
window; the session log is the durable layer. Anthropic long-running:
use structured handoff artifacts between sessions. Hashimoto: do not
let critical state live only in a Codex or Claude thread. The
project repository is the portability boundary.

## What it requires

- A `state/current.md` or `state.json` file (schema in
  `core/schemas/extension/state.schema.json`) is the system of record.
- Auto-memory features are local convenience, not authoritative.
- Handoff between sessions uses the state file plus the evidence
  ledger, not free-form chat transcripts.

## When this can be overridden

Overridable per task only when the state is ephemeral and the
project duration is `one-off`.

## How to verify

- INV-003, INV-004 lock checks.
- A restart scenario (Eval EVAL-007) verifies the next session can
  resume from the state file alone.

## Failure mode if ignored

A second session restarts from scratch. Decisions made in the first
session are forgotten. The project accumulates duplicate or
contradictory work.