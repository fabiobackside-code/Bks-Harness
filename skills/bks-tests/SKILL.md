---
name: bks-tests
description: >
  Analisa uma solution .NET, cria ou melhora um projeto único de testes xUnit dentro de src/
  e leva a cobertura a 90%+ em linhas, branches e métodos, com conformidade SonarQube.
  Use sempre que o usuário quiser criar testes para uma solution .NET, subir a cobertura,
  montar projeto de testes, gerar relatorio de cobertura, corrigir issues do SonarQube em
  testes, ou configurar coverlet e ReportGenerator. Trigger: cobertura de testes, xUnit,
  90% de cobertura, projeto de testes .NET, coverlet, ReportGenerator, SonarQube nos testes,
  testes unitários e de integração .NET.
---

# BKS-TESTS — Cobertura de testes em solution .NET

**Idioma:** interação e documentação gerada em **PT-BR**. Código, nomes de classe, método e
variavel em **inglês**.

## O que esta skill entrega

1. Analise da estrutura da solution e do que já existe de teste
2. Um projeto único de testes xUnit, dentro de `src/`, organizado em `Unit/`, `Integration/` e
   `Shared/`
3. Cobertura de 90%+ em linhas, branches e métodos
4. Relatorio HTML navegavel
5. Scripts de execução e integração com CI/CD
6. Guia de testes no repositório

## Duas regras que não se negociam

### Localização do projeto de testes

O projeto de testes fica em `src/`, junto dos projetos de produção:

```
src/
├── [ProjectName1]/
├── [ProjectName2]/
└── [SolutionName].Tests/     <- aqui
```

Nunca em `tests/`, `test/` ou na raiz. A solution inteira vive em `src/`; separar os testes
quebra a consistência, alonga os caminhos relativos entre projetos e complica build e deploy.

Um projeto só. Unitario e integração convivem nele, separados por diretório — não por projeto.

### Biblioteca de asserção

Use exclusivamente o `Assert` nativo do xUnit.

Nunca instale FluentAssertions: a v8 passou a licença comercial paga (Xceed) e a v7.x e a última
sob Apache 2.0. Não substitua por Shouldly nem equivalente.

## Fases

Execute na ordem. Cada fase tem sua referência — **abra a referência da fase no momento em que
for executa-la**, não antes.

| Fase | O que faz | Referencia |
|---|---|---|
| 1 | Mapeia a solution, os projetos e os gaps de teste | `references/solution-analysis.md` |
| 2 | Cria ou melhora o projeto de testes, com pacotes e coverage configurados | `references/test-project-setup.md` |
| 3 | Prioriza o que testar e gera os testes | `references/coverage-strategy.md` + `references/test-templates.md` |
| 4 | Executa com cobertura e gera o relatorio HTML | `references/coverage-execution.md` |
| 5 | Cria os scripts de automação e a integração com CI/CD | `references/coverage-execution.md` |
| 6 | Escreve o guia de testes do repositório | `references/test-docs-template.md` |

**Antes de gerar qualquer arquivo de teste**, leia `references/sonarqube-conformance.md` — são
cinco regras que evitam issue de SonarQube no código gerado (nullable, value type em
`Assert.NotNull`, using duplicado, `SqlException` obsoleto, mock com retorno nullable) e o
checklist de validação por arquivo.

## Antes de começar

Confirme com o usuário:

1. **Alvo de cobertura** — 90% e o default desta skill. Solution legada as vezes pede uma escada
   (70% agora, 90% em duas fases). Pergunte se 90% direto e realista aqui.
2. **Projetos de infraestrutura a excluir** — wrapper de transporte, adaptador de socket,
   biblioteca gerada. Cobrir isso não mede nada util e derruba o percentual da solution. Se
   houver, peça o padrão de nome; a exclusão entra no `sonar-project.properties` e no `.csproj`.
3. **Testes de integração** — se a solution depende de banco ou broker, confirme se há
   Testcontainers ou ambiente disponível. Sem isso, a fase de integração fica de fora e o alvo
   de cobertura muda.

Não pergunte o que da para descobrir lendo a solution.

## Conduta

**Mostre progresso por fase**, com o que foi criado e o percentual atingido. Não encerre sem
validar a cobertura contra o alvo — relatorio que não foi conferido não e entrega.

Se o alvo não for atingido, diga o número real, aponte as classes que faltam e proponha o próximo
passo. Nunca declare cobertura atingida sem a saída do relatorio.
