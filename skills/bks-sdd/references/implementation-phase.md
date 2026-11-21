# Implementação (Fase 6) — BKS-SDD Reference

Comandos `--impl-init`, `--task-run`, `--task-done`, `--status` e `--task-list`, com modelos de
IMPL e OUTPUT, caminhos de verificação e edge cases.

---

## Visão geral

> **Um motor só.** Em projeto `bkhar`, as tasks rodam pelo `/bkhar:loop`. Os comandos abaixo
> (`--impl-init`, `--task-run`) valem para o workspace avulso, com o código gerado na própria sessão.

A Fase 6 é o ciclo de execução das tasks geradas na Fase 5.3. Diferente das fases anteriores,
ela **executa e verifica** — não apenas específica. A skill age como orquestrador de execução.

**Pré-condições:**
- Projeto com `PLAN-[nome].md` aprovado (Fase 4) e arquitetura aprovada (`/bkhar:arch`)
- Pelo menos uma feature com `FEAT-[nome].md` + `TEST-[nome].md` aprovados (Fases 5.1 e 5.2)
- Pelo menos uma `TASK-[id].md` gerada (Fase 5.3)
- Stack declarada em `research/stack.md` do projeto (coletada no `--project`, Fase 2)

**Estrutura `spec/output/` (D2):**
```
spec/output/
├── results/
│   ├── IMPL-[feature].md          ← contrato de stack (gerado no --impl-init)
│   └── OUTPUT-TASK-[id].md        ← log de execução por task
└── code/
    └── [feature]/
        └── [arquivos gerados]     ← código-fonte; preenchido apenas no Modo Agente
```

> O rastreamento de progresso das tasks é feito via `TodoWrite` (não em arquivo PROGRESS-*.md).
> O `--status` lê o estado diretamente do `TodoWrite` — sem leitura de arquivos adicionais.

- `results/` é sempre preenchido, independente do modo de execução
- `code/` só é preenchido no **Modo Agente** (`--agent`); no Modo Contexto (`--context`) fica vazio
- O código em `code/` é staging temporário — o desenvolvedor move para o repositório real quando aprovado
- O workspace **nunca substitui o repositório real**

**Campo de agente nas tasks (D3):**

Cada task recebe o campo:
```markdown
**Agente:** implementador   ← valores: orquestrador | implementador | validador
```
Mapeamento PBQ (framework Harness Engineering):
- `orquestrador` — coordena, não implementa; gerência dependências e ordem
- `implementador` — escreve código; não escreve nem edita o teste do `validador`
- `validador` — escreve o RED das tasks de tipo `Teste`, verifica critérios de aceite, roda checklist do TEST spec

---

### Comando `--impl-init` — Inicializar ciclo de implementação

**Trigger:** `/bks-sdd --impl-init`

**Objetivo:** Preparar o contexto de implementação para uma feature. Gera o `IMPL-[feature].md`
com o contrato de stack e inicializa as tasks no `TodoWrite`.

**Fluxo:**

**Passo 6I.1 — Identificar o projeto em foco**

Mesmo comportamento das fases anteriores: um projeto → usa automaticamente; vários → pergunta.

**Passo 6I.2 — Listar features prontas para implementação**

Verificar quais features têm `TASK-[id].md` em `spec/tasks/` com status `Pendente`.
Apresentar ao usuário:

> *"Features prontas para implementação (com tasks pendentes):*
> *F1 — [nome] (3 tasks pendentes)*
> *F2 — [nome] (4 tasks pendentes)*
> *Qual deseja iniciar?"*

Se nenhuma feature tiver tasks pendentes:
> *"Não encontrei features com tasks pendentes. Execute `/bks-sdd --feature-task` (Fase 5.3)
> para gerar tasks antes de iniciar a implementação."*

**Passo 6I.3 — Ler a stack do projeto**

Ler `research/stack.md` do projeto. Extrair Framework, Database e Mensageria.

Se `stack.md` não existir ou tiver campos `A definir`, perguntar ao usuário os campos em falta
e **atualizar o arquivo `research/stack.md` com as respostas** antes de prosseguir.
Não perguntar campos já preenchidos.

**Passo 6I.4 — Identificar skill de implementação**

Mapear o Framework para a skill correspondente:
- `.NET` → `bks-dotnet-solutions`
- `Spring (Java/Kotlin)` → `bks-spring-solutions` *(ainda não disponível)*
- `TypeScript (Node.js)` → `bks-typescript-solutions`
- `Go` → `bks-go-solutions` *(ainda não disponível)*

Se a skill de implementação não estiver disponível para o framework declarado:
- Definir modo padrão automaticamente como **Modo Contexto** (`--context`)
- Informar ao usuário (não perguntar — comportamento é automático):
  > *"A skill de implementação para [Framework] ainda não está disponível. O ciclo desta feature
  > usará Modo Contexto — pacotes de contexto para execução externa."*
- Pular o Passo 6I.5 (modo já definido)

**Passo 6I.5 — Definir modo de execução padrão** *(executar somente se skill disponível)*

Perguntar ao usuário:

> *"Qual modo de execução padrão para esta feature?*
> *`1` Modo Agente (`--agent`) — Claude gera o código diretamente em `spec/output/code/`*
> *`2` Modo Contexto (`--context`) — Claude monta pacote de contexto para agente externo"*

Aguardar resposta. O modo padrão pode ser sobrescrito por task no `--task-run`.

**Passo 6I.6 — Gerar IMPL-[feature].md**

Criar `spec/output/results/IMPL-[feature-kebab].md`:
```markdown
# IMPL — [Nome da Feature]

**Feature:** F[N] — [nome]
**Projeto:** project-[nome]
**Criado:** [data]
**Atualizado:** [data]

## Stack

**Framework:** [valor]
**Database:** [valor]
**Mensageria:** [valor]
**Skill de implementação:** [skill ou "Não disponível — usar Modo Contexto"]

## Modo de execução padrão

[Agente | Contexto]

## Agente padrão do ciclo

[orquestrador | implementador | validador]

## Tasks em ordem de execução

| ID | Descrição | Tipo | Agente | Dependência |
|----|-----------|------|--------|-------------|
| TASK-001 | [desc] | Teste | validador | — |
| TASK-002 | [desc] | Impl. | implementador | TASK-001 |
...

## Observações
[Qualquer restrição específica desta feature para implementação]
```

**Passo 6I.7 — Inicializar tasks no TodoWrite**

Usar `TodoWrite` para registrar todas as tasks da feature com status `pending`:
- Para cada task em `spec/tasks/` da feature (na ordem de execução do IMPL-[feature].md):
  - `content`: `"[TASK-id] — [descrição curta]"` (forma imperativa)
  - `activeForm`: `"Executando [TASK-id] — [descrição curta]"`
  - `status`: `pending`

Isso inicializa o rastreamento visual de progresso — nenhum arquivo PROGRESS-*.md é criado.

**Passo 6I.8 — Registrar no log e orientar**

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --impl-init
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  Stack: Framework=[...] / Database=[...] / Mensageria=[...]
  Modo padrão: [Agente|Contexto]
  Tasks: [N] tarefas listadas em ordem de execução
  Artefatos: IMPL-[feature].md; tasks inicializadas no TodoWrite
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

Orientar o usuário:
> *"IMPL-[feature].md criado. Ciclo de implementação iniciado para F[N] — [nome].*
> *[N] tasks pendentes. Próximo passo: `/bks-sdd --task-run TASK-001` para iniciar a primeira task.*
> *Se encerrar a sessão antes de terminar, use `/bks-sdd --continue` na próxima sessão — o estado será recuperado automaticamente."*

---

### Comando `--task-run` — Executar uma task

**Trigger:** `/bks-sdd --task-run [TASK-id]` ou `/bks-sdd --task-run [TASK-id] --agent` ou `--context`

**Objetivo:** Iniciar a execução de uma task específica. Monta o contexto completo e executa
no modo configurado.

**Passo 6R.1 — Verificar pré-condições**

Verificar se existe `IMPL-[feature].md` correspondente à feature da task em `spec/output/results/`.
Se não existir:
> *"Não encontrei contrato de implementação para esta feature. Execute `/bks-sdd --impl-init`
> antes de rodar tasks de implementação."*

**Passo 6R.2 — Ler a task e verificar dependências**

Ler `TASK-[id].md` integralmente.

Se a task tem campo `**Dependência:**` preenchido, verificar se a task dependente está com
status `completed` no `TodoWrite`:
> *"TASK-[id] depende de TASK-[dep] que ainda não foi concluída.*
> *Conclua a tarefa dependente antes de continuar."*

**Passo 6R.3 — Determinar modo de execução**

- Se flag `--agent` fornecida: usar Modo Agente
- Se flag `--context` fornecida: usar Modo Contexto
- Se nenhuma flag: ler o campo `**Modo de execução padrão:**` em `spec/output/results/IMPL-[feature].md` e usar esse valor

**Passo 6R.4 — Atualizar status**

Atualizar `TASK-[id].md`: campo `**Status:**` → `Em execução`
Atualizar o `TodoWrite`: marcar a task `[TASK-id] — [descrição]` como `in_progress`

**Passo 6R.5 — Executar no modo definido**

**Modo Agente (`--agent`):**

Usar a tool `Agent` para isolar o contexto do implementador. O subagente recebe apenas os
artefatos necessários — sem o histórico completo da sessão principal.

Construir o prompt do subagente com:
1. Conteúdo completo de `TASK-[id].md`
2. Conteúdo completo de `FEAT-[feature].md`
3. Conteúdo completo de `TEST-[feature].md`
4. Seção Stack do `IMPL-[feature].md`
5. Instrução de caminho de saída: `spec/output/code/[feature]/`
6. Se skill de implementação disponível: instrução para seguir convenções da skill de stack

Seleção de modelo para o subagente:
- `sonnet` — tasks de lógica complexa, domínio, integrações
- `haiku` — tasks operacionais simples (estrutura de pastas, boilerplate, configs)

O subagente gera os arquivos em `spec/output/code/[feature]/` e retorna lista dos artefatos criados.

Ao receber o resultado do subagente:
> *"Execução concluída. Arquivos gerados em `spec/output/code/[feature]/`:*
> *- [lista de arquivos retornada pelo subagente]*
> *Execute `/bks-sdd --task-done TASK-[id]` para confirmar com o checklist do TEST spec."*

**Modo Contexto (`--context`):**

Montar e exibir o pacote de contexto:
```
Pacote TASK-[id]:
→ Stack: [Framework] / [Database] / [Mensageria]
→ Feature: F[N] — [nome]
→ Instrução: [instrução completa da task]
→ Agente: [valor do campo Agente da task]
→ Caminho esperado: [derivado da arquitetura do projeto]
→ Contrato de teste (cenários relevantes):
   - [cenário 1 do TEST-[nome].md]
   - [cenário de borda relevante]
→ Critério de aceite:
   - [checklist da task]
→ Dependências: [tasks concluídas que esta task consome]

Execute a implementação externamente e retorne com `/bks-sdd --task-done TASK-[id]`
para validar com o checklist do TEST spec.
```

**Passo 6R.6 — Gerar OUTPUT-TASK-[id].md**

Criar `spec/output/results/OUTPUT-TASK-[id].md`:
```markdown
# OUTPUT — TASK-[id]

**Task:** TASK-[id] — [descrição]
**Feature:** F[N] — [nome]
**Modo:** [Agente | Contexto]
**Iniciado:** [timestamp]
**Status:** Em execução

## Resultado da execução

[Modo Agente: lista de arquivos gerados]
[Modo Contexto: pacote de contexto montado]

## Checklist de verificação (preenchido no --task-done)

[a preencher]
```

---

### Comando `--task-done` — Marcar task como concluída

**Trigger:** `/bks-sdd --task-done [TASK-id]`

**Objetivo:** Fechar o ciclo de uma task executada. Implementa o Sensor do Harness Engineering.
O comportamento bifurca conforme o modo em que a task foi executada: **Modo Agente** (verificação
automática interna, sem interação humana) ou **Modo Contexto** (checklist interativo, aguarda
confirmação do usuário).

**Passo 6D.1 — Verificar status da task**

Verificar se `TASK-[id].md` tem status `Em execução`.
Se não:
> *"TASK-[id] não está com status 'Em execução'. Execute `/bks-sdd --task-run TASK-[id]`
> antes de marcar como concluída."*

**Passo 6D.2 — Ler TEST spec, cenários relevantes e determinar modo**

1. Ler `TEST-[nome].md` (campo `**Test Spec:**` da task).
2. Identificar os cenários do TEST relevantes à instrução desta task (por proximidade semântica).
3. Ler o campo `**Modo:**` em `spec/output/results/OUTPUT-TASK-[id].md`.
   - Se `Modo: Agente` → seguir o caminho **6D.3A** (verificação automática)
   - Se `Modo: Contexto` → seguir o caminho **6D.3C** (checklist interativo)

**Passo 6D.2E — Validação opcional no sandbox E2B** *(executar antes de qualquer verificação se E2B MCP disponível)*

Se E2B MCP estiver disponível no ambiente:
1. Verificar se a stack do projeto tem sandbox E2B compatível:
   - `.NET` → `dotnet` | `TypeScript/Node.js` → `node` | `Spring (Java)` → `java` | `Go` → `go`
2. Se stack compatível, perguntar ao usuário:
   > *"E2B MCP detectado. Deseja executar a suite de testes no sandbox antes de confirmar os cenários? (s/n)"*
3. Se usuário confirma `s`:
   - Executar no sandbox E2B: build + testes da stack declarada no projeto
   - Registrar resultado no cabeçalho de `TASK-[id].md`:
     ```
     **E2B Sandbox:** pass | fail — [output resumido em 1-2 linhas]
     ```
   - Se resultado = `fail`:
     > *"⚠️ Sandbox E2B retornou falha. Corrija o código antes de prosseguir.*
     > *Output: [output resumido]*
     > *Execute `/bks-sdd --task-done TASK-[id]` novamente após a correção."*
     - Interromper o fluxo (não apresentar checklist de TCs).
   - Se resultado = `pass`: registrar e prosseguir para o caminho 6D.3A ou 6D.3C normalmente.
4. Se usuário responde `n`: prosseguir diretamente para o caminho definido no Passo 6D.2.

Se E2B MCP indisponível, retornar erro ou stack sem sandbox compatível:
- Registrar no log: *"E2B MCP indisponível — passo de sandbox omitido"*
- Prosseguir diretamente para 6D.3A ou 6D.3C. Nenhum erro exibido ao usuário.

---

#### Caminho Modo Agente — Verificação automática

**Passo 6D.3A — Verificar internamente a cobertura dos cenários**

Sem interação com o usuário. Ler os arquivos gerados em `spec/output/code/[feature]/` e
verificar se cada cenário relevante do TEST spec está coberto pela implementação produzida
no `--task-run`:

- Para cada cenário: verificar se existe implementação correspondente nos arquivos gerados
  (by naming, structure, or logic match)
- Construir internamente a lista: `cenários cobertos` vs `cenários ausentes ou incompletos`

**Passo 6D.3B — Verificar a documentação de entrega** *(obrigatório, os dois modos)*

A regra está no corpo do `SKILL.md`, seção "Definição de pronto". Aplicar antes de marcar a
task como concluída.

---

**Passo 6D.4A-ok — Todos os cenários cobertos (Agente, Sucesso)**

1. Atualizar `TASK-[id].md`: `**Status:**` → `Concluída`
2. Marcar a task como `completed` no `TodoWrite`
3. Atualizar `OUTPUT-TASK-[id].md`: timestamp de conclusão + lista de cenários verificados + `Status: Concluída`
4. Verificar se todas as tasks da feature foram concluídas (todas `completed` no TodoWrite):
   - Se sim: atualizar `FEAT-[nome].md` `**Status:**` → `Concluída`
5. Registrar no log e salvar snapshot.
6. **Sem pausas.** Avançar diretamente: verificar a próxima task `pending` no TodoWrite e
   chamar internamente `--task-run TASK-[próxima]` se houver dependências resolvidas. Informar:
   > *"✅ TASK-[id] concluída automaticamente. Progresso: [X/N tasks]. Iniciando TASK-[próxima]..."*

**Passo 6D.4A-fail — Algum cenário não coberto (Agente, Falha)**

1. Manter status `Em execução`
2. Registrar no `OUTPUT-TASK-[id].md`: quais cenários não foram cobertos + gap identificado
3. Tentar autocorreção: se o gap for localizado (um arquivo ou função ausente), gerar a correção
   em `spec/output/code/[feature]/` e repetir o passo 6D.3A
4. Se após autocorreção o cenário ainda falhar, **interromper e informar o usuário**:
   > *"⚠️ TASK-[id] — gap não resolvido automaticamente.*
   > *Cenário: [nome do cenário]*
   > *Gap: [descrição precisa do que está faltando]*
   > *Arquivos gerados estão em `spec/output/code/[feature]/`. Corrija e execute*
   > *`/bks-sdd --task-done TASK-[id]` para revalidar."*

---

#### Caminho Modo Contexto — Checklist interativo

**Passo 6D.3C — Apresentar checklist interativo**

> *"Antes de marcar TASK-[id] como concluída, confirme os cenários do TEST-[nome].md:*
>
> *☐ Cenário 1 — [nome]: passou?*
> *☐ E1 — [edge case]: passou?*
> *☐ E3 — [edge case]: passou?*
> *☐ `README.md` e `ARCHITECTURE.md` atualizados com o que esta task produziu?*
>
> *Responda 'sim' para cada um, ou informe qual falhou e o motivo."*

O item de documentação **não é opcional** e vale para toda task que tocou tipo público, função
pública ou decisão estrutural — ver Passo 6D.3B. Se o usuário responder que não, **gerar ou
atualizar os arquivos antes de fechar a task**, não apenas registrar o gap.

Aguardar resposta do usuário antes de prosseguir.

**Passo 6D.4C-ok — Todos os cenários confirmados (Contexto, Sucesso)**

1. Atualizar `TASK-[id].md`: `**Status:**` → `Concluída`
2. Marcar a task como `completed` no `TodoWrite`
3. Atualizar `OUTPUT-TASK-[id].md`: timestamp de conclusão + cenários confirmados pelo usuário + `Status: Concluída`
4. Verificar se todas as tasks da feature foram concluídas (todas `completed` no TodoWrite):
   - Se sim: atualizar `FEAT-[nome].md` `**Status:**` → `Concluída`
   - Informar: *"Todas as tasks da feature F[N] — [nome] foram concluídas! ✅"*
5. Registrar no log e salvar snapshot.
6. Orientar e aguardar próximo comando do usuário:
   > *"TASK-[id] concluída ✅. Progresso: [X/N tasks].*
   > *Próximo passo: `/bks-sdd --task-run TASK-[próxima]`"*

**Passo 6D.4C-fail — Algum cenário falhou (Contexto, Falha)**

1. Manter status `Em execução`
2. Registrar no `OUTPUT-TASK-[id].md`: qual cenário falhou + motivo informado pelo usuário
3. Orientar:
   > *"[N] cenário(s) não passaram. Corrija a implementação e execute*
   > *`/bks-sdd --task-done TASK-[id]` novamente quando todos estiverem passando."*

---

### Comando `--status` — Dashboard de progresso do workspace

**Trigger:** `/bks-sdd --status`

**Objetivo:** Exibir o estado completo do workspace em visão de árvore — projetos, features e tasks.

**Fluxo:**

**Passo 6S.1 — Localizar workspace e projetos**

Localizar `workspace-*/`. Para cada projeto em `projects/`, ler `PLAN-[nome].md`.

**Passo 6S.2 — Agregar progresso**

Para cada feature de cada projeto:
- Ler o estado atual do `TodoWrite` para obter tasks e seus status (`pending` / `in_progress` / `completed`)
- Se o TodoWrite não tiver tasks desta feature (ciclo não iniciado), contar arquivos `TASK-[id].md`
  em `spec/tasks/` e verificar o campo `**Status:**` de cada um como fallback

**Passo 6S.3 — Exibir dashboard**

```
workspace-[nome]
└── project-[nome-1]     [6/8 tasks — 75%]
    ├── F1 [nome]        ✅ 3/3 tasks concluídas
    ├── F2 [nome]        🔄 2/3 tasks (1 em execução)
    └── F3 [nome]        ⏳ 0/2 tasks pendentes
└── project-[nome-2]     [0/5 tasks — 0%]
    └── F1 [nome]        ⏳ Não iniciada
```

Ícones de status de feature:
- ✅ Concluída — todas as tasks concluídas
- 🔄 Em andamento — pelo menos uma task Em execução ou Concluída
- ⏳ Pendente — nenhuma task iniciada ainda
- 📝 Sem tasks — feature com FEAT/TEST aprovados mas tasks não geradas ainda

---

### Comando `--task-list` — Listar tasks de uma feature

**Trigger:** `/bks-sdd --task-list` ou `/bks-sdd --task-list [feature-id]`

**Objetivo:** Mostrar o estado detalhado das tasks de uma feature específica.

**Fluxo:**

**Passo 6L.1 — Identificar feature**

- Se argumento fornecido (ex: `F1`): usar diretamente se existir no plano.
- Se não fornecido: listar features com tasks e perguntar ao usuário.

**Passo 6L.2 — Exibir tabela de tasks**

```
Feature: F[N] — [nome]
IMPL: spec/output/results/IMPL-[feature].md
Progresso: [X/N] tasks concluídas

ID        | Descrição                    | Tipo   | Agente        | Dep.  | Status
----------|------------------------------|--------|---------------|-------|----------
TASK-001  | [desc]                       | Teste  | validador     | —     | ✅ Concluída
TASK-002  | [desc]                       | Impl.  | implementador | T001  | 🔄 Em execução
TASK-003  | [desc]                       | Impl.  | implementador | T002  | ⏳ Pendente
```

---

### Comportamento do `--continue` na Fase 6 (D6)

Quando a fase ativa detectada for a Fase 6 (existem tasks Em execução ou Pendente),
o `--continue` exibe adicionalmente ao resumo padrão:

```
Fase ativa: 6 — Implementação
Projeto: project-[nome]
Feature em andamento: F[N] — [nome]
Tasks pendentes: TASK-002, TASK-003, TASK-005
Próximo passo sugerido: TASK-002 — [descrição] (sem dependências bloqueadas)
```

Seguido pelo dashboard `--status` completo do workspace.

O `--continue` **não retoma a execução automaticamente** — apenas mostra o estado e sugere
o próximo comando. O usuário deve confirmar com `/bks-sdd --task-run [TASK-id]` para avançar.
Isso previne execução acidental de tasks sem intenção explícita.

---

### Fluxo completo — Fase 6 (happy path)

**Modo Contexto** — interação humana em cada etapa:
```
Fases 1–5 concluídas (PLAN + FEAT + TEST + TASKS geradas)
    ↓
/bks-sdd --impl-init                  → IMPL-[feature].md + tasks inicializadas no TodoWrite
    ↓
/bks-sdd --task-run TASK-001 --context
    ↓ (entrega pacote de contexto → usuário executa externamente)
/bks-sdd --task-done TASK-001
    ↓ (checklist interativo → usuário confirma cenários → TASK-001 Concluída)
Usuário chama --task-run TASK-002 manualmente, repete até o fim
    ↓
Todas as tasks concluídas → FEAT-[nome].md: Concluída
    ↓
/bks-sdd --status           → feature aparece ✅ no dashboard
```

**Modo Agente** — execução autônoma, sem pausas entre tasks:
```
Fases 1–5 concluídas (PLAN + FEAT + TEST + TASKS geradas)
    ↓
/bks-sdd --impl-init                  → IMPL-[feature].md + tasks inicializadas no TodoWrite
    ↓
/bks-sdd --task-run TASK-001 --agent
    ↓ (agente gera código em spec/output/code/)
    → --task-done TASK-001 chamado automaticamente pelo agente
    ↓ (verificação interna dos cenários do TEST spec)
    → se ok: avança automaticamente para --task-run TASK-002 --agent
    → se falha localizada: tenta autocorreção e revalida
    → se falha irrecuperável: para e informa o usuário com gap preciso
Ciclo se repete até todas as tasks concluídas ou bloqueio explícito
    ↓
Todas as tasks concluídas → FEAT-[nome].md: Concluída (automático)
    ↓
/bks-sdd --status           → feature aparece ✅ no dashboard
```

**Bloqueios estruturais da Fase 6:**
- `--task-run` sem `--impl-init` prévio → bloqueado
- `--task-run` com dependência não concluída → bloqueado
- `--task-done` sem `--task-run` prévio (status diferente de Em execução) → bloqueado
- `--impl-init` para feature sem tasks → bloqueado; orientar Fase 5.3
- Modo Agente: `--task-done` sem arquivos em `spec/output/code/` → bloqueado; reexecutar `--task-run`

### Edge cases da Fase 6

| Situação | Comportamento |
|----------|---------------|
| Stack não declarada no projeto | Perguntar antes de gerar IMPL; salvar em `stack.md` |
| Skill de stack não disponível | Modo Contexto obrigatório; informar antes de iniciar |
| `--task-done` (Contexto) com cenário falhando | Manter Em execução; registrar falha; orientar correção |
| `--task-done` (Agente) com cenário não coberto | Tentar autocorreção; se falhar, interromper e reportar gap |
| Feature concluída parcialmente | Não marcar FEAT como Concluída até todas as tasks done |
| Task com dependência Em execução | Bloquear; mostrar qual task precisa concluir antes |
| Modo Agente sem arquivos gerados em code/ | Bloquear --task-done; reportar que --task-run não produziu output |
