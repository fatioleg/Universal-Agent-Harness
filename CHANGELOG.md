# Changelog

## 0.2.0 — 2026-08-29

- added separate, thin entrypoints for Codex and Claude Code;
- moved shared behavior to the canonical `HARNESS.md`;
- documented Codex, Codex Cloud, and Claude Code discovery behavior;
- added a reusable new-project request;
- added minimal project materialization templates;
- added deterministic repository validation and GitHub Actions;
- added target-platform fields to project input and resolved harness schemas.

## 0.3.0 — 2026-08-29

- added `archetypes/` with README and 9 reference-pattern stubs;
- added `core/principles/` with 9 markdown rationale files;
- added `core/policies/override-protocol.md`;
- added `core/schemas/extension/` with 8 JSON Schemas (state, evidence-ledger, decisions, tool-contract, permission-profile, failure-registry, eval-result, observability-run);
- added `evals/catalog.md` listing 10 universal eval categories;
- added `skills/classify-project/` with SKILL.md and supporting files for interactive classification;
- added `contracts/tools/` with README and 7 tool contract YAMLs (no implementations per AD-003);
- added `docs/agent-topology.md`, `docs/autonomy-levels.md`, `docs/references.md`, `docs/glossary.md`;
- added `examples/` placeholder;
- extended `scripts/validate_repo.py` with new required-file checks and schema/contract validation;
- documented AD-008 and AD-009 in `docs/DECISIONS.md`.

## 0.4.0 — 2026-08-29

- added `archetypes/full-sdd-project.md` (Spec-Driven Development lifecycle, named subagent roles, persistent memory, gates, handoffs);
- added `archetypes/knowledge-digestion.md` (caveman + MarkItDown + Graphify + Obsidian + optional NotebookLM pipeline as capability bundle);
- added `docs/sdd.md` with SPEC-00 through SPEC-04, Context Pack, Subagent Report, Handoff, Issues, Decisions, Gates, Completion checklist;
- added `docs/knowledge-digestion.md` describing the five-stage pipeline with role, when-to-use, and tradeoffs per stage;
- added `contracts/tools/caveman-compress.yaml`, `markitdown-normalize.yaml`, `graphify-build.yaml`, `obsidian-interface.yaml`, `notebooklm-explore.yaml` (12 tool contracts total);
- added capabilities `knowledge-digestion-pipeline`, `sdd-workflow`, `subagent-orchestration`, `checkpoint-handoff` to `core/universal.yaml`;
- documented AD-011 recording the v0.4.0 scope.

## 0.5.0 — 2026-08-29

- added `docs/tdd.md` — TDD red-green-refactor (Kent Beck / Fowler), test pyramid (Fowler / Ham Vocke), agent testing pyramid (LangWatch), mutation testing and approved scenarios (Böckeler), characterization tests (Feathers), test discipline rules and Definition of Done;
- added `docs/brownfield.md` — Legacy Code Change Algorithm (Feathers), characterization tests, seams, Sprout / Wrap techniques, agent-specific brownfield cautions (Hashimoto), safety checklist;
- added `docs/adr-template.md` — canonical ADR format (Context / Decision / Alternatives / Consequences) per AWS, Microsoft Azure, adr.github.io, with worked example;
- added 3 extension schemas: `acceptance-criterion.schema.json`, `test-case.schema.json`, `change-request.schema.json` (REQ→AC→Test→Impl traceability IDs);
- added `core/principles/10-proportional-design.md` — the smallest sufficient architecture satisfies the actual risks and constraints;
- added 3 project templates: `acceptance-criteria.template.md`, `test-cases.template.md`, `task-plan.template.md`;
- updated `docs/sdd.md` with requirement traceability, change protocol, prohibitions, Gate A–D, Definition of Done for tasks;
- updated `archetypes/full-sdd-project.md` and `archetypes/software-development.md` with cross-references to the new docs;
- updated `docs/references.md` with primary sources for TDD, test pyramid, brownfield, SDD enterprise practice, and ADRs;
- documented AD-012 recording the v0.5.0 scope.

## 0.5.1 — 2026-08-29

- added `docs/assets/harness-analogy.png` illustrating the
  energy-vs-intelligence parallel that motivates the harness
  concept, surfaced in `README.md` directly under the title;
- expanded `skills/classify-project/` from 15 to 24 questions
  across 6 groups, covering all 11 archetypes, 22 capabilities,
  12 tool contracts, and 11 schemas. Skill description and
  coverage section updated;
- fixed `eval-result` schema trigger missing from
  decision-tree.md (any project with running evals);
- deduped `AD-009` in `docs/DECISIONS.md` (renamed GitHub
  distribution decision to AD-013);
- heavy 3-pass audit (validator + static checks + spec-to-code
  compliance) executed; report at
  `docs/superpowers/audits/2026-08-29-v050-audit.md`. Result:
  PASS-WITH-NOTES, 0 critical, 0 important, 6 minor all
  AD-documented.

## 0.6.0 — 2026-10-11

- fixed CI: `actions/setup-python` cache now points to `requirements-dev.txt`; CI also runs behavioral tests;
- single product version: `VERSION` is the only release version; `core/universal.yaml` no longer declares
  `harness.version`; lock template pins `universal-agent-harness@0.6.0`; validator enforces consistency;
- bootstrap cases moved to the `BEVAL-*` namespace (`EVAL-*` stays the universal catalog);
- added UAH-lite (`skills/uah-init/`): `uah.py` (init, compile, import-plan, approve, task, checkpoint, preflight),
  stdlib-only Claude Code hook `uah_guard.py` (PreToolUse, SessionStart, Stop), H0 and risk H1 profiles, templates;
- deterministic fail-closed H0–H3 resolver compiled to `.claude/settings.json` permissions and hooks;
- plan approval bound to the sha256 of the plan body (G1); checkpoint/resume state in `state/current.md` (G4);
- OMC bound by artifacts (`.omc/plans`, `.omc/specs`) and pinned with `omc capabilities lock/check`;
- added `tests/test_uah_lite.py` (30 behavioral tests: AT-01/02/03/05/07/09/14 plus 14 regressions from an independent review — grant scope, fail-closed guard, quote-aware shell parsing, literal-directory protection, YAML-safe init, G4 with accented paths) and `docs/uah-lite.md`;
- documented AD-014.

## 0.7.0 — 2026-10-11

- added an integration catalog (`skills/uah-init/integrations/`) following the report's integration contract:
  Workflow_Digestion (documents → corpus → graph → Obsidian), specboard (module validation board with human-only
  verification) and CalcBoard (computational-chemistry results board);
- `project.yaml` gained `integrations:`; enabled integrations add trusted H1-level rules (specboard: human-only
  review/verify, `.specboard/**` and planning CLI allowed before approval; CalcBoard: `painel.py ler`;
  Workflow_Digestion: `graphify` asks because of token cost);
- new commands: `integrations [list|install|enable|disable]` (recommendations from `project.domains` + risk;
  install clones into `~/.claude/tools/` and links the skill) and `explain` (effective rules in plain language);
- `init --domains/--integrations`; unknown fields now fail with a spelling suggestion; richer `project.yaml` template;
- SessionStart summary and `preflight` report each enabled integration and whether it is installed (machine-specific
  status is kept out of the policy hash);
- 39 behavioral tests (9 new for integrations); documented AD-015.

## 0.8.0 — 2026-10-11

- MVP slices for incremental SDD: master plan (`plan/approved.md`) plus `plan/slices/slice-N.md`, each approved
  separately (`approve --slice N`, requires an approved master plan, human confirmation);
- once a project uses slices, the guard only allows material actions with an active, approved, unchanged slice;
  `slice done N` closes the gate until the next slice is approved;
- new `slice [list|new|activate|done]` command, `import-plan --slice N`, SDD slice template (REQ/AC, out of scope,
  tests, abandonment criterion, suggested executor agent);
- checkpoint records the active slice and reminds to rebuild the specboard; SessionStart, preflight and explain show
  slice status;
- SKILL.md documents the omc-plan → import-plan → specboard → approve → execute → slice done loop with a prompt
  template; 46 behavioral tests.

## 0.8.1 — 2026-10-11

- added the `publish-documents` integration (catalog entry) for the new skill
  https://github.com/fatioleg/publish-documents: single-source Quarto publishing with report-visual (Typst),
  journal-scientific (XeLaTeX) and word-editable (ABNT DOCX) profiles, preflight, verify and visual review;
- rules: `quarto install|add|use|update` and `tlmgr install` ask; `pubdoc.py preflight|doctor` allowed before plan
  approval; recommended for `artigo-teorico`, `fomento`, `edital`, `relatorio`, `revisao-de-literatura`, `documentos`;
- 47 behavioral tests.

## 0.8.2 — 2026-10-11

- added the `sci-figures` integration (catalog entry) for the new skill https://github.com/fatioleg/sci-figures:
  publication figures from short specs — 2D molecules (RDKit, ACS 1996), structures, crystals and surfaces (ASE),
  diagrams (D2) and data plots (matplotlib, colour-blind-safe journal style), with provenance manifest and verify;
- rules: `figs.py setup` (installs packages) asks; `figs.py doctor` allowed before plan approval; recommended for
  chemistry/materials/simulation domains, `artigo-teorico`, `relatorio`, `fomento`;
- 48 behavioral tests.

## 0.9.0 — 2026-10-11

Restrições do UAH sobre a execução do OMC (avaliação da proposta de "Work Dispatcher": rejeitado o dispatcher,
que duplicaria fila, estado e roteamento; adotadas só as restrições):
- reasoning level per task (`nível: leve | padrão | crítico`) in plan/slice templates, mapped in SKILL.md to OMC
  agents with pinned models (Haiku/Sonnet/Opus) and "deterministic tool first";
- attempt limit: `checkpoint --failed` counts failures per task; at the risk limit (low 5, medium 3, high 2; H2 may
  only lower via `policy.max_attempts`) the task is blocked, the guard denies material actions and SessionStart
  says PARE; only a human-confirmed `--reset-attempts` unblocks;
- cost per validated task: `checkpoint --status done --cost/--tokens/--level` appends to `state/tarefas.jsonl`;
  preflight reports validated tasks, mean attempts and cost per validated task;
- verified facts: OMC `routeTask()` exists but is not invoked at runtime by the plugin; `OMC_RUN_BUDGET_TOKENS`
  does not exist in OMC 5.4.0; no hard token budget is enforceable, so none is claimed;
- 67 behavioral tests.

## 0.8.4 — 2026-10-11

- new `uah.py setup-env [--integrations ids|all] [--install]`: reports the machine and, with `--install`,
  installs without sudo the `uah-init` skill link, catalog skills at their pinned commit, Quarto 1.10.19 and
  D2 0.9.0 (pinned version, SHA-256 checked against the project's checksum file, extracted to `~/.local/opt`
  with the tarfile `data` filter, linked in `~/.local/bin`) and the sci-figures venv; prints exact commands for
  OMC (Claude Code plugin), molar_vis (Rust/maturin) and system packages (apt);
- `setup-env --install` requires human confirmation inside UAH projects (H0-approve rule);
- README: "Instalação do zero" section; sci-figures catalog ref updated; 62 behavioral tests.

## 0.8.3 — 2026-10-11

Correções da auditoria do Codex:
- guard: regras regex aplicadas também ao comando normalizado pelo shell (sem aspas/escapes), fechando
  bypasses como `a''pprove`, `g''it push`, `cu''rl`; regras críticas compiladas também como permissões
  nativas do Claude Code (segunda camada: `Bash(git push:*)` ask, `Bash(gh repo delete:*)` deny etc.);
- política ausente: só `compile|init|preflight|status|explain` do uah.py passam (sem redirecionamento nem
  encadeamento); `approve`, `task --grant`, `integrations install` e o resto são negados;
- executáveis: `./cat` ou `tools/cat` não contam como leitura (só PATH ou diretórios de sistema);
  `cp|mv|ln|install -t DIR`/`--target-directory` entram na checagem de caminhos imutáveis;
- escrita fora do projeto: pede confirmação (negada antes da aprovação); só a área temporária fica livre;
- CLIs liberadas antes da aprovação (gate_cli) exigem o script dentro da skill instalada E de origem
  verificada (remoto git = repositório do catálogo), não apenas o nome do arquivo;
- G4: considera alterações já commitadas desde o último checkpoint e, sem git, varre o projeto;
- integrações fixadas por commit (`ref` no catálogo, validado como SHA de 40 caracteres); `install` faz
  checkout do ref e recusa clone com remoto diferente; status mostra origem verificada e commit fixado;
- compile atômico: settings.json é preparado antes e todos os arquivos são gravados por troca atômica;
- 58 testes (10 novos de auditoria).

## 0.1.0 — 2026-08-29

- created the initial declarative bootstrap;
- defined universal invariants, typed merge rules, schemas, and bootstrap evals;
- established dry-run before materialization and minimum sufficient topology.

