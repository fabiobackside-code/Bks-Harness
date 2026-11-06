---
description: "Liga, desliga e confere a integração do projeto com o Maestri — /bkhar:maestri [on|off|check]. Grava o bloco maestri do .bks-profile.json, valida se os terminais da equipe existem com os nomes do mapa e diz o que criar quando falta."
---

Configura como o harness usa o workspace do Maestri onde a sessão está. Rode no terminal `manager`,
**na raiz do repo do projeto**. Na raiz do vault, recuse e peça para abrir a sessão na pasta do
projeto.

Uso: `/bkhar:maestri` · `/bkhar:maestri on` · `/bkhar:maestri off` · `/bkhar:maestri check`

Argumento: `$ARGUMENTS`

A integração é opcional. Sem o bloco `maestri` no perfil, ou com `enabled: false`, tudo roda como
fora do Maestri: papéis por subagente e comandos na própria sessão.

## Sem argumento ou `check`

Rode e cole a saída inteira:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py show .
python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py check .
```

Saída 0 do `check`: diga em uma linha que a equipe está pronta. Saída 1: para cada linha `falta:`,
diga o que o usuário faz no canvas (seção "Montar o que falta") e pare.

## `on`

1. Rode `maestri list` e cole a saída. Sem resposta, a sessão não está no Maestri: diga isso e pare.
2. Compare os terminais conectados com o mapa padrão:

   | Vaga | Terminal padrão | Comando do terminal | Para quê |
   |---|---|---|---|
   | `manager` | `manager` | `claude` (ou `bkhar`) | este terminal: conduz e recebe todos os gates |
   | `architect` | `architect` | `claude --agent bkhar:architect` | FEAT, TASK, ADR, perguntas de contexto; roda os delegados `arch`, `prd` e `plan` |
   | `developer` | `developer` | `claude --agent bkhar:developer` | tentativas do LOOP-4 |
   | `tester` | `tester` | `claude --agent bkhar:tester` | TEST e RED |
   | `quality` | `quality` | `claude --agent bkhar:quality` | revisão |
   | `security` | `security` | `claude --agent bkhar:security` | revisão em área sensível |
   | `scribe` | `scribe` | `claude --agent bkhar:scribe` | ADR de painel |
   | executor `ops` | `ops` | `claude --model opus` | roda os comandos delegados `canonize`, `save` e `maintainability` |

   Terminal com outro nome para a mesma vaga: pergunte se é o mesmo papel e use `--role vaga=nome`.
3. Mostre o bloco que vai gravar e espere o ok. Depois rode:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py on . [--role vaga=nome ...] [--delegate comando=vaga|local ...]
   ```

   `--delegate save=local` tira um comando da delegação; `--delegate arch=ops` manda a arquitetura
   ao executor. O script recusa delegar ao `quality`, `security` ou `scribe` um comando que precisa
   de Bash (`arch`, `plan`, `save`).
4. O `on` termina com o `check`. Para cada `falta:`, oriente pela seção abaixo.
5. Nota de status ausente: com o ok do usuário, crie-a com `maestri note create --name "status"` e
   rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .`.
6. Lembre que o `outputs/run/status-canvas.md` e o `outputs/run/handoff/` ficam fora do git do
   projeto: se o `.gitignore` do projeto não os tiver, mostre as duas linhas e pergunte antes de
   acrescentar.

## `off`

Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py off .`. O mapa fica guardado e volta no
próximo `on`. Diga que, a partir de agora, os papéis vão por subagente e os comandos rodam neste
terminal.

## Montar o que falta

A criação é do usuário, no canvas: o harness não cria nem dispensa terminal, e o Maestro Mode fica
desligado.

- **Terminal faltando:** ferramenta Terminal, preset "Claude Code", o nome da vaga, o comando da
  tabela na aba Details e Connect só com o `manager`.
- **Este terminal com outro nome:** renomeie para `manager`, ou grave o nome com
  `--role manager=<nome>`.
- **Terminal fora do mapa:** não é erro. O despacho o ignora; desconecte se não tiver uso.
- **Mapa `models` no perfil:** acrescente `--model <id>` ao comando do papel.

Pronto o canvas, salve a partitura (`bkhar-equipe`) para inserir nos outros projetos.

Não commite. Responda em português do Brasil.
