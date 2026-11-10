#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_openrouter_key_hidden_input_2026_11_09.py —
Delta-Test für F1-2 (03_F1_AUFTRAG.md §F1-2: "einmalige VERDECKTE Eingabe
des externen OpenRouter-Keys").

Vorher fragte `scripts/setup.py:run_install_litellm` den OpenRouter-Key
beim Fehlen von Env/`.env` per `input(...)` ab -- der Key stand dabei im
Klartext im Terminal, waehrend der Nutzer ihn eintippt/einfuegt. Der Fix
ersetzt das durch `getpass.getpass(...)` (identisches Muster zum bereits
bestehenden OpenWebUI-Key-Prompt in `scripts/launcher.py:action_install`).

Double-Grenze (A4, offen gelegt): dies ist ein STATISCHER Quelltext-Check
(kein Live-Lauf) -- `run_install_litellm` selbst startet echte Docker-
Container und macht echte HTTP-Aufrufe; ein voller Verhaltenstest haette
dafuer Docker/Netzwerk/eine echte `scripts/litellm/`-Struktur gebraucht,
was fuer einen reinen Eingabe-Sichtbarkeits-Fix unverhaeltnismaessig waere.
Dieser Test beweist NUR, dass die konkrete `input(...)`-Stelle fuer den
OpenRouter-Key durch `getpass(...)` ersetzt wurde und nicht regressiert.

Pure Python, nur `assert`, echter Exitcode, kein Netzwerk/Docker."""
from __future__ import annotations

import re
import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"


def test_openrouter_key_prompt_uses_getpass_not_input():
    source = _SETUP_PY.read_text(encoding="utf-8")
    assert "from getpass import getpass" in source, \
        "getpass-Import fehlt -- sollte bereits vorhanden sein (OWUI-Key-Prompt verwendet es)"

    # Die konkrete OpenRouter-Key-Zeile: vorher `input("OpenRouter-API-Key ...)`,
    # jetzt `getpass("OpenRouter-API-Key ...)`.
    match = re.search(r'(input|getpass)\(\s*"OpenRouter-API-Key', source)
    assert match, "OpenRouter-API-Key-Promptzeile nicht gefunden -- Quelltext umbenannt/verschoben?"
    assert match.group(1) == "getpass", (
        f"OpenRouter-Key-Prompt verwendet weiterhin `{match.group(1)}(...)` -- "
        "Eingabe waere im Klartext sichtbar (F1-2-Regression)."
    )

    # Negativ-Gegenprobe: ein blankes `input("OpenRouter` darf NICHT mehr
    # irgendwo im Modul vorkommen (auch nicht an anderer Stelle neu eingefuehrt).
    assert 'input("OpenRouter-API-Key' not in source, \
        "ein unverdeckter input()-Aufruf fuer den OpenRouter-Key ist wieder im Quelltext"


def test_setup_module_still_parses_and_imports():
    """Regressionsschutz: die Aenderung darf `scripts/setup.py` syntaktisch
    / beim Modulimport nicht beschaedigen (reiner Import, kein `main()`-
    Aufruf, kein Docker/Netzwerk)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("f1_setup_import_check", _SETUP_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "run_install_litellm")
    assert hasattr(module, "getpass")


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
