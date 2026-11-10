#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n4_installed_missing_master_key_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N4 §N4-1 P1 (A1).

Vorher rief `_finish_installed_connection` (launcher.py) immer nur
`ensure_litellm_autowire` auf. Fehlte der LiteLLM-Master-Key (z.B. LiteLLM
nie eingerichtet), druckte `ensure_litellm_autowire` selbst nur einen
Verweis auf "Menü [1]/--install-litellm" -- aber der `installed`-Zweig IST
bereits [1]. [1] landete damit wieder an derselben Stelle (live aufgezeichnet
im n3-continuation-transcript, 108-131), ohne dass der Anschluss je fertig
wurde.

Deckt (echter Aufruferzweig, beide installed-[1]-Caller via
`_finish_installed_connection`):
  (A) Fehlender Master-Key + Zustimmung -> `run_install_litellm` (derselbe
      Baustein wie im fresh-Weg) wird aufgerufen, NICHT nur eine erneute
      `ensure_litellm_autowire`-Warnung ohne Fortsetzung. Kein Rückverweis
      in dieselbe Schleife.
  (B) Fehlender Master-Key + Ablehnung -> weder `run_install_litellm` noch
      `ensure_litellm_autowire` laufen (kein stiller Doppel-Pfad), klarer
      Hinweis zum erneuten Versuch.
  (C) Gegenprobe: Master-Key VORHANDEN -> `ensure_litellm_autowire` läuft
      direkt (eigene gespeicherte Werte korrekt weitergeführt), KEIN
      `run_install_litellm`-Aufruf (keine überflüssige Zweit-Installation).
  (D) Beide installed-Caller (Eingangscheck UND WP1d-Re-Check) zeigen
      dasselbe Verhalten -- der Fix sitzt an der gemeinsamen Stelle
      `_finish_installed_connection`.

Double-Grenze (A4, offen gelegt): `_detect_install_state`, `_docker_ok`,
`_openwebui_ok`, `_ensure_owui_env`, `_openrouter_key_status`,
`setup_module._update_env_file_preserving`, `setup_module.run_setup`,
`setup_module.run_install_litellm`, `setup_module.ensure_litellm_autowire`,
`action_update`, `_resolve_orphaned_kb_for_partial`, `_prompt`/`_pause` sind
vollständig gedoubelt. `setup_module._read_env_file` ist NICHT gedoubelt --
läuft gegen ein echtes temporäres `scripts/litellm/.env` (oder dessen
Abwesenheit), damit der real geprüfte Zweig genau der ist, den
`_finish_installed_connection` auch live nimmt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n4_installed_missing_master_key_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


def _run(*, first_state: str, recheck_state: str, master_key_present: bool,
         install_answer: str = "j"):
    import os
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp_repo = Path(tmp_s)
            (tmp_repo / "scripts" / "litellm").mkdir(parents=True)
            if master_key_present:
                (tmp_repo / "scripts" / "litellm" / ".env").write_text(
                    "LITELLM_MASTER_KEY=sk-litellm-already-there\n", encoding="utf-8",
                )
            # kein .env -> echte _read_env_file liefert {} -> master_key fehlt,
            # genau der reale Zweig aus dem Generalurteil-Befund.
            with mock.patch.object(launcher_mod, "REPO", tmp_repo), \
                 mock.patch.object(launcher_mod, "load_cfg", return_value={"project": "Proj"}), \
                 mock.patch.object(launcher_mod, "_detect_install_state",
                                    side_effect=[first_state, recheck_state]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=True), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod, "action_update", side_effect=lambda: None) as action_update_mock, \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock, \
                 mock.patch.object(launcher_mod.setup_module, "run_install_litellm") as install_litellm_mock, \
                 mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=("absent", None)), \
                 mock.patch.object(launcher_mod, "_prompt", side_effect=[install_answer, install_answer]), \
                 mock.patch.object(launcher_mod, "_pause"), \
                 mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
                launcher_mod.action_install()
            return run_setup_mock, action_update_mock, autowire_mock, install_litellm_mock
    finally:
        import os
        os.environ.clear()
        os.environ.update(saved_env)


def test_missing_master_key_accepted_reaches_install_litellm_not_same_loop():
    """(A): fehlender Master-Key, User stimmt der Einrichtung zu ->
    `run_install_litellm` wird erreicht -- der Anschluss kann fertig
    werden, statt nur erneut auf Menü [1] zu verweisen."""
    run_setup_mock, _action_update_mock, autowire_mock, install_litellm_mock = _run(
        first_state="installed", recheck_state="installed", master_key_present=False,
        install_answer="j",
    )
    assert run_setup_mock.call_count == 0, "installed darf NIE run_setup (destruktiv) ausloesen"
    assert install_litellm_mock.call_count == 1, (
        "fehlender Master-Key + Zustimmung haette run_install_litellm erreichen muessen "
        "(derselbe Baustein wie im fresh-Weg) -- statt in dieselbe Schleife zurueckzuverweisen"
    )
    assert autowire_mock.call_count == 0, (
        "ensure_litellm_autowire direkt aufzurufen waere wieder der alte Rueckverweis "
        "(druckt nur die Menü-[1]-Warnung, ohne den Schritt selbst anzubieten)"
    )


def test_missing_master_key_declined_skips_both_helpers():
    """(B): fehlender Master-Key, User lehnt ab -> kein stiller
    Doppel-Pfad, weder run_install_litellm noch ensure_litellm_autowire
    laufen."""
    run_setup_mock, _au, autowire_mock, install_litellm_mock = _run(
        first_state="installed", recheck_state="installed", master_key_present=False,
        install_answer="n",
    )
    assert run_setup_mock.call_count == 0
    assert install_litellm_mock.call_count == 0, "Ablehnung darf die Einrichtung nicht trotzdem ausloesen"
    assert autowire_mock.call_count == 0, "Ablehnung darf nicht auf den alten Rueckverweis zurueckfallen"


def test_master_key_present_uses_existing_values_no_second_install():
    """(C) Gegenprobe: Master-Key ist schon da -- eigene gespeicherte Werte
    korrekt weiterfuehren, KEIN run_install_litellm (keine ueberfluessige
    Zweit-Installation)."""
    run_setup_mock, _au, autowire_mock, install_litellm_mock = _run(
        first_state="installed", recheck_state="installed", master_key_present=True,
    )
    assert run_setup_mock.call_count == 0
    assert install_litellm_mock.call_count == 0, "vorhandener Master-Key braucht keine Neueinrichtung"
    assert autowire_mock.call_count == 1, "vorhandener Master-Key fuehrt direkt zu ensure_litellm_autowire"


def test_recheck_installed_missing_master_key_also_reaches_install_litellm():
    """(D): WP1d-Re-Check-Pfad (Eingangscheck 'fresh' ohne Key, Re-Check
    nach Key-Erfassung liefert 'installed') -- derselbe Fix gilt hier
    genauso, da beide Caller `_finish_installed_connection` teilen."""
    run_setup_mock, action_update_mock, autowire_mock, install_litellm_mock = _run(
        first_state="fresh", recheck_state="installed", master_key_present=False,
        install_answer="j",
    )
    assert run_setup_mock.call_count == 0
    assert action_update_mock.call_count == 1
    assert install_litellm_mock.call_count == 1, (
        "Re-Check 'installed' mit fehlendem Master-Key muss ebenfalls run_install_litellm erreichen"
    )
    assert autowire_mock.call_count == 0


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
