# Archetype: scientific-research

## When to use

- Primary deliverable is empirical or experimental.
- The project produces hypotheses, methods, results, and a discussion.
- Evidence burden is scientific or higher.
- The output is or will be peer-reviewed.

## Inherits from

- `core/` (universal invariants, schemas, evals)
- `bootstrap/` workflow

## Differs from base by

- **Knowledge strategy**: hybrid (lexical + semantic; graph only if
  recurring relational queries are demonstrated).
- **Default sensors**: EVAL-001, EVAL-003, EVAL-004, EVAL-005.
- **Permission defaults**: write to `evidence/`, `state/`,
  `decisions/`, `runs/`; read everywhere; execute declared
  computational tools; network read for literature.
- **Required scaffolds**: `evidence/`, `sources/manifest.jsonl`,
  `decisions/`, `state/`.

## Required sensors (from evals/catalog.md)

- EVAL-001 literature retrieval
- EVAL-003 structured extraction
- EVAL-004 numerical audit
- EVAL-005 citation verification

## Typical tool profile

- DOI resolver (Crossref)
- Reference manager (BibTeX or JSONL)
- Computational sensors per sub-discipline (RDKit, scipy, etc.)
- Statistical sensors for hypothesis testing
- Independent reviewer agent (topology Level B default)

## Evidence & provenance requirements

- Every material claim has a `CLAIM-NNNN` entry in the evidence
  ledger.
- Every numerical claim has a computational sensor trace.
- Every citation resolves via Crossref.
- Every transformation (raw → derived) is recorded in
  `provenance/`.

## Agent topology default

Level B (single agent plus independent reviewer). The reviewer
checks the producer's claims and citations against the evidence
ledger; the reviewer does not modify the producer's artifact.

## Autonomy defaults

- Read literature: L2 (sensor decides).
- Add a claim to the ledger: L1 (human approves inclusion).
- Modify a citation: L1.
- Run a computational sensor: L4.
- Change a hypothesis: L0.
- Submit for peer review: L0.

## Open questions / not-yet-defined

- How to handle claims that are partly computational and partly
  inferential (mixed-evidence cases).
- How to weight conflicting sources when neither is dominant.
- Whether to require a registered ORCID per author.

## Example instantiation

A 6-month study of plant oxidative signalling mapping SOD and CAT
with a downstream modelling plan. Topology stays at B; an
independent reviewer checks every claim against the ledger before
the modelling plan is generated.