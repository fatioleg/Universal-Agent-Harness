# Archetype: grant-project-proposal

## When to use

- Primary deliverable is a proposal to a funder.
- Funder templates and rules drive structure.
- Deadlines are explicit.
- Budgets must compute correctly.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: lexical (funder guidelines, prior
  proposals).
- **Default sensors**: template conformance, budget validator,
  citation verification.
- **Permission defaults**: read; write to `drafts/`, `state/`,
  `budgets/`.
- **Required scaffolds**: funder template, `budgets/`,
  `compliance/`, `state/`.

## Required sensors

- Template conformance (funder-specific)
- Budget validator (sums, categories, caps)
- EVAL-005 citation verification (if citing prior work)
- Deadline sensor (with countdown)

## Typical tool profile

- Funder template parser
- Budget spreadsheet validator
- Deadline tracker

## Evidence & provenance requirements

- Every claim about feasibility has a backing study or pilot.
- Every budget item has a category and a justification.
- Every compliance check has a record.

## Agent topology default

Level B. Independent reviewer checks feasibility claims and budget
consistency.

## Autonomy defaults

- Apply template: L4.
- Update draft: L2.
- Change a budget item: L1.
- Change a feasibility claim: L0.
- Submit: L0.

## Open questions / not-yet-defined

- How to handle funder-specific formatting edge cases.

## Example instantiation

A 12-page research proposal to a national funding agency with a
fixed budget cap. The harness enforces the template, validates
the budget, checks citations, and surfaces feasibility claims for
reviewer review.