---
description: LOOP-4 — implementa uma task sob goals verificáveis (build limpo, testes verdes, cenários cobertos) em no máximo 4 tentativas. O tester escreve o RED no passo 0; o developer implementa cada tentativa.
---

# LOOP-4 — Implementação com Goals (máx 4 tentativas)

A sessão principal conduz o loop: goals, contagem de tentativas, `/bkhar:save` e `BLOQUEIO-*.md`.
Ela segue o protocolo do Gerente (skill `bks-team`) e delega a escrita do teste ao `tester` e a
implementação ao `developer`, cada um em invocação separada.

GOAL padrão (ajuste por task):
  G1. dotnet build sem erros e sem warnings novos
  G2. dotnet test 100% verde
  G3. todos os cenários do TEST-[feature].md cobertos
  G4. código respeita brain/engineering/ do projeto (calisthenics + hexagonal)

PASSO 0 — RED (antes da primeira tentativa):
  1. Chamar o agente `tester` com a TASK, o TEST-[feature].md e as entradas
     do LEARNINGS.md cujas tags batem com a área da task.
  2. O `tester` escreve os testes dos cenários, só em projeto de teste, e roda.
  3. Portão "RED confirmado": os testes compilam e falham pelo motivo certo,
     com a saída real colada. Teste que já passa não é RED: volta ao `tester`.
  4. Sem o portão aberto, não há tentativa 1.

PROTOCOLO:
  tentativa = 1
  ENQUANTO tentativa <= 4:
    1. Chamar o agente `developer` com a TASK, a FEAT, o TEST e os testes RED,
       mais o registro das tentativas anteriores. Ele implementa e devolve a
       saída real de build e teste.
    2. Conferir nesta sessão: dotnet build ; dotnet test
    3. Auditar G3 e G4 explicitamente
    4. SE todos os goals passaram:
         -> marcar a task como concluída em specs/tasks/TASK-[feature].md,
            rodar /bkhar:save, reportar e PARAR (OK)
    5. SENÃO:
         -> registrar em specs/tasks/TASK-[feature].md, na seção
            "Tentativas" da task, o erro e a hipótese de correção
         -> tentativa = tentativa + 1
  SE tentativa > 4:
    -> PARAR. Gerar outputs/BLOQUEIO-[task].md com: goal que
       falhou, erro exato, o que foi tentado nas 4 rodadas e a
       pergunta objetiva que você precisa que EU responda.
    -> python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync . --state blocked

Dentro do Maestri, `tester` e `developer` são chamados nos terminais deles, com `/clear` antes de
cada task nova (skill `bks-team`, seção "Despacho"); fora dele, como subagentes.

Decisão que foge da FEAT volta do `developer` para esta sessão, que pergunta ao usuário antes da
próxima tentativa.

## Modo `autonomo`

Com `axes.mode: autonomo` no `.bks-profile.json`:

- Decisão que foge da FEAT não volta ao usuário: o `architect` a resolve e grava em
  `decisions/SUPOSICOES.md`, e a próxima tentativa segue. Dado pessoal, autorização e segredo
  não se presumem: geram `outputs/BLOQUEIO-[task].md`.
- O loop só para em `BLOQUEIO`, e o `BLOQUEIO` para a cadeia de tasks que depende desta, não a onda.
- Os goals, o passo 0 e o teto de 4 tentativas não mudam.

## Modo onda — `/bkhar:loop --wave N`

Roda a onda N do grafo (`--wave next` escolhe a primeira com task pendente). Só no `autonomo`: no
`colaborativo`, recuse e indique o `/bkhar:mode`. A sessão principal é o orquestrador e a única
que escreve o estado; subagente não chama subagente.

PREPARO:
  1. python ${CLAUDE_PLUGIN_ROOT}/scripts/readiness.py .        -> recusada, PARAR
  2. python ${CLAUDE_PLUGIN_ROOT}/scripts/run_state.py init .
  3. python ${CLAUDE_PLUGIN_ROOT}/scripts/run_state.py show .   -> cole a tabela

CICLO, enquanto a onda N tiver task pendente ou em curso:
  1. Ponto de controle: aplicar a inbox (seção "Inbox" abaixo) e regerar a nota de status:
     python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync .
  2. python ${CLAUDE_PLUGIN_ROOT}/scripts/wave_graph.py ready . --json
     -> só as tasks da onda N; o script já respeita o teto de 4 tasks simultâneas
        e só libera task cujas entradas (`consome`) estão aprovadas.
  3. Para cada task liberada: modelo do papel pelo mapa `models` (skill `bks-team`) e
     python ${CLAUDE_PLUGIN_ROOT}/scripts/run_state.py start . --task T-00X --model M [--worktree W]
  4. Dispare as tasks liberadas na mesma mensagem, para rodarem em paralelo:
     - `desenho`: o `architect` com a lente da task (referência em
       `skills/bks-arch/references/lentes-system-design.md`) e só o que ela consome, ARCH e
       modelos incluídos; escreve o contrato em `specs/contracts/` com `status: rascunho`. Contrato
       que contradiz um modelo aprovado é achado bloqueante da revisão da onda. Lente `ameaças` é do
       `security`. Sem worktree: cada task escreve só os seus arquivos.
     - `construcao`, `front`, `integracao`: worktree própria,
       git worktree add ../{repo}-wt/T-00X -b wave/N/T-00X
       FEAT e TEST pelo `/bkhar:refine` no modo `autonomo`, se faltarem; depois o LOOP-4 acima,
       com `tester` e `developer` trabalhando dentro da worktree. Cada tentativa:
       run_state.py attempt . --task T-00X --n K
  5. Task encerrada: run_state.py finish . --task T-00X --result passou|bloqueada [--cost USD].
     `bloqueada` gera `outputs/BLOQUEIO-[task].md` e segura só a cadeia que depende dela.
     Avise o usuário com uma notificação (a ferramenta de notificação da sessão, quando houver);
     o painel também avisa pelo navegador. Em seguida, `status_note.py sync .`: no Maestri, o
     `floor status` em `blocked` também notifica.

FIM DA ONDA:
  1. Integração: merge de cada `wave/N/T-00X` na branch de trabalho, em ordem de id. Conflito
     PARA a onda em `outputs/BLOQUEIO-onda-N.md`, com os arquivos em conflito.
  2. Build e suíte completos na branch de trabalho, saída colada.
  3. `/bkhar:review` no modo `autonomo` sobre o diff da onda inteira.
  4. Onda de desenho: em `rigor: producao`, cada contrato espera o usuário mudar para
     `status: aprovado`; em `poc`, revisão sem bloqueante aprova, e cada aprovação vira evento.
  5. Arquitetura viva: rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py stale .`; o que
     estiver defasado entra no relatório da onda e pede `/bkhar:arch --update` antes da onda seguinte.
  6. `git worktree remove` de cada task integrada.
  7. Grave `outputs/run/onda-N/RELATORIO.md`: tasks, tentativas, modelo, custo, suposições novas,
     sugestões da revisão e bloqueios.
  8. `status_note.py sync . --state review` quando a onda espera o usuário num portão; senão,
     `status_note.py sync .`.
  9. Siga para a próxima onda só se não houver portão: os contratos em `producao` e a entrega
     final esperam o usuário.

INBOX (`outputs/run/inbox/`, escrita pelo painel):
  Nos pontos de controle, entre tentativas e entre tasks:
  python ${CLAUDE_PLUGIN_ROOT}/scripts/run_state.py inbox .
  aplique cada pedido que ele listar e confirme com `run_state.py applied . --id <pedido>`.

PROIBIDO: 5ª tentativa, relaxar o goal, marcar como concluído com teste falhando, o `developer`
editar o teste do `tester`, ou pular o passo 0.
