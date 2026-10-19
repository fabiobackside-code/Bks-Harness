"""Guarda: recusa MediatR e qualquer dispatcher em codigo C#.

A orquestracao no padrao BKS e explicita, via PipelineOrchestrator. Um
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
    'O padrao BKS nao usa MediatR nem dispatcher — a orquestracao e explicita, '
    'via PipelineOrchestrator.\n\n'
    'Fluxo esperado:\n'
    '  Adapter Inbound cria a Transaction\n'
    '  UseCase.ExecuteAsync(transaction) — unico ponto de entrada publico\n'
    '  PipelineOrchestrator: Validation [10] > PreProcessing [20] > '
    'Processing [30] > PostProcessing [40]\n'
    '  retorna PipelineResult<TResponse>\n\n'
    'Reescreva chamando o use case direto pela porta em Ports/Application/, '
    'ou passe os passos ao PipelineOrchestrator.'
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
