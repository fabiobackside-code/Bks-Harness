---
description: Cria um projeto novo com a estrutura canônica e o perfil escolhido. Único ponto de entrada para começar um projeto. Roda na raiz do vault.
---

Crie um projeto novo. Rode com a sessão aberta na **raiz do vault** — o diretório que contém
`repos/`.

Se `BKS_VAULT` estiver definido e o diretório atual for outro, diga qual você vai usar antes de
criar qualquer coisa.

## Passo 1 — o que perguntar

Colete, numa única rodada de perguntas:

1. **Nome** do projeto — vira o diretório, em kebab-case
2. **Categoria** — as que existem em `repos/`; se o usuário disser uma que não existe, confirme
   antes de criar a pasta
3. **Perfil** — o que o projeto gera

Apresente os perfis com uma linha cada, para o usuário poder escolher:

| Perfil | Gera |
|---|---|
| `docs` | escopo, arquitetura, apresentação — sem código |
| `fullstack` | projeto completo faseado: docs, design, front, back, banco, infra |
| `frontend` | design, mocks, componentes, integração |
| `backend` | API, domínio, persistência, scripts |
| `component` | biblioteca, SDK, pacote |
| `infra` | IaC, pipeline, observabilidade |
| `data` | ETL, modelagem, BI |
| `legacy-docs` | documentar um legado, sem alterá-lo |
| `reengineering` | documentar e reescrever um legado |

A lista canônica está em `${CLAUDE_PLUGIN_ROOT}/profiles/`. Leia o diretório — não confie nesta
tabela se ela divergir dos arquivos.

## Passo 2 — os eixos

Leia `${CLAUDE_PLUGIN_ROOT}/profiles/{perfil}.md`. Ele diz quais eixos se aplicam e o que mais
perguntar.

Pergunte apenas os eixos que o perfil usa:

| Eixo | Valores | Padrão |
|---|---|---|
| `output` | `md`, `html` | `md` |
| `architecture_renderer` | ver `profiles/architecture-renderers/` | `mermaid` |
| `frontend_target` | `web`, `mobile`, `both` | `web` — só em `frontend` e `fullstack` |
| `rigor` | `producao`, `poc` | `producao` |

Mais as perguntas específicas que o arquivo do perfil lista em "O que perguntar na criação".

**Não pergunte o que o perfil não usa.** Um projeto `docs` não ouve pergunta sobre banco de dados,
e um `component` não ouve pergunta sobre alvo de frontend.

## Passo 3 — confirmar

Mostre o que vai ser criado — caminho, perfil, eixos — e espere. Não crie nada antes do aceite.

## Passo 4 — criar

Copie `${CLAUDE_PLUGIN_ROOT}/templates/project-skeleton/` para
`{vault}/repos/{categoria}/{nome}/` e preencha:

**`.bks-profile.json`** — conforme
`${CLAUDE_PLUGIN_ROOT}/profiles/bks-profile.schema.json`:

```json
{
  "profile": "backend",
  "category": "backside",
  "axes": {
    "output": "md",
    "architecture_renderer": "mermaid",
    "frontend_target": null,
    "rigor": "producao"
  }
}
```

Acrescente `stack` e `architecture_template` quando a conversa os tiver definido.

**`STATUS.md`** — o estado inicial. Fase: levantamento. Próximo passo: a primeira ação concreta do
perfil escolhido, que costuma ser `/bkhar:note` ou reunir o material de entrada. Não escreva "definir o
projeto" — isso não é ação.

**`WORKFLOW.md`** — a partir das fases do perfil. Remova as seções de fases que o perfil não usa.

**`JOURNAL.md`** — uma entrada: a data de hoje, "Projeto criado", perfil e escopo inicial em duas
linhas.

**`README.md`** — do template `PROJECT-README.md`, resolvido nesta ordem:
`${BKS_VAULT}/workbench/templates/`, senão `${CLAUDE_PLUGIN_ROOT}/templates/`.

**`CLAUDE.md`** — do template `REPO-CLAUDE.md`, mesma precedência. Declare as skills que o perfil
carrega e aponte `brain/domain/` e `brain/engineering/`.

**`git init`** — todo projeto nasce versionado. Primeiro commit com a estrutura.

## Passo 5 — informar

Em até cinco linhas: onde foi criado, qual perfil, e o primeiro comando a rodar.

Diga que o trabalho acontece com a sessão aberta **na pasta do projeto**, não aqui. Os comandos de
projeto escrevem onde a sessão está; rodar da raiz gravaria no lugar errado.

Não ofereça continuar o trabalho do projeto a partir do vault.

## Regras

**Um projeto por vez.** Se o usuário pedir vários, crie o primeiro e pergunte se segue.

**Nome que já existe não é sobrescrito.** Avise e pergunte se é para usar outro nome ou abrir o
que existe.

**Perfil errado custa caro depois.** Se a descrição do usuário não casar com o perfil que ele
escolheu, diga em uma linha antes de criar. A escolha é dele; o alerta é seu.

Responda em português do Brasil.
