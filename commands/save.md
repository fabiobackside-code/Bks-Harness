---
description: Fecha a sessão. Roteia decisões para decisions/, specs para specs/, atualiza o STATUS.md e acrescenta o marco no JOURNAL.md.
---

**Passo 0 — delegar.** Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/maestri_config.py delegate . --command save`.
Com `terminal <nome>`, siga a seção "Delegação de comando" da skill `bks-team` e não execute
os passos abaixo neste terminal. Com `local: <motivo>`, siga normalmente.

Feche a sessão registrando o que ela produziu. Rode com a sessão aberta na raiz do repositório do
projeto.

Se não houver `STATUS.md` na raiz, pergunte se é para criar a partir do template antes de seguir.

## O que vai para onde

| O que a sessão produziu | Destino |
|---|---|
| Decisão de arquitetura, stack ou contrato | `decisions/ADR-NNN.md` |
| Spec nova ou alterada | `specs/features/`, `specs/tests/`, `specs/tasks/` |
| Onde o projeto parou | `STATUS.md` — reescrito |
| Marco da sessão | `JOURNAL.md` — acrescentado no topo |
| Aprendizados que os agentes devolveram no rito | `JOURNAL.md`, na entrada da sessão, sob `### Aprendizados` |
| Defeito detectado e resolvido, com evidência | `LEARNINGS.md` — um caso por defeito, no topo |
| Canônico defasado pela spec ou pelo ADR | `STATUS.md` — seção do que trava, para o `/bkhar:canonize` |
| Modelo da arquitetura defasado | `STATUS.md` — seção do que trava, para o `/bkhar:arch --update` |
| Catálogo e dashboard da biblioteca | `docs/library/LIBRARY.md` e `docs/library/site/index.html` — regerados |
| Entregável gerado | `outputs/` |
| Conhecimento de domínio que surgiu | `brain/domain/` |
| Padrão técnico que se firmou | `brain/engineering/` |

Decisão sobre o **processo de trabalho** — não sobre este projeto — vai para
`${BKS_VAULT}/workbench/decisions/`. É raro; na dúvida, é do projeto.

## Regras

**Registre só o que foi verificado.** Se um teste rodou, cole a linha que comprova. Se não rodou,
escreva que não rodou. Nunca escreva que algo funciona porque parecia funcionar.

**O `STATUS.md` é reescrito, não acrescentado.** Ele diz onde o projeto está agora. Estado antigo
não se acumula ali — vai para o `JOURNAL.md`.

**O `JOURNAL.md` é acrescentado, nunca reescrito.** Entrada nova no topo, com a data em ISO.
Sessão que não produziu nada não vira entrada — não invente marco para justificar a sessão.

**`LEARNINGS.md` só com evidência.** Caso sem o teste que falhou ou o commit da correção não
entra: caso sem evidência vira suspeita, e suspeita não é aprendizado. Se o `LEARNINGS.md` não
existir, crie a partir do template `templates/project-skeleton/LEARNINGS.md` antes do primeiro caso.

**ADR só para decisão fechada.** Discussão em aberto fica no `STATUS.md`, na seção do que trava.
Um ADR que registra hesitação polui o log de decisões.

**Spec aprovada envelhece o canônico.** O `docs/canonical/CONTEXT.md` foi consolidado antes da
spec existir; decisão fechada depois dele não chega lá sozinha. O `/bkhar:save` acusa a defasagem, não
a corrige — quem reconsolida é o `/bkhar:canonize`, em sessão que possa responder às perguntas que ele
levanta.

## Passos

1. **Levante o que mudou.** `git status` e `git diff --stat`, mais o que a sessão decidiu sem
   tocar em arquivo. Se não houver repositório git, pergunte ao usuário o que considerar.
   Se existir `outputs/run/handoff/save.md`, este save foi delegado: o que a sessão decidiu está
   nele, escrito pelo `manager`, e vale como a conversa que este terminal não viu.

2. **Classifique** cada item pela tabela acima. Item que não se encaixa: pergunte, não invente
   destino.

3. **Escreva as decisões e as specs.** ADR numerado em sequência a partir do maior existente.
   Spec no formato do kit. O `STATUS.md` ainda não — ele fecha no passo 5, depois da verificação
   do canônico.

4. **Verifique o canônico.** Só se existir `docs/canonical/CONTEXT.md` — sem ele o projeto não
   usa o fluxo canônico e não há nada a alertar. Rode a verificação **depois** de gravar as specs
   e os ADRs do passo 3, senão o que esta sessão acabou de decidir não entra na conta:

   ```
   find specs decisions -name '*.md' -newer docs/canonical/CONTEXT.md
   ```

   Lista vazia: siga em frente sem comentar. Lista com arquivos: o canônico está defasado — leve
   para o passo 5 uma linha nomeando a versão atual do canônico e os arquivos mais novos que ele.

   Não rode `/bkhar:canonize` e não escreva nota de síntese em `docs/input/` para compensar — o
   `/bkhar:canonize` lê `specs/` e `decisions/` direto, e nota intermediária só afasta a afirmação da
   fonte.

   **A arquitetura e a biblioteca.** Só se existir `docs/library/`. Rode e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py stale .
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py index .
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py build .
   ```

   Saída 1 do `stale`: leve para o passo 5 os modelos defasados e o motivo. Avisa, não bloqueia; não
   rode o `/bkhar:arch` daqui. O `index` e o `build` regeram o catálogo e o dashboard, que entram no
   commit da sessão.

5. **Reescreva o `STATUS.md` por inteiro.** Se o passo 4 acusou defasagem, a linha entra na seção
   do que trava: o `/bkhar:canonize` destrava o canônico; o `/bkhar:arch --update`, a arquitetura.

6. **Acrescente ao `JOURNAL.md`** uma entrada: data, título curto do marco, duas a quatro linhas
   do que mudou e do que isso libera ou trava. Se algum rito da sessão devolveu aprendizados, eles
   entram na mesma entrada, sob `### Aprendizados`.

   Os casos de defeito resolvido que o `quality` devolveu vão para o `LEARNINGS.md`, um por caso,
   no formato do template. Caso sem evidência fica de fora e é dito em uma linha.

7. **Meça o consumo da sessão.** Siga `references/medicao-consumo.md`: ledger, painel
   `custo-tokens.md` e a tabela na entrada do `JOURNAL.md`. Se o script não existir, uma linha
   dizendo que pulou — a medição nunca bloqueia o `/bkhar:save`.

8. **Leve os candidatos ao vault.** Com `BKS_VAULT` definido, rode e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py export .
   ```

   Ele copia as propostas candidatas de `inbox/proposals/` para `${BKS_VAULT}/inbox/proposals/`,
   com o projeto no nome, e recusa a que tiver dado pessoal ou segredo. Recusada: diga qual e por
   quê, em uma linha; corrigir é editar a proposta, nunca contornar o filtro. Sem vault, pule.

9. **Lembre do harvest.** Com `BKS_VAULT` definido:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/harvest.py stale .
   ```

   Saída 1: anote no `STATUS.md`, na seção do que trava, que o projeto tem ADR ou caso mais novo que
   o último `/bkhar:harvest`. Não rode o harvest daqui.

10. **Regere a nota de status.** Depois do `STATUS.md` reescrito, rode e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .
   ```

   Ele grava `outputs/run/status-canvas.md` e, dentro do Maestri, a nota `status` e o
   `floor status`. Fora do Maestri, só o arquivo. A nota é espelho: nunca edite à mão.

11. **Confirme em até cinco linhas** o que foi gravado e onde. Uma linha por arquivo. Não repita o
   conteúdo que acabou de escrever. Se o canônico estiver defasado, feche com a instrução de rodar
   `/bkhar:canonize`.

Responda em português do Brasil.
