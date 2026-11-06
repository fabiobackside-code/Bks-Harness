"""Testes do guarda architect_bash: o que o architect pode rodar no Bash e o que os outros papéis não perdem."""
import json
import os
import subprocess
import sys
import tempfile

H = 'hooks/scripts'
ROOT = os.path.abspath('.')


def run(payload):
    r = subprocess.run([sys.executable, os.path.join(H, 'architect_bash.py')],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=20)
    out = r.stdout.strip()
    if not out:
        return 'ALLOW'
    return json.loads(out).get('hookSpecificOutput', {}).get('permissionDecision', 'ALLOW').upper()


def bash(command, agent='architect'):
    payload = {'tool_name': 'Bash', 'tool_input': {'command': command}}
    if agent is not None:
        payload['agent_type'] = agent
    return payload


PROJECT = tempfile.mkdtemp()
HOME = os.path.expanduser('~')


def write(path, tool='Write', agent='architect'):
    return {'tool_name': tool, 'agent_type': agent, 'cwd': PROJECT,
            'tool_input': {'file_path': path, 'content': 'x', 'new_string': 'x'}}


SCRIPT = os.path.join(ROOT, 'scripts', 'library.py').replace(os.sep, '/')
cases = [
    ('script do plugin por caminho', bash('python "%s" stale .' % SCRIPT), 'ALLOW'),
    ('script do plugin por variável', bash('python ${CLAUDE_PLUGIN_ROOT}/scripts/wave_graph.py validate .'), 'ALLOW'),
    ('agente com prefixo do plugin', bash('python ${CLAUDE_PLUGIN_ROOT}/scripts/library.py build .',
                                          'bkhar:architect'), 'ALLOW'),
    ('git status', bash('git status --short'), 'ALLOW'),
    ('git log com opção antes', bash('git --no-pager log --oneline -5'), 'ALLOW'),
    ('maestri ask com markdown em aspas simples',
     bash("maestri ask \"manager\" 'feito: `ARCH` em docs/; ver | tabela'"), 'ALLOW'),
    ('maestri ask com texto em aspas duplas', bash('maestri ask "manager" "resultado; pronto"'), 'ALLOW'),
    ('python de outro script', bash('python app/tools/seed.py'), 'DENY'),
    ('python com -c', bash('python -c "print(1)"'), 'DENY'),
    ('script com nome de plugin fora dele', bash('python /tmp/scripts/library.py stale .'), 'DENY'),
    ('dotnet build', bash('dotnet build'), 'DENY'),
    ('npm install', bash('npm install'), 'DENY'),
    ('git commit', bash('git commit -m x'), 'DENY'),
    ('git push', bash('git push origin main'), 'DENY'),
    ('encadeado com &&', bash('git status && rm -rf app'), 'DENY'),
    ('encadeado com ;', bash('git status; dotnet test'), 'DENY'),
    ('redirecionamento', bash('git diff > app/x.cs'), 'DENY'),
    ('substituição em aspas duplas', bash('maestri ask "manager" "$(dotnet test)"'), 'DENY'),
    ('crase em aspas duplas', bash('maestri ask "manager" "`dotnet test`"'), 'DENY'),
    ('maestri fora do ask', bash('maestri note write status x'), 'DENY'),
    ('git -c core.pager executa', bash("git -c core.pager='sh -c x' log"), 'DENY'),
    ('git -c colado', bash('git -ccore.pager=x log'), 'DENY'),
    ('git -C para outro repo', bash('git -C /tmp status'), 'DENY'),
    ('git --exec-path', bash('git --exec-path=/tmp log'), 'DENY'),
    ('git diff --output escreve', bash('git diff --output=app/x.cs'), 'DENY'),
    ('git diff --ext-diff', bash('git diff --ext-diff'), 'DENY'),
    ('git log --textconv', bash('git log -p --textconv'), 'DENY'),
    ('git grep -O abre pager', bash('git show -Ocat HEAD'), 'DENY'),
    ('git --no-pager log passa', bash('git --no-pager log -3'), 'ALLOW'),
    ('aspas ANSI-C', bash("maestri ask manager $'x\\' ; dotnet test'"), 'DENY'),
    ('barra invertida fora de aspas', bash('git status \\; dotnet test'), 'DENY'),
    ('comentário', bash('git status # x'), 'DENY'),
    ('Write em .git/config', write('.git/config'), 'DENY'),
    ('Edit em .gitconfig do usuário', write(os.path.join(HOME, '.gitconfig'), 'Edit'), 'DENY'),
    ('Write em ~/.config/git', write(os.path.join(HOME, '.config', 'git', 'config')), 'DENY'),
    ('Write de script no plugin', write(os.path.join(ROOT, 'scripts', 'x.py')), 'DENY'),
    ('Write em código da app', write('app/api/Program.cs'), 'DENY'),
    ('docs/../app escapa', write('docs/../app/x.cs'), 'DENY'),
    ('Write em docs passa', write('docs/library/ARCH.md'), 'ALLOW'),
    ('Edit em specs passa', write('specs/features/FEAT-x.md', 'Edit'), 'ALLOW'),
    ('Write em decisions passa', write('decisions/ADR-001.md'), 'ALLOW'),
    ('Write em outputs passa', write('outputs/PLAN-p.md'), 'ALLOW'),
    ('Write sem cwd recusado', {'tool_name': 'Write', 'agent_type': 'architect',
                                'tool_input': {'file_path': 'docs/x.md', 'content': 'x'}}, 'DENY'),
    ('Write do developer em app passa', write('app/api/Program.cs', agent='developer'), 'ALLOW'),
    ('developer não é afetado', bash('dotnet build', 'developer'), 'ALLOW'),
    ('sessão sem agente não é afetada', bash('dotnet build', None), 'ALLOW'),
    ('ferramenta de leitura passa', {'tool_name': 'Read', 'agent_type': 'architect',
                                     'tool_input': {'file_path': 'app/x.cs'}}, 'ALLOW'),
    ('payload quebrado libera', {}, 'ALLOW'),
]

fail = 0
for name, payload, expect in cases:
    got = run(payload)
    ok = got == expect
    fail += (not ok)
    print('%-4s %-44s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))
print('\nfalhas:', fail)
sys.exit(1 if fail else 0)
