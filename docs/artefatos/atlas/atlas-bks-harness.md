# Atlas do BKS Harness — Manual da Equipe de Agentes

Oct 18, 2026 · @Fabio Magalhaes

Versão 2.0.1, revisada contra o `bkhar` 3.0.1. A 2.0.0 reescreve o Atlas sobre o que existe no repositório: guias e sensores, o plugin como arquitetura, a equipe em terminais do Maestri, o `/bkhar:tasks`, a recuperação da task, o registro de regras, a deriva, a medição e o caminho real das versões. O que não existe sai marcado como *proposto*. O histórico de versões está no Apêndice F.

## Prefácio

Este manual descreve o BKS (Backside) Harness: uma equipe de sete papéis, seis agentes e o Gerente, que trabalha com você, conversa com você e faz o seu padrão de desenvolvimento crescer a cada projeto. Ele não é uma ferramenta de vibe coding. O código é consequência de conversas, decisões registradas e verificações executadas.

O harness nasceu de dois projetos. O **2brains** (`${BKS_VAULT}`, template público em `bks-2brains`) é o vault: guarda o que atravessa projetos. Ali ficam quem você é (`workbench/`), o que você aprendeu (`knowledge/`) e os projetos em `repos/{backside|w3|private}/`, cada um com git e memória próprios. O **BKS kit** (`bks-sdd-kit`, plugin `bks` 0.7.0) era a ferramenta: 17 skills, 12 comandos `/bks:*`, quatro agentes, guardas em `hooks/` e 20 casos de eval.

O harness é esse kit evoluído e rebatizado `bkhar`, sobre o mesmo vault. Na 3.0.1 ele tem 19 skills, 25 comandos `/bkhar:*`, seis agentes, oito guardas, 48 regras registradas e 28 casos de eval. Nenhum comando lê o vault para funcionar: cada projeto segue autossuficiente.

**Para quem é.** Para você, como arquiteto e dono do padrão. E, mais adiante, para a sua equipe de devs júnior e pleno, que podem trabalhar com os mesmos agentes e o mesmo padrão.

**Como ler.** Fundamentos e Arquitetura explicam o porquê e a estrutura. Equipe, Ritos e Aprendizado são o coração: quem trabalha, como dialoga e como aprende. Fluxo e comandos é a referência. O case mostra tudo funcionando. Implantação conta o caminho até aqui e o que vem depois. Evolução mostra como o harness cresce com skills novas. O Manual de comandos detalha cada comando. Os apêndices trazem templates e o histórico de versões.

Três documentos completam este: o guia para quem chega (`docs/artefatos/guia/`), que explica o desenho por pergunta; o treinamento (`docs/artefatos/treinamento/`), que ensina a instalar e usar; e o `docs/ARCHITECTURE.md`, com o porquê de cada decisão.

**Convenções.** Docs em PT-BR; código e comandos em inglês, com o prefixo `bkhar`. Item marcado como *proposto* não existe no repositório; o plano dele está no `docs/planejamento/harness-portavel/00-plano.md`.

## Parte I — Fundamentos

Um agente confiável é um modelo envolvido por um harness. O modelo raciocina. O harness decide o que ele vê, o que ele pode fazer, quando ele para e quem confere o resultado.

### 1. O problema

Sem estrutura, programar com IA (inteligência artificial) falha de três formas recorrentes:

- **Amnésia.** Não há memória entre sessões. Você reexplica contexto, padrão e decisões a cada conversa.
- **Suposição.** Onde falta fonte de verdade, o modelo preenche com chute. É daí que vem a alucinação de arquitetura.
- **Autoaprovação.** Quem implementa também declara que terminou. Ninguém executa a prova de que funciona.

A resposta não é um prompt melhor. É a estrutura em volta do modelo.

### 2. Guias e sensores

O vocabulário vem do artigo *Harness Engineering*, de Birgitta Böckeler. O harness controla o agente de dois jeitos:

- **Guia** age antes: é a instrução que o agente lê para não errar. Skills, comandos, agentes, templates e o `CLAUDE.md` do projeto.
- **Sensor** age depois: confere o resultado e devolve o erro que o guia não evitou. Pode ser **computacional**, um script determinístico que não gasta crédito, ou **inferencial**, outro agente que julga.

Quando o sensor computacional recusa a ação em vez de avisar, ele vira **trava**. O `no_dispatcher` é trava: a escrita de `using MediatR;` num `.cs` não acontece. O `writing_guard` é sensor de aviso: devolve os achados do texto e deixa a correção com o agente.

O harness cuida de cinco coisas, e cada uma tem peça própria:

| Responsabilidade | Pergunta que responde | No BKS Harness |
| --- | --- | --- |
| Contexto | O que entra na janela? | `STATUS.md` do projeto, canônico, specs aprovadas, corpo das skills; o detalhe fica em `references/` |
| Ferramentas | O que o agente pode executar? | as ferramentas do Claude Code, limitadas por papel e pelos guardas de `hooks/` |
| Fluxo | Em que ordem e com que portões? | os comandos `/bkhar:*`, cada um recusando começar sem o artefato aprovado da etapa anterior |
| Verificação | Quem prova que funcionou? | guardas e testes de arquitetura (computacionais); `tester`, `quality` e `security` (inferenciais) |
| Observação | Quanto custou e onde falhou? | `session_cost.py`, `METRICAS.md` por fase da task, `audit.py` e o delta dos evals |

### 3. O vault e o projeto

O **vault** guarda o que atravessa projetos. `workbench/` é o que é seu: `profile.md` (quem você é e como trabalha) e `decisions/` (ADRs sobre o processo, não sobre um projeto). `knowledge/` é o que você aprendeu, no padrão de wiki mantida por modelo de linguagem (LLM), o LLM Wiki do Karpathy: fontes imutáveis em `raw/`, páginas curadas em `wiki/`, catálogo em `index.md` e registro em `log.md`. Ela é alimentada pelo `/bkhar:ingest` e pelo `/bkhar:harvest`. Regra de ouro: antes de decidir arquitetura ou padrão, consulte a wiki e cite a página; o incerto vira `> [!uncertain]`, nunca chute.

O **projeto** é autossuficiente: abrir o repositório dá acesso a tudo que ele precisa. Cada um nasce com:

- `STATUS.md` (onde parei, o que trava, próximo passo), `WORKFLOW.md` e `JOURNAL.md` (marcos, do mais recente ao mais antigo);
- `.bks-profile.json` (perfil, eixos, modo de condução e o bloco opcional do Maestri);
- `brain/domain/` (o que o produto é) e `brain/engineering/` (como se constrói aqui);
- `decisions/`, `specs/{features,tests,tasks}/`, `docs/{input,design,canonical,history,library}/`, `outputs/` e `app/`.

O hub central `brain/_bks-ai/` do template público foi abandonado: um projeto só funcionava com ele por perto, e ele envelhecia sem que ninguém percebesse.

**Onde uma coisa nova vai.** Sobre você e vale para todo projeto → `workbench/`. Conhecimento geral, de mais de um projeto → `knowledge/`. O que um produto é → `{repo}/brain/domain/`. Como se constrói num projeto → `{repo}/brain/engineering/`. Decisão fechada de um projeto → `{repo}/decisions/`. Ferramenta, template, skill reusável → o plugin, nunca o vault.

### 4. O fluxo do 2brains: da pesquisa ao código

Nenhuma linha de código nasce sem contexto consolidado e spec aprovada. O fluxo tem duas fases.

**Fase pesquisa (sessão na raiz do vault, depois na raiz do projeto):**

1. `/bkhar:brain` na raiz do vault monta o panorama de todos os projetos a partir dos `STATUS.md` e diz qual tem trabalho pronto. Dentro de um projeto, lê só o `STATUS.md` dele.
2. `/bkhar:new-project` (único comando de projeto que roda no vault) cria `repos/{categoria}/{nome}/` com a estrutura canônica e grava o perfil em `.bks-profile.json`.
3. Você traz o material bruto para `docs/input/` e os rascunhos para `docs/design/`; `/bkhar:note` escreve notas vivas em `docs/input/notas/`.
4. `/bkhar:canonize` consolida tudo em `docs/canonical/CONTEXT.md`, com fontes citadas e `> [!uncertain]` nas divergências. A versão anterior vai para `docs/history/`.
5. `/bkhar:prd` gera o PRD (documento de requisitos do produto) em `docs/canonical/PRD-{projeto}.md`. Todo requisito rastreia para o `CONTEXT.md`.

**Fase código (raiz do repo do projeto):**

1. `/bkhar:plan` faz o plano macro e o grafo de tasks a partir do PRD aprovado.
2. `/bkhar:arch` elabora a arquitetura: o índice `ARCH-{projeto}.md` e um modelo por arquivo em `docs/library/architecture/`, desenhados pela `bks-arch`. É portão: sem o índice e os modelos aprovados, nenhuma feature começa, em nenhum dos dois modos.
3. `/bkhar:refine` (ou `/bkhar:spec`, sem rito) gera a feature (`specs/features/FEAT-*.md`) e, aprovada, o roteiro de teste, o TEST (`specs/tests/TEST-*.md`). Os dois saem com `**Status:** Aprovada`.
4. `/bkhar:tasks` decompõe a feature aprovada em `specs/tasks/TASK-[feature].md`: uma task por peça, cada uma com os cenários do TEST que ela cobre.
5. `/bkhar:loop T-NNN` implementa uma task sob LOOP-4, na branch `task/T-NNN`, com os guardas recusando escrita fora do padrão.
6. `/bkhar:review` revisa em painel; `/bkhar:maintainability` dá o parecer de manutenibilidade por aplicação de `app/`.
7. `/bkhar:save` fecha a sessão: decisões em `decisions/`, `STATUS.md` reescrito, marco no `JOURNAL.md`, alerta quando o canônico ou um modelo ficou mais velho que as decisões, e a medição de custo.

**A biblioteca do projeto.** `docs/library/` é a wiki do projeto: o catálogo `LIBRARY.md` lista, por referência, canônicos, arquitetura, contratos, specs, decisões e histórico, e o dashboard `site/index.html` mostra tudo com os diagramas renderizados. O `scripts/library.py stale` aponta o modelo que ficou para trás e o `/bkhar:arch --update` o refaz. O `/bkhar:library export` leva a biblioteca para `knowledge/wiki/projetos/{projeto}/` do vault, com o filtro de dado sensível do harvest.

&#91;embedded content: fluxo do 2brains · fase pesquisa e fase código\]

O `/bkhar:canonize` é o ponto em que o entendimento vira fonte única: a partir do PRD, a spec só cita `docs/canonical/` e a arquitetura aprovada. Quando uma decisão posterior contradiz o canônico, o `/bkhar:save` detecta e avisa.

**A skill `bks-sdd`.** Fora de um projeto `bkhar`, a skill conduz o mesmo método num workspace avulso, com PRD, plano, specs e memória de sessão. Dentro de um projeto, os comandos acima são o caminho; as tasks saem pelo `/bkhar:tasks`.

### 5. LOOP-4

Cada task tem no máximo quatro tentativas, contadas pelo `scripts/recovery.py`. Antes da primeira, o `tester` escreve o RED (o teste que falha antes do código), e o portão "RED confirmado" vira commit na branch `task/T-NNN`. A cada tentativa, o `developer` implementa e a sessão principal confere quatro goals:

- **goal 1 (G1):** build sem erro e sem warning novo;
- **goal 2 (G2):** testes 100% verdes;
- **goal 3 (G3):** cenários do TEST cobertos;
- **goal 4 (G4):** código fiel ao `brain/engineering/` do projeto.

Quando um goal falha, o erro real volta como contexto da próxima tentativa. Cada tentativa vira uma foto fora do histórico, em `refs/bkhar/T-NNN/impl-K`. Na quarta falha, o loop grava `outputs/BLOQUEIO-T-NNN.md` e só você destrava, com `/bkhar:loop T-NNN --resume`. Quinta tentativa, relaxar o goal ou marcar como concluído são proibidos. Se a sessão cai no meio, o mesmo `--resume` volta ao último ponto seguro, e a tentativa interrompida não conta.

&#91;embedded content: LOOP-4 · tentativa, gates, revisão ou decisão humana\]

A falha nunca é escondida: ou ela volta como contexto da próxima tentativa, ou chega até você.

### 6. Gates

Gate é uma verificação que a máquina executa, não uma opinião do modelo. Os oito guardas de `hooks/scripts/` rodam como hook do Claude Code, cada um com teste em `hooks/tests/`:

| Guarda | Quando | O que faz |
| --- | --- | --- |
| `secret_guard` | antes de ler, escrever ou rodar comando | recusa arquivo de segredo, credencial com valor real, remoção em massa, escrita fora do projeto e `reset --hard` fora de `task/*` |
| `architect_bash` | antes de Bash ou escrita | no papel `architect`, só scripts do plugin, `git` de leitura e `maestri ask`; escrita só em `specs/`, `decisions/`, `docs/` e `outputs/` |
| `no_dispatcher` | antes de escrever | recusa MediatR e equivalentes em C# |
| `comment_budget` | antes de escrever | recusa bloco de comentário acima de cinco linhas e marca de severidade |
| `dotnet_project` | antes de escrever | recusa FluentAssertions, solution nova em `.sln` e alteração de migration existente |
| `dod_docs` | antes de escrever | recusa tipo público novo sem `README.md` e `ARCHITECTURE.md` tocados na mesma leva |
| `writing_guard` | depois de escrever | devolve os achados de escrita da documentação; avisa, não recusa |
| `session_memory` | ao abrir a sessão | carrega o `STATUS.md` e avisa se ele ficou atrás do `JOURNAL.md` ou do git |

Os quatro guardas de código valem também antes do commit, pelo `scripts/precommit.py`, e no CI (integração contínua), que é uma casca fina sobre ele. Os esqueletos das três stacks geram ainda um teste de arquitetura junto com o código, que lê o código como texto e não traz pacote novo. Pronto significa gates verdes **e** revisão independente aprovada.

## Parte II — Arquitetura

O harness não é um programa com núcleo próprio. É um plugin do Claude Code: arquivos que o Claude Code lê (guias), scripts que ele roda (sensores e estado) e um lançador que troca o provedor do modelo. O motor de execução é o próprio Claude Code, e o `/bkhar:loop` é o único executor de tasks.

### 7. As três camadas

| Camada | O que é | Quem fornece |
| --- | --- | --- |
| Modelo | o raciocínio e a escrita | o provedor: Anthropic, DeepSeek ou OpenRouter |
| Harness da ferramenta | o laço de execução, as ferramentas de leitura e escrita, as permissões, os hooks | o Claude Code |
| Harness do usuário | o método: skills, comandos, agentes, guardas, scripts, perfis e templates | o plugin `bkhar` |

&#91;embedded content: as peças do bkhar · o que orienta, o que executa, o que confere\]

Trocar o provedor muda só a camada de cima, pelo lançador. Trocar o executor está fora da 3.0.0: é a portabilidade da 4.0.0, *proposta*.

### 8. Componentes

| Componente | Responsabilidade | Onde está |
| --- | --- | --- |
| Plugin `bkhar` | Empacota skills, comandos, agentes, guardas, perfis e templates numa instalação no escopo do usuário | `.claude-plugin/plugin.json` e `marketplace.json` |
| Gerente | Conduz os ritos, dá a vez a cada agente, expõe o conflito e para antes de gerar artefato | a skill `bks-team`, seguida pela sessão principal |
| Agentes | Os seis papéis, cada um com ferramentas e modelo próprios | `agents/*.md` |
| Skills | 19 guias carregados por gatilho, corpo curto e detalhe em `references/` | `skills/` |
| Perfis de projeto | Dizem quais fases, artefatos e skills se aplicam | nove perfis em `profiles/`, eixos no `.bks-profile.json` |
| Comandos com portões | Fases e portões; cada comando recusa começar sem o artefato aprovado | 25 comandos em `commands/` |
| Guardas | Recusam a ação fora do padrão, no hook, no pre-commit e no CI | `hooks/scripts/`, `scripts/precommit.py`, `scripts/install_guards.py` |
| Registro de regras | Liga cada regra à fonte que a enuncia e ao sensor que a confere | `rules.json`, com o relatório `docs/regras.md` |
| Recuperação da task | Branch, portões como commit, tentativas como foto, trava e retomada | `scripts/recovery.py` |
| Estado da execução em onda | Uma task por arquivo, com um escritor só | `outputs/run/`, escrito por `scripts/run_state.py` |
| Painel local | Acompanha ondas, tentativas, bloqueios e consumo; recebe sua interação | `scripts/dashboard.py` em `127.0.0.1`, escreve só em `outputs/run/inbox/` |
| Biblioteca do projeto | Catálogo, dashboard e exportação dos artefatos | `docs/library/`, gerada por `scripts/library.py` |
| Lançador e provedores | Troca o endereço e a chave do modelo no processo do `claude` | `scripts/bkhar.py`, `providers/`, chave cifrada pelo `scripts/keyvault.py` |
| Integração com o Maestri | Papéis em terminais, com queda para subagente, e comandos delegados | `scripts/maestri_config.py`, `scripts/status_note.py` |
| Aprendizado | Proposta candidata, promoção pelo usuário e consolidação no vault | `scripts/learning.py`, `scripts/harvest.py`, `inbox/proposals/` |
| Medição | Custo por sessão, métrica por fase da task, deriva e delta das skills | `scripts/session_cost.py`, `scripts/metrics.py`, `scripts/audit.py`, `evals/` |

### 9. Modelo por papel e provedor

O modelo de cada papel está no frontmatter do agente: Opus para `architect` e `security`, Sonnet para `developer`, `tester` e `quality`, Haiku para o `scribe`. A regra por trás: quem decide erra caro e usa o modelo mais forte; quem executa é protegido pelos gates e pode usar um mais barato. O mapa `models` do `.bks-profile.json` sobrescreve por projeto, e o Gerente passa o modelo em cada chamada.

O provedor entra pelo lançador `bkhar` (`decisions/ADR-006`). Os agentes declaram só o rótulo (`opus`, `sonnet` ou `haiku`), e o provedor ativo decide quem responde por cada um. O `providers/` guarda a definição de claude, deepseek e openrouter; a chave e o provedor ativo ficam fora do repositório, com a chave cifrada em AES-256-GCM (cifra autenticada) e a chave mestra no cofre do sistema operacional.

*Proposto:* revisor em fornecedor diferente do `developer`, para que os erros dos dois sejam menos correlacionados. Hoje o mapa é por rótulo, e todos os agentes de um rótulo seguem juntos.

### 10. Política de dados

O que o harness garante hoje é computacional:

- o `secret_guard` recusa ler arquivo de segredo e gravar credencial com valor real, no hook e antes do commit;
- o lançador limpa a `ANTHROPIC_API_KEY` do ambiente antes de apontar para um provedor de terceiro;
- o `learning.py export`, o `harvest` e o `library export` recusam levar ao vault o que tiver dado pessoal ou segredo;
- no modo `autonomous`, dado pessoal, autorização e segredo não se presumem: param em `BLOQUEIO`.

Projeto com área sensível ganha um manifesto em `{repo}/.claude/multiagente.md`, a partir do template `manifesto-projeto.md` do kit. O manifesto traz:
- os comandos de verificação;
- as zonas de contenção, que só a sessão principal edita;
- as áreas sensíveis, que exigem `/bkhar:review`;
- os invariantes do domínio.

O `/bkhar:review` lê o manifesto para dimensionar o painel.

*Proposto:* um policy engine que troque o provedor por zona sensível. Ele não existe. Hoje, em contexto bancário sob BACEN (Banco Central do Brasil) e LGPD (Lei Geral de Proteção de Dados), a escolha do provedor é sua, feita pelo lançador antes da sessão.

## Parte III — A Equipe

A equipe tem sete papéis, seis agentes e o Gerente, e cada um tem uma função, um limite e um conjunto de perguntas que sempre faz. Nenhum agente decide por você: eles aconselham, questionam e executam, mas a decisão é sua e fica registrada.

### 11. Visão geral

&#91;embedded content: a equipe · 6 agentes e o Gerente em 3 grupos\]

Quem revisa nunca é quem constrói, e quem decide é sempre você.

| Agente | Tipo (PBQ) | Papel | Pergunta que sempre faz | Modelo | Vem de (kit) |
| --- | --- | --- | --- | --- | --- |
| Gerente | Orquestrador | Conduz os ritos, consolida opiniões, cobra decisões | O que está pendente de decisão sua? | a sessão principal | Novo: skill `bks-team` |
| Arquiteto | Consultivo | Bounded contexts, padrões, FEAT, a lista de tasks (TASK) e ADR | Isso respeita o padrão ou pede exceção? | Opus | `planner` (FEAT, TASK) + `/bks:arch` |
| Dev | Implementador | Implementa e explica cada escolha | Qual alternativa descartei, e por quê? | Sonnet | `builder` + `/bks:loop` |
| Testes | Validador | Cenários, casos de borda, o RED antes do código | Qual cenário prova que isso está errado? | Sonnet | `planner` (TEST) + skill `bks-tests` |
| Segurança | Validador | AppSec, LGPD, BACEN, segredos | Que dado sensível passa por aqui? | Opus, só leitura | `reviewer` + `/bks:review` + `security-audit` |
| Qualidade | Validador | Clean Code, calisthenics, smells, manutenibilidade | Um júnior entende isso daqui a 6 meses? | Sonnet, só leitura | Novo (`bks-standards`, `bks-maintainability-review`) |
| Documentador | Consultivo | ADR, `STATUS.md`, `JOURNAL.md`, registro do verificado | O que aprendemos hoje que vale virar padrão? | Haiku | `scribe` + `/bks:save` + `bks-writing` |

Seis papéis são subagentes em `agents/`, com o modelo no frontmatter e o tier anunciado na primeira linha da resposta. O Gerente é a sessão principal seguindo a skill `bks-team`, porque só ela conversa com você no meio do trabalho. A equipe evoluiu dos quatro agentes do kit:
- o planner se dividiu em Arquiteto e Testes;
- o builder virou Dev, o reviewer virou Segurança e o scribe virou Documentador;
- Gerente e Qualidade entraram como papéis novos.

A coluna PBQ diz o tipo do papel no vocabulário do `bks-sdd`. As regras duras:
- o Dev não edita zona de contenção nem commita;
- a Segurança e a Qualidade só leem, e todo achado tem `arquivo:linha`;
- o Documentador nunca afirma teste sem evidência;
- o Arquiteto tem Bash, mas o guarda `architect_bash` o limita aos scripts do plugin, ao `git` de leitura e ao `maestri ask`, com escrita só em `specs/`, `decisions/`, `docs/` e `outputs/`.

**A equipe em terminais.** Com o Maestri ligado no projeto (`/bkhar:maestri on`), cada papel roda num terminal próprio, aberto com `claude --agent bkhar:<papel>`, e o Gerente fala com ele por `maestri ask`. Papel sem terminal conectado cai para subagente, pelo mesmo protocolo, e o harness segue inteiro fora do Maestri. Quem decide a rota de cada chamada é o `scripts/maestri_config.py` (`decisions/ADR-008` a `ADR-011`).

Os comandos que não chamam a equipe rodam noutro terminal, para não ocupar o Gerente:
- `arch`, `prd` e `plan` vão ao Arquiteto, porque são artefatos dele;
- `canonize`, `save` e `maintainability` vão ao executor `ops`, que só executa e não é papel.

Toda pergunta do terminal delegado volta como portão do Gerente: você decide num lugar só. O contexto passa por arquivo, em `outputs/run/handoff/`.

### 12. Os perfis

**Gerente.** É o mestre de cerimônias. Abre cada rito, decide quem fala, impede que a conversa avance sem uma resposta sua e resume os trade-offs em opções numeradas. Não opina sobre técnica: quando há conflito entre agentes, ele expõe o conflito, não o resolve. Fontes: `STATUS.md`, PRD, o plano macro (PLAN) e as decisões pendentes.

**Arquiteto.** Guarda o seu padrão: Hexagonal, DDD (desenho guiado pelo domínio) tático, TXC (Transaction Context) quando o projeto o adota e Result Pattern. Toda recomendação cita a regra ou a página da wiki que a sustenta. Quando uma decisão contradiz o padrão, ele exige um ADR. Escreve FEAT, TASK e ADR, e roda o `arch` e o `plan`. Fontes: skill `bks-standards`, `brain/engineering/` do projeto, `knowledge/wiki/architecture/`, os ADRs do projeto e as skills de stack e de arquitetura.

**Dev.** Implementa uma tentativa do LOOP-4 por vez, contra os testes que falham. Diferente de um vibe coder, ele explica: qual abordagem escolheu, qual descartou e por quê. Quando a spec é ambígua, ele para e pergunta antes de codificar. Fontes: FEAT, TEST, a task e as skills de stack.

**Testes.** Pensa como quem quer quebrar o sistema. Questiona a FEAT no refinamento, escreve o TEST e, no passo 0 do `/bkhar:loop`, o RED em código, antes do Dev. Não revisa os próprios testes. Fontes: TEST, critérios de aceite e os casos do `LEARNINGS.md` da área da task.

**Segurança.** Analisa cada FEAT e cada diff pelo ângulo de dado sensível, autorização, log, segredo e conformidade. Confere mascaramento e se a zona do manifesto foi respeitada. Fontes: manifesto, checklist de segurança, normas aplicáveis.

**Qualidade.** Revisa legibilidade, nomes, tamanho de função, comentários desnecessários e smells, sempre balanceando com custo real de performance. Pensa na sua equipe júnior e pleno como leitora do código. Julga também os testes que o Testes escreveu e os resultados da execução, e devolve o defeito resolvido como caso para o `LEARNINGS.md`. No `/bkhar:audit --deep`, procura contradição de sentido entre guias. Fontes: `bks-clean-code`, Object Calisthenics, catálogo de refactoring.

**Documentador.** Grava o ADR de cada painel logo depois da sua escolha e sincroniza a documentação do que já foi verificado. Fontes: tudo o que foi decidido e conferido na sessão.

### 13. Regras de convivência

1. **Toda opinião cita uma fonte.** Sua wiki, suas premissas ou uma referência primária. Opinião sem fonte vem marcada como tal.
2. **Ninguém aprova o próprio trabalho.** Quem implementa não revisa, e quem escreve o teste não é quem o faz passar.
3. **Conflito é exposto, não escondido.** Se Arquiteto e Dev discordam, você vê as duas posições.
4. **Na dúvida, pergunta.** Um agente que assume em vez de perguntar viola o perfil.
5. **Nada entra no cérebro sem você.** Agentes propõem; você aprova.

Competência nova chega por skill, não por reescrita do perfil (veja a Evolução, adiante).

## Parte IV — Ritos e diálogo

A equipe conversa com você em cinco formatos, cada um com começo, meio e fim. Os ritos substituem o "gera isso pra mim" por uma conversa com papéis claros.

| Rito | Comando | Quando | Quem participa | Termina com |
| --- | --- | --- | --- | --- |
| Refinamento | `/bkhar:refine` | Antes de cada FEAT | Gerente, Arquiteto, Testes, Segurança | FEAT e TEST aprovados por você |
| Painel | `/bkhar:panel` | Uma dúvida com mais de uma resposta razoável | Gerente + 2 ou 3 agentes | Sua decisão, registrada em ADR |
| Pergunta direta | `/bkhar:ask` | A qualquer momento | Um agente | Resposta com fonte |
| Revisão em painel | `/bkhar:review` | Depois de gates verdes | Testes, Segurança, Qualidade, Arquiteto | Aprovação ou novas tasks |
| Retrospectiva | `/bkhar:retro` | Quando há propostas candidatas | Você, sobre o que a equipe propôs | Cada proposta promovida ou rejeitada |

Nenhum rito grava `STATUS.md` nem `JOURNAL.md`: no fim, o Gerente lista o que o `/bkhar:save` grava. A exceção é o ADR do painel, que o Documentador grava logo depois da sua escolha.

### 14. Refinamento

O Gerente apresenta o pedido. Cada agente faz até três perguntas pelo seu ângulo. O Gerente agrupa as perguntas, você responde, e só então o Arquiteto escreve a FEAT com as suas respostas dentro. Aprovada, ela recebe `**Status:** Aprovada`, e o Testes escreve o TEST, que passa pela mesma aprovação. Uma FEAT que nasce sem refinamento, pelo `/bkhar:spec`, é exceção registrada no cabeçalho: `Refinamento: não (exceção)`. No `autonomous`, as perguntas viram suposições em `decisions/SUPOSICOES.md`.

### 15. Painel

Você faz uma pergunta aberta ("separação de leitura e escrita (CQRS) ou leitura direta aqui?"). Dois ou três agentes respondem em invocações separadas, sem ver a resposta um do outro: posição que viu a outra vira concordância. O Gerente apresenta as posições lado a lado, com prós, contras e fontes, numeradas como opções. Você escolhe, e o Documentador registra a decisão em ADR, com as opções descartadas.

### 16. Pergunta direta

Use `/bkhar:ask <agente> <pergunta>` para falar com um papel específico: `/bkhar:ask seguranca preciso mascarar esse campo no log?` O nome vale em inglês ou português. A resposta segue o perfil: cita a fonte e diz quando é opinião.

O atalho com arroba, previsto nas primeiras versões deste Atlas, não existe: no Claude Code, a arroba é menção de arquivo.

### 17. Revisão em painel

Depois que os gates passam, três revisores leem o diff em invocações separadas: Testes, Segurança e Qualidade. O Arquiteto entra quando o diff toca uma fronteira de contexto ou uma premissa. O manifesto do projeto (`.claude/multiagente.md`) diz que áreas exigem a Segurança. O Testes confere se cada cenário está coberto; a força dos testes é julgada pela Qualidade, porque quem escreveu o teste não o revisa. Cada achado vira um de três tipos:
- bloqueante, que vira proposta de task depois do seu ok;
- sugestão, que você decide;
- aprendizado.

Defeito resolvido, com evidência, vai para o `LEARNINGS.md` do projeto, que o Testes lê antes de escrever teste novo. A regra que só o julgamento confere sai numa rubrica, uma linha por regra, com veredito e `arquivo:linha`.

### 18. Retrospectiva

O `/bkhar:retro` mostra cada proposta candidata, com a evidência e a origem, e você decide o destino de cada uma: regra do projeto, do vault ou do kit, ou rejeição com motivo. As propostas chegam de três lugares: das suas correções durante o trabalho, dos ritos e das contradições que o `/bkhar:audit --deep` acha entre guias.

*Proposto:* uma rodada em que o Documentador pergunta a cada agente o que funcionou, o que travou e o que vale virar padrão.

### 19. O time também te provoca

A equipe não só responde: ela devolve perguntas sobre o seu padrão. Hoje isso acontece em dois pontos:
- o `/bkhar:save` avisa quando uma spec ou um ADR deixou o canônico para trás;
- o `/bkhar:audit --deep` acha dois guias que se contradizem e abre a proposta para você fechar.

*Proposto:* perguntas que leem o histórico de decisões, como estas:
- "Você decidiu isso três vezes sem ADR. Vira premissa?"
- "Você aceitou leitura direta duas vezes onde a premissa pede CQRS. A premissa está desatualizada?"

É assim que quem evolui é você, e não só o código.

## Parte V — O ciclo de aprendizado

O harness melhora porque o seu cérebro melhora, e o seu cérebro só muda com a sua aprovação. É isso que separa uma equipe que aprende de um modelo que acumula vícios.

### 20. O ciclo em quatro passos

1. **Observar.** Durante os ritos e o trabalho, cada correção sua, cada defeito resolvido e cada contradição achada entre guias conta.
2. **Propor.** O `scripts/learning.py propose` grava a proposta, uma por arquivo, em `inbox/proposals/` do projeto, com `status: candidata`, evidência e origem. O `/bkhar:save` a leva ao `inbox/proposals/` do vault e recusa a que tiver dado pessoal ou segredo.
3. **Curar.** Você revisa as candidatas com `/bkhar:retro`. Promove a regra do projeto (`brain/engineering/regras/`), do vault (`workbench/regras/`) ou do kit; ou rejeita, e ela vai para `archive/` com o motivo. Rejeitar também ensina.
4. **Incorporar.** A regra do projeto e a do vault passam a ser lidas na próxima sessão. A regra do kit entra pelo `learning.py apply`: vai para a seção `## Histórico de regras` do `SKILL.md` escolhido, com a proposta de origem, e fica com `eval: pendente` até o delta ser medido. Sem delta, ela sai.

&#91;embedded content: ciclo de aprendizado · 4 passos\]

O único passo que exige você é a curadoria; os outros três a equipe faz sozinha. Captura gravada direto como regra está recusada: suspeita viraria fato, e o agente passaria a citá-la.

**A contradição também é proposta.** O `/bkhar:audit --deep` junta os trechos de um tema e o Qualidade procura só contradição de sentido, com os dois `arquivo:linha`. Cada achado vira proposta `tipo: contradicao`, e só você a fecha: `resolve` quando o guia foi corrigido, `reject` com motivo. Entre 2026-11-14 e 2026-11-17, a rodada nos oito temas achou 36 contradições, todas corrigidas.

**A experiência de todos os projetos.** Na raiz do vault, o `/bkhar:harvest` indexa por script os ADRs e o `LEARNINGS.md` de `repos/` e do próprio kit, e consolida por tema em `knowledge/wiki/experiencia/`, com ponteiro para a origem.

**O `collaborative` treina o `autonomous`.** Cada correção que você faz no modo colaborativo vira candidata; promovida e medida, passa a valer quando o projeto roda sozinho.

### 21. Tipos de proposta

| Tipo | Destino ao ser aceita | Exemplo |
| --- | --- | --- |
| Regra de padrão | `skills/bks-standards/` (todo projeto) ou `brain/engineering/` (um projeto) | Máscara de CPF é responsabilidade do domínio |
| Regra de checklist | `skills/bks-team/references/` | Segurança: verificar log em nível Debug |
| Regra de skill | `## Histórico de regras` do `SKILL.md`, pelo `learning.py apply`, com eval pendente | Projeto de testes em `src/`, nunca em `tests/` |
| Contradição | o guia corrigido; a proposta fecha com `resolve` | Dois guias com ordens diferentes para os passos do TXC |
| Página de conhecimento | `knowledge/wiki/` do vault, via `/bkhar:ingest` | Resumo de um paper citado no painel |
| Template | `templates/` do plugin | Seção "Dados sensíveis" obrigatória na FEAT |
| Guarda | `hooks/scripts/` + teste em `hooks/tests/` | Domain não referencia Dapper |
| Sobre você ou o processo | `workbench/profile.md` ou `workbench/decisions/` | Preferência de revisão, ADR de processo |

### 22. Referências e fundamentos

Quando um agente traz um artigo, um livro ou um paper, ele não fica só na conversa. A proposta de ingestão, ao ser aceita, passa pelo `/bkhar:ingest` e vira página da wiki com link para a fonte primária. Com o tempo, as decisões passam a citar a **sua** wiki, e não a memória de treinamento do modelo.

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

Do escopo ao merge, cada etapa tem um dono, uma saída e um portão. O portão é um arquivo aprovado: o comando seguinte lê o registro de aprovação e recusa começar sem ele.

### 24. Fluxo de uma feature

| Etapa | Rito | Dono | Saída | Portão |
| --- | --- | --- | --- | --- |
| 1. Contexto da sessão | — | Gerente | `/bkhar:brain`: panorama ou STATUS do projeto | — |
| 2. Projeto | — | Você | `/bkhar:new-project` cria repo e perfil | — |
| 3. Entendimento | — | Gerente, Arquiteto | `docs/input/` → `/bkhar:canonize` → `CONTEXT.md` | Perguntas `[!uncertain]` respondidas |
| 4. Requisito | — | Arquiteto | `/bkhar:prd` → `PRD-{projeto}.md` | Sua aprovação |
| 5. Plano e arquitetura | — | Arquiteto | `/bkhar:plan` → PLAN e grafo; `/bkhar:arch` → índice de arquitetura (ARCH) e modelos em `docs/library/architecture/` | Sua aprovação do PLAN, do ARCH e de cada modelo |
| 6. Refinamento da feature | Refinamento | Gerente | Perguntas da equipe, apoiadas nos modelos, e suas respostas | Suas respostas |
| 7. FEAT | — | Arquiteto | FEAT com critérios e dados sensíveis | `**Status:** Aprovada` |
| 8. TEST | — | Testes | TEST com os cenários | `**Status:** Aprovada` |
| 9. Tasks | — | Arquiteto | `/bkhar:tasks` → `specs/tasks/TASK-[feature].md`, uma task por peça, cada uma com os cenários que cobre | Sua aprovação da lista; FEAT em `Em execução` |
| 10. Implementação | — | Testes, depois Dev | `/bkhar:loop T-NNN`: RED no passo 0, depois código e explicação das escolhas | RED confirmado; G1–G4; LOOP-4; guardas |
| 11. Revisão | Revisão em painel | Testes, Segurança, Qualidade | Achados com `arquivo:linha` | Sem crítica aberta |
| 12. Registro | — | Documentador | ADR, README, ARCHITECTURE.md, STATUS, JOURNAL, biblioteca regerada (`/bkhar:save`) | Modelo defasado vira aviso para o `/bkhar:arch --update` |
| 13. Aprendizado | Retrospectiva | Você | Propostas em `inbox/proposals/`, curadas no `/bkhar:retro` | Sua curadoria |

A task não vem em par Teste e Implementação: o RED é do Testes, no passo 0 do loop, e a task carrega os cenários que ele vai escrever. Todo cenário do TEST aparece em pelo menos uma task. Com o padrão TXC, as tasks seguem a ficha de cada transação, peça por peça.

### 25. Modos de condução

O projeto escolhe como é conduzido, em `axes.mode` do `.bks-profile.json`. O `collaborative` é o padrão; o `autonomous` é opcional e com limites.

| Onde | `collaborative` | `autonomous` |
| --- | --- | --- |
| `/bkhar:refine`, `/bkhar:spec` | os agentes perguntam e esperam você | o Arquiteto responde as próprias perguntas pelas fontes e grava cada resposta como suposição em `decisions/SUPOSICOES.md` |
| `/bkhar:tasks` | a lista espera a sua aprovação | a lista segue aprovada; cenário sem task para em `BLOQUEIO` |
| Portões seus | FEAT, TEST, a lista de tasks e cada tentativa | três: PRD, PLAN e ARCH aprovados; contratos da onda de desenho; entrega final |
| `/bkhar:loop` | decisão fora da FEAT para e pergunta | decisão fora da FEAT vira suposição; para só em `BLOQUEIO` |
| `/bkhar:review` | achados voltam para você | bloqueante volta ao loop; sugestão vai para o relatório da onda |
| Paralelismo | não | ondas em worktree |

**Prontidão.** O `/bkhar:mode autonomous` só troca o modo quando o `scripts/readiness.py`, sem chamar modelo, concede: CONTEXT revisado ou aprovado, PRD e PLAN aprovados, grafo válido, ARCH e modelos aprovados e em dia, nenhuma questão em aberto e a stack no perfil. A recusa lista o que falta por nível e o comando que resolve. A troca grava ADR; sem ADR, não houve troca.

**O que nenhum modo afrouxa:** os guardas de `hooks/`, build e testes verdes, o RED antes do código, o máximo de 4 tentativas, nada de push na `main` e a Segurança em área sensível. Dado pessoal, autorização e segredo não se presumem: param em `BLOQUEIO`. Em `rigor: producao`, os contratos da onda de desenho continuam com você.

### 26. Ondas e painel

O `/bkhar:plan` grava o grafo `outputs/GRAPH-{projeto}.json`. Cada task declara o que `consome`, o que `produz` e os `arquivos` que escreve. As ondas são calculadas, não declaradas: a task vem depois de quem produz o que ela consome, e só começa quando tudo o que consome existe com `status: aprovado`.

| Onda | Produz | Quem faz |
| --- | --- | --- |
| 0 · Contexto | canônico, PRD, PLAN, ARCH | você aprova |
| 1 · Desenho | contratos por lente: banco, API, infra, telemetria, ameaças | Arquiteto por lente, em paralelo; Segurança no modelo de ameaças |
| 2 · Construção | apps e serviços | LOOP-4 por task, cada uma na sua worktree |
| 3 · Front e integração | telas, testes de ponta a ponta | LOOP-4 por task |

O `/bkhar:loop --wave next` libera até 4 tasks simultâneas, cada uma na branch `wave/N/T-NNN`. No fim da onda, a sessão principal faz o merge das worktrees, roda build e suíte completos, chama o `/bkhar:review` sobre a onda inteira, confere a arquitetura viva e grava `outputs/run/onda-N/RELATORIO.md`. Conflito de merge para a onda; `BLOQUEIO` de uma task segura só a cadeia que depende dela.

O estado vive em `outputs/run/`, e só o orquestrador o escreve, pelo `scripts/run_state.py`, que recusa transição inválida: 5ª tentativa, task não liberada, execução pausada. O `/bkhar:status` mostra a tabela no terminal.

O painel acompanha e conversa com a execução:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py .     # http://127.0.0.1:8765
```

Ele mostra as ondas, as tasks e as tentativas ao vivo, os bloqueios, o modelo de cada papel e o consumo por modelo, agente e dia, e avisa pelo navegador quando uma task trava. Por ele você responde a um `BLOQUEIO`, pausa ou retoma a onda, deixa mensagem para a próxima tentativa e troca o modelo de um papel. Tudo vira pedido em `outputs/run/inbox/`, que o orquestrador aplica entre tentativas e entre tasks. Subagente em execução não recebe mensagem de fora, e o painel não finge controle em tempo real.

O `--wave`, o ramo `autonomous` e o painel com onda real ainda não rodaram num projeto: são da validação pós-3.0.0.

### 27. Travas e recuperação da task

A trava é o sensor computacional que recusa a ação antes que ela aconteça: o hook devolve a recusa, e a ferramenta não roda. Três travas seguram a task:

- **o `reset --hard`** só passa em `task/*` e `wave/*`. Na branch de trabalho, o `secret_guard` o recusa: voltar a um ponto ali levaria junto o que você commitou;
- **o teto de 4 tentativas** é contado pelo `recovery.py`, e o contador só sobe;
- **o terceiro bloqueio** da mesma task a devolve ao `/bkhar:refine`: aí o defeito está na especificação.

A fase é a da task: `spec → red → impl-K → review → integracao`. Portão e tentativa recebem tratamento diferente:
- **portão** (`spec`, `red`, `review`) é commit na branch da task e passa pelo pre-commit do projeto;
- **tentativa** é foto fora do histórico, em `refs/bkhar/T-NNN/impl-K`, montada num índice temporário sem tocar o seu.

O estado mora em `.git/bkhar/recovery/T-NNN.json`, fora da árvore e intocado pelo reset.

Na quarta falha, o `outputs/BLOQUEIO-T-NNN.md` traz o diagnóstico, o placar, as opções e a seção `## Retomada`. Você preenche o que mudou e roda `/bkhar:loop T-NNN --resume`; a retomada sem informação é recusada. Se a sessão cai, o mesmo `--resume` volta ao último ponto seguro, e a tentativa interrompida não conta. Duas quedas na mesma tentativa viram bloqueio.

A integração é `merge --no-ff`: a ordem `spec → red → review` fica no histórico como prova do método, e a task inteira se desfaz com um `revert -m 1`.

### 28. Regras, deriva e medição

**Toda regra tem registro.** O `rules.json` liga cada uma das 48 regras à fonte que a enuncia e ao sensor que a confere, computacional ou inferencial. O `scripts/rules_report.py` gera o `docs/regras.md` e recusa três defeitos:
- sensor fantasma, que aponta para arquivo inexistente;
- seção que sumiu da fonte;
- guarda órfão, que não verifica nenhuma regra.

Cinco regras não têm sensor; o relatório as lista, porque regra sem sensor é intenção, não garantia.

**A deriva é conferida em duas camadas.** O `scripts/audit.py` é computacional e roda na suíte. No kit, ele confere o registro e os parâmetros repetidos entre guia e sensor. No projeto, a cópia dos guardas, o CI e o `STATUS.md` contra o `JOURNAL.md` e o git. O `/bkhar:audit --deep` é a camada inferencial (Parte V).

**A medição** responde quanto custou, onde gastou e se a skill ajuda:

| O quê | Ferramenta | Responde |
| --- | --- | --- |
| custo da sessão | `scripts/session_cost.py`, chamado pelo `/bkhar:save` | tokens e dólares por modelo, com o acumulado em `.logs/` |
| custo da task | `scripts/metrics.py`, que grava o `METRICAS.md` | duração, tokens e custo por fase e por papel, e onde travou |
| efeito das skills | `claude plugin eval .` sobre `evals/` | o delta entre o braço com o plugin e o sem ele |

A linha de base de 2026-11-19 (`evals/BASELINE.md`) rodou os 28 casos: delta médio +0,19, com casos de +1,00 e uma regressão real aberta. O número que importa é o delta, não a nota: nota alta nos dois braços mostra que o modelo já sabia.

### 29. Comandos

Os comandos só existem no plugin, e o prefixo de um comando de plugin é o nome do plugin: por isso o kit foi rebatizado `bkhar`. Durante a migração, o plugin `bks` continua instalado para os projetos que ainda não mudaram. Não há executável de tasks separado: um motor só, o `/bkhar:loop`. O lançador `bkhar` só monta o ambiente do provedor e entrega o terminal ao `claude`.

| Comando | Onde roda | O que faz |
| --- | --- | --- |
| `/bkhar:brain` | Vault ou repo | Panorama dos projetos, ou o STATUS do projeto; avisa modelo defasado |
| `/bkhar:new-project` | Vault | Cria repo canônico e grava o perfil |
| `/bkhar:migrate` | Repo | Traz um projeto do `bks` para o `bkhar` e grava o `.bkhar.json` |
| `/bkhar:note` | Repo | Nota viva em `docs/input/notas/` |
| `/bkhar:canonize` | Repo | `docs/input/` + `docs/design/` → `CONTEXT.md` |
| `/bkhar:prd` | Repo | `CONTEXT.md` → `PRD-{projeto}.md` |
| `/bkhar:plan` | Repo | PRD → `outputs/PLAN-{projeto}.md` e o grafo `outputs/GRAPH-{projeto}.json` |
| `/bkhar:arch` | Repo | Portão: ARCH e um modelo por arquivo em `docs/library/architecture/`; `--update` refaz o defasado |
| `/bkhar:library` | Repo | Catálogo e dashboard da biblioteca; `export` para `knowledge/` do vault |
| `/bkhar:refine` | Repo | Rito de refinamento: perguntas da equipe, FEAT e TEST aprovados |
| `/bkhar:spec` | Repo | Entrevista → FEAT → TEST, sem rito |
| `/bkhar:tasks` | Repo | FEAT e TEST aprovados → `specs/tasks/TASK-[feature].md`, uma task por peça |
| `/bkhar:loop` | Repo | Passo 0 com o RED do Testes; LOOP-4 com o Dev na branch `task/T-NNN`; `--resume` retoma; `--wave` roda a onda do grafo |
| `/bkhar:review` | Repo | Revisão em painel: Testes, Qualidade e, em área sensível, Segurança |
| `/bkhar:status` | Repo | Tabela da execução em ondas: liberado, em curso, bloqueado, suposições abertas |
| `/bkhar:mode` | Repo | Troca entre `collaborative` e `autonomous` pela prontidão, com ADR |
| `/bkhar:maintainability` | Repo | Parecer de manutenibilidade por aplicação |
| `/bkhar:save` | Repo | Decisões, STATUS, JOURNAL, alertas do canônico e da arquitetura, medição, candidatas ao vault, biblioteca regerada |
| `/bkhar:audit` | Repo ou kit | Deriva entre registro, guias, sensores e estado; `--deep` procura contradição de sentido |
| `/bkhar:retro` | Repo | Promove cada proposta candidata a regra do projeto, do vault ou do kit, ou a rejeita com motivo |
| `/bkhar:harvest` | Vault | Indexa ADRs e `LEARNINGS.md` de `repos/` e do kit, e consolida por tema em `knowledge/wiki/experiencia/` |
| `/bkhar:ingest` | Vault | Fonte ou lote → página em `knowledge/wiki/` |
| `/bkhar:panel` | Repo | Painel com 2 ou 3 agentes independentes; ADR com as opções descartadas |
| `/bkhar:ask <agent>` | Repo | Pergunta direta a um papel, com resposta que cita a fonte |
| `/bkhar:maestri` | Repo, terminal do Gerente | Liga, desliga e confere a equipe em terminais do Maestri |

Fora dos comandos: a skill `bks-sdd` conduz o método num workspace avulso, e `claude plugin eval .` mede o delta das skills no repositório do harness.

*Proposto:* `/bkhar:brainstorm`, `/bkhar:skill new / list / promote` e um `/bkhar:cost` que junte o custo por agente, modelo, skill e fase.

Como usar cada comando, com passo a passo e exemplo: Parte X, Manual de comandos.

## Parte VII — Case: comprovante PIX

Este case é fictício. Ele acompanha uma feature do pedido à retrospectiva: um endpoint de consulta de comprovante PIX numa API .NET 10 em hexagonal, com Dapper e SQL Server. O projeto já passou pela fase pesquisa e pelo portão da arquitetura: `CONTEXT.md`, PRD, plano e ARCH estão aprovados. O `.bks-profile.json` declara perfil `backend` com rigor `producao`, e o manifesto `.claude/multiagente.md` lista pagamentos e dado pessoal como áreas sensíveis.

### 30. Pedido e refinamento

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

### 31. FEAT, TEST e tasks

A FEAT nasce com os critérios: 404 para inexistente ou alheio, CPF sempre mascarado, autorização por pagador ou recebedor, p95 abaixo de \[\_\_\] ms. Você aprova, e ela recebe `**Status:** Aprovada`. O Testes escreve o TEST, com um cenário por critério, e você o aprova do mesmo jeito.

O `/bkhar:tasks` decompõe a feature em quatro tasks, uma por peça: a porta de leitura no domínio, o adapter Dapper, a regra de autorização e o endpoint. Cada task carrega os cenários do TEST que cobre, e o "comprovante de outro cliente" cai na task da regra. Você aprova a lista, e a FEAT passa a `Em execução`.

### 32. Implementação sob LOOP-4

Na task do adapter, `/bkhar:loop T-012` abre a branch `task/T-012`. No passo 0, o Testes escreve o RED: os cenários da task em xUnit, todos falhando pelo motivo certo. Você confirma, e o portão vira commit.

| Tentativa | O que aconteceu | Gate | Resultado |
| --- | --- | --- | --- |
| 1 | Dev referencia um tipo que não existe | `dotnet build` (G1) | Falhou; o erro volta como contexto |
| 2 | Domain passa a referenciar Dapper diretamente | `LayerDependencyTests`, o teste de arquitetura do esqueleto | Falhou; viola a hexagonal |
| 3 | Repositório movido para o adapter, porta no domínio | `dotnet test` (G2) e cenários cobertos (G3) | Passou |

A cada tentativa, o Dev explica o que mudou e por quê. Na tentativa 2, ele registra: "Coloquei a query no domínio para simplificar; o teste de arquitetura mostrou que viola a premissa. Movi para o adapter." As tentativas 1 e 2 ficam como foto em `refs/bkhar/T-012/`, fora do histórico, e o placar vai para o estado da task.

### 33. Revisão em painel

- **Segurança (bloqueante):** um log em nível Debug grava o comprovante completo, com CPF. Vira nova task.
- **Qualidade (sugestão):** o handler tem 40 linhas; propõe extrair a autorização num serviço de domínio. Você aceita.
- **Testes (aprendizado):** faltou um cenário para recebedor consultando comprovante de outro recebedor. Vira task, e o caso entra no `LEARNINGS.md`.

O Dev corrige, os gates passam de novo, e o painel aprova. A task integra com `merge --no-ff`, e a ordem `spec → red → review` fica no histórico.

### 34. Registro e retrospectiva

O `/bkhar:save` grava o ADR "Leitura direta para comprovante", atualiza `README.md` e `ARCHITECTURE.md`, reescreve o `STATUS.md`, acrescenta o marco no `JOURNAL.md` e mede o custo da sessão. O `METRICAS.md` mostra que fase da task gastou mais e quanto custou: \[fase\], \[\_\_\] dólares.

Saem três propostas candidatas em `inbox/proposals/`:

1. **Premissa:** CPF como value object que só expõe a versão mascarada.
2. **Checklist de Segurança:** verificar logs em nível Debug em todo diff de zona sensível.
3. **Template de FEAT:** seção "Quem pode ver" obrigatória em toda consulta.

No `/bkhar:retro`, você promove o template como regra do projeto. A premissa e o checklist vão para o kit: o `learning.py apply` os põe no histórico de regras das skills escolhidas, com eval pendente. Na próxima feature, o Segurança já pergunta sobre log Debug no refinamento, e o template já pede "Quem pode ver". Você aprovou seis vezes e não reexplicou nada.

## Parte VIII — Implantação

A implantação partiu do kit que já funcionava e nunca parou os projetos em curso. O repositório público do harness é `fabiobackside-code/Bks-Harness`, e recebe só versão concluída. Neste Atlas, `<harness>` é a pasta onde você o clonou: por exemplo, `C:\dev\bks-harness` no Windows ou `~/dev/bks-harness` no Linux e no macOS. Para instalar e começar a usar, o roteiro passo a passo é o treinamento, em `docs/artefatos/treinamento/treinamento-bks-harness.md`.

### 35. O caminho até aqui

| Versão | O que trouxe | Estado |
| --- | --- | --- |
| 0.7.0 | o kit `bks`: 17 skills, 12 comandos, quatro agentes, guardas e evals | origem |
| 0.8.0 | o kit importado com histórico e rebatizado `bkhar`; `/bkhar:migrate` | feita |
| 0.9.0 | a equipe: seis agentes e o Gerente, `ask`, `panel`, `refine`, revisão em painel, `LEARNINGS.md` | feita |
| 1.0.0 | modos e prontidão, ondas pelo grafo, painel com inbox, arquitetura como portão, biblioteca, `retro` e `harvest` | feita |
| 1.1.0 | lançador `bkhar` com Claude, DeepSeek e OpenRouter, chave cifrada, skill `bks-design-system` | feita |
| 2.0.0 | aplicação com CLI e web | pausada: o Maestri a substituiu |
| 3.0.1 | a equipe em terminais do Maestri, despacho por papel, comandos delegados, Bash limitado do Arquiteto; e as lacunas de Harness Engineering: recuperação da task, observabilidade, sensores de arquitetura, registro de regras, deriva, linha de base dos evals, `/bkhar:tasks`, guia para quem chega | feita: tag `v3.0.0` no privado; a `v3.0.1`, com o manifesto em 3.0.1, no privado e no público |
| validação pós-3.0.0 | as provas do piloto, as execuções de referência e o contexto por papel | depois da tag `v3.0.0` |
| 4.0.0 | portabilidade: o harness em outro executor além do Claude Code | *proposta* |

A 3.0.0 fecha por construção (`decisions/ADR-018`): o critério de saída é o que está no repositório, com suíte verde e linha de base medida. A prova no piloto vem depois da tag, sobre a versão final.

**Os projetos.** O plugin `bks` continua instalado até o último projeto migrar. A migração é um projeto por vez, com o `/bkhar:migrate`, e o `nquantic` vai por último. Aposentar o `bks` é o último passo, depois da medição.

### 36. Estrutura de pastas

```
<harness>\                               o harness (plugin bkhar), ex.: C:\dev\bks-harness
├── .claude-plugin\                      plugin.json (name: bkhar) + marketplace.json
├── agents\                              architect, developer, tester, security,
│                                        quality, scribe (o Gerente é a skill bks-team)
├── commands\                            os 25 comandos /bkhar:*
├── skills\                              as 19 skills, cada uma com references\
├── hooks\                               hooks.json, scripts\ (8 guardas) e tests\
├── profiles\ · templates\               nove perfis e o schema; FEAT, TASK, ADR, esqueleto
├── providers\                           claude, deepseek, openrouter
├── scripts\                             recovery, run_state, wave_graph, readiness,
│                                        metrics, session_cost, audit, rules_report,
│                                        learning, harvest, library, dashboard,
│                                        bkhar, keyvault, maestri_config, precommit,
│                                        install_guards, publish, build_artefatos
├── rules.json                           o registro das 48 regras
├── evals\ · tests\                      28 casos com a linha de base; suíte sem modelo
├── decisions\                           ADR-001 a ADR-018
└── docs\                                ARCHITECTURE, regras.md, artefatos\, planejamento\

${BKS_VAULT}\                              o vault, só conteúdo
├── workbench\                           profile.md, decisions\, regras\
├── knowledge\                           wiki\ (experiencia\, projetos\), raw\, tools\
├── inbox\proposals\                     candidatas vindas dos projetos
├── repos\{backside,w3,private,old}\     os projetos, cada um com git próprio
│   └── {projeto}\                       STATUS, WORKFLOW, JOURNAL, LEARNINGS,
│                                        .bks-profile.json, brain\{domain,engineering}\,
│                                        decisions\, specs\, docs\ (library\),
│                                        outputs\ (run\), inbox\proposals\, app\
└── docs\                                guias do vault

~\.claude\settings.json                   env BKS_VAULT (raiz do vault), BKS_KNOWLEDGE
~\.bkhar\providers.json                   provedor ativo; a chave fica cifrada no cofre
```

### 37. Onde estamos

- [x] Importar o kit com histórico e rebatizar o plugin `bkhar`; `/bkhar:migrate`
- [x] Instalar `bkhar` ao lado do `bks`
- [x] Equipe, Gerente e ritos (0.9.0)
- [x] Modos, ondas, painel, portão de arquitetura, biblioteca, `retro` e `harvest` (1.0.0)
- [x] Provedores pelo lançador, com a chave cifrada (1.1.0)
- [x] Equipe em terminais do Maestri, com queda para subagente (3.0.1)
- [x] Recuperação da task, métrica por fase, sensores de arquitetura, registro de regras e deriva (3.0.0)
- [x] Linha de base dos evals: 28 casos, delta médio +0,19 (3.0.0)
- [ ] Fechar a 3.0.0: arrumação, atestado, merge, tag e publicação (Ações 013 a 015)
- [ ] Validação pós-3.0.0 no `poc-treino-harness`: rito por terminal, comando delegado, Bash recusado no Arquiteto, Maestri fechado e reaberto
- [ ] `--wave`, ramo `autonomous` e painel numa onda real
- [ ] Migrar os projetos, um por vez, e aposentar o `bks`

## Parte IX — Evolução: skills plugáveis

O harness foi feito para crescer. Cada capacidade nova entra como uma skill, que qualquer agente pode carregar, sem mexer nos comandos nem nos perfis.

### 38. Agente e skill

O agente é o papel: **quem** pergunta, decide ou revisa. A skill é a capacidade: **como** se faz brainstorming, análise de ameaças ou profiling. Um mesmo agente ganha competência nova quando você liga uma skill ao perfil dele, e uma mesma skill pode servir a vários agentes.

As skills carregam sob demanda. Só o nome e a descrição ficam sempre no contexto; o corpo entra quando a skill é acionada, e as referências só quando o caso pede. Por isso a regra que a skill não pode perder fica no corpo: a linha de base mostrou que regra só em `references/` pode não chegar ao modelo.

### 39. Catálogo

| Skill | O que traz | Usada por | Situação |
| --- | --- | --- | --- |
| `bks-sdd` | Ciclo SDD (desenvolvimento guiado por especificação) completo num workspace avulso, custo | Gerente, Arquiteto | Existe (465 linhas no corpo, o resto em `references/`) |
| `bks-team` | O protocolo do Gerente: ritos, despacho por terminal ou subagente, conflito exposto | Gerente | Existe |
| `bks-create-plan-tasks` | Decomposição em tasks atômicas | Gerente | Existe |
| `bks-standards` | Premissas, calisthenics, comentário, regras por linguagem | Arquiteto, Qualidade, Dev | Existe |
| `bks-dotnet-solutions` | .NET em hexagonal, montado pelas portas, no padrão direto ou no TXC | Arquiteto, Dev | Existe |
| `bks-typescript-solutions` | API, agente LangGraph, worker, consumer em TypeScript | Arquiteto, Dev | Existe |
| `bks-go-solutions` | API, worker, consumer, CLI e SDK em Go | Arquiteto, Dev | Existe |
| `bks-tests` | Testes em qualquer stack: `Assert` nativo, projeto em `src/`, código de saída | Testes | Existe |
| `bks-arch` | Notação BKS para Mermaid, archify, C4, TOGAF | Arquiteto, Documentador | Existe |
| `bks-design-system` | Design system ao lado da taste-skill | Dev | Existe |
| `bks-writing` | Padrão de escrita da documentação em PT-BR | Documentador | Existe |
| `bks-maintainability-review` | Parecer de manutenibilidade, nota 0–100 | Qualidade, Arquiteto | Existe, sem uso real |
| `security-audit` | Entrada, autorização, segredo, dado sensível | Segurança | Existe |
| `api-design` · `refactor-guide` · `debug-assistant` | Contrato HTTP; refatoração com rede; do sintoma à causa | Arquiteto, Dev | Existem |
| `doc-writer` · `pr-writer` · `frontend-design` | Docstring e README; PR pelo diff real; interface | Documentador, Dev | Existem |
| `brainstorming` | Divergir e convergir, pre-mortem, seis chapéus | Gerente, todos nos painéis | *Proposta* |
| `performance` | Orçamento de latência, BenchmarkDotNet, carga, alocação | Dev, Qualidade, Arquiteto | *Proposta* |
| `lang-java-spring` · `lang-php` | Convenções por linguagem no padrão hexagonal | Dev, Qualidade | *Proposta* |
| `legado-interop` | Mainframe, COBOL, TCP binário, Anti-Corruption Layer | Arquiteto, Dev | *Proposta* |

### 40. Anatomia de uma skill

```
skills\bks-tests\
├── SKILL.md          nome, descrição (o gatilho), regras críticas, histórico de regras
└── references\       o detalhe, carregado só quando o caso pede

evals\tests-local-projeto\
└── case.yaml         o pedido, os graders e o número de execuções
```

O `SKILL.md` é o formato que o Claude Code já entende: o corpo fica curto e o detalhe mora em `references/`. Os casos de eval ficam fora da skill, em `evals/`, porque o `claude plugin eval` os lê de lá. A seção `## Histórico de regras` recebe a regra promovida pelo `/bkhar:retro`, com a proposta de origem.

### 41. Ciclo de vida

Hoje a skill tem dois estados: **existe**, com pelo menos um caso de eval e o delta medido na linha de base, ou ***proposta***. A regra nova numa skill existente entra com `eval: pendente` e sai se o delta não aparecer.

*Proposto:* um ciclo com quatro estágios e critério explícito entre eles.

| Estágio | Critério de entrada | Onde pode ser usada |
| --- | --- | --- |
| Proposta | Surgiu na retro ou a pedido seu | Em nenhum lugar ainda |
| Experimental | `SKILL.md` escrito e pelo menos 5 evals | Projetos não sensíveis, com aviso |
| Estável | Passa nas evals e em 3 FEATs reais, com sua aprovação | Todos os projetos |
| Deprecada | Substituída por outra ou sem uso | Projetos que a fixaram, até migrarem |

&#91;embedded content: ciclo de vida da skill · 4 estágios e seus critérios\]

Os critérios ficam entre os estágios: uma skill só avança quando cumpre o que está escrito embaixo da seta.

### 42. Versionamento

Algumas skills já declaram `version:` no frontmatter. A regra é o versionamento semântico:

- **MAJOR** quando muda o comportamento esperado (uma regra removida, um formato de saída novo).
- **MINOR** quando acrescenta sem quebrar (uma pergunta nova no checklist, uma referência nova).
- **PATCH** quando corrige texto ou exemplo.

*Proposto:* faixa aceita no perfil do agente, como `security-audit@^1`; um `skills.lock` por projeto, para revisar uma FEAT antiga com as mesmas regras; e a tag `skill/<nome>/v<versão>` no Git.

### 43. Como uma skill nasce

Uma skill nasce do ciclo de aprendizado: quando a retrospectiva acumula propostas sobre o mesmo tema, o tema vira candidato a skill. O caminho hoje:

1. a proposta promovida ao kit no `/bkhar:retro` entra pelo `learning.py apply`, no histórico de regras da skill mais próxima;
2. um caso em `evals/` prova a regra: `claude plugin eval . --case <caso>` roda com e sem o plugin, e o que vale é o delta;
3. quando o tema não cabe em skill existente, ele vira skill nova, com o seu caso de eval.

*Proposto:* `/bkhar:skill new` e `/bkhar:skill promote`, com um rito de brainstorming para escrever a skill.

**Exemplo: Go já fez esse caminho.** A `bks-go-solutions` nasceu das suas convenções: hexagonal em pacotes, erro idiomático no lugar de `Result[T]`, testes de tabela, e o TXC por executor tipado quando o projeto o adota. Ela alimenta e consome a base `knowledge/wiki/go/`, com lições anonimizadas dos projetos. Na linha de base, o caso `go-txc` deu delta +0,50, e o `go-teste-arquitetura`, +0,50. O próximo candidato é `lang-java-spring`, pelo mesmo caminho.

### 44. O harness também evolui

O próprio harness segue o padrão que ele aplica. Agentes, comandos, skills, guardas e perfis são versionados em `<harness>`, e o ciclo dele é **mudar → provar → medir**. Uma mudança vive no diretório da sua natureza, a suíte estrutural prova que nada quebrou, e o eval mede se a skill muda a decisão do agente. Decisão sobre o harness vira ADR em `<harness>\decisions\`; decisão sobre como você trabalha, em `workbench/decisions/` do vault.

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

### B. Definição de provedor

A definição de cada provedor fica em `providers/`, no formato `version: 1`. Ela diz o endereço, os nomes das variáveis e o modelo padrão de cada rótulo. A chave e o provedor ativo ficam fora do repositório, em `~/.bkhar/`, com a chave cifrada. Exemplo, o `providers/deepseek.json`:

```json
{
  "version": 1,
  "name": "deepseek",
  "requires_key": true,
  "base_url": "https://api.deepseek.com/anthropic",
  "env": {
    "base_url": "ANTHROPIC_BASE_URL",
    "token": "ANTHROPIC_AUTH_TOKEN",
    "labels": {
      "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
      "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
      "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL"
    },
    "clear": ["ANTHROPIC_API_KEY"]
  },
  "default_models": {
    "opus": "deepseek-v4-pro",
    "sonnet": "deepseek-flash",
    "haiku": "deepseek-flash"
  },
  "single_model": false
}
```

O `clear` esvazia a `ANTHROPIC_API_KEY` no processo filho: herdada do shell, ela iria ao endereço de terceiro. Os agentes continuam declarando só o rótulo, e o provedor ativo decide quem responde por cada um.

### C. Glossário

| Termo | Significado |
| --- | --- |
| Harness | Tudo em volta do modelo: contexto, ferramentas, fluxo, verificação e observação |
| Guia | Instrução que o agente lê antes de agir: skill, comando, agente, template |
| Sensor | O que confere o resultado depois da ação; computacional (script) ou inferencial (agente) |
| Trava | Sensor computacional que recusa a ação em vez de avisar |
| Plugin | Pacote do Claude Code com skills, comandos, agentes e guardas; o nome dele é o prefixo dos comandos |
| Vault | `${BKS_VAULT}`: `workbench/` (você), `knowledge/` (o que você aprendeu) e `repos/` (os projetos) |
| Projeto autossuficiente | Cada repo guarda sua memória, decisão e domínio; nenhum comando de projeto lê o vault |
| STATUS, WORKFLOW, JOURNAL | Onde parei; o fluxo de comandos do projeto; os marcos, do mais recente ao mais antigo |
| Perfil | O que o projeto gera (`backend`, `fullstack`, `component`...), em `.bks-profile.json` |
| Rigor | Eixo do perfil: `producao` ou `poc`; dimensiona a revisão |
| CONTEXT.md | Contexto canônico do projeto, gerado pelo `/bkhar:canonize` a partir de `docs/input/` |
| FEAT, TEST, TASK | Spec da feature, cenários de teste e a lista de tasks de uma peça cada, em `specs/` |
| RED | O teste escrito antes do código, ainda falhando; o Testes o escreve no passo 0 do loop |
| LOOP-4 | Até quatro tentativas com goals G1–G4, na branch `task/T-NNN`; depois, `BLOQUEIO-*.md` e decisão sua |
| Foto | Tentativa guardada fora do histórico, em `refs/bkhar/T-NNN/impl-K` |
| Gate | Verificação executada pela máquina, não declarada pelo modelo |
| Guarda | Hook que recusa a escrita fora do padrão, com teste próprio |
| Manifesto | `.claude/multiagente.md`: zonas de contenção, áreas sensíveis, invariantes |
| Zona de contenção | Arquivo que só a sessão principal edita (Composition Root, migrations, numeração de ADR) |
| Área sensível | Parte do manifesto que exige revisão independente da Segurança |
| PBQ | Tipo do papel: orquestrador, implementador ou validador |
| Rito | Formato de conversa com papéis, começo e fim |
| Proposta | Aprendizado candidato (`status: candidata`) em `inbox/proposals/`, à espera do `/bkhar:retro` |
| Modo | `collaborative` (padrão) ou `autonomous`, em `axes.mode` do perfil |
| Prontidão | Checagem por script que concede o `autonomous`: entradas aprovadas e nada em aberto |
| Suposição | Resposta que o Arquiteto presumiu no `autonomous`, registrada em `decisions/SUPOSICOES.md` |
| Onda | Conjunto de tasks do grafo liberadas juntas, até 4 em paralelo |
| ARCH | Índice da arquitetura em `docs/library/architecture/`, que aponta um modelo por arquivo |
| Biblioteca | `docs/library/`: catálogo e dashboard dos artefatos do projeto |
| Skill | Capacidade versionada que um ou mais agentes carregam sob demanda |
| Eval | Caso que mede o delta de uma skill: o agente com ela contra o agente sem ela |
| Delta | A diferença de nota entre o braço com o plugin e o sem ele; o número que importa |
| Registro de regras | `rules.json`: cada regra ligada à fonte e ao sensor que a confere |
| Deriva | Guia e sensor que deixaram de dizer a mesma coisa; conferida pelo `audit` |
| Lançador | `bkhar`: monta o ambiente do provedor e entrega o terminal ao `claude` |
| TXC | Transaction Context: contexto somente leitura da transação, criado pela sessão; padrão opcional por projeto (`txc: "base"`) |

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
| Apresentação BKS Harness | 3.0.0 | 2026-11-20 | Revista contra o Atlas 2.0.0: quatro slides novos (guias e sensores, a equipe em terminais, travas e recuperação, regras e medição), arquitetura, componentes, modelo e provedor, comandos, caminho e versões reescritos; `/tasks` no fluxo; o que não existe sai como proposto; 34 slides |
| Atlas do BKS Harness | 2.0.1 | 2026-11-21 | 3.0.0 e 3.0.1 feitas no roteiro de versões; contagem da Visão geral referida à 3.0.1 |
| Atlas do BKS Harness | 2.0.0 | 2026-11-20 | Revisão completa contra a 3.0: guias e sensores nos Fundamentos; a Arquitetura passa a ser o plugin real, com a Figura 3 refeita e sem o core hexagonal, o `routing.yaml` e o policy engine; equipe em terminais do Maestri; `/bkhar:tasks` no fluxo; seções novas de travas e recuperação e de regras, deriva e medição; tabela dos 25 comandos; case com RED e tasks; Implantação com o caminho real das versões; catálogo das 19 skills; Apêndice B com a definição de provedor; glossário com o vocabulário do guia. Seções do case em diante renumeradas de 28–42 para 30–44 |
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
