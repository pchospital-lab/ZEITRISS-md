#!/usr/bin/env python3
"""tests/mmo_sim/test_r7_02_n2_content_confirm_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7, §03 (R7-02) NACHTRAG N2
(Flo-Direktive 2026-11-19).

Ursache (am echten OWUI-0.11.3-Backend read-only verifiziert): fuer die
ungetrackten Module meldet `list_files()` eine `meta.file_hash`, die NICHT
dem rohen SHA-256 des tatsaechlich gespeicherten Inhalts entspricht, OBWOHL
der in der aktiven KB gebundene Inhalt byte-identisch zum lokalen Kandidaten
ist. `_classify_kb_name_candidates` (Quelle: `meta.file_hash`/`hash`)
verfehlt die bereits korrekte Kopie deshalb -> Vergleichs-Upload ->
serverweite Duplicate-Kollision gegen die gleichnamigen Fremdkopien ->
falsches "fehlgeschlagen", obwohl der Inhalt bereits korrekt gebunden ist.

Fix (`run_sync` + `_confirm_active_kb_file_by_content` + `APIClient.
get_file_content`): schlaegt der Metadaten-Hashvergleich fehl, wird der
ROHE Inhalt der gleichnamigen Aktiv-KB-Kandidaten gefetcht und per SHA-256
gegen den lokalen Inhalt bestaetigt -- NUR Kandidaten in der aktiven KB,
KEIN Behandeln von "duplicate" als Erfolg, keine Fehlerunterdrueckung.

Dieser Test bildet GENAU die 0.11.3-Divergenz ab (`meta.file_hash` != roher
SHA-256) -- der bestehende `test_r7_02_kb_sync_tracked_identity_confirm`-
Double setzt beide gleich und kann den Fix daher nicht pruefen. Der Double
ersetzt NUR `APIClient._request`; `APIClient` (inkl. der neuen
`get_file_content`) UND `run_sync` laufen ECHT. Kein Docker/Netzwerk.

Flos vier Gegenfaelle: (A) Inhalt identisch, Metadatum abweichend ->
bestaetigen ohne Upload/Link; (B) Inhalt wirklich abweichend -> regulaerer
Update-Pfad; (C) identischer Inhalt NUR ausserhalb der aktiven KB -> keine
aktive Bindung abgeleitet; (D) Inhalt unlesbar -> offen, kein erfundener
Erfolg.

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
_spec = importlib.util.spec_from_file_location("r7_02_n2_setup_under_test", _SETUP_PY)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
_KB_ID = "kb-active-1"
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


class _DivergentHashDouble:
    """Wie der r7-02-Double, ABER: `meta.file_hash`/`hash` ist pro Seed frei
    waehlbar (bildet die 0.11.3-Divergenz ab), und `GET /files/{id}/content`
    liefert den rohen Inhalt. `content_unreadable`-Set erzwingt Gegenfall D."""

    def __init__(self, *, seed_files=None, kb_id=_KB_ID, preset=None, content_unreadable=None):
        self.kb_id = kb_id
        self.store: dict = {}
        self.filenames: dict = {}
        self.collection_of: dict = {}
        self.meta_hash: dict = {}
        self.linked: set = set()
        self.uploaded: list = []
        self.deleted: list = []
        self.linked_calls: list = []
        self.unlinked_calls: list = []
        self.content_fetched: list = []
        self.content_unreadable = set(content_unreadable or [])
        self._preset = preset
        self._next_id = 100
        for sf in (seed_files or []):
            fid = sf["id"]
            self.store[fid] = sf["content"]
            self.filenames[fid] = sf["filename"]
            self.collection_of[fid] = sf.get("collection_name")
            # KEY: meta.file_hash may DIVERGE from the real content sha256
            self.meta_hash[fid] = sf.get("meta_file_hash", self._hash(sf["content"]))
            if sf.get("collection_name") == kb_id:
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
            return (200, json.dumps(self._preset).encode()) if self._preset else (404, b'{"detail":"nf"}')
        if method == "GET" and path.startswith("/api/v1/files/?page="):
            page = int(path.rsplit("=", 1)[1])
            if page > 1:
                return 200, b'{"items": [], "total": 0}'
            items = [
                {"id": fid, "filename": self.filenames[fid],
                 "hash": self.meta_hash[fid],
                 "meta": {"collection_name": self.collection_of.get(fid),
                          "file_hash": self.meta_hash[fid]}}
                for fid in self.store
            ]
            return 200, json.dumps({"items": items, "total": len(items)}).encode()
        # R7-02-N2: raw content endpoint
        m = re.match(r"^/api/v1/files/([^/]+)/content$", path)
        if method == "GET" and m:
            fid = m.group(1)
            self.content_fetched.append(fid)
            if fid in self.content_unreadable or fid not in self.store:
                return 404, b'{"detail":"not found"}'
            return 200, self.store[fid]
        if method == "POST" and path == "/api/v1/files/":
            fname = _extract_upload_filename(data if isinstance(data, bytes) else b"")
            content = _extract_upload_content(data if isinstance(data, bytes) else b"", content_type)
            self._next_id += 1
            new_id = f"file-new-{self._next_id}"
            self.store[new_id] = content
            self.filenames[new_id] = fname
            self.collection_of.setdefault(new_id, None)
            self.meta_hash[new_id] = self._hash(content)
            self.uploaded.append(fname)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/add":
            file_id = (data or {}).get("file_id")
            h = self._hash(self.store.get(file_id, b""))
            colliding = [fid for fid in self.linked
                         if fid != file_id and self._hash(self.store.get(fid, b"")) == h]
            if colliding:
                return 400, b'{"detail": "400: Duplicate content detected"}'
            self.linked.add(file_id)
            self.collection_of[file_id] = self.kb_id
            self.linked_calls.append((self.kb_id, file_id))
            return 200, b"{}"
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/remove":
            file_id = (data or {}).get("file_id")
            if file_id not in self.store or file_id not in self.linked:
                return 400, b'{"detail": "nf"}'
            self.linked.discard(file_id)
            if self.collection_of.get(file_id) == self.kb_id:
                self.collection_of[file_id] = None
            self.unlinked_calls.append((self.kb_id, file_id))
            return 200, b"{}"
        if method == "DELETE" and path.startswith("/api/v1/files/"):
            file_id = path.rsplit("/", 1)[1]
            if file_id not in self.store:
                return 400, b'{"detail":"nf"}'
            del self.store[file_id]
            self.linked.discard(file_id)
            self.deleted.append(file_id)
            return 200, b"{}"
        return 200, b"{}"


_PRESET = {
    "id": "p1", "name": "Proj", "base_model_id": "openrouter/deepseek/deepseek-v3.2",
    "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
    "params": {"system": "Du bist die SL."},
}
_CFG = {
    "project": "Proj", "kb_name": "Proj Wissensspeicher", "masterprompt": "meta/masterprompt.md",
    "params": {}, "suggestions": [],
    "variants": {"default": {"preset_id": "p1", "preset_name": "Proj",
                             "model": "openrouter/deepseek/deepseek-v3.2", "cache": False}},
    "default_variant": "default",
}


def _build_repo(tmp: Path, content: str):
    (tmp / "kb").mkdir()
    (tmp / "kb" / "a.md").write_text(content, encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


def _run_sync(tmp: Path, http):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        holder = {}

        def _factory(base_url, api_key):
            c = _RealAPIClient(base_url, api_key)
            c._request = http.request
            holder["client"] = c
            return c
        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", side_effect=_factory):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                try:
                    setup_mod.run_sync(tmp, _CFG, {"no_verify": True, "assume_yes": True})
                    ok = True
                except SystemExit as exc:
                    ok = exc.code in (0, None)
            return ok, buf.getvalue(), holder.get("client")
    finally:
        os.environ.clear(); os.environ.update(saved)


_LOCAL = "ZEITRISS Modul: aktueller Inhalt Zeile 1\nZeile 2\n"
_LOCAL_SHA = hashlib.sha256(_LOCAL.encode()).hexdigest()


def _foreign_copies(content_bytes):
    """5 gleichnamige Fremdkopien (collectionfremd), wie real beobachtet."""
    return [
        {"id": f"foreign-{i}", "filename": "a.md", "content": content_bytes,
         "collection_name": f"other-kb-{i}", "meta_file_hash": "FOREIGNHASH%d" % i}
        for i in range(5)
    ]


def test_A_identical_content_divergent_metadata_confirmed_without_reupload():
    """Gegenfall A (Kern): aktive-KB-Kopie hat byte-identischen Inhalt, aber
    `meta.file_hash` weicht ab -> content-gebunden bestaetigt, KEIN Upload,
    KEIN Link-Versuch."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td); _build_repo(tmp, _LOCAL)
        seeds = [{"id": "active-stale-meta", "filename": "a.md", "content": _LOCAL.encode(),
                  "collection_name": _KB_ID, "meta_file_hash": "DIVERGENT-NOT-THE-REAL-SHA256"}]
        seeds += _foreign_copies(_LOCAL.encode())
        http = _DivergentHashDouble(seed_files=seeds, preset=_PRESET)
        ok, out, _ = _run_sync(tmp, http)
        assert ok, out
        assert http.uploaded == [], f"es darf KEIN Re-Upload passieren: {http.uploaded}"
        assert http.linked_calls == [], f"kein neuer Link-Versuch: {http.linked_calls}"
        assert "active-stale-meta" in http.content_fetched, "content-Bestaetigung muss gefetcht haben"
        man = json.loads((tmp / ".openwebui-sync.json").read_text())
        assert man["kb_files"]["a.md"]["file_id"] == "active-stale-meta", man


def test_B_actually_different_content_takes_regular_update_path():
    """Gegenfall B: aktive-KB-Inhalt ist WIRKLICH anders -> kein falsches
    'aktuell', regulaerer Upload-/Aktualisierungspfad."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td); _build_repo(tmp, _LOCAL)
        seeds = [{"id": "active-old", "filename": "a.md", "content": b"VERALTETER anderer Inhalt\n",
                  "collection_name": _KB_ID, "meta_file_hash": "DIVERGENT-OLD"}]
        http = _DivergentHashDouble(seed_files=seeds, preset=_PRESET)
        ok, out, _ = _run_sync(tmp, http)
        assert ok, out
        assert http.uploaded == ["a.md"], f"verschiedener Inhalt muss hochgeladen werden: {http.uploaded}"


def test_C_identical_content_only_outside_active_kb_no_active_binding():
    """Gegenfall C: identischer Inhalt existiert NUR in fremden Collections,
    NICHT in der aktiven KB -> daraus wird KEINE aktive Bindung abgeleitet
    (regulaerer Upload in die aktive KB)."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td); _build_repo(tmp, _LOCAL)
        seeds = _foreign_copies(_LOCAL.encode())  # only foreign, none in our KB
        http = _DivergentHashDouble(seed_files=seeds, preset=_PRESET)
        ok, out, _ = _run_sync(tmp, http)
        assert ok, out
        assert http.uploaded == ["a.md"], f"fremde Kopie darf keine aktive Bindung vortaeuschen: {http.uploaded}"
        # keine fremde Kopie wurde als Kandidat inhaltlich gefetcht (same_name-Filter greift vorher)
        assert all(not fid.startswith("foreign-") for fid in http.content_fetched), http.content_fetched


def test_D_unreadable_content_is_left_open_no_invented_success():
    """Gegenfall D: aktive-KB-Kopie mit divergentem Metadatum, aber Inhalt
    NICHT lesbar -> KEINE Bestaetigung erfunden, regulaerer Pfad."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td); _build_repo(tmp, _LOCAL)
        seeds = [{"id": "active-unreadable", "filename": "a.md", "content": _LOCAL.encode(),
                  "collection_name": _KB_ID, "meta_file_hash": "DIVERGENT-X"}]
        http = _DivergentHashDouble(seed_files=seeds, preset=_PRESET,
                                    content_unreadable={"active-unreadable"})
        ok, out, _ = _run_sync(tmp, http)
        # Unlesbarer Inhalt -> KEINE content-Bestaetigung -> der Fix erfindet
        # keinen Erfolg. Er faellt in den regulaeren Pfad, der hier ehrlich
        # scheitert: der Inhalt IST vorhanden (aktive-KB-Kopie), aber
        # unbestaetigbar -> Vergleichs-Upload kollidiert -> ehrliches
        # "Unklar/fehlgeschlagen", a.md wird NICHT faelschlich als gebunden
        # markiert. Genau das ist Gegenfall D ("offen gelassen").
        assert "active-unreadable" in http.content_fetched, "muss den Leseversuch gemacht haben"
        assert http.uploaded == ["a.md"], f"regulaerer Pfad versucht: {http.uploaded}"
        man_path = tmp / ".openwebui-sync.json"
        man = json.loads(man_path.read_text()) if man_path.exists() else {}
        assert "a.md" not in (man.get("kb_files") or {}), (
            f"kein erfundener Erfolg -> a.md darf NICHT als bestaetigt im Manifest stehen: {man}"
        )
        assert ("Unklar" in out or "fehlgeschlagen" in out or "nicht verkn" in out), (
            "ehrliche Fehlermeldung erwartet (kein stilles 'ok')"
        )


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn(); print(f"OK   {fn.__name__}"); passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}"); traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}"); traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
