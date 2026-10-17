#!/usr/bin/env python3
"""
tests/mmo_sim/test_s3_wallet_alias_uniqueness_and_empty_sibling_drift.py --
S3 (ZR-N2-STABILISIERUNG-WEITERLAUF-2026-10-17-R1): zwei Luecken im F1/F2-
Aliasfix (`mmo_sim/domain/zeitriss/save_correction.py:detect_unjustified_
drift`/`_is_allowed_required_key_rename`/`_is_allowed_amount_wrap`), BEIDE
echt reproduziert GEGEN DEN ALTEN CODE vor diesem Fix (sha-referenziert
unten, Original+Derivat+Diff-Konvention dieses Repos):

1. Doppel-Alias-Kollaps: `amount:100, credits:100` -> NUR `balance:100`
   wurde unabhaengig fuer JEDEN alten Schluessel einzeln als "genau EIN
   neuer Kandidat" erkannt (`len(candidates) == 1` pro altem Schluessel,
   ohne zu pruefen, ob dieser EINE Kandidat bereits von einem ANDEREN alten
   Schluessel verbraucht wurde) -- BEIDE Aliasse wurden faelschlich als
   wertgleicher 1:1-Rename durchgelassen, Drift blieb leer. Jetzt: EIN
   verbrauchter neuer Blattpfad kann nur EINEN alten Alias decken; der
   zweite bleibt (und macht damit Drift insgesamt nicht-leer -> HOLD).

2. Leere-Zusatzfeld-Bypass: `_flatten` erzeugt fuer ein leeres Objekt/Array
   KEINEN Blattpfad -- ein zusaetzliches `{}`/`[]` NEBEN dem eigentlichen
   Rename (z.B. `{"balance": 100, "history": []}` statt `{"balance": 100}`)
   war fuer die bisherige, rein geflattete `candidates`-Zaehlung komplett
   unsichtbar und wurde durchgelassen. Jetzt: `_sibling_keys_match`
   vergleicht die ROHEN Elternobjekt-Schluessel (nicht die geflatteten
   Blaetter) und erkennt JEDEN unbegruendeten Zusatzschluessel, auch einen
   mit leerem Wert.

Beide Faelle werden hier GEGEN DEN ECHTEN gepinnten v7-Validator (`evaluate`)
UND isoliert gegen `detect_unjustified_drift` belegt. Pure Python, nur
`assert`, echter Exitcode -- gleiches Muster wie `test_n2f_a_f1_f2_wallet_
key_rename_fix_2026_10_17.py`."""
from __future__ import annotations

import copy
import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

CHAR_ID = "CHR-S3-9Q21"


def _wallet_block(char_id: str, wallet_obj: object) -> dict:
    block = full_v7_save(char_id, name="Ren Okafor", callsign="S3")
    block["economy"] = {"wallets": {char_id: wallet_obj}}
    return block


def test_double_alias_collapse_is_now_rejected_as_drift():
    """Reproduziert den konkreten 01_AUFTRAG.md-§S3-Fund: `amount:100,
    credits:100` -> NUR `balance:100` darf NICHT als wertgleicher
    Eindeutigkeits-Rename durchgehen -- die Zuordnung alt->neu ist nicht
    mehr eindeutig (zwei Aliasse auf einen Wert)."""
    before = _wallet_block(CHAR_ID, {"amount": 100, "credits": 100})
    after = _wallet_block(CHAR_ID, {"balance": 100})
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    assert f"/economy/wallets/{CHAR_ID}" in error_paths, error_paths

    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift, "Doppel-Alias-Kollaps (amount+credits -> balance) MUSS als Drift erkannt werden (HOLD)"
    drifted_paths = {row[0] for row in drift}
    assert f"/economy/wallets/{CHAR_ID}/amount" in drifted_paths or (
        f"/economy/wallets/{CHAR_ID}/credits" in drifted_paths
    ), drift


def test_single_alias_rename_still_accepted_unaffected_by_uniqueness_fix():
    """Positive Kontrolle: der bereits bestehende, legitime EIN-Alias-Rename
    (F1/F2) bleibt vom neuen Eindeutigkeits-Check VOELLIG unberuehrt."""
    before = _wallet_block(CHAR_ID, {"amount": 100})
    after = _wallet_block(CHAR_ID, {"balance": 100})
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift == [], drift


def test_empty_sibling_object_next_to_rename_is_now_rejected_as_drift():
    """01_AUFTRAG.md §S3: ein zusaetzliches LEERES Objekt neben dem
    eigentlichen Rename (`{"balance": 100, "history": {}}`) darf den engen
    Driftvertrag NICHT passieren -- auch wenn es (anders als ein Scalar-
    Zusatzschluessel) in den geflatteten Blaettern unsichtbar bliebe."""
    before = _wallet_block(CHAR_ID, {"amount": 100})
    after = _wallet_block(CHAR_ID, {"balance": 100, "history": {}})
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift, "leeres Zusatzobjekt neben dem Rename MUSS als Drift erkannt werden (HOLD)"


def test_empty_sibling_list_next_to_rename_is_now_rejected_as_drift():
    """Wie oben, mit leerem Array statt Objekt (`{"balance": 100,
    "log": []}`) -- beide Container-Typen (`_flatten` behandelt dict/list
    identisch) muessen gleich erkannt werden."""
    before = _wallet_block(CHAR_ID, {"amount": 100})
    after = _wallet_block(CHAR_ID, {"balance": 100, "log": []})
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift, "leeres Zusatzarray neben dem Rename MUSS als Drift erkannt werden (HOLD)"


def test_empty_sibling_next_to_scalar_to_object_wrap_is_now_rejected():
    """Dieselbe Luecke betrifft auch den AELTEREN Zahl->Objekt-Wrap-Pfad
    (`_is_allowed_amount_wrap`, nicht nur den Geschwister-Rename): Zahl
    100 -> `{"balance": 100, "meta": []}` darf nicht durchgehen, nur weil
    'meta' leer ist."""
    before = _wallet_block(CHAR_ID, 100)
    after = _wallet_block(CHAR_ID, {"balance": 100, "meta": []})
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift, "leeres Zusatzfeld neben dem Zahl->Objekt-Wrap MUSS als Drift erkannt werden (HOLD)"


def test_unrelated_untouched_empty_containers_elsewhere_stay_driftfree():
    """Gegenkontrolle gegen eine falsch-positive Ueberkorrektur: ein an
    ANDERER Stelle im Dokument bereits VOR UND NACH der Korrektur gleich
    gebliebener leerer Container (z.B. `economy` ausserhalb des Wallets)
    darf durch den neuen Check NICHT ploetzlich als Drift auftauchen --
    `_flatten` bleibt bewusst global unveraendert (kein Blattpfad fuer
    leere Container AUSSERHALB der gezielten Geschwisterpruefung)."""
    before = full_v7_save(CHAR_ID, name="Ren Okafor", callsign="S3")
    before["economy"] = {"wallets": {CHAR_ID: {"amount": 100}}}
    after = copy.deepcopy(before)
    after["economy"]["wallets"][CHAR_ID] = {"balance": 100}
    # `logs.flags.imported_saves` bleibt in beiden Faellen `[]` (Fixture-Default) --
    # unveraendert und ohne jeden Bezug zum Wallet-Rename.
    assert before["logs"]["flags"]["imported_saves"] == [] == after["logs"]["flags"]["imported_saves"]
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift == [], drift


def test_fully_regenerated_unrelated_block_with_now_empty_economy_stays_driftfree():
    """Regressionsbeleg fuer den w48/`test_sc04`-Fall, der WAEHREND der
    Entwicklung dieses Fixes real brach: ein komplett NEU generierter,
    inhaltlich unverwandter Korrekturversuch (SL ignoriert den defekten
    Entwurf komplett und liefert einen frischen gueltigen Save), bei dem
    `economy` dadurch von einem (fehlerhaft befuellten) Objekt zu einem
    LEEREN Objekt wird, bleibt weiterhin driftfrei -- der S3-Fix darf
    NICHT jeden irgendwo neu entstehenden leeren Container global als
    Drift behandeln, nur den gezielten Geschwisterfall am Rename-/Wrap-
    Elternknoten selbst."""
    before = full_v7_save(CHAR_ID, name="Ren Okafor")
    before["economy"] = {"wallets": {CHAR_ID: 500}}
    after = full_v7_save(CHAR_ID, name="Ren Okafor")
    assert after["economy"] == {}
    error_paths = {e.path for e in save_correction_domain.evaluate(before, CHAR_ID).structure.errors}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths)
    assert drift == [], drift


def _run(name: str, fn) -> bool:
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL {name}: {e}")
        traceback.print_exc()
        return False
    except Exception as e:  # pragma: no cover
        print(f"ERROR {name}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    print(f"PASS {name}")
    return True


if __name__ == "__main__":
    tests = [
        ("test_double_alias_collapse_is_now_rejected_as_drift",
         test_double_alias_collapse_is_now_rejected_as_drift),
        ("test_single_alias_rename_still_accepted_unaffected_by_uniqueness_fix",
         test_single_alias_rename_still_accepted_unaffected_by_uniqueness_fix),
        ("test_empty_sibling_object_next_to_rename_is_now_rejected_as_drift",
         test_empty_sibling_object_next_to_rename_is_now_rejected_as_drift),
        ("test_empty_sibling_list_next_to_rename_is_now_rejected_as_drift",
         test_empty_sibling_list_next_to_rename_is_now_rejected_as_drift),
        ("test_empty_sibling_next_to_scalar_to_object_wrap_is_now_rejected",
         test_empty_sibling_next_to_scalar_to_object_wrap_is_now_rejected),
        ("test_unrelated_untouched_empty_containers_elsewhere_stay_driftfree",
         test_unrelated_untouched_empty_containers_elsewhere_stay_driftfree),
        ("test_fully_regenerated_unrelated_block_with_now_empty_economy_stays_driftfree",
         test_fully_regenerated_unrelated_block_with_now_empty_economy_stays_driftfree),
    ]
    ok_all = [_run(name, fn) for name, fn in tests]
    sys.exit(0 if all(ok_all) else 1)
