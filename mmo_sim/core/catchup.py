#!/usr/bin/env python3
"""
mmo_sim/core/catchup.py — spielergesteuerter Catch-up-/Vorspiel-Orchestrator
(SPIELFLUSS-SPEC.md, Flo-GO 2026-10-21).

Catch-up ("ausgewaehlte zurueckliegende Personas spielen nach, bis sie deine
Abschnittszahl erreichen") und Vorspielen ("ausgewaehlte Personas spielen
JETZT ihren eigenen naechsten Abschnitt") sind laut Spec DIESELBE Maschine,
nur ein anderer Auslöse-Moment/`target`-Aufruf -- `run_catch_up` ist darum
der EINE Einstieg fuer beide, KEIN zweiter Code-Pfad (Leitprinzip "KISS,
nicht verkuenstlen").

Schluessel-Invariante (Spec, Abschnitt "Schluessel-Invariante", zwingend):
Kandidaten = (gewaehlte, bereite Personas) MINUS (Mitglieder des aktuellen/
zuletzt gespielten Tisches des auslösenden Spielers) MINUS (bereits auf/
ueber Ziel). Wer mit dir am Tisch war, ist bereits gleichauf -- ein
erneutes Nachziehen wuerde ihn überzaehlig machen.

Reuse (Leitprinzip "Reuse vor Neubau"): `core.lobby_flow.run_lobby_window`
ist die EINZIGE Spielstart-/Tischmechanik, die dieses Modul aufruft (kein
eigener GM-/Persona-Aufruf, kein zweiter Tischcode) -- NUR der `ai_personas`-
Pool, der ihr pro Fenster uebergeben wird, wird hier gesteuert (eingeschraenkt
auf die noch unter Ziel liegenden Kandidaten, Fenster fuer Fenster kleiner
werdend, sobald einzelne Kandidaten ihr Ziel erreichen).

B2/M4 (CRITIC-REPORT-R2.md) im Catch-up-Kontext: `run_lobby_window`s
PRE-STEP/STEP-2-Finder koennen weiterhin unbedingt einen gebundenen,
`WAITING_HUMAN`-blockierten Tisch waehlen (B2) bzw. einen zweiten,
gleichzeitig gebundenen Tisch uebersehen, solange ein erster fortsetzbar
bleibt (M4, "selbstheilend" sobald der erste schliesst, s. CRITIC-REPORT-
R2.md). DIESER Orchestrator macht beides gegenstandslos, OHNE die Finder
selbst anzufassen (Risiko fuer `test_r2d_lobby_resume_belegkette_guard.py`
vermieden, s. SPIELFLUSS-IMPL-REPORT.md "Offenes/Unsicheres"):
- B2: ein `WAITING_HUMAN`-Fenster wird HIER erkannt, der blockierte Tisch
  wird fuer den Rest DIESES Aufrufs aus dem Kandidatenpool entfernt (kein
  Monopol mehr -- der naechste Fensteraufruf bekommt einen kleineren
  `ai_personas`-Pool ohne diese Mitglieder, andere Kandidaten kommen zum
  Zug) statt denselben blockierten Tisch endlos erneut anzufragen.
- M4: der Orchestrator ruft `run_lobby_window` so lange erneut auf (bis
  Ziel/Sicherheits-Cap), dass ein zuerst fortsetzbarer Tisch Zeit hat,
  vollstaendig zu schliessen -- danach wird ein zweiter, bisher uebersehener
  gebundener Tisch fuer PRE-STEP wieder sichtbar (`len(candidate_ids)==1`).
  Die alte Lab-Schleife (`lab/cli.py`, VOR dieser Aenderung) konnte das
  wegen ihrer kleinen `--max-idle-windows`-Grenze als PRIMAERE Terminierung
  oft gar nicht erleben; hier ist die Fenstergrenze ein groszuegiger
  Sicherheits-Cap, kein frueher Abbruch.

M3 (CRITIC-REPORT-R2.md): ein `LobbyOutcomeKind.STOPPED`-Fenster wird HIER
explizit gesurfacet (`CatchUpReport.stopped`/`stopped_reason`) und beendet
die Schleife SOFORT -- kein Weiterversuchen, kein verschluckter Fehler
(ergaenzt den Fix in `lobby_flow.py` selbst, der verhindert, dass `STOPPED`
dort bereits vor Rueckgabe durch einen "nebenbei" gefundenen Tisch
ueberschrieben wird)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from . import lobby_flow
from . import lobby_service
from . import store as core_store

# Grosszuegige, aber endliche Sicherheits-Caps (Fix3-Charakter: Sicherheit,
# NICHT die primaere Terminierung -- die ist "alle Kandidaten am Ziel").
DEFAULT_MAX_WINDOWS = 200
DEFAULT_IDLE_SAFETY_CAP = 8


@dataclass
class CatchUpReport:
    """Ehrlicher Bericht (SPIELFLUSS-SPEC.md: "wer wie viele Abschnitte,
    Endzaehlung, blockiert/kein Fortschritt — ehrlich"). `notes` ist
    menschlich lesbar (wie `LobbyWindowOutcome.reason`), `blocked` ist
    maschinenlesbar (persona_keys, die ihr `per_target` NICHT erreicht
    haben -- leer heisst vollstaendiger Erfolg, sofern `stopped` auch
    `False` ist).

    P3-Fix (BL1-FIX-SPEC-R4 2026-10-21): `unready` (ANS ENDE angehaengt,
    Default `[]` -- bestehende Positionsargument-Konstruktionen bleiben
    unveraendert aufrufbar) listet die ausgewaehlten (`selected`)
    Mitglieder, die NICHT spielbereit sind (`sorted(set(selected) -
    ready_keys)`), in JEDEM Rueckgabepfad gesetzt. Zweck: `lab/cli.py`
    kann damit eine leere `candidates`-Menge ehrlich von echter
    Abschnitts-Paritaet unterscheiden (sonst unbeschraenkter Null-Arbeits-
    Loop, s. dortiger Fix)."""

    candidates: list[str]
    start_counts: dict[str, int]
    end_counts: dict[str, int]
    per_target: dict[str, int]
    windows_run: int
    stopped: bool
    stopped_reason: str | None
    blocked: list[str]
    notes: list[str] = field(default_factory=list)
    unready: list[str] = field(default_factory=list)

    @property
    def reached_target(self) -> bool:
        return not self.blocked and not self.stopped


def ready_persona_keys(session) -> set[str]:
    """Minimal-Reuse von `lobby_flow.run_lobby_window`s Roster-Aufbau (NUR
    die bereits bestaetigten, spielbereiten Personas -- kein Tisch-/
    Fenster-Seiteneffekt, kein zweiter Community-Bootstrap). Liefert eine
    leere Menge, wenn (noch) keine bestaetigte Community existiert (ehrlich,
    kein Erraten)."""
    from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
    from ..ui.tui import _ActiveSaveUnresolved

    community_id = f"community-{session.participant_id}"
    community_dir = session.run_dir / "community"
    bootstrap = peek_bootstrap(community_dir, community_id)
    if bootstrap is None or not bootstrap.personas_written:
        return set()

    def _resolve_for_roster(pk: str):
        try:
            return session._resolve_member(pk)
        except _ActiveSaveUnresolved:
            return None

    roster = lobby_service.community_roster(
        session.run_dir, bootstrap.personas_written, session.onboarding_dir, _resolve_for_roster,
    )
    return {r.persona_key for r in roster if r.ready}


def run_catch_up(
    session, *, selected: set[str], current_table_members: set[str],
    target: int | None = None, max_rounds: int | None = None,
    max_windows: int = DEFAULT_MAX_WINDOWS, idle_safety_cap: int = DEFAULT_IDLE_SAFETY_CAP,
    on_window=None,
) -> CatchUpReport:
    """Treibt ausgewaehlte, zurueckliegende Personas gezielt weiter -- Catch-up
    (`target=None`: Ziel = aktuelle Abschnittszahl von `session.
    participant_id`, dem auslösenden Spieler) UND Vorspielen (`max_rounds`:
    jeder Kandidat spielt bis zu `max_rounds` Abschnitte ÜBER seine EIGENE
    aktuelle Zahl hinaus, unabhaengig vom Spieler) laufen durch DIESELBE
    Schleife. Ein explizites `target` (absolute Zahl) deckt den dritten,
    seltener gebrauchten Fall ab (z.B. Headless-Lab-Runden, s.
    `lab/cli.py::_run_controller`, das pro Runde ein konkretes `target`
    setzt, weil es keinen "auslösenden Spieler" mit eigenem Save gibt).

    Kandidaten = `selected` ∩ bereite Personas ∩ NICHT in
    `current_table_members` ∩ (eigene Abschnittszahl < individuelles Ziel)
    -- die Schluessel-Invariante (Spec) ist durch das `current_table_
    members`-Minus HART erzwungen, nicht nur empfohlen: ein Mitglied dieser
    Menge taucht NIEMALS in `ai_personas` fuer irgendein Fenster dieses
    Aufrufs auf.

    Terminiert, sobald ALLE Kandidaten ihr individuelles Ziel erreicht haben
    (Erfolg), ODER ein `STOPPED`-Fenster auftritt (M3 -- sofortiger Abbruch,
    `stopped=True`), ODER kein Kandidat mehr ohne menschliche Entscheidung
    weiterkommt (`idle_safety_cap` aufeinanderfolgende Fenster ohne
    Fortschritt -- Sicherheits-Cap, NICHT die primaere Terminierung), ODER
    die harte Fenstergrenze `max_windows` erreicht ist (zweiter, grosszuegiger
    Sicherheits-Cap gegen echte Endlosfaelle).

    `on_window` (optional): wird nach JEDEM internen `run_lobby_window`-
    Aufruf mit dem jeweiligen `LobbyWindowOutcome` aufgerufen -- reiner
    Diagnose-Hook, KEIN Kontrollfluss (Rueckgabewert wird ignoriert). Reuse
    fuer `lab/cli.py`s bestehende `_write_last_window`-Diagnose (Fix aus
    Bau-GO 2026-09-27): ohne diesen Hook wuerde `lab status`/`lab attach`
    erst nach dem GESAMTEN Catch-up-Aufruf (potenziell viele Fenster) ein
    neues `last_window` sehen, statt wie bisher nach jedem einzelnen."""
    if session.run_dir is None:
        return CatchUpReport(
            candidates=[], start_counts={}, end_counts={}, per_target={},
            windows_run=0, stopped=True,
            stopped_reason="keine Laufumgebung konfiguriert (run_dir fehlt) -- kein Catch-up.",
            blocked=[], unready=sorted(selected),
        )

    run_dir = session.run_dir
    counts = core_store.sections_played_by_participant(run_dir)
    ready_keys = ready_persona_keys(session)
    unready = sorted(set(selected) - ready_keys)
    base_candidates = (set(selected) & ready_keys) - set(current_table_members)

    if target is not None:
        per_target = {pk: target for pk in base_candidates}
    elif max_rounds is not None:
        per_target = {pk: counts.get(pk, 0) + max_rounds for pk in base_candidates}
    else:
        trigger_count = counts.get(session.participant_id, 0)
        per_target = {pk: trigger_count for pk in base_candidates}

    candidates = sorted(pk for pk in base_candidates if counts.get(pk, 0) < per_target[pk])
    start_counts = {pk: counts.get(pk, 0) for pk in candidates}

    if not candidates:
        # P3-Fix: den leeren-Kandidaten-Fall ehrlich differenzieren -- leer
        # WEIL (mindestens teilweise) unbereit, statt pauschal "bereits
        # Paritaet" (das war fuer vollstaendig unbereite Auswahlen falsch
        # und fuehrte im Lab-Loop zu einem unbeschraenkten Null-Arbeits-
        # Loop mit falschem DONE, s. `lab/cli.py`).
        if base_candidates:
            note = (
                f"Keine Kandidaten unter Ziel -- bereits Paritaet fuer die spielbereiten "
                f"ausgewaehlten Teilnehmer ({sorted(base_candidates)}), kein Catch-up noetig."
            )
            if unready:
                note += f" Nicht spielbereit (unberuehrt, kein Ziel gesetzt): {unready}."
        elif unready:
            note = (
                f"Keine spielbereiten ausgewaehlten Teilnehmer (unready={unready}) -- nichts "
                "ausfuehrbar, kein Catch-up/Vorspielen moeglich."
            )
        else:
            note = (
                "Keine Kandidaten -- alle ausgewaehlten Mitglieder sind Teil des aktuellen/"
                "zuletzt gespielten Tisches (Schluessel-Invariante), kein Catch-up noetig."
            )
        return CatchUpReport(
            candidates=[], start_counts={}, end_counts={}, per_target={},
            windows_run=0, stopped=False, stopped_reason=None, blocked=[],
            notes=[note], unready=unready,
        )

    notes: list[str] = []
    windows_run = 0
    stopped = False
    stopped_reason: str | None = None
    idle = 0
    blocked_this_run: set[str] = set()
    # BL1-FIX (sekundaer, Ehrlichkeit): Tische, die PRE-STEP in einem Fenster
    # geliefert hat, deren Mitglieder aber NICHT mit `remaining` ueberlappen
    # (ein fuer DIESEN Aufruf fremder, nicht ausgewaehlter Tisch) -- NACH dem
    # primaeren Fix (store.find_bound_active_unplayed_table`s `ai_personas`-
    # Filter) sollte das kaum mehr auftreten, bleibt aber als ehrlicher
    # Report-Hinweis erhalten (z.B. falls STEP 2s `find_bound_active_
    # continuable_table`, das bewusst KEINEN eigenen ai_personas-Filter hat,
    # einen fremden Tisch ueber `play_bound_table`s Gate als WAITING_HUMAN
    # zurueckgibt).
    foreign_blocked_tables: set[str] = set()
    sl_len_seen = core_store.table_progress_lengths(run_dir)

    while True:
        counts = core_store.sections_played_by_participant(run_dir)
        remaining = sorted(
            pk for pk in candidates if counts.get(pk, 0) < per_target[pk] and pk not in blocked_this_run
        )
        if not remaining:
            break
        if windows_run >= max_windows:
            notes.append(
                f"Sicherheits-Fenstergrenze ({max_windows}) erreicht -- kontrollierter Abbruch, "
                f"Rest bleibt zurueck: {remaining}."
            )
            break

        windows_run += 1
        outcome = lobby_flow.run_lobby_window(session, ai_personas=frozenset(remaining))
        if on_window is not None:
            on_window(outcome)
        notes.append(f"Fenster {windows_run} (Pool {remaining}): {outcome.kind.value} -- {outcome.reason}")

        if outcome.kind == lobby_flow.LobbyOutcomeKind.STOPPED:
            stopped = True
            stopped_reason = outcome.reason
            break

        if outcome.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED:
            idle = 0
            continue

        progressed = False
        if outcome.table_id is not None:
            cur_lengths = core_store.table_progress_lengths(run_dir)
            cur_len = cur_lengths.get(outcome.table_id, 0)
            prev_len = sl_len_seen.get(outcome.table_id, 0)
            if cur_len > prev_len:
                sl_len_seen[outcome.table_id] = cur_len
                progressed = True

        newly_blocked: set[str] = set()
        if outcome.kind == lobby_flow.LobbyOutcomeKind.WAITING_HUMAN and outcome.table_id is not None:
            # B2 (CRITIC-REPORT-R2.md, im Catch-up-Kontext): dieser Tisch kann
            # ohne eine menschliche Entscheidung nicht weiter -- NICHT erneut
            # anfragen (das waere Monopolisierung), sondern seine Kandidaten
            # fuer den Rest dieses Aufrufs ueberspringen, andere Kandidaten
            # bekommen die naechsten Fenster.
            try:
                stuck_table = core_store.Table.load(run_dir, outcome.table_id)
                stuck_members = set(stuck_table.members) & set(remaining)
            except (OSError, json.JSONDecodeError, KeyError):
                # N2 (CRITIC-REPORT-R3.md): `KeyError` ergaenzt, konsistent mit
                # den uebrigen Store-Helfern -- eine beschaedigte Tischdatei
                # (fehlender Pflichtschluessel) darf den gesamten Catch-up-
                # Lauf nicht mit einem rohen Traceback abbrechen; stattdessen
                # "kein Fortschritt fuer diesen Tisch" fuer dieses Fenster.
                stuck_table = None
                stuck_members = set()
            if stuck_members:
                newly_blocked = stuck_members - blocked_this_run
                blocked_this_run |= stuck_members
                notes.append(
                    f"Tisch {outcome.table_id} wartet auf eine menschliche Entscheidung -- "
                    f"{sorted(stuck_members)} fuer diesen Aufruf uebersprungen (kein Monopol)."
                )
            elif stuck_table is not None:
                # BL1-FIX (sekundaer, Ehrlichkeit, CRITIC-REPORT-R3.md): dieser
                # Tisch blockiert PRE-STEP, hat aber KEIN Mitglied in
                # `remaining` -- ein fuer DIESEN Aufruf fremder, nicht
                # ausgewaehlter Tisch. NICHT als generisches "kein Fortschritt
                # der eigenen Kandidaten" verbuchen, sondern ehrlich separat
                # ausweisen (s. `foreign_blocked_tables`/Abschluss-Hinweis
                # unten).
                foreign_blocked_tables.add(outcome.table_id)
                notes.append(
                    f"Tisch {outcome.table_id} wartet auf eine menschliche Entscheidung, hat aber "
                    f"KEIN Mitglied in der fuer diesen Aufruf ausgewaehlten Menge {remaining} -- "
                    "ein fremder, nicht ausgewaehlter Tisch blockiert PRE-STEP dieses Fenster "
                    "(wird NICHT den ausgewaehlten Kandidaten als eigenes Scheitern zugerechnet)."
                )

        if progressed or newly_blocked:
            # N1 (CRITIC-REPORT-R3.md): `idle` auch zuruecksetzen, wenn in
            # diesem Fenster NEU `blocked_this_run`-Mitglieder identifiziert
            # wurden -- das ist ehrlicher Fortschritt im Sinne "ein weiterer
            # blockierter Kandidat erkannt und aus dem Pool entfernt", nicht
            # nur echtes `sl_log`-Wachstum.
            idle = 0
            continue

        idle += 1
        if idle >= idle_safety_cap:
            abort_note = (
                f"Keine Fortschritt ueber {idle_safety_cap} Fenster (Sicherheits-Cap) -- "
                f"kontrollierter Abbruch, Rest bleibt zurueck: {remaining}."
            )
            if foreign_blocked_tables:
                abort_note += (
                    f" Hinweis (Ehrlichkeit): mindestens ein fremder, nicht ausgewaehlter Tisch "
                    f"{sorted(foreign_blocked_tables)} hat PRE-STEP in diesem Zeitraum wiederholt "
                    "blockiert -- der Abbruch ist nicht zwangslaeufig eigenes Scheitern von "
                    f"{remaining}."
                )
            notes.append(abort_note)
            break

    end_counts_full = core_store.sections_played_by_participant(run_dir)
    end_counts = {pk: end_counts_full.get(pk, 0) for pk in candidates}
    blocked = sorted(pk for pk in candidates if end_counts.get(pk, 0) < per_target[pk])

    return CatchUpReport(
        candidates=candidates, start_counts=start_counts, end_counts=end_counts,
        per_target=per_target, windows_run=windows_run, stopped=stopped,
        stopped_reason=stopped_reason, blocked=blocked, notes=notes, unready=unready,
    )
