# Notação BKS — o que vira no, e o que fica de fora

A paleta diz que cor usar. Este documento diz **o que desenhar**.

## O que vira no

Vira no o que tem existência própria e pode falhar sozinho:

- processo que roda: serviço, worker, função
- coisa que guarda estado: banco, cache, filesystem, blob
- coisa que transporta: fila, topico, barramento
- fronteira de entrada: gateway, ingress, canal
- artefato consumido por outro: biblioteca, SDK

**Não vira no:** classe, método, tabela, arquivo de configuração, framework. São detalhes de
implementação — vivem no código, não no diagrama de arquitetura.

Regra prática: se você não consegue reiniciar sozinho, provavelmente não e um no.

## Fronteiras

Toda arquitetura tem ao menos uma fronteira: onde termina o que você controla.

| Fronteira | Mostra |
|---|---|
| confiança | onde a entrada deixa de ser confiavel |
| processo | o que roda junto e cai junto |
| rede | o que atravessa a rede — e paga a latência |
| domínio | onde a linguagem do negócio muda |

Um diagrama sem fronteira não permite avaliar risco: tudo parece igualmente seguro.

## Rotulos

**No:** o nome real, como aparece no repositório ou na infraestrutura. Não "Servico de Pedidos"
quando o serviço se chama `orders-api`. Quem le o diagrama vai procurar o nome que você escreveu.

**Aresta:** o que trafega ou o protocolo. `POST /orders`, `pedido.criado`, `SELECT`. Não "envia
dados" — toda aresta envia dados.

**Agrupamento:** o nome da fronteira. `Cluster produção`, `Rede interna`, `Contexto de cobranca`.

## Direção

A seta aponta para quem **recebe a chamada**, não para onde o dado vai.

Um serviço que le do banco aponta para o banco, ainda que o dado venha na direção contraria. O que
o diagrama mostra e a dependência: quem precisa de quem para funcionar.

Em fluxo de dados a convenção se inverte — ali a seta segue o dado. Por isso os dois não se
misturam no mesmo desenho.

## Densidade

| Nos | O que fazer |
|---|---|
| até 12 | um diagrama |
| 13 a 25 | agrupe por fronteira, considere dois níveis |
| acima de 25 | fatie por contexto, ou use C4 |

Diagrama que precisa de zoom para ser lido já falhou como diagrama.

## O que fica de fora

- o que não ajuda a responder a pergunta do diagrama
- infraestrutura de suporte que existe em todo lugar — log, metrica, DNS — a menos que a pergunta
  seja sobre observabilidade
- variantes de ambiente, quando a topologia e a mesma: desenhe uma e diga que vale para todas
- o que ainda não existe, misturado ao que existe. Se precisa mostrar o futuro, faça dois
  diagramas — atual e alvo
