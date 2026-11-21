"""Testes do scripts/session_cost.py: onde ele procura os transcripts.

Uso: python tests/test_session_cost.py
"""
import importlib.util
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('session_cost', os.path.join(ROOT, 'scripts', 'session_cost.py'))
session_cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_cost)

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


def test_projects_dir():
    print('\npasta dos transcripts')
    got = session_cost.projects_dir({'CLAUDE_CONFIG_DIR': os.path.join('X:', os.sep, 'Claude')})
    check('CLAUDE_CONFIG_DIR define a pasta', got == Path('X:', os.sep, 'Claude', 'projects'), str(got))
    got = session_cost.projects_dir({})
    check('sem a variável vale ~/.claude', got == Path(os.path.expanduser('~'), '.claude', 'projects'), str(got))
    got = session_cost.projects_dir({'CLAUDE_CONFIG_DIR': ''})
    check('variável vazia vale ~/.claude', got == Path(os.path.expanduser('~'), '.claude', 'projects'), str(got))
    got = session_cost.projects_dir({'CLAUDE_CONFIG_DIR': os.path.join('~', 'cfg')})
    check('til na variável é expandido', got == Path(os.path.expanduser('~'), 'cfg', 'projects'), str(got))


def test_current_models_priced():
    print('\npreço dos modelos atuais')
    pricing = session_cost.load_pricing()
    for model in ('claude-opus-5-5', 'claude-sonnet-5-5', 'claude-haiku-5-5', 'claude-fable-5-2'):
        got = session_cost.resolve_model(pricing, model)
        check('%s tem entrada própria' % model, got == model, 'resolveu para %r' % got)
    expected = {'claude-sonnet-5': (2.00, 10.00), 'claude-fable-5': (10.00, 50.00),
                'claude-opus-5-5': (4.00, 20.00), 'claude-haiku-5-5': (0.10, 0.50)}
    for model, (inp, out) in expected.items():
        p = pricing['models'].get(model, {})
        check('%s a US$ %.2f / %.2f' % (model, inp, out), (p.get('input'), p.get('output')) == (inp, out),
              str(p))


def main():
    print('testes do session_cost.py')
    test_projects_dir()
    test_current_models_priced()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
