# UAH-lite (v0.9.0)

Implementação mínima e executável da recomendação da auditoria de 11/10/2026: o UAH deixa de ser só
documentação e passa a **compilar** as regras H0–H3 para o ponto onde elas podem ser aplicadas de fato, ou seja,
as `permissions` e os hooks do Claude Code.

## O que é instalado em cada projeto

| Arquivo | Papel | Quem escreve |
|---|---|---|
| `CLAUDE.md` / `AGENTS.md` | entrypoint curto (bloco `UAH:BEGIN…END`; o conteúdo existente é preservado) | `uah.py init` |
| `project.yaml` | H2: identidade, risco, regras do projeto | humano (edição pede confirmação) |
| `plan/approved.md` | plano; o hash do corpo é a revisão aprovada | agente/OMC + aprovação humana |
| `state/current.md` | estado de retomada (tarefa, status, próxima ação, commit) | `uah.py checkpoint` |
| `.uah/` | runtime fixado: `uah.py`, `hooks/uah_guard.py`, perfis H0/H1, `policy.json`, `plan.lock.json`, `versions.json`, `omc-capabilities.lock.json` | `uah.py` (imutável para o agente) |
| `.claude/settings.json` | regras `permissions` + hooks `PreToolUse`, `SessionStart` (e `Stop` em risco alto) | `uah.py compile` (preserva o que já existia) |

Faça commit de tudo, inclusive `.uah/`. Não versione `.omc/`, que pode conter transcripts.

## Camadas

- **H0** `profiles/h0.json`: invariantes universais (não apagar raiz/home, não executar `curl | sh`, não usar force push; push, publicação, envio de dados e sudo pedem confirmação; aprovação de plano é humana).
- **H1** `profiles/risk-{low,medium,high}.json`: overlay escolhido pelo `risk` do projeto.
- **H2** `project.yaml → policy`: caminhos imutáveis/protegidos, regras extras, `settings_allow`, `grantable`.
- **H3** `.uah/task.yaml`: restrições da tarefa e concessões temporárias (no máximo 7 dias), só das listadas em `grantable`.

Resolução *fail-closed*: listas só crescem; o gate e o G4 só endurecem; `settings_allow` que conflite com deny/ask
superior, campo desconhecido ou regex inválida → `BLOQUEADO` e nada é escrito.

## Gates

- **G1:** com risco medium/high, antes de `approve` o agente só lê e edita `plan/`, `state/`, `project.yaml`, `CLAUDE.md`, `AGENTS.md` e `.omc/`. O hash vincula a aprovação à revisão: editar o plano reabre o gate.
- **G4:** em risco alto, o hook `Stop` impede encerrar a sessão (uma vez, sem loop) se houver alterações mais novas que `state/current.md`.

## Integração com OMC (por artefato, não por nome de comando)

`deep-interview` gera `.omc/specs/*.md` e `plan`/`ralplan` gera `.omc/plans/*.md`; `uah.py import-plan` copia o arquivo para
`plan/approved.md`, substituindo o caminho da home por `~`. `init` grava `omc capabilities lock` e o `preflight` roda `check`:
se o OMC mudar, o preflight avisa.

## Integrações (v0.7.0)

Catálogo em `skills/uah-init/integrations/*.json`, no formato de contrato de integração da §7 do relatório:
repositório, quando usar, quando não usar, etapa do fluxo, requisitos e regras próprias. Uma integração só entra
nas regras do projeto quando listada em `project.yaml → integrations`. A instalação é detectada pelo `SKILL.md`
da skill (`name:`), e o commit instalado é registrado. O estado instalado ou não fica fora do hash da política,
então a mesma política vale em máquinas diferentes.

| Integração | Etapa | Quando | Regras que acrescenta |
|---|---|---|---|
| [Workflow_Digestion](https://github.com/fatioleg/Workflow_Digestion) | descoberta | pasta com muitos documentos → corpus, grafo, vault do Obsidian | `graphify` pede confirmação (custo de tokens) |
| [specboard](https://github.com/fatioleg/specboard) | entre `import-plan` e `approve`; execução | projeto modular medium/high: módulos, contratos pré-registrados, fila de verificação humana | `review`/`verify` negados ao agente; `verificacoes.jsonl` imutável; `.specboard/**` e `specboard.py init/validate/queue/build/lock/amend` liberados antes da aprovação |
| [CalcBoard](https://github.com/fatioleg/CalcBoard) | execução e validação | saídas de ORCA, CP2K, VASP, Gaussian, QE, ASE | `painel.py ler` liberado antes da aprovação |
| [publish-documents](https://github.com/fatioleg/publish-documents) | execução e entrega | documento formatado em PDF/DOCX (relatório, artigo, parecer, proposta) via Quarto: perfis report-visual, journal-scientific e word-editable (técnico ou ABNT) | `quarto install/add/use` e `tlmgr install` pedem confirmação; `pubdoc.py preflight/doctor` liberados antes da aprovação |
| [sci-figures](https://github.com/fatioleg/sci-figures) | execução e entrega | figuras de publicação por especificação: moléculas 2D (RDKit ACS 1996), **moléculas 3D ray-traced (molar_vis: proteínas, docking, superfícies, MD)**, estruturas/cristais/superfícies (ASE), fluxogramas (D2), gráficos de dados (matplotlib), com manifesto e verificação | `figs.py setup` pede confirmação; `figs.py doctor` liberado antes da aprovação; `maturin develop` (Rust) para molecule-3d pede confirmação |

Comandos: `uah.py integrations` (lista + recomendações por `project.domains` e risco),
`integrations install <id>` (clona em `~/.claude/tools/` e liga a skill em `~/.claude/skills/`),
`integrations enable|disable <id>` (edita só a linha `integrations:` do `project.yaml`, preservando os comentários,
e recompila). `install` e `enable` pedem confirmação humana.
O Workflow_Digestion implementa, na prática, os contratos `markitdown-normalize`, `graphify-build` e
`obsidian-interface` de `contracts/tools/`.

## Fatias de MVP (v0.8.0)

Para projetos incrementais: `plan/approved.md` é o plano geral (aprovado uma vez) e `plan/slices/slice-N.md`
são fatias aprovadas uma a uma (`approve --slice N`, sempre com confirmação humana e exigindo o plano geral
aprovado). Depois da primeira fatia (`.uah/slices.lock.json` com `mode: true`), o gate G1 só libera execução com
uma fatia **ativa, aprovada e inalterada**. `slice done N` fecha o gate até a próxima fatia.

| Comando | Efeito |
|---|---|
| `import-plan .omc/plans/slice-N.md --slice N` | traz a fatia planejada pelo `omc-plan` (rascunho) |
| `slice new N [--title …]` | cria a fatia a partir do template SDD (REQ, AC, fora do escopo, testes, critério de abandono, agente executor) |
| `approve --slice N` | aprova e ativa a fatia |
| `slice` / `slice list` | estado de cada fatia e qual está ativa |
| `slice activate N` | troca a fatia ativa (o gate segue o estado de aprovação dela) |
| `slice done N` | conclui a fatia e fecha o gate até a próxima |

O `checkpoint` registra a fatia ativa e, com o specboard ativo, lembra de rodar `specboard.py validate && build`.
A `SKILL.md` traz um modelo de prompt para `/oh-my-claudecode:omc-plan --consensus` que pede só o plano da fatia,
porque o `omc-plan` não edita arquivos nem gera painéis antes da aprovação. O painel fica com o specboard, e a
orquestração com o bloco UAH no `CLAUDE.md`.

## `explain`

`uah.py explain` mostra as regras efetivas em linguagem simples: risco, gates, caminhos imutáveis e protegidos, o que
é negado, o que pede confirmação (com o id de origem, H0/H1/INT/H2/H3), o que está liberado e as integrações ativas.
Campos desconhecidos no `project.yaml` geram erro com sugestão de grafia (ex.: `risc` → `risk`).

## Instalação da skill

```bash
ln -s "$PWD/skills/uah-init" ~/.claude/skills/uah-init
```

## Testes

`python -m unittest discover -s tests -v`: 67 testes comportamentais (AT-01, 02, 03, 05, 07, 09, 14; 14 regressões da revisão independente; 11 de integrações; 7 de fatias; 10 da auditoria do Codex; 4 do setup-env; 5 de tentativas/custo) sem rede e sem LLM.
Verificado manualmente com Claude Code 2.1.296 (`claude -p`): o hook nega `Write` com o plano pendente e libera depois de `approve`.

## Integrações fixadas por commit (v0.8.3)

Cada entrada do catálogo tem `ref` (SHA de 40 caracteres, conferido pelo validador). O comando
`integrations install` clona o repositório, recusa um clone existente com remoto diferente e faz checkout
do `ref`. O status mostra se a skill instalada tem **origem verificada** (remoto git = repositório do
catálogo) e se o commit instalado é o fixado. Só as skills verificadas podem usar as CLIs liberadas antes da
aprovação (`gate_cli`). Para atualizar uma integração, publique-a, troque o `ref` no catálogo e rode os testes.

## Limites conhecidos

- A análise de Bash é heurística (`python -c`, `bash -c` e scripts não são inspecionados por dentro). É defesa contra deriva do agente, não contra um adversário.
- O Codex lê `AGENTS.md` e o estado, mas os hooks são do Claude Code. No Codex, o enforcement depende do sandbox/aprovação dele.
- Permissões temporárias existem só no hook (o Claude Code não tem expiração nativa).
- Windows nativo: use `--python python`; o OMC tem recursos só para Linux. WSL2 é recomendado.
