---
name: bks-dotnet-solutions
version: 2.0
description: |
  Guia prescritivo para geração de soluções .NET completas com Arquitetura Hexagonal BKS,
  padrão TXC (Transaction Context) e DDD. Use SEMPRE que o usuário quiser criar, estruturar
  ou implementar qualquer solução .NET — Minimal API, Worker/Background Service ou SDK/Lib.

  Trigger: criar projeto .NET, hexagonal em .NET, TXC, transaction parameter object,
  CRUD com Dapper ou EF Core, Stored Procedures, Single Project vs Multi Project,
  BKS Stack, estrutura de pastas para projeto C#.

  A skill é OPINIONADA e PRESCRITIVA — recomenda ativamente, não apenas lista opções.
  É EMBEDDABLE — toda decisão obrigatória de padrão (TXC vs ALT-1/2/3/4) está documentada
  in-line; o agente NÃO PODE pular a árvore de decisão.

trigger_keywords:
  - .net solution
  - hexagonal .net
  - minimal api
  - worker .net
  - sdk .net
  - txc
  - transaction context
  - bks stack
  - dapper crud
  - stored procedure .net
  - single project vs multi project

related_guidelines:
  - GUIDELINE-DDD-v2.md          (tático: Entities, VOs, Aggregates, Domain Services)
  - GUIDELINE-HEXAGONAL-v2.md    (estrutural: Ports & Adapters, dependências)
  - GUIDELINE-CONTEXTOS-v2.md    (estratégico: Bounded Contexts, Subdomain types)
---

# bks-dotnet-solutions — Skill v2.0

> **Mudanças vs v1:** Adoção do padrão TXC (Transaction Context). Estrutura de pastas
> reduzida (~73% menos arquivos por entidade CRUD). Árvore de decisão obrigatória
> (TXC vs ALT-1/2/3/4) embutida na Fase 5. Declaração de padrão obrigatória no output.
> Integração explícita com 3 guidelines auxiliares (DDD, Hexagonal, Contextos).

---

## REGRA ZERO — ANTES DE GERAR QUALQUER CÓDIGO

> **Esta regra é absoluta e não negociável.**

Você DEVE:

1. Conduzir a **Entrevista Estruturada (7 fases)** — sem pular fases mesmo que o usuário tenha dado pistas no prompt inicial. Cada fase é uma decisão consciente.
2. Para cada operação a gerar, percorrer a **Árvore de Decisão TXC** (Fase 5.2) e **declarar explicitamente** no output qual padrão foi escolhido. A ausência da declaração é proibida.
3. Cumprir as **Restrições Absolutas** (seção final) — qualquer violação invalida a geração.
4. Quando houver dúvida arquitetural, **PERGUNTE ao usuário antes de implementar**. Não invente tecnologias não mencionadas.

---

## ENTREVISTA ESTRUTURADA — 7 FASES

### Fase 1 — Tipo de solução

```
Pergunta:
  Qual o tipo de solução?
  [A] Minimal API (REST)
  [B] Worker / Background Service
  [C] SDK / Biblioteca reutilizável

Saída: {tipo_solucao}
```

### Fase 2 — Modo de projeto

```
Pergunta:
  SingleProject (1 csproj com Features/) ou MultiProject (Domain + Application + Adapters + Host)?

Recomendação automática (a confirmar com usuário):
  - 1-3 contextos coesos, time único, deploy junto → SingleProject
  - 4+ contextos OU times distintos OU regras de dependência via project reference → MultiProject

Ver GUIDELINE-CONTEXTOS-v2.md §6 para critérios completos.

Saída: {modo_projeto}
```

### Fase 3 — Complexidade do domínio

```
Pergunta:
  O domínio tem regras de negócio ricas (validações, transições de estado, eventos)
  ou é predominantemente CRUD de leitura/escrita simples?

  [A] Domínio rico — usar Aggregates, Value Objects, Domain Events, Domain Services
  [B] CRUD simples — entidades anêmicas com validação básica

Saída: {complexidade_dominio}
```

### Fase 4 — Banco de dados

```
Pergunta:
  Qual banco e tecnologia de acesso?

  [A] Sem banco (puro processamento, integrações)
  [B] PostgreSQL com Dapper                ← preferência BKS
  [C] PostgreSQL com EF Core
  [D] SQL Server com Dapper                ← preferência BKS
  [E] SQL Server com EF Core
  [F] SQL Server com Stored Procedures     ← ver references/stored-procedures.md
  [G] MongoDB
  [H] Redis (cache)
  [I] Outro — especificar

Saída: {banco}, {acesso}
```

### Fase 5 — Entidades, contextos e operações

#### 5.1 — Listagem

```
Pergunta:
  Quais Bounded Contexts e quais entidades por contexto?
  Para cada entidade, quais operações? (CRUD padrão ou customizadas?)

Output esperado:
  Contexto: Vendas
    Entidade: Pedido
      Operações: Create, GetById, GetAll, Update, Cancel, Confirm
    Entidade: ItemPedido (entidade interna do aggregate Pedido)

  Contexto: Catalogo
    Entidade: Produto
      Operações: Create, GetById, GetAll, Update, Delete
```

#### 5.2 — Árvore de Decisão TXC (OBRIGATÓRIA POR OPERAÇÃO)

> **Para cada operação listada na 5.1, percorra a árvore e declare o padrão escolhido.**

```
A operação tem regras de negócio que TRANSFORMAM ESTADO entre etapas distintas?
│
├── NÃO ──→ É leitura de dados?
│           │
│           ├── SIM ──→ Quantas fontes de dados?
│           │           ├── 1 fonte, filtro simples ──→ [ALT-1] QueryHandler
│           │           └── 2+ fontes ou filtros dinâmicos complexos ──→ [ALT-2] QueryComposer
│           │
│           └── NÃO ──→ É processamento de múltiplos registros?
│                       ├── SIM ──→ [ALT-3] BatchProcessor
│                       └── NÃO ──→ É operação técnica sem domínio? ──→ [ALT-4] UtilityScript
│
└── SIM ──→ O estado precisa ser rastreado entre 2+ etapas distintas?
            │
            ├── NÃO (1 etapa só) ──→ [ALT-1] SimpleCommandHandler
            │
            └── SIM ──→ As etapas cruzam Entry + Domain + Infra?
                        ├── NÃO (tudo na infra, ex: ETL interno) ──→ [ALT-3] BatchProcessor
                        └── SIM ──→ ✅ USE TXC
```

#### 5.3 — Tabela de decisão rápida

| Operação típica | Padrão | Razão |
|---|---|---|
| `GetById` (busca por id, projeção direta) | ALT-1 QueryHandler | Leitura simples sem regra |
| `GetAll` / `List` com filtros opcionais simples | ALT-1 QueryHandler | Sem efeito colateral |
| `GetDashboard` (combina 3+ repos) | ALT-2 QueryComposer | Composição multi-fonte |
| `Create` com validação + cálculo + evento | ✅ TXC | Estado em 3 fases |
| `Update` com transição de estado | ✅ TXC | Regra de transição |
| `Cancel` com validação de prazo + notificação | ✅ TXC | 2+ etapas com domínio |
| `Confirm` com regra de negócio + evento | ✅ TXC | Estado evolui |
| `Delete` simples sem regra | ALT-1 SimpleCommandHandler | 1 etapa, sem estado |
| `ImportFromCsv` (10k linhas) | ALT-3 BatchProcessor | Contexto por item |
| `ExportReport` | ALT-2 QueryComposer | Leitura composta |
| `RebuildIndex` (operação técnica) | ALT-4 UtilityScript | Sem domínio |

#### 5.4 — Declaração obrigatória no output

Antes de gerar o código de cada operação, o agente DEVE imprimir:

```
Operação: {Nome}
Decisão de padrão: [TXC | ALT-1 QueryHandler | ALT-1 SimpleCommandHandler |
                    ALT-2 QueryComposer | ALT-3 BatchProcessor | ALT-4 UtilityScript]
Caminho da árvore: [ramo seguido, ex.: "SIM (regras) → SIM (2+ etapas) → SIM (cruza camadas) → TXC"]
Razão: [justificativa de uma frase, em linguagem do negócio]
```

#### 5.5 — Sinais de alerta TXC sendo forçado

Se durante a geração for detectado qualquer sinal abaixo, **PARE e reavalie**:

1. Transaction com apenas `Input` e `Output`, sem campos de estado intermediário → use ALT-1.
2. Transaction com um único método semântico → use ALT-1 SimpleCommandHandler.
3. Métodos com nomes técnicos (`SetData`, `LoadResult`, `StoreValue`) em vez de nomes do negócio (`HydrateCliente`, `ApplyPricing`, `FinalizeWith`) → o domínio não foi modelado; revisar.
4. Handler com `if (!tx.IsValid) return` antes de qualquer chamada ao domínio → o "domínio" pode ser apenas persistência disfarçada.
5. Transaction com mais de 7 campos de estado → feature não decomposta; quebrar em sub-features.

### Fase 6 — Observabilidade

```
Pergunta:
  Endpoint OTLP (OpenTelemetry) ou local apenas (console + Serilog)?

Saída: {observabilidade}
```

### Fase 7 — Confirmação consolidada

```
Apresentar tabela final:
  Tipo solução:    {tipo_solucao}
  Modo projeto:    {modo_projeto}
  Complexidade:    {complexidade_dominio}
  Banco/Acesso:    {banco} / {acesso}
  Bounded Contexts: [lista]
  Operações × Padrão: [tabela com declarações da Fase 5.4]
  Observabilidade: {observabilidade}

Aguardar "OK" do usuário antes de gerar código.
```

---

## ESTRUTURAS DE PASTA

### A) Single Project — TXC + ALT-1 misturados (recomendação padrão)

```
src/
{ServiceName}/
├── _Shared/
│   ├── Domain/Core/Common/
│   │   ├── Pipeline/
│   │   │   ├── PipelineResult.cs              ← contrato de retorno
│   │   │   └── PipelineOrchestrator.cs        ← opcional, fluxos com 4+ etapas
│   │   ├── Transactions/
│   │   │   └── BaseTransaction.cs             ← opcional (CorrelationId, UserId, TraceId)
│   │   ├── Entity.cs
│   │   ├── ValueObject.cs
│   │   └── DomainException.cs
│   └── Adapters/
│       ├── Inbound/API/
│       │   ├── ApiExtensions.cs               ← ConfigureAPI() + UseAPIExtensions()
│       │   ├── SwaggerExtensions.cs
│       │   └── JwtExtensions.cs               ← JWT Bearer (obrigatório)
│       └── Outbound/
│           ├── Persistence/IDbConnectionFactory.cs
│           └── Observability/
│               ├── Logging/
│               ├── Tracing/
│               └── Metrics/
├── Features/
│   └── {Contexto}Context/
│       └── {Entidade}/
│           ├── Domain/                                   ← DENTRO do hexágono
│           │   ├── {Entidade}.cs                         (Aggregate Root, class)
│           │   ├── {VO}.cs                               (Value Objects)
│           │   ├── {Evento}.cs                           (Domain Events)
│           │   ├── I{Entidade}Repository.cs              ← Secondary Port
│           │   └── {Entidade}DomainService.cs            (opcional)
│           ├── Application/                              ← DENTRO do hexágono
│           │   ├── {Entidade}Transaction.cs              ← TXC (se aplicável)
│           │   ├── {Entidade}Response.cs                 ← DTO único reutilizável
│           │   ├── I{Entidade}Handler.cs                 ← Primary Port (TXC consolida ops)
│           │   ├── {Entidade}Handler.cs                  ← Implementação (Create/Update/Cancel)
│           │   ├── Get{Entidade}ByIdHandler.cs           ← ALT-1 (1 arquivo, sem TXC)
│           │   ├── List{Entidade}Handler.cs              ← ALT-1
│           │   └── {Entidade}DashboardComposer.cs        ← ALT-2 (se houver)
│           └── Persistence/                              ← FORA do hexágono
│               ├── {DB}{Entidade}Repository.cs           ← implementa IPedidoRepository
│               └── {DB}{Entidade}ReadRepository.cs       ← CQRS read (opcional)
├── Program.cs
├── appsettings.json
└── appsettings.Development.json
```

**Contagem de arquivos por entidade típica (Pedido com Create/Update/Cancel + GetById/List):**
- Domain: 4 arquivos (Pedido, ItemPedido, Evento, IPedidoRepository)
- Application: 5 arquivos (Transaction, Response, IHandler, Handler, GetByIdHandler+ListHandler como 2 arquivos OU 1 ReadHandler)
- Persistence: 1-2 arquivos
- **Total: 10-11 arquivos** (vs 28+ na v1)

### B) Multi Project — TXC + ALT-1

```
src/
├── {ServiceName}.Domain/                       Domain.csproj
│   ├── Common/{Entity, VO, DomainException, PipelineResult}.cs
│   └── {Contexto}Context/{Entidade}/
│       ├── {Entidade}.cs
│       ├── {VO}.cs
│       ├── {Evento}.cs
│       └── I{Entidade}Repository.cs
│
├── {ServiceName}.Application/                  Application.csproj  → ref Domain
│   ├── Extensions/ApplicationExtensions.cs     ← ConfigureApplication()
│   └── UseCases/{Contexto}/{Entidade}/
│       ├── {Entidade}Transaction.cs
│       ├── {Entidade}Response.cs
│       ├── I{Entidade}Handler.cs
│       ├── {Entidade}Handler.cs                ← TXC: Create/Update/Cancel
│       ├── Get{Entidade}ByIdHandler.cs         ← ALT-1
│       └── List{Entidade}Handler.cs            ← ALT-1
│
├── {ServiceName}.Adapters.Outbound.Persistence/   Adapters.Outbound.Persistence.csproj  → ref Domain
│   ├── Extensions/PersistenceExtensions.cs     ← ConfigurePersistence()
│   ├── SQL/{DB}/IDbConnectionFactory.cs
│   └── {Contexto}/{DB}{Entidade}Repository.cs
│
└── {ServiceName}.API/                          {ServiceName}.API.csproj  → ref Application + Adapters
    ├── Program.cs
    ├── appsettings.json
    ├── Extensions/{ApiExtensions, JwtExtensions, SwaggerExtensions}.cs
    └── Endpoints/{Contexto}/{Entidade}Endpoints.cs
```

> 📌 **Formato da solution:** toda solution .NET 10 é **`.slnx`** — formato XML padrão do SDK 10,
> mais enxuto e sem os GUIDs duplicados do formato clássico. `dotnet new sln` sob o SDK 10 já gera
> `.slnx` por padrão. O `.sln` clássico fica reservado a solution que precise abrir em ferramenta
> sem suporte ao novo formato.

> 🛑 **Biblioteca de asserção:** **nunca FluentAssertions.** A v8 passou a licença comercial paga
> (Xceed) e a v7.x é a última sob Apache 2.0. Use o `Assert` nativo do xUnit — zero dependência de
> licença, uma a menos a auditar.

### C) Worker / Background Service

```
src/
{ServiceName}.Worker/
├── _Shared/                                    (igual ao SingleProject API)
├── Features/{Contexto}Context/{Entidade}/      (igual)
├── Workers/                                    ← Primary Adapters (IHostedService)
│   ├── {Entidade}KafkaConsumer.cs
│   └── {Entidade}ScheduledJob.cs
├── Program.cs                                  ← Host.CreateDefaultBuilder
└── appsettings.json
```

Workers que **iniciam um processamento de domínio** acionam `IPedidoHandler.CreateAsync(tx, ct)` — é Primary Adapter chamando Primary Port com TXC.

Workers que processam **lotes** usam ALT-3 BatchProcessor.

### D) SDK / Biblioteca

Ver `references/sdk-patterns.md`. Resumo:
- Sem `Adapters/Inbound/` (não há host).
- Expõe API pública via Fluent Builder.
- `IServiceCollection` extension para integração em hosts consumidores.

---

## TEMPLATES DE CÓDIGO

### Template 1 — TXC

```csharp
// {Entidade}Transaction.cs
namespace {ServiceName}.Features.{Contexto}Context.{Entidade}.Application;

public sealed record {Entidade}Transaction
{
    // Entrada (imutável, init-only)
    public required {TipoInput} Input { get; init; }
    public Guid CorrelationId { get; init; } = Guid.NewGuid();

    // Estado de domínio (privado set, evolui entre fases)
    public {TipoDominio}? {EstadoIntermediario} { get; private set; }

    // Output
    public {Entidade}Response? Resultado { get; private set; }

    // Métodos semânticos — nomes do NEGÓCIO
    public void Hydrate{Dependencia}({Tipo} dado) => {EstadoIntermediario} = dado;
    public void Apply{RegraDeNegocio}({Tipo} valor) { /* transforma estado */ }
    public void FinalizeWith({Entidade}Response resultado) => Resultado = resultado;
}
```

```csharp
// I{Entidade}Handler.cs — Primary Port
namespace {ServiceName}.Features.{Contexto}Context.{Entidade}.Application;

public interface I{Entidade}Handler
{
    ValueTask<PipelineResult<{Entidade}Response>> CreateAsync(
        {Entidade}Transaction tx, CancellationToken ct = default);

    ValueTask<PipelineResult<{Entidade}Response>> UpdateAsync(
        {Entidade}Transaction tx, CancellationToken ct = default);

    // Operações que exigem Transaction diferente (input distinto) usam Transaction próprio:
    ValueTask<PipelineResult<{Entidade}Response>> CancelAsync(
        Cancel{Entidade}Transaction tx, CancellationToken ct = default);
}
```

```csharp
// {Entidade}Handler.cs — Implementação
namespace {ServiceName}.Features.{Contexto}Context.{Entidade}.Application;

public class {Entidade}Handler : I{Entidade}Handler
{
    private readonly I{Entidade}Repository _repository;
    private readonly I{Dependencia}Service _dependenciaService;
    private readonly IEventDispatcher _eventDispatcher;

    public {Entidade}Handler(
        I{Entidade}Repository repository,
        I{Dependencia}Service dependenciaService,
        IEventDispatcher eventDispatcher)
    {
        _repository = repository;
        _dependenciaService = dependenciaService;
        _eventDispatcher = eventDispatcher;
    }

    public async ValueTask<PipelineResult<{Entidade}Response>> CreateAsync(
        {Entidade}Transaction tx, CancellationToken ct = default)
    {
        // Fase 1 — EntryHandler: validação de entrada
        if (!IsInputValid(tx.Input, out var inputError))
            return PipelineResult<{Entidade}Response>.Failure(inputError);

        // Fase 2 — DomainService: regras de negócio
        var dependência = await _dependenciaService.ValidarAsync(tx.Input.{Id}, ct).ConfigureAwait(false);
        if (dependência is null)
            return PipelineResult<{Entidade}Response>.Failure("{Dependencia} não encontrada");
        tx.Hydrate{Dependencia}(dependência);

        // Aplica regra de negócio (delegada ao domínio)
        tx.Apply{RegraDeNegocio}({calculo});

        // Fase 3 — InfraAdapter: persistência + eventos
        var aggregate = {Entidade}.Criar(tx.{EstadoIntermediario}!, /* params puros */);
        aggregate.Confirmar();  // método de domínio que emite DomainEvent

        await _repository.SalvarAsync(aggregate, ct).ConfigureAwait(false);
        await _eventDispatcher.PublishAsync(aggregate.Eventos, ct).ConfigureAwait(false);
        aggregate.LimparEventos();

        tx.FinalizeWith({Entidade}Response.From(aggregate));
        return PipelineResult<{Entidade}Response>.Success(tx.Resultado!);
    }

    private static bool IsInputValid({TipoInput} input, out string error)
    {
        // validação de formato/presença (NÃO regra de negócio)
        error = string.Empty;
        return true;
    }
}
```

### Template 2 — ALT-1 QueryHandler

```csharp
// Get{Entidade}ByIdHandler.cs — 1 ARQUIVO, sem Transaction
namespace {ServiceName}.Features.{Contexto}Context.{Entidade}.Application;

public class Get{Entidade}ByIdHandler
{
    private readonly I{Entidade}ReadRepository _repository;

    public Get{Entidade}ByIdHandler(I{Entidade}ReadRepository repository)
        => _repository = repository;

    public async ValueTask<PipelineResult<{Entidade}Response>> HandleAsync(
        Guid id, CancellationToken ct = default)
    {
        var entity = await _repository.FindByIdAsync(id, ct).ConfigureAwait(false);
        return entity is null
            ? PipelineResult<{Entidade}Response>.Failure("{Entidade} não encontrado")
            : PipelineResult<{Entidade}Response>.Success({Entidade}Response.From(entity));
    }
}
```

### Template 3 — ALT-2 QueryComposer

```csharp
public class {Nome}DashboardComposer
{
    private readonly I{Repo1} _repo1;
    private readonly I{Repo2} _repo2;
    private readonly I{Repo3} _repo3;

    public async ValueTask<PipelineResult<{Response}>> ComposeAsync(
        {Query} query, CancellationToken ct = default)
    {
        var task1 = _repo1.GetAsync(query.Filter1, ct);
        var task2 = _repo2.GetAsync(query.Filter2, ct);
        var task3 = _repo3.GetAsync(ct);

        await Task.WhenAll(task1, task2, task3).ConfigureAwait(false);

        return PipelineResult<{Response}>.Success(
            {Response}.Compose(task1.Result, task2.Result, task3.Result));
    }
}
```

### Template 4 — ALT-3 BatchProcessor

```csharp
public class Import{Entidade}BatchProcessor
{
    private readonly I{Entidade}Repository _repository;
    private readonly ILogger<Import{Entidade}BatchProcessor> _logger;

    public async ValueTask<BatchResult> ProcessAsync(
        Import{Entidade}Command command, CancellationToken ct = default)
    {
        var results = new BatchResult();
        await foreach (var line in command.Reader.ReadLinesAsync(ct).ConfigureAwait(false))
        {
            try
            {
                var entity = {Entidade}.Criar(/* mapping da linha */);
                await _repository.SalvarAsync(entity, ct).ConfigureAwait(false);
                results.RecordSuccess(line.LineNumber);
            }
            catch (DomainException ex)
            {
                _logger.LogWarning(ex, "Falha na linha {Line}", line.LineNumber);
                results.RecordFailure(line.LineNumber, ex.Message);
            }
        }
        return results;
    }
}
```

### Template 5 — Endpoint Minimal API (Primary Adapter)

```csharp
public static class {Entidade}Endpoints
{
    public static IEndpointRouteBuilder Map{Entidade}Endpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/{entidades}").RequireAuthorization();   // JWT obrigatório

        // POST → TXC
        group.MapPost("/", async (
            Criar{Entidade}Request req,
            I{Entidade}Handler handler,
            CancellationToken ct) =>
        {
            var tx = new {Entidade}Transaction { Input = req.ToInput() };
            var result = await handler.CreateAsync(tx, ct);
            return result.IsSuccess
                ? Results.Created($"/api/{entidades}/{result.Value!.Id}", result.Value)
                : Results.UnprocessableEntity(result.Error);
        });

        // GET by id → ALT-1 QueryHandler
        group.MapGet("/{id:guid}", async (
            Guid id,
            Get{Entidade}ByIdHandler handler,
            CancellationToken ct) =>
        {
            var result = await handler.HandleAsync(id, ct);
            return result.IsSuccess
                ? Results.Ok(result.Value)
                : Results.NotFound(result.Error);
        });

        return app;
    }
}
```

### Template 6 — Program.cs (composição)

```csharp
var builder = WebApplication.CreateBuilder(args);

// 1. Inbound — API
builder.Services.ConfigureAPI(builder.Configuration);

// 2. Application — Handlers (TXC + ALT-1/2/3)
builder.Services.ConfigureApplication(builder.Configuration);

// 3. Outbound — Persistence + Observability
builder.Services.ConfigurePersistence(builder.Configuration);
builder.Services.ConfigureTracing(builder.Configuration);
builder.Host.AddSerilogAdapter(builder.Configuration);

var app = builder.Build();

// Encapsula middleware + endpoints + healthchecks + app.Run()
app.UseAPIExtensions();
```

---

## REGRAS DE TIPO (.NET)

| Situação | Tipo C# |
|---|---|
| Transaction (TXC) | `sealed record` |
| Command / Query / Request DTO / Response DTO | `sealed record class` |
| Value Object ≤ 16 bytes | `readonly record struct` |
| Value Object > 16 bytes | `sealed record class` |
| Entity / Aggregate Root | `class` (NUNCA `record`) |
| Domain Event | `sealed record class` |
| `PipelineResult<T>` | `readonly record struct` |

---

## RESTRIÇÕES ABSOLUTAS

> **Violação de qualquer item abaixo invalida a geração e exige reescrita.**

### Arquiteturais
1. ❌ MediatR, BSMediator ou qualquer dispatcher de mensagens internas.
2. ❌ `record` para Entities/Aggregates (semântica de identidade exige `class`).
3. ❌ `IQueryable<T>` exposto por Secondary Port — vaza ORM para o domínio.
4. ❌ EF Core annotations no Domain layer.
5. ❌ Repositórios genéricos `IRepository<T>` "catchall".
6. ❌ Domain referenciando Application, Adapters ou frameworks externos.
7. ❌ Application referenciando Adapters concretos (apenas Ports).
8. ❌ Aggregate ou Domain Service recebendo `{Entidade}Transaction` como parâmetro.

### Performance
9. ❌ `.Result` ou `.Wait()` em código async.
10. ✅ `ValueTask<T>` em todas as Primary Ports e operações de hot-path.
11. ✅ `ConfigureAwait(false)` em todo `await` de library/infrastructure.
12. ✅ Logging estruturado (sem string interpolation em hot path).
13. ✅ `StringComparison.Ordinal` em comparações que não são linguísticas.

### Segurança (Minimal API)
14. ✅ JWT Bearer obrigatório: `AddAuthentication() + AddJwtBearer() + AddAuthorization()`.
15. ✅ `RequireAuthorization()` em **TODOS** os `MapGroup` e endpoints (exceto health/swagger explicitamente liberados).
16. ✅ `UseAuthentication()` + `UseAuthorization()` no pipeline após `RequestTracingMiddleware`.

### Result Pattern
17. ❌ `throw` para erros de negócio (entidade não encontrada, regra violada, validação). Use `PipelineResult<T>.Failure(...)`.
18. ✅ `throw` apenas para: dependência nula, configuração inválida, estado irrecuperável.
19. ❌ `PipelineResult<T>` declarado como nullable (`PipelineResult<T>?`).

### TXC específico
20. ❌ Transaction sem campos de estado intermediário (apenas Input + Output) — use ALT-1.
21. ❌ Métodos do Transaction com nomes técnicos (`SetData`, `LoadResult`) — use nomes do negócio.
22. ❌ Transaction com mais de 7 campos de estado — decompor a feature.
23. ❌ Domain conhecendo o tipo Transaction.
24. ❌ Pular a árvore de decisão da Fase 5.2 — declaração de padrão é obrigatória.

### Convenções de nomenclatura
25. ✅ `{Entidade}Response` único por entidade, vive em `Application/` (não em `Create/`).
26. ✅ Namespace de entidade contém `{Contexto}Context` para evitar colisão.
27. ✅ Métodos async sufixados com `Async`.
28. ✅ Interfaces prefixadas com `I`.
29. ✅ `Configure{Camada}()` para registro DI; `Use{Camada}Extensions()` para middleware.

### Documentação e comentário
30. ✅ `README.md` e `ARCHITECTURE.md` na raiz — **entregues junto com o código, nunca depois**.
    Solução sem os dois não está entregue.
31. ❌ Decisão, trade-off, histórico ou comparação com implementação anterior em **comentário de
    código** — isso vive no `ARCHITECTURE.md`. No código ficam só **contrato** (resumo de 1 linha
    em membro público) e **guarda contra regressão** (até 2 linhas, o que quebra, sem ponteiro).
32. ❌ Marca de severidade (🔴 ⚠️ 🟡 ✅ 📌) em comentário — quem escreve 🔴 está argumentando,
    não descrevendo.
33. ❌ Bloco de comentário acima de **5 linhas**. O teto é por bloco, não por proporção.
34. ✅ **Teste de arquitetura guardando 31–33**, gerado junto com o código. Regra sem guarda
    executável é intenção, e intenção não sobrevive à pressa.

---

## CHECKLIST DE GERAÇÃO

Antes de entregar a solução, confirme:

### Estrutura
- [ ] Projetos nomeados conforme tabela (HEXAGONAL-v2 §6)
- [ ] `Program.cs` em `Adapters/Inbound/API/` (multi) ou raiz (single)
- [ ] `appsettings.json` no projeto host

### Decisões de padrão
- [ ] Toda operação tem declaração de padrão (Fase 5.4)
- [ ] Caminho da árvore documentado para cada operação
- [ ] Nenhum sinal de alerta da Fase 5.5 presente

### Domain (ver GUIDELINE-DDD-v2)
- [ ] Entidades como `class`, ID imutável, sem setters anêmicos
- [ ] Value Objects imutáveis
- [ ] Aggregates pequenos, referências externas só por ID
- [ ] Domain Events nomeados no passado, despachados após persistência
- [ ] `Ports/Outbound/I{Entidade}Repository` no domínio
- [ ] Zero imports de framework no Domain

### Application
- [ ] `{Entidade}Transaction` apenas onde TXC se aplica
- [ ] Handler implementa Primary Port (TXC consolidado ou ALT-1 granular)
- [ ] `ApplicationExtensions.ConfigureApplication()` registra todos Handlers
- [ ] Result Pattern em todos os Handlers — sem exceptions de negócio

### Adapters (ver GUIDELINE-HEXAGONAL-v2)
- [ ] `ApiExtensions.cs` com `ConfigureAPI()` + `UseAPIExtensions()` (encapsula `app.Run()`)
- [ ] Endpoints com `Map{Entidade}Endpoints()`
- [ ] Validators com FluentValidation em `Adapters/Inbound/API/Validators/`
- [ ] `PersistenceExtensions.ConfigurePersistence()` por banco
- [ ] Repositórios em `Outbound/Persistence/SQL/{DB}/` ou `NoSQL/{DB}/`

### Qualidade
- [ ] `CancellationToken` em todos os métodos async de infraestrutura
- [ ] `using` / `await using` em todos `IDisposable` / `IAsyncDisposable`
- [ ] Sem abreviações (`customerId`, não `custId`)
- [ ] Sem `else` desnecessário (use guard clauses)
- [ ] JWT obrigatório em todos os endpoints

### Testes
- [ ] xUnit com `Assert` nativo para cada Handler (TXC e ALT-1/2/3) — **nunca FluentAssertions**
- [ ] Domain unit tests sem mocks (apenas `new()`)
- [ ] Integration tests com Testcontainers para Secondary Adapters
- [ ] Para TXC: testes asseguram estado intermediário do Transaction

### 🔴 Documentação — parte da entrega, não etapa posterior

**Solução sem `README.md` e `ARCHITECTURE.md` não está entregue.** Mesmo peso do build e dos
testes. Vale também para alteração: toda task que cria ou altera tipo público, função pública ou
decisão estrutural os atualiza **antes de fechar**.

- [ ] `README.md` na raiz — o que é · como rodar · estrutura (1 nível) · stack · links. **Nunca ADR
      nem detalhe classe-a-classe**
- [ ] `ARCHITECTURE.md` na raiz — índice · camadas · ADRs curtos (linka `decisions/` se a pasta
      existir, **sem duplicar**) · dicionário por módulo/classe relevante
- [ ] Variáveis de ambiente documentadas, **separando configuração de secret** — o que vai para
      `appsettings`/ConfigMap e o que vai para o cofre/Secret. Matriz por ambiente (Local ·
      Desenvolvimento · Produção) com o `Environment` padrão do .NET

### 🔴 Comentário no código — o quê fica, o porquê sai

Quem desenhou o código o entende sem comentário; quem não desenhou lê o `ARCHITECTURE.md`.

- [ ] **Contrato:** `/// <summary>` de 1 linha em membro público — o **quê**, nunca o **como**
- [ ] **Guarda contra regressão:** até 2 linhas, só quando editar aquela linha desfaz uma decisão.
      O que quebra, sem ponteiro (*"Não é record — ToString() exporia a ApiKey."*)
- [ ] **Nenhuma decisão, trade-off ou histórico em comentário** — vive no `ARCHITECTURE.md`
- [ ] **Nenhuma marca de severidade** (🔴 ⚠️ 🟡 ✅ 📌) em comentário — quem escreve 🔴 está
      argumentando, não descrevendo
- [ ] **Nenhum bloco de comentário acima de 5 linhas.** O teto é por bloco, não por proporção: um
      enum bem documentado é quase todo `summary` e está certo; o que denúncia ensaio é o bloco longo
- [ ] **Teste de arquitetura guardando as duas regras acima** — em `tests/.../Architecture/`, no
      mesmo lugar dos demais guardas estruturais

> 🔴 **Regra sem guarda executável é intenção, e intenção não sobrevive à pressa.** Gerar o teste
> junto com o código, não depois. Referência: `CommentBudgetTests` no `nq-sec-sdk` — dois testes,
> um recusa bloco acima do teto, outro recusa marca de severidade.

---

## INTEGRAÇÃO COM GUIDELINES

Esta skill é PRESCRITIVA mas remete aos guidelines para detalhe técnico:

| Pergunta do agente | Consultar |
|---|---|
| "Como modelar este Aggregate?" | `GUIDELINE-DDD-v2.md` §3 |
| "Onde fica está Secondary Port — Domain ou Application?" | `GUIDELINE-HEXAGONAL-v2.md` §2 |
| "Como nomear este Bounded Context?" | `GUIDELINE-CONTEXTOS-v2.md` Fase 3 |
| "Single ou Multi Project para este sistema?" | `GUIDELINE-CONTEXTOS-v2.md` §6 |
| "Como integrar com sistema externo?" | `GUIDELINE-HEXAGONAL-v2.md` §8 (ACL) |
| "Como o Transaction se relaciona com o Aggregate?" | `GUIDELINE-DDD-v2.md` §9 |
| "TXC viola Ports & Adapters?" | `GUIDELINE-HEXAGONAL-v2.md` §7 (não viola) |
| "Este comentário fica no código ou vai para o ARCHITECTURE.md?" | `references/comment-convention.md` |
| "Como escrevo o teste que guarda a convenção de comentário?" | `references/comment-convention.md` §O guarda executável |
| "Vou aplicar a convenção num repo já pronto — por onde começo?" | `references/comment-convention.md` §Retrofit |

---

## EXEMPLO COMPLETO — DECLARAÇÃO E GERAÇÃO

### Cenário do usuário
> "Criar API .NET para gerenciar Pedidos: Create com cálculo de total e validação de cliente,
> GetById, GetAll, Cancel com validação de prazo e notificação. PostgreSQL + Dapper."

### Output esperado do agente (cabeçalho antes do código)

```
═══════════════════════════════════════════════════════════════════
PROJETO: VendasService (Minimal API, SingleProject, PostgreSQL+Dapper)
BOUNDED CONTEXT: VendasContext
ENTIDADE: Pedido
═══════════════════════════════════════════════════════════════════

DECISÕES DE PADRÃO POR OPERAÇÃO:

1. Operação: Create
   Decisão de padrão: TXC
   Caminho da árvore: SIM (regras de cliente+pricing) → SIM (3+ etapas) → SIM (Entry+Domain+Infra) → TXC
   Razão: Cria pedido após validar cliente, calcular total e emitir evento — estado evolui em 3 fases.

2. Operação: Cancel
   Decisão de padrão: TXC
   Caminho da árvore: SIM (regra de prazo) → SIM (validação+persistência+notificação) → SIM (cruza camadas) → TXC
   Razão: Cancelamento valida prazo, atualiza aggregate e dispara notificação assíncrona.

3. Operação: GetById
   Decisão de padrão: ALT-1 QueryHandler
   Caminho da árvore: NÃO (sem regras) → SIM (leitura) → 1 fonte → ALT-1
   Razão: Busca por id com projeção direta. Sem regra, sem efeito colateral.

4. Operação: GetAll
   Decisão de padrão: ALT-1 QueryHandler
   Caminho da árvore: NÃO → SIM → 1 fonte → ALT-1
   Razão: Lista com filtros opcionais simples.

═══════════════════════════════════════════════════════════════════
GERAÇÃO DE CÓDIGO
═══════════════════════════════════════════════════════════════════

[árvore de arquivos]
[conteúdo de cada arquivo]
```

---

## COMPORTAMENTO ESPERADO DO AGENTE

1. **Leia esta skill INTEGRALMENTE antes de gerar qualquer código.**
2. **Conduza a entrevista das 7 fases.** Não pule.
3. **Para cada operação**, percorra a árvore de decisão (5.2) e declare o padrão (5.4).
4. **Gere a árvore de pastas** primeiro (visual em ASCII), depois os arquivos.
5. **Gere os arquivos em ordem:** Domain → Application → Adapters/Outbound → Adapters/Inbound → Program.cs.
6. **Pergunte antes de assumir** tecnologias não mencionadas (mensageria, cache, observabilidade).
7. **Não gere adapters não necessários** — deixe `// TODO: configurar Kafka` em vez de gerar lib que não foi pedida.
8. **Cada arquivo gerado deve compilar** — sem usings faltando.
9. **Gere testes unitários** para todos os Handlers (TXC e ALT-1/2/3).
10. **Se houver ambiguidade**, liste antes de gerar e proponha decisões.
11. **Após geração**, apresente o **checklist** preenchido para conferência do usuário.
12. 🔴 **Gere o que foi pedido — nada além.** Pedido de um endpoint devolve o endpoint, não o CRUD
    completo "já que estamos aqui". Não acrescente variante, alternativa ou caminho preventivo que
    ninguém pediu. Achado relevante fora do escopo: **cite em uma linha e siga**, não implemente.
13. 🔴 **Pergunta *ou/ou* exige resposta que decide.** Se você ofereceu duas opções mutuamente
    exclusivas e a resposta foi "sim", isso **não escolheu nada** — pergunte de novo, nomeando as
    opções. Prosseguir por suposição custa mais que a segunda pergunta.

---

## REFERÊNCIAS INTERNAS

- `references/stored-procedures.md` — Sub-padrões para SQL Server com SPs
- `references/ddd-patterns.md` — Detalhe de Aggregate, VO, Domain Events (complementar a GUIDELINE-DDD-v2)
- `references/worker-patterns.md` — `BackgroundService`, Polly, healthchecks, `IOptions<T>`
- `references/sdk-patterns.md` — Fluent Builder, `Result<T>`, `IServiceCollection` extension
- `references/comment-convention.md` — o quê fica no código, o porquê vai para o `ARCHITECTURE.md`; teste de arquitetura pronto e roteiro de retrofit

---

*Skill BKS .NET Solutions v2.0 — adoção do padrão TXC com alternativas YAGNI-aware*
