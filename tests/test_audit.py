"""Testes do scripts/audit.py: auditoria de deriva no kit e no projeto."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, 'scripts', 'audit.py')
INSTALL = os.path.join(ROOT, 'scripts', 'install_guards.py')
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print('%-5s %s%s' % ('OK' if ok else 'FALHA', name, '' if ok else '  ' + detail))


def git(repo, *args):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=repo,
                          capture_output=True, text=True)


def audit(path):
    r = subprocess.run([sys.executable, AUDIT, path], capture_output=True, text=True, encoding='utf-8')
    return r.returncode, r.stdout + r.stderr


def write(root, rel, text):
    path = os.path.join(root, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def project(host='none', profile_host=None):
    repo = tempfile.mkdtemp(prefix='bkhar-audit-')
    git(repo, 'init', '-q')
    subprocess.run([sys.executable, INSTALL, repo, '--host', host], capture_output=True)
    if profile_host:
        write(repo, '.bks-profile.json', json.dumps({'axes': {'git_host': profile_host}}))
    return repo


def kit(snippet):
    root = tempfile.mkdtemp(prefix='bkhar-audit-kit-')
    write(root, 'hooks/hooks.json', json.dumps({'hooks': {}}))
    write(root, 'docs/f.md', '# F\n\nTeto: 5 linhas\n')
    rules = [{'id': 'COD-01', 'regra': 'r', 'alvo': 'codigo', 'fonte': 'docs/f.md', 'sensores': [],
              'parametros': [{'nome': 'teto', 'valor': '5', 'em': [{'arquivo': 'docs/f.md', 'trecho': snippet}]}]}]
    write(root, 'rules.json', json.dumps({'rules': rules}))
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'rules_report.py'), '--root', root],
                   capture_output=True)
    return root


root = kit('Teto: 5 linhas')
code, out = audit(root)
check('kit coerente: saída 0', code == 0, out)
check('kit coerente: diz que é o kit', 'kit' in out, out)
shutil.rmtree(root, ignore_errors=True)

root = kit('Teto: 6 linhas')
code, out = audit(root)
check('kit com parâmetro divergente: saída 1 e nomeia', code == 1 and 'Teto: 6 linhas' in out, out)
shutil.rmtree(root, ignore_errors=True)

repo = project()
code, out = audit(repo)
check('projeto com guardas em dia: saída 0', code == 0, out)
check('projeto: diz que é projeto', 'projeto' in out, out)

with open(os.path.join(repo, '.bkhar', 'guards', 'secret_guard.py'), 'a', encoding='utf-8') as f:
    f.write('\n# mexido\n')
code, out = audit(repo)
check('cópia alterada: saída 1 e nomeia o guarda', code == 1 and 'secret_guard.py' in out, out)
check('cópia alterada: diz como destravar', 'install_guards.py' in out, out)
shutil.rmtree(repo, ignore_errors=True)

repo = project()
os.remove(os.path.join(repo, '.bkhar', 'guards', 'no_dispatcher.py'))
code, out = audit(repo)
check('guarda faltando na cópia: saída 1 e nomeia', code == 1 and 'no_dispatcher.py' in out, out)
shutil.rmtree(repo, ignore_errors=True)

repo = tempfile.mkdtemp(prefix='bkhar-audit-')
git(repo, 'init', '-q')
code, out = audit(repo)
check('projeto sem guardas: saída 1 e diz que faltam', code == 1 and 'não instalados' in out, out)
shutil.rmtree(repo, ignore_errors=True)

repo = project(host='none', profile_host='github')
code, out = audit(repo)
check('git_host github sem workflow: saída 1', code == 1 and 'bkhar-guards.yml' in out, out)
shutil.rmtree(repo, ignore_errors=True)

repo = project(host='gitlab', profile_host='gitlab')
check('git_host gitlab com CI: saída 0', audit(repo)[0] == 0, audit(repo)[1])
shutil.rmtree(repo, ignore_errors=True)

repo = project(host='none')
write(repo, '.bks-profile.json', json.dumps({'axes': {'mode': 'autonomo'}}))
code, out = audit(repo)
check('modo com o valor antigo: saída 1 e aponta o novo', code == 1 and '/bkhar:mode autonomous' in out, out)
write(repo, '.bks-profile.json', json.dumps({'axes': {'mode': 'autonomous'}}))
check('modo com o valor novo: saída 0', audit(repo)[0] == 0, audit(repo)[1])
shutil.rmtree(repo, ignore_errors=True)

repo = project()
write(repo, 'STATUS.md', '# STATUS\n\n> Última atualização: 2020-01-01\n')
git(repo, 'add', '-A')
git(repo, 'commit', '-q', '--no-verify', '-m', 'x')
code, out = audit(repo)
check('STATUS atrás do git: saída 1 e aponta a deriva', code == 1 and '2020-01-01' in out, out)
shutil.rmtree(repo, ignore_errors=True)

root = kit('Teto: 5 linhas')
write(root, 'inbox/proposals/2026-01-01-x.md',
      '---\ntipo: contradicao\nstatus: candidata\n---\n\n# Regra proposta\n\nA x B\n')
code, out = audit(root)
check('contradição em aberto: saída 1 e aponta o retro', code == 1 and '[contradicao]' in out
      and '2026-01-01-x.md' in out, out)
write(root, 'inbox/proposals/2026-01-01-x.md',
      '---\ntipo: correcao\nstatus: candidata\n---\n\n# Regra proposta\n\nY\n')
check('proposta que não é contradição não conta', audit(root)[0] == 0, audit(root)[1])
shutil.rmtree(root, ignore_errors=True)


def dossier(path, *args):
    r = subprocess.run([sys.executable, AUDIT, path, '--dossier', *args], capture_output=True, text=True,
                       encoding='utf-8')
    return r.returncode, r.stdout + r.stderr


root = kit('Teto: 5 linhas')
write(root, 'skills/a/SKILL.md', '# A\n\nlinha 1\nO pipeline tem 4 estágios.\nlinha 3\n')
write(root, 'agents/b.md', '# B\n\nO PipelineOrchestrator roda 5 estágios.\n')
write(root, 'commands/c.md', '# C\n\nnada do tema aqui\n')
write(root, 'docs/outro.md', 'pipeline fora do escopo\n')
write(root, 'skills/a/third-party/x.md', 'pipeline de terceiros\n')
code, out = dossier(root, 'pipeline')
check('dossiê: saída 0', code == 0, out)
check('dossiê: cita arquivo:linha dos dois trechos',
      'skills/a/SKILL.md:4' in out and 'agents/b.md:3' in out, out)
check('dossiê: traz contexto em volta do trecho', 'linha 1' in out and 'linha 3' in out, out)
check('dossiê: só o tema e só o escopo', 'commands/c.md' not in out and 'docs/outro.md' not in out, out)
check('dossiê: texto de terceiros fica fora', 'third-party' not in out, out)
code, out = dossier(root, 'inexistente')
check('dossiê de tema desconhecido: saída 2 e lista os temas', code == 2 and 'pipeline' in out, out)
code, out = dossier(root)
check('dossiê sem tema: lista os oito temas', code == 0 and len([l for l in out.splitlines() if l.startswith('  ')]) == 8, out)
shutil.rmtree(root, ignore_errors=True)

code, out = audit(ROOT)
check('o próprio kit sem deriva de registro', '[registro]' not in out and 'auditoria do kit' in out, out)

fail = results.count(False)
print('\n%d verificacoes, %d falhas' % (len(results), fail))
sys.exit(1 if fail else 0)
