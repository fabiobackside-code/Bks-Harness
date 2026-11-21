"""Guarda: recusa ler ou tocar arquivo de segredo, gravar segredo, apagar em massa, escrever fora do permitido
e git reset --hard fora da branch da task.

Vale para qualquer papel. O Bash e o PowerShell são lidos por token, não por parser:
o comando que menciona um arquivo sensível é recusado, qualquer que seja o verbo.
A linha com a marca bkhar-allow-secret fica fora da busca de segredo gravado.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, tool_input, written_content

PATH_TOOLS = ('Read', 'Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'Commit')
WRITE_TOOLS = ('Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'Commit')
SHELL_TOOLS = ('Bash', 'PowerShell')
ALLOW_MARK = 'bkhar-allow-secret'

ENV_SAFE = ('example', 'sample', 'template', 'dist')
KEY_EXT = ('.pem', '.key', '.pfx', '.p12', '.jks', '.keystore')
SSH_KEY = re.compile(r'^id_(rsa|dsa|ecdsa|ed25519)$')
CONFIG_EXT = ('.json', '.yml', '.yaml', '.config', '.ini', '.env', '.properties', '.xml', '.toml', '.conf')

TOKEN_PATTERNS = (
    ('chave privada', re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----')),
    ('chave de acesso AWS', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('token do GitHub', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{36,}\b')),
    ('chave da Anthropic', re.compile(r'\bsk-ant-[A-Za-z0-9_-]{20,}')),
)
CONN_STRING = re.compile(r'(?i)\b(?:password|pwd)=([^;"\'\s]+);')
CONFIG_SECRET = re.compile(
    r'(?i)["\']?\b(?:password|passwd|pwd|secret|api[_-]?key|client[_-]?secret|token)\b["\']?\s*[:=]\s*["\']?([^"\'\s,;}]*)')
PLACEHOLDER = re.compile(r'^(?:\$|\{|<|%|\*+$|x+$|changeme$|null$|none$|true$|false$)', re.I)
ENV_NAME = re.compile(r'^[A-Z][A-Z0-9_]+$')
SETTINGS = re.compile(r'^settings(\.[a-z]+)?\.json$')

RM_COMMANDS = ('rm', 'remove-item', 'ri', 'del', 'rd', 'rmdir', 'erase')
SEGMENT_SPLIT = re.compile(r'&&|\|\||[;|&\n]')
SHELL_TOKEN = re.compile(r'"[^"]*"|\'[^\']*\'|\S+')
MENTION_SPLIT = re.compile(r'[\s\'"`;|&<>()=,]+')
DRIVE_ROOT = re.compile(r'^[A-Za-z]:[\\/]?$')
MSYS_DRIVE = re.compile(r'^/([A-Za-z])(/|$)')

MESSAGE = ('Bloqueado pelo guarda de segredo: {why}.\n\n'
           'Arquivo de segredo (.env, chave, certificado) não é lido nem editado pelo agente; '
           'use o .env.example como modelo. Valor real de credencial vai para variável de ambiente '
           'ou cofre, nunca para o arquivo. Fixture de teste com segredo falso leva a marca '
           + ALLOW_MARK + ' na própria linha.')
TASK_BRANCH = re.compile(r'^(task/T-\d+|wave/\d+/T-\d+)$')
RESET_MESSAGE = ('Bloqueado pelo guarda: git reset --hard na branch %s.\n\n'
                 'O reset --hard só vale na branch da task (task/T-NNN ou wave/N/T-NNN), onde os '
                 'portões são commits e as tentativas são fotos. Para voltar a um ponto da task, '
                 'use /bkhar:loop T-NNN --resume.')


def basename(path):
    return re.split(r'[\\/]', path.rstrip('\\/'))[-1]


def is_sensitive(path):
    name = basename(str(path)).lower()
    if not name:
        return False
    if name == '.env' or name.endswith('.env'):
        return True
    if name.startswith('.env.'):
        return name[5:] not in ENV_SAFE
    if SSH_KEY.match(name):
        return True
    return name.endswith(KEY_EXT)


def native(path):
    path = os.path.expandvars(os.path.expanduser(str(path)))
    if os.name == 'nt':
        path = MSYS_DRIVE.sub(lambda m: m.group(1).upper() + ':/', path)
    return path


def resolve(path, cwd):
    path = native(path)
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    return os.path.normcase(os.path.realpath(path))


def inside(path, root):
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


def config_dirs(cwd):
    dirs = [os.path.join(os.path.expanduser('~'), '.claude')]
    if os.environ.get('CLAUDE_CONFIG_DIR'):
        dirs.append(os.environ['CLAUDE_CONFIG_DIR'])
    return [resolve(d, cwd or os.getcwd()) for d in dirs]


def protected_config(target, cwd):
    for root in config_dirs(cwd):
        if not inside(target, root):
            continue
        rest = os.path.relpath(target, root).replace(os.sep, '/').lower()
        if SETTINGS.match(rest) or rest == 'plugins' or rest.startswith('plugins/'):
            return True
    return False


def broad(root):
    home = resolve(os.path.expanduser('~'), root)
    return os.path.dirname(root) == root or root == home


def allowed_roots(cwd):
    roots = [resolve(r, cwd) for r in [cwd, tempfile.gettempdir()]
             + [os.environ[v] for v in ('TMP', 'TEMP', 'TMPDIR') if os.environ.get(v)]]
    roots += config_dirs(cwd)
    extra = [r for r in (os.environ.get('BKHAR_WRITE_ROOTS') or '').split(os.pathsep) if r.strip()]
    roots += [r for r in (resolve(e.strip(), cwd) for e in extra) if not broad(r)]
    return roots


def secret_in(content, path):
    is_config = basename(path).lower().endswith(CONFIG_EXT)
    for line in content.splitlines():
        if ALLOW_MARK in line:
            continue
        for label, pattern in TOKEN_PATTERNS:
            if pattern.search(line):
                return label
        for m in CONN_STRING.finditer(line):
            if not PLACEHOLDER.match(m.group(1)):
                return 'senha em connection string'
        if is_config:
            for m in CONFIG_SECRET.finditer(line):
                value = m.group(1)
                if value and not PLACEHOLDER.match(value) and not ENV_NAME.match(value):
                    return 'credencial em arquivo de configuração'
    return None


def mass_delete_target(command, cwd):
    for segment in SEGMENT_SPLIT.split(command):
        tokens = [t.strip('"\'') for t in SHELL_TOKEN.findall(segment)]
        if not tokens or tokens[0].lower() not in RM_COMMANDS:
            continue
        flags = [t for t in tokens[1:] if t.startswith('-')]
        targets = [t for t in tokens[1:] if not t.startswith('-')]
        recursive = any(f in ('-r', '-R', '--recursive') or f.lower().startswith('-rec')
                        or re.match(r'^-[a-zA-Z]*[rR][a-zA-Z]*$', f) for f in flags)
        if not recursive:
            continue
        for target in targets:
            if dangerous_target(target, cwd):
                return target
    return None


def dangerous_target(target, cwd):
    if target in ('/', '/*', '*', '.', './', '..') or DRIVE_ROOT.match(target):
        return True
    if target.startswith(('~', '$HOME', '${HOME}', '$env:USERPROFILE', '..')):
        return True
    if not cwd:
        return os.path.isabs(native(target))
    return not inside(resolve(target, cwd), resolve(cwd, cwd))


def git_branch(path):
    try:
        r = subprocess.run(['git', '-C', path, 'branch', '--show-current'], capture_output=True,
                           text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def hard_reset_branch(command, cwd):
    for segment in SEGMENT_SPLIT.split(command):
        tokens = [t.strip('"\'') for t in SHELL_TOKEN.findall(segment)]
        if not tokens or tokens[0].lower() not in ('git', 'git.exe'):
            continue
        if 'reset' not in tokens or '--hard' not in tokens:
            continue
        where = cwd or os.getcwd()
        if '-C' in tokens[:-1]:
            where = resolve(tokens[tokens.index('-C') + 1], where)
        branch = git_branch(where)
        if branch is not None and not TASK_BRANCH.match(branch):
            return branch or 'HEAD solto'
    return None


def check(payload):
    name = payload.get('tool_name') or ''
    ti = tool_input(payload)
    cwd = payload.get('cwd') or ''

    if name in SHELL_TOOLS:
        command = ti.get('command') or ''
        for token in MENTION_SPLIT.split(command):
            if is_sensitive(token):
                deny(MESSAGE.format(why='o comando menciona o arquivo sensível %s' % token))
        target = mass_delete_target(command, cwd)
        if target:
            deny(MESSAGE.format(why='remoção recursiva de %s, fora do projeto ou na raiz' % target))
        branch = hard_reset_branch(command, cwd)
        if branch:
            deny(RESET_MESSAGE % branch)
        return

    if name == 'Grep':
        for key in ('path', 'glob'):
            if is_sensitive(ti.get(key) or ''):
                deny(MESSAGE.format(why='busca em arquivo sensível (%s)' % ti.get(key)))
        return

    if name not in PATH_TOOLS:
        return
    path = ti.get('file_path') or ti.get('notebook_path') or ''
    if is_sensitive(path):
        where = 'arquivo sensível no commit' if name == 'Commit' else '%s em arquivo sensível' % name
        deny(MESSAGE.format(why='%s (%s)' % (where, basename(path))))
    if name not in WRITE_TOOLS:
        return
    found = secret_in(written_content(payload), path)
    if found:
        deny(MESSAGE.format(why='%s no conteúdo gravado em %s' % (found, basename(path))))
    if path and protected_config(resolve(path, cwd or os.getcwd()), cwd):
        deny(MESSAGE.format(why='configuração do Claude Code (%s) se edita à mão' % path))
    if cwd and path:
        target = resolve(path, cwd)
        if not any(inside(target, root) for root in allowed_roots(cwd)):
            deny(MESSAGE.format(why='escrita fora do projeto e das raízes permitidas (%s); '
                                    'raiz extra vai em BKHAR_WRITE_ROOTS' % path))


if __name__ == '__main__':
    guard(check)
