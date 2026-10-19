# Perfil `legacy-docs`

Entender um legado. Inventario, arquitetura reconstruída, regras de negócio extraídas — sem
alterar uma linha do código existente.

## Gera

- inventario: o que existe, em que linguagem, quanto, em que estado
- arquitetura reconstruída a partir do código, não da documentação antiga
- regras de negócio extraídas, com o ponto do código que as sustenta
- mapa de dependências: interno, externo, banco, integração
- modelo de dados como está, não como deveria ser
- pontos de risco: código morto, dependência sem suporte, regra duplicada, acoplamento crítico
- questões abertas — o que o código não responde e precisa de alguém

## Não gera

Código. Não refatora, não corrige, não "melhora enquanto documenta". Se o alvo é reescrever, o
perfil e `reengineering`.

## Fases

| Fase | Produz |
|---|---|
| inventario | `outputs/INVENTARIO-{projeto}.md` |
| leitura | `docs/input/` — anotações brutas da leitura do código |
| domínio | `brain/domain/` — as regras de negócio encontradas |
| arquitetura | `outputs/ARCH-{projeto}-ATUAL.md` — como o sistema e hoje |
| dados | `outputs/DADOS-{projeto}.md` — modelo como está |
| riscos | `outputs/RISCOS-{projeto}.md` |
| consolidação | `docs/canonical/CONTEXT.md` |
| fechamento | `STATUS.md`, `JOURNAL.md` |

## Regras

**Documente o que o código faz, não o que deveria fazer.** Onde houver divergência entre
comentario, documentação antiga e comportamento, o comportamento vence — e a divergência vira
questão aberta.

**Toda regra extraída aponta para o código.** Arquivo e linha. Regra sem referência é suposição, e
suposição sobre legado custa caro.

**O que o código não explica fica em aberto.** Não invente a intenção por tras de um `if` que
ninguém entende. Liste, e siga.

## Eixos

| Eixo | Vale | Padrão |
|---|---|---|
| `output` | sim | `md` |
| `architecture_renderer` | sim | `mermaid` |
| `frontend_target` | não | — |
| `rigor` | não | — |

## Skills

`bks-sdd` · `bks-arch` · `doc-writer` · `debug-assistant` (para entender comportamento obscuro)

## O que perguntar na criação

1. Onde está o código, e há acesso a um ambiente que rode?
2. Qual a linguagem e a versão?
3. Há alguém que conheca o sistema e possa responder duvidas?
4. O objetivo e entender, ou preparar uma reescrita?
5. Há documentação anterior? Ela e confiavel?
