---
name: bks-writing
description: >
  Padrão de escrita da documentação viva em português do Brasil: o texto se lê de primeira, sem
  abrir outro arquivo. Use SEMPRE que for escrever ou revisar ARCHITECTURE.md, README.md, cânone
  temático, spec (FEAT/TEST/TASK), material de treinamento, roteiro de apresentação ou comentário de
  código; e quando o usuário pedir para humanizar, tirar cara de texto gerado, deixar mais natural,
  mais direto ou mais legível. Cobre a decisão sintetizada no texto em vez do número do ADR no meio
  da frase, abertura pela informação, título que afirma, frase curta, termo definido no primeiro uso
  e a lista de muletas do português técnico.
---

# bks-writing — o texto se lê de primeira

Escreva para quem nunca viu o projeto e precisa entender esta parte hoje. Essa pessoa conhece a
stack, mas não sabe o que foi decidido, nem por quê, nem onde ficou registrado.

O teste é um só: ela lê o parágrafo uma vez e entende, sem abrir outro arquivo. Se precisar abrir um
ADR para entender a frase, o texto falhou.

O tom é o de um colega que explica o sistema a outro. Sem entusiasmo de anúncio, sem cerimônia de
relatório, sem piada para parecer próximo.

## Alcance

| Entra | Fica fora |
|---|---|
| `ARCHITECTURE.md` e `README.md` | ADR e `JOURNAL.md`, que registram o que mudou |
| cânones temáticos | `CONTEXT*.md`, fonte do `/bkhar:canonize`, que guarda o rastreio |
| specs: o corpo da feature, do teste e da task | `STATUS.md`, `CLAUDE.md`: painel e instrução de trabalho |
| treinamento e apresentações | `docs/prompts/`, `docs/history/`, `docs/input/` |
| comentário de código | — |

Quando o projeto tiver padrão próprio de escrita, ele prevalece no que divergir desta skill.

## 1. A decisão entra no texto

**O parágrafo diz o que é e se lê inteiro sozinho.** O número do ADR não aparece no meio da frase,
nem entre colchetes depois de uma afirmação. Quando a decisão ajuda a entender o parágrafo, ela
entra numa **nota de decisão** no fim dele:

```markdown
> *Decisão: {o que foi decidido, ou como isso afeta o que o parágrafo descreve} (ADR-NNN).*
```

A nota tem uma ou duas frases e se entende sem abrir o ADR. O número fica no fim, entre parênteses,
só para quem quiser auditar a origem.

- **Entra** quando o parágrafo descreve uma restrição que parece arbitrária sem a decisão.
- **Entra** quando a decisão vale para mais coisas que o parágrafo, e saber disso evita erro em
  outro lugar.
- **Não entra** quando o parágrafo já traz o argumento inteiro.
- **Uma nota por parágrafo.** Duas decisões no mesmo parágrafo indicam dois assuntos: divida.

Na spec, o vínculo formal com a decisão vai no frontmatter (`relacionada: ADR-NNN`). O corpo segue
esta skill, com nota de decisão quando ajudar.

Slide, roteiro e nota de apresentador não citam ADR, cânone nem spec. Quem assiste não tem esses
arquivos. A decisão entra como argumento na fala, sem número.

Exemplos de antes e depois em `references/exemplos.md`.

## 2. Abrir pela informação

O primeiro parágrafo de cada seção diz o que a seção afirma. Contexto, mecanismo e exceção vêm
depois. "Nesta seção será apresentado..." anuncia em vez de afirmar.

O título de seção, de slide e de bloco diz o que se aprende ali, e não apenas o nome da peça:
"A sessão guarda a conexão da execução inteira", e não "Sessão". Título com o nome da peça continua
certo em documento de referência, onde o leitor procura pelo nome.

## 3. A frase

<!-- bks-escrita: ignorar -->

- **Uma ideia por frase.** Frase com dois "e" e um "que" carrega três ideias.
- **Até 40 palavras.** Acima disso, o leitor perde o sujeito. A guarda aponta.
- **Voz ativa, com sujeito.** "O serviço abre a transação", e não "a transação é aberta".
- **Verbo simples.** "É", "tem", "faz". Evite "atua como", "possui", "se configura como".
- **Verbo, não substantivo.** "Valida a entrada", e não "realiza a validação da entrada".
- **Ritmo variado.** Três frases seguidas do mesmo tamanho cansam.
- **No máximo um parêntese por frase**, e nunca parêntese dentro de parêntese.

<!-- /bks-escrita -->

## 4. Os termos

- **Defina no primeiro uso**, em cada documento. Sigla, nome de tipo e jargão ganham meia frase de
  explicação na primeira vez.
- **Um nome por coisa.** Trocar "sessão" por "contexto" e depois por "escopo" só para variar faz o
  leitor pensar que são três coisas.
- **Crase só para identificador.** Parágrafo com metade das palavras entre crases é listagem, não
  explicação. Descreva com palavras e mostre o nome do tipo uma vez.

## 5. Concreto

- **Mostre a saída** em vez de dizer que funciona: a consulta com o resultado, o erro com o código.
- **Use um caso real**, com os valores que ele produz.
- **Número, não adjetivo.** "Cobre 128 objetos" diz mais que "cobre a maior parte".
- **Diga o limite**: o que o componente não faz, e o que acontece com entrada fora do esperado.

## 6. As muletas

<!-- bks-escrita: ignorar -->

Expressão que ocupa espaço sem dizer nada: enchimento ("vale ressaltar que"), ênfase ("robusto",
"crucial"), hesitação ("poderia eventualmente"), transição mecânica ("além disso" em todo
parágrafo), atribuição vaga ("recomenda-se"), fórmula ("não é só X, é Y"), fecho genérico. A lista
completa, com a troca de cada uma, está em `references/muletas.md`.

<!-- /bks-escrita -->

## 7. Pontuação e marcação

- **Travessão** é pontuação válida para aposto e inciso. Não serve para criar suspense, e não vai
  mais de um par por frase.
- **Negrito** marca o termo que o leitor deve fixar, no máximo um por parágrafo.
- **Sem emoji** e sem marca de severidade. Se é grave, a frase diz por quê.
- **Lista** é para itens paralelos. Causa e consequência ficam em parágrafo.

## 8. Comentário de código

Valem o teto e as categorias do `bks-standards`: contrato em uma linha, guarda contra regressão em
até duas, sem ponteiro para documento. Esta skill acrescenta o tom:

- O resumo do membro público fala com **quem chama**: o que faz e o que devolve. "Verifica se o
  texto corresponde ao valor cifrado", e não "implementa a verificação".
- A guarda contra regressão diz o que quebra: "Não é record: o `ToString()` gerado exporia a chave."
- As muletas da §6 valem também aqui.

## 9. O que a guarda confere e o que a revisão confere

O hook `writing_guard.py` roda depois de cada escrita em documentação viva e devolve ao agente o
que dá para contar. São seis achados: ADR fora da nota de decisão, nota sem síntese, frase acima de
40 palavras, sigla sem definição no documento, muleta da lista e emoji. Corrija na mesma passada, e
lembre o usuário de rodar o `/bkhar:review`, que o hook também anuncia.

Para conferir o arquivo inteiro, como item de DoD:

```
python ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/writing_guard.py <arquivo.md> [...]
```

Sai com 1 quando há achado. Exemplo de redação errada, citado de propósito, fica entre
`<!-- bks-escrita: ignorar -->` e `<!-- /bks-escrita -->`. Siglas que o leitor do projeto conhece
sem definição vão em `.bks/siglas-conhecidas.txt` na raiz do repositório, uma por linha.

O resto é da revisão, que o `/bkhar:review` conduz. Dê uma nota de 1 a 10 em cada dimensão:

| Dimensão | Pergunta |
|---|---|
| direto | o texto afirma, ou anuncia que vai afirmar? |
| ritmo | as frases variam de tamanho? |
| confiança no leitor | explica o necessário, sem repetir nem tutelar? |
| concreto | há caso real, número, saída? |
| densidade | dá para cortar algo sem perder fato? |

De 45 a 50, o texto está pronto. De 35 a 44, revise as dimensões mais fracas. Abaixo de 35,
reescreva.

## 10. Checklist de revisão

- [ ] Quem nunca viu o projeto entende cada parágrafo sem abrir outro arquivo.
- [ ] Nenhum número de ADR no corpo; decisão necessária está em nota de fim de parágrafo.
- [ ] Treinamento e apresentação não citam ADR, cânone nem spec.
- [ ] Cada seção abre pelo que afirma.
- [ ] Toda sigla e todo tipo do projeto estão definidos no primeiro uso.
- [ ] Nenhuma frase passa de 40 palavras.
- [ ] Há exemplo concreto onde há regra ou fórmula.
- [ ] Nenhuma muleta de `references/muletas.md`.
- [ ] No máximo um negrito por parágrafo; nenhum emoji.
- [ ] Nenhum fato do texto anterior se perdeu.
- [ ] Nada descreve o desenho anterior ("passa a", "antes era", "em vez de").

## Fontes externas

Duas skills públicas sob licença MIT serviram de insumo, e o texto original de cada uma está em
`third-party/`, com a licença. Elas são consulta, não norma: estão em inglês e trazem regras que
conflitam com esta skill. Antes de aplicar qualquer coisa delas, leia `references/fontes-externas.md`,
que diz o que vale, o que foi adaptado e o que foi descartado.
