# Modelos de arquivo do workspace — BKS-SDD Reference

Conteúdo inicial dos arquivos criados nas Fases 0 e 2 e o formato da entrada de log de cada
comando. Toda entrada de log é seguida de snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

---

## Fase 0 — arquivos do workspace

**Arquivo `.logs/session-[YYYY-MM-DD].md`** — criar com:
```markdown
# Log de Sessão — [YYYY-MM-DD]

## Sessão iniciada: [YYYY-MM-DDTHH:MM]
- Comando: /bks-sdd
- Ação: Criação do workspace `workspace-[nome]`
- Resultado: Estrutura criada com sucesso
```

**Arquivo `.states/state-initial-[YYYY-MM-DDTHH-MM].md`** — criar com:
```markdown
# Estado Inicial — [YYYY-MM-DDTHH:MM]

**Workspace:** workspace-[nome]
**Fase ativa:** 0 — Bootstrap concluído
**Próximo passo sugerido:** Adicionar arquivos de pesquisa em `research/` e executar `/bks-sdd --prd`

## Contexto da sessão
[Resumo do que foi declarado pelo usuário nesta sessão — objetivos, restrições, produto em mente]

## Estrutura criada
- `.logs/` — logs de sessão por data
- `.states/` — snapshots de estado para continuidade entre sessões
- `research/` — pesquisa e inputs primários para gerar o PRD
- `plan/` — plano macro do workspace (gerado futuramente)
- `projects/` — projetos internos com ciclos RPI próprios

## Questões em aberto
[Qualquer dúvida ou gap não resolvido na conversa até aqui]
```

**Arquivo `research/links.md`** — criar com:
```markdown
# Links de Referência

> Adicione aqui URLs que deseja usar como referência para gerar o PRD.
> Um link por linha. Exemplo:
> - https://exemplo.com/artigo

```

## Fase 2 — arquivos do projeto

**Arquivo `research/links.md`** — criar com:
```markdown
# Links de Referência — project-[nome-do-projeto]

> Adicione aqui URLs que deseja usar como referência para gerar o PRD deste projeto.
> Um link por linha. Exemplo:
> - https://exemplo.com/artigo

```

**Arquivo `research/stack.md`** — criar com os campos de stack coletados no Passo 2.1:
```markdown
# Stack — project-[nome-do-projeto]

**Framework:** [valor declarado]
**TypeScript Backend:** [valor declarado — apenas se Framework = TypeScript; omitir caso contrário]
**Database:** [valor declarado]
**Mensageria:** [valor declarado]

> Este arquivo é a fonte de verdade da stack tecnológica do projeto.
> Os campos aqui são herdados pela Fase 6 (--impl-init) para gerar o contrato de implementação.
> Atualize antes de executar --impl-init se algum campo mudar.
```

# Entradas de log por comando

## `--prd`
```
- [HH:MM] Comando: /bks-sdd --prd
  Inputs lidos: [lista de arquivos e URLs]
  Resultado: PRD.md gerado em research/
  Gaps identificados: [sim/não — quais]
```

## `--project`
```
- [HH:MM] Comando: /bks-sdd --project
  Projeto criado: project-[nome-do-projeto]
  Stack: Framework=[...] / Database=[...] / Mensageria=[...]
  Resultado: Estrutura RPI criada em projects/project-[nome-do-projeto]/
```

## `--project-prd`
```
- [HH:MM] Comando: /bks-sdd --project-prd
  Projeto: project-[nome-do-projeto]
  Inputs lidos: [lista de arquivos e URLs]
  Resultado: PRD-[nome-do-projeto].md gerado em projects/project-[nome]/research/
  Gaps identificados: [sim/não — quais]
```

## `--project-plan`
```
- [HH:MM] Comando: /bks-sdd --project-plan
  Projeto: project-[nome-do-projeto]
  PRD lido: PRD-[nome-do-projeto].md
  Resultado: PLAN-[nome-do-projeto].md gerado em projects/project-[nome]/plan/
  Features previstas: [N] features listadas
  Questões em aberto: [N]
```

## `--feature`
```
- [HH:MM] Comando: /bks-sdd --feature
  Projeto: project-[nome]
  Feature especificada: F[N] — [nome da feature]
  Arquivo: spec/features/FEAT-[nome].md
  Status: Aprovada
```

## `--feature-tests`
```
- [HH:MM] Comando: /bks-sdd --feature-tests (Fase 5.2)
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  FEAT lido: spec/features/FEAT-[nome].md (Status: Aprovada)
  Resultado: spec/tests/TEST-[nome].md gerado
  Status: Aprovada
  Cenários principais: [N] (cobre [N] critérios de aceite)
  Cenários de borda: [N]
```

## `--feature-task`
```
- [HH:MM] Comando: /bks-sdd --feature-task
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  TEST referenciado: spec/tests/TEST-[nome].md (Status: Aprovada)
  Tasks geradas: TASK-[001..N]
  Arquivos criados: spec/tasks/TASK-[id]-*.md (N arquivos)
```
