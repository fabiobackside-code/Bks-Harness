# Emitir em Mermaid

## Classes — declare uma vez, no topo

```
classDef backend    fill:#336698,stroke:#1F4266,color:#FFFFFF,stroke-width:2px
classDef storage    fill:#4A7C63,stroke:#2E5140,color:#FFFFFF,stroke-width:2px
classDef broker     fill:#B5713C,stroke:#8A5228,color:#FFFFFF,stroke-width:2px
classDef acesso     fill:#9E4B4B,stroke:#733535,color:#FFFFFF,stroke-width:2px
classDef componente fill:#B39038,stroke:#8A6E26,color:#1A1A1A,stroke-width:2px
classDef externo    fill:#6B7280,stroke:#4B5563,color:#FFFFFF,stroke-width:2px
classDef destaque   fill:#98CBFF,stroke:#336698,color:#1A1A1A,stroke-width:3px
```

Aplique com `class no1,no2 backend`, ou direto no no com `:::backend`.

## Arquitetura

```mermaid
flowchart TB
    classDef backend fill:#336698,stroke:#1F4266,color:#FFFFFF,stroke-width:2px
    classDef storage fill:#4A7C63,stroke:#2E5140,color:#FFFFFF,stroke-width:2px
    classDef broker  fill:#B5713C,stroke:#8A5228,color:#FFFFFF,stroke-width:2px
    classDef acesso  fill:#9E4B4B,stroke:#733535,color:#FFFFFF,stroke-width:2px

    CLIENTE[Cliente web]:::acesso
    GW[api-gateway]:::acesso

    subgraph interna [Rede interna]
        ORDERS[orders-api]:::backend
        BILLING[billing-worker]:::backend
        DB[(orders-db)]:::storage
        FILA[[pedido.criado]]:::broker
    end

    CLIENTE -->|HTTPS| GW
    GW -->|POST /orders| ORDERS
    ORDERS -->|SELECT INSERT| DB
    ORDERS -.->|pedido.criado| FILA
    FILA -.-> BILLING
```

Forma do no carrega tipo: cilindro para banco, subrotina para fila, retangulo para serviço.

## Sequencia

```mermaid
sequenceDiagram
    autonumber
    participant C as Cliente
    participant A as orders-api
    participant D as orders-db
    participant F as pedido.criado

    C->>A: POST /orders
    A->>D: INSERT pedido
    D-->>A: id
    A--)F: pedido.criado
    A-->>C: 201 Created

    Note over A,F: publicação assincrona — o cliente não espera
```

Setas: `->>` sincrono, `--)` assincrono, `-->>` retorno. Use `autonumber` para poder referenciar
os passos no texto.

## Ciclo de vida

```mermaid
stateDiagram-v2
    [*] --> Criado
    Criado --> Confirmado: pagamento aprovado
    Criado --> Cancelado: timeout 30min
    Confirmado --> Enviado: despacho
    Enviado --> Entregue: confirmação
    Enviado --> Extraviado: sem rastreio 15d
    Extraviado --> Enviado: reenvio
    Entregue --> [*]
    Cancelado --> [*]
```

Inclua o caminho de erro: timeout, extravio, reenvio. São os que causam incidente, e os que quem
implementa esquece.

## Fluxo de dados

```mermaid
flowchart LR
    classDef storage fill:#4A7C63,stroke:#2E5140,color:#FFFFFF
    classDef backend fill:#336698,stroke:#1F4266,color:#FFFFFF

    ORIGEM[(sistema de origem)]:::storage
    ETL[pipeline-cargas]:::backend
    LAKE[(data lake)]:::storage

    subgraph pii [Fronteira de dado pessoal]
        ANON[anonimizador]:::backend
    end

    ORIGEM -->|CPF, nome, endereco| ANON
    ANON -->|hash, faixa etaria| ETL
    ETL --> LAKE
```

Rotule a aresta com **o que** trafega, não com o verbo. Marque a fronteira de dado sensivel com
`subgraph` — e o que torna o diagrama util numa revisão de conformidade.

## Limites

Sem logo de empresa — use rótulo textual. Layout automático: para posicionamento controlado, o
renderer e `archify`.

Direção: `TB` para hierarquia e camada, `LR` para fluxo e pipeline.
