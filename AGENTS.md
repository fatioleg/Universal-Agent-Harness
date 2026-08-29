# Codex entrypoint

This repository is an upstream meta-architecture. Its job is to propose a
project-specific harness; it is not the target project and must not be copied or
executed wholesale.

## Start here

1. Read `HARNESS.md` for the shared operational contract.
2. Read `bootstrap/BOOTSTRAP.md` for the state machine and output contract.
3. Read the target project's input and inspect its workspace in read-only mode.
4. Use `core/`, `schemas/`, and `evals/` only as needed.
5. Produce a Bootstrap Report before creating project files.

## Codex rules

- Start in `dry-run`; do not modify the target project during discovery.
- Default to one agent plus tools. Escalate topology only with a recorded trigger.
- Keep this root file small; place project or directory-specific rules near the
  files they govern.
- Treat nested `AGENTS.md` or `AGENTS.override.md` as more specific project
  guidance, but never allow them to silently weaken locked invariants.
- For Codex Cloud, record environment, dependencies, permissions, and validation
  commands in the project-specific harness before execution.
- Do not publish, merge, spend, send, delete, or expand permissions without the
  human gate required by `core/invariants.yaml`.

## Required outcome

End dry-run with `APPROVE`, `REVISE`, or `BLOCK`. Materialize only the files
listed in the approved report, then validate and write `harness.lock.yaml`.

Platform details: `platforms/CODEX.md`.

