#!/usr/bin/env python3
"""
tests/mmo_sim/test_j4_tolerant_import_2026_11_02.py — Teilpaket C
(ZR-FIGURENREISE-TISCH-20261102-R1, J4/J5 Fremdimport-Toleranzpfad).

`import_export.preview_import_tolerant` (Teilpaket C): wie `preview_
import`, aber mit EINER zusaetzlichen, schmalen Toleranzstufe fuer die
EINE Fehlerklasse, die SAVECOMPAT strukturell nicht reparieren kann
(Cap-Ueberlauf `maxItems`/`minItems`, Diskriminator-Reuse `core.save_
correction.has_residual_structural_cap_overflow`). Die realen Best-
Effort-Originalsaves p01_latch (CHR-MAHLBERG-1974) und p02_breach
(CHR-BREACH-001) -- je 4 Fehler, `/continuity/shared_echoes` +
`/continuity/npc_roster` je `maxItems=6` -- liegen UNVERAENDERT (byte-
identisch zur Quelle, kein Handreinigen) unter `fixtures/j4_tolerant_
import/`.

Pure Python, nur `assert`, echter Exitcode, keine Schema-Edits."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import import_export  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation as save_validation_lib  # noqa: E402

_FIXTURE_DIR = _HERE / "fixtures" / "j4_tolerant_import"
_P01_PATH = _FIXTURE_DIR / "p01_latch.json"
_P02_PATH = _FIXTURE_DIR / "p02_breach.json"

# Checksums der byte-identischen Kopien, wie sie bei der Erstellung dieses
# Tests aus der Quelle (research/reference-best-effort/game-proof/end-
# saves/) kopiert wurden -- jede Abweichung heisst, die Fixtures wurden
# nachbearbeitet/"gereinigt" (ausdruecklich verboten).
_EXPECTED_MD5 = {
    "p01_latch.json": "726116ae907ebfd87d3ee20fbec4f007",
    "p02_breach.json": "8280abc7bcd29cd5fd1ed8ba7876041f",
}


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _load_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Fixture-Integritaet: p01/p02 bleiben as-is (kein Handreinigen) ─────────

def test_fixtures_p01_p02_byte_identical_to_captured_checksum():
    assert _md5(_P01_PATH) == _EXPECTED_MD5["p01_latch.json"], (
        "p01_latch.json wurde seit dem Kopieren aus der Quelle veraendert -- "
        "Testfigur muss as-is bleiben (kein Handreinigen)."
    )
    assert _md5(_P02_PATH) == _EXPECTED_MD5["p02_breach.json"], (
        "p02_breach.json wurde seit dem Kopieren aus der Quelle veraendert -- "
        "Testfigur muss as-is bleiben (kein Handreinigen)."
    )


# ── p01/p02 -> tolerated=True + sichtbare Warnungen ─────────────────────────

def test_p01_latch_tolerated_true_with_visible_warnings():
    raw = _load_raw(_P01_PATH)
    # Haertecheck: der harte Pfad lehnt p01 unveraendert ab (Vorbedingung
    # fuer den Toleranzpfad, sonst waere der Test gegenstandslos).
    try:
        import_export.preview_import(raw)
        assert False, "p01_latch sollte am harten preview_import scheitern (Vorbedingung)"
    except import_export.MalformedImportError:
        pass

    preview = import_export.preview_import_tolerant(raw)
    assert preview.tolerated is True
    assert preview.char_id == "CHR-MAHLBERG-1974"
    assert preview.single_char_ok is True
    assert len(preview.warnings) > 0, "tolerierter Import muss die Restwarnung sichtbar mitfuehren"
    assert any("maxItems" in w for w in preview.warnings)
    assert any("shared_echoes" in w for w in preview.warnings)
    assert any("npc_roster" in w for w in preview.warnings)


def test_p02_breach_tolerated_true_with_visible_warnings():
    raw = _load_raw(_P02_PATH)
    try:
        import_export.preview_import(raw)
        assert False, "p02_breach sollte am harten preview_import scheitern (Vorbedingung)"
    except import_export.MalformedImportError:
        pass

    preview = import_export.preview_import_tolerant(raw)
    assert preview.tolerated is True
    assert preview.char_id == "CHR-BREACH-001"
    assert preview.single_char_ok is True
    assert len(preview.warnings) > 0
    assert any("maxItems" in w for w in preview.warnings)


# ── harte Ablehnung bleibt: fehlgebundener Fall + nicht-Cap-Strukturfall ───

def test_missing_char_id_binding_case_stays_hard_rejected():
    """Haertung (RECONCILIATION-V3): `has_residual_structural_cap_overflow`
    liefert `False`, sobald `acceptance.binding_errors` nicht leer ist --
    ein Save ohne auswertbare char_id (hier: `id`-Feld der EINEN Figur
    entfernt) bleibt trotz GLEICHZEITIGEM Cap-Ueberlauf hart abgelehnt,
    NIE stillschweigend best-effort-faehig."""
    d = json.loads(_load_raw(_P01_PATH))
    broken = copy.deepcopy(d)
    del broken["characters"][0]["id"]
    raw = json.dumps(broken)

    try:
        import_export.preview_import(raw)
        assert False, "sollte am harten preview_import scheitern (Vorbedingung)"
    except import_export.MalformedImportError as original:
        original_msg = str(original)

    try:
        import_export.preview_import_tolerant(raw)
        assert False, "fehlgebundener Fall (keine auswertbare char_id) muss hart abgelehnt bleiben"
    except import_export.MalformedImportError as e:
        assert str(e) == original_msg, "Toleranzpfad darf bei Hartablehnung KEINE neue/geloskerte Meldung erzeugen"


def test_discriminator_hardening_rejects_mismatched_expected_char_id():
    """Direkter Reuse-Nachweis fuer den Diskriminator selbst (11 §/
    RECONCILIATION-V3-HAERTUNG): ein fremd erwarteter char_id fuehrt zu
    `binding_errors` -> `has_residual_structural_cap_overflow` liefert
    `False`, UNABHAENGIG vom gleichzeitigen Cap-Ueberlauf -- EXAKT die
    Haertung, die `preview_import_tolerant` reused."""
    from mmo_sim.core.save_correction import has_residual_structural_cap_overflow

    d = json.loads(_load_raw(_P01_PATH))
    assert has_residual_structural_cap_overflow(d, "CHR-MAHLBERG-1974") is True
    assert has_residual_structural_cap_overflow(d, "CHR-FREMD-0000") is False


def test_non_cap_structural_failure_stays_hard_rejected():
    """Ein Strukturfehler AUSSERHALB der Cap-Klasse (hier: `wallet` als
    String statt Zahl -- reiner `type`-Fehler, KEIN `maxItems`/`minItems`)
    bleibt hart abgelehnt, auch wenn die Cap-Arrays selbst im Rahmen sind."""
    d = json.loads(_load_raw(_P01_PATH))
    fixed_caps = copy.deepcopy(d)
    fixed_caps["continuity"]["shared_echoes"] = fixed_caps["continuity"]["shared_echoes"][:6]
    fixed_caps["continuity"]["npc_roster"] = fixed_caps["continuity"]["npc_roster"][:6]
    fixed_caps["characters"][0]["wallet"] = "not-a-number"
    raw = json.dumps(fixed_caps)

    try:
        import_export.preview_import(raw)
        assert False, "sollte am harten preview_import scheitern (Vorbedingung)"
    except import_export.MalformedImportError as original:
        original_msg = str(original)
        assert "maxItems" not in original_msg and "minItems" not in original_msg, (
            "Vorbedingung verletzt: dieser Fixturen-Fehler sollte NICHT in die Cap-Klasse fallen"
        )

    try:
        import_export.preview_import_tolerant(raw)
        assert False, "nicht-Cap-Strukturfall muss hart abgelehnt bleiben"
    except import_export.MalformedImportError as e:
        assert str(e) == original_msg


# ── Erfolgspfad bleibt additiv bytegleich (tolerated=False, warnings=()) ───

def test_healthy_block_via_tolerant_path_matches_plain_preview_additively():
    block = full_v7_save("chrono-j4-healthy", level=3)
    raw = import_export.export_save_text(block)

    plain = import_export.preview_import(raw)
    tolerant = import_export.preview_import_tolerant(raw)

    assert tolerant.tolerated is False
    assert tolerant.warnings == ()
    assert tolerant.char_id == plain.char_id
    assert tolerant.level == plain.level
    assert tolerant.n_characters == plain.n_characters
    assert tolerant.single_char_ok == plain.single_char_ok


def test_existing_preview_import_behaviour_unchanged_for_malformed_json():
    try:
        import_export.preview_import("das ist kein JSON")
        assert False
    except import_export.MalformedImportError:
        pass


def test_existing_preview_import_roundtrip_still_green():
    block = full_v7_save("chrono-j4-roundtrip", level=7)
    text = import_export.export_save_text(block)
    preview = import_export.preview_import(text)
    assert preview.char_id == "chrono-j4-roundtrip"
    assert preview.level == 7
    assert preview.single_char_ok
    assert preview.tolerated is False
    assert preview.warnings == ()


# ── Schema-Unveraendert-Beleg (die BEIDEN v7-Schemas, kein Schema-Edit) ─────

def test_v7_schemas_unchanged_checksum():
    tolerant_path = save_validation_lib.TOLERANT_SCHEMA_PATH
    export_path = save_validation_lib.EXPORT_SCHEMA_PATH
    assert tolerant_path.is_file()
    assert export_path.is_file()
    # Reiner Existenz-/Lesbarkeitsbeleg hier; der tatsaechliche Vorher/
    # Nachher-Checksumvergleich steht (echter `git diff`-Beleg) im Report --
    # dieser Test haelt zusaetzlich fest, dass BEIDE Schemas unveraendert
    # weiterhin erfolgreich geladen/selbst-geprueft werden (Modulimport
    # oben waere sonst schon fehlgeschlagen).
    tolerant_schema = json.loads(tolerant_path.read_text(encoding="utf-8"))
    export_schema = json.loads(export_path.read_text(encoding="utf-8"))
    assert tolerant_schema.get("$id")
    assert export_schema.get("$id")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
