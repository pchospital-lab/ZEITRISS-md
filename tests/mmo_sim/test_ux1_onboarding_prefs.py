#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_onboarding_prefs.py — UX02 (ZEITRISS Terminal UX-1,
02 §B "Erstfuehrung und Hinweise").

Beweist: Erstfuehrung erscheint bei leerem Datenroot, bleibt beim naechsten
Start (gleicher Datenroot) aus ("kein erneuter Fragebogen"), ist jederzeit
ueber 'einfuehrung' wiederholbar, und ein defekter Praeferenzwert zeigt die
Fuehrung hoechstens erneut -- verliert aber NIE eine Figur (02 §B
verbindlich). Die Praeferenzdatei liegt NACHWEISLICH getrennt vom
Onboarding-/v7-Save-Scratch.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui import onboarding_prefs  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


def test_intro_shown_on_first_run_with_empty_data_root():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("Kurze Einfuehrung" in p for p in printed), printed
        # R9 (Korrekturzyklus 1): Praeferenzdatei liegt jetzt PRO
        # `participant_id` ("ui_prefs__p1.json"), nicht mehr als EINE
        # gemeinsame "ui_prefs.json" pro Datenroot (s. `onboarding_prefs.
        # py:_path`) -- die alte gemeinsame Pfadform bleibt nur fuer
        # Aufrufer OHNE `participant_id`-Argument erhalten (Rueckwaerts-
        # kompatibel, s. `test_pref_file_is_separate_from_onboarding_and_
        # has_no_v7_fields` unten, das weiterhin ohne Argument aufruft).
        assert (d / "ui_prefs__p1.json").is_file()
        assert not (d / "ui_prefs.json").exists()


def test_intro_not_shown_again_after_restart_same_data_root():
    """UX02: 'Neustart ohne erneuten Fragebogen'."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed1: list[str] = []
        TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=printed1.append,
        ).run()
        assert any("Kurze Einfuehrung" in p for p in printed1), printed1

        printed2: list[str] = []
        TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=printed2.append,
        ).run()
        assert not any("Kurze Einfuehrung" in p for p in printed2), printed2


def test_intro_is_repeatable_via_einfuehrung_word():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        onboarding_prefs.mark_tutorial_seen(d)
        printed: list[str] = []
        it = iter(["einfuehrung"])

        def _fn(prompt: str = "") -> str:
            try:
                return next(it)
            except StopIteration:
                raise EOFError()

        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_fn, print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any(p == "Einfuehrung:" for p in printed), printed


def test_corrupt_pref_file_reshows_intro_but_never_touches_catalog_or_onboarding():
    """02 §B verbindlich: ein defekter Praeferenzwert darf keine Figur
    verlieren -- hier simuliert durch bereits VORHANDENE Figur-/Onboarding-
    Daten, die nach einem kaputten `ui_prefs.json` unveraendert bleiben
    muessen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "ui_prefs.json").write_text("{not valid json", encoding="utf-8")
        catalog_marker = d / "catalog" / "sentinel.txt"
        catalog_marker.parent.mkdir(parents=True, exist_ok=True)
        catalog_marker.write_text("untouched", encoding="utf-8")

        prefs = onboarding_prefs.load(d)
        assert prefs.tutorial_seen is False

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("Kurze Einfuehrung" in p for p in printed), printed
        assert catalog_marker.read_text(encoding="utf-8") == "untouched"
        assert not (d / "onboarding").exists() or list((d / "onboarding").iterdir()) == []


def test_pref_file_is_separate_from_onboarding_and_has_no_v7_fields():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        onboarding_prefs.mark_tutorial_seen(d)
        import json
        data = json.loads((d / "ui_prefs.json").read_text(encoding="utf-8"))
        assert set(data.keys()) == {"tutorial_seen"}
        assert "characters" not in data and "v" not in data
        assert (d / "ui_prefs.json").parent == d
        assert not (d / "onboarding").exists()


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
