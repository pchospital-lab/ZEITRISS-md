#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_litellm_autowire_not_skipped_2026_11_09.py — Delta-
Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1a (P1a).

Vorher übersprang `scripts/launcher.py:action_install` den GESAMTEN
Auto-Wire-/Connection-Check, sobald `_litellm_ok()` einen laufenden
passenden litellm-Container meldete — ein laufender Container ist aber nur
ein Komponentenhinweis (Prozess existiert), kein Beleg für eine
funktionierende OWUI<->LiteLLM-Connection/Route. Zusätzlich fiel
`_litellm_ok()` bei unlesbarer `setup.json` auf einen großzügigen
"irgendein litellm-Container reicht"-Pass zurück statt "nicht prüfbar" zu
melden.

Deckt:
  (A) `_litellm_ok()`: unlesbare Konfig (`load_cfg` wirft) -> `ok=False`,
      "nicht prüfbar" in der Meldung, auch wenn Container laufen.
  (B) `action_install`: wenn `_litellm_ok()` `True` meldet, wird
      `setup_module.ensure_litellm_autowire` trotzdem aufgerufen (nicht nur
      eine "übersprungen"-Meldung ohne jeden Check).

Double-Grenze (A4, offen gelegt): `subprocess.run`, `_detect_install_state`,
`_docker_ok`, `_openwebui_ok`, `_ensure_owui_env`, `_openrouter_key_status`,
`setup_module._update_env_file_preserving`, `setup_module.run_setup`,
`setup_module.ensure_litellm_autowire`, `_prompt`/`_pause` sind vollständig
gedoubelt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import traceback
import types
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n2_litellm_autowire_not_skipped_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


def _fake_result(returncode=0, stdout="", stderr=""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_litellm_ok_unreadable_config_is_not_checkable_not_a_pass():
    """Unlesbare setup.json -> `_litellm_ok()` darf NICHT grosszuegig 'OK'
    zurueckgeben, nur weil IRGENDEIN litellm-Container laeuft."""
    def _run(cmd, **kw):
        return _fake_result(stdout="litellm-irgendwas\n")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run), \
         mock.patch.object(launcher_mod, "_expected_litellm_container_name", return_value=None):
        ok, info = launcher_mod._litellm_ok()
    assert ok is False, f"unlesbare Konfig darf kein grosszuegiger Pass sein: {info}"
    assert "nicht prüfbar" in info, info


def test_action_install_runs_autowire_even_when_container_already_running():
    """`_litellm_ok()` meldet True (Container laeuft) -> `action_install`
    darf den Auto-Wire-/Connection-Check NICHT komplett ueberspringen,
    sondern muss `ensure_litellm_autowire` trotzdem (idempotent) aufrufen."""
    import os
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with mock.patch.object(launcher_mod, "_detect_install_state",
                                side_effect=["fresh", "fresh"]), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
             mock.patch.object(launcher_mod, "_prompt", return_value=""), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "litellm-zeitriss")), \
             mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock:
            launcher_mod.action_install()
        assert run_setup_mock.call_count == 1
        assert autowire_mock.call_count == 1, (
            "ensure_litellm_autowire haette trotz laufendem Container aufgerufen "
            "werden muessen -- ein laufender Container ist nur ein Komponentenhinweis, "
            "kein Beleg fuer eine bestaetigte Connection/Route."
        )
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


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
