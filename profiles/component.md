# Perfil `component`

Biblioteca reusável. SDK, DLL, pacote — código consumido por outros projetos, não executado
sozinho.

## Gera

- contrato público da biblioteca
- implementação
- testes — o consumidor depende do contrato, entao o contrato precisa de prova
- empacotamento e versionamento
- README e ARCHITECTURE

## Não gera

Aplicação, interface, infraestrutura de execução. Uma biblioteca não tem `Program.cs` de produção.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` |
| consolidação | `docs/canonical/CONTEXT.md` |
| contrato | `specs/features/FEAT-*.md` — a API publica antes da implementação |
| especificação | `specs/tests/TEST-*.md`, `specs/tasks/TASK-*.md` |
| arquitetura | `outputs/ARCH-{projeto}.md` |
| implementação | `app/` |
| empacotamento | versionamento, publicação, changelog |
| revisão | independente |
| fechamento | `STATUS.md`, `JOURNAL.md` |

O contrato vem antes de tudo. Uma biblioteca cujo contrato muda depois de publicada quebra quem a
usa.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | sim | `producao` |

## Skills

`bks-sdd` · `bks-standards` · `bks-dotnet-solutions`, `bks-typescript-solutions` ou
`bks-go-solutions` · `bks-tests` · `bks-arch` · `api-design`

## O que perguntar na criação

1. Qual a stack — .NET, TypeScript, Go, outra?
2. Onde a biblioteca sera publicada — NuGet, npm, módulo Go, registro interno?
3. Há compatibilidade a manter com uma versão anterior?
