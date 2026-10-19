---
name: bks-create-plan-tasks
description: >
  Cria planos de execução estruturados com tasks atômicas e otimizadas para consumo de tokens.
  Use SEMPRE que o usuário pedir para criar um plano de tasks para qualquer trabalho:
  feature, bugfix, refatoração, documentação, migração, análise, etc.
  Trigger em: "crie um plano", "monte um plano", "plano de tasks", "decompor em tasks",
  "plano de execução", "quero planejar", "gere tasks para", "estruture o trabalho".
  NÃO implementa nada — apenas gera o plano e aguarda aprovação.
---

# BKS-Create-Plans-Tasks — Skill de Geração de Planos

**Idioma:** Todo output desta skill — perguntas, respostas, documentos gerados — deve estar em **Português do Brasil (PT-BR)**.
**Código gerado:** Inglês (nomes de classes, métodos, variáveis).

Esta skill gera planos de execução estruturados com tasks atômicas, seguindo os princípios de
otimização de tokens da Anthropic e as boas práticas de decomposição de trabalho.

---

## Quando invocar

- Usuário pede explicitamente um plano, mapa de tasks ou decomposição de trabalho
- Usuário descreve um trabalho e pergunta como abordar
- Usuário usa o comando `/bks-creat-plans-tasks`

**Não invocar quando:**
- O usuário já tem um plano e quer apenas executar uma task específica
- O trabalho tem menos de 2 passos e cabe em uma única instrução

---

## Passo 1 — Coletar contexto mínimo

Antes de gerar o plano, verificar se o usuário forneceu os dados obrigatórios.
Se algum estiver faltando, fazer as perguntas em uma única mensagem (não uma por vez).

**Dados obrigatórios:**
- **Título:** nome curto do trabalho (se não fornecido, inferir da descrição)
- **Objetivo:** o que deve existir ao final — 1 frase verificável
- **Entrada:** descrição do trabalho, arquivo de referência, ou user story

**Dados opcionais (inferir quando possível):**
- **Repositório / caminho local**
- **Stack:** linguagem/framework principal
- **Restrições específicas**
- **Critérios de sucesso**

Se a descrição do usuário já contiver tudo, pular direto para o Passo 2.
Se faltar apenas dados opcionais, prosseguir com valores inferidos e indicá-los no plano.

---

## Passo 2 — Análise prévia (antes de decompor)

Antes de gerar as tasks, realizar internamente:

1. **Identificar tipo do trabalho:**
   - `FEATURE` — nova funcionalidade
   - `BUGFIX` — correção de comportamento incorreto
   - `REFACTOR` — reestruturação sem mudança de comportamento externo
   - `DOCS` — documentação, specs, ADRs
   - `MIGRATION` — migração de dados, upgrade de dependências
   - `ANALYSIS` — investigação, diagnóstico, pesquisa
   - `INFRA` — configuração, CI/CD, ambiente

2. **Estimar complexidade:**
   - `SIMPLES` — 1 a 3 tasks, um único artefato
   - `MÉDIA` — 4 a 7 tasks, múltiplos artefatos relacionados
   - `COMPLEXA` — 8+ tasks, múltiplos artefatos independentes

3. **Identificar arquivos impactados** (quando repositório é conhecido)

4. **Identificar dependências** entre as partes do trabalho

---

## Passo 3 — Gerar o plano

Gerar o plano completo seguindo a estrutura canônica definida em `references/plan-structure.md`.

### Regras de decomposição de tasks (OBRIGATÓRIAS)

Carregar e aplicar todas as regras de `references/task-rules.md`.

Resumo das regras críticas:
1. **ATOMICIDADE** — cada task produz 1 artefato verificável (FEITO/NÃO FEITO)
2. **AUTOCONTIDO** — o prompt de cada task lista os arquivos a ler e o que produzir, sem depender de memória de sessão anterior
3. **TAMANHO** — 1 arquivo grande (>200 linhas) por task; tasks pequenas podem ser agrupadas (máx 3 do mesmo tipo)
4. **/clear** — declarar `/clear` no início do prompt de cada task; obrigatório em tasks com geração de código
5. **DEPENDÊNCIAS** — mapear dependências e indicar `[PARALELO]` quando possível
6. **STATUS** — usar apenas: `PENDENTE | EM CURSO | CONCLUÍDA | BLOQUEADA | IGNORADA`

### Otimizações de tokens (regras Anthropic)

Aplicar estas práticas em todos os prompts de task gerados:

- **Prompt de início autocontido:** incluir apenas arquivos necessários — não listar o projeto inteiro
- **Instruções negativas antes de positivas:** listar o que NÃO fazer antes do que fazer, evitando correções tardias
- **Critério binário:** cada checklist deve ter resposta SIM/NÃO, sem ambiguidade
- **Contexto mínimo suficiente:** o prompt da task deve ter o contexto mínimo para execução correta, não máximo
- **Sem contexto repetido entre tasks:** cada task referência apenas o que precisa, não copia o contexto geral
- **Artefato de saída explícito:** especificar exatamente o arquivo ou resultado esperado

---

## Passo 4 — Apresentar e aguardar aprovação

Após gerar o plano:

1. Apresentar o plano completo
2. Indicar o número de tasks, complexidade estimada e tempo estimado (se possível)
3. Perguntar: *"O plano está correto? Posso prosseguir ou há ajustes?"*
4. **NÃO implementar nada** sem aprovação explícita

---

## Passo 5 — Salvar o plano (quando solicitado)

Se o usuário confirmar e pedir para salvar:

- Caminho padrão: `planos/PLAN-[título-kebab-case]-[YYYY-MM-DD].md`
- Usar o template completo de `references/plan-structure.md`
- Confirmar o caminho antes de salvar

Se o usuário não pedir para salvar, o plano existe apenas na conversa.

---

## Fluxo de execução após aprovação

Após aprovação do plano, orientar o usuário com os prompts de controle:

| Situação | Prompt sugerido |
|---|---|
| Iniciar a primeira task | `/clear` → cole o "Prompt de início" da T-001 |
| Aprovar e avançar | `Aprovado. Execute a task conforme o plano.` |
| Pausar e verificar | `Pause. Mostre o artefato gerado. Aguarde instrução.` |
| Task bloqueada | `Marque T-XXX como BLOQUEADA. Motivo: [motivo]. Passe para a próxima PENDENTE.` |
| Ignorar uma task | `Marque T-XXX como IGNORADA. Motivo: [motivo].` |
| Atualizar status | `Atualize §5 Estado de Execução: T-XXX = CONCLUÍDA, data [YYYY-MM-DD].` |
| Retomar plano | `Leia [caminho do plano]. Identifique a primeira task PENDENTE. Execute /clear e cole o prompt dela.` |
| Fechar plano | `Plano encerrado. Atualize §5 com todos os status finais. Resuma o que ficou pendente.` |

---

## Referências internas

- `references/plan-structure.md` — template canônico do plano
- `references/task-rules.md` — regras detalhadas de decomposição e otimização de tokens
