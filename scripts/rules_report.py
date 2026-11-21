"""Valida o registro de regras (rules.json) e gera o relatório docs/regras.md.

Uso: rules_report.py [--root DIR] [--check]
Recusa sensor fantasma (aponta para arquivo inexistente) e guarda órfão (hook que não verifica regra).
Com --check, não escreve: sai 1 se o registro for inválido ou o relatório estiver defasado.
"""
import json
import os
import re
import sys

ALVOS = ('codigo', 'documentacao', 'processo', 'kit')
TIPOS = ('computacional', 'inferencial')
CAMADAS = ('hook', 'pre-commit', 'ci', 'suite', 'script', 'revisao')
FORCAS = ('direto', 'indireto', 'aviso')
REPORT = os.path.join('docs', 'regras.md')
HOOK_SCRIPT = re.compile(r'hooks/scripts/([a-z0-9_]+\.py)')
HEADING = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.M)


def load(root):
    with open(os.path.join(root, 'rules.json'), encoding='utf-8') as f:
        return json.load(f)['rules']


def headings(root, rel):
    with open(os.path.join(root, *rel.split('/')), encoding='utf-8') as f:
        return {m.group(1).strip() for m in HEADING.finditer(f.read())}


def parameter_problems(root, rid, param, exists):
    found = []
    name, value = param.get('nome') or '?', str(param.get('valor') or '')
    for place in param.get('em') or []:
        rel, snippet = place.get('arquivo'), place.get('trecho') or ''
        if not re.search(r'(?<![\w.])%s(?![\w.])' % re.escape(value), snippet):
            found.append('%s: parâmetro "%s" = %s não aparece no trecho "%s"' % (rid, name, value, snippet))
        elif not exists(rel):
            found.append('%s: parâmetro "%s": %s não existe' % (rid, name, rel))
        else:
            with open(os.path.join(root, *rel.split('/')), encoding='utf-8') as f:
                if snippet not in f.read():
                    found.append('%s: parâmetro "%s": o trecho "%s" sumiu de %s; guia e sensor divergem'
                                 % (rid, name, snippet, rel))
    return found


def problems(root, rules):
    found, seen = [], set()

    def exists(rel):
        return isinstance(rel, str) and os.path.exists(os.path.join(root, *rel.split('/')))

    for r in rules:
        rid = r.get('id') or '?'
        if rid in seen:
            found.append('%s: id repetido' % rid)
        seen.add(rid)
        if not (r.get('regra') or '').strip():
            found.append('%s: sem enunciado em "regra"' % rid)
        if r.get('alvo') not in ALVOS:
            found.append('%s: alvo %r fora de %s' % (rid, r.get('alvo'), ', '.join(ALVOS)))
        if not exists(r.get('fonte')):
            found.append('%s: fonte %s não existe' % (rid, r.get('fonte')))
        elif r.get('secao') and r['secao'] not in headings(root, r['fonte']):
            found.append('%s: seção "%s" não existe em %s' % (rid, r['secao'], r['fonte']))
        for p in r.get('parametros') or []:
            found += parameter_problems(root, rid, p, exists)
        for s in r.get('sensores') or []:
            if s.get('tipo') not in TIPOS:
                found.append('%s: tipo de sensor %r inválido' % (rid, s.get('tipo')))
            if not exists(s.get('onde')):
                found.append('%s: sensor fantasma, %s não existe' % (rid, s.get('onde')))
            if s.get('teste') is not None and not exists(s.get('teste')):
                found.append('%s: teste do sensor %s não existe' % (rid, s.get('teste')))
            for c in s.get('camadas') or []:
                if c not in CAMADAS:
                    found.append('%s: camada %r inválida' % (rid, c))
            if s.get('forca') not in FORCAS:
                found.append('%s: força %r inválida' % (rid, s.get('forca')))

    with open(os.path.join(root, 'hooks', 'hooks.json'), encoding='utf-8') as f:
        declared = set(HOOK_SCRIPT.findall(f.read()))
    used = {os.path.basename(s.get('onde') or '') for r in rules for s in r.get('sensores') or []}
    for guard in sorted(declared - used):
        found.append('guarda órfão: %s não verifica nenhuma regra registrada' % guard)
    return found


def computational(rule):
    return [s for s in rule.get('sensores') or [] if s.get('tipo') == 'computacional']


def best_force(rule):
    forces = {s.get('forca') for s in computational(rule)}
    return next(f for f in FORCAS if f in forces)


def classify(rule):
    if computational(rule):
        return 'computacional'
    if rule.get('sensores'):
        return 'inferencial'
    return 'nenhum'


def sensor_text(s):
    extra = '' if s.get('forca') == 'direto' else ', %s' % s.get('forca')
    return '%s `%s` (%s%s)' % ('C' if s['tipo'] == 'computacional' else 'I', s['onde'],
                               ', '.join(s.get('camadas') or []), extra)


def render(rules):
    kinds = [classify(r) for r in rules]
    comp = [r for r in rules if classify(r) == 'computacional']
    indirect = sum(1 for r in comp if best_force(r) == 'indireto')
    warn = sum(1 for r in comp if best_force(r) == 'aviso')
    lines = [
        '# Regras do bkhar e seus sensores', '',
        '> Gerado por `scripts/rules_report.py` a partir do `rules.json`. Não editar à mão.', '',
        'Regras: %d · com sensor computacional: %d (%d indireto, %d de aviso) · só inferencial: %d · '
        'sem sensor: %d' % (len(rules), len(comp), indirect, warn, kinds.count('inferencial'),
                            kinds.count('nenhum')), '',
        '## Por alvo', '',
        '| Alvo | Regras | Computacional | Só inferencial | Sem sensor |',
        '|---|---|---|---|---|',
    ]
    for alvo in ALVOS:
        group = [classify(r) for r in rules if r['alvo'] == alvo]
        if group:
            lines.append('| %s | %d | %d | %d | %d |' % (alvo, len(group), group.count('computacional'),
                                                       group.count('inferencial'), group.count('nenhum')))
    lines += ['', '## Sem sensor', '']
    lines += ['- %s · %s%s' % (r['id'], r['regra'], ' — %s' % r['motivo'] if r.get('motivo') else '')
              for r in rules if classify(r) == 'nenhum'] or ['Nenhuma.']
    lines += ['', '## Parâmetros vinculados', '',
              'Valor repetido entre guia e sensor; mudar num lugar só quebra o `--check`.', '',
              '| id | Parâmetro | Valor | Onde aparece |', '|---|---|---|---|']
    for r in rules:
        for p in r.get('parametros') or []:
            where = sorted({e['arquivo'] for e in p.get('em') or []})
            lines.append('| %s | %s | %s | %s |' % (r['id'], p['nome'], p['valor'],
                                                    ', '.join('`%s`' % w for w in where)))
    lines += ['', '## Registro', '', '| id | Regra | Fonte | Sensores |', '|---|---|---|---|']
    for r in rules:
        sensors = '<br>'.join(sensor_text(s) for s in r.get('sensores') or []) or '—'
        source = '`%s`' % r['fonte'] + (' · %s' % r['secao'] if r.get('secao') else '')
        lines.append('| %s | %s | %s | %s |' % (r['id'], r['regra'], source, sensors))
    return '\n'.join(lines) + '\n'


def main(argv):
    root = os.path.abspath(argv[argv.index('--root') + 1]) if '--root' in argv else \
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rules = load(root)
    found = problems(root, rules)
    if found:
        print('registro de regras inválido:')
        for p in found:
            print('  ' + p)
        return 1
    text = render(rules)
    path = os.path.join(root, REPORT)
    if '--check' in argv:
        try:
            with open(path, encoding='utf-8') as f:
                current = f.read()
        except OSError:
            current = None
        if current != text:
            print('%s defasado: rode python scripts/rules_report.py' % REPORT.replace(os.sep, '/'))
            return 1
        print('ok: %d regras, relatório em dia' % len(rules))
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('ok: %d regras, %s gerado' % (len(rules), REPORT.replace(os.sep, '/')))
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
