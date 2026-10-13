#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_origin_finish_group_shape.py — R12-W76: F02 §B/R03
SHAPE-GROUP, echte Kontrollwerte VOR jedem Resume-Transport auch auf dem
Gruppenpfad pruefen (`mmo_sim/core/save_correction.py:pursue_group_save_
correction`).

Luecke (VOR diesem Fix): der Einzelfigurpfad prueft `attempts_used` eines
resumierten HOLD/WINDOW_PAUSED-Datensatzes VOR jedem Transport auf echten
`int` (kein `bool`) im gueltigen offenen Slotbereich 1..max_attempts (s.
`pursue_single_figure_correction`s `invalid_resume_slot_shape`-Zweig). Der
Gruppenpfad (`open_round is not None`-Resume-Zweig) prufte die betroffenen
Memberrecords bislang NUR auf Identitaet (Marker/Tisch/Abschnitt/Rolle/
char_id/persona_key), NICHT auf dieselbe `attempts_used`-Form -- ein
korrupter Wert (z.B. `bool` statt `int` durch eine nebenlaeufige/korrupte
Schreiboperation) erreichte unbemerkt den Resume-Transport.

Fix: dieselbe SHAPE-Probe wie der Einzelfigurpfad, ANGEWANDT auf ALLE
Memberrecords der offenen Runde, VOR `_window.slot_resumable`/jedem
Transport-Call. Verletzung -> ALLE Mitglieder der Runde `state="hold"`,
`reason="invalid_resume_slot_shape"`, Marker geloescht (dieselbe
Konsequenz wie `unresolved_prior_round_outcome`).

Abdeckung (CASES.json SHAPE-GROUP, mindestens zwei betroffene Figuren):
  (neg) EIN Mitglied mit `attempts_used=True` (bool) in einer offenen Runde
        mit ZWEI Mitgliedern -> BEIDE Mitglieder HOLD, Marker geloescht,
        KEIN Transport-Call.
  (pos) dieselbe offene Runde mit gueltigen `attempts_used`-Werten (echte
        `int`, 1..max_attempts) -> Resume wird NICHT durch die neue Probe
        blockiert, der Transport wird regulaer versucht (Regressionskontrolle
        -- Runden-ID (`round_no`) und pro-Figur-Zaehler bleiben dabei
        getrennt, s. Docstring `pursue_group_save_correction`).

Pure Python, nur `assert`, echter Exitcode -- gleiches Aufbaumuster wie
`test_w49_group_round_restart_2026_10_08.py`/`test_r12_provenance_close_
group_identity.py`."""
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
from _r12_window_hold_fixture import close_window, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_two_member_table(run_dir: Path, states_dir: Path):
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-r12-origin-finish-shape",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    def __init__(self):
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        raise AssertionError("kein Transport-Call erwartet -- SHAPE-Verletzung muss VOR jedem Versand HOLD halten.")


class _RecordingGm:
    """Zaehlt Aufrufe und liefert eine minimale, syntaktisch gueltige
    Antwort -- fuer die POSITIVE Kontrolle genuegt der Nachweis, dass der
    Transport ueberhaupt erreicht wird (die SHAPE-Probe blockiert NICHT),
    unabhaengig davon, ob die Antwort inhaltlich zu einem vollstaendigen
    Gruppenabschluss fuehrt."""

    def __init__(self, content: str = "keine gueltigen Speicherstaende in dieser Antwort."):
        self.calls = []
        self._content = content

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        return {"content": self._content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _open_round_with_both_members_window_paused(section_id: str):
    """Baut einen Zweier-Tisch, BEIDE Mitglieder mit ungueltigem Entwurf
    (beide `missing`), oeffnet (via echtem Deadline-Pre-Send-Block) Runde 1
    fuer BEIDE -- Marker + beide Memberrecords landen `window_paused`,
    `attempts_used=1` (echter `int`) fuer beide."""
    root = Path(tempfile.mkdtemp())
    run_dir, states_dir = root / "run", root / "states"
    lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

    leader_invalid = _wallet_as_number("chrono-leader")
    guest_invalid = _wallet_as_number("chrono-guest")
    harvested = {"leader_pk": leader_invalid, "guest_pk": guest_invalid}

    close_window(run_dir, deadline=1.0)
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, states_dir, "2026-10-10", ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
        harvest_completion
    )

    gm = _ExplodingGm()
    harvested_blocked, completion_blocked = save_correction.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert gm.calls == [], "Admission-Gate muss den Transport-Call verhindern, nicht nur nachtragen."
    assert not completion_blocked.success and set(completion_blocked.missing) == {"leader_pk", "guest_pk"}
    open_round_path = save_correction._open_round_path(run_dir, table.table_id, section_id)
    assert open_round_path.exists(), "Invariante 6: der Marker muss bei einem Deadline-Block ERHALTEN bleiben."

    for char_id in ("chrono-leader", "chrono-guest"):
        repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
        member_record = save_correction.load_record(run_dir, repair_key)
        assert member_record["state"] == "window_paused" and member_record["attempts_used"] == 1, member_record

    return root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path


# ---------------------------------------------------------------------------
# (neg) EIN korrupter Member-attempts_used (bool) -> BEIDE Mitglieder HOLD,
#       Marker geloescht, KEIN Transport-Call.
# ---------------------------------------------------------------------------

def test_neg_corrupted_member_attempts_shape_holds_whole_round_before_transport():
    """R12-W77 (F02-MARKER-Fix, 01_BINDUNGSERHALT.md §B, L06-GROUP-CONTROL):
    W76 erwartete hier faelschlich 'Marker geloescht, beide Mitglieder
    terminal hold' -- das widerspricht dem Vertrag (GENERALREVIEW.md §4):
    eine Ablehnung bei korrupter SHAPE MUSS die widerspruechliche Runde
    HALTEN statt sie zu zerstoeren. Vorher (W76): `_clear_open_round` +
    `mark_hold` je Mitglied liefen, der Marker verschwand, beide
    Memberrecords wurden auf state='hold' ueberschrieben. Nachher (W77):
    die Zahl-/SHAPE-Probe selbst bleibt (0 Calls, 0 neue Requests, kein
    Abschluss), ABER Marker/Memberrecords/round_no/attempts/Requesthistorie
    bleiben vollstaendig byte-/modegleich (PRE==POST) -- Wiederholung bleibt
    gleich, keine neue Runde, keine manuelle Reparatur des korrupten Werts."""
    section_id = "section-shape-neg"
    root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path = (
        _open_round_with_both_members_window_paused(section_id)
    )
    try:
        guest_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-guest")
        tampered = dict(save_correction.load_record(run_dir, guest_repair_key))
        tampered["attempts_used"] = True  # bool statt int -- genau die W74/W75-Gefahr, jetzt auch im Gruppenpfad.
        save_correction._write_record(run_dir, guest_repair_key, tampered)

        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-leader")
        round_counter_path = save_correction._round_counter_path(run_dir, table.table_id, section_id)
        # R12-W77 (PRE==POST-Beleg): volle Byte-/Modus-Momentaufnahme JEDER
        # betroffenen Datei VOR dem Ablehnungsaufruf -- Marker, beide
        # Memberrecords, Rundenzaehler, komplette Requesthistorie.
        pre_open_round_bytes = open_round_path.read_bytes()
        pre_open_round_mode = open_round_path.stat().st_mode
        pre_guest_bytes = (save_correction._record_path(run_dir, guest_repair_key)).read_bytes()
        pre_guest_mode = (save_correction._record_path(run_dir, guest_repair_key)).stat().st_mode
        pre_leader_bytes = (save_correction._record_path(run_dir, leader_repair_key)).read_bytes()
        pre_leader_mode = (save_correction._record_path(run_dir, leader_repair_key)).stat().st_mode
        pre_round_counter_bytes = round_counter_path.read_bytes() if round_counter_path.exists() else None
        pre_ledger_records = request_ledger._all_records(run_dir)

        open_window(run_dir)
        before_ledger = len(request_ledger._all_records(run_dir))
        gm = _ExplodingGm()
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert gm.calls == [], f"KEIN Transport-Call bei korrupter Member-SHAPE -- {gm.calls}"
        assert len(request_ledger._all_records(run_dir)) == before_ledger, "0 neue Requestdatensaetze."
        assert not completion_after.success and set(completion_after.missing) == {"leader_pk", "guest_pk"}
        assert open_round_path.exists(), (
            "R12-W77: der Marker MUSS nach der SHAPE-Ablehnung ERHALTEN bleiben (kein _clear_open_round) -- "
            "die widerspruechliche Runde wird gehalten, nicht geloescht."
        )

        # PRE==POST: vollstaendige Byte-/Modusidentitaet nach der Ablehnung.
        assert open_round_path.read_bytes() == pre_open_round_bytes, "Marker-Bytes unveraendert."
        assert open_round_path.stat().st_mode == pre_open_round_mode, "Marker-Modus unveraendert."
        assert save_correction._record_path(run_dir, guest_repair_key).read_bytes() == pre_guest_bytes, (
            "Member-Record (chrono-guest, korrumpiert) muss byte-identisch bleiben."
        )
        assert save_correction._record_path(run_dir, guest_repair_key).stat().st_mode == pre_guest_mode
        assert save_correction._record_path(run_dir, leader_repair_key).read_bytes() == pre_leader_bytes, (
            "Member-Record (chrono-leader, unveraendert) muss byte-identisch bleiben."
        )
        assert save_correction._record_path(run_dir, leader_repair_key).stat().st_mode == pre_leader_mode
        if pre_round_counter_bytes is not None:
            assert round_counter_path.read_bytes() == pre_round_counter_bytes, "round_no-Zaehler unveraendert."
        assert request_ledger._all_records(run_dir) == pre_ledger_records, "Requesthistorie vollstaendig unveraendert."

        for char_id in ("chrono-leader", "chrono-guest"):
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            record = save_correction.load_record(run_dir, repair_key)
            assert record["last_reason"] != "invalid_resume_slot_shape", (
                f"R12-W77: der Mitgliedsdatensatz darf durch die Ablehnung NICHT beschrieben werden "
                f"(kein Member-Write) -- {char_id}: {record}"
            )
        # Wiederholung bleibt gleich: ein zweiter Aufruf trifft erneut auf
        # dieselbe (weiterhin korrupte) SHAPE und haelt erneut identisch.
        gm2 = _ExplodingGm()
        harvested_after2, completion_after2 = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm2, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert gm2.calls == [], "Wiederholung bleibt gleich: wieder KEIN Transport-Call."
        assert open_round_path.exists(), "Wiederholung bleibt gleich: Marker weiterhin erhalten."
        assert not completion_after2.success and set(completion_after2.missing) == {"leader_pk", "guest_pk"}
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# (pos) gueltige Member-attempts_used (echter int, im Bereich) -> Resume
#       wird NICHT durch die neue Probe blockiert, Transport wird versucht.
# ---------------------------------------------------------------------------

def test_pos_valid_member_attempts_shape_does_not_block_resume_transport():
    section_id = "section-shape-pos"
    root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path = (
        _open_round_with_both_members_window_paused(section_id)
    )
    try:
        open_window(run_dir)
        gm = _RecordingGm()
        save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert len(gm.calls) >= 1, (
            f"mit gueltiger SHAPE MUSS der Resume-Transport regulaer versucht werden -- {gm.calls}"
        )
        assert gm.calls[0][0] == 1, (
            f"der ERSTE Resume-Call MUSS die bereits eroeffnete Runde 1 wiederverwenden (round_no), "
            f"NICHT eine neue Runde -- {gm.calls[0]}"
        )
        for char_id in ("chrono-leader", "chrono-guest"):
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            record = save_correction.load_record(run_dir, repair_key)
            assert record["last_reason"] != "invalid_resume_slot_shape", (
                f"die neue SHAPE-Probe darf einen gueltigen Wert NICHT ablehnen -- {char_id}: {record}"
            )
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)


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
