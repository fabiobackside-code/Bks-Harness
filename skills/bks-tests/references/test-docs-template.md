## 📋 FASE 6: DOCUMENTAÇÃO

**Criar arquivo:** `README_TESTES.md`

```markdown
# 📊 Guia de Testes - [SolutionName]

## 📁 Estrutura do Projeto

```
src/
├── [ProjectName1]/              ← Código de produção
├── [ProjectName2]/              ← Código de produção
└── [SolutionName].Tests/        ← PROJETO DE TESTES
    ├── Unit/                    ← Testes unitários
    ├── Integration/             ← Testes de integração
    └── Shared/                  ← Recursos compartilhados
```

## 🎯 Meta de Cobertura

- **Threshold:** 90% em linhas, branches e métodos
- **Domain/Core:** 98%+
- **Application:** 95%+
- **Infrastructure:** 90%+
- **API:** 90%+

## 🚀 Como Executar os Testes

### Todos os Testes
```bash
./run-tests-with-coverage.sh
# ou
./run-tests-with-coverage.sh all
```

### Apenas Testes Unitários
```bash
./run-tests-with-coverage.sh unit
```

### Apenas Testes de Integração
```bash
./run-tests-with-coverage.sh integration
```

### Via dotnet
```bash
# Todos
cd src/[SolutionName].Tests
dotnet test

# Unitários
dotnet test --filter "FullyQualifiedName~.Unit."

# Integração
dotnet test --filter "FullyQualifiedName~.Integration."
```

## 📊 Visualizar Relatório de Cobertura

Após executar os testes:

```bash
# Abrir relatório HTML
open TestResults/CoverageReport/index.html

# Ou no Linux/WSL
xdg-open TestResults/CoverageReport/index.html
```

## 🏗️ Organização dos Testes

### Unit/ (Testes Unitários)
- Testes isolados
- Sem dependências externas
- Rápidos (< 100ms cada)
- Usa mocks para dependências

### Integration/ (Testes de Integração)
- Testa fluxos completos
- Pode usar banco InMemory
- Usa WebApplicationFactory
- Mais lentos (< 5s cada)

### Shared/ (Recursos Compartilhados)
- **Builders/**: Criação de dados de teste (Bogus)
- **Fixtures/**: Configurações xUnit
- **Helpers/**: Métodos auxiliares
- **Mocks/**: Factories de mocks

## 📝 Padrões de Teste

### Nomenclatura
```
[MetodoTestado]_[Cenário]_[ResultadoEsperado]
```

Exemplo:
```csharp
CalcularDesconto_ComValorNegativo_DeveLancarException
```

### Estrutura (AAA Pattern)
```csharp
[Fact]
public async Task Exemplo()
{
    // Arrange - Preparar
    var input = Builder.CreateValid();
    
    // Act - Executar
    var result = await _sut.Metodo(input);
    
    // Assert - Verificar
    Assert.True(result);
}
```

## 🔧 Adicionar Novos Testes

### 1. Para Testes Unitários
```bash
# Criar em src/[SolutionName].Tests/Unit/[Camada]/
touch src/[SolutionName].Tests/Unit/Domain/MinhaClasseTests.cs
```

### 2. Para Testes de Integração
```bash
# Criar em src/[SolutionName].Tests/Integration/
touch src/[SolutionName].Tests/Integration/API/MeuEndpointTests.cs
```

### 3. Usar Builders do Shared/
```csharp
using [SolutionName].Tests.Shared.Builders;

var entidade = MinhaEntidadeBuilder.CreateValid();
```

## 🐛 Troubleshooting

### Testes não encontrados
```bash
# Limpar e rebuild
dotnet clean
dotnet build
dotnet test
```

### Coverage não atinge 90%
```bash
# Ver gaps de cobertura
cat TestResults/CoverageReport/Summary.txt

# Consultar relatório detalhado
open TestResults/CoverageReport/index.html
```

### Testes de integração falhando
- Verificar se InMemoryDatabase está limpo
- Verificar seed de dados
- Verificar configurações no CustomWebApplicationFactory

## 📚 Recursos

- [Documentação xUnit](https://xunit.net/)
- [Moq](https://github.com/moq/moq)
- [Bogus](https://github.com/bchavez/Bogus)

---

**Localização do Projeto de Testes:** `src/[SolutionName].Tests/`  
**Threshold de Cobertura:** 90%
```

---

