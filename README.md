# bks-harness

Harness de engenharia assistida para o Claude Code: o método BKS de Spec-Driven Development em
skills, comandos, agentes, guardas e evals, empacotados como o plugin `bkhar`. Uma equipe de
agentes que conversa com você, não vibe coding.

Para entender o desenho antes de instalar:

| Documento | Para que |
|---|---|
| `docs/artefatos/atlas/atlas-bks-harness.html` | Atlas: a equipe, os ritos, os comandos e o manual de uso |
| `docs/artefatos/apresentacao/apresentacao-bks-harness.html` | Apresentação: a visão geral em slides |
| `docs/artefatos/manual/manual-comandos.md` | Manual de comandos |
| `docs/ARCHITECTURE.md` | As decisões estruturais do kit e o porquê de cada uma |

Comandos em inglês, prefixo `bkhar`. Documentação em português do Brasil.

## O kit (base 0.7.0, agora `bkhar` 3.0.0-beta)

Plugin do Claude Code com o kit BKS de **Spec-Driven Development** — o processo que leva uma ideia
de produto até código implementado, passando por PRD, planos, especificações de feature, cenários
de teste e tasks executáveis.

Não e um framework de código. É o processo de trabalho: skills que conduzem o ciclo, comandos que
operam o workbench e agentes com papéis separados.

> **3.0.0-beta.** Esta versão traz a integração com o Maestri: a equipe em terminais, o
> `/bkhar:maestri`, a delegação de comando e o `architect` com Bash sob guarda. Essa parte ainda está
> em prova num projeto piloto. Sem o bloco `maestri` no perfil do projeto, o harness funciona como na
> 1.1.0: papéis por subagente e comandos na própria sessão.

### Instalação

```
/plugin marketplace add fabiobackside-code/Bks-Harness
/plugin install bkhar@bks-harness
```

Em uma linha, no Claude Code 2.1.275 ou mais novo:

```
/plugin install bkhar --marketplace fabiobackside-code/Bks-Harness
```

Para instalar a partir de um clone local: `/plugin marketplace add <pasta-do-clone>` (ex.: `C:\dev\bks-harness`).

O passo a passo completo, do pré-requisito ao primeiro ciclo com a equipe e com o vault opcional,
está no manual de treinamento: [`docs/artefatos/treinamento/treinamento-bks-harness.html`](docs/artefatos/treinamento/treinamento-bks-harness.html),
pronto para imprimir em PDF.

Para usar a equipe em terminais do Maestri, siga o guia:
[`docs/artefatos/maestri/guia-maestri.html`](docs/artefatos/maestri/guia-maestri.html).

### Antes de instalar o harness

Git, Python 3 (com `python -m pip install -r requirements.txt`) e Node.js são os pré-requisitos. O harness roda com a conta do Claude Code ou, pelo lançador `bkhar`, com DeepSeek ou OpenRouter. O guia completo, com o `PATH` e a guarda da chave, está na seção "Antes de instalar o harness" do manual de comandos: [`docs/artefatos/manual/manual-comandos.md`](docs/artefatos/manual/manual-comandos.md).

### O que vem no kit

#### Skills

| Skill | Para que serve |
|---|---|
| `bks-sdd` | Ciclo SDD completo: workspace, PRD, projetos, plano macro, feature specs, cenários de teste, tasks e execução |
| `bks-dotnet-solutions` | Geração de soluções .NET com Arquitetura Hexagonal e o padrão TXC (Transaction Context) |
| `bks-typescript-solutions` | Backends Node.js + TypeScript: API REST, agente LangGraph, worker e consumer, também sob TXC |
| `bks-go-solutions` | Soluções Go: API REST, worker, consumer, CLI e SDK — TXC na forma que Go admite, erro idiomático no lugar de `Result[T]` |
| `bks-team` | Protocolo do Gerente: conduz os ritos da equipe, chama cada agente em invocação separada, numera as opções e para antes de gerar artefato |
| `bks-create-plan-tasks` | Decomposição de qualquer trabalho em tasks atomicas otimizadas para consumo de tokens |
| `bks-tests` | Cobertura de testes em solution .NET: projeto xUnit único em `src/`, 90%+ em linhas, branches e métodos, conformidade SonarQube |
| `bks-standards` | Padrões de engenharia BKS: premissas de codificação, dependências .NET e Go, calisthenics, politica de comentario, SEDA e TCP |
| `bks-arch` | Notação BKS de diagramas: paleta da marca, semantica de cor por tipo de no, convenção de linha — emite para Mermaid, archify, C4 ou TOGAF |
| `api-design` | Contrato de endpoint: semantica HTTP, versionamento, erro, paginação, idempotência |
| `frontend-design` | Interface com identidade própria — estrutura de componente, hierarquia visual, consistência |
| `security-audit` | Revisão de segurança: entrada, autorização, segredo, dado sensivel |
| `debug-assistant` | Do sintoma a causa: reproduzir, capturar em teste, isolar a camada |
| `refactor-guide` | Mudar estrutura sem mudar comportamento, com rede de teste antes |
| `doc-writer` | Docstring, README e comentario — sob o teto de comentario do kit |
| `bks-writing` | Padrão de escrita da documentação viva em PT-BR: decisão sintetizada no texto, abertura pela informação, frase curta, termo definido, lista de muletas |
| `bks-maintainability-review` | Parecer de manutenibilidade por aplicação, nota de 0 a 100 para um dev pleno, e a fundamentação teórica e técnica do projeto; critérios por stack, hoje .NET e SQL |
| `pr-writer` | Titulo e descrição de PR a partir do diff real, não da memória da conversa |

#### Comandos

| Comando | O que faz |
|---|---|
| `/bkhar:brain` | Retoma a sessão: quem você e, onde parou, próximo passo |
| `/bkhar:new-project` | Cria projeto novo com a estrutura canônica — único ponto de entrada |
| `/bkhar:note` | Escreve nota viva em `docs/input/notas/` do projeto |
| `/bkhar:ingest` | Ingere conhecimento para a base transversal em `knowledge/` do vault |
| `/bkhar:canonize` | Consolida pesquisa e design num contexto canônico único |
| `/bkhar:prd` | Gera o PRD a partir do contexto canônico |
| `/bkhar:plan` | Gera o plano macro `outputs/PLAN-{projeto}.md` a partir do PRD — obrigatório no perfil `fullstack` |
| `/bkhar:spec` | Caminho direto, sem rito: o `architect` escreve a especificação e o `tester`, os cenários |
| `/bkhar:arch` | Portão de arquitetura: com o PLAN aprovado, escreve o índice ARCH e um modelo por arquivo em `docs/library/architecture/`, pela `bks-arch`, para você aprovar; `--update` refaz só o que está defasado |
| `/bkhar:library` | Biblioteca do projeto: catálogo `docs/library/LIBRARY.md`, dashboard `docs/library/site/index.html`, aviso de arquitetura defasada e exportação para `knowledge/` do vault |
| `/bkhar:refine` | Refinamento: a equipe pergunta antes; o `architect` escreve a especificação e o `tester`, os cenários |
| `/bkhar:loop` | LOOP-4: o `tester` escreve o teste que falha, o `developer` implementa; máximo 4 tentativas. Com `--wave N`, no modo `autonomo`, roda a onda do grafo com até 4 tasks em paralelo, cada uma em worktree |
| `/bkhar:review` | Revisão em painel: `tester`, `quality` e, em área sensível, `security`, cada um em invocação separada |
| `/bkhar:maintainability` | Inventaria `app/`, gera um parecer de manutenibilidade por aplicação em `outputs/maintainability/` e a fundamentação do projeto em `outputs/references/` |
| `/bkhar:ask` | Pergunta direta a um agente da equipe, com resposta que cita a fonte |
| `/bkhar:panel` | Painel: 2 ou 3 agentes respondem sem ver os outros; você escolhe e o `scribe` registra a decisão |
| `/bkhar:retro` | Retrospectiva do aprendizado: você promove cada proposta candidata a regra do projeto, do vault ou do kit, ou a rejeita |
| `/bkhar:harvest` | Na raiz do vault: indexa por script os ADRs e o `LEARNINGS.md` de `repos/` e consolida por tema em `knowledge/wiki/experiencia/` |
| `/bkhar:save` | Roteia o resultado da sessão pela regra dos dois lugares |
| `/bkhar:status` | Estado da execução em ondas: tasks por onda, o que está liberado, bloqueios e suposições abertas; só lê |
| `/bkhar:mode` | Troca o modo de condução (`colaborativo` ou `autonomo`): roda a checagem de prontidão, grava ADR e altera o `.bks-profile.json` |
| `/bkhar:maestri` | Liga, desliga e confere a integração com o Maestri: grava o bloco `maestri` do `.bks-profile.json`, valida os terminais da equipe e do executor `ops` e diz o que criar quando falta |
| `/bkhar:migrate` | Traz um projeto do `bks` para o `bkhar`: confere o layout, troca o prefixo no `WORKFLOW.md` e no `CLAUDE.md`, grava o `.bkhar.json`; não commita |

#### Modos de condução, ondas e painel

O projeto escolhe o modo em `axes.mode` do `.bks-profile.json`:

| Modo | Como anda |
|---|---|
| `colaborativo` (padrão) | a equipe pergunta e espera você em cada FEAT (especificação da feature), TEST (cenários de teste) e tentativa |
| `autonomo` | a pergunta vira suposição em `decisions/SUPOSICOES.md`; você aprova o PRD, o PLAN (plano macro) e o ARCH (arquitetura), os contratos da onda de desenho e a entrega |

O `/bkhar:mode autonomo` só troca o modo quando `scripts/readiness.py` concede: canônico, PRD,
PLAN e grafo (`outputs/GRAPH-{projeto}.json`) aprovados, ARCH e modelos aprovados e em dia, sem
questão em aberto, e a stack no perfil.
Daí o `/bkhar:loop --wave N` roda as ondas do grafo: desenho, construção, front e integração. Cada
onda tem até 4 tasks em paralelo, cada uma na sua worktree, e uma task só começa quando o que ela
consome está aprovado.

Nenhum modo afrouxa os guardas, o teste escrito antes do código, as 4 tentativas, a proibição de
push na `main` e o `security` em área sensível.

O painel acompanha a execução e conversa com ela:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py .     # http://127.0.0.1:8765
```

Ele mostra as ondas, as tasks e as tentativas ao vivo, os bloqueios, o modelo de cada papel e o
consumo por modelo, agente e dia. Por ele você responde a um bloqueio, pausa ou retoma a onda,
deixa mensagem para a próxima tentativa e troca o modelo de um papel. Tudo vira pedido em
`outputs/run/inbox/`, que o orquestrador aplica no próximo ponto de controle. O painel escuta só em
`127.0.0.1` e não escreve estado.

O modelo de cada papel vem do frontmatter do agente; o mapa `models` do `.bks-profile.json`
sobrescreve por projeto.

#### Equipe em terminais do Maestri

O [Maestri](https://www.themaestri.app) é um aplicativo de área de trabalho para agentes: um
canvas com terminais de agente, notas e conexões, operado pela CLI `maestri`. Com ele, cada papel
da equipe roda no próprio terminal, e você acompanha todos trabalhando ao mesmo tempo, em vez de ver
só o resultado dos subagentes. O Gerente do harness continua no comando: o Maestri mostra e
transporta, e a memória segue nos arquivos do projeto. Testado com o Maestri 0.30.1 para Windows.

Em beta: a integração ainda está em prova num projeto piloto. O passo a passo completo, da
montagem do canvas aos exercícios, está no guia:
[`docs/artefatos/maestri/guia-maestri.html`](docs/artefatos/maestri/guia-maestri.html).

A integração é opcional e vale por projeto. No terminal `manager`, `/bkhar:maestri on` grava o
bloco `maestri` no `.bks-profile.json` e confere se os terminais existem com os nomes do mapa;
`/bkhar:maestri off` desliga e guarda o mapa. Desligada, tudo roda como fora do Maestri.

Ligada, cada papel roda no próprio terminal, criado a partir de uma partitura salva por você:

| Terminal | Comando |
|---|---|
| `manager` | `claude` (ou `bkhar`, para outro provedor) |
| `architect`, `developer`, `tester`, `quality`, `security`, `scribe` | `claude --agent bkhar:<papel>` |
| `ops` (executor) | `claude --model opus` |

Cada terminal se conecta só ao `manager`. O Gerente fala com os papéis por `maestri ask` e limpa a
sessão com `/clear` antes de cada rito. Papel sem terminal conectado cai para subagente. O Maestro
Mode fica desligado.

Os comandos `arch`, `prd` e `plan` rodam delegados no `architect`, e `canonize`, `save` e
`maintainability`, no `ops`. O `architect` tem Bash limitado pelo guarda
`hooks/scripts/architect_bash.py`: scripts do plugin, `git` de leitura e `maestri ask`.

Você chama os comandos no `manager`. Ele entrega o contexto da sessão por arquivo
(`outputs/run/handoff/`), repassa a você toda pergunta do terminal delegado e devolve o resultado.
Você só fala com o `manager`.

O andamento aparece na nota `status` do canvas e na barra lateral (`floor status`):

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .
```

O `/bkhar:loop` e o `/bkhar:save` rodam esse comando sozinhos. Ele regera
`outputs/run/status-canvas.md` a partir do `STATUS.md` e do estado das ondas e, no Maestri, copia o
texto para a nota. O arquivo fica fora do git do projeto. Decisões em `decisions/ADR-009` e
`decisions/ADR-010` e `decisions/ADR-011`.

O aprendizado volta como candidato: cada correção sua vira proposta em `inbox/proposals/`, o
`/bkhar:save` a leva ao vault com filtro de dado pessoal e segredo, e só o `/bkhar:retro` a promove
a regra. O `/bkhar:harvest` consolida no vault as decisões de todos os projetos.

#### Arquitetura e biblioteca do projeto

A arquitetura é portão nos dois modos: `prd → plan → arch (aprovado) → refine/spec`. O `/bkhar:arch`
escreve o índice `docs/library/architecture/ARCH-{projeto}.md` e um modelo por arquivo em
`models/` (C4, dados, sequências, fronteiras sensíveis, implantação), desenhados pela notação da
`bks-arch` no motor do perfil, todos em `status: rascunho`. Sem ARCH e modelos aprovados, o
`/bkhar:refine` e o `/bkhar:spec` não começam, e a prontidão do `autonomo` recusa.

Os modelos são artefatos vivos. Cada um declara `atualizado` e, opcionalmente, `fontes`; ADR,
contrato ou PLAN mais novo o deixa defasado. O `/bkhar:save`, o `/bkhar:brain` e o fim de cada onda
avisam, e o `/bkhar:arch --update` refaz só o que ficou para trás.

A biblioteca cataloga por referência tudo o que o projeto produziu — canônicos, arquitetura,
contratos, specs, decisões, ilustrações, histórico — e apresenta no dashboard estático
`docs/library/site/index.html`, com os diagramas renderizados e a linha do tempo das specs e do
diário. O `/bkhar:library export` leva a biblioteca para `knowledge/wiki/projetos/{projeto}/` do
vault, com o mesmo filtro de dado sensível do harvest:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py index|stale|build|export .
```

#### Agentes

| Agente | Papel | Modelo |
|---|---|---|
| `architect` | Guarda o padrão; escreve especificação, tasks e registros de decisão; nunca código de produção | Opus |
| `tester` | Escreve os cenários e o teste que falha antes do código; confere a cobertura | Sonnet |
| `developer` | Implementa uma tentativa do loop por vez contra os testes que falham; não commita | Sonnet |
| `security` | Revisão de segurança independente, só leitura, todo achado com `arquivo:linha` | Opus |
| `quality` | Legibilidade, arquivos de teste e resultados; devolve casos para o `LEARNINGS.md` | Sonnet |
| `scribe` | Registra apenas o que foi confirmado com evidência | Haiku |

### Perfis de projeto

Um projeto declara **o que gera**, e o perfil determina quais fases se aplicam. Um projeto de
documentação não recebe pergunta sobre banco de dados; uma biblioteca não passa por design de tela.

| Perfil | Para |
|---|---|
| `docs` | entrega documental — escopo, arquitetura, apresentação |
| `fullstack` | projeto completo faseado |
| `frontend` | design, mocks, componentes |
| `backend` | API, domínio, persistência |
| `component` | biblioteca, SDK, pacote |
| `infra` | IaC, pipeline, observabilidade |
| `data` | ETL, modelagem, BI |
| `legacy-docs` | entender um legado sem altera-lo |
| `reengineering` | documentar e reescrever um legado |

Quatro eixos atravessam os perfis: formato de saída (`md`/`html`), renderer de arquitetura,
alvo de frontend (`web`/`mobile`/`both`) e rigor (`producao`/`poc`).

O `/bkhar:new-project` grava a escolha em `.bks-profile.json`. Detalhes em
[`profiles/`](profiles/README.md).

### Guardas

O kit instala cinco hooks. Os três primeiros **recusam a escrita** quando a regra e violada — a
razão volta no próprio bloqueio, para corrigir e repetir. O `writing_guard` não recusa: a escrita
acontece, e os achados voltam ao agente para correção na mesma passada.

| Guarda | Quando dispara | O que recusa |
|---|---|---|
| `no_dispatcher` | escrita em `.cs` | `MediatR`, `IMediator`, `ISender`, `IRequestHandler<>`, `AddMediatR` e equivalentes — a orquestração BKS e explicita, via `PipelineOrchestrator` |
| `comment_budget` | escrita em `.cs` | bloco de comentario acima de 5 linhas, e marca de severidade em comentario |
| `dod_docs` | escrita em `.cs` que declara tipo público | a escrita, enquanto `README.md` e `ARCHITECTURE.md` não tiverem sido tocados na mesma leva |
| `writing_guard` | depois da escrita em `.md` de documentação viva | nada — devolve ao agente ADR fora da nota de decisão, frase acima de 40 palavras, sigla sem definição, muleta e emoji do trecho escrito, e lembra o usuário de rodar o `/bkhar:review` |
| `session_memory` | inicio de sessão | nada — carrega o `STATUS.md` do projeto, ou o perfil do usuário na raiz do vault, e avisa quando o `STATUS.md` é mais antigo que o último commit ou a última entrada do `JOURNAL.md` |

Os guardas de código ignoram arquivo de teste, arquivo fora de repositório git e qualquer coisa
que não seja `.cs`. O `writing_guard` ignora `STATUS.md`, `JOURNAL.md`, `CLAUDE.md`, ADR,
`CONTEXT*.md`, `docs/prompts/`, `docs/history/`, `docs/input/` e instrução de agente (`skills/`,
`commands/`, `agents/`). Ele também roda como linha de comando sobre arquivos inteiros:
`python hooks/scripts/writing_guard.py <arquivo.md>`, com saída 1 quando há achado. Falha interna de um guarda libera a escrita: regra que quebra o fluxo por bug próprio
deixa de ser usada em uma semana.

Rodar os testes dos guardas:

```
bash hooks/tests/run.sh
```

Os guardas exigem `python` no PATH.

### Verificação

Duas suites, que respondem a perguntas diferentes.

**Estrutural** — o arquivo continua integro depois que mexeram nele? Frontmatter, referência que
resolve, comando documentado que existe, guarda declarado que compila. Roda sem modelo:

```
python tests/test_structure.py
bash hooks/tests/run.sh
```

Os scripts têm suíte própria, uma por script: `python tests/test_<script>.py` (`readiness`,
`wave_graph`, `run_state`, `dashboard`, `learning`, `harvest`, `library`).

**Comportamental** — a skill ainda decide certo? Recusa MediatR, mantém o projeto de testes em
`src/`, pergunta antes de assumir. Roda o agente de verdade, com braco baseline sem o plugin para
medir o delta:

```
claude plugin eval .
```

Os casos estão em `evals/`. As duas se complementam: a estrutural pega o refactor que quebrou o
arquivo, a de eval pega o refactor que manteve o arquivo valido e perdeu a regra.

### Configuração

Os comandos de workbench (`/bkhar:brain`, `/bkhar:save`, `/bkhar:new-project`, `/bkhar:note`, `/bkhar:canonize`, `/bkhar:prd`,
`/bkhar:review`) operam sobre um vault de projetos. Aponte-o por variavel de ambiente:

| Variavel | Aponta para | Exemplo |
|---|---|---|
| `BKS_VAULT` | Raiz do vault | `C:/dev/2brains` |
| `BKS_KNOWLEDGE` | Base de conhecimento transversal | `${BKS_VAULT}/knowledge` |

São duas. Cada projeto guarda sua própria memória, decisão e domínio — não há hub central a
apontar.

As skills (`bks-sdd`, `bks-dotnet-solutions`, `bks-typescript-solutions`, `bks-go-solutions`,
`bks-create-plan-tasks`, `bks-tests`, `bks-standards`, `bks-arch`, e as sete importadas)
funcionam sem nenhuma configuração — operam sobre o diretório de
trabalho atual.

### O ciclo, em uma passada

```
/bkhar:new-project   cria a estrutura
/bkhar:note          material bruto entra
/bkhar:canonize      vira contexto canônico
/bkhar:prd           vira PRD
/bkhar:plan          vira plano macro e grafo de tasks
/bkhar:arch          vira arquitetura: ARCH + modelos, para aprovar (portão)
/bkhar:refine        vira FEAT + TEST apoiada nos modelos (ou /bkhar:spec, sem rito)
                   (ou a skill bks-sdd, para o ciclo com workspace e plano macro)
/bkhar:loop          implementa task sob goals
/bkhar:review        revisão independente
/bkhar:maintainability  parecer por aplicação e fundamentação
/bkhar:library       catálogo, dashboard e exportação para o vault
/bkhar:save          registra decisões e progresso, regera a biblioteca
```

### `/bkhar:spec` ou a skill `bks-sdd`?

Os dois especificam, em escalas diferentes.

**`/bkhar:spec`** vai direto ao FEAT e ao TEST, dentro do repositório. É o caminho padrão para uma
feature que você já entende, num projeto que já existe.

**A skill `bks-sdd`** é o ciclo completo, com PRD, plano macro e decomposição em tasks, mantendo
estado entre sessões num `workspace-*/`. Vale quando o produto é novo e grande, ou quando o
escopo é incerto e precisa de decomposição formal.

| Flag | Para que |
|---|---|
| `/bks-sdd` | cria o `workspace-[nome]/` |
| `--prd` | gera o PRD a partir do que está em `research/` |
| `--project` / `--project-prd` / `--project-plan` | projeto interno, seu PRD e seu plano de fases |
| `--feature` / `--feature-tests` / `--feature-task` | FEAT, depois TEST, depois as tasks |
| `--feature-list` / `--task-list` / `--status` | o que existe e onde parou |
| `--impl-init` / `--task-done` | executa e fecha task |
| `--continue` / `--tan` / `--clear` | retoma, ou encerra salvando o estado |
| `--cost` / `--cost-report` | consumo da sessão e do ciclo |

As etapas não se pulam: `--feature-tests` só roda com FEAT aprovado, `--feature-task` só com TEST
aprovado. É a mesma regra do `/bkhar:spec`, aplicada a um ciclo maior.

### Arquitetura de agentes

O `bkhar` trabalha com uma equipe de sete papéis. Seis são subagentes; o sétimo, o Gerente, é a
sessão principal seguindo a skill `bks-team`, porque subagente não conversa com você no meio do
trabalho nem chama outro subagente. Cada papel tem **as ferramentas do seu trabalho, e só elas**: a
restrição é o desenho, não uma economia.

| Papel | Tipo | Modelo | Ferramentas | O que a restrição impede |
|---|---|---|---|---|
| Gerente | orquestrador | sessão principal | as da sessão | não opina sobre técnica nem escolhe entre agentes |
| `architect` | consultivo | Opus | leitura + escrita, `Bash` limitado por guarda | roda só os scripts do plugin, `git` de leitura e `maestri ask`; escreve especificação e decisão, nunca código |
| `tester` | validador | Sonnet | leitura + escrita + `Bash` | escreve só teste; não revisa os próprios testes |
| `developer` | implementador | Sonnet | leitura + escrita + `Bash` | não commita, não mexe no teste do `tester`, não revisa o próprio código |
| `security` | validador | Opus | **só leitura** | não conserta o que julga; achado vira relato, não commit |
| `quality` | validador | Sonnet | **só leitura** | não conserta o que julga; devolve o defeito resolvido como caso |
| `scribe` | consultivo | Haiku | leitura + escrita | registra o que foi confirmado; não decide o que foi feito |

Quatro consequências desse arranjo:

**Quem escreve o teste não é quem faz o teste passar.** No `/bkhar:loop`, o `tester` escreve o
teste que falha antes da primeira tentativa, e o `developer` implementa contra ele. Na revisão, o
`tester` confere só a cobertura dos cenários; a qualidade dos testes é julgada pelo `quality`.

**A revisão é independente porque não pode agir.** `security` e `quality` sem `Write` não têm como
transformar um achado em correção silenciosa. Quem revisa não conserta; quem conserta não aprova o
próprio conserto.

**O modelo acompanha o julgamento exigido.** Opus onde se julga: segurança e arquitetura, porque
spec errada contamina toda task abaixo dela. Sonnet onde se executa e se confere. Haiku onde se
transcreve evidência.

**A decisão é sua.** Num painel, cada agente responde sem ver os outros, o Gerente numera as
posições e você escolhe; o `scribe` grava a decisão com as opções descartadas.

Os ritos têm comando próprio: `/bkhar:ask` (pergunta a um agente), `/bkhar:panel` (decisão),
`/bkhar:refine` (perguntas antes da especificação) e `/bkhar:review` (revisão em painel). O agente
também pode ser chamado pelo nome, `bkhar:<agente>`. O `@agente` no prompt não serve: no Claude
Code, `@` é menção de arquivo.

Defeito detectado e resolvido, com evidência, vira caso no `LEARNINGS.md` do projeto: o `quality`
identifica, o `/bkhar:save` grava e o `tester` lê os casos da área antes de escrever teste novo.

### Kit e vault, juntos

O kit funciona sozinho — skills, comandos e guardas não leem nada de fora. O que o
[vault](https://github.com/fabiobackside-code/bks-2brains) acrescenta é **memória entre
projetos**, e é daí que vem o ganho maior.

| | Sem vault | Com vault |
|---|---|---|
| Padrão de código | o que o modelo lembra do treinamento | `workbench/` diz como *você* trabalha |
| Decisão técnica | recomeça a cada projeto | `knowledge/wiki/` guarda o que você já concluiu |
| Erro conhecido | repete até doer de novo | registrado, com o sinal que teria avisado |
| Contexto de sessão | o que couber no prompt | `STATUS.md` do projeto, lido pelo `/bkhar:brain` |

#### Por que consome menos

Não é promessa, é mecânica — e é medível no próprio kit:

**Progressive disclosure.** As skills somam 4.584 linhas de entrada e 12.455 em `references/` —
razão de 2,7×. A referência só entra no contexto quando a tarefa a exige. A `bks-tests` carrega
93 linhas e mantém 1.847 disponíveis.

**Estado fora da sessão.** `STATUS.md` e `JOURNAL.md` guardam onde o projeto parou. Retomar custa
a leitura de um arquivo, não a reconstrução do histórico a cada abertura.

**Conhecimento sob demanda.** O acervo do vault é consultado quando a pergunta o exige. Cinquenta
páginas curadas custam menos que quinhentas linhas de instrução carregadas sempre.

#### Por que alucina menos

**A resposta cita fonte que existe.** Quando o agente consulta `knowledge/wiki/`, a afirmação tem
origem conferível em `knowledge/raw/`. O que ele "lembra" do treinamento não tem.

**Os guardas recusam, não avisam.** Um hook que bloqueia a escrita errada não depende de o agente
ter lido a regra. Aviso é sugestão; recusa é garantia.

**A spec precede o código.** FEAT e TEST aprovados antes de implementar dão critério de aceite
verificável. Sem isso, "pronto" é opinião.

O que isto **não** resolve: se a sua wiki estiver errada, o agente erra com confiança e com
citação. Por isso `raw/` é imutável e a página curada tem estado — para dar como conferir de onde
a conclusão veio.

> Os 18 casos de eval do kit medem se cada skill muda a decisão do agente. A baseline com o delta
> entre os braços `with` e `without` ainda não rodou; até lá, o que está escrito aqui é mecanismo,
> não número medido.

### Idioma

Documentação e artefatos gerados em **PT-BR**. Código, nomes de tipo, método e variavel em
**inglês**.

### Licenca

MIT — veja [LICENSE](LICENSE).
