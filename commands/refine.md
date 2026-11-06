---
description: Refinamento — /bkhar:refine <pedido>. Arquiteto, Testes e Segurança fazem até três perguntas cada; com as respostas do usuário, o architect escreve a FEAT e, aprovada, o tester escreve o TEST.
---

Refinamento de um pedido antes da FEAT, pelo protocolo do Gerente (skill `bks-team`). É o caminho
padrão; o `/bkhar:spec` fica como exceção, sem rito.

Uso: `/bkhar:refine <pedido>`. Rode com o Claude Code aberto na raiz do repositório do projeto.

## Portão de arquitetura

Antes de tudo, confira `docs/library/architecture/ARCH-{projeto}.md` e os modelos em
`docs/library/architecture/models/`. Sem o ARCH, ou com ele ou um modelo fora de `status: aprovado`,
pare e diga para rodar `/bkhar:arch`; vale nos dois modos. O `architect` lê o ARCH e os modelos antes
de perguntar ou de escrever a FEAT, e a FEAT cita o modelo em que se apoia. Decisão da FEAT que
contradiz um modelo aprovado não entra: vira ADR e `/bkhar:arch --update`.

Passos:

1. **Perguntar.** Chame `architect`, `tester` e `security`, cada um em invocação separada e em
   paralelo, com o pedido e o contexto do projeto. Cada um faz até três perguntas pelo seu ângulo,
   sem ver as perguntas dos outros.
2. **Agrupar.** Junte as perguntas por tema, numere e diga quem fez cada uma. Pergunta repetida
   entre agentes aparece uma vez, com os dois nomes.
3. **Ouvir.** Apresente ao usuário e espere as respostas. Pergunta sem resposta fica como decisão
   pendente; se ela bloqueia a FEAT, pare aqui.
4. **FEAT.** Chame o `architect` com o pedido, as perguntas e as respostas. Ele escreve
   `specs/features/FEAT-[nome].md` pelo template `FEAT.md` (precedência: `{repo}/.bks/templates/`,
   senao `${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`), com as
   respostas dentro e o cabeçalho `Refinamento: sim`.
5. **Aprovar.** Mostre a FEAT e pergunte se está aprovada. Ajuste volta ao `architect`.
6. **TEST.** Aprovada a FEAT, chame o `tester` para escrever `specs/tests/TEST-[nome].md`.
7. **Fechar.** Liste o que o `/bkhar:save` grava: decisões pendentes e aprendizados dos agentes.

NUNCA implemente nesta etapa. O rito não grava `STATUS.md` nem `JOURNAL.md`.

## Modo `autonomo`

Com `axes.mode: autonomo` no `.bks-profile.json`, os passos 3 e 5 mudam (skill `bks-team`, seção
"Modo `autonomo`"):

3. **Presumir.** Chame o `architect` com as perguntas agrupadas. Ele responde a cada uma pelas
   fontes do projeto e grava uma linha por resposta em `decisions/SUPOSICOES.md`. Pergunta sobre
   dado pessoal, autorização ou segredo não se presume: pare em `outputs/BLOQUEIO-[nome].md`.
5. **Sem portão.** A FEAT sai com `Refinamento: autonomo` e a lista das suposições que usou, e
   segue direto para o TEST.

O pedido vem da task do grafo (`outputs/GRAPH-{projeto}.json`); o contexto do agente é só o que a
task declara em `consome`.

FEAT e TEST em português do Brasil correto, com acentuação; nome de arquivo e slug em ASCII.
