#!/usr/bin/env python3
"""
mmo_sim/core/table_admission.py — host-autoritativer Pre-Start-Tisch-Dienst
(ZR-FIGURENREISE-TISCH-20261102-R1, Teilpaket A, design.md §1).

Schmal, generisch, persistent, atomar über `core.admission._atomic_write_json`
(dieselbe Härtung wie `request_ledger`/`save_corrections`). KEINE ZEITRISS-
Feldnamen -- nur Teilnehmer-IDs, Tisch-Key, Zustand, exakt dieselbe
Domänentrennung wie `save_correction.py`/`save_compatibility.py`.

Die hier verwaltete Hostautorität ist AUSDRÜCKLICH SEPARAT von der später im
Spielpfad abgeleiteten Leaderrolle (`store.derive_group_and_leader`, entsteht
erst aus der ersten voll angenommenen Offer) -- dieses Modul berührt
`store.py` nicht. Jede host-only Transition prüft `host_id` GEGEN den
persistierten Record (`record["host_id"]`), NIE gegen einen Parameter-
Glauben des Aufrufers.

Ablage: `run_dir/table_admission/<table_key>.json`. Record-Form:
    {
      "table_key", "host_id", "roster": [host_id, ...],
      "requests": [guest_id, ...], "state": "open" | "started" | "closed",
      "created_ts", "updated_ts",
      "log": [ {ts, actor, action, target}, ... ],  # append-only Audit
    }

Restart-fest: ein vorhandener Record wird von JEDER Funktion UNVERÄNDERT
geladen (nie 0-reset) -- nur `offer_table` legt bei fehlendem Record einen
frischen an.

KEIN TUI-Wiring in diesem Modul (Teilpaket A) -- die Übergabe an den
bestehenden Spielpfad (`store.create_table_from_offer_log` +
`app_service.run_play_session`) macht ein späteres Stage-4-Wiring, um
Kollisionen in `tui.py` zu vermeiden (design.md §1)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .admission import _atomic_write_json, _table_stop_path, read_table_stop


class TableAdmissionError(RuntimeError):
    """Allgemeiner Fehler eines Tisch-Admission-Übergangs (unbekannter
    Tisch, ungültiger Zustand für die angeforderte Operation, Host-
    Selbstentfernung, ...). Basisklasse für `HostAuthorityError`."""


class HostAuthorityError(TableAdmissionError):
    """Eine HOST-ONLY-Transition (`accept_request`/`reject_request`/
    `remove_member`/`start_table`) wurde mit einem `host_id` aufgerufen, der
    NICHT mit dem persistierten `record["host_id"]` übereinstimmt."""


class OperatorAuthorityError(TableAdmissionError):
    """ZR-BETREIBER O6: ein Betreiber-Stop (`request_table_stop`) wurde von
    einem `operator_id` verlangt, der NICHT der gebundene Betreiber (= Host)
    dieses Tisches ist, oder fuer einen Tisch, dessen Admission-Record nicht
    auf die angegebene Store-`table_id` gebunden ist. Ein fremder Aufrufer
    darf einen fremden Tisch nicht stoppen."""


STATE_OPEN = "open"
STATE_STARTED = "started"
STATE_CLOSED = "closed"


def _records_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "table_admission"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(run_dir: str | Path, table_key: str) -> Path:
    safe = table_key.replace("/", "_")
    return _records_dir(run_dir) / f"{safe}.json"


def load_record(run_dir: str | Path, table_key: str) -> dict | None:
    """Restart-fest: liest den persistierten Record unverändert von der
    Platte. `None`, wenn für `table_key` noch nie ein Tisch angeboten wurde."""
    p = _record_path(run_dir, table_key)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _write_record(run_dir: str | Path, table_key: str, data: dict) -> None:
    _atomic_write_json(_record_path(run_dir, table_key), data)


def _require_existing(run_dir: str | Path, table_key: str) -> dict:
    record = load_record(run_dir, table_key)
    if record is None:
        raise TableAdmissionError(f"kein Tisch-Record für table_key={table_key!r} -- offer_table zuerst.")
    return record


def _require_host(record: dict, host_id: str) -> None:
    if record["host_id"] != host_id:
        raise HostAuthorityError(
            f"host_id={host_id!r} ist nicht Host von table_key={record['table_key']!r} "
            f"(tatsächlicher Host: {record['host_id']!r})."
        )


def _require_open(record: dict, *, action: str) -> None:
    if record["state"] != STATE_OPEN:
        raise TableAdmissionError(
            f"Tisch {record['table_key']!r} ist nicht offen (state={record['state']!r}) -- "
            f"{action} nicht zulässig."
        )


def _append_log(record: dict, *, actor: str, action: str, target: str | None) -> None:
    log = record.setdefault("log", [])
    log.append({"ts": time.time(), "actor": actor, "action": action, "target": target})


def offer_table(run_dir: str | Path, *, host_id: str, table_key: str) -> dict:
    """Legt einen neuen Tisch an: `state="open"`, `roster=[host_id]`,
    `requests=[]`. Idempotent, wenn für `table_key` bereits ein Record mit
    DEMSELBEN `host_id` existiert (restart-fest, UNVERÄNDERT zurückgegeben --
    kein 0-Reset). Existiert bereits ein Record mit einem ANDEREN `host_id`,
    wirft `HostAuthorityError` -- ein fremder Aufrufer darf einen bestehenden
    Tisch nicht stillschweigend übernehmen."""
    existing = load_record(run_dir, table_key)
    if existing is not None:
        _require_host(existing, host_id)
        return existing
    now = time.time()
    record = {
        "table_key": table_key, "host_id": host_id, "roster": [host_id], "requests": [],
        "state": STATE_OPEN, "created_ts": now, "updated_ts": now, "log": [],
    }
    _append_log(record, actor=host_id, action="offer_table", target=table_key)
    _write_record(run_dir, table_key, record)
    return record


def request_join(run_dir: str | Path, *, table_key: str, guest_id: str) -> dict:
    """Gast-initiiert, gast-erlaubt: fügt `guest_id` zu `requests` hinzu
    (dedup). No-op, wenn `guest_id` bereits im `roster` ist (schon Mitglied).
    Nur zulässig, solange der Tisch `state="open"` ist."""
    record = dict(_require_existing(run_dir, table_key))
    if guest_id in record["roster"]:
        return record
    _require_open(record, action="request_join")
    if guest_id in record["requests"]:
        return record
    record["requests"] = [*record["requests"], guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=guest_id, action="request_join", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def withdraw_request(run_dir: str | Path, *, table_key: str, guest_id: str) -> dict:
    """Entfernt die eigene offene Anfrage von `guest_id`. No-op, wenn
    `guest_id` nicht (mehr) in `requests` steht."""
    record = dict(_require_existing(run_dir, table_key))
    if guest_id not in record["requests"]:
        return record
    record["requests"] = [g for g in record["requests"] if g != guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=guest_id, action="withdraw_request", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def accept_request(run_dir: str | Path, *, table_key: str, host_id: str, guest_id: str) -> dict:
    """HOST-ONLY (`host_id == record["host_id"]`, sonst `HostAuthorityError`
    -- geprüft gegen den persistierten Record, nie gegen den Parameter
    allein). Verschiebt `guest_id` von `requests` nach `roster` (dedup). Nur
    zulässig, solange der Tisch `state="open"` ist."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    _require_open(record, action="accept_request")
    if guest_id not in record["requests"]:
        raise TableAdmissionError(
            f"guest_id={guest_id!r} hat keine offene Anfrage an table_key={table_key!r}."
        )
    record["requests"] = [g for g in record["requests"] if g != guest_id]
    if guest_id not in record["roster"]:
        record["roster"] = [*record["roster"], guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="accept_request", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def reject_request(run_dir: str | Path, *, table_key: str, host_id: str, guest_id: str) -> dict:
    """HOST-ONLY; entfernt `guest_id` aus `requests` (no-op, wenn keine
    offene Anfrage vorliegt)."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if guest_id not in record["requests"]:
        return record
    record["requests"] = [g for g in record["requests"] if g != guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="reject_request", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def remove_member(run_dir: str | Path, *, table_key: str, host_id: str, guest_id: str) -> dict:
    """HOST-ONLY; entfernt `guest_id` aus `roster`. Der Host selbst ist NICHT
    entfernbar (`guest_id == host_id` wirft `TableAdmissionError`, auch wenn
    `host_id` korrekt ist). No-op, wenn `guest_id` nicht (mehr) im roster ist."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if guest_id == record["host_id"]:
        raise TableAdmissionError(f"Host {host_id!r} kann nicht per remove_member entfernt werden.")
    if guest_id not in record["roster"]:
        return record
    record["roster"] = [g for g in record["roster"] if g != guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="remove_member", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def leave_table(run_dir: str | Path, *, table_key: str, guest_id: str) -> dict:
    """Ein Gast entfernt sich selbst aus `roster`. Der Host kann sich NICHT
    über diesen Pfad entfernen (`guest_id == record["host_id"]` wirft
    `TableAdmissionError` -- Solo-Gate/Tischauflösung ist ein eigener,
    hier nicht gebauter Pfad, s. design.md J3). No-op, wenn `guest_id`
    nicht (mehr) im roster ist."""
    record = dict(_require_existing(run_dir, table_key))
    if guest_id == record["host_id"]:
        raise TableAdmissionError(f"Host {guest_id!r} kann den Tisch nicht über leave_table verlassen.")
    if guest_id not in record["roster"]:
        return record
    record["roster"] = [g for g in record["roster"] if g != guest_id]
    record["updated_ts"] = time.time()
    _append_log(record, actor=guest_id, action="leave_table", target=guest_id)
    _write_record(run_dir, table_key, record)
    return record


def roster(run_dir: str | Path, table_key: str) -> dict:
    """Read-only View auf den persistierten Record (lokal jeder lesbar).
    Wirft `TableAdmissionError`, wenn für `table_key` noch kein Tisch
    angeboten wurde."""
    return _require_existing(run_dir, table_key)


def list_open_tables(run_dir: str | Path) -> list[dict]:
    """R2-Nachzug (F1 §1): read-only Übersicht aller `state="open"`-Tische
    unter `run_dir/table_admission/*.json` -- die lokale Antwort auf "ein
    neuer Gast muss lokale Angebote sehen, OHNE vorher einen table_key zu
    kennen". Scannt dieselbe Ablage wie `load_record`/`roster` (kein neuer
    Store); JEDER lokal erreichbare Teilnehmer darf das lesen (dieselbe
    Lesefreigabe wie `roster`). Liefert deterministisch nach `table_key`
    sortiert, leer bei fehlendem/leerem `table_admission`-Verzeichnis."""
    d = Path(run_dir) / "table_admission"
    if not d.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(d.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("state") == STATE_OPEN:
            out.append(record)
    return out


def bind_section(run_dir: str | Path, *, table_key: str, host_id: str, section_id: str) -> dict:
    """HOST-ONLY (F2 §1): bindet die TATSAECHLICH gestartete Spielabschnitt-
    kennung (`store.create_table_from_offer_log`s real zurueckgegebene
    `table.table_id`, NICHT der Admission-`table_key`) in den persistierten
    Record zurueck (`record["section_id"]`). Idempotent bei wiederholter
    Bindung derselben `section_id` (Retry/Resume-fest, kein Fehler). Eine
    ABWEICHENDE `section_id` (neuer Folgeabschnitt nach echtem Abschluss,
    s. `close_table`) überschreibt die alte Bindung bewusst -- das ist eine
    ANDERE Operation, kein Fehlerfall (02_NACHZUG §F2: 'Ein bewusst
    gewählter neuer Folgeabschnitt ist eine ANDERE Operation')."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if record.get("section_id") == section_id:
        return record
    record["section_id"] = section_id
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="bind_section", target=section_id)
    _write_record(run_dir, table_key, record)
    return record


def close_table(run_dir: str | Path, *, table_key: str, host_id: str) -> dict:
    """HOST-ONLY (F2 §1/§2): markiert den Admission-Record als
    `state="closed"`, NACHDEM der tatsaechlich gebundene Spielabschnitt
    real abgeschlossen ist (Aufrufer -- `ui/tui.py:_cmd_table_start` --
    prueft das VOR diesem Aufruf gegen `store.Table.load(...).status`,
    dieses Modul kennt `store.py` selbst nicht). Idempotent, wenn der
    Tisch bereits `state="closed"` ist. Schliesst die in F2 benannte
    Lücke: ohne diesen Übergang blieb ein Admission-Record nach echtem
    Abschnittsabschluss für immer faelschlich `state="started"`, sodass
    ein erneuter `start_table`-Aufruf auf DERSELBEN `table_key` idempotent
    'gelang', obwohl der zugrunde liegende Abschnitt laengst zu war (statt
    den Host ehrlich auf 'geschlossen -- neues Angebot noetig' zu
    verweisen)."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if record["state"] == STATE_CLOSED:
        return record
    record["state"] = STATE_CLOSED
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="close_table", target=record.get("section_id"))
    _write_record(run_dir, table_key, record)
    return record


def find_admission_for_section(run_dir: str | Path, section_id: str) -> tuple[str | None, str | None]:
    """R3-Nachzug (F2 §2): reine Reverse-Lesefunktion -- findet `(table_key,
    host_id)` des EINEN Records, der tatsaechlich auf `section_id` gebunden
    ist (`record["section_id"] == section_id`), UNABHAENGIG vom aktuellen
    `state` (auch ein bereits `closed` liegender Record wird gefunden --
    der Aufrufer ruft `close_table` idempotent, kein Fehler). Bewusst OHNE
    Host-Filter: ein Gast-Resume (`_resume_bound_table` ist Leader- UND
    Gast-erreichbar) muss dieselbe Bindung finden koennen wie ein
    Host-Resume -- die tatsaechliche `close_table`-Transition bleibt
    trotzdem host_id-gebunden (geprueft GEGEN den hier zurueckgelieferten,
    bereits persistierten `record["host_id"]`, NIE gegen einen Aufrufer-
    Glauben). `(None, None)`, wenn kein Record auf `section_id` gebunden
    ist."""
    d = Path(run_dir) / "table_admission"
    if not d.is_dir():
        return None, None
    for path in sorted(d.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("section_id") == section_id:
            return record.get("table_key"), record.get("host_id")
    return None, None


def find_open_host_table(run_dir: str | Path, host_id: str) -> str | None:
    """R3-Nachzug (F3 §2): reine Lesefunktion -- `table_key` des EINEN
    Records, dessen tatsaechlicher Betreiber `host_id` IST (persistiertes
    `record["host_id"] == host_id`) und der aktuell noch aktiv ist
    (`state` in {open, started}), sonst `None`. Spiegelbildlich zu dem
    Zielhost-Check in `ui/tui.py:_cmd_table_request_persona` (F3 §1): dort
    darf die EIGENE Persona nur am EIGENEN/host-freien Tisch anfragen; hier
    wird in Gegenrichtung erkannt, ob eine als Persona zu TREIBENDE freie ID
    selbst ein aktiver (fremder) Betreiber ist -- ein Alias darf keinen
    anderen aktiven Bestand als Persona freigeben (F3 §2). Wie
    `find_admission_for_section` eine reine Reverse-Lesefunktion: KEIN Write,
    keine Transition, kein 0-Reset. Ein bereits `closed` liegender Record
    zaehlt NICHT (der fruehere Betreiber ist nicht mehr aktiv)."""
    d = Path(run_dir) / "table_admission"
    if not d.is_dir():
        return None
    for path in sorted(d.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("host_id") == host_id and record.get("state") in (STATE_OPEN, STATE_STARTED):
            return record.get("table_key")
    return None


def reopen_table(run_dir: str | Path, *, table_key: str, host_id: str) -> dict:
    """HOST-ONLY (R3-Nachzug F2 §3): setzt einen `state="started"`-Record
    OHNE JEMALS gebundene `section_id` zurueck auf `state="open"` --
    GENAU der Fall, dass eine Startvorbedingung (Laufumgebung/Figur/
    Zustimmung, geprueft innerhalb des bestehenden Spielpfads) scheiterte,
    BEVOR je ein Abschnitt real angelegt wurde (`store.create_table_from_
    offer_log`). Ohne diesen Rueckbau bliebe der Tisch in einer unwahren
    'gestartet'-Sackgasse eingefroren -- jede weitere `request_join`/
    `accept_request` lehnt `_require_open` sonst dauerhaft ab, obwohl NIE
    real gespielt wurde.

    Sicherheitsgrenze: ist BEREITS eine `section_id` gebunden, ist das KEIN
    fehlgeschlagener Start mehr, sondern eine reale, pausierte Teilnahme --
    `reopen_table` wirft dann `TableAdmissionError` (kein Rueckbau; der
    Aufrufer behandelt das defensiv, s. `ui/tui.py:_cmd_table_start`). No-op
    (liefert den Record unveraendert), wenn der Zustand bereits NICHT
    `state="started"` ist (idempotent/restart-fest wie jede andere
    Transition hier)."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if record["state"] != STATE_STARTED:
        return record
    if record.get("section_id"):
        raise TableAdmissionError(
            f"Tisch {table_key!r} hat bereits eine gebundene Abschnittskennung "
            f"({record['section_id']!r}) -- kein Rueckbau auf 'open' (reale Teilnahme, "
            "kein fehlgeschlagener Start)."
        )
    record["state"] = STATE_OPEN
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="reopen_table", target=None)
    _write_record(run_dir, table_key, record)
    return record


def start_table(run_dir: str | Path, *, table_key: str, host_id: str) -> dict:
    """HOST-ONLY; `state="started"`, friert roster/requests ein (jede
    weitere `request_join`/`accept_request`/`reject_request`-Mutation lehnt
    danach mit `TableAdmissionError` ab, s. `_require_open`). Idempotent,
    wenn der Tisch bereits `state="started"` ist (restart-fest). Ein bereits
    `state="closed"` liegender Tisch kann nicht erneut gestartet werden.

    Die tatsächliche Übergabe an den bestehenden Spielpfad
    (`store.create_table_from_offer_log` + `app_service.run_play_session`)
    macht das TUI-Wiring SPÄTER (design.md §1) -- hier wird nur der
    Zustandsübergang + der zu diesem Zeitpunkt eingefrorene roster
    geliefert."""
    record = dict(_require_existing(run_dir, table_key))
    _require_host(record, host_id)
    if record["state"] == STATE_STARTED:
        return record
    if record["state"] == STATE_CLOSED:
        raise TableAdmissionError(f"Tisch {table_key!r} ist geschlossen -- kann nicht erneut gestartet werden.")
    record["state"] = STATE_STARTED
    record["updated_ts"] = time.time()
    _append_log(record, actor=host_id, action="start_table", target=None)
    _write_record(run_dir, table_key, record)
    return record


def request_table_stop(
    run_dir: str | Path, *, table_key: str, operator_id: str, table_id: str,
    reason: str | None = None,
) -> dict:
    """ZR-BETREIBER O2/O3/O6 (2026-11-03): setzt einen DURABLEN, tisch-
    adressierten Betreiber-Stop fuer genau die Store-`table_id` dieses
    Tisches. AUTORITAET (O6): `operator_id` MUSS der persistierte Betreiber
    (= `record["host_id"]`) von `table_key` sein, UND der Record MUSS bereits
    auf eben diese `table_id` gebunden sein (`record["section_id"] ==
    table_id`, s. `bind_section` -- die fruehe Identitaetsbindung VOR dem
    blockierenden Spielaufruf, design.md §1e). Ein fremder `operator_id` oder
    ein nicht/anders gebundener Tisch -> `OperatorAuthorityError`, KEIN Write.

    Der Stop ist bewusst durabel (eigene Datei auf Platte, s. `admission.
    _table_stop_path`): er ueberlebt einen frischen Prozess und wird von
    `store.complete_section` (vor dem Plan-Pin) sowie an jeder Gate-Grenze
    (`read_admission_block(table_id=...)`) gelesen. Idempotent -- ein bereits
    gesetzter Stop wird nicht dupliziert, der aelteste Grund bleibt erhalten.
    Das normale Spiel ruft NIE `clear_table_stop`; ein Abbruch bleibt."""
    record = dict(_require_existing(run_dir, table_key))
    if record["host_id"] != operator_id:
        raise OperatorAuthorityError(
            f"operator_id={operator_id!r} ist nicht Betreiber von table_key={table_key!r} "
            f"(tatsaechlicher Betreiber: {record['host_id']!r}) -- Stop abgelehnt."
        )
    bound = record.get("section_id")
    if bound != table_id:
        raise OperatorAuthorityError(
            f"Tisch {table_key!r} ist nicht auf table_id={table_id!r} gebunden "
            f"(gebunden: {bound!r}) -- Stop-Ziel unzulaessig (O6). "
            "Die Identitaetsbindung (bind_section) muss VOR dem Stop vorliegen."
        )
    already, _ = read_table_stop(run_dir, table_id)
    path = _table_stop_path(Path(run_dir), table_id)
    if already:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    payload = {
        "schema": "table-stop/1",
        "table_key": table_key,
        "table_id": table_id,
        "operator_id": operator_id,
        "reason": reason or f"Betreiber {operator_id!r} hat Tisch {table_key!r} gestoppt.",
        "ts": time.time(),
    }
    _atomic_write_json(path, payload)
    return payload


def clear_table_stop(run_dir: str | Path, *, table_id: str) -> bool:
    """Entfernt den tisch-adressierten Stop. NUR fuer kontrollierte
    Freigabe/Tests -- der normale Abbruchpfad ruft dies NIE (ein Betreiber-
    Stop ist durabel, s. `request_table_stop`). `True`, wenn eine Datei
    entfernt wurde."""
    path = _table_stop_path(Path(run_dir), table_id)
    if path.exists():
        path.unlink()
        return True
    return False
