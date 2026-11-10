#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n3_installed_reaches_connection_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N3 §N3-1a.

Vorher endete der `installed`-Zweig von `scripts/launcher.py:action_install`
(Eingangscheck UND der WP1d-Re-Check nach Key-Erfassung) per
`action_update()` (git-pull + `run_sync`, bearbeitet nur Preset/KB/Dateien)
-> `return`. `ensure_litellm_autowire` (der idempotente Anschlusshelfer)
lag nur HINTER `run_setup` und wurde auf diesem Weg NIE erreicht -- ein
Preset+KB ohne fertige OWUI<->LiteLLM-Connection blieb nach einem "[1]"
auf einem bereits installierten Bestand für immer unverbunden.

Deckt:
  (A) Eingangscheck liefert "installed" -> `ensure_litellm_autowire` wird
      aufgerufen, UNABHÄNGIG davon, ob der User das Update-Angebot annimmt
      oder ablehnt (beide Antworten dürfen den Anschluss nicht überspringen).
  (B) WP1d-Re-Check (nach Key-Erfassung) liefert "installed" -> derselbe
      Anschluss wird erreicht (kein reiner `action_update`-Return).
  (C) `run_setup` läuft in KEINEM der Fälle (kein destruktiver Neuaufbau
      für einen bereits installierten Bestand).

Double-Grenze (A4, offen gelegt): `_detect_install_state`, `_docker_ok`,
`_openwebui_ok`, `_ensure_owui_env`, `_openrouter_key_status`,
`setup_module._update_env_file_preserving`, `setup_module.run_setup`,
`setup_module.ensure_litellm_autowire`, `action_update`,
`_resolve_orphaned_kb_for_partial`, `_prompt`/`_pause` sind vollständig
gedoubelt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n3_installed_reaches_connection_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


def _run(first_state: str, recheck_state: str, *, update_answer: str = ""):
    import os
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with mock.patch.object(launcher_mod, "_detect_install_state",
                                side_effect=[first_state, recheck_state]), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(launcher_mod.setup_module, "_read_env_file",
                                return_value={"LITELLM_MASTER_KEY": "sk-litellm-test-fake"}), \
             mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
             mock.patch.object(launcher_mod, "action_update") as action_update_mock, \
             mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock, \
             mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=None), \
             mock.patch.object(launcher_mod, "_prompt", return_value=update_answer), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
            launcher_mod.action_install()
        return run_setup_mock, action_update_mock, autowire_mock
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_installed_on_entry_check_reaches_autowire_when_update_accepted():
    run_setup_mock, action_update_mock, autowire_mock = _run(
        first_state="installed", recheck_state="installed", update_answer="j",
    )
    assert run_setup_mock.call_count == 0, "installed darf NIE run_setup (destruktiv) ausloesen"
    assert action_update_mock.call_count == 1
    assert autowire_mock.call_count == 1, (
        "installed-Zweig (Eingangscheck) muss ensure_litellm_autowire erreichen, "
        "nicht per action_update()->return daran vorbeilaufen"
    )


def test_installed_on_entry_check_reaches_autowire_even_when_update_declined():
    """Kernfall: der Anschluss ist UNABHAENGIG vom Update-Angebot faellig --
    auch wer das Update ablehnt, darf nicht auf einer unverbundenen
    Installation sitzen bleiben."""
    run_setup_mock, action_update_mock, autowire_mock = _run(
        first_state="installed", recheck_state="installed", update_answer="n",
    )
    assert run_setup_mock.call_count == 0
    assert action_update_mock.call_count == 0, "abgelehntes Update darf nicht trotzdem laufen"
    assert autowire_mock.call_count == 1, (
        "Anschluss darf nicht am abgelehnten Update-Angebot haengen -- "
        "ensure_litellm_autowire muss trotzdem erreicht werden"
    )


def test_recheck_installed_reaches_autowire_not_just_action_update_return():
    """WP1d-Re-Check-Pfad (Eingangscheck 'fresh' ohne Key, Re-Check nach
    Key-Erfassung liefert 'installed') -- derselbe Anschluss-Fix gilt hier
    genauso, das ist der im Generalurteil konkret beschriebene Nutzerfall
    (Abbruch nach KB-/Presetanlage vor dem fertigen Anschluss)."""
    run_setup_mock, action_update_mock, autowire_mock = _run(
        first_state="fresh", recheck_state="installed", update_answer="j",
    )
    assert run_setup_mock.call_count == 0
    assert action_update_mock.call_count == 1
    assert autowire_mock.call_count == 1, (
        "Re-Check 'installed' darf nicht per reinem action_update-Return am "
        "Anschlusshelfer vorbeilaufen"
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
