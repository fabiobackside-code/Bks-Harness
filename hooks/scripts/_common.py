"""Utilitarios compartilhados pelos guardas do bks-harness.

Um guarda le o payload do hook em stdin, decide, e responde em stdout com o
formato de PreToolUse: allow segue em silencio, deny recusa a escrita com a
razao. Erro interno do guarda nunca bloqueia — regra que quebra o fluxo por bug
proprio deixa de ser usada em uma semana.
"""
import json
import os
import sys

CS_EXTENSIONS = ('.cs',)


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def tool_input(payload):
    return payload.get('tool_input') or {}


def target_path(payload):
    return tool_input(payload).get('file_path') or ''


def written_content(payload):
    """Texto que este tool call quer gravar.

    Write traz o arquivo inteiro em content. Edit traz o trecho novo em
    new_string. MultiEdit traz uma lista de edits; concatena os trechos novos.
    """
    ti = tool_input(payload)
    if 'content' in ti:
        return ti.get('content') or ''
    if 'new_string' in ti:
        return ti.get('new_string') or ''
    edits = ti.get('edits')
    if isinstance(edits, list):
        return '\n'.join(e.get('new_string') or '' for e in edits if isinstance(e, dict))
    return ''


def is_csharp(path):
    return path.lower().endswith(CS_EXTENSIONS)


def is_test_path(path):
    p = path.replace(chr(92), '/').lower()
    return '/tests/' in p or '/test/' in p or '.tests/' in p or p.endswith('tests.cs')


def allow():
    sys.exit(0)


def deny(reason):
    json.dump({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason,
        }
    }, sys.stdout)
    sys.exit(0)


def guard(fn):
    """Roda o guarda. Qualquer excecao interna libera a escrita."""
    try:
        fn(read_payload())
    except SystemExit:
        raise
    except Exception:
        pass
    allow()
