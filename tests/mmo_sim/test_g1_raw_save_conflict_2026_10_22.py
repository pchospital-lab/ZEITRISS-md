#!/usr/bin/env python3
"""
tests/mmo_sim/test_g1_raw_save_conflict_2026_10_22.py —
G1_RAW_SAVE_CONFLICT (02-AUFTRAG.md §1, 01-SAVE-CODE-REVIEW.md §G1,
2026-10-22): Repro-first fuer den engen Erstharvest-Konflikt.

Befund: `harvest_from_debrief` dedupliziert Savebloecke nach 'erster
gewinnt' (`extract_all_saves`), BEVOR ihre Widerspruchsfreiheit geprueft
wird. Gibt der GM auf ein Leader-`!save` fuer DIESELBE aktuelle Figur zwei
jeweils gueltige, aber ABWEICHENDE v7-Bloecke aus, verschwindet der zweite
Stand lautlos -- und bei ansonsten vollstaendiger Tischgruppe wird der
erste Block als erfolgreicher Abschnitt veroeffentlicht (Plan gepinnt,
__final geschrieben, Sequenz erhoeht). Die strengere Rohkonfliktpruefung
(`save_correction.pursue_group_save_correction`) wird NUR bei fehlender/
ungueltiger Erstannahme erreicht -- hier also nie.

Fix (gezielt, kein neuer Savepfad): ein injizierter `harvest_conflict_
detector` (gebaut aus `policy.build_harvest_conflict_detector`, Reuse der
VORHANDENEN `save_validation.extract_checked_single`/`find_duplicate_save_
ids`) prueft die ROHEN, noch undeduplizierten Bloecke je aktueller Figur
VOR `complete_section`. Konflikt -> HALTEN (kein Gewinner, kein Pin, kein
__final, kein seq-Fortschritt). Identische Wiederholung ist KEIN Konflikt.

Faehrt GENAU den Produktionspfad (`core.app_service.run_play_session`,
denselben, den `ui/tui.py` UND `core/lobby_flow.py` verwenden) mit einem
Fake-GM/geskripteten Treiber. Pure Python, nur `assert`, echter Exitcode
(Konvention wie `test_save_command_completion_trigger_2026_10_22.py`)."""
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
    build_harvest_conflict_detector,
    build_save_command_completion_fallback,
)

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class ScriptedDriver:
    """Geskripteter Fake-Teilnehmer (reiner Testcode, kein Cross-Test-Import)."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


class _FakeGmTransport:
    """Fake-GM-Transport an der Runtime-Grenze (kein Netz) -- liefert GENAU
    die vorgegebenen Antworttexte der Reihe nach."""

    def __init__(self, scripted_contents):
        self._contents = list(scripted_contents)
        self.calls = []

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


def _seed_persona_state(ps_store, states_dir, pk, char_id):
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_table(root: Path, table_id: str, leader_cid: str, guest_cids=None):
    """1 Leader + N Gaeste. Liefert `(lobby, table, ps_store, env)`."""
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


def _anchor_decision(cid: str, text: str = "Anker-Text.") -> ParticipantDecision:
    return ParticipantDecision(text=text, save_payload=full_v7_save(cid, name="Test"), origin_source="fake:anchor")


def _run_leader_guest_section(
    lobby, table, ps_store, env, *, gm_contents, guest_cids, section_id,
    with_conflict_detector: bool,
):
    """Faehrt einen Gruppen-Abschnitt: Anker (Leader) + je ein Import-Turn
    pro Gast + EIN Leader-'!save'-Debrief-Turn. `with_conflict_detector`
    steuert, ob der G1-Fix aktiv ist (ROT=False -> Alt-Verhalten)."""
    gm = _FakeGmTransport(scripted_contents=gm_contents)
    drivers = {"leader_pk": ScriptedDriver([
        _anchor_decision(table.chrononaut_ids["leader_pk"]),
        ParticipantDecision(text="!save", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
    ])}
    contexts = {"leader_pk": {"user": "ctx-leader_pk"}}
    for idx, cid in enumerate(guest_cids):
        pk = f"guest{idx + 1}_pk"
        drivers[pk] = ScriptedDriver([
            ParticipantDecision(text=f"Import Gast {idx + 1}.", save_payload=full_v7_save(cid, name="Test"), origin_source=f"fake:guest{idx + 1}"),
            ParticipantDecision(text=f"Reflexion: Gast {idx + 1} zufrieden.", origin_source=f"fake:guest{idx + 1}-reflect"),
        ])
        contexts[pk] = {"user": f"ctx-{pk}"}
    controller = TableController(leader_key="leader_pk", drivers=drivers)
    event_log = EventLog(env.run_dir)
    outcome = app_service.run_play_session(
        lobby, table, gm, controller, section_id, contexts, env.states_dir,
        "2026-10-22", "2026-10-22T20:00:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, event_log=event_log,
        max_turns=2 + len(guest_cids),
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        harvest_conflict_detector=build_harvest_conflict_detector() if with_conflict_detector else None,
    )
    return outcome, gm


def _conflict_debrief(leader_cid, guest_cid, *, leader_blocks, guest_wallet=0.0):
    """Gruppen-Debrief: die `leader_blocks` (eine Liste von (save_id, wallet)-
    Tupeln) ergeben je einen v7-Block fuer `leader_cid`, dazu EIN sauberer
    Block fuer `guest_cid` (ansonsten vollstaendige Tischgruppe)."""
    parts = ["SaveGuard: HQ bestaetigt. Deepsave ausgegeben.", "---"]
    for save_id, wallet in leader_blocks:
        parts.append(full_v7_block_text(leader_cid, name="Test", save_id=save_id, wallet=wallet))
    parts.append(full_v7_block_text(guest_cid, name="Test", wallet=guest_wallet))
    return "\n".join(parts)


def _assert_held(outcome, env, section_id, ps_store, states_dir, leader_pk="leader_pk"):
    assert not outcome.completion.success, (
        "ein Save-Rohkonflikt (zwei abweichende gueltige Bloecke derselben Figur) haette "
        f"NICHT als erfolgreicher Abschnitt veroeffentlicht werden duerfen ({outcome.completion.reason!r})."
    )
    assert "konflikt" in (outcome.completion.reason or "").casefold(), (
        f"der Haltegrund sollte den Rohkonflikt benennen, war: {outcome.completion.reason!r}."
    )
    final = store._completion_final_path(env.run_dir, section_id)
    assert not final.exists(), "ein gehaltener Konflikt darf KEIN __final.json schreiben."
    published = store.load_current_save(env.run_dir, leader_pk, ps_store, states_dir=states_dir)
    assert published is None, (
        "ein gehaltener Konflikt darf KEINEN current_save der Konfliktfigur veroeffentlichen, "
        f"fand aber: {published!r}."
    )


# ---------------------------------------------------------------------------
# Test 1 (Kern-Repro, gleiche save_id): ROT (ohne Detector -> stiller
# 'erster gewinnt', Abschnitt wird faelschlich veroeffentlicht) -> GRUEN
# (mit Detector -> gehalten). Zwei abweichende gueltige Bloecke derselben
# Figur mit GLEICHER save_id, Gast vollstaendig.
# ---------------------------------------------------------------------------
def test_same_save_id_conflict_red_publishes_green_holds():
    leader_cid, guest_cid = "chrono-leader-g1a", "chrono-guest-g1a"
    debrief = _conflict_debrief(
        leader_cid, guest_cid,
        leader_blocks=[("dup-save-id", 100.0), ("dup-save-id", 250.0)],
    )
    gm_contents = [
        "SL-Antwort auf Anker-Turn (Leader).",
        "SL-Antwort auf Import-Turn (Gast 1).",
        debrief,
    ]

    # --- ROT: ohne Detector reduziert 'erster gewinnt' auf Block 1 und
    # veroeffentlicht -- beweist den Bug.
    with tempfile.TemporaryDirectory() as td_red:
        lobby, table, ps_store, env = _build_table(Path(td_red), "t-g1a-red", leader_cid, guest_cids=[guest_cid])
        outcome_red, gm_red = _run_leader_guest_section(
            lobby, table, ps_store, env, gm_contents=list(gm_contents),
            guest_cids=[guest_cid], section_id="section-g1a-red", with_conflict_detector=False,
        )
        assert outcome_red.completion.success, (
            "ROT-Repro widerlegt: ohne Detector haette der stille 'erster gewinnt' den Abschnitt "
            f"veroeffentlichen muessen ({outcome_red.completion.reason!r})."
        )
        final_red = store._completion_final_path(env.run_dir, "section-g1a-red")
        assert final_red.exists(), "ROT-Pfad haette (fehlerhaft) __final.json schreiben muessen."
        pub_red = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert pub_red is not None and pub_red.get("save_id") == "dup-save-id", (
            "ROT-Pfad haette genau den ersten Block ('erster gewinnt') veroeffentlicht."
        )
        assert pub_red.get("characters", [{}])[0].get("wallet") == 100.0, (
            "ROT: der veroeffentlichte Block ist der erste (wallet=100.0), der zweite verschwand still."
        )

    # --- GRUEN: mit Detector wird der Konflikt VOR Pin/Veroeffentlichung
    # erkannt und der Abschnitt gehalten.
    with tempfile.TemporaryDirectory() as td_green:
        lobby, table, ps_store, env = _build_table(Path(td_green), "t-g1a-green", leader_cid, guest_cids=[guest_cid])
        outcome_green, gm_green = _run_leader_guest_section(
            lobby, table, ps_store, env, gm_contents=list(gm_contents),
            guest_cids=[guest_cid], section_id="section-g1a-green", with_conflict_detector=True,
        )
        _assert_held(outcome_green, env, "section-g1a-green", ps_store, env.states_dir)


# ---------------------------------------------------------------------------
# Test 2 (verschiedene save_id): zwei abweichende gueltige Bloecke derselben
# Figur mit VERSCHIEDENEN save_ids -> ebenfalls gehalten (der char_id-Zweig
# von find_duplicate_save_ids greift).
# ---------------------------------------------------------------------------
def test_different_save_id_same_figure_conflict_holds():
    leader_cid, guest_cid = "chrono-leader-g1b", "chrono-guest-g1b"
    debrief = _conflict_debrief(
        leader_cid, guest_cid,
        leader_blocks=[("save-v1", 100.0), ("save-v2", 250.0)],
    )
    gm_contents = [
        "SL-Antwort auf Anker-Turn (Leader).",
        "SL-Antwort auf Import-Turn (Gast 1).",
        debrief,
    ]
    with tempfile.TemporaryDirectory() as td:
        lobby, table, ps_store, env = _build_table(Path(td), "t-g1b", leader_cid, guest_cids=[guest_cid])
        outcome, gm = _run_leader_guest_section(
            lobby, table, ps_store, env, gm_contents=gm_contents,
            guest_cids=[guest_cid], section_id="section-g1b", with_conflict_detector=True,
        )
        _assert_held(outcome, env, "section-g1b", ps_store, env.states_dir)


# ---------------------------------------------------------------------------
# Test 3 (Gegenfall, identische Wiederholung): derselbe Block zweimal fuer
# dieselbe Figur -> KEIN Konflikt, normaler Abschluss, KEINE Doppel-
# verarbeitung (genau EIN geernteter Block je Figur, __final geschrieben).
# ---------------------------------------------------------------------------
def test_identical_repeat_is_not_a_conflict_and_completes():
    leader_cid, guest_cid = "chrono-leader-g1c", "chrono-guest-g1c"
    # Zweimal exakt derselbe Block (gleiche save_id, gleicher Inhalt).
    debrief = _conflict_debrief(
        leader_cid, guest_cid,
        leader_blocks=[("same-save", 180.0), ("same-save", 180.0)],
    )
    gm_contents = [
        "SL-Antwort auf Anker-Turn (Leader).",
        "SL-Antwort auf Import-Turn (Gast 1).",
        debrief,
    ]
    with tempfile.TemporaryDirectory() as td:
        lobby, table, ps_store, env = _build_table(Path(td), "t-g1c", leader_cid, guest_cids=[guest_cid])
        outcome, gm = _run_leader_guest_section(
            lobby, table, ps_store, env, gm_contents=gm_contents,
            guest_cids=[guest_cid], section_id="section-g1c", with_conflict_detector=True,
        )
        assert outcome.completion.success, (
            "eine IDENTISCHE Wiederholung desselben Blocks ist KEIN Konflikt und haette "
            f"normal abschliessen muessen ({outcome.completion.reason!r})."
        )
        assert set(outcome.completion.members_completed) == {"leader_pk", "guest1_pk"}
        assert set(outcome.harvested.keys()) == {"leader_pk", "guest1_pk"}, (
            "genau EIN geernteter Block je Figur -- keine Doppelverarbeitung der Wiederholung."
        )
        final = store._completion_final_path(env.run_dir, "section-g1c")
        assert final.exists(), "der Gegenfall (identische Wiederholung) haette __final.json schreiben muessen."
        published = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert published is not None and published.get("save_id") == "same-save"
        assert published.get("characters", [{}])[0].get("wallet") == 180.0


# ---------------------------------------------------------------------------
# Test 4 (Detector-Unit, direkt): der aus policy.build_harvest_conflict_
# detector gebaute Detektor meldet Konflikte je Figur und schweigt bei
# identischer Wiederholung / Einzelblock / fremder Figur.
# ---------------------------------------------------------------------------
def test_conflict_detector_unit_semantics():
    detect = build_harvest_conflict_detector()
    leader_cid, guest_cid = "chrono-u-leader", "chrono-u-guest"
    cid_to_pk = {leader_cid: "leader_pk", guest_cid: "guest1_pk"}

    # (a) zwei abweichende Bloecke derselben Figur -> Konflikt gemeldet.
    conflict_text = "\n".join([
        full_v7_block_text(leader_cid, save_id="a", wallet=10.0),
        full_v7_block_text(leader_cid, save_id="b", wallet=20.0),
        full_v7_block_text(guest_cid, wallet=0.0),
    ])
    msgs = detect(conflict_text, cid_to_pk)
    assert msgs and any(leader_cid in m for m in msgs), f"Konflikt der Leaderfigur sollte gemeldet sein: {msgs!r}"
    assert not any(guest_cid in m for m in msgs), f"die saubere Gastfigur darf KEINEN Konflikt melden: {msgs!r}"

    # (b) identische Wiederholung -> KEIN Konflikt.
    identical_text = "\n".join([
        full_v7_block_text(leader_cid, save_id="x", wallet=50.0),
        full_v7_block_text(leader_cid, save_id="x", wallet=50.0),
    ])
    assert detect(identical_text, cid_to_pk) == [], "identische Wiederholung ist kein Konflikt."

    # (c) Einzelblock + fremde Figur -> KEIN Konflikt.
    single_text = full_v7_block_text(leader_cid, wallet=5.0) + "\n" + full_v7_block_text("chrono-stranger", wallet=7.0)
    assert detect(single_text, cid_to_pk) == [], "ein einzelner Block je Figur ist kein Konflikt."

    # (d) leerer Text -> KEIN Konflikt.
    assert detect("", cid_to_pk) == []


def main() -> int:
    tests = [
        test_same_save_id_conflict_red_publishes_green_holds,
        test_different_save_id_same_figure_conflict_holds,
        test_identical_repeat_is_not_a_conflict_and_completes,
        test_conflict_detector_unit_semantics,
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
