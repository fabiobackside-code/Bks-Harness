"""Testes do scripts/keyvault.py: cifra AES-256-GCM, chave mestra no cofre e máscara.

Uso: python tests/test_keyvault.py
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('keyvault', os.path.join(ROOT, 'scripts', 'keyvault.py'))
keyvault = importlib.util.module_from_spec(spec)
spec.loader.exec_module(keyvault)

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


def raises(fn):
    try:
        fn()
    except keyvault.KeyVaultError as exc:
        return exc
    return None


master = bytes(range(32))
other = bytes(range(1, 33))

record = keyvault.encrypt('sk-abc123', master)
check('roundtrip', keyvault.decrypt(record, master) == 'sk-abc123')
check('record_shape', record.get('v') == 1 and set(record) == {'v', 'nonce', 'ct'}, str(sorted(record)))

a = keyvault.encrypt('sk-abc123', master)
b = keyvault.encrypt('sk-abc123', master)
check('nonce_changes', a['nonce'] != b['nonce'] and a['ct'] != b['ct'])

bad = dict(record)
bad['ct'] = ('A' if record['ct'][0] != 'A' else 'B') + record['ct'][1:]
check('tamper_rejected', raises(lambda: keyvault.decrypt(bad, master)) is not None)

future = dict(record, v=2)
check('unknown_version_rejected', raises(lambda: keyvault.decrypt(future, master)) is not None)

check('wrong_master_rejected', raises(lambda: keyvault.decrypt(record, other)) is not None)

check('malformed_record_rejected',
      raises(lambda: keyvault.decrypt({'v': 1, 'nonce': '!!', 'ct': '!!'}, master)) is not None)

store = FakeStore()
k1 = keyvault.master_key(store, create=True)
k2 = keyvault.master_key(store, create=True)
check('master_created_once', k1 == k2 and len(k1) == 32)
check('master_readable_without_create', keyvault.master_key(store, create=False) == k1)
check('master_stored_in_service', ('bkhar', 'master') in store.data)

err = raises(lambda: keyvault.master_key(FakeStore(), create=False))
check('master_missing_message', err is not None and 'bkhar provider set' in str(err), str(err))

check('mask_short_and_long',
      keyvault.mask('abc') == '****' and keyvault.mask('sk-123456789') == '****6789'
      and keyvault.mask('abcd') == '****')

empty = FakeStore()
raises(lambda: keyvault.master_key(empty, create=False))
check('missing_writes_nothing', empty.data == {})

check('short_master_rejected_encrypt',
      raises(lambda: keyvault.encrypt('x', bytes(16))) is not None
      and raises(lambda: keyvault.encrypt('x', bytes(24))) is not None)
check('short_master_rejected_decrypt', raises(lambda: keyvault.decrypt(record, bytes(16))) is not None)

real_import = __builtins__['__import__'] if isinstance(__builtins__, dict) else __builtins__.__import__


def no_keyring(name, *args, **kwargs):
    if name == 'keyring':
        raise ImportError('simulado')
    return real_import(name, *args, **kwargs)


if isinstance(__builtins__, dict):
    __builtins__['__import__'] = no_keyring
else:
    __builtins__.__import__ = no_keyring
try:
    err = raises(lambda: keyvault.master_key(None, create=False))
finally:
    if isinstance(__builtins__, dict):
        __builtins__['__import__'] = real_import
    else:
        __builtins__.__import__ = real_import
check('keyring_missing_is_keyvault_error', err is not None and 'requirements.txt' in str(err), str(err))

err = raises(lambda: keyvault.decrypt(bad, master))
check('error_has_no_secret', err is not None and 'sk-abc123' not in str(err))

print('\n%d checagens, %d falhas' % (checks, len(failures)))
sys.exit(1 if failures else 0)
