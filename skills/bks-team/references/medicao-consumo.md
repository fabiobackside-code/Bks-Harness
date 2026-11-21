# Medição de consumo

> Chamado pelo `/bkhar:save` no passo final. Depende de `scripts/session_cost.py`, que o kit versiona.
> Se o Python ou o script não estiverem disponíveis, informe em uma linha e siga - a falha da
> medição nunca bloqueia o `/bkhar:save`.

## Onde está o script

O script vive em `${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py` e lê o `pricing.json` ao lado
dele. Não há cópia fora do plugin: a instalação em `~/.claude/scripts/` foi removida em 2026-09-15.

Se o script não existir, ou o Python não estiver disponível, escreva "medição pulada:
session_cost.py não encontrado" e encerre o `/bkhar:save` normalmente. Não instale nada, não peça para
instalar.

Depois de gravar tudo acima, meça o consumo desta sessão e mostre ao usuário.

**Passo 1 — localizar o ledger.** O ledger é `{repo do projeto}/.logs/cost-ledger.jsonl`. Se a
sessão não estiver dentro de um repositório de projeto, use
`${BKS_VAULT}/workbench/.logs/cost-ledger.jsonl`.

**Passo 2 — determinar a fase.** Use o rótulo da fase bks-sdd em que a sessão trabalhou (ex.:
`Fase 5.1 — Feature Spec`, `Fase 6 — Implementação`). Fora de um fluxo bks-sdd, use um rótulo
curto do trabalho feito (ex.: `manutencao`, `spike`).

**Passo 3 — executar** (Bash, uma linha):

```bash
python "<script localizado acima>" append \
  --ledger "<caminho do passo 1>" \
  --phase "<rótulo do passo 2>" \
  --label "<resumo de 3-6 palavras do que a sessão fez>"
```

**Passo 4 — exibir.** Reproduza a saída do script na íntegra (a tabela markdown já vem pronta).
Acrescente uma linha final com o acumulado do processo:

```bash
python "<script localizado acima>" report --ledger "<mesmo caminho>"
```

Do relatório acumulado, mostre apenas a linha **TOTAL GERAL** — o detalhamento completo fica para
o fechamento do bks-sdd (`--cost-report`).

**Passo 5 — painel `custo-tokens.md`.** Além do ledger JSONL (o registro fino, por checkpoint),
atualize o arquivo que o Dataview lê direto (`FROM "" WHERE tipo = "custo-tokens"`, sem caminho
fixo).

- **Onde:** `{repo do projeto}/.logs/custo-tokens.md` — por projeto. Cada projeto tem o seu; um
  arquivo único e compartilhado seria sobrescrito quando dois projetos rodassem `/bkhar:save` no mesmo
  dia.
- **Se não existir:** crie com frontmatter e uma tabela de checkpoints:
  ```
  ---
  tipo: custo-tokens
  workspace: {nome do projeto/repo}
  acumulado_usd: {custo deste checkpoint, número puro}
  checkpoints: 1
  ultima_atualizacao: YYYY-MM-DD
  ---

  | Data/hora | Fase | Custo do checkpoint | Acumulado |
  |---|---|---|---|
  | {timestamp} | {rótulo do passo 2} | {custo} | {acumulado_usd} |
  ```
- **Se já existir:** acrescente uma linha na tabela e atualize o frontmatter (`acumulado_usd` soma
  o novo checkpoint, `checkpoints` incrementa, `ultima_atualizacao` vira hoje). Nunca recrie do
  zero — isso apagaria o histórico do projeto.
- Extraia o custo do checkpoint e o acumulado do que o `session_cost.py` já reportou nos passos 3
  e 4 — não recalcule por fora do script.

**Passo 6 — registrar no `JOURNAL.md`.** Acrescente a tabela do passo 4 à entrada da sessão, sob o
subtítulo `### Consumo da sessao` (grafado assim, sem acento, porque os `JOURNAL.md` existentes já
usam esse título), junto com o acumulado do processo. Se a entrada do dia já tiver essa seção
(segundo `/bkhar:save` no mesmo dia), **substitua** a tabela em vez de acrescentar outra — o
snapshot é cumulativo, duas tabelas confundiriam.

**Passo 7 — síntese de modelos.** Se o relatório trouxe a tabela de subagentes, reproduza-a na
entrada do `JOURNAL.md`, sob o subtítulo `### Modelos usados`, junto com uma linha do que os
agentes fizeram nesta sessão. Sem subagente na sessão, pule sem comentar.

A tabela responde onde cada tier foi gasto. Ela existe para calibrar a escolha do modelo com dado,
não com opinião: agente que consome muito e entrega pouco é candidato a baixar de tier; agente
barato que gera retrabalho é candidato a subir. Ver `docs/ARCHITECTURE.md`.

Dois limites a respeitar ao ler:

- O tier vem do que o agente **declara**, não do que a plataforma reportou — a notificação de
  conclusão traz tokens, não modelo.
- Os tokens do subagente **não entram no custo** da tabela principal, que só vê o thread da
  sessão. Somar os dois por fora seria inventar preço para token cujo tier é inferido.

**Se o script ou o passo 5 falharem** (Python ausente, transcript não encontrado, `custo-tokens.md`
ilegível): informe o erro em uma linha e siga — a falha da medição nunca bloqueia o `/bkhar:save`.

**Nunca** afirme que o valor é a fatura real. É estimativa por token contra a tabela local
`pricing.json`, ao lado do script.
