#!/usr/bin/env python3
"""Grafo de tasks do modo autonomo: validação, ondas e liberação, sem chamada de modelo.

Uso:
  wave_graph.py validate [REPO]          sai 0 sem problema, 1 com problema, 2 sem grafo
  wave_graph.py waves [REPO] [--json]    ondas calculadas de depende_de e consome/produz
  wave_graph.py ready [REPO] [--json]    tasks liberadas agora, pelo estado em outputs/run/
"""
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MAX_PARALLEL = 4
ROLES = ('architect', 'developer', 'tester', 'security', 'quality', 'scribe')
KINDS = ('desenho', 'construcao', 'front', 'integracao')
LISTS = ('depende_de', 'consome', 'produz', 'arquivos')
APPROVED = ('aprovado', 'revisado')
DONE = 'passou'
ACTIVE = re.compile(r'^(em curso|tentativa)')
ARCH = re.compile(r'^docs/library/architecture/ARCH-[^/]+\.md$')


def load(repo):
    found = sorted(glob.glob(os.path.join(repo, 'outputs', 'GRAPH-*.json')))
    if not found:
        return None
    with io.open(found[0], encoding='utf-8') as fh:
        return json.load(fh)


def _tasks(graph):
    return (graph.get('tasks') or []) if isinstance(graph, dict) else []


def _producers(tasks):
    out = {}
    for t in tasks:
        for p in t.get('produz') or []:
            out.setdefault(p, []).append(t['id'])
    return out


def predecessors(graph):
    tasks = _tasks(graph)
    producers = _producers(tasks)
    preds = {}
    for t in tasks:
        before = set(t.get('depende_de') or [])
        for p in t.get('consome') or []:
            before.update(x for x in producers.get(p, []) if x != t['id'])
        preds[t['id']] = before
    return preds


def _levels(graph):
    preds = predecessors(graph)
    levels, visiting = {}, set()

    def level(tid):
        if tid in levels:
            return levels[tid]
        if tid in visiting:
            raise ValueError(tid)
        visiting.add(tid)
        lv = 1 + max([level(p) for p in preds.get(tid, ()) if p in preds] or [-1])
        visiting.discard(tid)
        levels[tid] = lv
        return lv

    for tid in preds:
        level(tid)
    return levels


def validate(graph):
    tasks = _tasks(graph)
    if not tasks:
        return ['grafo sem tasks']
    problems, seen = [], set()
    for t in tasks:
        tid = t.get('id')
        if not tid:
            problems.append('task sem id')
            continue
        if tid in seen:
            problems.append('id %s repetido' % tid)
        seen.add(tid)
        for key in LISTS:
            if not isinstance(t.get(key), list):
                problems.append('task %s sem a lista `%s`' % (tid, key))
        if t.get('papel') not in ROLES:
            problems.append('task %s com papel desconhecido `%s`' % (tid, t.get('papel')))
        if t.get('tipo') not in KINDS:
            problems.append('task %s com tipo desconhecido `%s`' % (tid, t.get('tipo')))
    if problems:
        return problems
    for t in tasks:
        if t['tipo'] == 'desenho' and not any(ARCH.match(c) for c in t['consome']):
            problems.append('task %s de desenho não consome o ARCH '
                            '(docs/library/architecture/ARCH-{projeto}.md)' % t['id'])
    for t in tasks:
        for dep in t['depende_de']:
            if dep not in seen:
                problems.append('task %s depende de %s, que não existe' % (t['id'], dep))
    if problems:
        return problems
    try:
        levels = _levels(graph)
    except ValueError as exc:
        return ['ciclo no grafo passando por %s' % exc]
    owners = {}
    for t in tasks:
        for f in t['arquivos']:
            owners.setdefault((levels[t['id']], f), []).append(t['id'])
    for (lv, f), ids in sorted(owners.items()):
        if len(ids) > 1:
            problems.append('onda %d: %s declaram o mesmo arquivo %s' % (lv + 1, ', '.join(ids), f))
    return problems


def waves(graph):
    levels = _levels(graph)
    out = [[] for _ in range(max(levels.values()) + 1)] if levels else []
    for tid in sorted(levels):
        out[levels[tid]].append(tid)
    return out


def _status(path):
    if not path.endswith('.md') or not os.path.isfile(path):
        return None
    with io.open(path, encoding='utf-8') as fh:
        m = re.match(r'^---\r?\n(.*?)\r?\n---', fh.read(), re.S)
    if not m:
        return None
    s = re.search(r'^status:\s*(.+?)\s*$', m.group(1), re.M)
    return s.group(1).strip().lower() if s else None


def _available(repo, rel):
    path = os.path.join(repo, rel)
    if not os.path.exists(path):
        return False
    status = _status(path)
    return status is None or status in APPROVED


def ready(graph, repo, state):
    """Tasks que podem começar agora: entradas aprovadas, produtores concluídos, dentro do teto."""
    tasks = _tasks(graph)
    producers = _producers(tasks)
    active = sum(1 for s in state.values() if ACTIVE.match(s or ''))
    out = []
    for t in sorted(tasks, key=lambda x: x['id']):
        if state.get(t['id'], 'pendente') != 'pendente':
            continue
        if any(state.get(d) != DONE for d in t['depende_de']):
            continue
        ok = True
        for rel in t['consome']:
            makers = [m for m in producers.get(rel, []) if m != t['id']]
            if any(state.get(m) != DONE for m in makers) or not _available(repo, rel):
                ok = False
                break
        if ok:
            out.append(t['id'])
    return out[:max(0, MAX_PARALLEL - active)]


def read_state(repo):
    state = {}
    for path in glob.glob(os.path.join(repo, 'outputs', 'run', '*', 'T-*.json')):
        try:
            with io.open(path, encoding='utf-8') as fh:
                data = json.load(fh)
            state[data['id']] = data.get('estado', 'pendente')
        except (OSError, ValueError, KeyError):
            continue
    return state


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = '--json' in args
    args = [a for a in args if a != '--json']
    if not args or args[0] not in ('validate', 'waves', 'ready'):
        print(__doc__)
        return 2
    repo = os.path.abspath(args[1] if len(args) > 1 else os.getcwd())
    graph = load(repo) if os.path.isdir(repo) else None
    if graph is None:
        print('outputs/GRAPH-{projeto}.json não encontrado em %s' % repo)
        return 2
    problems = validate(graph)
    if args[0] == 'validate' or problems:
        if as_json:
            print(json.dumps({'problems': problems}, ensure_ascii=False, indent=2))
        else:
            print('grafo: %s' % ('ok' if not problems else '%d problema(s)' % len(problems)))
            for p in problems:
                print('  - %s' % p)
        return 1 if problems else 0
    if args[0] == 'waves':
        result = waves(graph)
        if as_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            for i, ids in enumerate(result, 1):
                print('onda %d: %s' % (i, ', '.join(ids)))
        return 0
    result = ready(graph, repo, read_state(repo))
    print(json.dumps(result) if as_json else ('liberadas: %s' % (', '.join(result) or 'nenhuma')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
