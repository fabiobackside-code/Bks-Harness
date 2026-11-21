"""Testes do guarda secret_guard: leitura de segredo, segredo escrito, apagar em massa e escrita fora do permitido."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

H = 'hooks/scripts'
PROJECT = tempfile.mkdtemp(prefix='bkhar-proj-', dir=os.path.expanduser('~'))
OTHER = os.path.join(os.path.dirname(PROJECT), 'outro-projeto')
EXTRA = os.path.join(os.path.dirname(PROJECT), 'raiz-extra')

AWS = 'AKIA' + 'ABCDEFGHIJKLMNOP'
GH = 'ghp_' + 'a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8'
ANT = 'sk-ant-' + 'api03-abcdefghijklmnopqrstuvwxyz'
PEM = '-----BEGIN ' + 'RSA PRIVATE KEY-----\nMIIE\n-----END RSA PRIVATE KEY-----'
ALLOW_MARK = 'bkhar-allow-' + 'secret'


def run(payload, env=None):
    r = subprocess.run([sys.executable, os.path.join(H, 'secret_guard.py')],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=20,
                       env=env)
    out = r.stdout.strip()
    if not out:
        return 'ALLOW'
    return json.loads(out).get('hookSpecificOutput', {}).get('permissionDecision', 'ALLOW').upper()


def tool(name, **ti):
    return {'tool_name': name, 'cwd': PROJECT, 'tool_input': ti}


def bash(command, name='Bash'):
    return tool(name, command=command)


def write(path, content='x', name='Write'):
    return tool(name, file_path=path, content=content)


def edit(path, new):
    return tool('Edit', file_path=path, old_string='a', new_string=new)


def p(*parts):
    return os.path.join(PROJECT, *parts)


cases = [
    ('Read .env', tool('Read', file_path=p('.env')), 'DENY'),
    ('Read .env.prod', tool('Read', file_path=p('api', '.env.prod')), 'DENY'),
    ('Read prod.env', tool('Read', file_path=p('prod.env')), 'DENY'),
    ('Read id_rsa', tool('Read', file_path=os.path.join('~', '.ssh', 'id_rsa')), 'DENY'),
    ('Read cert.pfx', tool('Read', file_path=p('certs', 'api.pfx')), 'DENY'),
    ('Read server.pem', tool('Read', file_path=p('server.pem')), 'DENY'),
    ('Read tls.key', tool('Read', file_path=p('tls.key')), 'DENY'),
    ('Read .env.example passa', tool('Read', file_path=p('.env.example')), 'ALLOW'),
    ('Read .env.template passa', tool('Read', file_path=p('.env.template')), 'ALLOW'),
    ('Read id_rsa.pub passa', tool('Read', file_path=p('id_rsa.pub')), 'ALLOW'),
    ('Read código passa', tool('Read', file_path=p('src', 'Program.cs')), 'ALLOW'),
    ('Grep em .env', tool('Grep', pattern='DB', path=p('.env')), 'DENY'),
    ('Grep com glob *.pem', tool('Grep', pattern='x', glob='**/*.pem'), 'DENY'),
    ('Grep no código passa', tool('Grep', pattern='Password', path=p('src')), 'ALLOW'),
    ('Edit em .env', edit(p('.env'), 'A=1'), 'DENY'),

    ('Bash cat .env', bash('cat .env'), 'DENY'),
    ('Bash type .env', bash('type .\\.env'), 'DENY'),
    ('Bash cp .env', bash('cp api/.env /tmp/x'), 'DENY'),
    ('Bash python open', bash('python -c "open(\'.env\').read()"'), 'DENY'),
    ('PowerShell Get-Content', bash('Get-Content .env', 'PowerShell'), 'DENY'),
    ('Bash git add .env', bash('git add .env'), 'DENY'),
    ('Bash cat .env.example passa', bash('cat .env.example'), 'ALLOW'),
    ('Bash comum passa', bash('dotnet build src/Api.csproj'), 'ALLOW'),

    ('Bash rm -rf ~', bash('rm -rf ~'), 'DENY'),
    ('Bash rm -rf /', bash('rm -rf /'), 'DENY'),
    ('Bash rm -fr ..', bash('rm -fr ../outro'), 'DENY'),
    ('Bash rm -r -f C:\\', bash('rm -r -f C:\\'), 'DENY'),
    ('Bash rm -rf fora do projeto', bash('rm -rf "%s"' % OTHER), 'DENY'),
    ('Bash rm encadeado', bash('dotnet clean && rm -rf $HOME'), 'DENY'),
    ('PowerShell Remove-Item fora', bash('Remove-Item -Recurse -Force ~\\docs', 'PowerShell'), 'DENY'),
    ('Bash rm -rf ./bin passa', bash('rm -rf ./bin'), 'ALLOW'),
    ('Bash rm -rf node_modules passa', bash('rm -rf node_modules obj'), 'ALLOW'),
    ('Bash rm -rf dentro por absoluto passa', bash('rm -rf "%s"' % p('bin')), 'ALLOW'),
    ('Bash rm sem -r passa', bash('rm build.log'), 'ALLOW'),
    ('PowerShell Remove-Item dentro passa', bash('Remove-Item -Recurse -Force .\\bin', 'PowerShell'), 'ALLOW'),

    ('Write chave privada', write(p('key.txt'), PEM), 'DENY'),
    ('Write chave AWS', write(p('src', 'Aws.cs'), 'var k = "%s";' % AWS), 'DENY'),
    ('Write token GitHub', write(p('ci.sh'), 'TOKEN=%s' % GH), 'DENY'),
    ('Edit chave Anthropic', edit(p('src', 'Llm.ts'), 'const k = "%s"' % ANT), 'DENY'),
    ('Write senha em appsettings', write(p('appsettings.json'), '{"Db": {"Password": "Pr0d#2026"}}'), 'DENY'),
    ('Write connection string em código', write(p('src', 'Db.cs'),
                                                'var cs = "Server=db;User Id=sa;Password=Pr0d#2026;";'),  # bkhar-allow-secret
     'DENY'),
    ('Write senha em yaml', write(p('config.yml'), 'db:\n  password: Pr0d#2026\n'), 'DENY'),
    ('Write placeholder passa', write(p('appsettings.json'), '{"Db": {"Password": "${DB_PASS}"}}'), 'ALLOW'),
    ('Write nome de variável passa', write(p('providers.json'), '{"token": "ANTHROPIC_AUTH_TOKEN"}'), 'ALLOW'),
    ('Write senha vazia passa', write(p('appsettings.json'), '{"Db": {"Password": ""}}'), 'ALLOW'),
    ('Write código com Password passa', write(p('src', 'User.cs'), 'user.Password = request.Password;'), 'ALLOW'),
    ('Write com marca de exceção passa', write(p('tests', 'Fixture.cs'),
                                               'var k = "%s"; // %s' % (AWS, ALLOW_MARK)), 'ALLOW'),
    ('MultiEdit com segredo', tool('MultiEdit', file_path=p('a.cs'),
                                   edits=[{'old_string': 'a', 'new_string': 'k = "%s"' % AWS}]), 'DENY'),

    ('Write fora do projeto', write(os.path.join(OTHER, 'x.txt')), 'DENY'),
    ('Write relativo subindo', write(os.path.join('..', 'outro-projeto', 'x.txt')), 'DENY'),
    ('Write no projeto passa', write(p('src', 'x.cs')), 'ALLOW'),
    ('Write relativo no projeto passa', write(os.path.join('docs', 'x.md')), 'ALLOW'),
    ('Write no temporário passa', write(os.path.join(tempfile.gettempdir(), 'x.txt')), 'ALLOW'),
    ('Write na configuração do Claude passa',
     write(os.path.join(os.path.expanduser('~'), '.claude', 'x.md')), 'ALLOW'),
    ('Write sem cwd passa', {'tool_name': 'Write', 'tool_input': {'file_path': os.path.join(OTHER, 'x')}},
     'ALLOW'),

    ('Commit de .env pelo pre-commit', write(p('.env'), 'DB=x', name='Commit'), 'DENY'),
    ('Commit com chave pelo pre-commit', write(p('a.cs'), 'k = "%s"' % AWS, name='Commit'), 'DENY'),
    ('Commit limpo pelo pre-commit passa', write(p('a.cs'), 'class A {}', name='Commit'), 'ALLOW'),
    ('payload vazio libera', {}, 'ALLOW'),
    ('ferramenta sem input libera', {'tool_name': 'Bash'}, 'ALLOW'),
    ('comando nulo libera', tool('Bash', command=None), 'ALLOW'),
    ('ferramenta desconhecida libera', tool('Glob', pattern='*.env'), 'ALLOW'),
]

fail = 0
for name, payload, expect in cases:
    got = run(payload)
    ok = got == expect
    fail += (not ok)
    print('%-5s %-44s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

REPO = tempfile.mkdtemp(prefix='bkhar-git-')
NO_REPO = tempfile.mkdtemp(prefix='bkhar-sem-git-')


def git(*args):
    subprocess.run(['git', '-C', REPO] + list(args), capture_output=True, text=True)


git('init', '-q', '-b', 'feat/x')
git('-c', 'user.name=t', '-c', 'user.email=t@example.com', 'commit', '-q', '--allow-empty', '-m', 'base')
reset_cases = [
    ('reset --hard na branch de trabalho recusado', 'git reset --hard HEAD~1', None, 'DENY'),
    ('reset --hard encadeado recusado', 'git status && git reset --hard', None, 'DENY'),
    ('reset --hard por -C recusado', 'git -C "%s" reset --hard' % REPO, PROJECT, 'DENY'),
    ('reset --soft passa', 'git reset --soft HEAD~1', None, 'ALLOW'),
    ('reset --hard na task/T-003 passa', 'git reset --hard HEAD', 'task/T-003', 'ALLOW'),
    ('reset --hard na wave/2/T-004 passa', 'git reset --hard HEAD', 'wave/2/T-004', 'ALLOW'),
    ('reset --hard fora de repositório passa', 'git reset --hard', NO_REPO, 'ALLOW'),
]
for name, command, ctx, expect in reset_cases:
    cwd = REPO
    if ctx and ctx.startswith(('task/', 'wave/')):
        git('switch', '-q', '-c', ctx)
    elif ctx:
        cwd = ctx
    got = run({'tool_name': 'Bash', 'cwd': cwd, 'tool_input': {'command': command}})
    git('switch', '-q', 'feat/x')
    ok = got == expect
    fail += (not ok)
    print('%-5s %-44s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

CONFIG = os.path.join(os.path.dirname(PROJECT), 'config-claude')
HOME = os.path.expanduser('~')
DRIVE = os.path.splitdrive(PROJECT)[0] + os.sep


def with_env(**extra):
    env = dict(os.environ)
    env.pop('BKHAR_WRITE_ROOTS', None)
    env.update(extra)
    return env


env_cases = [
    ('BKHAR_WRITE_ROOTS libera raiz extra', write(os.path.join(EXTRA, 'x.txt')),
     with_env(BKHAR_WRITE_ROOTS=EXTRA), 'ALLOW'),
    ('BKHAR_WRITE_ROOTS com várias raízes', write(os.path.join(EXTRA, 'x.txt')),
     with_env(BKHAR_WRITE_ROOTS=os.pathsep.join([OTHER + '-nada', EXTRA])), 'ALLOW'),
    ('raiz da unidade em BKHAR_WRITE_ROOTS ignorada', write(os.path.join(OTHER, 'x.txt')),
     with_env(BKHAR_WRITE_ROOTS=DRIVE), 'DENY'),
    ('home em BKHAR_WRITE_ROOTS ignorado', write(os.path.join(OTHER, 'x.txt')),
     with_env(BKHAR_WRITE_ROOTS=HOME), 'DENY'),
    ('settings.json do ~/.claude recusado', write(os.path.join(HOME, '.claude', 'settings.json')),
     with_env(), 'DENY'),
    ('settings.local.json do ~/.claude recusado', write(os.path.join(HOME, '.claude', 'settings.local.json')),
     with_env(), 'DENY'),
    ('plugins do ~/.claude recusado', write(os.path.join(HOME, '.claude', 'plugins', 'x.json')),
     with_env(), 'DENY'),
    ('memória no ~/.claude passa', write(os.path.join(HOME, '.claude', 'projects', 'p', 'memory', 'm.md')),
     with_env(), 'ALLOW'),
    ('settings.json do CLAUDE_CONFIG_DIR recusado', edit(os.path.join(CONFIG, 'settings.json'), '{}'),
     with_env(CLAUDE_CONFIG_DIR=CONFIG), 'DENY'),
    ('memória no CLAUDE_CONFIG_DIR passa', write(os.path.join(CONFIG, 'projects', 'p', 'memory', 'm.md')),
     with_env(CLAUDE_CONFIG_DIR=CONFIG), 'ALLOW'),
]
for name, payload, env, expect in env_cases:
    got = run(payload, env)
    ok = got == expect
    fail += (not ok)
    print('%-5s %-44s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

with open(os.path.join(PROJECT, '.bks-profile.json'), 'w', encoding='utf-8') as f:
    json.dump({'guards': {'write_roots': [EXTRA]}}, f)
got = run(write(os.path.join(EXTRA, 'x.txt')), with_env())
ok = got == 'DENY'
fail += (not ok)
print('%-5s %-44s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', 'write_roots no perfil não vale mais',
                                              'DENY', got))
os.remove(os.path.join(PROJECT, '.bks-profile.json'))
os.rmdir(PROJECT)
os.rmdir(NO_REPO)
shutil.rmtree(REPO, ignore_errors=True)

print('\nfalhas:', fail)
sys.exit(1 if fail else 0)
