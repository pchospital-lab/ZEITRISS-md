#!/usr/bin/env bash
set -euo pipefail
python3 tools/lint_runtime.py
python3 scripts/lint_arena.py
python3 scripts/lint_hud_codex.py
python3 scripts/lint_signal_devices.py
python3 scripts/validate_index.py
echo "All smoke checks passed."
