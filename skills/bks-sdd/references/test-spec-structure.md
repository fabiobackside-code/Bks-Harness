# Test Spec Structure — BKS-SDD Reference

Este documento define o template canônico do `TEST-[nome].md` gerado pela Fase 6 da skill BKS-SDD.
Cada feature aprovada pode ter exatamente um arquivo de test spec, criado **antes** das tasks de
implementação. O TEST-[nome].md é o artefato que define o que deve ser verdadeiro para a feature
ser considerada completa — ele precede e orienta a implementação.

---

## Template

```markdown
# Test Spec — [Nome da Feature]

**Feature:** F[N] — [nome da feature]
**Arquivo de feature:** FEAT-[nome].md
**Projeto:** project-[nome]
**Status:** Draft | Aprovada
**Criado:** [YYYY-MM-DD]
**Atualizado:** [YYYY-MM-DD]

---

## 1. Objetivo

[1–2 frases. Descreve o que está test spec valida e por que esses cenários foram escolhidos.
Não repetir a descrição da feature — focar no ângulo de verificação.]

## 2. Cenários Principais (Happy Path)

Cenários do fluxo esperado, em formato Gherkin (Given/When/Then).
Cada cenário deve cobrir exatamente um critério de aceite do FEAT-[nome].md §2.

### Cenário 1 — [Nome descritivo]

```gherkin
Given [estado inicial do sistema ou contexto do ator]
When  [ação executada pelo ator ou sistema]
Then  [resultado esperado verificável]
```

**Critério de aceite coberto:** [referência ao item do §2 do FEAT]

### Cenário 2 — [Nome descritivo]

```gherkin
Given [estado inicial]
When  [ação]
Then  [resultado esperado]
And   [resultado adicional, se necessário]
```

**Critério de aceite coberto:** [referência ao item do §2 do FEAT]

[repetir para cada critério de aceite do FEAT]

## 3. Cenários de Borda (Edge Cases)

Casos derivados dos Comportamentos de Borda do FEAT-[nome].md §3.
Cada linha da tabela de borda do FEAT deve ter pelo menos um caso aqui.

| # | Situação | Entrada / Condição | Resultado esperado | Tipo |
|---|----------|-------------------|-------------------|------|
| E1 | [ex: payload vazio] | [ex: body: {}] | [ex: HTTP 400, mensagem "payload obrigatório"] | Validação |
| E2 | [ex: timeout na dep. externa] | [ex: serviço X indisponível] | [ex: HTTP 503, evento registrado no log] | Resiliência |
| E3 | [ex: requisição duplicada] | [ex: mesmo ID enviado duas vezes] | [ex: HTTP 200 com resultado da primeira operação] | Idempotência |

**Tipos de borda aceitos:**
- `Validação` — entrada inválida ou fora do contrato esperado
- `Resiliência` — falha em dependência externa ou timeout
- `Idempotência` — operação repetida deve produzir mesmo resultado
- `Concorrência` — múltiplos atores acessando o mesmo recurso simultaneamente
- `Limite` — valores no extremo permitido (zero, máximo, string vazia)
- `Segurança` — tentativa de acesso não autorizado ou bypass de validação

## 4. Cenários Fora de Escopo

Casos que explicitamente NÃO serão testados nesta feature, com justificativa.
Isso evita que o agente implementador os inclua por conta própria.

| Caso | Motivo para não testar aqui |
|------|-----------------------------|
| [ex: performance sob carga] | [ex: coberto por suite de load test separada] |
| [ex: validação de campos do módulo X] | [ex: responsabilidade da feature F3] |

## 5. Pré-condições de Ambiente

O que deve estar configurado ou disponível para que estes testes possam ser executados.

- [ex: banco de dados com schema migrado]
- [ex: serviço de autenticação disponível (pode ser mock)]
- [ex: variável de ambiente `PAYMENT_API_URL` configurada]

## 6. Rastreabilidade

- **Feature:** `spec/features/FEAT-[nome].md` — §2 Critérios de Aceite (origem dos cenários principais)
- **Feature:** `spec/features/FEAT-[nome].md` — §3 Comportamentos de Borda (origem dos edge cases)
- **Plano:** `plan/PLAN-[nome].md` — §3 linha F[N]
```

---

## Orientações campo a campo

**Cenários Principais (§2):** Cada cenário cobre exatamente **um** critério de aceite do FEAT.
Relação 1:1 mínima — um critério pode ter mais de um cenário, mas cada cenário cobre só um
critério. Se um critério do FEAT não tiver cenário correspondente aqui, a test spec está incompleta
e não pode ser aprovada.

Regras para o Gherkin:
- `Given` descreve o estado do mundo antes da ação — não a ação em si
- `When` é sempre uma ação singular: uma chamada de API, um evento, um clique
- `Then` descreve o estado do mundo depois — não o processo que levou a ele
- `And` pode ser usado após qualquer step, mas nunca como primeiro step
- Sem condicional no Gherkin (`if`, `or`) — separar em cenários distintos
- Sem `But` — usar outro cenário para o comportamento alternativo

**Cenários de Borda (§3):** Derivados diretamente do §3 do FEAT. Se o FEAT tem 4 linhas na
tabela de borda, esta seção deve ter no mínimo 4 linhas. Casos implícitos não documentados
no FEAT podem ser adicionados, mas devem ser justificados.

A coluna **Tipo** é obrigatória — ajuda o agente implementador a entender o que está sendo
testado e escolher a estratégia de implementação correta.

**Cenários Fora de Escopo (§4):** Esta seção é tão importante quanto os cenários positivos.
Um agente sem esta seção pode implementar testes de responsabilidade de outra feature,
criando acoplamento indesejado entre specs. Mínimo: 1 linha. Se nenhum caso se aplicar,
escrever: *"Nenhum caso identificado como fora de escopo para esta feature."*

**Pré-condições de Ambiente (§5):** Listar apenas o que é específico para esta feature —
não listar dependências genéricas do projeto. Se uma pré-condição deve ser configurada
pelo agente como parte das tasks, indicar isso explicitamente.

---

## Nome do arquivo

Formato: `TEST-[nome-kebab-case].md`

O nome deve ser **idêntico** ao nome do `FEAT-[nome].md` correspondente:
- `FEAT-validação-autorização-transação.md` → `TEST-validação-autorização-transação.md`
- `FEAT-registro-atomico-debito-credito.md` → `TEST-registro-atomico-debito-credito.md`

Isso garante rastreabilidade imediata: dado qualquer FEAT, o TEST correspondente é encontrado
em `spec/tests/TEST-[mesmo-nome].md` sem busca adicional.

---

## Ciclo de vida do status

```
Draft → Aprovada
```

- `Draft`: gerado pela skill, ainda não revisado pelo usuário
- `Aprovada`: usuário revisou e aprovou — desbloqueia o comando `--feature-task`

**Importante:** o `--feature-task` só gera tasks de implementação se o `TEST-[nome].md`
correspondente tiver `Status: Aprovada`. Esta é a garantia TDD estrutural do fluxo BKS-SDD —
nenhuma task de implementação existe sem test spec aprovada.

---

## Relação com outros artefatos

```
FEAT-[nome].md (Fase 5)
    ↓ §2 Critérios de Aceite  → alimenta §2 Cenários Principais (1:1 mínimo)
    ↓ §3 Comportamentos de Borda → alimenta §3 Cenários de Borda

TEST-[nome].md (Fase 6) ← este documento
    ↓ aprovação → desbloqueia /bks-sdd --feature-task
    ↓ §2 e §3   → referenciados nos critérios de aceite das TASKs

TASK-[id]-[descrição].md (Fase 5, gerada após aprovação do TEST)
    ↑ campo "Test Spec:" → referência este arquivo
    ↑ "Definição de pronto" → inclui "cenários do TEST-[nome].md passando"
```

---

## Decisões de design adotadas

1. **Happy path em Gherkin, edge cases em tabela:** Gherkin é mais legível para cenários
   narrativos e facilita revisão humana. Tabela é mais densa e adequada para edge cases
   que seguem padrão repetitivo de entrada/saída.

2. **Nome do arquivo idêntico ao FEAT:** Elimina ambiguidade de rastreabilidade. Dado
   qualquer FEAT, o TEST correspondente é `spec/tests/TEST-[mesmo-nome].md`.

3. **Bloqueio estrito do `--feature-task`:** O comando não gera tasks de implementação
   sem TEST aprovado. Não é configurável por projeto — é uma garantia estrutural do fluxo
   BKS-SDD. Projetos que não querem testes simplesmente não executam a Fase 6 e usam
   `--feature-task` diretamente a partir da Fase 5.

4. **Seção "Fora de Escopo" obrigatória:** Previne que o agente implemente testes de
   responsabilidade alheia, mantendo os limites da feature bem definidos e o acoplamento
   entre specs sob controle.

5. **`spec/tests/` paralelo a `spec/features/` e `spec/tasks/`:** Reflete visualmente a
   ordem do ciclo: features → tests → tasks. A simetria de nomenclatura (FEAT/TEST/TASK)
   torna a relação entre artefatos imediata sem necessidade de consulta à documentação.
