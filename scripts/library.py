#!/usr/bin/env python3
"""Biblioteca do projeto: catálogo, defasagem da arquitetura, dashboard e exportação para o vault.

Uso:
  library.py index [REPO] [--check]                 gera docs/library/LIBRARY.md
  library.py stale [REPO] [--json]                  sai 1 quando há documento de arquitetura defasado
  library.py build [REPO] [--check]                 gera docs/library/site/index.html
  library.py export [REPO] [--vault V] [--date D]   escreve as páginas em library.export do vault
"""
import datetime
import glob
import html
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARCH_DIR = 'docs/library/architecture'
INDEX = 'docs/library/LIBRARY.md'
SITE = 'docs/library/site/index.html'
MERMAID_VERSION = '11.4.1'
MERMAID = 'https://cdn.jsdelivr.net/npm/mermaid@%s/dist/mermaid.esm.min.mjs' % MERMAID_VERSION
IMAGES = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
DEFAULT_SOURCES = ('decisions/ADR-*.md', 'specs/contracts/*.md')
DATE = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
FM = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n?', re.S)
BASED_ON = re.compile(r'^\s*(\S+)\s*\(v(\d+)\)')

SECTIONS = (
    ('Canônicos', 'canonicos', ('docs/canonical/*.md', 'outputs/PLAN-*.md')),
    ('Arquitetura', 'arquitetura', (ARCH_DIR + '/ARCH-*.md', ARCH_DIR + '/models/*.md')),
    ('Contratos', 'contratos', ('specs/contracts/*.md',)),
    ('Especificação', 'especificacao', ('specs/features/*.md', 'specs/tests/*.md', 'specs/tasks/*.md')),
    ('Decisões', 'decisoes', ('decisions/*.md',)),
    ('Ilustrações', 'ilustracoes', ('docs/input/assets/*', ARCH_DIR + '/render/*')),
    ('Histórico', 'historico', ('docs/history/*.md',)),
)
TECHS = (('.net', 'dotnet'), ('c#', 'dotnet'), ('spring', 'spring-boot'), ('java', 'spring-boot'),
         ('typescript', 'typescript'), ('node', 'typescript'), ('php', 'php'), ('laravel', 'php'),
         ('go ', 'go'), ('golang', 'go'))


def _read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def _rel(repo, path):
    return os.path.relpath(path, repo).replace(os.sep, '/')


def split(text):
    """Separa o frontmatter (dict) do corpo."""
    m = FM.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k = re.match(r'^([A-Za-z_][\w-]*):\s*(.*?)\s*$', line)
        if not k:
            continue
        value = k.group(2)
        if value.startswith('[') and value.endswith(']'):
            value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
        else:
            value = value.strip('"\'')
        meta[k.group(1)] = value
    return meta, text[m.end():]


def title_of(meta, body, path):
    if meta.get('title'):
        return meta['title']
    for line in body.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return os.path.splitext(os.path.basename(path))[0]


def date_of(meta, text):
    if meta.get('atualizado'):
        return meta['atualizado']
    for line in text.splitlines()[:10]:
        m = DATE.search(line)
        if m:
            return m.group(1)
    return ''


def _entry(repo, path):
    rel = _rel(repo, path)
    if not rel.endswith('.md'):
        return {'path': rel, 'title': os.path.basename(rel), 'status': '', 'version': '', 'date': '',
                'meta': {}, 'body': ''}
    text = _read(path)
    meta, body = split(text)
    return {'path': rel, 'title': title_of(meta, body, path), 'status': meta.get('status', ''),
            'version': meta.get('version', ''), 'date': date_of(meta, text), 'meta': meta, 'body': body}


def _listed(name):
    return not (name.startswith('.') or name.startswith('_') or name in ('README.md', 'CLAUDE.md'))


def catalog(repo):
    """Seções do catálogo, cada uma com as entradas em ordem de caminho."""
    out = []
    for name, _, patterns in SECTIONS:
        paths = set()
        for pattern in patterns:
            for p in glob.glob(os.path.join(repo, pattern)):
                if os.path.isfile(p) and _listed(os.path.basename(p)):
                    paths.add(p)
        out.append((name, [_entry(repo, p) for p in sorted(paths, key=lambda x: _rel(repo, x))]))
    return out


def project_name(repo):
    return os.path.basename(os.path.abspath(repo))


def render_index(repo):
    lines = ['# Biblioteca — %s' % project_name(repo), '',
             '> Catálogo gerado por `library.py index`; não se edita à mão. O dashboard é `site/index.html`.', '']
    for name, entries in catalog(repo):
        lines += ['## %s' % name, '']
        if not entries:
            lines += ['Nenhum.', '']
            continue
        lines += ['| Documento | Status | Versão | Data | Caminho |', '|---|---|---|---|---|']
        for e in entries:
            lines.append('| %s | %s | %s | %s | [%s](../../%s) |' % (
                e['title'].replace('|', '/'), e['status'] or '—', e['version'] or '—', e['date'] or '—',
                e['path'], e['path']))
        lines.append('')
    return '\n'.join(lines)


def _generate(repo, rel, text, check):
    path = os.path.join(repo, rel)
    if check:
        current = _read(path) if os.path.isfile(path) else None
        if current != text:
            print('%s defasado: rode library.py %s' % (rel, 'index' if rel == INDEX else 'build'))
            return 1
        return 0
    _write(path, text)
    return 0


def index(repo, check=False):
    return _generate(repo, INDEX, render_index(repo), check)


def stale(repo):
    """Documentos da arquitetura com fonte mais nova que o `atualizado` deles."""
    found = []
    docs = sorted(glob.glob(os.path.join(repo, ARCH_DIR, 'ARCH-*.md')) +
                  glob.glob(os.path.join(repo, ARCH_DIR, 'models', '*.md')))
    for path in docs:
        rel = _rel(repo, path)
        meta, _ = split(_read(path))
        mine = meta.get('atualizado', '')
        if not mine:
            found.append({'path': rel, 'motivo': 'sem `atualizado` no frontmatter'})
            continue
        patterns = meta.get('fontes') or list(DEFAULT_SOURCES)
        if isinstance(patterns, str):
            patterns = [patterns]
        newer = []
        for pattern in patterns:
            for src in sorted(glob.glob(os.path.join(repo, pattern))):
                if os.path.abspath(src) == os.path.abspath(path) or not os.path.isfile(src):
                    continue
                text = _read(src)
                d = date_of(split(text)[0], text)
                if d and d > mine:
                    newer.append('%s (%s)' % (_rel(repo, src), d))
        if newer:
            found.append({'path': rel, 'motivo': 'fonte depois de %s: %s' % (mine, ', '.join(newer))})
        based = BASED_ON.match(meta.get('baseado_em', ''))
        if based and os.path.isfile(os.path.join(repo, based.group(1))):
            src_version = split(_read(os.path.join(repo, based.group(1))))[0].get('version', '')
            if src_version.isdigit() and int(src_version) > int(based.group(2)):
                found.append({'path': rel, 'motivo': '%s está na v%s; o documento cita a v%s'
                              % (based.group(1), src_version, based.group(2))})
    return found


def _md(body):
    import markdown
    out = markdown.markdown(body, extensions=['tables', 'fenced_code'])
    return re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                  r'<pre class="mermaid">\1</pre>', out, flags=re.S)


def _strip_h1(body):
    return re.sub(r'^\s*# .*\n', '', body, count=1)


def _first_paragraph(body):
    for block in re.split(r'\n\s*\n', _strip_h1(body)):
        block = block.strip()
        if block and not block.startswith(('#', '>', '|', '```', '-', '*')):
            return block
    return ''


def _status_sentence(repo):
    path = os.path.join(repo, 'STATUS.md')
    if not os.path.isfile(path):
        return ''
    m = re.search(r'^## Em uma frase\s*\n(.*?)(?=^## |\Z)', _read(path), re.S | re.M)
    return m.group(1).strip() if m else ''


def _journal(repo):
    path = os.path.join(repo, 'JOURNAL.md')
    if not os.path.isfile(path):
        return []
    out = []
    for m in re.finditer(r'^## (\d{4}-\d{2}-\d{2})\s*[·-]?\s*(.*)$', _read(path), re.M):
        out.append({'date': m.group(1), 'kind': 'diário', 'title': m.group(2).strip(), 'text': '', 'status': ''})
    return out


def _badge(e):
    bits = [b for b in (e['status'], ('v' + e['version']) if e['version'] else '', e['date']) if b]
    return ' · '.join(html.escape(b) for b in bits)


def _doc_block(e, open_=False):
    return ('<details class="doc"%s><summary><span class="t">%s</span><span class="m">%s</span></summary>'
            '<div class="body">%s<p class="src">%s</p></div></details>'
            % (' open' if open_ else '', html.escape(e['title']), _badge(e),
               _md(_strip_h1(e['body'])), html.escape(e['path'])))


CSS = """
:root{--bg:#f7f6f2;--fg:#1d1d1b;--mut:#6b6a64;--card:#fff;--line:#e2e0d8;--acc:#1f5f8b;--ok:#2f7d4f;--warn:#a5671b}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ecebe6;--mut:#a3a29b;--card:#1e1e1c;--line:#33322f;--acc:#7fb4d8;--ok:#7cc79a;--warn:#e0a85a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{display:grid;grid-template-columns:230px 1fr;min-height:100vh}
nav{position:sticky;top:0;height:100vh;overflow:auto;padding:24px 16px;border-right:1px solid var(--line)}
nav h1{font-size:17px;margin:0 0 16px}nav a{display:block;color:var(--fg);text-decoration:none;padding:4px 8px;border-radius:6px}
nav a:hover{background:var(--card)}nav .n{color:var(--mut);float:right}
main{padding:32px 40px;max-width:1100px}section{margin-bottom:40px}h2{border-bottom:1px solid var(--line);padding-bottom:6px}
.lead{font-size:17px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px}
.doc{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0}
.doc summary{cursor:pointer;padding:12px 16px;display:flex;gap:12px;justify-content:space-between}
.doc .m,.src,.tl .d{color:var(--mut);font-size:13px}.doc .body{padding:0 20px 12px;overflow-x:auto}
table{border-collapse:collapse}td,th{border:1px solid var(--line);padding:4px 8px}
pre{background:var(--bg);padding:12px;border-radius:8px;overflow-x:auto}pre.mermaid{background:transparent}
.tl{list-style:none;padding:0}.tl li{border-left:2px solid var(--line);padding:4px 0 12px 16px}
.tl .k{color:var(--acc);font-size:12px;text-transform:uppercase;margin-right:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}
figure img{max-width:100%}figcaption{font-size:13px;color:var(--mut)}
@media (max-width:760px){.wrap{grid-template-columns:1fr}nav{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:16px}}
"""


def render_site(repo):
    name = project_name(repo)
    sections = catalog(repo)
    by = dict(sections)
    dates = [e['date'] for _, es in sections for e in es if e['date']]
    nav, parts = [], []

    def add(sid, label, body, count=None):
        n = '<span class="n">%d</span>' % count if count is not None else ''
        nav.append('<a href="#%s">%s%s</a>' % (sid, label, n))
        parts.append('<section id="%s"><h2>%s</h2>%s</section>' % (sid, label, body))

    lead = _status_sentence(repo)
    add('visao', 'Visão', '<div class="lead">%s</div><p class="src">Artefato mais recente: %s</p>'
        % (_md(lead) if lead else 'Sem frase de estado no STATUS.md.', max(dates) if dates else '—'))
    for label, sid in (('Canônicos', 'canonicos'), ('Arquitetura', 'arquitetura'), ('Contratos', 'contratos'),
                       ('Decisões', 'decisoes'), ('Histórico', 'historico')):
        es = by[label]
        body = ''.join(_doc_block(e, open_=(sid == 'arquitetura')) for e in es) or '<p>Nenhum.</p>'
        add(sid, label, body, len(es))
        if sid == 'contratos':
            events = _journal(repo)
            for e in by['Especificação'] + by['Decisões']:
                kind = 'decisão' if e['path'].startswith('decisions/') else 'spec'
                events.append({'date': e['date'], 'kind': kind, 'title': e['title'],
                               'text': _first_paragraph(e['body']), 'status': e['status']})
            events.sort(key=lambda x: (x['date'] or '0000', x['kind'], x['title']), reverse=True)
            items = ''.join('<li><span class="d">%s</span><br><span class="k">%s</span><b>%s</b>%s%s</li>' % (
                html.escape(ev['date'] or 'sem data'), html.escape(ev['kind']), html.escape(ev['title']),
                (' · ' + html.escape(ev['status'])) if ev['status'] else '',
                ('<br>' + html.escape(ev['text'])) if ev['text'] else '') for ev in events)
            add('linha-do-tempo', 'Linha do tempo', '<ul class="tl">%s</ul>' % items if items else '<p>Nenhum.</p>',
                len(events))
    figs = []
    for e in by['Ilustrações']:
        src = '../../../' + e['path']
        if e['path'].lower().endswith(IMAGES):
            figs.append('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>'
                        % (html.escape(src), html.escape(e['title']), html.escape(e['path'])))
        else:
            figs.append('<figure><a href="%s">%s</a><figcaption>%s</figcaption></figure>'
                        % (html.escape(src), html.escape(e['title']), html.escape(e['path'])))
    add('ilustracoes', 'Ilustrações', '<div class="grid">%s</div>' % ''.join(figs) if figs else '<p>Nenhum.</p>',
        len(figs))
    return ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Biblioteca %s</title><style>%s</style></head><body><div class="wrap">'
            '<nav><h1>%s</h1>%s</nav><main>%s</main></div>'
            '<script type="module">import mermaid from "%s";'
            'mermaid.initialize({startOnLoad:true,theme:matchMedia("(prefers-color-scheme: dark)").matches?"dark":"default"});'
            '</script></body></html>\n'
            % (html.escape(name), CSS.strip(), html.escape(name), ''.join(nav), ''.join(parts), MERMAID))


def build(repo, check=False):
    return _generate(repo, SITE, render_site(repo), check)


def _profile(repo):
    try:
        return json.loads(_read(os.path.join(repo, '.bks-profile.json')))
    except (OSError, ValueError):
        return {}


def _techs(profile):
    stack = ' '.join(str(v) for v in (profile.get('stack') or {}).values()).lower() + ' '
    found = []
    for needle, tech in TECHS:
        if needle in stack and tech not in found:
            found.append(tech)
    return found or ['agnostic']


def _q(value):
    return '"%s"' % str(value).replace('"', "'")


def export(repo, vault, date=None):
    """Escreve o catálogo como páginas da knowledge; recusa tudo se uma página tiver achado."""
    date = date or datetime.date.today().isoformat()
    profile = _profile(repo)
    target = (profile.get('library') or {}).get('export')
    if not target:
        return {'problems': ['exportação não configurada: falta `library.export` no .bks-profile.json'],
                'code': 2, 'written': []}
    name = project_name(repo)
    dest = os.path.join(vault, target.replace('{projeto}', name))
    techs = '[%s]' % ', '.join(_techs(profile))
    origin = _rel(vault, repo) if os.path.abspath(repo).startswith(os.path.abspath(vault)) else name
    pages, assets, problems = {}, [], []
    for label, slug, _ in SECTIONS:
        for e in dict(catalog(repo))[label]:
            if slug == 'ilustracoes':
                if e['path'].lower().endswith(IMAGES):
                    assets.append(e['path'])
                continue
            page = '%s/%s' % (slug, os.path.basename(e['path']))
            kind = 'architecture' if slug in ('arquitetura', 'contratos') else 'output'
            text = ('---\ntitle: %s\ntype: "%s"\ndomain: "projetos"\ntags: [%s, %s]\ntechnologies: %s\n'
                    'sources: [%s]\nsource_count: 1\ncreated: %s\nupdated: "%s"\nstatus: "%s"\n'
                    'related: [index]\n---\n\n# %s\n\n%s\n\n> Origem: `%s/%s`\n'
                    % (_q(e['title']), kind, name, slug, techs, _q('%s/%s' % (origin, e['path'])),
                       _q(e['date'] or date), date, 'stable' if e['status'] == 'aprovado' else 'draft',
                       e['title'], _strip_h1(e['body']).strip(), origin, e['path']))
            hits = harvest.check_page(vault, text)
            problems.extend('%s: %s' % (e['path'], h) for h in hits)
            pages[page] = (text, e['title'], label)
    if problems:
        return {'problems': problems, 'code': 1, 'written': []}

    manifest = os.path.join(dest, '_export.json')
    before = json.loads(_read(manifest)).get('arquivos', []) if os.path.isfile(manifest) else []
    lines = ['---', 'title: %s' % _q('Projeto %s' % name), 'type: "output"', 'domain: "projetos"',
             'tags: [%s]' % name, 'technologies: %s' % techs, 'sources: [%s]' % _q(origin),
             'source_count: 1', 'created: "%s"' % date, 'updated: "%s"' % date, 'status: "draft"',
             'related: []', '---', '', '# Projeto %s' % name, '']
    lead = _status_sentence(repo)
    if lead:
        lines += [lead, '']
    for label, slug, _ in SECTIONS:
        mine = sorted((p, t) for p, (_, t, lb) in pages.items() if lb == label)
        if mine:
            lines += ['## %s' % label, ''] + ['- [[%s|%s]]' % (p[:-3], t) for p, t in mine] + ['']
    written = sorted(pages) + ['index.md'] + ['assets/' + os.path.basename(a) for a in assets]
    for page, (text, _, _) in pages.items():
        _write(os.path.join(dest, page), text)
    _write(os.path.join(dest, 'index.md'), '\n'.join(lines))
    for a in assets:
        os.makedirs(os.path.join(dest, 'assets'), exist_ok=True)
        shutil.copyfile(os.path.join(repo, a), os.path.join(dest, 'assets', os.path.basename(a)))
    removed = [f for f in before if f not in written]
    for f in removed:
        p = os.path.join(dest, f)
        if os.path.isfile(p):
            os.remove(p)
    _write(manifest, json.dumps({'projeto': name, 'exportado_em': date, 'arquivos': written},
                                ensure_ascii=False, indent=2) + '\n')
    _wiki_index(vault, dest, name, len(pages), date)
    _wiki_log(vault, dest, name, len(pages), date)
    return {'problems': [], 'code': 0, 'written': written, 'removed': removed, 'dest': dest}


def _wiki_index(vault, dest, name, count, date):
    path = os.path.join(vault, 'knowledge', 'wiki', 'index.md')
    if not os.path.isfile(path):
        return
    link = os.path.relpath(os.path.join(dest, 'index.md'), os.path.dirname(path)).replace(os.sep, '/')
    row = '| [Projeto %s](%s) | %d páginas, exportado em %s | projeto, %s | draft |' % (name, link, count, date, name)
    lines = _read(path).split('\n')
    lines = [l for l in lines if '](%s)' % link not in l]
    if '## Projetos' not in lines:
        while lines and not lines[-1].strip():
            lines.pop()
        lines += ['', '## Projetos', '| Page | Summary | Tags | Status |', '|------|---------|------|--------|']
        lines.append(row)
        lines.append('')
    else:
        i = lines.index('## Projetos')
        j = i + 1
        while j < len(lines) and not lines[j].startswith('|------'):
            j += 1
        lines.insert(j + 1 if j < len(lines) else i + 1, row)
    _write(path, '\n'.join(lines))


def _wiki_log(vault, dest, name, count, date):
    path = os.path.join(vault, 'knowledge', 'wiki', 'log.md')
    if not os.path.isfile(path):
        return
    rel = os.path.relpath(dest, os.path.join(vault, 'knowledge')).replace(os.sep, '/')
    text = _read(path).rstrip('\n')
    text += ('\n\n## [%s] export | %s\n- Pages created: %d páginas em %s/\n- Pages updated: wiki/index.md\n'
             % (date, name, count, rel))
    _write(path, text)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in ('index', 'stale', 'build', 'export'):
        print(__doc__)
        return 2
    cmd, rest = args[0], args[1:]
    flags = {a for a in rest if a in ('--check', '--json')}

    def opt(name):
        if name in rest:
            i = rest.index(name)
            return rest[i + 1] if i + 1 < len(rest) else None
        return None

    values = {opt('--vault'), opt('--date')}
    positional = [a for a in rest if not a.startswith('--') and a not in values]
    repo = os.path.abspath(positional[0] if positional else os.getcwd())
    if cmd == 'index':
        return index(repo, '--check' in flags)
    if cmd == 'build':
        return build(repo, '--check' in flags)
    if cmd == 'stale':
        found = stale(repo)
        if '--json' in flags:
            print(json.dumps(found, ensure_ascii=False, indent=2))
        elif found:
            print('arquitetura defasada:')
            for f in found:
                print('  - %s: %s' % (f['path'], f['motivo']))
        else:
            print('arquitetura em dia')
        return 1 if found else 0
    vault = opt('--vault') or os.environ.get('BKS_VAULT')
    if not vault:
        print('vault não definido: use --vault ou BKS_VAULT')
        return 2
    result = export(repo, os.path.abspath(vault), opt('--date'))
    for p in result['problems']:
        print('  - %s' % p)
    if result['code'] == 0:
        print('exportado: %d arquivos em %s' % (len(result['written']), result['dest']))
        for f in result.get('removed', []):
            print('  removido: %s' % f)
    return result['code']


if __name__ == '__main__':
    sys.exit(main())
