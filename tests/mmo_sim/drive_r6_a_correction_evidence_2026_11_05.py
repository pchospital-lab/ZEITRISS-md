#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_a_correction_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R6, Familie `a_correction` (A/G4, 01_NACHZUG.md §A,
GUEST-PUBLICATION.md §2, 02_NACHWEISE_UND_RUECKGABE.md §2 "innere Antwort-/
Recoveryannahme"): die rein UNGUELTIGE R5D-Antwort deckt den konkret
geaenderten Korrekturzweig (`core/save_correction.py:pursue_single_figure_
correction`, R6-Fix A, zweiter `stop_check`-Recheck NACH `record_correction_
received`/`archive_raw_response` und VOR `mark_adopted`) NICHT ab -- hier wird
der Zweig mit einer SPAET GUELTIGEN Korrekturantwort erreicht, ueber den
ECHTEN Launcher-Subprozess (literal `scripts/mmo_sim.py`), GM-Anbieter NUR
als FIX5-Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`), NIE Live-Modell.

Ablauf (identische Launcher-/FIFO-/GM-Double-Harness wie `drive_r6_a_dialog_
evidence_2026_11_05.py`, aus `drive_r4_evidence_2026_11_04.py` importiert):
Gast startet den Erschaffungsdialog (`gast-erschaffung-dialog operator1`).
Der ERSTE GM-Call liefert sofort einen SCHEMA-UNGUELTIGEN Save-Entwurf (wie
R5D) -- das triggert automatisch die interne Korrekturstrecke (`_attempt_
correction`), OHNE dass der Gast je etwas eintippt. Der ZWEITE GM-Call (der
erste Korrektur-Request, `send_correction_turn`) blockiert und signalisiert
(Double-Stop-Race, `kind=creation`) -- der Betreiber tippt den ECHTEN
`gast-erschaffung-stop guest1`. NACH gewonnenem, durablem Stop liefert der
Double eine VOLLSTAENDIG GUELTIGE Korrekturantwort (dieselbe Figur-ID) --
der neue Recheck in `pursue_single_figure_correction` muss diese trotz
Gueltigkeit ABLEHNEN: `CorrectionOutcome(status='stopped')`, KEINE Adoption,
der aeussere Dialog meldet ebenfalls `status='stopped'`.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
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

import subprocess  # noqa: E402

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.domain.zeitriss.save_correction import creation_repair_key  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path("/home/altair/zr-betreiber-gast-20261105/r6/run/evidence/r6-runs/a_correction")
_RUN_ID = "a_correction_late_valid_answer_after_won_stop_no_adoption"


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"
        signal_path = root / "stop_signal.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-R6A-CORRECTION-GAST"
        participant_id = "guest1"

        invalid_block = full_v7_save(char_id, name="GastR6ACorrection", save_id="fixture-r6a-correction-001")
        invalid_block["economy"] = {"wallets": {char_id: 500}}  # schema-ungueltig -> Korrekturschleife
        invalid_content = "```json\n" + json.dumps(invalid_block, ensure_ascii=False) + "\n```"

        valid_block = full_v7_save(char_id, name="GastR6ACorrection", save_id="fixture-r6a-correction-002")
        valid_content = "```json\n" + json.dumps(valid_block, ensure_ascii=False) + "\n```"

        # Call 1: sofort ungueltiger Entwurf (triggert Korrektur, KEINE
        # Gastinteraktion noetig). Call 2: der ERSTE Korrektur-Request --
        # stoppt waehrend des offenen Aufrufs, liefert DANACH die SPAET
        # GUELTIGE Antwort.
        r4._write_gm_double_config(
            cfg_path, responses=[invalid_content, valid_content], calls_log=calls_log,
            stop={
                "after_call": 2, "kind": "creation", "signal_file": str(signal_path),
                "run_dir": str(run_dir), "operator_id": "operator1", "guest_id": participant_id, "generation": 1,
            },
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{participant_id}:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, f"gast-erschaffung-anfragen operator1")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, f"gast-erschaffung-annehmen {participant_id}")
        time.sleep(0.6)
        grant_before = creation_grants.grant_status(run_dir, participant_id)
        assert grant_before["status"] == "approved" and grant_before["generation"] == 1, grant_before

        repair_key = creation_repair_key(participant_id, char_id)

        # Ein einziger Gastbefehl loest Call1 (ungueltig) -> interne
        # Korrektur -> Call2 (blockiert/signalisiert) aus -- KEINE weitere
        # Gasteingabe noetig/erlaubt.
        r4._send_guest(in_f, "gast-erschaffung-dialog operator1")
        invalid_lines = r4._wait_for_marker(out_f, "[SL]", overall=15.0)
        assert any("SL korrigiert Format" in l or "Versuch 1/" in l for l in
                   r4._drain(out_f, settle=0.6, overall=8.0) + invalid_lines), (
            "R6/a_correction: die ungueltige Erstantwort muss die Korrekturstrecke sichtbar "
            f"anstossen: {invalid_lines}"
        )

        # Double blockiert im ersten Korrektur-Request, signalisiert ->
        # Betreiber tippt den ECHTEN Stop-Befehl.
        r4._wait_for_path(signal_path, overall=15.0)
        utc_stop_sent = r6.utc(time.time())

        # "Vorher"-Koerper des Korrekturdatensatzes: der Request ist
        # abgesandt (begin_attempt -> correction_pending), die Antwort noch
        # NICHT durabel verbucht (Double haengt im Stop-Race).
        record_before = sc.load_record(run_dir, repair_key)
        assert record_before is not None and record_before.get("state") == sc.STATE_CORRECTION_PENDING, (
            f"R6/a_correction: 'vorher' muss den offenen Korrektur-Request (correction_pending) "
            f"zeigen: {record_before}"
        )

        r4._send_op(proc, f"gast-erschaffung-stop {participant_id}")

        terminal_marker = (
            "ein adressierter Betreiber-Stop hat den gemeinsamen Entscheid waehrend der "
            "Save-Korrektur gewonnen"
        )
        terminal_lines = r4._wait_for_marker(out_f, terminal_marker, overall=15.0)
        joined_terminal = "".join(terminal_lines)
        assert (
            "dieser Weg ist terminal, kein weiterer Korrektur-Request, keine Annahme/Publikation"
            in joined_terminal
        ), joined_terminal
        assert "Deine Antwort" not in joined_terminal, terminal_lines

        tail_after_terminal = r4._drain(out_f, settle=0.8, overall=5.0)
        assert "Deine Antwort" not in "".join(tail_after_terminal), tail_after_terminal

        # "Nachher"-Koerper: die SPAET GUELTIGE Antwort wurde durabel
        # empfangen+archiviert (state=correction_received), aber NIE
        # adoptiert/accepted (R6-Fix A griff VOR mark_adopted).
        record_after = sc.load_record(run_dir, repair_key)
        assert record_after is not None and record_after.get("state") == sc.STATE_CORRECTION_RECEIVED, (
            f"R6/a_correction: 'nachher' muss die empfangene, aber NICHT adoptierte Korrekturantwort "
            f"zeigen (state=correction_received, NIE adopted): {record_after}"
        )
        assert record_after.get("attempts_used") == record_before.get("attempts_used"), (
            "R6/a_correction: derselbe Versuchs-Slot (attempts_used) -- kein zweiter Versand nach Stop."
        )

        decision_id = creation_grants._creation_decision_id("operator1", participant_id, 1)
        decision = admission.read_table_decision(run_dir, decision_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 2, (
            f"R6/a_correction: genau 2 GM-Calls erwartet (Initialturn ungueltig + 1 Korrektur-Request, "
            f"danach Stop -- KEIN dritter Request trotz gueltiger Antwort): {gm_calls}"
        )

        requests_dir = run_dir / "requests"
        all_requests = [
            json.loads(p.read_text(encoding="utf-8")) for p in sorted(requests_dir.glob("*.json"))
        ] if requests_dir.is_dir() else []
        assert len(all_requests) == 2, (
            f"R6/a_correction: genau 2 Requests im Ledger erwartet: {all_requests}"
        )
        assert all(r.get("state") == "accounted" and not r.get("error") for r in all_requests), (
            f"R6/a_correction: beide Requests (Initialturn + Korrektur-Request) muessen ehrlich "
            f"'accounted' ohne Fehler verbucht sein: {all_requests}"
        )

        current_path = run_dir / "current_saves" / f"{participant_id}.json"
        assert not current_path.exists(), "R6/a_correction: kein Current-Write nach Stop."
        guest_catalog_dir = op_data / "guests" / participant_id / "catalog"
        assert catalog.list_for_participant(guest_catalog_dir, participant_id) == [], (
            "R6/a_correction: keine Katalogfigur nach Stop (die spaet gueltige Antwort wurde NICHT "
            "adoptiert/publiziert)."
        )

        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"R6/a_correction: Launcher-Lauf ist unerwartet gescheitert: {stderr_text}"

        r6.write_process_result(
            _OUT_DIR, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="a_correction_full_launcher_transcript", run_id=_RUN_ID,
            teilnehmer_figur=participant_id, tisch_abschnitt="creation-operator1-guest1-gen1",
        )
        mf.export_tree(
            run_dir, "run", aussage="a_correction_run_dir_after_stop", run_id=_RUN_ID,
            teilnehmer_figur=participant_id, tisch_abschnitt="creation-operator1-guest1-gen1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="a_correction_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.write_json_body(
            "save_correction_record_before.json", record_before,
            aussage="a_correction_repair_record_before_late_valid_answer", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "save_correction_record_after.json", record_after,
            aussage="a_correction_repair_record_after_stop_no_adoption", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "invalid_lines": invalid_lines, "terminal_lines": terminal_lines,
                "tail_after_terminal": tail_after_terminal,
            }, aussage="a_correction_dialog_io_transcript", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "a_correction", "aussage": (
                "A/G4 innere Antwort-/Recoveryannahme (01_NACHZUG.md §A, GUEST-PUBLICATION.md §2): "
                "der konkret geaenderte Korrekturzweig (core/save_correction.py: pursue_single_figure_"
                "correction, neuer stop_check-Recheck NACH record_correction_received/archive_raw_"
                "response, VOR mark_adopted) wird mit einer SPAET GUELTIGEN Antwort erreicht -- trotz "
                "Gueltigkeit KEINE Adoption/Publikation, CorrectionOutcome(status='stopped'), Dialog "
                "meldet ebenfalls 'stopped'."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "repair_key": repair_key,
            "utc_stop_sent": utc_stop_sent,
            "gm_call_count": len(gm_calls),
            "record_state_before": record_before.get("state"),
            "record_state_after": record_after.get("state"),
            "attempts_used_unchanged": record_after.get("attempts_used") == record_before.get("attempts_used"),
            "decision": decision,
            "current_write": current_path.exists(),
            "catalog_entries": len(catalog.list_for_participant(guest_catalog_dir, participant_id)),
            "assertions_bestanden": [
                "ungueltiger Erstentwurf triggert Korrekturstrecke ohne Gasteingabe",
                "Double blockiert im ersten Korrektur-Request, signalisiert per Datei",
                "record_before.state == correction_pending",
                "echter Stopbefehl waehrend offenem Request gewonnen (decision=stopped)",
                "Double liefert DANACH eine VOLLSTAENDIG GUELTIGE Antwort",
                "record_after.state == correction_received (NIE adopted)",
                "gleicher attempts_used vor/nach (kein zweiter Versand)",
                "genau 2 GM-Calls, genau 2 Requests, beide accounted ohne Fehler",
                "terminal-Meldung erschienen, NIE 'Deine Antwort'",
                "kein Current-Write, keine Katalogfigur",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL a_correction: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK a_correction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
