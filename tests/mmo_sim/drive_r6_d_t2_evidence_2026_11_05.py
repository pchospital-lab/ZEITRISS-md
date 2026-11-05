#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_d_t2_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R6, Familie `d_t2` (G5/D, 01_NACHZUG.md §D,
STOP-EVIDENCE.md §4.2/§4.4): schliesst den von STOP-EVIDENCE.md §4.2 belegten
Reihenfolge-Rest -- der R5-T2-Beleg (`drive_r5_t2_evidence_2026_11_05.py`)
setzte den adressierten Betreiberstop erst, NACHDEM der normale neue Prozess
den noch offenen Primaerrest (Completed-Guard) bereits VOLLSTAENDIG
fertiggestellt hatte. R6 muss die RICHTIGE Reihenfolge zeigen: der Stop steht
bereits durabel, SOLANGE der Completed-Guard noch fehlt, BEVOR der naechste
normale Prozess den Primaerrest vollendet.

Mechanik (STOP-EVIDENCE.md §4.4 "Kleinstmoeglicher Nachzug"): Prozess 1 ist
dieselbe bereits erlaubte Grenzbarriere wie bei R5
(`_r5_t2_launcher_hardexit_in_primary_publication.py`), ERWEITERT um
`--operator-control-fifo` UND um ein WARTEN auf die echte `admission.
read_table_stop`-Durabilitaet NACH dem realen Statewrite, VOR dem Hardexit
(neuer Helper `_r6_d_launcher_hardexit_addressed_stop_before_guard.py`,
identischer Hardexit-Zeitpunkt wie R5 -- NOCH VOR dem Completed-Guard). Der
Treiber wartet auf ein Signalfile GENAU an dieser Grenze (Statewrite fertig,
Guard noch offen), sendet DANACH `/stop` ueber die ECHTE Kontroll-FIFO (der
nebenlaeufige `_OperatorControlScope`-Kontrollthread verarbeitet sie ueber
den echten Produktweg, `table_admission.request_table_stop`) und wartet,
bis Prozess 1 (der seinerseits auf dieselbe Durabilitaet wartet) hart
beendet. ERST DANACH startet Prozess 2 (derselbe NORMALE, UNGEPATCHTE
Launcher wie bei R5) und vollendet den Primaerrest (Completed-Guard) --
diesmal unter einem BEREITS gesetzten adressierten Stop. Danach dieselbe
vorhandene menschliche Kette wie R5: Resume erreicht die freiwillige lokale
Notiz, '/abbrechen' haelt sie offen, gehaltene Bindungen werden vor Final
gesichert, ein weiterer Prozess schliesst regulaer ab, ein letzter
identischer Retry zeigt volle Bytegleichheit.

GM-Anbieter ist eine Grenzinjektion (FIX5, `MMO_SIM_GM_TRANSPORT_DOUBLE`) --
NIE ein Live-Modelllauf. LITERAL ARGV: KEIN `-c`-Platzhalter.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import drive_r5_t2_evidence_2026_11_05 as r5t2  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path("/home/altair/zr-betreiber-gast-20261105/r6/run/evidence/r6-runs/d_t2")
_RUN_ID = "d_t2_addressed_stop_durable_before_guard_then_resume_completes_committed_plan"
_HARDEXIT_ADDRESSED_STOP_BEFORE_GUARD = _HERE / "_r6_d_launcher_hardexit_addressed_stop_before_guard.py"


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo_1 = fifo_dir / "guest_in_1.fifo"
        out_fifo_1 = fifo_dir / "guest_out_1.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"
        signal_path = root / "primary_write_done_awaiting_stop.json"

        write_test_profile(run_dir, max_turns=200)
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-r6d-guest"
        r5t2._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-r6d-guest-001")
        guest_current_path = run_dir / "current_saves" / "guest1.json"
        versions_dir = run_dir / "current_saves" / "guest1__versions"
        progress_state_path = states_dir / "guest1.json"

        table_id = "local-guest1"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        guard_path = store._completion_guard_path(run_dir, char_id, completion_section_id)

        debrief_save = full_v7_save(char_id, name="Gast-guest1", save_id="fixture-r6d-guest-002", level=2)
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\nSECTION-ABSCHLUSS-BESTAETIGT"
        )
        r5t2._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = dict(r5t2._gm_double_env(cfg_path))
        env.update({
            "MMO_SIM_R6_D_RUN_DIR": str(run_dir), "MMO_SIM_R6_D_TABLE_ID": table_id,
            "MMO_SIM_R6_D_SIGNAL_PATH": str(signal_path), "MMO_SIM_R6_D_WAIT_TIMEOUT": "25",
        })

        # ── Prozess 1 (erweiterte Grenzbarriere): echter Rundenverlauf bis
        # Plan-Pin + Primaersave + Version + Fortschrittszustand, DANACH
        # Warten auf die durable Stop-Bestaetigung (ueber den ECHTEN
        # Kontrollweg, s. Modul-Docstring), ERST DANACH os._exit(94) --
        # NOCH VOR dem Completed-Guard.
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_ADDRESSED_STOP_BEFORE_GUARD),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo_1}:{out_fifo_1}",
        ]
        utc_start1 = r6.utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r5t2._open_guest_fifo_pair(in_fifo_1, out_fifo_1)
        r5t2._wait_for_path(ctrl_fifo, overall=15.0)
        r5t2._drain(out_f1, settle=0.6, overall=10.0)

        r5t2._send_op(proc1, "tisch-anbieten mesaT2")
        time.sleep(0.6)
        r5t2._send_guest(in_f1, "tisch-anfragen mesaT2")
        after_request = r5t2._drain(out_f1, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaT2' gestellt" in l for l in after_request), after_request
        r5t2._send_op(proc1, "tisch-annehmen mesaT2 guest1")
        time.sleep(0.6)
        assert guest_current_path.exists(), "R6/d_t2: tisch-annehmen haette den Startsave (v0001) publizieren muessen."
        version_files_accept = sorted(versions_dir.glob("*.json"))
        assert len(version_files_accept) == 1, (
            f"R6/d_t2: nach Annahme wird GENAU EINE Startversion erwartet: {version_files_accept}"
        )

        r5t2._send_op(proc1, "tisch-start mesaT2")
        r5t2._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r5t2._deliver_guest_turn_answer(in_f1, out_f1, "Ich erkunde die Gegend.")
        second_turn_lines = r5t2._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert "Unbekannte Auswahl" not in "".join(second_turn_lines), (
            f"R6/d_t2: erste Rundenantwort wurde fehlgeleitet: {second_turn_lines}"
        )
        r5t2._deliver_guest_turn_answer(in_f1, out_f1, "Ich gehe weiter.")

        # ── GENAU an der Grenze (Statewrite fertig, Completed-Guard noch
        # offen): Signal abwarten, DANN den echten adressierten Stop ueber
        # die Kontroll-FIFO senden -- WAEHREND Prozess 1 noch lebt und auf
        # GENAU diese Durabilitaet wartet.
        r5t2._wait_for_path(signal_path, overall=25.0)
        utc_stop_sent = r6.utc(time.time())

        # Unabhaengig vom (noch lebenden) Prozess 1 bereits HIER am echten
        # Dateisystem bestaetigen: Primaerteil geschrieben, Guard fehlt noch.
        assert plan_path.exists(), "R6/d_t2: der Plan muss vor dem Primaerschritt real gepinnt sein."
        assert not final_path.exists(), "R6/d_t2: __final.json darf an dieser Grenze noch nicht existieren."
        assert not guard_path.exists(), (
            "R6/d_t2: der Completed-Guard darf an dieser Grenze NOCH NICHT existieren."
        )
        version_files_mid = sorted(versions_dir.glob("*.json"))
        assert len(version_files_mid) == 2, (
            f"R6/d_t2: nach dem Debrief-Primaersave werden GENAU 2 Versionen erwartet: {version_files_mid}"
        )
        decision_mid = admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "plan_committed", decision_mid
        stopped_before_stop_sent, _r = admission.read_table_stop(run_dir, table_id)
        assert stopped_before_stop_sent is False, (
            "R6/d_t2: VOR dem Senden von '/stop' darf noch KEIN durabler Tisch-Stop vorliegen."
        )

        fd = os.open(str(ctrl_fifo), os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write("/stop\n")

        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        assert proc1.returncode == 94, (
            f"R6/d_t2: Prozess 1 muss ueber os._exit(94) ECHT INNERHALB der Primaerpublikation enden, "
            f"ERST NACHDEM der adressierte Stop durabel bestaetigt wurde -- rc={proc1.returncode} "
            f"stderr={stderr1!r}"
        )
        r6.write_process_result(
            _OUT_DIR, "proc1_hardexit_after_addressed_stop_before_guard", argv=argv1, cwd=str(_REPO_ROOT),
            utc_start=utc_start1, utc_end=utc_end1, exit_code=proc1.returncode,
            stdout_text=stdout1, stderr_text=stderr1,
        )
        mf.record_process_files(
            "proc1_hardexit_after_addressed_stop_before_guard",
            aussage="d_t2_proc1_transcript_stop_durable_before_guard", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )

        # ── KERNAUSSAGE D: der adressierte Stop ist JETZT durabel, WAEHREND
        # der Completed-Guard WEITERHIN fehlt -- BEVOR irgendein neuer
        # normaler Prozess ueberhaupt gestartet wurde.
        stopped_after_proc1_exit, stop_reason_after_proc1_exit = admission.read_table_stop(run_dir, table_id)
        assert stopped_after_proc1_exit is True, (
            "R6/d_t2: nach Prozess 1s Exit muss der adressierte Stop durabel bestaetigt sein."
        )
        assert not guard_path.exists(), (
            "R6/d_t2: der Completed-Guard fehlt WEITERHIN -- der Stop wurde VOR der Primaerrest-"
            "Fertigstellung durabel, nicht danach (GENAU die R5-Umkehrung, die hier geschlossen wird)."
        )
        decision_after_proc1_exit = admission.read_table_decision(run_dir, table_id)
        assert decision_after_proc1_exit.get("decision") == "plan_committed", (
            f"R6/d_t2: die bereits gewonnene Planannahme darf durch den Stop NICHT zurueckgerollt "
            f"werden: {decision_after_proc1_exit}"
        )

        before_new_process_boundary = {
            "plan_exists": True, "final_exists": False, "guard_exists": False,
            "decision": decision_after_proc1_exit.get("decision"),
            "table_stop_durable": stopped_after_proc1_exit, "table_stop_reason": stop_reason_after_proc1_exit,
            "version_files": [p.name for p in version_files_mid],
            "note": (
                "Der adressierte Betreiberstop steht hier bereits durabel (table_stop_durable=true), "
                "WAEHREND der Completed-Guard weiterhin fehlt (guard_exists=false) -- BEVOR Prozess 2 "
                "(der naechste normale, ungepatchte Launcher) ueberhaupt gestartet wurde. Das ist die "
                "in STOP-EVIDENCE.md §4.2 geruegte Umkehrung: R5 setzte den Stop ERST NACH bereits "
                "vollstaendiger Primaerpublikation."
            ),
        }
        mf.export_tree(
            run_dir, "before_new_process_boundary_run", aussage="d_t2_boundary_run_stop_already_durable",
            run_id=_RUN_ID, teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )
        mf.export_tree(
            states_dir, "before_new_process_boundary_states",
            aussage="d_t2_boundary_states_stop_already_durable", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "before_new_process_boundary_inventory.json", before_new_process_boundary,
            aussage="d_t2_boundary_inventory_stop_already_durable", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )

        sha_guest_primary_mid = r6.sha256_of(guest_current_path)

        # ── Prozess 2 (literaler Launcher, ECHTER neuer Prozess, G2-
        # Implementierung, KEIN Hardexit-Patch): resumiert denselben
        # gebundenen Tisch UNTER dem bereits durabel gesetzten Stop -- die
        # bereits gewonnene Planannahme wird idempotent zu Ende geharvested
        # (Guard wird jetzt geschrieben, OHNE zweite Version/Publikation).
        in_fifo_2 = fifo_dir / "guest_in_2.fifo"
        out_fifo_2 = fifo_dir / "guest_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(r5t2._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_2}:{out_fifo_2}",
        ]
        utc_start2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv2, cwd=str(_REPO_ROOT), env=r5t2._gm_double_env(cfg_path), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f2, out_f2 = r5t2._open_guest_fifo_pair(in_fifo_2, out_fifo_2)
        r5t2._drain(out_f2, settle=0.6, overall=10.0)
        r5t2._send_op(proc2, "tisch-start mesaT2")
        resume_lines = r5t2._wait_for_marker(out_f2, "eigene lokale Notiz", overall=25.0)
        joined_resume = "".join(resume_lines)
        assert "KI-Leader" not in joined_resume, (
            f"R6/d_t2: der admittierte menschliche Leader darf NICHT als KI-Leader abgelehnt werden: "
            f"{joined_resume}"
        )

        assert guard_path.exists(), (
            "R6/d_t2: der echte Resume (Prozess 2) haette den ausstehenden Completed-Guard idempotent "
            "nachschreiben muessen -- TROTZ bereits durabel gesetztem adressiertem Stop (bereits "
            "gewonnene Planannahme wird NICHT zurueckgerollt)."
        )
        version_files_after_resume = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_after_resume] == [p.name for p in version_files_mid], (
            f"R6/d_t2: der idempotente Resume darf KEINE zusaetzliche Version erzeugen: "
            f"vorher={[p.name for p in version_files_mid]} nachher={[p.name for p in version_files_after_resume]}"
        )
        assert r6.sha256_of(guest_current_path) == sha_guest_primary_mid, (
            "R6/d_t2: der idempotente Resume darf den Primaersave NICHT veraendern."
        )
        decision_after_resume = admission.read_table_decision(run_dir, table_id)
        assert decision_after_resume.get("decision") == "plan_committed", (
            f"R6/d_t2: die Planannahme bleibt auch NACH dem Resume unveraendert erhalten: "
            f"{decision_after_resume}"
        )
        stopped_after_resume, _r2 = admission.read_table_stop(run_dir, table_id)
        assert stopped_after_resume is True, "R6/d_t2: der durable Stop bleibt auch nach dem Resume bestehen."

        r5t2._deliver_guest_turn_answer(in_f2, out_f2, "/abbrechen")
        abbrechen_out = r5t2._wait_for_marker(out_f2, "wird regulaer fertiggestellt", overall=15.0)
        joined_abbrechen = "".join(abbrechen_out)
        assert "Spielstand uebernommen" in joined_abbrechen, joined_abbrechen
        assert "KEIN Verwurf" in joined_abbrechen, joined_abbrechen
        assert "Unbekannte Auswahl" not in joined_abbrechen, abbrechen_out

        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r6.utc(time.time())
        in_f2.close()
        out_f2.close()
        assert proc2.returncode == 0, f"R6/d_t2: Prozess 2 ist unerwartet gescheitert: {stderr2}"
        assert not final_path.exists(), "R6/d_t2: '/abbrechen' an der Notiz darf NICHT finalisieren."
        assert r6.sha256_of(guest_current_path) == sha_guest_primary_mid, (
            "R6/d_t2: '/abbrechen' an der Notiz darf den Primaersave NICHT veraendern."
        )
        r6.write_process_result(
            _OUT_DIR, "proc2_resume_completes_committed_plan_under_durable_stop", argv=argv2,
            cwd=str(_REPO_ROOT), utc_start=utc_start2, utc_end=utc_end2, exit_code=proc2.returncode,
            stdout_text=stdout2, stderr_text=stderr2,
        )
        mf.record_process_files(
            "proc2_resume_completes_committed_plan_under_durable_stop",
            aussage="d_t2_proc2_transcript", run_id=_RUN_ID, teilnehmer_figur="guest1",
            tisch_abschnitt=table_id,
        )

        # ── §4.3-Nachzug (weiterverwendet): gehaltene Bindungen VOR Final
        # als echte Zwischenkoerper.
        held_bindings = r5t2._snapshot_held_bindings(
            run_dir, states_dir, table_id, char_id, completion_section_id,
            guard_path, versions_dir, progress_state_path,
        )
        mf.export_tree(
            run_dir, "held_bindings_run", aussage="d_t2_held_bindings_run", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )
        mf.export_tree(
            states_dir, "held_bindings_states", aussage="d_t2_held_bindings_states", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "held_bindings_before_final.json", held_bindings, aussage="d_t2_held_bindings_before_final",
            run_id=_RUN_ID, teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )

        # ── Prozess 3 (literaler Launcher, echter NEUER Prozess): derselbe
        # Fortsetzen-Weg erreicht die REGULAERE Fertigstellung.
        in_fifo_3 = fifo_dir / "guest_in_3.fifo"
        out_fifo_3 = fifo_dir / "guest_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(r5t2._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_3}:{out_fifo_3}",
        ]
        utc_start3 = r6.utc(time.time())
        proc3 = subprocess.Popen(
            argv3, cwd=str(_REPO_ROOT), env=r5t2._gm_double_env(cfg_path), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f3, out_f3 = r5t2._open_guest_fifo_pair(in_fifo_3, out_fifo_3)
        r5t2._drain(out_f3, settle=0.6, overall=10.0)
        r5t2._send_op(proc3, "tisch-start mesaT2")
        r5t2._wait_for_marker(out_f3, "eigene lokale Notiz", overall=25.0)
        r5t2._deliver_guest_turn_answer(in_f3, out_f3, "Echte freiwillige Abschlussnotiz: alles gut gelaufen.")
        r5t2._wait_for_path(final_path, overall=25.0)
        finish_out = r5t2._drain(out_f3, settle=0.6, overall=10.0)
        assert "Unbekannte Auswahl" not in "".join(finish_out), finish_out
        r5t2._send_op(proc3, "beenden")
        stdout3, stderr3 = proc3.communicate(timeout=30)
        utc_end3 = r6.utc(time.time())
        in_f3.close()
        out_f3.close()
        assert proc3.returncode == 0, f"R6/d_t2: Prozess 3 ist unerwartet gescheitert: {stderr3}"
        assert final_path.exists(), "R6/d_t2: der echte Fortsetzen-Prozess haette __final.json real schreiben muessen."
        r6.write_process_result(
            _OUT_DIR, "proc3_real_finish_via_voluntary_note", argv=argv3, cwd=str(_REPO_ROOT),
            utc_start=utc_start3, utc_end=utc_end3, exit_code=proc3.returncode,
            stdout_text=stdout3, stderr_text=stderr3,
        )
        mf.record_process_files(
            "proc3_real_finish_via_voluntary_note", aussage="d_t2_proc3_transcript", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )

        sha_final = r6.sha256_of(final_path)
        sha_guest_after_finish = r6.sha256_of(guest_current_path)
        version_files_after_finish = sorted(versions_dir.glob("*.json"))
        guest_private_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private_state is not None and guest_private_state.final_save is not None, (
            "R6/d_t2: die abgeschlossene Fassung haette in die private Gastablage geschrieben "
            "werden muessen."
        )
        reflections_path = run_dir / "reflections.jsonl"
        progress_state_after_finish = json.loads(progress_state_path.read_text(encoding="utf-8"))
        private_final_json_after_finish = json.dumps(guest_private_state.final_save, sort_keys=True)
        before_retry = {
            "final_sha256": sha_final, "guest_current_sha256": sha_guest_after_finish,
            "version_files": [p.name for p in version_files_after_finish],
            "version_shas": {p.name: r6.sha256_of(p) for p in version_files_after_finish},
            "progress_state_sha256": r6.sha256_of(progress_state_path),
            "progress_state_rounds_played": progress_state_after_finish.get("rounds_played"),
            "reflections_jsonl_sha256": r6.sha256_of(reflections_path) if reflections_path.exists() else None,
            "private_final_save_sha256": __import__("hashlib").sha256(
                private_final_json_after_finish.encode("utf-8")
            ).hexdigest(),
        }

        # ── Prozess 4 (literaler Launcher, identischer Retry): keine
        # weitere Wirkung.
        in_fifo_4 = fifo_dir / "guest_in_4.fifo"
        out_fifo_4 = fifo_dir / "guest_out_4.fifo"
        argv4 = [
            sys.executable, "-B", str(r5t2._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_4}:{out_fifo_4}",
        ]
        utc_start4 = r6.utc(time.time())
        result4 = subprocess.run(
            argv4, cwd=str(_REPO_ROOT), env=r5t2._gm_double_env(cfg_path),
            input="tisch-start mesaT2\nbeenden\n", capture_output=True, text=True, timeout=30,
        )
        utc_end4 = r6.utc(time.time())
        assert result4.returncode == 0, f"R6/d_t2: identischer Retry-Prozess ist unerwartet gescheitert: {result4.stderr}"
        assert "Tischstart abgelehnt: Tisch 'mesaT2' ist geschlossen" in result4.stdout, result4.stdout
        r6.write_process_result(
            _OUT_DIR, "proc4_identical_retry_no_double_effect", argv=argv4, cwd=str(_REPO_ROOT),
            utc_start=utc_start4, utc_end=utc_end4, exit_code=result4.returncode,
            stdout_text=result4.stdout, stderr_text=result4.stderr,
        )
        mf.record_process_files(
            "proc4_identical_retry_no_double_effect", aussage="d_t2_proc4_transcript", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt=table_id,
        )

        version_files_after_retry = sorted(versions_dir.glob("*.json"))
        progress_state_after_retry = json.loads(progress_state_path.read_text(encoding="utf-8"))
        guest_private_state_after_retry = onboarding.peek(guest_onboarding, "guest1")
        private_final_json_after_retry = json.dumps(guest_private_state_after_retry.final_save, sort_keys=True)
        after_retry = {
            "final_sha256": r6.sha256_of(final_path), "guest_current_sha256": r6.sha256_of(guest_current_path),
            "version_files": [p.name for p in version_files_after_retry],
            "version_shas": {p.name: r6.sha256_of(p) for p in version_files_after_retry},
            "progress_state_sha256": r6.sha256_of(progress_state_path),
            "progress_state_rounds_played": progress_state_after_retry.get("rounds_played"),
            "reflections_jsonl_sha256": r6.sha256_of(reflections_path) if reflections_path.exists() else None,
            "private_final_save_sha256": __import__("hashlib").sha256(
                private_final_json_after_retry.encode("utf-8")
            ).hexdigest(),
        }
        for key in before_retry:
            assert after_retry[key] == before_retry[key], (
                f"R6/d_t2: identischer Retry hat {key!r} veraendert: vorher={before_retry[key]!r} "
                f"nachher={after_retry[key]!r}"
            )

        mf.export_tree(
            run_dir, "run", aussage="d_t2_run_dir_final", run_id=_RUN_ID, teilnehmer_figur="guest1",
            tisch_abschnitt=table_id,
        )
        mf.export_tree(
            states_dir, "states", aussage="d_t2_states_dir_final", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest_onboarding, "guest_onboarding", aussage="d_t2_guest_onboarding_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest_catalog, "guest_catalog", aussage="d_t2_guest_catalog_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="d_t2_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "after_request": after_request, "second_turn_lines": second_turn_lines,
                "resume": joined_resume, "abbrechen": joined_abbrechen, "finish_tail": "".join(finish_out),
            }, aussage="d_t2_io_transcript", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "full_retry_comparison.json", {
                "before_retry": before_retry, "after_retry": after_retry,
                "identical": {k: (before_retry[k] == after_retry[k]) for k in before_retry},
            }, aussage="d_t2_full_retry_comparison", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "d_t2", "aussage": (
                "G5/D (01_NACHZUG.md §D, STOP-EVIDENCE.md §4.2/§4.4): der adressierte Betreiberstop "
                "steht jetzt durabel, SOLANGE der Completed-Guard noch fehlt, BEVOR der naechste "
                "normale Prozess (Prozess 2) ueberhaupt gestartet wurde -- GENAU die Umkehrung der "
                "R5-Reihenfolge. Die bereits gewonnene Planannahme (plan_committed) wird dadurch NICHT "
                "zurueckgerollt: Prozess 2 vollendet den Primaerrest (Completed-Guard) idempotent OHNE "
                "zweite Version. Danach dieselbe vorhandene menschliche Kette: Resume, '/abbrechen', "
                "gehaltene Bindungen vor Final, regulaerer Abschluss, voller identischer Retry-Vergleich."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "utc_stop_sent": utc_stop_sent,
            "table_stop_durable_before_guard": True,
            "decision_preserved_as_plan_committed": True,
            "version_count_stable_through_resume": (
                [p.name for p in version_files_mid] == [p.name for p in version_files_after_resume]
            ),
            "full_retry_comparison_identical": True,
            "assertions_bestanden": [
                "Primaerteil (Current/Version/Fortschritt) geschrieben, Completed-Guard fehlt an der Grenze",
                "VOR dem Senden von '/stop': admission.read_table_stop ist False",
                "echter adressierter Stop ueber die Kontroll-FIFO gesendet, WAEHREND Prozess 1 lebt/wartet",
                "Prozess 1 endet erst NACHDEM der Stop durabel bestaetigt wurde (os._exit(94))",
                "NACH Prozess-1-Exit: Stop durabel=True, Completed-Guard fehlt WEITERHIN, decision bleibt plan_committed",
                "Prozess 2 (normaler Launcher) vollendet den Primaerrest trotz bereits gesetztem Stop idempotent, keine zweite Version",
                "Resume/'/abbrechen'/gehaltene Bindungen/regulaerer Final wie im bestehenden T2-Beleg",
                "letzter identischer Retry: voller Vor-/Nach-Vergleich (Final/Current/Versionen/Fortschritt/Reflexionen/private Fassung) bytegleich",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL d_t2: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK d_t2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
