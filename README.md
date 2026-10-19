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

## O kit (base 0.7.0, agora `bkhar` 0.8.0)

Plugin do Claude Code com o kit BKS de **Spec-Driven Development** — o processo que leva uma ideia
de produto até código implementado, passando por PRD, planos, especificações de feature, cenários
de teste e tasks executáveis.

Não e um framework de código. É o processo de trabalho: skills que conduzem o ciclo, comandos que
operam o workbench e agentes com papéis separados.

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

### O que vem no kit

#### Skills

| Skill | Para que serve |
|---|---|
| `bks-sdd` | Ciclo SDD completo: workspace, PRD, projetos, plano macro, feature specs, cenários de teste, tasks e execução |
| `bks-dotnet-solutions` | Geração de soluções .NET com Arquitetura Hexagonal e o padrão TXC (Transaction Context) |
| `bks-typescript-solutions` | Backends Node.js + TypeScript: API REST, agente LangGraph, worker e consumer, também sob TXC |
| `bks-go-solutions` | Soluções Go: API REST, worker, consumer, CLI e SDK — TXC na forma que Go admite, erro idiomático no lugar de `Result[T]` |
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
| `/bkhar:spec` | Entrevista de bounded context e gera `FEAT` + `TEST` |
| `/bkhar:arch` | Gera `ARCH-[projeto].md` (C4 em Mermaid) e o README do repo |
| `/bkhar:loop` | LOOP-4: implementa task sob goals verificáveis, máximo 4 tentativas |
| `/bkhar:review` | Dispara revisão independente read-only |
| `/bkhar:maintainability` | Inventaria `app/`, gera um parecer de manutenibilidade por aplicação em `outputs/maintainability/` e a fundamentação do projeto em `outputs/references/` |
| `/bkhar:save` | Roteia o resultado da sessão pela regra dos dois lugares |
| `/bkhar:migrate` | Traz um projeto do `bks` para o `bkhar`: confere o layout, troca o prefixo no `WORKFLOW.md` e no `CLAUDE.md`, grava o `.bkhar.json`; não commita |

#### Agentes

| Agente | Papel | Modelo |
|---|---|---|
| `planner` | Escopo vira `FEAT`/`TEST`/`TASK` — nunca código de produção | Opus |
| `builder` | Implementa sob LOOP-4, dentro dos limites da FEAT aprovada | Sonnet |
| `reviewer` | Revisão de segurança independente, read-only | Opus |
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
| `session_memory` | inicio de sessão | nada — carrega o `STATUS.md` do projeto, ou o perfil do usuário na raiz do vault |

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
/bkhar:spec          vira FEAT + TEST
                   (ou a skill bks-sdd, para o ciclo com workspace e plano macro)
/bkhar:loop          implementa task sob goals
/bkhar:review        revisão independente
/bkhar:maintainability  parecer por aplicação e fundamentação
/bkhar:arch          consolida a visão de arquitetura
/bkhar:save          registra decisões e progresso
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

Os quatro agentes não são o mesmo trabalhador com nomes diferentes. Cada um tem **as ferramentas
do seu papel, e só elas** — a restrição é o desenho, não uma economia.

| Agente | Modelo | Ferramentas | O que a restrição impede |
|---|---|---|---|
| `planner` | Opus | leitura + escrita, sem `Bash` | não executa nada; escopo vira FEAT/TEST/TASK, nunca código |
| `builder` | Sonnet | leitura + escrita + `Bash` | implementa sob LOOP-4, dentro dos limites de uma FEAT aprovada |
| `reviewer` | Opus | **só leitura** | não conserta o que julga — achado vira relato, não commit |
| `scribe` | Haiku | leitura + escrita | registra o que foi confirmado; não decide o que foi feito |

Três consequências desse arranjo:

**A revisão é independente porque não pode agir.** O `reviewer` sem `Write` não tem como
transformar um achado em correção silenciosa. Quem revisa não conserta; quem conserta não aprova
o próprio conserto.

**O modelo acompanha o julgamento exigido.** Opus onde se julga — segurança no `reviewer`,
arquitetura no `planner`, porque spec errada contamina toda task abaixo dela. Sonnet onde se
executa spec aprovada. Haiku onde se transcreve evidência. Pagar Opus para registrar o que já foi decidido é desperdício; pagar Haiku
para julgar risco é imprudência.

**O papel é invocado, não assumido.** O `reviewer` roda em invocação separada de quem
implementou, sem o estado da sessão que produziu o código. Um agente que revisa o próprio
trabalho na mesma sessão carrega as premissas que o levaram ao defeito.

Invoque pelo nome: `bkhar:reviewer`, `bkhar:planner`, `bkhar:builder`, `bkhar:scribe`. O `/bkhar:review`
dispara o `reviewer` com o contexto certo.

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
