#!/usr/bin/env python3
"""
tests/mmo_sim/test_restnachzug_l_tui_20261124_r1.py — PR #3317 Restnachzug
2026-11-24, R1 (RECOVERY_REVIEW.md §1 "normale TUI- und Reflexionspause
erreichen den Recoveryweg nicht durchgaengig", 02_RESTAUFTRAG.md §R R1,
TUI-Konsumseite).

BEFUND (vor dem Fix): im direkten Tischweg `_run_table_round` pruefte die
TUI nach der normalen Rueckgabe NUR `outcome.completion.success`, NIRGENDS
`outcome.recovery_pause` -- das bereits bestehende kostenfreie
Recoverymenue (`_offer_orphan_recovery_menu`) oeffnete sich nur im alten
`except OpenReservationExistsError`-Zweig. Der Catch-up-Zweig
(`_cmd_catch_up_personas`) hatte dieses Signal bereits VORHER bekommen
(tui.py ~2199 `if report.stopped and report.recovery_pause`).

FIX: additiv NACH dem unveraenderten Erfolg/Stop/plan_committed/Pause-Block
in `_run_table_round` -- `if outcome.recovery_pause: self._offer_orphan_
recovery_menu()`. `outcome.recovery_pause` ist `SectionOutcome.recovery_
pause` (`core.runtime.py`) und wird vom Recovery-Worker (Linus-R) auf allen
Produktionspfaden (direkter Gate-Block UND Reflexionsvorsperre vor dem
Modellcall, beide via `blocked_outcome(..., recovery_pause=...)`) gesetzt --
`blocked_outcome` zwingt `completion.success=False`, ein gewoehnlicher
Erfolg kann dieses Feld NIE tragen.

Cross-Worker-Vertrag (einzige geteilte Schnittstelle): dieser Test
VERLAESST SICH NUR auf `SectionOutcome.recovery_pause` -- WIE dieses Feld
in einem echten Lauf gesetzt wird, ist Sache des Recovery-Worker-Pakets
(`core.runtime._RecoveryPause`/`_GateBlocked`, `core.lobby_flow`,
`request_ledger`) und wird hier NICHT nachgebaut. `app_service.
run_play_session` (genau der EINE Aufrufpunkt in `_run_table_round`, s.
dessen Moduldocstring) wird deshalb durch einen kontrollierten, direkt
konstruierten `SectionOutcome` ersetzt -- derselbe Isolationsschnitt, den
`FIX5B`s ProviderQuotaPausedError-Test im Produktcode bereits an genau
dieser Stelle vorsieht. Kein Text-Parsing: die `reason`-Strings in diesem
Test enthalten absichtlich WEDER "unknown" NOCH "recovery", um zu
beweisen, dass die TUI ausschliesslich das Boolean-Feld konsumiert, nicht
den Text.

`_offer_orphan_recovery_menu` selbst (das bereits bestehende, WIEDER-
VERWENDETE Menue -- KEINE zweite Hierarchie, kein neuer Mechanismus) laeuft
in den positiven Faellen UNGEMOCKT -- ein real angelegter Orphan-Request
(`request_ledger.begin`, dieselbe Technik wie `test_rec2_orphan_recovery_
menu_20261123_r1.py::_make_unknown_orphan`, hier lokal dupliziert statt
importiert, da dieses fremde Testmodul nicht angefasst werden darf) belegt,
dass das ECHTE Menue (nicht ein Stub) genau einmal reagiert.

Fixtures: `test_r3_f2_resume_admission_reconcile.py` (Zwei-Menschen-
Tischaufbau, bereits produktiv fuer denselben `_resume_bound_table`-Weg
genutzt) -- kein zweiter Bootstrap-Code. Pure `unittest.TestCase`."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_r3_f2_resume_admission_reconcile as r3f2  # noqa: E402

import mmo_sim.core.app_service as app_service  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.runtime import SectionOutcome  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402


def _make_unknown_orphan(run_dir: Path, *, table_id: str, section_id: str, participant: str) -> str:
    """Dasselbe Produktprimitiv wie `test_rec2_orphan_recovery_menu_
    20261123_r1.py::_make_unknown_orphan` (hier dupliziert, NICHT
    importiert -- jenes Testmodul gehoert einem anderen Worker):
    `request_ledger.begin()` und STOPPT dort -- state bleibt `sent`, der
    echte unbekannte Ausgang, fuer den R1/R2 gelten."""
    return request_ledger.begin(
        run_dir, role="gm_turn", content="SYNTHETIC unbeantworteter R1-TUI-Orphan-Request",
        reserved_usd=0.01, table_id=table_id, section_id=section_id, turn_idx=1, participant=participant,
    )


def _blocked_outcome(*, recovery_pause: bool, reason: str) -> SectionOutcome:
    """Baut GENAU die Rueckgabeform, die `core.runtime.py`s `blocked_
    outcome()` liefert (s. dessen Quelle: `completion.success` IMMER
    `False`, `reason` IMMER mit 'Admission-Gate blockiert: ' praefigiert) --
    OHNE `blocked_outcome` selbst aufzurufen (das ist Recovery-Worker-
    Terrain, `core/runtime.py`)."""
    completion = core_store.CompletionResult(
        success=False, already_completed=False, written=False,
        members_completed=[], missing=[], reason=f"Admission-Gate blockiert: {reason}",
    )
    return SectionOutcome(completion=completion, harvested={}, debrief_text="", recovery_pause=recovery_pause)


def _build_paused_two_human_table(run_dir: Path, states_dir: Path, onboarding_dir: Path, catalog_dir: Path):
    """Baut denselben real gebundenen, aktiven Zwei-Menschen-Tisch wie
    `test_n10_bf4_bf5_resume_and_loadpoint_20261124_r1.py::TestBf4
    ResumeOpenSectionSemantics` (host1 leader, guest1 registrierter
    Mensch-Gast) -- `_run_table_round`s Konsumseite ist fuer R1 unabhaengig
    davon, ob Leader/Gast Mensch oder Persona sind (das Signal kommt aus
    `outcome.recovery_pause`, nicht aus der Mitgliedschaft); der einfachere
    Zwei-Menschen-Aufbau reicht deshalb."""
    write_test_profile(run_dir, max_turns=200)
    r3f2._register_own_figure(
        onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1, run_dir=run_dir, states_dir=states_dir,
    )
    r3f2._register_own_figure(
        onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1, run_dir=run_dir, states_dir=states_dir,
    )
    r3f2._register_human_identity(onboarding_dir, "guest1")

    host_p1 = r3f2._fresh_host_session(
        onboarding_dir, catalog_dir, run_dir, states_dir,
        input_fn=r3f2._pausing_after_consent_input(), gm_transport_factory=lambda: r3f2._NeverClosingGm(),
    )
    guest_session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
        run_dir=run_dir, states_dir=states_dir, host_capable=False,
    )
    host_p1._cmd_table_offer(["mesaR1"])
    guest_session._cmd_table_request_join(["mesaR1"])
    host_p1._cmd_table_accept(["mesaR1", "guest1"])
    try:
        host_p1._cmd_table_start(["mesaR1"])
        raise AssertionError("Tischstart haette per /pause mit EndOfInput enden muessen.")
    except EndOfInput:
        pass

    from mmo_sim.core import table_admission
    bound_section_id = table_admission.load_record(run_dir, "mesaR1").get("section_id")
    assert bound_section_id, "section_id haette trotz Pause gebunden sein muessen."
    return core_store.Table.load(run_dir, bound_section_id)


class TestR1DirectTableRecoveryPauseOpensMenu(unittest.TestCase):
    """R1-Abnahme Teil 1: ein echter normaler Tischcaller mit
    `outcome.recovery_pause=True` oeffnet GENAU EINMAL das bereits
    bestehende kostenfreie Recoverymenue."""

    def test_recovery_pause_true_opens_existing_menu_exactly_once_and_back_is_inert(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)

            orphan_id = _make_unknown_orphan(
                run_dir, table_id=table.table_id, section_id=table.table_id, participant="host1",
            )
            before_snapshot = request_ledger.open_requests(run_dir)
            self.assertIn(orphan_id, {r["id"] for r in before_snapshot})

            # "Zurueck bleibt wirkungslos (keine Aenderung/kein Request)" --
            # R1/02_RESTAUFTRAG §R R1 Abnahme. KEIN "[j/n]"-Treffer fuer
            # irgendeinen Tisch-Konsensdialog noetig: `run_play_session` ist
            # gemockt, es finden KEINE echten Spielzuege/Prompts vor der
            # Outcome-Auswertung statt.
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=lambda prompt="": "/zurueck", print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
                gm_transport_factory=lambda: object(),
                host_capable=True,
            )

            fake_outcome = _blocked_outcome(recovery_pause=True, reason="gate_blocked_without_text_match")
            calls: list[int] = []

            def _fake_run_play_session(*args, **kwargs):
                calls.append(1)
                return fake_outcome

            with patch.object(app_service, "run_play_session", _fake_run_play_session):
                session._resume_bound_table(table)

            self.assertEqual(len(calls), 1, "der gemockte Aufrufpunkt haette genau einmal erreicht werden muessen.")
            out = "\n".join(printed)
            occurrences = out.count("echter unbekannter Ausgang")
            self.assertEqual(
                occurrences, 1,
                f"das bestehende Recoverymenue haette GENAU EINMAL reagieren muessen:\n{out}",
            )
            self.assertIn(
                "Abgebrochen -- keine Aenderung vorgenommen", out,
                f"'/zurueck' am Recovery-Menue haette wirkungslos bleiben muessen:\n{out}",
            )

            after_snapshot = {r["id"]: r for r in request_ledger.open_requests(run_dir)}
            self.assertIn(orphan_id, after_snapshot, "das Original darf durch 'zurueck' NICHT veraendert werden.")
            self.assertEqual(
                after_snapshot[orphan_id]["state"], "sent",
                "'zurueck' darf den offenen Request NICHT in einen autorisierten Folger ueberfuehren.",
            )
            self.assertEqual(
                len(request_ledger.open_requests(run_dir)), len(before_snapshot),
                "'zurueck' darf KEINEN zweiten (Folge-)Request anlegen.",
            )

    def test_recovery_pause_true_with_deny_answer_authorizes_no_retry_either(self):
        """Zweiter Gegenfall derselben Abnahme: 'nein' (statt '/zurueck')
        am Recovery-Menue bleibt GENAUSO wirkungslos -- `_offer_orphan_
        recovery_menu` selbst entscheidet, nicht die TUI-Konsumseite."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)
            orphan_id = _make_unknown_orphan(
                run_dir, table_id=table.table_id, section_id=table.table_id, participant="host1",
            )

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=lambda prompt="": "n", print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
                gm_transport_factory=lambda: object(),
                host_capable=True,
            )
            fake_outcome = _blocked_outcome(recovery_pause=True, reason="gate_blocked_without_text_match")
            with patch.object(app_service, "run_play_session", lambda *a, **k: fake_outcome):
                session._resume_bound_table(table)

            out = "\n".join(printed)
            self.assertEqual(out.count("echter unbekannter Ausgang"), 1, out)
            self.assertIn("Kein neuer Versuch autorisiert", out, out)
            state = {r["id"]: r for r in request_ledger.open_requests(run_dir)}[orphan_id]
            self.assertEqual(state["state"], "sent")


class TestR1ReflectionUnknownAlsoOpensMenu(unittest.TestCase):
    """R1-Abnahme Teil 2: ein Reflexions-Unknown VOR dem Modellcall nutzt
    (laut Cross-Worker-Vertrag) DIESELBE `outcome.recovery_pause`-
    Rueckmeldung -- die TUI-Konsumseite in `_run_table_round` kennt/braucht
    KEINEN separaten Reflexions-Code-Pfad, der 'reason'-Text wird NICHT
    ausgewertet (deshalb hier absichtlich OHNE die Worte 'unknown'/
    'recovery')."""

    def test_reflection_stage_recovery_pause_opens_same_menu_without_text_matching(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)
            _make_unknown_orphan(run_dir, table_id=table.table_id, section_id=table.table_id, participant="guest1")

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=lambda prompt="": "n", print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
                gm_transport_factory=lambda: object(),
                host_capable=True,
            )
            # Bewusst EIN reiner Lauftext ohne "unknown"/"recovery" -- NUR
            # das Boolean-Feld darf das Menue ausloesen.
            fake_outcome = _blocked_outcome(recovery_pause=True, reason="prestage_halt_before_model_dispatch")
            with patch.object(app_service, "run_play_session", lambda *a, **k: fake_outcome):
                session._resume_bound_table(table)

            out = "\n".join(printed)
            self.assertEqual(
                out.count("echter unbekannter Ausgang"), 1,
                f"ein Reflexions-Unknown muss DASSELBE bestehende Menue genau einmal erreichen:\n{out}",
            )


class TestR1OrdinaryBudgetStopOffersNoRecoveryChoice(unittest.TestCase):
    """R1-Abnahme Teil 3: ein gewoehnlicher Budgetstop (`recovery_pause=
    False`, der Default jedes bestehenden Aufrufers) bietet KEINE falsche
    Recoverywahl -- das Menue wird GAR NICHT aufgerufen, unabhaengig davon,
    ob reale Orphans im Run liegen."""

    def test_recovery_pause_false_never_calls_the_recovery_menu(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)
            # Ein real vorhandener Orphan aus einem VOELLIG unabhaengigen
            # Zusammenhang -- selbst DER darf einen gewoehnlichen Budgetstop
            # NICHT in eine Recoverywahl verwandeln (kein pauschales
            # Anzeigen bei JEDEM Stop).
            _make_unknown_orphan(run_dir, table_id="irrelevant-table", section_id="irrelevant-section", participant="host1")

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=lambda prompt="": (_ for _ in ()).throw(AssertionError(f"unerwarteter Prompt: {prompt!r}")),
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
                gm_transport_factory=lambda: object(),
                host_capable=True,
            )
            menu_calls: list[str] = []
            session._offer_orphan_recovery_menu = lambda: menu_calls.append("called")

            fake_outcome = _blocked_outcome(recovery_pause=False, reason="ordinary_budget_stop")
            with patch.object(app_service, "run_play_session", lambda *a, **k: fake_outcome):
                session._resume_bound_table(table)

            self.assertEqual(menu_calls, [], "ein gewoehnlicher Budgetstop darf das Recoverymenue NICHT aufrufen.")
            out = "\n".join(printed)
            self.assertNotIn("echter unbekannter Ausgang", out, out)

    def test_ordinary_success_also_never_calls_the_recovery_menu(self):
        """Gegenprobe: `blocked_outcome` erzwingt `completion.success=
        False`, sodass ein echter Erfolg `recovery_pause` strukturell nie
        tragen kann -- ein normaler Abschlusslauf (gemockter Erfolg) darf
        das Menue ebenfalls nie aufrufen."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=lambda prompt="": "",
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
                gm_transport_factory=lambda: object(),
                host_capable=True,
            )
            menu_calls: list[str] = []
            session._offer_orphan_recovery_menu = lambda: menu_calls.append("called")

            success_outcome = SectionOutcome(
                completion=core_store.CompletionResult(
                    success=True, already_completed=False, written=True,
                    members_completed=["host1", "guest1"], missing=[], reason="",
                ),
                harvested={}, debrief_text="", recovery_pause=False,
            )
            with patch.object(app_service, "run_play_session", lambda *a, **k: success_outcome):
                session._resume_bound_table(table)

            self.assertEqual(menu_calls, [], "ein echter Erfolg darf das Recoverymenue NIE aufrufen.")


class TestR1LobbyInitiativeRecoveryPauseReachesMenu(unittest.TestCase):
    """R1-Abnahme Teil 4 (Gegenpruefung 2026-11-24, 02_RESTAUFTRAG.md §R R1
    WOERTLICH "Dasselbe gilt fuer einen Unknown in der Lobby-Initiative"):
    der TUI-Konsument `_cmd_lobby_initiative` MUSS das von `run_lobby_window`
    gelieferte `LobbyWindowOutcome.recovery_pause` auswerten und dasselbe
    bestehende kostenfreie Recoverymenue erreichen. BEFUND vor dem Fix: er
    verwarf die Rueckgabe vollstaendig (`lobby_flow.run_lobby_window(self)`
    ohne Zuweisung), sodass die bereits korrekt gebaute Signalberechnung
    (`lobby_flow` ~884) und die R4-Fensterbindung den Spieler NIE erreichten.
    Cross-Worker-Vertrag wie die uebrigen R1-Tests: NUR das Boolean-Feld wird
    konsumiert; WIE `run_lobby_window` es in einem echten Lobby-Lauf setzt,
    ist -- genau wie der `run_play_session`-Schnitt der Tischtests -- bewusst
    durch einen kontrollierten Outcome ersetzt (kein Text-Parsing)."""

    def _session(self, d: Path):
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)
        return TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=lambda prompt="": "", print_fn=lambda *a, **k: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
            gm_transport_factory=lambda: object(), host_capable=True,
        )

    def test_lobby_initiative_recovery_pause_true_reaches_menu(self):
        import mmo_sim.core.lobby_flow as lobby_flow
        with tempfile.TemporaryDirectory() as td:
            session = self._session(Path(td))
            menu_calls: list[str] = []
            session._offer_orphan_recovery_menu = lambda: menu_calls.append("called")
            # Bewusst OHNE "unknown"/"recovery" im reason -- nur das Boolean zaehlt.
            outcome = lobby_flow.LobbyWindowOutcome(
                kind=lobby_flow.LobbyOutcomeKind.OPEN_WITH_REASON,
                reason="SYNTHETIC lobby halt before dispatch", recovery_pause=True,
            )
            with patch.object(lobby_flow, "run_lobby_window", lambda *a, **k: outcome):
                session._cmd_lobby_initiative()
            self.assertEqual(
                menu_calls, ["called"],
                "ein Lobby-Unknown muss das bestehende Recoverymenue genau einmal erreichen.",
            )

    def test_lobby_initiative_recovery_pause_false_never_reaches_menu(self):
        import mmo_sim.core.lobby_flow as lobby_flow
        with tempfile.TemporaryDirectory() as td:
            session = self._session(Path(td))
            menu_calls: list[str] = []
            session._offer_orphan_recovery_menu = lambda: menu_calls.append("called")
            outcome = lobby_flow.LobbyWindowOutcome(
                kind=lobby_flow.LobbyOutcomeKind.OPEN_WITH_REASON,
                reason="SYNTHETIC ordinary lobby exit", recovery_pause=False,
            )
            with patch.object(lobby_flow, "run_lobby_window", lambda *a, **k: outcome):
                session._cmd_lobby_initiative()
            self.assertEqual(
                menu_calls, [],
                "ein gewoehnlicher Lobby-Ausgang (Default recovery_pause=False) darf das Menue NICHT aufrufen.",
            )


class TestR1StoppedDispositionSuppressesRecoveryMenu(unittest.TestCase):
    """Gegenpruefung 2026-11-24 (02_RESTAUFTRAG.md §R "gueltige Disposition
    nach abgeschlossenem Settlement beachten"): faellt im direkten Tischweg
    ein `outcome.recovery_pause=True` mit einem bereits durablen, BEWUSSTEN
    Betreiber-Stop (`read_table_decision -> "stopped"`) zusammen, darf KEIN
    zusaetzliches Recoverymenue oeffnen -- die Endentscheidung ist getroffen
    (`_finalize_genuine_table_abort` lief, "ENDGUELTIG beendet (verworfen)"),
    ein Recovery-Angebot widerspraeche ihr (und koennte einen auf dem
    verworfenen Tisch nie konsumierten Folger autorisieren). Die drei
    R1-Pflichtfaelle (decided is None) bleiben unberuehrt -- hier mit der
    Kontrollprobe belegt. `_finalize_genuine_table_abort`/`read_table_
    decision` sind eigene, bereits abgedeckte Belange und werden -- analog
    zum `run_play_session`-Schnitt -- isoliert, um GENAU den neuen Guard
    (`and decided != "stopped"`) zu pruefen."""

    def _menu_calls_for(self, d: Path, decision_value):
        import mmo_sim.core.admission as core_admission
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        table = _build_paused_two_human_table(run_dir, states_dir, onboarding_dir, catalog_dir)
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=lambda prompt="": "", print_fn=lambda *a, **k: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=r3f2._SCHEMA_PATH,
            gm_transport_factory=lambda: object(), host_capable=True,
        )
        menu_calls: list[str] = []
        session._offer_orphan_recovery_menu = lambda: menu_calls.append("called")
        session._finalize_genuine_table_abort = lambda *a, **k: None
        fake_outcome = _blocked_outcome(recovery_pause=True, reason="gate_blocked_without_text_match")
        _decision = {"decision": decision_value} if decision_value is not None else None
        with patch.object(core_admission, "read_table_decision", lambda *a, **k: _decision), \
                patch.object(app_service, "run_play_session", lambda *a, **k: fake_outcome):
            session._resume_bound_table(table)
        return menu_calls

    def test_stopped_disposition_suppresses_menu_even_with_recovery_pause(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                self._menu_calls_for(Path(td), "stopped"), [],
                "ein bewusster Betreiber-Stop darf trotz recovery_pause KEIN Recoverymenue oeffnen.",
            )

    def test_recovery_pause_without_stop_still_opens_menu_control(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                self._menu_calls_for(Path(td), None), ["called"],
                "ohne Stop (decided is None) muss recovery_pause das Menue weiterhin erreichen (R1-Pflichtfall).",
            )


if __name__ == "__main__":
    unittest.main()
