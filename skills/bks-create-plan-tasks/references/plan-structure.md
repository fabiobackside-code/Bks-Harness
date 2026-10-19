# Estrutura Canônica do Plano — BKS-Create-Plans-Tasks

Template que toda geração de plano deve seguir.

---

## Template completo

```markdown
# Plano de Execução — [Título]

**Tipo:** FEATURE | BUGFIX | REFACTOR | DOCS | MIGRATION | ANALYSIS | INFRA
**Complexidade:** SIMPLES | MÉDIA | COMPLEXA
**Status:** RASCUNHO | APROVADO | EM EXECUÇÃO | CONCLUÍDO
**Criado:** [YYYY-MM-DD]
**Repositório:** [caminho local ou N/A]
**Stack:** [linguagem/framework ou N/A]

---

## §1 VISÃO GERAL

[Síntese em até 5 linhas: o que precisa ser feito, por quê, e qual a abordagem de execução.
Não descrever o "como" de cada task — isso vai no §4.]

---

## §2 MAPA DE DEPENDÊNCIAS

```
T-001 ──► T-002 ──► T-004
                └──► T-005 [PARALELO com T-004]
T-003 (independente)
```

[Se não houver dependências: "Todas as tasks são independentes."]

---

## §3 TABELA DE TASKS

| Task | Descrição | Tipo | Deps | Est. Tokens | Status |
|------|-----------|------|------|-------------|--------|
| T-001 | [nome curto] | IMPL / TEST / DOCS / INFRA / ANALYSIS | - | ~[N]k | PENDENTE |
| T-002 | [nome curto] | IMPL | T-001 | ~[N]k | PENDENTE |

**Tipos de task:**
- `IMPL` — implementação de código
- `TEST` — escrita de testes
- `DOCS` — documentação
- `INFRA` — configuração, ambiente, CI/CD
- `ANALYSIS` — investigação, leitura de código, diagnóstico
- `REFACTOR` — reestruturação de código existente

---

## §4 DETALHAMENTO DAS TASKS

### T-001 — [Nome da Task]

**Artefato de saída:** [arquivo ou resultado concreto]
**Depende de:** T-XXX | Nenhuma
**Pode ser executada em paralelo com:** T-XXX | N/A

**Arquivos a ler antes de iniciar:**
- `[caminho/arquivo.ext]` — [para que serve nesta task]
- `[caminho/outro.ext]` — [para que serve nesta task]

**O que fazer:**
1. [passo numerado, ação concreta]
2. [passo numerado, ação concreta]
3. [passo numerado, ação concreta]

**Checklist de conclusão:**
- [ ] [critério binário — SIM/NÃO]
- [ ] [critério binário — SIM/NÃO]
- [ ] [critério binário — SIM/NÃO]

**Prompt de início** *(autocontido — copiar após `/clear`):*

```
/clear

Contexto: [1-2 frases descrevendo o projeto/serviço, sem histórico da sessão]

Leia os arquivos abaixo antes de qualquer ação:
- [caminho/arquivo.ext]
- [caminho/outro.ext]

Tarefa: [descrição precisa do que produzir]

NÃO faça:
- [restrição 1]
- [restrição 2]

Produza: [artefato de saída exato]

Ao concluir, mostre o artefato gerado e aguarde instrução.
```

---

### T-002 — [Nome da Task]

[repetir estrutura acima]

---

## §5 ESTADO DE EXECUÇÃO

| Task | Status | Concluída em | Observações |
|------|--------|--------------|-------------|
| T-001 | PENDENTE | — | — |
| T-002 | PENDENTE | — | — |

---

## §6 COMO RETOMAR

```
Leia [caminho deste plano].
Identifique a primeira task com status PENDENTE na tabela §5.
Execute /clear e cole o "Prompt de início" dessa task.
Aguarde instrução após concluir cada artefato.
```
```

---

## Orientações de preenchimento

**§1 Visão Geral:** Responda "o que" e "por que agora", não "como". Deixe o "como" para §4.

**§2 Mapa de Dependências:** Use setas `──►` para dependências diretas. Indique `[PARALELO]` quando duas tasks não se bloqueiam. Se todas são independentes, diga explicitamente.

**§3 Tabela de Tasks:** Estimativa de tokens (`Est. Tokens`) é orientativa — ajuda o usuário a priorizar `/clear` entre tasks grandes. Calcular como: ~1k token ≈ 750 palavras de prompt + resposta estimada.

**§4 Detalhamento:** O "Prompt de início" é o artefato mais crítico da task. Deve ser copiável e colado diretamente após `/clear`, sem precisar de ajustes. Nunca referencie "a sessão anterior" ou "o que discutimos" — o contexto é reconstruído pelos arquivos listados.

**§5 Estado de Execução:** Atualizar conforme tasks são concluídas. É o único local de verdade sobre o progresso.

**§6 Como Retomar:** Bloco fixo. Copiar literalmente a cada plano — apenas substituir o caminho.
