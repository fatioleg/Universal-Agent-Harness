# Universal Eval Catalog

Ten universal eval categories that any harness can run to verify it
still performs across representative cases. This is the menu.
`evals/bootstrap-cases.yaml` is the specific test set used to
validate this Universal Harness repository itself.

## Relationship to validation, QA, and eval

- Validation checks one execution against an oracle.
- QA checks one artifact against its requirements.
- Eval checks the harness across a representative suite.

Eval answers: "Does this harness still perform?"

## The 10 categories

### EVAL-001 — literature retrieval

- **Purpose**: verify that source discovery returns relevant sources
  with correct bibliographic metadata.
- **Input fixture**: a known topic with a known set of canonical
  sources.
- **Expected behavior**: recall ≥ 0.9 on canonical sources; all DOIs
  resolve via Crossref.
- **Metrics**: recall, DOI resolution rate, false-positive rate.

### EVAL-002 — document ingestion

- **Purpose**: verify that source files are normalized into
  agent-legible Markdown or structured form without losing content.
- **Input fixture**: a known document with known structure (PDF,
  DOCX, PPTX, XLSX, HTML, image).
- **Expected behavior**: every section heading in the source has a
  counterpart in the normalized form; tables, figures, and
  references are preserved.
- **Metrics**: section coverage, table preservation rate, figure
  reference preservation.

### EVAL-003 — structured extraction

- **Purpose**: verify that the harness extracts structured fields
  from unstructured sources accurately.
- **Input fixture**: a document with known structured fields
  (entities, claims, methods, results).
- **Expected behavior**: F1 ≥ 0.85 against the gold standard.
- **Metrics**: precision, recall, F1, hallucinated-field rate.

### EVAL-004 — numerical audit

- **Purpose**: verify that any numerical claim in the output traces
  to a computational sensor and matches the source computation
  within tolerance.
- **Input fixture**: a document with known numerical claims.
- **Expected behavior**: every numerical claim has a sensor trace;
  re-computation reproduces the source within ±1% (or declared
  tolerance).
- **Metrics**: coverage of computational sensors, reproduction rate.

### EVAL-005 — citation verification

- **Purpose**: verify that every citation resolves to a real source
  and that the cited claim is supported by the cited location.
- **Input fixture**: a bibliography with known valid and invalid
  entries.
- **Expected behavior**: 100% valid DOI resolution; 100% claim-
  location consistency.
- **Metrics**: resolution rate, false-citation rate, claim
  drift rate.

### EVAL-006 — artifact generation

- **Purpose**: verify that a deliverable artifact (report, dataset,
  code package, model card) satisfies its acceptance criteria.
- **Input fixture**: a deliverable spec with acceptance criteria.
- **Expected behavior**: every acceptance criterion passes; no
  extra-material changes.
- **Metrics**: criterion pass rate, side-effect rate.

### EVAL-007 — handoff/restart

- **Purpose**: verify that a new agent session can resume work
  from the project's state and evidence files alone.
- **Input fixture**: a project at a known state with a known next
  action.
- **Expected behavior**: the next session reads state, produces a
  plan consistent with the recorded next action, and continues.
- **Metrics**: plan fidelity, reproducibility, time-to-resume.

### EVAL-008 — agent coordination

- **Purpose**: verify that a multi-agent topology (Level C/D/E)
  coordinates without dropping or duplicating tasks.
- **Input fixture**: a task DAG with known dependencies.
- **Expected behavior**: every task is assigned exactly once;
  every dependency is honored; the final artifact is a union of
  the parts.
- **Metrics**: assignment rate, dependency-respecting rate, lost-
  update rate.

### EVAL-009 — conflicting-source resolution

- **Purpose**: verify that the harness reconciles conflicting
  sources by recording both, distinguishing them, and resolving
  with explicit rationale.
- **Input fixture**: a topic with two known contradictory sources.
- **Expected behavior**: both sources are recorded; the conflict is
  flagged; a resolution is recorded in `decisions.schema.json` or
  the output.
- **Metrics**: source coverage, conflict detection rate, resolution
  explicitness.

### EVAL-010 — failure recovery

- **Purpose**: verify that a controlled failure is recorded, the
  repair path executes, and the harness resumes from the rollback
  point.
- **Input fixture**: a synthetic failure injected at a known point.
- **Expected behavior**: failure-registry entry created; repair
  attempt succeeds within retry budget; observability-run shows
  the failure and the recovery.
- **Metrics**: time-to-detect, time-to-repair, recovery success
  rate, regression-sensor coverage.

## How archetypes select subsets

Each archetype stub in `archetypes/` lists which subset of these
evals applies by default. A project's `harness.lock.yaml` records
the selected subset.

## Source references

- OpenAI — Harness engineering (representative eval suite).
- Anthropic — Harness design for long-running apps (independent
  evaluator, hard thresholds, regression cases).
- Birgitta Böckeler — Sensors for coding agents (sensors-cli
  trend tracking).