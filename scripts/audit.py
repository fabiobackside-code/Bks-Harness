"""Auditoria de deriva: no kit, registro de regras e parâmetros; no projeto, cópia dos guardas, CI e STATUS.

Uso: audit.py [DIR]                   achados; saída 0 sem achado, 1 com achado
     audit.py [DIR] --dossier [TEMA]  trechos do tema com arquivo:linha, insumo do --deep; sem tema, lista
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(KIT, 'hooks', 'scripts'))

import _drift  # noqa: E402
import install_guards  # noqa: E402
import learning  # noqa: E402
import rules_report  # noqa: E402

CI_FILES = {'github': '.github/workflows/bkhar-guards.yml', 'gitlab': '.bkhar/guards/gitlab-ci.yml'}
DOSSIER_SCOPE = ('skills/**/*.md', 'agents/*.md', 'commands/*.md', 'docs/ARCHITECTURE.md', 'README.md')
CONTEXT = 2
THEMES = {
    'pipeline': r'pipeline|orquestra|est[áa]gios?\b|\bsteps?\b|mediatr|dispatcher',
    'result': r'\bresult\b|pipelineresult|exce[çc][ãa]o|\bexceptions?\b|\bthrow\b|erro tipado',
    'txc': r'\btxc\b|transaction|imut[áa]ve|\brecords?\b|parameter object',
    'camadas': r'\bdomain\b|\badapters?\b|\bports?\b|hexagonal|dire[çc][ãa]o da depend',
    'teste': r'\btestes?\b|xunit|testcontainers|fluentassertions|\btdd\b|\bred\b',
    'comentario': r'coment[áa]rio|severidade|\bdocstring|architecture\.md',
    'segredo': r'segredo|\bsecrets?\b|\.env\b|\bpii\b|\bsenhas?\b|mascar|dado sens[íi]vel',
    'portoes': r'port[ãa]o|portões|ok do usu[áa]rio|aprova[çc][ãa]o|\baprovad|colaborativo|autonomo|collaborative|autonomous',
}


OLD_MODES = {'colaborativo': 'collaborative', 'autonomo': 'autonomous'}


def is_kit(path):
    return all(os.path.exists(os.path.join(path, *p.split('/'))) for p in ('rules.json', 'hooks/hooks.json'))


def read_bytes(path):
    try:
        with open(path, 'rb') as f:
            return f.read().replace(b'\r\n', b'\n')
    except OSError:
        return None


def kit_findings(path):
    rules = rules_report.load(path)
    found = [('registro', p, 'corrija o rules.json ou o guia') for p in rules_report.problems(path, rules)]
    if not found:
        try:
            with open(os.path.join(path, rules_report.REPORT), encoding='utf-8') as f:
                current = f.read()
        except OSError:
            current = None
        if current != rules_report.render(rules):
            found.append(('registro', 'docs/regras.md defasado', 'python scripts/rules_report.py'))
    return found


def guard_sources():
    sources = {'precommit.py': os.path.join(KIT, 'scripts', 'precommit.py')}
    for name in install_guards.GUARDS:
        sources[name] = os.path.join(KIT, 'hooks', 'scripts', name)
    return sources


def project_findings(path):
    found = []
    try:
        with open(os.path.join(path, '.bks-profile.json'), encoding='utf-8') as f:
            axes = json.load(f).get('axes') or {}
    except (OSError, ValueError):
        axes = {}
    mode = axes.get('mode')
    if mode in OLD_MODES:
        found.append(('perfil', 'axes.mode "%s" é o valor antigo' % mode, '/bkhar:mode %s' % OLD_MODES[mode]))
    fix = 'python "%s" . --host <github|gitlab|none>' % os.path.join(KIT, 'scripts', 'install_guards.py')
    gdir = os.path.join(path, '.bkhar', 'guards')
    if not os.path.isdir(gdir):
        return found + [('guardas', 'guardas não instalados em .bkhar/guards/', fix)]
    version = (read_bytes(os.path.join(gdir, 'VERSION')) or b'').decode('utf-8').strip()
    if version != install_guards.kit_version():
        found.append(('guardas', 'cópia na versão %s, kit na %s' % (version or '?', install_guards.kit_version()), fix))
    for name, source in sorted(guard_sources().items()):
        copy = read_bytes(os.path.join(gdir, name))
        if copy is None:
            found.append(('guardas', '%s falta na cópia' % name, fix))
        elif copy != read_bytes(source):
            found.append(('guardas', '%s difere do kit' % name, fix))
    host = axes.get('git_host') or ''
    ci = CI_FILES.get(host)
    if ci and not os.path.exists(os.path.join(path, *ci.split('/'))):
        found.append(('ci', 'git_host %s sem %s' % (host, ci), fix.replace('<github|gitlab|none>', host)))
    return found


def open_contradictions(path):
    found = []
    for proposal in sorted(glob.glob(os.path.join(path, 'inbox', 'proposals', '*.md'))):
        m = learning.meta(proposal)
        if m.get('tipo') == 'contradicao' and m.get('status') == 'candidata':
            found.append(('contradicao', 'em aberto: inbox/proposals/%s' % os.path.basename(proposal),
                          'corrija o guia e rode learning.py resolve, ou learning.py reject com motivo'))
    return found


def dossier_files(path):
    files = set()
    for pattern in DOSSIER_SCOPE:
        files.update(glob.glob(os.path.join(path, *pattern.split('/')), recursive=True))
    rels = (os.path.relpath(f, path).replace(os.sep, '/') for f in files)
    return sorted(r for r in rels if '/third-party/' not in r)


def dossier(path, theme):
    """Trechos de um tema, em markdown: cada bloco com arquivo:linha e o contexto em volta."""
    pattern = re.compile(THEMES[theme], re.IGNORECASE)
    out, total = [], 0
    for rel in dossier_files(path):
        with open(os.path.join(path, *rel.split('/')), encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        hits = [i for i, line in enumerate(lines) if pattern.search(line)]
        windows = []
        for i in hits:
            lo, hi = max(0, i - CONTEXT), min(len(lines), i + CONTEXT + 1)
            if windows and lo <= windows[-1][1]:
                windows[-1][1] = hi
                windows[-1][2].append(i)
            else:
                windows.append([lo, hi, [i]])
        for lo, hi, marks in windows:
            out.append('### %s:%s' % (rel, ','.join(str(m + 1) for m in marks)))
            out.extend('%4d  %s' % (n + 1, lines[n]) for n in range(lo, hi))
            out.append('')
            total += 1
    head = '# Dossiê — %s\n\n%d trecho(s) de %s\n\n' % (theme, total, ', '.join(DOSSIER_SCOPE))
    return head + '\n'.join(out)


def audit(path):
    found = kit_findings(path) if is_kit(path) else project_findings(path)
    found.extend(open_contradictions(path))
    _, message = _drift.check(path)
    if message:
        found.append(('status', message, 'atualize o STATUS.md pelo /bkhar:save'))
    return found


def main(argv):
    if '--dossier' in argv:
        i = argv.index('--dossier')
        rest, path = argv[i + 1:], os.path.abspath(argv[0] if i > 0 else '.')
        if not rest:
            print('temas do dossiê:')
            for name in THEMES:
                print('  %s' % name)
            return 0
        if rest[0] not in THEMES:
            print('tema desconhecido: %s; use um de %s' % (rest[0], ', '.join(THEMES)))
            return 2
        print(dossier(path, rest[0]))
        return 0
    path = os.path.abspath(argv[0] if argv else '.')
    kind = 'kit' if is_kit(path) else 'projeto'
    found = audit(path)
    print('auditoria do %s em %s' % (kind, path))
    for category, what, fix in found:
        print('[%s] %s\n    destrava: %s' % (category, what, fix))
    print('%d achado(s)' % len(found) if found else 'sem deriva')
    return 1 if found else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
