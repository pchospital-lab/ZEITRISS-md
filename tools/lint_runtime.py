#!/usr/bin/env python3
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True

tk = (ROOT/"systems"/"toolkit-gpt-spielleiter.md").read_text(encoding="utf-8")
sv = (ROOT/"systems"/"gameflow"/"speicher-fortsetzung.md").read_text(encoding="utf-8")

def req(pattern, text, msg):
    global ok
    if not re.search(pattern, text, re.S):
        print(f"[FAIL] {msg}")
        ok = False
    else:
        print(f"[ OK ] {msg}")

# Mission-Invarianten & Gates
req(r"StartMission\([^\)]*type=\"core\"", tk, "StartMission: type core path")
req(r"scene_total\s*=\s*12", tk, "Core: 12 Szenen gesetzt")
req(r"scene_total\s*=\s*14", tk, "Rift: 14 Szenen gesetzt")
req(r"Boss-Encounter in Szene 10", tk, "Boss-Hook vorhanden")
req(r"campaign\.mission_in_episode in \[5,10\]", tk,
    "Core-Boss nur in Mission 5/10 erlaubt")

# DelayConflict & Finale
req(r"DelayConflict\(\s*4\s*\)", tk, "DelayConflict(4) aktiv")
req(r"Finale blockiert", tk, "Finale-Guard-Text vorhanden")

# PRECISION-Validator
req(r"SceneHeader\(", tk, "SceneHeader-Macro vorhanden")
req(r"Decision\(", tk, "Decision-Macro vorhanden")
req(r"PRECISION fehlend", tk, "PRECISION-Warnung vorhanden")

# Px-HUD
req(r"Paradox[:\s]+[▓░]{5}", tk, "Px-Balken dargestellt")
req(r"TEMP", tk, "TEMP im HUD")
req(r"\+1 nach\s+\d", tk, "ETA bis nächster Px-Punkt")

# Seeds & Episode-Gate
req(r"Paradox 5 erreicht", tk, "Px5-HUD Tag")
req(r"can_launch_rift", tk, "can_launch_rift Macro vorhanden")
req(r"episode_completed\s*=\s*true", tk, "Episodenabschluss markiert")
req(r"apply_rift_mods_next_episode", tk, "Episoden-Boni werden gequeued")
req(r"launch_rift", tk, "launch_rift Gate vorhanden")

# Artefakt-Gate
req(r"artifact_allowed", tk, "Artefakt-Gate-Flag vorhanden")
req(r"campaign\.scene\s+not in\s+\[11,12,13\]", tk,
    "Artefakt nur in Szenen 11–13")
req(r"boss_defeated", tk, "Artefakt erst nach Boss")
req(r"d6\(\)\s*!=\s*6", tk, "Artefakt-Wurf 1W6==6 Gate")

# FR-Intervention
req(r"FR-INTRV:", tk, "Fraktionsintervention HUD-Tag vorhanden")

# Signal & Comms
req(r"validate_signal", tk, "Runtime Signal-Guard vorhanden")
req(r"Comms out of range", tk, "Comms-Reichweite Warnung vorhanden")
req(r"Jammer blockiert", tk, "Jammer-Block vorhanden")

# HQ Save Guard
req(r"Speichern nur im HQ", sv, "HQ-only Save Guard erwähnt")
req(r"sys_used == state\.sys|state\.sys_used == state\.sys", sv,
    "Deterministik geprüft")

# Preserve/Trigger Marker
req(r"campaign\.mode", tk, "Preserve/Trigger-Flag gesetzt")
req(r"preserve_pool|trigger_pool", tk, "Seed-Pools referenziert")
req(r"Briefing:\s*kleineres Übel sichern", tk,
    "Trigger-Pflichtsatz im Briefing")

sys.exit(0 if ok else 1)
