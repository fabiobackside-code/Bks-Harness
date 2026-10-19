# Stack SQL

Critérios para scripts SQL mantidos como aplicação própria: DDL, procedures, functions, views,
jobs e scripts de carga. SQL embutido no código de uma aplicação é avaliado pela stack dessa
aplicação, não por esta.

## Detecção

| Sinal | Conclusão |
| --- | --- |
| Pasta com arquivos `.sql` fora de projeto de código (ex.: `app/db/`, `app/sql/`) | Uma aplicação do tipo **Scripts SQL** |
| `.sqlproj` | Uma aplicação do tipo **Scripts SQL** |
| Pasta de migrations de ferramenta (Flyway, Liquibase, DbUp) | Parte da aplicação Scripts SQL que a contém |

Na dúvida sobre o que é uma aplicação (por exemplo, `.sql` espalhado em várias pastas), pergunte
antes de agrupar.

## Repertório da persona nesta stack

| Atributo | Repertório |
| --- | --- |
| Linguagem | T-SQL e PL/pgSQL: DML, DDL, joins, CTE, funções de janela simples |
| Programação | Procedures com parâmetros tipados, `TRY/CATCH`, transação explícita |
| Desempenho | Leitura de plano de execução, índice que cobre a consulta |

### Fora do repertório (cada uso conta como custo cognitivo)

- SQL dinâmico montado por concatenação, mesmo quando seguro.
- Cursores e laços linha a linha onde uma operação em conjunto resolveria.
- Hints de consulta e de índice sem medição registrada.
- CTE recursiva, `PIVOT` dinâmico e `MERGE` com várias cláusulas.
- Triggers com regra de negócio.

## Unidade de análise

O objeto de banco e quem o chama: procedure ou script, os objetos que ele toca e a ordem de
execução. Para scripts de deploy, o conjunto que leva o banco de uma versão à seguinte.

## Critérios

### Nomes e organização (A1, A6)

- Convenção única de nome para tabela, coluna, constraint e procedure.
- Um objeto por arquivo, com o nome do arquivo igual ao do objeto.
- Ordem de execução explícita: prefixo numérico, manifesto ou ferramenta de migration.

### Complexidade (A2, A3, A4)

- Procedure legível em uma tela; acima disso, dividida por etapa com nome.
- Procedure que chama procedure, view sobre view: conte os saltos como em A3.
- SQL dinâmico só com `sp_executesql` e parâmetros, nunca concatenando entrada.

### Erros e transação (A8)

- `TRY/CATCH` com `THROW` ou código de retorno padronizado em toda a pasta.
- Transação aberta e fechada no mesmo nível; nada de `COMMIT` em procedure chamada por outra que
  também abre transação, sem `SAVE TRANSACTION`.
- `SET XACT_ABORT ON` onde há transação.

### Operação e deploy (A9)

- Scripts idempotentes: `IF NOT EXISTS`, `CREATE OR ALTER`, ou ferramenta de migration que
  controla a versão aplicada.
- Script de rollback, ou o motivo registrado de não haver.
- Nenhuma credencial, servidor ou banco fixo no script.

### Testes e documentação (A7, A10)

- Testes de procedure (tSQLt, pgTAP) ou teste de integração da aplicação que a consome.
- Cabeçalho de uma linha por objeto dizendo o que ele faz; regra de negócio mantida no banco
  justificada em ADR.
