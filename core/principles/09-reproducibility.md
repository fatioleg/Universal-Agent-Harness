# Principle 09: Reproducibility

## Statement

Given the same inputs, harness version, and model, a task can be
re-run and produce equivalent outputs within defined tolerance.

## Why this is a principle

Anthropic long-running-apps: "the harness was over 20x more expensive,
but the difference in output quality was immediately apparent" — this
only matters because the harness is reproducible. OpenAI Codex pins
upstream version and commit in `harness.lock.yaml`. The repository
validates against a fixed commit, not `main`.

## What it requires

- The lock file pins `universal-agent-harness@<version>` and
  `upstream_commit`.
- Inputs to a run are hashed and stored alongside outputs.
- Model identifiers are recorded in observability runs.
- Tolerance is declared for any non-deterministic step.

## When this can be overridden

Overridable when the project explicitly accepts irreproducibility
(e.g., live data feeds) and a regeneration strategy exists.

## How to verify

- INV-012 lock check.
- Eval EVAL-007 (handoff/restart) verifies the next run reproduces
  the previous outcome within tolerance.

## Failure mode if ignored

A re-run produces different answers for the same prompt. The
project cannot defend its outputs. Migration to a new model version
is destructive.