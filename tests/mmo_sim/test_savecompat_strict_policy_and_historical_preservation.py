#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_strict_policy_and_historical_preservation.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`strict_policy_and_historical_preservation` (02_SAVEVERTRAG.md §B,
GENERALREVIEW.md).

Deckt zwei Haelften, wie im Brief verlangt ("die neue User-Policy als NEUE
Testfaelle; alte strikte-Policy-Tests bleiben erhalten"):

  1. NEUE Policy (R12-SAVECOMPAT): die beiden sanktionierten
     Wallet-Ausnahmen (Zahl->balance-Wrap, CU-Retention) sind die EINZIGEN
     Abweichungen vom strikten Exportschema, die ohne SL-Korrekturzyklus
     akzeptiert werden.
  2. HISTORISCHE Erhaltung: die alte, unveraenderte strikte
     Schemapruefung (`save_validation.validate_save_block` OHNE
     Projektion) bleibt fuer JEDEN anderen Fehlerfall GENAUSO strikt wie
     vor diesem Paket -- keine pauschale Lockerung, kein XFAIL/Skip."""
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
from mmo_sim.domain.zeitriss import save_validation as sv  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    CHAR_ID = "chrono-policy-01"

    # ── NEUE Policy: die beiden sanktionierten Ausnahmen werden akzeptiert ──────
    numeric_wallet = full_v7_save(CHAR_ID, name="Flo")
    numeric_wallet["economy"] = {"wallets": {CHAR_ID: 10}}
    check("new_policy_number_to_balance_accepted", scompat.evaluate_with_wallet_projection(numeric_wallet, CHAR_ID).accepted)

    cu_wallet = full_v7_save(CHAR_ID, name="Flo")
    cu_wallet["economy"] = {"wallets": {CHAR_ID: {"balance": 10, "currency": "CU"}}}
    check("new_policy_cu_retention_accepted", scompat.evaluate_with_wallet_projection(cu_wallet, CHAR_ID).accepted)

    # ── HISTORISCH erhalten: ALLE anderen strikten Faelle bleiben GENAUSO
    #    abgelehnt wie vor diesem Paket -- die Projektion darf NICHTS anderes
    #    "reparieren" als die beiden oben genannten Ausnahmen. ─────────────────
    missing_balance = full_v7_save(CHAR_ID, name="Flo")
    missing_balance["economy"] = {"wallets": {CHAR_ID: {"no_balance_here": 10}}}
    check(
        "historical_missing_balance_key_still_rejected",
        not scompat.evaluate_with_wallet_projection(missing_balance, CHAR_ID).accepted,
    )

    extra_unrelated_field = full_v7_save(CHAR_ID, name="Flo")
    extra_unrelated_field["economy"] = {"wallets": {CHAR_ID: {"balance": 10, "note": "unbekanntes Feld"}}}
    check(
        "historical_unrelated_additional_property_still_rejected",
        not scompat.evaluate_with_wallet_projection(extra_unrelated_field, CHAR_ID).accepted,
    )

    foreign_currency = full_v7_save(CHAR_ID, name="Flo")
    foreign_currency["economy"] = {"wallets": {CHAR_ID: {"balance": 10, "currency": "EUR"}}}
    check(
        "historical_non_CU_currency_still_rejected_no_guessing",
        not scompat.evaluate_with_wallet_projection(foreign_currency, CHAR_ID).accepted,
    )

    schema_version_mismatch = full_v7_save(CHAR_ID, name="Flo")
    schema_version_mismatch["v"] = 6
    check(
        "historical_schema_version_mismatch_still_rejected_even_with_valid_wallet",
        not scompat.evaluate_with_wallet_projection(schema_version_mismatch, CHAR_ID).accepted,
    )

    wrong_identity = full_v7_save(CHAR_ID, name="Flo")
    check(
        "historical_identity_binding_still_enforced",
        not sv.validate_save_block(wrong_identity, "some-other-char-id").accepted,
    )

    # ── Negativ (Kernregel): die strikte DIREKTE Pruefung (ohne Projektion)
    #    bleibt UNVERAENDERT streng fuer beide neuen Policy-Faelle selbst --
    #    die Ausnahme lebt NUR im Projektions-Overlay, NICHT im Basisschema. ───
    check("strict_direct_validation_still_rejects_numeric_wallet", not sv.validate_save_block(numeric_wallet, CHAR_ID).accepted)
    check("strict_direct_validation_still_rejects_cu_wallet", not sv.validate_save_block(cu_wallet, CHAR_ID).accepted)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
