"""Testes do scripts/status_note.py: a nota espelha STATUS.md e outputs/run/, e só fala com o Maestri dentro dele.

Uso: python tests/test_status_note.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('status_note', os.path.join(ROOT, 'scripts', 'status_note.py'))
status_note = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status_note)

failures = []
checks = 0
NOW = datetime(2026, 11, 6, 15, 30)


def check(name, condition, detail=''):
    global checks
    checks += 1
    if condition:
        print('  ok    %s' % name)
    else:
        print('  FALHA %s' % name)
        if detail:
            print('          %s' % detail)
        failures.append(name)


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


STATUS = """# STATUS — p

## Em uma frase

Onda 2 em curso, sem bloqueio de decisão.

---

## Próximo passo

1. Terminar a T-002.
2. Rodar a revisão da onda.

## Decisões fechadas

| 1 | algo |
"""


def task(tid, onda, estado, tentativa=0, tipo='construcao', titulo=''):
    return {'id': tid, 'onda': onda, 'titulo': titulo, 'tipo': tipo, 'papel': 'developer',
            'estado': estado, 'tentativa': tentativa, 'eventos': []}


def project(tasks=(), blocks=(), mode='autonomo'):
    root = os.path.join(tempfile.mkdtemp(), 'proj')
    write(root, 'STATUS.md', STATUS)
    write(root, '.bks-profile.json', json.dumps({'axes': {'mode': mode}}))
    for t in tasks:
        write(root, 'outputs/run/onda-%d/%s.json' % (t['onda'], t['id']), json.dumps(t))
    for name, body in blocks:
        write(root, 'outputs/BLOQUEIO-%s.md' % name, body)
    return root


def test_build():
    print('\nbuild')
    root = project([task('T-001', 1, 'passou', 1, 'desenho', 'contrato do banco'),
                    task('T-002', 2, 'tentativa 3', 3),
                    task('T-003', 2, 'pendente')],
                   [('T-009', '# Bloqueio\n\nFalta a chave do provedor.\n')])
    text = status_note.build(root, NOW)
    check('cabeçalho diz que é espelho e não se edita', 'Espelho gerado de STATUS.md e outputs/run/' in text
          and 'Não editar à mão' in text)
    check('data da geração entra', 'Atualizado: 2026-11-06 15:30' in text)
    check('modo vem do perfil', 'Modo: autonomo' in text)
    check('etapa é a primeira onda aberta', 'Etapa: onda 2 de 2 — construcao' in text, text)
    check('progresso conta só as passadas', 'Concluídas: 1/3' in text)
    check('frase copiada do STATUS.md', 'Onda 2 em curso, sem bloqueio de decisão.' in text)
    check('próximo passo copiado sem a régua', '1. Terminar a T-002.' in text and '\n---' not in text)
    check('seção seguinte do STATUS.md não vaza', 'Decisões fechadas' not in text)
    check('task passada marcada com título', '- [x] T-001 — contrato do banco (tentativa 1/4)' in text)
    check('task em curso mostra a tentativa', '- [ ] T-002 — em curso, tentativa 3/4' in text)
    check('task pendente sem tentativa', '- [ ] T-003\n' in text)
    check('falha conta as tentativas anteriores', 'T-002: 2 tentativa(s) falharam' in text)
    check('bloqueio com o motivo', '- outputs/BLOQUEIO-T-009.md — Falta a chave do provedor.' in text)


def test_empty():
    print('\nprojeto sem execução')
    root = project(mode='colaborativo')
    os.remove(os.path.join(root, '.bks-profile.json'))
    text = status_note.build(root, NOW)
    check('sem perfil vale colaborativo', 'Modo: colaborativo' in text)
    check('sem ondas', 'Etapa: sem execução em ondas · Concluídas: 0/0' in text)
    check('listas vazias aparecem como nenhum', '## Itens da spec\nnenhum' in text
          and '## Falhas\nnenhuma' in text and '## Bloqueios\nnenhum' in text)
    os.remove(os.path.join(root, 'STATUS.md'))
    check('sem STATUS.md não quebra', '(STATUS.md sem a seção)' in status_note.build(root, NOW))


def test_state():
    print('\nestado do floor')
    check('bloqueio vira blocked', status_note.auto_state([task('T-1', 1, 'pendente')], [('x', 'y')]) == 'blocked')
    check('task bloqueada vira blocked', status_note.auto_state([task('T-1', 1, 'bloqueada')], []) == 'blocked')
    check('tudo passou vira done', status_note.auto_state([task('T-1', 1, 'passou', 1)], []) == 'done')
    check('em curso vira working', status_note.auto_state([task('T-1', 1, 'tentativa 1', 1)], []) == 'working')
    check('todas encerradas', status_note.stage([task('T-1', 1, 'passou', 1)]) == 'todas as 1 ondas encerradas')


def test_escape():
    print('\nescape para a CLI')
    check('barra invertida dobrada', status_note.escape('outputs\\run') == 'outputs\\\\run')
    check('quebra de linha real preservada', status_note.escape('a\nb') == 'a\nb')


class Runner:
    def __init__(self, fail_write=False):
        self.calls, self.fail_write = [], fail_write

    def __call__(self, args):
        self.calls.append(args)
        if self.fail_write and args[1:3] == ['note', 'write']:
            return 1, 'note not found'
        return 0, ''


def test_sync():
    print('\nsync')
    root = project([task('T-001', 1, 'passou', 1), task('T-002', 1, 'tentativa 1', 1)])
    runner = Runner()
    old = os.environ.pop('MAESTRI_TERMINAL_ID', None)
    try:
        out = status_note.sync(root, runner=runner, now=NOW)
    finally:
        if old is not None:
            os.environ['MAESTRI_TERMINAL_ID'] = old
    path = os.path.join(root, 'outputs', 'run', 'status-canvas.md')
    check('fora do Maestri grava o arquivo', os.path.isfile(path))
    check('fora do Maestri não chama a CLI', runner.calls == [], str(runner.calls))
    check('fora do Maestri diz o que não fez', any('fora do Maestri' in l for l in out))

    os.environ['MAESTRI_TERMINAL_ID'] = 'x'
    try:
        check('dentro do Maestri sem bloco maestri não usa a CLI', status_note.maestri_cli(root) is None)
        profile = json.loads(io.open(os.path.join(root, '.bks-profile.json'), encoding='utf-8').read())
        profile['maestri'] = {'enabled': False, 'notes': {'status': 'painel'}}
        write(root, '.bks-profile.json', json.dumps(profile))
        check('integração desligada não usa a CLI', status_note.maestri_cli(root) is None)
        check('nome da nota vem do perfil', status_note.note_name(root) == 'painel')
    finally:
        if old is None:
            os.environ.pop('MAESTRI_TERMINAL_ID', None)
        else:
            os.environ['MAESTRI_TERMINAL_ID'] = old
    profile['maestri'] = {'enabled': True}
    write(root, '.bks-profile.json', json.dumps(profile))

    runner = Runner()
    out = status_note.sync(root, cli='maestri', runner=runner, now=NOW)
    check('dentro do Maestri escreve a nota status', runner.calls[0][:4] == ['maestri', 'note', 'write', 'status'])
    with io.open(path, encoding='utf-8') as fh:
        check('a nota recebe o mesmo texto do arquivo', runner.calls[0][4] == status_note.escape(fh.read()))
    check('floor status com estado e progresso',
          runner.calls[1] == ['maestri', 'floor', 'status', 'onda 1 de 1 — construcao',
                              '--state', 'working', '--progress', '1/2'], str(runner.calls[1]))
    check('relata nota e floor', 'nota status: ok' in out and 'floor status working: ok' in out, str(out))

    runner = Runner(fail_write=True)
    status_note.sync(root, state='review', cli='maestri', runner=runner, now=NOW)
    check('nota ausente é criada com nome fixo',
          runner.calls[1][:3] == ['maestri', 'note', 'create'] and runner.calls[1][-2:] == ['--name', 'status'])
    check('estado explícito vence o automático', runner.calls[2][5] == 'review')


def main():
    print('testes do status_note.py')
    for fn in (test_build, test_empty, test_state, test_escape, test_sync):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
