"""Testes da guarda de deriva do STATUS.md no session_memory.py."""
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(os.path.join('hooks', 'scripts', 'session_memory.py'))


def status(date):
    line = '> Última atualização: %s\n' % date if date else ''
    return '# STATUS — treino\n\n%s\n## Em uma frase\n\nEm curso.\n' % line


def journal(date):
    return '# JOURNAL — treino\n\n---\n\n## %s · marco\n\nAlgo mudou.\n' % date


def git(cwd, *args, date=None):
    env = dict(os.environ)
    if date:
        env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = date + 'T12:00:00'
    subprocess.run(['git', *args], cwd=cwd, env=env, check=True, capture_output=True)


def project(tmp, status_date, journal_date, commits=(), use_git=True):
    with open(os.path.join(tmp, 'STATUS.md'), 'w', encoding='utf-8') as fh:
        fh.write(status(status_date))
    with open(os.path.join(tmp, 'JOURNAL.md'), 'w', encoding='utf-8') as fh:
        fh.write(journal(journal_date))
    if not use_git:
        return
    git(tmp, 'init', '-q')
    git(tmp, 'config', 'user.email', 't@t')
    git(tmp, 'config', 'user.name', 't')
    for i, date in enumerate(commits):
        with open(os.path.join(tmp, 'f%d.txt' % i), 'w') as fh:
            fh.write(str(i))
        git(tmp, 'add', '-A')
        git(tmp, 'commit', '-q', '-m', 'c%d' % i, date=date)


def run(tmp):
    env = {k: v for k, v in os.environ.items() if k != 'BKS_VAULT'}
    env['GIT_CEILING_DIRECTORIES'] = os.path.dirname(tmp)
    r = subprocess.run([sys.executable, SCRIPT], cwd=tmp, env=env,
                       capture_output=True, text=True, timeout=20)
    out = r.stdout.strip()
    return json.loads(out) if out else {}


def drift_of(out):
    ctx = out.get('hookSpecificOutput', {}).get('additionalContext', '')
    return '## Deriva do STATUS.md' in ctx, out.get('systemMessage', ''), ctx


cases = [
    ('em dia: sem aviso', dict(status_date='2026-10-19', journal_date='2026-10-19',
                               commits=['2026-10-18', '2026-10-19']), False, None),
    ('commit posterior: aviso com contagem', dict(status_date='2026-10-19', journal_date='2026-10-19',
                                                  commits=['2026-10-19', '2026-10-20', '2026-10-22']),
     True, '2 commits'),
    ('JOURNAL posterior: aviso', dict(status_date='2026-10-19', journal_date='2026-10-25',
                                      commits=['2026-10-19']), True, '2026-10-25'),
    ('STATUS sem data: sem aviso', dict(status_date='', journal_date='2026-10-25',
                                        commits=['2026-10-30']), False, None),
    ('fora do Git, JOURNAL em dia: sem aviso', dict(status_date='2026-10-19', journal_date='2026-10-19',
                                                    use_git=False), False, None),
]

fail = 0
for name, kw, expect, needle in cases:
    with tempfile.TemporaryDirectory() as tmp:
        project(tmp, **kw)
        has, msg, ctx = drift_of(run(tmp))
    ok = has == expect and (not expect or (needle in ctx and needle in msg))
    fail += (not ok)
    print('%-4s %-40s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, has))
    if not ok and msg:
        print('       ', msg[:110])
print('\nfalhas:', fail)
sys.exit(1 if fail else 0)
