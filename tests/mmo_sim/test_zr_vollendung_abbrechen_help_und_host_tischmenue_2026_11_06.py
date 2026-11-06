#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_vollendung_abbrechen_help_und_host_tischmenue_2026_11_06.py
-- ZR-VOLLENDUNG-OHNE-LAN-20261106-R1 (01_AUFTRAG §2/§4, 02_ABNAHME V1/V4/V5).

Gezielte Belege fuer die beiden in diesem Auftrag beruehrten Terminal-UX-
Grenzen. Standalone-Assert-Skript (Konvention der datierten tests/mmo_sim/
test_zr_betreiber_o*-Dateien: `python3 -m unittest -q` findet die
Modulfunktionen NICHT, deshalb additiv in scripts/smoke.sh gestartet):

1. `_control_help_text("Spielzug")` nennt die drei TATSAECHLICHEN
   `/abbrechen`-Faelle (s. `_run_table_round.decide()`): ohne
   Betreiber-Tisch reine Pause; am Betreiber-Tisch VOR dem gemeinsamen
   Abschluss-Entscheid echter, endgueltiger Verwurf; NACH dem Entscheid
   nur Restabschluss. Der historische, von
   test_ux1_r7_help_footer_... geschuetzte Pause-Teilstring bleibt
   erhalten; der Nicht-Spielzug-Kontext bleibt die reine Schritt-Verwurf-
   Aussage.

2. Das `_cmd_menu_tisch`-Untermenue macht die Betreiber-/Hostaktionen
   (Anbieten/Annehmen/Ablehnen/Starten/Zuschauen) als benannte Optionen
   [5]-[9] auffindbar und dispatcht ueber den ECHTEN run()-Dispatcher auf
   GENAU die unveraenderten `_require_host`-gegateten Methoden. Ein reiner
   Gast (`host_capable=False`) sieht die Hostzeile NICHT; die Gastzeile
   [1]-[4] bleibt bytegleich.

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
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(lines):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return _fn


def _session(td: Path, *, host_capable: bool, script) -> tuple[TuiSession, list[str]]:
    run_dir = td / "run"
    onboarding_dir, catalog_dir = td / "onboarding", td / "catalog"
    write_test_profile(run_dir, max_turns=50)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
        participant_id="p1", run_dir=run_dir, host_capable=host_capable,
        input_fn=_scripted_input(script), print_fn=printed.append,
    )
    return session, printed


def test_abbrechen_help_spielzug_distinguishes_three_table_cases():
    """Der Spielzug-Hilfetext unterscheidet ungebundene Pause, gebundenen
    Verwurf vor Entscheid und Restabschluss nach Entscheid -- und behaelt
    den historischen Pause-Teilstring."""
    with tempfile.TemporaryDirectory() as t:
        session, _ = _session(Path(t), host_capable=True, script=[])
        spielzug = session._control_help_text("Spielzug")
        other = session._control_help_text("Figurwahl")

    # historischer, test_ux1_r7-geschuetzter ungebundener Pause-Teilstring
    assert "wie /pause: kontrolliert pausieren, kein Rollback" in spielzug, spielzug
    # gebundener Betreiber-Tisch VOR dem Abschluss-Entscheid: echter Verwurf
    assert "Betreiber-Tisch" in spielzug, spielzug
    assert "ENDGUELTIGER Verwurf" in spielzug, spielzug
    assert "VOR dem gemeinsamen Abschluss-Entscheid" in spielzug, spielzug
    # NACH dem Entscheid: nur Restabschluss, kein Rollback
    assert "Restabschluss" in spielzug, spielzug
    # Nicht-Spielzug bleibt die reine Schritt-Verwurf-Aussage (unveraendert)
    assert "verwirft nur die gerade offene, unbestaetigte Eingabe" in other, other
    assert "Betreiber-Tisch" not in other, other


def test_host_tisch_submenu_shows_and_dispatches_host_actions():
    """Host-Session: Untermenue zeigt die Hostzeile [5]-[9] und erreicht
    ueber den echten run()-Dispatcher die gegateten Hostmethoden mit den
    richtigen Argumenten."""
    with tempfile.TemporaryDirectory() as t:
        # [5] Tisch anbieten T1
        session, printed = _session(
            Path(t), host_capable=True,
            script=["tisch", "5", "T1", "/zurueck"],
        )
        offer_calls: list[list] = []
        session._cmd_table_offer = lambda args: offer_calls.append(list(args))
        assert session.run() == 0
        assert offer_calls == [["T1"]], offer_calls
        assert any("Betreiber/Host --" in p and "[5] Tisch anbieten" in p for p in printed), printed
        # Gastzeile bleibt bytegleich sichtbar
        assert any("Tisch --" in p and "[1] Offene Tische suchen" in p for p in printed), printed

    with tempfile.TemporaryDirectory() as t:
        # [6] Anfrage annehmen T1 / guestX  -> table_key + guest_id
        session, _ = _session(
            Path(t), host_capable=True,
            script=["tisch", "6", "T1", "guestX", "/zurueck"],
        )
        accept_calls: list[list] = []
        session._cmd_table_accept = lambda args: accept_calls.append(list(args))
        assert session.run() == 0
        assert accept_calls == [["T1", "guestX"]], accept_calls


def test_guest_tisch_submenu_hides_host_actions():
    """Reiner Gast (`host_capable=False`): KEINE Hostzeile, kein Zugriff auf
    die Hostaktionen -- die Gastzeile bleibt unveraendert."""
    with tempfile.TemporaryDirectory() as t:
        session, printed = _session(
            Path(t), host_capable=False,
            script=["tisch", "/zurueck"],
        )
        # Hostmethode kapern, um einen versehentlichen Dispatch zu erkennen
        offer_calls: list[list] = []
        session._cmd_table_offer = lambda args: offer_calls.append(list(args))
        assert session.run() == 0
        assert offer_calls == [], offer_calls
        assert not any("Betreiber/Host --" in p for p in printed), printed
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
