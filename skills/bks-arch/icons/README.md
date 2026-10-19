# Ícones

SVG genéricos para diagramas de infraestrutura. Sem marca de terceiro.

O kit não distribui logo oficial de AWS, Azure, Kafka ou equivalente: são marcas registradas, com
licença de uso própria, e redistribui-las num pacote MIT criaria um problema que não e nosso.

Estes ícones representam a **função** — banco, fila, container, balanceador, gateway — e seguem a
paleta de `../references/paleta.md`.

Nos seus próprios diagramas, use o logo que quiser. A restrição vale para o que o kit distribui.

## Convenção

Um arquivo por função, nomeado pelo que representa, não pelo produto:

```
database.svg        queue.svg          container.svg
cache.svg           topic.svg          load-balancer.svg
object-storage.svg  gateway.svg        scheduler.svg
```

`database.svg`, não `postgres.svg`. O icone diz o papel; o rótulo do no diz o produto.
