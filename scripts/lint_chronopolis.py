#!/usr/bin/env python3
"""Chronopolis lint: anchors, HUD backticks, loc gate, and no LINT leaks."""
from __future__ import annotations

from pathlib import Path
import re

from scripts.lib_repo import repo_root, read_text
from scripts.lib_lint import ok


def main() -> int:
    root = repo_root(Path(__file__))
    tk = read_text(root / "systems" / "toolkit-gpt-spielleiter.md")

    all_ok = True
    for tag in [
        r"LINT:CHRONO_KEY_GATE",
        r"LINT:CHRONO_MODULE",
        r"LINT:CHRONO_GUARDS",
        r"LINT:CHRONO_NO_SEEDS",
        r"LINT:CHRONO_NO_PARADOXON",
        r"LINT:CHRONO_NO_BOSS",
        r"LINT:CHRONO_NO_FR",
        r"LINT:CHRONO_SERVICES",
        r"LINT:CHRONO_RIFT_GATE",
        r"LINT:CHRONO_SIGNAL_GUARD",
        r"LINT:HQ_ADMIT_GUARD",
        r"LINT:FR_AT_HQ_ONLY",
    ]:
        all_ok &= ok(tag, f"{tag} present", tk)

    all_ok &= ok(r"`.*CHRONOPOLIS", "Chronopolis HUD backticked single-line", tk)
    all_ok &= ok(
        r"campaign\.loc\s*=\s*'CITY'", "start_chronopolis sets loc='CITY'", tk
    )
    all_ok &= ok(
        r"campaign\.loc\s*=\s*'HQ'", "exit_chronopolis resets loc='HQ'", tk
    )
    all_ok &= ok(r"LINT:CHRONO_KEY_HQ_HOOK", "HQ-entry key hook anchor present", tk)
    all_ok &= ok(
        r"exit_chronopolis\(\).*campaign\.loc\s*=\s*'HQ'.*hq_entry_hook\(\)",
        "Key auto-grant is called on HQ entry",
        tk,
    )
    all_ok &= ok(r"LINT:CHRONO_ABORT", "Chronopolis abort macro present", tk)
    all_ok &= ok(r"LINT:CHRONO_RESUME_GUARD", "Chronopolis resume guard present", tk)
    all_ok &= ok(
        r"chrono_abort\(\).*campaign\.loc\s*=\s*'HQ'",
        "Abort returns location to HQ",
        tk,
    )
    all_ok &= ok(
        r"chrono_resume_guard\(\)", "Resume guard is invoked in bootstrap/entry", tk
    )

    sv = root / "systems" / "gameflow" / "speicher-fortsetzung.md"
    if sv.exists():
        sv_text = read_text(sv)
        pattern_hq_save = (
            r"state\.location\s*==\s*['\"]HQ['\"]|"
            r"campaign\.loc\s*==\s*['\"]HQ['\"]"
        )
        if re.search(pattern_hq_save, sv_text, re.S):
            print("[ OK ] HQ-only save guard present in save module")
        else:
            print("[FAIL] HQ-only save guard missing in save module")
            all_ok = False
    else:
        print("[FAIL] Save module not found for HQ-only check")
        all_ok = False

    for i, line in enumerate(tk.splitlines(), 1):
        if "LINT:" in line and ("`" in line or "hud_tag(" in line):
            print(f"[FAIL] LINT anchor leaked in output (line {i})")
            all_ok = False
            break

    print("\nSummary:", "OK" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
