"""Suite estrutural do bks-harness (plugin bkhar).

Verifica o que um refactor de skill pode quebrar sem que ninguem perceba:
frontmatter integro, referencia citada que existe, referencia que existe sendo
citada, comando documentado que esta no repositorio, e as invariantes de
conteudo que dao identidade ao kit.

Nao verifica comportamento — se a skill ainda decide certo e trabalho das suites
em evals/, que rodam o agente de verdade. Esta aqui responde a outra pergunta:
o arquivo continua integro depois que eu mexi nele.

Uso: python tests/test_structure.py
"""
import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = chr(92)

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


def read(*parts):
    with io.open(os.path.join(ROOT, *parts), encoding='utf-8') as fh:
        return fh.read()


def listdir(*parts):
    p = os.path.join(ROOT, *parts)
    return sorted(os.listdir(p)) if os.path.isdir(p) else []


def frontmatter(text):
    m = re.match(r'^---\r?\n(.*?)\r?\n---', text, re.S)
    return m.group(1) if m else None


def field(fm, key):
    m = re.search(r'^%s:\s*(.+?)$' % re.escape(key), fm, re.M)
    return m.group(1).strip() if m else None


def test_manifests():
    print('\nmanifestos do plugin')
    plugin = json.loads(read('.claude-plugin', 'plugin.json'))
    market = json.loads(read('.claude-plugin', 'marketplace.json'))

    for key in ('name', 'version', 'description', 'license'):
        check('plugin.json tem %s' % key, key in plugin)

    check('marketplace.json lista o plugin',
          any(p.get('name') == plugin['name'] for p in market.get('plugins', [])))

    versions = set()
    for p in market.get('plugins', []):
        if p.get('name') == plugin['name']:
            versions.add(p.get('version'))
    check('versao bate entre plugin.json e marketplace.json',
          versions == {plugin['version']},
          'plugin.json=%s marketplace=%s' % (plugin['version'], sorted(versions)))


def test_skills():
    print('\nskills')
    skills = [d for d in listdir('skills')
              if os.path.isdir(os.path.join(ROOT, 'skills', d))]
    check('ha skills no repositorio', bool(skills))

    loose = [f for f in listdir('skills')
             if not os.path.isdir(os.path.join(ROOT, 'skills', f))]
    check('skills/ só contém pastas', not loose,
          'arquivo solto ou pacote .skill: %s' % ', '.join(loose))

    for skill in skills:
        text = read('skills', skill, 'SKILL.md')
        fm = frontmatter(text)
        check('%s: SKILL.md tem frontmatter' % skill, fm is not None)
        if not fm:
            continue

        name = field(fm, 'name')
        check('%s: name bate com o diretorio' % skill, name == skill,
              'frontmatter diz %r' % name)
        check('%s: tem description' % skill, 'description:' in fm)

        if 'description:' in fm:
            desc = fm[fm.index('description:'):]
            check('%s: description tem substancia' % skill, len(desc) > 120,
                  'description com %d chars — curta demais para o agente '
                  'decidir quando usar a skill' % len(desc))

        refs_dir = set(listdir('skills', skill, 'references'))

        declared = set(re.findall(r'references/([a-z0-9-]+\.md)', text))
        missing = declared - refs_dir
        check('%s: toda referencia citada com caminho existe' % skill, not missing,
              'citadas e ausentes: %s' % ', '.join(sorted(missing)))

        if refs_dir:
            mentioned = set(re.findall(r'([a-z0-9][a-z0-9-]*\.md)', text))
            orphans = refs_dir - mentioned
            check('%s: toda referencia e alcancavel pelo SKILL.md' % skill,
                  not orphans,
                  'nunca citadas: %s' % ', '.join(sorted(orphans)))

            bare = (refs_dir & mentioned) - declared
            check('%s: referencia citada com o caminho references/' % skill,
                  not bare,
                  'citadas so pelo nome: %s' % ', '.join(sorted(bare)))


def test_commands():
    print('\ncomandos')
    files = [f for f in listdir('commands') if f.endswith('.md')]
    check('ha comandos no repositorio', bool(files))

    for f in files:
        fm = frontmatter(read('commands', f))
        check('%s: tem frontmatter com description' % f,
              fm is not None and 'description:' in fm)

    readme = read('README.md')
    # o README cita o comando namespaceado (`/bkhar:save`); ver docs/ARCHITECTURE.md
    documented = set(re.findall(r'\|\s*`/bkhar:([a-z-]+)`\s*\|', readme))
    present = set(os.path.splitext(f)[0] for f in files)

    check('todo comando documentado existe', documented <= present,
          'no README mas nao no repositorio: %s'
          % ', '.join(sorted(documented - present)))
    check('todo comando esta documentado', present <= documented,
          'no repositorio mas nao no README: %s'
          % ', '.join(sorted(present - documented)))


def test_pointers():
    """Toda referencia a arquivo do repositorio citada em texto existe em disco.

    O regex das outras suites so casa ASCII minusculo, entao um ponteiro
    acentuado passava sem ser visto. Ver docs/ARCHITECTURE.md.
    """
    print('\nponteiros para arquivo')

    # caminho dentro de crase, com ao menos uma barra, terminando em extensao
    # pipeline Node.js externo citado no bks-sdd e nunca versionado aqui;
    # ver ENTREVISTA-unificacao.md, pendencia fora do escopo
    KNOWN_ABSENT = ('agents/INSTALL-AGENTS.md',
                    'agents/USE-AGENTS-STEPBYSTEP.md')
    KIT_DIRS = ('skills/', 'commands/', 'agents/', 'profiles/',
                'hooks/', 'templates/', 'evals/', 'tests/', 'scripts/')
    pattern = re.compile(r'`([^`\s]+/[^`\s]+\.(?:md|py|json|yaml|yml))`')
    scanned = 0
    broken = []

    for sub in ('commands', 'skills', 'agents', 'profiles'):
        base = os.path.join(ROOT, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            # texto de terceiro, copiado como esta; aponta para o repositorio de origem
            if 'third-party' in dirpath.replace(BS, '/').split('/'):
                continue
            for fn in filenames:
                if not fn.endswith('.md'):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT).replace(BS, '/')
                text = io.open(full, encoding='utf-8').read()
                for raw in pattern.findall(text):
                    # so ponteiros para dentro do kit; caminho do projeto
                    # consumidor (docs/, decisions/, .logs/) nao existe aqui
                    if not raw.startswith(KIT_DIRS):
                        continue
                    if '[' in raw or '{' in raw or '*' in raw or '<' in raw:
                        continue
                    if raw in KNOWN_ABSENT:
                        continue
                    scanned += 1
                    if not os.path.exists(os.path.join(ROOT, raw)):
                        broken.append('%s -> %s' % (rel, raw))

    check('ha ponteiros para verificar', scanned > 0,
          'nenhum caminho entre crases encontrado — regex quebrou?')
    check('todo ponteiro para arquivo do repositorio existe', not broken,
          '; '.join(sorted(set(broken))))


def test_agents():
    print('\nagentes')
    files = [f for f in listdir('agents') if f.endswith('.md')]
    check('ha agentes no repositorio', bool(files))

    for f in files:
        fm = frontmatter(read('agents', f))
        check('%s: tem frontmatter' % f, fm is not None)
        if not fm:
            continue
        check('%s: name bate com o arquivo' % f,
              field(fm, 'name') == os.path.splitext(f)[0])
        for key in ('description', 'model', 'tools'):
            check('%s: declara %s' % (f, key), field(fm, key) is not None)

    readme = read('README.md')
    documented = set(re.findall(
        r'\|\s*`([a-z]+)`\s*\|[^|]*\|\s*(?:Sonnet|Opus|Haiku)\s*\|', readme))
    present = set(os.path.splitext(f)[0] for f in files)
    check('todo agente esta documentado no README', present <= documented,
          'faltando: %s' % ', '.join(sorted(present - documented)))


def test_hooks():
    print('\nhooks')
    cfg = json.loads(read('hooks', 'hooks.json'))
    scripts_dir = set(listdir('hooks', 'scripts'))

    declared = set()
    for event in cfg.get('hooks', {}).values():
        for matcher in event:
            for hook in matcher.get('hooks', []):
                cmd = hook.get('command', '')
                for m in re.findall(r'scripts/([a-z_]+\.py)', cmd):
                    declared.add(m)

    check('hooks.json declara guardas', bool(declared))
    check('todo guarda declarado existe', declared <= scripts_dir,
          'declarados e ausentes: %s' % ', '.join(sorted(declared - scripts_dir)))

    runnable = set(s for s in scripts_dir
                   if s.endswith('.py') and not s.startswith('_'))
    check('todo guarda do diretorio esta declarado', runnable <= declared,
          'nunca declarados: %s' % ', '.join(sorted(runnable - declared)))

    for s in sorted(scripts_dir):
        if not s.endswith('.py'):
            continue
        try:
            ast.parse(read('hooks', 'scripts', s))
            check('%s: compila' % s, True)
        except SyntaxError as exc:
            check('%s: compila' % s, False, str(exc))


def test_invariants():
    print('\ninvariantes de conteudo')

    tests_skill = read('skills', 'bks-tests', 'SKILL.md')
    check('bks-tests proibe FluentAssertions',
          'FluentAssertions' in tests_skill and 'Assert` nativo' in tests_skill)
    check('bks-tests fixa o projeto de testes em src/',
          'src/' in tests_skill and 'Nunca em `tests/`' in tests_skill)

    dotnet = read('skills', 'bks-dotnet-solutions', 'SKILL.md')
    check('bks-dotnet-solutions cita o padrao TXC', 'TXC' in dotnet)

    sdd = read('skills', 'bks-sdd', 'SKILL.md')
    phases = set(re.findall(r'^\|\s*\*{0,2}(\d(?:\.\d)?)\*{0,2}\s*\|', sdd, re.M))
    expected = set(['0', '1', '2', '3', '4', '5', '6', '7'])
    check('bks-sdd mapeia as fases 0 a 7', expected <= phases,
          'encontradas: %s' % ', '.join(sorted(phases)))

    guard = read('hooks', 'scripts', 'no_dispatcher.py')
    check('o guarda de dispatcher cobre MediatR e IMediator',
          'MediatR' in guard and 'IMediator' in guard)

    maint = ('skills', 'bks-maintainability-review')
    stacks = [f for f in listdir(*(maint + ('stacks',))) if f.endswith('.md')]
    check('bks-maintainability-review tem a stack .NET', 'dotnet.md' in stacks)
    for f in stacks:
        text = read(*(maint + ('stacks', f)))
        check('stack %s declara Detecção, Repertório e Critérios' % f,
              all(s in text for s in ('## Detecção', '## Repertório', '## Critérios')))

    # cofre específico só no critério condicional, para o núcleo valer em qualquer projeto
    neutral = [read(*(maint + ('SKILL.md',)))] + [
        read(*(maint + ('references', f)))
        for f in ('persona-e-premissas.md', 'criterios-comuns.md', 'rubrica.md')]
    check('núcleo da bks-maintainability-review não cita CyberArk',
          not any('CyberArk' in t for t in neutral))

    command = read('commands', 'maintainability.md')
    check('/bkhar:maintainability grava fora do app/',
          'outputs/maintainability/' in command and 'outputs/references/' in command)
    check('/bkhar:canonize sugere o /bkhar:maintainability',
          '/bkhar:maintainability' in read('commands', 'canonize.md'))

    migrate = read('commands', 'migrate.md')
    layout = ('STATUS.md', 'WORKFLOW.md', 'JOURNAL.md', '.bks-profile.json', 'brain/', 'specs/')
    check('/bkhar:migrate confere o layout do projeto',
          all(item in migrate for item in layout),
          'faltam: %s' % ', '.join(i for i in layout if i not in migrate))
    check('/bkhar:migrate grava o .bkhar.json mínimo',
          all(k in migrate for k in ('.bkhar.json', '"plugin": "bkhar"', '"migrated_from": "bks"')))
    check('/bkhar:migrate exige árvore limpa e fechamento pelo /bks:save',
          'git status --porcelain' in migrate and '/bks:save' in migrate)
    check('/bkhar:migrate não commita', 'Não commite' in migrate)
    check('/bkhar:migrate preserva BKS_VAULT e o JOURNAL.md',
          'BKS_VAULT' in migrate and 'o `JOURNAL.md`, as ADRs' in migrate)


def test_profiles():
    print('\nperfis de projeto')
    files = [f for f in listdir('profiles')
             if f.endswith('.md') and f != 'README.md']
    check('ha perfis no repositorio', bool(files))

    schema = json.loads(read('profiles', 'bks-profile.schema.json'))
    declared = set(schema['properties']['profile']['enum'])
    present = set(os.path.splitext(f)[0] for f in files)

    check('todo perfil do schema tem arquivo', declared <= present,
          'no schema mas sem arquivo: %s' % ', '.join(sorted(declared - present)))
    check('todo arquivo de perfil esta no schema', present <= declared,
          'com arquivo mas fora do schema: %s' % ', '.join(sorted(present - declared)))

    readme = read('profiles', 'README.md')
    for name in sorted(present):
        text = read('profiles', '%s.md' % name)
        check('%s: diz o que gera' % name, '## Gera' in text)
        check('%s: declara as fases' % name, '## Fases' in text)
        check('%s: declara os eixos' % name, '## Eixos' in text)
        check('%s: declara as skills' % name, '## Skills' in text)
        check('%s: listado no README de perfis' % name,
              '(%s.md)' % name in readme)


def test_renderers():
    print('\nrenderers de arquitetura')
    files = [f for f in listdir('profiles', 'architecture-renderers')
             if f.endswith('.md') and f not in ('README.md', '_TEMPLATE.md')]
    check('ha renderers no repositorio', bool(files))

    defaults = []
    for f in sorted(files):
        text = read('profiles', 'architecture-renderers', f)
        fm = frontmatter(text)
        name = os.path.splitext(f)[0]
        check('%s: tem frontmatter' % f, fm is not None)
        if not fm:
            continue
        check('%s: renderer bate com o arquivo' % f,
              field(fm, 'renderer') == name)
        check('%s: declara o tipo' % f, field(fm, 'tipo') is not None)
        check('%s: diz quando e a escolha certa' % f,
              '## Quando e a escolha certa' in text)
        check('%s: declara o limite' % f, '## Limite honesto' in text)
        # o frontmatter usa `padrao` ou `padrão`; ver ENTREVISTA-unificacao.md
        if 'true' in (field(fm, 'padrao'), field(fm, 'padrão')):
            defaults.append(name)

    check('ha exatamente um renderer padrao', len(defaults) == 1,
          'padroes encontrados: %s' % (', '.join(defaults) or 'nenhum'))

    schema = json.loads(read('profiles', 'bks-profile.schema.json'))
    schema_default = schema['properties']['axes']['properties'][
        'architecture_renderer'].get('default')
    check('o padrao do schema tem arquivo',
          schema_default in [os.path.splitext(f)[0] for f in files],
          'schema diz %r' % schema_default)


def test_evals():
    print('\nsuites de eval')
    cases = [d for d in listdir('evals')
             if os.path.isfile(os.path.join(ROOT, 'evals', d, 'case.yaml'))]
    check('ha casos de eval', bool(cases))

    plugin = json.loads(read('.claude-plugin', 'plugin.json'))
    declared = plugin.get('experimental', {}).get('evals')
    check('plugin.json aponta o diretorio de evals',
          declared is not None,
          'sem experimental.evals — o comando cai no default evals/')

    try:
        import yaml
    except ImportError:
        print('  nota  pyyaml ausente: os case.yaml nao foram parseados')
        return

    for case in cases:
        try:
            data = yaml.safe_load(read('evals', case, 'case.yaml'))
            ok = True
        except Exception as exc:
            check('%s: case.yaml e YAML valido' % case, False, str(exc))
            continue
        check('%s: case.yaml e YAML valido' % case, ok)

        check('%s: name bate com o diretorio' % case,
              data.get('name') == case,
              'case.yaml diz %r' % data.get('name'))

        # O schema do CLI: `claude plugin eval` recusa a carga fora dele, e o
        # caso nao roda. Ver ARCHITECTURE.md, "Schema dos casos de eval".
        check('%s: schema_version e 1.1' % case,
              data.get('schema_version') == '1.1',
              'diz %r — 1.0 nao carrega mais' % data.get('schema_version'))

        execution = data.get('execution')
        check('%s: tem bloco execution' % case, isinstance(execution, dict),
              'prompt e max_turns vivem dentro de execution no schema 1.1')
        if isinstance(execution, dict):
            check('%s: execution.prompt preenchido' % case,
                  bool(execution.get('prompt')))
            check('%s: execution.max_turns definido' % case,
                  bool(execution.get('max_turns')))

        check('%s: prompt nao ficou no topo' % case, 'prompt' not in data,
              'prompt no topo e schema 1.0 — mover para execution')

        graders = data.get('graders') or []
        check('%s: tem grader' % case, bool(graders))

        vistos = set()
        for i, grader in enumerate(graders):
            nome = grader.get('name')
            check('%s: grader %d tem name' % (case, i), bool(nome),
                  'name e obrigatorio em cada grader')
            check('%s: grader %r nao repete' % (case, nome),
                  nome not in vistos)
            vistos.add(nome)
            check('%s: grader %r sem with_only' % (case, nome),
                  'with_only' not in grader,
                  'with_only saiu do schema — tool_used: Skill ja e indicador')
            if grader.get('type') == 'llm':
                check('%s: grader %r tem criteria' % (case, nome),
                      bool(grader.get('criteria')))

        scoring = [g for g in graders if g.get('type') != 'tool_used']
        check('%s: tem grader que pontua' % case, bool(scoring),
              'so indicadores with-only — o caso nao mede nada')


def test_public_hygiene():
    print('\nhigiene de repositorio publico')
    leaks = {
        'caminho absoluto de maquina':
            re.compile(r'[A-Z]:' + BS + r'{1,2}[A-Za-z]|[A-Z]:/(?:Users|Fabio)'),
        'endereco de e-mail pessoal':
            re.compile(r'[\w.+-]+@(?:gmail|hotmail|outlook)\.com'),
        # caminho do vault do autor; use ${BKS_VAULT}. README documenta o valor da
        # variavel; JOURNAL e docs/handoff/ sao historico
        'caminho do vault em vez de BKS_VAULT':
            re.compile('[A-Z]:[/' + BS + BS + ']{1,2}2brains'),
    }
    exempt = {'caminho do vault em vez de BKS_VAULT': ('README.md', 'JOURNAL.md', 'docs/handoff/')}
    found = dict((k, []) for k in leaks)

    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'results', '__pycache__')]
        for f in files:
            if not f.endswith(('.md', '.json', '.py', '.yaml', '.yml')):
                continue
            path = os.path.join(base, f)
            rel = os.path.relpath(path, ROOT).replace(BS, '/')
            if rel.startswith('tests/'):
                continue
            try:
                with io.open(path, encoding='utf-8') as fh:
                    text = fh.read()
            except Exception:
                continue
            for label, rx in leaks.items():
                if any(rel == e or (e.endswith('/') and rel.startswith(e))
                       for e in exempt.get(label, ())):
                    continue
                if rx.search(text):
                    found[label].append(rel)

    for label in sorted(leaks):
        hits = found[label]
        check('sem %s' % label, not hits, 'em: %s' % ', '.join(sorted(hits)))


old_agent_re = re.compile(r'`(?:bkhar:)?(?:planner|builder|reviewer)`|\|\s*(?:planner|builder|reviewer)\s*\|')


def test_team():
    print('\nequipe (Fase 3)')
    path = os.path.join(ROOT, 'skills', 'bks-team', 'SKILL.md')
    check('skills/bks-team/SKILL.md existe', os.path.isfile(path))
    team = read('skills', 'bks-team', 'SKILL.md') if os.path.isfile(path) else ''
    roles = ('architect', 'tester', 'developer', 'security', 'quality', 'scribe')
    absent = [r for r in roles if '`%s`' % r not in team]
    check('bks-team cita os seis papéis', not absent, 'faltando: %s' % ', '.join(absent))
    check('bks-team exige invocação separada e independente no painel',
          'invocação separada' in team and 'independente' in team)
    check('bks-team proíbe o Gerente de opinar sobre técnica', 'não opina sobre técnica' in team)
    check('bks-team: rito não grava estado', 'não grava estado' in team)
    check('bks-team para antes de gerar artefato', 'antes de qualquer passo que gere artefato' in team)

    sections = ('## Persona', '## Responsabilidades', '## Limites', '## Fontes obrigatórias',
                '## Perguntas obrigatórias', '## Skills que carrega', '## Aprendizado')
    profiles = {
        'architect': ('nunca escreve código de produção', 'adr'),
        'tester': ('red confirmado', 'learnings.md', 'não revisa os próprios testes'),
        'scribe': ('nunca afirma', 'evidência'),
        'developer': ('zona de contenção', 'nunca commita', 'nunca revisa o próprio código', 'red'),
        'security': ('arquivo:linha', 'crítica bloqueia', 'só lê'),
        'quality': ('learnings.md', 'só lê', 'arquivos de teste', 'linter'),
    }
    for role, musts in sorted(profiles.items()):
        path = os.path.join(ROOT, 'agents', role + '.md')
        check('agents/%s.md existe' % role, os.path.isfile(path))
        text = read('agents', role + '.md') if os.path.isfile(path) else ''
        missing = [s for s in sections if s not in text]
        check('%s: tem as sete seções do perfil' % role, not missing, 'faltando: %s' % ', '.join(missing))
        body = text.split('---', 2)[-1].lstrip()
        check('%s: primeira linha anuncia tier e ferramentas' % role,
              body.startswith('> Ao iniciar, diga em uma linha: `%s - ' % role))
        absent = [m for m in musts if m not in text.lower()]
        check('%s: regras duras do papel' % role, not absent, 'faltando: %s' % ', '.join(absent))

    commands = {
        'loop': ('passo 0', 'red confirmado', '`tester`', '`developer`', 'bloqueio-'),
        'review': ('`tester`', '`security`', '`quality`', 'não revisa os próprios testes',
                   'proposta de task'),
        'spec': ('`architect`', '`tester`', 'refinamento: não (exceção)'),
        'ask': ('architect', 'arquiteto', 'tester', 'testes', 'developer', 'dev', 'security',
                'seguranca', 'quality', 'qualidade', 'scribe', 'documentador', 'opinião'),
        'panel': ('independente', 'adr', 'descartadas', '`scribe`', 'invocação separada'),
        'refine': ('`architect`', '`tester`', '`security`', 'até três perguntas',
                   'refinamento: sim'),
    }
    for cmd in ('ask', 'panel', 'refine'):
        check('commands/%s.md existe' % cmd, os.path.isfile(os.path.join(ROOT, 'commands', cmd + '.md')))
    for cmd, musts in sorted(commands.items()):
        path = os.path.join(ROOT, 'commands', cmd + '.md')
        text = read('commands', cmd + '.md').lower() if os.path.isfile(path) else ''
        absent = [m for m in musts if m not in text]
        check('/bkhar:%s chama os papéis novos' % cmd, not absent, 'faltando: %s' % ', '.join(absent))
        old = [a for a in ('`planner`', '`builder`', '`reviewer`') if a in text]
        check('/bkhar:%s não cita agente antigo' % cmd, not old, 'cita: %s' % ', '.join(old))

    manual = read('docs', 'artefatos', 'manual', 'manual-comandos.md')
    cmds = set(os.path.splitext(f)[0] for f in listdir('commands') if f.endswith('.md'))
    no_block = sorted(c for c in cmds if '### `/bkhar:%s`' % c not in manual)
    check('o manual tem um bloco por comando', not no_block, 'sem bloco: %s' % ', '.join(no_block))

    atlas = read('docs', 'artefatos', 'atlas', 'atlas-bks-harness.md')
    body = atlas.split('### F. Histórico de versões')[0]
    check('Atlas não promete o atalho @agente', '`@<agente>`' not in body and '`@agente`' not in body.replace('O `@agente` no prompt não chama agente', ''))
    check('Atlas aponta os checklists para skills/bks-team/', 'agents/references/' not in body)
    proposed = [c for c in ('refine', 'panel', 'ask')
                if re.search(r'\|\s*`/bkhar:%s[^|]*\|.*\|\s*Proposto\s*\|' % c, body)]
    check('Atlas dá ask, panel e refine como existentes', not proposed, 'ainda propostos: %s' % ', '.join(proposed))

    slides = ('docs', 'artefatos', 'apresentacao', 'slides')
    cmds_slide = read(*(slides + ('comandos.html',)))
    rite_row = re.search(r'<tr>(?:(?!</tr>).)*/bkhar:refine(?:(?!</tr>).)*</tr>', cmds_slide)
    check('slide comandos dá os ritos como existentes',
          bool(rite_row) and 'Proposto' not in rite_row.group(0) and ':ask' in rite_row.group(0))
    repo_slide = read(*(slides + ('manual-repo.html',)))
    absent = [c for c in ('/bkhar:refine', '/bkhar:ask', ':panel') if c not in repo_slide]
    check('slide manual-repo cita os comandos de rito', not absent, 'faltando: %s' % ', '.join(absent))
    stale = [f for f in ('roteamento.html', 'conceitos.html', 'equipe.html')
             if re.search(r'planner hoje|reviewer hoje|reviewer\.vendor|reviewer sempre roda', read(*(slides + (f,))))]
    check('slides sem os agentes antigos como estado atual', not stale, 'em: %s' % ', '.join(stale))

    readme = read('README.md')
    check('README lista a skill bks-team', '| `bks-team` |' in readme)
    check('README não cita agente antigo', not old_agent_re.search(readme))
    arch = read('docs', 'ARCHITECTURE.md')
    check('ARCHITECTURE registra a equipe da Fase 3',
          '### A equipe conversa' in arch and 'protocolo da sessão principal' in arch)
    for manifest in ('plugin.json', 'marketplace.json'):
        check('%s em 0.9.0' % manifest, '"version": "0.9.0"' in read('.claude-plugin', manifest))

    left = [a for a in ('planner', 'builder', 'reviewer')
            if os.path.isfile(os.path.join(ROOT, 'agents', a + '.md'))]
    check('agentes antigos removidos de agents/', not left, 'ainda existem: %s' % ', '.join(left))
    roles = set(('architect', 'tester', 'developer', 'security', 'quality', 'scribe'))
    present = set(os.path.splitext(f)[0] for f in listdir('agents') if f.endswith('.md'))
    check('agents/ tem só os seis papéis', present == roles, 'encontrados: %s' % ', '.join(sorted(present)))

    cites = []
    for top in ('templates', 'profiles', 'skills'):
        for base, _, files in os.walk(os.path.join(ROOT, top)):
            for f in files:
                if f.endswith('.md'):
                    rel = os.path.relpath(os.path.join(base, f), ROOT).replace(BS, '/')
                    with io.open(os.path.join(base, f), encoding='utf-8') as fh:
                        if old_agent_re.search(fh.read()):
                            cites.append(rel)
    check('templates, perfis e skills não citam agente antigo', not cites, 'em: %s' % ', '.join(sorted(cites)))

    learn = os.path.join(ROOT, 'templates', 'project-skeleton', 'LEARNINGS.md')
    check('template LEARNINGS.md existe', os.path.isfile(learn))
    learn_text = read('templates', 'project-skeleton', 'LEARNINGS.md').lower() if os.path.isfile(learn) else ''
    fields = ('tags', 'sintoma', 'causa', 'teste que teria pegado', 'evidência')
    absent = [f for f in fields if f not in learn_text]
    check('LEARNINGS.md tem os campos do caso', not absent, 'faltando: %s' % ', '.join(absent))
    save = read('commands', 'save.md').lower()
    absent = [m for m in ('learnings.md', '### aprendizados', 'sem evidência') if m not in save]
    check('/bkhar:save grava aprendizados e LEARNINGS.md', not absent, 'faltando: %s' % ', '.join(absent))
    check('template FEAT.md tem o campo Refinamento', 'Refinamento:' in read('templates', 'FEAT.md'))

    checklists = ('planning-checklist.md', 'planning-anti-patterns.md',
                  'code-review-checklist.md', 'code-review-anti-patterns.md')
    check('agents/references/ não existe', not os.path.isdir(os.path.join(ROOT, 'agents', 'references')))
    moved = set(listdir('skills', 'bks-team', 'references'))
    check('os quatro checklists estão em skills/bks-team/references/',
          set(checklists) <= moved, 'faltando: %s' % ', '.join(sorted(set(checklists) - moved)))


def main():
    print('suite estrutural do bks-harness')
    for fn in (test_manifests, test_skills, test_commands, test_pointers,
               test_agents,
               test_hooks, test_invariants, test_profiles, test_renderers,
               test_evals, test_public_hygiene, test_team):
        fn()

    print('\n%d verificacoes, %d falhas' % (checks, len(failures)))
    if failures:
        print('\nfalharam:')
        for f in failures:
            print('  - %s' % f)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
