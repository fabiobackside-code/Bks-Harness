# Manifesto multi-agente — template BKS

Copie para `{repo}/.claude/multiagente.md` e preencha ao marcar um projeto como
**Alto** ou **Crítico** (campo `criticidade` no `STATUS.md` do projeto).
Sem manifesto preenchido, não paralelize — não delegue a `/bkhar:review` obrigatória.
Curto de propósito: é lido em toda delegação, cada linha inútil custa token em toda sessão futura.

---

```markdown
# Manifesto multi-agente — <PROJETO>

**Criticidade:** Crítico | Alto | Padrão
**Atualizado:** <data>

## Comandos de verificação
- Build: `dotnet build`
- Teste: `dotnet test`
- E2E (se houver): `<comando + pré-requisitos>`

## Zonas de contenção
Exclusivas do orquestrador — subagentes descrevem, não editam:

| Arquivo | Por quê |
|---|---|
| `Program.cs` (Composition Root) | Todo registro de feature/adapter passa aqui |
| `{Feature}/{Operação}/*Steps.cs` do Pipeline Orchestrator | Toda operação registra estágios aqui |
| `db/migrations/NNN_*` | Numeração colide |
| `decisions/ADR-NNN.md` | Numeração ADR-NNN colide |
| `specs/tasks/` | Numeração TASK-NNN colide |
| `STATUS.md` | Reescrito por inteiro pelo `/bkhar:save` — dois agentes se sobrescrevem |
| mocks/fixtures compartilhados de teste | Dois agentes editando a mesma struct |

## Recursos numerados compartilhados
Reservar ANTES de qualquer fan-out. A fonte da verdade é o repositório, não a spec:
```bash
ls db/migrations/ | tail -1
ls decisions/ | tail -1
ls specs/tasks/ | tail -1
```

## Zonas paralelizáveis
Dois agentes só ao mesmo tempo se cada um ficar inteiramente dentro de:
- `Features/{ContextoA}/` vs `Features/{ContextoB}/` (bounded contexts distintos)
- `FEAT-*.md`/`TEST-*.md` de features distintas em `specs/`

## Áreas sensíveis — revisão independente obrigatória (`/bkhar:review`)
- Autenticação/autorização (`Identidade/`, JWT, RBAC)
- Qualquer código que mova dinheiro, altere saldo ou grava contábil (TXC: `DataContabil`, `Nsu`)
- Isolamento entre tenants/inquilinos (`InquilinoId` no TXC)
- Dado pessoal/regulado (LGPD)
- Assinatura/validação de webhook, integração TCP externa

## Invariantes do domínio (o `security` verifica explicitamente)
- Zero `float`/`double` em campo monetário — sempre `decimal`
- Idempotência por CONSTRAINT de banco, nunca só checagem em código
- Toda query filtra por `InquilinoId`/`tenant` — sem exceção, inclusive agregados/relatórios
- TXC é lido, nunca mutado pela aplicação
- `<invariantes específicas deste projeto>`

## Perfis disponíveis
Vêm do plugin `bkhar`, invocados pelo nome. O Gerente, que conduz os ritos, é a sessão principal
seguindo a skill `bks-team`.

| Perfil | Invocação | Para que |
|---|---|---|
| architect | `bkhar:architect` | padrão, FEAT, TASK e ADR; nunca código |
| tester | `bkhar:tester` | TEST e o RED em código, antes da implementação |
| developer | `bkhar:developer` | implementa uma tentativa do LOOP-4 por vez |
| security | `bkhar:security` | revisão de segurança read-only, invocação separada |
| quality | `bkhar:quality` | legibilidade, arquivos de teste, casos para o `LEARNINGS.md` |
| scribe | `bkhar:scribe` | ADR de painel e doc de trabalho já verificado |

## Convenções — aponte, não repita
- Quem é o usuário: `workbench/profile.md`, no vault
- Padrão técnico geral: skill `bks-standards` do kit
- .NET: skill `bks-dotnet-solutions` · Testes: skill `bks-tests`
- Padrões transversais (TXC e outros): `knowledge/wiki/patterns/`, no vault
- Como se constrói NESTE projeto: `{repo}/brain/engineering/`
- O que o produto É: `{repo}/brain/domain/`
```

## Como descobrir zonas de contenção (se ainda não souber)
```bash
git log --format="" --name-only -n 100 | sort | uniq -c | sort -rn | head -20
```
Arquivo que aparece sempre pelo mesmo motivo (append de registro, numeração, wiring) é zona de
contenção. Arquivo grande que muda por motivos variados é só um arquivo grande.
