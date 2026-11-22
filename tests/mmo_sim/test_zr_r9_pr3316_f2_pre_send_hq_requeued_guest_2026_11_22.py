#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_f2_pre_send_hq_requeued_guest_2026_11_22.py —
ZR-R9-PR3316-PREMERGE-NACHZUG-20261122, Befund F2 (GROUP-REVIEW.md §F2,
01_REVIEW.txt Abschnitt 3): `core/runtime.py:_candidate_hq_hold_reason`
prüft nur Mitglieder, für die beim aktiven PRE-SEND-Erstcheck bereits ein
Content-/Cache-Block vorliegt -- ein zu diesem Zeitpunkt noch GANZ
fehlender Gast wird bewusst übersprungen (Sache von `missing`). Der neue
aktive PRE-SEND-Zweig (`pre_send_active_leader_authority`, `runtime.py:
~1039-1052`) macht `save_correction.pursue_group_save_correction` danach
für GENAU diesen fehlenden Gast erreichbar -- sein später nachgeforderter
Block durchlief bisher NIE erneut die HQ-Prüfung und konnte mit
`continuity.last_seen.mode="core"` (oder jedem anderen Nicht-HQ-Modus)
adoptiert und veröffentlicht werden (belegt durch
`repro_non_hq_correction.py` im Supportpaket).

Nachzug: `mmo_sim/domain/zeitriss/save_correction.py:hq_mode_hold_reason`
(additive reine Domänenfunktion, identische Regel wie `_candidate_hq_
hold_reason`) + `core/save_correction.py:pursue_group_save_correction`s
neuer additiver `require_hq`-Parameter (Default `False`, jeder bestehende
Aufrufer bleibt bytegleich) -- geprüft wird jeder spät nachgeforderte/
best-effort-übernommene/wiederhergestellte Block VOR Plan/Publish; Nicht-
HQ bleibt retry-fähig (verbleibendes Budget) statt den ganzen Abschluss
sofort zu verhindern. `core/runtime.py`s PRE-SEND-Zweig setzt `require_hq=
True` NUR für diesen aktiven Übergang -- der normale `not pre_send`-
Nachforderweg bleibt unverändert ohne diese Regel (keine Mode-Umschreibung,
kein Entfernen von `and not pre_send`, kein pauschales Belegen des
neutralen Store mit einer neuen Spielregel).

Echter Leader-plus-zwei-Gäste-Caller (`pursue_group_save_correction` ist
die reale Produktfunktion, identisches Testmuster zu bereits bestehendem
`test_w49_group_round_restart_2026_10_08.py`/`test_w49c_partial_adoption_
mid_round_resumes_both_members_without_resend` -- EINE Korrekturnachricht
liefert zwei Mitgliederantworten in einer Message, exakt wie beim echten
Gruppenkorrektur-Versand).

  F2-rot  -- `require_hq=False` (der Zustand JEDES Aufrufers VOR diesem
             Nachzug, inkl. des PRE-SEND-Zweigs, der den Parameter noch
             nicht kannte): ein spät nachgeforderter Nicht-HQ-Gast
             (mode="core") wird adoptiert UND der Abschluss wird
             veröffentlicht -- GENAU der belegte Bug.
  F2-grün -- `require_hq=True` (neuer PRE-SEND-Zweig): derselbe Nicht-HQ-
             Gast wird NICHT adoptiert, kein Plan/keine Veröffentlichung;
             eine SPÄTERE, tatsächlich am HQ gespeicherte Korrektur
             desselben Gasts wird regulär angenommen (Retry-Fähigkeit,
             kein künstlicher terminaler Hold).

Zusätzlich: Negativfälle core/rift/chronopolis sowie fehlender/falsch
getypter HQ-Marker direkt gegen die neue Domänenfunktion (Drei-Mitglieder-
Test ist hier Pflicht nachzuziehen, s. Befund).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)

_MEMBERS = ("leader_pk", "marek_pk", "dronov_pk")
_CHAR_IDS = {"leader_pk": "chrono-leader", "marek_pk": "chrono-marek", "dronov_pk": "chrono-dronov"}
_CID_TO_PK = {v: k for k, v in _CHAR_IDS.items()}


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_three_member_table(run_dir: Path, states_dir: Path, table_id: str) -> tuple:
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    for pk in _MEMBERS:
        _seed_persona_state(ps_store, states_dir, pk, _CHAR_IDS[pk])
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for pk in _MEMBERS:
        lobby.join(pk)
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["marek_pk", "dronov_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "marek_pk", "accept": True},
            {"type": "consent", "offer_id": "o1", "from": "dronov_pk", "accept": True},
        ],
        chrononaut_ids=dict(_CHAR_IDS),
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


def _hq_block(char_id: str, name: str) -> dict:
    block = full_v7_save(char_id, name=name)
    block["continuity"]["last_seen"]["mode"] = "hq"
    return block


def _non_hq_block(char_id: str, name: str, mode: str = "core") -> dict:
    block = full_v7_save(char_id, name=name)
    block["continuity"]["last_seen"]["mode"] = mode
    return block


class _CountingGm:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"_CountingGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _setup_leader_hq_two_guests_missing(run_dir: Path, states_dir: Path, table_id: str, section_id: str):
    lobby, table, ps_store = _build_three_member_table(run_dir, states_dir, table_id)
    leader_valid = _hq_block("chrono-leader", "Leader")
    harvested = {"leader_pk": leader_valid}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, states_dir, "2026-11-22", ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and set(harvest_completion.missing) == {"marek_pk", "dronov_pk"}, (
        harvest_completion
    )
    return lobby, table, ps_store, harvested, harvest_completion


# ---------------------------------------------------------------------------
# F2-rot -- require_hq=False (jeder Aufrufer VOR diesem Nachzug): ein spaet
# nachgeforderter Nicht-HQ-Gast wird adoptiert UND veroeffentlicht.
# ---------------------------------------------------------------------------

def test_f2_rot_without_require_hq_adopts_non_hq_guest_and_publishes():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-f2-rot"
        lobby, table, ps_store, harvested, harvest_completion = _setup_leader_hq_two_guests_missing(
            run_dir, states_dir, "t-f2-rot", section_id,
        )

        marek_valid = _hq_block("chrono-marek", "Marek")
        dronov_non_hq = _non_hq_block("chrono-dronov", "Dronov", mode="core")
        gm = _CountingGm([
            f"```json\n{json.dumps(marek_valid)}\n```\n```json\n{json.dumps(dronov_non_hq)}\n```",
        ])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=False,  # der alte, ungeschuetzte Zustand.
        )
        assert len(gm.calls) == 1, gm.calls

        # DAS ist der belegte Bug: der Nicht-HQ-Gast wird OHNE jede erneute
        # HQ-Pruefung adoptiert, der Abschluss gelingt und veroeffentlicht.
        assert completion_after.success, completion_after.reason
        assert harvested_after["dronov_pk"]["continuity"]["last_seen"]["mode"] == "core"
        plan_path = store._completion_plan_path(run_dir, section_id)
        assert plan_path.exists(), "ohne die F2-Pruefung wird der Plan trotz Nicht-HQ-Gast gepinnt."


# ---------------------------------------------------------------------------
# F2-gruen -- require_hq=True (neuer PRE-SEND-Zweig): der Nicht-HQ-Gast
# wird NICHT adoptiert, kein Plan/keine Veroeffentlichung; eine spaetere
# tatsaechlich am HQ gespeicherte Korrektur wird regulaer angenommen.
# ---------------------------------------------------------------------------

def test_f2_gruen_with_require_hq_rejects_non_hq_guest_then_accepts_later_hq_correction():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-f2-gruen"
        lobby, table, ps_store, harvested, harvest_completion = _setup_leader_hq_two_guests_missing(
            run_dir, states_dir, "t-f2-gruen", section_id,
        )

        # EIN Aufruf -- `pursue_group_save_correction`s eigene while-Schleife
        # fragt intern so lange weitere Runden nach, wie Budget bleibt und
        # Mitglieder fehlen (01_AUFTRAG_SAVEGATE.md §B); Runde 1 liefert
        # Marek (HQ) + Dronov (Nicht-HQ) in EINER Nachricht, Runde 2 liefert
        # Dronovs tatsaechlich am HQ gespeicherte Korrektur.
        marek_valid = _hq_block("chrono-marek", "Marek")
        dronov_non_hq = _non_hq_block("chrono-dronov", "Dronov", mode="core")
        dronov_hq = _hq_block("chrono-dronov", "Dronov")
        gm = _CountingGm([
            f"```json\n{json.dumps(marek_valid)}\n```\n```json\n{json.dumps(dronov_non_hq)}\n```",
            f"```json\n{json.dumps(dronov_hq)}\n```",
        ])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=True,
        )
        assert len(gm.calls) == 2, (
            f"genau ZWEI Runden -- Runde 1 (Dronov Nicht-HQ, retry-faehig) + Runde 2 (Dronov HQ) -- {gm.calls}"
        )

        # Erfolg erst NACH der tatsaechlich gueltigen HQ-Korrektur; der
        # final uebernommene Dronov-Block ist der HQ-Stand, NICHT der
        # zwischenzeitlich abgelehnte Nicht-HQ-Versuch.
        assert completion_after.success, completion_after.reason
        assert harvested_after["marek_pk"]["continuity"]["last_seen"]["mode"] == "hq"
        assert harvested_after["dronov_pk"]["continuity"]["last_seen"]["mode"] == "hq"
        assert harvested_after["dronov_pk"] == dronov_hq

        dronov_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-dronov")
        dronov_record = save_correction.load_record(run_dir, dronov_repair_key)
        assert dronov_record["attempts_used"] == 2, (
            "BEIDE Versuche (Nicht-HQ Runde 1 + HQ Runde 2) muessen das Budget verbrauchen, "
            f"kein Doppelzaehlen/kein Ueberspringen -- {dronov_record['attempts_used']}"
        )

        plan_path = store._completion_plan_path(run_dir, section_id)
        assert plan_path.exists(), "nach der gueltigen HQ-Korrektur muss der Plan gepinnt sein."
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert set(plan_data["members"].keys()) == set(_MEMBERS)

        # DAS ist der eigentliche Beleg: der tatsaechlich veroeffentlichte
        # Dronov-Stand ist der HQ-Block -- der Nicht-HQ-Versuch aus Runde 1
        # wurde zu KEINEM Zeitpunkt veroeffentlicht.
        published_dronov = store.load_current_save(run_dir, "dronov_pk", ps_store, states_dir=states_dir)
        assert published_dronov == dronov_hq, (
            "der zwischenzeitlich abgelehnte Nicht-HQ-Versuch wurde veroeffentlicht -- "
            f"genau der F2-Bruch: {published_dronov}"
        )


# ---------------------------------------------------------------------------
# Negativfaelle core/rift/chronopolis sowie fehlender/falsch getypter
# HQ-Marker -- direkt gegen die neue Domaenenfunktion (Drei-Mitglieder-
# Kontext bleibt oben abgedeckt; hier die vollstaendige Modusmatrix).
# ---------------------------------------------------------------------------

def test_f2_hq_mode_hold_reason_matrix():
    for mode in ("core", "rift", "chronopolis", "arena", "briefing", "debrief"):
        block = _non_hq_block("chrono-marek", "Marek", mode=mode)
        reason = save_correction_domain.hq_mode_hold_reason("marek_pk", block)
        assert reason is not None and "marek_pk" in reason and mode in reason, (mode, reason)

    block_missing_mode = full_v7_save("chrono-marek", name="Marek")
    block_missing_mode["continuity"]["last_seen"].pop("mode", None)
    reason = save_correction_domain.hq_mode_hold_reason("marek_pk", block_missing_mode)
    assert reason is not None, "fehlendes mode-Feld gilt bewusst NICHT als HQ."

    block_malformed = full_v7_save("chrono-marek", name="Marek")
    block_malformed["continuity"]["last_seen"] = None
    reason = save_correction_domain.hq_mode_hold_reason("marek_pk", block_malformed)
    assert reason is not None, "null last_seen haelt kontrolliert, kein AttributeError."

    hq = _hq_block("chrono-marek", "Marek")
    assert save_correction_domain.hq_mode_hold_reason("marek_pk", hq) is None

    assert save_correction_domain.hq_mode_hold_reason("marek_pk", None) is None, (
        "ein fehlender Block ist Sache von complete_section's missing-Zweig, nicht dieser Funktion."
    )


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
