#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_candidate_selection_and_provenance.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`candidate_selection_and_provenance` (02_SAVEVERTRAG.md §C,
`domain.zeitriss.save_compatibility.select_candidate`).

Deckt: deterministische Auswahl bevorzugt den ERSTEN vollstaendig
gueltigen, identitaets-/inhaltstreuen GANZEN Kandidaten (direkt ODER ueber
die wertgleiche Wallet-Projektion) in GENAU der vom Aufrufer vorgegebenen
Reihenfolge -- KEIN Ranking nach Laenge/Vollstaendigkeits-Heuristik, KEIN
Vermischen mehrerer Kandidaten. `source_tag` im Ergebnis gehoert IMMER zu
GENAU dem gewaehlten Kandidaten (nie einer gemischten Herkunft)."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    CHAR_ID = "chrono-select-01"

    invalid_1 = full_v7_save(CHAR_ID, name="Flo")
    invalid_1["v"] = 6  # schema-ungueltig UNABHAENGIG vom Wallet -- die Wallet-Projektion kann das NICHT reparieren.
    invalid_1["economy"] = {"wallets": {CHAR_ID: 999}}

    cu_valid_via_projection = full_v7_save(CHAR_ID, name="Flo")
    cu_valid_via_projection["economy"] = {"wallets": {CHAR_ID: {"balance": 42, "currency": "CU"}}}

    fully_valid = full_v7_save(CHAR_ID, name="Flo")
    fully_valid["economy"] = {"wallets": {CHAR_ID: {"balance": 7}}}

    another_fully_valid = full_v7_save(CHAR_ID, name="Flo")
    another_fully_valid["economy"] = {"wallets": {CHAR_ID: {"balance": 1234}}}

    # ── 1) Reihenfolge entscheidet: der erste gueltige (ggf. via Projektion)
    #      Kandidat gewinnt, nicht der "beste"/laengste. ────────────────────────
    res1 = scompat.select_candidate(
        [("attempt-1", invalid_1), ("attempt-2", cu_valid_via_projection), ("attempt-3", fully_valid)],
        CHAR_ID,
    )
    check("first_valid_in_order_selected", res1.selected is not None and res1.source_tag == "attempt-2")
    check("selection_used_projection_flag_set", res1.used_projection is True)
    check("selected_canonical_has_no_currency_key", "currency" not in res1.selected["economy"]["wallets"][CHAR_ID])
    check("selection_reason_is_selected", res1.reason == "selected")

    # ── 2) Waere der direkt gueltige Kandidat FRUEHER in der Liste, gewinnt
    #      ER (keine Projektions-Praeferenz, reine Reihenfolge) ────────────────
    res2 = scompat.select_candidate(
        [("attempt-1", invalid_1), ("attempt-2", fully_valid), ("attempt-3", cu_valid_via_projection)],
        CHAR_ID,
    )
    check("earlier_direct_valid_wins_over_later_projectable", res2.source_tag == "attempt-2")
    check("earlier_direct_valid_used_projection_false", res2.used_projection is False)

    # ── 3) Negativ: kein einziger Kandidat gueltig -> selected None, reason
    #      dokumentiert den ZULETZT geprueften Kandidaten (nicht 'erraten') ────
    res3 = scompat.select_candidate([("only-attempt", invalid_1)], CHAR_ID)
    check("no_valid_candidate_selected_is_none", res3.selected is None)
    check("no_valid_candidate_reason_references_last_attempt", "only-attempt" in res3.reason)
    check("no_valid_candidate_source_tag_is_none", res3.source_tag is None)

    # ── 4) Negativ: leere Kandidatenliste -> 'no_candidates', kein Crash ────────
    res4 = scompat.select_candidate([], CHAR_ID)
    check("empty_candidate_list_reason_no_candidates", res4.selected is None and res4.reason == "no_candidates")

    # ── 5) Provenance ist NIE gemischt: zwei verschiedene gueltige Kandidaten
    #      mit unterschiedlichem Inhalt -> source_tag gehoert GENAU zum
    #      gewaehlten, nicht zu beiden/einem Mix. ───────────────────────────────
    res5 = scompat.select_candidate(
        [("attempt-A", fully_valid), ("attempt-B", another_fully_valid)],
        CHAR_ID,
    )
    check("provenance_matches_chosen_content_not_other", res5.source_tag == "attempt-A" and res5.selected == fully_valid)
    check("provenance_not_the_unchosen_alternative", res5.selected != another_fully_valid)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
