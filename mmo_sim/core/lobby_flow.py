#!/usr/bin/env python3
"""
mmo_sim/core/lobby_flow.py — UI-neutraler gemeinsamer Lobby-/Tischaufruf
(Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, H-A).

Aus `ui/tui.py:_cmd_lobby_initiative`/`_play_bound_table`/
`_resume_consistency_hold_reason` extrahiert -- KEIN TUI-Rewrite, KEINE
zweite Offer-/Resume-/Kontextlogik. Die drei Funktionen hier sind
byte-identisch in ihrem Verhalten/ihren Konsolentexten zu ihren frueheren
TUI-Methoden (dieselben `session._print`-Aufrufe, dieselbe Reihenfolge,
dieselben Guards); NEU ist ausschliesslich, dass jeder bisherige `return`
zusaetzlich ein maschinenlesbares `LobbyWindowOutcome` liefert, statt nur
`None`. `session` ist ein `ui.tui.TuiSession`-Objekt (oder ein Objekt mit
identischer Schnittstelle) -- TUI ruft diese Funktionen MIT SICH SELBST als
`session` auf (`_cmd_lobby_initiative` wird zum duennen Wrapper), Headless
(`mmo_sim/lab/cli.py`) konstruiert eine eigene `TuiSession`-Instanz OHNE
interaktives Terminal (`input_fn`/`print_fn` sind fuer Headless neutral/
loggend) und ruft DIESELBEN Funktionen auf -- ein Abschnitt laeuft dadurch
strukturell nie zweimal (TUI und Lab teilen sich `run_play_session` UND
diesen Aufrufweg).

`ai_personas` (H-F/H09, neu): die Menge der Persona-Keys, die dieser Aufruf
ueberhaupt mit einem KI-Treiber (`persona_driver_factory`) spielen darf. TUI
ruft weiterhin mit `ai_personas=None` auf (unveraendertes Verhalten, H01 --
der bisherige manuelle Weg kennt gar keine Tischmitglieder ausserhalb der
eigenen Community). Lab uebergibt IMMER die explizit bestaetigte Community-
Persona-Menge (ggf. durch `--personas` weiter eingeschraenkt): trifft
`play_bound_table` auf einen Tischmitglied AUSSERHALB dieser Menge (z.B. ein
menschlicher Teilnehmer mit eigener Figur, der ueber den unabhaengigen
`_cmd_local_round`-Weg an denselben Tisch gebunden wurde), haelt der Aufruf
mit `WAITING_HUMAN` an, OHNE fuer dieses Mitglied einen KI-Treiber zu
konstruieren (kein automatischer Adapterwechsel, 01_AUFTRAG §4 H-F)."""
from __future__ import annotations

import datetime
import inspect
from dataclasses import dataclass
from enum import Enum


class LobbyOutcomeKind(str, Enum):
    """Maschinenlesbares Ergebnis eines begrenzten Lobbyfensters (01_AUFTRAG
    §3 Entscheidung 1). Namen/Bedeutung sind Main-Entscheidung, s.
    ANSCHLUSSPLAN-HEADLESS.md."""

    SECTION_COMPLETED = "section_completed"
    NO_CONSENSUS = "no_consensus"
    WAITING_HUMAN = "waiting_human"
    STOPPED = "stopped"
    OPEN_WITH_REASON = "open_with_reason"


@dataclass
class LobbyWindowOutcome:
    """Konkrete Referenzen statt Prosa (01_AUFTRAG §4 H-A: "Namen/Dataclass
    frei, Bedeutung nicht"). `reason` ist der bereits vorhandene, fuer
    Menschen lesbare Text (identisch zu dem, was TUI ohnehin per
    `session._print` ausgegeben haette) -- der Headless-Controller trifft
    seine Fortsetzungsentscheidung jedoch NUR ueber `kind`, nie ueber
    `reason`-Text-Parsing."""

    kind: LobbyOutcomeKind
    reason: str
    table_id: str | None = None
    section_id: str | None = None
    window_id: str | None = None
    request_id: str | None = None


def resume_consistency_hold_reason(
    session, lobby, table, derivation, resolved_chrononaut_ids: dict[str, str],
) -> str | None:
    """Portiert aus `ui/tui.py:_resume_consistency_hold_reason` -- unveraendertes
    Verhalten, s. dortiger (weiterhin gueltiger) Docstring fuer die volle
    Begruendung. `session` liefert nur `run_dir` (fuer
    `lobby_service.offer_resolutions_for`)."""
    from . import lobby_service

    table_source_offer_id = table.operator_meta.get("source_offer_id")
    if derivation.source_offer_id != table_source_offer_id:
        return (
            "Angebots-Kennung der Ableitung "
            f"({derivation.source_offer_id!r}) stimmt nicht mit der "
            f"am Tisch hinterlegten Angebots-Kennung ({table_source_offer_id!r}) "
            "ueberein"
        )
    if derivation.leader != table.leader:
        return (
            f"abgeleiteter Leader ({derivation.leader!r}) stimmt nicht "
            f"mit dem tatsaechlichen Tisch-Leader ({table.leader!r}) ueberein"
        )
    if sorted(derivation.members) != sorted(table.members):
        return (
            f"abgeleitete Mitglieder ({derivation.members!r}) stimmen "
            f"nicht mit den tatsaechlichen Tisch-Mitgliedern ({table.members!r}) "
            "ueberein"
        )
    if set(derivation.members) != set(table.chrononaut_ids.keys()):
        return (
            "Mitgliederkreis und die am Tisch hinterlegte Figuren-Zuordnung "
            f"(chrononaut_ids: {sorted(table.chrononaut_ids)!r}) sind nicht "
            "fuer ALLE Mitglieder deckungsgleich"
        )
    for pk in derivation.members:
        actual_chrono_id = resolved_chrononaut_ids.get(pk)
        table_chrono_id = table.chrononaut_ids[pk]
        if actual_chrono_id != table_chrono_id:
            return (
                f"die tatsaechlich aufgeloeste Current-Figur von '{pk}' "
                f"({actual_chrono_id!r}) stimmt nicht mit der am Tisch "
                f"hinterlegten Figuren-Zuordnung ({table_chrono_id!r}) ueberein"
            )
    if any(
        lobby.is_locked(table.chrononaut_ids[pk]) != table.table_id
        for pk in derivation.members
    ):
        return "mindestens ein Mitgliedslock zeigt nicht (mehr) auf diesen Tisch"
    if derivation.source_offer_id is not None and any(
        rec.get("table_id") != table.table_id or rec.get("outcome") != "table_bound"
        for rec in lobby_service.offer_resolutions_for(session.run_dir, derivation.source_offer_id)
    ):
        return (
            "die Resolution-Menge fuer diese Angebots-Kennung enthaelt einen "
            "Eintrag, der (table_id/outcome) nicht zu diesem Tisch passt"
        )
    return None


def play_bound_table(
    session, lobby, table, offer_events: list[dict],
    source_offer_id: str | None, active_saves: dict[str, dict],
    ai_personas: frozenset[str] | None = None,
) -> LobbyWindowOutcome:
    """Portiert aus `ui/tui.py:_play_bound_table` (unveraendertes Verhalten/
    Konsolentexte fuer den bereits vorhandenen Pfad). NEU (H-F/H09): steht
    ein Tischmitglied AUSSERHALB der ausdruecklich erlaubten `ai_personas`-
    Menge, wird HIER angehalten -- VOR jeder Treiberkonstruktion fuer
    IRGENDEIN Mitglied dieses Tisches (kein Teil-Adapterwechsel, kein
    KI-Ersatz fuer eine fehlende menschliche Antwort)."""
    if ai_personas is not None:
        missing = sorted(set(table.members) - set(ai_personas))
        if missing:
            reason = (
                f"Tisch {table.table_id} hat Mitglied(er) {missing} ausserhalb der "
                "ausdruecklich gewaehlten KI-Personamenge dieses Lab-Laufs -- wartet auf "
                "menschliche Entscheidung, kein automatischer Adapterwechsel, kein "
                "Spielstart (H-F)."
            )
            session._print(f"Lobby-Initiative: {reason}")
            return LobbyWindowOutcome(
                kind=LobbyOutcomeKind.WAITING_HUMAN, reason=reason,
                table_id=table.table_id, section_id=f"{table.table_id}-section",
            )

    from . import app_service
    from .controller import TableController
    from .persona_state import PersonaStateStore
    from ..domain.zeitriss import saves as zeitriss_saves
    from ..domain.zeitriss.policy import (
        COMPLETION_MARKER,
        ZeitrissHarvestValidator,
        build_harvest_conflict_detector,
        build_save_command_completion_fallback,
    )

    agreed_activity = None
    if source_offer_id:
        for ev in offer_events:
            if ev.get("type") == "offer" and ev.get("id") == source_offer_id:
                agreed_activity = ev.get("activity")
                break

    def _table_start_note(pk: str) -> str:
        note = "Du fuehrst diesen Tisch als Leader." if pk == table.leader else "Ich trete dem Tisch bei."
        if pk == table.leader and agreed_activity:
            note += (
                f"\nAus der Lobby-Uebereinkunft angenommener gemeinsamer Vorschlag: {agreed_activity} "
                "-- du entscheidest deine tatsaechliche Spielnachricht an diesem Tisch weiterhin selbst."
            )
        return note

    ps_store = PersonaStateStore(schema_path=session.schema_path)
    drivers = {pk: session.persona_driver_factory(pk) for pk in table.members}
    contexts = {
        pk: {
            "system": session._own_system_context(pk),
            "user": _table_start_note(pk),
            "import_save_payload": active_saves[pk],
        }
        for pk in table.members
    }
    try:
        accepts_table_id = len(inspect.signature(session.gm_transport_factory).parameters) >= 1
    except (TypeError, ValueError):
        accepts_table_id = False
    try:
        gm_transport = session.gm_transport_factory(table.table_id) if accepts_table_id else session.gm_transport_factory()
    except Exception as e:  # SL-Anbindung nicht herstellbar -- kein stiller Fallback (03 §4).
        reason = f"Lobby-Initiative: SL-Anbindung fuer Tisch {table.table_id} nicht verfuegbar ({e}) — kein Spielstart."
        session._print(reason)
        return LobbyWindowOutcome(
            kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
            table_id=table.table_id, section_id=f"{table.table_id}-section",
        )

    controller = TableController(table.leader, drivers)
    today = datetime.date.today().isoformat()
    ts = datetime.datetime.now().isoformat()
    section_id = f"{table.table_id}-section"
    outcome = app_service.run_play_session(
        lobby, table, gm_transport, controller, section_id,
        contexts, session.states_dir, today, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief,
        # OPTION2-CMD (FIX-SPEC-OPTION2-CMD.md): Leader-`!save`/`!speichern`
        # + bindbarer v7-Save schliesst den Abschnitt GLEICHWERTIG zum
        # Top-Level-Marker -- der Marker-Pfad bleibt unveraendert.
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        harvest_conflict_detector=build_harvest_conflict_detector(),
    )
    if outcome.completion.success:
        reason = (
            f"Lobby-Tisch abgeschlossen: {outcome.completion.members_completed} — neues begrenztes "
            "Lobbyfenster jederzeit ueber 'b' moeglich (kein automatischer zweiter Abschnitt)."
        )
        session._print(reason)
        return LobbyWindowOutcome(
            kind=LobbyOutcomeKind.SECTION_COMPLETED, reason=reason,
            table_id=table.table_id, section_id=section_id,
        )
    reason = f"Lobby-Tisch nicht abgeschlossen ({outcome.completion.reason}) — kann fortgesetzt werden."
    session._print(reason)
    return LobbyWindowOutcome(
        kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
        table_id=table.table_id, section_id=section_id,
    )


def run_lobby_window(session, ai_personas: frozenset[str] | None = None) -> LobbyWindowOutcome:
    """Portiert aus `ui/tui.py:_cmd_lobby_initiative` -- unveraendertes
    Verhalten/Konsolentexte (s. dortiger, weiterhin gueltiger Docstring fuer
    die volle Begruendung jedes einzelnen Zweigs). `ai_personas=None`
    (TUI-Default) aendert NICHTS am bisherigen Verhalten. Lab uebergibt
    IMMER eine konkrete Menge (s. Moduldocstring)."""
    if (
        session.run_dir is None or session.states_dir is None or session.schema_path is None
        or session.gm_transport_factory is None or session.persona_driver_factory is None
    ):
        reason = (
            "Lobby-Initiative erfordert eine konfigurierte Laufumgebung (run_dir/states_dir/"
            "schema_path), eine SL-Anbindung (gm_transport_factory) UND eine Persona-Anbindung "
            "(persona_driver_factory) — hier nicht konfiguriert, kein Initiativschritt "
            "(Live-Setup, s. docs/mmo-sim.md)."
        )
        session._print(reason)
        return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason)

    from . import lobby_service
    from . import store as core_store
    from .scheduler import FairScheduler
    from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
    from ..domain.zeitriss.policy import COMPLETION_MARKER
    from ..adapters.base import (
        decision_contract_instruction,
        initiative_proposal_contract_instruction,
        interpret_decision_contract,
        interpret_initiative_proposal,
    )
    from .completion_marker import completion_marker_matches
    from ..ui.tui import _ActiveSaveUnresolved

    community_id = f"community-{session.participant_id}"
    community_dir = session.run_dir / "community"
    bootstrap = peek_bootstrap(community_dir, community_id)
    if bootstrap is None or not bootstrap.personas_written:
        reason = (
            f"Lobby-Initiative: keine bestehende bestaetigte Spielgemeinschaft {community_id!r} "
            "gefunden — zuerst 'c' aufrufen (keine neue Generation hier)."
        )
        session._print(reason)
        return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason)

    def _resolve_for_roster(pk: str):
        try:
            return session._resolve_member(pk)
        except _ActiveSaveUnresolved:
            return None

    roster = lobby_service.community_roster(
        session.run_dir, bootstrap.personas_written, session.onboarding_dir, _resolve_for_roster,
    )
    not_ready = [r.persona_key for r in roster if not r.ready]
    bound = {r.persona_key: r.bound_table_id for r in roster if r.ready and r.bound_table_id is not None}
    free = [r for r in roster if r.ready and r.bound_table_id is None]
    session._print(
        f"Lobby {community_id!r} ({len(roster)} Mitglieder): "
        f"frei/spielbereit={[r.persona_key for r in free]} gebunden={bound} noch_nicht_bereit={not_ready}"
    )

    from ..domain.zeitriss.policy import ZeitrissTableSizePolicy

    lobby = core_store.Lobby(session.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for r in free:
        lobby.join(r.persona_key)
    chrononaut_ids: dict[str, str] = {r.persona_key: r.chrononaut_id for r in free}
    active_saves: dict[str, dict] = {}
    offer_events: list[dict] = lobby_service.reconstruct_pending_offer_events(
        session.run_dir, offer_id_prefix="lobby-offer-",
    )
    try:
        window_section_id = lobby_service.resolve_window_id(session.run_dir, community_id, offer_events)
        lobby_service.mark_window_open(session.run_dir, community_id, window_section_id)
    except lobby_service.WindowStateUnavailableError as e:
        reason = (
            f"Lobby-Initiative: Fenster-Cursordatei fuer {community_id!r} ist gerade nicht "
            f"zuverlaessig lesbar ({e}) — kontrolliert gesperrt, kein neues Fenster erraten, "
            "kein Request an irgendein Mitglied."
        )
        session._print(reason)
        return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason)

    pre_derivation = core_store.derive_group_and_leader(offer_events)
    confirmed_derivation = pre_derivation if pre_derivation.leader is not None else None
    steps_taken = 0
    stop_kind: LobbyOutcomeKind | None = None
    stop_reason: str | None = None

    if confirmed_derivation is None:
        def _resume_bound_table(resumable: "core_store.Table") -> LobbyWindowOutcome:
            """Gemeinsamer Resume-Body fuer BEIDE Fundarten (Recovery/Ernte
            UND Mid-Play-Fortsetzung) -- inhaltlich UNVERAENDERT gegenueber
            der Vor-R4-FixB1-Fassung, nur in eine Closure extrahiert, damit
            er von zwei getrennten Aufrufstellen (PRE-STEP vor STEP 1, STEP 2
            nach STEP 1) genutzt werden kann, ohne Code zu duplizieren."""
            lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
            offer_log_snapshot = list(resumable.operator_meta.get("offer_log") or [])
            snapshot_derivation = core_store.derive_group_and_leader(offer_log_snapshot)
            if snapshot_derivation.leader is None or not snapshot_derivation.members:
                reason = (
                    f"Lobby-Initiative: Tisch {resumable.table_id} ist gebunden, aber "
                    "sein gespeicherter Angebots-Schnappschuss ist nicht eindeutig "
                    "rekonstruierbar — kontrolliert offen, kein automatischer "
                    "Spielstart, kein Unlock."
                )
                session._print(reason)
                return LobbyWindowOutcome(
                    kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                    table_id=resumable.table_id,
                )
            resolved_members: dict[str, tuple[dict, str]] = {}
            for pk in snapshot_derivation.members:
                try:
                    resolved = session._resolve_member(pk)
                except _ActiveSaveUnresolved:
                    reason = (
                        f"Lobby-Initiative: Spielstand von '{pk}' fuer die "
                        f"Wiederaufnahme von Tisch {resumable.table_id} gerade nicht "
                        "lesbar — kein Resume, kontrolliert offen."
                    )
                    session._print(reason)
                    return LobbyWindowOutcome(
                        kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                        table_id=resumable.table_id,
                    )
                if resolved is None:
                    reason = (
                        f"Lobby-Initiative: '{pk}' hat fuer die Wiederaufnahme von "
                        f"Tisch {resumable.table_id} keine abgeschlossene Figur mehr "
                        "— kein Resume, kontrolliert offen."
                    )
                    session._print(reason)
                    return LobbyWindowOutcome(
                        kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                        table_id=resumable.table_id,
                    )
                resolved_members[pk] = resolved
            active_saves_resume = {pk: v[0] for pk, v in resolved_members.items()}
            chrononaut_ids_resume = {pk: v[1] for pk, v in resolved_members.items()}
            mismatch_reason = resume_consistency_hold_reason(
                session, lobby, resumable, snapshot_derivation, chrononaut_ids_resume,
            )
            if mismatch_reason is not None:
                reason = (
                    f"Lobby-Initiative: Tisch {resumable.table_id} ist gebunden, aber "
                    f"die Belege widersprechen sich ({mismatch_reason}) — kontrolliert "
                    "offen, kein automatischer Spielstart, kein Unlock, keine neue "
                    "Resolution."
                )
                session._print(reason)
                return LobbyWindowOutcome(
                    kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                    table_id=resumable.table_id,
                )
            table, _resume_derivation = core_store.create_table_from_offer_log(
                lobby, resumable.table_id, offer_log_snapshot, chrononaut_ids_resume,
            )
            if table is None:
                reason = (
                    f"Lobby-Initiative: Tisch {resumable.table_id} konnte fuer die "
                    "Wiederaufnahme nicht geladen werden — kontrolliert offen, kein "
                    "automatischer Spielstart."
                )
                session._print(reason)
                return LobbyWindowOutcome(
                    kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                    table_id=resumable.table_id,
                )
            if snapshot_derivation.source_offer_id is not None and not lobby_service.offer_resolution_exists(
                session.run_dir, snapshot_derivation.source_offer_id,
            ):
                try:
                    lobby_service.append_offer_resolution(
                        session.run_dir, snapshot_derivation.source_offer_id,
                        outcome="table_bound", table_id=table.table_id,
                    )
                except OSError as e:
                    reason = (
                        f"Lobby-Initiative: Tisch {table.table_id} ist gebunden, aber "
                        "die fehlende Resolution konnte auch jetzt nicht dauerhaft "
                        f"nachgeschrieben werden ({e}) — kontrolliert offen, spaeter "
                        "bei gesundem Zugriff erneut ausfuehrbar."
                    )
                    session._print(reason)
                    return LobbyWindowOutcome(
                        kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason,
                        table_id=table.table_id,
                    )
            return play_bound_table(
                session, lobby, table, offer_log_snapshot,
                snapshot_derivation.source_offer_id, active_saves_resume,
                ai_personas=ai_personas,
            )

        # PRE-STEP -- Recovery/Ernte-Wiederaufnahme bleibt UNVERAENDERT strikt
        # vorrangig, VOR STEP 1 und VOR STEP 2 (B1-FIX-SPEC.md betrifft NUR
        # die Mid-Play-Fortsetzung `find_bound_active_continuable_table`,
        # NICHT diesen bereits bestehenden, rein lesenden Konsistenz-/
        # Ernte-Pfad -- der ruft NIEMALS einen Personentreiber auf, bevor er
        # entweder abschliesst oder kontrolliert haelt, s. `resume_
        # consistency_hold_reason` unten in `_resume_bound_table`. Ein
        # bestehender Sicherheits-Regressionstest (test_r2d_lobby_resume_
        # belegkette_guard.py) verlangt genau das: VOR jeder Personaent-
        # scheidung kontrolliert offenhalten, auch wenn ein strukturell noch
        # zu diesem Tisch gehoerendes Mitglied wegen eines fehlenden Locks
        # in der groben Roster-Sicht (`free`/`bound`, reiner `locks.json`-
        # Schnappschuss) faelschlich "frei" erscheint -- STEP 1 duerfte so
        # ein Mitglied NIE vor dieser Konsistenzpruefung befragen.
        #
        # BL1-FIX (BL1-FIX-SPEC.md, CRITIC-REPORT-R3.md): `ai_personas` wird
        # HIER durchgereicht -- analog zu STEP 1 (`free_selectable` unten)
        # und zum bereits bestehenden Gate in `play_bound_table`. Ein
        # gebundener, ungespielter Tisch, dessen Mitglieder NICHT
        # VOLLSTAENDIG in `ai_personas` liegen (z.B. weil der Spieler
        # bewusst nur eine Teilmenge auswaehlt), gewinnt PRE-STEP dadurch
        # NICHT mehr unbedingt -- er faellt durch zu STEP 1, statt die
        # Initiative-Phase fuer die tatsaechlich ausgewaehlten, bereiten
        # Figuren JEDES Fenster zu blockieren (BL1: sonst 0 Initiative-
        # Chancen fuer die Auswahl, faelschliches `blocked`).
        # `ai_personas=None` (TUI-Default, alle freien) aendert nichts.
        if bound:
            resumable = core_store.find_bound_active_unplayed_table(
                session.run_dir,
                {r.persona_key: r.chrononaut_id for r in roster if r.ready},
                bound,
                marker=COMPLETION_MARKER,
                marker_matches=completion_marker_matches,
                ai_personas=ai_personas,
            )
            if resumable is not None:
                return _resume_bound_table(resumable)

        # R4-FixB1 (B1-FIX-SPEC.md, 02_JETZT_ENTWICKELN.md §1): freie,
        # spielbare Figuren bekommen IN JEDEM Fenster ZUERST eine
        # Initiative-Chance -- unabhaengig davon, ob ein anderer Tisch
        # gebunden/aktiv/fortsetzbar bleibt (B1: Fix1 gewann bisher
        # STRUKTURELL immer gegen Fix2, solange ein gebundener Tisch
        # aktiv war). Nur die fuer DIESEN Lauf tatsaechlich spielbaren
        # freien Figuren (ai_personas-Schnitt) zaehlen hier; `free` (ALLE
        # spielbereiten, ungebundenen Mitglieder) bleibt fuer die Lobby-
        # Sichtbarkeit/Beitrittsliste massgeblich. `candidate_ids` (unten,
        # STEP 1) nutzt seit dem P2-Fix (BL1-FIX-SPEC-R4 2026-10-21)
        # DIESES `free_selectable` statt `free` -- eine ausgewaehlte
        # Persona darf nur noch andere AUSGEWAEHLTE Personas einladen,
        # sonst blieb ein Angebot an eine ausgeschlossene/nicht ausgewaehlte
        # freie Persona offen stehen (sie ist nicht im `scheduler_pool`,
        # ihre Zustimmung wird nie eingeholt) und hielt die ausgewaehlte
        # Gruppe bis zur Idle-Grenze fest. TUI-Default `ai_personas is
        # None` aendert nichts (identisch zu allen freien Mitgliedern).
        free_selectable = [
            r for r in free if ai_personas is None or r.persona_key in ai_personas
        ]

        # STEP 1 -- Freie Initiative ZUERST (nur wenn es ueberhaupt eine
        # spielbare freie Figur gibt; sonst gibt es niemanden, den der
        # Scheduler befragen koennte, und STEP 1 wird ohne Effekt
        # uebersprungen -- STEP 2 unten greift dann direkt).
        if free_selectable:
            limit = session._lobby_initiative_step_limit()
            # G1 (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, REVIEW-
            # HEADLESS-BETRIEBSGRENZEN.md Probe 02): die explizite KI-Auswahl
            # (`ai_personas`) gilt bereits HIER, an der Initiative-/Consent-
            # Schleife -- vorher wurde der Scheduler ueber ALLE freien Mitglieder
            # aufgebaut und `persona_driver_factory(pk)` fuer JEDES freie
            # Mitglied gerufen, `ai_personas` griff erst in `play_bound_table`
            # (also NACHDEM ein nicht ausgewaehltes Mitglied bereits eine echte
            # Initiative-/Consent-Anfrage erhalten hatte). `free` (ALLE
            # spielbereiten, ungebundenen Mitglieder) bleibt fuer die Lobby-
            # Sichtbarkeit/Beitrittsliste/`candidate_ids` unveraendert (grosse
            # Lobby bleibt sichtbar, ein ausgewaehltes Mitglied darf weiterhin
            # ein NICHT ausgewaehltes Mitglied in `wants` einladen) -- NUR der
            # Scheduler-/Treiber-Pool, der tatsaechlich initiativ/konsentierend
            # BEFRAGT wird, ist auf `ai_personas` eingeschraenkt. `ai_personas is
            # None` (TUI-Default) aendert nichts (identisch zu allen freien
            # Mitgliedern, H01 unveraendert). Ein Angebot, das ausschliesslich
            # die Zustimmung eines NICHT ausgewaehlten Mitglieds noch braucht,
            # wird dadurch strukturell nie automatisch beantwortet -- es bleibt
            # als offenes Angebot im Log stehen (kein Simulieren, keine
            # Restgruppe, s. Moduldocstring).
            scheduler_pool = [
                r.persona_key for r in free if ai_personas is None or r.persona_key in ai_personas
            ]
            scheduler = FairScheduler(scheduler_pool)
            already_acted = {
                ev.get("proposed_by") or ev.get("from")
                for ev in offer_events if ev.get("type") == "offer"
            }
            for already in already_acted:
                scheduler.pause(already)

            turn_counts: dict[str, int] = {}
            candidate_ids: list[str] = []

            for _ in range(limit):
                pk = scheduler.next_initiative()
                if pk is None:
                    session._print(
                        "Lobby-Initiative: alle Mitglieder pausiert/keiner mehr aktiv — kontrollierte "
                        "Rueckkehr, kein leerer Inferenzloop."
                    )
                    break
                steps_taken += 1
                turn_idx = turn_counts.get(pk, 0)
                turn_counts[pk] = turn_idx + 1
                driver = session.persona_driver_factory(pk)
                own_ctx = session._own_system_context(pk)
                pending = lobby_service.open_offer_for(pk, offer_events)
                ts_now = datetime.datetime.now().isoformat()
                table_view = {"lobby_messages": lobby_service.lobby_messages_for(lobby, pk)}
                try:
                    if pending is not None:
                        proposer_display = pending.proposed_by or pending.from_persona
                        extra_notes = ""
                        if pending.activity:
                            extra_notes += f"Vorgeschlagene Aktivitaet: {pending.activity}\n"
                        if pending.leader == pk:
                            extra_notes += (
                                "Zusaetzlich wirst du gebeten, diesen Tisch als LEADER zu fuehren -- "
                                "eine Zusage (accept) zu dieser Einladung gilt zugleich als Zusage "
                                "zur Leaderrolle, eine Ablehnung lehnt BEIDES ab.\n"
                            )
                        ctx = {
                            "system": own_ctx,
                            "user": (
                                f"'{proposer_display}' schlaegt eine gemeinsame Runde mit dir vor "
                                f"(gewuenschte Teilnehmer: {sorted(pending.wants)}).\n"
                                + extra_notes
                                + decision_contract_instruction(pending.offer_id, pk)
                            ),
                            "decision_contract": {"offer_id": pending.offer_id, "participant_id": pk},
                            "table_view": table_view,
                        }
                        decision, block_reason = lobby_service.request_admitted_decision(
                            session.run_dir, driver, ctx, role="lobby_offer_response", participant=pk,
                            section_id=window_section_id, turn_idx=turn_idx,
                        )
                    else:
                        # P2-Fix (BL1-FIX-SPEC-R4 2026-10-21): `candidate_ids`
                        # (die Einladungs-/Wunschliste) nutzt `free_selectable`
                        # (bereits auf `ai_personas` beschraenkt, s. Kommentar
                        # oben) statt `free` -- sonst kann eine ausgewaehlte
                        # Persona eine ausgeschlossene/nicht ausgewaehlte freie
                        # Persona in `wants` einladen.
                        candidate_ids = [r.persona_key for r in free_selectable if r.persona_key != pk]
                        ctx = {
                            "system": own_ctx,
                            "user": initiative_proposal_contract_instruction(candidate_ids),
                            "table_view": table_view,
                        }
                        decision, block_reason = lobby_service.request_admitted_decision(
                            session.run_dir, driver, ctx, role="lobby_initiative", participant=pk,
                            section_id=window_section_id, turn_idx=turn_idx,
                        )
                except Exception as e:  # Transportfehler -- kein Auto-Accept, kontrollierter Stop.
                    msg = f"Lobby-Initiative: Anfrage an '{pk}' fehlgeschlagen ({e}) — Initiative gestoppt."
                    session._print(msg)
                    stop_kind, stop_reason = LobbyOutcomeKind.STOPPED, msg
                    break
                if decision is None:
                    msg = f"Lobby-Initiative gestoppt (Admission-Gate: {block_reason}) — kein weiterer Request."
                    session._print(msg)
                    stop_kind, stop_reason = LobbyOutcomeKind.STOPPED, msg
                    break

                if pending is not None:
                    if decision.decision in ("accept", "reject"):
                        decision_kind = decision.decision
                    else:
                        decision_kind, _explanation = interpret_decision_contract(
                            decision.text, offer_id=pending.offer_id, participant_id=pk,
                        )
                    session._append_invitation_log({
                        "type": "response", "offer_id": pending.offer_id, "ts": ts_now,
                        "from": pk, "decision": decision_kind, "origin_source": decision.origin_source,
                    })
                    offer_events.append({
                        "type": "consent", "offer_id": pending.offer_id, "from": pk,
                        "accept": decision_kind == "accept",
                    })
                    session._print(f"'{pk}' antwortet auf Angebot '{pending.offer_id}': {decision_kind}.")
                else:
                    kind, wants, extra = interpret_initiative_proposal(decision.text, candidate_ids=candidate_ids)
                    lobby_service.post_lobby_message_if_present(lobby, pk, extra.get("message") if extra else None)
                    if kind == "pause":
                        scheduler.pause(pk)
                        session._print(f"'{pk}' pausiert dieses Lobbyfenster.")
                        continue
                    if kind != "propose":
                        session._print(f"'{pk}': keine gueltige Initiativantwort ({decision.text!r}) — kein Angebot.")
                        continue
                    leader = (extra or {}).get("leader") or "self"
                    activity = (extra or {}).get("activity")
                    offer_from = pk if leader == "self" else leader
                    offer_wants = list(wants)
                    if leader != "self":
                        if leader not in offer_wants:
                            offer_wants.append(leader)
                        if pk not in offer_wants:
                            offer_wants.append(pk)
                    offer_id = lobby_service.offer_id_for(window_section_id, pk, turn_idx)
                    offer_record = {
                        "type": "offer", "offer_id": offer_id, "ts": ts_now, "from": offer_from,
                        "wants": list(offer_wants), "window_id": window_section_id,
                    }
                    if leader != "self":
                        offer_record["leader"] = leader
                        offer_record["proposed_by"] = pk
                    if activity:
                        offer_record["activity"] = activity
                    session._append_invitation_log(offer_record)
                    offer_events.append({
                        "type": "offer", "id": offer_id, "from": offer_from, "wants": list(offer_wants),
                        "window_id": window_section_id,
                        "leader": leader if leader != "self" else None,
                        "activity": activity, "proposed_by": pk if leader != "self" else None,
                    })
                    if leader != "self":
                        session._append_invitation_log({
                            "type": "response", "offer_id": offer_id, "ts": ts_now,
                            "from": pk, "decision": "accept",
                            "origin_source": "lobby_initiative:proposer-self-consent",
                        })
                        offer_events.append({"type": "consent", "offer_id": offer_id, "from": pk, "accept": True})
                    session._print(f"'{pk}' schlaegt eine Runde vor (wants={wants}, leader={leader}).")

                derivation = core_store.derive_group_and_leader(offer_events)
                if derivation.leader is not None:
                    confirmed_derivation = derivation
                    break

        # R4-M3-Fix (CRITIC-REPORT-R2.md BLOCKER M3, SPIELFLUSS-SPEC.md "M3
        # durch explizites Surfacen"): ein in STEP 1 gesetzter Stopgrund (ein
        # echter Transportfehler ODER ein Admission-Gate-Block fuer eine
        # freie Figur) hat Vorrang vor einem erst in STEP 2 "nebenbei"
        # gefundenen fortsetzbaren Tisch -- sonst verschluckt ein harmloser
        # Resume-Fund denselben echten Fehler, den STEP 1 bereits erkannt
        # hat (vorher: STEP 2 konnte unbedingt mit `_resume_bound_table(...)`
        # zurueckkehren, OHNE `stop_kind`/`stop_reason` je zu lesen -- der
        # Aufrufer bekam `SECTION_COMPLETED` statt `STOPPED`, der Fehler war
        # fuer ihn unsichtbar).
        if stop_kind is not None:
            lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
            return LobbyWindowOutcome(kind=stop_kind, reason=stop_reason or "", window_id=window_section_id)

        # STEP 2 -- gebundenen Tisch wiederaufnehmen/fortsetzen, NUR wenn
        # STEP 1 (falls gelaufen) keinen neuen Tisch gebildet hat. Der
        # Resume-Body bleibt inhaltlich UNVERAENDERT (Recovery/Ernte
        # bleibt strikt vorrangig vor Mid-Play-Fortsetzung, s. Fix1-
        # Kommentar unten).
        if confirmed_derivation is None and bound:
            # R4-Fix1 (02_JETZT_ENTWICKELN.md §1, ABSCHNITT-A-ROOTCAUSE.md §5),
            # nach R4-FixB1 (B1-FIX-SPEC.md) HIER in STEP 2 (nach STEP 1):
            # die Recovery-/Ernte-Wiederaufnahme ist bereits oben im PRE-STEP
            # (strikt vorrangig, UNVERAENDERT) geprueft worden und hat NICHTS
            # geliefert -- erst DANN einen bereits BEGONNENEN (nicht-leeres
            # sl_log), aktiven, noch nicht abgeschlossenen Tisch fuer einen
            # WEITEREN regulaeren Zug aufgreifen, und zwar NACH der freien
            # Runde (STEP 1), damit freie Figuren nicht mehr abgeschnitten
            # werden (B1). Der Resume-Body (`_resume_bound_table`) ist fuer
            # einen bereits gespielten Tisch bereits korrekt (F5/A6:
            # existierender offener Tisch wird samt echtem sl_log geladen;
            # `SectionRuntime` setzt bei `len(sl_log)` fort).
            resumable = core_store.find_bound_active_continuable_table(
                session.run_dir,
                {r.persona_key: r.chrononaut_id for r in roster if r.ready},
                bound,
                ai_personas=ai_personas,
            )
            if resumable is not None:
                return _resume_bound_table(resumable)
            else:
                open_ids = ", ".join(sorted(set(bound.values())))
                # R4-FixB1 (B1-FIX-SPEC.md Step 2): `free_selectable` ist
                # bereits VOR STEP 1 oben berechnet (gilt fuer beide Steps
                # identisch) -- hier nur noch verwenden, nicht neu bilden.
                if not free_selectable:
                    # Kein spielbares freies Mitglied -> reine Diagnose-
                    # Rueckkehr UNVERAENDERT wie bisher (kein Auto-Start, kein
                    # zweiter Tisch, kein Unlock, kein Persona-Request). Der
                    # ambige-Autoritaet-Fall und der Hard-Interrupt-Resume mit
                    # ausschliesslich gebundenen ausgewaehlten Personas bleiben
                    # damit exakt die bisherige kontrollierte Diagnose. Fenster
                    # schliessen.
                    reason = (
                        f"Lobby-Initiative: Tisch(e) {open_ids} bereits gebunden, Fortsetzung/"
                        "Resolution aus den vorhandenen Belegen nicht zuverlaessig zuordenbar "
                        "(ungeklaert/ausstehend) — kein automatischer Spielstart, kein zweiter "
                        "Tisch, kontrolliert offen."
                    )
                    session._print(reason)
                    lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
                    return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason)
                # R4-FixB1 (vormals R4-Fix2, 02_JETZT_ENTWICKELN.md §1,
                # ABSCHNITT-A-ROOTCAUSE.md §3/§5, B1-FIX-SPEC.md Step 2): es
                # GIBT spielbare freie, ungebundene Figuren -- STEP 1 oben hat
                # sie bereits befragt (Interleaving: freie Initiative zuerst,
                # s. B1-FIX-SPEC.md), nur ohne bestaetigten Konsens. Ein
                # gebundener Tisch, der weder wiederaufnehmbar (Recovery/Ernte)
                # noch fortsetzbar (Mid-Play) ist, hat deren Initiative darum
                # NICHT abgeschnitten. Es gibt KEINEN Zwangsbeitritt zum
                # gebundenen Tisch: STEP 1 befragt ausschliesslich den `free`-
                # Pool, und `create_table_from_offer_log` weist einen bereits
                # gebundenen (gelockten) Chrononauten ohnehin ab. Das
                # Lobbyfenster bleibt dafuer bewusst OFFEN (KEIN clear_window_
                # open hier) -- die terminale Pruefung unten verwaltet/
                # schliesst es wie im normalen initiativen Fall.
                reason = (
                    f"Lobby-Initiative: Tisch(e) {open_ids} bereits gebunden, Fortsetzung/"
                    "Resolution aus den vorhandenen Belegen nicht zuverlaessig zuordenbar "
                    "(ungeklaert/ausstehend) — kein automatischer Spielstart, kein zweiter "
                    "Tisch; freie, ungebundene Figuren hatten in diesem Fenster bereits ihre "
                    "Initiative (R4-FixB1 Interleaving, STEP 1 vor STEP 2)."
                )
                session._print(reason)
                # KEIN return -> Durchfall zur terminalen Pruefung unten.

        if not free:
            lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
            reason = (
                "Lobby-Initiative: niemand frei/spielbereit (alle noch nicht fertig oder bereits "
                "tischgebunden) — kein Initiativschritt, keine Ersatzgruppe."
            )
            session._print(reason)
            return LobbyWindowOutcome(kind=LobbyOutcomeKind.NO_CONSENSUS, reason=reason, window_id=window_section_id)

    if confirmed_derivation is None:
        lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
        session._print(
            f"Lobby-Initiative beendet ({steps_taken} Initiativschritte) ohne bestaetigten Tisch "
            "— kontrollierte Rueckkehr, keine Ersatzgruppe."
        )
        final_kind = stop_kind or LobbyOutcomeKind.NO_CONSENSUS
        final_reason = stop_reason or (
            f"Lobby-Initiative beendet ({steps_taken} Initiativschritte) ohne bestaetigten Tisch "
            "— kontrollierte Rueckkehr, keine Ersatzgruppe."
        )
        return LobbyWindowOutcome(kind=final_kind, reason=final_reason, window_id=window_section_id)

    for pk in confirmed_derivation.members:
        try:
            resolved = session._resolve_member(pk)
        except _ActiveSaveUnresolved:
            reason = (
                f"Lobby-Initiative: Spielstand von '{pk}' gerade nicht lesbar — kein "
                "Tischstart, bis die tatsaechliche Autoritaet geklaert ist."
            )
            session._print(reason)
            return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason, window_id=window_section_id)
        if resolved is None:
            reason = f"Lobby-Initiative: '{pk}' hat keine abgeschlossene Figur mehr — kein Tischstart."
            session._print(reason)
            return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason, window_id=window_section_id)
        active_saves[pk], chrononaut_ids[pk] = resolved

    table_id = "lobby-" + "-".join(sorted(confirmed_derivation.members))
    table, derivation = core_store.create_table_from_offer_log(
        lobby, table_id, offer_events, chrononaut_ids,
    )
    if table is None:
        try:
            lobby_service.append_offer_resolution(
                session.run_dir, confirmed_derivation.source_offer_id, outcome="no_table",
            )
        except OSError as e:
            reason = (
                f"Lobby-Initiative: Tisch konnte nicht angelegt werden ({derivation.reason}), UND die "
                f"Resolution dafuer konnte nicht dauerhaft geschrieben werden ({e}) — kontrolliert "
                "gestoppt, kein Verbrauch dieser Zustimmung fuer den naechsten Aufruf behauptet."
            )
            session._print(reason)
            return LobbyWindowOutcome(kind=LobbyOutcomeKind.STOPPED, reason=reason)
        lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)
        reason = f"Lobby-Initiative: Tisch konnte nicht angelegt werden: {derivation.reason}"
        session._print(reason)
        return LobbyWindowOutcome(kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason)
    if derivation.source_offer_id is None:
        mismatch_reason = resume_consistency_hold_reason(
            session, lobby, table, confirmed_derivation, chrononaut_ids,
        )
        if mismatch_reason is not None:
            reason = (
                f"Lobby-Initiative: Tisch {table.table_id} ist gebunden, aber die Belege "
                f"widersprechen sich ({mismatch_reason}) — kontrolliert offen, kein "
                "automatischer Spielstart, kein Unlock, keine neue Resolution."
            )
            session._print(reason)
            return LobbyWindowOutcome(
                kind=LobbyOutcomeKind.OPEN_WITH_REASON, reason=reason, table_id=table.table_id,
            )
    try:
        lobby_service.append_offer_resolution(
            session.run_dir, confirmed_derivation.source_offer_id, outcome="table_bound",
            table_id=table.table_id,
        )
    except OSError as e:
        reason = (
            f"Lobby-Initiative: Tisch {table.table_id} angelegt, aber die Resolution-Bindung "
            f"konnte nicht dauerhaft geschrieben werden ({e}) — kontrolliert gestoppt, kein "
            "Spielstart aus einer nicht durabel gebundenen Zustimmung (naechster Aufruf nimmt "
            "diesen Tisch wieder auf, statt einen zweiten aus derselben Zustimmung anzulegen)."
        )
        session._print(reason)
        return LobbyWindowOutcome(kind=LobbyOutcomeKind.STOPPED, reason=reason, table_id=table.table_id)
    lobby_service.clear_window_open(session.run_dir, community_id, window_section_id)

    return play_bound_table(
        session, lobby, table, offer_events, confirmed_derivation.source_offer_id, active_saves,
        ai_personas=ai_personas,
    )
