---
description: LOOP-4 — implementa uma task sob goals verificáveis (build limpo, testes verdes, cenários cobertos) em no máximo 4 tentativas, na branch task/T-NNN. O tester escreve o RED no passo 0; o developer implementa cada tentativa; --resume retoma do bloqueio ou da queda.
---

# LOOP-4 — Implementação com Goals (máx 4 tentativas)

A sessão principal conduz o loop: goals, contagem de tentativas, `/bkhar:save` e `BLOQUEIO-*.md`.
Ela segue o protocolo do Gerente (skill `bks-team`) e delega a escrita do teste ao `tester` e a
implementação ao `developer`, cada um em invocação separada.

A task vem de `specs/tasks/TASK-[feature].md`, escrito pelo `/bkhar:tasks`. Task que não está
lá não roda: indique o `/bkhar:tasks`.

GOAL padrão (ajuste por task):
  G1. dotnet build sem erros e sem warnings novos
  G2. dotnet test 100% verde
  G3. todos os cenários do TEST-[feature].md cobertos
  G4. código respeita brain/engineering/ do projeto (calisthenics + hexagonal)

Toda chamada abaixo a `recovery.py` é `python ${CLAUDE_PLUGIN_ROOT}/scripts/recovery.py <subcomando> .
--task T-00X`. Saída `recusado:` para o loop e vai ao usuário como está; não contorne.

PASSO 0 — branch e RED (antes da primeira tentativa):
  1. recovery.py begin  -> cria a task/T-00X a partir da branch atual; recusa árvore suja
     e branch protegida (main, master e `guards.protected_branches` do perfil).
  2. Chamar o agente `tester` com a TASK, o TEST-[feature].md e as entradas
     do LEARNINGS.md cujas tags batem com a área da task.
  3. O `tester` escreve os testes dos cenários, só em projeto de teste, e roda.
  4. Portão "RED confirmado": os testes compilam e falham pelo motivo certo,
     com a saída real colada. Teste que já passa não é RED: volta ao `tester`.
  5. recovery.py gate --phase red  -> commit do portão, sob o pre-commit do projeto.
  6. Sem o portão commitado, não há tentativa 1.

PROTOCOLO:
  tentativa = 1
  ENQUANTO tentativa <= 4:
    1. recovery.py attempt --n <tentativa>
    2. Chamar o agente `developer` com a TASK, a FEAT, o TEST e os testes RED,
       mais o registro das tentativas anteriores. Ele implementa e devolve a
       saída real de build e teste.
    3. Conferir nesta sessão: dotnet build ; dotnet test
    4. Auditar G3 e G4 explicitamente
    5. recovery.py snapshot --score "<placar: testes verdes X/Y, build ok>" [--passed]
       -> foto da tentativa em refs/bkhar/T-00X/impl-K, fora do histórico.
    6. SE todos os goals passaram (snapshot com --passed):
         -> revisão; aprovada: recovery.py gate --phase review e recovery.py integrate
            (merge --no-ff na branch de origem; conflito para e lista os arquivos)
         -> marcar a task como concluída em specs/tasks/TASK-[feature].md,
            rodar /bkhar:save, reportar e PARAR (OK)
    7. SENÃO:
         -> registrar em specs/tasks/TASK-[feature].md, na seção
            "Tentativas" da task, o erro e a hipótese de correção
         -> tentativa = tentativa + 1
  SE tentativa > 4:
    -> PARAR. recovery.py block --goal "<goal que falhou>" --error "<erro exato>"
       --question "<a pergunta objetiva que você precisa que EU responda>"
       Ele grava outputs/BLOQUEIO-T-00X.md com o diagnóstico, o placar das 4 tentativas, as
       opções de resolução e a seção "Retomada", e volta a árvore ao portão red.
    -> Mostre ao usuário o BLOQUEIO inteiro: as opções e o comando de retomada, não só o erro.
    -> python ${CLAUDE_PLUGIN_ROOT}/scripts/status_note.py sync . --state blocked

## Retomada — `/bkhar:loop T-00X --resume`

Rode `recovery.py resume` e siga a ação que ele imprimir. Ele decide pelo estado da task:

| Estado | O que acontece |
|---|---|
| bloqueada | exige "O que mudou" preenchido no BLOQUEIO e abre o ciclo seguinte com o contador zerado, partindo de `spec` (o `tester` refaz o RED), `red` (ambos pedem commit novo no FEAT ou no TEST) ou `impl-K` (a foto daquela tentativa). O texto que ele imprime vai ao `developer` na tentativa 1 do ciclo novo. |
| em curso (houve queda) | volta ao último ponto seguro sem pedir informação; tentativa interrompida não conta, e duas quedas na mesma tentativa geram BLOQUEIO por interrupção |
| terminal (3º bloqueio) | recusa; a task volta ao `/bkhar:refine` |

Snapshot e git divergentes (outra branch, árvore suja onde não cabe) param a retomada com a
divergência na saída; não adivinhe o estado.

Dentro do Maestri, `tester` e `developer` são chamados nos terminais deles, com `/clear` antes de
cada task nova (skill `bks-team`, seção "Despacho"); fora dele, como subagentes.

Decisão que foge da FEAT volta do `developer` para esta sessão, que pergunta ao usuário antes da
próxima tentativa.

## Modo `autonomous`

Com `axes.mode: autonomous` no `.bks-profile.json`:

- Decisão que foge da FEAT não volta ao usuário: o `architect` a resolve e grava em
  `decisions/SUPOSICOES.md`, e a próxima tentativa segue. Dado pessoal, autorização e segredo
  não se presumem: geram `outputs/BLOQUEIO-[task].md`.
- O loop só para em `BLOQUEIO`, e o `BLOQUEIO` para a cadeia de tasks que depende desta, não a onda.
- Os goals, o passo 0 e o teto de 4 tentativas não mudam.

## Modo onda — `/bkhar:loop --wave N`

Roda a onda N do grafo (`--wave next` escolhe a primeira com task pendente). Só no `autonomous`: no
`collaborative`, recuse e indique o `/bkhar:mode`. A sessão principal é o orquestrador e a única
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
       recovery.py begin ../{repo}-wt/T-00X --task T-00X --base <branch de trabalho>
       FEAT e TEST pelo `/bkhar:refine` no modo `autonomous`, se faltarem; depois o LOOP-4 acima,
       com `tester` e `developer` trabalhando dentro da worktree e o `recovery.py` apontado para
       ela. Cada tentativa vai aos dois estados: `recovery.py attempt` (o teto) e
       run_state.py attempt . --task T-00X --n K (o painel)
  5. Task encerrada: run_state.py finish . --task T-00X --result passou|bloqueada [--cost USD].
     `bloqueada` gera `outputs/BLOQUEIO-[task].md` e segura só a cadeia que depende dela.
     Avise o usuário com uma notificação (a ferramenta de notificação da sessão, quando houver);
     o painel também avisa pelo navegador. Em seguida, `status_note.py sync .`: no Maestri, o
     `floor status` em `blocked` também notifica.

FIM DA ONDA:
  1. Integração: `recovery.py integrate . --task T-00X` para cada task aprovada, em ordem de id,
     na raiz do repositório (merge --no-ff na branch de trabalho). Conflito PARA a onda em
     `outputs/BLOQUEIO-onda-N.md`, com os arquivos que o `integrate` listou.
  2. Build e suíte completos na branch de trabalho, saída colada.
  3. `/bkhar:review` no modo `autonomous` sobre o diff da onda inteira.
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
editar o teste do `tester`, pular o passo 0, voltar a um ponto fora do `--resume` ou `git reset
--hard` fora da branch da task (o `secret_guard` recusa).
