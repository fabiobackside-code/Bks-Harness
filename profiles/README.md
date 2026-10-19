# Perfis de projeto

Um projeto declara **o que gera**. O perfil determina quais fases se aplicam, quais artefatos
saem, e quais skills o agente carrega.

Isso existe para que um projeto de documentação não receba pergunta sobre banco de dados, e um
projeto de biblioteca não passe por design de tela.

## Como se declara

O `/bkhar:new-project` grava `.bks-profile.json` na raiz do projeto:

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

As skills leem esse arquivo. Sem ele, perguntam.

## Os perfis

| Perfil | Para | Não gera |
|---|---|---|
| [`docs`](docs.md) | entrega documental | código |
| [`fullstack`](fullstack.md) | projeto completo faseado | — |
| [`frontend`](frontend.md) | camada visual | backend, banco |
| [`backend`](backend.md) | servidor e dados | interface |
| [`component`](component.md) | biblioteca reusável | aplicação |
| [`infra`](infra.md) | plataforma e entrega | aplicação |
| [`data`](data.md) | dados e analytics | interface |
| [`legacy-docs`](legacy-docs.md) | entender um legado | código — não altera nada |
| [`reengineering`](reengineering.md) | reescrever um legado | — |

`reengineering` consome `legacy-docs` como primeira fase. Quem só quer entender o legado para no
primeiro; quem vai reescrever passa pelos dois.

## Os eixos

Valem para vários perfis e são escolhidos junto com ele.

### `output` — formato de saída

| Valor | Gera |
|---|---|
| `md` | markdown apenas |
| `html` | HTML navegavel, exportavel para PDF |

### `architecture_renderer` — como o diagrama e desenhado

Registro extensivel em [`architecture-renderers/`](architecture-renderers/). Cada renderer e um
arquivo; adicionar um novo e criar um arquivo, substituir e trocar o conteúdo.

| Valor | E |
|---|---|
| `mermaid` | nativo, versionavel em texto — **padrão** |
| `archify` | skill externa, HTML interativo com export |
| `togaf` | template documental TOGAF |
| `c4` | C4 model — Context, Container, Component |

Todos aplicam a notação BKS: paleta, semantica de cor e convenção de linha definidas em
`skills/bks-arch/`.

### `frontend_target` — o que a interface e

Vale para `frontend` e `fullstack`.

| Valor | Gera |
|---|---|
| `web` | aplicação web |
| `mobile` | aplicativo movel |
| `both` | os dois, com design compartilhado |

### `rigor` — quanto de disciplina

| Valor | Exige |
|---|---|
| `producao` | testes, documentação, ADRs — **padrão** |
| `poc` | protótipo descartável: teste só no caminho crítico, documentação mínima |

`rigor: poc` afrouxa a exigência; não a elimina. Um POC sem nenhum teste é um POC que ninguém
consegue avaliar.

## Fases

Cada perfil declara sua sequência. As comuns:

| Fase | O que faz | Comando |
|---|---|---|
| entrada | material bruto entra | `/bkhar:note` |
| consolidação | vira contexto canônico | `/bkhar:canonize` |
| produto | vira PRD | `/bkhar:prd` |
| especificação | vira FEAT e TEST; as TASKs vêm do agente `planner` ou da skill `bks-sdd` | `/bkhar:spec` |
| arquitetura | vira ARCH e README | `/bkhar:arch` |
| implementação | vira código | `/bkhar:loop` |
| revisão | revisão independente | `/bkhar:review` |
| fechamento | STATUS e JOURNAL | `/bkhar:save` |

Um perfil pode pular fases, acrescentar as suas, ou mudar o que uma fase produz. O que cada um faz
está no seu arquivo.

## Acrescentar um perfil

Crie o arquivo seguindo o formato dos existentes: o que gera, o que não gera, as fases, os eixos
que se aplicam, as skills que carrega, e o que o `/bkhar:new-project` deve perguntar.

Nenhuma skill tem a lista de perfis embutida — todas leem este diretório.
