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

## SQL só com parâmetro (`SEC-01`)

O mesmo arquivo barra SQL montado com texto em qualquer pasta de `src/`: template com `${...}` e
string com SQL somada a um valor (`'... = ' + id`). Passam o placeholder com array de valores
(`$1`, `?`) e o template com tag (`` sql`...` ``), que o driver parametriza. A leitura é pela árvore
do `typescript`, então comentário não conta. O limite é o do texto: a consulta montada em mais de
um comando (`q += id`) passa e fica com o `security` (`SEC-03`).

## O teste

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import ts from 'typescript';

const SRC = resolve(process.cwd(), 'src');
const ENTRY = ['routes', 'plugins', 'handlers', 'consumers', 'workers', 'processors', 'graph'];
const SQL = /\bselect\b[\s\S]+\bfrom\b|\binsert\s+into\b|\bupdate\s+[\w."[\]]+\s+set\b|\bdelete\s+from\b|\bwhere\s+\w+\s*(?:=|<>|<|>|\blike\b|\bin\b)/i;

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

function constantText(node: ts.Node): string | null {
  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) return node.text;
  if (ts.isParenthesizedExpression(node)) return constantText(node.expression);
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
    const left = constantText(node.left);
    const right = constantText(node.right);
    return left !== null && right !== null ? left + right : null;
  }
  return null;
}

function sqlBuiltFromText(file: string): number[] {
  const source = ts.createSourceFile(file, readFileSync(file, 'utf8'), ts.ScriptTarget.Latest, true);
  const lines: number[] = [];
  const visit = (node: ts.Node): void => {
    const templated = ts.isTemplateExpression(node) && !ts.isTaggedTemplateExpression(node.parent)
      && SQL.test(node.getText(source));
    let concatenated = false;
    if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
      const left = constantText(node.left);
      const right = constantText(node.right);
      concatenated = (left === null) !== (right === null) && SQL.test(left ?? right ?? '');
    }
    if (templated || concatenated) lines.push(source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1);
    ts.forEachChild(node, visit);
  };
  visit(source);
  return lines;
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

test('SQL só com parâmetro, sem texto montado', () => {
  const offenders = sourceFiles(SRC).flatMap((file) =>
    sqlBuiltFromText(file).map((line) => `${relative(SRC, file)}:${line} monta SQL com texto`));
  assert.deepEqual(offenders, []);
});
```
