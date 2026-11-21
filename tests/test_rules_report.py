"""Testes do scripts/rules_report.py: validação do registro de regras e relatório gerado."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'rules_report.py')
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print('%-5s %s%s' % ('OK' if ok else 'FALHA', name, '' if ok else '  ' + detail))


def kit(rules, guards=('g1.py',)):
    root = tempfile.mkdtemp(prefix='bkhar-rules-')
    for rel in ('docs/fonte.md', 'agents/quality.md', 'hooks/tests/test_g1.py'):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        with open(os.path.join(root, rel), 'w', encoding='utf-8') as f:
            f.write('# Fonte\n\n## Seção boa\n\nTeto: 5 linhas\n')
    os.makedirs(os.path.join(root, 'hooks', 'scripts'), exist_ok=True)
    hooks = []
    for g in guards:
        open(os.path.join(root, 'hooks', 'scripts', g), 'w').close()
        hooks.append({'matcher': 'Write', 'hooks': [
            {'type': 'command', 'command': 'python "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/%s"' % g}]})
    with open(os.path.join(root, 'hooks', 'hooks.json'), 'w') as f:
        json.dump({'hooks': {'PreToolUse': hooks}}, f)
    with open(os.path.join(root, 'rules.json'), 'w', encoding='utf-8') as f:
        json.dump({'rules': rules}, f)
    return root


def run(root, *args):
    r = subprocess.run([sys.executable, SCRIPT, '--root', root, *args], capture_output=True,
                       text=True, encoding='utf-8')
    return r.returncode, r.stdout + r.stderr


def comp(onde='hooks/scripts/g1.py', **extra):
    s = {'tipo': 'computacional', 'onde': onde, 'teste': 'hooks/tests/test_g1.py',
         'camadas': ['hook'], 'forca': 'direto'}
    s.update(extra)
    return s


def rule(rid, sensores, alvo='codigo', fonte='docs/fonte.md'):
    return {'id': rid, 'regra': 'regra %s' % rid, 'alvo': alvo, 'fonte': fonte, 'sensores': sensores}


INF = {'tipo': 'inferencial', 'onde': 'agents/quality.md', 'camadas': ['revisao'], 'forca': 'direto'}
VALID = [dict(rule('COD-01', [comp()]), secao='Seção boa',
              parametros=[{'nome': 'teto', 'valor': '5', 'em': [
                  {'arquivo': 'docs/fonte.md', 'trecho': 'Teto: 5 linhas'},
                  {'arquivo': 'hooks/tests/test_g1.py', 'trecho': 'Teto: 5 linhas'}]}]), rule('COD-02', [INF]), rule('DOC-01', [], alvo='documentacao'),
         rule('KIT-01', [comp(forca='aviso')], alvo='kit')]

root = kit(VALID)
code, out = run(root)
check('registro válido: saída 0', code == 0, out)
report = open(os.path.join(root, 'docs', 'regras.md'), encoding='utf-8').read()
check('relatório conta as regras', 'Regras: 4' in report, report[:300])
check('relatório conta computacional', 'com sensor computacional: 2' in report, report[:300])
check('relatório separa indireto e aviso', '1 de aviso' in report, report[:300])
check('relatório conta só inferencial', 'só inferencial: 1' in report, report[:300])
check('relatório conta sem sensor', 'sem sensor: 1' in report, report[:300])
check('relatório lista a sem sensor', 'DOC-01' in report.split('## Sem sensor')[1].split('##')[0])
check('relatório lista o parâmetro vinculado', 'teto' in report.split('## Parâmetros vinculados')[-1]
      and '## Parâmetros vinculados' in report, report)
check('--check em dia: saída 0', run(root, '--check')[0] == 0)
with open(os.path.join(root, 'docs', 'regras.md'), 'a', encoding='utf-8') as f:
    f.write('\nmexido à mão\n')
code, out = run(root, '--check')
check('--check com relatório defasado: saída 1', code == 1 and 'defasado' in out, out)
shutil.rmtree(root, ignore_errors=True)

cases = [
    ('sensor fantasma', [rule('COD-01', [comp(onde='hooks/scripts/nao_existe.py')])], 'nao_existe.py'),
    ('teste do sensor inexistente', [rule('COD-01', [comp(teste='hooks/tests/nada.py')])], 'nada.py'),
    ('fonte inexistente', [rule('COD-01', [comp()], fonte='docs/sumiu.md')], 'sumiu.md'),
    ('seção inexistente na fonte', [dict(rule('COD-01', [comp()]), secao='Não existe')], 'Não existe'),
    ('parâmetro divergente entre guia e sensor',
     [dict(rule('COD-01', [comp()]), parametros=[{'nome': 'teto', 'valor': '5', 'em': [
         {'arquivo': 'docs/fonte.md', 'trecho': 'Seção boa'},
         {'arquivo': 'hooks/scripts/g1.py', 'trecho': 'MAX = 5'}]}])], 'MAX = 5'),
    ('parâmetro sem o valor no trecho',
     [dict(rule('COD-01', [comp()]), parametros=[{'nome': 'teto', 'valor': '7', 'em': [
         {'arquivo': 'docs/fonte.md', 'trecho': 'Seção boa'}]}])], 'teto'),
    ('parâmetro em arquivo inexistente',
     [dict(rule('COD-01', [comp()]), parametros=[{'nome': 'teto', 'valor': '5', 'em': [
         {'arquivo': 'docs/sumiu.md', 'trecho': 'x 5'}]}])], 'sumiu.md'),
    ('id repetido', [rule('COD-01', [comp()]), rule('COD-01', [])], 'COD-01'),
    ('alvo inválido', [rule('COD-01', [comp()], alvo='outro')], 'outro'),
    ('tipo de sensor inválido', [rule('COD-01', [comp(tipo='magico')])], 'magico'),
    ('camada inválida', [rule('COD-01', [comp(camadas=['nuvem'])])], 'nuvem'),
    ('força inválida', [rule('COD-01', [comp(forca='talvez')])], 'talvez'),
    ('regra sem enunciado', [{'id': 'COD-01', 'alvo': 'codigo', 'fonte': 'docs/fonte.md', 'sensores': [comp()]}],
     'regra'),
]
for name, rules, needle in cases:
    root = kit(rules)
    code, out = run(root)
    check('%s: saída 1 e nomeia o problema' % name, code == 1 and needle in out, out)
    shutil.rmtree(root, ignore_errors=True)

root = kit([rule('COD-01', [comp()])], guards=('g1.py', 'g2.py'))
code, out = run(root)
check('guarda órfão: saída 1 e nomeia o guarda', code == 1 and 'g2.py' in out, out)
shutil.rmtree(root, ignore_errors=True)

code, out = run(ROOT, '--check')
check('registro do kit válido e relatório em dia', code == 0, out)

fail = results.count(False)
print('\n%d verificacoes, %d falhas' % (len(results), fail))
sys.exit(1 if fail else 0)
