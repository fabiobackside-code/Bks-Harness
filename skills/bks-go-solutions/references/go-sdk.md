# SDK / biblioteca em Go

Prompt especializado do tipo `SDK`. Pré-requisito: `go-standards.md`, na skill `bks-standards`.

A diferença entre biblioteca e serviço não é técnica, é de compromisso: **a API pública de uma
biblioteca é contrato com quem você não controla.** Cada símbolo exportado é promessa que o
compilador dos outros vai cobrar.

## A regra que governa o resto

**Exporte o mínimo.** Um tipo, uma função, um campo que não precisa ser público fica em minúscula.
Tornar público depois é acréscimo compatível; tornar privado é quebra.

Cada símbolo exportado é peso permanente. Em Go isso é mais severo que em .NET: não há `internal`
de assembly nem `InternalsVisibleTo` — o que está fora de `internal/` e é maiúsculo, é API.

## Layout

```
{sdk}/
  client.go                  o tipo de entrada
  options.go                 functional options
  errors.go                  erros sentinela e tipados exportados
  {recurso}.go               um arquivo por recurso da API
  internal/
    transport/               HTTP, retry, autenticação — invisível de fora
  example_test.go            exemplos executáveis
  go.mod
```

Raiz do módulo é a API pública. `internal/` é fechado pelo compilador — ninguém importa, e você
refatora sem quebrar consumidor. Use `internal/` generosamente; é a única fronteira real que Go dá.

`pkg/` não é necessário quando o módulo já é a biblioteca.

## Construção: functional options

O construtor com muitos parâmetros envelhece mal — cada opção nova quebra a assinatura. Functional
options é o idioma Go para isso:

```go
type Client struct {
	baseURL    string
	httpClient *http.Client
	timeout    time.Duration
	logger     *slog.Logger
}

type Option func(*Client)

func WithHTTPClient(hc *http.Client) Option {
	return func(c *Client) { c.httpClient = hc }
}

func WithTimeout(d time.Duration) Option {
	return func(c *Client) { c.timeout = d }
}

func New(apiKey string, opts ...Option) (*Client, error) {
	if apiKey == "" {
		return nil, ErrMissingAPIKey
	}

	c := &Client{
		baseURL:    defaultBaseURL,
		httpClient: http.DefaultClient,
		timeout:    30 * time.Second,
		logger:     slog.Default(),
	}
	for _, opt := range opts {
		opt(c)
	}
	return c, nil
}
```

Obrigatório é parâmetro posicional; opcional é `Option`. Adicionar opção nova é sempre compatível.

**Aceite `*http.Client` do chamador.** Ele já tem transporte com proxy, TLS corporativo, timeout e
instrumentação configurados. SDK que constrói o próprio cliente sem permitir substituição é
inutilizável em ambiente com política de rede.

## `context.Context` em toda operação de rede

```go
func (c *Client) GetOrder(ctx context.Context, id string) (Order, error)
```

Primeiro parâmetro, sempre, sem exceção. Nunca guarde `context.Context` em campo de struct.

SDK sem `context` não pode ter chamada cancelada nem prazo imposto pelo chamador — defeito que só
aparece em produção, quando um serviço lento trava quem consome.

## Erros: sentinelas e tipos exportados

```go
var (
	ErrNotFound     = errors.New("resource not found")
	ErrUnauthorized = errors.New("unauthorized")
	ErrRateLimited  = errors.New("rate limited")
)

// APIError carries the server response for callers that need the detail.
type APIError struct {
	StatusCode int
	Code       string
	Message    string
	RequestID  string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("api error %d (%s): %s", e.StatusCode, e.Code, e.Message)
}

func (e *APIError) Is(target error) bool {
	switch {
	case e.StatusCode == http.StatusNotFound:
		return target == ErrNotFound
	case e.StatusCode == http.StatusUnauthorized:
		return target == ErrUnauthorized
	}
	return false
}
```

O consumidor discrimina com `errors.Is` sem inspecionar string. `RequestID` na estrutura de erro é
o que permite ao suporte rastrear a chamada.

Sentinela exportada é API: renomear ou remover quebra. Publique só as que o consumidor precisa
distinguir.

## Retry

Só em erro transitório: 429, 5xx, timeout de rede. Nunca em 4xx de cliente — retentar 400 é laço
inútil.

Backoff exponencial com jitter. Sem jitter, mil clientes que falharam juntos retornam juntos e
derrubam o servidor de novo.

Respeite `Retry-After` quando o servidor mandar, e limite a tentativa pelo `ctx` — o prazo do
chamador manda sobre a política de retry do SDK.

Retry por padrão precisa ser desligável (`WithRetry(0)`): quem já tem política própria não quer a
sua por cima.

## Concorrência

Documente explicitamente se o cliente é seguro para uso concorrente. `*http.Client` é; se o seu
tipo o é também, diga no comentário do `Client` — o consumidor precisa saber se pode compartilhar
uma instância entre goroutines ou se cria uma por uso.

Um SDK que não declara isso força quem consome a assumir o pior.

## Dependências

Idealmente zero além da stdlib. Cada dependência do SDK entra no `go.mod` de todo consumidor e
pode conflitar com o que ele já usa.

Antes de adicionar: dá para fazer com a stdlib com esforço razoável? Quase sempre dá, para HTTP,
JSON e retry.

## Versionamento

SemVer, aplicado a sério — o Go module proxy o obriga.

`v0.x.y` admite quebra; é onde a API amadurece. Chegar em `v1.0.0` é declarar estabilidade, e a
partir dali quebra exige `/v2` no caminho do módulo, com o consumidor migrando manualmente. Não
promova a v1 antes de a API ter sido usada por alguém que não é você.

Depreciar sem quebrar: manter o símbolo e marcar `// Deprecated: use X instead.` — os editores
avisam.

## Documentação

`go doc` é a documentação. Comentário de símbolo exportado começa pelo nome do símbolo:

```go
// Client is a thread-safe client for the Order API.
type Client struct{ ... }
```

`example_test.go` com funções `Example` compila, roda em `go test` e aparece no pkg.go.dev — é
documentação que o CI verifica. Documentação que não compila apodrece.

`doc.go` no pacote raiz com a visão geral e o exemplo mínimo de uso.

## Testes

Table-driven no comportamento; `httptest.NewServer` para simular a API remota sem rede.

Teste que não pode faltar num SDK: **compatibilidade da superfície pública.** Se a API sumir ou
mudar de assinatura, os próprios exemplos param de compilar — mais uma razão para eles existirem.

## Antes de fechar

`gofmt` · `go vet ./...` · `go test -race ./...` · `golangci-lint run` · `go doc ./...` legível ·
README com instalação e exemplo mínimo · ARCHITECTURE.
