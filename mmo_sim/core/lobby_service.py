#!/usr/bin/env python3
"""
mmo_sim/core/lobby_service.py — kleiner wiederverwendbarer Lobby-/Offer-Dienst
zwischen UI und bestehenden Primitiven (01_AUFTRAG_LOBBY_INITIATIVE.md §3/§4
A-E, MAIN-DATENWEGENTSCHEIDUNG.md Boundary-Map).

Extrahiert die Offer-/Consent-/Einladungs-Requestlogik, die vorher NUR in
`ui/tui.py:_cmd_local_round`/`_admitted_invite_decision` lag, in einen von
BEIDEN Wegen (dem bestehenden manuellen `l`-Weg UND der neuen freien
Lobbyinitiative) genutzten Baustein -- keine zweite Engine, keine doppelte
Kontrollvertrags-/Ledger-Logik (01_AUFTRAG §4 A: "kleiner wiederverwendbarer
Dienst zwischen UI und bestehenden Primitiven ist erlaubt").

`core/scheduler.py:FairScheduler` bleibt ausschliesslich fuer
Reihenfolge/Fenster zustaendig (`open_window`/`next_initiative`/`pause`) --
der Aufrufer (`ui/tui.py:_cmd_lobby_initiative`) instanziert/befragt ihn NUR
fuer die Zug-Reihenfolge, trifft aber selbst KEINE Entscheidung (01_AUFTRAG
§4 A). Tisch-/Abschnittsanlage
laeuft weiterhin ausschliesslich ueber die bestehende `core.store.
create_table_from_offer_log`/`core.store.derive_group_and_leader` (C: "1-5
INKLUSIVE Leader ueber denselben produktiven Vorschlagspfad") -- dieses Modul
dupliziert diese Ableitung NICHT, sondern speist nur das Offer-Log, das die
Ableitung bereits kennt.

D (Rueckkehr/Dedup): `request_admitted_decision` unten verwendet DIESELBE
known-ID/missing-Record-Wiederaufnahme wie `core.creation_service.
run_admitted_creation_dialog` (`request_ledger.find_durable_result`/
`find_answered_without_text`) -- ein frischer Interpreter, der eine
Lobby-Initiative-Entscheidung wiederholt anfragt, sendet KEINEN zweiten
Request fuer dieselbe Operationsidentitaet (Tisch/Abschnitt/Rolle/Turn/
Teilnehmer), sofern bereits eine durable Antwort vorliegt (L08)."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from . import request_ledger
from .admission import _atomic_write_json, read_admission_block, reservation_for_request
from .store import Lobby, VisibilityError
from ..adapters.base import ParticipantDecision

INVITATION_LOG_FILENAME = "invitation_decisions.jsonl"
WINDOW_STATE_FILENAME = "lobby_window_state.json"


def _invitation_log_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / INVITATION_LOG_FILENAME


def append_offer_log_record(run_dir: str | Path, record: dict) -> None:
    """W1 (F..., "Angebot+Antworten VOR Tischanlage festhalten"): append-only
    Nachweislog, real auf Platte, unabhaengig vom Tischausgang -- IDENTISCHES
    Dateiformat/-name zu `ui/tui.py`s bisheriger `_append_invitation_log`
    (Test `test_p2_community_creation.py` liest exakt diese Datei/dieses
    Schema). Ohne `run_dir` bleibt dies ein No-op (kein Absturz, kein
    erfundenes Verzeichnis).

    R2-Nachzug (REVIEW-LOBBY.md §4, MAIN-DATENWEGENTSCHEIDUNG.md B): dieser
    Writer bleibt ausschliesslich fuer die reinen AUDIT-Eintraege ('offer'/
    'response') zustaendig und darf einen `OSError` weiterhin verschlucken --
    "Reines Audit darf getrennt weiter swallowen". Die OPERATIVE Resolution
    (`append_offer_resolution`) nutzt dagegen `_append_offer_log_record_
    durable` unten, die einen Writefehler NICHT verschluckt."""
    if run_dir is None:
        return
    try:
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        path = _invitation_log_path(run_dir)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass  # Nachweislog ist Audit, kein Blocker fuer den eigentlichen Ablauf.


def _append_offer_log_record_durable(run_dir: str | Path, record: dict) -> None:
    """R2-Nachzug (REVIEW-LOBBY.md §4, MAIN-DATENWEGENTSCHEIDUNG.md B):
    GENAU WIE `append_offer_log_record`, ausser dass ein `OSError` HIER NICHT
    verschluckt wird -- fuer operative Eintraege (aktuell nur 'resolution'),
    deren Verlust eine bereits verbrauchte Zustimmung erneut anwendbar machen
    wuerde (REVIEW-LOBBY.md §4: "ein fehlerhafter Nachweiswrite ist KEINE
    Erlaubnis, die Bindung wegzulassen"). Der Aufrufer (`ui/tui.py:_cmd_
    lobby_initiative`) faengt diesen Fehler kontrolliert ab (sichtbare
    Meldung, kein Spielstart aus einer nicht durabel gebundenen Zustimmung),
    OHNE den bereits angelegten Tisch stillschweigend fortzusetzen. Ohne
    `run_dir` bleibt dies -- wie beim Audit-Log -- ein No-op."""
    if run_dir is None:
        return
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = _invitation_log_path(run_dir)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_offer_log(run_dir: str | Path) -> list[dict]:
    path = _invitation_log_path(run_dir)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def request_admitted_decision(
    run_dir: str | Path, driver, ctx: dict, *, role: str, participant: str,
    table_id: str | None = None, section_id: str | None = None, turn_idx: int | None = None,
) -> tuple["ParticipantDecision | None", str | None]:
    """Admission-gated Entscheidungsanfrage fuer Angebote/Einladungen/
    Initiativantworten -- derselbe reservierte+persistierte Requestweg wie
    jeder andere Modellrequest (`core.runtime.SectionRuntime._admitted_
    decision`, I2-Nachzug). Liefert `(decision, None)` bei einer tatsaechlich
    (neu ODER wiederaufgefundenen) empfangenen Antwort, `(None, reason)` wenn
    das Admission-Gate blockiert, wirft die Ausnahme des Treibers unveraendert
    weiter (kein Auto-Accept bei Transportfehler).

    D/L08 (WEGKARTE §6/§8, 02_ABNAHME L08): PRUEFT VOR jeder neuen
    Reservierung, ob fuer GENAU DIESE Operationsidentitaet
    (`table_id`/`section_id`/`role`/`turn_idx`/`participant`) bereits eine
    durable Antwort vorliegt (`request_ledger.find_durable_result`) -- ein
    frischer Interpreter/Retry sendet dann KEINEN zweiten Request, sondern
    rekonstruiert die `ParticipantDecision` aus dem bereits empfangenen Text
    (`origin_source='ledger:recovered'`, `.decision` bewusst `None` -- der
    Aufrufer wertet den Text ueber denselben Kontrollvertrag wie einen frisch
    empfangenen aus, keine zweite Interpretationslogik). Ein Treffer OHNE
    Text (`find_answered_without_text`, verlorene Altantwort) blockiert
    kontrolliert (`(None, reason)`) statt eine neue Anfrage fuer eine bereits
    beantwortete Operation zu senden.

    K4-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 A, REVIEW-LOBBY.md §6):
    ein `state="received"`-Treffer wird NICHT mehr ungeprueft als
    freigegebene Entscheidung zurueckgegeben. `request_ledger.
    settle_received` haelt einen Datensatz OHNE bekannte Originaldauer
    (`received_seconds` abwesend/`None`) bewusst bei `state="received"` --
    das ist eine UNGEKLAERTE Wirkung (Kosten-/Latenzbuchung offen), keine
    abgeschlossene Voraussetzung. Bleibt der Datensatz nach `settle_received`
    weiterhin `received` (nicht `accounted`), wird die Antwort NICHT
    freigegeben, sondern kontrolliert offen gehalten (`(None, reason)`,
    identisch zum bestehenden creation-seitigen Vertrag,
    `core.creation_service.run_admitted_creation_dialog`) -- KEIN erneuter
    Modellaufruf (die Antwort liegt ja bereits vor), aber auch KEINE
    Weiterverwendung einer Wirkung, die noch nicht vollstaendig verbucht
    ist. `accounted`/bekannte Dauer/Dauer 0/vollstaendige `received`-Recovery
    bleiben unveraendert positive Faelle (dieser Zweig wird dann erreicht)."""
    identity_kwargs = dict(
        table_id=table_id, section_id=section_id, role=role,
        turn_idx=turn_idx, participant=participant,
    )
    durable = request_ledger.find_durable_result(run_dir, **identity_kwargs)
    if durable is not None:
        if durable.get("state") == "received":
            durable = request_ledger.settle_received(run_dir, durable)
        if durable.get("state") != "accounted":
            return None, (
                f"bereits empfangene Antwort ({role}/{participant}) mit noch ungeklaerter "
                "Wirkung (settle_received bleibt 'received') -- kontrolliert offen, kein "
                "erneuter Modellaufruf, keine Freigabe einer unvollstaendig verbuchten Antwort."
            )
        return (
            ParticipantDecision(
                text=durable.get("result_text") or "",
                origin_source="ledger:recovered",
            ),
            None,
        )
    lost = request_ledger.find_answered_without_text(run_dir, **identity_kwargs)
    if lost is not None:
        return None, (
            f"bereits beantwortete Operation ({role}/{participant}) ohne rekonstruierbaren "
            "Text -- kein erneuter Modellaufruf fuer dieselbe Identitaet."
        )

    reserved_usd, output_bound_known = reservation_for_request(driver, ctx)
    route = getattr(getattr(driver, "config", None), "base_url", None)
    # G2b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27): PRO TREIBER
    # ermittelt (Default `True` erhaelt das Verhalten fuer jeden Treiber ohne
    # diesen Marker unveraendert) -- s. `core.admission.read_admission_block`-
    # Docstring. Initiative-/Consent-/Einladungsrollen laufen ueber DENSELBEN
    # `persona_driver_factory`-Treiber wie `core.runtime._admitted_decision`.
    dollar_billed = getattr(driver, "is_dollar_billed", True)
    blocked, reason = read_admission_block(
        run_dir, reserved_usd=reserved_usd, output_bound_known=output_bound_known, route=route,
        dollar_billed=dollar_billed,
    )
    if blocked:
        return None, reason
    request_id = request_ledger.begin(
        run_dir,
        content=json.dumps(ctx, ensure_ascii=False, sort_keys=True, default=str),
        reserved_usd=reserved_usd, route=route,
        output_limit_tokens=getattr(getattr(driver, "config", None), "max_tokens", None),
        dollar_billed=dollar_billed,
        **identity_kwargs,
    )
    t0 = time.monotonic()
    try:
        decision = driver.decide(ctx)
    except Exception as e:
        request_ledger.finish_error(run_dir, request_id, error=e, seconds=time.monotonic() - t0)
        raise
    request_ledger.finish_received(
        run_dir, request_id, usage=(decision.meta or {}).get("usage"),
        seconds=time.monotonic() - t0, result_text=decision.text,
    )
    return decision, None


@dataclass
class RosterEntry:
    """Sichtbare Lobby-Zeile fuer EINE Community-Persona (01_AUFTRAG §4 A:
    "nicht fertige, pausierte oder tischgebundene Mitglieder sichtbar korrekt
    einordnen; nicht als Ersatzspieler verwenden")."""

    persona_key: str
    ready: bool
    chrononaut_id: str | None
    bound_table_id: str | None


def community_roster(
    run_dir: str | Path, community_ids: list[str], onboarding_dir: str | Path,
    resolve_active_save_fn,
) -> list[RosterEntry]:
    """L01: liest die BESTEHENDE bestaetigte Community (`community_ids` kommt
    vom Aufrufer aus `domain.zeitriss.community_bootstrap.peek(...)
    .personas_written` -- keine neue Generation hier) und ordnet jede Persona
    sichtbar korrekt ein: `ready=False` (noch kein abgeschlossener
    Erschaffungsdialog -- kein Ersatzspieler), sonst `bound_table_id` (bereits
    an einem Tisch gebunden) oder frei/spielbereit. `resolve_active_save_fn`
    ist injiziert (identische Autoritaet wie `ui/tui.py:_resolve_member` --
    `_resolve_active_save` + `onboarding.peek` + `zeitriss_saves.
    block_char_id`), damit dieses Modul KEINE eigene, zweite
    Save-Autoritaet-Kopie fuehrt."""
    lobby_for_locks = Lobby(run_dir, table_size_policy=_NoopSizePolicy())
    out: list[RosterEntry] = []
    for pk in community_ids:
        resolved = resolve_active_save_fn(pk)
        if resolved is None:
            out.append(RosterEntry(persona_key=pk, ready=False, chrononaut_id=None, bound_table_id=None))
            continue
        _active_save, chrononaut_id = resolved
        bound_table_id = lobby_for_locks.is_locked(chrononaut_id)
        out.append(RosterEntry(
            persona_key=pk, ready=True, chrononaut_id=chrononaut_id, bound_table_id=bound_table_id,
        ))
    return out


class _NoopSizePolicy:
    """`community_roster` braucht nur `Lobby.is_locked` (reine Lesung der
    gemeinsamen `locks.json`) -- keine Tischgroessenregel noetig, ein echtes
    Policy-Objekt waere hier eine unnoetige Domaenenkopplung (A1)."""

    min_size = 1
    max_size = 10 ** 9

    def validate_size(self, size: int) -> bool:
        return True


def offer_id_for(window_id: str, from_persona: str, turn_idx: int) -> str:
    """R1.2-Nachzug (REVIEW-LOBBY.md §3.2, MAIN-DATENWEGENTSCHEIDUNG.md A):
    Angebot-IDs muessen im konkreten Community/Lauf/FENSTER eindeutig sein --
    vorher `lobby-offer-{pk}-{turn_idx}` OHNE Fensterbezug, wodurch zwei
    verschiedene Fenster derselben Community/desselben Vorschlagenden
    identisch `lobby-offer-sniper-0` erzeugten (Probe 03: eine alte
    Resolution derselben Offer-ID liess die Rekonstruktion ein neues, echtes
    Angebot verwerfen). Diese EINE Stelle konstruiert die offer_id -- sowohl
    der Produktweg (`ui/tui.py:_cmd_lobby_initiative`) als auch Tests nutzen
    SIE (keine zweite, davon abweichende Formel). Bleibt mit dem Praefix
    `'lobby-offer-'` kompatibel (s. `reconstruct_pending_offer_events`s
    `offer_id_prefix`)."""
    return f"lobby-offer-{window_id}-{from_persona}-{turn_idx}"


@dataclass
class PendingOffer:
    offer_id: str
    from_persona: str
    wants: list[str]
    leader: str | None = None
    activity: str | None = None
    proposed_by: str | None = None


def open_offer_for(participant: str, offer_events: list[dict]) -> PendingOffer | None:
    """Findet ein noch NICHT vollstaendig abgeleitetes Angebot, das
    `participant` unter seinen `wants` fuehrt und von `participant` noch
    keine Konsens-Antwort erhalten hat -- die Grundlage fuer 'wird gerade ein
    offenes Angebot an dich gestellt?' in `run_lobby_initiative_step`. Nutzt
    dieselbe Ableitungsfunktion wie die Tischanlage (`derive_group_and_leader`)
    NICHT erneut (das waere doppelte Logik) -- diese Funktion beantwortet nur
    "gibt es ueberhaupt ein offenes, an dich gerichtetes Angebot", die
    eigentliche Vollstaendigkeits-/Leaderableitung bleibt exklusiv bei
    `derive_group_and_leader`/`create_table_from_offer_log`."""
    offers: dict[str, PendingOffer] = {}
    answered: set[tuple[str, str]] = set()
    for ev in offer_events:
        if ev.get("type") == "offer":
            oid = ev["id"]
            offers[oid] = PendingOffer(
                offer_id=oid, from_persona=ev["from"], wants=list(ev.get("wants") or []),
                leader=ev.get("leader"), activity=ev.get("activity"),
                proposed_by=ev.get("proposed_by"),
            )
        elif ev.get("type") == "consent":
            answered.add((ev.get("offer_id"), ev.get("from")))
    for oid, offer in offers.items():
        if participant in offer.wants and (oid, participant) not in answered:
            return offer
    return None


def _window_state_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / WINDOW_STATE_FILENAME


class WindowStateUnavailableError(RuntimeError):
    """R1.3-Nachzug (REVIEW-LOBBY.md §3.3, MAIN-DATENWEGENTSCHEIDUNG.md A):
    die persistente Fenster-Cursordatei EXISTIERT, ist aber gerade nicht
    zuverlaessig lesbar/parsebar/strukturell eindeutig -- eine notwendige
    Cursor-Autoritaet, die NICHT als leer behandelt und mit einem erratenen
    Cursor 0 ueberschrieben werden darf (vorher: `except (OSError,
    JSONDecodeError): data = {}`, wodurch zwei bereits real gefragte Personas
    nach einem einzelnen Lesefehler erneut als frisch/pausiert erschienen).
    Der Aufrufer (`ui/tui.py:_cmd_lobby_initiative`) haelt bei diesem Fehler
    sichtbar KONTROLLIERT an -- kein Request an irgendein Mitglied, kein
    erratener neuer Cursor, keine Rekonstruktion einer verlorenen Historie."""


def _read_window_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise WindowStateUnavailableError(
            f"Fenster-Cursordatei {path} ist vorhanden, aber gerade nicht zuverlaessig lesbar/"
            f"parsebar ({e}) -- fail-closed, kein Ueberschreiben mit einem erratenen leeren Stand."
        ) from e
    if not isinstance(data, dict):
        raise WindowStateUnavailableError(
            f"Fenster-Cursordatei {path} hat eine unerwartete Struktur ({type(data).__name__}) -- "
            "fail-closed, kein Ueberschreiben."
        )
    return data


def _window_entry_cursor(entry: object) -> int:
    """End-Critic-Nachzug (Hauptbefund 1, END-CRITIC.md §4.3): ein VORHANDENER
    Community-Eintrag, der weder `dict` (neues Schema) noch `int`/`float`
    (altes Schema) ist -- z.B. eine Zeichenkette nach einer gezielten
    Teilkorruption, die den TOP-LEVEL-Dict-Check in `_read_window_state`
    unveraendert besteht -- wurde bisher still als `cursor=0` interpretiert
    und ueberschrieben (Probe B/`r13_collision_demo.py`: reproduzierte
    dieselbe R1.2-offer_id-Kollision ueber diesen anderen Ausloeser). Fehlt
    der Eintrag GANZ (`entry is None`, echte neue/leere Community), bleibt
    `0` weiterhin korrekt -- nur ein VORHANDENER, aber unlesbarer Eintrag ist
    jetzt fail-closed wie die Top-Level-Struktur."""
    if entry is None:
        return 0
    if isinstance(entry, dict):
        raw = entry.get("cursor", 0)
    elif isinstance(entry, (int, float)) and not isinstance(entry, bool):
        raw = entry
    else:
        raise WindowStateUnavailableError(
            f"Fenster-Cursor-Eintrag hat eine unerwartete Struktur ({type(entry).__name__}) -- "
            "fail-closed, kein Ueberschreiben mit einem erratenen Cursor."
        )
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise WindowStateUnavailableError(
            f"Fenster-Cursor-Eintrag hat einen unerwarteten 'cursor'-Wert ({type(raw).__name__}) -- "
            "fail-closed, kein Ueberschreiben mit einem erratenen Cursor."
        )
    return int(raw)


def _window_entry_pending(entry: object) -> str | None:
    """s. `_window_entry_cursor` (Hauptbefund 1): dieselbe Fail-closed-Grenze
    auf der `pending`-Seite -- ein altes reines Int/Float-Schema hat nie eine
    `pending`-Markierung (legitim `None`), ein VORHANDENER, aber weder
    `dict` noch `int`/`float` Eintrag ist dagegen unlesbar."""
    if entry is None or (isinstance(entry, (int, float)) and not isinstance(entry, bool)):
        return None
    if not isinstance(entry, dict):
        raise WindowStateUnavailableError(
            f"Fenster-Cursor-Eintrag hat eine unerwartete Struktur ({type(entry).__name__}) -- "
            "fail-closed, kein Ueberschreiben mit einem erratenen Cursor."
        )
    pending = entry.get("pending")
    return pending if isinstance(pending, str) and pending else None


def _next_window_id(run_dir: str | Path, community_id: str) -> str:
    """K1/K2-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 A, MAIN-
    DATENWEGENTSCHEIDUNG.md Zustandstabelle "Neues b-Fenster nach Pause/
    Abschluss"): kleine PERSISTENTE Fenster-Zaehlerdatei je `community_id`
    (KEIN Universaljournal/DB) -- liefert eine stabile NEUE Fenster-ID und
    schreibt den naechsten Stand SOFORT atomar zurueck. Erste jemals
    vergebene ID einer Community bleibt bewusst `lobby-{community_id}-0`
    (identisches Format zur alten `len(...)`-basierten Formel) -- eine
    bestehende API-/Datenvertragsprobe (02_ABNAHME Fall 05) bindet einen
    Altdatensatz an genau diese woertliche erste Fenster-ID.

    R1.1/R1.3-Nachzug (REVIEW-LOBBY.md §3.1/§3.3, MAIN-DATENWEGENTSCHEIDUNG.md
    A): (1) Lese-/Parse-/Strukturfehler der Datei sind KEIN leerer Stand mehr
    -- s. `WindowStateUnavailableError`. (2) traegt der bereits persistierte
    Community-Eintrag eine noch NICHT geloeschte `pending`-Markierung (s.
    `mark_window_open`/`clear_window_open`), wird DIESE unveraendert
    zurueckgegeben, OHNE den Cursor zu erhoehen -- eine bereits VOR ihrem
    Offer-Logeintrag beantwortete erste Initiative (Prozessabbruch zwischen
    Ledger-Accounting und Offer-Log-Write, Probe 02) verliert dadurch ihre
    Fensteridentitaet nicht an einen neu erratenen Cursor (kein Re-Ask, s.
    `request_ledger.find_durable_result`-Dedup unter DERSELBEN section_id).
    Ein reiner, direkter Aufruf OHNE je gesetzte `pending`-Markierung (z.B.
    ein Einheitstest, der nur diese Funktion prueft) zieht dagegen weiterhin
    JEDES Mal einen GENUIN NEUEN Cursor -- `mark_window_open` wird
    ausschliesslich vom vollen `_cmd_lobby_initiative`-Weg gesetzt, nie hier."""
    path = _window_state_path(run_dir)
    data = _read_window_state(path)
    entry = data.get(community_id)
    pending = _window_entry_pending(entry)
    if pending:
        return pending
    cursor = _window_entry_cursor(entry)
    window_id = f"lobby-{community_id}-{cursor}"
    data[community_id] = {"cursor": cursor + 1, "pending": None}
    _atomic_write_json(path, data)
    return window_id


def mark_window_open(run_dir: str | Path, community_id: str, window_id: str) -> None:
    """R1.1-Nachzug: markiert `window_id` als das aktuell in Bearbeitung
    befindliche (noch nicht definitiv abgeschlossene) Fenster dieser
    Community -- vom Aufrufer (`ui/tui.py:_cmd_lobby_initiative`) IMMER
    unmittelbar NACH `resolve_window_id`, VOR dem ersten echten Request
    dieses Initiativschritts gesetzt. Ein Prozessabbruch danach (z.B. beim
    Offer-Logeintrag) verliert die Markierung NICHT -- `_next_window_id`
    liefert beim naechsten Aufruf dieselbe `window_id` zurueck (kein neuer
    Cursor). Idempotent (dasselbe `window_id` erneut zu setzen ist ein
    No-op-aehnlicher Zustand)."""
    path = _window_state_path(run_dir)
    data = _read_window_state(path)
    cursor = _window_entry_cursor(data.get(community_id))
    data[community_id] = {"cursor": cursor, "pending": window_id}
    _atomic_write_json(path, data)


def clear_window_open(run_dir: str | Path, community_id: str, window_id: str) -> None:
    """R1.1-Nachzug: loescht die `pending`-Markierung fuer `window_id`,
    SOBALD diese Runde tatsaechlich definitiv abgeschlossen ist (Resolution
    geschrieben -- `outcome='table_bound'`/`'no_table'` -- ODER die gesamte
    Runde endet OHNE jedes neue/fortgesetzte Angebot, z.B. alle Mitglieder
    pausiert). NUR danach darf der naechste Aufruf wieder einen GENUIN NEUEN
    Cursor ziehen (K1: "neues Fenster nach reiner Pause" bleibt erhalten).
    Ein Nichttreffer (andere/keine `pending`-Markierung, z.B. weil ein
    ANDERER Aufruf bereits geraeumt hat) bleibt ein No-op -- keine fremde/
    neuere Markierung ueberschreiben."""
    path = _window_state_path(run_dir)
    data = _read_window_state(path)
    entry = data.get(community_id)
    if _window_entry_pending(entry) == window_id:
        data[community_id] = {"cursor": _window_entry_cursor(entry), "pending": None}
        _atomic_write_json(path, data)


def resolve_window_id(run_dir: str | Path, community_id: str, pending_offer_events: list[dict]) -> str:
    """K1/K2-Nachzug: ein NEUES Fenster braucht eine stabile NEUE
    Fenster-/Operationsidentitaet (Main-Zustandstabelle "Neues b-Fenster
    nach Pause"/"nach Abschluss") -- ein FORTGESETZTES (unterbrochenes, noch
    offenes) Fenster behaelt dagegen seine urspruengliche Identitaet (Main-
    Zustandstabelle "Offener Schritt ... unterbrochen"). Liegt bereits ein
    NOCH OFFENES (nicht resolvedes) Angebot vor (s. `reconstruct_pending_
    offer_events`), traegt dessen 'offer'-Ereignis die beim urspruenglichen
    Fensterstart vergebene `window_id` -- diese wird UNVERAENDERT
    wiederverwendet (kein neuer Cursor, keine neue Identitaet fuer eine
    bereits laufende, noch nicht abgeschlossene Operation). Liegt KEIN
    offenes Angebot vor (frisches Fenster, ODER das vorherige Fenster wurde
    entweder rein pausiert ODER bereits vollstaendig resolved -- s.
    `append_offer_resolution`), wird ueber `_next_window_id` eine GENUIN NEUE
    Fenster-ID gezogen."""
    for ev in pending_offer_events:
        if ev.get("type") == "offer" and ev.get("window_id"):
            return ev["window_id"]
    return _next_window_id(run_dir, community_id)


def append_offer_resolution(
    run_dir: str | Path, offer_id: str | None, *, outcome: str, table_id: str | None = None,
) -> None:
    """K1/K2-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 A: "bestaetigtes
    Angebot mit tatsaechlicher Tisch-/Section-ID verknuepfen"): markiert ein
    Angebot, dessen Konsens vollstaendig abgeleitet UND tatsaechlich
    ANGEWANDT wurde (Tischanlage versucht), als resolved -- `outcome`
    ist entweder `"table_bound"` (ein echter Tisch ist entstanden,
    `table_id` gesetzt) oder `"no_table"` (Ableitung vollstaendig, aber die
    Tischanlage selbst hat abgelehnt, z.B. 0/6-Groessengrenze/Sperre --
    KEIN automatischer Ersatzversuch, aber auch KEIN stilles Verschwinden:
    `outcome`/`table_id` bleiben im Append-only-Log auffindbar). Ein
    resolvedes Angebot wird von `reconstruct_pending_offer_events` NICHT
    mehr als offen zurueckgegeben (weder erneut angefragt noch erneut
    angewandt) -- 'vollstaendig zugestimmt' (Konsens) ist damit klar von
    'verbraucht' (resolved) unterschieden: ein Angebot OHNE Resolution-
    Eintrag bleibt auffindbar/fortsetzbar, selbst wenn sein Konsens bereits
    vollstaendig war (unterbrochener Anwendungsschritt, Main-Zustandstabelle
    "Offener Schritt ... unterbrochen")."""
    if offer_id is None:
        return
    _append_offer_log_record_durable(run_dir, {
        "type": "resolution", "offer_id": offer_id, "outcome": outcome, "table_id": table_id,
    })


def offer_resolution_exists(
    run_dir: str | Path, offer_id: str | None, *,
    table_id: str | None = None, outcome: str | None = None,
) -> bool:
    """R2-Nachzug (echtes Resume, MAIN-QUELLENENTSCHEIDUNG-RESUME.md):
    prueft, ob fuer `offer_id` im (ggf. reparierten) Angebotslog bereits ein
    `resolution`-Eintrag steht -- fuer das idempotente Nachziehen einer
    fehlenden B1-Resolution beim Resume eines bereits gebundenen Tisches.
    B2 hat seine Resolution bereits; dort darf `append_offer_resolution`
    NICHT ein zweites Mal aufgerufen werden ("nichts Neues erfinden").

    Konsistenz-Guard (MAIN-QUELLENENTSCHEIDUNG-ZUORDNUNG.md Fall 04): ohne
    `table_id`/`outcome` bleibt die urspruengliche reine Existenzfrage
    (irgendein Resolution-Eintrag fuer diese Angebots-Kennung) unveraendert.
    Werden `table_id` und/oder `outcome` mitgegeben, zaehlt NUR ein Eintrag,
    dessen eigene `table_id`/`outcome` damit uebereinstimmt -- ein Eintrag,
    der fuer dieselbe Angebots-Kennung auf einen ANDEREN Tisch verweist,
    gilt dann NICHT als passende Bindung fuer diesen Tisch."""
    if offer_id is None:
        return False
    for rec in read_offer_log(run_dir):
        if rec.get("type") != "resolution" or rec.get("offer_id") != offer_id:
            continue
        if table_id is not None and rec.get("table_id") != table_id:
            continue
        if outcome is not None and rec.get("outcome") != outcome:
            continue
        return True
    return False


def offer_resolutions_for(run_dir: str | Path, offer_id: str | None) -> list[dict]:
    """R1-Nachzug (MAIN-QUELLENENTSCHEIDUNG-BELEGKETTE.md): liefert ALLE
    `resolution`-Eintraege fuer `offer_id` aus dem Angebotslog -- anders als
    `offer_resolution_exists` (Early-Return beim ersten Treffer) verdeckt
    diese vollstaendige Menge keinen weiteren, widerspruechlichen Eintrag
    derselben Angebots-Kennung. Der Caller (`ui/tui.py`) muss die gesamte
    zurueckgegebene Menge auf Vereinbarkeit mit dem tatsaechlichen Tisch
    pruefen, nicht nur die Existenz EINES passenden Eintrags."""
    if offer_id is None:
        return []
    return [
        rec for rec in read_offer_log(run_dir)
        if rec.get("type") == "resolution" and rec.get("offer_id") == offer_id
    ]


def reconstruct_pending_offer_events(run_dir: str | Path, *, offer_id_prefix: str) -> list[dict]:
    """D/L08 (WEGKARTE §6/§8, 02_ABNAHME L08 "wirklich neuer Interpreter
    liest offenes Angebot/Antwort/teilweise Tischanlage"): rekonstruiert die
    NOCH OFFENEN (nicht resolvedes) Angebots-/Antwort-Ereignisse aus dem
    persistenten `invitation_decisions.jsonl` -- in der Form, die
    `core.store.derive_group_and_leader` erwartet (Offer-Eintraege mit
    Schluessel 'id', Consent-Eintraege mit 'offer_id'), plus additiv
    `window_id` (Fensterbindung, s. `resolve_window_id`) am Offer-Ereignis.
    Ein frischer `_cmd_lobby_initiative`-Aufruf (neuer Prozess/neue Session)
    sieht damit ein bereits gestelltes, noch unbeantwortetes eigenes
    Angebot weiter und stellt es NICHT neu.

    K1/K2-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 A, REVIEW-LOBBY.md
    §3/§4): ein Angebot gilt NUR NOCH dann als "verbraucht" (wird hier
    verworfen), wenn es einen expliziten Resolution-Eintrag traegt (s.
    `append_offer_resolution`) -- NICHT mehr allein deshalb, weil sein
    Konsens irgendwann vollstaendig war. Das trennt "vollstaendig
    zugestimmt" (Konsens) von "in einem geschlossenen Tisch verbraucht"
    (tatsaechlich angewandt): ein Angebot, dessen Konsens bereits
    vollstaendig ist, aber dessen Anwendung (Tischanlage) unterbrochen
    wurde, BEVOR die Resolution geschrieben werden konnte, bleibt hier
    weiterhin auffindbar -- der Aufrufer (`ui/tui.py:_cmd_lobby_initiative`)
    prueft Vollstaendigkeit VOR dem Initiativschritt-Loop erneut und
    schliesst die Anwendung (Tischanlage + Resolution-Schreiben) direkt ab,
    OHNE eine neue Reservierung/Anfrage fuer die bereits vorliegenden
    Antworten. `offer_id_prefix` grenzt gegen den unabhaengigen manuellen
    `l`-Weg ab (dessen Angebote unter 'invite-'/'lead-invite-' laufen --
    eigener Namensraum, keine Vermischung der beiden Offer-Pools)."""
    offers: dict[str, dict] = {}
    consents: dict[str, list[dict]] = {}
    resolved: set[str] = set()
    order: list[str] = []
    for rec in read_offer_log(run_dir):
        offer_id = rec.get("offer_id")
        if not isinstance(offer_id, str) or not offer_id.startswith(offer_id_prefix):
            continue
        rtype = rec.get("type")
        if rtype == "offer":
            if offer_id not in offers:
                order.append(offer_id)
            offers[offer_id] = {
                "from": rec.get("from"), "wants": list(rec.get("wants") or []),
                "window_id": rec.get("window_id"), "leader": rec.get("leader"),
                "activity": rec.get("activity"), "proposed_by": rec.get("proposed_by"),
            }
        elif rtype == "response":
            consents.setdefault(offer_id, []).append(
                {"from": rec.get("from"), "accept": rec.get("decision") == "accept"},
            )
        elif rtype == "resolution":
            resolved.add(offer_id)

    events: list[dict] = []
    for offer_id in order:
        if offer_id in resolved:
            continue  # tatsaechlich angewandt (Tisch entstanden oder kontrolliert abgelehnt) -- verbraucht.
        offer = offers[offer_id]
        events.append({
            "type": "offer", "id": offer_id, "from": offer["from"], "wants": list(offer["wants"]),
            "window_id": offer.get("window_id"), "leader": offer.get("leader"),
            "activity": offer.get("activity"), "proposed_by": offer.get("proposed_by"),
        })
        for c in consents.get(offer_id, []):
            events.append({"type": "consent", "offer_id": offer_id, "from": c["from"], "accept": c["accept"]})
    return events


def lobby_messages_for(lobby: Lobby, persona_key: str) -> list[dict]:
    """K3-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 B): erlaubte
    gemeinsame Lobbyereignisse (`Lobby.post_lobby_message`-Historie) fuer
    den tatsaechlichen Kontextaufbau VOR einer Reservierung (`_own_system_
    context`-Aufrufer haengt dies zusaetzlich als `table_view` an, s.
    `adapters.base.render_public_wire_text`). `persona_key` ist an dieser
    Stelle immer bereits Lobby-Mitglied (der Aufrufer joint jedes freie
    Mitglied VOR dem Initiativschritt) -- `VisibilityError` bleibt trotzdem
    defensiv abgefangen (leere Historie statt Absturz), falls das je nicht
    zutrifft."""
    try:
        return lobby.lobby_messages(persona_key)
    except VisibilityError:
        return []


def post_lobby_message_if_present(lobby: Lobby, persona_key: str, message: str | None) -> None:
    """K3-Nachzug: schreibt eine normale, tatsaechlich AUSGESPROCHENE
    oeffentliche Lobbyaeusserung (aus dem erweiterten Kontrollvertrag,
    `adapters.base.interpret_initiative_proposal`s `message`-Feld) in den
    erlaubten oeffentlichen Kanal -- NICHT nur in einen Operatorreport
    (01_AUFTRAG §3 B). Ein leeres/fehlendes `message` bleibt ein No-op
    (kein erfundener Text)."""
    if not message:
        return
    try:
        lobby.post_lobby_message(persona_key, message)
    except VisibilityError:
        pass
