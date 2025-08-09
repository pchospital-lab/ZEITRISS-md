#!/usr/bin/env python3
"""Arena lint: checks presence of runtime guards, HUD backticks, actions & anchors."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
TK = (ROOT/"systems"/"toolkit-gpt-spielleiter.md").read_text(encoding="utf-8")

def ok(pat, msg):
    if not re.search(pat, TK, re.S):
        print(f"[FAIL] {msg}"); return False
    print(f"[ OK ] {msg}"); return True

all_ok = True
all_ok &= ok(r"LINT:ARENA_MODULE", "LINT anchors present (ARENA_MODULE)")
all_ok &= ok(r"LINT:ARENA_GUARDS", "Guards anchor present")
all_ok &= ok(r"LINT:ARENA_NO_SEEDS", "Seeds suppressed in arena")
all_ok &= ok(r"LINT:ARENA_NO_PARADOX", "Paradox frozen in arena")
all_ok &= ok(r"LINT:ARENA_NO_BOSS", "Boss suppressed in arena")
all_ok &= ok(r"LINT:ARENA_NO_FR_INTERVENTION", "FR intervention suppressed")
all_ok &= ok(r"arena_action\(", "ArenaAction macro exists")
all_ok &= ok(r"Aktion blockiert – Gerät angeben", "Device requirement text present")
all_ok &= ok(r"Jammer aktiv", "Jammer action present")
all_ok &= ok(r"ARENA·", "Arena HUD label present")
all_ok &= ok(r"`.*ARENA", "HUD overlay is in backticks")

raise SystemExit(0 if all_ok else 1)
