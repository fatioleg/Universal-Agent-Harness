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

## AD-011 — v0.4.0 scope: SDD archetype + knowledge-digestion pipeline

- Status: accepted
- Date: 2026-08-29
- Decision: extend v0.3.0 with two new archetypes that capture the
  practitioner patterns the user explicitly relies on:
  (1) `full-sdd-project` for projects needing the full Spec-Driven
  Development lifecycle (Project Charter → Requirements → Architecture →
  Validation → Deliverable), named subagent roles, persistent memory,
  structured handoffs, gates, and a completion checklist; and
  (2) `knowledge-digestion` for projects whose primary capability is
  ingesting a corpus through the canonical five-stage pipeline
  caveman → MarkItDown → Graphify → Obsidian → optional NotebookLM.
  Both ship as opt-in archetypes (not H1 packages), accompanied by
  dedicated docs (`docs/sdd.md`, `docs/knowledge-digestion.md`) and
  five new tool contracts. No implementations ship with the
  contracts (AD-010 honored).
- Reason: v0.3.0 deliberately excluded SDD and the digestion pipeline as
  defaults. The user works with both as a routine part of complex
  projects, so the harness must offer them as first-class reference
  patterns rather than forcing each project to reinvent them. AD-011
  records the promotion to the v0.4.0 catalog while preserving the
  "simplest sufficient harness" principle: every archetype, doc, and
  contract is opt-in.

## AD-012 — v0.5.0 scope: TDD discipline, brownfield safety, ADR format

- Status: accepted
- Date: 2026-08-29
- Decision: extend v0.4.0 with three practice-area docs grounded in
  established primary sources, plus the schemas and templates that
  make them executable in projects:
  (1) `docs/tdd.md` codifies TDD red-green-refactor (Kent Beck /
  Fowler), the practical test pyramid (Ham Vocke on Martin Fowler's
  site), the Agent Testing Pyramid (LangWatch), mutation testing
  and approved scenarios (Böckeler), and characterization tests
  (Feathers). Each technique is framed with explicit "when to apply"
  and "when not to apply".
  (2) `docs/brownfield.md` codifies Michael Feathers' Legacy Code
  Change Algorithm — identify change points → find seams → break
  dependencies → write characterization tests → change → refactor —
  with Sprout, Wrap, and seam techniques. Includes agent-specific
  cautions grounded in Hashimoto's adoption story.
  (3) `docs/adr-template.md` codifies the canonical ADR format
  (Context, Decision, Alternatives, Consequences) per AWS,
  Microsoft Azure Well-Architected Framework, and adr.github.io,
  with a worked example.
  The `software-development` archetype gains a recommended mutation-
  testing sensor (per Böckeler — coverage alone is insufficient).
  The `full-sdd-project` archetype gains cross-references to the
  new docs and to three new project templates (`acceptance-criteria`,
  `test-cases`, `task-plan`).
  Three new extension schemas formalize REQ→AC→Test→Impl traceability:
  `acceptance-criterion.schema.json`, `test-case.schema.json`,
  `change-request.schema.json`.
  One new principle (`10-proportional-design.md`) records the
  smallest-sufficient-architecture rule.
  No implementations ship. Schemas and templates only. AD-010
  honored.
- Reason: v0.4.0 added the SDD archetype and the knowledge-digestion
  pipeline but did not formalize the test discipline or the
  brownfield protocol that practitioners rely on. Cross-source
  audit (Kent Beck via Fowler, Fowler / Ham Vocke Practical Test
  Pyramid, Feathers Working Effectively with Legacy Code, LangWatch
  Agent Testing Pyramid, Böckeler sensors article, AWS / Microsoft /
  adr.github.io for ADRs) confirms that each piece has primary or
  mainstream-industry support. AD-012 records the v0.5.0 scope and
  the explicit citation of primary sources in `docs/references.md`.

## AD-013 — GitHub distribution model

- Status: accepted
- Date: 2026-08-29
- Decision: publish as a versioned upstream harness repository. New projects pin
  a tag/commit or release checksum and materialize only their resolved harness.
- Rejected: using GitHub “Use this template” as the primary mechanism, because
  copying the full tree causes template drift.

## AD-014 — v0.6.0: UAH-lite compiles policy into the runtime

- Status: accepted
- Date: 2026-10-11
- Context: the 2026-10-11 integration report and feasibility audit found that the
  repository had ~46k words of Markdown and 255 lines of code; H0–H3 merge,
  permissions, and evals depended on LLM interpretation. OMC 5.4 already provides
  interview, planning with approval boundary, capability lock, durable goal
  ledger, checkpoints, and worktree teams.
- Decision: implement only the residual responsibility of UAH as a small skill
  (`skills/uah-init`): a deterministic fail-closed resolver whose output is
  Claude Code `permissions` and hooks (the only real enforcement point), a plan
  approval gate bound to the plan hash, and versioned resume state. Integrate
  OMC by artifacts, not command names, and pin it with `omc capabilities lock`.
- Rejected: own policy engine outside the runtime (cannot block tools); own
  interviewer/planner/ledger/scheduler/memory (duplicates OMC/Claude Code);
  ai-memory and parallelism by default (deferred until a pilot shows need).
- Consequences: AD-003's "no automatic resolver" is superseded for the risk/
  permission subset only; archetype classification remains agent-assisted.
  Bash analysis is heuristic and documented as such.

## AD-015 — v0.7.0: integration catalog instead of hard-wired tools

- Status: accepted
- Date: 2026-10-11
- Context: the author maintains reusable Claude Code skills (Workflow_Digestion,
  specboard, CalcBoard) that fit specific stages of the UAH flow. Hard-wiring them
  would make every project carry tools it does not need.
- Decision: describe each tool as a catalog entry (repo, stage, when / when not,
  requirements, trusted rule overlay). A project opts in through
  `project.yaml → integrations`; installation is detected, never assumed, and kept
  out of the policy hash. Enabling or installing requires human confirmation.
- Rejected: a plugin marketplace or automatic installation (report §7); copying
  the tools into this repository (drift).
- Consequences: AT-05 is enforced at the integration level (declared ≠ installed ≠
  enabled); new tools are added by writing one JSON file plus tests.
