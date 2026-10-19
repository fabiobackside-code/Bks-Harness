#!/usr/bin/env python3
"""Publica no clone do repositório público só o que a lista permite.

Uso:
  python scripts/publish.py --check        valida o que sairia, sem copiar
  python scripts/publish.py <destino>      valida e sincroniza o clone público em <destino>

A lista do que pode sair e a regra de cada recusa estão em decisions/ADR-002.
O script não faz commit nem push: isso fica no clone público, com o ok do Fabio.
"""
import io
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOW = (
    '.claude-plugin/', 'agents/', 'commands/', 'evals/', 'hooks/', 'profiles/', 'skills/',
    'templates/', 'tests/', 'scripts/',
    'docs/artefatos/atlas/', 'docs/artefatos/apresentacao/', 'docs/artefatos/manual/',
    'docs/ARCHITECTURE.md', 'README.md', 'LICENSE', '.gitignore', '.gitattributes',
)

PRIVATE_START = '<!-- privado:inicio -->'
PRIVATE_END = '<!-- privado:fim -->'
PRIVATE_BLOCK = re.compile(r'[ \t]*' + re.escape(PRIVATE_START) + r'.*?' + re.escape(PRIVATE_END) + r'[ \t]*\n?', re.S)

LEAKS = {
    'caminho da máquina do autor': re.compile(
        r'\b[A-Za-z]:[\\/]{1,2}(?:Users[\\/]{1,2}fabio|Fabio|2brains|bks-harness|pip-tmp)'
        r'|\bX:[\\/]', re.I),
    'e-mail fora de noreply': re.compile(
        r'[\w.+-]+@(?!users\.noreply\.github\.com|anthropic\.com|example\.com)[\w-]+\.[\w.-]+'),
}

TEXT_EXT = ('.md', '.json', '.py', '.sh', '.yaml', '.yml', '.html', '.txt', '.css', '.js', '')


def allowed(rel):
    return any(rel == a or (a.endswith('/') and rel.startswith(a)) for a in ALLOW)


def tracked_files(root):
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=root, capture_output=True, check=True)
    return [p for p in out.stdout.decode('utf-8').split('\0') if p]


def strip_private(text, rel):
    """Remove os blocos privados; marcador desbalanceado é erro."""
    if text.count(PRIVATE_START) != text.count(PRIVATE_END):
        raise ValueError('%s: marcador privado desbalanceado' % rel)
    stripped = PRIVATE_BLOCK.sub('', text)
    return re.sub(r'\n{3,}', '\n\n', stripped) if stripped != text else text


def build(root, files):
    """Monta {caminho: bytes} do que sai e a lista de recusas."""
    output, problems = {}, []
    for rel in sorted(f for f in files if allowed(f)):
        with open(os.path.join(root, rel), 'rb') as fh:
            data = fh.read()
        if os.path.splitext(rel)[1].lower() in TEXT_EXT:
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                output[rel] = data
                continue
            if rel.endswith('.md'):
                try:
                    text = strip_private(text, rel)
                except ValueError as exc:
                    problems.append(str(exc))
                    continue
            for n, line in enumerate(text.splitlines(), 1):
                for label, rx in LEAKS.items():
                    m = rx.search(line)
                    if m:
                        problems.append('%s:%d  [%s]  %s' % (rel, n, label, m.group(0)))
            data = text.encode('utf-8')
        output[rel] = data
    return output, problems


def sync(output, dest):
    """Espelha output em dest, preservando o .git; devolve (gravados, removidos)."""
    written, removed = [], []
    for base, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), dest).replace('\\', '/')
            if rel not in output:
                os.remove(os.path.join(dest, rel))
                removed.append(rel)
    for rel, data in output.items():
        path = os.path.join(dest, rel)
        if os.path.isfile(path):
            with open(path, 'rb') as fh:
                if fh.read() == data:
                    continue
        os.makedirs(os.path.dirname(path) or dest, exist_ok=True)
        with open(path, 'wb') as fh:
            fh.write(data)
        written.append(rel)
    for base, dirs, _ in os.walk(dest, topdown=False):
        if '.git' not in base.split(os.sep) and base != dest and not os.listdir(base):
            os.rmdir(base)
    return written, removed


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    output, problems = build(ROOT, tracked_files(ROOT))
    if problems:
        print('publicação recusada, %d achado(s):' % len(problems))
        for p in problems:
            print('  ' + p)
        return 1
    if argv[0] == '--check':
        print('ok: %d arquivo(s) sairiam para o público' % len(output))
        return 0
    dest = os.path.abspath(argv[0])
    if os.path.normcase(dest) == os.path.normcase(ROOT):
        print('destino é o próprio repositório privado')
        return 2
    if not os.path.isdir(os.path.join(dest, '.git')):
        print('destino não é um clone git: %s' % dest)
        return 2
    written, removed = sync(output, dest)
    print('%d arquivo(s) publicados, %d gravado(s), %d removido(s)' % (len(output), len(written), len(removed)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
