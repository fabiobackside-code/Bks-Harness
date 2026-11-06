#!/usr/bin/env python3
"""Aprendizado candidato: propõe, filtra dado sensível, leva ao vault, promove e rejeita. Sem modelo.

Uso:
  learning.py propose [REPO] --tipo correcao|aprendizado --regra TEXTO --evidencia TEXTO --origem TEXTO
  learning.py list [REPO]
  learning.py export [REPO] [--vault DIR]          padrão: BKS_VAULT
  learning.py promote [REPO] --arquivo F --escopo projeto|vault|kit [--vault DIR] [--kit DIR]
  learning.py reject [REPO] --arquivo F --motivo TEXTO
  learning.py scrub --texto TEXTO
"""
import argparse
import glob
import io
import os
import re
import shutil
import sys
import unicodedata
from datetime import date, datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

KINDS = ('correcao', 'aprendizado')
SCOPES = ('projeto', 'vault', 'kit')
KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SENSITIVE = (
    ('e-mail', re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')),
    ('CPF', re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b')),
    ('CNPJ', re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b')),
    ('cartão', re.compile(r'\b(?:\d[ -]?){13,19}\b')),
    ('chave de API', re.compile(r'\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}')),
    ('token do GitHub', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}')),
    ('chave da AWS', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('senha', re.compile(r'(?i)\b(?:password|senha|pwd|secret|token)\s*[=:]\s*\S+')),
    ('chave privada', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('JWT', re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}')),
)


class LearningError(Exception):
    """Operação recusada: nada foi escrito."""


def scrub(text):
    return ['%s: %s' % (name, m.group(0)[:12] + '…') for name, rx in SENSITIVE for m in rx.finditer(text or '')]


def _one_line(value):
    return ' '.join(str(value).split())


def _slug(text):
    s = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:48] or 'regra'


def meta(path):
    with io.open(path, encoding='utf-8') as fh:
        m = re.match(r'^---\n(.*?)\n---', fh.read(), re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(':')
        out[k.strip()] = v.strip()
    return out


def _body(path):
    with io.open(path, encoding='utf-8') as fh:
        return re.sub(r'^---\n.*?\n---\n?', '', fh.read(), count=1, flags=re.S)


def _write(path, fields, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    head = '\n'.join('%s: %s' % (k, _one_line(v)) for k, v in fields.items() if v is not None)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('---\n%s\n---\n%s' % (head, body))
    return path


def _free(path):
    base, ext = os.path.splitext(path)
    n, out = 2, path
    while os.path.exists(out):
        out = '%s-%d%s' % (base, n, ext)
        n += 1
    return out


def propose(repo, kind, rule, evidence, origem):
    if kind not in KINDS:
        raise LearningError('tipo %r; use %s' % (kind, ' ou '.join(KINDS)))
    if not _one_line(rule) or not _one_line(evidence) or not _one_line(origem):
        raise LearningError('proposta precisa de regra, evidência e origem')
    today = date.today().isoformat()
    path = _free(os.path.join(repo, 'inbox', 'proposals', '%s-%s.md' % (today, _slug(rule))))
    fields = {'tipo': kind, 'projeto': os.path.basename(os.path.abspath(repo)), 'status': 'candidata',
              'data': today, 'origem': origem, 'evidencia': evidence}
    return _write(path, fields, '\n# Regra proposta\n\n%s\n' % rule.strip())


def candidates(repo):
    return [p for p in sorted(glob.glob(os.path.join(repo, 'inbox', 'proposals', '*.md')))
            if meta(p).get('status') == 'candidata']


def export_to_vault(repo, vault):
    result = {'exportadas': [], 'recusadas': []}
    if not vault:
        return result
    project = os.path.basename(os.path.abspath(repo))
    for path in candidates(repo):
        m = meta(path)
        if m.get('exportado_em'):
            continue
        with io.open(path, encoding='utf-8') as fh:
            hits = scrub(fh.read())
        if hits:
            result['recusadas'].append({'arquivo': path, 'achados': hits})
            continue
        dest = _free(os.path.join(vault, 'inbox', 'proposals', '%s--%s' % (project, os.path.basename(path))))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(path, dest)
        m['exportado_em'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        _write(path, m, _body(path))
        result['exportadas'].append(path)
    return result


def promote(repo, path, scope, vault=None, kit=None):
    if scope not in SCOPES:
        raise LearningError('escopo %r; use %s' % (scope, ', '.join(SCOPES)))
    if not os.path.isfile(path):
        raise LearningError('proposta %s não existe' % path)
    if scope == 'vault' and not vault:
        raise LearningError('promover ao vault pede BKS_VAULT ou --vault')
    m = meta(path)
    with io.open(path, encoding='utf-8') as fh:
        hits = scrub(fh.read()) if scope != 'projeto' else []
    if hits:
        raise LearningError('dado sensível na proposta: %s' % '; '.join(hits))
    name = os.path.basename(path)
    if scope == 'projeto':
        dest, status = os.path.join(repo, 'brain', 'engineering', 'regras', name), 'promovida'
    elif scope == 'vault':
        dest, status = os.path.join(vault, 'workbench', 'regras', name), 'promovida'
    else:
        dest, status = os.path.join(kit or KIT_ROOT, 'inbox', 'proposals', '%s--%s' % (m.get('projeto', 'p'), name)), 'para-eval'
    m.update(status=status, promovida_em=date.today().isoformat(), escopo=scope)
    dest = _write(_free(dest), m, _body(path))
    os.remove(path)
    return dest


def reject(repo, path, reason):
    if not _one_line(reason):
        raise LearningError('rejeição precisa de motivo')
    m = meta(path)
    m.update(status='rejeitada', motivo=reason, rejeitada_em=date.today().isoformat())
    dest = _write(_free(os.path.join(repo, 'archive', 'proposals', os.path.basename(path))), m, _body(path))
    os.remove(path)
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(description='aprendizado candidato do bkhar')
    ap.add_argument('cmd', choices=('propose', 'list', 'export', 'promote', 'reject', 'scrub'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    for flag in ('--tipo', '--regra', '--evidencia', '--origem', '--arquivo', '--escopo', '--vault',
                 '--kit', '--motivo', '--texto'):
        ap.add_argument(flag)
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    try:
        if a.cmd == 'propose':
            print(propose(repo, a.tipo, a.regra, a.evidencia, a.origem))
        elif a.cmd == 'list':
            for p in candidates(repo):
                print('%s  %s' % (os.path.basename(p), meta(p).get('origem', '')))
        elif a.cmd == 'export':
            r = export_to_vault(repo, a.vault or os.environ.get('BKS_VAULT'))
            print('exportadas: %d' % len(r['exportadas']))
            for x in r['recusadas']:
                print('recusada: %s — %s' % (os.path.basename(x['arquivo']), '; '.join(x['achados'])))
        elif a.cmd == 'promote':
            print(promote(repo, a.arquivo, a.escopo, a.vault or os.environ.get('BKS_VAULT'), a.kit))
        elif a.cmd == 'reject':
            print(reject(repo, a.arquivo, a.motivo))
        elif a.cmd == 'scrub':
            hits = scrub(a.texto)
            print('\n'.join(hits) or 'limpo')
            return 1 if hits else 0
    except LearningError as exc:
        print('recusado: %s' % exc)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
