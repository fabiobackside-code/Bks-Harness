# Custo & Telemetria (Fase 7) — BKS-SDD Reference

Registro de consumo no ledger, `--cost`, `--cost-report`, conclusão do projeto e nota no vault.

---

Mede o consumo de tokens e o custo estimado do processo BKS-SDD, para comparar modelos,
comparar projetos e identificar as fases mais caras do fluxo.

**Ferramenta:** `${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py`
**Tabela de preços:** `${CLAUDE_PLUGIN_ROOT}/scripts/pricing.json` (USD por 1M tokens, editavel)
**Ledger do workspace:** `workspace-[nome]/.logs/cost-ledger.jsonl`

O ledger e um arquivo JSONL append-only, uma entrada por (sessão x fase). Como o transcript
de uma sessão e cumulativo, uma segunda gravação da mesma sessão+fase **substitui** a anterior
em vez de somar — o total nunca infla por gravar duas vezes.

> **Sempre apresentar o custo como estimativa.** O valor vem dos tokens registrados no
> transcript multiplicados pela tabela local de preços. Não e a fatura oficial da Anthropic,
> e planos de assinatura com valor fixo não cobram por token.

---

### Registro automático de consumo

Registrar no ledger **automaticamente**, sem o usuário pedir, ao concluir:

| Gatilho | Rotulo de fase a usar |
|---------|----------------------|
| `--prd` | `Fase 1 — PRD de Workspace` |
| `--project-prd` | `Fase 3 — PRD de Projeto` |
| `--project-plan` | `Fase 4 — Plano Macro` |
| `--feature` | `Fase 5.1 — Feature Spec` |
| `--feature-tests` | `Fase 5.2 — Test Scenarios` |
| `--feature-task` | `Fase 5.3 — Tasks` |
| `--task-done` | `Fase 6 — Implementação` |

Comando (Bash):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py" append \
  --ledger "workspace-[nome]/.logs/cost-ledger.jsonl" \
  --phase "Fase 5.1 — Feature Spec" \
  --label "FEAT-autenticação"
```

Nesses gatilhos o registro e **silencioso**: não exibir a tabela, apenas anexar uma linha
ao final da resposta:

> _Consumo registrado no ledger — acumulado do processo: [N] tokens, [US$ X]._

Obter o acumulado com `report --json` e ler `total.billable_tokens` e `total_cost_usd`.

**Gatilhos que registram E exibem a tabela completa** — todo encerramento de sessão, porque
e o momento em que o usuário quer ver o que a sessão custou:

| Gatilho | Rotulo de fase | Exibição |
|---------|----------------|----------|
| `--tan` | fase corrente da sessão | tabela completa + acumulado |
| `--clear` | fase corrente da sessão | tabela completa + acumulado |
| `/bkhar:save` | fase corrente da sessão | tabela completa + linha TOTAL GERAL |

Ou seja: **qualquer comando que salve e encerre uma sessão traz o resumo de consumo junto**,
sem o usuário precisar pedir.

**Se o script falhar** (Python ausente, transcript não encontrado, ledger sem permissão):
informar em uma linha e prosseguir. A telemetria nunca bloqueia o fluxo SDD.

---

### Comando `--cost` — Consumo da sessão atual

**Trigger:** `/bks-sdd --cost`

Mostra a tabela detalhada da sessão em curso, sem gravar no ledger:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py" session
```

Reproduzir a saída do script na integra.

---

### Comando `--cost-report` — Consumo total do processo

**Trigger:** `/bks-sdd --cost-report`, ou o convite automático na conclusão do projeto
(ver seção seguinte).

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py" report \
  --ledger "workspace-[nome]/.logs/cost-ledger.jsonl"
```

Reproduzir a saída na integra (por modelo, por fase, total geral) e complementar com uma
leitura analitica curta:

- Qual fase consumiu mais e por que (spec longa? muitas revisões? implementação com retry?)
- Proporção cache read vs input — read alto e bom sinal (contexto reaproveitado)
- Output tokens por fase — proxy do volume de artefato gerado
- Se houver mais de um modelo no ledger: custo por token entregue em cada um

Ao final, gravar o relatorio consolidado em
`workspace-[nome]/.logs/COST-REPORT-[YYYY-MM-DD].md` e informar o caminho ao usuário.

---

### Conclusão do projeto — última etapa obrigatória

Quando o processo BKS-SDD chega ao fim — a última task da última feature e marcada
Concluida e não restam features pendentes no `--status` — o relatorio de conclusão do
projeto e apresentado normalmente. **A última etapa desse relatorio, sempre, e perguntar
se o usuário quer o consolidado de consumo.**

Não gerar o consolidado automaticamente. Perguntar:

> **Projeto concluido.** Deseja o resumo consolidado de consumo de tokens e custo de todo
> o processo — por fase, por modelo e total geral?
>
> _Ja registrei [N] sessões no ledger, somando **[T] tokens — [US$ X]**. O consolidado abre
> essa soma por fase e por modelo, e fica salvo para comparar com outros projetos._

Obter `[N]`, `[T]` e `[US$ X]` com `report --json` (campos `sessions`,
`total.billable_tokens`, `total_cost_usd`) — assim a pergunta já mostra a ordem de
grandeza e o usuário decide informado.

**Se aceitar:** executar o fluxo completo do `--cost-report` acima — leitura analitica,
arquivo `COST-REPORT-[data].md` e nota no Obsidian (seção seguinte).

**Se recusar:** informar que o ledger continua gravado e que `/bks-sdd --cost-report` gera
o consolidado a qualquer momento depois. Não insistir.

---

### Integração com o Obsidian (segundo cerebro)

O workspace guarda o dado bruto; o vault guarda a leitura consolidada, que e o que serve
para comparar projetos meses depois.

Ao gerar o `--cost-report`, além do `COST-REPORT-[data].md` no workspace, gravar uma nota em:

```
{repo}/outputs/custos/custo-[projeto]-[YYYY-MM-DD].md
```

Formato da nota (PT-BR, com frontmatter para o Obsidian indexar e permitir Dataview):

```markdown
---
tipo: custo-projeto
projeto: [nome do projeto]
workspace: workspace-[nome]
data: YYYY-MM-DD
modelo_principal: [modelo com maior custo no ledger]
sessões: [N]
tokens_total: [T]
custo_usd: [X]
---

# Custo do projeto [nome]

[tabela por modelo — copiada do relatorio]

[tabela por fase — copiada do relatorio]

## Leitura

[analise curta: fase mais cara e por que, proporção cache read, comparação entre modelos]

## Comparação

[[custo-outro-projeto-...]] — se houver notas anteriores em `memory/custos/`, referenciar
as mais proximas em escopo para comparação direta.

Ledger de origem: `workspace-[nome]/.logs/cost-ledger.jsonl`
```

Criar o folder `outputs/custos/` se não existir. Ao final, acrescentar uma entrada no
`JOURNAL.md` do projeto apontando para a nota.

Os wikilinks `[[...]]` são o que permite, no Obsidian, abrir o grafo de custos e comparar
projetos lado a lado sem nenhum agregador externo.

---

### Comparação entre projetos

Os ledgers são arquivos independentes por workspace. Para comparar dois projetos, rodar
`report --json` em cada ledger e confrontar `total_cost_usd`, `total.billable_tokens` e a
quebra `by_phase`. Não existe agregador global — a comparação e explicita e sob demanda.

### Manutenção da tabela de preços

Quando os preços oficiais mudarem, editar `${CLAUDE_PLUGIN_ROOT}/scripts/pricing.json`
(valores em USD por 1.000.000 de tokens) e atualizar o campo `_updated`. Modelos ausentes
da tabela aparecem no relatorio marcados com `(!)` e contam custo zero — sinal de que a
tabela precisa de uma entrada nova.
