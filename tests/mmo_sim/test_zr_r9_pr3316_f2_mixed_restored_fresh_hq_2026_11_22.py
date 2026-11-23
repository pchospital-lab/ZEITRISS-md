#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_f2_mixed_restored_fresh_hq_2026_11_22.py —
ZR-R9-PR3316-PREMERGE-NACHZUG-20261122, Stage-2.5-Nachrunde (Critic-Fund,
GROUP-REVIEW.md F2 war unvollstaendig): `core/save_correction.py:pursue_
group_save_correction`s EINZIGER restored-HQ-Re-Check steht unter `if not
candidates:` (Zeile ~2609-2625) -- im GEMISCHTEN Fall (ein Mitglied via
Zeile ~2563 `restored_from_adopted` aus einem fruehren, gecrashten Prozess
zurueckgespielt (`STATE_ADOPTED` + `adopted_block`, W53-SS7-Mechanik) UND
ein ANDERES Mitglied mit einem FRISCHEN Kandidaten in `candidates`) ist
`candidates` NICHT leer -- der restored-HQ-Check wird dadurch komplett
UEBERSPRUNGEN, waehrend der Per-Kandidat-`require_hq`-Check (~Zeile 3016)
NUR den jeweils FRISCHEN Block prueft, nie das zurueckgespielte
`harvested[pk]`. Der finale `store.complete_section`-Aufruf (Zeile ~3077)
veroeffentlicht `harvested` dadurch OHNE jeden HQ-Guard fuer den restored-
Block -- ein nie geprueftes Nicht-HQ-Mitglied wird gepinnt+publiziert
trotz `require_hq=True` (reales W53-SS7-Crash-Fenster, terminaler
Speicherverlust).

Fix (Stage 2.5): ein zusaetzlicher `_hq_violation_hold_reason()`-Aufruf
AM ENDE jedes while-Rumpfdurchlaufs, VOR `_clear_open_round` (nicht
danach!) -- byte-strukturgleich zu Zeile ~2615-2625 (`save_correction_
hold` emittieren, `harvest_completion = store.CompletionResult(success=
False, already_completed=False, written=False, members_completed=[],
missing=[], reason=hq_violation)`, `break`). Platzierung VOR dem Marker-
Clear ist Pflicht: der Open-Round-Marker (inkl. F1-`expected_prev_ref_by_
member`-Bindung) bleibt bei HOLD erhalten, ein spaeterer Resume laeuft
ueber den bestehenden restored-Zweig idempotent erneut -- Clearen VOR dem
HOLD wuerde Bindung + Marker verwerfen und einen erneuten (falschen) GM-
Versand fuer ein bereits beantwortetes Mitglied riskieren (s. Testfall 2).

Drei Faelle (Briefing, Linus Stage 2.5):
  1. KERN (rot-vor/gruen-nach manuell via Fix-Hunk-Deaktivierung belegt,
     s. Worker-Report): Tisch mit Leader (HQ, bereits vollstaendig) +
     Mitglied Marek `STATE_ADOPTED` mit einem NICHT-HQ `adopted_block`
     (`continuity.last_seen.mode="core"`, zurueckgespielt aus einer
     frueheren gecrashten Runde) + Mitglied Dronov mit einem FRISCHEN,
     tatsaechlich HQ-gueltigen Kandidaten, `require_hq=True`. Erwartung MIT
     Fix: `completion.success is False`, `reason` nennt Marek + den
     Nicht-HQ-Grund, KEIN Plan/keine Publikation.
  2. RESUME-IDEMPOTENZ: nach dem HOLD aus (1) ein zweiter, unabhaengiger
     Aufruf mit frisch via `store.complete_section` ermittelter
     `harvest_completion` (nichts wurde je publiziert) und einem
     Transport, der bei JEDEM Call wirft -- belegt, dass der Dronov-
     Rundenmarker (NICHT geloescht, weil der Fix VOR `_clear_open_round`
     haelt) einen zweiten echten Versand verhindert UND das Ergebnis
     erneut (idempotent) HOLDet, ohne Marek jemals zu publizieren.
  3. KEIN FALSCHES HOLD: derselbe gemischte Aufbau, aber Mareks
     zurueckgespielter Block IST HQ-gueltig (`mode="hq"`) + Dronovs
     frischer Kandidat ist ebenfalls HQ -- `completion.success is True`,
     beide werden veroeffentlicht (der Fix ist reine Vorab-Pruefung ohne
     Schreibzugriff, kein falsches Halten bereits gueltiger Mitglieder).

Echter Drei-Mitglieder-Caller (`pursue_group_save_correction` ist die reale
Produktfunktion, identisches Testmuster zu `test_zr_r9_pr3316_f2_pre_send_
hq_requeued_guest_2026_11_22.py`/`test_w49_group_round_restart_2026_10_08.
py`) -- KEIN internes Monkeypatchen der Regel, nur echte Record-/Marker-
Zustaende ueber die oeffentlichen `save_correction`-Funktionen praepariert.

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


class _ExplodingGm:
    """Wirft bei JEDEM Call -- belegt, dass KEIN zweiter realer SL-Turn
    fuer ein bereits (ueber den Marker) durabel beantwortetes Mitglied
    ausgeloest wird (identisches Muster zu `test_w49_group_round_restart_
    2026_10_08.py`)."""

    def turn(self, *a, **k):
        raise AssertionError("Resume: kein zusaetzlicher realer SL-Turn fuer eine bereits offene/beantwortete Runde.")


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


def _preadopt_marek(run_dir: Path, table, section_id: str, adopted_block: dict) -> str:
    """Simuliert GENAU die W53-SS7-Vorbedingung (s. Modulkommentar in
    `pursue_group_save_correction`): eine FRUEHERE, dann gecrashte
    Prozessinstanz hat Mareks Antwort bereits via `begin_attempt` +
    `mark_adopted` akzeptiert, ist aber VOR dem naechsten `store.complete_
    section`-Aufruf abgestuerzt -- der Datensatz bleibt `STATE_ADOPTED`
    mit `adopted_block` gesetzt, OHNE dass je publiziert wurde."""
    repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-marek")
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key="marek_pk", char_id="chrono-marek",
        operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
    )
    save_correction.begin_attempt(run_dir, repair_key)
    save_correction.mark_adopted(run_dir, repair_key, adopted_block=adopted_block)
    return repair_key


# ---------------------------------------------------------------------------
# Fall 1 -- KERN: restored Nicht-HQ (Marek) + frischer HQ-Kandidat (Dronov),
# require_hq=True -> HOLD, kein Publish (rot-vor/gruen-nach manuell belegt,
# s. Worker-Report).
# ---------------------------------------------------------------------------

def test_f2_mixed_core_restored_nonhq_plus_fresh_hq_holds_no_publish():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-mixed-core"
        lobby, table, ps_store, harvested, harvest_completion = _setup_leader_hq_two_guests_missing(
            run_dir, states_dir, "t-mixed-core", section_id,
        )

        marek_non_hq = _non_hq_block("chrono-marek", "Marek", mode="core")
        _preadopt_marek(run_dir, table, section_id, marek_non_hq)

        dronov_hq = _hq_block("chrono-dronov", "Dronov")
        gm = _CountingGm([f"```json\n{json.dumps(dronov_hq)}\n```"])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=True,
        )
        assert len(gm.calls) == 1, (
            f"genau EIN Transport-Call fuer den frischen Kandidaten (Dronov) -- Marek wird NICHT erneut "
            f"angefragt (restored) -- {gm.calls}"
        )

        # DAS ist der belegte Bug/Fix-Gegenstand: OHNE den Stage-2.5-Fix
        # wuerde dieser gemischte Fall `completion_after.success is True`
        # liefern UND Mareks Nicht-HQ-Block mitpublizieren (candidates ist
        # wegen Dronov NICHT leer, der einzige Alt-Check unter `if not
        # candidates:` greift dann nicht).
        assert completion_after.success is False, completion_after
        assert completion_after.written is False
        assert completion_after.missing == []
        assert completion_after.reason is not None and "marek_pk" in completion_after.reason and "core" in completion_after.reason, (
            completion_after.reason
        )
        assert harvested_after["marek_pk"] == marek_non_hq, "restored bleibt sichtbar, wird aber NICHT publiziert."

        plan_path = store._completion_plan_path(run_dir, section_id)
        assert not plan_path.exists(), (
            "Der gemischte Fall darf den nie HQ-geprueften restored-Block NICHT publizieren (F2-Luecke)."
        )
        published_marek = store.load_current_save(run_dir, "marek_pk", ps_store, states_dir=states_dir)
        assert published_marek is None, "Mareks Nicht-HQ-Stand darf NIE veroeffentlicht werden."

        marker_path = save_correction._open_round_path(run_dir, table.table_id, section_id)
        assert marker_path.exists(), (
            "Marker/F1-expected_prev_ref_by_member-Bindung muessen beim HOLD erhalten bleiben "
            "(Platzierung VOR _clear_open_round ist Pflicht -- s. Testfall 2)."
        )

        dronov_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-dronov")
        dronov_record = save_correction.load_record(run_dir, dronov_repair_key)
        assert dronov_record["state"] == save_correction.STATE_ADOPTED and dronov_record["attempts_used"] == 1


# ---------------------------------------------------------------------------
# Fall 2 -- RESUME-IDEMPOTENZ: nach dem HOLD aus Fall 1 ein zweiter,
# unabhaengiger Aufruf -- der (wegen der Fix-Platzierung VOR
# `_clear_open_round`) ueberlebende Dronov-Rundenmarker verhindert einen
# zweiten realen Versand; das Ergebnis bleibt idempotent HOLD, nichts wird
# publiziert.
# ---------------------------------------------------------------------------

def test_f2_mixed_core_resume_after_hold_is_idempotent_no_resend_no_publish():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-mixed-resume"
        lobby, table, ps_store, harvested, harvest_completion = _setup_leader_hq_two_guests_missing(
            run_dir, states_dir, "t-mixed-resume", section_id,
        )

        marek_non_hq = _non_hq_block("chrono-marek", "Marek", mode="core")
        _preadopt_marek(run_dir, table, section_id, marek_non_hq)

        dronov_hq = _hq_block("chrono-dronov", "Dronov")
        gm1 = _CountingGm([f"```json\n{json.dumps(dronov_hq)}\n```"])

        harvested_after1, completion_after1 = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm1,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=True,
        )
        assert completion_after1.success is False, completion_after1
        marker_path = save_correction._open_round_path(run_dir, table.table_id, section_id)
        assert marker_path.exists(), "Vorbedingung fuer diesen Testfall: der Marker muss den ersten HOLD ueberleben."

        dronov_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-dronov")
        dronov_record_before = save_correction.load_record(run_dir, dronov_repair_key)
        assert dronov_record_before["state"] == save_correction.STATE_ADOPTED
        assert dronov_record_before["attempts_used"] == 1

        # "Neustart": ein frischer `harvest_completion`-Blick -- nichts
        # wurde je publiziert, BEIDE Mitglieder gelten weiterhin als
        # fehlend (identisches Resume-Muster zu den W49-Tests). Ein
        # Transport, der bei JEDEM Call wirft, belegt, dass KEIN zweiter
        # Versand fuer Dronov (bereits durabel beantwortet) erfolgt.
        harvest_completion_resume = store.complete_section(
            lobby, table, section_id, dict(harvested), states_dir, "2026-11-22",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion_resume.success
        assert set(harvest_completion_resume.missing) == {"marek_pk", "dronov_pk"}

        harvested_after2, completion_after2 = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion_resume, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=True,
        )

        assert completion_after2.success is False, completion_after2
        assert completion_after2.written is False
        assert completion_after2.reason is not None and "marek_pk" in completion_after2.reason, completion_after2.reason

        plan_path = store._completion_plan_path(run_dir, section_id)
        assert not plan_path.exists(), "Resume darf den Nicht-HQ-restored-Block ebenfalls NIE publizieren."
        published_marek = store.load_current_save(run_dir, "marek_pk", ps_store, states_dir=states_dir)
        assert published_marek is None

        dronov_record_after = save_correction.load_record(run_dir, dronov_repair_key)
        assert dronov_record_after["attempts_used"] == 1, (
            "kein erneuter Versand/Budgetverbrauch fuer Dronov beim Resume -- "
            f"{dronov_record_after['attempts_used']}"
        )


# ---------------------------------------------------------------------------
# Fall 3 -- KEIN FALSCHES HOLD: restored-Block IST HQ + frischer Kandidat
# ist HQ -> Erfolg, beide werden veroeffentlicht (reine Vorab-Pruefung,
# kein Schreibzugriff, kein falsches Halten bereits gueltiger Mitglieder).
# ---------------------------------------------------------------------------

def test_f2_mixed_core_restored_hq_plus_fresh_hq_succeeds_both_published():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-mixed-noholds"
        lobby, table, ps_store, harvested, harvest_completion = _setup_leader_hq_two_guests_missing(
            run_dir, states_dir, "t-mixed-noholds", section_id,
        )

        marek_hq = _hq_block("chrono-marek", "Marek")
        _preadopt_marek(run_dir, table, section_id, marek_hq)

        dronov_hq = _hq_block("chrono-dronov", "Dronov")
        gm = _CountingGm([f"```json\n{json.dumps(dronov_hq)}\n```"])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            require_hq=True,
        )
        assert len(gm.calls) == 1, gm.calls

        assert completion_after.success is True, completion_after.reason
        assert harvested_after["marek_pk"] == marek_hq
        assert harvested_after["dronov_pk"] == dronov_hq

        plan_path = store._completion_plan_path(run_dir, section_id)
        assert plan_path.exists(), "beide HQ-gueltigen Bloecke muessen gepinnt/veroeffentlicht werden."
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert set(plan_data["members"].keys()) == set(_MEMBERS)

        published_marek = store.load_current_save(run_dir, "marek_pk", ps_store, states_dir=states_dir)
        published_dronov = store.load_current_save(run_dir, "dronov_pk", ps_store, states_dir=states_dir)
        assert published_marek == marek_hq
        assert published_dronov == dronov_hq

        assert not save_correction._open_round_path(run_dir, table.table_id, section_id).exists()


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
