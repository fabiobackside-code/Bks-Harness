# Modo Fundamentação — documento de referência da solução

## Objetivo

Gerar e manter um documento de estudo que explique **em que se apoiou a construção da solução**: literatura, conceitos, princípios, estilos arquiteturais, padrões, abordagens de estruturação de código e as decisões técnicas tomadas.

O documento atende três leitores:

- **Quem construiu** e quer conhecer a base teórica do que foi produzido.
- **Quem orientou a construção via Claude** (Opus, Sonnet, Haiku, Fable ou outro modelo) por meio de prompts, specs e contexto, e precisa saber que fundamentos sustentam o resultado.
- **Quem vai manter**: o dev pleno da persona, que precisa de uma trilha de estudo para dominar o que está no código.

## Escopo: o projeto inteiro, não uma aplicação

Um único documento por **projeto** do kit, cobrindo todas as aplicações do `app/`. Exemplo: um projeto de farmácia com 3 APIs, 2 componentes e uma pasta de scripts SQL tem **um** documento de fundamentação, cobrindo as 6 aplicações, com uma matriz que mostra qual conceito aparece em qual aplicação.

- **Raiz:** a raiz do projeto, onde estão `STATUS.md` e `app/`. Fora de um projeto do kit, use a pasta que o usuário indicar; se não estiver claro, pergunte.
- Se apenas parte das aplicações for analisada nesta execução, atualize a parte delas e mantenha as demais como estavam na versão anterior, com a data da última verificação de cada uma.

## Onde salvar e como versionar

```
<raiz-do-projeto>/outputs/references/<projeto>_fundamentacao_v<N>_<AAAA-MM-DD>.html
<raiz-do-projeto>/outputs/references/<projeto>_fundamentacao.catalogo.json
```

- `<projeto>`: nome do projeto em kebab-case, sem acentos (ex.: `farmacia`).
- `<N>`: número inteiro da versão, começando em 1.
- O HTML de cada versão **nunca** é sobrescrito. Versões antigas ficam na pasta para estudo da evolução.
- O catálogo JSON é o índice vivo: guarda o estado atual de conceitos e decisões e o histórico de versões. É reescrito a cada nova versão (formato em `assets/catalogo-fundamentacao.exemplo.json`).

### Quando gerar uma nova versão

1. Leia o catálogo existente, se houver.
2. Levante conceitos e decisões no estado atual do código e da documentação.
3. Compare com o catálogo:
   - Conceito ou decisão **novo** → entra, marcado com "desde vN".
   - Conceito que **deixou de ser usado** → permanece no documento como "removido na vN", com o motivo, se conhecido.
   - Conceito com **mudança de aplicação** (ex.: Repository passou a usar Unit of Work; um projeto novo passou a usar o conceito) → atualizado, com a mudança no histórico.
   - Decisão revista → nova decisão que **substitui** a anterior; a antiga permanece marcada como "substituída por Dxx".
4. Se houver qualquer alteração, gere `v<N+1>` e atualize o catálogo.
5. Se não houver alteração, **não** gere nova versão. Informe ao usuário: "Fundamentação sem alterações; versão atual vN".

## Fontes a examinar

Na ordem:

1. Documentos de intenção: `CLAUDE.md`, `docs/canonical/CONTEXT.md`, PRD, `specs/`, `decisions/`, `brain/engineering/`, README, prompts registrados em `docs/prompts/`.
2. Estrutura: o inventário de aplicações, os arquivos de projeto e as referências entre eles, conforme a seção Detecção de cada `stacks/<linguagem>.md`.
3. Código: ponto de entrada, registro de dependências, domínio, ports, adapters, casos de uso, workers, componentes públicos, scripts SQL.
4. Testes.
5. Infra: `Dockerfile`, manifests, pipelines.
6. Histórico do Git (quando disponível): mensagens de commit e diffs que introduziram conceitos novos.

## Regras de rigor

- **Só entra no documento o que tem evidência** no código ou nos documentos de intenção. Cada conceito aponta onde aparece (projeto e arquivo).
- Classifique a aplicação de cada conceito:
  - **Aplicado:** presente e consistente.
  - **Aplicado parcialmente:** presente com desvios (ex.: DDD declarado, mas entidades anêmicas).
  - **Declarado e não aplicado:** citado em spec ou `CLAUDE.md`, sem correspondência no código. Isso é informação valiosa para quem orientou a construção.
- Nível do conceito em relação à persona (ver `persona-e-premissas.md`):
  - **Base:** dentro do repertório do time.
  - **Intermediário:** o time conhece o nome, mas raramente aplicou.
  - **Avançado:** fora do repertório. Marque como **estudo prioritário**.
- Referências: cite apenas obras, artigos, RFCs e documentações oficiais que você tem segurança de que existem. Indique capítulo ou seção quando souber; se não souber, cite só a obra. Nunca invente título, autor, ano ou capítulo. Na dúvida, marque "verificar referência".
- Explique cada conceito em linguagem acessível à persona: o que é, por que foi usado **nesta** solução, e um trecho curto do código que o ilustra.
- Não exponha segredos em trechos de código.

## Estrutura do documento (ordem de estudo)

Ordene do geral ao específico, para que a leitura sequencial funcione como trilha de aprendizado:

1. **Visão geral do projeto** — propósito, aplicações (APIs, Workers, Web Services, componentes, scripts SQL), como se relacionam e qual o papel de cada uma.
2. **Trilha de estudo recomendada** — sequência sugerida de conceitos, dos fundamentos aos específicos, com estimativa de esforço (leitura curta, capítulo, livro) e destaque para os de estudo prioritário.
3. **Decisões técnicas** — no formato de ADR resumido: ID (D01…), contexto, decisão, alternativas consideradas (se conhecidas), consequências, conceitos que a sustentam, onde está no código, origem (spec, prompt, ADR, inferida do código), status (vigente, substituída).
4. **Catálogo de conceitos por categoria**, nesta ordem:
   1. Princípios de design (ex.: SOLID, DRY, KISS, YAGNI, Lei de Demeter, Ocultação de informação, Object Calisthenics)
   2. Estilo arquitetural (ex.: Hexagonal / Ports & Adapters, Clean Architecture, monólito modular, microsserviços)
   3. Design estratégico e tático de domínio (ex.: contextos delimitados, linguagem ubíqua, entidade, value object, agregado, serviço de domínio, eventos de domínio)
   4. Estruturação do código (ex.: organização por camadas ou por feature/vertical slice, pipeline de execução, CQRS, padrões internos da organização como Pipeline Orchestration, Transaction Parameter Object, BKS-TXC)
   5. Padrões de projeto (GoF e afins: Strategy, Factory, Decorator, Adapter, Template Method, Builder)
   6. Padrões de aplicação corporativa (Repository, Unit of Work, Data Mapper, Service Layer, DTO, Options)
   7. Persistência e dados (micro-ORM, ORM, SQL parametrizado, transações, procedures, modelagem)
   8. Integração e mensageria (consumidores concorrentes, idempotência, dead letter, outbox, retry)
   9. Resiliência (timeout, retry com backoff, circuit breaker)
   10. Segurança (gestão de segredos em cofre, princípio do menor privilégio, prevenção de injeção)
   11. Desenho de APIs (REST, contratos, versionamento, Problem Details — RFC 9457, validação)
   12. Desenho de bibliotecas e componentes (superfície pública mínima, pontos de extensão, versionamento semântico, compatibilidade)
   13. Hospedagem e Workers (host genérico da stack, serviços em segundo plano, injeção de dependência, configuração)
   14. Observabilidade (OpenTelemetry: traces, métricas, logs, convenções semânticas)
   15. Plataforma e entrega (Twelve-Factor, contêineres, Kubernetes/OpenShift, health checks)
   16. Testes (pirâmide de testes, TDD, dublês de teste, testes de integração, testes de arquitetura)

   Inclua somente as categorias com conceitos encontrados. Para cada conceito:

   | Campo | Conteúdo |
   | --- | --- |
   | Nome | Nome canônico do conceito |
   | O que é | 2 a 3 frases, linguagem acessível |
   | Por que nesta solução | Motivo concreto, ligado a uma decisão (Dxx) quando houver |
   | Onde aparece | Projetos e arquivos |
   | Trecho ilustrativo | Até 15 linhas, sem segredos |
   | Aplicação | Aplicado / parcialmente / declarado e não aplicado |
   | Nível | Base / intermediário / avançado (estudo prioritário) |
   | Referências | Obra, autor, capítulo/seção quando conhecido |
   | Relacionados | Outros conceitos do catálogo |
   | Desde | Versão em que entrou; alterações posteriores |

5. **Matriz conceito × aplicação** — linhas = conceitos, colunas = aplicações do projeto.
6. **Glossário do domínio** — termos da linguagem ubíqua encontrados no código, com a classe ou tabela correspondente.
7. **Bibliografia consolidada** — agrupada por tema, com os conceitos que cada obra sustenta.
8. **Histórico de versões** — por versão: data, o que entrou, o que mudou, o que saiu, quais projetos foram verificados.

Use `assets/template-fundamentacao.html` e `references/catalogo-conceitos.md` (referências canônicas por conceito).
