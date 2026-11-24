#!/usr/bin/env python3
"""tests/mmo_sim/test_r8_01_tracked_active_kb_binding_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R8, §3 (R8-01).

Ursache (aus dem Quelltext belegt, VOR diesem Fix): in `run_sync`s
`if old_file_id:`-Zweig wurde `old_entry` NUR per ID aus `client.list_files()`
gesucht -- ohne Pruefung auf erwarteten Dateinamen UND aktive KB-Zugehoerigkeit
(`meta.collection_name == kb_id`). Ein getrackter `old_file_id`, der tatsaech-
lich einer FREMDEN Datei (gleicher Name, andere/keine KB) gehoert, konnte
dadurch ueber BEIDE Bestaetigungswege (Metadaten-Hash-Treffer ODER
`_confirm_active_kb_file_by_content`) faelschlich als "aktuell" durchgehen,
obwohl die aktive KB weiterhin nur eine veraltete gleichnamige Kopie trug.
Der anschliessende `_run_coverage_check` prueft nur den Dateinamen in der
aktiven KB (nicht deren Inhalt) und meldete dadurch faelschlich gruen.

Fix (`run_sync`, `if old_file_id:`-Zweig): ein getrackter `old_file_id` darf
die beiden Bestaetigungspfade nur betreten, wenn er nachweislich unter
`fp.name` zur AKTIVEN KB gehoert (`tracked_active`, geprueft gegen den
bereits gebauten `kb_name_index`, selbst bereits auf
`collection_name == kb_id` gefiltert -- kein zusaetzlicher `list_files()`-
Aufruf). Fehlt diese Bindung, faellt der Fall in den bestehenden Namens-
fallback (`else`-Zweig) -- die fremde ID landet dort NICHT in
`old_candidates` und wird folglich weder bestaetigt noch entlinkt/geloescht.

Fixtur (wie in `03_GEGENFALL_UND_ABNAHME.md` / `kb-binding-countercase.json`):
aktive KB = `kb_id`; lokale `a.md` = Inhalt N; Sync-Manifest trackt
`file_id = F` mit STALE md5 (!= aktueller lokaler Inhalt -> "geaendert").
F liegt in einer FREMDEN KB (`collection_name = other-kb-A`), Name `a.md`,
Inhalt N. Die aktive KB enthaelt zusaetzlich G (`collection_name = kb_id`),
Name `a.md`, ALTER Inhalt O. Zwei Varianten: (1) F liefert einen zum lokalen
Inhalt passenden `meta.file_hash` (Metadaten-Pfad wuerde faelschlich
greifen). (2) F liefert einen abweichenden `meta.file_hash`, aber sein
ROHER Inhalt ist N (Content-Pfad wuerde faelschlich greifen).

Echtes `run_sync` MIT aktiver Coverage (`no_verify` NICHT gesetzt) -- der
Double ersetzt NUR `APIClient._request`; `APIClient` (inkl. `list_files`,
`get_file_content`, `do_upload_file`, `add_file_to_knowledge`,
`remove_file_from_knowledge`, `delete_file`) UND `run_sync` UND
`_run_coverage_check` laufen ECHT. Kein Docker/Netzwerk.

Zusaetzlich ein Positiv-Erhalt (tracked-active Idempotenz, muss VOR UND
NACH dem Fix PASSEN): `old_file_id` liegt WIRKLICH in der aktiven KB unter
`a.md`, Inhalt == N, `meta.file_hash` divergent -> content-gebunden
bestaetigt, KEIN Upload/Link, Manifest behaelt die ID.

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
_spec = importlib.util.spec_from_file_location("r8_01_setup_under_test", _SETUP_PY)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)

_KB_ID = "kb-active-r8"
_FOREIGN_KB_ID = "other-kb-A"
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


class _R8BindingDouble:
    """Dieselbe inhaltsbasierte OWUI-Backendsemantik-Nachbildung wie in
    `test_r7_02_n2_content_confirm_2026_11_19.py` (dort erneut dupliziert
    statt importiert -- bestehende Testkonvention, reiner Testcode). NEU
    ggue. jenem Double: mehrere unterschiedliche `collection_name`-Werte
    gleichzeitig (fremde UND aktive KB), damit der R8-01-Gegenfall (gleich
    benannte Datei in FREMDER KB) abgebildet werden kann."""

    def __init__(self, *, seed_files=None, kb_id=_KB_ID, preset=None):
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
        self._preset = preset
        self._next_id = 100
        for sf in (seed_files or []):
            fid = sf["id"]
            self.store[fid] = sf["content"]
            self.filenames[fid] = sf["filename"]
            coll = sf.get("collection_name")
            self.collection_of[fid] = coll
            # KEY: meta.file_hash darf vom rohen SHA-256 abweichen (OWUI
            # 0.11.3-Divergenz, s. R7-02-N2).
            self.meta_hash[fid] = sf.get("meta_file_hash", self._hash(sf["content"]))
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
        m = re.match(r"^/api/v1/files/([^/]+)/content$", path)
        if method == "GET" and m:
            fid = m.group(1)
            self.content_fetched.append(fid)
            if fid not in self.store:
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
        # UPD-1: `wait_for_file_ready` fragt vor jedem Link-Versuch
        # `GET /api/v1/files/{id}` ab (OHNE `/content`-Suffix) -- bereits im
        # `store` liegender Inhalt gilt sofort als fertig extrahiert.
        if method == "GET" and re.match(r"^/api/v1/files/([^/]+)$", path):
            fid = path.rsplit("/", 1)[-1]
            if fid in self.store:
                return 200, json.dumps({"id": fid, "data": {"content": "ready"}}).encode()
            return 404, b'{"detail": "not found"}'
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


def _build_repo(tmp: Path, content: str) -> None:
    (tmp / "kb").mkdir()
    (tmp / "kb" / "a.md").write_text(content, encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


def _write_manifest(tmp: Path, *, file_id: str, stale_md5: str) -> None:
    (tmp / ".openwebui-sync.json").write_text(json.dumps({
        "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
        "masterprompt_path": "meta/masterprompt.md",
        "kb_files": {"a.md": {"md5": stale_md5, "file_id": file_id}},
        "last_sync": "2026-11-18T00:00:00",
    }), encoding="utf-8")


def _manifest(tmp: Path) -> dict:
    with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
        return json.load(f)


def _run_sync_with_real_coverage(tmp: Path, http):
    """Wie die bestehenden R7-02-Harnesse, ABER OHNE `no_verify=True` --
    die Coverage-Pruefung (`_run_coverage_check`) laeuft ECHT mit."""
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
                    setup_mod.run_sync(tmp, _CFG, {"assume_yes": True})
                    ok = True
                except SystemExit as exc:
                    ok = exc.code in (0, None)
            return ok, buf.getvalue(), holder.get("client")
    finally:
        os.environ.clear(); os.environ.update(saved)


_N = "ZEITRISS Modul R8-01: aktueller Inhalt\nZeile 2\n"
_N_BYTES = _N.encode("utf-8")
_N_SHA = hashlib.sha256(_N_BYTES).hexdigest()
_O_OLD = b"ZEITRISS Modul R8-01: VERALTETER Inhalt\n"
_STALE_MD5 = hashlib.md5(b"irgendein-frueherer-lokaler-stand").hexdigest()


def _active_bound_content(http) -> bytes:
    """Der tatsaechlich unter `a.md` in der AKTIVEN KB verlinkte Inhalt am
    Ende des Laufs -- der harte Abschlussbeleg (nicht nur 'Coverage gruen',
    sondern wirklich Inhalt N)."""
    active_ids = [
        fid for fid in http.store
        if http.filenames.get(fid) == "a.md" and http.collection_of.get(fid) == http.kb_id
    ]
    assert len(active_ids) == 1, (
        f"erwartet genau EINE aktiv verlinkte a.md, gefunden: {active_ids}"
    )
    return http.store[active_ids[0]]


def test_variant1_metadata_hash_match_on_foreign_tracked_id_must_not_confirm():
    """Gegenfall Variante 1: die getrackte Fremd-ID F liefert einen zum
    lokalen Inhalt N passenden `meta.file_hash` -- der Metadaten-Pfad wuerde
    F ohne das Gate faelschlich als aktuell bestaetigen, OBWOHL F nicht zur
    aktiven KB gehoert und die aktive KB nur die alte Kopie G (Inhalt O)
    trägt."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _build_repo(tmp, _N)
        _write_manifest(tmp, file_id="F", stale_md5=_STALE_MD5)
        http = _R8BindingDouble(
            seed_files=[
                {"id": "F", "filename": "a.md", "content": _N_BYTES,
                 "collection_name": _FOREIGN_KB_ID, "meta_file_hash": _N_SHA},
                {"id": "G", "filename": "a.md", "content": _O_OLD,
                 "collection_name": _KB_ID},
            ],
            preset=_PRESET,
        )
        ok, out, _client = _run_sync_with_real_coverage(tmp, http)

        assert ok, out
        assert _active_bound_content(http) == _N_BYTES, (
            "die AKTIVE KB muss am Ende Inhalt N tragen -- ein gruener "
            "Abschluss mit nur O (oder F unverlinkt) in der aktiven KB ist "
            "unzulaessig."
        )
        assert ("kb-active-r8", "F") not in http.unlinked_calls, (
            f"F darf wegen des veralteten Manifestverweises NICHT entlinkt werden: {http.unlinked_calls}"
        )
        assert "F" not in http.deleted, f"F darf NICHT geloescht werden: {http.deleted}"
        assert http.collection_of.get("F") == _FOREIGN_KB_ID, "F bleibt in KB A gebunden"
        assert http.store.get("F") == _N_BYTES, "F bleibt inhaltlich unangetastet"
        assert http.uploaded == ["a.md"], (
            f"der reguläre Pfad muss N tatsaechlich hochladen: {http.uploaded}"
        )
        man = _manifest(tmp)
        new_fid = man["kb_files"]["a.md"]["file_id"]
        assert new_fid not in ("F", "G"), (
            f"die neue Manifest-ID darf weder die Fremd-ID F noch die alte aktive G sein: {new_fid}"
        )


def test_variant2_raw_content_match_on_foreign_tracked_id_must_not_confirm():
    """Gegenfall Variante 2: `meta.file_hash` von F weicht ab, aber F liefert
    denselben ROHEN Inhalt N (Content-Pfad). Ohne das Gate wuerde
    `_confirm_active_kb_file_by_content(client, [F], sha(N))` F ebenfalls
    faelschlich bestaetigen."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _build_repo(tmp, _N)
        _write_manifest(tmp, file_id="F", stale_md5=_STALE_MD5)
        http = _R8BindingDouble(
            seed_files=[
                {"id": "F", "filename": "a.md", "content": _N_BYTES,
                 "collection_name": _FOREIGN_KB_ID, "meta_file_hash": "DIVERGENT-NICHT-DIE-ECHTE-SHA256"},
                {"id": "G", "filename": "a.md", "content": _O_OLD,
                 "collection_name": _KB_ID},
            ],
            preset=_PRESET,
        )
        ok, out, _client = _run_sync_with_real_coverage(tmp, http)

        assert ok, out
        assert _active_bound_content(http) == _N_BYTES, (
            "die AKTIVE KB muss am Ende Inhalt N tragen -- ein gruener "
            "Abschluss mit nur O in der aktiven KB ist unzulaessig."
        )
        assert ("kb-active-r8", "F") not in http.unlinked_calls, (
            f"F darf wegen des veralteten Manifestverweises NICHT entlinkt werden: {http.unlinked_calls}"
        )
        assert "F" not in http.deleted, f"F darf NICHT geloescht werden: {http.deleted}"
        assert http.collection_of.get("F") == _FOREIGN_KB_ID, "F bleibt in KB A gebunden"
        assert http.store.get("F") == _N_BYTES, "F bleibt inhaltlich unangetastet"
        assert http.uploaded == ["a.md"], (
            f"der reguläre Pfad muss N tatsaechlich hochladen: {http.uploaded}"
        )
        man = _manifest(tmp)
        new_fid = man["kb_files"]["a.md"]["file_id"]
        assert new_fid not in ("F", "G"), (
            f"die neue Manifest-ID darf weder die Fremd-ID F noch die alte aktive G sein: {new_fid}"
        )


def test_positive_tracked_active_content_bound_idempotency_preserved():
    """Positiv-Erhalt (muss VOR UND NACH dem Fix PASSEN): `old_file_id`
    gehoert WIRKLICH zur aktiven KB unter `a.md`, Inhalt == N,
    `meta.file_hash` divergent -> content-gebunden bestaetigt, KEIN
    Upload/Link, Manifest behaelt die ID. Sichert, dass das neue Gate die
    getrackte Idempotenz (R7-02/N2) nicht bricht."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _build_repo(tmp, _N)
        _write_manifest(tmp, file_id="active-tracked", stale_md5=_STALE_MD5)
        http = _R8BindingDouble(
            seed_files=[
                {"id": "active-tracked", "filename": "a.md", "content": _N_BYTES,
                 "collection_name": _KB_ID, "meta_file_hash": "DIVERGENT-ABWEICHEND"},
            ],
            preset=_PRESET,
        )
        ok, out, _client = _run_sync_with_real_coverage(tmp, http)

        assert ok, out
        assert http.uploaded == [], f"kein Re-Upload fuer bereits aktiv gebundenen Inhalt: {http.uploaded}"
        assert http.linked_calls == [], f"kein neuer Link-Versuch: {http.linked_calls}"
        assert "active-tracked" in http.content_fetched, "content-Bestaetigung muss gefetcht haben"
        assert "active-tracked" not in http.deleted
        man = _manifest(tmp)
        assert man["kb_files"]["a.md"]["file_id"] == "active-tracked", man
        assert man["kb_files"]["a.md"]["md5"] == hashlib.md5(_N_BYTES).hexdigest()


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
