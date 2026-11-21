"""Guarda: recusa MediatR e qualquer dispatcher em codigo C#.

A orquestracao no padrao BKS e explicita: servico pela porta ou sessao TXC. Um
dispatcher esconde a ordem dos passos atras de uma convencao de tipo, e o
custo aparece depois: nao da para ler o fluxo sem procurar o handler.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, is_csharp, target_path, written_content

PATTERNS = [
    (re.compile(r'\busing\s+MediatR\b'), 'using MediatR'),
    (re.compile(r'\bIMediator\b'), 'IMediator'),
    (re.compile(r'\bISender\b'), 'ISender'),
    (re.compile(r'\bIPublisher\b'), 'IPublisher'),
    (re.compile(r'\bIRequestHandler\s*<'), 'IRequestHandler<>'),
    (re.compile(r'\bINotificationHandler\s*<'), 'INotificationHandler<>'),
    (re.compile(r'\bBSMediator\b'), 'BSMediator'),
    (re.compile(r'\bAddMediatR\b'), 'AddMediatR'),
]

MESSAGE = (
    'Bloqueado: {found} em {path}.\n\n'
    'O padrao BKS nao usa MediatR nem dispatcher — a orquestracao e explicita.\n\n'
    'Fluxo esperado, conforme a forma do projeto:\n'
    '  padrao direto: o adapter chama o servico pela porta; o servico chama a porta de saida\n'
    '  TXC: o adapter chama session.ExecuteAsync(code, input); a sessao conduz '
    'Validation [10] > Idempotency [20] > Processing [40] > PostProcessing [50] '
    'pelo registro por codigo\n'
    '  as duas formas devolvem PipelineResult<T>\n\n'
    'Reescreva chamando o servico pela porta, ou registre a transacao por codigo.'
)


def check(payload):
    path = target_path(payload)
    if not is_csharp(path):
        return
    content = written_content(payload)
    if not content:
        return
    hits = [label for rx, label in PATTERNS if rx.search(content)]
    if hits:
        deny(MESSAGE.format(found=', '.join(sorted(set(hits))), path=os.path.basename(path)))


guard(check)
