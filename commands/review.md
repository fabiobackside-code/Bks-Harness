---
description: Dispara o agente reviewer em invocação separada e read-only para revisão independente de segurança e conformidade.
---

Dispare o agente `reviewer` em invocação SEPARADA da sessão
de implementação — read-only, nunca quem escreveu o código revisando a si mesmo.

Argumento esperado: qual repo revisar (${BKS_VAULT}/repos/{categoria}/{projeto}). Se não informado, pergunte
antes de continuar — nunca adivinhe o projeto ativo.

Pré-requisitos:
1. O projeto tem manifesto em {repo}/.claude/multiagente.md? Se não, PARE e oriente a criar a
   partir do template `manifesto-projeto.md` antes de revisar código crítico.
   Precedência de template: `{repo}/.bks/templates/`, senao `${BKS_VAULT}/workbench/templates/`, senao `${CLAUDE_PLUGIN_ROOT}/templates/`.
2. A mudança toca alguma "Área sensível" declarada no manifesto? Se não, revisão é opcional —
   não gaste Opus revisando mudança de documentação.

Revisão de escrita — sempre que a mudança toca documentação viva (`README.md`, `ARCHITECTURE.md`,
cânone, spec, treinamento), mesmo sem área sensível e sem manifesto. Roda nesta sessão, sem o
agente `reviewer`:

1. `python ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/writing_guard.py <arquivos .md tocados>` — cole a
   saída. Achado volta para correção.
2. Leia cada arquivo pela checklist e pela nota por dimensão da skill `bks-writing`. Reporte a
   nota de cada dimensão e o total; abaixo de 45, diga o que revisar.

Contexto obrigatório para o reviewer:
- `skills/bks-standards/references/checklist-revisao-critica.md`
- Seção "Invariantes do domínio" e "Áreas sensíveis" do manifesto do projeto
- {repo}/decisions/ (não repetir achado já decidido/aceito NESTE projeto)
- Diff ou arquivos específicos da entrega (não o repo inteiro)

Saída esperada: lista de achados no formato arquivo:linha/problema/exploração/severidade, ou
declaração explícita do escopo verificado se nada foi encontrado. Crítica bloqueia a entrega —
registre em {repo}/decisions/ e devolva ao builder para correção em invocação separada.
