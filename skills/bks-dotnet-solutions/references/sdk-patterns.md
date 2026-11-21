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

        if (_baseUrl is null)
            throw new InvalidOperationException("BaseUrl é obrigatória");

        return new MeuSdkImpl(_apiKey, _timeout, _baseUrl);
    }

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

## PipelineResult<T> em vez de exceção

O SDK usa o mesmo `PipelineResult<T>` e `PipelineError` das soluções (definição em
`references/txc-base.md`, seção "Resultado"), em `Models/PipelineResult.cs`. Um estilo de erro só:
nada de `Result<T>` próprio ao lado dele.

## ConfigureAwait(false) — Obrigatório em Libraries

```csharp
// CORRETO — evita deadlocks em contextos síncronos (WinForms, ASP.NET Classic)
public async Task<PipelineResult<DadosResponse>> BuscarAsync(string id, CancellationToken ct)
{
    var response = await _httpClient.GetAsync($"/dados/{id}", ct).ConfigureAwait(false);

    if (!response.IsSuccessStatusCode)
        return new PipelineError("sdk.http", $"HTTP {(int)response.StatusCode}");

    var content = await response.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
    var dados = JsonSerializer.Deserialize<DadosResponse>(content, _jsonOptions);

    return dados is not null
        ? dados
        : new PipelineError("sdk.desserializacao", "Falha ao desserializar resposta");
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
    └── PipelineResult.cs
```
