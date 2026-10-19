# Task Spec Structure — BKS-SDD Reference

Este documento define o template canônico do `TASK-[id]-[descrição].md` gerado pela Fase 5
da skill BKS-SDD. Cada task é a unidade atômica de execução — o que um agente de
implementação executa de forma independente, sem precisar ler o projeto inteiro.

---

## Template

```markdown
# Task — TASK-[id]: [Descrição Curta]

**Feature:** F[N] — [nome da feature]
**Test Spec:** `spec/tests/TEST-[nome].md`
**Projeto:** project-[nome]
**Dependências:** TASK-[ids anteriores] | nenhuma
**Status:** Pendente | Em execução | Concluída | Bloqueada

---

## Contexto

[Mínimo necessário para o agente executar sem ler o projeto inteiro.
2–5 frases. Responde: o que existe hoje, o que precisa mudar e por quê.
Não repetir o PRD nem a feature spec inteira — só o que é relevante para esta task.]

## Instrução

[Uma instrução clara e atômica. Começa com verbo no imperativo.
Exemplo: "Criar endpoint POST /transactions que valida saldo disponível na wallet de
origem, registra a transação com status 'pendente' e publica evento no tópico 'tx.created'."]

## Arquivos a criar ou modificar

- `[caminho/arquivo]` — [o que fazer neste arquivo]
- `[caminho/arquivo]` — [o que fazer neste arquivo]

## Critério de aceite

[Um único critério binário e verificável. Se isso for verdadeiro, a task está concluída.
Começa com verbo no infinitivo. Exemplo: "Retornar HTTP 201 com o ID da transação criada
quando o payload for válido e o saldo for suficiente."]

## Definição de pronto

- [ ] Código criado/modificado conforme instrução
- [ ] Critério de aceite verificado (manualmente ou por teste)
- [ ] Cenários do `TEST-[nome].md` correspondente passando
- [ ] Sem regressões nos testes existentes
- [ ] Task marcada como Concluída neste arquivo
```

---

## Orientações campo a campo

**ID (TASK-[id]):** Sequencial dentro do projeto, com zero-padding de 3 dígitos: TASK-001,
TASK-002, ... TASK-099. Nunca renumerar — se uma task for cancelada, o ID fica vago.
A numeração é global por projeto, não por feature. Assim TASK-007 pode pertencer a F2
enquanto TASK-008 pertence a F1.

**Dependências:** Listar os IDs das tasks que devem estar `Concluída` antes desta começar.
Se não há dependência, escrever "nenhuma" — não deixar em branco.

**Status:** O ciclo de vida correto é:
```
Pendente → Em execução → Concluída
                ↓
            Bloqueada (se dependência não resolvida ou impedimento externo)
```

**Contexto (§1):** Esta seção é o "feed forward" da task — ela garante que o agente
executor não precise de contexto adicional. Regra de ouro: se um desenvolvedor novo
pudesse ler só esta seção e a Instrução e entender o que fazer, está bom.
Não copiar e colar a descrição da feature — sintetizar apenas o que é relevante para
esta task específica.

**Instrução (§2):** Uma instrução, um verbo, uma ação. Regras:
- Começa com verbo no imperativo: "Criar", "Modificar", "Adicionar", "Remover", "Refatorar"
- Descreve O QUE fazer, não COMO fazer (o agente decide o como)
- É atômica: se precisar de dois verbos independentes, são duas tasks
- Não usa linguagem ambígua: "melhorar", "ajustar", "refatorar se necessário" são proibidos

**Arquivos a criar ou modificar (§3):** Lista os caminhos relativos à raiz do projeto.
Se não for possível determinar os arquivos com certeza, escrever:
`- [a determinar pelo agente com base na arquitetura existente]`

**Critério de aceite (§4):** É o sensor da task — a condição verificável que fecha o loop.
Diferença do critério de aceite da feature: a feature tem vários critérios coletivos;
a task tem exatamente um critério individual. Se a task não tem como verificar seu próprio
critério, está mal definida.

**Test Spec:** Campo obrigatório a partir da Fase 6. Referencia o `TEST-[nome].md` que define
os cenários que esta task deve fazer passar. O nome do arquivo TEST corresponde ao nome do
FEAT de origem — ex: task gerada de `FEAT-validação-autorização-transação.md` referência
`spec/tests/TEST-validação-autorização-transação.md`.

**Definição de pronto (§5):** Checklist padrão — não alterar. O agente marca cada item
conforme conclui. O item "Cenários do TEST-[nome].md passando" é o gatilho TDD: a task
só pode ser marcada Concluída quando os cenários definidos antes da implementação estiverem
verificados.

---

## Nome do arquivo

Formato: `TASK-[id]-[descrição-kebab-case].md`

- ID com zero-padding de 3 dígitos: `001`, `002`, ..., `099`
- Descrição: máximo 5 palavras em kebab-case, suficiente para identificar sem abrir o arquivo

Exemplos corretos:
- `TASK-001-validar-campos-payload.md`
- `TASK-002-verificar-saldo-wallet-origem.md`
- `TASK-003-registrar-tentativa-audit-log.md`
- `TASK-012-criar-endpoint-post-transactions.md`

Exemplos incorretos:
- `TASK-1-validar.md` (ID sem zero-padding)
- `task-001-validar-campos.md` (TASK deve ser maiúsculo)
- `TASK-001.md` (sem descrição)
- `TASK-001-validar-todos-os-campos-obrigatorios-do-payload-de-entrada.md` (descrição longa demais)

---

## Granularidade correta de uma task

Uma task está **grande demais** se:
- Leva mais de uma sessão de agente para completar
- Tem mais de um critério de aceite natural
- Modifica mais de 3 arquivos não relacionados
- A instrução precisa de dois verbos independentes ("criar X e integrar com Y")

Uma task está **vaga demais** se:
- Não tem critério de aceite verificável ("melhorar a performance")
- A instrução não começa com verbo concreto
- O contexto não permite que o agente entenda o que existe hoje

**Regra prática:** Uma task bem definida deve poder ser completada por um agente em
uma única sessão focada, sem precisar pedir esclarecimentos.

---

## Relação com outros artefatos

```
FEAT-[nome].md (Fase 5)
    ↓ §5 Tasks              → define quais TASKs existem e suas dependências
    ↓ §2 Critérios de Aceite → cada critério da feature vira critério de uma ou mais TASKs
    ↓ §4 Restrições Técnicas → herdadas pelo contexto de cada TASK

TEST-[nome].md (Fase 6)
    ↓ §2 Cenários Principais → referenciados no campo "Test Spec:" desta task
    ↓ §3 Edge Cases          → cobertos pelos testes implementados nas tasks

TASK-[id]-[descrição].md (Fase 5, gerada após TEST aprovado) ← este documento
    ↑ referência a feature pelo campo "Feature: F[N]"
    ↑ referência o test spec pelo campo "Test Spec:"
    → spec/output/ ← resultado da 