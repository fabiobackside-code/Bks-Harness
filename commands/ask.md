---
description: Pergunta direta a um agente da equipe — /bkhar:ask <agente> <pergunta>. O agente responde pelo seu perfil e cita a fonte; resposta sem fonte vem marcada como opinião.
---

Pergunta direta a um agente da equipe, pelo protocolo do Gerente (skill `bks-team`).

Uso: `/bkhar:ask <agente> <pergunta>`

Nomes aceitos, em inglês ou português:

| Agente | Também aceito |
|---|---|
| `architect` | arquiteto |
| `tester` | testes |
| `developer` | dev |
| `security` | seguranca, segurança |
| `quality` | qualidade |
| `scribe` | documentador |

Passos:

1. Sem agente ou sem pergunta, peça o que falta e pare. Nome fora da tabela: mostre a tabela e
   pare; não adivinhe o agente.
2. Chame o agente em invocação separada, com a pergunta e só os arquivos que ela cita.
3. Devolva a resposta como veio, sem reescrever o conteúdo técnico. Cada afirmação com fonte
   (`arquivo:linha`, documento ou skill); afirmação sem fonte vem marcada como **opinião**.
4. Se a resposta pedir uma decisão, apresente as opções numeradas e pergunte ao usuário. Não gere
   artefato (FEAT, TEST, TASK, ADR ou código) sem a resposta dele.
5. No fim, liste o "Aprendizado" que o agente devolveu, para o `/bkhar:save` registrar. Lista vazia
   aparece como "nenhum".

O comando não grava `STATUS.md` nem `JOURNAL.md`: rito não grava estado.

O `@agente` digitado no prompt não chama agente — no Claude Code, `@` é menção de arquivo. O
caminho é este comando.
