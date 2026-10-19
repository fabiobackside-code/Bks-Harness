# Rubrica de manutenibilidade

Os eixos detalham as subcaracterísticas de manutenibilidade da ISO/IEC 25010 (modularidade, reusabilidade, analisabilidade, modificabilidade, testabilidade) para a persona definida em `persona-e-premissas.md`.

Nota de 1 a 5 por eixo. Âncoras definidas para 1, 3 e 5; 2 e 4 são intermediárias.

## 1. Eixos e âncoras

### A1. Nomes e linguagem do domínio (Analisabilidade)
- **1:** nomes genéricos (`Manager`, `Helper`, `Processor`, `Data`); domínio irreconhecível.
- **3:** maioria dos nomes de domínio; alguns genéricos na camada de aplicação.
- **5:** classes, métodos e tabelas usam os termos do negócio; o fluxo é entendido só pelos nomes.

### A2. Tamanho e complexidade (Analisabilidade)
- **1:** métodos com complexidade cognitiva > 25 ou com mais de 60 linhas, de forma recorrente.
- **3:** maioria dos métodos com complexidade cognitiva ≤ 15 e ≤ 30 linhas.
- **5:** métodos com ≤ 15 linhas, ≤ 4 pontos de decisão e ≤ 4 parâmetros.

Limites baseados em Visser et al. (SIG) e no limiar padrão de complexidade cognitiva do SonarQube.

### A3. Profundidade de indireção (Analisabilidade)
- **1:** mais de 7 saltos do ponto de entrada ao efeito final; camadas que só repassam chamadas.
- **3:** 5 a 7 saltos, cada camada com papel claro.
- **5:** até 4–5 saltos; cada camada agrega comportamento (módulos profundos).

### A4. Aderência ao repertório (Analisabilidade)
- **1:** construções fora do repertório espalhadas pelo código de negócio.
- **3:** poucas, isoladas, sem explicação.
- **5:** ausentes, ou isoladas em componente nomeado com o porquê documentado.

### A5. Fronteiras (Modularidade)
- **1:** domínio referencia infraestrutura; adapters contêm regra de negócio.
- **3:** fronteiras corretas com vazamentos pontuais.
- **5:** domínio puro; ports pequenos e coesos; regras de arquitetura verificadas por teste.

### A6. Localidade de mudança (Modificabilidade)
- **1:** cenários de mudança exigem alterar 8+ arquivos em camadas distantes.
- **3:** 4 a 7 arquivos, com caminho previsível.
- **5:** até 3 arquivos, ou alteração concentrada numa fatia.

### A7. Testabilidade (Testabilidade)
- **1:** sem testes, ou domínio só testável com banco/cofre reais.
- **3:** domínio testado; adapters sem teste de integração.
- **5:** testes legíveis como especificação; criar um teste novo leva minutos.

### A8. Consistência e tratamento de erros (Analisabilidade)
- **1:** cada fluxo trata erro de um jeito; exceções engolidas.
- **3:** padrão definido, com exceções.
- **5:** um padrão único de erro, log e resposta em toda a solução.

### A9. Operabilidade e observabilidade (Modificabilidade)
- **1:** sem traces; logs não estruturados; configuração espalhada.
- **3:** OpenTelemetry configurado, nomes inconsistentes.
- **5:** spans, métricas e logs com nomes padronizados e correlação ponta a ponta.

### A10. Documentação do porquê (Analisabilidade)
- **1:** sem README ou ADR; comentários repetem o código.
- **3:** README de execução; decisões implícitas.
- **5:** README, ADRs das decisões não óbvias e comentários de intenção onde o código surpreende.

### A11. Duplicação vs. abstração (Reusabilidade)
- **1:** regra de negócio duplicada, ou abstrações genéricas criadas para 1–2 usos.
- **3:** duplicação baixa; uma ou outra abstração prematura.
- **5:** regra de negócio única; abstração só onde há 3+ usos reais.

Atenção: código gerado por IA tende a aplicar DRY e Object Calisthenics além do ponto em que reduzem custo de manutenção. Penalize o excesso tanto quanto a falta.

### A12. Superfície pública e extensibilidade (Reusabilidade, Modificabilidade) — bibliotecas, SDKs, componentes e Web Services
- **1:** tipos internos expostos como `public`; interfaces grandes; extensão só por herança de classes concretas; contrato quebrado sem versão major.
- **3:** superfície razoável com alguns tipos públicos desnecessários; pontos de extensão sem implementação padrão ou exemplo.
- **5:** superfície mínima; interfaces pequenas e coesas; pontos de extensão explícitos com implementação padrão e exemplo; compatibilidade verificada por ferramenta; versionamento semântico.

## 2. Releitura dos eixos para bibliotecas, SDKs e componentes

Componentes são organizados por superfície pública, não por casos de uso. Avalie sob a ótica de quem **evolui** e de quem **consome/estende**.

- **A3:** conte os saltos do ponto de entrada público até a implementação efetiva.
- **A5:** a fronteira principal é `public` vs. `internal`; tipos internos não vazam por parâmetros, retornos ou exceções públicas.
- **A6:** cenários são "estender sem modificar" (Aberto/Fechado) e "mudar o interno sem mudar o público".
- **A7:** inclui o consumidor conseguir testar o próprio código com fakes das interfaces públicas.
- **A10:** inclui XML docs nos tipos públicos, README com exemplo de uso e de extensão, CHANGELOG.

## 2a. Releitura dos eixos para Web Services

O contrato publicado (WSDL ou equivalente) é a superfície pública. A12 mede só o contrato: tamanho,
versionamento e compatibilidade. Os demais eixos seguem a leitura de API.

## 2b. Releitura dos eixos para Scripts SQL

A unidade é o objeto de banco e quem o chama (`stacks/sql.md`).

- **A3:** conte os saltos de procedure para procedure e de view para view.
- **A5:** a fronteira é entre regra de negócio e armazenamento; regra no banco sem ADR conta como vazamento.
- **A7:** testes de procedure, ou teste de integração da aplicação que consome o objeto.
- **A9:** idempotência do deploy, ordem de execução e rollback.

## 3. Pesos por tipo de solução

| Eixo | API | Worker | Biblioteca, SDK ou componente | Web Service | Scripts SQL |
| --- | --- | --- | --- | --- | --- |
| A1. Nomes e linguagem do domínio | 10 | 10 | 8 | 10 | 10 |
| A2. Tamanho e complexidade | 10 | 10 | 8 | 10 | 14 |
| A3. Profundidade de indireção | 12 | 10 | 8 | 10 | 8 |
| A4. Aderência ao repertório | 12 | 12 | 10 | 12 | 10 |
| A5. Fronteiras | 10 | 8 | 6 | 10 | 6 |
| A6. Localidade de mudança | 12 | 10 | 8 | 10 | 10 |
| A7. Testabilidade | 10 | 10 | 10 | 8 | 8 |
| A8. Consistência e erros | 6 | 10 | 6 | 8 | 12 |
| A9. Operabilidade e observabilidade | 6 | 10 | 4 | 6 | 8 |
| A10. Documentação do porquê | 6 | 5 | 10 | 8 | 8 |
| A11. Duplicação vs. abstração | 6 | 5 | 4 | 4 | 6 |
| A12. Superfície pública e extensibilidade | 0 | 0 | 18 | 4 | 0 |
| **Total** | **100** | **100** | **100** | **100** | **100** |

Se um eixo for "não avaliado", redistribua o peso dele proporcionalmente entre os eixos avaliados e informe isso.

## 4. Cálculo

**Passo 1 — nota base**

```
Base = Σ peso_i × (nota_i − 1) / 4
```

**Passo 2 — premissas**

- Premissa crítica violada (P01, P03, P04, P05; em componentes também P15): nota final limitada a **40**.
- Demais premissas violadas: **−5** cada.
- "Não avaliado" e "Não se aplica" não penalizam.

**Passo 3 — classificação**

| Faixa | Classificação | Leitura |
| --- | --- | --- |
| 85–100 | Excelente | Um dev do time assume a manutenção sem apoio |
| 70–84 | Bom | Assume com revisão pontual de um sênior |
| 50–69 | Atenção | Precisa de pareamento nas primeiras mudanças |
| 0–49 | Crítico | Manutenção depende de quem escreveu, ou de refatoração antes da entrega |

**Passo 4 — confiança**

- **Alta:** ≥ 60% dos eixos com nota medida e todas as premissas críticas avaliadas.
- **Média:** 30–59% medidos, ou alguma premissa crítica não avaliada.
- **Baixa:** < 30% medidos, ou fatia analisada parcial.

## 5. Ganho por ação

Cada nível em um eixo vale `peso ÷ 4` pontos. Use isso para estimar o ganho de cada ação do plano de melhoria.
