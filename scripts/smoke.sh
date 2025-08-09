#!/usr/bin/env bash
set -euo pipefail
python3 tools/lint_runtime.py
python3 scripts/lint_arena.py
python3 scripts/lint_chronopolis.py
python3 scripts/lint_hud_codex.py
python3 scripts/lint_signal_devices.py
python3 scripts/validate_index.py
echo "All smoke checks passed."

# Manual Chronopolis smoke (≈60–90 s):
# 1. start_chronopolis() ohne Schlüssel → Block "Schlüssel ab Level 10".
# 2. char.lvl=10; chrono_grant_key_if_lvl10(); start_chronopolis() → ok.
# 3. In Chronopolis: campaign.loc=='CITY'; Saveversuch → blockiert.
# 4. exit_chronopolis(); campaign.loc=='HQ'; Save → ok.
# 5. In Chronopolis: fr_contact(...) und chrono_launch_rift(...) → blockiert.
# 6. Im HQ mit episode_completed=true: chrono_launch_rift(seed) → startet Rift.
# 7. hq_admit für Nicht-Agenten blockiert; Gäste mit guest_custody erlaubt.
