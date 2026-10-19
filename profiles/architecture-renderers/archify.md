---
renderer: archify
tipo: skill-externa
skill: archify
licença: MIT
padrão: false
fallback: mermaid
---

# Archify

Skill externa que gera HTML interativo — pan, zoom, foco, navegação por camadas, export para PNG,
SVG e WebM.

## Dependencia

Não vem no kit. E skill de terceiro, com motor de renderização próprio, e evolui por conta
própria. Copia-la aqui criaria um fork que precisaria de manutenção.

**Se não estiver instalada**, avise e caia no `mermaid`. Não falhe.

## Quando e a escolha certa

- diagrama de infraestrutura com logo e posicionamento controlado
- entrega para apresentação ou consulta, não para diff
- sistema grande, onde navegar por camadas ajuda mais que ver tudo de uma vez
- reconstrução de arquitetura de legado, onde explorar importa

## O que suporta da notação BKS

| Elemento | Suporta |
|---|---|
| cor por tipo de no | sim |
| linha continua e pontilhada | sim |
| agrupamento por fronteira | sim |
| logo de empresa | sim |
| controle fino de posição | sim |
| tema claro e escuro | sim |

## Como aplicar a notação

O `archify` aceita cor por no. Use os tokens de `skills/bks-arch/references/paleta.md` no lugar do padrão
dele — sem isso, o diagrama sai no estilo da skill, não no seu.

Ícones de infraestrutura: use os SVG genéricos de `skills/bks-arch/icons/`. O kit não distribui
marca de terceiro.

## Limite honesto

Saída em HTML, não em texto. Um diagrama `archify` não se revisa em diff — versione o arquivo de
entrada, não só o HTML gerado.
