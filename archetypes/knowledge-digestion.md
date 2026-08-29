# Archetype: knowledge-digestion

## When to use

- The project ingests a non-trivial corpus of PDFs, DOCX, PPTX,
  XLSX, HTML, or images that must become agent-legible Markdown.
- The project benefits from retrieval over the corpus (lexical,
  semantic, or graph).
- The user prefers Obsidian as the human-facing knowledge
  interface.
- Optional: NotebookLM (via MCP) is acceptable as an external
  analysis surface.

This archetype documents the canonical five-stage pipeline
`caveman → MarkItDown → Graphify → Obsidian → optional NotebookLM`
**as a capability bundle selectable by the project**. Each tool
is opt-in; nothing here is mandatory.

## Inherits from

- `core/`
- `bootstrap/`
- Capability `knowledge-digestion-pipeline` from
  `core/universal.yaml`

## Differs from base by

- **Knowledge strategy**: lexical + semantic; graph selectively.
- **Default sensors**: EVAL-002 (ingestion), EVAL-009 (conflicting
  sources).
- **Permission defaults**: read source dir, write derived dirs,
  network read for NotebookLM only.
- **Required scaffolds**: `source/`, `canonical/`, `derived/`,
  `metadata/`, `provenance/`, optional `vault/`.

## The five tools and their roles

| Stage | Tool | Role | Stage type |
|---|---|---|---|
| 1 | **Caveman** | Context compression of retrieved snippets | Compress (not Digest) |
| 2 | **Microsoft MarkItDown** | Normalize source files to canonical Markdown | Digest (normalize) |
| 3 | **Graphify** | Build selective knowledge graph with evidence pointers | Digest (structure) |
| 4 | **Obsidian** | Human-facing knowledge interface | Present |
| 5 | **NotebookLM (MCP)** | External analysis and synthesis | Present (optional) |

## Strict ordering and the rule of separation

**Sources are immutable.** MarkItDown produces **derived**
representations. The original file is never overwritten.

```
source/
  paper.pdf               ← immutable
canonical/
  paper.md                ← derived (MarkItDown output)
metadata/
  paper.yaml              ← derived metadata
provenance/
  paper.provenance.json   ← transformation record
```

MarkItDown is **normalization**, not replacement. The Markdown
is an agent-legible representation; the PDF remains the
authoritative source for citations.

## Retrieval before compression (caveman)

Caveman is **not** used to compress the entire corpus. The
canonical pipeline:

```
Task context = Compress(Retrieve(Knowledge, Task))
```

NOT:

```
Knowledge base = Compress(All corpus)
```

Caveman's role is to compact **retrieved** snippets for the
task's context window, not to compress the whole knowledge base.
Without this rule, caveman destroys information at scale.

## Selective graph (Graphify)

Graphify is useful for relations that recur:

- molecule → protein
- compound → pathway
- paper → claim
- method → result
- entity → evidence

Graphs are **interpretations**, not knowledge. Every edge in a
scientific graph must carry a `SOURCE` pointer to the underlying
claim in the evidence ledger.

```
EDGE: Compound X --modulates--> SOD1
SOURCE: paper_023
LOCATION: page 7
EVIDENCE: experimental
CONFIDENCE: high
VALIDATION: computational-check
```

`NO_SCIENTIFIC_EDGE_WITHOUT_EVIDENCE_POINTER` is the rule.

## Obsidian as human interface

Obsidian is the **human knowledge interface**, not the backend
epistemological layer. The architecture:

```
       HUMAN
         ↕
     OBSIDIAN
         ↕
  KNOWLEDGE PLANE  ← canonical MarkItDown + Graphify output
         ↕
       AGENTS
```

The vault is a **view** over the canonical store. The canonical
store remains the system of record. Edits made in Obsidian
should be exported back to the canonical store with provenance,
or they will be lost when the vault is rebuilt.

## NotebookLM as external analysis

NotebookLM (via MCP) is acceptable as an **external analysis
surface** for synthesis questions, summaries, and Q&A over
the corpus. It is **not** the system of record. Important
findings must be exported back to the workspace with
provenance.

If the project does not need NotebookLM, omit it. The pipeline
is complete without step 5.

## Required sensors

- EVAL-002 document ingestion
- EVAL-009 conflicting-source resolution
- EVAL-001 literature retrieval (if corpus is publication-shaped)

## Typical tool profile

- Microsoft MarkItDown (PDF, DOCX, PPTX, XLSX, HTML, image →
  Markdown)
- Caveman (context compression library)
- Graphify (knowledge graph builder)
- Obsidian (vault viewer)
- NotebookLM MCP server (optional)

Tool contracts for each live in `contracts/tools/`:

- `markitdown-normalize.yaml`
- `caveman-compress.yaml`
- `graphify-build.yaml`
- `obsidian-interface.yaml`
- `notebooklm-explore.yaml`

All `eval_status: untested` per AD-010.

## Evidence & provenance requirements

- Every canonical file has a `source/` twin and a
  `provenance/` record.
- Every graph edge has a claim pointer.
- Every NotebookLM finding worth keeping returns to the
  workspace with provenance.

## Agent topology default

Level A. Tools suffice; an orchestrator may supervise if the
corpus is large. Escalate to B (independent reviewer) when
graph edges drive material decisions.

## Autonomy defaults

- Normalize a single source: L4.
- Build a graph edge: L2 (with provenance captured).
- Mark a source as superseded: L1.
- Delete a source: L0.
- Edit Obsidian vault manually: human only (the vault is the
  human interface).

## Open questions / not-yet-defined

- How to handle OCR quality issues in scanned PDFs that
  MarkItDown misreads.
- When to require a second human reviewer for graph edges in
  regulated domains.
- Whether Graphify should be re-run on every ingestion or only
  on the subset that triggers relational questions.
- Whether NotebookLM persistence should be enabled at all
  (default policy: ephemeral sessions only).

## Example instantiation

A 200-document regulatory corpus ingested once. Each PDF
becomes a canonical Markdown file. A small graph records
which regulations cite which earlier regulations. Obsidian
vault indexes the Markdown for human exploration. NotebookLM
is **not** enabled because the corpus is fully internal.

## Related archetypes

- `literature-review` — narrower, focused on published literature
  with citation verification.
- `knowledge-base` — narrower, long-running curation without
  the full ingestion pipeline.
- `scientific-research` — narrower, evidence-ledger heavy.

`knowledge-digestion` is the right choice when the **ingestion
pipeline itself** is the primary capability, not the eventual
analysis.