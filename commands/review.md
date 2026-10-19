---
description: Revisão em painel — tester, quality e, em área sensível, security revisam a entrega em invocações separadas e read-only. Cada achado vira bloqueante, sugestão ou aprendizado.
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
| `security` | quando o diff toca "Área sensível" do manifesto | dado sensível, autorização, log, segredo, zona de contenção |
| `architect` | quando o diff cruza fronteira de contexto ou premissa | fronteira, contrato, padrão |

O `tester` não revisa os próprios testes: a força das asserções e a fragilidade são do `quality`.

Pré-requisitos:
1. O projeto tem manifesto em {repo}/.claude/multiagente.md? Se não, `tester` e `quality` rodam;
   `security` não roda, e oriente a criar o manifesto a partir do template `manifesto-projeto.md`.
   Precedência de template: `{repo}/.bks/templates/`, senao `${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`.
2. A mudança toca alguma "Área sensível" declarada no manifesto? Se não, `security` não roda —
   não gaste Opus revisando mudança de documentação.

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
