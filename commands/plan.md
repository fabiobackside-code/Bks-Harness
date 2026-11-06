---
description: Gera o plano macro (outputs/PLAN-{projeto}.md) a partir do PRD — o faseamento do projeto. Obrigatório no perfil fullstack. Ponte entre /bkhar:prd e /bkhar:arch, que é o portão seguinte.
---

**Passo 0 — delegar.** Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py delegate . --command plan`.
Com `terminal <nome>`, siga a seção "Delegação de comando" da skill `bks-team` e não execute
os passos abaixo neste terminal. Com `local: <motivo>`, siga normalmente.

Gera o plano macro do projeto a partir do PRD — é a ponte entre /bkhar:prd e a especificação por
fase.

Rode na raiz do repo do projeto.

Pré-requisito: docs/canonical/PRD-{projeto}.md existe. Se não existir, PARE e oriente a rodar
/bkhar:prd primeiro — nunca gere plano direto do CONTEXT.md, de docs/input/ ou de docs/design/.

Faça, nesta ordem:

1. Leia o `.bks-profile.json`. No perfil `fullstack` o plano é obrigatório, e também em qualquer
   perfil que vá para o modo `autonomo`: a prontidão exige o plano e o grafo. Nos demais casos,
   diga em uma linha que o plano é opcional ali e pergunte se segue.

2. Leia docs/canonical/PRD-{projeto}.md, docs/canonical/CONTEXT.md e o plano anterior em
   outputs/PLAN-{projeto}.md, se existir, para não regredir no que já foi faseado.

3. Gere o plano pela estrutura da skill `bks-sdd`, em
   `${CLAUDE_PLUGIN_ROOT}/skills/bks-sdd/references/plan-structure.md`: visão geral, fases de
   execução, features previstas, dependências externas, assunções, questões em aberto, fontes.
   Cada fase diz objetivo, entregável verificável, dependências e critério de aceite.

4. No `fullstack`, as fases dizem em que ordem entram banco, backend, frontend (web, mobile ou
   ambos, conforme o `frontend_target`), componentes e infraestrutura. Fase que não está no PRD
   não entra: o perfil existe para faseamento, não para ampliação de escopo.

5. Toda fase e toda feature rastreiam de volta a um requisito do PRD. Se faltar no PRD algo que
   o faseamento exige, pare e aponte a lacuna antes de preencher com suposição.

6. Salve em outputs/PLAN-{projeto}.md, com frontmatter:
   ---
   projeto: {nome}
   version: N
   baseado_em: docs/canonical/PRD-{projeto}.md (vN)
   status: rascunho
   atualizado: YYYY-MM-DD
   ---
   Se já existir plano anterior, arquive em docs/history/PLAN-v{N}-{YYYY-MM-DD}.md antes de
   sobrescrever.

7. Grave o grafo de tasks em `outputs/GRAPH-{projeto}.json`, derivado das features do plano. É o
   que o modo `autonomo` executa em ondas:

   ```json
   {
     "projeto": "{nome}",
     "baseado_em": "outputs/PLAN-{projeto}.md (vN)",
     "tasks": [
       {"id": "T-001", "titulo": "contrato do banco", "tipo": "desenho", "papel": "architect",
        "lente": "banco", "depende_de": [],
        "consome": ["docs/canonical/PRD-{projeto}.md", "docs/library/architecture/ARCH-{projeto}.md"],
        "produz": ["specs/contracts/banco.md"], "arquivos": ["specs/contracts/banco.md"]}
     ]
   }
   ```

   - `tipo`: `desenho`, `construcao`, `front` ou `integracao`. `papel`: um dos agentes de `agents/`.
   - `lente`: no desenho, a referência que o `architect` carrega (banco, api, infra, telemetria,
     ameaças, ou outra lente de `skills/bks-arch/references/lentes-system-design.md`); `null` fora dele.
   - toda task de `desenho` consome o ARCH (`docs/library/architecture/ARCH-{projeto}.md`), que o
     `/bkhar:arch` escreve depois do plano aprovado; o `wave_graph.py validate` recusa o grafo sem ele.
   - `consome` e `produz` são caminhos no repositório; a construção consome os contratos
     (`specs/contracts/*.md`) que o desenho produz. `arquivos` é o que a task escreve: duas tasks da
     mesma onda não podem declarar o mesmo arquivo.

   Rode e cole a saída; problema volta para o grafo antes de seguir:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/wave_graph.py validate .
   python ${CLAUDE_PLUGIN_ROOT}/scripts/wave_graph.py waves .
   ```

8. Reporte as fases, uma linha cada, e o próximo passo: "revise o plano; com ele aprovado, rode
   /bkhar:arch, aprove a arquitetura e só então /bkhar:refine (ou /bkhar:spec) para as features da
   primeira fase".

Não escreva FEAT, TEST nem TASK aqui. O plano diz a ordem; a especificação acontece por fase,
nos comandos de spec.
