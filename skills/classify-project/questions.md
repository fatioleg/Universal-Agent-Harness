# Classification Questions

Fifteen questions in five groups. Ask one at a time. Skip questions
whose branch logic says to skip.

## Group 1 — Deliverable, source, duration (drives archetype)

### Q1 — Primary deliverable type

- (a) Written document (paper, report, proposal)
- (b) Code or deployable artifact
- (c) Curated knowledge base
- (d) Analysis result (numbers, plots, tables)

### Q2 — Source of truth

- (a) Published literature
- (b) Empirical observations or experiments
- (c) Existing dataset
- (d) Code repository
- (e) Combination of the above

### Q3 — Project duration

- (a) One-off (single deliverable)
- (b) Short (weeks)
- (c) Long-running (months or more, restartable)

## Group 2 — Evidence, reproducibility, risk (drives sensor selection)

### Q4 — Evidence burden

- (a) None (no scientific claims)
- (b) Standard (factual claims with citations)
- (c) Scientific (claims tied to methods, results)
- (d) Regulated (life, safety, regulatory)

### Q5 — Reproducibility requirement

- (a) Approximate reproduction is acceptable
- (b) Reproducible in principle
- (c) Bit-exact or near-bit-exact

### Q6 — Material risk

- (a) Low (internal, illustrative)
- (b) Medium (peer review, public)
- (c) High (regulatory, clinical, financial)
- (d) Critical (life, safety, large budget)

## Group 3 — Knowledge, retrieval, graph (drives knowledge plane)

### Q7 — Knowledge scale

- (a) Few sources (under 10)
- (b) Tens of sources (10–100)
- (c) Hundreds of sources (100+)

### Q8 — Retrieval need demonstrated?

- (a) Lexical (grep, BM25) is enough
- (b) Semantic (embedding) is required
- (c) Both are required

### Q9 — Relational queries recurred?

- (a) No
- (b) Yes (molecule → target, paper → claim, etc.)

If Q9 = No, skip graph. If Yes, Q9b records the recurring query.

## Group 4 — Coordination, parallelism, autonomy (drives topology)

### Q10 — Coordination need

- (a) One agent is enough
- (b) An independent reviewer is needed
- (c) One specialist or context boundary is distinct
- (d) Multiple specialties with independent verification

### Q11 — Genuine parallelism?

- (a) No (sequential is fine)
- (b) Yes (subtasks are independent and parallelizable)

### Q12 — Autonomy tolerance

- (a) Low (every material action needs human approval)
- (b) Medium (computational sensors can approve mechanical actions)
- (c) High (autonomous bounded workflow is acceptable)

## Group 5 — External actions, gates, observability (drives permissions + assurance)

### Q13 — External actions required?

- (a) None (project is self-contained)
- (b) Read-only external (literature search, public APIs)
- (c) Write external (publish, send, spend)

### Q14 — Human-gate frequency expected

- (a) Continuous (every material decision)
- (b) At decision points (start, mid, end, on blockers)
- (c) Minimal (only on irreversible actions)

### Q15 — Observability need

- (a) Minimal (one final summary is enough)
- (b) Per-task records (every task has a run record)
- (c) Per-decision records (every decision is logged)