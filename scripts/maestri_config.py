#!/usr/bin/env python3
"""Ligação do projeto com o Maestri: bloco `maestri` do .bks-profile.json, validação dos terminais e rota por papel.

Uso:
  maestri_config.py show [REPO]
  maestri_config.py on [REPO] [--role papel=terminal ...] [--note nome] [--delegate comando=papel|executor|local ...]
  maestri_config.py off [REPO]
  maestri_config.py check [REPO]                   saída 1 quando falta terminal, nota ou nome
  maestri_config.py route [REPO] --role PAPEL      "terminal <nome>" ou "subagente: <motivo>"
  maestri_config.py delegate [REPO] --command CMD  "terminal <nome>" ou "local: <motivo>"
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROLES = ('architect', 'developer', 'tester', 'quality', 'security', 'scribe')
NO_BASH = ('quality', 'security', 'scribe')
DELEGABLE = ('arch', 'prd', 'plan', 'canonize', 'save', 'maintainability')
NEEDS_BASH = ('arch', 'plan', 'save')
DEFAULT = {'enabled': True, 'manager': 'manager', 'roles': {r: r for r in ROLES},
           'executors': {'ops': 'ops'}, 'notes': {'status': 'status'},
           'delegate': {'arch': 'architect', 'prd': 'architect', 'plan': 'architect',
                        'canonize': 'ops', 'save': 'ops', 'maintainability': 'ops'}}


class ConfigError(Exception):
    """Pedido recusado: o perfil não muda."""


def _profile_path(repo):
    return os.path.join(repo, '.bks-profile.json')


def _load_profile(repo):
    path = _profile_path(repo)
    if not os.path.isfile(path):
        raise ConfigError('.bks-profile.json não encontrado; rode na raiz do projeto')
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _save_profile(repo, profile):
    path = _profile_path(repo)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(profile, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    os.replace(tmp, path)


def load(repo):
    """Bloco `maestri` completo, com os padrões preenchidos, ou None quando o projeto não o tem."""
    if not os.path.isfile(_profile_path(repo)):
        return None
    block = _load_profile(repo).get('maestri')
    if block is None:
        return None
    merged = json.loads(json.dumps(DEFAULT))
    merged['enabled'] = bool(block.get('enabled', False))
    merged['manager'] = block.get('manager') or DEFAULT['manager']
    merged['roles'].update(block.get('roles') or {})
    if 'executors' in block:
        merged['executors'] = dict(block['executors'] or {})
    merged['notes'].update(block.get('notes') or {})
    if 'delegate' in block:
        merged['delegate'] = dict(block['delegate'] or {})
    return merged


def _target(block, slot):
    """Nome do terminal de um papel ou executor do mapa; None quando o nome não existe."""
    if slot in block['roles']:
        return block['roles'][slot]
    return block['executors'].get(slot)


def delegation_problems(block):
    problems = []
    for cmd, slot in sorted(block['delegate'].items()):
        if cmd not in DELEGABLE:
            problems.append('comando %r não é delegável; use %s' % (cmd, ', '.join(DELEGABLE)))
        elif _target(block, slot) is None:
            problems.append('/bkhar:%s delegado a %r, que não é papel nem executor' % (cmd, slot))
        elif cmd in NEEDS_BASH and slot in NO_BASH:
            problems.append('/bkhar:%s precisa de Bash e %s não tem; delegue a um executor' % (cmd, slot))
    return problems


def enabled(repo):
    block = load(repo)
    return bool(block and block['enabled'])


def turn_on(repo, roles=None, note=None, delegate=None):
    profile = _load_profile(repo)
    block = profile.get('maestri') or json.loads(json.dumps(DEFAULT))
    block['enabled'] = True
    for key in ('manager', 'roles', 'executors', 'notes', 'delegate'):
        block.setdefault(key, json.loads(json.dumps(DEFAULT[key])))
    for slot, terminal in (roles or {}).items():
        if not terminal.strip():
            raise ConfigError('%s sem nome de terminal' % slot)
        if slot in ROLES:
            block['roles'][slot] = terminal.strip()
        elif slot == 'manager':
            block['manager'] = terminal.strip()
        else:
            block['executors'][slot] = terminal.strip()
    if note:
        block['notes']['status'] = note
    for cmd, slot in (delegate or {}).items():
        if slot in ('', 'local'):
            block['delegate'].pop(cmd, None)
        else:
            block['delegate'][cmd] = slot
    trial = json.loads(json.dumps(DEFAULT))
    trial.update(block)
    problems = delegation_problems(trial)
    if problems:
        raise ConfigError('; '.join(problems))
    profile['maestri'] = block
    _save_profile(repo, profile)
    return load(repo)


def turn_off(repo):
    profile = _load_profile(repo)
    if 'maestri' not in profile:
        return None
    profile['maestri']['enabled'] = False
    _save_profile(repo, profile)
    return load(repo)


def parse_list(text):
    """Lê a saída de `maestri list`: o nome deste terminal, os agentes e as notas conectados."""
    found = {'me': None, 'agents': [], 'notes': []}
    section = None
    for raw in (text or '').splitlines():
        line = raw.strip()
        low = line.lower()
        if low.startswith('you:'):
            section = 'me'
        elif low.startswith('connected agents'):
            section = 'agents'
        elif low.startswith('connected notes'):
            section = 'notes'
        elif line.endswith(':') and not line.startswith('-'):
            section = None
        elif line.startswith('- name:') and section:
            name = line.split(':', 1)[1].strip().strip('"')
            if section == 'me':
                found['me'] = name
            else:
                found[section].append(name)
    return found


def in_maestri(env=None):
    return bool((env if env is not None else os.environ).get('MAESTRI_TERMINAL_ID'))


def list_output():
    cli = os.environ.get('MAESTRI_CLI') or shutil.which('maestri')
    if not cli:
        return None
    done = subprocess.run([cli, 'list'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return done.stdout if done.returncode == 0 else None


def check(repo, listing, env=None):
    """Problemas que impedem o despacho por terminal; lista vazia quando tudo bate."""
    block = load(repo)
    if not block:
        return ['projeto sem bloco maestri; rode /bkhar:maestri on']
    if not block['enabled']:
        return ['integração desligada (maestri.enabled = false)']
    if not in_maestri(env):
        return ['esta sessão não está num terminal do Maestri (MAESTRI_TERMINAL_ID ausente)']
    if listing is None:
        return ['maestri list não respondeu']
    seen = parse_list(listing)
    problems = []
    if seen['me'] != block['manager']:
        problems.append('este terminal chama-se %r; o perfil espera %r' % (seen['me'], block['manager']))
    connected = {a.lower(): a for a in seen['agents']}
    for role in ROLES:
        want = block['roles'][role]
        if want.lower() not in connected:
            problems.append('papel %s: terminal %r não está conectado a este' % (role, want))
    notes = {n.lower() for n in seen['notes']}
    if block['notes']['status'].lower() not in notes:
        problems.append('nota %r não está conectada; crie com: maestri note create --name "%s"'
                        % (block['notes']['status'], block['notes']['status']))
    for slot, want in sorted(block['executors'].items()):
        if slot in block['delegate'].values() and want.lower() not in connected:
            problems.append('executor %s: terminal %r não está conectado a este' % (slot, want))
    problems += delegation_problems(block)
    expected = {block['roles'][r].lower() for r in ROLES} | {t.lower() for t in block['executors'].values()}
    extra = sorted(a for low, a in connected.items() if low not in expected)
    if extra:
        problems.append('terminais conectados fora do mapa (ignorados no despacho): %s' % ', '.join(extra))
    return problems


def delegate(repo, command, listing, env=None):
    """('terminal', nome) quando o comando roda em outro terminal; ('local', motivo) quando roda aqui."""
    if command not in DELEGABLE:
        return 'local', 'comando não delegável'
    block = load(repo)
    if not block or not block['enabled']:
        return 'local', 'integração com o Maestri desligada'
    if not in_maestri(env):
        return 'local', 'sessão fora do Maestri'
    slot = block['delegate'].get(command)
    if not slot:
        return 'local', 'comando sem delegação no perfil'
    if listing is None:
        return 'local', 'maestri list não respondeu'
    seen = parse_list(listing)
    want = _target(block, slot)
    if want is None:
        return 'local', 'delegado a %r, que não está no mapa' % slot
    if seen['me'] and seen['me'].lower() == want.lower():
        return 'local', 'este é o terminal %s' % want
    if seen['me'] and seen['me'].lower() != block['manager'].lower():
        return 'local', 'só o %s delega' % block['manager']
    agents = {a.lower(): a for a in seen['agents']}
    if want.lower() not in agents:
        return 'local', 'terminal %r não está conectado' % want
    return 'terminal', agents[want.lower()]


def route(repo, role, listing, env=None):
    """('terminal', nome) quando o papel vai para o terminal; ('subagente', motivo) no resto."""
    if role not in ROLES:
        raise ConfigError('papel %r desconhecido; use %s' % (role, ', '.join(ROLES)))
    block = load(repo)
    if not block or not block['enabled']:
        return 'subagente', 'integração com o Maestri desligada'
    if not in_maestri(env):
        return 'subagente', 'sessão fora do Maestri'
    if listing is None:
        return 'subagente', 'maestri list não respondeu'
    name = block['roles'][role]
    agents = {a.lower(): a for a in parse_list(listing)['agents']}
    if name.lower() not in agents:
        return 'subagente', 'terminal %r não está conectado' % name
    return 'terminal', agents[name.lower()]


def _roles_arg(values):
    roles = {}
    for item in values or []:
        if '=' not in item:
            raise ConfigError('use papel=terminal, recebido %r' % item)
        role, terminal = item.split('=', 1)
        roles[role.strip()] = terminal
    return roles


def main(argv=None):
    ap = argparse.ArgumentParser(description='ligação do projeto com o Maestri')
    ap.add_argument('cmd', choices=('show', 'on', 'off', 'check', 'route', 'delegate'))
    ap.add_argument('repo', nargs='?', default=os.getcwd())
    ap.add_argument('--role', action='append')
    ap.add_argument('--note')
    ap.add_argument('--command')
    ap.add_argument('--delegate', action='append')
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    try:
        if a.cmd == 'show':
            block = load(repo)
            print(json.dumps(block, ensure_ascii=False, indent=2) if block else 'sem bloco maestri: desligado')
            return 0
        if a.cmd == 'on':
            turn_on(repo, _roles_arg(a.role), a.note, _roles_arg(a.delegate))
            print('ligado')
        elif a.cmd == 'delegate':
            if not a.command:
                raise ConfigError('delegate pede --command')
            kind, detail = delegate(repo, a.command, list_output() if in_maestri() else None)
            print('terminal %s' % detail if kind == 'terminal' else 'local: %s' % detail)
            return 0
        elif a.cmd == 'off':
            print('desligado' if turn_off(repo) else 'sem bloco maestri: já desligado')
            return 0
        elif a.cmd == 'route':
            if not a.role or len(a.role) != 1:
                raise ConfigError('route pede um --role')
            kind, detail = route(repo, a.role[0], list_output() if in_maestri() else None)
            print('terminal %s' % detail if kind == 'terminal' else 'subagente: %s' % detail)
            return 0
        problems = check(repo, list_output() if in_maestri() else None)
        for p in problems:
            print('falta: %s' % p)
        if not problems:
            print('ok: manager, %d papéis e a nota de status conectados' % len(ROLES))
        return 1 if problems else 0
    except ConfigError as exc:
        print('recusado: %s' % exc)
        return 1


if __name__ == '__main__':
    sys.exit(main())
