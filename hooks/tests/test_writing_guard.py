import io, json, os, shutil, subprocess, sys, tempfile
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
H = os.path.join('hooks', 'scripts', 'writing_guard.py')

TMP = tempfile.mkdtemp()
os.makedirs(os.path.join(TMP, '.git'))
os.makedirs(os.path.join(TMP, 'docs', 'prompts'))


def put(rel, text):
    path = os.path.join(TMP, rel)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return path


def hook(payload):
    r = subprocess.run([sys.executable, H], input=json.dumps(payload),
                       capture_output=True, text=True, encoding='utf-8', timeout=20)
    return json.loads(r.stdout) if r.stdout.strip() else {}


def write(rel, text):
    return hook({'tool_name': 'Write', 'tool_input': {'file_path': put(rel, text), 'content': text}})


def edit(rel, text, new):
    return hook({'tool_name': 'Edit', 'tool_input': {'file_path': put(rel, text), 'new_string': new}})


def cli(*paths):
    return subprocess.run([sys.executable, H] + list(paths), capture_output=True,
                          text=True, encoding='utf-8', timeout=20).returncode


LONG = ' '.join(['palavra'] * 45) + '.'
NOTE_OK = 'O serviço não guarda cache.\n\n> *Decisão: nenhum serviço mantém cache em memória (ADR-012).*\n'
IGNORED = '<!-- bks-escrita: ignorar -->\nSem cache [ADR-012].\n<!-- /bks-escrita -->\n'
LEGACY = 'Legado com ADR-001 no corpo.\n\n'

cases = [
 ('ADR no corpo bloqueia', write('ARCHITECTURE.md', 'Sem cache [ADR-012].\n'), 'block', 'ADR fora'),
 ('nota de decisão passa', write('ARCHITECTURE.md', NOTE_OK), None, None),
 ('nota sem síntese bloqueia', write('README.md', '> *Decisão: ver ADR-021.*\n'), 'block', 'sem síntese'),
 ('frase de 45 palavras bloqueia', write('README.md', LONG + '\n'), 'block', '45 palavras'),
 ('muleta bloqueia', write('README.md', 'O serviço realiza a validação da entrada.\n'), 'block', 'nominalização'),
 ('emoji bloqueia', write('README.md', 'Cuidado \U0001F534 aqui.\n'), 'block', 'emoji'),
 ('sigla sem definição bloqueia', write('README.md', 'O TXC carrega o contexto.\n'), 'block', 'TXC'),
 ('sigla definida passa', write('README.md', 'O contexto de transação (TXC) segue junto.\n'), None, None),
 ('sigla conhecida passa', write('README.md', 'A API devolve JSON.\n'), None, None),
 ('região ignorada passa', write('README.md', IGNORED), None, None),
 ('código cercado passa', write('README.md', '```\nSem cache [ADR-012].\n```\n'), None, None),
 ('Edit confere só o trecho novo', edit('ARCHITECTURE.md', LEGACY + 'Trecho novo e limpo.\n', 'Trecho novo e limpo.'), None, None),
 ('Edit com achado bloqueia', edit('ARCHITECTURE.md', LEGACY + 'Novo com ADR-002.\n', 'Novo com ADR-002.'), 'block', 'ADR fora'),
]

fail = 0
for name, out, expect, needle in cases:
    got = out.get('decision')
    ok = got == expect and (needle is None or needle in out.get('reason', ''))
    ok = ok and '/bkhar:review' in out.get('systemMessage', '')
    fail += (not ok)
    print('%-4s %-34s esperado=%-6s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

scope = [
 ('STATUS.md fora do alcance', write('STATUS.md', 'Sem cache [ADR-012].\n')),
 ('docs/prompts fora do alcance', write(os.path.join('docs', 'prompts', 'p.md'), 'ADR-012.\n')),
 ('ADR-003.md fora do alcance', write('ADR-003.md', 'Ver ADR-002.\n')),
 ('código-fonte fora do alcance', hook({'tool_name': 'Write', 'tool_input': {'file_path': put('A.cs', '//'), 'content': '//'}})),
]
for name, out in scope:
    ok = out == {}
    fail += (not ok)
    print('%-4s %-34s esperado=silêncio obtido=%s' % ('OK' if ok else 'FALHA', name, out or 'silêncio'))

os.makedirs(os.path.join(TMP, '.bks'))
put(os.path.join('.bks', 'siglas-conhecidas.txt'), 'TXC\n')
for name, path, expect in [
    ('CLI sai 1 com achado', put('a.md', 'Sem cache [ADR-012].\n'), 1),
    ('CLI sai 0 limpo', put('b.md', NOTE_OK), 0),
    ('CLI lê siglas do projeto', put('c.md', 'O TXC carrega o contexto.\n'), 0),
]:
    got = cli(path)
    ok = got == expect
    fail += (not ok)
    print('%-4s %-34s esperado=%-6s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))

shutil.rmtree(TMP, ignore_errors=True)
print('\nfalhas:', fail)
sys.exit(1 if fail else 0)
