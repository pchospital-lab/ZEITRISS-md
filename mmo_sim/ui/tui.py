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
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..domain.zeitriss import catalog, import_export, onboarding
from ..domain.zeitriss import saves as zeitriss_saves
from ..domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy


@dataclass
class ResumeCard:
    community_id: str | None
    participant_id: str | None
    chrononaut_id: str | None
    last_valid_save_summary: str | None
    open_section_id: str | None = None


def render_boot_menu(resume: ResumeCard | None) -> str:
    """11 §2: 'Bei vorhandenen Daten zuerst eine verstaendliche Fortsetzen-
    Karte zeigen ... Darunter alternative Wege.'"""
    lines = ["ZEITRISS MMO-Sim"]
    if resume is not None and resume.community_id:
        stand = resume.last_valid_save_summary or "kein gueltiger Stand"
        offen = f" (Abschnitt {resume.open_section_id} unterbrochen)" if resume.open_section_id else ""
        lines.append(f"  Fortsetzen: {resume.community_id} · {resume.participant_id} · {resume.chrononaut_id} — {stand}{offen}")
    lines.append("  [n] Figur wechseln / neu erschaffen")
    lines.append("  [i] JSON importieren (Datei-Pfad oder Mehrzeilentext)")
    lines.append("  [e] Eigenen Save anzeigen / exportieren")
    lines.append("  [l] Gemeinsam an diesem Geraet spielen (lokale Runde) -- optional weitere")
    lines.append("      Teilnehmer in derselben Zeile: 'l <teilnehmer-id> persona:<id> ...'")
    lines.append("  [c] Neue Spielgemeinschaft")
    lines.append("  [s] Status / Einstellungen")
    lines.append("  [x] Beenden")
    return "\n".join(lines)


class EndOfInput(Exception):
    """Signalisiert EOF/Pipeline-Ende — vom Aufrufer als kontrollierte Pause
    zu behandeln (A11/A16: kein Absturz bei Skript-/Pipe-Eingabe)."""


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
    ):
        self.onboarding_dir = Path(onboarding_dir)
        self.catalog_dir = Path(catalog_dir)
        self.participant_id = participant_id
        self._input = input_fn or input
        self._print = print_fn or print
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

    def _readline(self, prompt: str) -> str:
        try:
            return self._input(prompt)
        except EOFError as e:
            raise EndOfInput() from e

    def _build_resume_card(self) -> ResumeCard | None:
        """11 §2: eine verstaendliche Fortsetzen-Karte aus vorhandenen
        Daten bauen -- vorher wurde IMMER `render_boot_menu(None)` gerufen
        (Review-Befund I3: 'Fortsetzen-Karte wird dort nie befuellt')."""
        chrononaut_id = catalog.last_selected(self.catalog_dir, self.participant_id)
        state = onboarding.peek(self.onboarding_dir, self.participant_id)
        final_save = state.final_save if state is not None else None
        if chrononaut_id is None and final_save is None:
            return None
        summary = None
        if final_save is not None:
            chars = final_save.get("characters")
            if isinstance(chars, list) and chars and isinstance(chars[0], dict):
                summary = f"{chars[0].get('name', '?')} (Level {chars[0].get('level', '?')})"
        return ResumeCard(
            community_id=None, participant_id=self.participant_id,
            chrononaut_id=chrononaut_id, last_valid_save_summary=summary,
        )

    def _cmd_new_or_switch_character(self) -> None:
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
        ein ehrlicher Teilstand (kein stiller Fallback auf eine Dummyfigur)."""
        entries = catalog.list_for_participant(self.catalog_dir, self.participant_id)
        # W4 (F4, PLAN-CRITIC.md Auflage 4: "echte Auswahl-Eingabe in n
        # statt nur Anzeige/'bereits abgeschlossen'"): bei bereits
        # registrierten Figuren wird jetzt WIRKLICH gefragt, statt nur
        # read-only aufzulisten und bei `completed` sofort abzubrechen --
        # der Mensch waehlt entweder eine bestehende Figur zum Aktivieren
        # (Chrononaut-ID) oder startet ausdruecklich eine WEITERE
        # Erschaffung ('neu').
        force_new = False
        if entries:
            active_id = catalog.active_chrononaut_id(self.catalog_dir, self.participant_id)
            self._print("Vorhandene Figuren:")
            for e in entries:
                marker = " (aktiv)" if e.chrononaut_id == active_id else ""
                self._print(f"  - {e.chrononaut_id}{marker}")
            choice = self._readline(
                "Chrononaut-ID zum Aktivieren eingeben, oder 'neu' fuer eine weitere Erschaffung: "
            ).strip()
            if choice and choice.lower() not in ("neu", "n", "new"):
                self._switch_active_figure(choice, entries)
                return
            force_new = True
        state = onboarding.start_or_resume(self.onboarding_dir, self.participant_id, force_new=force_new)
        if state.status == "completed":
            self._print(f"Erschaffung bereits abgeschlossen (Save vorhanden fuer {self.participant_id}).")
            return
        if self.run_dir is None or self.gm_transport_factory is None:
            self._print(
                "Neue Erschaffung erfordert eine konfigurierte SL-Anbindung (run_dir + "
                "gm_transport_factory) fuer den echten Erschaffungsdialog — hier nicht "
                "konfiguriert, kein Dialogstart (Live-Setup, s. docs/mmo-sim.md)."
            )
            return
        from ..core import request_ledger
        from ..core.admission import read_admission_block, reservation_for_wire_text
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
        except Exception as e:
            self._print(f"Erschaffungsdialog: SL-Anbindung nicht verfuegbar ({e}) — kein Dialogstart.")
            return
        self._print("Erschaffungsdialog gestartet/fortgesetzt (echter SL-Dialog, fortsetzbar, kein JSON noetig).")
        turn_idx = len(state.steps)
        outgoing = state.steps[-1]["answer"] if state.steps else (
            "Ich moechte einen neuen Chrononauten erschaffen. Fuehre mich Schritt fuer Schritt durch die Erschaffung."
        )
        while True:
            # A3/R07-Restintegrationsfix (WEGKARTE §6 A3, Plan-Critic-
            # Auflage, REVIEW-P2R.md R-C): der Gate-Check VOR der Schleife
            # (oben) ist NICHT ausreichend -- er lief bisher nur EINMAL vor
            # dem Dialogstart. Hier wird das Admission-Gate FRISCH von der
            # Platte VOR JEDER einzelnen Erschaffungsanfrage geprueft
            # (analog `core/runtime.py:_check_gate()`s Aufrufmuster in
            # `act()`) -- ein Stop, der WAEHREND der ersten Erschaffungs-
            # antwort gesetzt wird, verhindert die zweite (Test 07:
            # `len(seen)==1`).
            # Auflage 1 (F3, PLAN-CRITIC): body-basierte GM-Reservierung
            # AUCH am Erschaffungsdialog -- dieselbe Rolle wie jeder andere
            # GM-Turn (Q06-Prinzip), nicht die starre Pauschale.
            gm_reserved = reservation_for_wire_text(outgoing)
            blocked, reason = read_admission_block(self.run_dir, reserved_usd=gm_reserved)
            if blocked:
                self._print(
                    f"Erschaffungsdialog blockiert (Admission-Gate: {reason}) — kein weiterer "
                    "Modellaufruf, Fortschritt bleibt erhalten, spaeter fortsetzbar."
                )
                return
            # I2-Nachzug (Auflage 1/6): derselbe reservierte+persistierte
            # Requestweg wie jede andere Rolle -- Erschaffung ist ein
            # Modellrequest wie jeder Spielzug (W2, Test 05).
            request_id = request_ledger.begin(
                self.run_dir, role="creation_dialog", content=outgoing, reserved_usd=gm_reserved,
            )
            t0 = time.monotonic()
            try:
                result = gm_transport.turn(turn_idx, outgoing)
            except Exception as e:
                request_ledger.finish_error(self.run_dir, request_id, error=e, seconds=time.monotonic() - t0)
                self._print(f"Erschaffungsdialog: SL-Anfrage fehlgeschlagen ({e}) — Fortschritt bleibt erhalten, spaeter fortsetzbar.")
                return
            request_ledger.finish_received(
                self.run_dir, request_id, usage=result.get("usage"), seconds=time.monotonic() - t0,
            )
            sl_text = result.get("content", "")
            self._print(f"[SL] {sl_text}")
            save_blocks = zeitriss_saves.extract_all_saves(sl_text)
            candidate_char_id = zeitriss_saves.block_char_id(save_blocks[0]) if save_blocks else None
            if save_blocks and candidate_char_id is not None:
                try:
                    onboarding.complete_with_save(
                        self.onboarding_dir, self.participant_id, save_blocks[0],
                        ZeitrissHarvestValidator(), candidate_char_id,
                    )
                except ValueError as e:
                    self._print(f"SL-Erschaffungsergebnis ungueltig ({e}) — Dialog bleibt offen, keine Uebernahme.")
                    return
                # R05-Restintegrationsfix (WEGKARTE §4, REVIEW-P2R.md R-A):
                # derselbe autoritative Fertigstellungsweg wie `_cmd_import`
                # -- ein akzeptierter Save fuehrt NICHT nur zu einem
                # Onboarding-/Katalogeintrag, sondern auch zur echten
                # Persona-State-/Current-Save-Publikation, ohne die eine
                # als 'tischbereit' gemeldete Figur keinen Folgeabschnitt
                # abschliessen kann (Test 05).
                if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
                    from ..core.persona_state import PersonaStateStore
                    from ..core import store as core_store
                    ps_store = PersonaStateStore(schema_path=self.schema_path)
                    onboarding.ensure_participant_persona_state(
                        ps_store, self.states_dir, self.participant_id, candidate_char_id, save_blocks[0],
                    )
                    core_store.publish_current_save(
                        self.run_dir, self.participant_id, save_blocks[0], ps_store, self.states_dir,
                    )
                # A21 (WEGKARTE §8, 11 §6): Katalogregistrierung, s. `_cmd_import`.
                catalog.register(self.catalog_dir, catalog.CatalogEntry(
                    participant_id=self.participant_id, chrononaut_id=candidate_char_id,
                    persona_key=self.participant_id,
                ))
                # W4 (F4, Test 07): eigene, dauerhafte Savebytes JEDER
                # registrierten Figur -- unabhaengig davon, ob diese neue
                # Erschaffung gerade aktiv wird oder (bei gesperrter
                # aktiver Figur) inaktiv registriert bleibt.
                catalog.store_figure_save(self.catalog_dir, self.participant_id, candidate_char_id, save_blocks[0])
                try:
                    catalog.bind_for_section(self.catalog_dir, self.participant_id, candidate_char_id, has_open_section=False)
                except catalog.ActiveBindingError:
                    self._print(
                        f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Aktive Figur hat einen "
                        "offenen Abschnitt -- neue Figur bleibt INAKTIV registriert (Savebytes gesichert)."
                    )
                    return
                self._print(f"Erschaffung abgeschlossen: char_id={candidate_char_id}. Figur ist jetzt tischbereit.")
                return
            answer = self._readline("Deine Antwort: ")
            onboarding.record_step(self.onboarding_dir, self.participant_id, sl_text, answer)
            turn_idx += 1
            outgoing = answer

    def _switch_active_figure(self, chosen_id: str, entries: list) -> None:
        """W4 (F4, "echte Auswahl-Eingabe in n"): aktiviert eine bereits
        registrierte, bisher inaktive Figur -- laedt ihre eigenen,
        getrennt persistierten Savebytes (`catalog.load_figure_save`, NICHT
        den Single-Slot-Store einer ANDEREN Figur) und publiziert sie als
        neuen Current-Save. Ein Wechsel wird abgelehnt, solange die
        BISHERIGE aktive Figur einen offenen Abschnitt/Abschlussauftrag hat
        (dieselbe Sperrsemantik wie `_cmd_import`s Aktivwechsel, 11 §6)."""
        known_ids = {e.chrononaut_id for e in entries}
        if chosen_id not in known_ids:
            self._print(f"Unbekannte Chrononaut-ID {chosen_id!r} — keine Aenderung (verfuegbar: {sorted(known_ids)}).")
            return
        active_id = catalog.active_chrononaut_id(self.catalog_dir, self.participant_id)
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
        self._print("JSON-Datei-Pfad ODER Mehrzeilentext einfuegen, Ende mit einer Zeile 'ENDE':")
        lines = []
        while True:
            line = self._readline("")
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
        if len(lines) == 1:
            candidate_path = Path(raw)
            if candidate_path.is_file():
                try:
                    raw = candidate_path.read_text(encoding="utf-8")
                except OSError as e:
                    self._print(f"Datei konnte nicht gelesen werden: {e}")
                    return
        try:
            preview = import_export.preview_import(raw)
        except import_export.MalformedImportError as e:
            self._print(f"Import abgelehnt (strukturell ungueltig, kein Write): {e}")
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
        baseline_block = self._resolve_active_save(self.participant_id, existing_onboarding_save)
        existing_block_for_char_id = None
        if baseline_block is not None:
            baseline_char_id = zeitriss_saves.block_char_id(baseline_block)
            if baseline_char_id is not None:
                known_char_ids.add(baseline_char_id)
                if baseline_char_id == preview.char_id:
                    existing_block_for_char_id = baseline_block

        # Fall 3 (11 §5): bekannte Char-ID, abweichender Stand -- braucht die
        # ausdrueckliche Konfliktwahl, die der bisherige Hinweistext bereits
        # ankuendigte. Ohne echten Konflikt (Fall 1/2/4) wird NICHT gefragt.
        explicit_choice = None
        if preview.char_id in known_char_ids and existing_block_for_char_id is not None and existing_block_for_char_id != incoming_block:
            self._print(
                "Bekannte Figur mit abweichendem Stand -- ausdrueckliche Konfliktwahl noetig: "
                "'a' importierten Stand uebernehmen, 'k' bisherigen Stand behalten."
            )
            answer = self._readline("Wahl [a/k]: ").strip().lower()
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
        active_elsewhere = catalog.active_chrononaut_id(self.catalog_dir, self.participant_id)
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
                "(Import bleibt als inaktive Zweitfigur registriert)."
            )
            answer = self._readline("Wahl [w/b]: ").strip().lower()
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
        choice = self._readline("Wahl [w/v/s]: ").strip().lower()
        if choice != "v":
            self._print("Kein KI-Vorlauf gestartet (Standard: direkt weiterspielen ohne Levelangleichung).")
            return
        self._cmd_bounded_ai_preflight()

    def _cmd_bounded_ai_preflight(self) -> None:
        """A23 (WEGKARTE §8, 11 §7): 'KI-Vorlauf ist KEIN Levelknopf. Es ist
        eine Konfiguration des bereits beauftragten Labormodus.' Nutzt
        DENSELBEN Lab-/Gate-Weg (`lab.runner.LabRunner`), keine zweite
        Engine, kein automatisches Hochleveln. 01 §M4 (bindend): 'im
        Bauauftrag weiterhin nur Mockausfuehrung' -- ohne separates
        Live-Go bleibt dies eine ehrliche Budget-Konfiguration mit echtem
        Singleton-/Budget-Mechanismus, kein echter Modellaufruf."""
        from ..lab.runner import LabBudget, LabRunner, SingletonViolationError
        try:
            max_turns = int(self._readline("Max. Turns fuer diesen Vorlauf: ").strip())
            max_seconds = float(self._readline("Max. Sekunden: ").strip())
            max_usd = float(self._readline("Max. USD (synthetischer Tarif): ").strip())
        except ValueError:
            self._print("Ungueltige Budgetangabe -- kein Vorlauf gestartet.")
            return
        lab = LabRunner(self.run_dir, LabBudget(max_turns, max_seconds, max_usd))
        try:
            lab.start()
        except SingletonViolationError as e:
            self._print(f"KI-Vorlauf nicht gestartet: {e}")
            return
        self._print(
            f"KI-Vorlauf konfiguriert und gestartet (Budget: turns={max_turns} seconds={max_seconds} "
            f"usd={max_usd}). Freiwillige Personaentscheidungen, unveraenderte Regeln, echte Saves, "
            "eigener Chrononaut bleibt ungespielt. Ohne separates Live-Go bleibt dies Konfiguration/"
            "Mockausfuehrung (01 §M4) -- echte SL-/Persona-Anfragen fuer diesen Vorlauf sind ein "
            "spaeterer, gesondert freigegebener Schritt."
        )
        lab.release()

    def _cmd_export(self) -> None:
        """F5/K11 (WEGKARTE §6): Export = der aktuell PUBLIZIERTE Save
        (`core.store.load_current_save`), NICHT `onboarding.final_save` --
        letzteres ist nur der Stand der ERSCHAFFUNG, veraltet sobald der
        Save ueber eine echte Runde weiterpubliziert wurde (Test 10). Ohne
        konfigurierte Laufumgebung (run_dir/states_dir/schema_path) -- oder
        wenn (noch) kein Current-Save existiert -- bleibt der Onboarding-Save
        der ehrliche Fallback (z.B. direkt nach Erschaffung, vor der ersten
        Runde)."""
        state = onboarding.start_or_resume(self.onboarding_dir, self.participant_id)
        current_save = None
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            current_save = core_store.load_current_save(
                self.run_dir, self.participant_id, ps_store, states_dir=self.states_dir,
            )
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

    def _resolve_active_save(self, persona_key: str, onboarding_final_save: dict | None) -> dict | None:
        """A7/D1 (WEGKARTE §8, Plan-Critic A7, Tests 05/06): EINHEITLICHE
        Autoritaet fuer den 'aktuellen' Save eines Teilnehmers -- IMMER
        zuerst `core.store.load_current_save` (der zuletzt echt
        veroeffentlichte Stand); NUR wenn dafuer (noch) keine Version
        existiert (z.B. direkt nach Erschaffung, vor der ersten Runde/
        Publikation) faellt dies auf den reinen Onboarding-Stand zurueck.
        `onboarding.final_save` ist NACH Fortschritt KEINE konkurrierende
        Current-Autoritaet mehr (Muster von `_cmd_export` uebernommen,
        nicht neu erfunden) -- `_cmd_import`s Konfliktbasis UND
        `_cmd_local_round`s Spielstart verwenden jetzt DIESELBE Funktion."""
        if self.run_dir is not None and self.states_dir is not None and self.schema_path is not None:
            from ..core.persona_state import PersonaStateStore
            from ..core import store as core_store
            ps_store = PersonaStateStore(schema_path=self.schema_path)
            current = core_store.load_current_save(
                self.run_dir, persona_key, ps_store, states_dir=self.states_dir,
            )
            if current is not None:
                return current
        return onboarding_final_save

    def _own_system_context(self, persona_key: str) -> str:
        """D3/A7 (K7, WEGKARTE §6, PLAN-CRITIC-ABSCHLUSS.md HINWEIS):
        gemeinsamer Context-Builder -- baut den `system`-Kontext ueber die
        bereits vorhandene `PersonaStateStore.render_for_prompt` (nicht neu
        gebaut). Ohne konfigurierte Laufumgebung ODER ohne existierenden
        State (z.B. eine Persona, die noch nicht importiert hat) bleibt der
        Kontext ein leerer String -- kein Absturz, kein erfundener Inhalt."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            return ""
        from ..core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=self.schema_path)
        try:
            state = ps_store.load_state(persona_key, states_dir=self.states_dir)
        except FileNotFoundError:
            return ""
        return ps_store.render_for_prompt(state)

    def _append_invitation_log(self, record: dict) -> None:
        """W1 (F..., "Angebot+Antworten VOR Tischanlage festhalten"):
        append-only Nachweislog fuer Angebote und Teilnehmerantworten,
        real auf Platte, unabhaengig vom Tischausgang. Ohne konfigurierte
        Laufumgebung (Offline-Default ohne `run_dir`) bleibt dies ein
        No-op -- kein Absturz, kein erfundenes Verzeichnis."""
        if self.run_dir is None:
            return
        try:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            path = self.run_dir / "invitation_decisions.jsonl"
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass  # Nachweislog ist Audit, kein Blocker fuer den eigentlichen Ablauf.

    def _cmd_local_round(self, guest_tokens: list[str] | None = None) -> None:
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
        fuer 'Mensch als bewusst zustimmender Gast eines KI-Leaders')."""
        if self.run_dir is None or self.states_dir is None or self.schema_path is None or self.gm_transport_factory is None:
            self._print(
                "Lokale Runde erfordert eine konfigurierte Laufumgebung (run_dir/states_dir/"
                "schema_path) und eine SL-Anbindung (gm_transport_factory) — hier nicht "
                "konfiguriert, kein Spielstart (Live-Setup, s. docs/mmo-sim.md)."
            )
            return

        from ..core import app_service
        from ..core import store as core_store
        from ..core import request_ledger
        from ..core.admission import read_admission_block, reservation_for_request
        from ..core.controller import TableController
        from ..core.persona_state import PersonaStateStore
        from ..adapters.base import (
            ParticipantDecision,
            decision_contract_instruction,
            human_menu_decision,
            interpret_decision_contract,
        )

        def _admitted_invite_decision(driver, ctx: dict, role: str):
            """I2-Nachzug (Auflage 1/6): derselbe reservierte+persistierte
            Requestweg wie jede andere Rolle (`core.runtime.SectionRuntime.
            _admitted_decision`) -- Einladungen/Lobby sind Modellrequests wie
            jeder Spielzug. Liefert `(decision, None)` bei Erfolg,
            `(None, reason)` wenn das Admission-Gate blockiert; wirft die
            Ausnahme des Treibers unveraendert weiter (wie bisher)."""
            reserved_usd, output_bound_known = reservation_for_request(driver, ctx)
            route = getattr(getattr(driver, "config", None), "base_url", None)
            blocked, reason = read_admission_block(
                self.run_dir, reserved_usd=reserved_usd,
                output_bound_known=output_bound_known, route=route,
            )
            if blocked:
                return None, reason
            request_id = request_ledger.begin(
                self.run_dir, role=role,
                content=json.dumps(ctx, ensure_ascii=False, sort_keys=True, default=str),
                reserved_usd=reserved_usd, route=route,
                output_limit_tokens=getattr(getattr(driver, "config", None), "max_tokens", None),
            )
            t0 = time.monotonic()
            try:
                decision = driver.decide(ctx)
            except Exception as e:
                request_ledger.finish_error(self.run_dir, request_id, error=e, seconds=time.monotonic() - t0)
                raise
            request_ledger.finish_received(
                self.run_dir, request_id, usage=(decision.meta or {}).get("usage"),
                seconds=time.monotonic() - t0,
            )
            return decision, None

        tokens = list(guest_tokens or [])
        leader_persona_id: str | None = None
        if tokens and tokens[0].startswith("lead:persona:"):
            leader_persona_id = tokens[0].split(":", 2)[2]
            tokens = tokens[1:]
        leader_id = leader_persona_id if leader_persona_id else self.participant_id

        def _resolve_member(pid: str) -> tuple[dict, str] | None:
            """Liefert `(active_save, chrononaut_id)` fuer einen beliebigen
            Teilnehmer (Leader ODER Gast) — dieselbe Autoritaet (A7/D1) fuer
            alle Rollen."""
            member_state = onboarding.peek(self.onboarding_dir, pid)
            if member_state is None or member_state.final_save is None:
                return None
            member_active_save = self._resolve_active_save(pid, member_state.final_save)
            member_chrono_id = zeitriss_saves.block_char_id(member_active_save)
            if member_chrono_id is None:
                return None
            return member_active_save, member_chrono_id

        resolved_leader = _resolve_member(leader_id)
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
            leader_driver = self.persona_driver_factory(leader_persona_id)
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
                lead_decision, block_reason = _admitted_invite_decision(leader_driver, lead_invite_ctx, "lead_invite")
            except Exception as e:
                self._print(f"KI-Leader-Anfrage an '{leader_persona_id}' fehlgeschlagen: {e}")
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
            resolved_guest = _resolve_member(guest_id)
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
                confirm_answer = self._readline(
                    f"[{guest_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten? [j/n]: "
                )
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
                driver = self.persona_driver_factory(guest_id)
                invite_ctx = {
                    "system": self._own_system_context(guest_id),
                    "user": (
                        f"Du wirst von '{leader_id}' eingeladen, einer lokalen Runde beizutreten.\n"
                        + decision_contract_instruction(invitation_offer_id, guest_id)
                    ),
                    "decision_contract": {"offer_id": invitation_offer_id, "participant_id": guest_id},
                }
                try:
                    invite_decision, block_reason = _admitted_invite_decision(driver, invite_ctx, "guest_invite")
                except Exception as e:  # Transportfehler -- kein Auto-Accept.
                    self._print(f"Einladung an '{guest_id}' nicht zustande gekommen (Fehler): {e}")
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
            self._print(f"Lokale Runde konnte nicht gestartet werden: {derivation.reason}")
            return

        outer = self

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

            def __init__(self, save: dict | None, label: str | None = None):
                self._save = save
                self._turn = 0
                self._label = label

            def decide(self, context: dict):
                table_view = context.get("table_view") or {}
                sl_log = table_view.get("sl_log") or []
                if sl_log:
                    last = sl_log[-1]
                    outer._print(f"[SL] {last.get('content', '')}")
                for m in context.get("pending_table_messages") or []:
                    outer._print(f"[Tischabsprache] {m.get('from', '?')}: {m.get('text', '')}")
                prompt = f"[{self._label}] Deine Aktion: " if self._label else "Deine Aktion: "
                text = outer._readline(prompt)
                self._turn += 1
                payload = self._save if self._turn == 1 else None
                return ParticipantDecision(text=text, origin_source="human:terminal", save_payload=payload)

        # A24 (WEGKARTE §8): der Leader-Driver ist entweder der aufrufende
        # Mensch (`_HumanDriver`, unveraendertes Standardverhalten) ODER die
        # bereits zugesagte KI-Persona (`leader_driver`, echte modellbasierte
        # Konsolidierung ueber denselben `ParticipantDriver`-Vertrag wie
        # jeder Gast -- die Runtime unterscheidet Leader/Gast nicht am Typ).
        drivers = {leader_id: leader_driver if leader_persona_id else _HumanDriver(active_save)}
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
                drivers[guest_id] = _HumanDriver(guest_save)
            else:
                drivers[guest_id] = _HumanDriver(guest_save, label=guest_id)
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
        except Exception as e:  # SL-Anbindung nicht herstellbar -- kein stiller Fallback (03 §4).
            self._print(f"Lokale Runde: SL-Anbindung nicht verfuegbar ({e}) — kein Spielstart.")
            return

        today = datetime.date.today().isoformat()
        ts = datetime.datetime.now().isoformat()
        outcome = app_service.run_play_session(
            # D5/A6 (WEGKARTE §6 BLOCKER): `table.table_id` (nicht das
            # urspruenglich angefragte `table_id`) -- `create_table_from_
            # offer_log` kann bei geschlossenem Vorgaenger-Tisch eine
            # generationsweise hochgezaehlte Kennung zurueckgeben.
            lobby, table, gm_transport, controller, f"{table.table_id}-section",
            contexts,
            self.states_dir, today, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief,
        )
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
        if self.run_dir is None or self.states_dir is None or self.schema_path is None:
            self._print(
                "Neue Spielgemeinschaft: erfordert eine konfigurierte Laufumgebung "
                "(run_dir/states_dir/schema_path) — hier nicht konfiguriert, kein "
                "Community-Bootstrap (Live-Setup, s. docs/mmo-sim.md)."
            )
            return

        from ..core.persona_state import PersonaStateStore
        from ..domain.zeitriss.community_bootstrap import bootstrap_community

        ps_store = PersonaStateStore(schema_path=self.schema_path)
        today = datetime.date.today().isoformat()
        community_id = f"community-{self.participant_id}"
        demo_payload = self._synthetic_starter_pool(community_id, size=8)
        community_dir = self.run_dir / "community"
        result = bootstrap_community(
            community_dir, community_id, 1, demo_payload,
            ps_store, self.states_dir, today,
        )
        self._print(
            "Neue Spielgemeinschaft (SYNTHETISCHER Demo-Bootstrap, KEIN echter Modellaufruf): "
            f"{result.reason} (personas: {result.personas_written})"
        )

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
        while not self._quit:
            resume = self._build_resume_card()
            self._print(render_boot_menu(resume))
            try:
                raw_choice = self._readline("Auswahl: ").strip()
            except EndOfInput:
                self._print("\nEingabe beendet (EOF) — sicher pausiert, kein weiterer Modellaufruf.")
                return 0
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
                elif choice == "l":
                    self._cmd_local_round(extra_tokens)
                elif choice == "c":
                    self._cmd_community()
                elif choice == "s":
                    self._cmd_settings()
                elif choice in ("x", "q"):
                    self._quit = True
                elif choice == "":
                    continue
                else:
                    self._print(f"Unbekannte Auswahl: {choice!r}")
            except EndOfInput:
                self._print("\nEingabe beendet (EOF) waehrend eines Untermenues — sicher pausiert.")
                return 0
        return self.exit_code
