"""Guarda: teto de comentario em codigo C#.

Duas regras:

  1. Bloco de comentario ate 5 linhas. O que denuncia ensaio nao e a proporcao
     de comentario no arquivo, e o bloco longo — decisao e trade-off vivem no
     ARCHITECTURE.md, nao no meio do codigo.

  2. Sem marca de severidade. Quem escreve um circulo vermelho no comentario
     esta argumentando, nao descrevendo.

No codigo ficam duas coisas: contrato (uma linha em membro publico) e guarda
contra regressao (ate duas linhas, o que quebra se mudar). Sem ponteiro
para documento.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, is_csharp, target_path, written_content

MAX_BLOCK_LINES = 5

SEVERITY_MARKS = ['\U0001F534', '⚠', '\U0001F7E1', '✅', '\U0001F4CC',
                  '\U0001F6D1', '❌', '\U0001F7E2', '\U0001F525']

LINE_COMMENT = re.compile(r'^\s*(///|//)')
BLOCK_OPEN = re.compile(r'^\s*/\*')
BLOCK_CLOSE = re.compile(r'\*/')


def comment_blocks(lines):
    """Devolve (linha_inicial, tamanho) de cada bloco de comentario contiguo."""
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if LINE_COMMENT.match(line):
            start = i
            while i < n and LINE_COMMENT.match(lines[i]):
                i += 1
            blocks.append((start, i - start))
            continue
        if BLOCK_OPEN.match(line):
            start = i
            if BLOCK_CLOSE.search(line[line.index('/*') + 2:]):
                i += 1
            else:
                i += 1
                while i < n and not BLOCK_CLOSE.search(lines[i]):
                    i += 1
                i = min(i + 1, n)
            blocks.append((start, i - start))
            continue
        i += 1
    return blocks


def check(payload):
    path = target_path(payload)
    if not is_csharp(path):
        return
    content = written_content(payload)
    if not content:
        return

    lines = content.splitlines()
    name = os.path.basename(path)

    for idx, line in enumerate(lines):
        if not (LINE_COMMENT.match(line) or BLOCK_OPEN.match(line) or line.strip().startswith('*')):
            continue
        for mark in SEVERITY_MARKS:
            if mark in line:
                deny(
                    'Bloqueado: marca de severidade em comentario, {f} linha {n}.\n\n'
                    '  {src}\n\n'
                    'Marca de severidade em comentario e argumento, nao descricao. '
                    'Descreva o comportamento em texto simples; se a razao importa, '
                    'ela vive no ARCHITECTURE.md.'.format(
                        f=name, n=idx + 1, src=line.strip()[:120])
                )

    for start, size in comment_blocks(lines):
        if size > MAX_BLOCK_LINES:
            deny(
                'Bloqueado: bloco de comentario com {size} linhas em {f}, a partir da linha {n} '
                '(teto: {max}).\n\n'
                '  {src}\n  ...\n\n'
                'No codigo ficam duas coisas: contrato (uma linha em membro publico) e guarda '
                'contra regressao (ate duas linhas — o que quebra se mudar).\n\n'
                'Decisao, trade-off e historico vao para o ARCHITECTURE.md, sem ponteiro '
                'no comentario.'.format(
                    size=size, f=name, n=start + 1, max=MAX_BLOCK_LINES,
                    src=lines[start].strip()[:120])
            )


guard(check)
