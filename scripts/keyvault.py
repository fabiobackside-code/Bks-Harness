"""Cofre da chave do provedor: cifra AES-256-GCM e chave mestra no cofre do sistema."""
import base64
import binascii
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SERVICE = 'bkhar'
USER = 'master'
VERSION = 1
NONCE_SIZE = 12
KEY_SIZE = 32


class KeyVaultError(Exception):
    """Falha de cifra ou de acesso à chave mestra; a mensagem nunca carrega a chave."""


def _b64(data):
    return base64.b64encode(data).decode('ascii')


def encrypt(plaintext, master):
    """Cifra o texto e devolve o registro {v, nonce, ct}."""
    _check_master(master)
    nonce = os.urandom(NONCE_SIZE)
    ct = AESGCM(master).encrypt(nonce, plaintext.encode('utf-8'), None)
    return {'v': VERSION, 'nonce': _b64(nonce), 'ct': _b64(ct)}


def decrypt(record, master):
    """Decifra o registro; levanta KeyVaultError em versão, adulteração ou chave erradas."""
    if not isinstance(record, dict) or record.get('v') != VERSION:
        raise KeyVaultError('registro cifrado de versão desconhecida')
    _check_master(master)
    try:
        nonce = base64.b64decode(record['nonce'], validate=True)
        ct = base64.b64decode(record['ct'], validate=True)
        return AESGCM(master).decrypt(nonce, ct, None).decode('utf-8')
    except (KeyError, TypeError, ValueError, binascii.Error, InvalidTag):
        raise KeyVaultError('registro cifrado inválido, adulterado ou chave mestra diferente') from None


def _default_store():
    try:
        import keyring
    except ImportError:
        raise KeyVaultError("pacote 'keyring' ausente; rode 'python -m pip install -r requirements.txt'") from None
    return keyring


def _check_master(master):
    if not isinstance(master, bytes) or len(master) != KEY_SIZE:
        raise KeyVaultError('chave mestra deve ter 32 bytes')


def master_key(store=None, create=False):
    """Lê a chave mestra do cofre; com create=True gera e grava se não existir."""
    store = store or _default_store()
    try:
        stored = store.get_password(SERVICE, USER)
    except Exception as exc:
        raise KeyVaultError('cofre do sistema indisponível: %s' % type(exc).__name__) from None
    if stored:
        try:
            key = base64.b64decode(stored, validate=True)
        except (ValueError, binascii.Error):
            key = b''
        if len(key) != KEY_SIZE:
            raise KeyVaultError("chave mestra inválida no cofre; rode 'bkhar provider set' de novo")
        return key
    if not create:
        raise KeyVaultError("chave mestra ausente; rode 'bkhar provider set' de novo")
    key = os.urandom(KEY_SIZE)
    try:
        store.set_password(SERVICE, USER, _b64(key))
    except Exception as exc:
        raise KeyVaultError('cofre do sistema indisponível: %s' % type(exc).__name__) from None
    return key


def mask(secret):
    """Mascara o segredo mostrando só os quatro últimos caracteres."""
    return '****' + secret[-4:] if len(secret) > 4 else '****'
