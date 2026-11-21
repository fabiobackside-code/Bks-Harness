"""Testes do scripts/precommit.py sobre repositórios git temporários, no layout do kit e no da cópia do projeto."""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRECOMMIT = os.path.join(ROOT, 'scripts', 'precommit.py')
GUARDS = os.path.join(ROOT, 'hooks', 'scripts')
COPY = ('precommit.py', 'secret_guard.py', 'no_dispatcher.py', 'comment_budget.py', 'dotnet_project.py', '_common.py')

AWS = 'AKIA' + 'ABCDEFGHIJKLMNOP'
ALLOW_MARK = 'bkhar-allow-' + 'secret'
results = []


def check(name, ok):
    results.append(ok)
    print('%-5s %s' % ('OK' if ok else 'FALHA', name))


def git(repo, *args, ok=True):
    r = subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=repo,
                       capture_output=True, text=True)
    if ok and r.returncode:
        raise RuntimeError(r.stderr)
    return r


def new_repo():
    repo = tempfile.mkdtemp(prefix='bkhar-precommit-')
    git(repo, 'init', '-q')
    return repo


def put(repo, rel, data, stage=True):
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = 'wb' if isinstance(data, bytes) else 'w'
    with open(path, mode, **({} if isinstance(data, bytes) else {'encoding': 'utf-8'})) as f:
        f.write(data)
    if stage:
        git(repo, 'add', rel)


def run(repo, *args, script=PRECOMMIT):
    r = subprocess.run([sys.executable, script, *args], cwd=repo, capture_output=True,
                       text=True, encoding='utf-8')
    return r.returncode, r.stdout


def scenario(name, files, expect, *args):
    repo = new_repo()
    for rel, data in files:
        put(repo, rel, data)
    code, out = run(repo, *args)
    check('%s (saída %d)' % (name, expect), code == expect)
    shutil.rmtree(repo, ignore_errors=True)
    return out


scenario('staged .env barrado', [('.env', 'DB=x\n')], 1)
scenario('certificado binário barrado', [('certs/api.pfx', b'\x30\x82\xff\x00')], 1)
scenario('credencial em appsettings barrada', [('appsettings.json', '{"Db": {"Password": "Pr0d#2026"}}')], 1)
scenario('chave AWS em código barrada', [('src/Aws.cs', 'var k = "%s";' % AWS)], 1)
out = scenario('MediatR barrado', [('src/Handler.cs', 'using MediatR;\nclass H {}\n')], 1)
check('saída nomeia arquivo e guarda', 'src/Handler.cs (no_dispatcher.py)' in out)
out = scenario('mensagem fala de commit', [('.env', 'DB=x\n')], 1)
check('mensagem diz arquivo sensível no commit', 'arquivo sensível no commit' in out)
scenario('comentário longo barrado', [('src/A.cs', '\n'.join(['// linha'] * 7) + '\nclass A {}\n')], 1)
scenario('arquivo limpo passa', [('src/Ok.cs', 'class Ok {}\n'), ('README.md', '# ok\n')], 0)
scenario('marca de exceção passa', [('tests/Fixture.cs', 'var k = "%s"; // %s\n' % (AWS, ALLOW_MARK))], 0)
scenario('.env.example passa', [('.env.example', 'DB=\n')], 0)
scenario('nada staged passa', [], 0)

repo = new_repo()
put(repo, 'src/Ok.cs', 'class Ok {}\n')
git(repo, 'commit', '-q', '-m', 'base')
put(repo, '.env', 'DB=x\n')
git(repo, 'commit', '-q', '-m', 'segredo')
check('staged vazio depois do commit passa', run(repo)[0] == 0)
check('--all acha o .env já commitado', run(repo, '--all')[0] == 1)
git(repo, 'rm', '-q', '--cached', '.env')
check('remoção staged não é conferida', run(repo)[0] == 0)
shutil.rmtree(repo, ignore_errors=True)

scenario('FluentAssertions no csproj barrado',
         [('tests/A.Tests.csproj', '<PackageReference Include="FluentAssertions" Version="8.0.0" />\n')], 1)
scenario('.sln nova barrada', [('Api.sln', 'Microsoft Visual Studio Solution File\n')], 1)
repo = new_repo()
put(repo, 'src/Migrations/20240101_Init.cs', 'class Init {}\n')
git(repo, 'commit', '-q', '-m', 'base')
put(repo, 'src/Migrations/20240101_Init.cs', 'class Init { }\n')
check('migration existente alterada barrada', run(repo)[0] == 1)
git(repo, 'commit', '-q', '--no-verify', '-m', 'alterada')
check('--all não acusa migration já no histórico', run(repo, '--all')[0] == 0)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
gdir = os.path.join(repo, '.bkhar', 'guards')
os.makedirs(gdir)
for name in COPY:
    shutil.copy(os.path.join(GUARDS if name != 'precommit.py' else os.path.dirname(PRECOMMIT), name), gdir)
hooks = os.path.join(repo, '.githooks')
os.makedirs(hooks)
with open(os.path.join(hooks, 'pre-commit'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('#!/bin/sh\nexec "%s" .bkhar/guards/precommit.py\n' % sys.executable.replace('\\', '/'))
os.chmod(os.path.join(hooks, 'pre-commit'), 0o755)
git(repo, 'config', 'core.hooksPath', '.githooks')
git(repo, 'add', '.bkhar', '.githooks')
check('cópia do projeto: commit limpo passa pelo hook', git(repo, 'commit', '-q', '-m', 'base', ok=False).returncode == 0)
put(repo, 'appsettings.json', '{"Db": {"Password": "Pr0d#2026"}}')
r = git(repo, 'commit', '-q', '-m', 'segredo', ok=False)
check('cópia do projeto: commit com credencial recusado pelo hook', r.returncode != 0)
check('cópia do projeto: recusa vem do guarda copiado', 'secret_guard.py' in r.stdout + r.stderr)
check('cópia do projeto: --no-verify pula o hook', git(repo, 'commit', '-q', '--no-verify', '-m', 'x', ok=False).returncode == 0)
check('cópia do projeto: --all pega o que pulou o hook',
      run(repo, '--all', script=os.path.join(gdir, 'precommit.py'))[0] == 1)
shutil.rmtree(repo, ignore_errors=True)

fail = results.count(False)
print('\n%d verificacoes, %d falhas' % (len(results), fail))
sys.exit(1 if fail else 0)
