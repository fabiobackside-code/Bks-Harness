# Perfil `data`

Dados e analytics. Pipeline, modelagem, contratos de dados, BI.

## Gera

- pipeline de ingestao e transformação (ETL ou ELT)
- modelagem analitica
- contratos de dados entre produtor e consumidor
- qualidade: validação, detecção de anomalia, linhagem
- painel ou camada semantica de BI
- testes de pipeline e de qualidade

## Não gera

Aplicação transacional, interface de usuário. O consumo dos dados e de outro perfil.

## Fases

| Fase | Produz |
|---|---|
| entrada | `docs/input/` — fontes, volumes, frequência, donos |
| consolidação | `docs/canonical/CONTEXT.md` |
| inventario de fontes | `outputs/FONTES-{projeto}.md` — o que existe e em que estado |
| modelagem | modelo analitico e contratos de dados |
| arquitetura | `outputs/ARCH-{projeto}.md` — linhagem e fronteiras de dado sensivel |
| especificação | `specs/features/`, `specs/tests/` |
| implementação | `app/` — pipeline e transformações |
| qualidade | validação, anomalia, reconciliação |
| fechamento | `STATUS.md`, `JOURNAL.md` |

O inventario de fontes vem cedo. Pipeline construido sobre fonte que ninguém inspecionou quebra na
primeira carga real.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | sim | `producao` |

## Skills

`bks-sdd` · `bks-arch` · `bks-standards` · `security-audit` (dado pessoal e regulado)

## O que perguntar na criação

1. Quais as fontes, e quem e dono de cada uma?
2. Batch, streaming, ou os dois?
3. Onde os dados repousam — data lake, warehouse, banco relacional?
4. Há dado pessoal ou regulado no caminho?
5. Quem consome no fim — painel, API, modelo?
