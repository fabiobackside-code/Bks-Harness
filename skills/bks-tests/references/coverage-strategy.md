## 📋 FASE 3: GERAR TESTES COM 90%+ DE COBERTURA

### **Passo 3.1: Análise de Priorização**

**Crie arquivo:** `PLANO_TESTES.md`

```markdown
# Plano de Testes - Priorização

## Estrutura do Projeto

**Localização dos Testes:** `src/[SolutionName].Tests/`

```
src/
├── [ProjectName1]/         ← Código de produção
├── [ProjectName2]/         ← Código de produção
└── [SolutionName].Tests/   ← TESTES (Unit/, Integration/, Shared/)
```

## Prioridade CRÍTICA (95%+ obrigatório)

### 1. Domain/Core Layer
**Meta:** 98%+ de cobertura
**Localização no projeto de testes:** `src/[SolutionName].Tests/Unit/Domain/`

- [ ] Entidades de domínio
- [ ] Value Objects
- [ ] Aggregates
- [ ] Lógica de negócio

**Justificativa:** Core business rules - mais crítico

### 2. Application Layer
**Meta:** 95%+ de cobertura
**Localização no projeto de testes:** `src/[SolutionName].Tests/Unit/Application/`

- [ ] Use Cases
- [ ] Services
- [ ] Validators
- [ ] Mappers

**Justificativa:** Orquestração de lógica de negócio

### 3. Adapters/Infrastructure
**Meta:** 90%+ de cobertura
**Localização no projeto de testes:** `src/[SolutionName].Tests/Unit/Adapters/` e `Integration/`

- [ ] Repositories (lógica, não apenas CRUD)
- [ ] External Service Clients
- [ ] Mappers de dados

**Justificativa:** Integrações críticas

## Prioridade ALTA (85%+ aceitável)

### 4. Controllers/API Endpoints
**Meta:** 90%+ de cobertura
**Localização no projeto de testes:** `src/[SolutionName].Tests/Integration/API/`

- [ ] Validação de requests
- [ ] Mapeamento de responses
- [ ] Error handling

### 5. Utilities/Helpers
**Meta:** 85%+ de cobertura
**Localização no projeto de testes:** `src/[SolutionName].Tests/Unit/Utilities/`

- [ ] Extensions methods
- [ ] Helper classes

## Prioridade MÉDIA (pode ficar 75-85%)

### 6. Configuration/Startup
**Localização no projeto de testes:** `src/[SolutionName].Tests/Integration/Configuration/`

- [ ] DI Configuration
- [ ] Middleware setup
- [ ] Program.cs

**Justificativa:** Código de infraestrutura, difícil de testar, baixo valor

## Classes a EXCLUIR da Cobertura

- [ ] DTOs (Pure data classes sem lógica)
- [ ] Migrations
- [ ] Auto-generated code
- [ ] Program.cs / Startup.cs (configuração)
- [ ] [Outras classes identificadas]

---

## Organização no Projeto Único (src/)

```
src/[SolutionName].Tests/
├── Unit/              ← Testes Unitários (isolados, rápidos, < 100ms)
│   └── [Espelha estrutura dos projetos em src/]
│
├── Integration/       ← Testes de Integração (com dependências, < 5s)
│   ├── API/          ← Testes de endpoints
│   ├── Database/     ← Testes com banco
│   └── External/     ← Testes com serviços externos
│
└── Shared/           ← Código compartilhado entre Unit e Integration
    ├── Builders/     ← Test data builders
    ├── Fixtures/     ← xUnit fixtures/collections
    └── Helpers/      ← Métodos auxiliares
```
```


### **Passo 3.3: Diretrizes de Qualidade dos Testes**

Cada teste DEVE seguir:

✅ **Padrão AAA (Arrange-Act-Assert)**
- Arrange: Setup de dados e mocks
- Act: Executar método sendo testado
- Assert: Verificar resultado

✅ **Nomenclatura Clara**
- Formato: `[MetodoTestado]_[Cenário]_[ResultadoEsperado]`
- Exemplo: `CalcularDesconto_ComValorNegativo_DeveLancarException`

✅ **Um Assert por Conceito**
- Pode ter múltiplos asserts, mas testando o MESMO conceito
- Se testar conceitos diferentes, separar em testes diferentes

✅ **Independência**
- Testes não devem depender uns dos outros
- Ordem de execução não deve importar
- Testes unitários e de integração são independentes

✅ **Determinístico**
- Sempre retorna mesmo resultado
- Evitar DateTime.Now, Random, chamadas externas
- Usar Builders para dados consistentes

✅ **Rápido**
- Testes unitários (Unit/): < 100ms cada
- Testes integração (Integration/): < 5s cada

✅ **Organização Física**
- Unit/: Testes isolados, sem I/O, sem banco
- Integration/: Testes com dependências externas
- Shared/: Código reutilizável

✅ **Cobertura de Cenários**
Para cada método, testar:
1. ✅ Caminho feliz (happy path)
2. ✅ Validações de entrada (null, vazio, inválido)
3. ✅ Edge cases (limites, valores extremos)
4. ✅ Exceções esperadas
5. ✅ Interações com dependências
6. ✅ Diferentes branches (if/else, switch)

---

