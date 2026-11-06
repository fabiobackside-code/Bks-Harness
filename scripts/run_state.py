#!/usr/bin/env python3
"""Estado da execução em ondas: um arquivo por task em outputs/run/onda-N/, escrito só pelo orquestrador.

Uso:
  run_state.py init [REPO]
  run_state.py start [REPO] --task T-001 [--worktree CAMINHO] [--model opus]
  run_state.py attempt [REPO] --task T-001 --n 2
  run_state.py finish [REPO] --task T-001 --result passou|bloqueada [--cost 0.42]
  run_state.py pause|resume [REPO]
  run_state.py show [REPO] [--json]
  run_state.py inbox [REPO]                  pedidos do painel ainda não aplicados
  run_state.py applied [REPO] --id PEDIDO    aplica e arquiva o pedido
"""
import argparse
import glob
import io
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave_graph  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MAX_ATTEMPTS = 4
RESULTS = ('passou', 'bloqueada')


class StateError(Exception):
    """Transição recusada: o estado não muda."""


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def run_dir(repo):
    return os.path.join(repo, 'outputs', 'run')


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _read(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _graph(repo):
    graph = wave_graph.load(repo)
    if graph is None:
        raise StateError('outputs/GRAPH-{projeto}.json não encontrado')
    problems = wave_graph.validate(graph)
    if problems:
        raise StateError('grafo inválido: %s' % '; '.join(problems))
    return graph


def _path(repo, tid):
    found = glob.glob(os.path.join(run_dir(repo), 'onda-*', '%s.json' % tid))
    if not found:
        raise StateError('task %s sem estado; rode init' % tid)
    return found[0]


def get(repo, tid):
    return _read(_path(repo, tid))


def _save(repo, task, event):
    task['eventos'].append({'em': now(), 'o_que': event})
    _write(os.path.join(run_dir(repo), 'onda-%d' % task['onda'], '%s.json' % task['id']), task)
    return task


def init(repo):
    graph = _graph(repo)
    created = []
    for n, ids in enumerate(wave_graph.waves(graph), 1):
        for tid in ids:
            path = os.path.join(run_dir(repo), 'onda-%d' % n, '%s.json' % tid)
            if os.path.exists(path):
                continue
            t = next(x for x in graph['tasks'] if x['id'] == tid)
            task = {'id': tid, 'onda': n, 'titulo': t.get('titulo', ''), 'tipo': t['tipo'],
                    'papel': t['papel'], 'lente': t.get('lente'), 'modelo': None,
                    'estado': 'pendente', 'tentativa': 0, 'worktree': None, 'inicio': None,
                    'fim': None, 'custo_usd': None, 'eventos': []}
            _save(repo, task, 'criada')
            created.append(tid)
    if not os.path.exists(os.path.join(run_dir(repo), 'run.json')):
        _write(os.path.join(run_dir(repo), 'run.json'), {'pausado': False, 'atualizado': now()})
    return created


def paused(repo):
    path = os.path.join(run_dir(repo), 'run.json')
    return os.path.exists(path) and bool(_read(path).get('pausado'))


def set_paused(repo, value):
    _write(os.path.join(run_dir(repo), 'run.json'), {'pausado': bool(value), 'atualizado': now()})


def state_map(repo):
    return wave_graph.read_state(repo)


def start(repo, tid, worktree=None, model=None):
    graph = _graph(repo)
    if tid not in {t['id'] for t in graph['tasks']}:
        raise StateError('task %s não está no grafo' % tid)
    if paused(repo):
        raise StateError('execução pausada; retome antes de começar task')
    if tid not in wave_graph.ready(graph, repo, state_map(repo)):
        raise StateError('task %s não está liberada: entrada sem aprovar, produtor em curso ou teto de %d'
                         % (tid, wave_graph.MAX_PARALLEL))
    task = get(repo, tid)
    task.update(estado='em curso', worktree=worktree, modelo=model, inicio=now())
    return _save(repo, task, 'início' + (' em %s' % model if model else ''))


def attempt(repo, tid, n):
    task = get(repo, tid)
    if task['estado'] in ('pendente', 'passou', 'bloqueada'):
        raise StateError('task %s em %s não recebe tentativa' % (tid, task['estado']))
    if not 1 <= n <= MAX_ATTEMPTS or n < task['tentativa']:
        raise StateError('tentativa %d fora de 1..%d ou para trás' % (n, MAX_ATTEMPTS))
    task.update(estado='tentativa %d' % n, tentativa=n)
    return _save(repo, task, 'tentativa %d' % n)


def finish(repo, tid, result, cost=None):
    if result not in RESULTS:
        raise StateError('resultado %r; use %s' % (result, ' ou '.join(RESULTS)))
    task = get(repo, tid)
    if task['estado'] in ('pendente', 'passou', 'bloqueada'):
        raise StateError('task %s em %s não pode terminar' % (tid, task['estado']))
    task.update(estado=result, fim=now(), custo_usd=cost)
    return _save(repo, task, result)


REQUESTS = ('resposta_bloqueio', 'pausar', 'retomar', 'mensagem', 'modelo')
MODELS = ('opus', 'sonnet', 'haiku')


def inbox_dir(repo):
    return os.path.join(run_dir(repo), 'inbox')


def _check_request(repo, req):
    kind = req.get('tipo')
    if kind not in REQUESTS:
        raise StateError('pedido %r; use %s' % (kind, ', '.join(REQUESTS)))
    if kind in ('mensagem', 'resposta_bloqueio'):
        if not str(req.get('texto') or '').strip():
            raise StateError('%s sem texto' % kind)
        tasks = {t['id'] for t in _graph(repo)['tasks']}
        if req.get('task') not in tasks:
            raise StateError('task %r não está no grafo' % req.get('task'))
    if kind == 'modelo':
        if req.get('papel') not in wave_graph.ROLES:
            raise StateError('papel %r desconhecido' % req.get('papel'))
        if req.get('modelo') not in MODELS:
            raise StateError('modelo %r; use %s' % (req.get('modelo'), ', '.join(MODELS)))


def submit(repo, req):
    """Grava um pedido na inbox; é a única escrita permitida ao painel."""
    _check_request(repo, req)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    keep = ('tipo', 'task', 'texto', 'papel', 'modelo')
    data = {k: req[k] for k in keep if req.get(k) is not None}
    data.update(id='%s-%s' % (stamp, data['tipo']), criado_em=now())
    _write(os.path.join(inbox_dir(repo), data['id'] + '.json'), data)
    return data


def pending(repo):
    return [_read(p) for p in sorted(glob.glob(os.path.join(inbox_dir(repo), '*.json')))]


def applied(repo, rid):
    path = os.path.join(inbox_dir(repo), '%s.json' % os.path.basename(rid))
    if not os.path.isfile(path):
        raise StateError('pedido %s não está pendente' % rid)
    req = _read(path)
    kind = req['tipo']
    if kind in ('pausar', 'retomar'):
        set_paused(repo, kind == 'pausar')
    elif kind in ('mensagem', 'resposta_bloqueio'):
        _save(repo, get(repo, req['task']), '%s do usuário: %s' % (kind, req['texto']))
    elif kind == 'modelo':
        profile_path = os.path.join(repo, '.bks-profile.json')
        profile = _read(profile_path)
        profile.setdefault('models', {})[req['papel']] = req['modelo']
        _write(profile_path, profile)
    req['aplicado_em'] = now()
    _write(os.path.join(inbox_dir(repo), 'aplicados', os.path.basename(path)), req)
    os.remove(path)
    return req


def snapshot(repo):
    tasks = [_read(p) for p in sorted(glob.glob(os.path.join(run_dir(repo), 'onda-*', 'T-*.json')))]
    tasks.sort(key=lambda t: (t['onda'], t['id']))
    graph = wave_graph.load(repo)
    return {'tasks': tasks, 'waves': wave_graph.waves(graph) if graph else [],
            'paused': paused(repo),
            'ready': wave_graph.ready(graph, repo, state_map(repo)) if graph else []}


def render(repo):
    snap = snapshot(repo)
    lines = ['execução%s' % (' PAUSADA' if snap['paused'] else ''),
             '%-5s %-6s %-10s %-7s %-12s %-20s %s' % ('onda', 'task', 'papel', 'modelo', 'estado',
                                                     'início', 'custo')]
    for t in snap['tasks']:
        lines.append('%-5s %-6s %-10s %-7s %-12s %-20s %s' % (
            t['onda'], t['id'], t['papel'], t['modelo'] or '-', t['estado'], t['inicio'] or '-',
            '-' if t['custo_usd'] is None else 'US$ %.2f' % t['custo_usd']))
    lines.append('liberadas agora: %s' % (', '.join(snap['ready']) or 'nenhuma'))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description='estado da execução em ondas')
    ap.add_argument('cmd', choices=('init', 'start', 'attempt', 'finish', 'pause', 'resume', 'show',
                                      'inbox', 'applied'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--task')
    ap.add_argument('--worktree')
    ap.add_argument('--model')
    ap.add_argument('--n', type=int)
    ap.add_argument('--result')
    ap.add_argument('--cost', type=float)
    ap.add_argument('--id')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    try:
        if a.cmd == 'init':
            print('criadas: %s' % (', '.join(init(repo)) or 'nenhuma'))
        elif a.cmd == 'start':
            start(repo, a.task, a.worktree, a.model)
        elif a.cmd == 'attempt':
            attempt(repo, a.task, a.n)
        elif a.cmd == 'finish':
            finish(repo, a.task, a.result, a.cost)
        elif a.cmd in ('pause', 'resume'):
            set_paused(repo, a.cmd == 'pause')
        elif a.cmd == 'inbox':
            print(json.dumps(pending(repo), ensure_ascii=False, indent=2))
            return 0
        elif a.cmd == 'applied':
            applied(repo, a.id)
        if a.cmd == 'show':
            print(json.dumps(snapshot(repo), ensure_ascii=False, indent=2) if a.json else render(repo))
        elif a.cmd != 'init':
            print('ok')
    except StateError as exc:
        print('recusado: %s' % exc)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
