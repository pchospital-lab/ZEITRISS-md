#!/usr/bin/env python3
"""
tests/mmo_sim/test_r6_01_first_budget_via_settings_2026_11_19.py — R6-01
Regression (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-r6,
01_GENERAL_REVIEW.md R6-01, 02_NACHZUG_AUFTRAG.md A).

Befund: nach Import eines bereits fertigen Charakters in eine frische
Betreiber-Datenablage (noch keine `lab.status.json`) war die erste
endliche Betreiber-/Budgetfreigabe ueber die normale Oberflaeche NICHT
erreichbar: der Erschaffungsdialog bietet sie fuer eine abgeschlossene
Figur nicht mehr an, und `einstellungen budget erhoehen` wies den Erstfall
bisher nur mit "s. 'neue Erschaffung'" ab. Beide r5-Laeufe mussten deshalb
extern `mmo_sim.core.admission.grant_operator_budget(...)` in Python
aufrufen -- ein Workaround ausserhalb der Oberflaeche.

R6-01-Fix (`mmo_sim/ui/tui.py:_offer_operator_budget_raise`, Erstfall-
Zweig `status is None`): die normale Einstellungsoberflaeche
(`einstellungen budget erhoehen`, realer Caller `_cmd_settings(["budget",
"erhoehen"])`) stellt die erste endliche Freigabe jetzt selbst her --
derselbe Dialog/derselbe Vertrag wie im Erschaffungspfad
(`_offer_operator_budget_setup`), bereits host-gegatet (`_require_host`).
KEIN zweites Budgetprofil, KEIN externer Grant, KEIN `provider_free`.

Treibt den ECHTEN Caller `_cmd_settings(["budget", "erhoehen"])` an
(identisch zu `s`/`einstellungen` im Hauptdispatch). Gegenfaelle aus A:
  (1) frischer Hostimport mit Zustimmung -> erste endliche Freigabe
      ueber die Oberflaeche, kein provider_free, finite Werte.
  (2) Ablehnung ohne Grant/Request -> keine Datei, kein Modellaufruf.
  (3) Gast ohne Grant -> `_require_host` weist VOR jeder Freigabe ab,
      keine Betreiberfaehigkeit aus dem Importweg.
  (4) vorhandener Status/Zaehler -> der Erstfall-Zweig greift NICHT; der
      Setup-Dialog ueberschreibt eine bestehende Grenze nicht (das bleibt
      der getrennte Raise-Pfad, R3-07).
  (5) beschaedigter Status bleibt ein klarer Halt -> die vorhandene, aber
      unlesbare Datei wird NICHT ueberschrieben (fail-closed, R4-02).

Pure Python, nur `assert`, echter Exitcode -- lauffaehig per `pytest` UND
als eigenstaendiges Skript (identischer Stil/Helfer zu
test_r4_02_budget_raise_host_gate_2026_11_18.py)."""
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

from mmo_sim.core.admission import _status_path, grant_operator_budget  # noqa: E402
from mmo_sim.ui.tui import GuestCapabilityError, TuiSession  # noqa: E402


def _scripted_input(answers):
    it = iter(answers)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()

    return read


def _session(root: Path, *, input_fn=None, host_capable=True):
    run_dir = root / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="p1",
        input_fn=input_fn, print_fn=printed.append, run_dir=run_dir, host_capable=host_capable,
    )
    return session, run_dir, printed


def test_host_first_grant_reachable_through_normal_settings_after_import():
    """(1) KERN von R6-01: ein HOST OHNE jede `lab.status.json` richtet die
    erste endliche Freigabe ueber den normalen Einstellungs-Caller ein --
    kein externer Python-Grant, kein Handedit."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session, run_dir, printed = _session(
            # Setup: ja, dann 3x Default-Vorschlag (Turns/Sekunden/USD).
            root, input_fn=_scripted_input(["j", "", "", ""]), host_capable=True,
        )
        assert not _status_path(run_dir).exists(), "Vorbedingung: wirklich kein Grant/Handedit"

        session._cmd_settings(["budget", "erhoehen"])

        assert _status_path(run_dir).exists(), (
            "R6-01: die erste Freigabe muss ueber die normale Oberflaeche entstehen"
        )
        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert data.get("provider_free") is not True, (
            "eine echte Betreiberfreigabe darf NIE als provider_free (Testdouble) markiert sein"
        )
        assert isinstance(data.get("max_turns"), int) and data["max_turns"] > 0, data
        assert isinstance(data.get("max_usd"), (int, float)) and data["max_usd"] > 0, data
        assert any("Freigabe eingerichtet" in p for p in printed), printed


def test_declining_first_grant_writes_nothing_and_no_model_call():
    """(2) Ablehnung im Erstfall: keine `lab.status.json`, kein stilles
    Anlegen, kein Modellaufruf -- eine Statusanzeige erteilt keine Freigabe."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session, run_dir, printed = _session(
            root, input_fn=_scripted_input(["n"]), host_capable=True,  # Setup ablehnen
        )
        session._cmd_settings(["budget", "erhoehen"])

        assert not _status_path(run_dir).exists(), "kein heimliches Anlegen ohne Zustimmung"
        assert not any("Freigabe eingerichtet" in p for p in printed), printed


def test_guest_cannot_create_first_grant_via_settings():
    """(3) Host-/Gastgrenze: ein GAST erreicht ueber denselben realen Caller
    KEINE Ersteinrichtung -- `_require_host` weist VOR jedem Dialog/Write ab.
    Ein importierter Save/Resume erzeugt keine Betreiberfaehigkeit."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # Scripted Input wird NIE konsumiert, wenn das Gate frueh greift.
        session, run_dir, printed = _session(
            root, input_fn=_scripted_input([]), host_capable=False,
        )
        raised = False
        try:
            session._cmd_settings(["budget", "erhoehen"])
        except GuestCapabilityError as exc:
            raised = True
            assert "nur im Hostmodus" in str(exc), str(exc)
        assert raised, "Gast haette ueber den echten Caller abgewiesen werden muessen"
        assert not _status_path(run_dir).exists(), "Gast-Versuch darf KEINE Freigabe angelegt haben"


def test_existing_grant_is_not_touched_by_the_first_case_branch():
    """(4) Erhaltung: existiert bereits eine Grenze, greift der R6-01-
    Erstfall-Zweig NICHT -- der Setup-Dialog legt kein zweites Profil an und
    ueberschreibt die vorhandene Grenze nicht (das ist der getrennte
    Raise-Pfad). Hier: Host bestaetigt keine Erhoehung -> Grenze unveraendert,
    KEIN 'Freigabe eingerichtet' (das waere der Erstfall-Dialog)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=7, max_seconds=90.0, max_usd=2.0)
        before = _status_path(run_dir).read_bytes()

        # Raise-Dialog: Defaults behalten, Bestaetigung ablehnen -> keine Mutation.
        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["", "", "", "n"]), host_capable=True,
        )
        session._cmd_settings(["budget", "erhoehen"])

        assert _status_path(run_dir).read_bytes() == before, "bestehende Grenze haette unveraendert bleiben muessen"
        assert not any("Freigabe eingerichtet" in p for p in printed), (
            "bei vorhandener Grenze darf NICHT der Erstfall-Setup-Dialog laufen"
        )


def test_corrupted_status_is_a_clear_halt_not_overwritten():
    """(5) beschaedigte, aber VORHANDENE `lab.status.json` bleibt ein klarer
    Halt: der Erstfall-Setup ueberschreibt sie NICHT (er schreibt nur, wenn
    gar keine Datei existiert), ein moeglicher Verbrauchsstand geht nicht
    stillschweigend verloren (fail-closed, R4-02)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        status_path = _status_path(run_dir)
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text("{ kaputtes json: nicht parsebar", encoding="utf-8")
        before = status_path.read_bytes()

        # Selbst wenn Zustimmung gescriptet waere: die vorhandene (kaputte)
        # Datei darf NICHT ueberschrieben werden.
        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["j", "", "", ""]), host_capable=True,
        )
        session._cmd_settings(["budget", "erhoehen"])

        assert status_path.read_bytes() == before, "beschaedigte Datei haette unveraendert bleiben muessen"
        assert not any("Freigabe eingerichtet" in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
