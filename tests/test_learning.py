"""Testes do scripts/learning.py: proposta candidata, filtro de dado sensível, vault, promoção e rejeição.

Uso: python tests/test_learning.py
"""
import importlib.util
import io
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
        'chave de API': 'use sk-ant-api03-abcdefghijklmnopqrstuv',
        'token do GitHub': 'ghp_abcdefghijklmnopqrstuvwxyz0123456789',
        'senha': 'password=Sup3rSecreta',
        'chave privada': '-----BEGIN RSA PRIVATE KEY-----',
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


def main():
    print('testes do learning.py')
    for fn in (test_propose, test_scrub, test_vault_export, test_promote_and_reject):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
