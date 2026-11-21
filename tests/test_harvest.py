"""Testes do scripts/harvest.py: escopo do índice, defesa do nquantic, incremental, bloqueio e lembrete.

Uso: python tests/test_harvest.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
spec = importlib.util.spec_from_file_location('harvest', os.path.join(ROOT, 'scripts', 'harvest.py'))
hv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hv)

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
            print('          %s' % detail)
        failures.append(name)


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


ADR_A = '# ADR-001 — Dapper com conexão pelo construtor\n\n- **Data:** 2026-09-08\n- **Status:** aceita\n\n## Contexto\n\nbanco e repositório\n'
ADR_B = '# ADR-002 — Fila RabbitMQ para o envio\n\n> Status: aceito · 2026-10-19 · Fabio\n\n## Contexto\n\nmensageria\n'
ADR_NQ = '# ADR-007 — Contrato do Cliente Secreto via endpoint /pix/x\n\n- **Data:** 2026-08-01\n- **Status:** aceita\n\nautorização e segurança\n'


def vault():
    v = tempfile.mkdtemp()
    write(v, 'repos/backside/motor/decisions/ADR-001.md', ADR_A)
    write(v, 'repos/private/poc/decisions/ADR-002-fila.md', ADR_B)
    write(v, 'repos/private/poc/LEARNINGS.md', '# LEARNINGS\n\n## 2026-10-02 · teste flaky no PostgreSQL\n\nevidência\n')
    write(v, 'repos/old/antigo/decisions/ADR-001.md', ADR_A)
    write(v, 'repos/w3/nquantic/decisions/ADR-007-cliente-secreto.md', ADR_NQ)
    write(v, 'repos/w3/outro/decisions/ADR-001.md', ADR_A)
    write(v, 'repos/backup/x/decisions/ADR-001.md', ADR_A)
    write(v, 'knowledge/wiki/experiencia/_bloqueio.txt', '# termos do nquantic que não saem\nCliente Secreto\n/pix/\n')
    return v


def test_index_scope():
    print('\nescopo do índice')
    v = vault()
    try:
        idx = hv.index(v)
        entries = list(idx['entradas'].values())
        projects = sorted({e['projeto'] for e in entries})
        check('indexa backside, private, old e só o nquantic do w3',
              projects == ['antigo', 'motor', 'nquantic', 'poc'], projects)
        check('old entra marcado como histórico',
              all(e.get('historico') for e in entries if e['projeto'] == 'antigo'))
        a = next(e for e in entries if e['projeto'] == 'motor')
        check('lê título, data, estado e tema do ADR',
              a['titulo'].startswith('ADR-001') and a['data'] == '2026-09-08' and a['estado'] == 'aceita'
              and a['tema'] == 'dados', a)
        b = next(e for e in entries if e.get('titulo', '').startswith('ADR-002'))
        check('aceita o formato com Status na citação', b['data'] == '2026-10-19' and b['tema'] == 'mensageria', b)
        check('indexa os casos do LEARNINGS.md',
              any(e['tipo'] == 'learning' and e['projeto'] == 'poc' for e in entries))
        nq = [e for e in entries if e['projeto'] == 'nquantic']
        raw = json.dumps(nq, ensure_ascii=False)
        check('do nquantic grava só tema e data', nq and set(nq[0]) <= {'projeto', 'categoria', 'tipo', 'tema', 'data', 'conceito', 'mtime'}, nq)
        check('nada do nquantic vaza no índice', 'Secreto' not in raw and 'pix' not in raw and 'cliente' not in raw, raw)
        keys = json.dumps(list(idx['entradas']), ensure_ascii=False)
        check('a chave do nquantic não carrega o nome do arquivo', 'cliente-secreto' not in keys, keys)
        check('o índice fica em knowledge/wiki/experiencia/',
              os.path.isfile(os.path.join(v, 'knowledge', 'wiki', 'experiencia', '_index.json')))
    finally:
        shutil.rmtree(v)


def test_kit_source():
    print('\no kit como fonte')
    v = vault()
    kit = tempfile.mkdtemp()
    write(kit, 'decisions/ADR-018-fecha.md', ADR_A)
    write(kit, 'LEARNINGS.md', '# LEARNINGS\n\n## Preço errado na tabela\n\nevidência\n')
    try:
        idx = hv.index(v, kit)
        kit_entries = [e for e in idx['entradas'].values() if e['categoria'] == 'kit']
        check('indexa ADR e caso do kit', len(kit_entries) == 2, kit_entries)
        check('arquivo do kit apontado como kit/bks-harness',
              all(e['arquivo'].startswith('kit/bks-harness/') for e in kit_entries), kit_entries)
        check('sem kit, o índice fica só com o vault',
              all(e['categoria'] != 'kit' for e in hv.index(v)['entradas'].values()))
    finally:
        shutil.rmtree(v)
        shutil.rmtree(kit)


def test_clean_fields():
    print('\nmodelo vazio e estado')
    v = vault()
    write(v, 'repos/private/poc/LEARNINGS.md', '# LEARNINGS\n\n## {{Título curto do defeito}}\n\nmodelo\n\n'
                                               '## 2026-10-02 · teste flaky\n\nevidência\n')
    write(v, 'repos/private/poc/decisions/ADR-003-velho.md', '# ADR-003 — velho\n\n> Status: superseded\n')
    write(v, 'repos/private/poc/decisions/ADR-004-solto.md', '# ADR-004 — solto\n\nO status do pedido muda.\n')
    try:
        entries = list(hv.index(v)['entradas'].values())
        learns = [e['titulo'] for e in entries if e['tipo'] == 'learning' and e['projeto'] == 'poc']
        check('modelo vazio do LEARNINGS fica fora', learns == ['2026-10-02 · teste flaky'], learns)
        by = {e.get('titulo', '')[:7]: e.get('estado') for e in entries if e['projeto'] == 'poc'}
        check('superseded vira superada', by.get('ADR-003') == 'superada', by)
        check('palavra solta depois de status não vira estado', by.get('ADR-004') is None, by)
    finally:
        shutil.rmtree(v)


def test_incremental():
    print('\nincremental')
    v = vault()
    try:
        first = hv.index(v)
        again = hv.index(v)
        check('sem mudança, nada é relido', again['relidos'] == 0, again['relidos'])
        time.sleep(0.05)
        write(v, 'repos/private/poc/decisions/ADR-003.md',
              '# ADR-003 — OpenTelemetry\n\n- **Data:** 2026-11-01\n- **Status:** aceita\n\nobservabilidade\n')
        third = hv.index(v)
        check('arquivo novo é lido', third['relidos'] == 1 and len(third['entradas']) == len(first['entradas']) + 1,
              third['relidos'])
        os.remove(os.path.join(v, 'repos', 'private', 'poc', 'decisions', 'ADR-003.md'))
        fourth = hv.index(v)
        check('arquivo removido sai do índice', len(fourth['entradas']) == len(first['entradas']))
        themes = hv.themes(v)
        check('conta os temas', themes.get('dados', 0) >= 2, themes)
    finally:
        shutil.rmtree(v)


def test_page_check():
    print('\nchecagem da página consolidada')
    v = vault()
    try:
        ok = '# Mensageria\n\nRabbitMQ em dois projetos: poc (ADR-002).\n'
        check('página limpa passa', hv.check_page(v, ok) == [], hv.check_page(v, ok))
        bad = '# Segurança\n\nO nquantic resolveu o Cliente Secreto pela rota /pix/x.\n'
        hits = hv.check_page(v, bad)
        check('termo da lista de bloqueio recusa a página', len(hits) >= 2, hits)
        pii = '# Dados\n\nO CPF 123.456.789-09 aparecia no log.\n'
        check('dado pessoal recusa a página', hv.check_page(v, pii) != [])
    finally:
        shutil.rmtree(v)


def test_stale():
    print('\nlembrete no save')
    v = vault()
    try:
        repo = os.path.join(v, 'repos', 'private', 'poc')
        check('sem harvest, o projeto com ADR está pendente', hv.stale(repo, v))
        hv.index(v)
        check('logo depois do harvest, não está pendente', not hv.stale(repo, v))
        time.sleep(1.1)
        write(v, 'repos/private/poc/decisions/ADR-004.md', '# ADR-004 — x\n\n- **Data:** 2026-11-04\n')
        check('ADR mais novo que o harvest volta a pendente', hv.stale(repo, v))
        check('sem vault, nunca pendente', not hv.stale(repo, None))
    finally:
        shutil.rmtree(v)


def main():
    print('testes do harvest.py')
    for fn in (test_index_scope, test_kit_source, test_clean_fields, test_incremental, test_page_check, test_stale):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
