---
description: "Consolida a experiência dos projetos — indexa por script os ADRs e o LEARNINGS.md de repos/ e, por tema, escreve no vault o que foi decidido, descartado e revertido, com ponteiro para a origem. Roda na raiz do vault."
---

Consolida as decisões dos projetos do vault em `knowledge/wiki/experiencia/`. Rode **na raiz do
vault** (`${BKS_VAULT}`); dentro de um projeto, recuse e oriente.

## Escopo

| Fonte | Como entra |
|---|---|
| `repos/backside/`, `repos/private/` | por inteiro |
| `repos/old/` | por inteiro, marcado como histórico |
| `repos/w3/nquantic` | só conceito: tema e data no índice; na página, sem cliente, contrato, endpoint, volume ou dado operacional |
| demais de `repos/w3/` | fora |
| `backup/` | fora |

## Passo 1 — índice, sem modelo

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/harvest.py index .
python ${CLAUDE_PLUGIN_ROOT}/scripts/harvest.py themes .
```

Cole as duas saídas. O índice é incremental: só relê o arquivo que mudou.

## Passo 2 — escolher os temas

Mostre os temas com a contagem e pergunte quais consolidar agora. Sem resposta, consolide só os
temas com ADR novo desde a última página.

## Passo 3 — consolidar, um tema por vez

Leia as entradas do tema no `_index.json` e os ADRs que elas apontam. Escreva
`knowledge/wiki/experiencia/<tema>.md` com:

- o que foi decidido e em quais projetos;
- o que foi descartado, e por quê;
- o que foi revertido ou superado, e pelo quê;
- toda linha com o ponteiro para o ADR de origem (`repos/<categoria>/<projeto>/decisions/ADR-NNN`).

O ADR do projeto segue fonte; a página só sintetiza. Do `nquantic`, só o conceito, sem ponteiro de
arquivo: "uma decisão do `nquantic` sobre <tema>, em <data>".

## Passo 4 — checar antes de gravar

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/harvest.py check --page knowledge/wiki/experiencia/<tema>.md .
```

Saída 1: a página tem termo da lista de bloqueio (`knowledge/wiki/experiencia/_bloqueio.txt`) ou
dado sensível, e é recusada. Corrija e cheque de novo; nunca edite a lista para a página passar.

## Fechar

Acrescente a linha do harvest em `knowledge/wiki/log.md` e as páginas novas em
`knowledge/wiki/index.md`. Não commite. Mostre os arquivos tocados.

Responda em português do Brasil.
