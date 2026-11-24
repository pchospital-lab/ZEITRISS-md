#!/usr/bin/env python3
"""scripts/tests/test_setup_u4_outer_deadline_http_timeout_2026_11_24_r3.py --
ZR-PR3317-RESTNACHZUG-20261124-r3, U4 (UPDATE_UX_REVIEW.md "Rest U4").

Ursache (verifiziert am echten Code VOR diesem Fix): `_file_ready_deadline_s`
begrenzte NUR die Pollschleife (vormals setup.py ~1186-1214). Der Readiness-
GET rief `client.get_file` ohne Restfrist auf (vormals ~1082-1087, ~622-627);
`_request` nutzt Default 30s (vormals ~444-468). `add_file_to_knowledge`
behielt 360s bzw. den konfigurierten Wert (vormals ~582-612). Nach
erfolgreichem Readiness-Read wurde die verstrichene aeussere Frist vor dem
Link NICHT erneut geprueft (Reuse- wie Frischpfad). Ein kurzer positiver
Rest (z.B. aeussere Prozessfrist 16s) erlaubte dadurch trotzdem den vollen
regulaeren HTTP-Timeout (GET=30s/Link=360s) fuer einen EINZELNEN Request --
genau das vom `repro/update_r4_witness.py`-Fall `positive_outer_budget_http_
limits` dokumentierte, read-only belegte Verhalten am ungefixten Head.

Fix: `_remaining_outer_budget_s`/`_call_with_capped_timeout` (setup.py)
reichen den noch verbleibenden AEUSSEREN Prozessrest (`ZEITRISS_SYNC_OUTER_
DEADLINE_S`, dieselbe Env-Var wie der bestehende Pollschleifen-/Nullbudget-
Guard) jetzt bis zum einzelnen GET (`wait_for_file_ready`, ueber den bereits
vorhandenen `deadline_s`) und bis zum Link-POST (`add_file_to_knowledge`,
frisch VOR der Mutation neu berechnet, sowohl Reuse- als auch Frischpfad)
durch. `APIClient.get_file`/`add_file_to_knowledge` clampen den tatsaechlich
uebergebenen HTTP-Timeout auf `min(regulaerer_default, rest)`. Ohne
gesetzten aeusseren Rahmen (`ZEITRISS_SYNC_OUTER_DEADLINE_S` nicht gesetzt)
bleiben 30s/360s unveraendert.

Dieser Test treibt den ECHTEN `run_sync` mit gebundener aeusserer Frist und
den echten Methoden `APIClient.get_file`/`add_file_to_knowledge`/`_request`;
NUR `urllib.request.urlopen` ist ein rein lokaler Antwort-Double (identische
Grenze wie `repro/update_r4_witness.py`). Geprueft wird der an `urlopen`
tatsaechlich uebergebene `timeout`-Parameter fuer GET und Link, sowohl im
frischen Datei- als auch im Reuse-Pfad, plus der Gegenfall ohne gebundene
aeussere Frist (30s/360s bleiben). Kein echter HTTP-/Kindprozessaufruf."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock as mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

# Dieselbe dokumentierte Konvention wie test_setup_upd1_readiness_2026_11_23.py:
# `scripts/setup.py` fuegt sich beim Laden selbst vor den Repo-Root in
# sys.path ein -- den neu hinzugekommenen Pfadeintrag sofort nach dem Laden
# wieder entfernen, sonst findet ein SPAETER in DEMSELBEN Prozess entdecktes
# `import tests.mmo_sim` faelschlich `scripts/tests` statt des echten
# Top-Level-`tests/`-Pakets.
_sys_path_before_setup_exec = list(sys.path)
_spec = importlib.util.spec_from_file_location(
    "u4_r3_outer_deadline_http_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
for _p in list(sys.path):
    if _p not in _sys_path_before_setup_exec:
        sys.path.remove(_p)

_KB_ID = "kb-existing-1"


def _sync_cfg():
    return {
        "project": "Proj", "kb_name": "Proj Wissensspeicher", "masterprompt": "meta/masterprompt.md",
        "params": {}, "suggestions": [],
        "variants": {
            "default": {"preset_id": "p1", "preset_name": "Proj",
                        "model": "openrouter/deepseek/deepseek-v3.2", "cache": False},
        },
        "default_variant": "default",
    }


class _FakeAPIClientBase:
    """Minimaler Fake am aeusseren API-Rand -- `get_file`/`add_file_to_
    knowledge` werden pro Testklasse per Subclass auf die ECHTE `APIClient`
    umgeleitet (s. `Backend` unten); alles andere (Upload, Unlink, Delete,
    Content-Fallback) bleibt ein reiner In-Memory-Fake, identisch zur
    Konvention in `test_setup_upd1_readiness_2026_11_23.py`."""

    def __init__(self, *, existing_files, preset):
        self._existing_files = list(existing_files)
        self._preset = preset
        self.uploaded: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.unlinked: list[tuple[str, str]] = []
        self.deleted: list[str] = []
        self.last_add_file_code = None
        self.last_add_file_duplicate = None
        self._filename_of_id: dict[str, str] = {}
        self._next_id = 100

    def check_health(self):
        return True

    def check_auth(self):
        return True

    def get_model(self, model_id):
        return self._preset

    def upsert_model(self, payload):
        return True, "created"

    def list_files(self):
        return list(self._existing_files)

    def do_upload_file(self, filepath):
        self._next_id += 1
        new_id = f"file-new-{self._next_id}"
        self.uploaded.append(filepath.name)
        self._filename_of_id[new_id] = filepath.name
        return new_id

    def remove_file_from_knowledge(self, kb_id, file_id):
        self.unlinked.append((kb_id, file_id))
        return True

    def delete_file(self, file_id):
        self.deleted.append(file_id)
        self._existing_files = [f for f in self._existing_files if f.get("id") != file_id]
        return True

    def get_file_content(self, file_id):
        return None


class _ImmediateResponse:
    """`urlopen`-Context-Manager-Double -- sofortige Antwort, identisches
    Muster wie `repro/update_r4_witness.py`s `Response`."""

    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class Backend(_FakeAPIClientBase):
    """`get_file`/`add_file_to_knowledge` leiten auf die ECHTE `APIClient`
    um (`self._http`) -- NUR `urllib.request.urlopen` ist der lokale
    Antwort-Double (per `mock.patch` in `_run`). `outer_remaining_s` wird
    unveraendert durchgereicht, damit der Clamp in `APIClient.get_file`/
    `add_file_to_knowledge` tatsaechlich greift (ohne diese Durchreichung
    wuerde der Fake ihn stillschweigend verschlucken)."""

    def __init__(self, *, existing_files, preset, http):
        super().__init__(existing_files=existing_files, preset=preset)
        self._http = http

    def get_file(self, file_id, *, outer_remaining_s=None):
        return self._http.get_file(file_id, outer_remaining_s=outer_remaining_s)

    def add_file_to_knowledge(self, kb_id, file_id, *, outer_remaining_s=None):
        ok = self._http.add_file_to_knowledge(kb_id, file_id, outer_remaining_s=outer_remaining_s)
        self.last_add_file_code = self._http.last_add_file_code
        self.last_add_file_duplicate = self._http.last_add_file_duplicate
        self.linked.append((kb_id, file_id))
        if ok:
            for f in self._existing_files:
                if f.get("id") == file_id:
                    f["meta"] = {"collection_name": kb_id}
        return ok


class _OuterDeadlineHttpTimeoutBase(unittest.TestCase):
    """Gemeinsame Repo-/Env-Fixture fuer Frisch- und Reuse-Pfad."""

    def _write_repo(self, *, manifest_kb_files, content=b"NEU-INHALT"):
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_bytes(content)
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": manifest_kb_files,
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, make_client, *, outer_deadline=None, readiness_timeout="90"):
        """Baut die echte `APIClient` + den lokalen `urlopen`-Double
        (identisches Antwortmuster wie `repro/update_r4_witness.py`s
        `fake_urlopen`), haengt `calls` (Methode/Pfad/`timeout`) mit, und
        fuehrt `run_sync` ueber `make_client(http)` -> `Backend`."""
        http = setup_mod.APIClient("https://fixture.invalid", "SYNTHETIC-ONLY")
        calls: list[dict] = []

        def fake_urlopen(request, *, timeout, context):
            method = request.get_method()
            url = request.full_url
            calls.append({
                "method": method, "path": url.split("fixture.invalid", 1)[1],
                "timeout_s": timeout,
            })
            if method == "GET" and "/api/v1/files/" in url:
                fid = url.rsplit("/", 1)[-1]
                return _ImmediateResponse({"id": fid, "data": {"status": "completed", "content": "ready"}})
            if method == "POST" and url.endswith("/file/add"):
                return _ImmediateResponse({"ok": True})
            raise AssertionError(f"Unerwarteter Request an die blockierte HTTP-Grenze: {method} {url}")

        client = make_client(http)

        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = readiness_timeout
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        os.environ.pop("OWUI_ADD_FILE_TIMEOUT", None)
        if outer_deadline is not None:
            os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = outer_deadline
        else:
            os.environ.pop("ZEITRISS_SYNC_OUTER_DEADLINE_S", None)
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client), \
                 mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True, "assume_yes": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue(), calls, client
        finally:
            os.environ.clear()
            os.environ.update(saved)


class TestFreshUploadPathClampsGetAndLinkTimeout(_OuterDeadlineHttpTimeoutBase):
    """Frischer Datei-Pfad (vormals setup.py Upload ~5380/Readiness ~5401-
    5420/Link ~5434): kein Reuse-Kandidat sichtbar, `a.md` weicht vom
    Manifest ab -> echter Upload, dann Readiness-GET, dann Link-POST."""

    def setUp(self) -> None:
        self._write_repo(manifest_kb_files={
            "a.md": {"md5": hashlib.md5(b"ALT-INHALT").hexdigest(), "file_id": "file-a-old"},
        })

    def test_bound_outer_deadline_caps_get_and_link_http_timeout_below_default(self):
        ok, out, calls, client = self._run(
            lambda http: Backend(existing_files=[], preset=self.preset, http=http),
            outer_deadline="16",
        )
        self.assertTrue(ok, out)
        self.assertEqual(len(client.linked), 1)
        methods = [(c["method"], c["timeout_s"]) for c in calls]
        self.assertEqual(len(methods), 2, calls)
        get_timeout = next(c["timeout_s"] for c in calls if c["method"] == "GET")
        link_timeout = next(c["timeout_s"] for c in calls if c["method"] == "POST")
        self.assertLessEqual(get_timeout, 16.0, "GET-Timeout darf den regulären 30s-Default nicht mehr ausnutzen")
        self.assertLess(get_timeout, 30.0)
        self.assertLessEqual(link_timeout, 16.0, "Link-Timeout darf den regulären 360s-Default nicht mehr ausnutzen")
        self.assertLess(link_timeout, 360.0)

    def test_without_outer_deadline_env_keeps_the_regular_http_defaults(self):
        """Gegenfall (Abnahme U4): ohne gesetzten äußeren Rahmen bleiben
        30s/360s unverändert -- derselbe Vertrag wie vor diesem Nachzug."""
        ok, out, calls, client = self._run(
            lambda http: Backend(existing_files=[], preset=self.preset, http=http),
            outer_deadline=None,
        )
        self.assertTrue(ok, out)
        self.assertEqual([c["timeout_s"] for c in calls], [30.0, 360.0])


class TestReusedCandidatePathClampsGetAndLinkTimeout(_OuterDeadlineHttpTimeoutBase):
    """Reuse-Pfad (vormals setup.py Readiness ~5241-5266/Link ~5284-5289):
    ein sichtbarer, per Hash bestätigter, noch ungebundener Kandidat wird
    verlinkt -- KEIN Upload."""

    def setUp(self) -> None:
        self._write_repo(manifest_kb_files={}, content=b"NEU-INHALT")
        self._candidate_sha = hashlib.sha256(b"NEU-INHALT").hexdigest()

    def test_bound_outer_deadline_caps_get_and_link_http_timeout_below_default(self):
        ok, out, calls, client = self._run(
            lambda http: Backend(
                existing_files=[{
                    "id": "file-existing-101", "filename": "a.md",
                    "meta": {"file_hash": self._candidate_sha},
                }],
                preset=self.preset, http=http,
            ),
            outer_deadline="16",
        )
        self.assertTrue(ok, out)
        self.assertEqual(client.uploaded, [], "Reuse-Pfad -- kein zweiter Upload")
        self.assertEqual(len(client.linked), 1)
        self.assertEqual(len(calls), 2, calls)
        get_timeout = next(c["timeout_s"] for c in calls if c["method"] == "GET")
        link_timeout = next(c["timeout_s"] for c in calls if c["method"] == "POST")
        self.assertLessEqual(get_timeout, 16.0)
        self.assertLess(get_timeout, 30.0)
        self.assertLessEqual(link_timeout, 16.0)
        self.assertLess(link_timeout, 360.0)

    def test_without_outer_deadline_env_keeps_the_regular_http_defaults(self):
        ok, out, calls, client = self._run(
            lambda http: Backend(
                existing_files=[{
                    "id": "file-existing-101", "filename": "a.md",
                    "meta": {"file_hash": self._candidate_sha},
                }],
                preset=self.preset, http=http,
            ),
            outer_deadline=None,
        )
        self.assertTrue(ok, out)
        self.assertEqual([c["timeout_s"] for c in calls], [30.0, 360.0])


class TestExhaustedOuterBudgetClampsToFailFastNotDefault(unittest.TestCase):
    """U4-Randfall (Budget bereits ERSCHOEPFT): `_remaining_outer_budget_s`
    liefert via `max(0.0, outer_deadline_s - elapsed_s)` bei verbrauchtem
    aeusseren Rahmen literal `0.0`. Der Pro-Request-Clamp
    (`get_file`/`add_file_to_knowledge`/`upload_file`) rechnet dann
    `min(default, 0.0) = 0.0` und reicht `timeout=0.0` an `_request` durch.

    Dieser Test treibt die ECHTEN `APIClient`-Methoden (`get_file`,
    `add_file_to_knowledge`, `upload_file` -> echtes `_request`); nur
    `urllib.request.urlopen` ist der lokale Antwort-Double. Geprueft wird der
    an `urlopen` tatsaechlich uebergebene `timeout` -- er MUSS `0.0`
    (Fail-Fast im Erschoepfungsfall) sein, NICHT der volle Basisdefault.
    Am ungefixten Stand (`timeout or self.timeout`) faellt das falsy `0.0`
    lautlos auf `self.timeout` (30.0) zurueck -> Test schlaegt fehl
    (nicht-tautologisch)."""

    def _client_with_capture(self):
        http = setup_mod.APIClient("https://fixture.invalid", "SYNTHETIC-ONLY")
        seen: list[float] = []

        def fake_urlopen(request, *, timeout, context):
            seen.append(timeout)
            return _ImmediateResponse({"ok": True, "id": "f1", "data": {"status": "completed"}})

        return http, seen, fake_urlopen

    def test_get_file_zero_remainder_passes_zero_not_default(self):
        http, seen, fake_urlopen = self._client_with_capture()
        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            http.get_file("f1", outer_remaining_s=0.0)
        self.assertEqual(seen, [0.0],
                         "erschoepfter Rest (0.0) muss als 0.0-Timeout durchgereicht werden, "
                         "nicht auf den 30s-Default zurueckfallen")

    def test_add_file_zero_remainder_passes_zero_not_default(self):
        http, seen, fake_urlopen = self._client_with_capture()
        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            http.add_file_to_knowledge(_KB_ID, "f1", outer_remaining_s=0.0)
        self.assertEqual(seen, [0.0],
                         "erschoepfter Rest (0.0) muss als 0.0-Timeout durchgereicht werden, "
                         "nicht auf den 360s-Default zurueckfallen")

    def test_upload_file_zero_remainder_passes_zero_not_default(self):
        http, seen, fake_urlopen = self._client_with_capture()
        with tempfile.TemporaryDirectory() as d:
            fp = Path(d) / "a.md"
            fp.write_bytes(b"NEU-INHALT")
            with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                http.upload_file("/api/v1/files/", fp, outer_remaining_s=0.0)
        self.assertEqual(seen, [0.0],
                         "erschoepfter Rest (0.0) muss als 0.0-Timeout durchgereicht werden, "
                         "nicht auf den 120s-Upload-Default zurueckfallen")

    def test_none_remainder_keeps_regular_defaults(self):
        """Gegenfall: ohne aeusseren Rest (None) bleiben die regulaeren
        Defaults (GET 30 / Link 360 / Upload 120) unveraendert -- der Fix
        aendert NUR den exakt-Null-Fall."""
        http, seen, fake_urlopen = self._client_with_capture()
        saved = dict(os.environ)
        os.environ.pop("OWUI_UPLOAD_TIMEOUT", None)
        os.environ.pop("OWUI_ADD_FILE_TIMEOUT", None)
        try:
            with tempfile.TemporaryDirectory() as d:
                fp = Path(d) / "a.md"
                fp.write_bytes(b"NEU-INHALT")
                with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                    http.get_file("f1")
                    http.add_file_to_knowledge(_KB_ID, "f1")
                    http.upload_file("/api/v1/files/", fp)
        finally:
            os.environ.clear()
            os.environ.update(saved)
        self.assertEqual(seen, [30.0, 360.0, 120.0])


if __name__ == "__main__":
    unittest.main()
