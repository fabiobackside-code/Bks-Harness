---
description: Consolida docs/input/ e docs/design/ de um projeto num contexto canônico único, fonte para o /bkhar:prd e o /bkhar:spec.
---

Consolida o material de pesquisa (docs/input/ + docs/design/) de UM projeto em um contexto
canônico único — a fonte que vai alimentar o /bkhar:prd e, depois, o /bkhar:spec.

Este comando pode rodar aberto na raiz do vault (pergunte QUAL projeto,
${BKS_VAULT}/repos/{categoria}/{projeto}) ou já dentro do repo do projeto (aí o projeto é óbvio, não
pergunte).

Pré-requisito: o projeto existe (foi criado com /bkhar:new-project) e tem algo em docs/input/ e/ou
docs/design/. Se as duas pastas estiverem vazias, avise e pare — não invente contexto.

Faça, nesta ordem:

1. Leia TUDO em docs/input/{scope,interviews,research,assets}/ e docs/design/ (arquivos .md,
   .txt, .html; para PDF/docx, extraia o texto). NÃO leia brain/ (domínio do produto e
   padrões técnicos, não escopo/contexto) nem app/ (isso é código/experimento).

   Leia também specs/features/, specs/tests/ e decisions/, se existirem. Spec aprovada e ADR
   fechado são fonte canônica tanto quanto entrevista — depois da primeira entrega, são a parte
   mais atual do que o projeto decidiu. Trate cada um como fonte citável
   (ex.: "[decisions/ADR-004.md]"), não como material bruto a reinterpretar.

2. Monte um rascunho de docs/canonical/CONTEXT.md com, no mínimo, estas seções: Propósito do
   produto, Usuários/personas, Escopo (dentro/fora), Decisões já fixadas (com a fonte), Lacunas
   e perguntas em aberto, Glossário. Cite a fonte de cada afirmação relevante (ex.:
   "[docs/input/interviews/entrevista-01.md]").

   Em "Decisões já fixadas", o que vem de decisions/ e specs/ tem precedência sobre o material de
   docs/input/. Onde os dois se contradizem, a decisão fechada venceu a intenção original — não é
   divergência a marcar como incerta. Registre a mudança sob "## O que mudou desde v{N}", com as
   duas fontes.

3. Onde o material diverge ou é ambíguo, NÃO decida sozinho — marque
   `> [!uncertain] <pergunta objetiva>` no lugar e liste todas essas perguntas no fim, sob
   "## Perguntas em aberto". Pergunte ao usuário antes de fechar o documento, se possível.

3a. Se o projeto referencia uma skill — no CLAUDE.md, no STATUS.md, numa spec ou numa ADR —, leia
   o SKILL.md dela e confronte com o que o projeto concretizou: conceito, definição, guarda,
   fundamento, guideline. Skill escrita antes do código fica para trás; o projeto concreto é a
   evidência mais nova. Divergência não se resolve em silêncio — cada uma é questionável e entra
   em "## Divergências com skills", classificada:

   - **Aprendizado** — a skill está desatualizada; o projeto acertou o que ela não previa. O
     canônico segue o projeto, e a entrada diz o que muda na skill, com a fonte do projeto.
   - **Exceção** — o projeto diverge de propósito e a skill segue valendo para os outros. Só é
     exceção com ADR que a registre; sem ADR, é `> [!uncertain]`.

   Na dúvida entre as duas, pergunte. Não edite a skill daqui: ela mora fora do repo do projeto.
   Reporte o aprendizado para quem mantém a skill o aplicar.

4. Se já existir um docs/canonical/CONTEXT.md anterior: NÃO sobrescreva sem arquivar — copie a
   versão atual para docs/history/CONTEXT-v{N}-{YYYY-MM-DD}.md primeiro, incremente a versão no
   frontmatter do novo (version: N+1) e resuma o que mudou sob "## O que mudou desde v{N}".

5. Frontmatter obrigatório no CONTEXT.md:
   ---
   projeto: {nome}
   version: N
   status: rascunho | revisado
   atualizado: YYYY-MM-DD
   fontes: [lista dos arquivos de docs/input/, docs/design/, specs/ e decisions/ usados]
   ---

6. Registre o critério usado nesta consolidação em docs/prompts/prompt-canonize-{YYYY-MM-DD}.md
   — é o que permite regerar ou auditar depois.

7. Reporte: o que entrou no canônico, quantas perguntas ficaram em aberto, quantas divergências com
   skills há e de que classe, e o próximo passo
   ("revise docs/canonical/CONTEXT.md, responda as perguntas em aberto se quiser fechar tudo, e
   rode /bkhar:prd quando o contexto estiver bom o suficiente para virar requisito").

8. Se `app/` tiver código, acrescente uma linha ao reporte sugerindo `/bkhar:maintainability` para
   gerar o parecer de manutenibilidade de cada aplicação e a fundamentação do projeto. Com `app/`
   vazio, não sugira nada: não há o que avaliar.

Nunca promova para canônico algo que você mesmo inventou para preencher lacuna — isso é
alucinação disfarçada de síntese. Marque como incerto e pergunte.