#!/usr/bin/env python3
"""
tests/mmo_sim/test_save_command_completion_trigger_2026_10_22.py —
OPTION2-CMD (FIX-SPEC-OPTION2-CMD.md, 2026-10-22): Repro-first fuer den
KOMMANDO-basierten Abschnittsabschluss-Trigger -- ersetzt die PHRASEN-
basierte Variante (`test_deepsave_completion_trigger_2026_10_21.py`,
geloescht). Grund: der live gehostete GM formuliert die Save-Bestaetigung
FREI ("Deepsave wird ausgegeben"/"ausgegeben"/"exportiert") -- Prosa-
Matching ist tot (live3-Beweis). Der Trigger haengt jetzt am Leader-
`!save`/`!speichern`-Kommando dieses Turns + einem tatsaechlich bindbaren
v7-Save-Block, NICHT an GM-Worten.

Faehrt GENAU den Produktionspfad (`core.app_service.run_play_session`,
denselben, den `ui/tui.py` UND `core/lobby_flow.py` verwenden) mit einem
Fake-GM/geskripteten Treiber. Test 7 (Recovery) testet zusaetzlich die reine,
zustandslose `_section_completion_recovery.find_recoverable_entry`-Funktion
direkt (wie die bestehenden AR2/AR11-Tests), weil der kommando-gestuetzte
Recovery-Zweig dort additiv ansetzt.

Pure Python, nur `assert`, echter Exitcode (Konvention wie
`test_m1_runtime_section.py`)."""
from __future__ import annotations

import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_block_text, full_v7_save  # noqa: E402

import mmo_sim.core._section_completion_recovery as recovery  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.completion_marker import completion_marker_matches  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import save_command_entry_matches  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
)

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class ScriptedDriver:
    """Geskripteter Fake-Teilnehmer -- wie `test_m1_runtime_section.
    ScriptedDriver` (reiner Testcode, kein Cross-Test-Import, keine
    Produktabhaengigkeit)."""

    def __init__(self, script: list[ParticipantDecision]):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


class _FakeGmTransport:
    """Fake-GM-Transport an der Runtime-Grenze (kein Netz) -- liefert GENAU
    die vorgegebenen Antworttexte der Reihe nach, unabhaengig vom
    tatsaechlich gesendeten `user_text`."""

    def __init__(self, scripted_contents: list[str]):
        self._contents = list(scripted_contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        content = self._contents.pop(0) if self._contents else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake-chat"}


@dataclass
class Env:
    run_dir: Path
    states_dir: Path


def _make_env(root: Path) -> Env:
    env = Env(run_dir=root / "run", states_dir=root / "states")
    env.states_dir.mkdir(parents=True)
    return env


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _save_reply(char_ids: list[str], *, prose: str) -> str:
    """EINE beliebig formulierte Save-Prosa-Zeile gefolgt von je EINEM
    gueltigen v7-Block pro `char_ids`-Eintrag -- die Prosa selbst ist jetzt
    IRRELEVANT fuer den Trigger (Kommando-basiert), bleibt hier nur als
    realistische SL-Antwortform erhalten."""
    parts = [prose, "---"]
    for cid in char_ids:
        parts.append(full_v7_block_text(cid, name="Test"))
    return "\n".join(parts)


def _build_table(root: Path, table_id: str, leader_cid: str, guest_cids: list[str] | None = None):
    """1 Leader + N Gaeste (Fuenfer-Tischgrenze, N<=4). Liefert
    `(lobby, table, ps_store, env)`."""
    guest_cids = guest_cids or []
    env = _make_env(root)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, env.states_dir, "leader_pk", leader_cid)
    for idx, cid in enumerate(guest_cids):
        _seed_persona_state(ps_store, env.states_dir, f"guest{idx + 1}_pk", cid)

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    for idx in range(len(guest_cids)):
        lobby.join(f"guest{idx + 1}_pk")

    wants = [f"guest{idx + 1}_pk" for idx in range(len(guest_cids))]
    offer_events = [{"type": "offer", "id": "o1", "from": "leader_pk", "wants": wants}]
    for idx in range(len(guest_cids)):
        offer_events.append({"type": "consent", "offer_id": "o1", "from": f"guest{idx + 1}_pk", "accept": True})

    chrononaut_ids = {"leader_pk": leader_cid}
    for idx, cid in enumerate(guest_cids):
        chrononaut_ids[f"guest{idx + 1}_pk"] = cid

    table, derivation = store.create_table_from_offer_log(
        lobby, table_id, offer_log_events=offer_events, chrononaut_ids=chrononaut_ids,
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    write_test_profile(env.run_dir)
    return lobby, table, ps_store, env


def _run_section(
    lobby, table, ps_store, env, *, gm_contents, leader_script, guest_scripts,
    section_id, completion_fallback, max_turns,
):
    gm = _FakeGmTransport(scripted_contents=gm_contents)
    drivers = {"leader_pk": ScriptedDriver(leader_script)}
    contexts = {"leader_pk": {"user": "ctx-leader_pk"}}
    for idx, script in enumerate(guest_scripts):
        pk = f"guest{idx + 1}_pk"
        drivers[pk] = ScriptedDriver(script)
        contexts[pk] = {"user": f"ctx-{pk}"}
    controller = TableController(leader_key="leader_pk", drivers=drivers)
    event_log = EventLog(env.run_dir)
    outcome = app_service.run_play_session(
        lobby, table, gm, controller, section_id, contexts, env.states_dir,
        "2026-10-22", "2026-10-22T20:00:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, event_log=event_log,
        max_turns=max_turns, completion_fallback=completion_fallback,
    )
    return outcome, gm


def _anchor_decision(cid: str, text: str = "Anker-Text.") -> ParticipantDecision:
    return ParticipantDecision(text=text, save_payload=full_v7_save(cid, name="Test"), origin_source="fake:anchor")


# ---------------------------------------------------------------------------
# Test 1 (Kern, Repro-first, prosa-unabhaengig): ROT (ohne Fallback, altes
# Marker-only-Verhalten) -> GRUEN (mit dem kommando-basierten Fallback) --
# derselbe GM-Text mit der live3-Formulierung "Deepsave exportiert" (NICHT
# der alten Phrase "Deepsave wird ausgegeben"), an der das Phrasen-Matching
# scheiterte.
# ---------------------------------------------------------------------------
def test_save_command_with_bindable_block_completes_regardless_of_prose():
    with tempfile.TemporaryDirectory() as td_red, tempfile.TemporaryDirectory() as td_green:
        leader_cid = "chrono-leader-core"
        debrief = _save_reply([leader_cid], prose="SaveGuard: HQ-Phase bestaetigt. Deepsave exportiert.")

        # --- ROT: identischer Save-Text, aber OHNE injiziertes
        # `completion_fallback` -- beweist, dass ohne den Fix reiner
        # Marker-only-Betrieb den freien Prosa-Block NICHT erkennt.
        lobby, table, ps_store, env = _build_table(Path(td_red), "t-red", leader_cid)
        outcome_red, gm_red = _run_section(
            lobby, table, ps_store, env,
            gm_contents=["SL-Antwort auf Anker-Turn.", debrief],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
                ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
            ],
            guest_scripts=[], section_id="section-red", completion_fallback=None, max_turns=2,
        )
        assert not outcome_red.completion.success, (
            "ROT-Repro widerlegt: ohne Fallback haette 'Deepsave exportiert' (kein Marker, "
            f"kein Alt-Phrasenmatch) NICHT abschliessen duerfen, tat es aber "
            f"({outcome_red.completion.reason!r})."
        )
        assert outcome_red.harvested == {}
        assert len(gm_red.calls) == 2, "Anker + EIN Debrief-Turn ('!save') -- kein dritter Turn im ROT-Pfad."
        final_red = store._completion_final_path(env.run_dir, "section-red")
        assert not final_red.exists(), "ROT-Pfad darf kein __final.json geschrieben haben."

        # --- GRUEN: derselbe Text ("Deepsave exportiert"), jetzt MIT dem
        # kommando-basierten Fallback -- der Fix selbst. Beweist: das live3-
        # Problem (freie GM-Prosa) ist behoben, weil der Trigger GAR NICHT
        # mehr auf GM-Worte schaut.
        lobby2, table2, ps_store2, env2 = _build_table(Path(td_green), "t-green", leader_cid)
        outcome_green, gm_green = _run_section(
            lobby2, table2, ps_store2, env2,
            gm_contents=["SL-Antwort auf Anker-Turn.", debrief],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
                ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
            ],
            guest_scripts=[], section_id="section-green",
            completion_fallback=build_save_command_completion_fallback(table2, zeitriss_saves.harvest_from_debrief),
            max_turns=2,
        )
        assert outcome_green.completion.success, outcome_green.completion.reason
        assert outcome_green.completion.members_completed == ["leader_pk"]
        assert outcome_green.harvested, "Der echte Save-Block haette geerntet werden muessen."
        assert set(outcome_green.harvested.keys()) == {"leader_pk"}
        assert len(gm_green.calls) == 2, "Anker + EIN Debrief-Turn ('!save') -- kein dritter GM-Turn noetig."
        final_green = store._completion_final_path(env2.run_dir, "section-green")
        assert final_green.exists(), "GRUEN-Pfad haette __final.json schreiben muessen."
        published = store.load_current_save(env2.run_dir, "leader_pk", ps_store2, states_dir=env2.states_dir)
        assert published is not None and published.get("characters", [{}])[0].get("id") == leader_cid


# ---------------------------------------------------------------------------
# Test 2 (Import-Negativ, Flos Einwand): derselbe gueltige v7-Block in der
# GM-Antwort, aber Leader-Input dieses Turns ist KEIN Save-Kommando (normaler
# Spielzug) -> KEIN Abschluss (sonst wuerde jeder Start-Import triggern).
# ---------------------------------------------------------------------------
def test_block_present_but_leader_input_not_save_command_does_not_complete():
    with tempfile.TemporaryDirectory() as td:
        leader_cid = "chrono-leader-import"
        import_reply = _save_reply([leader_cid], prose="Willkommen zurueck, hier ist dein aktueller Stand:")
        lobby, table, ps_store, env = _build_table(Path(td), "t-import", leader_cid)
        outcome, gm = _run_section(
            lobby, table, ps_store, env,
            gm_contents=["SL-Antwort auf Anker-Turn.", import_reply],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="Normaler Spielzug.", origin_source="fake:leader-debrief"),
            ],
            guest_scripts=[], section_id="section-import",
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            max_turns=2,
        )
        assert not outcome.completion.success, (
            "ein gueltiger v7-Block OHNE Leader-'!save'-Kommando (normaler Spielzug/Import) "
            f"haette NICHT abschliessen duerfen ({outcome.completion.reason!r})."
        )
        assert outcome.harvested == {}


# ---------------------------------------------------------------------------
# Test 3 (SaveGuard-Verweigerung-Negativ): Leader-Input `!save`, aber die
# GM-Antwort liefert KEINEN Save-Block (Verweigerung ausserhalb HQ) -> KEIN
# Abschluss -- "nur HQ" wird so durch SaveGuard selbst erzwungen.
# ---------------------------------------------------------------------------
def test_save_command_without_any_block_does_not_complete():
    with tempfile.TemporaryDirectory() as td:
        leader_cid = "chrono-leader-refused"
        refusal = "SaveGuard: Ausserhalb des HQ ist kein Speichern moeglich. Kein Deepsave ausgegeben."
        lobby, table, ps_store, env = _build_table(Path(td), "t-refused", leader_cid)
        outcome, gm = _run_section(
            lobby, table, ps_store, env,
            gm_contents=["SL-Antwort auf Anker-Turn.", refusal],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
            ],
            guest_scripts=[], section_id="section-refused",
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            max_turns=2,
        )
        assert not outcome.completion.success, (
            "`!save` ausserhalb HQ ohne jeden Save-Block (SaveGuard-Verweigerung) haette "
            f"NICHT abschliessen duerfen ({outcome.completion.reason!r})."
        )
        assert outcome.harvested == {}


# ---------------------------------------------------------------------------
# Test 4 (Unbindbarer Block-Negativ): `!save` + v7-Block mit FREMDER char_id
# (kein aktuelles Tischmitglied) -> harvest leer -> KEIN Abschluss.
# ---------------------------------------------------------------------------
def test_save_command_with_unbindable_block_does_not_complete():
    with tempfile.TemporaryDirectory() as td:
        leader_cid = "chrono-leader-foreign"
        debrief = _save_reply(["chrono-stranger-not-at-this-table"], prose="Stand aktualisiert.")
        lobby, table, ps_store, env = _build_table(Path(td), "t-foreign", leader_cid)
        outcome, gm = _run_section(
            lobby, table, ps_store, env,
            gm_contents=["SL-Antwort auf Anker-Turn.", debrief],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
            ],
            guest_scripts=[], section_id="section-foreign",
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            max_turns=2,
        )
        assert not outcome.completion.success, (
            "`!save` + ein v7-Block mit einer FREMDEN char_id (nicht an einen aktuellen "
            f"Chrononauten bindbar) haette NICHT abschliessen duerfen ({outcome.completion.reason!r})."
        )
        assert outcome.harvested == {}


# ---------------------------------------------------------------------------
# Test 5 (Gruppen-Positiv): Leader + 2 Gaeste, Anker+2 Imports (Input !=
# '!save', kein Trigger), dann EIN Leader-'!save' mit GM-Antwort, die je
# Figur einen v7-Block liefert -> alle 3 geerntet, EIN Abschluss, kein
# Doppel-Fire (Turnzahl: Anker+2 Imports+1 Debrief = 4, kein fuenfter Turn).
# ---------------------------------------------------------------------------
def test_group_save_command_single_reply_harvests_all_members():
    with tempfile.TemporaryDirectory() as td:
        leader_cid, guest1_cid, guest2_cid = "chrono-leader-grp", "chrono-guest1-grp", "chrono-guest2-grp"
        lobby, table, ps_store, env = _build_table(
            Path(td), "t-group", leader_cid, guest_cids=[guest1_cid, guest2_cid],
        )
        group_debrief = _save_reply([leader_cid, guest1_cid, guest2_cid], prose="Gruppenstand ausgegeben.")
        outcome, gm = _run_section(
            lobby, table, ps_store, env,
            gm_contents=[
                "SL-Antwort auf Anker-Turn (Leader).",
                "SL-Antwort auf Import-Turn (Gast 1).",
                "SL-Antwort auf Import-Turn (Gast 2).",
                group_debrief,
            ],
            leader_script=[
                _anchor_decision(leader_cid),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
                ParticipantDecision(text="Reflexion: Leader zufrieden.", origin_source="fake:leader-reflect"),
            ],
            guest_scripts=[
                [
                    ParticipantDecision(text="Import Gast 1.", save_payload=full_v7_save(guest1_cid, name="Test"), origin_source="fake:guest1"),
                    ParticipantDecision(text="Reflexion: Gast 1 zufrieden.", origin_source="fake:guest1-reflect"),
                ],
                [
                    ParticipantDecision(text="Import Gast 2.", save_payload=full_v7_save(guest2_cid, name="Test"), origin_source="fake:guest2"),
                    ParticipantDecision(text="Reflexion: Gast 2 zufrieden.", origin_source="fake:guest2-reflect"),
                ],
            ],
            section_id="section-group",
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            max_turns=4,
        )
        assert outcome.completion.success, outcome.completion.reason
        assert set(outcome.completion.members_completed) == {"leader_pk", "guest1_pk", "guest2_pk"}
        assert set(outcome.harvested.keys()) == {"leader_pk", "guest1_pk", "guest2_pk"}
        assert len(gm.calls) == 4, (
            "Anker + 2 Import-Turns + GENAU EIN Gruppen-Debrief-Turn ('!save') -- kein "
            "Doppel-Fire/fuenfter Turn."
        )
        final_path = store._completion_final_path(env.run_dir, "section-group")
        assert final_path.exists(), "Gruppen-Abschluss haette __final.json schreiben muessen."


# ---------------------------------------------------------------------------
# Test 6 (Marker-Regression): der klassische Top-Level-Marker-Pfad bleibt
# UNVERAENDERT -- sowohl OHNE als auch MIT injiziertem Kommando-Fallback.
# ---------------------------------------------------------------------------
def test_marker_path_unchanged_with_and_without_fallback():
    for use_fallback in (False, True):
        with tempfile.TemporaryDirectory() as td:
            leader_cid = f"chrono-leader-marker-{use_fallback}"
            debrief = (
                "Abschnitt beendet.\n"
                f"{full_v7_block_text(leader_cid, name='Test')}\n"
                f"{COMPLETION_MARKER}"
            )
            lobby, table, ps_store, env = _build_table(Path(td), "t-marker", leader_cid)
            fallback = (
                build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief)
                if use_fallback else None
            )
            outcome, gm = _run_section(
                lobby, table, ps_store, env,
                gm_contents=["SL-Antwort auf Anker-Turn.", debrief],
                leader_script=[
                    _anchor_decision(leader_cid),
                    ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
                    ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
                ],
                guest_scripts=[], section_id="section-marker",
                completion_fallback=fallback, max_turns=2,
            )
            assert outcome.completion.success, (
                f"Marker-Pfad (fallback={use_fallback}) haette unveraendert abschliessen muessen "
                f"({outcome.completion.reason!r})."
            )
            assert set(outcome.harvested.keys()) == {"leader_pk"}


# ---------------------------------------------------------------------------
# Test 7 (Recovery): kommando-gestuetzte Crash-Recovery -- ein `sl_log` mit
# juengstem Eintrag `leader_message="!save"` + `content` mit gueltigem,
# bindbarem v7-Block (KEIN Marker) wird ueber das additive `entry_matches`-
# Praedikat trotzdem als recoverable erkannt. Gegenprobe: derselbe `content`,
# aber `leader_message` != Save-Kommando -> NICHT recoverable (reine
# Unit-Tests gegen `find_recoverable_entry` selbst, wie die bestehenden
# AR2/AR11-Tests).
# ---------------------------------------------------------------------------
class _FakeTableForFallback:
    """Minimaler Duck-Type fuer `build_save_command_completion_fallback`
    (braucht NUR `chrononaut_id_to_persona()`) -- kein vollstaendiges
    `store.Table`-Setup noetig fuer diesen reinen Unit-Test."""

    def __init__(self, cid_to_pk: dict[str, str]):
        self._cid_to_pk = cid_to_pk

    def chrononaut_id_to_persona(self) -> dict[str, str]:
        return self._cid_to_pk


def test_recovery_finds_save_command_entry_via_entry_matches_predicate():
    marker = COMPLETION_MARKER
    table_id = "t-recovery"
    section_id = "section-recovery"
    char_id = "chrono-recovery-leader"
    fallback = build_save_command_completion_fallback(
        _FakeTableForFallback({char_id: "leader_pk"}), zeitriss_saves.harvest_from_debrief,
    )

    # Treffe EXAKT die reale Recovery-Logik (kein Spiegel): die modulweite
    # `save_command_entry_matches`, an die die `_entry_matches`-Closure in
    # `run_full_section` 1:1 delegiert -- so kann dieser Test nicht von der
    # Produktionslogik wegdriften (genau die Drift, die B1/M1 durchrutschen liess).
    def entry_matches(entry: dict) -> bool:
        return save_command_entry_matches(entry, "leader_pk", fallback)

    block_content = _save_reply([char_id], prose="Stand gespeichert.")
    recoverable_entry = {
        "turn_idx": 3,
        "leader_message": "!save",
        "origin_persona_key": "leader_pk",
        "origin_raw_input": "!save",
        "content": block_content,
        "section_id": section_id,
        "expected_prev_ref_by_member": {"leader_pk": None},
    }
    found, hold_reason = recovery.find_recoverable_entry(
        [recoverable_entry], section_id, table_id, marker, completion_marker_matches,
        entry_matches=entry_matches,
    )
    assert found is recoverable_entry, (
        "ein kommando-gestuetzter Abschlussbeleg (Leader + '!save' + bindbarer v7-Block, "
        f"kein Marker) haette via entry_matches recoverable sein muessen -- "
        f"got (found={found!r}, hold_reason={hold_reason!r})."
    )
    assert hold_reason is None

    # Gegenprobe: derselbe content, aber origin_raw_input ist KEIN Save-Kommando.
    non_command_entry = dict(recoverable_entry, origin_raw_input="Normaler Spielzug.", leader_message="Normaler Spielzug.")
    found2, hold_reason2 = recovery.find_recoverable_entry(
        [non_command_entry], section_id, table_id, marker, completion_marker_matches,
        entry_matches=entry_matches,
    )
    assert found2 is None and hold_reason2 is None, (
        "ein Eintrag mit origin_raw_input != Save-Kommando (trotz gleichem content) haette "
        f"NICHT recoverable sein duerfen -- got (found={found2!r}, hold_reason={hold_reason2!r})."
    )

    # B1 (CRITIC-REPORT-CMD): ein GAST-Import-Eintrag (origin_persona_key !=
    # Leader) mit '!save' + bindbarem Block darf NIE als Leader-Abschluss
    # gelten -- Import-sicher auch im Recovery-Fenster.
    guest_entry = {
        "turn_idx": 2,
        "leader_message": "!save",
        "origin_persona_key": "guest1_pk",
        "origin_raw_input": "!save",
        "content": block_content,
        "section_id": section_id,
        "expected_prev_ref_by_member": {"leader_pk": None},
    }
    found_g, hold_g = recovery.find_recoverable_entry(
        [guest_entry], section_id, table_id, marker, completion_marker_matches,
        entry_matches=entry_matches,
    )
    assert found_g is None and hold_g is None, (
        "ein GAST-Import ('!save' von origin_persona_key='guest1_pk') haette NICHT als "
        f"Leader-Abschluss recoverable sein duerfen (B1) -- got (found={found_g!r})."
    )

    # M1 (CRITIC-REPORT-CMD): ein Leader-Anker-/Importturn, dessen
    # `leader_message` den eingebetteten Save-JSON-Block traegt, aber dessen
    # `origin_raw_input` der rohe '!save'-Befehl ist -> MUSS ueber den rohen
    # Input recoverable sein (nicht am eingebetteten leader_message scheitern).
    embedded_leader_entry = {
        "turn_idx": 4,
        "leader_message": "!save\n\n```json\n{\"v\": 7}\n```",
        "origin_persona_key": "leader_pk",
        "origin_raw_input": "!save",
        "content": block_content,
        "section_id": section_id,
        "expected_prev_ref_by_member": {"leader_pk": None},
    }
    found_m, hold_m = recovery.find_recoverable_entry(
        [embedded_leader_entry], section_id, table_id, marker, completion_marker_matches,
        entry_matches=entry_matches,
    )
    assert found_m is embedded_leader_entry and hold_m is None, (
        "ein Leader-'!save'-Turn mit eingebettetem Save-JSON im leader_message haette ueber "
        f"origin_raw_input recoverable sein muessen (M1) -- got (found={found_m!r})."
    )


# ---------------------------------------------------------------------------
# Test 8 (Default unveraendert): `completion_fallback=None` -> `completion_hit`
# reduziert sich exakt auf `marker_hit` (Alt-Verhalten) -- weder gewinnt ein
# `!save`-Kommando ohne injizierten Fallback neue Macht, noch verliert der
# klassische Marker-Pfad etwas.
# ---------------------------------------------------------------------------
def test_default_fallback_none_reduces_completion_hit_to_marker_hit():
    with tempfile.TemporaryDirectory() as td_a, tempfile.TemporaryDirectory() as td_b:
        # (a) Marker vorhanden, KEIN Fallback -- schliesst (marker_hit allein entscheidet).
        leader_cid_a = "chrono-leader-default-marker"
        debrief_a = f"Abschnitt beendet.\n{full_v7_block_text(leader_cid_a, name='Test')}\n{COMPLETION_MARKER}"
        lobby_a, table_a, ps_store_a, env_a = _build_table(Path(td_a), "t-default-a", leader_cid_a)
        outcome_a, gm_a = _run_section(
            lobby_a, table_a, ps_store_a, env_a,
            gm_contents=["SL-Antwort auf Anker-Turn.", debrief_a],
            leader_script=[
                _anchor_decision(leader_cid_a),
                ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
                ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
            ],
            guest_scripts=[], section_id="section-default-a", completion_fallback=None, max_turns=2,
        )
        assert outcome_a.completion.success, (
            f"ohne Fallback haette ein echter Marker weiterhin schliessen muessen ({outcome_a.completion.reason!r})."
        )

        # (b) KEIN Marker, aber Leader-Input ist '!save' + bindbarer v7-Block, KEIN
        # Fallback -- darf NICHT schliessen (ein `!save`-Kommando allein hat ohne
        # injizierten Fallback keine Sonderwirkung, exakt das Alt-Verhalten).
        leader_cid_b = "chrono-leader-default-nomarker"
        debrief_b = _save_reply([leader_cid_b], prose="Stand gespeichert.")
        lobby_b, table_b, ps_store_b, env_b = _build_table(Path(td_b), "t-default-b", leader_cid_b)
        outcome_b, gm_b = _run_section(
            lobby_b, table_b, ps_store_b, env_b,
            gm_contents=["SL-Antwort auf Anker-Turn.", debrief_b],
            leader_script=[
                _anchor_decision(leader_cid_b),
                ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
            ],
            guest_scripts=[], section_id="section-default-b", completion_fallback=None, max_turns=2,
        )
        assert not outcome_b.completion.success, (
            "ohne injizierten Fallback haette ein '!save' + bindbarer Block OHNE Marker "
            f"NICHT schliessen duerfen (Alt-Verhalten) ({outcome_b.completion.reason!r})."
        )
        assert outcome_b.harvested == {}


# ---------------------------------------------------------------------------
# Test 9 (Haertung, stale-last_leader_input): der Leader sendet am ANKER ein
# `!save`, das SaveGuard verweigert (kein Block, kein Abschluss) -- unmittelbar
# darauf echot ein GAST-Import in seiner GM-Antwort einen an den Gast bindbaren
# v7-Block. OHNE das Zuruecksetzen von `last_leader_input` auf den Nicht-Leader-
# Turn wuerde das frueher gesendete "!save" als stale Zustand haengen bleiben
# und den Gast-Import FAELSCHLICH als Abschluss werten. Mit der Haertung
# (`last_leader_input = None` fuer Nicht-Leader-Turns) schliesst nichts.
# ---------------------------------------------------------------------------
def test_stale_leader_save_does_not_complete_on_guest_import():
    with tempfile.TemporaryDirectory() as td:
        leader_cid, guest1_cid = "chrono-leader-stale", "chrono-guest1-stale"
        lobby, table, ps_store, env = _build_table(
            Path(td), "t-stale", leader_cid, guest_cids=[guest1_cid],
        )
        # Anker-Turn des Leaders ist bereits ein '!save' (mit eigenem Import-
        # Save-Payload, wie ein echter Ankerturn), die GM-Antwort darauf
        # verweigert (kein Block). Danach ein Gast-Import, dessen GM-Antwort
        # einen an den Gast bindbaren v7-Block echot.
        leader_anchor_save = ParticipantDecision(
            text="!save", save_payload=full_v7_save(leader_cid, name="Test"), origin_source="fake:anchor",
        )
        guest_import_echo = _save_reply([guest1_cid], prose="Willkommen, dein Stand:")
        outcome, gm = _run_section(
            lobby, table, ps_store, env,
            gm_contents=[
                "SaveGuard: Hier ist kein HQ -- kein Deepsave.",   # Anker-'!save' verweigert
                guest_import_echo,                                   # Gast-Import echot Block
                "SL-Antwort (laufender Turn, kein Block).",
            ],
            leader_script=[
                leader_anchor_save,
                ParticipantDecision(text="Normaler Spielzug.", origin_source="fake:leader-ongoing"),
                ParticipantDecision(text="Noch ein Spielzug.", origin_source="fake:leader-ongoing2"),
            ],
            guest_scripts=[[
                ParticipantDecision(
                    text="Gast tritt bei.", save_payload=full_v7_save(guest1_cid, name="Test"),
                    origin_source="fake:guest-import",
                ),
            ]],
            section_id="section-stale",
            completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            max_turns=2,
        )
        assert not outcome.completion.success, (
            "ein stale Leader-'!save' (am Anker verweigert) haette den unmittelbar folgenden "
            f"Gast-Import NICHT als Abschluss werten duerfen ({outcome.completion.reason!r})."
        )
        assert outcome.harvested == {}
        final = store._completion_final_path(env.run_dir, "section-stale")
        assert not final.exists(), "kein __final.json bei stale-'!save'-Gast-Import."


def main() -> int:
    tests = [
        test_save_command_with_bindable_block_completes_regardless_of_prose,
        test_block_present_but_leader_input_not_save_command_does_not_complete,
        test_save_command_without_any_block_does_not_complete,
        test_save_command_with_unbindable_block_does_not_complete,
        test_group_save_command_single_reply_harvests_all_members,
        test_marker_path_unchanged_with_and_without_fallback,
        test_recovery_finds_save_command_entry_via_entry_matches_predicate,
        test_default_fallback_none_reduces_completion_hit_to_marker_hit,
        test_stale_leader_save_does_not_complete_on_guest_import,
    ]
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
