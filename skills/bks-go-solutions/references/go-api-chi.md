# API REST em Go — `net/http` + chi

Prompt especializado do tipo `API`. Pré-requisito: `go-standards.md`, na skill `bks-standards`.

## Por que chi e não framework

Desde o Go 1.22 o `ServeMux` da stdlib roteia por método e por padrão de caminho
(`mux.HandleFunc("GET /orders/{id}", h)`). Para API pequena isso basta e não adiciona dependência.

chi entra quando há middleware por grupo, sub-router montado por contexto, ou mais de uma dúzia de
rotas. Ele é `http.Handler` puro — o handler continua com a assinatura da stdlib, sem tipo próprio
de contexto. Gin e Echo trocam essa compatibilidade por açúcar, e o custo aparece no dia em que se
quer usar qualquer middleware `net/http` de terceiro.

Regra: até ~10 rotas sem middleware por grupo, `ServeMux`. Acima disso, chi.

## Layout

```
cmd/{binário}/main.go
internal/
  {contexto}/                order.go, usecase.go, errors.go, port.go
  adapter/
    http/                    handler.go, router.go, middleware/, problem.go
    postgres/                store.go, queries.sql
  platform/
    config/                  config.go
    observability/           logger.go, tracing.go
migrations/
go.mod
```

Um diretório por contexto em `internal/`, com o tipo, a regra e a interface que ele consome no
mesmo pacote. Não crie `internal/domain/`, `internal/application/` e `internal/ports/` — isso é o
layout .NET traduzido, e espalha um contexto por três lugares.

## Composition root

```go
func main() {
	if err := run(); err != nil {
		slog.Error("fatal", "err", err)
		os.Exit(1)
	}
}

func run() error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("loading config: %w", err)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	pool, err := pgxpool.New(ctx, cfg.DatabaseURL)
	if err != nil {
		return fmt.Errorf("connecting to database: %w", err)
	}
	defer pool.Close()

	store := postgres.NewOrderStore(pool)
	useCase := order.NewCreateOrderUseCase(store)
	handler := httpadapter.NewOrderHandler(useCase)

	srv := &http.Server{
		Addr:              cfg.Addr(),
		Handler:           httpadapter.NewRouter(handler),
		ReadHeaderTimeout: 5 * time.Second,
	}
	return serve(ctx, srv)
}
```

`main` fino chamando `run() error` é o idioma: `os.Exit` pula os `defer`, então tudo que precisa
de limpeza fica dentro de `run`.

## Graceful shutdown

```go
func serve(ctx context.Context, srv *http.Server) error {
	errCh := make(chan error, 1)
	go func() {
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()

	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()
		return srv.Shutdown(shutdownCtx)
	}
}
```

O `context.WithTimeout` do shutdown parte de `context.Background()`, não do `ctx` já cancelado —
senão o prazo de drenagem nasce vencido. Erro comum e silencioso.

`ReadHeaderTimeout` fecha o Slowloris. Sem ele, `gosec` acusa (G112) e está certo.

## Router

```go
func NewRouter(h *OrderHandler) http.Handler {
	r := chi.NewRouter()

	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(30 * time.Second))

	r.Get("/health", healthHandler)

	r.Route("/orders", func(r chi.Router) {
		r.Use(RequireAuth)
		r.Post("/", h.Create)
		r.Get("/{id}", h.GetByID)
	})
	return r
}
```

Health check fora do grupo autenticado. Todo o resto dentro — a autenticação é opt-out explícito,
nunca opt-in esquecido.

## Handler: fronteira, não lógica

```go
func (h *OrderHandler) Create(w http.ResponseWriter, r *http.Request) {
	var req createOrderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeProblem(w, http.StatusBadRequest, "malformed body")
		return
	}

	txc, err := order.NewOrderContext(middleware.GetReqID(r.Context()), req.TenantID)
	if err != nil {
		writeProblem(w, http.StatusBadRequest, err.Error())
		return
	}

	result, err := h.useCase.Execute(r.Context(), txc, req.toInput())
	if err != nil {
		writeError(w, err)
		return
	}

	writeJSON(w, http.StatusCreated, toResponse(result))
}
```

O handler decodifica, monta o TXC, chama o use case e traduz. Nenhuma regra de negócio. DTO de
request e response ficam no pacote do adapter, não no de domínio — o contrato HTTP não vaza para
dentro.

## Tradução de erro num lugar só

```go
func writeError(w http.ResponseWriter, err error) {
	var insufficient *order.InsufficientBalanceError

	switch {
	case errors.Is(err, order.ErrNotFound):
		writeProblem(w, http.StatusNotFound, "order not found")
	case errors.Is(err, order.ErrAlreadyClosed):
		writeProblem(w, http.StatusConflict, "order already closed")
	case errors.As(err, &insufficient):
		writeProblem(w, http.StatusUnprocessableEntity, insufficient.Error())
	default:
		slog.Error("unhandled error", "err", err)
		writeProblem(w, http.StatusInternalServerError, "internal error")
	}
}
```

Uma função traduz erro de domínio em status. Espalhar isso pelos handlers garante divergência.
O caso `default` loga o erro real e devolve mensagem genérica — detalhe interno não sai na resposta.

Formato de erro: RFC 9457 (`application/problem+json`).

## Persistência

```go
type OrderStore struct{ pool *pgxpool.Pool }

func NewOrderStore(pool *pgxpool.Pool) *OrderStore { return &OrderStore{pool: pool} }

func (s *OrderStore) FindByID(ctx context.Context, id string) (order.Order, error) {
	const q = `SELECT id, tenant_id, status, total FROM orders WHERE id = $1`

	var row orderRow
	err := s.pool.QueryRow(ctx, q, id).Scan(&row.ID, &row.TenantID, &row.Status, &row.Total)
	if errors.Is(err, pgx.ErrNoRows) {
		return order.Order{}, order.ErrNotFound
	}
	if err != nil {
		return order.Order{}, fmt.Errorf("querying order %s: %w", id, err)
	}
	return row.toDomain()
}
```

`pgx.ErrNoRows` vira `order.ErrNotFound` na borda: o erro do driver não sobe. Query explícita,
parametrizada, sem concatenação. Tabela em `snake_case`.

## Testes

Handler com `httptest`, dublê como struct local:

```go
type stubUseCase struct {
	result order.Result
	err    error
}

func (s stubUseCase) Execute(context.Context, order.OrderContext, order.Input) (order.Result, error) {
	return s.result, s.err
}

func TestCreateReturns409WhenClosed(t *testing.T) {
	h := NewOrderHandler(stubUseCase{err: order.ErrAlreadyClosed})
	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/orders", strings.NewReader(`{"tenantId":"t1"}`))

	h.Create(rec, req)

	if rec.Code != http.StatusConflict {
		t.Fatalf("got %d, want %d", rec.Code, http.StatusConflict)
	}
}
```

Integração com `testcontainers-go` subindo o Postgres real e aplicando as migrations.

## Antes de fechar

`gofmt` · `go vet ./...` · `go test -race ./...` · `golangci-lint run` · README e ARCHITECTURE.
