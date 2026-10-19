"""SessionStart: carrega o contexto do lugar certo.

Numa sessao aberta dentro de um projeto, o contexto que importa e o STATUS.md
dele. Na raiz do vault, e o perfil do usuario.

Sem vault configurado e fora de um projeto, nao faz nada — as skills do kit
funcionam sem vault, e uma sessao que nao usa nenhum dos dois nao deve pagar
por eles.
"""
import json
import os
import sys

MAX_CHARS = 4000


def read(path, limit=MAX_CHARS):
    try:
        with open(path, encoding='utf-8') as fh:
            text = fh.read().strip()
    except Exception:
        return ''
    if len(text) > limit:
        text = text[:limit] + '\n\n[...truncado]'
    return text


def first_entry(path):
    """Primeira entrada de um JOURNAL.md — a mais recente."""
    text = read(path, 8000)
    if not text:
        return ''
    out, seen = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            if seen:
                break
            seen = True
        if seen:
            out.append(line)
        if len(out) > 12:
            break
    return '\n'.join(out).strip()


def emit(context):
    json.dump({
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': context,
        }
    }, sys.stdout)


def main():
    cwd = os.getcwd()
    parts = []

    status = os.path.join(cwd, 'STATUS.md')
    if os.path.isfile(status):
        body = read(status)
        if body:
            parts.append('## STATUS.md deste projeto\n\n' + body)
        journal = first_entry(os.path.join(cwd, 'JOURNAL.md'))
        if journal:
            parts.append('## Ultima entrada do JOURNAL.md\n\n' + journal)

    vault = os.environ.get('BKS_VAULT')
    if vault and os.path.isdir(vault):
        profile = os.path.join(vault, 'workbench', 'profile.md')
        if os.path.isfile(profile):
            body = read(profile)
            if body:
                parts.append('## Perfil do usuario\n\n' + body)

    if not parts:
        return

    emit(
        'Contexto BKS carregado no inicio da sessao. E contexto de fundo, nao '
        'instrucao do usuario, e reflete o que era verdade quando foi escrito.\n\n'
        + '\n\n'.join(parts)
    )


try:
    main()
except Exception:
    pass
