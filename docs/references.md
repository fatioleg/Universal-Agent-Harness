# References

The Universal Agent Harness design is informed by public writings
from practitioners, teams, and organizations working on agent
harnesses. This list is the working bibliography for v0.3.0.

## Primary sources

- **OpenAI** — Harness engineering: leveraging Codex in an
  agent-first world.
  https://openai.com/index/harness-engineering/
- **Mitchell Hashimoto** — My AI adoption journey.
  https://mitchellh.com/writing/my-ai-adoption-journey
- **Anthropic** — Managed agents.
  https://www.anthropic.com/engineering/managed-agents
- **Anthropic** — Harness design for long-running apps.
  https://www.anthropic.com/engineering/harness-design-long-running-apps
- **Birgitta Böckeler** — Sensors for coding agents (Martin Fowler
  site).
  https://martinfowler.com/articles/sensors-for-coding-agents.html

## Related tooling

- Birgitta Böckeler — `sensors-cli` (sidecar CLI for sensor
  orchestration, trend tracking).
  https://github.com/birgitta410/sensors-cli
- Vlad Khononov — Modularity Skills (LLM-judge review for
  modularity).
  https://github.com/vladikk/modularity
- Factory — ESLint plugin targeting agent failure modes.
  https://github.com/Factory-AI/eslint-plugin
- Stryker — mutation testing for JavaScript / TypeScript.
  https://stryker-mutator.io/
- dependency-cruiser — module boundary validation.
  https://github.com/sverweij/dependency-cruiser
- Matteo Vaccari — "Approved scenarios" testing pattern.
  https://matteo.vaccari.name/posts/acceptance-tests-for-ai-assisted-development/
- Pi — custom harness extension.
  https://pi.dev/

## Platform documentation

- OpenAI — Codex AGENTS.md documentation.
  https://developers.openai.com/codex/agent-configuration/agents-md
- OpenAI — Codex Cloud documentation.
  https://developers.openai.com/codex/cloud
- Anthropic — Claude Code memory documentation.
  https://docs.anthropic.com/en/docs/claude-code/memory
- Anthropic — Claude Code hooks documentation.
  https://docs.anthropic.com/en/docs/claude-code/hooks

## Local cross-references

- `docs/ARCHITECTURE.md` — the architectural thesis and four-plane
  model.
- `docs/glossary.md` — definitions of harness, archetype, sensor,
  and related terms.
- `docs/agent-topology.md` — Levels A–E.
- `docs/autonomy-levels.md` — L0–L5.
- `core/invariants.yaml` — the 12 locked invariants.
- `core/merge-policy.yaml` — typed resolution rules.
- `docs/DECISIONS.md` — Architecture Decisions AD-001 through
  AD-010.