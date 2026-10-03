#!/usr/bin/env python3
"""
tests/mmo_sim/e2e_offline_player_dialog.py — EIN durchgaengiger geskripteter
Offline-E2E-Dialog durch den ECHTEN CLI-/TUI-Einstieg (WEGKARTE §3,
Testvertrag, Pflichtbeleg fuer den P2-Produktdurchstich).

Deckt ab: Profil/Teilnehmer -> Save uebernehmen (real ueber `ui.tui.TuiSession
._cmd_import`: Vorschau UND die tatsaechliche Uebernahme ueber
`domain.zeitriss.import_export.resolve_import`/`onboarding.complete_with_save`,
beides jetzt EIN Aufruf desselben TUI-Kommandos) -> Figur waehlen
(`domain.zeitriss.catalog`) -> Gruppe bilden UND eine Persona (echter
`PersonaApiDriver` gegen einen echten Loopback-`FakeHTTPServer`) einladen,
REAL ueber `ui.tui.TuiSession._cmd_local_round(["persona:tech"])` (F2) ->
mehrere Szenen MIT Reaktion auf neue SL-Info (der GM-Stub variiert seine
Antwort nach empfangenem Wire-Text) -> gueltiger Abschluss + KI-Pflicht-
Reflexion (F6) -> Export ueber die ECHTE `TuiSession._cmd_export` (Current-
Save, F5) -> "neuer Prozess" (frische `TuiSession`-Instanz, derselbe
run_dir/onboarding_dir) -> korrekte Wiederaufnahme (F5/A8).

`core.app_service.run_play_session` ist GENAU der Call-Pfad, den auch
`ui.tui.TuiSession._cmd_local_round` UND `lab.runner.LabRunner.run_section`
verwenden (A4, spy-belegt in `test_a04_shared_app_service.py`) -- dieses
Skript ruft ihn NICHT mehr direkt auf, sondern ausschliesslich ueber
`TuiSession._cmd_local_round`, das die Persona-Einladung jetzt selbst
aufloest (BLOCKER 2 gefixt: Lobby-Join je Mitglied + Offer/Consent-Log +
mehrere `chrononaut_ids` sitzen im TUI-Kommando, nicht mehr daneben).

Stubs NUR an Prozess-/HTTP-Grenzen: `FakeHTTPServer` ist ein ECHTER
Loopback-HTTP-Server (127.0.0.1), der GM-Transport ist ein einfacher
In-Prozess-Fake (kein Netz, aber derselbe `GMTransport`-Vertrag wie
`adapters/gm_owui.py`). Echter Exitcode, kein Skip/Xfail."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.fakes import FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures"
SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
LOG: list[str] = []


def log(msg: str) -> None:
    print(msg)
    LOG.append(msg)


class _ReactingGm:
    """GM-Stub mit echter Reaktion auf empfangene SL-Info: variiert die
    Antwort danach, ob die vorherige Antwort bereits im Wire-Text auftaucht
    (beweist, dass die Runtime die zuletzt empfangene SL-Antwort tatsaechlich
    in den naechsten Kontext zurueckspeist, s. F1). `table_id`/`section_id`
    MUESSEN den echten Werten entsprechen, die `TuiSession._cmd_local_round`
    tatsaechlich verwendet (`completion_marker_matches` prueft exakt)."""

    def __init__(self, final_saves: dict[str, dict], table_id: str, section_id: str):
        self.calls: list[dict] = []
        self._final_saves = final_saves
        self._table_id = table_id
        self._section_id = section_id
        self._scene = 0

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        self._scene += 1
        if "TISCHNACHRICHTEN" in user_text and self._scene <= 3:
            content = f"Szene {self._scene}: die Gruppe reagiert auf die Gastabsprache."
        elif self._scene == 1:
            content = "Szene 1: Ihr steht am Einstiegspunkt. Was tut ihr?"
        elif self._scene < 4:
            content = f"Szene {self._scene}: neue Information -- ein Alarm ertoent in der Ferne."
        else:
            debrief = "Abschnitt beendet, ihr kehrt zur Lobby zurueck.\n"
            for blk in self._final_saves.values():
                debrief += f"```json\n{json.dumps(blk)}\n```\n"
            debrief += f"{COMPLETION_MARKER} table_id={self._table_id} section_id={self._section_id}"
            content = debrief
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "e2e-chat"}


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        onboarding_dir = base / "onboarding"
        catalog_dir = base / "catalog"
        run_dir = base / "run"
        states_dir = base / "states"
        exports_dir = base / "exports"
        # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): explizites, sichtbares
        # Testprofil-Setup -- ohne Autorisierung blockiert das Admission-Gate
        # jetzt JEDE Entscheidung (auch die des menschlichen Leaders).
        write_test_profile(run_dir)

        sniper_save = json.loads((FIX / "saves" / "sniper.json").read_text())
        tech_save = json.loads((FIX / "saves" / "tech.json").read_text())
        sniper_state = json.loads((FIX / "persona_states" / "sniper.json").read_text())
        tech_state = json.loads((FIX / "persona_states" / "tech.json").read_text())
        for st in (sniper_state, tech_state):
            st["rounds_played"] = 0
            st["round_history"] = {}
            st.pop("current_save_version", None)

        ps_store = PersonaStateStore(schema_path=SCHEMA)
        ps_store.save_state("sniper", sniper_state, states_dir=states_dir)
        ps_store.save_state("tech", tech_state, states_dir=states_dir)

        # ── Schritt 1: Profil/Teilnehmer + Save uebernehmen (real via TUI-Import) ──
        log("=== Schritt 1: Teilnehmer 'sniper' importiert einen externen v7-Save ===")
        import_lines = json.dumps(sniper_save).splitlines() or [json.dumps(sniper_save)]
        shown: list[str] = []
        # Kein Konfliktfall (frischer Teilnehmer, keine bekannte Char-ID) --
        # `_cmd_import` fragt daher NICHT nach einer Konfliktwahl (s. sein
        # Docstring), das Skript braucht kein zusaetzliches Wahl-Token.
        script_iter = iter(import_lines + ["ENDE"])

        def input_fn(prompt: str = "") -> str:
            try:
                return next(script_iter)
            except StopIteration:
                raise EOFError()

        boot_session = TuiSession(onboarding_dir, catalog_dir, "sniper", input_fn=input_fn, print_fn=shown.append)
        # Menuewahl 'i' fehlt im obigen Skript bewusst -- wir rufen den echten
        # Import-Befehl direkt auf (identisch zu choice=='i' im echten Loop).
        # BLOCKER 1 gefixt: `_cmd_import` liest die Vorschau UND uebernimmt
        # den Save jetzt tatsaechlich (kein Domaenencode-Umweg mehr noetig).
        boot_session._cmd_import()
        assert any("Vorschau: char_id=" in s for s in shown), "TUI-Importvorschau lief nicht real durch"
        log(f"  TUI-Importvorschau: {[s for s in shown if 'Vorschau' in s][0]}")
        assert any("Uebernahme abgeschlossen" in s for s in shown), "TUI-Import hat den Save nicht real uebernommen"
        adoption_line = [s for s in shown if "Uebernahme abgeschlossen" in s][0]
        log(f"  TUI-Uebernahme: {adoption_line}")
        sniper_char_id = zeitriss_saves.block_char_id(sniper_save)
        adopted_state = onboarding.peek(onboarding_dir, "sniper")
        assert adopted_state is not None and adopted_state.final_save == sniper_save, (
            "TUI-Import hat den importierten Save nicht in den Erschaffungsauftrag geschrieben"
        )

        # ── Schritt 2: Figur waehlen (Katalog) ──
        log("=== Schritt 2: Figur im Katalog binden ===")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="sniper", chrononaut_id=sniper_char_id, persona_key="sniper",
            display_name="Yael 'Sniper'",
        ))
        catalog.bind_for_section(catalog_dir, "sniper", sniper_char_id, has_open_section=False)
        assert catalog.last_selected(catalog_dir, "sniper") == sniper_char_id
        log(f"  Katalog: aktive Figur={catalog.last_selected(catalog_dir, 'sniper')}")

        # ── Schritt 3+4: Gruppe bilden (Leader laedt Persona-Gast ein) UND
        #    mehrere Szenen -- BEIDES real ueber `TuiSession._cmd_local_round`
        #    (BLOCKER 2 gefixt: kein manueller Lobby-/Tisch-/run_play_session-
        #    Aufbau mehr NEBEN dem TUI-Kommando). `tech` braucht dieselbe
        #    abgeschlossene Erschaffung wie ein Mensch, damit die Einladung
        #    ueber `onboarding.peek` real aufgeloest werden kann.
        log("=== Schritt 3+4: Gruppe einladen + mehrere Szenen (real ueber TuiSession._cmd_local_round) ===")
        tech_char_id = zeitriss_saves.block_char_id(tech_save)
        onboarding.start_or_resume(onboarding_dir, "tech")
        onboarding.complete_with_save(onboarding_dir, "tech", tech_save, ZeitrissHarvestValidator(), tech_char_id)

        with FakeHTTPServer([
            # D2/A1 (WEGKARTE §6 BLOCKER, PLAN-CRITIC-ABSCHLUSS.md): echte
            # Einladungs-Zusage VOR Tischaufnahme braucht jetzt einen
            # eigenen realen Request an die Persona -- ein Aufruf mehr als
            # vor der Fertigstellung.
            # I1-Fix (MAIN-ENTSCHEIDUNG I1-Kontrollform): eine Einladungs-
            # zusage muss jetzt der vollstaendig validierbaren Kontrollform
            # entsprechen (offer_id/participant_id gebunden an das
            # tatsaechliche Angebot -- deterministisch aus Leader+Gaesten
            # abgeleitet, `_cmd_local_round`s `invitation_offer_id`) statt
            # freiem Ja-Protokollwort-Fliesstext (semantisch notwendige
            # Protokollanpassung, dieselbe Zusage im neuen Vertrag).
            (200, {"choices": [{"message": {
                "content": "ENTSCHEIDUNG offer_id=invite-sniper-tech participant_id=tech "
                           "decision=accept explanation=Ich bin bereit.",
            }}]}),
            (200, {"choices": [{"message": {"content": "Ich sichere die Flanke und melde Bereitschaft."}}]}),
            (200, {"choices": [{"message": {"content": "Ich beobachte den Alarm weiter, keine Vorwarnung noetig."}}]}),
            (200, {"choices": [{"message": {"content": "Bin zufrieden mit dem Verlauf des Abschnitts."}}]}),
        ]) as srv:
            gm = _ReactingGm(
                {"sniper": sniper_save, "tech": tech_save},
                table_id="local-sniper-tech", section_id="local-sniper-tech-section",
            )
            # `_cmd_local_round` nutzt die ECHTE `TuiSession._HumanDriver`
            # (kein Skript-Fallback-Text mehr wie die alte manuelle
            # Umgehung) -- nach den zwei geskripteten Aktionen liefert
            # `next(..., default)` weiterhin eine gueltige Antwort, bis der
            # GM-Stub bei Szene 4 den Abschluss-Marker sendet.
            action_script = iter(["Wir betreten den Sektor vorsichtig.", "Wir folgen dem Alarm mit Deckung."])

            def local_round_input(prompt: str = "") -> str:
                return next(action_script, "Ich warte ab.")

            play_shown: list[str] = []
            play_session = TuiSession(
                onboarding_dir, catalog_dir, "sniper", input_fn=local_round_input, print_fn=play_shown.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=SCHEMA,
                gm_transport_factory=lambda: gm,
                persona_driver_factory=lambda pk: PersonaApiDriver(
                    PersonaApiConfig(srv.base_url, "SYNTHETIC_KEY", "synthetic-model"), pk,
                ),
            )
            # Echtes TUI-Kommando 'l persona:tech': Lobby-Join, Offer/Consent-
            # Log und mehrere `chrononaut_ids` werden JETZT von
            # `_cmd_local_round` selbst aufgeloest (statt daneben im Test).
            play_session._cmd_local_round(["persona:tech"])
            if play_specs := [s for s in play_shown if s.startswith("Gruppe eingeladen:")]:
                log(f"  {play_specs[0]}")
            # F2/A3: der Persona-Gast wird ueber den echten HTTP-Loopback
            # MEHRFACH real befragt -- beim Import-Turn, bei der Konsultation
            # waehrend der laufenden Spielturns (Absprachekanal) UND bei der
            # KI-Pflichtreflexion (F6) -- kein einmaliger Fixture-Lookup.
            assert len(srv.calls) >= 2, f"Persona-Gast haette mehrfach real ueber HTTP befragt werden muessen, war: {len(srv.calls)}"
            log(f"  Persona-Gast HTTP-Aufrufe (echter Loopback-Server, Import+Konsultation+Reflexion): {len(srv.calls)}")

        table = store.Table.load(run_dir, "local-sniper-tech")
        assert table.leader == "sniper" and set(table.members) == {"sniper", "tech"}
        log(f"  Tisch gebildet (real ueber TuiSession._cmd_local_round): leader={table.leader} members={table.members}")

        # ── Schritt 5: Abschluss + Erinnerung ──
        log("=== Schritt 5: Abschluss + Reflexion ===")
        completion_lines = [s for s in play_shown if s.startswith("Abschnitt abgeschlossen:")]
        assert completion_lines, f"Abschnitt wurde nicht real abgeschlossen (letzte Ausgaben: {play_shown[-5:]})"
        assert "sniper" in completion_lines[0] and "tech" in completion_lines[0], completion_lines[0]
        reflections_path = run_dir / "reflections.jsonl"
        reflection_lines = [json.loads(l) for l in reflections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        tech_reflection = [r for r in reflection_lines if r.get("persona_key") == "tech"]
        assert tech_reflection, "KI-Gast haette eine Pflichtreflexion abgeben muessen"
        tech_state_after = ps_store.load_state("tech", states_dir=states_dir)
        assert "last_reflection" in tech_state_after, "KI-Reflexion floss nicht in den Persona-State zurueck (F6)"
        log(f"  Abschluss (real ueber TUI): {completion_lines[0]}")
        log(f"  Reflexion (tech, KI-Pflicht) im State: {tech_state_after.get('last_reflection')!r}")

        # ── Schritt 6: Export ueber die ECHTE TuiSession._cmd_export (Current-Save) ──
        log("=== Schritt 6: Export (Current-Save, real ueber TuiSession) ===")
        onboarding.complete_with_save(onboarding_dir, "sniper", sniper_save, ZeitrissHarvestValidator(), sniper_char_id)
        export_shown: list[str] = []
        export_session = TuiSession(
            onboarding_dir, catalog_dir, "sniper", print_fn=export_shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=SCHEMA, exports_dir=exports_dir,
        )
        export_session._cmd_export()
        export_path = exports_dir / "sniper.json"
        assert export_path.is_file(), "Export-Datei fehlt"
        exported = json.loads(export_path.read_text(encoding="utf-8"))
        current = store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert exported == current, "Export weicht vom Current-Save ab (F5)"
        log(f"  Export geschrieben: {export_path.name}, entspricht Current-Save: {exported == current}")

        # ── Schritt 7: "neuer Prozess" -- frische TuiSession, korrekte Wiederaufnahme ──
        log("=== Schritt 7: neuer Prozess (frische TuiSession-Instanz) ===")
        gm2 = _ReactingGm(
            {"sniper": sniper_save, "tech": tech_save},
            table_id="local-sniper", section_id="local-sniper-section",
        )
        calls_before = len(gm2.calls)
        resumed_shown: list[str] = []
        resume_script = iter(["l", "Ich pruefe die Lage erneut.", "x"])

        def resume_input(prompt: str = "") -> str:
            try:
                return next(resume_script)
            except StopIteration:
                raise EOFError()

        resumed_session = TuiSession(
            onboarding_dir, catalog_dir, "sniper", input_fn=resume_input, print_fn=resumed_shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=SCHEMA,
            gm_transport_factory=lambda: gm2,
        )
        # 'l' OHNE weitere Teilnehmer-Tokens verwendet den Solo-Tischnamen
        # `local-sniper` -- ein ANDERER Tisch als der Gruppen-Tisch
        # `local-sniper-tech` aus Schritt 3+4 (BLOCKER 2: eingeladene Gaeste
        # bekommen einen eigenen Tisch-Namensraum, s. `_cmd_local_round`-
        # Docstring). Das ist die korrekte Anschluss-Semantik: eine SOLO-
        # Fortsetzung nach einer abgeschlossenen Gruppenrunde eroeffnet einen
        # NEUEN privaten Tisch, statt den (fuer eine Solo-Fortsetzung nicht
        # mehr vollstaendig besetzbaren) Gruppen-Tisch weiterzufuehren. Das
        # ist NICHT die Resume-innerhalb-derselben-Sektion-Semantik aus Test
        # 09/11 (die einen NICHT abgeschlossenen Solo-Tisch betrifft).
        resumed_session.run()
        assert len(gm2.calls) > calls_before, "neuer Prozess haette einen neuen Abschnittsturn ausloesen muessen"
        log(f"  Neuer Prozess: GM-Turns nach Wiederaufnahme/Neuanschluss: {len(gm2.calls)}")
        log(f"  Katalog nach Neustart weiterhin aktiv: {catalog.last_selected(catalog_dir, 'sniper')}")

        log("=== E2E-Dialog vollstaendig durchlaufen: PASS ===")
        return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    # E2E-Hygiene (WEGKARTE §0/§4, Review-Auflage): das Log NICHT mehr in
    # den getrackten Quellbaum schreiben -- ein Testlauf darf den Diff
    # gegen den Vertragsabschluss-Stand nicht mehr veraendern. Default
    # ausserhalb des Repos (System-Temp); `MMO_SIM_E2E_LOG_DIR` erlaubt
    # einen expliziten externen Ausgabeort (z.B. fuer den Worker-Report).
    import os
    log_dir = Path(os.environ.get("MMO_SIM_E2E_LOG_DIR", tempfile.gettempdir()))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "e2e_offline_player_dialog.log").write_text(
        "\n".join(LOG) + f"\n\nEXIT={rc}\n", encoding="utf-8",
    )
    sys.exit(rc)
