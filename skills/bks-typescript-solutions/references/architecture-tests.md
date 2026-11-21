# Teste de arquitetura das camadas

> Gerado junto com o código, em `tests/architecture.test.ts`, e rodado pelo `npm test`
> (`node --test`). Sem pacote novo: o teste usa o `typescript` que o projeto já tem para listar os
> imports de cada arquivo.

## O que ele guarda (`COD-05`)

O layout dos templates não tem pastas com o nome das camadas; a direção se traduz assim:

| Camada | Pastas em `src/` | Não importa |
|---|---|---|
| Domínio | `types/` | nenhuma outra pasta de `src/` e nenhum pacote de fora |
| Aplicação | `modules/` | as pastas de entrada |
| Entrada | `routes/`, `plugins/`, `handlers/`, `consumers/`, `workers/`, `processors/`, `graph/` | arquivo `*.repository.ts`: a entrada chama o serviço, nunca o acesso a dados |

Import relativo e por alias (`@/modules/...`) entram na conta. Arquivo de teste fica fora.

## O teste

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import ts from 'typescript';

const SRC = resolve(process.cwd(), 'src');
const ENTRY = ['routes', 'plugins', 'handlers', 'consumers', 'workers', 'processors', 'graph'];

function sourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) return sourceFiles(full);
    return name.endsWith('.ts') && !name.endsWith('.test.ts') ? [full] : [];
  });
}

function layerOf(path: string): string {
  return relative(SRC, path).split(sep)[0];
}

function imports(file: string): { spec: string; target: string | null }[] {
  const info = ts.preProcessFile(readFileSync(file, 'utf8'), true, true);
  return info.importedFiles.map(({ fileName: spec }) => {
    if (spec.startsWith('.')) return { spec, target: resolve(dirname(file), spec) };
    if (spec.startsWith('@/')) return { spec, target: resolve(SRC, spec.slice(2)) };
    return { spec, target: null };
  });
}

test('domínio em types/ não importa outra camada nem pacote de fora', () => {
  const offenders = sourceFiles(SRC)
    .filter((file) => layerOf(file) === 'types')
    .flatMap((file) => imports(file)
      .filter(({ spec, target }) => (target === null ? !spec.startsWith('node:') : layerOf(target) !== 'types'))
      .map(({ spec }) => `${relative(SRC, file)} importa ${spec}`));
  assert.deepEqual(offenders, []);
});

test('modules/ não importa a entrada', () => {
  const offenders = sourceFiles(SRC)
    .filter((file) => layerOf(file) === 'modules')
    .flatMap((file) => imports(file)
      .filter(({ target }) => target !== null && ENTRY.includes(layerOf(target)))
      .map(({ spec }) => `${relative(SRC, file)} importa ${spec}`));
  assert.deepEqual(offenders, []);
});

test('a entrada não importa repository direto', () => {
  const offenders = sourceFiles(SRC)
    .filter((file) => ENTRY.includes(layerOf(file)))
    .flatMap((file) => imports(file)
      .filter(({ target }) => target !== null && /\.repository(\.ts)?$/.test(target))
      .map(({ spec }) => `${relative(SRC, file)} importa ${spec}`));
  assert.deepEqual(offenders, []);
});
```
