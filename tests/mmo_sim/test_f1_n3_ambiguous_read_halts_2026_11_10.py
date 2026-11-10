#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n3_ambiguous_read_halts_2026_11_10.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N3 §N3-1c.

Vorher kollabierten `APIClient.get_model`/`list_knowledge` JEDEN
Nicht-Erfolg (401/500/0/unlesbarer Body) auf None/[] -- identisch zu einem
bestätigten "Preset/KB existiert nicht". `_detect_install_state` konnte
einen vorübergehend unlesbaren Bestand (z.B. OWUI mitten im Hochfahren,
Token noch nicht propagiert) damit nicht von einer echten Leere
unterscheiden und lief in "fresh"/falsches "partial" -- der nächste
`action_install`-Lauf hätte `run_setup` erreicht und einen funktionierenden
Bestand überschrieben.

Deckt:
  (A) `get_model` liefert `None` wegen HTTP 500 (nicht 404) ->
      `_detect_install_state` liefert `"unreachable"`, NICHT `"fresh"`
      oder `"partial"`.
  (B) `list_knowledge` liefert `[]` wegen HTTP 0 (Netzwerkfehler) ->
      ebenfalls `"unreachable"`.
  (C) Gegenprobe: `get_model` liefert `None` wegen HTTP 404 (ECHTE
      Abwesenheit, Standardfall für ein frisches Preset) -> bleibt
      `"fresh"`/`"partial"` wie bisher, KEINE Regression für den
      normalen Erstinstall-Weg.

Double-Grenze (A4, offen gelegt): ein minimaler `APIClient`-Double, der
NUR `check_health`/`get_model`/`list_knowledge` plus die beiden neuen
Status-Attribute (`last_model_status`/`last_knowledge_status`) nachbildet
-- kein echter HTTP-Client, kein `_request`. `load_cfg`/`_ensure_owui_env`/
`_openwebui_url` sind gedoubelt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import os
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n3_ambiguous_read_halts_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


class _StatusAwareFakeClient:
    """Double mit genau den Attributen, die die echte `APIClient` seit
    WP-N3-1c zusätzlich setzt -- simuliert einen bestimmten HTTP-Status
    OHNE echten Request."""

    def __init__(self, *, preset=None, knowledge=None, healthy=True,
                 model_status=200, knowledge_status=200):
        self._preset = preset
        self._knowledge = knowledge or []
        self._healthy = healthy
        self.last_model_status = None
        self.last_knowledge_status = None
        self._model_status = model_status
        self._knowledge_status = knowledge_status

    def check_health(self):
        return self._healthy

    def get_model(self, model_id):
        self.last_model_status = self._model_status
        return self._preset

    def list_knowledge(self):
        self.last_knowledge_status = self._knowledge_status
        return self._knowledge


_CFG = {"project": "Proj", "kb_name": "Proj Wissensspeicher"}


def _run_detect(client, *, tmp_repo):
    with mock.patch.object(launcher_mod, "REPO", tmp_repo), \
         mock.patch.object(launcher_mod, "load_cfg", return_value=_CFG), \
         mock.patch.object(launcher_mod, "_default_preset_id", return_value="p1"), \
         mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
         mock.patch.object(launcher_mod, "_openwebui_url", return_value="http://127.0.0.1:8080"), \
         mock.patch.object(launcher_mod.setup_module, "APIClient", return_value=client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        try:
            return launcher_mod._detect_install_state()
        finally:
            os.environ.clear()
            os.environ.update(saved)


def test_get_model_http_500_is_unreachable_not_fresh():
    client = _StatusAwareFakeClient(preset=None, knowledge=[], model_status=500)
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", (
        f"ein HTTP-500 auf get_model ist KEIN bestaetigtes 'Preset fehlt' -- war {state!r}"
    )


def test_list_knowledge_network_error_is_unreachable_not_fresh():
    client = _StatusAwareFakeClient(preset=None, knowledge=[], model_status=404, knowledge_status=0)
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", (
        f"HTTP-Status 0 (Netzwerkfehler) auf list_knowledge ist KEIN bestaetigtes "
        f"'keine KB da' -- war {state!r}"
    )


def test_get_model_http_401_is_unreachable_not_fresh():
    """Ein Auth-Fehler auf dem zustandsentscheidenden Read ist genauso
    unklar wie ein 500er -- nicht nur Server-Fehler zaehlen."""
    client = _StatusAwareFakeClient(preset=None, knowledge=[], model_status=401)
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", f"war {state!r}"


def test_get_model_http_404_stays_fresh_no_regression():
    """Gegenprobe: eine ECHTE 404 (Standardfall fuer ein frisches Preset,
    das es noch nie gab) darf NICHT als 'unreachable' durchgehen --
    sonst waere JEDER normale Erstinstall betroffen."""
    client = _StatusAwareFakeClient(preset=None, knowledge=[], model_status=404, knowledge_status=200)
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "fresh", f"echte 404 (nichts da) muss weiterhin 'fresh' bleiben, war {state!r}"


def test_double_without_status_attrs_is_unaffected_backward_compat():
    """Ein ALTER Double ohne die neuen Status-Attribute (z.B. bestehende
    Tests mit handgerolltem FakeClient) darf durch WP-N3-1c NICHT brechen
    -- `getattr(..., 200)` faellt auf das alte Verhalten zurueck."""
    class _OldStyleFakeClient:
        def check_health(self):
            return True

        def get_model(self, model_id):
            return None

        def list_knowledge(self):
            return []

    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(_OldStyleFakeClient(), tmp_repo=Path(tmp))
    assert state == "fresh", f"alter Double ohne Status-Attribute muss weiterhin 'fresh' liefern, war {state!r}"


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
