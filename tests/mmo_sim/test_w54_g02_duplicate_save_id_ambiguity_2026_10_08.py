#!/usr/bin/env python3
"""
tests/mmo_sim/test_w54_g02_duplicate_save_id_ambiguity_2026_10_08.py --
R12-Savegate, W54-Slice, G02 (FINDINGS.json/01_ENTSCHEIDUNG_UND_REPARATUR.md
§W54 G02, SC06).

Befund (General, GENERALREVIEW.md §4, eigene Gegenprobe am echten
Erschaffungsdienst): eine Antwort enthielt zwei einzeln vollschema-gueltige
Saves derselben Figur und derselben `save_id`, aber mit abweichendem Inhalt
(Level 1 vs. 2). `saves.extract_all_saves` deduplizierte NACH `save_id` --
der Dienst meldete `completed` und uebernahm GENAU DEN ERSTEN Block, OHNE
dass der Konflikt je sichtbar wurde. Der bereits vorhandene Detector
(`save_validation.find_duplicate_save_ids`) erkannte den Konflikt zwar,
wenn man ihm die rohen Bloecke direkt gab, war aber NICHT vor die
verlustbehaftete Auswahl verdrahtet (nur im Test aufgerufen, s.
`test_w43_save_validation_acceptance_gate_2026_10_07.py`s
`test_sc06_duplicate_save_id_conflict_not_hidden_by_first_wins`).

W54-Fix (`saves.py` NEU: `extract_all_saves_raw`; `save_validation.py` NEU:
`extract_checked_single`; `core/save_correction.py` + `core/
creation_service.py`): der Annahmepunkt sieht JETZT ALLE rohen,
undeduplizierten Kandidaten BEVOR irgendeine Auswahl getroffen wird --
`find_duplicate_save_ids` wird REAL auf diese Rohkandidaten angewendet.
Ein echter Konflikt (gleiche char_id/save_id, ABWEICHENDER Inhalt) wird
NIE als einer der beteiligten Bloecke uebernommen; stattdessen laeuft
derselbe budget-/request-gebundene Korrekturpfad wie bei einem
gewoehnlichen Schemafehler an, mit einer expliziten Mehrdeutigkeitsmeldung
an die SL. Identische Wiederholungen bleiben deterministisch (kein
Fehlalarm); unterschiedliche Personen/char_ids im selben Text bleiben
unberuehrt (Gruppen-Personen getrennt).

Abdeckung:
  W54-G02-A -- Erstantwort (Erschaffungsdialog): zwei Bloecke derselben
               char_id/save_id mit ABWEICHENDEM Inhalt werden NICHT
               uebernommen (weder der erste noch der zweite); eine
               eindeutige Korrekturantwort wird GENAU EINMAL uebernommen.
  W54-G02-B -- Korrekturantwort: derselbe Konflikt waehrend eines bereits
               laufenden Korrekturversuchs wird ebenso erkannt (keine
               Uebernahme, Budget verbraucht, naechste Runde eindeutig).
  W54-G02-C -- Identische Doppelausgabe (gleicher Inhalt zweifach) bleibt
               deterministisch GENAU EIN gueltiger Block -- kein
               Fehlalarm, kein Korrekturumweg.
  W54-G02-D -- Gruppenharvest: EIN Mitglied liefert konkurrierende
               Bloecke (Konflikt), ein ANDERES Mitglied liefert in
               DERSELBEN Antwort einen sauberen Block -- der Konflikt
               eines Mitglieds blockiert NICHT das andere (Gruppen-Personen
               getrennt); eine spaetere eindeutige Nachforderung schliesst
               den Abschnitt vollstaendig ab.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_w53_save_correction_adopted_replay_2026_10_08.py`. Kein Netz, kein
Livecall."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
import mmo_sim.domain.zeitriss.onboarding as onboarding  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402


def fenced(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def _no_persona_poll(*_a, **_k):
    raise AssertionError("W54-G02: kein Personapoll im menschlichen Erschaffungsdialog erwartet.")


class _ScriptedGm:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if not self._contents:
            raise AssertionError(f"W54-G02: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


# ---------------------------------------------------------------------------
# W54-G02-A -- Erstantwort mit zwei konkurrierenden Bloecken.
# ---------------------------------------------------------------------------

def test_w54g02a_conflicting_first_answer_is_never_silently_adopted():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        who = "testspieler_w54g02a"
        cid = "CHR-W54-G02A-01"

        block_lvl1 = full_v7_save(cid, name="Flo", level=1)
        block_lvl2 = full_v7_save(cid, name="Flo", level=2)
        assert block_lvl1["save_id"] == block_lvl2["save_id"], "beide Bloecke teilen dieselbe save_id (Default-Fixture)."
        assert block_lvl1 != block_lvl2
        resolved = full_v7_save(cid, name="Flo", level=5)

        onboarding.start_or_resume(onboarding_dir, who)
        gm = _ScriptedGm([fenced(block_lvl1) + "\n" + fenced(block_lvl2), fenced(resolved)])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=lambda _s: None,
        )

        assert len(gm.calls) == 2, "genau 1 Erstantwort + 1 Korrekturanfrage, kein Drittversand."
        assert outcome.status == "completed"
        assert outcome.save_block == resolved, (
            "SC06: weder block_lvl1 NOCH block_lvl2 duerfen uebernommen werden -- NUR die "
            "nachfolgende eindeutige Korrekturantwort."
        )
        state = onboarding.peek(onboarding_dir, who)
        assert state.final_save == resolved

        repair_key = save_correction_domain.creation_repair_key(who, cid)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "adopted" and record["attempts_used"] == 1
        assert record.get("adopted_block") == resolved


# ---------------------------------------------------------------------------
# W54-G02-B -- Konflikt waehrend einer bereits laufenden Korrekturantwort.
# ---------------------------------------------------------------------------

def test_w54g02b_conflicting_correction_answer_is_never_silently_adopted():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        who = "testspieler_w54g02b"
        cid = "CHR-W54-G02B-01"

        invalid = full_v7_save(cid, name="Flo")
        invalid["economy"] = {"wallets": {cid: 500}}  # schema-ungueltig -- loest Korrektur aus
        conflict_a = full_v7_save(cid, name="Flo", level=3)
        conflict_b = full_v7_save(cid, name="Flo", level=4)
        assert conflict_a["save_id"] == conflict_b["save_id"] and conflict_a != conflict_b
        resolved = full_v7_save(cid, name="Flo", level=1)
        resolved["economy"] = {"wallets": {cid: {"balance": 500}}}

        onboarding.start_or_resume(onboarding_dir, who)
        gm = _ScriptedGm([
            fenced(invalid),
            fenced(conflict_a) + "\n" + fenced(conflict_b),  # Korrekturantwort 1: mehrdeutig
            fenced(resolved),  # Korrekturantwort 2: eindeutig
        ])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=lambda _s: None,
        )

        assert len(gm.calls) == 3
        assert outcome.status == "completed"
        assert outcome.save_block == resolved, (
            "SC06: weder conflict_a NOCH conflict_b duerfen als Korrekturergebnis uebernommen werden."
        )

        repair_key = save_correction_domain.creation_repair_key(who, cid)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 2, "beide Korrekturversuche (mehrdeutig + eindeutig) zaehlen."
        assert record["state"] == "adopted" and record.get("adopted_block") == resolved


# ---------------------------------------------------------------------------
# W54-G02-C -- identische Doppelausgabe bleibt deterministisch, kein
# Fehlalarm.
# ---------------------------------------------------------------------------

def test_w54g02c_identical_repeated_block_is_not_a_false_conflict():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        who = "testspieler_w54g02c"
        cid = "CHR-W54-G02C-01"
        block = full_v7_save(cid, name="Flo")

        onboarding.start_or_resume(onboarding_dir, who)
        gm = _ScriptedGm([fenced(block) + "\n" + fenced(block)])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=lambda _s: None,
        )
        assert len(gm.calls) == 1, "kein Korrekturumweg fuer eine identische Doppelausgabe."
        assert outcome.status == "completed" and outcome.save_block == block


# ---------------------------------------------------------------------------
# W54-G02-D -- Gruppenharvest: ein Mitglied konfliktbehaftet, das andere
# Mitglied in DERSELBEN Antwort bleibt unberuehrt (Gruppen-Personen
# getrennt). Spaetere eindeutige Nachforderung schliesst den Abschnitt ab.
# ---------------------------------------------------------------------------

class _CountingGm:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"W54-G02-D: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _seed_persona_state(ps_store, states_dir, pk, char_id):
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _build_two_member_table(run_dir, states_dir):
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader-g02d")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest-g02d")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-w54g02d",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader-g02d", "guest_pk": "chrono-guest-g02d"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


_CID_TO_PK = {"chrono-leader-g02d": "leader_pk", "chrono-guest-g02d": "guest_pk"}


def test_w54g02d_group_harvest_conflict_for_one_member_does_not_block_the_other():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        leader_valid = full_v7_save("chrono-leader-g02d", name="Leader")
        guest_conflict_a = full_v7_save("chrono-guest-g02d", name="Flo", level=1)
        guest_conflict_b = full_v7_save("chrono-guest-g02d", name="Flo", level=2)
        assert guest_conflict_a["save_id"] == guest_conflict_b["save_id"] and guest_conflict_a != guest_conflict_b
        guest_resolved = full_v7_save("chrono-guest-g02d", name="Flo", level=9)

        harvested = {}
        harvest_completion = store.complete_section(
            lobby, table, "section-w54g02d", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success
        assert set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        # Runde 1: EINE Antwort fuer BEIDE -- Leader sauber, Guest mit
        # ABWEICHENDEM Doppelblock (Konflikt).
        round1_text = "\n".join([
            fenced(leader_valid), fenced(guest_conflict_a), fenced(guest_conflict_b),
        ])
        # Runde 2 (nur Guest noch offen): eindeutige Nachlieferung.
        round2_text = fenced(guest_resolved)
        gm = _CountingGm([round1_text, round2_text])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w54g02d", harvested=harvested,
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert len(gm.calls) == 2, f"genau 2 Gruppenrunden (Leader+Guest-Konflikt, dann Guest-Nachlieferung) -- {gm.calls}"
        assert completion_after.success, (
            f"nach der eindeutigen Guest-Nachlieferung MUSS der Abschnitt vollstaendig abschliessen -- {completion_after}"
        )
        assert harvested_after["leader_pk"] == leader_valid, "Leader (konfliktfrei) bleibt von Guests Konflikt unberuehrt."
        assert harvested_after["guest_pk"] == guest_resolved, (
            "SC06: weder guest_conflict_a NOCH guest_conflict_b duerfen uebernommen werden -- "
            "NUR die spaetere eindeutige Nachlieferung."
        )

        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w54g02d", "chrono-leader-g02d")
        guest_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w54g02d", "chrono-guest-g02d")
        leader_record = save_correction.load_record(run_dir, leader_repair_key)
        guest_record = save_correction.load_record(run_dir, guest_repair_key)
        assert leader_record["state"] == "adopted" and leader_record["attempts_used"] == 1
        assert guest_record["state"] == "adopted" and guest_record["attempts_used"] == 2
        assert guest_record.get("adopted_block") == guest_resolved


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
