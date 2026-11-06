---
description: Elabora a arquitetura do projeto para aprovação — índice ARCH e um modelo por arquivo em docs/library/architecture/, desenhados pela bks-arch. Com --update, refaz só o que está defasado. Rode na raiz do repo do projeto.
---

**Passo 0 — delegar.** Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py delegate . --command arch`.
Com `terminal <nome>`, siga a seção "Delegação de comando" da skill `bks-team` e não execute
os passos abaixo neste terminal. Com `local: <motivo>`, siga normalmente.

Rode com o Claude Code aberto na **raiz do repositório do projeto**. Argumento: `$ARGUMENTS`
(vazio ou `--update`).

A arquitetura é portão nos dois modos: `prd → plan → arch (aprovado) → spec/refine`. Nenhuma FEAT
começa sem ela aprovada.

1. Confira as entradas. Faltando, pare e diga qual comando gera:
   - `docs/canonical/PRD-{projeto}.md` com `status: aprovado` (`/bkhar:prd`);
   - `outputs/PLAN-{projeto}.md` com `status: aprovado` (`/bkhar:plan`), quando o perfil pede plano.

   `outputs/ARCH-{projeto}.md` do layout anterior é entrada: leia, aproveite o que ainda vale e,
   escrito o índice novo, mova-o para `docs/history/ARCH-legado-{AAAA-MM-DD}.md`.

2. Carregue a skill `bks-arch`: a notação (`references/notacao-bks.md`, `references/paleta.md`), a
   escolha do diagrama (`references/topologias.md`) e o emissor do motor em
   `axes.architecture_renderer` do `.bks-profile.json` (`references/emit-mermaid.md`,
   `references/emit-archify.md`; o registro está em `${CLAUDE_PLUGIN_ROOT}/profiles/architecture-renderers/`).
   Motor externo não instalado: avise e use `mermaid`. Para o conteúdo de dado, API, mensageria,
   infraestrutura e telemetria, use as lentes de `references/lentes-system-design.md`.

3. Com `--update`, rode e cole a saída; refaça **só** os documentos apontados:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py stale .
   ```

4. Escolha os modelos que o projeto pede, um por pergunta. Padrão: `c4-contexto`, `c4-container`,
   `dados`, `sequencia-<fluxo>` para cada fluxo crítico do PRD, `fronteiras-sensiveis` quando há dado
   pessoal, de cartão ou segredo, e `implantacao`. `c4-componente` e `ciclo-de-vida-<entidade>` só
   quando a pergunta existe. Modelo que o PRD não justifica não entra.

5. Escreva cada modelo em `docs/library/architecture/models/<modelo>.md`:

   ```yaml
   ---
   projeto: {nome}
   modelo: <modelo>
   version: N
   status: rascunho
   baseado_em: outputs/PLAN-{projeto}.md (vN)
   fontes: [decisions/ADR-*.md, specs/contracts/*.md]
   atualizado: AAAA-MM-DD
   ---
   ```

   Corpo: a pergunta que o modelo responde, o diagrama, a legenda do que cada nó é e as decisões que
   ele assume, com o requisito do PRD de cada uma. Saída do motor que não é texto (HTML do archify,
   SVG, PNG) vai para `docs/library/architecture/render/` e o modelo aponta para ela.

6. Escreva o índice `docs/library/architecture/ARCH-{projeto}.md`, com o mesmo frontmatter (sem
   `modelo`): visão em um parágrafo, mapa de bounded contexts, a tabela dos modelos (modelo, pergunta,
   status, caminho), decisões de pipeline, riscos e questões em aberto. Versão anterior vai para
   `docs/history/ARCH-v{N}-{AAAA-MM-DD}.md` antes de sobrescrever. Decisão estrutural nova vira ADR em
   `decisions/`.

7. Atualize o `README.md` do repositório: o que é, arquitetura resumida com link para o ARCH, como
   rodar, como testar, estrutura de pastas.

8. Gere o catálogo e o dashboard e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py index .
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py build .
   ```

9. Reporte os modelos, uma linha cada, e peça a aprovação: o usuário muda `status` para `aprovado` no
   ARCH e em cada modelo. A aprovação é sempre do usuário, nos dois modos: no `autonomo`, a prontidão
   só concede o modo com o ARCH aprovado. Próximo passo: `/bkhar:refine` ou `/bkhar:spec` para as features da primeira fase.

Não escreva FEAT, TEST nem código aqui.
