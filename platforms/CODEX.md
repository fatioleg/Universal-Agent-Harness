# Codex and Codex Cloud adapter

## Discovery

Codex loads `AGENTS.md` before work. It constructs an instruction chain from the
project root toward the current directory; guidance closer to the working
directory has higher precedence. `AGENTS.override.md` can replace `AGENTS.md` at
a directory level.

Implications for this harness:

- keep the upstream root `AGENTS.md` short;
- put project-specific rules in the generated project root `AGENTS.md`;
- add nested instructions only when a directory has real specialized rules;
- do not rely on a large root instruction file because combined project guidance
  has a context-size limit;
- validate that locked upstream invariants remain present in the resolved lock.

## Codex Cloud

Codex Cloud executes in an isolated repository environment. A project-specific
harness should record:

- setup and validation commands;
- required dependencies and environment variables;
- network policy and secrets boundaries;
- expected artifacts and acceptance checks;
- permission and human-review gates before merge or external actions.

The repository is the portability boundary. Critical state must not exist only
in a local Codex thread.

## Verification

From the repository root, ask Codex to list the instruction sources it loaded
and summarize the active constraints. From nested directories, repeat the check
when overrides exist.

Official documentation:

- https://developers.openai.com/codex/agent-configuration/agents-md
- https://developers.openai.com/codex/cloud

