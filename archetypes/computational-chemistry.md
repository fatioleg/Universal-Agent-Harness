# Archetype: computational-chemistry

## When to use

- Subset of computational-science for chemistry-specific work.
- Inputs include SMILES, InChI, MOL/SDF, crystal structures (CIF).
- Domain sensors (RDKit, OpenBabel, RDKit conformers, etc.) are
  available.

## Inherits from

- `core/`
- `bootstrap/`
- computational-science

## Differs from base by

- **Knowledge strategy**: lexical + chemistry graph (molecule →
  target → assay) when relational questions recur.
- **Default sensors**: EVAL-002, EVAL-004, plus chemistry
  validators (SMILES canonicalization, valency, unit consistency).
- **Permission defaults**: read/write inside project; execute
  chemistry tools; network optional.
- **Required scaffolds**: `inputs/molecules/`, `inputs/sources/`,
  `runs/`, `derived/`, `state/`.

## Required sensors

- EVAL-002 (ingestion of MOL/SDF/CIF)
- EVAL-004 (numerical audit, including unit checks)
- Chemistry validators:
  - SMILES canonicalization (RDKit)
  - Valency / aromaticity (RDKit)
  - Unit consistency (mass, volume, concentration)
  - 3D conformer generation (RDKit)
  - Crystal structure validation (pymatgen or equivalent)

## Typical tool profile

- RDKit (SMILES, descriptors, fingerprints)
- OpenBabel (format conversion)
- pymatgen (crystals)
- OpenMM or AMBER (MD, optional)
- scikit-learn / PyTorch (QSAR / property prediction)

## Evidence & provenance requirements

- Every molecule has a canonical SMILES, an InChI, and a source
  pointer.
- Every descriptor has a formula reference.
- Every run has a tool version, parameter set, and output hash.

## Agent topology default

Level C: orchestrator plus one computational-chemistry specialist.
The orchestrator handles general planning; the specialist handles
chemistry-specific work.

## Autonomy defaults

- Canonicalize a SMILES: L4 (deterministic sensor).
- Generate descriptors: L4.
- Re-run a pipeline: L2.
- Modify input molecule: L1.
- Submit for docking or external service: L0.

## Open questions / not-yet-defined

- How to handle proprietary structures (withheld in publications).
- When to require experimental validation for predicted properties.
- How to weight conflicting predictions from different tools.

## Example instantiation

A docking study of 50 candidate compounds against a single protein
target. The harness canonicalizes SMILES, generates descriptors,
runs docking with deterministic seeds, and records every run.
Topology C; specialist handles chemistry; orchestrator handles
reporting.