---
description: Traz um projeto do kit bks para o bkhar. Confere o layout, cria o que falta pelos templates, troca /bks: por /bkhar: no WORKFLOW.md e no CLAUDE.md e grava o .bkhar.json. Não commita.
---

Migre o projeto atual do plugin `bks` para o `bkhar`. Rode com a sessão aberta **na raiz do repo
do projeto** — `${BKS_VAULT}/repos/{categoria}/{projeto}/`. Na raiz do vault, recuse e peça para
abrir a sessão na pasta do projeto.

O layout do projeto não muda: o que muda é quem o lê. Projeto que não passar por aqui continua
funcionando com `/bks:*`; os dois plugins convivem até o fim da migração.

## Passo 1 — conferir antes de mexer

1. **Já migrado?** Se existir `.bkhar.json` na raiz, diga que o projeto já foi migrado, mostre o
   conteúdo e pare.
2. **Árvore limpa?** Rode `git status --porcelain`. Com qualquer mudança pendente, pare e peça para
   fechar a sessão com `/bks:save` e commitar antes. Migração em cima de trabalho inacabado mistura
   as duas coisas no mesmo diff.
3. **Layout:** confira cada item e monte a tabela `item · existe · ação`:

| Item | Se faltar |
|---|---|
| `STATUS.md` | cria pelo template |
| `WORKFLOW.md` | cria pelo template, com as fases do perfil |
| `JOURNAL.md` | cria pelo template, com a entrada da migração |
| `.bks-profile.json` | pergunta o perfil (Passo 2) |
| `brain/` | cria a pasta pelo template |
| `specs/features/`, `specs/tests/`, `specs/tasks/` | cria as pastas vazias |

Mostre a tabela e espere o ok antes de criar qualquer coisa.

## Passo 2 — o que falta

Os templates vêm de `${CLAUDE_PLUGIN_ROOT}/templates/project-skeleton/`. Arquivo que já existe
nunca é sobrescrito, nem para "atualizar o modelo".

**Sem `.bks-profile.json`:** apresente os perfis de `${CLAUDE_PLUGIN_ROOT}/profiles/` com uma linha
cada, como o `/bkhar:new-project` faz, e grave a escolha conforme
`${CLAUDE_PLUGIN_ROOT}/profiles/bks-profile.schema.json`. Leia o `STATUS.md` e o `README.md` do
projeto antes de sugerir: o perfil tem que casar com o que o projeto já gera.

## Passo 3 — trocar o prefixo

Troque `/bks:` por `/bkhar:` **só** no `WORKFLOW.md` e no `CLAUDE.md` do projeto. Liste cada
ocorrência (arquivo, linha, trecho) antes de trocar.

Não troque:

- nome de skill (`bks-sdd`, `bks-standards`, `bks-dotnet-solutions`...);
- variáveis `BKS_VAULT`, `BKS_KNOWLEDGE`, `BKS_BRAIN`, `BKS_REPOS`;
- o `JOURNAL.md`, as ADRs em `decisions/` e as specs em `specs/`: são registro do que foi feito
  com o `bks`, e reescrevê-los apaga a história.

## Passo 4 — marcar o projeto

Grave `.bkhar.json` na raiz, mínimo e sem caminho absoluto:

```json
{
  "plugin": "bkhar",
  "migrated_from": "bks",
  "migrated_at": "AAAA-MM-DD"
}
```

O perfil continua no `.bks-profile.json`; o caminho do vault continua na variável `BKS_VAULT`.

Acrescente no topo do `JOURNAL.md` uma entrada com a data de hoje: "Migrado para o bkhar", e em
uma linha o que foi criado no Passo 2.

## Passo 5 — mostrar, não commitar

Não commite. Mostre `git status --short` e `git diff --stat`, e sugira:

```
git add -A
git commit -m "chore: migra para o bks-harness"
```

Depois do commit, o próximo passo é abrir a sessão de novo e rodar `/bkhar:brain` para conferir que
o retomar funciona.

## Regras

**Um projeto por vez.** Se pedirem vários, migre o primeiro e pergunte se segue.

**Migração é entre fases, nunca no meio de uma.** Se o `STATUS.md` mostrar task em andamento,
avise em uma linha e pergunte se é para seguir.

**Reversível.** Até o commit, `git checkout -- . && git clean -fd` desfaz tudo; diga isso no
resumo final.

Responda em português do Brasil.
