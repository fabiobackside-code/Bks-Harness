"""Guarda: README.md e ARCHITECTURE.md acompanham mudanca de contrato publico.

Toda alteracao que cria ou altera tipo publico e decisao estrutural — e decisao
estrutural pertence a documentacao, nao ao comentario nem a memoria de quem
escreveu.

O guarda recusa a escrita de um tipo publico novo enquanto os dois arquivos nao
tiverem sido tocados na mesma leva de trabalho. Ele olha o working tree do git:
se README.md e ARCHITECTURE.md ja aparecem como modificados (ou nao existem no
repositorio ainda), a escrita segue.

Silencioso fora de repositorio git, em arquivo de teste, e em arquivo que so
mexe em membro privado.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, is_csharp, is_test_path, target_path, written_content

PUBLIC_TYPE = re.compile(
    r'^\s*public\s+(?:sealed\s+|abstract\s+|static\s+|partial\s+|readonly\s+)*'
    r'(class|record|interface|struct|enum)\s+(\w+)',
    re.M)

REQUIRED = ('README.md', 'ARCHITECTURE.md')


def git(args, cwd):
    return subprocess.run(['git'] + args, cwd=cwd, capture_output=True,
                          text=True, timeout=10)


def repo_root(path):
    start = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(start):
        return None
    r = git(['rev-parse', '--show-toplevel'], start)
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def pending(root):
    """Nomes de arquivo com mudanca nao commitada no working tree."""
    r = git(['status', '--porcelain'], root)
    if r.returncode != 0:
        return set()
    names = set()
    for line in r.stdout.splitlines():
        p = line[3:].strip().strip('"')
        if ' -> ' in p:
            p = p.split(' -> ')[-1]
        names.add(os.path.basename(p))
    return names


def check(payload):
    path = target_path(payload)
    if not is_csharp(path) or is_test_path(path):
        return

    content = written_content(payload)
    types = PUBLIC_TYPE.findall(content or '')
    if not types:
        return

    root = repo_root(path)
    if not root:
        return

    touched = pending(root)
    missing = []
    for doc in REQUIRED:
        if doc in touched:
            continue
        if not os.path.exists(os.path.join(root, doc)):
            missing.append(doc + ' (nao existe no repositorio)')
        else:
            missing.append(doc)

    if not missing:
        return

    kinds = ', '.join(sorted({'%s %s' % (k, n) for k, n in types}))
    deny(
        'Bloqueado: {f} declara tipo publico ({kinds}) e a documentacao nao acompanha.\n\n'
        'Pendente: {missing}\n\n'
        'README.md e ARCHITECTURE.md sao item de DoD, na mesma lista do build e dos testes: '
        'toda task que cria ou altera tipo publico, funcao publica ou decisao estrutural '
        'atualiza os dois antes de fechar.\n\n'
        'Atualize a documentacao e repita a escrita. Se a mudanca nao altera contrato nem '
        'decisao — refactor interno, renomeacao mecanica — registre isso no ARCHITECTURE.md '
        'ou deixe o tipo internal.'.format(
            f=os.path.basename(path), kinds=kinds, missing=', '.join(missing))
    )


guard(check)
