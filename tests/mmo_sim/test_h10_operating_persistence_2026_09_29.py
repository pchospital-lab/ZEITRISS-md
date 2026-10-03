#!/usr/bin/env python3
"""Fixed T1-T10 operational persistence matrix; existing component controls retained.

Synthetic nonzero status vectors are explicitly seeded, never fabricated as live
usage. All operational cases run the real dispatcher in new guarded children.
Writes/reads use the unchanged product. Faults are exact one-shot syscall seams.
Evidence is captured before cleanup. This is not a universal failure matrix.
"""
from __future__ import annotations
import base64,contextlib,json,os,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
from unittest.mock import patch
_HERE=Path(__file__).resolve().parent
_REPO_ROOT=_HERE.parents[1]
sys.path[:0]=[str(_HERE),str(_REPO_ROOT)]
from mmo_sim.lab import runner as lab_runner, cli as lab_cli
from mmo_sim.lab.runner import LabBudget,LabRunner,read_status
from mmo_sim.core import store as core_store,request_ledger,lobby_flow,lobby_service
from mmo_sim.core.admission import write_test_profile
import _h02_vollreise_support as sup
import _h05_stop_support as h05sup
import test_h02_vollreise_profiles_2026_09_28 as h2
import test_h05_stop_lifecycle_2026_09_29 as h5
import test_l01_l10_lobby_initiative as l01l10
import _h10_persistence_support as hs
_MMO_SIM=sup.MMO_SIM
_H10_SUPPORT=_HERE/'_h10_persistence_support.py'
_HYBRID_ISOLATION_FLAGS=['--permission-mode=plan','--safe-mode']

# Existing direct component controls are retained as ADDITIONAL tests.
def test_t1_start_status_write_fails_before_replace_preserves_last_valid_state():
    """VOR `os.replace`: der neue Statuswrite darf nie ankommen -- der
    zuletzt gültige, bereits mit NICHTNULL-Verbrauch UND beiden befüllten
    Dedup-Listen persistierte Stand bleibt bytegleich erhalten, kein
    unsichtbarer Lock nach dem Fehler."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(10, 600, 5))
        lab.start()
        lab.record_turn(seconds=12.5, usd=0.75)
        lab.record_turn(seconds=3.5, usd=0.20)
        # T1-T4 muessen NICHTNULL-Verbrauch + beide Dedup-Listen mitfuehren
        # (02_AUFTRAG_H10.md) -- beide Listen direkt am echten Statuspfad
        # gesetzt (dieselbe Autoritaet, die core.admission.record_usd_delta/
        # add_seconds separat pflegen; hier synthetisch vorbelegt, damit T1
        # unabhaengig von einem vollen Request-Ledger-Durchlauf pruefbar ist).
        status_path = lab_runner._status_path(run_dir)
        raw = json.loads(status_path.read_text(encoding="utf-8"))
        raw["reconciled_request_ids"] = ["req-A-t1"]
        raw["reconciled_seconds_request_ids"] = ["req-B-t1"]
        status_path.write_text(json.dumps(raw), encoding="utf-8")
        lab.release()
        before_bytes = status_path.read_bytes()
        assert not (run_dir / "lab.lock.json").exists()

        resumed = LabRunner(run_dir, LabBudget(10, 600, 5))
        hits = [0]
        orig_replace = lab_runner.os.replace

        def faulty_replace(src, dst, *a, **kw):
            if hits[0] == 0 and Path(dst) == status_path:
                hits[0] += 1
                raise OSError("T1_INJECT_BEFORE_REPLACE")
            return orig_replace(src, dst, *a, **kw)

        with patch.object(lab_runner.os, "replace", faulty_replace):
            try:
                resumed.start()
                raise AssertionError("start() haette den injizierten Fehler propagieren muessen")
            except OSError as exc:
                assert "T1_INJECT" in str(exc)
        assert hits[0] == 1, "Injektion muss GENAU einmal am echten os.replace-Ziel treffen"
        assert resumed._lock_fd is None, "erfolgloser Aufrufer haelt keine unsichtbare Sperre"
        assert not (run_dir / "lab.lock.json").exists(), "kein Fremdbesitz nach fehlgeschlagenem Erwerb"
        assert status_path.read_bytes() == before_bytes, (
            "letzter gueltiger Betrag-/Dedup-/Testprofilverbund muss bytegleich erhalten bleiben"
        )
        after = read_status(run_dir)
        assert after.turns_used == 2 and abs(after.usd_spent - 0.95) < 1e-9
        assert after.reconciled_request_ids == ["req-A-t1"]
        assert after.reconciled_seconds_request_ids == ["req-B-t1"]
        assert abs(after.seconds_elapsed - 16.0) < 1e-9, (
            f"Zeitverbrauch (record_turn(seconds=12.5)+(3.5)) muss Teil des vollstaendigen "
            f"Verbrauchsverbunds sein, ist {after.seconds_elapsed}"
        )

        # Gesunde Kontrolle: ein Folgestart (ohne Patch) gelingt, uebernimmt
        # denselben Verbund frisch, kein Request ausgeloest.
        retry = LabRunner(run_dir, LabBudget(10, 600, 5))
        retry.start()
        try:
            st = read_status(run_dir)
            assert st.running is True and st.pid == retry.pid
            assert st.turns_used == 2 and abs(st.usd_spent - 0.95) < 1e-9
            assert st.reconciled_request_ids == ["req-A-t1"]
            assert st.reconciled_seconds_request_ids == ["req-B-t1"]
            assert abs(st.seconds_elapsed - 16.0) < 1e-9
        finally:
            retry.release()
        assert lab_runner.os.replace is orig_replace

def test_t2_start_status_write_fails_after_replace_persists_full_new_state():
    """NACH echtem `os.replace`: der neue Status ist bereits vollständig auf
    Platte, der Aufrufer sieht trotzdem den Fehler und gibt seinen Lock
    öffentlich frei (kein Freibrief zum erneuten Initialisieren) -- ein
    späterer Folgestart bucht nichts doppelt/nichts auf null."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(10, 600, 5))
        lab.start()
        lab.record_turn(seconds=9.0, usd=0.42)
        status_path = lab_runner._status_path(run_dir)
        raw = json.loads(status_path.read_text(encoding="utf-8"))
        raw["reconciled_request_ids"] = ["req-A-t2"]
        raw["reconciled_seconds_request_ids"] = ["req-B-t2"]
        status_path.write_text(json.dumps(raw), encoding="utf-8")
        lab.release()

        resumed = LabRunner(run_dir, LabBudget(10, 600, 5))
        hits = [0]
        orig_replace = lab_runner.os.replace

        def faulty_replace_after(src, dst, *a, **kw):
            if hits[0] == 0 and Path(dst) == status_path:
                hits[0] += 1
                orig_replace(src, dst, *a, **kw)  # echter Replace laeuft VOLLSTAENDIG durch
                raise OSError("T2_INJECT_AFTER_REPLACE")
            return orig_replace(src, dst, *a, **kw)

        with patch.object(lab_runner.os, "replace", faulty_replace_after):
            try:
                resumed.start()
                raise AssertionError("start() haette den injizierten Fehler propagieren muessen")
            except OSError as exc:
                assert "T2_INJECT" in str(exc)
        assert hits[0] == 1
        # Der neue Status ist VOLLSTAENDIG committed (running=True, resumed.pid,
        # unveraendert derselbe Verbund) -- keine Mischung/Nullstellung.
        after_fault = read_status(run_dir)
        assert after_fault.running is True and after_fault.pid == resumed.pid
        assert after_fault.turns_used == 1 and abs(after_fault.usd_spent - 0.42) < 1e-9
        assert after_fault.reconciled_request_ids == ["req-A-t2"]
        assert after_fault.reconciled_seconds_request_ids == ["req-B-t2"]
        assert abs(after_fault.seconds_elapsed - 9.0) < 1e-9, (
            f"Zeitverbrauch (record_turn(seconds=9.0)) muss Teil des vollstaendigen "
            f"Verbrauchsverbunds sein, ist {after_fault.seconds_elapsed}"
        )
        # Der Lock wurde trotzdem oeffentlich freigegeben (der Aufrufer sah
        # ja einen Fehler und ist kein lebender Owner mehr).
        assert resumed._lock_fd is None
        assert not (run_dir / "lab.lock.json").exists()

        # Gesunde Kontrolle: naechste bewusste Wiederaufnahme bleibt sicher --
        # kein Doppelrequest, keine Neuinitialisierung, derselbe Verbund.
        retry = LabRunner(run_dir, LabBudget(10, 600, 5))
        retry.start()
        try:
            st = read_status(run_dir)
            assert st.turns_used == 1 and abs(st.usd_spent - 0.42) < 1e-9
            assert st.reconciled_request_ids == ["req-A-t2"]
            assert st.pid == retry.pid
            assert abs(st.seconds_elapsed - 9.0) < 1e-9
        finally:
            retry.release()
        assert lab_runner.os.replace is orig_replace

def test_t3_release_status_write_fails_before_replace_preserves_running_state():
    """VOR dem finalen Replace: frisch gebuchte Werte/Dedup bleiben stehen,
    der Fehler wird NICHT als erfolgreich gespeicherter Stop-Status
    ausgegeben; die echte Kernel-Sperre endet trotzdem korrekt (naechster
    regulaerer Owner wird nicht blockiert und ueberschreibt den alten Stand
    nicht mit geratenen Nullen)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(10, 600, 5))
        lab.start()
        lab.record_turn(seconds=5.0, usd=0.30)
        status_path = lab_runner._status_path(run_dir)
        raw = json.loads(status_path.read_text(encoding="utf-8"))
        raw["reconciled_request_ids"] = ["req-A-t3"]
        raw["reconciled_seconds_request_ids"] = ["req-B-t3"]
        # Nachzug (End-Critic 2026-09-29, CRITIC-REPORT.md Sammelbefund T1-T4):
        # aktive Testautoritaet + Unknown-Kosten synthetisch mitbelegen, exakt
        # dasselbe Muster wie die beiden Dedup-Listen oben -- _write_status()
        # uebernimmt beide Felder frisch von der Platte (runner.py Z.761/794).
        raw["provider_free"] = True
        raw["usd_unknown_turns"] = 1
        status_path.write_text(json.dumps(raw), encoding="utf-8")
        before_bytes = status_path.read_bytes()

        hits = [0]
        orig_replace = lab_runner.os.replace

        def faulty_replace(src, dst, *a, **kw):
            if hits[0] == 0 and Path(dst) == status_path:
                hits[0] += 1
                raise OSError("T3_INJECT_BEFORE_REPLACE")
            return orig_replace(src, dst, *a, **kw)

        with patch.object(lab_runner.os, "replace", faulty_replace):
            try:
                lab.release()
                raise AssertionError("release() haette den injizierten Fehler propagieren muessen")
            except OSError as exc:
                assert "T3_INJECT" in str(exc)
        assert hits[0] == 1
        # Status bytegleich unveraendert -- kein erfolgreich gespeicherter Stop.
        assert status_path.read_bytes() == before_bytes
        unchanged = read_status(run_dir)
        assert unchanged.running is True  # NICHT als erfolgreich beendet ausgegeben
        assert unchanged.turns_used == 1 and abs(unchanged.usd_spent - 0.30) < 1e-9
        assert unchanged.reconciled_request_ids == ["req-A-t3"]
        assert abs(unchanged.seconds_elapsed - 5.0) < 1e-9, (
            f"Zeitverbrauch (record_turn(seconds=5.0)) muss Teil des vollstaendigen "
            f"Verbrauchsverbunds sein, ist {unchanged.seconds_elapsed}"
        )
        assert unchanged.reconciled_seconds_request_ids == ["req-B-t3"], (
            f"Zeit-Dedup-Liste darf beim gescheiterten Replace nicht verloren sein, "
            f"ist {unchanged.reconciled_seconds_request_ids}"
        )
        assert unchanged.provider_free is True, "aktive provider_free-Testautoritaet muss mitgefuehrt werden"
        assert unchanged.usd_unknown_turns == 1, "Unknown-Kosten muessen mitverglichen werden"
        # Die echte OS-Sperre endet trotzdem (finally: flock/close) --
        # self._lock_fd ist danach None, auch wenn die Lock-DATEI (rein
        # informativ) noch den eigenen alten Eintrag traegt.
        assert lab._lock_fd is None

        # Gesunde Kontrolle: ein neuer regulaerer Owner wird NICHT blockiert
        # und ueberschreibt den alten Stand nicht mit Nullen -- er uebernimmt
        # den zuletzt gueltigen Verbund frisch von der Platte.
        successor = LabRunner(run_dir, LabBudget(10, 600, 5))
        successor.start()
        try:
            st = read_status(run_dir)
            assert st.pid == successor.pid and st.running is True
            assert st.turns_used == 1 and abs(st.usd_spent - 0.30) < 1e-9
            assert st.reconciled_request_ids == ["req-A-t3"]
            assert abs(st.seconds_elapsed - 5.0) < 1e-9
            assert st.reconciled_seconds_request_ids == ["req-B-t3"]
            assert st.provider_free is True
            assert st.usd_unknown_turns == 1
        finally:
            successor.release()
        assert lab_runner.os.replace is orig_replace

def test_t4_release_status_write_fails_after_replace_values_committed():
    """NACH dem finalen Replace: der neue (Release-)Status ist bereits
    vollstaendig committed, bevor der Fehler propagiert -- spaeteres Resume
    bucht nichts doppelt, keine fd-/Autoritaetsreparatur wird stillschweigend
    als PASS gewertet."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(10, 600, 5))
        lab.start()
        lab.record_turn(seconds=7.0, usd=0.55)
        status_path = lab_runner._status_path(run_dir)
        raw = json.loads(status_path.read_text(encoding="utf-8"))
        raw["reconciled_request_ids"] = ["req-A-t4"]
        raw["reconciled_seconds_request_ids"] = ["req-B-t4"]
        # Nachzug (End-Critic 2026-09-29, CRITIC-REPORT.md Sammelbefund T1-T4):
        # aktive Testautoritaet mitbelegen, s. T3-Kommentar oben fuer dasselbe
        # Muster/dieselbe Naht (_write_status() runner.py Z.794).
        raw["provider_free"] = True
        status_path.write_text(json.dumps(raw), encoding="utf-8")

        hits = [0]
        orig_replace = lab_runner.os.replace

        def faulty_replace_after(src, dst, *a, **kw):
            if hits[0] == 0 and Path(dst) == status_path:
                hits[0] += 1
                orig_replace(src, dst, *a, **kw)
                raise OSError("T4_INJECT_AFTER_REPLACE")
            return orig_replace(src, dst, *a, **kw)

        with patch.object(lab_runner.os, "replace", faulty_replace_after):
            try:
                lab.release()
                raise AssertionError("release() haette den injizierten Fehler propagieren muessen")
            except OSError as exc:
                assert "T4_INJECT" in str(exc)
        assert hits[0] == 1
        after = read_status(run_dir)
        assert after.running is False, "der echte finale Stop-Status ist vollstaendig committed"
        assert after.turns_used == 1 and abs(after.usd_spent - 0.55) < 1e-9
        assert after.reconciled_request_ids == ["req-A-t4"]
        # Sensitivitaets-Nachzug (05_QUELLEN_UND_PRUEFUNGEN.md/review_h10_
        # sensitivity.py: "T4 ... uebersieht Zeitverbrauch/Dedupverlust"):
        # der volle Verbrauchsverbund ist NICHT nur Betrag/Turns -- eine
        # nachtraegliche Manipulation von seconds_elapsed/reconciled_seconds_
        # request_ids NACH dem echten Replace waere mit den beiden Zeilen
        # oben ALLEIN unentdeckt geblieben (genau der vom Sensitivitaetstool
        # nachgewiesene blinde Fleck). Explizit UND zusammenhaengend pruefen.
        assert abs(after.seconds_elapsed - 7.0) < 1e-9, (
            f"Zeitverbrauch muss Teil des vollstaendigen Verbrauchsverbunds sein, ist {after.seconds_elapsed}"
        )
        assert after.reconciled_seconds_request_ids == ["req-B-t4"], (
            f"Zeit-Dedup-Liste darf nach dem echten Replace nicht geleert/verloren sein, "
            f"ist {after.reconciled_seconds_request_ids}"
        )
        assert after.provider_free is True, "aktive provider_free-Testautoritaet muss mitgefuehrt werden"
        assert lab._lock_fd is None

        # Gesunde Kontrolle: spaeteres Resume bucht nichts doppelt.
        resumed = LabRunner(run_dir, LabBudget(10, 600, 5))
        resumed.start()
        try:
            st = read_status(run_dir)
            assert st.turns_used == 1 and abs(st.usd_spent - 0.55) < 1e-9, "kein Doppel-Buchen"
            assert st.reconciled_request_ids == ["req-A-t4"]
            assert abs(st.seconds_elapsed - 7.0) < 1e-9
            assert st.reconciled_seconds_request_ids == ["req-B-t4"]
            assert st.provider_free is True
        finally:
            resumed.release()
        assert lab_runner.os.replace is orig_replace

def _run_t7_t8_case(num: int, profile: str, timing: str, case_dir: Path, extra_env: dict | None = None):
    """Baut GENAU EINE natürliche Reise (großer sechs-Persona-plus-Human-
    Schutzbestand, nur sniper+tech ausgewählt) über den echten CLI-
    Dispatcher bis zum echten `_write_last_window`-Aufruf INNERHALB der
    laufenden `_run_controller`-Ausführung -- reine Wiederverwendung
    bestehender H02/H05-Fixtures/Validatoren/Sequenzen (kein neues
    Antwortscript). Rückgabe: dict mit allen Rohbelegen für die
    aufrufenden Tests. `extra_env` (Default None, KEINE Verhaltensaenderung
    fuer die beiden regulaeren T7/T8-Tests): ausschliesslich fuer die
    Sensitivitaets-Gegenprobe (`MMO_SIM_H10_SENSITIVITY_PROBE=1`, s.
    `_h10_persistence_support.py`), die denselben echten Diagnose-Hit um
    eine synthetische Nachkorruption ergaenzt, um zu belegen, dass DIESE
    Assertions eine solche Aenderung tatsaechlich roeten (kein Vakuum-PASS)."""
    case_dir.mkdir(parents=True, exist_ok=True)
    root = case_dir / "data"
    tag = f"h10t{num}"
    schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, _human = h5._bootstrap_table_prereqs(
        root, tag,
    )
    seq = h2._persona_response_sequence_for_full_journey(offer_id)
    gm_texts = h2._gm_response_texts(h5.TABLE_ID, h5.SECTION_ID)
    responses = [h2._leader_nomination_proposal(), *seq]
    gm_journal = case_dir / "gm-receipts.jsonl"
    persona_capture = case_dir / "persona-receipts.jsonl"
    validators = {0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))}
    validators.update({i + 1: v for i, v in h2._persona_validators_for_full_journey(offer_id, h5.TABLE_ID, h5.SECTION_ID).items()})

    with contextlib.ExitStack() as es:
        gm = es.enter_context(sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": text}}], "usage": {}}) for text in gm_texts],
            receipts_path=gm_journal, label=f"T{num}-GM", validators=h2._gm_validators_for_full_journey(seq),
        ))
        extra = {
            "OPENWEBUI_URL": gm.base_url, "OPENWEBUI_API_KEY": "SYNTH-H10-GM",
            "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096", "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
        }
        if extra_env:
            extra.update(extra_env)
        if profile == "api":
            persona = es.enter_context(sup.recording_http_server(
                [(200, {"choices": [{"message": {"content": text}}], "usage": {}}) for text in responses],
                receipts_path=persona_capture, label=f"T{num}-persona", validators=validators,
            ))
            extra.update(MMO_SIM_PERSONA_API_BASE_URL=persona.base_url, MMO_SIM_PERSONA_API_KEY="SYNTH-H10-PERSONA")
            persona_calls_ref = persona
        else:
            final = h2._distinguishable_final_saves(h5.TABLE_ID, h5.SECTION_ID)
            queue = []
            for i, text in enumerate(responses):
                pk = "sniper" if i == 0 else h2._SEQ_PK[i - 1]
                current = final[pk] if i in (11, 12) else sup.load_fixture_save(pk)
                row = {"result": text, "expect_all": [sup.own_figure_marker(pk), sup.own_current_full_marker(current)]}
                if i == 1:
                    row["expect_all"].append("offer_id=" + offer_id)
                if 2 <= i <= 10:
                    row.update(
                        expect_sl_log_len=h2._TABLE_DECISION_PREFIX_LENGTHS[i - 2],
                        expect_table_id=h5.TABLE_ID, expect_gm_journal=str(gm_journal),
                    )
                queue.append(row)
            cli_path, _block, _release, _egress = h05sup.write_stalling_fake_cli(
                root, capture_path=persona_capture, queue=queue, block_at_index=99, wait_timeout=10,
            )
            workdir = root / "cli_workdir"
            workdir.mkdir(parents=True, exist_ok=True)
            extra.update(
                MMO_SIM_PERSONA_CLI=str(cli_path), MMO_SIM_PERSONA_ISOLATED_WORKDIR=str(workdir),
                MMO_SIM_PERSONA_ISOLATION_FLAGS=",".join(_HYBRID_ISOLATION_FLAGS),
            )
            persona_calls_ref = None
        env = h5._controller_env(tmp_root=root / "kid-controller", guard_dir=guard_dir, extra=extra)
        args = h5._standard_start_args(root, tag, profile)
        argv = [
            sys.executable, "-B", str(_H10_SUPPORT), "--source", str(_REPO_ROOT), "--root", str(root),
            "--case", str(case_dir), "--timing", timing, "--", *args,
        ]
        started = time.time()
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = proc.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=10)
            raise
        ended = time.time()
        (case_dir / "stdout.txt").write_bytes(stdout)
        (case_dir / "stderr.txt").write_bytes(stderr)
        (case_dir / "invocation.json").write_text(json.dumps({
            "argv": argv, "pid": proc.pid, "started": started, "ended": ended, "returncode": proc.returncode,
            "cwd":str(_REPO_ROOT), "environment":env, "timeout":False,
        }, indent=2), encoding="utf-8")
        gm_received = list(gm.received)
        gm_failures = list(gm.validation_failures)
        persona_calls = len(persona_calls_ref.calls) if persona_calls_ref is not None else None
        persona_failures = list(persona_calls_ref.validation_failures) if persona_calls_ref is not None else []

    return {
        "run_dir": run_dir, "table_id": h5.TABLE_ID, "section_id": h5.SECTION_ID,
        "community_id": f"community-{tag}", "guard_dir": guard_dir, "schema_path": schema_path,
        "states_dir": states_dir, "onboarding_dir": onboarding_dir, "root": root,
        "proc_returncode": proc.returncode, "stdout": stdout, "stderr": stderr,
        "gm_received": gm_received, "gm_validation_failures": gm_failures,
        "persona_calls": persona_calls, "persona_validation_failures": persona_failures,
        "expected_response_count": len(responses),
    }

# ---- Operational cases: one exclusive evidence directory per existing case. ----
@contextlib.contextmanager
def _case(name):
    case=sup.case_dir('H10-'+name)
    with tempfile.TemporaryDirectory(prefix='h10-'+name+'-') as td:
        root=Path(td)/'data';root.mkdir()
        try:yield case,root
        finally:
            actual_roots=[d for d in root.parent.iterdir() if d.is_dir() and (d/'run').is_dir()]
            window=root.parent/'window/data'
            if (window/'run').is_dir():actual_roots.append(window)
            hs.save(case/'final-authorities.json',{str(d.relative_to(root.parent)):hs.snapshot(d) for d in actual_roots})


def _bootstrap(root,cid):
    schema,states,run,onboarding,guard,offer,human=h5._bootstrap_table_prereqs(root,cid)
    assert len(list(states.glob('*.json')))==7
    return guard,offer,human


def _args(root,cid,verb='start',max_requests=40,profile='api'):
    return [verb,'--data-dir',str(root),'--community',cid,'--profile',profile,
            '--max-requests',str(max_requests),'--max-seconds','120','--max-usd','5',
            '--max-idle-windows','1','--max-wall-seconds','90','--personas','sniper,tech']


def _spawn(case,root,name,args,extra,fault='none'):
    out=case/name;out.mkdir(parents=True,exist_ok=False)
    env=h5._controller_env(tmp_root=root/('kid-'+name),guard_dir=root/'guard',extra=extra)
    argv=[sys.executable,'-B',str(_H10_SUPPORT),'--source',str(_REPO_ROOT),
          '--root',str(root),'--case',str(out),'--fault',fault,'--',*args]
    p=subprocess.Popen(argv,cwd=_REPO_ROOT,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p._h10={'argv':argv,'pid':p.pid,'cwd':str(_REPO_ROOT),'environment':env,'started_utc':hs.now()}
    p._h10_out=out
    return p


def _finish(p,timeout=90):
    timed_out=False
    try:stdout,stderr=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True;p.kill();stdout,stderr=p.communicate(timeout=10)
    out=p._h10_out;(out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
    hs.save(out/'invocation.json',{**p._h10,'ended_utc':hs.now(),'returncode':p.returncode,'timeout':timed_out})
    assert not timed_out,'Own cleanup timeout is not functional success'
    return p.returncode,stdout,stderr


def _run(case,root,name,args,extra=None,fault='none'):
    p=_spawn(case,root,name,args,extra or {},fault);rc,stdout,stderr=_finish(p)
    assert rc!=97,(p._h10_out/'BLOCKED.json').read_text()
    return rc,stdout,stderr


def _seed_status(root):
    run=root/'run';lab=LabRunner(run,LabBudget(30,300,5));lab.start()
    lab.record_turn(seconds=12.5,usd=.75);lab.release()
    p=run/'lab.status.json';d=json.loads(p.read_text())
    d.update(reconciled_request_ids=['SYNTHETIC-STATUS-USD'],
             reconciled_seconds_request_ids=['SYNTHETIC-STATUS-TIME'],usd_unknown_turns=2)
    hs.save(p,d)
    return hs.vector(d)


def _readers(case,root,label='readers'):
    before=hs.snapshot(root);hs.save(case/(label+'-before.json'),before)
    results={}
    for verb in ('status','attach'):
        rc,stdout,stderr=_run(case,root,label+'-'+verb,[verb,'--data-dir',str(root)])
        assert rc==0,stderr
        results[verb]=stdout.decode()
        assert hs.snapshot(root)==before,f'{verb} changed authority bytes'
    hs.save(case/(label+'-after.json'),hs.snapshot(root));return results


@contextlib.contextmanager
def _traps(case,label='trap'):
    with sup.recording_http_server([],receipts_path=case/(label+'-persona.jsonl'),label=label+'-persona') as p, \
         sup.recording_http_server([],receipts_path=case/(label+'-gm.jsonl'),label=label+'-gm') as g:
        extra={'MMO_SIM_PERSONA_API_BASE_URL':p.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-H10',
               'OPENWEBUI_URL':g.base_url,'OPENWEBUI_API_KEY':'SYNTH-H10','MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096'}
        try:yield extra,p,g
        finally:
            hs.save(case/(label+'-counts.json'),{'persona':len(p.calls),'gm':len(g.calls)})
            assert len(p.calls)==len(g.calls)==0,'Unexpected transport intake'


def _status_case(num):
    seam={1:'start-before',2:'start-after',3:'release-before',4:'release-after'}[num]
    with _case('T'+str(num)) as (case,root):
        cid='h10t'+str(num);_bootstrap(root,cid);expected=_seed_status(root)
        before=hs.snapshot(root);hs.save(case/'before.json',before)
        hs.save(case/'fixture-kind.json',{'status_vector':'explicit synthetic fixture, set before entry','expected':expected,'states':7})
        with _traps(case) as (extra,_,__):
            rc,stdout,stderr=_run(case,root,'fault',_args(root,cid,max_requests=1),extra,seam)
            assert rc!=0 and ('H10_PERSISTENCE_'+seam.upper().replace('-','_')).encode() in stderr
            hit=json.loads((case/'fault/fault-hit.json').read_text())
            assert hit['hit']==1 and hit['fault']==seam
            assert hit['real_systemcall_completed']==seam.endswith('after')
            assert any(f['function']=='_run_controller' for f in hit['stack'])
            for snap in (before,hit['before'],hit['after'],hs.snapshot(root)):
                status=json.loads(base64.b64decode(snap['status']['bytes_b64']))
                assert hs.vector(status)==expected,'Complete status vector changed'
                assert snap['protected']==before['protected']
                assert snap['requests']==before['requests']
            if num==1:assert hs.snapshot(root)['status']==before['status']
            # Sequential real successor demonstrates cleanup; no new ownership race.
            _readers(case,root)
            rc,_,err=_run(case,root,'healthy-resume',_args(root,cid,'resume',max_requests=1),extra)
            assert rc==0,err
            assert hs.vector(json.loads((root/'run/lab.status.json').read_text()))==expected
            assert not (root/'run/lab.lock.json').exists()
            assert hs.snapshot(root)['protected']==before['protected']
            assert hs.snapshot(root)['requests']==before['requests']
        hs.save(case/'assertions.json',{'fault_hit':1,'whole_nonzero_vector_preserved':True,'new_cli_successor':True,'new_requests':0})


def test_t1_cli_child_start_status_write_before_replace_real_process():_status_case(1)
def test_t2_cli_child_start_status_write_after_replace_real_process():_status_case(2)
def test_t3_cli_child_release_before_replace_real_process():_status_case(3)
def test_t4_cli_child_release_after_replace_real_process():_status_case(4)


def test_t5_external_lab_stop_cli_write_failure_is_not_a_false_success():
    with _case('T5') as (case,root):
        cid='h10t5';_bootstrap(root,cid)
        body={'choices':[{'message':{'content':'{"action":"pause"}'}}],'usage':{}}
        handler,blocked,release,receipts,failures=h05sup.make_stalling_handler([],body,
            validators={0:sup.make_persona_input_validator('sniper',None,expected_current=sup.load_fixture_save('sniper'))},
            journal_path=case/'persona-journal.jsonl',label='T5',wait_timeout=60)
        srv,thread,url=h05sup.start_http_server(handler)
        controller=None
        try:
            with sup.recording_http_server([],receipts_path=case/'gm-trap.jsonl',label='T5-GM') as gm:
                extra={'MMO_SIM_PERSONA_API_BASE_URL':url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-H10',
                       'OPENWEBUI_URL':gm.base_url,'OPENWEBUI_API_KEY':'SYNTH-H10','MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096'}
                controller=_spawn(case,root,'controller',_args(root,cid),extra)
                assert blocked.wait(30),'No actual inflight receipt'
                before=hs.snapshot(root);hs.save(case/'before-failed-stop.json',before)
                rc,out,err=_run(case,root,'failed-stop',['stop','--data-dir',str(root),'--reason','T5-failed'],extra,'stop-before')
                assert rc!=0 and b'H10_PERSISTENCE_STOP_BEFORE' in err and b'Stop angefordert' not in out
                assert hs.snapshot(root)==before and controller.poll() is None and len(receipts)==1
                hs.save(case/'after-failed-stop.json',hs.snapshot(root))
                # Regular stop is issued WHILE the same response remains blocked.
                rc,out,err=_run(case,root,'regular-stop',['stop','--data-dir',str(root),'--reason','T5-regular'],extra)
                assert rc==0 and b'Stop angefordert' in out,err
                held=hs.snapshot(root);hs.save(case/'after-stop-held.json',held)
                assert controller.poll() is None and len(receipts)==1
                for key in ('protected','status','requests'):assert held[key]==before[key]
                assert json.loads((root/'run/lab.stop').read_text())['reason']=='T5-regular'
                hs.save(case/'release-event.json',{'utc':hs.now(),'controller_pid':controller.pid,'regular_stop_rc':rc})
                release.set();rc,out,err=_finish(controller);assert rc==0,err
                assert len(receipts)==1 and not failures and not gm.calls
                after=hs.snapshot(root);assert after['protected']==before['protected']
                records=request_ledger._all_records(root/'run');assert len(records)==1 and records[0]['state']=='accounted'
                assert read_status(root/'run').turns_used==1
                assert not (root/'run/lab.lock.json').exists()
                hs.save(case/'after-response.json',after)
        finally:
            if controller is not None and controller.poll() is None:
                controller.kill();_finish(controller)
            h05sup.stop_http_server(srv,thread)


def test_t6_controller_stop_partial_write_then_oserror_leaves_no_silent_success():
    with _case('T6') as (case,root):
        cid='h10t6';_bootstrap(root,cid);expected=_seed_status(root)
        before=hs.snapshot(root);hs.save(case/'before.json',before)
        with _traps(case) as (extra,_,__):
            rc,out,err=_run(case,root,'fault',_args(root,cid,max_requests=1),extra,'stop-partial')
            assert rc!=0 and b'H10_PERSISTENCE_STOP_PARTIAL' in err
            hit=json.loads((case/'fault/fault-hit.json').read_text());assert hit['hit']==1
            assert any(f['function']=='_run_controller' for f in hit['stack'])
            intended=base64.b64decode(hit['intended_b64']);partial=(root/'run/lab.stop').read_bytes()
            assert partial==intended[:max(1,len(intended)//2)] and partial!=intended
            assert hs.vector(json.loads((root/'run/lab.status.json').read_text()))==expected
            after=hs.snapshot(root);assert after['protected']==before['protected'] and after['requests']==before['requests']
            hs.save(case/'after-fault.json',after)
            _readers(case,root)
        # Fresh independent control; the corrupt fault sample is never rewritten.
        healthy=root.parent/'healthy';healthy.mkdir();_bootstrap(healthy,'h10t6healthy');_seed_status(healthy)
        with _traps(case,'healthy-trap') as (extra,_,__):
            rc,_,err=_run(case,healthy,'healthy',_args(healthy,'h10t6healthy',max_requests=1),extra)
            assert rc==0,err
            assert hs.vector(json.loads((healthy/'run/lab.status.json').read_text()))==expected
            json.loads((healthy/'run/lab.stop').read_text())
        assert (root/'run/lab.stop').read_bytes()==partial
        hs.save(case/'healthy-final.json',hs.snapshot(healthy))


def _assert_common_t7_t8_invariants(num,timing,result):
    root=result['root'];run=result['run_dir'];case=run.parents[1];profile='api' if num==7 else 'hybrid'
    assert not result['gm_validation_failures'] and not result['persona_validation_failures']
    assert len(result['gm_received'])==5 and result['proc_returncode']!=0 and result['proc_returncode']!=97
    assert ('H10_PERSISTENCE_WINDOW_'+timing.upper()).encode() in result['stderr']
    hit=json.loads((case/'fault-hit.json').read_text());exitobs=json.loads((case/'child-exit-observation.json').read_text())
    assert hit['hit']==exitobs['hits']==1 and hit['protected']==exitobs['protected']
    assert hit['real_systemcall_completed']==(timing=='after')
    assert any(f['function']=='_run_controller' for f in hit['stack'])
    if timing=='before':assert not (run/'lab.last_window.json').exists()
    else:assert (run/'lab.last_window.json').read_bytes()==base64.b64decode(hit['intended_b64'])
    records=request_ledger._all_records(run);assert len(records)==16 and all(r['state']=='accounted' for r in records)
    assert (run/'completion'/f'{h5.SECTION_ID}__final.json').is_file()
    assert core_store.Table.load(run,h5.TABLE_ID).status=='closed'
    assert len(list(result['states_dir'].glob('*.json')))==7
    for pk in ('sniper','tech'):assert json.loads((root/'states'/f'{pk}.json').read_text())['rounds_played']==1
    before=hs.snapshot(root);hs.save(case/'before-readers.json',before)
    _readers(case,root)  # saved baseline BEFORE either reader, not a self-comparison
    assert hs.snapshot(root)==before
    finals=h2._distinguishable_final_saves(h5.TABLE_ID,h5.SECTION_ID)
    responses=['{"action":"pause"}','{"action":"pause"}'];capture=case/'resume-persona.jsonl'
    with contextlib.ExitStack() as es:
        gm=es.enter_context(sup.recording_http_server([],receipts_path=case/'resume-gm.jsonl',label='resume-GM'))
        extra={'OPENWEBUI_URL':gm.base_url,'OPENWEBUI_API_KEY':'SYNTH-H10','MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096'}
        if profile=='api':
            validators={i:sup.make_persona_input_validator(pk,None,expected_current=finals[pk]) for i,pk in enumerate(('sniper','tech'))}
            ps=es.enter_context(sup.recording_http_server([(200,{'choices':[{'message':{'content':x}}],'usage':{}}) for x in responses],
               receipts_path=capture,label='resume-persona',validators=validators))
            extra.update(MMO_SIM_PERSONA_API_BASE_URL=ps.base_url,MMO_SIM_PERSONA_API_KEY='SYNTH-H10')
        else:
            fakeroot=root/'resume-cli';fakeroot.mkdir()
            queue=[{'result':text,'expect_all':[sup.own_figure_marker(pk),sup.own_current_full_marker(finals[pk])]} for pk,text in zip(('sniper','tech'),responses)]
            cli,_,__,___=h05sup.write_stalling_fake_cli(fakeroot,capture_path=capture,queue=queue,block_at_index=99,wait_timeout=10)
            work=fakeroot/'work';work.mkdir()
            extra.update(MMO_SIM_PERSONA_CLI=str(cli),MMO_SIM_PERSONA_ISOLATED_WORKDIR=str(work),MMO_SIM_PERSONA_ISOLATION_FLAGS=','.join(_HYBRID_ISOLATION_FLAGS))
        rc,_,err=_run(case,root,'resume',_args(root,'h10t'+str(num),'resume',profile=profile),extra)
        assert rc==0,err
        assert not gm.calls
        if profile=='api':assert len(ps.calls)==2 and not ps.validation_failures
        else:assert len(capture.read_text().splitlines())==2
    after=hs.snapshot(root);hs.save(case/'after-resume.json',after)
    assert after['protected']==before['protected'],'Reader/resume changed protected complete section'
    rows=request_ledger._all_records(run);ids={r['id']:r for r in rows};assert len(rows)==len(ids)==18
    for row in records:assert ids[row['id']]==row
    status=read_status(run);assert status.turns_used==18 and status.provider_free is True
    assert not (run/'lab.lock.json').exists()
    hs.save(case/'assertions.json',{'existing_records_preserved':16,'records_after_resume':18,'real_resume':True,
        'real_readers_no_write':True,'protected_unchanged':True,'gm_count':5,'state_count':7})


def test_t7_last_window_write_failure_api_does_not_touch_authority():
    with _case('T7') as (case,root):
        result=_run_t7_t8_case(7,'api','before',root.parent/'window')
        try:_assert_common_t7_t8_invariants(7,'before',result)
        finally:_export_window(case,result)


def test_t8_last_window_write_failure_hybrid_does_not_touch_authority():
    with _case('T8') as (case,root):
        result=_run_t7_t8_case(8,'hybrid','after',root.parent/'window')
        try:_assert_common_t7_t8_invariants(8,'after',result)
        finally:_export_window(case,result)


def _export_window(case,result):
    src=result['run_dir'].parents[1]
    for f in src.rglob('*'):
        if f.is_file() and 'data' not in f.relative_to(src).parts:
            target=case/'window'/f.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
    hs.save(case/'window-final.json',hs.snapshot(result['root']))
    # Actual hybrid CLI output journal resides beside the input capture under data.
    for f in result['root'].rglob('*'):
        rel=f.relative_to(result['root'])
        if any(part.startswith('kid-') or part=='__pycache__' for part in rel.parts):continue
        if f.is_file() and f.suffix=='.jsonl':
            target=case/'window-data-journals'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)


def _build_known(root,cid,case):
    _guard,offer,_human=_bootstrap(root,cid)
    texts=[h2._leader_nomination_proposal(),h2._persona_response_sequence_for_full_journey(offer)[0]]
    vals={0:sup.make_persona_input_validator('sniper',None,expected_current=sup.load_fixture_save('sniper')),
          1:h2._persona_validators_for_full_journey(offer,h5.TABLE_ID,h5.SECTION_ID)[0]}
    with sup.recording_http_server([(200,{'choices':[{'message':{'content':x}}],'usage':{}}) for x in texts],
           receipts_path=case/'known-persona.jsonl',label='known-persona',validators=vals) as ps, \
         sup.recording_http_server([],receipts_path=case/'known-gm.jsonl',label='known-GM') as gm:
        extra={'MMO_SIM_PERSONA_API_BASE_URL':ps.base_url,'MMO_SIM_PERSONA_API_KEY':'SYNTH-H10',
               'OPENWEBUI_URL':gm.base_url,'OPENWEBUI_API_KEY':'SYNTH-H10','MMO_SIM_GM_OUTPUT_LIMIT_TOKENS':'4096'}
        rc,_,err=_run(case,root,'known-start',_args(root,cid,max_requests=2),extra)
        assert rc==0,err
        assert len(ps.calls)==2 and not ps.validation_failures and not gm.calls
    assert len(request_ledger._all_records(root/'run'))==2
    assert (root/'run/tables'/f'{h5.TABLE_ID}.json').is_file()
    assert read_status(root/'run').turns_used==2 and read_status(root/'run').provider_free is True
    hs.save(case/'known-final.json',hs.snapshot(root))


def _known_hold(num):
    with _case('T'+str(num)) as (case,original):
        cid='h10t'+str(num);_build_known(original,cid,case)
        root=original.parent/'fault-copy'
        shutil.copytree(original,root,ignore=shutil.ignore_patterns('kid-*','__pycache__'))
        p=root/'run/lab.status.json'
        if num==9:p.unlink()
        else:p.write_bytes(b'{ H10 controlled corrupt status')
        before=hs.snapshot(root);hs.save(case/'copy-before.json',before)
        _readers(case,root,'damaged-readers')
        with _traps(case) as (extra,_,__):
            rc,out,err=_run(case,root,'hold-resume',_args(root,cid,'resume',max_requests=2),extra)
            assert rc!=0,err
            if num==9:assert b'lab.status.json' in err and b'fehlt' in err
            else:assert b'JSONDecodeError' in err,err
            assert hs.snapshot(root)==before,'Hold changed authority bytes'
        hs.save(case/'copy-after.json',hs.snapshot(root))
        with _traps(case,'original-trap') as (extra,_,__):
            healthy=hs.snapshot(original)
            rc,_,err=_run(case,original,'original-resume',_args(original,cid,'resume',max_requests=2),extra)
            assert rc==0,err
            after=hs.snapshot(original)
            assert after['protected']==healthy['protected'] and after['requests']==healthy['requests']
            assert hs.vector(json.loads((original/'run/lab.status.json').read_text()))==hs.vector(json.loads(base64.b64decode(healthy['status']['bytes_b64'])))
        if num==9:
            # Genuine bootstrap-only: no request/table history. A budget pause is sufficient.
            fresh=original.parent/'bootstrap-only';fresh.mkdir();_bootstrap(fresh,'h10bootstrap')
            (fresh/'run/lab.status.json').unlink()
            assert not list((fresh/'run').glob('requests/*.json')) and not list((fresh/'run').glob('tables/*.json'))
            with _traps(case,'bootstrap-trap') as (extra,_,__):
                args=_args(fresh,'h10bootstrap','resume',max_requests=1)
                args[args.index('--max-wall-seconds')+1]='0.000000001'
                rc,_,err=_run(case,fresh,'bootstrap-resume',args,extra)
                assert rc==0 and b'fehlt' not in err,err
                assert read_status(fresh/'run').turns_used==0
            hs.save(case/'bootstrap-final.json',hs.snapshot(fresh))


def test_t9_resume_known_run_missing_status_json_is_hold_not_fresh_init():_known_hold(9)
def test_t10_resume_known_run_corrupt_status_json_is_hold_not_crash_guessing():_known_hold(10)

if __name__=='__main__':
    tests=[(n,f) for n,f in sorted(globals().items()) if n.startswith('test_t') and callable(f)]
    failed=0
    for name,test in tests:
        try:test();print('OK  ',name,flush=True)
        except Exception:failed+=1;print('FAIL',name,flush=True);traceback.print_exc()
    print(f'{len(tests)-failed}/{len(tests)} Tests bestanden.',flush=True)
    raise SystemExit(1 if failed else 0)
