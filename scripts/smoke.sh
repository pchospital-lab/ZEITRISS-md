#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
if command -v git >/dev/null 2>&1; then
  GIT_ROOT="$(git -C "${ROOT}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "${GIT_ROOT:-}" ]]; then ROOT="${GIT_ROOT}"; fi
fi

echo "Repo root: ${ROOT}"
cd "${ROOT}"

python3 tools/lint_runtime.py
python3 scripts/lint_arena.py
python3 scripts/lint_chronopolis.py
python3 scripts/lint_hud_codex.py
python3 scripts/lint_signal_devices.py
python3 scripts/validate_index.py
python3 scripts/check_lint_anchors.py

echo ""
echo "Manual Chronopolis Gate Smoke (60–90s):"
echo " 1) Lvl10 ohne Key -> HQ betreten -> erwartet: HUD 'Schlüssel erteilt'"
echo " 2) In CITY: fr_contact(...) -> BLOCK; im HQ -> OK"
echo " 3) chrono_launch_rift in CITY -> BLOCK; im HQ + episode_completed=true -> OK"
echo " 4) chrono_launch_rift ohne chrono.epoch -> nutzt campaign.epoch (Fallback)"
echo " 5) In CITY: Save -> BLOCK; im HQ: Save -> OK"
echo ""
echo "All smoke checks passed."
