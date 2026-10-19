# Workspace Structure — BKS-SDD Reference

Este documento descreve o papel de cada folder e arquivo dentro de um workspace BKS-SDD.
É lido pelo comando `/help-workspace` para orientar o usuário.

---

## Estrutura completa

```
workspace-[nome]/
├── .logs/
│   ├── session-YYYY-MM-DD.md
│   ├── cost-ledger.jsonl   ← telemetria de tokens/custo (Fase 7)
│   └── COST-REPORT-*.md    ← relatorio final de custo do processo
├── .states/
├── research/
│   ├── links.md
│   └── PRD.md              ← gerado pelo comando /bks-sdd --prd
├── plan/
│   └── PLAN.md             ← gerado futuramente
└── projects/
    └── project-[nome]/     ← gerado pelo comando /bks-sdd --project
        ├── research/
        │   ├── links.md
        │   └── PRD-[nome].md
        ├── plan/
        │   └── PLAN-[nome].md
        └── spec/
            ├── features/
            ├── tests/
            ├── tasks/
            └── output/
```

---

## Folders de controle interno

### `.logs/`

**Papel:** Registro histórico de todas as sessões de trabalho neste workspace.

**Quando é usado:** Automaticamente pela skill a cada sessão. Um arquivo por dia de trabalho
(`session-YYYY-MM-DD.md`). Cada arquivo registra os comandos executados, inputs processados
e resultados obtidos naquele dia.

**Não apague.** São o histórico auditável do seu projeto. Se precisar entender o que foi feito
em uma sessão anterior, este é o lugar.

**Formato de cada entrada:**
```
- [HH:MM] Comando: [comando]
  Ação: [o que foi feito]
  Resultado: [o que foi produzido]
```

**`cost-ledger.jsonl`** — ledger de consumo de tokens e custo estimado (Fase 7). Uma linha
JSON por (sessão × fase), gravada automaticamente pela skill e pelo comando `/bkhar:save`. Regravar
a mesma sessão+fase substitui a entrada anterior, nunca soma — o total não infla.

Cada entrada tem: `ts`, `session_id`, `phase`, `label`, `models` (uso e custo por modelo),
`total` e `total_cost_usd`.

Consolidação:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py" report   --ledger "workspace-[nome]/.logs/cost-ledger.jsonl"
```

**`COST-REPORT-[data].md`** — relatório consolidado do custo do processo, gerado por
`/bks-sdd --cost-report` e automaticamente na conclusão do projeto.

**Não apague.** São a base de comparação entre modelos e entre projetos.

---

### `.states/`

**Papel:** Snapshots do estado da sessão para garantir continuidade entre conversas com o Claude.

O Claude tem um limite de contexto por sessão. Este folder resolve o problema da "amnésia":
antes de encerrar uma sessão (ou automaticamente quando necessário), a skill salva um
snapshot completo do estado — o que foi feito, onde você está, o que vem a seguir.

**Quando é usado:**
- Automaticamente ao criar o workspace (estado inicial)
- Antes de operações longas (geração de PRD, criação de projetos)
- Ao executar `/bks-sdd --tan` ou `/bks-sdd --clear` (encerramento controlado)
- Proativamente a cada ~20 trocas de mensagens

**Como usar:** Na próxima sessão, execute `/bks-sdd --continue`. A skill vai ler o estado
mais recente e retomar de onde você parou.

**Tipos de arquivo:**
- `state-initial-[timestamp].md` — estado criado na inicialização do workspace
- `state-[timestamp].md` — snapshots intermediários durante o trabalho
- `state-final-[timestamp].md` — estado salvo no encerramento controlado (`--tan`)

**Não apague.** São o mecanismo de memória do seu workspace.

---

## Folders de conteúdo do workspace

### `research/`

**Papel:** Etapa inicial de levantamento de contexto para o projeto macro (workspace inteiro).

**O que colocar aqui:**
- Arquivos `.pdf` — pesquisas, análises competitivas, documentos de produto, briefings
- Arquivos `.md` — notas, requisitos preliminares, ideias brutas, wikis exportadas
- Arquivos `.txt` — transcrições, rascunhos, anotações livres
- `links.md` — lista de URLs que você quer usar como referência

**O que é gerado aqui:**
- `PRD.md` — o Product Requirements Document do workspace, gerado pelo comando `/bks-sdd --prd`

**Quando usar:** Antes de executar `/bks-sdd --prd`. Quanto mais contexto você colocar aqui,
mais preciso e completo será o PRD gerado.

---

### `research/links.md`

**Papel:** Lista curada de URLs que servem como referência para o PRD.

**Formato esperado** (flexível — a skill aceita variações):
```markdown
# Links de Referência

- https://exemplo.com/artigo-sobre-o-domínio
- https://concorrente.com
- https://documentação-técnica.io/api
```

A skill lê este arquivo, faz fetch de cada URL com WebFetch e extrai o conteúdo relevante
como input suplementar para o PRD. URLs que não carregam são registradas como "inatingíveis"
e a geração do PRD continua normalmente.

---

### `plan/`

**Papel:** Plano macro do workspace — a visão estratégica que orienta os projetos internos.

**Status atual:** Reservado para uso futuro (Fase 4 da skill).

**O que será gerado aqui:** Um `PLAN.md` com a decomposição estratégica do workspace em
projetos, fases e marcos. Este plano será derivado do `PRD.md` e orientará a criação dos
projetos internos em `projects/`.

---

### `projects/`

**Papel:** Container de todos os projetos internos do workspace.

Um workspace comporta múltiplos projetos. Cada projeto é um escopo delimitado de trabalho
com seu próprio ciclo RPI (Research → Plan → Implement/Specs). Projetos são criados com o
comando `/bks-sdd --project`.

**Estrutura de cada projeto:**

```
projects/
└── project-[nome]/
    ├── research/         ← mesma lógica do research/ do workspace, mas scoped ao projeto
    │   ├── links.md
    │   └── PRD-[nome].md ← gerado por /bks-sdd --project-prd
    ├── plan/
    │   └── PLAN-[nome].md ← gerado por /bks-sdd --project-plan
    └── spec/
        ├── features/     ← specs de features (Fase 5)
        ├── tests/        ← test specs por feature (Fase 6)
        ├── tasks/        ← tasks de implementação (Fase 5, desbloqueadas pela Fase 6)
        └── output/       ← artefatos gerados pela execução das specs
```

**Quando usar:** Após ter o PRD do workspace aprovado, crie um ou mais projetos internos
para decompor o trabalho em escopos menores e mais executáveis.

---

## A lógica do Harness aplicada ao workspace

Este workspace implementa os princípios de Harness Engineering:

| Componente Harness | Implementação no Workspace |
|---|---|
| **Memory** | `.states/` — snapshots que eliminam a amnésia entre sessões |
| **Bootstrap** | `.logs/` — histórico que permite reinicialização rápida do contexto |
| **Feed Forward** | `research/` → `plan/` → `projects/` — instrução estruturada antes da ação |
| **Sensors** | `spec/tests/` — cenários de teste definidos antes da implementação (Fase 6) |

O fluxo completo é: **pesquisar** → **especificar**