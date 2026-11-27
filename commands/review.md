---
description: Revisão em painel — tester, quality e, em área sensível ou adapter, security revisam a entrega em invocações separadas e read-only. Cada achado vira bloqueante, sugestão ou aprendizado.
---

Revisão em painel, conduzida pelo protocolo do Gerente (skill `bks-team`). Cada agente roda em
invocação SEPARADA da sessão de implementação e das outras revisões, sem ver a resposta dos outros.
Nunca quem escreveu revisa a si mesmo.

Argumento esperado: qual repo revisar (${BKS_VAULT}/repos/{categoria}/{projeto}). Se não informado, pergunte
antes de continuar — nunca adivinhe o projeto ativo.

Quem roda:

| Agente | Quando | O que revisa |
|---|---|---|
| `tester` | sempre que há diff de código | se cada cenário do TEST-[feature].md está coberto no código entregue |
| `quality` | sempre que há diff de código | legibilidade, os arquivos de teste, os resultados da execução |
| `security` | quando o diff toca "Área sensível" do manifesto, um adapter de entrada ou um adapter de saída de banco | dado sensível, autorização, log, segredo, zona de contenção, injeção |
| `architect` | quando o diff cruza fronteira de contexto ou premissa | fronteira, contrato, padrão |

O `tester` não revisa os próprios testes: a força das asserções e a fragilidade são do `quality`.

Pré-requisitos:
1. O diff toca adapter de entrada ou adapter de saída de banco (tabela abaixo)? Se sim, o
   `security` roda mesmo sem manifesto, com o escopo da injeção (`SEC-01` e `SEC-03`).
2. O projeto tem manifesto em {repo}/.claude/multiagente.md? Se não, oriente a criá-lo a partir do
   template `manifesto-projeto.md`; sem ele, o `security` só roda pelo item 1.
   Precedência de template: `{repo}/.bks/templates/`, senão `${BKS_VAULT}/workbench/templates/`, senão `${CLAUDE_PLUGIN_ROOT}/templates/`.
3. A mudança toca alguma "Área sensível" declarada no manifesto? Se não, e o item 1 também não
   se aplica, o `security` não roda: não gaste Opus revisando mudança de documentação.

Como reconhecer o adapter no diff, pelas mesmas pastas dos testes de arquitetura:

| Stack | Adapter de entrada | Adapter de saída de banco |
|---|---|---|
| .NET | `Adapters/Inbound/`, projeto `.Adapters.Inbound` | `Adapters/Outbound/` com Dapper, Entity Framework Core, Npgsql ou SqlClient |
| TypeScript | `routes/`, `plugins/`, `handlers/`, `consumers/`, `workers/`, `processors/`, `graph/` | `*.repository.ts` |
| Go | `internal/adapter/<nome>` que recebe a chamada (http, grpc, consumer) | `internal/adapter/<nome>` com `database/sql`, pgx ou driver de banco |

O adapter de saída que não fala com banco (HTTP, fila, arquivo) só entra pela "Área sensível".

Revisão de escrita — sempre que a mudança toca documentação viva (`README.md`, `ARCHITECTURE.md`,
cânone, spec, treinamento), mesmo sem área sensível e sem manifesto. Roda nesta sessão, sem
agente:

1. `python ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/writing_guard.py <arquivos .md tocados>` — cole a
   saída. Achado volta para correção.
2. Leia cada arquivo pela checklist e pela nota por dimensão da skill `bks-writing`. Reporte a
   nota de cada dimensão e o total; abaixo de 45, diga o que revisar.

Contexto para os agentes (cada um recebe o que o perfil dele pede):
- Diff ou arquivos específicos da entrega (não o repo inteiro)
- TEST-[feature].md da feature
- Seção "Invariantes do domínio" e "Áreas sensíveis" do manifesto do projeto
- {repo}/decisions/ (não repetir achado já decidido/aceito NESTE projeto)

Saída: os achados agrupados pelo Gerente, cada um com `arquivo:linha` e classificado como:
- **bloqueante** — vira proposta de task. O `architect` só escreve o `specs/tasks/TASK-*.md`
  depois do ok do usuário. Crítica do `security` é sempre bloqueante.
- **sugestão** — o usuário decide.
- **aprendizado** — defeito detectado e resolvido, com evidência, que o `quality` devolve como caso
  para o `LEARNINGS.md`. O `/bkhar:save` grava.

Revisão sem achado declara o escopo verificado por agente. A correção volta ao `developer`, em
invocação separada.

## Modo `autonomous`

Com `axes.mode: autonomous`, a revisão roda sobre a onda inteira, no fim dela, e o destino dos
achados muda:

- **bloqueante** vira TASK sem esperar o ok e volta ao `/bkhar:loop`, com o mesmo teto de 4
  tentativas;
- **crítica do `security`** não volta ao loop: para a cadeia em `outputs/BLOQUEIO-[task].md`, que
  só o usuário destrava;
- **sugestão** vai para `outputs/run/<onda>/RELATORIO.md`, que o usuário lê na entrega da onda;
- **aprendizado** segue como no colaborativo.
