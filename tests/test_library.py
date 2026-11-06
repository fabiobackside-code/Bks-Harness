"""Testes do scripts/library.py: catálogo, defasagem, dashboard e exportação para o vault.

Uso: python tests/test_library.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('library', os.path.join(ROOT, 'scripts', 'library.py'))
library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library)

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


def read(root, rel):
    with io.open(os.path.join(root, rel), encoding='utf-8') as fh:
        return fh.read()


def doc(status, date, title, body='', extra=''):
    return ('---\nprojeto: p\nversion: 1\nstatus: %s\n%satualizado: %s\n---\n\n# %s\n\n%s'
            % (status, extra, date, title, body))


ARCH_DIR = 'docs/library/architecture'


def project():
    root = os.path.join(tempfile.mkdtemp(), 'proj')
    write(root, '.bks-profile.json', json.dumps({
        'profile': 'backend', 'category': 'private', 'axes': {'rigor': 'poc'},
        'stack': {'backend': '.NET 10'}, 'library': {'export': 'knowledge/wiki/projetos/{projeto}'}}))
    write(root, 'STATUS.md', '# STATUS\n\n## Em uma frase\n\nO projeto está no desenho.\n\n## Fim\n')
    write(root, 'JOURNAL.md', '# JOURNAL\n\n## 2026-11-02 · Começo\n\nTexto.\n\n'
                              '## 2026-11-03 · PRD aprovado\n\nTexto.\n')
    write(root, 'docs/canonical/CONTEXT.md', doc('revisado', '2026-11-01', 'Contexto'))
    write(root, 'docs/canonical/PRD-p.md', doc('aprovado', '2026-11-02', 'PRD do p'))
    write(root, 'outputs/PLAN-p.md', doc('aprovado', '2026-11-03', 'Plano do p'))
    write(root, ARCH_DIR + '/ARCH-p.md',
          doc('aprovado', '2026-11-04', 'Arquitetura do p', 'Índice.\n',
              'baseado_em: outputs/PLAN-p.md (v1)\n'))
    write(root, ARCH_DIR + '/models/c4-contexto.md',
          doc('aprovado', '2026-11-04', 'C4 contexto',
              '```mermaid\nflowchart LR\n  a --> b\n```\n', 'modelo: c4-contexto\n'))
    write(root, 'specs/contracts/banco.md', doc('aprovado', '2026-11-04', 'Contrato do banco'))
    write(root, 'specs/features/FEAT-login.md',
          doc('aprovado', '2026-11-03', 'FEAT login', 'O usuário entra com senha forte.\n\n## Cenários\n'))
    write(root, 'decisions/ADR-001-banco.md', '# ADR-001 — Banco\n\n> Status: aceito · 2026-11-03\n')
    write(root, 'docs/input/assets/logo.png', 'png')
    return root


def vault_for(root):
    vault = os.path.dirname(root)
    write(vault, 'knowledge/wiki/index.md', '# Wiki Index\n\n## Foundations\n| Page | Summary | Tags | Status |\n'
                                            '|------|---------|------|--------|\n')
    write(vault, 'knowledge/wiki/log.md', '# Log\n')
    return vault


def test_catalog():
    print('\ncatálogo')
    root = project()
    try:
        sections = dict(library.catalog(root))
        check('canônicos trazem CONTEXT, PRD e PLAN',
              {e['path'] for e in sections['Canônicos']} ==
              {'docs/canonical/CONTEXT.md', 'docs/canonical/PRD-p.md', 'outputs/PLAN-p.md'},
              sections.get('Canônicos'))
        check('arquitetura traz índice e modelo', len(sections['Arquitetura']) == 2)
        check('título vem do primeiro cabeçalho',
              any(e['title'] == 'C4 contexto' for e in sections['Arquitetura']))
        check('decisão sem frontmatter tem data do corpo',
              sections['Decisões'][0]['date'] == '2026-11-03', sections['Decisões'])
        check('ilustração entra no catálogo',
              any(e['path'] == 'docs/input/assets/logo.png' for e in sections['Ilustrações']))
        library.index(root)
        text = read(root, 'docs/library/LIBRARY.md')
        check('LIBRARY.md lista o PRD com status', 'PRD-p.md' in text and 'aprovado' in text)
        check('index --check passa logo depois de gerar', library.index(root, check=True) == 0)
        write(root, 'specs/contracts/api.md', doc('rascunho', '2026-11-04', 'Contrato da API'))
        check('index --check falha com artefato novo', library.index(root, check=True) == 1)
    finally:
        shutil.rmtree(os.path.dirname(root))


def test_stale():
    print('\ndefasagem')
    root = project()
    try:
        check('nada defasado com fontes na mesma data', library.stale(root) == [], library.stale(root))
        write(root, 'decisions/ADR-002-cache.md', '# ADR-002 — Cache\n\n> Status: aceito · 2026-11-05\n')
        found = library.stale(root)
        check('ADR mais novo deixa os dois documentos defasados', len(found) == 2, found)
        check('motivo cita o ADR', all('ADR-002' in f['motivo'] for f in found), found)
        write(root, ARCH_DIR + '/models/c4-contexto.md',
              doc('aprovado', '2026-11-06', 'C4 contexto', '', 'fontes: [specs/contracts/*.md]\n'))
        found = [f['path'] for f in library.stale(root)]
        check('modelo com fontes próprias ignora o ADR', ARCH_DIR + '/models/c4-contexto.md' not in found, found)

        root2 = project()
        write(root2, 'outputs/PLAN-p.md', doc('aprovado', '2026-11-03', 'Plano', '').replace('version: 1', 'version: 2'))
        found = library.stale(root2)
        check('PLAN com versão nova deixa o ARCH defasado',
              any(f['path'].endswith('ARCH-p.md') and 'PLAN' in f['motivo'] for f in found), found)
        shutil.rmtree(os.path.dirname(root2))

        root3 = project()
        write(root3, ARCH_DIR + '/models/dados.md', '---\nstatus: rascunho\n---\n\n# Dados\n')
        found = library.stale(root3)
        check('modelo sem atualizado é apontado',
              any(f['path'].endswith('dados.md') and 'atualizado' in f['motivo'] for f in found), found)
        check('stale sai 1 quando há defasagem', library.main(['stale', root3]) == 1)
        shutil.rmtree(os.path.dirname(root3))
        check('stale sai 0 sem defasagem', library.main(['stale', project()]) == 0)
    finally:
        shutil.rmtree(os.path.dirname(root))


def test_build():
    print('\ndashboard')
    root = project()
    try:
        library.build(root)
        html = read(root, 'docs/library/site/index.html')
        check('mostra a frase de estado', 'O projeto está no desenho.' in html)
        check('Mermaid vira bloco renderizável', '<pre class="mermaid">' in html)
        check('Mermaid com versão fixa', library.MERMAID in html and library.MERMAID_VERSION.count('.') == 2)
        check('linha do tempo traz o JOURNAL', 'PRD aprovado' in html)
        check('síntese da FEAT traz o primeiro parágrafo', 'senha forte' in html)
        check('ilustração aponta para o arquivo do repositório', '../../../docs/input/assets/logo.png' in html)
        check('frontmatter não vaza no HTML', 'atualizado: 2026' not in html)
        check('build --check passa logo depois de gerar', library.build(root, check=True) == 0)
        write(root, 'decisions/ADR-002-cache.md', '# ADR-002 — Cache\n\n> Status: aceito · 2026-11-05\n')
        check('build --check falha com decisão nova', library.build(root, check=True) == 1)
    finally:
        shutil.rmtree(os.path.dirname(root))


def test_export():
    print('\nexportação')
    root = project()
    vault = vault_for(root)
    try:
        r = library.export(root, vault, '2026-11-04')
        check('exporta sem problema', not r['problems'], r)
        dest = 'knowledge/wiki/projetos/proj'
        page = read(vault, dest + '/arquitetura/ARCH-p.md')
        check('página tem frontmatter da knowledge', page.startswith('---\ntitle: "Arquitetura do p"'), page[:120])
        check('domínio é projetos', 'domain: "projetos"' in page)
        check('aprovado vira stable', 'status: "stable"' in page)
        check('tecnologia vem da stack', 'technologies: [dotnet]' in page, page[:400])
        check('corpo original sem o frontmatter antigo', 'Índice.' in page and 'baseado_em' not in page)
        check('ilustração copiada', os.path.isfile(os.path.join(vault, dest, 'assets', 'logo.png')))
        index = read(vault, dest + '/index.md')
        check('índice do projeto com wikilink', '[[arquitetura/ARCH-p|' in index, index)
        wiki = read(vault, 'knowledge/wiki/index.md')
        check('index.md da wiki ganha a seção Projetos', '## Projetos' in wiki and 'projetos/proj/index.md' in wiki, wiki)
        check('log.md ganha a entrada', 'export | proj' in read(vault, 'knowledge/wiki/log.md'))

        os.remove(os.path.join(root, 'specs', 'contracts', 'banco.md'))
        library.export(root, vault, '2026-11-05')
        check('página que saiu do catálogo é removida',
              not os.path.isfile(os.path.join(vault, dest, 'contratos', 'banco.md')))
        wiki = read(vault, 'knowledge/wiki/index.md')
        check('linha do projeto não se repete', wiki.count('projetos/proj/index.md') == 1, wiki)

        write(root, 'specs/contracts/banco.md', doc('aprovado', '2026-11-04', 'Banco', 'contato: dev@example.com\n'))
        r = library.export(root, vault, '2026-11-06')
        check('dado sensível recusa a exportação', bool(r['problems']), r)
        check('recusa não escreve a página',
              not os.path.isfile(os.path.join(vault, dest, 'contratos', 'banco.md')))

        write(root, '.bks-profile.json', json.dumps({'profile': 'backend', 'stack': {}}))
        check('sem library.export sai 2', library.main(['export', root, '--vault', vault]) == 2)
    finally:
        shutil.rmtree(vault)


def main():
    print('testes do library.py')
    for fn in (test_catalog, test_stale, test_build, test_export):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
