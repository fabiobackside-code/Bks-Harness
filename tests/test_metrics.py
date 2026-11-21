"""Testes do scripts/metrics.py: fases da task recortadas no transcript, sobre fixture.

Uso: python tests/test_metrics.py
"""
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('metrics', os.path.join(ROOT, 'scripts', 'metrics.py'))
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)

failures = []
checks = 0


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


def ev(at, what, phase, status='running', cycle=1, attempt=0):
    return {'at': '2026-11-20T%sZ' % at, 'what': what, 'phase': phase, 'status': status,
            'cycle': cycle, 'attempt': attempt}


DONE = {'task': 'T-001', 'status': 'done', 'cycle': 1, 'attempt': 2,
        'snapshots': {'impl-1': {'score': 'testes verdes 3/6'}, 'impl-2': {'score': 'testes verdes 6/6'}},
        'history': [], 'events': [
            ev('10:00:00', 'begin', 'red'),
            ev('10:10:00', 'portão red', 'impl'),
            ev('10:11:00', 'tentativa 1', 'impl-1', attempt=1),
            ev('10:20:00', 'foto impl-1: testes verdes 3/6', 'impl', attempt=1),
            ev('10:21:00', 'tentativa 2', 'impl-2', attempt=2),
            ev('11:00:00', 'foto impl-2: testes verdes 6/6', 'review', attempt=2),
            ev('11:10:00', 'portão review', 'reviewed', attempt=2),
            ev('11:12:00', 'integração', 'integration', attempt=2),
            ev('11:13:00', 'integrada em feat/x', 'done', status='done', attempt=2),
        ]}

BLOCKED = {'task': 'T-002', 'status': 'blocked', 'cycle': 1, 'attempt': 4, 'block_cause': 'attempts',
           'snapshots': {'impl-4': {'score': 'testes verdes 5/6'}}, 'history': [], 'events': [
               ev('12:00:00', 'begin', 'red'),
               ev('12:05:00', 'portão red', 'impl'),
               ev('12:06:00', 'tentativa 1', 'impl-1', attempt=1),
               ev('12:08:00', 'foto impl-1: falha', 'impl', attempt=1),
               ev('12:09:00', 'tentativa 2', 'impl-2', attempt=2),
               ev('12:10:00', 'queda na impl-2, interrompida não conta', 'impl', attempt=1),
               ev('12:11:00', 'tentativa 2', 'impl-2', attempt=2),
               ev('12:12:00', 'foto impl-2: falha', 'impl', attempt=2),
               ev('12:13:00', 'tentativa 3', 'impl-3', attempt=3),
               ev('12:14:00', 'foto impl-3: falha', 'impl', attempt=3),
               ev('12:15:00', 'tentativa 4', 'impl-4', attempt=4),
               ev('12:16:00', 'foto impl-4: testes verdes 5/6', 'impl', attempt=4),
               ev('12:17:00', 'bloqueio (attempts)', 'impl', status='blocked', attempt=4),
           ]}


def msg(at, mid, output, model='claude-sonnet-5-5'):
    return {'timestamp': '2026-11-20T%s.000Z' % at,
            'message': {'id': mid, 'model': model, 'content': [],
                        'usage': {'input_tokens': 0, 'output_tokens': output,
                                  'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}}}


def tool_use(at, uid, name, inp):
    return {'timestamp': '2026-11-20T%s.000Z' % at,
            'message': {'id': 'tu-' + uid, 'content': [{'type': 'tool_use', 'id': uid, 'name': name,
                                                        'input': inp}]}}


def notif(at, uid, tokens):
    return {'timestamp': '2026-11-20T%s.000Z' % at, 'type': 'user',
            'message': {'content': '<task-notification><tool-use-id>%s</tool-use-id>'
                                   '<subagent_tokens>%d</subagent_tokens></task-notification>' % (uid, tokens)}}


TRANSCRIPT = [
    msg('10:05:00', 'm1', 1000),
    tool_use('10:06:00', 'a1', 'Agent', {'subagent_type': 'bkhar:tester', 'description': 'RED'}),
    notif('10:09:00', 'a1', 20000),
    tool_use('10:07:00', 'q1', 'AskUserQuestion', {'questions': []}),
    msg('10:15:00', 'm2', 2000),
    msg('10:30:00', 'm3', 400000),
    msg('10:30:00', 'm3', 400000),
    tool_use('10:31:00', 'a2', 'Agent', {'subagent_type': 'bkhar:developer', 'description': 'impl-2'}),
    notif('10:50:00', 'a2', 90000),
    msg('11:05:00', 'm4', 3000),
    msg('12:07:00', 'm5', 5000),
    msg('13:00:00', 'm6', 7000),
    msg('09:00:00', 'm0', 999999),
]


def _rm_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def fixture():
    repo = tempfile.mkdtemp(prefix='bkhar-met-')
    subprocess.run(['git', '-C', repo, 'init', '-q'], capture_output=True)
    rec_dir = os.path.join(repo, '.git', 'bkhar', 'recovery')
    os.makedirs(rec_dir)
    for st in (DONE, BLOCKED):
        with io.open(os.path.join(rec_dir, '%s.json' % st['task']), 'w', encoding='utf-8') as fh:
            json.dump(st, fh, ensure_ascii=False)
    tdir = os.path.join(repo, 'transcripts')
    os.makedirs(tdir)
    with io.open(os.path.join(tdir, 's1.jsonl'), 'w', encoding='utf-8') as fh:
        for rec in TRANSCRIPT:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return repo, tdir


def test_build():
    print('\nmétrica sobre a fixture')
    repo, tdir = fixture()
    rows = metrics.build(repo, tdir, now='2026-11-20T14:17:00Z')
    by = {(r['task'], r['phase']): r for r in rows}
    check('janela red da T-001 com 10 min', by[('T-001', 'red')]['duration_s'] == 660, by.get(('T-001', 'red')))
    check('red junta o portão e a espera da tentativa 1', ('T-001', 'impl') not in by)
    check('impl-2 da T-001 com o pico de tokens', by[('T-001', 'impl-2')]['tokens'] == 400000,
          by.get(('T-001', 'impl-2')))
    check('mensagem repetida conta uma vez', sum(r['tokens'] for r in rows if r['task'] == 'T-001') == 406000,
          [r['tokens'] for r in rows])
    check('mensagem fora de janela não entra', all(r['tokens'] < 999999 for r in rows))
    check('custo da janela pela tabela', abs(by[('T-001', 'impl-2')]['cost_usd'] - 4.0) < 1e-6,
          by[('T-001', 'impl-2')]['cost_usd'])
    check('papel pelos subagentes', by[('T-001', 'red')]['roles'] == {'tester': 20000}, by[('T-001', 'red')])
    check('developer na impl-2', by[('T-001', 'impl-2')]['roles'] == {'developer': 90000})
    check('pergunta ao usuário contada', by[('T-001', 'red')]['questions'] == 1)
    check('resultado da tentativa', 'testes verdes 6/6' in by[('T-001', 'impl-2')]['outcome'],
          by[('T-001', 'impl-2')]['outcome'])
    check('revisão e integração viram fases', ('T-001', 'review') in by and ('T-001', 'integracao') in by)
    blk = by[('T-002', 'bloqueio')]
    check('bloqueio em aberto até agora', blk['open'] and blk['duration_s'] == 7200, blk)
    check('bloqueio conta a espera pelo usuário', blk['tokens'] == 7000, blk)
    check('arquivo jsonl gravado', os.path.isfile(os.path.join(repo, 'outputs', 'run', 'metrics', 'metrics.jsonl')))
    shutil.rmtree(repo, onerror=_rm_readonly)


def test_report():
    print('\nrelatório responde sozinho')
    repo, tdir = fixture()
    metrics.build(repo, tdir, now='2026-11-20T14:17:00Z')
    with io.open(os.path.join(repo, 'outputs', 'run', 'metrics', 'METRICAS.md'), encoding='utf-8') as fh:
        text = fh.read()
    check('fase que mais gasta', 'Fase que mais gasta: `impl`' in text, text[:400])
    check('onde travou', 'T-002' in text and 'bloqueada' in text and 'testes verdes 5/6' in text)
    check('queda contada', '| T-002 | bloqueada | 1 | 1 | 1 |' in text, text)
    check('papel developer', '| developer |' in text)
    check('limite declarado', 'terminais do Maestri' in text)
    shutil.rmtree(repo, onerror=_rm_readonly)


def test_empty():
    print('\nsem task')
    repo = tempfile.mkdtemp(prefix='bkhar-met-')
    subprocess.run(['git', '-C', repo, 'init', '-q'], capture_output=True)
    check('sem estado, nada gerado', metrics.build(repo, repo) == [])
    check('sem METRICAS.md', not os.path.exists(os.path.join(repo, 'outputs', 'run', 'metrics')))
    shutil.rmtree(repo, onerror=_rm_readonly)


def main():
    print('testes do metrics.py')
    for fn in (test_build, test_report, test_empty):
        try:
            fn()
        except Exception as exc:
            check('%s sem exceção' % fn.__name__, False, repr(exc))
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
