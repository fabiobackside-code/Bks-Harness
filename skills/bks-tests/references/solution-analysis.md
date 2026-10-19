## 📋 FASE 1: ANÁLISE COMPLETA DA SOLUTION

### **Passo 1.1: Mapear Estrutura da Solution**

Execute os seguintes comandos para entender a estrutura:

```bash
# Listar todos os projetos da solution
dotnet sln list

# Mostrar estrutura de diretórios
find . -name "*.csproj" -o -name "*.slnx" -o -name "*.sln" | head -20

# Identificar projetos principais
echo "📁 Estrutura de src/:"
ls -la src/ 2>/dev/null || ls -la

# VERIFICAR se projeto de testes está em localização ERRADA
echo ""
echo "🔍 Verificando localização de projetos de teste..."

# Verificar pasta tests/ separada (ERRADO)
if [ -d "tests/" ]; then
    echo "⚠️ ATENÇÃO: Encontrada pasta tests/ - Projetos devem estar em src/!"
    ls -la tests/
fi

# Verificar pasta test/ separada (ERRADO)
if [ -d "test/" ]; then
    echo "⚠️ ATENÇÃO: Encontrada pasta test/ - Projetos devem estar em src/!"
    ls -la test/
fi

# Verificar se já existe projeto de testes em src/ (CORRETO)
echo ""
echo "✅ Verificando src/ (localização correta):"
find src/ -name "*Tests*.csproj" -o -name "*Test.csproj" 2>/dev/null || echo "Nenhum projeto de testes encontrado em src/"

echo ""
echo "📋 REGRA: Projeto de testes DEVE estar em src/[SolutionName].Tests/"
```

### **Passo 1.1b: Marcar projetos de infraestrutura para exclusão**

Pergunte ao usuário se a solution tem projeto de infraestrutura sem logica de negócio própria
(wrapper de transporte, adaptador de socket, biblioteca gerada) que deva ficar fora da cobertura
e da analise. Se houver, ele informa o padrão de nome — referido aqui como `<PADRAO>`.

Com o padrão em maos:

```bash
echo "Buscando projetos de infraestrutura para exclusão..."
INFRA_PROJECTS=$(find . -name "*.csproj" | grep -i "<PADRAO>")
INFRA_DIRS=$(find . -type d -iname "*<PADRAO>*")

if [ -n "$INFRA_PROJECTS" ] || [ -n "$INFRA_DIRS" ]; then
    echo "Projetos encontrados - serao EXCLUIDOS do SonarQube:"
    echo "$INFRA_PROJECTS"
    echo "$INFRA_DIRS"

    if [ ! -f sonar-project.properties ]; then
        cat > sonar-project.properties <<'EOF'
sonar.exclusions=**/<PADRAO>*/**
sonar.coverage.exclusions=**/<PADRAO>*/**
sonar.cpd.exclusions=**/<PADRAO>*/**
EOF
        echo "sonar-project.properties criado com as exclusões"
    else
        echo "sonar-project.properties já existe - conferir se as exclusões estão presentes:"
        grep -i "exclusions" sonar-project.properties || echo "Adicionar as exclusões manualmente"
    fi
else
    echo "Nenhum projeto de infraestrutura a excluir"
fi
```

Sem padrão informado, pule este passo — não aplique exclusão por conta própria.

### **Passo 1.2: Analisar Projetos Principais**

Para cada projeto principal identificado, analise:

**Crie um arquivo:** `ANALISE_PROJECTS.md`

```markdown
# Análise de Projetos - [Nome da Solution]

## Estrutura Identificada

```
src/
├── [ProjectName1]/          ← Projeto principal 1
├── [ProjectName2]/          ← Projeto principal 2
└── [SolutionName].Tests/    ← Projeto de testes (se existe)
```

## Projetos Principais (src/)

### Projeto 1: [Nome]
- **Path:** src/[ProjectName]/
- **Framework:** [.NET version]
- **Tipo:** [ClassLibrary/Web/Console]
- **Arquitetura:** [Hexagonal/Limpa/MVC/etc]
- **Dependências principais:**
  - [listar principais NuGet packages]
- **Camadas identificadas:**
  - [ ] Domain/Core
  - [ ] Application
  - [ ] Infrastructure/Adapters
  - [ ] API/Controllers
- **Número de classes:** [X]
- **Número de métodos públicos:** [Y]
- **Complexidade estimada:** [Baixa/Média/Alta]

### Projeto 2: [Nome]
[repetir estrutura acima]

## Projetos de Teste Existentes

### Projeto Teste: [Nome]
- **Path:** src/[SolutionName].Tests/ (ou outra localização)
- **Framework de Teste:** [xUnit/NUnit/MSTest]
- **Estrutura:** [Único projeto / Múltiplos projetos]
- **Organização Interna:**
  - [ ] Testes separados em pastas (Unit/ e Integration/)
  - [ ] Testes misturados
- **Coverage atual:** [X%] (se disponível)
- **Número de testes:** [N]
  - Unitários: [X]
  - Integração: [Y]
- **Packages instalados:**
  - [ ] xunit
  - [ ] xunit.runner.visualstudio
  - [ ] coverlet.collector
  - [ ] Moq
  - [ ] Bogus
  - [ ] Microsoft.NET.Test.Sdk
  - [ ] WebApplicationFactory (para testes de integração)
- **Problemas identificados:**
  - [listar issues]

## Gaps Identificados

### Projetos SEM Testes
1. [Nome do projeto] - Prioridade: ALTA/MÉDIA/BAIXA
2. [Nome do projeto] - Prioridade: ALTA/MÉDIA/BAIXA

### Áreas com Baixa Cobertura
1. [Área/Namespace] - Cobertura atual: X%
2. [Área/Namespace] - Cobertura atual: X%

### Testes Faltantes
- [ ] Testes de Controller/API Endpoints
- [ ] Testes de Services
- [ ] Testes de Repositories
- [ ] Testes de Validators
- [ ] Testes de Mappers/Extensions
- [ ] Testes de Domain Entities/Value Objects
- [ ] Testes de Integration
- [ ] Testes de Edge Cases

## Recomendações Iniciais

1. [Recomendação prioritária]
2. [Recomendação secundária]
3. [...]
```

### **Passo 1.3: Analisar Código para Entender Dependências**

Identifique padrões usados no projeto:

```bash
# Buscar por injeção de dependência
grep -r "IServiceCollection" src/ | head -10

# Buscar por Entity Framework
grep -r "DbContext" src/ | head -10

# Buscar por padrões de repositório
grep -r "Repository" src/ | head -10

# Buscar por validators
grep -r "FluentValidation\|IValidator" src/ | head -10

# Buscar por APIs/Controllers
find src/ -name "*Controller.cs" -o -name "*Api.cs" | head -10
```

---

