#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_env_loader_file_fallback_2026_11_09.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-2c (P2-
Konfigurationsrest).

Vorher kehrten `scripts/launcher.py:_ensure_owui_env` und
`scripts/setup.py:_auto_load_owui_env` SOFORT zurück, sobald
`OPENWEBUI_API_KEY` schon im Prozess-Env stand -- eine NUR in
`~/.openwebui_env` gespeicherte bewusste `MMO_SIM_PERSONA_CLI`/`_API_*`-
Wahl wurde dann NIE geladen. `mmo_sim/adapters/factories.py:_maybe_default_
local_persona_api_env` sieht nur das Environment und hätte in diesem Fall
einen ANDEREN API-Default setzen+persistieren können, statt die bereits
gespeicherte Wahl zu respektieren.

Deckt:
  (A) `launcher.py:_ensure_owui_env`: OPENWEBUI_API_KEY bereits im
      Prozess-Env, ABER MMO_SIM_PERSONA_CLI nur in der Datei -> wird
      trotzdem nachgeladen. Ein bereits gesetzter Prozesswert wird dabei
      NICHT überschrieben (Gegenprobe).
  (B) `setup.py:_auto_load_owui_env`: dieselbe Nachlade-Garantie; Rückgabe
      bleibt korrekt (`True`, wenn tatsächlich etwas geladen wurde, auch
      wenn OPENWEBUI_API_KEY schon gesetzt war).
  (C) `factories.py:_maybe_default_local_persona_api_env`: eine gespeicherte
      `MMO_SIM_PERSONA_CLI`-Wahl (nur in der Datei, OPENWEBUI_API_KEY schon
      im Prozess-Env) wird VOR der Default-Entscheidung geladen -> kein
      neuer API-Default wird gesetzt/persistiert (die CLI-Wahl hat Vorrang).

Double-Grenze (A4, offen gelegt): `Path.home()` wird auf ein temporäres
Verzeichnis umgelenkt (kein Zugriff auf die echte `~/.openwebui_env` dieser
Maschine). Reine Datei-/Env-Operationen, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_launcher_spec = importlib.util.spec_from_file_location(
    "f1_n2_env_loader_fallback_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_launcher_spec)
_launcher_spec.loader.exec_module(launcher_mod)

_setup_spec = importlib.util.spec_from_file_location(
    "f1_n2_env_loader_fallback_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_setup_spec)
_setup_spec.loader.exec_module(setup_mod)

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from mmo_sim.adapters import factories as factories_mod  # noqa: E402


def _with_home_env(contents: str):
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-env-loader-"))
    (tmp / ".openwebui_env").write_text(contents, encoding="utf-8")
    return tmp


def test_launcher_ensure_owui_env_loads_missing_persona_choice_despite_key_set():
    home = _with_home_env("MMO_SIM_PERSONA_CLI=claude-from-file\n")
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "already-set-in-process"
    os.environ.pop("MMO_SIM_PERSONA_CLI", None)
    try:
        with mock.patch.object(launcher_mod.Path, "home", return_value=home):
            ok = launcher_mod._ensure_owui_env()
        assert ok is True
        assert os.environ.get("MMO_SIM_PERSONA_CLI") == "claude-from-file", (
            "nur-in-Datei gespeicherte Persona-Wahl haette trotz gesetztem "
            "OPENWEBUI_API_KEY nachgeladen werden muessen"
        )
        assert os.environ.get("OPENWEBUI_API_KEY") == "already-set-in-process", (
            "bereits gesetzter Prozesswert darf NICHT ueberschrieben werden"
        )
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(home, ignore_errors=True)


def test_setup_auto_load_owui_env_loads_missing_persona_choice_despite_key_set():
    home = _with_home_env("MMO_SIM_PERSONA_API_BASE_URL=http://file-stored/v1\n")
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "already-set-in-process"
    os.environ.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
    try:
        with mock.patch.object(setup_mod.Path, "home", return_value=home):
            loaded = setup_mod._auto_load_owui_env()
        assert loaded is True, "Rueckgabe haette True sein muessen -- etwas wurde tatsaechlich nachgeladen"
        assert os.environ.get("MMO_SIM_PERSONA_API_BASE_URL") == "http://file-stored/v1"
        assert os.environ.get("OPENWEBUI_API_KEY") == "already-set-in-process"
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(home, ignore_errors=True)


def test_setup_auto_load_owui_env_does_not_override_existing_process_values():
    """Gegenprobe: ein bewusst gesetzter Prozesswert bleibt Vorrang, auch
    wenn die Datei einen anderen Wert fuer denselben Key hat."""
    home = _with_home_env("OPENWEBUI_URL=http://from-file:9999\n")
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "already-set-in-process"
    os.environ["OPENWEBUI_URL"] = "http://from-process:8080"
    try:
        with mock.patch.object(setup_mod.Path, "home", return_value=home):
            setup_mod._auto_load_owui_env()
        assert os.environ.get("OPENWEBUI_URL") == "http://from-process:8080", (
            "bewusster Prozesswert haette Vorrang vor dem Datei-Wert haben muessen"
        )
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(home, ignore_errors=True)


def _make_fake_repo_with_litellm() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-persona-default-repo-"))
    (tmp / "setup.json").write_text(json.dumps({
        "project": "f1n2test",
        "default_variant": "sonnet",
        "variants": {"sonnet": {"preset_id": "f1n2test-sonnet"}},
        "litellm": {"port": 4322},
    }), encoding="utf-8")
    lite_dir = tmp / "scripts" / "litellm"
    lite_dir.mkdir(parents=True)
    (lite_dir / ".env").write_text(
        "OPENROUTER_API_KEY=sk-or-fake\nLITELLM_MASTER_KEY=sk-litellm-should-not-be-used\n",
        encoding="utf-8",
    )
    shutil.copy(_REPO_ROOT / "scripts" / "setup.py", tmp / "scripts" / "setup.py")
    return tmp


def test_persona_default_respects_stored_cli_choice_loaded_from_file_before_defaulting():
    """F1-N2 WP-N2-2c Kernfall: `MMO_SIM_PERSONA_CLI` steht NUR in der
    Datei, `OPENWEBUI_API_KEY` ist bereits im Prozess-Env gesetzt (z.B. vom
    GM-Pfad weiter oben) -- `_maybe_default_local_persona_api_env` darf
    TROTZDEM keinen neuen API-Default setzen, weil die gespeicherte
    CLI-Wahl Vorrang hat. Vor dem Fix sah die Funktion die Datei nie (das
    Nachladen passierte nirgends), haette also faelschlich den lokalen
    LiteLLM-API-Default gesetzt+persistiert."""
    repo = _make_fake_repo_with_litellm()
    home = _with_home_env("MMO_SIM_PERSONA_CLI=claude-stored-choice\n")
    saved = dict(os.environ)
    for k in ("MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL",
              "MMO_SIM_PERSONA_API_KEY", "MMO_SIM_PERSONA_API_MODEL"):
        os.environ.pop(k, None)
    os.environ["OPENWEBUI_API_KEY"] = "already-set-in-process"
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=home):
            factories_mod._maybe_default_local_persona_api_env(repo_root=repo)
        assert os.environ.get("MMO_SIM_PERSONA_CLI") == "claude-stored-choice", (
            "gespeicherte CLI-Wahl haette geladen werden muessen"
        )
        assert os.environ.get("MMO_SIM_PERSONA_API_BASE_URL") is None, (
            "mit geladener CLI-Wahl haette KEIN neuer API-Default gesetzt werden duerfen"
        )
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(repo, ignore_errors=True)
        shutil.rmtree(home, ignore_errors=True)


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
