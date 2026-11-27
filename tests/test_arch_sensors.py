"""Prova dos testes de arquitetura dos esqueletos: limpo passa, violação plantada é barrada.

Extrai o código de skills/bks-*-solutions/references/architecture-tests.md para um projeto mínimo
temporário e roda o teste da stack (dotnet test, node --test, go test). Stack sem toolchain é
pulada com aviso. Lento: rode quando mexer nessas referências.

Uso: python tests/test_arch_sensors.py [dotnet|ts|go]
"""
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = []
checks = 0
skipped = []


def check(name, condition, detail=''):
    global checks
    checks += 1
    if condition:
        print('  ok    %s' % name)
    else:
        print('  FALHA %s' % name)
        if detail:
            print('          %s' % detail[-1500:])
        failures.append(name)


def code_block(skill, lang):
    path = os.path.join(ROOT, 'skills', skill, 'references', 'architecture-tests.md')
    with io.open(path, encoding='utf-8') as fh:
        text = fh.read()
    m = re.search(r'```%s\n(.*?)```' % lang, text, re.S)
    return m.group(1)


def write(root, rel, text):
    path = os.path.join(root, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def run(cmd, cwd, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       timeout=timeout, shell=(os.name == 'nt'))
    return r.returncode, r.stdout + r.stderr


def _rm(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def prove(stack, files, cmd, violations, first_cmd=None):
    root = tempfile.mkdtemp(prefix='bkhar-arch-%s-' % stack)
    try:
        for rel, text in files.items():
            write(root, rel, text)
        code, out = run(first_cmd or cmd, root)
        check('%s: projeto limpo passa' % stack, code == 0, out)
        if code != 0:
            return
        for name, (rel, text, marker) in violations.items():
            original = files.get(rel)
            write(root, rel, text)
            code, out = run(cmd, root)
            check('%s: %s barrada' % (stack, name), code != 0 and marker in out, out)
            if original is None:
                os.remove(os.path.join(root, *rel.split('/')))
            else:
                write(root, rel, original)
    finally:
        shutil.rmtree(root, onerror=_rm)


CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.14.1" />
    <PackageReference Include="xunit" Version="2.9.3" />
    <PackageReference Include="xunit.runner.visualstudio" Version="3.1.4" />
  </ItemGroup>
  <ItemGroup>
    <Using Include="Xunit" />
  </ItemGroup>
</Project>
'''

ORDER = 'namespace Shop.Domain.Core.Models;\n\npublic sealed record Order(string Id);\n'
SERVICE = ('using Shop.Domain.Core.Models;\n\nnamespace Shop.Domain.Services;\n\n'
           'public sealed class OrderService\n{\n    public Order Create(string id) => new(id);\n}\n')
ENDPOINT = ('using Shop.Domain.Services;\n\nnamespace Shop.Adapters.Inbound.HttpAdapter;\n\n'
            'public sealed class OrderEndpoint(OrderService service)\n{\n'
            '    public string Post(string id) => service.Create(id).Id;\n}\n')
REPOSITORY = ('using Npgsql;\nusing Shop.Domain.Core.Models;\n\nnamespace Shop.Adapters.Outbound.PostgresAdapter;\n\n'
              'public sealed class OrderRepository\n{\n'
              '    private const string Insert = "INSERT INTO orders (id) VALUES (@id)";\n'
              '    private const string Find = "SELECT id " +\n        "FROM orders WHERE id = @id";\n'
              '    private const string Raw = \"\"\"\n        SELECT id FROM orders WHERE id = @id\n        \"\"\";\n\n'
              '    // SELECT id FROM orders WHERE id = \' + id\n'
              '    public void Save(Order order) { }\n\n'
              '    public int Delete(OrderContext db, string id) =>\n'
              '        db.Database.ExecuteSqlInterpolated($"DELETE FROM orders WHERE id = {id}");\n\n'
              '    public string Log(string id) => $"order {id} saved";\n}\n')
STEP = ('using System.Diagnostics;\n\nnamespace Shop.Application.Pipeline;\n\npublic abstract class BksStep\n{\n'
        '    private static readonly ActivitySource Source = new("Shop");\n\n'
        '    protected Activity? Start(string name) => Source.StartActivity(name);\n}\n')


def test_dotnet():
    print('\n.NET: LayerDependencyTests')
    if not shutil.which('dotnet'):
        skipped.append('dotnet')
        return
    test = code_block('bks-dotnet-solutions', 'csharp').replace('{ServiceName}', 'Shop')
    files = {'Shop.slnx': '<Solution />\n', 'src/Shop.Tests/Shop.Tests.csproj': CSPROJ,
             'src/Shop.Tests/Architecture/LayerDependencyTests.cs': test,
             'src/Shop/Domain/Core/Models/Order.cs': ORDER, 'src/Shop/Domain/Services/OrderService.cs': SERVICE,
             'src/Shop/Adapters/Inbound/HttpAdapter/OrderEndpoint.cs': ENDPOINT,
             'src/Shop/Adapters/Outbound/PostgresAdapter/OrderRepository.cs': REPOSITORY,
             'src/Shop/Application/Pipeline/BksStep.cs': STEP}
    project = 'src/Shop.Tests/Shop.Tests.csproj'
    violations = {
        'COD-04 using Npgsql no Domain': ('src/Shop/Domain/Core/Models/Order.cs', 'using Npgsql;\n' + ORDER,
                                          'Domain_references_only_System'),
        'COD-05 Domain usando adapter': ('src/Shop/Domain/Services/OrderService.cs',
                                         'using Shop.Adapters.Outbound.PostgresAdapter;\n' + SERVICE,
                                         'Layers_depend_inward'),
        'COD-05 entrada citando a saída por nome qualificado': (
            'src/Shop/Adapters/Inbound/HttpAdapter/OrderEndpoint.cs',
            ENDPOINT.replace('public string Post', 'private readonly Shop.Adapters.Outbound.PostgresAdapter.'
                                                   'OrderRepository _repo = new();\n    public string Post'),
            'Layers_depend_inward'),
        'COD-07 Activity à mão no serviço': (
            'src/Shop/Domain/Services/OrderService.cs',
            SERVICE.replace('public Order Create', 'public object Trace() => new System.Diagnostics.Activity("x");\n'
                                                   '    public Order Create'),
            'Spans_come_from_the_pipeline'),
        'COD-13 dynamic': ('src/Shop/Domain/Services/OrderService.cs',
                           SERVICE.replace('public Order Create', 'public dynamic Any() => 1;\n    public Order Create'),
                           'No_dynamic'),
        'SEC-01 SQL interpolado': (
            'src/Shop/Adapters/Outbound/PostgresAdapter/OrderRepository.cs',
            REPOSITORY.replace('public void Save', 'public string ById(string id) =>\n'
                               '        $"SELECT id FROM orders WHERE id = \'{id}\'";\n\n    public void Save'),
            'Sql_takes_only_parameters'),
        'SEC-01 SQL concatenado': (
            'src/Shop/Adapters/Outbound/PostgresAdapter/OrderRepository.cs',
            REPOSITORY.replace('public void Save', 'public string ById(string id) =>\n'
                               '        "SELECT id FROM orders WHERE id = \'" + id + "\'";\n\n    public void Save'),
            'Sql_takes_only_parameters'),
        'SEC-01 SQL no string.Format': (
            'src/Shop/Adapters/Outbound/PostgresAdapter/OrderRepository.cs',
            REPOSITORY.replace('public void Save', 'public string ById(string id) =>\n'
                               '        string.Format("DELETE FROM orders WHERE id = \'{0}\'", id);\n\n    public void Save'),
            'Sql_takes_only_parameters'),
    }
    prove('dotnet', files, ['dotnet', 'test', project, '--no-build', '--nologo'], violations,
          first_cmd=['dotnet', 'test', project, '--nologo'])


TS_FILES = {
    'package.json': '{"type": "module", "private": true}\n',
    'src/types/order.types.ts': 'export interface Order { id: string }\n',
    'src/modules/order/order.service.ts': ("import type { Order } from '../../types/order.types.ts';\n"
                                           "import { save } from './order.repository.ts';\n"
                                           "export const create = (id: string): Order => save({ id });\n"),
    'src/modules/order/order.repository.ts': ("import pg from 'pg';\n"
                                              "const sql = (s: TemplateStringsArray, ...v: unknown[]) => ({ s, v });\n"
                                              "export const insert = 'INSERT INTO orders (id) VALUES ($1)';\n"
                                              "export const find = (id: string) => ['SELECT id ' + 'FROM orders WHERE id = $1', [id]];\n"
                                              "export const byTag = (id: string) => sql`SELECT id FROM orders WHERE id = ${id}`;\n"
                                              "// SELECT id FROM orders WHERE id = ' + id\n"
                                              "export const log = (id: string) => `order ${id} saved`;\n"
                                              "export const save = <T>(o: T): T => o;\n"),
    'src/routes/order.routes.ts': "import { create } from '../modules/order/order.service.ts';\nexport const r = create;\n",
}


def test_ts():
    print('\nTypeScript: architecture.test.ts')
    if not shutil.which('node') or not shutil.which('npm'):
        skipped.append('ts')
        return
    files = dict(TS_FILES)
    files['tests/architecture.test.ts'] = code_block('bks-typescript-solutions', 'ts')
    root = tempfile.mkdtemp(prefix='bkhar-arch-tsdeps-')
    code, out = run(['npm', 'install', 'typescript@5', '--no-audit', '--no-fund', '--silent',
                     '--prefix', root], ROOT, timeout=300)
    if code != 0:
        skipped.append('ts (npm install typescript falhou)')
        shutil.rmtree(root, onerror=_rm)
        return
    deps = os.path.join(root, 'node_modules')
    violations = {
        'domínio importando pacote de fora': ('src/types/order.types.ts',
                                              "import { z } from 'zod';\n" + TS_FILES['src/types/order.types.ts'],
                                              'importa zod'),
        'domínio importando modules': ('src/types/order.types.ts',
                                       "import { create } from '../modules/order/order.service.ts';\n"
                                       + TS_FILES['src/types/order.types.ts'], 'order.service'),
        'modules importando a entrada': ('src/modules/order/order.service.ts',
                                         "import { r } from '../../routes/order.routes.ts';\n"
                                         + TS_FILES['src/modules/order/order.service.ts'], 'order.routes'),
        'entrada importando repository': ('src/routes/order.routes.ts',
                                          "import { save } from '../modules/order/order.repository.ts';\n"
                                          + TS_FILES['src/routes/order.routes.ts'], 'order.repository'),
        'SEC-01 SQL em template': ('src/modules/order/order.repository.ts',
                                   TS_FILES['src/modules/order/order.repository.ts']
                                   + "export const byId = (id: string) => `SELECT id FROM orders WHERE id = '${id}'`;\n",
                                   'monta SQL com texto'),
        'SEC-01 SQL concatenado': ('src/modules/order/order.repository.ts',
                                   TS_FILES['src/modules/order/order.repository.ts']
                                   + "export const byId = (id: string) => 'SELECT id ' + 'FROM orders WHERE id = ' + id;\n",
                                   'monta SQL com texto'),
    }
    cmd = ['node', '--test', 'tests/architecture.test.ts']
    fixture = tempfile.mkdtemp(prefix='bkhar-arch-ts-')
    try:
        for rel, text in files.items():
            write(fixture, rel, text)
        shutil.copytree(deps, os.path.join(fixture, 'node_modules'))
        code, out = run(cmd, fixture)
        check('ts: projeto limpo passa', code == 0, out)
        for name, (rel, text, marker) in violations.items():
            write(fixture, rel, text)
            code, out = run(cmd, fixture)
            check('ts: %s barrada' % name, code != 0 and marker in out, out)
            write(fixture, rel, files[rel])
    finally:
        shutil.rmtree(fixture, onerror=_rm)
        shutil.rmtree(root, onerror=_rm)


GO_FILES = {
    'go.mod': 'module example.com/shop\n\ngo 1.24\n',
    'internal/order/order.go': 'package order\n\ntype Order struct{ ID string }\n',
    'internal/order/port.go': 'package order\n\ntype Store interface{ Save(Order) error }\n',
    'internal/adapter/http/handler.go': 'package http\n\nimport _ "example.com/shop/internal/order"\n',
    'internal/adapter/postgres/store.go': ('package postgres\n\nimport _ "example.com/shop/internal/order"\n\n'
                                           'const insert = "INSERT INTO orders (id) VALUES ($1)"\n\n'
                                           'const find = "SELECT id " + "FROM orders WHERE id = $1"\n\n'
                                           '// SELECT id FROM orders WHERE id = \' + id\n'
                                           'func label(id string) string { return "order " + id }\n'),
    'internal/platform/config/config.go': 'package config\n',
}


def test_go():
    print('\nGo: architecture_test.go')
    if not shutil.which('go'):
        skipped.append('go')
        return
    files = dict(GO_FILES)
    files['internal/architecture_test.go'] = code_block('bks-go-solutions', 'go')
    violations = {
        'COD-05 contexto importando adapter': (
            'internal/order/order.go',
            'package order\n\nimport _ "example.com/shop/internal/adapter/postgres"\n\ntype Order struct{ ID string }\n',
            'TestContextsDoNotImportAdapters'),
        'COD-05 entrada importando a saída': (
            'internal/adapter/http/handler.go',
            'package http\n\nimport _ "example.com/shop/internal/adapter/postgres"\n',
            'TestAdaptersDoNotImportEachOther'),
        'COD-19 Result[T]': ('internal/order/result.go', 'package order\n\ntype Result[T any] struct{ V T }\n',
                             'TestNoGenericResult'),
        'SEC-01 SQL no Sprintf': (
            'internal/adapter/postgres/query.go',
            'package postgres\n\nimport "fmt"\n\n'
            'func byID(id string) string { return fmt.Sprintf("SELECT id FROM orders WHERE id = \'%s\'", id) }\n',
            'TestSqlTakesOnlyParameters'),
        'SEC-01 SQL concatenado': (
            'internal/adapter/postgres/query.go',
            'package postgres\n\nfunc byID(id string) string { return "SELECT id FROM orders WHERE id = \'" + id + "\'" }\n',
            'TestSqlTakesOnlyParameters'),
    }
    prove('go', files, ['go', 'test', './internal/'], violations)


def main():
    print('prova dos testes de arquitetura')
    only = sys.argv[1:]
    for key, fn in (('dotnet', test_dotnet), ('ts', test_ts), ('go', test_go)):
        if not only or key in only:
            try:
                fn()
            except Exception as exc:
                check('%s sem exceção' % key, False, repr(exc))
    for s in skipped:
        print('  PULADO %s: toolchain ausente' % s)
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
