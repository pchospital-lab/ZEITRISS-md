#!/usr/bin/env bash
# Kompatibler Wrapper: ein Exportpfad, eine Slot-Liste, eine Anleitung.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_BASE="${1:-$REPO/.exports}"
exec python3 "$SCRIPT_DIR/setup.py" --export --out "$OUT_BASE" "${@:2}"
