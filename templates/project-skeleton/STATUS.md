# STATUS — {{PROJETO}}

> Ponto de entrada do projeto. Leia só este arquivo para saber onde as coisas estão e o que fazer
> a seguir. Atualizado pelo `/bkhar:save` ao fim de cada sessão; lido pelo `/bkhar:brain`.
>
> Última atualização: {{DATA}}

---

## Em uma frase

{{Uma frase que diz onde o projeto está. Não o que ele é — onde ele está.}}

---

## Fase atual

**{{Fase}}** — {{o que caracteriza esta fase e o que a encerra}}

---

## O que trava

{{O que impede o próximo passo. Se nada trava, escreva "Nada trava." e siga.}}

| Bloqueio | Espera | Quem destrava |
|---|---|---|
| {{o que está parado}} | {{decisão, pessoa, evento}} | {{quem}} |

Bloqueio resolvido sai daqui e vira entrada no `JOURNAL.md`. Este quadro mostra o que trava
**agora**, não o que já travou.

---

## Próximo passo

{{Uma ação concreta, executável agora. Não um tema, não uma área — uma ação.}}

{{Se há vários caminhos possíveis, diga por onde começar e por quê. Ordem de construção vale mais
que lista de tarefas.}}

---

## Decisões que valem

{{O que já foi decidido e não se reabre sem motivo novo. Existe para que a próxima sessão não
gaste tempo rediscutindo o que já está fechado.}}

| # | Decisão | Onde |
|---|---|---|
| 1 | {{a decisão, em uma linha}} | {{ADR-NNN ou documento}} |

Toda linha aponta para onde a decisão está registrada com contexto. Decisão sem referência é
memória — e memória não sobrevive a duas semanas.

---

## Aberto

{{O que ficou pendente e não trava o próximo passo. Lista curta; o que envelhece sem virar
trabalho sai daqui.}}

---

## Mapa dos documentos

{{Onde cada coisa está, para que a próxima sessão encontre sem procurar.}}

| Documento | Para que |
|---|---|
| este arquivo | onde parei, o que trava, próximo passo |
| `WORKFLOW.md` | o fluxo de comandos deste projeto |
| `JOURNAL.md` | marcos e sessões, do mais recente ao mais antigo |
| `decisions/` | as decisões, com contexto e alternativas descartadas |
| `specs/` | features, cenários de teste, tasks |
| `docs/canonical/` | contexto consolidado — a fonte após o `/bkhar:canonize` |
| `docs/input/` | material bruto ainda não consolidado |
| `brain/domain/` | o que o produto é — regra de negócio, método, normativo |
| `brain/engineering/` | como se constrói aqui — padrão técnico deste projeto |

{{Acrescente os documentos próprios do projeto que a próxima sessão precisa achar.}}
