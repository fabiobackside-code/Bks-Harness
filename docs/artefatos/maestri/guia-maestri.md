# Guia do Maestri — Usar o harness com terminais de agente

Versão 1.0.0, testado com o Maestri 0.30.1 para Windows, o Claude Code 2.1.319 e o plugin `bkhar` 3.0.0-beta.

## Antes de começar

Este guia mostra como usar o harness `bkhar` dentro do Maestri, com cada papel da equipe no seu
próprio terminal, e o que muda quando a sessão roda num terminal comum. Ele pressupõe o harness
instalado e uma primeira sessão feita: se ainda não chegou lá, siga antes o treinamento
(`docs/artefatos/treinamento/treinamento-bks-harness.md`).

A regra que organiza tudo: **o Gerente do harness conduz, e o Maestri só mostra e transporta.** A
memória do projeto continua nos arquivos de sempre (`STATUS.md`, `JOURNAL.md`, `decisions/`), e nada
no canvas a substitui.

> **Beta.** A integração com o Maestri chegou na 3.0.0-beta e ainda está em prova num projeto
> piloto. Sem o bloco `maestri` no perfil do projeto, o harness funciona como na 1.1.0.

## O que é o Maestri

O [Maestri](https://www.themaestri.app) é um aplicativo de área de trabalho para agentes de inteligência artificial. Num
canvas, você posiciona terminais de agente, notas em markdown e portais de navegador, e liga uns aos
outros por conexões. Um terminal conectado a outro pode mandar pedidos a ele e ler as respostas pela
CLI `maestri`, que o aplicativo instala.

| Conceito | O que é no Maestri | Como o harness usa |
|---|---|---|
| Workspace | espaço de trabalho com diretório e ambiente | um por projeto, com o diretório na raiz do repositório e o ambiente **Local** |
| Canvas | área onde ficam terminais, notas e conexões | a equipe inteira à vista |
| Terminal | processo de agente num quadro do canvas | um por papel; o nome do terminal é o nome do papel |
| Conexão | linha que deixa um terminal falar com outro ou ler uma nota | em estrela: cada terminal liga só ao `manager` |
| Nota | markdown no canvas, lido e escrito pela CLI | a nota `status`, espelho gerado do estado do projeto |
| Partitura | equipe salva para inserir de novo | a equipe montada uma vez e reaproveitada nos outros projetos |
| Role | prompt fixo que abre o agente num subdiretório | **não usado**: o subdiretório afastaria o agente do `STATUS.md` |
| Maestro Mode | deixa um agente criar e dispensar outros | **sempre desligado**: dois orquestradores brigariam pelo comando |

## Dois jeitos de rodar

O mesmo comando funciona nos dois jeitos. O que decide é o bloco `maestri` do `.bks-profile.json`
do projeto e se a sessão está num terminal do Maestri.

| Situação | Papéis da equipe | Comandos delegáveis | Nota de status |
|---|---|---|---|
| Maestri, bloco ligado, terminal conectado | terminal do papel | `architect` ou `ops` | arquivo, nota e barra lateral |
| Maestri, bloco ligado, terminal ausente | subagente, com o motivo em uma linha | no `manager` | arquivo e nota |
| Maestri, bloco desligado ou ausente | subagente | na própria sessão | só o arquivo |
| Terminal comum | subagente | na própria sessão | só o arquivo |

## Montar o workspace

Crie um workspace por projeto, com o diretório na raiz do repositório do projeto e o ambiente
**Local**. O harness guarda o estado nos arquivos do projeto, então não precisa que o processo
sobreviva ao fechamento do aplicativo; o WSL (Subsistema Windows para Linux) trocaria os caminhos
do Windows e quebraria os guardas.

&#91;embedded content: equipe no canvas\]

| Terminal | Comando (aba Details) | Ferramentas | Como devolve o resultado |
|---|---|---|---|
| `manager` | `claude` (ou `bkhar`, para outro provedor) | todas | é onde você lê e decide |
| `architect` | `claude --agent bkhar:architect` | Bash limitado por guarda | resposta inteira |
| `developer` | `claude --agent bkhar:developer` | com Bash | resposta inteira |
| `tester` | `claude --agent bkhar:tester` | com Bash | resposta inteira |
| `quality` | `claude --agent bkhar:quality` | só leitura | última tela e arquivo |
| `security` | `claude --agent bkhar:security` | só leitura | última tela e arquivo |
| `scribe` | `claude --agent bkhar:scribe` | sem Bash | última tela e arquivo |
| `ops` | `claude --model opus` | todas | resposta inteira |

O `--agent` faz a sessão assumir o perfil, as ferramentas e o modelo do agente, os mesmos do
subagente. Se o projeto tiver o mapa `models` no perfil, acrescente `--model <id>` ao comando.

O `ops` não é papel da equipe: só executa os comandos delegados `canonize`, `save` e
`maintainability`. Troque para `--model sonnet` se quiser gastar menos.

O Bash do `architect` é limitado pelo guarda `hooks/scripts/architect_bash.py`: scripts do plugin,
`git` de leitura e `maestri ask`, um comando por chamada. A escrita dele só passa em `specs/`,
`decisions/`, `docs/` e `outputs/` do projeto.

Passo a passo no canvas:

1. Crie o workspace pela barra lateral.
2. Para cada linha da tabela, use a ferramenta Terminal com o preset "Claude Code", dê o nome exato e
   ajuste o comando na aba Details.
3. Desligue o Maestro Mode em todos os terminais (aba Details).
4. Conecte cada terminal ao `manager` pelo botão Connect, e só a ele.
5. No `manager`, crie a nota com nome fixo: `maestri note create --name "status"`. Sem `--name`, a
   nota é renomeada pela própria primeira linha a cada escrita.
6. No `manager`, rode `/bkhar:maestri on` até o `check` passar.
7. Salve a partitura. Nos próximos projetos, insira a partitura e rode `/bkhar:maestri on`.

**Mais terminais não são necessários.** Os comandos delegados rodam um de cada vez, e um `ops`
basta. Terminal a mais no canvas não quebra nada: o `check` o aponta como fora do mapa, e o
despacho o ignora.

**Confira.** No `manager`, `maestri list` mostra os sete outros terminais e a nota `status`, todos
conectados a ele.

## Ligar, desligar e conferir

O `/bkhar:maestri` roda no `manager`, na raiz do projeto, a qualquer momento.

| Comando | O que faz |
|---|---|
| `/bkhar:maestri` ou `check` | mostra o bloco e confere o nome deste terminal, os seis papéis, o `ops`, a nota e o mapa de delegação |
| `/bkhar:maestri on` | lê o `maestri list`, pergunta pelo terminal de nome diferente, grava o bloco com o seu ok e confere |
| `/bkhar:maestri off` | desliga e guarda o mapa para o próximo `on` |

O bloco gravado no `.bks-profile.json`:

```json
"maestri": {
  "enabled": true,
  "manager": "manager",
  "roles": { "architect": "architect", "developer": "developer", "tester": "tester",
             "quality": "quality", "security": "security", "scribe": "scribe" },
  "executors": { "ops": "ops" },
  "notes": { "status": "status" },
  "delegate": { "arch": "architect", "prd": "architect", "plan": "architect",
                "canonize": "ops", "save": "ops", "maintainability": "ops" }
}
```

Terminal com outro nome: `--role developer=dev`. Tirar um comando da delegação:
`--delegate save=local`. O script recusa delegar `arch`, `plan` ou `save` ao `quality`, ao
`security` ou ao `scribe`, que não têm Bash.

O `on` lembra também de deixar fora do git do projeto o `outputs/run/status-canvas.md` e o
`outputs/run/handoff/`, e pergunta antes de acrescentar as linhas ao `.gitignore`.

**Confira.** `/bkhar:maestri check` termina em `ok: manager, 6 papéis e a nota de status conectados`.

## Trabalhar no modo colaborativo

1. Abra o workspace e só os terminais que a etapa usa. Papel fechado cai para subagente, e você não
   paga o custo fixo de sessão dele.
2. No `manager`, rode `/bkhar:brain`: ele diz onde o projeto parou e qual é o próximo passo.
3. Rode o comando que o `STATUS.md` indica. Nos ritos (`refine`, `spec`, `loop`, `review`, `panel`,
   `ask`), o Gerente limpa a sessão do papel com `/clear`, manda o pedido com os arquivos a ler, e
   você vê o trabalho no terminal do papel.
4. Em cada portão, o `manager` para com as opções numeradas. Responda ali.
5. Falar direto com um papel no terminal dele é permitido. O Gerente lê esse terminal
   (`maestri check`) antes de seguir.
6. Feche com `/bkhar:save` no `manager`. Ele roda delegado no `ops` e regera a nota.

| Etapa | Terminais abertos |
|---|---|
| canônico | `manager`, `ops` |
| PRD (requisitos do produto), plano e arquitetura | `manager`, `architect` |
| refinamento e especificação | `manager`, `architect`, `tester` |
| construção | `manager`, `tester`, `developer` |
| revisão | `manager`, `quality`, `security` |
| fechamento | `manager`, `ops` |

Não há save automático ao fechar terminal. O que não passou pelo `/bkhar:save` fica só na conversa.

**Confira.** Num `/bkhar:ask architect ...`, o pedido aparece no terminal do `architect` e a resposta
volta ao `manager` com a fonte citada.

## Trabalhar no modo autônomo

1. Rode `/bkhar:mode autonomo` no `manager`. A checagem de prontidão concede o modo ou diz o que
   falta.
2. Abra os terminais de construção e revisão, e o `architect` se a onda tiver tarefa de desenho.
3. Rode `/bkhar:loop --wave next`: até 4 tarefas em paralelo, cada uma na sua worktree, com até 4
   tentativas por tarefa.
4. Acompanhe pela nota `status` e pela barra lateral. Os estados `blocked` e `review` notificam você.
5. No portão ou no fim, a nota basta para validar. O detalhe fica em `specs/tasks/` e em
   `outputs/run/onda-N/RELATORIO.md`.

A nota é regerada inteira pelo `scripts/status_note.py` em cada ponto de controle. Ninguém escreve
nela à mão, e ela nunca substitui o `STATUS.md`:

```
# Status · meu-projeto
> Espelho gerado de STATUS.md e outputs/run/. Não editar à mão. Atualizado: 2026-11-06 15:30

Modo: autonomo · Etapa: onda 2 de 5 — construcao · Concluídas: 3/9

## Em uma frase
## Próximo passo
## Itens da spec
## Falhas
## Bloqueios
```

**Confira.** Com a onda rodando, a barra lateral mostra a etapa e o progresso, como `3/9`.

## Comandos delegados

`arch`, `prd` e `plan` rodam no `architect`; `canonize`, `save` e `maintainability`, no `ops`.
Nenhum ocupa a conversa do `manager`, e você continua chamando-os ali.

1. Você digita `/bkhar:save` no `manager`.
2. O primeiro passo do comando consulta o perfil e recebe `terminal ops`.
3. O `manager` grava `outputs/run/handoff/save.md` com as decisões da sessão e o que cada papel
   produziu. O `ops` não viu a conversa: o arquivo é o canal.
4. O `manager` limpa o `ops` e pede o comando.
5. Toda pergunta do `ops` volta ao `manager` como portão. Você responde no `manager`, e ele devolve
   a resposta ao `ops`.
6. No fim, o `manager` mostra o resultado, regera a nota e arquiva o handoff.

Enquanto o terminal delegado escreve, o `manager` não toca no `STATUS.md`, no `JOURNAL.md` nem em
`decisions/`: há um escritor de estado por vez.

**Confira.** Depois do `/bkhar:save` delegado, o handoff está em `outputs/run/handoff/aplicados/`.

## Responder aos portões

O portão sempre aparece no `manager`, inclusive o que nasce num terminal delegado. O formato é fixo:
opções numeradas, quem defende cada uma, a fonte e o conflito exposto. Responda com o número, ou com
"outra:" e o texto. Em pergunta de duas alternativas exclusivas, responda com a opção nomeada, não
com "sim".

O Maestri Remote, o aplicativo para celular, abre um terminal real e permitiria responder pelo
telefone. Ele exige o Maestri Wire ligado, o que abre acesso remoto à máquina; o harness não foi
testado com ele.

## Fora do Maestri

Num terminal comum, na raiz do projeto:

1. Rode `claude`, ou `bkhar` para outro provedor.
2. Use `/bkhar:brain`, os mesmos comandos e o `/bkhar:save` no fim.
3. Os papéis rodam como subagentes: você vê o resultado, não o trabalho de cada um.
4. Os comandos delegáveis rodam na própria sessão; o primeiro passo responde
   `local: sessão fora do Maestri`.
5. A nota de status vira só o arquivo `outputs/run/status-canvas.md`.

Nada precisa ser desligado para sair do Maestri. O `/bkhar:maestri off` serve para quando você quer
subagentes mesmo dentro dele.

## Problemas e recuperação

| Sintoma | O que fazer |
|---|---|
| `Unknown command: /bkhar:maestri` | a sessão foi aberta antes de o plugin ganhar o comando; saia com `/exit` e abra de novo com `claude --continue` |
| O `check` acusa terminal faltando ou com outro nome | crie ou renomeie no canvas, ou grave o nome com `--role vaga=nome` |
| O `manager` espera um terminal há muito tempo | `maestri check "<nome>"` mostra a tela; se estiver num pedido de permissão, responda lá; nunca reenvie o pedido |
| O `/clear` chegou como `C:/Program Files/Git/clear/n` | foi o Git Bash; apague a linha (Ctrl-U) e envie pelo PowerShell, ou prefixe com `MSYS_NO_PATHCONV=1` |
| Um papel "esqueceu" o contexto | é o `/clear` funcionando; o pedido tem de nomear os arquivos a ler |
| O `save` delegado deixou de fora uma decisão | o handoff estava incompleto; diga a decisão no `manager` e rode `/bkhar:save` de novo |
| A nota está velha ou mudou de nome | `python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .`; se o nome mudou, recrie com `--name "status"` |
| `Bloqueado no architect` | o guarda recusou um comando fora dos três usos do papel; o pedido é do `developer` ou do `tester` |
| "Invalid API key" num terminal | uma `ANTHROPIC_API_KEY` inválida no ambiente da máquina; remova ou corrija a variável |

## Exercícios

| # | Faça | Resultado esperado |
|---|---|---|
| 1 | `/bkhar:maestri check` | `ok: manager, 6 papéis e a nota de status conectados` |
| 2 | `/bkhar:ask architect qual é a fronteira de contexto do módulo principal?` | o pedido aparece no terminal do `architect`; a resposta volta ao `manager` com fonte |
| 3 | feche o terminal do `architect` e repita o exercício 2 | o `manager` avisa que o terminal não está conectado e responde por subagente |
| 4 | no terminal do `architect`, peça "rode `dotnet --version`" | `Bloqueado no architect`; um `git status` passa |
| 5 | `/bkhar:save` no `manager` | o `ops` trabalha, as perguntas aparecem no `manager`, a nota é regerada |
| 6 | `/bkhar:maestri off` e repita o exercício 2 | resposta por subagente, nada no terminal do `architect`; depois, `on` |
| 7 | `/bkhar:panel` com uma pergunta de modelagem | dois ou três papéis trabalham ao mesmo tempo; o `manager` para com as opções; o `scribe` grava o ADR (registro de decisão) |
| 8 | num terminal comum, `claude` e o exercício 2 | resposta por subagente; o primeiro passo dos comandos delegáveis responde `local` |

## Referência rápida

| Comando | Para quê |
|---|---|
| `maestri list` | quem está conectado |
| `maestri ask "<nome>" "<pedido>"` | pedido; espera o terminal ficar ocioso (dê até 10 minutos) |
| `maestri ask --batch '{"A": "...", "B": "..."}'` | pedidos em paralelo |
| `maestri ask "<nome>" --raw "/clear\n"` | limpa a sessão do terminal |
| `maestri check "<nome>"` | lê a tela atual |
| `maestri note create --name "status"` | nota com nome fixo |
| `maestri floor status "<texto>" --state working\|blocked\|review\|done --progress n/m` | estado na barra lateral |
| `/bkhar:maestri [on\|off\|check]` | integração do projeto |
| `python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py route . --role <papel>` | para onde o papel vai agora |
| `python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .` | regera a nota |

As decisões por trás deste guia estão em `docs/ARCHITECTURE.md`, nas seções sobre o Maestri.

## Histórico de versões

| Versão | Data | O que mudou |
|---|---|---|
| 1.0.0 | 2026-11-06 | Primeira versão, com o `bkhar` 3.0.0-beta |
