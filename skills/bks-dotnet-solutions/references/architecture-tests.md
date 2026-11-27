# Teste de arquitetura das camadas

> Gerado junto com o código, em `src/{ServiceName}.Tests/Architecture/LayerDependencyTests.cs`, ao
> lado do `CommentBudgetTests` (`references/comment-convention.md`). Sem pacote novo: o teste lê o
> código-fonte como texto, e o xUnit do projeto de testes basta.

## O que ele guarda

| Teste | Regra | Barra |
|---|---|---|
| `Domain_references_only_System` | `COD-04` | `using` no Domain que não seja `System.*` nem o próprio Domain (`using Npgsql;`) |
| `Layers_depend_inward` | `COD-05` | Domain citando Application ou Adapters; Application citando Adapters; adapter de entrada citando o de saída e vice-versa. Vale para `using` e para nome qualificado no código |
| `Spans_come_from_the_pipeline` | `COD-07` | `new Activity(` ou `.StartActivity(` fora de `Application/Pipeline/` e do adapter de observabilidade |
| `No_dynamic` | `COD-13` | o tipo `dynamic` em qualquer camada |
| `Sql_takes_only_parameters` | `SEC-01` | SQL em string interpolada (`$"... WHERE id = {id}"`), concatenada com valor (`"... = '" + id`) ou passada ao `string.Format`. Passam o `@param` do Dapper e o `FromSql`/`ExecuteSql` do EF Core, que parametrizam a interpolação |

A camada de cada arquivo sai da pasta (`Domain/`, `Application/`, `Adapters/Inbound/`,
`Adapters/Outbound/`, `main/`) ou do projeto (`.Domain`, `.Application`, `.Adapters.Inbound`,
`.Adapters.Outbound`, `.Host`). Por isso o teste vale nas formas de projeto único e de vários
projetos. Comentário e string são retirados antes da busca; o teste de SQL tira só o comentário,
porque o que ele procura está dentro da string.

O limite é o do texto: dependência que só aparece no IL (reflexão, tipo herdado de outro assembly)
passa. A violação comum, que é o `using` ou o nome qualificado entre camadas, é barrada. No SQL, a
consulta montada em mais de um comando (`sql += id;`) também passa e fica com o `security` (`SEC-03`).

## O teste

Troque `{ServiceName}` pelo nome do serviço.

```csharp
using System.Text.RegularExpressions;

namespace {ServiceName}.Tests.Architecture;

/// <summary>Guarda a direção das dependências entre camadas, lendo o código-fonte.</summary>
public sealed class LayerDependencyTests
{
    private enum Layer { Domain, Application, Inbound, Outbound, Host, Other }

    private static readonly Regex Noise = new(
        @"@""(?:""""|[^""])*""|""(?:\\.|[^""\\\n])*""|//[^\n]*|/\*.*?\*/",
        RegexOptions.Singleline);

    private static readonly Regex UsingDirective = new(
        @"^\s*(?:global\s+)?using\s+(?:static\s+)?(?:\w+\s*=\s*)?([\w.]+)\s*;",
        RegexOptions.Multiline);

    private static readonly Regex QualifiedName = new(@"\b[A-Za-z_]\w*(?:\.\w+)+");
    private static readonly Regex HandmadeSpan = new(@"new\s+(?:[\w.]+\.)?Activity\s*\(|\.StartActivity\s*\(");
    private static readonly Regex DynamicType = new(@"\bdynamic\b");

    private static readonly Regex Token = new(
        @"(?<comment>//[^\n]*|/\*.*?\*/)|(?<text>\$*"""""".*?""""""|(?:\$@|@\$|@)""(?:""""|[^""])*""|\$?""(?:\\.|[^""\\\n])*""|'(?:\\.|[^'\\\n])+')",
        RegexOptions.Singleline);

    private static readonly Regex SqlText = new(
        @"\bselect\b.+\bfrom\b|\binsert\s+into\b|\bupdate\s+[\w.\[\]]+\s+set\b|\bdelete\s+from\b|\bwhere\s+\w+\s*(?:=|<>|<|>|\blike\b|\bin\b)",
        RegexOptions.IgnoreCase | RegexOptions.Singleline);

    private static readonly Regex Hole = new(@"\{[^{}""]+\}");
    private static readonly Regex Concatenated = new(@"\G\s*\+\s*(?![@$]*"")");
    private static readonly Regex FormatCall = new(@"\bFormat\s*\(\s*$");
    private static readonly Regex ParameterizedCall = new(
        @"\b(?:FromSql|FromSqlInterpolated|ExecuteSql|ExecuteSqlAsync|ExecuteSqlInterpolated|ExecuteSqlInterpolatedAsync|SqlQuery)\s*\(\s*$");

    private static readonly Dictionary<Layer, Layer[]> Forbidden = new()
    {
        [Layer.Domain] = [Layer.Application, Layer.Inbound, Layer.Outbound, Layer.Host],
        [Layer.Application] = [Layer.Inbound, Layer.Outbound, Layer.Host],
        [Layer.Inbound] = [Layer.Outbound, Layer.Host],
        [Layer.Outbound] = [Layer.Inbound, Layer.Host],
    };

    [Fact]
    public void Domain_references_only_System()
    {
        var offenders = Sources()
            .Where(source => source.Layer == Layer.Domain)
            .SelectMany(source => UsingDirective.Matches(source.Code)
                .Select(match => match.Groups[1].Value)
                .Where(name => !IsSystem(name) && NamespaceLayer(name) != Layer.Domain)
                .Select(name => $"{source.Path}: using {name}"))
            .ToList();

        Assert.True(offenders.Count == 0, "Domain referencia só System.*:" + Lines(offenders));
    }

    [Fact]
    public void Layers_depend_inward()
    {
        var offenders = new List<string>();

        foreach (var source in Sources().Where(source => Forbidden.ContainsKey(source.Layer)))
        {
            var names = UsingDirective.Matches(source.Code).Select(match => match.Groups[1].Value)
                .Concat(QualifiedName.Matches(source.Code).Select(match => match.Value));

            offenders.AddRange(names
                .Where(name => Forbidden[source.Layer].Contains(NamespaceLayer(name)))
                .Distinct()
                .Select(name => $"{source.Path} ({source.Layer}) cita {name}"));
        }

        Assert.True(offenders.Count == 0, "Dependência contra a direção Adapters → Application → Domain:"
            + Lines(offenders));
    }

    [Fact]
    public void Spans_come_from_the_pipeline()
    {
        var offenders = Sources()
            .Where(source => !source.Path.Contains("/Application/Pipeline/")
                && !source.Path.Contains("Observability"))
            .Where(source => HandmadeSpan.IsMatch(source.Code))
            .Select(source => source.Path)
            .ToList();

        Assert.True(offenders.Count == 0, "Activity montada à mão; o span vem do pipeline:" + Lines(offenders));
    }

    [Fact]
    public void No_dynamic()
    {
        var offenders = Sources()
            .Where(source => DynamicType.IsMatch(source.Code))
            .Select(source => source.Path)
            .ToList();

        Assert.True(offenders.Count == 0, "dynamic sem tipagem forte:" + Lines(offenders));
    }

    [Fact]
    public void Sql_takes_only_parameters()
    {
        var offenders = new List<string>();

        foreach (var source in Sources())
        {
            foreach (Match token in Token.Matches(source.Raw))
            {
                var text = token.Groups["text"];
                if (!text.Success || !SqlText.IsMatch(text.Value)) continue;

                var before = source.Raw[Math.Max(0, text.Index - 80)..text.Index];
                var interpolated = text.Value.StartsWith('$') && Hole.IsMatch(text.Value)
                    && !ParameterizedCall.IsMatch(before);
                var concatenated = Concatenated.IsMatch(source.Raw, text.Index + text.Length);

                if (interpolated || concatenated || FormatCall.IsMatch(before))
                {
                    offenders.Add($"{source.Path}:{source.Raw[..text.Index].Count(c => c == '\n') + 1}");
                }
            }
        }

        Assert.True(offenders.Count == 0, "SQL montado com texto; passe o valor como parâmetro:" + Lines(offenders));
    }

    private static IEnumerable<(string Path, Layer Layer, string Code, string Raw)> Sources()
    {
        var root = Path.Combine(SolutionRoot(), "src");

        return Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories)
            .Select(file => Path.GetRelativePath(root, file).Replace('\\', '/'))
            .Where(path => !path.Contains("/bin/") && !path.Contains("/obj/")
                && !path.Split('/')[0].EndsWith(".Tests", StringComparison.Ordinal))
            .Select(path => (Path: path, Text: File.ReadAllText(Path.Combine(root, path))))
            .Select(item => (item.Path, FileLayer(item.Path), Noise.Replace(item.Text, " "), item.Text));
    }

    private static Layer FileLayer(string path)
    {
        var segments = path.Split('/');
        var project = segments[0];

        if (project.EndsWith(".Adapters.Inbound", StringComparison.Ordinal)) return Layer.Inbound;
        if (project.EndsWith(".Adapters.Outbound", StringComparison.Ordinal)) return Layer.Outbound;
        if (project.EndsWith(".Application", StringComparison.Ordinal)) return Layer.Application;
        if (project.EndsWith(".Domain", StringComparison.Ordinal)) return Layer.Domain;
        if (project.EndsWith(".Host", StringComparison.Ordinal)) return Layer.Host;

        var folder = segments.Length > 1 ? segments[1] : string.Empty;
        var sub = segments.Length > 2 ? segments[2] : string.Empty;

        return folder switch
        {
            "Domain" => Layer.Domain,
            "Application" => Layer.Application,
            "Adapters" when sub == "Inbound" => Layer.Inbound,
            "Adapters" when sub == "Outbound" => Layer.Outbound,
            "main" => Layer.Host,
            _ => Layer.Other,
        };
    }

    private static Layer NamespaceLayer(string name)
    {
        var parts = name.Split('.');

        for (var index = 1; index < parts.Length; index++)
        {
            if (parts[index] == "Adapters" && index + 1 < parts.Length)
            {
                if (parts[index + 1] == "Inbound") return Layer.Inbound;
                if (parts[index + 1] == "Outbound") return Layer.Outbound;
            }

            if (parts[index] == "Application") return Layer.Application;
            if (parts[index] == "Domain") return Layer.Domain;
        }

        return Layer.Other;
    }

    private static bool IsSystem(string name) => name == "System" || name.StartsWith("System.", StringComparison.Ordinal);

    private static string Lines(IEnumerable<string> items) => Environment.NewLine + string.Join(Environment.NewLine, items);

    private static string SolutionRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);

        while (dir is not null && !dir.EnumerateFiles("*.slnx").Any() && !dir.EnumerateFiles("*.sln").Any())
        {
            dir = dir.Parent;
        }

        return dir?.FullName ?? throw new InvalidOperationException("solution não encontrada acima do binário de teste");
    }
}
```
