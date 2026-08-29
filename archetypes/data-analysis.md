# Archetype: data-analysis

## When to use

- Primary deliverable is an analysis result on an existing dataset.
- Statistical assumptions must be declared.
- Reproducibility is via scripts + versioned data.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: lexical (code, data dictionary).
- **Default sensors**: EVAL-002 (dataset schema), EVAL-004
  (numerical audit), EVAL-007 (reproducibility).
- **Permission defaults**: read dataset; write to `derived/`,
  `runs/`, `state/`.
- **Required scaffolds**: `data/`, `code/`, `derived/`, `runs/`,
  `state/`.

## Required sensors

- EVAL-002 dataset schema validation
- EVAL-004 numerical audit
- EVAL-007 handoff/restart

## Typical tool profile

- pandas / polars / duckdb
- Statistical libraries (scipy, statsmodels)
- Visualization (matplotlib, seaborn, plotly)

## Evidence & provenance requirements

- Every input dataset has a hash and a license note.
- Every transformation is a script in `code/`.
- Every result includes a `runs/` manifest.

## Agent topology default

Level A. Tools and computational sensors suffice.

## Autonomy defaults

- Run a script: L4.
- Modify a script: L2.
- Modify input data: L1.
- Publish a result: L0.

## Open questions / not-yet-defined

- How to handle PII or sensitive data.
- When to require IRB approval documentation in the manifest.

## Example instantiation

A 30-day analysis of sales data with weekly reports. The harness
ingests the dataset, validates the schema, runs the analysis,
records each run manifest, and produces weekly reports.