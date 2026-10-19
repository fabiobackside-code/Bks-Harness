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

## Configuração via IOptions<T>

```csharp
// Core/Common/Configuration/WorkerSettings.cs
public sealed class WorkerSettings
{
    public TimeSpan Intervalo { get; init; } = TimeSpan.FromSeconds(30);
    public int MaxTentativas { get; init; } = 3;

    // Validação na startup — falha rápido em vez de falhar em runtime
    public static void Validate(WorkerSettings s)
    {
        if (s.Intervalo <= TimeSpan.Zero)
            throw new ArgumentException("Intervalo deve ser positivo");
    }
}

// Program.cs
builder.Services
    .AddOptions<WorkerSettings>()
    .BindConfiguration("Worker")
    .Validate(WorkerSettings.Validate)
    .ValidateOnStart();
```

## Retry com Polly

```csharp
// Infrastructure/DependencyInjection.cs
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
