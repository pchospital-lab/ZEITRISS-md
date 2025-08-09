#!/usr/bin/env python3
"""Chronopolis lint: anchors, HUD backticks, loc gate, and no LINT leaks."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
TK = (ROOT/"systems"/"toolkit-gpt-spielleiter.md").read_text(encoding="utf-8")

def ok(pat, msg):
    if not re.search(pat, TK, re.S):
        print(f"[FAIL] {msg}")
        return False
    print(f"[ OK ] {msg}")
    return True

all_ok = True
for tag in [
    r"LINT:CHRONO_KEY_GATE",
    r"LINT:CHRONO_MODULE",
    r"LINT:CHRONO_GUARDS",
    r"LINT:CHRONO_NO_SEEDS",
    r"LINT:CHRONO_NO_PARADOX",
    r"LINT:CHRONO_NO_BOSS",
    r"LINT:CHRONO_NO_FR",
    r"LINT:CHRONO_SERVICES",
    r"LINT:CHRONO_RIFT_GATE",
    r"LINT:CHRONO_SIGNAL_GUARD",
    r"LINT:HQ_ADMIT_GUARD",
    r"LINT:FR_AT_HQ_ONLY",
]:
    all_ok &= ok(tag, f"{tag} present")

all_ok &= ok(r"`.*CHRONOPOLIS", "Chronopolis HUD backticked single-line")
all_ok &= ok(r"campaign\.loc\s*=\s*'CITY'", "start_chronopolis sets loc='CITY'")
all_ok &= ok(r"campaign\.loc\s*=\s*'HQ'", "exit_chronopolis resets loc='HQ'")

for i, line in enumerate(TK.splitlines(), 1):
    if "LINT:" in line and ("`" in line or "hud_tag(" in line):
        print(f"[FAIL] LINT anchor leaked in output (line {i})")
        all_ok = False
        break

sys.exit(0 if all_ok else 1)
