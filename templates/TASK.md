---
feature: specs/features/FEAT-[nome].md
test: specs/tests/TEST-[nome].md
---
# TASK-[nome]

**Padrão:** TXC | direto

| ID | Título | Peça | Depende de | Cenários | Status |
|---|---|---|---|---|---|
| T-NNN | ... | `CODIGO.TRANSACAO` · `ValidateAsync` ou n/a | — | C1, B2 | Pendente |

## T-NNN — [título]

**Status:** Pendente | Em execução | Concluída | Bloqueada
**Peça TXC alvo:** `CODIGO.TRANSACAO` · `ValidateAsync` | n/a
**Depende de:** T-NNN | nenhuma

### Instrução
Uma ação, com verbo no imperativo.

### Arquivos
- `caminho/arquivo` — o que muda

### Cenários do TEST
- C1 — [nome do cenário que o `tester` escreve como RED]

### Definição de pronto
- [ ] cenários acima verdes, build sem warning novo
- [ ] dado entre passos por retorno tipado; TXC e envelope sem mutação (só TXC)
- [ ] README.md e ARCHITECTURE.md atualizados com o que esta task produziu
- [ ] comentários seguem a convenção: contrato e guarda no código; decisão no ARCHITECTURE.md
- [ ] documentação tocada segue a skill bks-writing

### Tentativas
Preenchida pelo `/bkhar:loop`: erro e hipótese de cada tentativa que falhou.
