"""Deriva do STATUS.md: data declarada anterior ao último commit ou à última entrada do JOURNAL.md."""
import os
import re
import subprocess

STATUS_DATE = re.compile(r'[ÚU]ltima atualiza[çc][ãa]o:\s*(\d{4}-\d{2}-\d{2})')
JOURNAL_DATE = re.compile(r'^## (\d{4}-\d{2}-\d{2})', re.M)


def _read(path):
    try:
        with open(path, encoding='utf-8') as fh:
            return fh.read()
    except Exception:
        return ''


def status_date(cwd):
    m = STATUS_DATE.search(_read(os.path.join(cwd, 'STATUS.md')))
    return m.group(1) if m else ''


def journal_date(cwd):
    m = JOURNAL_DATE.search(_read(os.path.join(cwd, 'JOURNAL.md')))
    return m.group(1) if m else ''


def commit_dates(cwd):
    """Datas dos commits que tocam esta pasta, do mais recente ao mais antigo."""
    try:
        r = subprocess.run(['git', 'log', '--format=%cs', '-n', '500', '--', '.'],
                           cwd=cwd, capture_output=True, text=True, timeout=5)
    except Exception:
        return []
    if r.returncode != 0:
        return []
    return [d for d in r.stdout.split() if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d)]


def check(cwd):
    """Devolve (contexto, mensagem) quando há deriva; (None, None) caso contrário."""
    declared = status_date(cwd)
    if not declared:
        return None, None

    findings = []
    later = [d for d in commit_dates(cwd) if d > declared]
    if later:
        findings.append('%d commits depois dela (o último em %s)' % (len(later), later[0]))
    journal = journal_date(cwd)
    if journal > declared:
        findings.append('entrada do JOURNAL.md em %s' % journal)
    if not findings:
        return None, None

    summary = 'STATUS.md declara %s; há %s.' % (declared, ' e '.join(findings))
    context = ('## Deriva do STATUS.md\n\n' + summary + '\n\nO STATUS.md pode não descrever o '
               'estado atual. Diga isso ao usuário e ofereça atualizá-lo; não atualize sozinho.')
    return context, 'Deriva: ' + summary
