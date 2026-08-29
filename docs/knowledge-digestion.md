# Knowledge Digestion

This document describes the canonical five-stage knowledge
digestion pipeline supported by the `knowledge-digestion`
archetype: **caveman → MarkItDown → Graphify → Obsidian →
optional NotebookLM**.

Each stage is **opt-in**. Nothing here is mandatory for a
project that does not ingest a non-trivial corpus. Stages can be
skipped, replaced, or reordered when justified, but the canonical
order below is the default because each stage depends on the
previous.

## The five stages

| Stage | Tool | Role | Stage type |
|---|---|---|---|
| 1 | **Caveman** | Context compression of retrieved snippets | Compress |
| 2 | **Microsoft MarkItDown** | Normalize source files to canonical Markdown | Digest (normalize) |
| 3 | **Graphify** | Build selective knowledge graph with evidence pointers | Digest (structure) |
| 4 | **Obsidian** | Human-facing knowledge interface | Present |
| 5 | **NotebookLM (MCP)** | External analysis and synthesis | Present (optional) |

## Stage 1 — Caveman: compress, do not digest

Caveman's role is **context compression**, not knowledge
digestion. The canonical pipeline:

```
Task context = Compress(Retrieve(Knowledge, Task))
```

**Not**:

```
Knowledge base = Compress(Entire corpus)
```

Without this rule, caveman destroys information at scale. The
compression is applied to the **retrieved slice** the current task
needs, not to the whole corpus.

When to use caveman:

- The retrieved slice is larger than the task's context budget.
- The task tolerates lossy compaction (most synthesis tasks do).
- The model would otherwise run out of context.

When **not** to use caveman:

- The corpus is small enough to fit directly.
- The task requires exact quotes or exact numerical fidelity
  (use retrieval + raw inclusion instead).

## Stage 2 — MarkItDown: normalize for agents

Microsoft MarkItDown converts PDF, DOCX, PPTX, XLSX, HTML, and
image files into agent-legible Markdown.

The conversion is **normalization**, not replacement. The
original file is never overwritten. The canonical layout:

```
source/
  paper.pdf               ← immutable, original
canonical/
  paper.md                ← derived (MarkItDown output)
metadata/
  paper.yaml              ← derived metadata
provenance/
  paper.provenance.json   ← transformation record
```

For each canonical file:

- `source/...` is the original.
- `canonical/...` is the agent-legible Markdown.
- `metadata/...` carries structured fields (title, authors, date,
  DOI, identifiers).
- `provenance/...` records the transformation tool, version,
  inputs, outputs, and any warnings.

When to use MarkItDown:

- The source file is in a format agents cannot read directly.
- The corpus is large enough to justify a canonical store.
- Retrieval over the corpus is anticipated.

When **not** to use MarkItDown:

- The source is already Markdown or text.
- The corpus is small and one-off.

## Stage 3 — Graphify: structure selectively

Graphify builds a knowledge graph. The graph is an
**interpretation**, not knowledge itself.

Useful relations:

- molecule → protein
- compound → pathway
- paper → claim
- method → result
- project → researcher
- entity → evidence

The graph is **selective**. Build edges only for relations that
recur; do not auto-graph every sentence.

**Every scientific edge carries a source pointer**:

```
EDGE: Compound X --modulates--> SOD1
SOURCE: paper_023
LOCATION: page 7
EVIDENCE: experimental
CONFIDENCE: high
VALIDATION: computational-check
```

Rule: `NO_SCIENTIFIC_EDGE_WITHOUT_EVIDENCE_POINTER`. A relation
without provenance is indistinguishable from a hallucination.

When to use Graphify:

- Relational questions recur (molecule → target, paper →
  claim, etc.).
- Evidence-ledger linkage is in use.

When **not** to use Graphify:

- The corpus is small and homogeneous.
- No relational queries are anticipated.

## Stage 4 — Obsidian: human interface

Obsidian is a **viewer** over the canonical store, not the
backend epistemological layer.

```
       HUMAN
         ↕
     OBSIDIAN
         ↕
  KNOWLEDGE PLANE   ← canonical + Graphify output
         ↕
       AGENTS
```

The Obsidian vault reads from `canonical/`. Edits made in
Obsidian should be exported back to `canonical/` with
provenance, or they will be lost when the vault is rebuilt.

When to use Obsidian:

- A human wants a navigable interface over the corpus.
- The project benefits from bidirectional links between
  documents.

When **not** to use Obsidian:

- The project has no human explorer.
- The corpus is fully machine-driven.

## Stage 5 — NotebookLM (MCP): external analysis, optional

NotebookLM via MCP is an **external analysis surface** for
synthesis questions, summaries, and Q&A over the corpus. It is
**not** the system of record.

Important findings must be exported back to the workspace with
provenance:

- notebooklm-output/2026-08-29-summary.md (the synthesized text)
- metadata/2026-08-29-summary.yaml (source-pointer, query, model)
- provenance/2026-08-29-summary.json (transformation record)

Default policy: **ephemeral NotebookLM sessions**. Disable
persistence in NotebookLM if available. The workspace is the
durable layer.

When to use NotebookLM:

- Synthesis over a large corpus benefits from a dedicated
  long-context model.
- The user explicitly opts in.

When **not** to use NotebookLM:

- The corpus is fully internal or sensitive.
- Privacy or data-leakage risk is unacceptable.

## Why these five specifically

Each stage answers a distinct question:

- **MarkItDown** — "How does the agent read a PDF?"
- **Caveman** — "How does the agent fit a 10k-token slice into a
  4k context?"
- **Graphify** — "How does the agent answer 'what compounds
  modulate target X'?"
- **Obsidian** — "How does a human browse the corpus?"
- **NotebookLM** — "How does a long-context model help with
  synthesis?"

Drop any stage whose question is irrelevant.

## What is not in this pipeline

- Vector databases — orthogonal. A project may add a vector
  index over `canonical/` without changing this pipeline.
- Full-text search — orthogonal. Add `grep` or BM25 on top.
- Auto-summarization of every document — not recommended. The
  compression step happens at retrieval time, not ingestion
  time.

## Cross-references

- `archetypes/knowledge-digestion.md` — the archetype that
  bundles this pipeline.
- `contracts/tools/caveman-compress.yaml`
- `contracts/tools/markitdown-normalize.yaml`
- `contracts/tools/graphify-build.yaml`
- `contracts/tools/obsidian-interface.yaml`
- `contracts/tools/notebooklm-explore.yaml`
- `core/schemas/extension/evidence-ledger.schema.json` — for
  graph edges.
- `core/principles/01-preserve-sources.md` — source immutability.
- `core/principles/02-maintain-provenance.md` — provenance
  obligation.