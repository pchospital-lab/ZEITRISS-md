#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_terminal_m_completion_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP1e (PF1.5).

Vorher nannte `scripts/setup.py:run_setup`s Abschlussmeldung
Browser→neuer Chat→Preset→Starttext als EINZIGEN "So geht's weiter"-Weg;
`run_install_litellm`s Erfolgsmeldung nannte Menü `[3]` als nächsten
Schritt. Beides führte am normalen Terminalspiel (`[M] ZEITRISS spielen
(Terminal)` im ZEITRISS-Starter, s. `scripts/launcher.py`) vorbei — obwohl
das seit der venv-Bootstrap-Arbeit (F1-1) der vorgesehene Normalweg ist.

Statischer Quelltext-Check (analog zum bestehenden Muster in
`test_f1_openrouter_key_hidden_input_2026_11_09.py`): `run_setup`/
`run_install_litellm` starten echte Docker-Container, KB-Indexierung und
OpenWebUI-Calls — ein voller Verhaltenstest wäre für eine reine
Formulierungsänderung unverhältnismäßig. Dieser Test beweist NUR, dass
beide Abschlusstexte jetzt `[M]` als normalen Weg nennen UND den
Browser-Chat weiterhin als optional erwähnen (nicht ersatzlos gestrichen).

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import re
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"
_SOURCE = _SETUP_PY.read_text(encoding="utf-8")


def _function_source(name: str) -> str:
    """Extrahiert den Quelltext einer Top-Level-`def <name>(` bis zur
    naechsten Top-Level-`def ` (spaltenbuendig bei Spalte 0) -- reicht fuer
    dieses Modul, das keine verschachtelten Top-Level-Funktionsdefinitionen
    mit identischem Einrueckmuster hat."""
    match = re.search(rf"^def {re.escape(name)}\(", _SOURCE, re.MULTILINE)
    assert match, f"Funktion {name} nicht gefunden -- Quelltext umbenannt/verschoben?"
    start = match.start()
    next_def = re.search(r"^def \w", _SOURCE[match.end():], re.MULTILINE)
    end = match.end() + next_def.start() if next_def else len(_SOURCE)
    return _SOURCE[start:end]


def test_run_install_litellm_success_message_names_terminal_m_as_normal_way():
    body = _function_source("run_install_litellm")
    assert "[M]" in body, "run_install_litellm nennt den Terminalweg [M] nicht mehr in der Erfolgsmeldung"
    assert "optional" in body.lower(), "Browser-Chat sollte als optional erwaehnt bleiben, nicht ersatzlos gestrichen"
    assert "Nichts mehr zu klicken — mit Menü [3] direkt ins Spiel." not in body, (
        "alte Formulierung (Menü [3] als einziger naechster Schritt) ist noch da -- WP1e-Regression"
    )


def test_run_setup_completion_message_names_terminal_m_as_normal_way():
    body = _function_source("run_setup")
    # "So geht's weiter:" Abschnitt extrahieren, um sicherzustellen, dass
    # [M] DIREKT dort (nicht nur irgendwo sonst im riesigen run_setup) als
    # erster/normaler Weg genannt wird.
    idx = body.find("So geht's weiter:")
    assert idx != -1, "Abschlussabschnitt 'So geht's weiter:' nicht gefunden"
    snippet = body[idx:idx + 400]
    assert "[M]" in snippet, f"[M] wird im Abschlussabschnitt nicht genannt:\n{snippet}"
    assert "optional" in snippet.lower(), f"Browser-Chat sollte als optional markiert sein:\n{snippet}"


def test_setup_module_still_parses_and_imports():
    """Regressionsschutz: die Textaenderung darf `scripts/setup.py`
    syntaktisch/beim Modulimport nicht beschaedigen."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("f1_n1_terminal_m_setup_import_check", _SETUP_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "run_setup")
    assert hasattr(module, "run_install_litellm")


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
