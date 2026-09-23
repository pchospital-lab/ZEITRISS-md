#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS MMO-Sim — TUI-Einstiegspunkt (analog `zeitriss.py`-Shim, P2 M3).

Duenner Shim: die eigentliche Terminal-Logik liegt in `mmo_sim/ui/tui.py`.
Aufruf: `python scripts/mmo_sim.py [--participant <id>]`.

Kein Browser fuers Spielen (11 §7). Ohne `--participant` wird — sofern unter
`--data-dir` bereits ein Teilnehmer bekannt ist — DIESER wiederverwendet
(P2-Fertigstellung I3, REVIEW-P2.md Test 07: "Normaler Neustart ohne
Sonderargument darf nicht neue Identitaet erzeugen"); nur beim allerersten
Lauf fuer ein `--data-dir` wird eine neue Teilnehmer-ID erzeugt."""
from __future__ import annotations

import argparse
import json
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


def _default_persona_driver_factory(data_dir: Path):
    """A1 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER, verifiziert `scripts/mmo_sim.py:94`):
    echte `persona_driver_factory` -- analog `_default_gm_transport_factory`,
    kein stiller Fallback. Waehlt je nach Umgebungskonfiguration entweder das
    Hybrid-Profil (`claude_code_local`, `MMO_SIM_PERSONA_CLI` gesetzt) oder das
    API-Profil (`openai_compatible`, `MMO_SIM_PERSONA_API_*` gesetzt). Ohne
    eine der beiden Konfigurationen wirft die Konstruktion eine klare
    Fehlermeldung -- `_cmd_local_round` faengt das bereits ab (kein
    Spielstart), exakt wie bei `gm_transport_factory`."""

    def factory(persona_key: str):
        import os
        cli_binary = os.environ.get("MMO_SIM_PERSONA_CLI")
        api_base_url = os.environ.get("MMO_SIM_PERSONA_API_BASE_URL")
        if cli_binary:
            from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver
            isolated_workdir = os.environ.get("MMO_SIM_PERSONA_ISOLATED_WORKDIR") or str(data_dir / "persona_workdir")
            Path(isolated_workdir).mkdir(parents=True, exist_ok=True)
            extra_flags_raw = os.environ.get("MMO_SIM_PERSONA_ISOLATION_FLAGS", "")
            extra_flags = [f for f in extra_flags_raw.split(",") if f]
            config = ClaudeCodeConfig(
                binary=cli_binary, isolated_workdir=isolated_workdir,
                extra_isolation_flags=extra_flags,
            )
            return PersonaClaudeCodeDriver(config, persona_key)
        if api_base_url:
            from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver
            config = PersonaApiConfig(
                base_url=api_base_url,
                api_key=os.environ.get("MMO_SIM_PERSONA_API_KEY", ""),
                model=os.environ.get("MMO_SIM_PERSONA_API_MODEL", ""),
            )
            return PersonaApiDriver(config, persona_key)
        raise RuntimeError(
            "Persona-Anbindung nicht konfiguriert (weder MMO_SIM_PERSONA_CLI "
            "noch MMO_SIM_PERSONA_API_BASE_URL gesetzt) -- kein stiller "
            "Fallback, kein Persona-Spielstart (03 §1/§4)."
        )

    return factory


def _default_gm_transport_factory(data_dir: Path):
    """F5/K2 (WEGKARTE §6): echter Adapter-Factory statt hartverdrahtetem
    `None`. Baut -- NUR bei tatsaechlichem Aufruf durch `TuiSession.
    _cmd_local_round` (nicht bei Programmstart/Definition) -- einen echten
    `GmOwuiTransport` gegen den bestehenden P1-SL-Client
    (`internal/qa/harness/agent_mp/sl_client.py`). Ohne live konfigurierte
    SL-Anbindung (`OPENWEBUI_API_KEY` etc.) wirft die Konstruktion eine klare
    Fehlermeldung, die `_cmd_local_round` bereits abfaengt ('SL-Anbindung
    nicht verfuegbar — kein Spielstart') -- kein stiller Fallback, keine
    echte Inferenz bei blossem Programmstart oder Menue-Anzeige.

    A6/D3 (WEGKARTE §8, Plan-Critic A6, Test 10): `factory(table_id)` reicht
    die aufrufende Tisch-Identitaet an `GmOwuiTransport` durch -- jeder
    Tisch bekommt eine EIGENE `sl_history.jsonl` (Unterverzeichnis desselben
    `data_dir/run`-Stores), kein geteilter Verlauf/Chat fuer verschiedene
    Tische im selben `--data-dir`."""

    def factory(table_id: str):
        from mmo_sim.adapters.gm_owui import GmOwuiTransport
        sl_client_path = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"
        return GmOwuiTransport(sl_client_path, data_dir / "run", table_id=table_id)

    return factory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ZEITRISS MMO-Sim Terminaloberflaeche")
    parser.add_argument("--participant", default=None, help="bestehende Teilnehmer-ID (sonst wird die zuletzt genutzte wiederverwendet bzw. beim allerersten Lauf eine neue erzeugt)")
    parser.add_argument("--data-dir", default=str(_REPO_ROOT / "internal" / "mmo_sim_data"),
                         help="Datenverzeichnis fuer Onboarding-/Katalog-Journale")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
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
        gm_transport_factory=_default_gm_transport_factory(data_dir),
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
