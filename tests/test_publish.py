"""Testes do scripts/publish.py: o que sai, o que é recusado, o que é removido do clone.

Uso: python tests/test_publish.py
"""
import importlib.util
import io
import os
import shutil
import subprocess
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
                   'docs/ARCHITECTURE.md': 'x', 'docs/artefatos/historico/v1.html': 'x',
                   'docs/artefatos/treinamento/t.md': 'x',
                   'bin/bkhar.cmd': 'x', 'providers/deepseek.json': 'x', 'requirements.txt': 'x'})
    out, problems = publish.build(root, ['skills/a/SKILL.md', 'STATUS.md', 'docs/specs/f.md',
                                         'docs/ARCHITECTURE.md', 'docs/artefatos/historico/v1.html',
                                         'docs/artefatos/treinamento/t.md',
                                         'bin/bkhar.cmd', 'providers/deepseek.json', 'requirements.txt'])
    check('skill sai', 'skills/a/SKILL.md' in out)
    check('ARCHITECTURE sai', 'docs/ARCHITECTURE.md' in out)
    check('manual de treinamento sai', 'docs/artefatos/treinamento/t.md' in out)
    check('lançador sai', 'bin/bkhar.cmd' in out)
    check('definição de provedor sai', 'providers/deepseek.json' in out)
    check('requirements sai', 'requirements.txt' in out)
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
        'drive X com barra dupla de JSON': ('skills/g.json', '{"p": "X:' + '\\\\Claude\\\\skills"}', True),
        'pasta do autor em D': ('skills/h.md', 'D:\\' + 'Fabio\\BackSide\\SDD', True),
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


def gitc(repo, *args):
    return subprocess.run(['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@example.com'] + list(args),
                          capture_output=True, text=True)


def test_external_contribution():
    print('\ncontribuição externa')
    src = source({'skills/a.md': 'original\n', 'README.md': 'leia\n'})
    gitc(src, 'init', '-q')
    gitc(src, 'add', '-A')
    gitc(src, 'commit', '-q', '-m', 'base')
    dest = tempfile.mkdtemp()
    gitc(dest, 'init', '-q')
    check('clone sem manifesto não confere', publish.external_changes({}, dest) is None)
    out, _ = publish.build(src, ['skills/a.md', 'README.md'])
    check('manifesto sai junto', publish.MANIFEST in out)
    publish.sync(out, dest)
    gitc(dest, 'add', '-A')
    gitc(dest, 'commit', '-q', '-m', 'publicação')
    check('publicação recém-feita não acusa nada', publish.external_changes(out, dest) == [])

    write(dest, 'skills/a.md', 'original\nmelhoria de fora\n')
    write(dest, 'skills/b.md', 'arquivo novo de fora\n')
    gitc(dest, 'add', '-A')
    gitc(dest, 'commit', '-q', '-m', 'PR de fork')
    out, _ = publish.build(src, ['skills/a.md', 'README.md'])
    ext = publish.external_changes(out, dest)
    check('mudança e arquivo de fora acusados', ext == ['skills/a.md', 'skills/b.md'], ext)

    patch = os.path.join(src, 'outputs', 'publish', 'incoming.patch')
    check('incoming gera o patch', publish.incoming(dest, patch) == patch)
    with io.open(patch, encoding='utf-8') as fh:
        text = fh.read()
    check('patch traz a contribuição e não o manifesto',
          'melhoria de fora' in text and 'arquivo novo de fora' in text and publish.MANIFEST not in text)
    applied = gitc(src, 'apply', '--3way', patch)
    check('patch aplica no privado', applied.returncode == 0, applied.stderr)

    out, _ = publish.build(src, ['skills/a.md', 'skills/b.md', 'README.md'])
    check('contribuição trazida libera a publicação', publish.external_changes(out, dest) == [])
    publish.sync(out, dest)
    with io.open(os.path.join(dest, 'skills', 'a.md'), encoding='utf-8') as fh:
        check('contribuição sobrevive à publicação seguinte', 'melhoria de fora' in fh.read())
    check('arquivo novo de fora sobrevive', os.path.isfile(os.path.join(dest, 'skills', 'b.md')))

    write(dest, 'README.md', 'leia\r\n')
    check('CRLF do checkout não conta como mudança', publish.external_changes(out, dest) == [])
    os.remove(os.path.join(dest, 'README.md'))
    ext = publish.external_changes(out, dest)
    check('arquivo apagado no público acusado', ext == ['README.md (apagado no público)'], ext)
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dest, ignore_errors=True)


def test_tag_hint():
    print('\ntag por versão')
    src = source({'.claude-plugin/plugin.json': '{"version": "9.9.9"}'})
    dest = tempfile.mkdtemp()
    gitc(dest, 'init', '-q')
    gitc(dest, 'commit', '-q', '--allow-empty', '-m', 'x')
    check('sugere a tag da versão', 'git tag v9.9.9' in (publish.tag_hint(src, dest) or ''))
    gitc(dest, 'tag', 'v9.9.9')
    check('tag existente avisa', 'já existe' in (publish.tag_hint(src, dest) or ''))
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dest, ignore_errors=True)


def test_destination():
    print('\ndestino')
    check('destino igual à origem recusa', publish.main([publish.ROOT]) == 2)
    plain = tempfile.mkdtemp()
    check('destino sem .git recusa', publish.main([plain]) == 2)
    shutil.rmtree(plain)


def main():
    print('testes do publish.py')
    for fn in (test_allowlist, test_private_block, test_leaks, test_sync, test_external_contribution, test_tag_hint,
               test_destination):
        fn()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
