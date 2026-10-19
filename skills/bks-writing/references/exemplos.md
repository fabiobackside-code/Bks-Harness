# Exemplos de antes e depois

Casos genéricos, um por regra da skill. Servem para calibrar o tom antes de reescrever um documento.

<!-- bks-escrita: ignorar -->

## Restrição que parece arbitrária

Antes:

> **Sem cache** [ADR-012], nem do catálogo: uma leitura por requisição. Cachear faria o serviço
> executar contra uma linha que o DBA já desativou.

Depois:

> O serviço lê o catálogo de operações a cada requisição e não guarda cópia em memória. Com uma
> cópia, ele executaria uma operação que o DBA já desativou.
>
> > *Decisão: nenhuma biblioteca do produto mantém cache; guardar e invalidar dado é responsabilidade
> > de quem a consome (ADR-012).*

O leitor entende por que não há cache aqui e fica sabendo que não há em nenhuma outra biblioteca.
Não precisa abrir nada.

## O parágrafo já traz o argumento

Antes:

> A razão está na ADR-013: os dois módulos são autônomos, e o núcleo **não reexpõe** o de segurança.

Depois:

> O núcleo e o módulo de segurança são bibliotecas independentes, e o núcleo não expõe o outro por
> dentro.
>
> > *Decisão: os dois módulos são autônomos, cada um registrado pelo host (ADR-013).*

## Nota sem síntese

Antes:

> > *Decisão: ver ADR-021.*

A nota não diz nada a quem não abrir o ADR. A guarda aponta. Depois:

> > *Decisão: a fila é a única porta de entrada do processamento em lote; não há chamada síncrona
> > (ADR-021).*

## Abrir pela informação

| Antes | Depois |
|---|---|
| "Nesta seção será apresentado o funcionamento da sessão." | "A sessão guarda a conexão e a transação de banco de uma execução inteira, do início ao commit." |
| "O envelope é um conceito importante." | "O envelope é o formato único em que toda requisição entra e sai do serviço." |

## Título que afirma

| Antes | Depois |
|---|---|
| `## Sessão` | `## A sessão guarda a conexão da execução inteira` |
| `## Validações` | `## Três validações, em três lugares` |
| Slide "Portas" | Slide "O núcleo declara o que precisa; o host entrega" |

## Identificador demais

| Antes | Depois |
|---|---|
| "O `DebitExecutor` herda do `TransactionalExecutor<DebitEnvelope, DebitInput, DebitOutput>` e sobrescreve o `ApplyRuleAsync`, que devolve `Result<DebitInput>`." | "O executor do débito aplica a regra de negócio antes de executar e devolve o que a decisão vai avaliar. A regra fica no `ApplyRuleAsync` do `DebitExecutor`." |

## Comentário de código

| Antes | Depois |
|---|---|
| `/// Implementa a verificação do valor cifrado.` | `/// Verifica se o texto claro corresponde ao valor cifrado.` |
| `// Ver ARCHITECTURE.md §12 (ADR-031) antes de mudar.` | `// Não é record: o ToString() gerado exporia a chave.` |

## Treinamento

Antes, na nota do apresentador:

> "Conforme a ADR-007 e o CANONE-BANCO, a procedure não faz commit."

Depois:

> "A procedure não faz commit. Quem abre a transação é o serviço, e só ele sabe se a operação
> inteira deu certo."

<!-- /bks-escrita -->
