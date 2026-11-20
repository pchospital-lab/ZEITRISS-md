#!/usr/bin/env python3
"""
mmo_sim/core/_section_completion_recovery.py — R12-AUTORECOVERY: reine,
zustandslose Suchfunktion fuer den automatischen dauerhaften
Abschluss-Wiederanschluss in `core/runtime.py:SectionRuntime.run_full_section`.

Kein neuer Dienst, keine zweite Saveautorität, kein Schreibzugriff -- dieses
Modul liest ausschliesslich das bereits im Prozess vorhandene `Table.sl_log`
(von `core/store.py:submit_to_sl` additiv um `section_id`, `chat_id` und
`expected_prev_ref_by_member` ergaenzt, s. dort) und entscheidet, ob darin
bereits eine durabel empfangene, aber noch nicht geplante Markerantwort fuer
GENAU die angefragte `section_id` steckt.

AR2 (01_ABSCHLUSSVERTRAG.md Teil A/C): DREI Ergebnisse statt eines blossen
`None`-Freibriefs --
    (None, None)        kein Abschlussbeleg fuer diese Section -- normaler
                         Spielweg (Aufrufer faehrt mit Anker/Import/Turn-
                         Schleife fort).
    (entry, None)        ein eindeutig positiv gebundener Abschlussbeleg --
                         der Aufrufer darf GENAU `entry` ernten.
    (None, hold_reason)  ein BEKANNTER Marker-/Abschlussbeleg mit fehlender/
                         kaputter/mehrdeutiger Bindung (fehlender Schnapp-
                         schuss, Legacy-Eintrag ohne jede Section-Bindung,
                         oder -- ueber `request_binding_error` -- eine
                         fehlende/beschaedigte/fremde/driftende Original-
                         Requestanbindung) -- kontrollierter HOLD, NIEMALS
                         ein neuer Spiel-/GM-Turn, KEINE Migration/Ernte.

Domaenenneutral: kennt weder "v7" noch ein festes Fuenf-Personen-Limit; der
Marker-String, die Vergleichsfunktion (`completion_marker_matches`) UND die
optionale Request-Bindungspruefung (`request_binding_error`) kommen vom
Aufrufer (`core/runtime.py`), der allein `core/request_ledger.py` kennt --
dieses Modul importiert es bewusst NICHT selbst (reine Such-/Entscheidungs-
funktion, I/O bleibt beim Aufrufer)."""
from __future__ import annotations

from typing import Callable

RequestBindingCheck = Callable[[dict], "str | None"]
"""Vom Aufrufer gebaute, reine Pruessfunktion: nimmt den gefundenen sl_log-
Eintrag, liefert `None`, wenn die ORIGINAL-Requestoperation (Id/Rolle/Tisch/
Section/Turn/Teilnehmer, gesendeter Inhalt UND exakt empfangener, unveraen-
derter Antworttext) positiv UND widerspruchsfrei gebunden ist, sonst einen
menschenlesbaren HOLD-Grund."""


EntryMatchCheck = Callable[[dict], bool]
"""Vom Aufrufer gebaute, reine OPTIONALE Zusatzpruefung (OPTION2-CMD,
FIX-SPEC-OPTION2-CMD.md §3): nimmt den gefundenen sl_log-Eintrag, liefert
True, wenn er -- UNABHAENGIG von `marker_matches` -- als kommando-gestuetzter
Abschlussbeleg gilt (z.B. `leader_message` war ein Save-Kommando UND
`content` traegt einen bindbaren Save-Block). Default `None` ergibt exakt
das bisherige Marker-only-Verhalten (bestehende Marker-Aufrufe/Tests
unveraendert)."""


def find_recoverable_entry(
    sl_log: list[dict], section_id: str, table_id: str, marker: str,
    marker_matches: Callable[[str, str, str, str], bool],
    *, request_binding_error: RequestBindingCheck | None = None,
    entry_matches: EntryMatchCheck | None = None,
) -> tuple[dict | None, str | None]:
    """Liefert `(entry, hold_reason)` -- s. Moduldocstring fuer die drei
    moeglichen Kombinationen.

    Kontrollierter Stopp statt Raten (AR04/AR05/AR06/AR11) -- JEDE der
    folgenden Bedingungen muss zutreffen, sonst HOLD statt stillschweigender
    Ernte ODER stillschweigendem Rueckfall auf einen neuen Spielturn:

    1. `sl_log` ist nicht leer -- sonst `(None, None)` (kein Abschlussbeleg,
       normaler Spielweg, z.B. der allererste Aufruf einer Section).
    2. NUR der JUENGSTE Eintrag (`sl_log[-1]`) ist ueberhaupt ein Kandidat --
       ein GM-Turn folgt im Normalfall nie auf einen bereits erkannten
       Marker-Treffer (der Normalpfad finalisiert/pinnt sofort); ein
       aelterer Eintrag derselben oder einer anderen Section wird deshalb
       NIE rueckwirkend herangezogen (keine Fremd-Section-Rueckgriffe).
    3. Der juengste Eintrag muss zu GENAU dieser Section gehoeren (`entry
       ["section_id"] == section_id`) ODER ueberhaupt KEINE Section-Bindung
       tragen (`None` -- ein Legacy-Eintrag aus der Zeit vor R12-AUTO-
       RECOVERY). Ein Eintrag mit einer ANDEREN, expliziten `section_id`
       gehoert zu einer fremden Section/einem fremden Lauf und wird
       uebersprungen (`(None, None)`, normaler Spielweg -- "keine Global-
       blockade fuer normale Tische ohne offenen Abschlussbezug").
    4. GENAU der `content` DIESES Eintrags (niemals `leader_message` oder
       ein Tisch-Chat-Eintrag -- Leader-/Operatorinput ist KEINE SL-Antwort)
       erfuellt `marker_matches(content, marker, table_id, section_id)`,
       exakt dieselbe Grammatikpruefung wie im ununterbrochenen Normalfall --
       ODER (OPTION2-CMD, additiv) ein uebergebenes `entry_matches(entry)`
       liefert True (kommando-gestuetzter Abschlussbeleg, s. `EntryMatchCheck`).
       Keiner der beiden Treffer => `(None, None)` (die Szene laeuft einfach
       weiter, kein Abschlussbeleg vorhanden).
    5. Traegt der Treffer ueberhaupt KEINE Section-Bindung (`entry_section
       is None`, Schritt 3), ist er -- UNABHAENGIG von jedem weiteren Feld
       -- per Definition unzureichend gebunden: `(None, hold_reason)`
       (Legacy, "keine Migration").
    6. Sonst muss der Eintrag ein (nicht-`None`) `expected_prev_ref_by_
       member` tragen -- fehlt dieser Schnappschuss (AR11), ist die Bindung
       ebenfalls unzureichend: `(None, hold_reason)` -- AR2 schliesst damit
       den vorherigen Fehlgriff, bei fehlendem Schnappschuss stillschweigend
       auf einen NEUEN Spielturn zurueckzufallen.
    7. Ist eine `request_binding_error`-Pruefung uebergeben, muss sie fuer
       `entry` `None` liefern (positiv gebundener, widerspruchsfreier,
       unveraenderter Original-Request/-Antwort) -- jeder zurueckgelieferte
       Grund wird 1:1 als `hold_reason` durchgereicht."""
    if not sl_log:
        return None, None
    entry = sl_log[-1]
    entry_section = entry.get("section_id")
    if entry_section not in (section_id, None):
        return None, None
    content = entry.get("content") or ""
    matched = marker_matches(content, marker, table_id, section_id)
    if not matched and entry_matches is not None:
        matched = entry_matches(entry)
    if not matched:
        return None, None
    if entry_section is None:
        # AR2 (Teil C): ein Legacy-Eintrag OHNE jede Section-Bindung ist per
        # Definition unzureichend gebunden -- UNABHAENGIG davon, ob er
        # zufaellig (synthetisch/fremd) einen Schnappschuss traegt. Niemals
        # automatisch adoptieren/migrieren, aber auch nicht wie "kein Beleg"
        # behandeln (das war der stillschweigende Rueckfall auf einen neuen
        # Spielturn, den AR2 schliesst).
        return None, (
            "Marker-/Abschlussbeleg gefunden, aber der Eintrag traegt ueberhaupt keine "
            "Section-Bindung (Legacy-Eintrag aus der Zeit vor R12-AUTORECOVERY) -- "
            "unzureichend gebunden, kontrollierter HOLD statt automatischer Ernte, "
            "Migration oder stillschweigendem neuen Spielturn."
        )
    if entry.get("expected_prev_ref_by_member") is None:
        return None, (
            "Marker-/Abschlussbeleg gefunden, aber ohne durabel gebundenen "
            "Generations-Schnappschuss ('expected_prev_ref_by_member' fehlt -- "
            "Legacy-Eintrag oder Aufrufer ohne R12-AUTORECOVERY-Bindung) -- "
            "unzureichende Bindung, kontrollierter HOLD statt automatischer "
            "Ernte oder stillschweigendem neuen Spielturn."
        )
    if request_binding_error is not None:
        reason = request_binding_error(entry)
        if reason is not None:
            return None, reason
    return entry, None


def find_pending_leader_export(
    sl_log: list[dict], section_id: str, leader_pid: str,
    harvest_own_export: EntryMatchCheck,
    is_explicit_save_command: Callable[[str | None], bool],
    *, request_binding_error: RequestBindingCheck | None = None,
) -> tuple[dict | None, str | None]:
    """ZR-R8-STRUKTURTEST-TERMINAL-RAG-20261120-R1 Stage 3 (03_FIXAUFTRAG.md
    §4, M12-Kernbug): findet einen bereits VORHANDENEN, noch nicht
    uebernommenen eigenen HQ-Export des Leaders IRGENDWO in `sl_log` DIESER
    Section -- nicht nur im juengsten Eintrag wie `find_recoverable_entry`
    (dessen AR2-Vertrag bewusst nur Crash-/Pause-Fenster VOR jeder Marker-
    Pruefung abdeckt, s. Moduldocstring). Der belegte M12-Fall: die SL zeigt
    den Export in EINEM Turn (z.B. auf eine freie Aktion), die ausdrueckliche
    Leaderentscheidung `!save` kommt ERST einen oder mehrere Turns SPAETER
    UND wird von der SL mit einer SaveGuard-Verweigerung beantwortet (KEIN
    neuer Export in DIESER Antwort). Ohne diese Funktion bliebe der bereits
    gueltige Export fuer immer unerreichbar -- die Section liefe mit
    normalen (bezahlten) Folgeturns weiter oder haengt in der Reject-
    Antwort fest (Kernbug H1, `run/ledger.md` STAGE 2).

    Gleiche Drei-Ergebnis-Vertrag wie `find_recoverable_entry` (s.
    Moduldocstring AR2): `(None, None)` kein Kandidat (normaler Weg,
    unveraendert); `(entry, None)` ein eindeutig positiv gebundener Export
    -- der Aufrufer darf GENAU `entry["content"]` wie eine frische SL-
    Antwort ernten (`core.runtime.SectionRuntime.finalize`); `(None,
    hold_reason)` ein erkannter, aber unzureichend gebundener/zu alter
    Export -- kontrollierter HOLD, NIEMALS automatische Ernte.

    Reine Suchfunktion (kein I/O, kein Call) -- ALLE domaenenspezifischen/
    identitaetsbezogenen Entscheidungen kommen vom Aufrufer als injizierte
    Praedikate (dieselbe Philosophie wie `find_recoverable_entry`s
    `entry_matches`/`request_binding_error`, kein Spiegel-Drift):

    - `harvest_own_export(entry) -> bool`: True, wenn `entry["content"]`
      einen bindbaren, vom AKTUELLEN Current abweichenden eigenen Save des
      Leaders traegt (identische Autoritaet wie `ui/tui.py`s Pending-Gate
      -- `harvest_extractor` + Ingest-Abgleich gegen den echten Current,
      s. `core.runtime`-Aufrufstelle).
    - `is_explicit_save_command(raw_input) -> bool`: dieselbe Autoritaet
      wie `SectionRuntime.explicit_completion_attempt`/`domain.zeitriss.
      policy.is_save_command` -- hier NUR zum Ausschliessen von Save-
      Kommando-Eintraegen selbst (die sind nie der Export) UND zur
      Stufe-2-Pruefung unten.

    Ablauf:

    1. Kandidat = der JUENGSTE Eintrag dieser Section mit `origin_
       persona_key == leader_pid`, dessen `origin_raw_input` KEIN Save-
       Kommando ist (ein Save-Kommando-Eintrag ist selbst nie der Export,
       sondern hoechstens der spaeter gepruefte Commitwunsch) UND dessen
       `content` `harvest_own_export` erfuellt. Absichtlich der JUENGSTE
       (nicht der aelteste wie `ui/tui.py`s Warn-Gate, das bewusst beim
       ERSTEN Fund stehenbleibt, um eine Warnung nicht vorzeitig zu
       entwaffnen) -- fuer die tatsaechliche UEBERNAHME gilt der
       aktuellste gueltige Kandidat (03 §4 "unveraenderte Fortgeltung").
    2. Keine versteckte Eskalation (03 §4): liegt NACH dem Kandidaten ein
       WEITERER Leader-Eintrag mit einem NICHT-Save-Kommando-Rohinput
       (= eine echte neue freie Aktion, zwischenzeitlicher Storyfortschritt,
       03 §5 Negativfall), ist der Kandidat nicht mehr aktuell -- `(None,
       None)`, unveraenderter normaler Weg (die aktuelle Eingabe geht wie
       bisher weiter, KEIN Shortcut, aber auch KEINE neue Eskalation).
       Weitere Save-Kommando-Versuche (z.B. ein frueherer abgelehnter
       `!save`) ZWISCHEN Kandidat und Ende sind UNSCHAEDLICH (genau der
       belegte M12-Fall: Kandidat turn7, Reject turn8).
    3. Fehlende Section-Bindung oder fehlender Generations-Schnappschuss
       (`expected_prev_ref_by_member`) -> `(None, hold_reason)`, dieselbe
       Vorsicht wie `find_recoverable_entry` AR2 Teil C/AR11.
    4. `request_binding_error(candidate)` (falls uebergeben) muss `None`
       liefern -- dieselbe Originalprovenienz-Pruefung wie die bestehende
       R12-AUTORECOVERY (`core.runtime.run_full_section:_request_binding_
       error`), hier auf den gefundenen Kandidaten statt `sl_log[-1]`
       angewandt."""
    candidate: dict | None = None
    candidate_idx = -1
    for idx, entry in enumerate(sl_log):
        if entry.get("origin_persona_key") != leader_pid:
            continue
        entry_section = entry.get("section_id")
        if entry_section not in (section_id, None):
            continue
        raw_input = entry.get("origin_raw_input")
        if raw_input is not None and is_explicit_save_command(raw_input):
            continue
        if not harvest_own_export(entry):
            continue
        candidate, candidate_idx = entry, idx
    if candidate is None:
        return None, None
    for later in sl_log[candidate_idx + 1:]:
        if later.get("origin_persona_key") != leader_pid:
            continue
        later_raw = later.get("origin_raw_input")
        if later_raw is not None and not is_explicit_save_command(later_raw):
            # Echte neue freie Aktion NACH dem Kandidaten -- zwischen-
            # zeitlicher Storyfortschritt, der Kandidat gilt nicht mehr als
            # unveraendert fortgeltend (03 §4/§5). Kein HOLD-Text hier
            # (das ist kein erkannter-aber-unzureichender Export, sondern
            # schlicht "kein aktueller Kandidat mehr") -- normaler Weg.
            return None, None
    if candidate.get("section_id") is None:
        return None, (
            "Gefundener Eigenexport traegt ueberhaupt keine Section-Bindung "
            "(Legacy-Eintrag) -- unzureichend gebunden, kontrollierter HOLD statt "
            "automatischer Uebernahme."
        )
    if candidate.get("expected_prev_ref_by_member") is None:
        return None, (
            "Gefundener Eigenexport ohne durabel gebundenen Generations-Schnappschuss "
            "('expected_prev_ref_by_member' fehlt) -- unzureichende Bindung, "
            "kontrollierter HOLD statt automatischer Uebernahme."
        )
    if request_binding_error is not None:
        reason = request_binding_error(candidate)
        if reason is not None:
            return None, reason
    return candidate, None
