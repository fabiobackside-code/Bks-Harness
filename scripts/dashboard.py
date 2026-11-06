#!/usr/bin/env python3
"""Painel local do bkhar: execução em ondas, consumo e modelo por papel, com interação pela inbox.

Uso: dashboard.py [REPO] [--port 8765] [--sessions DIR] [--no-open]
Escuta só em 127.0.0.1. Lê o estado; escreve só em outputs/run/inbox/.
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_state  # noqa: E402
import session_cost  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PLUGIN_ROOT = os.path.dirname(HERE)
PAGE = os.path.join(HERE, 'dashboard.html')
MAX_BODY = 16 * 1024
LOCAL_HOSTS = ('127.0.0.1', 'localhost')
FAMILIES = ('opus', 'sonnet', 'haiku', 'fable')


def _read_json(path, default=None):
    try:
        with io.open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def default_models():
    out = {}
    for path in sorted(glob.glob(os.path.join(PLUGIN_ROOT, 'agents', '*.md'))):
        with io.open(path, encoding='utf-8') as fh:
            m = re.search(r'^model:\s*(\S+)', fh.read(), re.M)
        out[os.path.splitext(os.path.basename(path))[0]] = m.group(1) if m else None
    return out


def family(model):
    low = (model or '').lower()
    return next((f for f in FAMILIES if f in low), 'outro')


def _usage_records(path):
    seen = set()
    with io.open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get('message')
            usage = msg.get('usage') if isinstance(msg, dict) else None
            if not isinstance(usage, dict):
                continue
            if msg.get('model') == '<synthetic>':
                continue
            mid = msg.get('id') or rec.get('uuid')
            if mid in seen:
                continue
            seen.add(mid)
            cw = usage.get('cache_creation') or {}
            w5, w1 = cw.get('ephemeral_5m_input_tokens'), cw.get('ephemeral_1h_input_tokens')
            if w5 is None and w1 is None:
                w5, w1 = usage.get('cache_creation_input_tokens', 0) or 0, 0
            u = {'input': usage.get('input_tokens', 0) or 0, 'output': usage.get('output_tokens', 0) or 0,
                 'cache_write_5m': w5 or 0, 'cache_write_1h': w1 or 0,
                 'cache_read': usage.get('cache_read_input_tokens', 0) or 0}
            yield (rec.get('timestamp') or '')[:10] or 'sem data', msg.get('model') or 'desconhecido', u


def cost_summary(sessions_dir):
    """Consumo dos transcripts do projeto, por família de modelo, por agente e por dia."""
    pricing = session_cost.load_pricing()
    files = [(p, 'sessão principal') for p in glob.glob(os.path.join(sessions_dir, '*.jsonl'))]
    for p in glob.glob(os.path.join(sessions_dir, '*', 'subagents', 'agent-*.jsonl')):
        meta = _read_json(p[:-len('.jsonl')] + '.meta.json', {}) or {}
        files.append((p, (meta.get('agentType') or 'subagente').split(':')[-1]))
    by_model, by_agent, by_day, unpriced = {}, {}, {}, set()
    for path, agent in files:
        for day, model, u in _usage_records(path):
            usd, key = session_cost.cost_of(pricing, model, u)
            if key is None:
                unpriced.add(model)
            tokens = sum(u.values())
            fam = family(model)
            for bucket, k in ((by_model, fam), (by_agent, agent)):
                row = bucket.setdefault(k, {'usd': 0.0, 'tokens': 0})
                row['usd'] += usd
                row['tokens'] += tokens
            by_day.setdefault(day, {}).setdefault(fam, 0.0)
            by_day[day][fam] += usd
    return {
        'total_usd': sum(r['usd'] for r in by_model.values()),
        'total_tokens': sum(r['tokens'] for r in by_model.values()),
        'by_model': [dict(familia=k, **v) for k, v in sorted(by_model.items())],
        'by_agent': sorted((dict(agente=k, **v) for k, v in by_agent.items()), key=lambda r: -r['usd']),
        'by_day': [{'dia': d, 'por_modelo': by_day[d]} for d in sorted(by_day)],
        'sem_preco': sorted(unpriced),
    }


def sessions_dir_for(repo):
    base = session_cost.PROJECTS_DIR
    slug = session_cost.slug_for_cwd(repo).lower()
    if Path(base).is_dir():
        for d in Path(base).iterdir():
            if d.is_dir() and d.name.lower() == slug:
                return str(d)
    return str(Path(base) / session_cost.slug_for_cwd(repo))


def state(repo):
    profile = _read_json(os.path.join(repo, '.bks-profile.json'), {}) or {}
    overrides = profile.get('models') or {}
    models = {role: {'padrao': d, 'efetivo': overrides.get(role, d)}
              for role, d in default_models().items()}
    blocks = []
    for p in sorted(glob.glob(os.path.join(repo, 'outputs', 'BLOQUEIO-*.md'))):
        with io.open(p, encoding='utf-8') as fh:
            text = fh.read()
        blocks.append({'task': os.path.basename(p)[len('BLOQUEIO-'):-3], 'texto': text[:4000]})
    open_count = 0
    sup = os.path.join(repo, 'decisions', 'SUPOSICOES.md')
    if os.path.isfile(sup):
        with io.open(sup, encoding='utf-8') as fh:
            open_count = sum(1 for l in fh if l.startswith('| S-') and re.search(r'\|\s*aberta\s*\|\s*$', l))
    try:
        run = run_state.snapshot(repo)
    except (run_state.StateError, OSError, ValueError):
        run = {'tasks': [], 'waves': [], 'paused': False, 'ready': []}
    return {'projeto': os.path.basename(os.path.abspath(repo)),
            'mode': (profile.get('axes') or {}).get('mode', 'colaborativo'),
            'rigor': (profile.get('axes') or {}).get('rigor'),
            'models': models, 'run': run, 'inbox': run_state.pending(repo),
            'blocks': blocks, 'assumptions_open': open_count}


def handler_for(repo, sessions_dir):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'bkhar-dashboard'

        def log_message(self, fmt, *args):
            pass

        def _send(self, status, body, ctype='application/json; charset=utf-8'):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def _local(self):
            host = (self.headers.get('Host') or '').rsplit(':', 1)[0].strip('[]')
            if host not in LOCAL_HOSTS:
                return False
            origin = self.headers.get('Origin')
            if origin:
                m = re.match(r'^https?://([^/:]+)(:\d+)?$', origin)
                return bool(m) and m.group(1) in LOCAL_HOSTS
            return True

        def do_GET(self):
            if not self._local():
                return self._send(403, {'erro': 'só localhost'})
            if self.path == '/':
                with io.open(PAGE, 'rb') as fh:
                    return self._send(200, fh.read(), 'text/html; charset=utf-8')
            if self.path == '/api/state':
                return self._send(200, state(repo))
            if self.path == '/api/cost':
                return self._send(200, cost_summary(sessions_dir))
            return self._send(404, {'erro': 'não encontrado'})

        def do_POST(self):
            if not self._local():
                return self._send(403, {'erro': 'só localhost'})
            if self.path != '/api/inbox':
                return self._send(405, {'erro': 'só /api/inbox aceita escrita'})
            size = int(self.headers.get('Content-Length') or 0)
            if size > MAX_BODY:
                return self._send(413, {'erro': 'pedido grande demais'})
            try:
                req = json.loads(self.rfile.read(size).decode('utf-8') or '{}')
                if not isinstance(req, dict):
                    raise ValueError('pedido não é objeto')
                return self._send(201, run_state.submit(repo, req))
            except (ValueError, run_state.StateError) as exc:
                return self._send(400, {'erro': str(exc)})

    return Handler


def make_server(repo, port=8765, host='127.0.0.1', sessions_dir=None):
    if host not in ('127.0.0.1',):
        raise ValueError('o painel escuta só em 127.0.0.1')
    repo = os.path.abspath(repo)
    return ThreadingHTTPServer((host, port), handler_for(repo, sessions_dir or sessions_dir_for(repo)))


def main(argv=None):
    ap = argparse.ArgumentParser(description='painel local do bkhar')
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--sessions')
    ap.add_argument('--no-open', action='store_true')
    a = ap.parse_args(argv)
    server = make_server(a.repo, a.port, sessions_dir=a.sessions)
    url = 'http://127.0.0.1:%d' % server.server_address[1]
    print('painel em %s · Ctrl+C encerra' % url)
    if not a.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
