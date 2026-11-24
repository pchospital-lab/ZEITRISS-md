#!/usr/bin/env python3
"""scripts/tests/test_setup_launcher_u3_coverage_undetermined_2026_11_24_r3.py --
ZR-PR3317-RESTNACHZUG-20261124-r3, U3 (UPDATE_UX_REVIEW.md "Rest U3").

Ursache (verifiziert am echten Code VOR diesem Fix): `_run_coverage_check`
liefert bereits `(names, undetermined)` zurueck (r2-Fix). Beide `run_sync`-
Caller (unveraenderter Schnellpfad `setup.py` -- vormals ~4974-4988, und
geaenderter Pfad -- vormals ~5635-5647) lasen das Tupel als `coverage_
missing, _coverage_undetermined` und VERWARFEN den Zusatzstatus. Die
Maschinen-Summary (`_print_sync_machine_summary`) kannte nur `kb_failed` +
Zaehler; Parser (`launcher_update._parse_sync_result_line`) und State
uebernahmen genau diese Felder; Anzeige/Diagnose (`launcher._describe_kb_
sync_status`/`_check_persisted_sync_status`) konnten den Grund nicht mehr
unterscheiden. Eine leere/unlesbare Coverageantwort ("aktuell nicht
abschliessend pruefbar") und ein belegter Fehlbestand ("nachgewiesen
fehlend") endeten dadurch identisch als `kb_failed`-Namensliste und wurden
spaeter GLEICH als "offen" angezeigt.

Fix: `coverage_undetermined` wird jetzt durch BEIDE `run_sync`-Caller, die
Summary-Zeile (`SYNC_RESULT ... coverage_undetermined=0/1`), den Parser,
den persistierten State und die beiden unveraenderten Anzeigefunktionen
durchgereicht. Beide Faelle bleiben Nicht-Erfolg (`sys.exit(1)`); nur die
gespeicherte Endanzeige (`_describe_kb_sync_status`) und der Diagnosetext
(`_check_persisted_sync_status`, `status` bleibt bewusst "offen" --
unveraenderte Gate-/Fix-Vorschlag-Semantik) unterscheiden den Grund.

Dieser Test treibt den ECHTEN `run_sync` ueber BEIDE Caller-Zweige
(unveraenderter Schnellpfad UND geaenderter Pfad mit echtem Upload/Link)
mit je (a) einer leeren/unauswertbaren Coverageantwort und (b) einem
vollstaendig gelesenen, echt fehlenden Sollbestand, fuehrt die reale
Ausgabe ueber den echten Summary-Parser + State + die unveraenderten
Anzeigefunktionen und beweist die unterscheidbare Endanzeige. Fixture-
Muster identisch zu `test_setup_upd1_readiness_2026_11_23.py` /
`test_launcher_action_update_upd2_sync_status_2026_11_23.py`. Kein
Docker/Netzwerk-Call."""
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
from types import SimpleNamespace

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

# Dieselbe dokumentierte Konvention wie test_setup_upd1_readiness_2026_11_23.py
# / test_setup_run_setup_coverage_wording_2026_11_24_r2.py: `scripts/setup.py`
# fuegt sich beim Laden selbst vor den Repo-Root in sys.path ein -- den neu
# hinzugekommenen Pfadeintrag sofort nach dem Laden wieder entfernen, sonst
# findet ein SPAETER in DEMSELBEN Prozess entdecktes `import tests.mmo_sim`
# faelschlich `scripts/tests` statt des echten Top-Level-`tests/`-Pakets.
_sys_path_before_setup_exec = list(sys.path)
_spec = importlib.util.spec_from_file_location(
    "u3_r3_coverage_undetermined_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
for _p in list(sys.path):
    if _p not in _sys_path_before_setup_exec:
        sys.path.remove(_p)

from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402

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


class _FakeAPIClient:
    """Minimaler Fake am aeusseren API-Rand -- identische Konvention wie
    `test_setup_upd1_readiness_2026_11_23.py._FakeAPIClient`, hier auf das
    fuer U3 Noetige reduziert (keine Readiness-Verzoegerung -- Standard
    'immediate', der Fokus liegt auf dem Coverage-Check NACH dem Link)."""

    def __init__(self, *, existing_files, preset):
        self._existing_files = list(existing_files)
        self._preset = preset
        self.uploaded: list[str] = []
        self.linked: list[tuple[str, str]] = []
        self.unlinked: list[tuple[str, str]] = []
        self.deleted: list[str] = []
        self.last_add_file_code = None
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

    def get_file(self, file_id):
        return 200, {"id": file_id, "data": {"status": "completed", "content": "extrahierter Inhalt"}}

    def add_file_to_knowledge(self, kb_id, file_id):
        self.linked.append((kb_id, file_id))
        self.last_add_file_code = 200
        for f in self._existing_files:
            if f.get("id") == file_id:
                f["meta"] = {"collection_name": kb_id}
        return True

    def remove_file_from_knowledge(self, kb_id, file_id):
        self.unlinked.append((kb_id, file_id))
        return True

    def delete_file(self, file_id):
        self.deleted.append(file_id)
        self._existing_files = [f for f in self._existing_files if f.get("id") != file_id]
        return True

    def get_file_content(self, file_id):
        return None


# Dieselben zwei Coverage-Antworten wie im UPDATE_UX_REVIEW.md-Witness
# (`repro/update_r4_witness.py`, read-only -- NICHT dieselbe Datei, nur
# dieselbe Fallunterscheidung): eine leere/unauswertbare Liste (unbestimmt)
# gegen eine auswertbare, nicht-leere Liste, die die erwartete Datei
# dennoch NICHT gebunden traegt (nachgewiesen fehlend).
_UNDETERMINED_EXISTING_FILES: list = []
_MISSING_EXISTING_FILES = [
    {"id": "other", "filename": "other.md", "meta": {"collection_name": _KB_ID}},
]


def _through_parser_state_and_display(tmp: Path, out: str):
    """Fuehrt eine echte `run_sync`-Ausgabe ueber den echten Summary-Parser
    + `run_sync_subprocess` (State-Schreibpfad) + die unveraenderten
    Anzeigefunktionen -- derselbe Weg wie der echte Launcher."""
    subprocess_ok, _tail = lu.run_sync_subprocess(
        tmp, runner=lambda *a, **k: SimpleNamespace(returncode=1, stdout=out, stderr=""),
    )
    summary = lu._parse_sync_result_line(out)
    state = lu.read_state(tmp)
    display = L._describe_kb_sync_status(state)
    with mock.patch.object(L, "REPO", tmp):
        persisted_status, persisted_detail = L._check_persisted_sync_status()
    return subprocess_ok, summary, display, persisted_status, persisted_detail


class TestUnchangedFastPathCallerDistinguishesUndeterminedFromMissing(unittest.TestCase):
    """Fall U3, unveraenderter Schnellpfad (vormals setup.py ~4974-4988):
    "a.md" ist laut Manifest unveraendert (gleicher md5) -- der Schnellpfad
    "nichts geaendert" greift, die Coverage-Pruefung laeuft trotzdem."""

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

    def test_both_cases_are_non_success_but_distinguishable_end_state(self):
        ok_u, out_u = self._run(_FakeAPIClient(existing_files=_UNDETERMINED_EXISTING_FILES, preset=self.preset))
        self.assertFalse(ok_u, "leere/unauswertbare Coverageantwort muss weiterhin Nicht-Erfolg sein")
        sub_ok_u, summary_u, display_u, pstatus_u, pdetail_u = _through_parser_state_and_display(self.tmp, out_u)
        self.assertFalse(sub_ok_u)
        self.assertIsNotNone(summary_u)
        self.assertIn("a.md", summary_u["kb_failed"])
        self.assertTrue(summary_u["coverage_undetermined"], "unbestimmte Antwort muss im SYNC_RESULT markiert sein")
        self.assertIn("aktuell nicht abschließend prüfbar", display_u)
        self.assertEqual(pstatus_u, "offen", "status bleibt unveraendert 'offen' -- nur der Grundtext unterscheidet")
        self.assertIn("aktuell nicht abschließend prüfbar", pdetail_u)

        # Frisches Repo fuer den zweiten Fall (derselbe Manifest-/Masterprompt-
        # Stand, nur der Coverage-Backend-Rand unterscheidet sich).
        self.setUp()
        ok_m, out_m = self._run(_FakeAPIClient(existing_files=_MISSING_EXISTING_FILES, preset=self.preset))
        self.assertFalse(ok_m, "ein belegter Fehlbestand muss weiterhin Nicht-Erfolg sein")
        sub_ok_m, summary_m, display_m, pstatus_m, pdetail_m = _through_parser_state_and_display(self.tmp, out_m)
        self.assertFalse(sub_ok_m)
        self.assertIsNotNone(summary_m)
        self.assertIn("a.md", summary_m["kb_failed"])
        self.assertFalse(summary_m["coverage_undetermined"], "nachgewiesen fehlend ist KEIN unbestimmter Fall")
        self.assertIn("noch offen", display_m)
        self.assertNotIn("aktuell nicht abschließend prüfbar", display_m)
        self.assertEqual(pstatus_m, "offen")
        self.assertNotIn("aktuell nicht abschließend prüfbar", pdetail_m)

        # Kernaussage der Abnahme: unterscheidbare Endanzeige trotz gleich
        # bleibendem Nicht-Erfolg in beiden Faellen.
        self.assertNotEqual(display_u, display_m)
        self.assertNotEqual(pdetail_u, pdetail_m)


class TestChangedPathCallerDistinguishesUndeterminedFromMissing(unittest.TestCase):
    """Fall U3, geaenderter Pfad (vormals setup.py ~5635-5647): "a.md" weicht
    vom Manifest ab -- echter Upload + Link laeuft, die abschliessende
    Coverage-Pruefung danach ist der hier getestete zweite Caller."""

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
                        setup_mod.run_sync(self.tmp, _sync_cfg(), {"assume_yes": True})
                        ok = True
                    except SystemExit as exc:
                        ok = exc.code in (0, None)
                return ok, buf.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_both_cases_are_non_success_but_distinguishable_end_state(self):
        client_u = _FakeAPIClient(existing_files=list(_UNDETERMINED_EXISTING_FILES), preset=self.preset)
        ok_u, out_u = self._run(client_u)
        self.assertFalse(ok_u, "leere/unauswertbare Coverageantwort muss weiterhin Nicht-Erfolg sein")
        self.assertEqual(len(client_u.linked), 1, "der echte Upload/Link laeuft trotz spaeterer Coverage-Unbestimmtheit")
        sub_ok_u, summary_u, display_u, pstatus_u, pdetail_u = _through_parser_state_and_display(self.tmp, out_u)
        self.assertFalse(sub_ok_u)
        self.assertIsNotNone(summary_u)
        self.assertIn("a.md", summary_u["kb_failed"])
        self.assertTrue(summary_u["coverage_undetermined"])
        self.assertIn("aktuell nicht abschließend prüfbar", display_u)
        self.assertEqual(pstatus_u, "offen")

        self.setUp()
        client_m = _FakeAPIClient(existing_files=list(_MISSING_EXISTING_FILES), preset=self.preset)
        ok_m, out_m = self._run(client_m)
        self.assertFalse(ok_m, "ein belegter Fehlbestand muss weiterhin Nicht-Erfolg sein")
        self.assertEqual(len(client_m.linked), 1)
        sub_ok_m, summary_m, display_m, pstatus_m, pdetail_m = _through_parser_state_and_display(self.tmp, out_m)
        self.assertFalse(sub_ok_m)
        self.assertIsNotNone(summary_m)
        self.assertIn("a.md", summary_m["kb_failed"])
        self.assertFalse(summary_m["coverage_undetermined"])
        self.assertIn("noch offen", display_m)
        self.assertNotIn("aktuell nicht abschließend prüfbar", display_m)
        self.assertEqual(pstatus_m, "offen")

        self.assertNotEqual(display_u, display_m)
        self.assertNotEqual(pdetail_u, pdetail_m)


if __name__ == "__main__":
    unittest.main()
