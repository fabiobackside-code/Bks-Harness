"""Guarda: no agente architect, o Bash só roda scripts do plugin, git de leitura e maestri ask.

Os outros agentes e a sessão principal passam direto. O agente vem do campo
agent_type do evento. A escrita do architect fica restrita a specs/, decisions/, docs/ e outputs/.
"""
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, tool_input

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GIT_READ = ('status', 'log', 'diff', 'show', 'rev-parse', 'ls-files', 'blame')
GIT_BEFORE = ('--no-pager',)
GIT_DENIED = ('--config-env', '--exec-path', '--git-dir', '--work-tree', '--output', '--ext-diff',
              '--textconv', '--upload-pack', '--open-files-in-pager')
GIT_SHORT_DENIED = ('-c', '-C', '-O')
WRITABLE = ('specs', 'decisions', 'docs', 'outputs')
PYTHON = ('python', 'python3', 'py')
MAESTRI = ('maestri', '$MAESTRI_CLI', '${MAESTRI_CLI}')
SCRIPT = re.compile(r'[\\/]scripts[\\/][a-z_]+\.py$')
WRITE_TOOLS = ('Write', 'Edit', 'MultiEdit', 'NotebookEdit')
BACKSLASH = chr(92)

MESSAGE = (
    'Bloqueado no architect: {why}.\n\n'
    'Neste papel o Bash serve a três usos: python dos scripts do plugin '
    '(${{CLAUDE_PLUGIN_ROOT}}/scripts/*.py), git só de leitura ({git}) e maestri ask '
    'para devolver o resultado ao manager. Um comando por chamada, sem encadear.\n\n'
    'Build, teste, instalação e commit são do developer e do tester: devolva o pedido ao Gerente.'
)


def is_architect(payload):
    kind = str(payload.get('agent_type') or '')
    return kind == 'architect' or kind.endswith(':architect')


def unsafe_syntax(command):
    """Construção de shell que o guarda não analisa; None quando o comando é simples."""
    if "$'" in command or '$"' in command:
        return 'aspas ANSI-C ou de tradução'
    single = double = False
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == "'" and not double:
            single = not single
        elif ch == '"' and not single:
            double = not double
        elif ch == BACKSLASH and not single:
            if not double:
                return 'barra invertida fora de aspas'
            i += 1
        elif not single and (ch == '`' or command.startswith('$(', i)):
            return 'substituição de comando'
        elif not single and not double and ch in ';&|<>\n#':
            return 'encadeamento, redirecionamento ou comentário (%r)' % ch
        i += 1
    if single or double:
        return 'aspas sem fechar'
    return None


def _script_inside_plugin(path):
    path = path.replace('${CLAUDE_PLUGIN_ROOT}', PLUGIN_ROOT).replace('$CLAUDE_PLUGIN_ROOT', PLUGIN_ROOT)
    if not SCRIPT.search(path):
        return False
    real = os.path.normcase(os.path.realpath(path))
    root = os.path.normcase(os.path.realpath(os.path.join(PLUGIN_ROOT, 'scripts')))
    return os.path.dirname(real) == root


def git_refusal(args):
    rest = list(args)
    while rest and rest[0] in GIT_BEFORE:
        rest = rest[1:]
    if not rest or rest[0] not in GIT_READ:
        return 'git %s não é leitura' % (rest[0] if rest else '(sem subcomando)')
    for token in rest[1:]:
        name = token.split('=', 1)[0]
        if name in GIT_DENIED or (not token.startswith('--') and token[:2] in GIT_SHORT_DENIED):
            return 'opção de git que executa ou escreve (%s)' % token
    return None


def refusal(command):
    """Motivo da recusa, ou None quando o comando cabe no papel."""
    why = unsafe_syntax(command)
    if why:
        return why
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return 'comando que não se lê'
    if not tokens:
        return 'comando vazio'
    head = tokens[0]
    if head in PYTHON:
        if len(tokens) > 1 and _script_inside_plugin(tokens[1]):
            return None
        return 'python fora dos scripts do plugin'
    if head == 'git':
        return git_refusal(tokens[1:])
    if head in MAESTRI:
        return None if len(tokens) > 1 and tokens[1] == 'ask' else 'maestri só com ask'
    return '%s não é um dos três usos' % head


def write_refusal(path, cwd):
    """Motivo da recusa da escrita, ou None quando o destino resolvido está numa pasta do papel."""
    if not path or not cwd:
        return 'destino ou diretório do projeto ausente'
    real = os.path.normcase(os.path.realpath(os.path.join(cwd, path)))
    project = os.path.normcase(os.path.realpath(cwd))
    for folder in WRITABLE:
        base = os.path.join(project, folder)
        if real == base or real.startswith(base + os.sep):
            return None
    return 'escrita fora de %s do projeto' % ', '.join(f + '/' for f in WRITABLE)


def check(payload):
    if not is_architect(payload):
        return
    tool = payload.get('tool_name')
    if tool in WRITE_TOOLS:
        ti = tool_input(payload)
        path = str(ti.get('file_path') or ti.get('notebook_path') or '')
        why = write_refusal(path, str(payload.get('cwd') or ''))
        if why:
            deny('Bloqueado no architect: %s (%s). Código, scripts e configuração não são deste papel.'
                 % (why, path))
        return
    if tool != 'Bash':
        return
    command = str(tool_input(payload).get('command') or '').strip()
    why = refusal(command)
    if why:
        deny(MESSAGE.format(why=why, git=', '.join(GIT_READ)))


guard(check)
