---
name: uah-init
description: "UAH-lite: prepara qualquer projeto (artigo, revisão de literatura, simulação molecular, software, edital) com o harness mínimo e proporcional ao risco: 5 arquivos (CLAUDE.md/AGENTS.md curtos, project.yaml, plan/approved.md, state/current.md), permissões e hooks do Claude Code compilados de H0–H3, gate de plano aprovado por humano (G1) e checkpoint de retomada (G4). Use quando o usuário disser \"/uah-init\", \"iniciar harness\", \"preparar projeto com UAH\", \"aprovar o plano\", \"checkpoint\", \"retomar o projeto\", \"status do UAH\", ou ao abrir um projeto que já tem .uah/. Integra, quando necessário, Workflow_Digestion (documentos → corpus → grafo → Obsidian), specboard (painel de validação de módulos), CalcBoard (painel de cálculos), publish-documents (PDF/DOCX profissional com Quarto) e sci-figures (figuras de publicação por especificação). Suporta desenvolvimento incremental por fatias de MVP (plano geral + slice-N aprovadas uma a uma, com omc-plan e specboard). Subcomandos: (vazio)=init, approve, checkpoint, status, task, compile, explain, integrations, slice."
---

# UAH-lite — harness mínimo por projeto

O UAH-lite **não orquestra**: a entrevista e o planejamento ficam com o OMC, a execução com o Claude Code/OMC.
Ele só (1) materializa o mínimo, (2) compila as regras H0–H3 em `permissions`/hooks do Claude Code,
(3) amarra a execução a um plano aprovado por humano e (4) mantém o estado de retomada no repositório.

CLI: `python3 ~/.claude/skills/uah-init/uah.py` antes do init; depois, a cópia fixada `python3 .uah/uah.py`.
Se o projeto declara `runtime.python` no `project.yaml` (ex.: `python` no Windows), use esse comando.

## Princípios que você deve seguir

- **Proporcionalidade:** não crie arquivos, agentes, entrevistas ou integrações além do necessário. Projeto trivial = risco `low`.
- **Não duplicar:** nada de entrevistador ou planejador próprio. Use `/oh-my-claudecode:deep-interview` e `/oh-my-claudecode:plan` (ou `ralplan`) **só quando houver lacunas reais**.
- **Fonte de verdade:** arquivos versionados > plano aprovado > memórias (Claude, OMC, ai-memory).
- **Aprovação é humana:** nunca rode `approve` nem `task --grant` sem o "sim" explícito do usuário na conversa. O hook pede confirmação de qualquer jeito.
- **Não contorne o guard.** Se o hook negar algo, relate e proponha o caminho legítimo (aprovar plano, editar `project.yaml` + compile, concessão H3).

## `/uah-init` (sem argumento): preparar o projeto

1. **Descoberta (G0, só leitura):** veja se já existe `.uah/`. Se existir, rode `python3 .uah/uah.py preflight`, resuma e pare (o projeto já está preparado). Se não existir, inspecione rapidamente README, CLAUDE.md, estrutura, dados e git.
2. **Risco:** proponha um nível com uma linha de justificativa e confirme com `AskUserQuestion`:
   - `low`: exploratório, descartável, sem dado original nem entregável formal. Sem gate.
   - `medium` (padrão): entregável real (artigo, análise, código, proposta). Gate G1.
   - `high`: resultado publicável/científico crítico, dados originais, dinheiro, terceiros. Gate G1, checkpoint G4 obrigatório e confirmação para instalar pacotes, usar ssh e qualquer `rm`.
3. **Init:** `python3 ~/.claude/skills/uah-init/uah.py init --risk <nível> --title "<título>" --domains <rótulos>` (acrescente `--python python` no Windows nativo).
   Use rótulos de domínio como `literatura`, `revisao-de-literatura`, `artigo-teorico`, `fomento`, `edital`, `quimica-computacional`, `modelagem-molecular`, `dft`, `materiais`, `software` e `sdd`. Eles orientam as recomendações de integração.
3b. **Integrações:** rode `python3 .uah/uah.py integrations`. Proponha só as marcadas RECOMENDADA que o projeto realmente usa, com `AskUserQuestion` (multiSelect).
   Com o "sim" do usuário: `python3 .uah/uah.py integrations enable <ids>` e, se necessário, `python3 .uah/uah.py integrations install <ids>` (clona o repositório do autor e cria a skill). Os dois comandos pedem confirmação humana. Depois de instalar, avise que é preciso reiniciar o Claude Code.
   Se faltarem ferramentas (Quarto, D2, ambiente Python do sci-figures), rode `python3 .uah/uah.py setup-env` para o relatório. Com o "sim" do usuário, `setup-env --install` instala sem sudo, em versão fixa e com checksum conferido. Para OMC, molar_vis e pacotes de sistema, repasse ao usuário os comandos que o relatório mostra.
4. **Proteções do projeto:** se houver dados brutos, PDFs-fonte ou resultados de referência, proponha `policy.immutable_paths` (ex.: `data/raw/**`) no `project.yaml` e rode `python3 .uah/uah.py compile`.
5. **Plano:**
   - Objetivo claro e pequeno: escreva você mesmo `plan/approved.md` seguindo o template (escopo, entregáveis com aceite, tarefas T-xxx com "pronto quando").
   - Ambíguo ou grande: rode `/oh-my-claudecode:deep-interview` (ambiguidade) e/ou `/oh-my-claudecode:plan`. Depois importe com `python3 .uah/uah.py import-plan .omc/plans/<arquivo>.md` (ou `.omc/specs/...`).
6. **Aprovação:** mostre o plano resumido e pergunte com `AskUserQuestion` (Aprovar / Revisar). Só com "Aprovar", rode `python3 .uah/uah.py approve`. O guard pede a confirmação humana do comando.
7. **Fechamento:** `python3 .uah/uah.py checkpoint --task T-001 --status active --next "<primeira ação>"`. Diga ao usuário quais arquivos foram criados e se deve fazer commit.

## Quando acionar cada integração (só se estiver ativa no projeto)

O resumo do início da sessão lista as integrações ativas e se estão instaladas. Não acione uma integração inativa: proponha ativá-la.

| Integração | Etapa | Acione quando | Não acione quando |
|---|---|---|---|
| **workflow-digestion** (`/workflow-digestion <pasta>`) | descoberta, antes do plano | há uma pasta com muitos documentos-fonte (PDF/DOCX/PPTX/planilhas) a transformar em corpus, grafo e vault do Obsidian para revisão de literatura, edital ou base de conhecimento | um ou poucos arquivos (use markitdown) ou só código |
| **specboard** (`/specboard`) | entre `import-plan` e `approve`, e a cada etapa executada | projeto modular em risco medium/high: o painel transforma o plano em módulos e contratos pré-registrados e serve de apoio para o humano aprovar. Durante a execução, marque as etapas como `executado` com evidência | projeto de tarefa única ou risco low |
| **publish-documents** (`/publish-documents`) | execução e entrega | o entregável é um documento formatado (relatório, artigo, parecer, proposta) em PDF/DOCX. Registre o perfil no plano; os portões de QA (preflight, verify, inspeção visual, aceite) viram critérios de aceite da fatia | nota rápida ou texto que fica só no repositório; edital em plataforma web |
| **sci-figures** (`/sci-figures`) | execução e entrega | o projeto precisa de figuras de publicação (moléculas, estruturas, superfícies, fluxogramas, gráficos de dados). Toda figura de dados nasce de arquivo de dados e script; `verify` sem FAIL e a folha de contato inspecionada viram critérios de aceite | captura de tela ou ilustração artística; painel interativo de cálculos (CalcBoard) |
| **calcboard** (`/calcboard`) | execução e validação | existem saídas de cálculo (ORCA, CP2K, VASP, Gaussian, QE, ASE): gere o painel antes de declarar um resultado aceito e anexe-o como evidência no checkpoint | não há cálculos |

Regras que o guard aplica às integrações:
- **workflow-digestion:** o `graphify` pede confirmação, porque a extração semântica custa muitos tokens. Proteja a pasta-fonte em `immutable_paths`.
- **specboard:** `review`/`verify` e `.specboard/verificacoes.jsonl` são só do humano. Antes da aprovação, o agente pode editar `.specboard/**` e rodar `specboard.py init|validate|queue|build|lock|amend`.
- **calcboard:** antes da aprovação, só `painel.py ler`. O `gerar` vem depois do approve.

## Fatias de MVP (SDD incremental): `/uah-init slice`

Use quando o projeto avança em incrementos: um **plano geral** (`plan/approved.md`, aprovado uma vez) e
**fatias** (`plan/slices/slice-N.md`), cada uma aprovada antes de ser implementada. Depois da primeira fatia,
o guard só libera execução se houver uma fatia **ativa, aprovada e inalterada**.

Fluxo de cada fatia:
1. **Planejar com o OMC (só planejamento).** O `omc-plan` não edita arquivos nem gera painéis antes da aprovação, então peça apenas o plano da fatia. Modelo de prompt (troque N):
   ```
   /oh-my-claudecode:omc-plan --consensus "Crie .omc/plans/slice-N.md: a fatia N (MVP) do plano geral em
   .omc/plans/, coerente com a spec da deep-interview em .omc/specs/ e com o ADR do planejamento prévio.
   Formato SDD: objetivo da fatia; depende de; dentro e fora do escopo; requisitos REQ-N.x; critérios de
   aceite AC-N.x ligados aos REQ; contratos/interfaces; plano de testes; critério de abandono; tarefas
   T-N.x com 'pronto quando'; agente executor sugerido (designer para UI, executor para o resto)."
   ```
   Sem o OMC, crie a fatia com `python3 .uah/uah.py slice new N --title "..."`. O template já traz as seções SDD.
2. **Trazer para o UAH:** `python3 .uah/uah.py import-plan .omc/plans/slice-N.md --slice N`.
3. **Painel (se o specboard estiver ativo):** rode `/specboard` para refletir a fatia como módulo(s), com contratos e etapas. Mostre o painel ao usuário para apoiar a revisão.
4. **Aprovar:** pergunte com `AskUserQuestion`. Com o "sim", rode `python3 .uah/uah.py approve --slice N`. A fatia fica ativa e o guard pede confirmação humana.
5. **Executar:** delegue ao agente indicado na fatia. Use o `designer` do OMC **só para interface/UI**. Para código, dados ou cálculo, use o `executor`; para texto, o `writer`. A cada etapa, faça `checkpoint` e, com o specboard ativo, `specboard.py validate && build`, marcando a etapa como `executado` com evidência. O usuário faz `review`/`verify`.
6. **Encerrar a fatia:** quando todos os AC estiverem verificados pelo usuário, rode `python3 .uah/uah.py slice done N`. O gate fecha até a próxima fatia ser aprovada.

Para ver o estado das fatias: `python3 .uah/uah.py slice`. A fatia ativa e o estado dela aparecem no resumo do início da sessão.

**O CLAUDE.md não vira orquestrador:** memória, contexto, estado, regras, skills e integrações já chegam pelo bloco UAH, pelo `state/current.md` e pelo resumo da sessão. Mantenha o `CLAUDE.md` curto. Se o usuário quiser um mapa de agentes/skills do projeto, crie `docs/agentes.md` e aponte para ele em uma linha.

## Nível de raciocínio, tentativas e custo (sem orquestrador extra)

O OMC executa e escolhe agentes; o UAH só impõe **restrições**. Cada tarefa do plano ou da fatia tem
`nível: leve | padrão | crítico`. Delegue conforme o nível, usando os agentes do OMC, que já têm modelo fixo:

| Nível | Quando | Como executar |
|---|---|---|
| `leve` | busca, extração, conversão, formatação, contagem | **ferramenta determinística primeiro** (script, RDKit, grep, pubdoc, figs). Se precisar de modelo: `explore` ou `writer` (Haiku) |
| `padrão` | código, análise, síntese, figuras, textos técnicos | `executor`, `scientist`, `debugger`, `test-engineer`, `designer` (só UI) ou `document-specialist` (Sonnet); valide com `verifier` |
| `crítico` | decisão científica, fundamentação teórica, arquitetura, resultado publicável | `analyst`, `architect` ou `critic` (Opus) **+ revisão independente** (`code-reviewer` ou `kd-peer-review`) |

O nível pode subir se a tarefa se mostrar mais difícil. Uma tarefa "simples" que decide um resultado científico é `crítico`.

**Tentativas.** Quando o verify ou os testes de uma tarefa reprovarem, registre:
`python3 .uah/uah.py checkpoint --task T-x --status active --next "…" --failed "motivo" --level <nível>`.
Ao atingir o limite do risco (low 5, medium 3, high 2; o `project.yaml` pode reduzir com `policy.max_attempts`), a
tarefa fica **bloqueada**: o guard nega alterações materiais. **Pare** e leve ao usuário as opções: replanejar,
subir o nível ou abandonar. O desbloqueio (`--reset-attempts`) é decisão humana e pede confirmação.

**Custo por tarefa validada.** Ao concluir uma tarefa que passou na verificação, registre:
`checkpoint --task T-x --status done --next "…" --level <nível> --cost <USD do /cost> [--tokens N]`.
O `preflight` mostra as tarefas validadas, as tentativas médias e o custo por tarefa validada, que é a métrica que
importa: um modelo barato que falha repetidamente pode sair mais caro.

## `/uah-init approve`

Revise com o usuário o `plan/approved.md` atual (ou a fatia: `plan/slices/slice-N.md`). Se ele aprovar, rode `python3 .uah/uah.py approve` (ou `approve --slice N`).
Se o comando recusar o plano por estar incompleto, complete o plano. Use `--allow-incomplete` somente se o usuário pedir explicitamente; a exceção fica registrada.
Qualquer edição posterior no corpo do plano reabre o gate até a nova aprovação.

## `/uah-init checkpoint` (gate G4)

Use antes de encerrar a sessão, trocar de conta/máquina, delegar ou quando o hook Stop pedir:
`python3 .uah/uah.py checkpoint --task T-xxx --status <active|paused|blocked|done> --next "<próxima ação delimitada>" [--blocker "..."] [--note "..."]`.
Escreva `next_action` para que outro agente sem este contexto saiba exatamente o que fazer. Depois, sugira commit.

## `/uah-init explain`

Rode `python3 .uah/uah.py explain` para mostrar em linguagem simples o que está bloqueado, o que pede confirmação, o que está liberado e de que camada vem cada regra (H0, H1, INT, H2, H3). Use quando o usuário perguntar "o que o UAH bloqueia aqui?" ou quando um bloqueio surpreender.

## `/uah-init status` ou ao retomar

`python3 .uah/uah.py preflight`. Leia `state/current.md` e `plan/approved.md`, confira o `workspace_commit` com o git
e relate: tarefa ativa, próxima ação, bloqueios e avisos (`FAIL`/`WARN`). Resolva os `FAIL` antes de trabalhar.

## `/uah-init task` (contexto H3 e concessões temporárias)

- Restringir para uma tarefa: edite as regras em `.uah/task.yaml` com o comando `task`, que só aceita restrições.
- Concessão temporária (ex.: liberar `git push origin feat/...` por 4 h): ela precisa existir em `policy.grantable` do `project.yaml` (editar esse arquivo pede confirmação). Depois, com o "sim" do usuário: `python3 .uah/uah.py task --id T-xxx --grant <id> --hours 4`.
- Limpar: `python3 .uah/uah.py task --clear`.

## O que o UAH-lite não faz (de propósito)

Não cria banco vetorial, grafo, scheduler, memória própria, catálogo de plugins nem equipe de agentes.
Paralelismo: `/team` ou `omc team` com worktrees. ai-memory: opcional e desligado.
A análise de Bash do guard é heurística: é defesa contra deriva do agente, não contra um adversário. Ações críticas continuam exigindo revisão humana.
