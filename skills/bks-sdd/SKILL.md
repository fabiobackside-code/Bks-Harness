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

**Siglas**

- PRD — documento de requisitos do produto (PRD)
- PLAN — plano macro do projeto (PLAN)
- ARCH — índice da arquitetura aprovada (ARCH)
- FEAT — especificação da feature (FEAT)
- TEST — cenários de teste da feature (TEST)
- TASK — instrução atômica de implementação (TASK)
- TXC — Transaction Context, o padrão de transação do kit (TXC)
- DDD — Domain-Driven Design (DDD)
- TDD — desenvolvimento guiado por teste (TDD), com RED (teste falhando) e GREEN (teste passando)
- P0 — prioridade máxima do plano (P0)
- IMPL — contrato de implementação da feature (IMPL)
- OUTPUT — registro de execução da task (OUTPUT)
- SDD — Spec-Driven Development (SDD)
- BKS — Backside, o padrão de engenharia do kit (BKS)
- RPI — o ciclo Research → Plan → Implement (RPI)

## Conduta — vale em todas as fases

**Entregue o que foi pedido, nada além.** O escopo da resposta é o escopo do pedido. Um pedido de
correção pontual não vira reescrita de seção; um comando pedido não vira guia com variantes e
diagnóstico preventivo.

> **Não confundir com os artefatos.** PRD, FEAT, TEST e TASK têm o conteúdo que a estrutura exige —
> a regra é contra **inflar além do pedido**, não contra preencher a peça.

Sinais de inflação: variante que ninguém pediu · diagnóstico de erro que não aconteceu · repetir o
que já está em outro documento · recapitular o que já é visível. Achado relevante fora do escopo
entra como **uma linha**, não como implementação.

**Em dúvida de contexto, pergunte antes de responder** — escopo, destino do artefato, ou
alternativas mutuamente exclusivas. **Pergunta *ou/ou* respondida com "sim" não decidiu nada:**
pergunte de novo nomeando as opções, em vez de escolher por suposição. Não pergunte o que dá para
verificar lendo o repositório ou executando.

Esta skill orquestra o fluxo de Spec-Driven Development em fases; o mapa abaixo diz o comando de cada uma.

## Mapa de Fases

| Fase | Descrição | Comandos |
|------|-----------|----------|
| 0 | Workspace Bootstrap — cria estrutura, `.states`, `.logs` | `/bks-sdd` |
| 1 | PRD de Workspace — gera `PRD.md` a partir do `\research` | `/bks-sdd --prd` |
| 1.5 | Session Management — snapshots de estado, continuidade, limpeza | `--continue`, `--tan`, `--clear` |
| 2 | Projetos Internos — cria `\project-[nome]` com estrutura RPI | `/bks-sdd --project` |
| 3 | PRD de Projeto — gera `PRD-[nome].md` por projeto | `/bks-sdd --project-prd` |
| 4 | Plano Macro — gera `PLAN-[nome].md` orientando specs | `/bks-sdd --project-plan` |
| **5** | **Feature Specs — ciclo completo de especificação por feature** | `--feature-list` |
| 5.1 | Spec — gera `FEAT-[nome].md` a partir do plano | `--feature` |
| 5.2 | Test Scenarios — gera `TEST-[nome].md` após FEAT aprovado | `--feature-tests`, `--feature-tests-list` |
| 5.3 | Tasks — gera `TASK-[id].md` após TEST aprovado | `--feature-task` |
| **6** | **Implementação** — execução das tasks; orquestração, verificação e progresso | `--impl-init`, `--task-run`, `--task-done`, `--task-list`, `--status` |
| **7** | **Custo & Telemetria** — consumo de tokens e custo por sessão e do processo inteiro | `--cost`, `--cost-report` |

---

## Referências por fase

Ler a referência **quando a fase pedir**, não antes. As regras que não podem faltar estão neste
corpo; a referência traz modelo de arquivo, mensagem ao usuário e detalhe de comando.

| Fase | Referência |
|---|---|
| 0, 2 | `references/workspace-structure.md`, `references/project-structure.md`, `references/workspace-templates.md` (conteúdo inicial dos arquivos e formato do log de cada comando) |
| 1, 3 | `references/prd-structure.md`, `references/input-sources.md` |
| 1.5 | `references/session-management.md` |
| 4 | `references/plan-structure.md` |
| 5 | `references/feature-spec-structure.md`, `references/test-spec-structure.md`, `references/task-spec-structure.md`, `references/feature-cycle.md` |
| 6 | `references/implementation-phase.md` |
| 7 | `references/cost-telemetry.md` |
| arquitetura | `references/ddd-bounded-contexts-guidelines.md`, `references/ddd-tactic-guidelines.md`, `references/hexagonal-arch-guidelines.md`, `references/txc-guidelines.md` |

**Log e estado, em toda fase que gera artefato:** ao concluir, acrescentar a entrada no
`.logs/session-[data].md` (formato em `workspace-templates.md`) e criar o snapshot em
`.states/state-[YYYY-MM-DDTHH-MM].md`.

**Projeto em foco, em toda fase de projeto:** um projeto em `projects/` → usar sem perguntar;
mais de um → listar e perguntar qual.

---

## Fase 0 — Workspace Bootstrap

**Quando:** `/bks-sdd` sem argumento, ou o usuário quer iniciar um workspace.

1. **Workspace existente.** Se houver `workspace-*` no diretório atual, não criar outro: avisar
   *"Encontrei um workspace existente: `workspace-[nome]`. Não criarei um novo."* e seguir o fluxo
   do `--continue` (Fase 1.5).
2. **Pedir o nome.** Perguntar:

   > **Qual o nome do seu workspace?**
   >
   > *O workspace é o ambiente raiz do seu projeto macro. Na raiz da sua pasta será criado um folder `workspace-[nome]` com a estrutura para Spec-Driven Development: pesquisa, projetos internos, planos e specs. Não apague os folders internos — cada um tem um papel. `/help-workspace` explica cada pasta.*

   **Não prosseguir sem o nome.** Não deduzir o nome do diretório atual nem inventar um.
3. **Confirmar antes de criar.** Mostrar a estrutura e pedir confirmação explícita:

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

   **Não criar nada sem confirmação** ("sim", "pode criar", "confirmo" ou equivalente). A resposta
   para aqui e espera o usuário.
4. **Criar.** Após a confirmação, criar a estrutura com o conteúdo inicial de
   `references/workspace-templates.md`. O papel de cada folder está em
   `references/workspace-structure.md`.
5. **Comunicar.** Dizer que o workspace foi criado e os próximos passos: arquivos de pesquisa
   (`.pdf`, `.md`, `.txt`) em `research/`, links em `research/links.md`, depois `/bks-sdd --prd`.
   Comandos de sessão: `--continue`, `--tan`, `--clear`, `/help-workspace`.

---

## Fase 1 — PRD de Workspace

**Quando:** `/bks-sdd --prd`, ou pedido de PRD em qualquer forma ("gera o PRD", "PRD com os
arquivos da pasta", "tem um links.md com referências").

**Pré-requisito:** workspace ativo. Sem ele: *"Não encontrei um workspace ativo. Execute
`/bks-sdd` para criar um antes de gerar o PRD."*

### 1.1 — Coletar inputs

Ler todos os `.pdf`, `.md` e `.txt` de `workspace-[nome]/research/`, sem pular nenhum. Se houver
`research/links.md`, para cada URL:
1. YouTube (`youtube.com`, `youtu.be`): `TranscriptAPI.get_youtube_transcript` e usar a transcrição
2. demais: `WebFetch` e extrair o relevante
3. URL que falha: registrar no log e seguir — não bloqueia a geração

Somar o contexto que o usuário declarou na sessão. Sem arquivo nem link: *"Não encontrei arquivos
ou links.md em `research/`. Pode descrever o produto/projeto aqui diretamente?"*

### 1.2 — Esclarecer antes de escrever

**Lacuna crítica se pergunta; não se preenche com suposição.** Se o material não diz qual problema
resolve e para quem, qual a métrica primária de sucesso, ou quais restrições técnicas e de negócio
existem, perguntar antes de escrever qualquer seção.

- `AskUserQuestion`, no máximo **3 perguntas por rodada**, objetivas e agrupadas
- não perguntar o que os arquivos de input já respondem
- **não entregar PRD inventando** público-alvo, métrica, requisito não funcional ou escopo que o
  usuário não deu

### 1.3 — Gerar o PRD

Seguir exatamente `references/prd-structure.md`. Salvar em `workspace-[nome]/research/PRD.md`.
Tom claro e preciso, sem enchimento. Fontes no §13 conforme `references/input-sources.md`.

### 1.4 — Checkpoint de revisão

Conferir, sem imprimir o checklist, e sinalizar só os gaps:
1. escopo e intenção delimitados
2. critérios de aceite testáveis
3. limites de arquitetura e restrições explícitos
4. trabalho dividido em fases
5. fontes vinculadas

Dimensão crítica sem resposta vai para `## Questões em Aberto` no fim do `PRD.md`.

### 1.5 — Fechar

Log e estado. Orientar: revisar o `PRD.md`; depois `/bks-sdd --tan` para encerrar ou
`/bks-sdd --project` para criar projetos internos.

**Output:** `workspace-[nome]/research/PRD.md`, em PT-BR.

---

## Fase 1.5 — Session Management

Comandos transversais, válidos em qualquer fase. Detalhe e formato do arquivo de estado em
`references/session-management.md`.

| Comando | O que faz |
|---|---|
| `--continue` | lê o estado mais recente em `.states/`, mostra fase, último passo, próximo passo e custo acumulado (`session_cost.py report --json`), e **espera confirmação antes de retomar** |
| `--tan` | pede confirmação, grava `state-final-[timestamp].md`, fecha o log e **registra e exibe o consumo da sessão** (Fase 7) — nunca pular |
| `--clear` | igual ao `--tan`, inclusive o consumo: o usuário não perde estado nem custo ao limpar a conversa |
| `/help-workspace` | explica cada folder a partir de `references/workspace-structure.md` |

**Snapshot automático:** antes de operação longa (PRD, criação de projeto) e quando a conversa
passa de umas 20 trocas.

---

## Fase 2 — Projetos Internos

**Quando:** `/bks-sdd --project`, ou "cria um projeto", "novo projeto chamado X".

**Pré-requisito:** workspace ativo; sem ele, sugerir `/bks-sdd`.

1. **Nome e stack.** Perguntar o nome; um projeto é um escopo delimitado do workspace, com
   Research → Plan → Implement próprios. Depois, os campos que a Fase 6 herda:
   - **Framework:** `1` .NET · `2` Spring (Java/Kotlin) · `3` TypeScript (Node.js) · `4` Go · `5` outro
   - **Banco principal:** `1` PostgreSQL · `2` SQL Server · `3` MongoDB · `4` MySQL · `5` Redis · `6` nenhum
   - **Mensageria:** `1` Kafka · `2` RabbitMQ · `3` Google Pub/Sub · `4` nenhuma
   - **Se TypeScript**, antes de seguir: tipo de backend — `1` Express · `2` Fastify · `3` LangGraph
     · `4` Worker (BullMQ/pg-boss) · `5` Consumer (RabbitMQ/Kafka)

   "Ainda não sei" vira `A definir`, atualizável antes do `--impl-init`.
2. **Projeto existente.** Se `projects/project-[nome]/` já existe, perguntar se abre e continua; se
   não, pedir outro nome.
3. **Confirmar antes de criar.** Mostrar a estrutura e esperar confirmação explícita:

   ```
   project-[nome]/
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
4. **Criar** com o conteúdo de `references/workspace-templates.md`. `research/stack.md` é a fonte
   de verdade da stack. Papel dos folders em `references/project-structure.md`.
5. **Fechar.** Log e estado. Próximos passos: pesquisa em `project-[nome]/research/`, depois
   `/bks-sdd --project-prd`; o `--project-plan` exige PRD aprovado.

---

## Fase 3 — PRD de Projeto

**Quando:** `/bks-sdd --project-prd`, ou "PRD do projeto X".

**Pré-requisito:** workspace ativo e projeto em foco.

1. **Inputs.** Mesmo procedimento do 1.1, sobre `project-[nome]/research/`. O `PRD.md` do workspace,
   se existir, entra como contexto macro: o PRD do projeto é coerente com ele.
2. **Esclarecer.** Mesma regra do 1.2 — até 3 perguntas por rodada, sem repetir o que o PRD do
   workspace ou os arquivos respondem. Lacunas típicas: escopo dentro do workspace, critério de
   sucesso do projeto, dependência de outro projeto.
3. **Gerar** seguindo `references/prd-structure.md`, adaptado ao projeto:
   - §1 o escopo dentro do workspace, não o problema macro
   - §4 o que é deste projeto e o que é de outro
   - §8 integrações com outros projetos
   - §9 fases que mapeiam direto para as features da Fase 5

   **Arquitetura no §8.** Com DDD ou Hexagonal, ler antes `ddd-bounded-contexts-guidelines.md`
   (contextos, subdomínios, Context Map), `ddd-tactic-guidelines.md` (agregados, eventos) e
   `hexagonal-arch-guidelines.md` (portas e adapters).

   **Com `txc` no `.bks-profile.json`, em qualquer stack, `txc-guidelines.md` é obrigatório.** O §8
   usa o template TXC-aware (§8a–§8d de `prd-structure.md`). A Primary Port é a sessão (em Go, o
   `txc.Op` de cada transação). O contrato é o catálogo de códigos de transação por BoundedContext
   no §8b — nunca `I{Entidade}Handler` nem `ICreateXxxUseCase`. Secondary Ports são por agregado,
   não um `IDBRepositoryPort` genérico. Decisão ainda não validada entra como assunção explícita.

   Salvar em `project-[nome]/research/PRD-[nome].md`; fontes no §13 conforme `input-sources.md`.
4. **Checkpoint** como no 1.4, conferindo também as dependências com outros projetos e o vínculo
   com o PRD do workspace.
5. **Fechar.** Log e estado. Orientar: revisar e, aprovado, `/bks-sdd --project-plan`.

**Output:** `project-[nome]/research/PRD-[nome].md`, em PT-BR.

---

## Fase 4 — Plano Macro do Projeto

**Quando:** `/bks-sdd --project-plan`, ou "plano do projeto X".

**Pré-requisito:** projeto em foco com `PRD-[nome].md`. Sem ele: *"Não encontrei o PRD do projeto
`project-[nome]`. Execute `/bks-sdd --project-prd` antes de gerar o plano."*

1. **Ler o PRD inteiro**, com atenção a §9 (fases), §5 (requisitos), §10 (critérios de aceite) e
   §12 (questões abertas); o PRD do workspace, se houver, para o alinhamento.
2. **Questões abertas que afetam o plano:** mostrar as mais críticas e perguntar se resolve agora
   ou gera com as assunções documentadas. Esperar a resposta.
3. **Gerar** seguindo `references/plan-structure.md`. Com DDD ou Hexagonal no §8 do PRD, ler as
   guidelines de arquitetura antes de mapear as features: cada feature já sai associada ao seu
   contexto delimitado e às portas e adapters que vai criar. Salvar em
   `project-[nome]/plan/PLAN-[nome].md`.
4. **Checkpoint de coerência:** toda fase do §9 coberta; todo requisito P0 do §5 com feature; as
   dependências do §8 nas dependências externas; as questões do §12 documentadas. Lacuna vai para
   o §6 do plano.
5. **Fechar.** Log e estado. Orientar: revisar prioridades e questões; aprovado, as features entram
   na Fase 5.

**Output:** `project-[nome]/plan/PLAN-[nome].md`, em PT-BR.

---

## Fase 5 — Feature Specs

Cada feature passa por **5.1 Spec → 5.2 Test Scenarios → 5.3 Tasks**, nesta ordem. Nenhuma
sub-fase se pula; cada artefato desbloqueia o seguinte. Listagens (`--feature-list`,
`--feature-tests-list`), mensagens de revisão e o fluxo completo estão em
`references/feature-cycle.md`.

**Pré-requisito:** `PLAN-[nome].md` aprovado e **arquitetura aprovada** — índice ARCH e modelos em
`docs/library/architecture/`, pelo `/bkhar:arch`. Nenhuma FEAT começa sem ela.

**Uma feature por vez**, em cada sub-fase: gerar → revisar → aprovar → próxima. Nunca todas de uma
vez. Todo artefato nasce `Draft` e só vira `Aprovada` quando o usuário aprova.

### 5.1 — Spec (`--feature`)

1. **Escolher.** Listar as features do §3 do PLAN sem `FEAT` em `spec/features/` e sugerir a P0
   mais alta. Dependência de feature ainda sem spec: avisar que gera em Draft com a dependência
   registrada e esperar confirmação.
2. **Padrão de implementação** — obrigatório em .NET, TypeScript e Go. O padrão é do projeto, não
   da feature; TXC e padrão direto não se misturam (`decisions/ADR-016`). Pelo campo `txc` do
   `.bks-profile.json`:

   | `txc` | Padrão | O que cada operação vira |
   |---|---|---|
   | `"base"` ou `"motor"` | TXC | uma transação por código: escrita → executor transacional; leitura → executor de consulta (`txc-guidelines.md`, Seção 3) |
   | ausente | padrão direto | serviço da aplicação com contrato Input/Output, sem sessão nem executores |

   Sem `.bks-profile.json`, perguntar antes. O campo `**Padrão de implementação:**` do FEAT é
   obrigatório: o executor depende dele.
3. **Gerar** `spec/features/FEAT-[nome].md` pelo `feature-spec-structure.md`, a partir da linha da
   feature no PLAN e dos requisitos do PRD. Com DDD ou Hexagonal, o §4 Restrições Técnicas já traz
   o agregado raiz, os eventos publicados e as portas necessárias (`ddd-tactic-guidelines.md`,
   `hexagonal-arch-guidelines.md`). **Feature TXC: `txc-guidelines.md` é obrigatório antes do §5**
   — Seção 3 para escolher o executor, Seção 6 para uma ficha da transação por código. Padrão
   direto: contrato Input/Output. §6 Tasks fica vazio; §7 rastreia PLAN e PRD.
4. **Aprovar.** Pedir revisão de §2 (critérios binários), §3 (bordas do domínio), §4 e §5 (na ficha
   TXC, o que o `ValidateAsync` lê, a regra e a compensação). Aprovado, `Status: Aprovada`.

### 5.2 — Test Scenarios (`--feature-tests`)

**Só com FEAT `Aprovada`.** O TEST vem depois do FEAT e antes das tasks — a ordem é estrutural.

1. **Escolher** entre as FEATs aprovadas sem `spec/tests/TEST-[mesmo-nome].md`.
2. **Ler o FEAT:** §2 vira Cenários Principais (1:1 no mínimo), §3 vira Cenários de Borda (cada
   linha, pelo menos um caso), §4 vira Pré-condições de Ambiente. Com portas e adapters no §4,
   incluir borda de `Concorrência` (vários agregados) e de `Resiliência` (cada adapter externo).
3. **Gerar** `spec/tests/TEST-[nome].md`, mesmo nome do FEAT, pelo `test-spec-structure.md`: §4
   Fora de Escopo com pelo menos uma linha (ou *"Nenhum caso identificado como fora de escopo para
   esta feature."*); §6 rastreia FEAT e PLAN.

   Gherkin: `Given` é estado antes, nunca a ação; `When` é uma ação só; `Then` é estado depois, não
   processo; sem `if` ou `or` — separar em cenários; sem `But`.
4. **Aprovar.** Conferir se cada critério e cada borda do FEAT têm cenário, e se há caso que outro
   agente implementaria por engano. Aprovado, `Status: Aprovada`.

### 5.3 — Tasks (`--feature-task`)

Em projeto `bkhar`, as tasks saem pelo `/bkhar:tasks`: uma task por peça, com o RED escrito no
passo 0 do `/bkhar:loop`. Os passos abaixo valem para o workspace avulso.

**Bloqueio TDD: só com TEST `Aprovada`.** TEST em Draft ou ausente: parar e orientar
`--feature-tests`. Não gerar task sem TEST aprovado.

1. **Escolher** entre as FEATs aprovadas, com TEST aprovado e §6 vazio.
2. **Ler** FEAT (§2 a §5 e o padrão), TEST (§2 e §3) e `task-spec-structure.md`. O TEST é a fonte
   da definição de pronto: ao fim das tasks, todo cenário está coberto.
3. **Decompor.**

   **Padrão TXC** — um par Teste + Implementação por peça da ficha, nesta ordem:
   - `[10]` validação da entrada, sem I/O (se a ficha tiver)
   - `ValidateAsync` — leitura pelas Secondary Ports, devolve `TValidation`
   - `ApplyRule` — a regra de negócio, devolve `TDecision`
   - `ExecuteAsync` — gravação pela Port, e `CancelAsync` se a ficha declara compensação
   - `[50]`, se a ficha tiver
   - registro do código e adapter de entrada chamando a sessão, com o replay da `[20]` coberto

   Em Go, os passos do `txc.Steps`: `Check` (`[10]`), `Validate`, `ApplyRule`, `Execute` e `Cancel`;
   o registro é o construtor do `txc.Op`, e o adapter chama o `Op`. Executor de consulta: um par só
   para o `ExecuteAsync`, mais o do registro e adapter. Cada task declara a `**Peça TXC alvo:**`.
   Sinal de alerta: `ValidateAsync` que não lê nada e `ApplyRule` que só repassa → é consulta.

   **Padrão direto:** `**Peça TXC alvo:** n/a`; setup → testes RED → implementação GREEN →
   integração.

   **Sempre:** uma instrução atômica por task (um verbo); Teste e Implementação em par, a de
   implementação dependendo da de teste.
4. **Gerar** `spec/tasks/TASK-[id]-[descrição].md` pelo template, com `**Test Spec:**`,
   `**Feature:**`, `**Padrão:**`, `**Peça TXC alvo:**`, a definição de pronto (abaixo) e o
   `**Agente:**`:
   - `Teste` (RED) → `validador` — o `tester`, que escreve o RED antes do código
   - `Implementação` (GREEN), `Setup` e `Infra` → `implementador`
   - validação ou revisão de critérios → `validador`
   - coordenação entre features → `orquestrador`
   - em dúvida → `implementador`
5. **Atualizar o FEAT:** tabela do §6 com as tasks (modelo em `feature-cycle.md`) e
   `Status: Em execução`. Log e estado.

### Definição de pronto — entra em toda task

Regra que não entra na DoD não é executada; por isso ela nasce na geração da task, não só na
conferência.

- Padrão TXC: `[ ] Dado entre passos por retorno tipado; TXC e envelope sem mutação`
- Toda task que cria ou altera tipo público, função pública ou decisão estrutural:
  - `[ ] README.md e ARCHITECTURE.md atualizados com o que esta task produziu`
  - `[ ] Comentários seguem a convenção: contrato e guarda no código; decisão no ARCHITECTURE.md`
  - `[ ] Documentação tocada segue a skill bks-writing — writing_guard.py sem achado nos arquivos`

**Task sem `README.md` e `ARCHITECTURE.md` atualizados não está concluída** — mesmo peso do build
e dos testes. Ausente ou desatualizado: gerar ou atualizar antes de fechar, sem perguntar.
`README.md`: o que é, como rodar, estrutura de um nível, stack, links — nunca ADR nem detalhe
classe a classe. `ARCHITECTURE.md`: índice, camadas, ADRs curtos (linka `decisions/`) e o
dicionário dos tipos criados ou alterados.

Convenção de comentário no código produzido:
- **fica:** resumo de 1 linha em membro público e guarda contra regressão de até 2 linhas;
  como exceção, até 2 linhas, gotcha não óbvio e ausência deliberada de código
- **sai:** decisão, trade-off, histórico — vivem no `ARCHITECTURE.md`
- **proibido:** marca de severidade em comentário; **bloco acima de 5 linhas**

Regra sem guarda executável é intenção: onde a stack permitir, a convenção vira teste de
arquitetura no projeto (referência: `CommentBudgetTests` no `nq-sec-sdk`).

---

## Fase 6 — Implementação

Executa e verifica as tasks da Fase 5.3. Comandos, modelos de IMPL e OUTPUT, caminhos Agente e
Contexto e edge cases em `references/implementation-phase.md`.

**Pré-condições:** PLAN e arquitetura aprovados; FEAT e TEST aprovados; tasks geradas; stack em
`research/stack.md` (campo `A definir` → perguntar e atualizar o arquivo antes).

| Comando | O que faz |
|---|---|
| `--impl-init` | escolhe a feature com tasks pendentes, lê a stack, mapeia a skill (`.NET` → `bks-dotnet-solutions`, TypeScript → `bks-typescript-solutions`, Go → `bks-go-solutions`), define o modo, gera `IMPL-[feature].md` e inicializa as tasks no `TodoWrite` |
| `--task-run [id]` | confere IMPL e dependências, marca `Em execução` e executa: `--agent` gera o código por subagente isolado em `spec/output/code/[feature]/`; `--context` monta o pacote para execução externa |
| `--task-done [id]` | o sensor: confere os cenários do TEST relevantes à task e a definição de pronto; Agente verifica sozinho e tenta autocorreção, Contexto passa o checklist ao usuário |
| `--status`, `--task-list` | painel do workspace e tabela de tasks de uma feature |

**Bloqueios:** `--task-run` sem `--impl-init`, ou com dependência não concluída; `--task-done` com
a task fora de `Em execução`; `--impl-init` sem tasks; Modo Agente sem arquivo em `code/`. O
`--continue` na Fase 6 mostra o estado e sugere a próxima task, mas não executa sozinho. FEAT só
vira `Concluída` com todas as tasks concluídas. O workspace nunca substitui o repositório real.

---

## Fase 7 — Custo & Telemetria

Consumo de tokens e custo estimado por sessão e do processo, pelo
`${CLAUDE_PLUGIN_ROOT}/scripts/session_cost.py` sobre o ledger
`workspace-[nome]/.logs/cost-ledger.jsonl`. Comandos, rótulos de fase e a nota no vault em
`references/cost-telemetry.md`.

- **Registro silencioso** ao concluir `--prd`, `--project-prd`, `--project-plan`, `--feature`,
  `--feature-tests`, `--feature-task` e `--task-done`: uma linha com o acumulado no fim da resposta.
- **Registro com a tabela completa** em todo encerramento: `--tan`, `--clear` e `/bkhar:save`.
- `--cost` mostra a sessão sem gravar; `--cost-report` consolida o processo.
- **Conclusão do projeto:** a última etapa do relatório é perguntar se o usuário quer o
  consolidado de consumo, com a ordem de grandeza já na pergunta. Não gerar sem o sim.
- Sempre apresentar como **estimativa**: tokens do transcript vezes a tabela local de preços.
- Script que falha: uma linha e seguir. A telemetria nunca bloqueia o fluxo.
