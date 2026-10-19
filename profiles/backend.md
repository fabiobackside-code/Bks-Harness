# Perfil `backend`

Servidor e dados. API, domínio, persistência — sem interface.

## Gera

- API e contratos
- domínio, sob arquitetura hexagonal e padrão TXC
- modelo de dados e scripts SQL
- testes unitários e de integração
- README e ARCHITECTURE

## Não gera

Interface, design, mock de tela. Consumidor da API é outro projeto ou outro perfil.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` |
| consolidação | `docs/canonical/CONTEXT.md` |
| produto | `docs/canonical/PRD-{projeto}.md` |
| modelagem | modelo de domínio e de dados; DDL em `app/db/` |
| especificação | `specs/features/`, `specs/tests/`, `specs/tasks/` |
| arquitetura | `outputs/ARCH-{projeto}.md` |
| implementação | `app/` — domínio, portas, adapters |
| revisão | independente |
| fechamento | `STATUS.md`, `JOURNAL.md` |

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | sim | `producao` |

## Skills

`bks-sdd` · `bks-standards` · `bks-dotnet-solutions`, `bks-typescript-solutions` ou
`bks-go-solutions` · `bks-tests` · `bks-arch` · `api-design` · `security-audit`

## O que perguntar na criação

1. Qual a stack — .NET, TypeScript, Go, outra?
2. Qual o banco — SQL Server, PostgreSQL, outro?
3. Há mensageria — Kafka, RabbitMQ, nenhuma?
4. Como se autentica — JWT próprio, provedor externo, nenhuma?
