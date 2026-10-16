#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_conflict_no_silent_merge.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`conflict_no_silent_merge` (02_SAVEVERTRAG.md §C,
`domain.zeitriss.save_compatibility.merge_conflict_free`).

Deckt die bewusst ENGEN Merge-Regeln: NUR Pfade, die im Primaerkandidaten
GAR NICHT existieren, werden aus Zusatzquellen ergaenzt (kein
`dict.update`, kein Ueberschreiben, keine Maximalwert-Auswahl); liegt ein
fehlender Pfad in MEHREREN Zusatzquellen MIT abweichendem Wert vor, ist das
ein KONFLIKT -- NICHT uebernommen, in `conflicts` gelistet, bleibt im
`merged`-Ergebnis ABWESEND (kein 'erster gewinnt'); Listenwerte werden NIE
elementweise konkateniert/dedupliziert."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    primary = {"a": 1, "b": {"x": 1}, "list_field": [1, 2]}

    # ── 1) Fehlender Pfad, UEBEREINSTIMMEND in zwei Zusatzquellen -> uebernommen,
    #      Provenance nennt die ERSTE liefernde Quelle. ─────────────────────────
    res1 = scompat.merge_conflict_free(
        primary, "primary-tag",
        [("supp-1", {"new_field": "same-value"}), ("supp-2", {"new_field": "same-value"})],
    )
    check("agreeing_missing_field_merged", res1.merged.get("new_field") == "same-value")
    check("agreeing_missing_field_provenance_is_first_source", res1.provenance.get("/new_field") == "supp-1")
    check("agreeing_missing_field_no_conflict_recorded", len(res1.conflicts) == 0)

    # ── 2) Fehlender Pfad, ABWEICHEND in zwei Zusatzquellen -> KONFLIKT,
    #      NICHT uebernommen, bleibt in `merged` ABWESEND ("kein erster
    #      gewinnt"). ───────────────────────────────────────────────────────────
    res2 = scompat.merge_conflict_free(
        primary, "primary-tag",
        [("supp-1", {"disputed_field": "value-A"}), ("supp-2", {"disputed_field": "value-B"})],
    )
    check("conflicting_missing_field_absent_from_merged", "disputed_field" not in res2.merged)
    check("conflicting_missing_field_recorded_as_conflict", any(c.path == "/disputed_field" for c in res2.conflicts))
    conflict_entry = next(c for c in res2.conflicts if c.path == "/disputed_field")
    check(
        "conflict_lists_both_source_values",
        {t for t, _ in conflict_entry.values_by_source} == {"supp-1", "supp-2"},
    )

    # ── 3) EXISTIERENDER Pfad in primary wird NIE ueberschrieben -- selbst wenn
    #      eine Zusatzquelle einen abweichenden Wert liefert (kein dict.update,
    #      keine Maximalwert-Auswahl). ───────────────────────────────────────────
    res3 = scompat.merge_conflict_free(
        primary, "primary-tag",
        [("supp-1", {"a": 999}), ("supp-2", {"b": {"x": 999}})],
    )
    check("existing_scalar_field_never_overwritten", res3.merged["a"] == 1)
    check("existing_nested_field_never_overwritten", res3.merged["b"]["x"] == 1)
    check("no_silent_update_recorded_as_provenance_either", "/a" not in res3.provenance and "/b/x" not in res3.provenance)

    # ── 4) Listen werden NIE elementweise konkateniert/dedupliziert -- ein
    #      bereits vorhandener Listenpfad bleibt exakt wie im Primaerkandidaten,
    #      unabhaengig vom Inhalt der Zusatzquelle. ─────────────────────────────
    res4 = scompat.merge_conflict_free(
        primary, "primary-tag",
        [("supp-1", {"list_field": [1, 2, 3, 4]})],
    )
    check("existing_list_field_not_concatenated", res4.merged["list_field"] == [1, 2])

    # ── 5) EIN NEUER Listenpfad (im Primaerkandidaten gar nicht vorhanden) wird
    #      als GANZER Wert uebernommen, nicht elementweise gemischt. ───────────
    res5 = scompat.merge_conflict_free(
        primary, "primary-tag",
        [("supp-1", {"new_list": [9, 9, 9]})],
    )
    check("new_list_field_adopted_as_whole_value", res5.merged.get("new_list") == [9, 9, 9])

    # ── 6) EINE einzelne Zusatzquelle (kein zweiter Widerspruch) -> kein
    #      Konflikt, normal uebernommen. ─────────────────────────────────────────
    res6 = scompat.merge_conflict_free(primary, "primary-tag", [("supp-1", {"single_source_field": "ok"})])
    check("single_supplement_no_conflict", len(res6.conflicts) == 0 and res6.merged.get("single_source_field") == "ok")

    # ── 7) Negativ: `merged` ist eine Kopie, kein Alias auf `primary` --
    #      Mutation des Ergebnisses darf `primary` NICHT veraendern. ───────────
    res7 = scompat.merge_conflict_free(primary, "primary-tag", [])
    res7.merged["a"] = 12345
    check("merged_result_is_deep_copy_not_alias", primary["a"] == 1)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
