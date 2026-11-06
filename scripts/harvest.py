#!/usr/bin/env python3
"""Índice das decisões e dos casos de repos/ do vault, incremental e sem modelo, mais as checagens do harvest.

Uso:
  harvest.py index [VAULT]                 atualiza knowledge/wiki/experiencia/_index.json
  harvest.py themes [VAULT] [--json]       contagem por tema, para a consolidação
  harvest.py check --page ARQUIVO [VAULT]  recusa página com termo da lista de bloqueio ou dado sensível
  harvest.py stale REPO [VAULT]            sai 1 quando o projeto tem ADR ou caso mais novo que o índice
VAULT padrão: BKS_VAULT.
"""
import glob
import hashlib
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import learning  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FULL = ('backside', 'private')
HISTORY = ('old',)
CONCEPT_ONLY = {'w3': ('nquantic',)}
DATE = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
STATUS = re.compile(r'(?i)status\W{0,6}\s*([a-zà-ú-]+)')
THEMES = (
    ('dados', r'banco|dapper|ef core|\bsql\b|postgres|schema|migration|reposit[óo]rio|oracle|mongo'),
    ('mensageria', r'rabbit|kafka|\bfila|mensageria|consumer'),
    ('seguranca', r'seguran[çc]a|autoriza|autentica|keycloak|segredo|\bpii\b|lgpd'),
    ('observabilidade', r'opentelemetry|telemetria|\blogging\b|\btrace|m[ée]trica|observabilidade'),
    ('teste', r'\bteste|xunit|testcontainers|\btdd\b|\beval'),
    ('api', r'\bapi\b|endpoint|minimal api|\brest\b|grpc|contrato'),
    ('infra', r'docker|kubernetes|deploy|\binfra|\bci\b|openshift'),
    ('frontend', r'react|front|\btela|\bui\b|mobile'),
    ('arquitetura', r'hexagonal|pipeline|\bporta|adapter|dom[íi]nio|\bddd\b|arquitetura|\bsdk\b|sess[ãa]o'),
    ('processo', r'processo|workflow|harness|plugin|m[ée]todo|\bsdd\b'),
)


def index_path(vault):
    return os.path.join(vault, 'knowledge', 'wiki', 'experiencia', '_index.json')


def blocklist_path(vault):
    return os.path.join(vault, 'knowledge', 'wiki', 'experiencia', '_bloqueio.txt')


def theme(text):
    low = text.lower()
    return next((name for name, rx in THEMES if re.search(rx, low)), 'geral')


def _read(path):
    with io.open(path, encoding='utf-8', errors='replace') as fh:
        return fh.read()


def sources(vault):
    """(caminho, categoria, projeto, historico, conceito) de cada arquivo que entra no índice."""
    out = []
    for cat_dir in sorted(glob.glob(os.path.join(vault, 'repos', '*'))):
        cat = os.path.basename(cat_dir)
        if not os.path.isdir(cat_dir) or (cat not in FULL + HISTORY and cat not in CONCEPT_ONLY):
            continue
        for proj_dir in sorted(glob.glob(os.path.join(cat_dir, '*'))):
            proj = os.path.basename(proj_dir)
            if not os.path.isdir(proj_dir) or (cat in CONCEPT_ONLY and proj not in CONCEPT_ONLY[cat]):
                continue
            files = sorted(glob.glob(os.path.join(proj_dir, 'decisions', 'ADR-*.md')))
            learn = os.path.join(proj_dir, 'LEARNINGS.md')
            if os.path.isfile(learn):
                files.append(learn)
            for f in files:
                out.append((f, cat, proj, cat in HISTORY, cat in CONCEPT_ONLY))
    return out


def _key(vault, path, concept):
    rel = os.path.relpath(path, vault).replace(os.sep, '/')
    if concept:
        return '%s:%s' % (rel.split('/')[2], hashlib.sha1(rel.encode('utf-8')).hexdigest()[:12])
    return rel


def _parse(path, cat, proj, historic, concept):
    text = _read(path)
    if os.path.basename(path) == 'LEARNINGS.md':
        chunks = re.split(r'(?m)^## ', text)[1:]
        items = [('learning', c.splitlines()[0].strip(), c) for c in chunks if c.strip()]
    else:
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith('# ')), os.path.basename(path))
        items = [('adr', title, text)]
    entries = []
    for kind, title, body in items:
        head = '\n'.join(body.splitlines()[:15])
        d = DATE.search(title) or DATE.search(head)
        e = {'projeto': proj, 'categoria': cat, 'tipo': kind, 'tema': theme(title + '\n' + body[:600]),
             'data': d.group(1) if d else None}
        if concept:
            e['conceito'] = True
        else:
            s = STATUS.search(head)
            e.update(titulo=title, estado=s.group(1).lower() if s else None,
                     arquivo=None)
            if historic:
                e['historico'] = True
        entries.append(e)
    return entries


def index(vault):
    path = index_path(vault)
    old = json.loads(_read(path)) if os.path.isfile(path) else {}
    files_old, entries_old = old.get('arquivos', {}), old.get('entradas', {})
    files, entries, reread = {}, {}, 0
    for f, cat, proj, historic, concept in sources(vault):
        fkey = _key(vault, f, concept)
        mtime = os.path.getmtime(f)
        cached = files_old.get(fkey)
        if cached and cached['mtime'] == mtime and all(k in entries_old for k in cached['entradas']):
            files[fkey] = cached
            entries.update({k: entries_old[k] for k in cached['entradas']})
            continue
        reread += 1
        keys = []
        for n, e in enumerate(_parse(f, cat, proj, historic, concept)):
            k = fkey if e['tipo'] == 'adr' else '%s#%d' % (fkey, n + 1)
            if not concept:
                e['arquivo'] = os.path.relpath(f, vault).replace(os.sep, '/')
            e['mtime'] = mtime
            entries[k] = e
            keys.append(k)
        files[fkey] = {'mtime': mtime, 'entradas': keys}
    data = {'atualizado_ts': time.time(), 'arquivos': files, 'entradas': entries}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    data['relidos'] = reread
    return data


def themes(vault):
    path = index_path(vault)
    if not os.path.isfile(path):
        return {}
    out = {}
    for e in json.loads(_read(path))['entradas'].values():
        out[e['tema']] = out.get(e['tema'], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def check_page(vault, text):
    hits = []
    bl = blocklist_path(vault)
    if os.path.isfile(bl):
        low = text.lower()
        for term in _read(bl).splitlines():
            term = term.strip()
            if term and not term.startswith('#') and term.lower() in low:
                hits.append('termo bloqueado: %s' % term)
    return hits + learning.scrub(text)


def stale(repo, vault):
    if not vault:
        return False
    files = glob.glob(os.path.join(repo, 'decisions', 'ADR-*.md'))
    learn = os.path.join(repo, 'LEARNINGS.md')
    if os.path.isfile(learn):
        files.append(learn)
    if not files:
        return False
    path = index_path(vault)
    last = json.loads(_read(path)).get('atualizado_ts', 0) if os.path.isfile(path) else 0
    return max(os.path.getmtime(f) for f in files) > last


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = '--json' in args
    args = [a for a in args if a != '--json']
    page = None
    if '--page' in args:
        i = args.index('--page')
        page = args[i + 1]
        del args[i:i + 2]
    if not args or args[0] not in ('index', 'themes', 'check', 'stale'):
        print(__doc__)
        return 2
    cmd, rest = args[0], args[1:]
    if cmd == 'stale':
        repo = os.path.abspath(rest[0] if rest else os.getcwd())
        vault = rest[1] if len(rest) > 1 else os.environ.get('BKS_VAULT')
        pend = stale(repo, vault)
        print('harvest pendente' if pend else 'harvest em dia')
        return 1 if pend else 0
    vault = rest[0] if rest else os.environ.get('BKS_VAULT')
    if not vault or not os.path.isdir(os.path.join(vault, 'repos')):
        print('vault sem repos/: defina BKS_VAULT ou passe o caminho')
        return 2
    if cmd == 'index':
        data = index(vault)
        print('índice: %d entradas, %d arquivo(s) relido(s)' % (len(data['entradas']), data['relidos']))
    elif cmd == 'themes':
        t = themes(vault)
        print(json.dumps(t, ensure_ascii=False) if as_json else '\n'.join('%-16s %d' % kv for kv in t.items()))
    elif cmd == 'check':
        hits = check_page(vault, _read(page))
        print('\n'.join(hits) or 'página limpa')
        return 1 if hits else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
