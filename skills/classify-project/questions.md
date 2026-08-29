# Classification Questions

Twenty-four questions in six groups. Ask one at a time. Skip
questions whose branch logic says to skip based on prior
answers.

## Group 1 — Project complexity and shape (drives archetype + proportional design)

### Q1 — Project complexity

Classify the project on a scale from trivial to critical. This
follows `core/principles/10-proportional-design.md` and
determines which archetypes, schemas, and capabilities are
even on the table.

- (a) **trivial** — single deliverable, no integration, no
  external action, no reproducibility requirement.
- (b) **small** — short timeline, one domain, one or two
  deliverables.
- (c) **medium** — multi-week, multi-deliverable, possibly
  multi-domain.
- (d) **large** — multi-month, multi-agent justified, evidence
  burden material.
- (e) **complex / critical** — life, safety, regulatory,
  clinical, large budget.

If Q1 = a or b, skip Q19 (SDD workflow only makes sense for
medium+). If Q1 = a, the recommended archetype is H0 only with
project-specific overrides.

### Q2 — Primary deliverable type

- (a) Written document (paper, report, proposal)
- (b) Code or deployable artifact
- (c) Curated knowledge base
- (d) Analysis result (numbers, plots, tables)
- (e) Combination of deliverable types

### Q3 — Source of truth

- (a) Published literature
- (b) Empirical observations or experiments
- (c) Existing dataset
- (d) Code repository
- (e) Combination of the above

### Q4 — Project duration

- (a) One-off (single deliverable)
- (b) Short (weeks)
- (c) Long-running (months or more, restartable)

## Group 2 — Evidence, reproducibility, risk (drives sensor selection + risk floor)

### Q5 — Evidence burden

- (a) None (no scientific claims)
- (b) Standard (factual claims with citations)
- (c) Scientific (claims tied to methods, results)
- (d) Regulated (life, safety, regulatory)

### Q6 — Reproducibility requirement

- (a) Approximate reproduction is acceptable
- (b) Reproducible in principle
- (c) Bit-exact or near-bit-exact

### Q7 — Material risk

- (a) Low (internal, illustrative)
- (b) Medium (peer review, public)
- (c) High (regulatory, clinical, financial)
- (d) Critical (life, safety, large budget)

## Group 3 — Knowledge, retrieval, graph, ingestion pipeline (drives knowledge plane)

### Q8 — Knowledge scale

- (a) Few sources (under 10)
- (b) Tens of sources (10–100)
- (c) Hundreds of sources (100+)
- (d) Thousands or more

### Q9 — Retrieval need demonstrated?

- (a) Lexical (grep, BM25) is enough
- (b) Semantic (embedding) is required
- (c) Both are required

### Q10 — Relational queries recurred?

- (a) No
- (b) Yes (molecule → target, paper → claim, etc.)

If Q10 = No, skip graph tooling. If Yes, Q10b records the
recurring query type.

### Q11 — Ingestion pipeline needed?

Which stages of the canonical pipeline
`caveman → MarkItDown → Graphify → Obsidian → NotebookLM`
apply? **Multi-select** (any combination):

- (a) **MarkItDown normalization** — converting PDF/DOCX/PPTX/
  XLSX/HTML/image to canonical Markdown.
- (b) **Caveman compression** — compacting retrieved slices
  for context-budget tasks.
- (c) **Graphify knowledge graph** — building relations
  between entities with evidence pointers.
- (d) **Obsidian vault** — human-facing knowledge interface.
- (e) **NotebookLM external analysis** — long-context
  synthesis via MCP. Requires explicit opt-in.
- (f) **None** — project does not need corpus ingestion.

If Q11 = f, skip the digestion pipeline. If Q11 includes c,
the `graphify-build` and `knowledge-digestion-pipeline`
capabilities are activated.

## Group 4 — Coordination, parallelism, autonomy, state continuity (drives topology + autonomy)

### Q12 — Coordination need

- (a) One agent is enough
- (b) An independent reviewer is needed
- (c) One specialist or context boundary is distinct
- (d) Multiple specialties with independent verification

### Q13 — Genuine parallelism?

- (a) No (sequential is fine)
- (b) Yes (subtasks are independent and parallelizable)

### Q14 — Autonomy tolerance

- (a) Low (every material action needs human approval)
- (b) Medium (computational sensors can approve mechanical
  actions)
- (c) High (autonomous bounded workflow is acceptable)

### Q15 — State continuity, handoff, compaction needed?

- (a) No — single session, no restart
- (b) Yes — multiple sessions, handoffs required, compaction
  between sessions needed
- (c) Yes — multi-agent with structured handoff artifacts
  between roles

If Q15 = a, the `state` schema is instantiated as a
session-only file. If b or c, `state`, `checkpoint-handoff`,
and `observability-run` schemas are instantiated.

## Group 5 — Development discipline: SDD, TDD, brownfield, ADR, change protocol

### Q16 — Brownfield or greenfield?

- (a) **Greenfield** — new project, no existing code to
  integrate with.
- (b) **Brownfield** — modifying or extending an existing
  codebase.
- (c) **Mixed** — new project that must interoperate with
  existing systems.

If Q16 = b or c, the `docs/brownfield.md` protocol applies:
characterization tests before refactors, Legacy Code Change
Algorithm, seams, Sprout / Wrap techniques.

### Q17 — Test strategy

- (a) **TDD red-green-refactor** — discipline of writing
  tests first, then minimal code, then refactor.
- (b) **Characterization tests first** — capture current
  behavior before changing brownfield code.
- (c) **Approval / golden-master** — pre-validated reference
  outputs that runs must match within tolerance.
- (d) **Mutation testing** — Stryker-style, to catch tests
  that exercise code without asserting on it.
- (e) **Mixed** — combine several strategies per task.

Q17 only affects sensor recommendations; any combination is
valid.

### Q18 — SDD workflow scope

When does the project need Spec-Driven Development?

- (a) **None** — write code directly. For trivial and small
  projects (Q1 = a or b).
- (b) **Charter only** — one paragraph capturing objective,
  scope, deliverables.
- (c) **Light SDD** — Project Charter + Requirements with
  acceptance criteria. No full Architecture spec.
- (d) **Full SDD** — Charter + Requirements + Architecture +
  Validation + Deliverable, with REQ→AC→Test→Impl
  traceability.
- (e) **Full SDD + named subagents** — full SDD plus named
  specialist roles (Research, Domain Expert, Data Auditor,
  Implementation, QA, Red-Team).

If Q18 = d or e, the `archetypes/full-sdd-project.md` archetype
applies. The REQ→AC→Test→Impl schemas
(`acceptance-criterion`, `test-case`, `change-request`) are
instantiated.

### Q19 — ADR / decision log

- (a) None — informal notes suffice.
- (b) Yes — record significant decisions as ADRs with the
  canonical format (Context / Decision / Alternatives /
  Consequences).
- (c) Yes, plus supersession chain — when a decision is
  replaced, the prior ADR is linked as superseded.

If Q19 = b or c, `docs/adr-template.md` is the template and
ADRs are tracked in `docs/DECISIONS.md`.

### Q20 — Change protocol needed?

- (a) No — requirements are stable; one-shot specification.
- (b) Yes — requirements will change; formal change request
  workflow (CR-NNNN) before modifying specs, criteria, and
  tests.

If Q20 = b, the `change-request.schema.json` schema is
instantiated.

## Group 6 — External actions, gates, observability, recovery (drives permissions + assurance)

### Q21 — External actions required?

- (a) None (project is self-contained)
- (b) Read-only external (literature search, public APIs)
- (c) Write external (publish, send, spend)

### Q22 — Human-gate frequency expected

- (a) Continuous (every material decision)
- (b) At decision points (start, mid, end, on blockers)
- (c) Minimal (only on irreversible actions)

### Q23 — Independent review and Red-Team

- (a) No — producer self-critique suffices.
- (b) Independent reviewer on each material artifact.
- (c) Independent reviewer plus Red-Team adversary at every
  gate.

### Q24 — Observability depth

- (a) Minimal (one final summary is enough)
- (b) Per-task records (every task has a run record)
- (c) Per-decision records (every decision is logged)

## Branching summary

- Q1 = a → skip Q19 (SDD too heavy for trivial).
- Q1 = a → skip Q16 (brownfield irrelevant for trivial
  greenfield).
- Q9 = No → skip Q11 graph stages (c, d, e may still apply
  for non-graph ingestion).
- Q15 = a → skip checkpoint-handoff schema instantiation.
- Q18 = a → skip REQ/AC/TEST schema instantiation.
- Q20 = a → skip change-request schema instantiation.