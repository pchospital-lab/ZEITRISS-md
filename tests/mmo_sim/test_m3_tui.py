#!/usr/bin/env python3
"""
tests/mmo_sim/test_m3_tui.py — A16 (Terminal, Ctrl-C/EOF, geskriptete
Eingabe) + A17-Weg ueber die TUI-Schicht.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession, render_boot_menu, ResumeCard  # noqa: E402


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def test_boot_menu_renders_resume_card_when_present():
    card = ResumeCard(community_id="comm-1", participant_id="p1", chrononaut_id="chrono-1",
                       last_valid_save_summary="Level 3, Abschnitt 2 abgeschlossen")
    text = render_boot_menu(card)
    assert "Fortsetzen: comm-1 · p1 · chrono-1" in text
    assert "Level 3" in text


def test_boot_menu_without_resume_card_shows_fresh_options():
    text = render_boot_menu(None)
    assert "Fortsetzen" not in text
    assert "[c] Neue Spielgemeinschaft" in text


def test_tui_eof_during_menu_pauses_cleanly_no_crash():
    """A11/A16: EOF/Pipeline-Ende darf keinen Absturz und keinen weiteren
    Modellaufruf ausloesen, sondern eine kontrollierte Pause."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([]),  # sofortiges EOF
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("EOF" in p for p in printed)


def test_tui_onboarding_without_sl_anbindung_stays_honest_partial_state():
    """A17 (WEGKARTE §8): OHNE konfigurierte SL-Anbindung (run_dir/
    gm_transport_factory) bleibt [n] ein ehrlicher Teilstand -- kein Dummy-
    Save, kein stiller Fallback auf die alte Fixfrage."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["n", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("konfigurierte SL-Anbindung" in p for p in printed)

        from mmo_sim.domain.zeitriss.onboarding import start_or_resume
        state = start_or_resume(d / "onboarding", "p1")
        assert state.status == "in_progress"
        assert state.steps == []


def test_tui_scripted_onboarding_real_sl_dialog_completes_with_valid_save():
    """A17 (WEGKARTE §8, 11 §3, REVIEW-P2V.md A17 OFFEN): echter,
    fortsetzbarer SL-Erschaffungsdialog statt einer einzelnen fest
    gespeicherten Frage/Antwort -- ersetzt den frueheren Test auf die alte
    Fixfrage-ohne-SL-Dialog-Semantik (semantisch notwendige Anpassung, 04
    §3: A17 verlangt genau diesen echten Dialog als Zielzustand). Frage
    anzeigen, Antwort SOFORT persistieren (Crash-Sicherheit), bis die
    SL-Antwort einen gueltigen v7-Save-Block enthaelt."""
    import json
    save_path = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves" / "sniper.json"
    save_block = json.loads(save_path.read_text(encoding="utf-8"))

    class _FakeCreationGm:
        def __init__(self):
            self.calls: list[tuple[int, str]] = []

        def turn(self, idx, text):
            self.calls.append((idx, text))
            if len(self.calls) == 1:
                return {"content": "Wie beginnt deine Zeitreise?"}
            return {"content": "```json\n" + json.dumps(save_block) + "\n```"}

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        gm = _FakeCreationGm()
        # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): explizites Testprofil
        # -- der Erschaffungsdialog ist ein Modellrequest hinter demselben
        # Admission-Gate wie jede andere Entscheidung.
        write_test_profile(d / "run")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["n", "Ich erwache in einem Rift.", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=None,
            gm_transport_factory=lambda: gm,
        )
        rc = session.run()
        assert rc == 0
        assert any("[SL] Wie beginnt deine Zeitreise?" in p for p in printed)
        assert any("Erschaffung abgeschlossen" in p for p in printed)
        assert len(gm.calls) == 2
        assert gm.calls[0][1].startswith("Ich moechte einen neuen Chrononauten")
        assert gm.calls[1][1] == "Ich erwache in einem Rift."

        from mmo_sim.domain.zeitriss.onboarding import peek
        state = peek(d / "onboarding", "p1")
        assert state.status == "completed"
        assert state.steps[0]["question"] == "Wie beginnt deine Zeitreise?"
        assert state.steps[0]["answer"] == "Ich erwache in einem Rift."
        assert state.final_save == save_block


def test_tui_onboarding_dialog_interrupted_by_eof_stays_resumable():
    """A17: Abbruch VOR dem ersten gueltigen Save (hier: EOF direkt bei der
    ersten SL-Frage) laesst die Erschaffung offen/fortsetzbar -- kein
    Dummy-Save, kein gezaehlter Fortschritt."""

    class _FakeCreationGm:
        def turn(self, idx, text):
            return {"content": "Wie beginnt deine Zeitreise?"}

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["n"]),  # EOF genau bei der Antwort-Aufforderung
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=None,
            gm_transport_factory=lambda: _FakeCreationGm(),
        )
        rc = session.run()
        assert rc == 0
        assert any("EOF" in p for p in printed)

        from mmo_sim.domain.zeitriss.onboarding import peek
        state = peek(d / "onboarding", "p1")
        assert state.status == "in_progress"
        assert state.steps == []
        assert state.final_save is None


def test_tui_import_rejects_malformed_without_crash():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", "kein json", "ENDE", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("abgelehnt" in p for p in printed)


def test_tui_local_round_ai_leader_requires_real_consent_then_consolidates():
    """A24 (WEGKARTE §8, 02 §4 'KI-Leader: eigene modellbasierte
    Konsolidierung', 11 §8): `l lead:persona:<id>` macht eine eingeladene
    Persona zum Leader -- ECHTE, protokollierte Zusage VOR Tischaufnahme
    (derselbe Entscheidungsvertrag wie ein Gast), danach sendet SIE
    (nicht der aufrufende Mensch) an die SL. Der aufrufende Mensch wird
    selbst zum Gast (eigene Freigabe durch den Kommandoaufruf)."""
    import json

    from mmo_sim.adapters.base import ParticipantDecision
    from mmo_sim.domain.zeitriss import onboarding as ob
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    fix = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
    sniper_save = json.loads((fix / "sniper.json").read_text(encoding="utf-8"))
    tech_save = json.loads((fix / "tech.json").read_text(encoding="utf-8"))

    class _FakeLeaderDriver:
        def __init__(self):
            self.calls: list[dict] = []

        def decide(self, ctx):
            self.calls.append(ctx)
            if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
                return ParticipantDecision("Guter Einsatz heute.", origin_source="fake:persona")
            if len(self.calls) == 1:
                # I1 (MAIN-ENTSCHEIDUNG I1-Kontrollform): die Leaderzusage
                # muss jetzt der vollstaendig validierbaren Kontrollform
                # entsprechen (offer_id/participant_id gebunden an das
                # tatsaechliche Angebot, s. `decision_contract` im Kontext)
                # statt freiem "Ja, ..."-Fliesstext -- die alte Form wuerde
                # unter I1 strukturell 'invalid' liefern (semantisch
                # notwendige Protokollanpassung, kein Verhaltensverlust:
                # dieselbe Zusage, jetzt im vereinbarten Vertrag).
                dc = ctx.get("decision_contract") or {}
                return ParticipantDecision(
                    f"ENTSCHEIDUNG offer_id={dc.get('offer_id')} participant_id={dc.get('participant_id')} "
                    "decision=accept explanation=Ich uebernehme die Leaderrolle.",
                    origin_source="fake:persona",
                )
            return ParticipantDecision("Wir gehen vorsichtig vor.", origin_source="fake:persona")

    class _FakeGm:
        def __init__(self):
            self.calls: list[str] = []

        def turn(self, idx, text):
            self.calls.append(text)
            if len(self.calls) >= 2:
                content = (
                    "```json\n" + json.dumps(sniper_save) + "\n```\n"
                    "```json\n" + json.dumps(tech_save) + "\n```\n"
                    f"{COMPLETION_MARKER} table_id=local-tech-sniper section_id=local-tech-sniper-section"
                )
            else:
                content = "Szene laeuft, was tut ihr?"
            return {"content": content, "usage": {}}

    leader_driver = _FakeLeaderDriver()
    gm = _FakeGm()

    from mmo_sim.core.persona_state import PersonaStateStore
    schema_path = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        ps_store = PersonaStateStore(schema_path=schema_path)
        for pid, save in (("sniper", sniper_save), ("tech", tech_save)):
            char_id = _block_char_id(save)
            ob.start_or_resume(d / "onboarding", pid)
            ob.complete_with_save(d / "onboarding", pid, save, _ZeitrissHarvestValidator(), char_id)
            ob.ensure_participant_persona_state(ps_store, d / "states", pid, char_id, save)
        printed = []
        # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): explizites Testprofil.
        write_test_profile(d / "run")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input(["l lead:persona:tech", "Wir ruecken vor.", "Reflexionsnotiz.", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states",
            schema_path=_REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json",
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: leader_driver,
        )
        rc = session.run()
        assert rc == 0
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed
        # Erste Anfrage an die Persona war die Leader-Einladung, nicht ein
        # normaler Spielzug (echte Zusage VOR Tischaufnahme).
        assert "Leader" in leader_driver.calls[0]["user"]
        assert len(gm.calls) == 2
        assert any(r.get("kind") == "ai_required_reflection" and r.get("persona_key") == "tech"
                   for r in _read_reflections(d / "run"))

        from mmo_sim.core import store as core_store
        table = core_store.Table.load(d / "run", "local-tech-sniper")
        assert table.leader == "tech"
        assert set(table.members) == {"sniper", "tech"}
        assert table.status == "closed"


def test_tui_local_round_ai_leader_actually_consolidates_guest_table_proposal():
    """A24-Nachtrag (End-Critic-REST 2026-09-23, WICHTIG-2): der vorige Test
    (`..._then_consolidates`) deckte trotz seines Namens ausschliesslich
    Consent+Tischentstehung+Abschluss ab -- der eigentliche
    Konsolidierungspfad (`runtime.py:poll_guests_and_consolidate` /
    `pending_table_messages`) wurde in der GESAMTEN Suite an keiner Stelle
    ausgeuebt (kein einziger Treffer fuer `pending_table_messages` oder
    `poll_guests_and_consolidate` unter `tests/`). Dieser Test erzwingt
    ueber einen Fake-GM, der erst nach vier echten Turns abschliesst, dass
    (a) der Tisch tatsaechlich eine zweite Runde (`ongoing_round`) erreicht,
    (b) der menschliche Gast dabei ueber `poll_guests_and_consolidate` einen
    Tischvorschlag einreicht (`store.post_table_message`), (c) der
    KI-Leader-Driver diesen Vorschlag im naechsten Turn tatsaechlich in
    `ctx['pending_table_messages']` SIEHT, und (d) der an die SL gesendete
    Wire-Text den Vorschlag inhaltlich uebernimmt -- echte Konsolidierung,
    nicht nur ein unbenutzt durchgereichter Kontext."""
    import json

    from mmo_sim.adapters.base import ParticipantDecision
    from mmo_sim.domain.zeitriss import onboarding as ob
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    fix = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
    sniper_save = json.loads((fix / "sniper.json").read_text(encoding="utf-8"))
    tech_save = json.loads((fix / "tech.json").read_text(encoding="utf-8"))

    GUEST_PROPOSAL = "Vorschlag: wir schleichen an der Falle vorbei statt sie zu sprengen."

    class _FakeLeaderDriver:
        def __init__(self):
            self.calls: list[dict] = []
            self.seen_pending: list[list[dict]] = []

        def decide(self, ctx):
            self.calls.append(ctx)
            if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
                return ParticipantDecision("Guter Einsatz heute.", origin_source="fake:persona")
            pending = ctx.get("pending_table_messages") or []
            self.seen_pending.append(pending)
            if len(self.calls) == 1:
                # I1 (MAIN-ENTSCHEIDUNG I1-Kontrollform): s. Analogtest
                # oben -- Leaderzusage jetzt in der vollstaendig
                # validierbaren Kontrollform statt freiem Fliesstext.
                dc = ctx.get("decision_contract") or {}
                return ParticipantDecision(
                    f"ENTSCHEIDUNG offer_id={dc.get('offer_id')} participant_id={dc.get('participant_id')} "
                    "decision=accept explanation=Ich uebernehme die Leaderrolle.",
                    origin_source="fake:persona",
                )
            if pending:
                # Echte Konsolidierung: der Gastvorschlag fliesst WOERTLICH
                # in den an die SL gesendeten Text ein (kein blosses
                # Ignorieren eines nur durchgereichten Kontexts).
                text = "Wir folgen dem Tischvorschlag: " + pending[-1]["text"]
                return ParticipantDecision(text, origin_source="fake:persona")
            return ParticipantDecision("Wir beobachten die Lage weiter.", origin_source="fake:persona")

    class _FakeGm:
        def __init__(self):
            self.calls: list[str] = []

        def turn(self, idx, text):
            self.calls.append(text)
            if len(self.calls) >= 4:
                content = (
                    "```json\n" + json.dumps(sniper_save) + "\n```\n"
                    "```json\n" + json.dumps(tech_save) + "\n```\n"
                    f"{COMPLETION_MARKER} table_id=local-tech-sniper section_id=local-tech-sniper-section"
                )
            else:
                content = "Szene laeuft, was tut ihr?"
            return {"content": content, "usage": {}}

    leader_driver = _FakeLeaderDriver()
    gm = _FakeGm()

    from mmo_sim.core.persona_state import PersonaStateStore
    schema_path = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        ps_store = PersonaStateStore(schema_path=schema_path)
        for pid, save in (("sniper", sniper_save), ("tech", tech_save)):
            char_id = _block_char_id(save)
            ob.start_or_resume(d / "onboarding", pid)
            ob.complete_with_save(d / "onboarding", pid, save, _ZeitrissHarvestValidator(), char_id)
            ob.ensure_participant_persona_state(ps_store, d / "states", pid, char_id, save)
        printed = []
        # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): explizites Testprofil.
        write_test_profile(d / "run")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="sniper",
            input_fn=_scripted_input([
                "l lead:persona:tech",  # Auswahl + Gastbeitritt unter KI-Leader.
                "Ich bin bereit.",  # sniper: Import-/Beitrittsturn.
                GUEST_PROPOSAL,  # sniper: Tischabsprache ueber poll_guests_and_consolidate.
                "Reflexionsnotiz.",  # sniper: freiwillige menschliche Reflexion.
                "x",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states",
            schema_path=_REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json",
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: leader_driver,
        )
        rc = session.run()
        assert rc == 0
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed

        # (a)+(c) Der Vorschlag war im Kontext des naechsten Leader-Turns
        # tatsaechlich sichtbar (pending_table_messages), nicht nur
        # theoretisch verdrahtet.
        assert any(
            any(m.get("text") == GUEST_PROPOSAL for m in pending)
            for pending in leader_driver.seen_pending
        ), leader_driver.seen_pending

        # (d) Der an die SL gesendete Wire-Text hat den Vorschlag
        # tatsaechlich uebernommen (echte Konsolidierung, nicht nur
        # Sichtbarkeit ohne Wirkung).
        assert any(GUEST_PROPOSAL in call_text for call_text in gm.calls), gm.calls

        # (b) Der Konsolidierungspfad wurde tatsaechlich durchlaufen (Anker
        # + Gast-Import + 2 Ongoing-Runden), nicht durch Sofortabschluss
        # umgangen.
        assert len(gm.calls) == 4

        from mmo_sim.core import store as core_store
        table = core_store.Table.load(d / "run", "local-tech-sniper")
        assert table.leader == "tech"
        assert set(table.members) == {"sniper", "tech"}
        assert table.status == "closed"
        # Die konsolidierte Tischnachricht bleibt im persistenten Verlauf
        # erhalten (store.post_table_message), nicht nur im Testzustand.
        assert any(m.get("text") == GUEST_PROPOSAL for m in table.table_messages)


def _block_char_id(block: dict) -> str:
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves
    return zeitriss_saves.block_char_id(block)


def _ZeitrissHarvestValidator():
    from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
    return ZeitrissHarvestValidator()


def _read_reflections(run_dir: Path) -> list[dict]:
    import json
    path = run_dir / "reflections.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_tui_import_of_higher_level_save_offers_bounded_ai_preflight():
    """A23 (WEGKARTE §8, 11 §7 'Direktspielen ist Standard, optionaler
    begrenzter KI-Vorlauf ist explizite Lab-Konfiguration'): ein Import mit
    Level >= 2 bietet die Wahl an; 'w' (Standard) startet KEINEN Vorlauf;
    'v' konfiguriert einen echten, budgetierten `LabRunner` (01 §M4: 'im
    Bauauftrag weiterhin nur Mockausfuehrung' -- kein echter Modellaufruf,
    aber ein echter Singleton-/Budget-Mechanismus)."""
    import json

    higher_save = {
        "v": 7, "save_id": "fixture-veteran-001", "_fixture_note": "SIMULIERT/FIXTURE",
        "characters": [{"char_id": "CHR-VETERAN-001", "id": "CHR-VETERAN-001", "name": "Rho", "callsign": "VETERAN", "level": 5}],
    }
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", json.dumps(higher_save), "ENDE", "w", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states",
            schema_path=_REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json",
        )
        rc = session.run()
        assert rc == 0
        assert any("erfahrener" in p for p in printed), printed
        assert any("Kein KI-Vorlauf gestartet" in p for p in printed)
        assert not (d / "run" / "lab.status.json").exists()

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", json.dumps(higher_save), "ENDE", "v", "10", "60", "1.0", "x"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states",
            schema_path=_REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json",
        )
        rc = session.run()
        assert rc == 0
        assert any("KI-Vorlauf konfiguriert und gestartet" in p for p in printed), printed
        assert (d / "run" / "lab.status.json").exists()
        status = json.loads((d / "run" / "lab.status.json").read_text(encoding="utf-8"))
        assert status["max_turns"] == 10 and status["running"] is False  # release() nach Konfiguration


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
