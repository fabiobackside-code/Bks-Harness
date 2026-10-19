---
name: bks-arch
description: >
  Notação BKS para diagramas de arquitetura: paleta derivada da marca, semantica de cor por
  tipo de no (backend, storage, broker, canal de acesso, componente), convenção de linha
  para fluxo sincrono e assincrono, e escolha do tipo de diagrama. Emite para Mermaid,
  archify, C4 ou TOGAF — a notação e a mesma, o motor e plugavel. Use ao desenhar
  arquitetura, topologia, fluxo de dados, sequência, ciclo de vida ou diagrama de
  infraestrutura. Trigger: diagrama de arquitetura, topologia, C4, TOGAF, mermaid, archify,
  desenhar o sistema, notação de diagrama, paleta de diagrama.
---

# BKS-ARCH — notação de arquitetura

Esta skill e a **notação**, não o motor. Ela decide o que cada cor e cada linha significam; o
renderer decide como desenhar.

Por isso um diagrama BKS parece um diagrama BKS em qualquer motor — e trocar de motor não muda o
que o leitor entende.

## Primeiro: qual diagrama

| Se a pergunta e | O diagrama e |
|---|---|
| do que o sistema e feito e como as peças se falam | **arquitetura** |
| em que ordem as coisas acontecem entre atores | **sequência** |
| por onde o dado passa e onde repousa | **fluxo de dados** |
| que estados uma entidade atravessa | **ciclo de vida** |
| quem faz o que, e onde decide | **workflow** |

Escolher errado custa mais que desenhar mal. Um diagrama de arquitetura respondendo pergunta de
sequência vira caixa com seta demais.

Detalhes em `references/topologias.md`.

## Depois: qual motor

Le `.bks-profile.json` do projeto, campo `axes.architecture_renderer`. Sem o arquivo, pergunte.

| Motor | Quando |
|---|---|
| `mermaid` | padrão — vive no repositório, revisa em diff, sem dependência |
| `archify` | infraestrutura com logo, entrega para apresentação, sistema grande de navegar |
| `c4` | públicos diferentes precisam de níveis de zoom diferentes |
| `togaf` | exigência formal de arquitetura corporativa |

O registro está em `profiles/architecture-renderers/`. Cada motor tem seu arquivo com o que
suporta e o que não suporta.

Se o motor escolhido for skill externa e ela não estiver instalada, **avise e caia no mermaid**.
Não falhe.

## A notação

Cor por papel, nunca por estetica:

| Papel | Cor | Para |
|---|---|---|
| backend | azul `#336698` | serviço, API, worker, use case |
| storage | verde `#4A7C63` | banco, blob, filesystem, cache |
| broker | laranja `#B5713C` | Kafka, RabbitMQ, fila, topico |
| acesso | vermelho `#9E4B4B` | gateway, ingress, canal externo, usuário |
| componente | amarelo `#B39038` | biblioteca, SDK, DLL |
| externo | cinza `#6B7280` | terceiro, fora da fronteira |

Linha continua = sincrono, quem chama espera. Linha pontilhada = assincrono.

Tokens completos, contraste e tema escuro em `references/paleta.md`.

## Referencias

| Arquivo | Quando abrir |
|---|---|
| `references/paleta.md` | ao atribuir cor — tokens, contraste, tema |
| `references/topologias.md` | ao escolher o tipo de diagrama |
| `references/notacao-bks.md` | ao decidir o que vira no, e o que fica de fora |
| `references/emit-mermaid.md` | ao gerar em Mermaid |
| `references/emit-archify.md` | ao gerar em archify |

## Regras

**Um diagrama responde uma pergunta.** Se precisa de duas, são dois diagramas.

**Cor nunca e a única informação.** Todo no tem rótulo. O diagrama sobrevive a impressão em preto
e branco.

**Sem cor viva.** A paleta e dessaturada de propósito. Trinta nos em cor saturada cansam antes de
serem lidos.

**O que não ajuda a responder a pergunta sai.** Diagrama completo não e diagrama util.
