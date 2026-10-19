# Padrão de organização de projeto

> A estrutura canônica de um projeto vive num lugar só: `docs/ESTRUTURA.md`, no vault.
> Este arquivo aponta para ela e registra apenas o que é do kit.

A árvore, o que entra em cada diretório e a regra dos três arquivos de estado
(`STATUS.md` / `JOURNAL.md` / `WORKFLOW.md`) estão em **`docs/ESTRUTURA.md`**, seção "Projeto".
O esqueleto executável está em `templates/project-skeleton/`.

Idioma dos nomes de arquivo e pasta: inglês. Conteúdo e conversa: PT-BR. Código: inglês.

## O que o `/bkhar:new-project` faz

1. Copia `templates/project-skeleton/` para `repos/{categoria}/{projeto}/`.
2. Preenche o wiring: `CLAUDE.md`, `README.md`, `STATUS.md`, `WORKFLOW.md`, `JOURNAL.md`,
   `.bks-profile.json` (perfil, renderer, eixos) e `.gitignore`.
3. Não traz material bruto nem inicializa git — passos manuais do usuário.

Depois, manualmente: trazer material para `docs/input/`, rodar `/bkhar:canonize`, revisar
`docs/canonical/CONTEXT.md`, rodar `/bkhar:prd`, e só então `/bkhar:spec`.

## O ciclo de vida do conteúdo

```
docs/input/ + docs/design/  --/canonize-->  docs/canonical/CONTEXT.md  --/prd-->
docs/canonical/PRD-{projeto}.md  --/spec-->  specs/  --/loop-->  app/
```

`/bkhar:spec` só pode citar `docs/canonical/` — nunca `docs/input/` ou `docs/design/` direto. Se faltar
algo no canônico para especificar uma feature, rode `/bkhar:canonize` de novo em vez de "emprestar" do
material bruto.

## Comandos e onde rodam

| Comando | Onde | Faz |
|---|---|---|
| `/bkhar:brain` | raiz do vault | panorama de todos os projetos |
| `/bkhar:brain` | raiz do repo | retoma este projeto, a partir do `STATUS.md` |
| `/bkhar:new-project` | raiz do vault | cria a estrutura canônica |
| `/bkhar:note` | raiz do repo | nota viva em `docs/input/notas/` |
| `/bkhar:canonize` | raiz do repo | `docs/input/`+`docs/design/` → `docs/canonical/CONTEXT.md` |
| `/bkhar:prd` | raiz do repo | `CONTEXT.md` → `docs/canonical/PRD-*.md` |
| `/bkhar:spec` | raiz do repo | PRD/CONTEXT → `specs/features/` → `specs/tests/` → `specs/tasks/` |
| `/bkhar:arch` | raiz do repo | specs → `outputs/ARCH-*.md` |
| `/bkhar:loop` | raiz do repo | implementa via LOOP-4 |
| `/bkhar:review` | raiz do repo | revisão independente, read-only |
| `/bkhar:save` | raiz do repo | ADR, `STATUS.md`, `JOURNAL.md` |

Fora o `/bkhar:new-project`, todo comando de projeto roda com a sessão aberta na raiz do repositório do
projeto. Rodar do vault gravaria no lugar errado.
