---
description: "Estado da execução em ondas — tabela das tasks por onda, o que está liberado agora, bloqueios e suposições abertas. Só lê."
---

Mostra onde a execução em ondas está. Rode na raiz do repo do projeto. Só lê: nada aqui escreve
estado.

1. Rode e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/run_state.py show .
   python ${CLAUDE_PLUGIN_ROOT}/scripts/wave_graph.py waves .
   ```

   Sem `outputs/run/`, diga que nenhuma onda começou e que a primeira roda com
   `/bkhar:loop --wave next`, no modo `autonomo`.

2. Liste os `outputs/BLOQUEIO-*.md`, um por linha, com a pergunta objetiva de cada um.
3. Conte as linhas `aberta` de `decisions/SUPOSICOES.md`.
4. Diga, em uma linha, que o painel abre com
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py .` em `http://127.0.0.1:8765`.

Responda em até doze linhas, além das tabelas coladas.
