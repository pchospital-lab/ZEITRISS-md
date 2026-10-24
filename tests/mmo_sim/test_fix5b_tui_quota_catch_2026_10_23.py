#!/usr/bin/env python3
"""
tests/mmo_sim/test_fix5b_tui_quota_catch_2026_10_23.py — FIX5B
(CRITIC-FIX5-REVIEW.md Punkt 1, BLOCKER) + R4-Rundenabschluss P1-P4
(Generalreview `01-PRODUCT-REVIEW.md` 2026-10-24): die getypte Kontingent-/
Budgetpause (`mmo_sim.adapters.base.ProviderQuotaPausedError`) MUSS den
ECHTEN Endnutzer-TUI-Spielerpfad erreichen -- nicht nur das private
Lab-/Harness-Driver-JSON -- UND nach Wiederverfuegbarkeit regulaer genau
einmal abschliessen, egal ob die Pause im gewoehnlichen Zug, in der
Pflichtreflexion oder in der Savekorrektur auftrat (P1/P2). Zusaetzlich:
der SaveGuard-Gegenfall (P3) und der Config-Error-Gegenfall (P4) bleiben
vom echten Kontingent-/Admission-Pausenpfad unterscheidbar.

PUBLIC, Produkt-Ebene, KEIN Driver-Import. Teil A treibt ausschliesslich
`mmo_sim.ui.tui.TuiSession` (den tatsaechlichen Terminal-Einstieg hinter
`scripts/mmo_sim.py` -- derselbe `_cmd_local_round` -> `core.app_service.
run_play_session`-Pfad). Teil B treibt `mmo_sim.core.runtime.SectionRuntime`
bzw. `mmo_sim.core.save_correction.pursue_group_save_correction` direkt --
GENAU dieselben Produktfunktionen, die `app_service.run_play_session`
(und damit TUI/Lab) intern aufruft (I1/A4) -- im selben Stil wie die
bestehenden `test_w48_save_correction_2026_10_07.py`/`test_w49_group_
round_restart_2026_10_08.py`-Resume-Tests. Teil C/D sind enge, reine
Unit-Gegenfaelle (P4-Matcher, P3-SaveGuard-Erkennung).

Einziger Stub pro Test: der GM-Transport (`.turn()`) und/oder die
Persona-Driver (`.decide()`), die die REALE, produktseitige
`ProviderQuotaPausedError` werfen (GM-Route, analog
`mmo_sim/adapters/gm_owui.py:GmOwuiTransport.turn` bei HTTP 402/429) --
kein Vollstub des Pruefgegenstands (`tui.py`/`app_service.py`/
`core/runtime.py`/`core/save_correction.py` laufen alle echt).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision, ProviderQuotaPausedError  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding as ob  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    is_save_command,
    is_saveguard_rejection,
)
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _QuotaPausingGm:
    """GM-Stub (echter `GMTransport`-Vertrag, kein echtes Netz): wirft bei
    `.turn()` dieselbe getypte Exception, die der echte `GmOwuiTransport`
    bei einer 402/429-Antwort wirft (s. `gm_owui.py:198-207`) -- simuliert
    GENAU die vom Review nachgewiesene reale Aufrufkette OHNE echten HTTP-
    Server."""

    def __init__(self):
        self.calls: list[str] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append(user_text)
        raise ProviderQuotaPausedError(
            "gm_owui: Kontingent-/Budgetpause erkannt: HTTP 429: "
            '{"error":{"message":"Rate limit exceeded","type":"insufficient_quota"}}'
        )


class _CountingGm:
    """Liefert der Reihe nach vorgegebene Antworten; wirft bei jedem
    Ueberschuss -- Beleg gegen einen unerwarteten zusaetzlichen Aufruf."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[str] = []

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append(user_text)
        if not self._contents:
            raise AssertionError(f"_CountingGm: unerwarteter zusaetzlicher Aufruf (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _onboard_solo_participant(data_dir: Path, participant_id: str) -> None:
    save = full_v7_save(f"CHR-{participant_id.upper()}", name=participant_id, save_id=f"fixture-{participant_id}-initial-001")
    char_id = save["characters"][0]["id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    ob.start_or_resume(data_dir / "onboarding", participant_id)
    ob.complete_with_save(data_dir / "onboarding", participant_id, save, ZeitrissHarvestValidator(), char_id)
    ob.ensure_participant_persona_state(ps_store, data_dir / "states", participant_id, char_id, save)


# ---------------------------------------------------------------------------
# Teil A -- echter TUI-Spielerpfad (FIX5B, unveraendert + Resume-Erweiterung)
# ---------------------------------------------------------------------------

def test_tui_real_play_path_catches_quota_pause_with_calm_message_no_traceback():
    """Treibt eine ECHTE Solo-Spielrunde ueber `TuiSession` ('l' ohne
    Gast-Token -- derselbe Aufrufpunkt, den ein gebundener Tisch-Resume
    ebenfalls durchlaeuft, s. `_resume_bound_table`-Docstring): der
    Spielzug ruft real `app_service.run_play_session` -> `core.runtime` ->
    den GM-Stub auf, der die getypte Kontingent-Pause wirft. Erwartung:
    kein Crash, keine rohe Exception im Terminal, ruhige Spielermeldung,
    kontrolliert zurueck ins Hauptmenue (kein erzwungenes Finalisieren)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _onboard_solo_participant(d, "sniper")
        write_test_profile(d / "run")

        gm = _QuotaPausingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input(["l", "Ich pruefe die Lage.", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        try:
            rc = session.run()
        except ProviderQuotaPausedError:
            raise AssertionError(
                "ProviderQuotaPausedError erreichte ungefangen session.run() -- "
                "genau der vom Review nachgewiesene rohe Traceback auf dem Spielerterminal."
            )

        assert rc == 0, "ein getypter Kontingent-Fehler darf die TUI NICHT abstuerzen lassen"
        assert gm.calls, "der GM-Stub muss tatsaechlich aufgerufen worden sein (echter Spielzug, kein Vollstub)"

        joined = "\n".join(printed)
        assert "Traceback" not in joined and "File \"" not in joined and "Error:" not in joined, (
            f"kein roher Python-Traceback/Crash-Look auf dem Spielerterminal: {joined[-1000:]}"
        )
        calm_message = next(
            (p for p in printed if ("Kontingent" in p or "Guthaben" in p) and "gespeichert" in p.lower()
             and "fortsetzen" in p.lower()),
            None,
        )
        assert calm_message, f"ruhige Spielermeldung (WAS/BERUHIGUNG/WIE WEITER) fehlt: {printed[-5:]}"
        assert not any("Abschnitt abgeschlossen" in p for p in printed), (
            "die Pause darf KEINEN falschen Abschnittsabschluss ausloesen (kein Finalisieren)"
        )
        # Nahtlos fortsetzbar: die Session selbst ist nicht abgestuerzt (sie
        # hat die naechste Eingabe 'x' noch regulaer verarbeitet und sich
        # kontrolliert beendet) -- bereits durch rc==0 oben belegt.


def test_tui_quota_pause_message_matches_product_shared_source():
    """Die im Terminal gezeigte Meldung MUSS aus der EINEN produktseitigen
    Quelle (`adapters.base.quota_pause_player_message`) stammen -- derselben
    Funktion, an die `driver.integrated._quota_pause_player_message`
    delegiert (FIX5B: eine Quelle, keine Dopplung zwischen TUI und
    Harness)."""
    from mmo_sim.adapters.base import quota_pause_player_message

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _onboard_solo_participant(d, "sniper")
        write_test_profile(d / "run")

        gm = _QuotaPausingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input(["l", "Ich pruefe die Lage.", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        session.run()
        expected = quota_pause_player_message(None)
        assert expected in printed, (
            f"die TUI-Ausgabe muss WOERTLICH die produktseitige Funktion verwenden, nicht einen "
            f"zweiten, abweichenden Text: erwartet {expected!r} in {printed[-5:]!r}"
        )


def test_tui_normal_turn_quota_pause_then_resume_completes_exactly_once():
    """R4-Rundenabschluss (P1-Kontext, Normalzug-Referenzfall): nach der
    sichtbaren Pause (oben bereits belegt) MUSS ein regulaerer neuer
    Aufruf ('l' erneut, derselbe gebundene Tisch) denselben Zug normal
    fortsetzen und GENAU EINMAL abschliessen -- kein zweiter GM-Call fuer
    den bereits pausierten Zug, kein doppelter Abschluss."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _onboard_solo_participant(d, "sniper")
        write_test_profile(d / "run")

        gm_pause = _QuotaPausingGm()
        printed_1: list[str] = []
        session_1 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input(["l", "Ich pruefe die Lage.", "x"]),
            print_fn=printed_1.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm_pause,
        )
        rc1 = session_1.run()
        assert rc1 == 0
        assert len(gm_pause.calls) == 1, "genau EIN GM-Call fuer den pausierten Zug, kein Retry in derselben Session."

        # Neuer regulaerer Aufruf nach Wiederverfuegbarkeit: derselbe
        # gebundene Tisch, jetzt ein normal antwortender GM-Stub. Die
        # Antwort muss den ECHTEN, bereits onboardeten v7-Save von
        # "sniper" als Block tragen -- sonst meldet `complete_section`
        # eine fehlende Figur und loest eine Korrekturnachforderung aus
        # (hier nicht Testgegenstand).
        sniper_save = full_v7_save("CHR-SNIPER", name="sniper", save_id="fixture-sniper-initial-001")
        gm_ok = _CountingGm([f"Alles ruhig.\n```json\n{json.dumps(sniper_save)}\n```\n{COMPLETION_MARKER}"])
        printed_2: list[str] = []
        session_2 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input(["l", "Weiter bitte.", "x"]),
            print_fn=printed_2.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm_ok,
        )
        rc2 = session_2.run()
        assert rc2 == 0
        assert len(gm_ok.calls) == 1, (
            f"genau EIN neuer GM-Call nach Wiederverfuegbarkeit erwartet, kein Doppelversand: {gm_ok.calls}"
        )
        assert any("Abschnitt abgeschlossen" in p for p in printed_2), (
            f"der fortgesetzte Zug muss regulaer genau einmal abschliessen: {printed_2}"
        )
        assert not any("Abschnitt abgeschlossen" in p for p in printed_1), (
            "die urspruengliche pausierte Session darf KEINEN Abschluss gezeigt haben."
        )


# ---------------------------------------------------------------------------
# Teil B -- Quota-Pause in der Pflichtreflexion (P1) ueber `SectionRuntime`
# ---------------------------------------------------------------------------

class _RaisingThenScriptedDriver:
    """Geskripteter Fake-Teilnehmer: jedes Skriptelement ist entweder eine
    `ParticipantDecision` (wird zurueckgegeben) ODER eine `BaseException`-
    Instanz (wird geworfen) -- erlaubt, GENAU den N-ten Aufruf dieses
    Treibers typisiert scheitern zu lassen, ohne den Pruefgegenstand
    (`controller.collect_decision`/`core.runtime._admitted_decision`)
    selbst zu stubben."""

    def __init__(self, script: list):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("_RaisingThenScriptedDriver: Skript erschoepft -- unerwarteter zusaetzlicher Aufruf.")
        item = self._script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class _NeverCalledDriver:
    def decide(self, context: dict) -> ParticipantDecision:
        raise AssertionError(
            "kein weiterer Modellaufruf erwartet: dieses Mitglied hat bereits erfolgreich reflektiert "
            "(Dedup ueber reflections.jsonl) -- ein Resume darf es NICHT erneut befragen."
        )


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_two_member_table(run_dir: Path, states_dir: Path, table_id: str):
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


def test_reflection_quota_pause_stops_round_then_resumes_exactly_once():
    """P1 (R4-Rundenabschluss): eine `ProviderQuotaPausedError` WAEHREND der
    Pflicht-KI-Reflexion eines Mitglieds darf NICHT im generischen
    `pending_recovery`-Pfad verschwinden -- sie muss die Runde SOFORT ohne
    weitere Modellanfragen beenden und bis zum Aufrufer durchreichbar sein
    (hier: ungefangen aus `run_full_section`, derselbe Typ, den `ui/tui.py`
    faengt). Bereits erfolgreich reflektierte Mitglieder werden bei einem
    Resume NICHT erneut befragt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir, "t-p1-reflect")

        leader_save = full_v7_save("chrono-leader", name="Leader")
        guest_save = full_v7_save("chrono-guest", name="Guest")
        debrief = (
            "Abschnitt beendet.\n"
            f"```json\n{json.dumps(leader_save)}\n```\n"
            f"```json\n{json.dumps(guest_save)}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        gm = _CountingGm(["SL-Antwort auf Anker-Turn.", "SL-Antwort auf Gast-Turn.", debrief])

        # `table.members` ist alphabetisch sortiert (`store.py`: `members =
        # sorted({o["from"]} | o["wants"])`) -- "guest_pk" < "leader_pk",
        # guest reflektiert also VOR leader. Guest bekommt die normale
        # Antwort (committet), leader loest die Pause aus (danach SOFORT
        # Schluss, kein drittes Mitglied in dieser Zweiertisch-Runde).
        leader_driver = _RaisingThenScriptedDriver([
            ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief.", origin_source="fake:leader-debrief"),
            ProviderQuotaPausedError("persona_claude_code: Kontingent-/Budgetpause erkannt (Test)"),
        ])
        guest_driver = _RaisingThenScriptedDriver([
            ParticipantDecision(text="Turn.", save_payload=guest_save, origin_source="fake:guest"),
            ParticipantDecision(text="Reflexion: alles ruhig.", origin_source="fake:guest-reflect"),
        ])
        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
        event_log = EventLog(run_dir)
        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=event_log,
        )
        section_id = "section-p1-reflect"
        try:
            runtime.run_full_section(
                controller, section_id,
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
                states_dir=states_dir, today="2026-10-24", ts="2026-10-24T20:00:00",
            )
            raise AssertionError("ProviderQuotaPausedError haette ungefangen propagieren muessen (P1).")
        except ProviderQuotaPausedError:
            pass

        assert len(gm.calls) == 3, f"kein weiterer GM-Call nach der Pause erwartet: {gm.calls}"
        assert guest_driver.calls == 2, "guest wurde genau einmal fuer die Reflexion (und einmal fuer Import) angefragt."

        reflections_path = run_dir / "reflections.jsonl"
        entries = [json.loads(line) for line in reflections_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        required = [e for e in entries if e.get("kind") == "ai_required_reflection"]
        pending = [e for e in entries if e.get("status") == "pending_recovery"]
        assert len(required) == 1 and required[0]["persona_key"] == "guest_pk", (
            f"nur die guest-Reflexion ist bereits committet, die leader-Reflexion NICHT (Pause danach): {entries}"
        )
        assert len(pending) == 1 and pending[0]["persona_key"] == "leader_pk", pending
        assert "Kontingent-/Budgetpause erkannt" in pending[0]["error"], pending[0]

        assert table.status == "active", f"Tisch darf NICHT final geschlossen sein: {table.status}"
        assert not store._completion_final_path(run_dir, section_id).exists(), (
            "kein __final-Marker trotz Pause waehrend der Reflexion erlaubt."
        )

        # Resume: frischer Controller, leader bekommt jetzt eine normale
        # Antwort; guest DARF NICHT erneut angefragt werden (bereits
        # committet) -- `_NeverCalledDriver` wirft, falls doch.
        gm_never = _CountingGm([])

        def _gm_never_turn(*_a, **_k):
            raise AssertionError("P1-Resume: kein GM-Call erwartet (die Reflexion ist privat, kein SL-Turn).")
        gm_never.turn = _gm_never_turn

        leader_driver_2 = _RaisingThenScriptedDriver([
            ParticipantDecision(text="Reflexion: jetzt ok.", origin_source="fake:leader-reflect-resume"),
        ])
        controller_2 = TableController(
            leader_key="leader_pk", drivers={"leader_pk": leader_driver_2, "guest_pk": _NeverCalledDriver()},
        )
        runtime_2 = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm_never, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=EventLog(run_dir),
        )
        outcome = runtime_2.run_full_section(
            controller_2, section_id,
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=states_dir, today="2026-10-24", ts="2026-10-24T20:05:00",
        )
        assert outcome.completion.success, outcome.completion.reason
        assert leader_driver_2.calls == 1, "leader wird nach Wiederverfuegbarkeit genau EINMAL neu angefragt."

        entries_after = [
            json.loads(line) for line in reflections_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        required_after = [e for e in entries_after if e.get("kind") == "ai_required_reflection"]
        assert len(required_after) == 2, (
            f"genau EINE neue (leader) Pflichtreflexion kommt hinzu, die guest-Reflexion wird NICHT "
            f"doppelt committet: {entries_after}"
        )
        assert sorted(e["persona_key"] for e in required_after) == ["guest_pk", "leader_pk"]
        repeat = store.finalize_section_after_reflection(lobby, table, section_id)
        assert repeat.success and repeat.already_completed, "ein wiederholter Finalize-Aufruf bleibt idempotent."


# ---------------------------------------------------------------------------
# Teil B2 -- Quota-Pause in der Savekorrektur (P2) ueber
# `save_correction.pursue_group_save_correction` direkt (derselbe Stil wie
# `test_w49_group_round_restart_2026_10_08.py`s Crash-/Restart-Tests).
# ---------------------------------------------------------------------------

_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def test_savecorrection_quota_pause_stays_resumable_then_resumes_exactly_once():
    """P2 (R4-Rundenabschluss): eine sicher beobachtete, vollstaendig
    verbuchte Kontingent-/Budgetablehnung WAEHREND einer Gruppen-
    Savekorrektur darf NICHT pauschal zu `transport_error` -> `mark_hold` +
    `_clear_open_round` (terminal) werden. Die offene Runde (Mitgliederset
    + Repair-Key) bleibt erhalten; nach Wiederverfuegbarkeit legt der
    reguläre Pfad EINEN neuen Request an, OHNE das Korrekturbudget
    (`attempts_used`) ein zweites Mal zu verbrauchen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir, "t-p2-correction")

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-p2-correction", harvested, states_dir, "2026-10-24",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        def _raise_quota(*_a, **_k):
            raise ProviderQuotaPausedError(
                "gm_owui: Kontingent-/Budgetpause erkannt: HTTP 429: "
                '{"error":{"message":"Rate limit exceeded","type":"insufficient_quota"}}'
            )
        gm_pause = _CountingGm([])
        gm_pause.turn = _raise_quota

        repair_key = save_correction_domain.group_repair_key(table.table_id, "section-p2-correction", "chrono-guest")

        try:
            save_correction.pursue_group_save_correction(
                lobby=lobby, table=table, section_id="section-p2-correction", harvested=dict(harvested),
                harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-24",
                harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm_pause,
                cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            )
            raise AssertionError("ProviderQuotaPausedError haette ungefangen propagieren muessen (P2).")
        except ProviderQuotaPausedError:
            pass

        record_after_pause = save_correction.load_record(run_dir, repair_key)
        assert record_after_pause["attempts_used"] == 1, (
            f"genau EIN Versuch verbraucht (nicht zwei) -- die Pause darf KEINEN zweiten Slot kosten: "
            f"{record_after_pause}"
        )
        assert record_after_pause["state"] not in ("hold", "aborted"), (
            f"eine Kontingentpause darf NICHT terminal (mark_hold) werden: {record_after_pause}"
        )
        open_round = save_correction._load_open_round(run_dir, table.table_id, "section-p2-correction")
        assert open_round is not None, "die offene Runde (Mitgliederset) muss ERHALTEN bleiben, kein _clear_open_round."
        assert open_round["round"] >= 2, (
            f"ein NEUER round_no (frische Requestidentitaet) macht den naechsten Aufruf sendefaehig: {open_round}"
        )
        assert [m["char_id"] for m in open_round["members"]] == ["chrono-guest"], open_round
        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-p2-correction", "chrono-leader")
        assert save_correction.load_record(run_dir, leader_repair_key) is None, (
            "fuer die von Anfang an gueltige Leader-Figur darf NIE ein Korrekturdatensatz entstehen."
        )

        # Resume: frischer, funktionsfaehiger Transport -- MUSS dieselbe
        # (jetzt neu identifizierte) Runde fortsetzen, GENAU EINEN neuen
        # realen Transport-Call ausloesen, OHNE die alte Historie/den
        # Verbrauch zu ueberschreiben.
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        gm_ok = _CountingGm([f"```json\n{json.dumps(guest_valid)}\n```"])
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-p2-correction", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-24",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm_ok,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_after.success, completion_after.reason
        assert len(gm_ok.calls) == 1, f"genau EIN neuer Transport-Call nach Wiederverfuegbarkeit: {gm_ok.calls}"
        assert harvested_after["guest_pk"] == guest_valid
        assert harvested_after["leader_pk"] == leader_valid, "der alte, bereits gueltige Leader-Save bleibt unveraendert."

        record_after_resume = save_correction.load_record(run_dir, repair_key)
        assert record_after_resume["attempts_used"] == 1, (
            f"das Korrekturbudget bleibt bei 1 -- die Quota-Pause selbst verbraucht KEINEN Slot: "
            f"{record_after_resume}"
        )
        assert record_after_resume["state"] == "adopted"
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-p2-correction").exists(), (
            "der Rundenmarker muss nach vollstaendiger Verarbeitung geloescht sein."
        )


# ---------------------------------------------------------------------------
# Teil C -- P4: Config-Error-Gegenfall (bleibt terminal/generisch, KEIN
# Kontingent-Resume) vs. echtes Limitschema; GM-429-vs-402-Klassifikation.
# ---------------------------------------------------------------------------

def test_config_error_with_bare_word_quota_is_not_a_quota_pause():
    """P4: `result="Config error: please check your quota settings in the
    admin panel"` enthaelt das blosse Wort "quota", ist aber KEIN
    Kontingent-Resume-Signal (Generalreview-Gegenfall) -- Fix5B verengte
    nur den historischen Wrapper, nicht diesen gemeinsamen Matcher."""
    from mmo_sim.adapters.persona_claude_code import is_quota_pause_result_text

    assert is_quota_pause_result_text(
        "Config error: please check your quota settings in the admin panel"
    ) is False, "ein beliebiger Config-Fehler mit dem blossen Wort 'quota' darf KEINEN Kontingent-Resume legitimieren."


def test_real_quota_signatures_are_still_classified_as_quota_pause():
    """P4-Gegenprobe: ein echtes Limitschema (Erschoepfungswort gepaart mit
    'quota', ODER die bestehenden Phrasen, ODER ein echter Reset-Zeitpunkt
    nach 'resets') bleibt unveraendert als Kontingentpause erkannt."""
    from mmo_sim.adapters.persona_claude_code import is_quota_pause_result_text

    assert is_quota_pause_result_text("You have exceeded your quota, resets 5:30pm (Europe/Berlin)") is True
    assert is_quota_pause_result_text("5-hour session limit reached") is True
    assert is_quota_pause_result_text("API rate limit exceeded, please slow down") is True
    assert is_quota_pause_result_text("out of quota for this billing period") is True
    assert is_quota_pause_result_text("Auth failed: invalid API key") is False


def test_gm_429_without_credit_marker_gets_retry_hint_while_402_gets_topup_hint():
    """P4: 429 (reines Ratenlimit OHNE `insufficient_quota`-Marker) bekommt
    einen Warte-/Retry-Hinweis statt des Aufladehinweises; 402 bleibt bei
    'Guthaben/Abo aufladen'. Stoppen bleibt in BEIDEN Faellen konservativ
    (`ProviderQuotaPausedError`)."""
    import mmo_sim.adapters.gm_owui as gm_owui
    from mmo_sim.adapters.base import quota_pause_is_rate_limited, quota_pause_player_message

    class _Boom429:
        def turn(self, *a, **k):
            raise RuntimeError("HTTP 429: {\"error\":{\"message\":\"slow down\"}}")

    class _Boom402:
        def turn(self, *a, **k):
            raise RuntimeError('HTTP 402: {"error":{"message":"insufficient_quota"}}')

    t429 = gm_owui.GmOwuiTransport.__new__(gm_owui.GmOwuiTransport)
    t429._session = _Boom429()
    t402 = gm_owui.GmOwuiTransport.__new__(gm_owui.GmOwuiTransport)
    t402._session = _Boom402()

    try:
        t429.turn(0, "hi")
        raise AssertionError("haette ProviderQuotaPausedError werfen muessen")
    except ProviderQuotaPausedError as exc:
        assert quota_pause_is_rate_limited(str(exc)) is True, str(exc)
        msg = quota_pause_player_message(None, rate_limited=quota_pause_is_rate_limited(str(exc)))
        assert "erneut versuchen" in msg.lower() and "aufladen" not in msg.lower(), msg

    try:
        t402.turn(0, "hi")
        raise AssertionError("haette ProviderQuotaPausedError werfen muessen")
    except ProviderQuotaPausedError as exc:
        assert quota_pause_is_rate_limited(str(exc)) is False, str(exc)
        msg = quota_pause_player_message(None, rate_limited=quota_pause_is_rate_limited(str(exc)))
        assert "aufladen" in msg.lower(), msg


# ---------------------------------------------------------------------------
# Teil D -- P3: SaveGuard-Gegenfall (ausdrueckliche Verweigerung finalisiert
# NICHT) vs. positiver Fall (erlaubt, aber fehlender Export -> begrenzte
# Nachforderung bleibt erhalten).
# ---------------------------------------------------------------------------

def _build_solo_table(run_dir: Path, states_dir: Path, table_id: str):
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
        chrononaut_ids={"leader_pk": "chrono-leader"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


def test_explicit_save_with_saveguard_rejection_does_not_finalize_or_force_correction():
    """P3: ein exaktes `!save`, auf das die SL/SaveGuard mit der kanonischen
    Verweigerungsmeldung antwortet (keine HQ-Erlaubnis, kein v7-Block),
    darf NICHT ueber die dritte `explicit_completion_attempt`-Bedingung
    finalisieren und KEINE exporterzwingende Korrektur ausloesen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_solo_table(run_dir, states_dir, "t-p3-reject")

        leader_save = full_v7_save("chrono-leader", name="Leader")
        rejection_text = "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt."
        gm = _CountingGm([rejection_text])
        leader_driver = _RaisingThenScriptedDriver([
            ParticipantDecision(text="!save", save_payload=leader_save, origin_source="fake:leader"),
        ])
        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver})
        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=EventLog(run_dir),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        outcome = runtime.run_full_section(
            controller, "section-p3-reject", contexts_by_persona={"leader_pk": {"user": "ctx-leader"}},
            states_dir=states_dir, today="2026-10-24", ts="2026-10-24T20:00:00", max_turns=1,
        )
        assert not outcome.completion.success, (
            f"eine ausdrueckliche SaveGuard-Verweigerung darf NICHT finalisieren: {outcome.completion}"
        )
        assert "max_turns" in outcome.completion.reason, (
            f"der Zug muss als GEWOEHNLICHER Spielzug durchgehen (max_turns-Ende), NICHT als Korrektur-HOLD: "
            f"{outcome.completion.reason}"
        )
        repair_key = save_correction_domain.group_repair_key(table.table_id, "section-p3-reject", "chrono-leader")
        assert save_correction.load_record(run_dir, repair_key) is None, (
            "eine SaveGuard-Ablehnung darf KEINEN Korrekturdatensatz/exporterzwingende Nachforderung ausloesen."
        )


def test_explicit_save_without_saveguard_rejection_still_requests_limited_followup():
    """P3-Gegenprobe (positiver Fall bleibt erhalten): ein exaktes `!save`,
    auf das die SL OHNE SaveGuard-Ablehnung und OHNE neuen bindbaren Export
    antwortet ('bereits gespeichert'), loest weiterhin den bestehenden
    begrenzten Korrektur-/Nachforderversuch aus (FIX2, unveraendert)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_solo_table(run_dir, states_dir, "t-p3-allowed")

        leader_save = full_v7_save("chrono-leader", name="Leader")
        no_export_text = "Bereits gespeichert, kein neuer Export noetig."
        # Die Korrekturantwort muss einen ECHTEN, bindbaren v7-Block tragen
        # (sonst fordert die begrenzte Nachforderung ein zweites/drittes
        # Mal nach, bis das Budget erschoepft ist) -- der Test prueft hier
        # nur, DASS genau ein Korrekturversuch ausgeloest wird, nicht die
        # Drift-/Validierungslogik selbst.
        correction_text = f"```json\n{json.dumps(leader_save)}\n```"
        gm = _CountingGm([no_export_text, correction_text])
        leader_driver = _RaisingThenScriptedDriver([
            ParticipantDecision(text="!save", save_payload=leader_save, origin_source="fake:leader"),
        ])
        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver})
        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=EventLog(run_dir),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        runtime.run_full_section(
            controller, "section-p3-allowed", contexts_by_persona={"leader_pk": {"user": "ctx-leader"}},
            states_dir=states_dir, today="2026-10-24", ts="2026-10-24T20:00:00", max_turns=1,
        )
        assert len(gm.calls) == 2, (
            f"die dritte OR-Bedingung muss weiterhin einen begrenzten Korrekturversuch (zweiter GM-Call) "
            f"ausloesen, wenn KEINE SaveGuard-Ablehnung vorliegt: {gm.calls}"
        )


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
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
