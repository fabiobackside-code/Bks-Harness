---
description: Biblioteca do projeto — /bkhar:library [build|stale|export]. Gera o catálogo e o dashboard de docs/library/, aponta a arquitetura defasada e exporta a biblioteca para knowledge/ do vault.
---

A biblioteca é a wiki do projeto: cataloga canônicos, arquitetura, contratos, specs, decisões,
ilustrações e histórico onde eles estão, e os apresenta num dashboard estático. Rode com a sessão
aberta **na raiz do repositório do projeto**; na raiz do vault, recuse.

Uso: `/bkhar:library` (igual a `build`) · `/bkhar:library stale` · `/bkhar:library export`

## `build`

Rode e cole a saída:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py index .
python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py build .
python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py stale .
```

Diga onde abrir o dashboard (`docs/library/site/index.html`) e, se o `stale` saiu 1, quais modelos
estão defasados e que o `/bkhar:arch --update` os refaz. O catálogo e o dashboard são versionados:
entram no commit junto com o que os mudou.

## `stale`

Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py stale .` e cole a saída. Não corrija nada
daqui: quem refaz modelo é o `/bkhar:arch --update`.

## `export`

Leva a biblioteca para o vault. Escreve fora do repositório, por isso só roda quando pedido.

1. Confira `library.export` no `.bks-profile.json`. Sem ele, diga que a exportação não está
   configurada e mostre a chave (`"library": {"export": "knowledge/wiki/projetos/{projeto}"}`).
   Não grave a chave sem o ok.
2. Confira `BKS_VAULT`. Sem ele, peça o caminho do vault.
3. Mostre o destino (`${BKS_VAULT}/<library.export>`) e espere o ok.
4. Rode e cole a saída:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py export .
   ```

   Saída 1: alguma página tem termo da lista de bloqueio do harvest ou dado pessoal ou segredo, e
   nada foi escrito. Diga qual página e o achado; corrigir é editar o documento de origem, nunca
   contornar o filtro. Saída 2: falta configuração.
5. Saída 0: o script escreveu uma página por documento com o frontmatter da knowledge, o `index.md`
   do projeto no destino, a linha do projeto na seção `## Projetos` de `knowledge/wiki/index.md` e a
   entrada em `knowledge/wiki/log.md`. Página que saiu do catálogo foi removida do destino. Liste
   em até cinco linhas o que mudou no vault. Não commite o vault.

Responda em português do Brasil.
