# Worker / background service em Go

Prompt especializado do tipo `WORKER`. Pré-requisito: `go-standards.md`, na skill `bks-standards`.

Em Go não há `IHostedService` nem TopShelf. O worker é um binário comum que roda um laço até o
`context.Context` ser cancelado. Isso é vantagem: o mesmo binário roda em contêiner, em systemd e
no terminal do desenvolvedor, sem host intermediário.

## Layout

```
cmd/{binário}/main.go
internal/
  {contexto}/                regra e a interface consumida
  worker/                    runner.go, job.go
  adapter/postgres/
  platform/config/
```

## A forma do laço

Toda unidade de trabalho é uma função com assinatura fixa. O runner ordena a execução, trata erro
e respeita o cancelamento.

```go
type Job interface {
	Name() string
	Run(ctx context.Context) error
}

type Runner struct {
	job      Job
	interval time.Duration
	log      *slog.Logger
}

func (r *Runner) Start(ctx context.Context) error {
	ticker := time.NewTicker(r.interval)
	defer ticker.Stop()

	for {
		if err := r.runOnce(ctx); err != nil {
			r.log.Error("job failed", "job", r.job.Name(), "err", err)
		}

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
		}
	}
}
```

Erro de uma execução **não derruba o worker** — loga e segue para o próximo tick. Derrubar por
falha transitória transforma indisponibilidade do banco em reinício em laço.

`runOnce` isola a execução para que um `panic` num job não mate o processo:

```go
func (r *Runner) runOnce(ctx context.Context) (err error) {
	defer func() {
		if rec := recover(); rec != nil {
			err = fmt.Errorf("panic in job %s: %v", r.job.Name(), rec)
		}
	}()

	jobCtx, cancel := context.WithTimeout(ctx, r.timeout)
	defer cancel()

	return r.job.Run(jobCtx)
}
```

`recover` só aqui, na fronteira do runner. Espalhar `recover` pelo domínio esconde defeito.

Timeout por execução é obrigatório: sem ele, uma consulta travada trava o worker para sempre.

## Shutdown

```go
func run() error {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	runner := worker.NewRunner(job, cfg.Interval, logger)

	if err := runner.Start(ctx); err != nil && !errors.Is(err, context.Canceled) {
		return err
	}
	logger.Info("worker stopped")
	return nil
}
```

`context.Canceled` é término esperado, não falha — não vaza como erro de saída. O `select` no laço
garante que o SIGTERM interrompe a espera imediatamente, sem aguardar o tick.

Para trabalho longo, o job também precisa checar `ctx.Done()` internamente. Quem só verifica entre
ciclos ignora o shutdown por toda a duração de uma execução.

## Concorrência (VT-W3)

Serial por padrão. Só paralelize quando a medição justificar.

Com N goroutines, `errgroup` limita e propaga:

```go
func (r *Runner) processBatch(ctx context.Context, items []Item) error {
	g, ctx := errgroup.WithContext(ctx)
	g.SetLimit(r.workers)

	for _, item := range items {
		g.Go(func() error {
			return r.handle(ctx, item)
		})
	}
	return g.Wait()
}
```

`SetLimit` é o que impede o worker de abrir mil conexões simultâneas ao processar um lote grande.

A partir do Go 1.22 a variável de laço é nova a cada iteração — a captura acima é segura. Em
módulo declarando `go` anterior a 1.22, a semântica antiga vale e é preciso `item := item`.

**Toda goroutine precisa de caminho de término.** Goroutine sem quem a espere e sem cancelamento é
vazamento — o equivalente Go de thread órfã.

## Fila em PostgreSQL (VT-W2)

Não introduza broker para o que a tabela resolve. Locking por `FOR UPDATE SKIP LOCKED`:

```go
const claimQuery = `
	UPDATE jobs
	   SET status = 'processing', claimed_at = now()
	 WHERE id IN (
	       SELECT id FROM jobs
	        WHERE status = 'pending' AND run_after <= now()
	        ORDER BY run_after
	        LIMIT $1
	        FOR UPDATE SKIP LOCKED
	 )
	RETURNING id, payload`
```

`SKIP LOCKED` deixa várias réplicas do worker consumirem a mesma tabela sem colidir e sem
bloquear. Reivindicar e processar na mesma transação garante que o job não some se o processo cair.

Cada job carrega `attempts`; ao estourar o máximo, vai para `failed` com o erro registrado —
o dead letter da fila em banco.

## Idempotência

Worker reexecuta: reinício, redeploy, timeout com efeito já aplicado. Todo job precisa tolerar
processar duas vezes o mesmo item. Chave de idempotência com `UNIQUE` no banco é o mecanismo mais
barato; contar com "não vai acontecer" não é mecanismo.

## Observabilidade

`log/slog` estruturado, com o campo de correlação em todo registro do job. Cada execução emite
início, fim, duração e resultado. Sem isso, worker é caixa-preta — falha silenciosa passa semanas
despercebida.

Com OpenTelemetry (VC-4), um span por execução, e o contexto propagado para o adapter de saída.

## Testes

Job é função com dependências injetadas — teste direto, table-driven, sem subir o runner.

Para o runner, `context.WithCancel` e verificação de que `Start` retorna ao cancelar:

```go
func TestRunnerStopsOnCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	r := NewRunner(noopJob{}, time.Millisecond, slog.Default())

	go func() {
		time.Sleep(10 * time.Millisecond)
		cancel()
	}()

	if err := r.Start(ctx); !errors.Is(err, context.Canceled) {
		t.Fatalf("got %v, want context.Canceled", err)
	}
}
```

`go test -race ./...` não é opcional em worker concorrente.

## Antes de fechar

`gofmt` · `go vet ./...` · `go test -race ./...` · `golangci-lint run` · README e ARCHITECTURE.
