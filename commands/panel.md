---
description: Painel — /bkhar:panel <pergunta>. O Gerente chama 2 ou 3 agentes em invocações separadas e independentes, apresenta as posições numeradas, o usuário escolhe e o scribe grava o ADR com as opções descartadas.
---

Painel de decisão, pelo protocolo do Gerente (skill `bks-team`).

Uso: `/bkhar:panel <pergunta>` — opcionalmente com os agentes: `/bkhar:panel architect,security <pergunta>`.

Passos:

1. **Escolher os agentes.** Se o usuário não disse, escolha 2 ou 3 pela tabela "Escolher o painel"
   da skill `bks-team`, diga quais e por quê em uma linha, e aceite a troca que ele pedir.
2. **Chamar.** Cada agente em invocação separada, todas em paralelo, com a mesma pergunta e o mesmo
   contexto. Nenhum agente recebe a resposta de outro: a posição precisa ser independente.
3. **Apresentar.** As posições numeradas, cada uma com quem defende, a favor, contra e fonte, no
   formato da skill `bks-team`. Conflito entre agentes aparece lado a lado, sem escolha do Gerente.
   Resposta sem fonte vem marcada como opinião.
4. **Parar e perguntar.** "Qual opção você escolhe?" Nada é gravado antes da resposta.
5. **Registrar.** Com a escolha, chame o `scribe` para gravar o ADR em `{repo}/decisions/` com o
   template `ADR.md` (precedência: `{repo}/.bks/templates/`, senao
   `${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`). As opções
   descartadas entram na seção "Alternativas descartadas e por quê", com o agente que defendeu
   cada uma.
6. **Fechar.** Liste o que o `/bkhar:save` grava: decisão pendente, se o usuário não escolheu, e os
   aprendizados dos agentes.

Sem escolha do usuário, não há ADR: a pergunta fica como decisão pendente.

Fora o ADR, o painel não grava `STATUS.md` nem `JOURNAL.md`: rito não grava estado.
