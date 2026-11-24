#!/usr/bin/env python3
"""tests/mmo_sim/test_r7_02_kb_sync_tracked_identity_confirm_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7, §03 (R7-02).

Ursache (verifiziert am echten Backend-Lese-Code, `scripts/setup.py:run_sync`
changed-Schleife, ~Zeile 4518-4560, VOR diesem Fix): fuer eine Datei MIT
bereits getracktem `old_file_id` (`files_manifest[name]["file_id"]`) prüfte
der Code NIE, ob dieser getrackte Altbestand am BACKEND bereits den
aktuellen lokalen Inhalt trägt -- er ging IMMER direkt in den blinden
Re-Upload-Pfad. Der NAMENSFALLBACK (fehlender Manifest-Eintrag, `else`-
Zweig direkt daneben, WP-F1-N8 R2) hatte GENAU diesen identitätsgebundenen
Hash-Check (`_classify_kb_name_candidates`) bereits -- nur der getrackte
Zweig nicht.

Das erklärt die reale r6-Launcher-Beobachtung (7 unbestätigte Dateien,
"HTTP 400 Duplicate-Content"): ist die lokale Manifest-MD5 stale (z.B. weil
der getrackte Altbestand zwischenzeitlich AM BACKEND bereits den aktuellen
Inhalt trägt -- etwa durch einen manuellen Fix am Backend oder einen
früheren, teilweise unpersistierten Lauf), während die lokale Datei selbst
unverändert ist, erkennt der alte Code das NICHT: er lädt den (bereits
vorhandenen) Inhalt ERNEUT hoch und versucht ihn zu verlinken. OpenWebUIs
tatsächliche Backend-Semantik (retrieval.py:1666-1685, collection-weiter
Content-Hash-Duplicate-Check, von `_ContentHttpDouble` hier nachgebildet --
in den bestehenden Nachbar-Tests `test_f1_n5_1b_unclear_file_list_halts_
2026_11_10.py` bereits gegen das echte v0.11.3-Backend verifiziert) weist
diesen Vergleichs-Upload dann als "400 Duplicate content detected" zurück,
OHNE dass der getrackte Altbestand je als bereits korrekt bestätigt wird --
die Datei bleibt dauerhaft unbestätigt ("0/7"), obwohl sie am Backend
bereits korrekt gebunden ist.

Kleinster kausaler Fix (scripts/setup.py, `run_sync`): BEVOR der getrackte
`old_file_id`-Zweig blind re-uploaded, denselben Content-Hash-Vergleich wie
im Namensfallback ausführen (ECHTER Backend-Read: `client.list_files()`,
`meta.file_hash`/`hash`, am laufenden Backend verifizierte Felder, s.
Nachbar-Tests) -- trägt der getrackte Altbestand bereits den lokalen
Inhalt, wird GENAU der bestehende `target_fid`-Zweig (idempotenter
Abgleich, KEIN Upload) genutzt, unverändert wie im Namensfallback-Fall.

Double-Grenze (identisch zu `test_f1_n5_1b_unclear_file_list_halts_
2026_11_10.py`, NUR dort erneut dupliziert statt importiert -- bestehende
Testkonvention dieser Suite, reiner Testcode): `_ContentHttpDouble` ersetzt
NUR `APIClient._request`; `APIClient` selbst (`list_files`, `do_upload_
file`, `add_file_to_knowledge`, `remove_file_from_knowledge`, `delete_
file`) UND `run_sync` laufen ECHT. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import re
import tempfile
import traceback
import unittest.mock as mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "r7_02_kb_sync_tracked_identity_confirm_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)

_KB_ID = "kb-existing-1"
_RealAPIClient = setup_mod.APIClient


def _extract_upload_filename(body: bytes) -> str:
    m = re.search(rb'filename="([^"]+)"', body or b"")
    return m.group(1).decode("utf-8") if m else ""


def _extract_upload_content(body: bytes, content_type: str) -> bytes:
    m = re.search(r"boundary=([^\s;]+)", content_type or "")
    if not m:
        return b""
    marker = b"--" + m.group(1).encode()
    parts = (body or b"").split(marker)
    if len(parts) < 2:
        return b""
    idx = parts[1].find(b"\r\n\r\n")
    if idx == -1:
        return b""
    content = parts[1][idx + 4:]
    return content[:-2] if content.endswith(b"\r\n") else content


class _ContentHttpDouble:
    """Dieselbe inhaltsbasierte OWUI-Backendsemantik-Nachbildung wie in
    `test_f1_n5_1b_unclear_file_list_halts_2026_11_10.py` (dort gegen das
    echte v0.11.3-Backend verifiziert) -- hier NUR erneut dupliziert
    (bestehende Testkonvention, reiner Testcode, kein Produktimport)."""

    def __init__(self, *, seed_files=None, kb_id=_KB_ID, preset=None):
        self.kb_id = kb_id
        self.store: dict = {}
        self.filenames: dict = {}
        self.collection_of: dict = {}
        self.linked: set = set()
        self.uploaded: list = []
        self.deleted: list = []
        self.linked_calls: list = []
        self.unlinked_calls: list = []
        self._preset = preset
        self._next_id = 100
        for sf in (seed_files or []):
            fid = sf["id"]
            self.store[fid] = sf["content"]
            self.filenames[fid] = sf["filename"]
            coll = sf.get("collection_name")
            self.collection_of[fid] = coll
            if coll == kb_id:
                self.linked.add(fid)

    @staticmethod
    def _hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def request(self, method, path, data=None, content_type="application/json", timeout=None):
        if method == "GET" and path == "/api/config":
            return 200, b"{}"
        if method == "GET" and path == "/api/models":
            return 200, b'{"data": []}'
        if method == "GET" and path.startswith("/api/v1/models/model?id="):
            if self._preset is not None:
                return 200, json.dumps(self._preset).encode()
            return 404, b'{"detail": "not found"}'
        if method == "GET" and path.startswith("/api/v1/files/?page="):
            page = int(path.rsplit("=", 1)[1])
            if page > 1:
                return 200, b'{"items": [], "total": 0}'
            items = [
                {"id": fid, "filename": self.filenames[fid],
                 "hash": self._hash(self.store[fid]),
                 "meta": {"collection_name": self.collection_of.get(fid),
                          "file_hash": self._hash(self.store[fid])}}
                for fid in self.store
            ]
            return 200, json.dumps({"items": items, "total": len(items)}).encode()
        if method == "POST" and path == "/api/v1/files/":
            fname = _extract_upload_filename(data if isinstance(data, bytes) else b"")
            content = _extract_upload_content(data if isinstance(data, bytes) else b"", content_type)
            self._next_id += 1
            new_id = f"file-new-{self._next_id}"
            self.store[new_id] = content
            self.filenames[new_id] = fname
            self.collection_of.setdefault(new_id, None)
            self.uploaded.append(fname)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/add":
            file_id = (data or {}).get("file_id")
            content = self.store.get(file_id, b"")
            h = self._hash(content)
            colliding = [
                fid for fid in self.linked
                if fid != file_id and self._hash(self.store.get(fid, b"")) == h
            ]
            if colliding:
                return 400, b'{"detail": "400: Duplicate content detected"}'
            self.linked.add(file_id)
            self.collection_of[file_id] = self.kb_id
            self.linked_calls.append((self.kb_id, file_id))
            return 200, b"{}"
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/remove":
            file_id = (data or {}).get("file_id")
            if file_id not in self.store or file_id not in self.linked:
                return 400, b'{"detail": "400: NOT_FOUND"}'
            self.linked.discard(file_id)
            if self.collection_of.get(file_id) == self.kb_id:
                self.collection_of[file_id] = None
            self.unlinked_calls.append((self.kb_id, file_id))
            return 200, b"{}"
        # UPD-1: `wait_for_file_ready` fragt vor jedem Link-Versuch GENAU
        # diesen Endpunkt ab -- bereits im `store` liegender Inhalt gilt
        # sofort als fertig extrahiert (dieser Double modelliert keine
        # Verarbeitungsverzögerung, nicht sein Testgegenstand).
        if method == "GET" and path.startswith("/api/v1/files/") and "?" not in path and path != "/api/v1/files/":
            file_id = path.rsplit("/", 1)[-1]
            if file_id in self.store:
                return 200, json.dumps({"id": file_id, "data": {"content": "ready"}}).encode()
            return 404, b'{"detail": "not found"}'
        if method == "DELETE" and path.startswith("/api/v1/files/"):
            file_id = path.rsplit("/", 1)[1]
            if file_id not in self.store:
                return 400, b'{"detail": "Not found"}'
            del self.store[file_id]
            self.linked.discard(file_id)
            self.filenames.pop(file_id, None)
            self.collection_of.pop(file_id, None)
            self.deleted.append(file_id)
            return 200, b"{}"
        return 200, b"{}"


def _build_repo(tmp: Path, *, filenames=("a.md",), content="Inhalt 0") -> None:
    (tmp / "kb").mkdir()
    for name in filenames:
        (tmp / "kb" / name).write_text(content, encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


_N8_PRESET = {
    "id": "p1", "name": "Proj",
    "base_model_id": "openrouter/deepseek/deepseek-v3.2",
    "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
    "params": {"system": "Du bist die SL."},
}

_SYNC_CFG = {
    "project": "Proj", "kb_name": "Proj Wissensspeicher", "masterprompt": "meta/masterprompt.md",
    "params": {}, "suggestions": [],
    "variants": {
        "default": {"preset_id": "p1", "preset_name": "Proj",
                    "model": "openrouter/deepseek/deepseek-v3.2", "cache": False},
    },
    "default_variant": "default",
}


def _run_sync(tmp: Path, http):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        real_client_holder = {}

        def _client_factory(base_url, api_key):
            client = _RealAPIClient(base_url, api_key)
            client._request = http.request
            real_client_holder["client"] = client
            return client

        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", side_effect=_client_factory):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                try:
                    setup_mod.run_sync(tmp, _SYNC_CFG, {"no_verify": True, "assume_yes": True})
                    ok = True
                except SystemExit as exc:
                    ok = exc.code in (0, None)
            return ok, buf.getvalue(), real_client_holder.get("client")
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _write_manifest(tmp: Path, manifest: dict) -> None:
    (tmp / ".openwebui-sync.json").write_text(json.dumps(manifest), encoding="utf-8")


def _manifest(tmp: Path) -> dict:
    with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
        return json.load(f)


def test_tracked_old_file_id_already_matching_backend_content_is_confirmed_without_reupload():
    """Kernbeleg des R7-02-Fixes: `old_file_id` ist getrackt (Manifest-
    Eintrag existiert), seine MD5 ist aber STALE (repraesentiert einen
    FRUEHEREN lokalen Inhalt) -- das Backend selbst traegt unter GENAU
    diesem `old_file_id` bereits den AKTUELLEN lokalen Inhalt (z.B. durch
    einen frueheren, teilweise unpersistierten Lauf oder einen manuellen
    Fix am Backend). VOR dem Fix: blinder Re-Upload -> OWUIs collection-
    weiter Duplicate-Check weist den Vergleichs-Upload gegen GENAU diesen
    `old_file_id` zurueck -> dauerhaft unbestaetigt, obwohl der Inhalt am
    Backend bereits korrekt gebunden ist (die reale "0/7"-Ursache). NACH
    dem Fix: identitaetsgebundener Hash-Abgleich erkennt `old_file_id` als
    bereits korrekt -- KEIN Re-Upload, sofort bestaetigt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",), content="AKTUELLER-INHALT")
        http = _ContentHttpDouble(
            seed_files=[
                {"id": "file-a-tracked", "filename": "a.md", "content": b"AKTUELLER-INHALT",
                 "collection_name": _KB_ID},
            ],
            kb_id=_KB_ID, preset=_N8_PRESET,
        )
        # Manifest traegt eine STALE MD5 (repraesentiert einen frueheren
        # lokalen Inhalt "ALTER-INHALT") MIT dem getrackten `file_id` --
        # genau der Zustand, der `run_sync`s MD5-Vergleich a.md als
        # "geaendert" einordnen laesst, OBWOHL das Backend unter
        # `old_file_id` bereits den AKTUELLEN Inhalt traegt.
        _write_manifest(tmp, {
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {"a.md": {"md5": hashlib.md5(b"ALTER-INHALT").hexdigest(), "file_id": "file-a-tracked"}},
            "last_sync": "2026-11-18T00:00:00",
        })

        ok, out, _client = _run_sync(tmp, http)

        assert ok is True, (
            f"ein getrackter Altbestand, der am Backend bereits den aktuellen Inhalt traegt, "
            f"muss OHNE Re-Upload bestaetigt abschliessen: {out}"
        )
        assert http.uploaded == [], (
            f"KEIN Vergleichs-Upload, wenn der getrackte old_file_id bereits identitaetsgebunden "
            f"den lokalen Inhalt traegt (das war GENAU der fehlende Check -- R7-02): {http.uploaded}"
        )
        assert "file-a-tracked" in http.store and "file-a-tracked" in http.linked, (
            "der bestaetigte getrackte Altbestand bleibt unveraendert verlinkt"
        )
        assert "file-a-tracked" not in http.deleted, "die korrekte eigene Datei wird NICHT geloescht"
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-tracked"
        assert manifest["kb_files"]["a.md"]["md5"] == hashlib.md5(b"AKTUELLER-INHALT").hexdigest(), (
            "die Manifest-MD5 muss jetzt den tatsaechlichen (zuvor stale) lokalen Inhalt korrekt tragen"
        )


def test_tracked_old_file_id_with_real_content_difference_still_gets_replaced():
    """Gegenprobe (Regressionsschutz): unterscheidet sich der getrackte
    Altbestand WIRKLICH vom lokalen Inhalt, bleibt der bestehende Ersatzweg
    (Upload + Link + Altentfernung) UNVERAENDERT aktiv -- der neue Check
    darf einen echten Aenderungsfall NICHT faelschlich als 'schon korrekt'
    lesen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",), content="NEU-INHALT")
        http = _ContentHttpDouble(
            seed_files=[
                {"id": "file-a-old", "filename": "a.md", "content": b"ALTER-INHALT",
                 "collection_name": _KB_ID},
            ],
            kb_id=_KB_ID, preset=_N8_PRESET,
        )
        _write_manifest(tmp, {
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {"a.md": {"md5": hashlib.md5(b"ALTER-INHALT").hexdigest(), "file_id": "file-a-old"}},
            "last_sync": "2026-11-18T00:00:00",
        })

        ok, out, _client = _run_sync(tmp, http)

        assert ok is True, out
        assert http.uploaded == ["a.md"], (
            "ein ECHT abweichender getrackter Altbestand muss weiterhin normal ersetzt (hochgeladen) "
            f"werden: {http.uploaded}"
        )
        assert "file-a-old" not in http.store, "der echte Altbestand wird nach bestaetigtem Ersatz entfernt"
        manifest = _manifest(tmp)
        new_id = manifest["kb_files"]["a.md"]["file_id"]
        assert new_id != "file-a-old" and new_id in http.linked
        assert manifest["kb_files"]["a.md"]["md5"] == hashlib.md5(b"NEU-INHALT").hexdigest()


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
