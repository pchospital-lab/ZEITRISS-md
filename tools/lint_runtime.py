#!/usr/bin/env python3
"""Runtime lint for ZEITRISS guard rails.
Offline-only; checks presence of critical strings/macros to prevent regressions."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Pattern


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def req(pattern: str | Pattern[str], text: str, msg: str, fails: List[str]) -> None:
    pat: Pattern[str] = re.compile(pattern, re.S) if isinstance(pattern, str) else pattern
    if not pat.search(text):
        print(f"[FAIL] {msg}")
        fails.append(msg)
    else:
        print(f"[ OK ] {msg}")


def main(argv: List[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    tk = load_text(root / "systems" / "toolkit-gpt-spielleiter.md")
    sv = load_text(root / "systems" / "gameflow" / "speicher-fortsetzung.md")

    fails: List[str] = []

    # Mission-Invarianten & Gates
    req(r"StartMission\([^\)]*type=\"core\"", tk, "StartMission: type core path", fails)
    req(r"scene_total\s*=\s*12", tk, "Core: 12 Szenen gesetzt", fails)
    req(r"scene_total\s*=\s*14", tk, "Rift: 14 Szenen gesetzt", fails)
    req(r"Boss-Encounter in Szene 10", tk, "Boss-Hook vorhanden", fails)
    req(r"campaign\.mission_in_episode in \[5,10\]", tk,
        "Core-Boss nur in Mission 5/10 erlaubt", fails)

    # DelayConflict & Finale
    req(r"DelayConflict\(\s*4\s*\)", tk, "DelayConflict(4) aktiv", fails)
    req(r"Finale blockiert", tk, "Finale-Guard-Text vorhanden", fails)

    # PRECISION-Validator
    req(r"SceneHeader\(", tk, "SceneHeader-Macro vorhanden", fails)
    req(r"Decision\(", tk, "Decision-Macro vorhanden", fails)
    req(r"PRECISION fehlend", tk, "PRECISION-Warnung vorhanden", fails)

    # Px-HUD
    req(r"Paradox[:\s]+[▓░]{5}", tk, "Px-Balken dargestellt", fails)
    req(r"TEMP", tk, "TEMP im HUD", fails)
    req(r"\+1 nach\s+\d", tk, "ETA bis nächster Px-Punkt", fails)

    # Seeds & Episode-Gate
    req(r"Paradox 5 erreicht", tk, "Px5-HUD Tag", fails)
    req(r"can_launch_rift", tk, "can_launch_rift Macro vorhanden", fails)
    req(r"episode_completed\s*=\s*true", tk, "Episodenabschluss markiert", fails)
    req(r"apply_rift_mods_next_episode", tk, "Episoden-Boni werden gequeued", fails)
    req(r"launch_rift", tk, "launch_rift Gate vorhanden", fails)

    # Artefakt-Gate
    req(r"artifact_allowed", tk, "Artefakt-Gate-Flag vorhanden", fails)
    req(r"campaign\.scene\s+not in\s+\[11,12,13\]", tk,
        "Artefakt nur in Szenen 11–13", fails)
    req(r"boss_defeated", tk, "Artefakt erst nach Boss", fails)
    req(r"d6\(\)\s*!=\s*6", tk, "Artefakt-Wurf 1W6==6 Gate", fails)

    # FR-Intervention
    req(r"FR-INTRV:", tk, "Fraktionsintervention HUD-Tag vorhanden", fails)

    # Signal & Comms
    req(r"validate_signal", tk, "Runtime Signal-Guard vorhanden", fails)
    req(r"Comms out of range", tk, "Comms-Reichweite Warnung vorhanden", fails)
    req(r"Jammer blockiert", tk, "Jammer-Block vorhanden", fails)

    # HQ Save Guard
    req(r"Speichern nur im HQ", sv, "HQ-only Save Guard erwähnt", fails)
    req(r"sys_used == state\.sys|state\.sys_used == state\.sys", sv,
        "Deterministik geprüft", fails)

    # Preserve/Trigger Marker
    req(r"campaign\.mode", tk, "Preserve/Trigger-Flag gesetzt", fails)
    req(r"preserve_pool|trigger_pool", tk, "Seed-Pools referenziert", fails)
    req(r"Briefing:\s*kleineres Übel sichern", tk,
        "Trigger-Pflichtsatz im Briefing", fails)

    print("\nSummary:", "OK" if not fails else f"{len(fails)} issue(s)")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())

