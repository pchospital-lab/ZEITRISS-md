#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mmo_sim_launcher_hook.py — optionaler Projekt-Einstieg fuer `launcher.py`
(P2 M3, PLAN.md §2: "Launcher bekommt optionalen Projekt-Hook statt
hartkodierter MMO-Sonderfaelle").

`launcher.py` importiert dieses Modul optional (try/except ImportError,
analog `rite_module`) und ruft bei Auswahl `[M]` ausschliesslich `launch()`
auf — der generische Launcher-Core enthaelt selbst KEINE MMO-Sim-Logik.

P2-Fertigstellung (I3, REVIEW-P2.md §I3/Test 14): `scripts/mmo_sim.py`
heisst genauso wie das echte Paket `mmo_sim/` im Repo-Root. Liegt
`scripts/` im `sys.path` (wie hier), bindet ein plattes `import mmo_sim`
den Namen `mmo_sim` in `sys.modules` an DIESE Shim-DATEI, bevor deren
eigener `from mmo_sim.core import identity`-Import laeuft — die Datei
versucht dann, sich selbst als Paket zu importieren:
`ModuleNotFoundError: No module named 'mmo_sim.core'; 'mmo_sim' is not a
package'`. Fix: die Shim-Datei per EXPLIZITEM Pfad unter einem eindeutigen,
kollisionsfreien Modulnamen laden (analog `adapters/gm_owui.py`s
`_load_sl_client_module`) — der Name `mmo_sim` wird dabei nie mehrdeutig
belegt, `scripts/mmo_sim.py` bleibt fuer den Direktaufruf
(`python scripts/mmo_sim.py`) unveraendert an seinem dokumentierten Ort."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def launch() -> int:
    entry_path = _SCRIPTS_DIR / "mmo_sim.py"
    spec = importlib.util.spec_from_file_location("mmo_sim_scripts_entrypoint", entry_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"mmo_sim_launcher_hook: konnte Entrypoint nicht laden von {entry_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main([])
