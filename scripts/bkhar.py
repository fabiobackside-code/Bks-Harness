"""Lançador bkhar: escolhe o provedor e inicia o claude com o ambiente montado."""
import argparse
import getpass
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import keyvault  # noqa: E402
    import providers  # noqa: E402
    MISSING = None
except ImportError as exc:
    keyvault = providers = None
    MISSING = exc.name or 'desconhecida'


def _parser():
    parser = argparse.ArgumentParser(prog='bkhar', description='Lançador do claude com provedor configurável.')
    sub = parser.add_subparsers(dest='command')
    prov = sub.add_parser('provider', help='configura o provedor')
    prov_sub = prov.add_subparsers(dest='action', required=True)
    set_cmd = prov_sub.add_parser('set', help='define o provedor ativo')
    set_cmd.add_argument('name', choices=providers.NAMES)
    set_cmd.add_argument('--key', help='chave da API; sem ela, é pedida sem eco')
    set_cmd.add_argument('--reasoning', help='modelo de raciocínio (opus), só deepseek')
    set_cmd.add_argument('--chat', help='modelo de conversa (sonnet e haiku), só deepseek')
    set_cmd.add_argument('--model', help='modelo único, só openrouter')
    prov_sub.add_parser('show', help='mostra o provedor ativo')
    return parser


def _models(args, definition):
    if definition['single_model']:
        return {'model': args.model}
    if args.reasoning or args.chat:
        models = dict(definition['default_models'])
        if args.reasoning:
            models['opus'] = args.reasoning
        if args.chat:
            models['sonnet'] = models['haiku'] = args.chat
        return models
    return None


def _provider_set(args, store):
    definition = providers.load_definition(args.name)
    key = args.key
    if definition['requires_key'] and not key:
        key = getpass.getpass('Chave de %s: ' % args.name)
    providers.set_provider(args.name, key=key, models=_models(args, definition), store=store)
    print("provedor ativo: %s" % args.name)


def run_child(args, env=None, popen=subprocess.Popen):
    """Inicia o claude e devolve o código de saída dele; Ctrl+C no lançador não derruba o filho."""
    child = popen(args, env=env)
    while True:
        try:
            return child.wait()
        except KeyboardInterrupt:
            continue


def _launch(rest, run, which, store):
    claude = which('claude')
    if not claude:
        print("claude não encontrado no PATH; instale o Claude Code e tente de novo", file=sys.stderr)
        return 127
    env = providers.build_env(os.environ, store)
    return run([claude] + rest, env=env)


def main(argv, run=run_child, which=shutil.which, store=None):
    """Executa o comando e devolve o código de saída; o do claude, no lançamento."""
    if MISSING:
        print("erro: dependência ausente: %s; rode 'python -m pip install -r requirements.txt'" % MISSING,
              file=sys.stderr)
        return 1
    argv = list(argv)
    rest = []
    if '--' in argv:
        cut = argv.index('--')
        argv, rest = argv[:cut], argv[cut + 1:]
    try:
        args = _parser().parse_args(argv)
        if args.command == 'provider' and args.action == 'set':
            _provider_set(args, store)
            return 0
        if args.command == 'provider':
            print(providers.show(store))
            return 0
        return _launch(rest, run, which, store)
    except (providers.ConfigError, keyvault.KeyVaultError, ValueError) as exc:
        print('erro: %s' % exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
