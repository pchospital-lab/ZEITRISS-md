#!/usr/bin/env python3
"""
mmo_sim/core/request_ledger.py — persistenter Pro-Request-Datensatz (I2-
Nachzug, WEGKARTE-MAIN.md/PLAN-CRITIC.md/MAIN-ENTSCHEIDUNG.md).

EIN schlanker persistenter Requestauftrag pro Modellanfrage: eine kleine
Datei je Request unter `run_dir/requests/<id>.json` (Auflage 2, PLAN-
CRITIC F4, bindend: NICHT in `lab.status.json`/`LabStatus` — dessen
Dataclass-Konstruktor (`lab/runner.read_status`) bricht bei jedem
unbekannten Top-Level-Key, drei externe Suiten + `ui/tui.py:_cmd_settings`
lesen dieselbe Datei). Zustandsmaschine:

    reserved -> sent -> received | error -> accounted

`begin()` deckt reserved+sent in einem Schritt ab und committet die
Reservierung UNMITTELBAR VOR dem tatsaechlichen Adapter-/Transport-Aufruf
in `lab.status.json` (`core.admission.record_turn_usage`, EIN Turn/EIN
reservierter USD-Betrag) — ab diesem Zeitpunkt gilt das Budget als
verbraucht, UNABHAENGIG davon, ob je eine Antwort eintrifft (Case 05: eine
verlorene Antwort nach nachweislich abgesandtem Request darf Verbrauch und
offene Verpflichtung nicht auf 0 zuruecksetzen — ein Resume mit frischem
Budgetstand wuerde sonst blind erneut senden). `finish_received()`/
`finish_error()` schreiben NUR den beobachteten Ausgang fest (Audit/
Nachweis) und tragen die tatsaechlich gemessene Latenz nach
(`core.admission.add_seconds`) — sie fassen `turns_used`/`usd_spent` NICHT
noch einmal an (kein Doppel-Anrechnen derselben Anfrage, Auflage 6).

Serieller Writer: dieselbe PID-Lock-Singleton-Garantie wie `lab/runner.py`
deckt bereits ab, dass pro `run_dir` nur EIN schreibender Controller aktiv
ist — kein neuer DB-/Scheduler-Mechanismus noetig (WEGKARTE §"Erhalten")."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path

from .admission import add_seconds, record_turn_usage


def _requests_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "requests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _request_path(run_dir: str | Path, request_id: str) -> Path:
    return _requests_dir(run_dir) / f"{request_id}.json"


def load_request(run_dir: str | Path, request_id: str) -> dict | None:
    p = _request_path(run_dir, request_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def open_requests(run_dir: str | Path) -> list[dict]:
    """Alle Requestdatensaetze, die NICHT `accounted` sind -- End-Critic-/
    Debug-Sicht auf offene Verpflichtungen fuer ein `run_dir` (I2:
    "End-Critic muss den implementierten Requestdatensatz + echte
    Wiederaufnahme sehen")."""
    d = Path(run_dir) / "requests"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("state") != "accounted":
            out.append(data)
    return out


def _write_request(run_dir: str | Path, request_id: str, data: dict) -> None:
    _request_path(run_dir, request_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8",
    )


def begin(
    run_dir: str | Path, *, role: str, content: str, reserved_usd: float | None,
    route: str | None = None, output_limit_tokens: float | None = None,
    table_id: str | None = None, section_id: str | None = None,
) -> str:
    """Legt den Requestdatensatz an (state=reserved), committet die
    Reservierung SOFORT in `lab.status.json` und markiert state=sent — ALLES
    VOR dem eigentlichen Adapter-/Transport-Aufruf (der Aufrufer ruft
    `begin()` unmittelbar davor auf). `content` ist der TATSAECHLICH zu
    sendende Text (Hash+Laenge, kein Klartext-Volldump — Auditbeleg ohne
    zusaetzliches Datenschutzrisiko). Liefert die `request_id` fuer
    `finish_received`/`finish_error`."""
    request_id = uuid.uuid4().hex
    content = content or ""
    data = {
        "id": request_id,
        "role": role,
        "route": route,
        "content_chars": len(content),
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "output_limit_tokens": output_limit_tokens,
        "reserved_usd": reserved_usd,
        "table_id": table_id,
        "section_id": section_id,
        "state": "reserved",
        "reserved_ts": time.time(),
        "sent_ts": None,
        "settled_ts": None,
        "usage": None,
        "error": None,
    }
    _write_request(run_dir, request_id, data)
    # Case 05 (bindend): die Reservierung wird VOR dem Versand committet --
    # ein Timeout/Verbindungsabbruch NACH diesem Punkt darf turns_used/
    # usd_spent nicht unberuehrt lassen (sonst blockiert ein zweiter Versuch
    # nicht, obwohl bereits real gesendet wurde).
    record_turn_usage(run_dir, 0.0, reserved_usd)
    data["state"] = "sent"
    data["sent_ts"] = time.time()
    _write_request(run_dir, request_id, data)
    return request_id


def finish_received(run_dir: str | Path, request_id: str, *, usage: dict | None = None, seconds: float = 0.0) -> None:
    """Erfolgreich beantworteter Request. `turns_used`/`usd_spent` wurden
    bereits in `begin()` committet (kein zweites Anrechnen) -- hier wird nur
    die reale Latenz nachgetragen und der Datensatz final auf `accounted`
    gesetzt (idempotent: ein erneuter Aufruf fuer dieselbe `request_id`
    aendert nichts mehr, da `load_request` bereits `accounted` liefert und
    der Aufrufer diese Funktion je `request_id` genau einmal aufruft)."""
    data = load_request(run_dir, request_id)
    if data is None or data.get("state") == "accounted":
        return
    data["state"] = "received"
    data["usage"] = usage
    data["settled_ts"] = time.time()
    _write_request(run_dir, request_id, data)
    add_seconds(run_dir, seconds)
    data["state"] = "accounted"
    _write_request(run_dir, request_id, data)


def finish_error(run_dir: str | Path, request_id: str, *, error: object, seconds: float = 0.0) -> None:
    """Versand fand statt (state war bereits `sent`), aber keine
    verwertbare Antwort (Timeout/Transportfehler/Ausnahme) -- die bereits in
    `begin()` committete Reservierung bleibt UNANGETASTET (kein Refund,
    Case 05: 'Versuch + reservierte Verpflichtung bei fehlender Antwort
    bleiben erhalten'). Der Datensatz wechselt nach `error` und sofort
    weiter nach `accounted` (die lokale Buchung fuer DIESE Anfrage ist
    damit abschliessend — ein spaeterer Retry ist ein NEUER Request mit
    eigener Reservierung, kein Wiederaufsetzen auf demselben Datensatz)."""
    data = load_request(run_dir, request_id)
    if data is None or data.get("state") == "accounted":
        return
    data["state"] = "error"
    data["error"] = str(error)[:500]
    data["settled_ts"] = time.time()
    _write_request(run_dir, request_id, data)
    add_seconds(run_dir, seconds)
    data["state"] = "accounted"
    _write_request(run_dir, request_id, data)
