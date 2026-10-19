# Renderers de arquitetura

Registro extensivel. Cada arquivo declara um jeito de desenhar diagrama.

**Adicionar** e criar um arquivo. **Substituir** e trocar o conteúdo de um. Nenhuma skill do kit
tem renderer embutido — todas leem este diretório.

A notação — paleta, semantica de cor, convenção de linha — e a mesma para todos, e vive em
`skills/bks-arch/`. O renderer decide **como desenhar**; a notação decide **o que cada cor e cada
linha significam**.

## Disponiveis

| Renderer | Tipo | Notação | Logo de infra |
|---|---|---|---|
| [`mermaid`](mermaid.md) | nativo | completa | não |
| [`archify`](archify.md) | skill externa | completa | sim |
| [`c4`](c4.md) | template + mermaid | completa | não |
| [`togaf`](togaf.md) | template documental | parcial | não |

`mermaid` e o padrão: nativo, versionavel em texto, sem dependência.

## Formato

Ver [`_TEMPLATE.md`](_TEMPLATE.md).
