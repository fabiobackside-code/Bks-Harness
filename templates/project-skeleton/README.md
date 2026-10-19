# {{PROJETO}} — esqueleto de exemplo

Esta pasta existe só para mostrar a **estrutura canônica** de um projeto. Está vazia de
propósito — sem escopo real, sem stack definida, sem specs preenchidas.

## Estrutura

```
{{projeto}}/
├── STATUS.md              onde parei, o que trava, próximo passo
├── WORKFLOW.md            o fluxo de comandos deste projeto
├── JOURNAL.md             marcos e sessões, do mais recente ao mais antigo
├── LEARNINGS.md           defeitos resolvidos, com evidência, que o tester lê antes do teste novo
├── README.md              o que e o projeto
├── CLAUDE.md              contexto que o agente carrega
├── .bks-profile.json      perfil, renderer, eixos
│
├── brain/
│   ├── domain/            o que o produto E — regra de negócio, método, normativo
│   └── engineering/       como se constrói AQUI — padrão técnico, skill local
│
├── docs/
│   ├── input/             material bruto: notas, entrevistas, pesquisa, escopo
│   ├── design/            bancada de trabalho
│   ├── canonical/         contexto consolidado — a fonte após o /canonize
│   ├── history/           o que foi superado
│   └── prompts/           registro de auditoria do próprio processo
│
├── specs/
│   ├── features/          FEAT-*.md
│   ├── tests/             TEST-*.md
│   └── tasks/             TASK-*.md
│
├── decisions/             ADR-NNN deste projeto
├── outputs/               entregáveis gerados
└── app/                   código
```

## Os três arquivos de estado

| Arquivo | Responde | Escrito por | Reescrito? |
|---|---|---|---|
| `STATUS.md` | onde o projeto está **agora** | `/bkhar:save` | sim, por inteiro |
| `JOURNAL.md` | como chegou até aqui | `/bkhar:save` | não, só acrescenta |
| `WORKFLOW.md` | como se trabalha aqui | `/bkhar:new-project` | só quando o fluxo muda |

`STATUS.md` é o ponto de entrada. O `/bkhar:brain` lê ele.

## Como usar de verdade

Rode `/new-project {{nome}} {{categoria}}` com a sessão aberta na **raiz do vault** para gerar a
sua versão preenchida. Depois traga material para `docs/input/` e siga o ciclo descrito no
`WORKFLOW.md` gerado: `/bkhar:note` → `/bkhar:canonize` → `/bkhar:prd` → `/bkhar:spec` → `/bkhar:arch` → `/bkhar:loop` → `/bkhar:review` →
`/bkhar:save`.

Todos os comandos de projeto rodam com a sessão aberta na raiz do repositório do projeto — não no
vault.
