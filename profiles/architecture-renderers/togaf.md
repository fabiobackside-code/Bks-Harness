---
renderer: togaf
tipo: template-documental
base: mermaid
padrão: false
fallback: mermaid
---

# TOGAF

Template de arquitetura corporativa. Documento estruturado nas quatro camadas do TOGAF, com
diagramas de apoio.

## Quando e a escolha certa

- a entrega é documento de arquitetura corporativa, não diagrama de sistema
- há exigência formal de método — cliente, órgão regulador, área de arquitetura
- o escopo atravessa vários sistemas e envolve processo de negócio

Para um sistema só, `c4` entrega mais com menos cerimônia.

## Camadas

| Camada | Cobre |
|---|---|
| Negocio | processos, atores, capacidades, serviços de negócio |
| Dados | entidades, fluxos, propriedade, ciclo de vida |
| Aplicação | sistemas, integrações, contratos |
| Tecnologia | plataforma, rede, ambientes |

Cada camada gera uma seção e ao menos um diagrama.

## Como aplicar a notação

Os diagramas de apoio saem em Mermaid, com a paleta BKS. A camada de Tecnologia se beneficia de
`archify` quando há logo de infraestrutura.

## Limite honesto

TOGAF é pesado. Aplicado a um projeto pequeno, produz documento que ninguém lê. Confirme que há
exigência real de método antes de escolher — não escolha por parecer mais completo.
