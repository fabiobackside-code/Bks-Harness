"""Instala ou atualiza os guardas do bkhar num projeto: cópia em .bkhar/guards/, hook pre-commit e CI do host.

Uso: python install_guards.py <dir-do-projeto> --host github|gitlab|none
Arquivo que não é do bkhar (hook, core.hooksPath, .gitlab-ci.yml) não é sobrescrito: vira aviso.
"""
import json
import os
import shutil
import stat
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARDS = ('secret_guard.py', 'no_dispatcher.py', 'comment_budget.py', 'dotnet_project.py', '_common.py')
HOSTS = ('github', 'gitlab', 'none')
MARK = 'bkhar-guards'
GITLAB_JOB = '.bkhar/guards/gitlab-ci.yml'


def kit_version():
    with open(os.path.join(KIT, '.claude-plugin', 'plugin.json'), encoding='utf-8') as f:
        return json.load(f)['version']


def git(project, *args):
    return subprocess.run(['git', *args], cwd=project, capture_output=True, text=True)


def copy_template(name, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(os.path.join(KIT, 'templates', 'ci', name), dest)


def install(project, host):
    done, warnings = [], []
    gdir = os.path.join(project, '.bkhar', 'guards')
    os.makedirs(gdir, exist_ok=True)
    shutil.copyfile(os.path.join(KIT, 'scripts', 'precommit.py'), os.path.join(gdir, 'precommit.py'))
    for name in GUARDS:
        shutil.copyfile(os.path.join(KIT, 'hooks', 'scripts', name), os.path.join(gdir, name))
    version = kit_version()
    with open(os.path.join(gdir, 'VERSION'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(version + '\n')
    done.append('guardas %s em .bkhar/guards/' % version)

    hook = os.path.join(project, '.githooks', 'pre-commit')
    if os.path.exists(hook) and MARK not in open(hook, encoding='utf-8', errors='replace').read():
        warnings.append('.githooks/pre-commit já existe e não é do bkhar: acrescente a chamada a '
                        '.bkhar/guards/precommit.py nele')
    else:
        copy_template('pre-commit', hook)
        os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        done.append('hook .githooks/pre-commit')

    if host == 'github':
        copy_template('github-guards.yml', os.path.join(project, '.github', 'workflows', 'bkhar-guards.yml'))
        done.append('CI .github/workflows/bkhar-guards.yml')
    elif host == 'gitlab':
        copy_template('gitlab-guards.yml', os.path.join(project, *GITLAB_JOB.split('/')))
        root_ci = os.path.join(project, '.gitlab-ci.yml')
        if not os.path.exists(root_ci):
            with open(root_ci, 'w', encoding='utf-8', newline='\n') as f:
                f.write('include:\n  - local: %s\n' % GITLAB_JOB)
            done.append('CI .gitlab-ci.yml com include do job')
        elif GITLAB_JOB not in open(root_ci, encoding='utf-8', errors='replace').read():
            warnings.append('.gitlab-ci.yml já existe: acrescente "include: - local: %s"' % GITLAB_JOB)
        else:
            done.append('CI do GitLab já incluído')

    if git(project, 'rev-parse', '--git-dir').returncode != 0:
        warnings.append('não é repositório git: rode git init e depois este script de novo para ativar o hook')
        return done, warnings
    current = git(project, 'config', 'core.hooksPath').stdout.strip()
    if current and current != '.githooks':
        warnings.append('core.hooksPath aponta para %s: mantido; o hook do bkhar fica inativo' % current)
    else:
        git(project, 'config', 'core.hooksPath', '.githooks')
        done.append('core.hooksPath = .githooks')
    if MARK in open(hook, encoding='utf-8', errors='replace').read():
        git(project, 'add', '--chmod=+x', '.githooks/pre-commit')
    return done, warnings


def main(argv):
    if len(argv) != 3 or argv[1] != '--host' or argv[2] not in HOSTS:
        print('uso: install_guards.py <dir-do-projeto> --host %s' % '|'.join(HOSTS))
        return 2
    project = os.path.abspath(argv[0])
    if not os.path.isdir(project):
        print('diretório não existe: %s' % project)
        return 2
    done, warnings = install(project, argv[2])
    for line in done:
        print('ok     ' + line)
    for line in warnings:
        print('aviso  ' + line)
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
