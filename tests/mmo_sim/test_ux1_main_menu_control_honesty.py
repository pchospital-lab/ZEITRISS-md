#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_main_menu_control_honesty.py — R4 (Korrekturzyklus
1, T-Befund 1, UX04/05), ZEITRISS Terminal UX-1.

Der Intro-Text bewarb `/stand`/`/verlauf`/`/pause` als "an jeder Eingabe"
nutzbar -- im Hauptmenue ergaben sie aber vorher durchgaengig
"Unbekannte Auswahl: '/stand'" usw. (Bedienprobe `tester/out/BEDIENPROBE.md`
Aufgabe 6/zusammenfassender Befund 1). Dieser Test beweist: das Hauptmenue
antwortet jetzt auf alle drei Befehle mit einem klaren, EHRLICHEN Hinweis
statt "Unbekannte Auswahl" -- `/stand` funktioniert dabei ECHT (zeigt den
tatsaechlichen Stand, falls vorhanden), `/verlauf`/`/pause` erklaeren
ehrlich, dass sie sich auf einen laufenden Spielabschnitt beziehen, den es
am Hauptmenue noch nicht gibt.

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

from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def test_stand_verlauf_pause_no_longer_unbekannte_auswahl_at_main_menu():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["/stand", "/verlauf", "/pause"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        rc = session.run()
        assert rc == 0
        assert not any("Unbekannte Auswahl: '/stand'" in p for p in printed), printed
        assert not any("Unbekannte Auswahl: '/verlauf'" in p for p in printed), printed
        assert not any("Unbekannte Auswahl: '/pause'" in p for p in printed), printed
        # /stand ohne vorhandenen Stand: ehrliche Meldung, kein Traceback.
        assert any("Kein aktueller Stand vorhanden" in p for p in printed), printed
        # /verlauf und /pause erklaeren ehrlich den Geltungsbereich.
        assert any("laufenden Spielabschnitt" in p for p in printed), printed


def test_stand_at_main_menu_shows_real_resume_line_when_present():
    """`/stand` im Hauptmenue ist kein Stub -- zeigt echte Fortsetzen-Zeile,
    wenn eine Community existiert (derselbe Produktionsweg wie `_cmd_
    community`)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["c", "/stand", "beenden"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        rc = session.run()
        assert rc == 0
        assert any(p.strip().startswith("Fortsetzen: community-p1") for p in printed), printed


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
