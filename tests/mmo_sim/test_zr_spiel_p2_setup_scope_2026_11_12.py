#!/usr/bin/env python3
"""tests/mmo_sim/test_zr_spiel_p2_setup_scope_2026_11_12.py — ZR-SPIEL-FINISH-P2
Block A (Setup-Scope), standalone Assert-Skript (Konvention der datierten
`tests/mmo_sim/test_*_2026_*.py` -- `python3 -m unittest -q` findet die
Modulfunktionen hier NICHT, da keine `unittest.TestCase`; `scripts/smoke.sh`
startet solche Dateien additiv direkt, s. andere `test_f1_*`-Dateien).

Deckt die zwei WP-P2-Fixes in `scripts/setup.py`:

A1 (`run_setup`s "other_vks"-KB-Link-Nachzug, ~Zeile 4426ff): hing bisher
JEDER installierten Nebenvariante bedingungslos `meta.knowledge` auf die
neue `kb_id` um -- das biegt bei Erstinstallation einer neuen eigenen
Test-KB auch ein produktives Schwesterpreset (andere KB) ungefragt um.
Jetzt: nur Nebenvarianten anfassen, deren `meta.knowledge` GENAU EINEN
Eintrag auf GENAU eine der in diesem Lauf tatsächlich ersetzten alten
KB-IDs trägt; bei Erstinstallation (keine ersetzte KB) KEIN Nachzug;
mehrdeutige Treffer (0 oder >1) werden übersprungen statt erraten; nur
der treffende Eintrag wird ersetzt, der Rest von `meta`/`params` bleibt.

A2 (Dateilöschung in `run_setup` UND `run_reset`): hing bisher an einem
reinen instanzweiten Dateinamen-Match (`run_setup`) bzw. zusätzlich an
einem zu breiten KB-Namens-Präfix (`run_reset`: `startswith(project)`).
Jetzt: Dateien werden nur gelöscht, wenn `meta.collection_name`
NACHWEISLICH zu einer der in diesem Lauf tatsächlich entfernten KB-IDs
gehört; `run_reset`s KB-Auswahl bindet an exakte Namensgleichheit
(`cfg["kb_name"]`, dieselbe Berechnung wie `run_setup`) statt an einen
Projektpräfix; vor dem destruktiven Pfad muss `list_files()` nachweislich
vollständig gelesen sein (`last_files_complete`); ein fehlgeschlagenes
`delete_file()` bricht den restlichen Batch ab statt blind weiterzulöschen
und meldet kein pauschales Erfolgsschild.

Double-Grenze: NUR `APIClient._request` ist gedoubelt (kein echter
Netzwerk-Call) -- `run_setup`, `run_reset`, `discover_knowledge_files`,
`APIClient` selbst (`list_knowledge`, `list_files`, `get_model`,
`upsert_model`, `delete_model`, `delete_knowledge`, `delete_file`,
`do_upload_file`, `add_file_to_knowledge`, ...) laufen ECHT gegen den
simulierten HTTP-Rand. `_auto_load_owui_env` ist gedoubelt (kein Zugriff
auf ~/.openwebui_env). Kein Docker/Netzwerk-Call, kein echtes OWUI.

Tests:
  (1) test_a1_fresh_kb_install_does_not_touch_unrelated_sibling_preset
  (2) test_a1_sibling_with_matching_old_kb_link_gets_single_entry_relinked_rest_preserved
  (3) test_a2_same_filename_file_in_protected_kb_is_not_globally_deleted
  (4) test_a2_incomplete_file_list_halts_before_destructive_delete
  (5) test_a2_failed_delete_stops_batch_and_does_not_claim_false_success
  (6) test_reset_path_exact_kb_name_match_not_prefix_and_file_cleanup_scoped

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import tempfile
import traceback
import unittest.mock as mock
import urllib.parse
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "zr_spiel_p2_setup_scope_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)

_RealAPIClient = setup_mod.APIClient


def _extract_upload_filename(body: bytes) -> str:
    m = re.search(rb'filename="([^"]+)"', body or b"")
    return m.group(1).decode("utf-8") if m else ""


def _build_repo(tmp: Path, *, filenames=("a.md",)) -> None:
    (tmp / "kb").mkdir()
    for i, name in enumerate(filenames):
        (tmp / "kb" / name).write_text(f"Inhalt {i}", encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL.", encoding="utf-8")


_PROJECT = "ZRTestProj"
_KB_NAME = f"{_PROJECT} Wissensspeicher"

_SETUP_CFG = {
    "project": _PROJECT,
    "kb_name": _KB_NAME,
    "masterprompt": "meta/masterprompt.md",
    "params": {"temperature": 0.7, "max_tokens": 32000},
    "suggestions": ["Start"],
    "default_variant": "default",
    "variants": {
        "default": {
            "preset_id": "p-default",
            "preset_name": _PROJECT,
            "model": "openrouter/deepseek/deepseek-v3.2",
            "cache": False,
        },
        "sibling": {
            "preset_id": "p-sibling",
            "preset_name": f"{_PROJECT} Budget",
            "model": "openrouter/deepseek/deepseek-v3.2",
            "cache": False,
        },
    },
}


class _SetupHttpDouble:
    """Fake NUR am äußeren HTTP-Rand (`APIClient._request`). Hält KBs,
    Files und Model-Presets als einfache dicts; zeichnet jeden
    sicherheitsrelevanten Call auf, damit die Tests reale Effekte statt
    geratener Zwischenzustände prüfen."""

    def __init__(self, *, knowledge=None, files=None, models=None,
                 new_kb_id="kb-new-1", files_pages=None,
                 fail_delete_file_ids=None, fail_update_model_ids=None):
        self.knowledge = {kb["id"]: dict(kb) for kb in (knowledge or [])}
        self.files = {f["id"]: dict(f) for f in (files or [])}
        # `models` ist ein dict id -> Preset-Payload (nicht eine Liste --
        # ein Preset hat seine id bereits als Mapping-Key, kein eigenes
        # Umpacken nötig).
        self.models = {mid: dict(m) for mid, m in (models or {}).items()}
        self.new_kb_id = new_kb_id
        # Optionaler Override der paginierten /files/?page=-Antworten, um
        # unvollständige/formfalsche Reads zu simulieren (last_files_complete).
        self.files_pages = files_pages
        self.fail_delete_file_ids = set(fail_delete_file_ids or [])
        self.fail_update_model_ids = set(fail_update_model_ids or [])

        self.deleted_knowledge_ids: list[str] = []
        self.reset_vector_calls: list[str] = []
        self.deleted_file_ids: list[str] = []
        self.delete_file_attempts: list[str] = []
        self.get_model_calls: list[str] = []
        self.update_model_payloads: list[dict] = []
        self.created_model_payloads: list[dict] = []
        self.deleted_model_ids: list[str] = []
        self.uploaded_files: list[str] = []
        self.linked_files: list[tuple] = []
        self._next_file_id = 9000

    def request(self, method, path, data=None, content_type="application/json", timeout=None):
        if method == "GET" and path == "/api/config":
            return 200, b"{}"
        if method == "GET" and path == "/api/v1/files/":
            # check_auth() -- kein Pagination-Query, immer simple ok.
            return 200, b"{}"
        if method == "GET" and path == "/api/models":
            return 200, b'{"data": []}'
        if method == "GET" and path == "/api/v1/knowledge/":
            items = list(self.knowledge.values())
            return 200, json.dumps({"items": items, "total": len(items)}).encode()
        if method == "DELETE" and path.startswith("/api/v1/knowledge/") and path.endswith("/delete"):
            kb_id = path.split("/")[-2]
            self.knowledge.pop(kb_id, None)
            self.deleted_knowledge_ids.append(kb_id)
            return 200, b"{}"
        if method == "POST" and path.startswith("/api/v1/knowledge/") and (
            path.endswith("/reset") or path.endswith("/reindex")
        ):
            self.reset_vector_calls.append(path)
            return 200, b"{}"
        if method == "POST" and path == "/api/v1/knowledge/create":
            return 200, json.dumps({"id": self.new_kb_id}).encode()
        if method == "GET" and path.startswith("/api/v1/files/?page="):
            page = int(path.rsplit("=", 1)[1])
            if self.files_pages is not None:
                idx = page - 1
                if 0 <= idx < len(self.files_pages):
                    return self.files_pages[idx]
                return 200, b'{"items": [], "total": 0}'
            if page > 1:
                return 200, b'{"items": [], "total": 0}'
            items = list(self.files.values())
            return 200, json.dumps({"items": items, "total": len(items)}).encode()
        if method == "DELETE" and path.startswith("/api/v1/files/"):
            file_id = path.rsplit("/", 1)[1]
            self.delete_file_attempts.append(file_id)
            if file_id in self.fail_delete_file_ids:
                return 500, b'{"detail": "internal error"}'
            self.files.pop(file_id, None)
            self.deleted_file_ids.append(file_id)
            return 200, b"{}"
        if method == "POST" and path == "/api/v1/files/":
            fname = _extract_upload_filename(data if isinstance(data, bytes) else b"")
            self._next_file_id += 1
            new_id = f"file-new-{self._next_file_id}"
            self.uploaded_files.append(fname)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path.startswith("/api/v1/knowledge/") and path.endswith("/file/add"):
            kb_id = path.split("/")[-3]
            file_id = (data or {}).get("file_id")
            self.linked_files.append((kb_id, file_id))
            return 200, b"{}"
        if method == "GET" and path.startswith("/api/v1/models/model?id="):
            raw = path[len("/api/v1/models/model?id="):]
            model_id = urllib.parse.unquote(raw)
            self.get_model_calls.append(model_id)
            m = self.models.get(model_id)
            if m is None:
                return 404, b'{"detail": "not found"}'
            return 200, json.dumps(m).encode()
        if method == "POST" and path == "/api/v1/models/model/update":
            model_id = (data or {}).get("id")
            self.update_model_payloads.append(dict(data or {}))
            if model_id in self.fail_update_model_ids:
                return 500, b'{"detail": "internal error"}'
            if model_id in self.models:
                self.models[model_id] = dict(data)
            return 200, json.dumps({"id": model_id}).encode()
        if method == "POST" and path == "/api/v1/models/create":
            self.created_model_payloads.append(dict(data or {}))
            new_id = (data or {}).get("id")
            if new_id:
                self.models[new_id] = dict(data)
            return 200, json.dumps({"id": new_id}).encode()
        if method == "POST" and path == "/api/v1/models/model/delete":
            model_id = (data or {}).get("id")
            existed = model_id in self.models
            self.models.pop(model_id, None)
            self.deleted_model_ids.append(model_id)
            return (200, b"{}") if existed else (404, b'{"detail": "not found"}')
        return 200, b"{}"


def _run_with(repo_fn, tmp: Path, http: _SetupHttpDouble, cfg: dict, opts: dict):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        def _client_factory(base_url, api_key):
            client = _RealAPIClient(base_url, api_key)
            client._request = http.request
            return client

        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", side_effect=_client_factory), \
             mock.patch.object(setup_mod.time, "sleep", return_value=None):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                try:
                    repo_fn(tmp, cfg, opts)
                    exited = None
                except SystemExit as exc:
                    exited = exc.code
            return exited, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _run_setup(tmp: Path, http: _SetupHttpDouble, cfg: dict, opts: dict):
    return _run_with(setup_mod.run_setup, tmp, http, cfg, opts)


def _run_reset(tmp: Path, http: _SetupHttpDouble, cfg: dict, opts: dict):
    return _run_with(setup_mod.run_reset, tmp, http, cfg, opts)


_OPTS = {"assume_yes": True, "no_verify": True, "variants": ["default"]}


# ── (1)/(2): A1 — KB-Link-Nachzug nur bei nachweislicher Zugehörigkeit ──

def test_a1_fresh_kb_install_does_not_touch_unrelated_sibling_preset():
    """Erstinstallation einer neuen Test-KB (keine bestehende KB mit
    `kb_name` -> `old_kb_ids` leer) darf ein bereits installiertes, nicht
    adressiertes Schwesterpreset mit eigener FREMDER KB NICHT anfassen --
    nicht einmal lesen (kein `get_model`-Call), geschweige denn updaten."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {
                "knowledge": [{"id": "kb-prod-other", "name": "Prod KB", "type": "collection"}],
                "description": "Produktiver Sibling",
            },
            "params": {"system": "Produktiver Sibling-Prompt"},
        }
        http = _SetupHttpDouble(
            knowledge=[],  # keine bestehende KB mit kb_name -> old_kb_ids leer
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_setup brach unerwartet ab: exited={exited}\n{out}"
        assert "p-sibling" not in http.get_model_calls, (
            "Erstinstallation ohne ersetzte KB darf das fremde Sibling-Preset "
            "gar nicht erst lesen -- kein Zugehörigkeitsgrund vorhanden"
        )
        assert not any(p.get("id") == "p-sibling" for p in http.update_model_payloads), (
            "kein Update-Call für das unverwandte Sibling-Preset"
        )
        assert http.models["p-sibling"]["meta"]["knowledge"] == [
            {"id": "kb-prod-other", "name": "Prod KB", "type": "collection"}
        ], "das fremde Preset muss unverändert auf seiner eigenen KB bleiben"


def test_a1_sibling_with_matching_old_kb_link_gets_single_entry_relinked_rest_preserved():
    """Die eigene alte gemeinsame KB wird ersetzt (`old_kb_ids` = {kb-old-1}).
    Das Sibling-Preset hat ZWEI knowledge-Einträge: einen auf die ersetzte
    alte KB, einen auf eine unbeteiligte dritte KB. Nur der treffende Eintrag
    wird auf die neue KB umgebogen -- Position/zweiter Eintrag, Description,
    profile_image_url, suggestion_prompts, params und base_model_id bleiben
    exakt erhalten."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {
                "knowledge": [
                    {"id": "kb-old-1", "name": "Old", "type": "collection"},
                    {"id": "kb-unrelated-2", "name": "Other", "type": "collection"},
                ],
                "description": "Sibling desc",
                "profile_image_url": "data:image/png;base64,XXXX",
                "suggestion_prompts": [{"content": "hi"}],
            },
            "params": {"system": "Sibling prompt", "temperature": 0.33},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_setup brach unerwartet ab: exited={exited}\n{out}"
        assert "p-sibling" in http.get_model_calls
        updates = [p for p in http.update_model_payloads if p.get("id") == "p-sibling"]
        assert len(updates) == 1, "genau EIN Nachzugs-Update für das Sibling-Preset"
        payload = updates[0]
        assert payload["meta"]["knowledge"] == [
            {"id": "kb-new-1", "name": _KB_NAME, "type": "collection"},
            {"id": "kb-unrelated-2", "name": "Other", "type": "collection"},
        ], "nur der treffende Eintrag wird ersetzt, der unbeteiligte Eintrag bleibt an seiner Position"
        assert payload["meta"]["description"] == "Sibling desc"
        assert payload["meta"]["profile_image_url"] == "data:image/png;base64,XXXX"
        assert payload["meta"]["suggestion_prompts"] == [{"content": "hi"}]
        assert payload["params"] == {"system": "Sibling prompt", "temperature": 0.33}, (
            "Params der Fremdvariante bleiben unangetastet (bewusster Drift des Nutzers)"
        )
        assert payload["base_model_id"] == "openrouter/mistral/foo"


# ── (3)/(4)/(5): A2 — Dateilöschung nur bei nachweislicher Zugehörigkeit ──

def test_a2_same_filename_file_in_protected_kb_is_not_globally_deleted():
    """Ziel-KB (`kb-old-1`, wird ersetzt) und eine fremde/geschützte KB
    (`kb-protected-999`) haben je eine Datei MIT DEMSELBEN Dateinamen
    (`shared.md`). Nur die Datei der ersetzten Ziel-KB darf gelöscht
    werden -- die geschützte, gleichnamige Datei einer fremden KB bleibt
    unangetastet (ID + Bestand)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("shared.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            files=[
                {"id": "f-old-A", "filename": "shared.md", "meta": {"collection_name": "kb-old-1"}},
                {"id": "f-protect-B", "filename": "shared.md", "meta": {"collection_name": "kb-protected-999"}},
            ],
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_setup brach unerwartet ab: exited={exited}\n{out}"
        assert "f-old-A" in http.deleted_file_ids, "die Datei der ERSETZTEN Ziel-KB darf entfernt werden"
        assert "f-protect-B" not in http.deleted_file_ids, (
            "eine gleichnamige Datei einer FREMDEN KB darf NICHT über den "
            "instanzweiten Dateinamen-Match mitgerissen werden"
        )
        assert "f-protect-B" in http.files, "die geschützte Datei bleibt im Bestand erhalten"


def test_a2_incomplete_file_list_halts_before_destructive_delete():
    """Ein HTTP-Fehler auf der ersten Seite von `list_files()` lässt
    `last_files_complete` False -- eine leere/unvollständige Liste ist KEIN
    Sicherheitsbeleg für "keine Kollision" und darf den Löschpfad nicht
    freigeben. Erwartet: KEINE Datei wird gelöscht, klare Meldung."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            files=[{"id": "f-old-A", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            files_pages=[(500, b"server error")],
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_setup brach unerwartet ab: exited={exited}\n{out}"
        assert http.deleted_file_ids == [], (
            "ein unvollständiger/unklarer Dateibestands-Read darf KEINE Löschung auslösen"
        )
        assert "unklar" in out.lower() or "unvollständig" in out.lower(), out


def test_a2_failed_delete_stops_batch_and_does_not_claim_false_success():
    """Zwei zu löschende Dateien derselben ersetzten KB; die erste
    `delete_file`-Mutation schlägt konkret fehl (HTTP 500). Erwartet: die
    ZWEITE Datei wird NICHT mehr blind gelöscht (Batch abgebrochen), UND es
    gibt KEIN pauschales Erfolgsschild ("N alte Dateien entfernt"), weil real
    nichts entfernt wurde."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md", "b.md"))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            files=[
                {"id": "f-a", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}},
                {"id": "f-b", "filename": "b.md", "meta": {"collection_name": "kb-old-1"}},
            ],
            fail_delete_file_ids={"f-a"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_setup brach unerwartet ab: exited={exited}\n{out}"
        assert http.delete_file_attempts == ["f-a"], (
            "nach dem ersten echten Löschfehlschlag darf 'b.md' NICHT mehr "
            "angefasst werden -- keine blinden Folgelöschungen"
        )
        assert "f-b" in http.files, "die nicht angefasste zweite Datei bleibt im Bestand"
        assert "f-a" not in http.deleted_file_ids
        assert "entfernt" not in out.lower() or "nicht entfernt werden" in out.lower(), (
            "kein pauschales Erfolgsschild, wenn real 0 Dateien entfernt wurden:\n" + out
        )
        assert "abgebrochen" in out.lower(), out


# ── (6): gleicher gefährlicher Selektor im Reset-Pfad ───────────────────

def test_reset_path_exact_kb_name_match_not_prefix_and_file_cleanup_scoped():
    """`run_reset` wählte KBs bisher über `startswith(project)` -- eine KB,
    deren Name mit dem Projektnamen beginnt, aber NICHT der echte
    `kb_name` ist (z.B. eine Test-/Fork-KB "<Projekt>-P1-Test"), wäre
    mitgerissen worden. Jetzt bindet die Auswahl an exakte Namensgleichheit
    (dieselbe `kb_name`-Berechnung wie `run_setup`). Zusätzlich darf eine
    gleichnamige Datei der NICHT entfernten Decoy-KB nicht global gelöscht
    werden. `run_reset` baut danach per Full-Rebuild (`run_setup`) neu auf
    -- derselbe Double/Client wird dabei weiterverwendet (kein zweiter
    Mock-Aufbau nötig, `APIClient` ist global gepatcht)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        decoy_kb_name = f"{_PROJECT}-P1-Test"  # startswith(project) == True, exakt != kb_name
        assert decoy_kb_name.startswith(_PROJECT)
        assert decoy_kb_name != _KB_NAME
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-real-1", "name": _KB_NAME},
                {"id": "kb-decoy-2", "name": decoy_kb_name},
            ],
            files=[
                {"id": "f-real", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}},
                {"id": "f-decoy", "filename": "a.md", "meta": {"collection_name": "kb-decoy-2"}},
            ],
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"run_reset brach unerwartet ab: exited={exited}\n{out}"
        assert "kb-real-1" in http.deleted_knowledge_ids, "die echte, exakt namensgleiche KB wird entfernt"
        assert "kb-decoy-2" not in http.deleted_knowledge_ids, (
            "ein reiner Projektpräfix-Match darf eine fremde/Test-KB mit "
            "ähnlichem Namen NICHT mitreißen"
        )
        assert "kb-decoy-2" in http.knowledge, "die Decoy-KB bleibt unangetastet im Bestand"
        assert "f-real" in http.deleted_file_ids, "die Datei der echten, entfernten KB darf gelöscht werden"
        assert "f-decoy" not in http.deleted_file_ids, (
            "eine gleichnamige Datei der NICHT entfernten Decoy-KB darf nicht "
            "global gelöscht werden"
        )
        assert "f-decoy" in http.files


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
