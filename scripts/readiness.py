#!/usr/bin/env python3
"""Checagem de prontidão do modo autonomo, sem chamada de modelo.

Uso: readiness.py [REPO] [--json]
Sai 0 quando concede o modo, 1 quando recusa e lista o que falta por nível.
"""
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library  # noqa: E402
import wave_graph  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CONTEXT_OK = ('revisado', 'aprovado')
OPEN_HEADING = re.compile(r'^#{2,4}\s+(?:\d+\.\s*)?(?:quest(?:õ|o)es|perguntas)\s+em\s+aberto', re.I)
CLOSED = re.compile(r'^\s*[-*]\s+\[[xX]\]')
UNCHECKED = re.compile(r'^\s*[-*]\s+\[\s\]\s*(.+)')
BULLET = re.compile(r'^\s*[-*]\s+(.+)')
TABLE_SEP = re.compile(r'^\s*\|[\s:|-]+\|\s*$')


def read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def status_of(path):
    m = re.match(r'^---\r?\n(.*?)\r?\n---', read(path), re.S)
    if not m:
        return None
    s = re.search(r'^status:\s*(.+?)\s*$', m.group(1), re.M)
    return s.group(1).strip().lower() if s else None


def one(repo, pattern):
    found = sorted(glob.glob(os.path.join(repo, pattern)))
    return found[0] if found else None


def open_items(path):
    """Itens ainda abertos nas seções de questões ou perguntas em aberto do documento."""
    items, inside, header_seen = [], False, False
    for line in read(path).splitlines():
        if line.startswith('#'):
            inside = bool(OPEN_HEADING.match(line))
            header_seen = False
            continue
        if not inside or not line.strip():
            continue
        if CLOSED.match(line):
            continue
        m = UNCHECKED.match(line)
        if m:
            items.append(m.group(1).strip())
            continue
        if line.lstrip().startswith('|'):
            if TABLE_SEP.match(line):
                header_seen = True
                continue
            if header_seen:
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                items.append(' · '.join(c for c in cells if c))
            continue
        m = BULLET.match(line)
        if m and not m.group(1).lower().startswith('nenhum'):
            items.append(m.group(1).strip())
    return items


def graph_problems(path):
    try:
        graph = json.loads(read(path))
    except ValueError as exc:
        return ['%s não é JSON válido: %s' % (os.path.basename(path), exc)]
    return ['%s: %s' % (os.path.basename(path), p) for p in wave_graph.validate(graph)]


def evaluate(repo):
    levels, warnings = [], []

    def level(name, missing):
        levels.append({'level': name, 'ok': not missing, 'missing': missing})

    missing = []
    context = os.path.join(repo, 'docs', 'canonical', 'CONTEXT.md')
    if not os.path.isfile(context):
        missing.append('docs/canonical/CONTEXT.md não existe (/bkhar:canonize)')
    elif status_of(context) not in CONTEXT_OK:
        missing.append('docs/canonical/CONTEXT.md com status `%s`; precisa `revisado` ou `aprovado`'
                       % status_of(context))
    prd = one(repo, os.path.join('docs', 'canonical', 'PRD-*.md'))
    if not prd:
        missing.append('PRD não existe (/bkhar:prd)')
    elif status_of(prd) != 'aprovado':
        missing.append('PRD com status `%s`; precisa `aprovado`' % status_of(prd))
    level('Contexto', missing)

    missing = []
    plan = one(repo, os.path.join('outputs', 'PLAN-*.md'))
    if not plan:
        missing.append('PLAN não existe (/bkhar:plan)')
    elif status_of(plan) != 'aprovado':
        missing.append('PLAN com status `%s`; precisa `aprovado`' % status_of(plan))
    graph = one(repo, os.path.join('outputs', 'GRAPH-*.json'))
    if not graph:
        missing.append('outputs/GRAPH-{projeto}.json não existe (/bkhar:plan gera o grafo)')
    else:
        missing.extend(graph_problems(graph))
    level('Plano', missing)

    missing = []
    arch = one(repo, os.path.join('docs', 'library', 'architecture', 'ARCH-*.md'))
    if not arch:
        missing.append('docs/library/architecture/ARCH-{projeto}.md não existe (/bkhar:arch)')
    else:
        docs = [arch] + sorted(glob.glob(os.path.join(repo, 'docs', 'library', 'architecture', 'models', '*.md')))
        for d in docs:
            if status_of(d) != 'aprovado':
                missing.append('%s com status `%s`; precisa `aprovado`' % (os.path.basename(d), status_of(d)))
        missing.extend('%s defasado: %s' % (os.path.basename(f['path']), f['motivo'])
                       for f in library.stale(repo))
    level('Arquitetura', missing)

    missing = []
    for doc in (prd, plan):
        if doc:
            name = os.path.basename(doc)
            missing.extend('%s: %s' % (name, item) for item in open_items(doc))
    level('Abertos', missing)

    missing = []
    profile_path = os.path.join(repo, '.bks-profile.json')
    try:
        profile = json.loads(read(profile_path))
    except (OSError, ValueError):
        profile = None
    if profile is None:
        missing.append('.bks-profile.json ausente ou inválido')
    elif not profile.get('stack'):
        missing.append('.bks-profile.json sem `stack`')
    level('Execução', missing)

    rules = glob.glob(os.path.join(repo, 'brain', 'engineering', 'regras', '*.md'))
    if not any(status_of(r) == 'promovida' for r in rules):
        warnings.append('nenhuma regra promovida em brain/engineering/regras/ (/bkhar:retro)')

    return {'granted': all(l['ok'] for l in levels), 'levels': levels, 'warnings': warnings}


def render(result):
    out = ['prontidão do modo autonomo: %s' % ('CONCEDIDA' if result['granted'] else 'RECUSADA')]
    for l in result['levels']:
        out.append('  %-11s %s' % (l['level'], 'ok' if l['ok'] else 'falta'))
        out.extend('              - %s' % m for m in l['missing'])
    for w in result['warnings']:
        out.append('  aviso       %s' % w)
    return '\n'.join(out)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = '--json' in args
    args = [a for a in args if a != '--json']
    repo = os.path.abspath(args[0] if args else os.getcwd())
    result = evaluate(repo)
    print(json.dumps(result, ensure_ascii=False, indent=2) if as_json else render(result))
    return 0 if result['granted'] else 1


if __name__ == '__main__':
    sys.exit(main())
