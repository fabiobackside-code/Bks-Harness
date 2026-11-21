# Ciclo de Feature (Fase 5) — BKS-SDD Reference

Comandos de listagem, mensagens ao usuário, registros de log e o fluxo da Fase 5. Os portões,
a decomposição em tasks e a definição de pronto estão no corpo do `SKILL.md`.

---

## Comando `--feature-list`

**Objetivo:** Mostrar o estado atual de todas as features do projeto em foco — FEAT, TEST e Tasks.

**Passo 5L.1 — Identificar o projeto em foco**

Verificar se há projetos com `PLAN-[nome].md` em `plan/`.
- Se houver apenas um projeto com plano, usá-lo automaticamente.
- Se houver múltiplos, listar e perguntar ao usuário qual deseja visualizar.

**Passo 5L.2 — Construir a tabela de status**

Para cada feature listada no `PLAN-[nome].md` §3, verificar:
- Existe `spec/features/FEAT-[nome].md`? → determinar o status pelo campo `**Status:**` do arquivo
- Existe `spec/tests/TEST-[nome].md`? → determinar o status pelo campo `**Status:**` do arquivo
- Existe `spec/tasks/TASK-[id]-*.md` referenciando esta feature? → contar tasks

Apresentar a tabela:

```
Projeto: project-[nome]
Plano: PLAN-[nome].md

ID  | Feature              | Fase | Prior. | FEAT        | TEST            | Tasks
----|----------------------|------|--------|-------------|-----------------|-------
F1  | [nome]               | F1   | P0     | ✅ Aprovada | ✅ Aprovada     | 4 tasks
F2  | [nome]               | F1   | P0     | ✅ Aprovada | ⛔ Não criado   | —
F3  | [nome]               | F2   | P1     | 📝 Draft    | ⛔ Não aplicável | —
F4  | [nome]               | F2   | P2     | ⏳ Pendente | ⛔ Não aplicável | —
```

Legenda de ícones:
- ✅ Aprovada — artefato existe e aprovado pelo usuário
- 📝 Draft — artefato criado mas ainda não aprovado
- ⛔ Não criado — FEAT aprovado mas TEST ainda não foi gerado (próxima ação necessária)
- ⛔ Não aplicável — FEAT não aprovado; TEST não pode ser criado ainda
- ⏸ Em execução — pelo menos uma task com status "Em execução"
- 🏁 Concluída — todos os critérios de aceite verificados
- ⏳ Pendente — ainda sem spec


## Comando `--feature-tests-list`

**Objetivo:** Mostrar o estado das test specs de todas as features do projeto em foco.

**Passo 5.2L.1 — Identificar o projeto em foco**

Mesmo comportamento das fases anteriores: um projeto → usa automaticamente; vários → pergunta.

**Passo 5.2L.2 — Construir a tabela de status**

Para cada feature listada no `PLAN-[nome].md` §3, verificar:
- Existe `spec/features/FEAT-[nome].md`? → qual o Status?
- Existe `spec/tests/TEST-[nome].md`? → qual o Status?

Apresentar a tabela:

```
Projeto: project-[nome]
Plano: PLAN-[nome].md

ID  | Feature                    | FEAT Status  | TEST Status       | Tasks
----|----------------------------|--------------|-------------------|-------
F1  | [nome]                     | ✅ Aprovada  | ✅ Aprovada       | 4 tasks
F2  | [nome]                     | ✅ Aprovada  | 📝 Draft          | —
F3  | [nome]                     | ✅ Aprovada  | ⛔ Não criado     | —
F4  | [nome]                     | 📝 Draft     | ⛔ Não aplicável  | —
F5  | [nome]                     | ⏳ Pendente  | ⛔ Não aplicável  | —
```

Legenda:
- ✅ Aprovada — artefato existe e foi aprovado pelo usuário
- 📝 Draft — artefato existe mas ainda não aprovado
- ⛔ Não criado — FEAT aprovado mas TEST ainda não foi gerado (ação necessária)
- ⛔ Não aplicável — FEAT não aprovado; TEST não pode ser criado ainda


## Mensagens de revisão

### FEAT (5.1)

> *"FEAT-[nome].md criado com status Draft. Revise especialmente:*
> *- §2 Critérios de Aceite — cada item deve ser binário e verificável*
> *- §3 Comportamentos de Borda — adicione casos específicos do seu domínio*
> *- §4 Restrições Técnicas — inclua limites arquiteturais relevantes*
> *- §5 Contratos de Dados — se TXC, verifique em cada ficha o que o `ValidateAsync` lê, a regra e a compensação*
>
> *Quando aprovado, me diga 'aprovado' e eu atualizo o status.*
> *Próximo passo após aprovação: `/bks-sdd --feature-tests` para criar os cenários de teste*
> *desta feature. O `--feature-task` só gera tasks após o TEST estar aprovado."*

### TEST (5.2)

> *"TEST-[nome].md criado com status Draft (Fase 5.2). Revise especialmente:*
> *- §2 Cenários Principais — cada critério de aceite do FEAT tem um cenário correspondente?*
> *- §3 Cenários de Borda — cada comportamento de borda do FEAT está coberto?*
> *- §4 Fora de Escopo — há casos que outro agente poderia implementar por engano?*
>
> *Quando aprovado, me diga 'aprovado' e eu atualizo o status para Aprovada.*
> *Após aprovação, execute `/bks-sdd --feature-task` (Fase 5.3) para gerar as tasks.*
> *O `--feature-task` só libera tasks quando este TEST estiver com Status: Aprovada."*

### Tasks geradas (5.3)

Orientar o usuário:
> *"[N] tasks geradas para F[N] — [nome]. A ordem respeita TDD: tasks de teste primeiro (RED),
> depois implementação (GREEN). Execute as tasks na sequência indicada pelas dependências.*
>
> *Próximo passo: `/bks-sdd --feature-list` para ver o estado geral do projeto, ou
> `/bks-sdd --feature` para especificar a próxima feature."*

## Tabela §6 do FEAT

```markdown
## 6. Tasks desta Feature

| ID | Descrição | Peça TXC (se TXC) | Tipo | Dependência |
|----|-----------|-------------------|------|-------------|
| TASK-001 | [descrição curta] | `PEDIDO.CRIAR` · `ValidateAsync` | Teste | nenhuma |
| TASK-002 | [descrição curta] | `PEDIDO.CRIAR` · `ValidateAsync` | Implementação | TASK-001 |
| TASK-003 | [descrição curta] | `PEDIDO.CRIAR` · `ApplyRule` | Teste | TASK-002 |
| TASK-004 | [descrição curta] | `PEDIDO.CRIAR` · `ApplyRule` | Implementação | TASK-003 |
```

## Fluxo completo

```
PLAN-[nome].md
    ↓
/bkhar:arch                             → ARCH + modelos      (aprovado pelo usuário)
    ↓
Fase 5.1 — /bks-sdd --feature          → FEAT-[nome].md      (Draft → Aprovada)
    ↓
Fase 5.2 — /bks-sdd --feature-tests    → TEST-[nome].md      (Draft → Aprovada)
    ↓
Fase 5.3 — /bks-sdd --feature-task     → TASK-[id]-*.md      (Pendente → em execução)
    ↓
Fase 6   — Implementação               → (a definir)
```

**Regras de bloqueio estrutural:**
- `--feature-tests` (5.2) só executa se existir FEAT com `Status: Aprovada`
- `--feature-task` (5.3) só executa se existir TEST com `Status: Aprovada`
- Não é possível pular sub-fases — a sequência 5.1 → 5.2 → 5.3 é estrutural

**Visibilidade do estado:**
- `/bks-sdd --feature-list` — visão geral de todas as features (FEAT + TEST + Tasks)
- `/bks-sdd --feature-tests-list` — foco específico no estado das test specs (Fase 5.2)
