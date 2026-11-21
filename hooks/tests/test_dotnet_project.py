"""Testes do guarda dotnet_project: FluentAssertions, solution .sln nova e migration existente alterada."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

H = 'hooks/scripts'
REPO = tempfile.mkdtemp(prefix='bkhar-dotnet-')
NO_REPO = tempfile.mkdtemp(prefix='bkhar-sem-git-')


def git(*args):
    subprocess.run(['git', '-C', REPO] + list(args), capture_output=True, text=True)


def put(rel, text):
    path = os.path.join(REPO, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


put('src/Api/Migrations/20240101_Init.cs', 'class Init {}')
put('src/Api/Migrations/AppDbContextModelSnapshot.cs', 'class Snap {}')
put('Legacy.sln', 'Microsoft Visual Studio Solution File')
git('init', '-q')
git('add', '-A')
git('-c', 'user.name=t', '-c', 'user.email=t@example.com', 'commit', '-q', '-m', 'base')


def run(payload):
    r = subprocess.run([sys.executable, os.path.join(H, 'dotnet_project.py')],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=20)
    out = r.stdout.strip()
    if not out:
        return 'ALLOW'
    return json.loads(out).get('hookSpecificOutput', {}).get('permissionDecision', 'ALLOW').upper()


def w(rel, content='x', name='Write', root=REPO, scope=None):
    payload = {'tool_name': name, 'cwd': root,
               'tool_input': {'file_path': os.path.join(root, *rel.split('/')), 'content': content}}
    if scope:
        payload['bkhar_scope'] = scope
    return payload


FA = '<Project><ItemGroup><PackageReference Include="FluentAssertions" Version="8.0.0" /></ItemGroup></Project>'
XUNIT = '<Project><ItemGroup><PackageReference Include="xunit" Version="2.9.3" /></ItemGroup></Project>'

cases = [
    ('FluentAssertions no csproj recusado', w('tests/A.Tests/A.Tests.csproj', FA), 'DENY'),
    ('FluentAssertions no Directory.Packages.props recusado',
     w('Directory.Packages.props', '<PackageVersion Include="FluentAssertions" Version="7.0.0" />'), 'DENY'),
    ('xunit no csproj passa', w('tests/A.Tests/A.Tests.csproj', XUNIT), 'ALLOW'),
    ('FluentAssertions recusado também no --all', w('A.csproj', FA, name='Commit', scope='all'), 'DENY'),
    ('.sln nova recusada', w('Api.sln', 'Microsoft Visual Studio Solution File'), 'DENY'),
    ('.sln existente editada passa', w('Legacy.sln', 'Microsoft Visual Studio Solution File'), 'ALLOW'),
    ('.slnx passa', w('Api.slnx', '<Solution />'), 'ALLOW'),
    ('migration existente alterada recusada', w('src/Api/Migrations/20240101_Init.cs', 'class Init { }'), 'DENY'),
    ('migration existente por Edit recusada',
     {'tool_name': 'Edit', 'cwd': REPO, 'tool_input': {
         'file_path': os.path.join(REPO, 'src', 'Api', 'Migrations', '20240101_Init.cs'),
         'old_string': 'class', 'new_string': 'sealed class'}}, 'DENY'),
    ('migration nova passa', w('src/Api/Migrations/20250101_AddIndex.cs', 'class AddIndex {}'), 'ALLOW'),
    ('snapshot do modelo passa', w('src/Api/Migrations/AppDbContextModelSnapshot.cs', 'class Snap { }'), 'ALLOW'),
    ('migration existente no --all passa',
     w('src/Api/Migrations/20240101_Init.cs', 'class Init {}', name='Commit', scope='all'), 'ALLOW'),
    ('.sln existente no --all passa', w('Legacy.sln', 'x', name='Commit', scope='all'), 'ALLOW'),
    ('.sln nova fora de repositório recusada', w('Api.sln', 'x', root=NO_REPO), 'DENY'),
    ('arquivo comum passa', w('src/Api/Program.cs', 'var app = 1;'), 'ALLOW'),
    ('payload vazio libera', {}, 'ALLOW'),
]

fail = 0
for name, payload, expect in cases:
    got = run(payload)
    ok = got == expect
    fail += (not ok)
    print('%-5s %-52s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

shutil.rmtree(REPO, ignore_errors=True)
shutil.rmtree(NO_REPO, ignore_errors=True)
print('\nfalhas:', fail)
sys.exit(1 if fail else 0)
