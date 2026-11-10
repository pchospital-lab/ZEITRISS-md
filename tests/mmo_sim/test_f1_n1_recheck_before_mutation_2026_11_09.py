#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_recheck_before_mutation_2026_11_09.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP1d (PF1.6).

Vorher klassifizierte `scripts/launcher.py:action_install` den Install-
Zustand per `_detect_install_state()` NUR EINMAL, ganz am Anfang, OHNE
Key (ein frischer Shell-Start kennt `OPENWEBUI_API_KEY` noch nicht) — das
lieferte zwangsläufig `"fresh"`/`"partial_no_key"`, selbst wenn in
OpenWebUI längst Preset+KB existieren. Direkt danach lief `run_setup`,
das gleichnamige Presets/KBs vor dem Neuaufbau LÖSCHT. Fix: NACH
erfolgreicher Key-Erfassung, VOR `run_setup`, wird `_detect_install_state()`
ERNEUT aufgerufen (jetzt mit Key) — liefert dieser Re-Check `"installed"`,
leitet `action_install` auf `[4] Aktualisieren` um statt blind `run_setup`
zu fahren.

Double-Grenze (A4, offen gelegt): `_detect_install_state`, `_docker_ok`,
`_openwebui_ok`, `_ensure_owui_env`, `_openrouter_key_status`,
`setup_module._update_env_file_preserving`, `setup_module.run_setup`,
`action_update`, `_prompt`/`_pause` sind vollständig gedoubelt — dieser
Test beweist NUR die Entscheidungslogik (Re-Check-Ergebnis entscheidet,
ob `run_setup` läuft), keine echte Docker-/OWUI-/Dateisystem-Interaktion.

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
    "f1_n1_recheck_before_mutation_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


def _run_action_install_with_states(first_state: str, recheck_state: str):
    """Fährt `action_install()` mit `_detect_install_state` so gedoubelt,
    dass der ERSTE Aufruf (Eingangsklassifizierung) `first_state` liefert
    und der ZWEITE Aufruf (WP1d-Re-Check nach Key-Erfassung) `recheck_state`.
    Gibt (run_setup_mock, action_update_mock) zurück, damit der Aufrufer
    Call-Counts prüfen kann."""
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
             mock.patch.object(launcher_mod, "_prompt", return_value=""), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=("absent", None)), \
             mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire"):
            launcher_mod.action_install()
        return run_setup_mock, action_update_mock
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_recheck_installed_after_fresh_initial_check_skips_destructive_run_setup():
    """Der Kernfall aus PF1.6: Eingangscheck ohne Key -> "fresh"; Re-Check
    MIT frisch gesetztem Key -> "installed". `run_setup` darf NICHT
    laufen (das würde das bestehende Preset+KB löschen); statt dessen muss
    auf den Update-Pfad umgeleitet werden."""
    run_setup_mock, action_update_mock = _run_action_install_with_states(
        first_state="fresh", recheck_state="installed",
    )
    assert run_setup_mock.call_count == 0, (
        "run_setup haette NICHT laufen duerfen -- der Re-Check fand eine bestehende Installation"
    )
    assert action_update_mock.call_count == 1, "Re-Check 'installed' haette auf action_update umleiten muessen"


def test_recheck_fresh_after_fresh_initial_check_proceeds_with_run_setup():
    """Gegenprobe: bleibt der Re-Check ebenfalls 'fresh' (wirklich nichts
    da), ist `run_setup` weiterhin der korrekte, NICHT-destruktive naechste
    Schritt (normale Erstinstallation)."""
    run_setup_mock, action_update_mock = _run_action_install_with_states(
        first_state="fresh", recheck_state="fresh",
    )
    assert run_setup_mock.call_count == 1, "ein echter Erstinstall (durchgehend 'fresh') sollte run_setup ausloesen"
    assert action_update_mock.call_count == 0


def test_recheck_partial_prompts_before_destructive_run_setup():
    """Re-Check liefert 'partial' (Preset ohne KB-Link) -- run_setup darf
    nur nach expliziter Bestaetigung laufen, nicht automatisch."""
    with mock.patch.object(launcher_mod, "_confirm_reinstall_after_partial", return_value=True):
        run_setup_mock, action_update_mock = _run_action_install_with_states(
            first_state="fresh", recheck_state="partial",
        )
    assert run_setup_mock.call_count == 1, "nach bestaetigtem 'partial' sollte run_setup laufen"
    assert action_update_mock.call_count == 0


def test_recheck_partial_declined_aborts_without_run_setup():
    with mock.patch.object(launcher_mod, "_confirm_reinstall_after_partial", return_value=False):
        run_setup_mock, action_update_mock = _run_action_install_with_states(
            first_state="fresh", recheck_state="partial",
        )
    assert run_setup_mock.call_count == 0, "abgelehnter 'partial'-Re-Check darf run_setup NICHT ausloesen"
    assert action_update_mock.call_count == 0


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
