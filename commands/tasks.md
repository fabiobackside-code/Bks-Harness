---
description: Decompõe uma feature aprovada em tasks — /bkhar:tasks <feature>. O architect lê FEAT, TEST e ARCH e escreve specs/tasks/TASK-[feature].md, uma task por peça, no formato que o /bkhar:loop executa.
---

Ponte entre a especificação e a implementação: do FEAT e do TEST aprovados sai a lista de tasks que
o `/bkhar:loop` executa uma a uma. Rode na raiz do repositório do projeto, uma feature por vez.

## Portão

Antes de tudo, confira, nesta ordem, e pare no primeiro que faltar, dizendo o comando que destrava:

1. `docs/library/architecture/ARCH-{projeto}.md` e os modelos em `docs/library/architecture/models/`
   com `status: aprovado` → senão, `/bkhar:arch`.
2. `specs/features/FEAT-[feature].md` com `**Status:** Aprovada` → senão, `/bkhar:refine` ou
   `/bkhar:spec`.
3. `specs/tests/TEST-[feature].md` com `**Status:** Aprovada` → senão, o TEST volta ao `tester`.
4. `specs/tasks/TASK-[feature].md` ainda inexistente → se existir, mostre as tasks e pergunte se
   refaz; task com `Status` diferente de `Pendente` nunca é reescrita.

Vale nos dois modos.

## Passos

1. **Numerar.** O primeiro ID é o maior `T-NNN` encontrado em `specs/tasks/*.md` e em
   `outputs/GRAPH-{projeto}.json`, mais um. O ID vira a branch `task/T-NNN` do `/bkhar:loop`.
2. **Decompor.** Chame o `architect` com o FEAT, o TEST, o ARCH e os modelos que a FEAT cita. Ele
   escreve `specs/tasks/TASK-[feature].md` pelo template `TASK.md` (precedência:
   `{repo}/.bks/templates/`, senao `${BKS_VAULT}/workbench/templates/`, senao
   `${CLAUDE_PLUGIN_ROOT}/templates/`), com estas regras:
   - **uma task por peça**, sem par Teste e Implementação: o RED é do `tester`, no passo 0 do
     `/bkhar:loop`, e a task carrega os cenários que ele vai escrever;
   - **padrão TXC** (campo `txc` do `.bks-profile.json`): uma task por peça da ficha de cada
     transação, na ordem `[10]`, `ValidateAsync`, `ApplyRule`, `ExecuteAsync` (com `CancelAsync` se
     houver compensação), `[50]`, registro do código e adapter de entrada; executor de consulta tem
     só `ExecuteAsync` e registro. Em Go, os passos do `txc.Steps` e o construtor do `txc.Op`;
   - **padrão direto**: setup, regra, adapter e integração, uma ação por task;
   - todo cenário do TEST aparece em pelo menos uma task; cenário sem task volta ao `architect`;
   - duas tasks não declaram o mesmo arquivo sem dependência entre elas;
   - definição de pronto da skill `bks-sdd` (seção "Definição de pronto") em toda task.
3. **Conferir.** Liste as tasks, uma linha cada: ID, título, peça, dependência e cenários. Diga que
   cenário do TEST ficou sem task, se algum ficou.
4. **Aprovar.** Pergunte se a lista está aprovada. Ajuste volta ao `architect`.
5. **Fechar.** Aprovada, preencha a seção de tasks da FEAT com a mesma tabela, troque o
   `**Status:**` da FEAT para `Em execução` e diga a próxima ação: `/bkhar:loop T-NNN`, pela
   primeira task sem dependência.

NUNCA implemente nem escreva teste nesta etapa.

## Modo `autonomous`

Com `axes.mode: autonomous` no `.bks-profile.json`, o passo 4 não espera o usuário: a lista segue
aprovada, e o que o `architect` precisou presumir vai para `decisions/SUPOSICOES.md`. Cenário do
TEST sem task não se presume: para em `outputs/BLOQUEIO-[feature].md`.

## Idioma

O TASK é escrito em português do Brasil correto, com acentuação. Nome de arquivo e ID seguem ASCII.
