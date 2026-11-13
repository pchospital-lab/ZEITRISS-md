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

N2-Nachzug (LINUS_N2_BRIEF.md A-R0/A-R1/A-R2/A-R3, General-Review
SETUP_QUELLENPRUEFUNG.md): Preset-Delete-Fehlklassifikation, Sibling-Relink-
Teilfehler, Reset-KB-Delete-Fehlerfolge, unlesbare Listenmitglieder:
  (15) test_a_r0_run_setup_preset_delete_http_error_halts_with_null_follow_up_mutation
  (16) test_a_r0_run_reset_preset_delete_http_error_is_honest_and_does_not_block_kb_cleanup
  (17) test_reset_kb_delete_http_error_halts_before_manifest_and_rebuild
  (18) test_a2_mixed_list_with_one_unreadable_member_preserves_candidate_file
  (19) test_a2_fully_unreadable_member_list_preserves_candidate_file
  (20) test_a1_sibling_unreadable_knowledge_entry_with_zero_matches_halts_before_any_mutation
  (21) test_a1_failed_sibling_relink_with_second_independent_success_is_overall_partial_failure

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
                 fail_delete_model_ids=None, knowledge_detail_raw_files=None,
                 fail_delete_model_401_ids=None):
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
        # WP-N3-K2: Model-IDs, deren delete_model()-Mutation einen echten
        # HTTP-401-Fehler liefert (statt 500) -- unterscheidet den
        # mehrdeutigen Auth-/Scope-Fehler auf ein per GET200 bestaetigt
        # vorhandenes Objekt vom bestaetigten 404 (Abwesenheit) UND vom
        # unspezifischen 500 (`fail_delete_model_ids`).
        self.fail_delete_model_401_ids = set(fail_delete_model_401_ids or [])
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
        # WP-N3-K5: KB-Delete-VERSUCHE (erfolgreich ODER fehlgeschlagen)
        # getrennt von `deleted_knowledge_ids` (nur Erfolge) erfassen -- sonst
        # ist "kb-x not in deleted_knowledge_ids" mehrdeutig zwischen "nie
        # versucht" und "versucht, aber fehlgeschlagen".
        self.delete_knowledge_attempts: list[str] = []
        # WP-N4-A2: lokale Sync-Manifest-VERSUCHE (Write/Unlink) fuer den
        # exakten `.openwebui-sync.json`-Pfad -- aufgezeichnet VOR der
        # tatsaechlichen Operation, auch bei intern abgefangenem Fehler oder
        # gleichlautendem Neuschreiben (nicht nur End-Existenz/End-Bytes).
        # Befuellt von `_run_with()`s Instrumentierung um `_save_sync_
        # manifest()`/`Path.unlink()`, NICHT vom HTTP-Rand hier -- das lokale
        # Manifest ist kein HTTP-Call.
        self.manifest_write_attempts: list[str] = []
        self.manifest_unlink_attempts: list[str] = []
        # Gemeinsame GEORDNETE Folge beider Ereignistypen (write/unlink) in
        # tatsaechlicher Aufruf-Reihenfolge -- die beiden Listen oben allein
        # koennen eine vorher-nachher-Reihenfolge (Reset-Unlink vor
        # spaeterem Neubau-Write) nicht belegen.
        self.manifest_attempts: list[tuple[str, str]] = []
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
            self.delete_knowledge_attempts.append(kb_id)
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
            if model_id in self.fail_delete_model_401_ids:
                return 401, b'{"detail": "unauthorized"}'
            existed = model_id in self.models
            self.models.pop(model_id, None)
            return (200, b"{}") if existed else (404, b'{"detail": "not found"}')
        # WP-N2-A-T1/WP-N4-A2: ab hier unbekannte/nicht explizit modellierte
        # Pfade -- SCHREIBENDE Methoden (POST/PUT/PATCH/DELETE) werden
        # erfasst UND sofort sichtbar abgelehnt, statt unbeobachtet (WP-N2)
        # oder zwar erfasst, aber trotzdem mit HTTP 200 (WP-N4-A2-Rest) mit
        # pauschalem Erfolg durchzulaufen. Ein echter Produktcode-Pfad trifft
        # hier nur, wenn eine tatsaechlich benoetigte Route in diesem Double
        # noch FEHLT -- das muss als Testfehler auffallen, nicht als
        # stillschweigender Erfolg. Lesende GETs bleiben wie bisher
        # unveraendert (kein Mutationsrisiko, zu viele legitime Such-/
        # Status-Reads um sie hier einzeln zu modellieren).
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            self.unknown_write_requests.append((method, path))
            raise AssertionError(
                f"_SetupHttpDouble: unbekannter schreibender Request "
                f"{method} {path} -- nicht explizit modellierte Route darf "
                "NICHT stillschweigend HTTP 200 erhalten."
            )
        return 200, b"{}"


def _run_with(repo_fn, tmp: Path, http: _SetupHttpDouble, cfg: dict, opts: dict):
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    # WP-N4-A2: Write-/Unlink-VERSUCHE fuer den exakten Manifestpfad VOR der
    # echten Operation aufzeichnen -- auch wenn `_save_sync_manifest` einen
    # Schreibfehler intern abfaengt (nur `print_warn`, nie fatal, s. dessen
    # Docstring) oder gleichlautend neu schreibt. Beide Originale bleiben
    # tatsaechlich ausgefuehrt; nur die Beobachtung wird ergaenzt.
    manifest_path = tmp / ".openwebui-sync.json"
    _orig_save_manifest = setup_mod._save_sync_manifest
    _orig_unlink = Path.unlink

    def _tracking_save_manifest(repo_arg, manifest_arg):
        attempt_path = str(Path(repo_arg) / ".openwebui-sync.json")
        http.manifest_write_attempts.append(attempt_path)
        http.manifest_attempts.append(("write", attempt_path))
        return _orig_save_manifest(repo_arg, manifest_arg)

    def _tracking_unlink(self, *a, **kw):
        if str(self) == str(manifest_path):
            http.manifest_unlink_attempts.append(str(self))
            http.manifest_attempts.append(("unlink", str(self)))
        return _orig_unlink(self, *a, **kw)

    try:
        def _client_factory(base_url, api_key):
            client = _RealAPIClient(base_url, api_key)
            client._request = http.request
            return client

        with mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch.object(setup_mod, "APIClient", side_effect=_client_factory), \
             mock.patch.object(setup_mod.time, "sleep", return_value=None), \
             mock.patch.object(setup_mod, "_save_sync_manifest", side_effect=_tracking_save_manifest), \
             mock.patch.object(Path, "unlink", _tracking_unlink):
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


def _assert_zero_writes(http: _SetupHttpDouble, out: str, *, tmp: "Path | None" = None,
                         manifest_sentinel: "bytes | None" = None,
                         expected_preset_delete_attempts: "tuple" = ()) -> None:
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
    geschrieben/geloescht haben.

    WP-N3-K5: `delete_knowledge_attempts` (VERSUCHE, nicht nur Erfolge)
    ergaenzt. Mit `manifest_sentinel` (Bytes) zusaetzlich die staerkere
    Sentinel-Pruefung: ein VORHER bereits vorhandenes lokales Manifest muss
    im Haltfall byte-identisch unangetastet bleiben, nicht nur "existiert
    weiterhin" bzw. "wurde nicht NEU angelegt".

    WP-N4-A2: `manifest_write_attempts`/`manifest_unlink_attempts` (echte
    VERSUCHE, von `_run_with()` um `_save_sync_manifest()`/`Path.unlink()`
    aufgezeichnet, nicht nur End-Existenz/End-Bytes) ergaenzt -- ein reiner
    Endzustands-Check (Sentinel gleich, Datei existiert weiterhin) saehe
    einen fehlgeschlagenen oder gleichlautend erneut schreibenden Versuch
    NICHT. Erst die leere Versuchsliste zusammen mit dem Endzustand belegt,
    dass vor dem Halt wirklich NICHTS versucht wurde."""
    assert http.deleted_model_ids == list(expected_preset_delete_attempts), (
        f"nur die exakt erlaubten initialen Preset-Deletes:\n{out}"
    )
    assert http.deleted_knowledge_ids == [], f"kein KB-Delete:\n{out}"
    assert http.delete_knowledge_attempts == [], f"kein KB-Delete-Versuch:\n{out}"
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
    assert http.manifest_write_attempts == [], (
        f"kein Manifest-Write-VERSUCH vor dem Halt:\n{out}"
    )
    assert http.manifest_unlink_attempts == [], (
        f"kein Manifest-Unlink-VERSUCH vor dem Halt:\n{out}"
    )
    if tmp is not None:
        manifest = tmp / ".openwebui-sync.json"
        if manifest_sentinel is not None:
            assert manifest.exists(), f"Sentinel-Manifest darf im Haltfall nicht verschwinden:\n{out}"
            assert manifest.read_bytes() == manifest_sentinel, (
                f"Sentinel-Manifest-Bytes muessen im Haltfall unveraendert bleiben:\n{out}"
            )
        else:
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
        # WP-N4-A2: in einem NORMAL durchlaufenden Setup muss der neue
        # Manifest-Write-Versuch tatsaechlich beobachtet worden sein -- sonst
        # waere eine leere Versuchsliste in einem Haltfall kein Beleg fuer
        # aktive Beobachtung, sondern koennte genauso gut bedeuten, dass die
        # Instrumentierung gar nichts aufzeichnet.
        manifest_path = str(tmp / ".openwebui-sync.json")
        assert http.manifest_write_attempts == [manifest_path], (
            f"ein normaler Setup-Lauf muss GENAU EINEN Manifest-Write-Versuch "
            f"aufzeichnen: {http.manifest_write_attempts}\n{out}"
        )
        assert http.manifest_unlink_attempts == [], "ein Erstsetup loescht kein Manifest"


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
    nichts entfernt wurde.

    K4 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3): der Batch-Abbruch
    selbst war schon korrekt, aber der Fehler verschwand bisher vor der
    Summary/dem Exitcode -- die VORHERIGE Fassung dieses Tests verlangte
    noch `exited in (None, 0)`, was genau das kritisierte unqualifizierte
    "Setup abgeschlossen!" bei echtem Teilfehler kodierte. Jetzt: sichere
    unabhaengige Folgeschritte (neue KB/Preset/Upload) duerfen trotzdem
    fertig werden, aber der Gesamtlauf endet mit Exit 1 und einer konkreten
    Fehlerbenennung statt eines unqualifizierten Erfolgsschilds."""
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
        assert exited == 1, (
            f"ein echter Datei-Cleanup-Fehler darf NICHT hinter einem "
            f"unqualifizierten Erfolgsschild verschwinden: exited={exited}\n{out}"
        )
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
        assert "Setup abgeschlossen!" not in out, (
            "kein unqualifiziertes Vollerfolgsschild bei echtem Datei-Cleanup-Teilfehler:\n" + out
        )
        assert "f-a" in out and "ID f-a" in out and "f-b" in out and "ID f-b" in out, (
            "die betroffenen Datei-IDs (fehlgeschlagen + ausgelassen) muessen im "
            "Gesamtausgang konkret benannt werden:\n" + out
        )
        assert http.created_knowledge_calls == [_KB_NAME], (
            "sichere unabhaengige Aufbauschritte (neue KB) duerfen trotz des "
            "Datei-Cleanup-Teilfehlers fertig werden:\n" + out
        )


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
    Mock-Aufbau nötig, `APIClient` ist global gepatcht).

    WP-N4-A2: mit einem VORHER bereits vorhandenen lokalen Sync-Manifest --
    ein normaler Reset muss dessen Unlink-VERSUCH beobachten, der
    anschliessende Full-Rebuild (`run_setup`) danach einen neuen
    Write-VERSUCH. Erst die tatsaechliche Reihenfolge (Unlink vor dem
    spaeteren Neubau-Write) belegt, dass die Beobachtung echte Versuche
    sieht und nicht nur einen zufaelligen Endzustand."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        manifest_path = tmp / ".openwebui-sync.json"
        manifest_path.write_text('{"masterprompt_md5": "old"}', encoding="utf-8")
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
        manifest_path_str = str(manifest_path)
        assert http.manifest_unlink_attempts == [manifest_path_str], (
            f"der Reset muss den Unlink-VERSUCH des vorhandenen Manifests "
            f"beobachten: {http.manifest_unlink_attempts}\n{out}"
        )
        assert http.manifest_write_attempts == [manifest_path_str], (
            f"der anschliessende Neuaufbau muss GENAU EINEN neuen "
            f"Manifest-Write-Versuch beobachten: {http.manifest_write_attempts}\n{out}"
        )
        assert http.manifest_attempts == [("unlink", manifest_path_str), ("write", manifest_path_str)], (
            f"der Unlink-Versuch des alten Manifests muss tatsaechlich VOR dem "
            f"Write-Versuch des Neuaufbaus liegen, nicht nur irgendwann "
            f"beide einmal: {http.manifest_attempts}\n{out}"
        )


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
    (inkl. Preset-Delete der gewählten Variante) abbrechen.

    K5 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3): ein VORHER bereits
    vorhandenes lokales Sync-Manifest (Sentinel) muss im Haltfall
    byte-identisch unangetastet bleiben -- nicht nur "existiert weiterhin",
    sondern tatsaechlich unveraendert."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        manifest_sentinel = b'{"existing": true}'
        (tmp / ".openwebui-sync.json").write_bytes(manifest_sentinel)
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            model_read_error_ids={"p-sibling"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, f"ein Lesefehler beim Sibling-Preset muss hart abbrechen: exited={exited}\n{out}"
        _assert_zero_writes(http, out, tmp=tmp, manifest_sentinel=manifest_sentinel)


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
        assert http.delete_knowledge_attempts == ["kb-old-1"], (
            "K5: der fehlgeschlagene KB-Delete-VERSUCH selbst muss erfasst sein -- "
            "nicht nur 'nie in deleted_knowledge_ids gelandet'"
        )
        assert http.delete_file_attempts == [], (
            "nach fehlgeschlagener KB-Entfernung darf KEINE Dateilöschung versucht werden"
        )
        assert http.created_model_payloads == [], "keine neue Preset-Anlage auf Basis einer nur angenommenen Ersetzung"
        assert http.uploaded_files == [] and http.linked_files == []
        assert http.manifest_write_attempts == [], "Null-Folge-Mutation: kein Manifest-Write-VERSUCH nach diesem Teilfehler"
        assert http.manifest_unlink_attempts == [], "Null-Folge-Mutation: kein Manifest-Unlink-VERSUCH nach diesem Teilfehler"
        assert "abgebrochen" in out.lower(), out


# ── (15)-(21): N2-Nachzug -- A-R0/A-R1/A-R2/A-R3 (LINUS_N2_BRIEF.md) ────────


def test_a_r0_run_setup_preset_delete_http_error_halts_with_null_follow_up_mutation():
    """A-R0: delete_model() liefert fuer das GEWAEHLTE Preset einen echten
    HTTP-500-Fehler -- das ist KEIN bestaetigtes Nichtvorhandensein (anders
    als ein 404). run_setup muss VOR den abhaengigen KB-/Dateischritten mit
    sys.exit(1) abbrechen; der Delete-VERSUCH selbst ist real passiert, aber
    keine einzige Folgemutation (KB-Delete/-Create, Datei, neues Preset).

    WP-N4-A1: braucht ein TATSAECHLICH vorhandenes 'p-default' mit gueltiger
    Ziel-KB-Bindung (meta.knowledge -> kb-old-1) -- seit dem A1-Fix fuehrt
    `run_setup` den im Preflight bestaetigten Praesenzentscheid bis zur
    Deletephase mit: ein bestaetigt ABWESENDES (GET404) Preset bekommt gar
    keinen Delete-POST mehr, der hier erwartete HTTP-500 wuerde also nie
    erreicht. Mit dieser Fixture durchlaeuft 'p-default' den Preflight als
    bestaetigt VORHANDEN (GET200 + zulaessige Bindung) und wird deshalb
    tatsaechlich an delete_model() gegeben, wo der simulierte 500 greift."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        default_preset = {
            "id": "p-default", "name": _PROJECT,
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"knowledge": [{"id": "kb-old-1", "name": _KB_NAME, "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-default": default_preset},
            fail_delete_model_ids={"p-default"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein HTTP-500 bei delete_model() darf NICHT als bestaetigte "
            f"Abwesenheit durchlaufen: exited={exited}\n{out}"
        )
        _assert_zero_writes(http, out, tmp=tmp, expected_preset_delete_attempts=["p-default"])
        assert "war nicht vorhanden" not in out, (
            "ein echter HTTP-Fehler darf NICHT als 'war nicht vorhanden' gemeldet werden:\n" + out
        )


def test_a_r0_run_reset_preset_delete_http_error_halts_before_kb_cleanup_with_real_sibling_link():
    """K1 (General-Review 01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3):
    ein fehlgeschlagener Preset-Delete im Reset-Pfad muss VOR den
    abhaengigen KB-/Vektor-/Datei-/Manifest-/Neuaufbauschritten enden. Die
    VORHERIGE Fassung dieses Tests (siehe Git-Historie) verlangte
    ausdruecklich `exited in (None, 0)` UND die KB-Loeschung TROTZ
    fehlgeschlagenem Preset-Delete -- das kodierte genau die vom General
    verbotene Fortsetzung: ein ueberlebender Sibling zeigt weiterhin auf die
    alte KB, die trotzdem entfernt wird; ein spaeterer Neuaufbau erkennt den
    kaputten Sibling nicht mehr, weil die alte KB schon weg ist. Die
    vorherige Fixture hatte zudem GAR KEIN reales Sibling-Preset (`models=`
    war leer) -- jetzt mit einem REAL vorhandenen Preset ('p-sibling'),
    dessen `meta.knowledge` tatsaechlich auf die Reset-Ziel-KB
    ('kb-real-1') verweist, genau der Fall, den ein stiller Weiterlauf
    gefaehrden wuerde."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {
                "knowledge": [{"id": "kb-real-1", "name": _KB_NAME, "type": "collection"}],
            },
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            files=[{"id": "f-real", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}}],
            models={"p-sibling": sibling_preset},
            fail_delete_model_ids={"p-sibling"},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein fehlgeschlagenes Preset-Delete mit real verknuepftem "
            f"Sibling-Preset muss den Reset VOR KB-/Vektor-/Datei-/Manifest-/"
            f"Neuaufbauschritten abbrechen: exited={exited}\n{out}"
        )
        assert "Preset 'p-sibling' war nicht vorhanden" not in out, (
            "ein echter HTTP-Fehler darf NICHT als bestaetigte Abwesenheit gemeldet werden:\n" + out
        )
        assert "p-sibling' nicht loeschbar" in out, out
        assert "Preset 'p-default' war nicht vorhanden" in out, (
            "ein bestaetigt abwesendes (404) Preset bekommt weiterhin die normale Meldung:\n" + out
        )
        assert "kb-real-1" in http.knowledge, "die KB bleibt bestehen (Bestand an diesem Punkt erhalten)"
        assert "f-real" in http.files, "die Datei bleibt bestehen"
        _assert_zero_writes(http, out, tmp=tmp, expected_preset_delete_attempts=["p-sibling"])
        assert "starte jetzt sauberen Neuaufbau" not in out, (
            "die Erfolgsmeldung 'Reset abgeschlossen — starte jetzt sauberen "
            "Neuaufbau.' darf nach diesem Teilfehler NICHT erscheinen:\n" + out
        )
        assert "abgebrochen" in out.lower(), out


def test_reset_file_cleanup_failure_is_not_lost_behind_later_successful_rebuild():
    """K4 im Reset-Pfad (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3):
    ein echter Datei-Cleanup-Fehler waehrend des Reset-Batches durfte
    bisher hinter einem anschliessend erfolgreichen `run_setup`-Neuaufbau
    und der unqualifizierten 'Reset abgeschlossen'-Meldung verschwinden.
    Jetzt: Batch-Stop bleibt (zweite Datei bleibt unangetastet), der
    nachfolgende Neuaufbau darf unabhaengig fertig werden, aber der GESAMTE
    Lauf endet mit Exit 1 und ohne die unqualifizierte Erfolgsmeldung."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md", "b.md"))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            files=[
                {"id": "f-a", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}},
                {"id": "f-b", "filename": "b.md", "meta": {"collection_name": "kb-real-1"}},
            ],
            fail_delete_file_ids={"f-a"},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein echter Datei-Cleanup-Fehler im Reset darf NICHT hinter "
            f"einem spaeter erfolgreichen Neuaufbau verschwinden: exited={exited}\n{out}"
        )
        assert http.delete_file_attempts == ["f-a"], "Batch-Stop bleibt erhalten -- 'b.md' wird nicht angefasst"
        assert "f-b" in http.files, "die nicht angefasste zweite Datei bleibt im Bestand"
        assert "kb-real-1" in http.deleted_knowledge_ids, "die unabhaengige KB-Entfernung laeuft trotzdem weiter"
        assert "Reset abgeschlossen — starte jetzt sauberen Neuaufbau." not in out, (
            "keine unqualifizierte Reset-Erfolgsmeldung bei echtem Datei-Cleanup-Teilfehler:\n" + out
        )
        assert http.created_knowledge_calls, (
            "der unabhaengige Neuaufbau (run_setup) darf trotzdem fertig werden:\n" + out
        )
        assert "f-a" in out and "ID f-a" in out and "f-b" in out and "ID f-b" in out, (
            "die betroffenen Datei-IDs (fehlgeschlagen + ausgelassen) muessen konkret "
            "benannt werden:\n" + out
        )


def test_reset_kb_delete_http_error_halts_before_manifest_and_rebuild():
    """A-R2: `delete_knowledge()` schlaegt fuer die Reset-KB konkret fehl
    (HTTP 500). Der Lauf muss VOR Dateiloeschung, Manifest-Unlink, der
    'Reset abgeschlossen'-Meldung und dem automatischen run_setup-Neuaufbau
    mit sys.exit(1) enden -- ein bereits vorhandenes lokales Manifest bleibt
    unangetastet, und die bekannte, nur nicht entfernte KB wird NICHT als
    'keine KB gefunden' gemeldet."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        manifest = tmp / ".openwebui-sync.json"
        manifest.write_text('{"existing": true}', encoding="utf-8")
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            files=[{"id": "f-real", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}}],
            fail_delete_knowledge_ids={"kb-real-1"},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein fehlgeschlagenes KB-Delete muss den Reset VOR Manifest/"
            f"Neuaufbau abbrechen: exited={exited}\n{out}"
        )
        assert "kb-real-1" not in http.deleted_knowledge_ids
        assert http.delete_knowledge_attempts == ["kb-real-1"], (
            "K5: der fehlgeschlagene KB-Delete-VERSUCH selbst muss erfasst sein"
        )
        assert "kb-real-1" in http.knowledge, "die KB bleibt bestehen"
        assert http.delete_file_attempts == [], "keine Dateiloeschung nach fehlgeschlagenem KB-Delete"
        assert manifest.read_text(encoding="utf-8") == '{"existing": true}', (
            "das lokale Manifest darf NICHT geloescht werden, solange die alte KB noch existiert"
        )
        assert http.manifest_unlink_attempts == [], (
            "kein Manifest-Unlink-VERSUCH (nicht nur unveraenderter Endzustand) nach diesem Teilfehler"
        )
        assert http.manifest_write_attempts == [], "kein Manifest-Write-VERSUCH nach diesem Teilfehler"
        assert http.created_knowledge_calls == [], "kein Neuaufbau (run_setup) nach diesem Teilfehler"
        assert "starte jetzt sauberen Neuaufbau" not in out, (
            "die Erfolgsmeldung 'Reset abgeschlossen — starte jetzt sauberen "
            "Neuaufbau.' darf nach diesem Teilfehler NICHT erscheinen:\n" + out
        )
        assert "Keine projektzugehörige KB gefunden" not in out, (
            "eine bekannte, nur nicht entfernte KB darf nicht als 'keine KB gefunden' gemeldet werden:\n" + out
        )
        assert "abgebrochen" in out.lower(), out


def test_a2_mixed_list_with_one_unreadable_member_preserves_candidate_file():
    """A-R3: `GET /knowledge/{id}` einer fremden/geschuetzten KB antwortet
    mit HTTP 200 und einer formal gueltigen Liste, die aber EIN unlesbares
    Mitglied enthaelt (weder dict-mit-str-id noch str) neben einem sonst
    gueltigen Eintrag -- `get_knowledge_files()` darf das NICHT
    stillschweigend zu einer kleineren/leeren Liste verkleinern. Die
    Kandidaten-Datei der Ziel-KB bleibt konservativ erhalten."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-old-1", "name": _KB_NAME},
                {"id": "kb-protected-1", "name": "Fremdes Projekt KB"},
            ],
            files=[{"id": "f-maybe-shared", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            knowledge_detail_raw_files={"kb-protected-1": [{"unlesbar": True}, {"id": "f-other"}]},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"exited={exited}\n{out}"
        assert "f-maybe-shared" not in http.deleted_file_ids, (
            "eine formal gueltige, aber teilweise unlesbare Mischliste darf NICHT als "
            "bestaetigte Leer-/Fremdliste gelten"
        )
        assert "f-maybe-shared" in http.files


def test_a2_fully_unreadable_member_list_preserves_candidate_file():
    """Wie oben, aber ALLE Mitglieder der fremden KB sind unlesbar (keine
    einzige gueltige ID, inkl. einer leeren String-ID) -- auch das ist
    KEINE bestaetigte Leerliste."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[
                {"id": "kb-old-1", "name": _KB_NAME},
                {"id": "kb-protected-1", "name": "Fremdes Projekt KB"},
            ],
            files=[{"id": "f-maybe-shared2", "filename": "a.md", "meta": {"collection_name": "kb-old-1"}}],
            knowledge_detail_raw_files={"kb-protected-1": [{"unlesbar": True}, ""]},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"exited={exited}\n{out}"
        assert "f-maybe-shared2" not in http.deleted_file_ids
        assert "f-maybe-shared2" in http.files


def test_a1_sibling_unreadable_knowledge_entry_with_zero_matches_halts_before_any_mutation():
    """A-R3: ein Sibling-Preset hat EINEN nicht interpretierbaren
    `meta.knowledge`-Eintrag (weder dict-mit-str-id) UND sonst keinen
    Treffer auf `old_kb_ids` -- das darf NICHT als 'eindeutig fremd,
    vollstaendig gelesen' durchgehen, weil die Liste gar nicht vollstaendig
    lesbar war. Unterscheidet den legitimen (Test 2), den eindeutig fremden
    (Test 9) und diesen unlesbaren Fall."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"knowledge": [{"unlesbar": True}, {"id": "kb-fully-unrelated"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein nicht interpretierbarer meta.knowledge-Eintrag darf nicht zu "
            f"'eindeutig fremd' werden: exited={exited}\n{out}"
        )
        _assert_zero_writes(http, out, tmp=tmp)


def test_a1_failed_sibling_relink_with_second_independent_success_is_overall_partial_failure():
    """A-R1: zwei Nebenvarianten sind an die ersetzte alte KB gebunden. Der
    Update-Call fuer die erste schlaegt konkret fehl (HTTP 500); die
    zweite, unabhaengige, wird TROTZDEM fertig nachgezogen. Der Gesamtlauf
    endet mit Fehlerstatus (kein 'Setup abgeschlossen!'), die betroffene
    Variante/Preset-/alte+neue-KB-ID werden konkret im Output genannt."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        cfg = dict(_SETUP_CFG)
        cfg["variants"] = dict(_SETUP_CFG["variants"])
        cfg["variants"]["sibling2"] = {
            "preset_id": "p-sibling2", "preset_name": f"{_PROJECT} Ultra",
            "model": "openrouter/deepseek/deepseek-v3.2", "cache": False,
        }
        sibling1 = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {"knowledge": [{"id": "kb-old-1", "name": "Old", "type": "collection"}]},
            "params": {},
        }
        sibling2 = {
            "id": "p-sibling2", "name": f"{_PROJECT} Ultra",
            "base_model_id": "openrouter/mistral/bar",
            "meta": {"knowledge": [{"id": "kb-old-1", "name": "Old", "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling1, "p-sibling2": sibling2},
            new_kb_id="kb-new-1",
            fail_update_model_ids={"p-sibling"},
        )
        exited, out = _run_setup(tmp, http, cfg, _OPTS)
        assert exited == 1, f"ein kaputter Sibling-Link muss den Gesamtlauf mit Exit != 0 beenden: exited={exited}\n{out}"
        assert http.models["p-sibling"]["meta"]["knowledge"] == [
            {"id": "kb-old-1", "name": "Old", "type": "collection"}
        ], "bei HTTP 500 darf der Remote-Zustand NICHT geaendert sein"
        assert http.models["p-sibling2"]["meta"]["knowledge"] == [
            {"id": "kb-new-1", "name": _KB_NAME, "type": "collection"}
        ], "der unabhaengige zweite Relink muss trotzdem fertig laufen"
        assert "Setup abgeschlossen!" not in out, "kein pauschales Erfolgsschild trotz kaputtem Sibling-Link"
        assert "p-sibling" in out and "kb-old-1" in out and "kb-new-1" in out, (
            "Variante/Preset-ID/alte+neue KB-ID muessen konkret genannt werden:\n" + out
        )


def test_a1_chosen_preset_bound_to_foreign_kb_halts_before_any_mutation():
    """A-R3 Zielbindung des GEWAEHLTEN Presets: `old_kb_ids` wird allein ueber
    Namensgleichheit (`kb.name == kb_name`) bestimmt. Zeigt das in DIESEM Lauf
    gewaehlte, bereits installierte Preset (`p-default`) aktuell auf eine KB,
    die die Namenssuche NICHT als `old_kb_ids` erfasst hat, ist die Zielbindung
    nicht vollstaendig -- das Setup darf NICHT mit einer geratenen Bindung
    destruktiv weiterfahren, sondern muss VOR jeder Mutation halten. Deckt den
    Guard-Pfad (setup.py:4516-4551) ab, den die uebrigen A1-Tests nur ueber den
    bestaetigten-404-Zweig streifen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        chosen_preset = {
            "id": "p-default", "name": _PROJECT,
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            # zeigt auf eine KB, die NICHT ueber den Namen als old_kb_ids
            # gefunden wurde -- die Namenssuche hat sie verfehlt.
            "meta": {"knowledge": [{"id": "kb-fremd-1", "name": "Fremd", "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],  # old_kb_ids = {kb-old-1}
            models={"p-default": chosen_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein gewaehltes Preset, das auf eine ueber den Namen NICHT gefundene "
            f"KB zeigt, muss VOR jeder Mutation halten: exited={exited}\n{out}"
        )
        assert "p-default" in http.get_model_calls, "die Zielbindung muss das gewaehlte Preset wirklich gelesen haben"
        assert "kb-fremd-1" in out, "die abweichende, nicht gebundene KB muss konkret genannt werden:\n" + out
        _assert_zero_writes(http, out, tmp=tmp)


# ── N3-Nachzug (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3, K1-K5) ─────
# Die vorherigen gruenen Tests enthielten noch einen ausdruecklich falschen
# Reset-Sollwert (K1, oben korrigiert) bzw. deckten K2/K3.1/K3.2 gar nicht
# ab. Die folgenden Tests schliessen genau diese benannten Luecken.


def test_a_r0_run_setup_preset_delete_http_401_after_confirmed_presence_is_not_treated_as_absence():
    """K2 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3: 'delete_model
    789-802 liefert fuer jedes 401 (False, True)'): ein per GET200 VORHER
    bestaetigt vorhandenes Preset, dessen Delete-Versuch mit HTTP 401 statt
    200/404 antwortet, darf NICHT als bestaetigte Abwesenheit gelten -- ein
    echter Auth-/Scope-Fehler auf ein bekanntes Objekt ist kein 'war schon
    weg'. Deckt den Unterschied zu einem bestaetigten 404 (409?) bzw. einem
    generischen 500 ab (s. test_a_r0_..._with_null_follow_up_mutation)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        chosen_preset = {
            "id": "p-default", "name": _PROJECT,
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {"knowledge": [{"id": "kb-old-1", "name": _KB_NAME, "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-default": chosen_preset},
            fail_delete_model_401_ids={"p-default"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein per GET200 bestaetigt vorhandenes Preset, das bei Delete "
            f"HTTP 401 liefert, darf NICHT als bestaetigte Abwesenheit "
            f"durchlaufen: exited={exited}\n{out}"
        )
        assert "p-default" in http.get_model_calls, "die Praesenz muss vorher tatsaechlich GEPRUEFT worden sein"
        _assert_zero_writes(http, out, tmp=tmp, expected_preset_delete_attempts=["p-default"])
        assert "war nicht vorhanden" not in out, (
            "HTTP 401 nach bestaetigtem GET200 darf NICHT als 'war nicht vorhanden' gemeldet werden:\n" + out
        )


def test_a1_chosen_preset_confirmed_absent_via_404_skips_delete_attempt_entirely():
    """WP-N4-A1: ein per GET404 im Preflight bestaetigt ABWESENDES gewaehltes
    Preset darf in der Deletephase gar keinen Delete-POST mehr auslösen --
    der im Preflight schon getroffene Praesenzentscheid wird jetzt
    tatsaechlich bis zum Delete mitgefuehrt statt nur gelesen und dort
    wieder verworfen. Absicherung: `fail_delete_model_401_ids` traegt fuer
    GENAU diese ID einen simulierten HTTP-401 -- wuerde `delete_model()`
    trotzdem aufgerufen, waere das (bei einem bestaetigt abwesenden Preset)
    ein erfundener Fehler. Normaler Aufbau bleibt moeglich."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={},  # p-default bewusst NICHT vorhanden -> echtes 404
            fail_delete_model_401_ids={"p-default"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), (
            f"ein bestaetigt abwesendes gewaehltes Preset darf den Aufbau "
            f"NICHT anhalten: exited={exited}\n{out}"
        )
        assert "p-default" in http.get_model_calls, "die Abwesenheit muss tatsaechlich GEPRUEFT worden sein"
        assert "p-default" not in http.deleted_model_ids, (
            "ein bestaetigt abwesendes Preset darf GAR KEINEN Delete-POST mehr "
            "erhalten -- der simulierte Delete-401-Fallenstein darf nicht erreicht werden"
        )
        assert "Kein vorhandenes Preset für Variante 'default' — Neuanlage." in out, out


def test_a1_chosen_preset_read_error_halts_before_any_mutation():
    """Vorabhalt-Zweig fuer das GEWAEHLTE Preset selbst (nicht nur eine
    Nebenvariante, s. test_a1_sibling_read_error_halts_before_any_mutation):
    ein echter Lesefehler (HTTP 500, nicht 404) auf `get_model('p-default')`
    ist KEIN bestaetigtes Nichtvorhandensein -- Setup muss VOR jeder
    Mutation (inkl. Delete) abbrechen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            model_read_error_ids={"p-default"},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein Lesefehler beim gewaehlten Preset muss hart abbrechen: exited={exited}\n{out}"
        )
        assert "p-default" in http.get_model_calls
        _assert_zero_writes(http, out, tmp=tmp)


def test_reset_preset_bound_to_foreign_kb_halts_before_any_preset_delete():
    """K3 Punkt 1 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3): `run_reset`
    las bisher KEINE Presetbeziehungen vor dem ersten Presetdelete -- ein
    konfiguriertes Preset mit einer Fremd-KB-Bindung waere schon geloescht
    gewesen, bevor ein spaeterer Setup-Guard ueberhaupt lesen konnte (N2 A1
    verlangte denselben begrenzten Identitaetsentscheid im Reset). Dieselbe
    begrenzte Zielbindung wie im Setup-Preflight fuer das gewaehlte Preset
    (s. test_a1_chosen_preset_bound_to_foreign_kb_halts_before_any_mutation)
    muss VOR dem ersten Reset-Presetdelete greifen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {"knowledge": [{"id": "kb-fremd-1", "name": "Fremd", "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein Reset-Preset mit Bindung an eine ueber den Namen NICHT "
            f"gefundene KB muss VOR dem ersten Presetdelete halten: exited={exited}\n{out}"
        )
        # WP-N4-A2: vorher nur Preset-/KB-Loeschzaehler geprueft (General-
        # Review INTERNAL_CODE_REVIEW.md §4 Punkt 3) -- der gemeinsame Helfer
        # deckt jetzt den VOLLSTAENDIGEN Ledger ab, inkl. Manifest-Versuchen.
        _assert_zero_writes(http, out, tmp=tmp)
        assert "kb-fremd-1" in out, "die abweichende KB muss konkret genannt werden:\n" + out
        assert "p-sibling" in http.get_model_calls, "die Zielbindung muss das Reset-Preset wirklich gelesen haben"


def test_reset_preset_confirmed_absent_via_404_skips_delete_attempt_entirely():
    """WP-N4-A1 im Reset-Pfad: ein per GET404 bestaetigt abwesendes
    konfiguriertes Preset bekommt in der Delete-Schleife KEINEN Delete-POST
    mehr -- der Preflight-Entscheid wird tatsaechlich verwendet statt nur
    gelesen und verworfen. Ein simulierter 401-Fallenstein fuer GENAU diese
    ID beweist, dass `delete_model()` dafuer gar nicht aufgerufen wird. Das
    andere, tatsaechlich vorhandene konfigurierte Preset wird normal
    entfernt, der Reset laeuft bis zum Neuaufbau durch."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {"knowledge": [{"id": "kb-real-1", "name": _KB_NAME, "type": "collection"}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            files=[{"id": "f-real", "filename": "a.md", "meta": {"collection_name": "kb-real-1"}}],
            models={"p-sibling": sibling_preset},  # p-default bewusst NICHT vorhanden -> echtes 404
            fail_delete_model_401_ids={"p-default"},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited in (None, 0), f"exited={exited}\n{out}"
        assert "p-default" not in http.deleted_model_ids, (
            "ein bestaetigt abwesendes Preset darf GAR KEINEN Delete-POST mehr "
            "erhalten -- der simulierte Delete-401-Fallenstein darf nicht erreicht werden"
        )
        assert "p-sibling" in http.deleted_model_ids, "das tatsaechlich vorhandene Preset wird normal geloescht"
        assert "Preset 'p-default' war nicht vorhanden" in out, out
        assert "kb-real-1" in http.deleted_knowledge_ids, "der Reset laeuft bis zur KB-Entfernung durch"


def test_reset_preset_read_error_halts_before_any_preset_delete():
    """Vorabhalt-Zweig in `run_reset`s Presetpreflight: ein echter Lesefehler
    (HTTP 500, nicht 404) auf einem konfigurierten Preset ist KEIN
    bestaetigtes Nichtvorhandensein -- der Reset muss VOR dem ersten
    Presetdelete abbrechen."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-real-1", "name": _KB_NAME}],
            model_read_error_ids={"p-default"},
            new_kb_id="kb-rebuilt-1",
        )
        exited, out = _run_reset(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein Lesefehler auf ein konfiguriertes Reset-Preset muss VOR dem "
            f"ersten Presetdelete abbrechen: exited={exited}\n{out}"
        )
        _assert_zero_writes(http, out, tmp=tmp)


def test_a1_sibling_mixed_knowledge_list_with_target_hit_and_unreadable_entry_halts_before_any_mutation():
    """K3 Punkt 2 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3):
    `knowledge=[{"id":"kb-old-1"},{}]` wurde bisher trotz unlesbarem zweiten
    Element als Einzeltreffer zum Relink vorgemerkt, weil der
    Unklarheitsguard nur bei NULL Treffern ausgewertet wurde. Ein
    bestaetigter Zieltreffer macht ein zusaetzliches unlesbares Element
    NICHT sicher -- muss VOR jeder Mutation halten (unterscheidet sich von
    test_a2_mixed_list_with_one_unreadable_member_preserves_candidate_file,
    das die FREMDE/geschuetzte KB-Detailliste betrifft, nicht die
    Sibling-Zugehoerigkeitsliste hier)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        sibling_preset = {
            "id": "p-sibling", "name": f"{_PROJECT} Budget",
            "base_model_id": "openrouter/mistral/foo",
            "meta": {"knowledge": [{"id": "kb-old-1"}, {}]},
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-sibling": sibling_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein bestaetigter Zieltreffer neben einem unlesbaren Element "
            f"darf NICHT relinkt werden -- Halt VOR jeder Mutation erwartet: "
            f"exited={exited}\n{out}"
        )
        _assert_zero_writes(http, out, tmp=tmp)


def test_a1_chosen_preset_knowledge_null_is_not_treated_as_confirmed_empty_halts_before_any_mutation():
    """K3 Punkt 3 (01_GENERAL_URTEIL_UND_N2_ERRATUM.md Abschnitt 3):
    `meta.knowledge=None`/fehlendes Feld wurde bisher ueber `or []` wie eine
    bestaetigte Leerliste behandelt. Ohne belegte Backend-Semantik darf das
    NICHT gelten -- Halt VOR jeder Mutation. Eine echte bestaetigte
    Leerliste ([]) bleibt an anderer Stelle weiter zulaessig (nur der
    isinstance-Check greift dafuer, kein Halt)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        _build_repo(tmp, filenames=("a.md",))
        chosen_preset = {
            "id": "p-default", "name": _PROJECT,
            "base_model_id": "openrouter/deepseek/deepseek-v3.2",
            "meta": {},  # kein "knowledge"-Feld -> .get("knowledge") == None
            "params": {},
        }
        http = _SetupHttpDouble(
            knowledge=[{"id": "kb-old-1", "name": _KB_NAME}],
            models={"p-default": chosen_preset},
            new_kb_id="kb-new-1",
        )
        exited, out = _run_setup(tmp, http, _SETUP_CFG, _OPTS)
        assert exited == 1, (
            f"ein fehlendes/None `meta.knowledge` des gewaehlten Presets darf "
            f"NICHT wie eine bestaetigte Leerliste behandelt werden: exited={exited}\n{out}"
        )
        assert "p-default" in http.get_model_calls
        _assert_zero_writes(http, out, tmp=tmp)


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
