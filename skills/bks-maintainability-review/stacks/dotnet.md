# Stack .NET

Critérios da stack .NET (C#), do .NET Framework 4.x ao .NET 10. Complementam a rubrica e os
critérios comuns. Cada item indica o eixo que alimenta.

## Detecção

| Sinal | Conclusão |
| --- | --- |
| `.slnx` ou `.sln` | Uma aplicação. Os `.csproj` abaixo dela são partes da mesma aplicação |
| `.csproj` sem solution acima dele em `app/` | Uma aplicação isolada |
| `WebApplication`, `MapGet`/`MapPost`, `ControllerBase` | Tipo **API** |
| `BackgroundService`, `IHostedService`, `ServiceBase`, TopShelf, consumidor de fila | Tipo **Worker** |
| `ServiceContract`, `OperationContract`, `.svc`, `CoreWCF`, `asmx` | Tipo **Web Service** |
| `classlib` sem host, `PackageId`, extensão `AddXyz(...)` | Tipo **Componente** (biblioteca, SDK) |
| `SqlFunction`, `SqlProcedure` (SQLCLR) | Tipo **Componente**, com o motor do banco como consumidor |

Uma solução com API e biblioteca interna gera um parecer por parte. Ignore `bin/`, `obj/`,
migrations geradas e clientes gerados por ferramenta.

Medições úteis: `dotnet list reference` para referências entre projetos, busca por
`public (class|interface|record)` para a superfície pública, contagem de linhas por método.

## Repertório da persona nesta stack

| Atributo | Repertório |
| --- | --- |
| Linguagem | C# moderno: `record`, pattern matching, `async`/`await`, LINQ, generics simples |
| Hospedagem | Minimal API, Controllers, `BackgroundService`, DI nativa, `IOptions<T>` |
| Dados | Dapper, EF Core, ADO.NET, Stored Procedures |
| Testes | xUnit com `Assert` nativo, fakes manuais, Testcontainers |
| Observabilidade | `ActivitySource`, `Meter`, `ILogger` estruturado |

### Fora do repertório (cada uso conta como custo cognitivo)

- Reflection, expression trees, source generators, `dynamic`, emissão de IL.
- Generics com múltiplas restrições aninhadas; covariância e contravariância explícitas.
- Programação funcional avançada: mônadas, railway-oriented encadeado, combinadores.
- Metaprogramação por convenção: auto-registro de DI por varredura de assembly, interceptors,
  decorators gerados.
- `Span<T>`, `Memory<T>`, pooling manual e otimização de alocação sem medição que a justifique.
- Concorrência manual (`SemaphoreSlim`, `Channel<T>`, locks) fora de um componente nomeado e
  documentado.

## Critérios

### Dapper e acesso a dados (A3, A5, A6, A8)

- Onde o SQL mora: inline no repositório, constantes, arquivos `.sql` embarcados ou procedures.
  Qualquer opção serve; misturar sem critério é custo.
- Mapeamento explícito entre colunas e propriedades. `multi-map` com `splitOn` complexo ou
  `QueryMultiple` encadeado precisam de comentário ou teste.
- Tipos de parâmetro declarados (`DbType`, tamanho de `varchar`) onde o SQL Server faria conversão
  implícita.
- Um padrão único de transação: quem abre, quem confirma, quem descarta.
- DTOs de persistência separados das entidades de domínio, com conversão num só lugar.

### EF Core (A4, A5, A6)

- Configuração por Fluent API, fora do domínio; nada de annotations nas entidades.
- Consultas com `AsNoTracking` onde só há leitura; carregamento relacionado explícito.
- Migrations geradas não entram na contagem de complexidade.

### APIs (A1, A3, A8)

- Erros convertidos em `ProblemDetails` por um mecanismo central.
- Contrato OpenAPI gerado a partir do código.

### Workers (A6, A8, A9)

- `ExecuteAsync` legível em uma tela.
- Escopo de DI criado por iteração quando há dependências *scoped*, como conexão.
- `stoppingToken` respeitado em todo I/O.

### Web Services WCF e SOAP (A5, A8, A12)

- `ServiceContract` e `DataContract` separados da implementação e do domínio.
- Versionamento do contrato explícito no namespace; mudança incompatível vira contrato novo.
- Falhas expostas como `FaultContract` tipado, sem vazar exceção interna.
- Configuração de binding num lugar só, não espalhada entre `web.config` e código.

### Bibliotecas, SDKs e componentes (A4, A5, A10, A12)

- O restante da API fica `internal`. `InternalsVisibleTo` só para testes.
- Registro por extensão única (`services.AddXyz(options => ...)`) com `Options` validadas.
- Exceções públicas próprias do componente, sem vazar exceções de bibliotecas internas.
- XML docs em todos os tipos e membros públicos.
- Verificação de compatibilidade com `PublicApiAnalyzers` ou diff de API.

### SQLCLR (A4, A7, A9)

- Assembly com `PERMISSION_SET` mínimo; `UNSAFE` só com o motivo registrado.
- Lógica testável fora do SQL Server, com a função SQLCLR como adaptador fino.

### Observabilidade (A9)

- `ActivitySource` e `Meter` declarados num lugar conhecido, um por componente.
- Em bibliotecas, o componente emite telemetria mas não configura exporters, que são do host.
