<!-- UAH:BEGIN — bloco gerado pelo UAH-lite; edite fora dos marcadores -->
## Harness do projeto (UAH-lite)

- **Retomar:** leia `state/current.md` e depois `plan/approved.md`. Confira com `python3 .uah/uah.py preflight`.
- **Fonte de verdade:** arquivos versionados > plano aprovado > memórias (Claude, OMC, ai-memory). Resumos de memória nunca substituem evidência.
- **Gate G1:** com risco medium/high, nenhuma alteração material antes de o plano ser aprovado por um humano (`/uah-init approve`). Mudar o corpo do plano reabre o gate.
- **Planejamento:** use a entrevista e o planejamento do OMC só quando houver lacunas reais. Importe o plano com `python3 .uah/uah.py import-plan <arquivo>`.
- **Checkpoint G4:** ao pausar, trocar de conta/máquina ou delegar, rode `python3 .uah/uah.py checkpoint --task T-xxx --status <active|paused|blocked|done> --next "..."`.
- **Política:** `.uah/policy.json` é gerada (não editar). Para mudar regras, edite `project.yaml` e rode `python3 .uah/uah.py compile`. Risco: **{{risk}}**.
- **Integrações:** as ativas aparecem no resumo do início da sessão, com quando e como usar. Para listar ou sugerir, rode `python3 .uah/uah.py integrations`. As regras efetivas ficam em `python3 .uah/uah.py explain`.
- Ações externas (push, publicação, envio de dados, sudo) pedem confirmação. Dados em `immutable_paths` não são alterados.
<!-- UAH:END -->
