#!/usr/bin/env python3
"""Nota de status do canvas: espelho gerado do STATUS.md e de outputs/run/, nunca fonte.

Uso:
  status_note.py build [REPO]                 grava outputs/run/status-canvas.md e o imprime
  status_note.py sync [REPO] [--state S]      grava o arquivo e, dentro do Maestri, a nota e o floor status
"""
import argparse
import glob
import io
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maestri_config  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

NOTE_NAME = 'status'
NOTE_PATH = os.path.join('outputs', 'run', 'status-canvas.md')
STATES = ('working', 'blocked', 'review', 'done')
MAX_ATTEMPTS = 4
NEXT_STEP_LINES = 12


def _read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def section(markdown, title):
    """Corpo da seção `## title`, sem as linhas de régua, ou '' se não houver."""
    lines, inside = [], False
    for line in markdown.splitlines():
        if line.startswith('## '):
            if inside:
                break
            inside = line[3:].strip().lower() == title.lower()
            continue
        if inside and line.strip() != '---':
            lines.append(line)
    return '\n'.join(lines).strip()


def _tasks(repo):
    tasks = []
    for path in glob.glob(os.path.join(repo, 'outputs', 'run', 'onda-*', 'T-*.json')):
        with io.open(path, encoding='utf-8') as fh:
            tasks.append(json.load(fh))
    return sorted(tasks, key=lambda t: (t['onda'], t['id']))


def _blocks(repo):
    found = []
    for path in sorted(glob.glob(os.path.join(repo, 'outputs', 'BLOQUEIO-*.md'))):
        reason = next((l.strip() for l in _read(path).splitlines()
                       if l.strip() and not l.startswith('#') and l.strip() != '---'), '')
        found.append(('outputs/' + os.path.basename(path), reason))
    return found


def _mode(repo):
    path = os.path.join(repo, '.bks-profile.json')
    if not os.path.isfile(path):
        return 'colaborativo'
    with io.open(path, encoding='utf-8') as fh:
        return (json.load(fh).get('axes') or {}).get('mode') or 'colaborativo'


def stage(tasks):
    if not tasks:
        return 'sem execução em ondas'
    waves = sorted({t['onda'] for t in tasks})
    open_waves = [t['onda'] for t in tasks if t['estado'] not in ('passou', 'bloqueada')]
    if not open_waves:
        return 'todas as %d ondas encerradas' % len(waves)
    n = min(open_waves)
    kinds = sorted({t['tipo'] for t in tasks if t['onda'] == n})
    return 'onda %d de %d — %s' % (n, len(waves), ', '.join(kinds))


def progress(tasks):
    return '%d/%d' % (sum(1 for t in tasks if t['estado'] == 'passou'), len(tasks))


def auto_state(tasks, blocks):
    if blocks or any(t['estado'] == 'bloqueada' for t in tasks):
        return 'blocked'
    if tasks and all(t['estado'] == 'passou' for t in tasks):
        return 'done'
    return 'working'


def _task_line(t):
    title = (' — %s' % t['titulo']) if t.get('titulo') else ''
    if t['estado'] == 'passou':
        return '- [x] %s%s (tentativa %d/%d)' % (t['id'], title, t['tentativa'], MAX_ATTEMPTS)
    if t['estado'] == 'pendente':
        return '- [ ] %s%s' % (t['id'], title)
    if t['estado'] == 'bloqueada':
        return '- [ ] %s%s — bloqueada' % (t['id'], title)
    return '- [ ] %s%s — em curso, tentativa %d/%d' % (t['id'], title, t['tentativa'], MAX_ATTEMPTS)


def build(repo, now=None):
    """Texto da nota, montado só a partir dos arquivos do projeto."""
    status_path = os.path.join(repo, 'STATUS.md')
    status = _read(status_path) if os.path.isfile(status_path) else ''
    tasks, blocks = _tasks(repo), _blocks(repo)
    stamp = (now or datetime.now()).strftime('%Y-%m-%d %H:%M')
    name = os.path.basename(os.path.abspath(repo))
    next_step = section(status, 'Próximo passo').splitlines()[:NEXT_STEP_LINES]

    out = ['# Status · %s' % name,
           '> Espelho gerado de STATUS.md e outputs/run/. Não editar à mão. Atualizado: %s' % stamp,
           '',
           'Modo: %s · Etapa: %s · Concluídas: %s' % (_mode(repo), stage(tasks), progress(tasks)),
           '',
           '## Em uma frase',
           section(status, 'Em uma frase') or '(STATUS.md sem a seção)',
           '',
           '## Próximo passo',
           '\n'.join(next_step) or '(STATUS.md sem a seção)',
           '',
           '## Itens da spec']
    out += [_task_line(t) for t in tasks] or ['nenhum']
    retried = [t for t in tasks if t['estado'].startswith('tentativa') and t['tentativa'] > 1]
    out += ['', '## Falhas']
    out += ['- %s: %d tentativa(s) falharam; ver specs/tasks/, seção "Tentativas"' % (t['id'], t['tentativa'] - 1)
            for t in retried] or ['nenhuma']
    out += ['', '## Bloqueios']
    out += ['- %s — %s' % (path, reason) for path, reason in blocks] or ['nenhum']
    return '\n'.join(out) + '\n'


def write(repo, now=None):
    text = build(repo, now)
    path = os.path.join(repo, NOTE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    return text


def escape(text):
    """Conteúdo para a CLI do Maestri, que decodifica \\n e \\t: a barra literal vai dobrada."""
    return text.replace('\\', '\\\\')


def maestri_cli(repo):
    """Caminho da CLI quando o projeto liga o Maestri e a sessão está num terminal dele; senão None."""
    if not os.environ.get('MAESTRI_TERMINAL_ID') or not maestri_config.enabled(repo):
        return None
    return os.environ.get('MAESTRI_CLI') or shutil.which('maestri')


def note_name(repo):
    block = maestri_config.load(repo)
    return block['notes']['status'] if block else NOTE_NAME


def _run(args):
    done = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return done.returncode, (done.stdout or '') + (done.stderr or '')


def sync(repo, state=None, cli=None, runner=_run, now=None):
    """Grava o arquivo; com o Maestri, espelha na nota `status` e no floor status. Devolve as linhas do que fez."""
    text = write(repo, now)
    done = ['arquivo: %s' % NOTE_PATH.replace(os.sep, '/')]
    cli = cli if cli is not None else maestri_cli(repo)
    if not cli:
        return done + ['fora do Maestri ou integração desligada: nota e floor status não atualizados']
    name = note_name(repo)
    code, _ = runner([cli, 'note', 'write', name, escape(text)])
    if code != 0:
        code, _ = runner([cli, 'note', 'create', escape(text), '--name', name])
    done.append('nota %s: %s' % (name, 'ok' if code == 0 else 'falhou'))
    tasks, blocks = _tasks(repo), _blocks(repo)
    state = state or auto_state(tasks, blocks)
    code, _ = runner([cli, 'floor', 'status', stage(tasks), '--state', state, '--progress', progress(tasks)])
    done.append('floor status %s: %s' % (state, 'ok' if code == 0 else 'falhou'))
    return done


def main(argv=None):
    ap = argparse.ArgumentParser(description='nota de status do canvas')
    ap.add_argument('cmd', choices=('build', 'sync'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--state', choices=STATES)
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    if a.cmd == 'build':
        print(write(repo), end='')
        return 0
    for line in sync(repo, a.state):
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
