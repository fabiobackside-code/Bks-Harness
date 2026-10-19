# Suítes de eval do bks-harness

Casos para `claude plugin eval`. Cada diretório tem um `case.yaml` com o prompt, os graders e as
tags.

```
claude plugin eval .
claude plugin eval . --case 'dotnet-*'
claude plugin eval . --tag guarda
claude plugin eval . --threshold 0.8
```

## O que estas suites verificam

Comportamento, não estrutura. A pergunta e se a skill ainda **decide certo** depois de mexerem
nela — se recusa MediatR, se mantém o projeto de testes em `src/`, se pergunta antes de assumir.

A verificação de que o arquivo continua integro (frontmatter, referência que resolve, comando
documentado que existe) e da suite estrutural, em `tests/test_structure.py`, que roda sem
depender de modelo.

As duas se complementam: a estrutural pega o refactor que quebrou o arquivo, e estas pegam o
refactor que manteve o arquivo valido e perdeu a regra.

## Os casos

Cada caso testa a regra **sob pressão**: o prompt pede explicitamente o que a skill deve recusar,
ou descreve o atalho que ela não deve tomar. Um caso que só pergunta o que a skill já quer
responder não mede nada.

| Caso | Pressão aplicada |
|---|---|
| `dotnet-sem-dispatcher` | pede MediatR pelo nome |
| `dotnet-txc` | pede propagação de contexto sem dizer como |
| `tests-assert-nativo` | pede FluentAssertions pelo nome |
| `tests-local-projeto` | pede o projeto de testes em `tests/` na raiz |
| `doc-writer-teto-comentario` | pede comentario longo com alerta em vermelho |
| `security-audit-autorização` | afirma que o time e um pentest já aprovaram |
| `debug-reproduz-antes` | pede o null check direto, sem diagnostico |
| `refactor-rede-antes` | mistura refatoração, correção de bug e otimização |
| `api-design-contrato` | traz um desenho pronto com GET que altera estado |
| `frontend-design-identidade` | pede "algo simples e padrão" |
| `pr-writer-le-diff` | descreve a mudança como "nada demais" |
| `arch-notação-bks` | não menciona cor nem convenção — a notação tem que sair sozinha |
| `arch-fallback-renderer` | pede renderer externo e logo de marca |
| `new-project-perfil` | descreve um projeto sem nomear o perfil |
| `bks-sdd-fase-0` | invoca a fase sem dar o nome do workspace |
| `bks-sdd-fase-1` | pede PRD com escopo curto demais |
| `plan-tasks-atomicas` | pede plano onde caberia começar a implementar |
| `ts-seleção-tipo` | descreve backend sem dizer de que tipo |
| `writing-decisao-no-texto` | pede o ADR entre colchetes, "vale ressaltar" e alerta vermelho no título |
| `maintainability-inventario-pergunta` | manda aplicar critério de .NET ao front Node e proíbe perguntar |

## Ablação

O default e `--ablation with-without`: cada caso roda também sem o plugin, e o relatorio mostra o
delta. E o número que importa — um caso que passa nos dois bracos não está medindo a skill, está
medindo o modelo.

Grader marcado `with-only` (o `tool_used: Skill`, por exemplo) indica que a skill disparou, e não
entra na pontuação.

## Estado

Escritas contra o formato documentado em `claude plugin eval --help`, **ainda não executadas** —
o comando está em early access. Ao rodar pela primeira vez, espere ajustar campo e limiar antes
de tratar o resultado como linha de base.
