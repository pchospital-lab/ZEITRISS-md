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

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

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

def test_existing_linked_file_with_identical_content_keeps_old_id():
    """(F): eine bereits in DIESER KB verlinkte gleichnamige Datei wird NICHT
    blind geloescht -- das Duplicate-Orakel bestaetigt identischen Inhalt
    (Link des neuen Uploads scheitert MIT "Duplicate content"-Signatur,
    WAEHREND die alte Version noch haengt), die ALTE (bestaetigt richtige)
    file_id bleibt im Manifest erhalten."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        existing_page = (200, json.dumps({
            "items": [{"id": "file-a-in-kb", "filename": "a.md",
                       "meta": {"collection_name": _KB_ID}}],
            "total": 1,
        }).encode())
        http = _HttpDouble(
            files_pages=[existing_page],
            link_behavior={"a.md": "duplicate"},
        )
        ok, _out, client = _run(tmp, http)
        assert ok is True, "Duplicate-bestaetigt-identischer Inhalt ist KEIN Fehlerfall"
        assert client.last_files_complete is True
        assert "a.md" in http.uploaded, "der Oracle-Test erfordert einen Vergleichs-Upload"
        assert ("file-a-in-kb" not in http.deleted), (
            "die ALTE, bereits verlinkte Datei darf bei bestaetigtem Duplicate-Fund NICHT geloescht werden"
        )
        assert (_KB_ID, "file-a-in-kb") not in http.unlinked, (
            "die ALTE, bereits verlinkte Datei darf bei bestaetigtem Duplicate-Fund NICHT entlinkt werden"
        )
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-in-kb", (
            "Manifest muss die ERHALTENE alte file_id tragen, nicht eine neue"
        )


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
    """(H, Defense-in-Depth): selbst wenn der Upload — entgegen dem realen
    OpenWebUI-Backend (`uuid4()` unbedingt) — eine BEREITS existierende
    file_id zurueckgaebe (`new_file_id == existing_fid`), darf KEIN
    Loeschpfad die einzige Kopie der Wissensdatei vernichten. Der lokale
    Guard (`distinct`) erzwingt die No-Loss-Invariante unabhaengig von der
    externen, unversionierten Backend-Zusicherung."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        existing_page = (200, json.dumps({
            "items": [{"id": "file-a-in-kb", "filename": "a.md",
                       "meta": {"collection_name": _KB_ID}}],
            "total": 1,
        }).encode())
        # Upload liefert kollidierend DIESELBE id wie die bereits verlinkte Datei;
        # Re-Link meldet Duplicate (identischer Inhalt) -> elif-Zweig.
        http = _HttpDouble(
            files_pages=[existing_page],
            link_behavior={"a.md": "duplicate"},
            collision_upload_id="file-a-in-kb",
        )
        ok, _out, _client = _run(tmp, http)
        assert "file-a-in-kb" not in http.deleted, (
            "bei ID-Kollision (new_file_id == existing_fid) darf die einzige Kopie "
            "NIE geloescht werden -- sonst stiller, irreversibler Datenverlust"
        )
        assert (_KB_ID, "file-a-in-kb") not in http.unlinked, (
            "die einzige Kopie darf bei ID-Kollision auch nicht entlinkt werden"
        )
        manifest = _manifest(tmp)
        assert manifest["kb_files"]["a.md"]["file_id"] == "file-a-in-kb", (
            "die erhaltene (einzige) file_id muss im Manifest stehen"
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
