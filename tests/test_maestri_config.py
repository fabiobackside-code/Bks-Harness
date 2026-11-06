"""Testes do scripts/maestri_config.py: liga e desliga por perfil, valida os terminais e decide a rota.

Uso: python tests/test_maestri_config.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('maestri_config', os.path.join(ROOT, 'scripts', 'maestri_config.py'))
mc = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
spec.loader.exec_module(mc)

failures = []
checks = 0
IN = {'MAESTRI_TERMINAL_ID': 't1'}
OUT = {}


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


def project(block=None):
    root = tempfile.mkdtemp()
    profile = {'profile': 'fullstack', 'axes': {'mode': 'colaborativo'}}
    if block is not None:
        profile['maestri'] = block
    with io.open(os.path.join(root, '.bks-profile.json'), 'w', encoding='utf-8') as fh:
        json.dump(profile, fh)
    return root


def profile(root):
    with io.open(os.path.join(root, '.bks-profile.json'), encoding='utf-8') as fh:
        return json.load(fh)


def listing(me='manager', agents=('architect', 'developer', 'tester', 'quality', 'security', 'scribe', 'ops'),
            notes=('status',)):
    lines = ['You:', '  - name: "%s"' % me, '', 'Connected agents:']
    lines += ['  - name: "%s"' % a for a in agents]
    lines += ['', 'Connected notes (use `maestri note read/write/edit`):']
    lines += ['  - name: "%s"' % n for n in notes]
    return '\n'.join(lines) + '\n'


def test_parse():
    print('\nleitura do maestri list')
    seen = mc.parse_list(listing())
    check('nome deste terminal', seen['me'] == 'manager')
    check('agentes conectados', len(seen['agents']) == 7 and 'ops' in seen['agents'])
    check('notas conectadas', seen['notes'] == ['status'])
    empty = mc.parse_list('You:\n  - name: "Claude Code"\n\nNo connected agents, notes, or portals.\n')
    check('sem conexões', empty['me'] == 'Claude Code' and empty['agents'] == [] and empty['notes'] == [])


def test_on_off():
    print('\nliga e desliga')
    root = project()
    check('sem bloco vale desligado', mc.load(root) is None and not mc.enabled(root))
    mc.turn_on(root, {'developer': 'dev'})
    block = profile(root)['maestri']
    check('on grava o bloco ligado', block['enabled'] is True)
    check('on aceita nome próprio de terminal', block['roles']['developer'] == 'dev')
    check('on preenche os padrões', block['roles']['architect'] == 'architect' and block['executors'] == {'ops': 'ops'})
    check('o resto do perfil fica intacto', profile(root)['axes'] == {'mode': 'colaborativo'})
    mc.turn_off(root)
    check('off só desliga e guarda o mapa', profile(root)['maestri']['enabled'] is False
          and profile(root)['maestri']['roles']['developer'] == 'dev')
    mc.turn_on(root)
    check('on de novo religa sem perder o mapa', mc.enabled(root) and mc.load(root)['roles']['developer'] == 'dev')
    mc.turn_on(root, delegate={'prd': 'architect', 'save': 'local'})
    block = mc.load(root)
    check('delegação por comando', block['delegate']['prd'] == 'architect' and 'save' not in block['delegate'])
    for bad in ({'arch': 'quality'}, {'save': 'scribe'}, {'arch': 'ninguem'}, {'loop': 'ops'}):
        try:
            mc.turn_on(root, delegate=bad)
            check('recusa delegação inválida %s' % bad, False)
        except mc.ConfigError:
            check('recusa delegação inválida %s' % bad, True)
    check('delegação recusada não muda o perfil', mc.load(root)['delegate'].get('arch') == 'architect')
    check('padrão: arch, prd e plan ao architect; o resto ao ops',
          mc.DEFAULT['delegate'] == {'arch': 'architect', 'prd': 'architect', 'plan': 'architect',
                                      'canonize': 'ops', 'save': 'ops', 'maintainability': 'ops'})
    try:
        mc.turn_on(root, {'developer': ' '})
        check('recusa terminal sem nome', False)
    except mc.ConfigError:
        check('recusa terminal sem nome', True)


def test_check():
    print('\nvalidação dos terminais')
    root = project({'enabled': True})
    check('tudo conectado passa', mc.check(root, listing(), IN) == [], str(mc.check(root, listing(), IN)))
    check('fora do Maestri falha', any('MAESTRI_TERMINAL_ID' in p for p in mc.check(root, listing(), OUT)))
    check('sem maestri list falha', mc.check(root, None, IN) == ['maestri list não respondeu'])
    problems = mc.check(root, listing(me='Claude Code'), IN)
    check('terminal com nome errado', any("chama-se 'Claude Code'" in p for p in problems))
    problems = mc.check(root, listing(agents=('architect', 'developer', 'tester', 'quality', 'scribe', 'ops')), IN)
    check('papel faltando', any("papel security" in p for p in problems), str(problems))
    problems = mc.check(root, listing(agents=('architect', 'developer', 'tester', 'quality', 'security', 'scribe')), IN)
    check('executor faltando', any("executor ops" in p for p in problems), str(problems))
    problems = mc.check(root, listing(notes=('teste-spike-4',)), IN)
    check('nota faltando ensina a criar', any('maestri note create --name "status"' in p for p in problems))
    problems = mc.check(root, listing(agents=('architect', 'developer', 'tester', 'quality', 'security',
                                              'scribe', 'ops', 'extra')), IN)
    check('terminal fora do mapa avisado', any('extra' in p for p in problems))
    check('maiúsculas não importam', mc.check(root, listing(agents=('Architect', 'developer', 'tester', 'quality',
                                                                     'security', 'scribe', 'OPS'),
                                                            notes=('Status',)), IN) == [])
    check('desligado falha com o motivo', mc.check(project({'enabled': False}), listing(), IN)
          == ['integração desligada (maestri.enabled = false)'])
    check('sem bloco ensina o on', 'maestri on' in mc.check(project(), listing(), IN)[0])


def test_route():
    print('\nrota por papel')
    root = project({'enabled': True, 'roles': {'developer': 'dev'}})
    check('papel conectado vai ao terminal', mc.route(root, 'architect', listing(), IN) == ('terminal', 'architect'))
    check('nome mapeado é usado',
          mc.route(root, 'developer', listing(agents=('dev',)), IN) == ('terminal', 'dev'))
    kind, why = mc.route(root, 'developer', listing(), IN)
    check('terminal ausente cai para subagente', kind == 'subagente' and "'dev'" in why)
    check('fora do Maestri vai para subagente', mc.route(root, 'architect', listing(), OUT)[0] == 'subagente')
    check('desligado vai para subagente',
          mc.route(project({'enabled': False}), 'architect', listing(), IN)[0] == 'subagente')
    check('sem bloco vai para subagente', mc.route(project(), 'architect', listing(), IN)[0] == 'subagente')
    try:
        mc.route(root, 'manager', listing(), IN)
        check('papel desconhecido recusado', False)
    except mc.ConfigError:
        check('papel desconhecido recusado', True)


def test_delegate():
    print('\ndelegação de comando')
    root = project({'enabled': True})
    check('save do manager vai ao ops', mc.delegate(root, 'save', listing(), IN) == ('terminal', 'ops'))
    check('arch do manager vai ao architect', mc.delegate(root, 'arch', listing(), IN) == ('terminal', 'architect'))
    kind, why = mc.delegate(root, 'arch', listing(me='architect', agents=('manager',)), IN)
    check('no próprio architect o arch roda local', kind == 'local' and 'este é o terminal architect' in why)
    kind, why = mc.delegate(root, 'save', listing(me='ops', agents=('manager',)), IN)
    check('no próprio ops roda local', kind == 'local' and 'este é o terminal ops' in why)
    kind, why = mc.delegate(root, 'save', listing(me='architect', agents=('manager',)), IN)
    check('só o manager delega', kind == 'local' and 'só o manager' in why)
    check('comando não delegável roda local', mc.delegate(root, 'loop', listing(), IN)[0] == 'local')
    check('executor ausente roda local', mc.delegate(root, 'save', listing(agents=('architect',)), IN)[0] == 'local')
    check('fora do Maestri roda local', mc.delegate(root, 'save', listing(), OUT)[0] == 'local')
    check('desligado roda local', mc.delegate(project({'enabled': False}), 'save', listing(), IN)[0] == 'local')
    root = project({'enabled': True, 'delegate': {'prd': 'architect'}})
    check('prd ao architect', mc.delegate(root, 'prd', listing(), IN) == ('terminal', 'architect'))
    check('comando fora do mapa roda local', mc.delegate(root, 'save', listing(), IN)[0] == 'local')


def test_cli():
    print('\nlinha de comando')
    root = project()
    check('show sem bloco', mc.main(['show', root]) == 0)
    old = os.environ.pop('MAESTRI_TERMINAL_ID', None)
    try:
        check('on fora do Maestri grava e acusa a falta', mc.main(['on', root, '--role', 'developer=dev',
                                                                    '--delegate', 'prd=architect']) == 1)
    finally:
        if old is not None:
            os.environ['MAESTRI_TERMINAL_ID'] = old
    check('on gravou pela linha', mc.load(root)['roles']['developer'] == 'dev'
          and mc.load(root)['delegate']['prd'] == 'architect')
    check('on recusa par sem =', mc.main(['on', root, '--role', 'developer']) == 1)
    check('off', mc.main(['off', root]) == 0 and not mc.enabled(root))
    check('route sem papel recusa', mc.main(['route', root]) == 1)
    check('delegate sem comando recusa', mc.main(['delegate', root]) == 1)


def main():
    print('testes do maestri_config.py')
    for fn in (test_parse, test_on_off, test_check, test_route, test_delegate, test_cli):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
