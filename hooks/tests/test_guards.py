import json, subprocess, sys, os
H = 'hooks/scripts'

def run(script, payload):
    r = subprocess.run([sys.executable, os.path.join(H, script)],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=20)
    out = r.stdout.strip()
    if not out:
        return 'ALLOW', ''
    try:
        d = json.loads(out)
        h = d.get('hookSpecificOutput', {})
        return h.get('permissionDecision', 'ALLOW').upper(), h.get('permissionDecisionReason', '')
    except Exception:
        return 'PARSE-FAIL', out[:200]

def w(path, content):
    return {'tool_name': 'Write', 'tool_input': {'file_path': path, 'content': content}}

cases = [
 ('no_dispatcher', 'MediatR bloqueia', w('C:/x/src/Handler.cs', 'using MediatR;\npublic class A {}'), 'DENY'),
 ('no_dispatcher', 'IMediator bloqueia', w('C:/x/src/S.cs', 'public class S { private readonly IMediator _m; }'), 'DENY'),
 ('no_dispatcher', 'pipeline passa', w('C:/x/src/S.cs', 'public class S { private readonly PipelineOrchestrator _p; }'), 'ALLOW'),
 ('no_dispatcher', 'md ignora', w('C:/x/README.md', 'using MediatR;'), 'ALLOW'),

 ('comment_budget', 'bloco 7 linhas bloqueia',
   w('C:/x/src/A.cs', 'public class A {\n' + '\n'.join('    // linha %d' % i for i in range(7)) + '\n}'), 'DENY'),
 ('comment_budget', 'bloco 4 linhas passa',
   w('C:/x/src/A.cs', 'public class A {\n' + '\n'.join('    // linha %d' % i for i in range(4)) + '\n}'), 'ALLOW'),
 ('comment_budget', 'severidade bloqueia',
   w('C:/x/src/A.cs', 'public class A {\n    // \U0001F534 cuidado\n}'), 'DENY'),
 ('comment_budget', 'bloco /* */ 8 linhas bloqueia',
   w('C:/x/src/A.cs', 'public class A {\n    /*\n' + '\n'.join('     * l%d' % i for i in range(6)) + '\n     */\n}'), 'DENY'),
 ('comment_budget', 'xmldoc 3 linhas passa',
   w('C:/x/src/A.cs', '/// <summary>\n/// Faz X.\n/// </summary>\npublic class A {}'), 'ALLOW'),
]
fail = 0
for script, name, payload, expect in cases:
    got, reason = run(script + '.py', payload)
    ok = got == expect
    fail += (not ok)
    print('%-4s %-34s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, expect, got))
    if not ok and reason:
        print('       ', reason.splitlines()[0][:110])
print('\nfalhas:', fail)
