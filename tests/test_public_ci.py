"""O CI do público: a árvore que o publish.py monta passa nos mesmos passos, sem segredo.

Monta a saída do publish.py num repositório temporário e roda nela cada passo `run:` do
.github/workflows/guards.yml, como um PR de fork rodaria. Leva cerca de um minuto.

Uso: python tests/test_public_ci.py
"""
import importlib.util
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('publish', os.path.join(ROOT, 'scripts', 'publish.py'))
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)
WORKFLOW = '.github/workflows/guards.yml'

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
            print('          %s' % detail[-1200:])
        failures.append(name)


def steps(text):
    """Comandos dos passos run:, um por linha, sem a instalação de dependência."""
    out, block = [], False
    for line in text.splitlines():
        m = re.match(r'^\s+run:\s*(.*)$', line)
        if m:
            block = m.group(1).strip() == '|'
            if not block:
                out.append(m.group(1).strip())
            continue
        if block and re.match(r'^\s{10,}\S', line):
            out.append(line.strip())
        else:
            block = False
    return [c for c in out if not c.startswith('pip ')]


def _rm(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main():
    print('CI do público sobre a árvore publicada')
    output, problems = publish.build(ROOT, publish.tracked_files(ROOT))
    check('publicação sem recusa', not problems, '; '.join(problems))
    text = output.get(WORKFLOW, b'').decode('utf-8')
    check('workflow vai ao público', bool(text))
    check('token só de leitura', re.search(r'(?m)^permissions:\s*\n\s+contents:\s*read', text) is not None)
    check('sem gatilho pull_request_target', re.search(r'(?m)^\s*pull_request_target\s*:', text) is None)
    check('sem segredo', 'secrets.' not in text)
    for rel in ('CONTRIBUTING.md', '.github/CODEOWNERS', '.github/pull_request_template.md'):
        check('%s vai ao público' % rel, rel in output)
    root = tempfile.mkdtemp(prefix='bkhar-public-')
    try:
        for rel, data in output.items():
            path = os.path.join(root, *rel.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as fh:
                fh.write(data)
        for args in (['init', '-q'], ['add', '-A'],
                     ['-c', 'user.name=t', '-c', 'user.email=t@example.com', 'commit', '-q', '-m', 'publicação']):
            subprocess.run(['git'] + args, cwd=root, capture_output=True)
        for cmd in steps(text):
            r = subprocess.run(cmd, cwd=root, shell=True, capture_output=True, text=True, encoding='utf-8',
                               errors='replace', timeout=600)
            check('passo do CI: %s' % cmd, r.returncode == 0, r.stdout + r.stderr)
    finally:
        shutil.rmtree(root, onerror=_rm)
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
