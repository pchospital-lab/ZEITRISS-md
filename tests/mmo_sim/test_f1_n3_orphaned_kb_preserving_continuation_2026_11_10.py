#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n3_orphaned_kb_preserving_continuation_2026_11_10.py
— Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N3 §N3-1b.

Vorher führte `state == "partial"` (inkl. des WP-N2-1d-Orphaned-KB-Falls:
eine eindeutig namensgleiche KB existiert bereits, aber kein Preset) IMMER
zu `_confirm_reinstall_after_partial()` (Default-Antwort "j") -> bei
Zustimmung `run_setup`s destroy&recreate-Block, der die vorhandene KB
LÖSCHT und neu aufbaut. Für eine eindeutig passende KB war das kein
"ergänzen", sondern ein ungefragter Neuaufbau eines eigentlich brauchbaren
Teilbestands.

Deckt:
  (A) `_resolve_orphaned_kb_for_partial`: eindeutig namensgleiche KB + KEIN
      Preset -> liefert die KB (id+name), KEIN Netzwerk-Mutationscall.
  (B) `_resolve_orphaned_kb_for_partial`: Preset existiert schon (anderer
      'partial'-Fall, z.B. Preset ohne KB-Link) -> liefert None, der
      Caller bleibt beim bisherigen Confirm->run_setup-Pfad.
  (C) `action_install` (state=='partial', orphaned-KB gefunden) ->
      `setup_module.complete_orphaned_kb_install` wird mit der
      BESTEHENDEN kb_id aufgerufen, `run_setup` läuft NICHT,
      `_confirm_reinstall_after_partial` (der j-vorbelegte Löschzweig)
      wird NICHT erreicht.

Double-Grenze (A4, offen gelegt): `setup_module.APIClient` ist für (A)/(B)
vollständig gedoubelt (keine echten HTTP-Calls); für (C) sind
`_detect_install_state`, `_resolve_orphaned_kb_for_partial`,
`setup_module.complete_orphaned_kb_install`, `setup_module.run_setup`,
`setup_module.ensure_litellm_autowire`, `_confirm_reinstall_after_partial`
gedoubelt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import os
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n3_orphaned_kb_preserving_continuation_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


class _FakeClient:
    def __init__(self, *, preset=None, knowledge=None, healthy=True):
        self._preset = preset
        self._knowledge = knowledge or []
        self._healthy = healthy

    def check_health(self):
        return self._healthy

    def get_model(self, model_id):
        return self._preset

    def list_knowledge(self):
        return self._knowledge


_CFG = {
    "project": "Proj",
    "kb_name": "Proj Wissensspeicher",
    "variants": {"default": {"preset_id": "p1", "preset_name": "Proj"}},
    "default_variant": "default",
}


def _resolve_with_client(client, cfg=_CFG):
    with mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
         mock.patch.object(launcher_mod, "_openwebui_url", return_value="http://127.0.0.1:8080"), \
         mock.patch.object(launcher_mod, "_default_preset_id", return_value="p1"), \
         mock.patch.object(launcher_mod.setup_module, "APIClient", return_value=client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        try:
            return launcher_mod._resolve_orphaned_kb_for_partial(cfg)
        finally:
            os.environ.clear()
            os.environ.update(saved)


def test_orphaned_kb_without_preset_resolves_to_existing_kb():
    client = _FakeClient(
        preset=None,
        knowledge=[{"id": "kb-orphan-1", "name": "Proj Wissensspeicher"}],
    )
    kb = _resolve_with_client(client)
    assert kb is not None, "eindeutig namensgleiche KB ohne Preset haette aufgeloest werden muessen"
    assert kb["id"] == "kb-orphan-1", kb


def test_preset_already_exists_does_not_resolve_as_orphaned():
    """Preset existiert -> das ist ein ANDERER 'partial'-Fall (z.B. Preset
    ohne KB-Link); dafuer darf NICHT die Orphaned-KB-Ergaenzung greifen."""
    client = _FakeClient(
        preset={"id": "p1", "meta": {}},
        knowledge=[{"id": "kb-1", "name": "Proj Wissensspeicher"}],
    )
    kb = _resolve_with_client(client)
    assert kb is None, "mit vorhandenem Preset darf kein Orphaned-KB-Fall erkannt werden"


def test_no_matching_kb_resolves_to_none():
    client = _FakeClient(preset=None, knowledge=[])
    kb = _resolve_with_client(client)
    assert kb is None


def _run_action_install_partial(*, orphaned_kb):
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with mock.patch.object(launcher_mod, "_detect_install_state",
                                side_effect=["partial", "partial"]), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=orphaned_kb), \
             mock.patch.object(launcher_mod, "_confirm_reinstall_after_partial") as confirm_mock, \
             mock.patch.object(launcher_mod.setup_module, "complete_orphaned_kb_install",
                                return_value=True) as complete_mock, \
             mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
             mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock, \
             mock.patch.object(launcher_mod, "_prompt", return_value=""), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
            launcher_mod.action_install()
        return confirm_mock, complete_mock, run_setup_mock, autowire_mock
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_partial_with_orphaned_kb_completes_without_destructive_run_setup():
    kb = {"id": "kb-orphan-9", "name": "Proj Wissensspeicher"}
    confirm_mock, complete_mock, run_setup_mock, autowire_mock = _run_action_install_partial(
        orphaned_kb=kb,
    )
    assert run_setup_mock.call_count == 0, (
        "orphaned-KB-Fall darf NICHT in run_setup's destroy&recreate laufen"
    )
    assert confirm_mock.call_count == 0, (
        "der j-vorbelegte Reinstall-Confirm darf fuer den eindeutigen "
        "Orphaned-KB-Fall nicht erreicht werden -- das ist kein Loeschdefault"
    )
    assert complete_mock.call_count == 1
    assert complete_mock.call_args[0][2] == "kb-orphan-9", (
        "complete_orphaned_kb_install muss mit der BESTEHENDEN kb_id aufgerufen werden"
    )
    assert autowire_mock.call_count == 1, (
        "nach der Ergaenzung muss derselbe Connection-Schritt wie im installed-Pfad laufen"
    )


def test_partial_without_orphaned_kb_keeps_existing_confirm_path():
    """Gegenprobe: kein eindeutiger Orphaned-KB-Fall -> der bisherige,
    ausdrueckliche Confirm->run_setup-Pfad bleibt unveraendert bestehen
    (Reset ist weiterhin eine getrennte, nicht vorbelegte Wahl)."""
    confirm_mock, complete_mock, run_setup_mock, autowire_mock = _run_action_install_partial(
        orphaned_kb=None,
    )
    assert complete_mock.call_count == 0
    # Eingangscheck UND WP1d-Re-Check liefern hier beide "partial" (Mock-
    # Setup oben) -- beide treffen denselben Confirm-Prompt, der Mock bleibt
    # per Default truthy und laesst den Lauf bis zum Ende durch. Entscheidend
    # ist nur: der Confirm-Pfad wird WEITERHIN erreicht (>=1), nicht uebersprungen.
    assert confirm_mock.call_count >= 1, "ohne eindeutige KB bleibt der Confirm-Prompt der richtige Weg"


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
