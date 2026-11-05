#!/usr/bin/env python3
"""
tests/mmo_sim/_r4_launcher_hardexit_between_publication.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261104-R4, TEIL B/T4-B: gebundene Skriptdatei (KEIN
`-c`-Platzhalter) wie `_r4_launcher_hardexit_before_reflection.py`, aber
mit dem Klassen-Monkeypatch an der ANDEREN Abbruch-Grenze: `TuiSession.
_finish_granted_guest_creation` wird durch einen harten `os._exit(94)`
ersetzt -- dieselbe Technik wie `drive_r3_g5_evidence_2026_11_04.py`s
`_hard_exit_between_publication_steps` (dort ein Instanz-Monkeypatch auf
einer direkt konstruierten Session, hier ein Klassen-Monkeypatch gegen den
ECHTEN Launcher-Dispatch). `run_admitted_creation_dialog` hat zu diesem
Zeitpunkt `onboarding.complete_with_save` bereits real ausgefuehrt (Phase 1:
der angenommene Save ist durabel) -- NUR die Publikation (Katalog/Current)
in `_finish_granted_guest_creation` (Phase 2) fehlt noch.

`sys.argv[1:]` wird UNVERAENDERT an `launcher.main(...)` durchgereicht."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _hard_exit_between_publication_steps(*_a, **_kw):
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(94)


TuiSession._finish_granted_guest_creation = _hard_exit_between_publication_steps

import scripts.mmo_sim as launcher  # noqa: E402

if __name__ == "__main__":
    sys.exit(launcher.main(sys.argv[1:]))
