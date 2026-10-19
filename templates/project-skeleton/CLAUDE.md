# {{PROJETO}} (categoria: {{backside | w3 | private}})

> **Esqueleto de exemplo.** Esta pasta mostra a estrutura canônica de um projeto real, mas está
> vazia de propósito — sem escopo, sem stack, sem specs preenchidas. Use `/bkhar:new-project` na raiz do
> vault para gerar a sua versão com conteúdo real.

## O projeto é autossuficiente

Tudo que uma sessão precisa está neste repositório. Nenhum comando lê o vault para funcionar.

## Boot da sessão — carregar nesta ordem

| # | Arquivo | Para que |
|---|---|---|
| 1 | `./STATUS.md` | onde o projeto parou, o que trava, próximo passo |
| 2 | `./WORKFLOW.md` | o fluxo de comandos deste projeto |
| 3 | `./brain/engineering/` | como se constrói aqui — padrão técnico local |
| 4 | `./brain/domain/` | o que o produto é — regra de negócio, método, normativo |

Skill em `brain/engineering/` sobrescreve a equivalente do kit para este projeto.

O perfil do usuário vive no vault (`workbench/profile.md`) e é carregado pelo ambiente, não por
este arquivo.

## Onde cada coisa está

| O que | Onde |
|---|---|
| Specs — fonte de verdade para implementar | `./specs/{features,tests,tasks}/` |
| Decisões deste projeto | `./decisions/ADR-NNN.md` |
| Contexto consolidado (após `/bkhar:canonize`) | `./docs/canonical/` |
| Material bruto ainda não consolidado | `./docs/input/` |
| Entregáveis gerados | `./outputs/` |
| Código | `./app/` |

## Idioma

Documentação e artefatos em português do Brasil. Código, nomes de tipo, método e variável em
inglês.
