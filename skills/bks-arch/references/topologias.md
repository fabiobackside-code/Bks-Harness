# Topologias — qual diagrama para qual pergunta

## Arquitetura

**Responde:** do que o sistema e feito, e como as peças se falam.

Nos são peças executáveis ou armazenamento: serviço, banco, fila, gateway, biblioteca. Arestas são
dependências — quem chama quem.

**Não mostra** ordem temporal. Se a pergunta e "o que acontece primeiro", o diagrama e outro.

Agrupe por fronteira real: processo, container, rede, domínio. Agrupamento por semelhanca visual
engana.

## Sequencia

**Responde:** em que ordem as coisas acontecem, entre quais atores.

Participantes na horizontal, tempo descendo. Mensagem sincrona com linha continua e retorno
explicito; assincrona com pontilhada e sem espera.

**Marque o que pode falhar.** Uma sequência que só mostra o caminho feliz esconde justamente o que
precisa ser projetado.

Limite: cerca de sete participantes. Acima disso, fatie por cenário.

## Fluxo de dados

**Responde:** por onde o dado passa, o que o transforma, onde repousa.

Nos são transformações e repositórios. Arestas são o dado em movimento — rotule com **o que**
trafega, não com o verbo.

**Marque a fronteira de dado sensivel.** Onde dado pessoal ou regulado atravessa um limite, o
diagrama mostra. E o que torna o diagrama util numa revisão de conformidade.

## Ciclo de vida

**Responde:** que estados uma entidade atravessa, e o que dispara cada transição.

Nos são estados; arestas são eventos. Todo estado precisa de saída, menos o final. Estado sem
saída que não e final e bug de modelagem — mostre.

**Inclua o caminho de erro.** Estado de falha, retentativa, expiração. São os que causam incidente.

## Workflow

**Responde:** quem faz o que, e onde se decide.

Raias por ator ou sistema. Losango para decisão, com as saidas rotuladas.

**Marque onde espera.** Aprovação humana, lote noturno, timeout — o tempo de espera e o que
explica por que o processo demora.

---

## Erros que aparecem sempre

**Um diagrama para duas perguntas.** Arquitetura com numeração de ordem tenta ser sequência
também, e falha nas duas.

**Tudo no mesmo diagrama.** Completo não e util. O que não ajuda a responder a pergunta sai.

**Fronteira ausente.** Sem mostrar onde termina o que você controla, ninguém sabe onde estão os
riscos.

**Aresta sem rótulo.** Uma seta sem rótulo diz que existe relação, não qual. Rotule com protocolo,
dado ou evento.
