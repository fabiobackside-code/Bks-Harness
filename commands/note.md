---
description: Escreve ou atualiza uma nota viva em docs/input/notas/ do projeto atual — material bruto para alimentar o /bkhar:canonize.
---

`/bkhar:note <assunto> [--pasta <subpasta>]`

Escreve ou atualiza UMA nota viva em `docs/input/notas/` do projeto atual, no padrão já
consolidado nos projetos do vault: material bruto do autor para alimentar o `/bkhar:canonize` —
nunca decisão fechada. Diferente de `docs/input/research/` (material de terceiros).

Argumentos:
- `<assunto>`: do que a nota trata. Vira o nome do arquivo em `SCREAMING-KEBAB.md` (ex.:
  "arquitetura pretendida" → `ARQUITETURA-PRETENDIDA.md`). Sem data no nome — a nota é viva,
  cresce ao longo dos dias; a cronologia fica numa seção `## Estado em YYYY-MM-DD` dentro do
  arquivo, nunca no nome do arquivo.
- `--pasta <subpasta>` (opcional): grava dentro de `docs/input/notas/<subpasta>/` em vez da
  raiz de `notas/` — use para a fila de um colaborador externo específico (ex.:
  `<especialista>/`, com apontamentos e áudios de um especialista de domínio, tratados à parte
  das notas do próprio autor).

Faça, nesta ordem:

0. **Bootstrap** (só se `docs/input/notas/` ainda não existir neste repo):
   - Pergunte ao usuário, em UMA pergunta objetiva: qual é a hierarquia de fontes deste projeto
     (ex.: num projeto de método, especialista de domínio > livro do método > base científica;
     num projeto regulado, normativo do órgão > POC > cânone interno). Se ele não souber ainda, deixe a seção como `[EM ABERTO]` — não
     invente uma hierarquia.
   - Crie `docs/input/notas/LEIA-ME.md` com esta estrutura fixa (adaptando ao projeto):
     - **O que é esta pasta** — material bruto do autor para o `/bkhar:canonize`; diferente de
       `docs/input/research/`. Status: entrada crua, nada aqui é decisão fechada — a parte
       definitiva mora em `docs/canonical/`.
     - **Exceção à imutabilidade de `docs/input/`** — se o `CLAUDE.md` do repo trata
       `docs/input/` como imutável, registre que `notas/` é a exceção: material vivo, editado
       e ampliado ao longo das sessões; agentes podem e devem editá-la.
     - **Regras desta pasta** — as regras fixas: (1) uma nota por assunto, nome
       `SCREAMING-KEBAB.md` sem data; (2) marcar incerteza com `> [!uncertain]`, nunca como
       afirmação; (3) não reabrir o que já está fechado em `docs/canonical/` — nota que
       contradiz uma decisão fixada deve dizer isso explicitamente, com o argumento, nunca
       sussurrar a mudança; (4) idioma: documentação em PT-BR, identificador de código em
       inglês.
     - **Marcação de procedência** — tabela fixa: `[AUTOR]` decisão ou observação do autor —
       autoridade sobre produto e arquitetura; `[PESQUISA]` resultado de rodada de pesquisa
       técnica; `[INFERIDO]` leitura nossa, precisa de validação; `[EM ABERTO]` lacuna
       reconhecida.
     - **Hierarquia de fontes** — o que o usuário respondeu no passo anterior.
     - **Índice** — tabela vazia (`Nota | Assunto`), preenchida a cada `/bkhar:note`.
     - **Fluxo** — diagrama fixo:
       ```
       docs/input/notas/  +  docs/input/research/  +  docs/design/
               │
               ▼  /bkhar:canonize
       docs/canonical/CONTEXT.md
               │
               ▼  /bkhar:prd
       docs/canonical/PRD-{projeto}.md
               │
               ▼  /bkhar:spec
       specs/features/ · specs/tasks/ · specs/tests/
       ```
   - Avise que a pasta foi criada e continue para o passo 1 com a primeira nota.

1. Verifique se `docs/canonical/` já tem alguma decisão fechada que colida com o assunto da
   nota. Se colidir, NÃO ignore — abra a nota (ou a seção nova) declarando o conflito
   explicitamente, com o argumento, em vez de sussurrar uma mudança (regra 3 acima).

2. Se a nota (`docs/input/notas/[<subpasta>/]<ASSUNTO>.md`) ainda não existe: crie com um
   cabeçalho `# <título>` e o conteúdo que o autor passou nesta mensagem, já com procedência
   marcada (default `[AUTOR]` para o que ele escreveu direto; use `[PESQUISA]`/`[INFERIDO]` só
   para o que VOCÊ está acrescentando e não veio dele) e incerteza como `> [!uncertain]` onde
   for o caso.

3. Se a nota já existe: NÃO sobrescreva o conteúdo anterior. Acrescente sob uma nova seção
   `## Estado em YYYY-MM-DD` (data de hoje) com o que mudou. Se o novo conteúdo contradiz algo
   já escrito na própria nota, marque a contradição explicitamente ali — não apague o texto
   antigo em silêncio.

4. Atualize a tabela `## Índice` do `LEIA-ME.md`: acrescente ou atualize a linha da nota (nome
   do arquivo | assunto em uma frase).

5. Reporte: o que foi criado/alterado (arquivo e seção), se algum conflito com
   `docs/canonical/` foi sinalizado, e o próximo passo ("quando tiver notas suficientes sobre
   este assunto, rode `/bkhar:canonize`" — ou, se a hierarquia de fontes ainda estiver
   `[EM ABERTO]`, lembre disso).

Nunca escreva como decisão fechada o que é rascunho — é o mesmo erro que o `/bkhar:canonize` evita do
lado de lá. `docs/input/notas/` é a exceção à imutabilidade normal de `docs/input/`: aqui, o
`/bkhar:note` pode e deve editar o que já existe.
