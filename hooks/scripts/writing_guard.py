"""Guarda: padrão de escrita da skill bks-writing em documentação viva.

Como hook PostToolUse, devolve ao agente os achados do trecho escrito e lembra o usuário de rodar
o /bkhar:review. Como linha de comando, confere arquivos inteiros e sai com 1 se houver achado:
    python writing_guard.py [--max-palavras 40] [--resumo] arquivo.md [...]
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import read_payload, target_path, tool_input

MAX_WORDS = 40

OUT_OF_SCOPE_NAMES = {'status.md', 'journal.md', 'claude.md', 'agents.md', 'memory.md',
                      'skill.md', 'changelog.md'}
OUT_OF_SCOPE_DIRS = {'decisions', '.claude', 'memory', 'commands', 'agents', 'skills', 'templates',
                     'evals', 'third-party', 'node_modules', 'results', '.git', '.bks'}
OUT_OF_SCOPE_DOCS_DIRS = {'history', 'prompts', 'input'}

CRUTCHES = [
    (r'vale (ressaltar|destacar|lembrar)', 'enchimento'),
    (r'é importante (notar|ressaltar|destacar|lembrar)', 'enchimento'),
    (r'cabe (destacar|ressaltar|lembrar)', 'enchimento'),
    (r'com o objetivo de', 'enchimento'),
    (r'de forma a(?!\w)', 'enchimento'),
    (r'visando', 'enchimento'),
    (r'no que (tange|diz respeito)', 'enchimento'),
    (r'a nível de', 'enchimento'),
    (r'devido ao fato de', 'enchimento'),
    (r'sendo que', 'enchimento'),
    (r'atualmente', 'enchimento'),
    (r'neste momento', 'enchimento'),
    (r'robust[oa]s?(?!\w)', 'ênfase'),
    (r'poderos[oa]s?(?!\w)', 'ênfase'),
    (r'elegantes?(?!\w)', 'ênfase'),
    (r'crucia(l|is)(?!\w)', 'ênfase'),
    (r'de forma transparente', 'ênfase'),
    (r'sem esforço', 'ênfase'),
    (r'eventualmente', 'hesitação'),
    (r'ademais', 'transição'),
    (r'em suma', 'transição'),
    (r'recomenda-se', 'atribuição vaga'),
    (r'sabe-se que', 'atribuição vaga'),
    (r'(realiz|efetu)(a|am|ar|ando|ou) (a|o|as|os) ', 'nominalização'),
    (r'atua(m)? como', 'verbo simples'),
    (r'possu(i|em)(?!\w)', 'verbo simples'),
]
CRUTCHES = [(re.compile(r'(?i)(?<!\w)' + p), rule) for p, rule in CRUTCHES]

EMOJI = re.compile('[\U0001F300-\U0001FAFF]|[☀-➿]')
ADR = re.compile(r'ADR-\d+')
ACRONYM = re.compile(r'(?<![\w-])[A-Z][A-Z0-9]{1,5}(?![\w-])')
CODE_SPAN = re.compile(r'`[^`]*`')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
FENCE = re.compile(r'^\s*(```|~~~)')
IGNORE_OPEN = re.compile(r'<!--\s*(bks-escrita|conferir-escrita):\s*ignorar\s*-->')
IGNORE_CLOSE = re.compile(r'<!--\s*/(bks-escrita|conferir-escrita)\s*-->')
NOTE_START = re.compile(r'^\s*(>\s*)+\*Decis[aã]o:')
QUOTE = re.compile(r'^\s*(>\s*)+')
LIST_ITEM = re.compile(r'^\s*([-*]|\d+\.)\s+')
NOT_PROSE = re.compile(r'^\s*(\||#|---|\*\*\*|<)')
SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\**\s+(?=[A-ZÀ-Ú"*(])')


def in_scope(path):
    if not path.lower().endswith('.md'):
        return False
    parts = [p.lower() for p in re.split(r'[\\/]+', path) if p]
    name = parts[-1] if parts else ''
    if name in OUT_OF_SCOPE_NAMES or name.startswith('context') or name.startswith('adr-'):
        return False
    dirs = parts[:-1]
    if OUT_OF_SCOPE_DIRS & set(dirs):
        return False
    for i, d in enumerate(dirs[:-1]):
        if d == 'docs' and dirs[i + 1] in OUT_OF_SCOPE_DOCS_DIRS:
            return False
    return True


def read_acronyms(path):
    found = set()
    if os.path.isfile(path):
        with io.open(path, encoding='utf-8') as fh:
            for line in fh:
                s = line.strip()
                if s and not s.startswith('#'):
                    found.add(s)
    return found


def known_acronyms(doc_path):
    """Lista do kit mais a do repositório do documento, em .bks/siglas-conhecidas.txt."""
    known = read_acronyms(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'siglas-conhecidas.txt'))
    d = os.path.dirname(os.path.abspath(doc_path))
    while True:
        known |= read_acronyms(os.path.join(d, '.bks', 'siglas-conhecidas.txt'))
        if os.path.isdir(os.path.join(d, '.git')):
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return known


def prose_lines(lines):
    """(número, texto) das linhas fora de frontmatter, código cercado e região ignorada."""
    in_code = in_front = ignoring = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            in_front = True
            continue
        if in_front:
            if line.strip() == '---':
                in_front = False
            continue
        if FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        if IGNORE_OPEN.search(line):
            ignoring = True
            continue
        if IGNORE_CLOSE.search(line):
            ignoring = False
            continue
        if ignoring:
            continue
        yield i + 1, line


def analyze(text, known, max_words=MAX_WORDS):
    """Lista de (linha, regra, trecho) do documento inteiro."""
    findings = []
    defined = set()
    paragraph = []
    note = None

    def add(n, rule, excerpt):
        t = excerpt.strip()
        findings.append((n, rule, t if len(t) <= 110 else t[:107] + '...'))

    def close_paragraph():
        if not paragraph:
            return
        joined = ' '.join(t for _, t in paragraph)
        joined = LINK.sub(r'\1', CODE_SPAN.sub('X', joined))
        for sentence in SENTENCE_SPLIT.split(joined):
            words = len([w for w in sentence.split() if re.search(r'\w', w)])
            if words > max_words:
                add(paragraph[0][0], 'frase com %d palavras' % words, sentence)
        del paragraph[:]

    for n, line in prose_lines(text.splitlines()):
        if NOTE_START.match(line):
            note = [n, '']
        if note is not None:
            note[1] += ' ' + QUOTE.sub('', line)
            if line.rstrip().endswith('*'):
                synthesis = re.sub(r'\*?Decis[aã]o:', '', note[1])
                synthesis = re.sub(r'\(ADR-\d+[^)]*\)', '', synthesis)
                synthesis = re.sub(r'[*.\s]+', ' ', synthesis)
                if len(synthesis.split()) < 4:
                    add(note[0], 'nota de decisão sem síntese', note[1])
                note = None
            continue

        bare = CODE_SPAN.sub('', line)
        for _ in ADR.finditer(bare):
            add(n, 'ADR fora da nota de decisão', line)
        if EMOJI.search(line):
            add(n, 'emoji ou marca de severidade', line)
        for rx, rule in CRUTCHES:
            if rx.search(bare):
                add(n, 'muleta: ' + rule, line)
        for m in ACRONYM.finditer(bare):
            s = m.group(0)
            if s in known or s in defined:
                continue
            defined.add(s)
            if not re.search(r'\b%s\s*\(|\(\s*%s\b' % (s, s), bare):
                add(n, 'sigla sem definição: ' + s, line)

        is_prose = bool(line.strip()) and not NOT_PROSE.match(line)
        if is_prose:
            paragraph.append((n, LIST_ITEM.sub('', QUOTE.sub('', line))))
        if not is_prose or LIST_ITEM.match(line):
            close_paragraph()
    close_paragraph()
    return findings


def written_ranges(payload, text):
    """Faixas de linha (início, fim) que este tool call escreveu; None quando foi o arquivo todo."""
    ti = tool_input(payload)
    if 'content' in ti:
        return None
    pieces = [ti.get('new_string') or '']
    if isinstance(ti.get('edits'), list):
        pieces = [e.get('new_string') or '' for e in ti['edits'] if isinstance(e, dict)]
    ranges = []
    for piece in pieces:
        idx = text.find(piece) if piece else -1
        if idx < 0:
            continue
        start = text.count('\n', 0, idx) + 1
        ranges.append((start, start + piece.count('\n')))
    return ranges


def hook(payload):
    path = target_path(payload)
    if not in_scope(path) or not os.path.isfile(path):
        return
    with io.open(path, encoding='utf-8') as fh:
        text = fh.read()
    findings = analyze(text, known_acronyms(path))
    ranges = written_ranges(payload, text)
    if ranges is not None:
        findings = [f for f in findings if any(a <= f[0] <= b for a, b in ranges)]

    name = os.path.basename(path)
    reminder = ('bks-writing: documentação viva alterada em %s. Rode /bkhar:review antes de fechar; '
                'ele confere o padrão de escrita.' % name)
    out = {'systemMessage': reminder}
    if findings:
        lines = ['%s:%d  [%s]  %s' % (name, n, rule, t) for n, rule, t in findings]
        out['systemMessage'] = reminder + ' %d achado(s) devolvido(s) ao agente.' % len(findings)
        out['decision'] = 'block'
        out['reason'] = ('O trecho escrito fere o padrão da skill bks-writing. Corrija na mesma '
                         'passada:\n\n' + '\n'.join(lines))
    json.dump(out, sys.stdout, ensure_ascii=False)


def cli(argv):
    max_words, summary, files = MAX_WORDS, False, []
    it = iter(argv)
    for a in it:
        if a == '--max-palavras':
            max_words = int(next(it))
        elif a == '--resumo':
            summary = True
        else:
            files.append(a)
    total = []
    for f in files:
        with io.open(f, encoding='utf-8-sig') as fh:
            for n, rule, t in analyze(fh.read(), known_acronyms(f), max_words):
                total.append((f, n, rule, t))
    if summary:
        counts = {}
        for f, _, rule, _ in total:
            key = (f, re.sub(r'frase com \d+ palavras', 'frase longa', rule.split(':')[0]))
            counts[key] = counts.get(key, 0) + 1
        for (f, rule), c in sorted(counts.items(), key=lambda kv: -kv[1]):
            print('%5d  %s  %s' % (c, f, rule))
    else:
        for f, n, rule, t in total:
            print('%s:%d  [%s]  %s' % (f, n, rule, t))
    print('%d achado(s) em %d arquivo(s).' % (len(total), len(files)))
    return 1 if total else 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if len(sys.argv) > 1:
        sys.exit(cli(sys.argv[1:]))
    try:
        hook(read_payload())
    except Exception:
        pass
    sys.exit(0)
