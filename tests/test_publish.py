"""Testes do scripts/publish.py: o que sai, o que é recusado, o que é removido do clone.

Uso: python tests/test_publish.py
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('publish', os.path.join(ROOT, 'scripts', 'publish.py'))
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)

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


def source(files):
    root = tempfile.mkdtemp()
    for rel, text in files.items():
        write(root, rel, text)
    return root


def test_allowlist():
    print('\nlista do que pode sair')
    root = source({'skills/a/SKILL.md': 'x', 'STATUS.md': 'x', 'docs/specs/f.md': 'x',
                   'docs/ARCHITECTURE.md': 'x', 'docs/artefatos/historico/v1.html': 'x'})
    out, problems = publish.build(root, ['skills/a/SKILL.md', 'STATUS.md', 'docs/specs/f.md',
                                         'docs/ARCHITECTURE.md', 'docs/artefatos/historico/v1.html'])
    check('skill sai', 'skills/a/SKILL.md' in out)
    check('ARCHITECTURE sai', 'docs/ARCHITECTURE.md' in out)
    check('STATUS fica', 'STATUS.md' not in out)
    check('spec de fase fica', 'docs/specs/f.md' not in out)
    check('histórico de artefato fica', 'docs/artefatos/historico/v1.html' not in out)
    check('sem recusa', not problems, problems)
    shutil.rmtree(root)


def test_private_block():
    print('\nbloco privado')
    text = 'antes\n<!-- privado:inicio -->\nsegredo X:' + '\\bks-harness\n<!-- privado:fim -->\ndepois\n'
    root = source({'README.md': text, 'skills/b.md': '<!-- privado:inicio -->\nsem fim\n'})
    out, problems = publish.build(root, ['README.md'])
    readme = out['README.md'].decode('utf-8')
    check('bloco removido', 'segredo' not in readme and 'antes\ndepois' in readme, readme)
    check('caminho dentro do bloco não é recusado', not problems, problems)
    out, problems = publish.build(root, ['skills/b.md'])
    check('marcador desbalanceado recusa', any('desbalanceado' in p for p in problems), problems)
    shutil.rmtree(root)


def test_leaks():
    print('\nrecusas')
    cases = {
        'drive X': ('skills/a.md', 'veja X:' + '\\bks-harness\\STATUS.md', True),
        'pasta do usuário': ('skills/b.md', 'C:/Users/' + 'fabio/.claude', True),
        'vault do autor': ('skills/c.md', 'D:\\' + '2brains\\repos', True),
        'e-mail pessoal': ('skills/d.md', 'autor: alguem@' + 'gmail.com', True),
        'e-mail noreply': ('skills/e.md', '1+a@users.noreply.github.com', False),
        'caminho de exemplo': ('skills/f.md', 'clone em C:\\dev\\bks-harness', False),
        'caminho de teste': ('hooks/tests/t.py', "w('C:/x/src/A.cs')", False),
    }
    for name, (rel, text, refused) in cases.items():
        root = source({rel: text})
        _, problems = publish.build(root, [rel])
        check('%s %s' % (name, 'recusa' if refused else 'passa'), bool(problems) == refused, problems)
        shutil.rmtree(root)


def test_sync():
    print('\nsincronização')
    dest = tempfile.mkdtemp()
    write(dest, '.git/HEAD', 'ref')
    write(dest, 'velho/arquivo.md', 'x')
    write(dest, 'README.md', 'antigo')
    written, removed = publish.sync({'README.md': b'novo', 'skills/a.md': b'a'}, dest)
    check('arquivo fora da lista é removido', 'velho/arquivo.md' in removed)
    check('pasta vazia some', not os.path.exists(os.path.join(dest, 'velho')))
    check('.git preservado', os.path.isfile(os.path.join(dest, '.git', 'HEAD')))
    check('arquivo alterado é regravado', 'README.md' in written)
    written, _ = publish.sync({'README.md': b'novo', 'skills/a.md': b'a'}, dest)
    check('segunda rodada não regrava', written == [], written)
    shutil.rmtree(dest)


def test_destination():
    print('\ndestino')
    check('destino igual à origem recusa', publish.main([publish.ROOT]) == 2)
    plain = tempfile.mkdtemp()
    check('destino sem .git recusa', publish.main([plain]) == 2)
    shutil.rmtree(plain)


def main():
    print('testes do publish.py')
    for fn in (test_allowlist, test_private_block, test_leaks, test_sync, test_destination):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
