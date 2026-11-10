#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n5_1b_unclear_file_list_halts_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N5 §N5-1b (N4-A3-Rest).

Vorher behandelte `complete_orphaned_kb_install` (setup.py) einen Fehler
ODER eine unerwartete (nicht-Listen-)Antwort von `client.list_files()`
identisch zu einer BESTÄTIGTEN leeren Dateiliste (`except Exception:
all_files = []`). Ein unklarer/unterbrochener Read konnte sich damit NICHT
von bestätigter Leere unterscheiden -- der Helper hätte ALLE `kb_files` als
"nicht in der KB" fehlklassifiziert und blind hochgeladen (stilles
Upload-Ableiten aus einem ungeklärten Zustand).

Deckt (direkter Aufruf von `complete_orphaned_kb_install`, Fake NUR am
äußeren API-Rand -- der Helfer selbst läuft unverändert real, s. Double-
Grenze im bestehenden `orphaned_kb_completion`-Test):
  (A) `list_files()` wirft eine Exception -> Ergänzung bricht VOR jeder
      Mutation ab (`False`, KEIN Upload, KEIN Manifest-Write) -- sichtbarer
      Befund statt stillem Upload-Ableiten.
  (B) `list_files()` liefert etwas, das KEINE Liste ist (z.B. `None`,
      simuliert einen unvollständigen/falsch geformten Read) -> derselbe
      Abbruch VOR jeder Mutation.
  (C) Gegenprobe: eine echte, lesbare LEERE Liste (bestätigt keine Dateien
      vorhanden) bleibt der normale Ergänzungsweg -- Uploads laufen wie
      bisher, kein Überreagieren auf den Fix.

Double-Grenze (A4, offen gelegt): wie im bestehenden
`orphaned_kb_completion`-Test -- ein `_FakeAPIClient` ersetzt NUR die
äußere HTTP-Schicht, `complete_orphaned_kb_install` selbst ist NICHT
gemockt und läuft mit einem echten temporären Repo. Kein Docker/
Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import traceback
import unittest.mock as mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n5_1b_unclear_file_list_halts_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


class _FakeAPIClient:
    """Fake NUR am äußeren API-Rand -- `list_files` liefert gezielt einen
    Fehler/eine falsche Form statt einer echten Dateiliste."""

    _UNSET = object()

    def __init__(self, base_url, api_key, *, list_files_raises=None, list_files_returns=_UNSET):
        self._list_files_raises = list_files_raises
        self._list_files_returns = [] if list_files_returns is self._UNSET else list_files_returns
        self.uploaded: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.unlinked: list[tuple[str, str]] = []
        self.deleted: list[str] = []
        self._next_id = 100

    def check_health(self):
        return True

    def upsert_model(self, payload):
        return True, "created"

    def list_files(self):
        if self._list_files_raises is not None:
            raise self._list_files_raises
        return self._list_files_returns

    def do_upload_file(self, filepath):
        self._next_id += 1
        new_id = f"file-new-{self._next_id}"
        self.uploaded.append(filepath.name)
        return new_id

    def add_file_to_knowledge(self, kb_id, file_id):
        self.linked.append((kb_id, file_id))
        return True

    def remove_file_from_knowledge(self, kb_id, file_id):
        self.unlinked.append((kb_id, file_id))
        return True

    def delete_file(self, file_id):
        self.deleted.append(file_id)
        return True


def _build_repo(tmp: Path) -> None:
    (tmp / "kb").mkdir()
    (tmp / "kb" / "a.md").write_text("Inhalt A", encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


_CFG = {
    "project": "Proj",
    "kb_name": "Proj Wissensspeicher",
    "masterprompt": "meta/masterprompt.md",
    "params": {},
    "suggestions": [],
    "variants": {
        "default": {
            "preset_id": "p1", "preset_name": "Proj",
            "model": "openrouter/deepseek/deepseek-v3.2", "cache": False,
        },
    },
}

_KB_ID = "kb-existing-1"


def _run(tmp: Path, client: _FakeAPIClient):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", return_value=client):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                ok = setup_mod.complete_orphaned_kb_install(tmp, _CFG, _KB_ID)
            return ok, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


def test_list_files_exception_halts_before_any_upload():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, list_files_raises=ConnectionError("boom"))
        ok, out = _run(tmp, client)
        assert ok is False, "ein Fehler bei list_files() ist KEINE bestaetigte Leere -- darf nicht True liefern"
        assert client.uploaded == [], (
            "ein unklarer Dateilisten-Read darf KEINEN Upload ausloesen (kein stilles Upload-Ableiten)"
        )
        assert not (tmp / ".openwebui-sync.json").exists(), (
            "bei einem unklaren Read darf KEIN Manifest geschrieben werden -- "
            "die Unvollstaendigkeitsmeldung bleibt sonst unwahr"
        )
        assert "nicht lesbar" in out.lower() or "unklar" in out.lower(), out


def test_list_files_non_list_result_halts_before_any_upload():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, list_files_returns=None)
        ok, out = _run(tmp, client)
        assert ok is False, "eine Nicht-Listen-Antwort ist KEINE bestaetigte Leere -- darf nicht True liefern"
        assert client.uploaded == [], (
            "ein formfalscher Dateilisten-Read darf KEINEN Upload ausloesen"
        )
        assert not (tmp / ".openwebui-sync.json").exists()
        assert "unklar" in out.lower(), out


def test_confirmed_empty_list_still_reaches_normal_upload_path():
    """Gegenprobe (C): eine echte, lesbare LEERE Liste (bestaetigt keine
    Dateien vorhanden) ist KEIN unklarer Read -- der normale Ergaenzungsweg
    bleibt moeglich, kein Ueberreagieren auf den Fix."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, list_files_returns=[])
        ok, _out = _run(tmp, client)
        assert ok is True
        assert client.uploaded == ["a.md"], "bestaetigt leere Liste darf den normalen Upload-Weg nicht blockieren"
        with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["kb_files"]["a.md"]["file_id"], "Manifest sollte die bestaetigt hochgeladene Datei enthalten"


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
