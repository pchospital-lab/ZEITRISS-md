#!/usr/bin/env python3
"""
mmo_sim/core/creation_service.py — gemeinsamer Kern des fortsetzbaren
SL-Erschaffungsdialogs (11 §3, M2/A17), genutzt von `ui/tui.py:_cmd_new_or_
switch_character` (Mensch) UND `domain/zeitriss/community_creation.py`
(Persona-getriebene Community-Erstgeneration, P2-Community-Block
2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md §3).

Der GM-Turn-Mechanismus (Admission-Gate FRISCH vor jeder Anfrage,
body-basierte Reservierung, Requestledger-Bindung, v7-Save-Erkennung,
`onboarding.complete_with_save`) ist fuer BEIDE Antwortgeber identisch —
nur WER die naechste Antwort liefert (Mensch per readline, Persona per
admitted Modellrequest ueber einen eigenen Treiber) unterscheidet sich.
Diese Trennung ist die im Community-Auftrag ausdruecklich erlaubte kleine
TUI-Extraktion ("persona-driver ersetzt `_readline`") — der Rest von
`_cmd_new_or_switch_character` (Katalogauswahl, Aktivfiguren-Lock/-Sync,
Publikation) bleibt in `ui/tui.py`, da diese Logik einen bereits
VORHANDENEN Current-Save einer ANDEREN aktiven Figur voraussetzt (Mensch
mit Mehrfigurenwechsel) — bei einer frisch erschaffenen Community-Persona
existiert dafuer strukturell nie ein Vorzustand."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import request_ledger
from .admission import read_admission_block, reservation_for_wire_text
from ..domain.zeitriss import onboarding as onboarding_lib
from ..domain.zeitriss import saves as zeitriss_saves


@dataclass
class ReplyResult:
    """Ergebnis eines einzelnen Antwortversuchs (Mensch ODER Persona) auf
    eine SL-Frage im Erschaffungsdialog.

    `kind`:
      - "answer": `text` ist die naechste an die SL zu sendende Nachricht —
        der Dialog wird fortgesetzt.
      - "paused": Admission-Gate blockiert (Budget/Stop) ODER Persona lehnt
        strukturiert ab — Fortschritt bleibt erhalten, spaeter fortsetzbar,
        KEIN weiterer Modellaufruf fuer DIESE Persona in diesem Versuch.
      - "error": Transport-/Adapterfehler beim Einholen der Antwort — wie
        "paused" behandelt (Dialog bleibt offen), aber mit Fehlerursache."""

    kind: str
    text: str = ""
    reason: str = ""
    # C2 (P2-Community-Kontinuitaet 2026-09-25): die Request-ID des
    # Antwortgeber-Requests (falls einer stattfand, z.B. ein admitted
    # Persona-Treiber-Call) -- `None` fuer den menschlichen Antwortgeber
    # (kein eigener Modellrequest). Dient ausschliesslich der Audit-/
    # Checkpoint-Verknuepfung (`onboarding.record_pending_answer`), keiner
    # neuen Ledger-Logik.
    request_id: str | None = None


@dataclass
class CreationDialogOutcome:
    status: str  # "completed" | "paused" | "error"
    save_block: dict | None = None
    chrononaut_id: str | None = None
    reason: str = ""


def _settle_pending_or_hold(run_dir: str | Path, request_id: str | None) -> bool:
    """A1-Rest (Altformat-Recovery-Nachzug 2026-09-26, MAIN-DATENWEGENTSCHEIDUNG.md
    A1-Rest): dieselbe Settlement-/Unklarheitsentscheidung wie im direkten
    Ledgerweg (s. `request_ledger.find_durable_result`/`settle_received`-
    Docstrings), aber fuer den ZWEITEN Wiederaufnahmeweg -- einen bereits
    lokal gespeicherten `onboarding.pending_step` (`sl_reply`/
    `persona_answer`), der seine verknuepfte Request-ID (`sl_request_id`/
    `persona_request_id`) bisher NICHT auf noch offene Buchung prueft, bevor
    sein Text als erledigte Voraussetzung fuer Cursorfortschritt/
    `complete_with_save`/`record_step` weiterverwendet wird.

    `request_id is None`: menschlicher Antwortgeber (kein eigener
    Modellrequest, s. `ReplyResult.request_id`-Docstring) -- nichts zu
    settlen, nicht blockieren. Ist dagegen eine Request-ID AUSDRUECKLICH
    vorhanden, kennt der Aufrufer bereits einen konkreten Modellauftrag --
    liefert `load_request` dafuer `None` (Datei fehlt/wurde verschoben/
    ein einmaliges ENOENT an der Stat-/exists-Nahtstelle), bedeutet das
    NICHT "kein Modellrecord = menschliche Antwort", sondern "bekannter
    Auftrag, dessen Datensatz gerade nicht verfuegbar ist" (MAIN-
    DATENWEGENTSCHEIDUNG.md, Korrektur der vorigen zu weiten Freigabe).
    Diese Funktion liefert dafuer False (kontrollierbar offen -- kein
    Cursorfortschritt, keine Speicherpublikation, kein abhaengiger
    Folgeaufruf), NICHT True. Der allgemeine `load_request`-Vertrag (None
    NUR fuer eine initial abwesende Datei) bleibt unveraendert; nur diese
    Freigabeentscheidung wird korrigiert. Bereits `accounted` (auch ein
    alter Record ohne `result_text`, test_05): No-op, True. `received`:
    GENAU EINMAL `settle_received` versuchen (idempotent, identischer Weg
    wie `find_durable_result`s `received`-Zweig weiter unten in dieser
    Datei UND `community_creation._persona_get_reply_factory`) -- fehlt
    die urspruengliche Dauer (`received_seconds` abwesend), bleibt der
    Datensatz unveraendert bei `state=received` und diese Funktion liefert
    False (kontrolliert offen, kein Uebergang nach `accounted`, keine
    Schaetzung/Nullbuchung). Jeder andere Zustand (z.B. ein Record, der nie
    ueber `finish_received` gelaufen ist) ist fuer einen bereits lokal
    gespeicherten `pending_step` nicht real erwartbar, wird aber ebenso
    konservativ als kontrolliert offen (False) behandelt statt stillschweigend
    als erledigt durchzugehen. Eine vorhandene, aber unlesbare/nicht
    einordenbare Datei bleibt unveraendert fail-closed: `load_request`
    wirft dafuer `IndeterminateRequestRecordError`, die hier UNGEFANGEN an
    den Aufrufer propagiert (G2)."""
    if request_id is None:
        return True
    record = request_ledger.load_request(run_dir, request_id)
    if record is None:
        return False
    if record.get("state") == "accounted":
        return True
    if record.get("state") == "received":
        record = request_ledger.settle_received(run_dir, record)
        if record.get("state") == "accounted":
            return True
    return False


def run_admitted_creation_dialog(
    *,
    run_dir: str | Path,
    onboarding_dir: str | Path,
    participant_id: str,
    turn_idx_start: int,
    initial_outgoing: str,
    gm_transport,
    get_reply: Callable[[int, str], ReplyResult],
    harvest_validator,
    print_fn: Callable[[str], None] = lambda s: None,
    role: str = "creation_dialog",
    table_id: str | None = None,
    section_id: str | None = None,
) -> CreationDialogOutcome:
    """Treibt EINEN fortsetzbaren SL-Erschaffungsdialog bis zu einem
    gueltigen v7-Save ODER einer kontrollierten Pause/einem Fehler.

    Identisch zum vormaligen Schleifenkoerper in
    `ui/tui.py:_cmd_new_or_switch_character` (E1-E3/A3/R07/I2-Nachzug/G2):
    Admission-Gate wird VOR JEDEM einzelnen GM-Turn frisch von der Platte
    gelesen (kein einmaliger Vorabcheck), body-basierte Reservierung
    (`reservation_for_wire_text`), derselbe reservierte+persistierte
    Requestweg wie jeder andere Modellschritt (`request_ledger.begin`/
    `finish_received`/`finish_error`). `onboarding.record_step` persistiert
    JEDEN Zwischenschritt sofort (Crash-Sicherheit) — ein Abbruch zwischen
    zwei Fragen verliert nur die gerade noch unbeantwortete Frage.

    `get_reply` liefert die naechste Antwort auf die zuletzt empfangene
    SL-Frage — fuer einen Menschen ein simples `self._readline(...)` (kein
    eigener Modellrequest, `EndOfInput` propagiert unveraendert an den
    Aufrufer), fuer eine Persona ein VOLLSTAENDIG admission+ledger
    gebundener Treiber-Call (s. `domain/zeitriss/community_creation.py`).
    `table_id`/`section_id` binden den GM-Turn zusaetzlich an
    Community/Generation (Community-Erstgeneration) bzw. bleiben `None`
    (Menschlicher Erschaffungsdialog, unveraendert wie vor dieser
    Extraktion)."""
    run_dir = Path(run_dir)
    onboarding_dir = Path(onboarding_dir)
    gm_output_limit = getattr(gm_transport, "output_limit_tokens", None)
    gm_route = getattr(gm_transport, "base_url", None)
    turn_idx = turn_idx_start
    outgoing = initial_outgoing
    while True:
        # C2 (P2-Community-Kontinuitaet 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
        # §3): ein bereits empfangener, aber noch nicht in `steps` uebernommener
        # SL-Reply fuer GENAU DIESEN offenen Schritt (`onboarding.pending_step`)
        # wird WIEDERVERWENDET statt erneut angefordert -- ein lokaler Retry
        # nach einem Fehler zwischen "SL-Antwort empfangen" und "Schritt
        # persistiert" darf die bereits abgerechnete SL-Anfrage NICHT
        # wiederholen (02_ABNAHME "SL-Antwort liegt vor, Persona fehlt").
        pending = onboarding_lib.peek(onboarding_dir, participant_id)
        pending_step = pending.pending_step if pending is not None else None
        if pending_step is not None and pending_step.get("sl_reply") is not None:
            sl_text = pending_step["sl_reply"]
            print_fn(
                f"[SL] {sl_text} (wiederaufgenommen aus bereits erhaltenem Ergebnis -- "
                "kein erneuter SL-Request)"
            )
            # A1-Rest (Altformat-Recovery-Nachzug 2026-09-26,
            # MAIN-DATENWEGENTSCHEIDUNG.md A1-Rest): dieser gespeicherte
            # `sl_reply` traegt dieselbe Request-ID (`sl_request_id`), die
            # ein direkt aus dem Ledger gefundener Treffer (Zweig oben)
            # bereits vor Weiterverwendung settlen/blockieren muss. VOR dem
            # gemeinsamen `extract_all_saves`/`complete_with_save`-Weg
            # unten geprueft -- deckt sowohl den Fall ab, dass `sl_text`
            # hier noch eine gewoehnliche Zwischenfrage ist (Cursor
            # rueckt unten zur Personaantwort vor), als auch den Erstsavefall
            # (unten direkt `complete_with_save`).
            if not _settle_pending_or_hold(run_dir, pending_step.get("sl_request_id")):
                print_fn(
                    "Erschaffungsdialog blockiert (Altformat-Recovery: Requestautoritaet der "
                    "bereits gespeicherten SL-Antwort nicht gesichert -- Datensatz nicht "
                    "verfuegbar oder Originaldauer unbekannt) — kein Cursorfortschritt, "
                    "keine Speicherpublikation, Fortschritt bleibt erhalten, spaeter "
                    "fortsetzbar."
                )
                return CreationDialogOutcome(
                    status="paused", reason="altformat_unresolved_pending_settlement",
                )
        else:
            # C2 (P2-Community-Ergebnisuebergabe 2026-09-25,
            # MAIN-DATENWEGENTSCHEIDUNG.md §3): der lokale `pending_step` kennt
            # diesen Schritt (noch) nicht -- das kann ENTWEDER ein wirklich
            # neuer Schritt sein ODER ein bereits durabel abgerechneter Schritt,
            # dessen lokaler Checkpoint-Write (`record_pending_reply`) danach
            # an einem gewoehnlichen `OSError` gescheitert ist. Vor jeder neuen
            # Reservierung/jedem neuen Versand wird deshalb ZUERST der
            # dauerhafte Ledger-Datensatz fuer GENAU DIESE Operationsidentitaet
            # geprueft -- nur wenn dort NICHTS bereits empfangen wurde, folgt
            # ein echter neuer Modellaufruf.
            recovered = request_ledger.find_durable_result(
                run_dir, table_id=table_id, section_id=section_id, role=role,
                turn_idx=turn_idx, participant=participant_id,
            )
            if recovered is not None:
                # R1 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
                # §3): ein `received`-Treffer traegt zwar bereits den
                # empfangenen Text, aber seine Kosten-/Latenznachbuchung kann
                # noch offen sein (s. `request_ledger.finish_received`s
                # G3-Fix/R1-Fix). GENAU EINMAL nachholen, BEVOR dieser Text
                # als erledigte Voraussetzung fuer den naechsten Schritt
                # behandelt wird -- schlaegt das fehl, propagiert die
                # Ausnahme UNGEFANGEN (kontrolliert offen, kein `completed`
                # mit still ausgelassener Buchung). Ein `accounted`-Treffer
                # bleibt ein reiner No-op (s. `settle_received`-Docstring).
                if recovered.get("state") == "received":
                    recovered = request_ledger.settle_received(run_dir, recovered)
                    # A1 (Altformat-Recovery-Nachzug 2026-09-25,
                    # MAIN-DATENWEGENTSCHEIDUNG.md A1): `settle_received`
                    # transitioniert NICHT nach `accounted`, wenn die
                    # Originaldauer unbekannt ist (Schluessel `received_seconds`
                    # abwesend, Altrecord vor R1). Kein `completed`/
                    # `already_ready`, kein abhaengiger Modellaufruf -- der
                    # Dialog bleibt kontrolliert offen, Cursor rueckt NICHT vor.
                    if recovered.get("state") != "accounted":
                        print_fn(
                            "Erschaffungsdialog blockiert (Altformat-Recovery: Originaldauer "
                            "der bereits empfangenen SL-Antwort unbekannt) — kein weiterer "
                            "Modellaufruf, Fortschritt bleibt erhalten, spaeter fortsetzbar."
                        )
                        return CreationDialogOutcome(
                            status="paused", reason="altformat_unresolved_received_seconds",
                        )
                sl_text = recovered["result_text"]
                print_fn(
                    f"[SL] {sl_text} (durabel aus dem Requestledger wiederhergestellt -- "
                    "lokaler Checkpoint-Write war zuvor fehlgeschlagen, kein erneuter SL-Request)"
                )
                onboarding_lib.record_pending_reply(
                    onboarding_dir, participant_id, sl_reply=sl_text, sl_request_id=recovered["id"],
                )
            else:
                # A2 (Altformat-Recovery-Nachzug 2026-09-25,
                # MAIN-DATENWEGENTSCHEIDUNG.md A2): `find_durable_result`
                # fand keinen Treffer -- das kann ENTWEDER ein wirklich neuer
                # Schritt sein ODER ein Alt-Record, der zwar bereits
                # erfolgreich gesendet+verbucht wurde, aber nie einen Text
                # persistiert hat (10024452-Stand). Der lokale Checkpoint
                # (`pending_step.sl_reply`) wurde oben bereits als leer
                # geprueft -- ohne diesen Check wuerde eine bereits
                # beantwortete Operation blind ein zweites Mal angefragt.
                answered_without_text = request_ledger.find_answered_without_text(
                    run_dir, table_id=table_id, section_id=section_id, role=role,
                    turn_idx=turn_idx, participant=participant_id,
                )
                if answered_without_text is not None:
                    print_fn(
                        "Erschaffungsdialog blockiert (Altformat-Recovery: bereits gesendete "
                        "SL-Anfrage ohne erhaltenen Text) — keine neue Anfrage, Fortschritt "
                        "bleibt erhalten, spaeter fortsetzbar."
                    )
                    return CreationDialogOutcome(
                        status="paused", reason="altformat_unresolved_missing_result_text",
                    )
                gm_reserved = reservation_for_wire_text(outgoing, output_limit_tokens=gm_output_limit)
                blocked, reason = read_admission_block(
                    run_dir, reserved_usd=gm_reserved,
                    output_bound_known=(gm_output_limit is not None), route=gm_route,
                )
                if blocked:
                    print_fn(
                        f"Erschaffungsdialog blockiert (Admission-Gate: {reason}) — kein weiterer "
                        "Modellaufruf, Fortschritt bleibt erhalten, spaeter fortsetzbar."
                    )
                    return CreationDialogOutcome(status="paused", reason=str(reason))
                request_id = request_ledger.begin(
                    run_dir, role=role, content=outgoing, reserved_usd=gm_reserved,
                    route=gm_route, output_limit_tokens=gm_output_limit,
                    turn_idx=turn_idx, participant=participant_id,
                    table_id=table_id, section_id=section_id,
                )
                t0 = time.monotonic()
                try:
                    if gm_output_limit is not None:
                        result = gm_transport.turn(turn_idx, outgoing, output_limit_tokens=gm_output_limit)
                    else:
                        result = gm_transport.turn(turn_idx, outgoing)
                except Exception as e:
                    request_ledger.finish_error(run_dir, request_id, error=e, seconds=time.monotonic() - t0)
                    print_fn(f"Erschaffungsdialog: SL-Anfrage fehlgeschlagen ({e}) — Fortschritt bleibt erhalten, spaeter fortsetzbar.")
                    return CreationDialogOutcome(status="error", reason=str(e))
                sl_text = result.get("content", "")
                # C2: der empfangene Text wird BEREITS HIER (im selben
                # atomaren Requestledger-Write, der `state=accounted` setzt)
                # dauerhaft an diese Operationsidentitaet gebunden -- BEVOR
                # der separate lokale Checkpoint-Write (unten) versucht wird
                # und ggf. fehlschlaegt (s. `request_ledger.finish_received`/
                # `find_durable_result` Docstrings).
                request_ledger.finish_received(
                    run_dir, request_id, usage=result.get("usage"), seconds=time.monotonic() - t0,
                    result_text=sl_text,
                )
                print_fn(f"[SL] {sl_text}")
                # SOFORT persistieren -- BEVOR die Personaantwort eingeholt
                # wird (der naechste, ggf. teure/fehlschlagende Schritt). Ein
                # OSError GENAU hier verliert NICHT mehr den Text (s.o.) --
                # ein Folgeprozess erreicht den `recovered`-Zweig oben.
                onboarding_lib.record_pending_reply(
                    onboarding_dir, participant_id, sl_reply=sl_text, sl_request_id=request_id,
                )
        save_blocks = zeitriss_saves.extract_all_saves(sl_text)
        candidate_char_id = zeitriss_saves.block_char_id(save_blocks[0]) if save_blocks else None
        if save_blocks and candidate_char_id is not None:
            try:
                onboarding_lib.complete_with_save(
                    onboarding_dir, participant_id, save_blocks[0],
                    harvest_validator, candidate_char_id,
                )
            except ValueError as e:
                print_fn(f"SL-Erschaffungsergebnis ungueltig ({e}) — Dialog bleibt offen, keine Uebernahme.")
                return CreationDialogOutcome(status="error", reason=str(e))
            return CreationDialogOutcome(
                status="completed", save_block=save_blocks[0], chrononaut_id=candidate_char_id,
            )
        if pending_step is not None and pending_step.get("persona_answer") is not None:
            reply_text = pending_step["persona_answer"]
            # A1-Rest (Altformat-Recovery-Nachzug 2026-09-26,
            # MAIN-DATENWEGENTSCHEIDUNG.md A1-Rest): symmetrisch zum
            # SL/Erstsave-Guard oben -- die gespeicherte Personaantwort
            # traegt dieselbe `persona_request_id`, die vor `record_step()`
            # (dem naechsten Cursorfortschritt) dieselbe Settlement-
            # Voraussetzung wie der direkte Ledgerweg erfuellen muss.
            # `persona_request_id is None` (menschlicher Antwortgeber) wird
            # von `_settle_pending_or_hold` selbst nicht blockiert (n-Pfad
            # erhalten).
            if not _settle_pending_or_hold(run_dir, pending_step.get("persona_request_id")):
                print_fn(
                    "Erschaffungsdialog blockiert (Altformat-Recovery: Requestautoritaet der "
                    "bereits gespeicherten Personaantwort nicht gesichert -- Datensatz nicht "
                    "verfuegbar oder Originaldauer unbekannt) — kein Cursorfortschritt, "
                    "Fortschritt bleibt erhalten, spaeter fortsetzbar."
                )
                return CreationDialogOutcome(
                    status="paused", reason="altformat_unresolved_pending_settlement",
                )
        else:
            reply = get_reply(turn_idx, sl_text)
            if reply.kind != "answer":
                return CreationDialogOutcome(status=reply.kind, reason=reply.reason)
            # C2: SOFORT persistieren -- BEVOR `record_step()` (der
            # abschliessende Schritt-Write, der auch fehlschlagen kann)
            # aufgerufen wird.
            onboarding_lib.record_pending_answer(
                onboarding_dir, participant_id,
                persona_answer=reply.text, persona_request_id=reply.request_id,
            )
            reply_text = reply.text
        onboarding_lib.record_step(onboarding_dir, participant_id, sl_text, reply_text)
        turn_idx += 1
        outgoing = reply_text
