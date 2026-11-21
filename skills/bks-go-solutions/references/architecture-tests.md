# Teste de arquitetura dos pacotes

> Gerado junto com o código, em `internal/architecture_test.go`, e rodado pelo `go test ./...`. Sem
> dependência nova: só `go/parser` da biblioteca padrão.

## O que ele guarda

| Teste | Regra | Barra |
|---|---|---|
| `TestContextsDoNotImportAdapters` | `COD-05` | pacote de contexto em `internal/{contexto}` importando `internal/adapter/...` |
| `TestAdaptersDoNotImportEachOther` | `COD-05` | um adapter importando outro (`adapter/http` citando `adapter/postgres`): a entrada fala com o contexto, nunca com a saída |
| `TestNoGenericResult` | `COD-19` | tipo `Result[T]` declarado ou usado; erro é `error` no segundo retorno |

A camada vem do caminho: `internal/adapter/<nome>` é adapter, `internal/platform/...` é
infraestrutura compartilhada, e o resto de `internal/` é contexto. Arquivo `_test.go` fica fora.

## O teste

```go
package internal_test

import (
	"go/ast"
	"go/parser"
	"go/token"
	"io/fs"
	"path/filepath"
	"strings"
	"testing"
)

type goFile struct {
	rel  string
	file *ast.File
}

func sources(t *testing.T) []goFile {
	t.Helper()
	var out []goFile
	fset := token.NewFileSet()
	err := filepath.WalkDir(".", func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, ".go") || strings.HasSuffix(path, "_test.go") {
			return err
		}
		f, perr := parser.ParseFile(fset, path, nil, parser.SkipObjectResolution)
		if perr != nil {
			return perr
		}
		out = append(out, goFile{rel: filepath.ToSlash(path), file: f})
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	return out
}

func area(rel string) (kind, name string) {
	parts := strings.Split(rel, "/")
	switch {
	case parts[0] == "adapter" && len(parts) > 2:
		return "adapter", parts[1]
	case parts[0] == "platform":
		return "platform", ""
	default:
		return "context", parts[0]
	}
}

func importedAdapter(path string) string {
	i := strings.Index(path, "/internal/adapter/")
	if i < 0 {
		return ""
	}
	return strings.Split(path[i+len("/internal/adapter/"):], "/")[0]
}

func TestContextsDoNotImportAdapters(t *testing.T) {
	for _, src := range sources(t) {
		if kind, _ := area(src.rel); kind != "context" {
			continue
		}
		for _, imp := range src.file.Imports {
			if importedAdapter(strings.Trim(imp.Path.Value, `"`)) != "" {
				t.Errorf("%s importa %s: o contexto declara a interface, o adapter a implementa", src.rel, imp.Path.Value)
			}
		}
	}
}

func TestAdaptersDoNotImportEachOther(t *testing.T) {
	for _, src := range sources(t) {
		kind, name := area(src.rel)
		if kind != "adapter" {
			continue
		}
		for _, imp := range src.file.Imports {
			if other := importedAdapter(strings.Trim(imp.Path.Value, `"`)); other != "" && other != name {
				t.Errorf("%s importa o adapter %s: a entrada fala com o contexto", src.rel, other)
			}
		}
	}
}

func TestNoGenericResult(t *testing.T) {
	for _, src := range sources(t) {
		ast.Inspect(src.file, func(n ast.Node) bool {
			var name string
			switch node := n.(type) {
			case *ast.TypeSpec:
				name = node.Name.Name
			case *ast.IndexExpr:
				if id, ok := node.X.(*ast.Ident); ok {
					name = id.Name
				}
			case *ast.IndexListExpr:
				if id, ok := node.X.(*ast.Ident); ok {
					name = id.Name
				}
			}
			if name == "Result" {
				t.Errorf("%s usa Result[T]: em Go o erro é error no segundo retorno", src.rel)
				return false
			}
			return true
		})
	}
}
```
