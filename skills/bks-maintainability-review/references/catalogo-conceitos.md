# Catálogo de conceitos e referências canônicas

Use esta lista como ponto de partida para citar a origem de cada conceito encontrado na solução. Ela não é exaustiva: conceitos fora dela podem entrar, desde que a referência seja confiável (ver regras em `fundamentacao.md`).

## Princípios de design

| Conceito | Referência canônica |
| --- | --- |
| SOLID (conjunto) | Robert C. Martin, *Agile Software Development: Principles, Patterns, and Practices* (2002) |
| SRP — Responsabilidade única | Robert C. Martin, *Agile Software Development*; *Clean Architecture*, cap. sobre SRP |
| OCP — Aberto/Fechado | Bertrand Meyer, *Object-Oriented Software Construction*; reformulação em Martin |
| LSP — Substituição de Liskov | Barbara Liskov e Jeannette Wing, "A Behavioral Notion of Subtyping" (1994) |
| ISP — Segregação de interfaces | Robert C. Martin, *Agile Software Development* |
| DIP — Inversão de dependência | Robert C. Martin, *Agile Software Development*; Mark Seemann e Steven van Deursen, *Dependency Injection Principles, Practices, and Patterns* |
| DRY | Andrew Hunt e David Thomas, *The Pragmatic Programmer* |
| KISS / YAGNI | Kent Beck, *Extreme Programming Explained* |
| Lei de Demeter | Karl Lieberherr e Ian Holland, trabalhos do Projeto Demeter (Northeastern University) |
| Ocultação de informação | David Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" (1972) |
| Object Calisthenics | Jeff Bay, em *The ThoughtWorks Anthology* |
| Módulos profundos, complexidade | John Ousterhout, *A Philosophy of Software Design* |
| Duplicação vs. abstração errada | Sandi Metz, "The Wrong Abstraction" (artigo) |

## Estilo arquitetural

| Conceito | Referência canônica |
| --- | --- |
| Arquitetura Hexagonal / Ports & Adapters | Alistair Cockburn, "Hexagonal Architecture" (artigo) |
| Clean Architecture, regra de dependência | Robert C. Martin, *Clean Architecture* |
| Microsserviços | Sam Newman, *Building Microservices* |
| Padrões de microsserviços (saga, outbox, API gateway) | Chris Richardson, *Microservices Patterns* |
| Sistemas de dados distribuídos | Martin Kleppmann, *Designing Data-Intensive Applications* |

## Domínio

| Conceito | Referência canônica |
| --- | --- |
| DDD estratégico e tático (contexto delimitado, linguagem ubíqua, entidade, value object, agregado, repositório, serviço de domínio) | Eric Evans, *Domain-Driven Design* |
| DDD na prática, eventos de domínio, regras de agregados | Vaughn Vernon, *Implementing Domain-Driven Design* |
| Introdução moderna a DDD | Vlad Khononov, *Learning Domain-Driven Design* |

## Estruturação do código

| Conceito | Referência canônica |
| --- | --- |
| Vertical Slice Architecture | Jimmy Bogard, "Vertical Slice Architecture" (artigo) |
| CQRS | Greg Young, documentos sobre CQRS; Martin Fowler, "CQRS" (bliki) |
| Padrões internos da organização (ex.: Pipeline Orchestration, Transaction Parameter Object, BKS-TXC) | Documentação interna ou skills da organização. Cite o documento interno como fonte e indique o conceito público mais próximo (ex.: Pipes and Filters, Parameter Object, Chain of Responsibility) |
| Pipes and Filters | Gregor Hohpe e Bobby Woolf, *Enterprise Integration Patterns* |
| Parameter Object | Martin Fowler, *Refactoring* (Introduce Parameter Object) |

## Padrões de projeto

| Conceito | Referência canônica |
| --- | --- |
| Strategy, Factory Method, Abstract Factory, Builder, Decorator, Adapter, Template Method, Chain of Responsibility, Observer | Gamma, Helm, Johnson e Vlissides, *Design Patterns* (1994) |
| Refatoração rumo a padrões | Joshua Kerievsky, *Refactoring to Patterns* |

## Padrões de aplicação corporativa

| Conceito | Referência canônica |
| --- | --- |
| Repository, Unit of Work, Data Mapper, Service Layer, DTO, Gateway | Martin Fowler, *Patterns of Enterprise Application Architecture* |
| Options pattern, injeção de dependência e configuração em .NET | Documentação oficial do .NET (Microsoft Learn) |

## Persistência e segurança

| Conceito | Referência canônica |
| --- | --- |
| Dapper (micro-ORM) | Documentação e repositório oficial do Dapper |
| Prevenção de SQL injection, consultas parametrizadas | OWASP, *SQL Injection Prevention Cheat Sheet* |
| Gestão de segredos | OWASP, *Secrets Management Cheat Sheet*; documentação oficial do CyberArk |
| Menor privilégio | Saltzer e Schroeder, "The Protection of Information in Computer Systems" (1975) |

## Integração e resiliência

| Conceito | Referência canônica |
| --- | --- |
| Competing Consumers, Idempotent Receiver, Dead Letter Channel, Message Channel | Hohpe e Woolf, *Enterprise Integration Patterns* |
| Transactional Outbox | Chris Richardson, *Microservices Patterns* |
| Timeout, Circuit Breaker, Bulkhead | Michael Nygard, *Release It!* |
| Retry com backoff em .NET | Documentação do Polly e de `Microsoft.Extensions.Resilience` |

## APIs e componentes

| Conceito | Referência canônica |
| --- | --- |
| REST | Roy Fielding, tese de doutorado (2000), cap. 5 |
| Problem Details para APIs HTTP | RFC 9457 |
| Semântica HTTP | RFC 9110 |
| Desenho de bibliotecas .NET | Cwalina, Barton e Abrams, *Framework Design Guidelines* |
| Desenho de APIs públicas | Joshua Bloch, "How to Design a Good API and Why it Matters" (palestra) |
| Versionamento semântico | Semantic Versioning 2.0.0 (semver.org) |

## Hospedagem, observabilidade e plataforma

| Conceito | Referência canônica |
| --- | --- |
| Generic Host, BackgroundService, Worker Service | Documentação oficial do .NET (Microsoft Learn) |
| Injeção de dependência | Seemann e van Deursen, *Dependency Injection Principles, Practices, and Patterns* |
| OpenTelemetry (traces, métricas, logs, convenções semânticas) | Documentação oficial do OpenTelemetry |
| Observabilidade | Charity Majors, Liz Fong-Jones e George Miranda, *Observability Engineering* |
| Twelve-Factor App | Adam Wiggins, The Twelve-Factor App (12factor.net) |
| Health checks, probes, OpenShift | Documentação oficial do Kubernetes e do OpenShift |

## Testes

| Conceito | Referência canônica |
| --- | --- |
| TDD | Kent Beck, *Test-Driven Development: By Example* |
| Dublês de teste (mock, stub, fake, spy) | Gerard Meszaros, *xUnit Test Patterns* |
| Pirâmide de testes | Mike Cohn, *Succeeding with Agile*; Martin Fowler, "TestPyramid" (bliki) |
| Testes unitários eficazes | Vladimir Khorikov, *Unit Testing Principles, Practices, and Patterns* |
| Código legado e pontos de teste | Michael Feathers, *Working Effectively with Legacy Code* |
| Testes de arquitetura | Documentação do NetArchTest / ArchUnitNET |
