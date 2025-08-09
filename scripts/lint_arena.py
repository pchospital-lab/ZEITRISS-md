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
for tag in [
    "LINT:ARENA_SNAPSHOT","LINT:ARENA_RESTORE","LINT:ARENA_BLOCK_SAVE",
    "LINT:ARENA_SINGLE_INSTANCE","LINT:ARENA_AFK_GUARD",
    "LINT:ARENA_BUDGET","LINT:ARENA_PSI_HINT","LINT:ARENA_COMMS_REUSE",
    "LINT:ARENA_CAMPAIGN_SNAP","LINT:ARENA_ABORT","LINT:ARENA_LOG"
]:
    all_ok &= ok(tag, f"{tag} present")
for tag in [
  r"LINT:ARENA_TIEBREAK",
  r"LINT:ARENA_RULE_PENALTY",
  r"LINT:ARENA_MODE_CONTROL",
  r"LINT:ARENA_MODE_ELIMINATION",
]:
    all_ok &= ok(tag, f"{tag} present")
all_ok &= ok(r"arena_action\(", "ArenaAction macro exists")
all_ok &= ok(r"Aktion blockiert – Gerät angeben", "Device requirement text present")
all_ok &= ok(r"Jammer aktiv", "Jammer action present")
all_ok &= ok(r"ARENA·", "Arena HUD label present")
all_ok &= ok(r"`.*ARENA", "HUD overlay is in backticks")
all_ok &= ok(r"PHASE:", "Arena HUD displays phase tag")

def assert_no_anchor_in_output_context(text, label):
    for i, line in enumerate(text.splitlines(), 1):
        if "LINT:" in line and ("`" in line or "hud_tag(" in line):
            print(f"[FAIL] {label}: LINT anchor leaked at line {i}")
            return False
    return True

all_ok &= assert_no_anchor_in_output_context(TK, "toolkit")

raise SystemExit(0 if all_ok else 1)
