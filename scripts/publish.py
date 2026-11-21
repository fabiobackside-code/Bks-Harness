#!/usr/bin/env python3
"""Publica no clone do repositório público só o que a lista permite.

Uso:
  python scripts/publish.py --check                valida o que sairia, sem copiar
  python scripts/publish.py <destino>              valida e sincroniza o clone público em <destino>
  python scripts/publish.py --incoming <destino>   patch do que o público recebeu desde a última publicação

A lista do que pode sair e a regra de cada recusa estão em decisions/ADR-002.
O script não faz commit, tag nem push: isso fica no clone público, com o ok do Fabio.
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOW = (
    '.claude-plugin/', '.githooks/', 'agents/', 'commands/', 'evals/', 'hooks/', 'profiles/', 'skills/',
    'templates/', 'tests/', 'scripts/', 'bin/', 'providers/', 'requirements.txt',
    'docs/artefatos/atlas/', 'docs/artefatos/apresentacao/', 'docs/artefatos/manual/',
    'docs/artefatos/treinamento/', 'docs/artefatos/maestri/', 'docs/artefatos/guia/',
    'docs/ARCHITECTURE.md', 'docs/regras.md', 'rules.json', 'README.md', 'LICENSE', '.gitignore', '.gitattributes',
    '.github/', 'CONTRIBUTING.md',
)
MANIFEST = '.publish-manifest.json'

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
    output[MANIFEST] = manifest(root, output)
    return output, problems


def digest(data):
    """Hash do conteúdo com CRLF lido como LF: o autocrlf do clone não conta como mudança."""
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def version(root):
    try:
        with io.open(os.path.join(root, '.claude-plugin', 'plugin.json'), encoding='utf-8') as fh:
            return json.load(fh).get('version')
    except (OSError, ValueError):
        return None


def manifest(root, output):
    files = {rel: digest(data) for rel, data in sorted(output.items()) if rel != MANIFEST}
    text = json.dumps({'version': version(root), 'files': files}, ensure_ascii=False, indent=1)
    return (text + '\n').encode('utf-8')


def dest_files(dest):
    found = {}
    for base, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), dest).replace('\\', '/')
            if rel != MANIFEST:
                with open(os.path.join(dest, rel), 'rb') as fh:
                    found[rel] = digest(fh.read())
    return found


def external_changes(output, dest):
    """Arquivos do clone que a publicação anterior não deixou e que a atual apagaria ou sobrescreveria."""
    path = os.path.join(dest, MANIFEST)
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding='utf-8') as fh:
        previous = json.load(fh).get('files', {})
    current = dest_files(dest)
    coming = {rel: digest(data) for rel, data in output.items() if rel != MANIFEST}
    changed = [rel for rel, h in current.items() if previous.get(rel) != h and coming.get(rel) != h]
    deleted = [rel for rel, h in previous.items()
               if rel not in current and coming.get(rel) == h]
    return sorted(changed) + ['%s (apagado no público)' % rel for rel in sorted(deleted)]


def incoming(dest, patch_path):
    """Grava o patch das mudanças do público desde a última publicação; devolve o caminho ou None."""
    last = subprocess.run(['git', '-C', dest, 'log', '-1', '--format=%H', '--', MANIFEST],
                          capture_output=True, text=True).stdout.strip()
    if not last:
        return None
    diff = subprocess.run(['git', '-C', dest, 'diff', '--binary', last, 'HEAD', '--', '.',
                           ':(exclude)%s' % MANIFEST], capture_output=True).stdout
    os.makedirs(os.path.dirname(patch_path), exist_ok=True)
    with open(patch_path, 'wb') as fh:
        fh.write(diff)
    return patch_path if diff.strip() else None


def tag_hint(root, dest):
    v = version(root)
    if not v:
        return None
    tags = subprocess.run(['git', '-C', dest, 'tag', '-l', 'v' + v], capture_output=True, text=True).stdout
    if tags.strip():
        return 'a tag v%s já existe no público: a versão do plugin.json não mudou desde a última' % v
    return ('versão %s: depois do merge da release na main do público, rode no clone '
            'git tag v%s && git push origin v%s' % (v, v, v))


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
    incoming_mode = len(argv) == 2 and argv[0] == '--incoming'
    if len(argv) != 1 and not incoming_mode:
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
    dest = os.path.abspath(argv[-1])
    if os.path.normcase(dest) == os.path.normcase(ROOT):
        print('destino é o próprio repositório privado')
        return 2
    if not os.path.isdir(os.path.join(dest, '.git')):
        print('destino não é um clone git: %s' % dest)
        return 2
    if incoming_mode:
        patch = incoming(dest, os.path.join(ROOT, 'outputs', 'publish', 'incoming.patch'))
        if not patch:
            print('nada do público para trazer desde a última publicação')
            return 0
        print('patch gravado: %s' % os.path.relpath(patch, ROOT))
        print('revise e aplique no privado: git apply --3way %s' % os.path.relpath(patch, ROOT).replace('\\', '/'))
        return 0
    external = external_changes(output, dest)
    if external is None:
        print('sem %s no clone: primeira publicação com manifesto, sem conferir contribuição' % MANIFEST)
    elif external:
        print('publicação recusada: o público tem mudança que não veio do privado e seria apagada:')
        for rel in external:
            print('  ' + rel)
        print('traga-a antes: python scripts/publish.py --incoming %s' % argv[-1])
        return 1
    written, removed = sync(output, dest)
    print('%d arquivo(s) publicados, %d gravado(s), %d removido(s)' % (len(output), len(written), len(removed)))
    hint = tag_hint(ROOT, dest)
    if hint:
        print(hint)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
