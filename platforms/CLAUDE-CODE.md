# Claude Code adapter

## Discovery

Claude Code uses `CLAUDE.md` and `CLAUDE.local.md` for persistent project
instructions. More specific directory guidance can be discovered as Claude reads
files under those directories. Path-scoped rules may live in `.claude/rules/`
when a real project needs them.

Implications for this harness:

- keep the upstream root `CLAUDE.md` short and specific;
- put project-specific guidance in the generated project root `CLAUDE.md`;
- use `.claude/rules/` only for rules that genuinely apply to scoped paths;
- avoid importing a large documentation tree at launch because imports organize
  content but do not reduce loaded context;
- use `/context` to inspect loaded instruction sources when debugging adherence.

## Memory boundary

Claude auto memory is machine-local and is not shared across machines or cloud
environments. It may help a session, but it cannot be the project system of
record. Material state, evidence, decisions, and reproducibility information
must return to versioned project files.

## Deterministic controls

Instructions describe desired behavior. Requirements that must execute at a
specific lifecycle point should eventually become a hook, test, schema, or other
computational sensor after the project demonstrates that need.

Official documentation:

- https://docs.anthropic.com/en/docs/claude-code/memory
- https://docs.anthropic.com/en/docs/claude-code/hooks

