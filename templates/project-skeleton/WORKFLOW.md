# WORKFLOW — {{PROJETO}}

> O fluxo de comandos deste projeto. Para saber **onde o projeto está**, leia `STATUS.md`.
>
> Todos os comandos rodam com a sessão aberta na **raiz deste repositório**. Não há comando que
> precise do vault: o projeto é autossuficiente.

---

## Perfil

**{{perfil}}** — {{docs · fullstack · frontend · backend · component · infra · data ·
legacy-docs · reengineering}}

O perfil está em `.bks-profile.json` e determina quais fases se aplicam. As fases que o perfil
não usa não aparecem abaixo.

---

## Ciclo

### 1 · Entrada de material

`/bkhar:note <assunto>` — material bruto vai para `docs/input/notas/`. Nota viva: cresce ao longo dos
dias, com seção `## Estado em AAAA-MM-DD`. Nunca decisão fechada.

Material de terceiros (artigo, entrevista, norma) vai para `docs/input/research/` à mão.

### 2 · Consolidação

`/bkhar:canonize` — lê `docs/input/` e `docs/design/` e escreve `docs/canonical/CONTEXT.md`. É a fonte
única a partir daqui; o material bruto deixa de ser lido pelos comandos seguintes.

Rode quando as notas pararem de mudar, não antes.

O comando é re-executável e versionado: a cada rodada a versão anterior vai para `docs/history/`
e o `CONTEXT.md` novo abre com o que mudou. Depois da fase 5, ele passa a ler também `specs/` e
`decisions/` — spec aprovada e ADR fechado são a parte mais atual do que o projeto decidiu, e o
canônico que os ignora alimenta o `/bkhar:prd` seguinte com informação vencida.

### 3 · Produto

`/bkhar:prd` — do `CONTEXT.md` sai o PRD. O que o produto é, para quem, e o que conta como pronto.

### 4 · Plano e arquitetura

`/bkhar:plan` — do PRD aprovado sai o plano macro `outputs/PLAN-{{projeto}}.md` e o grafo de tasks.

`/bkhar:arch` — com o plano aprovado, elabora a arquitetura: o índice
`docs/library/architecture/ARCH-{{projeto}}.md` e um modelo por arquivo em
`docs/library/architecture/models/` (C4, dados, sequências, fronteiras sensíveis, implantação),
desenhados pela notação BKS no renderer do `.bks-profile.json`. Atualiza o `README.md`.

É portão: nenhuma FEAT começa sem o ARCH e os modelos em `status: aprovado`, nos dois modos. Os
modelos são vivos: ADR, contrato ou plano mais novo que um modelo o deixa defasado, e o
`/bkhar:arch --update` refaz só o que ficou para trás.

### 5 · Especificação

`/bkhar:refine` (ou `/bkhar:spec`, sem rito) — gera `specs/features/FEAT-*.md` apoiada nos modelos
aprovados. Depois de aprovado, `specs/tests/TEST-*.md`. Depois de aprovado, `specs/tasks/TASK-*.md`.

Não pule a aprovação entre os três. Spec aprovada sem teste vira código sem critério.

### 6 · Implementação

`/bkhar:loop` — implementa uma task sob LOOP-4: no máximo quatro tentativas contra goals verificáveis
(build limpo, testes verdes, cenários da `TEST` cobertos).

### 7 · Revisão

`/bkhar:review` — revisão independente, read-only, em invocação separada. Quem escreveu não revisa a
própria segurança.

### 8 · Fechamento

`/bkhar:save` — roteia o resultado da sessão:

| O que | Para onde |
|---|---|
| Decisão de arquitetura ou stack | `decisions/ADR-NNN.md` |
| Spec nova ou alterada | `specs/` |
| Onde o projeto parou | `STATUS.md` |
| Marco da sessão | `JOURNAL.md` |
| Entregável | `outputs/` |
| Catálogo e dashboard da biblioteca | `docs/library/LIBRARY.md`, `docs/library/site/index.html` |

O `/bkhar:save` regera o catálogo e o dashboard e avisa quando um modelo da arquitetura está
defasado. `/bkhar:library export` leva a biblioteca para `knowledge/` do vault, quando o perfil tem
`library.export`.

Antes de fechar o `STATUS.md`, o `/bkhar:save` compara a data do `CONTEXT.md` com a de `specs/` e
`decisions/`. Se o canônico ficou para trás, a pendência entra na seção do que trava — quem
destrava é o `/bkhar:canonize`, na fase 2, numa sessão que possa responder às perguntas que ele levanta.
É aqui que o ciclo deixa de ser linear.

---

## Onde o conhecimento vive

| Pasta | O que entra |
|---|---|
| `brain/domain/` | o que o produto **é** — regra de negócio, método, normativo |
| `brain/engineering/` | como se constrói **aqui** — padrão técnico, skill local |

Skill em `brain/engineering/` sobrescreve a equivalente do kit para este projeto.

---

## Retomando

Abra a sessão na raiz deste repositório e rode `/bkhar:brain`. Ele lê o `STATUS.md` e diz onde você
parou, o que trava e qual o próximo passo.
