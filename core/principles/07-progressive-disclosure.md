# Principle 07: Progressive Disclosure

## Statement

Load the smallest relevant context. Retrieve details on demand. AGENTS.md
and CLAUDE.md are maps, not encyclopedias.

## Why this is a principle

OpenAI's Codex docs: a large root AGENTS.md crowds out project
guidance. Anthropic context engineering: context is finite; just-in-time
retrieval beats preload. Hashimoto: each line in a focused AGENTS.md is
based on a bad agent behavior and resolved it.

## What it requires

- Root entrypoints stay under 8 KiB (validated by
  `scripts/validate_repo.py`).
- Detailed rules live near the files they govern or in dedicated
  docs.
- Task context is assembled dynamically:
  `Context = Compress(Retrieve(Knowledge, Task))`.
- Retrieval precedes compression.

## When this can be overridden

Overridable per task with a documented reason; entrypoints must
remain readable.

## How to verify

- INV-007 lock check.
- Validator enforces entrypoint size.

## Failure mode if ignored

The model loses context budget to upstream documentation, project
guidance, and task-relevant content together. Reasoning degrades.