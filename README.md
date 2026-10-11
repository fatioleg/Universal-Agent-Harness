# Universal Agent Harness

> Meta-arquitetura versionada para configurar o menor harness robusto
> necessário para cada novo projeto assistido por IA. Legível por
> Codex e Claude Code sem duplicar o núcleo de regras
> entre plataformas.

![Harness analogy — machines operationalize energy; harnesses operationalize intelligence](./docs/assets/harness-analogy.png)

## Para que serve

Este repositório é um **bootstrap de harness** — uma infraestrutura
reutilizável que você aponta para um projeto novo. Em vez de começar
cada projeto do zero, você aponta o agente para cá e o harness
propõe a configuração mínima suficiente para aquele projeto.

A arquitetura segue quatro camadas (Control, Knowledge, Execution,
Assurance) e três princípios inegociáveis: **invariantes, não
implementações**; **harness determinístico primeiro**; **fonte como
autoridade** (sources imutáveis, representações derivadas).

## Como usar em um projeto novo

**Caminho recomendado (v0.6.0): UAH-lite.** Instale a skill uma vez
(`ln -s "$PWD/skills/uah-init" ~/.claude/skills/uah-init`) e rode
`/uah-init` no Claude Code dentro do projeto. Ela cria 5 arquivos curtos,
compila H0–H3 em `permissions` e hooks do Claude Code, exige plano aprovado
por humano antes de alterações materiais (risco medium/high) e mantém
`state/current.md` para retomada. Detalhes: [`docs/uah-lite.md`](docs/uah-lite.md).

Caminhos declarativos anteriores (continuam válidos):

1. **Caminho mais leve** — referencie este repositório como
   submódulo Git ou clone fixado em `.harness/upstream` no seu
   projeto. Registre o commit exato em `harness.lock.yaml`.
2. **Caminho pela skill** — peça ao agente para carregar a skill
   `classify-project` (em `skills/classify-project/SKILL.md`).
   Ela faz 15 perguntas e recomenda arquétipo, capacidades,
   contratos de ferramentas e sensores antes de qualquer
   Bootstrap Report.
3. **Caminho pelo bootstrap** — use `bootstrap/NEW-PROJECT.md`
   como prompt inicial do Codex ou do Claude Code. Ele
   executará o protocolo em `bootstrap/BOOTSTRAP.md` em modo
   dry-run e produzirá o Bootstrap Report.

Todos os caminhos terminam em `APPROVE`, `REVISE` ou `BLOCK`
antes de qualquer modificação no projeto de destino.

## Funcionalidades disponíveis para estruturar um harness otimizado

### Invariantes e princípios

- **12 invariantes travadas** em `core/invariants.yaml` — `locked`,
  não podem ser silenciosamente enfraquecidas.
- **9 princípios** em `core/principles/` — versão legível por
  humanos, com proveniência da fonte (OpenAI, Anthropic,
  Hashimoto, Böckeler).
- **Protocolo de override** em `core/policies/override-protocol.md`
  — quais princípios podem ser desviados, quais não, e o que
  registrar quando um desvio é necessário.

### Arquétipos de referência

Em `archetypes/` você encontra 11 padrões de workflow
documentados. **Atenção: são referência, não pacotes H1**.
Não são mesclados via `core/merge-policy.yaml` até que pelo
menos dois projetos reais justifiquem a promoção:

- `scientific-research` — investigação empírica, ledger de
  evidência pesado.
- `computational-science` — simulação e análise numérica,
  reprodutibilidade como núcleo.
- `computational-chemistry` — subset do anterior com sensores
  químicos (RDKit, pymatgen).
- `literature-review` — revisão sistemática, verificação de
  citação, PRISMA.
- `knowledge-base` — curadoria de longa duração, dedup e
  resolução de conflitos.
- `data-analysis` — análise de dataset, sensores estatísticos,
  manifest de execução.
- `software-development` — código-centrado, testes e linters
  como sensores primários.
- `document-production` — template-driven, validadores de
  formatação.
- `grant-project-proposal` — prazo + orçamento + sensores de
  conformidade do financiador.
- `full-sdd-project` — Spec-Driven Development completo:
  cinco specs (Charter, Requirements, Architecture, Validation,
  Deliverable), subagentes nomeados (Research, Domain Expert,
  Data Auditor, Implementation, QA, Red-Team), Context Packs,
  Subagent Reports, Handoffs, Issues, Decisions, Gates,
  Completion checklist. Veja `docs/sdd.md`.
- `knowledge-digestion` — pipeline canônica de ingestão
  `caveman → MarkItDown → Graphify → Obsidian → NotebookLM
  (opcional)`. Cada ferramenta é opt-in com papel definido.
  Veja `docs/knowledge-digestion.md`.

### Schemas de runtime

Em `core/schemas/extension/` você tem 8 schemas JSON Schema
draft 2020-12 para os artefatos que projetos podem instanciar:

- `state.schema.json` — o que está acontecendo agora.
- `evidence-ledger.schema.json` — claims com proveniência.
- `decisions.schema.json` — decisões com rationale.
- `tool-contract.schema.json` — contrato de ferramenta.
- `permission-profile.schema.json` — escopo por papel.
- `failure-registry.schema.json` — falhas com harness patch.
- `eval-result.schema.json` — resultado de eval.
- `observability-run.schema.json` — um registro por execução.

Schemas base (`project-input`, `resolved-harness`) ficam em
`schemas/` e são byte-idênticos desde v0.2.0.

### Topologia de agentes (Levels A–E)

Detalhado em `docs/agent-topology.md`. Cada nível adiciona custo
de coordenação; só escale quando houver justificativa registrada.

- **A** — agente único + ferramentas. Default.
- **B** — agente + revisor independente.
- **C** — orquestrador + um especialista.
- **D** — especialistas paralelos.
- **E** — equipe multiagente + verificação independente.

### Níveis de autonomia (L0–L5)

Detalhado em `docs/autonomy-levels.md`. Autonomia é por
capacidade e limitada por escopo, validadores, retries e
escalation. Default universal: baixo (L0–L1 em ações
materiais).

### Catálogo universal de evals

Em `evals/catalog.md`, 10 categorias de avaliação que qualquer
harness pode aplicar: retrieval, ingestão, extração, auditoria
numérica, verificação de citação, geração de artefato, handoff,
coordenação, resolução de conflitos, recuperação de falha.
Cada arquétipo seleciona seu subconjunto.

### Contratos de ferramentas (sem código)

Em `contracts/tools/` você tem 7 especificações YAML de
ferramentas que o agente pode invocar. **As implementações estão
adiadas para v0.4.0+** (AD-003, AD-010) até que pilotos reais
justifiquem. Os contratos informam ao agente quais capacidades
existem conceitualmente:

- `check-invariants` — verifica lock contra invariantes travadas.
- `diff-harness` — diff entre versões H0.
- `verify-artifact` — verificador genérico com perfil de sensor.
- `list-events` — leitura de log de eventos.
- `sensor-trend` — tendência de sensores (padrão Böckeler).
- `lock-drift-check` — drift entre commit fixado e upstream real.
- `scaffold-project` — geração de harness de projeto a partir
  de `project.yaml`.
- `caveman-compress` — comprimir slice recuperado ao budget
  de tokens.
- `markitdown-normalize` — converter PDF/DOCX/PPTX/XLSX/HTML/
  image para Markdown canônico.
- `graphify-build` — grafo de conhecimento com ponteiro de
  evidência em cada aresta.
- `obsidian-interface` — sincronizar canônico ↔ vault Obsidian.
- `notebooklm-explore` — análise externa via NotebookLM MCP
  (efêmero por default).

### Skill de classificação interativa

Em `skills/classify-project/`, uma skill que o agente carrega
quando você pede para começar um projeto novo. 15 perguntas em
5 grupos, com árvore de decisão e template de saída. Arquétipo,
capacidades, contratos, sensores, schemas, topologia e
autonomia ficam pré-configurados antes do Bootstrap Report.

### Spec-Driven Development (SDD)

SDD é o workflow estruturado para projetos complexos. Vive em
três lugares:

- **`docs/sdd.md`** — guia canônica do SDD no harness. Cobre
  cinco specs (Project Charter, Requirements, Architecture,
  Validation, Deliverable), Context Pack, Subagent Report,
  Handoff, Issues, Decisions, Gates (A–D), Definition of
  Done, change protocol, lista de proibições, e a regra
  "especificação é source of truth para intenção; código é
  source of truth para comportamento atual".

- **`archetypes/full-sdd-project.md`** — archetype opt-in para
  projetos que precisam da máquina completa: SDD workflow,
  seis subagentes nomeados (Research, Domain Expert, Data
  Auditor, Implementation, QA, Red-Team), persistent memory,
  handoffs estruturados, gates em sequência. Aciona a
  capability `sdd-workflow`.

- **`templates/project/`** — três templates novos para
  operacionalizar o SDD em um projeto:
  - `acceptance-criteria.template.md` — REQ→AC→Test→Impl
    com matriz de cobertura.
  - `test-cases.template.md` — pyramid mix + estrutura
    given/when/then.
  - `task-plan.template.md` — decomposição por tarefa com
    Definition of Done por task.

Schemas de extensão formalizam os identificadores:

- `acceptance-criterion.schema.json` (AC-NNNN-NN).
- `test-case.schema.json` (TEST-NNNN-NN com `pyramid_layer`).
- `change-request.schema.json` (CR-NNNN).

A regra de **proporcionalidade** vale: SDD completo só se
aplica a projetos médios / grandes / complexos. Projetos
triviais não precisam das cinco specs — uma página de charter
já basta.

### Disciplina de testes (TDD e test pyramid)

`docs/tdd.md` codifica a disciplina de testes com respaldo em
fontes primárias:

- **TDD red-green-refactor** (Kent Beck via Fowler).
- **Test pyramid** prático — unit, integration, contract,
  end-to-end, regression — com Ham Vocke no Fowler site.
- **Agent testing pyramid** — deterministic unit (base) →
  evals & optimization (middle) → simulations (peak), per
  LangWatch.
- **Mutation testing** e **approved scenarios** (Böckeler).
- **Characterization tests** para brownfield (Feathers).
- Regras explícitas de "quando TDD se aplica" e "quando não".

### Brownfield safety

`docs/brownfield.md` codifica o protocolo de Feathers para
trabalhar com código existente:

- Definição de legacy code como código sem testes.
- Legacy Code Change Algorithm: identify change points →
  find seams → break dependencies → write characterization
  tests → change → refactor.
- Técnicas Sprout e Wrap.
- Cautelas específicas para agentes (Hashimoto: end-of-day
  agents, sem ship unsupervised).

### ADR format canônico

`docs/adr-template.md` define o formato de ADR (Context,
Decision, Alternatives, Consequences) alinhado com AWS,
Microsoft Azure Well-Architected Framework e a comunidade
adr.github.io, com exemplo preenchido.

### Rastreabilidade REQ→AC→Test→Impl

Três novos schemas de extensão formalizam identificadores:

- `acceptance-criterion.schema.json` (AC-NNNN-NN).
- `test-case.schema.json` (TEST-NNNN-NN com pyramid_layer).
- `change-request.schema.json` (CR-NNNN).

Mais três templates:

- `templates/project/acceptance-criteria.template.md`.
- `templates/project/test-cases.template.md`.
- `templates/project/task-plan.template.md`.

### Princípio da arquitetura proporcional

`core/principles/10-proportional-design.md` registra a regra
"menor arquitetura suficiente" — classificar projeto em
trivial / pequeno / médio / grande / complexo-crítico e
ativar somente o que a classe de risco exige.

### Infraestrutura operacional e governança

O harness expõe uma série de artefatos de governança que
operacionalizam as práticas acima. Eles já existem no repo;
este README serve como índice.

**Contrato operacional canônico (`HARNESS.md`).** Define
a state machine de bootstrap:

```text
INITIAL → DISCOVERED → PROPOSED → APPROVED → MATERIALIZED → VALIDATED
```

Todo projeto novo começa em dry-run. A passagem
`PROPOSED → MATERIALIZED` requer aprovação humana quando a
proposta contém decisões científicas, estratégicas,
externas, irreversíveis, de permissão, publicação ou custo.

**Recovery loop.** Documentado em `HARNESS.md` §Recovery:

```text
PLAN → PRECHECK → EXECUTE → OBSERVE → SENSE
                                    ├─ PASS → COMMIT
                                    └─ FAIL → CLASSIFY
                                                ├─ REPAIR → REVALIDATE
                                                └─ ROLLBACK / ESCALATE
```

Agentes não terminam em PASS/FAIL silencioso. Falhas viram
entradas no `failure-registry.schema.json`; correções viram
sensores de regressão.

**Bootstrap Report.** Ao final do dry-run, o agente produz um
relatório de 12 seções cobrindo entendimento, inventário,
classificação, capabilities selecionadas, resolução H0-H3,
topologia, knowledge/estratégia de contexto, permissões e
gates, validação/QA/eval/observability/recovery, lista exata
de arquivos a criar com seus triggers, avisos, blockers e
recomendação final (`APPROVE`, `REVISE` ou `BLOCK`). Detalhes
em `bootstrap/BOOTSTRAP.md` §10.

**NEW-PROJECT.md.** Template de prompt inicial pronto para
Codex ou Claude Code. Define a estrutura de declaração que o
agente recebe, incluindo o pedido de referenciar o upstream
harness por URL/tag/commit pinados. Não copiar o repo;
apontar para ele.

**Templates mínimos para projetos gerados.** Todo projeto
novo criado via bootstrap recebe pelo menos:

- `AGENTS.md` — entrypoint para Codex / Codex Cloud.
- `CLAUDE.md` — entrypoint para Claude Code.
- `project.yaml` — input canônico do projeto, validado contra
  `schemas/project-input.schema.json`.
- `harness.lock.yaml` — pin do upstream commit + capabilities
  resolvidas + permissões + topologia + assurance.

Ambos entrypoints de plataforma são gerados apenas quando o
projeto declara a plataforma correspondente como alvo.

**Resolução tipada H0-H3 (`core/merge-policy.yaml`).** O
harness usa um mecanismo de merge **typed**, não concat
de strings:

- **H0** — universal invariants, defaults, schemas.
- **H1** — lifecycle profile opcional, capability overlays,
  domain packs.
- **H2** — configuração e bindings do projeto.
- **H3** — restrições de curta duração para uma task.

Regras: campos desconhecidos são rejeitados; permissões podem
ser restringidas mas não expandidas silenciosamente; assurance
floors só podem ser fortalecidos; conflitos falham fechados.

**Quatro planos de responsabilidade.** Documentados em
`docs/ARCHITECTURE.md` como lenses, não como serviços
obrigatórios:

- **Control** — intent, specification, routing, permissions,
  budgets, gates, state transitions.
- **Knowledge** — sources, representations, retrieval,
  context assembly, evidence, provenance.
- **Execution** — agents, models, skills, tools, code,
  compute, external services.
- **Assurance** — guides, sensors, validators, evals,
  observability, review, recovery.

`Assurance` observa os outros três. Um projeto pequeno pode
ter um Knowledge Plane trivial e nenhum orchestration service.

**Capability vocabulary.** 18 capabilities declaradas em
`core/universal.yaml` e selecionáveis via Bootstrap Report.
Exemplos: `discovery`, `specification`, `state-continuity`,
`source-ingestion`, `normalization`, `cataloging`,
`lexical-retrieval`, `semantic-retrieval`, `graph-retrieval`,
`context-compression`, `scientific-evidence`,
`computational-execution`, `data-analysis`,
`artifact-production`, `independent-review`, `external-write`,
`publication`, `long-running-orchestration`. Cada capability
aciona capacidades concretas no harness.

**Defaults universais.** Conservadores por design: `delete`,
`install`, `publish`, `send`, `spend`, `merge` são
`denied` por padrão. `read` é `allowed-within-scope`,
`network` é `task-justified`. Expansões acima do default
requerem human gate explícito.

**Platform-specific docs.** Comportamento de discovery
documentado por plataforma:

- `platforms/CODEX.md` — Codex e Codex Cloud (instruction chain
  AGENTS.md, override por pasta, ambiente isolado do Cloud).
- `platforms/CLAUDE-CODE.md` — Claude Code (CLAUDE.md,
  `.claude/rules/`, auto memory como conveniência local
  apenas).

**Override protocol.** `core/policies/override-protocol.md`
define quando princípios podem ser desviados, quais não, e o
que registrar quando o desvio é necessário. Três princípios
não podem ser desviados (preserve-sources, maintain-
provenance, expose-failures); os outros seis podem via
protocolo explícito.

**Failure registry.** Toda falha recorrente é registrada em
`core/schemas/extension/failure-registry.schema.json` com
`pattern`, `root_cause`, `harness_patch`, `regression_sensor`,
`status` e `linked_eval`. Falhas que se tornam sistêmicas
promovem o harness; falhas locais não.

**Glossário.** `docs/glossary.md` define harness, archetype,
sensor (computacional vs inferencial), guide, evidence
ledger, claim, provenance, H0-H3, lock file, Bootstrap Report,
tool contract, validation vs QA vs eval, permission profile,
material gate. ~80 linhas, ponto de entrada para vocabulário.

**Architecture Decision Records.** `docs/DECISIONS.md`
registra AD-001 a AD-012 (criação inicial, H1 composition,
v0.1.0 scope, state and memory, permissions, language,
pilot order, cross-platform entrypoints, v0.3.0 scope,
v0.4.0 scope, v0.5.0 scope). Cada AD registra uma decisão
que de outro modo ficaria implícita no código.

**Exemplos.** `examples/` é placeholder intencional para um
worked example end-to-end. A entrada do primeiro exemplo é
adiada até que pelo menos um projeto real tenha sido
bootstrapped via protocolo (AD-003).

**Validador.** `scripts/validate_repo.py` valida schemas,
YAML, IDs únicos de invariantes e evals, exemplo de entrada,
tamanho dos entrypoints, e roteamento de referências. Roda
localmente e em CI (`scripts/validate_repo.py` em GitHub
Actions).

**Como ativar a skill em um projeto novo:**

- Claude Code descobre a skill automaticamente em
  `skills/classify-project/SKILL.md` no workspace. Para projetos
  novos, adicione este repo como submódulo em `.harness/upstream`
  ou copie `skills/classify-project/` para `.claude/skills/`.
- Codex descobre a skill em
  `.codex/agent-configuration/skills/classify-project/SKILL.md`.
  Copie ou symlink o diretório para esse caminho no projeto.
- O `description` no frontmatter da skill lista frases-gatilho
  ("start a new project", "bootstrap a project", "qual
  arquitetura de harness") para que o agente carregue a skill
  sob demanda mesmo sem você nomeá-la.

### Garantia e observabilidade

- **Sensors computacionais preferidos** sobre LLM-judge
  (Böckeler).
- **Revisor independente** com contexto separado do produtor
  para reduzir anchoring.
- **Loop de recuperação** documentado em `HARNESS.md`:
  PLAN → PRECHECK → EXECUTE → OBSERVE → SENSE → (REPAIR ou
  ESCALATE).
- **Loop de falha → patch de harness** — toda falha recorrente
  vira sensor de regressão (Hashimoto).
- **Validador determinístico** em `scripts/validate_repo.py`
  roda localmente e em CI.

## Estrutura

```text
Universal-Agent-Harness/
├── AGENTS.md                 # entrypoint para Codex / Codex Cloud
├── CLAUDE.md                 # entrypoint para Claude Code
├── HARNESS.md                # contrato canônico compartilhado
├── VERSION                   # 0.6.0 (única versão do produto)
├── CHANGELOG.md
├── README.md                 # este arquivo
│
├── core/
│   ├── universal.yaml        # defaults
│   ├── invariants.yaml       # 12 invariantes travadas
│   ├── merge-policy.yaml     # resolução tipada H0-H3
│   ├── principles/           # 9 princípios em prosa
│   ├── policies/             # override-protocol.md
│   ├── schemas/extension/    # 11 schemas de runtime
│   └── evals/                # (placeholder)
│
├── archetypes/               # 11 padrões de referência (não H1)
│
├── bootstrap/                # BOOTSTRAP.md, NEW-PROJECT.md, exemplo
│
├── templates/project/        # templates para projetos gerados
│
├── platforms/                # CODEX.md, CLAUDE-CODE.md
│
├── schemas/                  # project-input, resolved-harness
│
├── skills/classify-project/  # skill interativa
├── skills/uah-init/          # UAH-lite (executável): uah.py, hooks/uah_guard.py,
│                             # profiles/ (H0 + risco H1), templates/
│
├── tests/test_uah_lite.py    # testes comportamentais (AT-01/02/03/05/07/09/14)
│
├── contracts/tools/          # 12 contratos YAML (sem código)
│
├── docs/                     # ARCHITECTURE, agent-topology,
│                             # autonomy-levels, glossary, references,
│                             # sdd, knowledge-digestion, tdd,
│                             # brownfield, adr-template, DECISIONS,
│                             # uah-lite
│
├── evals/
│   ├── bootstrap-cases.yaml  # cases BEVAL-* para validar este repo
│   └── catalog.md            # 10 categorias universais
│
├── examples/                 # placeholder
│
├── scripts/validate_repo.py  # validador estático (roda local e em CI)
│
└── .github/workflows/validate.yml
```

## Validação

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py
```

python -m unittest discover -s tests -v   # testes comportamentais do UAH-lite
```

O validador e os testes rodam no GitHub Actions. Saída esperada do
validador em v0.6.0:

```text
PASS: Universal Agent Harness 0.6.0
PASS: 102 required files
PASS: 12 locked invariants
PASS: 8 bootstrap eval cases
PASS: 11 extension schemas
PASS: 12 tool contracts
PASS: version consistency (VERSION, lock template, UAH-lite runtime)
```

## Status

Versão **0.6.0**. Inclui o UAH-lite (`skills/uah-init`), primeira
parte executável: resolvedor H0–H3 determinístico compilado para o
Claude Code, gate de plano aprovado e checkpoint de retomada, com
testes comportamentais. Núcleo multiplataforma, 11 arquétipos de
referência, 11 schemas de runtime (incluindo AC, Test,
ChangeRequest), skill de classificação, 12 contratos de
ferramentas (sem implementações), catálogo universal de
evals, guias de SDD, knowledge-digestion, TDD, brownfield e
ADR format.

A classificação é agent-assisted. Um resolvedor automático
completo só será considerado depois que pilotos reais
demonstrarem regras estáveis e mecanicamente verificáveis
(AD-003).

## Quando **não** usar este harness

- O projeto é trivial e não justifica governança.
- O usuário prefere que o agente improvise.
- Não há intenção de versionar configuração, sensores ou
  decisões.
- Não há expectativa de auditoria ou reprodutibilidade.

## Referências da proposta

Estas são as fontes primárias que fundamentam a arquitetura.
Cada link aponta para a publicação que inspirou decisões
específicas deste design. A bibliografia completa está em
`docs/references.md`.

### Camada 1 — Harness, agentes e observabilidade

- **OpenAI — Harness engineering: leveraging Codex in an
  agent-first world.**
  https://openai.com/pt-BR/index/harness-engineering/

  Onde entra: AGENTS.md enxuto como mapa, scaffolds
  reutilizáveis, repositório como system of record, contexto
  escasso e progressivo, observabilidade acessível ao agente,
  arquitetura enforceable e controle de entropia.

- **Mitchell Hashimoto — My AI adoption journey.**
  https://mitchellh.com/writing/my-ai-adoption-journey

  Onde entra: princípio de "engineer the harness". Toda
  falha recorrente vira patch de harness + sensor de
  regressão + eval. Loop `failure → root cause → harness
  patch → regression sensor → eval`. AGENTS.md por pasta
  com cada linha ligada a um erro real. Brownfield safety:
  end-of-day agents produzindo relatórios, sem ship
  unsupervised.

- **Anthropic — Managed agents.**
  https://www.anthropic.com/engineering/managed-agents

  Onde entra: separar session, harness e sandbox. Harness
  stateless com `wake/getSession`/`emitEvent`/`getEvents`.
  Tools como `execute(name, input) → string`. Proxies OAuth
  para credenciais ficarem fora do sandbox. Sandbox
  provisionado lazy via tool call. Cattle-not-pets.

- **Birgitta Böckeler — Sensors for coding agents.**
  https://martinfowler.com/articles/sensors-for-coding-agents.html

  Onde entra: taxonomia guides vs sensors, computacional vs
  inferencial. Preferência por sensor determinístico. Eixos
  de runtime (during/pipeline/schedule/production).
  `sensors-cli` como referência para `sensor-trend.yaml`.
  Harness templates como bundles reutilizáveis de guides +
  sensors — origem da ideia de archetypes. Mutation testing
  e approved scenarios como sensores avançados.

- **Anthropic — Harness design for long-running apps.**
  https://www.anthropic.com/engineering/harness-design-long-running-apps

  Onde entra: context resets vs compaction reavaliados por
  modelo. Handoff artifacts estruturados. Comunicação
  file-based entre agentes. Sprint contracts. Padrão
  generator-evaluator (GAN). Planner + generator + evaluator
  com Playwright. Thresholds duros por critério. "Stress-test
  every harness component" — remover o que ficou obsoleto.
  Separação entre baseline funcional e melhorias baseadas em
  modelo.

### Camada 2 — Test discipline e Spec-Driven Development

#### 2a — TDD e test pyramid

- **Kent Beck via Martin Fowler — Test-Driven Development.**
  https://martinfowler.com/bliki/TestDrivenDevelopment.html

  Onde entra: `docs/tdd.md` codifica o ciclo red-green-refactor
  (Beck) com a ressalva de Fowler que "não é bala de prata" e
  que o terceiro passo (refactor) é o mais comumente
  negligenciado.

- **Ham Vocke — The Practical Test Pyramid (Martin Fowler
  site).**
  https://martinfowler.com/articles/practical-test-pyramid.html

  Onde entra: shape da pirâmide de testes — unit na base,
  integration no meio, e2e no topo. Regra "push tests down
  the pyramid". "Don't test trivial code". "Test observable
  behavior, not implementation."

- **LangWatch — The Agent Testing Pyramid (June 2025).**
  https://langwatch.ai/scenario/best-practices/the-agent-testing-pyramid/

  Onde entra: pirâmide adaptada para LLM-agent systems —
  deterministic unit tests (base) → evals & optimization
  (middle) → simulations (peak). Sempre manter unit tests
  determinísticos do plumbing, mesmo em projetos agent-heavy.

- **Rafal Wilinski — Agentic Evals Pyramid.**
  https://rwilinski.ai/posts/evals-pyramid/

  Onde entra: ciclo iterativo de unit-test-like evals para
  iteração rápida + trajectory evals para confiança no
  workflow.

#### 2b — Brownfield (Feathers)

- **Michael Feathers — Working Effectively with Legacy Code.**
  https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/

  Onde entra: `docs/brownfield.md` codifica o Legacy Code
  Change Algorithm (identify change points → find seams →
  break dependencies → write characterization tests →
  change → refactor), técnicas Sprout / Wrap, e definição
  de legacy code como "código sem testes".

- **Daedtech — Characterization Tests (Feathers).**
  https://daedtech.com/characterization-tests/

  Onde entra: approval tests / golden master tests como
  ferramenta de safety net em brownfield.

#### 2c — Spec-Driven Development

- **Microsoft — Spec-First Approach to AI-Native Engineering.**
  https://developer.microsoft.com/blog/spec-driven-development-ai-native-engineering/

  Onde entra: SDD como prática mainstream enterprise em
  2025-2026. Spec Kit como toolkit de referência. Valida a
  decisão do harness de tratar SDD como workflow first-class
  via `archetypes/full-sdd-project.md`.

- **IBM — What is Spec-Driven Development?**
  https://www.ibm.com/think/topics/spec-driven-development

  Onde entra: metodologia SDD canônica — spec como source of
  truth, executable specifications, structured workflow.
  Sustenta o formato das cinco SPEC-NN em `docs/sdd.md`.

- **Allegro Tech Blog — Spec-Driven Development best practices.**
  https://blog.allegro.tech/2026/06/spec-driven-development-best-practices.html

  Onde entra: "ask for analysis and generation of a task list
  first", "keep tasks small and self-contained", "iterate on
  the spec". Validação prática das recomendações de
  `docs/sdd.md` e do template `task-plan.template.md`.

- **Martin Fowler — Exploring Gen-AI: SDD tools.**
  https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html

  Onde entra: panorama das ferramentas SDD atuais (Kiro,
  spec-kit); valida a abordagem do harness como ferramenta
  canônica.

### Camada 3 — Architecture Decision Records

- **AWS — Master ADRs best practices.**
  https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/

  Onde entra: `docs/adr-template.md` segue as recomendações
  AWS — uma decisão por ADR, log versionado, status
  rastreável, link para código.

- **Microsoft Azure — Maintain an ADR.**
  https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record

  Onde entra: ADRs começam no início do workload e continuam
  ao longo da vida; brownfield também recebe ADRs
  retroativos para decisões significativas passadas.

- **adr.github.io — Architectural Decision Records.**
  https://adr.github.io/

  Onde entra: comunidade canônica de ADRs; formato
  Context/Decision/Consequences é o padrão da indústria.

## Referências

A bibliografia completa (fontes primárias, ferramentas
relacionadas e documentação de plataforma) está em
`docs/references.md`. Cobre, além das cinco acima:

- Sensors / ferramentas citadas nos artigos
  (`sensors-cli`, Modularity Skills, Stryker,
  dependency-cruiser, ESLint plugin da Factory).
- Documentação oficial de Codex AGENTS.md, Codex Cloud,
  Claude Code memory e Claude Code hooks.

## Licença

Esta meta-arquitetura é distribuída para reutilização.
Verifique o arquivo `LICENSE` (se presente) ou entre em contato
para termos específicos.
