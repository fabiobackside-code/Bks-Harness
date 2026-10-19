# SKILL-NEW-VERSION
> Prompt para evolução da skill `bks-typescript-backend`
> Use este prompt sempre que quiser ajustar, expandir ou corrigir o que a skill gera.

---

## Contexto

Você está evoluindo a skill **`bks-typescript-backend`**, que gera backends Node.js + TypeScript
a partir de um fluxo guiado de 5 fases.

A skill é composta por:

| Arquivo | Responsabilidade |
|---------|-----------------|
| `SKILL.md` | Agente orquestrador: registro de tipos, variáveis comuns (VC-*), variáveis específicas (VT-*), fluxo das 5 fases, exemplos de interação |
| `references/bks-api-express.md` | Prompt especializado: API REST com Express 4 + TypeScript |
| `references/bks-agent-langgraph.md` | Prompt especializado: Agente LangGraph com StateGraph + nodes |
| `references/bks-{tipo}.md` | Prompts especializados futuros (um por tipo de backend) |

---

## O que você quer mudar?

Descreva a evolução desejada em qualquer formato livre. Exemplos:

### Adicionar novo tipo de backend
```
Quero adicionar suporte ao tipo FASTIFY:
- API REST com Fastify 5 + TypeScript
- Plugins organizados por domínio
- Validação de schema com @fastify/type-provider-zod
- Autenticação via @fastify/jwt
```

Quero adicionar suporte ao tipo WORKER:
- Sugira um padrão que se adeque aos demais usados pela skill
```

Quero adicionar suporte ao tipo CONSUMER:
- Sugira um padrão que se adeque aos demais usados pela skill
```

### Modificar variável ou fase existente
```
Quero adicionar VC-6 "ORM" na Fase 2, com opções: Prisma | Drizzle | Nenhum.
Isso deve afetar o que é gerado no módulo de persistência de todos os tipos que usam banco.
```

### Corrigir padrão de código gerado
```
No tipo EXPRESS, o pattern do error handler global está incompleto.
Precisa capturar também erros de autenticação (401) separados dos erros de negócio (422).

Nem todos os projetos envolverão integração com LLMs via Anthropic ou Openrouter
```

### Adicionar restrição absoluta a um prompt especializado
```
No bks-api-express.md, adicionar restrição:
- Nunca usar `res.json()` com status implícito — sempre usar `res.status(N).json()`
```

### Alterar estrutura de pastas gerada
```
No tipo EXPRESS, mover os validators para dentro de cada rota ao invés de arquivo separado.
Novo caminho: src/routes/{módulo}/{módulo}.routes.ts (validator inline no mesmo arquivo)
```

### Adicionar feature transversal
```
Quero que todos os tipos que usam banco gerem também um docker-compose.yml
com o serviço de banco configurado (PostgreSQL, SQLServer, MongoDB ou Redis conforme VC-3).
```

---

## Instruções para o Claude

Ao receber este prompt com a descrição da evolução:

1. **Leia os arquivos atuais** da skill antes de propor qualquer mudança:
   - `SKILL.md`
   - `references/bks-api-express.md`
   - `references/bks-agent-langgraph.md`
   - Qualquer outro `references/bks-*.md` existente

2. **Identifique exatamente** quais arquivos da skill precisam ser alterados e por quê.

3. **Aponte impactos cruzados**: se uma mudança em `SKILL.md` exige mudança em um `references/bks-*.md`, ou vice-versa, liste tudo antes de editar.

4. **Proponha as alterações** de forma clara antes de aplicá-las. Aguarde confirmação se a mudança for estrutural (novo tipo, nova variável obrigatória, mudança de fluxo de fases).

5. **Aplique as edições** nos arquivos correspondentes.

6. **Reempacote** a skill:
   ```bash
   cd skill-build/bks-typescript-backend-edit
   # IMPORTANTE: usar System.IO.Compression para gerar caminhos relativos (Compress-Archive gera caminhos inválidos)
   powershell -Command "
   \$src = Get-Location
   \$dest = Join-Path (Resolve-Path '..').Path 'bks-typescript-backend.zip'
   if (Test-Path \$dest) { Remove-Item \$dest }
   Add-Type -AssemblyName System.IO.Compression.FileSystem
   \$zip = [System.IO.Compression.ZipFile]::Open(\$dest, 'Create')
   Get-ChildItem -Recurse -File | ForEach-Object {
     \$rel = \$_.FullName.Substring(\$src.Path.Length + 1).Replace('\', '/')
     [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(\$zip, \$_.FullName, \$rel) | Out-Null
   }
   \$zip.Dispose()
   "
   cp ../bks-typescript-backend.zip ../bks-typescript-backend.skill
   ```

7. **Atualize o CLAUDE.md** do repositório se a mudança alterar o propósito ou escopo da skill.

---

## Regras que nunca mudam

Independente da evolução solicitada, as seguintes regras são invioláveis em qualquer prompt especializado:

- Fluxo de 5 fases com confirmação obrigatória na Fase 4 antes de gerar código
- Nunca inventar valores — sempre perguntar quando variável não fornecida
- Nenhum arquivo gerado começa com fence markdown como primeira linha
- Variáveis de ambiente acessadas **apenas** em `src/config/config.ts`
- `process.env` nunca referenciado diretamente fora do arquivo de config
- Todos os tipos explícitos — nunca `any` sem justificativa
