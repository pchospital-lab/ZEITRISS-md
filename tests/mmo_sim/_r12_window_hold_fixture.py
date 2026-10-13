#!/usr/bin/env python3
"""
tests/mmo_sim/_r12_window_hold_fixture.py — gemeinsamer Testhelper fuer
`test_r12_window_hold_*.py` (R12-W73, D-HOLD Pre-Send-Window-Resume).

FIXTURE_ONLY (kein Produktcode kennt diese Datei): kapselt das wiederholt
gebrauchte Testmuster "Admissionfenster oeffnen/schliessen" (ueber
`write_test_profile` + direktes `wall_deadline`-Feld in `lab.status.json`,
derselbe atomare Schreibweg wie die Produktfunktion selbst nutzt) und den
exakten Deadline-vor-Versand-Reason-Text (01_AUFTRAG_SAVEGATE.md-Forensik,
W73-BRIEF.md)."""
from __future__ import annotations

import json
from pathlib import Path

from mmo_sim.core.admission import write_test_profile, _atomic_write_json, _status_path

DEADLINE_REASON_TEMPLATE = (
    "admission_blocked:reale Laufzeitgrenze (Wall-Clock) erreicht "
    "(Deadline {deadline}, frisch von Platte, H-E)."
)


def deadline_reason(deadline: float) -> str:
    return DEADLINE_REASON_TEMPLATE.format(deadline=deadline)


def open_window(run_dir: str | Path) -> None:
    """Admissionfenster offen: `write_test_profile` ohne `wall_deadline` --
    ggf. vorhandenes `wall_deadline` eines frueheren `close_window`-Aufrufs
    im selben `run_dir` wird entfernt (sonst bliebe die alte, abgelaufene
    Deadline bestehen)."""
    write_test_profile(run_dir)
    status_path = _status_path(run_dir)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    if "wall_deadline" in data:
        del data["wall_deadline"]
        _atomic_write_json(status_path, data)


def close_window(run_dir: str | Path, *, deadline: float = 1.0) -> str:
    """Admissionfenster geschlossen: `wall_deadline` liegt in der
    Vergangenheit (Default `1.0`, weit vor jedem realistischen `time.
    time()`). Liefert den exakten `reason`-Text, den `read_admission_block`
    dafuer erzeugt (fuer Assertions gegen `last_reason`)."""
    write_test_profile(run_dir)
    status_path = _status_path(run_dir)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    data["wall_deadline"] = deadline
    _atomic_write_json(status_path, data)
    return deadline_reason(deadline)
