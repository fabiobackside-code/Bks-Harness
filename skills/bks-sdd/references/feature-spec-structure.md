# Feature Spec Structure — BKS-SDD Reference

Este documento define o template canônico do `FEAT-[nome].md` gerado pela Fase 5 da skill BKS-SDD.
Cada feature do `PLAN-[nome].md` gera exatamente um arquivo seguindo esta estrutura.

---

## Template

```markdown
# Feature Spec — [Nome da Feature]

**ID:** F[N]
**Projeto:** project-[nome]
**Plano de referência:** PLAN-[nome].md
**Fase de execução:** Fase [N]
**Prioridade:** P0 / P1 / P2
**Status:** Draft | Review | Aprovada | Em execução | Concluída
**Criado:** [YYYY-MM-DD]

---

## 1. Descrição

[O que esta feature faz e para quem. 2–4 frases. Sem jargão técnico desnecessário.
Deve ser compreensível por alguém que não leu o PRD. Responde: "o que é", "por que existe"
e "quem usa".]

## 2. Critérios de Aceite

Lista binária — cada item é "passou" ou "não passou". Sem ambiguidade.
Cada critério deve ser verificável por um agente ou testador sem interpretação adicional.

- [ ] [critério testável 1 — começa com verbo no infinitivo]
- [ ] [critério testável 2]
- [ ] [critério testável 3]

## 3. Comportamentos de Borda

Casos que não são o fluxo principal mas precisam ser tratados explicitamente.
Se um comportamento de borda não estiver aqui, o agente implementador pode ignorá-lo.

| Situação | Comportamento esperado |
|----------|------------------------|
| [ex: requisição com payload vazio] | [ex: retorna HTTP 400 com mensagem "payload obrigatório"] |
| [ex: timeout na dependência externa] | [ex: retorna HTTP 503 e registra evento no log de erros] |
| [ex: valor duplicado / idempotência] | [ex: retorna HTTP 200 com o resultado da operação anterior] |

## 4. Restrições Técnicas

Limites que o agente implementador deve respeitar.
Não são sugestões — são restrições que invalidam a implementação se violadas.

- [ex: não chamar serviços externos de forma síncrona — usar fila assíncrona]
- [ex: tempo de resposta máximo de 200ms no p95]
- [ex: não armazenar PII em logs]
- [ex: seguir o contrato de interface definido em `contracts/[arquivo]`]

## 5. Contratos de Dados

**Padrão de implementação:** [TXC | ALT-1 QueryHandler | ALT-1 SimpleCommandHandler | ALT-2 QueryComposer | ALT-3 BatchProcessor | ALT-4 UtilityScript]

> Preenchido pelo Passo 5F.4 da skill (árvore de decisão TXC vs ALT). Obrigatório para projetos .NET e TypeScript.
> Para regras completas, ver `references/txc-guidelines.md`.

**Se TXC — Transaction Map:**

| Fase | Método Semântico | Responsabilidade | Estado Intermediário |
|------|------------------|------------------|----------------------|
| 1. Hydrate | `HydrateXxx(input)` | Popula campos de entrada na Transaction | `tx.Campo1`, `tx.Campo2` |
| 2. Apply | `HydrateXxxCriado(aggregate)` | Chama domínio, captura aggregate | `tx.Aggregate` |
| 3. Finalize | `FinalizeWith(aggregate)` | Prepara PipelineResult com Response | `PipelineResult<Response>` |

**Se ALT — Contrato simplificado:**

- **Input:** [tipo de entrada — ex: `Guid id`, `ListRequest query`]
- **Output:** `PipelineResult<[TipoResponse]>`

## 6. Tasks desta Feature

Preenchido após execução de `/bks-sdd --feature-task`.
Enquanto vazio, o status desta feature é "Aprovada" mas não "Em execução".

| ID | Descrição | Dependência |
|----|-----------|-------------|
| TASK-001 | [descrição curta — começa com verbo] | nenhuma |
| TASK-002 | [descrição curta] | TASK-001 |

## 7. Rastreabilidade

- **Plano:** `PLAN-[nome].md` — §3 Features Previstas, linha F[N]
- **PRD:** `PRD-[nome].md` — §5 Requisito R[N]
- **Workspace PRD:** `research/PRD.md` — §[seção relevante] *(se aplicável)*

## 8. Test Spec

Preenchido após execução de `/bks-sdd --feature-tests` (Fase 6).
Enquanto não aprovado, o comando `/bks-sdd --feature-task` fica bloqueado para esta feature.

- **Arquivo:** `spec/tests/TEST-[nome].md`
- **Status:** *(pendente | Draft | Aprovada)*
```

---

## Orientações campo a campo

**ID (F[N]):** Deve corresponder exatamente ao ID na tabela §3 do `PLAN-[nome].md`.
Nunca renumerar — se uma feature for removida, o ID fica vago (não reutilizar).

**Status:** O ciclo de vida correto é:
```
Draft → Review → Aprovada → Em execução → Concluída
```
- `Draft`: gerado pela skill, ainda não revisado pelo usuário
- `Review`: usuário está revisando critérios de aceite
- `Aprovada`: usuário aprovou — pronto para `/bks-sdd --feature-task`
- `Em execução`: tasks geradas e pelo menos uma em andamento
- `Concluída`: todos os critérios de aceite verificados

**Descrição (§1):** Três perguntas que a descrição deve responder:
1. O que esta feature entrega? (funcionalidade)
2. Por que ela existe? (valor para o produto)
3. Quem a usa diretamente? (usuário final, outro serviço, agente)

**Critérios de Aceite (§2):** Regras de ouro:
- Cada critério começa com verbo no infinitivo: "Retornar", "Persistir", "Validar", "Publicar"
- Cada critério é binário: ou passou ou não passou — sem "parcialmente"
- Máximo 7 critérios. Se precisar de mais, a feature está grande demais para uma spec

**Comportamentos de Borda (§3):** A ausência de um caso aqui significa que o agente pode
escolher qualquer comportamento. Se um comportamento é importante, documente.
Mínimo: 2 linhas. Máximo: 8 linhas — se precisar de mais, extraia uma nova feature.

**Restrições Técnicas (§4):** Diferença entre restrição e sugestão:
- Restrição: "não usar chamada síncrona para o serviço X" (violação invalida a task)
- Sugestão: "considerar cache para reduzir latência" (não é restrição — não coloque aqui)

**Contratos de Dados (§5):** Preenchido pelo Passo 5F.4 da skill (árvore de decisão TXC vs ALT).
Para projetos .NET ou TypeScript: campo `Padrão de implementação` obrigatório; se TXC, preencher a tabela Transaction Map com as fases e métodos semânticos da operação.
Ver `references/txc-guidelines.md` Seções 2 e 5 para a árvore de decisão e template da tabela.

**Tasks (§6):** Preenchido automaticamente por `/bks-sdd --feature-task`.
Não preencher manualmente — a skill atualiza esta seção e cria os arquivos correspondentes.
**Atenção:** o `--feature-task` só é desbloqueado após o `TEST-[nome].md` correspondente
estar com `Status: Aprovada` (§8). Ver Fase 6.

**Rastreabilidade (§7):** A skill preenche automaticamente com base no projeto e plano em foco.
Verificar se os números de seção do PRD estão corretos após geração.

**Test Spec (§8):** Preenchido automaticamente por `/bks-sdd --feature-tests`.
Não preencher manualmente — a skill cria o arquivo e atualiza o status nesta seção.

---

## Nome do arquivo

Formato: `FEAT-[nome-kebab-case].md`

Exemplos corretos:
- `FEAT-validação-autorização-transação.md`
- `FEAT-registro-atomico-debito-credito.md`
- `FEAT-consulta-saldo-em-tempo-real.md`

Exemplos incorretos:
- `FEAT-F1.md` (não usar só o ID)
- `FEAT-ValidacaoAutorização.md` (não usar camelCase)
- `feat-validação.md` (FEAT deve ser maiúsculo)

---

## Relação com outros artefatos

```
PLAN-[nome].md (Fase 4)
    ↓ §3 Features Previstas, linha F[N] → ID e nome desta feature

FEAT-[nome].md (Fase 5) ← este documento
    ↓ §2 Critérios de Aceite  → alimenta cenários principais do TEST-[nome].md
    ↓ §3 Comportamentos de Borda → alimenta edge cases do TEST-[nome].md
    ↓ §5 Contratos de Dados (Transaction Map) → alimenta §4 Contratos do TEST-[nome].md
    ↓ §8 Test Spec            → referência TEST-[nome].md (gerado pela Fase 6)

TEST-[nome].md (Fase 6)
    ↓ aprovação → desbloqueia --feature-task

TASK-[id]-[descrição].md (Fase 5, gerada após TEST aprovado)
    ↑ 