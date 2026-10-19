# Regras de Decomposição de Tasks — BKS-Create-Plans-Tasks

Regras obrigatórias ao decompor qualquer trabalho em tasks. Aplicar sempre, sem exceção.

---

## Regra 1 — ATOMICIDADE

Cada task produz **exatamente 1 artefato verificável** com critério binário (FEITO / NÃO FEITO).

**Artefato válido:**
- Um arquivo criado ou modificado
- Um conjunto de testes passando
- Uma configuração aplicada e verificada
- Um documento gerado

**Artefato inválido:**
- "Melhorar o código" (sem arquivo ou critério definido)
- "Refatorar onde necessário" (escopo aberto)
- "Verificar se funciona" (ação, não artefato)

**Critério binário:** A checklist de conclusão deve ter itens com resposta SIM/NÃO.
- Ruim: "código bem estruturado"
- Bom: "arquivo `OrderService.cs` com menos de 200 linhas"

---

## Regra 2 — AUTOCONTIDO

O **Prompt de início** de cada task deve ser copiável e executável após `/clear`,
sem depender de memória da sessão anterior ou de contexto implícito.

**Deve incluir:**
- Contexto mínimo do projeto (1-2 frases)
- Lista exata dos arquivos a ler
- Descrição precisa do que produzir
- Restrições relevantes para essa task
- O artefato de saída esperado

**Não deve incluir:**
- Referências a "o que discutimos antes"
- "Como combinado" ou "conforme acordado"
- Contexto de outras tasks (cada uma é independente)

---

## Regra 3 — TAMANHO

**Task grande (>200 linhas de código):** 1 arquivo por task.

**Tasks pequenas:** podem ser agrupadas, máx 3 por task, somente se:
- São do mesmo tipo (ex: 3 arquivos de configuração)
- Nenhuma depende de outra dentro do grupo
- O prompt de início ainda é autocontido

**Operações destrutivas** (mover arquivo, deletar, renomear, alterar schema): sempre em task separada.
Justificativa: operações destrutivas têm impacto imprevisível e devem ser verificadas isoladamente.

---

## Regra 4 — /clear OBRIGATÓRIO

Declarar `/clear` no início do prompt de cada task.

**`/clear` é obrigatório quando:**
- Geração de código (qualquer linguagem)
- Geração de arquivos de configuração
- Modificação de múltiplos arquivos
- Task com estimativa > 2k tokens

**`/clear` é opcional quando:**
- Task puramente de análise (leitura + resposta curta)
- Task de documentação de 1 arquivo pequeno

Mesmo quando opcional, incluir `/clear` por padrão. O custo é zero; o benefício é contexto limpo.

---

## Regra 5 — DEPENDÊNCIAS E PARALELISMO

Mapear dependências entre tasks e identificar oportunidades de execução em paralelo.

**Dependência real:** T-002 usa o artefato de T-001 como entrada.
**Não é dependência:** T-002 é sobre o mesmo tema que T-001, mas não precisa do artefato.

**Indicar `[PARALELO]`** quando duas tasks não se bloqueiam — o usuário pode executá-las em agentes separados ou simplesmente na sequência que preferir.

**Ordenar tasks:**
1. Tasks sem dependências primeiro
2. Tasks que desbloqueiam mais tasks seguintes têm prioridade
3. Tasks de teste após as de implementação correspondente
4. Tasks de documentação por último (exceto se forem pré-requisito de implementação)

---

## Regra 6 — STATUS

Usar apenas os status abaixo, sem variações:

| Status | Quando usar |
|--------|-------------|
| `PENDENTE` | task ainda não iniciada |
| `EM CURSO` | task iniciada, artefato não entregue |
| `CONCLUÍDA` | artefato entregue e checklist confirmada |
| `BLOQUEADA` | dependência não resolvida ou impedimento externo |
| `IGNORADA` | decisão de não executar (com motivo registrado) |

---

## Otimizações de tokens — Orientações da Anthropic

Aplicar em todos os prompts de task gerados para reduzir consumo de tokens sem perder qualidade:

### 1. Contexto mínimo suficiente
Incluir apenas o contexto necessário para executar a task corretamente.
Não copiar o contexto geral do projeto em cada prompt — referenciar o arquivo.

```
✅ Bom: "Leia src/Application/UseCases/CreateOrderUseCase.cs antes de iniciar."
❌ Ruim: [colar 300 linhas do arquivo diretamente no prompt]
```

### 2. Instruções negativas antes de positivas
Listar o que NÃO fazer primeiro evita que o modelo inicie na direção errada e precise corrigir.

```
✅ Bom:
NÃO faça:
- Altere migrations existentes
- Adicione dependências sem confirmação

Produza:
- Novo endpoint POST /orders em OrderEndpoints.cs

❌ Ruim:
Produza um novo endpoint POST /orders. Não altere migrations. Não adicione pacotes.
```

### 3. Formato explícito de saída
Especificar o formato do artefato esperado reduz iterações de correção.

```
✅ Bom: "Produza o arquivo OrderEndpoints.cs completo, pronto para substituir o existente."
❌ Ruim: "Atualize o endpoint conforme necessário."
```

### 4. Sem contexto repetido entre tasks
Cada task referência apenas o que precisa. O contexto geral do projeto não é copiado de task para task.

### 5. Critério de parada explícito
Toda task termina com: *"Ao concluir, mostre o artefato gerado e aguarde instrução."*
Evita que o modelo continue para a próxima task sem aprovação.

### 6. Estimativa de tokens por task
Incluir estimativa orientativa na tabela §3 (`Est. Tokens`).
Critério para `ALTA` estimativa (marcar `~4k+`): geração de arquivo >150 linhas, múltiplos arquivos, ou análise de código extenso.
Tasks com estimativa alta são candidatas prioritárias ao `/clear` entre elas.

---

## Exemplos de decomposição por tipo de trabalho

### FEATURE nova — padrão hexagonal

```
T-001 [ANALYSIS] — Ler código existente e mapear pontos de integração
T-002 [IMPL]     — Criar entidade e value objects no Domain          (deps: T-001)
T-003 [IMPL]     — Criar Port interfaces (Application + Outbound)    (deps: T-002)
T-004 [IMPL]     — Implementar UseCase                               (deps: T-003)
T-005 [IMPL]     — Implementar Repository (adapter outbound)         (deps: T-003) [PARALELO com T-004]
T-006 [IMPL]     — Implementar endpoint (adapter inbound)            (deps: T-004)
T-007 [TEST]     — Testes unitários do UseCase                       (deps: T-004)
T-008 [TEST]     — Testes de integração do endpoint                  (deps: T-006, T-005)
```

### BUGFIX — padrão mínimo

```
T-001 [ANALYSIS] — Reproduzir o bug e identificar a causa raiz
T-002 [IMPL]     — Aplicar a correção                                (deps: T-001)
T-003 [TEST]     — Escrever teste que falha sem a correção            (deps: T-001) [PARALELO com T-002]
```

### REFACTOR — padrão seguro

```
T-001 [TEST]     — Escrever testes de regressão cobrindo comportamento atual
T-002 [ANALYSIS] — Mapear responsabilidades e propor nova estrutura   (deps: T-001)
T-003 [REFACTOR] — Extrair [Responsabilidade A] para nova classe      (deps: T-001, T-002)
T-004 [REFACTOR] — Extrair [Responsabilidade B] para nova classe      (deps: T-001, T-002) [PARALELO com T-003]
T-005 [TEST]     — Confirmar que todos os testes de regressão passam  (deps: T-003, T-004)
```
