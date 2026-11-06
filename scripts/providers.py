"""Configuração do provedor: definições em providers/, escolha em $BKHAR_HOME/providers.json."""
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keyvault  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVIDERS_DIR = os.path.join(ROOT, 'providers')
NAMES = ('claude', 'deepseek', 'openrouter')
LABELS = ('opus', 'sonnet', 'haiku')
VERSION = 1


class ConfigError(Exception):
    """providers.json ilegível, de versão desconhecida ou com entrada incompleta; a mensagem traz o caminho."""


def load_definition(name):
    """Carrega a definição do provedor; ValueError lista os válidos quando o nome é desconhecido."""
    if name not in NAMES:
        raise ValueError("provedor desconhecido '%s'; válidos: %s" % (name, ', '.join(NAMES)))
    with io.open(os.path.join(PROVIDERS_DIR, name + '.json'), encoding='utf-8') as fh:
        return json.load(fh)


def config_path():
    """Caminho de providers.json sob $BKHAR_HOME (padrão ~/.bkhar)."""
    home = os.environ.get('BKHAR_HOME') or os.path.join(os.path.expanduser('~'), '.bkhar')
    return os.path.join(home, 'providers.json')


def read_config():
    """Lê a configuração; ConfigError quando o JSON é inválido ou a versão não é 1."""
    path = config_path()
    try:
        with io.open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return _empty()
    except (OSError, ValueError):
        raise ConfigError("arquivo de configuração inválido: %s; rode 'bkhar provider set' de novo" % path) from None
    if not isinstance(data, dict) or data.get('version') != VERSION:
        raise ConfigError("versão de configuração desconhecida em %s; rode 'bkhar provider set' de novo" % path)
    return data


def _write_config(data):
    path = config_path()
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, prefix='providers.', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _empty():
    return {'version': VERSION, 'active': 'claude', 'providers': {}}


def _load_or_empty():
    try:
        return read_config()
    except ConfigError:
        return _empty()


def _resolve_models(definition, models):
    if definition['single_model']:
        name = (models or {}).get('model')
        if not isinstance(name, str) or not name.strip():
            raise ValueError("o provedor '%s' exige um modelo; use --model <modelo>" % definition['name'])
        return {label: name.strip() for label in LABELS}
    if models:
        missing = [label for label in LABELS if not str(models.get(label) or '').strip()]
        if missing:
            raise ValueError('modelos ausentes: %s' % ', '.join(missing))
        return {label: str(models[label]).strip() for label in LABELS}
    return dict(definition['default_models'])


def set_provider(name, key=None, models=None, store=None):
    """Grava o provedor ativo; a chave vai cifrada. Devolve a configuração gravada."""
    definition = load_definition(name)
    entry = {}
    if definition['requires_key']:
        key = (key or '').strip()
        if not key:
            raise ValueError("o provedor '%s' exige uma chave" % name)
        entry['models'] = _resolve_models(definition, models)
        master = keyvault.master_key(store, create=True)
        entry['key'] = keyvault.encrypt(key, master)
    data = _load_or_empty()
    data['providers'][name] = entry
    data['active'] = name
    _write_config(data)
    return data


def _active(data):
    name = data.get('active')
    entry = data.get('providers', {}).get(name)
    if name == 'claude':
        return name, entry or {}
    if name not in NAMES or entry is None:
        raise ConfigError("provedor ativo inválido em %s; rode 'bkhar provider set' de novo" % config_path())
    models = entry.get('models') if isinstance(entry, dict) else None
    if not isinstance(models, dict) or 'key' not in entry or not all(models.get(l) for l in LABELS):
        raise ConfigError("entrada de '%s' incompleta em %s; rode 'bkhar provider set %s' de novo"
                          % (name, config_path(), name))
    return name, entry


def show(store=None):
    """Descreve o provedor ativo, o modelo por rótulo e a chave mascarada."""
    name, entry = _active(read_config())
    lines = ['provedor: %s' % name]
    if load_definition(name)['requires_key']:
        secret = keyvault.decrypt(entry['key'], keyvault.master_key(store, create=False))
        for label in LABELS:
            lines.append('%s: %s' % (label, entry['models'][label]))
        lines.append('chave: %s' % keyvault.mask(secret))
    return '\n'.join(lines)


def build_env(base_env, store=None):
    """Cópia de base_env com as variáveis do provedor ativo; para claude, cópia sem alteração."""
    env = dict(base_env)
    name, entry = _active(read_config())
    definition = load_definition(name)
    if not definition['requires_key']:
        return env
    spec = definition['env']
    secret = keyvault.decrypt(entry['key'], keyvault.master_key(store, create=False))
    for var in spec.get('clear', []):
        env[var] = ''
    env[spec['base_url']] = definition['base_url']
    env[spec['token']] = secret
    for label in LABELS:
        env[spec['labels'][label]] = entry['models'][label]
    return env
