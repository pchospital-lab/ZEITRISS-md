#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r7_help_footer_pause_binds_to_saved_state_2026_10_06.py
-- R7 Phase C (BRIEF-W29.md C2), ZEITRISS Terminal UX-1.

`mmo_sim/ui/tui.py:_control_help_text` (generischer Hilfe-Footer, an JEDEM
Kontext gleich) warb `/pause` bisher mit einer nackten Pauschale
("kein Datenverlust") ohne zu sagen, WAS genau erhalten bleibt. Der
Spielzug-Fehlerpfad (`_cmd_local_round`, OSError-Zweig) sagt seit W24b
praeziser: "der zuletzt gueltige, bereits gespeicherte Stand bleibt
erhalten". Dieser Test beweist: der Hilfe-Footer bindet jetzt an denselben
Wortlaut statt der nackten Pauschale, fuer mehrere Kontexte (keine neue
Entscheidungslogik, reiner Text).

Pure Python, nur `assert`, echter Exitcode, keine Subprozesse/Dateien
noetig (reine Textmethode ohne Seiteneffekte)."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import TuiSession  # noqa: E402

_BOUND_WORDING = "zuletzt gueltige, bereits gespeicherte Stand bleibt erhalten"
_BARE_PAUSCHALE = "kontrolliert pausieren, kein Datenverlust"


def _session() -> TuiSession:
    # `_control_help_text` ist eine reine Textmethode ohne Dateizugriff --
    # die Pfade werden nur als `Path`-Attribute gespeichert, nie gelesen.
    return TuiSession(onboarding_dir="/nonexistent/onboarding", catalog_dir="/nonexistent/catalog", participant_id="p1")


def test_help_footer_pause_clause_binds_to_last_saved_state_not_bare_pauschale():
    session = _session()
    for context in ("Spielzug", "Rundenbeitritt", "Startwahl bestaetigen"):
        text = session._control_help_text(context)
        assert _BOUND_WORDING in text, (
            f"Hilfe-Footer (context={context!r}) bindet '/pause' nicht an den "
            f"zuletzt gueltigen gespeicherten Stand: {text!r}"
        )
        assert _BARE_PAUSCHALE not in text, (
            f"Hilfe-Footer (context={context!r}) verwendet noch die nackte "
            f"Pauschale statt der gebundenen Formel: {text!r}"
        )
        # Die Formel haengt am '/pause'-Baustein, nicht irgendwo im Text.
        assert "/pause (kontrolliert pausieren" in text, text
        assert "kein Datenverlust)" in text, text


def test_help_footer_abbrechen_clause_still_context_dependent_unchanged():
    """Scope-Regression: C2 betrifft NUR die '/pause'-Teilzeile -- die
    bereits kontextabhaengige '/abbrechen'-Formel (W24b) bleibt
    unveraendert (keine flaechige Sanierung ohne Befund)."""
    session = _session()
    spielzug_text = session._control_help_text("Spielzug")
    other_text = session._control_help_text("Rundenbeitritt")
    assert "wie /pause: kontrolliert pausieren, kein Rollback" in spielzug_text, spielzug_text
    assert "verwirft nur die gerade offene, unbestaetigte Eingabe" in other_text, other_text


def _run(tests):
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"OK   {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {fn.__name__}: {e}")
        except Exception:
            failures += 1
            print(f"ERROR {fn.__name__}:")
            traceback.print_exc()
    total = len(tests)
    print(f"\n{total - failures}/{total} Tests bestanden.")
    return failures


if __name__ == "__main__":
    failures = _run([
        test_help_footer_pause_clause_binds_to_last_saved_state_not_bare_pauschale,
        test_help_footer_abbrechen_clause_still_context_dependent_unchanged,
    ])
    sys.exit(1 if failures else 0)
