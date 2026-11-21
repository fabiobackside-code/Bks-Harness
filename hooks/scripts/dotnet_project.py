"""Guarda: projeto .NET sem FluentAssertions, sem solution .sln nova e sem migration existente alterada.

Novo e existente se medem contra o HEAD do repositório; fora de git, contra o disco. No --all do
pre-commit (CI) todo arquivo está no HEAD, então só a regra do FluentAssertions vale ali.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import guard, deny, target_path, written_content

PACKAGE_FILES = ('.csproj', '.props', '.targets', 'packages.config')
FLUENT = re.compile(r'(?i)Include\s*=\s*"FluentAssertions(\.[A-Za-z.]+)?"|id\s*=\s*"FluentAssertions"')
MIGRATION_DIR = re.compile(r'(?i)(^|/)Migrations/')


def committed(path):
    folder = os.path.dirname(path) or '.'
    while folder and not os.path.isdir(folder):
        parent = os.path.dirname(folder)
        if parent == folder:
            return os.path.exists(path)
        folder = parent
    rel = os.path.relpath(path, folder).replace(os.sep, '/')
    try:
        inside = subprocess.run(['git', '-C', folder, 'rev-parse', '--is-inside-work-tree'],
                                capture_output=True, text=True, timeout=10)
        if inside.returncode != 0:
            return os.path.exists(path)
        r = subprocess.run(['git', '-C', folder, 'cat-file', '-e', 'HEAD:./%s' % rel], capture_output=True,
                           timeout=10)
    except (OSError, subprocess.SubprocessError):
        return os.path.exists(path)
    return r.returncode == 0


def check(payload):
    path = target_path(payload)
    if not path:
        return
    norm = path.replace('\\', '/')
    name = norm.rsplit('/', 1)[-1]
    lower = name.lower()
    whole_repo = payload.get('bkhar_scope') == 'all'

    if lower.endswith(PACKAGE_FILES) and FLUENT.search(written_content(payload)):
        deny('Bloqueado: FluentAssertions em %s.\n\n'
             'A v8 passou a licença comercial paga; o kit usa o Assert nativo do xUnit. '
             'Tire o pacote e escreva as asserções com Assert.' % name)

    if whole_repo:
        return

    if lower.endswith('.sln') and not committed(path):
        deny('Bloqueado: solution nova em formato .sln (%s).\n\n'
             'Solution .NET 10 nasce como .slnx, o formato XML do SDK 10. O .sln clássico só '
             'quando alguma ferramenta exigir; nesse caso, peça a exceção ao usuário.' % name)

    if lower.endswith('.cs') and MIGRATION_DIR.search(norm) and not lower.endswith('modelsnapshot.cs') \
            and committed(path):
        deny('Bloqueado: alteração da migration existente %s.\n\n'
             'Migration aplicada não muda: o banco de quem já rodou fica diferente do código. '
             'Crie uma migration nova com a correção.' % name)


if __name__ == '__main__':
    guard(check)
