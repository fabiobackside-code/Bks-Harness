---
description: "Retrospectiva do aprendizado — o usuário promove cada proposta candidata a regra do projeto, do vault ou do kit, ou a rejeita com motivo. Só o usuário promove."
---

Revisa as propostas candidatas do projeto atual e decide, uma a uma, o que vira regra. Rode na
raiz do repo do projeto.

## Passo 1 — o que está pendente

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py list .
```

Sem candidata, diga isso e pare. Para cada uma, mostre a regra, a evidência e a origem, numeradas.
Junte as que dizem a mesma coisa e diga quais duplicam regra já em `brain/engineering/regras/`.

## Passo 2 — o usuário decide

Para cada proposta, pergunte o destino e espere a resposta:

| Destino | Quando | Onde vai |
|---|---|---|
| `projeto` | vale só para este repositório | `brain/engineering/regras/`, `status: promovida` |
| `vault` | vale para todo projeto da mesma stack | `${BKS_VAULT}/workbench/regras/` |
| `kit` | muda como o harness trabalha | `inbox/proposals/` do harness, `status: para-eval` |
| rejeitar | errada, duplicada ou suspeita | `archive/proposals/` do projeto, com o motivo |

O Gerente não escolhe o destino. Proposta sem resposta continua candidata.

## Passo 3 — aplicar

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py promote . --file <proposta> --scope project|vault|kit
python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py reject . --file <proposta> --reason "<motivo>"
```

O script recusa levar ao vault ou ao kit proposta com dado pessoal ou segredo.

Rodando no próprio kit, as propostas com `status: para-eval` em `inbox/proposals/` esperam a última
decisão: a qual skill a regra vai. Pergunte, e com a resposta:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/learning.py apply --file <proposta> --skill <nome>
```

Ele acrescenta a regra à seção `## Histórico de regras` do `SKILL.md`, com a proposta de origem e a
evidência, e arquiva a proposta como `aplicada`, com `eval: pendente`. Escrever a regra no ponto
certo do guia, além do histórico, é edição de skill: mostre o trecho e espere o ok.

## Regras

- **Só o usuário promove.** Regra promovida passa a valer no modo `autonomous` e é lida pelos agentes.
- **Regra do kit só fica com medida.** Ela espera o `claude plugin eval` mostrar delta entre o braço
  `with` e o `without`; sem delta, sai do guia e do histórico. A proposta aplicada guarda
  `eval: pendente` até a medida.
- Regra promovida no projeto libera o aviso de "Aprendizado" do `readiness.py`.
- Não commite. Mostre `git status --short` e uma linha por destino.

Responda em português do Brasil.
