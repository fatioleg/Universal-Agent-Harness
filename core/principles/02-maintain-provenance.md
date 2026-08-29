# Principle 02: Maintain Provenance

## Statement

Every material scientific or factual claim must retain an evidence
pointer to a source location and a transformation record.

## Why this is a principle

Böckeler's sensors article and Anthropic's long-running-apps harness
both treat provenance as the link between a claim and the artifact
that justifies it. Without provenance, claims are indistinguishable
from hallucinations. With provenance, claims survive model changes
and reviewer scrutiny.

## What it requires

- The evidence ledger (`core/schemas/extension/evidence-ledger.schema.json`)
  is instantiated for any project with `evidence_burden: scientific`
  or higher.
- Every entry into the ledger records claim_id, source_id,
  source_location, and evidence_type.
- Cross-references between claims and artifacts use stable IDs.

## When this can be overridden

Never. Like preserve-sources, this principle is non-overridable.

## How to verify

- INV-002 lock check in `core/invariants.yaml`.
- Eval EVAL-005 (citation verification) checks claim-source linkage.
- Eval EVAL-009 (conflicting-source resolution) checks that provenance
  disambiguates contradictions.

## Failure mode if ignored

Two agents may make the same claim from different sources and the
project cannot reconcile. A reviewer cannot audit. The output looks
authoritative but cannot be defended.