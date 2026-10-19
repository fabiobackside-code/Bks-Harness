# Treinamento do bks-harness — Instalação e uso

Versão 1.0.0, testado com o Claude Code 2.1.303 e o plugin `bkhar` 0.9.0.

## Antes de começar

Este manual leva você do zero até a primeira sessão produtiva e, depois, a um ciclo completo com a
equipe de agentes. Ele é um roteiro, não uma referência: siga os capítulos na ordem.

Cada capítulo fecha com **Confira**, o que deve aparecer na sua tela se o passo deu certo. Não
avance com uma conferência falhando. Os capítulos de uso trazem também um **Exercício** curto.

O harness (o conjunto de ferramentas em volta do modelo) tem duas peças que você instala:

- **o kit**, o plugin `bkhar` do Claude Code, publicado no repositório `Bks-Harness`;
- **o vault**, opcional, o template `bks-2brains`, onde ficam o seu perfil, o seu conhecimento e
  os seus projetos.

Os caminhos deste manual são exemplos, como `C:\dev\2brains`. Troque pelos seus.

Para o porquê de cada decisão, leia o Atlas. Para o detalhe de cada comando, o manual de comandos,
que é a Parte X do Atlas. Os dois estão em `docs/artefatos/` do repositório.

## Parte 1 — Instalação

### 1. O que você vai instalar

O **kit** é o motor. Traz as skills (instruções que o agente carrega sob demanda), os comandos
`/bkhar:*`, os seis agentes da equipe e os guardas, scripts que recusam a escrita fora do padrão.
Instala uma vez por máquina e vale em qualquer pasta.

O **vault** é a memória entre projetos. Guarda quem você é (`workbench/`), o que você aprendeu
(`knowledge/`) e os seus projetos (`repos/`). É opcional: sem ele, o kit funciona no diretório
onde a sessão estiver aberta.

O **projeto** guarda o próprio estado: `STATUS.md`, specs, decisões e código, com git próprio.
Nenhum comando depende de um hub central.

&#91;embedded content: kit, vault e projeto\]

**Confira.** Você sabe responder: se eu apagar o vault, o kit continua funcionando? Sim. O que se
perde é a memória entre projetos.

### 2. Antes de começar

| Requisito | Para quê | Como conferir |
|---|---|---|
| Claude Code, instalado e autenticado | é onde o plugin roda | `claude --version` |
| `git` | clonar o vault e versionar os projetos | `git --version` |
| Python 3 no `PATH`, chamado `python` | os guardas são scripts Python | `python --version` |

O manual foi testado com o Claude Code 2.1.303. Versões mais novas devem funcionar; se algo
divergir, confira a versão antes de qualquer outra coisa.

O Python é obrigatório, mesmo sem escrever uma linha de Python. Os guardas rodam antes de cada
escrita de arquivo; se o comando `python` não existir, eles falham em toda escrita.

No Windows, o instalador do Python tem a opção de pôr o `python.exe` no `PATH`. Marque. Se o terminal
responder `python3` mas não `python`, crie o alias ou reinstale com a opção marcada.

**Confira.** Os três comandos da tabela respondem com uma versão, sem erro.

### 3. Instalar o plugin

Dentro de uma sessão do Claude Code:

```
/plugin marketplace add fabiobackside-code/Bks-Harness
/plugin install bkhar@bks-harness
```

Ou pelo terminal, fora da sessão:

```
claude plugin marketplace add fabiobackside-code/Bks-Harness
claude plugin install bkhar@bks-harness
```

Três nomes aparecem aqui, e cada um tem um papel:

| Nome | É o quê |
|---|---|
| `Bks-Harness` | o repositório no GitHub |
| `bks-harness` | o marketplace, o catálogo que o Claude Code registra |
| `bkhar` | o plugin, e o prefixo dos comandos: `/bkhar:brain` |

O plugin entra no escopo `user`: vale em qualquer pasta da máquina. Feche a sessão e abra outra
para os comandos aparecerem; a instalação avisa `Restart to apply changes`.

Para instalar a partir de um clone local, troque o primeiro comando por
`claude plugin marketplace add <pasta-do-clone>`, por exemplo `C:\dev\bks-harness`. Nesse caso o
plugin é lido direto da pasta: o que estiver no disco vale na próxima sessão.

&#91;embedded content: caminho da instalação\]

**Confira.** `claude plugin list` mostra:

```
❯ bkhar@bks-harness
  Version: 0.9.0
  Scope: user
  Status: ✔ enabled
```

E `claude plugin details bkhar@bks-harness` lista `Agents (6)  architect, developer, quality,
scribe, security, tester` e os hooks `PreToolUse`, `SessionStart` e `PostToolUse`. O custo fixo
fica em torno de 3,2 mil tokens por sessão.

### 4. Montar o vault (opcional)

Pule este capítulo se quiser só o kit. Volte a ele quando sentir falta de memória entre projetos.

**Clonar e desligar do template.** O template já cumpriu o papel dele; o seu vault é outro
repositório:

```
git clone https://github.com/fabiobackside-code/bks-2brains C:\dev\2brains
cd C:\dev\2brains
rm -rf .git
git init
git add -A
git commit -m "chore: vault inicial a partir do template"
```

No PowerShell, troque o `rm -rf .git` por `Remove-Item -Recurse -Force .git`.

Se for publicar o seu vault, use um repositório **privado**. A partir do perfil, ele guarda o que
é seu.

**Apontar o kit para o vault.** Duas variáveis de ambiente, em `~/.claude/settings.json`:

```json
{
  "env": {
    "BKS_VAULT": "C:/dev/2brains",
    "BKS_KNOWLEDGE": "C:/dev/2brains/knowledge"
  }
}
```

No Windows, barras normais funcionam. Abra uma sessão nova depois de salvar: a sessão aberta antes
não enxerga a variável.

**Escrever o perfil.** É o arquivo que o agente lê em toda sessão, de qualquer projeto:

```
cp workbench/profile.example.md workbench/profile.md
```

Reescreva com o seu conteúdo: experiência, stack, arquitetura padrão, regras inegociáveis e
preferências de resposta. Escreva regra, não desejo. "Nunca use MediatR, a orquestração é
explícita" muda o comportamento do agente; "gosto de código limpo" não muda nada.

&#91;embedded content: mapa do vault\]

**Confira.** Abra o Claude Code na pasta do vault e pergunte: "Leia o profile.md. O que você
entendeu sobre como eu trabalho?" A resposta mostra o que o perfil comunica de fato.

### 5. Conferir que está de pé

| # | Conferência | Resultado esperado |
|---|---|---|
| 1 | `python --version` | uma versão 3.x |
| 2 | `claude plugin list` | `bkhar@bks-harness`, `enabled` |
| 3 | digitar `/bkhar:` numa sessão nova | a lista mostra `brain`, `ask`, `panel`, `save` e os demais |
| 4 | `/bkhar:brain` na pasta do vault | o panorama, vazio se não há projeto |
| 5 | `/bkhar:brain` numa pasta sem vault nem `STATUS.md` | ele pergunta onde você quer trabalhar |

O item 4 só vale com vault. O item 5 mostra que o comando não adivinha: sem estado, ele pergunta.

**Confira.** Os cinco itens batem, ou os quatro sem o item 4, se você não montou o vault.

### 6. Quando algo não aparece

Só os casos já vistos na prática:

| Sintoma | Causa | O que fazer |
|---|---|---|
| `/bkhar:` não aparece no autocompletar | a sessão foi aberta antes da instalação | feche e abra uma sessão nova |
| digitar `brain` sugere só o comando de outro plugin | dois plugins com comando de mesmo nome | digite o prefixo `/bkhar:`, ou desligue o outro plugin no projeto, em `.claude/settings.json`, com `"enabledPlugins": {"<plugin>@<marketplace>": false}` |
| toda escrita de arquivo falha com erro de hook | `python` fora do `PATH` | volte ao capítulo 2 |
| `/bkhar:brain` não acha o vault | `BKS_VAULT` ausente ou com caminho errado | confira o `settings.json` e abra uma sessão nova |

**Confira.** Nenhum dos quatro sintomas aparece na sua máquina.

## Parte 2 — Uso

### 7. O primeiro projeto

Com vault, abra a sessão na raiz dele e rode:

```
/bkhar:new-project
```

Ele pergunta, numa rodada só, o nome, a categoria e o **perfil**, que define o que o projeto gera:
`docs`, `fullstack`, `frontend`, `backend`, `component`, `infra`, `data`, `legacy-docs` ou
`reengineering`. O projeto nasce em `repos/{categoria}/{nome}/`, com git próprio.

Sem vault, crie uma pasta com `repos/` dentro e abra a sessão nela: ela faz o papel de raiz.

O esqueleto traz os arquivos que dão memória ao projeto:

| Arquivo | Para quê |
|---|---|
| `STATUS.md` | onde o projeto parou, o que trava, o próximo passo |
| `JOURNAL.md` | os marcos, do mais recente ao mais antigo |
| `LEARNINGS.md` | defeitos resolvidos, com evidência, que o `tester` lê antes de escrever teste novo |
| `CLAUDE.md` | o contexto que o agente carrega no projeto |
| `.bks-profile.json` | o perfil e o rigor do projeto |

A partir daqui, todo comando de projeto roda **na raiz do projeto**. Abra uma sessão nova lá.

**Exercício.** Crie um projeto `docs` chamado `treino-harness`. Abra uma sessão na pasta dele e
rode `/bkhar:brain`.

**Confira.** O `/bkhar:brain` responde em poucas linhas com "onde parou", "o que trava" e
"próximo passo", lidos do `STATUS.md` novo.

### 8. O ciclo

O trabalho segue uma ordem, e você aprova entre as etapas:

| Etapa | Comando | O que produz |
|---|---|---|
| Material bruto | `/bkhar:note` | notas em `docs/input/notas/` |
| Consolidação | `/bkhar:canonize` | o contexto canônico em `docs/canonical/` |
| Produto | `/bkhar:prd` | o PRD (documento de requisitos do produto) |
| Especificação | `/bkhar:refine` ou `/bkhar:spec` | a FEAT (especificação da feature) e o TEST (os cenários) |
| Arquitetura | `/bkhar:arch` | a visão C4 (os níveis contexto, container e componente) e o README |
| Implementação | `/bkhar:loop` | código com teste, task a task |
| Revisão | `/bkhar:review` | os achados do painel |
| Fechamento | `/bkhar:save` | `STATUS.md`, `JOURNAL.md`, decisões e aprendizados gravados |

Projeto pequeno pode começar na especificação. O que não se pula é a aprovação: nenhuma etapa gera
artefato sem você aprovar a anterior.

**Refine ou spec?** O `/bkhar:refine` é o caminho com a equipe: `architect`, `tester` e
`security` fazem até três perguntas cada antes de escrever. O `/bkhar:spec` é o caminho direto,
para quando a feature já está clara.

&#91;embedded content: o ciclo\]

**Exercício.** No `treino-harness`, rode `/bkhar:note` com duas frases sobre o que o projeto deve
documentar.

**Confira.** Existe um arquivo novo em `docs/input/notas/`, com o seu texto.

### 9. A equipe

Seis agentes, cada um com as ferramentas do seu trabalho e só elas:

| Papel | Modelo | Pode | Não pode |
|---|---|---|---|
| `architect` | Opus | escrever FEAT, TASK (a tarefa do plano) e ADR (o registro de decisão) | executar comando ou escrever código de produção |
| `tester` | Sonnet | escrever o TEST e o teste que falha | revisar os próprios testes |
| `developer` | Sonnet | implementar uma tentativa por vez | commitar ou mexer no teste do `tester` |
| `security` | Opus | ler e apontar o risco com `arquivo:linha` | escrever: só lê |
| `quality` | Sonnet | julgar legibilidade, testes e resultados | escrever: só lê |
| `scribe` | Haiku | registrar o que foi confirmado | decidir o que foi feito |

O sétimo papel, o **Gerente**, é a própria sessão seguindo a skill `bks-team`. Ele chama os
agentes, junta as respostas sem reescrevê-las e para antes de gerar qualquer artefato. Não opina
sobre técnica.

Duas formas de falar com a equipe a qualquer momento:

```
/bkhar:ask security o log desta rota grava o CPF do cliente?
/bkhar:panel devo guardar o histórico em tabela própria ou em evento?
```

O `ask` chama um agente. O `panel` chama dois ou três, cada um sem ver a resposta do outro. O
Gerente numera as posições, você escolhe, e o `scribe` grava o ADR com as opções descartadas.

Os nomes aceitam português: `arquiteto`, `testes`, `dev`, `seguranca`, `qualidade`,
`documentador`. Não use `@agente` no prompt: no Claude Code, `@` menciona arquivo.

&#91;embedded content: equipe e ritos\]

**Exercício.** No `treino-harness`, rode `/bkhar:ask architect que pastas este projeto tem e para
que serve cada uma?`

**Confira.** A primeira linha da resposta anuncia o agente, como `architect - Opus - ...`. Cada
afirmação cita a fonte, e o que vier sem fonte aparece marcado como **opinião**.

### 10. Implementar e revisar

O `/bkhar:loop` implementa uma task do plano, no protocolo LOOP-4: no máximo quatro tentativas.

1. **Passo 0.** O `tester` escreve o RED (o teste que ainda falha). Você confirma que ele falha pelo
   motivo certo: é o portão "RED confirmado".
2. **Tentativas.** O `developer` implementa, uma tentativa por vez, contra os goals: build limpo,
   testes verdes, cenários do TEST cobertos.
3. **Falha.** O erro real volta como contexto da tentativa seguinte. Nada é escondido.
4. **Quarta falha.** O loop para com um `BLOQUEIO` e devolve a decisão para você.

Quem escreve o teste não é quem o faz passar. É essa separação que impede o teste de ser escrito
para caber no código.

Depois, o `/bkhar:review` revisa em painel: o `tester` confere a cobertura dos cenários, o
`quality` julga o código e os testes e, em área sensível, o `security` entra. Cada achado sai como
bloqueante, sugestão ou aprendizado.

&#91;embedded content: LOOP-4 com passo 0\]

**Exercício.** Pergunte `/bkhar:ask tester o que é o portão RED confirmado do /bkhar:loop?`

**Confira.** A resposta cita o `loop.md` como fonte, e você sabe dizer o que acontece na quarta
falha: o loop para e a decisão é sua.

### 11. Uma sessão de trabalho

Toda sessão segue o mesmo desenho:

1. **Abrir** com `/bkhar:brain`. Ele lê o `STATUS.md` e diz onde o projeto parou.
2. **Trabalhar** com os comandos e os ritos.
3. **Fechar** com `/bkhar:save`. Ele grava o estado para a próxima sessão.

O `/bkhar:save` atualiza o `STATUS.md`, acrescenta o marco no `JOURNAL.md`, grava decisões em
`decisions/` e os casos de defeito resolvido no `LEARNINGS.md`. Os ritos não gravam estado durante
a conversa; o Gerente lista o que registrar, e o `save` grava.

O estado mora em arquivo, não no histórico do chat. Retomar custa a leitura de um arquivo, não a
reconstrução da conversa.

&#91;embedded content: uma sessão\]

**Exercício.** No `treino-harness`, rode `/bkhar:save`. Feche a sessão, abra outra e rode
`/bkhar:brain`.

**Confira.** O `/bkhar:brain` da sessão nova responde com o estado que o `/bkhar:save` gravou.

### 12. Referência rápida

| Comando | Para quê | Onde rodar |
|---|---|---|
| `/bkhar:brain` | retomar: panorama ou estado do projeto | raiz do vault ou do projeto |
| `/bkhar:new-project` | criar projeto | raiz do vault |
| `/bkhar:ingest` | trazer conhecimento para `knowledge/` | raiz do vault |
| `/bkhar:note` | registrar material bruto | raiz do projeto |
| `/bkhar:canonize` | consolidar o material | raiz do projeto |
| `/bkhar:prd` | gerar o PRD | raiz do projeto |
| `/bkhar:refine` | especificar com a equipe | raiz do projeto |
| `/bkhar:spec` | especificar direto | raiz do projeto |
| `/bkhar:arch` | arquitetura e README | raiz do projeto |
| `/bkhar:loop` | implementar uma task | raiz do projeto |
| `/bkhar:review` | revisão em painel | raiz do projeto |
| `/bkhar:ask` | perguntar a um agente | qualquer ponto |
| `/bkhar:panel` | decidir com dois ou três agentes | qualquer ponto |
| `/bkhar:save` | fechar a sessão | raiz do projeto |
| `/bkhar:maintainability` | parecer de manutenibilidade de `app/` | raiz do projeto |
| `/bkhar:migrate` | trazer projeto do kit antigo `bks` | raiz do projeto |

O detalhe de cada comando, com passo a passo e exemplo, está no manual de comandos.

**Confira.** Você sabe qual comando abre e qual fecha toda sessão: `/bkhar:brain` e
`/bkhar:save`.

## Histórico de versões

| Versão | Data | O que mudou |
|---|---|---|
| 1.0.0 | 2026-10-19 | Primeira versão: instalação pelo repositório público, vault `bks-2brains`, ciclo, equipe da 0.9.0, LOOP-4 com passo 0 e sessão de trabalho |
