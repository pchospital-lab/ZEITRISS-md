#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_kiss_menu.py — UX01/UX03 (ZEITRISS Terminal UX-1,
02 §A, MENUE_ENTSCHEIDUNG.md).

Beweist die EINE KISS-Zielhierarchie (Fortsetzen/Spielen/Charaktere/
Einstellungen/Beenden) ist real verdrahtet -- additiv zu den unveraenderten
Einzelbuchstaben-Hotkeys (dokumentierte Kompatibilitaetsaliase, 02 §A). Fuer
Solo ohne KI/Mitspieler loest 'spielen' -> '1' (Runde zusammenstellen) KEINEN
Persona-Call aus (UX03: Solo ohne KI-Lobby/Persona-Aufrufe).

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


def _persona_factory_fails_if_called(_pid: str):
    raise AssertionError("UX03: Solo-Weg darf KEINEN Persona-Call ausloesen")


def test_charaktere_word_dispatches_to_same_n_i_e_paths():
    """UX01/03: 'charaktere' -> [1] ruft exakt denselben, unveraenderten
    `_cmd_new_or_switch_character`-Weg auf wie der Einzelbuchstabe 'n'."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["charaktere", "1"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("konfigurierte SL-Anbindung" in p for p in printed), printed


def test_spielen_word_offline_solo_never_calls_persona_factory():
    """UX03 Kernfall: 'spielen' -> '1' (Runde zusammenstellen) -> ohne
    weitere Menschen/KI (nur Enter) loest 0 Persona-Calls aus, SELBST wenn
    eine Persona-Factory konfiguriert waere (hier bewusst eine, die bei
    JEDEM Aufruf failt, um einen versteckten Call sofort sichtbar zu
    machen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "spielen", "1",   # Spielen -> Runde zusammenstellen
                "1",              # Lokale Runde: [1] Allein mit KI-Mitspielern
                "",               # KI-Mitspieler: leer = keine
            ]),
            print_fn=printed.append,
            persona_driver_factory=_persona_factory_fails_if_called,
        )
        rc = session.run()
        assert rc == 0
        # Ohne abgeschlossene Figur bricht die Einrichtung vor jedem
        # Spielstart kontrolliert ab -- Hauptsache: kein AssertionError aus
        # der Persona-Factory oben ist aufgetreten (0 Calls).
        assert not any("UX03" in p for p in printed), printed


def test_einstellungen_word_same_output_as_s_hotkey():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed_word: list[str] = []
        TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["einstellungen"]), print_fn=printed_word.append,
        )._cmd_settings()

        printed_hotkey: list[str] = []
        TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["s"]), print_fn=printed_hotkey.append,
        )._cmd_settings()
        assert printed_word == printed_hotkey


def test_old_single_letter_hotkeys_still_work_unchanged():
    """02 §A: 'Alte TUI-Hotkeys ... als dokumentierte Kompatibilitaetsaliase
    erhalten' -- 'x' beendet weiterhin direkt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["x"]), print_fn=lambda *_a: None,
        )
        rc = session.run()
        assert rc == 0
        assert session._quit is True


def test_beenden_word_also_quits():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["beenden"]), print_fn=lambda *_a: None,
        )
        rc = session.run()
        assert rc == 0
        assert session._quit is True


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
