# Padrões para Workers e Background Services

## Estrutura Base

```csharp
public sealed class MeuWorker(
    ILogger<MeuWorker> logger,
    IMeuDomainService service,
    IOptions<WorkerSettings> settings) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        logger.LogInformation("Worker iniciado em {Timestamp}", DateTime.UtcNow);

        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessarCicloAsync(stoppingToken);
            await Task.Delay(settings.Value.Intervalo, stoppingToken);
        }
    }

    private async Task ProcessarCicloAsync(CancellationToken ct)
    {
        try
        {
            await service.ProcessarAsync(ct);
        }
        catch (OperationCanceledException)
        {
            // cancelamento é esperado — não logar como erro
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Erro ao processar ciclo em {Timestamp}", DateTime.UtcNow);
        }
    }
}
```

**Regras:**
- `CancellationToken` propagado em todos os métodos async
- Separação entre lógica do worker (ciclo) e lógica de domínio (service)
- `OperationCanceledException` tratado separadamente — não é erro

## Várias portas de entrada no mesmo host

Cada porta de entrada declarada na fase 5 é um adapter próprio em `Adapters/Inbound/`. Com HTTP
entre elas, o projeto usa o Web SDK e o `WebApplication` hospeda também os `BackgroundService` das
outras portas. Todo adapter abre um escopo de DI por mensagem e chama o mesmo destino: o serviço no
padrão direto, a sessão no TXC (Transaction Context).

```csharp
// main/Program.cs — HTTP, TCP e agendamento no mesmo processo
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpAdapter(builder.Configuration);
builder.Services.AddTcpServerAdapter(builder.Configuration);    // registra TcpServerService
builder.Services.AddSchedulerAdapter(builder.Configuration);    // registra ReprocessamentoJob
var app = builder.Build();
app.MapPedidoEndpoints();
app.Run();
```

```csharp
// Adapters/Inbound/TcpServerAdapter/TcpServerService.cs
public sealed partial class TcpServerService(
    IServiceScopeFactory scopes, IOptions<TcpServerSettings> settings, ILogger<TcpServerService> logger)
    : BackgroundService
{
    private readonly SemaphoreSlim _conexoes = new(settings.Value.ConexoesMaximas);
    private readonly List<Task> _atendimentos = [];

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var listener = new TcpListener(IPAddress.Any, settings.Value.Porta);
        listener.Start();
        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                await _conexoes.WaitAsync(stoppingToken);
                var client = await listener.AcceptTcpClientAsync(stoppingToken);
                _atendimentos.RemoveAll(t => t.IsCompleted);
                _atendimentos.Add(AtenderAsync(client, stoppingToken));
            }
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { }
        await Task.WhenAll(_atendimentos);
    }

    private async Task AtenderAsync(TcpClient client, CancellationToken ct)
    {
        try
        {
            using (client)
            await using (var scope = scopes.CreateAsyncScope())
            {
                var stream = client.GetStream();
                var mensagem = await TcpFraming.ReadAsync(stream, ct);
                var service = scope.ServiceProvider.GetRequiredService<IPedidoService>();
                var resultado = await service.ProcessarAsync(mensagem, ct);
                await TcpFraming.WriteAsync(stream, resultado, ct);
            }
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            LogFalhaConexao(logger, ex);
        }
        finally
        {
            _conexoes.Release();
        }
    }

    [LoggerMessage(Level = LogLevel.Error, Message = "Falha ao atender conexão TCP")]
    private static partial void LogFalhaConexao(ILogger logger, Exception ex);
}
```

O enquadramento da mensagem (`TcpFraming`) é do protocolo de cada projeto; a skill não o inventa.
No TXC, o adapter preenche o `BksCallContext` do escopo e chama
`IBksSession.ExecuteAsync(code, input)` no lugar do serviço.

```csharp
// Adapters/Inbound/SchedulerAdapter/ReprocessamentoJob.cs — lote item a item no TXC
public sealed class ReprocessamentoJob(IServiceScopeFactory scopes, IOptions<SchedulerSettings> settings)
    : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(settings.Value.Intervalo);
        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            await using var scope = scopes.CreateAsyncScope();
            var pendentes = scope.ServiceProvider.GetRequiredService<IPedidoRepository>();
            var lote = $"reprocessar:{DateTime.UtcNow:yyyyMMddHHmm}";
            foreach (var p in await pendentes.ListarPendentesAsync(stoppingToken))
            {
                await using var item = scopes.CreateAsyncScope();
                var session = item.ServiceProvider.GetRequiredService<IBksSession>();
                await session.ExecuteAsync<ReprocessarInput, ReprocessarOutput>(
                    VendasCodes.Reprocessar, new ReprocessarInput(p.Id, $"{lote}:{p.Id}"), stoppingToken);
            }
        }
    }
}
```

Cada item tem a própria chave de idempotência: o reinício pula o que já foi feito, e a falha de um
item não derruba os outros.

## Configuração via IOptions<T>

```csharp
// Core/Common/Configuration/WorkerSettings.cs
public sealed class WorkerSettings
{
    public TimeSpan Intervalo { get; init; } = TimeSpan.FromSeconds(30);
    public int MaxTentativas { get; init; } = 3;

    // Validação na startup — falha rápido em vez de falhar em runtime
    public static bool IsValid(WorkerSettings s) => s.Intervalo > TimeSpan.Zero && s.MaxTentativas > 0;
}

// Program.cs
builder.Services
    .AddOptions<WorkerSettings>()
    .BindConfiguration("Worker")
    .Validate(WorkerSettings.IsValid, "Worker: Intervalo e MaxTentativas devem ser positivos")
    .ValidateOnStart();
```

## Retry com Polly

```csharp
// Adapters/Outbound/{Porta}Adapter/ — Add{Porta}, encadeado em main/ServiceConfiguration.cs
builder.Services
    .AddHttpClient<IExternalApi, ExternalApiAdapter>()
    .AddStandardResilienceHandler();  // .NET Resilience Extensions (Polly 8+)

// ou com política customizada
builder.Services
    .AddResiliencePipeline("meu-pipeline", pipeline =>
    {
        pipeline.AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(2),
            BackoffType = DelayBackoffType.Exponential,
            UseJitter = true
        });
    });
```

## Health Checks

```csharp
// Program.cs
builder.Services
    .AddHealthChecks()
    .AddCheck("worker-live", () => HealthCheckResult.Healthy())
    .AddNpgsql(connectionString, name: "database");  // ou AddSqlServer

app.MapHealthChecks("/health/live",  new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = c => c.Name != "worker-live" });
```
