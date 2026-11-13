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

N1-A-Nachzug (SETUP_FINAL_REVIEW.md §3-§5, Preflight VOR erster Mutation):
  (7) test_a1_unclear_knowledge_list_response_halts_before_any_mutation
  (8) test_a1_sibling_confirmed_absent_via_404_continues_without_halt_or_relink
  (9) test_a1_sibling_unrelated_knowledge_list_with_replaced_kb_continues_without_relink
  (10) test_a1_sibling_read_error_halts_before_any_mutation
  (11) test_a1_sibling_malformed_knowledge_field_halts_before_any_mutation
  (12) test_a2_shared_file_id_in_target_and_protected_kb_is_preserved
  (13) test_a2_unreadable_protected_kb_detail_preserves_candidate_file
  (14) test_a3_failed_kb_removal_stops_before_file_deletion_and_preset_recreation

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
                 fail_delete_file_ids=None, fail_update_model_ids=None,
                 knowledge_list_response=None, knowledge_files=None,
                 unreadable_knowledge_detail_ids=None,
                 fail_delete_knowledge_ids=None, model_read_error_ids=None,
                 fail_delete_model_ids=None, knowledge_detail_raw_files=None):
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
        # WP-N1-A1: optionaler Override der KB-LISTEN-Antwort (nicht der
        # einzelnen Detailantwort), um einen unlesbaren/formfalschen
        # `list_knowledge()`-Read zu simulieren -- (code, body)-Tupel.
        self.knowledge_list_response = knowledge_list_response
        # WP-N1-A2: kb_id -> Liste von File-IDs, die `GET /knowledge/{id}`
        # fuer DIESE KB als `files` zurueckgibt (die einzige Quelle fuer
        # eine Mehrfachzugehoerigkeit jenseits von `meta.collection_name`).
        # Eine hier NICHT gelistete KB antwortet mit einer bestaetigten
        # LEEREN Liste (Default -- die meisten Tests brauchen keine
        # Sharing-Simulation); `unreadable_knowledge_detail_ids` simuliert
        # stattdessen den dokumentierten `files: null`-Bug.
        self.knowledge_files = {kid: list(v) for kid, v in (knowledge_files or {}).items()}
        self.unreadable_knowledge_detail_ids = set(unreadable_knowledge_detail_ids or [])
        self.fail_delete_knowledge_ids = set(fail_delete_knowledge_ids or [])
        # WP-N1-A1: Model-IDs, deren `get_model()`-Read einen echten
        # Lesefehler (HTTP 500) simulieren statt eines bestaetigten 404.
        self.model_read_error_ids = set(model_read_error_ids or [])
        # WP-N2-A-R0: Model-IDs, deren delete_model()-Mutation einen echten
        # HTTP-500-Fehler liefert (statt 200 bei vorhandenem oder 404/401
        # bei bestaetigt abwesendem Preset) -- unterscheidet den Fehlerfall
        # von der bestaetigten Abwesenheit.
        self.fail_delete_model_ids = set(fail_delete_model_ids or [])
        # WP-N2-A-R3: kb_id -> ROHE (ungesaeuberte) `files`-Liste fuer
        # `GET /knowledge/{id}`, um unlesbare Mischlisten/Memberlisten zu
        # simulieren (z.B. [{"unlesbar": true}] oder [""] ) -- im
        # Unterschied zu `knowledge_files` (saubere String-IDs) oder
        # `unreadable_knowledge_detail_ids` (kompletter HTTP-Fehler).
        self.knowledge_detail_raw_files = {
            kid: list(v) for kid, v in (knowledge_detail_raw_files or {}).items()
        }

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
        # WP-N2-A-T1: der behauptete "vollstaendige Mutationsledger" deckte
        # bisher NICHT create_knowledge (POST wurde gar nicht erfasst) und
        # KEINE unbekannten schreibenden Requests ab -- letztere bekamen
        # pauschal HTTP 200 OHNE jede Erfassung (General-Review
        # SETUP_QUELLENPRUEFUNG.md A-T1). Beide Luecken werden hier
        # geschlossen, damit `_assert_zero_writes` echte Vollstaendigkeit
        # pruefen kann.
        self.created_knowledge_calls: list[str] = []
        self.unknown_write_requests: list[tuple] = []
        self._next_file_id = 9000

    def request(self, method, path, data=None, content_type="application/json", timeout=None):
        if method == "GET" and path == "/api/config":
            return 200, b"{}"
        if method == "POST" and path == "/api/chat/completions":
            # test_model(): reine Erreichbarkeits-/Typo-Probe fuer das
            # Base-Model, KEINE der im Vertrag gemeinten Mutationen
            # (Preset/KB/Vektor/Datei/Manifest/Embedding) -- bewusst NICHT
            # im unknown_write_requests-Ledger erfasst.
            return 200, b"{}"
        if method == "GET" and path == "/api/v1/files/":
            # check_auth() -- kein Pagination-Query, immer simple ok.
            return 200, b"{}"
        if method == "GET" and path == "/api/models":
            return 200, b'{"data": []}'
        if method == "GET" and path == "/api/v1/knowledge/":
            if self.knowledge_list_response is not None:
                return self.knowledge_list_response
            items = list(self.knowledge.values())
            return 200, json.dumps({"items": items, "total": len(items)}).encode()
        if method == "GET" and path.startswith("/api/v1/knowledge/") and path != "/api/v1/knowledge/" and (
            not path.endswith("/delete")
        ):
            # WP-N1-A2: Detail-Read EINER KB (`get_knowledge_files`) --
            # unterschieden von der Listen-Antwort oben (`.../knowledge/`
            # ohne Suffix) und vom DELETE-Pfad (eigener `method`-Zweig).
            kb_id = urllib.parse.unquote(path[len("/api/v1/knowledge/"):])
            if kb_id in self.unreadable_knowledge_detail_ids:
                return 500, b'{"detail": "internal error"}'
            if kb_id in self.knowledge_detail_raw_files:
                return 200, json.dumps(
                    {"id": kb_id, "files": self.knowledge_detail_raw_files[kb_id]}
                ).encode()
            member_ids = self.knowledge_files.get(kb_id, [])
            return 200, json.dumps({"id": kb_id, "files": member_ids}).encode()
        if method == "DELETE" and path.startswith("/api/v1/knowledge/") and path.endswith("/delete"):
            kb_id = path.split("/")[-2]
            if kb_id in self.fail_delete_knowledge_ids:
                return 500, b'{"detail": "internal error"}'
            self.knowledge.pop(kb_id, None)
            self.deleted_knowledge_ids.append(kb_id)
            return 200, b"{}"
        if method == "POST" and path.startswith("/api/v1/knowledge/") and (
            path.endswith("/reset") or path.endswith("/reindex")
        ):
            self.reset_vector_calls.append(path)
            return 200, b"{}"
        if method == "POST" and path == "/api/v1/knowledge/create":
            self.created_knowledge_calls.append((data or {}).get("name"))
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
            if model_id in self.model_read_error_ids:
                return 500, b'{"detail": "internal error"}'
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
            self.deleted_model_ids.append(model_id)
            if model_id in self.fail_delete_model_ids:
                return 500, b'{"detail": "internal error"}'
            existed = model_id in self.models
            self.models.pop(model_id, None)
            return (200, b"{}") if existed else (404, b'{"detail": "not found"}')
        # WP-N2-A-T1: ab hier unbekannte/nicht explizit modellierte Pfade --
        # SCHREIBENDE Methoden (POST/PUT/PATCH/DELETE) werden erfasst statt
        # unbeobachtet mit HTTP 200 durchzulaufen (vorher: pauschales
        # `return 200, b"{}"` ohne jede Spur). Lesende GETs bleiben wie
        # bisher unveraendert (kein Mutationsrisiko, zu viele legitime
        # Such-/Status-Reads um sie hier einzeln zu modellieren).
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            self.unknown_write_requests.append((method, path))
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


def _assert_zero_writes(http: _SetupHttpDouble, out: str, *, tmp: "Path | None" = None) -> None:
    """WP-N1-A1: ein kontrollierter Halt vor der ersten Mutation bedeutet
    NULL Einträge im VOLLSTÄNDIGEN Mutationsledger -- nicht nur
    `deleted_file_ids`. Der General-Review (SETUP_FINAL_REVIEW.md §5)
    kritisiert genau das: ein Testname "Halt vor Löschung", der nur eine
    einzelne letzte Löschfunktion beobachtet, bestätigt den WEITERLAUFENDEN
    Ablauf statt ihn zu widerlegen.

    WP-N2-A-T1: um `created_knowledge_calls` (POST .../knowledge/create war
    bisher UNBEOBACHTET) und `unknown_write_requests` (unbekannte
    schreibende Requests liefen bisher pauschal als HTTP 200 OHNE Erfassung
    durch) ergaenzt -- derselbe gemeinsame Helfer wird jetzt auch im
    Resetfall verwendet (vorher prüfte der Reset-Halt-Test nur 3 der 9+
    Listen). Mit `tmp` zusaetzlich die lokale Manifest-Beobachtung: ein
    Halt VOR jeder Mutation darf auch kein `.openwebui-sync.json`
    geschrieben/geloescht haben."""
    assert http.deleted_model_ids == [], f"kein Preset-Delete:\n{out}"
    assert http.deleted_knowledge_ids == [], f"kein KB-Delete:\n{out}"
    assert http.reset_vector_calls == [], f"kein Vektor-Reset:\n{out}"
    assert http.deleted_file_ids == [], f"kein Datei-Delete:\n{out}"
    assert http.delete_file_attempts == [], f"kein Datei-Delete-Versuch:\n{out}"
    assert http.uploaded_files == [], f"kein Upload:\n{out}"
    assert http.linked_files == [], f"kein Link:\n{out}"
    assert http.created_model_payloads == [], f"keine Preset-Neuanlage:\n{out}"
    assert http.update_model_payloads == [], f"kein Preset-Update:\n{out}"
    assert http.created_knowledge_calls == [], f"keine KB-Neuanlage:\n{out}"
    assert http.unknown_write_requests == [], (
        f"keine unbeobachteten schreibenden Requests: {http.unknown_write_requests}\n{out}"
    )
    if tmp is not None:
        manifest = tmp / ".openwebui-sync.json"
        assert not manifest.exists(), f"kein lokales Sync-Manifest-Write/-Delete vor dem Halt:\n{out}"


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
    freigeben.

    WP-N1-A1 (General-Review SETUP_FINAL_REVIEW.md §5, Zeilen 66-74): die
    URSPRÜNGLICHE Fassung dieses Tests verlangte nur `exited in (None, 0)`
    und `deleted_file_ids == []` -- das bestätigt nur, dass die explizite
    Dateischleife übersprungen wird, NICHT dass Preset-/KB-Deletes und
    anschließende Create-/Upload-/Link-Schritte ebenfalls unterbleiben.
    Jetzt mit dem vorgezogenen Preflight: ein unklarer Dateibestand stoppt
    VOR der ersten Mutation -- `run_setup` bricht mit exit(1) ab, und der
    GESAMTE Mutationsledger bleibt leer (kein einziger Preset-/KB-/Datei-
    Write, keine Preset-Neuanlage)."""
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
        assert exited == 1, f"ein unklarer Dateibestand muss VOR jeder Mutation hart abbrechen: exited={exited}\n{out}"
        _assert_zero_writes(http, out, tmp=tmp)
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


def test_reset_path_unclear_file_list_halts_before_any_mutation():
    """WP-N1-A1 im `run_reset`-Pfad: derselbe Vorabentscheid wie in
    `run_setup` -- ein unklarer Dateibestand muss VOR dem ersten
    Preset-Delete abbrechen, nicht erst nach KB-/Preset-Löschung mit
    bloßer Warnung weiterlaufen (der alte Reihenfolgefehler, SETUP_FINAL_
    REVIEW.md §3: "`run_reset`... Presetlöschung und KB-/Vektorlöschung
    kommen vor der Dateiinventur")."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            files=[{"id": "f-real", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}}],
            files_pages=[(500, b"server error")],
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"ein unklarer Dateibestand muss run_reset VOR jeder Mutation abbrechen: exited={exited}\n{out}"
        # WP-N2-A-T1 (General-Review A-T1): bisher prüfte dieser Test nur
        # drei der 9+ Mutationslisten -- derselbe gemeinsame Helfer wie bei
        # den run_setup-Halt-Tests deckt jetzt den VOLLSTÄNDIGEN Ledger ab
        # (inkl. created_knowledge_calls, unknown_write_requests, lokales
        # Sync-Manifest), auch im Resetfall.
        _assert_zero_writes(http, out, tmp=tmp)
        assert "kb-real-1" in http.knowledge, "die KB bleibt unangetastet"


def test_reset_path_shared_file_id_in_protected_kb_is_preserved():
    """WP-N1-A2 im `run_reset`-Pfad: derselbe Schutz-Check wie in
    `run_setup` -- eine File-ID, die laut `GET /knowledge/{id}` auch von
    einer fremden, nicht zu entfernenden KB mitgeführt wird, bleibt
    erhalten, der Rest des Resets (Preset-/KB-Entfernung, danach
    Full-Rebuild via `run_setup`) läuft normal weiter."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-real-1", "name": _KB_NAME},
                {"id": "kb-protected-1", "name": "Fremdes Projekt KB"},
            ],
            files=[{"id": "f-shared", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}}],
            knowledge_files={"kb-protected-1": ["f-shared"]},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"exited={exited}\n{out}"
        assert "f-shared" not in http.deleted_file_ids, (
            "eine auch von einer fremden KB mitgeführte File-ID darf NICHT global gelöscht werden"
        )
        assert "f-shared" in http.files
        assert "kb-real-1" in http.deleted_knowledge_ids, "die eigene KB wird trotzdem normal entfernt"


# ── (7)-(14): N1-A-Nachzug -- Preflight VOR erster Mutation ─────────────
# (SETUP_FINAL_REVIEW.md §3-§5): Sibling- und Datei-Zugehörigkeit müssen
# VOR Preset-/KB-/Datei-Deletes bestimmt sein; unklare Lage -> kontrollierter
# Halt mit NULL Writes im GESAMTEN Mutationsledger, nicht nur bei der
# letzten Dateischleife.

def test_a1_unclear_knowledge_list_response_halts_before_any_mutation():
    """`list_knowledge()` selbst liefert einen formfalschen Körper (kein
    `items`-Feld) -- das ist genauso unklar wie ein HTTP-Fehler und darf
    den destruktiven Pfad NICHT freigeben. Muss VOR dem ersten Preset-
    Delete abbrechen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge_list_response=(200, b'{"detail": "unexpected shape"}'),
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"ein formfalscher KB-Listen-Körper muss hart abbrechen: exited={exited}\n{out}"
        _assert_zero_writes(http, out, tmp=tmp)
        assert "unklar" in out.lower() or "nicht lesbar" in out.lower(), out


def test_a1_sibling_confirmed_absent_via_404_continues_without_halt_or_relink():
    """Eine ersetzte KB (`old_kb_ids` nicht leer) UND ein Sibling-Preset,
    das schlicht NICHT installiert ist (bestätigtes HTTP 404) -- das ist
    KEIN Lesefehler und darf den Lauf NICHT anhalten. Unterscheidet sich
    von Test (10): dort ist 404 durch einen echten 500er ersetzt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={},  # p-sibling bewusst NICHT vorhanden -> echtes 404
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"ein bestätigt abwesendes Sibling darf NICHT anhalten: exited={exited}\n{out}"
        assert "p-sibling" in http.get_model_calls, "die Abwesenheit muss tatsächlich GEPRÜFT worden sein"
        assert not any(p.get("id") == "p-sibling" for p in http.update_model_payloads), (
            "ein nicht installiertes Sibling bekommt keinen Nachzugs-Update-Call"
        )


def test_a1_sibling_unrelated_knowledge_list_with_replaced_kb_continues_without_relink():
    """Eine ersetzte KB UND ein installiertes Sibling mit einer vollständig
    gelesenen, aber KOMPLETT UNBETEILIGTEN `meta.knowledge`-Liste (0 Treffer
    auf `old_kb_ids`) -- eindeutig fremd, vollständig gelesen, darf
    übersprungen werden, OHNE anzuhalten und OHNE Update."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"knowledge": [{"id": "kb-fully-unrelated", "name": "X", "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"ein eindeutig fremdes Sibling darf NICHT anhalten: exited={exited}\n{out}"
        assert not any(p.get("id") == "p-sibling" for p in http.update_model_payloads)
        assert http.models["p-sibling"]["meta"]["knowledge"] == [
            {"id": "kb-fully-unrelated", "name": "X", "type": "collection"}
        ], "das unbeteiligte Sibling bleibt vollständig unverändert"


def test_a1_sibling_read_error_halts_before_any_mutation():
    """Ein installiertes Sibling, dessen `get_model()`-Read einen ECHTEN
    Lesefehler liefert (HTTP 500, nicht 404) -- `get_model()==None` bedeutet
    hier "Lesefehler", NICHT "nicht installiert". Muss VOR jeder Mutation
    (inkl. Preset-Delete der gewählten Variante) abbrechen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            model_read_error_ids={"p-sibling"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"ein Lesefehler beim Sibling-Preset muss hart abbrechen: exited={exited}\n{out}"
        _assert_zero_writes(http, out, tmp=tmp)


def test_a1_sibling_malformed_knowledge_field_halts_before_any_mutation():
    """Ein installiertes Sibling, dessen `meta.knowledge` KEINE Liste ist
    (z.B. ein String oder fehlt) -- das ist KEIN Zugehörigkeitsbeweis für
    "unverwandt" und darf NICHT stillschweigend übersprungen werden
    (genau der in SETUP_FINAL_REVIEW.md §3 belegte alte Fehler). Muss VOR
    jeder Mutation abbrechen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"knowledge": "not-a-list"},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"ein formfalsches meta.knowledge muss hart abbrechen: exited={exited}\n{out}"
        _assert_zero_writes(http, out, tmp=tmp)


def test_a2_shared_file_id_in_target_and_protected_kb_is_preserved():
    """Dieselbe File-ID (`f-shared`) ist laut `meta.collection_name` Teil
    der zu ersetzenden Ziel-KB (`kb-old-1`), wird aber laut `GET /knowledge/
    {id}` auch von einer fremden, NICHT entfernten Schutz-KB
    (`kb-protected-1`) tatsächlich mitgeführt. `collection_name` allein
    beweist keine Exklusivität -- die Datei muss erhalten bleiben, der
    Rest des Rebuilds läuft normal weiter (kein globaler Halt, nur ein
    einzelnes geschütztes Objekt)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-old-1", "name": _KB_NAME},
                {"id": "kb-protected-1", "name": "Fremdes Projekt KB"},
            ],
            files=[{"id": "f-shared", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            knowledge_files={"kb-protected-1": ["f-shared"]},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"ein einzelnes geschütztes Objekt darf den Rebuild nicht global stoppen: exited={exited}\n{out}"
        assert "f-shared" not in http.deleted_file_ids, (
            "eine auch von einer fremden KB mitgeführte File-ID darf NICHT global gelöscht werden"
        )
        assert "f-shared" in http.files, "Inhalt + Schutzbeziehung bleiben erhalten"
        assert "kb-old-1" in http.deleted_knowledge_ids, "die eigene Ziel-KB wird trotzdem normal ersetzt"


def test_a2_unreadable_protected_kb_detail_preserves_candidate_file():
    """Wie (12), aber die fremde KB antwortet auf `GET /knowledge/{id}`
    unlesbar (HTTP 500, simuliert den dokumentierten `files: null`-Bug) --
    Exklusivität ist damit NICHT belegbar. Konservativ: die Kandidaten-
    Datei bleibt ebenfalls erhalten, statt eine Leerliste zu unterstellen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-old-1", "name": _KB_NAME},
                {"id": "kb-protected-1", "name": "Fremdes Projekt KB"},
            ],
            files=[{"id": "f-maybe-shared", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            unreadable_knowledge_detail_ids={"kb-protected-1"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"exited={exited}\n{out}"
        assert "f-maybe-shared" not in http.deleted_file_ids, (
            "unbelegbare Exklusivität einer fremden KB muss konservativ erhalten, nicht geraten werden"
        )
        assert "f-maybe-shared" in http.files


def test_a3_failed_kb_removal_stops_before_file_deletion_and_preset_recreation():
    """`delete_knowledge()` schlägt für die zu entfernende KB konkret fehl
    (HTTP 500) -- das darf NICHT als gelungene Ersetzung durchlaufen. Keine
    Dateilöschung, keine neue KB, kein neues Preset -- enger Teilfehler.
    Das Preset-Aufräumen der GEWÄHLTEN Variante selbst (eigener, unabhängig
    bestehender Mutationsschritt) läuft normal weiter."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            files=[{"id": "f-old-A", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            fail_delete_knowledge_ids={"kb-old-1"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"eine fehlgeschlagene KB-Entfernung muss hart abbrechen: exited={exited}\n{out}"
        assert "kb-old-1" not in http.deleted_knowledge_ids, "die KB-Entfernung ist tatsächlich fehlgeschlagen"
        assert http.delete_file_attempts == [], (
            "nach fehlgeschlagener KB-Entfernung darf KEINE Dateilöschung versucht werden"
        )
        assert http.created_model_payloads == [], "keine neue Preset-Anlage auf Basis einer nur angenommenen Ersetzung"
        assert http.uploaded_files == [] and http.linked_files == []
        assert "abgebrochen" in out.lower(), out


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
