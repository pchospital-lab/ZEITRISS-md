#!/usr/bin/env python3
"""
mmo_sim/ui/tui.py — Terminalansicht (M3, 01 §3 M3, 11 §2/§4/§8).

Einfaches, robustes Menue + Eingabeschleife: kein Browser fuers Spielen.
`input_fn`/`print_fn` sind injizierbar — dieselbe Klasse wird sowohl fuer den
echten interaktiven Betrieb (stdin/stdout) als auch fuer geskriptete
Parity-/Bedien-Tests (A16, 04 §5 "Human-/Lab-Paritaet") verwendet.

Deckt aus 11 §2 den geführten Einstieg (Fortsetzen-Karte / neue Figur /
Import / lokale Runde / Einstellungen) UND behandelt Ctrl-C/EOF als
kontrollierte Pause statt Absturz (A11/A16).

P2-Fertigstellung (I3, REVIEW-P2.md §I3):
- `l`/`c`/`s` sind jetzt ECHTE Wege statt "Unbekannte Auswahl" (Test 05).
- `i` liest einen angebotenen DATEIPFAD tatsaechlich von der Platte statt
  ihn als rohen JSON-Text zu parsen (Test 06).
- `e` exportiert zusaetzlich in eine eigenstaendige Datei (Review: "besitzt
  keinen verbundenen Dateiexport").
- `l` (lokale Runde) verwendet — sofern Laufumgebung + SL-Anbindung
  konfiguriert sind — GENAU `core.app_service.run_play_session`, denselben
  Call-Pfad wie `lab/runner.LabRunner.run_section` (I1/A4). Ohne
  konfigurierte Laufumgebung/SL-Anbindung (Offline-Default) gibt `l` eine
  EHRLICHE Statusmeldung aus (kein Stub, der Erfolg vortaeuscht) — das ist
  bewusst KEINE kuenstliche Scope-Reduktion, sondern der reale Zustand ohne
  Live-Setup (03 §7)."""
from __future__ import annotations

import datetime
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..core.creation_service import ReplyResult, run_admitted_creation_dialog
from ..domain.zeitriss import catalog, import_export, onboarding
from ..domain.zeitriss import saves as zeitriss_saves
from ..domain.zeitriss.policy import (
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
)
from . import rendering


@dataclass
class ResumeCard:
    community_id: str | None
    participant_id: str | None
    chrononaut_id: str | None
    last_valid_save_summary: str | None
    open_section_id: str | None = None
    # G03/P04 (General-Befund 'P04_OPEN_CREATION_NOT_OFFERED'): eine real
    # begonnene, noch nicht abgeschlossene Erschaffung ist ein EIGENER
    # fortsetzbarer Zustand -- getrennt von `open_section_id` (offener
    # SPIELabschnitt) und von einem bereits ABGESCHLOSSENEN Save.
    pending_creation: bool = False
    # G03/UX12: ein bekannter, aber GERADE nicht lesbarer autoritativer
    # Current -- Aufrufer MUESSEN dies als Stop-Grund behandeln, nicht als
    # "kein Stand" (das waere ein stiller Rueckfall auf den evtl. veralteten
    # Onboarding-Stand).
    authority_unresolved: bool = False


def render_boot_menu(resume: ResumeCard | None) -> str:
    """11 §2: 'Bei vorhandenen Daten zuerst eine verstaendliche Fortsetzen-
    Karte zeigen ... Darunter alternative Wege.'

    G01-Fix (ZEITRISS Terminal UX-1 Wiederanlauf, REVIEW.md §G01, UX01/UX03):
    zeigt NUR MEHR die EINE KISS-Zielhierarchie (Fortsetzen/Spielen/
    Charaktere/Einstellungen/Beenden) -- NICHT mehr gleichzeitig den
    vollstaendigen alten Einzelbuchstaben-Hotkeybaum ('Kompatibilitaets-
    Hotkeys'-Block). 02 §A ausdruecklich: 'Alte TUI-Hotkeys ... als
    dokumentierte Kompatibilitaetsaliase erhalten' -- ABER 'rechtfertigen
    keine dauerhaft doppelte Normalansicht'. Die alten Einzelbuchstaben
    (n/i/e/g/l/c/b/s/x, s. `run()`) bleiben strukturell UNVERAENDERT
    dispatchbar (reine Anzeigenaenderung hier, `run()` liest weiterhin
    dieselben Buchstaben) -- sie sind jetzt echte UNSICHTBARE
    Kompatibilitaetsaliase statt einer zweiten sichtbaren Normalansicht.
    `test_ux1_kiss_menu.py:test_old_single_letter_hotkeys_still_work_unchanged`
    belegt das weiterhin funktionierende, nur nicht mehr beworbene 'x'."""
    # R2 (C-M2, UX11, Korrekturzyklus 1): nicht mehr exklusiv an
    # `community_id` gaten -- der weitaus haeufigere Einstiegspfad ([n]
    # Figur erschaffen -> solo spielen) erzeugt NIE eine Community und
    # blieb dadurch von "Fortsetzen" dauerhaft ausgeschlossen, obwohl eine
    # echte Figur-Save vorhanden ist (`_cmd_local_round([])` prueft intern
    # ohnehin die richtige Autoritaet fuer beide Faelle).
    has_resume = resume is not None and bool(resume.community_id or resume.chrononaut_id)
    lines = ["ZEITRISS MMO-Sim", ""]
    lines.append("Hauptmenue:")
    if has_resume:
        lines.append("  [fortsetzen] Fortsetzen")
        stand = resume.last_valid_save_summary or "kein gueltiger Stand"
        offen = f" (Abschnitt {resume.open_section_id} unterbrochen)" if resume.open_section_id else ""
        chrono_display = resume.chrononaut_id if resume.chrononaut_id else "kein eigener Chrononaut"
        # R2-Folgefix: `community_id` kann jetzt (Solo-Figur ohne Community)
        # real `None` sein -- kein literales "None" in der Anzeige (UX22).
        community_display = resume.community_id if resume.community_id else "keine Community"
        lines.append(f"  Fortsetzen: {community_display} · {resume.participant_id} · {chrono_display} — {stand}{offen}")
    lines.append("  [spielen] Spielen (Runde zusammenstellen / Meine KI-Spielgemeinschaft)")
    lines.append("  [charaktere] Charaktere (waehlen/erschaffen, importieren, exportieren)")
    lines.append("  [registrieren] Neue lokale Person registrieren (eigene Figur unter ihrer ID)")
    lines.append("  [einstellungen] Einstellungen")
    lines.append("  [beenden] Beenden")
    lines.append("  (? oder /hilfe an jeder Eingabe zeigt Kontexthilfe, kein Zugverbrauch)")
    return "\n".join(lines)


class EndOfInput(Exception):
    """Signalisiert EOF/Pipeline-Ende — vom Aufrufer als kontrollierte Pause
    zu behandeln (A11/A16: kein Absturz bei Skript-/Pipe-Eingabe)."""


class _ActiveSaveUnresolved(Exception):
    """I4-Nachzug (Vertrag §3 A/B, R1b): interne Signalisierung innerhalb
    `_cmd_local_round`, dass `_resolve_active_save` fuer einen Teilnehmer
    (Leader ODER Gast) einen bekannten, gerade nicht lesbaren Current-Save
    meldet -- der Aufrufer MUSS den Spielstart kontrolliert ablehnen statt
    stillschweigend den alten Onboarding-Stand an die SL zu senden."""


def _human_fresh_attempt_key(participant_id: str) -> str:
    """r2-Nacharbeit (02_NACHARBEITSAUFTRAG.md §1): Schluessel fuer
    `onboarding.bind_attempt`, EINER pro Mensch -- bindet die Generation
    seiner bewusst neuen Zusatzerschaffungen, GETRENNT von der eigentlichen
    `onboarding__<participant_id>.json`-Datei der ERSTEN/normalen
    Erschaffung (die bleibt unveraendert, s. `_cmd_new_or_switch_
    character`)."""
    return f"human-fresh-create::{participant_id}"


def _human_fresh_onboarding_key(participant_id: str, generation: int) -> str:
    """r2-Nacharbeit: eigene, von der menschlichen Hauptkennung GETRENNTE
    Onboarding-/Requestledger-Buchhaltungskennung fuer EINEN bewusst neuen
    Zusatzerschaffungsversuch -- analog zu `domain.zeitriss.community_
    creation._additional_onboarding_key` auf der Persona-Seite. NUR fuer
    Onboarding-Scratch/Requestledger-Buchung -- Katalog/Current/Persona-
    State bleiben IMMER an der realen `participant_id`-Identitaet
    gebunden."""
    return f"{participant_id}__fresh_gen{generation}"


def _fresh_start_invite_attempt_key(participant_id: str, persona_key: str) -> str:
    """r2-Nacharbeit (02_NACHARBEITSAUFTRAG.md §2): Schluessel fuer
    `onboarding.bind_attempt`, EINER pro (einladender Mensch, eingeladene
    Persona)-Paarung -- bindet die Generation EINER Frischstart-
    Einladungsgelegenheit GETRENNT vom best-effort `invitation_decisions.
    jsonl`-Auditlog (`lobby_service.append_offer_log_record`, `OSError`
    dort bewusst verschluckt) und von `catalog.list_for_participant`s
    Kataloganzahl."""
    return f"fresh-start-invite::{participant_id}::{persona_key}"


class NonInteractiveImportError(ValueError):
    """F-PROCESS-GAP (ZR-N2-LIVEBUNDLE-FRESH-20261018-R1, DELIVERABLE 5):
    `import_save_for_participant_noninteractive` deckt bewusst NUR den
    EINEN Fall ab, den ein frischer Hybrid-2+3-Lauf tatsaechlich braucht
    (allererster Import, keine bekannte Char-ID, keine aktive Bindung,
    kein Konflikt) -- jeder andere Fall (Konflikt/Sperre/Mehrdeutigkeit)
    bricht HIER laut ab, statt ihn zu raten/automatisch aufzuloesen."""


def import_save_for_participant_noninteractive(
    *, catalog_dir: Path, onboarding_dir: Path, run_dir: Path | None, participant_id: str,
    raw_save_text: str, harvest_validator: ZeitrissHarvestValidator,
    states_dir: Path | None = None, persona_state_store=None,
):
    """Nicht-interaktives Gegenstueck zu `TuiSession._cmd_import` fuer GENAU
    den allerersten, konfliktfreien Import EINER Figur fuer einen NOCH
    FRISCHEN Teilnehmer (DELIVERABLE 5, 'normaler Produktimport' fuer
    p01_latch/p02_breach im Hybrid-2+3-Treiber): ruft DIESELBEN
    Produktfunktionen in DERSELBEN Reihenfolge wie die interaktive
    `_cmd_import` (`import_export.preview_import` ->
    `import_export.resolve_import` -> `catalog.store_figure_save` ->
    `onboarding.complete_with_save`) -- KEINE zweite Importregelimplementierung,
    NUR die TTY-Rueckfragen (Konfliktwahl/Bestaetigung) entfallen, weil
    dieser Aufrufer per Definition keinen der Faelle konstruiert, die eine
    Rueckfrage ausloesen wuerden (frischer `onboarding_dir`/`catalog_dir`,
    keine bekannte Char-ID, keine aktive Tischbindung).

    Wirft `NonInteractiveImportError`, wenn die Eingabe tatsaechlich einen
    der interaktiven Faelle (Konflikt/Sperre/Mehrdeutigkeit/Parken)
    trifft -- kein stilles Raten einer Wahl, die ein Mensch sonst am
    Prompt treffen wuerde.

    `states_dir`/`persona_state_store` (additiv, optional -- `None` =
    unveraendertes Verhalten, nur Katalog/Onboarding, kein `PersonaCreation
    Outcome`): wenn BEIDE gesetzt sind, wird NACH dem Import dieselbe
    Publikations-Abgleichfunktion aufgerufen, die `advance_community_
    creation` fuer jede ERSCHAFFENE Figur nutzt (`domain.zeitriss.
    community_creation._publication_reconcile` -- Current-Save-
    Veroeffentlichung, Persona-State, aktive Bindung), damit eine
    IMPORTIERTE Figur fuer den nachfolgenden Lobby-/Tischweg GENAU GLEICH
    'bereit' ist wie eine neu erschaffene -- kein zweiter, abweichender
    Bereitschaftsbegriff. Liefert dann ein `PersonaCreationOutcome`
    (`status='completed'`), sonst (ohne beide Parameter) den rohen,
    tatsaechlich uebernommenen Save-Block."""
    try:
        preview = import_export.preview_import(raw_save_text)
    except import_export.MalformedImportError as e:
        raise NonInteractiveImportError(f"Import strukturell ungueltig, kein Write: {e}") from e
    incoming_block = json.loads(raw_save_text)
    known_char_ids = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, participant_id)}
    if preview.char_id in known_char_ids:
        raise NonInteractiveImportError(
            f"char_id={preview.char_id!r} ist fuer {participant_id!r} bereits bekannt -- "
            "dieser Helfer deckt nur den allerersten, konfliktfreien Import ab."
        )
    active_binding = False
    open_completion_order = False
    if run_dir is not None and preview.char_id is not None:
        from ..core import store as core_store
        active_binding = core_store.chrononaut_active_binding(run_dir, preview.char_id)
        open_completion_order = core_store.chrononaut_open_completion_order(run_dir, preview.char_id)
    decision = import_export.resolve_import(
        incoming_block, known_char_ids=known_char_ids, existing_block_for_char_id=None,
        active_binding=active_binding, open_completion_order=open_completion_order,
    )
    if decision.action != "register_new":
        raise NonInteractiveImportError(
            f"erwartete Entscheidung 'register_new' fuer einen frischen Import, bekommen: "
            f"{decision.action!r} ({decision.reason})."
        )
    catalog.store_figure_save(catalog_dir, participant_id, preview.char_id, decision.block)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(
        onboarding_dir, participant_id, decision.block, harvest_validator, preview.char_id,
    )
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=preview.char_id, persona_key=participant_id,
    ))
    if states_dir is not None and persona_state_store is not None and run_dir is not None:
        from ..domain.zeitriss.community_creation import _publication_reconcile
        return _publication_reconcile(
            run_dir=run_dir, states_dir=states_dir, onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            persona_key=participant_id, final_save=decision.block, ps_store=persona_state_store,
        )
    return decision.block


class TuiSession:
    def __init__(
        self,
        onboarding_dir: str | Path, catalog_dir: str | Path, participant_id: str,
        input_fn: Callable[[str], str] | None = None,
        print_fn: Callable[[str], None] | None = None,
        *,
        run_dir: str | Path | None = None,
        states_dir: str | Path | None = None,
        schema_path: str | Path | None = None,
        gm_transport_factory: Callable[[], object] | None = None,
        exports_dir: str | Path | None = None,
        persona_driver_factory: Callable[[str], object] | None = None,
        ascii_fallback: bool = False,
    ):
        self.onboarding_dir = Path(onboarding_dir)
        self.catalog_dir = Path(catalog_dir)
        self.participant_id = participant_id
        self._input = input_fn or input
        # R12-SAVECOMPAT (03_TERMINAL_UND_BILD.md): derselbe `print_fn`-
        # Rohaufruf wie bisher ("l print_fn or print"), aber JEDER Aufruf
        # geht zusaetzlich durch `rendering.render_for_terminal` -- EIN
        # Minimalrenderer fuer die bestehende Produktanzeige (Markdown-
        # Subset -> ANSI, gefaehrliche rohe Steuerzeichen aus Modelltext
        # entfernt), OHNE das an `onboarding`/`sl_log`/Save-Dateien
        # geschriebene Protokoll zu veraendern (die bekommen den
        # unveraenderten Rohtext weiterhin VOR diesem Aufruf, s. z.B.
        # `core.creation_service.run_admitted_creation_dialog`s
        # `onboarding_lib.record_pending_reply(..., sl_reply=sl_text, ...)`
        # VOR `print_fn(f"[SL] {sl_text}")`). `ascii_fallback` ist ein
        # expliziter, vom Aufrufer gesetzter Opt-in (Konstruktorparameter
        # ODER `MMO_SIM_TUI_ASCII_FALLBACK=1`, kein stiller Default-Verlust).
        ascii_fallback_env = os.environ.get("MMO_SIM_TUI_ASCII_FALLBACK") == "1"
        self._ascii_fallback = bool(ascii_fallback) or ascii_fallback_env
        raw_print = print_fn or print

        def _rendered_print(text: str) -> None:
            raw_print(rendering.render_for_terminal(text, ascii_fallback=self._ascii_fallback))

        self._print = _rendered_print
        self.exit_code = 0
        self._quit = False
        # Optionale Laufumgebung/SL-Anbindung fuer `l` (lokale Runde, I1/A4)
        # -- ohne diese vier Werte bleibt `l` eine ehrliche Statusmeldung
        # statt eines Spielversuchs ohne Produktionsgrundlage.
        self.run_dir = Path(run_dir) if run_dir is not None else None
        self.states_dir = Path(states_dir) if states_dir is not None else None
        self.schema_path = Path(schema_path) if schema_path is not None else None
        self.gm_transport_factory = gm_transport_factory
        self.exports_dir = Path(exports_dir) if exports_dir is not None else self.onboarding_dir.parent / "exports"
        # F2/K5 (WEGKARTE BLOCKER 2): optionaler Treiber-Baukasten fuer
        # eingeladene KI-Personas in der lokalen Runde ('l persona:<id>') --
        # ohne Konfiguration bleibt eine Persona-Einladung eine ehrliche
        # Fehlermeldung statt eines stillen Fallbacks (03 §4).
        self.persona_driver_factory = persona_driver_factory
        # SPIELFLUSS-SPEC.md ("Aktive Gruppe / Ausschluss"): rein In-Memory
        # fuer DIESE Sitzung -- KEINE neue Community-Struktur, nur eine
        # Markierung, welche bereits bestaetigten Community-Personas fuer
        # "Personas spielen lassen" (Catch-up/Vorspielen) NIE Kandidat sind.
        # Ausgeschlossene Personas nerven/blocken nie, sie sind einfach
        # nicht Teil des Catch-up-/Vorspiel-Pools dieser Sitzung.
        self._excluded_personas: set[str] = set()

    def _readline(self, prompt: str) -> str:
        try:
            return self._input(prompt)
        except EOFError as e:
            raise EndOfInput() from e

    # UX04/05 (02 §C, "Einmaliger zentraler, kontextbewusster Bedienvertrag
    # statt ad-hoc-Abfangen in zehn Dialogen"): EIN gemeinsamer Satz
    # reservierter Steuerzeilen, erreichbar an den wesentlichen Prompts
    # (Boot-Auswahl, Erschaffungsantwort, Spielzug) -- Hilfe/Stand/Verlauf
    # geben NUR Information zurueck und fragen DIESELBE Zeile erneut ab
    # (kein Zugverbrauch, kein GM-/Persona-Call, bisherige Auswahl/Text
    # bleibt unberuehrt, weil der Aufrufer bei 'help'/'status'/'history'
    # schlicht nie verlassen wird). `/zurueck`/`/abbrechen`/`/pause` werden
    # NICHT hier interpretiert -- das bleibt Sache des jeweiligen Aufrufers
    # (unterschiedliche Bedeutung je Kontext, 02 §C: Abbruch waehrend eines
    # offenen Abschnitts heisst Pause, nicht Rollback). Ein literaler Text,
    # der wie eine Steuerzeile aussieht, bleibt ueber ein fuehrendes '\'
    # eingebbar (Escape, s. 02 §C 'erklaerte Escape-/Texteingabe').
    _CONTROL_TOKENS = ("/zurueck", "/abbrechen", "/pause", "/stand", "/verlauf")

    def _control_help_text(self, context: str) -> str:
        # W24b (BRIEF-W24b.md Punkt 3): die vorherige PAUSCHALE Zusage
        # "/abbrechen (Vorgang verwerfen)" war ueberall dieselbe, obwohl die
        # tatsaechliche Wirkung je Kontext unterschiedlich ist (s. die
        # einzelnen `control in ("zurueck", "abbrechen", "pause")`-Zweige
        # dieser Datei): NUR waehrend eines laufenden Spielabschnitts
        # (Kontext "Spielzug") wirkt `/abbrechen` wie `/pause` (02 §C, kein
        # Rollback). An jedem Erschaffungs-/Auswahl-/Importkontext dagegen
        # verwirft es NUR die gerade offene, unbestaetigte Eingabe/Auswahl
        # dieses Schritts -- bereits gespeicherte/veroeffentlichte Figuren-
        # und Erschaffungsdaten bleiben unveraendert und fortsetzbar,
        # NIEMALS werden dabei schon publizierte Bytes geloescht.
        if context == "Spielzug":
            abbrechen_line = (
                "/abbrechen (waehrend dieses laufenden Abschnitts wie /pause: "
                "kontrolliert pausieren, kein Rollback)"
            )
        else:
            abbrechen_line = (
                "/abbrechen (verwirft nur die gerade offene, unbestaetigte Eingabe/"
                "Auswahl dieses Schritts -- bereits gespeicherte/veroeffentlichte "
                "Daten bleiben unveraendert und fortsetzbar, nie geloescht)"
            )
        return (
            f"Hilfe ({context}): /zurueck (eine Ebene zurueck) · {abbrechen_line} · /stand "
            "(aktueller Stand) · /verlauf (bisherige SL-Antworten dieses Schritts) · "
            "/pause (kontrolliert pausieren -- der zuletzt gueltige, bereits gespeicherte "
            "Stand bleibt erhalten, kein Datenverlust). '?' oder '/hilfe' "
            "zeigt diesen Text erneut, verbraucht keinen Zug/Request. Text, der wie "
            "eine Steuerzeile aussieht, aber als normaler Text gemeint ist: mit "
            "fuehrendem '\\' eingeben (z.B. '\\/pause' wird als Text '/pause' gesendet)."
        )

    def _readline_with_controls(
        self, prompt: str, *, context: str, history: list[str] | None = None,
        speaker_pid: str | None = None,
    ) -> tuple[str, str | None]:
        """Liest eine Zeile und erkennt die reservierten Steuerzeilen oben.
        Liefert `(text, control)` — `control` ist `None` fuer normalen
        Nutztext (inkl. entschaerftem Escape-Text), sonst einer der Werte in
        `_CONTROL_TOKENS` (ohne fuehrenden Slash: 'zurueck'/'abbrechen'/
        'pause'/'stand'/'verlauf' werden bereits HIER fuer Stand/Verlauf
        beantwortet und erneut abgefragt — nur 'zurueck'/'abbrechen'/'pause'
        werden an den Aufrufer zurueckgereicht, weil deren Wirkung vom
        jeweiligen Kontext abhaengt).

        WICHTIG (02 §C): ein bare `?` zaehlt NUR, wenn es die GESAMTE
        (getrimmte) Eingabe ist — ein Fragezeichen irgendwo im Satz bleibt
        unveraendert Nutztext, da hier auf Gleichheit, nicht auf Teilstring
        geprueft wird.

        G04/UX20 (General-Befund G04, W3-Hunk selektiv uebernommen, s.
        W3-REUSE.md): `speaker_pid` (optional, Default `None` ->
        `self.participant_id`, unveraendertes Verhalten fuer JEDEN
        bestehenden Aufrufer ohne dieses Argument) laesst `/stand` den Stand
        der GERADE EINGEBENDEN Person zeigen, nicht pauschal den aeusseren
        Sessionteilnehmer -- `_HumanDriver.decide()` (geteiltes Terminal,
        mehrere Menschen) uebergibt hier ihre eigene `_pid`.

        G04/UX20 `/verlauf`: zeigt nicht mehr nur still `history[-10:]` --
        eine wiederholte `/verlauf`-Eingabe INNERHALB desselben Prompts
        blaettert sichtbar weiter zurueck (10er-Seiten), bis der Anfang der
        vollstaendig erhaltenen (nie gekuerzten) Historie erreicht ist. Nur
        die ANZEIGE blaettert -- `history` selbst und der an das Modell
        gehende Kontext bleiben unveraendert/vollstaendig."""
        verlauf_shown = 0
        while True:
            raw = self._readline(prompt)
            stripped = raw.strip()
            key = stripped.lower()
            if key.startswith("\\/") or key.startswith("\\?"):
                return raw[1:], None
            if key in ("?", "/hilfe", "/?"):
                self._print(self._control_help_text(context))
                continue
            if key == "/stand":
                card = self._build_resume_card(participant_id=speaker_pid)
                if card is None:
                    self._print("Kein aktueller Stand vorhanden.")
                else:
                    detail = render_boot_menu(card)
                    stand_lines = [ln for ln in detail.splitlines() if ln.strip().startswith("Fortsetzen:")]
                    self._print(stand_lines[0].strip() if stand_lines else "Stand vorhanden, keine Fortsetzen-Zeile.")
                continue
            if key == "/verlauf":
                if not history:
                    self._print("Kein bisheriger Verlauf in diesem Schritt.")
                else:
                    total = len(history)
                    page_size = 10
                    end = max(0, total - verlauf_shown)
                    start = max(0, end - page_size)
                    page = history[start:end]
                    for line in page:
                        self._print(line)
                    verlauf_shown += len(page)
                    if start > 0:
                        self._print(f"... {start} weitere, aeltere Eintraege -- '/verlauf' erneut fuer mehr.")
                    else:
                        self._print(f"(Anfang des Verlaufs erreicht, {total} Eintraege gesamt.)")
                continue
            if key == "/zurueck":
                return raw, "zurueck"
            if key == "/abbrechen":
                return raw, "abbrechen"
            if key == "/pause":
                return raw, "pause"
            return raw, None

    class _ParticipantFocusGuard:
        """UX07 (02 §D.2, 'Die anschliessende Erschaffung oder der Import
        laufen nach bewusster Fokusuebernahme unter GENAU ihrer ID'):
        schaltet `session.participant_id` NUR fuer die Laufzeit des
        `with`-Blocks auf eine andere, bereits registrierte ID um und
        restauriert sie IMMER (auch bei Exception/EOF) danach. Aendert
        NICHTS an `_cmd_new_or_switch_character`/`_cmd_import`/deren
        Hilfsmethoden selbst -- die lesen/schreiben bereits korrekt ueber
        `self.participant_id`, der strukturelle Mangel war nur das Fehlen
        eines UI-Wegs, diesen Zeiger temporaer und bewusst zu wechseln
        (OFFENE_BEDIENBEFUNDE.md Punkt 6 referenziert dieselbe Luecke fuer
        den Rollentausch-Fall; dies ist der enger gefasste, tatsaechlich
        beauftragte Fall: eine NEU registrierte Person bekommt ihre EIGENE
        erste Figur, kein Rollentausch einer bestehenden Figur)."""

        def __init__(self, session: "TuiSession", target_pid: str):
            self._session = session
            self._target = target_pid
            self._original: str | None = None

        def __enter__(self) -> "TuiSession":
            self._original = self._session.participant_id
            self._session.participant_id = self._target
            return self._session

        def __exit__(self, exc_type, exc, tb) -> bool:
            self._session.participant_id = self._original
            return False

    def _cmd_register_new_person(self) -> None:
        """UX07: registriert eine NEUE lokale Person ueber die VORHANDENE
        `ParticipantRegistry` (keine zweite Personendatenwelt, derselbe
        Speicherort wie `_local_round_select_humans`), bestaetigt die
        Fokusuebernahme (wiederverwendet `_local_round_handoff`, derselbe
        bewusste Uebernahme-Vertrag wie bei einer Terminaluebergabe) und
        laesst die Person DANACH unter GENAU ihrer eigenen ID eine Figur
        erschaffen oder importieren -- ohne `--participant`/CLI-Neustart.
        Abbruch/EOF an jedem Schritt: klarer Rueckweg, KEINE Aenderung
        (Registrierung bleibt bestehen, falls bereits geschrieben; keine
        Figur wird ohne bestaetigte Fokusuebernahme angelegt).

        G05/P07 (General-Befund 'P07_REGISTRATION_IGNORES_FOREIGN_WRITER'):
        derselbe Lab-Owner-Guard wie `_cmd_new_or_switch_character`/
        `_cmd_import` jetzt VOR dem ersten Registry-Write dieses Wegs --
        vorher pruefte nur der frueh im Skript laufende Guard
        (`scripts/mmo_sim.py:_foreign_active_lab_owner`), ein WAEHREND einer
        bereits offenen TUI aktiv werdender fremder Lab-Lauf blieb fuer
        'registrieren' unbewacht. Kein fremdes Lock wird geloescht oder
        uebernommen, keine neue Ownerregel -- derselbe rein lesende
        `active_lock_pid`-Guard wie ueberall sonst.

        G02/P01 (General-Befund 'P01_CONTROL_AS_PERSON_NAME', W3-Hunk
        selektiv uebernommen, s. W3-REUSE.md): der Namensprompt nutzt jetzt
        denselben kontextbewussten Leser (`_readline_with_controls`) statt
        eines rohen `_readline` -- '/abbrechen'/'/zurueck'/'/pause' werden
        dadurch als Abbruch verarbeitet statt woertlich als Anzeigename
        gespeichert zu werden ('?'/'/hilfe'/'/stand'/'/verlauf' bleiben wie
        ueberall reine Information, kein Zugverbrauch, derselbe Prompt wird
        danach erneut gestellt). Ein literaler Text, der wie eine Steuerzeile
        aussieht, bleibt ueber das erklaerte fuehrende '\\' eingebbar."""
        if self._lab_active_guard("Registrierung"):
            return
        from ..registry.participants import ParticipantRegistry

        try:
            display, control = self._readline_with_controls(
                "Name der neuen lokalen Person (leer = abbrechen): ",
                context="Neue Person registrieren",
            )
        except EndOfInput:
            self._print("\nRegistrierung abgebrochen (EOF) -- keine Aenderung.")
            return
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Registrierung abgebrochen -- keine Aenderung.")
            return
        display = display.strip()
        if not display:
            self._print("Registrierung abgebrochen -- kein Name eingegeben, keine Aenderung.")
            return
        registry = ParticipantRegistry(self._local_round_registry_dir())
        # R6 (T-Befund 3, UX02/UX07, Korrekturzyklus 1): bei Namensgleichheit
        # die bestehende Person erkennen (reine Lesefunktion, s. `registry/
        # participants.py:find_by_display_name`) und "als bestehende <Name>
        # fortsetzen" anbieten -- vorher erzeugte ein erneutes 'registrieren'
        # mit demselben Anzeigenamen (z.B. nach Ctrl-C + Neustart)
        # stillschweigend eine ZWEITE, komplett neue ID unter demselben
        # Namen (02 §D.1: "Altbestand nicht neu anlegen"). Mehrere
        # bereits bestehende Treffer (seltener Altfall, z.B. aus der Zeit
        # VOR diesem Fix) werden ehrlich benannt, aber nicht automatisch
        # aufgeloest -- das bleibt eine bewusste Neu-Registrierung, um
        # keine falsche Person zu waehlen.
        existing_matches = registry.find_by_display_name(display)
        target_participant = None
        if len(existing_matches) == 1:
            self._print(
                f"Bereits bekannt: '{display}' ist schon registriert (von einer frueheren Sitzung). "
                "Als diese bestehende Person fortsetzen, statt eine zweite Registrierung unter "
                "demselben Namen anzulegen?"
            )
            # Q01 (REVIEW.md R01, 05.10.2026, `:386-389`): dieser Prompt las
            # vorher roh (`self._readline`) -- '/abbrechen'/'/zurueck'/
            # '/pause' wurden woertlich als (ungueltige) j/n-Antwort
            # behandelt, `answer == "j"` blieb False, und der Code fiel
            # DANACH in den "else"-Zweig unten durch, der stattdessen eine
            # ZWEITE, komplett neue Registrierung unter demselben Namen
            # anlegte -- exakt der vom Review belegte Doppel-Datensatz nach
            # Abbruch. Derselbe zentrale Leser (`_readline_with_controls`)
            # wie an den anderen Prompts dieser Funktion: eine Steuerzeile
            # wird HIER lokal verarbeitet (kein Speichern/Weiterleiten als
            # j/n-Antwort) und bricht die GESAMTE Registrierung ab, bevor
            # irgendein Write passiert -- verwirft nur den aktuellen
            # Entwurf (den gerade eingegebenen Namen), kein Rueckbau der
            # bereits bestehenden Person. '?'/'/hilfe'/'/stand'/'/verlauf'
            # bleiben wie ueberall reine Information (derselbe Prompt wird
            # danach erneut gestellt).
            try:
                answer_raw, control = self._readline_with_controls(
                    "Als bestehende Person fortsetzen? [j/n]: ",
                    context="Bestehende Person bestaetigen",
                )
            except EndOfInput:
                self._print("\nRegistrierung abgebrochen (EOF) -- keine Aenderung.")
                return
            if control in ("zurueck", "abbrechen", "pause"):
                self._print(
                    "Registrierung abgebrochen -- keine Aenderung (weder zweite Registrierung "
                    f"noch Fortsetzung als '{display}')."
                )
                return
            answer = answer_raw.strip().lower()
            if answer == "j":
                target_participant = existing_matches[0]
        elif len(existing_matches) > 1:
            self._print(
                f"'{display}' ist bereits MEHRFACH registriert ({len(existing_matches)} bestehende "
                "Eintraege unter diesem Namen) -- keine automatische Auswahl, um keine falsche Person "
                "zu uebernehmen. Es wird eine weitere, eigene Registrierung angelegt."
            )
        if target_participant is not None:
            self._print(f"Fortsetzung als bestehende Person '{display}' bestaetigt.")
            new_participant = target_participant
        else:
            # Q06 (REVIEW.md R04, 05.10.2026): derselbe `_lab_active_guard`
            # stand bisher NUR vor dem Namensdialog (oben, Funktionsanfang)
            # -- ein WAEHREND dieser Eingabe (Name + evtl. j/n-Bestaetigung)
            # erst aktiv werdender FREMDER Lab-Lock blieb fuer den
            # tatsaechlichen Registry-Write danach unbewacht (General-Probe
            # Q06: 'OWNER_ACTIVATED_DURING_NAME_PROMPT' -> trotzdem
            # 'Neu registriert'). Erneuter Aufruf UNMITTELBAR vor diesem
            # gemeinsamen Write -- derselbe rein lesende Guard, kein
            # Loeschen/Uebernehmen eines fremden Locks, keine neue
            # Ownerregel. Der fruehe Guard am Funktionsanfang bleibt
            # unveraendert bestehen (deckt den Fall ab, dass der Lock schon
            # VOR dem ersten Prompt aktiv ist, spart in diesem Fall die
            # Namenseingabe selbst).
            if self._lab_active_guard("Registrierung"):
                return
            new_participant = registry.register_participant(kind="human", display_name=display)
            self._print(
                f"Neu registriert: {new_participant.participant_id} ({display}). "
                "Figur-/Katalogdaten bleiben eine gemeinsame Ablage -- nur die ID aendert sich."
            )
        if not self._local_round_handoff(new_participant.participant_id):
            self._print(
                f"Fokus bleibt bei '{self.participant_id}' -- '{new_participant.participant_id}' "
                "ist registriert, aber noch nicht aktiv uebernommen. Spaeter ueber "
                "'registrieren' erneut moeglich (Registrierung bleibt erhalten)."
            )
            return
        with self._ParticipantFocusGuard(self, new_participant.participant_id):
            self._print(f"Fokus uebernommen: du bist jetzt als '{self.participant_id}' aktiv.")
            # R9 (C-K2, UX02, Korrekturzyklus 1): die Erstfuehrung ist jetzt
            # pro `participant_id` gefuehrt (s. `onboarding_prefs.py`) --
            # sie wird hier direkt nach der Fokusuebernahme gezeigt, wenn
            # GENAU diese (neue) Person sie noch nie gesehen hat. Reine
            # Anzeige (0 GM-/Persona-Calls), kein zusaetzlicher
            # `_readline`-Aufruf, daher keine verschobene Eingabezeile fuer
            # bestehende Tests.
            self._maybe_show_first_run_intro()
            # R10 (W10, C2-bestaetigter MUSS-Blocker UX04/UX05): derselbe
            # kontextbewusste Leser (`_readline_with_controls`) wie an den
            # anderen Stellen dieser Funktion -- vorher nahm der rohe
            # `_readline` hier '/stand'/'?'/'/hilfe'/'/verlauf'/'/zurueck'/
            # '/abbrechen'/'/pause' woertlich als (ungueltige) Figur-Wahl
            # statt sie als Steuerzeilen zu beantworten bzw. kontrolliert
            # abzubrechen. `has_existing_figure` (reine Lesefunktion, kein
            # neuer Schreibzugriff) unterscheidet den Re-Fokus-Fall (Person
            # hat schon eine Figur, z.B. Ben/CHR-BEN) von einer wirklich
            # neuen Person ohne Figur, damit die Abschluss-/Abbruchmeldung
            # den tatsaechlichen Figurstatus nennt statt faelschlich immer
            # "ohne eigene Figur" zu behaupten.
            has_existing_figure = bool(
                catalog.list_for_participant(self.catalog_dir, self.participant_id)
            )
            try:
                raw, control = self._readline_with_controls(
                    "Fuer diese Person [n] Figur erschaffen oder [i] importieren: ",
                    context="Figur erschaffen oder importieren",
                )
            except EndOfInput:
                self._print("\nKeine Erschaffung/Import gewaehlt (EOF).")
                raw, control = "", None
            choice = raw.strip().lower()
            if control in ("zurueck", "abbrechen", "pause"):
                if has_existing_figure:
                    self._print(
                        "Abgebrochen -- die vorhandene Figur dieser Person bleibt erhalten, "
                        "kein Erschaffungs-/Importvorgang gestartet."
                    )
                else:
                    self._print("Abgebrochen -- Person bleibt ohne eigene Figur registriert.")
            elif choice == "n":
                self._cmd_new_or_switch_character()
            elif choice == "i":
                self._cmd_import()
            elif has_existing_figure:
                self._print(
                    "Kein neuer Erschaffungs-/Importweg gewaehlt -- die vorhandene Figur dieser "
                    "Person bleibt erhalten, Fokus geht zurueck."
                )
            else:
                self._print("Kein Erschaffungs-/Importweg gewaehlt -- Person bleibt ohne eigene Figur registriert.")
        self._print(f"Fokus zurueck bei '{self.participant_id}' (deine urspruengliche Identitaet).")

    def _cmd_menu_spielen(self) -> None:
        """KISS-Submenue 'Spielen' (02 §A) — dispatcht additiv auf die
        UNVERAENDERTEN Kommandos `g`/`l`(Runde zusammenstellen) bzw. `c`/`b`
        (Meine KI-Spielgemeinschaft). Kein neuer Spielweg, nur Benennung +
        Steuerzeilen-Zugriff.

        [3]/[4] (SPIELFLUSS-SPEC.md Abschnitt 3, 2026-10-21): "Personas
        spielen lassen" (Catch-up, spielergesteuert, NIE automatisch) und
        die "aktive Gruppe"-Ausschluss-Bedienung. [5] (M1-Fix, BL1-FIX-
        SPEC.md 2026-10-21): "Vorspielen" ist derselbe Orchestrator
        (`core.catchup.run_catch_up`, `max_rounds=1`), aber ein EIGENER,
        klar benannter Ausloese-Moment -- vorher war `max_rounds` im
        gesamten Produktpfad nie erreichbar (M1: bei bereits erreichter
        Paritaet tat [3] nichts, obwohl genau das der Vorspielen-Fall der
        Spec ist, "du musst mal weg"). Dein eigenes Tischspiel ([1]/[2])
        bleibt dadurch UNVERAENDERT nie geblockt -- alles rein additive,
        vom Spieler ausgeloeste Aktionen."""
        self._print(
            "Spielen -- [1] Runde zusammenstellen  [2] Meine KI-Spielgemeinschaft  "
            "[3] Personas spielen lassen (Catch-up)  [4] Aktive Gruppe/Ausschluss  "
            "[5] Personas vorspielen lassen (1 Abschnitt vor -- du spielst danach deinen) "
            "(/zurueck fuer Hauptmenue)"
        )
        text, control = self._readline_with_controls(
            "Auswahl: ", context="Spielen-Untermenue",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            return
        choice = text.strip()
        if choice == "1":
            self._cmd_local_round_setup()
        elif choice == "2":
            self._cmd_community()
            self._print("Weitere Option in 'Meine KI-Spielgemeinschaft': [b] Personas zusammenbringen.")
        elif choice == "3":
            self._cmd_catch_up_personas()
        elif choice == "4":
            self._cmd_active_group_settings()
        elif choice == "5":
            self._cmd_catch_up_personas(vorspielen=True)
        else:
            self._print(f"Unbekannte Auswahl: {choice!r} -- zurueck zum Hauptmenue.")

    def _cmd_catch_up_personas(self, vorspielen: bool = False) -> None:
        """SPIELFLUSS-SPEC.md Abschnitt 3 ("Personas spielen lassen"): EINE
        vom Spieler ausgeloeste Aktion, Catch-up UND Vorspielen sind
        mechanisch DIESELBE Maschine (`core.catchup.run_catch_up`), nur ein
        anderer Ausloese-Moment -- `vorspielen=False` (Menuepunkt [3],
        Default) zielt auf DEINE aktuelle Abschnittszahl (`target=None`,
        nur Kandidaten, die HINTER dir liegen). Kandidaten = bereite
        Community-Personas MINUS du selbst MINUS ausgeschlossen
        (`self._excluded_personas`) MINUS Mitglieder deines Tisches
        (Catch-up: `core.store.current_or_recent_table_members` --
        aktuell/zuletzt gespielt; Vorspielen: `core.store.
        current_active_table_members` -- NUR ein wirklich aktiv laufender
        Tisch, s. P1-Fix unten) MINUS bereits auf deiner Abschnittszahl.
        Reuse: `core.catchup.run_catch_up` ist die einzige Spielmechanik
        hier -- keine zweite Tisch-/GM-Logik.

        M1-Fix (BL1-FIX-SPEC.md 2026-10-21): `vorspielen=True` (Menuepunkt
        [5]) ist der vorher im gesamten Produktpfad unerreichbare
        `max_rounds`-Pfad -- jede wahlbare Persona spielt JETZT GENAU EINEN
        Abschnitt UEBER ihre eigene Zahl hinaus (`max_rounds=1`),
        UNABHAENGIG davon, ob sie vor/hinter/gleichauf mit dir ist (anders
        als Catch-up gibt es hier keine "hinter mir"-Vorbedingung -- genau
        der von der Spec verlangte "ich muss mal weg, lass die Personas
        ihren Abschnitt vorspielen"-Fall, der bei bereits erreichter
        Paritaet ueber [3] bisher wirkungslos war).

        P1-Fix (BL1-FIX-SPEC-R4 2026-10-21): `current_or_recent_table_
        members` lieferte fuer Vorspielen faelschlich auch die Mitglieder
        des zuletzt GESCHLOSSENEN Tisches -- direkt NACH einem
        abgeschlossenen Gruppenabschnitt waren cqb/face damit fuer [5]
        unerreichbar, obwohl ihr gemeinsamer Abschnitt bereits fertig war.
        Vorspielen zieht jetzt `current_active_table_members` ab (nur ein
        WIRKLICH laufender Abschnitt schuetzt), Catch-up bleibt bei der
        breiteren `current_or_recent_table_members`-Abzugsmenge."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            self._print(
                "Personas spielen lassen erfordert eine konfigurierte Laufumgebung (run_dir/"
                "states_dir/schema_path) -- hier nicht konfiguriert, keine Aktion."
            )
            return
        from ..lab.runner import active_lock_pid
        pid = active_lock_pid(self.run_dir, exclude_pid=os.getpid())
        if pid is not None:
            self._print(
                f"Personas spielen lassen: ein aktiver Lab-Lauf (pid={pid}) kontrolliert diese "
                "Datenablage — kein zweiter schreibender Controller (H-D)."
            )
            return

        from ..core import catchup, store as core_store
        ready_keys = catchup.ready_persona_keys(self)
        # M1-Fix (BL1-FIX-SPEC-R4, P1): Vorspielen [5] schuetzt NUR einen
        # WIRKLICH aktiv laufenden gemeinsamen Abschnitt (current_active_
        # table_members, KEIN Closed-Fallback) -- die Mitglieder eines
        # bereits geschlossenen Tisches sind fuer Vorspielen wieder
        # wahlbar. Catch-up [3] behaelt den breiteren Schutz (current_or_
        # recent_table_members) unveraendert.
        if vorspielen:
            current_table = core_store.current_active_table_members(self.run_dir, self.participant_id)
        else:
            current_table = core_store.current_or_recent_table_members(self.run_dir, self.participant_id)
        eligible_pool = ready_keys - {self.participant_id} - self._excluded_personas - current_table
        if not eligible_pool:
            self._print(
                "Personas spielen lassen: aktuell keine wahlbaren Kandidaten (alle entweder an "
                "deinem Tisch, ausgeschlossen oder noch nicht spielbereit)."
            )
            return

        counts = core_store.sections_played_by_participant(self.run_dir)
        if vorspielen:
            # M1-Fix: Vorspielen hat KEINE "hinter mir"-Vorbedingung -- jede
            # wahlbare Persona darf unabhaengig von ihrer eigenen Zahl einen
            # Abschnitt vorlegen (`run_catch_up`s `max_rounds` traegt das
            # bereits: `per_target = eigene_zahl + max_rounds`, IMMER > eigene
            # Zahl).
            behind = sorted(eligible_pool)
            action_label = "Vorspielen (je 1 Abschnitt ueber die eigene Zahl hinaus)"
        else:
            my_count = counts.get(self.participant_id, 0)
            behind = sorted(pk for pk in eligible_pool if counts.get(pk, 0) < my_count)
            if not behind:
                self._print(
                    f"Personas spielen lassen: alle wahlbaren Kandidaten sind bereits bei deiner "
                    f"Abschnittszahl ({my_count}) -- kein Catch-up noetig (fuer Vorspielen vor "
                    "deinem naechsten Abschnitt: Menuepunkt [5])."
                )
                return
            action_label = f"Catch-up (bis zu deiner Abschnittszahl {my_count})"

        self._print(
            f"Wahlbare Kandidaten fuer {action_label} (Abschnitte bisher): "
            + ", ".join(f"{pk}({counts.get(pk, 0)})" for pk in behind)
        )
        raw, control = self._readline_with_controls(
            f"Welche jetzt spielen lassen? (kommagetrennt, leer = alle {behind}): ",
            context="Personas-spielen-lassen-Auswahl",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Personas spielen lassen abgebrochen -- kein Fenster gestartet.")
            return
        raw = raw.strip()
        if not raw:
            chosen = set(behind)
        else:
            requested = {p.strip() for p in raw.split(",") if p.strip()}
            unknown = requested - set(behind)
            if unknown:
                self._print(
                    f"Personas spielen lassen: {sorted(unknown)} sind keine wahlbaren Kandidaten "
                    f"(wahlbar: {behind}) -- kein Fenster gestartet."
                )
                return
            chosen = requested

        self._print(
            f"⏳ Das spielt jetzt den/die Abschnitt(e) von {sorted(chosen)} -- du wartest "
            "(dein eigenes Tischspiel ist davon unberuehrt)."
        )
        report = catchup.run_catch_up(
            self, selected=chosen, current_table_members=current_table,
            target=None, max_rounds=1 if vorspielen else None,
        )
        for note in report.notes:
            self._print(f"  {note}")
        self._print(
            f"Personas spielen lassen beendet: Start {report.start_counts} -> Ende "
            f"{report.end_counts} (Fenster: {report.windows_run}, gestoppt: {report.stopped}"
            f"{' (' + report.stopped_reason + ')' if report.stopped_reason else ''}, "
            f"blockiert/kein Fortschritt: {report.blocked or '(keine)'})."
        )

    def _cmd_active_group_settings(self) -> None:
        """SPIELFLUSS-SPEC.md Abschnitt 3 ("aktive Gruppe/Ausschluss"):
        einfache Umschalt-Bedienung -- Reuse der bestehenden Teilmengen-
        Auswahl-Idee (`lab/cli.py --personas`/`ai_personas`), KEINE neue
        Community-Struktur. Ausgeschlossene Personas sind fuer 'Personas
        spielen lassen' NIE Kandidat (s. `_cmd_catch_up_personas`)."""
        if self.run_dir is None:
            self._print("Aktive Gruppe erfordert eine konfigurierte Laufumgebung (run_dir).")
            return
        from ..core import catchup
        ready_keys = sorted(catchup.ready_persona_keys(self) - {self.participant_id})
        if not ready_keys:
            self._print("Aktive Gruppe: keine spielbereiten Personas in deiner Community.")
            return
        active = [pk for pk in ready_keys if pk not in self._excluded_personas]
        excluded = [pk for pk in ready_keys if pk in self._excluded_personas]
        self._print(
            f"Aktive Gruppe (nimmt an Catch-up/Vorspielen teil): {active or '(keine)'}\n"
            f"Ausgeschlossen (nie Kandidat, blockt/nervt nie): {excluded or '(keine)'}"
        )
        raw, control = self._readline_with_controls(
            "Persona ausschliessen/wieder aufnehmen (Name eingeben zum Umschalten, leer = "
            "unveraendert zurueck): ", context="Aktive-Gruppe-Einstellung",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            return
        raw = raw.strip()
        if not raw:
            return
        if raw not in ready_keys:
            self._print(f"Aktive Gruppe: {raw!r} ist keine bekannte spielbereite Persona ({ready_keys}).")
            return
        if raw in self._excluded_personas:
            self._excluded_personas.discard(raw)
            self._print(f"'{raw}' wieder in der aktiven Gruppe.")
        else:
            self._excluded_personas.add(raw)
            self._print(f"'{raw}' ausgeschlossen -- nie mehr Catch-up-/Vorspiel-Kandidat, bis wieder aufgenommen.")

    def _cmd_menu_charaktere(self) -> None:
        """KISS-Submenue 'Charaktere' (02 §A) — dispatcht additiv auf die
        UNVERAENDERTEN Kommandos `n`/`i`/`e`.

        W24b (BRIEF-W24b.md Punkt 2): zeigt sich selbst erneut, wenn die
        darunterliegende Figurwahl (`_cmd_new_or_switch_character`) explizit
        ueber `/zurueck` verlassen wurde (Rueckgabe `True`), statt wie
        vorher pauschal bis ins Hauptmenue durchzufallen -- '/zurueck'/
        '/abbrechen'/'/pause' DIREKT an diesem Untermenue-Prompt gehen
        unveraendert sofort zurueck ins Hauptmenue."""
        while True:
            self._print(
                "Charaktere -- [1] Auswaehlen/neu erstellen  [2] Importieren  "
                "[3] Exportieren/ansehen (/zurueck fuer Hauptmenue)"
            )
            text, control = self._readline_with_controls(
                "Auswahl: ", context="Charaktere-Untermenue",
            )
            if control in ("zurueck", "abbrechen", "pause"):
                return
            choice = text.strip()
            if choice == "1":
                if self._cmd_new_or_switch_character():
                    continue
                return
            elif choice == "2":
                self._cmd_import()
                return
            elif choice == "3":
                self._cmd_export()
                return
            else:
                self._print(f"Unbekannte Auswahl: {choice!r} -- zurueck zum Hauptmenue.")
                return

    _INTRO_LINES = (
        "  1) Die Spielleitung (SL) fuehrt die Welt -- du entscheidest deine Figur.",
        "  2) Gespielt wird in Abschnitten; der letzte gueltige Save ist deine Fortsetzungsbasis.",
        # R4 (T-Befund 1, UX04/05, Korrekturzyklus 1): die alte Zeile
        # bewarb '/stand'/'/verlauf'/'/pause' unpraezise als "an jeder
        # Eingabe" -- '?'/'/hilfe'/'/stand' sind das tatsaechlich,
        # '/verlauf'/'/pause' gelten dagegen nur im laufenden
        # Spielabschnitt (sonst ehrlicher Hinweis statt Ausfuehrung).
        "  3) Hilfe ohne Modellanfrage: '?'/'/hilfe'/'/stand' an jeder Eingabe; "
        "'/verlauf'/'/pause' im laufenden Spielabschnitt.",
    )

    def _maybe_show_first_run_intro(self) -> None:
        """UX02 (02 §B): kurze Erstfuehrung, NICHT blockierend (kein
        `_readline`-Aufruf hier) -- 'ueberspringbar' ist dadurch der
        denkbar guenstigste Fall: es gibt nichts zu beantworten, die
        naechste normale Auswahl laeuft sofort weiter, kein bestehendes
        Testskript verliert dadurch eine Eingabezeile. Die Praeferenz liegt
        GETRENNT vom v7-Save/Onboarding-Scratch (`onboarding_prefs.py`) --
        ein fehlender/defekter Wert zeigt die Fuehrung einfach erneut,
        beruehrt aber NIE Figur-/Katalogdaten (0 GM-/Persona-Calls, reine
        Anzeige). 'einfuehrung' im Hauptmenue zeigt denselben Text jederzeit
        erneut (Wiederholbarkeit, 02 §B)."""
        from . import onboarding_prefs
        data_root = self.onboarding_dir.parent
        # R9 (C-K2, UX02, Korrekturzyklus 1): PRO `participant_id` statt
        # pro `data_root` -- vorher sah nur die GLOBAL erste Person, die
        # dieses Datenverzeichnis je gestartet hat, die Erstfuehrung; jede
        # ueber 'registrieren' neu hinzukommende Person auf demselben
        # Geraet bekam sie NIE automatisch angezeigt (nur manuell ueber
        # 'einfuehrung' abrufbar). Dieselbe fail-soft-Semantik bleibt
        # erhalten (reine Anzeige-Praeferenz, kein Figur-/Katalogbezug).
        prefs = onboarding_prefs.load(data_root, self.participant_id)
        if prefs.tutorial_seen:
            return
        self._print("Kurze Einfuehrung (jederzeit erneut über 'einfuehrung' im Hauptmenue):")
        for line in self._INTRO_LINES:
            self._print(line)
        onboarding_prefs.mark_tutorial_seen(data_root, self.participant_id)

    def _cmd_show_intro_again(self) -> None:
        """UX02: dieselbe Fuehrung jederzeit erneut abrufbar -- eigener,
        neuer Menuewort-Dispatch ('einfuehrung'/'tutorial'), beruehrt
        `_cmd_settings()` NICHT (kein zusaetzlicher Readline-Aufruf dort,
        keine Regression fuer bestehende 's'-Tests)."""
        self._print("Einfuehrung:")
        for line in self._INTRO_LINES:
            self._print(line)

    def _cmd_menu_fortsetzen(self) -> None:
        """KISS 'Fortsetzen' (02 §A/§E): fuehrt NUR dann tatsaechlich fort,
        wenn `_build_resume_card()` einen real existierenden, zu diesem
        Teilnehmer gehoerenden Stand ausweist (UX11) — ohne Beleg wird
        Fortsetzen NICHT zum Neuanfang (02 §A: 'ausblenden oder deaktiviert
        mit einem kurzen ehrlichen Hinweis'), es startet insbesondere KEINE
        neue Runde/Community an dieser Stelle.

        G03-Gesamtfix (dieselbe Autoritaet fuer Karte UND Dispatch):
        - UX12: ein bekannter, aber GERADE nicht lesbarer Current
          (`card.authority_unresolved`) ist ein sicherer STOPP -- kein
          stiller Rueckfall auf eine evtl. veraltete Fassung, keine neue
          Runde als getarnter Ersatz.
        - P04/Q07 (REVIEW.md R03, 05.10.2026): eine offene, noch nicht
          abgeschlossene Erschaffung (`card.pending_creation`) OHNE jede
          bereits existierende Figur liefert jetzt eine eigene,
          unterscheidbare Fortsetzen-Antwort UND bindet sie tatsaechlich an
          den vorhandenen Verlauf -- `_cmd_new_or_switch_character()` wird
          direkt aufgerufen (derselbe Weg wie 'n'/[charaktere], derselbe
          `onboarding_key`), ein echter Erschaffungszug folgt (kein reiner
          Wegweiser-Text mehr, der vorher sogar bei einer real offenen
          Erschaffung ohne jeden weiteren Zug kam).
        - P09: eine real gebundene, noch offene Mehrpersonen-Tischbindung
          (`card.open_section_id`, dieselbe Lock-Autoritaet wie die Karte)
          hat Vorrang vor dem pauschalen Solo-Aufruf -- `_resume_bound_table`
          setzt GENAU diesen Tisch mit seiner tatsaechlichen, bereits
          akzeptierten Besetzung fort (kein `_cmd_local_round([])`, das
          strukturell einen ANDEREN -- leeren -- Tisch-Namensraum trifft,
          s. `_cmd_local_round`-Docstring 'table_id = local-<leader>
          [-<gaeste>]'). Bleibt die gebundene Tischzuordnung trotz
          bekanntem Lock nicht eindeutig lesbar, ist das ebenfalls ein
          sicherer Stopp (UX12), kein automatischer Solo-/Ersatztisch."""
        card = self._build_resume_card()
        # R2 (C-M2, UX11): Gate auf `community_id ODER chrononaut_id ODER
        # pending_creation ODER authority_unresolved` -- eine offene
        # Erschaffung oder ein bekannter, nur gerade nicht lesbarer Current
        # sind ebenfalls ein real fortsetzbarer/zu behandelnder Zustand,
        # keine leere Karte.
        if card is None or not (
            card.community_id or card.chrononaut_id or card.pending_creation or card.authority_unresolved
        ):
            self._print(
                "Fortsetzen: kein tatsaechlich fortsetzbarer Stand gefunden (weder Community noch "
                "Figur-Save) — bitte zuerst 'spielen'/'charaktere' fuer einen Start nutzen."
            )
            return
        if card.authority_unresolved:
            self._print(
                "Fortsetzen nicht moeglich: der aktuell veroeffentlichte Spielstand ist gerade "
                "nicht lesbar -- keine Fortsetzen-Autoritaet (kein Reparaturwrite, kein Rueckfall "
                "auf eine aeltere Fassung, keine neue Runde als Ersatz)."
            )
            return
        # R2-Folgefix: `card.community_id` kann jetzt (Solo-Figur ohne
        # Community) real `None` sein -- kein literales "None" in der
        # Anzeige (UX22-Vertrag, wie bereits in `render_boot_menu`).
        community_display = card.community_id or "keine Community"
        self._print(f"Fortsetzen: {community_display} · {card.participant_id} · {card.chrononaut_id or '—'}.")
        if card.chrononaut_id is not None and card.open_section_id is not None:
            table = self._resolve_bound_table_for_resume(card.chrononaut_id, card.open_section_id)
            if table is None:
                self._print(
                    f"Fortsetzen nicht moeglich: die gebundene Tischzuordnung ('{card.open_section_id}') "
                    "ist gerade nicht eindeutig lesbar -- kein automatischer Solo-/Ersatztisch, keine "
                    "alte Save-Uebernahme (sicherer Stopp)."
                )
                return
            self._resume_bound_table(table)
            return
        if card.chrononaut_id is None and card.pending_creation:
            # Q07 (REVIEW.md R03, 05.10.2026, vormals ":637ff"): dieser Zweig
            # gab bisher NUR einen Wegweiser-Text aus ("bitte ueber
            # '[n]'/[charaktere] fortsetzen") -- kein Erschaffungszug folgte,
            # der Fake-GM-Zaehler blieb 0. Anzeige (`card.pending_creation`,
            # oben aus `_build_resume_card`) UND Ausfuehrung nutzen jetzt
            # DENSELBEN Zustandsentscheid: dieselbe Methode, die 'n'/
            # [charaktere] bereits fuer eine offene Erschaffung aufruft
            # (`_cmd_new_or_switch_character`, bindet ueber denselben
            # unveraenderten `onboarding_key=self.participant_id`-Scratch an
            # genau den Auftrag, den `onboarding.peek` fuer die Karte
            # gelesen hat) wird HIER direkt weiterverwendet -- kein neuer
            # Vorgang, keine zweite Erschaffungsautoritaet, derselbe echte
            # SL-Dialog setzt beim naechsten Schritt fort (`turn_idx=len(
            # state.steps)`), inklusive aller bestehenden Guards (Lab-
            # Aktivitaet, Admission-Gate, SL-Anbindungspruefung).
            self._print(
                "Fortsetzen: eine begonnene Figur-Erschaffung ist noch offen -- wird jetzt direkt "
                "fortgesetzt (derselbe Erschaffungsauftrag, kein neuer Vorgang)."
            )
            self._cmd_new_or_switch_character()
            return
        self._cmd_local_round([])

    def _resolve_bound_table_for_resume(self, chrononaut_id: str, table_id: str):
        """G03/P09: laedt GENAU den Tisch, an den `chrononaut_id` laut Lock
        gebunden ist -- dieselbe `table_id`, die bereits auf der Karte steht
        (`core.store.locked_table_id`). Reiner Lesezugriff, kein Write.
        Liefert `None` bei JEDEM nicht eindeutig sicheren Fall (Tischdatei
        nicht ladbar, Tisch nicht `active`, `chrononaut_id` tatsaechlich
        nicht Mitglied) -- der Aufrufer behandelt `None` HIER als sicheren
        STOPP (UX12: die Karte zeigte bereits einen bekannten Lock; ein
        nicht auflösbares Detail darf nicht in einen stillen Solo-Fallback
        kippen)."""
        if self.run_dir is None:
            return None
        from ..core import store as core_store
        try:
            table = core_store.Table.load(self.run_dir, table_id)
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            return None
        if table.status != "active":
            return None
        if chrononaut_id not in table.chrononaut_ids.values():
            return None
        return table

    def _resume_bound_table(self, table) -> None:
        """G03/P09 (ZEITRISS Terminal UX-1, Korrekturzyklus 2, General-
        Befund 'P09_MAIN_RESUME_TWO_PERSON_SECTION'): setzt einen bereits
        bestehenden, real gebundenen Tisch (Leader- ODER Gast-Resume, z.B.
        nach einem echten OS-Neustart) tatsaechlich fort -- OHNE den
        Einladungs-/Konsens-Loop aus `_cmd_local_round` erneut zu
        durchlaufen. Die Mitgliedschaft dieses Tisches ist bereits real
        zugesagt/gebunden (sonst wuerde die Tischdatei nicht existieren) --
        ein erneuter Consent-Dialog oder ein erneuter Persona-Modellaufruf
        fuer bereits aufgenommene Mitglieder waere ein verbotener
        Doppelcall/Publikation. Jeder MENSCH am geteilten Geraet bestaetigt
        weiterhin ueber `_local_round_handoff` (`guided=True`), bevor er
        tatsaechlich eingibt -- kein KI-Ersatz, kein stiller zweiter
        Schreiber. `table.leader`/`table.members`/`table.chrononaut_ids`
        bleiben unveraendert (kein Write hier, `_run_table_round` schreibt
        ausschliesslich ueber den bestehenden `app_service.run_play_session`-
        Pfad, identisch zum frischen Einladungsweg)."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None or self.gm_transport_factory is None:
            self._print(
                "Fortsetzen (gebundener Tisch) erfordert eine konfigurierte Laufumgebung (run_dir/"
                "states_dir/schema_path) und eine SL-Anbindung (gm_transport_factory) — hier nicht "
                "konfiguriert, kein Spielstart."
            )
            return
        if self._lab_active_guard("Fortsetzen (gebundener Tisch)"):
            return
        from ..core import store as core_store
        from ..core.persona_state import PersonaStateStore

        humans = {pid for pid, _name in self._local_round_list_humans()}

        def _is_persona_member(pid: str) -> bool:
            return pid != self.participant_id and pid not in humans

        leader_id = table.leader
        leader_persona_id = leader_id if _is_persona_member(leader_id) else None
        try:
            resolved_leader = self._resolve_member(leader_id)
        except _ActiveSaveUnresolved:
            self._print(
                "Fortsetzen nicht moeglich: der aktuell veroeffentlichte Spielstand des Leaders ist "
                "gerade nicht lesbar -- kein Spielstart, bis die tatsaechliche Autoritaet geklaert ist."
            )
            return
        if resolved_leader is None or resolved_leader[1] != table.chrononaut_ids.get(leader_id):
            self._print(
                f"Fortsetzen nicht moeglich: die Leaderzuordnung des gebundenen Tisches "
                f"'{table.table_id}' ist nicht konsistent lesbar -- kein automatischer Ersatz "
                "(sicherer Stopp)."
            )
            return
        active_save, _leader_chrono = resolved_leader
        leader_driver = None
        if leader_persona_id:
            if self.persona_driver_factory is None:
                self._print(
                    f"Fortsetzen nicht moeglich: KI-Leader '{leader_persona_id}' erfordert eine "
                    "konfigurierte Persona-Anbindung (persona_driver_factory) — hier nicht konfiguriert."
                )
                return
            try:
                leader_driver = self.persona_driver_factory(leader_persona_id)
            except Exception:
                self._print(self._opaque_boundary_error(f"Fortsetzen: KI-Leader '{leader_persona_id}' nicht moeglich"))
                return

        guest_specs: list[tuple[str, bool, dict, object | None]] = []
        for pid in table.members:
            if pid == leader_id:
                continue
            is_persona = _is_persona_member(pid)
            try:
                resolved = self._resolve_member(pid)
            except _ActiveSaveUnresolved:
                self._print(
                    f"Fortsetzen nicht moeglich: der aktuell veroeffentlichte Spielstand von '{pid}' "
                    "ist gerade nicht lesbar -- kein Spielstart, bis die tatsaechliche Autoritaet "
                    "geklaert ist."
                )
                return
            if resolved is None or resolved[1] != table.chrononaut_ids.get(pid):
                self._print(
                    f"Fortsetzen nicht moeglich: die Mitgliedzuordnung ('{pid}') des gebundenen "
                    f"Tisches '{table.table_id}' ist nicht konsistent lesbar -- kein automatischer "
                    "Ersatz (sicherer Stopp)."
                )
                return
            guest_active_save, _guest_chrono = resolved
            driver = None
            if is_persona:
                if self.persona_driver_factory is None:
                    self._print(
                        f"Fortsetzen nicht moeglich: '{pid}' erfordert eine konfigurierte Persona-"
                        "Anbindung (persona_driver_factory) — hier nicht konfiguriert."
                    )
                    return
                try:
                    driver = self.persona_driver_factory(pid)
                except Exception:
                    self._print(self._opaque_boundary_error(f"Fortsetzen: '{pid}' nicht moeglich"))
                    return
            guest_specs.append((pid, is_persona, guest_active_save, driver))

        ps_store = PersonaStateStore(schema_path=self.schema_path)
        lobby = core_store.Lobby(self.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join(leader_id)
        for guest_id, _is_p, _save, _driver in guest_specs:
            lobby.join(guest_id)
        self._print(
            f"Gebundener Tisch erkannt ({table.table_id}, Mitglieder: {table.members}) -- wird mit "
            "dieser tatsaechlichen Besetzung fortgesetzt (keine neue Einladung, keine Doppelcalls)."
        )
        self._run_table_round(
            table, lobby, ps_store, leader_id, leader_persona_id, leader_driver, active_save, guest_specs,
            guided=True, current_focus_pid=self.participant_id,
        )

    def _build_resume_card(self, participant_id: str | None = None) -> ResumeCard | None:
        """11 §2: eine verstaendliche Fortsetzen-Karte aus vorhandenen
        Daten bauen -- vorher wurde IMMER `render_boot_menu(None)` gerufen
        (Review-Befund I3: 'Fortsetzen-Karte wird dort nie befuellt').

        G04/UX20 (General-Befund G04, `_readline_with_controls`, W3-Hunk
        selektiv uebernommen, s. W3-REUSE.md): optionaler `participant_id`
        (Default `None` -> `self.participant_id`, unveraendertes Verhalten
        fuer JEDEN bestehenden Aufrufer ohne dieses Argument) laesst `/stand`
        an einem geteilten Terminal den Stand der GERADE EINGEBENDEN Person
        zeigen statt pauschal des aeusseren Sessionteilnehmers -- dieselbe
        Lesefunktion/Autoritaet fuer jede gueltige lokale Teilnehmer-ID.

        UX-1/UX11-Fix (OFFENE_BEDIENBEFUNDE.md Punkt 1, General-Befund G01):
        `community_id` war HIER vorher fest `None` codiert -- die Bedingung
        in `render_boot_menu()` (`resume.community_id`) war dadurch ueber den
        normalen Startweg STRUKTURELL NIE erfuellbar, die Fortsetzen-Zeile
        erschien nie, auch nicht bei vorhandenem Stand. Jetzt: reine
        Lesefunktion `community_bootstrap.peek` (bereits produktiv in
        `_cmd_community` genutzt, kein neuer Speicherort, kein Write) prueft
        die tatsaechlich real existierende, zu DIESEM Teilnehmer gehoerende
        Gemeinschaft `community-<participant_id>` -- NUR wenn `run_dir`
        konfiguriert ist (ohne Laufumgebung bleibt die Karte wie vorher ohne
        Community-Teil, kein Regressionsrisiko fuer die vielen Tests ohne
        `run_dir`). Ein nicht lesbarer/defekter Bootstrap-Datensatz faellt
        auf `None` zurueck (Anzeige bleibt sicher, kein Absturz) -- die
        tatsaechliche Autoritaetspruefung beim echten Fortsetzen-Versuch
        (`_cmd_community`/`_cmd_local_round`) bleibt davon unberuehrt und
        eigenstaendig fehlerfest (UX12). Kein Schreibzugriff beim blossen
        Kartenaufbau (02 §E: 'Keine neuen Saves/Claims/Personas allein beim
        Oeffnen der Karte').

        G03/P03 (General-Befund 'P03_STALE_RESUME_SUMMARY'): die Karte nutzte
        HIER bisher AUSSCHLIESSLICH `onboarding.peek(...).final_save` fuer
        die Zusammenfassung -- einen bereits veroeffentlichten NEUEREN
        Current (`core.store.publish_current_save`, z.B. nach einem
        gespielten Abschnitt) zeigte sie dadurch NIE, obwohl genau dieser
        Current dieselbe Autoritaet ist, die jeder echte Spielstart nutzt
        (`self._resolve_active_save`, von `_cmd_local_round`/`_resolve_member`
        bereits produktiv verwendet). Jetzt DIESELBE Funktion/Autoritaet wie
        der tatsaechliche Start -- Karte und Dispatch koennen dadurch nicht
        mehr auseinanderlaufen. Ein bekannter, aber GERADE nicht lesbarer
        Current (`unresolved=True`) wird ehrlich als solcher markiert
        (`authority_unresolved`, UX12) statt stillschweigend auf den
        (ggf. veralteten) Onboarding-Stand zurueckzufallen -- kein
        Reparaturwrite, reine Anzeige/Signalisierung.

        G03/P04 (General-Befund 'P04_OPEN_CREATION_NOT_OFFERED'): eine
        bereits BEGONNENE, aber noch nicht abgeschlossene Erschaffung
        (`onboarding.peek(...).status == 'in_progress'`) lieferte bisher
        `None` -- obwohl es dafuer real etwas Fortsetzbares gibt. Jetzt wird
        dieser Zustand als eigenes Flag benannt (kein erfundener Chrononaut/
        Save), getrennt von einem offenen SPIELabschnitt (`open_section_id`)
        und von einem bereits abgeschlossenen Save.

        `open_section_id` traegt jetzt die tatsaechliche Tisch-/Lock-
        Bindung (`core.store.locked_table_id`, reiner Lesezugriff auf
        `locks.json`) statt des vorherigen Literals 'aktiv' -- der Dispatch
        (`_cmd_menu_fortsetzen`) kann so dieselbe konkrete ID verwenden wie
        die Anzeige, statt sie durch einen Platzhaltertext zu verdecken."""
        participant_id = participant_id or self.participant_id
        chrononaut_id = catalog.last_selected(self.catalog_dir, participant_id)
        state = onboarding.peek(self.onboarding_dir, participant_id)
        onboarding_final_save = state.final_save if state is not None else None
        final_save, unresolved = self._resolve_active_save(participant_id, onboarding_final_save)
        pending_creation = state is not None and state.status == "in_progress"
        community_id: str | None = None
        open_section_id: str | None = None
        if self.run_dir is not None:
            try:
                from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
                candidate_id = f"community-{participant_id}"
                existing = peek_bootstrap(self.run_dir / "community", candidate_id)
                if existing is not None:
                    community_id = candidate_id
            except (OSError, ValueError, KeyError):
                community_id = None
            if chrononaut_id is not None:
                try:
                    from ..core import store as core_store
                    open_section_id = core_store.locked_table_id(self.run_dir, chrononaut_id)
                except (OSError, ValueError):
                    open_section_id = None
        if (
            chrononaut_id is None and final_save is None and community_id is None
            and not unresolved and not pending_creation
        ):
            return None
        if unresolved:
            summary = "aktueller Spielstand gerade nicht lesbar -- keine Fortsetzen-Autoritaet (kein Reparaturwrite)"
        elif final_save is not None:
            summary = None
            chars = final_save.get("characters")
            if isinstance(chars, list) and chars and isinstance(chars[0], dict):
                # W45: das echte v7-Schema fuehrt das Figurenlevel unter
                # `lvl` (saveGame.v7.export.schema.json, Pflichtfeld) -- das
                # alte `level` wurde nie vom Schema verlangt, nur von
                # schmalen Legacy-Testfixtures zufaellig mitgefuehrt;
                # `lvl` hat Vorrang, `level` bleibt als reiner Fallback.
                lvl = chars[0].get("lvl", chars[0].get("level", "?"))
                summary = f"{chars[0].get('name', '?')} (Level {lvl})"
        elif pending_creation:
            summary = "Figur-Erschaffung begonnen, noch nicht abgeschlossen (fortsetzen ueber 'n'/[charaktere])"
        else:
            summary = None
        return ResumeCard(
            community_id=community_id, participant_id=participant_id,
            chrononaut_id=chrononaut_id, last_valid_save_summary=summary,
            open_section_id=open_section_id, pending_creation=pending_creation,
            authority_unresolved=unresolved,
        )

    def _opaque_boundary_error(self, context: str, *, attempted: bool = False) -> str:
        """G05 (ZEITRISS Terminal UX-1, Korrekturzyklus 2, General-Befund
        'P06_RAW_FACTORY_DETAIL_EXPOSED'): EINE gemeinsame, ruhige
        Fehlermeldung fuer alle Fehler an der externen GM-/Persona-/CLI-
        Grenze (`gm_transport_factory`/`persona_driver_factory`-Aufrufe und
        ihre unmittelbaren Transportfehler) -- NIE die urspruengliche
        Exception-/Traceback-/Key-/Promptdetails im Spielertext, egal was
        die konkrete Anbindung konkret wirft (z.B. ein Secret-Fragment in
        einer defekten Factory). Kein Fallback, kein zusaetzlicher Call;
        das Originaldetail bleibt ausschliesslich der echten Exception
        selbst (fuer einen separaten, hier nicht erweiterten technischen
        Beleg/Log) vorbehalten, nicht der Spieleransicht.

        Q05B (REVIEW.md R04, 05.10.2026, UX18): `attempted` unterscheidet
        VOR-Anfrage-gescheitert von Anfrage-versucht/Ergebnis-unklar --
        vorher behauptete diese EINE Meldung an JEDER Aufrufstelle "kein
        Modellaufruf", auch dort, wo `lobby_service.request_admitted_
        decision`/`_admitted_invite_decision` zuvor bereits `request_
        ledger.begin()` UND den tatsaechlichen `driver.decide(ctx)`-Aufruf
        ausgefuehrt hatten, bevor die Ausnahme hier ankam (Fabrikbau
        `persona_driver_factory(...)`/`gm_transport_factory(...)` bleibt
        dagegen echt vor-Anfrage, `attempted` bleibt dort `False`, der
        Standardwert aendert also kein bestehendes Verhalten). Kein
        falsches Nullaufruf-/Nullkostenversprechen, kein automatischer
        Retry (der Aufrufer bricht weiterhin einfach ab), weiterhin keine
        Secret-/Traceback-Ausgabe in beiden Zweigen."""
        if attempted:
            return (
                f"{context} — technischer Fehler an der externen Anbindung NACH einem bereits "
                "versuchten Aufruf (Ergebnis unklar, moeglicherweise bereits Wirkung/Kosten "
                "entstanden) -- kein automatischer erneuter Versuch. Keine Fehlerdetails in "
                "dieser Ansicht (Schutz vor Secret-/Innendetail-Lecks)."
            )
        return (
            f"{context} — technischer Fehler an der externen Anbindung, kein Modellaufruf. "
            "Keine Fehlerdetails in dieser Ansicht (Schutz vor Secret-/Innendetail-Lecks)."
        )

    # R5P02 (ZEITRISS TERMINAL-UX1-R6-FERTIGSTELLUNG): die EINZIGEN
    # `PersonaCreationOutcome.reason`-Praefixe aus
    # `domain/zeitriss/community_creation.py`, die ein `error`-Outcome
    # NACHWEISLICH VOR jedem Request (`gm_transport_factory`/
    # `persona_driver_factory` wirft beim Fabrikbau, oder gar kein
    # Bootstrap-Profilentwurf gefunden) zuordnen -- gelesen, nicht
    # geaendert, reine Textanker wie der bestehende Redaktionsabgleich in
    # `_redact_creation_status_text`. JEDER andere `error`-Grund (z.B. ein
    # nach echtem `gm_transport.turn()` gefangener Fehler aus
    # `core/creation_service.run_admitted_creation_dialog`) ist belegt
    # versucht.
    _PRE_REQUEST_CREATION_ERROR_PREFIXES = (
        "kein Bootstrap-Profilentwurf fuer ",
        "SL-Anbindung nicht verfuegbar: ",
        "Persona-Anbindung nicht verfuegbar: ",
    )

    def _is_confirmed_pre_request_creation_error(self, reason: object) -> bool:
        """`True` NUR, wenn `reason` nachweislich einem der obigen,
        bekannten Vor-Anfrage-Faelle entspricht -- jeder unbekannte/fehlende
        Grund liefert `False` (sicherer Default: im Zweifel als belegt
        versucht behandeln, NIE faelschlich 'kein Modellaufruf' behaupten)."""
        return isinstance(reason, str) and reason.startswith(self._PRE_REQUEST_CREATION_ERROR_PREFIXES)

    def _lab_active_guard(self, action_label: str) -> bool:
        """G3b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, REVIEW-
        HEADLESS-BETRIEBSGRENZEN.md Probe 05): derselbe Guard wie in
        `_cmd_lobby_initiative`/`_cmd_local_round` (`active_lock_pid(...,
        exclude_pid=os.getpid())`), jetzt als gemeinsamer Baustein fuer ALLE
        uebrigen TUI-Schreibwege (Erschaffung/Import/Community) -- vorher
        sassen die Guards nur vor `b`/`l`; ein aktiver Lab-Lauf blieb fuer
        `n`/`i`/`c` ein unbewachter zweiter Schreiber auf Katalog/Marker/
        State/Current (Probe 05: 7 Dateien bei lebendem Labowner). Liefert
        `True`, wenn eine Ablehnung ausgesprochen wurde -- der Aufrufer
        bricht dann SOFORT ab, vor jedem Write. `run_dir is None` (kein
        Lab-faehiges Setup) bleibt unveraendert (kein Guard moeglich/noetig,
        identisch zu den bestehenden Aufrufstellen). Lesende `lab status`/
        `lab attach` bleiben von diesem Guard unberuehrt."""
        if self.run_dir is None:
            return False
        from ..lab.runner import active_lock_pid
        pid = active_lock_pid(self.run_dir, exclude_pid=os.getpid())
        if pid is None:
            return False
        self._print(
            f"{action_label}: ein aktiver Lab-Lauf (pid={pid}) kontrolliert diese Datenablage "
            "— kein zweiter schreibender Controller (H-D/G3b). Nur lesende Ansicht moeglich "
            "('python scripts/mmo_sim.py lab status/attach')."
        )
        return True

    def _cmd_new_or_switch_character(self) -> bool:
        """A17 (WEGKARTE §8, 11 §3, REVIEW-P2V.md A17 OFFEN): echter,
        fortsetzbarer SL-Erschaffungsdialog statt einer einzelnen fest
        gespeicherten Frage/Antwort. Der Assistent oeffnet ueber den
        `gm_transport_factory` (derselbe GM-Transport-Vertrag wie das Spiel,
        eigene Chat-Identitaet `onboarding-<participant_id>` -- D3-konform
        getrennt vom Spielverlauf) einen Dialog: SL-Frage anzeigen, Antwort
        des Menschen einholen, SOFORT persistieren (Crash-Sicherheit, s.
        `onboarding.record_step`), bis die SL-Antwort einen strukturell
        gueltigen v7-Save-Block enthaelt. Bricht der Mensch vorher ab (EOF),
        bleibt die Erschaffung offen/fortsetzbar (kein Dummy-Save, kein
        gezaehlter Fortschritt). Ohne konfigurierte SL-Anbindung bleibt dies
        ein ehrlicher Teilstand (kein stiller Fallback auf eine Dummyfigur).

        W24b (BRIEF-W24b.md Punkt 2): liefert `True` genau dann, wenn die
        Figurwahl selbst (Kontext "Figurwahl", s. unten) ueber `/zurueck`
        verlassen wurde -- ein direkter Aufrufer mit eigener Untermenue-
        Ebene (`_cmd_menu_charaktere`) nutzt das, um GENAU diese Ebene
        erneut zu zeigen statt pauschal bis ins Hauptmenue durchzufallen.
        Jeder andere Rueckweg (abbrechen/pause/EOF/abgeschlossene Auswahl)
        liefert `False`/`None` -- bestehende Aufrufer, die den Rueckgabewert
        ignorieren, verhalten sich unveraendert."""
        if self._lab_active_guard("Neue/wechselnde Figur"):
            return
        entries = catalog.list_for_participant(self.catalog_dir, self.participant_id)
        # W4 (F4, PLAN-CRITIC.md Auflage 4: "echte Auswahl-Eingabe in n
        # statt nur Anzeige/'bereits abgeschlossen'"): bei bereits
        # registrierten Figuren wird jetzt WIRKLICH gefragt, statt nur
        # read-only aufzulisten und bei `completed` sofort abzubrechen --
        # der Mensch waehlt entweder eine bestehende Figur zum Aktivieren
        # (Chrononaut-ID) oder startet ausdruecklich eine WEITERE
        # Erschaffung ('neu').
        force_new = False
        # r2-Nacharbeit (02_NACHARBEITSAUFTRAG.md §1, 01_UNABHAENGIGE_REVIEW.md
        # §3 BLOCKER "human_fresh_reset"): `onboarding_key` bleibt die
        # UNVERAENDERTE `self.participant_id`-Datei fuer die normale erste
        # Erschaffung/Fortsetzung (Rueckwaertskompatibilitaet, viele
        # bestehende Tests lesen genau diesen Schluessel). NUR fuer eine
        # BEWUSST NEUE Zusatzerschaffung (force_new) bekommt der Dialog eine
        # EIGENE, von `onboarding.bind_attempt` VOR dem ersten Request
        # dauerhaft gebundene Generation -- analog zu `domain.zeitriss.
        # community_creation._additional_onboarding_key` fuer die
        # Persona-Seite. Vorher ersetzte `force_new=True` IMMER denselben
        # Scratch an der UNVERAENDERTEN `self.participant_id`-Datei, WAEHREND
        # der menschliche `creation_dialog` ueber `run_admitted_creation_
        # dialog`s `participant_id` weiterhin an dieselben Requestledger-
        # Operationsfelder (`table_id=None, section_id=None, role=
        # "creation_dialog", turn_idx=0, participant=self.participant_id`)
        # gebunden blieb wie die vorherige Erschaffung -- eine zweite
        # bewusst neue Erschaffung fand darin den laengst abgerechneten
        # ALTEN Save wieder (`request_ledger.find_durable_result`) und
        # publizierte ihn als neue Fertigstellung, wobei der inzwischen
        # erspielte Fortschritt der ersten neuen Figur ueberschrieben wurde.
        onboarding_key = self.participant_id
        fresh_generation: int | None = None
        # E2E-Nacharbeit B1-MENUE (2026-10-02, 02_B1B2_NACHZUG.md §C): eine
        # bereits angenommene, aber nach einem Katalog-/Figursave-I/O-Fehler
        # noch nicht vollstaendig persistierte Zusatzfigur-Erschaffung einer
        # Persona wird HIER sichtbar als EIGENE, von 'neu' GETRENNTE Auswahl
        # angeboten (`domain.zeitriss.community_creation.find_resumable_
        # additional_creation`, reine Lesefunktion) -- 'neu' bleibt
        # unveraendert ein bewusst NEUER, eigener Vorgang (erfordert
        # weiterhin eine eigene Menschenfigur-Erschaffung); 'fortsetzen'
        # erfordert KEINE weitere Menschenfigur und KEINE erneute
        # Einladungsentscheidung -- reiner Nachtrag bereits real erhaltener
        # Savebytes ueber denselben, bereits gebundenen Vorgang (0
        # zusaetzliche SL-/Einladungsaufrufe).
        from ..domain.zeitriss.community_creation import find_resumable_additional_creation
        resumable = find_resumable_additional_creation(self.onboarding_dir)
        if entries:
            active_id = catalog.active_chrononaut_id(self.catalog_dir, self.participant_id)
            self._print("Vorhandene Figuren:")
            for idx, e in enumerate(entries, start=1):
                marker = " (aktiv)" if e.chrononaut_id == active_id else ""
                name = self._effective_display_name(e)
                label = f"{name} " if name else ""
                self._print(f"  [{idx}] {label}{e.chrononaut_id}{marker}")
            prompt = (
                "Nummer oder Name zum Aktivieren eingeben (Chrononaut-ID bleibt als Detailweg "
                "moeglich), oder 'neu' fuer eine weitere Erschaffung"
            )
            if resumable:
                self._print("Offene, bereits angenommene Zusatzfigur-Erschaffung(en) (noch ohne eigenen Save):")
                for r in resumable:
                    self._print(f"  - fortsetzen:{r['persona_key']}")
                prompt += ", oder 'fortsetzen:<persona-id>' fuer eine offene Zusatzfigur"
            # F02 (W18, Brief §Fachvertrag 1): dieser Prompt las vorher roh
            # (`self._readline`) -- '/hilfe'/'/zurueck'/'/abbrechen'/'/pause'
            # etc. gingen dadurch als woertliche Chrononaut-ID/Persona-ID an
            # `_switch_active_figure`/`_resume_additional_persona_creation`
            # (roher W11-Matrixbefund, Zeile 6). Derselbe zentrale Leser wie
            # an jedem anderen Prompt: '?'/'/hilfe'/'/stand'/'/verlauf'
            # werden DORT bereits lokal beantwortet (kein Verlassen dieser
            # Methode, also kein Figurwechsel/Erschaffungs-/Importturn).
            # '/zurueck'/'/abbrechen'/'/pause' kommen hier als `control`
            # zurueck -- eine Steuerzeile loest HIER explizit KEINEN
            # Figurwechsel und KEINEN neuen Erschaffungs-/Importvorgang aus
            # (0 Writes/Calls).
            choice, control = self._readline_with_controls(prompt + ": ", context="Figurwahl")
            if control in ("zurueck", "abbrechen", "pause"):
                self._print(
                    "Lokal verarbeitet -- keine Figurauswahl, kein neuer Erschaffungs-/"
                    "Importvorgang. Bestehende Figuren bleiben unveraendert."
                )
                # W24b (BRIEF-W24b.md Punkt 2): `/zurueck` meldet "eine
                # Ebene zurueck" an den Aufrufer (True) -- `/abbrechen`/
                # `/pause` behalten das bisherige Verhalten (Rueckfall bis
                # zum naechsten eigenstaendigen Aufrufer, i.d.R.
                # Hauptmenue), weil nur Punkt 2 explizit `/zurueck` betrifft.
                return control == "zurueck"
            choice = choice.strip()
            if resumable and choice.lower().split(":", 1)[0] == "fortsetzen":
                self._resume_additional_persona_creation(choice, resumable)
                return False
            if choice and choice.lower() not in ("neu", "n", "new"):
                resolved, selection_error = self._resolve_character_choice(choice, entries)
                if selection_error is not None:
                    self._print(selection_error)
                    return
                self._switch_active_figure(resolved, entries)
                return
            force_new = True
            try:
                fresh_generation = onboarding.bind_attempt(
                    self.onboarding_dir, _human_fresh_attempt_key(self.participant_id),
                    seed_generation=len(entries) + 1,
                )
            except (OSError, ValueError) as e:
                self._print(
                    f"Neue Erschaffung nicht moeglich (Vorgangsbindung fehlgeschlagen: {e}) -- "
                    "HALT vor jedem Modellaufruf, kein Ueberschreiben eines bestehenden Auftrags."
                )
                return
            onboarding_key = _human_fresh_onboarding_key(self.participant_id, fresh_generation)
        state = onboarding.start_or_resume(self.onboarding_dir, onboarding_key)
        if state.status == "completed":
            if fresh_generation is not None:
                # B1-Fix (r2-Nacharbeit 2026-10-02, 04_NAECHSTE_SESSION.md §2):
                # ein frueherer Lauf hat fuer DIESELBE, noch nicht
                # `resolve_attempt`-markierte Generation bereits einen
                # gueltigen Save erhalten (`onboarding.complete_with_save`,
                # unten in `run_admitted_creation_dialog`) -- die
                # Katalogpersistenz/Publikation ist aber NICHT abgeschlossen
                # (sonst waere diese Generation bereits resolviert und
                # `onboarding_key` zeigte auf eine NEUE, noch leere
                # Generation statt auf dieses `completed`-Dokument). Setzt
                # DENSELBEN Vorgang mit den bereits empfangenen Savebytes
                # fort -- KEIN zweiter SL-Request, KEINE zweite neue Figur.
                self._finish_new_character_creation(state.final_save, fresh_generation, force_new)
                return
            self._print(f"Erschaffung bereits abgeschlossen (Save vorhanden fuer {self.participant_id}).")
            return
        if self.run_dir is None or self.gm_transport_factory is None:
            self._print(
                "Neue Erschaffung erfordert eine konfigurierte SL-Anbindung (run_dir + "
                "gm_transport_factory) fuer den echten Erschaffungsdialog — hier nicht "
                "konfiguriert, kein Dialogstart (Live-Setup, s. docs/mmo-sim.md)."
            )
            return
        from ..core.admission import read_admission_block
        blocked, reason = read_admission_block(self.run_dir)
        if blocked:
            self._print(f"Erschaffungsdialog blockiert (Admission-Gate: {reason}) — kein Modellaufruf.")
            return
        import inspect
        try:
            accepts_id = len(inspect.signature(self.gm_transport_factory).parameters) >= 1
        except (TypeError, ValueError):
            accepts_id = False
        onboarding_chat_id = f"onboarding-{self.participant_id}"
        try:
            gm_transport = self.gm_transport_factory(onboarding_chat_id) if accepts_id else self.gm_transport_factory()
        except Exception:
            self._print(self._opaque_boundary_error("Erschaffungsdialog: SL-Anbindung nicht verfuegbar"))
            return
        self._print("Erschaffungsdialog gestartet/fortgesetzt (echter SL-Dialog, fortsetzbar, kein JSON noetig).")
        turn_idx = len(state.steps)
        initial_outgoing = state.steps[-1]["answer"] if state.steps else (
            "Ich moechte einen neuen Chrononauten erschaffen. Fuehre mich Schritt fuer Schritt durch die Erschaffung."
        )

        def _human_get_reply(_turn_idx: int, _sl_text: str) -> ReplyResult:
            # Menschlicher Antwortgeber: kein eigener Modellrequest (wie vor
            # dieser Extraktion) -- `EndOfInput` bei EOF propagiert
            # unveraendert bis `run()` (I2-Kern-Extraktion, s.
            # `core/creation_service.py`-Docstring).
            #
            # Q02 (REVIEW.md R01, 05.10.2026, vormals `:1070-1077`): dieser
            # Prompt las vorher roh (`self._readline`) -- '/hilfe' UND
            # '/abbrechen' gingen dadurch als woertliche Antwort sowohl in
            # den Onboardingzustand (`onboarding.record_step`, ueber
            # `run_admitted_creation_dialog`) ALS AUCH an den synthetischen
            # GM (drei Fake-GM-Aufrufe fuer eine einzige wirkliche Absicht).
            # Derselbe zentrale Leser (`_readline_with_controls`) wie an
            # jedem anderen Prompt: '?'/'/hilfe'/'/stand'/'/verlauf' werden
            # DORT bereits lokal beantwortet (kein Verlassen dieser
            # Methode, also erst recht kein GM-Call). '/zurueck'/
            # '/abbrechen'/'/pause' kommen hier als `control` zurueck und
            # werden NICHT als `kind="answer"` an die SL gesendet --
            # `ReplyResult(kind="paused", ...)` haelt den bereits
            # persistierten Dialogfortschritt unveraendert offen/
            # fortsetzbar (derselbe Vertrag wie ein Admission-Gate-Stop,
            # s. `core/creation_service.ReplyResult`-Docstring), KEIN
            # weiterer SL-/GM-Request fuer diesen Versuch. Literaler Text,
            # der wie eine Steuerzeile aussieht, bleibt ueber das erklaerte
            # fuehrende '\\' eingebbar und erreicht die SL unveraendert als
            # Nutztext (inkl. JSON/Mehrzeilentext, da `_readline_with_
            # controls` nur die GESAMTE getrimmte Zeile vergleicht).
            raw, control = self._readline_with_controls(
                "Deine Antwort: ", context="Erschaffungsantwort",
            )
            if control in ("zurueck", "abbrechen", "pause"):
                self._print(
                    "Lokal verarbeitet -- diese Steuerzeile wird NICHT als Antwort an die SL "
                    "gesendet. Fortschritt bleibt erhalten, spaeter mit 'n'/[charaktere] fortsetzbar."
                )
                return ReplyResult(kind="paused", reason=f"human_local_{control}")
            return ReplyResult(kind="answer", text=raw)

        # I2-Kern-Extraktion (MAIN-DATENWEGENTSCHEIDUNG.md §3, "kleine
        # gemeinsame Erschaffungs-/App-Service-Extraktion"): der GM-Turn-
        # Mechanismus (Admission-Gate FRISCH pro Turn, body-basierte
        # Reservierung, Requestledger-Bindung, v7-Save-Erkennung,
        # `onboarding.complete_with_save`) ist jetzt in
        # `core/creation_service.run_admitted_creation_dialog` -- derselbe
        # Kern, den `domain/zeitriss/community_creation.py` fuer die
        # Persona-getriebene Community-Erstgeneration nutzt (persona-driver
        # ersetzt `_human_get_reply`). Verhalten/Printtexte fuer den
        # menschlichen Pfad bleiben BYTEGLEICH zum vorherigen Inline-Code.
        outcome = run_admitted_creation_dialog(
            run_dir=self.run_dir, onboarding_dir=self.onboarding_dir,
            # r2-Nacharbeit (s. Docstring/Kommentar an der Aufrufstelle oben):
            # `onboarding_key` ist fuer eine bewusst neue Zusatzerschaffung
            # eine EIGENE, dauerhaft gebundene Generation -- NICHT mehr
            # `self.participant_id` -- damit `request_ledger`s
            # Operationsidentitaet (`role="creation_dialog", turn_idx,
            # participant`) zwei verschiedene bewusst neue Erschaffungen
            # NICHT mehr ueber dieselben Requestfelder verwechselt.
            participant_id=onboarding_key, turn_idx_start=turn_idx,
            initial_outgoing=initial_outgoing, gm_transport=gm_transport,
            get_reply=_human_get_reply, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=self._print, role="creation_dialog",
        )
        if outcome.status == "completed":
            self._finish_new_character_creation(outcome.save_block, fresh_generation, force_new)
            return

    def _finish_new_character_creation(
        self, save_block: dict, fresh_generation: int | None, force_new: bool,
    ) -> None:
        """Gemeinsamer Abschluss-/Publikationspfad fuer eine neue
        Erschaffung -- erreicht sowohl von einem GERADE fertig gewordenen
        SL-Dialog (`outcome.save_block`) ALS AUCH von einer Wiederaufnahme
        eines bereits `completed`, aber noch nicht vollstaendig
        publizierten Vorgangs (`state.final_save`, s. Aufrufstelle oben) --
        in BEIDEN Faellen sind das dieselben, bereits einmal real erhaltenen
        Savebytes, NIE ein neuer Modellaufruf.

        B1-Fix (r2-Nacharbeit 2026-10-02, 04_NAECHSTE_SESSION.md §2):
        `onboarding.resolve_attempt` markiert diese Generation ERST NACH
        erfolgreicher Katalogpersistenz (`catalog.register` UND `catalog.
        store_figure_save`) als abgeschlossen -- vorher geschah das VOR
        diesen beiden Writes; ein gewoehnlicher Katalog-I/O-Fehler
        (`OSError`) hinterliess dadurch eine bereits resolvierte Generation
        OHNE durchgefuehrte Persistenz. Der naechste Menue-Reentry ('n' ->
        'neu') bindet dann ueber `bind_attempt` eine NEUE Generation (die
        alte gilt ja als erledigt) und startet einen ZWEITEN echten
        SL-Dialog -- der erste, bereits erhaltene Save (`state.final_save`)
        bleibt fuer immer unregistriert/ungespeichert, eine zweite Figur
        entsteht statt der Fortsetzung der ersten (01_UNABHAENGIGE_REVIEW.md
        B1). Resolve passiert deshalb HIER, NACH beiden Writes, NIE davor.

        B2-Fix (r2-Nacharbeit 2026-10-02, 04_NAECHSTE_SESSION.md §3): BEVOR
        irgendein Katalog-/Current-Write fuer `candidate_char_id` passiert,
        wird geprueft, ob diese ID BEREITS (bei einem BELIEBIGEN Teilnehmer,
        s. `catalog.find_registration`) registriert ist UND dort mit
        ABWEICHENDEN Bytes gespeichert ist -- ein struktureller Save mit
        einer bereits vergebenen/fremden char_id (SL-Fehlverhalten/
        Verwechslung) darf NIE automatisch den bestehenden Stand
        ueberschreiben (sichtbarer kontrollierter Konflikt/HOLD statt
        stillem Ueberschreiben, kein automatischer Zweitrequest, keine
        Konfliktentscheidung ohne Nutzereingabe). Die EIGENE, bereits
        teilregistrierte neue Figur (identische Bytes, aus einem fruehereren
        Teilschritt DIESER Generation, z.B. B1-Resume nach einem
        `store_figure_save`-Fehler mit bereits erfolgreichem `register`)
        bleibt davon klar unterschieden -- deckungsgleiche/noch nicht
        vorhandene Bytes gelten NICHT als Konflikt, nur ein ABWEICHENDER
        bereits gespeicherter Stand haelt an."""
        candidate_char_id = zeitriss_saves.block_char_id(save_block)
        if candidate_char_id is None:
            self._print(
                "Erschaffung nicht abschliessbar: der uebernommene Save enthaelt keine "
                "auswertbare Chrononaut-ID -- kein Katalog-/Current-Write, Vorgang bleibt offen."
            )
            return
        # E2E-Nacharbeit (2026-10-02, 02_B1B2_NACHZUG.md §B/§A): dieselbe
        # reale Aktivitaets-/Current-Autoritaet wird HIER EINMALIG ermittelt
        # und unten (Aktivierungs-/Sperrlogik) WIEDERVERWENDET -- nicht
        # zweimal aufgeloest (derselbe Lesevorgang, s. `_resolve_real_
        # active_chrononaut_id`-Docstring zu I4-Nachzug).
        active_before, active_current, unresolved = self._resolve_real_active_chrononaut_id()
        existing_registration = catalog.find_registration(self.catalog_dir, candidate_char_id)
        if existing_registration is not None:
            if existing_registration.participant_id != self.participant_id:
                # B2-OWNER: bekannte FREMDE Eigentuemerschaft haelt
                # UNABHAENGIG von Save-Inhaltsgleichheit oder einem
                # fehlenden Archivsave -- weder Byte-Gleichheit noch ein
                # fehlender Fremd-Save beweist eine eigene
                # Auftragszugehoerigkeit zu dieser ID.
                self._print(
                    f"Erschaffung angehalten: char_id={candidate_char_id} ist bereits einem "
                    f"anderen Teilnehmer ({existing_registration.participant_id!r}) zugeordnet -- "
                    "kontrollierter Konflikt, kein automatisches Uebernehmen/Umbenennen. Vorgang "
                    "bleibt offen, kein zweiter Modellaufruf."
                )
                return
            # Auftragsbindung-Nachzug (2026-10-02,
            # 02_RESTNACHZUG_AUFTRAGSBINDUNG.md §2, ersetzt die vorherige
            # inhaltsbasierte B2-CURRENT/"abweichend"-Pruefung vollstaendig):
            # eine bestehende EIGENE Registrierung ist NUR dann diesem
            # Aufruf zuzurechnen, wenn `onboarding.attempt_claim_matches`
            # belegt, dass GENAU diese `candidate_char_id` bereits unter
            # GENAU `fresh_generation` beansprucht wurde (derselbe, noch
            # offene -- oder gerade jetzt zum ersten Mal abzuschliessende --
            # Auftrag). Blosse Inhaltsgleichheit mit dem Archiv, ein
            # fehlendes Archiv ODER ein aktiver Katalogzeiger sind KEIN
            # Ersatz dafuer: eine bereits VOLLSTAENDIG abgeschlossene
            # (resolvte) fruehere Generation + ein bewusst NEUER Auftrag
            # (neue Generation), dessen SL zufaellig dieselbe ID/denselben
            # Inhalt liefert, erfuellt `attempt_claim_matches` NICHT (der
            # Claim-Datensatz nennt noch die ALTE Generation) -- HOLD. Ein
            # legitimer B1-Resume (Register lief durch, Figursave/Current-
            # Publikation scheiterte) erfuellt ihn SEHR WOHL, weil
            # `record_attempt_claim` (s.u.) den Claim bereits beim ERSTEN
            # Durchlauf DIESER Generation geschrieben hat, BEVOR
            # irgendein ueberschreibender Write passierte.
            own_claim_ok = fresh_generation is not None and onboarding.attempt_claim_matches(
                self.onboarding_dir, _human_fresh_attempt_key(self.participant_id),
                generation=fresh_generation, char_id=candidate_char_id,
            )
            if not own_claim_ok:
                self._print(
                    f"Erschaffung angehalten: char_id={candidate_char_id} gehoert nicht nachweislich "
                    "zu diesem offenen Erschaffungsauftrag (bereits vorhandene eigene Registrierung "
                    "ohne passende Auftragsbindung -- gleicher Teilnehmer, gleicher Inhalt oder ein "
                    "fehlendes Archiv beweisen keine Zugehoerigkeit) -- kontrollierter Konflikt, kein "
                    "automatischer Erfolg. Vorgang bleibt offen, kein zweiter Modellaufruf."
                )
                return
        if fresh_generation is not None:
            # Auftragsbindung JETZT dauerhaft festhalten -- VOR dem ersten
            # ueberschreibenden Write unten (Register/Figursave/Current).
            # Idempotent bei Reentry derselben Generation/ID (I/O-Fehler
            # zwischen hier und `resolve_attempt`, s. B1-Fix-Docstring).
            onboarding.record_attempt_claim(
                self.onboarding_dir, _human_fresh_attempt_key(self.participant_id),
                generation=fresh_generation, char_id=candidate_char_id,
            )
        # G1-Fix (Nacharbeit 2026-10-03, REWORK-BRIEF.md G1): Persona-Paritaet
        # (`community_creation.py:1016`, `has_figure_save`) -- der EIGENE
        # Figuren-Archivsave fuer `candidate_char_id` (falls vorhanden) wird
        # HIER EINMALIG geladen, VOR jedem Katalog-Write, und unten (statt
        # eines unbedingten Writes) zum Schutz vor einem Wiederaufnahme-
        # Rueckfall genutzt. IA-1-Nachzug (Nacharbeit 2026-10-03,
        # BRIEF-IA1.md): derselbe geladene Wert (`own_archive_before`, NICHT
        # nur sein Vorhandensein) wird WEITER UNTEN zusaetzlich fuer den
        # Ziel-Archiv-Inhaltsvergleich (IA-1-Guard) wiederverwendet -- kein
        # zweiter Lesevorgang noetig.
        own_archive_before = catalog.load_figure_save(
            self.catalog_dir, self.participant_id, candidate_char_id,
        )
        has_figure_save = own_archive_before is not None
        # R05-Restintegrationsfix (WEGKARTE §4, REVIEW-P2R.md R-A):
        # derselbe autoritative Fertigstellungsweg wie `_cmd_import`
        # -- ein akzeptierter Save fuehrt NICHT nur zu einem
        # Onboarding-/Katalogeintrag, sondern auch zur echten
        # Persona-State-/Current-Save-Publikation, ohne die eine
        # als 'tischbereit' gemeldete Figur keinen Folgeabschnitt
        # abschliessen kann (Test 05).
        # A21 (WEGKARTE §8, 11 §6): Katalogregistrierung, s. `_cmd_import`.
        catalog.register(self.catalog_dir, catalog.CatalogEntry(
            participant_id=self.participant_id, chrononaut_id=candidate_char_id,
            persona_key=self.participant_id,
        ))
        # W4 (F4, Test 07): eigene, dauerhafte Savebytes JEDER
        # registrierten Figur -- unabhaengig davon, ob diese neue
        # Erschaffung gerade aktiv wird oder (bei gesperrter
        # aktiver Figur) inaktiv registriert bleibt.
        # G1-Fix (REWORK-BRIEF.md G1): NUR schreiben, wenn noch KEIN eigenes
        # Archiv existiert -- exakt die Persona-Paritaet
        # (`community_creation.py:1035`, `if not has_figure_save:`). Der
        # vorher UNBEDINGTE Write ueberschrieb bei einem zweiten Resume
        # derselben offenen Generation ein inzwischen (z.B. durch
        # switch-away) fortgeschrittenes eigenes Archiv transient mit dem
        # alten `save_block` (Current blieb dabei korrekt geschuetzt, s.
        # CC-1-Guard unten -- nur das Archiv fiel zurueck). B1-Resume nach
        # store-Fehler (Archiv ABSENT, weil `register` lief, `store_figure_
        # save` aber vorher scheiterte) schreibt weiterhin -- `has_figure_
        # save` ist dort `False` -- ebenso die Erst-Erschaffung (Test 07/W4,
        # kein Archiv vorhanden).
        if not has_figure_save:
            catalog.store_figure_save(self.catalog_dir, self.participant_id, candidate_char_id, save_block)
        # CC-1-Fix (02_CLAIM_CURRENT_NACHZUG.md, UNABHAENGIGER Current-/
        # Standautoritaets-Schutz ZUSAETZLICH zum Claim-Gate oben): das
        # Auftragsbindung-Claim-Gate oben beweist nur, dass `candidate_
        # char_id` zu DIESEM offenen Erschaffungsauftrag gehoert -- es
        # beweist NICHT, dass `save_block` (der hier zu publizierende
        # Erstsave) noch der aktuelle Stand dieser Figur ist. Ein Resume
        # DERSELBEN, bereits aktiven Figur (`active_before ==
        # candidate_char_id`) ueberspringt den weiter unten folgenden
        # `locked`-Block UND `_sync_outgoing_active_figure` (No-op bei
        # gleicher ID) -- ohne diesen zusaetzlichen, vom Claim UNABHAENGIGEN
        # Inhaltsvergleich gegen den real geladenen `active_current` wuerde
        # ein inzwischen real fortgeschrittener Stand hier stillschweigend
        # auf den Erstsave zurueckgesetzt. Bei Abweichung: fail-closed HOLD
        # (nicht publizieren, Current bleibt erhalten, kein zweiter Modell-/
        # Einladungsaufruf). Bei Gleichheit (echter idempotenter
        # Teilabschluss): normal fertigstellen, keine maskierte No-op-
        # Loesung.
        #
        # IA-1-Nachzug (BRIEF-IA1.md, ehrlicher Abschlussstatus): dieser
        # Guard UND der neue IA-1-Guard direkt darunter sitzen jetzt
        # ABSICHTLICH VOR `onboarding.resolve_attempt` (vorher direkt nach
        # `store_figure_save`, s. B1-Fix-Docstring oben) -- ein HOLD hier
        # darf die Generation NICHT als erledigt markieren (vorher: Meldung
        # sagte "Vorgang bleibt offen", `resolved` war aber bereits `true`,
        # ein klarer Widerspruch). `unresolved`/`locked` WEITER UNTEN bleiben
        # UNVERAENDERT vor `resolve_attempt` erreichbar -- das sind keine
        # Inhaltskonflikte, sondern bereits abgeschlossene (nur inaktive)
        # Registrierungen, deren `resolved=true` unveraendert korrekt bleibt.
        if (
            active_current is not None
            and zeitriss_saves.block_char_id(active_current) == candidate_char_id
            and active_current != save_block
        ):
            self._print(
                f"Erschaffung angehalten: char_id={candidate_char_id} hat bereits einen abweichenden, "
                "spaeter erspielten aktuellen Spielstand -- kontrollierter Konflikt, kein automatisches "
                "Ueberschreiben. Vorgang bleibt offen, kein zweiter Modellaufruf."
            )
            return
        # IA-1-Fix (BRIEF-IA1.md, archiv-resume-nachzug): CC-1 oben greift
        # NUR, wenn `candidate_char_id` SELBST die aktuell aktive Figur ist
        # -- bei einem normalen Wegwechsel (eine ANDERE Figur ist aktiv)
        # gehoert `active_current` nicht `candidate_char_id`, CC-1 feuert
        # nicht. Ein Claim beweist nur Auftragseigentum, ein vorhandenes
        # Archiv (G1) nur dessen Existenz -- KEINES der beiden beweist, dass
        # `save_block` noch der aktuelle Stand DIESER (dann inaktiven)
        # Figur ist. Deshalb HIER ein vom Claim/von CC-1/G1 UNABHAENGIGER
        # Ziel-Archiv-Inhaltsvergleich: existiert `own_archive_before`
        # (derselbe oben bereits geladene Wert) UND weicht er inhaltlich von
        # `save_block` ab (die Figur ist also, UNABHAENGIG davon, welche
        # ANDERE Figur gerade aktiv ist, selbst bereits fortgeschritten) ->
        # fail-closed HOLD: NICHT aktivieren/publizieren, Archiv UND Current
        # bleiben unberuehrt, kein zweiter Modell-/Einladungsaufruf. Erst-
        # Erschaffung (kein Archiv) und B1-Resume-nach-store-Fehler (Archiv
        # ABSENT) sowie ein echter idempotenter Teilabschluss (Archiv ==
        # save_block) sind davon unberuehrt (`own_archive_before is None`
        # bzw. `== save_block`) und laufen normal durch. Kein Level-
        # Heuristik/Merge/Downgrade.
        if own_archive_before is not None and own_archive_before != save_block:
            self._print(
                f"Erschaffung angehalten: char_id={candidate_char_id} hat bereits ein abweichendes, "
                "eigenes, fortgeschrittenes Figuren-Archiv -- kontrollierter Konflikt, kein "
                "automatisches Ueberschreiben. Vorgang bleibt offen, kein zweiter Modellaufruf."
            )
            return
        # B1-Fix (s. Docstring oben): ERST JETZT, NACH erfolgreicher
        # Katalogpersistenz UND NACH den beiden obigen Inhaltskonflikt-
        # Guards (CC-1/IA-1, s. deren Kommentare), gilt diese Generation
        # fuer `bind_attempt` als abgeschlossen -- die NAECHSTE bewusst neue
        # Erschaffung bekommt eine WEITERE, neue Generation (kein
        # Wiederaufnehmen dieses jetzt fertigen Vorgangs). Nur fuer den
        # force_new-Pfad gebunden (fresh_generation is None sonst).
        if fresh_generation is not None:
            onboarding.resolve_attempt(
                self.onboarding_dir, _human_fresh_attempt_key(self.participant_id), fresh_generation,
            )
        # I4 Luecke 2 (02_ABNAHME_I4 Weg 2, Vertrag §3 B): die REALE
        # Bindung der BISHERIGEN aktiven Figur wird HIER geprueft --
        # VOR jeder Current-/State-Publikation. Vorher wurde
        # UNBEDINGT publiziert (Zeile unten lief immer zuerst) und
        # erst danach `bind_for_section(..., has_open_section=False)`
        # aufgerufen -- ein Literal, das NIE `True` wurde und die
        # eigene Schutzlogik von `bind_for_section` strukturell
        # umging: eine neue Figur ersetzte damit eine tischgebundene
        # aktive Figur als Current, obwohl deren Abschnitt/
        # Abschlussauftrag offen blieb (`has_open_section=False` ist
        # KEIN Ersatz fuer die echte Autoritaetspruefung, Vertrag §3
        # B).
        #
        # I4-Nachzug (Vertrag §3 A/T1b): 'aktive Figur' wurde bereits OBEN
        # (E2E-Nacharbeit, vor der Identitaetspruefung) ueber `_resolve_
        # real_active_chrononaut_id` bestimmt (reale Current-Fassung, NICHT
        # der ggf. veraltete `catalog.active_chrononaut_id`-Zeiger) und wird
        # hier WIEDERVERWENDET (`active_before`/`active_current`/
        # `unresolved`, derselbe Lesevorgang -- kein zweiter Aufruf noetig).
        if unresolved:
            self._print(
                f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Der Spielstand der "
                "bisherigen aktiven Figur ist gerade nicht lesbar -- neue Figur bleibt INAKTIV "
                "registriert (Savebytes gesichert), kein Aktivwechsel ohne geklaerte Autoritaet."
            )
            return
        locked = False
        if self.run_dir is not None and active_before is not None and active_before != candidate_char_id:
            from ..core import store as core_store
            locked = (
                core_store.chrononaut_active_binding(self.run_dir, active_before)
                or core_store.chrononaut_open_completion_order(self.run_dir, active_before)
            )
        if locked:
            self._print(
                f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Aktive Figur '{active_before}' hat einen "
                "offenen Abschnitt/Abschlussauftrag -- neue Figur bleibt INAKTIV registriert (Savebytes gesichert)."
            )
            return
        # I4 Luecke 1 (s. `_sync_outgoing_active_figure`): die
        # bisherige aktive Figur (falls vorhanden und ungebunden)
        # wird VOR dem Ueberschreiben von Current mit ihrem zuletzt
        # real veroeffentlichten Stand im Katalog gesichert.
        self._sync_outgoing_active_figure(candidate_char_id, active_before, active_current)
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            onboarding.ensure_participant_persona_state(
                ps_store, self.states_dir, self.participant_id, candidate_char_id, save_block,
            )
            core_store.publish_current_save(
                self.run_dir, self.participant_id, save_block, ps_store, self.states_dir,
            )
        try:
            catalog.bind_for_section(self.catalog_dir, self.participant_id, candidate_char_id, has_open_section=False)
        except catalog.ActiveBindingError:
            # Defensiv: der reale Sperr-Check oben haette diesen Fall
            # bereits per fruehem `return` abgefangen (kein
            # Doppelpfad, analog `_switch_active_figure`).
            self._print(
                f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Aktive Figur hat einen "
                "offenen Abschnitt -- neue Figur bleibt INAKTIV registriert (Savebytes gesichert)."
            )
            return
        self._print(f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Figur ist jetzt tischbereit.")
        # Gate B (02_PERSONA_NEUER_CHRONONAUT.md Zielfall, Terminal-
        # Bestand/Neustart-Auftrag 2026-10-02): genau an DIESER Stelle --
        # der Mensch hat soeben bewusst eine ZUSAETZLICHE eigene Figur
        # gewaehlt (force_new, s.o.) -- bietet die Gelegenheit, eine
        # bekannte Persona zu demselben gemeinsamen Frischstart
        # einzuladen (01_AUFTRAG §Gate B: "Ein bewusst gestarteter
        # Wunsch an die ausgewaehlte Persona ... reicht. Keine
        # automatische Nachfrage an die ganze Community"). Nur fuer den
        # force_new-Fall (nicht fuer eine blosse Figuraktivierung) --
        # `_invite_persona_fresh_start` selbst bleibt No-op ohne
        # konfigurierte Laufumgebung.
        if force_new:
            self._invite_persona_fresh_start()
        return

    # R5-Sicherheitsnachzug (01_SICHERHEITSNACHZUG.md Nachtrag, 2026-10-06,
    # Befund "sichtbares IA-1-HOLD erwartet"): `status == "blocked"` wird in
    # `community_creation.py` fuer MEHRERE, verschiedene, intern-authored
    # (vertrauenswuerdige) Gruende verwendet (Archiv-HOLD, abweichender
    # Current-Stand, Current-Autoritaet unlesbar, Claim-Mismatch,
    # Fremd-Owner, fehlende Chrononaut-ID, Admission-Gate). Jede dieser
    # Ankerphrasen ist eine mehrwortige, mit dem jeweiligen `reason`-Text in
    # `community_creation.py` exakt uebereinstimmende Teilzeile (nur dort
    # gelesen, nie geaendert) -- ein blosses Vorkommen von "Archiv"/
    # "blocked"/"Admission" als Einzelwort reicht NICHT zur Klassifikation
    # (s. `_redact_creation_status_text` unten). Die Admission-Gate-Gruende
    # selbst (`core.admission.read_admission_block`) sind heterogen und
    # matchen keine dieser Ankerphrasen -- sie fallen bewusst auf den
    # bisherigen Default-Text in `known["blocked"]` durch.
    _BLOCKED_REASON_ANCHORS = (
        (
            "fortgeschrittenes Figuren-Archiv",
            "geschuetztes eigenes, fortgeschrittenes Figuren-Archiv -- Vorgang "
            "offen, kein automatisches Ueberschreiben/Neuerstellen, Fortschritt "
            "bleibt erhalten, spaeter fortsetzbar.",
        ),
        (
            "spaeter erspielten aktuellen Spielstand",
            "abweichender, spaeter erspielter aktueller Spielstand -- Vorgang "
            "offen, kein automatisches Ueberschreiben, Fortschritt bleibt "
            "erhalten, spaeter fortsetzbar.",
        ),
        (
            "nicht strengt lesbar",
            "Current-Save-Autoritaet gerade nicht sicher lesbar -- Vorgang "
            "offen, keine Aktivierung/Publikation ohne geklaerten Stand, "
            "spaeter fortsetzbar.",
        ),
        (
            "nicht nachweislich zu diesem offenen Zusatzfigur-Auftrag",
            "Zugehoerigkeit zu diesem offenen Zusatzfigur-Auftrag nicht "
            "nachweisbar -- kontrollierter Konflikt, kein automatischer "
            "Erfolg, Vorgang bleibt offen, spaeter fortsetzbar.",
        ),
        (
            "ist bereits einem anderen Teilnehmer",
            "Figur ist bereits einem anderen Teilnehmer zugeordnet -- "
            "kontrollierter Konflikt, kein automatisches Uebernehmen/"
            "Umbenennen, Vorgang bleibt offen, spaeter fortsetzbar.",
        ),
        (
            "auswertbare Chrononaut-ID im final_save",
            "abgeschlossener Auftrag ohne auswertbare Chrononaut-ID -- "
            "Vorgang offen, spaeter fortsetzbar.",
        ),
    )

    def _redact_creation_status_text(self, status: str, reason: object = None) -> str:
        """R4-Sicherheitsnachzug (01_SICHERHEITSNACHZUG.md, 2026-10-05,
        Review-Befund M01/R3P01/R3P02), R5-Nachtrag (2026-10-06, sichtbares
        IA-1-HOLD): reiner Fehlertext-Formatter fuer die beiden Zusatzfigur-
        Druckpunkte unten -- ersetzt ein rohes `outcome.reason` (kann eine
        fremde Transport-/Exception-/Validierungsdetailzeile aus
        `core/creation_service.py` bzw. `domain/zeitriss/
        community_creation.py` enthalten) durch eine verstaendliche, eng an
        den tatsaechlichen internen Status gebundene Textzeile. Bekannte
        Statuswerte werden eng abgebildet; ein unbekannter Statuswert wird
        NICHT blind interpoliert, sondern bekommt denselben neutralen Text
        wie der zusammengefuehrte Outcome-Druckpunkt (01 §Textanforderungen):
        Vorgang fehlgeschlagen, Fortschritt bleibt erhalten, kein
        automatischer weiterer Versuch, moegliche bereits entstandene
        Wirkung/Kosten nicht ausgeschlossen.

        R5-Nachtrag: NUR fuer `status == "blocked"` wird `reason`
        zusaetzlich gegen `_BLOCKED_REASON_ANCHORS` geprueft (mehrwortige,
        eindeutige Ankerphrasen, die exakt den intern-authored Gruenden in
        `community_creation.py` entsprechen) -- matcht eine Ankerphrase,
        wird die zugehoerige feste, eigene, sichere Kategorietextzeile
        zurueckgegeben (z.B. die Archiv-HOLD-Zeile mit dem Wort "Archiv").
        Matcht keine, faellt `status == "blocked"` auf den unveraenderten
        Admission-Gate-Default-Text zurueck. `status == "error"` (dessen
        `reason` eine fremde Exception-/Transport-/Validierungsdetailzeile
        ODER ein kuenstlich mit "Archiv" praeparierter Text sein kann) wird
        NIE gegen diese Ankerphrasen geprueft -- immer derselbe neutrale,
        redigierte Text, nie Kategorie, nie Echo. Kein roher `reason`-
        Durchlass, keine Secret-Blacklist, keine Core-Abhaengigkeit -- reine
        lokale Textzuordnung, keine Entscheidungs-/Navigations-/
        Persistenzlogik."""
        if status == "blocked" and reason is not None:
            reason_text = str(reason)
            for anchor, category_text in self._BLOCKED_REASON_ANCHORS:
                if anchor in reason_text:
                    return category_text
        known = {
            "blocked": (
                "Admission-Gate blockiert -- kein Modellaufruf, Fortschritt "
                "bleibt erhalten, spaeter fortsetzbar."
            ),
            "no_driver": (
                "keine konfigurierte SL-/Persona-Anbindung -- kein Modellaufruf, "
                "Fortschritt bleibt erhalten, spaeter fortsetzbar."
            ),
            "paused": "Vorgang pausiert -- Fortschritt bleibt erhalten, spaeter fortsetzbar.",
            "error": (
                "Anbindung/Vorgang fehlgeschlagen, Fortschritt bleibt erhalten, kein "
                "automatischer weiterer Versuch. Moegliche bereits entstandene "
                "Wirkung/Kosten nicht ausgeschlossen."
            ),
        }
        return known.get(
            status,
            (
                "Vorgang fehlgeschlagen, Fortschritt bleibt erhalten, kein "
                "automatischer weiterer Versuch. Moegliche bereits entstandene "
                "Wirkung/Kosten nicht ausgeschlossen."
            ),
        )

    def _invite_persona_fresh_start(self) -> None:
        """Gate B (02_PERSONA_NEUER_CHRONONAUT.md Zielfall, Terminal-
        Bestand/Neustart-Auftrag 2026-10-02): nach der soeben gewaehlten
        ZUSAETZLICHEN eigenen Figur (s. Aufrufstelle oben) kann der Mensch
        eine bekannte, bereits spielende KI-Persona einladen, EBENFALLS
        einen ZUSAETZLICHEN eigenen Chrononauten zu erschaffen, damit beide
        gemeinsam auf Level 1 frisch beginnen koennen. Freiwilligkeit (02
        verbindlich): die Persona kann zustimmen, ablehnen oder pausieren
        (echter Entscheidungsvertrag ueber `core.lobby_service.request_
        admitted_decision`, DERSELBE Vertrag wie eine Tischeinladung in
        `_cmd_local_round` -- kein erfundenes Accept, kein verdeckter
        Ersatz durch eine andere Persona). Eine Ablehnung/Pause/Blockade
        erzeugt KEINE neue Figur -- ihre alte Figur, die Community/das
        Roster und alle fremden Personadaten bleiben vollstaendig
        unveraendert; der hoehere, bestehende Einladungs-/Importweg
        (`_cmd_local_round`, `_cmd_import`) bleibt ein unveraenderter,
        zulaessiger Alternativweg.

        Reine Gelegenheit, kein Erschaffungsdialog/keine Zustimmung
        vorwegnehmend (01_AUFTRAG §Gate B): nur EINE ausdruecklich benannte
        Persona wird gefragt, keine automatische Vollgruppen-/Community-
        Nachfrage. Ohne konfigurierte Laufumgebung/SL-/Persona-Anbindung
        bleibt dies ein stiller No-op (dieselbe ehrliche Teilstandsregel
        wie der uebrige Erschaffungsdialog, kein Stub-Erfolg)."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            return
        if self.gm_transport_factory is None or self.persona_driver_factory is None:
            return
        # F02 (W18, Brief §Fachvertrag 2): dieser Prompt las vorher roh
        # (`self._readline`) -- '/hilfe' etc. gingen dadurch als woertliche
        # Persona-ID in den Einladungs-/Katalogabgleich unten. Derselbe
        # zentrale Leser wie an jedem anderen Prompt: '?'/'/hilfe'/'/stand'/
        # '/verlauf' werden DORT bereits lokal beantwortet; '/zurueck'/
        # '/abbrechen'/'/pause' kommen hier als `control` zurueck -- eine
        # Steuerzeile spricht HIER explizit KEINE Einladung aus (kein
        # Modellaufruf, 0 Calls). Der Formatter/Outcome-Druck dieser
        # Funktion bleibt unveraendert W17-fix, nur diese EINGABE-Zeile
        # wird hier gebunden.
        try:
            persona_key, control = self._readline_with_controls(
                "Bekannte Persona zu einem gemeinsamen Frischstart einladen "
                "(Persona-ID, leer = nein): ",
                context="Frischstart-Einladung",
            )
        except EndOfInput:
            self._print("\nEinladung zum gemeinsamen Frischstart abgebrochen (EOF) -- keine Aenderung.")
            return
        if control in ("zurueck", "abbrechen", "pause"):
            self._print(
                "Lokal verarbeitet -- keine Einladung ausgesprochen, kein Modellaufruf, keine Aenderung."
            )
            return
        persona_key = persona_key.strip()
        if not persona_key or persona_key == self.participant_id:
            return
        entries = catalog.list_for_participant(self.catalog_dir, persona_key)
        if not entries:
            self._print(
                f"'{persona_key}' hat noch keine bestehende Figur -- kein Zusatzfigur-Fall "
                "(regulaere Erschaffung/Einladung ueber [c]/[l], kein Frischstart-Spezialweg noetig)."
            )
            return

        from ..adapters.base import decision_contract_instruction, interpret_decision_contract
        from ..core import lobby_service
        from ..domain.zeitriss.community_creation import advance_additional_persona_creation

        # r2-Nacharbeit (02_NACHARBEITSAUFTRAG.md §2, 01_UNABHAENGIGE_REVIEW.md
        # §4 BLOCKER "audit_loss_reuses_accept"): `role`+`participant` allein
        # identifizieren eine Operation NICHT eindeutig ueber die gesamte
        # Laufzeit von `run_dir` hinweg -- eine SPAETERE, inhaltlich
        # unabhaengige Einladung an dieselbe, bereits bekannte Persona (vom
        # Produkt selbst als Regelfall vorgesehen) wuerde sonst faelschlich
        # die laengst abgeschlossene Alt-Antwort ueber `find_durable_result`
        # wiederverwenden, OHNE die Persona fuer DIESE Gelegenheit real zu
        # fragen (Freiwilligkeitsverstoss). Die FRUEHERE Nacharbeit (End-Critic
        # 2026-10-02, Finding 1) band dafuer einen wachsenden, aus der
        # bereits vorhandenen Logzeilenzahl (`lobby_service.read_offer_log`)
        # abgeleiteten Bestandteil an offer_id/section_id -- DIESES Log ist
        # aber ausdruecklich best-effort-Audit (`append_offer_log_record`
        # faengt `OSError` bewusst ab, s. dort). Ein fehlschlagender
        # Audit-Append liess den Zaehler stehen bleiben: die naechste,
        # inhaltlich unabhaengige Gelegenheit bekam DIESELBE offer_id/
        # section_id wie die bereits abgeschlossene vorherige und
        # `find_durable_result` reichte deren laengst erteilte Zustimmung
        # unveraendert weiter, OHNE `driver.decide()` fuer die neue
        # Gelegenheit je aufzurufen.
        #
        # `onboarding.bind_attempt` bindet die Generation dieser Einladungs-
        # GELEGENHEIT jetzt GETRENNT von Auditzeilen/Kataloganzahl, VOR dem
        # ersten Modellaufruf, durabel (kein best-effort-Write) -- ein
        # Schreib-/Zuordnungsfehler HIER haelt kontrolliert an (s.u.), statt
        # ueber einen Zaehler/eine UUID hinwegzuspringen. Eine bereits
        # resolvierte (abgeschlossene) Generation fuer dieselbe (Mensch,
        # Persona)-Paarung erhaelt beim naechsten Aufruf automatisch eine
        # NEUE Generation; eine NOCH NICHT resolvierte (z.B. nach einem
        # Transportfehler/Admission-Block) wird unveraendert WIEDERAUFGENOMMEN
        # (dieselbe offer_id/section_id, derselbe bereits erhaltene Entscheid
        # ueber `find_durable_result` -- kein Doppelrequest).
        # `invite_generation` bindet NUR die Identitaet der Einladungs-
        # GELEGENHEIT selbst (offer_id/section_id/Resolve-Lifecycle) -- die
        # davon GETRENNTE Erschaffungs-`generation` fuer `advance_additional_
        # persona_creation` (unten, nach `accept`) bleibt unveraendert aus der
        # tatsaechlichen Kataloganzahl abgeleitet (wie vor dieser Nacharbeit):
        # eine abgelehnte/pausierte Gelegenheit verbraucht dadurch KEINE
        # Erschaffungs-Generation, die eine spaeter tatsaechlich angenommene
        # Gelegenheit fuer dieselbe Persona dann uebersehen oder ueberspringen
        # wuerde.
        try:
            invite_generation = onboarding.bind_attempt(
                self.onboarding_dir, _fresh_start_invite_attempt_key(self.participant_id, persona_key),
                seed_generation=len(entries) + 1,
            )
        except (OSError, ValueError) as e:
            self._print(
                f"Einladung an '{persona_key}' nicht moeglich (Vorgangsbindung fehlgeschlagen: {e}) -- "
                "HALT vor jedem Modellaufruf, keine Zustimmung angefordert/wiederverwendet."
            )
            return
        offer_id = f"fresh-start-invite-{persona_key}-{self.participant_id}-{invite_generation}"
        ctx = {
            "system": self._own_system_context(persona_key),
            "user": (
                f"'{self.participant_id}' hat gerade selbst eine ZUSAETZLICHE eigene Figur "
                "erschaffen und moechte gemeinsam mit dir frisch auf Level 1 beginnen. Du bist "
                "frei, dies anzunehmen, abzulehnen oder zu pausieren -- deine bisherige Figur "
                "bleibt in jedem Fall unveraendert und spielbereit.\n"
                + decision_contract_instruction(offer_id, persona_key)
            ),
            "decision_contract": {"offer_id": offer_id, "participant_id": persona_key},
        }
        self._append_invitation_log({
            "type": "offer", "offer_id": offer_id,
            "ts": datetime.datetime.now().isoformat(),
            "from": self.participant_id, "wants": [persona_key], "kind": "fresh_start_invite",
        })
        # G05/P06 (General-Befund 'P06_RAW_FACTORY_DETAIL_EXPOSED'): dieser
        # Factory-Aufruf stand vorher VOR jedem schuetzenden `try` -- eine
        # fehlende/fehlerhafte Persona-Konfiguration konnte hier ungefangen
        # durchschlagen (moeglicher Python-Traceback statt einer ruhigen
        # Textzeile). Jetzt derselbe kontrollierte, redigierte Rueckweg wie
        # bei KI-Leader/Gast-Einladung.
        try:
            driver = self.persona_driver_factory(persona_key)
        except Exception:
            self._print(self._opaque_boundary_error(f"Einladung an '{persona_key}' zum gemeinsamen Frischstart nicht moeglich"))
            return
        try:
            decision, block_reason = lobby_service.request_admitted_decision(
                self.run_dir, driver, ctx, role="fresh_start_invite", participant=persona_key,
                section_id=f"fresh-start-{persona_key}-{self.participant_id}-{invite_generation}",
            )
        except Exception:  # Transportfehler -- kein Auto-Accept, Gelegenheit bleibt offen/resumierbar.
            self._print(self._opaque_boundary_error(
                f"Einladung an '{persona_key}' zum gemeinsamen Frischstart nicht zustande gekommen",
                attempted=True,
            ))
            return
        if decision is None:
            # Admission-Gate blockiert -- Gelegenheit bleibt ABSICHTLICH offen
            # (kein `resolve_attempt`): ein spaeterer Aufruf bekommt dieselbe
            # Generation/offer_id und damit denselben, bereits begonnenen
            # Vorgang zurueck, statt einen neuen zu beginnen oder die
            # Blockade zu ueberspringen.
            self._print(f"Einladung an '{persona_key}' blockiert (Admission-Gate: {block_reason}) — kein Modellaufruf.")
            return
        if decision.decision in ("accept", "reject"):
            decision_kind = decision.decision
        else:
            decision_kind, _explanation = interpret_decision_contract(
                decision.text, offer_id=offer_id, participant_id=persona_key,
            )
        self._append_invitation_log({
            "type": "response", "offer_id": offer_id,
            "ts": datetime.datetime.now().isoformat(),
            "from": persona_key, "decision": decision_kind, "origin_source": decision.origin_source,
        })
        # Eine tatsaechliche Entscheidung (accept ODER reject) liegt jetzt
        # vor -- diese Gelegenheit ist abgeschlossen (resolved), GETRENNT
        # vom (weiterhin best-effort) Auditlog oben. Der NAECHSTE Aufruf
        # fuer dieselbe (Mensch, Persona)-Paarung bekommt dadurch eine neue
        # Generation statt diese bereits entschiedene Gelegenheit erneut
        # anzutreffen.
        onboarding.resolve_attempt(
            self.onboarding_dir, _fresh_start_invite_attempt_key(self.participant_id, persona_key), invite_generation,
        )
        if decision_kind != "accept":
            self._print(
                f"'{persona_key}' hat die Einladung zum gemeinsamen Frischstart nicht angenommen "
                f"(Entscheidung: {decision_kind}) -- ihre alte Figur bleibt unveraendert, keine neue Figur."
            )
            return
        community_id = f"community-{self.participant_id}"
        generation = len(entries) + 1
        outcome = advance_additional_persona_creation(
            run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
            onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
            community_id=community_id, generation=generation, persona_key=persona_key,
            gm_transport_factory=self.gm_transport_factory, persona_driver_factory=self.persona_driver_factory,
            print_fn=self._print,
        )
        if outcome.status in ("completed", "already_ready"):
            self._print(
                f"'{persona_key}' hat ihre Zusatzfigur erschaffen: char_id={outcome.chrononaut_id}. "
                f"{outcome.reason or 'Figur ist tischbereit.'}"
            )
        else:
            self._print(
                f"'{persona_key}': Zusatzfigur-Erschaffung {outcome.status} -- "
                f"{self._redact_creation_status_text(outcome.status, outcome.reason)}"
            )

    def _resume_additional_persona_creation(self, choice: str, resumable: list[dict]) -> None:
        """E2E-Nacharbeit B1-MENUE (2026-10-02, 02_B1B2_NACHZUG.md §C):
        Gegenstueck zu `_invite_persona_fresh_start` fuer den Fall, dass
        eine Persona eine Einladung bereits ANGENOMMEN hat und ihre eigene
        Zusatzfigur-Erschaffung bereits vollstaendig DURCHGEFUEHRT wurde
        (`advance_additional_persona_creation`s SL-Dialog ist `completed`),
        aber die anschliessende Katalogpersistenz nach einem gewoehnlichen
        `register`/`store_figure_save`-I/O-Fehler noch offen ist (s.
        `community_creation.find_resumable_additional_creation`).

        Ruft `advance_additional_persona_creation` mit DERSELBEN, bereits
        gebundenen `generation` erneut auf -- die Funktion selbst erkennt
        `state.status == "completed"` und holt NUR die Katalogpersistenz
        nach (`_publication_reconcile_additional`), OHNE jeden neuen SL-
        Turn. KEINE erneute Einladungsentscheidung (Freiwilligkeit wurde
        bereits bei der urspruenglichen Annahme real eingeholt -- dies ist
        reiner Nachtrag bereits vorliegender Bytes, kein neues Angebot,
        kein Consent-Autofill fuer eine ANDERE/neue Gelegenheit). 'neu'
        bleibt davon unberuehrt ein getrennter, bewusst neuer Vorgang."""
        parts = choice.split(":", 1)
        requested_persona_key = parts[1].strip() if len(parts) == 2 and parts[1].strip() else None
        if requested_persona_key is None:
            if len(resumable) == 1:
                requested_persona_key = resumable[0]["persona_key"]
            else:
                self._print(
                    "Mehrere offene Zusatzfigur-Vorgaenge -- bitte 'fortsetzen:<persona-id>' angeben: "
                    + ", ".join(sorted(r["persona_key"] for r in resumable))
                )
                return
        match = next((r for r in resumable if r["persona_key"] == requested_persona_key), None)
        if match is None:
            self._print(f"Kein offener Zusatzfigur-Vorgang fuer '{requested_persona_key}' gefunden -- keine Aenderung.")
            return
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            self._print("Fortsetzen erfordert eine konfigurierte Laufumgebung (run_dir/states_dir/schema_path).")
            return
        from ..domain.zeitriss.community_creation import advance_additional_persona_creation
        outcome = advance_additional_persona_creation(
            run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
            onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
            community_id=f"community-{self.participant_id}", generation=match["generation"],
            persona_key=requested_persona_key,
            gm_transport_factory=self.gm_transport_factory, persona_driver_factory=self.persona_driver_factory,
            print_fn=self._print,
        )
        if outcome.status in ("completed", "already_ready"):
            self._print(
                f"'{requested_persona_key}' Zusatzfigur-Erschaffung fortgesetzt: char_id={outcome.chrononaut_id}. "
                f"{outcome.reason or 'Figur ist jetzt tischbereit.'}"
            )
        else:
            self._print(
                f"'{requested_persona_key}': Fortsetzen {outcome.status} -- "
                f"{self._redact_creation_status_text(outcome.status, outcome.reason)}"
            )

    def _resolve_real_active_chrononaut_id(self) -> tuple[str | None, dict | None, bool]:
        """I4-Nachzug (02_ABNAHME_I4-AA, Vertrag §3 A): massgeblich fuer
        'wer ist wirklich aktiv' ist die real VEROEFFENTLICHTE Current-
        Fassung (`store.load_current_save_or_raise` -> `zeitriss_saves.
        block_char_id`), NICHT der ggf. veraltete `catalog.active_
        chrononaut_id`-Zeiger. Dieses Feld kann durch das bereits vor I4
        bestehende Absturzfenster zwischen `core_store.publish_current_save`
        und `catalog.bind_for_section` veraltet sein, waehrend Current
        selbst schon den neuen Stand traegt (End-Critic-Befund BLOCKER 1,
        2026-09-25 erneut bestaetigt: dieses veraltete Feld ist KEINE
        harmlose Anzeigeverzoegerung, sondern wurde bislang an mehreren
        Stellen als Autoritaet fuer Rueckgabe-/Sperrentscheidungen
        missbraucht, s. `_switch_active_figure`/`_cmd_import`/`_cmd_new_or_
        switch_character`).

        Weicht der Katalogzeiger von der realen Autoritaet ab, wird er HIER
        konsistent nachgezogen (`catalog.bind_for_section`, dieselbe
        bestehende Persistenz, kein neuer Speicherort) -- ein
        `ActiveBindingError` dabei ist defensiv unerheblich (Aufrufer prueft
        eine echte Sperre ueber den zurueckgegebenen `real_id` ohnehin
        separat, kein Doppelpfad).

        Liefert `(chrononaut_id, current_block, unresolved)`:
        `unresolved=True` heisst, ein BEKANNTER Current-Save konnte gerade
        NICHT gelesen werden (`store.CurrentSaveUnavailableError`, Vertrag
        §3 B) -- die reale Autoritaet bleibt in diesem Fall UNGEKLAERT; der
        Aufrufer MUSS den Uebergang kontrolliert ablehnen statt auf den
        (ggf. veralteten) Katalogzeiger auszuweichen. Ohne konfigurierte
        Laufumgebung oder ohne existierenden Current-Save bleibt der
        Katalogzeiger der einzig verfuegbare (unveraenderte) Rueckfall --
        das ist der legitime Erstzustand vor jeder Publikation."""
        catalog_active = catalog.active_chrononaut_id(self.catalog_dir, self.participant_id)
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            return catalog_active, None, False
        from ..core.persona_state import PersonaStateStore
        from ..core import store as core_store
        ps_store = PersonaStateStore(schema_path=self.schema_path)
        try:
            current = core_store.load_current_save_or_raise(
                self.run_dir, self.participant_id, ps_store, states_dir=self.states_dir,
            )
        except core_store.CurrentSaveUnavailableError:
            return catalog_active, None, True
        if current is None:
            return catalog_active, None, False
        real_id = zeitriss_saves.block_char_id(current)
        if real_id is None:
            return catalog_active, current, False
        if real_id != catalog_active:
            try:
                catalog.bind_for_section(self.catalog_dir, self.participant_id, real_id, has_open_section=False)
            except catalog.ActiveBindingError:
                pass  # defensiv, kein Doppelpfad -- Aufrufer prueft locked separat.
        return real_id, current, False

    def _sync_outgoing_active_figure(
        self, new_chrononaut_id: str, outgoing_id: str | None, outgoing_current: dict | None,
    ) -> None:
        """I4 Luecke 1 (02_ABNAHME_I4 Weg 1, Vertrag §3 A/C): vor JEDEM
        Aktivwechsel (Auswahl, Import, fertige Erschaffung -- 11 §6/Vertrag
        §3 B: 'dieselbe reale Bindungsentscheidung') wird der zuletzt real
        veroeffentlichte Current-Save der BISHERIGEN aktiven Figur in ihre
        EIGENE Katalog-Persistenz gesichert (`catalog.store_figure_save`).

        Ohne diesen Schritt haelt `catalog.store_figure_save` fuer jede
        Figur nur den Stand ihres letzten Imports/ihrer Erschaffung fest
        (dort zuletzt geschrieben, s. `_cmd_import`/`_cmd_new_or_switch_
        character`) -- ein gueltiger Abschnittsabschluss aktualisiert diese
        Kopie NICHT (er schreibt nur ueber `core.store.publish_current_save`
        / `_resume_and_harvest` den Single-Slot-Store). Ein spaeterer
        Rueckwechsel (`catalog.load_figure_save`) wuerde dann den
        veralteten Import-/Erschaffungsstand statt des zuletzt erspielten
        Fortschritts neu als Current publizieren (A -> B -> A Regression,
        02_ABNAHME_I4 Test 02). No-op ohne bisherige aktive Figur/Fassung
        oder wenn die Zielfigur bereits aktiv ist.

        I4-Nachzug (2026-09-25): `outgoing_id`/`outgoing_current` werden vom
        Aufrufer bereits einmalig ueber `_resolve_real_active_chrononaut_id`
        aufgeloest (dieselbe reale Current-Fassung, nicht der ggf.
        veraltete Katalogzeiger, und derselbe Lesevorgang statt eines
        zweiten -- wichtig fuer testbare Einmal-Fehlerinjektion an der
        Versionsdatei). Diese Funktion selbst liest nichts mehr; sie
        persistiert nur noch, was der Aufrufer bereits als reale Autoritaet
        ermittelt hat. Ein `bind_for_section`-Fehlschlagen NACH dieser
        Funktion (an der Aufrufstelle) ist WEITERHIN kein Datenverlust,
        aber die vorher hier dokumentierte Einstufung des veralteten
        Katalogzeigers als 'harmlose, selbstheilende Anzeigeverzoegerung'
        war zu optimistisch: unkorrigiert diente er andernorts als
        Autoritaet fuer Rueckgabe-/Sperrentscheidungen (s. `_resolve_real_
        active_chrononaut_id`) -- dieser Fix schliesst genau das."""
        if outgoing_id is None or outgoing_current is None or outgoing_id == new_chrononaut_id:
            return
        catalog.store_figure_save(self.catalog_dir, self.participant_id, outgoing_id, outgoing_current)

    def _effective_display_name(self, entry) -> str:
        """R5P01 (ZEITRISS TERMINAL-UX1-R6-FERTIGSTELLUNG, General-Befund
        'Figurname nicht erreichbar'): WEDER `_cmd_new_or_switch_character`s
        Erschaffungs-Publikationsweg NOCH `_cmd_import` setzen je einen
        `CatalogEntry.display_name` (keine Aufrufstelle von `catalog.
        register` uebergibt ihn) -- Anzeige UND Namensaufloesung fielen
        dadurch IMMER auf die reine Chrononaut-ID zurueck, selbst wenn der
        tatsaechlich gespeicherte v7-Save einen echten `characters[0].name`
        trug. Liest denselben bereits vorhandenen reinen Leser wie
        `_switch_active_figure` (`catalog.load_figure_save`, NUR fuer
        `entry.participant_id`/`entry.chrononaut_id` -- nie eine fremde
        Figur) -- KEINE Katalog-/Save-Mutation, KEINE neue persistente
        Namensquelle, nur ein zusaetzlicher Lesevorgang zur Anzeige/
        Aufloesung. `display_name` (falls je gesetzt) bleibt Vorrang; ein
        fehlender/unlesbarer/strukturell leerer Save liefert weiterhin ''
        (Aufrufer fallen dann wie bisher auf die rohe Chrononaut-ID
        zurueck, kein Rateweg)."""
        if entry.display_name:
            return entry.display_name
        save_block = catalog.load_figure_save(self.catalog_dir, entry.participant_id, entry.chrononaut_id)
        if not isinstance(save_block, dict):
            return ""
        chars = save_block.get("characters")
        if isinstance(chars, list) and chars and isinstance(chars[0], dict):
            name = chars[0].get("name")
            if isinstance(name, str) and name.strip():
                return name
        return ""

    def _resolve_character_choice(
        self, choice: str, entries: list,
    ) -> tuple[str, str | None]:
        """F02 (W18, Brief §Fachvertrag 1): normale Auswahl ueber eine
        STABILE Auswahlnummer (1-basierter Index in der vom autoritativen
        Katalog-Leser `catalog.list_for_participant` gelieferten Reihenfolge,
        s. Aufrufstelle) oder ueber einen eindeutigen Anzeigenamen
        (`_effective_display_name`, s. dort -- `CatalogEntry.display_name`
        sofern gesetzt, SONST der real gespeicherte `characters[0].name` aus
        dem eigenen v7-Save, R5P01-Fix) -- die Chrononaut-ID bleibt
        ZUSAETZLICH direkt eingebbar (bewusster Detail-/
        Kompatibilitaetsweg, unveraendertes Verhalten fuer bestehende
        Aufrufer/Tests, die eine ID eintippen).

        Liefert `(resolved, error_message)`. Bei eindeutiger Nummern- oder
        Namensaufloesung ist `error_message` `None` und `resolved` die
        aufgeloeste Chrononaut-ID. Bei einer Namensdublette ODER einer
        Nummer ausserhalb des Bereichs wird NICHT geraten -- `resolved`
        bleibt die rohe Eingabe (fuer eine konsistente Fehlermeldung an der
        Aufrufstelle) und `error_message` enthaelt den Hinweistext; der
        Aufrufer bricht dann OHNE Aktivwechsel ab. Ohne Nummern-/Namenstreffer
        wird die rohe Eingabe unveraendert als Chrononaut-ID-Kandidat
        zurueckgegeben -- dieselbe Pruefung wie vor dieser Erweiterung
        (`_switch_active_figure`s `known_ids`-Abgleich) entscheidet dann
        ueber gueltig/unbekannt."""
        trimmed = choice.strip()
        if trimmed.isdigit():
            idx = int(trimmed)
            if 1 <= idx <= len(entries):
                return entries[idx - 1].chrononaut_id, None
            return choice, f"Keine Figur mit Nummer {idx} -- verfuegbar: 1..{len(entries)}."
        name_matches = [
            (i, e) for i, e in enumerate(entries, start=1)
            if self._effective_display_name(e).strip().lower() == trimmed.lower()
        ] if trimmed else []
        if len(name_matches) == 1:
            return name_matches[0][1].chrononaut_id, None
        if len(name_matches) > 1:
            dupes = ", ".join(f"[{i}] {e.chrononaut_id}" for i, e in name_matches)
            return choice, f"Name {choice!r} ist nicht eindeutig -- bitte Nummer oder ID angeben ({dupes})."
        return choice, None

    def _switch_active_figure(self, chosen_id: str, entries: list) -> None:
        """W4 (F4, "echte Auswahl-Eingabe in n"): aktiviert eine bereits
        registrierte, bisher inaktive Figur -- laedt ihre eigenen,
        getrennt persistierten Savebytes (`catalog.load_figure_save`, NICHT
        den Single-Slot-Store einer ANDEREN Figur) und publiziert sie als
        neuen Current-Save. Ein Wechsel wird abgelehnt, solange die
        BISHERIGE aktive Figur einen offenen Abschnitt/Abschlussauftrag hat
        (dieselbe Sperrsemantik wie `_cmd_import`s Aktivwechsel, 11 §6).

        I4-Nachzug (Vertrag §3 A/T1a/T1b): 'bisherige aktive Figur' wird
        HIER ueber `_resolve_real_active_chrononaut_id` bestimmt (reale
        Current-Fassung), NICHT ueber den ggf. nach einem unterbrochenen
        Wechsel veralteten `catalog.active_chrononaut_id`-Zeiger -- sonst
        wuerde (T1a) ein bereits aktives Ziel faelschlich als 'inaktiv'
        behandelt und aus seinem veralteten Katalogstand neu publiziert
        (Fortschritts-Rollback), und (T1b) die Sperrpruefung gegen die
        falsche (unlocked) alte ID statt die real gebundene Figur pruefen
        (Bindungsumgehung)."""
        known_ids = {e.chrononaut_id for e in entries}
        if chosen_id not in known_ids:
            self._print(f"Unbekannte Chrononaut-ID {chosen_id!r} — keine Aenderung (verfuegbar: {sorted(known_ids)}).")
            return
        active_id, active_current, unresolved = self._resolve_real_active_chrononaut_id()
        if unresolved:
            self._print(
                f"Wechsel zu '{chosen_id}' nicht moeglich: der Spielstand der bisherigen aktiven Figur "
                "ist gerade nicht lesbar — kein Wechsel, bis die tatsaechliche Autoritaet geklaert ist "
                "(Fassung bleibt ungefaehrdet, spaeter erneut versuchen)."
            )
            return
        if chosen_id == active_id:
            self._print(f"'{chosen_id}' ist bereits die aktive Figur.")
            return
        locked = False
        if self.run_dir is not None and active_id is not None:
            from ..core import store as core_store
            locked = (
                core_store.chrononaut_active_binding(self.run_dir, active_id)
                or core_store.chrononaut_open_completion_order(self.run_dir, active_id)
            )
        if locked:
            self._print(
                f"Wechsel zu '{chosen_id}' nicht moeglich: aktive Figur '{active_id}' hat einen "
                "offenen Abschnitt/Abschlussauftrag — zuerst abschliessen oder Sitzung fortsetzen (11 §6)."
            )
            return
        # I4 Luecke 1 (s. `_sync_outgoing_active_figure`): die bisherige
        # aktive Figur wird VOR dem Ueberschreiben von Current mit ihrem
        # zuletzt real veroeffentlichten Stand im Katalog gesichert.
        self._sync_outgoing_active_figure(chosen_id, active_id, active_current)
        save_block = catalog.load_figure_save(self.catalog_dir, self.participant_id, chosen_id)
        if save_block is None:
            self._print(f"Fuer '{chosen_id}' liegen keine gespeicherten Savebytes vor — Wechsel nicht moeglich.")
            return
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            onboarding.ensure_participant_persona_state(
                ps_store, self.states_dir, self.participant_id, chosen_id, save_block,
            )
            core_store.publish_current_save(
                self.run_dir, self.participant_id, save_block, ps_store, self.states_dir,
            )
        try:
            catalog.bind_for_section(self.catalog_dir, self.participant_id, chosen_id, has_open_section=False)
        except catalog.ActiveBindingError:
            pass  # bereits oben ueber `locked` behandelt -- defensiv, kein Doppelpfad.
        self._print(f"Aktive Figur gewechselt: {active_id!r} -> {chosen_id!r}.")

    def _cmd_import(self) -> None:
        if self._lab_active_guard("Import"):
            return
        self._print(
            "JSON-Datei-Pfad ODER Mehrzeilentext einfuegen, Ende mit einer Zeile 'ENDE' "
            "('/abbrechen' oder '/zurueck' als ERSTE Zeile bricht ab, kein Write):"
        )
        lines = []
        while True:
            line = self._readline("")
            # R5b (T-Befund, UX05/UX16, Korrekturzyklus 1): nur die ERSTE
            # Zeile wird auf einen Abbruchbefehl geprueft (exakte
            # Gleichheit) -- kein globaler Parser, der JEDE Zeile des
            # Mehrzeilen-JSON-Texts als Steuerzeile interpretiert (echter
            # v7-Save-Text beginnt nie mit genau dieser Zeile). Das ist der
            # klar benannte Abbruchweg, der hier vorher fehlte (ein
            # eingegebenes '/abbrechen' wurde bisher einfach als Teil des
            # einzufuegenden Texts gewertet und landete ungueltig in
            # `json.loads`).
            if not lines and line.strip() in ("/abbrechen", "/zurueck"):
                self._print("Import abgebrochen -- kein Text uebernommen, kein Write.")
                return
            if line.strip() == "ENDE":
                break
            lines.append(line)
        raw = "\n".join(lines).strip()
        if not raw:
            self._print("Kein Text erhalten — Import abgebrochen (kein Write).")
            return
        # I3/Test 06: ein angebotener DATEIPFAD (genau eine Zeile, verweist
        # auf eine existierende Datei) wird GELESEN statt als roher JSON-Text
        # geparst -- vorher ging jede Eingabe direkt in `json.loads`.
        # W45: ein einzeiliger voller v7-JSON-Text kann die Pfadkomponenten-
        # Laengengrenze des Dateisystems ueberschreiten -- `Path.is_file()`
        # wirft dann OSError (ENAMETOOLONG) statt False zu liefern. Das ist
        # erkennbar KEIN Dateipfad, also faellt die Eingabe kontrolliert auf
        # den rohen-JSON-Zweig zurueck statt mit Traceback abzubrechen.
        if len(lines) == 1:
            try:
                is_path = Path(raw).is_file()
            except OSError:
                is_path = False
            if is_path:
                candidate_path = Path(raw)
                try:
                    raw = candidate_path.read_text(encoding="utf-8")
                except OSError as e:
                    self._print(f"Datei konnte nicht gelesen werden: {e}")
                    return
        try:
            preview = import_export.preview_import(raw)
        except import_export.MalformedImportError as e:
            # R8 (T-Befund 4, UX05/UX18, Korrekturzyklus 1): `preview_import`
            # (mmo_sim/domain/zeitriss/import_export.py, ausserhalb des hier
            # erlaubten Edit-Scopes) haengt bei einem JSON-Parserfehler den
            # ROHEN Python-`json`-Fehlertext an (z.B. "Expecting value: line
            # 1 column 1 (char 0)") -- technisches Fachchinesisch fuer
            # Laien. Nur die ANZEIGE hier wird laientauglich gemacht (kein
            # Traceback, kein rohes Exception-Detail); der "kein
            # Write"-Schutz und alle anderen (bereits verstaendlichen)
            # Schema-Meldungen bleiben unveraendert.
            msg = str(e)
            if msg.startswith("kein gueltiges JSON:"):
                msg = (
                    "der eingegebene Text/die Datei ist kein gueltiges JSON (z.B. fehlende "
                    "Anfuehrungszeichen, Kommas oder Klammern) — bitte Text/Datei pruefen und "
                    "erneut versuchen."
                )
            self._print(f"Import abgelehnt (strukturell ungueltig, kein Write): {msg}")
            return
        self._print(f"Vorschau: char_id={preview.char_id} level={preview.level} Herkunft=extern importiert")

        # F5/K4 (WEGKARTE BLOCKER 1): Vorschau allein uebernimmt nichts --
        # ab hier tatsaechliche Uebernahme ueber `import_export.resolve_import`
        # (11 §5, vier Zielzuordnungsfaelle) + `onboarding.complete_with_save`.
        incoming_block = json.loads(raw)
        known_char_ids = {e.chrononaut_id for e in catalog.list_for_participant(self.catalog_dir, self.participant_id)}
        existing_state = onboarding.peek(self.onboarding_dir, self.participant_id)
        existing_onboarding_save = existing_state.final_save if existing_state is not None else None
        # A7/D1 (WEGKARTE §8, Plan-Critic A7, Test 06): Konfliktbasis ist
        # der aktuell PUBLIZIERTE Stand (`_resolve_active_save`), NICHT
        # `onboarding.final_save` -- sonst publiziert 'bisherigen Stand
        # behalten' einen veralteten Erschaffungsstand als neue aktuelle
        # Version und wirft echten Fortschritt weg.
        # I4-Nachzug (Vertrag §3 A/B, R1a): die Konfliktbasis muss VOR jeder
        # a/k-Wahl und jedem Zielsave-Write feststehen -- ein bekannter,
        # gerade nicht lesbarer Current darf NICHT durch den (moeglicherweise
        # veralteten) Onboarding-Stand ersetzt werden (sonst wuerde 'k'
        # echten Fortschritt zurueckrollen). Kontrollierter Abbruch VOR jeder
        # weiteren Entscheidung/jedem Write; erster Import ohne
        # veroeffentlichten Current (unresolved=False, baseline_block=None
        # oder Onboarding-Stand) bleibt unveraendert moeglich.
        baseline_block, baseline_unresolved = self._resolve_active_save(
            self.participant_id, existing_onboarding_save,
        )
        if baseline_unresolved:
            self._print(
                "Import abgebrochen: der aktuell veroeffentlichte Spielstand ist gerade nicht "
                "lesbar — keine Konfliktentscheidung ohne geklaerte Autoritaet (kein Write, "
                "spaeter erneut versuchen)."
            )
            return
        # R5a (T-Befund, UX05/UX16, Korrekturzyklus 1) -- GEPRUEFT, NICHT
        # UMGESETZT: eine echte "Vorschau -> bestaetigen/verwerfen"-Abfrage
        # genau an dieser Stelle (ALLERERSTER Import, noch kein
        # Katalogeintrag/aufloesbarer Stand) wurde versucht und wieder
        # ENTFERNT -- jede zusaetzliche Pflichteingabe HIER verschiebt die
        # Eingabezeilen ALLER bestehenden, real-subprocess-gescripteten
        # Tests, die einen fehlerfrei durchlaufenden Erstimport als
        # (impliziten) Setup-Schritt nutzen (beobachtet: `test_a23_
        # bounded_vorlauf_2026_09_30.py::test_v3_api_profile_real_tui_to_
        # lab_to_persona_journey` haengt dadurch in einem echten
        # Subprozess fest, 150s Timeout, zieht ueber `generate_existing_
        # a23_journey_inputs()` KASKADIEREND `test_a13_local_provenance_
        # 2026_09_30.py` mit). Bleibt ehrlich dokumentierter Blocker (s.
        # WORKER2-REPORT.md) statt eines UI-Nachbaus, der die bestehende
        # Testsuite bricht -- R5b (Abbruch waehrend JSON-Mehrzeilen-
        # Eingabe UND an der [w/b]-Rueckfrage, beide unten) bleibt real
        # umgesetzt.
        existing_block_for_char_id = None
        if baseline_block is not None:
            baseline_char_id = zeitriss_saves.block_char_id(baseline_block)
            if baseline_char_id is not None:
                known_char_ids.add(baseline_char_id)
                if baseline_char_id == preview.char_id:
                    existing_block_for_char_id = baseline_block
        # I4 Weg 3 (02_ABNAHME_I4, Vertrag §3 D "Importkonflikt betrifft die
        # ZIELFIGUR, auch wenn sie inaktiv ist"): ohne diesen Fallback bleibt
        # `existing_block_for_char_id` fuer eine bereits registrierte, aber
        # INAKTIVE Figur immer `None` (der obige Zweig deckt nur die
        # AKTIVE/`baseline`-Figur ab) -- ein Re-Import derselben inaktiven
        # Figur wuerde dann selbst bei byte-identischen Bytes NIE den
        # idempotenten `noop_identical`-Fall erreichen (A20: "identischer
        # Import No-op" gilt fuer JEDE bekannte Char-ID, nicht nur die
        # aktive) und ein abweichender Stand wuerde ohne echte Vorschau
        # bloss geparkt statt der bestehenden Konfliktwahl unten angeboten.
        if existing_block_for_char_id is None and preview.char_id in known_char_ids:
            existing_block_for_char_id = catalog.load_figure_save(
                self.catalog_dir, self.participant_id, preview.char_id,
            )

        # Fall 3 (11 §5): bekannte Char-ID, abweichender Stand -- braucht die
        # ausdrueckliche Konfliktwahl, die der bisherige Hinweistext bereits
        # ankuendigte. Ohne echten Konflikt (Fall 1/2/4) wird NICHT gefragt.
        explicit_choice = None
        if preview.char_id in known_char_ids and existing_block_for_char_id is not None and existing_block_for_char_id != incoming_block:
            self._print(
                "Bekannte Figur mit abweichendem Stand -- ausdrueckliche Konfliktwahl noetig: "
                "'a' importierten Stand uebernehmen, 'k' bisherigen Stand behalten."
            )
            # F02 (W18, Brief §Fachvertrag 3): dieser Prompt las vorher roh
            # (`self._readline`) -- '/hilfe' etc. landeten als ungueltige
            # Wahl im geparkten Zweig unten, OHNE jemals echten Hilfetext zu
            # zeigen. Derselbe zentrale Leser wie an jedem anderen Prompt;
            # eine Steuerzeile loest HIER explizit KEINE Konfliktwahl/Write
            # aus (0 Writes). Das JSON-/Mehrzeilen-Paste weiter oben in
            # dieser Funktion (ENDE-Marker) bleibt bewusst AUSSERHALB dieses
            # zentralen Lesers (eigene Erstzeilenpruefung, s. dort).
            answer, control = self._readline_with_controls(
                "Wahl [a/k]: ", context="Importkonflikt (abweichender Stand)",
            )
            if control in ("zurueck", "abbrechen", "pause"):
                self._print("Lokal verarbeitet -- Import bleibt geparkt (kein Write), keine Konfliktwahl getroffen.")
                return
            answer = answer.strip().lower()
            if answer == "a":
                explicit_choice = "adopt_incoming"
            elif answer == "k":
                explicit_choice = "keep_existing"
            else:
                self._print("Keine gueltige Wahl getroffen -- Import bleibt geparkt (kein Write).")
                return

        # D1/A1 (K3, PLAN-CRITIC-ABSCHLUSS.md BLOCKER): echte Lock-/
        # Bindungspruefung statt hart verdrahtetem `active_binding=False` --
        # ohne konfigurierte Laufumgebung (Offline-Default) bleibt die alte
        # konfliktfreie Semantik erhalten (kein Store zum Pruefen vorhanden).
        active_binding = False
        open_completion_order = False
        if self.run_dir is not None and preview.char_id is not None:
            from ..core import store as core_store
            active_binding = core_store.chrononaut_active_binding(self.run_dir, preview.char_id)
            open_completion_order = core_store.chrononaut_open_completion_order(self.run_dir, preview.char_id)

        decision = import_export.resolve_import(
            incoming_block, known_char_ids=known_char_ids,
            existing_block_for_char_id=existing_block_for_char_id,
            active_binding=active_binding, open_completion_order=open_completion_order,
            explicit_choice=explicit_choice,
        )
        if decision.action == "parked":
            self._print(f"Import geparkt (keine Uebernahme): {decision.reason}")
            return
        if decision.action == "noop_identical":
            self._print(f"Identischer Save bereits vorhanden -- kein zweiter Fortschritt: {decision.reason}")
            return
        # G02/P12 (General-Befund 'P12_FIRST_IMPORT_WRITES_WITHOUT_YES', 02
        # §C "Abbrechen vor einer expliziten Bestaetigung verwirft nur den
        # Entwurf"): ohne bereits getroffene Konfliktwahl (`explicit_choice`
        # oben, Fall 3 'a'/'k') lief JEDE tatsaechliche Uebernahme --
        # INSBESONDERE der allererste Import ohne jeden Konflikt (frischer
        # Datenroot) -- bisher sofort in den Write unten, ohne irgendeine
        # Ja-Bestaetigung. Jetzt: Vorschau ist bereits oben gezeigt: eine
        # eigene, ausdruecklich bestaetigte Zeile VOR dem ersten Write
        # (`catalog.store_figure_save` unten). Abbruch/EOF verwirft NUR
        # diesen Entwurf -- kein Write erfolgt vor dieser Stelle, bereits
        # bestehende Figuren/Registrierungen anderer frueherer Importe
        # bleiben unberuehrt. Die bereits bestehende 'a'/'k'-Konfliktwahl
        # (Fall 3) gilt selbst schon als ausdruecklicher Ja-Entscheid --
        # keine doppelte Rueckfrage fuer denselben Entwurf.
        if explicit_choice is None:
            from ..adapters.base import human_menu_decision
            try:
                confirm_raw, confirm_control = self._readline_with_controls(
                    f"Figur char_id={preview.char_id} jetzt uebernehmen und speichern? [j/n]: ",
                    context="Import bestaetigen",
                )
            except EndOfInput:
                self._print("\nImport abgebrochen (EOF) -- kein Write, Entwurf verworfen.")
                return
            if confirm_control in ("zurueck", "abbrechen", "pause"):
                self._print("Import abgebrochen -- kein Write, Entwurf verworfen.")
                return
            confirm_decision, _explanation = human_menu_decision(confirm_raw)
            if confirm_decision != "accept":
                self._print("Import abgebrochen -- kein Write, Entwurf verworfen.")
                return
        # register_new | adopt_incoming | keep_existing -> Save wirklich
        # uebernehmen (kein Dummy-v7).
        # W4-Fix (F4, PLAN-CRITIC.md Auflage 4, Test 07 review_p2w_
        # boundaries.py): eigene, dauerhafte Savebytes JEDER registrierten
        # Figur -- UNABHAENGIG davon, ob dieser Import gleich aktiv wird
        # oder (bei bereits anderweitig aktiver/gesperrter Figur) inaktiv
        # registriert bleibt. Vorher lief `onboarding.complete_with_save`
        # hier UNBEDINGT fuer JEDEN Import und ueberschrieb den EINEN
        # Onboarding-Slot (`onboarding.py`, ein Slot pro Teilnehmer,
        # unabhaengig von der Char-ID) -- ein zweiter Import einer anderen
        # Figur loeschte damit die Bytes der ERSTEN inaktiven Figur, obwohl
        # nur eine Katalog-ID von ihr uebrig blieb (Bug). Jetzt: die
        # getrennte, per (participant_id, chrononaut_id) geschluesselte
        # Persistenz (`catalog.store_figure_save`) haelt JEDE Figur fest;
        # `onboarding.complete_with_save` (der EINE Slot) wird weiter unten
        # NUR NOCH aufgerufen, wenn diese Uebernahme tatsaechlich die
        # AKTIVE Figur wird/bleibt (Onboarding bildet damit wieder korrekt
        # NUR den aktuellen Erschaffungs-/Importkontext der aktiven Figur
        # ab, "Onboarding ≠ Mehrfigurenarchiv", WEGKARTE W4).
        catalog.store_figure_save(self.catalog_dir, self.participant_id, preview.char_id, decision.block)
        # A2/R11-Restintegrationsfix (WEGKARTE §4 A2, Plan-Critic-Auflage,
        # REVIEW-P2R.md R-F, END-CRITIC-ABSCHLUSSWEGE.md BLOCKER-1): Betrifft
        # die Uebernahme eine ANDERE Char-ID als die aktuell aktive Figur,
        # darf sie NIE automatisch als Aktivwechsel durchlaufen -- UNABHAENGIG
        # davon, ob die aktive Figur GERADE gesperrt ist. Der erste Wurf
        # dieses Fixes pruefte nur den gesperrten Fall (Tisch/Abschlussauftrag
        # offen) und liess den entsperrten Alltagsfall (Mensch hat einen
        # Abschnitt bereits regulaer abgeschlossen, Lock ist laut
        # `release_chrononaut` beim Abschluss wieder weg, ist wieder in der
        # Lobby) unveraendert still durchlaufen -- exakt der urspruengliche
        # R-F-Fehler, nur ausserhalb des vom p2r-Test 11 geprueften
        # Zeitfensters (Tisch dort permanent gesperrt gehalten).
        #   - Gesperrt (offener Abschnitt/Abschlussauftrag): strukturell
        #     verbotener Wechsel (11 §6: "Offene Abschnitte zunaechst
        #     fortsetzen oder kontrolliert abbrechen, nicht durch einen
        #     Charakterwechsel umgehen") -- reine inaktive Zweitregistrierung,
        #     keine Rueckfrage moeglich (ein Wechsel waere ohnehin verboten).
        #   - Entsperrt (saubere Abschnittsgrenze): ein Wechsel verlangt eine
        #     ausdrueckliche Bestaetigung, analog zur bereits vorhandenen
        #     Konfliktabfrage 'Wahl [a/k]' oben (Fall 3) -- NICHT automatisch
        #     als 'register_new'-Aktivwechsel durchlaufen.
        # Der ALLERERSTE Import ohne jede aktive Bindung (active_elsewhere is
        # None) bleibt unveraendert ein normaler Aktivwechsel ohne Rueckfrage.
        #
        # I4-Nachzug (Vertrag §3 A/T1b): 'aktive Figur' wird HIER ueber
        # `_resolve_real_active_chrononaut_id` bestimmt (reale Current-
        # Fassung), NICHT ueber den ggf. veralteten `catalog.active_
        # chrononaut_id`-Zeiger -- sonst wuerde die Sperrpruefung gegen die
        # falsche (unlocked) alte ID statt die real gebundene Figur pruefen
        # (Bindungsumgehung ueber Import).
        active_elsewhere, active_current, unresolved = self._resolve_real_active_chrononaut_id()
        if unresolved:
            # Zielsave bleibt inaktiv registriert (Bytes bereits oben ueber
            # `catalog.store_figure_save` gesichert) statt nach dem gerade
            # lesbaren, aber ggf. falschen Katalogzeiger freizugeben.
            catalog.register(self.catalog_dir, catalog.CatalogEntry(
                participant_id=self.participant_id, chrononaut_id=preview.char_id,
                persona_key=self.participant_id,
            ))
            self._print(
                f"Zweite Figur registriert (INAKTIV): char_id={preview.char_id}. Der Spielstand der "
                "bisherigen aktiven Figur ist gerade nicht lesbar — kein Import-Aktivwechsel, bis die "
                "tatsaechliche Autoritaet geklaert ist (spaeter erneut versuchen)."
            )
            return
        locked_elsewhere = False
        if self.run_dir is not None and active_elsewhere is not None and active_elsewhere != preview.char_id:
            from ..core import store as core_store
            locked_elsewhere = (
                core_store.chrononaut_active_binding(self.run_dir, active_elsewhere)
                or core_store.chrononaut_open_completion_order(self.run_dir, active_elsewhere)
            )
        if active_elsewhere is not None and active_elsewhere != preview.char_id:
            if locked_elsewhere:
                catalog.register(self.catalog_dir, catalog.CatalogEntry(
                    participant_id=self.participant_id, chrononaut_id=preview.char_id,
                    persona_key=self.participant_id,
                ))
                self._print(
                    f"Zweite Figur registriert (INAKTIV): char_id={preview.char_id} — die aktive "
                    f"Figur {active_elsewhere!r} bleibt an einem offenen Abschnitt/Abschlussauftrag "
                    "gebunden, daher keine Current-/State-Aktivierung und kein Aktivwechsel "
                    "(saubere Abschnittsgrenze fuer einen spaeteren Wechsel abwarten)."
                )
                return
            self._print(
                f"Du hast bereits eine aktive Figur ({active_elsewhere!r}). Ein Wechsel zu "
                f"{preview.char_id!r} braucht eine ausdrueckliche Bestaetigung: "
                "'w' aktive Figur JETZT wechseln, 'b' bisherige aktive Figur behalten "
                "(Import bleibt als inaktive Zweitfigur registriert), '/abbrechen' den ganzen "
                "Import verwerfen (keine neue Registrierung)."
            )
            # F02 (W18, Brief §Fachvertrag 3): vormals ad-hoc-Sonderpruefung
            # NUR fuer die woertlichen Strings '/abbrechen'/'/zurueck' (W11-
            # Matrixbefund Zeile 8, "nicht ueber den zentralen Leser") --
            # '/pause'/'/hilfe'/'?'/'/stand'/'/verlauf' gingen hier bisher
            # ALS ANTWORT durch und landeten (ausser 'w') im 'b'-Zweig
            # darunter, der eine echte INAKTIV-Registrierung schreibt (ein
            # '/hilfe'-Versuch haette also einen Write ausgeloest). Jetzt
            # derselbe zentrale Leser wie an jedem anderen Prompt; JEDE der
            # fuenf Steuerzeilen bricht HIER kontrolliert ab, OHNE
            # `catalog.register` zu erreichen (0 Writes). Escaped Literal-
            # text ('\\/abbrechen') kommt als normaler Text zurueck und
            # faellt bewusst unveraendert in den 'b'-Zweig (keine versteckte
            # Sonderbedeutung fuer Text, der nur WIE eine Steuerzeile
            # aussieht).
            answer, control = self._readline_with_controls(
                "Wahl [w/b]: ", context="Importkonflikt (Aktivwechsel)",
            )
            if control in ("zurueck", "abbrechen", "pause"):
                self._print(
                    f"Lokal verarbeitet -- Import verworfen, char_id={preview.char_id} NICHT "
                    f"registriert. Aktive Figur {active_elsewhere!r} bleibt unveraendert."
                )
                return
            answer = answer.strip().lower()
            if answer != "w":
                catalog.register(self.catalog_dir, catalog.CatalogEntry(
                    participant_id=self.participant_id, chrononaut_id=preview.char_id,
                    persona_key=self.participant_id,
                ))
                self._print(
                    f"Zweite Figur registriert (INAKTIV): char_id={preview.char_id} — aktive Figur "
                    f"{active_elsewhere!r} bleibt gewaehlt (kein Aktivwechsel ohne ausdrueckliches 'w')."
                )
                return
        # W4-Fix: ab hier steht fest, dass diese Uebernahme die AKTIVE
        # Figur wird/bleibt (beide INAKTIV-Zweige oben haben bereits per
        # `return` verlassen) -- der EINE Onboarding-Slot (`onboarding.
        # final_save`) wird jetzt (und NUR jetzt) auf diesen Stand gesetzt,
        # damit er weiterhin den aktuellen Erschaffungs-/Importkontext der
        # AKTIVEN Figur widerspiegelt (Fall-3-Konfliktbasis oben,
        # Fortsetzen-Karte) -- kein Verlust: die inaktiven Faelle haben ihre
        # Bytes bereits ueber `catalog.store_figure_save` erhalten.
        # I4 Luecke 1 (s. `_sync_outgoing_active_figure`): die bisherige
        # aktive Figur (falls vorhanden, z.B. beim 'w'-Aktivwechsel oben)
        # wird VOR dem Ueberschreiben von Current mit ihrem zuletzt real
        # veroeffentlichten Stand im Katalog gesichert. No-op beim ALLERERSTEN
        # Import (noch keine aktive Figur).
        self._sync_outgoing_active_figure(preview.char_id, active_elsewhere, active_current)
        onboarding.start_or_resume(self.onboarding_dir, self.participant_id)
        onboarding.complete_with_save(
            self.onboarding_dir, self.participant_id, decision.block,
            ZeitrissHarvestValidator(), preview.char_id,
        )
        # D1/K2/K4 (PLAN-CRITIC-ABSCHLUSS.md A2/A7): Uebernahme erzeugt/
        # aktualisiert den gemeinsamen Persona-State UND publiziert die
        # Fassung als Current-Save -- NUR mit konfigurierter Laufumgebung
        # (Offline-Default bleibt reiner Onboarding-Stand, wie zuvor).
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            onboarding.ensure_participant_persona_state(
                ps_store, self.states_dir, self.participant_id, preview.char_id, decision.block,
            )
            core_store.publish_current_save(
                self.run_dir, self.participant_id, decision.block, ps_store, self.states_dir,
            )
        # A21 (WEGKARTE §8, 11 §6): Katalogregistrierung -- macht die Figur
        # in `catalog.list_for_participant`/`last_selected` sichtbar
        # (Fortsetzen-Karte, Mehrfiguren-Uebersicht). Bindet sie zugleich
        # als aktuell gewaehlte Figur (idempotent bei wiederholtem Import
        # derselben Char-ID).
        catalog.register(self.catalog_dir, catalog.CatalogEntry(
            participant_id=self.participant_id, chrononaut_id=preview.char_id,
            persona_key=self.participant_id,
        ))
        try:
            # END-CRITIC-ABSCHLUSSWEGE.md BLOCKER-1: `has_open_section` war
            # hier hartkodiert `False` und umging `bind_for_section`s eigene
            # interne Schutzlogik strukturell, unabhaengig vom echten
            # Sperrzustand. `locked_elsewhere` ist der oben bereits real
            # berechnete Wert (an dieser Stelle im Code immer `False`, weil
            # ein `True`-Wert oben bereits zu einem fruehen `return` gefuehrt
            # haette) -- die Weitergabe des tatsaechlichen Zustands statt
            # eines Literals ist der eigentliche Fix.
            catalog.bind_for_section(self.catalog_dir, self.participant_id, preview.char_id, has_open_section=locked_elsewhere)
        except catalog.ActiveBindingError:
            pass  # Import selbst ist kein Abschnittswechsel (D1: "Import != Spielabschnitt").
        self._print(f"Uebernahme abgeschlossen: action={decision.action} char_id={preview.char_id} ({decision.reason})")
        # A23 (WEGKARTE §8, 11 §7): "Nach hoeherem Import bleibt Direktspielen
        # ohne Levelangleichung der Standard." -- NUR bei tatsaechlicher
        # Uebernahme eines (angenommen) hoeheren Standes anbieten, nicht bei
        # keep_existing/noop_identical (kein neuer Stand uebernommen).
        if decision.action in ("register_new", "adopt_incoming"):
            self._maybe_offer_bounded_preflight(preview.level)

    def _maybe_offer_bounded_preflight(self, imported_level: int | None) -> None:
        """A23 (WEGKARTE §8, 11 §7): vereinfachte, aber ehrliche Heuristik
        fuer 'erfahrener als reguläre Stammfiguren' (Level >= 2; genaue
        Community-Baseline-Vergleiche sind ein offener Ausbau, s.
        WORKER-REPORT). Default ist WEITERSPIELEN ohne Levelangleichung
        (kein automatischer Vorlauf); der Vorlauf selbst bleibt EXPLIZIT zu
        bestaetigende Lab-Konfiguration."""
        if imported_level is None or not isinstance(imported_level, (int, float)) or imported_level < 2:
            return
        if self.run_dir is None:
            return
        self._print(
            f"Dein importierter Chrononaut ist erfahrener (Level {imported_level}) als reguläre neue Stammfiguren.\n"
            "  [w] Direkt weiterspielen -- alle Staende bleiben unveraendert\n"
            "  [v] Begrenzten KI-Vorlauf konfigurieren\n"
            "  [s] Spaeter entscheiden"
        )
        # F02 (W18, Brief §Fachvertrag 5): dies ist das ERSTE, aus dem
        # normalen Importweg (`_cmd_import`) erreichbare Gate dieser
        # Operatornahen Vorlaufkette -- synthetisch, kein Modell-/GM-Call an
        # dieser Stelle (ein echter Vorlauf braucht weiterhin die separate,
        # unveraenderte Startbestaetigung in `_cmd_bounded_ai_preflight`).
        # Derselbe zentrale Leser wie an jedem anderen Prompt; eine
        # Steuerzeile startet HIER explizit KEINEN Vorlauf. R5P03-Fix
        # (ZEITRISS TERMINAL-UX1-R6-FERTIGSTELLUNG): die TIEFEREN Profil-/
        # Personas-/Budget-Prompts (`_cmd_bounded_ai_preflight`,
        # `_bounded_preflight_select_personas`, `_bounded_preflight_
        # collect_budget`) sind jetzt EBENFALLS an diesen zentralen Leser
        # gebunden (vorher roh: ein erreichtes `/hilfe` wurde dort woertlich
        # als ungueltiges Profil/Personaliste/Budgetwert abgelehnt statt
        # Hilfe zu zeigen) -- weiterhin KEINE echte Vorlaufausfuehrung/
        # Budgetlogik-Aenderung, nur die Eingabeerkennung an diesen bereits
        # admin-nahen Prompts (W11-Matrix Zeile 15).
        choice, control = self._readline_with_controls(
            "Wahl [w/v/s]: ", context="KI-Vorlauf-Angebot",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Kein KI-Vorlauf gestartet (lokal verarbeitet, keine Aenderung).")
            return
        choice = choice.strip().lower()
        if choice != "v":
            self._print("Kein KI-Vorlauf gestartet (Standard: direkt weiterspielen ohne Levelangleichung).")
            return
        self._cmd_bounded_ai_preflight()

    def _cmd_bounded_ai_preflight(self) -> None:
        """A23 (WEGKARTE §8, 11 §7): echte Opt-in-Konfiguration fuer den
        begrenzten KI-Vorlauf. 'KI-Vorlauf ist KEIN Levelknopf. Es ist eine
        Konfiguration des bereits beauftragten Labormodus.' Nutzt DENSELBEN
        gemeinsamen, bereits abgenommenen Lab-Dispatcher
        (`scripts/mmo_sim.py lab resume ...`, derselbe Einstieg wie
        `mmo_sim.lab.cli.main`) als kontrollierten Kindprozess -- kein
        direkter neuer `LabRunner`-Scheinlauf, keine kopierte Lobby-/
        Request-/Save-Schleife. Erst NACH der letzten ausdruecklichen
        Startbestaetigung wird dieser Kindprozess ueberhaupt gestartet; jeder
        vorherige Rueckweg (leere/ungueltige Eingabe, EOF, 'nein') erwirbt
        keine Lab-Autoritaet und schreibt keinen Status/Budget/Stop."""
        if self.run_dir is None:
            self._print(
                "KI-Vorlauf erfordert eine konfigurierte Laufumgebung (run_dir) -- hier nicht "
                "konfiguriert, keine Konfiguration moeglich."
            )
            return
        if self._lab_active_guard("KI-Vorlauf"):
            return
        lookup = self._bounded_preflight_lookup_community()
        if lookup is None:
            return
        raw_community_id, community_id, available_personas = lookup

        profile, control = self._readline_with_controls(
            "Profil [api/hybrid]: ", context="KI-Vorlauf-Profil",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("KI-Vorlauf abgebrochen (lokal verarbeitet, kein Profil uebernommen, kein Vorlauf gestartet).")
            return
        profile = profile.strip().lower()
        if profile not in ("api", "hybrid"):
            self._print(
                f"KI-Vorlauf: ungueltiges/fehlendes Profil {profile!r} (nur 'api'/'hybrid') -- "
                "kein Vorlauf gestartet."
            )
            return

        selected = self._bounded_preflight_select_personas(available_personas)
        if selected is None:
            return

        budget = self._bounded_preflight_collect_budget()
        if budget is None:
            return

        self._print(
            "Zusammenfassung KI-Vorlauf (noch KEIN Start):\n"
            f"  Community: {community_id} (roh: {raw_community_id})\n"
            f"  Profil: {profile}\n"
            f"  Ausgewaehlte freie KI-Personas: {', '.join(selected)}\n"
            f"  max-requests={budget['max_requests']} max-seconds={budget['max_seconds']} "
            f"max-usd={budget['max_usd']} max-idle-windows={budget['max_idle_windows']} "
            f"max-wall-seconds={budget['max_wall_seconds']}\n"
            "  Eigener Chrononaut bleibt ungespielt; kein Level-/Wallet-/Ausruestungswrite; "
            "Konfigurationsfehler/Hold/Limit sind kein Spielerfolg."
        )
        confirm, control = self._readline_with_controls(
            "Vorlauf jetzt wirklich starten? [ja/nein]: ", context="KI-Vorlauf-Bestaetigung",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("KI-Vorlauf nicht gestartet (lokal verarbeitet, keine Lab-Autoritaet erworben).")
            return
        confirm = confirm.strip().lower()
        if confirm != "ja":
            self._print(
                "KI-Vorlauf nicht gestartet (keine ausdrueckliche Bestaetigung) -- keine "
                "Lab-Autoritaet erworben."
            )
            return

        argv = [
            "lab", "resume",
            "--data-dir", str(self.run_dir.parent),
            "--community", raw_community_id,
            "--profile", profile,
            "--personas", ",".join(selected),
            "--max-requests", str(budget["max_requests"]),
            "--max-seconds", str(budget["max_seconds"]),
            "--max-usd", str(budget["max_usd"]),
            "--max-idle-windows", str(budget["max_idle_windows"]),
            "--max-wall-seconds", str(budget["max_wall_seconds"]),
        ]
        self._bounded_preflight_dispatch_controller(argv, budget["max_wall_seconds"])

    def _bounded_preflight_lookup_community(self) -> tuple[str, str, list[str]] | None:
        """Bestimmt die Community ausschliesslich aus dem vorhandenen,
        konsistenten Sessionpfad -- derselbe deterministische Bezug wie
        `_cmd_community` (`community-<participant_id>`), kein Raten, kein
        impliziter Bootstrap. Fehlt eine bestaetigte Community mit
        geschriebenen Personas, wird kontrolliert abgelehnt (11 §7 V2:
        'fehlende Bestaende ... kontrollierter Abbruch'; A23 §2: 'Keine neue
        Community erzeugen und keinen Bestands-Hold umgehen')."""
        from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
        raw_community_id = self.participant_id
        community_id = f"community-{raw_community_id}"
        community_dir = self.run_dir / "community"
        bootstrap = peek_bootstrap(community_dir, community_id)
        if bootstrap is None or not bootstrap.personas_written:
            self._print(
                f"KI-Vorlauf: keine bestehende bestaetigte Spielgemeinschaft {community_id!r} "
                f"unter {community_dir} gefunden -- kein Vorlauf ohne vorhandene Community "
                "(kein automatischer Bootstrap durch diesen Dialog)."
            )
            return None
        available_personas = sorted(bootstrap.personas_written)
        self._print(
            f"Bestehende Spielgemeinschaft {community_id!r} -- verfuegbare freie KI-Personas: "
            f"{', '.join(available_personas)}"
        )
        return raw_community_id, community_id, available_personas

    def _bounded_preflight_select_personas(self, available: list[str]) -> list[str] | None:
        """Nur ausdruecklich genannte, tatsaechlich zur Community gehoerende
        Personas -- unbekannte/fremde/menschliche/leere Auswahl wird
        kontrolliert abgelehnt (11 §7 V2). `available` stammt bereits 1:1 aus
        `bootstrap.personas_written`, demselben Pool, den `lab.cli` selbst
        als gueltige Auswahl akzeptiert -- keine zweite Zuordnungslogik.

        R1-Nachzug (01_REVIEW_A23.md, 02_AUFTRAG_REST_A23.md §R1): `available`
        (`bootstrap.personas_written`) ist NUR Community-MITGLIEDSCHAFT, KEINE
        Aussage ueber frei/spielbereit -- eine gelistete Persona kann unfertig
        (Erschaffung nicht abgeschlossen), gerade nicht auflösbar (bekannter,
        aber nicht lesbarer Current) oder an einem Tisch/offenen Abschluss
        gebunden sein. Nach der reinen Mitgliedschaftspruefung (`unknown`
        oben) wird deshalb JEDE ausgewaehlte Persona zusaetzlich ueber
        DIESELBE bestehende Autoritaet wie jeder andere Spielstart aufgeloest
        (`self._resolve_member`, s. `_cmd_local_round`/`_cmd_lobby_initiative`)
        und auf bestehende Tisch-/Abschlussbindung geprueft (`core.store.
        chrononaut_active_binding`/`chrononaut_open_completion_order`,
        dieselben Leser wie `_cmd_import`). Der eigene menschliche Teilnehmer
        (`self.participant_id`) besitzt in dieser Community strukturell nie
        eine eigene KI-Stamm-Persona -- ein Treffer waere ohnehin schon durch
        `unknown` ausgeschlossen; die explizite Ablehnung hier haelt das
        trotzdem unmissverstaendlich fest, statt sich auf einen Seiteneffekt
        zu verlassen. KEINE neue Zweitautoritaet: nur vorhandene Leser, kein
        Lobby-Konstruktor mit Initialwrites, kein Ausweichen auf ein anderes
        Mitglied, keine Lock-Loeschung."""
        raw, control = self._readline_with_controls(
            f"KI-Personas (kommagetrennt, aus {', '.join(available)}): ", context="KI-Vorlauf-Personas",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("KI-Vorlauf abgebrochen (lokal verarbeitet, keine Persona-Auswahl, kein Vorlauf gestartet).")
            return None
        raw = raw.strip()
        requested = [p.strip() for p in raw.split(",") if p.strip()]
        if not requested:
            self._print("KI-Vorlauf: keine Persona ausgewaehlt -- kein Vorlauf gestartet.")
            return None
        selected = sorted(set(requested))
        unknown = [p for p in selected if p not in available]
        if unknown:
            self._print(
                f"KI-Vorlauf: unbekannte/nicht freie Personas {unknown} (verfuegbar: {available}) "
                "-- kein Vorlauf gestartet."
            )
            return None
        from ..core import store as core_store
        for pk in selected:
            if pk == self.participant_id:
                self._print(
                    f"KI-Vorlauf: {pk!r} ist der eigene menschliche Teilnehmer, keine KI-Persona -- "
                    "kein Vorlauf gestartet."
                )
                return None
            try:
                resolved = self._resolve_member(pk)
            except _ActiveSaveUnresolved:
                self._print(
                    f"KI-Vorlauf: Figur {pk!r} hat einen bekannten, gerade NICHT lesbaren Spielstand -- "
                    "nicht spielbereit, kein Vorlauf gestartet."
                )
                return None
            if resolved is None:
                self._print(
                    f"KI-Vorlauf: Figur {pk!r} ist noch nicht spielbereit (Erschaffung nicht "
                    "abgeschlossen) -- kein Vorlauf gestartet."
                )
                return None
            _active_save, chrononaut_id = resolved
            if self.run_dir is not None and (
                core_store.chrononaut_active_binding(self.run_dir, chrononaut_id)
                or core_store.chrononaut_open_completion_order(self.run_dir, chrononaut_id)
            ):
                self._print(
                    f"KI-Vorlauf: Figur {pk!r} ist an einem Tisch oder einem offenen Abschluss "
                    "gebunden -- kein Vorlauf gestartet."
                )
                return None
        return selected

    def _bounded_preflight_collect_budget(self) -> dict[str, float | int] | None:
        """Endliche Lauf-/Kosten-/Leerlauf-/Wallgrenzen -- validiert
        ausschliesslich ueber die BESTEHENDEN `lab.cli`-Typkonverter
        (`_positive_int`/`_finite_positive_float`, dieselbe NaN/Inf/0/
        negativ-Ablehnung wie der echte Controller), keine zweite
        Budgetlogik (A23 §2)."""
        import argparse
        from ..lab.cli import _finite_positive_float, _positive_int
        prompts = (
            ("max_requests", "Max. Requests (Turns) fuer diesen Vorlauf: ", _positive_int),
            ("max_seconds", "Max. Sekunden (aufsummierte Requestdauer): ", _finite_positive_float),
            ("max_usd", "Max. USD (synthetischer Tarif, beide Profile Pflicht): ", _finite_positive_float),
            ("max_idle_windows", "Max. aufeinanderfolgende Leerlauf-Fenster: ", _positive_int),
            ("max_wall_seconds", "Max. reale Wall-Sekunden (endliche Grenze): ", _finite_positive_float),
        )
        budget: dict[str, float | int] = {}
        for key, prompt, convert in prompts:
            raw, control = self._readline_with_controls(prompt, context="KI-Vorlauf-Budget")
            if control in ("zurueck", "abbrechen", "pause"):
                self._print("KI-Vorlauf abgebrochen (lokal verarbeitet, kein Budget uebernommen, kein Vorlauf gestartet).")
                return None
            raw = raw.strip()
            try:
                budget[key] = convert(raw)
            except argparse.ArgumentTypeError as e:
                self._print(f"KI-Vorlauf: ungueltige Budgetangabe fuer {key} ({e}) -- kein Vorlauf gestartet.")
                return None
        return budget

    def _bounded_preflight_dispatch_controller(self, argv: list[str], max_wall_seconds: float) -> None:
        """Ruft den EINEN vorhandenen gemeinsamen Dispatcher
        (`scripts/mmo_sim.py lab resume ...`, DERSELBE Einstieg wie
        `mmo_sim.lab.cli.main`) synchron als kontrollierten Kindprozess auf
        -- kein zweiter Controller, kein direkter `LabRunner`-Scheinlauf.
        Erbt die Umgebung des aufrufenden Prozesses unveraendert (keine
        neuen globalen Env-Werte), damit eine von aussen (Test-/Live-Setup)
        bereits konfigurierte Providerbindung fuer das Kind sichtbar bleibt.
        `max_wall_seconds` ist oben immer eine endliche Pflichtangabe -- der
        zusaetzliche Prozess-Timeout ist ein rein betriebssystemseitiges
        Sicherheitsnetz gegen einen haengenden Kindprozess, keine zweite
        Budgetautoritaet."""
        import subprocess
        import sys
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "scripts" / "mmo_sim.py"
        cmd = [sys.executable, "-B", str(script), *argv]
        self._print(f"KI-Vorlauf: starte gemeinsamen Lab-Controller als Kindprozess -- {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, cwd=str(repo_root), stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=max_wall_seconds + 60.0,
            )
        except subprocess.TimeoutExpired:
            self._print(
                "KI-Vorlauf: Controller-Kindprozess ueberschritt die Wall-Zeit-Grenze deutlich und "
                "wurde beendet -- kein Spielerfolg, moeglicher haengender Kindprozess."
            )
            return
        if result.stdout:
            self._print(result.stdout.rstrip("\n"))
        if result.stderr:
            self._print(result.stderr.rstrip("\n"))
        if result.returncode == 0:
            self._print(
                "KI-Vorlauf beendet (geordneter Stop/Budget/Leerlaufgrenze ueber den gemeinsamen "
                "Controller) -- eigener Chrononaut blieb ungespielt."
            )
        else:
            self._print(
                f"KI-Vorlauf: Controller-Kindprozess beendet mit exit={result.returncode} -- kein "
                "Spielerfolg, Konfigurationsfehler/Hold/Limit s. Ausgabe oben."
            )

    def _cmd_export(self) -> None:
        """F5/K11 (WEGKARTE §6): Export = der aktuell PUBLIZIERTE Save
        (`core.store.load_current_save_or_raise`), NICHT `onboarding.
        final_save` -- letzteres ist nur der Stand der ERSCHAFFUNG, veraltet
        sobald der Save ueber eine echte Runde weiterpubliziert wurde (Test
        10). Ohne konfigurierte Laufumgebung (run_dir/states_dir/
        schema_path) -- oder wenn (noch) gar kein Current-Save existiert --
        bleibt der Onboarding-Save der ehrliche Fallback (z.B. direkt nach
        Erschaffung, vor der ersten Runde).

        I4-Nachzug (Vertrag §3 A/B, R1c): ein BEKANNTER, gerade nicht
        lesbarer Current-Save darf NICHT heimlich durch den (moeglicherweise
        veralteten) Onboarding-Stand ersetzt und als 'Vollstaendiger Save'
        ausgegeben werden -- kontrollierter Abbruch OHNE Exportdatei statt
        einer irrefuehrenden Ausgabe."""
        state = onboarding.start_or_resume(self.onboarding_dir, self.participant_id)
        current_save = None
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            try:
                current_save = core_store.load_current_save_or_raise(
                    self.run_dir, self.participant_id, ps_store, states_dir=self.states_dir,
                )
            except core_store.CurrentSaveUnavailableError:
                self._print(
                    "Export abgebrochen: der aktuell veroeffentlichte Spielstand ist gerade nicht "
                    "lesbar — kein Export einer moeglicherweise veralteten Fassung (spaeter erneut "
                    "versuchen)."
                )
                return
        save_to_export = current_save if current_save is not None else state.final_save
        if save_to_export is None:
            self._print("Kein gueltiger Spielstand vorhanden — Verlauf ggf. gesichert, aber kein exportierbarer Save.")
            return
        text = import_export.export_save_text(save_to_export)
        self._print("Vollstaendiger Save (Text zum manuellen Kopieren):")
        self._print(text)
        # I3: "besitzt keinen verbundenen Dateiexport" -- jetzt ZUSAETZLICH
        # eine eigenstaendige Exportdatei schreiben (kein Harness-Wrapper).
        try:
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            export_path = self.exports_dir / f"{self.participant_id.replace('/', '_')}.json"
            export_path.write_text(text, encoding="utf-8")
            self._print(f"Zusaetzlich als Datei gespeichert: {export_path}")
        except OSError as e:
            self._print(f"Datei-Export fehlgeschlagen (Text oben bleibt gueltig): {e}")

    def _resolve_active_save(
        self, persona_key: str, onboarding_final_save: dict | None,
    ) -> tuple[dict | None, bool]:
        """A7/D1 (WEGKARTE §8, Plan-Critic A7, Tests 05/06): EINHEITLICHE
        Autoritaet fuer den 'aktuellen' Save eines Teilnehmers -- IMMER
        zuerst der real veroeffentlichte Stand; NUR wenn dafuer (noch) KEINE
        Version existiert (z.B. direkt nach Erschaffung, vor der ersten
        Runde/Publikation) faellt dies auf den reinen Onboarding-Stand
        zurueck. `onboarding.final_save` ist NACH Fortschritt KEINE
        konkurrierende Current-Autoritaet mehr (Muster von `_cmd_export`
        uebernommen, nicht neu erfunden) -- `_cmd_import`s Konfliktbasis UND
        `_cmd_local_round`s Spielstart verwenden jetzt DIESELBE Funktion.

        I4-Nachzug (Vertrag §3 A/B, R1): verwendet `core.store.load_current_
        save_or_raise` statt des fehlertoleranten `load_current_save` --
        liefert `(save, unresolved)`. `unresolved=True` heisst, ein
        BEKANNTER, bereits veroeffentlichter Current-Save konnte gerade
        NICHT gelesen werden (`store.CurrentSaveUnavailableError`); der
        Aufrufer MUSS diesen Fall kontrolliert ablehnen, statt den
        (moeglicherweise veralteten) Onboarding-Stand als Ersatz zu
        verwenden -- eine anfangs fehlgeschlagene Lektuere darf keine
        Entscheidung auf Basis der alten Fassung festschreiben."""
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            try:
                current = core_store.load_current_save_or_raise(
                    self.run_dir, persona_key, ps_store, states_dir=self.states_dir,
                )
            except core_store.CurrentSaveUnavailableError:
                return None, True
            # R-SCF-A (02_SAVEVERTRAG.md §D "naechster Abschnitt startet
            # ueber den Kompatibilitaetsladeweg ... VOR davon abhaengigen
            # Spielaktionen"): schliesst die in GAPS.md/review/INTAKE.md
            # dokumentierte Luecke -- bisher wurde ein noch nicht
            # adoptierter Kompatibilitaetsumschlag (s. `core.save_correction.
            # _write_compat_export_on_exhaustion`) von keinem Consumer je
            # wieder aufgegriffen. Bewusst VOR dem `current`-Rueckfall
            # geprueft (nicht nur, wenn `current is None`): ein kanonischer
            # Current wird NUR beim allerersten Veroeffentlichen (Ende der
            # Erschaffung, `_finish_new_character_creation`) geschrieben und
            # bleibt danach UNVERAENDERT, solange ein SPAETERER Abschnitt am
            # Budget scheitert -- ein reiner `current is None`-Gate wuerde
            # den dabei entstandenen (neueren) Kompatibilitaetsstand nie
            # erreichen und den Spielerfortschritt dieses Abschnitts still
            # unter den Tisch fallen lassen (genau der "stille Schwund",
            # den 02_SAVEVERTRAG verbietet). Ohne vorhandenen Umschlag (der
            # ueberwiegende bestehende Fall, inkl. JEDER bestehenden
            # Regression -- `_find_latest_pending_compat_export` liefert
            # dann `None`) ist dieser Zweig ein reiner No-Op, identisches
            # Verhalten zu vorher; ein bereits ADOPTIERTER Umschlag liefert
            # idempotent denselben, laengst im Store stehenden Block
            # zurueck (kein Doppel-Publish, s. `attempt_compat_load`-
            # Restart-Sicherheit); ein (noch) nicht reparierbarer Umschlag
            # (`status="hold"`) laesst den bisherigen `current`/
            # `onboarding_final_save`-Rueckfall unten unveraendert
            # bestehen ("App bleibt benutzbar, letzter valider Stand
            # bleibt erhalten", 02.D).
            compat_block = self._apply_pending_compat_load(persona_key)
            if compat_block is not None:
                return compat_block, False
            if current is not None:
                return current, False
        return onboarding_final_save, False

    def _find_latest_pending_compat_export(self, persona_key: str) -> dict | None:
        """R-SCF-A (02_SAVEVERTRAG.md §D): reiner Lesescan von `run_dir/
        save_compat/*/<version>.json` (additive Ablage, s. `core.
        save_correction._write_compat_export_on_exhaustion`) nach dem
        NEUESTEN Umschlag fuer GENAU `persona_key` -- unabhaengig davon, ob
        der schreibende Aufrufer die Einzelfigur-Ableitung
        (`creation_repair_key`, Erschaffungsweg) oder die Gruppen-Ableitung
        (`group_repair_key`, normaler `!save`/Fuenfer-Ernte-Weg am
        Abschnittsende) verwendet hat -- BEIDE schreiben `participant_id`/
        `char_id`/`repair_key` bereits als Teil des Umschlags selbst (s.
        `domain.zeitriss.save_compatibility.build_compat_envelope`), diese
        Funktion muss daher KEINE der beiden Ableitungsformeln kennen/neu
        nachbauen. Deckt insbesondere den Fall ab, dass eine Erschaffung nie
        erfolgreich abgeschlossen wurde (`onboarding_final_save is None`,
        also auch KEIN `char_id` ueber den Onboarding-Stand verfuegbar) --
        der Umschlag selbst traegt seine eigene `char_id`. Kein Write, keine
        Rekursion (nur zwei Verzeichnisebenen), bounded durch die Anzahl
        tatsaechlich vorhandener Kompatibilitaetsexporte."""
        import json

        base = Path(self.run_dir) / "save_compat"
        if not base.is_dir():
            return None
        best: dict | None = None
        for repair_dir in sorted(base.iterdir()):
            if not repair_dir.is_dir():
                continue
            versions = sorted(
                (p for p in repair_dir.glob("*.json") if p.stem.isdigit()), key=lambda p: int(p.stem),
            )
            if not versions:
                continue
            try:
                data = json.loads(versions[-1].read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict) or data.get("participant_id") != persona_key:
                continue
            if best is None or (data.get("created_ts") or 0) >= (best.get("created_ts") or 0):
                best = data
        return best

    def _apply_pending_compat_load(self, persona_key: str) -> dict | None:
        """R-SCF-A (02_SAVEVERTRAG.md §D): treibt den bereits vorhandenen,
        bounded Kompatibilitaetsladeweg (`core.save_compatibility.
        attempt_compat_load`) fuer `persona_key` an, WENN (und nur wenn)
        `_find_latest_pending_compat_export` einen noch nicht adoptierten
        Kompatibilitaetsumschlag findet. `repair_key`/`char_id` kommen
        DIREKT aus dem gefundenen Umschlag (NIE neu berechnet) -- derselbe
        Bindungsschluessel, unter dem der jeweilige Schreiber (Einzelfigur-
        ODER Gruppenpfad) den Export tatsaechlich angelegt hat. Liefert den
        kanonisch uebernommenen Block bei Erfolg, sonst `None` (kein
        Umschlag vorhanden ODER Reparatur innerhalb des bounded Budgets
        nicht moeglich -- der Aufrufer faellt in BEIDEN Faellen unveraendert
        auf den bisherigen `onboarding_final_save`-Pfad zurueck, kein neuer
        Fehlerzustand).

        R-SCF-A (ZR-SCF-HYBRID-DURCHSTICH-20261017-R1, Fix A): die
        `repair_fn` kommt jetzt von `core.compat_load_service.
        build_compat_repair_fn` -- sie versucht ZUERST weiterhin dieselbe
        lokale, wertgleiche Wallet-Projektion (02.B, kein Modellaufruf,
        unveraendertes Verhalten fuer jede bestehende Wallet-Regression),
        erreicht bei anderen behebbaren Strukturfehlern aber zusaetzlich
        die TATSAECHLICH konfigurierte SL (`self.gm_transport_factory`,
        exakt dieselbe Konstruktion wie fuer jeden anderen echten GM-Turn
        in dieser Klasse) -- derselbe fachliche Ladevertrag fuer die
        normale TUI UND den Headless-/Hybridpfad (beide konstruieren ihren
        `gm_transport` ueber dieselbe Factory). Ohne konfigurierte
        Laufumgebung/SL-Anbindung (`gm_transport_factory is None`, z.B.
        dieses Offline-Paket ohne Env) bleibt `gm_transport=None` -- die
        Fabrik liefert dann eine Funktion, die NUR noch die Wallet-
        Projektion versucht (identisches Verhalten zur alten
        `_offline_repair`, kein stiller Versuch, eine nicht konfigurierte
        SL anzusprechen)."""
        from ..core import compat_load_service
        from ..core import save_compatibility as save_compat_core

        envelope = self._find_latest_pending_compat_export(persona_key)
        if envelope is None:
            return None
        repair_key = envelope.get("repair_key")
        char_id = envelope.get("char_id")
        if not repair_key or not char_id:
            return None

        gm_transport = None
        if self.gm_transport_factory is not None:
            import inspect

            accepts_arg = len(inspect.signature(self.gm_transport_factory).parameters) >= 1
            table_id = envelope.get("table_id") or f"compat-load-{persona_key}"
            gm_transport = (
                self.gm_transport_factory(table_id) if accepts_arg else self.gm_transport_factory()
            )

        repair_fn = compat_load_service.build_compat_repair_fn(
            self.run_dir, repair_key=repair_key, char_id=char_id, participant_id=persona_key,
            gm_transport=gm_transport, table_id=envelope.get("table_id"), section_id=envelope.get("section_id"),
        )

        outcome = save_compat_core.attempt_compat_load(
            self.run_dir, repair_key=repair_key, char_id=char_id, participant_id=persona_key,
            states_dir=self.states_dir, schema_path=self.schema_path, envelope=envelope,
            repair_fn=repair_fn,
        )
        if outcome.status == "adopted":
            self._print(
                f"Kompatibilitaetsladeweg: Spielstand fuer {char_id} aus dem Kompatibilitaetsstand "
                "repariert und uebernommen (02_SAVEVERTRAG.md §D)."
            )
            return outcome.block
        if outcome.status == "hold":
            self._print(
                "Kompatibilitaetsladeweg: Spielstand bleibt im gesicherten Kompatibilitaetsstand "
                f"(Grund: {outcome.reason or 'offene Pruefhinweise'}) -- App bleibt benutzbar, "
                "kein automatischer Neustart."
            )
        return None

    def _own_system_context(self, persona_key: str) -> str:
        """D3/A7 (K7, WEGKARTE §6, PLAN-CRITIC-ABSCHLUSS.md HINWEIS):
        gemeinsamer Context-Builder -- baut den `system`-Kontext ueber die
        bereits vorhandene `PersonaStateStore.render_for_prompt` (nicht neu
        gebaut). Ohne konfigurierte Laufumgebung ODER ohne existierenden
        State (z.B. eine Persona, die noch nicht importiert hat) bleibt der
        Kontext ein leerer String -- kein Absturz, kein erfundener Inhalt.

        K3-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 B, REVIEW-LOBBY.md
        §5): `render_for_prompt` traegt jetzt bereits das gepinnte Profil/
        den Spielstil (persona_state.py-Nachzug) -- zusaetzlich haengt
        dieser gemeinsame Builder den gueltigen VOLLSTAENDIGEN eigenen
        Current (ueber DIESELBE Autoritaet `_resolve_active_save` wie jeder
        Spielstart) an, sofern einer bereits veroeffentlicht/bekannt ist --
        ohne bekannten Current (z.B. noch nie ein Abschnitt gespielt) bleibt
        dieser Teil einfach leer, kein erfundener Platzhalter. Ein GERADE
        NICHT lesbarer bekannter Current (`_ActiveSaveUnresolved`) macht den
        Kontext NICHT unsicher-blind -- er bleibt dann ohne Current-Zeile
        (derselbe Aufrufer, der diesen Kontext fuer eine Reservierung nutzt,
        prueft Save-Lesbarkeit vor einem echten Tischstart ohnehin separat
        ueber `_resolve_member`).

        R3.1-Nachzug (REVIEW-LOBBY.md §5.1, MAIN-DATENWEGENTSCHEIDUNG.md C):
        VORHER haengte dieser Builder trotz Docstring-Versprechen NUR
        `current.get('save_id')` an -- der eigene Inventarinhalt/die
        eigenen Charakterdaten erreichten die Lobbyentscheidung NICHT (Probe
        07: nur `save_id` im tatsaechlichen API-Wire-Body, das Inventar
        fehlte). Jetzt wird der GESAMTE geladene eigene Current-Datensatz
        (dieselbe, bereits streng gelesene `current`-Struktur -- kein neuer
        I4-Storeumbau, kein zweiter Leser) als JSON angehaengt. `current`
        ist ausschliesslich der EIGENE Spielstand von `persona_key` (ueber
        `_resolve_active_save(persona_key, ...)`) -- fremde Privatreflex-
        ionen/Fremdtische/Operator-/Devdaten sind darin strukturell nicht
        enthalten (kein zusaetzlicher Filter noetig)."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            return ""
        from ..core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=self.schema_path)
        try:
            state = ps_store.load_state(persona_key, states_dir=self.states_dir)
        except FileNotFoundError:
            return ""
        text = ps_store.render_for_prompt(state)
        current, unresolved = self._resolve_active_save(persona_key, None)
        if not unresolved and current is not None and isinstance(current, dict):
            text = (
                f"{text}\nEigener aktueller Spielstand (Current, vollstaendig): "
                f"{json.dumps(current, ensure_ascii=False, sort_keys=True)}"
            )
        return text

    def _append_invitation_log(self, record: dict) -> None:
        """W1 (F..., "Angebot+Antworten VOR Tischanlage festhalten"):
        append-only Nachweislog fuer Angebote und Teilnehmerantworten,
        real auf Platte, unabhaengig vom Tischausgang. Ohne konfigurierte
        Laufumgebung (Offline-Default ohne `run_dir`) bleibt dies ein
        No-op -- kein Absturz, kein erfundenes Verzeichnis.

        01_AUFTRAG_LOBBY_INITIATIVE.md §4 A ("kleiner wiederverwendbarer
        Dienst zwischen UI und bestehenden Primitiven"): delegiert an
        `core.lobby_service.append_offer_log_record` -- IDENTISCHES
        Dateiformat/-name wie zuvor, jetzt auch von `_cmd_lobby_initiative`
        genutzt (keine zweite Offer-Log-Implementierung)."""
        from ..core import lobby_service
        lobby_service.append_offer_log_record(self.run_dir, record)

    def _resolve_member(self, pid: str) -> tuple[dict, str] | None:
        """Liefert `(active_save, chrononaut_id)` fuer einen beliebigen
        Teilnehmer (Leader ODER Gast) — dieselbe Autoritaet (A7/D1) fuer
        alle Rollen. Extrahiert aus `_cmd_local_round` (vorher lokale
        Closure) -- jetzt auch von `_cmd_lobby_initiative` genutzt (01_AUFTRAG
        §4 A: derselbe Aufloesungsweg fuer beide Lobby-Wege, keine zweite
        Kopie der Save-/Chrononaut-Autoritaet).

        I4-Nachzug (Vertrag §3 A/B, R1b): wirft `_ActiveSaveUnresolved`,
        wenn `_resolve_active_save` einen bekannten, gerade nicht
        lesbaren Current-Save meldet -- der Aufrufer MUSS den
        Spielstart dann kontrolliert ablehnen, statt den (moeglicherweise
        veralteten) `member_state.final_save` an die SL zu senden."""
        member_state = onboarding.peek(self.onboarding_dir, pid)
        if member_state is None or member_state.final_save is None:
            return None
        member_active_save, unresolved = self._resolve_active_save(pid, member_state.final_save)
        if unresolved:
            raise _ActiveSaveUnresolved(pid)
        member_chrono_id = zeitriss_saves.block_char_id(member_active_save)
        if member_chrono_id is None:
            return None
        return member_active_save, member_chrono_id

    def _local_round_registry_dir(self) -> Path:
        """A24 R2 (02 §Auftrag R2: 'ueber die VORHANDENE Registry
        registrieren', '... keine zweite Personen-/Katalogdatenwelt').
        `TuiSession.__init__` ist nicht im A24-SCOPE änderbar, bekommt also
        keinen eigenen `registry_dir`-Parameter -- derselbe Ableitungsstil
        wie der bestehende `exports_dir`-Default (`self.onboarding_dir.
        parent / "exports"`) liefert denselben Pfad, den bestehende
        Testfixtures (`_a24_local_support.py: register_human`) ohnehin unter
        `<data-dir>/registry` anlegen."""
        return self.onboarding_dir.parent / "registry"

    def _local_round_list_humans(self) -> list[tuple[str, str]]:
        """Liest die VORHANDENE `ParticipantRegistry`-Dateiablage direkt
        (keine zweite Speicherwelt, kein neuer Store) und liefert alle
        bereits registrierten menschlichen Teilnehmer sichtbar als
        (participant_id, display_name)."""
        registry_dir = self._local_round_registry_dir()
        out: list[tuple[str, str]] = []
        if registry_dir.exists():
            for p in sorted(registry_dir.glob("participant__*.json")):
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if data.get("kind") == "human":
                    out.append((data["participant_id"], data.get("display_name", data["participant_id"])))
        return out

    def _local_round_select_humans(self) -> list[str] | None:
        """A24 R2 (11 §8 'mehrere Menschen an diesem Geraet'): vorhandene
        lokale menschliche Teilnehmer sichtbar auswaehlen ODER nach
        bewusster Eingabe ueber die vorhandene Registry neu registrieren.
        Liefert `None` bei Abbruch/EOF (klarer Rueckweg, keine Aenderung)."""
        from ..registry.participants import ParticipantRegistry

        known = self._local_round_list_humans()
        self._print("Vorhandene lokale Teilnehmer:")
        # R7 (T-Befund 2/4, UX02/03, Korrekturzyklus 1) -- GEPRUEFT, NICHT
        # UMGESETZT: ein Versuch, hier bei registriertem Anzeigenamen den
        # Namen VOR der ID zu zeigen, wurde wieder entfernt -- mehrere
        # Funktionen in `test_a24_local_two_humans_2026_10_01.py` pruefen
        # diese Zeile exakt mit der rohen ID an erster Stelle (abhaengig
        # vom jeweiligen Testszenario registriert/unregistriert), ein
        # einzelner Fix haette einen Teil dieser real-subprocess-Szenarien
        # bestehen lassen und einen anderen (`test_a24_guided_setup_g_path_
        # human_leader_with_handoff`) brechen. Bleibt ehrlich dokumentierter
        # Blocker (s. WORKER2-REPORT.md) statt einer riskanten Breitenaenderung
        # an einer grossen, bereits bestehenden Testdatei ausserhalb des
        # verfuegbaren Zeit-/Risikobudgets dieses Korrekturzyklus.
        self._print(f"  [0] {self.participant_id} (du, aufrufender Teilnehmer)")
        others = [(pid, name) for pid, name in known if pid != self.participant_id]
        for idx, (pid, name) in enumerate(others, start=1):
            self._print(f"  [{idx}] {pid} ({name})")
        # G02 (02 §C "Wesentliche Unterdialoge duerfen den zentralen Helper
        # nicht umgehen"): `_readline_with_controls` statt rohem `_readline`
        # -- '?'/'/hilfe' zeigen hier Kontexthilfe, '/abbrechen'/'/zurueck'/
        # '/pause' brechen kontrolliert ab, ohne die vorhandene Nummern-/
        # 'neu:'-Syntax oder die oben gezeigte Teilnehmerliste zu aendern.
        try:
            raw, control = self._readline_with_controls(
                "Weitere Menschen an diesem Geraet -- vorhandene Nummern kommagetrennt "
                "ODER 'neu:<Anzeigename>' fuer eine bewusste Neuregistrierung, leer = nur du: ",
                context="Weitere Menschen waehlen",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return None
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Einrichtung abgebrochen -- kein Spielstart, keine Aenderung.")
            return None
        raw = raw.strip()
        selected = [self.participant_id]
        if not raw:
            return selected
        registry = ParticipantRegistry(self._local_round_registry_dir())
        for tok in (t.strip() for t in raw.split(",") if t.strip()):
            if tok.startswith("neu:"):
                display = tok.split(":", 1)[1].strip() or "Mensch"
                new_p = registry.register_participant(kind="human", display_name=display)
                self._print(f"Neu registriert: {new_p.participant_id} ({display})")
                if new_p.participant_id not in selected:
                    selected.append(new_p.participant_id)
                continue
            if not tok.isdigit() or not (1 <= int(tok) <= len(others)):
                self._print(f"Einrichtung abgebrochen: ungueltige Auswahl {tok!r}.")
                return None
            pid, _name = others[int(tok) - 1]
            if pid not in selected:
                selected.append(pid)
        return selected

    def _local_round_connect_new_person_to_own_figure(self, pid: str) -> tuple[dict, str] | None:
        """Q04 (REVIEW.md R02, 05.10.2026, vormals ':2676-2774'): eine
        WAEHREND der Rundenzusammenstellung neu registrierte Person
        (`neu:<Name>` in `_local_round_select_humans`) hat noch keine
        Figur. Vorher brach `_local_round_confirm_figure` die GESAMTE
        Einrichtung hier ab und verlangte einen separaten Teilnehmer-
        durchgang samt erneuter Einrichtung (General-Repro Q04: 'registriert
        neu:Ben, bricht bei dessen fehlender Figur aber ab'). Jetzt wird
        GENAU der vorhandene Registrierungs-/Fokus-/Katalog-/Importweg
        verbunden: Fokusbestaetigung (`_local_round_handoff`, dieselbe
        Methode, die auch sonst die Terminaluebergabe bestaetigt) -> die
        bestehende Erschaffungs-/Import-/Export-Flaeche (`_cmd_menu_
        charaktere`) UNTER DER ID `pid` -> Rueckkehr zur Besetzung.

        Keine zweite Profilautoritaet, kein Liveanbieterassistent: die
        Erschaffung laeuft ueber eine ZWEITE `TuiSession`-Instanz mit
        EXAKT derselben Laufumgebung (gleicher `run_dir`/`catalog_dir`/
        `onboarding_dir`/`states_dir`/`schema_path`/`gm_transport_factory`/
        `persona_driver_factory`) und demselben Terminal (identische
        `_input`/`_print`) -- nur `participant_id` unterscheidet sich
        (`pid` statt `self.participant_id`). Exakt dasselbe Muster, mit dem
        bereits mehrere echte Menschen am selben Geraet je eine eigene
        `TuiSession` erhalten (s. `_a24_local_support.py`/die G03/P09-
        Mehrprozessbelege) -- keine neue Erschaffungs-/Katalogimplementierung.
        Lehnt die Person die Fokusuebergabe ab (Abbruch/EOF/Steuerzeile),
        bleibt dies ein klarer Rueckweg (kein KI-Ersatz, keine Dummyfigur);
        der Aufrufer behandelt `None` unveraendert als 'keine Figur'."""
        if not self._local_round_handoff(pid):
            return None
        sub_session = TuiSession(
            self.onboarding_dir, self.catalog_dir, pid,
            input_fn=self._input, print_fn=self._print,
            run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
            gm_transport_factory=self.gm_transport_factory,
            exports_dir=self.exports_dir, persona_driver_factory=self.persona_driver_factory,
        )
        sub_session._cmd_menu_charaktere()
        try:
            return self._resolve_member(pid)
        except _ActiveSaveUnresolved:
            return None

    def _local_round_confirm_figure(self, pid: str) -> bool:
        """A24 R2 (02 §Auftrag R2 'eigene Figur pro Mensch aus vorhandenen
        Zuordnungen zeigen und ausdruecklich bestaetigen'): nutzt dieselbe
        Autoritaet wie der eigentliche Spielstart (`_resolve_member`, kein
        zweiter Aufloesungsweg).

        Q04-Fix (REVIEW.md R02, 05.10.2026): eine fehlende Figur fuehrt
        NICHT mehr sofort zum Abbruch der gesamten Rundeneinrichtung --
        `_local_round_connect_new_person_to_own_figure` verbindet zuerst den
        vorhandenen Fokus-/Erschaffungs-/Importweg UNTER `pid`s eigener ID
        (kein KI-Ersatz, keine Dummyfigur, kein manuell editiertes JSON).
        Bleibt danach immer noch keine Figur vorhanden (abgebrochen/EOF/
        nicht fertiggestellt), bleibt der bisherige klare Rueckweg unveraendert
        bestehen."""
        try:
            resolved = self._resolve_member(pid)
        except _ActiveSaveUnresolved:
            self._print(
                f"'{pid}': der aktuell veroeffentlichte Spielstand ist gerade nicht lesbar -- "
                "kein Spielstart, bis die tatsaechliche Autoritaet geklaert ist."
            )
            return False
        if resolved is None:
            resolved = self._local_round_connect_new_person_to_own_figure(pid)
        if resolved is None:
            self._print(
                f"'{pid}' hat noch keine abgeschlossene Figur. Keine Dummyfigur und keine "
                "Uebernahme eines fremden Currents -- bitte zuerst im eigenen "
                "Teilnehmer-Durchgang ([n] neu erschaffen oder [i] importieren) eine Figur "
                "fertigstellen, danach die lokale Runde erneut einrichten (klarer Rueckweg)."
            )
            return False
        _save, chrono_id = resolved
        from ..adapters.base import human_menu_decision

        # G02 (02 §C): zentraler Helper statt rohem `_readline` -- '?'/
        # '/hilfe' zeigen Kontexthilfe, Steuerzeilen gelten hier als
        # Nicht-Bestaetigung (derselbe klare Rueckweg wie 'n').
        try:
            answer, control = self._readline_with_controls(
                f"'{pid}' spielt '{chrono_id}' -- bestaetigen? [j/n]: ",
                context="Figur bestaetigen",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return False
        if control in ("zurueck", "abbrechen", "pause"):
            self._print(f"Einrichtung abgebrochen: '{pid}' hat die Figur '{chrono_id}' nicht bestaetigt.")
            return False
        decision, _explanation = human_menu_decision(answer)
        if decision != "accept":
            self._print(f"Einrichtung abgebrochen: '{pid}' hat die Figur '{chrono_id}' nicht bestaetigt.")
            return False
        return True

    def _known_ai_overview(self) -> list[tuple[str, str]]:
        """UX10 (02 §D.4, REVIEW.md §G01: 'zeigt tatsaechlich bekannte,
        passende Bestandseintraege mit lesbaren Namen und Herkunft, statt
        eine freie Persona-ID als einzigen Weg zu verlangen'): liefert
        `(persona_key, lesbares_label)` fuer die EIGENE, bereits bestaetigte
        Spielgemeinschaft dieses Teilnehmers (`community-<participant_id>`,
        dieselbe deterministische ID wie `_cmd_community`/
        `_bounded_preflight_lookup_community` -- kein Raten, keine zweite
        Communityzuordnung).

        AUSSCHLIESSLICH reine Lesefunktionen (`community_bootstrap.peek`,
        `PersonaStateStore.load_state`, `_read_live_adoption_origin`) -- 0
        Persona-/GM-Calls, kein Bootstrap, keine neue Population (UX03/
        UX10: 'Ansehen = 0 Calls', 'Neustart = keine neue Population').
        Ohne konfigurierte Laufumgebung oder ohne bestehende Community
        bleibt die Liste leer -- KEIN impliziter Bootstrap, kein Fallback
        auf eine erfundene Population."""
        if self.run_dir is None:
            return []
        from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap

        community_id = f"community-{self.participant_id}"
        community_dir = self.run_dir / "community"
        bootstrap = peek_bootstrap(community_dir, community_id)
        if bootstrap is None or not bootstrap.personas_written:
            return []
        origin = self._read_live_adoption_origin(community_dir, community_id)
        origin_label = {
            "demo": "Herkunft: demo/SIMULIERT", "production": "Herkunft: production/PRODUKTIV",
        }.get(origin, "Herkunft: nicht gepinnt (SIMULIERT/DEMO-Standard)")
        ps_store = None
        if self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            ps_store = PersonaStateStore(schema_path=self.schema_path)
        overview: list[tuple[str, str]] = []
        for pk in sorted(bootstrap.personas_written):
            archetype = None
            if ps_store is not None:
                try:
                    state = ps_store.load_state(pk, states_dir=self.states_dir)
                except (FileNotFoundError, OSError, ValueError):
                    state = None
                if isinstance(state, dict):
                    archetype = state.get("archetype") or None
            label = f"{archetype} ({origin_label})" if archetype else origin_label
            overview.append((pk, label))
        return overview

    def _resolve_known_ai_tokens(self, tokens: list[str], overview: list[tuple[str, str]]) -> list[str]:
        """Q03 (REVIEW.md R02, 05.10.2026, vormals ':2782-2878'): loest die
        normale Namens-/Nummernwahl aus der angezeigten Bestandsuebersicht
        (`overview`, 1-basierter Anzeigeindex) tatsaechlich in die
        vorhandene autoritative Persona-ID (`pk`) auf -- Testeingabe '1'
        waehlt jetzt wirklich den ersten angezeigten Eintrag statt des
        rohen, bedeutungslosen Tokens '1' (General-Repro Q03: 'die
        Testeingabe 1 bleibt Token 1, nicht eine Auswahl aus dem Bestand').

        Reihenfolge je Token: (1) Anzeigeindex (`1`..`len(overview)`), (2)
        exakte technische ID (`pk`, unveraendert gueltiger Experten-/
        Kompatibilitaetsalias -- 02 §D.4: 'freie ID darf optional fuer
        Experten bleiben', kein Pflichtwissen mehr), (3) angezeigter Name
        case-insensitiv (`pk`, das in dieser Liste bereits der angezeigte
        Name ist) -- NICHT die mehrwortige Archetyp-/Herkunftsbeschreibung
        hinter dem Gedankenstrich, da das bestehende leerzeichengetrennte
        Mehrfachauswahlformat ('Persona-IDs, leerzeichengetrennt') einen
        mehrwortigen Namen ohne neue Anfuehrungszeichen-/Escapingsyntax
        nicht eindeutig von einer zweiten Auswahl trennen koennte (keine
        neue Eingabesyntax). Eine echte `pk`-Dublette ist strukturell nicht
        moeglich (eindeutiger dict-Schluessel); die Anzeige nennt den Index
        trotzdem je Zeile (s. `_local_round_select_ai`), falls zwei Zeilen
        zufaellig denselben sichtbaren Text tragen. Jedes andere Token
        (weder Index noch bekannte ID) bleibt UNVERAENDERT durchgereicht:
        keine neue Auswahlautoritaet, keine neue Sperre fuer eine freie
        Persona-ID ausserhalb der eigenen angezeigten Gemeinschaft."""
        known_ids = {pk for pk, _label in overview}
        name_hits: dict[str, list[str]] = {}
        for pk, _label in overview:
            name_hits.setdefault(pk.casefold(), []).append(pk)
        resolved: list[str] = []
        for tok in tokens:
            if tok.isdigit() and 1 <= int(tok) <= len(overview):
                resolved.append(overview[int(tok) - 1][0])
                continue
            if tok in known_ids:
                resolved.append(tok)
                continue
            matches = name_hits.get(tok.casefold())
            if matches is not None and len(matches) == 1:
                resolved.append(matches[0])
                continue
            resolved.append(tok)
        return resolved

    def _local_round_select_ai(self) -> list[str] | None:
        """A24 R2: ausgewaehlte KI-Personas fuer die lokale Runde (eigene
        Erschaffungs-/Zustimmungslogik bleibt unveraendert in
        `_cmd_local_round` -- diese Auswahl ist noch KEINE KI-Zustimmung).

        UX10-Fix (02 §D.4, REVIEW.md §G01): zeigt VOR der Eingabe die
        tatsaechlich bekannten KI-Personas der eigenen Spielgemeinschaft
        namentlich mit Herkunft (`_known_ai_overview`, reine Lesefunktion,
        0 Calls) -- die freie Persona-ID-Eingabe bleibt zusaetzlich als
        Expertenweg moeglich (02 §D.4: 'freie ID darf optional fuer
        Experten bleiben').

        Q03-Fix (REVIEW.md R02, 05.10.2026): JEDE Zeile der angezeigten
        Uebersicht nennt jetzt zusaetzlich ihren 1-basierten Auswahlindex
        ('[<i>] <pk> — <label>') -- bei gleichlautenden Namen (Dubletten)
        ist der Index damit immer eindeutig verfuegbar. Die eingegebenen
        Tokens werden ueber `_resolve_known_ai_tokens` in die tatsaechliche
        autoritative Persona-ID aufgeloest, BEVOR sie an `_cmd_local_round`
        weitergereicht werden -- 'Auswahl per ID' ist damit nicht mehr die
        einzig funktionierende Eingabeform, Index/Name funktionieren jetzt
        genauso. Unveraendertes grundlegendes Eingabeformat (leerzeichen-
        getrennte Tokens, leer = keine) -- bestehende Skripttests, die hier
        direkt eine gueltige ID liefern, bleiben unveraendert gueltig (exakte
        ID-Treffer werden 1:1 durchgereicht).

        G02 (02 §C): nutzt `_readline_with_controls`, damit '?'/'/hilfe' an
        dieser Stelle hilft statt die Einrichtung abzubrechen."""
        overview = self._known_ai_overview()
        if overview:
            self._print("Bekannte KI-Mitspieler (aus deiner Spielgemeinschaft, namensgefuehrt):")
            for idx, (pk, label) in enumerate(overview, start=1):
                self._print(f"  [{idx}] {pk} — {label}")
            self._print(
                "(Auswahl per Nummer ODER Name aus dieser Liste, leerzeichengetrennt -- die "
                "technische ID bleibt zusaetzlich als Experten-/Kompatibilitaetsweg moeglich; "
                "Ansehen allein loest keine Einladung/keinen Modellaufruf aus; eine freie "
                "Persona-ID bleibt ausserdem moeglich.)"
            )
        else:
            self._print(
                "Keine eigene KI-Spielgemeinschaft bekannt -- optional ueber 'Spielen > Meine "
                "KI-Spielgemeinschaft' anlegen; eine freie Persona-ID bleibt hier trotzdem moeglich."
            )
        try:
            raw, control = self._readline_with_controls(
                "KI-Mitspieler (Nummer/Name aus der Liste oder Persona-ID, leerzeichengetrennt, "
                "leer = keine): ",
                context="KI-Mitspieler waehlen",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return None
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Einrichtung abgebrochen -- kein Spielstart, keine Aenderung.")
            return None
        raw = raw.strip()
        tokens = [t for t in raw.split() if t]
        return self._resolve_known_ai_tokens(tokens, overview)

    def _local_round_select_leader(self, ai_tokens: list[str]) -> str | None:
        """A24 R2 (02 §Auftrag R2 'angefragten Leader (Human A oder
        angefragte tech)'): Leader ist entweder der aufrufende Mensch selbst
        oder eine der bereits ausgewaehlten KI-Personas -- kein freies
        Leaderwechselmenue, keine andere Person als Leader waehlbar.

        G02 (02 §C): nutzt `_readline_with_controls`."""
        try:
            raw, control = self._readline_with_controls(
                f"Leader dieser Runde -- [du] = {self.participant_id} oder eine der "
                f"angefragten KI-IDs {ai_tokens}: ",
                context="Leader waehlen",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return None
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Einrichtung abgebrochen -- kein Spielstart, keine Aenderung.")
            return None
        raw = raw.strip()
        if raw in ("", "du", self.participant_id):
            return self.participant_id
        if raw in ai_tokens:
            return raw
        self._print(f"Einrichtung abgebrochen: '{raw}' ist kein gueltiger Leader (weder du noch angefragte KI).")
        return None

    def _local_round_build_tokens(self, human_ids: list[str], ai_tokens: list[str], leader_choice: str) -> list[str]:
        """Baut ausschliesslich die `guest_tokens`-Parameterliste fuer den
        UNVERAENDERTEN `_cmd_local_round`-Aufruf -- keine eigene Einladungs-/
        Consent-/Tischlogik (die bleibt vollstaendig in `_cmd_local_round`)."""
        other_humans = [p for p in human_ids if p != self.participant_id]
        tokens: list[str] = []
        if leader_choice != self.participant_id:
            tokens.append(f"lead:persona:{leader_choice}")
            tokens.extend(other_humans)
            tokens.extend(f"persona:{p}" for p in ai_tokens if p != leader_choice)
        else:
            tokens.extend(other_humans)
            tokens.extend(f"persona:{p}" for p in ai_tokens)
        return tokens

    def _local_round_show_summary(self, human_ids: list[str], ai_tokens: list[str], leader_choice: str) -> bool:
        """A24 R2 (02 §Auftrag R2 'Zusammenfassung mit 1-5 Gesamtspielern
        einschliesslich Leader und letzte bewusste Startwahl ... Auswahl ist
        noch keine KI-Zustimmung und keine Tischaufnahme')."""
        total = len(human_ids) + len(ai_tokens)
        self._print(
            f"Zusammenfassung ({total} Spieler einschliesslich Leader): "
            f"Menschen={human_ids} KI={ai_tokens} Leader={leader_choice}. "
            "Diese Auswahl ist noch KEINE KI-Zustimmung und keine Tischaufnahme -- "
            "der bestehende Einladungs-/Consentweg folgt unveraendert danach."
        )
        from ..adapters.base import human_menu_decision

        # G02 (02 §C): zentraler Helper statt rohem `_readline`.
        try:
            answer, control = self._readline_with_controls(
                "Mit dieser Startwahl fortfahren? [j/n]: ", context="Startwahl bestaetigen",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return False
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Einrichtung abgebrochen: letzte Startwahl nicht bestaetigt.")
            return False
        decision, _explanation = human_menu_decision(answer)
        if decision != "accept":
            self._print("Einrichtung abgebrochen: letzte Startwahl nicht bestaetigt.")
            return False
        return True

    def _local_round_handoff(self, pid: str, *, in_round: bool = False) -> bool:
        """A24 R2 (02 §Auftrag R2 'Vor Uebergabe der geteilten Eingabe an
        einen anderen Menschen dessen Name/Teilnehmer-ID und eigene Figur
        eindeutig anzeigen und eine bewusste Uebernahme/Weiter-Aktion
        ermoeglichen; Abbrechen/EOF bleiben ein klarer Ruck-/Halteweg ohne
        KI-Ersatz'). Dies ist lokale Eingabezuordnung (kein OS-Login) und
        aendert WEDER `table.leader` NOCH Mitgliedschaft/Figur -- reine
        Bestaetigung VOR dem unveraenderten `_cmd_local_round`-Aufruf.

        G02 (02 §C): nutzt `_readline_with_controls` -- eine Steuerzeile an
        dieser Stelle gilt als Nicht-Uebernahme (derselbe klare Rueckweg wie
        'n'), kein KI-Ersatz, kein Datenverlust."""
        try:
            resolved = self._resolve_member(pid)
        except _ActiveSaveUnresolved:
            resolved = None
        chrono_id = resolved[1] if resolved is not None else "?"
        from ..adapters.base import human_menu_decision

        display_name = dict(self._local_round_list_humans()).get(pid, pid)
        self._print(f"Eingabe fuer: {display_name} | Teilnehmer {pid} | Figur {chrono_id}")
        try:
            answer, control = self._readline_with_controls(
                f"Geteiltes Terminal wird an '{pid}' (Figur '{chrono_id}') uebergeben -- "
                "bewusst uebernehmen? [j/n]: ",
                context="Terminaluebergabe",
            )
        except EndOfInput:
            if in_round:
                self._print("\nEingabeuebergabe beendet (EOF). Der angelegte Tisch und bisherige Daten bleiben erhalten; kein KI-Ersatz.")
            else:
                self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart; bereits angelegte Teilnehmer-/Figurdaten bleiben erhalten.")
            return False
        if control in ("zurueck", "abbrechen", "pause"):
            decision = "reject"
        else:
            decision, _explanation = human_menu_decision(answer)
        if decision != "accept":
            if in_round:
                self._print(f"Eingabeuebergabe an '{pid}' nicht bestaetigt. Der angelegte Tisch und bisherige Daten bleiben erhalten; kein KI-Ersatz.")
            else:
                self._print(f"Einrichtung abgebrochen: Uebergabe an '{pid}' nicht bestaetigt.")
            return False
        return True

    def _cmd_local_round_setup(self) -> None:
        """A24 R2 (02_AUFTRAG_A24_BEDIENGRENZE.md §R2, 11 §8): gefuehrter
        Einrichtungsweg fuer die lokale Runde -- fragt 'allein mit KI' oder
        'mehrere Menschen', laesst vorhandene lokale Teilnehmer sichtbar
        auswaehlen bzw. nach bewusster Eingabe ueber die vorhandene Registry
        registrieren, zeigt pro Mensch die eigene Figur aus vorhandenen
        Zuordnungen und laesst sie ausdruecklich bestaetigen, zeigt
        ausgewaehlte KIs + angefragten Leader + eine 1-5-Zusammenfassung
        einschliesslich Leader und laesst die letzte Startwahl bestaetigen,
        bestaetigt vor jeder Uebergabe des geteilten Terminals an einen
        WEITEREN Menschen dessen Name/Figur, und ruft danach UNVERAENDERT
        `_cmd_local_round` mit der fertigen Tokenliste auf -- der bestehende
        Einladungs-/Consentweg, die Tischanlage und die Kernrunde bleiben
        dadurch strukturell unveraendert (keine zweite Spielengine/
        Fokuspersistenz). Abbrechen/EOF an jedem Schritt ist ein klarer Halt
        ohne KI-Ersatz und ohne jede Aenderung.

        G02/P02 (General-Befund 'P02_HELP_ABORTS_ROUND_SETUP'): der
        Modusprompt nutzt jetzt den gemeinsamen kontextbewussten Leser
        (`_readline_with_controls`) statt eines rohen `_readline` --
        '?'/'/hilfe' zeigen hier dieselbe lokale Kontexthilfe und fragen
        DIESELBE Zeile erneut ab, statt die Einrichtung mit 'unbekannte
        Auswahl' zu verwerfen. Kein Zugverbrauch, kein GM-/Persona-Call."""
        try:
            mode, control = self._readline_with_controls(
                "Lokale Runde einrichten -- [1] Allein mit KI-Mitspielern "
                "[2] Mehrere Menschen an diesem Geraet: ",
                context="Runde einrichten",
            )
        except EndOfInput:
            self._print("\nEinrichtung abgebrochen (EOF) -- kein Spielstart, keine Aenderung.")
            return
        if control in ("zurueck", "abbrechen", "pause"):
            self._print("Einrichtung abgebrochen -- kein Spielstart, keine Aenderung.")
            return
        mode = mode.strip()
        if mode not in ("1", "2"):
            self._print(f"Einrichtung abgebrochen: unbekannte Auswahl {mode!r}.")
            return

        human_ids = [self.participant_id]
        if mode == "2":
            selected = self._local_round_select_humans()
            if selected is None:
                return
            human_ids = selected

        for pid in human_ids:
            if not self._local_round_confirm_figure(pid):
                return

        ai_tokens = self._local_round_select_ai()
        if ai_tokens is None:
            return

        leader_choice = self._local_round_select_leader(ai_tokens)
        if leader_choice is None:
            return

        if not self._local_round_show_summary(human_ids, ai_tokens, leader_choice):
            return

        confirmed_focus = self.participant_id
        for pid in human_ids:
            if pid == self.participant_id:
                continue
            if not self._local_round_handoff(pid):
                return
            confirmed_focus = pid

        guest_tokens = self._local_round_build_tokens(human_ids, ai_tokens, leader_choice)
        self._cmd_local_round(guest_tokens, guided=True, initial_focus=confirmed_focus)

    def _cmd_local_round(
        self, guest_tokens: list[str] | None = None, *, guided: bool = False,
        initial_focus: str | None = None,
    ) -> None:
        """I1/I3: gemeinsam an diesem Geraet spielen. Nutzt -- sofern
        konfiguriert -- GENAU `core.app_service.run_play_session`, denselben
        Call-Pfad wie `lab/runner.LabRunner.run_section` (A4).

        F2/K5 (WEGKARTE BLOCKER 2, 02 §8 "1-5 MENSCHEN UND KI-PERSONAS"):
        `guest_tokens` (aus 'l <id> ...' in derselben Auswahlzeile, s.
        `run()`) laedt weitere Teilnehmer VOR dem Tischstart ein -- ein
        blosser Teilnehmer-Name lauft als weiterer MENSCH am selben Geraet
        mit (geteiltes Terminal, eigener Eingabeprompt je Zug); ein Token
        'persona:<id>' laedt eine KI-Persona ueber `persona_driver_factory`
        ein (ohne konfigurierten Factory ehrliche Fehlermeldung, kein
        stiller Fallback). Genau der Mechanismus (Lobby-Join je Mitglied +
        Offer/Consent-Log + mehrere `chrononaut_ids`), den vorher nur der
        E2E-Testdialog manuell um `_cmd_local_round` HERUM nachbaute, sitzt
        jetzt IM Kommando selbst. Ohne `guest_tokens` bleibt der Solo-Weg
        unveraendert (Rueckwaertskompatibel zu P2F Test 08/09/10/11).

        A24 (WEGKARTE §8, 02 §4/11 §8 "KI-Leader: eigene modellbasierte
        Konsolidierung"): ein optionales FUEHRENDES Token `lead:persona:<id>`
        macht eine eingeladene Persona zum LEADER dieses Tisches statt des
        aufrufenden Menschen -- die Runtime behandelt jeden Leader (Mensch
        ODER Persona) bereits identisch (`core/runtime.py:act`/`controller.
        collect_decision`); die Persona muss die Leaderrolle zuerst ueber
        DENSELBEN Einladungs-/Gate-/Entscheidungsvertrag wie ein Gast
        annehmen -- ohne Zusage entsteht KEIN Tisch (kein KI-Ersatzleader
        ohne echte Entscheidung). Der aufrufende Mensch wird in diesem Fall
        selbst zum Gast (eigene Freigabe bereits durch den Kommandoaufruf
        gegeben, 02 §4: 'Mensch als Leader: eigene Freigabe' gilt spiegelbildlich
        fuer 'Mensch als bewusst zustimmender Gast eines KI-Leaders').

        A24 R2 (02_AUFTRAG_R2_R3.md §R2 'tatsaechliche Eingabeuebergabe'):
        `guided` (nur von `_cmd_local_round_setup` auf `True` gesetzt, der
        unveraenderte `l`-Tokenweg in `run()` ruft weiterhin ohne dieses
        Schluesselwort auf -- Default `False`) aktiviert einen FLUECHTIGEN,
        nur fuer DIESEN Aufruf gueltigen Fokuszeiger (`current_focus_pid`
        unten, reine Closure-Variable, keine Datei/kein Attribut): vor jeder
        TATSAECHLICHEN Eingabe eines anderen Menschen als des zuletzt
        bestaetigten zeigt `_local_round_handoff` (dieselbe Methode wie im
        Setup, kein Duplikat) Name/Teilnehmer-ID/Figur und verlangt eine
        bewusste Uebernahme -- das gilt fuer JEDEN Akteurwechsel inklusive
        der Rueckuebergabe an den aufrufenden Menschen, nicht nur den ersten.
        Lehnt der angefragte Mensch ab oder bricht per EOF ab, endet die
        Eingabe an der VORHANDENEN sicheren `EndOfInput`-Grenze (run():
        catch um 'g'/'l', s. dort) -- kein KI-Ersatz, kein nachtraeglich
        gewaehlter Ersatzleader, `table.leader`/Mitgliedschaft/Figur bleiben
        unberuehrt. Der bestehende `l`-Tokenweg bleibt dadurch OHNE neue
        Pflichtzeilen kompatibel (07 'l-Skriptweg bleibt ... kompatibel') --
        bei `guided=False` ist dieser gesamte Mechanismus wirkungslos."""
        # Preserve the actual last confirmed setup actor through consent and play.
        # This local value expires on return/exception; it is not a stored authority.
        current_focus_pid = (initial_focus or self.participant_id) if guided else None
        if self.run_dir is None or self.states_dir is None or self.schema_path is None or self.gm_transport_factory is None:
            self._print(
                "Lokale Runde erfordert eine konfigurierte Laufumgebung (run_dir/states_dir/"
                "schema_path) und eine SL-Anbindung (gm_transport_factory) — hier nicht "
                "konfiguriert, kein Spielstart (Live-Setup, s. docs/mmo-sim.md)."
            )
            return
        # H-D/H06 (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27): ein
        # aktiver Lab-Lauf ist der alleinige Schreiber fuer dieses `run_dir`
        # -- die lokale Runde lehnt kontrolliert ab, statt heimlich zum
        # zweiten Simulationscontroller zu werden (s. `_cmd_lobby_initiative`,
        # identischer Guard).
        from ..lab.runner import active_lock_pid
        pid = active_lock_pid(self.run_dir, exclude_pid=os.getpid())
        if pid is not None:
            self._print(
                f"Lokale Runde: ein aktiver Lab-Lauf (pid={pid}) kontrolliert diese Datenablage "
                "— kein zweiter schreibender Controller (H-D). Nur lesende Ansicht moeglich "
                "('python scripts/mmo_sim.py lab status/attach')."
            )
            return

        from ..core import app_service
        from ..core import store as core_store
        from ..core import lobby_service
        from ..core.controller import TableController
        from ..core.persona_state import PersonaStateStore
        from ..adapters.base import (
            ParticipantDecision,
            decision_contract_instruction,
            human_menu_decision,
            interpret_decision_contract,
        )

        def _admitted_invite_decision(driver, ctx: dict, role: str, participant: str):
            """01_AUFTRAG_LOBBY_INITIATIVE.md §4 A ("kleiner wiederverwendbarer
            Dienst zwischen UI und bestehenden Primitiven"): delegiert an
            `core.lobby_service.request_admitted_decision` -- derselbe
            reservierte+persistierte Requestweg wie jede andere Rolle
            (`core.runtime.SectionRuntime._admitted_decision`), jetzt
            zusaetzlich mit known-ID/missing-Record-Wiederaufnahme (D/L08,
            s. dortiger Docstring) -- ein frischer Interpreter, der nach
            einem Absturz dieselbe Einladungsanfrage erneut stellt,
            dupliziert keinen bereits empfangenen Request mehr.

            End-Critic-Nacharbeit (§6 END-CRITIC.md): `role`+`participant`
            allein identifizieren eine Operation NICHT eindeutig ueber die
            gesamte Laufzeit von `run_dir` hinweg -- eine SPAETERE, inhaltlich
            unabhaengige Einladung an dieselbe Person (Kernanwendungsfall,
            contract-v2 02 §3 "wiederkehrende bekannte Mitspieler sind
            erwuenscht") wuerde sonst faelschlich die laengst abgeschlossene
            Alt-Antwort ueber `find_durable_result` wiederverwenden, OHNE
            real gefragt zu werden. `round_section_id` (unten, EINMAL pro
            `_cmd_local_round`-Aufruf aus der bereits vorhandenen Logzeilen-
            zahl abgeleitet, wie `_cmd_lobby_initiative`s `window_section_id`)
            bindet die Identitaet zusaetzlich an DIESEN Rundenaufruf --
            zwei separate Aufrufe mit identischer Gruppe erhalten dadurch
            unterschiedliche `section_id`s, ein Retry INNERHALB derselben
            Runde (vor jedem eigenen Logwrite berechnet) dieselbe."""
            return lobby_service.request_admitted_decision(
                self.run_dir, driver, ctx, role=role, participant=participant,
                section_id=round_section_id,
            )

        # End-Critic-Nacharbeit (§6): EINMAL pro Rundenaufruf, VOR jedem
        # eigenen Logwrite dieser Runde berechnet -- s. Docstring oben.
        round_section_id = f"local-round-{len(lobby_service.read_offer_log(self.run_dir))}"

        tokens = list(guest_tokens or [])
        leader_persona_id: str | None = None
        if tokens and tokens[0].startswith("lead:persona:"):
            leader_persona_id = tokens[0].split(":", 2)[2]
            tokens = tokens[1:]
        leader_id = leader_persona_id if leader_persona_id else self.participant_id

        # 01_AUFTRAG §4 A: `self._resolve_member` (extrahierte Methode, s.
        # dortiger Docstring) ersetzt die vorherige lokale Closure -- auch
        # `_cmd_lobby_initiative` nutzt dieselbe Methode, keine zweite Kopie.
        _resolve_member = self._resolve_member

        try:
            resolved_leader = _resolve_member(leader_id)
        except _ActiveSaveUnresolved:
            if leader_persona_id:
                self._print(
                    f"KI-Leader '{leader_persona_id}' nicht moeglich: der aktuell veroeffentlichte "
                    "Spielstand ist gerade nicht lesbar — kein Spielstart, bis die tatsaechliche "
                    "Autoritaet geklaert ist."
                )
            else:
                self._print(
                    "Lokale Runde nicht moeglich: dein aktuell veroeffentlichter Spielstand ist "
                    "gerade nicht lesbar — kein Spielstart, bis die tatsaechliche Autoritaet "
                    "geklaert ist (Fassung bleibt ungefaehrdet, spaeter erneut versuchen)."
                )
            return
        if resolved_leader is None:
            if leader_persona_id:
                self._print(f"KI-Leader '{leader_persona_id}' hat keine abgeschlossene Figur — kein Spielstart.")
            else:
                self._print("Lokale Runde: noch keine abgeschlossene Figur vorhanden — zuerst [n] abschliessen.")
            return
        active_save, chrononaut_id = resolved_leader

        leader_driver = None
        if leader_persona_id:
            # A24/D4 (WEGKARTE §8, D2-Entscheidungsvertrag, D4-Gate):
            # eine KI-Leaderrolle ist KEINE Annahme ohne echte, protokollierte
            # Zusage -- derselbe Vertrag wie eine Gasteinladung.
            if self.persona_driver_factory is None:
                self._print(
                    f"KI-Leader '{leader_persona_id}' erfordert eine konfigurierte Persona-Anbindung "
                    "(persona_driver_factory) — hier nicht konfiguriert, kein Spielstart."
                )
                return
            # W2/I2 (F..., "ein Request-/Usageweg fuer ALLE Rollen", Case
            # 05): Treiber UND Kontext VOR dem Gate-Check konstruieren, damit
            # eine ggf. konfigurierte Ausgabeobergrenze (`PersonaApiConfig.
            # max_tokens`) UND die tatsaechliche Anfragegroesse (Input) in
            # eine anfragebezogene Reservierung einfliessen koennen (statt
            # Pauschalschwelle) -- s. `admission.reservation_for_request`.
            # I1 (MAIN-ENTSCHEIDUNG: 'KI-Leader + API/Hybrid-Gaeste: derselbe
            # semantische Einladungsvertrag'): deterministische, aus den
            # Aufrufparametern ableitbare offer_id (kein Zeitstempel) --
            # IDs/Rolle erreichen den tatsaechlichen Modellprompt (nicht nur
            # nachtraeglich das Audit-Log) und werden VOR Aufnahme geprueft.
            # UX18 (OFFENE_BEDIENBEFUNDE.md Punkt 8, General-Befund G04):
            # dieser Factory-Aufruf stand vorher VOR jedem schuetzenden
            # `try` -- eine fehlende Konfiguration (`RuntimeError` aus
            # `factories.py`) konnte hier ungefangen durchschlagen (moeglicher
            # Python-Traceback statt der sonst beobachtbaren ruhigen
            # Textzeile, analog `gm_transport_factory`-Fehlern weiter unten).
            # Jetzt derselbe kontrollierte Rueckweg wie bei der SL-Anbindung:
            # kein Secret-/Traceback-Leck, kein Fallback, kein Folgecall.
            try:
                leader_driver = self.persona_driver_factory(leader_persona_id)
            except Exception:
                self._print(self._opaque_boundary_error(f"KI-Leader '{leader_persona_id}' nicht moeglich"))
                return
            lead_offer_id = f"lead-invite-{leader_persona_id}-{self.participant_id}"
            lead_invite_ctx = {
                "system": self._own_system_context(leader_persona_id),
                "user": (
                    f"'{self.participant_id}' fragt dich, ob DU diese lokale Runde als Leader "
                    "fuehrst (du sendest die konsolidierten Nachrichten an die SL).\n"
                    + decision_contract_instruction(lead_offer_id, leader_persona_id)
                ),
                "decision_contract": {"offer_id": lead_offer_id, "participant_id": leader_persona_id},
            }
            try:
                lead_decision, block_reason = _admitted_invite_decision(
                    leader_driver, lead_invite_ctx, "lead_invite", leader_persona_id,
                )
            except Exception:
                self._print(self._opaque_boundary_error(
                    f"KI-Leader-Anfrage an '{leader_persona_id}' fehlgeschlagen", attempted=True,
                ))
                return
            if lead_decision is None:
                self._print(f"KI-Leader-Anfrage an '{leader_persona_id}' blockiert (Admission-Gate: {block_reason}) — kein Modellaufruf.")
                return
            # I1: `.decision` gilt nur, wenn es bereits accept/reject ist (vom
            # Adapter ueber genau dieselbe Kontrollform berechnet); jeder
            # andere Treiber (z.B. ein Testdouble, das `.decision` nie
            # setzt) faellt auf denselben Kontrollform-Check des Rohtexts
            # zurueck -- EIN Vertrag, unabhaengig vom Adapter.
            if lead_decision.decision in ("accept", "reject"):
                decision_kind = lead_decision.decision
            else:
                decision_kind, _explanation = interpret_decision_contract(
                    lead_decision.text, offer_id=lead_offer_id, participant_id=leader_persona_id,
                )
            self._append_invitation_log({
                "type": "response", "offer_id": lead_offer_id,
                "ts": datetime.datetime.now().isoformat(),
                "from": leader_persona_id, "decision": decision_kind,
                "origin_source": lead_decision.origin_source,
            })
            if decision_kind != "accept":
                self._print(f"'{leader_persona_id}' hat die Leaderrolle nicht angenommen (Entscheidung: {decision_kind}) — kein Spielstart.")
                return
            # Der Mensch wird selbst zum Gast dieses KI-gefuehrten Tisches --
            # eigene Freigabe liegt bereits durch den Kommandoaufruf vor.
            if self.participant_id not in tokens:
                tokens = [self.participant_id] + tokens

        # Weitere Teilnehmer (Mensch und/oder Persona) aufloesen, BEVOR der
        # Tisch entsteht -- jeder Gast braucht dieselbe abgeschlossene Figur
        # wie der Leader (ueber `onboarding.peek`, kein Katalog-Umweg noetig).
        #
        # D2/A1 (K5, WEGKARTE §6, PLAN-CRITIC-ABSCHLUSS.md BLOCKER):
        # Einladung != Zustimmung. Fuer eine eingeladene PERSONA wird echte,
        # protokollierte Zusage VOR jeder Tischaufnahme eingeholt (derselbe
        # `ParticipantDriver`-Vertrag, kein Auto-Fill) -- der Tisch ENTSTEHT
        # nicht, bevor diese Entscheidung vorliegt (Test 03: Mitgliedschaft
        # darf keiner Gastentscheidung vorausgehen). Scheitert die Zusage
        # (Ablehnung ODER Fehler beim Befragen -- sicherer Fehlschlag statt
        # Auto-Accept), bleibt der Gast schlicht aussen vor, der Leader kann
        # solo bzw. mit den uebrigen Gaesten weiterspielen.
        #
        # A24 (WEGKARTE §8, 11 §8 "Lokale menschliche Zustimmung wird
        # ausdruecklich eingegeben"): ein am selben Geraet mitspielender
        # MENSCH (Token ohne 'persona:'-Praefix) bestaetigt SELBST explizit
        # per eigener Eingabe -- keine automatische Zusage durch blosses
        # Erscheinen am geteilten Terminal mehr. Ausnahme: der aufrufende
        # Mensch selbst (bei KI-Leader-Modus oben in `tokens` eingefuegt)
        # hat seine Freigabe bereits durch den Kommandoaufruf gegeben.
        invited_ids: list[str] = []
        guest_specs: list[tuple[str, bool, dict, object | None]] = []
        # W1-B2-Fix (Main-Nacharbeit, End-Critic BLOCKER 2): jeder
        # zustimmungspflichtige Gast (Persona ODER zusaetzlicher Mensch)
        # wird hier als ANGEFRAGT vermerkt -- unabhaengig vom spaeteren
        # accept/reject/invalid. Der Abbruch-Guard unten prueft dann, ob
        # ALLE Angefragten zugesagt haben (kein stiller Solo-Tisch UND
        # keine still verkleinerte Restgruppe), statt fehlerhaft
        # `invited_ids` (das aus F3/table_id-Gruenden auch ablehnende
        # Personas enthaelt).
        requested_consent_guests: list[str] = []
        chrononaut_ids = {leader_id: chrononaut_id}
        # W1 (F..., "Angebot+Antworten VOR Tischanlage festhalten"): das
        # Angebot (wer wurde mit welchen Wunschteilnehmern angefragt) UND
        # jede einzelne Antwort werden real auf Platte festgehalten, BEVOR
        # ueberhaupt ein Tisch entsteht -- unabhaengig davon, ob die
        # Einladung am Ende angenommen wird. Reines Audit-/Nachweislog
        # (kein neuer Store, keine neue Architektur), append-only.
        # I1: deterministische, aus Leader+angefragten Gaesten ableitbare
        # offer_id (kein Zeitstempel) -- reproduzierbar fuer Tests UND fuer
        # eine reale Persona, die die ID im naechsten Turn korrekt
        # referenzieren koennen muss (Kontrollform-Bindung, s.
        # `decision_contract_instruction`).
        invitation_offer_id = "invite-" + leader_id + "-" + "-".join(
            sorted(t.split(":", 1)[-1] for t in tokens)
        ) if tokens else f"invite-{leader_id}-empty"
        if tokens:
            self._append_invitation_log({
                "type": "offer", "offer_id": invitation_offer_id,
                "ts": datetime.datetime.now().isoformat(),
                "from": leader_id, "wants": list(tokens),
            })
        for token in tokens:
            is_persona = token.startswith("persona:")
            guest_id = token.split(":", 1)[1] if is_persona else token
            if not guest_id or guest_id == leader_id:
                continue
            try:
                resolved_guest = _resolve_member(guest_id)
            except _ActiveSaveUnresolved:
                self._print(
                    f"Lokale Runde nicht moeglich: der aktuell veroeffentlichte Spielstand von "
                    f"'{guest_id}' ist gerade nicht lesbar — kein Spielstart, bis die tatsaechliche "
                    "Autoritaet geklaert ist."
                )
                return
            if resolved_guest is None:
                self._print(f"Einladung an '{guest_id}' nicht moeglich: keine abgeschlossene Figur vorhanden.")
                return
            guest_active_save, guest_chrononaut_id = resolved_guest
            # W1-B2-Fix: der aufrufende Mensch selbst ist bereits
            # freigegeben; jeder ANDERE angefragte Teilnehmer (Persona
            # oder zusaetzlicher Mensch) ist zustimmungspflichtig.
            if guest_id != self.participant_id:
                requested_consent_guests.append(guest_id)
            # A24/R03-Restintegrationsfix (WEGKARTE §5/§8 R02/R03,
            # REVIEW-P2R.md R-B, Test 03): ein am selben Geraet mitspielender
            # MENSCH (Token ohne 'persona:'-Praefix) bestaetigt SELBST
            # explizit per eigener Eingabe, VOR jeder Tischaufnahme -- bloss
            # als Token genannt zu sein war zuvor eine automatische Zusage
            # (`accept: True` ohne jede Eingabe). Dieselbe strukturierte
            # Ja/Nein-Auswertung wie bei Persona-Einladungen
            # (`interpret_yes_no_decision`, keine Negationsliste, "invalid"
            # -> keine Aufnahme). EOF/Abbruch VOR der ersten Bestaetigung
            # verhindert damit strukturell jede Tischanlage mit diesem Gast
            # (kein Tisch existiert bereits vor einer Gastentscheidung).
            if not is_persona and guest_id != self.participant_id:
                # Der aufrufende Mensch selbst hat seine Freigabe bereits
                # durch den Kommandoaufruf gegeben (auch als Gast eines
                # KI-Leaders, s. oben) -- nur ZUSAETZLICHE Menschen am
                # geteilten Geraet bestaetigen per eigener Eingabe.
                if guided and current_focus_pid != guest_id:
                    if not self._local_round_handoff(guest_id):
                        raise EndOfInput()
                    current_focus_pid = guest_id
                # R05 (UX09, 01_REVIEW_A23.md-Nachzug "2+3 .../pause nicht
                # komplett geliefert"): dieser Gastbeitritt war bisher die
                # EINZIGE Stelle, die eine rohe `_readline` statt des
                # zentralen Kontrollvertrags (`_readline_with_controls`,
                # `_CONTROL_TOKENS`) nutzte -- '/pause' erreichte hier nie
                # den Aufrufer, sondern verschwand unterschiedslos in der
                # binaeren Ja/Nein-Auswertung als 'invalid' (ununterscheidbar
                # von Kauderwelsch). Jetzt: derselbe Kontrollvertrag wie an
                # jedem anderen Menschprompt -- 'j'/'n' bleiben bytegleich
                # zur bisherigen Ja/Nein-Auswertung (kein 'control', `raw`
                # unveraendert an `human_menu_decision` weitergereicht);
                # '/zurueck'/'/abbrechen'/'/pause' werden EIGENS als
                # 'paused' protokolliert (kein 'invalid', keine
                # Falschzuordnung zu einer inhaltlichen Ablehnung) und
                # verlassen DIESEN Gast ohne Zusage -- der bestehende
                # Abbruch-Guard (alle Angefragten muessen zugesagt haben)
                # bleibt unveraendert wirksam, kein Tisch mit ungeklaerter
                # Besetzung.
                confirm_answer, confirm_control = self._readline_with_controls(
                    f"[{guest_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten? [j/n]: ",
                    context="Rundenbeitritt",
                )
                if confirm_control in ("zurueck", "abbrechen", "pause"):
                    self._append_invitation_log({
                        "type": "response", "offer_id": invitation_offer_id,
                        "ts": datetime.datetime.now().isoformat(),
                        "from": guest_id, "decision": "paused", "origin_source": "human:terminal",
                    })
                    self._print(
                        f"'{guest_id}' pausiert den Rundenbeitritt (/{confirm_control}) -- keine Zusage, "
                        "kein Tisch mit dieser Besetzung."
                    )
                    continue
                # I1 (MAIN-ENTSCHEIDUNG: 'kein JSON fuer Menschen') -- die
                # eindeutig bezeichnete Menuefrage selbst stellt die Bindung
                # an offer_id/participant_id her; derselbe (decision,
                # explanation)-Vertrag wie fuer Personas, nur ueber die
                # einfache Ja/Nein-Auswertung statt der Kontrollform.
                confirm_decision, _explanation = human_menu_decision(confirm_answer)
                self._append_invitation_log({
                    "type": "response", "offer_id": invitation_offer_id,
                    "ts": datetime.datetime.now().isoformat(),
                    "from": guest_id, "decision": confirm_decision, "origin_source": "human:terminal",
                })
                if confirm_decision != "accept":
                    self._print(
                        f"'{guest_id}' hat der lokalen Runde nicht zugestimmt "
                        f"(Eingabe: {confirm_answer!r}, Entscheidung: {confirm_decision})."
                    )
                    continue
            if is_persona and self.persona_driver_factory is None:
                self._print(
                    f"Einladung an Persona '{guest_id}' erfordert eine konfigurierte Persona-Anbindung "
                    "(persona_driver_factory) — hier nicht konfiguriert, kein Spielstart."
                )
                return
            invited_ids.append(guest_id)
            driver = None
            if is_persona:
                # D4/A1 (WEGKARTE §8, Test 04): Einladungen sind Modell-
                # requests hinter DERSELBEN Admission-Gate-Grenze wie Spiel/
                # Reflexion -- ein persistierter Stop verhindert bereits
                # DIESEN Request, nicht erst den naechsten Spielzug.
                # W2/I2 (F..., Test 04/05): Treiber UND Kontext VOR dem
                # Gate-Check bauen, damit eine konfigurierte Ausgabeobergrenze
                # UND die tatsaechliche Inputgroesse anfragebezogen reserviert
                # werden koennen (statt Pauschalschwelle, Case 05).
                # I1 (MAIN-ENTSCHEIDUNG I1-Kontrollform): IDs/Angebot/Rolle
                # erreichen so den tatsaechlichen Modellprompt (nicht nur
                # nachtraeglich das Audit-Log) und werden VOR Aufnahme
                # geprueft (`decision_contract`, s. `interpret_decision_
                # contract`).
                # UX18 (OFFENE_BEDIENBEFUNDE.md Punkt 8, General-Befund G04):
                # vorher stand dieser Aufruf VOR dem schuetzenden `try`
                # unten (der nur `_admitted_invite_decision` umschloss) --
                # eine fehlende Persona-Konfiguration konnte hier ungefangen
                # durchschlagen. Jetzt derselbe kontrollierte Rueckweg wie
                # beim KI-Leader: kein Secret-/Traceback-Leck, dieser EINE
                # Gast bleibt aussen vor, der Tisch kann mit den uebrigen
                # weiterlaufen (kein Abbruch der gesamten Runde).
                try:
                    driver = self.persona_driver_factory(guest_id)
                except Exception:
                    self._print(self._opaque_boundary_error(f"Einladung an Persona '{guest_id}' nicht moeglich") + " Dieser Gast bleibt aussen vor.")
                    invited_ids.remove(guest_id)
                    continue
                invite_ctx = {
                    "system": self._own_system_context(guest_id),
                    "user": (
                        f"Du wirst von '{leader_id}' eingeladen, einer lokalen Runde beizutreten.\n"
                        + decision_contract_instruction(invitation_offer_id, guest_id)
                    ),
                    "decision_contract": {"offer_id": invitation_offer_id, "participant_id": guest_id},
                }
                try:
                    invite_decision, block_reason = _admitted_invite_decision(
                        driver, invite_ctx, "guest_invite", guest_id,
                    )
                except Exception:  # Transportfehler -- kein Auto-Accept.
                    self._print(self._opaque_boundary_error(
                        f"Einladung an '{guest_id}' nicht zustande gekommen", attempted=True,
                    ))
                    continue
                if invite_decision is None:
                    self._print(f"Einladung an '{guest_id}' blockiert (Admission-Gate: {block_reason}) — kein Modellaufruf.")
                    continue
                # A4/D2 (WEGKARTE §8, Test 03): eine erfolgreich zugestellte
                # Antwort ist KEINE Zusage -- nur ein strukturell als
                # 'accept' ausgewertetes `decision`-Feld nimmt den Gast auf.
                # I1: `.decision` gilt nur als bereits berechnet, wenn der
                # Adapter selbst dieselbe Kontrollform ausgewertet hat
                # (accept/reject); jeder andere Treiber faellt auf denselben
                # Kontrollform-Check des Rohtexts zurueck -- EIN Vertrag.
                if invite_decision.decision in ("accept", "reject"):
                    decision_kind = invite_decision.decision
                else:
                    decision_kind, _explanation = interpret_decision_contract(
                        invite_decision.text, offer_id=invitation_offer_id, participant_id=guest_id,
                    )
                self._append_invitation_log({
                    "type": "response", "offer_id": invitation_offer_id,
                    "ts": datetime.datetime.now().isoformat(),
                    "from": guest_id, "decision": decision_kind,
                    "origin_source": invite_decision.origin_source,
                })
                if decision_kind != "accept":
                    self._print(f"Einladung an '{guest_id}' nicht angenommen (Entscheidung: {decision_kind}).")
                    continue
            guest_specs.append((guest_id, is_persona, guest_active_save, driver))
            chrononaut_ids[guest_id] = guest_chrononaut_id

        # W1-Fix (F..., Test 03 review_p2w_boundaries.py): eine explizit
        # angefragte Runde (`tokens` nicht leer), bei der KEIN einziger
        # angefragter Teilnehmer aufgenommen wurde (`invited_ids` leer --
        # das betrifft NUR reine Menschen-Ablehnungen: eine eingeladene
        # PERSONA reserviert ihren Platz in `invited_ids` bereits VOR ihrer
        # Entscheidung, s. oben, damit der Tisch-Namensraum F3-konform an
        # die urspruenglich eingeladenen IDs gebunden bleibt, auch wenn sie
        # ablehnt), darf NICHT still in ein Soloangebot ohne neue
        # Leaderentscheidung umgeschrieben werden -- der Abschnitt bricht
        # hier kontrolliert ab, KEIN Tisch entsteht (weder Solo- noch
        # Gruppentisch). Ein erneuter, ausdruecklicher Aufruf von 'l' (mit
        # oder ohne Teilnehmer) ist die einzige Fortsetzung.
        # W1-B2-Fix (Main-Nacharbeit, End-Critic BLOCKER 2): eine explizit
        # angefragte Runde scheitert, sobald AUCH NUR EIN zustimmungs-
        # pflichtiger Gast nicht zugesagt hat (Ablehnung/ungueltig/nicht
        # erreichbar) -- es entsteht dann WEDER ein Solo-Tisch NOCH eine
        # still verkleinerte Restgruppe. Geprueft wird gegen die tatsaechlich
        # aufgenommenen Gaeste (`guest_specs`), NICHT gegen `invited_ids`
        # (das aus F3/table_id-Gruenden auch abgelehnte Personas enthaelt und
        # den gemischten-Gruppen-Bug verursachte). `invited_ids` bleibt fuer
        # die table_id-Bindung unveraendert (F3). Nur ein erneuter
        # ausdruecklicher 'l'-Aufruf setzt die Runde fort.
        accepted_guest_ids = {g for g, _p, _s, _d in guest_specs}
        unfulfilled = [g for g in requested_consent_guests if g not in accepted_guest_ids]
        if tokens and unfulfilled:
            self._print(
                "Angefragte lokale Runde nicht zustande gekommen: nicht alle "
                "angefragten Teilnehmer haben zugesagt (offen/abgelehnt/ungueltig: "
                f"{sorted(unfulfilled)}) — kein automatischer Solo-/Restgruppen-"
                "weiterlauf ohne neue ausdrueckliche Wahl (erneut 'l' aufrufen)."
            )
            return

        ps_store = PersonaStateStore(schema_path=self.schema_path)
        lobby = core_store.Lobby(self.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join(leader_id)
        for guest_id, _is_persona, _save, _driver in guest_specs:
            lobby.join(guest_id)
        # Offer/Consent-Log wird ERST NACH echter Zusage gebaut (nur mit den
        # tatsaechlich zugesagten Gaesten) -- vorher (BLOCKER) stand hier
        # `accept: True` fuer jeden eingeladenen Gast, UNABHAENGIG von einer
        # Entscheidung.
        offer_events = [{
            "type": "offer", "id": "o1", "from": leader_id,
            "wants": [g for g, _p, _s, _d in guest_specs],
        }]
        offer_events += [
            {"type": "consent", "offer_id": "o1", "from": g, "accept": True} for g, _p, _s, _d in guest_specs
        ]
        # Eingeladene Gaeste bekommen einen EIGENEN Tisch-Namensraum
        # (`local-<leader>-<gast1>-...`) statt des Solo-Ids `local-<leader>` --
        # sonst wuerde ein SPAETERER Solo-Aufruf (kein guest_tokens) denselben
        # persistierten Mehrpersonen-Tisch resumen und beim naechsten Poll
        # ohne Treiber fuer die frueheren Gaeste abstuerzen (`table.members`
        # bleibt ueber Sektionsgrenzen hinweg bestehen, F5/A8-Resume). Der
        # Namensraum bleibt an die URSPRUENGLICH eingeladenen IDs gebunden
        # (nicht an das Zusage-Ergebnis) -- Test 03 laedt genau diesen
        # Tisch-Namen, auch wenn die Persona ablehnt.
        table_id = f"local-{leader_id}"
        if invited_ids:
            table_id += "-" + "-".join(sorted(invited_ids))
        table, derivation = core_store.create_table_from_offer_log(
            lobby, table_id,
            offer_log_events=offer_events,
            chrononaut_ids=chrononaut_ids,
        )
        if table is None:
            size = len(derivation.members)
            size_policy = lobby.table_size_policy
            if derivation.members and not size_policy.validate_size(size):
                self._print(
                    f"Lokale Runde konnte nicht gestartet werden: {size} Spieler angefragt; "
                    f"zulaessig sind {size_policy.min_size} bis {size_policy.max_size} "
                    "Menschen und KI-Personas zusammen, einschliesslich Leader. "
                    "Keine automatische Kuerzung; bitte die Gruppe bewusst neu waehlen."
                )
            else:
                self._print(f"Lokale Runde konnte nicht gestartet werden: {derivation.reason}")
            return

        # G03/P09-Extraktion: die eigentliche Rundenausfuehrung (Treiber-/
        # Kontextaufbau, SL-Transport, `app_service.run_play_session`) ist
        # IDENTISCH fuer einen frisch eingeladenen Tisch (hier) UND einen
        # bereits bestehenden, gebundenen Tisch beim Fortsetzen
        # (`_resume_bound_table`, kein zweiter Dispatch-Pfad) -- eine
        # gemeinsame Methode `_run_table_round` ersetzt den vorher hier
        # inline stehenden Rumpf.
        self._run_table_round(
            table, lobby, ps_store, leader_id, leader_persona_id, leader_driver,
            active_save, guest_specs, guided=guided, current_focus_pid=current_focus_pid,
        )

    def _run_table_round(
        self, table, lobby, ps_store, leader_id: str, leader_persona_id: str | None,
        leader_driver, active_save: dict | None,
        guest_specs: list[tuple[str, bool, dict, object | None]],
        *, guided: bool, current_focus_pid: str | None,
    ) -> None:
        """G03/P09 (ZEITRISS Terminal UX-1, Korrekturzyklus 2): aus
        `_cmd_local_round` extrahierter gemeinsamer Rumpf -- spielt einen
        BEREITS feststehenden Tisch (frisch eingeladen ODER real bestehend/
        gebunden) tatsaechlich. `_cmd_local_round` ruft dies NACH dem
        Einladungs-/Konsens-Loop + `create_table_from_offer_log` auf;
        `_resume_bound_table` (echtes Fortsetzen eines bereits gebundenen
        Mehrpersonentisches nach Neustart, P09) ruft dies DIREKT mit der aus
        der persistierten Tischdatei aufgeloesten Besetzung auf, OHNE den
        Einladungs-/Konsens-Loop erneut zu durchlaufen (die Mitgliedschaft
        ist dort bereits real zugesagt -- ein erneuter Consent-/Persona-
        Request waere ein verbotener Doppelcall/Publikation). Beide Aufrufer
        liefern dieselben Parameter (Leader-/Gast-Treiber, aufgeloeste
        aktuelle Saves, der feststehende `table`) -- kein zweiter
        Spielstart-Pfad, keine zweite Kopie der SL-/Reflexions-/Save-
        Anbindung."""
        from ..core import app_service
        from ..core.controller import TableController
        from ..adapters.base import ParticipantDecision
        # R1 (C-M1, UX14, Korrekturzyklur 1): dieselbe Formel wie
        # `core/runtime.py:SectionRuntime.__init__`s `_guests_imported`
        # (reine Lesefunktion ueber den bereits geladenen `table.sl_log`) --
        # `_purpose_label()`/die Payload-Wahl duerfen NICHT raten
        # (Pro-Prozess-Zaehler `self._turn`), sondern muessen dieselbe
        # PERSISTENTE Autoritaet konsultieren wie die Runtime selbst. Ohne
        # diesen Abgleich zeigte ein nach einem Prozessneustart bereits
        # frueher importierter Gast faelschlich "Erstbeitrag -> SL", obwohl
        # sein Beitrag real nur noch Tischabsprache wird (`poll_guests_and_
        # consolidate` liest `save_payload` nie aus).
        _sl_log_origins = {e.get("origin_persona_key") for e in table.sl_log}
        _already_imported_guests = {
            m for m in table.members if m != table.leader and m in _sl_log_origins
        }

        outer = self
        # Shared screen: publish every previously unseen public entry, not only
        # the last entry after several consecutive AI guest-imports.
        displayed_sl_count = 0
        # current_focus_pid deliberately remains the actor confirmed in setup/consent.
        # The first game contribution is not an implicit reset of that actor.

        class _HumanDriver:
            """F1 (K7/K8, WEGKARTE §6): zeigt die zuletzt empfangene
            oeffentliche SL-Antwort (`context['table_view']['sl_log']`) VOR
            der naechsten Eingabeaufforderung an -- vorher bekam der Mensch
            die SL-Antwort nie zu sehen (Test 08). Der erste Turn (Anker)
            haengt den aktuell ausgewaehlten v7-Save als `save_payload` an
            (wie beim Persona-Import), damit er tatsaechlich am GM-Transport
            ankommt (ueber `core/runtime.py`s Wire-Einbettung). `label`
            praefigiert den Eingabeprompt, wenn sich mehrere Menschen das
            Terminal teilen (BLOCKER 2) -- ohne Label unveraendert wie vorher.

            D2/K6 (WEGKARTE §6, Test 11): zeigt zusaetzlich eine noch nicht
            konsolidierte private Tischabsprache (`context
            ['pending_table_messages']`) VOR der Eingabeaufforderung an --
            der Mensch entscheidet mit voller Sicht, aber die Runtime haengt
            den Gastvorschlag NICHT mehr automatisch an die von ihm frei
            gewaehlte Antwort an (s. `core/runtime.py:act`)."""

            # I2-Nachzug: expliziter Marker statt Namens-/Attributraten --
            # `core/runtime.py:SectionRuntime._admitted_decision` erkennt
            # daran VOR jedem Dispatch, dass diese Entscheidung KEINE
            # Modellkosten verursacht (A1/R06) und ueberspringt Reservierung/
            # Requestledger fuer sie (Budget-neutral, wie vor diesem Umbau).
            is_human_driver = True

            def __init__(
                self, save: dict | None, pid: str, label: str | None = None, is_leader: bool = False,
                already_imported: bool = False,
            ):
                self._save = save
                self._turn = 0
                self._label = label
                self._pid = pid
                self._is_leader = is_leader
                # R1 (C-M1, UX14): die PERSISTENTE Autoritaet (aus `table.
                # sl_log`, s. `_already_imported_guests` oben), NICHT nur der
                # bei jedem Prozessneustart frisch bei 0 beginnende
                # Pro-Prozess-Zaehler `self._turn`.
                self._already_imported = already_imported

            def _purpose_label(self) -> str:
                # UX14/15 (02 §F, "Vier bestehende Faelle ausdruecklich
                # unterscheiden"): drei der vier Faelle laufen ueber diesen
                # generischen Zugprompt -- (1) Leader-Beitrag -> SL, (2) der
                # ERSTE Beitrag eines Gasts traegt den importierten Save und
                # laeuft ueber den Leader tatsaechlich bis zur SL durch,
                # (3) jeder WEITERE Gastbeitrag wird stattdessen als
                # Tischabsprache gespeichert (`poll_guests_and_consolidate`,
                # NICHT direkt an die SL). Der vierte Fall (freiwillige
                # lokale Abschlussnotiz) laeuft ebenfalls ueber DIESEN
                # `decide()`-Mechanismus (`_collect_reflections` ruft
                # denselben `controller.collect_decision`-Weg auf, s.
                # `decide()` unten) -- diese Methode hier kennt NUR die drei
                # Spielzug-Faelle und darf fuer den vierten Fall NICHT
                # aufgerufen werden (`decide()` zweigt dafuer VOR diesem
                # Aufruf ab, G04/P05: der vorherige Kommentar hier behauptete
                # faelschlich, die Notiz laufe 'nie ueber decide()' -- sie
                # tut es, nur eben mit einer eigenen Beschriftung).
                if self._is_leader:
                    return "Empfaenger: Spielleitung (SL)"
                if self._turn == 0 and not self._already_imported:
                    return "Empfaenger: ueber Leader an Spielleitung (dein Erstbeitrag, mit deinem Save)"
                return "Empfaenger: Tischabsprache (dein Tisch/Leader) — NICHT direkt an die SL"

            def decide(self, context: dict):
                nonlocal displayed_sl_count, current_focus_pid
                if guided and current_focus_pid != self._pid:
                    if not outer._local_round_handoff(self._pid, in_round=True):
                        raise EndOfInput()
                    current_focus_pid = self._pid
                table_view = context.get("table_view") or {}
                sl_log = table_view.get("sl_log") or []
                for entry in sl_log[displayed_sl_count:]:
                    outer._print(f"[SL] {entry.get('content', '')}")
                displayed_sl_count = len(sl_log)
                for m in context.get("pending_table_messages") or []:
                    outer._print(f"[Tischabsprache] {m.get('from', '?')}: {m.get('text', '')}")
                # UX14/15: Empfaenger-/Zweckzeile wird als EIGENE Zeile
                # UNMITTELBAR vor dem Prompt gedruckt (nicht in den
                # Prompttext selbst eingewoben) -- die bestehenden,
                # BYTEGLEICHEN Prompttexte "Deine Aktion:"/"[<label>] Deine
                # Aktion:" bleiben dadurch exakt erhalten (geschuetzt von
                # `test_a24_local_two_humans_2026_10_01.py`, das diese
                # exakten Teilstrings in echten Subprozess-Transkripten
                # zaehlt) -- nur zusaetzliche sichtbare Information, kein
                # veraenderter Eingabevertrag.
                #
                # G04/P05 (General-Befund 'P05_PRIVATE_NOTE_MISLABEL', W3-Hunk
                # selektiv uebernommen, s. W3-REUSE.md): `core/runtime.py:
                # _collect_reflections` ruft DENSELBEN `decide()`-Mechanismus
                # fuer den VIERTEN Eingabezweck (freiwillige lokale Notiz) auf
                # wie jeden normalen Spielzug -- `_purpose_label()` kennt
                # diesen vierten Zweck nicht und zeigte bisher IMMER die
                # Leader-/Gast-Spielzug-Beschriftung ("Spielleitung (SL)"/
                # "Tischabsprache"), obwohl die Notiz tatsaechlich NIE ueber
                # `gm_transport` laeuft, sondern (s. `_collect_reflections`-
                # Docstring) ausschliesslich lokal unter `reflections.jsonl`
                # landet (`kind=human_note`). Die bereits bedingt erlaubte
                # minimale typisierte Bruecke ist hier der vorhandene
                # `context['system'] == 'PRIVATE_REFLECTION_SENTINEL'`-Marker
                # (`_collect_reflections` setzt ihn bereits, kein neuer
                # Core-Write/-Vertrag, keine neue Produktregel) -- erkennt
                # `decide()` ihn, zeigt es die tatsaechlich zutreffende
                # lokale Beschriftung statt der Spielzug-Zweckzeile. Keine
                # Vertraulichkeitszusage bei geteiltem Bildschirm (02 §F).
                if context.get("system") == "PRIVATE_REFLECTION_SENTINEL":
                    outer._print(
                        "Empfaenger: eigene lokale Notiz (NICHT an Spielleitung/Tisch, freiwillig, "
                        "leer = keine Notiz, keine Vertraulichkeitszusage bei geteiltem Bildschirm)."
                    )
                else:
                    outer._print(self._purpose_label())
                label_prefix = f"[{self._label}] " if self._label else ""
                prompt = f"{label_prefix}Deine Aktion: "
                # UX04/05 (02 §C): Hilfe/Stand/Verlauf verbrauchen hier
                # KEINEN Zug -- `_readline_with_controls` beantwortet sie
                # selbst und fragt dieselbe Prompt-Zeile erneut ab, ohne
                # dass diese Methode je verlassen wird (kein `self._turn`
                # Inkrement, kein ParticipantDecision, also kein GM-/
                # Persona-Call fuer diese Zwischeneingaben).
                history = [f"[SL] {e.get('content', '')}" for e in sl_log]
                # G04/UX20 (W3-Hunk selektiv uebernommen, s. W3-REUSE.md):
                # `speaker_pid=self._pid` -- `/stand` an einem geteilten
                # Terminal zeigt den Stand DIESER gerade eingebenden Person,
                # nicht pauschal den aeusseren Sessionteilnehmer.
                text, control = outer._readline_with_controls(
                    prompt, context="Spielzug", history=history, speaker_pid=self._pid,
                )
                if control == "pause":
                    # 02 §C: Abbruch waehrend eines offenen Abschnitts
                    # bedeutet Pause/Beenden, kein fachlicher Rollback --
                    # dieselbe bereits bestehende, getestete kontrollierte
                    # Pausemechanik wie bei EOF/einer abgelehnten
                    # Fokusuebergabe (s. `_local_round_handoff` oben).
                    outer._print(
                        "Kontrolliert pausiert (/pause) — kein weiterer Zug, kein Modellaufruf; "
                        "der zuletzt gueltige Stand bleibt erhalten."
                    )
                    raise EndOfInput()
                if control in ("zurueck", "abbrechen"):
                    outer._print(
                        "Waehrend eines laufenden Abschnitts bedeutet Abbrechen Pause/Beenden, "
                        "kein Rollback (02 §C) — kontrolliert pausiert, kein Modellaufruf."
                    )
                    raise EndOfInput()
                text_out = text
                self._turn += 1
                # R1 (C-M1, UX14): dieselbe Autoritaet wie `_purpose_label()`
                # -- ein nach Neustart bereits frueher importierter Gast
                # haengt bei seinem (aus Prozesssicht) ersten Zug KEINEN
                # Save mehr an (sein Beitrag wird ohnehin nur noch
                # Tischabsprache, `poll_guests_and_consolidate` liest
                # `save_payload` nie aus -- die vorherige Zusicherung war
                # also irreführend, nicht nur wirkungslos).
                payload = self._save if (self._turn == 1 and not self._already_imported) else None
                return ParticipantDecision(text=text_out, origin_source="human:terminal", save_payload=payload)

        # A24 (WEGKARTE §8): der Leader-Driver ist entweder der aufrufende
        # Mensch (`_HumanDriver`, unveraendertes Standardverhalten) ODER die
        # bereits zugesagte KI-Persona (`leader_driver`, echte modellbasierte
        # Konsolidierung ueber denselben `ParticipantDriver`-Vertrag wie
        # jeder Gast -- die Runtime unterscheidet Leader/Gast nicht am Typ).
        drivers = {leader_id: leader_driver if leader_persona_id else _HumanDriver(active_save, leader_id, is_leader=True)}
        contexts = {leader_id: {
            "system": self._own_system_context(leader_id),
            "user": "Du fuehrst diese lokale Runde als KI-Leader." if leader_persona_id else "Ich beginne die lokale Runde.",
            # D3/A7 (K7, WEGKARTE §6): deterministische Save-Bindung durch
            # die Runtime selbst (s. `core/runtime.py:act`), NICHT vom
            # Modell erzeugt/abgeschrieben. `active_save` = aktuell
            # publizierter Stand (Test 05), nicht der veraltete
            # Erschaffungsstand.
            "import_save_payload": active_save,
        }}
        for guest_id, is_persona, guest_save, driver in guest_specs:
            if is_persona:
                drivers[guest_id] = driver
            elif guest_id == self.participant_id and leader_persona_id:
                # Der aufrufende Mensch ist hier selbst Gast eines KI-Leaders.
                drivers[guest_id] = _HumanDriver(
                    guest_save, guest_id, already_imported=guest_id in _already_imported_guests,
                )
            else:
                drivers[guest_id] = _HumanDriver(
                    guest_save, guest_id, label=guest_id,
                    already_imported=guest_id in _already_imported_guests,
                )
            contexts[guest_id] = {
                "system": self._own_system_context(guest_id),
                "user": "Ich trete der lokalen Runde bei.",
                "import_save_payload": guest_save,
            }
        if guest_specs:
            self._print(f"Gruppe eingeladen: leader={leader_id} gaeste={[g for g, _p, _s, _d in guest_specs]}")

        controller = TableController(leader_id, drivers)
        try:
            # A6/D3 (WEGKARTE §8, Test 10): Factories, die eine Tisch-
            # Identitaet entgegennehmen (echter Produktionsweg, s.
            # `scripts/mmo_sim.py:_default_gm_transport_factory`), bekommen
            # sie durchgereicht -- bestehende Zero-Arg-Test-Factories
            # (`lambda: gm`) bleiben unveraendert aufrufbar (Rueckwaerts-
            # kompatibel, kein Bruch bestehender Tests).
            import inspect
            try:
                accepts_table_id = len(inspect.signature(self.gm_transport_factory).parameters) >= 1
            except (TypeError, ValueError):
                accepts_table_id = False
            gm_transport = self.gm_transport_factory(table.table_id) if accepts_table_id else self.gm_transport_factory()
        except Exception:  # SL-Anbindung nicht herstellbar -- kein stiller Fallback (03 §4).
            self._print(self._opaque_boundary_error("Lokale Runde: SL-Anbindung nicht verfuegbar"))
            return

        today = datetime.date.today().isoformat()
        ts = datetime.datetime.now().isoformat()
        # W22 (Reserve-Reparatur, F05/T8 Journey 4): `request_ledger.begin`/
        # die Checkpoint-Writes innerhalb von `run_play_session` koennen bei
        # gesperrtem Storage (`OSError`/`PermissionError`) ODER bei einer
        # bereits offenen, nicht aufgeloesten Reservierung aus einem
        # frueheren Mid-Write-Crash (`request_ledger.OpenReservationExistsError`)
        # werfen -- sowohl bei einem frisch eingeladenen Tisch (Rundenturn)
        # ALS AUCH beim Fortsetzen eines gebundenen Tisches (`_resume_bound_
        # table`), da BEIDE Aufrufer ausschliesslich ueber diesen einen
        # Aufruf hierher kommen. Vorher erreichte der rohe Python-Traceback
        # ungefangen die Spieleransicht (F05-Klasse). Dieselbe request_
        # ledger-Semantik bleibt UNVERAENDERT (kein Auto-Resolve der offenen
        # Reservierung) -- der zugrunde liegende Reservierungszustand nach
        # einem Mid-Write-Crash bleibt ein bewusst hier NICHT behobenes
        # Residuum (s. W-REPORT.md). W24b: die beiden Faelle bekommen
        # GETRENNTE, ehrliche Anzeigen (s. die beiden `except`-Zweige unten)
        # statt der frueheren pauschalen "kein Datenverlust"+Retry-Zusage,
        # die fuer den offenen-Reservierung-Fall irrefuehrend war.
        from ..core import request_ledger
        try:
            outcome = app_service.run_play_session(
                # D5/A6 (WEGKARTE §6 BLOCKER): `table.table_id` (nicht das
                # urspruenglich angefragte `table_id`) -- `create_table_from_
                # offer_log` kann bei geschlossenem Vorgaenger-Tisch eine
                # generationsweise hochgezaehlte Kennung zurueckgeben.
                lobby, table, gm_transport, controller, f"{table.table_id}-section",
                contexts,
                self.states_dir, today, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
                ps_store, zeitriss_saves.harvest_from_debrief,
                # W51 (01_RESTAUFTRAG.md §3): additiv/optional -- reicht nur
                # die bisher stummen Gruppenkorrektur-Statuszeilen (s.
                # `core.runtime.SectionRuntime._group_correction_status_emit`)
                # ueber denselben bestehenden Terminalkanal durch, keine neue
                # Menuehierarchie.
                status_fn=self._print,
                # OPTION2-CMD (FIX-SPEC-OPTION2-CMD.md): Leader-`!save`/
                # `!speichern` + bindbarer v7-Save schliesst den Abschnitt
                # GLEICHWERTIG zum Top-Level-Marker -- derselbe Wiring-Punkt
                # wie `core/lobby_flow.py:play_bound_table`.
                completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
            )
        except request_ledger.OpenReservationExistsError:
            # W24b (Storage-HOLD Ehrlichkeit, BRIEF-W24b.md Punkt 1): die
            # vorherige PAUSCHALE "kein Datenverlust"+Retry-Zusage war fuer
            # DIESEN Fall falsch -- eine wieder verfuegbare Schreibberechtigung
            # loest die offene Requestreservierung aus einem frueheren Mid-
            # Write-Crash NICHT auf (`request_ledger.begin` prueft dieselbe
            # Operationsidentitaet erneut und wirft denselben Fehler wieder,
            # solange der offene Datensatz bestehen bleibt). KEINE automatische
            # Reservierungsfreigabe/Wiederanfrage/Locklöschung und KEIN
            # request_ledger-Umbau hier -- der tiefe Recoveryfall bleibt ein
            # bewusst OFFENER Befund (s. W-REPORT.md), kein falscher
            # UI-Retryrat.
            self._print(
                "Nicht aufgeloester HOLD: fuer diesen Abschnitt existiert noch eine offene, nicht "
                "abgeschlossene Requestreservierung aus einem frueheren Abbruch. Der letzte bestaetigte, "
                "gespeicherte Stand ist die verbindliche Grenze -- nicht der zuletzt versuchte Zug. "
                "Diese Reservierung wird HIER NICHT automatisch aufgehoben; ein erneuter Versuch ueber "
                "'n'/[fortsetzen] fuehrt zu demselben HOLD, solange die Reservierung offen bleibt -- das "
                "ist KEIN Vorschlag, es trotzdem zu versuchen. Dies ist ein bekannter, noch ungeloester "
                "Befund (keine Reparatur in dieser Ansicht), zurueck ins Hauptmenue. Keine Fehlerdetails "
                "in dieser Ansicht (Schutz vor Secret-/Innendetail-Lecks)."
            )
            return
        except OSError:
            # W24b (Storage-HOLD Ehrlichkeit, BRIEF-W24b.md Punkt 1): reiner
            # Schreibrechtefehler (Storage gesperrt/keine Berechtigung) OHNE
            # offene Reservierung -- hier IST ein spaeterer Retry ueber
            # 'n'/[fortsetzen] tatsaechlich sinnvoll, sobald Storage/
            # Anbindung wieder verfuegbar sind (anders als beim
            # OpenReservationExistsError-HOLD oben).
            self._print(
                "Speichern/Anbindung gerade nicht moeglich (Storage gesperrt oder keine Schreibrechte) "
                "-- der zuletzt gueltige, bereits gespeicherte Stand bleibt erhalten, kein Datenverlust. "
                "Dieser Versuch wurde sicher abgebrochen, zurueck ins Hauptmenue; spaeter erneut ueber "
                "'n'/[fortsetzen] versuchen, sobald Storage/Anbindung wieder verfuegbar sind. Keine "
                "Fehlerdetails in dieser Ansicht (Schutz vor Secret-/Innendetail-Lecks)."
            )
            return
        if outcome.completion.success:
            self._print(f"Abschnitt abgeschlossen: {outcome.completion.members_completed}")
        else:
            self._print(f"Abschnitt nicht abgeschlossen ({outcome.completion.reason}) — kann fortgesetzt werden.")

    # A10 (WEGKARTE §8, REVIEW-P2V.md §9/A01-A28-ABGLEICH A10): acht
    # konfigurierbare, DISTINKTE synthetische Start-Personas (02 §3: "Pool
    # von z.B. acht Start-Personas") -- klar als SIMULIERT/DEMO markiert,
    # kein echter Modellaufruf (Charaktererstellung durch die KI-SL bleibt
    # separate Live-Anfrage, 02 §3). Ersetzt den frueheren Ein-Personen-
    # Demopayload (Review-Befund: "Menue c erzeugt nur Demo-Payload fuer
    # einen Teilnehmer, keine reguläre neue Gemeinschaft mit Startfiguren").
    _STARTER_ARCHETYPES = (
        ("cqb", "Nahkampfspezialistin", "aggressiv-direkt"),
        ("sniper", "Weitschuss-Beobachter", "geduldig-praezise"),
        ("face", "Verhandlerin", "charismatisch-diplomatisch"),
        ("pyro", "Sprengstoffexperte", "impulsiv-risikofreudig"),
        ("tech", "Technik-Spezialistin", "analytisch-zurueckhaltend"),
        ("medic", "Feldsanitaeter", "fuersorglich-pragmatisch"),
        ("scout", "Aufklaererin", "wachsam-unabhaengig"),
        ("comms", "Kommunikationsoffizier", "kooperativ-organisiert"),
    )

    def _synthetic_starter_pool(self, community_id: str, size: int) -> dict[str, dict]:
        # Schema-konform (`^[a-z][a-z0-9_]*$`, A8-Konsistenz): community_id
        # darf Bindestriche enthalten (reine Anzeige-/Ordner-ID), persona_key
        # nicht.
        safe_suffix = community_id.replace("-", "_").lower()
        pool = {}
        for i in range(size):
            slot, archetype, play_style = self._STARTER_ARCHETYPES[i % len(self._STARTER_ARCHETYPES)]
            pk = f"{slot}_{safe_suffix}" if i < len(self._STARTER_ARCHETYPES) else f"{slot}{i}_{safe_suffix}"
            pool[pk] = {
                "_fixture_note": "SIMULIERT/DEMO -- kein echter Modellaufruf (PLAN-CRITIC.md A6)",
                "real_name": pk,
                "archetype": f"SIMULIERT: {archetype}",
                "play_style": f"SIMULIERT: {play_style}",
                "charwunsch": "SIMULIERT/DEMO -- kein Erschaffungsdialog durchlaufen (Community-Bootstrap ohne Live-Go).",
                # R04-Restintegrationsfix (WEGKARTE §4 A6, REVIEW-P2R.md
                # R-A): `plays_char={}` verletzt das reale Persona-State-
                # Schema (Pflichtfelder save_file/character_id/name/
                # callsign) und liess `c` mit ValidationError abstuerzen.
                # Technisch NEUTRALER Platzhalter (kein erfundener
                # Charakter/keine echte Chrononaut-Bindung) im selben Stil
                # wie `onboarding.ensure_participant_persona_state`s
                # "TECHNISCHER PLATZHALTER"-Konvention -- diese Start-
                # Persona ist ein Entwurf, KEINE spielbare Figur, bis sie
                # ueber denselben autoritativen Weg wie `n`/`i` real
                # erschaffen wird (Plan-Critic A5).
                "plays_char": {
                    "save_file": "NOCH_NICHT_ERSCHAFFEN",
                    "character_id": "NOCH_NICHT_ERSCHAFFEN",
                    "name": "NOCH_NICHT_ERSCHAFFEN",
                    "callsign": "NOCH_NICHT_ERSCHAFFEN",
                },
            }
        return pool

    # C4 (P2-Community-Ergebnisuebergabe 2026-09-25, 01_AUFTRAG §3 C4,
    # 02_ABNAHME 'Demo/Produkt'): getrennter, statisch DISTINKTER Pool fuer
    # eine bewusst gewaehlte produktive Neuanlage -- kein Bezug zu/keine
    # Uebernahme von `_STARTER_ARCHETYPES` (die bleiben ausschliesslich
    # SIMULIERT/DEMO). Statische unterschiedliche Profile genuegen (02 §3:
    # "keine weitere Modell-Biografiegeneration noetig") -- kein generativer
    # Modellaufruf fuer Biographien.
    _PRODUCTION_STARTER_ARCHETYPES = (
        ("vanguard", "Sturmlaeuferin", "furchtlos-vorpreschend"),
        ("shadow", "Schattenlaeufer", "verstohlen-lauernd"),
        ("oracle", "Orakel-Deuterin", "gruebelnd-weitsichtig"),
        ("forge", "Schmiedemeister", "beharrlich-handwerklich"),
        ("warden", "Waechterin", "schuetzend-wachsam"),
        ("rift", "Riftlaeufer", "ruhelos-neugierig"),
        ("anchor", "Ankerpunkt", "besonnen-verlaesslich"),
        ("spark", "Funkenwerferin", "spontan-kreativ"),
    )

    def _production_starter_pool(self, community_id: str, size: int) -> dict[str, dict]:
        """C4: bewusst GETRENNTE produktive Startpopulation -- gewaehlt, wenn
        ein Mensch bei einer NEUEN, bereits Live-konfigurierten Community
        explizit 'p' waehlt (s. `_cmd_community`). KEINE Uebernahme der
        SIMULIERT/DEMO-Profile, aber auch KEIN generativer Modellaufruf fuer
        Biographien -- statische unterschiedliche Profile sind hinreichend
        (02_PRODUKTVERTRAG §3)."""
        safe_suffix = community_id.replace("-", "_").lower()
        pool = {}
        for i in range(size):
            slot, archetype, play_style = self._PRODUCTION_STARTER_ARCHETYPES[
                i % len(self._PRODUCTION_STARTER_ARCHETYPES)
            ]
            pk = f"{slot}_{safe_suffix}" if i < len(self._PRODUCTION_STARTER_ARCHETYPES) else f"{slot}{i}_{safe_suffix}"
            pool[pk] = {
                "_fixture_note": (
                    "PRODUKTIV -- bewusst gewaehlte getrennte Startpopulation, keine "
                    "Demo-/Legacy-Uebernahme (01 §3 C4)."
                ),
                "real_name": pk,
                "archetype": archetype,
                "play_style": play_style,
                "charwunsch": (
                    "Noch kein Erschaffungsdialog gefuehrt -- eigener Chrononaut wird im "
                    "ersten echten SL-Dialog erschaffen."
                ),
                "plays_char": {
                    "save_file": "NOCH_NICHT_ERSCHAFFEN",
                    "character_id": "NOCH_NICHT_ERSCHAFFEN",
                    "name": "NOCH_NICHT_ERSCHAFFEN",
                    "callsign": "NOCH_NICHT_ERSCHAFFEN",
                },
            }
        return pool

    def _cmd_community(self) -> None:
        """F5/A7/A10 (WEGKARTE §6/§8, PLAN-CRITIC-DURCHSTICH.md HINWEIS,
        Option (i)): verdrahtet `bootstrap_community` mit einem klar
        markierten SYNTHETISCHEN Demo-Payload offline (01 §M2: 'Offline wird
        dies mit klar markierten Eingangsdaten geprueft') -- jetzt mit einem
        echten POOL distinkter Start-Personas (02 §3), nicht nur einem
        einzigen Demo-Eintrag fuer den aufrufenden Teilnehmer. Echte
        Erzeugung von Motivations-/Stil-Payloads per echtem Modellaufruf
        bleibt weiterhin EXPLIZIT ausserhalb dieser Fertigstellung
        (PLAN-CRITIC.md A6: keine erfundene Karriere) -- der Demo-Payload
        hier ist statisch, unmissverstaendlich als SIMULIERT gekennzeichnet,
        kein Live-Schritt. Der aufrufende MENSCH bekommt HIER keine eigene
        Stamm-Persona (er erschafft/importiert seine eigene Figur separat
        ueber [n]/[i], 02 §2: Person-/Persona-Identitaet bleiben getrennt)."""
        if self._lab_active_guard("Neue Spielgemeinschaft"):
            return
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            self._print(
                "Neue Spielgemeinschaft: erfordert eine konfigurierte Laufumgebung "
                "(run_dir/states_dir/schema_path) — hier nicht konfiguriert, kein "
                "Community-Bootstrap (Live-Setup, s. docs/mmo-sim.md)."
            )
            return

        from ..core.persona_state import PersonaStateStore
        from ..domain.zeitriss.community_bootstrap import bootstrap_community
        from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
        from ..domain.zeitriss.community_creation import advance_community_creation

        ps_store = PersonaStateStore(schema_path=self.schema_path)
        today = datetime.date.today().isoformat()
        community_id = f"community-{self.participant_id}"
        generation = 1
        community_dir = self.run_dir / "community"
        # C4 (P2-Community-Kontinuitaet 2026-09-25, 01_AUFTRAG §3A): `c`
        # unterscheidet SICHTBAR eine neue Gemeinschaft von einem
        # Fortsetzen einer vorhandenen -- `bootstrap_community` selbst ist
        # bereits idempotent (kein Doppelroster), `peek_bootstrap` liest nur
        # VORHER, ohne selbst etwas anzulegen.
        existing = peek_bootstrap(community_dir, community_id)
        # C4 (01 §3 C4, 'Beschriftung nicht gleichzeitig kein Modellaufruf
        # behaupten und danach Modelle starten'): wird VOR der Bootstrap-
        # Entscheidung gebraucht, s.u.
        live_configured = self.gm_transport_factory is not None and self.persona_driver_factory is not None
        if existing is not None:
            self._print(
                f"Fortsetzen: bestehende Spielgemeinschaft {community_id!r} "
                f"({len(existing.personas_written)} Mitglieder bereits geplant/initialisiert) "
                "-- keine neue Population, gepinnte Identitaeten bleiben unveraendert."
            )
            # `bootstrap_community` ignoriert `target_personas` vollstaendig,
            # sobald bereits ein Plan existiert (s. dessen Docstring) -- der
            # konkrete Pool hier ist bei einem Fortsetzen folgenlos.
            starter_pool = self._synthetic_starter_pool(community_id, size=8)
            # R3 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
            # §5): eine bestehende Gemeinschaft, die (noch offline ODER als
            # bewusstes 'd') ohne je eine explizite Live-Uebernahmeentscheidung
            # entstanden ist, darf bei jetzt konfigurierter Live-Anbindung
            # NICHT still in echte, budgetpflichtige Modellerschaffung
            # uebergehen ("Modellkonfiguration allein ist keine Adoption").
            # Ein bereits gepinnter Marker (s. `_read_live_adoption_origin`)
            # macht ein GESUNDES Fortsetzen weiterhin bequem -- fragt NICHT
            # jedes Mal neu.
            if live_configured and self._read_live_adoption_origin(community_dir, community_id) is None:
                origin = self._ask_live_starter_origin_choice(
                    f"Fortsetzen der noch nicht bewusst uebernommenen Bestandsgemeinschaft "
                    f"{community_id!r} mit jetzt konfigurierter Live-Anbindung"
                )
                if origin is None:
                    self._print(
                        "Uebernahmeentscheidung ungueltig/abgebrochen -- bestehende Gemeinschaft "
                        "bleibt unveraendert, KEIN Modellaufruf fuer diesen Aufruf. Erneut 'c' "
                        "aufrufen und [d]/[p] eindeutig waehlen."
                    )
                    return
                self._write_live_adoption_origin(community_dir, community_id, origin)
                self._print(
                    f"Uebernahme bestaetigt: Herkunft={origin!r} dauerhaft gepinnt "
                    "(Bestandsgemeinschaft, 01 §3 C4)."
                )
        else:
            self._print(f"Neue Spielgemeinschaft {community_id!r} wird angelegt.")
            if live_configured:
                # C4 (P2-Community-Ergebnisuebergabe 2026-09-25, 01_AUFTRAG
                # §3A/§3C4, 02_ABNAHME 'Demo/Produkt'): eine NEUE Community
                # mit bereits konfigurierter Live-Anbindung darf die
                # SIMULIERT/DEMO-Profile NICHT still fuer das konfigurierte
                # Modellspiel uebernehmen -- genau EINE bewusste, gefuehrte
                # Entscheidung (kein Fragenkatalog): explizite Uebernahme mit
                # gepinnter Herkunft ODER getrennte produktive Neuanlage.
                origin = self._ask_live_starter_origin_choice(
                    f"Neue Spielgemeinschaft {community_id!r} mit konfigurierter Live-Anbindung"
                )
                if origin is None:
                    self._print(
                        "Startpopulation-Entscheidung ungueltig/abgebrochen -- kein Bootstrap, "
                        "KEIN Modellaufruf fuer diesen Aufruf. Erneut 'c' aufrufen und [d]/[p] "
                        "eindeutig waehlen."
                    )
                    return
                if origin == "production":
                    starter_pool = self._production_starter_pool(community_id, size=8)
                    self._print(
                        "Startpopulation: getrennte PRODUKTIVE Neuanlage bewusst gewaehlt "
                        "(keine Demo-/Legacy-Uebernahme, 01 §3 C4)."
                    )
                else:
                    starter_pool = self._synthetic_starter_pool(community_id, size=8)
                    self._print(
                        "Startpopulation: SIMULIERT/DEMO-Profile bewusst als Startpopulation "
                        "uebernommen (Herkunft bleibt gepinnt, 01 §3 C4)."
                    )
                self._write_live_adoption_origin(community_dir, community_id, origin)
            else:
                # Ohne Live-Anbindung bleibt der Erschaffungsdialog ohnehin
                # ohne jeden Modellaufruf (s.u.) -- reine Offline-Demo,
                # unveraendert wie zuvor, keine Entscheidung noetig (und
                # KEIN Adoptionsmarker -- eine spaetere Live-Konfiguration
                # fuer dieselbe Gemeinschaft braucht dann die obige
                # Fortsetzen-Entscheidung, s.o.).
                starter_pool = self._synthetic_starter_pool(community_id, size=8)
        result = bootstrap_community(
            community_dir, community_id, generation, starter_pool,
            ps_store, self.states_dir, today,
        )
        self._print(f"Bootstrap: {result.reason} (personas: {result.personas_written})")
        # P2-Community-Erstgeneration (2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md):
        # der Bootstrap oben schreibt NUR Profil-ENTWUERFE (kein Current-Save,
        # keine Chrononaut-ID -- nicht spielbereit). Jede geplante Persona wird
        # jetzt durch ihren EIGENEN, fortsetzbaren SL-Erschaffungsdialog
        # gefuehrt (Persona-Treiber statt Mensch, s. `domain/zeitriss/
        # community_creation.py`). Ohne konfigurierte gm_transport_factory/
        # persona_driver_factory ODER ohne Admission-Freigabe (kein
        # `lab.status.json`) liefert JEDE Persona sofort 'no_driver'/
        # 'blocked' ohne jeden Modellaufruf -- identisch ehrlicher
        # Teilstand wie beim menschlichen Erschaffungsdialog, KEINE
        # Verhaltensaenderung fuer eine unkonfigurierte Laufumgebung
        # (Baseline-Beobachtung `observe_community_entry.py` bleibt
        # unveraendert: 8 Entwuerfe, 0 Current-Saves, ohne Live-Setup).
        if live_configured:
            self._print(
                "Persona-getriebene Erschaffung: echte SL-/Persona-Anbindung konfiguriert -- "
                "die geplanten Startprofile erhalten JETZT echte, budgetpflichtige Anfragen "
                "(kein Offline-Demo mehr fuer den Erschaffungsdialog selbst)."
            )
        else:
            self._print(
                "Persona-getriebene Erschaffung: keine SL-/Persona-Anbindung konfiguriert -- "
                "kein echter Modellaufruf moeglich (nur Profilentwuerfe, s. docs/mmo-sim.md)."
            )
        # C4 ('ein begrenzter Fortschrittsschritt ... erlaubt Rueckkehr,
        # ohne erst saemtliche acht Dialoge absolvieren zu muessen'):
        # Betreiber-/Startkonfiguration ueber ENV, Default `None` = bisheriges
        # Verhalten (alle geplanten Personas in einem `c`-Aufruf), keine
        # erzwungene Verhaltensaenderung ohne explizite Konfiguration.
        step_limit, limit_rejected = self._community_step_limit()
        if limit_rejected is not None:
            # Korrektur (P2-Community-Ergebnisuebergabe 2026-09-25): ein
            # EXPLIZIT gesetztes, aber ungueltiges Limit wird kontrolliert
            # abgelehnt -- NICHT still als unbegrenzt (voller Pool)
            # ausgefuehrt. Bootstrap oben ist bereits gelaufen (idempotent,
            # kein Modellaufruf); nur die budgetpflichtige Erschaffungs-
            # Fortsetzung fuer DIESEN Aufruf entfaellt.
            self._print(
                f"Begrenzter Fortschrittsschritt abgelehnt: {limit_rejected} -- kontrolliert "
                "abgelehnt, KEIN unbegrenzter Fortschrittsschritt fuer diesen Aufruf. "
                "MMO_SIM_COMMUNITY_STEP_LIMIT auf eine gueltige positive Ganzzahl setzen "
                "oder entfernen (= unbegrenzt) und 'c' erneut aufrufen."
            )
            return
        creation_outcomes = advance_community_creation(
            run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
            onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
            community_id=community_id, generation=generation,
            planned_persona_keys=list(result.personas_written),
            gm_transport_factory=self.gm_transport_factory,
            persona_driver_factory=self.persona_driver_factory,
            print_fn=self._print, limit=step_limit,
        )
        by_status: dict[str, int] = {}
        for oc in creation_outcomes:
            by_status[oc.status] = by_status.get(oc.status, 0) + 1
        # W22 (Reserve-Reparatur, F05/T7 §3b): vorher landete hier der
        # ROHE `dict(sorted(by_status.items()))`-Repr ("{'error': 8}") direkt
        # in der Spieleransicht -- kein echter Fehlertext, nur Python-Status-
        # Syntax. Redigiert jetzt zu einer verstaendlichen, ehrlichen Zeile
        # je Lagebild, OHNE den Live-Pfad offline lauffaehig zu machen (0
        # zusaetzliche Calls, keine Semantikaenderung an `community_creation.
        # advance_community_creation`). `no_driver` (keine Factories
        # konfiguriert) und `error` bleiben bewusst unterschiedliche,
        # jeweils ehrliche Meldungen.
        #
        # R5P02-Fix (ZEITRISS TERMINAL-UX1-R6-FERTIGSTELLUNG, General-Befund
        # 'no_call_claim_after_attempt'): die vorherige Annahme, `attempted`
        # duerfe HIER immer beim Default `False` bleiben, war UNVOLLSTAENDIG
        # -- sie stimmte nur fuer die beiden echten Fabrikbau-Faelle
        # (`gm_transport_factory`/`persona_driver_factory` wirft VOR jedem
        # Request, reason-Praefix `_PRE_REQUEST_CREATION_ERROR_PREFIXES`
        # unten) UND fuer ein fehlendes Bootstrap-Profil. Ein `error`-Outcome
        # aus `run_admitted_creation_dialog` (SL-Anfrage NACH `request_
        # ledger.begin()`+echtem `gm_transport.turn()` fehlgeschlagen) ODER
        # aus `advance_community_creation`s eigenem Batch-Catch (Fehler
        # WAEHREND eines bereits laufenden Erschaffungsversuchs) ist dagegen
        # ECHT belegt versucht -- die Sammelzeile behauptete bisher trotzdem
        # pauschal "kein Modellaufruf", obwohl `core/creation_service.py`
        # den sicheren "bereits versuchter Aufruf"-Hinweis fuer genau diese
        # Faelle bereits VORHER je Persona ueber `print_fn` ausgegeben hatte
        # (Widerspruch in derselben Ausgabe). Nur wenn ALLE `error`-Outcomes
        # dieses Aufrufs NACHWEISLICH vor-Anfrage sind (bekannte, exakte
        # Grundursachen-Praefixe, s.u.), bleibt `attempted=False` wahr.
        # Jeder andere/unbekannte `error`-Grund gilt als belegt versucht
        # (sicherer Default, keine falsche Nullkostenzusage) -- KEIN neuer
        # Statuskern, nur eine Textauswertung bereits vorhandener, von
        # `community_creation.py` zurueckgegebener `reason`-Strings; die
        # rohen `reason`-Texte selbst (koennen beliebige Exception-Nachrichten
        # enthalten) werden an dieser Stelle NIE ausgegeben, nur fuer den
        # `.startswith`-Abgleich gegen feste, bekannte Literale verwendet.
        if by_status.get("no_driver", 0):
            self._print(
                "Persona-Erschaffung nicht moeglich: benoetigt eine konfigurierte Live-Anbindung "
                "(gm_transport_factory + persona_driver_factory) -- dieser Pfad ist kein Offline-"
                "Demo. Fortschritt/Community bleibt erhalten, kein automatischer weiterer Versuch."
            )
        elif by_status.get("error", 0):
            error_reasons = [oc.reason for oc in creation_outcomes if oc.status == "error"]
            attempted = not all(self._is_confirmed_pre_request_creation_error(r) for r in error_reasons)
            self._print(
                self._opaque_boundary_error(
                    "Persona-getriebene Erstgeneration (SL-Erschaffungsdialog je Persona)",
                    attempted=attempted,
                )
            )
        else:
            self._print(
                "Persona-getriebene Erstgeneration (echter SL-Erschaffungsdialog je Persona): "
                f"{by_status.get('completed', 0) + by_status.get('already_ready', 0)} von "
                f"{len(creation_outcomes)} Personas tischbereit, {by_status.get('paused', 0)} "
                f"pausiert, {by_status.get('blocked', 0)} blockiert (Admission-Gate blocked)."
            )
        # C4 ('Bereits fertige und offene Mitglieder sichtbar'):
        finished = [oc.persona_key for oc in creation_outcomes if oc.status in ("already_ready", "completed")]
        open_ = [oc.persona_key for oc in creation_outcomes if oc.status not in ("already_ready", "completed")]
        self._print(f"Fertig/tischbereit: {finished}")
        self._print(f"Noch offen/wartend: {open_}")

    def _community_step_limit(self) -> tuple[int | None, str | None]:
        """C4: optionale Betreiber-/Startkonfiguration fuer einen begrenzten
        Fortschrittsschritt (01 §3 C4: 'Anzahl ist eine Betreiber-/
        Startkonfiguration, nie eine Fuenferlobbyregel'). Unveraendert
        (`None`, alle geplanten Personas in einem Aufruf) ohne explizite
        Konfiguration (`MMO_SIM_COMMUNITY_STEP_LIMIT` nicht gesetzt).

        Korrektur (P2-Community-Ergebnisuebergabe 2026-09-25,
        MAIN-DATENWEGENTSCHEIDUNG.md §4, REVIEW-COMMUNITY-ERGEBNISUEBERGABE.md
        §3): ein EXPLIZIT gesetzter, aber ungueltiger Wert (keine Ganzzahl
        ODER nicht positiv) fiel zuvor STILL auf `None` (unbegrenzt, voller
        Pool) zurueck -- ununterscheidbar vom bewusst unkonfigurierten
        Default. Das ist genau das verbotene Verhalten ('ungueltiges
        explizites Limit NICHT still als unbegrenzt ausfuehren'). Liefert
        jetzt `(limit, rejection_reason)`: `rejection_reason` ist `None` fuer
        den legitimen unkonfigurierten Default UND fuer ein gueltiges
        positives Limit; er ist GESETZT (und `limit` dann `None`) NUR fuer
        einen tatsaechlich vorhandenen, aber ungueltigen ENV-Wert -- der
        Aufrufer (`_cmd_community`) MUSS diesen Fall kontrolliert ablehnen
        (keine Erschaffungs-Fortsetzung fuer diesen Aufruf), NICHT selbst
        einen impliziten Ersatzwert waehlen."""
        raw = os.environ.get("MMO_SIM_COMMUNITY_STEP_LIMIT")
        if raw is None:
            return None, None
        try:
            value = int(raw)
        except ValueError:
            return None, (
                f"MMO_SIM_COMMUNITY_STEP_LIMIT={raw!r} ist keine gueltige Ganzzahl"
            )
        if value <= 0:
            return None, (
                f"MMO_SIM_COMMUNITY_STEP_LIMIT={value} ist nicht positiv"
            )
        return value, None

    def _ask_live_starter_origin_choice(self, prompt_context: str) -> str | None:
        """R3 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
        §5): EIN gemeinsamer, ausdruecklicher [d/p]-Herkunftsentscheid fuer
        BEIDE Staellen, die ihn brauchen (neue Community MIT Live-Anbindung,
        Fortsetzen einer noch nicht bewusst uebernommenen Bestandsgemeinschaft
        MIT jetzt konfigurierter Live-Anbindung). Liefert `"production"`
        NUR fuer `p`/`prod`/`produktiv`, `"demo"` NUR fuer `d`/`demo` -- JEDE
        andere Eingabe (leer, ungueltig, `EndOfInput` durch den Aufrufer NICHT
        gefangen) liefert `None`. Der Aufrufer MUSS `None` kontrolliert
        ablehnen (kein Bootstrap/keine Live-Erschaffungs-Fortsetzung fuer
        diesen Aufruf) -- diese Funktion selbst bucht/pinnt nichts, sie
        beantwortet nur die Eingabe.

        F02 (W18, Brief §Fachvertrag 4): die Eingabe laeuft ueber denselben
        zentralen Leser wie jeder andere Prompt -- '?'/'/hilfe'/'/stand'/
        '/verlauf' werden DORT bereits lokal beantwortet (0 Calls, dieselbe
        Frage wird erneut gestellt). '/zurueck'/'/abbrechen'/'/pause' fallen
        auf denselben bestehenden `None`-Vertrag zurueck wie JEDE andere
        nicht passende Eingabe (keine neue Sonderbedeutung, kein
        Modell-/Provider-Call, kein echter Vorlauf) -- der Aufrufer lehnt
        kontrolliert ab, unveraendert zum bisherigen Verhalten."""
        choice, control = self._readline_with_controls(
            f"{prompt_context}: bewusste Herkunftsentscheidung vor der ersten "
            "Modellanfrage -- [d] SIMULIERT/DEMO-Profile bewusst uebernehmen "
            "(Herkunft bleibt gepinnt) oder [p] als produktiv bestaetigen/neu "
            "anlegen (kein Demo-Bezug)? [d/p]: ",
            context="Herkunftsentscheidung",
        )
        if control in ("zurueck", "abbrechen", "pause"):
            return None
        choice = choice.strip().lower()
        if choice in ("p", "prod", "produktiv"):
            return "production"
        if choice in ("d", "demo"):
            return "demo"
        return None

    def _live_adoption_path(self, community_dir: Path) -> Path:
        return community_dir / "bootstrap__live_adoption.json"

    def _read_live_adoption_origin(self, community_dir: Path, community_id: str) -> str | None:
        """R3: liest den gepinnten Herkunfts-Marker (s.
        `_write_live_adoption_origin`) -- `None` sowohl fuer 'noch nie
        gepinnt' ALS AUCH fuer einen Marker einer fremden `community_id`
        (Kollisionsschutz, analog `community_bootstrap.peek`)."""
        p = self._live_adoption_path(community_dir)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict) or data.get("community_id") != community_id:
            return None
        origin = data.get("origin")
        return origin if origin in ("demo", "production") else None

    def _write_live_adoption_origin(self, community_dir: Path, community_id: str, origin: str) -> None:
        """R3: kleiner Sidecar-Marker (bewusst GETRENNT von
        `bootstrap__plan.json`, das `community_bootstrap.bootstrap_community`
        EINMALIG gepinnt und alleinig schreibt) -- haelt fest, dass fuer
        `community_id` bereits EINE ausdrueckliche Live-Herkunftsentscheidung
        ('demo' ODER 'production') getroffen wurde, damit ein gesundes
        Fortsetzen bequem bleibt (fragt NICHT jedes Mal neu)."""
        community_dir.mkdir(parents=True, exist_ok=True)
        self._live_adoption_path(community_dir).write_text(
            json.dumps({"community_id": community_id, "origin": origin, "pinned_ts": time.time()},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _lobby_initiative_step_limit(self) -> int:
        """01_AUFTRAG_LOBBY_INITIATIVE.md §4 A ("Betreiber-Initiativlimit =
        Betriebsbudget"): explizite Betreiber-/Startkonfiguration -- ANDERS
        als `_community_step_limit` (dort ist "unbegrenzt" der legitime
        Default) darf eine Lobbyinitiative NIE unbegrenzt laufen (kein
        leerer Inferenz-Endlosloop bei z.B. staendig neu vorschlagenden
        Personas) -- ein fehlender/ungueltiger ENV-Wert faellt deshalb auf
        einen kleinen POSITIVEN Default zurueck, nicht auf unbegrenzt."""
        raw = os.environ.get("MMO_SIM_LOBBY_INITIATIVE_LIMIT")
        if raw is None:
            return 12
        try:
            value = int(raw)
        except ValueError:
            return 12
        return value if value > 0 else 12

    def _play_bound_table(
        self, lobby, table, offer_events: list[dict],
        source_offer_id: str | None, active_saves: dict[str, dict],
    ) -> None:
        """Duenner Wrapper um `core.lobby_flow.play_bound_table` (Headless-/
        Lab-Lobbydurchstich, Bau-GO 2026-09-27, H-A) -- die eigentliche Logik
        wurde dorthin extrahiert, damit TUI UND Lab GENAU DENSELBEN Code
        aufrufen (kein zweiter Spielstart-Pfad). `self` erfuellt die
        `session`-Schnittstelle, die `lobby_flow` erwartet. TUI ruft
        weiterhin OHNE `ai_personas`-Einschraenkung auf (unveraendertes
        Verhalten, H01) -- diese Einschraenkung ist ein reines Lab-Feature."""
        from ..core import lobby_flow
        lobby_flow.play_bound_table(self, lobby, table, offer_events, source_offer_id, active_saves)

    def _resume_consistency_hold_reason(
        self, lobby, table, derivation, resolved_chrononaut_ids: dict[str, str],
    ) -> str | None:
        """Duenner Wrapper um `core.lobby_flow.resume_consistency_hold_reason`
        (s. `_play_bound_table`-Docstring -- dieselbe Extraktionsbegruendung)."""
        from ..core import lobby_flow
        return lobby_flow.resume_consistency_hold_reason(self, lobby, table, derivation, resolved_chrononaut_ids)

    def _cmd_lobby_initiative(self) -> None:
        """Duenner Wrapper um `core.lobby_flow.run_lobby_window` (Headless-/
        Lab-Lobbydurchstich, Bau-GO 2026-09-27, H-A) -- die vollstaendige
        Orchestrierung (vorher hier inline) wurde UI-neutral extrahiert, s.
        `mmo_sim/core/lobby_flow.py`-Moduldocstring fuer die volle
        Begruendung. TUI formatiert/druckt bereits waehrend des Ablaufs
        (`self._print`, `session` ist hier `self`) -- das zurueckgegebene
        `LobbyWindowOutcome` traegt keine zusaetzliche Information, die TUI
        noch drucken muesste (Headless wertet es dagegen aus, um zu
        entscheiden, ob ein weiteres Fenster folgt).

        H-D/H06 (EIN Writer pro Daten-/run-Bereich): ist fuer dieses
        `run_dir` gerade ein Lab-Lauf aktiv (lebender `lab.lock.json`-
        Inhaber), lehnt dieser manuelle Weg kontrolliert ab, statt heimlich
        zum zweiten Schreiber zu werden -- lesende `lab status`/`lab attach`
        bleiben davon unberuehrt."""
        if self.run_dir is not None:
            from ..lab.runner import active_lock_pid
            # F4-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `exclude_pid`
            # konsistent zur SCHWESTER-Aufrufstelle `_cmd_local_round` setzen
            # -- sonst blockiert sich ein Prozess, der `LabRunner` UND
            # `TuiSession` fuer dasselbe `run_dir` selbst konstruiert (z.B.
            # ein Test), faelschlich selbst (H-D beschreibt zwei
            # VERSCHIEDENE Prozesse, s. `active_lock_pid`-Docstring).
            pid = active_lock_pid(self.run_dir, exclude_pid=os.getpid())
            if pid is not None:
                self._print(
                    f"Lobby-Initiative: ein aktiver Lab-Lauf (pid={pid}) kontrolliert diese "
                    "Datenablage — kein zweiter schreibender Controller (H-D). Nur lesende "
                    "Ansicht moeglich ('python scripts/mmo_sim.py lab status/attach')."
                )
                return
        from ..core import lobby_flow
        lobby_flow.run_lobby_window(self)

    def _cmd_settings(self) -> None:
        """I1/I3: Status/Einstellungen -- reale, lokal verfuegbare Angaben."""
        self._print(f"Teilnehmer-ID: {self.participant_id}")
        entries = catalog.list_for_participant(self.catalog_dir, self.participant_id)
        self._print(f"Katalog-Eintraege: {len(entries)}")
        if self.run_dir is None:
            self._print("Laufumgebung (run_dir): nicht konfiguriert (kein Lab-Status verfuegbar).")
            return
        from ..core.admission import read_admission_block
        from ..lab.runner import read_status
        blocked, reason = read_admission_block(self.run_dir)
        self._print(f"Admission-Gate: {'blockiert (' + str(reason) + ')' if blocked else 'frei'}")
        status = read_status(self.run_dir)
        if status is not None:
            self._print(f"Lab-Status: turns_used={status.turns_used} usd_spent={status.usd_spent:.4f} running={status.running}")

    def run(self) -> int:
        self._maybe_show_first_run_intro()
        while not self._quit:
            resume = self._build_resume_card()
            self._print(render_boot_menu(resume))
            try:
                raw_choice = self._readline("Auswahl: ").strip()
            except EndOfInput:
                self._print("\nEingabe beendet (EOF) — sicher pausiert, kein weiterer Modellaufruf.")
                return 0
            # UX04 (02 §C): '?'/'/hilfe' an der Boot-Auswahl zeigt
            # Kontexthilfe und zeigt danach erneut dasselbe Menue -- kein
            # Zustand geht dabei verloren (es gibt an dieser Stelle noch
            # keinen offenen Teilschritt). Exakter Vergleich (nicht
            # Teilstring) — ein Fragezeichen irgendwo in einer anderen
            # Eingabe bleibt unveraendert diese andere Eingabe.
            if raw_choice.strip().lower() in ("?", "/hilfe", "/?"):
                self._print(self._control_help_text("Hauptmenue"))
                continue
            # BLOCKER 2 (WEGKARTE): 'l' erlaubt optionale weitere Tokens in
            # DERSELBEN Auswahlzeile ('l <teilnehmer-id> [...]' bzw.
            # 'l persona:<id>' fuer einen KI-Gast) -- kein zusaetzlicher
            # Eingabeschritt, damit bestehende Solo-Skripte/-Tests (nur 'l')
            # unveraendert bleiben.
            tokens = raw_choice.split()
            choice = tokens[0].lower() if tokens else ""
            extra_tokens = tokens[1:]
            try:
                if choice == "n":
                    self._cmd_new_or_switch_character()
                elif choice == "i":
                    self._cmd_import()
                elif choice == "e":
                    self._cmd_export()
                elif choice == "g":
                    self._cmd_local_round_setup()
                elif choice == "l":
                    self._cmd_local_round(extra_tokens)
                elif choice == "c":
                    self._cmd_community()
                elif choice == "b":
                    self._cmd_lobby_initiative()
                elif choice == "s":
                    self._cmd_settings()
                elif choice in ("x", "q"):
                    self._quit = True
                # UX01/UX03 (02 §A, MENUE_ENTSCHEIDUNG.md): die EINE
                # KISS-Zielhierarchie als ZUSAETZLICHE Worteintraege --
                # dispatcht additiv auf dieselben, unveraenderten Methoden
                # wie die Einzelbuchstaben oben (keine zweite Spiellogik,
                # kein entfernter alter Hotkey).
                elif choice in ("spielen", "play"):
                    self._cmd_menu_spielen()
                elif choice in ("charaktere", "charaktere.", "characters"):
                    self._cmd_menu_charaktere()
                elif choice in ("einstellungen", "settings"):
                    self._cmd_settings()
                elif choice in ("fortsetzen", "resume"):
                    self._cmd_menu_fortsetzen()
                elif choice in ("registrieren", "register"):
                    self._cmd_register_new_person()
                elif choice in ("einfuehrung", "tutorial"):
                    self._cmd_show_intro_again()
                elif choice in ("beenden", "quit", "exit"):
                    self._quit = True
                elif choice == "":
                    continue
                # R4 (T-Befund 1, UX04/05, Korrekturzyklus 1): die Erst-
                # fuehrung bewirbt `/stand`/`/verlauf`/`/pause` "an jeder
                # Eingabe" -- im Hauptmenue fielen sie vorher auf
                # "Unbekannte Auswahl" (falsche Universalzusage). `/stand`
                # funktioniert hier ECHT (derselbe bereits geladene
                # `resume`-Stand wie die Menuezeile oben); `/verlauf`/
                # `/pause` beziehen sich auf einen laufenden Spielabschnitt,
                # den es am Hauptmenue noch nicht gibt -- ehrlicher Hinweis
                # statt falscher Zusage, kein "Unbekannte Auswahl" mehr.
                elif choice == "/stand":
                    if resume is None:
                        self._print("Kein aktueller Stand vorhanden.")
                    else:
                        detail = render_boot_menu(resume)
                        stand_lines = [ln for ln in detail.splitlines() if ln.strip().startswith("Fortsetzen:")]
                        self._print(stand_lines[0].strip() if stand_lines else "Stand vorhanden, keine Fortsetzen-Zeile.")
                elif choice == "/verlauf":
                    self._print(
                        "/verlauf zeigt den bisherigen Gespraechsverlauf nur WAEHREND eines laufenden "
                        "Spielabschnitts (am Spielzug-Prompt) -- im Hauptmenue gibt es noch keinen Verlauf."
                    )
                elif choice == "/pause":
                    self._print(
                        "/pause unterbricht kontrolliert einen laufenden Spielabschnitt (am Spielzug-"
                        "Prompt) -- im Hauptmenue gilt dafuer 'beenden' oder EOF (Strg-D)."
                    )
                else:
                    self._print(f"Unbekannte Auswahl: {choice!r}")
            except EndOfInput:
                self._print("\nEingabe beendet (EOF) waehrend eines Untermenues — sicher pausiert.")
                return 0
        return self.exit_code
