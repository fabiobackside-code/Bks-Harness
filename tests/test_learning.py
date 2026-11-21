"""Testes do scripts/learning.py: proposta candidata, filtro de dado sensível, vault, promoção e rejeição.

Uso: python tests/test_learning.py
"""
import importlib.util
import io
import contextlib
import glob
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('learning', os.path.join(ROOT, 'scripts', 'learning.py'))
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)

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


def text(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def project():
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, 'decisions'))
    return root


def test_propose():
    print('\nproposta candidata')
    root = project()
    try:
        p = lr.propose(root, 'correcao', 'Repositório Dapper recebe a conexão pelo construtor.',
                       'o Fabio recusou a FEAT-cadastro: conexão aberta dentro do método',
                       origem='/bkhar:refine FEAT-cadastro · architect')
        check('grava em inbox/proposals/', os.path.dirname(p).endswith(os.path.join('inbox', 'proposals')))
        meta = lr.meta(p)
        check('nasce candidata, com tipo, origem e evidência',
              meta['status'] == 'candidata' and meta['tipo'] == 'correcao' and meta['origem']
              and 'evidencia' in meta, meta)
        try:
            lr.propose(root, 'correcao', 'regra', '', origem='x')
            check('recusa proposta sem evidência', False)
        except lr.LearningError:
            check('recusa proposta sem evidência', True)
        try:
            lr.propose(root, 'palpite', 'regra', 'ev', origem='x')
            check('recusa tipo desconhecido', False)
        except lr.LearningError:
            check('recusa tipo desconhecido', True)
    finally:
        shutil.rmtree(root)


def test_scrub():
    print('\nfiltro de dado pessoal e segredo')
    cases = {
        'e-mail': 'avise joao.silva@example.com',
        'CPF': 'cliente 123.456.789-09 reclamou',
        'CNPJ': 'empresa 12.345.678/0001-95',
        'cartão': 'cartão 4111 1111 1111 1111',
        'chave de API': 'use sk-ant-api03-abcdefghijklmnopqrstuv',  # bkhar-allow-secret
        'token do GitHub': 'ghp_abcdefghijklmnopqrstuvwxyz0123456789',  # bkhar-allow-secret
        'senha': 'password=Sup3rSecreta',
        'chave privada': '-----BEGIN RSA PRIVATE KEY-----',  # bkhar-allow-secret
        'JWT': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U',
    }
    for name, sample in cases.items():
        check('acusa %s' % name, bool(lr.scrub(sample)), lr.scrub(sample))
    clean = 'Repositório recebe IDbConnection pelo construtor; teste com Testcontainers 4.1.'
    check('texto técnico passa limpo', lr.scrub(clean) == [], lr.scrub(clean))


def test_vault_export():
    print('\nida ao vault')
    root, vault = project(), tempfile.mkdtemp()
    try:
        ok = lr.propose(root, 'aprendizado', 'Teste de integração sobe PostgreSQL por Testcontainers.',
                        'commit abc123 corrigiu o teste flaky', origem='/bkhar:review · quality')
        bad = lr.propose(root, 'correcao', 'Não logar o CPF 123.456.789-09 do cliente.',
                         'review', origem='/bkhar:review · security')
        result = lr.export_to_vault(root, vault)
        exported = os.listdir(os.path.join(vault, 'inbox', 'proposals'))
        check('leva a candidata limpa ao vault', len(exported) == 1 and result['exportadas'] == [ok], result)
        check('o arquivo no vault nomeia o projeto', exported[0].startswith(os.path.basename(root) + '--'), exported)
        check('recusa a que tem dado sensível', [r['arquivo'] for r in result['recusadas']] == [bad], result)
        check('a candidata exportada fica marcada', lr.meta(ok).get('exportado_em'))
        again = lr.export_to_vault(root, vault)
        check('exportar de novo não duplica', again['exportadas'] == [], again)
        check('sem vault não faz nada', lr.export_to_vault(root, None)['exportadas'] == [])
    finally:
        shutil.rmtree(root)
        shutil.rmtree(vault)


def test_promote_and_reject():
    print('\npromoção e rejeição')
    root, vault, kit = project(), tempfile.mkdtemp(), tempfile.mkdtemp()
    try:
        a = lr.propose(root, 'correcao', 'Regra A.', 'ev', origem='x')
        b = lr.propose(root, 'correcao', 'Regra B.', 'ev', origem='x')
        c = lr.propose(root, 'correcao', 'Regra C.', 'ev', origem='x')
        d = lr.propose(root, 'correcao', 'Regra D.', 'ev', origem='x')
        pa = lr.promote(root, a, 'projeto')
        check('regra do projeto vai para brain/engineering/regras/ promovida',
              os.path.dirname(pa).endswith(os.path.join('brain', 'engineering', 'regras'))
              and lr.meta(pa)['status'] == 'promovida', pa)
        check('a proposta promovida sai da inbox', not os.path.exists(a))
        pb = lr.promote(root, b, 'vault', vault=vault)
        check('regra do vault vai para workbench/regras/',
              pb.startswith(os.path.join(vault, 'workbench', 'regras')) and lr.meta(pb)['status'] == 'promovida', pb)
        pc = lr.promote(root, c, 'kit', kit=kit)
        check('regra do kit espera eval em inbox/proposals/ do harness',
              pc.startswith(os.path.join(kit, 'inbox', 'proposals')) and lr.meta(pc)['status'] == 'para-eval', pc)
        pd = lr.reject(root, d, 'duplica a regra A')
        check('rejeitada vai para archive/proposals/ com o motivo',
              os.path.dirname(pd).endswith(os.path.join('archive', 'proposals'))
              and lr.meta(pd)['status'] == 'rejeitada' and 'duplica' in lr.meta(pd)['motivo'], pd)
        try:
            lr.promote(root, lr.propose(root, 'correcao', 'E.', 'ev', origem='x'), 'vault', vault=None)
            check('promover ao vault sem vault recusa', False)
        except lr.LearningError:
            check('promover ao vault sem vault recusa', True)
    finally:
        for d_ in (root, vault, kit):
            shutil.rmtree(d_)


def test_contradiction():
    print('\ncontradição da auditoria')
    root = project()
    try:
        p = lr.propose(root, 'contradicao', 'A diz 4 estágios, B diz 5.', 'a.md:3 x b.md:9', origem='audit --deep pipeline')
        check('contradição é tipo aceito e fica candidata', lr.meta(p)['tipo'] == 'contradicao'
              and lr.meta(p)['status'] == 'candidata', p)
        r = lr.resolve(root, p, 'b.md corrigido para 4 estágios')
        check('corrigida vai para archive/proposals/ com a correção',
              os.path.dirname(r).endswith(os.path.join('archive', 'proposals'))
              and lr.meta(r)['status'] == 'corrigida' and '4 estágios' in lr.meta(r)['correcao'], r)
        check('a corrigida sai da inbox', not os.path.exists(p))
        try:
            lr.resolve(root, lr.propose(root, 'contradicao', 'C.', 'ev', origem='x'), '')
            check('resolver sem dizer a correção recusa', False)
        except lr.LearningError:
            check('resolver sem dizer a correção recusa', True)
    finally:
        shutil.rmtree(root)


def test_apply_to_skill():
    print('\nregra do kit no histórico da skill')
    root, kit = project(), tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(kit, 'skills', 'bks-tests'))
        with io.open(os.path.join(kit, 'skills', 'bks-tests', 'SKILL.md'), 'w', encoding='utf-8') as fh:
            fh.write('---\nname: bks-tests\n---\n\n# Testes\n')
        cand = lr.propose(root, 'aprendizado', 'Teste sai com código 1 na falha.', 'f33ec27', origem='save · quality')
        try:
            lr.apply(kit, cand, 'bks-tests')
            check('candidata não se aplica sem passar pelo retro', False)
        except lr.LearningError:
            check('candidata não se aplica sem passar pelo retro', True)
        pk = lr.promote(root, cand, 'kit', kit=kit)
        try:
            lr.apply(kit, pk, 'nao-existe')
            check('skill inexistente recusa', False)
        except lr.LearningError:
            check('skill inexistente recusa', True)
        done = lr.apply(kit, pk, 'bks-tests')
        skill = text(os.path.join(kit, 'skills', 'bks-tests', 'SKILL.md'))
        check('skill ganha o histórico de regras', '## Histórico de regras' in skill)
        check('linha com a regra e a proposta de origem',
              'Teste sai com código 1 na falha.' in skill and 'archive/proposals/%s' % os.path.basename(pk) in skill
              and 'f33ec27' in skill, skill)
        check('proposta arquivada como aplicada e eval pendente',
              lr.meta(done)['status'] == 'aplicada' and lr.meta(done)['eval'] == 'pendente'
              and os.path.dirname(done).endswith(os.path.join('archive', 'proposals')), done)
        check('proposta sai da inbox do kit', not os.path.exists(pk))
    finally:
        shutil.rmtree(root)
        shutil.rmtree(kit)


def test_cli_in_english():
    print('\nlinha de comando em inglês')
    root = tempfile.mkdtemp()
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lr.main(['propose', root, '--type', 'contradiction', '--rule', 'A vale.',
                            '--evidence', 'a.md:1 x b.md:2', '--origin', 'audit --deep teste'])
        created = glob.glob(os.path.join(root, 'inbox', 'proposals', '*.md'))
        check('--type contradiction grava a proposta', code in (0, None) and len(created) == 1, out.getvalue())
        check('o arquivo grava o tipo em português', created and 'tipo: contradicao' in io.open(created[0], encoding='utf-8').read())
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                lr.main(['propose', root, '--tipo', 'contradicao'])
            refused = False
        except SystemExit:
            refused = True
        check('a flag antiga --tipo é recusada', refused)
    finally:
        shutil.rmtree(root)


def main():
    print('testes do learning.py')
    for fn in (test_propose, test_scrub, test_vault_export, test_promote_and_reject, test_contradiction,
               test_apply_to_skill, test_cli_in_english):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
