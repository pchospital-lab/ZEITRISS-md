#!/usr/bin/env python3
"""
agent_mp/saves.py — QA-Fassaden-Shim (P2).

A6 (PLAN-CRITIC.md): die tatsaechliche v7-Save-Extraktion (ZEITRISS-
Domaenenwissen) lebt jetzt unter `mmo_sim/domain/zeitriss/saves.py` —
Core-Extraktion, KEINE Kopie. Diese Datei bleibt am alten Ort, damit
`import saves as save_lib` (rooms.py, section.py, faithful_section.py)
unveraendert funktioniert, re-exportiert aber nur noch aus der neuen
Implementierung.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.domain.zeitriss.saves import (  # noqa: F401,E402
    extract_all_saves,
    single_character_count,
    block_char_id,
    save_filename,
    extract_personal_saves,
)
