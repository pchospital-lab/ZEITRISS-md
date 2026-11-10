#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n4_orphaned_kb_completion_2026_11_10.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N4 §N4-1 P2 (A2+A3).

Vorher ergänzte `complete_orphaned_kb_install` (setup.py) keine fehlenden
Wissensdateien und keine fehlenden KB-Verknüpfungen -- es schrieb nur ein
Näherungs-Manifest: MD5 ALLER lokalen Wissensdateien, `file_id` aus einem
GLOBALEN `list_files()`-Namensmatch (kein Beleg für Zugehörigkeit zu DIESER
KB) oder leer, ausdrücklich "ohne Re-Upload". Der Generalurteil-Befund
bemängelte explizit, dass der bisherige Orphaned-Test den Ergänzungshelfer
komplett mockte und seine tatsächliche Vervollständigung nie bewies.

Deckt (direkter Aufruf von `complete_orphaned_kb_install`, Fake NUR am
äußeren API-Rand -- der Helfer selbst läuft unverändert real):
  (A) Eine Datei ist bereits NACHWEISLICH in DIESER KB (meta.collection_name
      == kb_id) -> kein Re-Upload, Manifest übernimmt die bestehende file_id.
  (B) Eine gleichnamige Datei existiert global, aber nur in einer ANDEREN KB
      -> KEIN Namensmatch als Zugehörigkeitsbeweis; die Datei wird für DIESE
      KB tatsächlich hochgeladen (`do_upload_file`) und verlinkt
      (`add_file_to_knowledge`).
  (C) Eine Datei existiert nirgendwo -> wird tatsächlich hochgeladen+verlinkt.
  (D) Ein Upload schlägt fehl -> Datei NICHT im Manifest, `all_ok=False`,
      Rückgabe spiegelt den unvollständigen Stand (kein falsches "synchron").
  (E) Ein Upload gelingt, aber der KB-Link schlägt fehl (auch nach Retry) ->
      verwaiste File-Entity wird aufgeräumt (`delete_file`), Datei NICHT im
      Manifest, `all_ok=False`.

Double-Grenze (A4, offen gelegt): ein `_FakeAPIClient` ersetzt NUR die
äußere HTTP-Schicht (check_health/upsert_model/list_files/do_upload_file/
add_file_to_knowledge/delete_file) -- `complete_orphaned_kb_install` selbst
ist NICHT gemockt und läuft mit einem echten temporären Repo (echte
`discover_knowledge_files`/`_file_md5`/`_save_sync_manifest`-Aufrufe gegen
echte Dateien). `setup_module.APIClient`-Konstruktor ist umgeleitet,
`_auto_load_owui_env` ist gedoubelt (kein Zugriff auf ~/.openwebui_env).
Kein Docker/Netzwerk-Call.

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
    "f1_n4_orphaned_kb_completion_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


class _FakeAPIClient:
    """Fake NUR am äußeren API-Rand (kein echter HTTP-Call) -- simuliert
    eine OpenWebUI-Instanz mit einem bestehenden globalen Datei-Bestand
    (manche Dateien gehören zu einer ANDEREN KB, s. Doku oben)."""

    def __init__(self, base_url, api_key, *, existing_files=None,
                 upload_fails_for=(), link_fails_for=()):
        self._existing_files = list(existing_files or [])
        self._upload_fails_for = set(upload_fails_for)
        self._link_fails_for = set(link_fails_for)
        self.uploaded: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.deleted: list[str] = []
        self._next_id = 100

    def check_health(self):
        return True

    def upsert_model(self, payload):
        return True, "created"

    def list_files(self):
        return list(self._existing_files)

    def do_upload_file(self, filepath):
        if filepath.name in self._upload_fails_for:
            return None
        self._next_id += 1
        new_id = f"file-new-{self._next_id}"
        self.uploaded.append(filepath.name)
        self._existing_files.append({
            "filename": filepath.name, "id": new_id, "meta": {},
        })
        return new_id

    def add_file_to_knowledge(self, kb_id, file_id):
        self.linked.append((kb_id, file_id))
        for f in self._existing_files:
            if f.get("id") == file_id and f["filename"] in self._link_fails_for:
                return False
        if file_id.startswith("file-new-"):
            for f in self._existing_files:
                if f.get("id") == file_id:
                    f["meta"] = {"collection_name": kb_id}
        return True

    def delete_file(self, file_id):
        self.deleted.append(file_id)
        self._existing_files = [f for f in self._existing_files if f.get("id") != file_id]
        return True


def _build_repo(tmp: Path) -> None:
    (tmp / "kb").mkdir()
    (tmp / "kb" / "a.md").write_text("Inhalt A", encoding="utf-8")
    (tmp / "kb" / "b.md").write_text("Inhalt B", encoding="utf-8")
    (tmp / "kb" / "c.md").write_text("Inhalt C", encoding="utf-8")
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


def _manifest(tmp: Path) -> dict:
    with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
        return json.load(f)


def test_already_in_kb_file_is_not_reuploaded():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, existing_files=[
            {"filename": "a.md", "id": "file-a-in-kb", "meta": {"collection_name": _KB_ID}},
        ])
        ok, _out = _run(tmp, client)
        assert ok is True
        assert "a.md" not in client.uploaded, "bereits verlinkte Datei darf NICHT neu hochgeladen werden"
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-in-kb"


def test_same_filename_in_other_kb_is_not_treated_as_member_and_gets_uploaded():
    """A2: ein globaler Namensmatch (Datei gehoert zu einer ANDEREN KB)
    ist KEIN Zugehoerigkeitsbeweis fuer DIESE KB -- die Datei muss echt
    hochgeladen+verlinkt werden."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, existing_files=[
            {"filename": "b.md", "id": "file-b-other-kb", "meta": {"collection_name": "some-other-kb"}},
        ])
        ok, _out = _run(tmp, client)
        assert ok is True
        assert "b.md" in client.uploaded, (
            "Datei mit gleichem Namen in EINER ANDEREN KB haette als fehlend "
            "in DIESER KB erkannt und tatsaechlich hochgeladen werden muessen"
        )
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["b.md"]["file_id"] != "file-b-other-kb", (
            "Manifest darf NICHT die File-ID der anderen KB uebernehmen (kein globaler Namensmatch)"
        )
        assert any(kb_id == _KB_ID for kb_id, _fid in client.linked), "neue Datei muss an DIESE kb_id verlinkt werden"


def test_missing_file_is_actually_uploaded_and_linked():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, existing_files=[])
        ok, _out = _run(tmp, client)
        assert ok is True
        assert set(client.uploaded) == {"a.md", "b.md", "c.md"}
        manifest = _manifest(tmp)
        for name in ("a.md", "b.md", "c.md"):
            assert manifest["kb_files"][name]["file_id"], f"{name} sollte eine echte file_id im Manifest haben"


def test_failed_upload_is_not_recorded_as_synced():
    """A3: ein fehlgeschlagener Upload darf NICHT als synchron verbucht
    werden -- Fehler sichtbar, all_ok=False, Manifest ohne diese Datei."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, existing_files=[], upload_fails_for={"c.md"})
        ok, out = _run(tmp, client)
        assert ok is False, "fehlgeschlagener Upload darf NICHT als vollstaendig/synchron gelten"
        assert "c.md" not in client.uploaded
        manifest = _manifest(tmp)
        assert "c.md" not in manifest["kb_files"], (
            "Manifest darf die fehlgeschlagene Datei NICHT als bestaetigt zugeordnet ausweisen"
        )
        assert "a.md" in manifest["kb_files"] and "b.md" in manifest["kb_files"], (
            "andere, erfolgreich ergaenzte Dateien bleiben im Manifest (teilweiser, ehrlicher Fortschritt)"
        )
        assert "fehlgeschlagen" in out.lower() or "nicht ergänzt" in out.lower(), out


def test_failed_link_after_successful_upload_cleans_up_and_is_not_synced():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        client = _FakeAPIClient(None, None, existing_files=[], link_fails_for={"c.md"})
        ok, _out = _run(tmp, client)
        assert ok is False
        assert "c.md" in client.uploaded, "Upload lief, nur der Link schlug fehl"
        assert len(client.deleted) >= 1, "verwaiste File-Entity nach fehlgeschlagenem Link sollte aufgeraeumt werden"
        manifest = _manifest(tmp)
        assert "c.md" not in manifest["kb_files"]


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
