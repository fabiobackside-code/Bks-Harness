# Persona do mantenedor e premissas

## 1. Persona de referência

O parecer mede o custo de manutenção para um desenvolvedor **pleno** do time. A persona tem uma
base neutra de linguagem, aqui, e um repertório por stack, em `stacks/<linguagem>.md`.

| Atributo | Definição |
| --- | --- |
| Experiência | 3 a 5 anos, pleno: entrega sozinho dentro de padrões conhecidos, pede revisão em decisão estrutural |
| Arquitetura | Hexagonal, Ports & Adapters, DDD tático, SOLID, Object Calisthenics, DRY |
| Tipos de solução | APIs REST, Workers, Web Services, bibliotecas/SDKs/componentes internos, scripts SQL |
| Dados | Bancos relacionais e não relacionais, com acesso explícito por SQL ou ORM |
| Segurança | Consome segredos por abstração, sem conhecer o funcionamento interno do cofre |
| Observabilidade | OpenTelemetry (traces, métricas, logs) |
| Plataforma | Docker e Kubernetes |

O repertório da stack diz o que a persona domina na linguagem e o que fica **fora do repertório**.
Usar o que está fora não é proibido. O critério é: **se usado, está isolado, nomeado com clareza e
com o porquê documentado?**

### Calibração pelo vault

Se `BKS_VAULT` estiver definido e acessível, leia antes de pontuar:

- `${BKS_VAULT}/workbench/profile.md`: o perfil de quem orienta o time. Ele calibra o repertório
  da persona (stacks e padrões que o time domina de fato) e as premissas que o time adota.
- `${BKS_VAULT}/knowledge/wiki/`: as lições e referências do time. Cite-as como fonte de achado ou
  de conceito quando se aplicarem, com o caminho relativo ao vault.

O vault calibra, não substitui: a persona continua pleno, e a rubrica não muda. Sem vault, use só
esta base e registre no cabeçalho do parecer "persona: base do kit, sem calibração do vault".

## 2. Premissas para todos os tipos (P01–P14)

Críticas: **P01, P03, P04, P05**. Qualquer violação limita a nota final a 40.

| ID | Premissa | Como verificar |
| --- | --- | --- |
| P01 | O domínio não referencia infraestrutura (driver de banco, ORM, cliente HTTP, cliente de cofre, SDK de telemetria) | Imports e referências do projeto ou namespace de domínio |
| P02 | Todo acesso a dados passa por um port declarado na aplicação ou no domínio e implementado num adapter | Interfaces de repositório/gateway fora da infra; implementações só na infra |
| P03 | SQL é parametrizado; nenhuma concatenação ou interpolação com entrada externa | Busca por interpolação ou `+` em comandos SQL; SQL dinâmico sem parâmetros |
| P04 | Nenhum segredo em código, arquivo de configuração, variável de ambiente em claro ou manifest | Padrões de senha/token/connection string; origem das credenciais |
| P05 | Se há cofre de credenciais, um único adapter o acessa, com cache e renovação explícitos | Um ponto de entrada para o cofre; política de expiração visível. Sem cofre: **Não se aplica** |
| P06 | Ciclo de vida de conexões e transações explícito | Abertura e descarte de conexão e transação |
| P07 | Toda operação de I/O é assíncrona e cancelável, onde a stack oferece isso | Assinaturas de ports e adapters; bloqueio síncrono sobre código assíncrono |
| P08 | Workers tratam falha por item sem derrubar o laço e respeitam encerramento gracioso | Laço principal, tratamento por iteração, sinal de parada (só Workers) |
| P09 | Traces, métricas e logs via OpenTelemetry com nomes padronizados e correlação | Fontes de trace e métrica, propagação de contexto, logs estruturados |
| P10 | Configuração externalizada e validada na inicialização | Leitura de configuração tipada e validada no startup |
| P11 | Health checks de liveness e readiness separados, compatíveis com o orquestrador | Endpoints e probes (APIs, Workers e Web Services) |
| P12 | Contêiner roda sem root e sem depender de UID fixo | Dockerfile, `USER`, permissões (quando há contêiner) |
| P13 | Componentes compartilhados têm contrato público pequeno, versionado e documentado | API pública, README, CHANGELOG |
| P14 | Há testes de unidade do domínio e testes de integração dos adapters críticos | Projetos de teste, cobertura dos fluxos principais |

Premissas que não se aplicam ao tipo (ex.: P08 numa biblioteca; P07, P11 e P12 em Scripts SQL)
são marcadas como **Não se aplica** e não penalizam.

## 3. Premissas adicionais para bibliotecas, SDKs e componentes (P15–P18)

Crítica: **P15**.

| ID | Premissa | Como verificar |
| --- | --- | --- |
| P15 | Mudança incompatível na superfície pública só ocorre com nova versão major | Analisador de API pública, comparação de API entre versões, CHANGELOG |
| P16 | Pontos de extensão são interfaces ou delegates documentados, com implementação padrão | Interfaces públicas, registro padrão, exemplo no README |
| P17 | Tipos que não fazem parte do contrato ficam fora da superfície pública | Tipos públicos vs. tipos efetivamente usados por consumidores |
| P18 | O consumidor registra e configura o componente com um único ponto de entrada e opções validadas | Extensão de registro, validação de opções |

## 4. Premissas do projeto

Premissas próprias do projeto (requisitos regulatórios, trilha de auditoria, idempotência,
padrões internos) vêm do `CLAUDE.md`, de `brain/engineering/` e de `decisions/`. Trate-as com IDs
`PU01`, `PU02`... e pergunte se são críticas. Na dúvida, trate como não crítica (−5).
