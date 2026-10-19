# TXC Guidelines — Transaction Context Pattern

> **Versão:** 1.0  
> **Escopo:** TXC v2 — padrão arquitetural central das skills bks-sdd v12+  
> **Referência primária:** `txc/validation/METRICAS.md`  
> **Paradigma:** Agnóstico de linguagem (exemplos em pseudocódigo com sabor .NET/TypeScript)  
> **Temperatura de decisão:** 0.02 — regras prescritivas, não sugestões

---

## SEÇÃO 1 — O Que é TXC

### Definição

**Transaction Context (TXC)** é um **Parameter Object** — não um DTO de entrada nem de saída. Ele transporta **estado intermediário** entre as fases de execução do Handler, carregando dados que pertencem ao fluxo de processamento mas não pertencem ao domínio nem à camada de apresentação.

```
// TXC: carrega estado ENTRE fases — não é input nem output
class PedidoTransaction {
    // Fase 1 — Hydrate (dados vindos de fora)
    ClienteId ClienteId  { get; private set; }
    Item[] Itens         { get; private set; }

    // Fase 2 — Apply (estado criado pelo domínio)
    Pedido Pedido        { get; private set; }

    // Métodos semânticos — chamados pelo Handler em sequência
    HydrateItens(clienteId, itens)   // Fase 1: popula campos de entrada
    HydratePedidoCriado(pedido)      // Fase 2: captura resultado do domínio
    FinalizeWith(pedido)             // Fase 3: prepara o output
}
```

### O que NÃO é TXC

- ❌ **NÃO é DTO de request** — não viaja da API para o Handler como input HTTP
- ❌ **NÃO é DTO de response** — não é retornado diretamente para o cliente
- ❌ **NÃO é Command/Query do CQRS** — não é o parâmetro da Primary Port
- ❌ **NÃO substitui o Aggregate** — não contém lógica de domínio

### Ciclo de vida obrigatório

```
1. Hydrate  → Primary Adapter popula campos de entrada na Transaction
2. Apply    → Handler chama Domain (Aggregate.Create/Cancel/etc.) e armazena resultado na Transaction
3. FinalizeWith → Transaction produz o Response final (PipelineResult)
```

### Regra de campos

A Transaction deve ter no máximo 5 campos de estado. Se precisar de mais, a feature provavelmente está misturando dois casos de uso distintos.

---

## SEÇÃO 2 — Árvore de Decisão TXC vs ALT

Execute está árvore para cada operação principal da feature. Documente o resultado no campo `Padrão de implementação:` do FEAT antes de escrever qualquer código.

```
A operação transforma estado entre 2+ etapas (Entry → Domain → Infra)?
│
├── NÃO ──→ É leitura?
│           ├── 1 fonte simples, sem join complexo
│           │     ──→ [ALT-1] QueryHandler
│           │         Exemplo: GetPedidoById, ListPedidosByStatus
│           │
│           ├── 2+ fontes / filtros complexos / agregações
│           │     ──→ [ALT-2] QueryComposer
│           │         Exemplo: relatório consolidado com joins de 3 tabelas
│           │
│           ├── Processamento em lote / coleção
│           │     ──→ [ALT-3] BatchProcessor
│           │         Exemplo: reprocessar pedidos pendentes da noite anterior
│           │
│           └── Utilitário técnico sem efeito de domínio
│                 ──→ [ALT-4] UtilityScript
│                     Exemplo: recalcular índice de busca, limpar cache
│
└── SIM ──→ Estado cruza Entry + Domain + Infra em 2+ fases distintas?
            │
            ├── SIM ──→ ✅ [TXC] Transaction Context Handler
            │               Exemplo: CreatePedido, CancelPedido, ApprovePayment
            │
            └── NÃO, 1 etapa simples ──→ [ALT-1] SimpleCommandHandler
                    Exemplo: MarkNotificationAsRead (sem efeito de domínio complexo)
```

### Exemplos por nó

| Operação | Padrão | Justificativa |
|----------|--------|---------------|
| `CreatePedido` | TXC | Hydrate itens → Domain.Create → Salvar → Publicar evento |
| `CancelPedido` | TXC | Hydrate pedido → Domain.Cancel → Salvar → Publicar evento |
| `GetPedidoById` | ALT-1 QueryHandler | Leitura simples, 1 fonte, sem transformação de estado |
| `ListPedidosByStatus` | ALT-1 QueryHandler | Leitura com filtro simples, sem efeito colateral |
| `RelatorioConsolidado` | ALT-2 QueryComposer | 3+ fontes, joins complexos, sem efeito colateral |
| `ReprocessarPendentes` | ALT-3 BatchProcessor | Opera sobre coleção, pode ter efeitos colaterais |
| `MarkNotificationAsRead` | ALT-1 SimpleCommandHandler | 1 etapa, sem estado intermediário relevante |

---

## SEÇÃO 3 — Regras de Primary Ports

### Regra fundamental

**Uma Primary Port por BoundedContext por tipo de operação (Command/Query).**

Nunca uma Primary Port por operação CRUD.

### Tabela ❌ Anti-padrão v1 vs ✅ TXC v2

| ❌ Anti-padrão v1 | ✅ TXC v2 |
|---|---|
| `ICreatePedidoUseCase` | `IPedidoHandler` (agrupa Create + Cancel) |
| `ICancelPedidoUseCase` | `IPedidoHandler` (uma interface por BC/tipo) |
| `IListPedidosUseCase` | `IPedidoQuery` (agrupa GetById + ListAll) |
| `IGetPedidoByIdUseCase` | `IPedidoQuery` (uma interface para todas as queries) |
| 4 interfaces para 4 operações | 2 interfaces para o BoundedContext Pedido |

### Formato canônico de Primary Port TXC

```csharp
// ✅ TXC v2 — Primary Port de Command (agrupa operações que transformam estado)
interface IPedidoHandler {
    Task<PipelineResult<PedidoResponse>> CreateAsync(PedidoTransaction tx, CancellationToken ct)
    Task<PipelineResult<PedidoResponse>> CancelAsync(CancelPedidoTransaction tx, CancellationToken ct)
}

// ✅ TXC v2 — Primary Port de Query (ALT-1, sem Transaction)
interface IPedidoQuery {
    Task<PipelineResult<PedidoResponse>> GetByIdAsync(Guid id, CancellationToken ct)
    Task<PipelineResult<IReadOnlyList<PedidoResponse>>> ListAllAsync(CancellationToken ct)
}
```

### Regra de agrupamento

- **Command Port:** agrupa operações TXC e ALT-1 SimpleCommand que pertencem ao mesmo BoundedContext
- **Query Port:** agrupa todas as queries (ALT-1, ALT-2) do mesmo BoundedContext
- **Nunca misturar:** Command Port não deve ter métodos de Query e vice-versa

### Nomenclatura

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Command Port | `I{Entidade}Handler` | `IPedidoHandler`, `IClienteHandler` |
| Query Port | `I{Entidade}Query` | `IPedidoQuery`, `IClienteQuery` |
| Implementação Command | `{Entidade}Handler` | `PedidoHandler` |
| Implementação Query | `{Entidade}QueryHandler` | `PedidoQueryHandler` |

---

## SEÇÃO 4 — Regras de Secondary Ports

### Regra fundamental

**Uma Secondary Port por aggregate ou recurso externo.**

Nunca uma Secondary Port genérica que serve múltiplos aggregates.

### Tabela ❌ Anti-padrão v1 vs ✅ TXC v2

| ❌ Anti-padrão v1 | ✅ TXC v2 |
|---|---|
| `IDBRepositoryPort` (genérico) | `IPedidoRepository` (específico do aggregate) |
| `IRepository<T>` (genérico com T) | `IClienteRepository` (específico) |
| `IDatabaseService` | `IPedidoRepository` + `IClienteRepository` separados |
| `IExternalServicePort` (genérico) | `IProcessadorDePagamento`, `INotificacaoService` (um por recurso) |

### Formato canônico de Secondary Port

```csharp
// ✅ TXC v2 — Secondary Port específica do aggregate
interface IPedidoRepository {
    Task<Pedido?> GetByIdAsync(Guid id, CancellationToken ct)
    Task<IReadOnlyList<Pedido>> GetAllAsync(CancellationToken ct)
    Task SaveAsync(Pedido pedido, CancellationToken ct)
}

// ✅ TXC v2 — Secondary Port específica do serviço externo
interface INotificacaoService {
    Task NotificarPedidoCriadoAsync(Guid pedidoId, string email, CancellationToken ct)
    Task NotificarPedidoCanceladoAsync(Guid pedidoId, CancellationToken ct)
}
```

### Onde ficam as Secondary Ports

- **Necessidade do domínio** (repositório do aggregate): `Domain/` ou `Features/{BC}/{Entidade}/Domain/`
- **Necessidade de orquestração** (serviço externo): `Application/` ou `Features/{BC}/{Entidade}/Application/`

---

## SEÇÃO 5 — Transaction Map

### O que é o Transaction Map

Tabela que documenta o fluxo interno de uma operação TXC: quais fases existem, qual método semântico é chamado em cada fase, qual é a responsabilidade e qual estado intermediário é carregado na Transaction após cada fase.

### Template canônico

| Fase | Método Semântico | Responsabilidade | Estado Intermediário |
|------|------------------|------------------|----------------------|
| 1. Hydrate | `HydrateXxx(input)` | Popula campos de entrada na Transaction a partir do request | `tx.Campo1`, `tx.Campo2` |
| 2. Apply | `HydrateXxxCriado(aggregate)` | Chama o domínio, captura o aggregate criado/modificado | `tx.Aggregate` |
| 3. Finalize | `FinalizeWith(aggregate)` | Prepara o PipelineResult com o Response final | `PipelineResult<Response>` |

### Exemplo — CreatePedido (TXC)

| Fase | Método Semântico | Responsabilidade | Estado Intermediário |
|------|------------------|------------------|----------------------|
| 1. Hydrate | `HydrateItens(clienteId, itens)` | Valida e popula dados de entrada | `tx.ClienteId`, `tx.Itens` |
| 2. Apply | `HydratePedidoCriado(pedido)` | Chama `Pedido.Criar()`, armazena aggregate | `tx.Pedido` |
| 3. Finalize | `FinalizeWith(pedido)` | Monta `PedidoResponse` e retorna `PipelineResult.Success` | `PipelineResult<PedidoResponse>` |

### Exemplo — CancelPedido (TXC)

| Fase | Método Semântico | Responsabilidade | Estado Intermediário |
|------|------------------|------------------|----------------------|
| 1. Hydrate | `HydratePedido(pedido)` | Carrega aggregate existente do repositório | `tx.Pedido` |
| 2. Apply | `HydratePedidoCancelado(pedido)` | Chama `pedido.Cancelar()`, captura resultado | `tx.Pedido` (mutado) |
| 3. Finalize | `FinalizeWith(pedido)` | Monta `PedidoResponse` com status Cancelado | `PipelineResult<PedidoResponse>` |

### Exemplo — GetPedidoById (ALT-1 — sem Transaction Map)

Para ALT-1, não há Transaction. Apenas:
- **Input:** `Guid id`
- **Output:** `PipelineResult<PedidoResponse>`

---

## SEÇÃO 6 — Anti-padrões Explícitos

### Anti-padrão 1 — Primary Port por operação CRUD

```
❌ ERRADO:
interface ICreatePedidoUseCase { ExecuteAsync(cmd) }
interface IListPedidosUseCase  { ExecuteAsync(query) }
interface ICancelPedidoUseCase { ExecuteAsync(cmd) }
// Resultado: 3 interfaces, 3 handlers, 3 registros no DI, duplicação de contexto

✅ CORRETO (TXC v2):
interface IPedidoHandler { CreateAsync(tx), CancelAsync(tx) }
interface IPedidoQuery   { GetByIdAsync(id), ListAllAsync() }
// Resultado: 2 interfaces, 2 handlers, contexto unificado do BoundedContext
```

### Anti-padrão 2 — Steps separados (ValidationStep, ProcessingStep)

```
❌ ERRADO:
[10] ValidationStep   → valida entrada separadamente
[20] PreProcessingStep → prepara dados
[30] ProcessingStep   → executa lógica
// Resultado: fluxo fragmentado, estado perdido entre steps, difícil de debugar

✅ CORRETO (TXC v2):
Handler.CreateAsync(tx):
    tx.HydrateItens(...)           // Fase 1: entrada
    var pedido = Pedido.Criar(...) // Fase 2: domínio
    tx.HydratePedidoCriado(pedido) // Fase 2: captura
    await _repo.SaveAsync(pedido)  // Fase 3: persistência
    return tx.FinalizeWith(pedido) // Fase 3: output
// Resultado: fluxo linear, estado explícito na Transaction, lógica em 1 arquivo
```

### Anti-padrão 3 — Secondary Port genérica (IDBRepositoryPort)

```
❌ ERRADO:
interface IDBRepositoryPort {
    SaveAsync(entity: object): void
    GetAsync(id: Guid): object
}
// Resultado: tipagem perdida, aggregate tratado como object, contrato sem semântica

✅ CORRETO (TXC v2):
interface IPedidoRepository {
    GetByIdAsync(id: Guid): Pedido?
    SaveAsync(pedido: Pedido): void
}
// Resultado: contrato tipado, nomes de método com semântica de domínio
```

### Anti-padrão 4 — Transaction sem estado intermediário

```
❌ ERRADO:
class PedidoTransaction {
    Input:  ClienteId, Itens        // só entrada
    Output: PedidoResponse          // só saída
    // Sem estado intermediário → não é TXC, é apenas um DTO com dois campos
}

✅ CORRETO (TXC v2):
class PedidoTransaction {
    // Entrada
    ClienteId ClienteId { get; private set; }
    Item[] Itens        { get; private set; }
    // Estado intermediário (criado durante o fluxo)
    Pedido Pedido       { get; private set; }
    // Métodos semânticos que transitam entre estados
    HydrateItens(...)           // popula entrada
    HydratePedidoCriado(pedido) // captura estado intermediário
    FinalizeWith(pedido)        // produz output
}
```

---

## SEÇÃO 7 — Checklist de Conformidade TXC

Use esta lista ao revisar um PRD §8 ou FEAT §5 gerado pela skill.

### Para PRD §8

| # | Verificação | SIM/NÃO |
|---|-------------|---------|
| 1 | §8 usa template TXC-aware (§8a–§8d) para projetos .NET/TypeScript? | |
| 2 | §8b lista Primary Ports agrupadas por BoundedContext (não por operação CRUD)? | |
| 3 | §8b distingue Handler (Command) de Query — nomes seguem `I{Entidade}Handler` / `I{Entidade}Query`? | |
| 4 | §8c lista Secondary Ports específicas por aggregate (não `IDBRepositoryPort` genérico)? | |
| 5 | §8a descreve fluxo com Transaction (Hydrate → Apply → FinalizeWith), não Steps numerados? | |
| 6 | Não há menção a `ICreateXxxUseCase`, `IUpdateXxxUseCase` ou `IDeleteXxxUseCase`? | |
| 7 | Não há menção a `ValidationStep`, `ProcessingStep`, `PostProcessingStep` como padrão? | |

### Para FEAT §5 (Contratos de Dados)

| # | Verificação | SIM/NÃO |
|---|-------------|---------|
| 1 | Campo `Padrão de implementação:` presente (TXC ou ALT-N)? | |
| 2 | Se TXC: tabela Transaction Map presente com Fase / Método Semântico / Responsabilidade / Estado Intermediário? | |
| 3 | Se ALT-1/2: contrato simplificado Input/Output presente (sem Transaction Map)? | |
| 4 | Transaction Map tem ≤ 5 linhas (≤ 5 campos de estado)? | |
| 5 | Métodos semânticos têm nomes de domínio (não nomes técnicos como `SetData`, `Process`)? | |
| 6 | §4 Restrições Técnicas menciona o aggregate root e os eventos publicados? | |

### Números validados (fonte: `txc/validation/METRICAS.md`)

| Métrica | v1 (baseline) | v2 (TXC) | Redução |
|---------|--------------|----------|---------|
| Linhas de plumbing por feature (4 ops) | ~86 | ~18 | **~79%** |
| Arquivos totais por feature (4 ops) | ~28 | 11 (canônico) | **~61%** |
| DTOs de resposta por feature | ~4 (um por op) | 1 (`PedidoResponse` único) | **~75%** |
| Arquivos de Steps (Validation/Processing) | ~8 (2 por op) | 0 | **~100%** |
