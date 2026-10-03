#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS MMO-Sim — TUI-Einstiegspunkt (analog `zeitriss.py`-Shim, P2 M3).

Duenner Shim: die eigentliche Terminal-Logik liegt in `mmo_sim/ui/tui.py`.
Aufruf: `python scripts/mmo_sim.py [--participant <id>]`.

Kein Browser fuers Spielen (11 §7). Ohne `--participant` wird — sofern unter
`--data-dir` bereits ein Teilnehmer bekannt ist — DIESER wiederverwendet
(P2-Fertigstellung I3, REVIEW-P2.md Test 07: "Normaler Neustart ohne
Sonderargument darf nicht neue Identitaet erzeugen"); nur beim allerersten
Lauf fuer ein `--data-dir` wird eine neue Teilnehmer-ID erzeugt.

Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27, H-B): ein FUEHRENDES
Subkommando `lab` (`python scripts/mmo_sim.py lab start|resume|status|stop|
attach ...`) delegiert VOR jeder TUI-/Teilnehmerlogik an
`mmo_sim.lab.cli.main` -- ein Aufruf OHNE dieses Subkommando bleibt exakt
die unveraenderte TUI (H01, kein impliziter Headless-Bootstrap)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
# W6-Fix: beim Direktaufruf `python scripts/mmo_sim.py` traegt Python
# `scripts/` selbst als sys.path[0] ein, BEVOR dieser Code laeuft. War
# `_REPO_ROOT` durch PYTHONPATH bereits (an spaeterer Position) im Pfad,
# uebersprang die alte Pruefung ("not in sys.path") den insert(0) -- dann
# blieb `scripts/` vor dem Repo-Root, `import mmo_sim` fand diese Shim-Datei
# statt des echten Pakets `mmo_sim/` (identische Kollision wie in
# `scripts/mmo_sim_launcher_hook.py` dokumentiert: "'mmo_sim' is not a
# package"). Fix: Repo-Root IMMER an Position 0 erzwingen (bestehendes
# Vorkommen zuerst entfernen), unabhaengig davon, ob/wo es schon im Pfad war.
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

from mmo_sim.core import identity  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402
from mmo_sim.adapters.factories import (  # noqa: E402
    default_gm_transport_factory as _default_gm_transport_factory,
    default_persona_driver_factory as _default_persona_driver_factory,
)

_LAST_PARTICIPANT_FILE = "last_participant.json"


def _resolve_participant_id(data_dir: Path, explicit: str | None) -> str:
    """I3/Test 07: ohne `--participant` wird die zuletzt fuer DIESES
    `--data-dir` verwendete Teilnehmer-ID wiederverwendet (Marker-Datei) --
    nicht bei jedem Start eine neue erzeugt. Eine explizit uebergebene
    `--participant`-ID aktualisiert den Marker (bewusster Wechsel)."""
    marker = data_dir / _LAST_PARTICIPANT_FILE
    if explicit:
        data_dir.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"participant_id": explicit}), encoding="utf-8")
        return explicit
    if marker.exists():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            pid = data.get("participant_id")
            if pid:
                return pid
        except (OSError, json.JSONDecodeError):
            pass
    pid = identity.new_participant_id()
    data_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"participant_id": pid}), encoding="utf-8")
    return pid


def _foreign_active_lab_owner(data_dir: Path) -> int | None:
    """F1 (Critic-Nacharbeit, Bau-GO 2026-09-27, REVIEW-TEILSTAND.md §3,
    Fall 05): derselbe REIN LESENDE Guard-Baustein wie
    `TuiSession._lab_active_guard` (`active_lock_pid(..., exclude_pid=
    os.getpid())`), hier VOR dem fruehen `_resolve_participant_id`-Marker-
    Write in `main()` -- der einzige verbleibende ungewachte fruehschreibende
    Einstieg lag VOR der spaeteren Kommandosperre der einzelnen `n`/`i`/`c`-
    TUI-Befehle. `run_dir` folgt derselben Konvention wie die spaetere
    `TuiSession`-Konstruktion (`data_dir / \"run\"`)."""
    from mmo_sim.lab.runner import active_lock_pid
    return active_lock_pid(data_dir / "run", exclude_pid=os.getpid())


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if raw_argv and raw_argv[0] == "report":
        from mmo_sim.reports.report import main as report_main
        return report_main(raw_argv[1:], repo_root=_REPO_ROOT)
    # H-B (Bau-GO 2026-09-27): fuehrendes Subkommando 'lab' delegiert VOR
    # jeder Teilnehmerausloesung/TUI-Konstruktion -- 0 Modellcalls, keine
    # Marker-/Communitydateien fuer 'lab status'/'lab attach'/'--help'/eine
    # abgelehnte Fehlkonfiguration (H01). Ein Aufruf OHNE 'lab' bleibt exakt
    # die bisherige TUI (unveraendert ab hier).
    if raw_argv and raw_argv[0] == "lab":
        from mmo_sim.lab.cli import main as lab_main
        return lab_main(raw_argv[1:], repo_root=_REPO_ROOT)

    parser = argparse.ArgumentParser(description="ZEITRISS MMO-Sim Terminaloberflaeche")
    parser.add_argument("--participant", default=None, help="bestehende Teilnehmer-ID (sonst wird die zuletzt genutzte wiederverwendet bzw. beim allerersten Lauf eine neue erzeugt)")
    parser.add_argument("--data-dir", default=str(_REPO_ROOT / "internal" / "mmo_sim_data"),
                         help="Datenverzeichnis fuer Onboarding-/Katalog-Journale")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    foreign_pid = _foreign_active_lab_owner(data_dir)
    if foreign_pid is not None:
        print(
            f"TUI-Start: ein aktiver Lab-Lauf (pid={foreign_pid}) kontrolliert diese "
            "Datenablage — kein zweiter schreibender Controller (H-D/G3b, F1). Nur "
            "lesende Ansicht moeglich ('python scripts/mmo_sim.py lab status/attach')."
        )
        return 1
    participant_id = _resolve_participant_id(data_dir, args.participant)
    schema_path = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
    session = TuiSession(
        onboarding_dir=data_dir / "onboarding",
        catalog_dir=data_dir / "catalog",
        participant_id=participant_id,
        run_dir=data_dir / "run",
        states_dir=data_dir / "states",
        schema_path=schema_path if schema_path.is_file() else None,
        # F5/K2: echter Adapter-Factory (nicht None) -- die tatsaechliche
        # Live-SL-Anbindung (03 §7, OPENWEBUI_API_KEY etc.) bleibt ein
        # separates Setup; ohne sie liefert der erste Aufruf eine klare
        # Fehlermeldung statt eines stillen Spielstarts.
        gm_transport_factory=_default_gm_transport_factory(data_dir, _REPO_ROOT),
        # A1: echte Factory statt None -- ohne MMO_SIM_PERSONA_CLI/_API_*
        # Umgebungskonfiguration liefert der erste Persona-Einladungsversuch
        # eine klare Fehlermeldung (s. `_default_persona_driver_factory`).
        persona_driver_factory=_default_persona_driver_factory(data_dir),
    )
    try:
        return session.run()
    except KeyboardInterrupt:
        print("\n  Pausiert (Ctrl-C) — kein weiterer Modellaufruf.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
