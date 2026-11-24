#!/usr/bin/env python3
"""
tests/mmo_sim/test_n06r_catchup_recovery_menu_reachable_20261124_r1.py — N06-R
(RECOVERY_REVIEW.md R2 Z.68 "Ueber die normale TUI kostenfrei anzeigen/pruefen
lassen", specialist-team-chain 2026-11-24, Workerin "Juno").

BEFUND (vor dem Fix): `_offer_orphan_recovery_menu()` (von N06/Mara gebaut)
wurde in `ui/tui.py` AUSSCHLIESSLICH beim seltenen `except request_ledger.
OpenReservationExistsError:`-Dead-End (`begin()`s letzte Verteidigungslinie,
Z.11034-11063) angeboten. Der HAEUFIGE Pfad -- eine R1-Vorsperre
(`runtime._RecoveryPause`) waehrend `lobby_flow.play_bound_table` --
mappt auf `LobbyOutcomeKind.STOPPED` (lobby_flow.py:309-320), das
`catchup.py`s bestehender STOPPED-break (Z.260-263) einsammelt, OHNE das
`recovery_pause`-Signal mitzunehmen -- `CatchUpReport` trug es nicht, der
TUI-Vorspielen/Catch-up-Handler (`_cmd_catch_up_personas`, ~Z.1972-2151)
druckte nur eine generische "gestoppt"-Zeile, OHNE das Menue anzubieten.

FIX (rein additiv): `LobbyWindowOutcome.recovery_pause` (Default False) und
`CatchUpReport.recovery_pause` (Default False) transportieren das Signal bis
zur TUI; `_cmd_catch_up_personas` ruft `_offer_orphan_recovery_menu()`
zusaetzlich auf, wenn `report.stopped and report.recovery_pause`.

Methode: direkte Aufrufe von `core.catchup.run_catch_up`/`core.lobby_flow`
(kein echter Modellcall) -- `lobby_flow.run_lobby_window` wird fuer die
Wiring-Tests durch einen kontrollierten `LobbyWindowOutcome` ersetzt (analog
dem bestehenden `on_window`-Diagnose-Hook-Vertrag), fuer den TUI-Test wird
`core.catchup.run_catch_up` selbst durch einen kontrollierten `CatchUpReport`
ersetzt -- dieselbe Fixture-Technik wie `test_rec1_recovery_wiring_20261123_
r1.py` (echte Produktpfade, Mock nur an der aeussersten Grenze) bzw. die
bestehenden `test_p3_catchup_unready_termination_2026_10_21.py`-Community-
Bootstrap-Helfer (`test_l01_l10_lobby_initiative.py::_bootstrap_community`/
`_make_ready`, Reuse statt Neubau).

Pure Python, `unittest.TestCase` (Lauf: `python3 -m unittest tests.mmo_sim.
test_n06r_catchup_recovery_menu_reachable_20261124_r1 -v`)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.core import catchup  # noqa: E402
from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _RecoveryPauseStoppedWindow:
    """Fuer `on_window`/Wiring-Tests: ersetzt `lobby_flow.run_lobby_window`
    fuer GENAU EINEN Aufruf durch einen kontrollierten `LobbyWindowOutcome`
    -- kein echter Tisch, kein Modellcall. `calls` zaehlt, wie oft
    `run_lobby_window` dadurch tatsaechlich ERSETZT (statt echt ausgefuehrt)
    wurde, damit ein Test sich nicht versehentlich auf einen leeren
    Kandidatenlauf (0 Fenster) verlaesst."""

    def __init__(self, outcome: lobby_flow.LobbyWindowOutcome):
        self.outcome = outcome
        self.calls = 0

    def __call__(self, session, ai_personas=None):
        self.calls += 1
        return self.outcome


class _CatchupWiringBase(unittest.TestCase):
    """Eine bereite Persona (`cqb`) in einer eigenen Community, ausgeloest
    von einem davon getrennten `TRIGGER_PK` -- identisches Bootstrap-Muster
    wie `test_p3_catchup_report_unready_field_mixed_selection`."""

    TRIGGER_PK = "n06r_trigger"

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        keys = ["cqb"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, f"community-{self.TRIGGER_PK}", keys,
        )
        l01._make_ready(onboarding_dir, states_dir, run_dir, "cqb")
        self.run_dir = run_dir
        self.session = TuiSession(
            onboarding_dir, catalog_dir, self.TRIGGER_PK,
            input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
            print_fn=lambda line: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        )
        self._orig_run_lobby_window = lobby_flow.run_lobby_window

    def tearDown(self) -> None:
        lobby_flow.run_lobby_window = self._orig_run_lobby_window
        self._td.cleanup()


class TestLobbyFlowCatchupRecoveryPauseWiring(_CatchupWiringBase):
    def test_recovery_pause_stopped_window_marks_catchup_report_recovery_pause_true(self):
        """Kernfall: ein STOPPED-Fenster MIT `recovery_pause=True` (der R1-
        Vorsperre-Fall) muss bis `CatchUpReport.recovery_pause` durchgereicht
        werden."""
        stub = _RecoveryPauseStoppedWindow(lobby_flow.LobbyWindowOutcome(
            kind=lobby_flow.LobbyOutcomeKind.STOPPED,
            reason="R1-Vorsperre: offener Orphan-Requestdatensatz, kein automatischer Blindversuch.",
            recovery_pause=True,
        ))
        lobby_flow.run_lobby_window = stub

        report = catchup.run_catch_up(
            self.session, selected={"cqb"}, current_table_members=set(), target=1,
        )

        self.assertEqual(stub.calls, 1, "run_lobby_window haette genau einmal aufgerufen werden muessen")
        self.assertTrue(report.stopped)
        self.assertTrue(report.recovery_pause, "R1-Vorsperre-STOPPED muss recovery_pause=True transportieren")
        self.assertEqual(
            report.stopped_reason,
            "R1-Vorsperre: offener Orphan-Requestdatensatz, kein automatischer Blindversuch.",
        )

    def test_other_stopped_reason_does_not_mark_recovery_pause_true(self):
        """Gegenprobe (kein Falsch-Positiv): ein ANDERER STOPPED-Grund (z.B.
        Betreiber-Stop/Fenstergrenze, `recovery_pause` auf dem Default
        `False`) darf NICHT als Recovery-Pause erscheinen."""
        stub = _RecoveryPauseStoppedWindow(lobby_flow.LobbyWindowOutcome(
            kind=lobby_flow.LobbyOutcomeKind.STOPPED,
            reason="Sicherheits-Fenstergrenze erreicht -- kontrollierter Abbruch.",
        ))
        lobby_flow.run_lobby_window = stub

        report = catchup.run_catch_up(
            self.session, selected={"cqb"}, current_table_members=set(), target=1,
        )

        self.assertEqual(stub.calls, 1)
        self.assertTrue(report.stopped)
        self.assertFalse(report.recovery_pause, "ein gewoehnlicher STOPPED-Grund ist KEINE Recovery-Pause")

    def test_default_lobby_window_outcome_recovery_pause_is_false(self):
        """Additivitaet: eine `LobbyWindowOutcome`-Konstruktion OHNE
        `recovery_pause`-Keyword (jeder bestehende Aufrufer) bleibt
        unveraendert bei `False`."""
        outcome = lobby_flow.LobbyWindowOutcome(
            kind=lobby_flow.LobbyOutcomeKind.OPEN_WITH_REASON, reason="unveraendert",
        )
        self.assertFalse(outcome.recovery_pause)

    def test_default_catchup_report_recovery_pause_is_false(self):
        """Additivitaet: eine `CatchUpReport`-Konstruktion OHNE
        `recovery_pause`-Keyword (jeder bestehende Aufrufer, z.B. die
        beiden fruehen Return-Pfade vor der Hauptschleife) bleibt
        unveraendert bei `False`."""
        report = catchup.CatchUpReport(
            candidates=[], start_counts={}, end_counts={}, per_target={},
            windows_run=0, stopped=True, stopped_reason="irrelevant", blocked=[],
        )
        self.assertFalse(report.recovery_pause)


class _TuiCatchupMenuBase(unittest.TestCase):
    """Treibt `TuiSession._cmd_catch_up_personas(vorspielen=True)` ECHT an
    (echter Community-Bootstrap, echte `_readline_with_controls`-Eingabe via
    `input_fn`) -- NUR `core.catchup.run_catch_up` wird durch einen
    kontrollierten `CatchUpReport` ersetzt (an der Modulgrenze, wie vom
    Briefing verlangt: "Mock/Stub den `catchup.run_catch_up`-Rueckgabewert").
    `vorspielen=True` (Menuepunkt [5]) vermeidet die zusaetzliche "bereits
    Paritaet"-Fruehausstiegsbedingung von Catch-up [3] -- fuer DIESEN Test
    (reine Signal-Weiterleitung nach dem Report) irrelevant, welcher der
    beiden Ausloeser verwendet wird (s. Briefing: "gilt der Fix fuer beide
    ... ueber dieselbe Zeile")."""

    TRIGGER_PK = "n06r_tui_trigger"

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        keys = ["cqb"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, f"community-{self.TRIGGER_PK}", keys,
        )
        l01._make_ready(onboarding_dir, states_dir, run_dir, "cqb")
        self.printed: list[str] = []
        self._inputs = iter(["cqb"])
        self.session = TuiSession(
            onboarding_dir, catalog_dir, self.TRIGGER_PK,
            input_fn=lambda prompt="": next(self._inputs),
            print_fn=self.printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        )
        self.menu_calls = 0
        self.session._offer_orphan_recovery_menu = self._track_menu_call
        self._orig_run_catch_up = catchup.run_catch_up

    def _track_menu_call(self) -> None:
        self.menu_calls += 1

    def tearDown(self) -> None:
        catchup.run_catch_up = self._orig_run_catch_up
        self._td.cleanup()

    def _stub_report(self, **overrides) -> catchup.CatchUpReport:
        base = dict(
            candidates=["cqb"], start_counts={"cqb": 0}, end_counts={"cqb": 0},
            per_target={"cqb": 1}, windows_run=1, stopped=False, stopped_reason=None,
            blocked=[], notes=[],
        )
        base.update(overrides)
        return catchup.CatchUpReport(**base)


class TestTuiCatchUpHandlerOffersRecoveryMenu(_TuiCatchupMenuBase):
    def test_stopped_with_recovery_pause_offers_menu_exactly_once(self):
        catchup.run_catch_up = lambda *a, **k: self._stub_report(
            stopped=True, stopped_reason="R1-Vorsperre.", recovery_pause=True,
        )

        self.session._cmd_catch_up_personas(vorspielen=True)

        self.assertEqual(self.menu_calls, 1, "report.stopped and report.recovery_pause muss das Menue GENAU EINMAL anbieten")

    def test_stopped_without_recovery_pause_does_not_offer_menu(self):
        """Andere STOPPED-Gruende (Fenstergrenze etc., `recovery_pause`
        Default `False`) loesen das Menue NICHT aus -- unveraendertes
        Verhalten fuer den bestehenden generischen Stop-Druck."""
        catchup.run_catch_up = lambda *a, **k: self._stub_report(
            stopped=True, stopped_reason="Sicherheits-Fenstergrenze erreicht.",
        )

        self.session._cmd_catch_up_personas(vorspielen=True)

        self.assertEqual(self.menu_calls, 0)

    def test_normal_successful_report_does_not_offer_menu(self):
        """Ein normaler, erfolgreicher Report (`stopped=False`) bietet das
        Menue selbstverstaendlich nicht an."""
        catchup.run_catch_up = lambda *a, **k: self._stub_report()

        self.session._cmd_catch_up_personas(vorspielen=True)

        self.assertEqual(self.menu_calls, 0)


if __name__ == "__main__":
    unittest.main()
