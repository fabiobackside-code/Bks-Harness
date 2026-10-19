# Perfil `reengineering`

Reescrever um legado. Entende primeiro, decide o alvo, migra com paridade comprovada.

## Gera

Tudo o que `legacy-docs` gera, e mais:

- decisão do alvo: stack, arquitetura, fronteiras
- estrategia de migração: de uma vez, por fatia, ou lado a lado
- mapa de paridade: cada regra do legado apontando para onde ela vive no novo
- testes de caracterização — o comportamento antigo capturado antes de qualquer reescrita
- código novo
- plano de corte e de retorno

## Fases

| Fase | Produz |
|---|---|
| **entendimento** | tudo do perfil `legacy-docs` |
| alvo | `decisions/ADR-*.md` — stack, arquitetura, o que sai de escopo |
| estrategia | `outputs/MIGRACAO-{projeto}.md` — como se atravessa |
| caracterização | testes que capturam o comportamento atual |
| paridade | `outputs/PARIDADE-{projeto}.md` — regra do legado por destino no novo |
| especificação | `specs/features/`, `specs/tests/`, `specs/tasks/` |
| arquitetura | `outputs/ARCH-{projeto}.md` — o sistema novo |
| implementação | `app/` |
| corte | plano de virada e de retorno |
| revisão | independente |
| fechamento | `STATUS.md`, `JOURNAL.md` |

A fase de entendimento não se pula. Reescrever o que não se entendeu produz um sistema novo com os
bugs antigos e sem as correções que ninguém sabia que existiam.

## Regras

**Teste de caracterização antes do código novo.** O comportamento atual — inclusive o errado —
precisa estar capturado antes de a reescrita começar. Sem isso não há como provar paridade.

**Comportamento errado que alguém depende continua sendo comportamento.** Ao encontrar um bug no
legado, registre e pergunte: corrigir na migração muda o contrato de quem consome.

**O mapa de paridade é a evidência de conclusão.** Regra sem destino no novo é escopo perdido, não
escopo cortado.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | sim, se houver interface | `web` |
| `rigor` | sim | `producao` |

## Skills

`bks-sdd` · `bks-standards` · `bks-arch` · `bks-tests` · `refactor-guide` ·
`bks-dotnet-solutions`, `bks-typescript-solutions` ou `bks-go-solutions` · `security-audit`

## O que perguntar na criação

1. Onde está o legado, e há ambiente que rode?
2. Qual a stack alvo?
3. Migração de uma vez, por fatia, ou os dois sistemas lado a lado por um periodo?
4. Há consumidores externos cujo contrato precisa ser preservado?
5. Há janela de corte, ou a virada e gradual?
6. O que explicitamente **não** vai ser migrado?
