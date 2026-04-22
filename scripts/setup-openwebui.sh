#!/usr/bin/env bash
# DEPRECATED — scripts/setup-openwebui.sh ist nur noch ein Shim.
#
# Der echte Setup-Pfad ist scripts/setup.py (einheitlich in allen Repos,
# OpenWebUI 0.9.1 kompatibel, mit Retrieval-Verify).
#
# Alte Zeilen liegen in scripts/setup-openwebui.sh.legacy.
# Beim nächsten Repo-Cleanup kann die .legacy-Datei entfernt werden.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "→ setup-openwebui.sh ist deprecated. Rufe scripts/setup.py auf..."
exec python3 "$SCRIPT_DIR/setup.py" "$@"
