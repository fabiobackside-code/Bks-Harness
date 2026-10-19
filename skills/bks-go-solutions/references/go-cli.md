# CLI / ferramenta em Go

Prompt especializado do tipo `CLI`. Pré-requisito: `go-standards.md`, na skill `bks-standards`.

Go é a linguagem certa para CLI porque compila num binário estático sem runtime: o usuário baixa
um arquivo e roda. Não desperdice isso adicionando dependência que não paga o próprio preço.

## Parser (VT-L2)

Até três subcomandos, `flag` da stdlib com `flag.NewFlagSet` por subcomando. Acima disso, ou com
necessidade de completion de shell e ajuda hierárquica, cobra.

O erro comum é começar com cobra por hábito: uma ferramenta de dois comandos ganha estrutura de
seis arquivos gerados para resolver o que trinta linhas de stdlib resolvem.

## Layout

```
cmd/{ferramenta}/main.go
internal/
  command/                   um arquivo por subcomando
  {contexto}/                a regra, sem nada de CLI
  platform/config/
```

A lógica fica em `internal/{contexto}`, testável sem invocar a linha de comando. `internal/command`
é adapter inbound — só faz parsing, chamada e formatação. É a mesma fronteira do handler HTTP.

## Estrutura

```go
func main() {
	if err := run(os.Args[1:], os.Stdout, os.Stderr); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func run(args []string, stdout, stderr io.Writer) error {
	if len(args) == 0 {
		printUsage(stderr)
		return errors.New("no command given")
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	switch args[0] {
	case "import":
		return command.Import(ctx, args[1:], stdout)
	case "verify":
		return command.Verify(ctx, args[1:], stdout)
	case "version":
		fmt.Fprintln(stdout, buildVersion())
		return nil
	default:
		printUsage(stderr)
		return fmt.Errorf("unknown command: %s", args[0])
	}
}
```

`run` recebe args e writers em vez de ler `os.Args` e escrever em `os.Stdout` direto. É o que torna
a CLI inteira testável — sem isso, testar exige subprocesso.

Ctrl+C cancela o `ctx`, e a operação em curso encerra por onde já está preparada para encerrar.

## Convenções que o usuário espera

| Convenção | Regra |
|---|---|
| Saída útil | `stdout`. Só o resultado |
| Log, erro, progresso | `stderr`. Nunca `stdout` |
| Código de saída | 0 sucesso, não-zero falha. Distinto por classe de erro quando útil |
| `--help` | em todo comando e subcomando |
| `--version` | com versão, commit e data de build |
| Pipe | detectar `stdin` não-tty e ler dele |
| `NO_COLOR` | respeitar, e desligar cor quando `stdout` não é tty |

Misturar log com resultado no `stdout` quebra todo uso em pipeline — é o defeito mais comum em CLI
gerada por IA.

## Saída em texto e JSON (VT-L3)

```go
type Renderer interface {
	Render(w io.Writer, result Result) error
}

func rendererFor(format string) (Renderer, error) {
	switch format {
	case "text", "":
		return textRenderer{}, nil
	case "json":
		return jsonRenderer{}, nil
	default:
		return nil, fmt.Errorf("unsupported format: %s", format)
	}
}
```

`--output json` é o que torna a ferramenta componível com `jq` e utilizável em script. O formato
JSON é contrato: mudá-lo quebra automação de terceiro, e vale o mesmo cuidado de uma API.

## Versão no build

```go
var (
	version = "dev"
	commit  = "none"
	date    = "unknown"
)
```

Injetadas por `-ldflags "-X main.version=$(VERSION)"`. Sem isso, o suporte não sabe qual binário o
usuário está rodando.

`go build -trimpath` remove caminho absoluto da máquina de build — evita vazar estrutura de
diretório no binário distribuído.

## Configuração

Precedência: flag > variável de ambiente > arquivo de configuração > default. Nessa ordem, sempre.

Segredo nunca vem por flag: argumento aparece em `ps` e no histórico do shell. Variável de
ambiente, arquivo com permissão restrita ou `stdin`.

## Testes

```go
func TestImportRejectsMissingFile(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := run([]string{"import", "--file", "ausente.csv"}, &stdout, &stderr)

	if !errors.Is(err, os.ErrNotExist) {
		t.Fatalf("got %v, want os.ErrNotExist", err)
	}
	if stdout.Len() != 0 {
		t.Errorf("stdout should stay empty on failure, got %q", stdout.String())
	}
}
```

`run` isolado testa a CLI inteira em memória. Para saída extensa e estável, golden file com
`-update` — mas só onde o formato já assentou; golden file de formato em evolução vira ruído.

Filesystem por `t.TempDir()`, limpo automaticamente.

## Distribuição

`GOOS`/`GOARCH` cruzam a compilação sem toolchain externa. `CGO_ENABLED=0` garante o binário
estático. Um binário por plataforma, com checksum publicado.

## Antes de fechar

`gofmt` · `go vet ./...` · `go test -race ./...` · `golangci-lint run` · README com exemplo de cada
comando · ARCHITECTURE.
