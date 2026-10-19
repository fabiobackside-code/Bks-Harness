---
description: Fluxo bks-sdd de especificação: entrevista sobre o bounded context e gera FEAT-[nome].md e, após aprovação, TEST-[nome].md.
---

Fluxo bks-sdd: entreviste-me sobre o bounded context, objetivos,
entidades, operações, integrações (TCP? filas? SEDA?) e critérios
de aceite VERIFICÁVEIS. Rode este comando com o Claude Code aberto
na RAIZ DO REPO do projeto (não na raiz do vault). Gere FEAT-[nome].md em
specs/features/ usando o template `FEAT.md`, resolvido nesta ordem:
`{repo}/.bks/templates/`, senao `${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`.
Depois de aprovado, gere TEST-[nome].md em specs/tests/. NUNCA
implemente nesta etapa.


## Idioma dos artefatos

FEAT, TEST e TASK são escritos em **português do Brasil correto, com acentuação e cedilha**.
Escreva "transação", "negócio", "critérios", "após", "não" — nunca a forma sem acento.
Vale para todo o corpo do documento: objetivo, regras, critérios de aceite, tabelas.

Se os arquivos já existentes do repositório estiverem sem acento, **não imite o defeito**: escreva
correto e avise o usuário em uma linha que o material anterior diverge.

Nome de arquivo, slug e chave de frontmatter seguem ASCII (`FEAT-transacao-execute.md`). O conteúdo,
não.
