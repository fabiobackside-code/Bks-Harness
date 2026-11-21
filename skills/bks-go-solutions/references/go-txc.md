# Base do Transaction Context em Go — `internal/platform/txc`

Gerada uma vez, só quando a VC-6 é TXC (Transaction Context), no pacote `internal/platform/txc`. O modelo é o do
`txc-guidelines.md` da skill `bks-sdd`; aqui está o contrato em Go.

Siglas: DTO (Data Transfer Object), HTTP (Hypertext Transfer Protocol).

## O que difere do .NET, e por quê

| Ponto | .NET (`txc-base.md`) | Go |
|---|---|---|
| Resultado | `PipelineResult<T>` | `(Out, error)`, o erro idiomático da seção 2 do `go-standards.md` |
| Primary Port | `IBksSession.ExecuteAsync(code, input)` com registro por código | `txc.Op[In, Out]`, uma função por transação, montada no `main.go` |
| Criação do TXC | a sessão | `NewTransaction` e `NewQuery`; o construtor do `Seed` não é exportado |
| Ficha da transação | classe que deriva do executor | `txc.Steps`, uma struct de funções |
| Idempotência | `IBksIdempotencyStore` genérico por método | `IdempotencyStore` com o resultado em bytes |

Sem registro por código, porque em Go ele obriga um mapa de `any` com asserção de tipo em tempo de
execução: troca erro de compilação por erro de execução. O `Op[In, Out]` é o equivalente tipado. O
adapter conhece só a entrada e a saída, nunca os tipos intermediários do pacote de domínio.

## O pacote

```go
package txc

import (
	"context"
	"encoding/json"
	"errors"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

// Call é o que o adapter de entrada sabe de quem chamou.
type Call struct {
	CorrelationID string
	UserID        string
	TenantID      string
}

// Seed é a identidade somente leitura de uma execução; só este pacote a cria.
type Seed struct {
	code, correlationID, userID, tenantID, traceID, idempotencyKey string
}

func (s Seed) Code() string           { return s.code }
func (s Seed) CorrelationID() string  { return s.correlationID }
func (s Seed) UserID() string         { return s.userID }
func (s Seed) TenantID() string       { return s.tenantID }
func (s Seed) TraceID() string        { return s.traceID }
func (s Seed) IdempotencyKey() string { return s.idempotencyKey }

func newSeed(ctx context.Context, code string, call Call, key string) Seed {
	return Seed{
		code: code, correlationID: call.CorrelationID, userID: call.UserID, tenantID: call.TenantID,
		traceID: trace.SpanContextFromContext(ctx).TraceID().String(), idempotencyKey: key,
	}
}

// IdempotentInput é a entrada que grava: declara a própria chave de idempotência.
type IdempotentInput interface {
	IdempotencyKey() string
}

// Op é a Primary Port de uma transação: o que o adapter de entrada recebe e chama.
type Op[In, Out any] func(ctx context.Context, call Call, in In) (Out, error)

// IdempotencyStore é a Port da [20]; o projeto implementa no adapter de banco.
type IdempotencyStore interface {
	Find(ctx context.Context, code, key string) (out []byte, found bool, err error)
	Save(ctx context.Context, code, key string, out []byte) error
}

// Steps é a ficha da transação; ApplyRule e Execute são obrigatórias.
type Steps[In IdempotentInput, V, D, Out any] struct {
	Check     func(in In) error                                       // [10], sem I/O
	Validate  func(ctx context.Context, s Seed, in In) (V, error)     // lê pelas Ports
	ApplyRule func(in In, v V) (D, error)                             // regra pura
	Execute   func(ctx context.Context, s Seed, d D) (Out, error)     // grava pela Port
	Confirm   func(ctx context.Context, s Seed) error                 // segunda fase
	Cancel    func(ctx context.Context, s Seed) error                 // compensação
	After     func(ctx context.Context, s Seed, in In, out Out, err error) error // [50]
	Critical  bool // a falha da [50] depois da gravação compensa e devolve o erro
}

var tracer = otel.Tracer("txc")

// NewTransaction monta a transação que grava: [10] → [20] → [40] → [50].
func NewTransaction[In IdempotentInput, V, D, Out any](
	code string, s Steps[In, V, D, Out], store IdempotencyStore,
) Op[In, Out] {
	if s.ApplyRule == nil || s.Execute == nil || store == nil {
		panic("txc: " + code + " sem ApplyRule, Execute ou IdempotencyStore")
	}
	return func(ctx context.Context, call Call, in In) (Out, error) {
		ctx, span := start(ctx, code, code)
		defer span.End()
		seed := newSeed(ctx, code, call, in.IdempotencyKey())

		if err := s.check(ctx, in); err != nil {
			return zero[Out](), record(span, err)
		}
		if out, found, err := replay[Out](ctx, store, seed); found || err != nil {
			return out, record(span, err)
		}
		out, err := s.process(ctx, seed, in)
		out, err = s.after(ctx, seed, in, out, err)
		if err != nil {
			return zero[Out](), record(span, err)
		}
		return out, record(span, save(ctx, store, seed, out))
	}
}

// NewQuery monta a consulta: sem [20] e sem gravar.
func NewQuery[In, Out any](code string, exec func(ctx context.Context, s Seed, in In) (Out, error)) Op[In, Out] {
	if exec == nil {
		panic("txc: " + code + " sem executor")
	}
	return func(ctx context.Context, call Call, in In) (Out, error) {
		ctx, span := start(ctx, code, code)
		defer span.End()
		out, err := exec(ctx, newSeed(ctx, code, call, ""), in)
		return out, record(span, err)
	}
}

func (s Steps[In, V, D, Out]) check(ctx context.Context, in In) error {
	if s.Check == nil {
		return nil
	}
	_, span := start(ctx, "step.10", "")
	defer span.End()
	return record(span, s.Check(in))
}

func (s Steps[In, V, D, Out]) process(ctx context.Context, seed Seed, in In) (Out, error) {
	ctx, span := start(ctx, "step.40", seed.code)
	defer span.End()

	var loaded V
	if s.Validate != nil {
		v, err := s.Validate(ctx, seed, in)
		if err != nil {
			return zero[Out](), record(span, err)
		}
		loaded = v
	}
	decision, err := s.ApplyRule(in, loaded)
	if err != nil {
		return zero[Out](), record(span, err)
	}
	out, err := s.Execute(ctx, seed, decision)
	if err != nil {
		return zero[Out](), record(span, err)
	}
	return out, record(span, s.confirm(ctx, seed))
}

func (s Steps[In, V, D, Out]) confirm(ctx context.Context, seed Seed) error {
	if s.Confirm == nil {
		return nil
	}
	err := s.Confirm(ctx, seed)
	if err == nil {
		return nil
	}
	return errors.Join(err, s.cancel(ctx, seed))
}

func (s Steps[In, V, D, Out]) after(ctx context.Context, seed Seed, in In, out Out, err error) (Out, error) {
	if s.After == nil {
		return out, err
	}
	_, span := start(ctx, "step.50", seed.code)
	defer span.End()
	afterErr := record(span, s.After(ctx, seed, in, out, err))
	if afterErr == nil || err != nil || !s.Critical {
		return out, err
	}
	return zero[Out](), errors.Join(afterErr, s.cancel(ctx, seed))
}

func (s Steps[In, V, D, Out]) cancel(ctx context.Context, seed Seed) error {
	if s.Cancel == nil {
		return nil
	}
	return s.Cancel(ctx, seed)
}

func replay[Out any](ctx context.Context, store IdempotencyStore, seed Seed) (Out, bool, error) {
	_, span := start(ctx, "step.20", seed.code)
	defer span.End()
	raw, found, err := store.Find(ctx, seed.code, seed.idempotencyKey)
	if err != nil || !found {
		return zero[Out](), false, record(span, err)
	}
	var out Out
	return out, true, record(span, json.Unmarshal(raw, &out))
}

func save[Out any](ctx context.Context, store IdempotencyStore, seed Seed, out Out) error {
	raw, err := json.Marshal(out)
	if err != nil {
		return err
	}
	return store.Save(ctx, seed.code, seed.idempotencyKey, raw)
}

func start(ctx context.Context, name, code string) (context.Context, trace.Span) {
	return tracer.Start(ctx, name, trace.WithAttributes(attribute.String("txc.code", code)))
}

func record(span trace.Span, err error) error {
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
	}
	return err
}

func zero[T any]() T {
	var v T
	return v
}
```

O `go.opentelemetry.io/otel` é só a API: sem SDK configurado, o tracer é no-op. Com VC-4 =
`log/slog` apenas, a base funciona igual e não exporta span. O pacote entra na confirmação da
fase 4, como toda dependência.

## O que a base faz

```
op(ctx, call, in)
  1. seed = (code, Call, trace do ctx, chave da entrada)
  2. [10] Check(in)                       falha → devolve, sem [50]
  3. [20] Find(code, key)                 achou → devolve a primeira saída, sem [50]
  4. [40] Validate → ApplyRule → Execute → Confirm; Confirm falhou → Cancel
  5. [50] After, em sucesso e em falha    crítica e falhou depois de gravar → Cancel e erro
  6. [20] Save(code, key, saída)          só em sucesso
```

A chave é gravada depois da `[40]` e da `[50]`. Quando a escrita e a chave precisam ser atômicas, o
adapter de banco implementa as duas na mesma transação de banco. A `[50]` roda síncrona: em Go,
goroutine sem caminho de término é proibida (checklist, item 6). Pânico não vira erro; é defeito e
derruba a requisição pelo `middleware.Recoverer`.

## Uma transação no pacote de domínio

```go
// internal/order/create.go
package order

const CodeCreate = "ORDER.CREATE"

type CreateInput struct {
	Key        string
	CustomerID string
	Items      []Item
}

func (in CreateInput) IdempotencyKey() string { return in.Key }

type CreateResult struct{ Number string }

type createLoaded struct {
	customer Customer
	discount Discount
}

type createExecutor struct {
	customers CustomerReader
	orders    Repository
}

// NewCreate monta a transação ORDER.CREATE; o adapter recebe só o Op.
func NewCreate(customers CustomerReader, orders Repository, store txc.IdempotencyStore) txc.Op[CreateInput, CreateResult] {
	x := createExecutor{customers: customers, orders: orders}
	return txc.NewTransaction(CodeCreate, txc.Steps[CreateInput, createLoaded, Order, CreateResult]{
		Check:     CreateInput.check,
		Validate:  x.validate,
		ApplyRule: x.applyRule,
		Execute:   x.execute,
	}, store)
}

func (in CreateInput) check() error {
	if len(in.Items) == 0 {
		return ErrNoItems
	}
	return nil
}

func (x createExecutor) validate(ctx context.Context, _ txc.Seed, in CreateInput) (createLoaded, error) {
	c, err := x.customers.FindByID(ctx, in.CustomerID)
	if err != nil {
		return createLoaded{}, fmt.Errorf("loading customer: %w", err)
	}
	return createLoaded{customer: c, discount: c.Category().Discount()}, nil
}

func (x createExecutor) applyRule(in CreateInput, l createLoaded) (Order, error) {
	return New(l.customer, in.Items, l.discount)
}

func (x createExecutor) execute(ctx context.Context, _ txc.Seed, o Order) (CreateResult, error) {
	if err := x.orders.Save(ctx, o); err != nil {
		return CreateResult{}, fmt.Errorf("saving order: %w", err)
	}
	return CreateResult{Number: o.Number()}, nil
}
```

`createLoaded` e `Order` são o `TValidation` e o `TDecision` do .NET: o dado de um passo chega ao
seguinte como retorno tipado. O seed não muda; nenhuma função recebe ponteiro para ele.

A consulta usa o `NewQuery`, com uma função só:

```go
// NewGet monta a consulta ORDER.GET.
func NewGet(orders Repository) txc.Op[GetInput, View] {
	return txc.NewQuery(CodeGet, func(ctx context.Context, _ txc.Seed, in GetInput) (View, error) {
		o, err := orders.FindByID(ctx, in.ID)
		if err != nil {
			return View{}, err
		}
		return toView(o), nil
	})
}
```

## Montagem e chamada

```go
// cmd/{binário}/main.go
idem := postgres.NewIdempotencyStore(pool)
orders := postgres.NewOrderStore(pool)
handler := httpadapter.NewOrderHandler(
	order.NewCreate(postgres.NewCustomerStore(pool), orders, idem),
	order.NewGet(orders),
)
```

```go
// internal/adapter/http/call.go
func callFrom(r *http.Request) txc.Call {
	return txc.Call{
		CorrelationID: middleware.GetReqID(r.Context()),
		UserID:        auth.UserID(r.Context()),
		TenantID:      auth.TenantID(r.Context()),
	}
}
```

O adapter preenche o `Call` e chama o `Op`. Não cria o seed nem encadeia passo. Os códigos são
constantes do pacote de cada contexto, um por transação.
