#!/usr/bin/env bash
# ZEITRISS - Unix-Launcher (macOS / Linux).
#
# Doppelklickbar (bei entsprechenden Desktop-Umgebungen) oder direkt:
#   ./zeitriss.sh
#
# Findet Python 3 und startet scripts/zeitriss.py.

set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "${SCRIPT_DIR}"

for candidate in python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
        # Prüfe, dass es wirklich Python 3 ist (manche 'python' sind 2.7)
        if "${candidate}" -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' 2>/dev/null; then
            exec "${candidate}" "${SCRIPT_DIR}/scripts/zeitriss.py" "$@"
        fi
    fi
done

echo
echo "  Python 3 wurde nicht gefunden."
echo
echo "  ZEITRISS braucht Python 3 (kostenlos)."
echo "    macOS:  brew install python3    (oder: https://www.python.org/downloads/)"
echo "    Linux:  sudo apt install python3 (oder distro-entsprechend)"
echo
exit 1
