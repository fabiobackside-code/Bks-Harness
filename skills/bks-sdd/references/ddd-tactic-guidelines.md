# APLICANDO-DDD-GUIDELINES

> **Versão:** 1.0  
> **Escopo:** Tático — como modelar o domínio dentro de um Contexto Delimitado  
> **Paradigma:** Agnóstico de linguagem / framework  
> **Temperatura de decisão:** 0.02 — regras prescritivas, não opinativas

---

## PROPÓSITO DESTE ARQUIVO

Este guideline instrui agentes de IA e desenvolvedores sobre como aplicar os blocos táticos do Domain-Driven Design dentro de um Bounded Context já identificado. Ele NÃO cobre identificação de contextos (ver `Identificando-Contextos-Delimitados-GUIDELINES.md`) nem estrutura de projeto (ver `Arquitetura-Hexagonal-GUIDELINES.md`).

---

## PRINCÍPIO FUNDAMENTAL

> **O domínio é o centro. Tudo protege o domínio. O domínio não conhece infraestrutura.**

A camada de domínio NUNCA importa frameworks, ORMs, bibliotecas de HTTP, loggers concretos, ou qualquer detalhe técnico. Ela é puro comportamento e regras de negócio.

---

## BLOCO 1 — ENTIDADES (Entities)

### Definição
Uma **Entidade** é um objeto definido por sua **identidade**, não por seus atributos. Dois objetos com mesmos atributos mas IDs diferentes são entidades distintas.

### Regras Obrigatórias
- SEMPRE ter um identificador único e imutável (ID).
- O ID deve ser gerado NO DOMÍNIO ou passado na criação — nunca gerado pela infraestrutura de fora.
- Entidades devem ENCAPSULAR seus invariantes — nunca expor setters públicos sem validação.
- Toda mudança de estado deve ocorrer via métodos com nomes de domínio (linguagem ubíqua).
- Entidades são MUTÁVEIS ao longo do tempo, mas sua identidade é permanente.

### Padrão de Implementação (agnóstico)

```
Entity<TId>
  - Id: TId (readonly, set only on construction)
  - Métodos de comportamento com nomes do negócio
  - Validações inline que lançam DomainException ao ser violadas
  - Sem getters/setters para estado interno sensível

Exemplo de nomes corretos (linguagem ubíqua):
  pedido.Confirmar()       ✅
  pedido.SetStatus("confirmed")  ❌

  conta.Creditar(valor)    ✅
  conta.Saldo += valor     ❌
```

### Anti-Padrões — NUNCA FAÇA
- `public void SetNome(string nome) { Nome = nome; }` — setter anêmico sem validação.
- Entidade que chama repositório ou serviço de infraestrutura.
- Entidade com lógica de persistência (EF annotations que influenciam comportamento).
- ID gerado pelo banco ANTES de a entidade existir no domínio.

---

## BLOCO 2 — VALUE OBJECTS (Objetos de Valor)

### Definição
Um **Value Object** é definido completamente por seus **atributos**. Não tem identidade própria. Dois VOs com mesmos atributos são iguais.

### Regras Obrigatórias
- SEMPRE imutável. Nenhum método muda estado; operações retornam novo VO.
- Implementar igualdade por valor (não por referência).
- Encapsular validação de formato/domínio no próprio VO.
- Substituir primitivos que carregam regras de negócio (Primitive Obsession → Value Object).

### Quando Criar um Value Object
```
Critério de decisão:
  - "Esse dado tem regras de formatação/validação?" → VO
  - "Esse dado representa um conceito do domínio?" → VO
  - "Dois instâncias com mesmo valor são intercambiáveis?" → VO

Exemplos:
  Email, CPF, CNPJ, Dinheiro, Endereço, Coordenada, Período, Range de Datas → VO ✅
  string email, decimal valor, string cpf → Primitive Obsession ❌
```

### Padrão de Implementação (agnóstico)

```
ValueObject
  - Todos campos readonly
  - Construtor valida invariantes, lança DomainException se inválido
  - Equals() baseado em campos
  - GetHashCode() consistente com Equals()
  - Métodos retornam NOVO VO em vez de mutar

Exemplo:
  Dinheiro.Somar(outro: Dinheiro): Dinheiro  ✅ retorna novo
  dinheiro.Valor += 10  ❌ mutação direta
```

### Anti-Padrões
- VO com ID próprio.
- VO com estado mutável.
- VO que persiste diretamente (ORM mapeia VO como entidade separada com ID).

---

## BLOCO 3 — AGGREGATES (Agregados)

### Definição
Um **Aggregate** é um cluster de Entidades e Value Objects tratado como uma ÚNICA UNIDADE de consistência transacional. Tem uma **Aggregate Root** (Raiz) que é o único ponto de entrada externo.

### Regras Fundamentais (não negociáveis)
1. **Toda transação modifica apenas UM aggregate** por vez.
2. **Referências externas só apontam para a Aggregate Root** — nunca para entidades internas.
3. **IDs entre aggregates, nunca referências de objeto** para outros aggregates.
4. **A Aggregate Root é responsável pela consistência de todos os membros internos.**
5. **Tamanho:** Prefira aggregates PEQUENOS. O tamanho ideal é o mínimo necessário para garantir invariantes.

### Identificação de Fronteiras

```
Perguntas para definir fronteira:
  1. "Quais dados PRECISAM estar consistentes na mesma transação?" → dentro do mesmo aggregate
  2. "Posso modificar X sem modificar Y na mesma operação?" → provavelmente aggregates separados
  3. "Existe invariante que envolve X e Y juntos?" → podem precisar estar no mesmo aggregate
  4. "Quantas instâncias simultâneas existem?" → Muitas = aggregate menor para reduzir contenção

Exemplo — Pedido de E-commerce:
  Aggregate: Pedido
    Root: Pedido (id, status, cliente-id, endereço-entrega)
    Interno: ItemPedido (produto-id, quantidade, preço-unitário)
    Interno: Desconto (tipo, valor)
  
  Separado (outro aggregate): Estoque
    Root: Estoque (produto-id)
  
  Comunicação: Pedido publica DomainEvent "PedidoConfirmado"
               Estoque consome evento e reserva itens → consistência eventual ✅
```

### Anti-Padrões
- Aggregate que referência outro aggregate por objeto (em vez de ID).
- Uma transação que modifica múltiplos aggregates diretamente.
- Aggregate "deus" que contém todo o modelo do sistema.
- Aggregate Root que expõe coleções internas para modificação direta.

```
  pedido.Itens.Add(item)         ❌ exposição direta da coleção
  pedido.AdicionarItem(item)     ✅ método controlado pela root
```

---

## BLOCO 4 — DOMAIN EVENTS (Eventos de Domínio)

### Definição
**Domain Events** são fatos que ACONTECERAM no domínio. São imutáveis, nomeados no passado, e representam mudanças de estado significativas para o negócio.

### Regras Obrigatórias
- Nome SEMPRE no passado: `PedidoConfirmado`, `PagamentoProcessado`, `ClienteCadastrado`.
- Imutável — nunca mude um evento após criação.
- Gerado pela Aggregate Root ao executar operações de negócio.
- Contém apenas dados necessários para os consumidores reagirem.
- NÃO contém lógica de negócio.

### Padrão de Despacho

```
Opção A — Coleta na Raiz (recomendada para domínios simples):
  Aggregate Root coleta eventos em lista interna
  Repositório/UoW lê e despacha após persistência
  
Opção B — MediatR/Message Bus (domínios distribuídos):
  Aggregate Root registra evento
  Após commit, framework despacha para handlers

Fluxo correto:
  1. pedido.Confirmar() → adiciona PedidoConfirmado à lista interna
  2. repositório.Salvar(pedido) → persiste
  3. dispatcher.Publicar(pedido.Eventos) → notifica outros contextos
  4. pedido.LimparEventos()
```

### Anti-Padrões
- Evento no presente: `ConfirmarPedido`, `ProcessarPagamento` — isso é comando, não evento.
- Evento que referência objetos complexos mutáveis em vez de dados primitivos/VOs.
- Despachar evento ANTES de persistir (estado inconsistente).

---

## BLOCO 5 — DOMAIN SERVICES (Serviços de Domínio)

### Definição
Um **Domain Service** contém lógica de negócio que NÃO pertence naturalmente a nenhuma Entidade ou Value Object — geralmente porque envolve múltiplos aggregates ou recursos externos abstraídos.

### Quando Criar (critério de decisão)
```
"Essa lógica pertence à Entidade/VO?"  → implementar na entidade ✅
"Envolve múltiplos aggregates?"         → Domain Service ✅
"Precisa de abstração de infra?"        → Domain Service com porta (interface) ✅
"Parece não pertencer a ninguém?"       → Domain Service ✅

Exemplos:
  TransferenciaService.Transferir(contaOrigem, contaDestino, valor)  ✅
  ValidadorCpfService (consulta receita federal via interface)        ✅
  PedidoService.CalcularFrete(pedido, endereço)                       ✅
```

### Regras
- Domain Service fica na camada de domínio.
- Se precisar de infra (ex: consultar banco externo), usa INTERFACE definida no domínio, implementada na infra.
- Não tem estado persistente próprio.
- Não é o mesmo que Application Service (que orquestra casos de uso).

### Anti-Padrões
- Domain Service que importa classes de infraestrutura diretamente.
- Application Service sendo chamado de Domain Service.
- Domain Service com estado (cache, counters) — isso é infra.

---

## BLOCO 6 — REPOSITORIES (Interfaces de Repositório)

### Definição
A **interface** do repositório é definida no DOMÍNIO. A implementação fica na infraestrutura.

### Regras Obrigatórias
- Interface no domínio, implementação na infraestrutura.
- Repositório opera em AGGREGATES, nunca em entidades internas diretamente.
- Retorna domínios ricos (aggregates), nunca DTOs ou entidades de banco.
- Métodos devem refletir linguagem ubíqua.

```
Domínio define:
  interface IPedidoRepository
    BuscarPorId(id: PedidoId): Pedido | null
    BuscarPorCliente(clienteId: ClienteId): Pedido[]
    Salvar(pedido: Pedido): void
    Remover(pedido: Pedido): void

Infraestrutura implementa:
  class PedidoRepositoryEfCore implements IPedidoRepository
    (usa DbContext, mapeia ORM → Aggregate)
```

### Anti-Padrões
- Repositório genérico `IRepository<T>` que expõe `IQueryable<T>` — vaza detalhes de ORM para o domínio.
- Repositório que retorna entidades do ORM diretamente.
- Múltiplos repositórios para diferentes partes do mesmo aggregate.

---

## BLOCO 7 — FACTORIES

### Definição
**Factories** encapsulam lógica complexa de criação de aggregates ou objetos de domínio quando o construtor simples não é suficiente.

### Quando Usar
```
Usar Factory quando:
  - Criação envolve múltiplos VOs e validações
  - Criação requer consultar outros aggregates
  - Lógica de criação é complexa demais para o construtor

Evitar Factory quando:
  - Construtor simples + validações são suficientes
  - Apenas um ou dois parâmetros
```

---

## BLOCO 8 — APPLICATION SERVICES

### Definição
**Application Services** orquestram casos de uso. NÃO contêm regras de negócio — delegam para o domínio.

### Responsabilidades
```
Application Service:
  1. Recebe Command/DTO da camada de apresentação/API
  2. Busca aggregate via repositório
  3. Chama método de domínio no aggregate
  4. Persiste via repositório/unit of work
  5. Despacha domain events
  6. Retorna resultado (DTO/Response) para a camada de cima

NÃO FAZER no Application Service:
  ❌ if (pedido.Status == "Pendente") pedido.Status = "Confirmado"  → regra de negócio no service
  ✅ pedido.Confirmar()  → regra encapsulada no aggregate
```

### Separação Application vs Domain Service

```
Application Service (orquestração, sem regra de negócio):
  - Coordena fluxo
  - Gerencia transações
  - Traduz entrada/saída (Command → Domain call → DTO)

Domain Service (regra de negócio que não cabe na entidade):
  - Pura lógica de negócio
  - Não sabe de persistência
  - Não sabe de HTTP/gRPC/mensageria
```

---

## CHECKLIST DE REVISÃO DDD TÁTICO

Antes de commitar código de domínio, verifique:

```
[ ] Entidades têm ID imutável e sem setters públicos diretos?
[ ] Value Objects são imutáveis e têm igualdade por valor?
[ ] Aggregates têm fronteiras mínimas necessárias?
[ ] Aggregates referenciam outros aggregates apenas por ID?
[ ] Uma transação = um aggregate?
[ ] Domain Events nomeados no passado?
[ ] Eventos despachados APÓS persistência?
[ ] Interface de repositório está no domínio?
[ ] Repositório opera em aggregates completos?
[ ] Application Service NÃO contém lógica de negócio?
[ ] Camada de domínio tem ZERO imports de framework/infra?
[ ] Nomes refletem a linguagem ubíqua do contexto?
[ ] Exceções de domínio são do tipo DomainException (não genéricas)?
```

---

## GLOSSÁRIO RÁPIDO

| Termo | Quando usar |
|---|---|
| Entity | Identidade única, mutável no tempo |
| Value Object | Definido por valor, imutável |
| Aggregate | Cluster de consistência transacional |
| Aggregate Root | Único ponto de entrada do aggregate |
| Domain Event | Fato ocorrido, nome no passado |
| Domain Service | Lógica que não cabe na entidade |
| Application Service | Orquestrador de caso de uso |
| Repository (interface) | Abstração de persistência no domínio |
| Factory | Criação complexa encapsulada |

---

## REFERÊNCIAS CONCEPTUAIS

- Eric Evans — *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003)
- Vaughn Vernon — *Implementing Domain-Driven Design* (2013)
- Vaughn Vernon — *Domain-Driven Design Distilled* (2016)
- Martin Fowler — *Patterns of Enterprise Application Architecture* (2002)
