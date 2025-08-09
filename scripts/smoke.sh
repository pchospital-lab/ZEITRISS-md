#!/usr/bin/env bash
set -euo pipefail
python3 tools/lint_runtime.py
python3 scripts/lint_arena.py
python3 scripts/lint_chronopolis.py
python3 scripts/lint_hud_codex.py
python3 scripts/lint_signal_devices.py
python3 scripts/validate_index.py
echo ""
echo "Manual Chronopolis Gate Smoke (60–90s):"
echo " 1) Lvl10 ohne Key -> HQ betreten -> erwartet: HUD 'Schlüssel erteilt'"
echo " 2) In CITY: fr_contact(...) -> BLOCK; im HQ -> OK"
echo " 3) chrono_launch_rift in CITY -> BLOCK; im HQ + episode_completed=true -> OK"
echo " 4) chrono_launch_rift ohne chrono.epoch -> nutzt campaign.epoch (Fallback)"
echo " 5) In CITY: Save -> BLOCK; im HQ: Save -> OK"
echo ""
echo "All smoke checks passed."
