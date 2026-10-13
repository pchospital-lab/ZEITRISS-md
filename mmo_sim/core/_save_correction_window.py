#!/usr/bin/env python3
"""
mmo_sim/core/_save_correction_window.py — R12 D-HOLD Pre-Send-Window-Resume
(W73-Slice, eng begrenzter Core-Helfer zu `save_correction.py`).

Reine, read-only Hilfsfunktionen gegen den bestehenden Request-Ledger (KEIN
eigener Schreibzugriff, KEIN neuer Produktzustand hier) -- entscheiden, ob
ein HOLD-/WINDOW_PAUSED-Korrekturdatensatz NACHWEISLICH an genau der
Admission-Deadline VOR jedem Versand blockiert wurde (nicht an irgendeinem
anderen `admission_blocked:`-Grund, nicht an Stop/Budget/Transport/Drift)
UND der zugehoerige Slot (Tisch/Abschnitt/Rolle/Turn/Teilnehmer-Identitaet,
s. `request_ledger._operation_identity`) tatsaechlich NIE einen
Requestdatensatz bekommen hat -- NUR dann ist ein regulaerer Resume im
GLEICHEN Slot sicher (01_AUFTRAG_SAVEGATE.md §C/§D, R12-W73-BRIEF.md
Invarianten 1/3)."""
from __future__ import annotations

from pathlib import Path

from . import request_ledger

PRE_SEND_DEADLINE_MARKER = "reale Laufzeitgrenze (Wall-Clock) erreicht (Deadline"


def is_pre_send_deadline_reason(reason: str | None) -> bool:
    """Invariante 1 (R12-W73-BRIEF.md): NUR der exakte Deadline-vor-Versand-
    Fall ist resumierbar -- `reason.startswith("admission_blocked:")` UND
    der EXAKTE Marker-Text ist enthalten (KEINE pauschale Textsuche nach
    `admission_blocked:` allein, KEINE Textsuche nach `stop`). Jede andere
    terminale Kategorie (Stop/Lab-Budget, max_turns/max_seconds/max_usd,
    transport_error, unclear_sent_in_flight, altformat_unresolved_*,
    unjustified_semantic_drift, attempt_budget_exhausted, adopted_*) bleibt
    dadurch unberuehrt terminal -- s. `save_correction.pursue_single_figure_
    correction`/`pursue_group_save_correction`, die diese Funktion VOR jeder
    Resume-Entscheidung aufrufen."""
    if not isinstance(reason, str):
        return False
    if not reason.startswith("admission_blocked:"):
        return False
    return PRE_SEND_DEADLINE_MARKER in reason


def _slot_resume_classification(
    run_dir: str | Path, *, role: str, table_id: str | None, section_id: str | None,
    turn_idx: int | None, participant: str | None,
) -> str:
    """R12-W74 (F01a/F01b-Nachzug): EINE gemeinsame, vollstaendige
    Ledger-Klassifikation einer Operationsidentitaet fuer GENAU drei
    moegliche Ausgaenge:

      - `"durable"`: ein bereits durabler ERFOLG (`request_ledger.
        find_durable_result` liefert einen Treffer -- `state in (received,
        accounted)`, `error is None`, `result_text` gesetzt) liegt fuer
        diese Identitaet vor. Der Slot wurde TATSAECHLICH versandt UND
        beantwortet -- ein Resume darf hier regulaer weiterlaufen: der
        naechste `send_correction_turn`-Aufruf findet GENAU diesen Treffer
        selbst wieder (dessen eigener `find_durable_result`-Check steht VOR
        jedem Admission-/Versandversuch) und liefert ihn OHNE zweiten POST
        zurueck (F01a).
      - `"never_sent"`: KEIN Requestdatensatz (in IRGENDEINEM Zustand) ist
        fuer diese Identitaet in `request_ledger._all_records` auffindbar --
        der Slot wurde nachweislich nie versandt, ein Resume darf einen
        frischen Versand ausloesen.
      - `"terminal"`: jeder andere Fund (eine offene/unklare Reservierung,
        ein bereits `accounted` Datensatz MIT `error`, ein beantworteter
        Datensatz ohne Text, oder ein nicht lesbarer/einordenbarer
        Datensatz -- `request_ledger.IndeterminateRequestRecordError`) --
        der Slot gilt NICHT als nie-versandt, ABER auch nicht als durabler
        Erfolg. Insbesondere ein `finish_error()`-Datensatz (`state=
        accounted`, `error` gesetzt) ist fuer `find_durable_result`/
        `find_answered_without_text` beide bewusst UNSICHTBAR (beide
        verlangen `error is None`) und faellt deshalb NIE in `open_requests`
        (nur nicht-`accounted` Datensaetze) -- ohne den zusaetzlichen
        Volltextscan ueber `_all_records` waere ein solcher Slot faelschlich
        `"never_sent"` und ein Resume wuerde ihn ein ZWEITES Mal versenden
        (F01b: zwei `accounted`-Requestdatensaetze fuer denselben `turn_idx`,
        `attempts_used` bleibt bei 1). Fail-closed bei Unbestimmbarkeit."""
    identity = (table_id, section_id, role, turn_idx, participant)
    try:
        if request_ledger.find_durable_result(
            run_dir, table_id=table_id, section_id=section_id, role=role,
            turn_idx=turn_idx, participant=participant,
        ) is not None:
            return "durable"
        for existing in request_ledger._all_records(run_dir):
            if request_ledger._operation_identity(existing) == identity:
                return "terminal"
    except request_ledger.IndeterminateRequestRecordError:
        return "terminal"
    return "never_sent"


def slot_never_sent(
    run_dir: str | Path, *, role: str, table_id: str | None, section_id: str | None,
    turn_idx: int | None, participant: str | None,
) -> bool:
    """Invariante 3 (R12-W73-BRIEF.md) UNVERAENDERT im Namen/Signatur (vom
    Gruppenpfad UND von Bestandstests, z.B. `test_r12_window_hold_single_
    figure.py` Fall (d), DIREKT aufgerufen) -- liefert jetzt `True` GENAU
    dann, wenn `_slot_resume_classification` `"never_sent"` ermittelt (s.
    dort fuer die volle, jetzt UM den F01b-Fall (`accounted` MIT `error`)
    erweiterte Begruendung). `last_request_id is None` allein beweist
    weiterhin NICHT Abwesenheit (eine FRUEHERE, zwischen `begin()` und
    `finish_received()`/`finish_error()` abgebrochene Prozessinstanz
    hinterlaesst einen offenen Datensatz, den `_slot_resume_classification`
    ueber den Volltextscan weiterhin als `"terminal"` (NICHT `"never_sent"`)
    erkennt)."""
    return _slot_resume_classification(
        run_dir, role=role, table_id=table_id, section_id=section_id,
        turn_idx=turn_idx, participant=participant,
    ) == "never_sent"


def slot_resumable(
    run_dir: str | Path, *, role: str, table_id: str | None, section_id: str | None,
    turn_idx: int | None, participant: str | None,
) -> bool:
    """R12-W74 (F01a-Fix): `True`, wenn der Slot ENTWEDER nachweislich nie
    versandt wurde (`"never_sent"`) ODER bereits ein durabler Erfolg dafuer
    vorliegt (`"durable"`) -- beide Faelle duerfen regulaer in
    `send_correction_turn` weiterlaufen (jener Aufruf selbst entscheidet
    dann, ob er frisch versendet ODER den durablen Treffer wiederverwendet).
    Jeder `"terminal"`-Fund (offene/unklare Reservierung, `accounted` MIT
    `error`, beantwortet ohne Text) bleibt NICHT resumierbar (F01b)."""
    return _slot_resume_classification(
        run_dir, role=role, table_id=table_id, section_id=section_id,
        turn_idx=turn_idx, participant=participant,
    ) in ("never_sent", "durable")


def is_resumable_pre_send_pause(run_dir: str | Path, record: dict) -> bool:
    """Invarianten 1/2/3/4 (R12-W73-BRIEF.md) kombiniert, auf Basis der
    bereits persistierten Datensatzfelder (`operation_key`/`table_id`/
    `section_id`/`persona_key`/`attempts_used`) -- gilt GENAUSO fuer einen
    bereits VOR diesem Fix gespeicherten Legacy-HOLD (Invariante 2: Legacy-D
    ueber normale Produktlogik, KEINE hardcodierte Figurenliste) wie fuer
    einen neu von `save_correction.mark_window_paused` gesetzten Datensatz.

    `record.get("state")` wird bewusst gegen die rohen Zustandsstrings
    `"hold"`/`"window_paused"` geprueft statt gegen importierte Konstanten
    aus `save_correction` -- dieses Modul wird von `save_correction`
    importiert, ein Rueckimport wuerde einen Zirkelbezug erzeugen; die
    Stringwerte sind Teil des bereits persistierten Datenschemas und damit
    ohnehin stabil.

    R12-W74 (F01c-Fix): KEIN eigener `last_request_id is not None`-Check
    mehr HIER -- `last_request_id` zeigt nach einem bereits ausgewerteten,
    ungueltigen Slot1 (`_reset_for_next_attempt` -> `begin_attempt` fuer
    Slot2) weiterhin auf SLOT1s Request-ID, obwohl Slot2 (der AKTUELLE
    `attempts_used`-Stand) nachweislich NIE versandt wurde -- ein pauschaler
    Nicht-Null-Check sperrte diesen legitimen Slot2-Resume faelschlich. Die
    Entscheidung haengt stattdessen AUSSCHLIESSLICH an der VOLLEN
    Ledger-Identitaetspruefung fuer `turn_idx=attempts_used` (`slot_
    resumable` -- Invariante 3), NICHT an null/nicht-null von
    `last_request_id`.

    `turn_idx` fuer die Ledger-Abwesenheitspruefung ist `attempts_used` --
    das gilt NUR fuer den Einzelfigur-/Erschaffungspfad (`send_correction_
    turn` wird dort IMMER mit `turn_idx=attempt_no==attempts_used`
    aufgerufen). Der Gruppenpfad verwendet eine GETRENNTE Rundenidentitaet
    (`turn_idx=round_no`, NICHT `attempts_used`) und ruft deshalb `slot_
    never_sent` direkt mit der Rundenidentitaet auf (s. `save_correction.
    pursue_group_save_correction`), statt diese Funktion zu verwenden.

    R12-W75 (F02-SHAPE-Nachzug): `attempts_used` wird hier NUR auf einen
    gueltigen UNTEREN Rand (`>= 1`, echter `int`, `bool` AUSGESCHLOSSEN --
    ein `bool` ist in Python ein `int`-Subtyp, `True < 1` ist `False` und
    wuerde sonst faelschlich als gueltig durchgehen) geprueft -- ein
    pauschal falsch typisierter Wert (z.B. ein String) wuerde die blanke
    `< 1`-Vergleichsoperation sonst mit einem ungefangenen `TypeError`
    abbrechen lassen, STATT kontrolliert `False` (= nicht resumierbar) zu
    liefern. Der OBERE Rand (`<= max_attempts`, kein offener Slot `4` o.ae.)
    wird bewusst NICHT hier, sondern erst in `save_correction.pursue_
    single_figure_correction`s eigenem SHAPE-Check geprueft (DORT ist
    `max_attempts` als Parameter bekannt, HIER nicht)."""
    if record.get("state") not in ("hold", "window_paused"):
        return False
    if not is_pre_send_deadline_reason(record.get("last_reason")):
        return False
    attempts_used = record.get("attempts_used", 0)
    if not isinstance(attempts_used, int) or isinstance(attempts_used, bool) or attempts_used < 1:
        return False
    return slot_resumable(
        run_dir, role=record.get("operation_key"), table_id=record.get("table_id"),
        section_id=record.get("section_id"), turn_idx=record.get("attempts_used"),
        participant=record.get("persona_key"),
    )
