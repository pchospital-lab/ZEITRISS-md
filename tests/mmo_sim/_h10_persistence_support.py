#!/usr/bin/env python3
"""H10 test-local observer/injector at the real dispatcher boundary.

Only the selected synthetic absolute Path.write_text/os.replace is intercepted.
No kernel lock, product function, return code or exception handler is replaced.
The real dispatcher runs with its real exception/finally semantics. Full byte
snapshots are evidence, not a new product authority or a repair mechanism.
"""
from __future__ import annotations
import argparse,base64,datetime,hashlib,json,os,runpy,sys,traceback
from pathlib import Path


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def raw(path):
    if not path.is_file(): return None
    b=path.read_bytes()
    return {'sha256':hashlib.sha256(b).hexdigest(),'bytes_b64':base64.b64encode(b).decode(),'size':len(b)}


def inventory(root,names):
    out={}
    for name in names:
        base=root/name
        for f in ([base] if base.is_file() else sorted(base.rglob('*')) if base.is_dir() else []):
            if f.is_file():out[f.relative_to(root).as_posix()]=raw(f)
    return out


def _snapshot(root):
    return inventory(root,['states','participants','onboarding','catalog','run/community',
        'run/communities','run/current_saves','run/completion','run/tables','run/locks.json','run/reflections.jsonl'])


def snapshot(root):
    return {'protected':_snapshot(root),'run_files':inventory(root,['run']),
            'status':raw(root/'run/lab.status.json'),'stop':raw(root/'run/lab.stop'),
            'requests':inventory(root,['run/requests'])}


def vector(status):
    return {k:status.get(k) for k in ('turns_used','usd_spent','seconds_elapsed','usd_unknown_turns',
       'reconciled_request_ids','reconciled_seconds_request_ids','provider_free')}


def save(path,data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('source','root','case'):ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--fault',choices=('none','start-before','start-after','release-before','release-after','stop-before','stop-partial','window-before','window-after'),default='none')
    ap.add_argument('--timing',choices=('before','after')) # original T7/T8 helper interface
    ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    source=a.source.resolve();root=a.root.resolve();out=a.case.resolve();out.mkdir(parents=True,exist_ok=True)
    fault='window-'+a.timing if a.timing else a.fault
    sys.path.insert(0,str(source));expected=(root/'guard/sitecustomize.py').resolve()
    proof={'pid':os.getpid(),'ppid':os.getppid(),'utc':now(),'interpreter':sys.executable,'command':cmd,
           'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fault':fault}
    try:
        import socket,sitecustomize,jsonschema
        actual=Path(sitecustomize.__file__).resolve()
        assert actual==expected and socket.getaddrinfo.__module__=='sitecustomize','GUARD_NOT_BOUND'
        jsonschema.validate({}, {'type':'object'})
        from mmo_sim.core import persona_state
        assert persona_state.jsonschema is jsonschema,'SCHEMA_NOT_BOUND_IN_PRODUCT'
        proof.update(guard=str(actual),guard_sha256=hashlib.sha256(actual.read_bytes()).hexdigest(),
                     jsonschema_file=jsonschema.__file__,schema_bound=True,functional_validate_ok=True)
    except (ImportError,AssertionError) as exc:
        proof.update(status='BLOCKED_BEFORE_FUNCTIONAL_ENTRY',error=repr(exc),schema_bound=False)
        save(out/'BLOCKED.json',proof);raise SystemExit(97)
    save(out/'child-entry.json',proof)
    original_replace=os.replace;original_write=Path.write_text;hits=[]
    targets={'start':root/'run/lab.status.json','release':root/'run/lab.status.json',
             'stop':root/'run/lab.stop','window':root/'run/lab.last_window.json'}
    def hit(target,intended,before,after,stack,systemcall_ran):
        row={'hit':1,'pid':os.getpid(),'utc':now(),'target':str(target),'fault':fault,
             'timing':fault.rsplit('-',1)[-1],'wrapper_sha256':proof['wrapper_sha256'],
             'stack':[{'file':f.filename,'line':f.lineno,'function':f.name} for f in stack],
             'before':before,'after':after,'protected':before['protected'],
             'intended_b64':base64.b64encode(intended).decode(),'target_after_b64':
               base64.b64encode(target.read_bytes()).decode() if target.is_file() else None,
             'real_systemcall_completed':systemcall_ran}
        hits.append(row);save(out/'fault-hit.json',row)
    def replace(src,dst,*args,**kw):
        group=fault.split('-')[0];stack=traceback.extract_stack()
        if group in ('start','release') and not hits and Path(dst).resolve()==targets[group] and any(f.name==group and Path(f.filename).name=='runner.py' for f in stack):
            target=targets[group];before=snapshot(root);intended=Path(src).read_bytes();done=False
            if fault.endswith('after'):original_replace(src,dst,*args,**kw);done=True
            hit(target,intended,before,snapshot(root),stack,done)
            raise OSError('H10_PERSISTENCE_'+fault.upper().replace('-','_'))
        return original_replace(src,dst,*args,**kw)
    def write(self,data,*args,**kw):
        group=fault.split('-')[0];stack=traceback.extract_stack()
        match=group in ('stop','window') and not hits and self.resolve()==targets[group]
        if group=='window' and match:match=json.loads(data).get('kind')=='section_completed'
        if match:
            target=targets[group];before=snapshot(root);intended=data.encode(kw.get('encoding') or 'utf-8');done=False
            if fault.endswith('after'):original_write(self,data,*args,**kw);done=True
            elif fault=='stop-partial':
                with target.open('wb') as f:f.write(intended[:max(1,len(intended)//2)]);f.flush()
            hit(target,intended,before,snapshot(root),stack,done)
            # Existing explicit synthetic sensitivity probe. Off for normal cases.
            if group=='window' and os.environ.get('MMO_SIM_H10_SENSITIVITY_PROBE')=='1':
                p=root/'states/tech.json';d=json.loads(p.read_text());d['rounds_played']+=7
                original_write(p,json.dumps(d),encoding='utf-8')
            raise OSError('H10_PERSISTENCE_'+fault.upper().replace('-','_'))
        return original_write(self,data,*args,**kw)
    os.replace=replace;Path.write_text=write
    sys.argv=[str(source/'scripts/mmo_sim.py'),'lab',*cmd]
    try:runpy.run_path(sys.argv[0],run_name='__main__')
    finally:
        os.replace=original_replace;Path.write_text=original_write
        save(out/'child-exit-observation.json',{'pid':os.getpid(),'utc':now(),'hits':len(hits),
          'protected':_snapshot(root),'snapshot':snapshot(root),
          'schema_bound':persona_state.jsonschema is jsonschema})

if __name__=='__main__':main()
