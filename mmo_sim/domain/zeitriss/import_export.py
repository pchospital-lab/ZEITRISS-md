#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/import_export.py — Import mit Vorschau/Konflikt,
Export als eigenstaendige Datei (11 §§4-5, M2, A18/A19/A20).

Vier Zielzuordnungsfaelle (11 §5):
  1. Unbekannte Char-ID -> als eigene Figur registrieren.
  2. Bekannte Char-ID, identischer Save -> idempotent, No-op.
  3. Bekannte Char-ID, abweichender Save -> Vorschau + ausdrueckliche Wahl.
  4. Fremde Zuordnung/aktive Bindung/offener Auftrag -> parken, keine
     Uebernahme.

Kein eigenstaendiger Migrationsregelbau — reine Struktur-/Ownership-Pruefung,
keine Regeltreue-Bewertung (die bleibt ZEITRISS/KI-SL vorbehalten, s. 11 §5).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from . import save_validation as save_validation_lib
from . import saves as save_lib


class MalformedImportError(ValueError):
    pass


@dataclass
class ImportPreview:
    char_id: str | None
    level: int | None
    n_characters: int
    single_char_ok: bool
    source_label: str = "extern importiert"


def preview_import(raw_text: str) -> ImportPreview:
    """Rein STRUKTURELLE Pruefung (11 §5: 'beweist keine Regeltreue einer
    extern gespielten Karriere'). Wirft `MalformedImportError` bei
    unbekanntem Schema/unvollstaendigem Block — KEIN Teil-Progress-Write.

    R12-Fix (01_AUFTRAG_SAVEGATE.md §E "ungueltiger eigener Import wird vor
    Write gesperrt", SC16): vorher pruefte diese Funktion nur die milden
    Bedingungen (v==7/'characters' vorhanden/genau 1 Figur) -- ein Block,
    der diese drei erfuellt, aber gegen die vollen v7-Schemas verstoesst
    (z.B. Wallet als blanke Zahl statt Objekt, ungueltiges campaign.mode),
    lief bisher unverfaengig durch `preview_import` und erreichte danach
    `catalog.store_figure_save` (bereits EIN Write), bevor die milde
    `ZeitrissHarvestValidator`-Pruefung in `onboarding.complete_with_save`
    ihn (jetzt, nach dem R12-Policy-Fix) ungefangen als `ValueError`
    zurueckwies. Die volle Schemapruefung (`save_validation.
    validate_structure`) laeuft deshalb HIER, VOR jedem Write, und nutzt
    dieselbe bestehende `MalformedImportError`-Flucht -- `ui/tui.py`s
    bereits vorhandener `except import_export.MalformedImportError`-Zweig
    (kein neuer UI-Pfad) zeigt den Korrekturhinweis lokal an und bricht
    kontrolliert ab (kein Write, kein automatischer SL-Auftrag)."""
    try:
        obj = json.loads(raw_text)
    except (json.JSONDecodeError, ValueError) as e:
        raise MalformedImportError(f"kein gueltiges JSON: {e}") from e
    if not isinstance(obj, dict) or obj.get("v") != 7 or "characters" not in obj:
        raise MalformedImportError("kein erkennbares v7-Save-Schema (fehlt 'v':7 oder 'characters').")
    n = save_lib.single_character_count(obj)
    if n != 1:
        raise MalformedImportError(
            f"Import erwartet genau EINEN Personal-Save (1 Figur), gefunden: {n}. "
            f"Sammelbloecke muessen ueber den bestehenden ZEITRISS-Exportweg einzeln geliefert werden."
        )
    structure = save_validation_lib.validate_structure(obj)
    if not structure.valid:
        hint = "; ".join(structure_error for structure_error in (
            f"{e.schema}:{e.path} ({e.check})" for e in structure.errors[:8]
        ))
        more = "" if not structure.truncated else f" (+{structure.total_error_count - len(structure.errors)} weitere)"
        raise MalformedImportError(
            f"Save erfuellt nicht die vollen v7-Schemas (kein Write): {hint}{more}."
        )
    cid = save_lib.block_char_id(obj)
    level = None
    chars = obj.get("characters")
    if isinstance(chars, list) and chars and isinstance(chars[0], dict):
        # W45: das echte v7-Schema fuehrt das Figurenlevel unter `lvl`
        # (saveGame.v7.export.schema.json, Pflichtfeld) -- `level` wurde
        # nie vom Schema verlangt, nur von schmalen Legacy-Testfixtures
        # zufaellig mitgefuehrt; `lvl` hat Vorrang, `level` bleibt Fallback.
        level = chars[0].get("lvl", chars[0].get("level"))
    return ImportPreview(char_id=cid, level=level, n_characters=n, single_char_ok=True)


@dataclass
class ImportDecision:
    action: str  # "register_new" | "noop_identical" | "adopt_incoming" | "keep_existing" | "parked"
    reason: str
    block: dict | None = None


def resolve_import(
    incoming_block: dict, known_char_ids: set[str],
    existing_block_for_char_id: dict | None,
    active_binding: bool, open_completion_order: bool,
    explicit_choice: str | None = None,
) -> ImportDecision:
    """Vier Faelle aus 11 §5. `explicit_choice` ('adopt_incoming' |
    'keep_existing') wird NUR fuer Fall 3 (abweichender Stand) gebraucht —
    ohne explizite Wahl bleibt der Import geparkt (kein automatisches
    Hochleveln/Mischen)."""
    cid = save_lib.block_char_id(incoming_block)
    if active_binding or open_completion_order:
        return ImportDecision(
            action="parked",
            reason="Aktive Tischbindung oder offener Abschlussauftrag — Import als nicht aktivierte Eingangsdatei geparkt.",
        )
    if cid not in known_char_ids:
        return ImportDecision(action="register_new", reason="Unbekannte Char-ID — als neue Figur registriert.", block=incoming_block)
    if existing_block_for_char_id == incoming_block:
        return ImportDecision(action="noop_identical", reason="Identischer Save bereits vorhanden — kein zweiter Fortschritt.")
    # Fall 3: abweichender Stand.
    if explicit_choice == "adopt_incoming":
        return ImportDecision(action="adopt_incoming", reason="Ausdrueckliche Wahl: importierter Stand wird aktiv.", block=incoming_block)
    if explicit_choice == "keep_existing":
        return ImportDecision(action="keep_existing", reason="Ausdrueckliche Wahl: bisheriger Stand bleibt aktiv.", block=existing_block_for_char_id)
    return ImportDecision(
        action="parked",
        reason="Bekannte Char-ID mit abweichendem Save — wartet auf ausdrueckliche Konfliktwahl (keine automatische Mischung/Hochlevelung).",
    )


def export_save_text(save_block: dict) -> str:
    """Vollstaendiger ZEITRISS-Save als eigenstaendiger, lesbarer JSON-Text —
    kein Harness-Wrapper, kein Auth-Token, kein privater Persona-State (11 §4)."""
    return json.dumps(save_block, ensure_ascii=False, indent=2)
