# Fontes externas — o que vale, o que foi adaptado, o que foi descartado

Duas skills públicas, sob licença MIT, deram insumo a esta. O original de cada uma está em
`third-party/`, com a licença e o commit de origem. Elas estão em inglês e foram escritas para blog
e texto acadêmico, não para documentação técnica em português. Por isso são **consulta**: quando uma
regra delas contradiz a `SKILL.md`, vale a `SKILL.md`.

| Pasta | Skill | Origem | Commit |
|---|---|---|---|
| `third-party/writing-anti-ai/` | `writing-anti-ai` | `Galaxy-Dawn/claude-scholar`, `skills/writing-anti-ai` | `903787345d6a`, 2026-09-23 |
| `third-party/human-writing/` | `human-writing` | `pr-pm/prpm`, `.claude/skills/human-writing` | `d6b1b17b4818`, 2026-10-14 |

Do `writing-anti-ai` vieram o `SKILL.md`, o catálogo de padrões em inglês, a lista de frases a cortar
e os exemplos em inglês. O catálogo e os exemplos em chinês ficaram de fora. O `SKILL.md` de cada
uma foi renomeado para `SKILL.original.md`, para que o carregador do plugin não o registre como
skill.

Ambas partem do guia da Wikipedia sobre sinais de texto gerado por modelo de linguagem.

<!-- bks-escrita: ignorar -->

## O que vale como está

| Regra | Fonte | Onde está na skill |
|---|---|---|
| cortar enchimento, hesitação e ênfase inflada | as duas | §6 e `references/muletas.md` |
| "é" no lugar de "atua como", "serve como" | `writing-anti-ai` | §3 |
| variar o tamanho das frases | `writing-anti-ai` | §3 |
| paralelismo negativo, trio forçado, sinônimo trocado só para variar | `writing-anti-ai` | §4 e `references/muletas.md` |
| atribuição vaga | as duas | `references/muletas.md` |
| fecho genérico positivo | `writing-anti-ai` | `references/muletas.md` |
| marcas de conversa com assistente | `writing-anti-ai` | `references/muletas.md` |
| abrir pela informação | `human-writing` | §2 |
| subtítulo que afirma | `human-writing` | §2 |
| mostrar a saída em vez de descrever | `human-writing` | §5 |
| dizer o limite | `human-writing` | §5 |
| detalhe concreto: número, nome, caso real | `human-writing` | §5 |

## O que foi adaptado

| Regra de origem | Adaptação |
|---|---|
| catálogo de vocabulário em inglês ("delve", "tapestry", "Furthermore") | catálogo próprio do português técnico em `references/muletas.md`: nominalização, "de forma a", "no que tange", gerundismo |
| nota de 1 a 10 por dimensão, total sobre 50 | a dimensão "autenticidade" virou "concreto"; a nota é da revisão, não da guarda |
| excesso de negrito | negrito no termo que o leitor deve fixar, no máximo um por parágrafo |
| lista com rótulo inline | vale quando o rótulo repete a frase; rótulo que é o termo definido continua certo |

<!-- /bks-escrita -->

## O que conflita e foi descartado

| Regra de origem | Por que não vale aqui |
|---|---|
| proibir o travessão, ou trocar por vírgula | em português, o travessão é pontuação de aposto e inciso. Vale só o limite de excesso da §7 |
| "personalidade": opinião, humor, primeira pessoa, sentimentos mistos | documentação de arquitetura e treinamento técnico falam como colega que explica, não como cronista |
| apartes de conversa ("We tried docs. They don't read them.") | mesmo motivo; o caso real entra como fato, não como piada |
| fechar com chamada para ação | tom de blog. O documento termina quando o assunto acaba |
| subtítulo a cada dois ou três parágrafos | o tamanho da seção segue o assunto, não uma cota |
| consultar memória de outra skill (`ml-paper-writing`) | aponta para arquivo que este kit não tem; a instrução não se aplica |

## O que nenhuma das duas cobre

É o núcleo próprio da `SKILL.md`. A decisão vai sintetizada no texto, e não como número de ADR no
meio da frase. Sigla e nome de tipo são definidos no primeiro uso. Também são próprios o corte da
nominalização, do parêntese empilhado, do histórico na documentação viva e do excesso de
identificador entre crases.
