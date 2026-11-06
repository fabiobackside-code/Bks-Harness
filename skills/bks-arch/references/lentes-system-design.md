# Lentes de system design

Na onda de desenho do modo `autonomo`, o `architect` é chamado uma vez por lente. A lente diz o
que ele lê antes de escrever o contrato. Os blocos vêm da system-design-skills (MIT), copiados sem
edição em `skills/bks-arch/third-party/system-design-skills/`.

## Lente → blocos

| Lente no grafo | Blocos que o `architect` lê | O contrato que sai |
|---|---|---|
| `banco` | `data-storage`, `caching`, `consistency-coordination`, `sequencer`, `sharded-counters` | schema, chaves, índices, estratégia de cache e de consistência |
| `api` | `api-design`, `service-decomposition` | rotas, contratos de entrada e saída, versionamento, idempotência |
| `mensageria` | `messaging-streaming`, `task-scheduling` | filas e tópicos, entrega, ordem, reprocessamento, agendamento |
| `infra` | `load-balancing`, `dns`, `content-delivery`, `blob-store`, `scaling-evolution` | topologia, balanceamento, armazenamento de objeto, caminho de escala |
| `telemetria` | `observability`, `distributed-logging` | métricas, traces, logs, alertas e SLO |
| `resiliencia` | `resilience-failure`, `consistency-coordination` | timeout, retry, circuit breaker, degradação |
| `busca` | `distributed-search` | índice, ingestão, relevância |
| `escala` | `requirements-scoping`, `back-of-the-envelope`, `scaling-evolution` | requisitos não funcionais e estimativa de carga |
| `ameaças` | nenhum bloco: é a lente do `security`, pela skill `security-audit` | modelo de ameaças |

O nome de um bloco também vale como lente, quando a task precisa só dele.

## Como o `architect` usa

1. Lê o `SKILL.original.md` de cada bloco da lente. A pasta `references/` do bloco só entra
   quando o contrato pede o aprofundamento: o bloco inteiro custa contexto que a task não consome.
2. Responde às perguntas da seção "Clarify first" do bloco pelas fontes do projeto. No `autonomo`,
   o que não tiver fonte vira linha em `decisions/SUPOSICOES.md`.
3. Escreve o contrato em `specs/contracts/<lente>.md`, em português, com `status: rascunho`, o
   trade-off escolhido e o descartado, e o diagrama na notação desta skill.
4. As premissas BKS (hexagonal, Pipeline explícito, Result Pattern, Dapper, testes com
   Testcontainers) prevalecem sobre a recomendação do bloco. Conflito vira ADR proposto, não
   adoção silenciosa.

## Por que não instalar como skill

Instalada, a system-design-skills traria o próprio orquestrador (`/design`) e o próprio agente,
concorrendo com o Gerente e com o `architect`, e gatilhos em inglês disputando os da `bks-arch`.
Como lente, ela entra só quando o grafo pede, no contexto da task.
