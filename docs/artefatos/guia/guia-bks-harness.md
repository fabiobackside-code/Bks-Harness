# Guia do bks-harness — O harness explicado para quem chega

Versão 0.2.0, escrito sobre o plugin `bkhar` 3.1.0.

## Para que serve este guia

Este guia explica o que o BKS (Backside) Harness faz e por que cada peça existe. Cada capítulo
responde a uma pergunta que quem chega costuma fazer. Os exemplos vêm dos testes do próprio kit ou
da linha de base dos evals (as avaliações automáticas das skills), não de um projeto inventado.

Três documentos se completam:

| Documento | Para quê |
|---|---|
| este guia | entender o desenho: o que orienta o agente, o que confere, o que proíbe |
| o treinamento (`docs/artefatos/treinamento/`) | instalar e rodar, passo a passo |
| o manual de comandos (`docs/artefatos/manual/`) | o detalhe de cada comando `/bkhar:*` |

O porquê de cada decisão, com as alternativas descartadas, está no `docs/ARCHITECTURE.md`.

## 0. Como começo?

Você instala o plugin, abre uma sessão numa pasta de projeto e roda `/bkhar:brain`; se ele
responde com onde o projeto parou, o harness está de pé.

O caminho mínimo usa quatro capítulos do treinamento, nesta ordem:

| Passo | Capítulo do treinamento | O que você faz |
|---|---|---|
| 1 | 2 · Antes de começar | conferir Python 3 no `PATH` e o Claude Code instalado |
| 2 | 3 · Instalar o plugin | `claude plugin marketplace add fabiobackside-code/Bks-Harness` e `claude plugin install bkhar@bks-harness`; abrir uma sessão nova |
| 3 | 7 · O primeiro projeto | criar uma pasta com `repos/` dentro, abrir a sessão nela e rodar `/bkhar:new-project` com o perfil `docs` |
| 4 | 5 · Conferir que está de pé | abrir a sessão na pasta do projeto criado e rodar `/bkhar:brain` |

O vault (o repositório de conhecimento pessoal, capítulo 4 do treinamento) é opcional e não entra
no caminho mínimo.

**Confira.** O `/bkhar:brain` responde em até seis linhas, com três itens lidos do `STATUS.md` que
o esqueleto criou:

```
Onde parou: fase de levantamento, projeto recém-criado.
O que trava: nada trava.
Próximo passo: /bkhar:note com o primeiro material de entrada.
```

O texto exato depende do perfil escolhido; os três itens aparecem sempre.

Se em vez disso ele pergunta onde você quer trabalhar, a sessão foi aberta fora do projeto: não
há `STATUS.md` na pasta. Esse comportamento é proposital. Sem estado, o comando pergunta em vez
de adivinhar, e é a primeira trava do harness que você vai encontrar (capítulo 5).

Os capítulos seguintes explicam o que aconteceu por baixo desses quatro passos.

## 1. O que é um harness?

Agente é modelo mais harness. O modelo raciocina e escreve. O harness é tudo em volta dele: as
instruções que ele lê, as ferramentas que usa, o que confere o trabalho, o que é proibido e o que
fica guardado de uma sessão para outra.

Pense num profissional competente recém-contratado. Ele sabe programar, mas não conhece a casa.
Você entrega o manual de padrões, revisa o que ele entrega, tranca o que ele não pode mexer e
mantém um caderno de passagem para quem pegar o trabalho no dia seguinte. O harness faz essas
quatro coisas para o agente.

No `bkhar` há três camadas:

| Camada | Quem fornece | O que traz |
|---|---|---|
| modelo | o provedor (Anthropic, DeepSeek, OpenRouter) | o raciocínio e a escrita |
| harness da ferramenta | o Claude Code | o laço de execução, as ferramentas de leitura e escrita, as permissões |
| harness do usuário | o plugin `bkhar` | skills, comandos, agentes, guardas, scripts e templates do método |

Este guia trata da terceira camada. As duas primeiras vêm prontas.

**Exemplo: o lançador troca o modelo sem trocar o harness.** O `bkhar` (`scripts/bkhar.py`, decisão
no `decisions/ADR-006`) inicia o `claude` com o endereço e a chave de outro provedor. Os agentes em
`agents/` continuam declarando `opus`, `sonnet` ou `haiku`, e o provedor ativo decide quem responde
por cada rótulo. Skills, guardas e comandos seguem os mesmos. Se o harness fosse parte do modelo,
trocar de provedor obrigaria a reescrever o método.

O que o harness do usuário faz se divide em dois tipos de controle. O guia orienta antes da ação
(capítulo 2). O sensor confere depois dela (capítulo 3). Quando o sensor recusa em vez de avisar,
ele vira trava (capítulo 5).

## 2. Guias: o que orienta o agente antes de agir?

Guia é toda instrução que o agente lê antes de agir. É controle de antecipação: diz o que fazer
para que o erro não aconteça.

| Guia | Onde mora | Quando o agente lê |
|---|---|---|
| skill | `skills/<nome>/SKILL.md` e `references/` | quando o pedido casa com a descrição da skill |
| comando | `commands/<nome>.md` | quando o usuário digita `/bkhar:<nome>` |
| agente | `agents/<papel>.md` | quando a sessão principal chama aquele papel |
| template | `templates/` | quando um comando gera a feature (FEAT), o roteiro de teste (TEST), as tasks (TASK) ou o esqueleto do projeto |
| `CLAUDE.md` do projeto | raiz do repositório | em toda sessão aberta ali |

A skill carrega em camadas. O corpo do `SKILL.md` é curto e entra inteiro; o detalhe fica em
`references/` e só é lido quando o caso pede. É o que deixa dezenove skills instaladas sem encher o
contexto de cada sessão.

O custo dessa economia apareceu na linha de base dos evals: regra que só existe em `references/`
pode não chegar ao modelo. Por isso as regras críticas ficam no corpo da skill.

**Exemplo: a skill .NET recusando o MediatR.** O caso `dotnet-sem-dispatcher` pede uma API que
use o MediatR pelo nome. A skill entregava o MediatR como "o que você pediu" e só depois sugeria a
alternativa. A regra de recusa voltou ao corpo da skill, e o delta do caso subiu de +0,33 para
+1,00: com a skill, o agente recusa e oferece a chamada explícita no lugar; sem ela, entrega o MediatR.

Guia tem um limite: o modelo pode ler e não seguir. Por isso a regra que importa ganha também um
sensor.

## 3. Sensores: o que confere o que o agente fez?

Sensor é o que confere o resultado depois da ação. É controle de retorno: acha o erro que o guia
não evitou e devolve ao agente para corrigir.

Há dois tipos:

- **computacional:** um script que lê o artefato e decide sozinho. É determinístico, roda em
  segundos e não gasta crédito. Exemplos: os guardas em `hooks/scripts/` e o `scripts/audit.py`.
- **inferencial:** outro agente julga o artefato. Pega o que script não pega, como legibilidade ou
  dado sensível num log, mas pode errar. Exemplos: o `quality` e o `security` na revisão.

**Exemplo: o `no_dispatcher` e o teste dele.** O guarda roda antes de toda escrita. O teste em
`hooks/tests/test_guards.py` tem dois casos que mostram o que ele vê:

| Escrita | Resultado |
|---|---|
| `C:/x/src/Handler.cs` com `using MediatR;` | recusada |
| `C:/x/README.md` com `using MediatR;` | liberada |

O guarda só olha código C#. Em documentação, falar do MediatR é legítimo.

**Exemplo: o `writing_guard`.** Ele roda depois de cada escrita em documento e devolve ao agente os
achados: frase acima de 40 palavras, sigla usada sem definição, emoji e muleta de texto. Não recusa,
avisa. Este guia passou por ele a cada edição, e é por isso que o título não traz a sigla BKS.

Toda regra do kit está no `rules.json`, ligada à fonte que a enuncia e ao sensor que a confere.
Alguns exemplos:

| Regra | Sensor | Tipo |
|---|---|---|
| COD-01 · sem MediatR nem dispatcher em C# | `hooks/scripts/no_dispatcher.py` | computacional |
| COD-09 · sem FluentAssertions; `Assert` nativo do xUnit | `hooks/scripts/dotnet_project.py` | computacional |
| DOC-05 · frase até 40 palavras, sigla definida, sem emoji | `hooks/scripts/writing_guard.py` | computacional |
| COD-17 · dado sensível não vai para log | `agents/security.md` | inferencial |
| SEC-01 · SQL só com parâmetro | teste de arquitetura de cada stack | computacional |
| COD-06 · exceção de negócio não escapa | `agents/quality.md` | inferencial |
| PRC-06 · só o usuário promove aprendizado | nenhum | — |

São 51 regras, e 5 não têm sensor. O `docs/regras.md`, gerado pelo `scripts/rules_report.py`, lista
quais são. Regra sem sensor é intenção declarada, não garantia.

O mesmo guarda vale em três momentos: antes da ação do agente (hook do Claude Code), antes do commit
(pre-commit) e no servidor de integração contínua (CI). As três camadas chamam o mesmo código.

## 4. A equipe: quem faz o quê?

O `bkhar` divide o trabalho em sete papéis. Quem escreve não revisa o que escreveu, e quem
especifica não implementa.

| Papel | Faz | Não faz |
|---|---|---|
| `manager` (Gerente) | conduz o rito, chama os outros, expõe o conflito | não opina sobre técnica |
| `architect` | escreve FEAT, TASK e ADR (registro de decisão) | não escreve código de produção |
| `tester` | escreve o TEST e o RED (o teste que falha antes do código) | não revisa os próprios testes |
| `developer` | implementa uma tentativa por vez | não commita nem revisa o próprio código |
| `security` | lê FEAT e diff pelo ângulo de dado sensível, segredo e injeção | não escreve |
| `quality` | revisa legibilidade, testes e resultados | não escreve |
| `scribe` | grava ADR e documentação do que foi verificado | não afirma teste sem evidência |

O Gerente não é subagente: é o protocolo que a sessão principal segue (skill `bks-team`), porque só
ela conversa com o usuário no meio do trabalho. Os outros seis são subagentes em `agents/`.

O fluxo do método SDD (desenvolvimento guiado por especificação) passa por portões. Cada portão é um
arquivo aprovado, e o comando seguinte não roda sem ele:

```
note → canonize → prd → plan → arch (portão) → refine/spec (FEAT e TEST aprovados)
     → tasks → loop (RED confirmado, revisão) → review
```

Há dois modos de condução, gravados no `.bks-profile.json`:

- **`collaborative`**, o padrão: cada portão espera o ok do usuário.
- **`autonomous`**: os portões seguem sem esperar. O modo só é concedido pelo `scripts/readiness.py`,
  que confere canônico, PRD (documento de requisitos do produto), plano e grafo aprovados. O que o
  agente precisou presumir vai para `decisions/SUPOSICOES.md`. Dado pessoal, autorização e segredo
  não se presumem: param em `outputs/BLOQUEIO-*.md`.

**Exemplo: o passo 0 do `/bkhar:loop`.** Antes de qualquer código, o `tester` escreve em código os
cenários que a task carrega, e eles têm de falhar. O portão "RED confirmado" vira commit na branch
`task/T-NNN`. Só então o `developer` recebe a primeira tentativa. Se o próprio `developer`
escrevesse o teste, a regra de quem testa não ser quem faz passar ficaria só no texto.

## 5. Travas: o que o agente não pode fazer?

Trava é o sensor computacional que recusa a ação antes que ela aconteça. Não depende de o modelo
concordar: o hook devolve a recusa, e a ferramenta não roda.

**Exemplo: o `secret_guard` e o `git reset --hard`.** Os casos de `hooks/tests/test_secret_guard.py`:

| Comando | Branch | Resultado |
|---|---|---|
| `git reset --hard HEAD~1` | branch de trabalho | recusado |
| `git status && git reset --hard` | branch de trabalho | recusado |
| `git reset --soft HEAD~1` | qualquer | liberado |

O `reset --hard` só passa em `task/T-NNN` ou `wave/N/T-NNN`, onde o `recovery.py` volta a um ponto
seguro da task. Na branch de trabalho, ele levaria junto o que o usuário commitou. O mesmo guarda
recusa ler arquivo de segredo (`.env`, chave privada, certificado), gravar credencial com valor
real, apagar em massa e escrever fora do projeto. Ele recusou até um comando deste guia: o texto
que ia ser gravado citava o `.env`.

**Exemplo: o `architect_bash`.** No papel `architect`, o Bash só roda scripts do plugin, `git` de
leitura e `maestri ask`, e a escrita só vale em `specs/`, `decisions/`, `docs/` e `outputs/`. O
arquiteto especifica; se ele pudesse gravar em `src/`, a separação de papéis do capítulo 4 seria
só combinada.

**Exemplo: o teto de 4 tentativas.** O `/bkhar:loop` dá ao `developer` no máximo quatro tentativas
por task. O contador só sobe. Na quarta falha, o loop grava `outputs/BLOQUEIO-T-NNN.md` com o
diagnóstico e as opções. Só o usuário destrava, com `/bkhar:loop T-NNN --resume` e o que mudou. O
terceiro bloqueio da mesma task a devolve ao `/bkhar:refine`: aí o defeito está na especificação.

Nem toda trava é hook. Os portões do capítulo 4 e o `/bkhar:brain` sem `STATUS.md` seguem o mesmo
princípio: sem a entrada escrita, o comando para e pergunta em vez de inventar.

O limite é declarado. A regra de escrita fora do projeto vigia o Write e o Edit, não o Bash, que
escreve onde quiser. As travas protegem contra acidente, não contra um agente decidido a burlá-las.

## 6. Memória: como o trabalho sobrevive ao fim da sessão?

O modelo não lembra da sessão anterior. Tudo que precisa durar vira arquivo no repositório do
projeto.

| Arquivo | Guarda | Quem escreve |
|---|---|---|
| `STATUS.md` | onde parou, o que trava, próximo passo | `/bkhar:save` |
| `JOURNAL.md` | um marco por sessão, em ordem | `/bkhar:save` |
| `decisions/ADR-*.md` | decisão com as opções descartadas | `scribe`, `/bkhar:save` |
| `LEARNINGS.md` | defeito resolvido, com evidência, como caso | `/bkhar:save`, com o caso que o `quality` devolveu |
| `inbox/proposals/` | correção do usuário candidata a regra | `scripts/learning.py` |

Na abertura da sessão, o hook `session_memory` carrega o `STATUS.md` e avisa se ele ficou atrás do
`JOURNAL.md` ou do git. O `/bkhar:brain` lê o mesmo arquivo e responde com o estado.

O aprendizado segue um caminho com o usuário no meio:

1. a correção vira proposta em `inbox/proposals/`;
2. o `/bkhar:retro` mostra cada uma, e o usuário promove a regra do projeto, do vault ou do kit;
3. a rejeitada vai para `archive/`, com o motivo.

O agente nunca grava regra direto. Suspeita gravada como regra vira fato, e o agente passa a
citá-la. No vault, o `/bkhar:harvest` consolida as decisões de todos os projetos por tema.

A task em execução tem memória própria. O `scripts/recovery.py` guarda o estado em
`.git/bkhar/recovery/T-NNN.json` e cada tentativa como foto em `refs/bkhar/T-NNN/impl-K`, fora do
histórico. Se a sessão cai no meio, `/bkhar:loop T-NNN --resume` volta ao último ponto seguro, e a
tentativa interrompida não conta.

## 7. Medição: como se sabe que funciona?

Um harness que não se mede vira coleção de regras que ninguém sabe se ajudam. O `bkhar` mede em
quatro pontos:

| O quê | Ferramenta | Responde |
|---|---|---|
| custo da sessão | `scripts/session_cost.py`, chamado pelo `/bkhar:save` | quantos tokens e quantos dólares, por modelo |
| custo da task | `scripts/metrics.py`, que grava o `METRICAS.md` | que fase e que papel gastam mais, onde travou |
| deriva | `scripts/audit.py` e `/bkhar:audit --deep` | guia e sensor ainda dizem a mesma coisa |
| efeito das skills | `claude plugin eval .` sobre `evals/` | a skill muda o comportamento do modelo |

O eval roda cada caso de `evals/<caso>/case.yaml` em dois braços: com o plugin e sem ele. O número
que importa é o delta entre os dois, não a nota. Nota alta nos dois braços mostra que o modelo já
sabia; o caso não mede a skill.

**Exemplo: a linha de base de 2026-11-19** (`evals/BASELINE.md`). Os 28 casos rodaram com
`--runs 1`, ao custo de $9,66:

- **delta médio +0,19.** O plugin ajuda, mas não em todo caso.
- **`dotnet-sem-dispatcher` com +1,00.** O braço com plugin passa inteiro; o sem plugin, em nada. É
  o caso do capítulo 2.
- **`tests-local-projeto` com 0,33 nos dois braços.** Com o diretório vazio, a skill aceita criar o
  projeto de testes em `tests/`, contra a regra do `src/`. É regressão real e está aberta.

Com uma execução por caso, a variação entre rodadas é grande: o `go-txc` deu 1,00 sozinho e 0,75 na
rodada completa. Por isso mudança de skill sai com o delta medido, e a conclusão só vale na
direção, não na segunda casa decimal.

A medição computacional também roda sem crédito: a suíte `tests/` e o `scripts/audit.py` entram em
toda mudança. Entre 2026-11-14 e 2026-11-17, a camada inferencial do `audit` achou 36 contradições
entre guias, todas corrigidas.

## 10. Glossário

| Termo | Significado |
|---|---|
| guia | instrução que o agente lê antes de agir: skill, comando, agente, template |
| sensor | o que confere o resultado depois da ação: script ou agente revisor |
| antecipação (feedforward) | controle que age antes do erro; é o papel do guia |
| retorno (feedback) | controle que acha o erro depois da ação; é o papel do sensor |
| computacional | conferido por script, determinístico, sem gastar crédito |
| inferencial | conferido por um modelo, que julga e pode errar |
| harness da ferramenta | o que o Claude Code traz: laço de execução, ferramentas, permissões |
| harness do usuário | o que o plugin `bkhar` acrescenta: o método, os papéis e os guardas |
| trava determinística | sensor computacional que recusa a ação em vez de avisar |
| portão | arquivo aprovado sem o qual o comando seguinte não roda |
| RED | o teste escrito antes do código, ainda falhando |
| eval | caso que roda o modelo com e sem o plugin e compara os dois |
| delta | a diferença de nota entre o braço com plugin e o sem plugin |
| bloqueio | `outputs/BLOQUEIO-*.md`: o ponto em que o agente para e só o usuário destrava |
