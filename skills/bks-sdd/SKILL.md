---
name: bks-sdd
description: >
  BKS Spec-Driven Development workflow — starts with PRD generation and grows to cover
  the full SDD cycle (PRD → project breakdown → specs → execution). Use this skill whenever
  the user wants to: generate a PRD, create a project spec, start a spec-driven workflow,
  break a product idea into phases, or structure work for AI-assisted development.
  Trigger on keywords: PRD, spec, bks-sdd, spec-driven, produto, planejamento de projeto,
  workspace spec, fases do projeto, levantamento de requisitos.
---

# BKS-SDD — Skill de Spec-Driven Development

**Idioma:** Todo output desta skill — perguntas, respostas, documentos gerados — deve estar em **Português do Brasil (PT-BR)**, independente do idioma em que o usuário escrever o comando.

## 🔴 Conduta — vale em todas as fases

**Entregue o que foi pedido, nada além.** O escopo da resposta é o escopo do pedido. Um pedido de
correção pontual não vira reescrita de seção; um comando pedido não vira guia com variantes e
diagnóstico preventivo.

> **Não confundir com os artefatos.** PRD, FEAT, TEST e TASK têm o conteúdo que a estrutura exige —
> a regra é contra **inflar além do pedido**, não contra preencher a peça.

Sinais de inflação: variante que ninguém pediu · diagnóstico de erro que não aconteceu · repetir o
que já está em outro documento · recapitular o que já é visível. Achado relevante fora do escopo
entra como **uma linha**, não como implementação.

**Em dúvida de contexto, pergunte antes de responder** — escopo, destino do artefato, ou
alternativas mutuamente exclusivas. 🔴 **Pergunta *ou/ou* respondida com "sim" não decidiu nada:**
pergunte de novo nomeando as opções, em vez de escolher por suposição. Não pergunte o que dá para
verificar lendo o repositório ou executando.

Esta skill orquestra o fluxo BKS de Spec-Driven Development. Foi projetada para crescer incrementalmente: cada fase é adicionada ao longo do tempo. As fases atualmente ativas estão marcadas com ✅.

## Mapa de Fases

| Fase | Descrição | Comandos | Status |
|------|-----------|----------|--------|
| 0 | Workspace Bootstrap — cria estrutura, `.states`, `.logs` | `/bks-sdd` | ✅ Ativa |
| 1 | PRD de Workspace — gera `PRD.md` a partir do `\research` | `/bks-sdd --prd` | ✅ Ativa |
| 1.5 | Session Management — snapshots de estado, continuidade, limpeza | `--continue`, `--tan`, `--clear` | ✅ Ativa |
| 2 | Projetos Internos — cria `\project-[nome]` com estrutura RPI | `/bks-sdd --project` | ✅ Ativa |
| 3 | PRD de Projeto — gera `PRD-[nome].md` por projeto | `/bks-sdd --project-prd` | ✅ Ativa |
| 4 | Plano Macro — gera `PLAN-[nome].md` orientando specs | `/bks-sdd --project-plan` | ✅ Ativa |
| **5** | **Feature Specs — ciclo completo de especificação por feature** | `--feature-list` | ✅ Ativa |
| 5.1 | Spec — gera `FEAT-[nome].md` a partir do plano | `--feature` | ✅ Ativa |
| 5.2 | Test Scenarios — gera `TEST-[nome].md` após FEAT aprovado | `--feature-tests`, `--feature-tests-list` | ✅ Ativa |
| 5.3 | Tasks — gera `TASK-[id].md` após TEST aprovado | `--feature-task` | ✅ Ativa |
| **6** | **Implementação** — execução das tasks; orquestração, verificação e progresso | `--impl-init`, `--task-run`, `--task-done`, `--task-list`, `--status` | ✅ Ativa |
| **7** | **Custo & Telemetria** — consumo de tokens e custo por sessão e do processo inteiro | `--cost`, `--cost-report` | ✅ Ativa |

---

## Fase 0 — Workspace Bootstrap

### Quando invocar esta fase

O usuário digita `/bks-sdd` sem outros argumentos, ou declara que quer iniciar um novo
workspace/projeto/ambiente de trabalho BKS. Esta fase cria toda a estrutura necessária para
as fases seguintes.

### Passo 0.1 — Verificar se já existe um workspace ativo

Antes de qualquer ação, verificar se existe um folder `workspace-*` no diretório de trabalho
atual (diretório montado do usuário).

**Se já existir um workspace:**
- Informar ao usuário: *"Encontrei um workspace existente: `workspace-[nome]`. Não criarei um novo. Recuperando a sessão mais recente..."*
- Executar o fluxo de `--continue` (Fase 1.5) para carregar o último estado salvo.
- Não prosseguir com a criação.

**Se não existir nenhum workspace:**
- Prosseguir para o Passo 0.2.

### Passo 0.2 — Pedir o nome do workspace

Perguntar ao usuário:

> **Qual o nome do seu workspace?**
>
> *O workspace é o ambiente raiz do seu projeto macro. Na raiz da sua pasta será criado um folder `workspace-[nome]` contendo toda a estrutura necessária para aplicar Spec-Driven Development com Harness Engineering. Ele organizará sua pesquisa, projetos internos, planos e specs. Por favor, não apague nenhum folder interno — cada um tem um papel específico. Você pode consultar `/help-workspace` a qualquer momento para entender o papel de cada pasta.*

Aguardar a resposta do usuário com o nome desejado. Não prosseguir sem o nome.

### Passo 0.3 — Confirmar antes de criar

Apresentar ao usuário o resumo do que será criado e pedir confirmação:

> *Vou criar a estrutura abaixo. Confirma?*
>
> ```
> workspace-[nome]/
> ├── .logs/
> ├── .states/
> ├── research/
> │   └── links.md
> ├── plan/
> └── projects/
> ```

Aguardar confirmação explícita ("sim", "pode criar", "ok", "confirmo", ou equivalente).
**Não criar nada sem confirmação.**

### Passo 0.4 — Criar a estrutura de folders

Após confirmação, criar a seguinte estrutura no diretório de trabalho do usuário:

```
workspace-[nome]/
├── .logs/
│   └── session-[YYYY-MM-DD].md
├── .states/
│   └── state-initial-[YYYY-MM-DDTHH-MM].md
├── research/
│   └── links.md
├── plan/
└── projects/
```

**Detalhes de cada folder** estão em `references/workspace-structure.md`.

**Arquivo `.logs/session-[YYYY-MM-DD].md`** — criar com:
```markdown
# Log de Sessão — [YYYY-MM-DD]

## Sessão iniciada: [YYYY-MM-DDTHH:MM]
- Comando: /bks-sdd
- Ação: Criação do workspace `workspace-[nome]`
- Resultado: Estrutura criada com sucesso
```

**Arquivo `.states/state-initial-[YYYY-MM-DDTHH-MM].md`** — criar com:
```markdown
# Estado Inicial — [YYYY-MM-DDTHH:MM]

**Workspace:** workspace-[nome]
**Fase ativa:** 0 — Bootstrap concluído
**Próximo passo sugerido:** Adicionar arquivos de pesquisa em `research/` e executar `/bks-sdd --prd`

## Contexto da sessão
[Resumo do que foi declarado pelo usuário nesta sessão — objetivos, restrições, produto em mente]

## Estrutura criada
- `.logs/` — logs de sessão por data
- `.states/` — snapshots de estado para continuidade entre sessões
- `research/` — pesquisa e inputs primários para gerar o PRD
- `plan/` — plano macro do workspace (gerado futuramente)
- `projects/` — projetos internos com ciclos RPI próprios

## Questões em aberto
[Qualquer dúvida ou gap não resolvido na conversa até aqui]
```

**Arquivo `research/links.md`** — criar com:
```markdown
# Links de Referência

> Adicione aqui URLs que deseja usar como referência para gerar o PRD.
> Um link por linha. Exemplo:
> - https://exemplo.com/artigo

```

### Passo 0.5 — Comunicar o resultado

Após criar a estrutura, informar ao usuário:

> ✅ **Workspace `workspace-[nome]` criado com sucesso!**
>
> **Próximos passos:**
> 1. Coloque seus arquivos de pesquisa (`.pdf`, `.md`, `.txt`) em `research/`
> 2. Adicione links de referência em `research/links.md`
> 3. Execute `/bks-sdd --prd` para gerar o PRD do workspace
>
> **Comandos disponíveis:**
> - `/bks-sdd --prd` — gera o PRD a partir do que está em `research/`
> - `/bks-sdd --continue` — retoma a sessão mais recente
> - `/bks-sdd --tan` — salva o estado atual e encerra a sessão com segurança
> - `/bks-sdd --clear` — limpa o contexto e salva estado final
> - `/help-workspace` — explica o papel de cada folder

---

## Fase 1 — PRD de Workspace

### Quando invocar esta fase

O usuário digita `/bks-sdd --prd` ou solicita a geração do PRD em qualquer forma:
- *"gera o PRD"*
- *"bks-sdd, quero gerar o PRD para um app de gestão de tarefas"*
- *"gera o PRD usando os arquivos que coloquei na pasta"*
- *"gera o PRD, tem um links.md com referências"*
- *"bks-sdd PRD — tenho PDFs de pesquisa, notas em .md e um links.md"*

### Pré-requisito

Verificar se existe um workspace ativo (`workspace-*/`). Se não existir, informar:
> *"Não encontrei um workspace ativo. Execute `/bks-sdd` para criar um antes de gerar o PRD."*

Se existir, trabalhar dentro de `workspace-[nome]/research/`.

### Passo 1.1 — Coletar inputs

Varrer `workspace-[nome]/research/` em busca de arquivos `.pdf`, `.md`, `.txt`.
Ler cada um. São inputs primários: requisitos, notas de pesquisa, análise competitiva, ideias brutas.
Não pular nenhum arquivo.

Se existir `research/links.md`, lê-lo. Para cada URL encontrada:
1. Se URL contém `youtube.com` ou `youtu.be`: usar `TranscriptAPI.get_youtube_transcript` para extrair a transcrição e incorporar como contexto
2. Para as demais URLs: buscar com `WebFetch` e extrair conteúdo relevante
3. URLs inatingíveis ou com falha de WebFetch: registrar erro no log da sessão e prosseguir — não bloquear geração

Usar também qualquer contexto declarado pelo usuário na sessão atual (objetivos, restrições, público-alvo, tom).

Se nenhum arquivo e nenhum link forem encontrados:
> *"Não encontrei arquivos ou links.md em `research/`. Pode descrever o produto/projeto aqui diretamente?"*

### Passo 1.2 — Esclarecer antes de escrever (se necessário)

Se informações críticas estiverem faltando, usar `AskUserQuestion` para conduzir a entrevista em rodadas de no máximo **3 perguntas por rodada**:
- Qual problema isso resolve? Para quem?
- Qual é a métrica primária de sucesso?
- Existem restrições técnicas ou de negócio conhecidas?

Nunca mais de 3 perguntas por chamada de `AskUserQuestion`.
Não fazer perguntas já respondidas pelos arquivos de input.

### Passo 1.3 — Gerar o PRD

Ler `references/prd-structure.md` para o template completo e instruções campo a campo.

Escrever o PRD seguindo exatamente aquela estrutura. Salvar como `workspace-[nome]/research/PRD.md`.
Tom: claro, preciso, sem enchimento — cada frase deve carregar informação.

Após salvar, verificar `references/input-sources.md` para orientações sobre documentação de fontes (§13 do PRD).

### Passo 1.4 — Checkpoint de revisão

Executar mentalmente o Spec Review Checklist (não imprimir o checklist — apenas sinalizar gaps):

1. Escopo e intenção — o problema está delimitado?
2. Comportamento funcional — os critérios de aceite são testáveis?
3. Arquitetura e restrições — os limites estão explícitos?
4. Plano de entrega — o trabalho está dividido em fases?
5. Rastreabilidade — as fontes estão vinculadas?

Se alguma dimensão crítica não estiver resolvida, adicionar `## Questões em Aberto` no final do `PRD.md`.

### Passo 1.5 — Atualizar log e estado

Após gerar o PRD, registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --prd
  Inputs lidos: [lista de arquivos e URLs]
  Resultado: PRD.md gerado em research/
  Gaps identificados: [sim/não — quais]
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md` com o contexto atual.

Orientar o usuário:
> *"PRD.md gerado em `research/`. Revise e, quando estiver satisfeito, execute `/bks-sdd --tan` para encerrar com segurança ou `/bks-sdd --project` para criar projetos internos."*

### Output

- Arquivo: `workspace-[nome]/research/PRD.md`
- Formato: Markdown, seguindo `references/prd-structure.md`
- **Idioma: Português do Brasil (PT-BR) — obrigatório**

---

## Fase 1.5 — Session Management

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

---

## Fase 2 — Projetos Internos

### Quando invocar esta fase

O usuário digita `/bks-sdd --project` ou declara que quer criar um projeto dentro do workspace:
- *"cria um projeto"*
- *"quero iniciar um projeto chamado X"*
- *"bks-sdd, novo projeto"*

### Pré-requisito

Verificar se existe um workspace ativo (`workspace-*/`). Se não existir:
> *"Não encontrei um workspace ativo. Execute `/bks-sdd` para criar um workspace antes de adicionar projetos."*

### Passo 2.1 — Pedir o nome do projeto e stack

Perguntar ao usuário:

> **Qual o nome do projeto?**
>
> *Um projeto é um escopo delimitado dentro do seu workspace. Cada projeto tem seu próprio ciclo de Research → Plan → Implement, com pesquisa, PRD e plano macro independentes. Você pode ter quantos projetos precisar dentro do mesmo workspace.*

Aguardar o nome. Após receber o nome, perguntar os campos de stack obrigatórios para a Fase 6:

> *Para preparar este projeto para a Fase 6 (Implementação), preciso de mais algumas informações:*
>
> **Framework de desenvolvimento:**
> `1` .NET | `2` Spring (Java/Kotlin) | `3` TypeScript (Node.js) — Express · Fastify · LangGraph · Worker · Consumer | `4` Go | `5` Outro (descreva)
>
> **Banco de dados principal:**
> `1` PostgreSQL | `2` SQL Server | `3` MongoDB | `4` MySQL | `5` Redis | `6` Nenhum
>
> **Mensageria:**
> `1` Kafka | `2` RabbitMQ | `3` Google Pub/Sub | `4` Nenhuma

Aguardar as respostas. Registrar como campos `Framework`, `Database` e `Mensageria` no arquivo de projeto. Esses campos são herdados por todas as features, tasks e pelo `--impl-init` da Fase 6.

**Regra condicional — TypeScript Backend:**
Se o usuário escolher `3` TypeScript no campo Framework, fazer obrigatoriamente a seguinte pergunta adicional ANTES de avançar para o Passo 2.2:

> **Tipo de backend TypeScript:**
> `1` API REST (Express) | `2` API REST (Fastify) | `3` Agente LangGraph | `4` Worker (BullMQ/pg-boss) | `5` Consumer (RabbitMQ/Kafka)
>
> *(Esta informação é necessária para a Fase 6 acionar a skill correta de geração de código.)*

Registrar a resposta como campo `TypeScript Backend` no arquivo `research/stack.md`. Se o usuário responder "ainda não sei", registrar como `A definir`.

Se o usuário responder "ainda não sei" para algum campo, registrar como `A definir` — a informação pode ser atualizada antes do `--impl-init`.

### Passo 2.2 — Verificar se o projeto já existe

Checar se já existe `workspace-[nome]/projects/project-[nome-do-projeto]/`.

**Se já existir:**
> *"O projeto `project-[nome]` já existe. Deseja abri-lo e continuar de onde parou?"*

Se o usuário confirmar, ler o estado mais recente em `.states/` do workspace e retomar.
Se não, pedir um nome diferente.

### Passo 2.3 — Confirmar antes de criar

Apresentar a estrutura que será criada e pedir confirmação:

> *Vou criar a estrutura abaixo dentro de `workspace-[nome]/projects/`. Confirma?*
>
> ```
> project-[nome-do-projeto]/
> ├── research/
> │   └── links.md
> ├── plan/
> └── spec/
>     ├── features/
>     ├── tasks/
>     └── output/
> ```

Aguardar confirmação explícita antes de criar qualquer coisa.

### Passo 2.4 — Criar a estrutura do projeto

Após confirmação, criar dentro de `workspace-[nome]/projects/`:

```
project-[nome-do-projeto]/
├── research/
│   ├── links.md
│   └── stack.md
├── plan/
└── spec/
    ├── features/
    ├── tasks/
    └── output/
        └── results/
```

**Arquivo `research/links.md`** — criar com:
```markdown
# Links de Referência — project-[nome-do-projeto]

> Adicione aqui URLs que deseja usar como referência para gerar o PRD deste projeto.
> Um link por linha. Exemplo:
> - https://exemplo.com/artigo

```

**Arquivo `research/stack.md`** — criar com os campos de stack coletados no Passo 2.1:
```markdown
# Stack — project-[nome-do-projeto]

**Framework:** [valor declarado]
**TypeScript Backend:** [valor declarado — apenas se Framework = TypeScript; omitir caso contrário]
**Database:** [valor declarado]
**Mensageria:** [valor declarado]

> Este arquivo é a fonte de verdade da stack tecnológica do projeto.
> Os campos aqui são herdados pela Fase 6 (--impl-init) para gerar o contrato de implementação.
> Atualize antes de executar --impl-init se algum campo mudar.
```

**Detalhes de cada folder** do projeto estão em `references/project-structure.md`.

### Passo 2.5 — Registrar no log e salvar estado

Adicionar entrada no `.logs/session-[data].md` do workspace:
```
- [HH:MM] Comando: /bks-sdd --project
  Projeto criado: project-[nome-do-projeto]
  Stack: Framework=[...] / Database=[...] / Mensageria=[...]
  Resultado: Estrutura RPI criada em projects/project-[nome-do-projeto]/
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md` com o contexto atualizado.

### Passo 2.6 — Comunicar o resultado

> ✅ **Projeto `project-[nome-do-projeto]` criado em `projects/`!**
>
> **Próximos passos:**
> 1. Coloque arquivos de pesquisa (`.pdf`, `.md`, `.txt`) em `project-[nome]/research/`
> 2. Adicione links em `project-[nome]/research/links.md`
> 3. Execute `/bks-sdd --project-prd` para gerar o PRD do projeto
>
> **Comandos do projeto:**
> - `/bks-sdd --project-prd` — gera o PRD deste projeto
> - `/bks-sdd --project-plan` — gera o plano macro *(requer PRD aprovado)*

### Output

- Estrutura de folders criada em: `workspace-[nome]/projects/project-[nome-do-projeto]/`
- Formato: conforme `references/project-structure.md`
- **Idioma: PT-BR — obrigatório**

---

## Fase 3 — PRD de Projeto

### Quando invocar esta fase

O usuário digita `/bks-sdd --project-prd` ou solicita o PRD de um projeto específico:
- *"gera o PRD do projeto X"*
- *"bks-sdd, PRD do projeto"*
- *"quero o PRD para o project-[nome]"*

### Pré-requisito

1. Verificar se existe um workspace ativo. Se não: sugerir `/bks-sdd`.
2. Identificar qual projeto está em foco. Se houver apenas um projeto em `projects/`, usá-lo automaticamente. Se houver mais de um, perguntar:
   > *"Encontrei os seguintes projetos: [lista]. Para qual devo gerar o PRD?"*

### Passo 3.1 — Coletar inputs do projeto

Varrer `workspace-[nome]/projects/project-[nome-do-projeto]/research/` em busca de arquivos `.pdf`, `.md`, `.txt`.
Ler cada um. São inputs primários: requisitos, notas, análise competitiva, ideias brutas. Não pular nenhum.

Se existir `research/links.md` do projeto, lê-lo. Para cada URL:
1. Se URL contém `youtube.com` ou `youtu.be`: usar `TranscriptAPI.get_youtube_transcript` para extrair a transcrição e incorporar como contexto
2. Para as demais URLs: buscar com `WebFetch` e extrair conteúdo relevante
3. URLs inatingíveis ou com falha de WebFetch: registrar erro no log da sessão e prosseguir — não bloquear geração

Usar também qualquer contexto declarado pelo usuário na sessão atual.

**Contexto adicional:** Se existir `workspace-[nome]/research/PRD.md` (PRD do workspace), lê-lo
também como contexto macro. O PRD do projeto deve ser coerente com a visão do workspace.

Se nenhum arquivo for encontrado no projeto:
> *"Não encontrei arquivos em `research/` do projeto. Pode descrever o escopo do projeto aqui diretamente?"*

### Passo 3.2 — Esclarecer antes de escrever (se necessário)

Se informações críticas estiverem faltando, usar `AskUserQuestion` para conduzir a entrevista em rodadas de no máximo **3 perguntas por rodada**:
- Qual o escopo deste projeto dentro do workspace?
- Quais são os critérios de sucesso específicos deste projeto?
- Existem dependências com outros projetos do workspace?

Nunca mais de 3 perguntas por chamada de `AskUserQuestion`.
Não repetir perguntas já respondidas pelo PRD do workspace ou pelos arquivos do projeto.

### Passo 3.3 — Gerar o PRD do projeto

Ler `references/prd-structure.md` para o template completo.

Escrever o PRD seguindo aquela estrutura com adaptações para contexto de projeto:
- §1 (Problem Statement): escopo dentro do workspace, não o problema macro
- §4 (Scope): delimitar claramente o que é deste projeto vs. outros projetos do workspace
- §8 (Architecture): mencionar integrações com outros projetos se existirem
- §9 (Delivery Plan): as fases do projeto devem mapear diretamente para as features/specs da Fase 5

**Se o projeto adotar DDD ou Arquitetura Hexagonal:**
Antes de escrever o §8 (Architecture), ler as guidelines arquiteturais disponíveis em `references/`:
- `references/ddd-bounded-contexts-guidelines.md` — para identificar Bounded Contexts, mapear o domínio estratégico, classificar subdomínios (Core/Supporting/Generic) e criar o Context Map
- `references/ddd-tactic-guidelines.md` — para modelar Entidades, Value Objects, Aggregates, Domain Events e Repositories dentro de cada contexto
- `references/hexagonal-arch-guidelines.md` — para estruturar Ports & Adapters, separar domínio de infraestrutura e definir adaptadores primários/secundários
- `references/txc-guidelines.md` — **OBRIGATÓRIO se o projeto for .NET ou TypeScript**; usar para preencher §8 com o template TXC-aware (§8a–§8d) em vez do template genérico; Primary Ports agrupadas por BoundedContext (não por operação CRUD — nunca `ICreateXxxUseCase` por operação); Secondary Ports por aggregate (não `IDBRepositoryPort` genérico); Transaction Map na tabela §8b

Usar essas guidelines para preencher o §8 com: identificação dos Bounded Contexts, decisões de build vs. buy por subdomínio, estrutura de portas e adaptadores, e regras de comunicação entre contextos. Registrar as decisões como assunções explícitas se ainda não estiverem validadas.

Para projetos .NET ou TypeScript: preencher §8 usando o template TXC-aware (§8a Internal Architecture, §8b Bounded Contexts e Aggregates, §8c Secondary Ports, §8d External Integrations e ACL) conforme definido em `references/prd-structure.md` e detalhado em `references/txc-guidelines.md`.

Salvar como `workspace-[nome]/projects/project-[nome-do-projeto]/research/PRD-[nome-do-projeto].md`.

Verificar `references/input-sources.md` para documentação de fontes no §13.

### Passo 3.4 — Checkpoint de revisão

Executar mentalmente o Spec Review Checklist (sinalizar apenas os gaps):

1. Escopo e intenção — o problema do projeto está delimitado dentro do workspace?
2. Comportamento funcional — os critérios de aceite são testáveis?
3. Arquitetura e restrições — as dependências com outros projetos estão explícitas?
4. Plano de entrega — o trabalho está dividido em fases executáveis?
5. Rastreabilidade — as fontes e o PRD do workspace estão vinculados?

Adicionar `## Questões em Aberto` se houver gaps críticos não resolvidos.

### Passo 3.5 — Registrar no log e salvar estado

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --project-prd
  Projeto: project-[nome-do-projeto]
  Inputs lidos: [lista de arquivos e URLs]
  Resultado: PRD-[nome-do-projeto].md gerado em projects/project-[nome]/research/
  Gaps identificados: [sim/não — quais]
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

Orientar o usuário:
> *"PRD-[nome-do-projeto].md gerado. Revise o documento e, quando aprovado, execute `/bks-sdd --project-plan` para gerar o plano macro de execução."*

### Output

- Arquivo: `workspace-[nome]/projects/project-[nome-do-projeto]/research/PRD-[nome-do-projeto].md`
- Formato: Markdown, seguindo `references/prd-structure.md`
- **Idioma: PT-BR — obrigatório**

---

## Fase 4 — Plano Macro do Projeto

### Quando invocar esta fase

O usuário digita `/bks-sdd --project-plan` ou solicita o plano do projeto:
- *"gera o plano do projeto X"*
- *"bks-sdd, quero o plano de execução"*
- *"project-plan para o [nome]"*

### Pré-requisito

1. Verificar se existe um workspace ativo. Se não: sugerir `/bks-sdd`.
2. Identificar o projeto em foco (mesma lógica da Fase 3 — um projeto: usa automaticamente; vários: pergunta).
3. Verificar se existe o `PRD-[nome-do-projeto].md` em `research/` do projeto.
   - Se não existir: *"Não encontrei o PRD do projeto `project-[nome]`. Execute `/bks-sdd --project-prd` antes de gerar o plano."*

### Passo 4.1 — Ler o PRD do projeto

Ler `workspace-[nome]/projects/project-[nome-do-projeto]/research/PRD-[nome-do-projeto].md` integralmente.

Extrair especificamente:
- §9 (Delivery Plan) — as fases propostas no PRD
- §5 (Functional Requirements) — os requisitos que precisam ser cobertos
- §10 (Acceptance Criteria) — os critérios que validam cada entrega
- §12 (Open Questions) — questões em aberto que afetam o planejamento

Se houver PRD do workspace (`workspace-[nome]/research/PRD.md`), lê-lo também para verificar
alinhamento estratégico.

### Passo 4.2 — Esclarecer se necessário

Se o PRD tiver questões em aberto (§12 não vazio) que impactam diretamente o planejamento,
apresentar ao usuário as mais críticas e perguntar como quer proceder:

> *"O PRD tem [N] questões em aberto que impactam o planejamento. Deseja resolvê-las agora ou gerar o plano com as assunções documentadas?"*

Aguardar resposta antes de prosseguir.

### Passo 4.3 — Gerar o Plano Macro

Ler `references/plan-structure.md` para o template completo do plano.

**Se o PRD do projeto (§8 Architecture) mencionar DDD ou Arquitetura Hexagonal:**
Antes de mapear as features no §3 do plano, ler:
- `references/ddd-bounded-contexts-guidelines.md` — para garantir que cada feature está corretamente associada ao seu Bounded Context
- `references/ddd-tactic-guidelines.md` — para verificar se a decomposição de features respeita fronteiras de aggregates e não viola invariantes de domínio
- `references/hexagonal-arch-guidelines.md` — para checar se features que envolvem integrações externas têm adaptadores mapeados

O objetivo é que o plano já oriente o agente executor sobre qual contexto delimitado cada feature pertence e quais portas/adaptadores precisarão ser criados — antecipando decisões arquiteturais que, se deixadas para a Fase 5, causam retrabalho.

Escrever o plano derivado do PRD. O `PLAN-[nome-do-projeto].md` deve conter:

```markdown
# Plano Macro — [Nome do Projeto]

**Status:** Draft | Review | Aprovado
**Versão:** 0.1
**Projeto:** project-[nome-do-projeto]
**PRD de referência:** PRD-[nome-do-projeto].md v[X]
**Criado:** [data]
**Atualizado:** [data]

---

## 1. Visão Geral do Plano

[2-3 frases resumindo a abordagem de execução — o que será construído, em que ordem e por quê]

## 2. Fases de Execução

Para cada fase do §9 do PRD, detalhar:

### Fase [N] — [Nome]

**Objetivo:** [o que esta fase entrega]
**Entregável:** [artefato concreto ao final]
**Dependências:** [fases anteriores ou projetos externos]
**Critérios de aceite:** [retirados do §10 do PRD aplicáveis a esta fase]
**Risco principal:** [o que pode dar errado]

## 3. Features Previstas

Lista das features que serão especificadas na Fase 5 (Feature Specs).
Para cada feature, indicar em qual fase de execução ela se encaixa.

| # | Feature | Fase | Prioridade (P0/P1/P2) | Observação |
|---|---------|------|-----------------------|------------|
| F1 | ... | Fase 1 | P0 | |
| F2 | ... | Fase 2 | P1 | |

## 4. Dependências Externas

Integrações, serviços, decisões de terceiros ou outros projetos do workspace
que este projeto precisa para avançar.

## 5. Assunções

O que estamos assumindo como verdadeiro para este plano ser válido.
Cada assunção deve ter uma forma de ser validada.

| Assunção | Como validar | Impacto se errada |
|----------|--------------|-------------------|
| ... | ... | Alto/Médio/Baixo |

## 6. Questões em Aberto

Questões do PRD (§12) ainda não resolvidas que impactam o plano.
Remover quando resolvidas.

- [ ] [questão]

## 7. Fontes

- PRD-[nome-do-projeto].md: base principal do plano
- [outros arquivos ou PRD do workspace consultados]
```

Salvar como `workspace-[nome]/projects/project-[nome-do-projeto]/plan/PLAN-[nome-do-projeto].md`.

### Passo 4.4 — Checkpoint de coerência

Verificar mentalmente:
1. Todas as fases do §9 do PRD estão cobertas no plano?
2. Todos os requisitos P0 do §5 têm uma feature associada?
3. As dependências do §8 estão refletidas nas dependências externas do plano?
4. As questões em aberto do §12 estão documentadas?

Se houver lacunas, adicioná-las à seção §6 do plano.

### Passo 4.5 — Registrar no log e salvar estado

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --project-plan
  Projeto: project-[nome-do-projeto]
  PRD lido: PRD-[nome-do-projeto].md
  Resultado: PLAN-[nome-do-projeto].md gerado em projects/project-[nome]/plan/
  Features previstas: [N] features listadas
  Questões em aberto: [N]
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

Orientar o usuário:
> *"PLAN-[nome-do-projeto].md gerado em `plan/`. O plano lista [N] features previstas. Revise, ajuste prioridades e questões em aberto. Quando aprovado, as features estão prontas para entrar na Fase 5 (Feature Specs)."*

### Output

- Arquivo: `workspace-[nome]/projects/project-[nome-do-projeto]/plan/PLAN-[nome-do-projeto].md`
- Formato: Markdown conforme template acima
- **Idioma: PT-BR — obrigatório**

---

---

## Fase 5 — Feature Specs

A Fase 5 é o ciclo completo de especificação de uma feature. Cada feature passa obrigatoriamente
por três sub-fases em sequência: **5.1 Spec → 5.2 Test Scenarios → 5.3 Tasks**.
Nenhuma sub-fase pode ser pulada — cada artefato desbloqueia a próxima.

### Quando invocar esta fase

O usuário executa qualquer comando `--feature*` ou `--feature-task`.
Pré-requisito: o projeto deve ter um `PLAN-[nome].md` aprovado em `plan/`.

**Templates canônicos:** ler `references/feature-spec-structure.md`, `references/test-spec-structure.md`
e `references/task-spec-structure.md` antes de gerar qualquer artefato.

---

### Comando `--feature-list` *(visão geral da Fase 5)*

**Objetivo:** Mostrar o estado atual de todas as features do projeto em foco — FEAT, TEST e Tasks.

**Passo 5L.1 — Identificar o projeto em foco**

Verificar se há projetos com `PLAN-[nome].md` em `plan/`.
- Se houver apenas um projeto com plano, usá-lo automaticamente.
- Se houver múltiplos, listar e perguntar ao usuário qual deseja visualizar.

**Passo 5L.2 — Construir a tabela de status**

Para cada feature listada no `PLAN-[nome].md` §3, verificar:
- Existe `spec/features/FEAT-[nome].md`? → determinar o status pelo campo `**Status:**` do arquivo
- Existe `spec/tests/TEST-[nome].md`? → determinar o status pelo campo `**Status:**` do arquivo
- Existe `spec/tasks/TASK-[id]-*.md` referenciando esta feature? → contar tasks

Apresentar a tabela:

```
Projeto: project-[nome]
Plano: PLAN-[nome].md

ID  | Feature              | Fase | Prior. | FEAT        | TEST            | Tasks
----|----------------------|------|--------|-------------|-----------------|-------
F1  | [nome]               | F1   | P0     | ✅ Aprovada | ✅ Aprovada     | 4 tasks
F2  | [nome]               | F1   | P0     | ✅ Aprovada | ⛔ Não criado   | —
F3  | [nome]               | F2   | P1     | 📝 Draft    | ⛔ Não aplicável | —
F4  | [nome]               | F2   | P2     | ⏳ Pendente | ⛔ Não aplicável | —
```

Legenda de ícones:
- ✅ Aprovada — artefato existe e aprovado pelo usuário
- 📝 Draft — artefato criado mas ainda não aprovado
- ⛔ Não criado — FEAT aprovado mas TEST ainda não foi gerado (próxima ação necessária)
- ⛔ Não aplicável — FEAT não aprovado; TEST não pode ser criado ainda
- ⏸ Em execução — pelo menos uma task com status "Em execução"
- 🏁 Concluída — todos os critérios de aceite verificados
- ⏳ Pendente — ainda sem spec

---

### Fase 5.1 — Spec (`--feature`)

**Objetivo:** Gerar a spec de uma feature a partir do plano. Uma feature por vez.

**Passo 5F.1 — Identificar o projeto em foco**

Mesmo comportamento do `--feature-list`: verificar planos existentes e perguntar se necessário.

**Passo 5F.2 — Listar features pendentes**

Verificar quais features do `PLAN-[nome].md` §3 ainda não têm `FEAT-[nome].md` correspondente
em `spec/features/`. Apresentar ao usuário:

> *"Encontrei [N] features ainda sem spec no projeto [nome]:*
> *F1 — [nome] (P0, Fase 1)*
> *F2 — [nome] (P0, Fase 1)*
> *F3 — [nome] (P1, Fase 2)*
> *Qual deseja especificar agora? (sugestão: começar pela P0 mais alta)"*

**Regra importante:** Nunca gerar todas as features de uma vez. Uma feature → revisão → próxima.

**Passo 5F.3 — Verificar dependências**

Se a feature escolhida tem dependência de outra feature ainda sem spec:
- Avisar: *"Atenção: F[N] depende de F[M] que ainda não foi especificada. Posso gerar mesmo assim em modo Draft, com a dependência registrada."*
- Aguardar confirmação do usuário antes de prosseguir.

**Passo 5F.4 — Decidir padrão de implementação (TXC vs ALT)**

> **Obrigatório para projetos .NET ou TypeScript. Execute antes de gerar o FEAT.**

Para a operação principal da feature, percorrer a árvore abaixo e declarar o padrão:

```
A feature tem regras de negócio que TRANSFORMAM ESTADO entre etapas distintas?
│
├── NÃO ──→ É leitura?
│           ├── 1 fonte simples ──→ [ALT-1] QueryHandler
│           └── 2+ fontes / filtros complexos ──→ [ALT-2] QueryComposer
│           NÃO, é batch/coleção ──→ [ALT-3] BatchProcessor
│               é técnica/utilitário ──→ [ALT-4] UtilityScript
└── SIM ──→ Estado entre 2+ etapas, cruzando Entry+Domain+Infra? ──→ ✅ TXC
            1 etapa só ──→ [ALT-1] SimpleCommandHandler
```

O campo `**Padrão de implementação:**` do FEAT será preenchido com o resultado desta decisão.
A ausência deste campo é proibida — o agente executor depende dele.

**Passo 5F.5 — Gerar o FEAT-[nome].md**

Ler:
1. `PLAN-[nome].md` — linha da feature escolhida (ID, nome, fase, prioridade, observação)
2. `research/PRD-[nome].md` — seção de requisitos funcionais correspondente
3. `references/feature-spec-structure.md` — template canônico (v2 TXC-aware)

**Se o projeto adotar DDD ou Arquitetura Hexagonal**, ler também:
4. `references/ddd-tactic-guidelines.md` — para identificar Aggregates afetados pela feature, nomear Domain Events gerados, verificar que as restrições técnicas (§4 do FEAT) proíbem lógica de negócio fora do domínio
5. `references/hexagonal-arch-guidelines.md` — para mapear quais Ports e Adapters precisam existir ou ser criados para esta feature (incluir em §4 Restrições Técnicas)
6. `references/txc-guidelines.md` — **OBRIGATÓRIO para features TXC em projetos .NET ou TypeScript**; ler antes de escrever §5 Contratos de Dados; usar Seção 2 (árvore de decisão) para confirmar o padrão e Seção 5 (Transaction Map) para preencher a tabela de fases e métodos semânticos

O resultado esperado é que a seção §4 (Restrições Técnicas) do FEAT já contenha as decisões arquiteturais relevantes — qual aggregate é a root, quais eventos são publicados, quais portas são necessárias — poupando o agente executor de ter que descobrir isso durante a implementação.

Gerar o arquivo `spec/features/FEAT-[nome-kebab-case].md` com status `Draft` seguindo o
template canônico (v2). Preencher automaticamente:
- ID, projeto, plano de referência, fase de execução, prioridade (do PLAN)
- **Campo `Padrão de implementação:`** com resultado da árvore de decisão do Passo 5F.4
- **Seção §5 Contratos de Dados**: se TXC, tabela Transaction Map com fases e métodos semânticos; se ALT, contrato simplificado (Input/Output)
- Rastreabilidade §7 com referências ao PLAN e PRD
- Seção §6 Tasks vazia (a ser preenchida por `--feature-task`)

Apresentar o arquivo gerado ao usuário para revisão.

**Passo 5F.6 — Aguardar aprovação**

> *"FEAT-[nome].md criado com status Draft. Revise especialmente:*
> *- §2 Critérios de Aceite — cada item deve ser binário e verificável*
> *- §3 Comportamentos de Borda — adicione casos específicos do seu domínio*
> *- §4 Restrições Técnicas — inclua limites arquiteturais relevantes*
> *- §5 Contratos de Dados — se TXC, verifique os métodos semânticos e estados intermediários*
>
> *Quando aprovado, me diga 'aprovado' e eu atualizo o status.*
> *Próximo passo após aprovação: `/bks-sdd --feature-tests` para criar os cenários de teste*
> *desta feature. O `--feature-task` só gera tasks após o TEST estar aprovado."*

Ao receber aprovação, atualizar o campo `**Status:**` no arquivo de `Draft` para `Aprovada`.

**Passo 5F.7 — Registrar no log e salvar estado**

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --feature
  Projeto: project-[nome]
  Feature especificada: F[N] — [nome da feature]
  Arquivo: spec/features/FEAT-[nome].md
  Status: Aprovada
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

---

### Fase 5.3 — Tasks (`--feature-task`)

**Objetivo:** Decompor uma feature aprovada (com TEST aprovado) em tasks atômicas executáveis por agente.

**Passo 5T.1 — Identificar o projeto em foco**

Mesmo comportamento dos comandos anteriores.

**Passo 5T.2 — Verificar TEST spec aprovada (bloqueio TDD)**

Antes de listar features, verificar se existe `spec/tests/TEST-[nome].md` com `Status: Aprovada`
para a feature candidata.

- Se o TEST existir e estiver `Aprovada`: prosseguir normalmente.
- Se o TEST existir mas estiver `Draft`: avisar e bloquear:
  > *"Encontrei `TEST-[nome].md` com status Draft. A test spec precisa estar aprovada antes
  > de gerar tasks de implementação. Execute `/bks-sdd --feature-tests` ou revise e aprove
  > o TEST existente."*
- Se o TEST **não existir**: bloquear e orientar:
  > *"Não encontrei test spec para F[N] — [nome]. A Fase 5.2 exige que os cenários de teste
  > sejam definidos e aprovados antes de gerar tasks de implementação. Execute
  > `/bks-sdd --feature-tests` para criar o TEST-[nome].md."*

Aguardar que o usuário resolva o bloqueio antes de prosseguir. Não gerar tasks sem TEST aprovado.

**Passo 5T.3 — Listar FEATs aprovadas com TEST aprovado e sem tasks**

Verificar quais arquivos em `spec/features/` têm `Status: Aprovada`, TEST correspondente em
`spec/tests/` com `Status: Aprovada`, e seção §5 Tasks ainda vazia. Apresentar ao usuário:

> *"Features aprovadas com test spec aprovada, prontas para quebrar em tasks:*
> *F1 — [nome]*
> *F2 — [nome]*
> *Qual deseja quebrar agora?"*

Se não houver FEATs nessas condições, orientar:
> *"Não encontrei features com FEAT + TEST aprovados e sem tasks. Execute `/bks-sdd --feature`
> para criar specs de feature, depois `/bks-sdd --feature-tests` para criar as test specs correspondentes."*

**Passo 5T.4 — Ler o FEAT e o TEST aprovados**

Ler:
1. `spec/features/FEAT-[nome].md` — §2 Critérios de Aceite, §3 Comportamentos de Borda, §4 Restrições Técnicas, **§5 Contratos de Dados (Transaction Map)**, **campo `Padrão de implementação`**
2. `spec/tests/TEST-[nome].md` — §2 Cenários Principais, §3 Cenários de Borda
3. `references/task-spec-structure.md` — template canônico da TASK (v2 TXC-aware)

O TEST aprovado é a fonte de verdade para o "Definição de pronto" de cada task. As tasks devem
ser decompostas de forma que, ao final, todos os cenários do TEST estejam cobertos.

O campo `**Padrão de implementação:**` do FEAT determina a granularidade das tasks:
- **TXC**: uma task por método semântico do Transaction (granularidade por fase do handler)
- **ALT-1/2/3/4**: decomposição convencional (setup → testes RED → implementação GREEN)

**Passo 5T.5 — Decompor em tasks atômicas**

Regras de decomposição **quando padrão = TXC:**
- Uma task por método semântico do Transaction é a granularidade ideal:
  - TASK-00A (Teste) + TASK-00B (Impl): método Fase 1 — EntryHandler (`Hydrate{X}`)
  - TASK-00C (Teste) + TASK-00D (Impl): método Fase 2 — DomainService (`Apply{Regra}`)
  - TASK-00E (Teste) + TASK-00F (Impl): Fase 3 — InfraAdapter (`FinalizeWith` + persistência)
- Cada task declara no campo `**Método semântico alvo:**` qual método do Transaction implementa
- Sinal de alerta: Transaction com apenas Input+Output sem estado intermediário → reclassificar para ALT-1

Regras de decomposição **quando padrão = ALT-1/2/3/4:**
- Campo `**Método semântico alvo:**` = "n/a"
- Decomposição convencional: setup → testes RED → implementação GREEN → integração

Regras comuns (todos os padrões):
- Cada task cobre exatamente uma instrução atômica (um verbo, uma ação)
- Tasks de teste e implementação são geradas em pares (RED → GREEN)
- A task de implementação deve declarar dependência da task de teste correspondente

Gerar os arquivos `TASK-[id]-[descrição-kebab-case].md` em `spec/tasks/` seguindo o
template canônico. Para cada task, preencher:
- Campo `**Test Spec:**` com `spec/tests/TEST-[nome].md`
- Campo `**Feature:**` com `F[N] — [nome da feature]`
- Campo `**Padrão:**` com o padrão herdado do FEAT
- Campo `**Método semântico alvo:**` conforme regras acima
- Checklist "Definição de pronto" — se TXC, incluir item "Estado intermediário do Transaction verificado"
- 🔴 Checklist "Definição de pronto" — **sempre** incluir, em toda task que cria ou altera tipo
  público, função pública ou decisão estrutural:
  - `[ ] README.md e ARCHITECTURE.md atualizados com o que esta task produziu`
  - `[ ] Comentários seguem a convenção: contrato e guarda no código; decisão no ARCHITECTURE.md`
  - `[ ] Documentação tocada segue a skill bks-writing — writing_guard.py sem achado nos arquivos`

  > **Por que na geração da task, e não só na conferência:** a regra de documentação já existia em
  > `memory/documentação.md` quando o `nq-sec-sdk` foi construído — e as 21 tasks nasceram sem o
  > item, então nenhuma o cobrou. **Regra que não entra na DoD não é executada.**
- Campo `**Agente:**` com o valor derivado do tipo de task:
  - Tasks de tipo `Teste` (RED) → `implementador`
  - Tasks de tipo `Implementação` (GREEN) → `implementador`
  - Tasks de tipo `Setup`/`Infra` → `implementador`
  - Tasks de validação/revisão de critérios → `validador`
  - Tasks de coordenação entre features → `orquestrador`
  - Padrão quando em dúvida: `implementador`

**Passo 5T.6 — Atualizar o FEAT com as tasks geradas**

Após criar todas as tasks, atualizar a seção §6 do `FEAT-[nome].md` com a tabela completa:

```markdown
## 6. Tasks desta Feature

| ID | Descrição | Método semântico (se TXC) | Tipo | Dependência |
|----|-----------|--------------------------|------|-------------|
| TASK-001 | [descrição curta] | HydrateCliente (Fase 1) | Teste | nenhuma |
| TASK-002 | [descrição curta] | HydrateCliente (Fase 1) | Implementação | TASK-001 |
| TASK-003 | [descrição curta] | ApplyPricing (Fase 2) | Teste | TASK-002 |
| TASK-004 | [descrição curta] | ApplyPricing (Fase 2) | Implementação | TASK-003 |
```

Atualizar também o campo `**Status:**` do FEAT para `Em execução`.

**Passo 5T.7 — Registrar no log e salvar estado**

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --feature-task
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  TEST referenciado: spec/tests/TEST-[nome].md (Status: Aprovada)
  Tasks geradas: TASK-[001..N]
  Arquivos criados: spec/tasks/TASK-[id]-*.md (N arquivos)
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

Orientar o usuário:
> *"[N] tasks geradas para F[N] — [nome]. A ordem respeita TDD: tasks de teste primeiro (RED),
> depois implementação (GREEN). Execute as tasks na sequência indicada pelas dependências.*
>
> *Próximo passo: `/bks-sdd --feature-list` para ver o estado geral do projeto, ou
> `/bks-sdd --feature` para especificar a próxima feature."*

---

## Fase 5.2 — Test Scenarios

### Quando invocar esta fase

O usuário executa `/bks-sdd --feature-tests` ou `/bks-sdd --feature-tests-list`, ou solicita
a criação de cenários de teste para uma feature:
- *"cria os testes da feature X"*
- *"quero a test spec da F2"*
- *"feature-tests para o projeto [nome]"*
- *"define os cenários de teste antes de gerar as tasks"*

**Posição no ciclo:** 5.1 Spec (FEAT aprovado) → **5.2 Test Scenarios (TEST)** → 5.3 Tasks

**Pré-requisito:** Existir pelo menos uma feature com `Status: Aprovada` em `spec/features/`.
O TEST é criado **depois** do FEAT aprovado e **antes** das tasks — esta ordem é estrutural.

**Template canônico:** ler `references/test-spec-structure.md` antes de gerar qualquer artefato.

---

### Comando `--feature-tests-list`

**Objetivo:** Mostrar o estado das test specs de todas as features do projeto em foco.

**Passo 5.2L.1 — Identificar o projeto em foco**

Mesmo comportamento das fases anteriores: um projeto → usa automaticamente; vários → pergunta.

**Passo 5.2L.2 — Construir a tabela de status**

Para cada feature listada no `PLAN-[nome].md` §3, verificar:
- Existe `spec/features/FEAT-[nome].md`? → qual o Status?
- Existe `spec/tests/TEST-[nome].md`? → qual o Status?

Apresentar a tabela:

```
Projeto: project-[nome]
Plano: PLAN-[nome].md

ID  | Feature                    | FEAT Status  | TEST Status       | Tasks
----|----------------------------|--------------|-------------------|-------
F1  | [nome]                     | ✅ Aprovada  | ✅ Aprovada       | 4 tasks
F2  | [nome]                     | ✅ Aprovada  | 📝 Draft          | —
F3  | [nome]                     | ✅ Aprovada  | ⛔ Não criado     | —
F4  | [nome]                     | 📝 Draft     | ⛔ Não aplicável  | —
F5  | [nome]                     | ⏳ Pendente  | ⛔ Não aplicável  | —
```

Legenda:
- ✅ Aprovada — artefato existe e foi aprovado pelo usuário
- 📝 Draft — artefato existe mas ainda não aprovado
- ⛔ Não criado — FEAT aprovado mas TEST ainda não foi gerado (ação necessária)
- ⛔ Não aplicável — FEAT não aprovado; TEST não pode ser criado ainda

---

### Comando `--feature-tests`

**Objetivo:** Gerar a test spec de uma feature aprovada. Uma feature por vez.

**Passo 5.2T.1 — Identificar o projeto em foco**

Mesmo comportamento dos comandos anteriores.

**Passo 5.2T.2 — Listar FEATs aprovadas sem TEST**

Verificar quais arquivos em `spec/features/` têm `Status: Aprovada` e **não** têm
`spec/tests/TEST-[mesmo-nome].md` correspondente. Apresentar ao usuário:

> *"Features aprovadas sem test spec (Fase 5.2):*
> *F2 — [nome]*
> *F3 — [nome]*
> *Qual deseja criar a test spec agora? (sugestão: mesma ordem de prioridade do plano)"*

**Regra importante:** Nunca gerar test specs de múltiplas features de uma vez.
Uma feature → revisão e aprovação do TEST → próxima. Mesmo princípio iterativo da Fase 5.1.

Se todas as features aprovadas já têm TEST, informar:
> *"Todas as features aprovadas já têm test spec. Use `/bks-sdd --feature-task` (Fase 5.3) para gerar
> tasks de implementação, ou `/bks-sdd --feature` para especificar novas features."*

**Passo 5.2T.3 — Ler o FEAT aprovado**

Ler integralmente `spec/features/FEAT-[nome-escolhido].md`. Extrair especificamente:
- §2 Critérios de Aceite — fonte dos Cenários Principais (relação 1:1 mínima)
- §3 Comportamentos de Borda — fonte dos Cenários de Borda (cada linha vira pelo menos um caso)
- §4 Restrições Técnicas — informa as Pré-condições de Ambiente e pode influenciar tipos de borda

**Se o projeto adotar DDD ou Arquitetura Hexagonal**, verificar nos cenários de borda se existem
casos de `Concorrência` (múltiplos aggregates) ou `Resiliência` (adapters externos). Se o FEAT §4
menciona portas/adapters, incluir cenários de resiliência para cada adapter externo referenciado.

**Passo 5.2T.4 — Gerar o TEST-[nome].md**

Ler `references/test-spec-structure.md` para o template canônico.

Gerar `spec/tests/TEST-[nome-kebab-case].md` com **o mesmo nome** do FEAT correspondente.
Status inicial: `Draft`.

Preencher:
- §2 Cenários Principais: um cenário Gherkin por critério de aceite do §2 do FEAT (1:1 mínimo)
- §3 Cenários de Borda: uma linha por comportamento de borda do §3 do FEAT (1:1 mínimo), com coluna Tipo preenchida
- §4 Fora de Escopo: pelo menos 1 linha — se nenhum se aplicar, escrever *"Nenhum caso identificado como fora de escopo para esta feature."*
- §5 Pré-condições de Ambiente: derivadas do §4 Restrições Técnicas do FEAT
- §6 Rastreabilidade: referências ao FEAT e ao PLAN

Regras Gherkin obrigatórias:
- `Given` = estado antes da ação, nunca a ação em si
- `When` = uma ação singular
- `Then` = estado depois, não o processo
- Sem condicional (`if`, `or`) — separar em cenários distintos
- Sem `But` — usar cenário separado para comportamento alternativo

Apresentar o arquivo gerado ao usuário para revisão.

**Passo 5.2T.5 — Aguardar aprovação**

> *"TEST-[nome].md criado com status Draft (Fase 5.2). Revise especialmente:*
> *- §2 Cenários Principais — cada critério de aceite do FEAT tem um cenário correspondente?*
> *- §3 Cenários de Borda — cada comportamento de borda do FEAT está coberto?*
> *- §4 Fora de Escopo — há casos que outro agente poderia implementar por engano?*
>
> *Quando aprovado, me diga 'aprovado' e eu atualizo o status para Aprovada.*
> *Após aprovação, execute `/bks-sdd --feature-task` (Fase 5.3) para gerar as tasks.*
> *O `--feature-task` só libera tasks quando este TEST estiver com Status: Aprovada."*

Ao receber aprovação, atualizar o campo `**Status:**` de `Draft` para `Aprovada`.

**Passo 5.2T.6 — Registrar no log e salvar estado**

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --feature-tests (Fase 5.2)
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  FEAT lido: spec/features/FEAT-[nome].md (Status: Aprovada)
  Resultado: spec/tests/TEST-[nome].md gerado
  Status: Aprovada
  Cenários principais: [N] (cobre [N] critérios de aceite)
  Cenários de borda: [N]
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

---

## Fluxo completo — Fase 5 (5.1 · 5.2 · 5.3)

O ciclo correto para cada feature, do plano à task executável:

```
PLAN-[nome].md
    ↓
Fase 5.1 — /bks-sdd --feature          → FEAT-[nome].md      (Draft → Aprovada)
    ↓
Fase 5.2 — /bks-sdd --feature-tests    → TEST-[nome].md      (Draft → Aprovada)
    ↓
Fase 5.3 — /bks-sdd --feature-task     → TASK-[id]-*.md      (Pendente → em execução)
    ↓
Fase 6   — Implementação               → (a definir)
```

**Regras de bloqueio estrutural:**
- `--feature-tests` (5.2) só executa se existir FEAT com `Status: Aprovada`
- `--feature-task` (5.3) só executa se existir TEST com `Status: Aprovada`
- Não é possível pular sub-fases — a sequência 5.1 → 5.2 → 5.3 é estrutural

**Visibilidade do estado:**
- `/bks-sdd --feature-list` — visão geral de todas as features (FEAT + TEST + Tasks)
- `/bks-sdd --feature-tests-list` — foco específico no estado das test specs (Fase 5.2)

### Output da Fase 5.2

- Arquivo: `workspace-[nome]/projects/project-[nome-do-projeto]/spec/tests/TEST-[nome-kebab-case].md`
- Formato: Markdown conforme `references/test-spec-structure.md`
- **Idioma: PT-BR — obrigatório**

---

## Fase 6 — Implementação

> **Dois modos de execução disponíveis:**
> - **Via skill** (este documento): `/bks-sdd --impl-init` + `--task-run --agent` — Claude Code gera o código diretamente na sessão.
> - **Via agentes autônomos** (`agents/`): pipeline Node.js externo com Bootstrap, PO, Arquiteto, Planejador, Spec Writer, QA, Task Decomposer e Orquestrador. Consulte `agents/INSTALL-AGENTS.md` para instalação e `agents/USE-AGENTS-STEPBYSTEP.md` para uso.
>
> Os dois modos são complementares — as Fases 0–5.3 (especificação) são sempre via skill; a Fase 6 (execução) pode usar qualquer um dos dois.

A Fase 6 é o ciclo de execução das tasks geradas na Fase 5.3. Diferente das fases anteriores,
ela **executa e verifica** — não apenas específica. A skill age como orquestrador de execução.

**Pré-condições:**
- Projeto com `PLAN-[nome].md` aprovado (Fase 4)
- Pelo menos uma feature com `FEAT-[nome].md` + `TEST-[nome].md` aprovados (Fases 5.1 e 5.2)
- Pelo menos uma `TASK-[id].md` gerada (Fase 5.3)
- Stack declarada em `research/stack.md` do projeto (coletada no `--project`, Fase 2)

**Estrutura `spec/output/` (D2):**
```
spec/output/
├── results/
│   ├── IMPL-[feature].md          ← contrato de stack (gerado no --impl-init)
│   └── OUTPUT-TASK-[id].md        ← log de execução por task
└── code/
    └── [feature]/
        └── [arquivos gerados]     ← código-fonte; preenchido apenas no Modo Agente
```

> O rastreamento de progresso das tasks é feito via `TodoWrite` (não em arquivo PROGRESS-*.md).
> O `--status` lê o estado diretamente do `TodoWrite` — sem leitura de arquivos adicionais.

- `results/` é sempre preenchido, independente do modo de execução
- `code/` só é preenchido no **Modo Agente** (`--agent`); no Modo Contexto (`--context`) fica vazio
- O código em `code/` é staging temporário — o desenvolvedor move para o repositório real quando aprovado
- O workspace **nunca substitui o repositório real**

**Campo de agente nas tasks (D3):**

Cada task recebe o campo:
```markdown
**Agente:** implementador   ← valores: orquestrador | implementador | validador
```
Mapeamento PBQ (framework Harness Engineering):
- `orquestrador` — coordena, não implementa; gerência dependências e ordem
- `implementador` — escreve código e testes
- `validador` — verifica critérios de aceite, roda checklist do TEST spec

---

### Comando `--impl-init` — Inicializar ciclo de implementação

**Trigger:** `/bks-sdd --impl-init`

**Objetivo:** Preparar o contexto de implementação para uma feature. Gera o `IMPL-[feature].md`
com o contrato de stack e inicializa as tasks no `TodoWrite`.

**Fluxo:**

**Passo 6I.1 — Identificar o projeto em foco**

Mesmo comportamento das fases anteriores: um projeto → usa automaticamente; vários → pergunta.

**Passo 6I.2 — Listar features prontas para implementação**

Verificar quais features têm `TASK-[id].md` em `spec/tasks/` com status `Pendente`.
Apresentar ao usuário:

> *"Features prontas para implementação (com tasks pendentes):*
> *F1 — [nome] (3 tasks pendentes)*
> *F2 — [nome] (4 tasks pendentes)*
> *Qual deseja iniciar?"*

Se nenhuma feature tiver tasks pendentes:
> *"Não encontrei features com tasks pendentes. Execute `/bks-sdd --feature-task` (Fase 5.3)
> para gerar tasks antes de iniciar a implementação."*

**Passo 6I.3 — Ler a stack do projeto**

Ler `research/stack.md` do projeto. Extrair Framework, Database e Mensageria.

Se `stack.md` não existir ou tiver campos `A definir`, perguntar ao usuário os campos em falta
e **atualizar o arquivo `research/stack.md` com as respostas** antes de prosseguir.
Não perguntar campos já preenchidos.

**Passo 6I.4 — Identificar skill de implementação**

Mapear o Framework para a skill correspondente:
- `.NET` → `bks-dotnet-solutions`
- `Spring (Java/Kotlin)` → `bks-spring-solutions` *(ainda não disponível)*
- `TypeScript (Node.js)` → `bks-typescript-solutions`
- `Go` → `bks-go-solutions` *(ainda não disponível)*

Se a skill de implementação não estiver disponível para o framework declarado:
- Definir modo padrão automaticamente como **Modo Contexto** (`--context`)
- Informar ao usuário (não perguntar — comportamento é automático):
  > *"A skill de implementação para [Framework] ainda não está disponível. O ciclo desta feature
  > usará Modo Contexto — pacotes de contexto para execução externa."*
- Pular o Passo 6I.5 (modo já definido)

**Passo 6I.5 — Definir modo de execução padrão** *(executar somente se skill disponível)*

Perguntar ao usuário:

> *"Qual modo de execução padrão para esta feature?*
> *`1` Modo Agente (`--agent`) — Claude gera o código diretamente em `spec/output/code/`*
> *`2` Modo Contexto (`--context`) — Claude monta pacote de contexto para agente externo"*

Aguardar resposta. O modo padrão pode ser sobrescrito por task no `--task-run`.

**Passo 6I.6 — Gerar IMPL-[feature].md**

Criar `spec/output/results/IMPL-[feature-kebab].md`:
```markdown
# IMPL — [Nome da Feature]

**Feature:** F[N] — [nome]
**Projeto:** project-[nome]
**Criado:** [data]
**Atualizado:** [data]

## Stack

**Framework:** [valor]
**Database:** [valor]
**Mensageria:** [valor]
**Skill de implementação:** [skill ou "Não disponível — usar Modo Contexto"]

## Modo de execução padrão

[Agente | Contexto]

## Agente padrão do ciclo

[orquestrador | implementador | validador]

## Tasks em ordem de execução

| ID | Descrição | Tipo | Agente | Dependência |
|----|-----------|------|--------|-------------|
| TASK-001 | [desc] | Teste | implementador | — |
| TASK-002 | [desc] | Impl. | implementador | TASK-001 |
...

## Observações
[Qualquer restrição específica desta feature para implementação]
```

**Passo 6I.7 — Inicializar tasks no TodoWrite**

Usar `TodoWrite` para registrar todas as tasks da feature com status `pending`:
- Para cada task em `spec/tasks/` da feature (na ordem de execução do IMPL-[feature].md):
  - `content`: `"[TASK-id] — [descrição curta]"` (forma imperativa)
  - `activeForm`: `"Executando [TASK-id] — [descrição curta]"`
  - `status`: `pending`

Isso inicializa o rastreamento visual de progresso — nenhum arquivo PROGRESS-*.md é criado.

**Passo 6I.8 — Registrar no log e orientar**

Registrar no `.logs/session-[data].md`:
```
- [HH:MM] Comando: /bks-sdd --impl-init
  Projeto: project-[nome]
  Feature: F[N] — [nome da feature]
  Stack: Framework=[...] / Database=[...] / Mensageria=[...]
  Modo padrão: [Agente|Contexto]
  Tasks: [N] tarefas listadas em ordem de execução
  Artefatos: IMPL-[feature].md; tasks inicializadas no TodoWrite
```

Criar snapshot em `.states/state-[YYYY-MM-DDTHH-MM].md`.

Orientar o usuário:
> *"IMPL-[feature].md criado. Ciclo de implementação iniciado para F[N] — [nome].*
> *[N] tasks pendentes. Próximo passo: `/bks-sdd --task-run TASK-001` para iniciar a primeira task.*
> *Se encerrar a sessão antes de terminar, use `/bks-sdd --continue` na próxima sessão — o estado será recuperado automaticamente."*

---

### Comando `--task-run` — Executar uma task

**Trigger:** `/bks-sdd --task-run [TASK-id]` ou `/bks-sdd --task-run [TASK-id] --agent` ou `--context`

**Objetivo:** Iniciar a execução de uma task específica. Monta o contexto completo e executa
no modo configurado.

**Passo 6R.1 — Verificar pré-condições**

Verificar se existe `IMPL-[feature].md` correspondente à feature da task em `spec/output/results/`.
Se não existir:
> *"Não encontrei contrato de implementação para esta feature. Execute `/bks-sdd --impl-init`
> antes de rodar tasks de implementação."*

**Passo 6R.2 — Ler a task e verificar dependências**

Ler `TASK-[id].md` integralmente.

Se a task tem campo `**Dependência:**` preenchido, verificar se a task dependente está com
status `completed` no `TodoWrite`:
> *"TASK-[id] depende de TASK-[dep] que ainda não foi concluída.*
> *Conclua a tarefa dependente antes de continuar."*

**Passo 6R.3 — Determinar modo de execução**

- Se flag `--agent` fornecida: usar Modo Agente
- Se flag `--context` fornecida: usar Modo Contexto
- Se nenhuma flag: ler o campo `**Modo de execução padrão:**` em `spec/output/results/IMPL-[feature].md` e usar esse valor

**Passo 6R.4 — Atualizar status**

Atualizar `TASK-[id].md`: campo `**Status:**` → `Em execução`
Atualizar o `TodoWrite`: marcar a task `[TASK-id] — [descrição]` como `in_progress`

**Passo 6R.5 — Executar no modo definido**

**Modo Agente (`--agent`):**

Usar a tool `Agent` para isolar o contexto do implementador. O subagente recebe apenas os
artefatos necessários — sem o histórico completo da sessão principal.

Construir o prompt do subagente com:
1. Conteúdo completo de `TASK-[id].md`
2. Conteúdo completo de `FEAT-[feature].md`
3. Conteúdo completo de `TEST-[feature].md`
4. Seção Stack do `IMPL-[feature].md`
5. Instrução de caminho de saída: `spec/output/code/[feature]/`
6. Se skill de implementação disponível: instrução para seguir convenções da skill de stack

Seleção de modelo para o subagente:
- `sonnet` — tasks de lógica complexa, domínio, integrações
- `haiku` — tasks operacionais simples (estrutura de pastas, boilerplate, configs)

O subagente gera os arquivos em `spec/output/code/[feature]/` e retorna lista dos artefatos criados.

Ao receber o resultado do subagente:
> *"Execução concluída. Arquivos gerados em `spec/output/code/[feature]/`:*
> *- [lista de arquivos retornada pelo subagente]*
> *Execute `/bks-sdd --task-done TASK-[id]` para confirmar com o checklist do TEST spec."*

**Modo Contexto (`--context`):**

Montar e exibir o pacote de contexto:
```
Pacote TASK-[id]:
→ Stack: [Framework] / [Database] / [Mensageria]
→ Feature: F[N] — [nome]
→ Instrução: [instrução completa da task]
→ Agente: [valor do campo Agente da task]
→ Caminho esperado: [derivado da arquitetura do projeto]
→ Contrato de teste (cenários relevantes):
   - [cenário 1 do TEST-[nome].md]
   - [cenário de borda relevante]
→ Critério de aceite:
   - [checklist da task]
→ Dependências: [tasks concluídas que esta task consome]

Execute a implementação externamente e retorne com `/bks-sdd --task-done TASK-[id]`
para validar com o checklist do TEST spec.
```

**Passo 6R.6 — Gerar OUTPUT-TASK-[id].md**

Criar `spec/output/results/OUTPUT-TASK-[id].md`:
```markdown
# OUTPUT — TASK-[id]

**Task:** TASK-[id] — [descrição]
**Feature:** F[N] — [nome]
**Modo:** [Agente | Contexto]
**Iniciado:** [timestamp]
**Status:** Em execução

## Resultado da execução

[Modo Agente: lista de arquivos gerados]
[Modo Contexto: pacote de contexto montado]

## Checklist de verificação (preenchido no --task-done)

[a preencher]
```

---

### Comando `--task-done` — Marcar task como concluída

**Trigger:** `/bks-sdd --task-done [TASK-id]`

**Objetivo:** Fechar o ciclo de uma task executada. Implementa o Sensor do Harness Engineering.
O comportamento bifurca conforme o modo em que a task foi executada: **Modo Agente** (verificação
automática interna, sem interação humana) ou **Modo Contexto** (checklist interativo, aguarda
confirmação do usuário).

**Passo 6D.1 — Verificar status da task**

Verificar se `TASK-[id].md` tem status `Em execução`.
Se não:
> *"TASK-[id] não está com status 'Em execução'. Execute `/bks-sdd --task-run TASK-[id]`
> antes de marcar como concluída."*

**Passo 6D.2 — Ler TEST spec, cenários relevantes e determinar modo**

1. Ler `TEST-[nome].md` (campo `**Test Spec:**` da task).
2. Identificar os cenários do TEST relevantes à instrução desta task (por proximidade semântica).
3. Ler o campo `**Modo:**` em `spec/output/results/OUTPUT-TASK-[id].md`.
   - Se `Modo: Agente` → seguir o caminho **6D.3A** (verificação automática)
   - Se `Modo: Contexto` → seguir o caminho **6D.3C** (checklist interativo)

**Passo 6D.2E — Validação opcional no sandbox E2B** *(executar antes de qualquer verificação se E2B MCP disponível)*

Se E2B MCP estiver disponível no ambiente:
1. Verificar se a stack do projeto tem sandbox E2B compatível:
   - `.NET` → `dotnet` | `TypeScript/Node.js` → `node` | `Spring (Java)` → `java` | `Go` → `go`
2. Se stack compatível, perguntar ao usuário:
   > *"E2B MCP detectado. Deseja executar a suite de testes no sandbox antes de confirmar os cenários? (s/n)"*
3. Se usuário confirma `s`:
   - Executar no sandbox E2B: build + testes da stack declarada no projeto
   - Registrar resultado no cabeçalho de `TASK-[id].md`:
     ```
     **E2B Sandbox:** pass | fail — [output resumido em 1-2 linhas]
     ```
   - Se resultado = `fail`:
     > *"⚠️ Sandbox E2B retornou falha. Corrija o código antes de prosseguir.*
     > *Output: [output resumido]*
     > *Execute `/bks-sdd --task-done TASK-[id]` novamente após a correção."*
     - Interromper o fluxo (não apresentar checklist de TCs).
   - Se resultado = `pass`: registrar e prosseguir para o caminho 6D.3A ou 6D.3C normalmente.
4. Se usuário responde `n`: prosseguir diretamente para o caminho definido no Passo 6D.2.

Se E2B MCP indisponível, retornar erro ou stack sem sandbox compatível:
- Registrar no log: *"E2B MCP indisponível — passo de sandbox omitido"*
- Prosseguir diretamente para 6D.3A ou 6D.3C. Nenhum erro exibido ao usuário.

---

#### Caminho Modo Agente — Verificação automática

**Passo 6D.3A — Verificar internamente a cobertura dos cenários**

Sem interação com o usuário. Ler os arquivos gerados em `spec/output/code/[feature]/` e
verificar se cada cenário relevante do TEST spec está coberto pela implementação produzida
no `--task-run`:

- Para cada cenário: verificar se existe implementação correspondente nos arquivos gerados
  (by naming, structure, or logic match)
- Construir internamente a lista: `cenários cobertos` vs `cenários ausentes ou incompletos`

**Passo 6D.3B — Verificar a documentação de entrega** 🔴 *obrigatório, os dois modos*

**Task sem `README.md` e `ARCHITECTURE.md` atualizados não está concluída** — mesmo peso do build
e dos testes. Executar **antes** de marcar a task como concluída, em qualquer modo.

Aplica-se quando a task criou ou alterou **tipo público, função pública ou decisão estrutural**.
Task puramente interna (refatoração sem mudança de superfície) pula este passo.

Verificar, na raiz do projeto:

| Arquivo | O que confere |
|---|---|
| `README.md` | o que é · como rodar · estrutura (1 nível) · stack · links. **Nunca ADR nem detalhe classe-a-classe** |
| `ARCHITECTURE.md` | índice · camadas · ADRs curtos (linka `decisions/` se existir, sem duplicar) · **dicionário dos tipos criados ou alterados nesta task** |

Se algum estiver ausente ou desatualizado em relação ao que a task produziu: **gerar ou atualizar
agora**, e só então prosseguir. Não perguntar ao usuário se deve fazer — é comportamento
automático [`memory/documentação.md`].

**Verificar também a convenção de comentário** no código produzido:

- **fica:** resumo de 1 linha em membro público (o **quê**) e guarda contra regressão de até 2
  linhas (o que quebra, sem ponteiro para documento)
- **sai:** decisão, trade-off, histórico, comparação com implementação anterior — vive no
  `ARCHITECTURE.md`
- **proibido:** marca de severidade (🔴 ⚠️ 🟡) em comentário; **bloco acima de 5 linhas**

> 🔴 **Regra sem guarda executável é intenção.** Onde a stack permitir, a verificação de comentário
> deve virar **teste de arquitetura** no projeto — não checagem manual a cada task. Referência:
> `CommentBudgetTests` no `nq-sec-sdk` (dois testes: bloco acima do teto, marca de severidade).

---

**Passo 6D.4A-ok — Todos os cenários cobertos (Agente, Sucesso)**

1. Atualizar `TASK-[id].md`: `**Status:**` → `Concluída`
2. Marcar a task como `completed` no `TodoWrite`
3. Atualizar `OUTPUT-TASK-[id].md`: timestamp de conclusão + lista de cenários verificados + `Status: Concluída`
4. Verificar se todas as tasks da feature foram concluídas (todas `completed` no TodoWrite):
   - Se sim: atualizar `FEAT-[nome].md` `**Status:**` → `Concluída`
5. Registrar no log e salvar snapshot.
6. **Sem pausas.** Avançar diretamente: verificar a próxima task `pending` no TodoWrite e
   chamar internamente `--task-run TASK-[próxima]` se houver dependências resolvidas. Informar:
   > *"✅ TASK-[id] concluída automaticamente. Progresso: [X/N tasks]. Iniciando TASK-[próxima]..."*

**Passo 6D.4A-fail — Algum cenário não coberto (Agente, Falha)**

1. Manter status `Em execução`
2. Registrar no `OUTPUT-TASK-[id].md`: quais cenários não foram cobertos + gap identificado
3. Tentar autocorreção: se o gap for localizado (um arquivo ou função ausente), gerar a correção
   em `spec/output/code/[feature]/` e repetir o passo 6D.3A
4. Se após autocorreção o cenário ainda falhar, **interromper e informar o usuário**:
   > *"⚠️ TASK-[id] — gap não resolvido automaticamente.*
   > *Cenário: [nome do cenário]*
   > *Gap: [descrição precisa do que está faltando]*
   > *Arquivos gerados estão em `spec/output/code/[feature]/`. Corrija e execute*
   > *`/bks-sdd --task-done TASK-[id]` para revalidar."*

---

#### Caminho Modo Contexto — Checklist interativo

**Passo 6D.3C — Apresentar checklist interativo**

> *"Antes de marcar TASK-[id] como concluída, confirme os cenários do TEST-[nome].md:*
>
> *☐ Cenário 1 — [nome]: passou?*
> *☐ E1 — [edge case]: passou?*
> *☐ E3 — [edge case]: passou?*
> *☐ `README.md` e `ARCHITECTURE.md` atualizados com o que esta task produziu?*
>
> *Responda 'sim' para cada um, ou informe qual falhou e o motivo."*

O item de documentação **não é opcional** e vale para toda task que tocou tipo público, função
pública ou decisão estrutural — ver Passo 6D.3B. Se o usuário responder que não, **gerar ou
atualizar os arquivos antes de fechar a task**, não apenas registrar o gap.

Aguardar resposta do usuário antes de prosseguir.

**Passo 6D.4C-ok — Todos os cenários confirmados (Contexto, Sucesso)**

1. Atualizar `TASK-[id].md`: `**Status:**` → `Concluída`
2. Marcar a task como `completed` no `TodoWrite`
3. Atualizar `OUTPUT-TASK-[id].md`: timestamp de conclusão + cenários confirmados pelo usuário + `Status: Concluída`
4. Verificar se todas as tasks da feature foram concluídas (todas `completed` no TodoWrite):
   - Se sim: atualizar `FEAT-[nome].md` `**Status:**` → `Concluída`
   - Informar: *"Todas as tasks da feature F[N] — [nome] foram concluídas! ✅"*
5. Registrar no log e salvar snapshot.
6. Orientar e aguardar próximo comando do usuário:
   > *"TASK-[id] concluída ✅. Progresso: [X/N tasks].*
   > *Próximo passo: `/bks-sdd --task-run TASK-[próxima]`"*

**Passo 6D.4C-fail — Algum cenário falhou (Contexto, Falha)**

1. Manter status `Em execução`
2. Registrar no `OUTPUT-TASK-[id].md`: qual cenário falhou + motivo informado pelo usuário
3. Orientar:
   > *"[N] cenário(s) não passaram. Corrija a implementação e execute*
   > *`/bks-sdd --task-done TASK-[id]` novamente quando todos estiverem passando."*

---

### Comando `--status` — Dashboard de progresso do workspace

**Trigger:** `/bks-sdd --status`

**Objetivo:** Exibir o estado completo do workspace em visão de árvore — projetos, features e tasks.

**Fluxo:**

**Passo 6S.1 — Localizar workspace e projetos**

Localizar `workspace-*/`. Para cada projeto em `projects/`, ler `PLAN-[nome].md`.

**Passo 6S.2 — Agregar progresso**

Para cada feature de cada projeto:
- Ler o estado atual do `TodoWrite` para obter tasks e seus status (`pending` / `in_progress` / `completed`)
- Se o TodoWrite não tiver tasks desta feature (ciclo não iniciado), contar arquivos `TASK-[id].md`
  em `spec/tasks/` e verificar o campo `**Status:**` de cada um como fallback

**Passo 6S.3 — Exibir dashboard**

```
workspace-[nome]
└── project-[nome-1]     [6/8 tasks — 75%]
    ├── F1 [nome]        ✅ 3/3 tasks concluídas
    ├── F2 [nome]        🔄 2/3 tasks (1 em execução)
    └── F3 [nome]        ⏳ 0/2 tasks pendentes
└── project-[nome-2]     [0/5 tasks — 0%]
    └── F1 [nome]        ⏳ Não iniciada
```

Ícones de status de feature:
- ✅ Concluída — todas as tasks concluídas
- 🔄 Em andamento — pelo menos uma task Em execução ou Concluída
- ⏳ Pendente — nenhuma task iniciada ainda
- 📝 Sem tasks — feature com FEAT/TEST aprovados mas tasks não geradas ainda

---

### Comando `--task-list` — Listar tasks de uma feature

**Trigger:** `/bks-sdd --task-list` ou `/bks-sdd --task-list [feature-id]`

**Objetivo:** Mostrar o estado detalhado das tasks de uma feature específica.

**Fluxo:**

**Passo 6L.1 — Identificar feature**

- Se argumento fornecido (ex: `F1`): usar diretamente se existir no plano.
- Se não fornecido: listar features com tasks e perguntar ao usuário.

**Passo 6L.2 — Exibir tabela de tasks**

```
Feature: F[N] — [nome]
IMPL: spec/output/results/IMPL-[feature].md
Progresso: [X/N] tasks concluídas

ID        | Descrição                    | Tipo   | Agente        | Dep.  | Status
----------|------------------------------|--------|---------------|-------|----------
TASK-001  | [desc]                       | Teste  | implementador | —     | ✅ Concluída
TASK-002  | [desc]                       | Impl.  | implementador | T001  | 🔄 Em execução
TASK-003  | [desc]                       | Impl.  | implementador | T002  | ⏳ Pendente
```

---

### Comportamento do `--continue` na Fase 6 (D6)

Quando a fase ativa detectada for a Fase 6 (existem tasks Em execução ou Pendente),
o `--continue` exibe adicionalmente ao resumo padrão:

```
Fase ativa: 6 — Implementação
Projeto: project-[nome]
Feature em andamento: F[N] — [nome]
Tasks pendentes: TASK-002, TASK-003, TASK-005
Próximo passo sugerido: TASK-002 — [descrição] (sem dependências bloqueadas)
```

Seguido pelo dashboard `--status` completo do workspace.

O `--continue` **não retoma a execução automaticamente** — apenas mostra o estado e sugere
o próximo comando. O usuário deve confirmar com `/bks-sdd --task-run [TASK-id]` para avançar.
Isso previne execução acidental de tasks sem intenção explícita.

---

### Fluxo completo — Fase 6 (happy path)

**Modo Contexto** — interação humana em cada etapa:
```
Fases 1–5 concluídas (PLAN + FEAT + TEST + TASKS geradas)
    ↓
/bks-sdd --impl-init                  → IMPL-[feature].md + tasks inicializadas no TodoWrite
    ↓
/bks-sdd --task-run TASK-001 --context
    ↓ (entrega pacote de contexto → usuário executa externamente)
/bks-sdd --task-done TASK-001
    ↓ (checklist interativo → usuário confirma cenários → TASK-001 Concluída)
Usuário chama --task-run TASK-002 manualmente, repete até o fim
    ↓
Todas as tasks concluídas → FEAT-[nome].md: Concluída
    ↓
/bks-sdd --status           → feature aparece ✅ no dashboard
```

**Modo Agente** — execução autônoma, sem pausas entre tasks:
```
Fases 1–5 concluídas (PLAN + FEAT + TEST + TASKS geradas)
    ↓
/bks-sdd --impl-init                  → IMPL-[feature].md + tasks inicializadas no TodoWrite
    ↓
/bks-sdd --task-run TASK-001 --agent
    ↓ (agente gera código em spec/output/code/)
    → --task-done TASK-001 chamado automaticamente pelo agente
    ↓ (verificação interna dos cenários do TEST spec)
    → se ok: avança automaticamente para --task-run TASK-002 --agent
    → se falha localizada: tenta autocorreção e revalida
    → se falha irrecuperável: para e informa o usuário com gap preciso
Ciclo se repete até todas as tasks concluídas ou bloqueio explícito
    ↓
Todas as tasks concluídas → FEAT-[nome].md: Concluída (automático)
    ↓
/bks-sdd --status           → feature aparece ✅ no dashboard
```

**Bloqueios estruturais da Fase 6:**
- `--task-run` sem `--impl-init` prévio → bloqueado
- `--task-run` com dependência não concluída → bloqueado
- `--task-done` sem `--task-run` prévio (status diferente de Em execução) → bloqueado
- `--impl-init` para feature sem tasks → bloqueado; orientar Fase 5.3
- Modo Agente: `--task-done` sem arquivos em `spec/output/code/` → bloqueado; reexecutar `--task-run`

### Edge cases da Fase 6

| Situação | Comportamento |
|----------|---------------|
| Stack não declarada no projeto | Perguntar antes de gerar IMPL; salvar em `stack.md` |
| Skill de stack não disponível | Modo Contexto obrigatório; informar antes de iniciar |
| `--task-done` (Contexto) com cenário falhando | Manter Em execução; registrar falha; orientar correção |
| `--task-done` (Agente) com cenário não coberto | Tentar autocorreção; se falhar, interromper e reportar gap |
| Feature concluída parcialmente | Não marcar FEAT como Concluída até todas as tasks done |
| Task com dependência Em execução | Bloquear; mostrar qual task precisa concluir antes |
| Modo Agente sem arquivos gerados em code/ | Bloquear --task-done; reportar que --task-run não produziu output |

---

## Fase 7 — Custo & Telemetria

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
