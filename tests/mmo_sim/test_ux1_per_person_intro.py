#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_per_person_intro.py — R9 (Korrekturzyklus 1, C-K2,
UX02), ZEITRISS Terminal UX-1.

Vorher lag `ui_prefs.json` (Erstfuehrung-"gesehen"-Merker) IMMER
gemeinsam pro `data_root`, nicht pro `participant_id`
(`mmo_sim/ui/onboarding_prefs.py`). Weil `onboarding_dir` typischerweise
EIN gemeinsames Verzeichnis fuer ALLE Teilnehmer eines `--data-dir` ist,
sah die Erstfuehrung nur die GLOBAL erste Person, die das Terminal je
gestartet hat -- jede ueber 'registrieren' neu hinzukommende Person auf
demselben Geraet bekam sie NIE automatisch angezeigt (C-K2).

Dieser Test beweist: Intro-Status wird jetzt PRO Person gefuehrt -- eine
neu registrierte zweite Person sieht die Erstfuehrung automatisch direkt
nach ihrer eigenen Fokusuebernahme, auch wenn die urspruenglich
aufrufende Person sie laengst "gesehen" hat.

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


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def test_second_registered_person_sees_her_own_intro_even_though_first_already_saw_it():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # Prozess 1: urspruengliche Person startet, sieht die Erstfuehrung
        # (globaler erster Start dieses Datenroots), registriert danach
        # eine zweite, neue Person -- lehnt deren Fokusuebernahme ab (haelt
        # den Test einfach, die Registrierung selbst bleibt bestehen).
        printed_1: list[str] = []
        session1 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["registrieren", "Zweite Person", "n", "beenden"]),
            print_fn=printed_1.append,
        )
        rc1 = session1.run()
        assert rc1 == 0
        assert any("Kurze Einfuehrung" in p for p in printed_1), printed_1

        humans = session1._local_round_list_humans()
        second_pid = next(pid for pid, name in humans if name == "Zweite Person")

        # Prozess 2 (simulierter Neustart, derselbe data_root): DIESELBE
        # urspruengliche Person startet erneut -- sieht die Fuehrung NICHT
        # mehr (bereits gesehen, Erhaltungsprobe fuer UX02).
        printed_2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["beenden"]),
            print_fn=printed_2.append,
        )
        session2.run()
        assert not any("Kurze Einfuehrung" in p for p in printed_2), printed_2

        # Prozess 3 (simulierter Neustart als die ZWEITE, neue Person,
        # z.B. ueber `--participant`): sieht ihre EIGENE Erstfuehrung --
        # R9 Kernassertion, vorher NIE automatisch gezeigt.
        printed_3: list[str] = []
        session3 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id=second_pid,
            input_fn=_scripted_input(["beenden"]),
            print_fn=printed_3.append,
        )
        session3.run()
        assert any("Kurze Einfuehrung" in p for p in printed_3), printed_3


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
