---
tipo: manual
versao: 1.0.0
atualizado: 2026-10-18
---

# Manual de comandos do `bkhar`

Este manual descreve cada comando do plugin `bkhar`: para que serve, onde rodar, o que pergunta e o que grava. O `bkhar` é o antigo kit `bks`, renomeado, e conduz o ciclo de SDD (Spec-Driven Development) dentro do Claude Code.

Todo comando responde com o prefixo do plugin: `/bkhar:brain`, `/bkhar:save`. Os dois plugins, `bks` e `bkhar`, ficam instalados lado a lado até a Fase 7 da migração, e o mesmo comando existe nos dois prefixos, com o mesmo comportamento. Qual usar depende do projeto, como mostra a seção "Dois prefixos convivendo".

| Grupo | Comandos | Onde rodar |
|---|---|---|
| Entrada e vault | `brain`, `new-project`, `ingest` | raiz do vault (`brain` também roda na raiz do repo) |
| Contexto e requisito | `note`, `canonize`, `prd` | raiz do repo (`canonize` e `prd` aceitam a raiz do vault e perguntam o projeto) |
| Especificação e arquitetura | `spec`, `arch` | raiz do repo |
| Execução e qualidade | `loop`, `review`, `maintainability` | raiz do repo |
| Fechamento e migração | `save`, `migrate` | raiz do repo |

> Os comandos de projeto escrevem no repositório onde a sessão está aberta. Rodar da pasta errada grava no lugar errado. Na dúvida, abra uma sessão nova na pasta do projeto.

O vault é apontado pela variável `BKS_VAULT`. Neste manual, `${BKS_VAULT}` representa a raiz dele, e `${BKS_VAULT}/repos/{categoria}/{projeto}` é a raiz de um repo de projeto.

## Dois prefixos convivendo

O `bks` atende os projetos que ainda não migraram; o `bkhar` atende os migrados e os novos. Você toca os dois tipos de projeto ao mesmo tempo, cada um com o seu prefixo.

| Situação | Prefixo | Como reconhecer |
|---|---|---|
| Projeto ainda no kit antigo | `/bks:*` | não tem `.bkhar.json` na raiz; o `WORKFLOW.md` cita `/bks:` |
| Projeto migrado | `/bkhar:*` | passou pelo `/bkhar:migrate`: tem `.bkhar.json` e o `WORKFLOW.md` cita `/bkhar:` |
| Projeto novo, depois da Fase 2 | `/bkhar:*` | nasce pelo `/bkhar:new-project` |
| Raiz do vault (`brain`, `new-project`, `ingest`) | qualquer um | os dois leem o mesmo vault; prefira `/bkhar:*` depois da Fase 2 |

Os exemplos deste manual usam `/bkhar:*`. Num projeto não migrado, troque o prefixo por `/bks:` e o resto vale igual. Não misture os dois prefixos na mesma sessão de um projeto: o `STATUS.md` e o `JOURNAL.md` registram o comando usado.

Todos os exemplos usam o mesmo projeto fictício: `pix-comprovante`, categoria `backside`, perfil `backend`, uma API .NET que emite o comprovante de uma transferência Pix.

---

## 1. O ciclo em uma passada

A ordem típica, do projeto novo ao fechamento de sessão. O PRD (Product Requirements Document, documento de requisitos de produto) é a ponte entre o contexto e a especificação.

| Ordem | Comando | Onde | O que acontece |
|---|---|---|---|
| 1 | `/bkhar:brain` | vault ou repo | retoma: panorama dos projetos, ou o estado de um projeto |
| 2 | `/bkhar:new-project` | vault | cria o repo com a estrutura canônica e o perfil |
| 3 | `/bkhar:note` | repo | material bruto do autor entra em `docs/input/notas/` |
| 4 | `/bkhar:canonize` | repo | `docs/input/` e `docs/design/` viram `docs/canonical/CONTEXT.md` |
| 5 | `/bkhar:prd` | repo | o contexto canônico vira `PRD-{projeto}.md` |
| 6 | `/bkhar:spec` | repo | entrevista gera a `FEAT` e, após aprovação, o `TEST` |
| 7 | `/bkhar:arch` | repo | as specs viram a visão de arquitetura e o README |
| 8 | `/bkhar:loop` | repo | implementa uma task sob goals verificáveis, no máximo 4 tentativas |
| 9 | `/bkhar:review` | repo | revisão independente, read-only |
| 10 | `/bkhar:maintainability` | repo | parecer por aplicação de `app/` e a fundamentação do projeto |
| 11 | `/bkhar:save` | repo | roteia decisões e specs, reescreve o `STATUS.md`, acrescenta ao `JOURNAL.md` |

Projeto que veio do kit antigo passa uma vez pelo `/bkhar:migrate` antes de entrar no ciclo com `/bkhar:*`.

O `/bkhar:ingest` fica fora da sequência: alimenta a base de conhecimento do vault a qualquer momento.

Três artefatos aparecem em todo o manual. A FEAT (especificação da feature) diz o que construir. O TEST (cenários de teste) diz como verificar. A TASK (tarefa executável) é a unidade que o `/bkhar:loop` implementa.

---

## 2. Entrada e vault

### `/bkhar:brain`

**Para que serve.** Retoma o trabalho. Na raiz do vault, monta o panorama de todos os projetos. Dentro de um repo, diz onde aquele projeto parou.

**Onde rodar.** Raiz do vault (modo panorama) ou raiz do repo de um projeto (modo projeto).

**Quando usar.** Primeira coisa de toda sessão.

**Pré-requisito.** Nenhum. O comando decide o modo pelo que encontra na pasta.

**O que ele faz, passo a passo.**

1. Descobre o modo: `STATUS.md` na raiz indica modo projeto; `repos/` com categorias indica modo panorama. Sem nenhum dos dois, pergunta onde trabalhar e para.
2. Se `BKS_VAULT` aponta para outra pasta, diz qual das duas está usando.
3. Modo projeto: lê o `STATUS.md`, a entrada mais recente do `JOURNAL.md` e o `.bks-profile.json`, se houver.
4. Modo projeto: responde em até seis linhas com onde parou, o que trava e o próximo passo.
5. Modo panorama: lê `workbench/profile.md` e, de cada projeto em `repos/*/*/`, só o `STATUS.md` e a data do `JOURNAL.md`.
6. Modo panorama: agrupa em ativo (entrada com menos de 30 dias), pausado e sem status, e fecha com uma sugestão de qual projeto seguir.

**O que produz.** Só texto na conversa. Nenhum arquivo.

**Exemplo.**

```
cd ${BKS_VAULT}
/bkhar:brain
→ ${BKS_VAULT} · 1 projeto · 1 ativo

  ATIVO
    pix-comprovante   backside   FEAT de emissão aprovada; TEST em revisão   2026-10-17

→ Pronto para seguir: pix-comprovante (aprovar o TEST da emissão).
→ Para trabalhar nele, abra uma sessão nova em ${BKS_VAULT}/repos/backside/pix-comprovante.

cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:brain
→ Onde parou: "FEAT de emissão aprovada; TEST em revisão."
→ O que trava: nada.
→ Próximo passo: revisar specs/tests/TEST-emissao-comprovante.md e aprovar.
```

**Cuidados.**

- O panorama pula `repos/old/`, que é arquivo morto.
- O panorama não abre `specs/`, `decisions/` nem código. Para detalhe, entre no projeto.
- Se o `STATUS.md` estiver defasado em relação ao `JOURNAL.md` ou ao git, o comando avisa e oferece atualizar. Ele não atualiza sozinho.
- A partir da raiz do vault, o comando não continua o trabalho de um projeto. Abra a sessão na pasta dele.

### `/bkhar:new-project`

**Para que serve.** Cria um projeto novo com a estrutura canônica e o perfil escolhido. É o único ponto de entrada para começar um projeto.

**Onde rodar.** Raiz do vault, a pasta que contém `repos/`.

**Quando usar.** Ao iniciar um projeto do zero.

**Pré-requisito.** Saber o nome, a categoria e o que o projeto vai gerar.

**O que ele faz, passo a passo.**

1. Pergunta, numa única rodada, o nome (vira o diretório, em kebab-case), a categoria e o perfil.
2. Lê `profiles/{perfil}.md` e pergunta só os eixos e as questões que o perfil usa.
3. Mostra caminho, perfil e eixos, e espera o aceite. Nada é criado antes disso.
4. Copia o esqueleto para `${BKS_VAULT}/repos/{categoria}/{nome}/` e preenche os arquivos iniciais.
5. Roda `git init` e faz o primeiro commit com a estrutura.
6. Informa, em até cinco linhas, onde criou, qual perfil e o primeiro comando a rodar.

Os perfis disponíveis:

| Perfil | Gera |
|---|---|
| `docs` | escopo, arquitetura, apresentação, sem código |
| `fullstack` | projeto completo faseado: docs, design, front, back, banco, infra |
| `frontend` | design, mocks, componentes, integração |
| `backend` | API, domínio, persistência, scripts |
| `component` | biblioteca, SDK, pacote |
| `infra` | infraestrutura como código, pipeline, observabilidade |
| `data` | ETL (extração, transformação e carga), modelagem, BI (inteligência de negócio) |
| `legacy-docs` | documentar um legado, sem alterá-lo |
| `reengineering` | documentar e reescrever um legado |

Os eixos que o perfil pode perguntar:

| Eixo | Valores | Padrão |
|---|---|---|
| `output` | `md`, `html` | `md` |
| `architecture_renderer` | `mermaid`, `archify`, `togaf`, `c4` | `mermaid` |
| `frontend_target` | `web`, `mobile`, `both` | `web`, só em `frontend` e `fullstack` |
| `rigor` | `producao`, `poc` | `producao` |

**O que produz.** Em `${BKS_VAULT}/repos/{categoria}/{nome}/`:

- `.bks-profile.json` com perfil, categoria e eixos
- `STATUS.md` com fase de levantamento e a primeira ação concreta
- `WORKFLOW.md` só com as fases do perfil
- `JOURNAL.md` com a entrada "Projeto criado"
- `README.md` e `CLAUDE.md` a partir dos templates `PROJECT-README.md` e `REPO-CLAUDE.md`
- as pastas do esqueleto: `app/`, `brain/`, `decisions/`, `docs/`, `outputs/`, `specs/`
- o repositório git com o primeiro commit

Os templates são resolvidos primeiro em `${BKS_VAULT}/workbench/templates/` e, na falta, no plugin.

**Exemplo.**

```
cd ${BKS_VAULT}
/bkhar:new-project
→ Nome do projeto? — pix-comprovante
→ Categoria (backside, w3, private)? — backside
→ Perfil? — backend
→ Stack? — .NET
→ Banco? — PostgreSQL
→ Mensageria? — nenhuma
→ Autenticação? — provedor externo
→ Saída md ou html? — md
→ Renderer de arquitetura? — mermaid
→ Rigor? — producao

→ Vou criar:
    ${BKS_VAULT}/repos/backside/pix-comprovante/
    perfil backend · output md · renderer mermaid · rigor producao
  Confirma? — sim

→ Criado em repos/backside/pix-comprovante (backend).
→ Primeiro comando: /bkhar:note com o material de entrada.
→ Abra uma sessão nova na pasta do projeto para trabalhar nele.
```

**Cuidados.**

- Um projeto por vez. Pedindo vários, o comando cria o primeiro e pergunta se segue.
- Nome que já existe não é sobrescrito. O comando pergunta se é outro nome ou se é para abrir o existente.
- Categoria que não existe em `repos/` exige confirmação antes de criar a pasta.
- Perfil errado custa caro depois. Se a descrição não casar com o perfil, o comando avisa em uma linha; a escolha é sua.
- O projeto `docs` não recebe pergunta sobre banco, e o `component` não recebe pergunta sobre frontend.

### `/bkhar:ingest`

**Para que serve.** Leva conhecimento para a base transversal do vault, em `${BKS_VAULT}/knowledge/`. Aceita uma fonte, um lote ou uma pasta de entrada.

**Onde rodar.** De qualquer pasta. O comando opera sempre sobre `${BKS_VAULT}/knowledge/`, e os caminhos do argumento são relativos a ela.

**Quando usar.** Quando um artigo, livro, paper ou vídeo merece virar página permanente da wiki. Também para arquivar uma nota pessoal de prospecção.

**Pré-requisito.** A fonte salva em `raw/`, um link, a tabela de lote ou arquivos em `raw/_inbox/`.

**Argumentos.** O caminho ou a URL da fonte. Sem argumento, assume `raw/_inbox/`.

| Chamada | Efeito |
|---|---|
| `/bkhar:ingest raw/papers/nome.pdf` | ingere um PDF |
| `/bkhar:ingest raw/articles/nome.md` | ingere um artigo já salvo em Markdown |
| `/bkhar:ingest raw/articles/nome.html` | ingere uma página web salva localmente |
| `/bkhar:ingest raw/videos/nome-transcrição.md` | ingere a transcrição de um vídeo |
| `/bkhar:ingest raw/notas-pessoais/nome.md` | arquiva uma nota pessoal, sem curar |
| `/bkhar:ingest https://exemplo.com/artigo` | busca o link, salva cópia em `raw/` e ingere |
| `/bkhar:ingest tools/batch-ingest.md` | processa a tabela de lote |
| `/bkhar:ingest raw/_inbox/` | classifica e processa tudo da pasta |

**O que ele faz, passo a passo.**

1. Classifica a natureza da fonte: externa (de terceiro, vai ser curada) ou nota pessoal (preservada como está). Na dúvida, pergunta.
2. Fonte externa: lê, resume, extrai conceitos e cria ou atualiza a página certa em `wiki/`.
3. Link ainda não salvo: grava antes uma cópia em `raw/articles/<slug>.md`, com a URL no frontmatter.
4. Nota pessoal: copia para `wiki/prospecções/<slug>.md` com `type: "prospecção"` ou `"reflexao"`, sem reescrever a ideia.
5. Lote: processa uma fonte por vez, da prioridade `high` para a `low`, e imprime uma linha por fonte.
6. Pasta de entrada: move cada arquivo para a subpasta certa de `raw/` e ingere pela regra do tipo.
7. Atualiza `wiki/index.md` e `wiki/log.md` ao fim de cada fonte.

**O que produz.**

- páginas em `${BKS_VAULT}/knowledge/wiki/`, ou em `wiki/prospecções/` para nota pessoal
- cópia da fonte em `raw/` quando veio de link ou da `_inbox`
- registro em `wiki/index.md` e `wiki/log.md`

**Exemplo.**

```
/bkhar:ingest raw/papers/hexagonal-architecture.pdf
→ Cria wiki/architecture/hexagonal-architecture.md e registra em index.md e log.md.

/bkhar:ingest raw/_inbox/
→ Classifica 3 arquivos:
    padroes-de-idempotencia.pdf      → raw/papers/
    palestra-pix-transcrição.md      → raw/videos/
    ideia-comprovante-offline.md     → nota pessoal? — sim → raw/notas-pessoais/
→ ✓ [high]   raw/papers/padroes-de-idempotencia.pdf → wiki/patterns/idempotencia.md
→ ✓ [medium] raw/videos/palestra-pix-transcrição.md → wiki/concepts/pix.md (atualizada)
→ ✓ [low]    raw/notas-pessoais/ideia-comprovante-offline.md → wiki/prospecções/comprovante-offline.md
→ wiki/index.md e wiki/log.md atualizados.
```

**Cuidados.**

- `raw/` é imutável. A fonte original nunca é editada; a exceção é `raw/notas-pessoais/`, que cresce por seção de data.
- Sem conteúdo extraível (PDF protegido, vídeo sem transcrição, link pago), o comando para e diz isso. Ele não inventa a partir do nome do arquivo.
- O comando não transcreve áudio. Um `.mp4` exige antes a transcrição em `.txt`, `.md` ou `.srt`.
- Fonte já registrada em `wiki/log.md` não é reprocessada sem pedido explícito.
- Material de domínio de um projeto não passa por aqui. Ele vai para o `brain/` do próprio projeto.

---

## 3. Contexto e requisito

### `/bkhar:note`

**Para que serve.** Escreve ou atualiza uma nota viva em `docs/input/notas/` do projeto. É material bruto do autor para o `/bkhar:canonize`, nunca decisão fechada.

**Onde rodar.** Raiz do repo do projeto.

**Quando usar.** Sempre que tiver uma ideia, uma observação ou um apontamento de especialista sobre o projeto.

**Pré-requisito.** Nenhum. Na primeira vez, o comando cria a pasta.

**Argumentos.** `<assunto> [--pasta <subpasta>]`.

- `<assunto>` vira o nome do arquivo em `SCREAMING-KEBAB.md`, sem data: "regras de emissão" vira `REGRAS-DE-EMISSAO.md`.
- `--pasta <subpasta>` grava em `docs/input/notas/<subpasta>/`, para a fila de um colaborador externo.

**O que ele faz, passo a passo.**

1. Na primeira vez, pergunta a hierarquia de fontes do projeto e cria `docs/input/notas/LEIA-ME.md`. Sem resposta, a seção fica `[EM ABERTO]`.
2. Confere se `docs/canonical/` já tem decisão que colide com o assunto. Se colidir, declara o conflito na nota, com o argumento.
3. Nota nova: cria com o título e o conteúdo, marcando a procedência de cada trecho.
4. Nota existente: acrescenta uma seção `## Estado em YYYY-MM-DD` com o que mudou. O texto anterior fica.
5. Atualiza a tabela `## Índice` do `LEIA-ME.md`.
6. Reporta o arquivo e a seção alterados, o conflito sinalizado, se houve, e o próximo passo.

As marcas de procedência:

| Marca | Significa |
|---|---|
| `[AUTOR]` | decisão ou observação do autor, com autoridade sobre produto e arquitetura |
| `[PESQUISA]` | resultado de rodada de pesquisa técnica |
| `[INFERIDO]` | leitura do agente, precisa de validação |
| `[EM ABERTO]` | lacuna reconhecida |

**O que produz.**

- `docs/input/notas/LEIA-ME.md`, na primeira execução
- `docs/input/notas/[<subpasta>/]<ASSUNTO>.md`, criada ou com seção nova

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:note regras de emissão
  O comprovante só sai depois da liquidação. Precisa do identificador
  fim a fim da transação. Não sei se o PDF é gerado na hora ou sob demanda.

→ docs/input/notas/ não existe. Qual a hierarquia de fontes deste projeto?
  — normativo do regulador > especialista de pagamentos > cânone interno
→ Criei docs/input/notas/LEIA-ME.md.
→ Criei docs/input/notas/REGRAS-DE-EMISSAO.md:
    [AUTOR] o comprovante só sai depois da liquidação
    [AUTOR] exige o identificador fim a fim da transação
    > [!uncertain] PDF gerado na hora ou sob demanda?
→ Índice do LEIA-ME atualizado.
→ Próximo passo: com notas suficientes sobre o assunto, rode /bkhar:canonize.
```

**Cuidados.**

- Rascunho nunca é escrito como decisão fechada.
- Incerteza vai como `> [!uncertain]`, nunca como afirmação.
- Nota que contradiz `docs/canonical/` diz isso com o argumento. A mudança não entra em silêncio.
- `docs/input/notas/` é a única parte editável de `docs/input/`. O resto é imutável.

### `/bkhar:canonize`

**Para que serve.** Consolida o material de pesquisa e design de um projeto num contexto canônico único, `docs/canonical/CONTEXT.md`. É a fonte do `/bkhar:prd` e do `/bkhar:spec`.

**Onde rodar.** Raiz do repo do projeto. Também roda na raiz do vault: aí pergunta qual projeto.

**Quando usar.** Depois de juntar material suficiente, e de novo sempre que entrar material novo ou spec e decisão novas. Rodar várias vezes é o uso normal.

**Pré-requisito.** O projeto existe e tem algo em `docs/input/` ou `docs/design/`. Com as duas pastas vazias, o comando avisa e para.

**O que ele faz, passo a passo.**

1. Lê `docs/input/{scope,interviews,research,assets}/`, `docs/design/`, e também `specs/features/`, `specs/tests/` e `decisions/`, se existirem.
2. Monta o rascunho com, no mínimo: propósito, personas, escopo dentro e fora, decisões já fixadas, lacunas e glossário. Cada afirmação relevante cita a fonte.
3. Em "Decisões já fixadas", o que vem de `decisions/` e `specs/` vence o material de `docs/input/`.
4. Onde o material diverge ou é ambíguo, marca `> [!uncertain]` e lista as perguntas em `## Perguntas em aberto`.
5. Se o projeto referencia uma skill, confronta o `SKILL.md` com o que o projeto fez e registra as divergências como aprendizado ou exceção.
6. Se já existe um `CONTEXT.md`, arquiva o anterior em `docs/history/` e incrementa a versão.
7. Grava o critério da consolidação em `docs/prompts/` e reporta o que entrou, as perguntas em aberto e o próximo passo.

**O que produz.**

- `docs/canonical/CONTEXT.md`, com frontmatter `projeto`, `version`, `status`, `atualizado` e `fontes`
- `docs/history/CONTEXT-v{N}-{YYYY-MM-DD}.md`, quando havia versão anterior
- `docs/prompts/prompt-canonize-{YYYY-MM-DD}.md`

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:canonize
→ Lidos: docs/input/notas/REGRAS-DE-EMISSAO.md, docs/input/notas/ARQUITETURA-PRETENDIDA.md,
         docs/input/research/manual-do-regulador.pdf
→ Gerado docs/canonical/CONTEXT.md v1 (status: rascunho).
→ Perguntas em aberto: 2
    - PDF gerado na hora ou sob demanda?
    - Comprovante de transação devolvida é emitido?
→ Divergências com skills: nenhuma.
→ Próximo passo: revise o CONTEXT.md, responda as perguntas se quiser fechar tudo,
  e rode /bkhar:prd quando o contexto estiver bom para virar requisito.
```

**Cuidados.**

- O comando não lê `brain/` nem `app/`. Esse material não é escopo.
- Nada inventado para fechar lacuna vira canônico. Lacuna é marcada como incerta e vira pergunta.
- Contradição entre decisão fechada e intenção original não é incerteza: a decisão venceu, e a mudança fica registrada em `## O que mudou desde v{N}`.
- A skill não é editada daqui. O aprendizado é reportado para quem a mantém.
- Se `app/` tiver código, o reporte sugere o `/bkhar:maintainability`.

### `/bkhar:prd`

**Para que serve.** Gera o PRD do projeto a partir do contexto canônico já consolidado. É a ponte entre o `/bkhar:canonize` e o `/bkhar:spec`.

**Onde rodar.** Raiz do repo do projeto. Também roda na raiz do vault: aí pergunta qual projeto.

**Quando usar.** Quando o `CONTEXT.md` foi revisado e está pronto para virar requisito formal.

**Pré-requisito.** `docs/canonical/CONTEXT.md` existe, com status pelo menos `rascunho`. Sem ele, o comando para e manda rodar o `/bkhar:canonize`.

**O que ele faz, passo a passo.**

1. Lê o `CONTEXT.md` e o PRD anterior, se houver, para não regredir no que já foi decidido.
2. Usa a estrutura de PRD da skill `bks-sdd`, se disponível. Sem ela, gera as seções padrão.
3. Rastreia cada requisito até uma seção do `CONTEXT.md`. Lacuna real é apontada antes de qualquer suposição.
4. Arquiva o PRD anterior em `docs/history/` e grava o novo com frontmatter.
5. Reporta o PRD e o próximo passo.

As seções padrão: problema, objetivo e métrica de sucesso, personas, escopo e fora de escopo, requisitos funcionais numerados, requisitos não funcionais, fases sugeridas, riscos, perguntas em aberto herdadas.

**O que produz.**

- `docs/canonical/PRD-{projeto}.md`, com frontmatter `projeto`, `version`, `baseado_em`, `status` e `atualizado`
- `docs/history/PRD-v{N}-{YYYY-MM-DD}.md`, quando havia versão anterior

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:prd
→ Gerado docs/canonical/PRD-pix-comprovante.md v1
  (baseado_em: docs/canonical/CONTEXT.md v2, status: rascunho).
→ Requisitos funcionais: RF-01 emitir comprovante após liquidação,
  RF-02 consultar comprovante pelo identificador fim a fim, ...
→ Pergunta herdada que ainda bloqueia: comprovante de transação devolvida.
→ Próximo passo: revise o PRD, feche o que está em aberto e rode /bkhar:spec
  na raiz deste repo para a primeira feature.
```

**Cuidados.**

- PRD nunca sai direto de `docs/input/` ou `docs/design/`.
- A partir daqui, o `/bkhar:spec` cita só `docs/canonical/`. Se uma spec precisar de algo de `docs/input/`, o canônico ficou incompleto: rode o `/bkhar:canonize` de novo.

---

## 4. Especificação e arquitetura

### `/bkhar:spec`

**Para que serve.** Entrevista você sobre um bounded context e gera a FEAT. Depois da aprovação, gera o TEST.

**Onde rodar.** Raiz do repo do projeto. Não na raiz do vault.

**Quando usar.** Para especificar uma feature que você já entende, num projeto que já existe. Uma feature por vez.

**Pré-requisito.** O PRD ou o `CONTEXT.md` em `docs/canonical/`.

**O que ele faz, passo a passo.**

1. Entrevista sobre o bounded context: objetivos, entidades, operações, integrações e critérios de aceite verificáveis.
2. Pergunta sobre integrações específicas: TCP, filas, SEDA (Staged Event-Driven Architecture).
3. Gera a FEAT em `specs/features/` a partir do template `FEAT.md`.
4. Espera a sua aprovação.
5. Gera o TEST em `specs/tests/`.

O template é resolvido nesta ordem: `{repo}/.bks/templates/`, `${BKS_VAULT}/workbench/templates/` e, por fim, o plugin.

**O que produz.**

- `specs/features/FEAT-[nome].md`
- `specs/tests/TEST-[nome].md`, depois da aprovação da FEAT

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:spec
→ Qual o bounded context? — Emissão de comprovante
→ Quais entidades? — Comprovante, Transação liquidada
→ Quais operações? — emitir, consultar por identificador fim a fim
→ Integrações? Fila, TCP, SEDA? — consome o evento de liquidação de uma fila
→ Critério de aceite verificável para "emitir"? — comprovante só existe
  para transação com status liquidada; segunda emissão devolve o mesmo comprovante
→ Gerado specs/features/FEAT-emissao-comprovante.md (status: Rascunho).
  Aprova? — sim
→ Gerado specs/tests/TEST-emissao-comprovante.md.
```

**Cuidados.**

- O comando nunca implementa. Código é etapa do `/bkhar:loop`.
- FEAT, TEST e TASK são escritos em português com acentuação. Nome de arquivo fica sem acento: `FEAT-emissao-comprovante.md`.
- Se os arquivos do repo estiverem sem acento, o comando escreve certo mesmo assim e avisa em uma linha.

### `/bkhar:arch`

**Para que serve.** Gera a visão de arquitetura do projeto e o README do repositório a partir das specs.

**Onde rodar.** Raiz do repo do projeto.

**Quando usar.** Com specs aprovadas, antes ou durante a implementação.

**Pré-requisito.** Specs em `specs/` do próprio repo.

**O que ele faz, passo a passo.**

1. Lê as specs em `specs/`.
2. Gera a visão C4 (modelo de diagramas Context, Container e Component) em Mermaid.
3. Acrescenta o mapa de bounded contexts, as decisões de pipeline e SEDA, e o contrato do protocolo TCP, quando houver.
4. Gera o README do repositório: o que é, arquitetura resumida, como rodar, como testar, estrutura de pastas.
5. Usa a skill `bks-c4-diagrams`, se disponível.

**O que produz.**

- `outputs/ARCH-[projeto].md`
- `README.md` na raiz do repo

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:arch
→ Lidas: specs/features/FEAT-emissao-comprovante.md, specs/tests/TEST-emissao-comprovante.md
→ Gerado outputs/ARCH-pix-comprovante.md:
    Context    — cliente do banco → API pix-comprovante → fila de liquidação
    Container  — API .NET · worker de emissão · PostgreSQL
    Component  — Adapter Inbound → UseCase EmitirComprovante → Port de persistência
→ Atualizado README.md.
```

**Cuidados.**

- O comando não recebe o nome do projeto como argumento. Ele usa o repo onde a sessão está.
- A arquitetura sai das specs. Spec ausente ou em rascunho gera uma visão pobre.

---

## 5. Execução e qualidade

### `/bkhar:loop`

**Para que serve.** Implementa uma task sob o protocolo LOOP-4: goals verificáveis, no máximo 4 tentativas.

**Onde rodar.** Raiz do repo do projeto.

**Quando usar.** Na fase de código, uma task por vez.

**Pré-requisito.** FEAT e TEST aprovados.

Os goals padrão, ajustáveis por task:

| Goal | Exige |
|---|---|
| `G1` | `dotnet build` sem erros e sem warnings novos |
| `G2` | `dotnet test` 100% verde |
| `G3` | todos os cenários do `TEST-[feature].md` cobertos |
| `G4` | código fiel a `brain/engineering/` do projeto (calisthenics e hexagonal) |

**O que ele faz, passo a passo.**

1. Implementa ou corrige a task atual.
2. Roda `dotnet build` e `dotnet test`.
3. Audita `G3` e `G4` explicitamente.
4. Se todos os goals passaram: marca a task como concluída em `specs/tasks/TASK-[feature].md`, roda o `/bkhar:save`, reporta e para.
5. Se algum falhou: registra o erro e a hipótese de correção na seção "Tentativas" da task, em `specs/tasks/TASK-[feature].md`, e começa a próxima tentativa.
6. Depois da quarta tentativa sem sucesso: para e gera o registro de bloqueio.

**O que produz.**

- código e testes em `app/`, com o `/bkhar:save` no fim
- ou `outputs/BLOQUEIO-[task].md`, com o goal que falhou, o erro exato, o que foi tentado e a pergunta que você precisa responder

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:loop
→ Tentativa 1: implementa EmitirComprovanteUseCase; build ok; test ok;
  G3 falha: cenário "segunda emissão devolve o mesmo comprovante" sem teste.
→ Tentativa 2: acrescenta o teste e a verificação de idempotência; G1 a G4 passam.
→ Concluído. Rodando /bkhar:save.
```

Caso de bloqueio:

```
→ Tentativa 4: G2 falha no teste de integração com o PostgreSQL.
→ Parado. Gerado outputs/BLOQUEIO-emitir-comprovante.md
  Pergunta: o worker de emissão pode ler a transação antes do commit da liquidação?
```

**Cuidados.**

- Proibido: quinta tentativa, relaxar o goal ou marcar como concluído com teste falhando.
- Os goals padrão são de .NET. Em outra stack, ajuste `G1` e `G2` na task.
- O registro de cada tentativa fica na própria task, não em arquivo solto: quem retoma o trabalho lê a task e vê o que já foi tentado.

### `/bkhar:review`

**Para que serve.** Dispara o agente `reviewer` numa invocação separada e read-only, para uma revisão independente de segurança e conformidade. Quem escreveu o código não revisa a si mesmo.

**Onde rodar.** Raiz do repo do projeto.

**Quando usar.** Antes de aprovar uma entrega que toca uma área sensível declarada no manifesto. Também quando a mudança toca documentação viva.

**Pré-requisito.** O manifesto em `{repo}/.claude/multiagente.md`. Sem ele, o comando para e orienta a criar a partir do template `manifesto-projeto.md`.

**Argumentos.** O repo a revisar, `${BKS_VAULT}/repos/{categoria}/{projeto}`. Sem argumento, o comando pergunta. Ele nunca adivinha o projeto ativo.

**O que ele faz, passo a passo.**

1. Confere o manifesto. Sem manifesto, para.
2. Confere se a mudança toca alguma área sensível do manifesto. Se não toca, a revisão é opcional.
3. Monta o contexto do `reviewer`: a checklist de revisão crítica, as invariantes e áreas sensíveis do manifesto, `decisions/` e o diff da entrega.
4. Dispara o `reviewer` em invocação separada.
5. Devolve os achados, ou a declaração do escopo verificado se nada foi encontrado.
6. Achado crítico bloqueia a entrega, é registrado em `decisions/` e volta ao `builder` em outra invocação.

Revisão de escrita, quando a mudança toca `README.md`, `ARCHITECTURE.md`, cânone, spec ou material de treinamento. Ela roda na própria sessão, sem o `reviewer` e mesmo sem manifesto:

1. Roda `python ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/writing_guard.py <arquivos .md>` e cola a saída.
2. Lê cada arquivo pela checklist da skill `bks-writing` e reporta a nota por dimensão e o total. Abaixo de 45, diz o que revisar.

**O que produz.** Uma lista de achados no formato `arquivo:linha`, problema, exploração e severidade. Achado crítico também vira registro em `decisions/`.

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:review ${BKS_VAULT}/repos/backside/pix-comprovante
→ Manifesto: .claude/multiagente.md
→ Área sensível tocada: "dado de transação de cliente".
→ reviewer · Opus · Read, Grep, Glob

→ app/PixComprovante.Api/Adapters/Inbound/ComprovanteEndpoints.cs:42
   Problema: a consulta por identificador fim a fim não confere o titular.
   Exploração: um cliente autenticado lê o comprovante de outro cliente.
   Severidade: crítica
→ Entrega bloqueada. Achado registrado em decisions/; correção volta ao builder.
```

**Cuidados.**

- Não gaste o `reviewer`, que roda em Opus, com mudança só de documentação. Para isso existe a revisão de escrita.
- O `reviewer` recebe o diff ou os arquivos da entrega, não o repo inteiro.
- Achado já decidido e aceito em `decisions/` não volta como novo.

### `/bkhar:maintainability`

**Para que serve.** Inventaria as aplicações de `app/`, gera um parecer de manutenibilidade por aplicação e atualiza o documento único de fundamentação do projeto. Usa a skill `bks-maintainability-review`.

**Onde rodar.** Raiz do repo do projeto, com `STATUS.md` na raiz. Na raiz do vault, o comando pergunta qual projeto e para.

**Quando usar.** Quando há código em `app/` e você quer uma nota de manutenibilidade, comparar versões ou ver a fundamentação teórica do projeto.

**Pré-requisito.** `app/` com código. Sem código, o comando diz isso e para.

**Argumentos.** `[opcional: nomes das aplicações a avaliar]`. Vazio avalia todas.

**O que ele faz, passo a passo.**

1. Inventaria `app/` pela detecção de cada stack conhecida e mostra a tabela de aplicação, stack, tipo e raiz.
2. Pergunta, uma pergunta por vez, quando o tipo é indeterminado, a stack não tem critérios ou não está claro o que é uma aplicação.
3. Acima de três aplicações, confirma a lista antes, porque cada parecer lê muito código.
4. Lê `CLAUDE.md`, `specs/`, `decisions/` e `brain/engineering/`. Com `BKS_VAULT` definido, calibra a persona pelo vault.
5. Gera um parecer por aplicação e compara com o parecer anterior, se houver.
6. Gera nova versão da fundamentação só se algum conceito ou decisão entrou, mudou ou saiu.
7. Grava o critério da execução e reporta uma linha por aplicação.

**O que produz.**

- `outputs/maintainability/<app>_<tipo>_<AAAA-MM-DD>.html`, um por aplicação; nome repetido ganha `_HHmm`
- a fundamentação do projeto em `outputs/references/`
- `docs/prompts/prompt-maintainability-{YYYY-MM-DD}.md`

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:maintainability
→ Aplicação              Stack   Tipo          Raiz
  pix-comprovante-api    .NET    API           app/PixComprovante.Api/PixComprovante.slnx
  db-scripts             SQL     Scripts SQL   app/db/
→ Duas aplicações, sem dúvida de tipo. Seguindo.

→ pix-comprovante-api · nota <nota> · faixa <faixa> · confiança <confiança>
  outputs/maintainability/pix-comprovante-api_API_2026-10-18.html
→ db-scripts · nota <nota> · faixa <faixa> · confiança <confiança>
  outputs/maintainability/db-scripts_Scripts-SQL_2026-10-18.html
→ Fundamentação: versão nova v1 em outputs/references/.
```

**Cuidados.**

- O comando nunca pontua sem evidência e nunca aplica o critério de uma stack a outra.
- Stack sem critérios em `stacks/` (hoje há .NET e SQL) é pulada, ou avaliada só com a rubrica comum e confiança baixa declarada. A escolha é sua.
- Parecer anterior nunca é sobrescrito.
- Sem vault, o parecer usa a persona base e registra isso.

---

## 6. Fechamento e migração

### `/bkhar:save`

**Para que serve.** Fecha a sessão. Roteia decisões para `decisions/` e specs para `specs/`, reescreve o `STATUS.md`, acrescenta o marco ao `JOURNAL.md` e mede o consumo.

**Onde rodar.** Raiz do repo do projeto.

**Quando usar.** Ao fechar a sessão, ou depois de um marco: feature aprovada, task concluída.

**Pré-requisito.** `STATUS.md` na raiz. Sem ele, o comando pergunta se é para criar a partir do template.

**O que ele faz, passo a passo.**

1. Levanta o que mudou com `git status` e `git diff --stat`, mais o que a sessão decidiu sem tocar em arquivo.
2. Classifica cada item pela tabela de destino. Item que não se encaixa vira pergunta.
3. Escreve os ADRs, numerados a partir do maior existente, e as specs.
4. Se existe `docs/canonical/CONTEXT.md`, procura specs e decisões mais novas que ele. Havendo, o canônico está defasado.
5. Reescreve o `STATUS.md` por inteiro. Defasagem do canônico entra na seção do que trava.
6. Acrescenta ao topo do `JOURNAL.md` a entrada com data, título e duas a quatro linhas do que mudou.
7. Mede o consumo da sessão pelo `session_cost.py`. Sem o script, diz em uma linha que pulou.
8. Confirma em até cinco linhas, uma por arquivo gravado.

O destino de cada coisa:

| O que a sessão produziu | Destino |
|---|---|
| decisão de arquitetura, stack ou contrato | `decisions/ADR-NNN.md` |
| spec nova ou alterada | `specs/features/`, `specs/tests/`, `specs/tasks/` |
| onde o projeto parou | `STATUS.md`, reescrito |
| marco da sessão | `JOURNAL.md`, acrescentado no topo |
| canônico defasado pela spec ou pelo ADR | `STATUS.md`, seção do que trava |
| entregável gerado | `outputs/` |
| conhecimento de domínio | `brain/domain/` |
| padrão técnico que se firmou | `brain/engineering/` |
| decisão sobre o processo de trabalho, rara | `${BKS_VAULT}/workbench/decisions/` |

A medição de consumo segue `commands/references/medicao-consumo.md`:

1. Grava o checkpoint no ledger `{repo}/.logs/cost-ledger.jsonl`, com a fase e um rótulo curto da sessão.
2. Mostra a tabela da sessão e a linha `TOTAL GERAL` do acumulado.
3. Atualiza o painel `{repo}/.logs/custo-tokens.md`, lido pelo Dataview, sem recriá-lo.
4. Registra a tabela no `JOURNAL.md`, sob `### Consumo da sessao`. Com subagentes, registra também `### Modelos usados`.

**O que produz.**

- `STATUS.md` reescrito e `JOURNAL.md` acrescido
- `decisions/ADR-NNN.md` e specs, quando a sessão os produziu
- `.logs/cost-ledger.jsonl` e `.logs/custo-tokens.md`

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:save
→ decisions/ADR-002.md — idempotência da emissão pelo identificador fim a fim
→ specs/tasks/TASK-emissao-comprovante.md — task 1 marcada concluída
→ STATUS.md — reescrito; trava: canônico v2 mais antigo que ADR-002.md e FEAT-emissao-comprovante.md
→ JOURNAL.md — entrada 2026-10-18 "Emissão idempotente implementada"
→ Consumo: tabela da sessão e TOTAL GERAL registrados no JOURNAL.md
→ Rode /bkhar:canonize para reconsolidar o canônico.
```

**Cuidados.**

- Só se registra o que foi verificado. Teste que rodou leva a linha que comprova; teste que não rodou é declarado assim.
- O `STATUS.md` é reescrito, nunca acumulado. Estado antigo vai para o `JOURNAL.md`.
- O `JOURNAL.md` é acrescido, nunca reescrito. Sessão que não produziu nada não vira entrada.
- ADR só para decisão fechada. Discussão em aberto fica no `STATUS.md`.
- O comando acusa o canônico defasado, mas não o corrige. Não rode o `/bkhar:canonize` dentro do save nem escreva nota de síntese para compensar.
- O valor de consumo é estimativa por token contra o `pricing.json` local, não a fatura real. Falha na medição nunca bloqueia o save.

### `/bkhar:migrate`

**Para que serve.** Traz um projeto do kit `bks` para o `bkhar`. Confere o layout, cria o que falta pelos templates, troca o prefixo no `WORKFLOW.md` e no `CLAUDE.md` e grava o `.bkhar.json`, que marca o projeto como migrado.

**Onde rodar.** Raiz do repo do projeto. Na raiz do vault, o comando recusa.

**Quando usar.** Uma vez por projeto, entre fases, com a sessão anterior fechada. É o passo que tira o projeto do `/bks:*` e o põe no `/bkhar:*`.

**Pré-requisito.** Árvore do git limpa: feche a sessão com `/bks:save` e commite antes. Projeto já com `.bkhar.json` não é migrado de novo.

**O que ele faz, passo a passo.**

1. Recusa se já existe `.bkhar.json` ou se há mudança pendente no git.
2. Confere `STATUS.md`, `WORKFLOW.md`, `JOURNAL.md`, `.bks-profile.json`, `brain/` e `specs/{features,tests,tasks}`, e mostra a tabela do que falta.
3. Com o seu ok, cria o que falta pelo esqueleto de projeto, sem sobrescrever nada. Sem `.bks-profile.json`, pergunta o perfil.
4. Lista e troca `/bks:` por `/bkhar:` só no `WORKFLOW.md` e no `CLAUDE.md`.
5. Grava o `.bkhar.json` e acrescenta a entrada da migração no topo do `JOURNAL.md`.
6. Mostra `git status` e `git diff --stat` e sugere o commit. Não commita.

**O que produz.**

- `.bkhar.json`: `{"plugin": "bkhar", "migrated_from": "bks", "migrated_at": "AAAA-MM-DD"}`
- `WORKFLOW.md` e `CLAUDE.md` com `/bkhar:*`
- os itens de layout que faltavam, e a entrada no `JOURNAL.md`

**Exemplo.**

```
cd ${BKS_VAULT}/repos/backside/pix-comprovante
/bkhar:migrate
→ árvore limpa; .bkhar.json não existe
→ layout: STATUS.md ok · WORKFLOW.md ok · JOURNAL.md ok · .bks-profile.json falta · brain/ ok · specs/ ok
→ "Qual o perfil? backend, fullstack, component..." — backend
→ WORKFLOW.md: 6 ocorrências de /bks: · CLAUDE.md: 2 — trocar? — sim
→ gravados .bks-profile.json e .bkhar.json; entrada no JOURNAL.md
→ git diff --stat: 4 arquivos. Sugestão: git commit -m "chore: migra para o bks-harness"
→ depois, abra a sessão de novo e rode /bkhar:brain
```

**Cuidados.**

- O `JOURNAL.md`, as ADRs e as specs não são reescritos: guardam o que foi feito com o `bks`.
- Nomes de skill (`bks-sdd`...) e as variáveis `BKS_*` ficam como estão.
- Até o commit, tudo é reversível: `git checkout -- .` e `git clean -fd` desfazem a migração.
- Projeto não migrado continua funcionando com `/bks:*`. Não há prazo para migrar antes da Fase 7.

---

## 7. A skill `bks-sdd`

O `/bkhar:spec` e a skill `bks-sdd` especificam em escalas diferentes.

| Use | Quando |
|---|---|
| `/bkhar:spec` | a feature já é entendida, o projeto já existe, e o FEAT e o TEST bastam |
| skill `bks-sdd` | o produto é novo e grande, ou o escopo é incerto e pede decomposição formal |

A skill conduz o ciclo completo, com PRD, plano macro e decomposição em tasks. Ela guarda o estado entre sessões num `workspace-*/`.

| Flag | Para que |
|---|---|
| `/bks-sdd` | cria o `workspace-[nome]/` |
| `--prd` | gera o PRD a partir do que está em `research/` |
| `--project` / `--project-prd` / `--project-plan` | projeto interno, seu PRD e seu plano de fases |
| `--feature` / `--feature-tests` / `--feature-task` | FEAT, depois TEST, depois as tasks |
| `--feature-list` / `--task-list` / `--status` | o que existe e onde parou |
| `--impl-init` / `--task-done` | executa e fecha task |
| `--continue` / `--tan` / `--clear` | retoma, ou encerra salvando o estado |
| `--cost` / `--cost-report` | consumo da sessão e do ciclo |

As etapas não se pulam. O `--feature-tests` só roda com FEAT aprovada, e o `--feature-task` só com TEST aprovado.

> Não confunda o `/bkhar:prd` com o `bks-sdd --prd`. O primeiro parte sempre de `docs/canonical/CONTEXT.md` e é o caminho padrão. O segundo é o fluxo pesado da skill, com plano e rastro de tasks.

Os projetos em curso usam o `/bkhar:spec` com `specs/` no repo. Nenhum deles tem `workspace-*`.

---

## 8. Agentes

Cada agente tem as ferramentas do seu papel, e só elas. A restrição é o desenho.

| Agente | Papel | Modelo | Ferramentas |
|---|---|---|---|
| `planner` | escopo vira FEAT, TEST e TASK; nunca código de produção | Opus | Read, Write, Grep, Glob |
| `builder` | implementa sob LOOP-4, dentro dos limites da FEAT aprovada | Sonnet | Read, Write, Edit, Grep, Glob, Bash |
| `reviewer` | revisão de segurança independente, só leitura | Opus | Read, Grep, Glob |
| `scribe` | registra só o que foi confirmado com evidência | Haiku | Read, Write, Edit, Grep, Glob |

Invoque pelo nome com o prefixo do plugin: `bkhar:planner`, `bkhar:builder`, `bkhar:reviewer`, `bkhar:scribe`. No plugin antigo, `bks:reviewer` e equivalentes.

O `/bkhar:review` dispara o `reviewer` com o contexto certo. Prefira o comando à invocação direta.

Ao iniciar, cada agente diz em uma linha o nome, o modelo e as ferramentas, para você saber que tier está pagando:

```
reviewer - Opus - Read, Grep, Glob
```

Três consequências do arranjo:

- **A revisão é independente porque não pode agir.** Sem `Write`, o `reviewer` não transforma achado em correção silenciosa.
- **O modelo acompanha o julgamento.** Opus onde se julga, Sonnet onde se executa spec aprovada, Haiku onde se transcreve evidência.
- **O papel é invocado, não assumido.** O `reviewer` roda sem o estado da sessão que produziu o código.

---

## 9. Guardas

O plugin instala cinco hooks. Os três primeiros recusam a escrita e devolvem a razão no bloqueio. O `writing_guard` deixa a escrita passar e devolve os achados para correção na mesma passada.

| Guarda | Quando dispara | O que recusa |
|---|---|---|
| `no_dispatcher` | escrita em `.cs` | `MediatR`, `IMediator`, `ISender`, `IRequestHandler<>`, `AddMediatR` e equivalentes |
| `comment_budget` | escrita em `.cs` | bloco de comentário acima de 5 linhas e marca de severidade em comentário |
| `dod_docs` | escrita em `.cs` que declara tipo público | a escrita, enquanto `README.md` e `ARCHITECTURE.md` não forem tocados na mesma leva |
| `writing_guard` | depois da escrita em `.md` de documentação viva | nada; devolve frase longa, sigla sem definição, muleta, emoji e ADR fora da nota de decisão |
| `session_memory` | início de sessão | nada; carrega o `STATUS.md` do projeto, ou o perfil na raiz do vault |

Os guardas de código ignoram arquivo de teste, arquivo fora de repositório git e o que não é `.cs`. Falha interna de um guarda libera a escrita. Todos exigem `python` no `PATH`.

O `writing_guard` também roda sobre arquivos inteiros, com saída 1 quando há achado:

```
python hooks/scripts/writing_guard.py docs/ARCHITECTURE.md
```

---

## 10. Cola rápida

| Comando | Onde rodar | Pré-requisito | Produz |
|---|---|---|---|
| `/bkhar:brain` | raiz do vault ou raiz do repo | nenhum | panorama, ou estado do projeto, só na conversa |
| `/bkhar:new-project` | raiz do vault | nome, categoria e perfil | `repos/{categoria}/{nome}/` com perfil, `STATUS.md`, `JOURNAL.md` e git |
| `/bkhar:ingest` | qualquer pasta | fonte, lote ou `raw/_inbox/` | página em `${BKS_VAULT}/knowledge/wiki/`, `index.md`, `log.md` |
| `/bkhar:note` | raiz do repo | nenhum | nota viva em `docs/input/notas/` |
| `/bkhar:canonize` | raiz do repo, ou vault perguntando o projeto | material em `docs/input/` ou `docs/design/` | `docs/canonical/CONTEXT.md` |
| `/bkhar:prd` | raiz do repo, ou vault perguntando o projeto | `CONTEXT.md` consolidado | `docs/canonical/PRD-{projeto}.md` |
| `/bkhar:spec` | raiz do repo | PRD ou `CONTEXT.md` | `specs/features/FEAT-*.md`, depois `specs/tests/TEST-*.md` |
| `/bkhar:arch` | raiz do repo | specs em `specs/` | `outputs/ARCH-[projeto].md` e `README.md` |
| `/bkhar:loop` | raiz do repo | FEAT e TEST aprovados | código com testes, ou `outputs/BLOQUEIO-[task].md` |
| `/bkhar:review` | raiz do repo | `.claude/multiagente.md` | achados de segurança e conformidade |
| `/bkhar:maintainability` | raiz do repo | código em `app/` | `outputs/maintainability/*.html`, `outputs/references/` |
| `/bkhar:save` | raiz do repo | `STATUS.md` | `STATUS.md` reescrito, `JOURNAL.md` acrescido, ADRs, specs e consumo |
| `/bkhar:migrate` | raiz do repo | árvore limpa, projeto no `bks` | `.bkhar.json`, prefixo trocado no `WORKFLOW.md` e no `CLAUDE.md` |

Só `/bkhar:brain` e `/bkhar:new-project` são de vault. Todos os outros escrevem no repositório onde a sessão está aberta.

---

## 11. Comandos propostos

Ainda não existem. Estão no desenho do harness e podem mudar antes de nascer.

| Comando | Onde rodaria | O que faria | Status |
|---|---|---|---|
| `/bkhar:refine` | repo | abre o rito de refinamento | *proposto* |
| `/bkhar:panel` | qualquer pasta | painel com 2 ou 3 agentes | *proposto* |
| `/bkhar:brainstorm` | qualquer pasta | rito de brainstorming com a skill de mesmo nome | *proposto* |
| `/bkhar:ask <agent>` | qualquer pasta | pergunta direta a um papel, com atalho `@<agente>` | *proposto* |
| `/bkhar:retro` | repo | retrospectiva da FEAT atual | *proposto* |
| `/bkhar:curate` | repo do harness | revisa as propostas pendentes | *proposto* |
| `/bkhar:skill new / list / promote` | repo do harness | cria, lista e promove skills | *proposto* |
| `/bkhar:cost` | repo | custo por agente, modelo, skill e fase, evoluindo o `--cost-report` | *proposto* |
