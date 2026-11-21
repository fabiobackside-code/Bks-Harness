# Catálogo de portas

Uma entrada por porta da entrevista (fases 5 e 6). Cada uma traz o contrato, o adapter mínimo, o
registro e as regras de recurso. A pasta de cada porta está na tabela de "Estruturas de pasta" do
`SKILL.md`.

Siglas: DI (injeção de dependência), TCP (Transmission Control Protocol), HTTP (Hypertext Transfer
Protocol), gRPC (chamada remota sobre HTTP/2), SOAP (web service XML), TXC (Transaction Context).

**Pacote NuGet:** a entrada cita o pacote usual; ele só entra no projeto com a confirmação do
usuário, na fase 9.

---

## Regras que valem para toda porta

| Regra | O que exige |
|---|---|
| Construtor | dependência pelo construtor; nunca `IServiceProvider` em serviço. Adapter de entrada usa `IServiceScopeFactory`, um escopo por mensagem |
| Domínio limpo | o domínio não conhece adapter concreto, driver nem `Microsoft.AspNetCore.*`; só a Port |
| Concorrência limitada | sem `Task.Run` solto nem `_ = MetodoAsync()`; trabalho paralelo passa por `Channel` com capacidade ou `SemaphoreSlim` |
| Estado por conexão | sem `lock` global nem estado estático mutável |
| Async correto | sem `async void`, `.Result`, `.Wait()`, `.GetAwaiter().GetResult()` nem `async` sem `await` |
| Memória | buffer do `ArrayPool<byte>` ou `System.IO.Pipelines`; sem `GC.Collect`; sem `Channel` sem limite |
| Log | `LoggerMessage` gerado na compilação (`[LoggerMessage]`); span não é logger; payload fora de tag de span |
| Erro | um estilo só: `PipelineResult<T>` na fronteira; exceção só para o inesperado |
| Configuração | uma seção de `appsettings.json` por adapter, lida por `IOptions<T>` com `ValidateOnStart`; nada de segredo, IP ou endpoint no código |
| Higiene | sem código morto, registro duplicado, pacote sem uso nem `#region` |

---

## Portas de entrada

Todo adapter de entrada termina no mesmo destino: `I{Entidade}Service` no padrão direto,
`IBksSession.ExecuteAsync(code, input)` no TXC, depois de preencher o `BksCallContext` do escopo.

### HTTP — Minimal API ou Kestrel no Worker

- **Contrato:** rotas em `Endpoints/{Entidade}Endpoints.cs`; a resposta é `IResult`, montada no
  adapter (`ToHttpResult`).
- **Adapter mínimo:** Template 2 (direto) ou 6 (TXC) do `SKILL.md`.
- **Registro:** `services.AddHttpAdapter(configuration)` e `app.Map{Entidade}Endpoints()`. No Worker,
  o projeto usa o Web SDK.
- **Recurso:** autenticação conforme a fase 5 (`RequireAuthorization()` só quando declarada);
  `CancellationToken` da requisição propagado até a Port.

### Servidor TCP

- **Contrato:** `TcpServerSettings` (porta, conexões máximas, timeout de leitura); o enquadramento
  da mensagem é do protocolo do projeto, numa classe própria.
- **Adapter mínimo:** `BackgroundService` com o listener; exemplo em `references/worker-patterns.md`.
- **Registro:** `services.AddTcpServerAdapter(configuration)` registra o `BackgroundService`.
- **Recurso:** conexões simultâneas limitadas por `SemaphoreSlim(ConexoesMaximas)`; buffer do
  `ArrayPool<byte>` ou `PipeReader`; leitura binária por `BinaryPrimitives` sobre
  `ReadOnlySpan<byte>`, sem `Marshal`; estado por conexão; timeout de leitura configurável.

### Consumer de fila — Kafka, RabbitMQ ou outro

- **Contrato:** `{Fila}ConsumerSettings` (tópico ou fila, grupo, prefetch, paralelismo).
- **Adapter mínimo:**

  ```csharp
  public sealed partial class PedidoConsumer(
      IServiceScopeFactory scopes, IConsumer<string, byte[]> consumer, IRejeitadasPublisher rejeitadas,
      ILogger<PedidoConsumer> logger)
      : BackgroundService
  {
      protected override async Task ExecuteAsync(CancellationToken stoppingToken)
      {
          await Task.Yield();
          while (!stoppingToken.IsCancellationRequested)
          {
              var msg = consumer.Consume(stoppingToken);
              await using var scope = scopes.CreateAsyncScope();
              var service = scope.ServiceProvider.GetRequiredService<IPedidoService>();
              var result = await service.ProcessarAsync(PedidoMessage.Parse(msg.Message.Value), stoppingToken);
              if (!result.IsSuccess)
              {
                  await rejeitadas.PublishAsync(msg.Message.Value, result.Errors, stoppingToken);
                  LogRejeitada(logger, msg.TopicPartitionOffset.ToString());
              }
              consumer.Commit(msg);
          }
      }

      [LoggerMessage(Level = LogLevel.Warning, Message = "Mensagem rejeitada em {Offset}")]
      private static partial void LogRejeitada(ILogger logger, string offset);
  }
  ```

- **Registro:** `services.AddKafkaConsumerAdapter(configuration)` (pacote `Confluent.Kafka`) ou
  `AddRabbitMqConsumerAdapter` (pacote `RabbitMQ.Client`).
- **Recurso:** confirmação (commit ou ack) só depois do resultado; paralelismo pelo prefetch ou por
  `Channel` com capacidade; mensagem que falha sempre vai para a fila de rejeitadas, sem laço de
  reentrega infinito.

### Agendamento

- **Contrato:** `SchedulerSettings` (intervalo ou expressão).
- **Adapter mínimo:** `BackgroundService` com `PeriodicTimer`; exemplo de lote em
  `references/worker-patterns.md`.
- **Registro:** `services.AddSchedulerAdapter(configuration)`.
- **Recurso:** uma execução por vez (o `PeriodicTimer` não sobrepõe ticks); no TXC, lote item a item
  pela sessão, cada item com a própria chave de idempotência.

### gRPC de entrada

- **Contrato:** o `.proto` do serviço, em `Adapters/Inbound/GrpcAdapter/Protos/`.
- **Adapter mínimo:** classe que herda do `{Servico}.{Servico}Base` gerado e só traduz mensagem em
  input, chama a Port e traduz o `PipelineResult` em resposta ou `RpcException`.
- **Registro:** `services.AddGrpc()` e `app.MapGrpcService<{Servico}GrpcAdapter>()` (pacote
  `Grpc.AspNetCore`); Web SDK.
- **Recurso:** deadline do cliente propagado como `CancellationToken`; autenticação conforme a fase 5.

---

## Portas de saída

A Port fica em `Domain/Core/Ports/`; o adapter, em `Adapters/Outbound/{Nome}Adapter/`. Uma Port
por aggregate ou recurso externo, nunca genérica (`IRepository<T>`).

### Banco relacional — SQL Server, PostgreSQL, Oracle, MySQL ou outro

- **Contrato:** `I{Entidade}Repository`, com métodos do negócio; nunca `IQueryable<T>`.
- **Adapter mínimo:** Dapper sobre `IDbConnectionFactory`, com SQL parametrizado; EF Core com Fluent
  API no adapter; Stored Procedure conforme `references/stored-procedures.md`.
- **Registro:** `services.Add{Banco}Adapter(configuration)`, com a connection string em
  `ConnectionStrings`, sobrescrita por variável de ambiente.
- **Recurso:** conexão aberta e descartada por operação (`await using`); pool do driver, nunca pool
  próprio; no TXC, o `IBksIdempotencyStore` mora neste adapter.

### Banco de documentos — MongoDB ou outro

- **Contrato:** `I{Entidade}Repository`, igual ao relacional.
- **Adapter mínimo:** `IMongoCollection<{Documento}>` com mapeamento no adapter; o aggregate não
  conhece atributo do driver (pacote `MongoDB.Driver`).
- **Registro:** `services.AddMongoAdapter(configuration)`; `MongoClient` como singleton.
- **Recurso:** um `MongoClient` por processo; índices criados na subida, não na consulta.

### Cache — Redis ou outro

- **Contrato:** `I{Recurso}Cache` com o que o negócio guarda (`ObterSaldoAsync`), não um
  `ICache` genérico.
- **Adapter mínimo:** `IConnectionMultiplexer` (pacote `StackExchange.Redis`) ou `HybridCache`.
- **Registro:** `services.AddCacheAdapter(configuration)`; multiplexer singleton.
- **Recurso:** expiração sempre declarada; falha do cache cai na fonte, sem derrubar a operação.

### Producer de fila — Kafka, RabbitMQ ou outro

- **Contrato:** `I{Evento}Publisher` com um método por evento de negócio.
- **Adapter mínimo:** `IProducer<string, byte[]>` (Kafka) ou canal do `RabbitMQ.Client`.
- **Registro:** `services.AddKafkaProducerAdapter(configuration)`; producer singleton.
- **Recurso:** confirmação de entrega aguardada; no TXC, a publicação depois da gravação vai na
  `[50]` não crítica, e a falha fica no span sem mudar o resultado; se a publicação for condição
  da operação, a `[50]` é crítica e a falha compensa.

### Cliente HTTP

- **Contrato:** `I{Sistema}Client` com as operações que a aplicação usa.
- **Adapter mínimo:** typed client sobre `HttpClient`.
- **Registro:** `services.AddHttpClient<I{Sistema}Client, {Sistema}HttpAdapter>()` com
  `.AddStandardResilienceHandler()`; uma política de resiliência por cliente.
- **Recurso:** sempre `IHttpClientFactory`, nunca `new HttpClient()`; timeout e base address em
  `IOptions<T>`.

### Cliente TCP

- **Contrato:** `I{Sistema}Client`; o enquadramento é do protocolo do sistema de destino.
- **Adapter mínimo:** pool de conexões próprio do adapter, com tamanho em `IOptions<T>`.
- **Registro:** `services.Add{Sistema}TcpAdapter(configuration)`; o pool é singleton.
- **Recurso:** conexões limitadas pelo pool; buffer do `ArrayPool<byte>`; timeout de conexão e de
  leitura; conexão quebrada sai do pool.

### Cliente SOAP

- **Contrato:** `I{Sistema}Client`; o contrato gerado do WSDL fica dentro do adapter.
- **Adapter mínimo:** proxy gerado pelo `dotnet-svcutil` (pacote `System.ServiceModel.Http`),
  embrulhado pela classe do adapter.
- **Registro:** `services.Add{Sistema}SoapAdapter(configuration)`; endpoint em `IOptions<T>`.
- **Recurso:** canal reaproveitado (`ChannelFactory` singleton); tipos do WSDL não atravessam a Port.

### Cliente gRPC

- **Contrato:** `I{Sistema}Client`; os tipos gerados do `.proto` ficam no adapter.
- **Adapter mínimo:** cliente gerado registrado pela fábrica (pacote `Grpc.Net.ClientFactory`).
- **Registro:** `services.AddGrpcClient<{Servico}.{Servico}Client>(o => o.Address = ...)`.
- **Recurso:** deadline por chamada; canal gerenciado pela fábrica.

### Observabilidade

- **Contrato:** `ActivitySource` e `Meter` do serviço, com o nome do serviço.
- **Adapter mínimo:** OpenTelemetry com exportador OTLP ou console, conforme a fase 8; Serilog para
  log estruturado.
- **Registro:** `services.AddObservabilityAdapter(configuration)`, com `AddSource` e `AddMeter` do
  serviço; endpoint OTLP por variável de ambiente.
- **Recurso:** span com tags de negócio, nunca o payload; métricas com contador e histograma.

---

## Outro

Para a tecnologia que a entrevista marcou como "outro", a skill não escolhe biblioteca:

1. **Port declarada** em `Domain/Core/Ports/`, com os métodos que o negócio usa.
2. **Adapter vazio** em `Adapters/{Inbound|Outbound}/{Nome}Adapter/`, que implementa a Port e
   devolve `PipelineError` "não implementado" até a especificação dizer a tecnologia.
3. **Teste de contrato** em `{ServiceName}.Tests`: o comportamento esperado da Port, escrito contra
   um substituto, pronto para rodar contra o adapter real quando ele existir.

O adapter real entra na especificação da feature. Trocar o adapter depois não toca o domínio.
