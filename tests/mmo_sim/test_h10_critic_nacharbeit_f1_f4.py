#!/usr/bin/env python3
"""
tests/mmo_sim/test_h10_critic_nacharbeit_f1_f4.py — dauerhafte Regressionen
fuer die vier End-Critic-Befunde F1-F4 zum Headless-/Lab-Lobbydurchstich
(Bau-GO 2026-09-27, CRITIC-REPORT.md), alle vom Worker selbst nachgearbeitet
(s. docs/mmo-sim.md "Critic-Nacharbeit (2026-09-27)").

F1 `lab status`/`lab attach` duerfen bei korruptem `lab.status.json` NICHT
   abstuerzen (H-C: 'kein Lauf'/'ungeklaert' statt Traceback).
F2 `--max-wall-seconds` muss vor JEDEM Request frisch geprueft werden
   (persistierte absolute Deadline + `core.admission.read_admission_block`),
   nicht nur einmal pro Lobbyfenster.
F3 `lab status` muss `stop_requested`/`stop_reason` FRISCH berechnen, nicht
   das eingefrorene `LabStatus`-Feld vom letzten `LabRunner._write_status()`
   spiegeln (`LabRunner.stop()`/`request_stop()` schreiben NUR die separate
   Stop-Flag-Datei).
F4 `_cmd_lobby_initiative` muss wie `_cmd_local_round` `exclude_pid=
   os.getpid()` an `active_lock_pid` uebergeben (Selbstblockade-Konsistenz)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.admission import read_admission_block  # noqa: E402
from mmo_sim.lab import cli as lab_cli  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402

from test_l01_l10_lobby_initiative import (  # noqa: E402
    _ScriptedDriver, _bootstrap_community, _make_ready, _session,
)


def test_f1_status_and_attach_report_unklar_instead_of_crashing_on_corrupt_json():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        (run_dir / "lab.status.json").write_text("{ das ist kein JSON", encoding="utf-8")

        payload = lab_cli._status_payload(run_dir)
        assert payload["run"] == "unklar", payload
        assert "beschaedigt" in payload["reason"] or "beschädigt" in payload["reason"], payload
        assert payload["stop_flag_present"] is False

        # Fehlendes Top-Level-Feld -- `LabStatus(**data)` wirft `TypeError`,
        # nicht `JSONDecodeError` -- muss ebenfalls abgefangen werden.
        (run_dir / "lab.status.json").write_text(json.dumps({"running": True}), encoding="utf-8")
        payload2 = lab_cli._status_payload(run_dir)
        assert payload2["run"] == "unklar", payload2


def test_f2_wall_deadline_persisted_and_checked_at_every_request_gate():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        budget = lab_runner.LabBudget(
            max_turns=100, max_seconds=1000.0, max_usd=10.0, max_wall_seconds=3600.0,
        )
        lab = lab_runner.LabRunner(run_dir, budget)
        lab.start()
        try:
            status = lab_runner.read_status(run_dir)
            assert status is not None and status.wall_deadline is not None, status
            now = time.time()
            assert now < status.wall_deadline <= now + 3600.0 + 5.0, status.wall_deadline

            # Noch nicht abgelaufen -- der reale Request-Gate-Check laesst durch.
            blocked, reason = read_admission_block(run_dir)
            assert blocked is False, reason

            # F2-Regression: eine bereits UEBERSCHRITTENE Wall-Clock-Deadline
            # muss den NAECHSTEN echten Request blockieren -- unabhaengig
            # davon, ob gerade ein neues Lobbyfenster beginnt oder nicht (der
            # alte Fehler pruefte dies nur EINMAL PRO FENSTER in
            # `lab.cli._run_controller`, nie am eigentlichen Admission-Gate).
            raw = json.loads((run_dir / "lab.status.json").read_text(encoding="utf-8"))
            raw["wall_deadline"] = time.time() - 1.0
            (run_dir / "lab.status.json").write_text(json.dumps(raw), encoding="utf-8")

            blocked2, reason2 = read_admission_block(run_dir)
            assert blocked2 is True, "abgelaufene Wall-Clock-Deadline muss den naechsten Request blockieren"
            assert "Wall-Clock" in (reason2 or ""), reason2

            # Dieselbe Deadline muss auch `LabRunner.should_stop()` (die
            # Controller-Fensterschleife) erreichen -- direkte In-Memory-
            # Manipulation statt eines unzuverlaessigen echten Sleeps.
            lab._wall_deadline = time.time() - 1.0
            stop, stop_reason = lab.should_stop()
            assert stop is True
            assert "Wall-Clock" in (stop_reason or ""), stop_reason
        finally:
            lab.release()


def test_f2_no_wall_seconds_configured_never_blocks_on_wall_clock():
    """Gegentest: ohne `--max-wall-seconds` (`max_wall_seconds=None`) darf
    NIE eine erfundene Wall-Clock-Grenze zuschlagen (Analogie zu `max_usd
    is None` fuer das Hybrid-Profil)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = lab_runner.LabRunner(
            run_dir, lab_runner.LabBudget(max_turns=100, max_seconds=1000.0, max_usd=10.0),
        )
        lab.start()
        try:
            status = lab_runner.read_status(run_dir)
            assert status.wall_deadline is None, status
            blocked, reason = read_admission_block(run_dir)
            assert blocked is False, reason
        finally:
            lab.release()


def test_f3_stop_requested_reflects_external_request_stop_freshly():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = lab_runner.LabRunner(
            run_dir, lab_runner.LabBudget(max_turns=100, max_seconds=1000.0, max_usd=10.0),
        )
        lab.start()
        try:
            before = lab_cli._status_payload(run_dir)
            assert before["stop_requested"] is False
            assert before["stop_flag_present"] is False

            # ECHTER externer Kontrollweg -- genau das, was `lab stop`
            # aufruft (KEIN `LabRunner`-Objekt, s. H-C).
            lab_runner.request_stop(run_dir, "f3-regression-external-stop")

            after = lab_cli._status_payload(run_dir)
            assert after["stop_flag_present"] is True
            # F3-Regression: vor dem Fix blieb `stop_requested` hier `False`
            # (eingefroren vom letzten `_write_status()`-Aufruf in `start()`),
            # obwohl `stop_flag_present` bereits `True` zeigte -- ein
            # widerspruechliches `lab status`.
            assert after["stop_requested"] is True, after
            assert "f3-regression-external-stop" in (after["stop_reason"] or ""), after

            # Idempotenz: wiederholtes Abfragen bleibt stabil (kein Reset,
            # kein Toggle).
            again = lab_cli._status_payload(run_dir)
            assert again["stop_requested"] is True
        finally:
            lab.release()


def test_f4_lobby_initiative_guard_excludes_own_pid_like_local_round():
    """F4: ein Prozess, der `LabRunner` UND `TuiSession` fuer dasselbe
    `run_dir` selbst konstruiert (wie der akzeptierte Bestandstest
    `test_i2_solo_play_blocked_when_lab_budget_exhausted`, nur ueber den
    `_cmd_lobby_initiative`- statt den `_cmd_local_round`-Pfad), darf sich
    NICHT selbst mit der H-D-Meldung blockieren -- vor dem Fix fehlte
    `exclude_pid` an genau dieser Aufrufstelle."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-f4", keys,
        )
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        lab = lab_runner.LabRunner(
            run_dir, lab_runner.LabBudget(max_turns=100, max_seconds=1000.0, max_usd=10.0),
        )
        lab.start()
        try:
            assert lab_runner.active_lock_pid(run_dir) == os.getpid(), (
                "Vorbedingung: dieser Prozess selbst haelt den Lab-Lock."
            )
            printed: list[str] = []
            session = _session(
                "f4", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
                gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(
                    AssertionError("kein GM-Call erwartet")
                ),
                persona_driver_factory=lambda pk: _ScriptedDriver(pk, ['{"action": "pause"}']),
                printed=printed,
            )
            session._cmd_lobby_initiative()
            out = "\n".join(printed)
            assert "kontrolliert diese Datenablage" not in out, (
                f"F4-Regression: eigener Prozess hat sich selbst am H-D-Guard blockiert:\n{out}"
            )
        finally:
            lab.release()


if __name__ == "__main__":
    import traceback

    tests = [
        test_f1_status_and_attach_report_unklar_instead_of_crashing_on_corrupt_json,
        test_f2_wall_deadline_persisted_and_checked_at_every_request_gate,
        test_f2_no_wall_seconds_configured_never_blocks_on_wall_clock,
        test_f3_stop_requested_reflects_external_request_stop_freshly,
        test_f4_lobby_initiative_guard_excludes_own_pid_like_local_round,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
