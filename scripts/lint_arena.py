#!/usr/bin/env python3
"""Arena lint: checks presence of runtime guards, HUD backticks, actions & anchors."""
from __future__ import annotations

from pathlib import Path

from scripts.lib_repo import repo_root, read_text
from scripts.lib_lint import ok


def assert_no_anchor_in_output_context(text: str, label: str) -> bool:
    for i, line in enumerate(text.splitlines(), 1):
        if "LINT:" in line and ("`" in line or "hud_tag(" in line):
            print(f"[FAIL] {label}: LINT anchor leaked at line {i}")
            return False
    return True


def main() -> int:
    root = repo_root(Path(__file__))
    tk = read_text(root / "systems" / "toolkit-gpt-spielleiter.md")

    all_ok = True
    all_ok &= ok(r"LINT:ARENA_MODULE", "LINT anchors present (ARENA_MODULE)", tk)
    all_ok &= ok(r"LINT:ARENA_GUARDS", "Guards anchor present", tk)
    all_ok &= ok(r"LINT:ARENA_NO_SEEDS", "Seeds suppressed in arena", tk)
    all_ok &= ok(r"LINT:ARENA_NO_PARADOXON", "Paradoxon frozen in arena", tk)
    all_ok &= ok(r"LINT:ARENA_NO_BOSS", "Boss suppressed in arena", tk)
    all_ok &= ok(r"LINT:ARENA_NO_FR_INTERVENTION", "FR intervention suppressed", tk)
    for tag in [
        "LINT:ARENA_SNAPSHOT",
        "LINT:ARENA_RESTORE",
        "LINT:ARENA_BLOCK_SAVE",
        "LINT:ARENA_SINGLE_INSTANCE",
        "LINT:ARENA_AFK_GUARD",
        "LINT:ARENA_BUDGET",
        "LINT:ARENA_PSI_HINT",
        "LINT:ARENA_COMMS_REUSE",
        "LINT:ARENA_CAMPAIGN_SNAP",
        "LINT:ARENA_ABORT",
        "LINT:ARENA_LOG",
    ]:
        all_ok &= ok(tag, f"{tag} present", tk)
    for tag in [
        r"LINT:ARENA_TIEBREAK",
        r"LINT:ARENA_RULE_PENALTY",
        r"LINT:ARENA_MODE_CONTROL",
        r"LINT:ARENA_MODE_ELIMINATION",
    ]:
        all_ok &= ok(tag, f"{tag} present", tk)
    all_ok &= ok(r"arena_action\(", "ArenaAction macro exists", tk)
    all_ok &= ok(
        r"Aktion blockiert\s*[–-]\s*Gerät angeben",
        "Device requirement text present",
        tk,
    )
    all_ok &= ok(r"Jammer aktiv", "Jammer action present", tk)
    all_ok &= ok(r"ARENA·", "Arena HUD label present", tk)
    all_ok &= ok(r"`.*ARENA", "HUD overlay is in backticks", tk)
    all_ok &= ok(r"PHASE:", "Arena HUD displays phase tag", tk)

    all_ok &= assert_no_anchor_in_output_context(tk, "toolkit")

    print("\nSummary:", "OK" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
