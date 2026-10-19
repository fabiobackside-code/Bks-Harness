# Padrões Go — BKS Stack

Este arquivo é o **delta**: onde a linguagem Go contradiz ou reinterpreta o padrão-base descrito em
`bks-premises.md`. O que não está aqui continua valendo como escrito lá — Hexagonal real,
pipeline explícito, TXC, pragmatismo token-aware.

Go não é C# com chaves. Traduzir o padrão .NET linha a linha produz código que compila e que
nenhum programador Go mantém.

A seção 1 é a tabela de tradução — consulta rápida, a saída padrão da linguagem para cada
construção .NET. As seções 2 a 10 são os pontos onde a tradução literal falha e é preciso entender
por quê.

## 1. Tabela de tradução: o que em .NET vira o quê em Go

Consulta rápida antes de escrever. A coluna da direita é a **saída padrão da linguagem** — o que um
programador Go escreveria. A da esquerda é o que se procura quando se vem do .NET, e quase sempre
não existe em Go por decisão de projeto da linguagem, não por falta.

**A regra que resolve o caso omisso:** se a construção .NET existe para contornar limitação que Go
não tem, ela não tem tradução — some. Se existe para expressar intenção, a intenção se expressa de
outro jeito.

### Linguagem

| .NET / C# | Go | Observação |
|---|---|---|
| `record` | `struct` com campos não exportados + construtor | imutabilidade por disciplina — seção 3 |
| `class` com herança | `struct` + embedding, ou interface | Go não tem herança. Embedding é composição, não `is-a` |
| `interface` implementada explicitamente | `interface` satisfeita estruturalmente | sem `implements`; declarada no consumidor — seção 4 |
| classe abstrata | interface + construtor | não há estado compartilhado por herança |
| `virtual` / `override` | campo de função, ou interface | polimorfismo só por interface |
| `null` | `nil` para ponteiro, slice, map, chan, interface, func | tipo valor **não** pode ser `nil` |
| `Nullable<T>` / `T?` | `*T`, ou `(T, bool)` | ponteiro para opcional real; par para "achou/não achou" |
| `enum` | `type Status int` + `iota` + `String()` | sem verificação de exaustividade no `switch` |
| `throw` / `try-catch` | `return err`, `errors.Is` / `errors.As` | `panic`/`recover` não é fluxo de controle — seção 2 |
| `finally` / `using` | `defer` | executa no retorno da função, não no fim do bloco |
| `IDisposable` | método `Close() error` + `defer` | sem interface de linguagem; convenção |
| `async` / `await` | chamada direta | I/O em Go já é não-bloqueante no runtime; não há função colorida |
| `Task<T>` | valor de retorno direto, ou `chan T` | goroutine + canal quando há concorrência real |
| `CancellationToken` | `context.Context` | primeiro parâmetro, sempre |
| `lock` | `sync.Mutex`, ou canal | "compartilhe memória comunicando", não o inverso |
| LINQ | laço `for` explícito | sem `Where`/`Select` encadeado; o laço é o idioma |
| `var` | `:=` | inferência só dentro de função |
| genérico `where T : IFoo` | `[T Foo]` (Go 1.18+) | use com parcimônia: interface resolve a maioria dos casos |
| método de extensão | função que recebe o tipo | só se pode adicionar método a tipo do próprio pacote |
| propriedade `{ get; set; }` | campo exportado, ou getter/setter explícitos | sem açúcar de propriedade |
| atributo / anotação | struct tag (só serialização), ou código explícito | sem reflexão para comportamento |
| namespace | pacote (= diretório) | um pacote por diretório, nome curto e minúsculo |
| `partial class` | vários arquivos no mesmo pacote | o pacote já é a unidade |
| construtor estático / `Module Initializer` | função `Load() (T, error)` chamada no `main` | `init()` não trata erro — use-o só para registro trivial |
| `internal` | minúscula, ou diretório `internal/` | garantido pelo compilador |
| `ToString()` | `String() string` (`fmt.Stringer`) | |
| `IEquatable<T>` | `==` para struct comparável, ou método `Equal` | |
| `IEnumerable<T>` | slice, ou `iter.Seq[T]` (Go 1.23+) | slice na maioria dos casos |
| `IAsyncEnumerable<T>` | `chan T` com `context` | |
| `dynamic` / `object` | `any` — só em borda de serialização | nunca em contrato de domínio |

### Bibliotecas

| .NET | Go | Observação |
|---|---|---|
| ASP.NET Core Minimal API | `net/http` + chi | `ServeMux` da stdlib até ~10 rotas |
| MediatR | — | já proibido pela premissa; em Go a chamada é direta |
| `IServiceCollection` / Autofac | wiring manual em `main.go` | seção 5 |
| `IHostedService` / `BackgroundService` | laço `for` + `context.Context` | binário comum |
| TopShelf | binário + systemd/contêiner | |
| Akka.NET | goroutine + canal + `sync` | ator é padrão, não framework |
| AutoMapper | função de conversão escrita à mão | mapeamento explícito; sem reflexão |
| FluentValidation | validação no construtor, retornando `error` | `go-playground/validator` só em borda HTTP |
| Dapper | `pgx` direto, ou `sqlc` | query explícita, como já é o default BKS |
| EF Core | — | ORM não entra por padrão |
| Serilog / `ILogger<T>` | `log/slog` (stdlib) | estruturado, sem dependência |
| Polly | retry escrito à mão, com `context` | ~30 linhas; sem biblioteca |
| xUnit | `testing` da stdlib, table-driven | |
| FluentAssertions | `if got != want { t.Fatalf(...) }` | mesma razão de sempre: sem asserção mágica |
| Moq / NSubstitute | struct local que satisfaz a interface | interface pequena torna o dublê trivial |
| Testcontainers | `testcontainers-go` | mesma ideia, mesma biblioteca |
| `System.Text.Json` | `encoding/json` (stdlib) | struct tag para o nome do campo |
| OpenTelemetry .NET | `go.opentelemetry.io/otel` | |
| `IOptions<T>` | struct de config + `Load() (Config, error)` | |
| Swashbuckle | OpenAPI escrito à mão, ou gerado do spec | |

### O que simplesmente não se traduz

Procurar equivalente para estes é o caminho mais curto para código que compila e que ninguém
mantém:

- **Container de DI por reflexão** — o grafo se lê em `main.go`. `dig`/`fx` trocam erro de
  compilação por erro de inicialização
- **Herança de implementação** — não existe. Composição por embedding, ou interface
- **Sobrecarga de método** — um nome, uma função. `CreateOrder` e `CreateOrderWithDiscount`, ou
  functional options
- **Parâmetro opcional / valor default** — functional options, ou struct de parâmetros
- **Exceção como fluxo** — `panic` mata o processo se não houver `recover`; nunca para regra de
  negócio
- **Propriedade computada** — método comum
- **Construtor que lança** — construtor devolve `(T, error)`
- **Atributo que muda comportamento em runtime** — comportamento é código explícito
- **`Result<T>` genérico** — seção 2. É a tentação mais frequente de quem vem de .NET
- **Camada de mapeamento automática** — escreva a função de conversão; ela é lida, versionada e
  depurável

Dois defeitos que a tradução literal não causa, mas que a linguagem permite e o revisor precisa
pegar: **`init()` com trabalho que pode falhar** (não há como devolver erro dali — inicialização
falível é função normal chamada no composition root) e **sombreamento de variável**, sobretudo de
`err` em bloco aninhado, que faz o erro interno ser descartado sem que a leitura acuse. Ambos estão
no checklist de revisão.

## 2. Erro de negócio: `error` idiomático, não `Result[T]`

A premissa diz "erro de negócio não é exceção". Em Go isso já é verdade por construção — a
linguagem não tem exceção de fluxo. A premissa está satisfeita sem nenhum tipo novo.

Um `Result[T]` genérico em Go é ritual importado: quebra o `if err != nil` que toda ferramenta,
todo linter e todo leitor esperam, e não compra nada em troca.

**A forma:** segundo retorno `error`, com tipos de erro próprios do domínio.

```go
package order

import "errors"

var (
	ErrNotFound      = errors.New("order not found")
	ErrAlreadyClosed = errors.New("order already closed")
)

// InsufficientBalanceError carrega o dado que o chamador precisa para decidir.
type InsufficientBalanceError struct {
	Required  Money
	Available Money
}

func (e *InsufficientBalanceError) Error() string {
	return "insufficient balance"
}
```

O chamador discrimina com `errors.Is` (erro sentinela) ou `errors.As` (erro com dado). O adapter
inbound traduz erro de domínio em status HTTP; o domínio nunca conhece `net/http`.

Envelopar com `%w` preserva a cadeia: `fmt.Errorf("closing order %s: %w", id, err)`. Sem `%w` o
`errors.Is` do chamador para de funcionar — regressão silenciosa.

`panic` fica para o que é excepcional de verdade: invariante do programa violada, erro de
programação. Nunca para regra de negócio.

## 3. TXC em Go: struct por valor, imutabilidade por disciplina

Go não tem `record` nem `readonly`. Imutabilidade não é garantida pelo compilador — é sustentada
por três decisões de forma:

- campos **não exportados**, acessíveis só por método getter do mesmo pacote;
- construtor `NewOrderContext(...)` que valida e é o único caminho de criação;
- passagem **por valor**, não por ponteiro, quando o struct é pequeno e o objetivo é não mutar.

```go
type OrderContext struct {
	correlationID string
	tenantID      string
	traceID       string
	requestedAt   time.Time
}

func NewOrderContext(correlationID, tenantID string) (OrderContext, error) {
	if correlationID == "" {
		return OrderContext{}, errors.New("correlation id is required")
	}
	return OrderContext{
		correlationID: correlationID,
		tenantID:      tenantID,
		requestedAt:   time.Now().UTC(),
	}, nil
}

func (c OrderContext) CorrelationID() string { return c.correlationID }
```

**Método com receiver por valor** (`func (c OrderContext)`) não muta o original. Receiver por
ponteiro (`func (c *OrderContext)`) muta — use só onde a mutação é o objetivo declarado.

Para evoluir o contexto ao longo da pipeline sem mutar, devolva uma cópia nova:

```go
func (c OrderContext) WithTraceID(traceID string) OrderContext {
	c.traceID = traceID // c é cópia; o original do chamador não muda
	return c
}
```

**Um campo de slice ou map quebra isso.** Ambos são referências: copiar o struct copia o
ponteiro, e o chamador consegue mutar o conteúdo. Se o contexto carrega coleção, copie na entrada
e devolva cópia no getter — ou aceite que aquele campo não é imutável e documente.

**`context.Context` não é o TXC.** `context.Context` transporta cancelamento, prazo e valores de
infraestrutura; o TXC transporta estado de negócio. Andam juntos na assinatura, nunca fundidos:

```go
func (uc *CreateOrderUseCase) Execute(ctx context.Context, txc OrderContext) (OrderResult, error)
```

## 4. Ports: a interface se declara no consumidor

Este é o ponto que mais inverte o layout hexagonal do .NET. Em Go a interface **pertence ao pacote
que a consome**, não ao que a implementa. Não existe `implements` — a satisfação é estrutural.

Consequência prática: não há um pacote `ports/` com todas as interfaces. Cada pacote de aplicação
declara, junto do código que a usa, a interface mínima de que precisa.

```go
// package order (aplicação) — declara o que precisa
type Repository interface {
	FindByID(ctx context.Context, id string) (Order, error)
	Save(ctx context.Context, o Order) error
}
```

```go
// package postgres (adapter) — implementa sem importar nada de order
type OrderStore struct{ db *sql.DB }

func (s *OrderStore) FindByID(ctx context.Context, id string) (order.Order, error) { ... }
```

A regra de dependência do hexagonal continua intacta — o domínio não importa infraestrutura. O que
muda é onde o arquivo da interface mora.

**Interface pequena.** Duas ou três operações. Uma interface de quinze métodos é um pacote mal
recortado. `interface{}` / `any` só em serialização de borda, nunca em contrato de domínio.

## 5. Composition root: `main.go`, wiring manual

Sem container de DI. Sem Autofac, sem `IServiceCollection`, sem geração por reflexão. O grafo se
monta explicitamente em `cmd/{binário}/main.go`, e essa explicitação é uma vantagem: o grafo
inteiro se lê num arquivo.

```go
func main() {
	cfg := config.Load()
	db := mustOpenDB(cfg.DatabaseURL)
	defer db.Close()

	store := postgres.NewOrderStore(db)
	useCase := order.NewCreateOrderUseCase(store)
	handler := httpadapter.NewOrderHandler(useCase)

	srv := newServer(cfg.Port, handler)
	runUntilSignal(srv)
}
```

`wire` (compile-time) é admissível em grafo grande. `dig`/`fx` (runtime, por reflexão) não —
troca erro de compilação por erro de inicialização.

## 6. Calisthenics em Go: mesmo destino, caminho oposto

A premissa pede "sem `else`, um nível de indentação". Go chega lá pelo idioma oposto ao de C#:
**early return com guard clause**, não polimorfismo.

```go
func (uc *CreateOrderUseCase) Execute(ctx context.Context, txc OrderContext) (OrderResult, error) {
	o, err := uc.repo.FindByID(ctx, txc.OrderID())
	if err != nil {
		return OrderResult{}, fmt.Errorf("loading order: %w", err)
	}
	if o.IsClosed() {
		return OrderResult{}, ErrAlreadyClosed
	}
	// caminho feliz sem indentação
	return uc.process(ctx, o)
}
```

O que **não** se traduz de .NET:

| Regra Calisthenics | Em Go |
|---|---|
| Um nível de indentação | vale, por early return — não por extração de método artificial |
| Sem `else` | vale, e é o idioma nativo |
| Envolver primitivo | só onde há invariante real. `type UserID string` é barato e vale; struct de um campo para todo primitivo, não |
| First-class collections | vale onde há regra sobre o conjunto; slice nu é aceitável quando não há |
| Um ponto por linha | não vale — `errors.Is(err, order.ErrNotFound)` é idiomático |
| Sem getter/setter | inverte, **e só aqui**: ver nota abaixo |

> **Getter em Go: a exceção, não a regra.** A prática comum diz campo exportado direto, sem
> getter nem setter, salvo lógica a encapsular — e está certa para struct de dados (`User{Name
> string}`). O TXC é a exceção: campo não exportado mais getter é o que Go oferece no lugar de
> `record`, e é o **único** modo de impedir mutação (seção 3). Fora de contexto transacional e de
> value object com invariante, getter em Go é cerimônia importada de C# — corte.

## 7. Pipeline explícito

A premissa proíbe MediatR e dispatcher. Em Go a proibição é a mesma, e a implementação é mais
simples do que em .NET: um estágio é uma função com assinatura fixa, e a pipeline é um slice
percorrido em ordem.

```go
type Stage func(ctx context.Context, txc OrderContext) (OrderContext, error)

func Run(ctx context.Context, txc OrderContext, stages ...Stage) (OrderContext, error) {
	for _, stage := range stages {
		next, err := stage(ctx, txc)
		if err != nil {
			return txc, err
		}
		txc = next
	}
	return txc, nil
}
```

Estágio devolve o contexto evoluído em vez de mutar o recebido — coerente com a seção 2. A ordem
fica visível no ponto de composição, não escondida em atributo ou registro.

**Não use `chan` para orquestrar pipeline síncrona.** Canal é para concorrência real. Pipeline de
estágios sequenciais é laço.

## 8. Layout de diretórios

```
cmd/{binário}/main.go        composition root, um por executável
internal/                    tudo que não é API pública — o compilador garante
  {contexto}/                pacote por contexto de domínio, não por camada técnica
    order.go                 tipo, regra e a interface que o pacote consome
    usecase.go
  adapter/
    http/                    inbound
    postgres/                outbound
pkg/                         só se algo é realmente importável de fora
```

**Pacote por contexto, não por camada.** `internal/order/` com tipo, regra e porta juntos — não
`internal/domain/`, `internal/application/`, `internal/ports/` espalhando um contexto por três
diretórios. O `internal/` do Go já dá a garantia de encapsulamento que em .NET se pede a
`InternalsVisibleTo`.

Nome de pacote é minúsculo, curto, sem underscore, e não se repete no identificador: `order.New`,
nunca `order.NewOrder`.

## 9. Testes

`testing` da stdlib, table-driven. Sem framework de asserção — a comunidade não usa, e a premissa
BKS de evitar dependência sem contrapartida vale aqui como vale para FluentAssertions no .NET.

```go
func TestCreateOrder(t *testing.T) {
	tests := []struct {
		name    string
		input   Input
		wantErr error
	}{
		{"pedido válido", validInput(), nil},
		{"saldo insuficiente", noBalanceInput(), ErrInsufficientBalance},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := sut.Execute(context.Background(), tt.input)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("got %v, want %v", err, tt.wantErr)
			}
		})
	}
}
```

Integração com `testcontainers-go`, mesmo princípio do Testcontainers no .NET. `t.Parallel()` onde
o teste não compartilha estado. Dublê é struct local que satisfaz a interface — sem biblioteca de
mock gerada.

## 10. Ferramental que não se discute

| O que | Comando |
|---|---|
| Formatação | `gofmt` — não há estilo alternativo |
| Verificação | `go vet ./...` |
| Corrida de dados | `go test -race ./...` em CI |
| Lint | `golangci-lint run` |
| Versão | a estável mais recente; `go.mod` declara a mínima suportada |

Estas cinco entram no CI. Formatação em Go não é preferência.

> Estrutura completa e entrevista de geração: skill `bks-go-solutions`.
