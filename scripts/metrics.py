#!/usr/bin/env python3
"""Métrica do fluxo por fase da task: o estado do recovery.py recortado no transcript da sessão.

Uso:
  metrics.py build [REPO] [--transcripts PASTA]   grava outputs/run/metrics/metrics.jsonl e METRICAS.md
  metrics.py show [REPO]                          imprime o METRICAS.md
"""
import argparse
import glob
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recovery  # noqa: E402
import session_cost  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

STATUS_LABEL = {'running': 'em curso', 'blocked': 'bloqueada', 'terminal': 'terminal', 'done': 'concluída'}
TAG = re.compile(r'<tool-use-id>([^<]+)</tool-use-id>.*?<subagent_tokens>(\d+)</subagent_tokens>', re.S)


def _ts(text):
    text = text.replace('Z', '+00:00')
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def _label(e):
    if e['status'] in ('blocked', 'terminal'):
        return 'bloqueio'
    phase = e['phase']
    if phase == 'impl':
        return 'impl-%d' % e['attempt'] if e['attempt'] else 'red'
    return {'reviewed': 'review', 'integration': 'integracao'}.get(phase, phase)


def windows(st, now):
    """Uma janela por trecho contínuo da mesma fase, do evento que a abre até o seguinte."""
    out = []
    events = st.get('events', [])
    for i, e in enumerate(events):
        if e['status'] == 'done':
            break
        label = _label(e)
        nxt = events[i + 1] if i + 1 < len(events) else None
        if out and out[-1]['phase'] == label and out[-1]['cycle'] == e['cycle']:
            win = out[-1]
        else:
            win = {'task': st['task'], 'cycle': e['cycle'], 'phase': label, 'start': e['at'], 'whats': []}
            out.append(win)
        win['whats'].append(e['what'])
        win['end'] = nxt['at'] if nxt else None
        win['closing'] = nxt['what'] if nxt else None
    for win in out:
        whats, closing = win.pop('whats'), win.pop('closing')
        win['outcome'] = closing if closing and closing.startswith('foto') else whats[-1]
        win['open'] = win['end'] is None
        end = _ts(win['end']) if win['end'] else now
        win['duration_s'] = int((end - _ts(win['start'])).total_seconds())
        win.update(tokens=0, cost_usd=0.0, roles={}, questions=0)
    return out


def _records(paths):
    """Mensagens com uso, notificações de subagente e perguntas ao usuário, com a hora de cada uma."""
    msgs, calls, subs, asks, seen = [], {}, [], [], set()
    for path in paths:
        with io.open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict) or not rec.get('timestamp'):
                    continue
                at = _ts(rec['timestamp'])
                m = rec.get('message')
                content = m.get('content') if isinstance(m, dict) else None
                for blk in content if isinstance(content, list) else []:
                    if isinstance(blk, dict) and blk.get('type') == 'tool_use':
                        if blk.get('name') == 'Agent':
                            role = (blk.get('input') or {}).get('subagent_type') or 'geral'
                            calls[blk.get('id')] = role.split(':')[-1]
                        elif blk.get('name') == 'AskUserQuestion':
                            asks.append(at)
                if 'subagent_tokens' in line:
                    for uid, tokens in TAG.findall(line):
                        subs.append((at, uid, int(tokens)))
                usage = m.get('usage') if isinstance(m, dict) else None
                if not isinstance(usage, dict):
                    continue
                mid = m.get('id') or rec.get('uuid')
                if mid in seen:
                    continue
                seen.add(mid)
                u = session_cost.empty_usage()
                cw = usage.get('cache_creation') or {}
                u.update(input=usage.get('input_tokens') or 0, output=usage.get('output_tokens') or 0,
                         cache_read=usage.get('cache_read_input_tokens') or 0,
                         cache_write_5m=cw.get('ephemeral_5m_input_tokens',
                                               usage.get('cache_creation_input_tokens') or 0) or 0,
                         cache_write_1h=cw.get('ephemeral_1h_input_tokens') or 0)
                msgs.append((at, m.get('model') or 'desconhecido', u))
    roles = [(at, calls.get(uid, 'desconhecido'), tokens) for at, uid, tokens in subs]
    return msgs, roles, asks


def _hits(wins, at, now):
    return [w for w in wins if _ts(w['start']) <= at < (_ts(w['end']) if w['end'] else now)]


def transcripts_for(repo):
    root = session_cost.projects_dir()
    slug = session_cost.slug_for_cwd(repo).lower()
    if not root.is_dir():
        return []
    return [str(f) for d in root.iterdir() if d.is_dir() and d.name.lower() == slug for f in d.glob('*.jsonl')]


def _states(repo):
    try:
        folder = recovery.state_dir(repo)
    except recovery.StateError:
        return []
    out = []
    for path in sorted(glob.glob(os.path.join(folder, 'T-*.json'))):
        with io.open(path, encoding='utf-8') as fh:
            out.append(json.load(fh))
    return out


def build(repo, transcripts=None, now=None):
    states = _states(repo)
    if not states:
        return []
    now = _ts(now) if now else datetime.now(timezone.utc)
    wins = [w for st in states for w in windows(st, now)]
    if transcripts and os.path.isdir(transcripts):
        paths = sorted(glob.glob(os.path.join(transcripts, '*.jsonl')))
    else:
        paths = transcripts_for(repo)
    msgs, roles, asks = _records(paths)
    pricing = session_cost.load_pricing()
    for at, model, usage in msgs:
        hit = _hits(wins, at, now)
        tokens = usage['input'] + usage['output'] + usage['cache_write_5m'] + usage['cache_write_1h'] \
            + usage['cache_read']
        cost, _ = session_cost.cost_of(pricing, model, usage)
        for w in hit:
            w['tokens'] += tokens // len(hit)
            w['cost_usd'] += cost / len(hit)
    for at, role, tokens in roles:
        for w in _hits(wins, at, now):
            w['roles'][role] = w['roles'].get(role, 0) + tokens
    for at in asks:
        for w in _hits(wins, at, now):
            w['questions'] += 1
    for w in wins:
        if w['phase'] == 'bloqueio' and not w['open']:
            w['questions'] += 1
        w['cost_usd'] = round(w['cost_usd'], 6)
    out = os.path.join(repo, 'outputs', 'run', 'metrics')
    os.makedirs(out, exist_ok=True)
    with io.open(os.path.join(out, 'metrics.jsonl'), 'w', encoding='utf-8', newline='\n') as fh:
        for w in wins:
            fh.write(json.dumps(w, ensure_ascii=False) + '\n')
    with io.open(os.path.join(out, 'METRICAS.md'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(states, wins, now))
    return wins


def _dur(seconds):
    h, rest = divmod(int(seconds), 3600)
    return '%dh %02dmin' % (h, rest // 60) if h else '%dmin %02ds' % divmod(rest, 60)


def _usd(v):
    return ('US$ %.2f' % v).replace('.', ',')


def render(states, wins, now):
    by_phase = {}
    for w in wins:
        key = 'impl' if w['phase'].startswith('impl-') else w['phase']
        acc = by_phase.setdefault(key, {'n': 0, 'time': 0, 'tokens': 0, 'cost': 0.0})
        acc['n'] += 1
        acc['time'] += w['duration_s']
        acc['tokens'] += w['tokens']
        acc['cost'] += w['cost_usd']
    total = sum(a['cost'] for a in by_phase.values()) or 1.0
    ranked = sorted(by_phase.items(), key=lambda kv: (kv[1]['cost'], kv[1]['time']), reverse=True)
    top, ta = ranked[0]
    lines = ['# Métricas do fluxo', '',
             '> Gerado pelo `metrics.py` em %s, sobre %d task(s). Custo estimado pela tabela local de preços.'
             % (now.strftime('%Y-%m-%d %H:%M UTC'), len(states)),
             '> Conta a sessão principal e os subagentes; os terminais do Maestri ficam fora.', '',
             'Fase que mais gasta: `%s` (%d%% do custo, %s).' % (top, round(100 * ta['cost'] / total),
                                                                  _dur(ta['time'])), '',
             '## Por fase', '',
             '| Fase | Janelas | Tempo | Tokens | Custo | % do custo |', '|---|---:|---:|---:|---:|---:|']
    for key, a in ranked:
        lines.append('| %s | %d | %s | %d | %s | %d%% |' % (key, a['n'], _dur(a['time']), a['tokens'],
                                                           _usd(a['cost']), round(100 * a['cost'] / total)))
    roles = {}
    for w in wins:
        for role, tokens in w['roles'].items():
            roles[role] = roles.get(role, 0) + tokens
    lines += ['', '## Por papel', '', '| Papel | Tokens |', '|---|---:|']
    lines += ['| %s | %d |' % (r, t) for r, t in sorted(roles.items(), key=lambda kv: -kv[1])] or ['| — | 0 |']
    lines += ['', '## Onde travou', '',
              '| Task | Estado | Ciclos | Bloqueios | Quedas | Fase mais longa | Último placar |',
              '|---|---|---:|---:|---:|---|---|']
    for st in states:
        mine = [w for w in wins if w['task'] == st['task']]
        longest = max(mine, key=lambda w: w['duration_s']) if mine else None
        whats = [e['what'] for e in st.get('events', [])]
        scores = [v['score'] for h in st.get('history', []) for v in h.get('snapshots', {}).values()]
        scores += [v['score'] for _, v in sorted(st.get('snapshots', {}).items())]
        lines.append('| %s | %s | %d | %d | %d | %s | %s |' % (
            st['task'], STATUS_LABEL.get(st['status'], st['status']), st.get('cycle', 1),
            sum(1 for w in whats if w.startswith('bloqueio')), sum(1 for w in whats if w.startswith('queda')),
            '%s (%s)' % (longest['phase'], _dur(longest['duration_s'])) if longest else '—',
            scores[-1] if scores else '—'))
    stuck = [st for st in states if st['status'] in ('blocked', 'terminal')]
    for st in stuck:
        lines.append('')
        lines.append('`%s` %s: causa `%s`, ciclo %d.' % (st['task'], STATUS_LABEL[st['status']],
                                                           st.get('block_cause') or '—', st.get('cycle', 1)))
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='métrica do fluxo por fase da task')
    ap.add_argument('cmd', choices=('build', 'show'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--transcripts')
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    path = os.path.join(repo, 'outputs', 'run', 'metrics', 'METRICAS.md')
    if a.cmd == 'build':
        wins = build(repo, a.transcripts)
        if not wins:
            print('nenhuma task com estado de recuperação; nada a medir')
            return 0
        print('gravado: %s (%d janelas)' % (os.path.relpath(path, repo), len(wins)))
        return 0
    if not os.path.isfile(path):
        print('sem métrica; rode metrics.py build')
        return 1
    with io.open(path, encoding='utf-8') as fh:
        print(fh.read())
    return 0


if __name__ == '__main__':
    sys.exit(main())
