---
description: Ingestão de conhecimento para a base em knowledge/ do vault — fonte única, lote ou pasta drop-zone.
---

NOTA (comando global): este comando opera SEMPRE sobre `${BKS_VAULT}/knowledge/`, independente
de onde a sessão está aberta — knowledge/ não é por-projeto, é a base transversal do vault. Todos
os caminhos abaixo (`raw/`, `wiki/`, `tools/`) são relativos a `${BKS_VAULT}/knowledge/`.

Uso:
```
/bkhar:ingest raw/papers/nome.pdf         → ingere um PDF específico (fonte externa: livro, artigo, paper)
/bkhar:ingest raw/articles/nome.md        → ingere um artigo já salvo em Markdown
/bkhar:ingest raw/articles/nome.html      → ingere uma página web salva localmente
/bkhar:ingest raw/videos/nome-transcrição.md   → ingere uma transcrição de vídeo
/bkhar:ingest raw/notas-pessoais/nome.md  → arquiva uma nota pessoal (prospecção, linha de pensamento) — NÃO vira página wiki curada
/bkhar:ingest https://exemplo.com/artigo  → busca o link, salva cópia em raw/, ingere
/bkhar:ingest tools/batch-ingest.md       → processa a tabela de lote (várias fontes)
/bkhar:ingest raw/_inbox/                 → classifica e processa TUDO que estiver na pasta
/bkhar:ingest                             → sem argumento: assume raw/_inbox/
```

## Duas naturezas de fonte — não confundir

Esta base guarda dois tipos de material, com destino diferente:

1. **Fonte externa** (PDF de livro/paper/artigo, transcrição de vídeo, clipping web) — conhecimento
   de terceiro. Vai para `raw/{papers,articles,videos,clippings,links}/`, e o `/bkhar:ingest` CURA: lê,
   resume, extrai conceitos, gera/atualiza página em `wiki/` seguindo o schema de página (Concept,
   Architecture, Pattern, etc — ver `../CLAUDE.md` deste repositório). `raw/notes/` também é fonte
   já curada (guidelines prescritivos escritos formalmente) — segue a mesma regra de fonte externa,
   não a regra de nota pessoal abaixo, mesmo sendo autoria própria.
2. **Nota pessoal / prospecção** (linha de pensamento ainda em aberto, ideia para projeto futuro,
   reflexão não fechada — o rascunho antes de virar guideline) — vai para `raw/notas-pessoais/`.
   O `/bkhar:ingest` NÃO resume nem reformula como se fosse fonte de terceiro: arquiva com frontmatter
   próprio (`type: "prospecção"` ou `type: "reflexao"`) em `wiki/prospecções/`, preservando a voz e
   a incerteza do autor. Nunca vira `## Definition` / `## Core principles` como se fosse conceito
   estabelecido — é pensamento em aberto, marcado como tal. Quando a ideia amadurecer e virar
   guideline formal, o destino muda para `raw/notes/` (fonte curada), não fica em
   `notas-pessoais/`.

Se o tipo da fonte não for óbvio pela extensão/conteúdo, pergunte ao usuário antes de classificar
— não adivinhe se é "conhecimento curado" ou "prospecção pessoal".

## Regras (sempre válidas, vêm de `../CLAUDE.md`)
- `raw/` é imutável: a fonte original nunca é editada, só lida e resumida (exceção: notas
  pessoais em `raw/notas-pessoais/`, que o autor pode reabrir e ampliar — arquivo append-only por
  seção de data, nunca reescrito por cima).
- Toda página nova/atualizada em `wiki/` leva o frontmatter YAML padrão
  (ver `../CLAUDE.md` seção "YAML Frontmatter Standard").
- Atualize `wiki/index.md` e `wiki/log.md` ao final de CADA fonte processada.
- Se não for possível extrair conteúdo real (PDF protegido, vídeo sem
  transcrição disponível, link bloqueado/pago), PARE e diga isso —
  nunca invente o conteúdo a partir do nome do arquivo ou da URL.
- **Idempotência:** se a fonte já tem página correspondente na wiki (mesmo
  arquivo/URL registrado em `wiki/log.md`), NÃO reprocesse por conta própria —
  avise que já existe e pergunte se é para atualizar mesmo assim. Só force
  reprocessamento se o usuário pedir explicitamente.

## Passo a passo por tipo de fonte

**PDF / paper** (`raw/papers/*.pdf`) — leia o arquivo diretamente (PDFs longos:
leia por intervalo de páginas). Resuma, extraia os conceitos-chave, crie ou
atualize a página certa em `wiki/`.

**Artigo em Markdown** (`raw/articles/*.md`) — normalmente já veio de um
clipper (ex. Obsidian Web Clipper). Leia e cure normalmente.

**Página HTML salva localmente** (`raw/articles/*.html`) — leia o arquivo como
texto/markup e extraia o conteúdo relevante (ignore nav/menu/rodapé/scripts).
Se o HTML estiver muito ruidoso para uma boa curadoria, diga isso e sugira
salvar a página como Markdown antes (Obsidian Web Clipper, ou "Reader mode" +
copiar/colar).

**Link web ainda não salvo** (URL direta) — busque o conteúdo da URL. ANTES de
curar para a wiki, salve uma cópia do conteúdo extraído em
`raw/articles/<slug-do-título>.md`, com a URL original no topo do frontmatter —
isso preserva a fonte mesmo se a página sair do ar depois. Só então gere/edite
a página em `wiki/`.

**Vídeo** (`raw/videos/*`) — este comando NÃO transcreve áudio/vídeo sozinho.
Espera um arquivo de TEXTO (`.txt`, `.md` ou `.srt`) com a transcrição. Se
receber um `.mp4`/`.mov` diretamente, PARE e oriente a gerar a transcrição
antes — legendas exportadas do YouTube, ou uma ferramenta local de
transcrição (ex. Whisper) — nunca invente o conteúdo do vídeo a partir do
nome do arquivo ou da descrição.

**Nota pessoal** (`raw/notas-pessoais/*.md`) — leia o arquivo. NÃO resuma nem cure como fonte
externa. Copie/organize para `wiki/prospecções/<slug>.md` com frontmatter
`type: "prospecção"` (ou `"reflexao"`), preservando o texto do autor essencialmente como está —
apenas adicione frontmatter, uma seção `## Contexto` (quando/por que foi escrita) se não estiver
óbvia, e `## Conecta com` linkando conceitos já existentes na wiki que se relacionam, SEM
reescrever a ideia em prosa de terceiro. Se o autor já indicou incerteza, preserve `> [!uncertain]`
tal como está — não resolva a incerteza por conta própria.

**Lote via tabela** (`tools/batch-ingest.md`) — leia a tabela
(# | Type | Path or URL | Title | Priority). Processe uma fonte por vez, na
ordem `high` → `medium` → `low`, cada uma seguindo a regra do seu tipo acima
(`pdf`, `article` = markdown/html local, `video` = transcrição, `link` = URL,
`nota` = nota pessoal). Ao final, imprima um resumo linha a linha no formato:
```
✓ [prioridade] <arquivo/URL de origem> → <página(s) de wiki/ criada(s) ou atualizada(s)>
```
usando `✗ [prioridade] <origem> → falhou: <motivo>` para as que falharem —
uma falha não interrompe o processamento das demais linhas da tabela. Feche
confirmando que `wiki/index.md` e `wiki/log.md` foram atualizados.

**Pasta drop-zone** (`raw/_inbox/`, padrão sem argumento, ou outra pasta indicada) — liste
todos os arquivos. Para cada um: identifique o tipo pela extensão/conteúdo E pela natureza
(fonte externa curada vs nota pessoal — pergunte se não for óbvio): `.pdf` → `papers/`,
`.md`/`.html` de artigo → `articles/`, transcrição de vídeo → `videos/`, lista de URLs →
`links/`, nota pessoal/prospecção → `notas-pessoais/`. MOVA para a subpasta correta dentro de
`raw/` (nunca deixe duplicado na `_inbox`), e então ingira cada um normalmente pela regra do seu
tipo. Ao final, resuma quantos arquivos de cada tipo foram processados e para onde foram.
