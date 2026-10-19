---
name: bks-standards
description: >
  Padrões de engenharia BKS: premissas de codificação, regras de dependência .NET e Go,
  Object Calisthenics, politica de documentação e comentario, SEDA e TCP sockets,
  e o checklist de revisão crítica. Use quando precisar decidir COMO construir —
  camadas, dependências, imutabilidade, tratamento de erro, comentario, ou quando
  revisar código contra os padrões da casa. Trigger: padrão BKS, premissa de
  codificação, regra de dependência, calisthenics, comentario no código, SEDA,
  socket TCP, checklist de revisão, padrão Go, erro idiomático em Go.
---

# BKS-STANDARDS — padrões de engenharia

Estes padrões governam **como** o código e gerado, em qualquer projeto. São método, não decisão de
um produto — por isso vivem no kit e não no vault.

Um projeto pode sobrescrever qualquer um deles em `brain/engineering/`. Onde houver conflito, o
projeto vence.

## Referencias

Abra a que a tarefa exige, não todas.

| Referencia | Quando abrir |
|---|---|
| `references/bks-premises.md` | antes de gerar código novo — e a fonte de verdade do método |
| `references/dotnet-standards.md` | projeto .NET: camadas, dependências, composition root |
| `references/go-standards.md` | projeto Go: onde a linguagem contradiz o padrão-base |
| `references/go-review-checklist.md` | ao revisar código Go — erro, concorrência, interface |
| `references/calisthenics.md` | ao decidir forma de classe e método |
| `references/documentacao.md` | ao escrever comentario, README ou ARCHITECTURE |
| `references/seda-tcp.md` | pipeline por estagios, socket, backpressure |
| `references/checklist-revisao-critica.md` | ao revisar código de area sensivel |

## As três que não se negociam

**Domínio agnostico.** `Domain/Core/Common` usa apenas `System.*`. Sem ORM, sem driver, sem
cliente de mensageria. Precisa de infraestrutura no domínio? A dependência entra invertida, por uma
porta.

**Orquestração explicita.** Sem MediatR, sem dispatcher. O use case e chamado direto pela porta, e
os passos ficam ordenados no pipeline. Há um guarda que recusa a escrita — ver `hooks/`.

**Erro de negócio não e exceção.** Use case devolve resultado tipado. Exceção fica para o que e
excepcional de verdade.
