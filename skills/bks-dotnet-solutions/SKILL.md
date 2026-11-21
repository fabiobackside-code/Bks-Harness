---
name: bks-dotnet-solutions
version: 3.0
description: |
  Guia prescritivo para geração de soluções .NET completas com Arquitetura Hexagonal BKS e DDD,
  montadas pelas portas de entrada e de saída. Use SEMPRE que o usuário quiser criar, estruturar
  ou implementar qualquer solução .NET — Minimal API, Worker/Background Service ou SDK/Lib.

  Trigger: criar projeto .NET, hexagonal em .NET, portas e adapters, Worker com TCP ou HTTP,
  consumer Kafka ou RabbitMQ, TXC, transaction context, CRUD com Dapper ou EF Core,
  Stored Procedures, Single Project vs Multi Project, estrutura de pastas para projeto C#.

  A skill é OPINIONADA e PRESCRITIVA — recomenda ativamente, não apenas lista opções.
  A entrevista de 9 fases é obrigatória: tipo, forma (padrão direto ou TXC), portas de entrada
  e de saída; o agente NÃO PODE gerar pasta de porta que a entrevista não declarou.

trigger_keywords:
  - .net solution
  - hexagonal .net
  - minimal api
  - worker .net
  - sdk .net
  - portas e adapters
  - worker tcp
  - txc
  - transaction context
  - bks stack
  - dapper crud
  - stored procedure .net
  - single project vs multi project

related_guidelines:
  - ddd-tactic-guidelines.md           (bks-sdd — tático: Entities, VOs, Aggregates, Domain Services)
  - hexagonal-arch-guidelines.md       (bks-sdd — estrutural: Ports & Adapters, dependências)
  - ddd-bounded-contexts-guidelines.md (bks-sdd — estratégico: Bounded Contexts, Subdomain types)
  - txc-guidelines.md                  (bks-sdd — o modelo do TXC, quando o projeto o adota)
---

# bks-dotnet-solutions — Skill v3.0

> **Mudanças vs v2:** a estrutura sai das portas de entrada e de saída declaradas na entrevista.
> Duas formas, escolhidas por projeto: padrão direto (entrada → serviço → porta) ou TXC
> (`txc: "base"`, com a base em `references/txc-base.md`). Toda lista tem "outro", que vira Port.
> Sai a árvore TXC × ALT-1..4 e o Transaction mutável (`decisions/ADR-015` e `ADR-016` do kit).

---

## Regra zero — antes de gerar qualquer código

> **Esta regra é absoluta e não negociável.**

Você deve:

1. Conduzir a **entrevista estruturada (9 fases)**, sem pular fases mesmo que o usuário tenha dado pistas no prompt inicial. Cada fase é uma decisão consciente.
2. Gerar só o que a entrevista declarou: cada porta de entrada e de saída escolhida vira adapter; porta não declarada não gera pasta nem código.
3. Na fase 7, **declarar explicitamente** como cada operação será construída, conforme a forma do projeto (fase 2). A ausência da declaração é proibida.
4. Cumprir as **Restrições Absolutas** (seção final): qualquer violação invalida a geração.
5. Quando houver dúvida arquitetural, **pergunte ao usuário antes de implementar**. Tecnologia que não está nas listas entra como "outro": vira Port com o adapter a especificar, nunca uma biblioteca inventada.

---

## Entrevista estruturada — 9 fases

Toda lista termina em "outro". O "outro" vira Port com o adapter a especificar na especificação
da feature; a skill não escolhe biblioteca por conta própria. Trocar o adapter de uma porta depois
da construção inicial não toca o domínio.

### Fase 1 — Tipo de solução

```
Pergunta:
  Qual o tipo de solução?
  [A] Minimal API (REST)
  [B] Worker / Background Service — pode ter várias portas de entrada no mesmo processo
  [C] SDK / Biblioteca reutilizável — sem porta de entrada; a API pública é a da biblioteca
  [D] Outro — especificar (ex.: CLI, função serverless); a skill parte do tipo mais próximo entre
      A, B e C, diz qual escolheu e lista na especificação o que o tipo pedido exige além dele

Saída: {tipo_solucao}
```

### Fase 2 — Forma do projeto: Transaction Context (TXC) ou padrão direto

```
Leia o campo txc do .bks-profile.json. Declarado: [A]. Campo ausente: [B], sem perguntar.
Só sem o arquivo .bks-profile.json faça a pergunta abaixo.

Pergunta:
  O projeto adota o TXC (Transaction Context)?
  [A] Sim, txc: "base" — toda operação é transação registrada por código:
      entrada → sessão → pipeline [10] [20] [40] [50] → executor
  [B] Não — padrão direto: entrada → serviço → porta de saída; a regra mora no serviço

Recomendação (a confirmar com o usuário):
  - várias operações de escrita que pedem idempotência, auditoria e compensação → [A]
  - cadastro simples, integração sem regra, serviço de leitura, gateway de protocolo → [B]

Saída: {forma} — vale para o projeto inteiro; não há mistura entre as duas
```

O `txc: "motor"` (pacote do `bks-motor-sdk`) não é gerado por esta skill; é o caminho de migração
de um projeto `base`: trocar a base pelo pacote e escrever a procedure de cada transação.

### Fase 3 — Modo de projeto

```
Pergunta:
  SingleProject (1 csproj) ou MultiProject (Domain + Application + Adapters + Host)?
  Vale para as duas formas da fase 2.

Recomendação automática (a confirmar com o usuário):
  - 1-3 contextos coesos, time único, deploy junto → SingleProject
  - 4+ contextos OU times distintos OU regras de dependência via project reference → MultiProject

Critérios completos: guia ddd-bounded-contexts-guidelines.md da skill bks-sdd.

Saída: {modo_projeto}
```

### Fase 4 — Complexidade do domínio

```
Pergunta:
  O domínio tem regras de negócio ricas (validações, transições de estado, eventos)
  ou é predominantemente cadastro de leitura e escrita simples?

  [A] Domínio rico — usar Aggregates, Value Objects, Domain Events, Domain Services
  [B] Cadastro simples — entidades anêmicas com validação básica

Saída: {complexidade_dominio}
```

### Fase 5 — Portas de entrada (múltipla escolha)

Pule esta fase no SDK. Na Minimal API, o HTTP já vem marcado; pergunte se há outras.

```
Pergunta:
  Por onde as operações entram? Marque todas.
  [A] HTTP — Minimal API, ou Kestrel dentro do Worker
  [B] Servidor TCP
  [C] Consumer de fila — Kafka, RabbitMQ ou outro
  [D] Agendamento — execução periódica
  [E] gRPC
  [F] Outro — especificar

Para cada porta marcada:
  Autenticação? JWT | chave de API | certificado mútuo | outro | nenhuma
  "Nenhuma" exige rede fechada declarada (ex.: só a rede interna das agências alcança a porta).

Saída: {portas_entrada} = [{porta, tecnologia, autenticacao}]
```

### Fase 6 — Portas de saída (múltipla escolha)

```
Pergunta:
  Com o que a aplicação fala? Marque todas.
  [A] Banco relacional — SQL Server, PostgreSQL, Oracle, MySQL ou outro
      acesso: Dapper (preferência BKS) | Entity Framework Core | Stored Procedure | outro
      Stored Procedure: ver references/stored-procedures.md
  [B] Banco de documentos — MongoDB ou outro
  [C] Cache — Redis ou outro
  [D] Producer de fila — Kafka, RabbitMQ ou outro
  [E] Cliente HTTP
  [F] Cliente TCP
  [G] Cliente SOAP (web service XML)
  [H] Cliente gRPC
  [I] Outro — especificar
  Nenhuma marcada: puro processamento, sem adapter de saída.

Saída: {portas_saida} = [{porta, tecnologia, acesso}]
```

### Fase 7 — Contextos, entidades e operações

#### 7.1 — Listagem

```
Pergunta:
  Quais Bounded Contexts e quais entidades por contexto?
  Para cada entidade, quais operações? (cadastro padrão ou customizadas?)
  Por qual porta de entrada cada operação chega?

Output esperado:
  Contexto: Vendas
    Entidade: Pedido
      Operações: Create (HTTP), GetById (HTTP), Cancel (HTTP), Reprocessar (Agendamento)
    Entidade: ItemPedido (entidade interna do aggregate Pedido)
```

#### 7.2 — Declaração por operação

Antes de gerar o código, imprima uma linha por operação, conforme a forma da fase 2.

**Padrão direto:**

| Operação | Entrada | Serviço | Portas de saída | Razão |
|---|---|---|---|---|
| `Create` | HTTP | `PedidoService.CriarAsync` | banco relacional | grava o pedido com o desconto da categoria |
| `GetById` | HTTP | `PedidoService.ObterAsync` | banco relacional | consulta por número |

**TXC** (modelo em `txc-guidelines.md` da skill `bks-sdd`):

| Operação | Código | Executor | Etapas | Razão |
|---|---|---|---|---|
| `Create` | `PEDIDO.CRIAR` | transacional | `[10]` `[20]` `[40]` `[50]` | grava o pedido e notifica o cliente |
| `GetById` | `PEDIDO.OBTER` | consulta | `[40]` | consulta por número, sem escrita |
| `Reprocessar` | `PEDIDO.REPROCESSAR` | transacional, item a item | `[20]` `[40]` | o worker chama a sessão uma vez por pedido |

Regras da declaração no TXC:
- escrita → executor transacional, sempre com `[20]`;
- consulta, de uma fonte ou composta → executor de consulta, um por consulta;
- lote → item a item pela sessão, cada um com a própria chave de idempotência; uma transação só
  para o lote apenas se o requisito exigir atomicidade;
- utilitário técnico sem regra (reindexar, limpar cache) → fora do TXC, job ou comando simples.

### Fase 8 — Observabilidade

```
Pergunta:
  Para onde vão traces, métricas e logs?
  [A] Endpoint OTLP (OpenTelemetry)
  [B] Local apenas (console + Serilog)
  [C] Outro — especificar

Saída: {observabilidade}
```

### Fase 9 — Confirmação consolidada

```
Apresentar tabela final:
  Tipo solução:      {tipo_solucao}
  Forma:             {forma}
  Modo projeto:      {modo_projeto}
  Complexidade:      {complexidade_dominio}
  Portas de entrada: [porta · tecnologia · autenticação]
  Portas de saída:   [porta · tecnologia · acesso]
  Bounded Contexts:  [lista]
  Operações:         [tabela da fase 7.2]
  Observabilidade:   {observabilidade}

Aguardar "OK" do usuário antes de gerar código.
```

---

## Estruturas de pasta

A estrutura sai da entrevista. Cada porta de entrada (fase 5) e de saída (fase 6) escolhida vira
uma pasta `{Nome}Adapter/` com a sua `Extensions/` e um `Add{Nome}(this IServiceCollection,
IConfiguration)`. **Porta não escolhida não gera pasta.** O namespace é o caminho da pasta, com o
prefixo do serviço. Contrato, adapter mínimo e regras de recurso de cada porta:
`references/ports-catalog.md`.

| Porta da entrevista | Pasta |
|---|---|
| HTTP de entrada | `Adapters/Inbound/HttpAdapter/` (`Endpoints/`, `Extensions/`) |
| Servidor TCP | `Adapters/Inbound/TcpServerAdapter/` |
| Consumer de fila | `Adapters/Inbound/{Kafka\|RabbitMq\|Outro}ConsumerAdapter/` |
| Agendamento | `Adapters/Inbound/SchedulerAdapter/` |
| gRPC de entrada | `Adapters/Inbound/GrpcAdapter/` |
| Banco relacional ou de documentos | `Adapters/Outbound/{SqlServer\|Postgres\|Oracle\|MySql\|Mongo\|Outro}Adapter/` |
| Cache | `Adapters/Outbound/CacheAdapter/` |
| Producer de fila | `Adapters/Outbound/{Kafka\|RabbitMq\|Outro}ProducerAdapter/` |
| Cliente HTTP, TCP, SOAP (web service XML) ou gRPC | `Adapters/Outbound/{Sistema}{Http\|Tcp\|Soap\|Grpc}Adapter/` |
| "Outro" | `Adapters/{Inbound\|Outbound}/{Nome}Adapter/` com a Port; o adapter fica a especificar |
| Observabilidade (fase 8) | `Adapters/Outbound/ObservabilityAdapter/`, sempre |

### A) Padrão direto — projeto único

```
src/
├── {ServiceName}/                              ← Web SDK com HTTP de entrada; Worker SDK sem
│   ├── Adapters/
│   │   ├── Inbound/{Porta}Adapter/             ← só as portas da fase 5
│   │   └── Outbound/{Porta}Adapter/            ← só as portas da fase 6, mais Observability
│   ├── Domain/
│   │   ├── Core/
│   │   │   ├── Ports/                          ← I{Entidade}Service (Primary), I{Entidade}Repository e clientes (Secondary)
│   │   │   ├── Models/                         ← entidades, Value Objects, eventos; subpasta por contexto se houver mais de um
│   │   │   ├── Settings/                       ← uma classe de opções por adapter
│   │   │   └── Common/                         ← PipelineResult<T>, PipelineError; só System.*
│   │   └── Services/                           ← {Entidade}Service: a regra de negócio
│   └── main/
│       ├── Program.cs                          ← só chama ServiceConfiguration
│       └── ServiceConfiguration.cs             ← encadeia os Add{Nome} de cada adapter
└── {ServiceName}.Tests/
```

Fluxo: adapter de entrada → `I{Entidade}Service` → Ports de saída → adapter. Sem sessão, pipeline,
steps nem orquestrador. Interface só onde há fronteira (adapter, ou teste que precisa de
substituto); classe interna do domínio sem segunda implementação não ganha interface.

### B) TXC (`txc: "base"`) — projeto único

```
src/
├── {ServiceName}/
│   ├── Adapters/
│   │   ├── Inbound/{Porta}Adapter/             ← chama IBksSession.ExecuteAsync(code, input)
│   │   └── Outbound/{Porta}Adapter/            ← inclui a implementação de IBksIdempotencyStore no adapter de banco
│   ├── Application/
│   │   ├── Pipeline/                           ← a base Bks* (references/txc-base.md), gerada uma vez
│   │   └── {Contexto}/
│   │       ├── {Contexto}Codes.cs              ← catálogo de códigos: o contrato da aplicação
│   │       ├── {Contexto}Transactions.cs       ← AddBksTransaction / AddBksQuery por código
│   │       └── {Operacao}/
│   │           ├── {Operacao}Input.cs, {Operacao}Output.cs
│   │           ├── {Operacao}Envelope.cs
│   │           ├── {Operacao}Validation.cs     ← [10], só quando a operação tem
│   │           └── {Operacao}Executor.cs       ← transacional ou de consulta
│   ├── Domain/
│   │   ├── Core/{Ports, Models, Settings, Common}/   ← igual à A; Common traz PipelineResult<T>
│   │   └── {Contexto}/{Entidade}.cs ...        ← aggregates com a regra pura (Pedido.Criar)
│   └── main/{Program.cs, ServiceConfiguration.cs}
└── {ServiceName}.Tests/
```

Não existe `I{Entidade}Handler`, `I{Operacao}UseCase` nem `{Entidade}Service` com regra: a Primary
Port é a sessão, e o catálogo de códigos diz o que a aplicação oferece.

### C) Multi Project — as duas formas

```
src/
├── {ServiceName}.Domain/                       Domain.csproj — Core/ (e Services/ no direto)
├── {ServiceName}.Application/                  só no TXC — Pipeline/ e {Contexto}/; → ref Domain
├── {ServiceName}.Adapters.Inbound/             {Porta}Adapter/ por porta da fase 5; → ref Domain (e Application no TXC)
├── {ServiceName}.Adapters.Outbound/            {Porta}Adapter/ por porta da fase 6; → ref Domain (e Application no TXC)
├── {ServiceName}.Host/                         main/ — Program.cs e ServiceConfiguration; → ref todos
└── {ServiceName}.Tests/
```

> **Formato da solution:** toda solution .NET 10 é **`.slnx`**, o formato XML padrão do SDK 10.
> `dotnet new sln` sob o SDK 10 já gera `.slnx`. O `.sln` clássico fica para ferramenta sem
> suporte ao formato novo.

> **Biblioteca de asserção:** nunca FluentAssertions. A v8 passou a licença comercial paga (Xceed)
> e a v7.x é a última sob Apache 2.0. Use o `Assert` nativo do xUnit.

### D) Worker com várias entradas

O Worker hospeda várias portas de entrada no mesmo processo. Cada porta é um adapter próprio:

| Porta | Forma no host |
|---|---|
| HTTP | Kestrel: o projeto usa o Web SDK, e o `WebApplication` hospeda também os `BackgroundService` das outras portas |
| Servidor TCP | `BackgroundService` com o listener; um escopo de DI por conexão ou mensagem |
| Consumer | `BackgroundService` do consumer; um escopo por mensagem |
| Agendamento | `BackgroundService` com `PeriodicTimer`; um escopo por execução |

Todo adapter de entrada chama o mesmo destino: `I{Entidade}Service` no padrão direto,
`IBksSession` no TXC. Lote no TXC é item a item pela sessão. Detalhe de cada adapter de entrada:
`references/worker-patterns.md`.

### E) SDK / Biblioteca

Ver `references/sdk-patterns.md`. Resumo:
- Sem `Adapters/Inbound/` (não há host); a fase 5 é pulada.
- Expõe API pública via Fluent Builder.
- `IServiceCollection` extension para integração em hosts consumidores.

---

## Templates de código

Os templates 1 e 2 são do padrão direto; os 3 a 6, do TXC; o 7 vale para os dois. Gere só os da
forma declarada na fase 2.

### Template 1 — Padrão direto: Port e serviço

```csharp
// Domain/Core/Ports/IPedidoService.cs
namespace {ServiceName}.Domain.Core.Ports;

public interface IPedidoService
{
    Task<PipelineResult<CriarPedidoOutput>> CriarAsync(CriarPedidoInput input, CancellationToken ct);
    Task<PipelineResult<PedidoView>> ObterAsync(string numero, CancellationToken ct);
}
```

```csharp
// Domain/Services/PedidoService.cs
namespace {ServiceName}.Domain.Services;

public sealed class PedidoService(IClienteRepository clientes, IPedidoRepository pedidos) : IPedidoService
{
    public async Task<PipelineResult<CriarPedidoOutput>> CriarAsync(CriarPedidoInput input, CancellationToken ct)
    {
        var cliente = await clientes.GetByIdAsync(input.ClienteId, ct);
        if (cliente is null) return PedidoErrors.ClienteInexistente;

        var pedido = Pedido.Criar(cliente, input.Itens, cliente.Categoria.Desconto);
        if (!pedido.IsSuccess) return pedido.Errors;

        await pedidos.SaveAsync(pedido.Value!, ct);
        return new CriarPedidoOutput(pedido.Value!.Numero);
    }

    public async Task<PipelineResult<PedidoView>> ObterAsync(string numero, CancellationToken ct)
    {
        var pedido = await pedidos.FindByNumeroAsync(numero, ct);
        return pedido is null ? PedidoErrors.PedidoInexistente : PedidoView.From(pedido);
    }
}
```

### Template 2 — Padrão direto: endpoint

```csharp
// Adapters/Inbound/HttpAdapter/Endpoints/PedidoEndpoints.cs
public static class PedidoEndpoints
{
    public static IEndpointRouteBuilder MapPedidoEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/pedidos").RequireAuthorization();

        group.MapPost("/", async (CriarPedidoRequest req, IPedidoService service, CancellationToken ct) =>
            (await service.CriarAsync(req.ToInput(), ct)).ToHttpResult(o => $"/api/pedidos/{o.Numero}"));

        group.MapGet("/{numero}", async (string numero, IPedidoService service, CancellationToken ct) =>
            (await service.ObterAsync(numero, ct)).ToHttpResult());

        return app;
    }
}
```

`RequireAuthorization()` só quando a fase 5 declarou autenticação para o HTTP. A resposta é montada
no adapter (`ToHttpResult`), nunca no serviço.

### Template 3 — TXC: códigos, entrada e envelope

```csharp
// Application/Vendas/VendasCodes.cs
public static class VendasCodes
{
    public const string CriarPedido = "PEDIDO.CRIAR";
    public const string ObterPedido = "PEDIDO.OBTER";
}

// Application/Vendas/CriarPedido/CriarPedidoEnvelope.cs
public sealed record CriarPedidoInput(Guid ClienteId, IReadOnlyList<ItemInput> Itens, string IdempotencyKey);
public sealed record CriarPedidoOutput(string Numero);
public sealed record CriarPedidoEnvelope(BksTransactionSeed Seed, CriarPedidoInput Input);
```

### Template 4 — TXC: executor transacional

```csharp
// Application/Vendas/CriarPedido/CriarPedidoValidation.cs — [10], sem I/O
public sealed class CriarPedidoValidation : BksValidationStep<CriarPedidoInput>
{
    protected override PipelineResult Validate(CriarPedidoInput input) =>
        input.Itens.Count == 0 ? PipelineResult.Fail(PedidoErrors.SemItens) : PipelineResult.Ok();
}

// Application/Vendas/CriarPedido/CriarPedidoExecutor.cs
public sealed record ClienteLido(Cliente Cliente, decimal DescontoCategoria);

public sealed class CriarPedidoExecutor(IClienteRepository clientes, IPedidoRepository pedidos)
    : BksTransactionalExecutor<CriarPedidoEnvelope, ClienteLido, Pedido, CriarPedidoOutput>
{
    protected override async Task<PipelineResult<ClienteLido>> ValidateAsync(CriarPedidoEnvelope env, CancellationToken ct)
    {
        var cliente = await clientes.GetByIdAsync(env.Input.ClienteId, ct);
        return cliente is null ? PedidoErrors.ClienteInexistente : new ClienteLido(cliente, cliente.Categoria.Desconto);
    }

    protected override PipelineResult<Pedido> ApplyRule(CriarPedidoEnvelope env, ClienteLido lido) =>
        Pedido.Criar(lido.Cliente, env.Input.Itens, lido.DescontoCategoria);

    protected override async Task<PipelineResult<CriarPedidoOutput>> ExecuteAsync(
        CriarPedidoEnvelope env, Pedido pedido, CancellationToken ct)
    {
        await pedidos.SaveAsync(pedido, ct);
        return new CriarPedidoOutput(pedido.Numero);
    }
}
```

Duas fases (`ConfirmAsync` e `CancelAsync`) só quando um efeito externo decide; o modelo está no
`txc-guidelines.md` da skill `bks-sdd`, Seção 3.

### Template 5 — TXC: executor de consulta

```csharp
// Application/Vendas/ObterPedido/ObterPedidoExecutor.cs
public sealed record ObterPedidoInput(string Numero);
public sealed record ObterPedidoEnvelope(BksTransactionSeed Seed, ObterPedidoInput Input);

public sealed class ObterPedidoExecutor(IPedidoRepository pedidos)
    : BksQueryExecutor<ObterPedidoEnvelope, PedidoView>
{
    protected override async Task<PipelineResult<PedidoView>> ExecuteAsync(ObterPedidoEnvelope env, CancellationToken ct)
    {
        var pedido = await pedidos.FindByNumeroAsync(env.Input.Numero, ct);
        return pedido is null ? PedidoErrors.PedidoInexistente : PedidoView.From(pedido);
    }
}
```

Consulta composta de várias fontes é o mesmo executor, com várias Ports no construtor.

### Template 6 — TXC: registro e endpoint

```csharp
// Application/Vendas/VendasTransactions.cs
public static class VendasTransactions
{
    public static BksPipelineBuilder AddVendas(this BksPipelineBuilder pipeline) => pipeline
        .AddBksTransaction<CriarPedidoInput, CriarPedidoEnvelope, CriarPedidoOutput>(VendasCodes.CriarPedido, t => t
            .Envelope((seed, input) => new CriarPedidoEnvelope(seed, input))
            .Executor<CriarPedidoExecutor>()
            .Validation<CriarPedidoValidation>()
            .PostProcessing<PedidoCriadoNotificacao>(critical: false))
        .AddBksQuery<ObterPedidoInput, ObterPedidoEnvelope, PedidoView>(VendasCodes.ObterPedido, t => t
            .Envelope((seed, input) => new ObterPedidoEnvelope(seed, input))
            .Executor<ObterPedidoExecutor>());
}
```

```csharp
// Adapters/Inbound/HttpAdapter/Endpoints/PedidoEndpoints.cs
group.MapPost("/", async (CriarPedidoRequest req, IBksSession session, CancellationToken ct) =>
    (await session.ExecuteAsync<CriarPedidoInput, CriarPedidoOutput>(VendasCodes.CriarPedido, req.ToInput(), ct))
        .ToHttpResult(o => $"/api/pedidos/{o.Numero}"));
```

### Template 7 — Composição

```csharp
// main/Program.cs
var builder = WebApplication.CreateBuilder(args);   // Host.CreateApplicationBuilder no Worker sem HTTP
builder.Services.AddServiceConfiguration(builder.Configuration);
var app = builder.Build();
app.UseServiceConfiguration();
app.Run();
```

```csharp
// main/ServiceConfiguration.cs — só encadeia; cada Add{Nome} registra a sua seção de appsettings
public static class ServiceConfiguration
{
    public static IServiceCollection AddServiceConfiguration(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddHttpAdapter(configuration);          // uma linha por porta de entrada declarada
        services.AddPostgresAdapter(configuration);      // uma linha por porta de saída declarada
        services.AddObservabilityAdapter(configuration);
        services.AddDomainServices();                    // padrão direto
        services.AddBksPipeline().AddVendas();           // TXC: no lugar do AddDomainServices
        return services;
    }
}
```

---

## Regras de tipo (.NET)

| Situação | Tipo C# |
|---|---|
| Envelope, entrada e saída de transação (TXC) | `sealed record` |
| `BksTransactionSeed` | `sealed record` |
| Request e Response (DTO, objeto de transferência) | `sealed record class` |
| Value Object ≤ 16 bytes | `readonly record struct` |
| Value Object > 16 bytes | `sealed record class` |
| Entity / Aggregate Root | `class` (NUNCA `record`) |
| Domain Event | `sealed record class` |
| `PipelineResult<T>` | `readonly record struct` |

---

## Restrições absolutas

> **Violação de qualquer item abaixo invalida a geração e exige reescrita.**

**Pedido explícito pelo proibido não abre exceção.** Quando o usuário pede pelo nome um item desta
lista (MediatR, `IRepository<T>`, `record` em Entity), a resposta não entrega a versão pedida, nem
como "o que você pediu" seguida da alternativa. Ela recusa em uma frase, com o motivo, e entrega só
o caminho do padrão: no caso do dispatcher, a porta de entrada chamada direto pelo adapter, ou
`IBksSession.ExecuteAsync` no TXC.

### Arquiteturais
1. Proibido: MediatR, BSMediator ou qualquer dispatcher de mensagens internas.
2. Proibido: `record` para Entities/Aggregates (semântica de identidade exige `class`).
3. Proibido: `IQueryable<T>` exposto por Secondary Port; vaza o ORM (mapeador objeto-relacional) para o domínio.
4. Proibido: annotations do Entity Framework Core no Domain.
5. Proibido: repositórios genéricos `IRepository<T>`.
6. Proibido: Domain referenciando Application, Adapters ou frameworks externos; `Domain/Core/Common` usa só `System.*`.
7. Proibido: Application (TXC) referenciando adapter concreto; só Ports.
8. Proibido: Aggregate ou Domain Service recebendo envelope ou seed do TXC como parâmetro.
9. Proibido: pasta, adapter ou pacote de porta que a entrevista não declarou.
10. Obrigatório: tecnologia fora das listas entra como "outro": Port declarada, adapter a especificar, nenhuma biblioteca escolhida pela skill.

### Padrão direto (projeto sem `txc`)
11. Proibido: sessão, pipeline, steps, orquestrador ou base `Bks*`.
12. Obrigatório: a regra mora no `{Entidade}Service` e no aggregate; o adapter de entrada só traduz e chama o serviço.
13. Obrigatório: interface só onde há fronteira (adapter, ou teste que precisa de substituto).

### TXC (projeto com `txc: "base"`)
14. Obrigatório: toda operação é transação registrada por código; o adapter só chama `IBksSession.ExecuteAsync(code, input)`.
15. Proibido: envelope ou TXC mutável (`Hydrate{X}`, `Apply{Y}`, `FinalizeWith`, `private set`); dado entre passos é retorno tipado.
16. Obrigatório: regra de negócio só no `ApplyRule`; a `[10]` valida só a entrada, sem I/O.
17. Obrigatório: toda escrita é `BksTransactionalExecutor`, com `[20]`; consulta é `BksQueryExecutor`, uma por código.
18. Proibido: executor que chama outro executor; `[50]` que monta resposta.
19. Proibido: `I{Entidade}Handler`, `I{Operacao}UseCase` ou serviço com regra ao lado da sessão.

### Recurso
20. Obrigatório: as regras de "Regras que valem para toda porta" do `references/ports-catalog.md`.
21. Proibido: `.Result`, `.Wait()`, `.GetAwaiter().GetResult()`, `async void`.
22. Obrigatório: `Task<T>` nas Ports; `ValueTask<T>` só em hot path com medição que o justifique.
23. Obrigatório: `ConfigureAwait(false)` em todo `await` de biblioteca (SDK).
24. Obrigatório: log por `LoggerMessage` gerado na compilação; sem interpolação de string em log.
25. Obrigatório: `StringComparison.Ordinal` em comparações que não são linguísticas.

### Segurança
26. Obrigatório: a autenticação de cada porta de entrada é a declarada na fase 5.
27. Obrigatório, quando o HTTP declarou JWT: `AddAuthentication() + AddJwtBearer() + AddAuthorization()`, `RequireAuthorization()` em todos os `MapGroup` e endpoints (exceto health e swagger explicitamente liberados), e `UseAuthentication()` + `UseAuthorization()` depois do middleware de tracing.
28. Obrigatório, quando uma porta declarou "nenhuma": a rede fechada que a protege está escrita no `README.md`.

### Result Pattern
29. Proibido: `throw` para erro de negócio (entidade não encontrada, regra violada, validação). Use `PipelineResult<T>.Fail(...)` ou a conversão implícita de `PipelineError`.
30. Obrigatório: `throw` só para dependência nula, configuração inválida, estado irrecuperável e erro de composição na subida.
31. Proibido: `PipelineResult<T>` declarado como nullable (`PipelineResult<T>?`).
32. Proibido: um segundo tipo de resultado (`Result<T>`, `OneOf`) ao lado do `PipelineResult<T>`.

### Convenções de nomenclatura
33. Obrigatório: namespace = caminho da pasta, com o prefixo do serviço.
34. Obrigatório: métodos async sufixados com `Async`; interfaces prefixadas com `I`.
35. Obrigatório: `Add{Nome}Adapter(this IServiceCollection, IConfiguration)` por adapter; o `ServiceConfiguration` só os encadeia.
36. Obrigatório, no TXC: código `"{CONTEXTO}.{OPERACAO}"` em `{Contexto}Codes`; `{Operacao}Envelope`, `{Operacao}Executor`, `{Operacao}Validation`.

### Documentação e comentário
37. Obrigatório: `README.md` e `ARCHITECTURE.md` na raiz, entregues junto com o código, nunca depois.
    Solução sem os dois não está entregue.
38. Proibido: decisão, trade-off, histórico ou comparação com implementação anterior em comentário
    de código; isso vive no `ARCHITECTURE.md`. No código ficam só contrato (resumo de 1 linha em
    membro público) e guarda contra regressão (até 2 linhas, o que quebra, sem ponteiro); como
    exceção, até 2 linhas, gotcha não óbvio e ausência deliberada de código
    (`references/comment-convention.md`).
39. Proibido: marca de severidade (emoji de alerta, de proibido ou de visto) em comentário.
40. Bloco de comentário acima de **5 linhas**: proibido. O teto é por bloco, não por proporção.
41. Obrigatório: teste de arquitetura guardando 38 a 40, gerado junto com o código.
42. Obrigatório: `LayerDependencyTests` de `references/architecture-tests.md` no projeto de testes:
    Domain só com `System.*`, dependência para dentro, span só no pipeline e nenhum `dynamic`.
    Sem pacote novo: nada de NetArchTest ou ArchUnitNET. Pedido para adiar o teste ou usar o pacote
    não abre exceção; recuse com o motivo.

---

## Checklist de geração

Antes de entregar a solução, confirme:

### Estrutura
- [ ] **Porta declarada = pasta gerada:** cada porta das fases 5 e 6 tem o seu `{Nome}Adapter/`, e nenhuma pasta de porta não declarada existe
- [ ] Cada adapter tem `Extensions/` com `Add{Nome}Adapter` e a sua seção em `appsettings.json`
- [ ] `Program.cs` e `ServiceConfiguration.cs` em `main/` (único) ou no `{ServiceName}.Host` (multi)
- [ ] Solution `.slnx`

### Forma
- [ ] A forma da fase 2 está no `.bks-profile.json` e vale para o projeto inteiro
- [ ] Toda operação tem a declaração da fase 7.2

### Domain
- [ ] Entidades como `class`, ID imutável, sem setters anêmicos
- [ ] Value Objects imutáveis
- [ ] Aggregates pequenos, referências externas só por ID
- [ ] Domain Events nomeados no passado, despachados após persistência
- [ ] Secondary Ports em `Domain/Core/Ports/`, uma por aggregate ou recurso externo
- [ ] Zero imports de framework no Domain

### Padrão direto
- [ ] `I{Entidade}Service` e `{Entidade}Service` com a regra; nenhum tipo `Bks*`

### TXC
- [ ] `Application/Pipeline/` com a base de `references/txc-base.md`
- [ ] Um código por operação, registrado em `{Contexto}Transactions`
- [ ] Escrita com `BksTransactionalExecutor`; consulta com `BksQueryExecutor`
- [ ] `IBksIdempotencyStore` implementado no adapter de banco

### Qualidade
- [ ] `CancellationToken` em todos os métodos async
- [ ] `using` / `await using` em todos os `IDisposable` / `IAsyncDisposable`
- [ ] Sem abreviações (`customerId`, não `custId`)
- [ ] Sem `else` desnecessário (use guard clauses)
- [ ] Regras de recurso do `references/ports-catalog.md` conferidas porta a porta

### Testes
- [ ] xUnit com `Assert` nativo, nunca FluentAssertions
- [ ] Domain unit tests sem mocks (apenas `new()`)
- [ ] Padrão direto: um teste por método do serviço, com as Ports substituídas
- [ ] TXC: `ValidateAsync`, `ApplyRule` e `ExecuteAsync` de cada executor; replay da `[20]` devolve o primeiro resultado
- [ ] Teste de contrato para cada Port "outro"
- [ ] Integration tests com Testcontainers para os adapters de saída
- [ ] Teste de registro de DI: cada adapter declarado resolve

### Documentação — parte da entrega, não etapa posterior

**Solução sem `README.md` e `ARCHITECTURE.md` não está entregue.** Mesmo peso do build e dos
testes. Vale também para alteração: toda task que cria ou altera tipo público, função pública ou
decisão estrutural os atualiza **antes de fechar**.

- [ ] `README.md` na raiz: o que é, como rodar, estrutura (1 nível), stack, portas e autenticação
      de cada uma, links. Nunca ADR nem detalhe classe a classe
- [ ] `ARCHITECTURE.md` na raiz: índice, camadas, forma (direto ou TXC), ADRs curtos (linka
      `decisions/` se a pasta existir, sem duplicar), dicionário por módulo ou classe relevante
- [ ] Variáveis de ambiente documentadas, separando configuração de segredo: o que vai para
      `appsettings` ou ConfigMap e o que vai para o cofre ou Secret. Matriz por ambiente (Local,
      Desenvolvimento, Produção) com o `Environment` padrão do .NET

### Comentário no código — o quê fica, o porquê sai

Quem desenhou o código o entende sem comentário; quem não desenhou lê o `ARCHITECTURE.md`.

- [ ] **Contrato:** `/// <summary>` de 1 linha em membro público; o quê, nunca o como
- [ ] **Guarda contra regressão:** até 2 linhas, só quando editar aquela linha desfaz uma decisão.
      O que quebra, sem ponteiro (*"Não é record: ToString() exporia a ApiKey."*)
- [ ] **Nenhuma decisão, trade-off ou histórico em comentário**; vive no `ARCHITECTURE.md`
- [ ] **Nenhuma marca de severidade** em comentário
- [ ] **Nenhum bloco de comentário acima de 5 linhas.** Um enum bem documentado é quase todo
      `summary` e está certo; o que denuncia ensaio é o bloco longo
- [ ] **Teste de arquitetura guardando as duas regras acima**, em `src/{ServiceName}.Tests/Architecture/`
- [ ] **`LayerDependencyTests`** ao lado dele, de `references/architecture-tests.md`, verde no `dotnet test`

> **Regra sem guarda executável é intenção, e intenção não sobrevive à pressa.** Gere o teste
> junto com o código, não depois. Modelo: `references/comment-convention.md`, seção do guarda
> executável.

---

## Integração com os guias

Esta skill é prescritiva e remete aos guias da skill `bks-sdd` para o detalhe:

| Pergunta do agente | Consultar |
|---|---|
| "Como modelar este Aggregate?" | `ddd-tactic-guidelines.md` |
| "Onde fica esta Port, e como integrar com sistema externo?" | `hexagonal-arch-guidelines.md` |
| "Como nomear este Bounded Context? Único ou Multi Project?" | `ddd-bounded-contexts-guidelines.md` |
| "Como o executor, o envelope e a sessão se relacionam?" | `txc-guidelines.md` |
| "Qual o adapter mínimo e as regras de recurso desta porta?" | `references/ports-catalog.md` |
| "Este comentário fica no código ou vai para o ARCHITECTURE.md?" | `references/comment-convention.md` |
| "Vou aplicar a convenção de comentário num repo já pronto: por onde começo?" | `references/comment-convention.md`, seção de retrofit |

---

## Exemplo completo — declaração e geração

### Cenário do usuário
> "Worker .NET de autorização de pedidos. Os pedidos chegam por HTTP (portal, com JWT) e por TCP
> (terminais da loja, rede interna). Grava em PostgreSQL com Dapper. Antes de autorizar, consulta o
> antifraude do parceiro, que fala um protocolo proprietário. Sem TXC."

### Output esperado do agente (cabeçalho antes do código)

```
═══════════════════════════════════════════════════════════════════
PROJETO: AutorizacaoService (Worker, padrão direto, SingleProject)
BOUNDED CONTEXT: Vendas · ENTIDADE: Pedido
═══════════════════════════════════════════════════════════════════

PORTAS DE ENTRADA:
  HTTP (Kestrel no Worker, Web SDK)   autenticação: JWT
  Servidor TCP                         autenticação: nenhuma — rede interna da loja (no README)

PORTAS DE SAÍDA:
  Banco relacional: PostgreSQL + Dapper
  Outro: antifraude do parceiro (protocolo proprietário) → IAntifraudeClient, adapter a especificar
  Observabilidade: OTLP

OPERAÇÕES:
| Operação  | Entrada    | Serviço                        | Portas de saída          | Razão                                  |
|-----------|------------|--------------------------------|--------------------------|----------------------------------------|
| Autorizar | HTTP, TCP  | PedidoService.AutorizarAsync   | antifraude, PostgreSQL   | consulta o risco e grava a decisão     |
| Consultar | HTTP       | PedidoService.ObterAsync       | PostgreSQL               | consulta por número                    |

ESTRUTURA:
  Adapters/Inbound/HttpAdapter/        Adapters/Inbound/TcpServerAdapter/
  Adapters/Outbound/PostgresAdapter/   Adapters/Outbound/AntifraudeAdapter/   (vazio + teste de contrato)
  Adapters/Outbound/ObservabilityAdapter/
  Domain/Core/{Ports, Models, Settings, Common}/   Domain/Services/   main/

PACOTES (aguardam confirmação): Dapper, Npgsql, OpenTelemetry.Extensions.Hosting,
  OpenTelemetry.Exporter.OpenTelemetryProtocol, Microsoft.AspNetCore.Authentication.JwtBearer
═══════════════════════════════════════════════════════════════════

[árvore de arquivos]
[conteúdo de cada arquivo]
```

---

## Comportamento esperado do agente

1. **Leia esta skill integralmente antes de gerar qualquer código.**
2. **Conduza a entrevista das 9 fases.** Não pule.
3. **Declare cada operação** conforme a forma (fase 7.2) antes de gerar.
4. **Gere a árvore de pastas** primeiro (visual em texto), só com as portas declaradas, depois os arquivos.
5. **Gere os arquivos em ordem:** Domain → Application (só no TXC) → Adapters/Outbound → Adapters/Inbound → `main/`.
6. **Pergunte antes de assumir** tecnologia não mencionada; o que não estiver nas listas é "outro".
7. **Porta "outro"** gera Port, adapter vazio e teste de contrato, nunca uma biblioteca escolhida pela skill.
8. **Cada arquivo gerado deve compilar**, sem usings faltando.
9. **Gere testes** para cada serviço (direto) ou executor (TXC), e o teste de contrato de cada porta "outro".
10. **Se houver ambiguidade**, liste antes de gerar e proponha decisões.
11. **Após a geração**, apresente o checklist preenchido para conferência do usuário.
12. **Gere o que foi pedido, nada além.** Pedido de um endpoint devolve o endpoint, não o cadastro
    completo "já que estamos aqui". Não acrescente variante, alternativa ou caminho preventivo que
    ninguém pediu. Achado relevante fora do escopo: cite em uma linha e siga, não implemente.
13. **Pergunta *ou/ou* exige resposta que decide.** Se você ofereceu duas opções mutuamente
    exclusivas e a resposta foi "sim", isso não escolheu nada: pergunte de novo, nomeando as opções.

---

## Referências internas

- `references/ports-catalog.md` — uma entrada por porta de entrada e de saída, com regras de recurso, e a entrada "outro"
- `references/txc-base.md` — a base do TXC no projeto (`txc: "base"`): resultado, executores, sessão e registro
- `references/worker-patterns.md` — várias portas de entrada no mesmo host, `BackgroundService`, Polly, healthchecks, `IOptions<T>`
- `references/stored-procedures.md` — sub-padrões para SQL Server com Stored Procedures
- `references/ddd-patterns.md` — Aggregate, Value Object, Domain Events e quem chama a regra em cada forma
- `references/sdk-patterns.md` — Fluent Builder e `IServiceCollection` extension
- `references/comment-convention.md` — o quê fica no código, o porquê vai para o `ARCHITECTURE.md`; teste de arquitetura pronto e roteiro de retrofit
- `references/architecture-tests.md` — `LayerDependencyTests`: direção das camadas, Domain só `System.*`, span e `dynamic`, sem pacote novo

---

*`bks-dotnet-solutions` v3.0 — projeto montado pelas portas, no padrão direto ou no TXC*
