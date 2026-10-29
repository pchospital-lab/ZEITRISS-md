#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_compat_export_after_three.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`compat_export_after_three` (02_SAVEVERTRAG.md §D,
`core.save_compatibility.build_and_write_compat_export`).

Deckt: nach endgueltig erschoepftem Korrekturbudget wird ein versionierter,
terminal-exportier-/importierbarer Kompatibilitaetsumschlag geschrieben,
der `raw_responses` FRISCH aus dem bereits vorhandenen Roharchiv liest
(kein zweiter Rohantwortspeicher); `canonical_import_eligible` ist IMMER
`False` -- NEGATIV: der Umschlag darf NIE als kanonisch-valide/completed
gezaehlt werden; ein frueherer Export wird NIE geloescht/ueberschrieben
(neue Versionsnummer je Aufruf)."""
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
from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    CHAR_ID = "chrono-export-01"
    REPAIR_KEY = "creation::participant-export-01::chrono-export-01"
    CREATED_TS = 1000000000.0

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)

        # Vorbedingung dieser Gruppe: nach drei erschoepften Korrekturversuchen
        # liegt bereits ein Roharchiv vor (wiederverwendet `archive_raw_response`
        # aus `raw_archive_and_atomic_commit`).
        for attempt_no, raw_text in enumerate(["Antwort 1 (ungueltig)", "Antwort 2 (ungueltig)", "Antwort 3 (ungueltig)"], start=1):
            save_compat_core.archive_raw_response(
                run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, section_id="s1", table_id="t1",
                attempt_no=attempt_no, request_id=f"req-{attempt_no}", raw_text=raw_text,
            )

        best_view = full_v7_save(CHAR_ID, name="Flo")
        best_view["economy"] = {"wallets": {CHAR_ID: {"balance": 50, "currency": "CU"}}}

        check("no_export_exists_before_first_write", save_compat_core.latest_compat_export(run_dir, REPAIR_KEY) is None)

        envelope, path1 = save_compat_core.build_and_write_compat_export(
            run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, participant_id="participant-export-01",
            operation_key="creation", table_id="t1", section_id="s1",
            best_view=best_view, last_valid=None, created_ts=CREATED_TS,
            errors=["attempt_budget_exhausted"],
        )
        check("export_schema_is_compat_envelope_schema", envelope["schema"] == scompat.COMPAT_ENVELOPE_SCHEMA)
        check("export_raw_responses_read_fresh_from_archive", len(envelope["raw_responses"]) == 3)
        check("export_version_starts_at_one", envelope["envelope_version"] == 1)
        # NEGATIV: der Kompat-Stand ist NIEMALS kanonisch/completed.
        check("export_canonical_import_eligible_is_false", envelope["canonical_import_eligible"] is False)
        check("export_structurally_valid", scompat.validate_compat_envelope(envelope) == [])
        check("export_recognized_as_compat_envelope", scompat.is_compat_envelope(envelope))
        check("export_not_recognized_as_plain_v7_save", not scompat.is_compat_envelope(best_view))

        # ── Zweiter Export (z.B. nach einer spaeteren Teilreparatur): NEUE
        #    Versionsnummer, der erste bleibt UNVERAENDERT auf Platte. ─────────
        envelope2, path2 = save_compat_core.build_and_write_compat_export(
            run_dir, repair_key=REPAIR_KEY, char_id=CHAR_ID, participant_id="participant-export-01",
            operation_key="creation", table_id="t1", section_id="s1",
            best_view=best_view, last_valid=None, created_ts=CREATED_TS + 10,
            errors=["attempt_budget_exhausted"],
        )
        check("second_export_gets_version_two", envelope2["envelope_version"] == 2)
        check("second_export_is_new_file_not_overwrite", path1 != path2 and path1.exists() and path2.exists())
        check("first_export_file_content_unchanged_after_second_write", save_compat_core.latest_compat_export(run_dir, REPAIR_KEY) == envelope2)

        # ── Negativ: ein Umschlag ganz ohne verwertbare Sicht (weder best_view
        #    noch last_valid) ist strukturell UNGUELTIG -- der Bauversuch wirft,
        #    schreibt NICHTS. ────────────────────────────────────────────────
        threw = False
        try:
            save_compat_core.build_and_write_compat_export(
                run_dir, repair_key="creation::participant-export-02::chrono-export-02", char_id="chrono-export-02",
                participant_id="participant-export-02", operation_key="creation", table_id=None, section_id=None,
                best_view=None, last_valid=None, created_ts=CREATED_TS,
            )
        except ValueError:
            threw = True
        check("empty_view_envelope_rejected_with_value_error", threw)
        check(
            "empty_view_envelope_did_not_write_any_file",
            save_compat_core.latest_compat_export(run_dir, "creation::participant-export-02::chrono-export-02") is None,
        )

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
