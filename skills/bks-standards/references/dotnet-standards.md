# Padrões .NET — BKS Stack

## Regras de dependência
Domain (Core: Ports, Models, Common) <- Application (só no TXC) <- Adapters <- Host (`main/`).
Domain nunca referencia infraestrutura. Domain/Core/Common sem
NuGet externo. Composition Root em `main/ServiceConfiguration.cs`, chamado pelo `Program.cs`.

## SingleProject (referência)
{ServiceName}/
  Adapters/Inbound/ e Adapters/Outbound/ (uma pasta por porta declarada)
  Domain/Core/{Ports, Models, Settings, Common}/ (Common: PipelineResult<T>, só System.*)
  Domain/Services/ (só no padrão direto: {Entidade}Service com a regra)
  Application/Pipeline/ e Application/{Contexto}/ (só com TXC: base, códigos, executores)
  main/ (Program.cs, ServiceConfiguration.cs)

## MultiProject
{ServiceName}.Domain / .Application (só no TXC) / .Adapters.Inbound / .Adapters.Outbound / .Host;
as Ports moram em `Domain/Core/Ports/`

## Solution e asserção (ADR-010, 27/08)
- Toda solution .NET 10 e `.slnx` (formato padrão do SDK 10). `.sln` classico
  só quando alguma ferramenta exigir.
- Asserção em teste: `Assert` nativo do xUnit. NUNCA FluentAssertions — a v8
  passou a licença comercial paga (Xceed); a v7.x e a última Apache 2.0.

## Dependência, banco e tipagem
- NUNCA adicionar pacote NuGet sem confirmação explícita, em qualquer camada: listar o
  pacote, a versão e o motivo, e esperar a aprovação.
- NUNCA alterar migration existente. Mudança de schema é sempre migration nova, nomeada
  `{Timestamp}_{DescricaoEmIngles}`.
- NUNCA `dynamic` nem `object` sem justificativa explícita: tipagem forte é a regra.
- Preferir `record` a `class` em objeto imutável: TXC, envelope, Value Object e DTO de
  resposta.

## Forma do projeto
Padrão direto (sem TXC): adapter → I{Entidade}Service → aggregate → Port.
TXC (`txc: "base"`): adapter → IBksSession.ExecuteAsync(code, input); escrita no
BksTransactionalExecutor, com `[20]`; leitura no BksQueryExecutor. As duas formas
devolvem PipelineResult<T> e não se misturam no mesmo projeto.

> Detalhes completos: skill bks-dotnet-solutions (entrevista obrigatória).
