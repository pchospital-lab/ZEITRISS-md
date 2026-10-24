#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_duo_save_loop_bounded_2026_10_23.py — FIX 2
(IMPLEMENTATION-SPEC-BETA.md, 02-AUFTRAG.md §1 "Duo-!save-Schleife
beheben", 01-LIVE-BEFUNDE.md §3): ein explizites, eigenstaendiges Leader-
`!save`, auf das die SL OHNE neuen bindbaren Export antwortet ("bereits
gespeichert"), darf NICHT als gewoehnlicher, folgenloser Spielzug behandelt
werden -- die Schleife lief vorher unbegrenzt mit weiteren normalen Runden
weiter (belegt: Duo-Tisch, Turns 17/18/21/22). Der Fix loest stattdessen
GENAU denselben bereits bestehenden, begrenzten Ernte-/Korrekturversuch wie
ein echter Marker-Treffer aus (`core.runtime.SectionRuntime.finalize` ->
`store.complete_section` + dessen begrenzter W48-Nachforderpfad,
`save_correction.pursue_group_save_correction`, max. 3 zusaetzliche
Anfragen).

Faehrt GENAU den Produktionspfad (`core.app_service.run_play_session`,
denselben, den `ui/tui.py` UND `core/lobby_flow.py` verwenden) mit einem
Fake-GM/geskripteten Treiber -- kein isolierter `finalize_*`-Aufruf.
Rot-vorher (ohne `explicit_completion_attempt`, alter Zustand) vs.
gruen-nachher (mit dem Fix) am SELBEN Szenario."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
    is_save_command,
)

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class _ScriptedDriver:
    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            return ParticipantDecision(text="Weiter beobachten.", origin_source="fake:exhausted")
        return self._script.pop(0)


class _FakeGmTransport:
    def __init__(self, scripted_contents: list[str]):
        self._contents = list(scripted_contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        content = self._contents.pop(0) if self._contents else "Kein neuer Export."
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake-chat"}


def _seed_persona_state(ps_store, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_table(root: Path, table_id: str, leader_cid: str, guest_cid: str):
    run_dir, states_dir = root / "run", root / "states"
    states_dir.mkdir(parents=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", leader_cid)
    _seed_persona_state(ps_store, states_dir, "guest_pk", guest_cid)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": leader_cid, "guest_pk": guest_cid},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    write_test_profile(run_dir)
    return lobby, table, ps_store, run_dir, states_dir


def _anchor_decision(cid: str, text: str = "Anker-Text.") -> ParticipantDecision:
    return ParticipantDecision(text=text, save_payload=full_v7_save(cid, name="Test"), origin_source="fake:anchor")


def _run_section(
    lobby, table, ps_store, run_dir, states_dir, *, gm_contents, leader_script, guest_script,
    section_id, explicit_completion_attempt, max_turns,
):
    gm = _FakeGmTransport(scripted_contents=gm_contents)
    leader_driver = _ScriptedDriver(leader_script)
    guest_driver = _ScriptedDriver(guest_script)
    drivers = {"leader_pk": leader_driver, "guest_pk": guest_driver}
    contexts = {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}}
    controller = TableController(leader_key="leader_pk", drivers=drivers)
    event_log = EventLog(run_dir)
    outcome = app_service.run_play_session(
        lobby, table, gm, controller, section_id, contexts, states_dir,
        "2026-10-23", "2026-10-23T20:00:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, event_log=event_log,
        max_turns=max_turns,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=explicit_completion_attempt,
    )
    return outcome, gm, leader_driver, guest_driver


def test_red_before_standalone_save_without_export_loops_into_further_normal_rounds():
    """ROT-VORHER: `explicit_completion_attempt=None` (alter Zustand, vor
    FIX2) -- ein autorisiertes, eigenstaendiges `!save` ohne neuen Export
    wird NICHT als Abschlussversuch erkannt. Beweist den belegten Defekt:
    der Leader wird NACH dem folgenlosen `!save` fuer EINEN weiteren,
    gewoehnlichen Spielzug befragt (Turns 17/18/21/22-Muster -- `!save`
    verschwindet wirkungslos, das Spiel laeuft normal weiter)."""
    with tempfile.TemporaryDirectory() as td:
        leader_cid, guest_cid = "chrono-leader-red", "chrono-guest-red"
        lobby, table, ps_store, run_dir, states_dir = _build_table(Path(td), "t-red", leader_cid, guest_cid)
        outcome, gm, leader_driver, guest_driver = _run_section(
            lobby, table, ps_store, run_dir, states_dir,
            gm_contents=[
                "SL-Antwort auf Anker-Turn.",
                "SL-Antwort auf Gast-Import.",
                "Hinweis: Speicherstand ist bereits gespeichert, kein neuer Export noetig.",
                "SL-Antwort auf den naechsten gewoehnlichen Spielzug.",
            ],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-save"),
                ParticipantDecision(text="Wir spielen trotzdem weiter.", origin_source="fake:leader-continue"),
            ],
            guest_script=[_anchor_decision(guest_cid)],
            section_id="section-red", explicit_completion_attempt=None, max_turns=5,
        )
        assert not outcome.completion.success, outcome.completion.reason
        assert outcome.harvested == {}
        # Der Defekt: NACH dem folgenlosen `!save` lief die Schleife normal
        # weiter -- der Leader wurde fuer einen VIERTEN Turn (den "Wir
        # spielen trotzdem weiter."-Zug) tatsaechlich befragt, GM bekam
        # einen VIERTEN echten Turn. Kein begrenzter Korrekturversuch, kein
        # kontrollierter Stop -- `!save` verschwand wirkungslos.
        assert len(gm.calls) == 5, (
            f"ROT-Repro widerlegt: ohne Fix haette die Schleife nach dem folgenlosen '!save' OHNE "
            f"Korrekturversuch einfach mit weiteren gewoehnlichen Spielzuegen (bis max_turns=5) "
            f"weiterlaufen muessen, gm.calls={len(gm.calls)}"
        )
        assert leader_driver.calls >= 3, (
            f"ROT-Repro: der Leader wurde nach dem folgenlosen '!save' fuer weitere gewoehnliche "
            f"Spielzuege befragt, driver.calls={leader_driver.calls}"
        )
        final_red = store._completion_final_path(run_dir, "section-red")
        assert not final_red.exists()
        plan_red = store._completion_plan_path(run_dir, "section-red")
        assert not plan_red.exists(), "ROT-Pfad: kein Abschluss-Auftrag wurde je versucht/gepinnt"


def test_green_after_standalone_save_without_export_triggers_bounded_correction_not_endless_rounds():
    """GRUEN-NACHHER (FIX2): identisches Szenario, jetzt MIT
    `explicit_completion_attempt=is_save_command` (derselbe Wiring-Punkt
    wie `core/lobby_flow.py:play_bound_table`/`ui/tui.py`). Das `!save`
    loest SOFORT einen Abschlussversuch aus: `store.complete_section`
    findet (noch) keine gueltigen Saves -> der bereits bestehende
    begrenzte W48-Nachforderpfad (`save_correction.
    pursue_group_save_correction`, max. 3 zusaetzliche Anfragen) wird
    aktiviert -- NICHT jedoch ein weiterer GEWOEHNLICHER Spielzug. Die
    Funktion kehrt kontrolliert (gehalten) zurueck, OHNE die vierte
    Leader-Scriptzeile ('Wir spielen trotzdem weiter.') je zu konsumieren."""
    with tempfile.TemporaryDirectory() as td:
        leader_cid, guest_cid = "chrono-leader-green", "chrono-guest-green"
        lobby, table, ps_store, run_dir, states_dir = _build_table(Path(td), "t-green", leader_cid, guest_cid)
        outcome, gm, leader_driver, guest_driver = _run_section(
            lobby, table, ps_store, run_dir, states_dir,
            gm_contents=[
                "SL-Antwort auf Anker-Turn.",
                "SL-Antwort auf Gast-Import.",
                "Hinweis: Speicherstand ist bereits gespeichert, kein neuer Export noetig.",
                # Falls der begrenzte Korrekturpfad tatsaechlich sendet
                # (bis zu 3 weitere Anfragen): auch hier kein gueltiger
                # Export -- die Korrektur MUSS begrenzt scheitern, NICHT
                # unbegrenzt weiterlaufen und NICHT synthetisch "gelingen".
                "Korrekturantwort ohne Export 1.",
                "Korrekturantwort ohne Export 2.",
                "Korrekturantwort ohne Export 3.",
            ],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-save"),
                # Diese Zeile darf in GRUEN NIEMALS konsumiert werden --
                # genau das beweist "keine unbegrenzten weiteren Runden".
                ParticipantDecision(text="Wir spielen trotzdem weiter.", origin_source="fake:leader-continue"),
            ],
            guest_script=[_anchor_decision(guest_cid)],
            section_id="section-green", explicit_completion_attempt=is_save_command, max_turns=5,
        )
        # KEINE unbegrenzten weiteren Story-/Persona-Runden: der Leader
        # wurde NUR fuer Anker + `!save` tatsaechlich befragt (2 echte
        # Entscheidungsanfragen), NIE fuer die dritte ("weiterspielen")
        # Scriptzeile.
        assert leader_driver.calls == 2, (
            f"FIX2 widerlegt: der Leader haette NACH dem folgenlosen '!save' NICHT fuer einen weiteren "
            f"gewoehnlichen Spielzug befragt werden duerfen, driver.calls={leader_driver.calls}"
        )
        # KEIN synthetischer Erfolg: die begrenzte Korrektur fand (in
        # diesem Szenario bewusst) keinen gueltigen Export -> kontrollierter
        # Fehlschlag, kein erfundener Abschluss.
        assert not outcome.completion.success, (
            f"kein synthetischer Erfolg erwartet (kein gueltiger Export in der Korrektur): {outcome.completion.reason}"
        )
        final_green = store._completion_final_path(run_dir, "section-green")
        assert not final_green.exists(), "kein erfundener Abschluss ohne gueltigen Export"
        # Der begrenzte Korrekturpfad selbst darf nicht unbegrenzt senden:
        # Anker(1) + Gast-Import(1) + !save-Turn(1) + hoechstens
        # MAX_ADDITIONAL_REQUESTS(=3) Korrekturrunden = hoechstens 6
        # GM-Aufrufe gesamt -- WEIT unter den 5 zusaetzlichen max_turns, die
        # ein gewoehnlicher Weiterspiel-Loop verbraucht haette.
        assert len(gm.calls) <= 6, f"Korrekturpfad darf nicht unbegrenzt senden: gm.calls={len(gm.calls)}"


def test_marker_path_still_completes_normally_with_fix2_wired():
    """Regressionsschutz: ein ECHTER Markertreffer (normale Fertigstellung,
    kein `!save`-Sonderfall) bleibt mit `explicit_completion_attempt`
    verdrahtet unveraendert erfolgreich -- der Fix fuegt NUR eine
    zusaetzliche OR-Bedingung hinzu, ersetzt den Marker-Pfad nicht."""
    with tempfile.TemporaryDirectory() as td:
        leader_cid, guest_cid = "chrono-leader-mk", "chrono-guest-mk"
        lobby, table, ps_store, run_dir, states_dir = _build_table(Path(td), "t-marker", leader_cid, guest_cid)
        leader_save = full_v7_save(leader_cid, name="Test")
        guest_save = full_v7_save(guest_cid, name="Test")
        marker_debrief = (
            "Die Mission ist erfolgreich abgeschlossen.\n"
            f"```json\n{__import__('json').dumps(leader_save)}\n```\n"
            f"```json\n{__import__('json').dumps(guest_save)}\n```\n"
            f"{COMPLETION_MARKER} table_id=t-marker section_id=section-marker"
        )
        outcome, gm, leader_driver, guest_driver = _run_section(
            lobby, table, ps_store, run_dir, states_dir,
            gm_contents=["SL-Antwort auf Anker-Turn.", marker_debrief],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="Wir berichten den Erfolg.", origin_source="fake:leader-debrief"),
                ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
            ],
            guest_script=[_anchor_decision(guest_cid), ParticipantDecision(text="Reflexion: ok.", origin_source="fake:guest-reflect")],
            section_id="section-marker", explicit_completion_attempt=is_save_command, max_turns=5,
        )
        assert outcome.completion.success, outcome.completion.reason
        final_marker = store._completion_final_path(run_dir, "section-marker")
        assert final_marker.exists()


if __name__ == "__main__":
    import traceback

    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except Exception as exc:  # noqa: BLE001
                failures.append(name)
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
