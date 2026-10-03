#!/usr/bin/env python3
"""A23-only subprocess/evidence helpers. No runtime logic or product writes.

The registry association is an explicit synthetic fixture step, performed while
TUI is waiting after the real import and before any preflight decision. The test
then reads full authority snapshots; it never manufactures a game completion.
"""
from __future__ import annotations
import base64
import contextlib
import hashlib
import json
import os
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
sys.path[:0] = [str(_REPO_ROOT), str(_HERE)]
import _h02_vollreise_support as sup
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.core import store
from mmo_sim.registry.participants import ApplicationRecordRef, ParticipantRegistry
MMO_SIM = sup.MMO_SIM


def higher_level_human_save(char_id='CHR-A23-HUMAN-001', name='A23Operator', callsign='A23OPS', level=5):
    return {'v':7, 'save_id':f'fixture-{char_id.lower()}-initial-001',
            '_fixture_note':'SIMULIERT/FIXTURE (A23-Vorlauf-Test, menschlicher Import)',
            'characters':[{'char_id':char_id,'id':char_id,'name':name,'callsign':callsign,'level':level}]}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path, dest: Path) -> dict:
    """Full bytes, precise collection interval and hashes; only own test data."""
    start = time.time()
    dest.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in ('states','run','onboarding','catalog','participants'):
        source = root/name
        if not source.exists():
            continue
        for path in sorted(source.rglob('*')):
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                data = path.read_bytes()
                target = dest/rel; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data); hashes[rel] = sha(data)
    value = {'started_utc':start,'ended_utc':time.time(),'hashes':hashes}
    sup.write_json(dest/'SNAPSHOT.json', value)
    return value


def protected(hashes: dict, *, players=()) -> dict:
    """Player progress may change; all other states/currents/identities must not."""
    result = {}
    for p,h in hashes.items():
        if p.startswith(('states/','catalog/','onboarding/','participants/','run/current_saves/','run/community/')):
            if p.startswith('states/') and any(p == f'states/{pk}.json' for pk in players):
                continue
            if p.startswith('run/current_saves/') and any(Path(p).name==pk+'.json' or Path(p).name.startswith(pk+'__') or '/'+pk+'__versions/' in p for pk in players):
                continue
            result[p]=h
    return result


def lab_authorities(hashes):
    return {p:h for p,h in hashes.items() if p.startswith('run/')}


def attach_imported_human(root: Path, pid: str) -> None:
    """Explicit registry fixture through existing API, no assertion of UI auto-link."""
    registry = ParticipantRegistry(root/'participants')
    human = registry.load_participant(pid)
    if human is None:  # Backward compatibility for the existing read-only guard repro.
        return
    ps = PersonaStateStore(schema_path=sup._SCHEMA)
    current = store.load_current_save_or_raise(root/'run',pid,ps,states_dir=root/'states')
    assert current is not None, 'human import did not publish a real Current'
    char_id = current['characters'][0]['char_id']
    registry.add_record_ref(pid, ApplicationRecordRef(record_id=char_id,schema='zeitriss-v7',version='7',owner_participant_id=pid,source='extern importiert'))
    p=registry.load_participant(pid)
    assert p.kind=='human' and any(r.record_id==char_id and r.owner_participant_id==pid for r in p.record_refs)


# Observer appended ONLY to a newly generated test-local guard, never a product
# method. It records actual TUI/Lab PIDs and actual Popen results after completion.
_OBSERVER = r'''
import atexit as _a, base64 as _b, hashlib as _h, json as _j, os as _o
import pathlib as _p, subprocess as _sp, sys as _s, time as _t
_a23_started = _t.time()
_a23_dir = _p.Path(__A23_AUDIT_DIR__)
_a23_dir.mkdir(parents=True, exist_ok=True)
def _a23_write(name, rec):
    with (_a23_dir/name).open('a',encoding='utf-8') as f: f.write(_j.dumps(rec,ensure_ascii=False)+'\n')
def _a23_exit():
    m=_s.modules.get('mmo_sim.core.persona_state')
    _a23_write('children.jsonl',{'pid':_o.getpid(),'ppid':_o.getppid(),'argv':_s.argv,
      'executable':_s.executable,'cwd':_o.getcwd(),'started_utc':_a23_started,'ended_utc':_t.time(),
      'state_module_loaded':m is not None,'jsonschema_bound':m is not None and getattr(m,'jsonschema',None) is not None,
      'guard_file':__file__,'guard_sha256':_h.sha256(_p.Path(__file__).read_bytes()).hexdigest(),
      'environment':{k:_o.environ.get(k) for k in ('HOME','TMPDIR','PYTHONPATH','PYTHONNOUSERSITE')}})
_a.register(_a23_exit)
_a23_init = _sp.Popen.__init__
_a23_communicate = _sp.Popen.communicate
def _a23_popen_init(self,*args,**kw):
    self._a23_start=_t.time()
    _a23_init(self,*args,**kw)
    _a23_write('spawns.jsonl',{'pid':self.pid,'ppid':_o.getpid(),'argv':self.args,'cwd':kw.get('cwd',_o.getcwd()),'started_utc':self._a23_start})
def _a23_popen_communicate(self,*args,**kw):
    result=_a23_communicate(self,*args,**kw)
    if not getattr(self,'_a23_recorded',False):
      self._a23_recorded=True
      def enc(value):
        if value is None:return None
        data=value.encode('utf-8') if isinstance(value,str) else value
        return {'b64':_b.b64encode(data).decode(),'sha256':_h.sha256(data).hexdigest(),'bytes':len(data),
                'capture':'text-mode UTF-8 re-encoding' if isinstance(value,str) else 'raw pipe bytes'}
      _a23_write('process-results.jsonl',{'pid':self.pid,'ppid':_o.getpid(),'argv':self.args,
        'returncode':self.returncode,'started_utc':self._a23_start,'ended_utc':_t.time(),
        'stdout':enc(result[0]),'stderr':enc(result[1])})
    return result
_sp.Popen.__init__=_a23_popen_init
_sp.Popen.communicate=_a23_popen_communicate
'''


def _environment(root, guard_dir, env_extra, require_schema_dependency):
    dependency = None; manifest = {}
    if require_schema_dependency:
        dependency,manifest=sup.copy_dependency_visibility(root/'schema-dependency-visibility')
    env=sup.minimal_lab_env(env_extra or {},tmp_root=root,guard_dir=guard_dir,schema_dependency_dir=dependency)
    # Guard identity checked before any child product execution.
    check=subprocess.run([sys.executable,'-B','-c',
        "import sys,pathlib,sitecustomize,socket; assert pathlib.Path(sitecustomize.__file__).resolve()==pathlib.Path(sys.argv[1]).resolve(); assert socket.getaddrinfo.__module__=='sitecustomize'",str(guard_dir/'sitecustomize.py')],env=env,cwd=_REPO_ROOT,stdin=subprocess.DEVNULL,capture_output=True,timeout=10)
    assert check.returncode==0, 'A23_GUARD_BLOCKED: '+check.stderr.decode('utf-8','replace')
    proof=None
    if require_schema_dependency:
        proof=sup.probe_schema_dependency(env);proof['dependency_visibility_manifest']=manifest
        assert proof.get('available') is True and proof.get('functional_validate_ok') is True, f'A23_SCHEMA_BLOCKED: {proof}'
    return env,proof


def run_tui(stdin_lines, *, participant_id, data_dir, env_extra=None, timeout=60,
            tmp_root=None, guard_dir=None, require_schema_dependency=False,
            case=None, steps=None, link_human=False):
    """Real dispatcher with optional real prompt checkpoints, never direct TuiSession.

    steps: (lines, expected prompt or None, snapshot label or None). At the
    import checkpoint the real TUI is blocked on its next stdin read. No model
    decisions have been sent. None prompt sends the remaining input and EOF.
    """
    root=tmp_root or Path(tempfile.mkdtemp(prefix='a23-child-'))
    root.mkdir(parents=True,exist_ok=True)
    guard_dir=guard_dir or sup.write_loopback_guard(root/'guard')
    if case is not None:
        case.mkdir(parents=True,exist_ok=False)
        # Each run gets its own guard clone. Existing H02 guard bytes untouched.
        copied=root/'observed-guard';shutil.copytree(guard_dir,copied)
        with (copied/'sitecustomize.py').open('a') as f:
            f.write(_OBSERVER.replace('__A23_AUDIT_DIR__',repr(str(case/'process-audit'))))
        guard_dir=copied
    env,proof=_environment(root,guard_dir,env_extra,require_schema_dependency)
    argv=[sys.executable,'-B','-u',str(MMO_SIM),'--participant',participant_id,'--data-dir',str(data_dir)]
    started=time.time();out=b'';err=b'';sent=b'';snapshots={};timed_out=False
    if case is not None:snapshots['before-ui']=snapshot(data_dir,case/'before-ui')
    proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          cwd=_REPO_ROOT,env=env)
    sel=selectors.DefaultSelector();sel.register(proc.stdout,selectors.EVENT_READ,'stdout');sel.register(proc.stderr,selectors.EVENT_READ,'stderr')
    deadline=time.monotonic()+timeout
    def pump(until=None,offset=0):
        nonlocal out,err
        while True:
            if until is not None and until.encode() in out[offset:]:return
            if not sel.get_map():
                if until is not None:raise AssertionError('A23_PROMPT_NOT_REACHED: '+until+'\n'+out.decode('utf8','replace')+err.decode('utf8','replace'))
                return
            if time.monotonic()>deadline:raise subprocess.TimeoutExpired(argv,timeout)
            for key,_ in sel.select(min(0.1,max(0,deadline-time.monotonic()))):
                data=os.read(key.fd,65536)
                if not data:sel.unregister(key.fileobj);continue
                if key.data=='stdout':out+=data
                else:err+=data
    schedule=steps if steps is not None else [(stdin_lines,None,None)]
    try:
        for lines,prompt,label in schedule:
            offset=len(out)
            data=('\n'.join(lines)+'\n').encode() if lines else b''
            if data:proc.stdin.write(data);proc.stdin.flush();sent+=data
            if prompt is not None:
                pump(prompt,offset)
                if label:
                    if label=='post-import' and link_human:attach_imported_human(data_dir,participant_id)
                    snapshots[label]=snapshot(data_dir,case/label)
            else:
                proc.stdin.close();pump();break
        proc.wait(timeout=max(1,deadline-time.monotonic()))
    except subprocess.TimeoutExpired:
        timed_out=True;proc.kill();proc.wait(timeout=10);raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=10)
        sel.close()
        if case is not None:
            (case/'stdout.bin').write_bytes(out);(case/'stderr.bin').write_bytes(err);(case/'stdin.bin').write_bytes(sent)
            sup.write_json(case/'invocation.json',{'pid':proc.pid,'ppid':os.getpid(),'argv':argv,'cwd':str(_REPO_ROOT),
                'started_utc':started,'ended_utc':time.time(),'returncode':proc.returncode,'timeout':timed_out,
                'environment':env,'stdin_sha256':sha(sent),'stdout_sha256':sha(out),'stderr_sha256':sha(err),
                'schema_dependency_proof':proof})
            snapshots['after-ui']=snapshot(data_dir,case/'after-ui')
        for stream in (proc.stdin,proc.stdout,proc.stderr):
            if stream and not stream.closed:stream.close()
    p=subprocess.CompletedProcess(argv,proc.returncode,out.decode('utf8'),err.decode('utf8'))
    p._a23_pid=proc.pid;p._a23_started_utc=started;p._a23_ended_utc=time.time();p._a23_cwd=str(_REPO_ROOT)
    p._a23_stdin=sent.decode();p._a23_schema_dependency_proof=proof;p._a23_snapshots=snapshots;p._a23_case=case
    return p


def log_tui_invocation(case,name,env_extra,proc):
    sup.append_jsonl(case/'invocations.json',{'name':name,'argv':list(proc.args),'pid':proc._a23_pid,
       'started_utc':proc._a23_started_utc,'ended_utc':proc._a23_ended_utc,'cwd':proc._a23_cwd,
       'env_extra':env_extra,'returncode':proc.returncode,'stdin':proc._a23_stdin})
    (case/f'stdout.{name}.txt').write_text(proc.stdout);(case/f'stderr.{name}.txt').write_text(proc.stderr)
    if proc._a23_schema_dependency_proof is not None:
        sup.write_json(case/f'schema-dependency-proof.{name}.json',proc._a23_schema_dependency_proof)
