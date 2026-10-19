## 📋 FASE 4: EXECUTAR TESTES E GERAR RELATÓRIO DE COBERTURA

### **Passo 4.1: Executar Testes com Cobertura**

```bash
# Navegar para pasta de testes em src/
cd src/[SolutionName].Tests

# Executar TODOS os testes (Unit + Integration) com cobertura
dotnet test \
  /p:CollectCoverage=true \
  /p:CoverletOutputFormat=cobertura \
  /p:CoverletOutput=./TestResults/coverage.cobertura.xml \
  /p:Threshold=90 \
  /p:ThresholdType=line,branch,method

# Se threshold não for atingido, build falhará
```

**Executar apenas testes unitários:**
```bash
dotnet test --filter "FullyQualifiedName~.Unit." \
  /p:CollectCoverage=true
```

**Executar apenas testes de integração:**
```bash
dotnet test --filter "FullyQualifiedName~.Integration." \
  /p:CollectCoverage=true
```

### **Passo 4.2: Gerar Relatório HTML**

```bash
# Instalar ReportGenerator (se ainda não tiver)
dotnet tool install -g dotnet-reportgenerator-globaltool

# Gerar relatório HTML
reportgenerator \
  -reports:"./TestResults/coverage.cobertura.xml" \
  -targetdir:"./TestResults/CoverageReport" \
  -reporttypes:"Html;HtmlSummary;Badges;TextSummary;JsonSummary" \
  -verbosity:"Info" \
  -title:"Test Coverage Report - 90% Target"

# Mostrar caminho do relatório
echo "📊 Relatório de Cobertura gerado em:"
echo "$(pwd)/TestResults/CoverageReport/index.html"
```

### **Passo 4.3: Analisar Resultados**

```bash
# Exibir resumo da cobertura no console
cat ./TestResults/CoverageReport/Summary.txt

# Ou extrair métricas do JSON
if command -v jq &> /dev/null; then
    echo "Cobertura de Linhas: $(jq -r '.summary.linecoverage' ./TestResults/CoverageReport/Summary.json)%"
    echo "Cobertura de Branches: $(jq -r '.summary.branchcoverage' ./TestResults/CoverageReport/Summary.json)%"
    echo "Cobertura de Métodos: $(jq -r '.summary.methodcoverage' ./TestResults/CoverageReport/Summary.json)%"
fi
```

### **Passo 4.4: Identificar Gaps de Cobertura**

**Criar arquivo:** `GAPS_COBERTURA.md`

```markdown
# Gaps de Cobertura Identificados

## Resumo Executivo

- **Cobertura Total de Linhas:** X%
- **Cobertura Total de Branches:** Y%
- **Cobertura Total de Métodos:** Z%
- **Meta:** 90% em todos os indicadores
- **Status:** ✅ ATINGIDO / ❌ NÃO ATINGIDO

## Localização do Projeto de Testes

**Path:** `src/[SolutionName].Tests/`

## Distribuição de Testes

### Testes Unitários (Unit/)
- **Total:** [N] testes
- **Localização:** src/[SolutionName].Tests/Unit/
- **Cobertura Média:** [X]%
- **Tempo de Execução:** [T]s

### Testes de Integração (Integration/)
- **Total:** [M] testes
- **Localização:** src/[SolutionName].Tests/Integration/
- **Cobertura Média:** [Y]%
- **Tempo de Execução:** [T]s

## Classes/Métodos com Baixa Cobertura

### Crítico (<80%)

| Classe | Método | Cobertura Atual | Branches não cobertos | Localização Teste | Ação Necessária |
|--------|--------|-----------------|----------------------|-------------------|-----------------|
| [ClassName] | [MethodName] | 65% | 3/7 | src/.../Unit/[Path] | Adicionar testes para casos X, Y, Z |
| ... | ... | ... | ... | ... | ... |

### Médio (80-89%)

| Classe | Método | Cobertura Atual | Branches não cobertos | Localização Teste | Ação Necessária |
|--------|--------|-----------------|----------------------|-------------------|-----------------|
| [ClassName] | [MethodName] | 85% | 1/5 | src/.../Unit/[Path] | Adicionar teste para edge case |
| ... | ... | ... | ... | ... | ... |

## Arquivos Completamente Sem Cobertura

1. `[Path/To/File.cs]` - Motivo: [Novo arquivo / Não testável / etc]
2. ...

## Plano de Ação

### Prioridade 1 - Crítico
- [ ] Adicionar testes em `src/[SolutionName].Tests/Unit/[Path]/[ClassName]Tests.cs`
- [ ] Cobrir branches não testados em [ClassName]

### Prioridade 2 - Importante
- [ ] Melhorar cobertura de [ClassName] de 85% para 90%+
- [ ] Adicionar testes de integração em `src/[SolutionName].Tests/Integration/[Path]/`

### Prioridade 3 - Nice to Have
- [ ] Refatorar testes de [ClassName] para melhor legibilidade
- [ ] Consolidar builders comuns em `src/[SolutionName].Tests/Shared/Builders/`
```

---

## 📋 FASE 5: CRIAR SCRIPTS DE AUTOMAÇÃO

### **Passo 5.1: Script de Execução Completa**

**Criar arquivo:** `run-tests-with-coverage.sh` **(na raiz do projeto)**

```bash
#!/bin/bash

# Script: Executar todos os testes com cobertura e gerar relatório
# Projeto: ÚNICO projeto consolidado em src/ com Unit/ e Integration/
# Threshold: 90%
# Uso: ./run-tests-with-coverage.sh [unit|integration|all]

set -e  # Parar em caso de erro

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
THRESHOLD=90
TEST_PROJECT="src/*.Tests/*.csproj"
MODE=${1:-all}  # all, unit, integration

echo -e "${BLUE}🧪 Iniciando execução de testes com análise de cobertura...${NC}"
echo -e "${BLUE}📊 Meta de cobertura: ${THRESHOLD}%${NC}"
echo -e "${BLUE}🎯 Modo: ${MODE}${NC}"
echo -e "${BLUE}📁 Projeto de testes: src/[SolutionName].Tests/${NC}"
echo ""

# Limpar resultados anteriores
echo "🧹 Limpando resultados anteriores..."
find ./src -type d -name "TestResults" -exec rm -rf {} + 2>/dev/null || true
echo ""

# Função para executar testes
run_tests() {
    local filter=$1
    local description=$2
    
    echo -e "${YELLOW}${description}${NC}"
    
    if [ "$filter" == "all" ]; then
        dotnet test $TEST_PROJECT \
          --configuration Release \
          --logger "console;verbosity=normal" \
          /p:CollectCoverage=true \
          /p:CoverletOutputFormat=cobertura \
          /p:CoverletOutput=./TestResults/coverage.cobertura.xml \
          /p:Exclude="[*.Tests]*" \
          || { echo -e "${RED}❌ Testes falharam${NC}"; exit 1; }
    else
        dotnet test $TEST_PROJECT \
          --configuration Release \
          --filter "FullyQualifiedName~.${filter}." \
          --logger "console;verbosity=normal" \
          /p:CollectCoverage=true \
          /p:CoverletOutputFormat=cobertura \
          /p:CoverletOutput=./TestResults/coverage.${filter}.cobertura.xml \
          /p:Exclude="[*.Tests]*" \
          || { echo -e "${RED}❌ Testes ${filter} falharam${NC}"; exit 1; }
    fi
    
    echo -e "${GREEN}✅ ${description} concluídos${NC}"
    echo ""
}

# Executar testes conforme modo selecionado
case $MODE in
    unit)
        run_tests "Unit" "📝 Executando APENAS testes unitários (Unit/)..."
        COVERAGE_FILES="./src/*/TestResults/coverage.Unit.cobertura.xml"
        ;;
    integration)
        run_tests "Integration" "🔗 Executando APENAS testes de integração (Integration/)..."
        COVERAGE_FILES="./src/*/TestResults/coverage.Integration.cobertura.xml"
        ;;
    all)
        run_tests "all" "🎯 Executando TODOS os testes (Unit/ + Integration/)..."
        COVERAGE_FILES="./src/*/TestResults/coverage.cobertura.xml"
        ;;
    *)
        echo -e "${RED}❌ Modo inválido: ${MODE}${NC}"
        echo "Uso: $0 [unit|integration|all]"
        exit 1
        ;;
esac

# Gerar relatório HTML
echo -e "${BLUE}📊 Gerando relatório consolidado de cobertura...${NC}"

reportgenerator \
  -reports:"${COVERAGE_FILES}" \
  -targetdir:"./TestResults/CoverageReport" \
  -reporttypes:"Html;HtmlSummary;Badges;JsonSummary;TextSummary" \
  -verbosity:"Info" \
  -title:"Test Coverage Report - Target: ${THRESHOLD}% - Mode: ${MODE}" \
  || { echo -e "${RED}❌ Falha ao gerar relatório${NC}"; exit 1; }

echo -e "${GREEN}✅ Relatório gerado com sucesso${NC}"
echo ""

# Exibir resumo
echo "═══════════════════════════════════════"
echo -e "${BLUE}📊 RESUMO DE COBERTURA${NC}"
echo "═══════════════════════════════════════"
cat ./TestResults/CoverageReport/Summary.txt
echo "═══════════════════════════════════════"
echo ""

# Extrair percentuais do summary.json
if command -v jq &> /dev/null; then
    LINE_COVERAGE=$(jq -r '.summary.linecoverage' ./TestResults/CoverageReport/Summary.json 2>/dev/null || echo "N/A")
    BRANCH_COVERAGE=$(jq -r '.summary.branchcoverage' ./TestResults/CoverageReport/Summary.json 2>/dev/null || echo "N/A")
    METHOD_COVERAGE=$(jq -r '.summary.methodcoverage' ./TestResults/CoverageReport/Summary.json 2>/dev/null || echo "N/A")

    echo -e "${BLUE}📈 Métricas de Cobertura:${NC}"
    echo "   Linhas:   ${LINE_COVERAGE}%"
    echo "   Branches: ${BRANCH_COVERAGE}%"
    echo "   Métodos:  ${METHOD_COVERAGE}%"
    echo ""

    # Verificar se atingiu threshold
    check_threshold() {
        local coverage=$1
        local name=$2
        
        # Remover % e converter para número
        coverage_num=$(echo $coverage | sed 's/%//')
        
        if (( $(echo "$coverage_num >= $THRESHOLD" | bc -l) )); then
            echo -e "${GREEN}✅ $name: $coverage >= ${THRESHOLD}%${NC}"
            return 0
        else
            echo -e "${RED}❌ $name: $coverage < ${THRESHOLD}%${NC}"
            return 1
        fi
    }

    THRESHOLD_PASS=true

    check_threshold "$LINE_COVERAGE" "Cobertura de Linhas" || THRESHOLD_PASS=false
    check_threshold "$BRANCH_COVERAGE" "Cobertura de Branches" || THRESHOLD_PASS=false
    check_threshold "$METHOD_COVERAGE" "Cobertura de Métodos" || THRESHOLD_PASS=false

    echo ""
else
    echo -e "${YELLOW}⚠️  jq não instalado. Instale para visualizar métricas detalhadas.${NC}"
    THRESHOLD_PASS=true  # Assumir passou se não conseguir verificar
fi

# Informações do projeto
echo -e "${BLUE}📁 Estrutura do Projeto de Testes:${NC}"
echo "   Projeto: src/[SolutionName].Tests/"
echo "   Unit Tests: src/[SolutionName].Tests/Unit/"
echo "   Integration Tests: src/[SolutionName].Tests/Integration/"
echo "   Shared: src/[SolutionName].Tests/Shared/"
echo ""

echo -e "${BLUE}📁 Relatório HTML disponível em:${NC}"
echo "   file://$(pwd)/TestResults/CoverageReport/index.html"
echo ""

if [ "$THRESHOLD_PASS" = false ]; then
    echo -e "${RED}⚠️  ATENÇÃO: Cobertura abaixo do threshold de ${THRESHOLD}%${NC}"
    echo "Consulte ./TestResults/CoverageReport/index.html para detalhes"
    echo "Revise GAPS_COBERTURA.md para plano de ação"
    exit 1
else
    echo -e "${GREEN}🎉 Parabéns! Cobertura acima de ${THRESHOLD}% em todos os indicadores${NC}"
fi
```

Tornar executável:
```bash
chmod +x run-tests-with-coverage.sh
```

**Exemplos de uso:**
```bash
# Executar todos os testes
./run-tests-with-coverage.sh

# Executar apenas testes unitários
./run-tests-with-coverage.sh unit

# Executar apenas testes de integração
./run-tests-with-coverage.sh integration
```

### **Passo 5.2: Integração com CI/CD**

**Criar arquivo:** `.github/workflows/test-coverage.yml`

```yaml
name: Test Coverage - 90% Target

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-coverage:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: '8.0.x'
    
    - name: Restore dependencies
      run: dotnet restore
    
    - name: Build
      run: dotnet build --no-restore --configuration Release
    
    - name: Run ALL Tests with Coverage (Unit + Integration)
      run: |
        dotnet test ./src/*.Tests/*.csproj \
          --no-build \
          --configuration Release \
          --logger "trx;LogFileName=test-results.trx" \
          /p:CollectCoverage=true \
          /p:CoverletOutputFormat=cobertura \
          /p:CoverletOutput=./TestResults/ \
          /p:Threshold=90 \
          /p:ThresholdType=line,branch,method \
          /p:ThresholdStat=total
    
    - name: Run Unit Tests Only (for metrics)
      continue-on-error: true
      run: |
        dotnet test ./src/*.Tests/*.csproj \
          --no-build \
          --configuration Release \
          --filter "FullyQualifiedName~.Unit." \
          --logger "console;verbosity=minimal"
    
    - name: Run Integration Tests Only (for metrics)
      continue-on-error: true
      run: |
        dotnet test ./src/*.Tests/*.csproj \
          --no-build \
          --configuration Release \
          --filter "FullyQualifiedName~.Integration." \
          --logger "console;verbosity=minimal"
    
    - name: Generate Coverage Report
      run: |
        dotnet tool install -g dotnet-reportgenerator-globaltool
        reportgenerator \
          -reports:"./src/**/TestResults/coverage.cobertura.xml" \
          -targetdir:"./CoverageReport" \
          -reporttypes:"Html;JsonSummary;Badges"
    
    - name: Upload Coverage Report
      uses: actions/upload-artifact@v4
      with:
        name: coverage-report
        path: ./CoverageReport
    
    - name: Comment PR with Coverage
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const summary = JSON.parse(fs.readFileSync('./CoverageReport/Summary.json', 'utf8'));
          
          const lineCoverage = parseFloat(summary.summary.linecoverage);
          const branchCoverage = parseFloat(summary.summary.branchcoverage);
          const methodCoverage = parseFloat(summary.summary.methodcoverage);
          
          const threshold = 90;
          const lineStatus = lineCoverage >= threshold ? '✅' : '❌';
          const branchStatus = branchCoverage >= threshold ? '✅' : '❌';
          const methodStatus = methodCoverage >= threshold ? '✅' : '❌';
          
          const comment = `## 📊 Test Coverage Report
          
          **Project Structure:** Tests in \`src/[SolutionName].Tests/\`
          
          | Metric | Coverage | Target | Status |
          |--------|----------|--------|--------|
          | Lines | ${summary.summary.linecoverage}% | 90% | ${lineStatus} |
          | Branches | ${summary.summary.branchcoverage}% | 90% | ${branchStatus} |
          | Methods | ${summary.summary.methodcoverage}% | 90% | ${methodStatus} |
          
          ${lineCoverage >= threshold && branchCoverage >= threshold && methodCoverage >= threshold ? '🎉 **All coverage targets met!**' : '⚠️ **Coverage below 90% threshold**'}
          
          **Project Organization:**
          - 📁 Unit Tests: \`src/[Project].Tests/Unit/\`
          - 📁 Integration Tests: \`src/[Project].Tests/Integration/\`
          - 📁 Shared Resources: \`src/[Project].Tests/Shared/\`
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
    
    - name: Fail if coverage below 90%
      run: |
        COVERAGE=$(jq -r '.summary.linecoverage' ./CoverageReport/Summary.json | sed 's/%//')
        if (( $(echo "$COVERAGE < 90" | bc -l) )); then
          echo "❌ Coverage $COVERAGE% is below 90% threshold"
          exit 1
        fi
```

---

