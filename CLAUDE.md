# Claude Code entrypoint

This repository is an upstream meta-architecture. Its job is to propose a
project-specific harness; it is not the target project and must not be copied or
executed wholesale.

## Start here

1. Read `HARNESS.md` for the shared operational contract.
2. Read `bootstrap/BOOTSTRAP.md` for the state machine and output contract.
3. Read the target project's input and inspect its workspace in read-only mode.
4. Use `core/`, `schemas/`, and `evals/` only as needed.
5. Produce a Bootstrap Report before creating project files.

## Claude Code rules

- Start in `dry-run`; do not modify the target project during discovery.
- Default to one agent plus tools. Use subagents only for justified specialization,
  independence, parallelism, or context isolation.
- Keep `CLAUDE.md` concise. Put path-specific project rules near the governed
  files or in `.claude/rules/` only when a real project requires them.
- Auto memory is local convenience, not the repository system of record. Return
  material state, evidence, and decisions to project files.
- Do not publish, merge, spend, send, delete, or expand permissions without the
  human gate required by `core/invariants.yaml`.

## Required outcome

End dry-run with `APPROVE`, `REVISE`, or `BLOCK`. Materialize only the files
listed in the approved report, then validate and write `harness.lock.yaml`.

Platform details: `platforms/CLAUDE-CODE.md`.

