#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_orphaned_kb_not_fresh_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1d (P1c).

Vorher prüfte `scripts/launcher.py:_detect_install_state` Auth/Health/
Default-Preset/lokales Sync-Manifest, aber NICHT, ob bereits eine
gleichnamige Knowledge Base in OpenWebUI existiert. `run_setup` legt die KB
VOR dem Preset an (s. "Knowledge Base vorbereiten..."-Block) -- ein Abbruch
dazwischen (Crash, Ctrl-C, Netzfehler) hinterlässt eine KB ohne Preset/
Manifest. Ohne Preset UND ohne Manifest klassifizierte die Funktion das als
"fresh" -> der nächste `action_install`-Lauf erreichte `run_setup` OHNE
Bestätigung, das gleichnamige KBs vor der Neuanlage stillschweigend
LÖSCHT ("destroy & recreate"-Block).

Deckt:
  (A) Kein Preset, kein Manifest, ABER eine KB mit demselben `kb_name` wie
      `run_setup` sie verwenden würde -> `_detect_install_state()` liefert
      `"partial"` (NICHT `"fresh"`) -- der Caller fragt dann explizit nach
      (`_confirm_reinstall_after_partial`), statt `run_setup` blind
      aufzurufen.
  (B) Gegenprobe: wirklich nichts da (kein Preset, kein Manifest, keine
      passende KB) -> bleibt `"fresh"` (echter Erstinstall unverändert).

Double-Grenze (A4, offen gelegt): `setup_module.APIClient` ist vollständig
gedoubelt (keine echten HTTP-Calls); `load_cfg`/`_ensure_owui_env`/
`_openwebui_url` sind gedoubelt bzw. laufen gegen echte, aber lokale
Dateien (kein Netzwerk). Kein Docker/Netzwerk-Call.

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
    "f1_n2_orphaned_kb_not_fresh_launcher_under_test", _LAUNCHER_PY,
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


def _run_detect(cfg, client, *, manifest_exists=False, tmp_repo=None):
    # Manifest-Existenz ueber ein echtes (temporaeres) REPO statt globalem
    # Path.exists-Patch steuern -- so bleibt der echte Dateisystem-Zugriff
    # unangetastet und es gibt keine Rekursionsgefahr beim Patchen von
    # `Path.exists` selbst.
    with mock.patch.object(launcher_mod, "REPO", tmp_repo), \
         mock.patch.object(launcher_mod, "load_cfg", return_value=cfg), \
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


_CFG = {"project": "Proj", "kb_name": "Proj Wissensspeicher"}


def test_orphaned_kb_without_preset_or_manifest_is_partial_not_fresh():
    client = _FakeClient(
        preset=None,
        knowledge=[{"id": "kb-orphan-1", "name": "Proj Wissensspeicher"}],
    )
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(_CFG, client, tmp_repo=Path(tmp))
    assert state == "partial", (
        f"verwaiste KB ohne Preset/Manifest haette 'partial' liefern muessen (nicht 'fresh'), war {state!r}"
    )


def test_truly_nothing_there_stays_fresh():
    client = _FakeClient(preset=None, knowledge=[])
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(_CFG, client, tmp_repo=Path(tmp))
    assert state == "fresh", f"echter Erstinstall (nichts da) sollte 'fresh' bleiben, war {state!r}"


def test_unrelated_kb_with_different_name_stays_fresh():
    """Eine KB, die NICHT zu diesem Projekt gehoert (anderer Name), darf
    den Erstinstall nicht fälschlich als 'partial' blockieren."""
    client = _FakeClient(
        preset=None,
        knowledge=[{"id": "kb-other", "name": "Ein ganz anderes Projekt"}],
    )
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(_CFG, client, tmp_repo=Path(tmp))
    assert state == "fresh", f"fremde KB (anderer Name) sollte 'fresh' nicht veraendern, war {state!r}"


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
