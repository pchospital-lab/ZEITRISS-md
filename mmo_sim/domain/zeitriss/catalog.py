#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/catalog.py — Mehrfiguren-Katalog pro Teilnehmer
(11 §6, M2, A21).

"Die stabile Teilnehmeridentitaet ist NICHT die Char-ID." Ein Teilnehmer kann
mehrere Chrononauten besitzen; pro Teilnahme wird GENAU EINE Figur explizit
gebunden, stabil fuer den Abschnitt. Ein Wechsel geht nur an einer sauberen
Abschnittsgrenze (kein Wechsel bei offenem Abschluss-Auftrag)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class ActiveBindingError(RuntimeError):
    """Ein Wechsel waehrend eines offenen Abschnitts ist nicht erlaubt."""


@dataclass
class CatalogEntry:
    participant_id: str
    chrononaut_id: str
    persona_key: str
    display_name: str = ""


def _path(catalog_dir: Path, participant_id: str) -> Path:
    safe = participant_id.replace("/", "_")
    return catalog_dir / f"catalog__{safe}.json"


def _load(path: Path) -> dict:
    if not path.exists():
        return {"entries": [], "last_selected_chrononaut_id": None, "active_chrononaut_id": None}
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def register(catalog_dir: str | Path, entry: CatalogEntry) -> None:
    """Fuegt eine Figur zum Katalog eines Teilnehmers hinzu — kein
    Neu-Einfuegen bei jedem Start (11 §6: 'nicht bei jedem Start neu
    einfuegen'), idempotent bei bereits vorhandener chrononaut_id."""
    catalog_dir = Path(catalog_dir)
    path = _path(catalog_dir, entry.participant_id)
    data = _load(path)
    if not any(e["chrononaut_id"] == entry.chrononaut_id for e in data["entries"]):
        data["entries"].append(entry.__dict__)
    _write(path, data)


def list_for_participant(catalog_dir: str | Path, participant_id: str) -> list[CatalogEntry]:
    data = _load(_path(Path(catalog_dir), participant_id))
    return [CatalogEntry(**e) for e in data["entries"]]


def bind_for_section(catalog_dir: str | Path, participant_id: str, chrononaut_id: str, has_open_section: bool) -> None:
    """Bindet die aktive Figur fuer den Abschnitt. Wirft `ActiveBindingError`,
    wenn bereits eine ANDERE Figur mit offenem Abschnitt aktiv ist — ein
    Charakterwechsel darf einen offenen Abschluss nicht umgehen (11 §6)."""
    catalog_dir = Path(catalog_dir)
    path = _path(catalog_dir, participant_id)
    data = _load(path)
    active = data.get("active_chrononaut_id")
    if has_open_section and active is not None and active != chrononaut_id:
        raise ActiveBindingError(
            f"Teilnehmer {participant_id!r} hat einen offenen Abschnitt mit Figur {active!r} — "
            f"kein Wechsel zu {chrononaut_id!r} vor sauberer Abschnittsgrenze."
        )
    data["active_chrononaut_id"] = chrononaut_id
    data["last_selected_chrononaut_id"] = chrononaut_id
    _write(path, data)


def last_selected(catalog_dir: str | Path, participant_id: str) -> str | None:
    """Komfortabler Default beim Restart (11 §6)."""
    data = _load(_path(Path(catalog_dir), participant_id))
    return data.get("last_selected_chrononaut_id")


def active_chrononaut_id(catalog_dir: str | Path, participant_id: str) -> str | None:
    """R11-Restintegrationsfix (WEGKARTE §4 A2): oeffentlicher Lesezugriff
    auf die aktuell AKTIVE Figurbindung -- `ui/tui.py:_cmd_import` prueft
    damit vor einer Aktivierung, ob der Teilnehmer bereits eine ANDERE
    Figur aktiv gebunden hat (nicht nur, ob die EINGEHENDE Char-ID selbst
    gesperrt ist)."""
    data = _load(_path(Path(catalog_dir), participant_id))
    return data.get("active_chrononaut_id")


def release_active(catalog_dir: str | Path, participant_id: str) -> None:
    catalog_dir = Path(catalog_dir)
    path = _path(catalog_dir, participant_id)
    data = _load(path)
    data["active_chrononaut_id"] = None
    _write(path, data)


# W4 (F4, PLAN-CRITIC.md Auflage 4, MAIN-ENTSCHEIDUNG.md Punkt 4, Test 07
# review_p2w_boundaries.py): getrennte Persistenz fuer JEDE registrierte
# Figur, geschluesselt ueber (participant_id, chrononaut_id) -- ZUSAETZLICH
# zum bestehenden Single-Slot-Store der AKTIVEN Figur (`core/store.py:
# load_current_save`/`publish_current_save`, ausschliesslich nach
# `persona_key`==`participant_id` geschluesselt, EIN Slot pro Teilnehmer)
# und zum Onboarding-`final_save` (`onboarding.py`, EIN Slot pro
# Teilnehmer fuer den GERADE aktiven Erschaffungs-/Importauftrag). Weder
# der Single-Slot-Store noch das Onboarding werden hier dupliziert oder
# umgewidmet -- diese Funktionen sind eine ZUSAETZLICHE, eigene
# Persistenz einzig fuer "jede registrierte Figur behaelt ihre eigenen
# Savebytes, auch wenn sie gerade inaktiv ist".


def _figure_save_path(catalog_dir: Path, participant_id: str, chrononaut_id: str) -> Path:
    safe_p = participant_id.replace("/", "_")
    safe_c = chrononaut_id.replace("/", "_")
    return catalog_dir / "figures" / f"{safe_p}__{safe_c}.json"


def store_figure_save(catalog_dir: str | Path, participant_id: str, chrononaut_id: str, save_block: dict) -> None:
    """Persistiert die v7-Savebytes EINER registrierten Figur -- unabhaengig
    davon, ob sie gerade aktiv ist. Aufrufer: jede Stelle, die eine Figur
    real registriert (Import, Erschaffung), damit ein SPAETERER Import/eine
    spaetere Erschaffung einer ANDEREN Figur diese Bytes nicht mehr
    ueberschreiben kann (vorheriger Bug: `onboarding.final_save` als
    einziger Speicherort wurde bei jedem neuen Import ueberschrieben)."""
    path = _figure_save_path(Path(catalog_dir), participant_id, chrononaut_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(save_block, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_figure_save(catalog_dir: str | Path, participant_id: str, chrononaut_id: str) -> dict | None:
    """Liest die persistierten Savebytes einer registrierten Figur zurueck,
    `None` wenn (noch) keine hinterlegt sind (z.B. Katalogeintrag aus einer
    Zeit vor diesem Fix)."""
    path = _figure_save_path(Path(catalog_dir), participant_id, chrononaut_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
