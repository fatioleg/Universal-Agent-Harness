---
name: uah-init
description: "UAH-lite: prepara qualquer projeto (artigo, revisão de literatura, simulação molecular, software, edital) com o harness mínimo e proporcional ao risco: 5 arquivos (CLAUDE.md/AGENTS.md curtos, project.yaml, plan/approved.md, state/current.md), permissões e hooks do Claude Code compilados de H0–H3, gate de plano aprovado por humano (G1) e checkpoint de retomada (G4). Use quando o usuário disser \"/uah-init\", \"iniciar harness\", \"preparar projeto com UAH\", \"aprovar o plano\", \"checkpoint\", \"retomar o projeto\", \"status do UAH\", ou ao abrir um projeto que já tem .uah/. Integra, quando necessário, Workflow_Digestion (documentos → corpus → grafo → Obsidian), specboard (painel de validação de módulos) e CalcBoard (painel de cálculos). Subcomandos: (vazio)=init, approve, checkpoint, status, task, compile, explain, integrations."
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
| **calcboard** (`/calcboard`) | execução e validação | existem saídas de cálculo (ORCA, CP2K, VASP, Gaussian, QE, ASE): gere o painel antes de declarar um resultado aceito e anexe-o como evidência no checkpoint | não há cálculos |

Regras que o guard aplica às integrações:
- **workflow-digestion:** o `graphify` pede confirmação, porque a extração semântica custa muitos tokens. Proteja a pasta-fonte em `immutable_paths`.
- **specboard:** `review`/`verify` e `.specboard/verificacoes.jsonl` são só do humano. Antes da aprovação, o agente pode editar `.specboard/**` e rodar `specboard.py init|validate|queue|build|lock|amend`.
- **calcboard:** antes da aprovação, só `painel.py ler`. O `gerar` vem depois do approve.

## `/uah-init approve`

Revise com o usuário o `plan/approved.md` atual. Se ele aprovar, rode `python3 .uah/uah.py approve`.
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
