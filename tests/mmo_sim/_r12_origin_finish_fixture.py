#!/usr/bin/env python3
"""
tests/mmo_sim/_r12_origin_finish_fixture.py — gemeinsamer Testhelper fuer
`test_r12_origin_finish_*.py` (R12-W76: F02-Herkunftsabschluss -- R01
Null-Binding, R02 Durable-Erfolgspraedikat, R03-SHAPE Gruppenpfad).

FIXTURE_ONLY (kein Produktcode kennt diese Datei): ergaenzt die bereits
bestehenden `_r12_provenance_close_fixture.py`/`_r12_window_hold_fixture.py`-
Helfer um die beiden synthetischen Requestledger-Formen, die fuer den R02-
Fix gebraucht werden (ein durabler Record MIT `error` trotz passendem
Text, und ein noch offener/unbeantworteter Record) -- beide werden NIE
ueber den regulaeren `begin()`/`finish_received()`/`finish_error()`-Weg
allein erzeugt (der Produktcode selbst schreibt `result_text`+`error`
niemals gleichzeitig), sondern bewusst direkt ueber `request_ledger.
_write_request` konstruiert (synthetische Gegenbelege, analog
`_r12_provenance_close_fixture.write_legacy_hold_record`)."""
from __future__ import annotations

import json
from pathlib import Path

import mmo_sim.core.request_ledger as request_ledger


def seed_error_origin_request(
    run_dir: str | Path, *, participant: str, table_id: str | None, section_id: str | None,
    role: str, turn_idx: int, evidence_block: dict, error: str = "SYNTHETIC_ORIGIN_TRANSPORT_ERROR",
) -> str:
    """Ein `state="accounted"`-Requestdatensatz, dessen `result_text` einen
    gueltig extrahierbaren Block traegt, ABER dessen `error`-Feld GESETZT
    ist -- R02: ein passender Text MIT Fehler ist KEINE erfolgreiche
    Originalantwort. Liefert die `request_id`."""
    request_id = request_ledger.begin(
        run_dir, role=role, content=f"onboarding-turn-{turn_idx}", reserved_usd=0.0,
        turn_idx=turn_idx, participant=participant, table_id=table_id, section_id=section_id,
    )
    data = request_ledger.load_request(run_dir, request_id)
    data["state"] = "accounted"
    data["error"] = error
    data["result_text"] = "```json\n" + json.dumps(evidence_block) + "\n```"
    request_ledger._write_request(run_dir, request_id, data)
    return request_id


def seed_unresolved_origin_request(
    run_dir: str | Path, *, participant: str, table_id: str | None, section_id: str | None,
    role: str, turn_idx: int,
) -> str:
    """Ein Requestdatensatz, der NIE `finish_received`/`finish_error`
    erreicht hat (`state` bleibt `"reserved"`/`"sent"`, `result_text` bleibt
    `None`) -- R02: ein unklarer/offener Zustand ohne Text ist KEINE
    erfolgreiche Originalantwort, egal welche Identitaet uebergeben wird.
    Liefert die `request_id`."""
    return request_ledger.begin(
        run_dir, role=role, content=f"onboarding-turn-{turn_idx}", reserved_usd=0.0,
        turn_idx=turn_idx, participant=participant, table_id=table_id, section_id=section_id,
    )
