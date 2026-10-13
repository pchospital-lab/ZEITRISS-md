#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_control_contract.py — UX04/UX05 (ZEITRISS Terminal
UX-1, 02 §C "Kommandos und Nutztext duerfen sich nicht verwechseln").

Beweist den neuen zentralen Steuerzeilen-Vertrag (`TuiSession.
_readline_with_controls`): `/hilfe`/`?` zeigen Hilfe OHNE Zug-/Callverbrauch
und OHNE die laufende Eingabe zu verlieren; `/pause` waehrend eines echten
Spielzugs (`_HumanDriver.decide`) pausiert kontrolliert (dieselbe bestehende
`EndOfInput`-Mechanik, kein neuer Absturzpfad); ein literales `x`/`q`/
Fragezeichen-im-Satz wird NICHT verschluckt; Escape (`\\/pause`) liefert den
literalen Text.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


# R12-Fix: `sniper.json` selbst bleibt unveraendert (Produkt-/QA-Fixture
# ausserhalb dieses Scopes); der Fake-GM liefert hier statt des schmalen
# Dateiinhalts (nur _fixture_note/characters/save_id/v, 12 von 15 Export-
# Pflichtfeldern fehlend) einen kanonischen `full_v7_save(...)` mit
# derselben Identitaet (char_id/name/callsign) wie `sniper.json`, damit
# die Erschaffung tatsaechlich angenommen wird und der Pause-Pfad erreicht
# werden kann.
_FIXTURE_SAVE = full_v7_save("CHR-SNIPER-001", name="Yael", callsign="SNIPER")


class _FakeCreationGm:
    """Gleiche Form wie `test_m3_tui.py`s Erschaffungs-Fake: `turn(idx,
    text)` -> `{"content": ...}`, erste Antwort die SL-Frage, zweite der
    v7-Save-Block."""

    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        if len(self.calls) == 1:
            return {"content": "Wie beginnt deine Zeitreise?"}
        return {"content": "```json\n" + json.dumps(_FIXTURE_SAVE) + "\n```"}


class _PlayGm:
    """Fake fuer den eigentlichen Spielzug (`_cmd_local_round`) -- `calls`
    beweist, dass '/pause' KEINEN Modellaufruf ausloest (UX04)."""

    def __init__(self):
        self.calls = 0
        self.output_limit_tokens = 2000

    def turn(self, turn_idx, user_text, output_limit_tokens=None):
        self.calls += 1
        return {"content": "Szene laeuft weiter.", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def test_readline_with_controls_help_does_not_consume_turn_or_lose_selection():
    """UX04: '?'/'/hilfe' zeigen Hilfe, fragen DIESELBE Zeile erneut ab --
    bisherige Auswahl bleibt vollstaendig erhalten, kein zusaetzlicher
    Aufruf an irgendeinen Call-Zaehler."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["?", "/hilfe", "mein echter text"]),
            print_fn=printed.append,
        )
        text, control = session._readline_with_controls("Frage: ", context="Testkontext")
        assert control is None
        assert text == "mein echter text"
        assert any("Hilfe (Testkontext)" in p for p in printed), printed
        assert sum(1 for p in printed if "Hilfe (Testkontext)" in p) == 2, printed


def test_bare_question_mark_only_triggers_help_not_substring_in_sentence():
    """02 §C: 'Fragezeichen im Satz' bleibt Nutztext -- nur ein EXAKTES
    bare '?' loest Hilfe aus."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["Was soll ich tun?"]),
            print_fn=printed.append,
        )
        text, control = session._readline_with_controls("Frage: ", context="Testkontext")
        assert control is None
        assert text == "Was soll ich tun?"
        assert not any("Hilfe (" in p for p in printed), printed


def test_escaped_literal_control_line_is_sent_as_text():
    """02 §C: ein literaler Text, der wie eine Steuerzeile aussieht, bleibt
    ueber ein fuehrendes '\\' eingebbar."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["\\/pause"]), print_fn=lambda *_a: None,
        )
        text, control = session._readline_with_controls("Frage: ", context="Testkontext")
        assert control is None
        assert text == "/pause", text


def test_zurueck_and_abbrechen_are_returned_to_caller_not_swallowed():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["/zurueck", "/abbrechen"]), print_fn=lambda *_a: None,
        )
        _text1, control1 = session._readline_with_controls("Frage: ", context="K")
        assert control1 == "zurueck"
        _text2, control2 = session._readline_with_controls("Frage: ", context="K")
        assert control2 == "abbrechen"


def test_literal_x_and_q_are_not_swallowed_as_abort():
    """02 §C: bare 'x'/'q' duerfen NICHT pauschal als Spielabbruch
    verschluckt werden -- `_readline_with_controls` behandelt sie als
    gewoehnlichen Nutztext (nur die explizit reservierten '/...'-Zeilen und
    das exakte '?' sind Steuerzeilen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["x", "q"]), print_fn=lambda *_a: None,
        )
        text1, control1 = session._readline_with_controls("Frage: ", context="K")
        assert control1 is None and text1 == "x"
        text2, control2 = session._readline_with_controls("Frage: ", context="K")
        assert control2 is None and text2 == "q"


def test_pause_during_real_play_turn_ends_session_controlled_no_crash():
    """UX13/UX04: '/pause' waehrend eines ECHTEN Spielzugs (Leader-Rolle,
    `_HumanDriver.decide`) pausiert kontrolliert -- `session.run()` liefert
    weiterhin rc=0, kein Traceback, und der Spiel-GM wird dafuer 0 Mal
    aufgerufen (kein Modellaufruf durch die Pause selbst)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        write_test_profile(run_dir)
        printed: list[str] = []
        creation_gm = _FakeCreationGm()
        play_gm = _PlayGm()
        gms = [creation_gm, play_gm]

        def factory():
            return gms.pop(0) if gms else play_gm

        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "n",  # neue Figur erschaffen
                "Ich erwache in einem Rift.",
                "l",  # lokale Runde solo starten
                "/pause",  # UX-1: kontrollierte Pause statt Spielzug
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=factory,
        )
        rc = session.run()
        assert rc == 0
        assert any("Empfaenger: Spielleitung (SL)" in p for p in printed), printed
        assert any("Kontrolliert pausiert" in p for p in printed), printed
        assert not any("Abschnitt abgeschlossen" in p for p in printed), printed
        assert play_gm.calls == 0, "Pause darf keinen Modellaufruf im Spielzug ausloesen"


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
