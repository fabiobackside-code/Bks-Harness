"""Testes do scripts/readiness.py: quando o modo autonomo é concedido e o que falta quando não é.

Uso: python tests/test_readiness.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('readiness', os.path.join(ROOT, 'scripts', 'readiness.py'))
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)

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


def doc(status, body=''):
    return '---\nprojeto: p\nversion: 1\nstatus: %s\n---\n\n# Doc\n\n%s' % (status, body)


GRAPH = {
    'projeto': 'p',
    'tasks': [
        {'id': 'T-001', 'tipo': 'desenho', 'papel': 'architect', 'lente': 'banco',
         'depende_de': [], 'consome': ['docs/canonical/PRD-p.md', 'docs/library/architecture/ARCH-p.md'],
         'produz': ['specs/contracts/banco.md'], 'arquivos': ['specs/contracts/banco.md']},
        {'id': 'T-002', 'tipo': 'construcao', 'papel': 'developer', 'lente': None,
         'depende_de': ['T-001'], 'consome': ['specs/contracts/banco.md'],
         'produz': ['app/api'], 'arquivos': ['app/api/Program.cs']},
    ],
}


def ready_project():
    root = tempfile.mkdtemp()
    write(root, '.bks-profile.json', json.dumps({
        'profile': 'backend', 'category': 'private',
        'axes': {'rigor': 'poc', 'mode': 'colaborativo'},
        'stack': {'backend': '.NET 10'}}))
    write(root, 'docs/canonical/CONTEXT.md', doc('revisado'))
    write(root, 'docs/canonical/PRD-p.md',
          doc('aprovado', '## Perguntas em aberto que bloqueiam decisão\n\nNenhuma.\n\n## Fim\n'))
    write(root, 'outputs/PLAN-p.md',
          doc('aprovado', '## 6. Questões em aberto\n\n- [x] Pergunta 1: resolvida.\n\n## 7. Fontes\n'))
    write(root, 'outputs/GRAPH-p.json', json.dumps(GRAPH))
    write(root, ARCH, arch('aprovado'))
    write(root, MODEL, arch('aprovado', 'modelo: c4-contexto\n'))
    return root


ARCH = 'docs/library/architecture/ARCH-p.md'
MODEL = 'docs/library/architecture/models/c4-contexto.md'


def arch(status, extra='', date='2026-11-04'):
    return '---\nprojeto: p\n%sversion: 1\nstatus: %s\natualizado: %s\n---\n\n# Arquitetura\n' % (
        extra, status, date)


def missing_of(result, level):
    for item in result['levels']:
        if item['level'] == level:
            return item['missing']
    return None


def test_granted():
    print('\nprojeto pronto')
    root = ready_project()
    try:
        r = readiness.evaluate(root)
        check('concede o modo com tudo aprovado', r['granted'], json.dumps(r, ensure_ascii=False))
        check('avisa que não há regra promovida',
              any('regra' in w for w in r['warnings']), r['warnings'])
        os.makedirs(os.path.join(root, 'brain', 'engineering', 'regras'))
        write(root, 'brain/engineering/regras/r1.md', doc('promovida'))
        r = readiness.evaluate(root)
        check('sem aviso de aprendizado com regra promovida', not r['warnings'], r['warnings'])
    finally:
        shutil.rmtree(root)


def test_context_and_plan():
    print('\ncontexto e plano')
    root = ready_project()
    try:
        write(root, 'docs/canonical/PRD-p.md', doc('rascunho'))
        r = readiness.evaluate(root)
        check('PRD em rascunho recusa', not r['granted'])
        check('diz que falta o PRD aprovado', any('PRD' in m for m in missing_of(r, 'Contexto')),
              missing_of(r, 'Contexto'))

        root2 = ready_project()
        os.remove(os.path.join(root2, 'outputs', 'GRAPH-p.json'))
        r = readiness.evaluate(root2)
        check('sem grafo recusa', not r['granted'])
        check('diz que falta o grafo', any('GRAPH' in m for m in missing_of(r, 'Plano')),
              missing_of(r, 'Plano'))
        shutil.rmtree(root2)

        root3 = ready_project()
        bad = json.loads(json.dumps(GRAPH))
        del bad['tasks'][1]['consome']
        write(root3, 'outputs/GRAPH-p.json', json.dumps(bad))
        r = readiness.evaluate(root3)
        check('task sem consome recusa', not r['granted'])
        check('aponta a task sem consome', any('T-002' in m for m in missing_of(r, 'Plano')),
              missing_of(r, 'Plano'))
        shutil.rmtree(root3)

        root4 = ready_project()
        write(root4, 'docs/canonical/CONTEXT.md', doc('rascunho'))
        r = readiness.evaluate(root4)
        check('canônico em rascunho recusa', not r['granted'])
        shutil.rmtree(root4)
    finally:
        shutil.rmtree(root)


def test_open_questions():
    print('\nquestões em aberto')
    root = ready_project()
    try:
        write(root, 'outputs/PLAN-p.md',
              doc('aprovado', '## 6. Questões em aberto\n\n- [ ] Pergunta 1: forma do mobile.\n'
                  '- [x] Pergunta 2: resolvida.\n\n## 7. Fontes\n'))
        r = readiness.evaluate(root)
        check('item aberto no PLAN recusa', not r['granted'])
        check('lista o item aberto', any('forma do mobile' in m for m in missing_of(r, 'Abertos')),
              missing_of(r, 'Abertos'))
        check('item marcado não conta', not any('resolvida' in m for m in missing_of(r, 'Abertos')))

        write(root, 'outputs/PLAN-p.md', doc('aprovado', '## 6. Questões em aberto\n\nNenhuma.\n'))
        write(root, 'docs/canonical/PRD-p.md',
              doc('aprovado', '## Perguntas em aberto que bloqueiam decisão\n\n'
                  '| # | Pergunta | Bloqueia |\n|---|---|---|\n| 1 | Mobile nativo? | fase 4 |\n'))
        r = readiness.evaluate(root)
        check('linha de tabela aberta no PRD recusa', not r['granted'])
        check('lista a pergunta da tabela', any('Mobile nativo' in m for m in missing_of(r, 'Abertos')),
              missing_of(r, 'Abertos'))
    finally:
        shutil.rmtree(root)


def test_architecture():
    print('\narquitetura')
    root = ready_project()
    try:
        os.remove(os.path.join(root, *ARCH.split('/')))
        r = readiness.evaluate(root)
        check('sem ARCH recusa', not r['granted'])
        check('diz que falta o ARCH', any('ARCH' in m for m in missing_of(r, 'Arquitetura') or []),
              missing_of(r, 'Arquitetura'))

        write(root, ARCH, arch('rascunho'))
        r = readiness.evaluate(root)
        check('ARCH em rascunho recusa', not r['granted'])

        write(root, ARCH, arch('aprovado'))
        write(root, MODEL, arch('rascunho', 'modelo: c4-contexto\n'))
        r = readiness.evaluate(root)
        check('modelo em rascunho recusa', not r['granted'])
        check('aponta o modelo', any('c4-contexto' in m for m in missing_of(r, 'Arquitetura')),
              missing_of(r, 'Arquitetura'))

        write(root, MODEL, arch('aprovado', 'modelo: c4-contexto\n'))
        write(root, 'decisions/ADR-009-cache.md', '# ADR-009\n\n> Status: aceito · 2026-11-09\n')
        r = readiness.evaluate(root)
        check('arquitetura defasada recusa', not r['granted'])
        check('diz o que está defasado', any('ADR-009' in m for m in missing_of(r, 'Arquitetura')),
              missing_of(r, 'Arquitetura'))
    finally:
        shutil.rmtree(root)


def test_stack():
    print('\nexecução')
    root = ready_project()
    try:
        write(root, '.bks-profile.json', json.dumps({
            'profile': 'backend', 'category': 'private', 'axes': {'rigor': 'poc'}}))
        r = readiness.evaluate(root)
        check('perfil sem stack recusa', not r['granted'])
        check('diz que falta a stack', bool(missing_of(r, 'Execução')), missing_of(r, 'Execução'))
    finally:
        shutil.rmtree(root)


def test_cli():
    print('\nlinha de comando')
    root = ready_project()
    try:
        code = readiness.main([root, '--json'])
        check('sai 0 quando concede', code == 0)
        write(root, 'outputs/PLAN-p.md', doc('rascunho'))
        code = readiness.main([root])
        check('sai 1 quando recusa', code == 1)
    finally:
        shutil.rmtree(root)


def main():
    print('testes do readiness.py')
    for fn in (test_granted, test_context_and_plan, test_open_questions, test_architecture,
               test_stack, test_cli):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
