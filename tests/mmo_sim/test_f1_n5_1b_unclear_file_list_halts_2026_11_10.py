#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n5_1b_unclear_file_list_halts_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N6 §N6-1b (N6-Nachzug zu
N5-1b).

WP-N6-1b korrigiert zwei Reste am N5-1b-Fix:

1. Der bisherige Test (und sein `except Exception`/`isinstance`-Guard im
   Helper) doubelte `list_files()` DIREKT (wirft/liefert `None`) -- das ist
   der FALSCHE Rand. Der echte `APIClient.list_files()` wirft im echten
   Betrieb praktisch nie: jeder HTTP-Fehler/formfalsche Körper/abgebrochene
   Pagination landet dort schon als leere/abgebrochene Seite (`break`,
   `return out`). Der alte Guard sah diese echten Fälle NIE. Jetzt setzt
   `list_files()` einen `last_files_complete`-Marker (analog zu
   `last_model_body_ok`), den `complete_orphaned_kb_install` VOR jeder
   Mutation prüft -- das ist der ECHTE Fehlerpfad, mit echtem `list_files`
   und NUR der äußeren HTTP-Schicht gedoubelt.

2. Eine bereits in der KB verlinkte gleichnamige Datei wurde bedingungslos
   entlinkt+gelöscht VOR dem Upload (Rückgaben ignoriert) -- bei Erfolg ging
   die korrekte alte ID unnötig verloren, scheiterte der Upload NACH dem
   Löschen, war der korrekte Inhalt ersatzlos weg. Jetzt: erhaltende
   Reihenfolge -- neuen Inhalt separat hochladen und an dieselbe KB linken,
   WÄHREND die alte Version noch hängt. OpenWebUIs dokumentierte
   "400 Duplicate content detected"-Eigenschaft dient als Orakel: Link
   gelingt -> Inhalt war anders -> jetzt sicher ersetzen (alte Version
   löschen). Link scheitert MIT Duplicate-Signatur -> Inhalt ist bestätigt
   identisch -> kein Ersatz nötig, alte Version bleibt unangetastet. Link
   scheitert OHNE Duplicate-Signatur (echter Fehler) -> alte Version bleibt
   unangetastet, aber NICHT bestätigt (sichtbare Unvollständigkeit).

Deckt (direkter Aufruf von `complete_orphaned_kb_install`, Fake NUR am
äußeren HTTP-Rand -- `APIClient` selbst (inkl. `list_files`, `get`,
`post_json`, `upload_file`, `delete`) UND der Helper laufen ECHT):
  (A) Erster Read HTTP-Fehler (Seite 1 ≠ 200) -> `last_files_complete`
      False -> Helper hält an (False, kein Upload, kein Manifest-Schaden).
  (B) Späterer Seitenfehler/Teilread (`total` > gelesen, Seite 2 ≠ 200) ->
      unvollständig -> Helper hält an.
  (C) Falsche Körperform (200-dict ohne `items`) -> unvollständig/unklar ->
      Helper hält an.
  (D) Gegenprobe gültige vollständige Leere (200 `{"items":[],"total":0}`)
      -> vollständig -> normaler Ergänzungsweg (Upload läuft).
  (E) Gegenprobe vollständige alt-unpaginierte Liste (JSON-Liste statt
      `{items,total}`) -> vollständig -> normaler Weg.
  (F) Erhalt eigener richtiger Datei: eine bereits in dieser KB verlinkte
      gleichnamige Datei behält ihre ID (Duplicate-Orakel bestätigt
      identischen Inhalt) -- kein blindes delete, Manifest trägt die
      ERHALTENE (alte) ID.
  (G) Fehlerfall erhält Bestand: ein echter Link-Fehlschlag (keine
      Duplicate-Signatur) beim nötigen Ersatz vernichtet den bestätigten
      Altbestand NICHT und meldet Unvollständigkeit wahr (kein Manifest-
      Eintrag für diese Datei, `all_ok=False`).

Double-Grenze (A4, offen gelegt): NUR `APIClient._request` ist gedoubelt
(kein echter Netzwerk-Call) -- `complete_orphaned_kb_install`,
`discover_knowledge_files`, `_file_md5`, `_save_sync_manifest`, UND
`APIClient` selbst (`list_files`, `get_model`/`list_knowledge` unbenutzt
hier, `upsert_model`, `do_upload_file`, `add_file_to_knowledge`,
`remove_file_from_knowledge`, `delete_file`) laufen ECHT gegen ein echtes
temporäres Repo. `_auto_load_owui_env` ist gedoubelt (kein Zugriff auf
~/.openwebui_env). Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk.

---

N7-Nachzug (ZR-MINT-F1-N7, PR #3301, 2026-11-10) — WP-N6-1b hatte EINE
Testlücke: (F)/(H) oben doubeln das "400 Duplicate content detected" über
einen reinen `link_behavior`-Dict pro DATEINAME -- das ist der FALSCHE
Rand. OWUIs echter Check (retrieval.py:1666-1685, gebundene Primärquelle)
ist COLLECTION-WEIT nach Content-HASH, nicht nach Namen: der 400 kann von
einer GANZ ANDEREN Datei derselben Wissensbasis stammen, nicht nur von
`existing_fid`. Der alte Helper-Code las daraus fälschlich "existing_fid
ist bestätigt synchron" -- N7-A1 korrigiert das (erhaltender Halt statt
falscher Bestätigung, da kein verlässlicher Pro-Datei-Hash über die
gebundene Primärquelle belegt ist). N7-A2 wertet die realen
Unlink/Delete-Rückgaben beim bestätigten Ersatz aus (Backendsemantik:
knowledge.py:1593-1659 -- Unlink kann die File-Entity schon selbst
mitlöschen, ein redundanter zweiter 200 ist NICHT verlangt). N7-A3 bringt
dieselbe erhaltende upload-vor-delete-Reihenfolge in `run_sync`s
Namensfallback (vorher: unbedingt löschen VOR dem Upload).

Neu/ersetzt wegen der N6-Testlücke:
  (F') `test_a1_collection_wide_duplicate_from_other_file_does_not_confirm_own_id`
       -- ersetzt die alte (F): ein COLLECTION-WEITER Duplicate-Treffer
       gegen eine ANDERE Datei B bestätigt die eigene `existing_fid` NICHT
       als synchron. Double jetzt inhaltsbasiert (`_ContentHttpDouble`).
  (H') `test_upload_returning_existing_id_never_destroys_only_copy`
       -- gleicher Name, jetzt gegen den inhaltsbasierten Double: die
       einzige WIRKLICH verifizierte (nicht erratene) Wiederverwendung
       einer ID ist die direkte ID-Gleichheit (`new_file_id == existing_fid`,
       retrieval.py:1677-1678 erlaubt Re-Add derselben file_id explizit).
  (I) `test_a3_followup_run_sync_upload_failure_preserves_lone_copy_then_resumes`
       -- zweistufig über den TATSÄCHLICHEN Folgecaller `run_sync` (nicht
       gemockt): Stufe 1 `complete_orphaned_kb_install` bleibt wegen A1-
       Ambiguität unvollständig (keine Manifest-Bestätigung), Stufe 2a
       `run_sync` erreicht über den fehlenden Manifest-Eintrag den
       Namensfallback, ein erneuter (echter, nicht Duplicate-) Link-Fehler
       darf die einzige richtige alte Kopie NICHT vorher vernichten, Stufe
       2b (weiterer `run_sync`, kein Rebuild) schließt denselben Zustand
       nach behobenem Transientfehler korrekt ab.
"""
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
    "f1_n6_1b_unclear_file_list_halts_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)

_KB_ID = "kb-existing-1"


def _extract_upload_filename(body: bytes) -> str:
    m = re.search(rb'filename="([^"]+)"', body or b"")
    return m.group(1).decode("utf-8") if m else ""


class _HttpDouble:
    """Fake NUR am äußeren HTTP-Rand (`APIClient._request`) -- `APIClient`
    selbst (`list_files`, `upsert_model`, `do_upload_file`,
    `add_file_to_knowledge`, `remove_file_from_knowledge`, `delete_file`)
    läuft ECHT gegen diese simulierten HTTP-Antworten."""

    def __init__(self, *, files_pages, link_behavior=None, kb_id=_KB_ID,
                 collision_upload_id=None):
        self.files_pages = files_pages  # list[(status:int, body:bytes)], 1-indexed via page-1
        self.link_behavior = dict(link_behavior or {})  # filename -> "ok"|"duplicate"|"fail"
        self.kb_id = kb_id
        # WP-N6-1b Defense-in-Depth: erzwingt den (beim realen Backend
        # unmoeglichen) pathologischen Fall, dass der Upload eine BEREITS
        # existierende file_id zurueckgibt -- zum Testen der No-Loss-Invariante.
        self.collision_upload_id = collision_upload_id
        self.uploaded: list[str] = []
        self.deleted: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.unlinked: list[tuple[str, str]] = []
        self._next_id = 100
        self._id_to_name: dict[str, str] = {}

    def request(self, method, path, data=None, content_type="application/json", timeout=None):
        if method == "GET" and path == "/api/config":
            return 200, b"{}"
        if method == "GET" and path == "/api/models":
            return 200, b'{"data": []}'
        if method == "POST" and path == "/api/v1/models/create":
            return 200, b'{"id": "p1"}'
        if method == "POST" and path == "/api/v1/models/model/update":
            return 200, b'{"id": "p1"}'
        if method == "GET" and path.startswith("/api/v1/files/?page="):
            page = int(path.rsplit("=", 1)[1])
            idx = page - 1
            if 0 <= idx < len(self.files_pages):
                return self.files_pages[idx]
            return 200, b'{"items": [], "total": 0}'
        if method == "POST" and path == "/api/v1/files/":
            fname = _extract_upload_filename(data if isinstance(data, bytes) else b"")
            if self.collision_upload_id is not None:
                new_id = self.collision_upload_id   # pathologischer Backend-Dedupe
            else:
                self._next_id += 1
                new_id = f"file-new-{self._next_id}"
            self._id_to_name[new_id] = fname
            self.uploaded.append(fname)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/add":
            file_id = (data or {}).get("file_id")
            fname = self._id_to_name.get(file_id, "")
            behavior = self.link_behavior.get(fname, "ok")
            if behavior == "duplicate":
                return 400, b'{"detail": "400: Duplicate content detected"}'
            if behavior == "fail":
                return 500, b'{"detail": "internal error"}'
            self.linked.append((self.kb_id, file_id))
            return 200, b"{}"
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/remove":
            file_id = (data or {}).get("file_id")
            self.unlinked.append((self.kb_id, file_id))
            return 200, b"{}"
        if method == "DELETE" and path.startswith("/api/v1/files/"):
            file_id = path.rsplit("/", 1)[1]
            self.deleted.append(file_id)
            return 200, b"{}"
        return 200, b"{}"


def _build_repo(tmp: Path, *, filenames=("a.md",)) -> None:
    (tmp / "kb").mkdir()
    for i, name in enumerate(filenames):
        (tmp / "kb" / name).write_text(f"Inhalt {i}", encoding="utf-8")
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


_RealAPIClient = setup_mod.APIClient


def _run(tmp: Path, http: _HttpDouble):
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
                ok = setup_mod.complete_orphaned_kb_install(tmp, _CFG, _KB_ID)
            return ok, buf.getvalue(), real_client_holder["client"]
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _manifest(tmp: Path) -> dict:
    with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
        return json.load(f)


# ── N7: inhaltsbasierter Double + run_sync-Testharness ──────────────────

def _extract_upload_content(body: bytes, content_type: str) -> bytes:
    """Extrahiert den rohen Dateiinhalt aus dem multipart/form-data-Body, den
    `APIClient.upload_file()` baut (setup.py ~448-468): Boundary aus dem
    Content-Type-Header, Inhalt zwischen dem Header-Block und dem
    End-Marker."""
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
    """Fake NUR am äußeren HTTP-Rand (`APIClient._request`). Simuliert OWUIs
    TATSÄCHLICHE Backendsemantik aus der gebundenen Primärquelle
    (retrieval.py:1666-1685): Duplicate-Erkennung ist COLLECTION-WEIT nach
    INHALTS-HASH, NICHT nach Dateiname. Der Store hält `file_id -> Inhalt`
    (Bytes) plus `linked` (file_ids, die aktuell in DIESER KB verlinkt
    sind). `add_file_to_knowledge` vergleicht den Hash des Inhalts hinter
    der gegebenen file_id gegen ALLE aktuell verlinkten Inhalte -- ein
    Treffer mit einer ANDEREN file_id löst "400 Duplicate content
    detected" aus (exakt retrieval.py:1683:
    `existing_file_id != metadata.get('file_id')`). Dieselbe file_id
    erneut zu verlinken ist dagegen immer erlaubt (Re-Add/Reindex,
    retrieval.py:1677-1678) -- NIE ein Duplicate gegen sich selbst.

    Das ist der WP-N6-1b-Testlücken-Fix: der alte `_HttpDouble` doubelte
    "duplicate" über ein `link_behavior`-Dict PRO DATEINAME -- das kann den
    N7-A1-Gegenfall (Duplicate durch eine ANDERE Datei derselben KB) gar
    nicht darstellen, weil es den Treffer künstlich an den Namen bindet,
    den OWUI laut Primärquelle nie prüft."""

    def __init__(self, *, seed_files=None, kb_id=_KB_ID, collision_upload_id=None,
                 fail_add_file_times=None, fail_remove_file_ids=None, preset=None):
        self.kb_id = kb_id
        self.store: dict = {}
        self.filenames: dict = {}
        self.collection_of: dict = {}
        self.linked: set = set()
        self.uploaded: list = []
        self.deleted: list = []
        self.linked_calls: list = []
        self.unlinked_calls: list = []
        self.collision_upload_id = collision_upload_id
        self.fail_add_file_times = dict(fail_add_file_times or {})
        # N7-A2: Fehlinjektion für /file/remove (transienter Unlink-Fehler),
        # OHNE die Datei zu entlinken/löschen -- der von Vera benannte, bisher
        # untestbare BLOCKER-Pfad.
        self.fail_remove_file_ids = set(fail_remove_file_ids or [])
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
            # N7-A1: OWUI liefert pro Datei `meta.file_hash` (= SHA-256 des
            # Inhalts; am echten v0.11.3-Backend verifiziert). Der Double
            # bildet das nach, damit der produktive Hash-first-Identitäts-
            # abgleich (statt des collectionweiten Duplicate-Ratens) geprüft
            # wird.
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
            content = _extract_upload_content(
                data if isinstance(data, bytes) else b"", content_type)
            new_id = self.collision_upload_id
            if new_id is None:
                self._next_id += 1
                new_id = f"file-new-{self._next_id}"
            self.store[new_id] = content
            self.filenames[new_id] = fname
            self.collection_of.setdefault(new_id, None)
            self.uploaded.append(fname)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path == f"/api/v1/knowledge/{self.kb_id}/file/add":
            file_id = (data or {}).get("file_id")
            fname = self.filenames.get(file_id, "")
            countdown = self.fail_add_file_times.get(fname, 0)
            if countdown > 0:
                self.fail_add_file_times[fname] = countdown - 1
                return 500, b'{"detail": "internal error"}'
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
            if file_id in self.fail_remove_file_ids:
                # Transienter Unlink-Fehler: Datei bleibt verlinkt+vorhanden.
                return 500, b'{"detail": "internal error"}'
            if file_id not in self.store or file_id not in self.linked:
                return 400, b'{"detail": "400: NOT_FOUND"}'
            self.linked.discard(file_id)
            if self.collection_of.get(file_id) == self.kb_id:
                self.collection_of[file_id] = None
            self.unlinked_calls.append((self.kb_id, file_id))
            return 200, b"{}"
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


_SYNC_CFG = dict(_CFG, default_variant="default")


def _run_sync(tmp: Path, http, *, cfg=None):
    """Treibt das ECHTE `run_sync` (der tatsächliche Folgecaller nach
    installed -> [1] -> Update, launcher.py:899-908/1337-1340) gegen den
    gegebenen Double. `no_verify`+`assume_yes`: überspringt den
    Retrieval-Smoke-Check und die interaktive Bestätigung (nicht Teil
    dieses Rests, A5 bleibt unberührt)."""
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
                    setup_mod.run_sync(tmp, cfg or _SYNC_CFG, {"no_verify": True, "assume_yes": True})
                    ok = True
                except SystemExit as exc:
                    ok = exc.code in (0, None)
            return ok, buf.getvalue(), real_client_holder.get("client")
    finally:
        os.environ.clear()
        os.environ.update(saved)


# ── (A)-(C): unvollständiger/unklarer Read haelt an ─────────────────────

def test_first_page_http_error_halts_before_any_upload():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        http = _HttpDouble(files_pages=[(500, b"server error")])
        ok, out, client = _run(tmp, http)
        assert ok is False, "ein HTTP-Fehler auf Seite 1 ist KEINE bestaetigte Leere -- darf nicht True liefern"
        assert client.last_files_complete is False
        assert http.uploaded == [], (
            "ein unvollstaendiger Dateilisten-Read darf KEINEN Upload ausloesen"
        )
        assert not (tmp / ".openwebui-sync.json").exists(), (
            "bei einem unklaren Read darf KEIN Manifest geschrieben werden"
        )
        assert "unklar" in out.lower() or "unvollständig" in out.lower(), out


def test_later_page_error_before_total_reached_halts_before_any_upload():
    page1 = (200, json.dumps({
        "items": [{"id": "f1", "filename": "other.md", "meta": {"collection_name": "some-other-kb"}}],
        "total": 5,
    }).encode())
    page2 = (500, b"server error")
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        http = _HttpDouble(files_pages=[page1, page2])
        ok, out, client = _run(tmp, http)
        assert ok is False, "eine vor Erreichen von 'total' abgebrochene Pagination ist KEINE bestaetigte Vollstaendigkeit"
        assert client.last_files_complete is False
        assert http.uploaded == []
        assert not (tmp / ".openwebui-sync.json").exists()
        assert "unklar" in out.lower() or "unvollständig" in out.lower(), out


def test_malformed_body_without_items_halts_before_any_upload():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp)
        http = _HttpDouble(files_pages=[(200, b'{"detail": "unexpected shape"}')])
        ok, out, client = _run(tmp, http)
        assert ok is False, "ein 200-dict ohne 'items' ist formfalsch, KEINE bestaetigte Leere"
        assert client.last_files_complete is False
        assert http.uploaded == []
        assert not (tmp / ".openwebui-sync.json").exists()
        assert "unklar" in out.lower() or "unvollständig" in out.lower(), out


# ── (D)-(E): Gegenproben -- vollstaendig gelesen, normaler Weg ──────────

def test_confirmed_complete_empty_page_reaches_normal_upload_path():
    """(D): eine echte, vollstaendig gelesene LEERE Seite (`total` erreicht)
    ist KEIN unklarer Read -- der normale Ergaenzungsweg bleibt moeglich."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _HttpDouble(files_pages=[(200, b'{"items": [], "total": 0}')])
        ok, _out, client = _run(tmp, http)
        assert ok is True
        assert client.last_files_complete is True
        assert http.uploaded == ["a.md"], "bestaetigt vollstaendige Leere darf den normalen Upload-Weg nicht blockieren"
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"]


def test_confirmed_complete_unpaginated_list_reaches_normal_upload_path():
    """(E): die alte, unpaginierte Antwortform (JSON-LISTE statt
    {items,total}) ist vollstaendig in einem Rutsch -- normaler Weg."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _HttpDouble(files_pages=[(200, b"[]")])
        ok, _out, client = _run(tmp, http)
        assert ok is True
        assert client.last_files_complete is True
        assert http.uploaded == ["a.md"]
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"]


# ── (F)/(G): erhaltende Ersatz-Logik fuer bereits verlinkte Dateien ─────

def test_a1_collection_wide_duplicate_from_other_file_does_not_confirm_own_id():
    """(F', ersetzt die alte (F) -- N6-Testlücke): OWUIs Duplicate-Check
    (retrieval.py:1666-1685) ist COLLECTION-WEIT nach Content-Hash, NICHT
    nach Dateiname. Hier hängt eine ANDERE Datei B ("other.md", Inhalt
    "GEMEINSAM") bereits in der KB; die lokale a.md soll jetzt ebenfalls
    "GEMEINSAM" tragen. Der Upload von a.mds neuem Inhalt kollidiert beim
    Link per Hash mit B (NICHT mit der eigenen `existing_fid`) -- der 400
    nennt keine file_id (knowledge.py:1477-1482), also darf das NICHT als
    Bestätigung gelesen werden, dass die eigene alte Datei ("file-a-in-kb",
    tatsächlicher Inhalt "ALT-A") bereits "GEMEINSAM" trägt. Erhaltender
    Halt: a.md bleibt UNBESTÄTIGT, die eigene alte Version UND die fremde
    Datei B bleiben beide unberührt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        (tmp / "kb" / "a.md").write_text("GEMEINSAM", encoding="utf-8")
        http = _ContentHttpDouble(seed_files=[
            {"id": "file-a-in-kb", "filename": "a.md", "content": b"ALT-A",
             "collection_name": _KB_ID},
            {"id": "file-b-other", "filename": "other.md", "content": b"GEMEINSAM",
             "collection_name": _KB_ID},
        ])
        ok, out, _client = _run(tmp, http)
        assert ok is False, (
            "ein collection-weiter Duplicate-Treffer gegen eine ANDERE Datei ist "
            "KEINE Bestätigung von existing_fid -- darf nicht True liefern"
        )
        assert http.store.get("file-a-in-kb") == b"ALT-A", (
            "die eigene alte Datei A darf NICHT verändert werden"
        )
        assert "file-a-in-kb" in http.linked and "file-a-in-kb" not in http.deleted, (
            "die eigene alte Datei A darf NICHT entlinkt/gelöscht werden -- unbestätigt heißt erhaltend, nicht destruktiv"
        )
        assert http.store.get("file-b-other") == b"GEMEINSAM", "fremde Datei B bleibt unberührt"
        assert "file-b-other" in http.linked and "file-b-other" not in http.deleted
        manifest = _manifest(tmp)
        assert "a.md" not in manifest["kb_files"], (
            "ohne echte Pro-Datei-Bestätigung darf a.md NICHT als synchron verbucht werden"
        )
        assert "unklar" in out.lower(), out


def test_a1_existing_file_with_matching_content_hash_is_confirmed_without_upload():
    """(N7-A1 Positivfall — der normale unterstützte Erfolgsfall MUSS
    abschließbar bleiben): eine bereits verlinkte gleichnamige Datei, deren
    OWUI-`meta.file_hash` (SHA-256, am echten Backend verifiziert) GENAU dem
    lokalen Inhalt entspricht, wird über diese echte Pro-ID-Quelle bestätigt
    — OHNE Vergleichs-Upload und OHNE collectionweites Duplicate-Raten. Das
    ist der häufige orphaned-KB-Fall (Dateien aus einem abgebrochenen Vorlauf
    sind bereits korrekt): er darf NICHT dauerhaft als unvollständig halten,
    sondern schließt sauber ab, die richtige ID bleibt erhalten."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        (tmp / "kb" / "a.md").write_text("KORREKT-A-INHALT", encoding="utf-8")
        http = _ContentHttpDouble(seed_files=[
            {"id": "file-a-in-kb", "filename": "a.md", "content": b"KORREKT-A-INHALT",
             "collection_name": _KB_ID},
        ])
        ok, out, _client = _run(tmp, http)
        assert ok is True, (
            "ein per Content-Hash bestätigter identischer Altbestand ist der normale "
            "Erfolgsfall und muss abschließbar sein (ok=True)"
        )
        assert http.uploaded == [], (
            "bei Hash-Identität darf KEIN Vergleichs-Upload ausgelöst werden"
        )
        assert http.store.get("file-a-in-kb") == b"KORREKT-A-INHALT" and "file-a-in-kb" in http.linked, (
            "die bestätigte eigene Datei bleibt unverändert verlinkt"
        )
        assert "file-a-in-kb" not in http.deleted, "die korrekte eigene Datei wird NICHT gelöscht"
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-in-kb", (
            "Manifest trägt die ERHALTENE, per Hash bestätigte eigene file_id"
        )
        assert "identisch" in out.lower() or "unverändert" in out.lower(), out


def test_existing_linked_file_with_real_difference_gets_replaced_safely():
    """Gegenprobe zu (F): unterscheidet sich der Inhalt wirklich (Link des
    neuen Uploads GELINGT, waehrend die alte Version noch haengt -- kein
    Duplicate-Reject), wird die alte Version ERST NACH bestaetigtem Ersatz
    entfernt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        existing_page = (200, json.dumps({
            "items": [{"id": "file-a-in-kb", "filename": "a.md",
                       "meta": {"collection_name": _KB_ID}}],
            "total": 1,
        }).encode())
        http = _HttpDouble(files_pages=[existing_page], link_behavior={"a.md": "ok"})
        ok, _out, _client = _run(tmp, http)
        assert ok is True
        assert "a.md" in http.uploaded
        assert "file-a-in-kb" in http.deleted, "nach bestaetigtem Ersatz darf die alte Version entfernt werden"
        assert (_KB_ID, "file-a-in-kb") in http.unlinked
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] != "file-a-in-kb", (
            "Manifest muss die NEUE, bestaetigt verlinkte file_id tragen"
        )


def test_a2_failed_unlink_does_not_delete_old_entity_and_reports_truthfully():
    """(N7-A2 BLOCKER, Vera): schlägt beim nötigen Ersatz das UNLINK der alten
    Version fehl (transienter 500), darf `delete_file` NICHT trotzdem laufen —
    sonst löscht die ungated DELETE-Route die alte File-Entity, während die
    KB-Bindung (laut gescheitertem Unlink) noch besteht (tote Referenz), und
    die Meldung „beide verlinkt" wäre faktisch falsch. Erwartet: alte Entity
    bleibt im Store UND verlinkt, kein confirmed, all_ok=False, ehrliche
    Meldung (die dann WAHR ist)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        (tmp / "kb" / "a.md").write_text("NEU-B-INHALT", encoding="utf-8")
        http = _ContentHttpDouble(
            seed_files=[
                {"id": "file-a-in-kb", "filename": "a.md", "content": b"ALT-A-INHALT",
                 "collection_name": _KB_ID},
            ],
            fail_remove_file_ids={"file-a-in-kb"},  # Unlink der alten schlägt fehl
        )
        ok, out, _client = _run(tmp, http)
        assert ok is False, "ein fehlgeschlagenes Unlink der nötigen Altentfernung ist KEIN vollständiger Erfolg"
        assert "file-a-in-kb" in http.store, (
            "die alte File-Entity darf bei fehlgeschlagenem Unlink NICHT per delete_file gelöscht werden "
            "(sonst tote Referenz: Entity weg, KB-Bindung bleibt)"
        )
        assert "file-a-in-kb" in http.linked, (
            "bei fehlgeschlagenem Unlink bleibt die alte Version tatsächlich verlinkt — die Meldung muss dazu passen"
        )
        assert "file-a-in-kb" not in http.deleted, "kein delete_file nach fehlgeschlagenem Unlink"
        manifest = _manifest(tmp)
        assert "a.md" not in manifest["kb_files"], "ein unbestätigter Ersatz darf NICHT als synchron verbucht werden"


def test_real_link_failure_during_replace_preserves_old_stock_and_reports_incomplete():
    """(G): ein echter Link-Fehlschlag (KEINE Duplicate-Signatur) beim
    noetigen Ersatz vernichtet den bestaetigten Altbestand NICHT -- die
    alte, bereits verlinkte Datei bleibt unangetastet, wird aber auch NICHT
    als bestaetigt verbucht (ehrliche Unvollstaendigkeit)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        existing_page = (200, json.dumps({
            "items": [{"id": "file-a-in-kb", "filename": "a.md",
                       "meta": {"collection_name": _KB_ID}}],
            "total": 1,
        }).encode())
        http = _HttpDouble(files_pages=[existing_page], link_behavior={"a.md": "fail"})
        ok, out, _client = _run(tmp, http)
        assert ok is False, "ein echter Link-Fehlschlag beim Ersatz ist KEIN vollstaendiger Erfolg"
        assert "file-a-in-kb" not in http.deleted, (
            "ein echter (nicht-Duplicate-) Link-Fehler darf den bestaetigten Altbestand NICHT loeschen"
        )
        assert (_KB_ID, "file-a-in-kb") not in http.unlinked, (
            "ein echter Link-Fehler darf die alte Version NICHT entlinken"
        )
        manifest = _manifest(tmp)
        assert "a.md" not in manifest["kb_files"], (
            "ein unbestaetigter Ersatz darf NICHT als synchron im Manifest stehen"
        )
        assert "fehlgeschlagen" in out.lower() or "unvollständig" in out.lower(), out


def test_upload_returning_existing_id_never_destroys_only_copy():
    """(H', Defense-in-Depth, gegen den inhaltsbasierten Double): selbst
    wenn der Upload — entgegen dem realen OpenWebUI-Backend (`uuid4()`
    unbedingt) — eine BEREITS existierende file_id zurueckgaebe
    (`new_file_id == existing_fid`), darf KEIN Loeschpfad die einzige
    Kopie vernichten. Anders als (F'): hier ist die ID-Gleichheit eine
    DIREKT VERIFIZIERTE Tatsache (Rückgabewert des eigenen Upload-Calls),
    keine Inferenz aus einem ambiguen Collection-Signal -- OWUIs
    retrieval.py:1677-1678 erlaubt genau das explizit (Re-Add derselben
    file_id = Reindex, kein Duplicate). Der Double entscheidet das jetzt
    über echten Hash-Vergleich (schließt die EIGENE file_id aus dem
    Kollisionscheck aus), nicht über ein manuell erzwungenes
    `link_behavior`. Der lokale `distinct`-Guard erzwingt die
    No-Loss-Invariante zusätzlich, unabhängig von der externen,
    unversionierten Backend-Zusicherung."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _ContentHttpDouble(
            seed_files=[{"id": "file-a-in-kb", "filename": "a.md",
                         "content": b"Inhalt 0", "collection_name": _KB_ID}],
            collision_upload_id="file-a-in-kb",
        )
        ok, _out, _client = _run(tmp, http)
        assert ok is True, "verifizierte ID-Gleichheit (Re-Add derselben file_id) ist KEIN Fehlerfall"
        assert "file-a-in-kb" not in http.deleted, (
            "bei ID-Kollision (new_file_id == existing_fid) darf die einzige Kopie "
            "NIE geloescht werden -- sonst stiller, irreversibler Datenverlust"
        )
        assert (_KB_ID, "file-a-in-kb") not in http.unlinked_calls, (
            "die einzige Kopie darf bei ID-Kollision auch nicht entlinkt werden"
        )
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-in-kb", (
            "die verifizierte (einzige) file_id muss im Manifest stehen"
        )


def test_a3_followup_run_sync_upload_failure_preserves_lone_copy_then_resumes():
    """(I) N7-A3, zweistufig über den TATSÄCHLICHEN Folgecaller (kein Mock,
    kein Spezialbefehl, kein `run_sync`-Neuaufguss):

    Stufe 1 (`complete_orphaned_kb_install`, ECHT): lokale a.md soll
    "FREMD-Y" tragen -- das ist exakt der Inhalt der FREMDEN Datei B
    ("other.md", "file-b-other") derselben KB, NICHT der tatsächliche
    Inhalt der eigenen alten Datei ("file-a-old", "ALT-X"). Das ist
    N7-A1-Ambiguität (wie (F') oben) -- der Helper hält erhaltend an,
    a.md bleibt NICHT im Manifest, "file-a-old" bleibt unangetastet.

    Stufe 2a (`run_sync`, ECHT, DIREKT aufgerufen -- der tatsächliche
    Folgecaller, den `installed` -> [1] -> Update erreicht,
    launcher.py:899-908/1337-1340): der lokale Inhalt ändert sich
    (normaler Weiterbetrieb) auf "NEU-Z". Der fehlende Manifest-Eintrag
    gilt als "geändert"; `run_sync` findet "file-a-old" über den
    Namensfallback (Manifest hat KEINEN `file_id`-Eintrag für a.md).
    VORHER (N7-A3-Bug): "file-a-old" würde HIER sofort entlinkt+gelöscht,
    VOR dem Upload von "NEU-Z". Simuliert wird ein echter (nicht
    Duplicate-) Transientfehler beim anschließenden Link (zwei
    fehlgeschlagene Versuche: Erstversuch + `run_sync`s interner
    1s-Retry) -- NACH dem Fix darf "file-a-old" das NICHT vorher verloren
    haben.

    Stufe 2b (`run_sync`, ECHT, weiterer Lauf, KEIN Rebuild): der
    Transientfehler ist vorbei, der Link gelingt -- derselbe Zustand
    schließt jetzt korrekt ab, Manifest trägt die neue bestätigte
    Zuordnung, "file-a-old" wird ERST JETZT entfernt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        kb_id = _KB_ID
        preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES,
                     "knowledge": [{"id": kb_id}]},
            "params": {"system": "Du bist die SL."},
        }
        http = _ContentHttpDouble(
            seed_files=[
                {"id": "file-a-old", "filename": "a.md", "content": b"ALT-X",
                 "collection_name": kb_id},
                {"id": "file-b-other", "filename": "other.md", "content": b"FREMD-Y",
                 "collection_name": kb_id},
            ],
            kb_id=kb_id,
            preset=preset,
        )

        # Stufe 1: A1-Ambiguität -- a.md bleibt unbestätigt.
        (tmp / "kb" / "a.md").write_text("FREMD-Y", encoding="utf-8")
        ok1, _out1, _client1 = _run(tmp, http)
        assert ok1 is False
        manifest1 = _manifest(tmp)
        assert "a.md" not in manifest1["kb_files"]
        assert http.store.get("file-a-old") == b"ALT-X", "Stufe 1 lässt die alte Version unangetastet"
        assert "file-a-old" in http.linked

        # Normaler Weiterbetrieb: lokaler Inhalt ändert sich erneut.
        (tmp / "kb" / "a.md").write_text("NEU-Z", encoding="utf-8")

        # Stufe 2a: echtes run_sync, zwei echte Link-Fehlschläge (kein Duplicate).
        http.fail_add_file_times["a.md"] = 2
        ok2, out2, _client2 = _run_sync(tmp, http)
        assert ok2 is False, "ein echter Upload-/Linkfehler bei der Fortsetzung ist KEIN vollständiger Erfolg"
        assert "file-a-old" in http.store, (
            "N7-A3-Gegenfall: die einzige richtige alte Kopie darf bei einem ERNEUTEN "
            "Upload-/Linkfehler NICHT vorher gelöscht worden sein"
        )
        assert "file-a-old" in http.linked, "die alte Version darf vor bestätigtem Ersatz nicht entlinkt werden"
        manifest2 = _manifest(tmp)
        assert "a.md" not in manifest2.get("kb_files", {}), (
            "ein fehlgeschlagener Ersatz darf nicht als bestätigt synchron verbucht werden"
        )
        assert "fehlgeschlagen" in out2.lower() or "unvollständig" in out2.lower(), out2

        # Stufe 2b: weiterer run_sync-Lauf, kein Rebuild -- Transientfehler vorbei.
        ok3, _out3, _client3 = _run_sync(tmp, http)
        assert ok3 is True, "nach behobenem Transientfehler muss derselbe Zustand korrekt abschließen"
        manifest3 = _manifest(tmp)
        assert manifest3["kb_files"]["a.md"]["md5"] == hashlib.md5(b"NEU-Z").hexdigest()
        new_id = manifest3["kb_files"]["a.md"]["file_id"]
        assert new_id in http.linked and new_id != "file-a-old"
        assert "file-a-old" not in http.store, (
            "nach bestätigtem Ersatz muss die alte Version ENTFERNT sein -- "
            "KEIN separater Rebuild nötig, derselbe run_sync-Lauf schließt ab"
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
