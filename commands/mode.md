---
description: "Troca o modo de condução do projeto — /bkhar:mode <colaborativo|autonomo>. Roda a checagem de prontidão, grava ADR e altera o .bks-profile.json. Sem argumento, mostra o modo atual e a prontidão."
---

Troca o modo de condução do projeto atual. Rode com a sessão aberta **na raiz do repo do
projeto**; na raiz do vault, recuse e peça para abrir a sessão na pasta do projeto.

Uso: `/bkhar:mode` · `/bkhar:mode colaborativo` · `/bkhar:mode autonomo`

## Passo 1 — onde o projeto está

1. Leia o `.bks-profile.json`. `axes.mode` ausente vale `colaborativo`.
2. Rode e cole a saída inteira:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/readiness.py .
   ```

3. Sem argumento, ou com o modo que o projeto já tem: mostre o modo atual e a saída, e pare.

## Passo 2 — decidir

**Para `autonomo`:**

- Saída 1 (RECUSADA): não troque. Agrupe o que falta por nível e diga, para cada item, o comando que
  o resolve (`/bkhar:canonize`, `/bkhar:prd`, `/bkhar:plan`, `/bkhar:arch` — ou `/bkhar:arch --update`
  quando o nível Arquitetura aponta defasagem — ou responder à questão em aberto). Pare.
- Saída 0 (CONCEDIDA): mostre os avisos e o que muda no projeto:
  - `refine` e `spec` sem pergunta ao usuário; cada resposta presumida vai para
    `decisions/SUPOSICOES.md`;
  - portões do usuário: PRD, PLAN e ARCH (já aprovados), contratos da onda de desenho, entrega final;
  - `/bkhar:loop --wave N` passa a rodar as ondas do grafo.

  Em `rigor: producao`, diga que os contratos da onda de desenho continuam com o usuário.

**Para `colaborativo`:** a volta é sempre permitida. Se houver onda em curso em `outputs/run/`,
diga que ela termina a task em andamento e para.

Mostre o que vai ser escrito e espere o ok.

## Passo 3 — escrever

1. `axes.mode` no `.bks-profile.json`. Nenhuma outra chave muda.
2. ADR em `decisions/`, pelo template `ADR.md` (precedência: `{repo}/.bks/templates/`, senão
   `${BKS_VAULT}/workbench/templates/`, senão `${CLAUDE_PLUGIN_ROOT}/templates/`), numerado em
   sequência ao maior ADR do projeto. Contexto: o modo anterior e o motivo. Evidência: a saída do
   `readiness.py`.
3. Uma entrada no topo do `JOURNAL.md`: "Modo `{modo}`", com o número do ADR.

Não commite. Mostre `git status --short`.

## Regras

- A troca nunca é silenciosa: sem ADR, não houve troca.
- Não aprove documento para passar na prontidão. Mudar `status: rascunho` para `aprovado` é
  decisão do usuário, no comando que gerou o documento.
- Nenhum modo afrouxa os guardas, o RED antes do código, as 4 tentativas, a proibição de push na
  `main` e o `security` em área sensível.

Responda em português do Brasil.
