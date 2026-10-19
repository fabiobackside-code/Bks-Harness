# Checklist de revisão — Go

Complementa `checklist-revisao-critica.md`, que é escrito em termos de .NET. Aqui está o que só
aparece em Go, e o que aparece diferente.

Ordem deliberada: o que **corrompe** vem antes do que **incomoda**. Vazamento de goroutine e erro
engolido derrubam produção; nome de variável, não.

## 1. Erro

- [ ] Todo `error` é checado. `_` só com comentário dizendo por quê
- [ ] Ao propagar, `fmt.Errorf("contexto: %w", err)` — **sem `%w` o `errors.Is` do chamador para
      de funcionar**, e a regressão é silenciosa
- [ ] Discriminação por `errors.Is` / `errors.As`, nunca por comparação de string de mensagem
- [ ] Erro do driver ou da biblioteca não sobe além do adapter: `pgx.ErrNoRows` vira erro de
      domínio na borda
- [ ] Mensagem de erro útil para depurar e sem dado sensível — o erro sai em log e, às vezes, em
      resposta
- [ ] Nenhum `panic` por regra de negócio. `panic` só em invariante de programa violada
- [ ] Nenhum `Result[T]` genérico (ver `go-standards.md`, seção 2)

## 2. Concorrência

O bloco mais caro de revisar e o mais caro de errar. Defeito de concorrência não aparece em teste
funcional — aparece em produção, sob carga, uma vez por semana.

- [ ] **Toda goroutine tem caminho de término definido.** Sem quem a espere e sem cancelamento, é
      vazamento — e goroutine vazada é memória vazada
- [ ] Nenhum bloqueio eterno possível em `channel` ou `select` sem `default` nem `ctx.Done()`
- [ ] `context.Context` propagado por toda a call stack de I/O, como primeiro parâmetro
- [ ] Estado compartilhado protegido por `sync.Mutex` / `RWMutex`, ou trocado por canal
- [ ] `errgroup` com `SetLimit` quando há fan-out — sem limite, um lote grande abre conexão sem teto
- [ ] `defer` dentro de laço: acumula até o fim da **função**, não da iteração. Extraia o corpo
- [ ] Módulo com `go` anterior a 1.22 no `go.mod`: variável de laço capturada exige `x := x`
- [ ] **`go test -race ./...` rodou.** Não é opcional aqui

## 3. Interface e API pública

- [ ] Interface declarada no pacote **consumidor**, não no que a implementa
- [ ] "Aceite interfaces, retorne structs" — parâmetro é interface, retorno é tipo concreto
- [ ] Interface pequena, por comportamento. Quinze métodos é pacote mal recortado
- [ ] Nenhuma interface criada "para o caso de precisar" — surge da necessidade, não da previsão
- [ ] Nada exportado sem necessidade. O que pode ser minúsculo, é
- [ ] `any` / `interface{}` só em borda de serialização, nunca em contrato de domínio
- [ ] Genérico só onde interface não resolve — não por elegância

## 4. Estrutura

- [ ] Pacote por contexto de domínio, não por camada técnica
- [ ] Sem dependência circular entre pacotes
- [ ] Nome de pacote curto, minúsculo, sem underscore, e não repetido no identificador
      (`order.New`, não `order.NewOrder`)
- [ ] `init()` sem trabalho que possa falhar — inicialização que pode dar erro é função normal
      devolvendo `error`, chamada no composition root
- [ ] Nenhum estado global mutável
- [ ] Sem sombreamento de variável que engane a leitura, sobretudo de `err` em bloco aninhado
- [ ] Caminho feliz à esquerda: guard clause com retorno antecipado, não `if/else` aninhado

## 5. Getter e setter — onde a regra geral não vale

A prática comum em Go diz: campo exportado direto, sem getter/setter, salvo lógica a encapsular. É
o certo para struct de dados.

**A exceção é o TXC.** Ali o getter **é** o mecanismo de imutabilidade — campo não exportado mais
getter é o que Go oferece no lugar de `record` (`go-standards.md`, seção 3). Não é cerimônia
importada de C#; é a única forma de impedir mutação.

- [ ] Struct de dados comum: campo exportado, sem getter/setter
- [ ] TXC e value object com invariante: campo não exportado, construtor validador, getter, e
      **nenhum setter**
- [ ] Struct que se diz imutável e tem campo de slice ou map: copiado na entrada e no getter, ou
      documentado como não imutável

## 6. Testes

- [ ] Table-driven onde há mais de um caso
- [ ] Sem biblioteca de asserção — `if got != want { t.Fatalf(...) }`
- [ ] Dublê é struct local que satisfaz a interface, não mock gerado
- [ ] Caso de borda coberto: valor zero, slice vazio, `nil`, erro esperado
- [ ] `t.TempDir()` para arquivo; nada escrito fora dele
- [ ] `t.Parallel()` onde não há estado compartilhado
- [ ] Consumidor de mensageria: teste de que processar a mesma mensagem duas vezes produz um
      efeito só

## 7. Desempenho

Só depois de o resto estar certo. Otimização que precede medição é ruído.

- [ ] `append` em laço quente com capacidade pré-alocada: `make([]T, 0, n)`
- [ ] Sem N+1 no acesso a banco
- [ ] Sem concatenação de string em laço — `strings.Builder`
- [ ] Struct grande passado por ponteiro; struct pequeno, por valor
- [ ] Benchmark onde o desempenho é requisito declarado, não onde se supõe

## 8. Segurança

- [ ] Query parametrizada. Nenhuma concatenação de SQL com entrada externa
- [ ] Toda entrada externa validada na borda
- [ ] Nenhum segredo em log, em mensagem de erro ou em argumento de linha de comando
- [ ] Comparação de token, assinatura ou hash por tempo constante (`subtle.ConstantTimeCompare`)
- [ ] `ReadHeaderTimeout` em todo `http.Server`
- [ ] Autenticação por opt-out explícito, nunca por opt-in esquecido

## 9. O que a máquina revisa, o revisor não

Se um comentário de revisão se repete, ele virou tarefa de ferramenta. Tempo de revisor é caro
demais para posicionamento de chave.

| Ferramenta | Pega |
|---|---|
| `gofmt` | formatação — não há estilo alternativo em Go |
| `go vet ./...` | erro provável: `printf` malformado, tag de struct inválida |
| `go test -race ./...` | corrida de dados |
| `golangci-lint run` | erro não checado, sombreamento, complexidade, importação não usada |
| `gosec` | injeção, segredo em código, timeout ausente |

Estes cinco no CI. O que eles pegam não vira comentário de revisão.

## 10. Sobre o PR, não sobre o código

- [ ] PR pequeno e atômico. Um de 2000 linhas é aprovado sem revisão de verdade — e todo mundo sabe
- [ ] Descrição diz **qual problema resolve e por que esta abordagem**, não o que o diff já mostra
- [ ] O autor aponta onde quer segunda opinião

Ao revisar, pergunte a intenção antes de propor mudança. "Isso está confuso" não é revisão;
"renomear para `FetchUserByID` deixa o contrato explícito" é.

## Fontes

Os antipadrões das seções 1 a 4 seguem *100 Go Mistakes and How to Avoid Them* (Teiva Harsanyi) e o
Effective Go. O recorte de revisão e o bloco 10 vieram de material de revisão de código Go em
português; o que está aqui é o que sobreviveu ao filtro dos padrões BKS — o restante ou já estava
em `bks-premises.md`, ou contradizia o TXC e virou a seção 5.
