#!/usr/bin/env python3
"""
tests/mmo_sim/_r12_window_resume_boundary_fixture.py — gemeinsamer
Testhelper fuer `test_r12_window_resume_boundary_*.py` (R12-W74:
F01a/F01b/F01c + F02 Boundary-Nachzug auf dem W73-Resultat).

FIXTURE_ONLY (kein Produktcode kennt diese Datei): kapselt den
wiederholt gebrauchten "echte Zweiprozess-Fall"-Baustein -- startet
EIN eingebettetes Python-Skript als GENUINE separate OS-Prozessinstanz
(`subprocess.run`, echter Exitcode, kein Thread/Funktionsaufruf-Fake),
mit demselben Offline-Audit-Hook wie die Review-Evidence-Probes
(`review-evidence/probe_w73_*.py`) -- jeder Netz-/Subprozess-/Fork-
Versuch des eingebetteten Skripts bricht sofort ab."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

_GUARD_PRELUDE = (
    "import sys\n"
    "def _r12_offline_guard(event, args):\n"
    "    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind', "
    "'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork'):\n"
    "        raise RuntimeError('OFFLINE_GUARD:' + event)\n"
    "sys.addaudithook(_r12_offline_guard)\n"
    f"sys.path.insert(0, {str(_REPO_ROOT)!r})\n"
    f"sys.path.insert(0, {str(_HERE)!r})\n"
)


def run_phase(script_body: str, *, timeout: float = 30.0) -> subprocess.CompletedProcess:
    """Fuehrt `script_body` (vollstaendiger, fuer sich lauffaehiger Python-
    Quelltext -- muss GENAU EIN JSON-Objekt als letzte stdout-Zeile drucken)
    in einem ECHTEN separaten OS-Prozess aus (`subprocess.run`, kein
    In-Process-Funktionsaufruf) -- `sys.path` ist bereits auf das Repo-Root
    + dieses Testverzeichnis gesetzt. Liefert das volle `CompletedProcess`
    (echter `returncode`, `stdout`, `stderr`) -- der Aufrufer prueft `rc`
    UND den geparsten JSON-Zustand selbst."""
    proc = subprocess.run(
        [sys.executable, "-c", _GUARD_PRELUDE + script_body],
        capture_output=True, text=True, timeout=timeout,
    )
    return proc


def last_json(proc: subprocess.CompletedProcess) -> dict:
    """Parst die letzte nicht-leere stdout-Zeile als JSON -- bei fehlender
    Ausgabe wird `stderr` (z.B. ein unerwarteter Traceback) in die
    Assertion-Meldung aufgenommen, statt eine kryptische `IndexError`/
    `JSONDecodeError` ohne Kontext zu werfen."""
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, f"keine stdout-Ausgabe (rc={proc.returncode}) -- stderr:\n{proc.stderr}"
    return json.loads(lines[-1])
