# Referências por eixo

Ao registrar um achado, cite o princípio e a referência desta tabela. Use o nome do conceito como aparece na obra (ex.: "módulo raso — Ousterhout", "shotgun surgery — Fowler").

| Referência | Eixos | Conceitos úteis |
| --- | --- | --- |
| ISO/IEC 25010 — Modelo de qualidade de produto | Todos | Subcaracterísticas de manutenibilidade |
| Visser et al., *Building Maintainable Software* — edição C# (O'Reilly/SIG) | A2, A5, A6, A11 | Unidades pequenas e simples, interfaces de unidade pequenas, acoplamento entre módulos |
| John Ousterhout, *A Philosophy of Software Design* | A3, A4, A10, A12 | Módulos profundos vs. rasos, complexidade acidental, pass-through methods, comentários de intenção |
| Felienne Hermans, *The Programmer's Brain* | A1, A3, A4 | Carga cognitiva, chunking, leitura de código desconhecido |
| G. Ann Campbell, *Cognitive Complexity* (white paper, SonarSource) | A2 | Complexidade cognitiva vs. ciclomática |
| Thomas McCabe, "A Complexity Measure" (1976) | A2 | Complexidade ciclomática |
| Chidamber & Kemerer, "A Metrics Suite for Object Oriented Design" (1994) | A5 | CBO, LCOM |
| Martin Fowler, *Refactoring* (2ª ed.) | A2, A6, A11 | Shotgun surgery, divergent change, speculative generality, middle man |
| Sandi Metz, "The Wrong Abstraction" (artigo) | A11 | Duplicação é mais barata que a abstração errada |
| Robert C. Martin, *Clean Code* / *Clean Architecture* | A1, A2, A5 | Nomenclatura, funções pequenas, regra de dependência, ISP, OCP |
| Jeff Bay, "Object Calisthenics" (*The ThoughtWorks Anthology*) | A2, A11 | Regras originais e contexto de exercício |
| Eric Evans, *Domain-Driven Design* | A1, A5 | Linguagem ubíqua, agregados, contextos delimitados |
| Vaughn Vernon, *Implementing Domain-Driven Design* | A5 | DDD tático e arquitetura hexagonal |
| Alistair Cockburn, "Hexagonal Architecture" (artigo) | A5 | Ports e adapters |
| Krzysztof Cwalina, Jeremy Barton e Brad Abrams, *Framework Design Guidelines* (3ª ed.) | A10, A12 | Desenho de APIs públicas .NET, extensibilidade, exceções, nomenclatura de bibliotecas |
| Joshua Bloch, "How to Design a Good API and Why it Matters" (palestra) | A12 | Superfície mínima, facilidade de uso correto |
| Adam Tornhill, *Software Design X-Rays* | A6 | Hotspots, acoplamento de mudança via histórico do Git |
| OpenTelemetry — Semantic Conventions (documentação) | A9 | Nomes de spans, atributos e métricas |
| Michael Nygard, "Documenting Architecture Decisions" (artigo) | A10 | Formato de ADR |
| Semantic Versioning 2.0.0 (semver.org) | A12 | Regras de versão major/minor/patch |

## Ferramentas para medir em vez de estimar

- **SonarQube:** complexidade cognitiva, duplicação.
- **NDepend:** acoplamento, regras de arquitetura, diff de API.
- **Code Metrics do Visual Studio:** Maintainability Index, complexidade ciclomática, profundidade de herança.
- **NetArchTest / ArchUnitNET:** P01, P02 e P17 como testes automatizados.
- **Microsoft.CodeAnalysis.PublicApiAnalyzers:** P15.
- **CodeScene:** hotspots e acoplamento de mudança.
