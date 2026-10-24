#!/usr/bin/env python3
"""
tests/mmo_sim/_recovery_public_fixture_paths.py — portable Pflichtfixture-
Bindung fuer `test_recovery_ops_r1.py`/`test_recovery_ops_r2.py`
(ZR-LIVEWEG-PR-KANDIDAT-20261016-R1, 01_AUFTRAG.md C).

Vorher brauchten `ZEITRISS_R1_BUDGET_CALC`/`ZEITRISS_R1_CONTROL_JSON` ein
privates Pruefpaket (ausdruecklich gebunden und zulaessig fuer das private
Rezensionspaket) -- ein frischer, oeffentlicher Repo-Checkout darf dieses
Paket NICHT mehr benoetigen. Diese Datei liefert GENAU EINE Aufloesestelle
fuer beide Pflichtfixtures:

  1. Ist die jeweilige Umgebungsvariable gesetzt, bindet sie UNVERAENDERT
     (Rueckwaertskompatibilitaet zur bisherigen privaten Pruefumgebung --
     ein Betreiber kann weiterhin ein eigenes Referenzpaket einhaengen).
  2. Fehlt sie, bindet der NEUTRALE Repo-Default unter
     `tests/mmo_sim/fixtures/recovery_contract/` -- IMMER im Checkout
     vorhanden, kein Exchange-/Chatpaket, keine Secrets.

Eine ausdruecklich auf eine NICHT vorhandene Datei zeigende Variable bleibt
weiterhin ehrlich BLOCKED_ENV (kein stiller Fallback bei einem erkennbar
FALSCHEN Pfad) -- nur das volkommene FEHLEN der Variable loest jetzt den
neutralen Default aus, s. `test_recovery_fixture_portability.py`."""
from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FIXTURE_DIR = _HERE / "fixtures" / "recovery_contract"

DEFAULT_BUDGET_CALC = _FIXTURE_DIR / "budget_calc_fixture.py"
DEFAULT_CONTROL_JSON = _FIXTURE_DIR / "control.synthetic.json"


def _resolve(env_name: str, default: Path) -> Path:
    raw = os.environ.get(env_name)
    if raw:
        return Path(raw)
    return default


def resolve_budget_calc() -> Path:
    """`ZEITRISS_R1_BUDGET_CALC` falls gesetzt, sonst der neutrale
    Repo-Default (`fixtures/recovery_contract/budget_calc_fixture.py`)."""
    return _resolve("ZEITRISS_R1_BUDGET_CALC", DEFAULT_BUDGET_CALC)


def resolve_control_json() -> Path:
    """`ZEITRISS_R1_CONTROL_JSON` falls gesetzt, sonst der neutrale
    Repo-Default (`fixtures/recovery_contract/control.synthetic.json`)."""
    return _resolve("ZEITRISS_R1_CONTROL_JSON", DEFAULT_CONTROL_JSON)
