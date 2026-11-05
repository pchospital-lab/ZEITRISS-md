#!/usr/bin/env python3
"""
tests/mmo_sim/_r4_launcher_hardexit_before_reflection.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261104-R4, TEIL B/T2: gebundene Skriptdatei (KEIN
`-c`-Platzhalter, literal als `[sys.executable, "-B", <dieser Pfad>,
<echte Launcher-Flags>]` gestartet), die den ECHTEN, UNVERAENDERTEN
`scripts/mmo_sim.py:main()` importiert (nicht nachgebaut) und VOR dessen
Aufruf GENAU EINEN Klassen-Monkeypatch an der Prozessabbruch-Grenze setzt:
`SectionRuntime._collect_reflections` wird durch einen harten `os._exit(94)`
ersetzt -- dieselbe Technik wie
`tests/mmo_sim/drive_r3_g5_evidence_2026_11_04.py`s `_hard_exit_before_
reflection` (dort gegen eine direkt konstruierte Session, hier gegen den
ECHTEN Launcher-Dispatch). Phase 1 (`store.complete_section`: Plan-Pin +
Primaersave) ist zu diesem Zeitpunkt bereits real abgeschlossen (die
Markerantwort hat `core.runtime.run_full_section` bereits bis zu diesem
Punkt gebracht) -- kein veraenderter Produktpfad, nur ein kontrollierter
harter Prozessabbruch GENAU an dieser Grenze.

`sys.argv[1:]` wird UNVERAENDERT an `launcher.main(...)` durchgereicht --
literal argv wie beim echten CLI-Aufruf."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

import mmo_sim.core.runtime as runtime_mod  # noqa: E402


def _hard_exit_before_reflection(*_a, **_kw):
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(94)


runtime_mod.SectionRuntime._collect_reflections = _hard_exit_before_reflection

import scripts.mmo_sim as launcher  # noqa: E402

if __name__ == "__main__":
    sys.exit(launcher.main(sys.argv[1:]))
