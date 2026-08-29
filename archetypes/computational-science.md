# Archetype: computational-science

## When to use

- Primary deliverable is a simulation, a numerical analysis, or a
  reproducible pipeline.
- Bit-exact or near-bit-exact reproduction is required.
- The project combines code, data, and runtime configuration.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: lexical only by default (code, data,
  config). Graph or semantic only if a relational question recurs.
- **Default sensors**: EVAL-002 (ingestion), EVAL-004 (numerical
  audit), EVAL-007 (handoff/restart).
- **Permission defaults**: read/write inside project; execute
  declared computational tools; network optional and task-justified.
- **Required scaffolds**: `runs/`, `data/`, `code/`, `config/`,
  `state/`.

## Required sensors

- EVAL-002 document ingestion (data dictionary, config schema)
- EVAL-004 numerical audit (deterministic recomputation)
- EVAL-007 handoff/restart (rerun reproducibility)

## Typical tool profile

- Deterministic scripting (Python, R, Julia, Fortran, etc.)
- Container or venv manifest
- Version-pinned dependencies
- Reproducibility manifest (`reproducibility.yaml`)

## Evidence & provenance requirements

- Every input dataset has a hash.
- Every run has a manifest (code version, data hash, parameters,
  outputs hash).
- Outputs that drive downstream claims pass EVAL-004.

## Agent topology default

Level A. Tools and computational sensors are sufficient. Escalate to
B only when a result drives a material scientific claim.

## Autonomy defaults

- Run a sensor: L4.
- Re-run a pipeline: L2.
- Modify input data: L1.
- Publish outputs: L0.

## Open questions / not-yet-defined

- Whether to require formal verification for any step.
- How to handle stochastic simulations (tolerance declarations).

## Example instantiation

A 6-hour molecular dynamics run repeated at three temperatures
with deterministic seeds. The harness records every run manifest;
EVAL-007 verifies the rerun reproduces within declared tolerance.