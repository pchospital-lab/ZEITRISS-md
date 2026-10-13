#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_synthetic_creation_refusal_and_config_2026_10_06.py
— W19/F03 (ZEITRISS Terminal UX-1, R5): die zwei Erhaltungs-/Fehlerfaelle
des echten Erschaffungsvertrags (`ui/tui.py:_cmd_new_or_switch_character`),
die der Main-Pre-T-Nachweis zusaetzlich zur erfolgreichen Erschaffung
(s. `test_ux1_r5_synthetic_creation_process_journey_2026_10_06.py`)
verlangt: eine Absage WAEHREND des Dialogs UND eine fehlende SL-
Konfiguration -- BEIDE sauber (kein Crash, kein erfundener Fortschritt).

Gleiches In-Prozess-Muster wie `test_ux1_q07_resume_open_creation_
2026_10_05.py` (direkte `TuiSession`-Konstruktion mit `input_fn`/`print_fn`,
ein scriptetes GM-Fake statt eines echten Loopback-HTTP-Servers) -- fuer
diese beiden reinen Kontrollfluss-/Konfigurationsproben ist kein echter
Subprozess/keine echte HTTP-Grenze noetig (anders als die Erschaffungs-
und Spielbelege, die echte Subprozesse gegen `_ux1_r5_synthetic_creation_
support.CreationCapableSmartGmServer` nutzen).

Pure Python, nur `assert`, synthetische Daten/Temp-Dirs, kein Netzwerk-/
externer Providercall."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _QuestionOnlyGm:
    """Scriptetes GM-Fake: liefert bei JEDEM Call nur eine Frage, NIE einen
    v7-Save -- fuer die Absage-Probe darf die Fake-SL ohnehin nie ein
    zweites Mal real aufgerufen werden (die Absage passiert lokal, VOR
    jedem weiteren Modellaufruf)."""

    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        return {"content": "Welche Grundausstattung waehlst du?"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def test_creation_cancel_via_abbrechen_leaves_dialog_open_no_save_no_crash():
    """Absage: der Mensch antwortet auf die EINE SL-Frage mit '/abbrechen'
    (zentraler Kontrollvertrag, `_readline_with_controls`) statt mit einem
    freien Text. Erwartung: `run_admitted_creation_dialog` liefert
    `status='paused'` (ueber `ReplyResult(kind='paused', ...)`), KEIN
    zweiter Fake-SL-Call, KEIN Save, der Onboarding-Zustand bleibt
    `in_progress` (fortsetzbar), kein Crash."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        pid = "canceller"
        write_test_profile(run_dir)

        gm = _QuestionOnlyGm()
        printed: list[str] = []
        queued = iter(["/abbrechen"])

        def _input_fn(prompt: str = "") -> str:
            return next(queued)

        session = TuiSession(
            onboarding_dir, catalog_dir, pid,
            input_fn=_input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()
        out = "\n".join(printed)

        assert len(gm.calls) == 1, f"genau EIN echter Fake-SL-Call (die Frage), kein zweiter nach der Absage: {gm.calls}"
        assert "Lokal verarbeitet" in out and "wird NICHT als Antwort an die SL gesendet" in out, out
        assert "Erschaffung abgeschlossen" not in out, "keine erfundene Fertigstellung nach einer Absage"

        state = onboarding.peek(onboarding_dir, pid)
        assert state is not None and state.status == "in_progress", (
            f"Dialog muss nach einer Absage offen/fortsetzbar bleiben, nicht completed/verloren: {state}"
        )
        catalog_figures = list((catalog_dir / "figures").glob("*.json")) if (catalog_dir / "figures").is_dir() else []
        assert not catalog_figures, "keine Katalog-/Figur-Persistenz nach einer Absage"


def test_creation_without_configured_sl_binding_stays_honest_not_configured():
    """Fehlende Konfiguration: `_cmd_new_or_switch_character` OHNE `run_dir`/
    `gm_transport_factory` (NOT_CONFIGURED) bleibt ehrlich -- derselbe
    bestehende, klare Hinweistext, KEIN Absturz, KEIN Fake-SL-Call (es
    existiert dafuer gar kein Transport), kein automatischer Spielstart/
    keine erfundene Fortschrittsmeldung. Gleiches Erhaltungsmuster wie
    `test_q07_fortsetzen_without_configured_sl_binding_stays_honest_no_fake_
    progress` in `test_ux1_q07_resume_open_creation_2026_10_05.py`, hier
    fuer den FRISCHEN Erschaffungseinstieg (nicht den Fortsetzen-Dispatch)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir = root / "onboarding"
        catalog_dir = root / "catalog"
        pid = "unconfigured"

        printed: list[str] = []

        def _eof_input(prompt: str = "") -> str:
            raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, pid,
            input_fn=_eof_input, print_fn=printed.append,
            # Bewusst KEIN run_dir/states_dir/schema_path/gm_transport_factory.
        )
        session._cmd_new_or_switch_character()
        out = "\n".join(printed)

        assert "konfigurierte SL-Anbindung" in out and "hier nicht" in out, out
        assert "Erschaffung abgeschlossen" not in out
        assert "Traceback" not in out

        state = onboarding.peek(onboarding_dir, pid)
        assert state is not None and state.status == "in_progress", (
            f"ohne SL-Anbindung bleibt der Dialog ehrlich offen, kein erfundener Abschluss: {state}"
        )


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
