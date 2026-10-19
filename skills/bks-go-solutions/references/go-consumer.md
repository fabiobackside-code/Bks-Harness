# Message consumer em Go — Kafka / RabbitMQ

Prompt especializado do tipo `CONSUMER`. Pré-requisito: `go-standards.md`, na skill `bks-standards`.

## Escolha da biblioteca (VT-C1)

**Kafka:** `segmentio/kafka-go` — Go puro, sem cgo, compila estático e roda em imagem `scratch`.
`confluent-kafka-go` depende de librdkafka via cgo; escolha-o só quando precisar de recurso que
o outro não tem (transações exactly-once, por exemplo), sabendo que perde o build estático.

**RabbitMQ:** `rabbitmq/amqp091-go` — a continuação oficial do `streadway/amqp`, que está
arquivado. Não gere código novo contra `streadway`.

## O ponto que decide corretude: commit manual

Com `GroupID` configurado, `ReadMessage` **comita o offset automaticamente** antes de o
processamento terminar. Se o processo cair depois disso, a mensagem foi perdida — comitada sem ter
sido processada.

`FetchMessage` + `CommitMessages` separa as duas coisas e é o default BKS (VT-C3 = manual):

```go
func (c *Consumer) Start(ctx context.Context) error {
	for {
		msg, err := c.reader.FetchMessage(ctx)
		if err != nil {
			if errors.Is(err, context.Canceled) {
				return nil
			}
			return fmt.Errorf("fetching message: %w", err)
		}

		if err := c.handle(ctx, msg); err != nil {
			c.log.Error("handling message", "topic", msg.Topic, "offset", msg.Offset, "err", err)
			if err := c.toDeadLetter(ctx, msg, err); err != nil {
				return fmt.Errorf("dead-lettering: %w", err)
			}
		}

		if err := c.reader.CommitMessages(ctx, msg); err != nil {
			return fmt.Errorf("committing offset: %w", err)
		}
	}
}
```

Ordem: processa, dead-letter em caso de falha, **só então comita**. Isso dá entrega *at-least-once*
— a mensagem pode repetir, nunca sumir.

Comitar mesmo após falha é deliberado: a mensagem já está no dead letter, e não comitar faria o
consumer reprocessar a mesma mensagem envenenada para sempre. Falhar ao *gravar* no dead letter é
que interrompe — aí a mensagem não está em lugar nenhum e comitar a perderia.

## Idempotência não é opcional

*At-least-once* significa que o handler **vai** receber a mesma mensagem duas vezes. Não é caso de
borda: é rebalanceamento de partição, redeploy e retentativa, e acontece em produção toda semana.

Chave de idempotência derivada da mensagem (ID de negócio, não o offset), com `UNIQUE` no banco:

```go
func (h *OrderHandler) Handle(ctx context.Context, evt OrderEvent) error {
	err := h.store.Insert(ctx, evt)
	if errors.Is(err, order.ErrDuplicate) {
		h.log.Info("already processed", "eventId", evt.ID)
		return nil
	}
	return err
}
```

Duplicata é sucesso, não erro — o efeito desejado já está aplicado.

## Configuração do reader

```go
reader := kafka.NewReader(kafka.ReaderConfig{
	Brokers:     cfg.Brokers,
	GroupID:     cfg.GroupID,
	Topic:       cfg.Topic,
	MinBytes:    10e3,
	MaxBytes:    10e6,
	MaxWait:     500 * time.Millisecond,
	StartOffset: kafka.FirstOffset,
})
```

Sem `CommitInterval` — defini-lo religa o commit assíncrono e desfaz o controle manual.

`StartOffset` só vale para grupo sem offset gravado. `FirstOffset` processa o histórico ao subir
pela primeira vez; `LastOffset` ignora o passado. A escolha errada aqui reprocessa meses de tópico
num deploy inicial.

## Timeout por mensagem

```go
func (c *Consumer) handle(ctx context.Context, msg kafka.Message) error {
	msgCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()

	var evt OrderEvent
	if err := json.Unmarshal(msg.Value, &evt); err != nil {
		return fmt.Errorf("%w: %v", ErrMalformed, err)
	}

	txc, err := order.NewOrderContext(correlationFrom(msg.Headers), evt.TenantID)
	if err != nil {
		return err
	}
	return c.useCase.Execute(msgCtx, txc, evt.ToInput())
}
```

Mensagem malformada nunca vai render sucesso na retentativa — vai direto ao dead letter, sem
retry. Distinguir erro permanente (payload inválido) de transitório (banco fora) é o que evita
tanto o laço infinito quanto a perda silenciosa.

O consumer é adapter inbound: desserializa, monta o TXC, chama o use case. Sem regra de negócio.

## Dead letter (VT-C4)

Kafka não tem DLQ nativa — é um tópico `{origem}.dlq` para onde você produz, preservando o payload
original e acrescentando cabeçalhos com o erro, o timestamp e o offset de origem. Sem esse
contexto, a fila de erro é um cemitério que ninguém consegue reprocessar.

RabbitMQ tem o mecanismo no broker: `x-dead-letter-exchange` na declaração da fila, e `Nack` com
`requeue=false` encaminha. Prefira o nativo a reimplementá-lo.

## Shutdown

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
defer stop()

defer func() {
	if err := reader.Close(); err != nil {
		logger.Error("closing reader", "err", err)
	}
}()

if err := consumer.Start(ctx); err != nil {
	return err
}
```

`FetchMessage` respeita o cancelamento e retorna `context.Canceled` — término esperado. `Close`
faz o reader sair do grupo de consumo de forma limpa, evitando o rebalanceamento por timeout que
trava as partições por dezenas de segundos.

Prazo de shutdown maior que o timeout de mensagem: a mensagem em voo precisa terminar e comitar.

## Testes

Handler é função pura de `(ctx, evento) error` — teste direto, sem broker.

Para o laço, `testcontainers-go` com Kafka real. Mock de broker testa o mock, não o consumer:
rebalanceamento e commit são exatamente o que quebra em produção.

Um teste que não pode faltar: **processar a mesma mensagem duas vezes produz um efeito só.**

## Antes de fechar

`gofmt` · `go vet ./...` · `go test -race ./...` · `golangci-lint run` · README e ARCHITECTURE.
