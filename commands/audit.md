---
description: "Auditoria de deriva de coerência. No kit, registro de regras e parâmetros entre guia e sensor; no projeto, cópia dos guardas, CI e STATUS; com --deep, contradição de sentido entre guias pelo quality. Só lê os guias."
---

Procura deriva: guia que deixou de bater com o sensor, cópia que ficou para trás, estado que não
descreve mais o repositório. Rode na raiz do kit ou do projeto. Só lê: quem corrige é o usuário, ou
o comando que a saída indica.

## Passo 1 — a parte computacional

Rode e cole a saída:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/audit.py .
```

O script detecta o contexto. No kit (tem `rules.json` e `hooks/hooks.json`), confere o registro de
regras, os parâmetros repetidos entre guia e sensor e o `docs/regras.md`. No projeto, confere se os
guardas estão em `.bkhar/guards/` e iguais aos do kit, se o CI do `git_host` existe e se o
`STATUS.md` está atrás do `JOURNAL.md` ou do git.

Cada achado vem com a linha `destrava:`. Repita-a ao usuário como está; não execute sozinho o que
ela manda. Contradição registrada e ainda não decidida também sai aqui, como `[contradicao]`.

## Passo 2 — `--deep`, só quando o usuário pede

`/bkhar:audit --deep` roda os oito temas; `/bkhar:audit --deep <tema>` roda um. Gasta crédito:
diga quantos temas vão rodar antes de começar. Os temas saem de
`python ${CLAUDE_PLUGIN_ROOT}/scripts/audit.py . --dossier`.

Para cada tema:

1. Gere o dossiê num arquivo temporário:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/audit.py . --dossier <tema> > <temp>/dossie-<tema>.md`
2. Invoque o `quality` com o caminho do dossiê. Ele procura só contradição de sentido entre guias e
   devolve, para cada uma, a regra que deveria valer e os dois `arquivo:linha` com a citação.
3. Grave cada contradição como proposta, sem corrigir o guia:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py propose . --type contradiction \
  --rule "<a regra que deveria valer>" --evidence "<arquivo:linha> x <arquivo:linha>" \
  --origin "audit --deep <tema> · quality"
```

O usuário decide cada uma. Se ele corrigir o guia, rode `learning.py resolve . --file <proposta>
--fix "<o que mudou>"`. Se rejeitar, rode `learning.py reject . --file <proposta> --reason
"<motivo>"`. As duas levam a proposta para `archive/proposals/`. A auditoria fica sem contradição
aberta quando o `inbox/proposals/` não tem mais nenhuma do tipo `contradicao`.

## Regras

**Não corrija durante a auditoria.** O comando aponta; a correção é um passo separado, com o ok do
usuário.

**Saída 0 é "sem deriva", não "tudo certo".** A parte computacional só vê o que o registro declara.

Responda em português do Brasil, em até dez linhas além da saída colada.
