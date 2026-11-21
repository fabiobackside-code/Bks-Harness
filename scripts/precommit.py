"""Roda os guardas de escrita sobre o que vai para o commit; com --all, sobre o repositório inteiro.

Cada arquivo vira o payload que o hook do Claude receberia ao gravá-lo, e cada guarda decide igual.
Os guardas vêm da pasta deste script (cópia em .bkhar/guards/) ou de hooks/scripts/ no kit.
"""
import contextlib
import io
import json
import os
import subprocess
import sys

GUARDS = (
    ('secret_guard.py', None),
    ('no_dispatcher.py', ('.cs',)),
    ('comment_budget.py', ('.cs',)),
    ('dotnet_project.py', ('.cs', '.csproj', '.props', '.targets', '.sln', 'packages.config')),
)


def guards_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, 'secret_guard.py')):
        return here
    return os.path.join(os.path.dirname(here), 'hooks', 'scripts')


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, capture_output=True, check=True).stdout


def listed_files(root, everything):
    if everything:
        out = git(root, 'ls-files', '-z')
    else:
        out = git(root, 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z')
    return [f for f in out.decode('utf-8').split('\0') if f]


def file_text(root, rel, everything):
    try:
        if everything:
            with open(os.path.join(root, rel), 'rb') as f:
                data = f.read()
        else:
            data = git(root, 'show', ':' + rel)
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return ''


def load_secret_guard(gdir):
    sys.path.insert(0, gdir)
    import secret_guard
    return secret_guard


def in_process_refusal(module, payload):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            module.check(payload)
    except SystemExit:
        pass
    out = buffer.getvalue().strip()
    if not out:
        return None
    return json.loads(out)['hookSpecificOutput'].get('permissionDecisionReason') or 'recusado'


def refusal(script, payload):
    r = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True, encoding='utf-8', timeout=30)
    out = r.stdout.strip()
    if not out:
        return None
    output = json.loads(out).get('hookSpecificOutput', {})
    if output.get('permissionDecision') != 'deny':
        return None
    return output.get('permissionDecisionReason') or 'recusado'


def main(argv):
    everything = '--all' in argv
    root = git(os.getcwd(), 'rev-parse', '--show-toplevel').decode('utf-8').strip()
    root = os.path.normpath(root)
    gdir = guards_dir()
    secret = load_secret_guard(gdir)
    blocked = 0
    for rel in listed_files(root, everything):
        text = file_text(root, rel, everything)
        if text is None:
            continue
        path = os.path.join(root, rel)
        payload = {'tool_name': 'Commit', 'cwd': root,
                   'tool_input': {'file_path': path, 'content': text}}
        if everything:
            payload['bkhar_scope'] = 'all'
        for name, extensions in GUARDS:
            if extensions and not rel.lower().endswith(extensions):
                continue
            if name == 'secret_guard.py':
                reason = in_process_refusal(secret, payload)
            else:
                reason = refusal(os.path.join(gdir, name), payload)
            if reason:
                blocked += 1
                print('BLOQUEADO %s (%s)' % (rel, name))
                print('  ' + reason.replace('\n', '\n  ').rstrip())
                break
    if blocked:
        print('\n%d arquivo(s) barrado(s). Corrija ou tire do commit.' % blocked)
        return 1
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
