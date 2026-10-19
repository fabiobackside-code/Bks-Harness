# Padrões para SDKs e Bibliotecas

## Princípios

- Zero dependência de framework de aplicação no Core do SDK
- Interfaces públicas enxutas; implementações `internal sealed`
- `ConfigureAwait(false)` em **todos** os awaits — biblioteca não sabe o contexto do caller
- Versionamento semântico + XML summary em toda API pública

## Fluent Builder Pattern

```csharp
// Ponto de entrada público da biblioteca
public sealed class MeuSdkBuilder
{
    private string _apiKey = string.Empty;
    private TimeSpan _timeout = TimeSpan.FromSeconds(30);
    private Uri? _baseUrl;

    public MeuSdkBuilder WithApiKey(string apiKey)
    {
        _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
        return this;
    }

    public MeuSdkBuilder WithTimeout(TimeSpan timeout)
    {
        _timeout = timeout;
        return this;
    }

    public MeuSdkBuilder WithBaseUrl(Uri baseUrl)
    {
        _baseUrl = baseUrl;
        return this;
    }

    public IMeuSdk Build()
    {
        if (string.IsNullOrWhiteSpace(_apiKey))
            throw new InvalidOperationException("ApiKey é obrigatória");

        return new MeuSdkImpl(_apiKey, _timeout, _baseUrl ?? DefaultUrl);
    }

    private static readonly Uri DefaultUrl = new("https://api.example.com");
}

// Uso:
var sdk = new MeuSdkBuilder()
    .WithApiKey("minha-chave")
    .WithTimeout(TimeSpan.FromSeconds(60))
    .Build();
```

## IServiceCollection Extension

```csharp
// Ponto de entrada para DI em aplicações ASP.NET Core
public static class MeuSdkExtensions
{
    /// <summary>Registra o MeuSdk no container de DI.</summary>
    public static IServiceCollection AddMeuSdk(
        this IServiceCollection services,
        Action<MeuSdkOptions> configure)
    {
        services.Configure(configure);
        services.AddSingleton<IMeuSdk, MeuSdkImpl>();
        return services;
    }
}
```

## Result<T> em vez de Exceptions

```csharp
// Resultado de operações — nunca exceptions para fluxo de negócio
public readonly record struct Result<T>
{
    public T? Value { get; }
    public string? Error { get; }
    public bool IsSuccess { get; }

    private Result(T? value, string? error, bool isSuccess)
        => (Value, Error, IsSuccess) = (value, error, isSuccess);

    public static Result<T> Ok(T value) => new(value, null, true);
    public static Result<T> Fail(string error) => new(default, error, false);

    public TOut Match<TOut>(Func<T, TOut> onSuccess, Func<string, TOut> onFailure)
        => IsSuccess ? onSuccess(Value!) : onFailure(Error!);
}
```

## ConfigureAwait(false) — Obrigatório em Libraries

```csharp
// CORRETO — evita deadlocks em contextos síncronos (WinForms, ASP.NET Classic)
public async Task<Result<DadosResponse>> BuscarAsync(string id, CancellationToken ct)
{
    var response = await _httpClient.GetAsync($"/dados/{id}", ct).ConfigureAwait(false);

    if (!response.IsSuccessStatusCode)
        return Result<DadosResponse>.Fail($"HTTP {(int)response.StatusCode}");

    var content = await response.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
    var dados = JsonSerializer.Deserialize<DadosResponse>(content, _jsonOptions);

    return dados is not null
        ? Result<DadosResponse>.Ok(dados)
        : Result<DadosResponse>.Fail("Falha ao desserializar resposta");
}
```

## Estrutura de Projeto SDK

```
MeuSdk/
├── MeuSdk.csproj         ← sem referências a framework de aplicação
├── IMeuSdk.cs            ← interface pública
├── MeuSdkBuilder.cs      ← builder público
├── MeuSdkExtensions.cs   ← extension para IServiceCollection
├── MeuSdkOptions.cs      ← configuração pública
├── Internal/
│   ├── MeuSdkImpl.cs     ← internal sealed
│   └── HttpClient/
│       └── MeuSdkHttpClient.cs  ← internal sealed
└── Models/
    ├── DadosResponse.cs
    └── Result.cs
```
