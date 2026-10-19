# ARQUITETURA-HEXAGONAL-GUIDELINES

> **Versão:** 2.0  
> **Escopo:** Estrutural — Ports & Adapters segundo o modelo original de Alistair Cockburn  
> **Paradigma:** Agnóstico de linguagem (exemplos em C# / .NET quando relevante)  
> **Temperatura de decisão:** 0.02 — regras prescritivas sobre estrutura, nomenclatura e dependências  
> **Fonte primária:** Alistair Cockburn — *Hexagonal Architecture* (2005, revisado 2023)

---

## PROPÓSITO DESTE ARQUIVO

Este guideline instrui agentes de IA e desenvolvedores sobre como estruturar projetos usando a **Arquitetura de Portas e Adaptadores (Ports & Adapters)** fiel ao modelo original de Alistair Cockburn — não uma variante renomeada. Inclui também como integrar as skills do ecossistema [agent-skills.techleads.club](https://agent-skills.techleads.club) neste workflow sem modificar a estrutura de specs existente.

---

## SEÇÃO 1 — O MODELO ORIGINAL PORTS & ADAPTERS

### A Metáfora do Hexágono

O hexágono NÃO representa seis lados ou seis camadas. É uma forma geométrica escolhida apenas para permitir que adaptadores sejam desenhados em cada "face". O que importa é a divisão em dois territórios:

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FORA DO HEXÁGONO          │   DENTRO DO HEXÁGONO           ║
║   (Mundo externo)           │   (A Aplicação)                ║
║                             │                                ║
║   Atores Primários          │   Portas Primárias             ║
║   (iniciam interação)       │   (contratos de entrada)       ║
║   ──────────────────────────│──────────────────────────────  ║
║   Adaptadores Primários     │   Lógica de Aplicação          ║
║   (Controller, CLI, Test)   │   (Use Cases / Application     ║
║                             │    Services)                   ║
║                             │                                ║
║                             │   Domínio                      ║
║                             │   (Regras de negócio puras)    ║
║                             │                                ║
║                             │   Portas Secundárias           ║
║   ──────────────────────────│   (contratos de saída)         ║
║   Adaptadores Secundários   │──────────────────────────────  ║
║   (DB, Email, API externa)  │                                ║
║   Atores Secundários        │                                ║
║   (acionados pela app)      │                                ║
║                             │                                ║
╚══════════════════════════════════════════════════════════════╝
```

### Terminologia Precisa (Use Sempre)

| Termo Original | Significado | O Que NÃO É |
|---|---|---|
| **Port (Porta)** | Interface definida DENTRO do hexágono | Camada, módulo, projeto |
| **Adapter (Adaptador)** | Implementação FORA do hexágono de uma Porta | Controller, Repository em si |
| **Primary Port** | Interface que a aplicação EXPÕE (entrada) | Não é "controller" |
| **Secondary Port** | Interface que a aplicação REQUER (saída) | Não é "repositório" |
| **Primary Adapter** | Implementa/usa o Primary Port (ex: Controller) | Não é "camada de apresentação" |
| **Secondary Adapter** | Implementa o Secondary Port (ex: EF Repository) | Não é "camada de infraestrutura" |
| **Primary Actor** | Quem usa a aplicação (humano, outro sistema, test) | O adapter em si |
| **Secondary Actor** | Sistema acionado pela aplicação (banco, email) | O adapter em si |

---

## SEÇÃO 2 — PORTAS (PORTS)

### Primary Ports — O Que a Aplicação Oferece

```
Definição exata (Cockburn):
  "A Primary Port é a interface que define os casos de uso da aplicação.
   É o contrato pelo qual o mundo externo acessa a funcionalidade."

Localização: DENTRO do hexágono — camada Application
Dono: A aplicação define, o adaptador externo implementa/usa

Formato canônico:
  - Uma interface por caso de uso (ou agrupamento coeso)
  - Nomes refletem intenção de negócio
  - Parâmetros são tipos do domínio da aplicação (Commands, Queries)
  - Nunca contém tipos de framework (HttpRequest, DbContext, etc.)

Exemplos:

  // Primary Port — definida DENTRO do hexágono (Application layer)
  interface ICriarPedido {
      Executar(command: CriarPedidoCommand): Result<PedidoId>
  }

  interface IConsultarPedido {
      BuscarPorId(query: BuscarPedidoQuery): Result<PedidoDetalheResponse>
      ListarPorCliente(query: ListarPedidosClienteQuery): Result<PedidoResumoResponse[]>
  }

  interface IConfirmarPedido {
      Executar(command: ConfirmarPedidoCommand): Result
  }
```

### Secondary Ports — O Que a Aplicação Requer

```
Definição exata (Cockburn):
  "A Secondary Port é a interface que a aplicação define para comunicar-se
   com atores secundários. A aplicação dirige — o adaptador serve."

Localização: DENTRO do hexágono — Domain (quando é necessidade do domínio)
             ou Application (quando é necessidade de orquestração)
Dono: A aplicação define, a infraestrutura implementa

Exemplos:

  // Secondary Port — necessidade do domínio (dentro do hexágono, Domain layer)
  interface IPedidoRepository {
      BuscarPorId(id: PedidoId): Pedido | null
      BuscarPendentesDoCliente(clienteId: ClienteId): Pedido[]
      Salvar(pedido: Pedido): void
  }

  // Secondary Port — necessidade da aplicação (dentro do hexágono, Application layer)
  interface INotificacaoService {
      NotificarPedidoConfirmado(pedidoId: PedidoId, email: Email): void
  }

  interface IProcessadorDePagamento {
      Processar(valor: Dinheiro, cartao: CartaoToken): ResultadoPagamento
  }

  interface IConsultaCep {
      Buscar(cep: string): EnderecoDTO | null
  }
```

### Regra de Ouro das Portas

```
REGRA: Portas são interfaces. São parte da aplicação.
       Adaptadores são implementações. São parte do mundo externo.

NUNCA confunda:
  ❌ "O repositório é a porta" → Errado. O repositório (EF, Dapper) é o ADAPTADOR.
     A INTERFACE IPedidoRepository é a PORTA.
  
  ❌ "O controller é a porta" → Errado. O controller é o ADAPTADOR.
     A INTERFACE ICriarPedido (use case) é a PORTA.

  ✅ Porta = interface que vive dentro do hexágono
  ✅ Adaptador = classe concreta que vive fora do hexágono
```

---

## SEÇÃO 3 — ADAPTADORES (ADAPTERS)

### Primary Adapters — Acionam a Aplicação

```
Definição: Código externo que traduz requests do mundo real para chamadas
           através de Primary Ports.

Localização: FORA do hexágono (Presentation / Driver layer)

Responsabilidade única: Traduzir formato externo → tipo da porta → chamar porta → traduzir resultado

Tipos de Primary Adapters:
  - HTTP Controller (REST, GraphQL)
  - gRPC Service Handler
  - CLI Command
  - Message Consumer (SQS, RabbitMQ consumer que INICIA processamento)
  - Test Double (o teste em si é um Primary Adapter!)
  - Scheduled Job (trigger de tempo que inicia caso de uso)

Padrão de implementação:

  // Primary Adapter — FORA do hexágono
  class PedidoController {
      constructor(private criarPedido: ICriarPedido) {}  // injeta a PORTA

      [POST /pedidos]
      async criar(httpRequest: HttpRequest): HttpResponse {
          // 1. Traduz formato HTTP → Command (tipo da porta)
          const command = CriarPedidoCommand.from(httpRequest.body)
          
          // 2. Chama através da Primary Port
          const result = await this.criarPedido.Executar(command)
          
          // 3. Traduz resultado → formato HTTP
          return result.match(
              id => HttpResponse.created({ id }),
              error => HttpResponse.unprocessable(error.message)
          )
      }
  }

  // Test como Primary Adapter — o teste usa a porta diretamente
  test("deve criar pedido válido") {
      const porta: ICriarPedido = new CriarPedidoHandler(mockRepo, mockNotif)
      const result = await porta.Executar(CriarPedidoCommand.valid())
      expect(result.isSuccess).toBe(true)
  }
```

### Secondary Adapters — Servem a Aplicação

```
Definição: Código externo que implementa Secondary Ports.
           A aplicação chama a porta; o adaptador executa a tecnologia.

Localização: FORA do hexágono (Infrastructure layer)

Tipos de Secondary Adapters:
  - Repository (EF Core, Dapper, MongoDB Driver)
  - Email Adapter (SendGrid, SES)
  - Payment Adapter (Stripe, PagSeguro)
  - Cache Adapter (Redis, MemoryCache)
  - Message Publisher (RabbitMQ publisher, SNS)
  - External API Adapter (ViaCep, Receita Federal)
  - File Storage Adapter (S3, Azure Blob)

Padrão de implementação:

  // Secondary Adapter — FORA do hexágono, implementa Secondary Port
  class PedidoRepositoryEfCore implements IPedidoRepository {
      constructor(private db: VendasDbContext) {}

      BuscarPorId(id: PedidoId): Pedido | null {
          // Responsabilidade: traduzir do modelo de persistência → Aggregate do domínio
          const entity = this.db.Pedidos.Find(id.Value)
          return entity != null ? PedidoMapper.toDomain(entity) : null
      }

      Salvar(pedido: Pedido): void {
          // Responsabilidade: traduzir do Aggregate → modelo de persistência
          const entity = PedidoMapper.toPersistence(pedido)
          this.db.SaveChanges(entity)
      }
  }

  // Secondary Adapter com ACL embutida (para sistemas externos com modelo diferente)
  class CorreiosFreteAdapter implements ICalculadoraDeFrete {
      Calcular(origem: Cep, destino: Cep, peso: Gramas): Dinheiro {
          // 1. Traduz tipos do domínio → tipos da API dos Correios
          const request = CorreiosMapper.toRequest(origem, destino, peso)
          
          // 2. Chama API externa
          const response = this.correiosHttpClient.Calcular(request)
          
          // 3. Traduz resposta da API → tipos do domínio (ACL embutida)
          return CorreiosMapper.toDomainPrice(response)
      }
  }
```

---

## SEÇÃO 4 — DENTRO DO HEXÁGONO

### Application Layer (Orquestração de Casos de Uso)

```
O que é: A "carne" do hexágono. Implementa as Primary Ports.
         Usa as Secondary Ports. NÃO contém regras de negócio.

Conteúdo:
  - Implementações de Primary Ports (Use Case Handlers, Application Services)
  - Commands e Queries (dados de entrada das portas)
  - Response DTOs (dados de saída das portas)
  - Secondary Ports que a aplicação define (interfaces de serviços de suporte)
  - Event Handlers (reage a Domain Events)
  - Pipeline behaviors (cross-cutting: logging, validação de input, transação)

Regra de dependência:
  ✅ Conhece: Domain
  ✅ Usa: Secondary Ports (interfaces) definidas aqui ou no Domain
  ❌ NÃO conhece: Adapters concretos
  ❌ NÃO conhece: Frameworks (HTTP, ORM, MQ)
```

### Domain Layer (Núcleo das Regras de Negócio)

```
O que é: O núcleo mais interno. Puro comportamento de negócio.
         Não sabe que existe um hexágono ao redor dele.

Conteúdo:
  - Entities e Aggregates
  - Value Objects
  - Domain Events
  - Domain Services
  - Secondary Ports que o domínio precisa (ex: IPedidoRepository)
  - Domain Exceptions
  - Specifications

Regra de dependência:
  ✅ Conhece: apenas si mesmo (linguagem/runtime base)
  ❌ NÃO conhece: Application layer
  ❌ NÃO conhece: NENHUMA biblioteca externa
  ❌ NÃO conhece: que existe HTTP, banco, mensageria
```

---

## SEÇÃO 5 — FLUXO DE CONTROLE COMPLETO

```
Fluxo de uma requisição (Primary Adapter → Primary Port → Domain → Secondary Port → Secondary Adapter):

  [HTTP Request]
       │
       ▼
  [Primary Adapter: PedidoController]
  ─ traduz HttpRequest → CriarPedidoCommand
       │
       ▼ (via injeção da Primary Port)
  [Primary Port: ICriarPedido]
       │
       ▼ (implementação dentro do hexágono)
  [Application: CriarPedidoCommandHandler]
  ─ valida command
  ─ chama domain (pedido = Pedido.Criar(command.ClienteId, command.Itens))
  ─ chama secondary port: IPedidoRepository.Salvar(pedido)
  ─ chama secondary port: INotificacaoService.NotificarPedidoCriado(...)
  ─ retorna Result<PedidoId>
       │
       ▼ (implementações fora do hexágono)
  [Secondary Adapter: PedidoRepositoryEfCore] ─── persiste
  [Secondary Adapter: SendGridNotificação]    ─── envia email
       │
       ▼ (resultado volta através da porta)
  [Primary Adapter: PedidoController]
  ─ traduz Result → HttpResponse 201 Created
       │
       ▼
  [HTTP Response]

REGRA DE DIREÇÃO DE CONTROLE:
  Primary: Adapter → Port → Application (o adapter aciona)
  Secondary: Application → Port → Adapter (a aplicação aciona)
  Domínio: nunca aciona nada fora de si mesmo
```

---

## SEÇÃO 6 — ESTRUTURA DE PROJETO

### Estrutura Canônica por Bounded Context

```
src/
  Vendas/                                    ← Bounded Context
    │
    ├── Hexagon/                             ← DENTRO DO HEXÁGONO
    │   ├── Domain/                          ← Núcleo
    │   │   ├── Pedidos/
    │   │   │   ├── Pedido.cs                (Aggregate Root)
    │   │   │   ├── ItemPedido.cs            (Entity interna)
    │   │   │   ├── PedidoStatus.cs          (Value Object)
    │   │   │   ├── PedidoConfirmado.cs      (Domain Event)
    │   │   │   └── IPedidoRepository.cs     ← SECONDARY PORT (necessidade do domínio)
    │   │   ├── Clientes/
    │   │   │   └── ClienteId.cs             (Value Object)
    │   │   └── Shared/
    │   │       ├── DomainException.cs
    │   │       ├── Entity.cs
    │   │       └── ValueObject.cs
    │   │
    │   └── Application/                     ← Orquestração + definição de portas
    │       ├── Ports/
    │       │   ├── Primary/                 ← PRIMARY PORTS (o que a app oferece)
    │       │   │   ├── ICriarPedido.cs
    │       │   │   ├── IConfirmarPedido.cs
    │       │   │   └── IConsultarPedido.cs
    │       │   └── Secondary/               ← SECONDARY PORTS (o que a app requer da infra)
    │       │       ├── INotificacaoService.cs
    │       │       └── IUnitOfWork.cs
    │       └── UseCases/
    │           ├── CriarPedido/
    │           │   ├── CriarPedidoCommand.cs
    │           │   ├── CriarPedidoCommandHandler.cs  (implementa ICriarPedido)
    │           │   └── CriarPedidoResponse.cs
    │           ├── ConfirmarPedido/
    │           │   ├── ConfirmarPedidoCommand.cs
    │           │   └── ConfirmarPedidoCommandHandler.cs
    │           └── ConsultarPedido/
    │               ├── BuscarPedidoQuery.cs
    │               ├── ConsultarPedidoHandler.cs     (implementa IConsultarPedido)
    │               └── PedidoDetalheResponse.cs
    │
    ├── Adapters/                            ← FORA DO HEXÁGONO
    │   ├── Primary/                         ← PRIMARY ADAPTERS (acionam a app)
    │   │   └── Http/
    │   │       ├── PedidosController.cs     (usa ICriarPedido, IConsultarPedido)
    │   │       └── PedidoRequestMapper.cs
    │   │
    │   └── Secondary/                       ← SECONDARY ADAPTERS (servem a app)
    │       ├── Persistence/
    │       │   ├── VendasDbContext.cs
    │       │   ├── PedidoRepositoryEfCore.cs   (implementa IPedidoRepository)
    │       │   └── Mappings/
    │       │       └── PedidoConfiguration.cs
    │       ├── Messaging/
    │       │   └── RabbitMqPublisher.cs
    │       ├── Email/
    │       │   └── SendGridNotificação.cs    (implementa INotificacaoService)
    │       └── ExternalApis/
    │           └── CorreiosFreteAdapter.cs   (implementa ICalculadoraDeFrete + ACL)
    │
    └── Composition/                         ← Composição de dependências (DI Root)
        └── VendasModule.cs                  (registra todos os bindings Port → Adapter)
```

### Por Que Esta Estrutura Reflete Ports & Adapters

```
Regra de leitura da estrutura:
  Hexagon/Domain/       → Nunca importa nada de fora de Hexagon/
  Hexagon/Application/  → Importa apenas Hexagon/Domain/
  Adapters/Primary/     → Importa apenas Hexagon/Application/Ports/Primary/
  Adapters/Secondary/   → Importa apenas Hexagon/Domain/ e Hexagon/Application/Ports/Secondary/
  Composition/          → Importa tudo (o único lugar que conhece todos)

Verificação automatizável (ArchUnit / NetArchTest):
  Regra 1: Nenhum tipo em Hexagon/ deve referenciar tipo em Adapters/
  Regra 2: Nenhum tipo em Hexagon/Domain/ deve referenciar tipo em Hexagon/Application/
  Regra 3: Nenhum tipo em Adapters/Primary/ deve referenciar Adapters/Secondary/ diretamente
```

---

## SEÇÃO 7 — ANTI-CORRUPTION LAYER (ACL) COMO ADAPTADOR

```
A ACL é um SECONDARY ADAPTER especializado — não uma camada separada.

Quando usar ACL:
  - Integração com sistema externo com modelo de dados diferente do seu
  - Integração com sistema legado
  - Quando o vocabulário externo não mapeia 1:1 com sua linguagem ubíqua

Onde fica: Adapters/Secondary/ExternalApis/ (ou Adapters/Secondary/Legacy/)

O que faz:
  1. Recebe chamada via Secondary Port (sua interface limpa)
  2. Traduz tipos do domínio → tipos do sistema externo
  3. Chama sistema externo
  4. Traduz resposta do sistema externo → tipos do domínio
  5. Retorna para a aplicação através da Secondary Port

O domínio NUNCA sabe que existe um sistema externo.
O domínio NUNCA vê tipos do sistema externo.
```

---

## SEÇÃO 8 — CQRS SOBRE PORTS & ADAPTERS

```
CQRS (Command Query Responsibility Segregation) se encaixa naturalmente:

Primary Ports de Command (mudam estado):
  interface ICriarPedido      → CriarPedidoCommand
  interface IConfirmarPedido  → ConfirmarPedidoCommand
  interface ICancelarPedido   → CancelarPedidoCommand

Primary Ports de Query (leem estado):
  interface IConsultarPedido  → BuscarPorIdQuery, ListarPorClienteQuery

Secondary Ports diferenciados:
  Write: IPedidoRepository (aggregate completo, ORM)
  Read:  IPedidoReadModel  (query otimizado, pode ser Dapper/View direta)

Secondary Adapters para Read:
  PedidoReadModelDapper implements IPedidoReadModel
  → Vai direto para banco com SQL otimizado
  → Retorna DTO de leitura (não aggregate)
  → Bypass do domain para reads puros ✅ (intencional no CQRS)
```

---

## SEÇÃO 9 — REGRAS DE DEPENDÊNCIA RESUMIDAS

```
┌─────────────────────────────────────────────────────────┐
│                    REGRA DE DEPENDÊNCIA                  │
│                                                          │
│  Adapters/Primary  ──►  Application (Primary Ports)      │
│  Adapters/Secondary ◄──  Application (Secondary Ports)   │
│  Application       ──►  Domain                           │
│  Domain            ──►  (nada externo)                   │
│                                                          │
│  Seta ──► significa "depende de / importa"               │
│                                                          │
│  NUNCA:                                                  │
│  Domain   ──► Application                                │
│  Domain   ──► Adapters                                   │
│  Hexagon  ──► Adapters (qualquer direção)                │
└─────────────────────────────────────────────────────────┘
```

---

## SEÇÃO 10 — ADOTANDO SKILLS DO TECHLEADS.CLUB NESTE WORKFLOW

> **Fonte:** [agent-skills.techleads.club](https://agent-skills.techleads.club) |
> [github.com/tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills)  
> **Princípio:** As skills abaixo são adotadas como **aceleradores de processo** dentro
> do workflow de Ports & Adapters. Elas NÃO modificam a estrutura de specs existente —
> são ativadas em momentos específicos do ciclo de design/desenvolvimento.

---

### SKILL: `domain-analysis`

**Papel no workflow Ports & Adapters:**
A `domain-analysis` é ativada na fase de **descoberta de Secondary Ports**. Ela analisa o domínio para identificar quais conceitos precisam de abstrações externas — ou seja, quais interfaces devem existir em `Hexagon/Domain/` ou `Hexagon/Application/Ports/Secondary/`.

**Quando acionar:**
```
TRIGGER: Antes de criar qualquer Secondary Adapter
PERGUNTA QUE A SKILL RESPONDE:
  "Quais necessidades o domínio tem que precisam de contratos externos?"
  "Existem conceitos de domínio sendo modelados incorretamente como infra?"

INPUTS QUE VOCÊ FORNECE:
  - Código do Bounded Context atual (ou descrição textual do domínio)
  - Contexto de negócio (o que o sistema faz)

OUTPUTS ESPERADOS:
  - Lista de Secondary Ports candidatas com justificativa de domínio
  - Identificação de conceitos que estão "vazando" para adaptadores
  - Sugestão de linguagem ubíqua para nomes das interfaces (Secondary Ports)
```

**Integração sem modificar specs:**
```
Uso correto (não altera specs):
  1. Rodar domain-analysis sobre o código/descrição do contexto
  2. Usar output para VALIDAR suas Secondary Ports existentes
     ou DESCOBRIR Ports que estão faltando
  3. O resultado alimenta o design das interfaces em Hexagon/Application/Ports/Secondary/
  4. Não modifica arquivos de spec — é input para decisões de design

Uso incorreto (evitar):
  ❌ Deixar a skill reescrever specs existentes automaticamente
  ❌ Usar output como verdade absoluta sem revisão de domínio
```

---

### SKILL: `coupling-analysis`

**Papel no workflow Ports & Adapters:**
A `coupling-analysis` é o **guardião arquitetural** — verifica se as fronteiras do hexágono estão sendo respeitadas e se Ports e Adapters estão no lugar correto. É a verificação automatizável das regras de dependência.

**Quando acionar:**
```
TRIGGER 1: Após implementar um novo Adapter (Primary ou Secondary)
TRIGGER 2: Em Pull Requests que tocam estrutura de projeto
TRIGGER 3: Revisão periódica do módulo inteiro

PERGUNTAS QUE A SKILL RESPONDE:
  "Existe algum tipo em Hexagon/ importando de Adapters/?"  → violação crítica
  "Existe coupling acidental entre Primary e Secondary Adapters?"  → violação
  "Os Secondary Adapters conhecem apenas as Secondary Ports?" → verificação
  "Existe algum tipo de Domain conhecendo Application?" → violação
  "Existem Ports sendo implementadas por múltiplos Adapters de forma inconsistente?" → sinal

INPUTS QUE VOCÊ FORNECE:
  - Diretório do Bounded Context
  - (Opcional) Regras de coupling explícitas no formato que a skill aceita

OUTPUTS ESPERADOS:
  - Mapa de dependências entre pacotes/namespaces
  - Violações das regras de dependência com localização exata (arquivo:linha)
  - Score de acoplamento por componente
  - Sugestão de refatoração para cada violação
```

**Integração sem modificar specs:**
```
Uso correto:
  1. Rodar coupling-analysis como etapa de CI/CD (gate de PR)
  2. Usar output para identificar violações de Ports & Adapters
  3. Corrigir nos arquivos de implementação — não nos arquivos de spec/guideline
  4. Configurar thresholds de acoplamento máximo por camada

Regras de coupling aceitas por este guideline (configure na skill):
  PROIBIDO: Hexagon.** → Adapters.**
  PROIBIDO: Hexagon.Domain.** → Hexagon.Application.**
  PROIBIDO: Adapters.Primary.** → Adapters.Secondary.**
  PERMITIDO: Adapters.Secondary.** → Hexagon.Domain.**
  PERMITIDO: Adapters.Secondary.** → Hexagon.Application.Ports.Secondary.**
  PERMITIDO: Adapters.Primary.** → Hexagon.Application.Ports.Primary.**
  PERMITIDO: Hexagon.Application.** → Hexagon.Domain.**
```

---

### SKILL: `technical-design-doc-creator`

**Papel no workflow Ports & Adapters:**
A `technical-design-doc-creator` é ativada na fase de **design de novos Ports e Adapters** — antes da implementação. Ela produz o TDD (Technical Design Document) que documenta decisões arquiteturais sobre:
- Quais Primary Ports serão criadas e por quê
- Quais Secondary Ports serão criadas e por quê
- Qual Secondary Adapter foi escolhido (e quais alternativas foram descartadas)
- Como a ACL será estruturada (quando houver)

**Quando acionar:**
```
TRIGGER 1: Antes de implementar uma nova integração externa (novo Secondary Adapter)
TRIGGER 2: Antes de adicionar um novo caso de uso significativo (nova Primary Port)
TRIGGER 3: Antes de refatorar fronteiras entre contextos
TRIGGER 4: Quando há decisão de escolha de tecnologia para um Adapter

NÃO ACIONAR PARA:
  ❌ Mudanças triviais em Adapters existentes (bug fix, ajuste de query)
  ❌ Novos Commands/Queries dentro de Port já existente
  ❌ Refatorações internas ao Hexagon sem mudança de Ports
```

**Seções relevantes do TDD para Ports & Adapters:**
```
O TDD gerado deve conter no mínimo (para contexto arquitetural):

1. CONTEXTO
   - Bounded Context afetado
   - Port(s) envolvida(s) (Primary ou Secondary)
   - Problema sendo resolvido

2. DECISÃO DE PORT
   - Nome da interface (Secondary Port ou Primary Port)
   - Localização: Domain ou Application?
   - Justificativa: por que essa abstração pertence aqui?
   - Contrato (métodos, parâmetros, retornos)

3. DECISÃO DE ADAPTER
   - Tecnologia escolhida e alternativas descartadas
   - Trade-offs explícitos (performance, complexidade, custo)
   - Se há ACL: como a tradução funciona

4. IMPACTO DE COUPLING
   - Quais outros componentes são afetados?
   - Resultado esperado do coupling-analysis após implementação

5. ESTRATÉGIA DE TESTE
   - Como testar a Port (in-memory adapter ou mock?)
   - Como testar o Adapter (integration test com testcontainer?)
```

**Integração sem modificar specs:**
```
Uso correto:
  1. Antes de implementar, acionar a skill com contexto do design
  2. Output = documento em /docs/architecture/decisions/ (ADR ou TDD)
  3. O documento é revisado e aprovado ANTES do código
  4. Specs existentes (guidelines, DDD, etc.) não são modificadas
  5. O TDD referência este guideline como base arquitetural

Não use para:
  ❌ Sobrescrever ou atualizar este arquivo de guidelines
  ❌ Documentar decisões retroativamente sem revisão
```

---

### SKILL: `gh-address-comments` (somente comentários de arquitetura/design)

**Papel no workflow Ports & Adapters:**
A `gh-address-comments` resolve comentários de revisão no GitHub. O escopo aqui é **estritamente restrito a comentários que referenciam arquitetura e design de Ports & Adapters** — sem tocar em specs, sem modificar guidelines, sem alterar regras de negócio.

**Filtro de comentários — O QUE a skill deve endereçar neste contexto:**
```
ENDEREÇAR (comentários de arquitetura/design permitidos):
  ✅ "Esse tipo está no lugar errado — deveria ser um Secondary Port, não um Adapter"
  ✅ "Esse Adapter está importando diretamente do Domain — viola a regra de dependência"
  ✅ "Esse Controller está chamando um Secondary Adapter diretamente — deveria usar Primary Port"
  ✅ "A nomenclatura não segue o padrão Ports & Adapters — renomear de XyzService para IXyz"
  ✅ "Falta ACL aqui — o tipo externo está vazando para o domínio"
  ✅ "Esse repositório está expondo IQueryable — viola a regra de Secondary Port"
  ✅ "O Command Handler está contendo regra de negócio — mover para o domínio"

NÃO ENDEREÇAR (fora do escopo ou risco de mudar specs):
  ❌ Comentários sobre estrutura de specs/guidelines
  ❌ Comentários sobre regras de negócio do domínio
  ❌ Comentários sobre testes de negócio (escopo de QA)
  ❌ Comentários sobre infraestrutura de deploy/CI
  ❌ Comentários ambíguos que poderiam afetar specs de domínio
```

**Configuração de uso seguro:**
```
Antes de rodar gh-address-comments em um PR:

PASSO 1 — Filtrar comentários relevantes:
  Identificar apenas comentários que contenham termos como:
    "port", "adapter", "hexagon", "dependency", "coupling",
    "layer", "domain leak", "import", "reference", "acl",
    "interface", "abstraction", "namespace", "project structure"

PASSO 2 — Verificar escopo da mudança sugerida:
  ✅ Mudança envolve: mover arquivo entre Adapters/ e Hexagon/
  ✅ Mudança envolve: renomear para seguir convenção de Port
  ✅ Mudança envolve: extrair interface (criar Port)
  ✅ Mudança envolve: remover import proibido
  ❌ Mudança envolve: alterar lógica de negócio
  ❌ Mudança envolve: modificar arquivo em Hexagon/Domain/ além de mover

PASSO 3 — Revisão humana obrigatória após a skill executar:
  Revisar diff antes de commitar
  Rodar coupling-analysis para confirmar que violações foram corrigidas
  Rodar testes de unidade (domain deve passar sem infra)
```

---

## SEÇÃO 11 — WORKFLOW INTEGRADO (DO DESIGN À IMPLEMENTAÇÃO)

```
Fluxo recomendado para novo feature/integração usando as skills:

FASE 1 — DESCOBERTA (antes de qualquer código)
  1. Rodar: domain-analysis
     → Identificar Secondary Ports necessárias
     → Validar linguagem ubíqua das interfaces
  
FASE 2 — DESIGN (antes de implementar)
  2. Rodar: technical-design-doc-creator
     → Documentar decisão de Port (Secondary ou Primary)
     → Documentar decisão de Adapter e trade-offs
     → Documentar impacto de coupling esperado
  
FASE 3 — IMPLEMENTAÇÃO (código)
  3. Implementar Primary Port(s) em Hexagon/Application/Ports/Primary/
  4. Implementar Secondary Port(s) em Hexagon/Domain/ ou Hexagon/Application/Ports/Secondary/
  5. Implementar Use Case Handler em Hexagon/Application/UseCases/
  6. Implementar Secondary Adapter(s) em Adapters/Secondary/
  7. Implementar Primary Adapter em Adapters/Primary/
  8. Registrar bindings em Composition/

FASE 4 — REVISÃO (PR)
  9. Rodar: coupling-analysis
     → Confirmar que nenhuma regra de dependência foi violada
  10. Em PR, usar: gh-address-comments (filtrado para arquitetura/design)
      → Endereçar apenas comentários de structure/coupling/naming
      → Não endereçar comentários de lógica de negócio/specs
```

---

## SEÇÃO 12 — TESTES NA ARQUITETURA DE PORTS & ADAPTERS

```
INSIGHT FUNDAMENTAL: Um teste é um Primary Adapter.
Testes provam que a Primary Port se comporta corretamente.

Tipos de teste por localização:

DENTRO DO HEXÁGONO:
  Domain Unit Tests:
    - Testam Entities, VOs, Aggregates diretamente
    - Zero mocks, zero DI — apenas new()
    - Provam invariantes do domínio

  Application Unit Tests (via Primary Port):
    - Testam Use Case Handlers via Primary Port interface
    - Secondary Ports são mockadas (in-memory adapters preferível a mocks)
    - Provam orquestração do caso de uso

FORA DO HEXÁGONO:
  Secondary Adapter Integration Tests:
    - Testam Adapters concretos contra tecnologia real (TestContainers)
    - Provam que o contrato da Secondary Port é satisfeito
    - Não testam regras de negócio

  Primary Adapter Integration Tests (E2E parcial):
    - Testam que o Primary Adapter traduz corretamente
    - WebApplicationFactory (.NET) com Secondary Adapters em memória
    - Provam que a "cola" entre o mundo externo e a Port funciona

REGRA DE OURO DE TESTES:
  Se o teste precisa de infraestrutura real para testar lógica de Domain → violação.
  Se o teste não consegue substituir o banco → Port mal definida.
  Se o teste testa lógica de negócio via HTTP → arquitetura vazando.
```

---

## CHECKLIST PORTS & ADAPTERS

```
PORTS (verificar por bounded context):
[ ] Existe pelo menos uma Primary Port por caso de uso de entrada?
[ ] Primary Ports estão em Hexagon/Application/Ports/Primary/?
[ ] Secondary Ports estão em Hexagon/Domain/ (necessidade de domínio)
    ou Hexagon/Application/Ports/Secondary/ (necessidade de orquestração)?
[ ] Todos os nomes de Port seguem o padrão I{NomeVerbo} ou I{NomeConceito}?
[ ] Nenhuma Port contém tipos de framework (HttpContext, DbSet, etc.)?

ADAPTERS (verificar por bounded context):
[ ] Todos os Primary Adapters ficam em Adapters/Primary/?
[ ] Todos os Secondary Adapters ficam em Adapters/Secondary/?
[ ] Cada Secondary Adapter implementa exatamente uma Secondary Port?
[ ] ACL está dentro do Secondary Adapter (não é camada separada)?
[ ] Nenhum Adapter fora de Composition/ faz new() de outro Adapter?

DEPENDÊNCIAS (rodar coupling-analysis para verificar):
[ ] Nenhum tipo em Hexagon/ importa de Adapters/?
[ ] Nenhum tipo em Domain/ importa de Application/?
[ ] Primary Adapters importam apenas Primary Ports?
[ ] Secondary Adapters importam apenas Secondary Ports e Domain types?

SKILLS INTEGRATION:
[ ] domain-analysis rodou antes de definir novas Secondary Ports?
[ ] technical-design-doc-creator gerou TDD para novos Ports/Adapters?
[ ] coupling-analysis rodou e passou sem violações?
[ ] gh-address-comments filtrado apenas para comentários de arquitetura/design?
```

---

## GLOSSÁRIO CANÔNICO (Terminologia de Cockburn)

| Termo | Definição Precisa |
|---|---|
| **Port** | Interface dentro do hexágono que define um contrato de comunicação |
| **Primary Port** | Interface que a aplicação EXPÕE — casos de uso acionáveis |
| **Secondary Port** | Interface que a aplicação REQUER — dependências externas abstraídas |
| **Adapter** | Implementação concreta fora do hexágono que respeita um contrato de Port |
| **Primary Adapter** | Adaptador que ACIONA a aplicação (Controller, CLI, Test, Consumer de trigger) |
| **Secondary Adapter** | Adaptador ACIONADO pela aplicação (Repository, EmailSender, ExternalAPIClient) |
| **Primary Actor** | Entidade do mundo real que usa a aplicação através de um Primary Adapter |
| **Secondary Actor** | Sistema externo que serve a aplicação através de um Secondary Adapter |
| **ACL** | Anti-Corruption Layer — Secondary Adapter com tradução de modelos |
| **Hexagon** | O limite que separa a aplicação do mundo externo (não uma forma geométrica real) |
| **Composition Root** | Único ponto que conhece todos os bindings Port → Adapter (DI container config) |

---

## SEÇÃO 13 — TXC SOBRE PORTS & ADAPTERS

> Para regras completas do padrão TXC (Primary Ports por BC, Transaction Map, anti-padrões), ver `references/txc-guidelines.md`.

### Posicionamento do Handler TXC na estrutura hexagonal

O **Handler TXC** vive **dentro do hexágono**, na **Application layer**, e implementa a **Primary Port** de Command do BoundedContext.

```
DENTRO DO HEXÁGONO
├── Domain/
│   ├── {Entidade}.cs           (Aggregate Root)
│   └── I{Entidade}Repository.cs ← Secondary Port (necessidade do domínio)
│
└── Application/
    ├── Ports/
    │   └── Primary/
    │       ├── I{Entidade}Handler.cs  ← Primary Port (Command) — 1 por BC
    │       └── I{Entidade}Query.cs    ← Primary Port (Query)  — 1 por BC
    ├── {Entidade}Transaction.cs       ← Parameter Object TXC (não é DTO)
    └── {Entidade}Handler.cs           ← Implementa I{Entidade}Handler
```

### Fluxo TXC dentro da estrutura hexagonal

```
[Primary Adapter: HTTP Controller]          ← FORA do hexágono
  │ cria Transaction, chama Primary Port
  ▼
[Primary Port: I{Entidade}Handler]          ← contrato DENTRO do hexágono
  ▼
[Handler: {Entidade}Handler]                ← implementação DENTRO do hexágono
  ├── tx.HydrateXxx(input)                 → Fase 1: popula Transaction
  ├── Aggregate.Create/Apply(...)          → Fase 2: chama domínio
  ├── tx.HydrateXxxCriado(aggregate)       → Fase 2: captura estado
  ├── IXxxRepository.SaveAsync(aggregate)  → Fase 3: via Secondary Port
  └── tx.FinalizeWith(aggregate)           → Fase 3: retorna PipelineResult
  ▼
[Secondary Adapter: {DB}{Entidade}Repository] ← FORA do hexágono
```

### Regra de agrupamento de Primary Ports em projetos TXC

Uma Primary Port de Command por BoundedContext — não uma por operação CRUD:

```
✅ I{Entidade}Handler  → agrupa: CreateAsync, CancelAsync, ApproveAsync (mesmo BC)
✅ I{Entidade}Query    → agrupa: GetByIdAsync, ListAllAsync (queries do BC)
❌ ICreate{Entidade}UseCase + ICancel{Entidade}UseCase + IList{Entidade}UseCase
```

---

## REFERÊNCIAS

- Alistair Cockburn — *Hexagonal Architecture* (2005, 2023) — alistair.cockburn.us/hexagonal-architecture
- Juan Manuel Garrido de Paz — *Hexagonal Me* — jmgarridopaz.github.io
- [github.com/tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) — Registry de skills
- [agent-skills.techleads.club](https://agent-skills.techleads.club) — Skills marketplace
