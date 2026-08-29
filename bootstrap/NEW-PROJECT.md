# New Project Request

Use this request with Codex, Codex Cloud, or Claude Code after granting the agent
read access to this Universal Agent Harness repository and the target project.

Replace the bracketed fields. Missing information may remain `UNKNOWN`; the agent
should ask only questions that materially change the proposed harness.

```text
You are bootstrapping a new project using the Universal Agent Harness.

UPSTREAM HARNESS
- Repository: [HARNESS_REPOSITORY_URL_OR_PATH]
- Version/tag/commit: [PINNED_VERSION_OR_COMMIT]
- Treat upstream as read-only.

TARGET PROJECT
- Workspace: [TARGET_PROJECT_PATH_OR_REPOSITORY]
- Objective: [OBJECTIVE]
- Domain: [DOMAIN]
- Background: [BACKGROUND_OR_UNKNOWN]
- Inputs: [INPUTS_OR_UNKNOWN]
- Deliverables: [DELIVERABLES]
- Constraints: [CONSTRAINTS_OR_UNKNOWN]
- Risk/deadline: [RISK_AND_DEADLINE_OR_UNKNOWN]
- Target agents: [CODEX, CODEX-CLOUD, CLAUDE-CODE, OR COMBINATION]
- Special requirements: [SPECIAL_REQUIREMENTS_OR_UNKNOWN]

INSTRUCTIONS
1. Load the platform entrypoint from the upstream harness:
   - AGENTS.md for Codex or Codex Cloud;
   - CLAUDE.md for Claude Code.
2. Read HARNESS.md and bootstrap/BOOTSTRAP.md from the upstream repository.
3. Begin in dry-run and read-only discovery mode.
4. Do not copy the upstream repository into the target project.
5. Do not assume multiagent architecture, SDD documents, memory systems,
   vector databases, graphs, or large directory trees.
6. Determine the smallest project-specific combination of specification,
   context, tools, permissions, sensors, evals, recovery, state, and agents.
7. Preserve existing project sources and organization.
8. Produce the complete Bootstrap Report and end with APPROVE, REVISE, or BLOCK.
9. Do not materialize or execute the project until I approve the report.
```

## After approval

Tell the agent:

```text
Materialize only the approved project-specific harness. Generate the platform
entrypoints required by target_agents, project.yaml, and harness.lock.yaml.
Add conditional files only when their approved trigger exists. Validate the
result and report BOOTSTRAP PASS or the exact blocking failure before executing
the first project task.
```

## Reference strategy

Preferred order:

1. pinned Git submodule or pinned clone;
2. repository URL plus an explicitly recorded commit hash;
3. downloaded release archive with checksum.

Avoid unpinned `main` as the only provenance. Never assume that the upstream
harness may modify the target project without the materialization gate.

