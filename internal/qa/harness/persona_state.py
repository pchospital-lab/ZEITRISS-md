#!/usr/bin/env python3
"""
persona_state.py — QA-Fassaden-Shim (P2).

A2/A6 (PLAN-CRITIC.md, BLOCKER/HINWEIS): die generische Persona-State-Engine
lebt jetzt unter `mmo_sim/core/persona_state.py` — der Schema-Pfad wird HIER,
an der QA-Fassaden-Grenze, EXPLIZIT gesetzt (kein `__file__`-relativer
Laufzeit-Patch mehr wie zuvor in `lobby/rooms.py:89-103`).

`rooms.py` importiert dieses Modul weiterhin als `import persona_state as ps`
und uebergibt `ps` 1:1 als `persona_state_store`-Argument an den neutralen
Kern (`mmo_sim.core.store`) — ein Modul ist dafuer genauso brauchbar wie eine
Instanz (Duck-Typing: nur `.load_state`/`.save_state`/`.update_state` werden
aufgerufen). `unittest.mock.patch.object(rooms.ps, "save_state", ...)` in
`test_lobby_tables.py` patcht damit exakt die Funktion, die der Kern
tatsaechlich aufruft.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent  # internal/qa/harness
_REPO_ROOT = _HERE.parents[1]  # harness -> qa -> internal -> (parents[1]=internal) ... siehe unten
# _HERE.parents[0] = internal/qa ; _HERE.parents[1] = internal ; _HERE.parents[2] = repo root
_REPO_ROOT = _HERE.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.persona_state import (  # noqa: E402
    PersonaStateStore,
    ROUND_HISTORY_CAP,  # noqa: F401
    LEARNINGS_CAP,  # noqa: F401
    GOALS_CAP,  # noqa: F401
    render_for_prompt,  # noqa: F401
    update_state,  # noqa: F401
)

# Der reale Schema-Pfad (verifiziert, existiert): internal/qa/fixtures/persona-state.schema.json.
# _HERE = internal/qa/harness -> _HERE.parent = internal/qa.
_SCHEMA_PATH = _HERE.parent / "fixtures" / "persona-state.schema.json"
_SCHEMA_CACHE = None  # back-compat Attribut, wird intern nicht mehr benutzt

# Kein Default-States-Verzeichnis: JEDER Aufrufer (Tests, section.py, rooms.py)
# uebergibt states_dir explizit — das ist bereits die real beobachtete
# Aufrufkonvention in P1 (Auflage 2, "kein __file__-relativer Default").
_STORE = PersonaStateStore(schema_path=_SCHEMA_PATH, default_states_dir=None)


def validate_state(state: dict) -> None:
    _STORE.validate_state(state)


def load_state(pk: str, states_dir=None) -> dict:
    return _STORE.load_state(pk, states_dir=states_dir)


def save_state(pk: str, state: dict, states_dir=None):
    return _STORE.save_state(pk, state, states_dir=states_dir)
