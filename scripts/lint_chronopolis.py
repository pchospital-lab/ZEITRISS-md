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
all_ok &= ok(r"LINT:CHRONO_KEY_HQ_HOOK", "HQ-entry key hook anchor present")
all_ok &= ok(r"exit_chronopolis\(\).*campaign\.loc\s*=\s*'HQ'.*hq_entry_hook\(\)",
             "Key auto-grant is called on HQ entry")

SV = (ROOT/"systems"/"gameflow"/"speicher-fortsetzung.md")
if SV.exists():
    sv_text = SV.read_text(encoding="utf-8")
    if re.search(r"campaign\.loc\s*==\s*['\"]HQ['\"]", sv_text, re.S):
        print("[ OK ] HQ-only save guard present in save module")
    else:
        print("[FAIL] HQ-only save guard missing in save module"); all_ok = False
else:
    print("[FAIL] Save module not found for HQ-only check"); all_ok = False

for i, line in enumerate(TK.splitlines(), 1):
    if "LINT:" in line and ("`" in line or "hud_tag(" in line):
        print(f"[FAIL] LINT anchor leaked in output (line {i})")
        all_ok = False
        break

sys.exit(0 if all_ok else 1)
