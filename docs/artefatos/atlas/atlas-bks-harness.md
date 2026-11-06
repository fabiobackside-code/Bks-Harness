# Atlas do BKS Harness — Manual da Equipe de Agentes

Oct 18, 2026 · @Fabio Magalhaes

Versão 1.9.0, revisada contra o `bkhar` 1.0.0. A 1.7.0 ganhou a equipe construída na Fase 3: seis agentes, o Gerente como protocolo da sessão principal, os ritos `/bkhar:ask`, `/bkhar:panel` e `/bkhar:refine`, a revisão em painel e o `LEARNINGS.md`. A 1.7.1 aponta para o manual de treinamento, que ensina a instalar e usar. A 1.7.2 acrescenta o `/bkhar:plan`, que gera o plano macro. A 1.7.3 conta a equipe como sete papéis, seis agentes e o Gerente. A 1.8.0 põe a arquitetura como portão antes da especificação e traz a biblioteca do projeto, com dashboard e exportação para o vault. A 1.9.0 cobre o resto da 1.0.0: os modos `colaborativo` e `autonomo`, a prontidão, as ondas pelo grafo, o painel com inbox, o modelo por papel e o aprendizado candidato com `/bkhar:retro` e `/bkhar:harvest`. O histórico de versões está no Apêndice F.

## Prefácio

Este manual descreve o BKS Harness: uma equipe de sete papéis de IA — seis agentes e o Gerente — que trabalha com você, conversa com você e faz o seu padrão de desenvolvimento crescer a cada projeto. Ele não é uma ferramenta de vibe coding. O código é consequência de conversas, decisões registradas e verificações executadas.

O harness nasce de dois projetos que já existem. O **2brains** (`${BKS_VAULT}`, template público em `bks-2brains`) é o vault: guarda o que atravessa projetos — quem você é (`workbench/`), o que você aprendeu (`knowledge/`) e os projetos em `repos/{backside|w3|private}/`, cada um com git próprio e memória própria. O **BKS kit** (`bks-sdd-kit`, plugin `bks` 0.7.0) é a ferramenta: 17 skills, 12 comandos `/bks:*`, quatro agentes (planner, builder, reviewer, scribe), guardas executáveis em `hooks/`, nove perfis de projeto e 20 casos de eval.

O harness não substitui nenhum dos dois: é o kit evoluído, rebatizado `bkhar`, sobre o mesmo vault. Tudo o que já funciona (comandos, fluxo de pesquisa e código, agentes, guardas, a regra de que cada projeto é autossuficiente) continua valendo. O harness acrescenta a equipe ampliada, os ritos, o ciclo de aprendizado, o ciclo de vida das skills e a independência de modelo.

**Para quem é.** Para você, como arquiteto e dono do padrão. E, mais adiante, para a sua equipe de devs júnior e pleno, que podem trabalhar com os mesmos agentes e o mesmo padrão.

**Como ler.** As Partes I e II explicam o porquê e a estrutura. As Partes III a V são o coração: a equipe, como ela dialoga e como ela aprende. A Parte VI é a referência de comandos. A Parte VII mostra tudo funcionando num case. A Parte VIII diz por onde começar. A Parte IX mostra como o harness evolui com skills novas. A Parte X é o manual de uso: cada comando com para que serve, onde rodar, o passo a passo e um exemplo. Os apêndices trazem templates prontos para copiar e o histórico de versões.

**Convenções.** Docs em PT-BR; código e comandos em inglês, com o prefixo bkhar. Itens marcados como *proposto* ainda não existem e serão construídos ao longo das fases de implantação.

## Parte I — Fundamentos

Um agente confiável é um modelo envolvido por um harness. O modelo raciocina. O harness decide o que ele vê, o que ele pode fazer, quando ele para e quem confere o resultado.

### 1. O problema

Sem estrutura, programar com IA falha de três formas recorrentes:

- **Amnésia.** Não há memória entre sessões. Você reexplica contexto, padrão e decisões a cada conversa.
- **Suposição.** Onde falta fonte de verdade, o modelo preenche com chute. É daí que vem a alucinação de arquitetura.
- **Autoaprovação.** Quem implementa também declara que terminou. Ninguém executa a prova de que funciona.

A resposta não é um prompt melhor. É a estrutura em volta do modelo.

### 2. As cinco responsabilidades do harness

| Responsabilidade | Pergunta que responde | No BKS Harness |
| --- | --- | --- |
| Contexto | O que entra na janela? | Brain via MCP, premissas, specs |
| Ferramentas | O que o agente pode executar? | MCP, shell controlado, gates |
| Fluxo | Em que ordem e com que portões? | Máquina de estados do BKS-SDD |
| Verificação | Quem prova que funcionou? | Gates + revisores independentes |
| Observação | Quanto custou e onde falhou? | Spans OpenTelemetry por agente |

### 3. O vault e o projeto

O **vault** guarda o que atravessa projetos. `workbench/` é o que é seu: `profile.md` (quem você é e como trabalha) e `decisions/` (ADRs sobre o processo, não sobre um projeto). `knowledge/` é o que você aprendeu, no padrão LLM Wiki do Karpathy: fontes imutáveis em `raw/`, páginas curadas em `wiki/{foundations,patterns,architecture,ddd,tdd,sdd,go,...}/`, catálogo em `index.md`, registro em `log.md`. Ela é alimentada pelo `/bkhar:ingest` e consultada com `tools/search.sh`. Regra de ouro: antes de decidir arquitetura ou padrão, consulte a wiki e cite a página; o incerto vira `> [!uncertain]`, nunca chute.

O **projeto** é autossuficiente: abrir o repositório dá acesso a tudo que ele precisa, e nenhum comando de projeto lê o vault para funcionar. Cada um nasce com `STATUS.md` (onde parei, o que trava, próximo passo), `WORKFLOW.md` (o fluxo de comandos deste projeto), `JOURNAL.md` (marcos, do mais recente ao mais antigo), `.bks-profile.json` (perfil e eixos), `brain/domain/` (o que o produto é), `brain/engineering/` (como se constrói aqui), `decisions/`, `specs/{features,tests,tasks}/`, `docs/{input,design,canonical,history}/`, `outputs/` e `app/`. O hub central `brain/_bks-ai/` do template público foi abandonado: um projeto só funcionava com ele por perto, e ele envelhecia sem que ninguém percebesse.

**Onde uma coisa nova vai.** Sobre você e vale para todo projeto → `workbench/`. Conhecimento geral, de mais de um projeto → `knowledge/`. O que um produto é → `{repo}/brain/domain/`. Como se constrói num projeto → `{repo}/brain/engineering/`. Decisão fechada de um projeto → `{repo}/decisions/`. Ferramenta, template, skill reusável → o plugin, nunca o vault.

### 4. O fluxo do 2brains: da pesquisa ao código

Nenhuma linha de código nasce sem contexto consolidado e spec aprovada. O fluxo tem duas fases.

**Fase pesquisa (sessão na raiz do vault, depois na raiz do projeto):**

1. `/bkhar:brain` na raiz do vault monta o panorama de todos os projetos a partir dos `STATUS.md` e diz qual tem trabalho pronto. Dentro de um projeto, lê só o `STATUS.md` dele.
2. `/bkhar:new-project` (único comando de projeto que roda no vault) cria `repos/{categoria}/{nome}/` com a estrutura canônica e grava o perfil em `.bks-profile.json`. Categorias: `backside`, `w3` e `private`.
3. Você traz o material bruto para `docs/input/` e os rascunhos para `docs/design/`; `/bkhar:note` escreve notas vivas em `docs/input/notas/`.
4. `/bkhar:canonize` consolida tudo em `docs/canonical/CONTEXT.md`, com fontes citadas e `> [!uncertain]` nas divergências. A versão anterior vai para `docs/history/`.
5. `/bkhar:prd` gera `docs/canonical/PRD-{projeto}.md`. Todo requisito rastreia para o CONTEXT.md.

**Fase código (raiz do repo do projeto):**

1. `/bkhar:plan` faz o plano macro e o grafo de tasks a partir do PRD aprovado.
2. `/bkhar:arch` elabora a arquitetura: o índice `docs/library/architecture/ARCH-{projeto}.md` e um modelo por arquivo (C4, dados, sequências, fronteiras sensíveis, implantação), desenhados pela `bks-arch` no renderer do perfil. É portão: sem ARCH e modelos aprovados, nenhuma FEAT começa, no `colaborativo` e no `autonomo`.
3. `/bkhar:refine` (ou `/bkhar:spec`, sem rito) gera `specs/features/FEAT-*.md` apoiada nos modelos; depois de aprovada, o `TEST`. A partir daqui, a spec só cita `docs/canonical/` e a arquitetura aprovada.
4. `/bkhar:loop` implementa sob LOOP-4, com os guardas de `hooks/` recusando escrita fora do padrão.
5. `/bkhar:review` dispara o reviewer em invocação separada e read-only; `/bkhar:maintainability` dá o parecer de manutenibilidade por aplicação de `app/`.
6. `/bkhar:save` fecha a sessão: decisões em `decisions/`, specs em `specs/`, `STATUS.md` reescrito, marco no `JOURNAL.md`, alerta quando o canônico ou um modelo da arquitetura ficou mais velho que as decisões, e regera a biblioteca do projeto.

**A biblioteca do projeto.** `docs/library/` é a wiki do projeto: o catálogo `LIBRARY.md` lista, por referência, canônicos, arquitetura, contratos, specs, decisões, ilustrações e histórico, e o dashboard `site/index.html` apresenta tudo com os diagramas renderizados e a linha do tempo. Os modelos são vivos: o `scripts/library.py stale` aponta o que ficou para trás e o `/bkhar:arch --update` refaz. O `/bkhar:library export` leva a biblioteca para `knowledge/wiki/projetos/{projeto}/` do vault, com o filtro de dado sensível do harvest.

&#91;embedded content: fluxo do 2brains · fase pesquisa e fase código\]

O `/bkhar:canonize` é o ponto em que o entendimento vira fonte única: a partir do PRD, a spec só cita `docs/canonical/`. Quando uma decisão posterior contradiz o canônico, o `/bkhar:save` detecta e avisa.

**Dois caminhos para a spec.** O `/bkhar:spec` é o caminho enxuto, e é o que todos os projetos em curso usam hoje. A skill `bks-sdd` é o caminho completo, com workspace, PLAN, TASKs em pares RED/GREEN e memória de sessão em `.states/`, para produto grande ou escopo incerto. Nos dois, as specs moram em `{repo}/specs/`.

### 5. LOOP-4

Cada task tem no máximo quatro tentativas. A cada rodada, o `/bkhar:loop` executa `dotnet build` e `dotnet test` e audita quatro goals: **G1** build sem erro e sem warning novo, **G2** testes 100% verdes, **G3** cenários do TEST cobertos e **G4** código fiel ao `brain/engineering/` do projeto (calisthenics e hexagonal). Quando um goal falha, o erro real volta como contexto da próxima tentativa. Na quarta falha, o loop para e gera `outputs/BLOQUEIO-[task].md` para você decidir. Quinta tentativa, relaxar o goal ou marcar como concluído são proibidos. No harness, G3 e G4 passam a ser conferidos também por execução (testes de arquitetura), não só auditados pelo modelo.

&#91;embedded content: LOOP-4 · tentativa, gates, revisão ou decisão humana\]

A falha nunca é escondida: ou ela volta como contexto da próxima tentativa, ou chega até você.

### 6. Gates

Gate é uma verificação que a máquina executa, não uma opinião do modelo. O kit já tem cinco guardas em `hooks/`, cada um com teste: `no_dispatcher` recusa MediatR e equivalentes, `comment_budget` recusa comentário acima de cinco linhas, `dod_docs` recusa tipo público novo sem `README.md` e `ARCHITECTURE.md` tocados na mesma leva, `writing_guard` confere o padrão de escrita e `session_memory` carrega o `STATUS.md` ao abrir a sessão. Os três primeiros recusam, não avisam. O harness acrescenta testes de arquitetura com NetArchTest ou ArchUnitNET (a camada Domain não referencia Dapper, por exemplo), lint e análise estática. Pronto significa gates verdes **e** revisão independente aprovada.

## Parte II — Arquitetura

O harness é hexagonal: o núcleo não sabe qual modelo, qual vault ou qual ferramenta de teste está do outro lado. Trocar o Claude pelo DeepSeek é escrever um adapter, sem tocar no core. É o mesmo padrão que você cobra da sua equipe.

### 7. As três camadas

- **Entrada (driving adapters):** C`laude Code com o plugin bkhar, servidor MCP, pipeline de` CI.
- **Core:** domínio (`Phase`, `Feat`, `Task`, `LoopAttempt`, `Gate`, `AgentTurn`, `Proposal`), pipeline com TXC e Result Pattern. Sem dependência de fornecedor.
- **Saída (driven adapters):** Anthropic, DeepSeek, Ollama local, vault 2brains, `dotnet test` e NetArchTest, OpenTelemetry.

As portas do core: `LlmProvider`, `KnowledgeStore`, `ToolHost`, `GateRunner`, `PolicyEngine`, `Telemetry` e `ConversationStore` (o histórico de diálogo entre você e a equipe).

&#91;embedded content: arquitetura hexagonal · entrada, core e saída\]

Trocar um fornecedor muda só a coluna da direita; o core e as portas ficam iguais.

### 8. Componentes

| Componente | Responsabilidade | Origem |
| --- | --- | --- |
| Plugin `bkhar` | Empacota skills, comandos, agentes, guardas, perfis e templates; uma instalação no escopo do usuário | Existe como plugin `bks` 0.7.0; renomeado na Fase 1 |
| Team orchestrator | Conduz os ritos, dá a vez a cada agente, consolida e cobra suas decisões | Existe (0.9.0): skill `bks-team`, seguida pela sessão principal |
| Agent registry | Os sete perfis com persona, limites, modelo e fontes | Existe (0.9.0): seis agentes em `agents/`; o Gerente é a skill `bks-team` |
| Skill registry | Cataloga as skills, versões e estágio de cada uma | Evolui `skills/` do kit (17 skills) |
| Perfis de projeto | Dizem quais fases, artefatos e skills se aplicam | Existe: nove perfis + eixos em `.bks-profile.json` |
| Orquestrador SDD | Fases e portões; impede pular etapa | Existe nos comandos `/bkhar:*`; no `autonomo`, `/bkhar:loop --wave` executa o grafo e `scripts/readiness.py` concede o modo |
| Estado da execução | Uma task por arquivo, com tentativas, worktree e custo; um escritor só | Existe (1.0.0): `outputs/run/`, escrito por `scripts/run_state.py` |
| Painel local | Acompanha ondas, tentativas, bloqueios e consumo; recebe sua interação | Existe (1.0.0): `scripts/dashboard.py` em `127.0.0.1`, escreve só em `outputs/run/inbox/` |
| Biblioteca do projeto | Catálogo, dashboard e exportação dos artefatos do projeto | Existe (1.0.0): `docs/library/`, gerada por `scripts/library.py` |
| Gate runner | Build, testes, regras de arquitetura e guardas | Evolui `hooks/` e o LOOP-4 do `/bkhar:loop` |
| Model router | Escolhe o modelo por agente e por zona | Parcial (1.0.0): modelo no frontmatter do agente, sobrescrito pelo mapa `models` do `.bks-profile.json`; por zona, na Fase 4 |
| Policy engine | Bloqueia zona sensível para provedor não aprovado | Novo, lê o manifesto `.claude/multiagente.md` |
| Proposal inbox | Recebe o que os agentes aprenderam, para sua curadoria | Existe (1.0.0): `inbox/proposals/` pelo `scripts/learning.py`; `/bkhar:retro` promove ou arquiva em `archive/` |
| Telemetry | Custo e uso por agente, modelo, skill e fase | Evolui `session_cost.py`, `--cost-report` e `.logs/custo-tokens.md` |
| Eval suite | Compara modelos e versões de skill com delta with × without | Existe: 20 casos, `claude plugin eval .`, suíte estrutural sem modelo |

### 9. Roteamento de modelos

Cada agente tem um modelo preferido, declarado em `routing.yaml`. Três regras guiam a escolha:

1. **Quem decide usa o modelo mais forte.** Arquiteto e Gerente erram caro; tokens são baratos perto disso.
2. **Quem executa pode usar o mais barato.** O Dev é protegido pelos gates.
3. **Quem revisa usa outro fornecedor.** Testes e Segurança rodam num fornecedor diferente do Dev, porque modelos diferentes erram de formas menos correlacionadas. É segregação de função de verdade.

**O que existe na 1.0.0.** O padrão de cada papel está no frontmatter do agente: Opus para `architect` e `security`, Sonnet para `developer`, `tester` e `quality`, Haiku para o `scribe`. O mapa `models` do `.bks-profile.json` sobrescreve por projeto, e o Gerente passa o modelo em cada chamada. O painel troca o modelo de um papel por pedido na inbox. O roteamento por fornecedor e por zona continua para a Fase 4.

### 10. Política de dados

Cada projeto declara em `.bks-profile.json` o perfil e o eixo `rigor` (`producao` ou `poc`). Projeto com área sensível ganha um manifesto em `{repo}/.claude/multiagente.md`, a partir do template `manifesto-projeto.md` do kit — hoje `nquantic` e `poc-sec-sdk` têm um. O manifesto traz: comandos de verificação, zonas de contenção (arquivos que só a sessão principal edita, como `Program.cs` e migrations), recursos numerados compartilhados, zonas paralelizáveis, áreas sensíveis que exigem `/bkhar:review` e invariantes do domínio. O policy engine do harness lê esse mesmo manifesto antes de cada chamada e troca o provedor quando a área exige. Em contexto bancário, sob BACEN e LGPD, isso não pode depender de lembrar.

A API hospedada do DeepSeek armazena dados fora do Brasil. Por isso, zonas sensíveis só usam provedor aprovado ou pesos abertos rodando localmente (Ollama ou vLLM). Segredos nunca entram no contexto: o harness só referencia o cofre CyberArk.

## Parte III — A Equipe

A equipe tem sete papéis — seis agentes e o Gerente —, e cada um tem uma função, um limite e um conjunto de perguntas que sempre faz. Nenhum agente decide por você: eles aconselham, questionam e executam, mas a decisão é sua e fica registrada.

### 11. Visão geral

&#91;embedded content: a equipe · 6 agentes e o Gerente em 3 grupos\]

Quem revisa nunca é quem constrói, e quem decide é sempre você.

| Agente | Tipo (PBQ) | Papel | Pergunta que sempre faz | Modelo hoje / sugerido | Vem de (kit) |
| --- | --- | --- | --- | --- | --- |
| Gerente | Orquestrador | Conduz os ritos, consolida opiniões, cobra decisões | O que está pendente de decisão sua? | a sessão principal | Novo: skill `bks-team` |
| Arquiteto | Consultivo | Bounded contexts, padrões, ADRs, fitness functions | Isso respeita o padrão ou pede exceção? | Opus | `planner` (FEAT, TASK) + `/bks:arch` |
| Dev | Implementador | Implementa e explica cada escolha | Qual alternativa descartei, e por quê? | Sonnet | `builder` + `/bks:loop` |
| Testes | Validador | Cenários, casos de borda, TDD RED/GREEN | Qual cenário prova que isso está errado? | Sonnet → outro fornecedor | `planner` (TEST) + skill `bks-tests` |
| Segurança | Validador | AppSec, LGPD, BACEN, segredos | Que dado sensível passa por aqui? | Opus, read-only | `reviewer` + `/bks:review` + `security-audit` |
| Qualidade | Validador | Clean Code, calisthenics, smells, manutenibilidade | Um júnior entende isso daqui a 6 meses? | Sonnet | Novo (`bks-standards`, `bks-maintainability-review`) |
| Documentador | Consultivo | ADR, C4, STATUS, JOURNAL, registro de aprendizado | O que aprendemos hoje que vale virar padrão? | Haiku | `scribe` + `/bks:save` + `bks-writing` |

No `bkhar` 0.9.0 a equipe existe. Seis papéis são subagentes em `agents/`, com modelo no frontmatter e o tier anunciado na primeira linha: `architect` (Opus), `tester` (Sonnet), `developer` (Sonnet), `security` (Opus, só leitura), `quality` (Sonnet, só leitura) e `scribe` (Haiku). O Gerente é a sessão principal seguindo a skill `bks-team`, porque subagente do Claude Code não conversa com você no meio do trabalho nem chama outro subagente. A equipe evoluiu dos quatro agentes do kit: o planner se dividiu em Arquiteto e Testes, o builder virou Dev, o reviewer virou Segurança, o scribe virou Documentador, e Gerente e Qualidade entraram como papéis novos. O plugin `bks` segue com os quatro antigos nos projetos não migrados. A coluna PBQ diz o tipo do papel no vocabulário da Fase 6 do `bks-sdd`. As regras duras continuam: o Dev não edita zona de contenção nem commita, a Segurança só lê e exige `arquivo:linha`, e o Documentador nunca afirma teste sem evidência.

### 12. Os perfis

**Gerente.** É o mestre de cerimônias. Abre cada rito, decide quem fala, impede que a conversa avance sem uma resposta sua e resume os trade-offs em opções numeradas. Não opina sobre técnica: quando há conflito entre agentes, ele expõe o conflito, não o resolve. No `bkhar`, o Gerente é a sessão principal seguindo a skill `bks-team`. Fontes: PRD, PLAN, `.states`, decisões pendentes.

**Arquiteto.** Guarda o seu padrão: Hexagonal, DDD tático, Pipeline com TXC, Result Pattern, SEDA quando cabe. Toda recomendação cita a regra ou a página da wiki que a sustenta. Quando uma decisão contradiz o padrão, ele exige um ADR. Fontes: skill `bks-standards`, `brain/engineering/` do projeto, `knowledge/wiki/architecture/`, ADRs do projeto, skills `bks-dotnet-solutions`, `bks-typescript-solutions`, `bks-go-solutions` e `bks-arch`.

**Dev.** Implementa as tasks sob LOOP-4. Diferente de um vibe coder, ele explica: qual abordagem escolheu, qual descartou e por quê. Quando a spec é ambígua, ele para e pergunta antes de codificar. Fontes: FEAT, TEST, TASK, skills de stack.

**Testes.** Pensa como quem quer quebrar o sistema. Questiona a FEAT no refinamento (casos de borda, respostas que vazam informação) e escreve os testes RED no passo 0 do `/bkhar:loop`, antes do Dev. Não revisa os próprios testes. A meta é rodar em fornecedor diferente do Dev, a partir da Fase 4. Fontes: TEST, critérios de aceite e os casos do `LEARNINGS.md` da área da task.

**Segurança.** Analisa cada FEAT e cada diff pelo ângulo de dado sensível, autorização, log, segredo e conformidade. Confere mascaramento, uso do CyberArk e se a zona do manifesto foi respeitada. Também roda em fornecedor diferente do Dev. Fontes: manifesto, checklist de segurança, normas aplicáveis.

**Qualidade.** Revisa legibilidade, nomes, tamanho de função, comentários desnecessários e smells, sempre balanceando com custo real de performance. Pensa na sua equipe júnior e pleno como leitora do código. Julga também os testes que o Testes escreveu e os resultados da execução, e devolve o defeito resolvido como caso para o `LEARNINGS.md`. Fontes: bks-clean-code, Object Calisthenics, catálogo de refactoring.

**Documentador.** Transforma decisões em ADR, mantém diagramas C4, atualiza o estado do projeto e grava o ADR de cada painel. Na fase da retrospectiva, ainda proposta, conduz o rito: recolhe o que cada agente aprendeu e transforma em propostas para o seu cérebro. Fontes: tudo o que foi decidido na sessão.

### 13. Regras de convivência

1. **Toda opinião cita uma fonte.** Sua wiki, suas premissas ou uma referência primária. Opinião sem fonte vem marcada como tal.
2. **Ninguém aprova o próprio trabalho.** Quem implementa não revisa.
3. **Conflito é exposto, não escondido.** Se Arquiteto e Dev discordam, você vê as duas posições.
4. **Na dúvida, pergunta.** Um agente que assume em vez de perguntar viola o perfil.
5. **Nada entra no cérebro sem você.** Agentes propõem; você aprova.

Cada perfil declara também as skills que o agente carrega, com a faixa de versão aceita (Parte IX). Competência nova chega por skill, não por reescrita do perfil.

## Parte IV — Ritos e diálogo

A equipe conversa com você em cinco formatos, cada um com começo, meio e fim. Os ritos substituem o "gera isso pra mim" por uma conversa com papéis claros.

| Rito | Quando | Quem participa | Termina com |
| --- | --- | --- | --- |
| Refinamento | Antes de cada FEAT | Gerente, Arquiteto, Testes, Segurança | FEAT aprovada por você |
| Painel | Uma dúvida com mais de uma resposta razoável | Gerente + 2 ou 3 agentes | Sua decisão, registrada em ADR |
| Pergunta direta | A qualquer momento | Um agente | Resposta com fonte |
| Revisão em painel | Depois de gates verdes | Testes, Segurança, Qualidade, Arquiteto | Aprovação ou novas tasks |
| Retrospectiva | Ao fim de cada FEAT | Todos, conduzidos pelo Documentador | Propostas para o cérebro |

Quatro ritos têm comando desde a 0.9.0: `/bkhar:refine`, `/bkhar:panel`, `/bkhar:ask` e `/bkhar:review`. A retrospectiva é proposta. Nenhum rito grava `STATUS.md` nem `JOURNAL.md`: no fim, o Gerente lista o que o `/bkhar:save` grava. A exceção é o ADR do painel, que o Documentador grava logo depois da sua escolha.

### 14. Refinamento

O Gerente apresenta o pedido. Cada agente faz até três perguntas pelo seu ângulo. O Gerente agrupa as perguntas, você responde, e só então o Arquiteto e o Testes escrevem FEAT e TEST com as suas respostas dentro. Uma FEAT que nasce sem refinamento, pelo `/bkhar:spec`, é exceção registrada no cabeçalho: `Refinamento: não (exceção)`.

### 15. Painel

Você faz uma pergunta aberta ("CQRS ou leitura direta aqui?"). Dois ou três agentes respondem de forma independente, sem ver a resposta um do outro. O Gerente apresenta as posições lado a lado, com prós, contras e fontes, numeradas como opções. Você escolhe, e o Documentador registra a decisão em ADR, com as opções descartadas.

### 16. Pergunta direta

Use `/bkhar:ask <agente> <pergunta>` para falar com um papel específico: `/bkhar:ask seguranca preciso mascarar esse campo no log?` O nome vale em inglês ou português. A resposta segue o perfil: cita a fonte e diz quando é opinião.

O atalho com arroba, previsto nas primeiras versões deste Atlas, não existe: no Claude Code, a arroba é menção de arquivo.

### 17. Revisão em painel

Depois que os gates passam, três revisores leem o diff em invocações separadas: Testes, Segurança e Qualidade. O Arquiteto entra quando o diff toca uma fronteira de contexto ou uma premissa. O Testes confere se cada cenário está coberto; a força dos testes é julgada pela Qualidade, porque quem escreveu o teste não o revisa. Cada achado vira um de três tipos: bloqueante (proposta de task, escrita depois do seu ok), sugestão (você decide) ou aprendizado. Defeito resolvido, com evidência, vai para o `LEARNINGS.md` do projeto, que o Testes lê antes de escrever teste novo; o resto espera a retrospectiva.

### 18. Retrospectiva

O Documentador pergunta a cada agente: o que funcionou, o que travou, o que vale virar padrão. O resultado não é um relatório, mas propostas candidatas para o seu cérebro (Parte V). Quem decide o destino de cada uma é você, no `/bkhar:retro`.

### 19. O time também te provoca

A equipe não só responde: ela observa o seu padrão e devolve perguntas. Exemplos:

- "Você decidiu isso três vezes sem ADR. Vira premissa?"
- "Essa decisão contradiz a premissa do projeto Split Payment. Qual vale?"
- "Você aceitou leitura direta duas vezes onde a premissa pede CQRS. A premissa está desatualizada?"

É assim que quem evolui é você, e não só o código.

## Parte V — O ciclo de aprendizado

O harness melhora porque o seu cérebro melhora, e o seu cérebro só muda com a sua aprovação. É isso que separa uma equipe que aprende de um modelo que acumula vícios.

### 20. O ciclo em quatro passos

1. **Observar.** Durante os ritos, cada agente anota padrões novos, anti-padrões encontrados, referências citadas e contradições com o padrão. Cada correção sua também conta.
2. **Propor.** O `scripts/learning.py propose` grava a proposta, uma por arquivo, em `inbox/proposals/` do projeto, com `status: candidata`, evidência e origem. O `/bkhar:save` a leva ao `inbox/proposals/` do vault e recusa a que tiver dado pessoal ou segredo.
3. **Curar.** Você revisa as candidatas com `/bkhar:retro`: promove a regra do projeto (`brain/engineering/regras/`), do vault (`workbench/regras/`) ou do kit, que espera eval antes de entrar; ou rejeita, e ela vai para `archive/` com o motivo. Rejeitar também ensina.
4. **Incorporar.** A regra promovida passa a ser lida pelos agentes na próxima sessão, e a prontidão do `autonomo` avisa quando o projeto ainda não tem nenhuma. Na raiz do vault, o `/bkhar:harvest` consolida as decisões de todos os projetos em `knowledge/wiki/experiencia/`, por tema, com ponteiro para o ADR de origem.

&#91;embedded content: ciclo de aprendizado · 4 passos\]

O único passo que exige você é a curadoria; os outros três a equipe faz sozinha. Captura gravada direto como regra está recusada: suspeita viraria fato, e o agente passaria a citá-la.

**O `colaborativo` treina o `autonomo`.** Cada correção que você faz no modo colaborativo vira candidata; promovida e medida, passa a valer quando o projeto roda sozinho.

### 21. Tipos de proposta

| Tipo | Destino ao ser aceita | Exemplo |
| --- | --- | --- |
| Regra de padrão | `skills/bks-standards/` (todo projeto) ou `brain/engineering/` (um projeto) | Máscara de CPF é responsabilidade do domínio |
| Regra de checklist | `skills/bks-team/references/` | Segurança: verificar log em nível Debug |
| Página de conhecimento | `knowledge/wiki/` do vault, via `/bkhar:ingest` | Resumo de um paper citado no painel |
| Template | `templates/` do plugin | Seção "Dados sensíveis" obrigatória na FEAT |
| Guarda | `hooks/scripts/` + teste em `hooks/tests/` | Domain não referencia Dapper |
| Sobre você ou o processo | `workbench/profile.md` ou `workbench/decisions/` | Preferência de revisão, ADR de processo |

### 22. Referências e fundamentos

Quando um agente traz um artigo, um livro ou um paper, ele não fica só na conversa. O Documentador cria uma proposta de ingestão, e ao ser aceita ela passa pelo `/bkhar:ingest` e vira página da wiki com link para a fonte primária. Com o tempo, as decisões passam a citar a **sua** wiki, e não a memória de treinamento do modelo.

### 23. Anatomia de uma proposta

```markdown
---
tipo: premissa
projeto: pix-comprovante
status: candidata
data: 2026-11-04
origem: retro FEAT-comprovante-pix
evidencia: ADR-007; CPF completo em log de Debug
---
# Máscara de CPF na camada de domínio

**O que muda:** CPF passa a ser um value object que só expõe a versão mascarada.
**Por quê:** a Segurança encontrou CPF completo em log de Debug.
**Onde se aplica:** todo projeto com zona de dados pessoais.
```

## Parte VI — Fluxo e comandos

Do escopo ao merge, cada etapa tem um dono, uma saída e um portão. Os portões humanos são os mesmos do bks-sdd de hoje; a diferença é que o harness não deixa avançar sem eles.

### 24. Fluxo de uma feature

| Etapa | Rito | Dono | Saída | Portão |
| --- | --- | --- | --- | --- |
| 1. Contexto da sessão | — | Gerente | `/bkhar:brain`: panorama ou STATUS do projeto | — |
| 2. Projeto | — | Você | `/bkhar:new-project` cria repo e perfil | — |
| 3. Entendimento | Refinamento do escopo | Gerente, Arquiteto | `docs/input/` → `/bkhar:canonize` → `CONTEXT.md` | Perguntas `[!uncertain]` respondidas |
| 4. Requisito | — | Arquiteto | `/bkhar:prd` → `PRD-{projeto}.md` | Sua aprovação |
| 4a. Plano e arquitetura | — | Arquiteto | `/bkhar:plan` → PLAN e grafo; `/bkhar:arch` → ARCH e modelos em `docs/library/architecture/` | Sua aprovação do PLAN, do ARCH e de cada modelo |
| 5. Refinamento da feature | Refinamento | Gerente | Perguntas da equipe, apoiadas nos modelos, e suas respostas | Suas respostas |
| 6. FEAT | — | Arquiteto | FEAT com critérios e dados sensíveis | Sua aprovação |
| 7. TEST | — | Testes | TEST e testes xUnit em RED | Sua aprovação |
| 8. TASK | — | Gerente | TASK-n em pares RED/GREEN (`bks-create-plan-tasks`) | — |
| 9. Implementação | — | Dev | Código e explicação das escolhas | G1–G4, LOOP-4, guardas |
| 10. Revisão | Revisão em painel | Testes, Segurança, Qualidade | Achados com `arquivo:linha` | Sem crítica aberta |
| 11. Registro | — | Documentador | ADR, README, ARCHITECTURE.md, STATUS, JOURNAL, biblioteca regerada (`/bkhar:save`) | Modelo defasado vira aviso para o `/bkhar:arch --update` |
| 12. Aprendizado | Retrospectiva | Documentador | Propostas em `inbox/proposals/` | Sua curadoria |

### 25. Modos de condução

O projeto escolhe como é conduzido, em `axes.mode` do `.bks-profile.json`. O `colaborativo` é o padrão; o `autonomo` é opcional e com limites.

| Onde | `colaborativo` | `autonomo` |
| --- | --- | --- |
| `/bkhar:refine`, `/bkhar:spec` | os agentes perguntam e esperam você | o Arquiteto responde as próprias perguntas pelas fontes e grava cada resposta como suposição em `decisions/SUPOSICOES.md` |
| Portões seus | FEAT, TEST e cada tentativa | três: PRD, PLAN e ARCH aprovados; contratos da onda de desenho; entrega final |
| `/bkhar:loop` | decisão fora da FEAT para e pergunta | decisão fora da FEAT vira suposição; para só em `BLOQUEIO` |
| `/bkhar:review` | achados voltam para você | bloqueante volta ao loop; sugestão vai para o relatório da onda |
| Paralelismo | não | ondas em worktree |

**Prontidão.** O `/bkhar:mode autonomo` só troca o modo quando o `scripts/readiness.py`, sem chamar modelo, concede: CONTEXT revisado ou aprovado, PRD e PLAN aprovados, grafo válido, ARCH e modelos aprovados e em dia, nenhuma questão em aberto e a stack no perfil. A recusa lista o que falta por nível e o comando que resolve. A troca grava ADR; sem ADR, não houve troca.

**O que nenhum modo afrouxa:** os guardas de `hooks/`, build e testes verdes, o RED antes do código, o máximo de 4 tentativas, nada de push na `main` e a Segurança em área sensível. Dado pessoal, autorização e segredo não se presumem: param em `BLOQUEIO`. Em `rigor: producao`, os contratos da onda de desenho continuam com você.

### 26. Ondas e painel

O `/bkhar:plan` grava o grafo `outputs/GRAPH-{projeto}.json`. Cada task declara o que `consome`, o que `produz` e os `arquivos` que escreve. As ondas são calculadas, não declaradas: a task vem depois de quem produz o que ela consome, e só começa quando tudo o que consome existe com `status: aprovado`.

| Onda | Produz | Quem faz |
| --- | --- | --- |
| 0 · Contexto | canônico, PRD, PLAN, ARCH | você aprova |
| 1 · Desenho | contratos por lente: banco, API, infra, telemetria, ameaças | Arquiteto por lente, em paralelo; Segurança no modelo de ameaças |
| 2 · Construção | apps e serviços | LOOP-4 por task, cada uma na sua worktree |
| 3 · Front e integração | telas, testes de ponta a ponta | LOOP-4 por task |

O `/bkhar:loop --wave next` libera até 4 tasks simultâneas. No fim da onda, a sessão principal faz o merge das worktrees, roda build e suíte completos, chama o `/bkhar:review` sobre a onda inteira, confere a arquitetura viva e grava `outputs/run/onda-N/RELATORIO.md`. Conflito de merge para a onda; `BLOQUEIO` de uma task segura só a cadeia que depende dela.

O estado vive em `outputs/run/`, e só o orquestrador o escreve, pelo `scripts/run_state.py`, que recusa transição inválida: 5ª tentativa, task não liberada, execução pausada. O `/bkhar:status` mostra a tabela no terminal.

O painel acompanha e conversa com a execução:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py .     # http://127.0.0.1:8765
```

Ele mostra as ondas, as tasks e as tentativas ao vivo, os bloqueios, o modelo de cada papel e o consumo por modelo, agente e dia, e avisa pelo navegador quando uma task trava. Por ele você responde a um `BLOQUEIO`, pausa ou retoma a onda, deixa mensagem para a próxima tentativa e troca o modelo de um papel. Tudo vira pedido em `outputs/run/inbox/`, que o orquestrador aplica no próximo ponto de controle, entre tentativas e entre tasks: subagente em execução não recebe mensagem de fora, e o painel não finge controle em tempo real.

### 27. Comandos

Os comandos já existem e só existem no plugin: a cópia global em `~/.claude/commands/` foi removida em 2026-09-15, porque divergia da do kit e vencia na resolução de nome. O prefixo de um comando de plugin é o nome do plugin, e nenhum frontmatter o remove. Por isso `/bkhar:*` exige que o plugin se chame `bkhar` (opção A, recomendada): o kit é rebatizado, e durante a migração o plugin `bks` continua instalado para os projetos que ainda não mudaram. Não há executável `bkhar` separado: um motor de execução só, o `/bkhar:loop`, que evolui o `/bks:loop`.

| Comando | Hoje no kit | Onde roda | O que faz | Status |
| --- | --- | --- | --- | --- |
| `/bkhar:brain` | `/bks:brain` | Vault ou repo | Panorama dos projetos, ou o STATUS do projeto; avisa modelo defasado | Existe |
| `/bkhar:new-project` | `/bks:new-project` | Vault | Cria repo canônico e grava o perfil | Existe |
| `/bkhar:migrate` | — | Repo | Traz um projeto do `bks` para o `bkhar` e grava o `.bkhar.json` | Existe (Fase 1) |
| `/bkhar:note` | `/bks:note` | Repo | Nota viva em `docs/input/notas/` | Existe |
| `/bkhar:canonize` | `/bks:canonize` | Repo | `docs/input/` + `docs/design/` → `CONTEXT.md` | Existe |
| `/bkhar:prd` | `/bks:prd` | Repo | `CONTEXT.md` → `PRD-{projeto}.md` | Existe |
| `/bkhar:plan` | — | Repo | PRD → `outputs/PLAN-{projeto}.md` e o grafo `outputs/GRAPH-{projeto}.json` | Existe (1.0.0, com grafo) |
| `/bkhar:arch` | `/bks:arch` | Repo | Portão: ARCH e um modelo por arquivo em `docs/library/architecture/`, pela `bks-arch`, para aprovar; `--update` refaz o defasado | Existe (1.0.0, portão) |
| `/bkhar:library` | — | Repo | Catálogo e dashboard da biblioteca; `export` para `knowledge/` do vault | Existe (1.0.0) |
| `/bkhar:refine` | — | Repo | Rito de refinamento: perguntas da equipe, FEAT com `Refinamento: sim`, TEST; no `autonomo`, as perguntas viram suposições | Existe (0.9.0; ramo `autonomo` na 1.0.0) |
| `/bkhar:spec` | `/bks:spec` | Repo | Entrevista → FEAT → TEST, sem rito | Existe; exceção ao `/bkhar:refine` |
| `/bkhar:loop` | `/bks:loop` | Repo | Passo 0 com o RED do Testes; LOOP-4 com o Dev; com `--wave N`, a onda do grafo com até 4 tasks em paralelo, cada uma em worktree | Existe (`--wave` na 1.0.0) |
| `/bkhar:review` | `/bks:review` | Repo | Revisão em painel: Testes, Qualidade e, em área sensível, Segurança | Existe |
| `/bkhar:status` | — | Repo | Tabela da execução em ondas: liberado, em curso, bloqueado, suposições abertas | Existe (1.0.0) |
| `/bkhar:mode` | — | Repo | Troca entre `colaborativo` e `autonomo` pela prontidão, com ADR | Existe (1.0.0) |
| `/bkhar:maintainability` | `/bks:maintainability` | Repo | Parecer de manutenibilidade por aplicação | Existe |
| `/bkhar:save` | `/bks:save` | Repo | Decisões, specs, STATUS, JOURNAL, alertas do canônico e da arquitetura, candidatas ao vault, biblioteca regerada | Existe |
| `/bkhar:retro` | — | Repo | Promove cada proposta candidata a regra do projeto, do vault ou do kit, ou a rejeita com motivo | Existe (1.0.0) |
| `/bkhar:harvest` | — | Vault | Indexa ADRs e `LEARNINGS.md` de `repos/` e consolida por tema em `knowledge/wiki/experiencia/` | Existe (1.0.0) |
| `/bkhar:ingest` | `/bks:ingest` | Vault | Fonte ou lote → página em `knowledge/wiki/` | Existe |
| `/bkhar:panel` | — | Repo | Painel com 2 ou 3 agentes independentes; ADR com as opções descartadas | Existe (0.9.0) |
| `/bkhar:ask <agent>` | — | Repo | Pergunta direta a um papel, com resposta que cita a fonte | Existe (0.9.0) |
| skill `bks-sdd` + flags | idem | Repo | Fluxo completo: workspace, PLAN, TASKs, `--context`, `--cost-report` | Existe |
| `/bkhar:brainstorm` | — | Qualquer pasta | Rito de brainstorming com a skill de mesmo nome | Proposto |
| `/bkhar:skill new / list / promote` | — | Repo do harness | Cria, lista e promove skills | Proposto |
| `/bkhar:cost` | `--cost-report` + `session_cost.py` | Repo | Custo por agente, modelo, skill e fase; o painel já mostra o consumo por modelo, agente e dia | Evolui o que existe |
| `claude plugin eval .` | idem | Repo do harness | Evals de skill com delta with × without | Existe, falta a baseline |

O `/bkhar:curate` previsto nas versões anteriores foi absorvido pelo `/bkhar:retro`: a curadoria é a promoção ou a rejeição de cada candidata.

Como usar cada comando, com passo a passo e exemplo: Parte X, Manual de comandos.

## Parte VII — Case: comprovante PIX

Este case é fictício. Ele acompanha uma feature do pedido à retrospectiva: um endpoint de consulta de comprovante PIX numa API .NET 10 em hexagonal, com Dapper e SQL Server. O projeto já passou pela fase pesquisa: `docs/canonical/CONTEXT.md` e `PRD-{projeto}.md` existem. O `.bks-profile.json` declara perfil `backend` com rigor `producao`, e o manifesto `.claude/multiagente.md` lista pagamentos e dado pessoal como áreas sensíveis.

### 28. Pedido e refinamento

> **Você:** `/bkhar:refine` endpoint para consultar comprovante PIX por id.
>
> **Gerente:** Antes da FEAT, o time tem quatro perguntas.
>
> **Segurança:** Quem pode consultar, só o pagador ou também o recebedor? Isso define o controle de acesso.
>
> **Testes:** "Comprovante inexistente" e "comprovante de outro cliente" devem dar a mesma resposta? Se não derem, o endpoint revela que o comprovante existe.
>
> **Arquiteto:** Suas premissas indicam CQRS para leitura pesada. O volume aqui justifica, ou leitura direta basta?
>
> **Qualidade:** O retorno usa Result Pattern ou exceção? A premissa diz Result, mas o projeto tem dois controllers com exceção.

Você responde: pagador e recebedor podem consultar; as duas situações retornam 404; leitura direta basta por enquanto; Result Pattern em todo o fluxo. O Arquiteto registra a escolha de leitura direta como ADR, com CQRS como alternativa descartada e o gatilho para revisitar.

### 29. FEAT e TEST

A FEAT nasce com os critérios: 404 para inexistente ou alheio, CPF sempre mascarado, autorização por pagador ou recebedor, p95 abaixo de \[\_\_\] ms. O agente de Testes escreve o TEST e os testes xUnit em RED, um por critério. Você aprova os dois.

### 30. Implementação sob LOOP-4

O routing.yaml pede DeepSeek como Dev, mas a zona é sensível. O policy engine troca para o modelo local e registra a troca.

| Tentativa | O que aconteceu | Gate | Resultado |
| --- | --- | --- | --- |
| 1 | Dev referencia um tipo que não existe | `dotnet build` | Falhou; o erro volta como contexto |
| 2 | Domain passa a referenciar Dapper diretamente | NetArchTest | Falhou; viola a hexagonal |
| 3 | Repositório movido para o adapter, porta no domínio | `dotnet test` | Passou |

A cada tentativa, o Dev explica o que mudou e por quê. Na tentativa 2, ele registra: "Coloquei a query no domínio para simplificar; o gate mostrou que viola a premissa. Movi para o adapter."

### 31. Revisão em painel

- **Segurança (bloqueante):** um log em nível Debug grava o comprovante completo, com CPF. Vira nova task.
- **Qualidade (sugestão):** o handler tem 40 linhas; propõe extrair a autorização num serviço de domínio. Você aceita.
- **Testes (aprendizado):** faltou um teste para recebedor consultando comprovante de outro recebedor. Vira task e proposta de checklist.

O Dev corrige, os gates passam de novo, e o painel aprova.

### 32. Registro e retrospectiva

O Documentador grava o ADR "Leitura direta para comprovante", atualiza o diagrama C4 de componentes, marca a FEAT como concluída e registra o custo: Arquiteto \[US$ \_\_\], Dev local, revisores \[US$ \_\_\].

Na retrospectiva, saem três propostas:

1. **Premissa:** CPF como value object que só expõe a versão mascarada.
2. **Checklist de Segurança:** verificar logs em nível Debug em todo diff de zona sensível.
3. **Template de FEAT:** seção "Quem pode ver" obrigatória em toda consulta.

Você promove as três com `/bkhar:retro`: a premissa e o checklist como regras do kit, à espera de eval, e o template como regra do projeto. Na próxima feature, o Segurança já pergunta sobre log Debug no refinamento, e o template já pede "Quem pode ver". Você aprovou cinco vezes e não reexplicou nada.

## Parte VIII — Implantação

A implantação parte do kit que já funciona e nunca para os projetos em curso. O repositório do harness é público no GitHub, `fabiobackside-code/Bks-Harness`. Neste Atlas, `<harness>` é a pasta onde você o clonou: por exemplo, `C:\dev\bks-harness` no Windows ou `~/dev/bks-harness` no Linux e no macOS. Cada fase já é útil sozinha, e o plugin `bks` continua instalado até o último projeto migrar. Para instalar e começar a usar, o roteiro passo a passo é o manual de treinamento, em `docs/artefatos/treinamento/treinamento-bks-harness.html`.

### 33. Fases

| Fase | Entrega | Critério de saída | Risco para projetos em curso |
| --- | --- | --- | --- |
| 0. Planejar | Plano, decisões fechadas, ADR-001 (nomenclatura A) | Decisões da seção 7 do plano respondidas | Nenhum |
| 1. Importar | Kit trazido com os 44 commits, renomeado `bkhar`, suíte estrutural verde, `/bkhar:migrate` escrito | `claude plugin validate` e testes estruturais passam | Nenhum: `bks` segue instalado |
| 2. Instalar lado a lado | `bkhar` instalado no escopo do usuário, aliases dos comandos antigos | Os dois plugins respondem sem colisão | Baixo |
| 3. Equipe e ritos | Seis agentes e o Gerente (skill `bks-team`); `/bkhar:ask`, `panel`, `refine`; `review` em painel; `LEARNINGS.md`. A 1.0.0 trouxe depois os modos, as ondas, o painel, o aprendizado candidato com `retro` e `harvest`, o portão de arquitetura e a biblioteca | Uma FEAT real com refinamento e painel | Nenhum até um projeto migrar |
| 4. Modelo plugável | `providers/`, Modo Contexto como primeiro adapter, policy engine lendo o manifesto | Um agente rodando em DeepSeek num projeto `poc` | Nenhum |
| 5. Piloto | O `poc-treino-harness` como teste do `autonomo` da 1.0.0, com as travas de consumo medidas | Retomar e fechar sessão sem atrito | Baixo, reversível |
| 6. Migrar os demais | Um por vez, entre fases; `nquantic` por último | Todos com `.bks-profile.json` e `/bkhar:*` | Baixo |
| 7. Medir e aposentar | Baseline das evals, delta por skill e modelo; `bks` desinstalado | Skill ou modelo só promovido com delta medido | — |

### 34. Estrutura de pastas

```
<harness>\                               o harness (plugin bkhar), ex.: C:\dev\bks-harness
├── .claude-plugin\                      plugin.json (name: bkhar) + marketplace.json
├── agents\                              manager, architect, developer, tester,
│                                        security, quality, scribe + references\
├── commands\                            /bkhar:* (os 12 de hoje + migrate, refine, panel, ...)
├── skills\                              as 17 de hoje + brainstorming, performance, ...
├── hooks\                               guardas que recusam a escrita, com testes
├── profiles\ · templates\               nove perfis e eixos; layout de projeto
├── providers\                           claude (padrão), deepseek, ollama
├── scripts\                             readiness, wave_graph, run_state, dashboard,
│                                        learning, harvest, library, publish
├── inbox\proposals\ · archive\          propostas da retro e rejeitadas
├── evals\ · tests\                      casos com delta e suíte estrutural
└── docs\                                PLANO-MIGRACAO, ARCHITECTURE, handoff\

${BKS_VAULT}\                              o vault, só conteúdo
├── workbench\                           profile.md, decisions\
├── knowledge\                           wiki\ (experiencia\, projetos\), raw\, tools\
├── repos\{backside,w3,private,old}\     os projetos, cada um com git próprio
│   └── {projeto}\                       STATUS, WORKFLOW, JOURNAL, .bks-profile.json,
│                                        brain\{domain,engineering}\, decisions\,
│                                        specs\, docs\ (library\), outputs\ (run\), app\
└── docs\                                guias do vault

~\.claude\settings.json                   env BKS_VAULT (raiz do vault), BKS_KNOWLEDGE
```

### 35. Primeiros passos

- [x] Criar `<harness>` com git local e o plano de migração
- [ ] Fechar as decisões: nomenclatura A, histórico do kit, merge da `feat/maintainability`, projeto piloto
- [x] Registrar o ADR-001 (nomenclatura) em `<harness>\decisions\`
- [x] Importar o `prj-bks-kit` com histórico e renomear o plugin para `bkhar`
- [x] Escrever o `/bkhar:migrate`
- [ ] Dar `.bks-profile.json` ao `nquantic` e ao `layan` (o `/bkhar:migrate` pergunta o perfil)
- [x] Instalar `bkhar` ao lado do `bks` com `/plugin marketplace add <harness>` (ex.: `C:\dev\bks-harness`)
- [x] Escrever a equipe, o Gerente e os ritos `/bkhar:ask`, `panel`, `refine` (0.9.0)
- [x] Escrever a retrospectiva e a curadoria: `/bkhar:retro` e `/bkhar:harvest` (1.0.0); o `curate` foi absorvido pelo `retro`
- [x] Modos `colaborativo` e `autonomo`, ondas pelo grafo e painel com inbox (1.0.0)
- [x] Portão de arquitetura e biblioteca do projeto (1.0.0)
- [ ] Piloto do `autonomo` no `poc-treino-harness`
- [ ] Migrar o piloto (`mcp-sql` ou `bks-motor-sdk`) e usar uma semana
- [ ] Rodar a baseline das evals quando houver crédito

## Parte IX — Evolução: skills plugáveis

O harness foi feito para crescer. Cada capacidade nova entra como uma skill versionada, que qualquer agente pode carregar, sem mexer no core nem nos perfis.

### 36. Agente e skill

O agente é o papel: **quem** pergunta, decide ou revisa. A skill é a capacidade: **como** se faz brainstorming, análise de ameaças ou profiling. Um mesmo agente ganha competência nova quando você liga uma skill ao perfil dele, e uma mesma skill pode servir a vários agentes.

As skills carregam sob demanda. Só o nome e a descrição ficam sempre no contexto; o corpo, as referências e os scripts entram quando a skill é acionada. É a mesma economia de tokens que motivou o BKS-TXC.

### 37. Catálogo inicial

| Skill | O que traz | Usada por | Situação |
| --- | --- | --- | --- |
| `bks-sdd` | Ciclo SDD completo, Modo Contexto, custo | Gerente, Arquiteto | Existe (2.062 linhas, a adelgaçar) |
| `bks-create-plan-tasks` | Decomposição em tasks atômicas | Gerente | Existe |
| `bks-standards` | Premissas, calisthenics, comentário, SEDA, TCP | Arquiteto, Qualidade, Dev | Existe |
| `bks-dotnet-solutions` | .NET em hexagonal com pipeline e TXC | Arquiteto, Dev | Existe |
| `bks-typescript-solutions` | API, agente LangGraph, worker, consumer em TS | Arquiteto, Dev | Existe |
| `bks-go-solutions` | API, worker, consumer, CLI e SDK em Go | Arquiteto, Dev | Existe |
| `bks-tests` | xUnit único, 90%+ de cobertura, SonarQube | Testes | Existe |
| `bks-arch` | Notação BKS para Mermaid, archify, C4, TOGAF | Arquiteto, Documentador | Existe |
| `bks-writing` | Padrão de escrita da documentação em PT-BR | Documentador | Existe |
| `bks-maintainability-review` | Parecer de manutenibilidade, nota 0–100 | Qualidade, Arquiteto | Existe (0.7.0, sem uso real) |
| `security-audit` | Entrada, autorização, segredo, dado sensível | Segurança | Existe; evolui com STRIDE, ASVS, LGPD, BACEN |
| `api-design` · `refactor-guide` · `debug-assistant` | Contrato HTTP; refatoração com rede; do sintoma à causa | Arquiteto, Dev | Existem |
| `doc-writer` · `pr-writer` · `frontend-design` | Docstring e README; PR pelo diff real; interface | Documentador, Dev | Existem |
| `brainstorming` | Divergir e convergir, pre-mortem, seis chapéus | Gerente, todos nos painéis | Proposta |
| `performance` | Orçamento de latência, BenchmarkDotNet, carga, alocação | Dev, Qualidade, Arquiteto | Proposta |
| `lang-java-spring` · `lang-php` | Convenções por linguagem no padrão hexagonal | Dev, Qualidade | Proposta |
| `legado-interop` | Mainframe, COBOL, TCP binário, Anti-Corruption Layer | Arquiteto, Dev | Proposta |

### 38. Anatomia de uma skill

```
skills\performance\
├── SKILL.md          nome, descrição, versão, agentes, gatilhos, instruções
├── references\       material de apoio, carregado só quando preciso
├── scripts\          ferramentas executáveis (ex.: rodar um benchmark)
├── evals\            casos de entrada com o resultado esperado
└── CHANGELOG.md      o que mudou em cada versão
```

O SKILL.md é o formato que o Claude já entende, com progressive disclosure: o corpo fica curto e o detalhe mora em `references/`. Para outros modelos, o primeiro adapter é o Modo Contexto (`--context`) do `bks-sdd`: o Claude monta o pacote de contexto da task e o agente externo executa, sem reescrever a skill.

### 39. Ciclo de vida

| Estágio | Critério de entrada | Onde pode ser usada |
| --- | --- | --- |
| Proposta | Surgiu na retro ou a pedido seu | Em nenhum lugar ainda |
| Experimental | SKILL.md escrito e pelo menos 5 evals | Projetos não sensíveis, com aviso |
| Estável | Passa nas evals e em 3 FEATs reais, com sua aprovação | Todos os projetos |
| Deprecada | Substituída por outra ou sem uso | Projetos que a fixaram, até migrarem |

&#91;embedded content: ciclo de vida da skill · 4 estágios e seus critérios\]

Os critérios ficam entre os estágios: uma skill só avança quando cumpre o que está escrito embaixo da seta.

### 40. Versionamento

Toda skill segue versionamento semântico:

- **MAJOR** quando muda o comportamento esperado (uma regra removida, um formato de saída novo).
- **MINOR** quando acrescenta sem quebrar (uma pergunta nova no checklist, uma referência nova).
- **PATCH** quando corrige texto ou exemplo.

Os perfis de agente declaram a faixa aceita, como `security-audit@^1`. Cada projeto tem um `skills.lock` que fixa a versão exata usada, para que uma FEAT de seis meses atrás possa ser revisada com as mesmas regras. No Git, cada versão ganha uma tag `skill/<nome>/v<versão>`.

### 41. Como uma skill nasce

Uma skill nasce do ciclo de aprendizado. Quando a retrospectiva acumula três ou mais propostas sobre o mesmo tema, o Documentador sugere transformá-las numa skill.

1. `/bkhar:skill new <nome>` abre um rito de brainstorming com você, o Arquiteto e o agente que vai usar a skill.
2. O Documentador escreve o SKILL.md e os primeiros casos em `evals/`; a skill entra como experimental.
3. `claude plugin eval . --case <caso>` roda os casos com e sem a skill; o que vale é o delta, de preferência em mais de um modelo.
4. Depois de três FEATs reais, `/bkhar:skill promote <nome>` pede sua aprovação para torná-la estável.

**Exemplo: Go já fez esse caminho.** A `bks-go-solutions` nasceu das suas convenções: hexagonal em pacotes, erro idiomático no lugar de `Result[T]`, testes de tabela. Ela alimenta e consome a base `knowledge/wiki/go/`, com lições anonimizadas dos projetos. Falta o caso de eval, que espera a baseline. O próximo candidato é `lang-java-spring`, pelo mesmo caminho.

### 42. O harness também evolui

O próprio harness segue o padrão que ele aplica. Agentes, comandos, skills, guardas e perfis são versionados em `<harness>`, e o ciclo dele é o mesmo do kit hoje: **mudar → provar → medir**. Uma mudança vive no diretório da sua natureza, a suíte estrutural prova que nada quebrou, e o eval mede se a skill muda a decisão do agente. Decisão sobre o harness vira ADR em `<harness>\decisions\`; decisão sobre como você trabalha, em `workbench/decisions/` do vault.

## Apêndices

### A. Template de perfil de agente

O formato real dos agentes do `bkhar`, aqui com a Segurança, resumida de `agents/security.md`. O frontmatter tem só as quatro chaves que o Claude Code lê; as skills que o papel carrega ficam numa seção do corpo, para não depender de chave que a plataforma não conhece. A primeira linha do corpo anuncia o tier, e as sete seções são as mesmas em todo perfil.

```markdown
---
name: security
description: Segurança da equipe. Analisa FEAT e diff pelo ângulo de dado sensível, autorização, log e segredo. Só lê; todo achado com arquivo:linha.
model: opus
tools: Read, Grep, Glob
---

> Ao iniciar, diga em uma linha: `security - Opus - Read, Grep, Glob`.

# Agente — security

## Persona
Analista de AppSec com experiência em sistemas bancários brasileiros.
Direto, cético, nunca aprova por cortesia.

## Responsabilidades
- No refinamento, até três perguntas pelo ângulo da segurança
- Na revisão em painel, o diff que toca área sensível do manifesto
- Classificar cada achado: bloqueante, sugestão ou aprendizado

## Limites
- Só lê; todo achado tem arquivo:linha
- Crítica bloqueia a entrega

## Fontes obrigatórias
- manifesto do projeto
- skills/bks-standards/references/checklist-revisao-critica.md
- skills/bks-team/references/code-review-checklist.md

## Perguntas obrigatórias
1. Que dado sensível passa por aqui?
2. Quem pode ver este dado, e como isso é verificado?
3. Algum log, mensagem de erro ou trace expõe o dado?

## Skills que carrega
`security-audit` e `bks-standards`.

## Aprendizado
Ao fim da revisão, devolva ao Gerente, em até 3 linhas, o que vale
virar regra de checklist ou premissa. O /bkhar:save registra.
```

### B. routing.yaml de referência

O ponto de partida são os modelos que os agentes do kit já usam. Trocas, como o DeepSeek no Dev, só entram depois das evals da Fase 7.

```yaml
agents:
  manager:   { model: session }         # a sessão principal, skill bks-team
  architect: { model: claude-opus }     # era o planner; em medição contra sonnet
  developer: { model: claude-sonnet }   # era o builder; candidato: deepseek em projeto poc
  tester:    { model: claude-sonnet }   # novo; meta: fornecedor diferente do developer
  security:  { model: claude-opus }     # era o reviewer (read-only)
  quality:   { model: claude-sonnet }   # novo
  scribe:    { model: claude-haiku }    # scribe hoje

rules:
  - order: [manager, architect, tester, developer, security, quality, scribe]
  - security.vendor != developer.vendor   # meta da Fase 4
  - loop.max_attempts: 4

zones:
  sensitive:                              # áreas sensíveis do manifesto
    allowed_vendors: [anthropic, ollama-local]
    fallback:
      developer: ollama-local
```

### C. Glossário

| Termo | Significado |
| --- | --- |
| Harness | Tudo em volta do modelo: contexto, ferramentas, fluxo, verificação e observação |
| Plugin | Pacote do Claude Code com skills, comandos, agentes e guardas; o nome dele é o prefixo dos comandos |
| Vault | `${BKS_VAULT}`: `workbench/` (você), `knowledge/` (o que você aprendeu) e `repos/` (os projetos) |
| Projeto autossuficiente | Cada repo guarda sua memória, decisão e domínio; nenhum comando de projeto lê o vault |
| STATUS, WORKFLOW, JOURNAL | Onde parei; o fluxo de comandos do projeto; os marcos, do mais recente ao mais antigo |
| Perfil | O que o projeto gera (`backend`, `fullstack`, `component`...), em `.bks-profile.json` |
| Rigor | Eixo do perfil: `producao` ou `poc`; dimensiona a revisão |
| CONTEXT.md | Contexto canônico do projeto, gerado pelo `/bkhar:canonize` a partir de `docs/input/` |
| FEAT, TEST, TASK | Spec da feature, cenários de teste e unidades de trabalho, em `specs/` |
| LOOP-4 | Até quatro tentativas com goals G1–G4; depois, `BLOQUEIO-*.md` e decisão sua |
| Gate | Verificação executada pela máquina, não declarada pelo modelo |
| Guarda | Hook que recusa a escrita fora do padrão, com teste próprio |
| Manifesto | `.claude/multiagente.md`: zonas de contenção, áreas sensíveis, invariantes |
| Zona de contenção | Arquivo que só a sessão principal edita (Composition Root, migrations, numeração de ADR) |
| Área sensível | Parte do manifesto que exige revisão independente e restringe provedor |
| PBQ | Tipo do papel: orquestrador, implementador ou validador |
| Rito | Formato de conversa com papéis, começo e fim |
| Proposta | Aprendizado candidato (`status: candidata`) em `inbox/proposals/`, à espera do `/bkhar:retro` |
| Modo | `colaborativo` (padrão) ou `autonomo`, em `axes.mode` do perfil |
| Prontidão | Checagem por script que concede o `autonomo`: entradas aprovadas e nada em aberto |
| Suposição | Resposta que o Arquiteto presumiu no `autonomo`, registrada em `decisions/SUPOSICOES.md` |
| Onda | Conjunto de tasks do grafo liberadas juntas, até 4 em paralelo |
| ARCH | Índice da arquitetura em `docs/library/architecture/`, que aponta um modelo por arquivo |
| Biblioteca | `docs/library/`: catálogo e dashboard dos artefatos do projeto |
| Skill | Capacidade versionada que um ou mais agentes carregam sob demanda |
| Eval | Caso que mede o delta de uma skill: o agente com ela contra o agente sem ela |
| TXC | Transaction Context: record imutável que flui pelos estágios do pipeline |

### D. Referências

- [GitHub Spec Kit — metodologia spec-driven](https://github.github.com/spec-kit/)
- [Anthropic — Claude Code: Best Practices for Agentic Coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — When to use multi-agent systems](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them)
- [Claude Agent SDK — visão geral](https://code.claude.com/docs/en/agent-sdk/overview)
- [Alistair Cockburn — Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture)
- [Scott Wlaschin — Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- [Matt Welsh — SEDA, SOSP 2001](https://www.sosp.org/2001/papers/welsh.pdf)
- [Jeff Bay — Object Calisthenics](https://bolcom.github.io/student-dojo/legacy-code/DevelopersAnonymous-ObjectCalisthenics.pdf)
- [Building a Second Brain × Zettelkasten](https://zettelkasten.de/posts/building-a-second-brain-and-zettelkasten/)

As referências vêm do README do 2brains.

Origens do próprio 2brains: a ideia do workbench isolado veio do [obsidian-ai-workbench](https://github.com/RenzoTakada/obsidian-ai-workbench) (RenzoTakada), e a governança multi-agente foi adaptada do [bks-multiagent-skill](https://github.com/DiegoAmorimDev/bks-multiagent-skill) (DiegoAmorimDev, MIT). O template público está em [bks-obsidian-2brains-ai-pattern](https://github.com/fabiobackside-code/bks-obsidian-2brains-ai-pattern).

### E. Template de skill

Exemplo da skill `performance` em estágio experimental.

```markdown
---
name: performance
version: 0.1.0
stage: experimental
agents: [dev, qualidade, arquiteto]
description: Orçamento de latência, profiling e testes de carga. Use quando a FEAT tiver meta de p95, quando o diff tocar caminho crítico ou quando o Qualidade suspeitar de alocação excessiva.
---
# Quando acionar
- FEAT com critério de latência, throughput ou memória
- Diff em handler, repositório ou consumer de alto volume

# Perguntas obrigatórias
1. Qual é o orçamento (p95, throughput) e de onde ele vem?
2. Qual é a medição atual, antes da mudança?
3. Onde estão as alocações e as idas ao banco no caminho crítico?

# Como medir
- Microbenchmark: BenchmarkDotNet (ver references/benchmarkdotnet.md)
- Carga: k6 com o cenário da FEAT (ver scripts/k6-template.js)

# Regras
- Nenhuma otimização sem medição antes e depois
- Legibilidade só é sacrificada com número que justifique, registrado em ADR

# Evals
Ver evals/: cada caso traz um diff e os achados esperados.
```

### F. Histórico de versões

| Artefato | Versão | Data | O que mudou |
| --- | --- | --- | --- |
| Atlas do BKS Harness | 1.9.0 | 2026-11-04 | Modos de condução e prontidão (seção 25), ondas e painel (seção 26), modelo por papel, Parte V com o aprendizado candidato, `/bkhar:retro` e `/bkhar:harvest`; tabela de comandos com toda a 1.0.0; prefixo `/bkhar:` no texto do estado atual; Parte X com o manual 1.4.1 |
| Apresentação BKS Harness | 2.0.0 | 2026-11-04 | Slides novos de modos e de ondas e painel; aprendizado com retro e harvest; roadmap com a 1.0.0 |
| Apresentação BKS Harness | 1.9.0 | 2026-11-04 | Fluxo com a arquitetura antes da especificação; `/bkhar:library` nos comandos e no manual de uso |
| Atlas do BKS Harness | 1.8.0 | 2026-11-04 | Arquitetura como portão antes da especificação nos dois modos; biblioteca do projeto em `docs/library/` com dashboard e exportação para `knowledge/`; `/bkhar:library` na tabela de comandos; Parte X com o manual 1.4.0 |
| Atlas do BKS Harness | 1.7.3 | 2026-10-22 | Equipe contada como sete papéis, seis agentes e o Gerente, no prefácio, na Parte III e na Figura 4 |
| Apresentação BKS Harness | 1.8.3 | 2026-10-22 | Capa, case e slide de versões contam a equipe como seis agentes e o Gerente |
| Atlas do BKS Harness | 1.7.2 | 2026-10-20 | `/bkhar:plan` na tabela de comandos; Parte X com o manual de comandos 1.2.0 |
| Atlas do BKS Harness | 1.7.0 | 2026-10-19 | Partes III e IV ajustadas à equipe construída na Fase 3: seis agentes, Gerente como skill `bks-team`, `/bkhar:ask`, `panel` e `refine` existentes, revisão em painel, `LEARNINGS.md`, sem o atalho com arroba; Apêndice A no formato real do perfil |
| Atlas do BKS Harness | 1.6.1 | 2026-10-19 | Caminhos da máquina do autor trocados por `<harness>`, com exemplo de pasta; o repositório passa a constar como público no GitHub |
| Atlas do BKS Harness | 1.6.0 | 2026-10-18 | Parte X, Manual de comandos, com cada comando explicado e exemplificado; diagramas do fluxo e da arquitetura atualizados; mantido no repositório `bks-harness` e gerado em HTML pronto para PDF |
| Atlas do BKS Harness | 1.5.0 | 2026-10-18 | Revisão contra o `${BKS_VAULT}` local e o kit `bks` 0.7.0: sai o hub `brain/_bks-ai/`, entram `workbench/`, `knowledge/` e o projeto autossuficiente; comandos `/bks:*` e o caminho para `/bkhar:*` (opção A); guardas, evals, perfis, rigor e as 17 skills como existentes; planner em Opus; coluna PBQ; propostas em `inbox/proposals/`; sem `bkhar run` nem brain compiler; fases, estrutura e primeiros passos alinhados ao `PLANO-MIGRACAO` |
| Atlas do BKS Harness | 1.4.0 | 2026-10-17 | Revisão contra o template público do 2brains: fluxo pesquisa → código, diagrama do fluxo, comandos, os quatro agentes, criticidade e manifesto, LOOP-4 com G1–G4 e `BLOQUEIO` |
| Atlas do BKS Harness | 1.3.0 | 2026-10-17 | Cinco diagramas e edição em HTML pronta para PDF |
| Atlas do BKS Harness | 1.2.0 | 2026-10-17 | Comandos em inglês com prefixo `bkhar`, atalho `@<agente>` |
| Atlas do BKS Harness | 1.1.0 | 2026-10-17 | Parte IX (skills plugáveis), skill registry, apêndices E e F |
| Atlas do BKS Harness | 1.0.0 | 2026-10-17 | Primeira versão: Partes I a VIII, equipe de sete agentes, ritos, ciclo de aprendizado, case |
| Treinamento do bks-harness | 1.0.0 | 2026-10-19 | Primeira versão do manual de instalação e uso, para quem instala pelo repositório público |
| Apresentação BKS Harness | 1.8.2 | 2026-10-20 | `/bkhar:plan` nos slides de comandos e de manual do repo |
| Apresentação BKS Harness | 1.8.1 | 2026-10-19 | Slide de versões com o manual de treinamento |
| Atlas do BKS Harness | 1.7.1 | 2026-10-19 | Aponta para o manual de treinamento na Parte VIII; o template do vault passa a ser o `bks-2brains` |
| Apresentação BKS Harness | 1.8.0 | 2026-10-19 | Slides de equipe, ritos, comandos e manual do repo com a equipe da Fase 3; conceitos e roteamento sem os agentes antigos como estado atual |
| Apresentação BKS Harness | 1.7.1 | 2026-10-19 | Slide do roadmap sem o caminho da máquina do autor |
| Apresentação BKS Harness | 1.7.0 | 2026-10-18 | Dois slides de manual de uso dos comandos, um para o vault e outro para o repo; mantida no repositório `bks-harness` e gerada em HTML pronto para PDF |
| Apresentação BKS Harness | 1.6.0 | 2026-10-18 | Mesma revisão do Atlas 1.5.0 aplicada aos slides |
| Apresentação BKS Harness | 1.5.0 | 2026-10-17 | Revisão contra o template público: 2brains hoje, fluxo pesquisa → código, comandos, equipe |
| Apresentação BKS Harness | 1.4.0 | 2026-10-17 | Diagramas da equipe, do LOOP-4 e do ciclo de aprendizado |
| Apresentação BKS Harness | 1.3.0 | 2026-10-17 | Comandos com prefixo `bkhar` |
| Apresentação BKS Harness | 1.2.0 | 2026-10-17 | Skills plugáveis e slide de versões |
| Apresentação BKS Harness | 1.1.0 | 2026-10-17 | Equipe de sete agentes, ritos, case refeito (21 slides) |
| Apresentação BKS Harness | 1.0.0 | 2026-10-17 | Primeira versão (17 slides) |

Regra: MAJOR quando muda a estrutura do harness, MINOR quando acrescenta parte ou capacidade, PATCH quando corrige texto.
