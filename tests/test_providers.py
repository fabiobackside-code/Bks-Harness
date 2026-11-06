"""Testes das definições de provedor em providers/.

Uso: python tests/test_providers.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
_spec = importlib.util.spec_from_file_location('providers', os.path.join(ROOT, 'scripts', 'providers.py'))
providers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(providers)
import keyvault
PROVIDERS_DIR = os.path.join(ROOT, 'providers')
NAMES = ('claude', 'deepseek', 'openrouter')
KEYS = ('version', 'name', 'requires_key', 'base_url', 'env', 'default_models', 'single_model')
LABELS = ('opus', 'sonnet', 'haiku')

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


def load(name):
    path = os.path.join(PROVIDERS_DIR, name + '.json')
    try:
        with io.open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        return exc


def definitions_are_valid():
    print('definitions_are_valid')
    defs = {}
    for name in NAMES:
        data = load(name)
        ok = isinstance(data, dict)
        check('%s.json carrega como JSON' % name, ok, '' if ok else repr(data))
        if not ok:
            continue
        defs[name] = data
        check('%s.json tem version 1' % name, data.get('version') == 1, data.get('version'))
        missing = [k for k in KEYS if k not in data]
        check('%s.json tem as chaves do formato' % name, not missing, missing)
        check('%s.json tem name igual ao arquivo' % name, data.get('name') == name, data.get('name'))

    claude = defs.get('claude')
    if claude:
        check('claude não pede chave', claude.get('requires_key') is False)
        check('claude não injeta variável',
              claude.get('base_url') is None and claude.get('env') is None
              and claude.get('default_models') is None)

    for name in ('deepseek', 'openrouter'):
        data = defs.get(name)
        if not data:
            continue
        env = data.get('env') or {}
        labels = env.get('labels') or {}
        check('%s pede chave' % name, data.get('requires_key') is True)
        check('%s tem endereço https' % name, str(data.get('base_url', '')).startswith('https://'),
              data.get('base_url'))
        check('%s tem variáveis de endereço e token' % name,
              bool(env.get('base_url')) and bool(env.get('token')), env)
        check('%s tem as três variáveis de rótulo' % name,
              all(labels.get(label) for label in LABELS), labels)
        clear = env.get('clear', [])
        check('%s env.clear, quando presente, é lista de nomes' % name,
              isinstance(clear, list) and all(isinstance(v, str) and v for v in clear), clear)

    for name, data in defs.items():
        if data.get('requires_key') is True:
            clear = (data.get('env') or {}).get('clear', [])
            check('%s pede chave e esvazia ANTHROPIC_API_KEY' % name,
                  isinstance(clear, list) and 'ANTHROPIC_API_KEY' in clear, clear)

    deepseek = defs.get('deepseek')
    if deepseek:
        models = deepseek.get('default_models') or {}
        check('deepseek tem modelo padrão por rótulo', all(models.get(l) for l in LABELS), models)
        check('deepseek não é modelo único', deepseek.get('single_model') is False)

    openrouter = defs.get('openrouter')
    if openrouter:
        check('openrouter é modelo único', openrouter.get('single_model') is True)
        check('openrouter não tem modelo padrão', openrouter.get('default_models') is None)


class FakeStore:
    def __init__(self):
        self.data = {}

    def get_password(self, service, user):
        return self.data.get((service, user))

    def set_password(self, service, user, value):
        self.data[(service, user)] = value


def raises(exc_type, fn):
    try:
        fn()
    except exc_type as exc:
        return exc
    return None


def read_text(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def decrypt_key(store, name='deepseek'):
    cfg = providers.read_config()
    return keyvault.decrypt(cfg['providers'][name]['key'], keyvault.master_key(store))


def configuration_behaviour():
    print('configuration_behaviour')
    saved_home = os.environ.get('BKHAR_HOME')
    with tempfile.TemporaryDirectory() as home:
        os.environ['BKHAR_HOME'] = home
        path = os.path.join(home, 'providers.json')
        check('config_path usa BKHAR_HOME', providers.config_path() == path, providers.config_path())

        absent = {'PATH': '/bin', 'ANTHROPIC_BASE_URL': 'https://x'}
        out = providers.build_env(absent, FakeStore())
        check('build_env sem providers.json é cópia igual', out == absent and out is not absent, out)
        check('show sem providers.json mostra claude', 'claude' in providers.show(FakeStore()))

        store = FakeStore()
        providers.set_provider('deepseek', key='  sk-1234\n', store=store)
        cfg = providers.read_config()
        defaults = {'opus': 'deepseek-v4-pro', 'sonnet': 'deepseek-flash', 'haiku': 'deepseek-flash'}
        check('set_deepseek_defaults', cfg['providers']['deepseek']['models'] == defaults
              and cfg['active'] == 'deepseek' and cfg['version'] == 1, cfg)
        check('key_not_in_plaintext', 'sk-1234' not in read_text(path))
        check('key_is_stripped', decrypt_key(store) == 'sk-1234', decrypt_key(store))
        shown = providers.show(store)
        check('show_masks_key', '****1234' in shown and 'sk-1234' not in shown, shown)

        env = providers.build_env({'PATH': '/bin', 'ANTHROPIC_API_KEY': 'real'}, store)
        check('build_env_deepseek', env['ANTHROPIC_BASE_URL'] == 'https://api.deepseek.com/anthropic'
              and env['ANTHROPIC_AUTH_TOKEN'] == 'sk-1234'
              and env['ANTHROPIC_DEFAULT_OPUS_MODEL'] == 'deepseek-v4-pro'
              and env['ANTHROPIC_DEFAULT_SONNET_MODEL'] == 'deepseek-flash'
              and env['ANTHROPIC_DEFAULT_HAIKU_MODEL'] == 'deepseek-flash'
              and env['PATH'] == '/bin', env)
        check('build_env_deepseek esvazia ANTHROPIC_API_KEY', env['ANTHROPIC_API_KEY'] == '', env)

        base = {'PATH': '/bin', 'ANTHROPIC_API_KEY': 'real'}
        snapshot = dict(base)
        providers.build_env(base, store)
        check('build_env_does_not_mutate_input', base == snapshot, base)

        providers.set_provider('openrouter', key='or-9999', models={'model': 'x/y'}, store=store)
        models = providers.read_config()['providers']['openrouter']['models']
        check('set_openrouter_single', models == {'opus': 'x/y', 'sonnet': 'x/y', 'haiku': 'x/y'}, models)
        check('openrouter_requires_model',
              raises(ValueError, lambda: providers.set_provider('openrouter', key='k', store=store)) is not None)
        check('deepseek exige chave',
              raises(ValueError, lambda: providers.set_provider('deepseek', key='  \n', store=store)) is not None
              and raises(ValueError, lambda: providers.set_provider('deepseek', store=store)) is not None)

        env = providers.build_env({'ANTHROPIC_API_KEY': 'real'}, store)
        check('build_env_openrouter', env['ANTHROPIC_API_KEY'] == '' and env['ANTHROPIC_AUTH_TOKEN'] == 'or-9999'
              and all(env[v] == 'x/y' for v in ('ANTHROPIC_DEFAULT_OPUS_MODEL',
                      'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL')), env)
        providers.set_provider('deepseek', key='k', models={'opus': ' a ', 'sonnet': 'b', 'haiku': 'c'}, store=store)
        check('modelos explícitos sem espaço', providers.read_config()['providers']['deepseek']['models']['opus'] == 'a')

        providers.set_provider('claude', store=store)
        incoming = {'ANTHROPIC_BASE_URL': 'https://x', 'ANTHROPIC_API_KEY': 'real'}
        out = providers.build_env(incoming, store)
        check('build_env_claude_untouched', out == incoming and out is not incoming, out)
        check('claude mantém ANTHROPIC_API_KEY', out['ANTHROPIC_API_KEY'] == 'real')

        write_text(path, '{')
        err = raises(providers.ConfigError, providers.read_config)
        check('corrupt_config_message', err is not None and path in str(err), err)
        write_text(path, json.dumps({'version': 9, 'active': 'claude', 'providers': {}}))
        err = raises(providers.ConfigError, providers.read_config)
        check('unknown_version_message', err is not None and path in str(err), err)

        providers.set_provider('claude', store=store)
        cfg = providers.read_config()
        check('set_provider recupera arquivo inválido', cfg['active'] == 'claude' and cfg['version'] == 1, cfg)
        write_text(path, '{')
        providers.set_provider('claude', store=store)
        check('set_provider recupera JSON corrompido', providers.read_config()['active'] == 'claude')

        for broken in ({'models': {'opus': 'a', 'sonnet': 'b', 'haiku': 'c'}}, {'key': {'v': 1}},
                       {'key': {'v': 1}, 'models': {'opus': 'a'}}, 'texto'):
            write_text(path, json.dumps({'version': 1, 'active': 'deepseek', 'providers': {'deepseek': broken}}))
            calls = (('show', lambda: providers.show(store)), ('build_env', lambda: providers.build_env({}, store)))
            for fn_name, fn in calls:
                err = raises(Exception, fn)
                check('entrada incompleta em %s vira ConfigError (%s)' % (fn_name, json.dumps(broken)),
                      isinstance(err, providers.ConfigError) and path in str(err) and chr(10) not in str(err), repr(err))

        os.remove(path)
        empty = FakeStore()
        providers.set_provider('deepseek', key='sk-5555', store=store)
        check('build_env sem chave mestra erra',
              raises(keyvault.KeyVaultError, lambda: providers.build_env({}, empty)) is not None)
        check('show sem chave mestra erra',
              raises(keyvault.KeyVaultError, lambda: providers.show(empty)) is not None)
        check('chave mestra não é criada por build_env', not empty.data, empty.data)

    if saved_home is None:
        os.environ.pop('BKHAR_HOME', None)
    else:
        os.environ['BKHAR_HOME'] = saved_home
    err = raises(ValueError, lambda: providers.load_definition('ollama'))
    check('unknown_provider', err is not None and 'claude, deepseek, openrouter' in str(err), err)
    check('load_definition devolve a definição', providers.load_definition('deepseek')['name'] == 'deepseek')


def main():
    print('testes das definições de provedor')
    definitions_are_valid()
    configuration_behaviour()
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
