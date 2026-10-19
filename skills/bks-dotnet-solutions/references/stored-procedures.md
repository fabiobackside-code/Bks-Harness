# Repositórios para Stored Procedures

## Sub-padrão A — Parâmetros Tipados

Cada SP tem seus parâmetros explicitamente declarados via `DynamicParameters`. Use este padrão quando a SP tem um conjunto definido de parâmetros de entrada e saída.

```csharp
public async Task<SpResult> ExecuteAsync(SpInput input, CancellationToken ct)
{
    using var activity = Activity.Current?.Source.StartActivity("Repository - sp_nome");
    using var conn = _connectionFactory.CreateConnection();

    var p = new DynamicParameters();
    // Parâmetros de entrada
    p.Add("@CodigoEntidade", input.CodigoEntidade);
    p.Add("@Valor",          input.Valor);
    // Parâmetros de saída — size SEMPRE explícito
    p.Add("@Retorno",  dbType: DbType.Int32,  direction: ParameterDirection.Output);
    p.Add("@Mensagem", dbType: DbType.String, direction: ParameterDirection.Output, size: 500);

    await conn.ExecuteAsync("sp_nome", p,
        commandTimeout: _dbSettings.CommandTimeout,
        commandType: CommandType.StoredProcedure);

    return new SpResult(
        Retorno:  p.Get<int>("@Retorno"),
        Mensagem: p.Get<string>("@Mensagem"));
}
```

**Regras:**
- `ParameterDirection.Output` com `size` explícito em todos os parâmetros de saída
- Para `varchar(max)` de saída: `size: -1`
- Nunca omitir o `commandType: CommandType.StoredProcedure`

---

## Sub-padrão B — Contrato JSON (mensagem_in / mensagem_out)

A SP recebe um único `varchar` com JSON serializado (`mensagem_in`) e retorna um único `varchar` com JSON serializado (`mensagem_out`).

```csharp
public async Task<TResponse> ExecuteAsync(TInput input, CancellationToken ct)
{
    using var activity = Activity.Current?.Source.StartActivity("Repository - sp_nome");
    using var conn = _connectionFactory.CreateConnection();

    var p = new DynamicParameters();
    p.Add("@mensagem_in",  JsonSerializer.Serialize(input, _jsonOptions));
    p.Add("@mensagem_out", dbType: DbType.String, direction: ParameterDirection.Output, size: -1); // -1 = MAX

    await conn.ExecuteAsync("sp_nome", p,
        commandTimeout: _dbSettings.CommandTimeout,
        commandType: CommandType.StoredProcedure);

    var raw = p.Get<string>("@mensagem_out");

    if (string.IsNullOrWhiteSpace(raw))
        throw new InvalidOperationException("SP retornou mensagem_out vazia");

    var response = JsonSerializer.Deserialize<TResponse>(raw, _jsonOptions)
        ?? throw new InvalidOperationException("Falha ao desserializar mensagem_out");

    return response;
}
```

**Regras críticas:**
- `size: -1` em parâmetros `varchar(max)` de saída — nunca omitir
- Validar `mensagem_out` antes de desserializar
- `JsonSerializerOptions` configurado na DI com `CamelCase` e `IgnoreNullValues` — **nunca** instanciar por chamada (alocação desnecessária)
- Se o contrato da SP inclui envelope de status (`código`/`mensagem`), desserializar para tipo intermediário de erro antes de mapear

---

## Connection Factory

```csharp
// Domain/Core/Ports/Outbound/IDbConnectionFactory.cs
public interface IDbConnectionFactory
{
    IDbConnection CreateConnection();
}

// Infrastructure — SQL Server
public sealed class SqlServerConnectionFactory : IDbConnectionFactory
{
    private readonly string _connectionString;
    public SqlServerConnectionFactory(IConfiguration cfg)
        => _connectionString = cfg.GetConnectionString("Default")!;
    public IDbConnection CreateConnection() => new SqlConnection(_connectionString);
}

// Infrastructure — PostgreSQL
public sealed class PostgreSqlConnectionFactory : IDbConnectionFactory
{
    private readonly string _connectionString;
    public PostgreSqlConnectionFactory(IConfiguration cfg)
        => _connectionString = cfg.GetConnectionString("Default")!;
    public IDbConnection CreateConnection() => new NpgsqlConnection(_connectionString);
}
```

---

## Nomenclatura para SPs

| Elemento | Padrão | Exemplo |
|---|---|---|
| Transaction | `Transaction{NomeSP}` | `TransactionBloqueioSaldo` |
| UseCase Port | `I{NomeSP}UseCase` | `IBloqueioSaldoUseCase` |
| UseCase impl | `{NomeSP}UseCase` | `BloqueioSaldoUseCase` |
| Validation Step | `{NomeSP}ValidationStep` | `BloqueioSaldoValidationStep` |
| Processing Step | `{NomeSP}ProcessingStep` | `BloqueioSaldoProcessingStep` |
| Repository Port | `I{Grupo}Repository` | `IBloqueioSaldoRepository` |
| Repository impl | `{DB}{Grupo}Repository` | `SqlServerBloqueioSaldoRepository` |
| SP Result record | `{NomeSP}Result` | `BloqueioSaldoResult` |
| SP Input record | `{NomeSP}Input` | `BloqueioSaldoInput` |
| Response DTO | `{NomeSP}Response` | `BloqueioSaldoResponse` |
