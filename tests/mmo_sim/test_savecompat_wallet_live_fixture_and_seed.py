#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_wallet_live_fixture_and_seed.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`wallet_live_fixture_and_seed` (02_SAVEVERTRAG.md §B).

Self-contained (FIXTURE_ONLY, s. `_full_v7_fixture.py`) -- bewusst OHNE
echte private p01-Live-Evidenz (die liegt ausserhalb dieses Baums und ist
bereits separat gegen die Produktions-APIs verifiziert, s.
`worker/logs/verify_wallet_fix_real_p01.py` + `.log`, 13/13 PASS,
eingefroren). Ein `tests/mmo_sim/`-File ist Teil des PUBLIC-Kandidaten
(CONTROL.json `public_allowed_prefixes`) und muss in JEDEM Checkout
(auch `clean_checkout_full_regression_smoke`) lauffaehig sein -- ein
hartcodierter privater Evidenzpfad waere dort nicht vorhanden. Dieser Test
deckt denselben Fehlerfall (ZEITRISS-eigene `currency:"CU"`-Zusatzangabe im
Wallet) stattdessen mit einer aequivalenten, oeffentlich-sicheren Fixture
ab UND prueft zusaetzlich die in 02_SAVEVERTRAG.md referenzierte
Seed-Illustration (`seed/wallet_projection_seed.py`, NICHT installiert) auf
Werte-Paritaet gegen die echte Domaenenfunktion -- das ist der
'...and_seed'-Teil dieser Gruppe."""
from __future__ import annotations

import copy
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


CHAR_ID = "chrono-wallet-seed-01"


def _seed_project_wallets(block: dict) -> dict:
    """Reine Kopie der Seed-Illustration (`seed/wallet_projection_seed.py:
    project_wallets`) -- das Paket selbst ist nicht Teil des installierten
    Produkts (CONTROL `forbidden_public`), diese Funktion dient NUR dem
    Paritaetsvergleich gegen die ECHTE Domaenenfunktion weiter unten, nicht
    als eigener Produktionscode-Pfad."""
    import math

    def _finite(v):
        return type(v) is int or (type(v) is float and math.isfinite(v))

    candidate = copy.deepcopy(block)
    economy = candidate.get("economy")
    wallets = economy.get("wallets") if type(economy) is dict else None
    if type(wallets) is not dict:
        return candidate
    for char_id, wallet in list(wallets.items()):
        if _finite(wallet):
            wallets[char_id] = {"balance": wallet}
        elif type(wallet) is dict and wallet.get("currency") == "CU" and _finite(wallet.get("balance")):
            del wallet["currency"]
    return candidate


if __name__ == "__main__":
    # ── 1) Live-Fixture: numerisches Wallet (bekannter realer Fehlertyp) ────────
    numeric_block = full_v7_save(CHAR_ID, name="Flo")
    numeric_block["economy"] = {"wallets": {CHAR_ID: 100}}

    direct = sv.validate_save_block(numeric_block, CHAR_ID)
    check("numeric_wallet_rejected_by_strict_schema_directly", not direct.accepted)

    outcome = scompat.evaluate_with_wallet_projection(numeric_block, CHAR_ID)
    check("numeric_wallet_accepted_via_projection", outcome.accepted and outcome.used_projection)
    check("numeric_wallet_canonical_is_balance_object", outcome.canonical_block["economy"]["wallets"][CHAR_ID] == {"balance": 100})
    check("numeric_wallet_retained_original_is_raw", outcome.retained_original == numeric_block)

    # ── 2) Live-Fixture: objektfoermiges Wallet mit CU-Zusatzfeld ───────────────
    cu_block = full_v7_save(CHAR_ID, name="Flo")
    cu_block["economy"] = {"wallets": {CHAR_ID: {"balance": 250, "currency": "CU"}}}

    direct_cu = sv.validate_save_block(cu_block, CHAR_ID)
    check("cu_wallet_rejected_by_strict_schema_directly", not direct_cu.accepted)

    outcome_cu = scompat.evaluate_with_wallet_projection(cu_block, CHAR_ID)
    check("cu_wallet_accepted_via_projection", outcome_cu.accepted and outcome_cu.used_projection)
    check("cu_wallet_canonical_has_no_currency_key", "currency" not in outcome_cu.canonical_block["economy"]["wallets"][CHAR_ID])
    check("cu_wallet_balance_value_unchanged", outcome_cu.canonical_block["economy"]["wallets"][CHAR_ID]["balance"] == 250)
    check("cu_wallet_annotation_records_retained_CU", outcome_cu.annotations[0]["retained_value"] == "CU")

    # ── 3) Negativ: Fremdwaehrung wird NICHT konvertiert, bleibt abgelehnt ──────
    foreign_block = full_v7_save(CHAR_ID, name="Flo")
    foreign_block["economy"] = {"wallets": {CHAR_ID: {"balance": 250, "currency": "USD"}}}
    foreign_outcome = scompat.evaluate_with_wallet_projection(foreign_block, CHAR_ID)
    check("foreign_currency_not_converted_stays_rejected", not foreign_outcome.accepted)
    check("foreign_currency_projection_did_not_change_value", not scompat.project_wallets_in_block(foreign_block).changed)

    # ── 4) Negativ: kein Save-Block vorhanden -> sauber abgelehnt, kein Crash ───
    none_outcome = scompat.evaluate_with_wallet_projection(None, CHAR_ID)
    check("missing_block_rejected_not_crashed", not none_outcome.accepted and none_outcome.canonical_block is None)

    # ── 5) Idempotenz: ein bereits kanonischer Block bleibt unveraendert ────────
    idem = scompat.project_wallets_in_block(outcome_cu.canonical_block)
    check("idempotent_on_already_canonical_block", idem.canonical_candidate == outcome_cu.canonical_block and not idem.changed)

    # ── 6) Seed-Paritaet: Illustration und echte Domaenenfunktion liefern
    #      WERTGLEICHE Kanonikfassung fuer BEIDE Live-Fehlertypen ──────────────
    for label, block in (("numeric", numeric_block), ("cu", cu_block), ("foreign", foreign_block)):
        seed_result = _seed_project_wallets(block)
        domain_result = scompat.project_wallets_in_block(block).canonical_candidate
        check(f"seed_and_domain_projection_agree_{label}", seed_result == domain_result)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
