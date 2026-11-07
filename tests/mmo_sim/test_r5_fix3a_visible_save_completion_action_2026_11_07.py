#!/usr/bin/env python3
"""
tests/mmo_sim/test_r5_fix3a_visible_save_completion_action_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5 (Arbeitsblock 1 Punkt 3, F3/
UX-R4-03: "Die Spielzugführung bietet weiter Aktion/Hilfe/Pause, aber
keinen sichtbaren normalen Speichern-/Abschnittsabschluss mit erklaerten
bestehenden Voraussetzungen").

Vorher stand `!save`/`!speichern` (bereits voll funktionsfaehige
Abschlussaktion, `domain.zeitriss.policy.SAVE_COMMANDS`/`is_save_command`)
an KEINER Stelle in der am Spielzug-Prompt erreichbaren Hilfe (`'?' `/
`/hilfe`, derselbe Mechanismus wie `/pause`/`/zurueck`/`/abbrechen`) --
nur externe Dokumentation kannte den Befehl. Dieser Test belegt am echten
`TuiSession`-Code:

1. Fuer den Leader listet die Spielzug-Hilfe `!save`/`!speichern` jetzt
   sichtbar, GENAU wie die uebrigen Steuerzeilen (gleicher Hilfetext-Block,
   gleiches Format) -- inkl. der fachlichen Voraussetzung (sicherer HQ-/
   Debriefkontext) und dass die SL selbst eine Ablehnung erklaert (keine
   neue Saveautoritaet, kein pauschales Sofortspeichern).
2. Fuer einen NICHT-Leader (Gast) erklaert dieselbe Hilfe ehrlich, dass
   `!save` nur wirksam ist, wenn die Leitung (Leader) es sendet -- keine
   falsche Erwartung einer eigenen Gast-Wirkung.
3. Jeder andere Kontext (z.B. 'Erschaffung') bleibt bytegleich ohne diese
   Zeile (keine Breiteneffekte auf andere Dialoge).
4. Ein echter `_readline_with_controls`-Durchlauf im Spielzug-Kontext:
   '?' zeigt die Hilfe (inkl. Save-Zeile) OHNE die Eingabe zu verbrauchen,
   die darauf folgende normale Eingabe (z.B. '!save' selbst) kommt
   unveraendert als Nutztext (`control is None`) beim Aufrufer an -- der
   Befehl wird NICHT von der Steuerzeilenerkennung verschluckt, sondern
   bytegleich an die bestehende `core/runtime.py`-Erkennung
   (`explicit_completion_attempt=is_save_command`) weitergereicht.

Pure Python, nur `assert`, echter Exitcode, synthetischer Temp-Dir, 0
echte GM-/Modellcalls (kein `app_service.run_play_session`-Aufruf noetig,
um den Hilfe-/Durchreichweg zu belegen)."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.domain.zeitriss.policy import is_save_command  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def test_leader_spielzug_help_lists_save_command_with_hq_precondition():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="leader_fix3a", print_fn=lambda *_a: None, host_capable=True,
        )
        help_text = session._control_help_text("Spielzug", is_leader=True)
        assert "!save" in help_text and "!speichern" in help_text, help_text
        assert "HQ-" in help_text or "HQ" in help_text, (
            "Die fachliche Voraussetzung (sicherer HQ-/Debriefkontext) muss in der "
            "sichtbaren Hilfe erklaert sein.", help_text,
        )
        assert "/pause" in help_text and "/zurueck" in help_text, (
            "Die neue Save-Zeile darf die uebrigen Steuerzeilen nicht verdraengen.", help_text,
        )


def test_guest_spielzug_help_explains_save_is_leader_only_not_own_action():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="gast_fix3a", print_fn=lambda *_a: None, host_capable=False,
        )
        help_text = session._control_help_text("Spielzug", is_leader=False)
        assert "!save" in help_text, help_text
        assert "Leader" in help_text or "Leitung" in help_text, (
            "Fuer einen Gast muss die Hilfe ehrlich erklaeren, dass '!save' nur bei der "
            "Leitung (Leader) wirkt, nicht beim Gast selbst.", help_text,
        )


def test_other_contexts_unaffected_no_save_line():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="x_fix3a", print_fn=lambda *_a: None, host_capable=True,
        )
        for ctx in ("Erschaffung", "Tisch", "Abschlusskarte"):
            help_text = session._control_help_text(ctx)
            assert "!save" not in help_text, (ctx, help_text)


def test_help_then_save_command_passes_through_unconsumed_as_plain_text():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="leader_fix3a_b", print_fn=printed.append, host_capable=True,
        )
        session._input = _scripted_input(["?", "!save"])
        text, control = session._readline_with_controls(
            "Deine Aktion: ", context="Spielzug", is_leader=True,
        )
        out = "\n".join(printed)
        assert "!save" in out and "!speichern" in out, (
            "'?' haette die Spielzug-Hilfe MIT der sichtbaren Save-Zeile drucken muessen.", out,
        )
        assert control is None, (
            "'!save' ist KEINE reservierte Steuerzeile (`_CONTROL_TOKENS`) -- sie muss "
            "unveraendert als normaler Nutztext durchgereicht werden.", (text, control),
        )
        assert text == "!save"
        assert is_save_command(text), (
            "Der durchgereichte Text muss von der bestehenden Domaenen-Policy weiterhin als "
            "echtes Save-Kommando erkannt werden (keine neue/zweite Erkennung hier).", text,
        )


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
