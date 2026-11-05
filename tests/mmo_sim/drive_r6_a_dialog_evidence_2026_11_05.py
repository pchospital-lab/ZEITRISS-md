#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_a_dialog_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R6, Familie `a_dialog` (A/G4, 01_NACHZUG.md §A,
GUEST-PUBLICATION.md §2, STOP-EVIDENCE.md §2): schliesst GENAU den von
STOP-EVIDENCE.md geruegten Mergeblocker A1. Aufgesetzt auf der ECHTEN
Launcher-Harness von `drive_r4_evidence_2026_11_04.py` (literal
`scripts/mmo_sim.py`, GM-Anbieter NUR als FIX5-Grenzinjektion
`MMO_SIM_GM_TRANSPORT_DOUBLE`, NIE Live-Modell) -- identisches Muster zu
`drive_r5_evidence_2026_11_05.py::run_family_r5a`, aber mit der dort noch
VERBOTENEN zusaetzlichen Q2-Gastantwort entfernt.

Ablauf: normaler laufender Gastdialog, Q1 beantwortet, Q2-Request offen
(Double blockiert + signalisiert per Datei) -> Betreiber tippt den ECHTEN
`gast-erschaffung-stop guest1`. Q2 kommt verspaetet zurueck und wird ehrlich
verbucht (`[SL] <q2>` wird gedruckt, Request `accounted`). Der NEUE
Stop-Recheck in `core/creation_service.py` (R6-Fix A) greift GENAU danach
und VOR `get_reply` -- der Treiber sendet DESHALB KEINE Gastantwort auf Q2.
Der Dialog muss von SELBST terminal enden (`status=stopped`), OHNE je das
"Deine Antwort: "-Prompt fuer Q2 zu zeigen.

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
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path("/home/altair/zr-betreiber-gast-20261105/r6/run/evidence/r6-runs/a_dialog")
_RUN_ID = "a_dialog_stop_terminal_without_q2_answer"


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
        char_id = "CHR-R6A-DIALOG-GAST"
        final_block = full_v7_save(char_id, name="GastR6ADialog", save_id="fixture-r6a-dialog-guest-001")
        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr praegender Ursprung?"
        final_content = "```json\n" + json.dumps(final_block, ensure_ascii=False) + "\n```"
        # Drei Antworten stehen bereit; die DRITTE (final_content) DARF nach
        # gewonnenem Stop NIE abgerufen werden (identisch zu R5A).
        r4._write_gm_double_config(
            cfg_path, responses=[q1, q2, final_content], calls_log=calls_log,
            stop={
                "after_call": 2, "kind": "creation", "signal_file": str(signal_path),
                "run_dir": str(run_dir), "operator_id": "operator1", "guest_id": "guest1", "generation": 1,
            },
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, "gast-erschaffung-anfragen operator1")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, "gast-erschaffung-annehmen guest1")
        time.sleep(0.6)
        grant_before = creation_grants.grant_status(run_dir, "guest1")
        assert grant_before["status"] == "approved" and grant_before["generation"] == 1, grant_before

        r4._send_guest(in_f, "gast-erschaffung-dialog operator1")
        r4._wait_for_marker(out_f, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_f, "Elena")

        # Double blockiert im Q2-Aufruf, signalisiert -> Betreiber tippt den
        # ECHTEN Stop-Befehl, WAEHREND der zweite Request noch offen ist.
        r4._wait_for_path(signal_path, overall=15.0)
        utc_stop_sent = r6.utc(time.time())
        r4._send_op(proc, "gast-erschaffung-stop guest1")

        # Q2 kommt verspaetet zurueck, wird ehrlich verbucht und gedruckt.
        # Double/Dialog kehren hier so schnell zurueck, dass Q2 und die
        # terminale Meldung oft im selben Lesefenster ankommen -- deshalb
        # direkt auf das jeweils naechste Markerziel warten statt vorher
        # pauschal zu drainen (das wuerde den Marker sonst "verschlucken").
        pre_q2: list[str] = []
        q2_lines = r4._wait_for_marker(out_f, f"[SL] {q2}", overall=15.0)

        # R6-KERNAUSSAGE: der Treiber sendet JETZT KEINE Gastantwort auf Q2.
        # Der neue Stop-Recheck (core.creation_service, R6-Fix A) muss den
        # Dialog von SELBST terminal beenden, OHNE je "Deine Antwort: " fuer
        # Q2 zu zeigen.
        terminal_marker = (
            "Gast-Erschaffungsdialog beendet: ein adressierter Betreiber-Stop hat den "
            "gemeinsamen Entscheid"
        )
        post_q2_lines = r4._wait_for_marker(out_f, terminal_marker, overall=15.0)
        joined_post_q2 = "".join(post_q2_lines)
        assert "Deine Antwort" not in joined_post_q2, (
            f"R6/a_dialog: nach Q2 darf NIE ein neuer Gastantwort-Prompt erscheinen (verbotenes "
            f"R5A-Verhalten) -- gesehen: {post_q2_lines}"
        )
        assert (
            "die soeben empfangene SL-Antwort bleibt verbucht, aber dieser Weg ist terminal: "
            "keine weitere Frage, keine Annahme/Publikation" in joined_post_q2
        ), joined_post_q2

        # Keine weitere Gastzeile wird je gesendet -- der Dialog ist laut
        # Produktaussage bereits terminal. Kurze Nachbeobachtung bestaetigt,
        # dass KEIN weiterer Prompt/Request mehr erscheint, bevor "beenden".
        tail_after_terminal = r4._drain(out_f, settle=0.8, overall=5.0)
        assert "Deine Antwort" not in "".join(tail_after_terminal), tail_after_terminal

        decision_id = creation_grants._creation_decision_id("operator1", "guest1", 1)
        decision = admission.read_table_decision(run_dir, decision_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 2, (
            f"R6/a_dialog: genau 2 GM-Calls erwartet (Q1-Anfrage + Q2-Anfrage, danach terminal "
            f"ohne dritten Request/Antwortversand): {gm_calls}"
        )

        by_turn: dict = {}
        req_dir = run_dir / "requests"
        for p in sorted(req_dir.glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            by_turn.setdefault(data.get("turn_idx"), []).append((p.name, data))
        assert 1 in by_turn and any(d.get("state") == "accounted" for _n, d in by_turn[1]), (
            f"R6/a_dialog: die verspaetete Q2-Antwort (turn_idx=1) muss ehrlich 'accounted' verbucht "
            f"sein: {by_turn.get(1)}"
        )
        assert 2 not in by_turn, (
            f"R6/a_dialog: kein dritter Request (turn_idx=2) erwartet: {sorted(by_turn)}"
        )

        # Konkrete Abwesenheit jeder Annahme-/Publikationswirkung.
        current_path = run_dir / "current_saves" / "guest1.json"
        assert not current_path.exists(), "R6/a_dialog: kein Current-Write nach Stop."
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        assert catalog.list_for_participant(guest_catalog, "guest1") == [], (
            "R6/a_dialog: keine Katalogfigur nach Stop."
        )

        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"R6/a_dialog: Launcher-Lauf ist unerwartet gescheitert: {stderr_text}"

        r6.write_process_result(
            _OUT_DIR, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="a_dialog_full_launcher_transcript", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt="creation-operator1-guest1-gen1",
        )

        # Phasenkoerper (unveraendert) exportieren VOR Tempverzeichnis-Reinigung.
        mf.export_tree(
            run_dir, "run", aussage="a_dialog_run_dir_after_stop", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt="creation-operator1-guest1-gen1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="a_dialog_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "pre_q2": pre_q2, "q2_lines": q2_lines, "post_q2_lines": post_q2_lines,
                "tail_after_terminal": tail_after_terminal,
            }, aussage="a_dialog_dialog_io_transcript", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "a_dialog", "aussage": (
                "A/G4 (01_NACHZUG.md §A, STOP-EVIDENCE.md §2 Mergeblocker A1): nach gewonnenem "
                "Betreiber-Stop beantwortet der Treiber die verspaetete Q2 NICHT mehr -- der neue "
                "Stop-Recheck (core/creation_service.py, nach ehrlicher Verbuchung, vor get_reply) "
                "beendet den Dialog von selbst terminal 'stopped', OHNE je 'Deine Antwort: ' fuer Q2 "
                "zu zeigen und ohne neue Annahme/Publikation."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "utc_stop_sent": utc_stop_sent,
            "gm_call_count": len(gm_calls),
            "request_turn_idxs_present": sorted(k for k in by_turn if k is not None),
            "decision": decision,
            "current_write": current_path.exists(),
            "catalog_entries": len(catalog.list_for_participant(guest_catalog, "guest1")),
            "assertions_bestanden": [
                "Deine Antwort fuer Q2 NIE gezeigt",
                "terminal_marker (R6-Fix-A-Text) erschienen",
                "genau 2 GM-Calls",
                "turn_idx=1 accounted, kein turn_idx=2",
                "decision=stopped",
                "kein Current-Write, keine Katalogfigur",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL a_dialog: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK a_dialog")
    return 0


if __name__ == "__main__":
    sys.exit(main())
