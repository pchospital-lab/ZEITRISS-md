#!/usr/bin/env bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
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
python3 tools/lint_debrief_trace.py
python3 -m scripts.lint_arena
python3 -m scripts.lint_chronopolis
python3 -m scripts.lint_doc_links
python3 -m scripts.lint_umlauts
python3 -m scripts.validate_index
python3 -m scripts.check_lint_anchors
python3 -m unittest -q

# Gear shop tiers deterministic
mkdir -p out
node tools/test_shop.js | tee out/shop.log
grep 'baseline: Shop-Tiers: T1:true T2:false T3:false · BP:0' out/shop.log
grep 'tier3-no-blueprint: Shop-Tiers: T1:true T2:true T3:false · BP:0' out/shop.log
grep 'tier3-with-blueprint: Shop-Tiers: T1:true T2:true T3:true · BP:1' out/shop.log
grep 'tier3-no-blueprint-cmd: Shop-Tiers: T1:true T2:true T3:false · BP:0' out/shop.log
grep 'tier3-with-blueprint-cmd: Shop-Tiers: T1:true T2:true T3:true · BP:1' out/shop.log

# Debrief rendert Belohnungen und Px-Tracker
mkdir -p out
node tools/test_debrief.js > out/debrief.log
grep 'Belohnungen · Chrono Units' out/debrief.log
grep -E 'Resonanz Px [0-5]/5' out/debrief.log
grep -E "Px .* TEMP" out/debrief.log

# HUD TTL mm:ss and Sweeps/Stress
node tools/test_hud.js > out/hud.log
grep -E "RW [0-9]{2}:[0-9]{2}" out/hud.log
head -n1 out/hud.log > out/scene_01.log
grep -m1 "Sweeps:" out/hud.log > out/scene_02.log
! grep "Sweeps:" out/scene_01.log
! grep "Stress " out/scene_01.log
grep "Sweeps:" out/scene_02.log

# FR tag only visible in scene 1
node tools/test_fr_tag.js 1 > out/scene_01.log
node tools/test_fr_tag.js 2 > out/scene_02.log
grep " · FR:" out/scene_01.log
! grep " · FR:" out/scene_02.log

# Foreshadow guard warns in precision mode
GM_STYLE=precision node tools/test_foreshadow.js | grep "Foreshadow low"

# CommsCheck message
node tools/test_comms.js | grep "CommsCheck failed"
node tools/test_comms_rx.js \
  | grep 'CommsCheck failed: require valid device/range or relay/jammer override.'

# Alias- und Squad-Radio-Logs
node tools/test_alias_trace.js | tee out/alias_trace.log
grep "Alias-Trace (2×):" out/alias_trace.log
grep "Squad-Radio (2×):" out/alias_trace.log

# Save whitelist and HQ guard
node tools/test_save.js | tee out/save.log
grep -E "SaveGuard: (Offline|HQ-only|Arena aktiv)" out/save.log
grep "save-ok" out/save.log

# Load path
node tools/test_load.js | tee out/load.log
grep "load-ok" out/load.log

# Startoptionen, Accessibility und Chronopolis-Gate
node tools/test_start.js > out/start.log
grep "start-ok" out/start.log

node tools/test_accessibility.js > out/accessibility.log
grep "accessibility-ok" out/accessibility.log

node tools/test_chronopolis_ack.js > out/chronopolis_ack.log
grep "chronopolis-ack-ok" out/chronopolis_ack.log

node tools/test_arena_schema.js > out/arena_schema.log
grep "arena-schema-ok" out/arena_schema.log


# Ruf/Alien-SSOT-Watchguard (Debrief/Tier-V/Onboarding)
node tools/test_ruf_alien_watchguard.js > out/ruf_alien_watchguard.log
grep "ruf-alien-watchguard-ok" out/ruf_alien_watchguard.log

# v7-SSOT-Driftguard (Legacy-Key-Regression)
node tools/test_v7_schema_consistency.js > out/v7_schema_consistency.log
grep "v7-schema-consistency-ok" out/v7_schema_consistency.log
# v7-Issue-Pack-Fixtures (5er/Split-Merge/OpenWebUI-Load)
node tools/test_v7_issue_pack.js > out/v7_issue_pack.log
grep "v7-issue-pack-ok" out/v7_issue_pack.log

# Kontinuitäts-Output-Contract (Recap/Beats/Echo-Fortwirkung)
node tools/test_continuity_output_contract.js > out/continuity_output_contract.log
grep "continuity-output-contract-ok" out/continuity_output_contract.log

# NPC-Kontinuität: SSOT-Feldanker + Fixture-Contract
node tools/test_npc_continuity_consistency.js > out/npc_continuity_consistency.log
grep "npc-continuity-consistency-ok" out/npc_continuity_consistency.log

# ITI-Hardcanon-Watchguard (Atlas/Kernpersonal/Driftbegriffe)
node tools/test_iti_hardcanon_watchguard.js > out/iti_hardcanon_watchguard.log
grep "iti-hardcanon-watchguard-ok" out/iti_hardcanon_watchguard.log

# Physicality-Watchguard (Linse/HUD vs. verankerte HQ-Projektion)
node tools/test_physicality_watchguard.js > out/physicality_watchguard.log
grep "physicality-watchguard-ok" out/physicality_watchguard.log

# Kausalabfang-Watchguard (Never happened als Cleanup-Protokoll)
node tools/test_kausalabfang_watchguard.js > out/kausalabfang_watchguard.log
grep "kausalabfang-watchguard-ok" out/kausalabfang_watchguard.log

# Start-/HQ-Onboarding-Watchguard (NLP-Startvertrag + Save->neuer-Chat)
node tools/test_onboarding_start_save_watchguard.js > out/onboarding_start_save_watchguard.log
grep "onboarding-start-save-watchguard-ok" out/onboarding_start_save_watchguard.log

# Default-Slot-Dependency-Watchguard (keine Runtime-Abhängigkeit auf optionales Modul)
node tools/test_default_slot_dependency_watchguard.js > out/default_slot_dependency_watchguard.log
grep "default-slot-dependency-watchguard-ok" out/default_slot_dependency_watchguard.log

# Director-Layer-Watchguard (Relevanzsatz + ITI-Bulletin Pflichtbeat)
node tools/test_director_layer_watchguard.js > out/director_layer_watchguard.log
grep "director-layer-watchguard-ok" out/director_layer_watchguard.log

# Hard-Final-Review-Watchguard (Split-Kanon/Einstieg/HQ-Kernbereich)
node tools/test_hard_final_review_watchguard.js > out/hard_final_review_watchguard.log
grep "hard-final-review-watchguard-ok" out/hard_final_review_watchguard.log


# Upload-Snapshot-Watchguard (historische Uploads klar vom aktiven SSOT getrennt)
node tools/test_upload_snapshot_watchguard.js > out/upload_snapshot_watchguard.log
grep "upload-snapshot-watchguard-ok" out/upload_snapshot_watchguard.log


# Prozess-Kompaktheit-Watchguard (Triage-Seiten bleiben operativ schlank)
node tools/test_process_compactness_watchguard.js > out/process_compactness_watchguard.log
grep "process-compactness-watchguard-ok" out/process_compactness_watchguard.log

# Watchguard-Loader-Consistency (keine lokalen Resolver-Resthelfer)
node tools/test_watchguard_loader_consistency.js > out/watchguard_loader_consistency.log
grep "watchguard-loader-consistency-ok" out/watchguard_loader_consistency.log

# Watchguard-Smoke-Coverage (alle Watchguards in smoke.sh verankert)
node tools/test_watchguard_smoke_coverage.js > out/watchguard_smoke_coverage.log
grep "watchguard-smoke-coverage-ok" out/watchguard_smoke_coverage.log

# Chronopolis-Gate-Watchguard (automatisiert den früheren Manual-Check)
node tools/test_chronopolis_gate_watchguard.js > out/chronopolis_gate_watchguard.log
grep "chronopolis-gate-watchguard-ok" out/chronopolis_gate_watchguard.log

echo ""
echo "All smoke checks passed."
