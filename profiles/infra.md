# Perfil `infra`

Plataforma e entrega. Infraestrutura como código, pipeline, observabilidade.

## Gera

- infraestrutura como código (Terraform, Bicep, manifests)
- pipeline de build e deploy
- observabilidade: metricas, logs, tracing, alertas
- politica de acesso e segredo
- runbook de operação
- testes de infraestrutura, onde a ferramenta permitir

## Não gera

Aplicação. Este perfil entrega a plataforma onde outra coisa roda.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` — requisitos de plataforma, restrições, custo |
| consolidação | `docs/canonical/CONTEXT.md` |
| topologia | `outputs/ARCH-{projeto}.md` — ambientes, rede, fronteiras |
| especificação | `specs/features/`, `specs/tests/` |
| implementação | `app/` — IaC e pipeline |
| observabilidade | dashboards, alertas, SLO |
| runbook | `outputs/RUNBOOK-{projeto}.md` |
| revisão | independente, com foco em acesso e exposição |
| fechamento | `STATUS.md`, `JOURNAL.md` |

A topologia vem antes do código. IaC escrito sem topologia decidida vira recurso órfão.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | sim | `producao` |

## Skills

`bks-sdd` · `bks-arch` · `security-audit` · `bks-standards`

## O que perguntar na criação

1. Onde roda — qual nuvem, ou on-premise?
2. Quais ambientes — desenvolvimento, homologação, produção?
3. Kubernetes, serverless, maquina virtual?
4. Há politica de segurança ou conformidade a atender?
5. Quem opera depois de entregue?
