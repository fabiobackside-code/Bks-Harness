# Perfil `fullstack`

Projeto completo, faseado. Documentação, design, front, back, banco, infraestrutura e componentes
— tudo com testes.

## Gera

Tudo o que os perfis `frontend`, `backend`, `infra` e `component` geram, sob um plano único e
faseado.

## Não gera

Nada fica de fora. O que muda é a ordem: este perfil existe para faseamento, não para ampliação de
escopo. Fase que não está no plano não entra sozinha.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` |
| consolidação | `docs/canonical/CONTEXT.md` |
| produto | `docs/canonical/PRD-{projeto}.md` |
| plano macro | `outputs/PLAN-{projeto}.md` — o faseamento |
| arquitetura | `outputs/ARCH-{projeto}.md` |
| modelagem | domínio, dados, DDL |
| design | telas, fluxos, sistema visual |
| especificação | `specs/features/`, `specs/tests/`, `specs/tasks/` — por fase |
| implementação | `app/` — backend, frontend, componentes |
| infraestrutura | IaC, pipeline, observabilidade |
| revisão | independente, por fase |
| fechamento | `STATUS.md`, `JOURNAL.md` |

O plano macro é obrigatório aqui. Sem ele, um projeto deste tamanho vira lista de tarefas sem
ordem, e a primeira fase nunca fecha.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | **sim** | `web` |
| `rigor` | sim | `producao` |

## Skills

Todas. `bks-sdd` conduz; as demais entram conforme a fase.

## O que perguntar na criação

1. Web, mobile, ou ambos?
2. Qual a stack de backend, e qual a de frontend?
3. Qual o banco? Há mensageria?
4. Onde roda — nuvem, on-premise, container?
5. Há prazo ou marco que force o faseamento?
