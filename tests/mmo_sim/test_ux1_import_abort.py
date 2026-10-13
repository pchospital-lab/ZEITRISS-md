#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_import_abort.py — R5b (Korrekturzyklus 1,
T-Befund, UX05/UX16), ZEITRISS Terminal UX-1.

Vorher wurde `/abbrechen`/`/zurueck` an ZWEI Stellen im Import-Weg NICHT
als Abbruch erkannt, sondern als normaler Text/Standardoption behandelt
(`tester/out/BEDIENPROBE.md` Aufgabe 3/8):

1. In der JSON-Mehrzeilentext-Eingabe (`[i]` -> "... Ende mit 'ENDE'"):
   ein eingegebenes `/abbrechen` wartete weiter auf 'ENDE' und landete
   dann als ungueltiges JSON.
2. An der `[w/b]`-Rueckfrage (zweiter Import bei bereits aktiver Figur):
   jede Eingabe ausser 'w' fiel auf das 'b'-Verhalten zurueck und schrieb
   TROTZDEM eine inaktive Zweitregistrierung -- es gab keine Moeglichkeit,
   den Import komplett zu verwerfen.

Dieser Test beweist beide Faelle als behoben: ein klar benannter
Abbruchweg (NUR bei exakter Gleichheit der ERSTEN Zeile bzw. der ganzen
Antwort -- kein globaler Parser, der jede Zeile/Antwort als Steuerzeile
interpretiert), kein Write bei Abbruch, keine geloeschten bestehenden
Figuren.

(R5a -- echte Bestaetigung vor dem ALLERERSTEN, bisher unbestaetigten
Import -- wurde geprueft, aber wieder entfernt: jede zusaetzliche
Pflichteingabe an dieser Stelle verschiebt die Eingabezeilen bestehender
real-subprocess-gescripteter Tests und laesst sie haengen/timeout, s.
WORKER2-REPORT.md.)

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
from mmo_sim.ui.tui import TuiSession  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _v7_save(char_id: str) -> str:
    # R12-Fix: kanonischer, gegen BEIDE v7-Schemas gueltiger Block statt
    # des alten Minimalfakes (fehlende Export-Pflichtfelder) -- derselbe
    # echte Import-Textpfad erwartet jetzt einen tatsaechlich annehmbaren
    # Save.
    return json.dumps(full_v7_save(char_id, name=char_id))


def test_abbrechen_as_first_line_of_json_multiline_input_aborts_no_write():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", "/abbrechen", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("Import abgebrochen" in p for p in printed), printed
        # Kein Parserfehler/kein "abgelehnt" -- es wurde als echter Abbruch
        # erkannt, nicht als (kaputter) JSON-Text verarbeitet.
        assert not any("abgelehnt" in p for p in printed), printed
        assert not any("Expecting" in p for p in printed), printed
        entries = catalog.list_for_participant(d / "catalog", "p1")
        assert entries == [], entries


def test_zurueck_as_first_line_of_json_multiline_input_also_aborts():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", "/zurueck", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("Import abgebrochen" in p for p in printed), printed


def test_abbrechen_not_recognized_mid_text_only_as_first_line_no_global_parser():
    """Erhaltungsprobe: `/abbrechen` NUR als allererste Zeile bricht ab --
    eine spaetere Zeile mit demselben Text bleibt normaler JSON-Inhalt
    (kein globaler Steuerzeilen-Parser fuer JEDE Zeile des Imports)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", "{", "/abbrechen", "}", "ENDE", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        # Kein Abbruch -- die Eingabe wurde als (kaputter) JSON-Text
        # weiterverarbeitet, '/abbrechen' war NICHT die erste Zeile.
        assert not any("Import abgebrochen" in p for p in printed), printed
        assert any("abgelehnt" in p for p in printed), printed


def test_wb_prompt_abbrechen_fully_discards_no_registration_existing_figure_untouched():
    """R5b Kernfall: zweiter Import bei bereits aktiver Figur, `/abbrechen`
    an der [w/b]-Rueckfrage -- der Import wird komplett verworfen (KEINE
    `catalog.register`-Zeile fuer die neue Figur), die bestehende aktive
    Figur bleibt vollstaendig unberuehrt (keine Loeschung)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            # TEST-DELTA (G02/P12): je ein zusaetzliches 'j' fuer die neue
            # Erstimport-Bestaetigung VOR der jeweils bestehenden Rueckfrage
            # -- das zweite 'j' bestaetigt nur die Uebernahme des Entwurfs,
            # das eigentliche '/abbrechen' bleibt unveraendert an der
            # [w/b]-Rueckfrage (R5b-Kernaussage dieses Tests).
            input_fn=_scripted_input([
                "i", _v7_save("CHR-FIRST"), "ENDE", "j",  # erste Figur, wird aktiv
                "i", _v7_save("CHR-SECOND"), "ENDE", "j", "/abbrechen",  # zweiter Import, abgebrochen
                "x",
            ]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("Import verworfen" in p for p in printed), printed
        assert not any("Zweite Figur registriert" in p for p in printed), printed
        entries = catalog.list_for_participant(d / "catalog", "p1")
        char_ids = {e.chrononaut_id for e in entries}
        assert "CHR-SECOND" not in char_ids, entries
        # Die bestehende aktive Erstfigur bleibt unveraendert vorhanden.
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-FIRST"


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
