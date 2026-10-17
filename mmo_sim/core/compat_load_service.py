#!/usr/bin/env python3
"""
mmo_sim/core/compat_load_service.py — reale SL-gestuetzte Reparatur fuer
NICHT-Wallet-Strukturfehler im Kompatibilitaetsladeweg (ZR-SCF-HYBRID-
DURCHSTICH-20261017-R1, Fix A, 02_KONKRETER_DURCHSTICH.md §A).

`core.save_compatibility.attempt_compat_load`s `repair_fn` kannte bisher NUR
`ui.tui._apply_pending_compat_load`s alte `_offline_repair` (reine, lokale
Wallet-Projektion — 02.B, KEIN Modellaufruf). Dieser Dienst liefert eine
ZWEITE `repair_fn`-Fabrik, `build_compat_repair_fn(...)`, die DENSELBEN
request-gebundenen SL-Transportweg wie `core.save_correction.
send_correction_turn` benutzt — Admission-Gate (`core.admission.
read_admission_block`) VOR JEDER physischen Anfrage, `request_ledger.
begin`/`finish_received`/`finish_error` (EIN Transportversuch, kein
verstecktes Resend), Rohsicherung ueber das bereits vorhandene
`save_compatibility.archive_raw_response` (02.C). KEIN neuer Transport-/
Ledger-/Admissionpfad — nur Wiederverwendung der bereits bestehenden
Bausteine, exakt wie CONTROL.json es fuer dieses optionale Modul vorsieht
("vorhandene Ledgerfunktionen BENUTZEN, deren Modul NICHT aendern").

Reihenfolge je Reparaturrunde (billigste/risikoärmste Stufe zuerst,
02_KONKRETER_DURCHSTICH.md §A "eindeutige wertgleiche Projektion bleibt
lokal zulaessig, ohne unnoetige Modellkosten"):
  1. lokale, wertgleiche Wallet-Projektion (`domain.save_compatibility.
     project_wallets_in_block`) — hilft sie, KEIN Modellaufruf.
  2. sonst (das ist die in diesem Fix neue Bruecke): EIN echter SL-Request
     an den tatsaechlich konfigurierten Transport (`gm_transport` — dasselbe
     Objekt, das der Aufrufer fuer jeden anderen echten GM-Turn benutzt)
     mit den konkreten Validatorhinweisen (`open_issues`), ueber dieselbe
     Nachrichtenform wie `domain.save_correction.build_correction_message`
     (01_AUFTRAG_SAVEGATE.md §C-Vertrag — NICHT neu erfunden).

Dieses Modul traegt KEIN eigenes Rundenbudget — der bereits bestehende,
aeussere Zaehler (`save_compatibility.MAX_COMPAT_LOAD_REPAIR_ATTEMPTS`/
`load_or_init_compat_load_record`, `attempts_used`) bleibt die EINZIGE
Autoritaet fuer "wie viele Reparaturrunden insgesamt" — exakt dieselbe
Zaehlung wie zuvor fuer die reine Wallet-Projektion, getrennt von
`save_correction.MAX_ADDITIONAL_REQUESTS` (01_AUFTRAG_SAVEGATE.md §C,
"drei zusaetzliche Save-Neuausgaben und begrenzte Lade-Reparatur getrennt
zaehlen"). Budget/Zeit/Stop (`read_admission_block`) werden VOR jeder
physischen Anfrage geprueft, NICHT erst danach; ein blockierter Versuch
liefert `None` zurueck — der aeussere Ladeweg haelt dann kontrolliert
`status="hold"`, exakt wie "keine Verbesserung moeglich". KEIN stiller
Zweitversand bei unklarem Ausgang: war fuer GENAU diese Reparaturrunde
bereits ein Request unterwegs/beantwortet (aber ohne auffindbaren Text),
liefert diese Funktion ebenfalls `None`, NIEMALS einen zweiten physischen
Request fuer dieselbe Runde."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from . import request_ledger
from . import save_compatibility as save_compat_core
from .admission import read_admission_block, reservation_for_wire_text
from ..domain.zeitriss import save_compatibility as save_compatibility_domain
from ..domain.zeitriss import save_correction as save_correction_domain
from ..domain.zeitriss import save_validation as save_validation_lib

#: dedizierte Operationsidentitaet (vgl. `core.save_correction.
#: send_correction_turn`-Docstring: "dedizierte Korrekturrolle/-
#: Operationsidentitaet verhindert Verwechslung mit gm_turn/
#: persona_decision") — eigener Name, NIE `save_correction.ROLE_*`
#: wiederverwenden: eigene Request-Bindung, getrennt von der laufenden
#: save_correction-Schleife UND vom Erschaffungsdialog.
ROLE_COMPAT_LOAD = "save_compat_load_repair"


def build_compat_repair_fn(
    run_dir: str | Path,
    *,
    repair_key: str,
    char_id: str,
    participant_id: str,
    gm_transport: object | None,
    table_id: str | None = None,
    section_id: str | None = None,
    role: str = ROLE_COMPAT_LOAD,
    max_attempts: int = save_compat_core.MAX_COMPAT_LOAD_REPAIR_ATTEMPTS,
) -> Callable[[dict, list], dict | None]:
    """Liefert `repair_fn(candidate, open_issues) -> dict | None` fuer
    `core.save_compatibility.attempt_compat_load`. `gm_transport` ist das
    bereits vom Aufrufer (normaler Produktweg, `TuiSession.
    gm_transport_factory`, identisch fuer TUI UND Headless-/Hybridpfad)
    konfigurierte Transportobjekt — `None` bedeutet "keine SL-Anbindung in
    diesem Lauf konfiguriert" (Offline-Paket/Test ohne Env); die
    zurueckgegebene Funktion versucht dann NUR die lokale Wallet-Projektion
    und liefert sonst `None` — identisches Verhalten zur alten
    `_offline_repair`, KEIN stiller Versuch, eine nicht konfigurierte
    SL anzusprechen."""

    def _repair(candidate: dict, open_issues: list) -> dict | None:
        projection = save_compatibility_domain.project_wallets_in_block(candidate)
        if projection.changed:
            return projection.canonical_candidate
        if gm_transport is None:
            return None
        return _sl_backed_repair(
            run_dir, repair_key=repair_key, char_id=char_id, participant_id=participant_id,
            gm_transport=gm_transport, table_id=table_id, section_id=section_id, role=role,
            max_attempts=max_attempts, candidate=candidate, open_issues=open_issues,
        )

    return _repair


def _sl_backed_repair(
    run_dir: str | Path,
    *,
    repair_key: str,
    char_id: str,
    participant_id: str,
    gm_transport: object,
    table_id: str | None,
    section_id: str | None,
    role: str,
    max_attempts: int,
    candidate: dict,
    open_issues: list,
) -> dict | None:
    """Der eigentliche request-gebundene SL-Aufruf — bewusst derselbe
    Ablauf wie `core.save_correction.send_correction_turn` (crash-sichere
    Wiederaufnahme ZUERST, dann Admission-Gate, dann `request_ledger.
    begin`, dann GENAU EIN Transportversuch, dann `finish_received`/
    `finish_error`), nur ohne Tisch/Leader-Weg (der Kompatibilitaetsladeweg
    laeuft je Persona, nicht je Gruppe — `table=None`-Zweig von
    `send_correction_turn`, direkter `gm_transport.turn()`-Aufruf)."""
    # `attempt_compat_load` erhoeht `attempts_used` BEREITS, BEVOR es
    # `repair_fn` aufruft (core/save_compatibility.py: `rounds_used += 1`
    # vor dem `repair_fn(...)`-Call) — der hier gelesene Record traegt den
    # fuer DIESE Runde bereits gueltigen, persistierten Stand. Diese
    # Funktion fuehrt dadurch KEINE eigene zweite Rundenzaehlung.
    record = save_compat_core.load_or_init_compat_load_record(run_dir, repair_key)
    attempt_no = max(int(record.get("attempts_used") or 0), 1)
    # EINDEUTIGE turn_idx je Reparaturrunde DIESES repair_key — kollidiert
    # nicht mit gm_turn/save_correction (eigene `role`=ROLE_COMPAT_LOAD).
    turn_idx = attempt_no

    structure = save_validation_lib.StructureReport(valid=False, errors=[], total_error_count=0, truncated=False)
    binding = [save_validation_lib.BindingError("compat_load_open_issue", item) for item in open_issues]
    acceptance = save_validation_lib.AcceptanceResult(accepted=False, structure=structure, binding_errors=binding)
    outgoing_text = save_correction_domain.build_correction_message(
        persona_key=participant_id, char_id=char_id, operation_label=role,
        acceptance=acceptance, original_block=candidate, attempt_no=attempt_no, max_attempts=max_attempts,
    )

    recovered = request_ledger.find_durable_result(
        run_dir, table_id=table_id, section_id=section_id, role=role, turn_idx=turn_idx, participant=participant_id,
    )
    if recovered is not None:
        if recovered.get("state") == "received":
            recovered = request_ledger.settle_received(run_dir, recovered)
            if recovered.get("state") != "accounted":
                return None  # zweiter Buchungswrite unvollstaendig -- kein Zweitversand, kontrolliertes HOLD oben.
        raw_text = recovered["result_text"]
        request_id = recovered["id"]
    else:
        answered_without_text = request_ledger.find_answered_without_text(
            run_dir, table_id=table_id, section_id=section_id, role=role, turn_idx=turn_idx, participant=participant_id,
        )
        if answered_without_text is not None:
            return None  # bereits versandt/abgerechnet, Text nicht (mehr) auffindbar -- kein stilles Resend bei unklarem Ausgang.

        gm_output_limit = getattr(gm_transport, "output_limit_tokens", None)
        gm_route = getattr(gm_transport, "base_url", None)
        reserved = reservation_for_wire_text(outgoing_text, output_limit_tokens=gm_output_limit)
        blocked, _reason = read_admission_block(
            run_dir, reserved_usd=reserved, output_bound_known=(gm_output_limit is not None), route=gm_route,
        )
        if blocked:
            return None  # Budget/Zeit/Stop VOR jeder physischen Anfrage -- kein Call, kontrolliertes HOLD oben.

        try:
            request_id = request_ledger.begin(
                run_dir, role=role, content=outgoing_text, reserved_usd=reserved, route=gm_route,
                output_limit_tokens=gm_output_limit, turn_idx=turn_idx, participant=participant_id,
                table_id=table_id, section_id=section_id,
            )
        except request_ledger.OpenReservationExistsError:
            return None  # unklarer Versand in flight fuer GENAU diese Runde -- kein zweiter Request.

        t0 = time.monotonic()
        try:
            if gm_output_limit is not None:
                result = gm_transport.turn(turn_idx, outgoing_text, output_limit_tokens=gm_output_limit)
            else:
                result = gm_transport.turn(turn_idx, outgoing_text)
        except Exception as exc:
            request_ledger.finish_error(run_dir, request_id, error=exc, seconds=time.monotonic() - t0)
            return None  # EIN Transportversuch -- kein verstecktes Retry; die aeussere Runde ist bereits verbraucht.

        raw_text = result.get("content", "")
        request_ledger.finish_received(
            run_dir, request_id, usage=result.get("usage"), seconds=time.monotonic() - t0, result_text=raw_text,
        )

    # 02.C: JEDE rohe SL-Antwort einer Korrekturoperation wird append-only
    # gesichert -- unabhaengig davon, ob sie unten als Kandidat akzeptiert/
    # verworfen/mehrdeutig eingestuft wird.
    save_compat_core.archive_raw_response(
        run_dir, repair_key=repair_key, char_id=char_id, section_id=section_id, table_id=table_id,
        attempt_no=attempt_no, request_id=request_id, raw_text=raw_text,
    )

    extracted, conflicts = save_correction_domain.extract_checked_single(raw_text, char_id)
    if extracted is None or conflicts:
        return None  # kein eindeutiger Block -- kontrolliertes HOLD statt Raten (mehrdeutige Identitaet/Geld/Inventar nicht annehmen).
    return extracted
