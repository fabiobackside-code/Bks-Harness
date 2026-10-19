# Emitir em archify

## Antes de começar

O `archify` e skill externa e não vem no kit. Verifique se está instalada.

**Se não estiver:** avise em uma linha e gere em Mermaid. Não falhe, e não peça ao usuário para
instalar no meio do trabalho.

## Aplicar a paleta BKS

O `archify` tem estilo próprio. Sem sobrepor as cores, o diagrama sai no estilo dele — não no seu.

Defina a cor de cada no pelo papel semantico:

| Papel | fill | stroke | color |
|---|---|---|---|
| backend | `#336698` | `#1F4266` | `#FFFFFF` |
| storage | `#4A7C63` | `#2E5140` | `#FFFFFF` |
| broker | `#B5713C` | `#8A5228` | `#FFFFFF` |
| acesso | `#9E4B4B` | `#733535` | `#FFFFFF` |
| componente | `#B39038` | `#8A6E26` | `#1A1A1A` |
| externo | `#6B7280` | `#4B5563` | `#FFFFFF` |
| destaque | `#98CBFF` | `#336698` | `#1A1A1A` |

Tema escuro: os tokens de fundo e texto estão em `paleta.md`. O `archify` suporta os dois temas —
verifique o contraste nos dois antes de entregar.

## Linhas

Continua para sincrono, tracejada para assincrono. A convenção e a mesma do Mermaid; muda só a
sintaxe do motor.

## Ícones de infraestrutura

Use os SVG genéricos de `../icons/`. O kit não distribui marca de terceiro — logo oficial de AWS,
Azure ou Kafka tem licença de uso de marca, e redistribuir num pacote MIT criaria um problema que
não e nosso.

Nos seus próprios diagramas, use o que quiser. A restrição vale para o que o kit distribui.

## Versionamento

O `archify` gera HTML, e um HTML de centenas de kilobytes não se revisa em diff.

**Versione o arquivo de entrada** — o JSON ou a descrição que gerou o diagrama. O HTML e saída,
como binario compilado: vai para `outputs/`, e o `.gitignore` do projeto decide se acompanha o
repositório.

## Quando vale a pena

- infraestrutura com logo e posicionamento controlado
- entrega para apresentação ou consulta, não para revisão em diff
- sistema grande, onde navegar por camadas ajuda mais que ver tudo de uma vez
- reconstrução de arquitetura de legado, onde explorar importa mais que versionar

Fora disso, Mermaid entrega o mesmo com menos dependência.
