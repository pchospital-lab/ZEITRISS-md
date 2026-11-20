#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r8_pending_save_commitfix_2026_11_20.py —
ZR-R8-STRUKTURTEST-TERMINAL-RAG-20261120-R1 Stage 3 (03_FIXAUFTRAG.md §4,
Kernbug H1 aus `run/preserve/M12-BINDING-MAP.md`).

Belegte Ursache (M12, Section `local-pe14d9b7bc5c84709__15`, Turns 6->7->8):
die SL gibt auf eine normale freie Aktion einen bindbaren eigenen HQ-Export
aus (KEIN begleitendes `!save`). Der Leader tippt erst einen Turn SPAETER
`!save`.

REWORK (Flos Order 2026-11-20, 03_FIXAUFTRAG.md §4): der urspruengliche Fix
(85f73130) war REAKTIV -- er liess das alleinstehende `!save` ERST ganz
normal zum GM gehen (bezahlter Call), wartete auf dessen SaveGuard-
Verweigerung und rettete DANACH den aelteren Export nach. Das verstoesst
gegen 03 §4 woertlich ("bevor ein weiterer GM-Saveaufruf entsteht") -- Flo
verlangt 0 zusaetzliche GM-/Correction-Calls, NICHT EINMAL den abgewiesenen.

Fix (dieser Rework): `core/runtime.py:SectionRuntime.run_full_section`s
`act()` prueft jetzt PRE-SEND -- GENAU an der Stelle, an der ein Leader-Turn
tatsaechlich an den GM-Transport dispatcht wird (VOR `wire_text`-Bau/
Reservierung/`self.submit()`) --, ob der aktuelle Leader-Input ein
explizites Save-Kommando ist UND ob bereits ein vollstaendig gueltiger,
nicht uebernommener eigener Export in `sl_log` liegt (`core/
_section_completion_recovery.find_pending_leader_export`, UNVERAENDERT).
Drei Faelle (03_FIXAUFTRAG.md §4 / Order §2): (1) Kandidat vollstaendig
gueltig -> Uebernahme ueber den vorhandenen `finalize`-Weg, OHNE den
`!save`-Turn je an den GM zu senden; (2) Kandidat vorhanden, aber
unvollstaendig/ungeeignet -> echter HOLD mit Grund, OHNE versteckte
Nachforderung (`finalize(..., pre_send=True)` unterdrueckt NUR den
`pursue_group_save_correction`-Zweig); (3) kein Kandidat -> regulaerer Weg,
das `!save` geht normal zum GM (z.B. fuer einen FRISCHEN Export, Fix-D-Test
unveraendert). Die vorherige REAKTIVE Pruefung (`completion_hit`s vierte
Bedingung, `_pending_export_candidate`) ist entfernt -- sie wird durch die
PRE-SEND-Pruefung vollstaendig ersetzt (kein Zwei-Pfade-Ueberlapp).

Testet am ECHTEN Verzweigungsort (`TuiSession._cmd_local_round` ->
`app_service.run_play_session` -> `core.runtime.SectionRuntime.run_full_
section`, derselbe Call-Pfad wie `test_zr_spiel_s1_fixd_save_integrity_
gate_2026_11_11.py`), KEIN isolierter Nachbau der Gate-/Recovery-Logik. Das
gescriptete GM-Fake wirft bei JEDEM Aufruf WAEHREND des `!save`-Turns (nicht
erst beim dritten) -- das ist der direkte Beleg fuer "0 zusaetzliche GM-/
Correction-Calls fuer DIESEN Turn".

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
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
from _section_completion_resume_fixtures import (  # noqa: E402
    ExplodingGmTransport, ReflectionOnlyDriver, ScriptedDriver, ScriptedGmTransport,
    build_two_member_table, make_env, make_ps_store, seed_persona_state,
)

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"

_CHAR_ID = "CHR-SNIPER-001"
_GATE_CORE_LINE = "der Stand wurde noch NICHT uebernommen"
_SAVEGUARD_REJECT = "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt."


def _queued_input(values: list[str]):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if not q:
            raise EOFError()
        return q.pop(0)
    return _fn


def _save_block_text(save_id: str, level: int = 2) -> str:
    block = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=level, save_id=save_id)
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


class _ScriptedTableGm:
    """Wie `test_zr_spiel_s1_fixd_save_integrity_gate_2026_11_11.py`s
    `_ScriptedTableGm`: wirft bei einem ueberzaehligen Call -- der direkte
    Beleg, dass ein abgewiesener/rekonstruierter Abschluss KEINEN weiteren
    GM-Call ausloest."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if not self._contents:
            raise AssertionError(
                f"_ScriptedTableGm: unerwarteter {len(self.calls)}. GM-Call (Skript erschoepft) "
                f"mit text={text!r} -- die Pending-Save-Commitfix-Uebernahme darf KEINEN "
                "zusaetzlichen GM-/Correction-Call ausloesen (03_FIXAUFTRAG.md §4/§5)."
            )
        content = self._contents.pop(0)
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, persona_key: str) -> dict:
    save = json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8"))
    from _full_v7_fixture import upgrade_narrow_save
    save = upgrade_narrow_save(save)
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    chrono_id = save["characters"][0]["id"]
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=persona_key, chrononaut_id=chrono_id, persona_key=persona_key,
    ))
    catalog.bind_for_section(catalog_dir, persona_key, chrono_id, has_open_section=False)
    return save


def _assert_calls(calls: list[str], expected_texts: list[str]) -> None:
    assert len(calls) == len(expected_texts), (calls, expected_texts)
    for actual, expected in zip(calls, expected_texts):
        assert actual == expected or actual.startswith(expected + "\n"), (actual, expected)


def test_m12_pre_send_adopts_prior_export_on_save_command_zero_gm_calls():
    """M12-Kernfall, PRE-SEND (Order §2 Fall 1, 03 §4/§5 "Expliziter Commit,
    Kandidat vollstaendig gueltig"): eine normale freie Aktion zeigt einen
    bindbaren, nicht uebernommenen eigenen Export (KEIN `!save` dabei) -> der
    Leader wird vom bestehenden Fix-D-Gate auf `!save` verwiesen -> das
    LITERALE `!save` darf den GM GAR NICHT MEHR erreichen (anders als vor
    diesem Rework) -- `act()` uebernimmt den frueher gezeigten Export bereits
    VOR jedem Dispatch. Das Skript haelt nur EINEN Eintrag bereit (die
    Export-Antwort auf die normale Aktion) -- JEDER weitere `.turn()`-Aufruf
    (also auch fuer den `!save`-Turn selbst) wirft."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            _save_block_text("m12-hq03-candidate-001", level=5),  # Turn 7: Deepsave auf freie Aktion.
            # KEIN zweiter Eintrag -- der '!save'-Turn darf den GM NIE erreichen.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich frage Halvorsen nach dem offenen Rift.",  # Turn 7 (normale Aktion).
                "!save",  # Turn 8 (vom Fix-D-Gate erzwungen) -- PRE-SEND, 0 GM-Calls.
                "",  # Pflicht-Abschlussnotiz -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        # Order §2 woertlich: "0 zusaetzliche GM-/Correction-Calls, nicht
        # einmal der abgewiesene" -- der '!save'-Turn selbst erzeugt KEINEN
        # Call mehr (anders als im ersten, reaktiven Fix: dort war es exakt
        # EIN zusaetzlicher, abgewiesener Call).
        _assert_calls(gm.calls, ["Ich frage Halvorsen nach dem offenen Rift."])
        assert any("Abschnitt abgeschlossen" in p for p in printed), (
            f"der frueher gezeigte Export musste PRE-SEND uebernommen worden sein: {printed}"
        )

        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after is not None and current_after.get("save_id") == "m12-hq03-candidate-001", (
            "Current muss GENAU den Inhalt des frueher gezeigten Exports tragen (03 §5 "
            f"'Uebernahme genau dieses Inhalts'), nicht aus der Reject-Antwort: {current_after}"
        )
        assert current_after["characters"][0].get("lvl") == 5, current_after


def test_m12_saveguard_reject_without_any_prior_export_stays_open_no_silent_success():
    """Negativfall (03 §5 "echte Mission-/City-/Arena-SaveGuard-
    Verweigerung"/"kein Export"): `!save` ohne JEDEN vorherigen bindbaren
    Export -> SaveGuard-Verweigerung bleibt eine ehrliche Verweigerung,
    KEINE stillschweigende Uebernahme irgendeines anderen Inhalts, Current
    bleibt unveraendert, kein 'Abschnitt abgeschlossen'."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        save_sniper = _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            "Ihr steht noch mitten im Einsatz.",  # normale Aktion, KEIN Export.
            _SAVEGUARD_REJECT,  # '!save' ausserhalb des HQ -- echte Verweigerung.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich sichere die Position.",
                "!save",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # kontrollierte Fortsetzung der laufenden Runde -- Eingabequeue erschoepft.

        _assert_calls(gm.calls, ["Ich sichere die Position.", "!save"])
        assert not any("Abschnitt abgeschlossen" in p for p in printed), (
            f"eine echte SaveGuard-Verweigerung ohne jeden Export darf NICHT als Erfolg "
            f"umgedeutet werden: {printed}"
        )
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after == save_sniper, (
            "Current darf durch eine ehrliche SaveGuard-Verweigerung NICHT veraendert worden "
            f"sein: {current_after}"
        )


def test_m12_pre_send_holds_on_stale_generation_no_adoption():
    """Testmatrix (Order §5 "Geaenderte Ursprungsgeneration / veralteter
    Snapshot -> HOLD, keine Uebernahme"): zwischen dem Export-Turn (der den
    PRE-SEND-Kandidaten erzeugt, samt `expected_prev_ref_by_member`-
    Schnappschuss von DIESEM Zeitpunkt) und dem spaeteren `!save` wird der
    TATSAECHLICHE Current-Stand ausserhalb der normalen Rundenfolge
    weiterbewegt (`core_store.publish_current_save`, z.B. ein Import/eine
    andere parallele Uebernahme). Die bestehende Drift-Pruefung in
    `store.py:_resume_and_harvest` (`expected_prev_ref != actual_prev_ref`,
    UNVERAENDERT) muss das PRE-SEND `finalize(..., pre_send=True)` genauso
    halten wie jeden anderen Aufrufer -- OHNE den Kandidaten zu uebernehmen
    und OHNE dass der `!save`-Turn den GM je erreicht (das Skript haelt nur
    EINEN Eintrag bereit)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            _save_block_text("m12-hq03-candidate-stale", level=5),  # Export-Turn (Kandidat).
            # KEIN zweiter Eintrag -- der '!save'-Turn darf den GM NIE erreichen.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich frage Halvorsen nach dem offenen Rift.",  # Export-Turn, NOCH KEIN '!save'.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass

        # Nach dem Export-Turn, VOR dem '!save': ein unabhaengiger, nicht aus
        # der normalen Rundenfolge stammender Publish bewegt den TATSAECHLICHEN
        # Current-Stand weiter -- der im Export-Turn gebundene `expected_prev_
        # ref_by_member`-Schnappschuss ist jetzt veraltet.
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        unrelated_save = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=9, save_id="unrelated-out-of-band")
        core_store.publish_current_save(run_dir, "sniper", unrelated_save, ps_store, states_dir)
        calls_before_save = list(gm.calls)

        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input(["!save"]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session2._cmd_local_round()
        except EndOfInput:
            pass

        assert gm.calls == calls_before_save, (
            "kein NEUER GM-Call fuer den '!save'-Turn erwartet (PRE-SEND-HOLD): " + repr(gm.calls)
        )
        assert not any("Abschnitt abgeschlossen" in p for p in printed), (
            f"eine veraltete Generation darf NICHT stillschweigend uebernommen werden: {printed}"
        )
        assert any("Vorgaengergeneration" in p or "nicht abgeschlossen" in p for p in printed), (
            f"der HOLD-Grund muss am realen Caller sichtbar sein: {printed}"
        )
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after == unrelated_save, (
            f"der Kandidat darf den unabhaengig weiterbewegten Current NICHT ueberschrieben haben: {current_after}"
        )


def _fenced_save(block: dict) -> str:
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


def _duo_run_section(lobby, table, ps_store, gm, controller, section_id, states_dir, max_turns):
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}},
        states_dir, "2026-11-20", "2026-11-20T09:30:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=max_turns,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


def test_m12_pre_send_mixed_group_adopts_full_group_zero_calls():
    """Testmatrix (Order §5 "Volle Mischgruppe", positiv): >=2 Mitglieder.
    Der Gast ist BEREITS vollstaendig gueltig gecacht (reuse des bestehenden
    J4-ROOTFIX-Seitencaches `_store_pending_valid_block`/`_load_pending_
    valid_block`, s. `store.complete_section`-Docstring; derselbe Mechanismus,
    der eine vorherige `pursue_group_save_correction`-Runde fuer EIN ANDERES
    Mitglied ueberlebt) -- NUR der Leader zeigt einen eigenen, noch nicht
    uebernommenen Export. `!save` muss PRE-SEND BEIDE Mitglieder exakt
    uebernehmen, OHNE jeden GM-Call (`ExplodingGmTransport`)."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-mixed-ok")
        write_test_profile(env.run_dir)
        section_id = "section-m12-mixed-ok"

        guest_good = full_v7_save("chrono-guest", name="Guest")
        pre_seed = store.complete_section(
            lobby, table, section_id, {"guest_pk": guest_good}, env.states_dir, "2026-11-20",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not pre_seed.success and pre_seed.missing == ["leader_pk"], pre_seed

        leader_export = full_v7_save("chrono-leader", name="Leader", level=5, save_id="m12-mixed-ok-leader")
        gm_setup = ScriptedGmTransport(scripted_contents=[
            _fenced_save(leader_export),  # Leader-Anker-Turn (Export, kein Marker).
            "Normaler Gastimport, keine Besonderheit.",  # Gast-Import-Turn.
        ])
        controller_setup = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([ParticipantDecision(text="Ich frage Halvorsen nach dem Rift.", origin_source="fake:scripted")]),
            "guest_pk": ScriptedDriver([ParticipantDecision(text="Ich importiere meine Figur.", origin_source="fake:scripted")]),
        })
        setup_outcome = _duo_run_section(
            lobby, table, ps_store, gm_setup, controller_setup, section_id, env.states_dir, max_turns=1,
        )
        assert not setup_outcome.completion.success, setup_outcome.completion  # kein Marker, Setup nur zum Export.

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_save = ExplodingGmTransport()
        controller_save = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="!save", origin_source="fake:scripted"),
                ParticipantDecision(text="Kurzer Rueckblick Leader.", origin_source="fake:scripted"),
            ]),
            "guest_pk": ReflectionOnlyDriver(reflection_text="Rueckblick Gast."),
        })
        outcome = _duo_run_section(
            lobby, table2, ps_store, gm_save, controller_save, section_id, env.states_dir, max_turns=5,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_save.calls == 0, f"kein GM-Call fuer den '!save'-Turn erwartet: {gm_save.calls}"
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) == leader_export
        assert store.load_current_save(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir) == guest_good


def test_m12_pre_send_mixed_group_holds_without_hidden_correction_call():
    """Testmatrix (Order §5 "Volle Mischgruppe", negativ -- 03 §4 "ohne
    versteckte bezahlte Nachforderung"): der Gast hat KEINEN gueltigen
    gecachten Block -- der Leader-Kandidat allein deckt die Gruppe NICHT.
    PRE-SEND darf den bestehenden `pursue_group_save_correction`-Weg NICHT
    erreichen (`ExplodingGmTransport` wirft bei JEDEM Aufruf) -- der
    Abschnitt haelt ehrlich mit dem bestehenden `missing`-Grund, kein
    unberechtigter Gruppenabschluss, kein automatischer Correction-Call."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-mixed-hold")
        write_test_profile(env.run_dir)
        section_id = "section-m12-mixed-hold"

        leader_export = full_v7_save("chrono-leader", name="Leader", level=5, save_id="m12-mixed-hold-leader")
        gm_setup = ScriptedGmTransport(scripted_contents=[
            _fenced_save(leader_export),
            "Normaler Gastimport, keine Besonderheit.",
        ])
        controller_setup = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([ParticipantDecision(text="Ich frage Halvorsen nach dem Rift.", origin_source="fake:scripted")]),
            "guest_pk": ScriptedDriver([ParticipantDecision(text="Ich importiere meine Figur.", origin_source="fake:scripted")]),
        })
        setup_outcome = _duo_run_section(
            lobby, table, ps_store, gm_setup, controller_setup, section_id, env.states_dir, max_turns=1,
        )
        assert not setup_outcome.completion.success, setup_outcome.completion

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_save = ExplodingGmTransport()
        controller_save = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([ParticipantDecision(text="!save", origin_source="fake:scripted")]),
            "guest_pk": ExplodingDriverStub(),
        })
        outcome = _duo_run_section(
            lobby, table2, ps_store, gm_save, controller_save, section_id, env.states_dir, max_turns=1,
        )
        assert not outcome.completion.success, (
            f"ein fehlender Gast darf NICHT zu einem unberechtigten Gruppenabschluss fuehren: {outcome.completion}"
        )
        assert "guest_pk" in outcome.completion.missing, outcome.completion
        assert gm_save.calls == 0, (
            f"kein versteckter Correction-Call fuer den fehlenden Gast erwartet: {gm_save.calls}"
        )
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) is None, (
            "ohne vollstaendige Gruppe darf auch der Leader-Anteil NICHT publiziert worden sein."
        )


class ExplodingDriverStub:
    """Guest-Treiber fuer den Mischgruppen-HOLD-Test: wird NICHT benoetigt
    (kein Poll in Runde 0, kein Reflexionsturn vor einem gehaltenen
    Abschluss) -- jeder Aufruf waere ein Testversagen."""

    def decide(self, context: dict):
        raise AssertionError("ExplodingDriverStub: keine Gast-Entscheidung erwartet (Abschluss haelt vor Reflexion).")


def test_m12_pre_send_survives_restart_with_trailing_reject_history_zero_calls():
    """Testmatrix (Order §2 "Muss nach Neustart ... UND mit bereits
    vorhandener Reject-Historie funktionieren"): nach dem Export-Turn wird
    EIN synthetischer, aus der Zeit VOR diesem Rework stammender Reject-
    Turn-Eintrag direkt in `sl_log` nachgetragen (derselbe Eintragstyp wie
    ein frueherer `!save`, der noch den alten, reaktiven Call-und-Reject-Weg
    durchlaufen hat) -- `find_pending_leader_export` darf diesen Save-
    Kommando-Eintrag weder als Kandidat noch als Story-Fortschritts-
    Invalidator werten (bestehende Garantie, UNVERAENDERT). Danach wird der
    Tisch NEU von Platte geladen (`store.Table.load`, derselbe Vertrag wie
    ein echter Prozess-Neustart ueber '1) Fortsetzen') und `!save` erneut
    gesendet -- PRE-SEND muss weiterhin OHNE jeden GM-Call uebernehmen."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        schema_path = env.run_dir.parent / "schema.json"
        ps_store = make_ps_store(schema_path)
        seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader")

        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-m12-restart",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
            chrononaut_ids={"leader_pk": "chrono-leader"},
        )
        assert table is not None, derivation
        write_test_profile(env.run_dir)
        section_id = "section-m12-restart"

        leader_export = full_v7_save("chrono-leader", name="Leader", level=5, save_id="m12-restart-leader")
        gm_setup = ScriptedGmTransport(scripted_contents=[_fenced_save(leader_export)])
        controller_setup = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([ParticipantDecision(text="Ich frage Halvorsen nach dem Rift.", origin_source="fake:scripted")]),
        })
        setup_outcome = app_service.run_play_session(
            lobby, table, gm_setup, controller_setup, section_id,
            {"leader_pk": {"user": "ctx-leader_pk"}},
            env.states_dir, "2026-11-20", "2026-11-20T09:30:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=1,
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        assert not setup_outcome.completion.success, setup_outcome.completion

        # Synthetischer Alt-Reject (reprodiziert den VOR diesem Rework
        # moeglichen Zustand: ein '!save', das noch den alten reaktiven Weg
        # durchlaufen hat und vom GM abgewiesen wurde) -- direkt an sl_log
        # angehaengt, kein Codepfad dieses Rework erzeugt das mehr selbst.
        table.sl_log.append({
            "turn_idx": len(table.sl_log), "origin_persona_key": "leader_pk",
            "section_id": section_id, "origin_raw_input": "!save",
            "content": _SAVEGUARD_REJECT, "gm_request_id": None,
        })
        table.persist()

        # Neustart: frischer Tisch-Load von Platte (derselbe Vertrag wie
        # '1) Fortsetzen' nach Prozessende).
        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_restart = ExplodingGmTransport()
        controller_restart = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="!save", origin_source="fake:scripted"),
                ParticipantDecision(text="Kurzer Rueckblick nach Neustart.", origin_source="fake:scripted"),
            ]),
        })
        outcome = app_service.run_play_session(
            lobby, table2, gm_restart, controller_restart, section_id,
            {"leader_pk": {"user": "ctx-leader_pk"}},
            env.states_dir, "2026-11-20", "2026-11-20T09:31:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=5,
            completion_fallback=build_save_command_completion_fallback(table2, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_restart.calls == 0, f"kein GM-Call nach Neustart erwartet: {gm_restart.calls}"
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) == leader_export


def test_m12_pre_send_idempotent_second_entry_no_double_write():
    """Testmatrix (Order §5 "Idempotente Wiederholung / unterbrochene
    Finalisierung"): nach erfolgreicher PRE-SEND-Uebernahme (solo) ist ein
    zweiter, idempotenter Re-Entry (derselbe Vertrag wie die bestehende
    R12-AUTORECOVERY-Idempotenz, `test_j3_second_fresh_entry_after_restart_
    is_idempotent`) KEIN zweiter Write/keine doppelte Buchung -- `store.
    complete_section` erkennt den bereits finalisierten `section_id` ueber
    `final_path.exists()` (UNVERAENDERT)."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        schema_path = env.run_dir.parent / "schema.json"
        ps_store = make_ps_store(schema_path)
        seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader")
        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-m12-idempotent",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
            chrononaut_ids={"leader_pk": "chrono-leader"},
        )
        assert table is not None, derivation
        write_test_profile(env.run_dir)
        section_id = "section-m12-idempotent"

        leader_export = full_v7_save("chrono-leader", name="Leader", level=5, save_id="m12-idempotent-leader")
        gm_setup = ScriptedGmTransport(scripted_contents=[_fenced_save(leader_export)])
        controller_setup = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([ParticipantDecision(text="Ich frage Halvorsen nach dem Rift.", origin_source="fake:scripted")]),
        })
        setup_outcome = app_service.run_play_session(
            lobby, table, gm_setup, controller_setup, section_id,
            {"leader_pk": {"user": "ctx-leader_pk"}},
            env.states_dir, "2026-11-20", "2026-11-20T09:30:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=1,
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        assert not setup_outcome.completion.success, setup_outcome.completion

        table2 = store.Table.load(env.run_dir, table.table_id)
        controller_save = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="!save", origin_source="fake:scripted"),
                ParticipantDecision(text="Kurzer Rueckblick.", origin_source="fake:scripted"),
            ]),
        })
        outcome1 = app_service.run_play_session(
            lobby, table2, ExplodingGmTransport(), controller_save, section_id,
            {"leader_pk": {"user": "ctx-leader_pk"}},
            env.states_dir, "2026-11-20", "2026-11-20T09:31:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=5,
            completion_fallback=build_save_command_completion_fallback(table2, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        assert outcome1.completion.success, outcome1.completion

        idempotent = store.complete_section(
            lobby, table2, section_id, {}, env.states_dir, "2026-11-20",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert idempotent.success and idempotent.already_completed and not idempotent.written, idempotent
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) == leader_export


def test_m12_pre_send_ignores_candidate_after_real_story_progress_end_to_end():
    """Testmatrix (Order §5 "Zwischenzeitlicher Gast-/Gruppenfortschritt
    nach dem Kandidaten -> Kandidat ungueltig, normaler Weg"), END-TO-END
    (Ergaenzung zum bereits vorhandenen reinen Einheitentest
    `test_unit_find_pending_leader_export_blocks_on_real_story_progress_
    after_candidate`): eine ECHTE weitere freie Aktion NACH dem Export
    macht den Kandidaten ungueltig -- `!save` geht wieder regulaer zum GM
    (dessen dritter Eintrag hier eine ehrliche SaveGuard-Verweigerung ist,
    weil kein neuer Export vorliegt). Auf `app_service.run_play_session`-
    Ebene (wie die uebrigen Matrixtests) statt ueber `TuiSession`: das
    bestehende Fix-D-UI-Gate (`ui/tui.py`, sperrt JEDE normale Folgeaktion
    des MENSCHLICHEN Terminal-Leaders nach einem gezeigten unbindbaren
    Export) wuerde die zweite freie Aktion hier sonst VOR dem echten
    Call abfangen -- das ist eine reine UI-Schutzschicht, kein Teil des
    hier getesteten Engine-Vertrags (`find_pending_leader_export` wird
    unveraendert ueber einen nicht-menschlichen `ScriptedDriver` erreicht,
    exakt wie bei den uebrigen Mischgruppen-/Neustart-Tests)."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        schema_path = env.run_dir.parent / "schema.json"
        ps_store = make_ps_store(schema_path)
        seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader")
        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-m12-superseded",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
            chrononaut_ids={"leader_pk": "chrono-leader"},
        )
        assert table is not None, derivation
        write_test_profile(env.run_dir)
        section_id = "section-m12-superseded"

        leader_export = full_v7_save("chrono-leader", name="Leader", level=5, save_id="m12-superseded-candidate")
        gm = ScriptedGmTransport(scripted_contents=[
            _fenced_save(leader_export),  # Export-Turn (wird durch die naechste echte Aktion ungueltig).
            "Ihr zieht weiter, nichts Besonderes passiert.",  # ECHTE neue freie Aktion danach.
            _SAVEGUARD_REJECT,  # '!save' geht regulaer zum GM (kein Kandidat mehr) -> ehrlicher Reject.
        ])
        controller = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="Ich frage Halvorsen nach dem Rift.", origin_source="fake:scripted"),
                ParticipantDecision(text="Ich gehe weiter zur naechsten Kreuzung.", origin_source="fake:scripted"),
                ParticipantDecision(text="!save", origin_source="fake:scripted"),
            ]),
        })
        outcome = app_service.run_play_session(
            lobby, table, gm, controller, section_id,
            {"leader_pk": {"user": "ctx-leader_pk"}},
            env.states_dir, "2026-11-20", "2026-11-20T09:30:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=3,
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command, save_guard_rejection_detector=is_saveguard_rejection,
        )
        assert not outcome.completion.success, (
            f"ein durch echten Storyfortschritt ueberholter Kandidat darf NICHT uebernommen werden: {outcome.completion}"
        )
        assert len(gm.calls) == 3, (
            f"'!save' muss regulaer (dritter Call) zum GM gehen, da kein aktueller Kandidat mehr vorliegt: {gm.calls}"
        )
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) is None, (
            "Current darf unveraendert bleiben (kein stiller Fallback auf den ueberholten Kandidaten)."
        )


def _is_save_command(text: str | None) -> bool:
    return (text or "").strip().casefold() in {"!save", "!speichern"}


def test_unit_find_pending_leader_export_picks_latest_valid_non_save_entry():
    """Reine Einheitenpruefung der neuen `core/_section_completion_
    recovery.find_pending_leader_export` (03 §4): findet den JUENGSTEN
    leader-eigenen, nicht-Save-Kommando-Eintrag dieser Section, dessen
    `harvest_own_export` True liefert -- bei mehreren gueltigen Treffern den
    AKTUELLSTEN (anders als `ui/tui.py`s Warn-Gate, das bewusst beim ERSTEN
    Fund stehenbleibt)."""
    from mmo_sim.core import _section_completion_recovery as recovery

    _snap = {"expected_prev_ref_by_member": {"leader": None}}
    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "alt-export", **_snap},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion B", "content": "neu-export", **_snap},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "!save", "content": "reject", **_snap},
    ]
    exportable = {"neu-export", "alt-export"}
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") in exportable,
        is_explicit_save_command=_is_save_command,
    )
    assert hold_reason is None, hold_reason
    assert candidate is not None and candidate["content"] == "neu-export", candidate


def test_unit_find_pending_leader_export_blocks_on_real_story_progress_after_candidate():
    """Negativfall (03 §4 'keine versteckte Eskalation'/§5 'zwischen-
    zeitlicher Storyfortschritt'): eine ECHTE weitere freie Aktion des
    Leaders NACH dem Kandidaten (kein Save-Kommando, kein neuer Export)
    macht den Kandidaten nicht mehr aktuell -- `(None, None)`, der normale
    Weg bleibt unveraendert (keine stillschweigende Uebernahme eines
    veralteten Exports)."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "export"},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Echte neue Aktion", "content": "story weiter"},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "!save", "content": "reject"},
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
    )
    assert candidate is None and hold_reason is None, (candidate, hold_reason)


def test_unit_find_pending_leader_export_holds_on_missing_generation_snapshot():
    """AR2-Analogon (03 §4 Provenienz): ein sonst gueltiger Kandidat OHNE
    `expected_prev_ref_by_member` ('Legacy'/keine R12-Bindung) wird NICHT
    automatisch uebernommen, sondern als HOLD mit Begruendung gemeldet --
    dieselbe Vorsicht wie `find_recoverable_entry`."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "export"},
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
    )
    assert candidate is None, candidate
    assert hold_reason is not None and "Generations-Schnappschuss" in hold_reason, hold_reason


def test_unit_find_pending_leader_export_honors_request_binding_error():
    """03 §4 Originalprovenienz: ein injizierter `request_binding_error`-
    Treffer (z.B. fehlender/abweichender Original-Requestbeleg) wird 1:1
    als HOLD-Grund durchgereicht -- KEINE automatische Uebernahme trotz
    sonst vollstaendiger Bindung."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {
            "origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A",
            "content": "export", "expected_prev_ref_by_member": {"leader": None},
        },
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
        request_binding_error=lambda entry: "kein gebundener Original-Requestbeleg",
    )
    assert candidate is None, candidate
    assert hold_reason == "kein gebundener Original-Requestbeleg", hold_reason


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
