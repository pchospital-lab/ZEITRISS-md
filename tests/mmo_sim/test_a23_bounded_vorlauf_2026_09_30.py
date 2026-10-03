#!/usr/bin/env python3
"""A23 V1-V5: real TUI entry, explicit import boundary, full evidence.
Existing H02/H05 helpers are reused unchanged. Five existing contract groups,
no new game/fault matrix. Human registration is an explicit test fixture.
"""
from __future__ import annotations
import base64
import contextlib
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
_HERE=Path(__file__).resolve().parent
_REPO_ROOT=_HERE.parents[1]
sys.path[:0]=[str(_REPO_ROOT),str(_HERE)]
import _a23_vorlauf_support as a23sup
import _h02_vollreise_support as sup
import test_h02_vollreise_profiles_2026_09_28 as h02
from mmo_sim.core import store as core_store, request_ledger
from mmo_sim.core.admission import write_test_profile
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.lab import runner as lab_runner
from mmo_sim.registry.participants import ParticipantRegistry
from mmo_sim.ui.tui import TuiSession  # kept for the historical repro, never called by new V1/V2
_SCHEMA_PATH=sup._SCHEMA


def _fixture(root,label,community=True):
    human=sup.register_human_participant(root/'participants','SYNTHETIC-A23-'+label)
    pid=human.participant_id
    if community:
        sup.bootstrap_six_persona_community(root,'community-'+pid)
        for pk in sup.SIX_PERSONAS:sup.make_ready(root/'onboarding',root/'states',root/'run',pk)
    write_test_profile(root/'run',max_usd=5.0)
    return pid


@contextlib.contextmanager
def _traps(case):
    case.mkdir(parents=True,exist_ok=True)
    with sup.recording_http_server([],receipts_path=case/'trap-persona.jsonl',label='a23-no-persona') as p, sup.recording_http_server([],receipts_path=case/'trap-gm.jsonl',label='a23-no-gm') as g:
        env={'MMO_SIM_PERSONA_API_BASE_URL':p.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-A23-NOT-A-KEY',
             'MMO_SIM_PERSONA_API_MODEL':'synthetic-a23','OPENWEBUI_URL':g.base_url,'OPENWEBUI_API_KEY':'SYNTH-A23-NOT-A-KEY',
             'MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096','MMO_SIM_LOBBY_INITIATIVE_LIMIT':'8'}
        yield p,g,env
        sup.write_json(case/'trap-counts.json',{'persona':len(p.calls),'gm':len(g.calls),'listening_during_case':True})


def _import_run(root,case,pid,save,tail,env,*,switch=False,confirm=False):
    prefix=['i',json.dumps(save),'ENDE']+(['w'] if switch else [])
    steps=[(prefix,'Wahl [w/v/s]: ','post-import')]
    if confirm:
        # tail includes v/profile/selection/five limits, then ja/nein/EOF and exit.
        steps.append((tail[:8],'Vorlauf jetzt wirklich starten? [ja/nein]: ','before-confirmation'))
        steps.append((tail[8:],None,None))
    else:steps.append((tail,None,None))
    p=a23sup.run_tui(prefix+tail,participant_id=pid,data_dir=root,env_extra=env,
       timeout=150,tmp_root=root/('kid-'+a23sup.sha(str(case).encode())[:12]),guard_dir=sup.write_loopback_guard(root/('guard-'+a23sup.sha(str(case).encode())[:12])),
       require_schema_dependency=True,case=case,steps=steps,link_human=True)
    a23sup.log_tui_invocation(case,case.name,env,p)
    assert p.returncode==0,p.stdout+p.stderr
    assert len(p._a23_snapshots['post-import']['hashes'])>0
    if confirm:
        assert p._a23_snapshots['post-import']['hashes']==p._a23_snapshots['before-confirmation']['hashes'], 'A23_CONFIG_WRITES_BEFORE_CONFIRMATION'
    return p


def _assert_no_preflight(p,persona,gm):
    assert not persona.calls and not gm.calls,'A23_UNAUTHORIZED_TRANSPORT'
    assert 'starte gemeinsamen Lab-Controller' not in p.stdout,'A23_UNAUTHORIZED_DISPATCH'
    assert p._a23_snapshots['post-import']['hashes']==p._a23_snapshots['after-ui']['hashes'],'A23_DEFAULT_AUTHORITY_CHANGED'
    _audit_processes(p._a23_case,0)


def test_v1_default_and_abort_paths_no_vorlauf_request_no_lab_authority():
    for label,tail in [('empty',['','x']),('w',['w','x']),('s',['s','x']),('eof',[]),
                       ('decline',['v','api','sniper,tech','64','240','5','1','300','nein','x']),
                       ('confirmation-eof',['v','api','sniper,tech','64','240','5','1','300'])]:
        case=sup.case_dir('A23_V1_'+label)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pid=_fixture(root,label);save=a23sup.higher_level_human_save()
            with _traps(case) as (ps,gm,env):
                p=_import_run(root,case/'import',pid,save,tail,env,confirm=label in ('decline','confirmation-eof'))
                _assert_no_preflight(p,ps,gm)
                assert 'erfahrener' in p.stdout
                # Real new dispatcher; identical import must not offer preflight again.
                if label=='w':
                    before=a23sup.snapshot(root,case/'before-restart')
                    q=a23sup.run_tui(['i',json.dumps(save),'ENDE','x'],participant_id=pid,data_dir=root,env_extra=env,
                      timeout=30,tmp_root=root/'kid-restart',guard_dir=sup.write_loopback_guard(root/'guard-restart'),
                      require_schema_dependency=True,case=case/'restart')
                    assert q.returncode==0 and 'Identischer Save bereits vorhanden' in q.stdout,q.stdout+q.stderr
                    assert 'Wahl [w/v/s]' not in q.stdout
                    assert before['hashes']==q._a23_snapshots['after-ui']['hashes'],'A23_NOOP_IMPORT_CHANGED_AUTHORITY'
                    assert not ps.calls and not gm.calls


def test_v2_negative_configuration_paths_abort_before_dispatch():
    cases=[('no-community',['v','x'],'keine bestehende bestaetigte Spielgemeinschaft',False),
      ('profile-empty',['v','','x'],'ungueltiges/fehlendes Profil',True),
      ('profile-wrong',['v','bad','x'],'ungueltiges/fehlendes Profil',True),
      ('selection-empty',['v','api','','x'],'keine Persona ausgewaehlt',True),
      ('selection-unknown',['v','api','ghost,sniper','x'],'unbekannte/nicht freie Personas',True),
      ('requests-nan',['v','api','sniper,tech','nan','x'],'ungueltige Budgetangabe fuer max_requests',True),
      ('seconds-nan',['v','api','sniper,tech','10','nan','x'],'ungueltige Budgetangabe fuer max_seconds',True),
      ('usd-inf',['v','api','sniper,tech','10','60','inf','x'],'ungueltige Budgetangabe fuer max_usd',True),
      ('idle-zero',['v','api','sniper,tech','10','60','1','0','x'],'ungueltige Budgetangabe fuer max_idle_windows',True),
      ('wall-negative',['v','api','sniper,tech','10','60','1','1','-5','x'],'ungueltige Budgetangabe fuer max_wall_seconds',True)]
    for label,tail,expected,community in cases:
        case=sup.case_dir('A23_V2_'+label)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pid=_fixture(root,label,community)
            with _traps(case) as (ps,gm,env):
                p=_import_run(root,case/'import',pid,a23sup.higher_level_human_save(),tail,env)
                assert expected in p.stdout,(label,p.stdout)
                _assert_no_preflight(p,ps,gm)


def _assert_full_journey_parity_both_profiles(
    case: Path, run_dir: Path, states_dir: Path, schema_path: Path, table_id: str, section_id: str, seq: list,
) -> dict:
    """R2-Nachzug (01_REVIEW_A23.md §R2: "V4 prueft ... keine vollstaendige
    eigene Save-/Runden-/Reflexions-/Versions-/Finalabschlusspruefung wie fuer
    BEIDE Profile verlangt" -- galt beim Review-Zeitpunkt ebenso fuer den V3-
    Umfang). Gemeinsamer Nachweis fuer V3 (API) UND V4 (Hybrid), ausschliesslich
    ueber vorhandene Leser (`h02._assert_full_journey_final_state`,
    `core_store.load_current_save_or_raise`, `PersonaStateStore.load_state`,
    `core_store._current_save_versions_dir`) -- keine zweite Store-Autoritaet.

    Deckt fuer BEIDE ausgewaehlten Personas (sniper, tech):
      * Tisch/Completion/Locks (via `h02._assert_full_journey_final_state`:
        `table.status=='closed'`, Leader, Mitglieder, `_read_locks(run_dir)=={}`).
      * Vollstaendiger eigener Endsave (`_h02_end_marker`, `save_id` != Start-
        Fixture) -- bereits vorhandene Pruefung, hier nur zentral aufgerufen.
      * GENAU EINE verbuchte Runde (`rounds_played==1`, woertlich aus dem
        eigenen `PersonaStateStore`-State gelesen -- exakt das Feld, das der
        gegebene 1->8-Reviewwrapper post-hoc veraendert; eine dauerhafte
        Assertion HIER schlaegt an diesem Nachlauf zwingend fehl).
      * Versionsinventar: Baseline plus GENAU EINE neue Current-Save-Version unter
        `current_saves/<pk>__versions/` (eine reale, neue Publikation je
        Persona in diesem Lauf, kein Ueberschreiben/Doppellauf).
      * Eigene Reflexion vorhanden (`last_reflection` nicht leer)."""
    summary = h02._assert_full_journey_final_state(case, run_dir, table_id, seq)
    ps_store = PersonaStateStore(schema_path=schema_path)
    parity: dict = {"table": summary, "personas": {}}
    for pk in h02.SELECTED:
        current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
        assert current is not None, f"kein veroeffentlichter Endsave fuer {pk}"
        assert current.get("_h02_end_marker") == f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}", current
        assert current.get("save_id") != sup.load_fixture_save(pk)["save_id"], (
            f"Current von {pk} ist bytegleich zur Start-Fixture geblieben"
        )
        state = ps_store.load_state(pk, states_dir=states_dir)
        rounds_played = state.get("rounds_played")
        assert rounds_played == 1, (
            f"R2: genau EINE verbuchte Runde fuer {pk} erwartet (dauerhafte Assertion, "
            f"kein Nachlauf darf dies unentdeckt lassen), tatsaechlich: {rounds_played}"
        )
        last_reflection = state.get("last_reflection")
        assert last_reflection, f"eigene Reflexion fuer {pk} fehlt (last_reflection leer/None)"
        # Versionsinventar: `sup.make_ready` (fuer ALLE sechs Personas VOR dem
        # Vorlauf aufgerufen) publiziert bereits genau EINE Baseline-Version
        # (0001) je Persona -- die echte Journey darf GENAU EINE weitere,
        # NEUE Version anhaengen (0002), kein Ueberschreiben, kein Doppellauf.
        versions_dir = core_store._current_save_versions_dir(run_dir / "current_saves", pk)
        version_files = sorted(versions_dir.glob("*.json")) if versions_dir.exists() else []
        assert len(version_files) == 2, (
            f"Versionsinventar fuer {pk}: Baseline (make_ready) + genau EINE neue Journey-Version "
            f"erwartet (2 gesamt), {len(version_files)} gefunden ({[p.name for p in version_files]})"
        )
        parity["personas"][pk] = {
            "current_save_id": current.get("save_id"), "rounds_played": rounds_played,
            "has_reflection": bool(last_reflection), "version_files": [p.name for p in version_files],
        }
    sup.write_json(case / "full-journey-parity.json", parity)
    return parity



def _classified(api=None,cli=None):
    result=[]
    for rec in (api if api is not None else cli)[1:]:
        if api is not None:
            m=rec['body']['messages'];system=m[0]['content'];user=m[1]['content']
        else:
            raw=rec['stdin'];system,_,user=raw[len('[SYSTEM]\n'):].partition('\n\n[USER]\n')
        pk=h02._identify_persona(system,user);assert pk is not None
        result.append({'pk':pk,'system':system,'user':user,'full':system+'\n'+user})
    return result


def _audit_processes(case,expected_labs):
    children=sup.read_jsonl(case/'process-audit/children.jsonl')
    labs=[x for x in children if len(x['argv'])>1 and x['argv'][1:3]==['lab','resume']]
    assert len(labs)==expected_labs,(expected_labs,children)
    invocation=json.loads((case/'invocation.json').read_text())
    for row in labs:
        assert row['ppid']==invocation['pid'] and row['jsonschema_bound'] is True
    tui=[x for x in children if x['pid']==invocation['pid']]
    assert len(tui)==1 and tui[0]['jsonschema_bound'] is True
    outputs=sup.read_jsonl(case/'process-audit/process-results.jsonl')
    for row in labs:
        match=[x for x in outputs if x['pid']==row['pid']]
        assert len(match)==1
        for key in ('stdout','stderr'):
            data=base64.b64decode(match[0][key]['b64']);assert a23sup.sha(data)==match[0][key]['sha256']
    return labs


def _journey(profile):
    case=sup.case_dir('A23_'+profile+'_complete_journey')
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);pid=_fixture(root,profile)
        offer=h02._offer_id_for_first_window(pid);table='lobby-sniper-tech';section=table+'-section'
        seq=h02._persona_response_sequence_for_full_journey(offer);gm_texts=h02._gm_response_texts(table,section)
        persona_texts=[h02._leader_nomination_proposal(),*seq]
        expected=h02._distinguishable_final_saves(table,section)
        gm_path=case/'gm-receipts.jsonl'
        with contextlib.ExitStack() as stack:
            gm=stack.enter_context(sup.recording_http_server([(200,{'choices':[{'message':{'content':x}}],'usage':{}}) for x in gm_texts],
               receipts_path=gm_path,label='a23-gm',validators=h02._gm_validators_for_full_journey(seq)))
            env={'OPENWEBUI_URL':gm.base_url,'OPENWEBUI_API_KEY':'SYNTH-A23-NOT-A-KEY',
                 'MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096','MMO_SIM_LOBBY_INITIATIVE_LIMIT':'8'}
            if profile=='api':
                validators={0:sup.make_persona_input_validator('sniper',None,expected_current=sup.load_fixture_save('sniper'))}
                validators.update({i+1:v for i,v in h02._persona_validators_for_full_journey(offer,table,section).items()})
                # Same H02 validators plus comparison to already emitted GM journal.
                def checked(v):
                    def run(body):
                        error=v(body)
                        if error:return error
                        view=sup.decode_public_table_view(body['messages'][1]['content'])
                        if view is not None:
                            for j,entry in enumerate(view.get('sl_log',[])):
                                if entry.get('content')!=sup.observed_choice_content(gm.received[j]):return 'A23_GM_PREFIX_MISMATCH'
                        return None
                    return run
                persona=stack.enter_context(sup.recording_http_server([(200,{'choices':[{'message':{'content':x}}],'usage':{}}) for x in persona_texts],
                  receipts_path=case/'persona-receipts.jsonl',label='a23-persona',validators={i:checked(v) for i,v in validators.items()}))
                env.update({'MMO_SIM_PERSONA_API_BASE_URL':persona.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-A23-NOT-A-KEY','MMO_SIM_PERSONA_API_MODEL':'synthetic'})
            else:
                fallback=stack.enter_context(sup.recording_http_server([],receipts_path=case/'no-api-fallback.jsonl',label='no-api-fallback'))
                capture=case/'cli-receipts.jsonl';queue=[]
                lengths={i+2:x for i,x in enumerate(h02._TABLE_DECISION_PREFIX_LENGTHS)}
                pks=['sniper',*h02._SEQ_PK]
                for i,(pk,text) in enumerate(zip(pks,persona_texts)):
                    cur=expected[pk] if i in (11,12) else sup.load_fixture_save(pk)
                    item={'result':text,'expect_all':[sup.own_figure_marker(pk),sup.own_current_full_marker(cur)]}
                    if i==1:item['expect_all'].append('offer_id='+offer)
                    if i in lengths:
                        item.update({'expect_sl_log_len':lengths[i],'expect_table_id':table,'expect_gm_journal':str(gm_path)})
                    queue.append(item)
                cli=sup.write_queued_fake_cli(root,capture_path=capture,queue=queue)
                work=root/'cli-workdir';work.mkdir()
                env.update({'MMO_SIM_PERSONA_CLI':str(cli),'MMO_SIM_PERSONA_ISOLATED_WORKDIR':str(work),
                    'MMO_SIM_PERSONA_ISOLATION_FLAGS':'--permission-mode=plan,--safe-mode',
                    'MMO_SIM_PERSONA_API_BASE_URL':fallback.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-A23-NOT-A-KEY','MMO_SIM_PERSONA_API_MODEL':'forbidden-fallback'})
            tail=['v',profile,'sniper,tech','64','240','5','1','300','ja','x']
            p=_import_run(root,case/'tui',pid,a23sup.higher_level_human_save(),tail,env,confirm=True)
            assert 'Lobby-Tisch abgeschlossen' in p.stdout,p.stdout+p.stderr
            assert len(gm.calls)==5 and gm.validation_failures==[]
            for r in gm.received:assert r['body']['max_tokens']==4096
            if profile=='api':
                assert len(persona.calls)==13 and persona.validation_failures==[]
                classified=_classified(api=persona.received)
            else:
                assert not fallback.calls
                cli_calls=sup.read_jsonl(capture);assert len(cli_calls)==13
                classified=_classified(cli=cli_calls)
                responses=sup.read_jsonl(sup.response_log_path_for(capture));assert len(responses)==13
                for r in responses:
                    raw=(r['stdout']+'\n').encode();assert r['rc']==0 and r['stdout_raw_sha256']==a23sup.sha(raw) and r['stdout_raw_bytes_len']==len(raw)
                fail_log=capture.parent/(capture.stem+'.validation-failures.jsonl')
                assert not fail_log.exists() or not fail_log.read_text().strip()
            observed=h02._observed_gm_texts_from_receipts(gm.received,gm_texts)
            h02._assert_public_sl_prefix_and_reflections_exact(classified,observed,table)
            h02._assert_gm_ledger_content_matches_observed(root/'run',table,h02._gm_leader_texts_for_full_journey(seq),gm_received=gm.received)
            sup.write_json(case/'classified-persona-wires.json',classified)
            sup.write_json(case/'observed-gm-texts.json',observed)
            persona_journal=persona.received if profile=='api' else [
                {'transport':'cli','input':request,'output':response}
                for request,response in zip(cli_calls,responses)]
            reconciliation=h02._assert_request_ledger_reconciles(root/'run',table,section,pid,
                persona_journal=persona_journal,gm_journal=gm.received)
            assert reconciliation['journal_based'] and len(reconciliation['assignments'])==18
            sup.write_json(case/'request-ledger-reconciliation.json',reconciliation)
        _audit_processes(case/'tui',1)
        before=p._a23_snapshots['post-import']['hashes'];after=p._a23_snapshots['after-ui']['hashes']
        assert a23sup.protected(before,players=h02.SELECTED)==a23sup.protected(after,players=h02.SELECTED),'A23_PROTECTED_ACTOR_CHANGED'
        states=sorted((root/'states').glob('*.json'));assert len(states)==7
        parity=_assert_full_journey_parity_both_profiles(case,root/'run',root/'states',_SCHEMA_PATH,table,section,seq)
        ps=PersonaStateStore(schema_path=_SCHEMA_PATH)
        for pk in h02.SELECTED:
            current=core_store.load_current_save_or_raise(root/'run',pk,ps,states_dir=root/'states')
            assert current==expected[pk],f'A23_FULL_CURRENT_MISMATCH: {pk}'
            state=ps.load_state(pk,states_dir=root/'states')
            assert state['last_reflection']==seq[8 if pk=='sniper' else 9]
        for c in classified[-2:]:
            pk=c['pk'];other='tech' if pk=='sniper' else 'sniper'
            assert seq[8 if pk=='sniper' else 9] in c['full']
            assert seq[8 if other=='sniper' else 9] not in c['full']
            assert sup.own_current_full_marker(expected[pk]) in c['full']
        records=request_ledger._all_records(root/'run');assert len(records)==18 and all(r['state']=='accounted' for r in records)
        status=lab_runner.read_status(root/'run');assert status.turns_used==18 and status.provider_free is True
        sup.write_json(case/'result.json',{'status':'PASS','profile':profile,'participant_id':pid,'state_count':7,'requests':18,'parity':parity})


def test_v3_api_profile_real_tui_to_lab_to_persona_journey():
    _journey('api')


def test_v4_hybrid_profile_real_tui_to_lab_to_fake_cli_journey():
    _journey('hybrid')


def test_v5_lost_status_authority_stays_t9_hold_via_tui_dispatch():
    case=sup.case_dir('A23_V5_resume_and_hold')
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);pid=_fixture(root,'resume');previous_requests={};previous_turns=0
        for ix in range(2):
            phase=case/f'normal-{ix}'
            with sup.recording_http_server([(200,{'choices':[{'message':{'content':'pause'}}]})],receipts_path=phase/'persona.jsonl',label='a23-resume-pause',validators={0:sup.make_persona_input_validator('sniper',None,expected_current=sup.load_fixture_save('sniper'))}) as ps, sup.recording_http_server([],receipts_path=phase/'gm.jsonl',label='a23-resume-no-gm') as gm:
                env={'MMO_SIM_PERSONA_API_BASE_URL':ps.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-A23-NOT-A-KEY','MMO_SIM_PERSONA_API_MODEL':'synthetic',
                     'OPENWEBUI_URL':gm.base_url,'OPENWEBUI_API_KEY':'SYNTH-A23-NOT-A-KEY','MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096','MMO_SIM_LOBBY_INITIATIVE_LIMIT':'1'}
                p=_import_run(root,phase/'tui',pid,a23sup.higher_level_human_save(char_id=f'CHR-A23-RESUME-{ix}'),
                    ['v','api','sniper,tech','64','240','5','1','300','ja','x'],env,switch=bool(ix),confirm=True)
                assert len(ps.calls)==1 and not gm.calls and not ps.validation_failures
            before=p._a23_snapshots['post-import']['hashes'];after=p._a23_snapshots['after-ui']['hashes']
            assert a23sup.protected(before)==a23sup.protected(after),'A23_RESUME_CHANGED_PLAYER_AUTHORITY'
            current={r['id']:r for r in request_ledger._all_records(root/'run')}
            assert all(current[k]==v for k,v in previous_requests.items())
            assert len(current)==ix+1 and all(r['state']=='accounted' for r in current.values())
            status=lab_runner.read_status(root/'run');assert status.turns_used==previous_turns+1 and status.provider_free is True
            previous_requests=current;previous_turns=status.turns_used
            _audit_processes(phase/'tui',1)
        # Exact existing T9 case: lose only status in own synthetic copy/state.
        old_status=(root/'run/lab.status.json').read_bytes();(case/'status-before-controlled-loss.json').write_bytes(old_status)
        (root/'run/lab.status.json').unlink()
        with _traps(case/'hold-traps') as (ps,gm,env):
            p=_import_run(root,case/'hold-tui',pid,a23sup.higher_level_human_save(char_id='CHR-A23-RESUME-HOLD',level=6),
                ['v','api','sniper,tech','64','240','5','1','300','ja','x'],env,switch=True,confirm=True)
            assert 'H10 T9' in p.stdout and 'Controller-Kindprozess beendet mit exit=2' in p.stdout,p.stdout
            assert not ps.calls and not gm.calls
            assert p._a23_snapshots['post-import']['hashes']==p._a23_snapshots['after-ui']['hashes'],'A23_T9_HOLD_CHANGED_AUTHORITY'
            assert {r['id']:r for r in request_ledger._all_records(root/'run')}==previous_requests
            assert not (root/'run/lab.status.json').exists()
            _audit_processes(case/'hold-tui',1)
        sup.write_json(case/'result.json',{'status':'PASS','participant_id':pid,'normal_resume_requests':len(previous_requests),'turns_before_loss':previous_turns,'hold_contacts':0})


def main():
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_')];failed=0
    for t in tests:
        try:t();print('OK  ',t.__name__)
        except Exception:
            failed+=1;print('FAIL',t.__name__);traceback.print_exc()
    print(f'{len(tests)-failed}/{len(tests)} Tests bestanden.');return int(failed>0)
if __name__=='__main__':raise SystemExit(main())
