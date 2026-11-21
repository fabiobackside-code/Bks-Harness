"""Testes do scripts/install_guards.py: cópia dos guardas, hook, CI por host e reinstalação."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'install_guards.py')
VERSION = json.load(open(os.path.join(ROOT, '.claude-plugin', 'plugin.json'), encoding='utf-8'))['version']
GUARD_FILES = ('precommit.py', 'secret_guard.py', 'no_dispatcher.py', 'comment_budget.py', 'dotnet_project.py', '_common.py')
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print('%-5s %s%s' % ('OK' if ok else 'FALHA', name, '' if ok else '  ' + detail))


def git(repo, *args):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=repo,
                          capture_output=True, text=True)


def new_repo(init=True):
    repo = tempfile.mkdtemp(prefix='bkhar-install-')
    if init:
        git(repo, 'init', '-q')
    return repo


def install(repo, *args):
    r = subprocess.run([sys.executable, SCRIPT, repo, *args], capture_output=True, text=True, encoding='utf-8')
    return r.returncode, r.stdout + r.stderr


def exists(repo, *parts):
    return os.path.exists(os.path.join(repo, *parts))


def read(repo, *parts):
    with open(os.path.join(repo, *parts), encoding='utf-8') as f:
        return f.read()


repo = new_repo()
code, out = install(repo, '--host', 'github')
check('github: saída 0', code == 0, out)
check('github: os cinco guardas copiados', all(exists(repo, '.bkhar', 'guards', f) for f in GUARD_FILES))
check('github: VERSION igual ao plugin.json', read(repo, '.bkhar', 'guards', 'VERSION').strip() == VERSION)
check('github: hook escrito', 'bkhar-guards' in read(repo, '.githooks', 'pre-commit'))
check('github: workflow escrito', exists(repo, '.github', 'workflows', 'bkhar-guards.yml'))
check('github: sem arquivo do GitLab', not exists(repo, '.gitlab-ci.yml'))
check('github: core.hooksPath ativo', git(repo, 'config', 'core.hooksPath').stdout.strip() == '.githooks')
mode = git(repo, 'ls-files', '-s', '.githooks/pre-commit').stdout
check('github: hook executável no índice', mode.startswith('100755'), mode)
git(repo, 'add', '-A')
r = git(repo, 'commit', '-q', '-m', 'base')
check('github: commit da instalação passa pelos próprios guardas', r.returncode == 0, r.stdout + r.stderr)
with open(os.path.join(repo, '.env'), 'w') as f:
    f.write('DB=x\n')
git(repo, 'add', '.env')
check('github: commit com .env recusado', git(repo, 'commit', '-q', '-m', 'x').returncode != 0)
git(repo, 'rm', '-q', '--cached', '.env')

with open(os.path.join(repo, '.bkhar', 'guards', 'VERSION'), 'w') as f:
    f.write('0.0.1\n')
code, out = install(repo, '--host', 'github')
check('reinstalação: saída 0', code == 0, out)
check('reinstalação: VERSION atualizado', read(repo, '.bkhar', 'guards', 'VERSION').strip() == VERSION)
check('reinstalação: hook sem duplicar', read(repo, '.githooks', 'pre-commit').count('bkhar-guards') == 1)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
code, out = install(repo, '--host', 'gitlab')
check('gitlab: saída 0', code == 0, out)
check('gitlab: job em .bkhar/guards', exists(repo, '.bkhar', 'guards', 'gitlab-ci.yml'))
check('gitlab: .gitlab-ci.yml inclui o job', '.bkhar/guards/gitlab-ci.yml' in read(repo, '.gitlab-ci.yml'))
check('gitlab: sem workflow do GitHub', not exists(repo, '.github'))
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
with open(os.path.join(repo, '.gitlab-ci.yml'), 'w', encoding='utf-8') as f:
    f.write('build:\n  script: [make]\n')
code, out = install(repo, '--host', 'gitlab')
check('gitlab existente: não sobrescreve', read(repo, '.gitlab-ci.yml') == 'build:\n  script: [make]\n')
check('gitlab existente: avisa o include', 'include' in out and code == 0, out)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
code, out = install(repo, '--host', 'none')
check('none: guardas e hook sem CI', code == 0 and exists(repo, '.githooks', 'pre-commit')
      and not exists(repo, '.github') and not exists(repo, '.gitlab-ci.yml'), out)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
git(repo, 'config', 'core.hooksPath', '.husky')
code, out = install(repo, '--host', 'none')
check('hooksPath alheio: mantido', git(repo, 'config', 'core.hooksPath').stdout.strip() == '.husky')
check('hooksPath alheio: avisa', '.husky' in out and code == 0, out)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
os.makedirs(os.path.join(repo, '.githooks'))
with open(os.path.join(repo, '.githooks', 'pre-commit'), 'w', encoding='utf-8') as f:
    f.write('#!/bin/sh\nnpm test\n')
code, out = install(repo, '--host', 'none')
check('hook alheio: mantido', read(repo, '.githooks', 'pre-commit') == '#!/bin/sh\nnpm test\n')
check('hook alheio: avisa', 'pre-commit' in out and code == 0, out)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo(init=False)
code, out = install(repo, '--host', 'none')
check('fora de repositório git: copia e avisa', code == 0 and exists(repo, '.bkhar', 'guards', 'VERSION')
      and 'git' in out, out)
shutil.rmtree(repo, ignore_errors=True)

repo = new_repo()
code, out = install(repo, '--host', 'bitbucket')
check('host inválido: saída 2', code == 2, out)
shutil.rmtree(repo, ignore_errors=True)

fail = results.count(False)
print('\n%d verificacoes, %d falhas' % (len(results), fail))
sys.exit(1 if fail else 0)
