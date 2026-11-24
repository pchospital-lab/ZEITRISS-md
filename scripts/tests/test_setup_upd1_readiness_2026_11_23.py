#!/usr/bin/env python3
"""scripts/tests/test_setup_upd1_readiness_2026_11_23.py —
ZR-UPDATE-RESUME-REPARATUR-20261123-r1, UPD-1 (03_UPDATE_UND_KB.md
Implementierungsauftrag 1, Abnahmefälle U1-U4).

Ursache (verifiziert am echten Code VOR diesem Fix): `setup.py:808-828`
(`do_upload_file`) liefert nach einem erfolgreichen Upload sofort die neue
File-ID zurück -- OHNE jede Prüfung, ob OpenWebUI den Inhalt bereits
extrahiert hat. Jeder Upload→Link-Caller (`complete_orphaned_kb_install`
~3904-3917/4028-4037, `run_sync` ~4738-4754, `run_setup` ~5820-5829, der
Coverage-Re-Link ~1659-1663) feuerte `add_file_to_knowledge` sofort danach,
im Fehlerfall gefolgt von GENAU EINEM blinden `time.sleep(1)` + Retry --
kein Zustandscheck, kein konfigurierbares Zeitbudget. Für die berichtete
asynchrone Verarbeitung (Upload sofort `id`, `data.content` wird ERST
verzögert nicht-leer) reicht das nicht.

Fix: `wait_for_file_ready()` (neu, setup.py) pollt GENAU das hochgeladene
File-Objekt (`GET /api/v1/files/{id}`, identitätsgebunden über die `id` im
Antwortkörper) bis `data` als dict vorliegt (Verarbeitung abgeschlossen)
UND `data.content` ein nicht-leerer String ist -- begrenzt (konfigurierbare
Deadline/Poll-Intervall), mit unterscheidbaren Terminalzuständen (ready /
pending_deadline / empty_content / auth_error / unreachable /
unknown_form). JEDER der vier Caller wartet jetzt darauf, BEVOR er
`add_file_to_knowledge` feuert.

Zwei Testebenen:
  1. `wait_for_file_ready` isoliert, mit vollständig injizierter Uhr
     (`sleep_fn`/`now_fn`) -- deterministisch, ohne echtes Warten.
  2. Die ECHTEN Caller `complete_orphaned_kb_install` und `run_sync` über
     einen Fake-API-Client (gleiche Konvention wie `test_f1_n4_orphaned_
     kb_completion_2026_11_10.py`/`test_r7_02_kb_sync_tracked_identity_
     confirm_2026_11_19.py`), mit winzigen Env-Var-Timeouts statt echtem
     Warten (`OWUI_FILE_READY_TIMEOUT`/`OWUI_FILE_READY_POLL_INTERVAL` --
     dieselben, am Call-Ort ausgelesenen Variablen, die ein echter Betrieb
     per Default auf 90 s/3 s setzt).

Double-Grenze: `_FakeAPIClient` ersetzt NUR die äußere API-Schicht
(check_health/do_upload_file/get_file/add_file_to_knowledge/remove_file_
from_knowledge/delete_file/list_files/upsert_model/get_model) -- die
getesteten Funktionen selbst (`wait_for_file_ready`, `complete_orphaned_
kb_install`, `run_sync`) laufen unverändert real gegen ein echtes
temporäres Repo. Kein Docker/Netzwerk-Call."""
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

# `scripts/setup.py` fuegt sich beim Laden selbst via `sys.path.insert(0,
# str(Path(__file__).resolve().parent))` vor den Repo-Root ein (dortiger
# ZR-LOCAL-TOKENHOST-L1-Kommentar) -- das laeuft beim `exec_module` unten
# mit. In einem GESAMTEN `python3 -m unittest -q`-Lauf ab Repo-Root bleibt
# dieser Pfadeintrag danach fuer den REST des Prozesses stehen: `scripts/
# tests/` hat ein eigenes `__init__.py`, also wuerde ein SPAETER entdecktes
# `import tests.mmo_sim` dann `scripts/tests` statt des echten Top-Level-
# `tests/`-Pakets finden (`ModuleNotFoundError: No module named 'tests.
# mmo_sim'` in VOELLIG unabhaengigen Testdateien -- lokal reproduziert).
# Dieselbe, bereits an anderer Stelle dokumentierte Konvention wie
# `scripts/tests/test_launcher_action_update.py`: den neu hinzugekommenen
# Pfadeintrag sofort nach dem Laden wieder entfernen.
_sys_path_before_setup_exec = list(sys.path)
_spec = importlib.util.spec_from_file_location(
    "upd1_readiness_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
for _p in list(sys.path):
    if _p not in _sys_path_before_setup_exec:
        sys.path.remove(_p)


# ── Ebene 1: `wait_for_file_ready` isoliert, injizierte Uhr ────────────

class _FakeReadinessClient:
    """Nur `get_file` -- `wait_for_file_ready` braucht sonst nichts."""

    def __init__(self, responses: list):
        self._responses = list(responses)
        self.calls = 0

    def get_file(self, file_id):
        self.calls += 1
        if len(self._responses) > 1:
            return self._responses.pop(0)
        return self._responses[0]


class _FakeClock:
    """Jeder `sleep_fn`-Aufruf rückt die Uhr um den angeforderten Betrag
    vor -- deterministisch, ohne echtes Warten."""

    def __init__(self):
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.t += s


class TestWaitForFileReadyIsolated(unittest.TestCase):
    def test_u1_ready_after_delay_polls_until_content_non_empty(self):
        clock = _FakeClock()
        client = _FakeReadinessClient([
            (200, {"id": "f1", "data": {"status": "pending"}}),
            (200, {"id": "f1", "data": {"status": "pending"}}),
            (200, {"id": "f1", "data": {"status": "completed", "content": "Inhalt da"}}),
        ])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertTrue(r.ready)
        self.assertEqual(r.status, "ready")
        self.assertEqual(client.calls, 3)

    def test_u2_never_ready_terminates_at_deadline_not_endless(self):
        clock = _FakeClock()
        client = _FakeReadinessClient([(200, {"id": "f1", "data": {"status": "pending"}})])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=3.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "pending_deadline")
        # Endliche Anzahl Polls, kein Endlospolling.
        self.assertLessEqual(client.calls, 6)

    def test_empty_content_after_processing_done_is_a_distinct_terminal_error(self):
        """Design-Vorgabe: 'EMPTY_CONTENT nach nachgewiesener Bereitschaft
        bleibt ein echter Fehler' -- abgeschlossene Verarbeitung (`data`
        ist ein dict) MIT leerem `content` ist NICHT dasselbe wie
        `pending_deadline` (noch laufende Verarbeitung) und endet SOFORT,
        ohne die Deadline abzuwarten."""
        clock = _FakeClock()
        client = _FakeReadinessClient([(200, {"id": "f1", "data": {"status": "completed", "content": ""}})])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "empty_content")
        self.assertEqual(client.calls, 1, "terminal -- kein weiteres Polling nötig")

    def test_n02_dict_pending_is_not_falsely_treated_as_complete(self):
        """N02/U-R1 (ZR-PR3317-Nachzug): der eigentliche Bug -- OWUI v0.11.3 legt
        die Datei SOFORT mit data={"status":"pending"} (ein DICT!) an. Der alte
        Helper wertete jedes data-dict als abgeschlossen und meldete nach EINEM
        GET faelschlich empty_content. Jetzt muss der pending-Zustand abgewartet
        und der spaetere completed-Inhalt erreicht werden."""
        clock = _FakeClock()
        client = _FakeReadinessClient([
            (200, {"id": "f1", "data": {"status": "pending"}}),
            (200, {"id": "f1", "data": {"status": "pending", "content": ""}}),
            (200, {"id": "f1", "data": {"status": "completed", "content": "endlich da"}}),
        ])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertTrue(r.ready, r)
        self.assertEqual(r.status, "ready")
        self.assertEqual(client.calls, 3, "pending-dict darf NICHT nach 1 GET terminieren")

    def test_n02_failed_with_partial_content_is_terminal_not_ready(self):
        """N02/U-R1: status=failed ist terminal -- auch wenn daneben Teilcontent
        stehengeblieben ist (models/files.py:370-378). Der alte Helper haette den
        Teiltext faelschlich als ready akzeptiert."""
        clock = _FakeClock()
        client = _FakeReadinessClient([
            (200, {"id": "f1", "data": {"status": "failed", "content": "halber Text", "error": "boom"}}),
        ])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready, r)
        self.assertEqual(r.status, "failed")
        self.assertEqual(client.calls, 1, "explizites failed ist terminal -- kein Polling")

    def test_legacy_form_without_status_but_content_is_ready(self):
        """N02/U-R1 Gegenfall: eine aeltere unterstuetzte Antwortform OHNE
        Statusfeld, aber mit nicht-leerem Inhalt, bleibt ein positiver
        Abschlussbeleg -> ready (keine Regression fuer Legacy-Backends)."""
        clock = _FakeClock()
        client = _FakeReadinessClient([(200, {"id": "f1", "data": {"content": "Legacy-Inhalt"}})])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertTrue(r.ready, r)
        self.assertEqual(r.status, "ready")
        self.assertEqual(client.calls, 1)

    def test_auth_error_is_immediate_and_distinct_from_pending(self):
        clock = _FakeClock()
        client = _FakeReadinessClient([(401, {"detail": "unauthorized"})])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "auth_error")
        self.assertEqual(client.calls, 1)

    def test_unreachable_is_transient_until_deadline_then_terminal(self):
        clock = _FakeClock()
        client = _FakeReadinessClient([(0, b"Connection refused")])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=2.5, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "unreachable")
        self.assertGreater(client.calls, 1, "Netzfehler wird bis zur Deadline als transient behandelt")

    def test_unknown_form_on_id_mismatch_does_not_guess(self):
        clock = _FakeClock()
        client = _FakeReadinessClient([(200, {"id": "SOME-OTHER-FILE", "data": {"content": "x"}})])
        r = setup_mod.wait_for_file_ready(
            client, "f1", deadline_s=10.0, poll_interval_s=1.0,
            sleep_fn=clock.sleep, now_fn=clock.now,
        )
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "unknown_form")
        self.assertEqual(client.calls, 1, "terminal -- eine fremde Antwort wird nicht weggepollt")

    def test_duplicate_signal_is_untouched_by_readiness_wait(self):
        """Abgrenzung: Duplicate-Content ist Sache von `add_file_to_
        knowledge` (`last_add_file_duplicate`), NICHT von `wait_for_file_
        ready` -- die Readiness-Wait kennt dieses Signal gar nicht."""
        self.assertNotIn("duplicate", {
            "ready", "pending_deadline", "empty_content", "auth_error",
            "unreachable", "unknown_form",
        })


# ── Ebene 2: echte Caller (complete_orphaned_kb_install, run_sync) ─────

_KB_ID = "kb-existing-1"


class _FakeAPIClient:
    """Fake NUR am äußeren API-Rand (gleiche Konvention wie
    `test_f1_n4_orphaned_kb_completion_2026_11_10.py`), um `readiness_mode`
    pro Dateiname erweitert."""

    def __init__(self, *, existing_files=None, readiness_mode=None,
                 preset=None, link_fails_for=(), link_fail_kind=None,
                 unlink_fails_for=()):
        self._existing_files = list(existing_files or [])
        self._readiness_mode = dict(readiness_mode or {})
        self._preset = preset
        self._link_fails_for = set(link_fails_for)
        # U4 (ZR-PR3317-Nachzug 20261123): je Dateiname "unclear" (Transport-
        # fehler, last_add_file_code=0, keine Serverantwort) oder "definitive"
        # (echter HTTP-Fehlercode) -- Default "definitive" fuer bestehende
        # Fixtures, die diesen Parameter nicht setzen.
        self._link_fail_kind = dict(link_fail_kind or {})
        self._unlink_fails_for = set(unlink_fails_for)
        self.uploaded: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.unlinked: list[tuple[str, str]] = []
        self.deleted: list[str] = []
        self.last_add_file_code = None
        self._filename_of_id: dict[str, str] = {}
        self._get_file_calls: dict[str, int] = {}
        self._next_id = 100

    # -- gemeinsame Oberfläche --
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

    def get_file(self, file_id):
        self._get_file_calls[file_id] = self._get_file_calls.get(file_id, 0) + 1
        n = self._get_file_calls[file_id]
        fname = self._filename_of_id.get(file_id, file_id)
        mode = self._readiness_mode.get(fname, "immediate")
        # N02/U-R1 (ZR-PR3317-Nachzug): gebundene OWUI-v0.11.3-Zustaende. "pending"
        # wird als DICT mit status abgebildet (der echte Bugausloeser -- ein
        # data-dict beweist KEINEN Abschluss), nicht mehr als data=None.
        if mode == "immediate":
            return 200, {"id": file_id, "data": {"status": "completed", "content": "extrahierter Inhalt"}}
        if mode == "legacy_ready":
            # Aeltere unterstuetzte Form OHNE Statusfeld, aber mit Inhalt -> ready.
            return 200, {"id": file_id, "data": {"content": "extrahierter Inhalt"}}
        if mode == "never":
            # Dauerhaft pending als DICT (echte async-Form) -> muss bis Deadline pollen.
            return 200, {"id": file_id, "data": {"status": "pending"}}
        if mode == "failed":
            # Explizites Scheitern mit stehengebliebenem Teilcontent -> terminal, NICHT ready.
            return 200, {"id": file_id, "data": {"status": "failed", "content": "halber Text", "error": "extraction boom"}}
        if mode == "empty_after_done":
            return 200, {"id": file_id, "data": {"status": "completed", "content": ""}}
        if mode.startswith("delay:"):
            threshold = int(mode.split(":", 1)[1])
            if n < threshold:
                return 200, {"id": file_id, "data": {"status": "pending"}}
            return 200, {"id": file_id, "data": {"status": "completed", "content": "extrahierter Inhalt"}}
        return 200, {"id": file_id, "data": {"status": "completed", "content": "extrahierter Inhalt"}}

    def add_file_to_knowledge(self, kb_id, file_id):
        fname = self._filename_of_id.get(file_id, file_id)
        self.linked.append((kb_id, file_id))
        if fname in self._link_fails_for:
            # U4: "unclear" bildet einen reinen Transportfehler ab (keine
            # Serverantwort, code=0) -- "definitive" einen echten vom Server
            # bestaetigten Fehlercode (z.B. 422). Nur "unclear" darf einen
            # blinden Delete der neuen File-Entity verhindern.
            kind = self._link_fail_kind.get(fname, "definitive")
            self.last_add_file_code = 0 if kind == "unclear" else 422
            return False
        self.last_add_file_code = 200
        for f in self._existing_files:
            if f.get("id") == file_id:
                f["meta"] = {"collection_name": kb_id}
        return True

    def remove_file_from_knowledge(self, kb_id, file_id):
        self.unlinked.append((kb_id, file_id))
        if file_id in self._unlink_fails_for:
            return False
        return True

    def delete_file(self, file_id):
        self.deleted.append(file_id)
        self._existing_files = [f for f in self._existing_files if f.get("id") != file_id]
        return True

    def get_file_content(self, file_id):
        # U2 (ZR-PR3317-RESTNACHZUG-20261124): Content-Fallback-Rand fuer
        # `_confirm_active_kb_file_by_content` -- Default "nicht lesbar"
        # (None), da keine der bisherigen Fixtures echten Rohinhalt braucht.
        return None


def _build_repo(tmp: Path, *, filenames=("a.md",), content="AKTUELLER-INHALT") -> None:
    (tmp / "kb").mkdir()
    for name in filenames:
        (tmp / "kb" / name).write_text(content, encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


_ORPHAN_CFG = {
    "project": "Proj", "kb_name": "Proj Wissensspeicher", "masterprompt": "meta/masterprompt.md",
    "params": {}, "suggestions": [],
    "variants": {
        "default": {"preset_id": "p1", "preset_name": "Proj",
                    "model": "openrouter/deepseek/deepseek-v3.2", "cache": False},
    },
}


def _run_orphan(tmp: Path, client: "_FakeAPIClient", *, readiness_timeout="0.3", readiness_poll="0.01"):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OWUI_FILE_READY_TIMEOUT"] = readiness_timeout
    os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = readiness_poll
    try:
        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", return_value=client):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                ok = setup_mod.complete_orphaned_kb_install(tmp, _ORPHAN_CFG, _KB_ID)
            return ok, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _manifest(tmp: Path) -> dict:
    with open(tmp / ".openwebui-sync.json", encoding="utf-8") as f:
        return json.load(f)


class TestCompleteOrphanedKbInstallRealCallerReadiness(unittest.TestCase):
    """U1/U2 am ECHTEN `complete_orphaned_kb_install`-Aufrufer (Anker
    setup.py:3904-3917 -- Replace-Zweig einer bereits abweichenden,
    verlinkten Altdatei)."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        _build_repo(self.tmp, filenames=("a.md",), content="AKTUELLER-INHALT")

    def _seed_existing(self):
        # Bereits verlinkte, aber INHALTLICH ABWEICHENDE Altdatei -- zwingt
        # den Replace-Zweig (kein Content-Hash-Match).
        return [{
            "id": "file-a-old", "filename": "a.md",
            "meta": {"collection_name": _KB_ID, "file_hash": "deadbeef" * 8},
        }]

    def test_u1_delayed_readiness_then_link_succeeds_old_version_removed(self):
        client = _FakeAPIClient(
            existing_files=self._seed_existing(),
            readiness_mode={"a.md": "delay:3"},
        )
        ok, out = _run_orphan(self.tmp, client)
        self.assertTrue(ok, out)
        self.assertEqual(client.uploaded, ["a.md"])
        self.assertEqual(len(client.linked), 1, "genau EIN Link-Versuch -- erst NACH bestätigter Readiness")
        self.assertIn((_KB_ID, "file-a-old"), client.unlinked, "Altbestand wird nach bestätigtem Ersatz entlinkt")
        self.assertIn("file-a-old", client.deleted, "Altbestand wird erst NACH bestätigtem Ersatz entfernt")
        new_id = next(f for f, name in client._filename_of_id.items() if name == "a.md")
        manifest = _manifest(self.tmp)
        self.assertEqual(manifest["kb_files"]["a.md"]["file_id"], new_id)

    def test_u2_never_ready_preserves_old_version_no_premature_link(self):
        client = _FakeAPIClient(
            existing_files=self._seed_existing(),
            readiness_mode={"a.md": "never"},
        )
        ok, out = _run_orphan(self.tmp, client)
        self.assertFalse(ok, "ein nie bereiter Inhalt darf NICHT als vollständig gemeldet werden")
        self.assertEqual(client.linked, [], "KEIN Link-Versuch, solange der Inhalt nicht bereit ist")
        self.assertEqual(client.unlinked, [], "der Altbestand wird NICHT angefasst")
        new_id = next(iter(client._filename_of_id), None)
        if new_id is not None:
            self.assertIn(new_id, client.deleted, "die verwaiste NEUE (nie verlinkte) File-Entity wird aufgeräumt")
        manifest = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest.get("kb_files", {}), "kein falsches Manifest-PASS")

    def test_u3_empty_content_after_processing_is_reported_distinctly_and_old_version_untouched(self):
        """U3-Teilbeleg am echten Caller: eine explizit leere Extraktion
        (Verarbeitung fertig, Inhalt leer) wird NICHT als "KB leer"/Reset
        interpretiert, sondern bleibt eine konkrete, auf die Einzeldatei
        bezogene Meldung -- der Altbestand bleibt dabei unangetastet (die
        isolierte auth_error-/unreachable-Klassifikation ist bereits in
        `TestWaitForFileReadyIsolated` bewiesen)."""
        client = _FakeAPIClient(
            existing_files=self._seed_existing(),
            readiness_mode={"a.md": "empty_after_done"},
        )
        ok, out = _run_orphan(self.tmp, client)
        self.assertFalse(ok)
        self.assertIn("empty_content", out)
        self.assertEqual(client.linked, [])
        self.assertEqual(client.unlinked, [], "Altbestand bleibt bei explizit leerer Extraktion unangetastet")


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


class TestRunSyncRealCallerReadinessAndMachineSummary(unittest.TestCase):
    """U1/U2 UND UPD-2s `SYNC_RESULT`-Zeile am ECHTEN `run_sync`-Aufrufer
    (Anker setup.py:4738-4754)."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("NEU-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {"a.md": {"md5": hashlib.md5(b"ALT-INHALT").hexdigest(), "file_id": "file-a-old"}},
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, client, **env):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = env.get("readiness_timeout", "0.3")
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = env.get("readiness_poll", "0.01")
        if "outer_deadline" in env:
            os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = env["outer_deadline"]
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True, "assume_yes": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_u1_real_sync_waits_then_links_and_emits_true_sync_result(self):
        client = _FakeAPIClient(
            existing_files=[],
            readiness_mode={"a.md": "delay:3"},
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        self.assertEqual(client.uploaded, ["a.md"])
        self.assertEqual(len(client.linked), 1)
        self.assertIn("SYNC_RESULT ", out)
        self.assertIn("kb_total=1 kb_confirmed=1 kb_failed=", out)
        self.assertNotIn("kb_failed=a.md", out)

    def test_u4_real_product_phase_text_appears_before_each_long_step(self):
        """U4 (UPDATE_UX_REVIEW.md U4, 02_RESTAUFTRAG.md §U4): echter
        Produkttext VOR den langen Upload-/Readiness-/Link-Schritten -- der
        bisherige Streamingtest bewies nur den Transport geschriebener
        Fixturezeilen, NICHT das Vorhandensein dieser Phasen im Produkt-
        caller selbst. Hier läuft der ECHTE `run_sync`-Aufrufer; die drei
        Phasentexte müssen in der richtigen Reihenfolge VOR ihrem jeweiligen
        Ergebnis erscheinen (nicht nur danach)."""
        client = _FakeAPIClient(
            existing_files=[],
            readiness_mode={"a.md": "delay:2"},
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        new_id = next(iter(client._filename_of_id), None)
        self.assertIsNotNone(new_id)
        upload_pos = out.index("a.md: Upload startet")
        wait_pos = out.index("a.md: warte auf Verarbeitungsbereitschaft")
        link_pos = out.index("a.md: verknüpfe mit Knowledge Base")
        linked_result_pos = out.index(f"— neu {new_id[:12]}")
        self.assertLess(upload_pos, wait_pos, "Upload-Phasentext muss vor dem Readiness-Wait stehen")
        self.assertLess(wait_pos, link_pos, "Readiness-Phasentext muss vor dem Link-Versuch stehen")
        self.assertLess(link_pos, linked_result_pos, "Link-Phasentext muss vor dem Link-Ergebnis stehen")

    def test_u2_real_sync_never_ready_preserves_old_and_reports_pending_failure(self):
        client = _FakeAPIClient(
            existing_files=[],
            readiness_mode={"a.md": "never"},
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertFalse(ok, "ein nie bereiter Inhalt darf den Sync nicht als Erfolg melden")
        self.assertEqual(client.linked, [], "kein Link-Versuch ohne bestätigte Readiness")
        self.assertIn("pending_deadline", out)
        self.assertIn("kb_failed=a.md", out)
        manifest = _manifest(self.tmp)
        self.assertEqual(
            manifest["kb_files"]["a.md"]["file_id"], "file-a-old",
            "der alte Manifest-Eintrag bleibt stehen -- kein falsches Manifest-PASS, "
            "naechster --sync wiederholt gezielt NUR diese Datei",
        )

    def test_u4_outer_deadline_caps_per_file_readiness_wait(self):
        """U4 (UPDATE_UX_REVIEW.md R4/U4, 02_RESTAUFTRAG.md §U4): ohne das
        fast erschöpfte ÄUSSERE Prozessbudget (`ZEITRISS_SYNC_OUTER_
        DEADLINE_S`, vom Launcher gesetzt) zu kennen, würde `wait_for_file_
        ready` seinen eigenen, davon unabhängigen `OWUI_FILE_READY_TIMEOUT`
        (hier 0.3s) ausschöpfen -- bei VIELEN Dateien in einem großen Sync
        könnte das den äußeren Rahmen überlaufen. Mit (nahezu) erschöpftem
        äußerem Budget darf GAR KEIN neuer Readiness-/Link-Request mehr
        starten (U4-Restnachzug: vorher erfolgte noch EIN GET, dessen
        sofortiges "completed" den anschließenden Link mit vollem 360s-
        Timeout erlaubt hätte, obwohl der äußere Prozess jederzeit hart
        beendet werden kann -- `get_file` wird jetzt GAR NICHT mehr
        aufgerufen, kein neuer mutierender Request startet)."""
        client = _FakeAPIClient(
            existing_files=[],
            readiness_mode={"a.md": "never"},
            preset=self.preset,
        )
        # 1s äußeres Budget minus der 15s-Sicherheitsmarge in
        # `_file_ready_deadline_s` -> rechnerisch bereits deutlich negativ,
        # der Datei-Deadline wird auf 0.0 gekappt.
        ok, out = self._run(client, outer_deadline="1")
        self.assertFalse(ok)
        self.assertIn("äußeres Prozessbudget bereits erschöpft", out)
        self.assertIn("kein neuer Readiness-/Link-Versuch", out)
        new_id = next(iter(client._filename_of_id), None)
        self.assertIsNotNone(new_id)
        self.assertNotIn(
            new_id, client._get_file_calls,
            "bei bereits erschöpftem äußerem Budget darf KEIN neuer GET-Request "
            "mehr starten (nicht einmal ein einziger Poll)",
        )
        self.assertIn(new_id, client.deleted, "verwaiste neue File-Entity wird trotzdem aufgeräumt")
        self.assertEqual(client.linked, [], "kein Link-Versuch mit erschöpftem Budget")

    def test_u4_without_outer_deadline_env_behaves_exactly_as_before(self):
        """Gegenfall: ohne gesetzte `ZEITRISS_SYNC_OUTER_DEADLINE_S` (z.B.
        direkter CLI-Aufruf von `setup.py --sync` ohne Launcher) bleibt das
        Verhalten unverändert -- derselbe Positivfall wie `test_u1_real_
        sync_waits_then_links_and_emits_true_sync_result`, nur zur
        Abgrenzung hier erneut mit explizit NICHT gesetzter Env-Var."""
        self.assertNotIn("ZEITRISS_SYNC_OUTER_DEADLINE_S", os.environ)
        client = _FakeAPIClient(
            existing_files=[], readiness_mode={"a.md": "delay:3"}, preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        self.assertEqual(len(client.linked), 1)


# ── U4 (ZR-PR3317-Nachzug 20261123): unklarer Linkausgang nicht mehr ──────
# destruktiv behandelt. `add_file_to_knowledge` (setup.py) reduzierte jeden
# Nicht-200-Ausgang auf `False`; ein reiner Transportfehler (last_add_file_
# code=0, keine Serverantwort) wurde dadurch wie ein echter Link-Fehler
# behandelt -- der Caller loeschte die neue File-Entity blind, obwohl der
# Server den Link bereits serverseitig gesetzt haben kann, bevor die Antwort
# verlorenging.

class TestCompleteOrphanedKbInstallUnclearLinkOutcome(unittest.TestCase):
    """Replace-Zweig (bereits verlinkte, inhaltlich abweichende Altdatei) --
    derselbe Caller wie `TestCompleteOrphanedKbInstallRealCallerReadiness`."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        _build_repo(self.tmp, filenames=("a.md",), content="AKTUELLER-INHALT")

    def _seed_existing(self):
        return [{
            "id": "file-a-old", "filename": "a.md",
            "meta": {"collection_name": _KB_ID, "file_hash": "deadbeef" * 8},
        }]

    def test_u4_unclear_transport_failure_preserves_new_file_no_blind_delete(self):
        """VORHER (Bug): jeder Nicht-200-Ausgang von `add_file_to_knowledge`
        loeste denselben Delete aus wie ein echter Link-Fehler -- auch bei
        last_add_file_code=0 (keine Serverantwort, der Server kann den Link
        trotzdem gesetzt haben). Altbestand UND neue Datei muessen hier
        unangetastet bleiben, keine automatische Loeschung auf Verdacht."""
        client = _FakeAPIClient(
            existing_files=self._seed_existing(),
            link_fails_for={"a.md"}, link_fail_kind={"a.md": "unclear"},
        )
        ok, out = _run_orphan(self.tmp, client)
        self.assertFalse(ok, "unklarer Ausgang darf nicht als bestätigt vollständig gelten")
        new_id = next(iter(client._filename_of_id), None)
        self.assertIsNotNone(new_id)
        self.assertNotIn(new_id, client.deleted, "neue File-Entity darf bei unklarem Ausgang NICHT gelöscht werden")
        self.assertNotIn("file-a-old", client.deleted, "Altbestand bleibt bei unklarem Ausgang unangetastet")
        self.assertEqual(client.unlinked, [], "kein Unlink-Versuch auf den Altbestand")
        self.assertIn("Unklar", out)
        self.assertIn("Transportfehler", out)
        self.assertIn("NICHT gelöscht", out)
        manifest = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest.get("kb_files", {}), "kein falsches Manifest-PASS bei unklarem Ausgang")

    def test_u4_definitive_link_error_still_deletes_the_orphaned_new_file(self):
        """Gegenfall: ein ECHTER, vom Server bestätigter Fehlercode (hier
        422) bleibt ein klarer Link-Fehler -- die verwaiste neue File-Entity
        wird weiterhin aufgeräumt. Beweist, dass die U4-Ausnahme NUR den
        Transportfehler-Fall (code=0) betrifft, nicht jeden Link-Fehler."""
        client = _FakeAPIClient(
            existing_files=self._seed_existing(),
            link_fails_for={"a.md"}, link_fail_kind={"a.md": "definitive"},
        )
        ok, out = _run_orphan(self.tmp, client)
        self.assertFalse(ok)
        new_id = next(iter(client._filename_of_id), None)
        self.assertIsNotNone(new_id)
        self.assertIn(new_id, client.deleted, "ein echter Link-Fehler räumt die verwaiste neue Entity weiterhin auf")
        self.assertNotIn("Transportfehler", out)


class TestRunSyncUnclearLinkOutcome(unittest.TestCase):
    """Derselbe U4-Fall am echten `run_sync`-Hauptpfad (neue Datei, kein
    bereits verlinkter Altbestand -- Anker setup.py 'echter Link-Fehler')."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("NEU-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {},
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = "0.3"
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_u4_real_sync_unclear_link_outcome_preserves_new_file(self):
        client = _FakeAPIClient(
            existing_files=[], preset=self.preset,
            link_fails_for={"a.md"}, link_fail_kind={"a.md": "unclear"},
        )
        ok, out = self._run(client)
        self.assertFalse(ok, "unklarer Linkausgang darf den Sync nicht als Erfolg melden")
        new_id = next(iter(client._filename_of_id), None)
        self.assertIsNotNone(new_id)
        self.assertNotIn(new_id, client.deleted, "neue File-Entity darf bei unklarem Ausgang NICHT gelöscht werden")
        self.assertIn("Unklar", out)
        self.assertIn("Transportfehler", out)
        manifest = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest.get("kb_files", {}))


# ── U6 (ZR-PR3317-Nachzug 20261123): Unlinkfehler im Entfernen-Pfad ───────
# ist jetzt ein Halt. `run_sync` Abschnitt "2b. Entfernte Dateien" ignorierte
# bisher die Rückgabe von `remove_file_from_knowledge`, löschte die Entity
# trotzdem und strich den Manifesteintrag -- ein fehlgeschlagenes Unlink
# blieb unsichtbar still (anders als der bereits korrekt behandelte
# Ersatzpfad für geänderte Dateien).

class TestRunSyncRemovedFileUnlinkFailureIsAHalt(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("AKTUELLER-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {
                "a.md": {"md5": hashlib.md5(b"AKTUELLER-INHALT").hexdigest(), "file_id": "file-a"},
                "removed.md": {"md5": "irrelevant", "file_id": "file-removed"},
            },
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = "0.3"
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_u6_unlink_failure_on_removed_file_is_a_halt_not_silent_delete(self):
        client = _FakeAPIClient(existing_files=[], preset=self.preset, unlink_fails_for={"file-removed"})
        ok, out = self._run(client)
        self.assertFalse(ok, "ein fehlgeschlagenes Unlink darf den Sync nicht als Erfolg melden")
        self.assertIn(("kb-existing-1", "file-removed"), client.unlinked, "Unlink wurde versucht")
        self.assertNotIn("file-removed", client.deleted, "KEIN Delete nach fehlgeschlagenem Unlink")
        self.assertIn("Unlink fehlgeschlagen", out)
        self.assertIn("removed.md", out)
        manifest = _manifest(self.tmp)
        self.assertEqual(
            manifest["kb_files"]["removed.md"]["file_id"], "file-removed",
            "Manifesteintrag bleibt stehen -- kein stilles Entfernen bei fehlgeschlagenem Unlink",
        )
        # U3 (UPDATE_UX_REVIEW.md R3, 02_RESTAUFTRAG.md §U3): "removed.md" ist
        # NICHT mehr Teil des lokalen Solls (nur "a.md" liegt in kb/) -- VORHER
        # fiel der Name aus `explicit_failed & expected` heraus und verschwand
        # komplett aus der SYNC_RESULT-Zeile (stiller Aufräumrest). Er MUSS
        # jetzt in `kb_failed=` sichtbar bleiben, ohne `kb_total`/`kb_confirmed`
        # (die sich nur auf den aktuellen Soll-Umfang beziehen) zu verzerren.
        sync_result_line = next(
            line for line in out.splitlines() if line.startswith("SYNC_RESULT ")
        )
        self.assertIn("kb_total=1", sync_result_line, sync_result_line)
        self.assertIn("kb_confirmed=1", sync_result_line, sync_result_line)
        self.assertIn("removed.md", sync_result_line.split("kb_failed=", 1)[1])

    def test_u6_successful_unlink_still_removes_as_before(self):
        """Gegenfall: ein erfolgreicher Unlink entfernt weiterhin wie vorher."""
        client = _FakeAPIClient(existing_files=[], preset=self.preset)
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        self.assertIn("file-removed", client.deleted)
        manifest = _manifest(self.tmp)
        self.assertNotIn("removed.md", manifest.get("kb_files", {}))


# ── U2 (ZR-PR3317-RESTNACHZUG-20261124, UPDATE_UX_REVIEW.md R2) ──────────
# Der erste fehlerhafte Link löscht den Kandidaten jetzt korrekt nicht
# (siehe `TestRunSyncUnclearLinkOutcome` oben). Die ID wurde aber bisher
# NICHT als offener Zusammenhang wieder aufgenommen: der Kandidatenindex
# (setup.py ~4723-4740) berücksichtigte nur bereits AKTIVE KB-Bindungen --
# ein sichtbarer, passender, noch UNGEBUNDENER Kandidat fiel heraus, der
# Caller erreichte erneut `do_upload_file` (~5067-5068). Reproduziert mit
# ZWEI nacheinander ausdrücklich aufgerufenen `run_sync`-Durchläufen auf
# derselben Fixture, exakt wie im Review-Nachweis gefordert.

class TestRunSyncSecondSyncReusesUnboundCandidate(unittest.TestCase):
    """Zweiter Sync nach unklarem erstem Linkausgang -- erhaltener
    Kandidat muss geklärt/verlinkt werden, KEIN zweiter Upload."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("NEU-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {},
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = "0.3"
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_u2_second_sync_relinks_preserved_candidate_without_second_upload(self):
        # Lauf 1: Linkausgang unklar (Transportfehler, code=0) -- Kandidat
        # wird laut bereits behobenem B2/U4-Fix NICHT gelöscht.
        client1 = _FakeAPIClient(
            existing_files=[], preset=self.preset,
            link_fails_for={"a.md"}, link_fail_kind={"a.md": "unclear"},
        )
        ok1, out1 = self._run(client1)
        self.assertFalse(ok1, "unklarer Linkausgang darf Lauf 1 nicht als Erfolg melden")
        new_id = next(iter(client1._filename_of_id), None)
        self.assertIsNotNone(new_id)
        self.assertNotIn(new_id, client1.deleted, "Kandidat aus Lauf 1 bleibt erhalten (B2/U4)")
        manifest_after_1 = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest_after_1.get("kb_files", {}), "kein falsches Manifest-PASS nach Lauf 1")

        # Lauf 2: derselbe Kandidat ist jetzt laut Backend sichtbar (gleicher
        # Dateiname, nachweislich identischer Inhalt per SHA-256), aber WEITER
        # UNGEBUNDEN (leeres `collection_name`). Das ist der bereits
        # akzeptierte LEERE-Collection-Positivfall (01_ABNAHMESTAND.md U2
        # Teilfall) -- NICHT identisch mit dem ursprünglichen Review-Witness,
        # der stattdessen `collection_name == file_id` (die rohe "own"-Form,
        # s. `TestRunSyncOriginalOwnCollectionCandidateForm` unten) verwendet.
        # Diesmal gelingt der Link.
        local_sha = hashlib.sha256(b"NEU-INHALT").hexdigest()
        client2 = _FakeAPIClient(
            existing_files=[{
                "id": new_id, "filename": "a.md",
                "meta": {"file_hash": local_sha},
            }],
            preset=self.preset,
        )
        ok2, out2 = self._run(client2)
        self.assertTrue(ok2, out2)
        self.assertEqual(client2.uploaded, [], "KEIN zweiter Upload derselben offenen Änderung")
        self.assertEqual(client2.linked, [(_KB_ID, new_id)], "genau DIESE erhaltene ID wird verlinkt")
        self.assertEqual(client2.deleted, [], "kein Delete -- weder Kandidat noch (nicht vorhandene) Altversion")
        self.assertIn("erhaltener Kandidat", out2)
        self.assertIn("kein erneuter Upload", out2)
        manifest_after_2 = _manifest(self.tmp)
        self.assertEqual(manifest_after_2["kb_files"]["a.md"]["file_id"], new_id)

    def test_u2_second_sync_with_genuinely_unresolved_candidate_stays_open_no_second_upload(self):
        """Gegenfall (Scope-Grenze, korrigiert laut UPDATE_UX_REVIEW.md R2):
        der sichtbare, gleichnamige Kandidat ist NICHT per Hash als
        identisch bestätigt (z.B. noch nicht fertig verarbeitet, kein
        `file_hash`) UND der Content-Fallback (`get_file_content` liefert
        hier bewusst kein Ergebnis) bestätigt ihn auch nicht. VORHER fiel
        dieser Fall auf den normalen Upload/Link-Pfad zurück -- das trug
        die Abnahme 'dieselbe offene Änderung klären oder offen melden,
        kein blinder Zweitupload' NICHT (Review-Kritik an genau diesem
        Test). 'Bei ungeklärter eigener offener Änderung offen bleiben'
        heißt: KEIN zweiter Upload, KEIN Delete des ungeklärten
        Kandidaten, der Lauf bleibt ehrlich unvollständig -- Nächster
        `--sync` prüft erneut."""
        client = _FakeAPIClient(
            existing_files=[{"id": "file-unclear-1", "filename": "a.md", "meta": {}}],
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertFalse(ok, "ungeklärter sichtbarer Kandidat darf den Lauf nicht als Erfolg melden")
        self.assertEqual(client.uploaded, [], "KEIN zweiter Upload bei ungeklärter eigener offener Änderung")
        self.assertNotIn("file-unclear-1", client.deleted, "der ungeklärte Altkandidat wird NICHT gelöscht")
        self.assertIn("Unklar", out)
        self.assertIn("KEIN zweiter Upload", out)
        manifest = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest.get("kb_files", {}), "kein falsches Manifest-PASS bei ungeklärtem Kandidaten")


class TestRunSyncOriginalOwnCollectionCandidateForm(unittest.TestCase):
    """U2 (UPDATE_UX_REVIEW.md R2, 02_RESTAUFTRAG.md §U2): die ursprüngliche
    Review-Witness-Form ist `meta.collection_name == <eigene Datei-ID>`
    (OWUI setzt das beim Upload, BEVOR irgendeine KB-Bindung existiert) --
    NICHT ein leeres `collection_name` (das ist der bereits akzeptierte,
    separat erhaltene Teilfall in `TestRunSyncSecondSyncReusesUnboundCandidate`).
    VORHER filterte der Reusezweig nur auf leeres `collection_name` -- ein
    sichtbarer Kandidat in der echten Originalform fiel komplett heraus und
    wurde blind zweit-hochgeladen (Review-Tabelle Zeile 2/3)."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("NEU-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _write_manifest(self, kb_files: dict) -> None:
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": kb_files,
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")

    def _run(self, client, **env):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = "0.3"
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        if "outer_deadline" in env:
            os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = env["outer_deadline"]
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"no_verify": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_original_own_collection_candidate_without_active_old_is_reused_without_upload(self):
        """Review-Tabelle Zeile 2: ursprüngliche Form `collection_name ==
        file_id`, KEINE aktiv getrackte Altversion. Der sichtbare Kandidat
        trägt bereits den lokalen Sollinhalt (Hash-Treffer) -- er muss
        direkt wiederverwendet/verlinkt werden, OHNE jeden Upload."""
        self._write_manifest({})
        local_sha = hashlib.sha256(b"NEU-INHALT").hexdigest()
        client = _FakeAPIClient(
            existing_files=[{
                "id": "file-existing-101", "filename": "a.md",
                "meta": {"collection_name": "file-existing-101", "file_hash": local_sha},
            }],
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        self.assertEqual(client.uploaded, [], "KEIN Upload -- der sichtbare Originalform-Kandidat wird direkt wiederverwendet")
        self.assertEqual(client.linked, [(_KB_ID, "file-existing-101")])
        self.assertEqual(client.deleted, [])
        self.assertIn("erhaltener Kandidat", out)
        manifest = _manifest(self.tmp)
        self.assertEqual(manifest["kb_files"]["a.md"]["file_id"], "file-existing-101")

    def test_tracked_old_version_and_original_own_collection_candidate_relinks_and_cleans_up_old(self):
        """Review-Tabelle Zeile 3: dieselbe ursprüngliche Form PLUS eine
        aktiv getrackte, inhaltlich tatsächlich abweichende Altversion.
        VORHER lag der Reusezweig NUR im `else` ohne aktiv getrackte
        Altversion -- der erste erhaltene Kandidat blieb unberücksichtigt,
        ein zweiter Upload wurde verknüpft und die Altversion entfernt.
        Jetzt: der sichtbare Originalform-Kandidat wird verlinkt (KEIN
        zweiter Upload), danach wird die bestätigte Altversion bereinigt --
        bewahrt bis zum gültigen Ersatz, dann gezielte Bereinigung."""
        self._write_manifest({"a.md": {
            "md5": hashlib.md5(b"ALT-INHALT").hexdigest(), "file_id": "file-a-old",
        }})
        local_sha = hashlib.sha256(b"NEU-INHALT").hexdigest()
        client = _FakeAPIClient(
            existing_files=[
                {
                    "id": "file-a-old", "filename": "a.md",
                    "meta": {"collection_name": _KB_ID, "file_hash": hashlib.sha256(b"ALT-INHALT").hexdigest()},
                },
                {
                    "id": "file-new-101", "filename": "a.md",
                    "meta": {"collection_name": "file-new-101", "file_hash": local_sha},
                },
            ],
            preset=self.preset,
        )
        ok, out = self._run(client)
        self.assertTrue(ok, out)
        self.assertEqual(client.uploaded, [], "KEIN zweiter Upload -- der erhaltene Kandidat wird genutzt")
        self.assertEqual(client.linked, [(_KB_ID, "file-new-101")])
        self.assertEqual(client.unlinked, [(_KB_ID, "file-a-old")], "die bestätigte Altversion wird NACH dem Ersatz bereinigt")
        self.assertEqual(client.deleted, ["file-a-old"])
        manifest = _manifest(self.tmp)
        self.assertEqual(manifest["kb_files"]["a.md"]["file_id"], "file-new-101")

    def test_exhausted_outer_budget_skips_readiness_and_link_for_reused_candidate(self):
        """U4 (UPDATE_UX_REVIEW.md U4, 02_RESTAUFTRAG.md §U4): derselbe
        Budget-Vertrag wie beim frischen Upload gilt jetzt auch für den
        U2-Reusezweig -- bei bereits erschöpftem äußerem Prozessbudget darf
        KEIN neuer Readiness-/Link-Request mehr starten. Der erhaltene
        Kandidat bleibt dabei UNANGETASTET (kein Delete -- er ist ein
        erhaltener Rest, keine in diesem Lauf frisch erzeugte Entity)."""
        self._write_manifest({})
        local_sha = hashlib.sha256(b"NEU-INHALT").hexdigest()
        client = _FakeAPIClient(
            existing_files=[{
                "id": "file-existing-101", "filename": "a.md",
                "meta": {"collection_name": "file-existing-101", "file_hash": local_sha},
            }],
            preset=self.preset,
        )
        ok, out = self._run(client, outer_deadline="1")
        self.assertFalse(ok, "erschöpftes äußeres Budget darf den Lauf nicht als Erfolg melden")
        self.assertEqual(client.uploaded, [])
        self.assertEqual(client.linked, [], "kein Link-Versuch mit erschöpftem Budget")
        self.assertEqual(client.deleted, [], "der erhaltene Kandidat wird NICHT gelöscht")
        self.assertIn("äußeres Prozessbudget bereits erschöpft", out)
        manifest = _manifest(self.tmp)
        self.assertNotIn("a.md", manifest.get("kb_files", {}))


# ── U3 (ZR-PR3317-RESTNACHZUG-20261124, UPDATE_UX_REVIEW.md R3) ──────────
# Summary, betroffene Restdateien und Prüfzeit waren nicht an denselben
# belegten Lauf gebunden: eine unbestimmte Coverage-Prüfung lieferte `True`
# (setup.py ~1826-1832), Coverage-Fehlteile wurden nicht als `kb_failed` an
# die Summary übergeben (~5285-5290, jetzt verschobene Zeilen), und ein aus
# dem Soll gestrichener Name mit fehlgeschlagenem Entfernen verschwand aus
# `kb_failed` (siehe bereits erweiterter Test oben, `test_u6_unlink_failure_
# on_removed_file_is_a_halt_not_silent_delete`).

class TestCoverageCheckUndeterminedIsNotSilentSuccess(unittest.TestCase):
    """Isolierter Test von `_run_coverage_check` -- kein echter `run_sync`-
    Umweg nötig, da die Funktion pur ist (nur `client.list_files()`)."""

    class _EmptyListClient:
        def list_files(self):
            return []

    class _FullListClient:
        """U3-Restnachzug: `list_files()` ist auswertbar (nicht leer), trägt
        aber KEINE der erwarteten Dateien -- nachweislich fehlend, nicht nur
        unbestimmt (Abgrenzung gegen den leeren/unauswertbaren Fall)."""

        def __init__(self, entries):
            self._entries = entries

        def list_files(self):
            return self._entries

    def test_empty_file_listing_is_reported_as_all_unconfirmed_not_as_success(self):
        """VORHER: `return True` -- eine unbestimmte Prüfung (API lieferte
        keine auswertbare Liste) wurde wie eine bestätigte Vollständigkeit
        behandelt. JETZT: eine nicht-leere Liste der betroffenen (= ALLER
        erwarteten) Dateien, die der Caller als Fehlteil werten muss, PLUS
        (U3-Restnachzug) `undetermined=True` -- kein nachgewiesener
        Fehlbestand, nur eine aktuell nicht abschließend mögliche Prüfung."""
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            missing, undetermined = setup_mod._run_coverage_check(
                self._EmptyListClient(), _KB_ID, ["a.md", "b.md"],
            )
        self.assertEqual(missing, ["a.md", "b.md"])
        self.assertTrue(undetermined, "leere/unauswertbare Liste ist unbestimmt, kein nachgewiesener Fehlbestand")
        self.assertIn("unbestimmt", buf.getvalue())

    def test_no_expected_files_is_vacuously_confirmed(self):
        """Gegenfall: keine konfigurierten Dateien -- nichts zu prüfen,
        `(None, False)` (bestätigt, nicht unbestimmt) bleibt der richtige
        Default."""
        missing, undetermined = setup_mod._run_coverage_check(self._EmptyListClient(), _KB_ID, [])
        self.assertIsNone(missing)
        self.assertFalse(undetermined)

    def test_genuinely_missing_file_is_not_undetermined(self):
        """U3-Restnachzug (UPDATE_UX_REVIEW.md U3, 02_RESTAUFTRAG.md §U3):
        `list_files()` liefert eine auswertbare, nicht-leere Liste, die
        erwartete Datei ist aber nachweislich NICHT in der KB gebunden --
        das ist ein echter Fehlbestand (`undetermined=False`), kein
        erfundener, aber auch kein "unbestimmt"-Fall."""
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            missing, undetermined = setup_mod._run_coverage_check(
                self._FullListClient([{
                    "id": "other", "filename": "unrelated.md",
                    "meta": {"collection_name": _KB_ID},
                }]),
                _KB_ID, ["a.md"],
            )
        self.assertEqual(missing, ["a.md"])
        self.assertFalse(undetermined, "nachweislich fehlend ist KEIN unbestimmter Fall")
        self.assertIn("FEHLGESCHLAGEN", buf.getvalue())
        self.assertIn("Menü [4]", buf.getvalue())
        self.assertNotIn("OWUI_UPLOAD_TIMEOUT", buf.getvalue())


class TestSyncMachineSummaryPreservesCleanupRest(unittest.TestCase):
    """Isolierter Test von `_print_sync_machine_summary` -- pure Funktion,
    kein `run_sync`-Umweg nötig."""

    def test_failed_name_outside_current_soll_stays_visible_without_skewing_totals(self):
        kb_files = [Path("a.md")]
        files_manifest = {"a.md": {"md5": "x", "file_id": "file-a"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            setup_mod._print_sync_machine_summary(
                kb_files, files_manifest, kb_failed=["removed-gone.md"],
            )
        line = buf.getvalue().strip()
        self.assertIn("kb_total=1", line)
        self.assertIn("kb_confirmed=1", line, "der Aufräumrest zählt nicht gegen den aktuellen Soll-Umfang")
        self.assertIn("removed-gone.md", line.split("kb_failed=", 1)[1])

    def test_in_scope_failure_still_reduces_confirmed_count_as_before(self):
        """Gegenfall: ein Fehlteil INNERHALB des aktuellen Solls zählt
        weiterhin regulär gegen `kb_confirmed` -- der Fix betrifft nur
        Namen AUSSERHALB von `expected`."""
        kb_files = [Path("a.md"), Path("b.md")]
        files_manifest = {"a.md": {"md5": "x", "file_id": "file-a"}, "b.md": {"md5": "y", "file_id": "file-b"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            setup_mod._print_sync_machine_summary(kb_files, files_manifest, kb_failed=["b.md"])
        line = buf.getvalue().strip()
        self.assertIn("kb_total=2", line)
        self.assertIn("kb_confirmed=1", line)
        self.assertIn("b.md", line.split("kb_failed=", 1)[1])


class TestRunSyncUnchangedPathReportsCoverageFailure(unittest.TestCase):
    """Realer `run_sync`-Aufrufer, 'nichts lokal geändert'-Schnellpfad: die
    Coverage-Prüfung lief dort VORHER bei Scheitern direkt in `sys.exit(1)`,
    OHNE je eine SYNC_RESULT-Zeile zu drucken -- der Launcher (`run_sync_
    subprocess`/`_parse_sync_result_line`) sah dann GAR KEINE Aufschlüsselung
    für diesen Lauf (weder Erfolg noch benannter Fehlteil)."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)
        self.addCleanup(self.tmp_ctx.cleanup)
        (self.tmp / "kb").mkdir()
        (self.tmp / "kb" / "a.md").write_text("AKTUELLER-INHALT", encoding="utf-8")
        (self.tmp / "meta").mkdir()
        (self.tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
        (self.tmp / ".openwebui-sync.json").write_text(json.dumps({
            "masterprompt_md5": setup_mod._text_md5("Du bist die SL."),
            "masterprompt_path": "meta/masterprompt.md",
            "kb_files": {"a.md": {"md5": hashlib.md5(b"AKTUELLER-INHALT").hexdigest(), "file_id": "file-a"}},
            "last_sync": "2026-11-18T00:00:00",
        }), encoding="utf-8")
        self.preset = {
            "id": "p1", "name": "Proj",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"capabilities": setup_mod.GOLDEN_CAPABILITIES, "knowledge": [{"id": _KB_ID}]},
            "params": {"system": "Du bist die SL."},
        }

    def _run(self, client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OWUI_FILE_READY_TIMEOUT"] = "0.3"
        os.environ["OWUI_FILE_READY_POLL_INTERVAL"] = "0.01"
        try:
            with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
                 mock.patch.object(setup_mod, "APIClient", return_value=client):
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_coverage_check_failure_on_unchanged_path_emits_sync_result_with_named_failure(self):
        # "a.md" ist laut Manifest unveraendert (gleicher md5) -- der
        # Schnellpfad "nichts geaendert" greift. Die KB-Dateiliste ist aber
        # leer (nicht mehr auswertbar) -> Coverage-Check unbestimmt.
        client = _FakeAPIClient(existing_files=[], preset=self.preset)
        ok, out = self._run(client)
        self.assertFalse(ok, "eine unbestimmte Coverage-Pruefung darf den Schnellpfad nicht als Erfolg melden")
        sync_result_lines = [l for l in out.splitlines() if l.startswith("SYNC_RESULT ")]
        self.assertEqual(len(sync_result_lines), 1, out)
        self.assertIn("a.md", sync_result_lines[0].split("kb_failed=", 1)[1])


class TestFileReadyDeadlineIsolated(unittest.TestCase):
    """Isolierter Test von `_file_ready_deadline_s` -- pure Funktion, liest
    nur die übergebene Env-Var, kein `run_sync`-Umweg nötig."""

    def setUp(self) -> None:
        self._saved = dict(os.environ)
        os.environ.pop("ZEITRISS_SYNC_OUTER_DEADLINE_S", None)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self._saved)))

    def test_no_outer_deadline_known_returns_none(self):
        self.assertIsNone(setup_mod._file_ready_deadline_s(10.0, 90.0))

    def test_plenty_of_remaining_budget_keeps_the_default(self):
        os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = "600"
        # 600 - 10 elapsed - 15 Sicherheitsmarge = 575 verbleibend, weit über
        # dem Default (90) -> der Default bleibt unverändert maßgeblich.
        self.assertEqual(setup_mod._file_ready_deadline_s(10.0, 90.0), 90.0)

    def test_low_remaining_budget_caps_below_the_default(self):
        os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = "100"
        # 100 - 50 elapsed - 15 Sicherheitsmarge = 35 verbleibend < Default 90.
        self.assertEqual(setup_mod._file_ready_deadline_s(50.0, 90.0), 35.0)

    def test_exhausted_budget_returns_zero_not_negative(self):
        os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = "10"
        self.assertEqual(setup_mod._file_ready_deadline_s(50.0, 90.0), 0.0)

    def test_unparseable_value_is_treated_like_unknown(self):
        os.environ["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = "not-a-number"
        self.assertIsNone(setup_mod._file_ready_deadline_s(10.0, 90.0))


if __name__ == "__main__":
    unittest.main()
