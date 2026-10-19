# Muletas do português técnico

São expressões que ocupam espaço sem dizer nada. Corte ou troque. As marcadas com `guarda` são
apontadas pelo `writing_guard.py`; as outras ficam para a revisão.

<!-- bks-escrita: ignorar -->

## Enchimento

| Antes | Depois | Guarda |
|---|---|---|
| "vale ressaltar que", "é importante notar que", "cabe destacar que" | corte e diga a coisa | guarda |
| "com o objetivo de", "de forma a", "visando" | "para" | guarda |
| "no que tange a", "no que diz respeito a", "a nível de" | "sobre", "em" | guarda |
| "devido ao fato de que" | "porque" | guarda |
| "neste momento", "atualmente" | corte; a documentação viva fala do presente | guarda |
| "sendo que" | divida a frase | guarda |
| "onde" fora de lugar ("a regra onde o serviço recusa") | "em que", "pela qual" | — |
| "vamos estar enviando" | "enviamos" | — |

## Verbo vazio com substantivo

| Antes | Depois | Guarda |
|---|---|---|
| "realiza a validação da entrada" | "valida a entrada" | guarda |
| "efetua o registro do log" | "registra o log" | guarda |
| "promove a abertura da conexão" | "abre a conexão" | — |
| "faz a verificação de que o valor corresponde" | "verifica se o valor corresponde" | — |
| "atua como", "se configura como" | "é" | guarda (atua como) |
| "possui" | "tem" | guarda |

## Ênfase e promoção

Corte "robusto", "poderoso", "elegante", "crucial", "fundamental", "essencial", "de forma
transparente", "sem esforço". A guarda aponta todas menos "fundamental" e "essencial", que têm uso
legítimo frequente e ficam para a revisão. Se a coisa é importante, mostre a consequência de errar.

| Antes | Depois |
|---|---|
| "O envelope tem papel crucial na arquitetura." | "Sem o envelope, cada API teria o próprio formato de entrada e saída." |

## Hesitação

| Antes | Depois | Guarda |
|---|---|---|
| "poderia eventualmente causar" | "causa", ou "causa quando…", com a condição | guarda (eventualmente) |
| "em princípio, o serviço tende a recusar" | "o serviço recusa" | — |

Se há dúvida real, confira no código e escreva o que encontrou. Se não der para conferir, diga o
que não foi verificado.

## Transição mecânica

"Além disso", "ademais", "dessa forma", "nesse sentido", "por fim", "em suma" no começo de quase
todo parágrafo. A guarda aponta "ademais" e "em suma"; as outras têm uso legítimo e ficam para a
revisão. Quando a ligação importa, diga qual é: "por isso", "mesmo assim", "nesse caso".

## Atribuição vaga

"Recomenda-se", "é considerado boa prática", "sabe-se que". Diga quem recomenda e por quê, ou
afirme. A guarda aponta "recomenda-se" e "sabe-se que".

## Fórmulas

- **Paralelismo negativo:** "não é só X, é Y". Diga o que é.
- **Trio forçado:** três adjetivos ou três benefícios porque três soa bem. Use quantos existirem.
- **Fecho genérico:** "assim, o sistema garante uma execução segura e confiável". A seção termina
  quando o assunto acaba.
- **Lista com rótulo inline:** "- **Desempenho:** o desempenho foi melhorado". Se o rótulo repete a
  frase, vire parágrafo.

## Marcas de conversa com assistente

"Espero que ajude", "fique à vontade para", "segue abaixo", "Claro!". Não pertencem a documento.

<!-- /bks-escrita -->
