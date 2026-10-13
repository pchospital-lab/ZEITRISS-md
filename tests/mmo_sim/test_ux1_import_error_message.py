#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_import_error_message.py — R8 (Korrekturzyklus 1,
T-Befund 4, UX05/UX18), ZEITRISS Terminal UX-1.

Vorher wurde beim JSON-Import ein kaputter Text mit dem ROHEN Python-
`json`-Fehlertext quittiert, z.B. "Import abgelehnt (strukturell
ungueltig, kein Write): kein gueltiges JSON: Expecting value: line 1
column 1 (char 0)" (`tester/out/BEDIENPROBE.md`, Aufgabe 3/8/9). Das ist
technisches Fachchinesisch fuer Laien. `mmo_sim/domain/zeitriss/
import_export.py` liegt ausserhalb des fuer diesen Korrekturzyklus
erlaubten Edit-Scopes (nur `mmo_sim/ui/*` + Tests) -- der Fix ersetzt
daher NUR die ANZEIGE in `TuiSession._cmd_import()`, nicht die zugrunde-
liegende Fehlerklasse.

Dieser Test beweist: ein strukturell kaputter JSON-Import zeigt eine
ehrliche, laientaugliche Meldung OHNE rohen Python-Fehlertext/Traceback,
behaelt aber den "kein Write"-Schutz UND einen klaren Rueckweg.

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


def test_broken_json_import_shows_layperson_message_no_raw_python_error():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", "{not valid json!!", "ENDE", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        reject_lines = [p for p in printed if "abgelehnt" in p]
        assert reject_lines, printed
        # Kein roher Python-Fehlertext/Traceback mehr in der Anzeige.
        assert not any("Expecting" in p for p in printed), printed
        assert not any("line 1 column" in p for p in printed), printed
        assert not any("char 0" in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed
        # Ehrliche, laientaugliche Kernbotschaft bleibt erhalten.
        assert any("kein gueltiges JSON" in p for p in reject_lines), reject_lines
        assert any("kein Write" in p for p in reject_lines), reject_lines


def test_schema_mismatch_import_message_stays_unchanged_human_readable():
    """Erhaltungsprobe: eine strukturell GUELTIGE JSON ohne v7-Schema
    (kein Parserfehler) zeigt weiterhin ihre bereits verstaendliche,
    unveraenderte Meldung -- R8 ersetzt NUR den rohen JSON-Parserfehler-
    Fall, nicht die anderen (bereits laientauglichen) Schema-Meldungen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", '{"name": "SynthTest"}', "ENDE", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        assert any("kein erkennbares v7-Save-Schema" in p for p in printed), printed


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
