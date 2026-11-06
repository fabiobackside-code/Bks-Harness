"""Testes do lançador scripts/bkhar.py, com run, which e cofre falsos.

Uso: python tests/test_bkhar.py
"""
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
_spec = importlib.util.spec_from_file_location('bkhar', os.path.join(ROOT, 'scripts', 'bkhar.py'))
bkhar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bkhar)
import providers

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


class FakeStore:
    def __init__(self):
        self.data = {}

    def get_password(self, service, user):
        return self.data.get((service, user))

    def set_password(self, service, user, value):
        self.data[(service, user)] = value


class Recorder:
    def __init__(self, code=0):
        self.calls = []
        self.code = code

    def __call__(self, args, env=None):
        self.calls.append((list(args), env))
        return self.code


def launch(argv, store, which=lambda name: '/bin/claude', code=0):
    rec = Recorder(code)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = bkhar.main(argv, run=rec, which=which, store=store)
    return rc, rec, out.getvalue(), err.getvalue()


def run_all():
    store = FakeStore()
    secret = 'sk-secret-1234'

    print('launch')
    rc, rec, _, _ = launch(['--', '-p', 'oi'], store)
    check('launch_passes_args', rc == 0 and rec.calls and rec.calls[0][0] == ['/bin/claude', '-p', 'oi'], rec.calls)
    rc, rec, _, _ = launch([], store, code=7)
    check('exit_code_is_claudes', rc == 7 and rec.calls[0][0] == ['/bin/claude'], rc)

    os.environ['ANTHROPIC_BASE_URL'] = 'https://parent'
    rc, rec, _, _ = launch([], store)
    check('claude_provider_keeps_parent_env', rec.calls[0][1].get('ANTHROPIC_BASE_URL') == 'https://parent',
          rec.calls[0][1].get('ANTHROPIC_BASE_URL'))
    del os.environ['ANTHROPIC_BASE_URL']

    print('provider set deepseek')
    rc, _, out, err = launch(['provider', 'set', 'deepseek', '--key', secret], store)
    cfg = providers.read_config()
    check('deepseek_default_fallback', rc == 0 and cfg['providers']['deepseek']['models']
          == {'opus': 'deepseek-v4-pro', 'sonnet': 'deepseek-flash', 'haiku': 'deepseek-flash'}, cfg)
    check('set_never_prints_key', secret not in out + err, out + err)

    rc, rec, _, _ = launch(['--', '-p', 'oi'], store)
    check('launch_uses_built_env', rec.calls[0][1].get('ANTHROPIC_AUTH_TOKEN') == secret, rec.calls[0][1])
    check('parent_env_untouched', secret not in os.environ.values()
          and 'ANTHROPIC_AUTH_TOKEN' not in os.environ)

    launch(['provider', 'set', 'deepseek', '--key', secret, '--reasoning', 'r', '--chat', 'c'], store)
    models = providers.read_config()['providers']['deepseek']['models']
    check('deepseek_flags', models == {'opus': 'r', 'sonnet': 'c', 'haiku': 'c'}, models)

    launch(['provider', 'set', 'deepseek', '--key', secret, '--chat', 'c'], store)
    models = providers.read_config()['providers']['deepseek']['models']
    check('deepseek_chat_only_falls_back', models == {'opus': 'deepseek-v4-pro', 'sonnet': 'c', 'haiku': 'c'}, models)

    launch(['provider', 'set', 'deepseek', '--key', secret, '--reasoning', 'r'], store)
    models = providers.read_config()['providers']['deepseek']['models']
    check('deepseek_reasoning_only_falls_back', models == {'opus': 'r', 'sonnet': 'deepseek-flash',
                                                          'haiku': 'deepseek-flash'}, models)

    rc, _, out, err = launch(['provider', 'show'], store)
    check('show_never_prints_key', rc == 0 and secret not in out + err and '****1234' in out, out + err)

    print('provider set openrouter / claude')
    rc, _, _, _ = launch(['provider', 'set', 'openrouter', '--key', secret, '--model', 'vendor/m'], store)
    models = providers.read_config()['providers']['openrouter']['models']
    check('openrouter_single_model', rc == 0 and set(models.values()) == {'vendor/m'}, models)
    rc, _, _, err = launch(['provider', 'set', 'openrouter', '--key', secret], store)
    check('openrouter_requires_model', rc == 1 and err.count('\n') == 1 and 'use --model <modelo>' in err, err)
    rc, _, _, _ = launch(['provider', 'set', 'claude'], store)
    check('set_claude', rc == 0 and providers.read_config()['active'] == 'claude')

    print('prompt da chave')
    real_getpass = bkhar.getpass.getpass
    bkhar.getpass.getpass = lambda prompt='': ' sk-typed-9999\n'
    try:
        rc, _, out, err = launch(['provider', 'set', 'deepseek'], store)
    finally:
        bkhar.getpass.getpass = real_getpass
    _, _, out2, _ = launch(['provider', 'show'], store)
    check('key_prompted_via_getpass', rc == 0 and '****9999' in out2, out2)

    print('erros')
    rc, rec, _, err = launch([], store, which=lambda name: None)
    check('claude_missing', rc == 127 and 'claude' in err and not rec.calls, (rc, err))

    with open(providers.config_path(), 'w', encoding='utf-8') as fh:
        fh.write('{lixo')
    rc, rec, _, err = launch([], store)
    check('config_error_exit', rc == 1 and err.count('\n') == 1 and 'Traceback' not in err and not rec.calls, err)
    rc, _, _, err = launch(['provider', 'show'], store)
    check('config_error_show', rc == 1 and err.count('\n') == 1, err)

    providers.set_provider('deepseek', key=secret, store=store)
    rc, rec, _, err = launch([], FakeStore())
    check('keyvault_error_exit', rc == 1 and err.count('\n') == 1 and 'Traceback' not in err
          and not rec.calls and secret not in err, err)


def missing_dependency():
    print('dependência ausente')
    names = [k for k in list(sys.modules) if k in ('keyvault', 'providers') or k.split('.')[0] == 'cryptography']
    saved = {k: sys.modules.pop(k) for k in names}
    saved.setdefault('cryptography', None)
    sys.modules['cryptography'] = None
    try:
        spec = importlib.util.spec_from_file_location('bkhar_nodeps', os.path.join(ROOT, 'scripts', 'bkhar.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = mod.main([], run=Recorder(), which=lambda name: '/bin/claude')
    finally:
        sys.modules.pop('cryptography', None)
        sys.modules.update({k: v for k, v in saved.items() if v is not None})
    text = err.getvalue()
    check('missing_dependency_exit', rc == 1 and text.count(chr(10)) == 1 and 'cryptography' in text
          and 'pip install -r requirements.txt' in text and 'Traceback' not in text, repr((rc, text)))


class InterruptedChild:
    def __init__(self, code):
        self.code = code
        self.waits = 0

    def wait(self):
        self.waits += 1
        if self.waits == 1:
            raise KeyboardInterrupt
        return self.code


def ctrl_c():
    print('Ctrl+C')
    started = []

    def popen(args, env=None):
        started.append(list(args))
        started.append(InterruptedChild(9))
        return started[-1]

    run = lambda args, env=None: bkhar.run_child(args, env=env, popen=popen)
    out, err = io.StringIO(), io.StringIO()
    old = os.environ.get('BKHAR_HOME')
    os.environ['BKHAR_HOME'] = tempfile.mkdtemp()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bkhar.main(['--', '-p', 'oi'], run=run, which=lambda name: '/bin/claude', store=FakeStore())
    finally:
        shutil.rmtree(os.environ['BKHAR_HOME'], ignore_errors=True)
        os.environ['BKHAR_HOME'] = old
    check('ctrl_c_keeps_child_code', rc == 9 and started and started[0] == ['/bin/claude', '-p', 'oi']
          and started[1].waits == 2, (rc, started))
    check('ctrl_c_no_traceback', err.getvalue() == '' and 'Traceback' not in out.getvalue(), err.getvalue())
    check('default_run_is_run_child', bkhar.main.__defaults__[0] is bkhar.run_child)


def main():
    print('testes do bkhar.py')
    home = tempfile.mkdtemp()
    old = os.environ.get('BKHAR_HOME')
    os.environ['BKHAR_HOME'] = home
    try:
        run_all()
        missing_dependency()
        ctrl_c()
    finally:
        if old is None:
            os.environ.pop('BKHAR_HOME', None)
        else:
            os.environ['BKHAR_HOME'] = old
        shutil.rmtree(home, ignore_errors=True)
    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
