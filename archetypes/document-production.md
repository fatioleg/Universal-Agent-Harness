# Archetype: document-production

## When to use

- Primary deliverable is a structured document (report, white paper,
  briefing).
- Templates and formatting validators drive quality.
- Review cycles are explicit.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: lexical.
- **Default sensors**: template conformance, citation verification,
  formatting validator.
- **Permission defaults**: read; write to `drafts/`, `state/`.
- **Required scaffolds**: `templates/`, `drafts/`, `state/`.

## Required sensors

- Template conformance check
- EVAL-005 citation verification (if the document cites sources)
- EVAL-006 artifact generation

## Typical tool profile

- Document compiler (Pandoc, LaTeX, docx)
- Template validator
- Citation resolver

## Evidence & provenance requirements

- Every fact in the document has a source pointer (if evidence
  burden is non-trivial).
- Every review cycle has a record.

## Agent topology default

Level A. Tools suffice; reviewer for material drafts.

## Autonomy defaults

- Apply template: L4.
- Reformat: L4.
- Update draft: L2.
- Change a claim: L1.
- Publish: L0.

## Open questions / not-yet-defined

- How to handle documents with mixed citation styles.

## Example instantiation

A monthly briefing memo with a fixed template. The harness
applies the template, validates citations, runs formatting
checks, and produces a draft ready for human review.