#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mmo_sim/ui/onboarding_prefs.py — getrennte UI-Praeferenzdatei (UX02, 02 §B).

NICHT Teil des v7-Saves und NICHT Teil von `domain/zeitriss/onboarding.py`s
Erschaffungs-Scratch (`onboarding__<id>.json`) -- eine eigene, kleine JSON-
Datei unter dem lokalen Datenroot (`<onboarding_dir>.parent/ui_prefs.json`),
die NUR Anzeige-/Erstfuehrungspraeferenzen haelt. Kein fachliches Feld, keine
Figur-/Katalog-/Requestledger-Beruehrung.

02 §B (verbindlich): "Ein fehlender/defekter Praeferenzwert darf keine Figur
verlieren, keine Population anlegen und keinen Spielzug ausloesen." Deshalb
ist jede Funktion hier fail-soft -- ein kaputtes/unlesbares `ui_prefs.json`
fuehrt NIE zu einer Exception nach aussen, nur zum sicheren Default (Fuehrung
wird dann erneut gezeigt, sonst nichts)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UiPrefs:
    tutorial_seen: bool = False


def _path(data_root: str | Path, participant_id: str | None = None) -> Path:
    # R9 (C-K2, UX02, Korrekturzyklus 1): OHNE `participant_id` bleibt EINE
    # gemeinsame Datei pro `data_root` (unveraendertes Verhalten,
    # rueckwaertskompatibel zu allen bestehenden Aufrufern/Tests ohne
    # dieses Argument). MIT `participant_id` (so ruft `ui/tui.py` jetzt
    # auf) bekommt JEDE Person ihre EIGENE Praeferenzdatei -- vorher lag
    # `ui_prefs.json` IMMER gemeinsam pro `data_root`, nicht pro Person;
    # eine neu registrierte zweite Person auf demselben Geraet sah die
    # Erstfuehrung dadurch NIE (die global erste Person hatte sie bereits
    # "gesehen"). Reine Pfadwahl, dieselbe fail-soft-Semantik fuer beide
    # Faelle.
    if participant_id is None:
        return Path(data_root) / "ui_prefs.json"
    safe = participant_id.replace("/", "_")
    return Path(data_root) / f"ui_prefs__{safe}.json"


def load(data_root: str | Path, participant_id: str | None = None) -> UiPrefs:
    """Reine Lesefunktion. Fehlende/defekte Datei -> sicherer Default,
    NIEMALS eine Exception (02 §B)."""
    p = _path(data_root, participant_id)
    if not p.exists():
        return UiPrefs()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return UiPrefs()
        return UiPrefs(tutorial_seen=bool(data.get("tutorial_seen", False)))
    except (OSError, ValueError, TypeError):
        return UiPrefs()


def mark_tutorial_seen(data_root: str | Path, participant_id: str | None = None) -> None:
    """Best-effort-Write (wie `lobby_service.append_offer_log_record`):
    ein fehlgeschlagener Write hier darf NIE den Programmfluss stoppen oder
    irgendeine Figur-/Katalogdatei beruehren -- im schlimmsten Fall wird die
    Fuehrung beim naechsten Start erneut gezeigt, das ist der einzige
    Nebeneffekt (02 §B: kein Datenverlust durch einen Praeferenzfehler)."""
    p = _path(data_root, participant_id)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps({"tutorial_seen": True}), encoding="utf-8")
        tmp.replace(p)
    except OSError:
        pass
