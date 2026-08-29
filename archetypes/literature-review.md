# Archetype: literature-review

## When to use

- Primary deliverable is a synthesis of published sources.
- Recall matters as much as precision.
- Inclusion and exclusion criteria are explicit.
- The output is a PRISMA-style flow diagram or equivalent.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: hybrid (lexical + semantic). Graph only
  when relational questions recur.
- **Default sensors**: EVAL-001, EVAL-005, EVAL-009.
- **Permission defaults**: read; write to `evidence/`, `state/`,
  `decisions/`. Network allowed for literature retrieval.
- **Required scaffolds**: `sources/manifest.jsonl`, `evidence/`,
  `decisions/`, `state/`.

## Required sensors

- EVAL-001 literature retrieval
- EVAL-005 citation verification
- EVAL-009 conflicting-source resolution

## Typical tool profile

- PubMed / OpenAlex / Crossref
- Reference manager (BibTeX or JSONL)
- PRISMA flow generator
- Independent reviewer (Level B default)

## Evidence & provenance requirements

- Every cited paper has a verified DOI.
- Every inclusion or exclusion decision is in `decisions/`.
- Every synthesis statement maps to one or more claims in the
  evidence ledger.

## Agent topology default

Level B (single agent plus independent reviewer). The reviewer
audits inclusion/exclusion consistency and citation accuracy.

## Autonomy defaults

- Search literature: L3.
- Add a citation: L1.
- Exclude a paper: L1.
- Change the inclusion criteria: L0.
- Submit a manuscript: L0.

## Open questions / not-yet-defined

- How to handle sources behind paywalls.
- How to weight preprints vs peer-reviewed versions.
- How to reconcile conflicting reviews of the same paper.

## Example instantiation

A systematic review of 200 papers on a specific intervention. The
harness runs the search, manages inclusion/exclusion with a
reviewer, generates a PRISMA diagram, and produces a draft
manuscript with citations tied to the evidence ledger.