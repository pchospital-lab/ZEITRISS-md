#!/usr/bin/env python3
"""scripts/tests/test_setup_run_setup_coverage_wording_2026_11_24_r2.py —
ZR-PR3317-RESTNACHZUG-20261124-r2, U3 (03_UPDATE_UND_KB.md / UPDATE_UX_REVIEW).

Geschlossene Grenze: Im r2-Restnachzug war der `run_setup`-U3-Zweig
(scripts/setup.py) laut Worker-Report "nur code-gelesen, kein Auto-Test"
(reine Wortwahl, identischer `sys.exit(1)`). Dieser Test schliesst die
Luecke durabel: er treibt das ECHTE `run_setup` durch bis zum
Coverage-Check und beweist, dass bei UNBESTIMMTER Coverage (list_files()
liefert keine auswertbare Liste) tatsaechlich
- die Wortwahl "Setup UNVOLLSTAENDIG — Wissensdateien nicht pruefbar" /
  "aktuell nicht abschliessend pruefbar" gewaehlt wird (NICHT "fehlen"), UND
- mit `sys.exit(1)` abgebrochen wird,
und das vom nachweislich ANDEREN "fehlen"-Zweig (echter, auswertbarer
Fehlbestand) sowie vom Erfolgsfall (vollstaendige Coverage) unterschieden
wird.

Herkunft: adaptiert aus dem adversarialen Repro der unabhaengigen
Kritikerin (vera-report.md, U3-Sonderauftrag), hier mit portablem Pfad
(Repo-Root relativ statt hardcodiert) als dauerhaft von `python3 -m
unittest -q` ab Repo-Root entdeckbarer Test.

Double-Grenze: identische Konvention wie
`scripts/tests/test_setup_upd1_readiness_2026_11_23.py` — `_FakeClient`
ersetzt NUR die aeussere OpenWebUI-API-Schicht; `run_setup` selbst laeuft
unveraendert real gegen ein echtes temporaeres Repo. `resolve_model_
provider` wird zusaetzlich gemockt, weil sie Host-Zustand liest, der mit
der hier geprueften Coverage-Verzweigung nichts zu tun hat. Kein
Docker/Netzwerk-Call. Schreibt nichts ins Repo (Fixtures in tempdir)."""
from __future__ import annotations

import importlib.util
import io
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

# `scripts/setup.py` fuegt sich beim Laden selbst vor den Repo-Root in
# sys.path ein; im GESAMTEN `python3 -m unittest -q`-Lauf ab Repo-Root
# bliebe dieser Eintrag sonst stehen und wuerde ein spaeter entdecktes
# `import tests.mmo_sim` auf `scripts/tests` fehlleiten. Dieselbe
# dokumentierte Konvention wie in test_setup_upd1_readiness_2026_11_23.py:
# den neu hinzugekommenen Pfadeintrag sofort nach dem Laden entfernen.
_sys_path_before = list(sys.path)
_spec = importlib.util.spec_from_file_location(
    "u3_run_setup_coverage_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
for _p in list(sys.path):
    if _p not in _sys_path_before:
        sys.path.remove(_p)


class _FakeClient:
    """Minimaler Fake am aeusseren API-Rand -- genug, um run_setup bis zum
    Coverage-Check durchlaufen zu lassen (frisches Setup: keine bestehende
    KB mit diesem Namen -> old_kb_ids leer -> KEIN list_files()-Aufruf vor
    dem Coverage-Check; der EINZIGE list_files()-Call im ganzen Lauf ist
    der in `_run_coverage_check` selbst)."""

    def __init__(self, *, files_for_coverage):
        self._files_for_coverage = files_for_coverage
        self.last_knowledge_status = 200
        self.last_knowledge_body_ok = True
        self.last_model_status = 404
        self._next_id = 0

    def check_health(self):
        return True

    def check_auth(self):
        return True

    def test_model(self, model_id):
        return True

    def get_model(self, model_id):
        self.last_model_status = 404
        return None

    def get_embedding_config(self):
        return {
            "RAG_EMBEDDING_ENGINE": "",
            "RAG_EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        }

    def list_knowledge(self):
        return []

    def create_knowledge(self, name, description):
        return "kb-new-1"

    def do_upload_file(self, filepath):
        self._next_id += 1
        return f"file-{self._next_id}"

    def get_file(self, file_id):
        return 200, {"id": file_id, "data": {"status": "completed", "content": "Inhalt"}}

    def add_file_to_knowledge(self, kb_id, file_id):
        return True

    def upsert_model(self, payload):
        return True, "created"

    def list_files(self):
        return self._files_for_coverage


def _build_repo(tmp: Path) -> Path:
    (tmp / "kb").mkdir()
    (tmp / "kb" / "a.md").write_text("Modul A", encoding="utf-8")
    (tmp / "kb" / "b.md").write_text("Modul B", encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")
    return tmp


def _cfg():
    return {
        "project": "U3Proj",
        "kb_name": "U3Proj Wissensspeicher",
        "masterprompt": "meta/masterprompt.md",
        "params": {},
        "suggestions": ["Start"],
        "default_variant": "default",
        "variants": {
            "default": {
                "preset_id": "p1",
                "preset_name": "U3Proj",
                "model": "openrouter/deepseek/deepseek-v3.2",
                "cache": False,
            },
        },
    }


def _run(tmp: Path, client):
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", return_value=client), \
             mock.patch.object(setup_mod, "resolve_model_provider", return_value=("legacy", None, None)):
            buf = io.StringIO()
            exit_code = None
            with redirect_stdout(buf), redirect_stderr(buf):
                try:
                    setup_mod.run_setup(tmp, _cfg(), {"assume_yes": True})
                except SystemExit as exc:
                    exit_code = exc.code
            return exit_code, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


class TestU3RunSetupCoverageBranch(unittest.TestCase):
    def test_undetermined_coverage_yields_not_pruefbar_wording_and_exit1(self):
        """list_files() liefert [] (keine auswertbare Liste)
        -> _run_coverage_check gibt (sorted(expected), True) zurueck
        (coverage_undetermined=True) -> run_setup MUSS die
        'nicht pruefbar'-Formulierung waehlen, NICHT 'fehlen', und mit
        exit(1) abbrechen."""
        with tempfile.TemporaryDirectory() as t:
            tmp = _build_repo(Path(t))
            client = _FakeClient(files_for_coverage=[])
            exit_code, out = _run(tmp, client)

        self.assertEqual(exit_code, 1, out)
        self.assertIn("Coverage-Check unbestimmt", out)
        self.assertIn("Setup UNVOLLSTÄNDIG — Wissensdateien nicht prüfbar", out)
        self.assertIn(
            "aktuell nicht abschließend prüfbar", out,
            "muss die U3-spezifische 'kein nachgewiesener Fehlbestand'-Formulierung zeigen",
        )
        self.assertNotIn("Wissensdateien fehlen", out)
        self.assertNotIn("Es fehlen Wissensdateien in der KB", out)

    def test_genuinely_missing_file_yields_fehlen_wording_and_exit1(self):
        """Gegenfall (Unterscheidungsbeweis): list_files() liefert eine
        AUSWERTBARE, aber unvollstaendige Liste (b.md bewusst nicht
        enthalten) -> nachgewiesener Fehlbestand, coverage_undetermined
        MUSS False bleiben -> 'fehlen'-Formulierung, NICHT 'nicht pruefbar',
        ebenfalls exit(1)."""
        with tempfile.TemporaryDirectory() as t:
            tmp = _build_repo(Path(t))
            client = _FakeClient(files_for_coverage=[
                {"id": "file-1", "filename": "a.md",
                 "meta": {"collection_name": "kb-new-1", "name": "a.md"}},
            ])
            exit_code, out = _run(tmp, client)

        self.assertEqual(exit_code, 1, out)
        self.assertIn("Coverage-Check FEHLGESCHLAGEN", out)
        self.assertIn("Setup UNVOLLSTÄNDIG — Wissensdateien fehlen", out)
        self.assertIn("Es fehlen Wissensdateien in der KB", out)
        self.assertNotIn("nicht prüfbar", out)
        self.assertNotIn("nicht abschließend prüfbar", out)

    def test_full_coverage_does_not_exit1_and_prints_success(self):
        """Positivfall: beide erwarteten Dateien sind nachweisbar in der KB
        -> coverage_ok=True -> run_setup darf NICHT ueber den
        Coverage-Zweig abbrechen."""
        with tempfile.TemporaryDirectory() as t:
            tmp = _build_repo(Path(t))
            client = _FakeClient(files_for_coverage=[
                {"id": "file-1", "filename": "a.md",
                 "meta": {"collection_name": "kb-new-1", "name": "a.md"}},
                {"id": "file-2", "filename": "b.md",
                 "meta": {"collection_name": "kb-new-1", "name": "b.md"}},
            ])
            exit_code, out = _run(tmp, client)

        self.assertIsNone(exit_code, out)
        self.assertIn("Coverage-Check grün", out)
        self.assertIn("Setup abgeschlossen!", out)


if __name__ == "__main__":
    unittest.main()
