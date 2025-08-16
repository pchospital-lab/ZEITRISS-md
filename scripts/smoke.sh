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
export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"

python3 tools/lint_runtime.py
python3 -m scripts.lint_arena
python3 -m scripts.lint_chronopolis
python3 -m scripts.lint_doc_links
python3 -m scripts.lint_umlauts
python3 -m scripts.validate_index
python3 -m scripts.check_lint_anchors
python3 -m unittest -q

# Gear shop tiers deterministic
node -e "const rt=require('./runtime');console.log(rt.on_command('!gear shop'))" | grep 'Shop-Tiers: T1:true'

# Debrief renders Px and TEMP
mkdir -p out
node tools/test_debrief.js > out/debrief.log
grep -E "Paradox: .* TEMP" out/debrief.log

# HUD TTL mm:ss and Sweeps/Stress
node tools/test_hud.js > out/hud.log
grep -E "TTL [0-9]{2}:[0-9]{2}" out/hud.log

# FR tag only visible in scene 1
node tools/test_fr_tag.js 1 > out/scene_01.log
node tools/test_fr_tag.js 2 > out/scene_02.log
grep " · FR:" out/scene_01.log
! grep " · FR:" out/scene_02.log

# Foreshadow guard warns in precision mode
GM_STYLE=precision node tools/test_foreshadow.js | grep "Foreshadow low"

# CommsCheck message
node tools/test_comms.js | grep "CommsCheck failed"

# Save whitelist and HQ guard
node tools/test_save.js | tee out/save.log
grep "Save denied: HQ-only." out/save.log
grep "save-ok" out/save.log

echo ""
echo "Manual Chronopolis Gate Smoke (60–90s):"
echo " 1) Lvl10 ohne Key -> HQ betreten -> erwartet: HUD 'Schlüssel erteilt'"
echo " 2) In CITY: fr_contact(...) -> BLOCK; im HQ -> OK"
echo " 3) chrono_launch_rift in CITY -> BLOCK; im HQ + episode_completed=true -> OK"
echo " 4) chrono_launch_rift ohne chrono.epoch -> nutzt campaign.epoch (Fallback)"
echo " 5) In CITY: Save -> BLOCK; im HQ: Save -> OK"
echo ""
echo "All smoke checks passed."
