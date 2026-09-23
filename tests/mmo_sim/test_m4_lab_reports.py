#!/usr/bin/env python3
"""
tests/mmo_sim/test_m4_lab_reports.py — A12 (Singleton/Budget/Stop) + A13
(lokale Reports/Issue-Entwuerfe ohne Modellcall).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.lab.runner import LabBudget, LabRunner, SingletonViolationError, read_status  # noqa: E402
from mmo_sim.reports.report import draft_issues, extract_provenance_excerpts, generate_report  # noqa: E402


def test_a12_singleton_blocks_second_writer_same_run_dir():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "run"
        # eigener echter PID (os.getpid()) garantiert, dass _pid_alive(...) ==
        # True ist -- ein frei erfundener PID koennte im Sandbox-Container
        # zufaellig zu keinem laufenden Prozess gehoeren.
        runner1 = LabRunner(d, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0), pid=os.getpid())
        runner1.start()
        runner2 = LabRunner(d, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0), pid=22222)
        try:
            runner2.start()
            assert False, "zweiter Lab-Lauf auf demselben run_dir haette abgelehnt werden muessen"
        except SingletonViolationError:
            pass
        runner1.release()
        # Nach release() darf ein neuer Lauf starten (kein dauerhafter Lock-Leak).
        runner2.start()
        runner2.release()


def test_a12_singleton_allows_restart_if_previous_pid_is_dead():
    """Ein abgestuerzter Lauf (PID existiert nicht mehr) darf nicht dauerhaft
    einen neuen Lauf blockieren."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "run"
        dead_pid = 999999  # praktisch garantiert nicht vergeben
        runner1 = LabRunner(d, LabBudget(max_turns=10, max_seconds=100, max_usd=1.0), pid=dead_pid)
        runner1.start()
        # KEIN runner1.release() -- simuliert Crash ohne Cleanup.
        runner2 = LabRunner(d, LabBudget(max_turns=10, max_seconds=100, max_usd=1.0), pid=12345)
        runner2.start()  # darf NICHT werfen, da dead_pid nicht mehr lebt


def test_a12_budget_stop_before_next_request():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "run"
        runner = LabRunner(d, LabBudget(max_turns=2, max_seconds=1000, max_usd=10.0), pid=1)
        runner.start()
        should_stop, reason = runner.should_stop()
        assert not should_stop
        runner.record_turn(seconds=1.0, usd=0.1)
        runner.record_turn(seconds=1.0, usd=0.1)
        should_stop, reason = runner.should_stop()
        assert should_stop and "max_turns" in reason
        status = read_status(d)
        assert status.turns_used == 2
        assert status.stop_requested


def test_a12_explicit_stop_flag_wins():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "run"
        runner = LabRunner(d, LabBudget(max_turns=1000, max_seconds=1000, max_usd=1000.0), pid=1)
        runner.start()
        runner.stop("Betreiber hat manuell gestoppt")
        should_stop, reason = runner.should_stop()
        assert should_stop
        assert "manuell" in reason


def test_a13_report_and_issue_drafts_from_events_only_no_model_call():
    events = [
        {"event_id": "e1", "event_type": "sl_turn", "actor": "leader", "payload": {}, "ts": "t1"},
        {"event_id": "e2", "event_type": "section_completed", "actor": None, "payload": {"section_id": "s1"}, "ts": "t2"},
        {"event_id": "e3", "event_type": "section_completion_rejected", "actor": None, "payload": {"reason": "kein Marker"}, "ts": "t3"},
        {"event_id": "e4", "event_type": "provider_auth_missing", "actor": None, "payload": {}, "ts": "t4"},
    ]
    report = generate_report(events)
    assert report.total_events == 4
    assert report.sl_turns == 1
    assert report.sections_completed == 1
    assert report.sections_rejected == 1
    assert report.provider_errors == 1

    drafts = draft_issues(report, events)
    titles = [d.title for d in drafts]
    assert any("Provider-Fehler" in t for t in titles)
    assert any("abgelehnte Abschnittsabschluesse" in t for t in titles)
    assert all(d.evidence_event_ids for d in drafts), "jeder Issue-Entwurf braucht Belegstellen"


def test_a13_provenance_excerpts_find_equipment_boss_combat_drift_mentions():
    """A13 (WEGKARTE §8, 02 §9, 01 §M4): lokale Rohbeleg-Provenienz aus
    unveraenderten `sl_turn`-Texten -- reine Stichwortsuche (keine
    Modellbewertung), mit exakter Fundstelle (event_id/table_id/turn_idx)."""
    events = [
        {"event_id": "e1", "event_type": "sl_turn", "actor": "leader",
         "payload": {"turn_idx": 0, "table_id": "t1", "section_id": "s1", "origin_persona_key": "sniper",
                     "content": "Du greifst zur Waffe und sicherst den Raum."},
         "ts": "t0"},
        {"event_id": "e2", "event_type": "sl_turn", "actor": "leader",
         "payload": {"turn_idx": 1, "table_id": "t1", "section_id": "s1", "origin_persona_key": "sniper",
                     "content": "Der Boss erhebt sich aus dem Schutt und blockt den Ausgang."},
         "ts": "t1"},
        {"event_id": "e3", "event_type": "sl_turn", "actor": "leader",
         "payload": {"turn_idx": 2, "table_id": "t1", "section_id": "s1", "origin_persona_key": "sniper",
                     "content": "Ihr steht bereit und beobachtet die Umgebung."},
         "ts": "t2"},
        {"event_id": "e4", "event_type": "section_completed", "actor": None, "payload": {}, "ts": "t3"},
    ]
    excerpts = extract_provenance_excerpts(events)
    by_category = {ex.category: ex for ex in excerpts}
    assert "ausruestung" in by_category and "Waffe" in by_category["ausruestung"].excerpt
    assert "boss" in by_category and by_category["boss"].event_id == "e2"
    assert "drift" in by_category and by_category["drift"].event_id == "e3"
    assert all(ex.table_id == "t1" for ex in excerpts)
    # section_completed traegt keinen sl_turn-Content -- kein falscher Treffer.
    assert all(ex.event_id != "e4" for ex in excerpts)


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
