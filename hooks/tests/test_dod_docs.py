import json, os, subprocess, sys, tempfile, shutil
H = os.path.abspath('hooks/scripts')

def run(payload):
    r = subprocess.run([sys.executable, os.path.join(H, 'dod_docs.py')],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=25)
    out = r.stdout.strip()
    if not out: return 'ALLOW', ''
    d = json.loads(out).get('hookSpecificOutput', {})
    return d.get('permissionDecision','ALLOW').upper(), d.get('permissionDecisionReason','')

def g(a, cwd): subprocess.run(['git']+a, cwd=cwd, capture_output=True, text=True)

tmp = tempfile.mkdtemp()
try:
    g(['init','-q'], tmp); g(['config','user.email','t@t'], tmp); g(['config','user.name','t'], tmp)
    for f in ('README.md','ARCHITECTURE.md'):
        open(os.path.join(tmp,f),'w').write('# doc\n')
    os.makedirs(os.path.join(tmp,'src'))
    open(os.path.join(tmp,'src','Old.cs'),'w').write('public class Old {}\n')
    g(['add','-A'], tmp); g(['commit','-qm','init'], tmp)

    cs = os.path.join(tmp,'src','New.cs')
    pub = {'tool_name':'Write','tool_input':{'file_path':cs,'content':'public sealed class New {}\n'}}
    priv = {'tool_name':'Write','tool_input':{'file_path':cs,'content':'internal class New {}\n'}}

    cases=[]
    cases.append(('tipo publico, docs limpas -> DENY', run(pub)[0], 'DENY'))
    cases.append(('tipo internal, docs limpas -> ALLOW', run(priv)[0], 'ALLOW'))

    open(os.path.join(tmp,'README.md'),'a').write('\nmudou\n')
    cases.append(('so README tocado -> DENY', run(pub)[0], 'DENY'))

    open(os.path.join(tmp,'ARCHITECTURE.md'),'a').write('\nmudou\n')
    cases.append(('README+ARCHITECTURE tocados -> ALLOW', run(pub)[0], 'ALLOW'))

    tst = os.path.join(tmp,'src','App.Tests','NewTests.cs')
    os.makedirs(os.path.dirname(tst))
    g(['checkout','--','README.md','ARCHITECTURE.md'], tmp)
    tp = {'tool_name':'Write','tool_input':{'file_path':tst,'content':'public class NewTests {}\n'}}
    cases.append(('arquivo de teste -> ALLOW', run(tp)[0], 'ALLOW'))

    out = {'tool_name':'Write','tool_input':{'file_path':os.path.join(tempfile.gettempdir(),'nogit','X.cs'),'content':'public class X {}\n'}}
    cases.append(('fora de repo git -> ALLOW', run(out)[0], 'ALLOW'))

    fail=0
    for name,got,exp in cases:
        ok = got==exp; fail += (not ok)
        print('%-5s %-40s esperado=%-5s obtido=%s' % ('OK' if ok else 'FALHA', name, exp, got))
    print('\nfalhas:', fail)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
