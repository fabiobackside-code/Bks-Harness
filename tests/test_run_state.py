"""Testes do scripts/run_state.py: estado de cada task da onda, um escritor só.

Uso: python tests/test_run_state.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('run_state', os.path.join(ROOT, 'scripts', 'run_state.py'))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

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


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


GRAPH = {'projeto': 'p', 'tasks': [
    {'id': 'T-001', 'titulo': 'contrato do banco', 'tipo': 'desenho', 'papel': 'architect',
     'lente': 'banco', 'depende_de': [], 'consome': ['docs/library/architecture/ARCH-p.md'], 'produz': ['specs/contracts/banco.md'],
     'arquivos': ['specs/contracts/banco.md']},
    {'id': 'T-002', 'titulo': 'api', 'tipo': 'construcao', 'papel': 'developer', 'lente': None,
     'depende_de': ['T-001'], 'consome': ['specs/contracts/banco.md'], 'produz': ['app/api'],
     'arquivos': ['app/api/Program.cs']},
]}


def project():
    root = tempfile.mkdtemp()
    write(root, 'outputs/GRAPH-p.json', json.dumps(GRAPH))
    write(root, 'docs/library/architecture/ARCH-p.md', '---\nstatus: aprovado\n---\n')
    return root


def load(root, tid):
    return rs.get(root, tid)


def test_lifecycle():
    print('\nciclo de vida')
    root = project()
    try:
        rs.init(root)
        t1 = load(root, 'T-001')
        check('init cria cada task pendente na sua onda',
              t1['estado'] == 'pendente' and t1['onda'] == 1 and load(root, 'T-002')['onda'] == 2, t1)
        check('o arquivo fica em outputs/run/onda-N/',
              os.path.isfile(os.path.join(root, 'outputs', 'run', 'onda-2', 'T-002.json')))

        rs.start(root, 'T-001', worktree='../p-wt/T-001', model='opus')
        t1 = load(root, 'T-001')
        check('start marca em curso, worktree, modelo e início',
              t1['estado'] == 'em curso' and t1['worktree'] == '../p-wt/T-001'
              and t1['modelo'] == 'opus' and t1['inicio'], t1)

        rs.attempt(root, 'T-001', 1)
        rs.attempt(root, 'T-001', 2)
        check('attempt registra a tentativa', load(root, 'T-001')['estado'] == 'tentativa 2')

        rs.finish(root, 'T-001', 'passou', cost=0.42)
        t1 = load(root, 'T-001')
        check('finish grava resultado, fim e custo',
              t1['estado'] == 'passou' and t1['fim'] and t1['custo_usd'] == 0.42, t1)
        check('cada transição vira evento', len(t1['eventos']) >= 4, t1['eventos'])
        init_again = rs.init(root)
        check('init de novo não apaga o que andou', load(root, 'T-001')['estado'] == 'passou')
    finally:
        shutil.rmtree(root)


def test_refusals():
    print('\ntransições recusadas')
    root = project()
    try:
        rs.init(root)
        for name, fn in (
                ('tentativa sem start', lambda: rs.attempt(root, 'T-001', 1)),
                ('finish sem start', lambda: rs.finish(root, 'T-001', 'passou')),
                ('task que não está no grafo', lambda: rs.start(root, 'T-999')),
        ):
            try:
                fn()
                check('recusa %s' % name, False)
            except rs.StateError:
                check('recusa %s' % name, True)
        rs.start(root, 'T-001')
        try:
            rs.attempt(root, 'T-001', 5)
            check('recusa a 5ª tentativa', False)
        except rs.StateError:
            check('recusa a 5ª tentativa', True)
        try:
            rs.finish(root, 'T-001', 'quase')
            check('recusa resultado desconhecido', False)
        except rs.StateError:
            check('recusa resultado desconhecido', True)
        try:
            rs.start(root, 'T-002')
            check('recusa start de task não liberada', False)
        except rs.StateError:
            check('recusa start de task não liberada', True)
    finally:
        shutil.rmtree(root)


def test_pause_and_show():
    print('\npausa e tabela')
    root = project()
    try:
        rs.init(root)
        rs.set_paused(root, True)
        try:
            rs.start(root, 'T-001')
            check('onda pausada recusa start', False)
        except rs.StateError:
            check('onda pausada recusa start', True)
        rs.set_paused(root, False)
        rs.start(root, 'T-001')
        table = rs.render(root)
        check('a tabela mostra a task e o estado', 'T-001' in table and 'em curso' in table, table)
        snap = rs.snapshot(root)
        check('o snapshot traz tasks, ondas e pausa',
              {'tasks', 'waves', 'paused'} <= set(snap) and len(snap['tasks']) == 2, snap.keys())
    finally:
        shutil.rmtree(root)


def test_inbox():
    print('\ninbox do painel')
    root = project()
    try:
        rs.init(root)
        write(root, '.bks-profile.json', json.dumps({'profile': 'backend', 'category': 'p',
                                                     'axes': {'mode': 'autonomo'}}))
        r1 = rs.submit(root, {'tipo': 'pausar'})
        r2 = rs.submit(root, {'tipo': 'mensagem', 'task': 'T-001', 'texto': 'use o schema public'})
        r3 = rs.submit(root, {'tipo': 'modelo', 'papel': 'developer', 'modelo': 'opus'})
        check('submit grava na inbox', len(rs.pending(root)) == 3, rs.pending(root))
        check('submit devolve id', r1['id'] and r1['id'] != r2['id'])
        for name, req in (('tipo desconhecido', {'tipo': 'apagar'}),
                          ('modelo fora da lista', {'tipo': 'modelo', 'papel': 'developer', 'modelo': 'gpt'}),
                          ('papel desconhecido', {'tipo': 'modelo', 'papel': 'planner', 'modelo': 'opus'}),
                          ('mensagem sem texto', {'tipo': 'mensagem', 'task': 'T-001'}),
                          ('task fora do grafo', {'tipo': 'mensagem', 'task': 'T-999', 'texto': 'x'})):
            try:
                rs.submit(root, req)
                check('recusa pedido com %s' % name, False)
            except rs.StateError:
                check('recusa pedido com %s' % name, True)
        check('pedido recusado não entra na inbox', len(rs.pending(root)) == 3)

        rs.applied(root, r1['id'])
        check('pausar aplicado pausa a execução', rs.paused(root))
        rs.applied(root, r2['id'])
        events = [e['o_que'] for e in rs.get(root, 'T-001')['eventos']]
        check('mensagem aplicada vira evento da task', any('schema public' in e for e in events), events)
        rs.applied(root, r3['id'])
        profile = json.load(io.open(os.path.join(root, '.bks-profile.json'), encoding='utf-8'))
        check('troca de modelo aplicada grava o mapa models',
              profile.get('models', {}).get('developer') == 'opus', profile)
        check('aplicado sai da inbox pendente', rs.pending(root) == [])
        check('aplicado fica guardado em inbox/aplicados/',
              len(os.listdir(os.path.join(root, 'outputs', 'run', 'inbox', 'aplicados'))) == 3)
        try:
            rs.applied(root, r1['id'])
            check('recusa aplicar duas vezes', False)
        except rs.StateError:
            check('recusa aplicar duas vezes', True)
    finally:
        shutil.rmtree(root)


def main():
    print('testes do run_state.py')
    for fn in (test_lifecycle, test_refusals, test_pause_and_show, test_inbox):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
