"""Testes do scripts/dashboard.py: só localhost, só escreve na inbox, custo por modelo, agente e dia.

Uso: python tests/test_dashboard.py
"""
import http.client
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
spec = importlib.util.spec_from_file_location('dashboard', os.path.join(ROOT, 'scripts', 'dashboard.py'))
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)
import run_state  # noqa: E402

failures = []
checks = 0


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


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


GRAPH = {'projeto': 'p', 'tasks': [
    {'id': 'T-001', 'titulo': 'contrato', 'tipo': 'desenho', 'papel': 'architect', 'lente': 'banco',
     'depende_de': [], 'consome': ['docs/library/architecture/ARCH-p.md'], 'produz': ['specs/contracts/banco.md'],
     'arquivos': ['specs/contracts/banco.md']}]}


def usage_line(model, ts, out_tokens, mid):
    return json.dumps({'type': 'assistant', 'timestamp': ts, 'message': {
        'id': mid, 'model': model, 'usage': {'input_tokens': 1000, 'output_tokens': out_tokens,
                                             'cache_read_input_tokens': 0,
                                             'cache_creation_input_tokens': 0}}})


def project():
    root = tempfile.mkdtemp()
    write(root, 'outputs/GRAPH-p.json', json.dumps(GRAPH))
    write(root, '.bks-profile.json', json.dumps({
        'profile': 'backend', 'category': 'p', 'axes': {'mode': 'autonomo', 'rigor': 'poc'},
        'models': {'developer': 'opus'}}))
    write(root, 'outputs/BLOQUEIO-T-001.md', '# Bloqueio\n\nQual schema usar?\n')
    write(root, 'decisions/SUPOSICOES.md',
          '| # | Data |\n|---|---|\n| S-001 | x | aberta |\n| S-002 | x | confirmada |\n')
    run_state.init(root)
    projects = tempfile.mkdtemp()
    sess = os.path.join(projects, 'slug')
    write(sess, 's1.jsonl', usage_line('claude-opus-5-5', '2026-11-04T10:00:00Z', 2000, 'm1') + '\n')
    write(sess, 's1/subagents/agent-a1.jsonl',
          usage_line('claude-sonnet-5-5', '2026-11-05T10:00:00Z', 500, 'm2') + '\n')
    write(sess, 's1/subagents/agent-a1.meta.json', json.dumps({'agentType': 'bkhar:developer'}))
    return root, sess


def snapshot_files(root):
    out = {}
    for d, _, files in os.walk(root):
        for f in files:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = os.path.getmtime(p)
    return out


class Client:
    def __init__(self, server):
        self.host, self.port = server.server_address[:2]

    def call(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection(self.host, self.port, timeout=5)
        h = {'Host': '127.0.0.1:%d' % self.port}
        h.update(headers or {})
        data = json.dumps(body).encode('utf-8') if body is not None else None
        if data is not None:
            h['Content-Type'] = 'application/json'
        conn.request(method, path, body=data, headers=h)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        try:
            return resp.status, json.loads(raw.decode('utf-8'))
        except ValueError:
            return resp.status, raw.decode('utf-8', 'replace')


def test_cost():
    print('\nconsumo')
    root, sess = project()
    try:
        c = dashboard.cost_summary(sess)
        models = {m['familia'] for m in c['by_model']}
        check('custo por família de modelo', models == {'opus', 'sonnet'}, c['by_model'])
        agents = {a['agente'] for a in c['by_agent']}
        check('custo por agente, com a sessão principal', agents == {'sessão principal', 'developer'},
              c['by_agent'])
        check('custo por dia', [d['dia'] for d in c['by_day']] == ['2026-11-04', '2026-11-05'],
              c['by_day'])
        check('total soma as partes',
              abs(c['total_usd'] - sum(m['usd'] for m in c['by_model'])) < 1e-9, c)
        check('pasta sem transcript devolve zero', dashboard.cost_summary(tempfile.mkdtemp())['total_usd'] == 0)
    finally:
        shutil.rmtree(root)


def test_server():
    print('\nservidor')
    root, sess = project()
    server = dashboard.make_server(root, port=0, sessions_dir=sess)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    cli = Client(server)
    try:
        check('escuta só em 127.0.0.1', server.server_address[0] == '127.0.0.1')
        try:
            dashboard.make_server(root, port=0, host='0.0.0.0')
            check('recusa escutar fora do localhost', False)
        except ValueError:
            check('recusa escutar fora do localhost', True)

        status, page = cli.call('GET', '/')
        check('serve a página', status == 200 and '<title>' in page)

        status, st = cli.call('GET', '/api/state')
        check('estado traz tasks, modo e modelos',
              status == 200 and st['mode'] == 'autonomo' and st['run']['tasks'][0]['id'] == 'T-001', st)
        check('modelo efetivo combina frontmatter e perfil',
              st['models']['developer'] == {'padrao': 'sonnet', 'efetivo': 'opus'}
              and st['models']['architect']['efetivo'] == 'opus', st['models'])
        check('estado lista os bloqueios', st['blocks'] and st['blocks'][0]['task'] == 'T-001', st['blocks'])
        check('estado conta as suposições abertas', st['assumptions_open'] == 1, st['assumptions_open'])

        status, cost = cli.call('GET', '/api/cost')
        check('custo pela API', status == 200 and cost['total_usd'] > 0, cost)

        before = snapshot_files(root)
        status, r = cli.call('POST', '/api/inbox', {'tipo': 'modelo', 'papel': 'tester', 'modelo': 'opus'},
                             {'Origin': 'http://127.0.0.1:%d' % cli.port})
        check('pedido válido entra na inbox', status == 201 and r['id'], r)
        after = snapshot_files(root)
        changed = [p for p in after if before.get(p) != after[p]]
        check('a escrita fica só na inbox',
              changed and all(p.replace(os.sep, '/').startswith('outputs/run/inbox/') for p in changed),
              changed)

        status, r = cli.call('POST', '/api/inbox', {'tipo': 'apagar'})
        check('pedido inválido volta 400', status == 400 and 'erro' in r, r)
        status, r = cli.call('POST', '/api/inbox', {'tipo': 'pausar'}, {'Origin': 'http://evil.example'})
        check('Origin de fora volta 403', status == 403)
        status, r = cli.call('GET', '/api/state', headers={'Host': 'evil.example'})
        check('Host de fora volta 403', status == 403)
        status, r = cli.call('POST', '/api/state', {})
        check('POST fora da inbox volta 405', status == 405)
        status, r = cli.call('GET', '/../../etc/passwd')
        check('caminho desconhecido volta 404', status == 404)
        status, r = cli.call('POST', '/api/inbox', {'tipo': 'mensagem', 'task': 'T-001', 'texto': 'x' * 20000})
        check('corpo grande demais volta 413', status == 413)
    finally:
        server.shutdown()
        server.server_close()
        shutil.rmtree(root)


def main():
    print('testes do dashboard.py')
    for fn in (test_cost, test_server):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
