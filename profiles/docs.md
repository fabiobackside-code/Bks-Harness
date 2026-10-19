# Perfil `docs`

Entrega documental. Escopo, arquitetura, apresentação — sem código de aplicação.

## Gera

- documento de escopo
- arquitetura no template escolhido (TOGAF, C4 ou próprio)
- apresentação, quando pedida
- ADRs das decisões tomadas no caminho

## Não gera

Código, banco de dados, infraestrutura. Se a conversa derivar para implementação, registre como
questão aberta e siga — mudar de perfil é decisão do usuário, não do agente.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` — notas, entrevistas, pesquisa |
| consolidação | `docs/canonical/CONTEXT.md` |
| escopo | `outputs/ESCOPO-{projeto}.md` |
| arquitetura | `outputs/ARCH-{projeto}.md` no template escolhido |
| apresentação | `outputs/APRESENTACAO-{projeto}.{md,html}` — se pedida |
| fechamento | `STATUS.md`, `JOURNAL.md` |

Sem `/bkhar:spec`, sem `/bkhar:loop`. Não há FEAT nem TASK: o artefato é o documento.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | não | — |

## Skills

`bks-sdd` (fases de entrada, consolidação e produto) · `bks-arch` · `doc-writer`

## O que perguntar na criação

1. Qual o template de arquitetura — TOGAF, C4 ou próprio?
2. A entrega inclui apresentação?
3. Saída em markdown ou HTML para PDF?
