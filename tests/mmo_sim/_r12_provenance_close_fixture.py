#!/usr/bin/env python3
"""
tests/mmo_sim/_r12_provenance_close_fixture.py — gemeinsamer Testhelper fuer
`test_r12_provenance_close_*.py` (R12-W75: positive F02-Wiederaufnahme-
bindung auf dem W74-Resultat).

FIXTURE_ONLY (kein Produktcode kennt diese Datei): kapselt das wiederholt
gebrauchte Testmuster "ECHTER, VOR dem F02-PROVENANCE-Fix geschriebener
Legacy-Korrekturdatensatz OHNE `bound_block`-Schluessel" (direkt ueber
`save_correction._write_record` konstruiert, NIE ueber `load_or_init_
record`/`begin_attempt`, die den Schluessel seit W74 IMMER mitschreiben --
s. `mmo_sim/core/save_correction.py:load_or_init_record` Docstring) und
"ein echter, via `request_ledger.begin`/`finish_received` abgeschlossener
Requestdatensatz, dessen `result_text` einen bestimmten Block fuer eine
bestimmte Figur traegt" (fuer die neue `_verify_legacy_provenance`-
Positivbindung in `pursue_single_figure_correction`)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from _full_v7_fixture import full_v7_save

import mmo_sim.core.request_ledger as request_ledger
import mmo_sim.core.save_correction as save_correction


def wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    """Schema-ungueltig (identisches Muster zu `test_r12_window_hold_single_
    figure.py:_wallet_as_number`): `economy.wallets.*` als blanke Zahl statt
    Objekt -- der genaue Defekt spielt fuer diese Suite keine Rolle, nur
    dass die ERSTE Validierung scheitert und eine reine Formatkorrektur
    (ohne inhaltliche Drift) ueber denselben Identitaets-/Namenswert moeglich
    bleibt."""
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def write_legacy_hold_record(
    run_dir: str | Path, *, repair_key: str, persona_key: str, char_id: str, operation_key: str,
    table_id: str | None = None, section_id: str | None = None, attempts_used: int, last_reason: str,
    errors: list[str] | None = None, state: str = "hold",
) -> dict:
    """Konstruiert einen ECHTEN Legacy-Korrekturdatensatz GENAU wie die alte,
    VOR dem W74-Fix aktive `mark_hold`-Logik ihn geschrieben haette -- OHNE
    jeden `"bound_block"`-Schluessel (nicht einmal `None`; die blosse
    Schluessel-ABWESENHEIT ist das Signal, das `pursue_single_figure_
    correction`s `"bound_block" in record`-Zweig unterscheidet, s. dort).
    Schreibt direkt ueber `save_correction._write_record` -- `load_or_init_
    record`/`begin_attempt`/`_reset_for_next_attempt` wuerden den Schluessel
    (seit W74) IMMER mitschreiben und sind deshalb fuer dieses Testmuster
    NICHT geeignet."""
    data = {
        "repair_key": repair_key, "persona_key": persona_key, "char_id": char_id,
        "operation_key": operation_key, "table_id": table_id, "section_id": section_id,
        "generation": None, "errors": list(errors or []),
        "attempts_used": attempts_used, "state": state,
        "created_ts": time.time(), "updated_ts": time.time(),
        "last_request_id": None, "last_reason": last_reason,
    }
    save_correction._write_record(run_dir, repair_key, data)
    return dict(data)


def seed_original_request(
    run_dir: str | Path, *, participant: str, table_id: str | None, section_id: str | None,
    role: str, turn_idx: int, evidence_block: dict,
) -> str:
    """Legt einen ECHTEN, vollstaendig abgeschlossenen (`state="accounted"`)
    Requestledger-Datensatz fuer GENAU diese Operationsidentitaet an, dessen
    `result_text` den uebergebenen Block als fenced-JSON-SL-Antworttext
    traegt -- die Quelle, gegen die `_verify_legacy_provenance`s
    Domainreader-Extraktion (`save_correction_domain.extract_checked_
    single`) tatsaechlich prueft. Liefert die `request_id` (fuer
    `original_request_id`)."""
    request_id = request_ledger.begin(
        run_dir, role=role, content=f"onboarding-turn-{turn_idx}", reserved_usd=0.0,
        turn_idx=turn_idx, participant=participant, table_id=table_id, section_id=section_id,
    )
    sl_text = "```json\n" + json.dumps(evidence_block) + "\n```"
    request_ledger.finish_received(run_dir, request_id, usage={}, seconds=0.01, result_text=sl_text)
    return request_id


class ExplodingGm:
    """Wie die bereits bestehenden `_ExplodingGm`-Testdoppel (z.B.
    `test_r12_window_hold_single_figure.py`) -- jeder Transport-Call ist in
    den HOLD-vor-Transport-Faellen dieser Suite ein Testfehler."""

    def __init__(self):
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        raise AssertionError("unerwarteter Transport-Call -- dieser Pfad muss VOR jedem Versand HOLD halten.")


class ScriptedGm:
    """Wie `test_r12_window_hold_single_figure.py:_ScriptedGm` -- liefert
    der Reihe nach vorbereitete Antworten, wirft bei einem unerwarteten
    zusaetzlichen Call."""

    def __init__(self, contents):
        self._contents = list(contents)
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if not self._contents:
            raise AssertionError("unerwarteter zusaetzlicher Transport-Call (keine weitere gescriptete Antwort).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}
