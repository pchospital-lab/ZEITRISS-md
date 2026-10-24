#!/usr/bin/env python3
"""
mmo_sim/core/save_compatibility.py — generische Orchestrierung für den
Save-/Load-Komfortvertrag (ZR-SAVECOMPAT-TERMINAL-20261016-R1,
02_SAVEVERTRAG.md §C/§D). ZEITRISS-spezifisches Wissen (Wallet-Projektion,
Kompatibilitätsumschlag-Form, Kandidatenauswahl/-merge) kommt ausschließlich
aus `domain.zeitriss.save_compatibility` (`save_compatibility_domain` unten)
-- dieses Modul kennt selbst keine ZEITRISS-Feldnamen, nur Dateipfade/
Zustand, genau wie `core/save_correction.py` seine Domänenschicht trennt.

Drei Verantwortlichkeiten:
  1. Rohsicherung (02.C): JEDE rohe SL-Antwort einer Korrekturoperation wird
     append-only unter `run_dir/save_corrections_raw/<repair_key>.json`
     gesichert -- unabhängig davon, ob sie später akzeptiert/verworfen/
     mehrdeutig war. Eigener, dedizierter Archivpfad (NICHT der generische
     `request_ledger`, der bleibt unverändert/unangetastet).
  2. Kompatibilitätsexport (02.D): nach endgültig erschöpftem
     Korrekturbudget wird ein versionierter Kompatibilitätsumschlag
     geschrieben -- NIE kanonisch, aber sofort terminal-exportier-/
     importierbar, App bleibt benutzbar.
  3. Kompatibilitätsladeweg (02.D): bounded (nie endlos), KI-SL-gestützte
     Reparatur VOR jeder abhängigen Spielaktion, dann ATOMARER Store-
     Commit über das bereits vorhandene `store.publish_current_save`
     (KEIN neuer Store-Schreibpfad -- "erweitern, nicht neu bauen")."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import store
from .admission import _atomic_write_json
from ..domain.zeitriss import save_compatibility as save_compatibility_domain
from ..domain.zeitriss import onboarding as onboarding_domain

#: 02.D: "je gespeicherter Operation/Loadphase dauerhaft begrenzen" -- kein
#: zweites endloses Dreierkarussell. Dieselbe Budgethöhe wie
#: `save_correction.MAX_ADDITIONAL_REQUESTS` (konsistente Nutzererwartung),
#: aber ein EIGENER, von der Korrekturschleife unabhängiger Zähler/Zustand
#: (dieser Lauf hat bereits einen Kompatibilitätsexport hinter sich, keine
#: neue Request-Bindung gegen den alten `repair_key`-Korrekturdatensatz).
MAX_COMPAT_LOAD_REPAIR_ATTEMPTS = 3


# ───────────────────────── A: Rohsicherung (append-only) ────────────────────


def _raw_archive_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "save_corrections_raw"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _raw_archive_path(run_dir: str | Path, repair_key: str) -> Path:
    safe = repair_key.replace("/", "_")
    return _raw_archive_dir(run_dir) / f"{safe}.json"


def read_raw_archive(run_dir: str | Path, repair_key: str) -> list[dict]:
    """Liest das bisher gesicherte Rohantwort-Archiv für `repair_key` --
    leere Liste, wenn (noch) keine einzige Antwort archiviert wurde."""
    import json

    p = _raw_archive_path(run_dir, repair_key)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def archive_raw_response(
    run_dir: str | Path, *, repair_key: str, char_id: str, section_id: str | None,
    table_id: str | None, attempt_no: int, request_id: str | None, raw_text: str,
) -> Path:
    """02.C: "Alle Antworten, inklusive abgeschnittener, vor der
    Weiterverarbeitung dauerhaft und append-only mit Run/Figur/Abschnitt/
    Requestbindung sichern." Append-only: liest den bisherigen Archivstand,
    HÄNGT GENAU EINEN neuen Eintrag an (nie wird ein vorhandener Eintrag
    verändert/entfernt) und schreibt das GANZE Archiv atomar zurück
    (dieselbe Temp-plus-`os.replace`-Härtung wie jeder andere Zustandswrite
    in diesem Paket, `core.admission._atomic_write_json`). Jeder Eintrag
    trägt Run (`run_dir` selbst, implizit durch den Ablagepfad),
    Figur/Abschnitt/Requestbindung -- unabhängig davon, ob `raw_text` später
    als Kandidat akzeptiert/verworfen/mehrdeutig eingestuft wird."""
    existing = read_raw_archive(run_dir, repair_key)
    entry = {
        "repair_key": repair_key, "char_id": char_id, "section_id": section_id,
        "table_id": table_id, "attempt_no": attempt_no, "request_id": request_id,
        "raw_text": raw_text, "archived_ts": time.time(),
    }
    existing.append(entry)
    _atomic_write_json(_raw_archive_path(run_dir, repair_key), existing)
    return _raw_archive_path(run_dir, repair_key)


# ──────────────────── B: Kompatibilitätsexport (02.D) ───────────────────────


def _compat_export_dir(run_dir: str | Path, repair_key: str) -> Path:
    safe = repair_key.replace("/", "_")
    d = Path(run_dir) / "save_compat" / safe
    d.mkdir(parents=True, exist_ok=True)
    return d


def latest_compat_export(run_dir: str | Path, repair_key: str) -> dict | None:
    """Liefert den zuletzt geschriebenen Kompatibilitätsumschlag für
    `repair_key`, oder `None`, wenn (noch) keiner existiert. "Der
    Kompatibilitätsexport und letzte valide Stand bleiben erhalten, auch
    bei Prozessende während der Übernahme" (02.D) -- ein früherer Export
    wird hier NIE gelöscht/überschrieben, `build_and_write_compat_export`
    legt immer eine NEUE Versionsdatei an."""
    import json

    d = _compat_export_dir(run_dir, repair_key)
    versions = sorted((int(p.stem) for p in d.glob("*.json") if p.stem.isdigit()))
    if not versions:
        return None
    latest_path = d / f"{versions[-1]:04d}.json"
    return json.loads(latest_path.read_text(encoding="utf-8"))


def build_and_write_compat_export(
    run_dir: str | Path, *, repair_key: str, char_id: str, participant_id: str, operation_key: str,
    table_id: str | None, section_id: str | None, best_view: dict | None, last_valid: dict | None,
    progress_evidence: list[dict] | None = None, conflicts: list[dict] | None = None,
    extensions: dict | None = None, errors: list[str] | None = None, provenance: dict | None = None,
    created_ts: float,
) -> tuple[dict, Path]:
    """02.D: baut EINEN neuen, versionierten Kompatibilitätsumschlag
    (`raw_responses` IMMER frisch aus dem bereits vorhandenen Roharchiv
    gelesen, s. `read_raw_archive` -- kein zweiter Rohantwort-Speicher) und
    schreibt ihn ATOMAR unter einer NEUEN Versionsnummer (nie
    überschreibend, s. `latest_compat_export`-Docstring). Liefert
    `(envelope, path)`; der Aufrufer (TUI/Terminal-Export-Kommando) ist für
    die Nutzermeldung "Gesichert mit Prüfhinweisen" zuständig -- diese
    Funktion schreibt nur die Datei, zeigt nichts an."""
    d = _compat_export_dir(run_dir, repair_key)
    existing = sorted((int(p.stem) for p in d.glob("*.json") if p.stem.isdigit()))
    version = (existing[-1] + 1) if existing else 1
    envelope = save_compatibility_domain.build_compat_envelope(
        envelope_version=version, repair_key=repair_key, char_id=char_id, participant_id=participant_id,
        operation_key=operation_key, table_id=table_id, section_id=section_id,
        raw_responses=read_raw_archive(run_dir, repair_key), best_view=best_view, last_valid=last_valid,
        progress_evidence=progress_evidence, conflicts=conflicts, extensions=extensions, errors=errors,
        provenance=provenance, created_ts=created_ts,
    )
    validation_errors = save_compatibility_domain.validate_compat_envelope(envelope)
    if validation_errors:
        raise ValueError(f"Kompatibilitätsumschlag strukturell ungültig: {validation_errors}")
    path = d / f"{version:04d}.json"
    _atomic_write_json(path, envelope)
    return envelope, path


# ───────────────────── C: Kompatibilitätsladeweg (02.D) ─────────────────────


def _compat_load_records_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "save_compat_load"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _compat_load_record_path(run_dir: str | Path, repair_key: str) -> Path:
    safe = repair_key.replace("/", "_")
    return _compat_load_records_dir(run_dir) / f"{safe}.json"


def load_or_init_compat_load_record(run_dir: str | Path, repair_key: str) -> dict:
    """Restart-fest, identisches Muster zu `save_correction.load_or_init_
    record`: ein bereits vorhandener Datensatz wird UNVERÄNDERT
    zurückgegeben, `attempts_used` bleibt über einen Prozessneustart
    erhalten -- derselbe Loadversuch wird NICHT doppelt gezählt."""
    import json

    p = _compat_load_record_path(run_dir, repair_key)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    data = {
        "repair_key": repair_key, "attempts_used": 0, "state": "pending",
        "created_ts": time.time(), "updated_ts": time.time(), "last_reason": None,
    }
    _atomic_write_json(p, data)
    return data


def _write_compat_load_record(run_dir: str | Path, repair_key: str, data: dict) -> None:
    data = dict(data, updated_ts=time.time())
    _atomic_write_json(_compat_load_record_path(run_dir, repair_key), data)


@dataclass
class CompatLoadOutcome:
    """`status`: "adopted" (kanonisch übernommen + atomar veröffentlicht),
    "hold" (bounded Reparatur ausgeschöpft oder keine Reparaturfunktion
    verfügbar -- App bleibt benutzbar, letzter Kompatibilitätsstand bleibt
    erhalten, s. Aufrufer-Docstring in `attempt_compat_load`)."""

    status: str
    block: dict | None = None
    reason: str = ""
    open_issues: list[str] = field(default_factory=list)
    repair_rounds_used: int = 0


def attempt_compat_load(
    run_dir: str | Path, *, repair_key: str, char_id: str, participant_id: str,
    states_dir: str | Path, schema_path: str | Path, envelope: dict,
    repair_fn: Callable[[dict, list[str]], dict | None] | None,
    max_attempts: int = MAX_COMPAT_LOAD_REPAIR_ATTEMPTS,
) -> CompatLoadOutcome:
    """02.D Compat-Ladeweg: nimmt den Kompatibilitätsumschlag `envelope`
    (s. `domain.save_compatibility.build_compat_envelope`), normalisiert/
    repariert VOR jeder abhängigen Spielaktion und schreibt bei Erfolg
    ATOMAR über das bereits vorhandene `store.publish_current_save` fort
    (identischer Weg wie eine bestätigte Import-Übernahme, `ui/tui.py:
    _cmd_import` -- kein neuer Store-Schreibpfad). Bounded: höchstens
    `max_attempts` Reparaturrunden ÜBER DIESEN AUFRUF HINWEG (restart-fest
    über `load_or_init_compat_load_record`), danach kontrolliertes HOLD --
    "kein zweites endloses Dreierkarussell" (02.D). Ein kompatibel
    gesicherter Save, der (noch) nicht automatisch reparierbar ist, ist
    KEIN Endlosfehler: HOLD lässt die App benutzbar, der letzte
    Kompatibilitätsstand bleibt unverändert auf Platte.

    `repair_fn(candidate, open_issues) -> dict | None` ist injiziert (KEIN
    echter Modellaufruf/keine Persona-API in diesem Paket, s. harte
    Grenzen) -- liefert `None`, wenn keine Verbesserung möglich ist (sofort
    HOLD, kein weiterer Versuch verschwendet)."""
    from ..domain.zeitriss import save_validation as save_validation_lib

    record = load_or_init_compat_load_record(run_dir, repair_key)
    if record["state"] in ("adopted", "hold"):
        return CompatLoadOutcome(
            status=record["state"], reason=record.get("last_reason") or "",
            repair_rounds_used=record.get("attempts_used", 0),
        )

    candidate = envelope.get("last_valid") or envelope.get("best_view")
    if candidate is None:
        record["state"] = "hold"
        record["last_reason"] = "no_usable_view_in_envelope"
        _write_compat_load_record(run_dir, repair_key, record)
        return CompatLoadOutcome(status="hold", reason="no_usable_view_in_envelope")

    rounds_used = record.get("attempts_used", 0)
    open_issues: list[str] = []
    while True:
        outcome = save_compatibility_domain.evaluate_with_wallet_projection(candidate, char_id)
        if outcome.accepted:
            ps_store_cls = _persona_state_store_cls()
            ps_store = ps_store_cls(schema_path=schema_path)
            onboarding_domain.ensure_participant_persona_state(
                ps_store, states_dir, participant_id, char_id, outcome.canonical_block,
            )
            store.publish_current_save(run_dir, participant_id, outcome.canonical_block, ps_store, states_dir)
            record["state"] = "adopted"
            record["last_reason"] = None
            record["attempts_used"] = rounds_used
            _write_compat_load_record(run_dir, repair_key, record)
            return CompatLoadOutcome(
                status="adopted", block=outcome.canonical_block, repair_rounds_used=rounds_used,
            )
        open_issues = list(outcome.acceptance.feedback_items)
        if rounds_used >= max_attempts or repair_fn is None:
            reason = "compat_load_attempts_exhausted" if rounds_used >= max_attempts else "repair_unavailable"
            record["state"] = "hold"
            record["last_reason"] = reason
            record["attempts_used"] = rounds_used
            _write_compat_load_record(run_dir, repair_key, record)
            return CompatLoadOutcome(
                status="hold", reason=reason, open_issues=open_issues, repair_rounds_used=rounds_used,
            )
        rounds_used += 1
        record["attempts_used"] = rounds_used
        record["state"] = "repairing"
        _write_compat_load_record(run_dir, repair_key, record)
        repaired = repair_fn(candidate, open_issues)
        if repaired is None or not isinstance(repaired, dict):
            record["state"] = "hold"
            record["last_reason"] = "repair_fn_returned_no_candidate"
            _write_compat_load_record(run_dir, repair_key, record)
            return CompatLoadOutcome(
                status="hold", reason="repair_fn_returned_no_candidate",
                open_issues=open_issues, repair_rounds_used=rounds_used,
            )
        candidate = repaired


def _persona_state_store_cls():
    from .persona_state import PersonaStateStore

    return PersonaStateStore
