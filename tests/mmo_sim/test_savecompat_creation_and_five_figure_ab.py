#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_creation_and_five_figure_ab.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`creation_and_five_figure_ab` (02_SAVEVERTRAG.md §A-D).

SCOPE-GRENZE (SK-A-cont-Brief): NUR der OFFLINE-pruefbare Struktur-/
Lifecycle-Anteil -- Save -> Kompat-Export -> neuer Prozess ->
Ladereparatur -> eine weitere Aktion, mit einer injizierten Fake-SL
(`repair_fn`, KEIN echter Modellaufruf). Die echten Geld-/Live-Anteile
(fuenf echte Figuren ueber eine reale Persona-CLI, A/B-Vergleich gegen
echte Transportkosten) sind NICHT Teil dieses Tests -- NOT_RUN, spaetere
Phase (SK-POST-C/Main-Endcheck mit echter Live-Autorisierung). Dieser Test
fingiert KEINE Hardcode-Endstaende -- jeder Zwischenschritt wird ueber die
echte Produktions-API ausgefuehrt, nur der Transport (SL-Antwort) ist
fingiert."""
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

import mmo_sim.core.save_compatibility as save_compat_core  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation as sv  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    _DUMMY_PERSONA_SCHEMA = (
        '{"type":"object","required":["v","persona_key","rounds_played"],"properties":{"v":{"const":2}}}'
    )

    CHAR_ID = "chrono-fivefig-ab-01"
    PARTICIPANT_ID = "participant-fivefig-ab-01"
    REPAIR_KEY = "creation::participant-fivefig-ab-01::chrono-fivefig-ab-01"

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        states_dir.mkdir(parents=True)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)

        # ── Schritt 1: drei (fingierte, "echte logische") Korrekturaufrufe
        #    scheitern -- jede Rohantwort wird append-only archiviert, bevor
        #    der endgueltige Export erfolgt (02.C/02.D-Kette). ────────────────
        broken_replies = [
            '```json\n{"v":7,"economy":{"wallets":{"chrono-fivefig-ab-01":{"balance":10,"currency":"GBP"}}}}\n```',
            '```json\n{"v":7,"economy":{"wallets":{"chrono-fivefig-ab-01":{"balance":10,"currency":"GBP"}}}}\n```',
            '```json\n{"v":7,"economy":{"wallets":{"chrono-fivefig-ab-01":{"balance":10,"currency":"GBP"}}}}\n```',
        ]
        for attempt_no, raw_text in enumerate(broken_replies, start=1):
            save_compat_core.archive_raw_response(
                run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, section_id="s1", table_id=None,
                attempt_no=attempt_no, request_id=f"req-{attempt_no}", raw_text=raw_text,
            )
        check("three_failed_attempts_archived_before_export", len(save_compat_core.read_raw_archive(run_dir, REPAIR_KEY)) == 3)

        # ── Schritt 2: Kompat-Export nach erschoepftem Budget (best_view =
        #    letzte Rohfassung, in sich NICHT kanonisch-gueltig). ─────────────
        best_view_raw = full_v7_save(CHAR_ID, name="Flo")
        best_view_raw["economy"] = {"wallets": {CHAR_ID: {"balance": 10, "currency": "GBP"}}}
        envelope, export_path = save_compat_core.build_and_write_compat_export(
            run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            operation_key="creation", table_id=None, section_id="s1",
            best_view=best_view_raw, last_valid=None, created_ts=1.0,
            errors=["attempt_budget_exhausted"],
        )
        check("compat_export_written_not_canonical", envelope["canonical_import_eligible"] is False)
        check("compat_export_file_on_disk", export_path.exists())

        # ── Schritt 3: "neuer Prozess" -- frischer `attempt_compat_load`-Aufruf
        #    auf DENSELBEN run_dir, KEIN In-Memory-Zustand wiederverwendet. ────
        reread_envelope = save_compat_core.latest_compat_export(run_dir, REPAIR_KEY)
        check("new_process_rereads_export_from_disk", reread_envelope == envelope)

        fixed = full_v7_save(CHAR_ID, name="Flo")
        fixed["economy"] = {"wallets": {CHAR_ID: {"balance": 10}}}  # GBP durch eine gueltige CU-Fassung ersetzt (Fake-SL)
        repair_calls = []

        def fake_sl_repair(candidate, open_issues):
            repair_calls.append(open_issues)
            return fixed

        load_outcome = save_compat_core.attempt_compat_load(
            run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=schema_path, envelope=reread_envelope, repair_fn=fake_sl_repair,
        )
        check("new_process_load_repair_adopted", load_outcome.status == "adopted")
        check("new_process_load_used_exactly_one_fake_sl_round", len(repair_calls) == 1)

        # ── Schritt 4: "weitere Spielaktion" als Offline-Probe -- der
        #    kanonische Save ist jetzt direkt (ohne jede Projektion) gueltig,
        #    kein zweites Endlos-Karussell, keine Doppel-`completed`. ─────────
        canonical = store.load_current_save(run_dir, PARTICIPANT_ID, ps_store, states_dir=states_dir)
        direct_check = sv.validate_save_block(canonical, CHAR_ID)
        check("next_action_reads_fully_canonical_save", direct_check.accepted)
        check("next_action_save_is_not_hardcoded_endstate", canonical["economy"]["wallets"][CHAR_ID]["balance"] == 10)

        # NEGATIV: ein erneuter Ladeversuch fuer denselben repair_key loest
        # KEINE zweite Veroeffentlichung/kein doppeltes "adopted" aus.
        load_outcome_2 = save_compat_core.attempt_compat_load(
            run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=states_dir, schema_path=schema_path, envelope=reread_envelope, repair_fn=fake_sl_repair,
        )
        check("repeat_load_after_adoption_is_not_a_second_completion", load_outcome_2.status == "adopted" and len(repair_calls) == 1)

    print()
    print("HINWEIS: Geld-/Live-Anteil (reale Persona-CLI, fuenf echte Figuren, A/B-Transportvergleich) ist NOT_RUN -- spaetere Phase.")
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
