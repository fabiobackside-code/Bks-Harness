# IDENTIFICANDO-CONTEXTOS-DELIMITADOS-GUIDELINES

> **Versão:** 1.0  
> **Escopo:** Estratégico — como descobrir, nomear e mapear Bounded Contexts  
> **Paradigma:** Agnóstico de linguagem / framework / stack  
> **Temperatura de decisão:** 0.02 — regras prescritivas, processo estruturado

---

## PROPÓSITO DESTE ARQUIVO

Este guideline instrui agentes de IA e desenvolvedores sobre como identificar Contextos Delimitados (Bounded Contexts) no nível estratégico do DDD. É o ponto de partida antes de qualquer decisão tática ou arquitetural. Sem contextos bem definidos, todo o resto é construção sobre areia.

---

## PRINCÍPIO FUNDAMENTAL

> **Um Bounded Context é uma fronteira explícita dentro da qual um modelo de domínio específico é válido e consistente. Fora dessa fronteira, o mesmo termo pode ter significado diferente.**

O objetivo NÃO é descobrir "microsserviços" ou "módulos". O objetivo é descobrir onde a **linguagem ubíqua muda** — porque onde a linguagem muda, o modelo muda, e o contexto muda.

---

## FASE 1 — EVENT STORMING (Descoberta do Domínio)

### O Que É
Event Storming é um workshop colaborativo de modelagem onde especialistas de negócio e desenvolvedores mapeiam o fluxo de domínio usando post-its. É o método mais eficaz para descobrir Bounded Contexts.

### Processo Estruturado

#### Passo 1 — Domain Events (post-its laranja)
```
Regra: Nomeie todos os fatos relevantes para o negócio.
Formato: Passado + verbo ("PedidoConfirmado", "PagamentoRecusado")
Quem participa: TODOS — devs, PO, especialistas de domínio

Perguntas guia:
  "O que acontece no sistema que é importante para o negócio?"
  "O que causa uma notificação, email, ou ação de alguém?"
  "Quais fatos precisamos rastrear?"

Output: Timeline de eventos em ordem cronológica no espaço
```

#### Passo 2 — Commands (post-its azuis)
```
Regra: Quem ou o que CAUSOU cada evento?
Formato: Imperativo ("ConfirmarPedido", "ProcessarPagamento")

Perguntas guia:
  "Quem iniciou essa ação?"
  "É um usuário, sistema, ou evento anterior?"
  "Existe uma intenção explícita aqui?"
```

#### Passo 3 — Aggregates (post-its amarelos)
```
Regra: Agrupe Commands + Events em torno de entidades que os processam

Perguntas guia:
  "Qual entidade de negócio executa esse comando?"
  "Qual entidade muda de estado quando esse evento ocorre?"
```

#### Passo 4 — Hotspots (post-its vermelhos)
```
Regra: Marque pontos de conflito, dúvida ou ambiguidade
Exemplos:
  "O termo 'Cliente' aqui é o mesmo de lá?"
  "Quem é dono desse dado?"
  "Esse processo não está claro para ninguém"
```

#### Passo 5 — Identificar Bounded Contexts
```
Observe padrões de:
  - Termos que mudam de significado
  - Grupos de eventos/aggregates coesos
  - Fronteiras de responsabilidade organizacional
  - Áreas onde "hotspots" se concentram
  - Mudanças de linguagem ubíqua
```

---

## FASE 2 — CRITÉRIOS DE IDENTIFICAÇÃO DE CONTEXTO

### Critério 1 — Mudança de Linguagem (Principal)

```
Sinal: O mesmo termo tem significados diferentes em partes distintas do sistema.

Exemplo — "Produto":
  No contexto de Catálogo:
    Produto = {nome, descrição, fotos, categorias, atributos técnicos}
  
  No contexto de Pedido:
    Produto = {productId, preço-no-momento-da-compra, quantidade}
  
  No contexto de Estoque:
    Produto = {sku, quantidade-disponível, localização-física}

→ Três contextos diferentes, três modelos diferentes para "Produto". ✅
```

### Critério 2 — Coesão Funcional

```
Sinal: Um grupo de funcionalidades que "andam juntas" naturalmente.

Perguntas:
  "Se eu precisar mudar X, quais outras coisas mudam junto?"
  "Quem tem expertise para validar esse comportamento?"
  "Esse conjunto de regras forma uma área de conhecimento coesa?"

Cuidado: Alta coesão ≠ único contexto obrigatório. Avalie também o critério de linguagem.
```

### Critério 3 — Fronteiras Organizacionais (Conway's Law)

```
Sinal: Times diferentes cuidam de áreas diferentes → provável contexto diferente.

Lei de Conway: "Organizações que projetam sistemas produzem designs que
               espelham a estrutura de comunicação da organização."

Aplicação:
  - Time de Vendas cuida de: Oportunidades, Propostas, Contratos → Contexto: Vendas
  - Time de Logística cuida de: Entregas, Rotas, Transportadoras → Contexto: Logística
  - Time Financeiro cuida de: Faturamento, Cobranças, Conciliação → Contexto: Financeiro

Atenção: Use como SINAL, não como regra absoluta. Times mal organizados podem produzir
         contextos mal definidos.
```

### Critério 4 — Frequência de Mudança (Change Rate)

```
Sinal: Partes que mudam por razões diferentes são candidatas a contextos diferentes.

Exemplo:
  Catálogo de Produtos (muda quando marketing atualiza) ≠
  Precificação (muda quando área comercial redefine políticas) ≠
  Inventário (muda quando operações registra movimento físico)

→ Três razões diferentes de mudança = três contextos candidatos.
```

### Critério 5 — Consistência vs. Consistência Eventual

```
Sinal: Dados que PRECISAM ser consistentes ao mesmo tempo → mesmo contexto.
       Dados que podem ser consistentes EVENTUALMENTE → contextos diferentes.

Exemplo:
  "Pedido" e "ItemPedido" precisam ser consistentes → mesmo contexto (Pedido)
  "Pedido confirmado" e "Estoque reservado" podem ter delay → contextos diferentes
                                                               comunicando via evento
```

---

## FASE 3 — NOMEAÇÃO DE CONTEXTOS

### Regras de Nomeação

```
Regra 1: Use substantivos do domínio de negócio, não técnicos.
  ❌ "ServiçoDePedidos", "MóduloDeClientes", "BackendDeEstoque"
  ✅ "Vendas", "Catálogo", "Estoque", "Faturamento", "Identidade"

Regra 2: O nome deve fazer sentido para especialistas de negócio.
  Se um especialista de domínio não reconhece o nome → renomeie.

Regra 3: Use a linguagem ubíqua do próprio contexto para nomeá-lo.
  "Qual é o conceito central deste conjunto de regras?"
  → O nome desse conceito central muitas vezes é o nome do contexto.

Regra 4: Prefira nomes curtos e diretos (1-2 palavras).
  ❌ "GerenciamentoDeIdentidadeEAcessoDeUsuários"
  ✅ "Identidade" ou "IAM"
```

---

## FASE 4 — CONTEXT MAP (Mapa de Contextos)

### O Que É
O Context Map documenta como os Bounded Contexts se relacionam e se comunicam. É essencial para entender dependências e definir estratégias de integração.

### Tipos de Relacionamento

#### 1. Shared Kernel (Núcleo Compartilhado)
```
Definição: Dois contextos compartilham uma parte do modelo explicitamente.
Quando usar: Raramente — apenas quando a duplicação seria prejudicial.
Custo: Alto — mudanças no kernel afetam ambos os times.
Sinal de alerta: Se o kernel cresce, provavelmente é um contexto próprio.

Representação: [ContextoA] ←—Shared Kernel—→ [ContextoB]
```

#### 2. Customer/Supplier (Cliente/Fornecedor)
```
Definição: Um contexto fornece dados/serviços para outro.
           O fornecedor deve negociar mudanças com o cliente.
Quando usar: Quando há dependência clara mas com negociação possível.

Representação: [Fornecedor] ——upstream——→ [Cliente] (downstream)
```

#### 3. Conformist (Conformista)
```
Definição: O contexto downstream aceita o modelo do upstream sem questionamento.
Quando usar: Quando o upstream é um sistema externo sem API negociável.
Exemplo: Integração com API da Receita Federal, gateway de pagamento.
```

#### 4. Anti-Corruption Layer — ACL
```
Definição: Camada de tradução que protege o domínio interno do modelo externo.
Quando usar: SEMPRE que integrar com sistema legado ou sistema externo com modelo diferente.
Benefício: O domínio interno permanece puro; a tradução fica isolada.

Estrutura:
  [Sistema Externo] → [ACL: Tradutores/Adaptadores] → [Domínio Interno]
  
Implementação:
  - Interface definida no domínio (porta)
  - Adaptador na infra que chama o externo e traduz para o modelo interno
  - Nenhum conceito externo "vaza" para o domínio
```

#### 5. Open Host Service (OHS) + Published Language
```
Definição: Contexto expõe API bem definida e documentada para outros contextos.
Quando usar: Quando muitos contextos consomem o mesmo fornecedor.
Exemplo: Contexto de Identidade/Auth expõe OHS para todos os outros contextos.
```

#### 6. Separate Ways
```
Definição: Contextos completamente independentes, sem integração.
Quando usar: Quando integrar custa mais do que duplicar.
```

### Template de Context Map

```
SISTEMA: [Nome do Sistema]
DATA: [Data de criação/atualização]

CONTEXTOS:
  [Nome]    | Responsabilidade principal
  --------- | ---------------------------
  Vendas    | Oportunidades, Propostas, Pedidos de venda
  Estoque   | Reservas, Movimentações, Inventário
  Catálogo  | Produtos, Categorias, Preços de tabela
  Identidade| Usuários, Autenticação, Permissões
  Financeiro| Faturamento, Recebimentos, Conciliação

RELACIONAMENTOS:
  Catálogo ——[OHS]——→ Vendas (fornece dados de produto)
  Vendas ——[Events]——→ Estoque (PedidoConfirmado → reservar itens)
  Vendas ——[Events]——→ Financeiro (PedidoConfirmado → gerar fatura)
  Identidade ——[OHS]——→ TODOS (autenticação centralizada)
  GatewayPagamento ——[ACL]——→ Financeiro (sistema externo isolado)
```

---

## FASE 5 — COMUNICAÇÃO ENTRE CONTEXTOS

### Regras de Integração

```
Regra 1: Contextos NÃO compartilham banco de dados.
  ❌ ContextoA e ContextoB lendo/escrevendo na mesma tabela diretamente.
  ✅ Cada contexto tem seu próprio schema/banco. Comunicação via API ou eventos.

Regra 2: Contextos NÃO chamam repositórios uns dos outros.
  ❌ PedidoService injetando ClienteRepository do contexto de Clientes.
  ✅ PedidoService chama API do contexto de Clientes ou usa dado já incorporado.

Regra 3: Dados entre contextos são copiados, não compartilhados.
  Cada contexto mantém o que PRECISA do outro em seu próprio modelo.
  Exemplo: Contexto de Pedidos guarda {clienteId, nomeCliente, emailCliente}
           — uma cópia no momento do pedido, não uma FK para tabela de Clientes.

Regra 4: Comunicação síncrona vs. assíncrona.
  Síncrona (REST/gRPC): Use quando a resposta é necessária AGORA para continuar.
  Assíncrona (eventos): Use quando a ação pode ser processada eventualmente.
  
  Prefira assíncrona para:
    - Notificações
    - Atualização de projeções/relatórios
    - Processos que podem ser retentados
  
  Use síncrona para:
    - Validações bloqueantes
    - Dados necessários para completar a operação atual
```

---

## ANTI-PADRÕES COMUNS DE CONTEXTOS

### 1. Mega-Contexto (God Context)
```
Sintoma: Um contexto que contém "tudo" relacionado a uma entidade central.
  ❌ Contexto "Cliente" que contém pedidos, histórico, financeiro, suporte...
  ✅ Contexto "Identidade" (dados cadastrais) + "Vendas" (pedidos do cliente) + etc.
```

### 2. Contexto por Camada Técnica
```
Sintoma: Contextos nomeados por responsabilidade técnica, não de negócio.
  ❌ "ContextoDeAPI", "ContextoDeBanco", "ContextoDeWorkers"
  ✅ "Catálogo", "Pedidos", "Notificações"
```

### 3. Contexto Anêmico
```
Sintoma: Contexto com apenas CRUDs sem regras de negócio reais.
Ação: Verificar se realmente é um contexto ou apenas uma tabela de suporte.
      CRUD puro pode ser um "Generic Subdomain" — não precisa de DDD tático completo.
```

### 4. Contexto Acoplado Implicitamente
```
Sintoma: Contextos que "funcionam" mas dependem do banco um do outro.
  ❌ JOIN entre tabelas de contextos diferentes no mesmo query
  ✅ Cada contexto tem sua visão própria dos dados que precisa
```

---

## CLASSIFICAÇÃO DE SUBDOMÍNIOS

```
Core Domain (Domínio Principal):
  - Diferenciador competitivo do negócio
  - Invista aqui: DDD completo, melhor time, maior atenção
  - Exemplo: Algoritmo de recomendação (e-commerce), Motor de precificação (fintech)

Supporting Subdomain (Subdomínio de Suporte):
  - Necessário mas não diferenciador
  - DDD moderado ou CRUD bem estruturado
  - Exemplo: Gestão de fornecedores, Cadastro de produtos

Generic Subdomain (Subdomínio Genérico):
  - Commodity — compre ou use solução de mercado
  - Não invista DDD aqui
  - Exemplo: Autenticação (use Keycloak/Auth0), Email (use SendGrid)

Decisão de build vs buy:
  Core Domain → BUILD (sempre)
  Supporting → BUILD com cuidado ou adapte solução
  Generic → BUY ou use open-source
```

---

## CHECKLIST DE CONTEXTOS DELIMITADOS

```
[ ] Event Storming realizado com especialistas de negócio?
[ ] Todos os Domain Events mapeados na timeline?
[ ] Linguagem ubíqua documentada POR CONTEXTO?
[ ] Fronteiras identificadas onde a linguagem muda?
[ ] Context Map criado e revisado por todos?
[ ] Tipos de relacionamento entre contextos definidos?
[ ] ACL criada para cada integração com sistema externo?
[ ] Subdomínios classificados (Core/Supporting/Generic)?
[ ] Estratégia build vs buy definida para cada subdomínio?
[ ] Cada contexto tem seu próprio schema/banco?
[ ] Comunicação entre contextos via API ou eventos (nunca DB compartilhado)?
[ ] Nomes de contextos validados com especialistas de negócio?
```

---

## GLOSSÁRIO DE CONTEXTOS ESTRATÉGICOS

| Termo | Definição |
|---|---|
| Bounded Context | Fronteira explícita onde um modelo é válido |
| Ubiquitous Language | Linguagem comum do contexto, usada por todos |
| Context Map | Diagrama de relacionamentos entre contextos |
| Core Domain | Diferenciador competitivo principal |
| Supporting Subdomain | Necessário mas não diferenciador |
| Generic Subdomain | Commodity — compre ou reutilize |
| ACL | Camada que protege o domínio de modelos externos |
| OHS | API pública e estável de um contexto |
| Event Storming | Workshop de descoberta de domínio |

---

## REFERÊNCIAS CONCEPTUAIS

- Eric Evans — *Domain-Driven Design* (2003) — Capítulos 14-17 (Strategic Design)
- Vaughn Vernon — *Implementing Domain-Driven Design* (2013) — Parte II
- Vaughn Vernon — *Domain-Driven Design Distilled* (2016)
- Alberto Brandolini — *Introducing EventStorming* (2021)
- Nick Tune & Scott Millett — *Patterns, Principles and Practices of DDD* (2015)
