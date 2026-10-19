## 📋 FASE 2: CRIAR OU MELHORAR PROJETO ÚNICO DE TESTES

### **Passo 2.1: Decisão - Criar Novo ou Melhorar Existente**

**IMPORTANTE:** O projeto de testes DEVE ser criado DENTRO da pasta `src/` junto com os outros projetos da solution.

**SE não existe projeto de testes COM xUnit:**

```bash
# CRIAR projeto de testes DENTRO de src/ (NUNCA em tests/)
dotnet new xunit -n [SolutionName].Tests -o src/[SolutionName].Tests

# Adicionar projeto à solution
dotnet sln add src/[SolutionName].Tests/[SolutionName].Tests.csproj

# Adicionar referências a TODOS os projetos principais que estão em src/
cd src/[SolutionName].Tests
dotnet add reference ../[ProjectName1]/[ProjectName1].csproj
dotnet add reference ../[ProjectName2]/[ProjectName2].csproj
# ... adicionar todos os projetos em src/ que serão testados
cd ../..

# Verificar estrutura criada
ls -la src/
# Deve mostrar: [ProjectName1]/, [ProjectName2]/, [SolutionName].Tests/
```

**SE existem MÚLTIPLOS projetos de teste:**

```markdown
⚠️ **ATENÇÃO:** Existem múltiplos projetos de teste separados.

Ação recomendada:
1. Criar NOVO projeto consolidado [SolutionName].Tests DENTRO de src/
2. Migrar testes existentes para estrutura unificada
3. Organizar em pastas Unit/ e Integration/
4. Remover projetos antigos após migração

Deseja prosseguir com a consolidação? [aguardar confirmação]
```

**SE projeto de testes existe FORA de src/ (ex: pasta tests/ separada):**

```bash
# VERIFICAR se existe pasta tests/ separada
if [ -d "tests/" ]; then
    echo "⚠️ ATENÇÃO: Encontrada pasta tests/ separada!"
    echo "O projeto de testes DEVE estar em src/ junto com os outros projetos."
    echo ""
    echo "Ações necessárias:"
    echo "1. Mover conteúdo de tests/[ProjectName].Tests/ para src/[SolutionName].Tests/"
    echo "2. Atualizar a solution (.slnx no .NET 10; .sln em legado) para apontar para src/[SolutionName].Tests/"
    echo "3. Atualizar referências entre projetos (usar ../ em vez de ../../)"
    echo "4. Remover pasta tests/ vazia após migração"
    echo ""
    
    # MOVER projeto existente
    mv tests/[ProjectName].Tests src/[SolutionName].Tests
    
    # ATUALIZAR referências na solution
    dotnet sln remove tests/[ProjectName].Tests/[ProjectName].Tests.csproj
    dotnet sln add src/[SolutionName].Tests/[SolutionName].Tests.csproj
    
    # ATUALIZAR referências entre projetos (de ../../src/ para ../)
    cd src/[SolutionName].Tests
    # Remover referências antigas
    dotnet remove reference ../../src/[ProjectName1]/[ProjectName1].csproj
    # Adicionar referências corretas
    dotnet add reference ../[ProjectName1]/[ProjectName1].csproj
    dotnet add reference ../[ProjectName2]/[ProjectName2].csproj
    cd ../..
    
    # REMOVER pasta tests/ vazia
    rmdir tests/
    
    echo "✅ Projeto movido de tests/ para src/"
fi
```

**SE existe mas NÃO é xUnit:**

```markdown
⚠️ **ATENÇÃO:** Projeto de testes usa [NUnit/MSTest].

Opções:
1. Migrar para xUnit (recomendado)
2. Continuar com framework existente

Decisão: [aguardar input do usuário]
```

### **Passo 2.2: Criar Estrutura Interna Organizada**

Criar estrutura de pastas DENTRO do projeto único em src/:

```bash
cd src/[SolutionName].Tests

# Criar estrutura organizada internamente
mkdir -p Unit
mkdir -p Integration
mkdir -p Shared

# Estrutura Unit - espelha o projeto principal
mkdir -p Unit/Domain/Core/Entities
mkdir -p Unit/Domain/Core/ValueObjects
mkdir -p Unit/Domain/Core/Aggregates
mkdir -p Unit/Application/UseCases
mkdir -p Unit/Application/Services
mkdir -p Unit/Adapters/Outbound

# Estrutura Integration
mkdir -p Integration/API
mkdir -p Integration/Database
mkdir -p Integration/ExternalServices

# Shared - recursos compartilhados
mkdir -p Shared/Builders
mkdir -p Shared/Fixtures
mkdir -p Shared/Helpers
mkdir -p Shared/Mocks

cd ../..
```

**Estrutura final do projeto:**

```
src/
├── [ProjectName1]/
├── [ProjectName2]/
└── [SolutionName].Tests/          ← PROJETO DE TESTES AQUI
    ├── Unit/                       # TESTES UNITÁRIOS
    │   ├── Domain/
    │   │   ├── Core/
    │   │   │   ├── Entities/
    │   │   │   ├── ValueObjects/
    │   │   │   └── Aggregates/
    │   │   └── Exceptions/
    │   ├── Application/
    │   │   ├── UseCases/
    │   │   ├── Services/
    │   │   └── Validators/
    │   └── Adapters/
    │       ├── Inbound/
    │       └── Outbound/
    │
    ├── Integration/                # TESTES DE INTEGRAÇÃO
    │   ├── API/
    │   │   ├── Controllers/
    │   │   └── Endpoints/
    │   ├── Database/
    │   │   ├── Repositories/
    │   │   └── Migrations/
    │   └── ExternalServices/
    │       ├── Cache/
    │       └── MessageBus/
    │
    └── Shared/                     # RECURSOS COMPARTILHADOS
        ├── Builders/               # Test Data Builders
        ├── Fixtures/               # xUnit Fixtures
        ├── Helpers/                # Test Helpers
        └── Mocks/                  # Mock Factories
```

### **Passo 2.3: Instalar Pacotes Essenciais**

Para o projeto de teste ÚNICO em src/, garantir que tenha:

```bash
cd src/[SolutionName].Tests

# Pacotes base xUnit
dotnet add package xunit --version 2.6.6
dotnet add package xunit.runner.visualstudio --version 2.5.6
dotnet add package Microsoft.NET.Test.Sdk --version 17.8.0

# Cobertura de código
dotnet add package coverlet.collector --version 6.0.0
dotnet add package coverlet.msbuild --version 6.0.0

# Mocking (assertions: Assert nativo do xUnit - NUNCA FluentAssertions)
dotnet add package Moq --version 4.20.70

# Geração de dados fake
dotnet add package Bogus --version 35.4.0

# Para testes de integração
dotnet add package Microsoft.AspNetCore.Mvc.Testing --version 8.0.0
dotnet add package Microsoft.EntityFrameworkCore.InMemory --version 8.0.0

# Voltar ao root
cd ../..
```

### **Passo 2.4: Configurar Coverage no .csproj**

Adicionar ao arquivo `src/[SolutionName].Tests/[SolutionName].Tests.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    
    <!-- Configurações de Cobertura -->
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>cobertura,json,lcov,opencover</CoverletOutputFormat>
    <CoverletOutput>./TestResults/</CoverletOutput>
    <!-- Excluir o próprio projeto de testes e, se houver, os projetos de infraestrutura (<PADRAO>) -->
    <Exclude>[*.Tests]*,[*<PADRAO>*]*</Exclude>
    <ExcludeByAttribute>Obsolete,GeneratedCode,CompilerGenerated,ExcludeFromCodeCoverage</ExcludeByAttribute>
    <ExcludeByFile>**/*.Designer.cs,**/*.g.cs,**/*.g.i.cs,**/<PADRAO>*/**</ExcludeByFile>

    <!-- Thresholds de Cobertura - 90% -->
    <Threshold>90</Threshold>
    <ThresholdType>line,branch,method</ThresholdType>
    <ThresholdStat>total</ThresholdStat>
  </PropertyGroup>

  <!-- Resto do arquivo... -->
</Project>
```

### **Passo 2.5: Criar Arquivo de Configuração de Testes**

**Criar arquivo:** `src/[SolutionName].Tests/xunit.runner.json`

```json
{
  "$schema": "https://xunit.net/schema/current/xunit.runner.schema.json",
  "methodDisplay": "method",
  "methodDisplayOptions": "all",
  "parallelizeAssembly": true,
  "parallelizeTestCollections": true,
  "maxParallelThreads": 4,
  "diagnosticMessages": false,
  "internalDiagnosticMessages": false
}
```

---

