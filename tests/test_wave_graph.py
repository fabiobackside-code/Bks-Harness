"""Testes do scripts/wave_graph.py: validação do grafo, ondas e liberação de task.

Uso: python tests/test_wave_graph.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('wave_graph', os.path.join(ROOT, 'scripts', 'wave_graph.py'))
wg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wg)

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


def task(tid, tipo='construcao', papel='developer', deps=(), consome=(), produz=(), arquivos=()):
    return {'id': tid, 'tipo': tipo, 'papel': papel, 'lente': None, 'depende_de': list(deps),
            'consome': list(consome), 'produz': list(produz), 'arquivos': list(arquivos)}


def graph(*tasks):
    return {'projeto': 'p', 'tasks': list(tasks)}


ARCH = 'docs/library/architecture/ARCH-p.md'

BASE = graph(
    task('T-001', 'desenho', 'architect', consome=['docs/canonical/PRD-p.md', ARCH],
         produz=['specs/contracts/banco.md'], arquivos=['specs/contracts/banco.md']),
    task('T-002', 'desenho', 'architect', consome=['docs/canonical/PRD-p.md', ARCH],
         produz=['specs/contracts/api.md'], arquivos=['specs/contracts/api.md']),
    task('T-003', consome=['specs/contracts/banco.md', 'specs/contracts/api.md'],
         produz=['app/api'], arquivos=['app/api/Program.cs']),
    task('T-004', 'front', consome=['app/api'], produz=['app/web'], arquivos=['app/web/index.tsx']),
)


def test_validate():
    print('\nvalidação')
    check('grafo correto não tem problema', wg.validate(BASE) == [], wg.validate(BASE))

    dup = graph(task('T-001'), task('T-001'))
    check('id repetido é problema', any('T-001' in p and 'repetido' in p for p in wg.validate(dup)),
          wg.validate(dup))

    ghost = graph(task('T-001', deps=['T-009']))
    check('dependência inexistente é problema', any('T-009' in p for p in wg.validate(ghost)))

    cycle = graph(task('T-001', deps=['T-002']), task('T-002', deps=['T-001']))
    check('ciclo é problema', any('ciclo' in p for p in wg.validate(cycle)), wg.validate(cycle))

    clash = graph(task('T-001', arquivos=['app/a.cs']), task('T-002', arquivos=['app/a.cs']))
    check('duas tasks da mesma onda no mesmo arquivo é problema',
          any('app/a.cs' in p for p in wg.validate(clash)), wg.validate(clash))

    no_arch = graph(task('T-001', 'desenho', 'architect', consome=['docs/canonical/PRD-p.md'],
                         produz=['specs/contracts/banco.md'], arquivos=['specs/contracts/banco.md']))
    check('desenho sem o ARCH no consome é problema',
          any('T-001' in p and 'ARCH' in p for p in wg.validate(no_arch)), wg.validate(no_arch))

    serial = graph(task('T-001', arquivos=['app/a.cs']),
                   task('T-002', deps=['T-001'], arquivos=['app/a.cs']))
    check('o mesmo arquivo em ondas diferentes é permitido', wg.validate(serial) == [],
          wg.validate(serial))

    role = graph(task('T-001', papel='planner'))
    check('papel desconhecido é problema', any('planner' in p for p in wg.validate(role)))

    kind = graph(task('T-001', tipo='mágica'))
    check('tipo desconhecido é problema', any('mágica' in p for p in wg.validate(kind)))


def test_waves():
    print('\nondas')
    waves = wg.waves(BASE)
    check('desenho em paralelo na primeira onda', waves[0] == ['T-001', 'T-002'], waves)
    check('construção depois do que consome', waves[1] == ['T-003'], waves)
    check('front por último', waves[2] == ['T-004'], waves)


def test_ready():
    print('\nliberação')
    root = tempfile.mkdtemp()
    try:
        write(root, 'docs/canonical/PRD-p.md', '---\nstatus: aprovado\n---\n')
        write(root, ARCH, '---\nstatus: rascunho\n---\n')
        ready = wg.ready(BASE, root, {})
        check('ARCH em rascunho segura o desenho', ready == [], ready)
        write(root, ARCH, '---\nstatus: aprovado\n---\n')
        ready = wg.ready(BASE, root, {})
        check('libera as tasks cujas entradas estão aprovadas', ready == ['T-001', 'T-002'], ready)

        write(root, 'specs/contracts/banco.md', '---\nstatus: rascunho\n---\n')
        write(root, 'specs/contracts/api.md', '---\nstatus: aprovado\n---\n')
        state = {'T-001': 'passou', 'T-002': 'passou'}
        ready = wg.ready(BASE, root, state)
        check('contrato em rascunho segura a construção', ready == [], ready)

        write(root, 'specs/contracts/banco.md', '---\nstatus: aprovado\n---\n')
        ready = wg.ready(BASE, root, state)
        check('contratos aprovados liberam a construção', ready == ['T-003'], ready)

        ready = wg.ready(BASE, root, {'T-001': 'em curso', 'T-002': 'passou'})
        check('produtor ainda em curso segura quem consome', 'T-003' not in ready, ready)

        state = {'T-001': 'passou', 'T-002': 'passou', 'T-003': 'bloqueada'}
        os.makedirs(os.path.join(root, 'app', 'api'))
        ready = wg.ready(BASE, root, state)
        check('BLOQUEIO segura a cadeia que depende', 'T-004' not in ready, ready)

        many = graph(*[task('T-%03d' % i, consome=['docs/canonical/PRD-p.md'],
                            arquivos=['app/%d.cs' % i]) for i in range(1, 8)])
        ready = wg.ready(many, root, {})
        check('libera no máximo 4 tasks ao mesmo tempo', len(ready) == wg.MAX_PARALLEL == 4, ready)
        ready = wg.ready(many, root, {'T-001': 'em curso', 'T-002': 'tentativa 2'})
        check('tasks em curso contam no teto', len(ready) == 2, ready)
    finally:
        shutil.rmtree(root)


def test_cli():
    print('\nlinha de comando')
    root = tempfile.mkdtemp()
    try:
        write(root, 'outputs/GRAPH-p.json', json.dumps(BASE))
        check('validate sai 0 com grafo correto', wg.main(['validate', root]) == 0)
        write(root, 'outputs/GRAPH-p.json', json.dumps(graph(task('T-001'), task('T-001'))))
        check('validate sai 1 com problema', wg.main(['validate', root]) == 1)
        check('sem grafo sai 2', wg.main(['validate', tempfile.gettempdir() + '/nao-existe']) == 2)
    finally:
        shutil.rmtree(root)


def main():
    print('testes do wave_graph.py')
    for fn in (test_validate, test_waves, test_ready, test_cli):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
