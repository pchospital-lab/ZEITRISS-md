#!/usr/bin/env python3
"""
mmo_sim/core/save_correction.py — persistente, request-gebundene,
wiederaufnehmbare SL-Korrekturschleife + realer Gruppenabschluss (R12-
Savegate, W44/W48-Slice, 01_AUFTRAG_SAVEGATE.md §B/§C/§D).

Generische Staging-/Repair-Orchestrierung (SCOPE.json semantic_constraints.
core: "generic staging/repair orchestration/request-bound calls; no
project-specific JSON field names in neutral storage; existing owner/run/
section/generation/claim/reflection guards preserved"). ZEITRISS-spezifisches
Wissen (Korrekturnachricht/Drift-Erkennung) kommt ausschliesslich aus
`domain.zeitriss.save_correction` (`save_correction_domain` unten) und aus
dem vom Aufrufer übergebenen `harvest_extractor` -- dieses Modul kennt
weder "wallet" noch "campaign.mode".

Zustandsmaschine je Korrekturdatensatz (01_AUFTRAG_SAVEGATE.md §C):

    validating -> correction_pending -> correction_received -> (erneut
    validating, bis akzeptiert ODER Budget erschöpft) -> adopted
                                                        -> hold / aborted

Persistiert unter `run_dir/save_corrections/<repair_key>.json`, atomar über
dieselbe Hilfsfunktion wie `lab.status.json`/`request_ledger`
(`core.admission._atomic_write_json` -- `request_ledger.py` importiert sie
bereits genauso, `admission.py` bleibt dabei unverändert/byteggleich). Der
Versuchszähler (`attempts_used`) wird VOR jedem Versand erhöht+persistiert
("jede gesendete Nachricht zählt, auch ohne passende Antwort") und NIE aus
einem neuen Kandidaten-/Originalhash auf 0 zurückgesetzt -- `load_or_init_
record` gibt einen bereits vorhandenen Datensatz UNVERÄNDERT zurück
(restart-fest, s. `repair_key`-Ableitung in `domain.zeitriss.save_correction`).

Der eigentliche Versand (`send_correction_turn`) ist EXAKT derselbe
Requestweg wie jeder andere Modellschritt (`core.creation_service.
run_admitted_creation_dialog`-Muster): Admission-Gate frisch von Platte,
body-basierte Reservierung, `request_ledger.begin`/`finish_received`/
`finish_error`, UND die bestehende crash-sichere Wiederaufnahme über
`find_durable_result`/`find_answered_without_text`/`settle_received` --
kein 'direkt Transport + später Journal'."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import recovery_ops
from . import request_ledger, store
from . import _save_correction_window as _window
from . import save_compatibility as save_compatibility_core
from ..adapters.base import ProviderQuotaPausedError
from .admission import _atomic_write_json, read_admission_block, reservation_for_wire_text
from ..domain.zeitriss import save_correction as save_correction_domain
from ..domain.zeitriss import save_compatibility as save_compatibility_domain

STATE_VALIDATING = "validating"
STATE_CORRECTION_PENDING = "correction_pending"
STATE_CORRECTION_RECEIVED = "correction_received"
STATE_ADOPTED = "adopted"
STATE_HOLD = "hold"
STATE_ABORTED = "aborted"
# R12-W73 (01_AUFTRAG_SAVEGATE.md §C/§D-Nachzug, Invarianten 1/3/4/5):
# NICHT terminal -- s. `mark_window_paused` unten/Modul-Helfer
# `_save_correction_window.py`. Ein NACHWEISLICH unversandter Deadline-vor-
# Versand-Block (`admission_blocked:` + exakter Wall-Clock-Marker, Slot
# ohne JEDEN Ledger-Datensatz) landet hier statt in `STATE_HOLD` -- derselbe
# Slot (`attempts_used` unveraendert) wird beim naechsten Aufruf regulaer
# erneut versucht, OHNE `STATE_VALIDATING`/`begin_attempt` (kein Inkrement).
STATE_WINDOW_PAUSED = "window_paused"

ROLE_CREATION = save_correction_domain.ROLE_CREATION
ROLE_GROUP = save_correction_domain.ROLE_GROUP
MAX_ADDITIONAL_REQUESTS = save_correction_domain.MAX_ADDITIONAL_REQUESTS


# ─────────────────────────── Persistenz (Zustand/Zähler) ───────────────────


def _records_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "save_corrections"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _record_path(run_dir: str | Path, repair_key: str) -> Path:
    safe = repair_key.replace("/", "_")
    return _records_dir(run_dir) / f"{safe}.json"


def load_record(run_dir: str | Path, repair_key: str) -> dict | None:
    p = _record_path(run_dir, repair_key)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _write_record(run_dir: str | Path, repair_key: str, data: dict) -> None:
    _atomic_write_json(_record_path(run_dir, repair_key), data)


#: R12-W74 (F02 Entwurfs-/Original-Bindung): Sentinel fuer "dieser optionale
#: Originalentwurf-Parameter wurde vom Aufrufer GAR NICHT angegeben" --
#: unterscheidbar von einem bewusst uebergebenen `None` (z.B. der
#: Mehrdeutigkeitskonflikt-Zweig in `pursue_single_figure_correction`, der
#: `current_block=None` fuehrt und das GENAU SO persistiert haben will).
_UNSET_ORIGINAL_BLOCK = object()

#: R12-W75 (F02-PROVENANCE): Sentinel fuer "die positive Legacy-Herkunfts-
#: pruefung in `_verify_legacy_provenance` hat ABGELEHNT" -- unterscheidbar
#: von einem tatsaechlich verifizierten Baseline-Block (immer ein `dict`,
#: NIE `None`: ohne einen wohldefinierten Block gibt es keine Drift-
#: Baseline, s. dort).
_LEGACY_PROVENANCE_REJECTED = object()


def load_or_init_record(
    run_dir: str | Path, repair_key: str, *, persona_key: str, char_id: str, operation_key: str,
    table_id: str | None = None, section_id: str | None = None, generation: int | None = None,
    errors: list[str] | None = None, original_block: dict | None = None,
) -> dict:
    """Restart-fest (01_AUFTRAG_SAVEGATE.md §C): existiert für `repair_key`
    bereits ein Datensatz, wird er UNVERÄNDERT zurückgegeben -- insbesondere
    bleibt `attempts_used` erhalten, unabhängig davon, mit welchem
    (ggf. neuen) Kandidaten/Originalhash dieser Aufruf erfolgt. NUR beim
    allerersten Aufruf für `repair_key` wird ein frischer Datensatz
    (`attempts_used=0`) angelegt+persistiert.

    R12-W74 (F02 Entwurfs-/Original-Bindung): `original_block` (additiv,
    Default `None`, bestehende direkte Aufrufer -- z.B. `test_r12_window_
    hold_*.py` -- bleiben unveraendert) wird NUR bei dieser ALLERERSTEN
    Anlage als `"bound_block"` mitpersistiert -- der dauerhaft an diesen
    Pausenrecord gebundene Originalentwurf, gegen den ein spaeterer Resume
    Drift misst, STATT gegen einen (evtl. ausgetauschten) aktuellen
    Caller-Kandidaten (s. `pursue_single_figure_correction`). Ein bereits
    vorhandener Datensatz behaelt sein `bound_block` unveraendert (dieselbe
    Restart-Festigkeit wie `attempts_used`)."""
    existing = load_record(run_dir, repair_key)
    if existing is not None:
        return existing
    data = {
        "repair_key": repair_key, "persona_key": persona_key, "char_id": char_id,
        "operation_key": operation_key, "table_id": table_id, "section_id": section_id,
        "generation": generation, "errors": list(errors or []),
        "attempts_used": 0, "state": STATE_VALIDATING,
        "created_ts": time.time(), "updated_ts": time.time(),
        "last_request_id": None, "last_reason": None,
        "bound_block": original_block,
    }
    _write_record(run_dir, repair_key, data)
    return data


def attempts_exhausted(record: dict, max_attempts: int = MAX_ADDITIONAL_REQUESTS) -> bool:
    return record.get("attempts_used", 0) >= max_attempts


def begin_attempt(run_dir: str | Path, repair_key: str, *, original_block=_UNSET_ORIGINAL_BLOCK) -> dict:
    """Erhöht den Versuchszähler SOFORT und persistiert ihn, BEVOR die
    Nachricht tatsächlich gesendet wird -- "jede gesendete Nachricht zählt,
    auch ohne passende Antwort" (01_AUFTRAG_SAVEGATE.md §C). Muss NACH
    `load_or_init_record` für denselben `repair_key` aufgerufen worden sein.

    R12-W74 (F02 Entwurfs-/Original-Bindung): `original_block` (additiv,
    Default der private `_UNSET_ORIGINAL_BLOCK`-Sentinel -- bestehende
    direkte Aufrufer, z.B. `test_r12_window_hold_*.py`, lassen `bound_block`
    dadurch unveraendert) stempelt bei ANGABE (auch `None`, der
    Mehrdeutigkeitskonflikt-Fall) den fuer DIESEN NEUEN Versuchs-Slot
    gueltigen Baseline-Entwurf durabel in den Datensatz -- ueberlebt einen
    Crash GENAU zwischen diesem Aufruf und der Antwortauswertung, sodass ein
    Resume (`pursue_single_figure_correction`) denselben Baseline-Entwurf
    wiederfindet, STATT den (evtl. zwischenzeitlich ausgetauschten)
    `candidate_block`-Parameter eines spaeteren Aufrufs zu uebernehmen."""
    record = load_record(run_dir, repair_key)
    if record is None:
        raise ValueError(f"kein Korrekturdatensatz für repair_key={repair_key!r} -- load_or_init_record zuerst.")
    record = dict(record)
    record["attempts_used"] = record.get("attempts_used", 0) + 1
    record["state"] = STATE_CORRECTION_PENDING
    if original_block is not _UNSET_ORIGINAL_BLOCK:
        record["bound_block"] = original_block
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


def record_correction_received(run_dir: str | Path, repair_key: str, *, request_id: str | None) -> dict:
    record = dict(load_record(run_dir, repair_key))
    record["state"] = STATE_CORRECTION_RECEIVED
    record["last_request_id"] = request_id
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


def mark_adopted(run_dir: str | Path, repair_key: str, *, adopted_block: dict | None = None) -> dict:
    """`adopted_block`, falls uebergeben, wird ATOMAR zusammen mit
    `state="adopted"` als neues internes Corrector-Metadatum persistiert
    (W53-SS7, 01_AUFTRAG_SAVEGATE.md §C-Bruecke "neue interne Corrector-
    Metadaten innerhalb der erlaubten save_correction-Mechanik sind
    zulaessig") -- ermoeglicht `pursue_group_save_correction`, einen bereits
    akzeptierten Block nach einem Absturz GENAU zwischen `_clear_open_round`
    und `store.complete_section` beim naechsten Aufruf aus DIESEM Datensatz
    zurueckzuspielen, statt ihn dauerhaft zu verlieren (s. dort)."""
    record = dict(load_record(run_dir, repair_key))
    record["state"] = STATE_ADOPTED
    if adopted_block is not None:
        record["adopted_block"] = adopted_block
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


def public_hold_reason(reason: str | None) -> str:
    """G03/SC15/SC17 (W54-Fix): oeffentliche, Terminal-/`print_fn`-sichere
    Kategorie fuer ein `CorrectionOutcome.reason`/`SendOutcome.reason` --
    NIE der rohe Text (kann `str(exc)` einer Fremdantwort/Transport-
    ausnahme sein, s. `send_correction_turn` unten). Reiner Durchreicher zu
    `domain.zeitriss.save_correction.public_hold_reason` (ZEITRISS-
    unabhaengige Kategorien waeren denkbar, aber die vorhandene
    Praefixkonvention -- `transport_error:`/`admission_blocked:`/... --
    gehoert bereits der Domainschicht, s. dort fuer die volle
    Kategorienliste/Begruendung)."""
    return save_correction_domain.public_hold_reason(reason)


def mark_hold(run_dir: str | Path, repair_key: str, *, reason: str) -> dict:
    record = dict(load_record(run_dir, repair_key))
    record["state"] = STATE_HOLD
    record["last_reason"] = reason
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


def mark_window_paused(run_dir: str | Path, repair_key: str, *, reason: str) -> dict:
    """R12-W73 (Invarianten 1/3/4/5): wie `mark_hold`, aber NICHT terminal --
    markiert einen NACHWEISLICH unversandten Deadline-vor-Versand-Block als
    regulaer im GLEICHEN Slot fortsetzbar (`attempts_used`/`last_request_id`
    bleiben dabei UNVERAENDERT, s. Aufrufer in `pursue_single_figure_
    correction`/`pursue_group_save_correction`). Idempotent: ist der
    Datensatz bereits `STATE_WINDOW_PAUSED` mit GENAU demselben `reason`,
    erfolgt KEIN weiterer Schreibzugriff (Invariante 5 -- wiederholte
    Aufrufe bei weiter geschlossenem Fenster duerfen NACH der ersten
    Migration keine ueberfluessigen Metadaten-Writes mehr ausloesen).

    R12-W74 (F02 "Keine spekulative Migration vor Admission"): dieselbe
    Idempotenz gilt jetzt AUCH, wenn der Datensatz bereits `STATE_HOLD` mit
    GENAU demselben `reason` ist -- ein bereits VOR diesem Modul
    gespeicherter Legacy-HOLD, dessen Admissionfenster bei einem erneuten
    Resume-Versuch NACHWEISLICH WEITERHIN geschlossen ist, bleibt dadurch
    `PRE==POST` bytegleich (kein Label-Wechsel `hold` -> `window_paused`
    allein aus Anlass der Pruefung). Der Datensatz transitioniert erst bei
    tatsaechlich zulaessiger Wiederaufnahme -- `pursue_single_figure_
    correction`s HOLD/WINDOW_PAUSED-Zweig ruft diese Funktion NICHT mehr
    spekulativ VOR einem echten `send_correction_turn`-Versuch auf, sondern
    nur noch aus dessen bestehendem `outcome.blocked`-Zweig, NACH einer
    frischen Admission-Pruefung.

    R12-W75 (F02-UNCHANGED-HOLD-Fix): die Idempotenz von oben verglich
    bisher NUR den exakten `reason`-TEXT -- ein weiterer Resume-Versuch
    GENAU derselben bereits HOLD/WINDOW_PAUSED-Identitaet, bei dem die
    Admission-Pruefung einen ANDEREN, aber ebenfalls abgelaufenen
    Deadlinewert liefert (anderer Text, z.B. ein frischer `time.time()`-
    Stempel in der Fehlermeldung), erfuellte die Textgleichheit NICHT und
    wurde faelschlich als neue Migration geschrieben (`hold`->
    `window_paused`, `last_reason` ueberschrieben) -- obwohl die Admission
    WEITERHIN geschlossen war und GAR KEIN neuer, in DIESEM Aufruf frisch
    via `begin_attempt` eroeffneter Slot vorliegt. Ein bereits HOLD/
    WINDOW_PAUSED-Datensatz, dessen GESPEICHERTER `last_reason` SELBST
    bereits ein Deadline-vor-Versand-Grund ist (`_window.
    is_pre_send_deadline_reason` -- das ist fuer JEDEN Datensatz, der diese
    Funktion ueberhaupt mit `state in (HOLD, WINDOW_PAUSED)` erreicht,
    GARANTIERT der Fall, s. `pursue_single_figure_correction`s/`pursue_
    group_save_correction`s `is_resumable_pre_send_pause`/`is_pre_send_
    deadline_reason`-Vorpruefung), bleibt deshalb JETZT bytegleich
    (`PRE==POST`), UNABHAENGIG vom exakten Deadlinewert im neuen `reason`-
    Text -- NUR ein Datensatz, der bei diesem Aufruf NOCH NICHT HOLD/
    WINDOW_PAUSED war (ein genuin frischer, soeben via `begin_attempt`
    eroeffneter Slot), darf weiterhin regulaer migrieren."""
    record = dict(load_record(run_dir, repair_key))
    if record["state"] in (STATE_WINDOW_PAUSED, STATE_HOLD) and (
        record.get("last_reason") == reason or _window.is_pre_send_deadline_reason(record.get("last_reason"))
    ):
        return record
    record["state"] = STATE_WINDOW_PAUSED
    record["last_reason"] = reason
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


def _reset_for_next_attempt(
    run_dir: str | Path, repair_key: str, *, errors: list[str], original_block=_UNSET_ORIGINAL_BLOCK,
) -> dict:
    """Markiert den aktuellen Versuchs-Slot als vollstaendig ausgewertet
    (nicht akzeptiert, keine Drift) -- `state` kehrt auf `validating`
    zurueck, DAS ist das Signal fuer die naechste Schleifenrunde, einen NEUEN
    Slot zu eroeffnen (s. `pursue_single_figure_correction`). `attempts_used`
    bleibt dabei unveraendert (wird NUR von `begin_attempt` erhoeht).

    R12-W74 (F02 Entwurfs-/Original-Bindung): `original_block` (additiv,
    Default der private `_UNSET_ORIGINAL_BLOCK`-Sentinel, bestehende
    Aufrufer -- z.B. der Gruppenpfad, der seine eigene Bindung bereits ueber
    den `_open_round`-Marker haelt -- bleiben unveraendert) stempelt bei
    ANGABE den NEUEN, fuer den naechsten Versuch gueltigen Baseline-Entwurf
    durabel nach (derselbe Mechanismus wie `begin_attempt`s gleichnamiger
    Parameter) -- der Einzelfigurpfad ruft dies mit dem jeweils aktuellen
    `current_block` auf, damit ein Crash VOR dem naechsten `begin_attempt`
    denselben Baseline-Entwurf fuer einen spaeteren Resume durabel
    wiederfindet."""
    record = dict(load_record(run_dir, repair_key))
    record["state"] = STATE_VALIDATING
    record["errors"] = list(errors)
    if original_block is not _UNSET_ORIGINAL_BLOCK:
        record["bound_block"] = original_block
    record["updated_ts"] = time.time()
    _write_record(run_dir, repair_key, record)
    return record


# ─────────────────────────── Request-gebundener Versand ────────────────────


@dataclass
class SendOutcome:
    blocked: bool
    text: str | None = None
    request_id: str | None = None
    reason: str | None = None


def send_correction_turn(
    run_dir: str | Path, *, role: str, table_id: str | None, section_id: str | None,
    participant: str, turn_idx: int, outgoing_text: str, gm_transport, table=None,
    output_limit_tokens_override: float | None = None,
) -> SendOutcome:
    """EIN request-gebundener Korrektur-Einzelversand -- derselbe Weg wie
    jeder andere Modellschritt (s. Moduldocstring). `table`, falls übergeben
    (Gruppenabschluss), leitet den tatsächlichen Transport-Call über
    `store.submit_to_sl` (Leader-only-/Tisch-geschlossen-/Lock-Prüfung,
    schreibt denselben `sl_log` fort -- "dieselbe SL-Session/denselben
    historischen Chatkontext"). Ohne `table` (Erschaffungsdialog, noch kein
    Tisch) wird `gm_transport.turn(...)` direkt aufgerufen, exakt wie
    `core.creation_service.run_admitted_creation_dialog`.

    FIX2 (R4-Rundenabschluss, 01-PRODUCT-REVIEW.md "Die tatsaechliche
    Nachforderung muss in die Ausgabe passen"): `output_limit_tokens_
    override`, additiv und OPTIONAL (Default `None`), ersetzt -- NUR fuer
    GENAU DIESEN Versand -- das sonst von `gm_transport.output_limit_
    tokens` gelesene Limit (`pursue_group_save_correction` skaliert es mit
    der Mitgliederzahl der aktuellen Runde). `None` (Default, JEDER
    bestehende Aufrufer inkl. `pursue_single_figure_correction`) belaesst
    das bisherige Verhalten vollstaendig unveraendert."""
    recovered = request_ledger.find_durable_result(
        run_dir, table_id=table_id, section_id=section_id, role=role,
        turn_idx=turn_idx, participant=participant,
    )
    if recovered is not None:
        if recovered.get("state") == "received":
            recovered = request_ledger.settle_received(run_dir, recovered)
            if recovered.get("state") != "accounted":
                return SendOutcome(blocked=True, reason="altformat_unresolved_received_seconds")
        return SendOutcome(blocked=False, text=recovered["result_text"], request_id=recovered["id"])
    answered_without_text = request_ledger.find_answered_without_text(
        run_dir, table_id=table_id, section_id=section_id, role=role,
        turn_idx=turn_idx, participant=participant,
    )
    if answered_without_text is not None:
        return SendOutcome(blocked=True, reason="altformat_unresolved_missing_result_text")

    gm_output_limit = (
        output_limit_tokens_override
        if output_limit_tokens_override is not None
        else getattr(gm_transport, "output_limit_tokens", None)
    )
    gm_route = getattr(gm_transport, "base_url", None)
    reserved = reservation_for_wire_text(outgoing_text, output_limit_tokens=gm_output_limit)
    blocked, reason = read_admission_block(
        run_dir, reserved_usd=reserved, output_bound_known=(gm_output_limit is not None), route=gm_route,
    )
    if blocked:
        return SendOutcome(blocked=True, reason=f"admission_blocked:{reason}")

    try:
        request_id = request_ledger.begin(
            run_dir, role=role, content=outgoing_text, reserved_usd=reserved, route=gm_route,
            output_limit_tokens=gm_output_limit, turn_idx=turn_idx, participant=participant,
            table_id=table_id, section_id=section_id,
        )
    except request_ledger.OpenReservationExistsError as exc:
        # SC10 (01_AUFTRAG_SAVEGATE.md §D): fuer GENAU diese Operationsidentitaet
        # existiert bereits ein offener (nicht abgeschlossener) Requestdatensatz
        # -- eine unklare sent-Ausfuehrung (Crash zwischen Versand und
        # Antwort/Fehlerabschluss). NIE retryen/neu nummerieren -- kontrolliert
        # blockiert melden, der Aufrufer haelt HOLD (alte gueltige Saves bleiben
        # unangetastet), statt einen zweiten Request fuer denselben Slot zu
        # versenden oder stillschweigend auf den naechsten Slot zu springen.
        return SendOutcome(blocked=True, reason=f"unclear_sent_in_flight:{exc}")
    t0 = time.monotonic()
    try:
        if table is not None:
            if gm_output_limit is not None:
                result = store.submit_to_sl(
                    table, participant, gm_transport, turn_idx, outgoing_text,
                    output_limit_tokens=gm_output_limit,
                )
            else:
                result = store.submit_to_sl(table, participant, gm_transport, turn_idx, outgoing_text)
        elif gm_output_limit is not None:
            result = gm_transport.turn(turn_idx, outgoing_text, output_limit_tokens=gm_output_limit)
        else:
            result = gm_transport.turn(turn_idx, outgoing_text)
    except ProviderQuotaPausedError as exc:
        # P2 (R4-Rundenabschluss): eine getypte Kontingent-/Budgetpause ist
        # HIER bereits vollstaendig verbucht (`finish_error` bucht die
        # Reservierung unveraendert nach `accounted`, s. `request_ledger.
        # finish_error`-Docstring) -- aber SEMANTISCH keine unklare
        # Versandsituation und kein gewoehnlicher Transportdefekt. Eigener,
        # getypt erkannter Reason-Praefix (`quota_paused:`, NICHT
        # `transport_error:`) laesst den Aufrufer (`pursue_group_save_
        # correction`) diesen Fall VON der generischen terminalen
        # Behandlung unterscheiden, ohne `request_ledger.py` selbst
        # anzufassen.
        request_ledger.finish_error(run_dir, request_id, error=exc, seconds=time.monotonic() - t0)
        return SendOutcome(blocked=True, reason=f"quota_paused:{exc}")
    except Exception as exc:
        request_ledger.finish_error(run_dir, request_id, error=exc, seconds=time.monotonic() - t0)
        return SendOutcome(blocked=True, reason=f"transport_error:{exc}")
    text = result.get("content", "")
    request_ledger.finish_received(
        run_dir, request_id, usage=result.get("usage"), seconds=time.monotonic() - t0, result_text=text,
    )
    return SendOutcome(blocked=False, text=text, request_id=request_id)


# ─────────────────────── Einzelfigur-Korrektur (Erschaffung) ───────────────


@dataclass
class CorrectionOutcome:
    status: str  # "accepted" | "hold"
    block: dict | None = None
    reason: str = ""
    drift: list = field(default_factory=list)
    # R-SCF-A (02_SAVEVERTRAG.md §D, additiv/OPTIONAL -- Default `None`
    # aendert KEIN bestehendes Aufruferverhalten/keine Dataclass-Gleichheit
    # gegen einen Vergleichswert ohne dieses Feld): Pfad des versionierten
    # Kompatibilitaetsumschlags, NUR gesetzt, wenn das additive Re-Export-
    # Budget dieses Laufs tatsaechlich erschoepft wurde (s.
    # `_write_compat_export_on_exhaustion` unten) -- "Nach drei erfolglosen
    # Neuausgaben: weiter, aber nicht luegen" (02.D). `None` bei jedem
    # anderen HOLD-Grund (Drift/Blockade/Fensterpause/Mehrdeutigkeit) --
    # diese sind KEIN Schema-/Kompatibilitaetsfehler.
    compat_export_path: str | None = None


def _verify_legacy_provenance(
    run_dir: str | Path, *, record: dict, participant_id: str, expected_chrononaut_id: str,
    table_id: str | None, section_id: str | None, original_request_id: str | None,
    original_evidence: dict | None, original_role: str | None, original_turn_idx: int | None,
    original_generation: int | None,
):
    """R12-W75/W76 (F02-PROVENANCE): POSITIVE Herkunftsbindung fuer einen
    Datensatz OHNE konkret gebundenen Originalentwurf -- entweder ein echter
    VOR diesem Fix geschriebener Legacy-HOLD-Datensatz, der GAR KEIN
    `"bound_block"` traegt, ODER (R12-W76) ein Datensatz MIT dem Schluessel,
    dessen Wert `None` ist, FALLS der Aufrufer dafuer ueberhaupt eine
    Herkunftsbehauptung mitbringt (s. Aufrufer `needs_legacy_verification`).
    Ein Datensatz mit einem KONKRETEN `dict`-`"bound_block"` geht NIE hier
    durch. Liefert den verifizierten Original-Entwurf (`dict`, die Drift-Baseline)
    NUR, wenn ALLE der folgenden Bedingungen zutreffen -- sonst den
    `_LEGACY_PROVENANCE_REJECTED`-Sentinel (der Aufrufer haelt dann
    kontrolliert HOLD, VOR jedem Transport/jeder Adoption):

      1. `original_request_id`/`original_evidence` wurden ueberhaupt
         uebergeben (beide, nicht nur eines).
      2. `original_request_id` loest tatsaechlich auf einen vorhandenen
         Requestledger-Datensatz auf (`request_ledger.load_request`).
      2a. R12-W76 (R02-Nachzug): dieser Datensatz ist ein durabler ERFOLG --
          dasselbe Praedikat wie `request_ledger.find_durable_result`/
          `request_ledger.py:439-441` (`state in ("received", "accounted")`
          UND `error is None` UND `result_text is not None`). Ein passender
          Text MIT gesetztem `error` (oder ein noch offener/unklarer
          Zustand) ist KEINE erfolgreiche Originalantwort.
      3. Dieser Datensatz gehoert NACHWEISLICH zur erwarteten
         Originaloperation -- `participant`/`table_id`/`section_id` MUESSEN
         mit der aktuellen Calleridentitaet uebereinstimmen; `role`/
         `turn_idx` MUESSEN mit `original_role`/`original_turn_idx`
         uebereinstimmen, FALLS der Aufrufer sie mitgibt (additiv/optional --
         ein Aufrufer ohne diese Felder bekommt dafuer keine zusaetzliche
         Pruefung, s. Funktionssignatur `pursue_single_figure_correction`);
         `generation` wird GENAUSO nur verglichen, wenn sowohl
         `original_generation` ALS AUCH der gespeicherte Korrekturdatensatz
         selbst (`record.get("generation")`) tatsaechlich einen Wert tragen
         ("soweit tatsaechlich vorhanden" -- kein Requestledger-Datensatz
         kennt ueberhaupt ein `generation`-Feld).
      4. Die TATSAECHLICH gespeicherte Antwort dieses Requests
         (`result_text`) enthaelt -- ueber denselben strikten Domainreader
         wie jede reguläre Korrekturantwort (`save_correction_domain.
         extract_checked_single`) -- GENAU EINEN eindeutigen Block fuer
         `expected_chrononaut_id` (kein fehlender, kein mehrdeutiger Fund).
      5. Dieser extrahierte Block ist BYTEGLEICH mit dem vom Aufrufer
         uebergebenen `original_evidence` -- NUR dann ist `original_evidence`
         tatsaechlich die historische Antwort dieses Requests und nicht ein
         (versehentlich oder absichtlich) ausgetauschter aktueller Kandidat.

    C36s verworfene Auslegung ("fail-closed = keine Drift-Annahme erfinden,
    nicht Resume verweigern") wird hier bewusst NICHT mehr angewandt -- eine
    fehlende/fremde/beschaedigte/widersprüchliche Herkunft fuehrt NICHT mehr
    zu `current_block=None` (Drift-Pruefung uebersprungen, jede Antwort
    durchgelassen), sondern zu einem kontrollierten HOLD VOR jedem Transport/
    jeder Adoption (s. Aufrufer)."""
    if original_request_id is None or original_evidence is None:
        return _LEGACY_PROVENANCE_REJECTED
    original_request = request_ledger.load_request(run_dir, original_request_id)
    if original_request is None:
        return _LEGACY_PROVENANCE_REJECTED
    # R12-W76 (F02-PROVENANCE-Nachzug/R02): dieselbe Durable-Erfolgspruefung
    # wie `request_ledger.find_durable_result` (state in received/accounted,
    # `error is None`, `result_text` gesetzt) -- ein passender `result_text`
    # MIT gesetztem `error` (oder ein noch nicht abgeschlossener/unklarer
    # Zustand) ist KEINE erfolgreiche Originalantwort und legitimiert keine
    # Herkunft, auch wenn Identitaet/Text andernfalls passen wuerden.
    if (
        original_request.get("state") not in ("received", "accounted")
        or original_request.get("error") is not None
        or original_request.get("result_text") is None
    ):
        return _LEGACY_PROVENANCE_REJECTED
    if (
        original_request.get("participant") != participant_id
        or original_request.get("table_id") != table_id
        or original_request.get("section_id") != section_id
    ):
        return _LEGACY_PROVENANCE_REJECTED
    if original_role is not None and original_request.get("role") != original_role:
        return _LEGACY_PROVENANCE_REJECTED
    if original_turn_idx is not None and original_request.get("turn_idx") != original_turn_idx:
        return _LEGACY_PROVENANCE_REJECTED
    # R12-W77 (F02-GENERATION-Fix, 01_BINDUNGSERHALT.md §C, L08-GENERATION):
    # W76 verglich hier mit `!=` (Python-Wertgleichheit) -- `1 == True`, eine
    # einseitig fehlende Gegenseite schaltete die ganze Pruefung automatisch
    # ab (GENERALREVIEW.md §5: `(1, True)`/`(True, 1)` wurden akzeptiert,
    # ein Einzelwert wurde nie gefordert). Fix: `None`/`None` (generationloser
    # Weg) bleibt unveraendert korrekt; TRAEGT irgendeine Seite tatsaechlich
    # einen Wert, wird die NOTWENDIGE Gegenseite jetzt gefordert (einseitig
    # vorhanden -> HOLD, KEIN erfundenes Requestledgerfeld) UND beide Seiten
    # muessen BEIDE denselben Typ (bool ausdruecklich NICHT int, keine
    # stille Typkonvertierung -- float/string/int-Widerspruch -> HOLD) UND
    # denselben Wert tragen.
    record_generation = record.get("generation")
    if original_generation is not None or record_generation is not None:
        if original_generation is None or record_generation is None:
            return _LEGACY_PROVENANCE_REJECTED
        if type(original_generation) is not type(record_generation):
            return _LEGACY_PROVENANCE_REJECTED
        if original_generation != record_generation:
            return _LEGACY_PROVENANCE_REJECTED
    extracted, conflicts = save_correction_domain.extract_checked_single(
        original_request.get("result_text") or "", expected_chrononaut_id,
    )
    if extracted is None or conflicts:
        return _LEGACY_PROVENANCE_REJECTED
    if extracted != original_evidence:
        return _LEGACY_PROVENANCE_REJECTED
    return original_evidence


def _write_compat_export_on_exhaustion(
    run_dir: str | Path, *, repair_key: str, participant_id: str, char_id: str, role: str,
    table_id: str | None, section_id: str | None, best_view: dict | None, errors: list[str],
    reason: str,
) -> Path | None:
    """R-SCF-A (02_SAVEVERTRAG.md §D, additiv/zusaetzlich -- schliesst die
    in GAPS.md/review/INTAKE.md dokumentierte Luecke "Compat-Kernfunktionen
    werden nur aus Tests gerufen, nicht aus normalen Consumern"): wird NUR
    an den bereits bestehenden, terminalen Re-Export-Budget-Erschoepfungs-
    HOLD-Stellen unten aufgerufen (NICHT bei Drift/Blockade/Fensterpause --
    02.D beschreibt ausdruecklich den Fall "reine Schema-/Kompatibilitaets-
    fehler"). Reiner additiver Seiteneffekt (schreibt eine NEUE versionierte
    Datei, s. `core.save_compatibility.build_and_write_compat_export`) --
    AENDERT NICHT die bestehende Rueckgabe/den bestehenden Kontrollfluss
    dieser Datei, nur `CorrectionOutcome.compat_export_path` (additiv,
    Default `None`) traegt das Ergebnis weiter. Best-effort: ein Fehler beim
    Export (z.B. strukturell ungueltiges `best_view`) darf den bestehenden,
    bereits korrekten HOLD-Rueckgabepfad NICHT verdecken -- wird geschluckt,
    `None` zurueckgegeben (Aufrufer behandelt das wie "kein Export
    geschrieben", niemals wie ein zusaetzlicher Fehlerzustand)."""
    try:
        _envelope, path = save_compatibility_core.build_and_write_compat_export(
            run_dir, repair_key=repair_key, char_id=char_id, participant_id=participant_id,
            operation_key=role, table_id=table_id, section_id=section_id,
            best_view=best_view, last_valid=None, progress_evidence=[], conflicts=[],
            extensions={}, errors=list(errors or []),
            provenance={"source": "core.save_correction", "reason": reason},
            created_ts=time.time(),
        )
    except (ValueError, OSError):
        return None
    return path


def pursue_single_figure_correction(
    *, run_dir: str | Path, participant_id: str, expected_chrononaut_id: str, candidate_block: dict | None,
    gm_transport, role: str = ROLE_CREATION, table_id: str | None = None, section_id: str | None = None,
    max_attempts: int = MAX_ADDITIONAL_REQUESTS, emit=None, forced_conflicts: list | None = None,
    original_request_id: str | None = None, original_evidence: dict | None = None,
    original_role: str | None = None, original_turn_idx: int | None = None, original_generation: int | None = None,
    restrict_drift_to_core_identity: bool = False,
) -> CorrectionOutcome:
    """Treibt bis zu `max_attempts` zusätzliche SL-Ausgaben für EINE Figur
    (01_AUFTRAG_SAVEGATE.md §C) -- wiederaufnehmbar (Restart lädt denselben
    Datensatz über `creation_repair_key`, Zähler bleibt erhalten) und
    request-gebunden (`send_correction_turn`). Gibt `status="accepted"` mit
    dem final gültigen Block ODER `status="hold"` mit Begründung zurück --
    bei HOLD bleibt der zuletzt gültige (ältere) Stand des Aufrufers
    unangetastet (diese Funktion schreibt NIE einen Save, nur den eigenen
    Korrekturdatensatz).

    W51 (01_RESTAUFTRAG.md §3, Operator-/Terminalintegration): `emit`, analog
    zum bereits bestehenden `pursue_group_save_correction`-Parameter
    unten (gleiche Signatur `emit(kind: str, payload: dict)`), ist additiv
    und OPTIONAL (Default `None` -> No-op, exakt wie beim Gruppenpfad) --
    kein bestehender Aufrufer ohne `emit` aendert sein Verhalten. Reine
    Benachrichtigung ueber bereits vorhandene Zustandsuebergaenge (kein
    neuer Zustand, kein zusaetzlicher Versand); der Aufrufer (`core.
    creation_service.run_admitted_creation_dialog`) uebersetzt dies in
    `print_fn`-Text ('Speicherstand wird geprueft' / 'SL korrigiert Format,
    Versuch n/3') -- die bisher stumme Korrekturschleife wird dadurch fuer
    das Terminal (`ui/tui.py`, SCOPE.json semantic_constraints.ui 'pending
    save/correction status and controls') ehrlich sichtbar, OHNE eine neue
    Menuehierarchie oder einen neuen Store-Zustand.

    G02/SC06 (W54-Fix): `forced_conflicts`, additiv und OPTIONAL (Default
    `None` -> unveraendertes Verhalten jedes bestehenden Aufrufers), ist
    gesetzt, wenn der Aufrufer VOR diesem Aufruf bereits ueber
    `save_validation.extract_checked_single`/`find_duplicate_save_ids`
    erkannt hat, dass die Rohantwort mehrere Bloecke fuer
    `expected_chrononaut_id` mit ABWEICHENDEM Inhalt enthielt --
    `candidate_block` ist in diesem Fall `None` (KEIN Block darf als
    Kandidat gelten, 'darf NIE als einer der Bloecke erfolgreich
    uebernommen werden'), und die Ablehnung wird STATT der normalen
    Schema-/Bindungspruefung aus genau diesen Konflikten gebaut
    (`save_correction_domain.forced_conflict_acceptance`) -- die SL erhaelt
    dadurch die tatsaechliche Mehrdeutigkeitsmeldung statt eines
    generischen 'fehlender Block'-Textes.

    R12-W74/W75 (F02 Legacy-D-Herkunft): `original_request_id`/`original_
    evidence`/`original_role`/`original_turn_idx`/`original_generation`,
    ALLE additiv und OPTIONAL (Default `None` -> unveraendertes Verhalten
    jedes bestehenden Aufrufers, z.B. jeder direkte Testaufruf ohne diese
    Parameter). Dienen AUSSCHLIESSLICH als Rueckfall fuer einen bereits
    vorhandenen, echten `STATE_HOLD`-Datensatz, der VOR diesem Fix angelegt
    wurde und deshalb KEIN eigenes `"bound_block"` trägt (die Praesenz
    dieses Schluessels selbst entscheidet, NICHT eine Figuren-/ID-Liste).
    Der Aufrufer (`core.creation_service.run_admitted_creation_dialog`)
    uebergibt dafuer den `sl_request_id` des Onboarding-`pending_step` plus
    den dort zuletzt gespeicherten Originalentwurf, sowie (da die Korrektur-
    operation unter einer ANDEREN Operationsidentitaet laeuft als der
    urspruengliche Onboarding-Turn, s. `ROLE_CREATION` vs. `role=
    "creation_dialog"`) dessen eigenen `role`/`turn_idx` als
    `original_role`/`original_turn_idx`.

    R12-W75 (F02-PROVENANCE-Fix, C36s "fail-closed = keine Drift-Annahme
    erfinden statt Resume verweigern" AUSDRUECKLICH VERWORFEN): die blosse
    Existenz IRGENDEINES auflösbaren `original_request_id` legitimiert
    `original_evidence` NICHT mehr als Baseline. `_verify_legacy_provenance`
    (s. dort) verlangt eine POSITIVE Bindung -- der aufgeloeste Request MUSS
    zur erwarteten Originaloperation passen (Teilnehmer/Tisch/Abschnitt
    immer, Rolle/Turn/Generation soweit uebergeben) UND seine tatsaechlich
    gespeicherte Antwort MUSS -- ueber denselben Domainreader wie jede
    reguläre Korrekturantwort -- zu `expected_chrononaut_id` extrahiert
    BYTEGLEICH mit `original_evidence` sein. Fehlt die Herkunft, ist sie
    fremd/beschaedigt/mehrdeutig/widersprüchlich (getauschtes
    `original_evidence`), ist das Ergebnis `_LEGACY_PROVENANCE_REJECTED` --
    der Aufrufer haelt dann kontrolliert HOLD VOR jedem Transport/jeder
    Adoption (NICHT mehr `current_block=None` mit uebersprungener Drift-
    Pruefung). Der legitime Null-Tisch-/Neu-Figur-/Erstkandidat-Weg
    (`forced_conflicts`, `candidate_block=None` bei Erstanlage) bleibt davon
    UNBERUEHRT -- diese Pruefung greift, wenn der Schluessel GAR NICHT
    vorhanden ist (echter Legacy-Datensatz) ODER (R12-W76, F02-NULL-BINDING-
    Fix) wenn er vorhanden, aber `None` ist UND der Aufrufer dafuer
    UEBERHAUPT eine Herkunftsbehauptung mitbringt (`original_request_id`/
    `original_evidence`, mindestens eines gesetzt) -- bringt der Aufrufer
    GAR KEINE Behauptung mit (beide `None`, der normale Zustand fuer eine
    echte Erstanlage/Mehrdeutigkeit), bleibt `bound_block=None` unveraendert
    `current_block=None` (keine Drift-Baseline, weil nie eine existierte).
    NIE aus dem heutigen `candidate_block` dieses Aufrufs eine alte Bindung
    erfinden, NIE eine D-ID-Allowlist.

    N2R5-DRIFTFIX (ZR-N2R-ANSCHLUSS-20261019-R4): `restrict_drift_to_core_
    identity`, additiv und OPTIONAL (Default `False` -> unveraendertes
    Verhalten jedes bestehenden Aufrufers, insb. `pursue_group_save_
    correction` und jeder direkte Testfixture ohne diesen Parameter, z.B.
    A_R2_CREATION/A_R2_GROUP). NUR der echte Erschaffungsdialog (`core.
    creation_service.run_admitted_creation_dialog`s `_attempt_correction`)
    setzt ihn `True` -- dort ist `current_block` (die Vergleichsbasis fuer
    `detect_unjustified_drift`, s.u.) IMMER der eigene, zuletzt abgelehnte
    SL-Entwurf DIESES Dialogs, NIE ein bestehender kanonischer Spielerstand
    (ein solcher existiert fuer eine brandneue Figur per Definition noch
    nicht). Durchgereicht an `detect_unjustified_drift`s gleichnamigen
    Parameter -- verengt dort das Ergebnis auf Identitaet/Kerninhalt
    (char_id/name/callsign/level/Attribute/Inventar/Fortschritt/Wallet-
    Betrag); jede andere Flavor-Abweichung zwischen zwei Erschaffungs-
    entwuerfen bleibt dann NICHT mehr Drift und faellt durch dieselbe,
    bereits bestehende Schleife unten in `_reset_for_next_attempt` (neuer
    Korrekturversuch, verbraucht ein Attempt-Budget-Slot, erst nach
    `MAX_ADDITIONAL_REQUESTS` HOLD `attempt_budget_exhausted`) -- KEIN
    neuer Zustand, KEIN Bypass von Budget/Admission/Transport."""
    emit = emit or (lambda *_a, **_k: None)
    repair_key = save_correction_domain.creation_repair_key(participant_id, expected_chrononaut_id)
    if forced_conflicts:
        acceptance = save_correction_domain.forced_conflict_acceptance(forced_conflicts)
    else:
        acceptance = save_correction_domain.evaluate(candidate_block, expected_chrononaut_id)
    if acceptance.accepted:
        return CorrectionOutcome(status="accepted", block=candidate_block)
    # R12-SAVECOMPAT (02_SAVEVERTRAG.md §B): KEIN Wallet-Projektionsfallback
    # an DIESER Stelle (v.a. bewusst anders als ein frueherer Entwurf dieses
    # Fixes) -- diese Stelle laeuft fuer JEDEN Erstkandidaten, bevor
    # ueberhaupt ein Korrekturdatensatz existiert, und zahlreiche bestehende
    # Regressionstests nutzen GENAU einen bloss-zahligen Wallet-Fixture-Wert
    # als generischen, bequemen Ausloeser fuer eine beliebige Korrektur-
    # Zustandsmaschine (Legacy-Provenance/Generation-Mismatch/Window-Pause/
    # HOLD-vor-Transport etc.) -- ein hier eingebauter Sofort-Accept wuerde
    # deren gesamten Zustandsmaschinenpfad ueberspringen (empirisch durch
    # einen vollen `run_all.py`-Lauf erhaert: 24 vorher gruene Testdateien
    # schlugen fehl). Die wertgleiche Wallet-Normalisierung greift deshalb
    # NUR innerhalb des bereits laufenden Korrekturzyklus (s. unten, nach
    # einer tatsaechlich empfangenen SL-Antwort) -- dort, wo 02.B den realen
    # Fehlerfall (p01-Teilstand, GENERALREVIEW.md) tatsaechlich zeigte.

    record = load_or_init_record(
        run_dir, repair_key, persona_key=participant_id, char_id=expected_chrononaut_id,
        operation_key=role, table_id=table_id, section_id=section_id,
        errors=acceptance.feedback_items, original_block=candidate_block,
    )
    current_block = candidate_block
    current_acceptance = acceptance
    # R12-W77 (F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A, L03-CHECKPOINT):
    # ein bereits BEGONNENER (nicht brandneuer) Datensatz -- `attempts_used
    # > 0` ist dafuer der einzige verlaessliche Indikator, s. `begin_attempt`/
    # `_reset_for_next_attempt` -- traegt seine gueltige Vergleichsbasis
    # bereits durabel in `bound_block`. Ein Resume in einem NEUEN
    # Prozessaufruf (Crash GENAU zwischen einem persistierten Konflikt-Reset
    # und dem naechsten `begin_attempt`) darf diese NICHT durch den frisch
    # uebergebenen `candidate_block`-Parameter DIESES Aufrufs ersetzen --
    # sonst genau derselbe Datenverlust wie im Retry-Loop unten, nur ueber
    # eine Prozessgrenze hinweg. STATE_HOLD/STATE_WINDOW_PAUSED/STATE_ADOPTED
    # bleiben ausgenommen -- die haben bereits ihre eigene, speziellere
    # Rueckbindung (Legacy-Provenance bzw. `adopted_block`) weiter unten UND
    # eigene SHAPE-Pruefung fuer einen korrupten `attempts_used` (bool/
    # String/ausserhalb des Bereichs, s. `invalid_resume_slot_shape`-Zweig).
    # Die Zustandspruefung steht deshalb BEWUSST VOR der `attempts_used`-
    # Typpruefung (kurzschliessend) -- sonst wuerde ein korrupter, nicht-
    # numerischer Wert (z.B. `"2"`) in GENAU diesen ausgenommenen Zustaenden
    # hier einen ungefangenen `TypeError` ausloesen, statt kontrolliert dem
    # bestehenden SHAPE-Check weiter unten ueberlassen zu werden.
    if (
        record["state"] not in (STATE_HOLD, STATE_WINDOW_PAUSED, STATE_ADOPTED)
        and isinstance(record.get("attempts_used"), int)
        and not isinstance(record.get("attempts_used"), bool)
        and record.get("attempts_used") > 0
    ):
        current_block = record.get("bound_block")
        current_acceptance = (
            save_correction_domain.evaluate(current_block, expected_chrononaut_id)
            if current_block is not None else acceptance
        )
    # Restart-Sicherheit (SC07): ein bereits TERMINAL abgeschlossener
    # Datensatz (HOLD nach Budget-Erschoepfung/Drift/Blockade, ODER bereits
    # adoptiert) wird NIE erneut angefasst -- kein neuer Versand, kein
    # erneutes Hochzaehlen, unabhaengig vom (ggf. neuen) `candidate_block`
    # dieses Aufrufs.
    #
    # R12-W73/W74 (Invarianten 1/2/3/4, F02 Caller/Record-Bindung): EIN HOLD
    # (auch ein bereits VOR diesem Fix gespeicherter Legacy-Datensatz, s.
    # `_window.is_resumable_pre_send_pause`) ODER ein bereits von einem
    # frueheren Aufruf dieser Funktion auf WINDOW_PAUSED migrierter
    # Datensatz wird NUR dann regulaer fortgesetzt, wenn (a) die AKTUELLEN
    # Caller-Identitaetsfelder (persona/char/role/table/section) GENAU mit
    # den gespeicherten Datensatzfeldern uebereinstimmen (F02: Ledger-
    # Abwesenheit fuer die ALTE Recordidentitaet darf KEINEN Versand unter
    # einer ANDEREN Calleridentitaet legitimieren -- ein Mismatch bleibt
    # TERMINAL, bevor ueberhaupt die Fenster-/Ledger-Pruefung greift) UND
    # (b) er NACHWEISLICH am Deadline-vor-Versand-Marker blockiert wurde UND
    # der Slot ueber die volle Ledger-Abwesenheits-/Durabilitaetspruefung
    # entweder NIE einen Requestdatensatz erhalten hat ODER bereits ein
    # durabler Erfolg vorliegt. Jeder andere HOLD/WINDOW_PAUSED-Grund
    # (Budget/Drift/Blockade/unklarer Versand/...) bleibt TERMINAL -- KEIN
    # STATE_VALIDATING, KEIN `begin_attempt`, `attempts_used` bleibt in
    # BEIDEN Zweigen unveraendert.
    #
    # R12-W74 (F02 "Keine spekulative Migration vor Admission"): KEIN
    # eigener `mark_window_paused`-Aufruf mehr HIER -- der Datensatz bleibt
    # bytegleich (`state` unveraendert `hold`/`window_paused`), solange nur
    # die Resumierbarkeit FESTGESTELLT, aber noch kein echter neuer
    # `send_correction_turn`-Versuch unternommen wurde. Eine tatsaechliche
    # Zustandstransition erfolgt NUR noch ueber den bereits bestehenden
    # `outcome.blocked`-Zweig unten (NACH einer frischen Admission-Pruefung)
    # ODER ueber die regulaere Antwortverarbeitung (`record_correction_
    # received`/`mark_adopted`/`mark_hold`), NIE spekulativ VOR einem
    # tatsaechlichen Versuch.
    if record["state"] in (STATE_HOLD, STATE_WINDOW_PAUSED):
        record_identity = (
            record.get("persona_key"), record.get("char_id"), record.get("operation_key"),
            record.get("table_id"), record.get("section_id"),
        )
        caller_identity = (participant_id, expected_chrononaut_id, role, table_id, section_id)
        # R-P5 (ZR-RECOVERY-OFFLINE-20261015-R1, 03_RECOVERY_VERTRAG.md
        # §R-P5): ein TERMINALER Drift-Hold (state=hold, last_reason=
        # unjustified_semantic_drift) ist per Konstruktion NIE ein
        # `_window.is_resumable_pre_send_pause`-Fall (das deckt nur NACHWEISLICH
        # unversandte Deadline-vor-Versand-Bloecke ab) -- ohne eine vom
        # Betreiber bewusst ueber `recovery_ops.apply_p5` erteilte, exakt
        # gebundene Einmalautorisierung bleibt er deshalb unveraendert
        # terminal (naechster Zweig unten). `try_consume_p5_allowance`
        # liefert NUR dann `True`, wenn genau EINE solche, noch nicht fuer
        # einen ANDEREN Vorzustand verbrauchte Autorisierung existiert --
        # KEIN Anheben von `MAX_ADDITIONAL_REQUESTS`, KEIN Reset des
        # Zaehlers. `recovery_extra_attempt` wird additiv im Datensatz
        # mitgefuehrt, damit ein Neustart NACH diesem Punkt (record bereits
        # `validating`, s.u.) den while-Loop weiterhin auf GENAU diesen
        # einen zusaetzlichen Versuch begrenzt (s. `recovery_extra_attempt_
        # opened` vor dem Loop) -- "bloss HOLD->validating" alleine wuerde
        # sonst das alte Mehrversuchsverhalten (bis `MAX_ADDITIONAL_
        # REQUESTS`) reaktivieren.
        # R2-GATE-Fix (GENERALREVIEW.md §5, 04_NAECHSTER_BAU_R2.md "GATE";
        # Originalbeleg `probe_p5_gates.py`s `stop_before_consume`): ein
        # bereits GESETZTER Stop / ein abgelaufenes Fenster / ein bekannt
        # unzureichendes Budget/Requestcap muss VOR jedem Grantverbrauch
        # UND VOR jeder `attempts_used`-Aenderung blockieren, mit NULL
        # physischen Requests (03_RECOVERY_VERTRAG.md §GATE). Im R1 wurde
        # `recovery_ops.try_consume_p5_allowance` (markiert den Grant
        # `consumed=True`) hier bereits aufgerufen, OBWOHL der naechste
        # `begin_attempt` (erhoeht `attempts_used`) und der eigentliche
        # `send_correction_turn` erst SPAETER im `while`-Loop unten auf das
        # Gate treffen -- ein bereits gesetzter Stop liess den Grant/Slot
        # trotzdem bereits verbraucht zurueck (Beleg: `consumed=true`/
        # `attempts_used=2` VOR dem Stop-Check persistiert). Der Fix prueft
        # das GENAU DIESELBE schreibfreie Gate (`read_admission_block`, auch
        # von `send_correction_turn` selbst verwendet) VOR dem P5-eligiblen
        # Zweig -- blockiert es, wird GAR NICHTS verbraucht/veraendert
        # (Grant bleibt unberuehrt, `attempts_used` bleibt unveraendert),
        # und es wird sofort HOLD zurueckgegeben.
        p5_grant_eligible = (
            record["state"] == STATE_HOLD and record_identity == caller_identity
            and record.get("last_reason") == recovery_ops.P5_REQUIRED_REASON
        )
        p5_consumed = False
        if p5_grant_eligible:
            gm_output_limit = getattr(gm_transport, "output_limit_tokens", None)
            gm_route = getattr(gm_transport, "base_url", None)
            # R2-N1-Fix (GENERALREVIEW.md §4 GATE, `p5_known_reservation_
            # insufficient`): die vorige Fassung rief `read_admission_block`
            # OHNE `reserved_usd` auf -- das faellt dort auf die PAUSCHALE
            # Ein-Turn-Schaetzung zurueck (`_synthetic_prices()[1]`), NICHT
            # auf die tatsaechlich fuer DIESEN P5-Zusatzversuch beabsichtigte
            # Reservierung. Ein Restbudget, das fuer die Pauschale reicht,
            # aber NICHT fuer den echten, deutlich teureren Korrekturtext
            # (realer Wiretext + Outputlimit), liess den Grant/`attempts_
            # used` dadurch VOR dem eigentlichen, spaeteren Dispatchguard in
            # `send_correction_turn` bereits verbrauchen (Originalbeleg:
            # `max_usd=0.11791`, tatsaechliche Reserve `1.50291` ->
            # faelschlich `consumed=true`/`attempts_used=2`, erst danach
            # HOLD). Fix: dieselbe Nachricht, die `send_correction_turn`
            # GLEICH NACH diesem Gate fuer GENAU diesen Versuch senden wuerde
            # (`save_correction_domain.build_correction_message`, identischer
            # `attempt_no`/`acceptance`/`original_block` wie im folgenden
            # `while`-Loop), wird HIER VORAB mit derselben `reservation_for_
            # wire_text`-Funktion wie jeder reale Versand reserviert UND vor
            # jedem Grant-/`attempts_used`-Verbrauch gegen Stop/Deadline/
            # Budget/Requestcap geprueft -- keine neue Preisannahme, keine
            # Timeoutaenderung, nur dieselbe bereits bestehende
            # Reservationsfunktion mit dem tatsaechlich beabsichtigten Text.
            pending_block = record.get("bound_block")
            pending_acceptance = (
                save_correction_domain.evaluate(pending_block, expected_chrononaut_id)
                if pending_block is not None else acceptance
            )
            pending_attempt_no = record.get("attempts_used", 0) + 1
            pending_message = save_correction_domain.build_correction_message(
                persona_key=participant_id, char_id=expected_chrononaut_id,
                operation_label=f"{role}:{participant_id}", acceptance=pending_acceptance,
                original_block=pending_block, attempt_no=pending_attempt_no, max_attempts=max_attempts,
            )
            pending_reserved_usd = reservation_for_wire_text(pending_message, output_limit_tokens=gm_output_limit)
            gate_blocked, gate_reason = read_admission_block(
                run_dir, reserved_usd=pending_reserved_usd,
                output_bound_known=(gm_output_limit is not None), route=gm_route,
            )
            if gate_blocked:
                return CorrectionOutcome(status="hold", reason=f"gate_blocked_before_consume:{gate_reason}")
            p5_consumed = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=repair_key, record=record)
        if p5_consumed:
            current_block = record.get("bound_block")
            current_acceptance = (
                save_correction_domain.evaluate(current_block, expected_chrononaut_id)
                if current_block is not None else acceptance
            )
            record = dict(record)
            record["state"] = STATE_VALIDATING
            record["recovery_extra_attempt"] = True
            record["errors"] = list(current_acceptance.feedback_items)
            record["updated_ts"] = time.time()
            _write_record(run_dir, repair_key, record)
        elif record_identity != caller_identity or not _window.is_resumable_pre_send_pause(run_dir, record):
            last_reason = record.get("last_reason") or "hold"
            # N2R5-BESTEFFORT: ein Prozess-Neustart GENAU zwischen diesem
            # `mark_hold(..., reason="attempt_budget_exhausted")` (s.o.) und
            # der Finalisierung durch den Aufrufer darf den bereits dort
            # gebundenen Best-Effort-Kandidaten (`bound_block`) NICHT
            # verlieren -- NUR fuer GENAU diesen Grund; jeder andere
            # terminale Grund (insbesondere `unjustified_semantic_drift`)
            # bleibt UNVERAENDERT ohne `block`.
            #
            # R4-CALLER-BINDUNG (02_JETZT_ENTWICKELN.md §2): der Best-Effort-
            # Block darf NUR an GENAU DENSELBEN Aufrufer zurueckgegeben werden,
            # der den `attempt_budget_exhausted`-Hold erzeugt hat
            # (`record_identity == caller_identity`). Wir erreichen diesen elif
            # auch bei einem FREMDEN Aufrufer (`record_identity !=
            # caller_identity`, erster Oder-Zweig oben) -- ein solcher Fremd-
            # Caller darf KEINEN uebernehmbaren Block erhalten (sonst
            # fremde Caller-Bindung, 02 §2). Nur der passende Resume
            # desselben Callers behaelt Best-Effort.
            resumed_block = (
                record.get("bound_block")
                if last_reason == "attempt_budget_exhausted" and record_identity == caller_identity
                else None
            )
            return CorrectionOutcome(status="hold", reason=last_reason, block=resumed_block)
        else:
            # R12-W75 (F02-SHAPE): `record["attempts_used"]` wird unten DIREKT
            # als `attempt_no` wiederverwendet (der Resume-Zweig des `while`
            # unten erreicht den `STATE_VALIDATING`-Zweig NICHT, der sonst
            # `begin_attempt` vor jedem Versand aufruft) -- ein korrupter Wert
            # (bool statt int, oder ausserhalb des gueltigen offenen Slotbereichs
            # 1..max_attempts, z.B. `4`) darf deshalb HIER, VOR jedem Transport,
            # nicht unbemerkt durchrutschen (W74-Bug: ein solcher Wert erreichte
            # bisher den synthetischen Transport-Versuch und hinterliess einen
            # `sent`-Ledger-Record, bevor der Ledger selbst den Typ ablehnte).
            resumed_attempts_used = record.get("attempts_used")
            if (
                not isinstance(resumed_attempts_used, int) or isinstance(resumed_attempts_used, bool)
                or not (1 <= resumed_attempts_used <= max_attempts)
            ):
                mark_hold(run_dir, repair_key, reason="invalid_resume_slot_shape")
                emit("save_correction_hold", {
                    "participant_id": participant_id, "char_id": expected_chrononaut_id,
                    "reason": "invalid_resume_slot_shape",
                })
                return CorrectionOutcome(status="hold", reason="invalid_resume_slot_shape")
            # F02 Entwurfs-/Original-Bindung: die Drift-Baseline fuer DIESEN
            # Resume ist der durabel GEBUNDENE Originalentwurf -- NIE der
            # (evtl. ausgetauschte) `candidate_block` dieses Aufrufs. Ein
            # Datensatz unter diesem Fix traegt `"bound_block"` IMMER (auch als
            # `None`, s. `load_or_init_record`/`begin_attempt`/`_reset_for_
            # next_attempt`); nur ein echter VOR diesem Fix geschriebener
            # Legacy-Datensatz hat den Schluessel GAR NICHT.
            #
            # R12-W76 (F02-NULL-BINDING-Fix, 01_POSITIVE_WIEDERAUFNAHMEBINDUNG.md
            # §A): `bound_block is None` (Schluessel vorhanden ODER abwesend) ist
            # KEIN Beweis fuer eine erlaubte freie Neuerstellung -- nur die
            # Schluessel-ABWESENHEIT allein darf laenger den caller-gelieferten
            # `_verify_legacy_provenance`-Rueckfall ausloesen (C36s verworfene
            # Lesart). Die Fallunterscheidung (b) vs (c) haengt daran, ob der
            # Aufrufer UEBERHAUPT eine Herkunftsbehauptung mitbringt
            # (`original_request_id`/`original_evidence`, mind. eines gesetzt --
            # NICHT der heutige `candidate_block`, KEINE D-ID-Allowlist):
            #   (b) Behauptung vorhanden (die Figur ist nachweislich KEINE
            #       Erstanlage, z.B. ein bereits belegter Entwurf/Fehler) ->
            #       DIESELBE positive Verifikation wie beim echten Legacy-Pfad;
            #       scheitert sie, kontrolliertes HOLD -- NIE ein Drift-Skip.
            #   (c) KEINE Behauptung (beide `None`) -> echte Erstanlage/
            #       Mehrdeutigkeitskonflikt (`forced_conflicts`/fehlender
            #       Erstkandidat) bleibt UNBERUEHRT ueber den bestehenden Weg
            #       korrigierbar (`current_block=None` -> `acceptance` dieses
            #       Aufrufs, keine Drift-Pruefung -- es gab nie eine
            #       wohldefinierte Baseline, s.u.).
            needs_legacy_verification = "bound_block" not in record or (
                record.get("bound_block") is None
                and (original_request_id is not None or original_evidence is not None)
            )
            if needs_legacy_verification:
                verified_block = _verify_legacy_provenance(
                    run_dir, record=record, participant_id=participant_id,
                    expected_chrononaut_id=expected_chrononaut_id, table_id=table_id, section_id=section_id,
                    original_request_id=original_request_id, original_evidence=original_evidence,
                    original_role=original_role, original_turn_idx=original_turn_idx,
                    original_generation=original_generation,
                )
                if verified_block is _LEGACY_PROVENANCE_REJECTED:
                    # R12-W75/W76 (F02-PROVENANCE): fehlende/fremde/beschaedigte/
                    # widersprüchliche Herkunft ist ein kontrollierter HOLD VOR
                    # jedem Transport/jeder Adoption -- NICHT `current_block=
                    # None` mit uebersprungener Drift-Pruefung (C36s Auslegung
                    # ausdruecklich verworfen, s. Docstring).
                    mark_hold(run_dir, repair_key, reason="legacy_provenance_unverified")
                    emit("save_correction_hold", {
                        "participant_id": participant_id, "char_id": expected_chrononaut_id,
                        "reason": "legacy_provenance_unverified",
                    })
                    return CorrectionOutcome(status="hold", reason="legacy_provenance_unverified")
                current_block = verified_block
            else:
                current_block = record.get("bound_block")
            current_acceptance = (
                save_correction_domain.evaluate(current_block, expected_chrononaut_id)
                if current_block is not None else acceptance
            )
    if record["state"] == STATE_ADOPTED:
        # G01/SC03/SC09/SC13/SC14 (W54-Fix, analog W53-SS7 im Gruppenpfad
        # unten): ein Neustart darf NIE den (hier erneut vom Aufrufer
        # uebergebenen) `candidate_block` als "accepted" zurueckgeben --
        # bei einem Crash NACH diesem `mark_adopted` (s. unten) UND VOR dem
        # terminalen `onboarding.complete_with_save` des Aufrufers ist
        # `candidate_block` dieses Aufrufs IMMER der alte, bereits
        # abgelehnte Entwurf (der Aufrufer kennt die tatsaechlich
        # akzeptierte Antwort an dieser Stelle nicht mehr -- sie wurde nie
        # lokal durabel gemacht). Die einzige vertrauenswuerdige Quelle ist
        # der durabel mit `state="adopted"` persistierte `adopted_block`.
        # Fehlt er (Altrecord vor diesem Fix) oder besteht er die volle
        # Re-Pruefung gegen BEIDE v7-Schemas nicht mehr, ist das ein
        # inkonsistenter Dauerbeleg: kontrolliertes HOLD statt einer
        # Vermutung ueber den Rueckgabewert.
        durable_block = record.get("adopted_block")
        if durable_block is None:
            mark_hold(run_dir, repair_key, reason="adopted_without_durable_block")
            emit("save_correction_hold", {
                "participant_id": participant_id, "char_id": expected_chrononaut_id,
                "reason": "adopted_without_durable_block",
            })
            return CorrectionOutcome(status="hold", reason="adopted_without_durable_block")
        durable_acceptance = save_correction_domain.evaluate(durable_block, expected_chrononaut_id)
        if not durable_acceptance.accepted:
            mark_hold(run_dir, repair_key, reason="adopted_durable_block_failed_revalidation")
            emit("save_correction_hold", {
                "participant_id": participant_id, "char_id": expected_chrononaut_id,
                "reason": "adopted_durable_block_failed_revalidation",
            })
            return CorrectionOutcome(status="hold", reason="adopted_durable_block_failed_revalidation")
        return CorrectionOutcome(status="accepted", block=durable_block)

    emit("save_validation_check", {
        "participant_id": participant_id, "char_id": expected_chrononaut_id, "role": role,
    })

    # R12-W74 (F02): `current_block`/`current_acceptance` sind bereits oben
    # gesetzt -- fuer einen BRANDNEUEN Datensatz unveraendert `candidate_
    # block`/`acceptance` dieses Aufrufs, fuer einen RESUME aus HOLD/
    # WINDOW_PAUSED der durabel GEBUNDENE Originalentwurf (NIE der hier
    # erneut uebergebene `candidate_block`, s. Kommentar oben).
    #
    # R-P5 (03_RECOVERY_VERTRAG.md §R-P5, "Einmaligkeit muss auch den
    # internen while-Loop begrenzen"): additiv im Datensatz gebunden (s.
    # `recovery_ops.try_consume_p5_allowance`-Aufrufstelle oben) -- RESTART-
    # FEST, weil `record.get("recovery_extra_attempt")` hier NEU aus dem
    # (ggf. erst jetzt frisch geladenen) Datensatz gelesen wird, nicht nur
    # innerhalb desselben Aufrufs gesetzt. Ein auf diesem Weg eroeffneter
    # Slot ist IMMER der letzte -- jedes Ergebnis ausser einer vollstaendig
    # akzeptierten Antwort fuehrt unten direkt zu HOLD, NIE zu einem
    # weiteren `_reset_for_next_attempt`/dritten Versand, unabhaengig vom
    # verbleibenden `MAX_ADDITIONAL_REQUESTS`-Budget.
    recovery_extra_attempt_opened = bool(record.get("recovery_extra_attempt"))
    while True:
        # Restart-Sicherheit (SC09/SC13): `state` unterscheidet "noch kein
        # Slot fuer die naechste Antwort eroeffnet" (`validating` -- gilt
        # initial UND nach jeder vollstaendig ausgewerteten, nicht
        # akzeptierten Antwort ohne Drift) von "Slot `attempts_used` wurde
        # bereits begonnen, aber diese ODER eine fruehere Prozessinstanz
        # hat seine Auswertung noch nicht abgeschlossen" (`correction_
        # pending`/`correction_received`, z.B. nach einem Crash GENAU
        # zwischen Versand und Entscheidung). NUR im ersten Fall wird
        # `attempts_used` erhoeht (ein neuer Slot wird eroeffnet, verbraucht
        # Budget) -- im zweiten Fall wird GENAU DERSELBE Slot erneut
        # angefragt; `send_correction_turn` liefert dafuer die bereits
        # durabel empfangene Antwort zurueck (kein Zweitversand), statt
        # stillschweigend auf den naechsten Slot vorzuruecken oder den
        # bereits gezaehlten Versuch zu verdoppeln.
        if record["state"] == STATE_VALIDATING:
            if attempts_exhausted(record, max_attempts):
                mark_hold(run_dir, repair_key, reason="attempt_budget_exhausted")
                emit("save_correction_hold", {
                    "participant_id": participant_id, "char_id": expected_chrononaut_id,
                    "reason": "attempt_budget_exhausted",
                })
                compat_path = _write_compat_export_on_exhaustion(
                    run_dir, repair_key=repair_key, participant_id=participant_id,
                    char_id=expected_chrononaut_id, role=role, table_id=table_id, section_id=section_id,
                    best_view=current_block, errors=current_acceptance.feedback_items,
                    reason="attempt_budget_exhausted",
                )
                # N2R5-BESTEFFORT (Flo-Design, ZR-N2R-ANSCHLUSS-20261020-
                # FINALRUN3): `block=current_block` ist additiv (Default
                # `None`, kein bestehender Aufrufer liest `.block` bei
                # `status="hold"`) -- liefert dem EINZIGEN vorgesehenen
                # Konsumenten (`core.creation_service.
                # run_admitted_creation_dialog`) den letzten Kandidaten
                # dieser Figur, damit er ihn best-effort finalisieren kann,
                # statt terminal zu pausieren. `current_block` ist hier NIE
                # ein durch Drift abgelehnter Kandidat (der fuehrt weiter
                # unten zu einem eigenen `unjustified_semantic_drift`-HOLD
                # OHNE `block`, UNVERAENDERT terminal) -- nur `None`, wenn
                # es (G02/SC06-Mehrdeutigkeitskonflikt) nie einen
                # wohldefinierten EINEN Kandidaten gab; der Aufrufer bleibt
                # dann unveraendert terminal HOLD.
                return CorrectionOutcome(
                    status="hold", reason="attempt_budget_exhausted", block=current_block,
                    compat_export_path=str(compat_path) if compat_path else None,
                )
            record = begin_attempt(run_dir, repair_key, original_block=current_block)

        attempt_no = record["attempts_used"]
        emit("save_correction_attempt", {
            "participant_id": participant_id, "char_id": expected_chrononaut_id,
            "attempt_no": attempt_no, "max_attempts": max_attempts,
        })
        message = save_correction_domain.build_correction_message(
            persona_key=participant_id, char_id=expected_chrononaut_id,
            operation_label=f"{role}:{participant_id}", acceptance=current_acceptance,
            original_block=current_block, attempt_no=attempt_no, max_attempts=max_attempts,
        )
        outcome = send_correction_turn(
            run_dir, role=role, table_id=table_id, section_id=section_id, participant=participant_id,
            turn_idx=attempt_no, outgoing_text=message, gm_transport=gm_transport,
        )
        if outcome.blocked:
            reason = outcome.reason or "blocked"
            # R12-W73 (Invarianten 1/3/5): ein NACHWEISLICH unversandter
            # Deadline-vor-Versand-Block (egal ob dies der erste Block
            # dieses Slots ist ODER ein wiederholter Block nach einem
            # bereits erfolgten WINDOW_PAUSED-Resume-Versuch, s.o.) wird
            # NICHT terminal -- idempotent (kein Write bei gleichbleibendem
            # `reason`) pausiert, KEIN Loop, KEIN Zaehler-/Metadatenchange.
            if _window.is_pre_send_deadline_reason(reason) and _window.slot_never_sent(
                run_dir, role=role, table_id=table_id, section_id=section_id,
                turn_idx=attempt_no, participant=participant_id,
            ):
                mark_window_paused(run_dir, repair_key, reason=reason)
                emit("save_correction_hold", {
                    "participant_id": participant_id, "char_id": expected_chrononaut_id,
                    "reason": reason,
                })
                return CorrectionOutcome(status="hold", reason=reason)
            mark_hold(run_dir, repair_key, reason=reason)
            emit("save_correction_hold", {
                "participant_id": participant_id, "char_id": expected_chrononaut_id,
                "reason": reason,
            })
            return CorrectionOutcome(status="hold", reason=reason)

        record = record_correction_received(run_dir, repair_key, request_id=outcome.request_id)

        # R-SCF-A (02_SAVEVERTRAG.md §A "Alle Antworten, inklusive
        # abgeschnittener, vor der Weiterverarbeitung dauerhaft und
        # append-only mit Run/Figur/Abschnitt/Requestbindung sichern"):
        # JEDE tatsaechlich empfangene rohe SL-Antwort dieser Figur wird
        # HIER archiviert, BEVOR irgendeine Extraktion/Annahme/Drift-
        # Pruefung stattfindet -- unabhaengig davon, ob sie spaeter
        # akzeptiert/verworfen/mehrdeutig eingestuft wird. Reiner additiver
        # Seiteneffekt (append-only Datei, s. `core.save_compatibility.
        # archive_raw_response`), AENDERT NICHTS am bestehenden `record`/
        # Kontrollfluss.
        save_compatibility_core.archive_raw_response(
            run_dir, repair_key=repair_key, char_id=expected_chrononaut_id, section_id=section_id,
            table_id=table_id, attempt_no=attempt_no, request_id=outcome.request_id,
            raw_text=outcome.text or "",
        )

        # G02/SC06 (W54-Fix): strikter, mehrdeutigkeitssicherer
        # Extraktionspfad fuer die Korrekturantwort -- sieht ALLE rohen
        # Kandidaten fuer `expected_chrononaut_id` in dieser EINEN Antwort,
        # BEVOR irgendeine Auswahl getroffen wird (statt des verlustbehafteten
        # 'erster gewinnt' aus `saves.extract_all_saves`).
        new_candidate, new_conflicts = save_correction_domain.extract_checked_single(
            outcome.text or "", expected_chrononaut_id,
        )
        if new_candidate is None:
            # Entweder keine auswertbare/zur Figur passende Antwort ODER
            # (falls `new_conflicts` nicht leer) mehrere rohe Bloecke
            # derselben char_id/save_id mit ABWEICHENDEM Inhalt -- in
            # BEIDEN Faellen wird KEIN Kandidat uebernommen. Bei einem
            # echten Konflikt wird die SL zusaetzlich explizit auf die
            # Mehrdeutigkeit hingewiesen (statt des zuletzt bekannten
            # generischen Fehlerkatalogs), damit der naechste Versuch (falls
            # Budget verbleibt) gezielt eine EINDEUTIGE Antwort anfordert.
            if new_conflicts:
                # R12-W77 (F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A): eine
                # mehrdeutige Zwischenantwort hebt die bereits belegte
                # Vergleichsbasis NICHT mehr auf -- `current_block` bleibt
                # der zuletzt durabel gebundene Originalentwurf (NICHT
                # `None`). Konfliktfeedback an die SL (`current_acceptance`
                # fuer die naechste Nachricht) und das Recht auf
                # Inhaltsaenderung bleiben getrennt: die Drift-Pruefung
                # weiter unten rekonstruiert ihre `error_paths` IMMER frisch
                # aus `current_block` selbst (s. dort), NIE aus diesem
                # `current_acceptance`-Objekt -- ein spaeterer Versuch, der
                # GENAU denselben Inhalt (oder eine zulaessige Formatkorrektur
                # an einem tatsaechlich gemeldeten Fehlerpfad) liefert, bleibt
                # deshalb weiterhin annehmbar; eine echte Umbenennung bleibt
                # weiterhin Drift.
                current_acceptance = save_correction_domain.forced_conflict_acceptance(new_conflicts)
            if recovery_extra_attempt_opened:
                # R-P5: der ueber `recovery_ops` gebundene zusaetzliche Slot ist
                # IMMER der letzte -- eine unauswertbare/mehrdeutige Antwort
                # darauf ist KEIN dritter automatischer Korrekturversuch (03
                # §R-P5: "sicherer Abschluss/HOLD ohne automatische dritte
                # Korrekturanfrage").
                mark_hold(run_dir, repair_key, reason="recovery_extra_attempt_exhausted")
                emit("save_correction_hold", {
                    "participant_id": participant_id, "char_id": expected_chrononaut_id,
                    "reason": "recovery_extra_attempt_exhausted",
                })
                compat_path = _write_compat_export_on_exhaustion(
                    run_dir, repair_key=repair_key, participant_id=participant_id,
                    char_id=expected_chrononaut_id, role=role, table_id=table_id, section_id=section_id,
                    best_view=current_block, errors=current_acceptance.feedback_items,
                    reason="recovery_extra_attempt_exhausted",
                )
                return CorrectionOutcome(
                    status="hold", reason="recovery_extra_attempt_exhausted",
                    compat_export_path=str(compat_path) if compat_path else None,
                )
            record = _reset_for_next_attempt(
                run_dir, repair_key, errors=current_acceptance.feedback_items, original_block=current_block,
            )
            continue

        # R12-SAVECOMPAT (02_SAVEVERTRAG.md §B, GENERALREVIEW.md): BEVOR die
        # neue Antwort gegen die bestehende Drift-/Annahmepruefung laeuft,
        # wird sie durch die reine, wertgleiche CU-Retention-Projektion
        # gereicht (ZEITRISS-eigene `currency:"CU"` aus dem geschlossenen
        # Exportwallet entfernt, NIE verworfen -- bleibt in der Rettungs-
        # sicht; der tatsaechlich im p01-Teilstand aufgetretene Fehler).
        # BEWUSST NUR diese eine Regel (NICHT der zusaetzliche Zahl->
        # balance-Wrap, `save_compatibility_domain.RULE_NUMBER_TO_BALANCE`
        # -- der ist bereits lange vor diesem Fix durch die unveraenderte
        # `detect_unjustified_drift`/`_is_allowed_amount_wrap`-Ausnahme
        # abgedeckt UND zahlreiche bestehende Regressionstests verwenden
        # einen DURCHGAENGIG bloss-zahligen Wallet-Fixturewert gezielt als
        # 'die SL liefert NIE eine gueltige Korrektur'-Ausloeser fuer
        # Budget-Erschoepfungs-/HOLD-Pfade, die mit Wallets nichts zu tun
        # haben -- eine zusaetzliche automatische Zahl-Wrap-Projektion
        # GENAU hier wuerde deren Fixture canceln, empirisch belegt durch
        # einen vollen `run_all.py`-Lauf). `new_candidate_for_check`
        # ersetzt den Rohkandidaten NUR fuer die Annahme-/Drift-/
        # Adoptionslogik dieses Versuchs; die Projektion ist durch
        # Konstruktion wertgleich (keine neue Drift-Kategorie noetig).
        new_projection = save_compatibility_domain.project_wallets_in_block(
            new_candidate, rules=save_compatibility_domain.CU_ONLY_RULES,
        )
        new_candidate_for_check = new_projection.canonical_candidate
        new_acceptance = save_correction_domain.evaluate(new_candidate_for_check, expected_chrononaut_id)
        # G02/SC06: `current_block` ist `None`, wenn der zuletzt
        # ausgewertete Slot ein erkannter Mehrdeutigkeitskonflikt war (kein
        # einzelner Caller-Kandidat, s. oben) -- es gibt dann KEINE
        # wohldefinierte EINE vorherige Fassung, gegen die eine Drift
        # sinnvoll gemessen werden koennte (mehrere widersprechende
        # Rohbloecke sind keine gemeinsame Basis). Die neue Antwort wird in
        # diesem Fall NUR auf Schema/Bindung geprueft (wie ein ganz neuer
        # erster Versuch), keine Drift-Pruefung.
        if current_block is None:
            drift = []
        else:
            # R12-SAVECOMPAT: dieselbe (engere, CU-only) Wallet-Projektion
            # wird SYMMETRISCH auch auf die Vergleichsbasis angewendet --
            # sonst wuerde ein bereits im Vorgaengerentwurf vorhandenes
            # CU-Feld eine kuenstliche Drift gegenueber der frisch
            # normalisierten neuen Antwort erzeugen (genau der reale Fehler,
            # der den p01-Teilstand in `last_reason=unjustified_semantic_
            # drift` festsetzte, obwohl Betrag und Save unveraendert waren).
            current_block_for_check = save_compatibility_domain.project_wallets_in_block(
                current_block, rules=save_compatibility_domain.CU_ONLY_RULES,
            ).canonical_candidate
            # R12-W77 (F02-LIFECYCLE-Fix): `error_paths` IMMER frisch aus
            # `current_block` selbst neu ausgewertet (NIE aus dem evtl. durch
            # einen Konfliktzwischenschritt ueberschriebenen
            # `current_acceptance`-Objekt, s. oben) -- dasselbe bereits
            # bestehende Idiom wie beim HOLD/WINDOW_PAUSED-Resume weiter oben
            # (`current_acceptance = evaluate(current_block, ...)`). Eine
            # echte Formatkorrektur nach einer Konfliktantwort (z.B. gleicher
            # Walletwert + gueltiger campaign.mode nach echtem Schemafehler)
            # bleibt dadurch annehmbar; eine Umbenennung bleibt Drift.
            base_acceptance = save_correction_domain.evaluate(current_block_for_check, expected_chrononaut_id)
            error_paths = {e.path for e in base_acceptance.structure.errors}
            drift = save_correction_domain.detect_unjustified_drift(
                current_block_for_check, new_candidate_for_check, error_paths,
                restrict_to_core_identity=restrict_drift_to_core_identity,
            )
        if drift:
            mark_hold(run_dir, repair_key, reason="unjustified_semantic_drift")
            emit("save_correction_hold", {
                "participant_id": participant_id, "char_id": expected_chrononaut_id,
                "reason": "unjustified_semantic_drift",
            })
            return CorrectionOutcome(status="hold", reason="unjustified_semantic_drift", drift=drift)

        if new_acceptance.accepted:
            # G01 (W54-Fix): die adoptierten Blockbytes werden ATOMAR mit
            # state="adopted" persistiert (identisches Muster zum W53-Fix
            # in `pursue_group_save_correction` unten) -- ein Crash GENAU
            # zwischen dieser Zeile und dem terminalen `onboarding.
            # complete_with_save`-Aufruf des Aufrufers findet den gueltigen
            # Block bei Wiederaufnahme durabel wieder (s. STATE_ADOPTED-
            # Zweig oben), statt den unvalidierten Caller-Kandidaten
            # zurueckzuspielen. R12-SAVECOMPAT: der adoptierte/zurueck-
            # gegebene Block ist `new_candidate_for_check` (die kanonische,
            # wertgleiche Projektion) -- NIE der rohe `new_candidate`, damit
            # kein CU-Feld in den kanonischen Store gelangt.
            mark_adopted(run_dir, repair_key, adopted_block=new_candidate_for_check)
            return CorrectionOutcome(status="accepted", block=new_candidate_for_check)

        if recovery_extra_attempt_opened:
            # R-P5: dieselbe Einmaligkeitsgrenze wie oben -- eine schema-/
            # bindungsungueltige (aber driftfreie) Antwort auf den gebundenen
            # zusaetzlichen Slot bleibt ein sicherer Abschluss, KEIN dritter
            # Versand, unabhaengig vom verbleibenden `MAX_ADDITIONAL_REQUESTS`-
            # Budget.
            mark_hold(run_dir, repair_key, reason="recovery_extra_attempt_exhausted")
            emit("save_correction_hold", {
                "participant_id": participant_id, "char_id": expected_chrononaut_id,
                "reason": "recovery_extra_attempt_exhausted",
            })
            compat_path = _write_compat_export_on_exhaustion(
                run_dir, repair_key=repair_key, participant_id=participant_id,
                char_id=expected_chrononaut_id, role=role, table_id=table_id, section_id=section_id,
                best_view=new_candidate_for_check, errors=new_acceptance.feedback_items,
                reason="recovery_extra_attempt_exhausted",
            )
            return CorrectionOutcome(
                status="hold", reason="recovery_extra_attempt_exhausted",
                compat_export_path=str(compat_path) if compat_path else None,
            )

        current_block = new_candidate
        current_acceptance = new_acceptance
        record = _reset_for_next_attempt(
            run_dir, repair_key, errors=new_acceptance.feedback_items, original_block=current_block,
        )


# ───────────────────────── Gruppenabschluss-Korrektur ──────────────────────


def _round_counter_path(run_dir: str | Path, table_id: str, section_id: str) -> Path:
    d = _records_dir(run_dir) / "_group_rounds"
    d.mkdir(parents=True, exist_ok=True)
    safe = f"{table_id}__{section_id}".replace("/", "_")
    return d / f"{safe}.json"


def _next_round_no(run_dir: str | Path, table_id: str, section_id: str) -> int:
    p = _round_counter_path(run_dir, table_id, section_id)
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        n = int(data.get("round", 0)) + 1
    else:
        n = 1
    _atomic_write_json(p, {"table_id": table_id, "section_id": section_id, "round": n})
    return n


# ───────────────────── Rundenidentitaet restart-fest (W49) ─────────────────
#
# W48-REPORT.md §6 dokumentierte offen: `_next_round_no` wurde bei JEDEM
# rundeneroeffnenden Aufruf unbedingt weitergezaehlt (kein Peek-vor-
# Increment, anders als `attempts_used`/`state` im Einzelfigurpfad) -- ein
# Prozessabsturz GENAU zwischen "Runde eroeffnet" (Zaehler/Budget erhoeht,
# Nachricht gebaut) und "Antwort verarbeitet" (Checkpoint) liess einen
# Neustart eine NEUE Runde (neuer `round_no`) eroeffnen, statt dieselbe
# Ledger-Operationsidentitaet (`table_id, section_id, role, turn_idx=
# round_no, participant`) wiederzuverwenden -- `send_correction_turn`s
# bestehende `find_durable_result`/`find_answered_without_text`/
# `OpenReservationExistsError`-Wiederaufnahme griff dadurch nie, weil die
# Identitaet (der `turn_idx`) sich am naechsten `pursue_group_save_
# correction`-Aufruf bereits geaendert hatte.
#
# Fix (eng, nur dieses Modul, KEIN neuer Transaktionskern): ein
# `_group_rounds/<table>__<section>.open.json`-Marker wird GENAU DANN
# persistiert, wenn eine Runde tatsaechlich NEU eroeffnet wird (Zaehler
# erhoeht, Budget verbraucht) -- VOR dem Versand (`send_correction_turn`).
# Existiert beim naechsten Aufruf bereits ein solcher Marker, ist das KEINE
# neue Runde, sondern die Wiederaufnahme einer bereits eroeffneten, noch
# nicht vollstaendig verarbeiteten Runde: derselbe `round_no`, dasselbe
# Mitgliederset, `begin_attempt` wird NICHT erneut aufgerufen (sonst
# Doppelzaehlung desselben Versuchs). Der Marker wird ERST geloescht, NACHDEM
# die Antwort dieser Runde vollstaendig in `harvested`/die Korrekturdatensaetze
# uebernommen wurde (vor dem naechsten `store.complete_section`-Aufruf, der
# bereits ueber die bestehende idempotente Produktmechanik laeuft und von
# diesem Fix nicht angefasst wird).


def _open_round_path(run_dir: str | Path, table_id: str, section_id: str) -> Path:
    d = _records_dir(run_dir) / "_group_rounds"
    d.mkdir(parents=True, exist_ok=True)
    safe = f"{table_id}__{section_id}".replace("/", "_")
    return d / f"{safe}.open.json"


def _load_open_round(run_dir: str | Path, table_id: str, section_id: str) -> dict | None:
    p = _open_round_path(run_dir, table_id, section_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _write_open_round(
    run_dir: str | Path, table_id: str, section_id: str, round_no: int, members: list[dict],
) -> None:
    _atomic_write_json(_open_round_path(run_dir, table_id, section_id), {
        "table_id": table_id, "section_id": section_id, "round": round_no, "members": members,
    })


def _clear_open_round(run_dir: str | Path, table_id: str, section_id: str) -> None:
    p = _open_round_path(run_dir, table_id, section_id)
    if p.exists():
        p.unlink()


def has_open_group_round(run_dir: str | Path, table_id: str, section_id: str) -> bool:
    """FIX1 (R4-Rundenabschluss, 01-PRODUCT-REVIEW.md "Ein verbliebener
    Produktblocker"): oeffentlicher, reiner Lesezugriff auf `_load_open_
    round` fuer den NORMALEN Spieler-/Lobby-Aufrufer (`core.runtime.
    SectionRuntime.run_full_section`) -- eine bereits NEU eroeffnete, aber
    noch nicht vollstaendig verarbeitete Gruppenkorrekturrunde (Marker +
    Mitgliederset, s. Modulkommentar oben) ist GENAUSO ein dauerhaft
    gebundener Korrekturzustand wie ein gepinnter `__plan.json` -- OHNE
    dass der Aufrufer diesen Zustand selbst interpretiert/veraendert.
    Identitaets-/Slot-/Admissionspruefung bleiben ausschliesslich in
    `pursue_group_save_correction` (derselben Funktion, die diese Runde
    auch geschrieben hat); diese Funktion liefert NUR die blosse
    Anwesenheit des Markers."""
    return _load_open_round(run_dir, table_id, section_id) is not None


#: FIX2 (R4-Duo-Anschluss): Zustaende einer Gruppen-Korrektur, die eine noch
#: OFFENE (nicht-adoptierte, nicht terminal gehaltene) Abschlussarbeit
#: bedeuten. WINDOW_PAUSED hat seinen eigenen marker-gebundenen Resume
#: (`has_open_group_round`), HOLD/ADOPTED/ABORTED sind terminal.
_OPEN_GROUP_CORRECTION_STATES = frozenset({
    STATE_VALIDATING, STATE_CORRECTION_PENDING, STATE_CORRECTION_RECEIVED,
})


def has_unfinished_group_round(
    run_dir: str | Path, table_id: str, section_id: str, max_attempts: int = MAX_ADDITIONAL_REQUESTS,
) -> bool:
    """FIX2 (R4-Duo-Anschluss, 02-FRESH-MAIN-AUFTRAG.md "Reparatur 2:
    unerledigte Abschlussarbeit dauerhaft erkennen"): marker-UNABHAENGIGER,
    rein lesender Nachweis einer ERSCHOEPFTEN, aber noch nicht abgeschlossenen
    Gruppenkorrektur fuer GENAU diesen Tisch/diese Section. Deckt das Fenster
    ab, das `has_open_group_round` NICHT sieht: nach ausgeschoepftem
    Korrekturbudget (`attempts_used >= MAX_ADDITIONAL_REQUESTS`) loescht
    `pursue_group_save_correction` den `.open.json`-Marker (`_clear_open_round`),
    die Mitglieds-Korrekturdatensaetze bleiben jedoch in einem offenen,
    NICHT-adoptierten Zustand (`validating`/`correction_pending`/
    `correction_received`) OHNE gepinnten Plan/Final. Genau dann darf der
    normale Spieleinstieg KEINEN Storyzug starten (belegter Duo-B-Fall:
    attempts_used=3, danach 14 unnoetige GM-Zuege), sondern muss den
    idempotenten Abschluss-/Recoveryzweig fuehren.

    BEWUSST eng auf ERSCHOEPFTE Datensaetze beschraenkt: ein offener, aber
    noch NICHT erschoepfter Korrekturzustand mit verbleibendem Budget gehoert
    entweder zum markergebundenen Resume (`has_open_group_round`) oder zu einem
    regulaeren Korrekturzug/Folgespielzug mit verbleibendem Budget (z.B. die
    Kompat-/Folgespiel-Faelle in `test_savecompat_*`, die nach erfolgreicher
    Reparatur regulaer weiterspielen) -- fuer die darf hier KEIN HOLD erzwungen
    werden. Reiner Lesezugriff (kein `mkdir`, keine Mutation); terminale
    Zustaende (adopted/hold/aborted) zaehlen NICHT als offen."""
    records_dir = Path(run_dir) / "save_corrections"
    if not records_dir.is_dir():
        return False
    for path in sorted(records_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            isinstance(record, dict)
            and record.get("operation_key") == ROLE_GROUP
            and record.get("table_id") == table_id
            and record.get("section_id") == section_id
            and record.get("state") in _OPEN_GROUP_CORRECTION_STATES
            and attempts_exhausted(record, max_attempts)
        ):
            return True
    return False


def pursue_group_save_correction(
    *, lobby, table, section_id: str, harvested: dict, harvest_completion,
    states_dir, today: str, harvest_validator, persona_state_store, gm_transport,
    cid_to_pk: dict, harvest_extractor, max_attempts: int = MAX_ADDITIONAL_REQUESTS,
    emit=None,
):
    """01_AUFTRAG_SAVEGATE.md §B: solange `store.complete_section(...)`
    `missing` Mitglieder meldet, werden GENAU diese (noch mit Budget)
    gezielt bei der SL nachgefordert -- über dieselbe Tisch-/SL-Session
    (`table.leader`-Kanal, `store.submit_to_sl`), bereits gültige Mitglieder
    bleiben unangetastet (nur `harvested[pk]` der tatsächlich angefragten
    `pk`s wird ggf. ersetzt). Jede Runde fragt ALLE aktuell fehlenden
    Mitglieder mit verbleibendem Budget in EINER Nachricht ab und erhöht
    DEREN Zähler vor dem Versand ("jede gesendete Nachricht zählt"). Bricht
    ab (gibt den zuletzt erhaltenen `CompletionResult` unverändert zurück),
    sobald entweder `complete_section` erfolgreich ist, kein Mitglied mehr
    Budget hat, oder ein Versand admission-/transportseitig blockiert.

    NUR aufzurufen, solange für `section_id` noch KEIN Abschluss-Auftrag
    gepinnt ist (`store.open_completion_order_for_table(...) is None`,
    vom Aufrufer VOR diesem Call geprüft) -- ein bereits gepinnter Plan
    repräsentiert eine COMMITTETE Entscheidung und wird von dieser Funktion
    NICHT angefasst (keine neue Gruppen-Transaktionsengine, Kandidatenstadium
    bleibt strikt vom validierten/gepinnten Stadium getrennt)."""
    from ..domain.zeitriss import saves as zeitriss_saves  # lokal: nur hier benoetigt (G02/SC06)

    emit = emit or (lambda *_a, **_k: None)
    run_dir = lobby.run_dir

    while not harvest_completion.success and harvest_completion.missing:
        open_round = _load_open_round(run_dir, table.table_id, section_id)
        candidates: list[dict] = []

        if open_round is not None:
            # Wiederaufnahme (W49, s. Modulkommentar oben): eine fruehere
            # Prozessinstanz hat diese Runde bereits eroeffnet (Zaehler
            # bereits erhoeht, Nachricht ggf. schon unterwegs/beantwortet),
            # ist aber VOR der vollstaendigen Verarbeitung gecrasht.
            # Dasselbe `round_no` + dasselbe Mitgliederset werden
            # unveraendert wiederverwendet -- `begin_attempt` NICHT erneut
            # aufrufen (Budget wurde bereits beim urspruenglichen
            # Rundenstart verbraucht).
            #
            # R12-W75 (F02-SHAPE Gruppenpfad): der Marker wird allein ueber
            # `_open_round_path(run_dir, table_id, section_id)` gefunden --
            # `safe = f"{table_id}__{section_id}".replace("/", "_")` kann
            # fuer zwei TATSAECHLICH verschiedene (table_id, section_id)-
            # Paare (falls eines davon "/" enthaelt) auf denselben Dateinamen
            # kollidieren. Die korrekte DATEIPOSITION alleine beweist deshalb
            # NICHT, dass der INHALT zur aktuellen Gruppenidentitaet passt --
            # der Marker TRAEGT seine eigene `table_id`/`section_id` (s.
            # `_write_open_round`) UND jedes betroffene Mitglieds-
            # Korrekturdatensatz traegt dieselben Identitaetsfelder (s.
            # `load_or_init_record`). Ein Widerspruch in IRGENDEINEM davon
            # (Marker ODER ein einzelnes Memberrecord) wird NICHT durch die
            # zufaellig passende Dateiposition verdeckt -> kontrollierter
            # HOLD, Marker/Members/round_no bleiben UNVERAENDERT (kein
            # `_clear_open_round`, kein Member-Write, keine neue Runde wird
            # erfunden) -- der naechste Aufruf sieht denselben Zustand
            # erneut und kann ihn mit der korrekten Identitaet erneut
            # pruefen.
            member_repair_keys = [
                save_correction_domain.group_repair_key(table.table_id, section_id, member["char_id"])
                for member in open_round["members"]
            ]
            member_records = [load_record(run_dir, k) for k in member_repair_keys]
            marker_identity_ok = (
                open_round.get("table_id") == table.table_id and open_round.get("section_id") == section_id
            )
            members_identity_ok = all(
                member_record is not None
                and member_record.get("table_id") == table.table_id
                and member_record.get("section_id") == section_id
                and member_record.get("operation_key") == ROLE_GROUP
                and member_record.get("char_id") == member["char_id"]
                and member_record.get("persona_key") == member["persona_key"]
                for member_record, member in zip(member_records, open_round["members"])
            )
            if not (marker_identity_ok and members_identity_ok):
                emit("save_correction_hold", {
                    "section_id": section_id, "table_id": table.table_id,
                    "reason": "group_round_identity_mismatch",
                })
                break
            # R12-W76 (F02-SHAPE Gruppenpfad, F02 §B): dieselbe SHAPE-Probe
            # wie der Einzelfigurpfad (`_window.is_resumable_pre_send_pause`/
            # `pursue_single_figure_correction`s eigener Check) -- ein
            # korrupter `attempts_used` (bool statt int, oder ausserhalb des
            # gueltigen offenen Slotbereichs 1..max_attempts) darf auch HIER,
            # VOR jedem Resume-Transport, nicht unbemerkt durchrutschen. Der
            # getrennte Gruppen-`round_no` (s.u.) ist NICHT das Versuchs-
            # budget einer Figur -- diese Probe prueft ausschliesslich die
            # pro-Mitglied `attempts_used`-Werte, NICHT `round_no`.
            members_shape_ok = all(
                isinstance(member_record.get("attempts_used"), int)
                and not isinstance(member_record.get("attempts_used"), bool)
                and 1 <= member_record.get("attempts_used") <= max_attempts
                for member_record in member_records
            )
            if not members_shape_ok:
                # R12-W77 (F02-MARKER-Fix, 01_BINDUNGSERHALT.md §B,
                # L06-GROUP-CONTROL): W76 rief hier je Mitglied `mark_hold`
                # UND `_clear_open_round` auf -- das zerstoert GENAU die
                # widerspruechliche Runde (Marker geloescht, BEIDE
                # Memberrecords ueberschrieben), die dieser Vorpruefzweig
                # eigentlich schuetzen soll (GENERALREVIEW.md §4). Die Zahl-/
                # SHAPE-Pruefung selbst bleibt (`members_shape_ok` oben) --
                # die Ablehnung HAELT jetzt NUR noch VOR jedem Transport,
                # OHNE Marker/Memberrecords/round_no/attempts/Requesthistorie
                # anzufassen (PRE==POST, byte-/modegleich). Kein neuer
                # Rundenaufbau beim naechsten Resume -- derselbe Marker und
                # dieselben (weiterhin korrupten) Memberrecords werden beim
                # naechsten Aufruf erneut genau hier abgelehnt (Wiederholung
                # bleibt gleich, keine manuelle Reparatur des Werts).
                emit("save_correction_hold", {
                    "section_id": section_id, "table_id": table.table_id,
                    "reason": "invalid_resume_slot_shape",
                })
                break
            round_no = open_round["round"]
            # R12-W74 (F01b Gruppen-Nachzug): VOR jedem Resume-Versand fuer
            # DIESE Rundenidentitaet (`table_id`/`section_id`/`ROLE_GROUP`/
            # `turn_idx=round_no`/`participant=table.leader`) dieselbe volle
            # Ledger-Klassifikation wie im Einzelfigurpfad (`_window.slot_
            # resumable`) -- ein bereits `accounted` Requestdatensatz MIT
            # `error` (echter Transportfehler VOR dieser Wiederaufnahme,
            # `finish_error`) oder eine offene/unklare Reservierung bleibt
            # TERMINAL: KEIN zweiter POST fuer dieselbe Runde. Ein durabler
            # Erfolg ODER echte Abwesenheit lassen den bestehenden,
            # unveraenderten Resume-Weg unten unberuehrt -- `send_
            # correction_turn`s eigener `find_durable_result`-Check deckt
            # beide Faelle bereits korrekt ab (kein zusaetzlicher Code
            # noetig).
            if not _window.slot_resumable(
                run_dir, role=ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                turn_idx=round_no, participant=table.leader,
            ):
                for member in open_round["members"]:
                    member_repair_key = save_correction_domain.group_repair_key(
                        table.table_id, section_id, member["char_id"],
                    )
                    mark_hold(run_dir, member_repair_key, reason="unresolved_prior_round_outcome")
                _clear_open_round(run_dir, table.table_id, section_id)
                emit("save_correction_hold", {
                    "section_id": section_id, "table_id": table.table_id,
                    "reason": "unresolved_prior_round_outcome",
                })
                break
            for member in open_round["members"]:
                pk = member["persona_key"]
                char_id = member["char_id"]
                repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
                record = load_record(run_dir, repair_key)
                original_block = member["original_block"]
                acceptance = save_correction_domain.evaluate(original_block, char_id)
                candidates.append({
                    "persona_key": pk, "char_id": char_id, "repair_key": repair_key,
                    "acceptance": acceptance, "original_block": original_block,
                    "attempt_no": record["attempts_used"] if record is not None else 1,
                })
        else:
            restored_from_adopted = False
            for pk in harvest_completion.missing:
                char_id = table.chrononaut_ids.get(pk)
                if char_id is None:
                    continue
                repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
                record = load_or_init_record(
                    run_dir, repair_key, persona_key=pk, char_id=char_id,
                    operation_key=ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                )
                # Restart-Sicherheit (analog SC07 im Einzelfigurpfad): ein
                # bereits TERMINAL abgeschlossener Datensatz (HOLD -- Budget
                # erschoepft, Drift, Blockade -- ODER bereits adoptiert) wird
                # NIE erneut angefragt, unabhaengig vom Zaehlerstand.
                #
                # R12-W73 (Invariante 6, Guard): `STATE_WINDOW_PAUSED`
                # gehoert ausdruecklich in diese Skip-Menge -- ein
                # pausiertes Mitglied wird NIE ueber diesen FRISCHEN Zweig
                # (der unten `begin_attempt`/einen neuen `round_no`
                # eroeffnet) erneut aufgenommen, das waere eine
                # Doppelzaehlung desselben Slots. Der einzige regulaere
                # Resume-Weg fuer ein WINDOW_PAUSED-Mitglied ist der
                # `open_round is not None`-Zweig oben (derselbe `round_no`,
                # dasselbe Mitgliederset, KEIN `begin_attempt`) -- solange
                # dieser Fix den Marker UND den Mitgliedszustand IMMER
                # gemeinsam setzt (s. `outcome.blocked`-Zweig unten), wird
                # dieser Zweig fuer ein WINDOW_PAUSED-Mitglied praktisch nie
                # erreicht; die Skip-Bedingung bleibt trotzdem als
                # Verteidigungslinie bestehen.
                if record["state"] in (STATE_HOLD, STATE_ADOPTED, STATE_WINDOW_PAUSED) or attempts_exhausted(record, max_attempts):
                    # R-SCF-A (02_SAVEVERTRAG.md §D/§E "Fuenfer-Ernte"):
                    # additiver Seiteneffekt, NUR ein Datei-Write in einem
                    # eigenen Verzeichnis (`save_compat/...`) -- RUEHRT
                    # `record`/`state`/`attempts_used`/die bestehende
                    # Skip-/Resume-Logik dieser Funktion NICHT an (bewusst
                    # KEIN `mark_hold` hier, s. Modulkommentar oben zu
                    # empirisch belegten Breitenregressionen durch
                    # Kontrollfluss-Aenderungen an dieser Stelle). Erfasst
                    # genau den Fall "echtes Re-Export-Budget dieser Figur
                    # in dieser Gruppenoperation erschoepft" (nicht HOLD/
                    # ADOPTED/WINDOW_PAUSED, die haben ihre eigene, bereits
                    # bestehende Behandlung).
                    if (
                        record["state"] not in (STATE_HOLD, STATE_ADOPTED, STATE_WINDOW_PAUSED)
                        and save_compatibility_core.latest_compat_export(run_dir, repair_key) is None
                    ):
                        # Nur EINMAL je `repair_key` gebaut (Idempotenz-
                        # Check ueber den bereits vorhandenen, nie
                        # ueberschreibenden Exportspeicher selbst) -- ein
                        # wiederholter Aufruf dieser Funktion (z.B. erneuter
                        # `store.complete_section`-Poll) haeuft sonst
                        # identische Exportversionen fuer unveraendertes
                        # `bound_block` an.
                        # R-SCF-A: `record.get("bound_block")` ist im
                        # Gruppenpfad strukturell IMMER `None` (weder
                        # `load_or_init_record` noch `begin_attempt` erhalten
                        # hier je einen `original_block`-Parameter, anders
                        # als im Einzelfigurpfad) -- `harvested.get(pk)` ist
                        # die tatsaechliche, zuletzt empfangene (wenn auch
                        # nicht akzeptierte) Antwort fuer `pk` und damit die
                        # einzig sinnvolle `best_view`.
                        _write_compat_export_on_exhaustion(
                            run_dir, repair_key=repair_key, participant_id=pk, char_id=char_id,
                            role=ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                            best_view=harvested.get(pk), errors=[],
                            reason="group_attempt_budget_exhausted",
                        )
                    if record["state"] == STATE_ADOPTED and record.get("adopted_block") is not None:
                        # W53-SS7 (CARRY-FORWARD seit W48/W49): dieser
                        # Kandidat wurde in einer frueheren, dann gecrashten
                        # Runde bereits akzeptiert UND die adoptierten
                        # Blockbytes wurden atomar mit state=ADOPTED
                        # persistiert (s. mark_adopted). Ohne dieses
                        # Zurueckspielen wuerde `harvested[pk]` weiterhin den
                        # alten (ungueltigen) Vorabsturz-Stand zeigen und der
                        # bereits akzeptierte Block waere nach einem Absturz
                        # GENAU zwischen `_clear_open_round` und
                        # `store.complete_section` dauerhaft verloren. Kein
                        # neuer Versand, kein `begin_attempt`, `attempts_used`
                        # bleibt unveraendert -- es wird nur der bereits
                        # erledigte Korrekturstand fuer die naechste
                        # `complete_section`-Pruefung sichtbar gemacht.
                        harvested[pk] = record["adopted_block"]
                        restored_from_adopted = True
                    continue
                original_block = harvested.get(pk)
                acceptance = save_correction_domain.evaluate(original_block, char_id)
                candidates.append({
                    "persona_key": pk, "char_id": char_id, "repair_key": repair_key,
                    "acceptance": acceptance, "original_block": original_block,
                    "attempt_no": record["attempts_used"] + 1,
                })

            if not candidates:
                if restored_from_adopted:
                    # Mindestens ein bereits adoptierter Block wurde eben aus
                    # dem Corrector-Metadatum zurueckgespielt -- GENAU DESHALB
                    # jetzt (idempotent, unveraenderter Store) erneut
                    # `complete_section` aufrufen, BEVOR die while-Schleife
                    # terminiert, statt den wiederhergestellten Stand
                    # ungenutzt zu verwerfen (s. Modulkommentar oben).
                    harvest_completion = store.complete_section(
                        lobby, table, section_id, harvested, states_dir, today, harvest_validator, persona_state_store,
                    )
                    continue
                break  # Budget fuer jedes noch fehlende Mitglied erschoepft -- ehrliches HOLD beim Aufrufer

            for c in candidates:
                begin_attempt(run_dir, c["repair_key"])
            round_no = _next_round_no(run_dir, table.table_id, section_id)
            # Marker VOR dem Versand persistieren (Crash-Fenster "vor Send"
            # UND "nach Response vor Checkpoint" werden dadurch identisch
            # behandelt -- beide finden beim Neustart denselben offenen
            # Marker und reichen `send_correction_turn` dieselbe
            # Operationsidentitaet erneut ein, s. Modulkommentar oben).
            _write_open_round(run_dir, table.table_id, section_id, round_no, [
                {"persona_key": c["persona_key"], "char_id": c["char_id"], "original_block": c["original_block"]}
                for c in candidates
            ])

        message = save_correction_domain.build_group_correction_message(
            table_id=table.table_id, section_id=section_id, requests=candidates, max_attempts=max_attempts,
        )
        emit("save_correction_attempt", {
            "section_id": section_id, "table_id": table.table_id,
            "members": [c["persona_key"] for c in candidates], "round": round_no,
        })
        # FIX2 (01-PRODUCT-REVIEW.md "Die tatsaechliche Nachforderung muss
        # in die Ausgabe passen"): mehrere vollstaendige v7-Personal-Saves
        # in EINER Nachricht, aber demselben EINEN konfigurierten Outputbound
        # anzufordern, trunkiert nachweislich (belegter 12.000-Token-Cap,
        # BREACH-Export mitten im JSON abgeschnitten, waehrend MAHLBERG
        # denselben Rahmen bereits verbraucht hatte). Reine Transport-
        # Grenze, GENAU fuer DIESEN Versand (keine Breitenaenderung an
        # `gm_transport.output_limit_tokens` selbst, kein Einfluss auf
        # andere Rollen/Turns): das deklarierte Limit skaliert mit der
        # Mitgliederzahl DIESER Runde, damit der Transport nachweislich
        # genug Raum fuer ALLE angeforderten vollstaendigen Bloecke
        # deklariert -- bei genau EINEM Mitglied (der ueberwiegende Fall,
        # inkl. jedes bestehenden Resume-Tests) bleibt das Verhalten exakt
        # unveraendert (kein Override, `send_correction_turn` faellt auf
        # `gm_transport.output_limit_tokens` zurueck). Ohne ermittelbaren
        # Basiswert (Fake-/Testtransport ohne `output_limit_tokens`) bleibt
        # ebenfalls unveraendert `None` (kein erfundenes Limit).
        base_output_limit = getattr(gm_transport, "output_limit_tokens", None)
        output_limit_override = (
            base_output_limit * len(candidates)
            if base_output_limit is not None and len(candidates) > 1
            else None
        )
        outcome = send_correction_turn(
            run_dir, role=ROLE_GROUP, table_id=table.table_id, section_id=section_id,
            participant=table.leader, turn_idx=round_no, outgoing_text=message,
            gm_transport=gm_transport, table=table, output_limit_tokens_override=output_limit_override,
        )
        if outcome.blocked:
            reason = outcome.reason or "blocked"
            # R12-W73 (Invariante 6): bei einem NACHWEISLICH unversandten
            # Deadline-vor-Versand-Block (Rundenidentitaet = `role=
            # ROLE_GROUP`, `turn_idx=round_no`, `participant=table.leader`
            # -- GENAU die Identitaet, mit der `send_correction_turn` oben
            # aufgerufen wurde) bleiben die offene Runde (`_open_round`-
            # Marker) UND das Mitgliederset ERHALTEN -- NICHT `_clear_open_
            # round`, NICHT terminal `mark_hold`. Der naechste Aufruf nimmt
            # oben (`open_round is not None`-Zweig) denselben `round_no`
            # und dasselbe Mitgliederset wieder auf, OHNE erneutes
            # `begin_attempt` (kein Doppelzaehlen). Idempotent: `mark_
            # window_paused` schreibt nur, wenn `reason` sich aendert.
            if _window.is_pre_send_deadline_reason(reason) and _window.slot_never_sent(
                run_dir, role=ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                turn_idx=round_no, participant=table.leader,
            ):
                for c in candidates:
                    mark_window_paused(run_dir, c["repair_key"], reason=reason)
                emit("save_correction_hold", {
                    "section_id": section_id, "table_id": table.table_id, "reason": reason,
                })
                break
            # P2 (R4-Rundenabschluss): eine sicher beobachtete, vollstaendig
            # verbuchte Kontingent-/Budgetablehnung (`send_correction_turn`
            # erkennt `ProviderQuotaPausedError` getypt, kein Freitext-
            # Substring, s. dort) ist WEDER ein unklarer Versand NOCH ein
            # gewoehnlicher Transportdefekt -- `request_ledger.finish_error`
            # hat den Request bereits abschliessend `accounted` gebucht
            # (Reservierung/Verbrauch bleiben unangetastet, KEIN Refund).
            # Die offene Runde (Mitgliederset + original_block je Figur)
            # bleibt darum ERHALTEN -- NICHT `mark_hold`, NICHT `_clear_
            # open_round`. Ein NEUER `round_no` (reine Request-IDENTITAET,
            # s. `_next_round_no`-Modulkommentar oben -- NICHT das pro-
            # Figur-Korrekturbudget `attempts_used`) macht den naechsten
            # regulaeren Aufruf wieder sendefaehig: `request_ledger.begin`
            # erlaubt einen frischen Request fuer eine bereits `accounted`
            # Identitaet (nur eine OFFENE/nicht-`accounted` Reservierung
            # blockiert `begin`); `begin_attempt` wird hier NICHT erneut
            # aufgerufen -- kein zusaetzlicher Korrekturslot wird verbraucht,
            # keine alte Request-ID/kein alter Verbrauch/kein erfolgreicher
            # Save wird ueberschrieben. Erneutes Werfen (statt nur `break`)
            # laesst diese Pause denselben Pfad erreichen wie eine Quota-
            # Pause im gewoehnlichen Zug/der Pflichtreflexion -- `finalize`/
            # `run_full_section` fangen `ProviderQuotaPausedError` NICHT
            # (nur `_GateBlocked`), sie durchlaeuft ungefangen bis zum
            # bestehenden `except ProviderQuotaPausedError`-Pausenpfad
            # (`ui/tui.py`) -- dieselbe ruhige Spielermeldung wie jede
            # andere Kontingentpause, kein stilles "nicht abgeschlossen".
            if reason.startswith("quota_paused:"):
                new_round_no = _next_round_no(run_dir, table.table_id, section_id)
                _write_open_round(run_dir, table.table_id, section_id, new_round_no, [
                    {"persona_key": c["persona_key"], "char_id": c["char_id"], "original_block": c["original_block"]}
                    for c in candidates
                ])
                emit("save_correction_hold", {
                    "section_id": section_id, "table_id": table.table_id, "reason": reason,
                })
                raise ProviderQuotaPausedError(reason[len("quota_paused:"):])
            for c in candidates:
                mark_hold(run_dir, c["repair_key"], reason=reason)
            _clear_open_round(run_dir, table.table_id, section_id)
            emit("save_correction_hold", {
                "section_id": section_id, "table_id": table.table_id, "reason": reason,
            })
            break

        for c in candidates:
            record_correction_received(run_dir, c["repair_key"], request_id=outcome.request_id)
            # R-SCF-A (02_SAVEVERTRAG.md §A/§E "Fuenfer-Ernte"): dieselbe
            # append-only Rohsicherung wie im Einzelfigurpfad -- JEDES
            # Gruppenmitglied dieser Runde bekommt die EINE empfangene
            # Rundenantwort (`outcome.text`, gemeinsam fuer alle `candidates`
            # dieser Runde) unter der EIGENEN `repair_key`/`char_id`-Bindung
            # archiviert, BEVOR Extraktion/Konfliktpruefung/Adoption
            # stattfindet. Reiner additiver Seiteneffekt.
            save_compatibility_core.archive_raw_response(
                run_dir, repair_key=c["repair_key"], char_id=c["char_id"], section_id=section_id,
                table_id=table.table_id, attempt_no=c["attempt_no"], request_id=outcome.request_id,
                raw_text=outcome.text or "",
            )

        new_saves = harvest_extractor(outcome.text or "", cid_to_pk)
        # G02/SC06 (W54-Fix): der (unveraenderte, injizierbare)
        # `harvest_extractor` selbst bleibt verlustbehaftet ('erster
        # gewinnt' bei gleicher save_id, s. `saves.harvest_from_debrief`)
        # -- diese ZUSAETZLICHE, enge Pruefung sieht die ROHEN,
        # UNDEDUPLIZIERTEN Bloecke JE char_id in GENAU dieser EINEN
        # Antwort (`saves.extract_all_saves_raw`) und verhindert, dass ein
        # von `harvest_extractor` dennoch gelieferter `new_block` fuer eine
        # char_id uebernommen wird, deren Rohbloecke sich WIDERSPRECHEN
        # (gleiche char_id/save_id, ABWEICHENDER Inhalt). Andere, konflikt-
        # freie Mitglieder derselben Antwort bleiben unberuehrt (Gruppen-
        # Personen getrennt).
        raw_blocks_by_char: dict[str, list] = {}
        for blk in zeitriss_saves.extract_all_saves_raw(outcome.text or ""):
            cid = zeitriss_saves.block_char_id(blk)
            if cid:
                raw_blocks_by_char.setdefault(cid, []).append(blk)
        for c in candidates:
            pk = c["persona_key"]
            char_id = c["char_id"]
            new_block = new_saves.get(pk)
            if new_block is None:
                continue  # weiterhin fehlend -- naechste complete_section-Pruefung meldet das erneut
            char_group = raw_blocks_by_char.get(char_id) or []
            char_conflicts = save_correction_domain.find_duplicate_save_ids(char_group) if len(char_group) > 1 else []
            if char_conflicts:
                # Mehrere rohe Bloecke fuer GENAU diese char_id mit
                # ABWEICHENDEM Inhalt -- `new_block` (die Auswahl des
                # unveraenderten `harvest_extractor`) wird NICHT uebernommen
                # (weder adoptiert noch in `harvested` geschrieben). Gleiche
                # Behandlung wie eine sonstige nicht akzeptierte Antwort
                # (s. `else`-Zweig unten): Slot gilt als ausgewertet, aber
                # NICHT terminal -- die naechste Runde (falls Budget
                # verbleibt, geprueft beim naechsten Fresh-Zweig-Eintritt
                # oben) fordert erneut an. Die SL erhaelt dabei die
                # tatsaechliche Mehrdeutigkeitsmeldung statt eines
                # generischen Fehlerkatalogs.
                _reset_for_next_attempt(run_dir, c["repair_key"], errors=[e.message for e in char_conflicts])
                continue
            new_acceptance = save_correction_domain.evaluate(new_block, char_id)
            old_block = c["original_block"]
            if old_block is not None:
                error_paths = {e.path for e in c["acceptance"].structure.errors}
                drift = save_correction_domain.detect_unjustified_drift(old_block, new_block, error_paths)
                if drift:
                    mark_hold(run_dir, c["repair_key"], reason="unjustified_semantic_drift")
                    emit("save_correction_hold", {
                        "section_id": section_id, "table_id": table.table_id,
                        "persona_key": pk, "reason": "unjustified_semantic_drift",
                    })
                    continue  # alten (ungueltigen) Stand NICHT durch die gedriftete Antwort ersetzen
            harvested[pk] = new_block
            if new_acceptance.accepted:
                mark_adopted(run_dir, c["repair_key"], adopted_block=new_block)
            else:
                _reset_for_next_attempt(run_dir, c["repair_key"], errors=new_acceptance.feedback_items)

        # Diese Runde ist jetzt vollstaendig verarbeitet (Antwort durabel
        # UND in harvested/Korrekturdatensaetze uebernommen) -- der Marker
        # wird GENAU HIER geloescht, VOR dem naechsten (bereits bestehenden,
        # idempotenten) `store.complete_section`-Aufruf. Ein Crash WAEHREND
        # `complete_section` selbst faellt in dessen eigene, von W49 nicht
        # beruehrte Idempotenz-Garantie (Plan wird nur bei vollem Erfolg
        # gepinnt) -- kein neuer Transaktionskern noetig.
        _clear_open_round(run_dir, table.table_id, section_id)

        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, states_dir, today, harvest_validator, persona_state_store,
        )

    return harvested, harvest_completion
