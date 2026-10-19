# Project Structure — BKS-SDD Reference

Este documento descreve o papel de cada folder e arquivo dentro de um projeto BKS-SDD.
É lido pelo comando `/help-workspace` e pela skill ao criar e navegar projetos.

---

## Estrutura completa de um projeto

```
project-[nome]/
├── research/
│   ├── links.md                        ← URLs de referência para o PRD do projeto
│   ├── PRD-[nome].md                   ← gerado por /bks-sdd --project-prd
│   └── [arquivos .pdf, .md, .txt]      ← inputs colocados pelo usuário
├── plan/
│   └── PLAN-[nome].md                  ← gerado por /bks-sdd --project-plan
└── spec/
    ├── features/                        ← specs de features (Fase 5)
    │   └── FEAT-[nome].md
    ├── tests/                           ← test specs por feature (Fase 6)
    │   └── TEST-[nome].md
    ├── tasks/                           ← tasks de implementação (Fase 5, após TEST aprovado)
    │   └── TASK-[id]-[descrição].md
    └── output/                          ← artefatos gerados pela execução das specs
```

---

## Folders e arquivos

### `research/`

**Papel:** Etapa de levantamento de contexto scoped ao projeto. Análoga ao `research/` do
workspace, mas focada no escopo deste projeto específico.

**O que colocar aqui:**
- Arquivos `.pdf` — pesquisas, docs de produto, análises competitivas scoped ao projeto
- Arquivos `.md` — notas de requisitos, ideias brutas, wikis relevantes
- Arquivos `.txt` — transcrições, rascunhos, anotações
- `links.md` — URLs de referência específicas para este projeto

**Contexto herdado:** A skill lê automaticamente o `PRD.md` do workspace como contexto macro
ao gerar o PRD do projeto. Não é necessário copiar nada do workspace para cá.

**O que é gerado aqui:**
- `PRD-[nome].md` — Product Requirements Document scoped ao projeto, gerado por `/bks-sdd --project-prd`

---

### `research/links.md`

**Papel:** Lista curada de URLs de referência específicas para este projeto.

**Formato esperado** (flexível):
```markdown
# Links de Referência — project-[nome]

- https://exemplo.com/api-docs
- https://concorrente.com/feature-x
```

A skill faz fetch de cada URL e extrai conteúdo relevante como input suplementar para o PRD
do projeto. Funciona da mesma forma que o `links.md` do workspace.

---

### `plan/`

**Papel:** Plano macro de execução do projeto, derivado do PRD.

**O que é gerado aqui:**
- `PLAN-[nome].md` — gerado por `/bks-sdd --project-plan`

O plano decompõe o PRD em fases de execução, lista as features previstas com prioridade,
mapeia dependências e documenta assunções. É o artefato que orienta a Fase 5 (Feature Specs).

**Quando usar:** Após o `PRD-[nome].md` estar aprovado. O plano é derivado do PRD — se o
PRD mudar significativamente, o plano precisa ser regenerado.

---

### `spec/`

**Papel:** Container de todas as especificações executáveis do projeto.

Organizado em quatro subfolders que representam estágios progressivos do ciclo spec → test → implement:

#### `spec/features/`

**Papel:** Specs de features — a decomposição do plano em unidades funcionais especificáveis.

Cada feature do `PLAN-[nome].md` vira um arquivo `FEAT-[nome].md` aqui.
Uma spec de feature descreve: o que a feature faz, critérios de aceite, comportamentos de
borda, restrições técnicas e referência ao test spec correspondente.

*(Fase 5)*

#### `spec/tests/`

**Papel:** Test specs por feature — cenários de teste definidos **antes** da implementação.

Cada `FEAT-[nome].md` aprovado gera um `TEST-[nome].md` correspondente aqui, via
`/bks-sdd --feature-tests`. O TEST define os cenários Gherkin do happy path e a tabela de
edge cases derivados do FEAT. O `--feature-task` só é desbloqueado após o TEST estar aprovado.

Formato de nome: `TEST-[nome].md` — idêntico ao FEAT correspondente.
Exemplo: `FEAT-validação-autorização-transação.md` → `TEST-validação-autorização-transação.md`

*(Fase 6)*

#### `spec/tasks/`

**Papel:** Tasks atômicas de implementação, geradas após o TEST correspondente estar aprovado.
Cada task é uma unidade de trabalho que um agente pode executar de forma independente.

Formato de nome: `TASK-[id]-[descrição-curta].md`
Exemplo: `TASK-001-criar-endpoint-autenticação.md`

*(Fase 5, desbloqueada pela Fase 6)*

#### `spec/output/`

**Papel:** Artefatos produzidos pela execução das tasks — logs de execução, código gerado,
resultados de validação, reports de sensores.

Este folder fecha o loop de feedback do Harness:
`research/` → `plan/` → `spec/features/` → `spec/tests/` → `spec/tasks/` → **`spec/output/`**
→ retroalimenta o próximo ciclo.

*(Populado pelo agente executor após conclusão das tasks)*

---

## Relação com o workspace

Um projeto é sempre filho de um workspace. A relação é:

```
workspace-[nome]/               ← visão macro (PRD de produto/negócio)
└── pro