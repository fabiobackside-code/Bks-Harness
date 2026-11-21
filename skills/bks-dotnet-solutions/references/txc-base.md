# Base Transaction Context (TXC) no projeto — `txc: "base"`

Gerada uma vez em `Application/Pipeline/`, com o namespace do projeto. O modelo é o do
`txc-guidelines.md` da skill `bks-sdd`; aqui está o contrato em C#. O `PipelineResult<T>` mora em
`Domain/Core/Common/`, porque o aggregate também o devolve.

## Resultado — `Domain/Core/Common/`

```csharp
public sealed record PipelineError(string Code, string Message);

public readonly record struct PipelineResult(bool IsSuccess, IReadOnlyList<PipelineError> Errors)
{
    public static PipelineResult Ok() => new(true, []);
    public static PipelineResult Fail(params PipelineError[] errors) => new(false, errors);
    public static PipelineResult<T> Fail<T>(params PipelineError[] errors) => PipelineResult<T>.Fail(errors);
}

public readonly record struct PipelineResult<T>(bool IsSuccess, T? Value, IReadOnlyList<PipelineError> Errors)
{
    public static PipelineResult<T> Ok(T value) => new(true, value, []);
    public static PipelineResult<T> Fail(params PipelineError[] errors) => new(false, default, errors);
    public static PipelineResult<T> Fail(IReadOnlyList<PipelineError> errors) => new(false, default, errors);

    public static implicit operator PipelineResult<T>(T value) => Ok(value);
    public static implicit operator PipelineResult<T>(PipelineError error) => Fail(error);
}
```

## TXC e chamada — `Application/Pipeline/`

```csharp
/// <summary>Identidade da execução; somente leitura, criada pela sessão.</summary>
public sealed record BksTransactionSeed(
    string Code, Guid CorrelationId, string? UserId, string? TenantId, string? TraceId, string? IdempotencyKey);

/// <summary>Contexto da chamada, preenchido pelo adapter de entrada no escopo da requisição ou mensagem.</summary>
public sealed class BksCallContext
{
    public Guid CorrelationId { get; set; } = Guid.NewGuid();
    public string? UserId { get; set; }
    public string? TenantId { get; set; }
}

/// <summary>Entrada que grava declara a própria chave de idempotência.</summary>
public interface IBksIdempotentInput
{
    string IdempotencyKey { get; }
}

/// <summary>A Primary Port da aplicação.</summary>
public interface IBksSession
{
    Task<PipelineResult<TOut>> ExecuteAsync<TIn, TOut>(string code, TIn input, CancellationToken ct = default);
}
```

O `BksCallContext` é registrado como `Scoped`. O adapter HTTP o preenche num middleware; os
adapters TCP, de consumer e de agendamento abrem um escopo por mensagem e o preenchem antes de
chamar a sessão. Nada de `AsyncLocal`.

## Etapas e executores

```csharp
/// <summary>[10] Validação pura da entrada, sem I/O.</summary>
public abstract class BksValidationStep<TIn>
{
    protected abstract PipelineResult Validate(TIn input);

    internal PipelineResult Run(TIn input) => Validate(input);
}

/// <summary>[50] Conclusão ou difusão; roda em sucesso e em falha, não monta resposta.</summary>
public abstract class BksPostProcessingStep<TEnvelope, TOut>
{
    protected abstract Task RunAsync(TEnvelope envelope, PipelineResult<TOut> result, CancellationToken ct);

    internal Task InvokeAsync(TEnvelope envelope, PipelineResult<TOut> result, CancellationToken ct) =>
        RunAsync(envelope, result, ct);
}

/// <summary>[40] Executor que grava: ler, decidir, gravar, confirmar ou compensar.</summary>
public abstract class BksTransactionalExecutor<TEnvelope, TValidation, TDecision, TOut>
{
    protected virtual Task<PipelineResult<TValidation>> ValidateAsync(TEnvelope envelope, CancellationToken ct) =>
        Task.FromResult(PipelineResult<TValidation>.Ok(default!));

    protected abstract PipelineResult<TDecision> ApplyRule(TEnvelope envelope, TValidation validation);

    protected abstract Task<PipelineResult<TOut>> ExecuteAsync(TEnvelope envelope, TDecision decision, CancellationToken ct);

    protected virtual Task<PipelineResult> ConfirmAsync(TEnvelope envelope, CancellationToken ct) =>
        Task.FromResult(PipelineResult.Ok());

    protected virtual Task CancelAsync(TEnvelope envelope, CancellationToken ct) => Task.CompletedTask;

    /// <summary>Compensação pedida pela sessão quando a [50] crítica falha depois da gravação.</summary>
    internal Task CompensateAsync(TEnvelope envelope, CancellationToken ct) => CancelAsync(envelope, ct);

    internal async Task<PipelineResult<TOut>> RunAsync(TEnvelope envelope, CancellationToken ct)
    {
        var validation = await ValidateAsync(envelope, ct);
        if (!validation.IsSuccess) return PipelineResult<TOut>.Fail(validation.Errors);

        var decision = ApplyRule(envelope, validation.Value!);
        if (!decision.IsSuccess) return PipelineResult<TOut>.Fail(decision.Errors);

        var written = await ExecuteAsync(envelope, decision.Value!, ct);
        if (!written.IsSuccess) return written;

        try
        {
            var confirmed = await ConfirmAsync(envelope, ct);
            if (confirmed.IsSuccess) return written;
            await CancelAsync(envelope, ct);
            return PipelineResult<TOut>.Fail(confirmed.Errors);
        }
        catch
        {
            await CancelAsync(envelope, ct);
            throw;
        }
    }
}

/// <summary>[40] Executor de consulta: lê e devolve; sem [20], sem gravar.</summary>
public abstract class BksQueryExecutor<TEnvelope, TOut>
{
    protected abstract Task<PipelineResult<TOut>> ExecuteAsync(TEnvelope envelope, CancellationToken ct);

    internal Task<PipelineResult<TOut>> RunAsync(TEnvelope envelope, CancellationToken ct) => ExecuteAsync(envelope, ct);
}

/// <summary>Resultado da busca da [20]: achou ou não, e o que a primeira execução devolveu.</summary>
public readonly record struct BksIdempotencyHit<TOut>(bool Found, PipelineResult<TOut> Result);

/// <summary>Port da [20]; o projeto implementa no adapter de banco.</summary>
public interface IBksIdempotencyStore
{
    Task<BksIdempotencyHit<TOut>> FindAsync<TOut>(string code, string key, CancellationToken ct);
    Task SaveAsync<TOut>(string code, string key, PipelineResult<TOut> result, CancellationToken ct);
}
```

## Registro

```csharp
services.AddBksPipeline()                                   // sessão, contexto da chamada, ActivitySource
    .AddBksTransaction<TIn, TEnvelope, TOut>(code, t => t
        .Envelope((seed, input) => new TEnvelope(seed, input))   // fábrica pura
        .Executor<TExecutor>()                                   // BksTransactionalExecutor
        .Validation<TValidationStep>()                           // opcional
        .PostProcessing<TPostStep>(critical: false))             // opcional
    .AddBksQuery<TIn, TEnvelope, TOut>(code, t => t
        .Envelope((seed, input) => new TEnvelope(seed, input))
        .Executor<TQueryExecutor>());                            // BksQueryExecutor
```

O `AddBksTransaction` exige `TIn : IBksIdempotentInput`. Código repetido, envelope ou executor
ausente recusam no `Build` do host com exceção de composição: é erro de programação, não de negócio.
Executor e etapas são resolvidos por tipo, no escopo da sessão.

## O que a sessão faz

```
ExecuteAsync(code, input)
  1. acha o registro do código; seed = (code, CallContext, Activity.Current?.TraceId, chave da entrada)
  2. envelope = fábrica(seed, input)
  3. [10] Validate(input)                          falha → devolve, sem [50]
  4. [20] só no transacional: FindAsync(code, key)  Found → devolve o Result gravado, sem [50]
  5. [40] RunAsync / ExecuteAsync do executor
  6. [50] crítica: antes da resposta; falha depois da [40] gravar → CompensateAsync e devolve o erro
  7. [20] só no transacional e sem compensação: SaveAsync(code, key, resultado)
  8. [50] não crítica: depois da resposta, a falha fica no span e não muda o resultado
```

Cada etapa abre o span `step.{ordem}` no `ActivitySource` do projeto, com o código como tag, e
registra a exceção técnica no span. Exceção que escapa do executor vira `PipelineResult` com um
`PipelineError` técnico; exceção de negócio não existe.

A base grava a chave de idempotência depois da `[40]`. Quando a escrita e a chave precisam ser
atômicas, o adapter de banco implementa as duas na mesma transação de banco.
