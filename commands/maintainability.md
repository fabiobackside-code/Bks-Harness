---
description: Inventaria as aplicações de app/, gera um parecer de manutenibilidade por aplicação e o documento único de fundamentação do projeto.
argument-hint: "[opcional: nomes das aplicações a avaliar]"
---

Avalia a manutenibilidade das aplicações concretas do projeto (APIs, Workers, Web Services,
componentes, SDKs, scripts SQL) e atualiza a fundamentação teórica e técnica que as sustenta. Use a
skill `bks-maintainability-review` para tudo que vem abaixo: persona, rubrica, critérios por stack
e templates estão nela.

Argumento: $ARGUMENTS, os nomes das aplicações a avaliar. Vazio avalia todas.

Faça, nesta ordem:

0. **Onde está.** Este comando roda no repositório de um projeto: precisa de `STATUS.md` na raiz.
   Aberto na raiz do vault (`repos/` presente), pergunte qual projeto e pare. Se `app/` não existir
   ou não tiver código, diga isso e pare. Não há o que avaliar.

1. **Inventário.** Percorra `app/` com a seção Detecção de cada arquivo em
   `${CLAUDE_PLUGIN_ROOT}/skills/bks-maintainability-review/stacks/` e mostre a tabela:

   ```
   Aplicação        Stack   Tipo          Raiz
   pedidos-api      .NET    API           app/Pedidos.Api/Pedidos.slnx
   db-scripts       SQL     Scripts SQL   app/db/
   front-web        Node    —             app/front/   stack sem critérios
   ```

2. **Pergunte antes de gastar.** Pare e pergunte, uma pergunta por vez, quando houver:
   - tipo indeterminado;
   - stack sem arquivo em `stacks/`: pular a aplicação, ou avaliar só com a rubrica e os critérios
     comuns, com confiança Baixa declarada;
   - dúvida sobre o que é uma aplicação.

   Sem dúvida e com até três aplicações, siga direto. Acima de três, confirme a lista antes: cada
   parecer lê muito código.

3. **Contexto.** Leia `CLAUDE.md`, `specs/`, `decisions/` e `brain/engineering/` do projeto. Se
   `BKS_VAULT` estiver definido, calibre a persona pelo vault como a skill descreve; sem vault,
   siga com a persona base e registre isso em cada parecer.

4. **Parecer por aplicação**, pelo modo Análise da skill, em
   `outputs/maintainability/<app>_<tipo>_<AAAA-MM-DD>.html`. Nunca sobrescreva: nome repetido ganha
   `_HHmm`. Se houver parecer anterior da mesma aplicação nessa pasta, compare com ele.

5. **Fundamentação**, uma por projeto, pelo modo Fundamentação da skill, em
   `outputs/references/`. Gere versão nova só se algum conceito ou decisão entrou, mudou ou saiu.

6. **Registro.** Grave o critério desta execução em
   `docs/prompts/prompt-maintainability-{YYYY-MM-DD}.md`: aplicações avaliadas e puladas, stack e
   tipo de cada uma, persona usada (com ou sem vault), perguntas feitas e respostas. É o que permite
   comparar duas execuções com a mesma régua.

7. **Reporte**, uma linha por aplicação: nome, nota, faixa, confiança e caminho do parecer. Depois,
   uma linha com a versão da fundamentação, ou "fundamentação sem alterações; versão atual vN".

Nunca pontue sem evidência e nunca aplique critério de uma stack a outra. Na dúvida, pergunte.
