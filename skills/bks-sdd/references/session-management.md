# Session Management — BKS-SDD Reference

Detalhe dos comandos transversais de sessão (`--continue`, `--tan`, `--clear`, snapshot e
`/help-workspace`). As regras que não podem faltar estão no corpo do `SKILL.md`.

---

Esta fase cobre os comandos de controle de sessão. São **transversais** — podem ser chamados
em qualquer momento, independente da fase ativa.

### Comando: `--continue`

**Trigger:** `/bks-sdd --continue` ou retorno ao workspace após pausa.

**Fluxo:**
1. Localizar folder `workspace-*` no diretório de trabalho.
2. Se não encontrar: *"Não encontrei nenhum workspace ativo. Execute `/bks-sdd` para criar um."*
3. Listar arquivos em `.states/` ordenados por data (mais recente primeiro).
4. Ler o estado mais recente.
5. Apresentar resumo:
   > *"Sessão de [data/hora] recuperada.*
   > *- Workspace: `workspace-[nome]`*
   > *- Fase ativa: [fase]*
   > *- Último passo: [descrição]*
   > *- Próximo passo sugerido: [sugestão]*
   >
   > *Deseja continuar de onde parou?"*
6. Informar o custo acumulado do processo até aqui, em uma linha — obtido com
   `session_cost.py report --json` sobre o ledger do workspace (campos `sessions`,
   `total.billable_tokens`, `total_cost_usd`):

   > _Processo até aqui: [N] sessões, [T] tokens — [US$ X]._

   Se o ledger ainda não existir, omitir a linha sem comentário.

7. Aguardar confirmação antes de retomar.

### Comando: `--tan` (That's All Now)

**Trigger:** `/bks-sdd --tan` — encerramento controlado da sessão.

**Fluxo:**
1. Avisar: *"Vou salvar o estado atual e encerrar a sessão. Confirma?"*
2. Aguardar confirmação.
3. Criar `.states/state-final-[YYYY-MM-DDTHH-MM].md` com:
   - Fase ativa no momento do encerramento
   - Resumo de tudo que foi feito na sessão
   - Próximos passos sugeridos
   - Questões em aberto
4. Adicionar entrada final no log:
   ```
   ## Sessão encerrada: [HH:MM]
   - Comando: /bks-sdd --tan
   - Estado salvo: state-final-[timestamp].md
   - Resumo: [síntese da sessão]
   ```
5. **Registrar e exibir o consumo da sessão** (Fase 7 — obrigatório, nunca pular):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py" append      --ledger "workspace-[nome]/.logs/cost-ledger.jsonl"      --phase "[fase corrente da sessão]"      --label "[resumo de 3-6 palavras da sessão]"
   ```

   Reproduzir a tabela retornada pelo script **na íntegra** — encerramento de sessão é um
   dos pontos em que o consumo é exibido, não apenas registrado. Em seguida, acrescentar o
   acumulado do processo (`report --json`, campos `total.billable_tokens` e `total_cost_usd`):

   > _Acumulado do processo até aqui: **[N] tokens — [US$ X]**._

   Copiar a mesma tabela para a seção `## Consumo da sessão` do
   `state-final-[timestamp].md` criado no passo 3, para que o `--continue` da próxima
   sessão já mostre de onde o custo partiu.

6. Confirmar: *"Estado salvo. Use `/bks-sdd --continue` na próxima sessão para retomar."*

### Comando: `--clear`

**Trigger:** `/bks-sdd --clear` ou `/clear` dentro de um workspace ativo.

**Comportamento:** Idêntico ao `--tan`, **incluindo o passo 5** (registrar e exibir o
consumo da sessão). O objetivo é que o usuário nunca perca nem o estado nem a contabilidade
de custo ao limpar a janela de conversa do Claude.

### Snapshot automático (proativo)

Criar snapshot automaticamente:
- Antes de qualquer operação longa (geração de PRD, criação de projeto)
- Quando o contexto da conversa estiver ficando extenso (~20 trocas de mensagens)

**Formato do arquivo de estado:**
```markdown
# Estado — [YYYY-MM-DDTHH:MM]

**Workspace:** workspace-[nome]
**Fase ativa:** [número e nome]
**Último comando:** [comando]
**Próximo passo sugerido:** [descrição]

## Contexto da sessão
[Síntese do que foi feito e declarado pelo usuário]

## Artefatos gerados
- [lista de arquivos criados ou modificados nesta sessão]

## Questões em aberto
- [gaps ou decisões pendentes]
```

### Comando: `/help-workspace`

**Trigger:** `/help-workspace`

**Ação:** Ler `references/workspace-structure.md` e apresentar explicação amigável de cada
folder do workspace ativo, seu propósito e quando usar.
