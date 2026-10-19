## 🔴 CONFORMIDADE SONARQUBE - LEIA ANTES DE GERAR QUALQUER TESTE

### **Exclusão de projetos de infraestrutura**

Alguma solution tem projeto de infraestrutura sem logica de negócio própria — wrapper de
transporte, adaptador de socket, biblioteca gerada. Cobrir esse código com teste unitário não
mede nada util e derruba o percentual da solution inteira.

Antes de gerar teste, **pergunte ao usuário** se existe algum projeto assim, e qual o padrão de
nome. Se ele indicar um padrão — chamado aqui de `<PADRAO>` — aplique a exclusão nos três lugares
abaixo. Se não houver nenhum, siga sem exclusão; não invente um padrão.

**Identificar os projetos:**
```bash
find . -name "*.csproj" | grep -i "<PADRAO>" || find . -type d -iname "*<PADRAO>*"
```

**Excluir no `sonar-project.properties` (criar na raiz se não existir):**
```properties
sonar.exclusions=**/<PADRAO>*/**
sonar.coverage.exclusions=**/<PADRAO>*/**
sonar.cpd.exclusions=**/<PADRAO>*/**
```

A exclusão equivalente no `.csproj` do projeto de testes está em
`references/test-project-setup.md`.

### **Issues SonarQube a EVITAR nos Testes Gerados**

Os seguintes problemas foram identificados anteriormente e **NUNCA devem aparecer** nos testes que você gerar:

#### ❌ ISSUE 1: CS8625 - Null literal para tipo não-nullable
**Problema:** `Cannot convert null literal to non-nullable reference type`
```csharp
// ❌ ERRADO - causa CS8625
string valor = null;
Activity activity = null;

// ✅ CORRETO - declarar como nullable
string? valor = null;
Activity? activity = null;

// ✅ CORRETO - usar null-forgiving só quando necessário (mockar returns obrigatórios)
_mockService.Setup(x => x.Get()).Returns(null!);  // Usar null! com moderação e justificativa
```

#### ❌ ISSUE 2: CS8618 - Campo não-nullable não inicializado no construtor
**Problema:** `Non-nullable field must contain a non-null value when exiting constructor`
```csharp
// ❌ ERRADO - campo Mock não inicializado
public class MinhaClasseTests
{
    private Mock<IServico> _mockServico;  // CS8618!
    private MinhaClasse _sut;             // CS8618!
}

// ✅ CORRETO - inicializar TODOS os campos no construtor
public class MinhaClasseTests
{
    private readonly Mock<IServico> _mockServico;
    private readonly MinhaClasse _sut;

    public MinhaClasseTests()
    {
        _mockServico = new Mock<IServico>();
        _sut = new MinhaClasse(_mockServico.Object);
    }
}
```

#### ❌ ISSUE 3: xUnit2002 - Assert.NotNull em tipo value type (struct)
**Problema:** `Do not use Assert.NotNull() on value type. Remove this assert.`

**ATENÇÃO CRÍTICA:** `BaseReturn`, `SPAError` e outros tipos de retorno podem ser **structs (value types)**. Value types NUNCA são null, então `Assert.NotNull()` é inválido.

```csharp
// ❌ ERRADO - BaseReturn é struct, nunca será null
var result = _sut.Execute(input);
Assert.NotNull(result);                      // xUnit2002!

// ✅ CORRETO - verificar propriedades do resultado
var result = _sut.Execute(input);
Assert.True(result.IsSuccess);               // OK para struct
Assert.Equal(esperado, result.Value);        // OK para struct

// REGRA: Antes de usar Assert.NotNull(),
// SEMPRE verificar se o tipo é class (reference type) ou struct (value type)
// Se for struct → usar assertions baseadas em propriedades/valores
```

**Como identificar se é value type:**
```bash
# Verificar no código fonte
grep -r "struct BaseReturn\|struct SPAError\|struct.*Return" src/ | head -10
grep -r "class BaseReturn\|class SPAError\|class.*Return" src/ | head -10
```

#### ❌ ISSUE 4: CS0105 - Using directive duplicado
**Problema:** `Using directive appeared previously in this namespace`
```csharp
// ❌ ERRADO - using duplicado
using Domain.Core.Base;
using Domain.Core.Base;  // CS0105!

// ✅ CORRETO - apenas uma vez cada using
using Domain.Core.Base;
```
**REGRA:** Sempre revisar usings antes de finalizar um arquivo de teste. Nunca adicionar duplicados.

#### ❌ ISSUE 5: CS0618 - SqlException obsoleto
**Problema:** `'SqlException' is obsolete: 'Use the Microsoft.Data.SqlClient package instead.'`
```csharp
// ❌ ERRADO - namespace obsoleto
using System.Data.SqlClient;
var ex = new System.Data.SqlClient.SqlException();

// ✅ CORRETO - usar Microsoft.Data.SqlClient
using Microsoft.Data.SqlClient;
// SqlException do Microsoft.Data.SqlClient é o correto
```

#### ❌ ISSUE 6: Possível null reference em parâmetros de mock Returns()
**Problema:** `Possible null reference argument for parameter 'value' in Returns(Activity value)`
```csharp
// ❌ ERRADO - passar null onde não esperado
_mockService.Setup(x => x.GetActivity()).Returns((Activity)null);

// ✅ CORRETO - retornar objeto válido ou usar ReturnsAsync com nullable
Activity? activity = null;
_mockService.Setup(x => x.GetActivity()).Returns(activity!);  // null-forgiving se necessário

// OU melhor ainda, retornar um objeto válido para o happy path
_mockService.Setup(x => x.GetActivity()).Returns(new Activity("operação-teste"));
```

---

### **Checklist de Conformidade SonarQube (validar ANTES de finalizar cada arquivo de teste)**

Antes de salvar qualquer arquivo `.cs` de teste, verificar:

- [ ] Todos os campos não-nullable estão inicializados no construtor?
- [ ] Nenhum `null` literal está sendo atribuído a tipo não-nullable?
- [ ] Os tipos de retorno testados foram verificados (class ou struct)?
- [ ] `Assert.NotNull()` usado APENAS em reference types?
- [ ] Nenhum using directive duplicado?
- [ ] `SqlException` vem de `Microsoft.Data.SqlClient` (não `System.Data.SqlClient`)?
- [ ] Returns de mocks com null usam `null!` apenas quando inevitável?

---


### **Passo 3.4: Regras Obrigatórias de Conformidade SonarQube**

**TODAS as seguintes regras devem ser seguidas em CADA arquivo de teste gerado:**

#### Regra 1 - Nullable Reference Types (CS8625, CS8618)

```csharp
// PADRÃO OBRIGATÓRIO para campos de teste:
public class ExemploTests
{
    // ✅ SEMPRE inicializar no construtor (não deixar como null implícito)
    private readonly Mock<IServico> _mockServico;
    private readonly ExemploClasse _sut;

    public ExemploTests()
    {
        // Inicializar TUDO aqui
        _mockServico = new Mock<IServico>();
        _sut = new ExemploClasse(_mockServico.Object);
    }

    [Fact]
    public async Task Metodo_Cenario_Resultado()
    {
        // Arrange - nunca atribuir null a tipos não-nullable
        string? valorNulo = null;           // ✅ nullable quando null for possível
        var dadosValidos = "valor válido";  // ✅ inicializado

        // Se precisar testar com null, usar tipo nullable:
        await Assert.ThrowsAsync<ArgumentNullException>(
            () => _sut.Metodo(null!)  // null! apenas em parâmetros de método, não em campos
        );
    }
}
```

#### Regra 2 - Value Types vs Reference Types (xUnit2002)

```csharp
// ANTES DE ESCREVER ASSERTIONS, identificar o tipo de retorno:
// grep -r "struct BaseReturn\|class BaseReturn" src/

// SE BaseReturn for STRUCT (value type):
[Fact]
public void Execute_ComDadosValidos_DeveRetornarSucesso()
{
    var result = _sut.Execute(input);

    // ✅ CORRETO para value types (structs)
    Assert.True(result.IsSuccess);
    Assert.Equal(valorEsperado, result.Value);
    Assert.True(string.IsNullOrEmpty(result.Error));

    // ❌ NUNCA para value types:
    // Assert.NotNull(result);           <- xUnit2002
}

// SE BaseReturn for CLASS (reference type):
[Fact]
public void Execute_ComDadosValidos_DeveRetornarSucesso()
{
    var result = _sut.Execute(input);

    // ✅ Para reference types, Assert.NotNull() é válido
    Assert.NotNull(result);
    Assert.True(result!.IsSuccess);
}
```

#### Regra 3 - Using Directives sem Duplicatas (CS0105)

```csharp
// PADRÃO de agrupamento de usings (sem duplicatas):
// Grupo 1: System
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

// Grupo 2: Microsoft
using Microsoft.Data.SqlClient;           // ✅ CORRETO (não System.Data.SqlClient)
using Microsoft.Extensions.Logging;

// Grupo 3: Terceiros (xUnit, Moq, Bogus)
using Moq;
using Xunit;

// Grupo 4: Projeto principal
using [SolutionName].Domain;
using [SolutionName].Application;

// Grupo 5: Projeto de testes
using [SolutionName].Tests.Shared.Builders;

// REGRA: cada namespace apenas UMA VEZ. Revisar antes de salvar.
```

#### Regra 4 - SqlException com namespace correto (CS0618)

```csharp
// ✅ CORRETO - Microsoft.Data.SqlClient
using Microsoft.Data.SqlClient;

// Para criar SqlException em testes (via reflection, pois é sealed):
private static SqlException CreateSqlException(int errorNumber = 547)
{
    // SqlException não tem construtor público, usar método helper
    var sqlErrors = (SqlErrorCollection)Activator.CreateInstance(
        typeof(SqlErrorCollection), true)!;
    var exception = (SqlException)Activator.CreateInstance(
        typeof(SqlException),
        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
        null,
        new object[] { "Test SQL Exception", sqlErrors, null!, Guid.NewGuid() },
        null)!;
    return exception;
}

// ❌ NUNCA usar:
// using System.Data.SqlClient;  <- CS0618 obsoleto
```

#### Regra 5 - Mock Returns com tipos nullable (CS8604 / null reference)

```csharp
// ✅ CORRETO - usar objeto real ou nullable explícito
_mockService
    .Setup(x => x.BuscarActivity(It.IsAny<string>()))
    .ReturnsAsync(new Activity("operação-teste"));   // Objeto válido - preferível

// Se precisar retornar null (apenas para reference types):
Activity? activityNula = null;
_mockService
    .Setup(x => x.BuscarActivity(It.IsAny<string>()))
    .ReturnsAsync(activityNula);   // ✅ usar variável nullable tipada

// ❌ NUNCA:
// .Returns(null)     <- CS8625 para non-nullable
// .Returns((Activity)null)  <- possível null reference warning
```

---

