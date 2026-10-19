# Padrões .NET — BKS Stack

## Regras de dependência
Core (Domain + Ports) <- Infrastructure (Adapters) <- API/Worker.
Domain nunca referência infraestrutura. Domain/Core/Common sem
NuGet externo. Composition Root só em Program.cs.

## SingleProject (referência)
{ServiceName}/
  _Shared/Domain/Core/Common/Pipeline/ (Orchestrator, Steps)
  _Shared/Domain/Core/Common/Transactions/BaseTransaction.cs
  _Shared/Adapters/ (Inbound/API, Outbound/Persistence)
  Features/{Contexto}Context/{Entidade}/
    Domain/  Persistence/  {Operação}/ (Steps, Transactions, UseCase)

## MultiProject
{ServiceName}.Core / .Infrastructure / .API (ou .Worker)

## Solution e asserção (ADR-010, 27/08)
- Toda solution .NET 10 e `.slnx` (formato padrão do SDK 10). `.sln` classico
  só quando alguma ferramenta exigir.
- Asserção em teste: `Assert` nativo do xUnit. NUNCA FluentAssertions — a v8
  passou a licença comercial paga (Xceed); a v7.x e a última Apache 2.0.

## Pipeline por complexidade
Rico: Full (Validation+Pre+Processing+Post)
CRUD: Minimal (GetById/List/Delete) ou Standard (Create/Update)

> Detalhes completos: skill bks-dotnet-solutions (entrevista obrigatória).
