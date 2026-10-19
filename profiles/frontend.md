# Perfil `frontend`

Camada visual. Design, mocks, componentes, integração com uma API que já existe.

## Gera

- design de telas e fluxos
- mocks navegaveis
- componentes
- integração com a API
- testes de componente e de fluxo

## Não gera

API, domínio, banco. Se a API ainda não existe, o projeto precisa de `fullstack` ou de um projeto
`backend` ao lado.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` |
| consolidação | `docs/canonical/CONTEXT.md` |
| produto | `docs/canonical/PRD-{projeto}.md` |
| design | telas, fluxos, sistema visual em `docs/design/` |
| mocks | protótipo navegavel em `outputs/mocks/` |
| especificação | `specs/features/`, `specs/tests/` |
| implementação | `app/` — componentes e integração |
| revisão | independente |
| fechamento | `STATUS.md`, `JOURNAL.md` |

O design vem antes do componente. Componente escrito antes do sistema visual vira refactor.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | **sim** | `web` |
| `rigor` | sim | `producao` |

`frontend_target` decide o que se constrói: `web`, `mobile`, ou `both` com design compartilhado.

## Skills

`bks-sdd` · `frontend-design` · `bks-arch` · `bks-tests` · `api-design` (para consumir o contrato)

## O que perguntar na criação

1. Web, mobile, ou ambos?
2. Qual o framework — React, Vue, React Native, outro?
3. A API já existe? Onde está o contrato?
4. Há sistema de design a seguir, ou vamos criar um?
