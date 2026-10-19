---
name: bks-maintainability-review
description: Avalia a MANUTENIBILIDADE das aplicações de um projeto (APIs, Workers, Web Services, bibliotecas, SDKs, componentes e scripts SQL) do ponto de vista de um desenvolvedor pleno, gera nota de 0 a 100 e parecer em HTML com evidências, referências e plano de melhoria, e gera/versiona o documento de FUNDAMENTAÇÃO do projeto (literatura, conceitos, princípios, padrões, arquitetura e decisões técnicas que sustentaram a construção). Critérios por stack em stacks/; hoje .NET e SQL. Use SEMPRE que o usuário pedir para avaliar, analisar, auditar ou dar parecer/nota sobre manutenibilidade, dívida técnica, complexidade ou qualidade arquitetural; e também quando pedir a fundamentação, base teórica, literatura, conceitos ou padrões usados num projeto. Trigger em: manutenibilidade, manutenabilidade, nota do código, parecer técnico, dívida técnica, comparar versões, fundamentação, referências do projeto, que padrões foram usados, base teórica, literatura do projeto, /bkhar:maintainability.
---

# BKS Maintainability Review

A skill tem dois modos:

| Modo | Produz | Escopo | Saída |
| --- | --- | --- | --- |
| **Análise** | Parecer de manutenibilidade com nota | Por aplicação | `<raiz-do-projeto>/outputs/maintainability/<app>_<tipo>_<AAAA-MM-DD>.html` |
| **Fundamentação** | Documento de estudo com literatura, conceitos, padrões e decisões | Projeto inteiro | `<raiz-do-projeto>/outputs/references/<projeto>_fundamentacao_v<N>_<AAAA-MM-DD>.html` + catálogo JSON |

A raiz do projeto é a pasta com `STATUS.md` e `app/`. As aplicações moram em `app/`; a saída nunca
vai para dentro delas.

**Regra de acionamento:**

- Pedido de análise de manutenibilidade, ou o comando `/bkhar:maintainability` → modo Análise e,
  **ao final, sempre** o modo Fundamentação (que só gera nova versão se houver alteração).
- Pedido de fundamentação, base teórica, conceitos ou padrões usados → somente o modo
  Fundamentação.

---

## Modo Análise

Você vai produzir um **parecer de manutenibilidade** para uma ou mais aplicações. A pergunta que o
parecer responde é:

> Quanto custa para um desenvolvedor pleno do time **entender, alterar e testar** este código com
> segurança?

Não avalie qualidade em abstrato. Código sofisticado e correto pode ter nota baixa se exigir
conhecimento acima do repertório do mantenedor. Isso é especialmente comum em código gerado por
IA, e é exatamente o que esta análise precisa revelar.

## Arquivos de referência

| Arquivo | Quando ler |
| --- | --- |
| `references/persona-e-premissas.md` | Sempre, no início. Persona pleno, calibração pelo vault, premissas P01–P18 |
| `references/rubrica.md` | Sempre, antes de pontuar. Eixos A1–A12, âncoras, pesos por tipo e cálculo |
| `references/criterios-comuns.md` | Sempre. Critérios que valem para qualquer stack |
| `references/criterios-condicionais.md` | Só se o código mostrar cofre de credenciais ou manifests de OpenShift/Kubernetes |
| `stacks/<linguagem>.md` | Sempre, para cada stack presente: detecção, repertório e critérios da linguagem |
| `references/referencias.md` | Ao citar o princípio de cada achado |
| `assets/template-parecer.html` | Ao escrever o relatório final (HTML) |
| `references/fundamentacao.md` | No modo Fundamentação: escopo, versionamento, rigor e estrutura do documento |
| `references/catalogo-conceitos.md` | No modo Fundamentação: referências canônicas por conceito |
| `assets/template-fundamentacao.html` | Ao escrever o documento de fundamentação |
| `assets/catalogo-fundamentacao.exemplo.json` | Formato do catálogo que controla as versões da fundamentação |

Stacks com critérios hoje: `skills/bks-maintainability-review/stacks/dotnet.md` e
`skills/bks-maintainability-review/stacks/sql.md`. Uma stack nova entra como arquivo novo em
`stacks/`, com as seções **Detecção**, **Repertório da persona nesta stack** e **Critérios**; o
fluxo abaixo não muda.

Premissas do projeto (`CLAUDE.md`, `brain/engineering/`, `decisions/`) **complementam** as padrão.
Em conflito, prevalece a do projeto.

## Fluxo

### Passo 1 — Inventariar as aplicações e o tipo de cada uma

Percorra `app/` aplicando a seção **Detecção** de cada arquivo em `stacks/`. Cada aplicação recebe
nome, stack, tipo e raiz. O tipo muda a unidade de análise e os pesos.

| Tipo | Unidade de análise |
| --- | --- |
| API | Fatia vertical de caso de uso: endpoint → use case → domínio → port → adapter → SQL |
| Worker | Ciclo: obter trabalho → processar item → persistir/publicar |
| Web Service | Operação do contrato publicado → implementação → domínio → adapter |
| Biblioteca, SDK ou componente | Superfície pública: tipos públicos, interfaces, opções, pontos de extensão |
| Scripts SQL | Objeto de banco e quem o chama; para deploy, o conjunto que leva o banco de uma versão à seguinte |

Componentes **não** são organizados por casos de uso, e sim por interfaces públicas que podem ser
consumidas e estendidas. Avalie-os sob a ótica de **dois mantenedores**: quem evolui o componente e
quem o consome ou estende.

Uma aplicação pode conter mais de um tipo (ex.: API + biblioteca interna). Nesse caso, avalie cada
parte com seu tipo e consolide no fim.

**Pare e pergunte** quando:

- o tipo de uma aplicação não puder ser determinado;
- a stack não tiver arquivo em `stacks/`. Ofereça duas saídas: pular a aplicação, ou avaliá-la só
  com a rubrica e os critérios comuns, com confiança **Baixa** declarada. Nunca invente critério
  de stack;
- não estiver claro o que é uma aplicação (código solto, `.sql` espalhado em várias pastas).

### Passo 2 — Montar o contexto

Antes de pontuar, colete:

1. **Mapa da aplicação**: árvore de pastas até 3 níveis, arquivos de projeto e referências entre
   eles.
2. **Decisões registradas**: `decisions/`, `specs/`, `brain/engineering/`, README, `CLAUDE.md`.
   Escolhas justificadas ali **não** são penalizadas; podem ser questionadas em seção separada.
3. **Calibração da persona**: se `BKS_VAULT` estiver definido, siga a seção "Calibração pelo
   vault" de `references/persona-e-premissas.md`. Sem vault, registre isso no cabeçalho.
4. **Métricas medidas** (saída de SonarQube, NDepend, analisadores da stack). Números medidos
   substituem estimativas.
5. **Código pela unidade de análise do tipo** (Passo 1), mais os componentes transversais: ponto
   de entrada, adapter de credenciais, fábrica de conexão, configuração de telemetria,
   `Dockerfile`, manifests.
6. **Testes** relacionados.
7. **Cenários de mudança**: 2 a 4 por aplicação, como pedidos reais do negócio. Se o projeto não
   tiver, **proponha** cenários plausíveis para o domínio e marque-os como "propostos pelo
   avaliador".
8. **Parecer anterior**: o mais recente da mesma aplicação em `outputs/maintainability/`, se
   houver. Ele vira a base da comparação do Passo 8.

Ignore código gerado e informe isso no relatório.

Se você tem acesso a um ambiente de execução e ao código, **meça o que puder em vez de estimar**:
contagem de linhas por método, número de parâmetros, profundidade de chamadas, referências entre
projetos, tipos públicos. Registre o comando usado. O que não for medido é marcado como
**estimado**.

### Passo 3 — Verificar premissas

Percorra P01–P14 (todos os tipos) e P15–P18 (só componentes) de
`references/persona-e-premissas.md`. Para cada uma: **Atende / Não atende / Não avaliado / Não se
aplica**, com evidência (arquivo e linha ou trecho).

"Não avaliado" é a resposta correta quando falta contexto. Nunca suponha.

### Passo 4 — Pontuar os eixos

Para cada eixo de `references/rubrica.md`:

- Dê nota de 1 a 5 pela âncora mais próxima (1, 3 ou 5; use 2 e 4 para intermediários).
- Cite a evidência principal.
- Marque se a nota é **medida** ou **estimada**.
- Para componentes, Web Services e Scripts SQL, aplique a releitura dos eixos descrita na rubrica.

### Passo 5 — Simular os cenários de mudança

Para cada cenário, liste:

- Arquivos que precisariam ser alterados.
- Caminho de leitura que o mantenedor percorreria até entender onde mexer (número de saltos).
- Construções fora do repertório que ele encontraria no caminho.
- Riscos de regressão.

Use o resultado como principal evidência dos eixos A3 e A6.

### Passo 6 — Calcular a nota

Siga exatamente o cálculo da rubrica: nota base ponderada pelos pesos do tipo, ajustes por
premissa, faixa de classificação e nível de confiança. **Mostre a conta.**

### Passo 7 — Escrever o parecer em HTML

Copie `assets/template-parecer.html`, substitua todos os marcadores `{{...}}` e remova os blocos
marcados como OPCIONAL que não se aplicarem. O arquivo final deve ser autocontido: nenhum CSS, JS,
fonte ou imagem externa.

**Onde salvar.** Um relatório por aplicação, na raiz do projeto:

```
<raiz-do-projeto>/outputs/maintainability/<app>_<tipo>_<AAAA-MM-DD>.html
```

- `<app>`: nome da aplicação em kebab-case, sem acentos (ex.: `pedidos-api`, `conciliacao-worker`,
  `db-scripts`).
- `<tipo>`: `api`, `worker`, `webservice`, `componente` ou `sql`.
- `<AAAA-MM-DD>`: data da análise.
- Crie `outputs/maintainability/` se não existir. Nunca sobrescreva um relatório: se já existir um
  com o mesmo nome, acrescente `_HHmm` ao final.
- Aplicação com mais de um tipo: um relatório por parte avaliada.

Regras de conteúdo:

- Todo achado tem: ID, eixo, severidade, evidência, princípio com referência bibliográfica e
  sugestão concreta.
- Sem evidência, não é achado.
- Aponte os pontos fortes, para que não sejam alterados numa nova versão.
- O plano de melhoria é ordenado por ganho estimado de pontos ÷ esforço, com a nota projetada após
  cada bloco de ações.
- Escreva para o arquiteto que vai decidir a evolução, em português, direto e com números.

### Passo 8 — Comparação

- **Parecer anterior da mesma aplicação** (achado no Passo 2): compare eixo a eixo, mostre o
  delta, indique quais ações do plano anterior foram aplicadas e se houve regressão em algum eixo.
- **Duas ou mais aplicações do mesmo tipo:** inclua uma seção comparativa: notas por eixo lado a
  lado, padrões que uma faz melhor e que a outra pode adotar, e problemas recorrentes (provável
  causa sistêmica: prompt de geração, template ou convenção).

Para que a comparação entre versões seja válida, registre no cabeçalho: data, identificação da
versão (tag, commit ou branch), tipo, modelo usado, fatia analisada e se a persona foi calibrada
pelo vault. Mudar qualquer desses itens muda a régua; aponte isso se acontecer.

### Passo 9 — Atualizar a fundamentação

Ao terminar a análise, execute o Modo Fundamentação (abaixo). Use o que já foi levantado na
análise como evidência, sem reler o que não mudou.

---

## Modo Fundamentação

Leia `references/fundamentacao.md` antes de começar. Resumo do fluxo:

1. **Delimitar o projeto.** Um único documento cobre todas as aplicações de `app/`.
2. **Ler o catálogo existente** em `outputs/references/<projeto>_fundamentacao.catalogo.json`, se
   houver.
3. **Levantar evidências** em documentos de intenção (`CLAUDE.md`, `docs/canonical/`, PRD,
   `specs/`, `decisions/`, prompts registrados), estrutura, código, testes, infra e histórico do
   Git.
4. **Identificar conceitos e decisões**: princípios, estilo arquitetural, DDD, estruturação do
   código, padrões de projeto e corporativos, persistência, integração, resiliência, segurança,
   desenho de APIs e de componentes, hospedagem, observabilidade, plataforma e testes. Classifique
   cada um em aplicação (aplicado, parcial, declarado e não aplicado) e nível para a persona (base,
   intermediário, avançado = estudo prioritário).
5. **Fundamentar** cada conceito com referências de `references/catalogo-conceitos.md`, da wiki do
   vault quando houver, ou de outras fontes confiáveis. Nunca invente obra, autor, ano ou capítulo.
6. **Comparar com o catálogo** e decidir: nova versão `v<N+1>` se algo entrou, mudou ou saiu; caso
   contrário, não gerar nova versão.
7. **Escrever** o HTML a partir de `assets/template-fundamentacao.html`, em ordem de estudo: visão
   geral → trilha de estudo → decisões → catálogo de conceitos → matriz conceito × aplicação →
   glossário → bibliografia → histórico.
8. **Salvar** o HTML versionado (nunca sobrescrever versões anteriores) e reescrever o catálogo
   JSON com o novo estado e o histórico.
9. **Informar** ao usuário a versão gerada e, em poucas linhas, o que entrou, mudou ou saiu.

---

## O que evitar

- Penalizar padrões que o time domina (Hexagonal, DDD tático, SOLID, OpenTelemetry) só por serem
  "verbosos".
- Recomendar construções fora do repertório como solução (ex.: trocar `if` por source generator).
- Recomendar mais abstração por padrão. Em código gerado por IA, o problema mais comum é
  **excesso** de camadas e abstrações prematuras, não falta.
- Notas sem conta explícita ou achados genéricos ("melhorar nomes") sem arquivo e linha.
- Aplicar critério de stack a uma linguagem que não tem arquivo em `stacks/`.
- Expor segredos encontrados no código: se achar um, reporte a localização e o tipo, nunca o
  valor.
- Na fundamentação: listar conceitos sem evidência no código, "enfeitar" a solução com padrões que
  ela não usa, ou citar referências incertas sem marcá-las para verificação.
