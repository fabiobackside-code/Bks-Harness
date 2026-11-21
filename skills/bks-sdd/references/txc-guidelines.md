# TXC Guidelines — Transaction Context Pattern

> **Versão:** 2.2 (`BksQueryExecutor` e `TDecision`, `decisions/ADR-016`)
> **Fonte:** o motor do NQuantic 3.0.0, validado em produção de desenvolvimento, sintetizado pelo
> `bks-motor-sdk`, sem o que é bancário (`decisions/ADR-015` do kit)
> **Escopo:** projeto que adota TXC no `.bks-profile.json`; sem a adoção, este guia não se aplica
> **Paradigma:** agnóstico de linguagem; exemplos em C#
> **Temperatura de decisão:** 0.02 — regras prescritivas, não sugestões

---

## SEÇÃO 1 — O que é TXC e quando adotar

**TXC (Transaction Context)** é o padrão que o autor do kit adota em sistemas com aspecto
transacional: operação que lê, decide e grava, e que precisa de rastro, idempotência e compensação.
Cada operação vira uma **transação registrada por código**, que corre sempre o mesmo pipeline.

Três peças, e só três, pertencem a cada transação:

| Peça | O que é | Quem escreve |
|---|---|---|
| **TXC** | identidade da execução: código, `CorrelationId`, `UserId`, `TenantId`, `TraceId`, chave de idempotência. **Somente leitura**; viaja por parâmetro, sem `AsyncLocal`; não carrega retorno | a sessão, ao abrir a transação |
| **Envelope** | a entrada da transação, já transformada do DTO de consumo, junto com o TXC. Nasce de uma **fábrica pura** `(seed, input) => envelope` | o consumidor, uma fábrica por transação |
| **Executor** | o lugar da regra de negócio e da escrita | o consumidor, um por transação |

**Dado entre passos é retorno tipado, não campo.** O executor lê no `ValidateAsync` e devolve um
`TValidation`; o `ApplyRule` o recebe como parâmetro. Nada é "hidratado" num objeto que muda.

**Quando adotar:** sistema com várias operações de escrita que precisam de idempotência, auditoria e
compensação (financeiro, pedidos, reservas, integrações com efeito). **Quando não adotar:** CRUD
simples, protótipo, serviço de leitura. O projeto declara a escolha no perfil (Seção 8).

---

## SEÇÃO 2 — O pipeline

Ordem fixa. O consumidor não reordena; só decide se registra as etapas opcionais.

```
ExecuteAsync(code, input)
  └─ fábrica do envelope      (seed, input) => envelope        pura, sem I/O
  └─ [10] Validation          opcional    validação pura da entrada, sem I/O
  └─ [20] Idempotency         obrigatória no executor que grava; ausente no de consulta
  └─ [40] Processing          obrigatória o executor
  └─ [50] PostProcessing      opcional    conclusão ou difusão; roda em sucesso e em falha
```

| # | Regra |
|---|---|
| `[10]` | Só a entrada: formato, obrigatoriedade, faixa. Não lê banco nem chama serviço, porque é validação pura da entrada. |
| `[20]` | Guarda de replay. Achou a chave: devolve o resultado da primeira execução e encerra; a `[50]` não roda. |
| `[40]` | Único ponto de escrita. A base conduz o executor (Seção 3); o consumidor não encadeia passos. |
| `[50]` | Não monta resposta (a resposta é do adapter). **Não crítica** (padrão): roda depois da resposta (em Go, síncrona antes de devolver), a falha fica no span e não muda o resultado. **Crítica**: a resposta espera por ela; se falhar depois de a `[40]` gravar, a base compensa e devolve o erro. |

Os números são a ordem e o nome do span (`step.{Order}`). Um domínio pode declarar etapa própria
entre `[20]` e `[40]` — o NQuantic tem a `[30]` de resolução de conta, bancária — mas o kit não traz
nenhuma; a regra de negócio da aplicação tem um lugar só, o `ApplyRule`.

**Telemetria é da base.** Cada etapa abre o span, mede, captura o erro e fecha. Quem escreve uma
etapa ou um executor não escreve instrumentação.

---

## SEÇÃO 3 — Os executores

Hierarquia selada: o consumidor deriva de um dos dois, nunca da base comum.

| Tipo | Para | `[20]` |
|---|---|---|
| `BksTransactionalExecutor<TEnvelope, TValidation, TDecision, TOut>` | operação que grava | sempre |
| `BksQueryExecutor<TEnvelope, TOut>` | consulta, sem gravar | nunca |

**No transacional, a base conduz a cadeia:**

```
ValidateAsync(envelope)            lê o que a regra precisa; devolve TValidation   virtual
ApplyRule(envelope, valid.)        a regra de negócio; devolve TDecision           abstract
ExecuteAsync(envelope, decisão)    grava TDecision pela Secondary Port             abstract
ConfirmAsync(envelope)             segunda fase; corpo vazio por padrão            virtual
falha depois de gravar → CancelAsync(envelope)  compensação                        virtual
```

- `ApplyRule` e `ExecuteAsync` são obrigatórios; os outros têm corpo padrão. O `ApplyRule` é síncrono:
  a regra é pura, e o que ela precisa ler já veio no `TValidation`.
- **Uma fase é o caso comum:** o `ExecuteAsync` grava o estado final e o `ConfirmAsync` fica vazio.
- **Duas fases quando há efeito externo que decide** (reservar o quarto e cobrar o cartão): o
  `ExecuteAsync` grava com status `Executed`, o `ConfirmAsync` chama o efeito e leva a `Confirmed`, o
  `CancelAsync` libera. A entidade ganha o status; o modo pendente (confirmar depois) é só do motor.

```csharp
protected override async Task<PipelineResult<ReservaOutput>> ExecuteAsync(ReservaEnvelope env, Reserva r, CancellationToken ct)
{
    await reservas.SaveAsync(r with { Status = ReservaStatus.Executed }, ct);
    return new ReservaOutput(r.Id);
}

protected override async Task<PipelineResult> ConfirmAsync(ReservaEnvelope env, CancellationToken ct)
{
    var cobranca = await gateway.CobrarAsync(env.Input.Cartao, env.Input.Valor, ct);
    if (!cobranca.Aprovada) return PipelineResult.Fail(ReservaErrors.PagamentoRecusado);   // a base chama o CancelAsync
    await reservas.MarcarAsync(env.Input.ReservaId, ReservaStatus.Confirmed, ct);
    return PipelineResult.Ok();
}

protected override Task CancelAsync(ReservaEnvelope env, CancellationToken ct) =>
    reservas.LiberarAsync(env.Input.ReservaId, ct);
```

- Ordem, `try` e compensação ficam privados na base.
- O efeito externo depois de gravar (notificar, publicar) na `[50]` não crítica, se falha, vai ao
  span e **não muda o resultado**; só a `[50]` crítica que falha compensa e devolve o erro.
- Integração externa entra pelo construtor, como Port da aplicação.

**Consulta é um executor por consulta**, registrado por código como qualquer transação. Leitura
composta de várias fontes é o mesmo `BksQueryExecutor`, com várias Ports no construtor.

**Lote é item por item pela sessão.** O worker lê a coleção e chama `ExecuteAsync` uma vez por
item, cada um com a própria chave de idempotência: o reinício pula o que já foi feito, e a falha de
um item não derruba os outros.

```csharp
foreach (var p in await pendentes.ListarAsync(ct))
    await session.ExecuteAsync<ReprocessarInput, ReprocessarOutput>(
        PedidoCodes.Reprocessar, new ReprocessarInput(p.Id, $"{lote.Chave}:{p.Id}"), ct);
```

Lote como **uma transação só** (um código, o executor processa a coleção, tudo ou nada) só quando o
requisito exige atomicidade do lote; a ficha da transação diz por quê.

**Utilitário técnico fica fora do TXC.** Recalcular índice, limpar cache, migrar dado sem regra de
negócio: job ou comando simples, sem registro por código.

---

## SEÇÃO 4 — Registro e chamada

O consumidor registra cada transação por código, num builder tipado. Quem chama vê só o código e a
entrada; o envelope fica escondido.

```csharp
services.AddBksPipeline()
    .AddBksTransaction<CriarPedidoInput, CriarPedidoEnvelope, CriarPedidoOutput>(PedidoCodes.Criar, t => t
        .Envelope((seed, input) => new CriarPedidoEnvelope(seed, input))
        .Executor<CriarPedidoExecutor>()
        .Validation<CriarPedidoValidation>()
        .PostProcessing<PedidoCriadoNotificacao>(critical: false))
    .AddBksQuery<ObterPedidoInput, ObterPedidoEnvelope, PedidoView>(PedidoCodes.Obter, t => t
        .Envelope((seed, input) => new ObterPedidoEnvelope(seed, input))
        .Executor<ObterPedidoExecutor>());

// adapter inbound
app.MapPost("/pedidos", async (CriarPedidoRequest req, IBksSession session, CancellationToken ct) =>
{
    var result = await session.ExecuteAsync<CriarPedidoInput, CriarPedidoOutput>(
        PedidoCodes.Criar, req.ToInput(), ct);
    return result.ToHttpResult();   // a resposta é montada aqui, fora do pipeline
});
```

| Regra | Detalhe |
|---|---|
| Códigos | constantes por BoundedContext (`PedidoCodes.Criar = "PEDIDO.CRIAR"`); código repetido recusa na subida |
| Registro | escrita em `AddBksTransaction`, que exige `TIn : IBksIdempotentInput`; consulta em `AddBksQuery`, sem `[20]` |
| Composição | falta de envelope ou de executor recusa na subida com exceção de composição — é erro de programação, não fere o Result Pattern |
| Resultado | `PipelineResult<TOut>` com a coleção de erros tipados; exceção de negócio nunca escapa |
| Dependências | executor e etapas resolvidos por tipo, no escopo da sessão |

**A Primary Port é a sessão** (em Go, o `txc.Op[In, Out]` de cada transação). Não existe `I{Entidade}Handler` nem `I{Operacao}UseCase`: o
contrato que o adapter usa é `IBksSession.ExecuteAsync(code, input)`, e o catálogo de
códigos do BC diz o que a aplicação oferece.

---

## SEÇÃO 5 — Exemplo de referência: Criar Pedido

O cliente envia itens. O sistema confere o cliente, aplica o desconto da categoria, grava o pedido e
devolve o número.

```csharp
public sealed record CriarPedidoEnvelope(BksTransactionSeed Seed, CriarPedidoInput Input);

public sealed class CriarPedidoValidation : BksValidationStep<CriarPedidoInput>          // [10]
{
    protected override PipelineResult Validate(CriarPedidoInput input) =>
        input.Itens.Count == 0 ? PipelineResult.Fail(PedidoErrors.SemItens) : PipelineResult.Ok();
}

public sealed record ClienteLido(Cliente Cliente, decimal DescontoCategoria);           // TValidation

public sealed class CriarPedidoExecutor(IClienteRepository clientes, IPedidoRepository pedidos)
    : BksTransactionalExecutor<CriarPedidoEnvelope, ClienteLido, Pedido, CriarPedidoOutput>
{
    protected override async Task<PipelineResult<ClienteLido>> ValidateAsync(CriarPedidoEnvelope env, CancellationToken ct)
    {
        var cliente = await clientes.GetByIdAsync(env.Input.ClienteId, ct);
        return cliente is null
            ? PipelineResult.Fail<ClienteLido>(PedidoErrors.ClienteInexistente)
            : new ClienteLido(cliente, cliente.Categoria.Desconto);
    }

    protected override PipelineResult<Pedido> ApplyRule(CriarPedidoEnvelope env, ClienteLido lido) =>
        Pedido.Criar(lido.Cliente, env.Input.Itens, lido.DescontoCategoria);

    protected override async Task<PipelineResult<CriarPedidoOutput>> ExecuteAsync(CriarPedidoEnvelope env, Pedido pedido, CancellationToken ct)
    {
        await pedidos.SaveAsync(pedido, ct);
        return new CriarPedidoOutput(pedido.Numero);
    }
}
```

Nada no envelope muda depois de criado; cada passo recebe o que precisa e devolve o próprio
resultado.

---

## SEÇÃO 6 — Ficha da transação (FEAT §5)

Substitui o antigo Transaction Map. Uma ficha por código de transação.

| Campo | Criar Pedido |
|---|---|
| Código | `PEDIDO.CRIAR` |
| Executor | transacional |
| Entrada (`TIn`) | `ClienteId`, `Itens` |
| Envelope | `Seed` + `Input` |
| `[10]` | pelo menos um item; quantidade > 0 |
| `TValidation` (o que o `ValidateAsync` lê) | `Cliente`, desconto da categoria |
| Regra (`ApplyRule`) | `Pedido.Criar` com o desconto; recusa cliente bloqueado |
| Gravação (Port) | `IPedidoRepository.SaveAsync` |
| Compensação | nenhuma (uma escrita só) |
| Saída (`TOut`) | `Numero` |
| `[50]` | notificação ao cliente, não crítica |
| Erros | `SemItens`, `ClienteInexistente`, `ClienteBloqueado` |

Para consulta, a ficha tem só Código, Executor (`consulta`), Entrada, Ports lidas, Saída e Erros.

---

## SEÇÃO 7 — Secondary Ports e anti-padrões

**Uma Secondary Port por aggregate ou recurso externo**, nunca genérica:

| Errado | Certo |
|---|---|
| `IDBRepositoryPort`, `IRepository<T>` | `IPedidoRepository`, `IClienteRepository` |
| `IExternalServicePort` | `IProcessadorDePagamento`, `INotificacaoService` |

Repositório do aggregate fica junto do domínio; serviço externo, na aplicação.

**Anti-padrões:**

| Anti-padrão | Por que dói | Forma certa |
|---|---|---|
| Objeto de transação com `HydrateX()` e `private set` que muda a cada fase | estado escondido; a ordem das chamadas vira regra implícita | retorno tipado: `ValidateAsync` → `TValidation` → `ApplyRule` |
| Adapter que busca dependência e preenche a transação | adapter com regra; teste do fluxo exige HTTP | adapter só chama `ExecuteAsync(code, input)`; a leitura é do `ValidateAsync` |
| Regra de negócio na `[10]` ou numa etapa extra | dois lugares para a mesma coisa | regra só no `ApplyRule`; `[10]` só valida a entrada |
| Executor que encadeia outro executor | duas transações sem rastro comum | uma transação por código; composição é da aplicação, fora do motor |
| Escrita sem `[20]` | reenvio duplica o efeito | toda escrita é `BksTransactionalExecutor` |
| `[50]` montando a resposta | resposta depende de etapa que roda depois | a resposta é do adapter |
| `I{Operacao}UseCase` ou `I{Entidade}Handler` | uma interface por operação sem ganho | a sessão (em Go, o `txc.Op`) é a Primary Port; o catálogo de códigos é o contrato |

---

## SEÇÃO 8 — Base no projeto ou motor

O projeto declara no `.bks-profile.json`:

| `txc` | O que o kit gera |
|---|---|
| ausente | nada de TXC; vale a arquitetura do perfil sem este guia |
| `"base"` | base mínima dentro do projeto (`Application/Pipeline/`), com os nomes do motor (prefixo `Bks`) no namespace do projeto, para não colidir com tipos de framework como `ITransaction`: sessão, registro, etapas `[10]` `[20]` `[50]`, os dois executores, `PipelineResult<T>`. Três pontos divergem do motor: o resultado (`PipelineResult<T>`), o executor de consulta (`BksQueryExecutor`, que no motor é `BksDirectExecutor`; `ADR-016`) e o quarto tipo do executor transacional (`TDecision`): no motor a procedure grava a partir do envelope, na base o `ExecuteAsync` recebe o que a regra decidiu para gravar pela Port. A idempotência usa uma Port (`IBksIdempotencyStore`) que o projeto implementa |
| `"motor"` | referência ao pacote do `bks-motor-sdk`, com a API dele. Só quando a persistência é por stored procedure por transação em PostgreSQL, o caso para o qual o motor foi feito |

A forma é a mesma nos dois: registro por código, envelope por fábrica, executores, pipeline. Migrar
de `base` para `motor` é trocar a base pelo pacote e escrever a procedure de cada transação. O motor
acrescenta o que a base não tem: as ações `Validate`, `Execute`, `Confirm` e `Cancel` na procedure,
journal, modo pendente, recuperação e estorno.

---

## SEÇÃO 9 — Checklist de conformidade

### PRD §8

| # | Verificação |
|---|---|
| 1 | O perfil declara `txc` e o PRD diz por que o sistema é transacional |
| 2 | §8b lista, por BoundedContext, o catálogo de códigos de transação |
| 3 | §8c lista Secondary Ports por aggregate ou recurso, nenhuma genérica |
| 4 | §8a mostra o adapter chamando a sessão e o pipeline `[10] → [20] → [40] → [50]` |
| 5 | Não há `I{Operacao}UseCase`, `I{Entidade}Handler`, `HydrateX` nem `PreProcessing` |

### FEAT §5

| # | Verificação |
|---|---|
| 1 | Uma ficha (Seção 6) por código de transação |
| 2 | Toda escrita usa executor transacional; toda leitura, executor de consulta |
| 3 | A `[10]` só valida a entrada; a regra está no `ApplyRule` |
| 4 | O `TValidation` nomeia o que é lido e de qual Port |
| 5 | Compensação declarada quando há mais de uma escrita ou efeito externo crítico |
| 6 | Erros de negócio tipados e listados |
