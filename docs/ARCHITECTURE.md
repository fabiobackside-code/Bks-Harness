# Arquitetura do bks-harness (plugin bkhar)

## O que este repositório é

Um plugin do Claude Code. Não contém código de aplicação — contém **processo**: instruções que o
agente carrega para conduzir um ciclo de Spec-Driven Development.

A unidade de entrega é o pacote instalável. Antes deste repo, skills, comandos e agentes viviam
soltos em pastas de usuário, sem versão e duplicados entre a instalação global e o vault. O
empacotamento existe para dar a essas peças uma única fonte da verdade, versionada.

## Estrutura

```
.claude-plugin/     manifestos (plugin.json, marketplace.json)
skills/             skills, cada uma com SKILL.md + references/
commands/           slash commands
agents/             subagentes com papel e modelo declarados
scripts/            utilitarios chamados pelas skills (medição de custo)
hooks/              guardas executáveis de regra
evals/              suites de eval das skills, um diretório por caso
docs/               está documentação
```

## Decisões

### Progressive disclosure nas skills

Cada skill tem um `SKILL.md` de entrada e um diretório `references/` carregado sob demanda. O
`SKILL.md` decide qual referência abrir; o conteúdo pesado não entra no contexto até ser
necessário.

O motivo e custo: uma skill que carrega todas as suas fases a cada invocação paga por instrução
que não vai usar. `bks-sdd` tem sete fases; um comando de status não precisa das outras seis.

`bks-tests` nasceu já neste formato: era um slash command de 2043 linhas que entrava inteiro no
contexto a cada invocação. Virou um `SKILL.md` de 93 linhas — regras inegociaveis, tabela de fases
e ponteiros — com sete referências abertas sob demanda.

Estado atual: `bks-sdd`, `bks-dotnet-solutions` e `bks-typescript-solutions` tem `references/`,
mas o `SKILL.md` ainda concentra as fases. O adelgacamento está planejado para depois das suites
de eval — refactor de skill validada em uso sem rede de teste e aposta, não engenharia.

`bks-go-solutions` nasceu no formato alvo: 222 linhas de entrada — registro de tipos, variáveis,
fluxo, base de aprendizado e checklist — contra 856 do .NET e 716 do TypeScript, com os cinco
prompts especializados em `references/`, abertos um por vez. É a referência de como as outras três
devem ficar.

### O delta de linguagem mora em `bks-standards`, não na skill geradora

As premissas (TXC, pipeline explícito, Result, calisthenics, pragmatismo token-aware) são método,
não linguagem, e vivem em `bks-standards/references/bks-premises.md`. As skills geradoras
produzem estrutura e apontam para lá.

Go forçou a distinção a ficar explícita, porque é a primeira linguagem do kit que **contradiz** o
padrão-base em pontos concretos: `error` idiomático no lugar de `Result[T]`, imutabilidade por
disciplina sem `record`, interface declarada no consumidor e não no provedor, wiring manual sem
container, e metade do Object Calisthenics chegando por early return em vez de polimorfismo.

Esse delta ficou em `bks-standards/references/go-standards.md`, simétrico ao `dotnet-standards.md`
que já existia — não dentro de `bks-go-solutions`. A alternativa (skill autossuficiente) duplicaria
premissa em duas casas, e premissa duplicada diverge na primeira mudança. `bks-premises.md` ganhou
um aviso no ponto onde o padrão-base é descrito em termos de C#, porque quem lê aquele parágrafo e
gera Go direto produz código que compila e que nenhum programador Go mantém.

### A skill de Go alimenta e consome uma base de aprendizado

`bks-go-solutions` é a primeira skill do kit que **escreve fora do projeto**: a cada geração,
consulta `${BKS_KNOWLEDGE}/wiki/go/` antes e registra depois. As demais só leem referência
estática.

A razão é que Go entrou como stack nova, sem os anos de prática que .NET e TypeScript já têm. O que
se aprende nos primeiros projetos é justamente o que não está em nenhuma referência — e sem
registro, se perde entre uma sessão e outra.

O registro é em duas casas, com papéis distintos, e é o que resolve a confidencialidade: o caso
completo com nomes reais fica em `brain/engineering/` do projeto (repositório fechado, contexto
ligado ao código); a wiki recebe a lição destilada e **anonimizada**. Os projetos de origem são de
domínio bancário — a lição é transversal, o caso não é. A regra de anonimização está no `index.md`
da base e repetida na skill, porque regra que vive num lugar só não sobrevive à pressa.

Quatro classes: padrão, armadilha, trecho e decisão Go vs .NET. A quarta existe para que a escolha
de stack seja revisitável com evidência, e não por impressão.

O risco conhecido é a base encher de trivialidade — página que repete o Effective Go. A contenção
é instrução explícita de só registrar o que custou tempo, e `status: draft` até a lição se repetir
em outro projeto. Se não bastar, o passo seguinte é uma guarda executável, não mais texto.

### Caminhos por variavel de ambiente

Os comandos de workbench referenciavam caminhos absolutos de uma maquina. Num pacote público isso
não funciona e vaza estrutura pessoal.

As referências passaram a `${BKS_VAULT}` e `${BKS_KNOWLEDGE}`. São duas, não mais: cada projeto
guarda sua própria memória, decisão e domínio, e não há hub central a apontar.

As skills não dependem de nenhuma das duas — operam sobre o diretório de trabalho atual, e por
isso servem a qualquer projeto sem configuração. Só dois comandos precisam do vault: `/bkhar:brain` no
modo panorama, que percorre `repos/`, e `/bkhar:new-project`, que cria dentro dele.

### Separação de papéis entre agentes

Quatro agentes com ferramentas e modelos distintos, não um agente genérico:

- `reviewer` e read-only e roda em invocação separada. Quem escreveu o código não revisa a própria
  segurança — o vies de quem implementou e saber que o filtro está la porque o pos nos outros
  três.
- `scribe` roda em Haiku e só registra o que foi confirmado com evidência. Documentação que
  infere resultado e pior que documentação ausente.
- `planner` não tem Bash nem Edit de código de produção. Separar quem específica de quem
  implementa evita spec escrita para caber no que já foi codado.
- `builder` opera sob LOOP-4 — no máximo quatro tentativas contra goals verificáveis (build
  limpo, testes verdes, cenários da `TEST` cobertos).

### Regra precisa de guarda executável

Regra que vive só em texto de instrução não sobrevive a pressa. Um SDK deste kit foi construido
inteiro — quatro fases, vinte e uma tasks — sem `README.md` nem `ARCHITECTURE.md`, e com quase um
terco do código em comentario. A regra existia havia uma semana. Vivia no lugar errado: era lida
na abertura da sessão, e não no ponto onde o trabalho e conferido.

Os guardas em `hooks/` são a resposta. Três deles recusam a escrita, não avisam:

- `no_dispatcher` recusa `MediatR` e equivalentes em `.cs`. Dispatcher esconde a ordem dos passos
  atras de uma convenção de tipo; não da para ler o fluxo sem procurar o handler.
- `comment_budget` recusa bloco acima de cinco linhas e marca de severidade. O que denúncia ensaio
  não e a proporção de comentario no arquivo, e o bloco longo — decisão e trade-off pertencem a
  este documento.
- `dod_docs` recusa a declaração de tipo público enquanto `README.md` e `ARCHITECTURE.md` não
  tiverem sido tocados na mesma leva. Le o working tree do git, não o conteúdo dos documentos:
  o guarda cobra que a documentação entre na mesma passada, não julga se ela ficou boa.

Três escolhas os mantém usaveis. Ignoram arquivo de teste, arquivo fora de repositório git e o
que não e `.cs`. Falha interna libera a escrita — guarda que quebra o fluxo por bug próprio e
desligado em uma semana, e a regra volta a ser intenção. E cada um tem teste em `hooks/tests/`,
pela mesma razão que existe: guarda sem teste também e só intenção.

### Schema dos casos de eval

Os casos vivem em `evals/<caso>/case.yaml` e o `plugin.json` os declara em
`experimental.evals`. O schema é do `claude plugin eval`, não nosso: fora dele o caso não carrega
e não roda.

O schema `1.1` difere do `1.0` em quatro pontos: `prompt` e `max_turns` vivem dentro de
`execution`; todo grader tem `name`; `with_only` não existe mais — `tool_used: Skill` já é tratado
como indicador de disparo, fora da pontuação; e `runs` fica no topo.

Os 18 casos passaram semanas escritos em `1.0` sem carregar. `test_evals` checava se o YAML
parseava e se o `name` batia com o diretório — nada disso falha quando o schema muda. A suíte
passava verde enquanto a suíte de eval estava inteira fora do ar.

Por isso `test_evals` valida contra o schema, e não contra o parser. A regra que só o CLI conhece
precisa de guarda deste lado; senão a próxima mudança de schema volta a passar despercebida até
alguém gastar crédito para descobrir.

Os nomes dos graders são derivados do critério — `sem-mediatr`, `verifica-propriedade` — e não
posicionais. O relatório do CLI os imprime a cada run, e `g1 falhou` não diz o que quebrou.

### O canônico é realimentado pela spec, e a divergência é detectada no `/bkhar:save`

O fluxo documental do kit foi desenhado em mão única: `/bkhar:canonize` consolida `docs/input/` e
`docs/design/` em `docs/canonical/CONTEXT.md`, o `/bkhar:prd` transforma isso em requisito e o `/bkhar:spec`
em FEAT e TEST. Na prática o sentido se inverte depois da primeira entrega: a FEAT aprovada e o
ADR fechado passam a ser a verdade do projeto, e o canônico envelhece sem que nada sinalize.

A correção tem duas metades, e cada uma resolve um problema diferente.

O `/bkhar:canonize` passou a ler `specs/` e `decisions/` como fonte, ao lado de `docs/input/` e
`docs/design/`. Sem isso, reconsolidar não recupera o que foi aprovado — o comando releria o
mesmo material de pesquisa e produziria a mesma versão. A alternativa considerada era uma nota
ponte em `docs/input/notas/`, escrita por quem fechasse a sessão: foi descartada porque a nota é
síntese de segunda mão, e o comando proíbe promover ao canônico o que não tem fonte. Spec
aprovada já é fonte, com caminho e data — não precisa de intermediário.

O `/bkhar:save` detecta a divergência por data de modificação: arquivo em `specs/` ou `decisions/` mais
recente que o `CONTEXT.md` significa canônico defasado. O alerta vai para a seção do que trava no
`STATUS.md`, não só para o relatório da sessão, porque é o `STATUS.md` que o `/bkhar:brain` lê na sessão
seguinte — aviso que morre no fim da sessão não é aviso, é ruído.

O `/bkhar:save` não roda `/bkhar:canonize` sozinho, e esse limite é deliberado. O `/bkhar:canonize` pergunta quando
encontra ambiguidade, e travar o fechamento de sessão numa pergunta de consolidação troca um
débito visível por uma sessão que não fecha. Projeto sem `docs/canonical/CONTEXT.md` não recebe
alerta nenhum: nem todo projeto usa o fluxo canônico, e alertar sobre ausência de um arquivo
opcional treina o leitor a ignorar o aviso.

A revisão foi considerada como lugar da detecção e descartada. O `/bkhar:review` dispensa mudança que
não toca área sensível — documentação, justamente — e o agente `reviewer` é read-only, em
invocação separada, sem o estado da sessão que aprovou a FEAT. Divergência de canônico também não
é achado de segurança em `arquivo:linha`, e diluir o contrato do agente enfraquece o que ele já
faz bem.

A detecção por `mtime` é grosseira de propósito — acusa divergência quando a spec mudou só de
formatação. O falso positivo custa uma reconsolidação; o falso negativo custa um canônico errado
alimentando o próximo `/bkhar:prd`.

### O projeto concreto realimenta a skill que ele referencia

Skill de componente — conceitos, guardas, fundamentos, guidelines — é escrita antes do código que
ela descreve. Enquanto o componente está em construção, o código decide coisas que a skill não
previa, e a skill envelhece em silêncio: quem a carrega numa sessão seguinte aplica a regra velha
com a autoridade de uma regra vigente.

O `/bkhar:canonize` confronta a skill referenciada pelo projeto com o que o projeto concretizou, e
classifica cada divergência. **Aprendizado** é a skill desatualizada: o canônico segue o projeto e
a entrada diz o que muda na skill. **Exceção** é o projeto divergindo de propósito, com a skill
valendo para os outros — e só é exceção com ADR que a registre. Sem ADR, a divergência é pergunta:
chamar de exceção o que ninguém decidiu é o mesmo que deixar a regra cair.

O comando reporta e não edita a skill. A skill mora fora do repositório do projeto — no plugin ou
em `~/.claude/skills/` —, e o `/bkhar:canonize` escreve só no repositório onde roda. A atualização é
de quem mantém a skill, com a entrada do canônico como fonte.

### Os comandos existem só no plugin

`/bkhar:brain`, `/bkhar:save` e os outros nove viviam em duas cópias: `commands/` deste repositório e
`~/.claude/commands/`, instalada à mão. A cópia global venceu a do plugin na resolução de nome, o
que tornava o repositório origem de um comando que não era o executado.

O custo apareceu quando a validação do `/bkhar:save` 0.2.1 rodou contra a cópia errada: o comando
exercitado não tinha a verificação do canônico que a sessão pretendia testar, e a prova registrada
no `JOURNAL.md` não valia.

As cópias divergiram em três eixos. Sete dos onze comandos diferiam só por acentuação. Quatro
divergiam em conteúdo, e nenhum dos dois lados era completo: o `save` do kit tinha o ciclo do
canônico, o global tinha a medição de consumo. O kit carregava dois ponteiros quebrados que a
cópia global não tinha.

A instalação global foi removida em 2026-09-15, depois de migrado o que ela tinha de melhor. Um
comando do método passa a existir só onde o plugin está instalado. A alternativa — manter as duas
com um script de sincronização — foi descartada: sincronizador é peça que alguém tem que lembrar
de rodar, e a duplicação já tinha produzido defeito exatamente por ninguém lembrar.

A medição de consumo saiu do corpo do `/bkhar:save` para `commands/references/medicao-consumo.md`, e o
`session_cost.py` resolve o `pricing.json` ao lado de si — validado rodando da cópia instalada
depois de apagada a global.

### Ponteiro para arquivo é verificado

O `test_structure.py` casava referências com `[a-z0-9-]+\.md`, que não alcança nome acentuado.
`checklist-revisão-crítica.md` citado contra `checklist-revisao-critica.md` em disco passava sem
ser visto — o mesmo defeito que `607d5e1` já corrigira uma vez em `documentacao.md`.

A suíte passou a verificar todo caminho entre crases que aponte para dentro do kit. Caminho do
projeto consumidor (`docs/canonical/`, `decisions/`) e molde com placeholder ficam de fora: não
existem neste repositório por definição. Seis ponteiros quebrados apareceram na primeira execução,
incluindo uma das três falhas que a suíte já acusava sem diagnóstico.

### O plugin chama-se `bks`, e o prefixo é assumido

Comando vindo de plugin é sempre namespaceado: a documentação do Claude Code diz que o prefixo
existe para evitar colisão entre plugins e que nenhuma chave de frontmatter o remove. `name:` no
arquivo do comando controla o sufixo, não o prefixo.

Descobriu-se isso depois de apagar a instalação global, quando os comandos passaram a responder
como `bks-sdd-kit:save`. A mesma documentação explica por que a cópia global vencia antes: a
precedência é enterprise > personal > project > plugin, e `~/.claude/commands/` é personal.

Três saídas foram pesadas. Reescrever a documentação para `bks-sdd-kit:` mantinha um prefixo de
dezessete caracteres. Restaurar a cópia pessoal devolvia `/save` puro e com ele a duplicação que
esta sessão eliminou. A escolhida foi encurtar o namespace: o plugin passou a chamar-se `bks`, e
os comandos respondem como `/bks:save`.

O `name` do marketplace continua `bks-sdd-kit`, assim como o repositório — só o nome do plugin
mudou, porque é dele que sai o prefixo. A instalação passa a ser `bks@bks-sdd-kit`.

Em 2026-10-18, a importação do kit para o `bks-harness` trocou o nome do plugin para `bkhar`, e os
comandos passaram a responder como `/bkhar:*`. O raciocínio desta seção continua valendo; só o nome
mudou.

### O tier do modelo e visivel, e o subagente entra na conta

Os quatro agentes ja escolhiam modelo por perfil no frontmatter, mas a escolha era invisivel em
execucao: so quem abrisse o arquivo sabia que o `reviewer` custa Opus. O tier passou a ser
anunciado na primeira linha de cada agente.

A medicao tinha um buraco maior. O `session_cost.py` le o bloco `usage` do transcript, e o
consumo de subagente nao esta la — o transcript do subagente e outro arquivo, sem `usage`. Numa
sessao desta data, tres subagentes consumiram 278.890 tokens que nao entravam em relatorio nenhum.

O dado existe na notificacao de conclusao (`<subagent_tokens>`), e o tipo do agente na chamada da
tool `Agent`; os dois se ligam pelo `tool-use-id`. O script passou a correlacionar os dois e
reportar uso por agente.

O que essa tabela **nao** faz e somar ao custo. A notificacao traz tokens, nao tier — o modelo
exibido e o que o agente declara. Multiplicar token por preco de um tier inferido produziria um
numero com aparencia de medida e fundamento de suposicao.

### Como comparar um tier contra outro

O `planner` subiu para Opus em 2026-09-15, para medicao. A pergunta que isso abre — Opus paga o
proprio preco na especificacao? — nao se responde lendo duas specs e escolhendo a que soa melhor.
Isso e julgamento, nao medida, e e o mesmo vicio do eval sem delta.

A spec nao e o produto; o produto e a implementacao que ela permitiu. Tres sinais ja existem no
fluxo e sao contaveis:

| Sinal | Onde | O que denuncia |
|---|---|---|
| Tentativas do LOOP-4 | o `/bkhar:loop` registra | spec ambigua faz o builder errar e repetir |
| Achados do `reviewer` | `/bkhar:review` produz | spec que nao fechou invariante vira achado |
| FEAT alterada apos aprovada | git | spec que nao aguentou o contato com o codigo |

Compara-se um periodo, nao uma spec: dez FEATs num tier contra dez no outro. O custo aparece no
ledger; o beneficio, nas tres colunas acima. Se o tier mais caro poupa uma rodada de LOOP-4 por
spec, pagou — implementar errado e refazer custa mais que especificar bem.

Isso e indicio, nao experimento: projeto, dominio e complexidade mudam no meio. Serve para
decidir uma linha de frontmatter, nao para publicar conclusao.

### A escrita da documentação tem skill e guarda próprias

A documentação viva dos projetos tropeçava no número do ADR no meio da frase: o leitor tinha de
abrir a decisão para entender o parágrafo. A skill `bks-writing` fixa a regra central, que é
sintetizar a decisão no próprio texto. Quando a decisão ajuda, ela entra numa nota de fim de
parágrafo, com o número só no fim, como rastreio. A skill nasceu do padrão aplicado num projeto
consumidor, sobre quatro documentos de arquitetura e os decks de treinamento, e chegou aqui sem
nome, caminho ou exemplo daquele projeto.

Duas skills públicas sob licença MIT deram insumo: `writing-anti-ai` e `human-writing`. O texto
original de cada uma está em `skills/bks-writing/third-party/`, com a licença e o commit de origem,
e não é instalado como skill. Instaladas, as duas disputariam o gatilho com a `bks-writing` e
aplicariam regras que conflitam com o português técnico, como proibir o travessão. Por isso o
`references/fontes-externas.md` classifica cada regra delas: vale, foi adaptada ou foi descartada.
A suíte estrutural não verifica ponteiro dentro de `third-party/`, que é texto de terceiro sem
edição.

A guarda `writing_guard.py` roda depois da escrita, e não antes, ao contrário das guardas de
código. Frase longa e sigla sem definição têm falso positivo, e um bloqueio antes da escrita
travaria a edição de documento legado. Depois da escrita, o hook devolve ao agente os achados do
trecho escrito e não do arquivo inteiro, e mostra ao usuário o lembrete de rodar o `/bkhar:review`.
O `/bkhar:review` passou a conferir a escrita sempre que a mudança toca documentação viva, sem o
agente `reviewer`: roda a guarda nos arquivos tocados e dá a nota por dimensão da skill.

O mesmo script roda como linha de comando sobre o arquivo inteiro, e é assim que entra na DoD. A
contagem bate com a da guarda em PowerShell do projeto de origem: 75 achados no documento antes da
reescrita e nenhum depois, com a lista de siglas do projeto em `.bks/siglas-conhecidas.txt`.

Junto com a skill, o comentário de código perdeu o ponteiro para documento. A guarda contra
regressão diz o que quebra se alguém mudar a linha; o `ARCHITECTURE.md` diz na abertura para que
serve, e o comentário não precisa apontar para ele. O `doc-writer`, o `bks-dotnet-solutions`, o
`bks-sdd` e a mensagem do `comment_budget` seguem essa regra.

### A manutenibilidade é um comando próprio, separado do `/bkhar:review`

O `/bkhar:maintainability` avalia cada aplicação de `app/` e gera o documento de fundamentação do
projeto, pela skill `bks-maintainability-review`. Ele não entrou no `/bkhar:review` por três
diferenças. O agente `reviewer` só lê, e o parecer grava HTML. A revisão olha o diff de uma entrega
que toca área sensível, e a manutenibilidade olha o `app/` inteiro. Achado crítico da revisão
bloqueia a entrega, e a nota de manutenibilidade orienta a evolução sem bloquear nada.

A saída fica em `outputs/maintainability/` e `outputs/references/`, na raiz do projeto. A skill de
origem gravava ao lado do `.sln`, o que no kit poria relatório dentro de `app/`, no meio do código.

A persona é um desenvolvedor pleno. Quando `BKS_VAULT` está definido, o comando lê o perfil e a
wiki do vault para calibrar o repertório e citar as referências do time. Isso é a única leitura de
vault fora dos comandos de workbench, e é opcional: sem vault, o comando roda com a persona do kit
e diz isso no parecer. A regra de autossuficiência continua valendo, porque o vault melhora o
resultado sem ser condição para ele.

O núcleo da skill não conhece linguagem. Detecção, repertório e critérios de cada stack moram em
`skills/bks-maintainability-review/stacks/`, hoje com .NET e SQL. Java, Node, Go, PHP e Python
entram como arquivo novo, com as mesmas três seções, que a suíte estrutural exige. Aplicação de
stack sem arquivo não é pontuada em silêncio: o comando pergunta se pula ou se avalia só com a
rubrica, com confiança baixa. Cofre de credenciais e OpenShift saíram do núcleo para
`references/criterios-condicionais.md`, que só se aplica quando o código mostra a tecnologia.

O `/bkhar:canonize` sugere o comando no fim quando `app/` tem código. Antes disso, não há aplicação
para avaliar, e a sugestão seria ruído.

### O público recebe uma lista, não uma cópia

O trabalho vive num repositório privado; o público só recebe versão concluída. A cópia é do
`scripts/publish.py`, que parte dos arquivos versionados e deixa sair só o que está na lista
`ALLOW`. Arquivo novo fica de fora até alguém incluí-lo: esquecer custa um arquivo a menos no
público, nunca um vazamento.

Duas recusas protegem o que passa pela lista: caminho da máquina do autor e e-mail que não seja
noreply. O texto que só faz sentido no privado fica num bloco entre ``, que o script remove do Markdown. Assim o README e os artefatos têm uma fonte
só. A alternativa, uma pasta de trabalho no `.gitignore`, vaza com um `git add -f` e tira a versão
do estado do projeto.

O script não faz commit nem push. A publicação chega numa branch `release` do público, e o merge
para a `main`, que é a branch que o marketplace lê, é um pull request do Fabio.

## Consumidores

O kit foi extraido de um vault em uso. Os projetos que o consomem continuam sendo a fonte de
validação — mudança de contrato aqui precisa ser verificada contra eles antes de virar versão.
