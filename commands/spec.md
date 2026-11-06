---
description: Fluxo bks-sdd de especificação direto, sem rito: entrevista sobre o bounded context, o architect gera FEAT-[nome].md e, após aprovação, o tester gera TEST-[nome].md.
---

Fluxo bks-sdd direto, sem o rito de refinamento. O caminho com a equipe perguntando antes da FEAT é
o `/bkhar:refine`; este comando continua existindo como exceção.

## Portão de arquitetura

Antes de tudo, confira `docs/library/architecture/ARCH-{projeto}.md` e os modelos em
`docs/library/architecture/models/`. Sem o ARCH, ou com ele ou um modelo fora de `status: aprovado`,
pare e diga para rodar `/bkhar:arch`; vale nos dois modos. O `architect` lê o ARCH e os modelos antes
de perguntar ou de escrever a FEAT, e a FEAT cita o modelo em que se apoia. Decisão da FEAT que
contradiz um modelo aprovado não entra: vira ADR e `/bkhar:arch --update`.

Entreviste-me sobre o bounded context, objetivos, entidades, operações, integrações (TCP? filas?
SEDA?) e critérios de aceite VERIFICÁVEIS. Rode este comando com o Claude Code aberto na RAIZ DO
REPO do projeto (não na raiz do vault).

Com as respostas, chame o agente `architect` para gerar FEAT-[nome].md em specs/features/ usando o
template `FEAT.md`, resolvido nesta ordem: `{repo}/.bks/templates/`, senao
`${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`. O cabeçalho da FEAT
leva `Refinamento: não (exceção)`.

Depois de aprovada, chame o agente `tester` para gerar TEST-[nome].md em specs/tests/. NUNCA
implemente nesta etapa.

## Modo `autonomo`

Com `axes.mode: autonomo`, não há entrevista: o `architect` tira as respostas do PRD, do PLAN e
dos contratos que a task consome, e grava em `decisions/SUPOSICOES.md` o que precisou presumir. A
FEAT leva `Refinamento: autonomo` e segue para o TEST sem portão. Dado pessoal, autorização e
segredo não se presumem: param em `outputs/BLOQUEIO-[nome].md`.


## Idioma dos artefatos

FEAT, TEST e TASK são escritos em **português do Brasil correto, com acentuação e cedilha**.
Escreva "transação", "negócio", "critérios", "após", "não" — nunca a forma sem acento.
Vale para todo o corpo do documento: objetivo, regras, critérios de aceite, tabelas.

Se os arquivos já existentes do repositório estiverem sem acento, **não imite o defeito**: escreva
correto e avise o usuário em uma linha que o material anterior diverge.

Nome de arquivo, slug e chave de frontmatter seguem ASCII (`FEAT-transacao-execute.md`). O conteúdo,
não.
