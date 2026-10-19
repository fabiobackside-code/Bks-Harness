# Convenção de comentário — regra e guarda executável

O código carrega **o quê**. O `ARCHITECTURE.md` carrega **o porquê**.

Quem desenhou o código o entende sem comentário; quem não desenhou lê o `ARCHITECTURE.md`.
Comentário que ensaia arquitetura dentro do arquivo não serve a nenhum dos dois — e envelhece sem
ninguém notar, porque nada o testa.

---

## As três categorias

| Categoria | No código? | Formato |
|---|---|---|
| **A · Contrato** | sim | `/// <summary>` de 1 linha em membro público — o **quê**, nunca o **como** |
| **B · Guarda contra regressão** | sim, até 2 linhas | só quando editar aquela linha desfaz uma decisão. O que quebra, sem ponteiro |
| **C · Decisão, trade-off, histórico** | **não** | vive no `ARCHITECTURE.md` |

### Por que B existe

A guarda precisa ser lida **no ponto da edição**. Quem for "modernizar" um tipo para `record` não
vai abrir outro arquivo antes de fazê-lo. Mover a guarda inteira para o `ARCHITECTURE.md` destrói a
função dela. A guarda diz o que quebra; o porquê completo fica no `ARCHITECTURE.md`, que diz na
abertura para que serve, e o comentário não aponta para ele.

```csharp
// ✅ B correto — o que quebra, 2 linhas
/// <summary>Configuração da capacidade de segredos.</summary>
/// <remarks>Não é record — ToString() gerado exporia a ApiKey.</remarks>
public sealed class NqSecretOptions

// ❌ C — o raciocínio inteiro dentro do arquivo
/// <remarks>
/// <b>Não é record.</b> record gera ToString() automático com todas as propriedades, e Value é
/// string — escalar, portanto impressa por inteiro. O segredo vazaria em qualquer log de
/// diagnóstico. Probe de 28/08 mostrou que o ToString() de record não despeja o conteúdo de
/// coleções — imprime o nome do tipo. Aqui o risco é real porque o valor é escalar; em tipos que
/// guardam só coleções o argumento seria outro (construtor público e with).
/// </remarks>
```

### Exceção — ausência deliberada de código

Comentário que explica código que **não está ali**. Nenhum leitor infere do código o que não foi
escrito. Teto de 2 linhas.

```csharp
// Não rebusca em kid desconhecido: viraria DoS contra o próprio IdP [E4].
return Reject("kid: chave desconhecida");
```

---

## Proibido

- Bloco de trade-off, comparação com implementação anterior, histórico de decisão
- Comentário que só repete o nome do membro
- **Marca de severidade** (🔴 ⚠️ 🟡 ✅ 📌) — quem escreve 🔴 está argumentando, não descrevendo
- **Bloco acima de 5 linhas**

### O teto é por bloco, não por proporção

Proporção é métrica ruim: um enum bem documentado é quase todo `summary` e **está certo**, enquanto
um arquivo grande esconde um ensaio de 12 linhas dentro de uma razão baixa.

O que a categoria C tem de próprio é o **bloco longo** — ninguém escreve seis linhas seguidas para
dizer *o quê*.

---

## O guarda executável

**Regra sem teste é intenção, e intenção não sobrevive à pressa.** Gerar junto com o código, em
`tests/{Projeto}.Tests/Architecture/`.

```csharp
namespace {Projeto}.Tests.Architecture;

/// <summary>Guarda a convenção de comentário: o código carrega o quê, o ARCHITECTURE.md o porquê.</summary>
public sealed class CommentBudgetTests
{
    private const int MaxBlockLines = 5;

    private static readonly string[] ForbiddenMarkers = ["🔴", "⚠️", "🟡", "✅", "📌"];

    private static IEnumerable<FileInfo> SourceFiles =>
        new DirectoryInfo(SourceRoot)
            .EnumerateFiles("*.cs", SearchOption.AllDirectories)
            .Where(file => !file.FullName.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !file.FullName.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"));

    [Fact]
    public void No_comment_block_grows_into_an_essay()
    {
        var offenders = SourceFiles
            .SelectMany(file => LongBlocks(file)
                .Select(block => $"{file.Name}:{block.Start} — {block.Length} linhas seguidas"))
            .ToList();

        Assert.True(
            offenders.Count == 0,
            $"Bloco acima de {MaxBlockLines} linhas é decisão, e decisão vive no ARCHITECTURE.md:"
            + Environment.NewLine + string.Join(Environment.NewLine, offenders));
    }

    [Fact]
    public void No_comment_carries_a_severity_marker()
    {
        var offenders = new List<string>();

        foreach (var file in SourceFiles)
        {
            var number = 0;

            foreach (var line in File.ReadLines(file.FullName))
            {
                number++;

                if (!IsComment(line))
                {
                    continue;
                }

                var marker = ForbiddenMarkers.FirstOrDefault(line.Contains);

                if (marker is not null)
                {
                    offenders.Add($"{file.Name}:{number} carrega '{marker}'");
                }
            }
        }

        Assert.True(
            offenders.Count == 0,
            "Marca de severidade indica argumento, não contrato:"
            + Environment.NewLine + string.Join(Environment.NewLine, offenders));
    }

    private static IEnumerable<(int Start, int Length)> LongBlocks(FileInfo file)
    {
        var lines = File.ReadAllLines(file.FullName);
        var start = 0;
        var length = 0;

        for (var index = 0; index < lines.Length; index++)
        {
            if (IsComment(lines[index]))
            {
                if (length == 0)
                {
                    start = index + 1;
                }

                length++;

                continue;
            }

            if (length > MaxBlockLines)
            {
                yield return (start, length);
            }

            length = 0;
        }

        if (length > MaxBlockLines)
        {
            yield return (start, length);
        }
    }

    private static bool IsComment(string line)
    {
        var trimmed = line.TrimStart();

        return trimmed.StartsWith("//", StringComparison.Ordinal)
            || trimmed.StartsWith("/*", StringComparison.Ordinal)
            || trimmed.StartsWith("*", StringComparison.Ordinal);
    }
}
```

`SourceRoot` resolve subindo a árvore até achar a solution — não use caminho relativo fixo, porque
o diretório de trabalho muda entre `dotnet test` na raiz e execução pela IDE.

---

## Retrofit em repositório já pronto

Nunca o repo inteiro de uma vez — o diff fica inviável de revisar.

1. **Por pasta**, na ordem da dependência: `Domain` → `Ports` → `Adapters` → `Infrastructure`
2. Escrever o `ARCHITECTURE.md` **antes** — é o destino do material que sai; sem ele o conteúdo se
   perde em vez de mudar de lugar
3. Escrever o teste **antes** do retrofit: dá alvo objetivo, em vez de julgar arquivo a arquivo
4. Revisar o diff a cada pasta

> ⚠️ **Um teste de arquitetura pode depender de texto no comentário.** No `nq-sec-sdk`, dois testes
> exigiam a marcação `PRESUMIDO`/`RK-E` no código do adaptador HSM — e o retrofit a apagou. Rodar a
> suíte completa a cada pasta, não só no fim.
