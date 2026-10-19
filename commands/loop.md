---
description: LOOP-4 — implementa uma task sob goals verificáveis (build limpo, testes verdes, cenários cobertos) em no máximo 4 tentativas.
---

# LOOP-4 — Implementação com Goals (máx 4 tentativas)

GOAL padrão (ajuste por task):
  G1. dotnet build sem erros e sem warnings novos
  G2. dotnet test 100% verde
  G3. todos os cenários do TEST-[feature].md cobertos
  G4. código respeita brain/engineering/ do projeto (calisthenics + hexagonal)

PROTOCOLO:
  tentativa = 1
  ENQUANTO tentativa <= 4:
    1. Implementar/corrigir a task atual
    2. Executar: dotnet build ; dotnet test
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

PROIBIDO: 5ª tentativa, relaxar o goal, ou marcar como concluído
com teste falhando.
