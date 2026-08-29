# Architecture Decision Log

## AD-001 — Canonical location

- Status: accepted
- Date: 2026-08-29
- Decision: use `AAAAMyArchitetures/Universal-Agent-Harness/` and preserve the
  existing folder name for now.
- Reason: avoid breaking synchronized paths and preserve existing sources.

## AD-002 — H1 composition

- Status: accepted
- Decision: one optional lifecycle profile plus composable capability overlays
  and domain packs.
- Rejected: a mutually exclusive list mixing domains, workflows, and outputs.

## AD-003 — Scope of v0.1.0

- Status: accepted
- Decision: provide an agent-readable dry-run protocol, typed schemas, locked
  invariants, merge policy, minimal materialization contract, and eval fixtures.
- Deferred: executable resolver, vector database, graph, session automation,
  fixed multiagent roles, and platform-specific adapters.

## AD-004 — State and memory

- Status: accepted
- Decision: no universal `.memory/` tree. Persistent state is conditional;
  conversation history is never authoritative.

## AD-005 — Permissions

- Status: accepted
- Decision: least privilege with explicit gates for permission expansion,
  external effects, irreversible actions, publishing, sending, and spending.

## AD-006 — Language

- Status: accepted
- Decision: configuration keys, schemas, and stable IDs use English;
  explanatory documentation may use Portuguese. Avoid full bilingual duplication.

## AD-007 — Pilot order

- Status: accepted
- Decision: test increasing complexity with a simple document, a scientific
  literature review, and a computational chemistry project.

## Pending decisions

- Select the first real project pilot.
- Decide whether v0.2.0 should add a small local validator/resolver after the
  first pilot exposes actual enforcement needs.
- Promote the first H1 package only after repeated evidence justifies it.

## AD-008 — Cross-platform entrypoints

- Status: accepted
- Date: 2026-08-29
- Decision: maintain thin `AGENTS.md` and `CLAUDE.md` entrypoints that route to
  one canonical `HARNESS.md`.
- Rejected: duplicate full harness instructions for Codex and Claude Code.

## AD-009 — v0.3.0 scope

- Status: accepted
- Date: 2026-08-29
- Decision: extend v0.2.0 with archetypes, extension schemas, principles,
  classification skill, tool contracts, and operational concept docs. Keep all
  v0.2.0 schemas, invariants, merge-policy, and platform entrypoints unchanged.
- Reason: deliver the gap-closure items identified in the cross-source audit
  (OpenAI, Hashimoto, Anthropic, Böckeler) without breaking v0.2.0
  compatibility or violating the minimality principle.

## AD-010 — Tool contracts without implementations

- Status: accepted
- Date: 2026-08-29
- Decision: v0.3.0 ships tool **contracts** (YAML specifications in
  `contracts/tools/`) but no executable implementations. Tool implementations
  are deferred to v0.4.0+ until at least two real pilots demonstrate stable
  classifiers per the merged-policy `minimality` rule (INV-011).
- Reason: AD-003 defers the executable resolver. Tool contracts equip the agent
  with knowledge of what tools exist without prematurely committing to
  implementations. AD-010 records this as a deliberate distinction, not an
  oversight.

## AD-009 — GitHub distribution model

- Status: accepted
- Date: 2026-08-29
- Decision: publish as a versioned upstream harness repository. New projects pin
  a tag/commit or release checksum and materialize only their resolved harness.
- Rejected: using GitHub “Use this template” as the primary mechanism, because
  copying the full tree causes template drift.
