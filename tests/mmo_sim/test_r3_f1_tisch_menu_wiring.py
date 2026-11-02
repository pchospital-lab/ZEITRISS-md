#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_f1_tisch_menu_wiring.py -- ZR-FIGURENREISE-TISCH-
NACHZUG-20261102-R3, Beleglueckenschluss zu F1 (Abschluss-Critic
Restbefund 2).

Die neuen F1-Tests (`test_r3_f1_guest_table_service.py`) rufen
`_cmd_table_request_join`/`_cmd_table_accept` direkt auf und umgehen den
Menue-Dispatcher vollstaendig. Damit war ausgerechnet die im R2-Review am
konkretesten benannte, in R3 behobene SICHTBARE Verdrahtung ungetestet:
- die unbedingte Boot-Menuezeile `[tisch]` (Host UND Gast), und
- der `run()`-Dispatchzweig `choice == "tisch"` -> `_cmd_menu_tisch`,
  dessen Untermenue-Option 1 den Tischdienst `_cmd_table_search` erreicht.

Eine kuenftige Regression hier (Tippfehler im `choice`-String, ein
versehentlich entferntes `elif`, eine geloeschte Menuezeile) wird von den
206 bestehenden Testdateien nicht erkannt. Dieser schmale Test schliesst
genau diese Luecke -- ueber den ECHTEN run()-Dispatcher mit gescripteten
Eingaben, kein Direktaufruf der Zielmethode.

Pure Python, nur `assert`, echter Exitcode (gleiches Muster wie
`test_r3_f1_guest_table_service.py`)."""
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
from mmo_sim.ui.tui import TuiSession, render_boot_menu  # noqa: E402


def _scripted_input(lines):
    """Liefert die gescripteten Zeilen der Reihe nach; danach EOF
    (`EOFError` -> `_readline` wirft `EndOfInput` -> `run()` beendet mit 0).
    So wird die exakte Eingabemenge erzwungen: ein versehentlich
    zusaetzlich konsumierter Prompt wuerde sofort als EOF auffliegen."""
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return _fn


def test_f1_boot_menu_shows_tisch_entry_for_guest_and_host():
    """Die `[tisch]`-Zeile ist UNBEDINGT sichtbar -- fuer Gast
    (`host_capable=False`) UND Host (`host_capable=True`). Reine
    Anzeige-/Wiring-Pruefung an der echten Produktfunktion."""
    guest_menu = render_boot_menu(None, host_capable=False)
    host_menu = render_boot_menu(None, host_capable=True)
    assert "[tisch]" in guest_menu, guest_menu
    assert "[tisch]" in host_menu, host_menu
    # Die Zeile beschreibt den Gastnutzen (Mitspielen bei einem anderen
    # Host) -- kein host-only Gate in der Anzeige.
    assert "Tisch suchen / anfragen" in guest_menu, guest_menu


def test_f1_boot_dispatch_tisch_reaches_table_search_via_submenu():
    """Der ECHTE run()-Dispatcher erreicht ueber `tisch` -> Untermenue-
    Option `1` den Tischdienst `_cmd_table_search` -- nicht per Direkt-
    aufruf, sondern durch gescriptete Eingaben am Hauptmenue. Damit sind
    sowohl der `choice == "tisch"`-Zweig als auch die Untermenue-Option 1
    gegen eine stille Regression abgesichert."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        onboarding_dir, catalog_dir = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=50)

        search_calls: list[list] = []
        printed: list[str] = []

        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            participant_id="guestW", run_dir=run_dir, host_capable=False,
            input_fn=_scripted_input(["tisch", "1", "/zurueck"]),
            print_fn=printed.append,
        )

        # Zielmethode kapern (kein echter Tischdienst-Seiteneffekt noetig --
        # geprueft wird die VERDRAHTUNG, nicht `_cmd_table_search` selbst,
        # das `test_stage5_tui_wiring`/`test_r2_f1_f2_f3_tabledienst`
        # bereits echt abdecken).
        def _spy_table_search(args):
            search_calls.append(list(args))

        session._cmd_table_search = _spy_table_search

        exit_code = session.run()

        assert exit_code == 0, f"run() haette am EOF sauber mit 0 enden muessen: {exit_code}"
        assert search_calls == [[]], (
            "Hauptmenue 'tisch' -> Untermenue '1' haette GENAU EINMAL "
            f"_cmd_table_search([]) erreichen muessen, erreicht: {search_calls!r}"
        )
        # Das Untermenue wurde wirklich angezeigt (echter _cmd_menu_tisch-
        # Durchlauf, nicht nur ein stiller Dispatch).
        assert any("Tisch --" in p and "[1] Offene Tische suchen" in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
