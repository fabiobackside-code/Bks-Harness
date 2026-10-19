---
renderer: {{nome}}
tipo: {{nativo | skill-externa | template | template-documental}}
skill: {{nome da skill, se externa}}
licença: {{se externa}}
padrão: false
fallback: mermaid
---

# {{Nome}}

{{O que este renderer produz, em duas linhas.}}

## Dependencia

{{Se for skill externa: o que precisa estar instalado, e o que fazer quando não está. Se for
nativo ou template: diga que não há dependência.}}

## Quando e a escolha certa

{{Três a cinco situações concretas. Não "quando você quer um diagrama bonito" — quando o formato
resolve um problema que os outros não resolvem.}}

## O que suporta da notação BKS

| Elemento | Suporta |
|---|---|
| cor por tipo de no | |
| linha continua e pontilhada | |
| agrupamento por fronteira | |
| logo de empresa | |
| controle fino de posição | |

## Como aplicar a notação

{{Como os tokens de skills/bks-arch/paleta.md entram neste renderer. Código, não descrição.}}

## Limite honesto

{{O que este renderer não faz bem. Sem isso, quem escolhe descobre tarde.}}
