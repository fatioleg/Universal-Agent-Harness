# Archetype: knowledge-base

## When to use

- The project is a long-running curation effort.
- Sources are added and revised continuously.
- Dedup and conflict resolution are first-class concerns.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: hybrid (lexical + semantic). Graph when
  relational queries recur.
- **Default sensors**: EVAL-002, EVAL-009.
- **Permission defaults**: read/write inside `evidence/`,
  `sources/`, `state/`.
- **Required scaffolds**: `sources/manifest.jsonl`, `evidence/`,
  `decisions/`, `state/`.

## Required sensors

- EVAL-002 document ingestion
- EVAL-009 conflicting-source resolution

## Typical tool profile

- Source manifest manager
- Dedup detector (DOI or fuzzy match)
- Conflict resolver (computational + reviewer)

## Evidence & provenance requirements

- Every source has a version history.
- Every conflict resolution is in `decisions/`.
- Every derived summary points back to its source claims.

## Agent topology default

Level A. The curator workflow is straightforward; tools suffice.

## Autonomy defaults

- Ingest a new source: L2.
- Resolve a duplicate: L1.
- Mark a source as superseded: L1.
- Delete a source: L0.

## Open questions / not-yet-defined

- When to require human review for conflict resolution.
- How to handle retraction cascades.

## Example instantiation

A multi-year curation of regulatory guidance documents across
jurisdictions. The harness ingests new releases, detects
superseded versions, and surfaces conflicts for reviewer review.