#!/usr/bin/env bash
# ZEITRISS - Unix-Launcher (macOS / Linux).
#
# Doppelklickbar (bei entsprechenden Desktop-Umgebungen) oder direkt:
#   ./zeitriss.sh
#
# Findet Python 3 und startet scripts/zeitriss.py.

# Kein `set -e`: wir fangen jeden Exit-Code unten explizit ab (statt den
# Prozess hart abzubrechen), damit bei einem Startfehler noch die
# Terminal-Pause laufen kann.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "${SCRIPT_DIR}"

# Haelt das Terminal bei einem Startfehler offen, damit die Fehlermeldung
# nicht verschwindet, bevor der Nutzer sie lesen kann (Terminals, die sich
# nach Prozessende sofort schliessen). NUR interaktiv ([ -t 0 ]) und NICHT
# headless/Testlauf (ZEITRISS_NO_PAUSE gesetzt) -- sonst wuerde ein CI-
# oder Skript-Aufruf ewig auf Enter warten.
_pause_on_error() {
    if [ -t 0 ] && [ -z "${ZEITRISS_NO_PAUSE:-}" ]; then
        read -rp "  Drücke Enter zum Schließen … " _unused
    fi
}

for candidate in python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
        # Prüfe, dass es wirklich Python 3 ist (manche 'python' sind 2.7)
        if "${candidate}" -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' 2>/dev/null; then
            # Kein `exec` mehr: als Subprozess starten, damit wir den
            # Exit-Code sehen und bei Fehler die Terminal-Pause zeigen
            # koennen, bevor das Skript (und mit ihm das Terminal) endet.
            "${candidate}" "${SCRIPT_DIR}/scripts/zeitriss.py" "$@"
            rc=$?
            if [ "${rc}" -ne 0 ]; then
                echo
                echo "  ZEITRISS wurde mit einem Fehler beendet (Exit ${rc})."
                _pause_on_error
            fi
            exit "${rc}"
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
_pause_on_error
exit 1
