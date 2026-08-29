# Principle 08: Prefer Deterministic

## Statement

If a property is deterministically testable, use a computational
sensor. Reserve LLM-judges for properties that genuinely require
inference.

## Why this is a principle

Böckeler's computational-vs-inferential distinction is the entire
rationale. Examples: SMILES validity via RDKit, DOI resolution via
Crossref, schema validation, type checking, lint, mutation testing.
Anthropic long-running-apps: hard thresholds per criterion beat
soft generator self-criticism.

## What it requires

- For each invariant in the project, identify whether a computational
  sensor exists.
- If yes, the sensor must run before any inferential check.
- Inferential sensors document which computational property they
  cannot check.

## When this can be overridden

Overridable when no computational sensor exists, with the override
recorded in the decision log.

## How to verify

- INV-008 lock check.
- Eval catalog entries declare computational-vs-inferential.

## Failure mode if ignored

An LLM-judge invents a plausible reason to pass a wrong answer. The
cost of inference is paid without the benefit of determinism.