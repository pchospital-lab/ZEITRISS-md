#!/usr/bin/env python3
"""
tests/mmo_sim/test_n2r4_save_correction_schema_hint_2026_10_19.py
-- ZR-N2R-ANSCHLUSS-20261019-R4, Arbeit A: der normale, request-gebundene
SL-Korrekturprompt (`mmo_sim/domain/zeitriss/save_correction.py:
build_correction_message`) transportiert jetzt den aus dem UNVERÄNDERTEN
v7-Exportschema abgeleiteten Zielform-Hinweis.

Hintergrund (01_REVIEW_N2R3.md §1): Im R3-Live-Lauf meldete der Validator nur
"100 is not of type 'object'". Ohne Zielform riet die SL `{"cu": 100}` -- das
v7-Exportschema verlangt aber ein Objekt mit numerischem Pflichtfeld `balance`
und verbietet Zusatzfelder (`additionalProperties: false`). Der Driftwächter
kennt `balance|amount|credits|value`, NICHT `cu`. Ein gemeldeter
`callsign: null`-Typfehler braucht die leere Zeichenkette, keine neue
Identität.

Diese Tests belegen die kleinste echte Produktänderung:
  - Der Korrekturprompt nennt für den Wallet-Fehlerpfad die schema-abgeleitete
    Zielform (Objekt, Pflichtfeld `balance` (number), keine Zusatzfelder) und
    für einen null-Callsign die leere Zeichenkette.
  - Er whitelistet NICHT `cu` und lockert kein Schema.
  - Die korrekte `{"balance": 100}`-Form + leerer Callsign ist schema-gültig
    UND driftfrei (wird im Normalpfad übernommen).
  - R3s `{"cu": 100}` bleibt abgelehnt (schema-ungültig UND Wallet-Drift).
  - R2-artiger Story-/NPC-Nachtrag bleibt Drift (keine Aufweichung).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
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

from mmo_sim.domain.zeitriss import save_correction as sc  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation as sv  # noqa: E402

from _full_v7_fixture import full_v7_save  # noqa: E402

EXPECTED = "CHR-REITHER-001"
WALLET_PATH = "/economy/wallets/CHR-REITHER-001"
CALLSIGN_PATH = "/characters/0/callsign"


def _draft_block() -> dict:
    """Vollstaendiger, sonst gueltiger v7-Save mit GENAU den beiden in R3
    belegten Schemafehlern (01_REVIEW_N2R3.md §1): Wallet als blanke Zahl
    unter `/economy/wallets/<id>` und `callsign: null`. Nutzt die bestehende
    Suite-Fixture, damit nur diese zwei Felder fehlerhaft sind."""
    block = full_v7_save(EXPECTED, name="Agnes Reither")
    block["characters"][0]["callsign"] = None
    block["economy"] = {"wallets": {EXPECTED: 100}}
    return block


def _error_paths(acc: sv.AcceptanceResult) -> set[str]:
    return {e.path for e in acc.structure.errors}


def test_a1_correction_message_carries_schema_derived_targets() -> None:
    block = _draft_block()
    acc = sv.validate_save_block(block, EXPECTED)
    assert not acc.accepted, "Der Entwurf muss abgelehnt sein (Wallet-Typ + null-Callsign)."
    msg = sc.build_correction_message(
        persona_key="p03_n2r4_restaurator", char_id=EXPECTED,
        operation_label="save_correction_creation:p03_n2r4_restaurator",
        acceptance=acc, original_block=block, attempt_no=1,
    )
    assert "Erwartete Zielstruktur" in msg, "Zielform-Abschnitt fehlt im Korrekturprompt."
    assert "`balance` (number)" in msg, "Schema-abgeleiteter balance-Hinweis fehlt."
    assert "ohne zusätzliche Felder" in msg, "additionalProperties:false-Hinweis fehlt."
    assert "leere Zeichenkette" in msg, "Leerer-Callsign-Hinweis fehlt."
    # Kein cu-Whitelisting in der an die SL gesendeten Anweisung (nur der
    # unveraenderte DATEN-Block darunter darf den Originalwert zeigen).
    instruction = msg.split("Unveränderter betroffener Entwurf", 1)[0]
    assert "cu" not in instruction.lower().split(), "Kein cu-Whitelisting im Prompt."


def test_a2_correct_balance_and_empty_callsign_is_valid_and_driftfree() -> None:
    block = _draft_block()
    error_paths = _error_paths(sv.validate_save_block(block, EXPECTED))
    corrected = copy.deepcopy(block)
    corrected["economy"]["wallets"][EXPECTED] = {"balance": 100}
    corrected["characters"][0]["callsign"] = ""
    acc = sv.validate_save_block(corrected, EXPECTED)
    assert acc.accepted, f"Die schema-korrekte Zielform muss angenommen werden: {acc.feedback_items}"
    drift = sc.detect_unjustified_drift(block, corrected, error_paths)
    assert drift == [], f"Die reine Schemareparatur darf KEINE Drift sein: {drift}"


def test_a3_cu_object_stays_rejected_and_is_wallet_drift() -> None:
    block = _draft_block()
    error_paths = _error_paths(sv.validate_save_block(block, EXPECTED))
    corrected = copy.deepcopy(block)
    corrected["economy"]["wallets"][EXPECTED] = {"cu": 100}
    corrected["characters"][0]["callsign"] = ""
    acc = sv.validate_save_block(corrected, EXPECTED)
    assert not acc.accepted, "{cu:100} verletzt required balance + additionalProperties:false."
    drift = sc.detect_unjustified_drift(block, corrected, error_paths)
    assert drift, "Ein verschwindender Wallet-Betrag unter cu muss Drift bleiben."
    assert any(d[0].startswith(WALLET_PATH) for d in drift), f"Wallet-Pfad-Drift erwartet: {drift}"


def test_a4_story_npc_backfill_stays_drift() -> None:
    block = _draft_block()
    error_paths = _error_paths(sv.validate_save_block(block, EXPECTED))
    corrected = copy.deepcopy(block)
    corrected["economy"]["wallets"][EXPECTED] = {"balance": 100}
    corrected["characters"][0]["callsign"] = ""
    corrected["continuity"]["npc_roster"].append({"id": "NPC-NEW-999", "name": "Erfunden"})
    corrected["characters"][0]["history"] = {"milestones": ["erfundener Meilenstein"]}
    drift = sc.detect_unjustified_drift(block, corrected, error_paths)
    assert drift, "Hinzuerfundene NPC/History muss Drift bleiben (kein Backfill)."
    assert any("npc_roster" in d[0] or "milestones" in d[0] for d in drift), drift


def test_a5_unknown_path_yields_no_spurious_hint() -> None:
    """Robustheit: ein Fehlerpfad ohne navigierbaren Schemaknoten erzeugt
    keinen erfundenen Zielhinweis (nur tatsaechlich auflösbare Pfade)."""
    assert sc._schema_node_for_path("/nicht/im/schema/vorhanden") is None
    assert sc._describe_expected_shape(None) is None
    # Wallet-Knoten liefert deterministisch die Objekt/balance-Beschreibung.
    node = sc._schema_node_for_path(WALLET_PATH)
    shape = sc._describe_expected_shape(node)
    assert shape is not None and "balance" in shape and "Objekt" in shape, shape


def main() -> int:
    tests = [
        test_a1_correction_message_carries_schema_derived_targets,
        test_a2_correct_balance_and_empty_callsign_is_valid_and_driftfree,
        test_a3_cu_object_stays_rejected_and_is_wallet_drift,
        test_a4_story_npc_backfill_stays_drift,
        test_a5_unknown_path_yields_no_spurious_hint,
    ]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\nall {len(tests)} N2R4 save-correction schema-hint tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
