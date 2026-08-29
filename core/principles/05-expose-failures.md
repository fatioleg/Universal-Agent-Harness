# Principle 05: Expose Failures

## Statement

Failures, unavailable tools, uncertainty, retries, and incomplete
validation must be visible in the project's observability layer.

## Why this is a principle

Hashimoto: "if you give an agent a way to verify its work, it more
often than not fixes its own mistakes." Anthropic managed-agents
relies on tool-call errors surfacing in the harness loop rather than
WebSocket event streams. Anthropic long-running-apps reads evaluator
logs to find judgment divergence. All three depend on visibility.

## What it requires

- An observability record per agent run
  (`core/schemas/extension/observability-run.schema.json`).
- A failure registry entry per recurring failure pattern
  (`core/schemas/extension/failure-registry.schema.json`).
- "Silence is not success": every gate has a positive or negative
  outcome recorded.

## When this can be overridden

Never. Non-overridable per the override protocol.

## How to verify

- INV-009 lock check.
- Eval EVAL-010 (failure recovery) executes a controlled failure
  and verifies the failure is recorded.

## Failure mode if ignored

Crashes look like successes. Re-runs cannot reproduce. The harness
stops learning from its own mistakes.