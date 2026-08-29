# Principle 04: Verify Critical Outputs

## Statement

Outputs that drive downstream decisions must pass computational sensors
before they are acted upon. Inferential sensors supplement, never
replace, deterministic checks.

## Why this is a principle

Böckeler's taxonomy distinguishes computational sensors (type checker,
ESLint, RDKit, dependency-cruiser, Stryker, GitLeaks) from
inferential sensors (LLM-judge review prompts). The rule: prefer
deterministic. Anthropic long-running-apps uses an independent
evaluator with hard thresholds per criterion; the evaluator cannot
be the generator criticizing itself.

## What it requires

- For each deliverable, identify the critical outputs.
- For each critical output, prefer a computational sensor from
  `evals/catalog.md`.
- Inferential review is allowed but must be labelled as such.
- Independent reviewers receive only spec, artifact, evidence, and
  acceptance criteria — not the producer's reasoning chain.

## When this can be overridden

Overridable per task with explicit human approval and a recorded
compensating control.

## How to verify

- INV-008 lock check.
- Eval EVAL-004 (numerical audit) and EVAL-005 (citation verification)
  are mandatory for scientific evidence burden.

## Failure mode if ignored

Critical outputs silently regress. A reviewer using the same context
as the producer anchors to the producer's reasoning and misses the bug.