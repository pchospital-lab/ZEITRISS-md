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
             mock.patch.object(launcher_mod, "resolve_model_provider_choice",
                                return_value=("cloud", None, None)), \
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


def _run_local(first_state: str, recheck_state: str, *, update_answer: str = "j"):
    """O1-B.B3 (RELEASE-CASES.json): dieselbe Installed-/Auth-Recheck-
    Kette wie `_run` oben, aber `resolve_model_provider_choice` liefert
    `("local", <profil>, None)` statt `("cloud", None, None)` -- das
    treibt `_finish_installed_connection`s LOKALEN Zweig (`setup_module.
    _ensure_owui_local_connection` + `_rewire_preset_base_model_local`,
    launcher.py:703-717) echt durch beide Aufrufstellen (Eingangscheck
    UND WP1d-Re-Check), statt ihn am Cloud-Zweig vorbeilaufen zu lassen
    (Pass-2-Lücke, integrator-pass2-report.md: "keiner wurde gegen einen
    zustandsbehafteten OWUI-Double getrieben ... gleiche Luecke wie
    O2-A's Installed/Auth-Recheck-Aufrufer"). `_ensure_owui_local_
    connection`/`_rewire_preset_base_model_local` selbst sind HIER
    gedoubelt (ihre echte HTTP-Logik ist Gegenstand von O2-A/O3-B) --
    dieser Test prüft den LAUNCHER-Dispatch: lokal gewählt -> genau diese
    zwei erhaltenden Funktionen erreicht, mit dem UNVERÄNDERTEN
    Profilobjekt, OHNE `run_setup`/`ensure_litellm_autowire` (kein
    Neuaufbau, kein LiteLLM-Cache-Zwang im lokalen Zweig)."""
    import os
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    local_profile = mock.sentinel.o1b_b3_local_profile
    try:
        with mock.patch.object(launcher_mod, "_detect_install_state",
                                side_effect=[first_state, recheck_state]), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
             mock.patch.object(launcher_mod, "resolve_model_provider_choice",
                                return_value=("local", local_profile, None)), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(launcher_mod.setup_module, "_read_env_file",
                                return_value={"LITELLM_MASTER_KEY": "sk-litellm-test-fake"}), \
             mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
             mock.patch.object(launcher_mod, "action_update") as action_update_mock, \
             mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock, \
             mock.patch.object(launcher_mod.setup_module, "_ensure_owui_local_connection",
                                return_value=(True, "Connection bereits vorhanden")) as conn_mock, \
             mock.patch.object(launcher_mod.setup_module, "_rewire_preset_base_model_local",
                                return_value=(True, "zeigt jetzt auf lokal")) as rewire_mock, \
             mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=None), \
             mock.patch.object(launcher_mod, "_prompt", return_value=update_answer), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
            launcher_mod.action_install()
        return run_setup_mock, autowire_mock, conn_mock, rewire_mock, local_profile
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_installed_on_entry_check_local_branch_reaches_connection_and_rewire_no_rebuild():
    """O1-B.B3 Eingangscheck-Aufrufstelle (launcher.py:979): 'installed'+
    lokal gewähltes Profil erreicht die erhaltende Connection+Rewire-Kette
    -- kein `run_setup` (kein Neuaufbau aus unklarer/blosser Lesung), kein
    `ensure_litellm_autowire` (das ist der CLOUD-LiteLLM-Anschluss, hier
    nicht einschlägig), unverändertes Profilobjekt an beide Funktionen."""
    run_setup_mock, autowire_mock, conn_mock, rewire_mock, profile = _run_local(
        first_state="installed", recheck_state="installed",
    )
    assert run_setup_mock.call_count == 0, "installed+lokal darf NIE run_setup (destruktiv) ausloesen"
    assert autowire_mock.call_count == 0, "lokaler Zweig ruft den Cloud-LiteLLM-Anschluss NICHT auf"
    assert conn_mock.call_count == 1
    assert conn_mock.call_args.args[2] is profile, (
        "das aufgelöste lokale Profil muss unverändert an _ensure_owui_local_connection "
        "durchgereicht werden -- keine Re-Auflösung/Kopie"
    )
    assert rewire_mock.call_count == 1
    assert rewire_mock.call_args.args[-1] is profile


def test_recheck_installed_local_branch_reaches_connection_and_rewire():
    """O1-B.B3 WP1d-Re-Check-Aufrufstelle (launcher.py:1243): derselbe
    erhaltende Anschluss nach Key-Erfassung, lokal gewähltes Profil --
    kein run_setup trotz anfänglich 'fresh' klassifiziertem Bestand."""
    run_setup_mock, autowire_mock, conn_mock, rewire_mock, profile = _run_local(
        first_state="fresh", recheck_state="installed",
    )
    assert run_setup_mock.call_count == 0, (
        "WP1d-Re-Check 'installed'+lokal darf NICHT mehr auf run_setup zurueckfallen, "
        "nur weil der Eingangscheck (ohne Key) noch 'fresh' meldete"
    )
    assert conn_mock.call_count == 1
    assert conn_mock.call_args.args[2] is profile
    assert rewire_mock.call_count == 1


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
