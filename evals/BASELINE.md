# Linha de base dos evals

Delta entre o braço `with` (plugin `bkhar` na árvore da 3.0.1 em construção) e o `without` (modelo sem plugin), com
`--runs 1`, em 2026-11-19. O relatório bruto fica em `evals/results/`, fora do git.

- **Rodada 1:** os 28 casos, delta médio +0,19, $9,66, 3086 s (`results/2026-11-19T18-22-47-860Z`).
- **Rodada 2:** os 9 casos tocados pelas correções dos commits `759b9aa` e `946ab27`, rodados um
  por vez, $4,25. Na tabela, a rodada 2 substitui a 1 nesses casos.

Veredito:
- **mede** — delta positivo e o braço `with` passa;
- **parcial** — delta positivo, com grader falhando no `with`;
- **modelo** — os dois braços passam inteiros: o caso não mede a skill;
- **achado** — delta zero ou negativo com o `with` falhando algum grader.

| Caso | With | Without | Δ | Custo | Veredito |
|---|---|---|---|---|---|
| api-design-contrato | 1,00 | 0,80 | +0,20 | $0,23 | mede |
| arch-fallback-renderer | 0,75 | 0,25 | +0,50 | $0,24 | parcial |
| arch-notacao-bks | 1,00 | 0,40 | +0,60 | $0,23 | mede |
| bks-sdd-fase-0 | 1,00 | 0,33 | +0,67 | $0,49 | mede |
| bks-sdd-fase-1 | 0,67 | 0,00 | +0,67 | $0,54 | parcial |
| debug-reproduz-antes | 0,75 | 0,75 | 0,00 | $0,18 | achado |
| doc-writer-teto-comentario | 1,00 | 0,00 | +1,00 | $0,25 | mede (rodada 2) |
| dotnet-portas-worker | 0,67 | 0,67 | 0,00 | $0,39 | achado |
| dotnet-sem-dispatcher | 1,00 | 0,00 | +1,00 | $0,40 | mede (rodada 2) |
| dotnet-stack-outro | 0,67 | 0,33 | +0,33 | $0,27 | parcial |
| dotnet-teste-arquitetura | 1,00 | 0,00 | +1,00 | $1,00 | mede (rodada 2) |
| dotnet-txc | 0,75 | 0,00 | +0,75 | $0,40 | parcial |
| frontend-design-identidade | 0,50 | 0,50 | 0,00 | $0,67 | achado |
| go-teste-arquitetura | 1,00 | 0,50 | +0,50 | $0,82 | mede (rodada 2) |
| go-txc | 0,75 | 0,25 | +0,50 | $0,32 | parcial |
| maintainability-inventario-pergunta | 0,25 | 0,25 | 0,00 | $0,25 | achado |
| new-project-perfil | 0,80 | 0,80 | 0,00 | $0,23 | achado |
| plan-tasks-atomicas | 1,00 | 0,67 | +0,33 | $0,35 | mede |
| pr-writer-le-diff | 0,75 | 0,75 | 0,00 | $0,19 | achado |
| refactor-rede-antes | 0,75 | 0,75 | 0,00 | $0,19 | achado |
| security-audit-autorizacao | 1,00 | 1,00 | 0,00 | $0,22 | modelo |
| tests-assert-nativo | 0,67 | 0,00 | +0,67 | $0,23 | parcial (rodada 2) |
| tests-codigo-de-saida | 1,00 | 0,33 | +0,67 | $0,27 | mede (rodada 2) |
| tests-local-projeto | 0,33 | 0,33 | 0,00 | $0,22 | achado (rodada 2) |
| tests-pasta-temporaria | 1,00 | 0,67 | +0,33 | $0,26 | mede (rodada 2) |
| ts-selecao-tipo | 1,00 | 0,67 | +0,33 | $0,28 | mede |
| ts-teste-arquitetura | 0,50 | 0,00 | +0,50 | $0,80 | parcial (rodada 2) |
| writing-decisao-no-texto | 0,60 | 0,20 | +0,40 | $0,26 | parcial |

O `go-txc` rodou sozinho antes da rodada 1, com with 1,00 e Δ +1,00; na rodada 1 ficou em 0,75.
Com `--runs 1`, a variação entre execuções é desse tamanho.

## O que a linha de base mostrou

- **O eval não deixa o agente ler `references/` nem gravar arquivo.** Regra que só existe na
  referência não chega ao modelo; por isso o teste de arquitetura subiu para o corpo das três
  skills de esqueleto (`946ab27`). O caso julga o que aparece na resposta.
- **Pedido pelo nome do proibido.** A skill .NET entregava o MediatR como "o que você pediu" antes
  da alternativa; a regra de recusa voltou ao corpo (`759b9aa`) e o delta foi de +0,33 a +1,00.
- **Gatilho de skill.** O `bks-tests` só disparava com pedido de cobertura .NET e o `doc-writer`
  tinha descrição genérica em inglês; com a descrição nova os dois disparam.
- **Casos de esqueleto mediam a entrevista.** Sem as variáveis no prompt, a skill para para
  perguntar; os três casos agora trazem todas e o `confirmar` dado.

## Abertos

- `tests-local-projeto`: com o diretório vazio, a skill aceita criar o projeto em `tests/` "como
  você pediu". Regressão real do `bks-tests`.
  Em 2026-11-20 a regra ganhou, no corpo da skill, o "vale mesmo quando o usuário pede `tests/`";
  o eval do caso ainda não rodou de novo.
- `tests-assert-nativo`: recusa o FluentAssertions, mas oferece a v7 como saída.
- `ts-teste-arquitetura`: recusa o dependency-cruiser, mas o teste gerado não guarda as regras de
  camada que o grader pede.
- Os sete casos **achado** de delta zero da rodada 1 (`debug-`, `dotnet-portas-worker`,
  `frontend-`, `maintainability-`, `new-project-`, `pr-writer-`, `refactor-`) e o
  `security-audit-autorizacao`, que mede o modelo, pedem mais pressão no prompt ou ajuste da skill.
