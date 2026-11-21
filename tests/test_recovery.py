"""Testes do scripts/recovery.py: portão, foto, trava, retomada e integração sobre repositório git temporário.

Uso: python tests/test_recovery.py
"""
import importlib.util
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('recovery', os.path.join(ROOT, 'scripts', 'recovery.py'))
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)

failures = []
checks = 0
TID = 'T-003'


def check(name, condition, detail=''):
    global checks
    checks += 1
    if condition:
        print('  ok    %s' % name)
    else:
        print('  FALHA %s' % name)
        if detail:
            print('          %s' % detail)
        failures.append(name)


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo] + list(args), capture_output=True, text=True)
    return r.stdout.strip()


def write(repo, rel, text):
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def read(repo, rel):
    path = os.path.join(repo, rel)
    if not os.path.exists(path):
        return None
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def refused(fn, *args, **kw):
    try:
        fn(*args, **kw)
    except rec.StateError as exc:
        return str(exc)
    return None


def _rm_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def repo_on_feature():
    repo = tempfile.mkdtemp(prefix='bkhar-rec-')
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'user.name', 'teste')
    git(repo, 'config', 'user.email', 'teste@example.com')
    git(repo, 'config', 'core.autocrlf', 'false')
    write(repo, 'specs/FEAT-x.md', 'feat\n')
    write(repo, 'specs/TEST-x.md', 'cenarios\n')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '-m', 'spec aprovada')
    git(repo, 'switch', '-q', '-c', 'feat/x')
    return repo


def cleanup(repo):
    shutil.rmtree(repo, onerror=_rm_readonly)


def to_red(repo):
    rec.begin(repo, TID)
    write(repo, 'tests/calc_test.py', 'assert soma(1, 1) == 2\n')
    rec.gate(repo, TID, 'red')


def fail_attempt(repo, n, text):
    rec.attempt(repo, TID, n)
    write(repo, 'src/calc.py', text)
    rec.snapshot(repo, TID, 'testes verdes %d/6' % n)


def to_blocked(repo):
    to_red(repo)
    for n in range(1, 5):
        fail_attempt(repo, n, 'versao %d\n' % n)
    rec.block(repo, TID, goal='G2 testes verdes', error='AssertionError em soma',
              question='O arredondamento é HALF_EVEN?')


def fill_resume(repo, what, start):
    path = rec.get(repo, TID)['blocked_file']
    head, _, section = read(repo, os.path.relpath(path, repo)).partition('## Retomada')
    section = section.replace('O que mudou:\n', 'O que mudou: %s\n' % what, 1)
    section = re.sub(r'(?m)^Partir de: \S+', 'Partir de: %s' % start, section, count=1)
    write(repo, os.path.relpath(path, repo), head + '## Retomada' + section)


def test_begin():
    print('\npasso 0: branch da task')
    repo = repo_on_feature()
    write(repo, 'solto.txt', 'x')
    check('árvore suja é recusada', refused(rec.begin, repo, TID))
    os.remove(os.path.join(repo, 'solto.txt'))
    git(repo, 'switch', '-q', 'main')
    check('branch protegida é recusada', refused(rec.begin, repo, TID))
    git(repo, 'switch', '-q', 'feat/x')
    head = git(repo, 'rev-parse', 'HEAD')
    rec.begin(repo, TID)
    st = rec.get(repo, TID)
    check('cria a task/T-003', git(repo, 'branch', '--show-current') == 'task/T-003')
    check('guarda a branch de origem', st['base_branch'] == 'feat/x', st)
    check('portão spec é o HEAD da origem', st['gates']['spec'] == head, st)
    check('fase red', st['phase'] == 'red', st)
    ev = st['events'][-1]
    check('evento leva fase, estado, ciclo e tentativa',
          (ev.get('phase'), ev.get('status'), ev.get('cycle'), ev.get('attempt')) == ('red', 'running', 1, 0), ev)
    check('begin repetido é recusado', refused(rec.begin, repo, TID))
    cleanup(repo)


def test_gates_and_attempts():
    print('\nportões, tentativas e fotos')
    repo = repo_on_feature()
    rec.begin(repo, TID)
    check('tentativa antes do RED é recusada', refused(rec.attempt, repo, TID, 1))
    write(repo, 'tests/calc_test.py', 'assert soma(1, 1) == 2\n')
    rec.gate(repo, TID, 'red')
    st = rec.get(repo, TID)
    check('portão red é commit', git(repo, 'log', '-1', '--format=%s').startswith('red(T-003)'),
          git(repo, 'log', '-1', '--format=%s'))
    check('sha do red guardado', st['gates']['red'] == git(repo, 'rev-parse', 'HEAD'))
    check('pular tentativa é recusado', refused(rec.attempt, repo, TID, 2))
    rec.attempt(repo, TID, 1)
    write(repo, 'src/novo.py', 'arquivo novo\n')
    rec.snapshot(repo, TID, 'testes verdes 2/6')
    ref = 'refs/bkhar/T-003/impl-1'
    check('foto vira ref', git(repo, 'rev-parse', '--verify', '-q', ref) != '')
    check('foto leva arquivo novo', git(repo, 'show', '%s:src/novo.py' % ref) == 'arquivo novo')
    check('foto fora do histórico', git(repo, 'log', '-1', '--format=%s').startswith('red('))
    check('placar no estado', rec.get(repo, TID)['snapshots']['impl-1']['score'] == 'testes verdes 2/6')
    for n in (2, 3, 4):
        rec.attempt(repo, TID, n)
        rec.snapshot(repo, TID, 'testes verdes %d/6' % n)
    check('5ª tentativa é recusada', refused(rec.attempt, repo, TID, 5))
    cleanup(repo)


def test_block_and_resume():
    print('\ntrava e retomada')
    repo = repo_on_feature()
    to_blocked(repo)
    st = rec.get(repo, TID)
    text = read(repo, os.path.relpath(st['blocked_file'], repo)) or ''
    check('estado bloqueado', st['status'] == 'blocked', st)
    check('BLOQUEIO com o diagnóstico', 'AssertionError em soma' in text and 'HALF_EVEN' in text)
    check('BLOQUEIO com as opções', '## Opções de resolução' in text)
    check('BLOQUEIO com o placar das tentativas', 'testes verdes 4/6' in text)
    check('BLOQUEIO com o comando', '/bkhar:loop T-003 --resume' in text)
    check('árvore volta ao red no bloqueio', read(repo, 'src/calc.py') is None)
    check('refs ficam no bloqueio comum', git(repo, 'rev-parse', '--verify', '-q', 'refs/bkhar/T-003/impl-2') != '')
    check('retomada sem o que mudou é recusada', refused(rec.resume, repo, TID))
    fill_resume(repo, 'corrigi o arredondamento no TEST', 'red')
    check('partir do red sem commit novo é recusado', refused(rec.resume, repo, TID))
    fill_resume(repo, '', 'impl-2')
    out = rec.resume(repo, TID)
    st = rec.get(repo, TID)
    check('ciclo 2', st['cycle'] == 2, st)
    check('contador zerado no ciclo novo', st['attempt'] == 0, st)
    check('portão spec intacto', st['gates']['spec'] == git(repo, 'rev-parse', 'feat/x'))
    check('árvore com a foto da impl-2', read(repo, 'src/calc.py') == 'versao 2\n', read(repo, 'src/calc.py'))
    check('Dev recebe o que mudou', 'corrigi o arredondamento' in out.get('briefing', ''), out)
    check('Dev recebe o placar anterior', 'testes verdes 4/6' in out.get('briefing', ''), out)
    rec.attempt(repo, TID, 1)
    check('tentativa 1 do ciclo novo aceita', rec.get(repo, TID)['attempt'] == 1)
    cleanup(repo)


def test_resume_from_red_after_fix():
    print('\nretomada do red com correção commitada')
    repo = repo_on_feature()
    to_blocked(repo)
    write(repo, 'specs/TEST-x.md', 'cenarios com HALF_EVEN\n')
    git(repo, 'commit', '-q', '-am', 'corrige TEST')
    fill_resume(repo, 'TEST corrigido', 'red')
    rec.resume(repo, TID)
    st = rec.get(repo, TID)
    check('red passa a ser o commit da correção', st['gates']['red'] == git(repo, 'rev-parse', 'HEAD'), st)
    check('sem tentativa na árvore', read(repo, 'src/calc.py') is None)
    cleanup(repo)


def test_terminal():
    print('\nteto de 3 ciclos')
    repo = repo_on_feature()
    to_blocked(repo)
    for cycle in (2, 3):
        fill_resume(repo, 'ciclo %d' % cycle, 'impl-1')
        rec.resume(repo, TID)
        for n in range(1, 5):
            fail_attempt(repo, n, 'c%d v%d\n' % (cycle, n))
        rec.block(repo, TID, goal='G2', error='falha', question='?')
    st = rec.get(repo, TID)
    text = read(repo, os.path.relpath(st['blocked_file'], repo)) or ''
    check('3º bloqueio é terminal', st['status'] == 'terminal', st)
    check('terminal aponta o /bkhar:refine', '/bkhar:refine' in text)
    fill_resume(repo, 'mais uma', 'impl-1')
    check('retomada do terminal é recusada', refused(rec.resume, repo, TID))
    cleanup(repo)


def test_crash():
    print('\nqueda no meio')
    repo = repo_on_feature()
    to_red(repo)
    fail_attempt(repo, 1, 'v1\n')
    fail_attempt(repo, 2, 'v2\n')
    rec.attempt(repo, TID, 3)
    write(repo, 'src/calc.py', 'quebrado pela metade')
    out = rec.resume(repo, TID)
    st = rec.get(repo, TID)
    check('foto da interrompida', git(repo, 'rev-parse', '--verify', '-q', 'refs/bkhar/T-003/impl-3-interrupted') != '')
    check('árvore volta à impl-2', read(repo, 'src/calc.py') == 'v2\n', read(repo, 'src/calc.py'))
    check('interrompida não conta', st['attempt'] == 2, st)
    check('portão spec não refeito', st['gates']['spec'] == git(repo, 'rev-parse', 'feat/x'))
    check('ação diz refazer a impl-3', 'impl-3' in out.get('action', ''), out)
    rec.attempt(repo, TID, 3)
    write(repo, 'src/calc.py', 'de novo pela metade')
    rec.resume(repo, TID)
    st = rec.get(repo, TID)
    check('segunda queda na mesma tentativa bloqueia', st['status'] == 'blocked' and st['block_cause'] == 'interruption', st)
    fill_resume(repo, 'Maestri reiniciado', 'impl-2')
    rec.resume(repo, TID)
    st = rec.get(repo, TID)
    check('bloqueio por queda não gasta ciclo', st['cycle'] == 1 and st['attempt'] == 2, st)
    cleanup(repo)


def test_crash_in_red_and_review():
    print('\nqueda no red e na revisão')
    repo = repo_on_feature()
    rec.begin(repo, TID)
    write(repo, 'tests/meio.py', 'pela metade')
    out = rec.resume(repo, TID)
    check('queda no red descarta e refaz o RED', read(repo, 'tests/meio.py') is None and 'red' in out['action'], out)
    write(repo, 'tests/calc_test.py', 'assert soma(1, 1) == 2\n')
    rec.gate(repo, TID, 'red')
    rec.attempt(repo, TID, 1)
    write(repo, 'src/calc.py', 'certo\n')
    rec.snapshot(repo, TID, 'testes verdes 6/6', passed=True)
    check('tentativa aprovada leva à revisão', rec.get(repo, TID)['phase'] == 'review')
    write(repo, 'src/calc.py', 'mexido durante a revisão')
    out = rec.resume(repo, TID)
    check('queda na revisão restaura a aprovada', read(repo, 'src/calc.py') == 'certo\n' and 'review' in out['action'], out)
    cleanup(repo)


def test_divergence_and_reset_guard():
    print('\ndivergência e reset fora da branch da task')
    repo = repo_on_feature()
    to_red(repo)
    git(repo, 'switch', '-q', 'feat/x')
    check('branch diferente da do estado para', refused(rec.resume, repo, TID))
    check('reset na branch de trabalho é recusado', refused(rec.reset_hard, repo, 'HEAD'))
    cleanup(repo)


def test_integrate():
    print('\nintegração')
    repo = repo_on_feature()
    to_red(repo)
    rec.attempt(repo, TID, 1)
    write(repo, 'src/calc.py', 'certo\n')
    rec.snapshot(repo, TID, 'testes verdes 6/6', passed=True)
    rec.gate(repo, TID, 'review')
    rec.integrate(repo, TID)
    parents = git(repo, 'log', '-1', '--format=%P', 'feat/x').split()
    subjects = git(repo, 'log', '--format=%s', 'feat/x')
    check('merge --no-ff na origem', len(parents) == 2, parents)
    check('portões no histórico', 'red(T-003)' in subjects and 'review(T-003)' in subjects, subjects)
    check('branch da task apagada', git(repo, 'branch', '--list', 'task/T-003') == '')
    check('refs apagadas', git(repo, 'for-each-ref', 'refs/bkhar/') == '')
    check('estado concluído', rec.get(repo, TID)['status'] == 'done')
    cleanup(repo)


def test_integrate_conflict_and_crash():
    print('\nconflito e queda na integração')
    repo = repo_on_feature()
    to_red(repo)
    rec.attempt(repo, TID, 1)
    write(repo, 'specs/FEAT-x.md', 'versão da task\n')
    rec.snapshot(repo, TID, 'ok', passed=True)
    rec.gate(repo, TID, 'review')
    git(repo, 'switch', '-q', 'feat/x')
    write(repo, 'specs/FEAT-x.md', 'versão da origem\n')
    git(repo, 'commit', '-q', '-am', 'mudança paralela')
    git(repo, 'switch', '-q', 'task/T-003')
    msg = refused(rec.integrate, repo, TID)
    check('conflito para e lista o arquivo', msg and 'specs/FEAT-x.md' in msg, msg)
    check('sem merge pela metade', not os.path.exists(os.path.join(repo, '.git', 'MERGE_HEAD')))
    git(repo, 'switch', '-q', 'feat/x')
    git(repo, 'merge', '--no-ff', '-q', 'task/T-003')
    st = rec.get(repo, TID)
    st['phase'] = 'integration'
    rec._save(repo, st)
    out = rec.resume(repo, TID)
    check('queda na integração aborta o merge', not os.path.exists(os.path.join(repo, '.git', 'MERGE_HEAD'))
          and 'integra' in out['action'], out)
    cleanup(repo)


def main():
    print('testes do recovery.py')
    for fn in (test_begin, test_gates_and_attempts, test_block_and_resume, test_resume_from_red_after_fix,
               test_terminal, test_crash, test_crash_in_red_and_review, test_divergence_and_reset_guard,
               test_integrate, test_integrate_conflict_and_crash):
        try:
            fn()
        except Exception as exc:
            check('%s sem exceção' % fn.__name__, False, repr(exc))
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
