#!/usr/bin/env python3
"""
tests/mmo_sim/test_rec1_recovery_wiring_20261123_r1.py — R1-Abnahme
(RECOVERY_REVIEW.md R1 "Kleinster vollstaendiger Nachzug", PR-#3317-Nachzug
2026-11-23): der tatsaechliche Runtime-/Lobby-/Reflexionsweg konsumiert jetzt
die per `request_ledger.authorize_bound_retry` autorisierte Recovery, statt
sie an `begin()`s Dedup-Pruefung mit `OpenReservationExistsError` zu
verlieren (S1-Befund, gemeldeter `persona_decision`/`turn_idx=45`/`vanguard`-
Fall).

Faehrt die ECHTEN Produktpfade (`core.runtime.SectionRuntime._admitted_
decision`/`submit`/`_collect_reflections`, `core.lobby_service.request_
admitted_decision`) direkt an -- kein Mock AUF diesen Pfaden, nur
`ScriptedDriver`/`_FakeGmTransport` an der aeussersten Treiber-/Transport-
grenze (analog `test_m1_runtime_section.py`). Die Ledger-/Autorisierungs-
kette selbst (`begin`/`dispose_open_orphan`/`authorize_bound_retry`) laeuft
echt gegen `request_ledger.py` (FROZEN, nicht Teil dieses Nachzugs).

Pure Python, `unittest.TestCase` (Lauf: `python3 -m unittest tests.mmo_sim.
test_rec1_recovery_wiring_20261123_r1 -v`)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.request_ledger import OpenReservationExistsError  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime, _RecoveryPause  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)
SECTION_ID = "section-rec1"


class ScriptedDriver:
    """Minimaler Fake-Treiber -- identisch im Vertrag zu `test_m1_runtime_
    section.py:ScriptedDriver` (eigene, kleine Kopie statt Cross-Test-Import,
    damit diese Datei wie die uebrigen Testdateien dieses Verzeichnisses
    eigenstaendig bleibt)."""

    def __init__(self, script: list[ParticipantDecision]):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


class _FakeGmTransport:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        content = self._contents.pop(0) if self._contents else "SL-Antwort."
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake-chat"}


def _no_harvest(debrief_text: str, cid_to_pk: dict[str, str]) -> dict:
    return {}


class _Rec1Base(unittest.TestCase):
    """Gemeinsamer Tisch (Leader `leader_pk` + Persona `vanguard`) -- `vanguard`
    ist absichtlich derselbe Persona-Key wie im gemeldeten R1-Fall."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        self.run_dir = root / "run"
        self.states_dir = root / "states"
        self.states_dir.mkdir(parents=True)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        self.ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        self.lobby = store.Lobby(self.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        self.lobby.join("leader_pk")
        self.lobby.join("vanguard")
        self.table, derivation = store.create_table_from_offer_log(
            self.lobby, "t-rec1",
            offer_log_events=[
                {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["vanguard"]},
                {"type": "consent", "offer_id": "o1", "from": "vanguard", "accept": True},
            ],
            chrononaut_ids={"leader_pk": "chrono-leader", "vanguard": "chrono-vanguard"},
        )
        self.assertIsNotNone(self.table, f"Tisch haette entstehen muessen: {derivation}")
        write_test_profile(self.run_dir)
        # `_collect_reflections` committet in einen Persona-State -- ohne
        # geseedeten State scheitert `load_state` mit `FileNotFoundError`
        # (eigene, von der Vorsperre UNABHAENGIGE Fehlerquelle) und wuerde
        # die Reflexions-Tests faelschlich ueber den Statewrite-Pfad statt
        # ueber die eigentlich getestete Vorsperre/den Orphan-Dreischritt
        # scheitern lassen.
        for pk, chrono_id in (("leader_pk", "chrono-leader"), ("vanguard", "chrono-vanguard")):
            self.ps_store.save_state(pk, {
                "v": 2, "persona_key": pk, "rounds_played": 0,
                "plays_char": {"character_id": chrono_id, "name": "Test"},
            }, states_dir=self.states_dir)

    def tearDown(self) -> None:
        self._td.cleanup()

    def _make_runtime(self, gm_transport, drivers: dict) -> tuple[SectionRuntime, TableController]:
        controller = TableController(leader_key="leader_pk", drivers=drivers)
        runtime = SectionRuntime(
            lobby=self.lobby, table=self.table, gm_transport=gm_transport,
            marker="MARKER-UNUSED", harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=self.ps_store, harvest_extractor=_no_harvest,
        )
        runtime._current_section_id = SECTION_ID
        runtime._states_dir = self.states_dir
        return runtime, controller

    def _make_authorized_orphan(self, *, role: str, turn_idx: int, participant: str) -> str:
        """Baut GENAU den S1-Befund nach: `begin()` legt `state=sent` an,
        der Transportabschluss (`finish_received`/`finish_error`) wird NIE
        erreicht (simulierter Absturz) -- `dispose_open_orphan` +
        `authorize_bound_retry` (beide FROZEN/echt, Teil der bereits
        vorhandenen R2-Ledgerbausteine) liefern GENAU den autorisierten,
        `reserved`/`recovery_of`-Folger, den der Caller jetzt konsumieren
        muss."""
        original_id = request_ledger.begin(
            self.run_dir, role=role, content=f"wire-text-{role}-{turn_idx}",
            reserved_usd=0.01, route=None, output_limit_tokens=None,
            table_id=self.table.table_id, section_id=SECTION_ID,
            turn_idx=turn_idx, participant=participant, dollar_billed=True,
        )
        request_ledger.dispose_open_orphan(
            self.run_dir, original_id, reason="S1-Befund: Absturz zwischen Versandmarker und Antwort.",
        )
        retry_id = request_ledger.authorize_bound_retry(self.run_dir, original_id)
        self.assertNotEqual(retry_id, original_id)
        return retry_id

    def _make_unauthorized_orphan(self, *, role: str, turn_idx: int, participant: str) -> str:
        """Gegenfall: derselbe `state=sent`-Absturz, aber OHNE jede
        Dispose-/Autorisierungsentscheidung -- der Ausgang bleibt bewusst
        unbekannt."""
        return request_ledger.begin(
            self.run_dir, role=role, content=f"wire-text-{role}-{turn_idx}",
            reserved_usd=0.01, route=None, output_limit_tokens=None,
            table_id=self.table.table_id, section_id=SECTION_ID,
            turn_idx=turn_idx, participant=participant, dollar_billed=True,
        )

    def _make_answered_without_text(self, *, role: str, turn_idx: int, participant: str) -> str:
        """R1-Gegenfall: ein bereits VOLLSTAENDIG abgerechneter (state=
        accounted) Request OHNE rekonstruierbaren Text -- erscheint NICHT in
        `open_requests()` (kein `reserved`/`sent` mehr), die fruehe Round-
        Vorsperre (Zeile ~630) trifft ihn deshalb NICHT; `_admitted_decision`
        findet ihn erst ueber `find_answered_without_text` und wirft dort
        `_RecoveryPause` -- GENAU der Pfad, den R1s Fix (`recovery_pause =
        isinstance(e, _RecoveryPause)`) jetzt vom gewoehnlichen `_GateBlocked`
        unterscheiden muss."""
        request_id = request_ledger.begin(
            self.run_dir, role=role, content=f"wire-text-{role}-{turn_idx}",
            reserved_usd=0.01, route=None, output_limit_tokens=None,
            table_id=self.table.table_id, section_id=SECTION_ID,
            turn_idx=turn_idx, participant=participant, dollar_billed=True,
        )
        request_ledger.finish_received(self.run_dir, request_id, usage={}, seconds=0.1)
        return request_id


class TestPersonaDecisionTurn45Vanguard(_Rec1Base):
    """R1-Hauptfall: `persona_decision`/`turn_idx=45`/`vanguard`."""

    def test_authorized_follower_consumed_exactly_once_reaches_transport(self):
        retry_id = self._make_authorized_orphan(role="persona_decision", turn_idx=45, participant="vanguard")
        driver = ScriptedDriver([ParticipantDecision(text="vanguard entscheidet.", origin_source="fake:vanguard")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": driver,
        })
        runtime._turn_idx = 45

        record = runtime._admitted_decision("persona_decision", controller, "vanguard", {"user": "ctx"})

        self.assertEqual(driver.calls, 1, "der Transport/Treiber wurde tatsaechlich erreicht, kein zweiter Pause-Abbruch")
        self.assertEqual(record.decision.text, "vanguard entscheidet.")
        retry_record = request_ledger.load_request(self.run_dir, retry_id)
        self.assertEqual(retry_record["state"], "accounted", "GENAU EINMAL via commit_authorized_retry+finish_received konsumiert")
        # Exakt EIN Record fuer diese Identitaet wurde NEU durch diesen Aufruf veraendert
        # (der autorisierte Folger) -- kein zweiter, zusaetzlicher `begin()`-Record.
        matches = [
            d for d in request_ledger._all_records(self.run_dir)
            if d.get("table_id") == self.table.table_id and d.get("section_id") == SECTION_ID
            and d.get("role") == "persona_decision" and d.get("turn_idx") == 45 and d.get("participant") == "vanguard"
        ]
        self.assertEqual(len(matches), 2, "Original (disponiert) + autorisierter Folger -- kein dritter Record")

    def test_fresh_reentry_after_successful_decision_reuses_it_zero_second_requests(self):
        """R2 (RECOVERY_REVIEW R2 "erfolgreiche Personaantwort geht beim
        frischen Eintritt weiterhin verloren"): Personaantwort erhalten ->
        (simulierter) Gatepause/Crash vor GM -> frischer Runtime-Eintritt
        derselben Section/Identitaet -> dieselbe Entscheidung EINMAL
        weiterverwenden, NULL zweite Personarequests (ABNAHME-Wortlaut).
        `turn_idx` bleibt zwischen beiden Aufrufen unveraendert, weil der
        reale Caller (`act()`) ihn erst NACH dem naechsten Gate (vor GM)
        erhoeht -- ein Crash GENAU dort trifft beim Re-Entry dieselbe
        Identitaet erneut."""
        driver = ScriptedDriver([
            ParticipantDecision(
                text="vanguard entscheidet (einmalig).", origin_source="fake:vanguard",
                save_payload={"note": "erhalten"},
            ),
        ])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": driver,
        })
        runtime._turn_idx = 45

        first = runtime._admitted_decision("persona_decision", controller, "vanguard", {"user": "ctx"})
        self.assertEqual(driver.calls, 1)
        self.assertEqual(first.decision.text, "vanguard entscheidet (einmalig).")

        # Simulierter Crash/Gatepause VOR dem GM-Turn (runtime.py ~1516-1525,
        # s. RECOVERY_REVIEW R2): frischer Prozess, NEUE SectionRuntime,
        # dieselbe Section/Identitaet, derselbe `turn_idx` (noch nicht
        # erhoeht). Der Treiber wuerde bei JEDEM Aufruf eine Ausnahme
        # werfen -- ein zweiter Personarequest faellt damit sofort auf.
        class _ExplodingDriver:
            def decide(self, context):
                raise AssertionError(
                    "R2: frischer Eintritt haette die bereits erhaltene Entscheidung "
                    "wiederverwenden muessen, kein zweiter Modellaufruf."
                )

        runtime2, controller2 = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": _ExplodingDriver(),
        })
        runtime2._turn_idx = 45

        second = runtime2._admitted_decision("persona_decision", controller2, "vanguard", {"user": "ctx"})

        self.assertEqual(
            second.decision.text, "vanguard entscheidet (einmalig).",
            "R2-FIX: dieselbe durabel gebundene Entscheidung muss rekonstruiert zurueckgegeben werden",
        )
        self.assertEqual(second.decision.origin_source, "fake:vanguard")
        self.assertEqual(second.decision.save_payload, {"note": "erhalten"})
        retry_record = request_ledger.load_request(
            self.run_dir,
            next(
                d["id"] for d in request_ledger._all_records(self.run_dir)
                if d.get("table_id") == self.table.table_id and d.get("section_id") == SECTION_ID
                and d.get("role") == "persona_decision" and d.get("turn_idx") == 45
                and d.get("participant") == "vanguard"
            ),
        )
        self.assertEqual(retry_record["state"], "accounted")
        self.assertIsNotNone(retry_record["result_text"], "R2-FIX: result_text muss dauerhaft persistiert sein")

    def test_without_authorization_pauses_typed_no_second_begin_original_untouched(self):
        orphan_id = self._make_unauthorized_orphan(role="persona_decision", turn_idx=45, participant="vanguard")
        before = dict(request_ledger.load_request(self.run_dir, orphan_id))
        driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": driver,
        })
        runtime._turn_idx = 45

        with self.assertRaises(_RecoveryPause):
            runtime._admitted_decision("persona_decision", controller, "vanguard", {"user": "ctx"})

        self.assertEqual(driver.calls, 0, "kein Modellaufruf ohne bewusste Recovery-Entscheidung")
        after = request_ledger.load_request(self.run_dir, orphan_id)
        self.assertEqual(after, before, "Originalrecord bleibt bytegleich unberuehrt")
        matches = [
            d for d in request_ledger._all_records(self.run_dir)
            if d.get("table_id") == self.table.table_id and d.get("section_id") == SECTION_ID
            and d.get("role") == "persona_decision" and d.get("turn_idx") == 45 and d.get("participant") == "vanguard"
        ]
        self.assertEqual(len(matches), 1, "kein zweiter begin()-Record angelegt")

    def test_pre_fix_regression_proof_raw_begin_raises_openreservationexists(self):
        """Gegenprobe zur Spezifikation: ruft man `begin()` (den alten,
        unverdrahteten Weg) DIREKT fuer dieselbe Identitaet auf, wirft
        `request_ledger` selbst weiterhin unveraendert `OpenReservationExistsError`
        -- `begin()`s eigene Dedup-Pruefung ist bewusst NICHT angefasst
        worden (letzte Verteidigungslinie)."""
        self._make_authorized_orphan(role="persona_decision", turn_idx=45, participant="vanguard")
        with self.assertRaises(OpenReservationExistsError):
            request_ledger.begin(
                self.run_dir, role="persona_decision", content="erneuter blinder Versuch",
                reserved_usd=0.01, table_id=self.table.table_id, section_id=SECTION_ID,
                turn_idx=45, participant="vanguard", dollar_billed=True,
            )


class TestGuestPollAnalog(_Rec1Base):
    def test_guest_poll_authorized_follower_consumed(self):
        retry_id = self._make_authorized_orphan(role="guest_poll", turn_idx=3, participant="vanguard")
        driver = ScriptedDriver([ParticipantDecision(text="Gast-Poll-Antwort.")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": driver,
        })
        runtime._turn_idx = 3

        record = runtime._admitted_decision("guest_poll", controller, "vanguard", {"user": "ctx"})

        self.assertEqual(driver.calls, 1)
        self.assertEqual(record.decision.text, "Gast-Poll-Antwort.")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")


class TestReflectionAnalog(_Rec1Base):
    def test_reflection_vorsperre_exempts_authorized_follower_and_consumes_it(self):
        retry_id = self._make_authorized_orphan(role="reflection", turn_idx=1, participant="vanguard")
        leader_driver = ScriptedDriver([ParticipantDecision(text="Leader-Reflexion.")])
        vanguard_driver = ScriptedDriver([ParticipantDecision(text="vanguard-Reflexion (autorisierter Folger).")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        self.assertTrue(ok, f"Vorsperre haette den autorisierten Folger NICHT mehr blockieren duerfen: {pause_reason}")
        self.assertFalse(recovery_pause, "kein Stop, also auch keine Recovery-Pause")
        self.assertEqual(vanguard_driver.calls, 1, "autorisierter Folger wurde tatsaechlich real befragt")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")

    def test_reflection_second_entry_after_follower_accounted_no_longer_blocked(self):
        """R3 (RECOVERY_REVIEW R3 "Disposition auch nach erfolgreichem Child
        auswerten"): Fortsetzung von `test_reflection_vorsperre_exempts_
        authorized_follower_and_consumes_it` -- der vorhandene Test endete
        bisher nach dem ERSTEN erfolgreichen `_collect_reflections`-Aufruf
        und deckte den ZWEITEN Eintritt nicht ab (briefing-Beleg). Nach dem
        ersten Aufruf ist der autorisierte Folger `accounted` (nicht mehr
        `reserved`) -- er verschwindet aus `open_requests()`, und das
        bytegleiche `sent`-Original (`retry_id`s `recovery_of`-Ziel) ist
        damit VOR dem R3-Fix wieder ein Blocker fuer die GESAMTE Runde,
        obwohl beide Mitglieder bereits erfolgreich reflektiert haben. Ein
        frischer zweiter Eintritt (neue `SectionRuntime`-Instanz, derselbe
        `run_dir`/Tisch -- simuliert einen Crash VOR dem finalen Abschluss
        und einen neuen Prozess) muss schliessen, OHNE auch nur einen
        weiteren Modellaufruf auszuloesen."""
        retry_id = self._make_authorized_orphan(role="reflection", turn_idx=1, participant="vanguard")
        leader_driver = ScriptedDriver([ParticipantDecision(text="Leader-Reflexion.")])
        vanguard_driver = ScriptedDriver([ParticipantDecision(text="vanguard-Reflexion (autorisierter Folger).")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })
        runtime._turn_idx = 1
        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )
        self.assertTrue(ok, f"Erster Aufruf haette schliessen muessen: {pause_reason}")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")

        # Zweiter, frischer Eintritt -- NEUE SectionRuntime-Instanz, FRISCHE
        # Treiber, die bei JEDEM Aufruf eine Ausnahme werfen (kein Skript-
        # Eintrag): ein echter weiterer Modellaufruf wuerde sofort auffallen.
        class _ExplodingDriver:
            def decide(self, context):
                raise AssertionError(
                    "zweiter Eintritt haette KEINEN weiteren Modellaufruf auslösen duerfen "
                    "(beide Mitglieder bereits erfolgreich reflektiert, R3-Disposition "
                    "muss das bytegleiche sent-Original jetzt ausnehmen)."
                )

        runtime2, controller2 = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": _ExplodingDriver(), "vanguard": _ExplodingDriver(),
        })
        runtime2._turn_idx = 1
        ok2, pause_reason2, recovery_pause2 = runtime2._collect_reflections(
            controller2, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )
        self.assertTrue(
            ok2,
            f"R3: zweiter Eintritt nach erfolgreich accounted-em Folger darf nicht mehr "
            f"blockieren (bytegleiches Original waere sonst wieder Blocker): {pause_reason2}",
        )
        self.assertFalse(recovery_pause2)
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")

    def test_reflection_vorsperre_open_unknown_now_carries_recovery_signal(self):
        """R1/R3 (PR #3317-Nachzug r2, RECOVERY_REVIEW.md §1 "die fruehe
        Unknown-Sperre als Recoveryausgang weiterreichen"): ein echter offener
        `sent`-Reflection-Unknown fuer diese Table/Section OHNE gueltige
        Grantbindung haelt die Runde weiterhin (ok=False, kein Mitglied neu
        befragt), traegt aber JETZT das Recovery-Signal (`recovery_pause=True`)
        statt stillem `(False, None, False)` -- `finalize`/TUI erreichen damit
        das bestehende Recovery-Menue. Vorher erwartete dieser Test
        ausdruecklich `recovery_pause=False` (das war genau der vom Review
        benannte verschluckte Fall). `pause_reason` bleibt None: es ist der
        fruehe Round-Vorsperren-Ausgang, kein per-Mitglied `_GateBlocked`."""
        self._make_unauthorized_orphan(role="reflection", turn_idx=1, participant="vanguard")
        leader_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        vanguard_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        # Rohe Rueckgabe des realen Callers (kein gemockter Zwischenwert):
        print(f"[R1-vorsperre-raw] ok={ok!r} pause_reason={pause_reason!r} recovery_pause={recovery_pause!r}")
        self.assertFalse(ok)
        self.assertIsNone(pause_reason, "fruehe Round-Vorsperre, kein per-Mitglied _GateBlocked")
        self.assertTrue(
            recovery_pause,
            "R1: die fruehe Unknown-Sperre traegt jetzt das Recovery-Signal (Menue erreichbar)",
        )
        self.assertEqual(leader_driver.calls, 0)
        self.assertEqual(vanguard_driver.calls, 0)

    def test_reflection_member_level_recovery_pause_sets_flag_for_finalize(self):
        """R1 (RECOVERY_REVIEW R1 "Reflexionsvorsperre verliert die
        Recovery-Unterscheidung"): ein bereits VOLLSTAENDIG abgerechneter
        Reflexionsrequest ohne rekonstruierbaren Text (`find_answered_
        without_text`) erreicht NICHT die fruehe Round-Vorsperre (die nur
        `open_requests()`, also `reserved`/`sent`, kennt) -- `_admitted_
        decision` wirft fuer GENAU dieses Mitglied `_RecoveryPause` beim
        Betreten der Pro-Mitglied-Schleife. Vor dem Fix reduzierte der
        `except _GateBlocked`-Fang dies auf einen gewoehnlichen `pause_
        reason`-String und verlor die Unterscheidung (`finalize()` haette
        `SectionOutcome.recovery_pause` NIE auf `True` setzen koennen) --
        jetzt muss `recovery_pause` selbst `True` sein."""
        self._make_answered_without_text(role="reflection", turn_idx=1, participant="vanguard")
        leader_driver = ScriptedDriver([ParticipantDecision(text="Leader-Reflexion.")])
        vanguard_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        self.assertFalse(ok)
        self.assertIsNotNone(pause_reason)
        self.assertTrue(
            recovery_pause,
            "R1-FIX: ein echter _RecoveryPause waehrend der Reflexion muss recovery_pause=True "
            "liefern, damit finalize() SectionOutcome.recovery_pause korrekt setzen kann.",
        )
        self.assertEqual(vanguard_driver.calls, 0, "kein Modellaufruf fuer eine bereits abgerechnete Operation")

    def test_reflection_ordinary_budget_block_during_round_does_not_set_recovery_pause(self):
        """Gegenprobe zum vorigen Test: ein GEWOEHNLICHER Admission-/
        Budget-Stop (kein Ledger-Unknown) waehrend der Reflexionsrunde darf
        `recovery_pause` NICHT auf `True` setzen -- `_check_gate`/der
        normale `_GateBlocked`-Pfad in `_admitted_decision` wirft niemals
        `_RecoveryPause`."""
        write_test_profile(self.run_dir, max_usd=0.0)
        leader_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        vanguard_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        self.assertFalse(ok)
        self.assertIsNotNone(pause_reason)
        self.assertFalse(recovery_pause, "ein gewoehnlicher Budget-Stop ist KEINE Recovery-Pause")
        self.assertEqual(leader_driver.calls, 0)
        self.assertEqual(vanguard_driver.calls, 0)

    # --- PR #3317-Nachzug r2 (RECOVERY_REVIEW.md §1/§2) ---------------------
    def _seed_members_reflected(self):
        """Beide Mitglieder im Archiv als bereits reflektiert markieren --
        isoliert die Vorsperre: nach ihr ist die Mitgliederschleife ein
        No-op, sodass das Ergebnis AUSSCHLIESSLICH vom Vorsperren-/Settlement-
        Pfad bestimmt wird."""
        path = self.run_dir / "reflections.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            for pk in ("leader_pk", "vanguard"):
                fh.write(json.dumps({
                    "persona_key": pk, "section_id": SECTION_ID, "ts": "seed", "text": "x",
                    "origin_source": "seed", "kind": "ai_required_reflection",
                }, ensure_ascii=False) + "\n")

    def _make_received_reflection_follower(self, *, with_duration: bool):
        """Autorisierter Reflection-Folger, der tatsaechlich empfangen wurde
        (`finish_received`), dessen abschliessender `accounted`-Markerwrite
        aber unterbrochen wurde -- Record bleibt `received`. `with_duration`
        steuert, ob die urspruengliche Antwortdauer bekannt ist."""
        retry_id = self._make_authorized_orphan(role="reflection", turn_idx=1, participant="vanguard")
        request_ledger.commit_authorized_retry(
            self.run_dir, retry_id, content="reflektion-wire", reserved_usd=0.01,
        )
        request_ledger.finish_received(
            self.run_dir, retry_id, usage={}, seconds=1.0, result_text="vanguard-reflexion",
        )
        rec = request_ledger.load_request(self.run_dir, retry_id)
        rec["state"] = "received"  # accounted-Markerwrite verloren (Review-Witness §1)
        if not with_duration:
            rec.pop("received_seconds", None)  # A1: unbekannte Dauer -> ehrliches HOLD
        request_ledger._write_request(self.run_dir, retry_id, rec)
        return retry_id

    def test_reflection_vorsperre_settles_bound_received_follower_then_proceeds(self):
        """R1/R3 (RECOVERY_REVIEW.md §1): ein korrekt VOLL gebundener
        `received`-Folger mit bekannter Dauer, dessen `accounted`-Markerwrite
        unterbrochen wurde, wird von der Vorsperre ueber den vorhandenen
        idempotenten `settle_received` kostenfrei abgeschlossen (KEIN
        Modellcall) -- danach raeumt die accounted-Ausnahme das Original und
        die Runde laeuft normal weiter."""
        retry_id = self._make_received_reflection_follower(with_duration=True)
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "received")
        self._seed_members_reflected()
        exploding = ScriptedDriver([])  # jeder Aufruf wuerde "Skript erschoepft" werfen
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": exploding, "vanguard": exploding,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        print(f"[R1-received-settle-raw] ok={ok!r} recovery_pause={recovery_pause!r} "
              f"child_state={request_ledger.load_request(self.run_dir, retry_id)['state']!r}")
        self.assertEqual(
            request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted",
            "R1: die Vorsperre hat den received-Folger kostenfrei nach accounted gesettled",
        )
        self.assertTrue(ok, f"nach Settlement keine Sperre mehr: {pause_reason}")
        self.assertFalse(recovery_pause)
        self.assertEqual(exploding.calls, 0, "R1: kein erneuter Modellrequest (Settlement ist kostenfrei)")

    def test_reflection_vorsperre_received_unknown_duration_stays_honest_hold(self):
        """R1 (RECOVERY_REVIEW.md §1 "unbekannte urspruengliche Dauer bleibt
        ehrlich HOLD"): fehlt die Originaldauer, laesst `settle_received` den
        Record bewusst bei `received` -- die Vorsperre settlet NICHT nach
        accounted, haelt kontrolliert offen und traegt das Recovery-Signal."""
        retry_id = self._make_received_reflection_follower(with_duration=False)
        exploding = ScriptedDriver([])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": exploding, "vanguard": exploding,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        print(f"[R1-honest-hold-raw] ok={ok!r} recovery_pause={recovery_pause!r} "
              f"child_state={request_ledger.load_request(self.run_dir, retry_id)['state']!r}")
        self.assertFalse(ok)
        self.assertTrue(recovery_pause, "R1: unbekannte Dauer -> HOLD mit Recovery-Signal (Menue erreichbar)")
        self.assertEqual(
            request_ledger.load_request(self.run_dir, retry_id)["state"], "received",
            "R1: keine erfundene Nullbuchung, keine Schaetzung -- bleibt received",
        )
        self.assertEqual(exploding.calls, 0)

    def test_reflection_vorsperre_run_id_drift_revokes_accounted_exemption(self):
        """R5 (RECOVERY_REVIEW.md §2): die accounted-Ausnahme der Vorsperre
        nutzt jetzt denselben vollstaendigen Bindungsentscheid wie
        `commit_authorized_retry`. Eine Run-Bindungsdrift NACH der Disposition
        (bytegleiches Original, Folger accounted, aber `run_id.json` fremd)
        hebt die Ausnahme auf -- das Original bleibt Sperre und die Vorsperre
        traegt das Recovery-Signal statt still durchzulassen."""
        (self.run_dir / "run_id.json").write_text('{"run_id": "run-A"}', encoding="utf-8")
        retry_id = self._make_authorized_orphan(role="reflection", turn_idx=1, participant="vanguard")
        request_ledger.commit_authorized_retry(
            self.run_dir, retry_id, content="reflektion-wire", reserved_usd=0.01,
        )
        request_ledger.finish_received(
            self.run_dir, retry_id, usage={}, seconds=1.0, result_text="vanguard-reflexion",
        )
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")
        # Run-Bindung driftet (Restore/Kopie aus fremdem Lauf):
        (self.run_dir / "run_id.json").write_text('{"run_id": "run-B-FREMD"}', encoding="utf-8")
        exploding = ScriptedDriver([])
        runtime, controller = self._make_runtime(gm_transport=None, drivers={
            "leader_pk": exploding, "vanguard": exploding,
        })
        runtime._turn_idx = 1

        ok, pause_reason, recovery_pause = runtime._collect_reflections(
            controller, SECTION_ID, "2026-11-23T12:00:00",
            contexts_by_persona={"leader_pk": {"system": "s"}, "vanguard": {"system": "s"}},
            states_dir=self.states_dir,
        )

        print(f"[R5-vorsperre-drift-raw] ok={ok!r} recovery_pause={recovery_pause!r}")
        self.assertFalse(ok)
        self.assertTrue(recovery_pause, "R5: Run-Drift hebt die accounted-Ausnahme auf -> Recovery-Signal")
        self.assertEqual(exploding.calls, 0, "R5: kein Modellcall bei aufgehobener Ausnahme")


class TestGmTurnSubmitAnalog(_Rec1Base):
    def test_submit_authorized_follower_consumed_reaches_transport(self):
        retry_id = self._make_authorized_orphan(role="gm_turn", turn_idx=7, participant="leader_pk")
        gm = _FakeGmTransport(contents=["SL-Antwort auf Retry."])
        runtime, controller = self._make_runtime(gm_transport=gm, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": ScriptedDriver([]),
        })
        runtime._turn_idx = 7

        result = runtime.submit(controller, "leader_pk", "Wire-Text.", "2026-11-23T12:00:00", reserved_usd=0.01)

        self.assertEqual(len(gm.calls), 1, "GM-Transport tatsaechlich erreicht, kein Pause-Abbruch")
        self.assertEqual(result["content"], "SL-Antwort auf Retry.")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")

    def test_submit_without_authorization_pauses_typed_no_transport_call(self):
        self._make_unauthorized_orphan(role="gm_turn", turn_idx=7, participant="leader_pk")
        gm = _FakeGmTransport(contents=["sollte nie gesendet werden."])
        runtime, controller = self._make_runtime(gm_transport=gm, drivers={
            "leader_pk": ScriptedDriver([]), "vanguard": ScriptedDriver([]),
        })
        runtime._turn_idx = 7

        with self.assertRaises(_RecoveryPause):
            runtime.submit(controller, "leader_pk", "Wire-Text.", "2026-11-23T12:00:00", reserved_usd=0.01)

        self.assertEqual(len(gm.calls), 0)


class TestLobbyServiceAnalog(_Rec1Base):
    def test_request_admitted_decision_consumes_authorized_follower(self):
        from mmo_sim.core import lobby_service

        retry_id = self._make_authorized_orphan(role="lobby_initiative", turn_idx=2, participant="vanguard")
        driver = ScriptedDriver([ParticipantDecision(text="Initiative-Antwort.")])

        decision, block_reason = lobby_service.request_admitted_decision(
            self.run_dir, driver, {"user": "ctx"}, role="lobby_initiative", participant="vanguard",
            table_id=self.table.table_id, section_id=SECTION_ID, turn_idx=2,
        )

        self.assertIsNone(block_reason)
        self.assertIsNotNone(decision)
        self.assertEqual(decision.text, "Initiative-Antwort.")
        self.assertEqual(driver.calls, 1)
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")

    def test_request_admitted_decision_without_authorization_pauses(self):
        from mmo_sim.core import lobby_service

        orphan_id = self._make_unauthorized_orphan(role="lobby_initiative", turn_idx=2, participant="vanguard")
        driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])

        decision, block_reason = lobby_service.request_admitted_decision(
            self.run_dir, driver, {"user": "ctx"}, role="lobby_initiative", participant="vanguard",
            table_id=self.table.table_id, section_id=SECTION_ID, turn_idx=2,
        )

        self.assertIsNone(decision)
        self.assertIsNotNone(block_reason)
        self.assertEqual(driver.calls, 0)
        self.assertEqual(request_ledger.load_request(self.run_dir, orphan_id)["state"], "sent")


class TestRunFullSectionOuterCatchMapsRecoveryPause(_Rec1Base):
    """Verifiziert `run_full_section`s bestehenden aeusseren `except
    _GateBlocked`-Catch (briefing Punkt 2): faengt er einen `_RecoveryPause`
    (Subklasse), markiert `SectionOutcome.recovery_pause=True` -- fuer einen
    GEWOEHNLICHEN Admission-/Budget-`_GateBlocked` bleibt es bei `False`
    (sonst wuerde `lobby_flow.play_bound_table`s neue Kind-Weiterleitung
    JEDEN Stop als `STOPPED` ausweisen, nicht nur den Recovery-Fall)."""

    def test_unauthorized_orphan_propagates_to_outer_catch_as_recovery_pause(self):
        self._make_unauthorized_orphan(role="persona_decision", turn_idx=0, participant="leader_pk")
        leader_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        vanguard_driver = ScriptedDriver([])
        gm = _FakeGmTransport(contents=[])
        runtime, controller = self._make_runtime(gm_transport=gm, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })

        outcome = runtime.run_full_section(
            controller, SECTION_ID,
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "vanguard": {"user": "ctx"}},
            states_dir=self.states_dir, today="2026-11-23", ts="2026-11-23T12:00:00",
        )

        self.assertFalse(outcome.completion.success)
        self.assertTrue(outcome.recovery_pause, "unbehandelter Orphan muss als Recovery-Pause markiert werden")
        self.assertEqual(leader_driver.calls, 0)

    def test_ordinary_budget_block_is_not_marked_as_recovery_pause(self):
        write_test_profile(self.run_dir, max_usd=0.0)
        leader_driver = ScriptedDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        vanguard_driver = ScriptedDriver([])
        gm = _FakeGmTransport(contents=[])
        runtime, controller = self._make_runtime(gm_transport=gm, drivers={
            "leader_pk": leader_driver, "vanguard": vanguard_driver,
        })

        outcome = runtime.run_full_section(
            controller, SECTION_ID,
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "vanguard": {"user": "ctx"}},
            states_dir=self.states_dir, today="2026-11-23", ts="2026-11-23T12:00:00",
        )

        self.assertFalse(outcome.completion.success)
        self.assertFalse(outcome.recovery_pause, "ein gewoehnlicher Budget-Stop ist KEINE Recovery-Pause")
        self.assertEqual(leader_driver.calls, 0)


if __name__ == "__main__":
    unittest.main()
