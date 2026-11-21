---
name: bks-tests
description: >
  Escreve e revisa testes em qualquer stack (.NET, Python, TypeScript, Go) e, numa solution .NET,
  cria o projeto único de testes xUnit dentro de src/ e leva a cobertura a 90%+ com conformidade
  SonarQube. Use sempre que o usuário pedir para escrever um teste, um script de teste ou de
  checagem, revisar teste existente, montar projeto de testes, subir a cobertura ou configurar
  coverlet e ReportGenerator. Trigger: escrever teste, teste unitário, teste de integração,
  xUnit, pytest, node --test, go test, script de checagem, cobertura de testes, 90% de
  cobertura, coverlet, ReportGenerator, SonarQube nos testes, FluentAssertions.
---

# BKS-TESTS — Testes em qualquer stack e cobertura em solution .NET

**Idioma:** interação e documentação gerada em **PT-BR**. Código, nomes de classe, método e
variável em **inglês**.

## Regras de qualquer stack

Valem para todo teste e todo script de checagem, pedido avulso ou dentro das fases abaixo.

### Pasta fora de repositório é criada pelo teste

Teste que precisa de diretório fora de repositório git cria a própria pasta temporária
(`tempfile.TemporaryDirectory`, `tmp_path`, `t.TempDir()`, `fs.mkdtemp`) e a remove no fim.
Nunca usa a home do usuário nem outra pasta fixa da máquina: a home pode ser um repositório
(dotfiles versionados), e o teste passa a depender de onde roda. Vale mesmo quando o usuário
sugere a home.

### Falha sai com código diferente de zero

Script de teste ou de checagem sai com código 1 quando algo falha e com 0 só quando tudo passa.
Imprimir a contagem não basta: `run.sh`, CI e pre-commit leem o código de saída, não o texto. Vale
mesmo quando o usuário diz que o resumo impresso basta; explique o motivo ao recusar.

### Biblioteca de asserção em .NET

Use exclusivamente o `Assert` nativo do xUnit, inclusive quando o usuário pede FluentAssertions
pelo nome: escreva o teste com `Assert` e diga por quê.

Nunca instale FluentAssertions: a v8 passou a licença comercial paga (Xceed) e a v7.x é a última
sob Apache 2.0. Não substitua por Shouldly nem equivalente.

## Solution .NET — o que esta skill entrega

1. Análise da estrutura da solution e do que já existe de teste
2. Um projeto único de testes xUnit, dentro de `src/`, organizado em `Unit/`, `Integration/` e
   `Shared/`
3. Cobertura de 90%+ em linhas, branches e métodos
4. Relatório HTML navegável
5. Scripts de execução e integração com CI/CD
6. Guia de testes no repositório

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

Vale mesmo quando o usuário pede `tests/` pelo nome ou diz que é como costuma organizar: crie o
projeto em `src/` e diga por quê, em vez de seguir o pedido ou mudar a estrutura em silêncio.

Um projeto só. Unitário e integração convivem nele, separados por diretório — não por projeto.

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

## Histórico de regras

Regra que entrou pelo `/bkhar:retro`, com a proposta de origem.
- 2026-11-18 · Teste que precisa de pasta fora de repositório git cria a própria pasta temporária; a home do usuário pode ser um repositório. · origem: `archive/proposals/bks-harness--2026-11-18-teste-que-precisa-de-pasta-fora-de-repositorio-g.md` (save 2026-11-18 · Ações 004 a 008; evidência: test_secret_guard falhou com PROJECT sob a home (C:/Users/... é repositório git); corrigido no commit 0754210)
- 2026-11-18 · Script de teste sai com código 1 quando há falha; imprimir a contagem não basta para o run.sh nem para o CI. · origem: `archive/proposals/bks-harness--2026-11-18-script-de-teste-sai-com-codigo-1-quando-ha-falha.md` (save 2026-11-18 · Ações 004 a 008; evidência: hooks/tests/test_guards.py imprimia falhas e saía 0; corrigido no commit f33ec27)
