# Padrões DDD Tático

Use estes padrões quando a complexidade do domínio for **Rica**.

## Aggregate Root

```csharp
// Entities são classes, nunca records
public class Pedido : AggregateRoot
{
    public PedidoId Id { get; private set; }
    public ClienteId ClienteId { get; private set; }
    public PedidoStatus Status { get; private set; }
    private readonly List<ItemPedido> _itens = [];

    private Pedido() { } // para ORM

    // Factory method — construção controlada
    public static Pedido Criar(ClienteId clienteId) => new()
    {
        Id = PedidoId.Novo(),
        ClienteId = clienteId,
        Status = PedidoStatus.Rascunho
    };

    public void AdicionarItem(ItemPedido item)
    {
        if (Status != PedidoStatus.Rascunho)
            throw new DomainException("Pedido não pode ser alterado após confirmação");
        _itens.Add(item);
    }

    public void Confirmar()
    {
        if (!_itens.Any())
            throw new DomainException("Pedido sem itens não pode ser confirmado");
        Status = PedidoStatus.Confirmado;
        AddDomainEvent(new PedidoConfirmado(Id, ClienteId));
    }
}
```

**Regras:**
- Setters sempre `private`
- Constructor privado para ORM
- Factory method estático para criação controlada
- Métodos de comportamento encapsulam regras
- Domain Events nomeados no passado, disparados via `AddDomainEvent` após mudança de estado

## Value Objects

```csharp
// ≤ 16 bytes → readonly record struct
public readonly record struct PedidoId(Guid Value)
{
    public static PedidoId Novo() => new(Guid.NewGuid());
}

// > 16 bytes → record class
public sealed record Endereco(
    string Logradouro,
    string Numero,
    string CEP,
    string Cidade,
    string UF);
```

## Domain Events

```csharp
// Nomeados no passado, imutáveis
public sealed record PedidoConfirmado(PedidoId PedidoId, ClienteId ClienteId)
    : IDomainEvent
{
    public DateTime OcorridoEm { get; } = DateTime.UtcNow;
}
```

## Application Service (Orquestração via Pipeline)

Application Services não contêm regra de negócio. Orquestram via PipelineOrchestrator.

```csharp
public sealed class CreatePedidoUseCase(
    PipelineOrchestrator<TransactionCreatePedido, PedidoResponse> pipeline)
    : ICreatePedidoUseCase
{
    public ValueTask<PipelineResult<PedidoResponse>> ExecuteAsync(
        TransactionCreatePedido transaction, CancellationToken ct = default)
        => pipeline.ExecuteAsync(transaction, ct);
}
```

## Repositório (Port no Domain)

```csharp
// Interface definida no Domain/Core — sem nenhuma dependência de framework
public interface IPedidoRepository
{
    ValueTask<Pedido?> GetByIdAsync(PedidoId id, CancellationToken ct);
    ValueTask<IReadOnlyList<Pedido>> GetAllAsync(CancellationToken ct);
    ValueTask AddAsync(Pedido pedido, CancellationToken ct);
    ValueTask UpdateAsync(Pedido pedido, CancellationToken ct);
    ValueTask DeleteAsync(PedidoId id, CancellationToken ct);
}
```
