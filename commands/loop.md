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

Decisão que foge da FEAT volta do `developer` para esta sessão, que pergunta ao usuário antes da
próxima tentativa.

PROIBIDO: 5ª tentativa, relaxar o goal, marcar como concluído com teste falhando, o `developer`
editar o teste do `tester`, ou pular o passo 0.
