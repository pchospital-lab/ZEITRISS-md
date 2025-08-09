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

# DelayConflict & Finale
req(r"DelayConflict\(\s*4\s*\)", tk, "DelayConflict(4) aktiv")
req(r"Finale blockiert", tk, "Finale-Guard-Text vorhanden")

# PRECISION-Validator
req(r"SceneHeader\(", tk, "SceneHeader-Macro vorhanden")
req(r"Decision\(", tk, "Decision-Macro vorhanden")
req(r"PRECISION fehlend", tk, "PRECISION-Warnung vorhanden")

# Paradox/Seeds/Artifacts
req(r"Paradox 5 erreicht", tk, "Px5-HUD Tag")
req(r"apply_rift_mods_next_episode", tk, "Episoden-Boni Macro vorhanden")
req(r"launch_rift", tk, "launch_rift Gate vorhanden")
req(r"artifact_allowed", tk, "Artefakt-Gate-Flag vorhanden")

# Signal & Comms
req(r"validate_signal", tk, "Runtime Signal-Guard vorhanden")
req(r"Comms out of range", tk, "Comms-Reichweite Warnung vorhanden")

# HQ Save Guard
req(r"Speichern nur im HQ", sv, "HQ-only Save Guard erwähnt")
req(r"sys_used == state\.sys|state\.sys_used == state\.sys", sv, "Deterministik geprüft")

sys.exit(0 if ok else 1)
