#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS – Setup-Launcher (Einstiegspunkt).

Dünner Shim: die gesamte Launcher-Logik liegt im generischen
`scripts/launcher.py` (in allen Bausätzen byte-identisch). Dieses Script
existiert nur, damit der vertraute Aufruf `python scripts/zeitriss.py` und
die Doppelklick-Wrapper (zeitriss.sh / zeitriss.bat) weiter funktionieren.

Projekt-Identität (Name, Tagline, "Spiel starten"-Wording, Lore) kommt aus
dem `launcher`-Block in setup.json bzw. aus scripts/rite.py — nicht aus
diesem Shim.

Aufruf:
    python scripts/zeitriss.py
    ./zeitriss.sh              (Unix-Wrapper)
    zeitriss.bat               (Windows-Doppelklick)
"""

from __future__ import annotations

import sys
from pathlib import Path

# scripts/ in den Importpfad, damit `launcher` gefunden wird, egal von wo
# das Script gestartet wird.
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import launcher  # noqa: E402
except ImportError as e:
    print(f"FEHLER: scripts/launcher.py kann nicht importiert werden: {e}")
    sys.exit(1)


if __name__ == "__main__":
    try:
        sys.exit(launcher.main())
    except KeyboardInterrupt:
        print("\n  Abgebrochen.")
        sys.exit(130)
