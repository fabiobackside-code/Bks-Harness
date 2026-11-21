#!/usr/bin/env python3
"""Recuperação da task do LOOP-4: branch própria, portão como commit, tentativa como foto, trava e retomada.

Uso:
  recovery.py begin [REPO] --task T-003 [--base feat/x]     passo 0; --base só numa branch wave/N/T-NNN
  recovery.py gate [REPO] --task T-003 --phase spec|red|review
  recovery.py attempt [REPO] --task T-003 --n 2
  recovery.py snapshot [REPO] --task T-003 --score "testes verdes 5/6" [--passed]
  recovery.py block [REPO] --task T-003 --goal G2 --error "..." --question "..."
  recovery.py resume [REPO] --task T-003
  recovery.py integrate [REPO] --task T-003
  recovery.py show [REPO] --task T-003
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MAX_ATTEMPTS = 4
MAX_CYCLES = 3
MAX_INTERRUPTIONS = 2
PROTECTED = ('main', 'master')
TASK_BRANCH = re.compile(r'^(task/T-\d+|wave/\d+/T-\d+)$')
BLOCK_PREFIX = 'outputs/BLOQUEIO-'
EXCLUDE_BLOCK = ':(exclude)%s*' % BLOCK_PREFIX
GATES = ('spec', 'red', 'review')
RESUME_FIELDS = re.compile(r'^O que mudou:(.*?)^Partir de:[ \t]*(\S*)', re.M | re.S)


class StateError(Exception):
    """Operação recusada: o estado e a árvore não mudam."""


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _git(repo, *args, check=True, env=None):
    r = subprocess.run(['git', '-C', repo] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=env)
    if check and r.returncode != 0:
        raise StateError('git %s falhou: %s' % (args[0], (r.stderr or r.stdout).strip()))
    return r


def _out(repo, *args):
    return _git(repo, *args).stdout.strip()


def _exists(repo, ref):
    return _git(repo, 'rev-parse', '-q', '--verify', ref, check=False).returncode == 0


def state_dir(repo):
    common = _out(repo, 'rev-parse', '--git-common-dir')
    if not os.path.isabs(common):
        common = os.path.join(repo, common)
    return os.path.join(common, 'bkhar', 'recovery')


def _path(repo, tid):
    return os.path.join(state_dir(repo), '%s.json' % tid)


def get(repo, tid):
    path = _path(repo, tid)
    if not os.path.isfile(path):
        raise StateError('task %s sem estado de recuperação; rode begin' % tid)
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _save(repo, st, event=None):
    if event:
        st['events'].append({'at': now(), 'what': event, 'phase': st['phase'], 'status': st['status'],
                             'cycle': st['cycle'], 'attempt': st['attempt']})
    path = _path(repo, st['task'])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return st


def current_branch(repo):
    return _out(repo, 'branch', '--show-current')


def dirty(repo):
    lines = _git(repo, 'status', '--porcelain', '--untracked-files=all').stdout.splitlines()
    return [ln[3:] for ln in lines if ln.strip() and not ln[3:].strip('"').startswith(BLOCK_PREFIX)]


def protected(repo):
    names = list(PROTECTED)
    profile = os.path.join(repo, '.bks-profile.json')
    if os.path.isfile(profile):
        with io.open(profile, encoding='utf-8') as fh:
            names += json.load(fh).get('guards', {}).get('protected_branches', [])
    return names


def reset_hard(repo, target):
    """Volta a árvore ao alvo; só em branch de task ou de onda."""
    branch = current_branch(repo)
    if not TASK_BRANCH.match(branch):
        raise StateError('reset --hard só em branch task/* ou wave/*; atual: %s' % (branch or 'HEAD solto'))
    _git(repo, 'reset', '-q', '--hard', target)
    _git(repo, 'clean', '-q', '-fd', '-e', BLOCK_PREFIX + '*')


def _photo(repo, tid, name):
    fd, index = tempfile.mkstemp(prefix='bkhar-index-')
    os.close(fd)
    os.remove(index)
    env = dict(os.environ, GIT_INDEX_FILE=index)
    try:
        _git(repo, 'read-tree', 'HEAD', env=env)
        _git(repo, 'add', '-A', '--', '.', EXCLUDE_BLOCK, env=env)
        tree = _git(repo, 'write-tree', env=env).stdout.strip()
    finally:
        if os.path.exists(index):
            os.remove(index)
    sha = _out(repo, 'commit-tree', tree, '-p', 'HEAD', '-m', 'foto %s %s' % (tid, name))
    _git(repo, 'update-ref', 'refs/bkhar/%s/%s' % (tid, name), sha)
    return sha


def _restore(repo, st, name):
    ref = 'refs/bkhar/%s/%s' % (st['task'], name)
    if not _exists(repo, ref):
        raise StateError('foto %s não existe' % name)
    reset_hard(repo, st['gates']['red'])
    _git(repo, 'read-tree', '-u', '--reset', ref)
    _git(repo, 'reset', '-q')


def _running(st, *phases):
    if st['status'] != 'running':
        raise StateError('task %s está %s' % (st['task'], st['status']))
    if phases and st['phase'] not in phases:
        raise StateError('task %s na fase %s; esperado %s' % (st['task'], st['phase'], ' ou '.join(phases)))


def _on_branch(repo, st):
    branch = current_branch(repo)
    if branch != st['branch']:
        raise StateError('estado diz %s, o git está em %s; confira antes de seguir'
                         % (st['branch'], branch or 'HEAD solto'))


def begin(repo, tid, base=None):
    if os.path.isfile(_path(repo, tid)) and get(repo, tid)['status'] != 'done':
        raise StateError('task %s já tem estado; use resume' % tid)
    branch = current_branch(repo)
    if not branch:
        raise StateError('HEAD solto; abra a task a partir de uma branch')
    if dirty(repo):
        raise StateError('árvore suja; commite ou guarde antes do passo 0: %s' % ', '.join(dirty(repo)[:5]))
    if TASK_BRANCH.match(branch):
        if not base:
            raise StateError('na branch %s, informe --base com a branch de trabalho' % branch)
        task_branch = branch
    else:
        if branch in protected(repo):
            raise StateError('branch protegida %s; abra a task a partir da branch de trabalho' % branch)
        base, task_branch = branch, 'task/%s' % tid
        _git(repo, 'switch', '-q', '-c', task_branch)
    st = {'task': tid, 'branch': task_branch, 'base_branch': base, 'status': 'running', 'phase': 'red',
          'cycle': 1, 'attempt': 0, 'gates': {'spec': _out(repo, 'rev-parse', 'HEAD')}, 'snapshots': {},
          'interruptions': {}, 'block_cause': None, 'blocked_file': None, 'blocked_head': None,
          'history': [], 'events': []}
    return _save(repo, st, 'begin em %s a partir de %s' % (task_branch, base))


def gate(repo, tid, phase):
    if phase not in GATES:
        raise StateError('portão %r; use %s' % (phase, ', '.join(GATES)))
    st = get(repo, tid)
    _running(st, 'review' if phase == 'review' else 'red')
    _on_branch(repo, st)
    _git(repo, 'add', '-A', '--', '.', EXCLUDE_BLOCK)
    if _git(repo, 'diff', '--cached', '--quiet', check=False).returncode == 0:
        raise StateError('portão %s sem mudança para commitar' % phase)
    labels = {'spec': 'especificação corrigida', 'red': 'RED confirmado', 'review': 'revisão aprovada'}
    r = _git(repo, 'commit', '-q', '-m', '%s(%s): %s' % (phase, tid, labels[phase]), check=False)
    if r.returncode != 0:
        raise StateError('commit do portão %s recusado: %s' % (phase, (r.stderr or r.stdout).strip()))
    st['gates'][phase] = _out(repo, 'rev-parse', 'HEAD')
    st['phase'] = {'spec': 'red', 'red': 'impl', 'review': 'reviewed'}[phase]
    if phase == 'spec':
        st['gates'].pop('red', None)
    return _save(repo, st, 'portão %s' % phase)


def attempt(repo, tid, n):
    st = get(repo, tid)
    _running(st, 'impl', 'review')
    _on_branch(repo, st)
    if n != st['attempt'] + 1 or n > MAX_ATTEMPTS:
        raise StateError('tentativa %d recusada: a próxima é %d, teto %d'
                         % (n, st['attempt'] + 1, MAX_ATTEMPTS))
    st.update(attempt=n, phase='impl-%d' % n)
    return _save(repo, st, 'tentativa %d' % n)


def snapshot(repo, tid, score, passed=False):
    st = get(repo, tid)
    name = 'impl-%d' % st['attempt']
    _running(st, name)
    _on_branch(repo, st)
    sha = _photo(repo, tid, name)
    st['snapshots'][name] = {'sha': sha, 'score': score, 'passed': bool(passed)}
    st['phase'] = 'review' if passed else 'impl'
    return _save(repo, st, 'foto %s: %s' % (name, score))


def _block_text(st, goal, error, question):
    tid = st['task']
    terminal = st['status'] == 'terminal'
    if st['block_cause'] == 'interruption':
        cause = 'duas quedas na tentativa %d' % (st['attempt'] + 1)
    else:
        cause = '%d tentativas sem passar nos goals' % MAX_ATTEMPTS
    rows = ['| %s | %s |' % (k, v['score']) for k, v in sorted(st['snapshots'].items())]
    scored = [k for k in sorted(st['snapshots']) if not k.endswith('interrupted')]
    best = scored[-1] if scored else 'red'
    lines = ['# BLOQUEIO — %s' % tid, '',
             '> Ciclo %d de %d, em %s. Causa: %s.' % (st['cycle'], MAX_CYCLES, now(), cause), '',
             '## Diagnóstico', '',
             '- **Goal que falhou:** %s' % goal,
             '- **Erro:** %s' % error,
             '- **Pergunta para você:** %s' % question, '',
             '## Tentativas deste ciclo', '',
             '| Tentativa | Placar |', '|---|---|'] + (rows or ['| — | — |']) + ['']
    if terminal:
        lines += ['## Retomada fechada', '',
                  'Terceiro bloqueio da task: o problema está na especificação, não na implementação.',
                  'Leve a task ao `/bkhar:refine` para reescrever o `FEAT` e o `TEST`.', '']
        return '\n'.join(lines)
    lines += ['## Opções de resolução', '',
              '1. **Especificação errada ou ambígua:** corrija o `FEAT` ou o `TEST`, commite na `%s` e'
              % st['branch'],
              '   retome com `Partir de: spec` (o `tester` refaz o RED) ou `Partir de: red` (os testes'
              ' já valem).',
              '2. **Falta informação ao Dev:** escreva em "O que mudou" o que ele precisa saber e retome'
              ' com',
              '   `Partir de: %s`, a tentativa mais recente.' % best,
              '3. **Problema de ambiente** (queda, dependência, ferramenta): corrija o ambiente, diga'
              ' o que',
              '   mudou e retome da tentativa mais recente.', '',
              'Para não se repetir: o Dev do ciclo novo recebe o que você escrever abaixo e o placar'
              ' acima.',
              'Retomada sem informação nova é recusada; o terceiro bloqueio fecha a retomada.', '',
              '## Retomada', '',
              'Preencha e rode `/bkhar:loop %s --resume`.' % tid, '',
              'O que mudou:', '',
              'Partir de: red', '']
    return '\n'.join(lines)


def _block(repo, st, goal, error, question, cause):
    reset_hard(repo, st['gates']['red'])
    terminal = cause == 'attempts' and st['cycle'] >= MAX_CYCLES
    st.update(status='terminal' if terminal else 'blocked', block_cause=cause,
              blocked_head=_out(repo, 'rev-parse', 'HEAD'),
              blocked_file=os.path.join(os.path.abspath(repo), BLOCK_PREFIX + '%s.md' % st['task']))
    os.makedirs(os.path.dirname(st['blocked_file']), exist_ok=True)
    with io.open(st['blocked_file'], 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(_block_text(st, goal, error, question))
    return _save(repo, st, 'bloqueio (%s)%s' % (cause, ' terminal' if terminal else ''))


def block(repo, tid, goal, error, question):
    st = get(repo, tid)
    _running(st)
    _on_branch(repo, st)
    if st['phase'].startswith('impl-'):
        name = st['phase']
        st['snapshots'][name] = {'sha': _photo(repo, tid, name), 'score': 'sem placar', 'passed': False}
    return _block(repo, st, goal, error, question, 'attempts')


def _reopen(repo, st):
    with io.open(st['blocked_file'], encoding='utf-8') as fh:
        m = RESUME_FIELDS.search(fh.read())
    what, start = (m.group(1).strip(), m.group(2).strip()) if m else ('', '')
    if not what:
        raise StateError('preencha "O que mudou" no %s antes de retomar' % os.path.basename(st['blocked_file']))
    if start not in ('spec', 'red') and not re.match(r'^impl-\d+$', start):
        raise StateError('"Partir de: %s" inválido; use spec, red ou impl-K' % start)
    _on_branch(repo, st)
    if dirty(repo):
        raise StateError('árvore suja; commite a correção antes de retomar')
    head = _out(repo, 'rev-parse', 'HEAD')
    if start in ('spec', 'red') and head == st['blocked_head']:
        raise StateError('Partir de: %s pede commit novo no FEAT ou no TEST desde o bloqueio' % start)
    if start.startswith('impl-') and head != st['blocked_head']:
        raise StateError('há commit novo desde o bloqueio; parta de spec ou red')
    scores = '; '.join('%s %s' % (k, v['score']) for k, v in sorted(st['snapshots'].items()))
    briefing = 'O que mudou: %s\nPlacar do ciclo %d: %s' % (what, st['cycle'], scores or 'sem tentativa')
    if start == 'spec':
        st['gates']['spec'] = head
        st['gates'].pop('red', None)
        st['phase'] = 'red'
    elif start == 'red':
        st['gates']['red'] = head
        st['phase'] = 'impl'
    else:
        _restore(repo, st, start)
        st['phase'] = 'impl'
    st['history'].append({'cycle': st['cycle'], 'cause': st['block_cause'], 'what': what,
                          'start': start, 'snapshots': st['snapshots']})
    if st['block_cause'] != 'interruption':
        st.update(cycle=st['cycle'] + 1, attempt=0, snapshots={})
    st.update(status='running', interruptions={}, block_cause=None, blocked_head=None)
    _save(repo, st, 'retomada do bloqueio, ciclo %d, partindo de %s' % (st['cycle'], start))
    return {'action': 'ciclo %d, partindo de %s' % (st['cycle'], start), 'briefing': briefing}


def _recover(repo, st):
    phase = st['phase']
    if phase == 'integration':
        if _exists(repo, 'MERGE_HEAD'):
            _git(repo, 'merge', '--abort')
        st['phase'] = 'reviewed'
        _save(repo, st, 'queda na integração: merge abortado')
        return {'action': 'refazer a integração'}
    _on_branch(repo, st)
    if phase == 'red':
        reset_hard(repo, st['gates']['spec'])
        _save(repo, st, 'queda no red')
        return {'action': 'refazer a fase red a partir do spec'}
    if phase.startswith('impl-'):
        k = st['attempt']
        _photo(repo, st['task'], 'impl-%d-interrupted' % k)
        count = st['interruptions'].get(str(k), 0) + 1
        st['interruptions'][str(k)] = count
        st.update(attempt=k - 1, phase='impl')
        if count >= MAX_INTERRUPTIONS:
            _block(repo, st, 'tentativa %d concluída' % k, 'a sessão caiu %d vezes na mesma tentativa' % count,
                   'O ambiente (Maestri, memória, ferramenta) está estável?', 'interruption')
            return {'action': 'BLOQUEIO por queda repetida na impl-%d' % k}
        if k > 1:
            _restore(repo, st, 'impl-%d' % (k - 1))
        else:
            reset_hard(repo, st['gates']['red'])
        _save(repo, st, 'queda na impl-%d, interrompida não conta' % k)
        return {'action': 'refazer a impl-%d a partir da impl-%d' % (k, k - 1)}
    if phase == 'impl':
        if st['attempt']:
            _restore(repo, st, 'impl-%d' % st['attempt'])
        else:
            reset_hard(repo, st['gates']['red'])
        _save(repo, st, 'queda entre tentativas')
        return {'action': 'seguir para a impl-%d' % (st['attempt'] + 1)}
    if phase == 'review':
        _restore(repo, st, 'impl-%d' % st['attempt'])
        _save(repo, st, 'queda na revisão')
        return {'action': 'refazer a review sobre a impl-%d' % st['attempt']}
    if dirty(repo):
        raise StateError('fase %s com árvore suja; confira antes de seguir' % phase)
    return {'action': 'integrar'}


def resume(repo, tid):
    st = get(repo, tid)
    if st['status'] == 'done':
        raise StateError('task %s já concluída' % tid)
    if st['status'] == 'terminal':
        raise StateError('retomada fechada no terceiro bloqueio; leve a task ao /bkhar:refine')
    if st['status'] == 'blocked':
        return _reopen(repo, st)
    return _recover(repo, st)


def integrate(repo, tid):
    st = get(repo, tid)
    _running(st, 'reviewed')
    if dirty(repo):
        raise StateError('árvore suja; nada entra na integração fora do portão de revisão')
    st['phase'] = 'integration'
    _save(repo, st, 'integração')
    if current_branch(repo) != st['base_branch']:
        _git(repo, 'switch', '-q', st['base_branch'])
    r = _git(repo, 'merge', '--no-ff', '-q', '-m', 'merge(%s): integra a task' % tid, st['branch'], check=False)
    if r.returncode != 0:
        files = _out(repo, 'diff', '--name-only', '--diff-filter=U').split()
        if _exists(repo, 'MERGE_HEAD'):
            _git(repo, 'merge', '--abort')
        st['phase'] = 'reviewed'
        _save(repo, st, 'conflito na integração')
        raise StateError('conflito na integração, resolva à mão: %s' % (', '.join(files) or r.stderr.strip()))
    refs = _out(repo, 'for-each-ref', '--format=%(refname)', 'refs/bkhar/%s/' % tid).split()
    for ref in refs:
        _git(repo, 'update-ref', '-d', ref)
    _git(repo, 'branch', '-q', '-D', st['branch'], check=False)
    st.update(status='done', phase='done')
    return _save(repo, st, 'integrada em %s' % st['base_branch'])


def main(argv=None):
    ap = argparse.ArgumentParser(description='recuperação da task do LOOP-4')
    ap.add_argument('cmd', choices=('begin', 'gate', 'attempt', 'snapshot', 'block', 'resume', 'integrate',
                                      'show'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--task', required=True)
    ap.add_argument('--base')
    ap.add_argument('--phase')
    ap.add_argument('--n', type=int)
    ap.add_argument('--score')
    ap.add_argument('--passed', action='store_true')
    ap.add_argument('--goal', default='')
    ap.add_argument('--error', default='')
    ap.add_argument('--question', default='')
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    try:
        if a.cmd == 'begin':
            begin(repo, a.task, a.base)
        elif a.cmd == 'gate':
            gate(repo, a.task, a.phase)
        elif a.cmd == 'attempt':
            attempt(repo, a.task, a.n)
        elif a.cmd == 'snapshot':
            snapshot(repo, a.task, a.score or 'sem placar', a.passed)
        elif a.cmd == 'block':
            st = block(repo, a.task, a.goal, a.error, a.question)
            print(st['blocked_file'])
            return 0
        elif a.cmd == 'resume':
            out = resume(repo, a.task)
            print(out['action'])
            if out.get('briefing'):
                print(out['briefing'])
            return 0
        elif a.cmd == 'integrate':
            integrate(repo, a.task)
        if a.cmd == 'show':
            print(json.dumps(get(repo, a.task), ensure_ascii=False, indent=2))
        else:
            print('ok')
    except StateError as exc:
        print('recusado: %s' % exc)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
