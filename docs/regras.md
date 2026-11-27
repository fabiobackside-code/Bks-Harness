# Regras do bkhar e seus sensores

> Gerado por `scripts/rules_report.py` a partir do `rules.json`. Não editar à mão.

Regras: 51 · com sensor computacional: 36 (2 indireto, 4 de aviso) · só inferencial: 10 · sem sensor: 5

## Por alvo

| Alvo | Regras | Computacional | Só inferencial | Sem sensor |
|---|---|---|---|---|
| codigo | 23 | 14 | 9 | 0 |
| documentacao | 6 | 5 | 1 | 0 |
| processo | 14 | 11 | 0 | 3 |
| kit | 8 | 6 | 0 | 2 |

## Sem sensor

- PRC-06 · Só o usuário promove aprendizado — a promoção é ato do usuário no /bkhar:retro; não há ação de agente que um script confira
- PRC-13 · Gerente não opina sobre técnica; conflito exposto sem escolha — comportamento do Gerente no rito; só o usuário confere
- PRC-14 · Painel com invocações separadas e independentes — comportamento do Gerente no rito; só o usuário confere
- KIT-07 · Decisão no ARCHITECTURE.md, não em comentário, também no código Python do kit — conferida na revisão do próprio kit, sem ferramenta que leia comentário Python
- KIT-08 · Mudança de skill sai com o delta do eval — o eval custa crédito; o delta é exigido no processo de mudança de skill

## Parâmetros vinculados

Valor repetido entre guia e sensor; mudar num lugar só quebra o `--check`.

| id | Parâmetro | Valor | Onde aparece |
|---|---|---|---|
| COD-02 | teto de linhas por bloco de comentário | 5 | `README.md`, `docs/ARCHITECTURE.md`, `hooks/scripts/comment_budget.py`, `skills/bks-dotnet-solutions/SKILL.md`, `skills/bks-dotnet-solutions/references/comment-convention.md`, `skills/bks-go-solutions/SKILL.md`, `skills/bks-sdd/SKILL.md`, `skills/bks-standards/references/documentacao.md` |
| DOC-05 | teto de palavras por frase | 40 | `README.md`, `hooks/scripts/writing_guard.py`, `skills/bks-writing/SKILL.md` |
| PRC-03 | tasks simultâneas na onda | 4 | `README.md`, `commands/loop.md`, `docs/ARCHITECTURE.md`, `scripts/wave_graph.py` |
| PRC-04 | tentativas por task no LOOP-4 | 4 | `README.md`, `agents/developer.md`, `commands/loop.md`, `commands/mode.md`, `docs/ARCHITECTURE.md`, `scripts/run_state.py` |

## Registro

| id | Regra | Fonte | Sensores |
|---|---|---|---|
| COD-01 | Sem MediatR nem dispatcher em C# | `skills/bks-standards/references/bks-premises.md` · Padrão-base: Hexagonal + Result; Pipeline e TXC quando o projeto adota o TXC | C `hooks/scripts/no_dispatcher.py` (hook, pre-commit, ci) |
| COD-02 | Bloco de comentário até 5 linhas em C# | `skills/bks-standards/references/documentacao.md` · Comentário no código | C `hooks/scripts/comment_budget.py` (hook, pre-commit, ci) |
| COD-03 | Sem marca de severidade em comentário | `skills/bks-standards/references/documentacao.md` · Comentário no código | C `hooks/scripts/comment_budget.py` (hook, pre-commit, ci) |
| COD-04 | Domínio referencia só System.* | `skills/bks-standards/references/dotnet-standards.md` · Regras de dependência | C `skills/bks-dotnet-solutions/references/architecture-tests.md` (suite) |
| COD-05 | Dependência Adapters → Application → Domain, nunca o contrário | `skills/bks-standards/references/dotnet-standards.md` · Regras de dependência | C `skills/bks-dotnet-solutions/references/architecture-tests.md` (suite)<br>C `skills/bks-typescript-solutions/references/architecture-tests.md` (suite)<br>C `skills/bks-go-solutions/references/architecture-tests.md` (suite) |
| COD-06 | Exceção de negócio não escapa; o serviço ou o executor devolve PipelineResult | `skills/bks-standards/references/bks-premises.md` · Padrão-base: Hexagonal + Result; Pipeline e TXC quando o projeto adota o TXC | I `agents/quality.md` (revisao, indireto) |
| COD-07 | Sem Activity montada à mão; o span vem do pipeline | `skills/bks-standards/references/bks-premises.md` · Padrão-base: Hexagonal + Result; Pipeline e TXC quando o projeto adota o TXC | C `skills/bks-dotnet-solutions/references/architecture-tests.md` (suite) |
| COD-08 | TXC é record imutável | `skills/bks-standards/references/bks-premises.md` · Padrão-base: Hexagonal + Result; Pipeline e TXC quando o projeto adota o TXC | I `agents/architect.md` (revisao) |
| COD-09 | Sem FluentAssertions; Assert nativo do xUnit | `skills/bks-standards/references/dotnet-standards.md` · Solution e asserção (ADR-010, 27/08) | C `hooks/scripts/dotnet_project.py` (hook, pre-commit, ci) |
| COD-10 | Solution .NET 10 em .slnx | `skills/bks-standards/references/dotnet-standards.md` · Solution e asserção (ADR-010, 27/08) | C `hooks/scripts/dotnet_project.py` (hook, pre-commit) |
| COD-11 | Pacote NuGet só com confirmação explícita | `skills/bks-standards/references/dotnet-standards.md` · Dependência, banco e tipagem | I `agents/quality.md` (revisao) |
| COD-12 | Migration existente não é alterada | `skills/bks-standards/references/dotnet-standards.md` · Dependência, banco e tipagem | C `hooks/scripts/dotnet_project.py` (hook, pre-commit) |
| COD-13 | Sem dynamic nem object sem justificativa | `skills/bks-standards/references/dotnet-standards.md` · Dependência, banco e tipagem | C `skills/bks-dotnet-solutions/references/architecture-tests.md` (suite) |
| COD-14 | record em Transaction, Value Object e DTO de resposta | `skills/bks-standards/references/dotnet-standards.md` · Dependência, banco e tipagem | I `agents/architect.md` (revisao) |
| COD-15 | Toda task tem teste | `skills/bks-tests/SKILL.md` · Solution .NET — o que esta skill entrega | I `agents/tester.md` (revisao) |
| COD-16 | Projeto de testes em src/ | `skills/bks-tests/SKILL.md` · Localização do projeto de testes | I `agents/architect.md` (revisao) |
| COD-17 | Dado sensível não vai para log | `skills/bks-standards/references/checklist-revisao-critica.md` · Núcleo (qualquer domínio) | I `agents/security.md` (revisao) |
| COD-18 | Credencial com valor real não entra em código nem configuração | `docs/ARCHITECTURE.md` · A guarda vale em três camadas, e cada uma só vê o que alcança | C `hooks/scripts/secret_guard.py` (hook, pre-commit, ci) |
| COD-19 | Go: erro idiomático, sem Result[T] | `skills/bks-standards/references/go-standards.md` · 2. Erro de negócio: `error` idiomático, não `Result[T]` | C `skills/bks-go-solutions/references/architecture-tests.md` (suite) |
| COD-20 | Go: interface declarada no consumidor | `skills/bks-standards/references/go-standards.md` · 4. Ports: a interface se declara no consumidor | I `agents/architect.md` (revisao) |
| SEC-01 | SQL só com parâmetro, sem concatenação nem interpolação de texto | `skills/bks-standards/references/checklist-revisao-critica.md` · Núcleo (qualquer domínio) | C `skills/bks-dotnet-solutions/references/architecture-tests.md` (suite)<br>C `skills/bks-typescript-solutions/references/architecture-tests.md` (suite)<br>C `skills/bks-go-solutions/references/architecture-tests.md` (suite)<br>I `agents/security.md` (revisao) |
| SEC-02 | Dependência sem CVE conhecido | `skills/bks-standards/references/checklist-revisao-critica.md` · Núcleo (qualquer domínio) | C `templates/ci/github-guards.yml` (ci)<br>C `templates/ci/gitlab-guards.yml` (ci)<br>I `agents/security.md` (revisao) |
| SEC-03 | Entrada externa que chega a SQL, shell, caminho ou URL é revisada pelo security | `skills/bks-standards/references/checklist-revisao-critica.md` · Núcleo (qualquer domínio) | I `agents/security.md` (revisao) |
| DOC-01 | Task que cria tipo público atualiza README.md e ARCHITECTURE.md | `skills/bks-standards/references/documentacao.md` · Quando gerar/atualizar | C `hooks/scripts/dod_docs.py` (hook) |
| DOC-02 | Decisão e trade-off vão para o ARCHITECTURE.md, não para comentário | `skills/bks-standards/references/documentacao.md` · Comentário no código | C `hooks/scripts/comment_budget.py` (hook, pre-commit, ci, indireto) |
| DOC-03 | Sem ponteiro para documento em comentário | `skills/bks-standards/references/documentacao.md` · Comentário no código | C `hooks/scripts/comment_budget.py` (hook, pre-commit, ci) |
| DOC-04 | PT-BR com acentuação; identificador técnico em ASCII | `skills/bks-standards/references/documentacao.md` · Idioma | I `agents/quality.md` (revisao) |
| DOC-05 | Doc viva: frase até 40 palavras, sigla definida, sem muleta nem emoji | `skills/bks-writing/SKILL.md` · 9. O que a guarda confere e o que a revisão confere | C `hooks/scripts/writing_guard.py` (hook, aviso) |
| DOC-06 | ADR citado só na nota de decisão | `skills/bks-writing/SKILL.md` · 1. A decisão entra no texto | C `hooks/scripts/writing_guard.py` (hook, aviso) |
| PRC-01 | Task de desenho consome o ARCH aprovado | `docs/ARCHITECTURE.md` · A arquitetura é portão, e o modelo sabe quando ficou para trás | C `scripts/wave_graph.py` (script) |
| PRC-02 | O modo autônomo só com a prontidão aprovada | `docs/ARCHITECTURE.md` · O modo `autonomous` é concedido por script, não por pedido | C `scripts/readiness.py` (script) |
| PRC-03 | Até 4 tasks simultâneas na onda | `docs/ARCHITECTURE.md` · As ondas saem do grafo, e o estado tem um escritor só | C `scripts/wave_graph.py` (script) |
| PRC-04 | Até 4 tentativas por task no LOOP-4 | `docs/ARCHITECTURE.md` · As ondas saem do grafo, e o estado tem um escritor só | C `scripts/run_state.py` (script) |
| PRC-05 | Painel e dashboard escrevem só na inbox | `docs/ARCHITECTURE.md` · O painel escreve só na inbox | C `scripts/dashboard.py` (script, indireto) |
| PRC-06 | Só o usuário promove aprendizado | `docs/ARCHITECTURE.md` · O aprendizado volta como candidato, e só o usuário promove | — |
| PRC-07 | architect: Bash só nos scripts do plugin, git de leitura e maestri ask; escrita só em specs/, decisions/, docs/ e outputs/ | `docs/ARCHITECTURE.md` · A integração com o Maestri é configuração, e o `manager` concentra os comandos delegados | C `hooks/scripts/architect_bash.py` (hook) |
| PRC-08 | Agente não lê nem edita arquivo de segredo | `docs/ARCHITECTURE.md` · A guarda vale em três camadas, e cada uma só vê o que alcança | C `hooks/scripts/secret_guard.py` (hook) |
| PRC-09 | Sem remoção recursiva na raiz, no home ou fora do projeto | `docs/ARCHITECTURE.md` · A guarda vale em três camadas, e cada uma só vê o que alcança | C `hooks/scripts/secret_guard.py` (hook) |
| PRC-10 | Escrita só no projeto e nas raízes permitidas; configuração do Claude à mão | `docs/ARCHITECTURE.md` · A guarda vale em três camadas, e cada uma só vê o que alcança | C `hooks/scripts/secret_guard.py` (hook) |
| PRC-11 | STATUS.md não fica atrás do JOURNAL.md nem do git | `docs/ARCHITECTURE.md` · A deriva do `STATUS.md` é conferida na abertura da sessão | C `hooks/scripts/session_memory.py` (hook, aviso) |
| PRC-12 | Modelo de arquitetura defasado é avisado | `docs/ARCHITECTURE.md` · A arquitetura é portão, e o modelo sabe quando ficou para trás | C `scripts/library.py` (script, aviso) |
| PRC-13 | Gerente não opina sobre técnica; conflito exposto sem escolha | `skills/bks-team/SKILL.md` · O que o Gerente não faz | — |
| PRC-14 | Painel com invocações separadas e independentes | `skills/bks-team/SKILL.md` · Escolher o painel quando o usuário não diz | — |
| KIT-01 | Todo guarda tem teste em hooks/tests/ | `docs/ARCHITECTURE.md` · Regra precisa de guarda executável | C `tests/test_structure.py` (suite, ci) |
| KIT-02 | Todo guarda do diretório está declarado no hooks.json | `docs/ARCHITECTURE.md` · Regra precisa de guarda executável | C `tests/test_structure.py` (suite, ci) |
| KIT-03 | Caminho citado em documento existe | `docs/ARCHITECTURE.md` · Ponteiro para arquivo é verificado | C `tests/test_structure.py` (suite, ci) |
| KIT-04 | HTML dos artefatos em dia com a fonte | `README.md` · Verificação | C `scripts/build_artefatos.py` (suite, ci) |
| KIT-05 | Público não vaza caminho local nem e-mail | `docs/ARCHITECTURE.md` · O público recebe uma lista, não uma cópia | C `scripts/publish.py` (suite, ci) |
| KIT-06 | O kit passa nos próprios guardas | `docs/ARCHITECTURE.md` · A guarda vale em três camadas, e cada uma só vê o que alcança | C `scripts/precommit.py` (pre-commit, ci) |
| KIT-07 | Decisão no ARCHITECTURE.md, não em comentário, também no código Python do kit | `docs/ARCHITECTURE.md` · Regra precisa de guarda executável | — |
| KIT-08 | Mudança de skill sai com o delta do eval | `README.md` · Verificação | — |
