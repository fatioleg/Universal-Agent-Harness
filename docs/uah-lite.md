# UAH-lite (v0.6.0)

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

## Instalação da skill

```bash
ln -s "$PWD/skills/uah-init" ~/.claude/skills/uah-init
```

## Testes

`python -m unittest discover -s tests -v`: testes comportamentais (AT-01, 02, 03, 05, 07, 09, 14) sem rede e sem LLM.
Verificado manualmente com Claude Code 2.1.296 (`claude -p`): o hook nega `Write` com o plano pendente e libera depois de `approve`.

## Limites conhecidos

- A análise de Bash é heurística (`python -c`, `bash -c` e scripts não são inspecionados por dentro). É defesa contra deriva do agente, não contra um adversário.
- O Codex lê `AGENTS.md` e o estado, mas os hooks são do Claude Code. No Codex, o enforcement depende do sandbox/aprovação dele.
- Permissões temporárias existem só no hook (o Claude Code não tem expiração nativa).
- Windows nativo: use `--python python`; o OMC tem recursos só para Linux. WSL2 é recomendado.
