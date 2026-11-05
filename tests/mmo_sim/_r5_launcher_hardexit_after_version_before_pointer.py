#!/usr/bin/env python3
"""
tests/mmo_sim/_r5_launcher_hardexit_after_version_before_pointer.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R5, TEIL B/T4-B (01_NACHZUG.md §3,
GUEST-OPERATOR.md §4, STATIC-CROSSCHECK (a)): gebundene Skriptdatei (KEIN
`-c`-Platzhalter), die `scripts.mmo_sim` importiert (nicht nachbaut) und
`sys.argv[1:]` UNVERAENDERT an `launcher.main(...)` durchreicht.

Monkeypatch an der GENAU gerуegten inneren Publikationsgrenze: `mmo_sim.
core.store._write_current_save_version` wird so umhuellt, dass es die echte
Versionsdatei (`0001.json`) schreibt -- und DANN `os._exit(94)` ausfuehrt,
BEVOR `publish_current_save` den State-Zeiger (`current_save_version`-Ref)
setzt. Das hinterlaesst exakt den statisch bestaetigten Zwischenzustand:
`0001.json` existiert, aber der Persona-State traegt (noch) keinen
Current-Zeiger. KEIN veraenderter Produktpfad -- nur eine Prozess-
unterbrechung GENAU zwischen Schritt 2 und 3 derselben vorhandenen
`publish_current_save`-Sequenz. Der normale Retry (frischer, UNGEPATCHTER
Launcher) muss diesen erreichten Schritt uebernehmen, ohne eine zweite
inhaltsgleiche Version (`0002.json`) anzulegen."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

from mmo_sim.core import store as core_store  # noqa: E402

_real_write_version = core_store._write_current_save_version


def _write_version_then_hard_exit(current_saves_dir, persona_key, block):
    # Echte Versionsdatei schreiben (Schritt 2 der vorhandenen Sequenz) ...
    path = _real_write_version(current_saves_dir, persona_key, block)
    # ... dann hart abbrechen VOR dem State-Zeiger (Schritt 3). Rueckgabewert
    # (version_path) erreicht den Aufrufer nie -- genau die reale Unterbrechung.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(94)
    return path  # unerreichbar; nur fuer Signaturtreue


core_store._write_current_save_version = _write_version_then_hard_exit

import scripts.mmo_sim as launcher  # noqa: E402

if __name__ == "__main__":
    sys.exit(launcher.main(sys.argv[1:]))
