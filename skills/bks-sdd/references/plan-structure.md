# Plan Structure — BKS-SDD Reference

Este documento define a estrutura canônica do `PLAN-[nome].md` gerado pela Fase 4 da skill BKS-SDD.
O plano é derivado do PRD do projeto e orienta a geração de specs de features na Fase 5.

---

## Template

```markdown
# Plano Macro — [Nome do Projeto]

**Status:** Draft | Review | Aprovado
**Versão:** 0.1
**Projeto:** project-[nome]
**PRD de referência:** PRD-[nome].md v[X]
**Criado:** [YYYY-MM-DD]
**Atualizado:** [YYYY-MM-DD]

---

## 1. Visão Geral do Plano

[2–3 frases resumindo a abordagem de execução: o que será construído, em que ordem e por quê.
Não repetir o PRD — este parágrafo deve responder "como vamos executar", não "o que vamos fazer".]

## 2. Fases de Execução

[Para cada fase do §9 do PRD, criar uma subseção:]

### Fase 1 — [Nome da Fase]

**Objetivo:** [O que esta fase entrega, em uma frase]
**Entregável:** [Artefato concreto e verificável ao final desta fase]
**Dependências:** [Fases anteriores ou projetos externos necessários. "Nenhuma" se for a primeira.]
**Critérios de aceite:** [Retirados do §10 do PRD, aplicáveis a esta fase]
**Risco principal:** [O maior risco técnico ou de negócio desta fase]
**Features desta fase:** [Lista de IDs do §3 deste plano que pertencem a esta fase]

### Fase 2 — [Nome da Fase]

[repetir estrutura acima]

## 3. Features Previstas

Lista completa das features que serão especificadas na Fase 5.
Cada feature corresponde a uma unidade funcional coerente do projeto.
O ID da feature (F1, F2, ...) é usado como referência nas fases de execução e nas specs.

| # | Feature | Fase de Execução | Prioridade | Observação |
|---|---------|-----------------|------------|------------|
| F1 | [nome descritivo] | Fase 1 | P0 | [contexto se necessário] |
| F2 | [nome descritivo] | Fase 1 | P0 | |
| F3 | [nome descritivo] | Fase 2 | P1 | |

**Legenda de prioridade:**
- P0: Essencial — bloqueia entrega se ausente
- P1: Importante — deve estar na versão inicial mas tem alternativa
- P2: Desejável — pode ser diferido sem impacto crítico

## 4. Dependências Externas

Integrações, serviços externos, decisões de terceiros ou outros projetos do workspace
que este projeto precisa para avançar. Especificar em qual fase de execução cada dependência
é necessária.

| Dependência | Tipo | Necessária na Fase | Responsável / Forma de resolver |
|-------------|------|-------------------|---------------------------------|
| [ex: API de pagamento] | Serviço externo | Fase 2 | [equipe / decisão pendente] |

Se não houver dependências externas: *"Nenhuma dependência externa identificada."*

## 5. Assunções

O que está sendo assumido como verdadeiro para que este plano seja válido.
Cada assunção deve ter uma forma concreta de ser validada antes ou durante a execução.

| Assunção | Como validar | Impacto se errada | Fase afetada |
|----------|--------------|-------------------|--------------|
| [ex: A API X suporta webhook] | Testar na Fase 1 | Alto — muda arquitetura de eventos | Fase 2+ |

## 6. Questões em Aberto

Questões do PRD (§12) ainda não resolvidas que impactam o planejamento.
Este é o mesmo mecanismo do §12 do PRD, mas em nível de plano.
Remover itens conforme forem resolvidos. Plano pronto para execução quando esta seção estiver vazia.

- [ ] [questão herdada do PRD ou nova, identificada durante o planejamento]

## 7. Fontes

- `PRD-[nome].md`: base principal do plano
- `workspace-[nome]/research/PRD.md`: contexto macro do workspace *(se consultado)*
- [outros arquivos ou referências usadas no planejamento]
```

---

## Orientações campo a campo

**Visão Geral (§1):** Uma frase deve responder "que abordagem vamos usar" (ex: "começamos pela
autenticação para desbloquear todas as demais features") e outra deve responder "por que está
ordem" (ex: "as features de P0 são interdependentes, então a Fase 1 as agrupa para evitar
retrabalho"). Evite repetir o Problem Statement do PRD.

**Fases de Execução (§2):** Cada fase deve ser verticalmente fatiada — um slice funcional
de ponta a ponta, não "backend da Fase 1, frontend da Fase 2". Isso alinha com o princípio
SDD de incrementos verificáveis. O critério: se a Fase N falhar, a Fase N-1 já entregou algo
utilizável.

**Features Previstas (§3):** Esta tabela é o input direto da Fase 5 (Feature Specs). Nomeie
as features de forma descritiva para o usuário leigo, não apenas técnica. Exemplos ruins:
"módulo auth", "CRUD usuários". Exemplos bons: "Login e recuperação de senha", "Gestão de
perfil de usuário". A granularidade certa: uma feature deve caber em uma spec de 1–2 páginas.

**Assunções (§5):** Assunções não documentadas são riscos silenciosos. Se você está assumindo
que uma API existe, que um volume é baixo, ou que um usuário tem um comportamento específico,
documente aqui. A coluna "Como validar" força concretude — se não há forma de validar, a
assunção provavelmente é um risco que deveria estar em §12.

**Questões em Aberto (§6):** O plano só está pronto para execução quando §6 estiver vazio.
Se uma questão não puder ser resolvida antes de iniciar, transformá-la em uma assunção (§5)
com impacto e forma de validação explícitos.

---

## Relação com outros artefatos

```
PRD-[nome].md (Fase 3)
    ↓ §9 Delivery Plan → alimenta §2 Fases de Execução
    ↓ §5 Functional Requirements → alimenta §3 Features Previstas
    ↓ §10 Acceptance Criteria → alimenta critérios de aceite de cada fase
    ↓ §12 Open Questions → alimenta §6 Questões em Aberto

PLAN-[nome].md (Fase 4) ← este documento
    ↓ §3 Features Previstas → alimenta FEAT-[nome].md (Fase 5)
    ↓ §2 Critérios de aceite por fase → alimenta validações das specs
```

## SDD level targeting

- **Spec-first:** Preencher §1–§3. O plano orienta a execução e pode ser simplificado após.
- **Spec-anchored:** Preencher todas as seções. Manter o plano atualizado conforme execução avança.
- **Spec-as-source:** O plano é o artefato primário — nenhuma spec de feature é criada sem
  estar listada aqui com prioridade e fase definidas.

Para a maioria dos projetos, target **spec-anchored** como padrão.
