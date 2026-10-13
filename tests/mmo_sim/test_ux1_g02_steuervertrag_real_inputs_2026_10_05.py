#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_g02_steuervertrag_real_inputs_2026_10_05.py — G02
(ZEITRISS Terminal UX-1, Wiederanlauf W5/B): EIN Steuervertrag an echten
Eingabestellen, keine zweite Parserwelt.

Deckt als dauerhafte positive Regressionen (General-Befund G02, Probes
P01/P02/P10-P12):
  - P01/P10 (UX04/07): `registrieren` -> Namensprompt -> `/abbrechen` darf
    NICHT als Anzeigename gespeichert werden (kontextbewusster Leser).
  - P02/P11 (UX04/05): `spielen` -> `1` -> `?` zeigt lokale Kontexthilfe
    und erhaelt die laufende Einrichtung, statt mit "unbekannte Auswahl"
    abzubrechen.
  - P12 (UX16/06): Erstimport schreibt NUR nach ausdruecklichem Ja;
    Abbruch/EOF verwirft den Entwurf, kein Write.
  - UX05: literales `x`/`q`, escaped Steuerzeile (`\\/abbrechen`), EOF
    kontrolliert (kein Haengen, kein Teilwrite).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs
(keine echten Spieler-/Providerdaten, kein Netz-/Live-Call)."""
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
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

# R12-Fix: kanonischer, gegen BEIDE v7-Schemas gueltiger Block statt des
# schmalen `sniper.json`-Minimalinhalts (sniper.json selbst bleibt
# unveraendert) -- dieselbe Identitaet (char_id/name/callsign), aber
# tatsaechlich durch den echten Import-Textpfad annehmbar.
_FIXTURE_SAVE = full_v7_save("CHR-SNIPER-001", name="Yael", callsign="SNIPER")


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


# ---------------------------------------------------------------------------
# P01/P10: /abbrechen am Namensprompt ist Abbruch, keine Nutzdaten.
# ---------------------------------------------------------------------------

def test_abbrechen_at_name_prompt_is_not_stored_as_display_name():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["/abbrechen"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert any("Registrierung abgebrochen -- keine Aenderung" in p for p in printed), printed
        humans = session._local_round_list_humans()
        assert not any(name == "/abbrechen" for _pid, name in humans), humans
        assert humans == [], humans


def test_zurueck_at_name_prompt_also_aborts_without_write():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["/zurueck"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert session._local_round_list_humans() == []


def test_question_mark_at_name_prompt_shows_help_then_accepts_real_name():
    """'?' an diesem Prompt verbraucht keine Registrierung -- dieselbe
    Zeile wird danach erneut abgefragt (zentraler Helper, kein Umgehen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["?", "Echte Person", "n"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert any(p.startswith("Hilfe (Neue Person registrieren)") for p in printed), printed
        humans = session._local_round_list_humans()
        assert any(name == "Echte Person" for _pid, name in humans), humans


def test_escaped_literal_slash_abbrechen_is_stored_as_real_name():
    """UX05: ein literaler Text, der wie eine Steuerzeile aussieht, bleibt
    ueber das erklaerte fuehrende '\\' eingebbar und wird NICHT als Abbruch
    interpretiert."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["\\/abbrechen", "n"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        humans = session._local_round_list_humans()
        assert any(name == "/abbrechen" for _pid, name in humans), humans


def test_bare_x_and_q_are_stored_as_literal_names_not_swallowed_as_abort():
    """UX05 (02 §C): bare `x`/`q` sind NUR an den dafuer dokumentierten
    Top-Level-Menue-Hotkeys 'Beenden', NICHT in `_CONTROL_TOKENS` -- an
    einem Freitextprompt wie dem Namensprompt bleiben sie gewoehnlicher
    Nutztext, kein pauschal verschluckter Abbruch."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for literal in ("x", "q"):
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=d / "onboarding" / literal, catalog_dir=d / "catalog" / literal,
                participant_id="original-human",
                input_fn=_scripted_input([literal, "n"]),
                print_fn=printed.append,
            )
            session._cmd_register_new_person()
            humans = session._local_round_list_humans()
            assert any(name == literal for _pid, name in humans), (literal, humans)


# ---------------------------------------------------------------------------
# P02/P11: `spielen` -> `1` -> `?` zeigt lokale Hilfe, Einrichtung bleibt.
# ---------------------------------------------------------------------------

def test_help_at_round_setup_mode_prompt_keeps_setup_alive():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            # '?' am Modusprompt -> Hilfe, dann regulaer Modus 1, dann keine
            # Figur vorhanden -> kontrollierter Abbruch (kein KI-Ersatz).
            input_fn=_scripted_input(["?", "1"]),
            print_fn=printed.append,
        )
        session._cmd_local_round_setup()
        assert any(p.startswith("Hilfe (Runde einrichten)") for p in printed), printed
        assert not any("unbekannte Auswahl" in p for p in printed), printed
        # Ohne abgeschlossene Figur endet der Weg kontrolliert (kein
        # GM-/Persona-Call, kein KI-Ersatz) -- das beweist, dass die
        # Auswahl '1' TATSAECHLICH verarbeitet wurde statt verworfen.
        assert any("noch keine abgeschlossene Figur" in p for p in printed), printed


def test_unknown_mode_choice_still_aborts_cleanly():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            input_fn=_scripted_input(["9"]),
            print_fn=printed.append,
        )
        session._cmd_local_round_setup()
        assert any("unbekannte Auswahl" in p for p in printed), printed


def test_abbrechen_at_round_setup_mode_prompt_aborts_without_ai_substitute():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            input_fn=_scripted_input(["/abbrechen"]),
            print_fn=printed.append,
        )
        session._cmd_local_round_setup()
        assert any("Einrichtung abgebrochen -- kein Spielstart, keine Aenderung." in p for p in printed), printed


# ---------------------------------------------------------------------------
# G02 (02 §C "Wesentliche Unterdialoge duerfen den zentralen Helper nicht
# umgehen"): weitere Unterdialoge der Rundeneinrichtung, die bisher
# denselben rohen `_readline`-Bug wie die Modusauswahl hatten.
# ---------------------------------------------------------------------------

def test_help_at_select_ai_prompt_keeps_setup_alive():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
        )
        session._print = printed.append
        session._input = _scripted_input(["?", "persona-a persona-b"])
        tokens = session._local_round_select_ai()
        assert any(p.startswith("Hilfe (KI-Mitspieler waehlen)") for p in printed), printed
        assert tokens == ["persona-a", "persona-b"], tokens


def test_abbrechen_at_select_leader_prompt_aborts_cleanly():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            input_fn=_scripted_input(["/abbrechen"]), print_fn=lambda *_a: None,
        )
        result = session._local_round_select_leader(["persona-a"])
        assert result is None


def test_help_at_handoff_prompt_keeps_handoff_alive_then_accepts():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            input_fn=_scripted_input(["?", "j"]), print_fn=printed.append,
        )
        accepted = session._local_round_handoff("other-pid")
        assert any(p.startswith("Hilfe (Terminaluebergabe)") for p in printed), printed
        assert accepted is True


# ---------------------------------------------------------------------------
# P12: Erstimport schreibt nur nach ausdruecklichem Ja.
# ---------------------------------------------------------------------------

def test_fresh_first_import_without_explicit_yes_does_not_write():
    """UX16/06: frischer Datenroot, Vorschau wird gezeigt, aber auf die
    Bestaetigung folgt 'n' -- kein Katalogeintrag, kein Write."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        raw = json.dumps(_FIXTURE_SAVE)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="erstimport-human",
            input_fn=_scripted_input([raw, "ENDE", "n"]),
            print_fn=printed.append,
        )
        session._cmd_import()
        assert any(p.startswith("Vorschau:") for p in printed), printed
        assert any("kein Write, Entwurf verworfen" in p for p in printed), printed
        assert catalog.list_for_participant(d / "catalog", "erstimport-human") == []


def test_fresh_first_import_eof_at_confirmation_does_not_write():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        raw = json.dumps(_FIXTURE_SAVE)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="erstimport-human",
            input_fn=_scripted_input([raw, "ENDE"]),  # EOF genau an der Bestaetigungszeile
            print_fn=printed.append,
        )
        session._cmd_import()
        assert any("kein Write, Entwurf verworfen" in p for p in printed), printed
        assert catalog.list_for_participant(d / "catalog", "erstimport-human") == []


def test_fresh_first_import_with_explicit_yes_writes_exactly_once():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        raw = json.dumps(_FIXTURE_SAVE)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="erstimport-human",
            input_fn=_scripted_input([raw, "ENDE", "j"]),
            print_fn=printed.append,
        )
        session._cmd_import()
        entries = catalog.list_for_participant(d / "catalog", "erstimport-human")
        assert len(entries) == 1, entries


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
