#!/usr/bin/env python3
"""Offline runtime lint for ZEITRISS guard rails."""

from __future__ import annotations

import re
from pathlib import Path

# Import helpers; rely on PYTHONPATH or fallback to repo root
try:
    from scripts.lib_repo import repo_root, read_text, get_logger
except Exception:  # pragma: no cover - fallback for direct calls
    import sys
    _root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(_root))
    from scripts.lib_repo import repo_root, read_text, get_logger  # type: ignore

log = get_logger("lint_runtime")


def req(pattern: str | re.Pattern[str], text: str, msg: str, fails: list[str]) -> None:
    pat: re.Pattern[str] = re.compile(pattern, re.S) if isinstance(pattern, str) else pattern
    if not pat.search(text):
        log.error("[FAIL] %s", msg)
        fails.append(msg)
    else:
        log.info("[ OK ] %s", msg)


def main() -> int:
    root = repo_root(Path(__file__))
    fails: list[str] = []

    try:
        tk = read_text(root / "systems" / "toolkit-gpt-spielleiter.md")
    except FileNotFoundError as e:
        log.error(str(e))
        fails.append(str(e))
        tk = ""

    try:
        sv = read_text(root / "systems" / "gameflow" / "speicher-fortsetzung.md")
    except FileNotFoundError as e:
        log.error(str(e))
        fails.append(str(e))
        sv = ""

    # Mission-Invarianten & Gates
    req(r"StartMission\([^\)]*type=\"core\"", tk, "StartMission: type core path", fails)
    req(r"scene_total\s*=\s*12", tk, "Core: 12 Szenen gesetzt", fails)
    req(r"scene_total\s*=\s*14", tk, "Rift: 14 Szenen gesetzt", fails)
    req(r"LINT:BOSS_SCENE10_RIFT", tk, "Boss-Hook vorhanden", fails)
    req(r"LINT:CORE_BOSS_M05_M10", tk, "Core-Boss nur in Mission 5/10 erlaubt", fails)

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
    req(r"LINT:PX5_SEED_GATE", tk, "Px5-HUD Tag", fails)
    req(r"can_launch_rift", tk, "can_launch_rift Macro vorhanden", fails)
    req(r"episode_completed\s*=\s*true", tk, "Episodenabschluss markiert", fails)
    req(r"apply_rift_mods_next_episode", tk, "Episoden-Boni werden gequeued", fails)
    req(r"launch_rift", tk, "launch_rift Gate vorhanden", fails)

    # Artefakt-Gate
    req(r"artifact_allowed", tk, "Artefakt-Gate-Flag vorhanden", fails)
    req(r"LINT:RIFT_ARTIFACT_11_13_D6", tk, "Artefakt-Gate-Block vorhanden", fails)

    # FR-Intervention
    req(r"LINT:FR_INTERVENTION", tk, "Fraktionsintervention HUD-Tag vorhanden", fails)

    # Signal & Comms
    req(r"validate_signal", tk, "Runtime Signal-Guard vorhanden", fails)
    req(r"Comms out of range", tk, "Comms-Reichweite Warnung vorhanden", fails)
    req(r"Jammer blockiert", tk, "Jammer-Block vorhanden", fails)

    # HQ Save Guard
    req(r"LINT:HQ_ONLY_SAVE", sv, "HQ-only Save Guard erwähnt", fails)
    req(r"sys_used == state\.sys|state\.sys_used == state\.sys", sv, "Deterministik geprüft", fails)

    # Preserve/Trigger Marker
    req(r"campaign\.mode", tk, "Preserve/Trigger-Flag gesetzt", fails)
    req(r"preserve_pool|trigger_pool", tk, "Seed-Pools referenziert", fails)
    req(r"Briefing:\s*kleineres Übel sichern", tk, "Trigger-Pflichtsatz im Briefing", fails)

    log.log(25, "Summary: %s", "OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
