#!/usr/bin/env python3
"""
mmo_sim/core/request_ledger.py — persistenter Pro-Request-Datensatz (I2-
Nachzug, WEGKARTE-MAIN.md/PLAN-CRITIC.md/MAIN-ENTSCHEIDUNG.md).

EIN schlanker persistenter Requestauftrag pro Modellanfrage: eine kleine
Datei je Request unter `run_dir/requests/<id>.json` (Auflage 2, PLAN-
CRITIC F4, bindend: NICHT in `lab.status.json`/`LabStatus` — dessen
Dataclass-Konstruktor (`lab/runner.read_status`) bricht bei jedem
unbekannten Top-Level-Key, drei externe Suiten + `ui/tui.py:_cmd_settings`
lesen dieselbe Datei). Die VOLLEN Requestdaten (Rolle/Inhalt-Hash/Route/...)
bleiben davon unberuehrt weiterhin ausschliesslich hier. B1 (MAIN-KORREKTUR
I2-Nacharbeit 2026-09-24) ergaenzt in `lab.status.json`/`LabStatus` GENAU
EIN schlankes, additives Feld (`reconciled_request_ids`, Default leere
Liste) als Idempotenz-Index fuer `admission.record_usd_delta` — s. dessen
Docstring; das ist kein Verstoss gegen obige Auflage, da keine reichen
Requestdaten dorthin dupliziert werden, nur eine ID-Liste bereits
angewandter Kostenkorrekturen. Zustandsmaschine:

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
import os
import time
import uuid
from pathlib import Path

from .admission import (
    _atomic_write_json,
    add_seconds,
    booked_reservation_amount,
    compute_turn_usd,
    is_reservation_booked,
    record_turn_usage,
    record_usd_delta,
)


def _requests_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "requests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _request_path(run_dir: str | Path, request_id: str) -> Path:
    return _requests_dir(run_dir) / f"{request_id}.json"


class IndeterminateRequestRecordError(RuntimeError):
    """G2 (Requestdatensatz-I/O, I2-REVIEW-VOR-CLOSEOUT.md §3): ein
    VORHANDENER Requestdatensatz konnte nicht gelesen/geparst werden, oder
    sein Inhalt ist nicht als gueltiger Request einordenbar (gewoehnlicher
    sequenzieller Python-Lese-/Parsefehler -- kein Powerloss-/fsync-/
    Mehrprozess-Szenario). "Nicht lesbar" ist NICHT dasselbe wie "abwesend":
    ein bekannter, in seinem Zustand nicht bestimmbarer Datensatz haelt den
    betroffenen Ablauf (`begin()`s Identitaetspruefung, jede Debug-/
    End-Critic-Sicht ueber `open_requests()`/`load_request()`) kontrolliert
    gesperrt, statt ihn per `continue`/`None` unsichtbar zu machen und eine
    zweite Reservierung/Versand fuer dieselbe logische Operation zuzulassen.
    Kein automatisches Loeschen/Umschreiben/Archivieren/Neu-UUID auf
    Verdacht -- die Sperre gilt nur, solange der Datensatz tatsaechlich
    nicht lesbar ist (ein spaeterer, wieder erfolgreicher Scan ist kein
    Dauerverbot, s. REVIEW-BEFUND Fall 02: derselbe Lesefehler feuert dort
    genau einmal)."""



# G2-Lesevertragsnachzug (Rest A, 2026-09-24, REVIEW-G2.md §3): exakt die
# Schluessel, die `begin()`s Dict-Literal IMMER schreibt -- unabhaengig
# davon, ob der jeweilige Wert `None` ist (z.B. `route`/`table_id`/
# `section_id`/`turn_idx`/`participant` sind bereits heute legitime
# optionale Aufruferfelder, s. `begin()`s Signatur). Ein FEHLENDER
# Schluessel ist deshalb nie dasselbe wie ein bewusst vorhandenes `None` --
# nur die Abwesenheit macht einen Datensatz indeterminate, nicht sein Wert.
#
# R2-Fix (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md §4):
# `result_text` ABSICHTLICH NICHT mehr hier gelistet -- ein gueltiger, vom
# VORHERIGEN Writer (vor C2) korrekt ohne dieses Feld geschriebener
# Bestandsrecord (kein Powerloss/keine Korruption, nur ein aelteres,
# nach wie vor abgeschlossenes Schema) wuerde sonst allein wegen des NEUEN
# optionalen Feldes als `IndeterminateRequestRecordError` gesperrt --
# fehlender Schluessel == abwesend/None, s. `_CONTROL_FIELD_TYPES`-Schleife
# unten (`allow_none=True`, jetzt ueber `.get()` statt `[key]` gelesen).
# Alle anderen Schluessel bleiben unveraendert Pflicht.
_REQUIRED_RECORD_KEYS = (
    "id", "role", "route", "content_chars", "content_sha256",
    "output_limit_tokens", "reserved_usd", "table_id", "section_id",
    "turn_idx", "participant", "state", "reserved_ts", "sent_ts",
    "settled_ts", "usage", "error", "usd_reconciled",
)

# G2b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27) NICHT in
# `_REQUIRED_RECORD_KEYS` gelistet -- wie `result_text`/`received_seconds`
# (s. R2-/A1-Fix oben) ist ein FEHLENDER `dollar_billed`-Schluessel bei einem
# aelteren, vor diesem Fix geschriebenen Record gleichwertig zu einem
# bewusst gesetzten `True` (die alte Welt kannte nur dollarbepflichtete
# Rollen) -- kein Bestandsbruch fuer vorhandene Requestdatensaetze.

# Die einzigen von `begin()`/`finish_received()`/`finish_error()`
# geschriebenen `state`-Werte (s. Zustandsmaschine im Moduldocstring). Ein
# vorhandenes, aber unbekanntes/falsch typisiertes `state`-Feld ist ein
# widerspruechliches Kontrollfeld, kein gueltiges Terminal-/Zwischenlabel.
_VALID_STATES = frozenset({"reserved", "sent", "received", "error", "accounted"})


def _is_number_not_bool(value: object) -> bool:
    """`bool` ist in Python ein Subtyp von `int` -- `isinstance(True, int)`
    ist `True`. Fuer Kontrollfelder, die einen echten Zahlenwert (Zaehler/
    Zeitstempel/Betrag) tragen, ist ein `bool` deshalb NIE gueltig, obwohl
    ein nackter `isinstance(value, (int, float))`-Test ihn durchliesse."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# G2-Lesevertragsnachzug (REST 1, 2026-09-24, REVIEW-G2-KONTROLLFELDER.md
# §3): Schluesselpraesenz allein (obiger `_REQUIRED_RECORD_KEYS`-Check)
# beweist noch keinen gueltigen WERT. Matrix aus den tatsaechlichen
# `begin()`/`finish_received()`/`finish_error()`-Writes (s. `begin()`s
# Dict-Literal unten) UND den echten Aufrufern (`core.runtime.py`,
# `ui/tui.py:_cmd_settings`/Gast-Pfad ruft `begin()` OHNE `table_id`/
# `section_id`/`turn_idx` -- diese bleiben dort `None`, ein bereits heute
# legitimer Positivfall). `allow_none=True` bedeutet: ein vorhandenes,
# bewusst gesetztes `None` bleibt gueltig -- nur ein PRAESENTER, aber falsch
# typisierter Wert an derselben Stelle ist das Signal (G2, nicht die
# Schluessel-Abwesenheit, die bereits oben behandelt wird). `state` hat
# einen eigenen, bereits bestehenden Wertebereichs-Check weiter unten und
# ist hier bewusst NICHT nochmal aufgefuehrt.
_CONTROL_FIELD_TYPES: tuple[tuple[str, object, bool], ...] = (
    ("id", lambda v: isinstance(v, str) and v != "", False),
    ("role", lambda v: isinstance(v, str), False),
    ("route", lambda v: isinstance(v, str), True),
    ("content_chars", lambda v: isinstance(v, int) and not isinstance(v, bool), False),
    ("content_sha256", lambda v: isinstance(v, str), False),
    ("output_limit_tokens", _is_number_not_bool, True),
    ("reserved_usd", _is_number_not_bool, True),
    ("table_id", lambda v: isinstance(v, str), True),
    ("section_id", lambda v: isinstance(v, str), True),
    ("turn_idx", lambda v: isinstance(v, int) and not isinstance(v, bool), True),
    ("participant", lambda v: isinstance(v, str), True),
    ("reserved_ts", _is_number_not_bool, False),
    ("sent_ts", _is_number_not_bool, True),
    ("settled_ts", _is_number_not_bool, True),
    ("usage", lambda v: isinstance(v, dict), True),
    ("error", lambda v: isinstance(v, str), True),
    ("usd_reconciled", lambda v: isinstance(v, bool), False),
    # C2 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    # §3): der tatsaechlich EMPFANGENE Antworttext dieser Operation (GM-Reply
    # ODER Persona-Antwort) -- s. `finish_received()`/`find_durable_result()`
    # Docstrings. `None` bis zum ersten `finish_received()`-Aufruf (per
    # `begin()` initial gesetzt) und bleibt `None` bei `finish_error()`
    # (kein Text wurde je empfangen).
    ("result_text", lambda v: isinstance(v, str), True),
    # R1 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md §3):
    # die im ERSTEN `finish_received()`-Write persistierte URSPRUENGLICHE
    # Antwortdauer (s. `finish_received`/`settle_received` Docstrings) --
    # `None`/abwesend fuer jeden Record, der vor diesem Fix ODER ueber
    # `finish_error()` geschrieben wurde (kein Text, keine Dauer je
    # empfangen). Optional wie `result_text`: ein FEHLENDER Schluessel ist
    # kein Indeterminate-Signal, nur ein PRAESENTER falsch typisierter Wert.
    ("received_seconds", _is_number_not_bool, True),
    # G2b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27): ob DIESE
    # konkrete Operation ueber eine tatsaechlich abgerechnete API-Rolle lief
    # (`True`, Default/fehlender Schluessel bei Altrecords) oder ueber eine
    # CLI-/Abo-Rolle mit eigenen Turn-/Zeit-/Kontingentgrenzen (`False`) --
    # s. `begin()`/`finish_received()` Docstrings.
    ("dollar_billed", lambda v: isinstance(v, bool), True),
)


def _reject_duplicate_object_keys(pairs: list[tuple[str, object]]) -> dict:
    """G2-Lesevertragsnachzug (REST 2, 2026-09-24, REVIEW-G2-KONTROLLFELDER.md
    §4): `json.loads`s Standardverhalten behaelt bei einem doppelten Key
    still den LETZTEN Wert (`dict`-Literalsemantik) -- ein absichtlich
    angehaengtes zweites `"state": "accounted"` neben einem unveraendert
    vorhandenen `"state": "sent"` wuerde so unbemerkt zur Abschlussautoritaet.
    Als `object_pairs_hook` sieht diese Funktion ALLE Schluessel-Wert-Paare
    eines JSON-Objekts (auch verschachtelte, z.B. `usage`) in Dekodierreihenfolge
    -- ein bereits gesehener Schluessel im SELBEN Objekt ist nicht eindeutig
    einordenbar und wird hier, BEIM Dekodieren, abgelehnt (zu spaet waere eine
    Pruefung erst NACH `json.loads`, die den Widerspruch bereits verworfen
    haette). Der bestehende Writer (`_write_request`/`_atomic_write_json`)
    erzeugt ausschliesslich eindeutige Keys -- diese Pruefung betrifft nur
    absichtlich widerspruechlich manipulierte vorhandene Dateien."""
    seen: dict = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(
                f"doppelter JSON-Schluessel {key!r} im selben Objekt -- nicht "
                "eindeutig einordenbar (G2 REST 2)."
            )
        seen[key] = value
    return seen


def _classify_or_raise(p: Path) -> dict:
    """Gemeinsamer Leseweg fuer `load_request()`/`open_requests()`: liest
    UND klassifiziert genau EINEN vorhandenen Requestdatensatz. Ein
    gewoehnlicher Lese-/Parsefehler ODER ein Inhalt, der nicht als
    Requestdatensatz erkennbar ist (kein dict, kein `state`-Feld), wird NIE
    als leiser Erfolg/Abwesenheit behandelt -- s. `IndeterminateRequestRecordError`.

    G2-Fix (Rest A, 2026-09-24, REVIEW-G2.md §3 Fall 02/03): ein
    syntaktisch gueltiges JSON-Objekt MIT `state`-Feld ist allein noch KEIN
    ausreichend eingeordneter Requestdatensatz -- ein FEHLENDER
    Pflichtschluessel (z.B. ein geloeschtes `participant`-Feld, Fall 02)
    macht `begin()`s `.get()`-basierte Identitaetspruefung sonst blind (ein
    fehlender Schluessel wird zu `None` und passt nicht mehr zur bereits
    reservierten Operation -- eine zweite Reservierung waere die Folge). Ein
    bloss aus `{"state": "accounted"}` bestehendes Objekt (Fall 03) traegt
    keinerlei Identitaets-/Buchungsnachweis und beweist keine abgeschlossene
    Operation -- beide Faelle werden deshalb wie ein Lese-/Parsefehler
    behandelt: kontrollierte Sperre (`IndeterminateRequestRecordError`)
    statt eines stillen `.get()->None`-Durchrutschens oder eines
    unbelegten `accounted`-Skips. Ein bereits vorhandener, bewusst gesetzter
    `None`-Wert in einem der o.g. optionalen Felder bleibt dagegen
    unveraendert gueltig -- nur die Schluessel-ABWESENHEIT ist das Signal."""
    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw, object_pairs_hook=_reject_duplicate_object_keys)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise IndeterminateRequestRecordError(
            f"Requestdatensatz {p.name!r} ist vorhanden, aber nicht lesbar/parsebar "
            f"({type(exc).__name__}: {exc}) -- kontrollierte Sperre statt Behandlung "
            "als abwesend (G2)."
        ) from exc
    if not isinstance(data, dict) or "state" not in data:
        raise IndeterminateRequestRecordError(
            f"Requestdatensatz {p.name!r} ist vorhanden, aber sein Inhalt ist nicht als "
            "gueltiger Requestdatensatz einordenbar (kein Objekt oder fehlendes "
            "'state'-Feld) -- kontrollierte Sperre statt Behandlung als abwesend (G2)."
        )
    missing = [key for key in _REQUIRED_RECORD_KEYS if key not in data]
    if missing:
        raise IndeterminateRequestRecordError(
            f"Requestdatensatz {p.name!r} ist vorhanden, aber ihm fehlt mindestens ein "
            f"Pflichtschluessel ({', '.join(missing)}) -- unzureichende Request-/"
            "Operationsidentitaet, kontrollierte Sperre statt Behandlung als abwesend/"
            "abgeschlossen (G2, REVIEW-G2.md §3 Fall 02/03)."
        )
    if not isinstance(data["state"], str) or data["state"] not in _VALID_STATES:
        raise IndeterminateRequestRecordError(
            f"Requestdatensatz {p.name!r}: 'state' ({data.get('state')!r}) ist kein "
            "gueltiger bekannter Zustand -- widerspruechliches/falsch typisiertes "
            "Kontrollfeld, kontrollierte Sperre statt Behandlung als abgeschlossen (G2)."
        )
    # G2-Lesevertragsnachzug (REST 1, 2026-09-24, REVIEW-G2-KONTROLLFELDER.md
    # §3): ein PRAESENTER Schluessel beweist noch keinen gueltigen Wert --
    # `_operation_identity()`/`begin()`s Doppelreservierungspruefung
    # vergleicht die Werte ohne eigene Typpruefung; ein falsch typisierter
    # Wert (z.B. `turn_idx: "1"` statt `1`, `participant: ["p-g2"]` statt
    # `"p-g2"`) darf deshalb nicht wie ein gewoehnlicher abweichender Wert
    # durchgereicht werden. `allow_none=True`-Felder duerfen weiterhin ein
    # bewusstes `None` tragen (s. `_CONTROL_FIELD_TYPES`-Docstring).
    #
    # R2-Fix (Community-Recovery 2026-09-25): `data.get(key)` statt
    # `data[key]` -- fuer die noch immer in `_REQUIRED_RECORD_KEYS`
    # gelisteten Schluessel bleibt das Verhalten identisch (Praesenz oben
    # bereits geprueft). Fuer `result_text`/`received_seconds` (NICHT mehr
    # in `_REQUIRED_RECORD_KEYS`, s. dort) macht das einen fehlenden
    # Schluessel gleichwertig zu einem bewusst vorhandenen `None` -- exakt
    # das ist der R2-Kompatibilitaetsvertrag (fehlender Schluessel ==
    # abwesend/None, keine Bestandsbereinigung/Neuschreibung noetig).
    for key, validator, allow_none in _CONTROL_FIELD_TYPES:
        value = data.get(key)
        if value is None and allow_none:
            continue
        if not validator(value):
            raise IndeterminateRequestRecordError(
                f"Requestdatensatz {p.name!r}: Kontrollfeld {key!r} ({value!r}) hat "
                "einen unzulaessigen Typ/Wert -- widerspruechliches/falsch "
                "typisiertes Kontrollfeld, kontrollierte Sperre statt Behandlung als "
                "gueltig (G2 REST 1)."
            )
    return data


def load_request(run_dir: str | Path, request_id: str) -> dict | None:
    """Liefert `None` NUR fuer einen echten, initial abwesenden Datensatz
    (Datei existiert nicht). Existiert die Datei, aber ist nicht lesbar/
    parsebar oder nicht als Request einordenbar, wird das NICHT als
    erfolgreicher No-op verdeckt -- `IndeterminateRequestRecordError`
    propagiert an den Aufrufer (G2, gleichwertiger Leseweg zu
    `open_requests()`)."""
    p = _request_path(run_dir, request_id)
    if not p.exists():
        return None
    return _classify_or_raise(p)


def open_requests(run_dir: str | Path) -> list[dict]:
    """Alle Requestdatensaetze, die NICHT `accounted` sind -- End-Critic-/
    Debug-Sicht auf offene Verpflichtungen fuer ein `run_dir` (I2:
    "End-Critic muss den implementierten Requestdatensatz + echte
    Wiederaufnahme sehen").

    G2-Fix (Requestdatensatz-I/O, I2-REVIEW-VOR-CLOSEOUT.md §3): ein
    vorhandener, aber nicht lesbarer/parsebarer/einordenbarer Datensatz wird
    NICHT mehr per `continue` uebersprungen (das machte eine offene
    Reservierung fuer `begin()`s Identitaetspruefung unsichtbar und liess
    eine zweite Buchung/einen zweiten Versand fuer dieselbe logische
    Operation zu) -- `IndeterminateRequestRecordError` propagiert
    ungefangen, der Scan bricht kontrolliert ab, BEVOR irgendeine neue
    Reservierung geschrieben wird (ein echter initial leerer
    Requestbereich, `d.is_dir()` False oder ein leeres Verzeichnis, bleibt
    der erlaubte Positivfall und liefert weiterhin `[]`)."""
    d = Path(run_dir) / "requests"
    if not d.is_dir():
        return []
    # G2-Fix (Rest B, 2026-09-24, REVIEW-G2.md §4): `Path.glob()` faengt
    # jeden `OSError` seiner internen Verzeichnisenumeration ab und liefert
    # danach still eine LEERE Trefferliste (s. `pathlib._WildcardSelector.
    # _select_from`: `except OSError: pass`) -- ein bestehendes, aber gerade
    # nicht vollstaendig lesbares Requestverzeichnis (z.B. ein transienter
    # Berechtigungsfehler) wirkte dadurch wie ein echter leerer Erstlauf und
    # liess `begin()`s Identitaetspruefung eine bereits offene Reservierung
    # uebersehen. `os.scandir()` (oeffentliche stdlib-API, KEIN
    # pathlib-internes Implementierungsdetail) wirft einen Enumerationsfehler
    # stattdessen normal -- hier NICHT abgefangen, sondern kontrolliert in
    # `IndeterminateRequestRecordError` gefasst und an den Aufrufer
    # propagiert (dieselbe Sperrsemantik wie ein nicht lesbarer Einzeldatensatz,
    # s. `_classify_or_raise`). Ein tatsaechlich leeres oder initial fehlendes
    # Verzeichnis (`d.is_dir()` False, oben) bleibt der erlaubte Positivfall.
    # Ein spaeterer, wieder erfolgreicher Scan ist kein Dauerverbot -- der
    # Fehler wird bei jedem Aufruf neu ermittelt, nichts wird gemerkt.
    return [data for data in _all_records(run_dir) if data.get("state") != "accounted"]


def _all_records(run_dir: str | Path) -> list[dict]:
    """Gemeinsamer Volltextscan fuer `open_requests()` (nur nicht-`accounted`)
    UND `find_durable_result()` (braucht die `received`- UND `accounted`-
    Datensaetze -- Ueberschneidung mit `open_requests()` ist hier bewusst,
    ein `received` Datensatz ist gleichzeitig "offen" fuer `begin()`s Dedup
    UND ein moeglicher Treffer fuer `find_durable_result()`, s. dessen
    Docstring). Dieselbe G2-Sperrsemantik wie
    zuvor inline in `open_requests()`: ein nicht lesbares/aufzaehlbares
    Verzeichnis oder ein einzelner nicht einordenbarer Datensatz propagiert
    `IndeterminateRequestRecordError` UNGEFANGEN, BEVOR irgendeine neue
    Reservierung geschrieben wird -- ein leeres/initial fehlendes
    Verzeichnis bleibt der erlaubte Positivfall (`[]`)."""
    d = Path(run_dir) / "requests"
    if not d.is_dir():
        return []
    try:
        with os.scandir(d) as it:
            names = sorted(entry.name for entry in it if entry.name.endswith(".json"))
    except OSError as exc:
        raise IndeterminateRequestRecordError(
            f"Requestverzeichnis {d} konnte nicht vollstaendig aufgelistet werden "
            f"({type(exc).__name__}: {exc}) -- kontrollierte Sperre statt Behandlung "
            "als leeren Erstlauf (G2, REVIEW-G2.md §4)."
        ) from exc
    return [_classify_or_raise(d / name) for name in names]


def find_durable_result(
    run_dir: str | Path, *, table_id: str | None, section_id: str | None, role: str,
    turn_idx: int | None, participant: str | None,
) -> dict | None:
    """C2 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §3): beantwortet "wurde fuer GENAU DIESE logische Operation (s.
    `_operation_identity`) bereits eine Modellantwort tatsaechlich empfangen
    UND dauerhaft auf Platte geschrieben?" -- unabhaengig davon, ob das
    LOKALE Folge-Checkpoint-Write (`onboarding.record_pending_reply`/
    `record_pending_answer`) diesen Text ebenfalls schon uebernommen hat.

    `begin()`s `open_requests()`-Dedup schuetzt NUR offene (nicht
    `accounted`) Reservierungen -- ein bereits `accounted` Datensatz macht
    die Operationsidentitaet fuer `begin()` wieder frei (Case 05: Reservierung
    bleibt Buchungsende, kein Refund). Das war die eigentliche Luecke: ein
    normaler Python-`OSError` GENAU zwischen `finish_received()` (accounted)
    und dem lokalen Onboarding-Checkpoint-Write liess einen Folgeprozess
    dieselbe bereits abgerechnete Anfrage blind ein zweites Mal senden, weil
    er nur die LOKALE `pending_step`-Datei kannte, nicht den bereits
    dauerhaften Ledger-Datensatz.

    C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): `state in ("received",
    "accounted")` statt nur `"accounted"`. `finish_received()` schreibt
    `result_text` bereits im ERSTEN der beiden Writes (Uebergang nach
    `state=received`) -- der ZWEITE Write (Uebergang nach `accounted`,
    dazwischen `add_seconds`/`record_usd_delta`) kann an einem gewoehnlichen
    `OSError` scheitern (vorbestehendes, bewusstes G3-Fix/R1-Fix-Verhalten:
    `finish_received` faengt diesen Fehler NICHT ab, der Datensatz bleibt
    ehrlich bei `state=received` haengen). Ohne diese Erweiterung war ein
    solcher Datensatz fuer diese Funktion UNSICHTBAR, obwohl sein
    `result_text` bereits durabel vorlag -- `begin()`s Dedup haelt die
    Operationsidentitaet aber gleichzeitig als OFFEN (nicht `accounted`)
    gesperrt: ein Folgeversuch fand weder einen wiederverwendbaren Text
    (dieser Check) noch durfte er eine neue Reservierung anlegen
    (`OpenReservationExistsError` aus `begin()`) -- ein permanenter Deadlock
    fuer genau diese Operationsidentitaet. Ein `state=received` Datensatz mit
    bereits gesetztem `result_text` traegt exakt denselben Beweis eines
    tatsaechlich empfangenen Ergebnisses wie ein `accounted` Datensatz --
    nur die NACHGELAGERTE Kosten-/Latenzbuchung (`add_seconds`/
    `record_usd_delta`) ist (noch) offen, nicht der empfangene Text selbst.
    R1-Korrektur (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
    §3): "der zweite Write bleibt hier unrepariert" beschreibt NUR, was DIESE
    Funktion selbst tut -- sie ist ein reiner Lesevorgang und schreibt nie.
    Das ist NICHT gleichbedeutend mit "der Aufrufer darf einen `received`-
    Treffer wie einen `accounted`-Treffer als erledigte Voraussetzung
    behandeln und ungeprueft weiterruecken". Ein `result_text` OHNE
    vollstaendige Kosten-/Latenzbuchung ist noch keine bestaetigte
    Bereitschaft -- der Auftrag DARF offen bleiben, aber der Verbraucher
    darf ihn dann nicht still als erledigt verwenden und volle Bereitschaft
    meldenden. Deshalb ruft jeder echte Aufrufer (s.u.) fuer einen
    `state=received`-Treffer VOR jeder Weiterverwendung genau einmal
    `settle_received()` auf (idempotente Fortsetzung des zweiten Writes) --
    schlaegt das fehl, bleibt der Datensatz ehrlich offen UND der Aufrufer
    bricht kontrolliert ab (kein `completed`/`already_ready`, kein weiterer
    Modellaufruf mit still ausgelassener Wirkung).

    Aufrufer (`core.creation_service.run_admitted_creation_dialog` fuer den
    GM-Turn, `domain.zeitriss.community_creation._persona_get_reply_factory`
    fuer den Persona-Turn) rufen dies VOR jeder neuen Reservierung/jedem
    neuen Versand fuer eine Operationsidentitaet auf, deren lokaler
    Checkpoint (noch) keinen Text traegt. Nur ein `state in ("received",
    "accounted")` Datensatz OHNE `error` UND MIT gesetztem `result_text` gilt
    als wiederverwendbar -- ein `finish_error()`-Datensatz (kein Text je
    empfangen, `state=accounted` direkt nach `error`) bleibt bewusst
    UNSICHTBAR fuer diese Funktion, ein Retry NACH einem echten Transportfehler
    ist weiterhin ein legitimer NEUER Versand (Case 05), keine Wiederholung
    eines bereits empfangenen Ergebnisses. Liefert bei (praktisch nie
    auftretenden) mehreren Treffern fuer dieselbe Identitaet den zuletzt
    reservierten Datensatz -- unter normalem Betrieb (`begin()`s Dedup bleibt
    unveraendert wirksam fuer OFFENE Reservierungen) entsteht hoechstens
    EIN wiederverwendbarer Treffer pro Identitaet."""
    identity = (table_id, section_id, role, turn_idx, participant)
    matches = [
        data for data in _all_records(run_dir)
        if data.get("state") in ("received", "accounted")
        and data.get("error") is None
        and data.get("result_text") is not None
        and _operation_identity(data) == identity
    ]
    if not matches:
        return None
    matches.sort(key=lambda d: d.get("reserved_ts") or 0.0)
    return matches[-1]


def find_answered_without_text(
    run_dir: str | Path, *, table_id: str | None, section_id: str | None, role: str,
    turn_idx: int | None, participant: str | None,
) -> dict | None:
    """A2 (Altformat-Recovery-Nachzug 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    A2): erkennt einen ALTEN Requestdatensatz fuer GENAU DIESE
    Operationsidentitaet (s. `_operation_identity`), der nachweislich bereits
    gesendet UND erfolgreich beantwortet/verbucht wurde (`state in
    ("received", "accounted")`, `error is None`), dessen `result_text` aber
    NICHT (mehr) vorliegt (ABWESENT/`None`) -- ein Vorversions-Writer (vor
    C2, z.B. der 10024452-Stand) hat diesen Text nie persistiert.

    Bewusstes Gegenstueck zu `find_durable_result()`: jene Funktion verlangt
    `result_text is not None` (Textabgleich) -- ein Record ohne Text ist fuer
    sie deshalb bewusst KEIN Treffer und macht die Operationsidentitaet fuer
    `begin()`s Dedup wieder frei (ein bereits `accounted`er Datensatz sperrt
    `begin()` nicht mehr). Ohne diese Funktion sah ein Aufrufer deshalb einen
    bereits erfolgreich abgerechneten Altauftrag als "nie gesendet" an und
    reservierte/versandte blind ein zweites Mal fuer dieselbe logische
    Operation (REVIEW-COMMUNITY-ALTFORMAT.md §4: 4 statt 3 Versuche, 0.20
    statt 0.15 USD).

    Aufrufer (`core.creation_service.run_admitted_creation_dialog` GM-Turn,
    `domain.zeitriss.community_creation._get_reply` Persona-Turn) rufen dies
    im "`find_durable_result()` == None"-Zweig VOR jedem neuen `begin()`/
    Versand fuer eine Operationsidentitaet auf, deren lokaler Checkpoint
    (noch) keinen Text traegt (der Aufrufer hat zu diesem Zeitpunkt bereits
    selbst geprueft, dass der Text auch nicht im lokalen Onboarding-/
    Pending-Checkpoint eindeutig gebunden vorliegt -- s. `onboarding.peek`/
    `pending_step` im jeweiligen Aufrufer). Liefert diese Funktion einen
    Treffer, blockieren sie kontrolliert (KEINE neue Reservierung/Anfrage
    fuer dieselbe Operationsidentitaet, sichtbare Pause statt stillem
    Weiterruecken) -- der urspruenglich empfangene Text ist nicht
    rekonstruierbar; eine neue Modellanfrage waere KEINE Wiederholung einer
    verlorenen Antwort, sondern eine zusaetzliche, nicht autorisierte
    Anfrage fuer eine bereits beantwortete Operation.

    KEIN universelles "alle accounted IDs sperren": nur ein Treffer fuer
    GENAU DIESE Identitaet blockiert -- eine andere Operationsidentitaet
    (anderer `turn_idx`/Teilnehmer/Tisch/Abschnitt) bleibt unberuehrt, ein
    echter neuer/spaeterer Turn (Case 06) und eine bewusste R4-
    Pausefortsetzung (neuer Entscheiderturn) bleiben normale, erlaubte
    Anfragen. Ein `finish_error()`-Datensatz (kein Text je empfangen,
    `error` gesetzt) bleibt bewusst UNSICHTBAR fuer diese Funktion -- ein
    Retry NACH einem echten Transportfehler ist weiterhin ein legitimer
    NEUER Versand (Case 05), keine Wiederholung eines bereits empfangenen
    Ergebnisses. Liefert bei (praktisch nie auftretenden) mehreren Treffern
    fuer dieselbe Identitaet den zuletzt reservierten Datensatz (analog
    `find_durable_result`)."""
    identity = (table_id, section_id, role, turn_idx, participant)
    matches = [
        data for data in _all_records(run_dir)
        if data.get("state") in ("received", "accounted")
        and data.get("error") is None
        and data.get("result_text") is None
        and _operation_identity(data) == identity
    ]
    if not matches:
        return None
    matches.sort(key=lambda d: d.get("reserved_ts") or 0.0)
    return matches[-1]


def find_open_orphan(
    run_dir: str | Path, *, table_id: str | None, section_id: str | None, role: str,
    turn_idx: int | None, participant: str | None,
) -> dict | None:
    """REC-1 (04_REQUEST_RECOVERY.md §2A/§3, ZR-UPDATE-RESUME-REPARATUR
    2026-11-23): Gegenstueck zu `find_durable_result`/`find_answered_
    without_text` fuer den Zustand, den beide bewusst NICHT abdecken --
    ein Requestdatensatz fuer GENAU DIESE Operationsidentitaet (s.
    `_operation_identity`), der noch in `state in ("reserved", "sent")`
    steht: `begin()` hat die Reservierung committet und (bei `sent`) den
    Versandmarker gesetzt, aber `finish_received`/`finish_error` wurde nie
    erreicht (S1-Befund: Prozessabsturz zwischen Versandmarker und
    Transportantwort ODER der Provider hat tatsaechlich geantwortet, die
    lokale Antwort ging aber verloren -- aus dem Zustand allein nicht
    unterscheidbar, deshalb bewusst NICHT als Fehler/Erfolg behauptet).

    `begin()` selbst wirft fuer denselben Treffer `OpenReservationExistsError`
    (identische `open_requests()`+`_operation_identity`-Pruefung, s. dort) --
    diese Funktion macht GENAU DENSELBEN Befund VOR dem Aufruf sichtbar und
    rein LESEND, damit ein Aufrufer eine kontrollierte, typisierte Pause mit
    verstaendlicher Begruendung (betroffene Requestdatensatz-ID, kein
    Stacktrace) liefern kann, statt die rohe Ausnahme unbehandelt bis zum
    Prozessende zu propagieren. KEIN Ersatz fuer `begin()`s eigene Pruefung
    (bleibt als letzte Verteidigungslinie unveraendert bestehen, falls ein
    Aufrufer diese Funktion nicht vorschaltet) -- reiner Lesevorgang, kein
    Zustand wird hier veraendert, keine Reservierung/Sperre wird aufgehoben.

    Liefert bei (praktisch nie auftretenden) mehreren offenen Treffern fuer
    dieselbe Identitaet den zuletzt reservierten Datensatz (analog
    `find_durable_result`/`find_answered_without_text`)."""
    identity = (table_id, section_id, role, turn_idx, participant)
    matches = [
        data for data in _all_records(run_dir)
        if data.get("state") in ("reserved", "sent")
        and _operation_identity(data) == identity
    ]
    if not matches:
        return None
    matches.sort(key=lambda d: d.get("reserved_ts") or 0.0)
    return matches[-1]


def _write_request(run_dir: str | Path, request_id: str, data: dict) -> None:
    """G2-Fix (Requestdatensatz-I/O, I2-REVIEW-VOR-CLOSEOUT.md §4): schreibt
    ueber dieselbe atomare Dateihilfe wie `lab.status.json`
    (`core.admission._atomic_write_json`) -- Temp-Datei im selben `requests/`
    Verzeichnis, erst VOLLSTAENDIG geschrieben, dann per `os.replace`
    kontrolliert veroeffentlicht. Ein gewoehnlicher Teilschreib-`OSError`
    auf dem Temp-Pfad (egal bei welchem Zustandsuebergang -- reserved,
    sent, received, error, accounted, s. `begin()`/`finish_received()`/
    `finish_error()`) hinterlaesst den zuletzt gueltigen, vollstaendig
    veroeffentlichten Requestdatensatz UNVERAENDERT (kein halb
    geschriebenes/korruptes Dokument mehr, das `open_requests()`s
    Identitaetspruefung dann als 'unlesbar -> abwesend' fehlinterpretieren
    koennte). Die Temp-Datei liegt NICHT unter dem `*.json`-Glob, den
    `open_requests()`/`load_request()` betrachten -- ein verwaister
    Temp-Rest (nur bei einem Absturz WAEHREND dieses Aufrufs moeglich,
    fsync-/Powerloss-Haertung ist nicht beauftragt) wird dadurch nie als
    fertiger Request gelesen; `_atomic_write_json` raeumt ihren EIGENEN
    Temp-Pfad bei einem Fehler bereits bestmoeglich auf. Der Fehler selbst
    propagiert ungefangen (kein stiller Erfolg)."""
    _atomic_write_json(_request_path(run_dir, request_id), data)


def _operation_identity(data: dict) -> tuple:
    """G2 (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 03): die logische Operationsidentitaet
    eines Requestdatensatzes -- Tisch/Abschnitt/Rolle(Phase)/Turn/Teilnehmer,
    NICHT der reine Inhalts-Hash (zwei spaeter tatsaechlich gesendete,
    inhaltlich identische Turns bleiben zwei legitime Auftraege, weil sich
    `turn_idx` bei jedem erfolgreich ABGESCHLOSSENEN Turn erhoeht -- s.
    `core.runtime.SectionRuntime.submit`)."""
    return (
        data.get("table_id"), data.get("section_id"), data.get("role"),
        data.get("turn_idx"), data.get("participant"),
    )


class OpenReservationExistsError(RuntimeError):
    """G2 (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 03): `begin()` hat fuer DIESELBE
    logische Operation (s. `_operation_identity`) bereits einen offenen
    (nicht `accounted`) Requestdatensatz gefunden -- kontrollierte
    Ablehnung statt einer zweiten Reservierung/Doppelbelastung fuer einen
    lokalen Retry VOR dem Versandmarker. Der vorhandene offene Auftrag
    bleibt dabei unveraendert erhalten (kein Refund, kein blinder
    Neuversand)."""


def begin(
    run_dir: str | Path, *, role: str, content: str, reserved_usd: float | None,
    route: str | None = None, output_limit_tokens: float | None = None,
    table_id: str | None = None, section_id: str | None = None,
    turn_idx: int | None = None, participant: str | None = None,
    dollar_billed: bool = True,
) -> str:
    """Legt den Requestdatensatz an (state=reserved), committet die
    Reservierung SOFORT in `lab.status.json` und markiert state=sent — ALLES
    VOR dem eigentlichen Adapter-/Transport-Aufruf (der Aufrufer ruft
    `begin()` unmittelbar davor auf). `content` ist der TATSAECHLICH zu
    sendende Text (Hash+Laenge, kein Klartext-Volldump — Auditbeleg ohne
    zusaetzliches Datenschutzrisiko). Liefert die `request_id` fuer
    `finish_received`/`finish_error`.

    G2-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 03): `turn_idx`/`participant`
    (additiv, zusammen mit `table_id`/`section_id`/`role` die logische
    Operationsidentitaet, s. `_operation_identity`) -- existiert bereits
    ein OFFENER (nicht `accounted`) Requestdatensatz fuer DIESELBE
    Operationsidentitaet (`open_requests()`), wirft `begin()` VOR jedem
    neuen Schreibzugriff `OpenReservationExistsError` -- eine zweite
    Reservierung fuer denselben, noch nicht abgeschlossenen lokalen Auftrag
    (z.B. ein Retry nach einem Absturz zwischen Budgetbuchung und
    Versandmarker/Transport) wird kontrolliert abgelehnt, statt den alten
    offenen Auftrag unaufgeloest zu lassen und zusaetzlich ein zweites Mal
    zu buchen. Ohne unterscheidende Felder (alle `None`, z.B. Aufrufer ohne
    Tisch-/Turnkontext) bleibt die Pruefung wirksam -- ein Aufrufer, der
    `begin()` mehrfach fuer wirklich unabhaengige Auftraege im selben
    `run_dir` verwendet, muss unterscheidende Felder mitgeben (alle echten
    Produktaufrufer tun das bereits, s. `core.runtime.py`/`ui/tui.py`).

    B-Fix (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-BUCHUNGSGRENZEN.md
    §4 Fall 04, seit G1 IMMER `require_authority=True`): schlaegt die
    Reservierungsbuchung (`admission.record_turn_usage`) fehl -- Read-/
    Parsefehler einer vorhandenen ODER eine inzwischen fehlende
    `lab.status.json`, propagiert ungefangen -- bricht `begin()` HIER ab:
    `data["state"] = "sent"` wird NICHT mehr erreicht. Der Aufrufer
    (`core.runtime.SectionRuntime.submit`/`_admitted_decision`) ruft den
    eigentlichen Transport (GM-/Persona-Request) immer ERST NACH `begin()`
    auf -- eine propagierte Ausnahme verhindert dadurch den echten Versand,
    statt einen scheinbar versandbereiten Auftrag (`state=sent`,
    `turns_used`/`usd_spent` unveraendert bei 0) zu liefern."""
    identity = (table_id, section_id, role, turn_idx, participant)
    for existing in open_requests(run_dir):
        if _operation_identity(existing) == identity:
            raise OpenReservationExistsError(
                f"Bereits ein offener Requestdatensatz (id={existing.get('id')!r}, "
                f"state={existing.get('state')!r}) fuer dieselbe logische Operation "
                f"(table_id={table_id!r}, section_id={section_id!r}, role={role!r}, "
                f"turn_idx={turn_idx!r}, participant={participant!r}) -- kein zweiter "
                "Reservierungsversand fuer denselben noch nicht abgeschlossenen Auftrag "
                "(G2, REVIEW-RESERVIERUNGSABSCHLUSS.md §4 Fall 03)."
            )
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
        "turn_idx": turn_idx,
        "participant": participant,
        "state": "reserved",
        "reserved_ts": time.time(),
        "sent_ts": None,
        "settled_ts": None,
        "usage": None,
        "error": None,
        "usd_reconciled": False,
        "result_text": None,
        "dollar_billed": dollar_billed,
    }
    _write_request(run_dir, request_id, data)
    # Case 05 (bindend): die Reservierung wird VOR dem Versand committet --
    # ein Timeout/Verbindungsabbruch NACH diesem Punkt darf turns_used/
    # usd_spent nicht unberuehrt lassen (sonst blockiert ein zweiter Versuch
    # nicht, obwohl bereits real gesendet wurde). G1: `require_authority=
    # True` -- eine fehlende `lab.status.json` an DIESER Stelle ist ein
    # Fehler, kein Offline-No-op (der vorgelagerte Gatecheck hat bereits
    # ein gueltiges Profil verlangt).
    #
    # G2b (Bau-GO 2026-09-27): eine NICHT dollarbepflichtete Rolle (CLI/Abo,
    # `dollar_billed=False`) bucht IMMER exakt `0.0` -- NIE `reserved_usd`
    # (das waere eine erfundene Dollarabrechnung fuer eine Rolle, die H-E
    # zufolge keine hat) UND NIE `None`/unbekannt (das wuerde `record_turn_
    # usage` faelschlich einen KONSERVATIV GESCHAETZTEN synthetischen Preis
    # fuer eine 'unbeobachtbare, aber real abgerechnete' Anfrage verbuchen
    # lassen -- diese Anfrage ist strukturell nicht abgerechnet, nicht bloss
    # unbeobachtet).
    booked_usd = reserved_usd if dollar_billed else 0.0
    # K (PR #3317-Nachzug r2, RECOVERY_REVIEW.md §3): den initial gebuchten
    # Reservebetrag crashfest je request-id in `lab.status.json`
    # (`reservation_booked_usd`) festhalten -- `commit_authorized_retry`
    # rechnet eine spaetere Nachbuchung gegen diesen autoritativen Stand.
    record_turn_usage(
        run_dir, 0.0, booked_usd, require_authority=True,
        booked_reservation_id=request_id, booked_reservation_usd=booked_usd,
    )
    data["state"] = "sent"
    data["sent_ts"] = time.time()
    _write_request(run_dir, request_id, data)
    return request_id


def finish_received(
    run_dir: str | Path, request_id: str, *, usage: dict | None = None, seconds: float = 0.0,
    result_text: str | None = None,
) -> None:
    """Erfolgreich beantworteter Request. `turns_used`/die URSPRUENGLICHE
    Reservierung wurden bereits in `begin()` committet (kein zweites
    Anrechnen der Reservierung) -- hier wird die reale Latenz nachgetragen,
    eine etwaige Kostenkorrektur gebucht (s. u.) und der Datensatz final auf
    `accounted` gesetzt (idempotent: ein erneuter Aufruf fuer dieselbe
    `request_id`, dessen Datensatz bereits `accounted` ist, aendert nichts
    mehr).

    C2 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §3): `result_text` (der tatsaechlich empfangene GM-/Persona-Antworttext)
    wird -- falls uebergeben -- bereits in DIESEM ersten `_write_request`-Aufruf
    (Uebergang nach `state=received`) mitgeschrieben, NICHT erst spaeter. Ab
    genau diesem atomaren Schreibvorgang ist der Text dauerhaft ueber
    `find_durable_result()` fuer dieselbe Operationsidentitaet wiederauffindbar
    -- unabhaengig davon, ob ein NACHFOLGENDER, separater lokaler Checkpoint-
    Write (`onboarding.record_pending_reply`/`record_pending_answer`) danach
    noch fehlschlaegt. Das schliesst genau das Fenster, das ein Folgeprozess
    zuvor nur ueber die (dann leere) lokale `pending_step`-Datei sehen konnte:
    er fragt jetzt zusaetzlich den bereits durablen Ledger-Datensatz ab, statt
    blind dieselbe Anfrage neu zu senden. `result_text=None` (Default) bleibt
    unveraendert fuer Aufrufer, die diesen Mechanismus nicht nutzen (z.B.
    bestehende I2/G2-Tests) -- ein Datensatz ohne `result_text` ist fuer
    `find_durable_result()` schlicht kein Treffer, kein Verhaltensunterschied
    sonst.

    C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): "ab genau diesem
    atomaren Schreibvorgang durabel wiederauffindbar" bezieht sich auf DIESEN
    ERSTEN `_write_request`-Aufruf (Uebergang nach `state=received`), NICHT
    auf den spaeteren, separaten Uebergang nach `state=accounted` weiter
    unten (dazwischen liegen `add_seconds`/`record_usd_delta`, die beide
    einen gewoehnlichen `OSError` bewusst ungefangen propagieren, s. G3-Fix/
    R1-Fix unten). `find_durable_result()` erkennt seit dieser Nacharbeit
    ausdruecklich BEIDE Zustaende (`received` UND `accounted`) als
    wiederverwendbaren Treffer -- ein Datensatz, der wegen eines Fehlers in
    `add_seconds`/`record_usd_delta` dauerhaft bei `state=received`
    haengenbleibt, ist deshalb trotzdem ab diesem ERSTEN Write durabel
    auffindbar; nur seine Kosten-/Latenznachbuchung bleibt dann dauerhaft
    unvollstaendig (kontrolliert offen, s. `find_durable_result()`-Docstring),
    nicht der empfangene Text selbst.

    E5 (Auflage 5, MAIN-ENTSCHEIDUNG I2-Nachzug GM-Weg, PLAN-CRITIC Fallstrick
    1/2): der real via `compute_turn_usd(usage)` ermittelte Betrag wird mit
    der VOR dem Versand committeten `reserved_usd` verglichen -- NUR wenn
    real > reserviert, wird die Differenz zusaetzlich auf `usd_spent`
    nachgebucht (`admission.record_usd_delta`). `usage=None` (Case 05,
    verlorene Antwort) UND ein technisch vorhandenes, aber nicht auswertbares
    `usage={}` liefern BEIDE `None` aus `compute_turn_usd` -- identisch
    behandelt als 'keine Reduktion, Reservierung bleibt Endstand' (KEIN
    Refund bei real<=reserved, Case 05 bleibt unangetastet).

    B1-Fix (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3): `delta`
    wird bei JEDEM Aufruf (auch einem Retry aus einem frischen Prozess fuer
    denselben, noch nicht `accounted` Datensatz) NEU aus `reserved_usd`/
    `usage` berechnet -- beide sind bereits VOR dem ersten Aufruf stabil
    persistiert, die Neuberechnung liefert deshalb bei einem Retry denselben
    Wert. Die EINMALIGKEIT der Buchung wird NICHT mehr hier (ueber den lokalen
    `usd_reconciled`-Marker) entschieden, sondern von `admission.
    record_usd_delta` selbst, die Betrag UND angewandte `request_id` ATOMAR
    in DEMSELBEN `lab.status.json`-Schreibvorgang festhaelt (kein Fenster
    zwischen 'Betrag gebucht' und 'als gebucht markiert' -- genau das
    Fenster, das den alten `usd_reconciled`-Marker angreifbar machte: der
    Marker stand bereits fest, BEVOR die Buchung selbst passiert war, sodass
    ein Absturz dazwischen die Buchung dauerhaft verlor, s. REVIEW-I2.md §3
    Fall 02). `usd_reconciled` bleibt als Auditfeld erhalten (bestehende
    Tests/End-Critic-Sicht lesen es), ist aber nicht mehr die
    Entscheidungsquelle fuer 'wurde das Delta schon angewandt'.

    `record_usd_delta` sitzt weiterhin an DERSELBEN Stelle wie `add_seconds`
    -- zwischen dem ersten und dem zweiten `_write_request`-Aufruf (PLAN-
    CRITIC Auflage 5) -- ein simulierter Schreibfehler GENAU zwischen diesen
    beiden Schritten (Test `test_reconciliation_write_failure_after_delta_
    booked_before_accounted_is_retry_safe`) zeigt weiterhin `state=received`,
    `usd_reconciled=True` UND das bereits gebuchte Delta, ohne dass ein Retry
    es doppelt bucht (die Idempotenzpruefung in `record_usd_delta` haelt das
    zweite Mal fest, dass diese `request_id` bereits in
    `reconciled_request_ids` steht).

    R1-Fix (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
    02): diese Funktion faengt KEINE Ausnahme von `record_usd_delta` ab.
    Schlaegt die Delta-Buchung fehl (nicht lesbare/kaputte `lab.status.json`
    ODER ein Teilschreibfehler -- `record_usd_delta` propagiert beides seit
    R1/R2, statt still zurueckzukehren), bricht `finish_received` hier ab:
    die letzten beiden Zeilen (`state=accounted`) werden NICHT mehr
    erreicht, der Datensatz bleibt ehrlich `state=received`. Ein
    voruebergehender Lesefehler ist damit KEIN erfolgreicher No-op mehr,
    sondern ein offener, retryfaehiger Zwischenzustand -- exakt wie ein
    Schreibfehler zwischen den beiden `_write_request`-Aufrufen (Absatz
    oben). `record_usd_delta` selbst haelt Betrag UND angewandte
    `request_id` ATOMAR (R2: Temp-Datei + `os.replace`, s. `core.admission.
    _atomic_write_json`) in DEMSELBEN `lab.status.json`-Schreibvorgang fest
    (kein Fenster zwischen 'Betrag gebucht' und 'als gebucht markiert' --
    genau das Fenster, das den alten `usd_reconciled`-Marker angreifbar
    machte: der Marker stand bereits fest, BEVOR die Buchung selbst
    passiert war, sodass ein Absturz dazwischen die Buchung dauerhaft
    verlor, s. REVIEW-I2.md §3 Fall 02). Ein gewoehnlicher Teilschreibfehler
    WAEHREND dieses Writes zerstoert dank R2 nicht mehr den zuletzt
    gueltigen `lab.status.json`-Stand.

    G3-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 04/05): `add_seconds` faengt seither
    ebenfalls KEINEN Lese-/Parsefehler mehr ab (analog `record_usd_delta`)
    -- ein Fehler GENAU beim Nachtragen der Dauer bricht `finish_received`
    HIER ab (Fall 04: `received` bleibt offen, `seconds_elapsed` bleibt
    unveraendert statt faelschlich `accounted` mit 0 zu werden). `add_seconds`
    dedupliziert zusaetzlich per `request_id` (eigene Liste,
    `reconciled_seconds_request_ids`, getrennt von `reconciled_request_ids`
    fuer die Geldkorrektur) -- ein Retry NACH einem Fehler zwischen dieser
    Zeile und dem finalen `state=accounted`-Marker (Fall 05) traegt dieselbe
    Dauer deshalb nicht ein zweites Mal nach."""
    data = load_request(run_dir, request_id)
    if data is None or data.get("state") == "accounted":
        return
    # G2b (Bau-GO 2026-09-27): eine NICHT dollarbepflichtete Rolle (CLI/Abo)
    # hat `begin()` bereits mit `reserved_usd=0.0` (nicht dem geschaetzten
    # Wert) gebucht -- eine ggf. vom Treiber gemeldete `usage` (z.B. Token-
    # zaehlung eines CLI-Tools) darf HIER keine nachtraegliche Dollarkorrektur
    # ausloesen (das waere exakt die verbotene erfundene Dollarabrechnung
    # fuer eine Rolle ohne API-Kosten, H-E).
    dollar_billed = data.get("dollar_billed", True)
    reserved_usd = data.get("reserved_usd")
    real_usd = compute_turn_usd(usage) if dollar_billed else None
    delta = None
    if real_usd is not None and reserved_usd is not None and real_usd > reserved_usd:
        delta = real_usd - reserved_usd
    data["state"] = "received"
    data["usage"] = usage
    data["settled_ts"] = time.time()
    data["usd_reconciled"] = True
    data["result_text"] = result_text
    # R1 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md §3):
    # dieselbe URSPRUENGLICHE, tatsaechlich gemessene Antwortdauer wird
    # bereits in DIESEM ersten Write dauerhaft mitgeschrieben -- ein
    # Folgeprozess, der spaeter (nach einem Fehler in `add_seconds`/
    # `record_usd_delta` unten) `settle_received()` fuer diesen Record
    # aufruft, hat die reale Latenz des damaligen Requests selbst nicht
    # mehr beobachtet und darf sie deshalb weder auf 0 setzen noch neu
    # schaetzen -- s. `settle_received()`-Docstring.
    data["received_seconds"] = seconds
    _write_request(run_dir, request_id, data)
    add_seconds(run_dir, request_id, seconds)
    if delta is not None:
        record_usd_delta(run_dir, request_id, delta)
    data["state"] = "accounted"
    _write_request(run_dir, request_id, data)


def settle_received(run_dir: str | Path, record: dict) -> dict:
    """R1 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md §3):
    idempotente Fortsetzung des ZWEITEN `finish_received()`-Writes fuer
    einen Datensatz, den `find_durable_result()` als `state=received`
    (nicht `accounted`) geliefert hat -- sein `result_text`/`usage`/
    `received_seconds` liegen bereits durabel vor (ERSTER Write), nur die
    NACHGELAGERTE Kosten-/Latenzbuchung (`add_seconds`/`record_usd_delta`)
    ist noch offen, weil sie beim urspruenglichen `finish_received()`-Aufruf
    an einem gewoehnlichen `OSError` gescheitert ist (G3-Fix/R1-Fix in
    `finish_received`, dort ungefangen).

    Ein Aufrufer (`core.creation_service.run_admitted_creation_dialog` fuer
    den GM-Turn, `domain.zeitriss.community_creation._persona_get_reply_
    factory` fuer den Persona-Turn) MUSS dies fuer einen `state=received`-
    Treffer aus `find_durable_result()` GENAU EINMAL aufrufen, BEVOR er den
    Treffer als abgeschlossene Voraussetzung fuer den naechsten Schritt
    (Cursor-/Bereitschaftsfortschritt) behandelt -- sonst wird eine
    tatsaechlich noch offene Buchung still uebergangen (REVIEW-COMMUNITY-
    RECOVERY.md §3: 'kann eine Figur vollstaendig veroeffentlichen ...
    obwohl ein zugehoeriger Request dauerhaft offen und unvollstaendig
    verbucht bleibt').

    Idempotent wie `finish_received` selbst: ein bereits `accounted`er
    Datensatz ist ein No-op (liefert ihn unveraendert zurueck -- ein
    Aufrufer darf dies deshalb gefahrlos auch fuer einen bereits
    `accounted`en Treffer aufrufen, ohne den Zustand vorher selbst pruefen
    zu muessen). Verwendet `record["received_seconds"]` (die im ERSTEN
    `finish_received()`-Write persistierte URSPRUENGLICHE Antwortdauer)
    statt einer neu gemessenen Dauer -- ein Folgeprozess hat die
    tatsaechliche Latenz des damaligen Requests nicht mehr beobachtet,
    darf sie deshalb weder auf 0 setzen noch neu schaetzen (R1).

    A1-Fix (Altformat-Recovery-Nachzug 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    A1): unbekannt ist NICHT 0. Ein Bestandsrecord OHNE `received_seconds`
    (Schluessel ABWESENT -- vor diesem Fix geschrieben, s.
    `_CONTROL_FIELD_TYPES`) traegt keine bekannte Dauer nach. Fruehere
    Fassung buchte in diesem Fall `0.0` (identisch zu `add_seconds`s
    bestehendem `if not seconds: return` No-op) und setzte den Datensatz
    trotzdem auf `accounted` -- das war eine erfundene Nullbuchung, fuer die
    keine Nutzerfreigabe vorliegt (REVIEW-COMMUNITY-ALTFORMAT.md §3). Diese
    Funktion unterscheidet jetzt PRAESENZ des Schluessels (`"received_seconds"
    in record`, NICHT Truthiness -- eine tatsaechlich aufgezeichnete `0.0` ist
    weiterhin eine gueltige bekannte Dauer und wird normal gesettled) von
    ABWESENHEIT: fehlt der Schluessel (oder ist er explizit `None`), bleibt
    der Datensatz UNVERAENDERT bei `state=received` -- KEINE Zeit-/
    Geldbuchung, KEIN Uebergang nach `accounted`. Der Aufrufer (GM in
    `creation_service.run_admitted_creation_dialog`, Persona in
    `domain.zeitriss.community_creation._get_reply`) MUSS danach pruefen, ob
    der zurueckgelieferte Datensatz jetzt `state=accounted` traegt -- ist das
    nicht der Fall, blockiert er kontrolliert (kein `completed`/
    `already_ready`, kein abhaengiger Modellaufruf, Cursor/Publikation
    ruecken NICHT vor). `usage`/`reserved_usd` sind bereits Teil des
    uebergebenen, aus `find_durable_result()` stammenden Datensatzes
    (derselbe erste Write).

    Ein Fehler in `add_seconds`/`record_usd_delta` propagiert weiterhin
    UNGEFANGEN -- der Datensatz bleibt dann ehrlich bei `state=received`,
    exakt wie bei einem frischen `finish_received()`-Aufruf; ein spaeterer
    Aufruf (fuer denselben Datensatz/dieselbe `request_id`) ist erneut
    idempotent sicher (beide Helfer dedupliziert per `request_id`, s.
    `admission.add_seconds`/`record_usd_delta`)."""
    if record.get("state") == "accounted":
        return record
    if "received_seconds" not in record or record.get("received_seconds") is None:
        # A1: unbekannte Originaldauer -- kontrolliert offen halten, keine
        # Schaetzung/Nullbuchung, kein Uebergang nach `accounted` (s.o.).
        return record
    request_id = record["id"]
    reserved_usd = record.get("reserved_usd")
    usage = record.get("usage")
    seconds = record["received_seconds"]
    # G2b (Bau-GO 2026-09-27): dieselbe Nicht-Dollarrolle-Ausnahme wie
    # `finish_received()` -- s. dortigen Kommentar.
    dollar_billed = record.get("dollar_billed", True)
    real_usd = compute_turn_usd(usage) if dollar_billed else None
    delta = None
    if real_usd is not None and reserved_usd is not None and real_usd > reserved_usd:
        delta = real_usd - reserved_usd
    add_seconds(run_dir, request_id, seconds)
    if delta is not None:
        record_usd_delta(run_dir, request_id, delta)
    settled = dict(record)
    settled["state"] = "accounted"
    _write_request(run_dir, request_id, settled)
    return settled


def finish_error(run_dir: str | Path, request_id: str, *, error: object, seconds: float = 0.0) -> None:
    """Versand fand statt (state war bereits `sent`), aber keine
    verwertbare Antwort (Timeout/Transportfehler/Ausnahme) -- die bereits in
    `begin()` committete Reservierung bleibt UNANGETASTET (kein Refund,
    Case 05: 'Versuch + reservierte Verpflichtung bei fehlender Antwort
    bleiben erhalten'). Der Datensatz wechselt nach `error` und sofort
    weiter nach `accounted` (die lokale Buchung fuer DIESE Anfrage ist
    damit abschliessend — ein spaeterer Retry ist ein NEUER Request mit
    eigener Reservierung, kein Wiederaufsetzen auf demselben Datensatz).

    G3-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4): derselbe `add_seconds`-Vertrag wie
    `finish_received` -- ein Fehler beim Nachtragen der Dauer bricht HIER
    ab (`state=error` bleibt offen, wird nicht faelschlich `accounted`),
    ein Retry fuer dieselbe `request_id` traegt dieselbe Dauer dank der
    `reconciled_seconds_request_ids`-Deduplizierung nicht doppelt nach."""
    data = load_request(run_dir, request_id)
    if data is None or data.get("state") == "accounted":
        return
    data["state"] = "error"
    data["error"] = str(error)[:500]
    data["settled_ts"] = time.time()
    _write_request(run_dir, request_id, data)
    add_seconds(run_dir, request_id, seconds)
    data["state"] = "accounted"
    _write_request(run_dir, request_id, data)


# ---------------------------------------------------------------------------
# REC-2 (04_REQUEST_RECOVERY.md §2B/§2C, ZR-UPDATE-RESUME-REPARATUR
# 2026-11-23): additive Unknown-Disposition + EIN crashfest gebundener
# neuer Versuch fuer einen echten `find_open_orphan()`-Treffer.
# ---------------------------------------------------------------------------


class StaleDispositionError(RuntimeError):
    """REC-2 (04 §2C: 'veraenderte Zielbindung/Vorzustand VOR Wirkung
    ablehnen'): der Originalrecord hat sich seit der Disposition veraendert
    (anderer `state`/`content_sha256` -- z.B. inzwischen doch durabel
    empfangen) -- die Disposition ist damit NICHT mehr an denselben
    Vorzustand gebunden, den sie bei ihrer Erstellung bewertet hat.
    Kontrollierte Ablehnung statt stillem Weiterverwenden eines veralteten
    Befunds."""


def _recovery_dispositions_dir(run_dir: str | Path) -> Path:
    # BEWUSST ein eigenes Verzeichnis, NICHT `requests/` -- `_all_records()`
    # globt `requests/*.json` und wuerde eine Dispositionsdatei dort als
    # (nicht einordenbaren) Requestdatensatz fehlinterpretieren und damit
    # `begin()`s Dedup/`open_requests()`/`find_durable_result()` fuer JEDEN
    # Aufrufer verfaelschen. Additiv/getrennt vom Originalrecord (04 §2B:
    # 'kann den Originalrecord unangetastet lassen').
    #
    # R4 (PR #3317-Nachzug 2026-11-23, RECOVERY_REVIEW R4): REINE Pfadberechnung,
    # KEIN `mkdir` -- `_recovery_disposition_path`/`load_recovery_disposition`
    # werden auch vom zugesagt rein lesenden Inspect/Plan/Zurueck-Weg aufgerufen
    # und duerfen die Ablage NICHT anlegen (frueher erzeugte ein blosser
    # `load_recovery_disposition(...)`-Aufruf `run/recovery_dispositions/`,
    # obwohl er nur `None` lieferte). Die Verzeichnisanlage passiert jetzt
    # ausschliesslich im bewussten Mutationspfad ueber
    # `_ensure_recovery_dispositions_dir` (`dispose_open_orphan`/
    # `authorize_bound_retry`, unmittelbar vor ihrem Write).
    return Path(run_dir) / "recovery_dispositions"


def _ensure_recovery_dispositions_dir(run_dir: str | Path) -> Path:
    """R4: legt die Dispositionsablage an -- NUR im bewussten Mutationspfad
    unmittelbar vor einem `_atomic_write_json` aufzurufen (dessen Temp-Datei
    das Zielverzeichnis bereits braucht). Die reine Pfad-/Lesefunktion bleibt
    schreibfrei."""
    d = _recovery_dispositions_dir(run_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _recovery_disposition_path(run_dir: str | Path, original_request_id: str) -> Path:
    return _recovery_dispositions_dir(run_dir) / f"{original_request_id}.json"


def load_recovery_disposition(run_dir: str | Path, original_request_id: str) -> dict | None:
    """Rein lesend -- `None` ohne vorhandene Disposition fuer diese
    Original-Request-ID (kein erfundener Default)."""
    path = _recovery_disposition_path(run_dir, original_request_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _current_run_id(run_dir: str | Path) -> str | None:
    """R5 (RECOVERY_REVIEW R5 "vollstaendige Grantbindung vor Nutzung"):
    liest `run_id.json` (von `core.store._run_id` geschrieben) rein lesend,
    OHNE sie bei Abwesenheit anzulegen -- fuer den Run-Bindungs-Re-Check in
    `dispose_open_orphan`/`commit_authorized_retry`. `None` bei fehlender/
    unlesbarer/unvollstaendiger Datei (kein erfundener Ersatzwert, kein
    neuer strikter Lesevertrag -- `core.recovery_ops._run_binding` bleibt
    die strengere Auditfassung fuer `plan_orphan_recovery`/`apply_orphan_
    recovery`; dies hier ist nur der leichte Re-Check unmittelbar vor
    Verbrauch an der gemeinsamen Low-Level-Naht, die `recovery_ops`
    NICHT importieren darf, ohne einen Zirkelimport zu erzeugen)."""
    path = Path(run_dir) / "run_id.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    run_id = data.get("run_id") if isinstance(data, dict) else None
    return run_id if isinstance(run_id, str) and run_id else None


def dispose_open_orphan(run_dir: str | Path, original_request_id: str, *, reason: str) -> dict:
    """REC-2 §2B: haelt additiv fest, dass der alte Ausgang von
    `original_request_id` UNBEKANNT bleibt (weder Erfolg noch Fehlschlag
    behauptet), die bisherige Reservierung BLEIBT (dieser Aufruf schreibt
    den Originalrecord NICHT um), und bindet einen Entscheidungsgrund daran.
    Der Originalrecord selbst (Usage/Dauer/Kosten/`result_text`/`state`)
    bleibt bytegleich unveraendert -- diese Funktion schreibt ausschliesslich
    in `recovery_dispositions/`.

    Nur fuer einen ECHTEN offenen Orphan sinnvoll (`state in ("reserved",
    "sent")`, s. `find_open_orphan`) -- ein bereits abgeschlossener Record
    (`received`/`accounted`/`error`) hat einen bekannten Ausgang, den eine
    Unknown-Disposition nicht ueberschreiben darf (04 §2A Tabelle: 'echte
    beobachtete Fehlerantwort bereits korrekt verbucht -> bestehenden
    Fehler-/Retryvertrag erhalten').

    Idempotent: eine bereits vorhandene Disposition fuer DIESELBE Original-
    ID wird NICHT durch eine zweite ersetzt, solange sie noch zum aktuellen
    Originalzustand passt (`state`+`content_sha256` unveraendert) --
    liefert dann die BESTEHENDE Disposition unveraendert zurueck (kein
    zweiter Dispositionseintrag, kein verlorener `granted_request_id`,
    falls bereits ein gebundener Versuch autorisiert wurde). Hat sich der
    Originalrecord seitdem veraendert (z.B. doch noch durabel empfangen),
    wirft dies `StaleDispositionError` -- keine stille Weiterverwendung
    einer ueberholten Disposition (04 §2C).

    R5 (RECOVERY_REVIEW R5/§6 "vollstaendige Grantbindung vor Nutzung"):
    haelt additiv den VOLLEN Original-Dateihash (`original_request_sha256`,
    staerker als der bereits vorhandene `original_content_sha256`, der nur
    das `content`-Feld misst) UND die aktuelle Run-Bindung (`bound_run_id`,
    s. `_current_run_id`) fest -- beide werden von `commit_authorized_
    retry` unmittelbar VOR Verbrauch gegen den dann aktuellen Stand
    geprueft (Apply prueft diese Werte zwar bereits VOR diesem Aufruf
    gegen den Plan, reichte sie bisher aber nicht dauerhaft an den Grant
    weiter). Keine zweite Recoverydatenbank -- beide Felder leben im
    bereits bestehenden Dispositionsdokument."""
    record = load_request(run_dir, original_request_id)
    if record is None:
        raise ValueError(
            f"kein Requestdatensatz fuer id={original_request_id!r} -- Disposition braucht einen "
            "real vorhandenen Originalrecord."
        )
    # Staleness-Check VOR dem Vorzustands-Guard unten: eine BEREITS
    # vorhandene Disposition, deren Originalrecord sich seitdem veraendert
    # hat (z.B. inzwischen `accounted`), ist IMMER ein Staleness-Befund
    # (`StaleDispositionError`) -- unabhaengig davon, ob der NEUE Zustand
    # selbst fuer eine FRISCHE Disposition gueltig waere. Nur wenn NOCH
    # KEINE Disposition existiert, entscheidet der Vorzustands-Guard unten,
    # ob ueberhaupt eine neue angelegt werden darf.
    existing = load_recovery_disposition(run_dir, original_request_id)
    if existing is not None:
        if (
            existing.get("original_state_at_disposition") == record.get("state")
            and existing.get("original_content_sha256") == record.get("content_sha256")
        ):
            return existing
        raise StaleDispositionError(
            f"Disposition fuer id={original_request_id!r} existiert bereits, aber der "
            f"Originalrecord hat sich seitdem veraendert (vorher state="
            f"{existing.get('original_state_at_disposition')!r}, jetzt {record.get('state')!r}) -- "
            "keine stille Neuerstellung einer veralteten Disposition."
        )
    if record.get("state") not in ("reserved", "sent"):
        raise ValueError(
            f"Requestdatensatz id={original_request_id!r} hat state={record.get('state')!r} -- "
            "eine Unknown-Disposition ist nur fuer einen echten offenen Orphan (state in "
            "('reserved','sent')) sinnvoll, nicht fuer einen bereits abgeschlossenen Record "
            "(04 §2A: bestehenden Vertrag fuer received/accounted/error erhalten)."
        )
    disposition = {
        "original_request_id": original_request_id,
        "original_state_at_disposition": record.get("state"),
        "original_content_sha256": record.get("content_sha256"),
        # Liste statt Tupel: JSON kennt keine Tupel -- ein nach dem Schreiben
        # neu von der Platte gelesenes Dict (`load_recovery_disposition`)
        # haette sonst `list` statt `tuple`, obwohl inhaltlich identisch --
        # `== ` auf dem direkt zurueckgegebenen Dict (dieser Aufruf) UND dem
        # spaeter neu gelesenen (idempotenter zweiter Aufruf) soll bytegleich
        # vergleichbar bleiben.
        "original_identity": list(_operation_identity(record)),
        # R5: voller Byte-Hash der Originaldatei (nicht nur `content`) --
        # erkennt JEDE Drift des Originalrecords, nicht nur eine am
        # gesendeten Inhalt.
        "original_request_sha256": hashlib.sha256(
            _request_path(run_dir, original_request_id).read_bytes()
        ).hexdigest(),
        "bound_run_id": _current_run_id(run_dir),
        "reason": str(reason),
        "disposed_ts": time.time(),
        "granted_request_id": None,
    }
    _ensure_recovery_dispositions_dir(run_dir)
    _atomic_write_json(_recovery_disposition_path(run_dir, original_request_id), disposition)
    return disposition


def authorize_bound_retry(run_dir: str | Path, original_request_id: str) -> str:
    """REC-2 §2B/§2C: autorisiert GENAU EINEN neuen, an die Disposition
    gebundenen Versuch fuer den disponierten Orphan -- liefert dessen NEUE
    `request_id`. Der neue Record wird mit `state="reserved"` angelegt (NOCH
    KEIN `sent`) und traegt additiv `recovery_of=original_request_id` +
    `recovery_reason` -- der tatsaechliche Versand/Transport-Call bleibt
    beim regulaeren Caller (04 §2D: 'Apply autorisiert/reconciliert NUR;
    Versand erst ueber regulaeren Caller mit dessen Budget-/Spielregeln').
    Dieser Aufruf selbst macht KEINEN Modell-/Transportcall.

    Crashfeste Kopplung (04 §2C: 'Verbrauchsmarke der einmaligen
    Autorisierung und die zugehoerige neue Request-ID muessen so dauerhaft
    gekoppelt werden, dass ein Absturz keinen zweiten Nachfolger
    ermoeglicht'): die neue Request-ID wird DETERMINISTISCH aus der
    Original-ID abgeleitet (`sha256(original_id + ':rec2-retry')`), NICHT
    zufaellig -- ein Absturz zwischen 'neuer Record geschrieben' und
    'Disposition auf granted_request_id aktualisiert' UND ein anschliessender
    Retry dieser Funktion berechnen/finden DIESELBE ID wieder (Idempotenz
    ueber den Dateinamen selbst, kein zweiter Nachfolger moeglich). Bereits
    gesetztes `granted_request_id` liefert dieselbe ID erneut zurueck
    (wiederholtes Apply = No-op, 04 §2C)."""
    disposition = load_recovery_disposition(run_dir, original_request_id)
    if disposition is None:
        raise ValueError(
            f"keine Disposition fuer id={original_request_id!r} -- erst `dispose_open_orphan` "
            "aufrufen, bevor ein gebundener Versuch autorisiert werden kann."
        )
    record = load_request(run_dir, original_request_id)
    if (
        record is None
        or record.get("state") != disposition.get("original_state_at_disposition")
        or record.get("content_sha256") != disposition.get("original_content_sha256")
    ):
        raise StaleDispositionError(
            f"Originalrecord id={original_request_id!r} passt nicht mehr zur Disposition "
            "(veraenderter Vorzustand) -- kein Apply auf einer veralteten Bindung (04 §2C)."
        )
    if disposition.get("granted_request_id"):
        return disposition["granted_request_id"]
    new_request_id = hashlib.sha256(f"{original_request_id}:rec2-retry".encode("utf-8")).hexdigest()
    # Verteidigungslinie gegen genau den beschriebenen Crash: der neue
    # Record koennte bereits existieren (vorheriger Absturz NACH diesem
    # Write, VOR dem Disposition-Update unten) -- dann NICHT erneut
    # anlegen, nur die Disposition nachziehen.
    if load_request(run_dir, new_request_id) is None:
        table_id, section_id, role, turn_idx, participant = disposition["original_identity"]
        new_record = {
            "id": new_request_id,
            "role": role,
            "route": record.get("route"),
            "content_chars": record.get("content_chars"),
            "content_sha256": record.get("content_sha256"),
            "output_limit_tokens": record.get("output_limit_tokens"),
            "reserved_usd": record.get("reserved_usd"),
            "table_id": table_id,
            "section_id": section_id,
            "turn_idx": turn_idx,
            "participant": participant,
            "state": "reserved",
            "reserved_ts": time.time(),
            "sent_ts": None,
            "settled_ts": None,
            "usage": None,
            "error": None,
            "usd_reconciled": False,
            "result_text": None,
            "dollar_billed": record.get("dollar_billed", True),
            "recovery_of": original_request_id,
            "recovery_reason": disposition.get("reason"),
        }
        _write_request(run_dir, new_request_id, new_record)
    disposition = dict(disposition)
    disposition["granted_request_id"] = new_request_id
    _ensure_recovery_dispositions_dir(run_dir)
    _atomic_write_json(_recovery_disposition_path(run_dir, original_request_id), disposition)
    return new_request_id


def disposition_binding_intact(
    run_dir: str | Path, follower_record: dict | None, original_record: dict | None,
    disposition: dict | None,
) -> bool:
    """R5 (PR #3317-Nachzug r2, RECOVERY_REVIEW.md R5/§2 "denselben
    vorhandenen vollstaendigen Bindungsentscheid vor jeder Grant-Ausnahme und
    am Verbrauch anwenden"): REIN LESENDES Praedikat, das GENAU dieselben
    fuenf Bindungspruefungen wie `commit_authorized_retry` zusammenfasst,
    aber NICHTS wirft und NICHTS schreibt -- fuer die Grant-Ausnahmen in
    `core.runtime._collect_reflections` und der Open-Plan-Vorsperre in
    `core.lobby_flow`, die bisher nur truthy `recovery_of`/`state` bzw. allein
    `original_identity` prueften. `follower_record` ist der gebundene Folger
    (`recovery_of`), `original_record` sein referenziertes Original,
    `disposition` die unter der Original-ID geladene Disposition.

    True NUR wenn ALLE gelten (fehlende/`None` erwartete Dispositionsfelder
    ueberspringen ihre jeweilige Pruefung -- identisch zu `commit_authorized_
    retry`, das `expected_* is None`-Felder ebenfalls nicht erzwingt):
    1. Disposition vorhanden UND ihr `granted_request_id` zeigt GENAU auf
       diesen Folger (kein fremder/veralteter Grant).
    2. Originalrecord vorhanden UND `state`/`content_sha256` unveraendert
       seit der Disposition.
    3. Volle Operationsidentitaet von Original UND Folger == gebundene
       `original_identity`.
    4. Voller Byte-Hash der Originaldatei == gebundener `original_request_
       sha256`.
    5. Aktuelle Run-Bindung == gebundene `bound_run_id`.
    Jeder Lesefehler (fehlende Datei etc.) ergibt False -- kein erfundener
    Treffer. Dies DUPLIZIERT die `commit_authorized_retry`-Entscheidung
    bewusst als nebenwirkungsfreie Vorab-Pruefung (kein neuer Datenspeicher,
    keine zweite Recoverylogik); `commit_authorized_retry` bleibt die
    AUTORITATIVE werfende Fassung am tatsaechlichen Buchungseinstieg."""
    if follower_record is None or disposition is None:
        return False
    if disposition.get("granted_request_id") != follower_record.get("id"):
        return False
    if (
        original_record is None
        or original_record.get("state") != disposition.get("original_state_at_disposition")
        or original_record.get("content_sha256") != disposition.get("original_content_sha256")
    ):
        return False
    expected_identity = disposition.get("original_identity")
    if expected_identity is not None and (
        list(_operation_identity(original_record)) != expected_identity
        or list(_operation_identity(follower_record)) != expected_identity
    ):
        return False
    original_request_id = disposition.get("original_request_id") or original_record.get("id")
    expected_hash = disposition.get("original_request_sha256")
    if expected_hash is not None:
        try:
            actual_hash = hashlib.sha256(
                _request_path(run_dir, original_request_id).read_bytes()
            ).hexdigest()
        except OSError:
            return False
        if actual_hash != expected_hash:
            return False
    expected_run_id = disposition.get("bound_run_id")
    if expected_run_id is not None and _current_run_id(run_dir) != expected_run_id:
        return False
    return True


def commit_authorized_retry(
    run_dir: str | Path, request_id: str, *, content: str, reserved_usd: float | None,
    route: str | None = None, output_limit_tokens: float | None = None, dollar_billed: bool = True,
) -> None:
    """REC-2 §2B/§2D: der REGULAERE Caller (nicht `authorize_bound_retry`
    selbst) ruft dies UNMITTELBAR VOR seinem eigenen Transport-`try` fuer
    einen bereits per `authorize_bound_retry` reservierten Record auf --
    exakt dieselben zwei Schritte wie `begin()` (Budget-Reservierung JETZT
    buchen, dann `state="sent"`), aber auf der SCHON VORHANDENEN, deterministisch
    gebundenen `request_id` statt einer neuen Zufalls-UUID (04 §2C: 'aktuelle
    Admission/Route/Outputgrenze und eine eigene einmalige Reservierung').
    `content`/`reserved_usd`/`route`/`output_limit_tokens` kommen vom
    Aufrufer FRISCH aus dem tatsaechlich jetzt zu sendenden Kontext (04 §2B:
    'der neue Request speichert seinen tatsaechlich verwendeten Input; ein
    neu aufgebauter Kontext wird nicht als nachgewiesen bytegleicher
    Altinput ausgegeben') -- koennen vom Autorisierungszeitpunkt abweichen.

    Idempotent/crashfest: nur wirksam, wenn der Record noch `state=
    "reserved"` ist (der Zustand, den `authorize_bound_retry` hinterlaesst).
    Ein Record, der bereits `"sent"` oder weiter ist (z.B. nach einem Absturz
    NACH einem vorherigen `commit_authorized_retry`-Aufruf, VOR dem
    eigentlichen Transport-Call), wird NICHT erneut gebucht -- kein
    Doppelbuchen, kein zweiter `record_turn_usage`-Aufruf fuer dieselbe ID."""
    record = load_request(run_dir, request_id)
    if record is None:
        raise ValueError(f"kein Requestdatensatz fuer id={request_id!r} -- authorize_bound_retry zuerst aufrufen.")
    if not record.get("recovery_of"):
        raise ValueError(
            f"Requestdatensatz id={request_id!r} traegt kein `recovery_of` -- commit_authorized_retry "
            "ist nur fuer einen per `authorize_bound_retry` angelegten Record vorgesehen."
        )
    # R2 (PR #3317-Nachzug 2026-11-23, RECOVERY_REVIEW.md R2 Z.60-62): die
    # beiden Checks oben pruefen nur die BEDEUTUNG des `recovery_of`-Feldes,
    # nicht ob dieser Record tatsaechlich aus einer echten, ungebrochenen
    # `dispose_open_orphan`->`authorize_bound_retry`-Kette stammt -- es
    # fehlte jede `load_recovery_disposition`-Lesung UND ein Abgleich gegen
    # die AKTUELLE Original-/Grantbindung ("Eine richtige Bedien-/
    # Anwendungsschicht, die diese Anforderungen stattdessen garantiert,
    # fehlt"). `core.recovery_ops` (die jetzt gebaute R2-Anwendungsschicht)
    # garantiert Run-/Writer-/Plan-/Vorzustandsbindung bereits VOR dem
    # `authorize_bound_retry`-Aufruf -- dies hier ist der laut Review
    # geforderte Pflicht-Rest GENAU an diesem Low-Level-Einstieg: VOR jeder
    # Buchung erneut lesen+pruefen, dass (a) eine Disposition fuer
    # `original_request_id` existiert, (b) ihr `granted_request_id` GENAU
    # auf DIESEN `request_id` zeigt (kein fremder/veralteter Folger), und
    # (c) der referenzierte Originalrecord sich seit der Disposition NICHT
    # veraendert hat (dieselbe Staleness-Pruefung wie `authorize_bound_
    # retry` selbst, hier zusaetzlich unmittelbar am tatsaechlichen
    # Buchungseinstieg wiederholt). Bewusst VOR dem `state != "reserved"`-
    # Rueckgabepfad unten -- die Bindung gilt fuer JEDEN Aufruf, auch einen
    # idempotenten Wiedereintritt, nicht nur den allerersten.
    original_request_id = record.get("recovery_of")
    disposition = load_recovery_disposition(run_dir, original_request_id)
    if disposition is None or disposition.get("granted_request_id") != request_id:
        raise ValueError(
            f"Requestdatensatz id={request_id!r}: keine passende Disposition fuer "
            f"recovery_of={original_request_id!r} (granted_request_id stimmt nicht oder fehlt) -- "
            "commit_authorized_retry bucht nur einen tatsaechlich ueber dispose_open_orphan/"
            "authorize_bound_retry gebundenen Folger."
        )
    original_record = load_request(run_dir, original_request_id)
    if (
        original_record is None
        or original_record.get("state") != disposition.get("original_state_at_disposition")
        or original_record.get("content_sha256") != disposition.get("original_content_sha256")
    ):
        raise StaleDispositionError(
            f"Original id={original_request_id!r} hat sich seit der Disposition veraendert -- "
            "commit_authorized_retry bucht nicht auf einer veralteten Original-/Grantbindung."
        )
    # R5 (RECOVERY_REVIEW R5/§6 "vollstaendige Grantbindung vor Nutzung"):
    # der obige Check prueft nur `state`/`content_sha256` -- weder die
    # volle Operationsidentitaet (Original UND der hier zu verbuchende
    # Folger selbst) noch der volle Original-Dateihash noch die Run-
    # Bindung wurden bisher gegen den aktuellen Stand wiederholt (Apply,
    # `core.recovery_ops.apply_orphan_recovery`, prueft sie zwar VOR diesem
    # Aufruf gegen den Plan, reicht sie aber nicht an den Grant weiter). Ein
    # truthy `recovery_of` + passendes `granted_request_id` allein genuegt
    # NICHT (Review-Wortlaut) -- bei JEDER Drift bricht dies TYPISIERT und
    # OHNE Versand ab (noch VOR der Buchung unten).
    expected_identity = disposition.get("original_identity")
    if expected_identity is not None and (
        list(_operation_identity(original_record)) != expected_identity
        or list(_operation_identity(record)) != expected_identity
    ):
        raise StaleDispositionError(
            f"Original id={original_request_id!r}: Operationsidentitaet von Original und/oder "
            "Folger stimmt nicht (mehr) mit der bei der Disposition gebundenen Identitaet ueberein "
            "-- commit_authorized_retry bucht nicht auf einer veralteten Identitaetsbindung."
        )
    expected_hash = disposition.get("original_request_sha256")
    if expected_hash is not None and (
        hashlib.sha256(_request_path(run_dir, original_request_id).read_bytes()).hexdigest() != expected_hash
    ):
        raise StaleDispositionError(
            f"Original id={original_request_id!r}: voller Dateihash stimmt nicht (mehr) mit dem bei "
            "der Disposition gebundenen Hash ueberein -- commit_authorized_retry bucht nicht auf "
            "einer veralteten Dateibindung."
        )
    expected_run_id = disposition.get("bound_run_id")
    if expected_run_id is not None and _current_run_id(run_dir) != expected_run_id:
        raise StaleDispositionError(
            f"Original id={original_request_id!r}: aktuelle Run-Bindung (run_id.json) stimmt nicht "
            "(mehr) mit der bei der Disposition gebundenen Run-Identitaet ueberein -- "
            "commit_authorized_retry bucht nicht auf einer fremden/veralteten Run-Bindung."
        )
    if record.get("state") != "reserved":
        return
    # R3 (PR #3317-Nachzug 2026-11-23, RECOVERY_REVIEW R3, RECOVERY_LEDGER_WITNESS):
    # crashfester Wiedereintritt NACH erfolgreicher Buchung (`record_turn_usage`
    # unten), aber VOR dem `state="sent"`-Write -- der Record blieb `reserved`,
    # das Budget ist aber schon gebucht. Die bereits gebuchte Reservierung darf
    # dann NICHT mit frisch berechneten (ggf. hoeheren) Versandparametern
    # ueberschrieben werden: `record_turn_usage` waere per `once_request_id` ein
    # No-op (keine zweite Buchung), waehrend `finish_received` das Delta spaeter
    # gegen das hoehere `reserved_usd` rechnete und den bereits gebuchten Betrag
    # unterschlueg (Witness: erhaltene Summe 0,011 statt erforderlicher 0,021 USD).
    # Der VOR der Buchung geschriebene Record traegt bereits die tatsaechlich
    # gebuchte BASIS (`reserved_usd`/`dollar_billed`) -- NUR diese bleibt
    # eingefroren, weil `finish_received` das Delta gegen den gebuchten
    # `reserved_usd` rechnet; ein Rewrite verursachte das Unterbuchen. Die rein
    # DESKRIPTIVEN Audit-Felder (`content_sha256`/`content_chars`/`route`/
    # `output_limit_tokens`) muessen dagegen den TATSAECHLICH jetzt physisch
    # gesendeten Input widerspiegeln: der Caller ruft nach diesem Commit
    # `gm_transport.turn(..., outgoing)` mit dem frischen (ggf. nach Crash-
    # Neustart geaenderten) Kontext, nicht mit dem Alt-Text. Blieben die
    # Content-Felder stale, behauptete der Record einen anderen Inhalt als
    # physisch versendet und braeche stillschweigend die projektweite
    # Hash-Integritaetsgarantie (AR3, `core/runtime.py`: content_sha256 ==
    # UTF-8-Hash des Wire-Textes). `is_reservation_booked` ist fail-closed: eine
    # fehlende/unlesbare `lab.status.json` propagiert HIER, bevor der Record
    # mutiert wird (keine Zustandsaenderung bei unklarer Buchungsautoritaet).
    if is_reservation_booked(run_dir, request_id):
        # K (RECOVERY_REVIEW §5/N08 "geaenderte Versand-/Billingbasis vor
        # sent konsistent buchen"): die oben beschriebene eingefrorene
        # Basis (`reserved_usd`/`dollar_billed`, wie VOR diesem Record-
        # Write bereits gebucht) bleibt fuer den unveraenderten Fall
        # richtig. Zwei bestellte Restfaelle bleiben sonst offen, wenn der
        # frische Caller jetzt (a) eine GROESSERE Reserve und/oder (b) eine
        # geaenderte Billingklasse (False->True) einreicht: (a) die neue
        # Mehrverpflichtung wuerde vor Versand nie gebucht, Ausgang bleibt
        # unbekannt -> Gesamtverpflichtung bliebe bei der alten (niedrigeren)
        # Buchung haengen; (b) `finish_received` ignoriert ein tatsaechliches
        # `usage.usd` spaeter wegen des alten `dollar_billed=False`-Markers.
        # FIX: nur wenn die NEUE Buchungsbasis tatsaechlich hoeher ist als
        # die bereits gebuchte, wird GENAU die Differenz VOR dem `sent`-
        # Marker idempotent nachgebucht -- ueber einen EIGENEN
        # `once_request_id` (kollidiert nicht mit der bereits angewandten
        # `request_id`-Buchung oben, dedupliziert sich selbst bei einem
        # Retry NACH dieser Nachbuchung, VOR dem folgenden Write). `reserved_
        # usd`/`dollar_billed` werden dann auf die NEUE Basis aktualisiert,
        # damit `finish_received`/`settle_received` ihr Delta gegen die
        # tatsaechlich volle Verpflichtung rechnen. Eine gleiche oder
        # niedrigere neue Basis bleibt unveraendert eingefroren (keine
        # pauschale Unveraenderlichkeitsforderung, aber auch kein Abbuchen).
        # K (PR #3317-Nachzug r2, RECOVERY_REVIEW.md §3 "feste Topup-ID
        # verliert die zweite geaenderte Buchungsbasis"): die Nachbuchung
        # rechnet gegen den KUMULATIV in `lab.status.json` festgehaltenen
        # gebuchten Betrag (`booked_reservation_amount`, crashfest), NICHT
        # gegen die ggf. nach einem Crash veraltete `reserved_usd` des
        # Records. Der `once_request_id` wird nach der ZIELbasis gekeyt
        # (`:rebook-topup:<ziel>`), damit eine zweite, hoehere Basis nach
        # einem Crash ihre noch fehlende Differenz tatsaechlich nachbucht
        # (die alte feste ID blockierte jede weitere Differenz) und ein
        # echter Retry DERSELBEN Zielbasis idempotent bleibt. `count_turn=
        # False`: eine reine Geldkorrektur ist kein neuer Modellversuch.
        # `reservation_booked_usd` wird ATOMAR mit der Buchung auf die neue
        # Zielbasis gehoben -- so entsteht nach jedem Crash nur die noch
        # fehlende Verpflichtung und der Record behauptet keine ungebookte
        # Basis. Rueckwaertskompatibel: fehlt der Statusbetrag (Altrecord vor
        # diesem Feld), faellt der Vergleich auf den record-basierten Stand
        # zurueck.
        status_booked_usd = booked_reservation_amount(run_dir, request_id)
        old_dollar_billed = record.get("dollar_billed", True)
        old_reserved_usd = record.get("reserved_usd")
        record_old_booked_usd = old_reserved_usd if old_dollar_billed else 0.0
        if status_booked_usd is not None:
            old_booked_usd = status_booked_usd
        else:
            old_booked_usd = record_old_booked_usd
        new_booked_usd = reserved_usd if dollar_billed else 0.0
        if (
            old_booked_usd is not None and new_booked_usd is not None
            and new_booked_usd > old_booked_usd
        ):
            record_turn_usage(
                run_dir, 0.0, new_booked_usd - old_booked_usd, require_authority=True,
                once_request_id=f"{request_id}:rebook-topup:{new_booked_usd!r}",
                count_turn=False,
                booked_reservation_id=request_id, booked_reservation_usd=new_booked_usd,
            )
            committed_usd = new_booked_usd
        else:
            # Gleiche/niedrigere neue Basis bleibt eingefroren (kein Abbuchen);
            # die bereits gebuchte, crashfeste Basis bleibt die Verpflichtung.
            committed_usd = old_booked_usd
        # Der Record behauptet GENAU die (crashfest) gebuchte Basis -- nie mehr
        # (keine ungebookte Basis nach einem Crash im Up-Booking), nie weniger
        # (sonst unterschlueg `finish_received`/`settle_received` den bereits
        # gebuchten Betrag beim Delta gegen `reserved_usd`). Nur fuer die
        # dollarbepflichtete Rolle -- eine Nicht-Dollarrolle bucht immer 0.0
        # und behaelt ihre deskriptive `reserved_usd`/`dollar_billed`
        # unveraendert (keine erfundene Dollarabrechnung, G2b).
        if dollar_billed and committed_usd is not None:
            record["reserved_usd"] = committed_usd
            record["dollar_billed"] = True
        content = content or ""
        record["content_chars"] = len(content)
        record["content_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
        record["route"] = route
        record["output_limit_tokens"] = output_limit_tokens
        record["state"] = "sent"
        record["sent_ts"] = time.time()
        _write_request(run_dir, request_id, record)
        return
    content = content or ""
    record["content_chars"] = len(content)
    record["content_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    record["reserved_usd"] = reserved_usd
    record["route"] = route
    record["output_limit_tokens"] = output_limit_tokens
    record["dollar_billed"] = dollar_billed
    _write_request(run_dir, request_id, record)
    booked_usd = reserved_usd if dollar_billed else 0.0
    # K (PR #3317-Nachzug r2, RECOVERY_REVIEW.md §3): erstmalige Buchung des
    # Folgers -- den gebuchten Betrag crashfest je request-id festhalten
    # (s. `begin`), damit eine spaetere Nachbuchung gegen den autoritativen
    # Stand statt gegen eine ggf. veraltete `reserved_usd` rechnet.
    record_turn_usage(
        run_dir, 0.0, booked_usd, require_authority=True, once_request_id=request_id,
        booked_reservation_id=request_id, booked_reservation_usd=booked_usd,
    )
    record["state"] = "sent"
    record["sent_ts"] = time.time()
    _write_request(run_dir, request_id, record)
