---
description: Retoma o trabalho. Na raiz do vault, monta o panorama de todos os projetos a partir dos STATUS.md. Dentro de um repositório de projeto, lê o STATUS.md dele.
---

Retome o trabalho. O que fazer depende de onde a sessão está aberta — decida primeiro.

## Passo 1 — descobrir o modo

Verifique o diretório de trabalho atual:

- Existe `STATUS.md` na raiz? → **modo projeto**
- Existe `repos/` com subpastas de categoria? → **modo panorama**
- Nenhum dos dois → pergunte ao usuário onde ele quer trabalhar e pare

Não adivinhe. Se `BKS_VAULT` estiver definido e o diretório atual for outro, diga qual dos dois
você está usando antes de continuar.

---

## Modo projeto

Leia, nesta ordem:

1. `STATUS.md` — onde o projeto está
2. `JOURNAL.md` — apenas a entrada mais recente, para saber o que mudou por último
3. `.bks-profile.json`, se existir — perfil e renderer

Responda em até seis linhas:

- **Onde parou** — a frase do `STATUS.md`, não um resumo dela
- **O que trava**, se algo trava
- **Próximo passo** — a ação concreta que o `STATUS.md` nomeia

Se o `STATUS.md` estiver desatualizado em relação ao `JOURNAL.md` ou ao git log, diga isso em uma
linha e ofereça atualizá-lo. Não atualize sozinho.

Se não houver `STATUS.md`, ofereça criá-lo a partir do template do kit.

---

## Modo panorama

Leia `workbench/profile.md` — quem é o usuário e como ele trabalha.

Percorra `repos/*/*/` e, para cada projeto, leia:

- `STATUS.md` — a frase de estado, a fase, e o que trava
- `JOURNAL.md` — a data da entrada mais recente

**Pule `repos/old/`.** É arquivo morto: projeto encerrado ou substituído, guardado porque apagar
seria irreversível, não porque ainda valha. Não entra no panorama, não entra na contagem, não
aparece como sugestão.

Não leia mais nada. Não abra `specs/`, `decisions/` nem código — o panorama é calculado desses
dois arquivos, e ler além disso custa tokens sem mudar a resposta.

Monte a visão, agrupada por estado e ordenada pela data mais recente primeiro:

```
{{vault}} · {{n}} projetos · {{n}} ativos

ATIVO
  {{projeto}}   {{categoria}}   {{frase de estado, truncada}}   {{data}}

PAUSADO
  {{projeto}}   {{categoria}}   {{frase de estado, truncada}}   {{data}}
```

Classifique como **ativo** o projeto cuja entrada mais recente do `JOURNAL.md` tem menos de 30
dias; **pausado** acima disso. Projeto sem `STATUS.md` entra numa terceira seção, `SEM STATUS`,
com a data do último commit.

Feche com uma linha de sugestão: qual projeto tem trabalho pronto para seguir, e qual está travado
esperando algo. Baseie-se no que trava — projeto bloqueado por decisão externa não é candidato.

Cite o caminho do repositório (`${BKS_VAULT}/repos/{categoria}/{projeto}`) e termine dizendo que,
para trabalhar num projeto, o usuário abre uma sessão nova na pasta dele. Não ofereça continuar o
trabalho do projeto a partir da raiz: os comandos de projeto escrevem no repositório onde a sessão
está aberta, e rodar da raiz gravaria no lugar errado.

---

## Em ambos os modos

Responda em português do Brasil. Não narre o que você leu, não liste os arquivos abertos, não
recapitule a estrutura do vault. A resposta é o estado, não o relatório de como você o obteve.
