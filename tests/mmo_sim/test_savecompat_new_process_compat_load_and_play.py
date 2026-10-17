#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_new_process_compat_load_and_play.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`new_process_compat_load_and_play` (02_SAVEVERTRAG.md §D,
`core.save_compatibility.attempt_compat_load`).

Deckt: ein naechster Abschnitt laedt ueber den Kompat-Weg; die KI-SL
("Fake-SL" hier: eine injizierte `repair_fn`, kein echter Modellaufruf,
s. harte Grenzen) normalisiert/repariert VOR jeder abhaengigen
Spielaktion; bei Erfolg ATOMARER kanonischer Store-Commit (`store.
publish_current_save`, derselbe bestehende Schreibpfad); bounded (max. 3
Reparaturrunden); KEINE Doppel-`adopted`/Belohnung bei einem erneuten
Aufruf fuer denselben `repair_key` NACH bereits erfolgter Uebernahme
(Neustart-/Resume-Sicherheit); ein unlösbarer Fall endet in `hold`, App
bleibt benutzbar (kein Endlos-Karussell)."""
from __future__ import annotations

import copy
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

import mmo_sim.core.save_compatibility as save_compat_core  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],"properties":{"v":{"const":2}}}'
)


def _new_env(root: Path):
    run_dir, states_dir = root / "run", root / "states"
    states_dir.mkdir(parents=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    return run_dir, states_dir, PersonaStateStore(schema_path=schema_path, default_states_dir=None)


if __name__ == "__main__":
    CHAR_ID = "chrono-compatload-01"
    PARTICIPANT_ID = "participant-compatload-01"

    # ── 1) "Neuer Prozess": last_valid ist DIREKT wallet-projizierbar (die SL
    #      muss GAR NICHT real aufgerufen werden -- `repair_fn=None`). ─────────
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, ps_store = _new_env(root)
        last_valid = full_v7_save(CHAR_ID, name="Flo")
        last_valid["economy"] = {"wallets": {CHAR_ID: {"balance": 80, "currency": "CU"}}}
        envelope = scompat.build_compat_envelope(
            envelope_version=1, repair_key="rk-01", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            operation_key="creation", table_id=None, section_id=None, raw_responses=[], best_view=None,
            last_valid=last_valid, created_ts=1.0,
        )
        outcome = save_compat_core.attempt_compat_load(
            run_dir, repair_key="rk-01", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=ps_store.schema_path, envelope=envelope, repair_fn=None,
        )
        check("direct_projectable_candidate_adopted_without_repair_fn", outcome.status == "adopted")
        check("adopted_block_has_no_currency_key", "currency" not in outcome.block["economy"]["wallets"][CHAR_ID])

        # "weitere Spielaktion" als Offline-Probe: der kanonische Store wurde
        # ATOMAR fortgeschrieben und ist ab jetzt regulaer lesbar/spielbar.
        played_back = store.load_current_save(run_dir, PARTICIPANT_ID, ps_store, states_dir=states_dir)
        check("published_save_readable_for_next_action", played_back == outcome.block)

        # NEGATIV: ein zweiter Aufruf fuer DENSELBEN repair_key NACH Adoption
        # darf KEINE zweite Veroeffentlichung/kein doppeltes "adopted" ausloesen.
        outcome2 = save_compat_core.attempt_compat_load(
            run_dir, repair_key="rk-01", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=ps_store.schema_path, envelope=envelope, repair_fn=None,
        )
        check("second_call_same_repair_key_still_adopted_no_relapse", outcome2.status == "adopted")
        check(
            "second_call_did_not_reset_attempt_rounds",
            outcome2.repair_rounds_used == outcome.repair_rounds_used,
        )

    # ── 2) Fake-SL-Reparatur (injizierte repair_fn statt echter Inferenz): der
    #      Rohkandidat ist zunaechst NICHT projizierbar (Fremdwaehrung), die
    #      Fake-SL liefert nach EINER Runde eine korrigierte Fassung. ─────────
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, ps_store = _new_env(root)
        broken = full_v7_save(CHAR_ID, name="Flo")
        broken["economy"] = {"wallets": {CHAR_ID: {"balance": 80, "currency": "USD"}}}  # nicht automatisch loesbar
        fixed = full_v7_save(CHAR_ID, name="Flo")
        fixed["economy"] = {"wallets": {CHAR_ID: {"balance": 80}}}

        call_log = []

        def fake_sl_repair(candidate, open_issues):
            call_log.append(copy.deepcopy(open_issues))
            return fixed

        envelope2 = scompat.build_compat_envelope(
            envelope_version=1, repair_key="rk-02", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            operation_key="creation", table_id=None, section_id=None, raw_responses=[], best_view=None,
            last_valid=broken, created_ts=1.0,
        )
        outcome3 = save_compat_core.attempt_compat_load(
            run_dir, repair_key="rk-02", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=ps_store.schema_path, envelope=envelope2, repair_fn=fake_sl_repair,
        )
        check("fake_sl_repair_called_exactly_once_before_adoption", len(call_log) == 1)
        check("fake_sl_repair_result_adopted", outcome3.status == "adopted" and outcome3.block == fixed)

    # ── 3) NEGATIV: ein unlösbarer Fall (Fake-SL liefert NIE etwas Gueltiges)
    #      endet bounded in `hold`, OHNE Endlos-Karussell -- genau 3 Runden. ───
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, ps_store = _new_env(root)
        unsolvable = full_v7_save(CHAR_ID, name="Flo")
        unsolvable["economy"] = {"wallets": {CHAR_ID: {"balance": 80, "currency": "GBP"}}}
        calls = {"n": 0}

        def never_fixes(candidate, open_issues):
            calls["n"] += 1
            return candidate  # bleibt dauerhaft ungueltig

        envelope3 = scompat.build_compat_envelope(
            envelope_version=1, repair_key="rk-03", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            operation_key="creation", table_id=None, section_id=None, raw_responses=[], best_view=None,
            last_valid=unsolvable, created_ts=1.0,
        )
        outcome4 = save_compat_core.attempt_compat_load(
            run_dir, repair_key="rk-03", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=ps_store.schema_path, envelope=envelope3, repair_fn=never_fixes,
        )
        check("unsolvable_case_ends_in_hold_not_crash", outcome4.status == "hold")
        check("unsolvable_case_bounded_to_max_attempts", calls["n"] == save_compat_core.MAX_COMPAT_LOAD_REPAIR_ATTEMPTS)
        check("unsolvable_case_reason_is_attempts_exhausted", outcome4.reason == "compat_load_attempts_exhausted")

        # Restart-Simulation: ein weiterer Aufruf nach HOLD ruft die Fake-SL
        # NICHT erneut auf (kein zweites endloses Dreierkarussell) UND bleibt
        # bei demselben HOLD-Grund.
        outcome5 = save_compat_core.attempt_compat_load(
            run_dir, repair_key="rk-03", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=ps_store.schema_path, envelope=envelope3, repair_fn=never_fixes,
        )
        check("resume_after_hold_does_not_call_repair_fn_again", calls["n"] == save_compat_core.MAX_COMPAT_LOAD_REPAIR_ATTEMPTS)
        check("resume_after_hold_reports_same_hold_state", outcome5.status == "hold")

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
