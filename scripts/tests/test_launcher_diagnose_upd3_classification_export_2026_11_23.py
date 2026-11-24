#!/usr/bin/env python3
"""scripts/tests/test_launcher_diagnose_upd3_classification_export_2026_11_23.py —
ZR-UPDATE-RESUME-REPARATUR-20261123-r1, UPD-3 (03_UPDATE_UND_KB.md
Implementierungsauftrag 4, Abnahmefälle U3/U8/U9, 06_ENDUSER_ABNAHME.md A3/A5/A6).

Ursache (verifiziert am echten Aufrufer `action_diagnose()`, VOR diesem
Fix): `get_model() is None` wurde PAUSCHAL als "Preset fehlt" gemeldet
(egal ob 404, 401/403 oder Timeout/Formfehler), und ein HTTP-/Antwortfehler
im Query-Client ergab `result.get("hits", 0) == 0` -- ununterscheidbar von
einer tatsächlich leeren KB ("KB-Retrieval lieferte 0 Treffer"). Beide
Fälle hätten fälschlich automatische Reparaturvorschläge ("install"/"sync")
ausgelöst statt "nicht prüfbar" zu melden. Außerdem gab es KEINEN lokalen,
redigierten Diagnoseexport (03 §4 Absatz 3 / 06 U9/A6) -- das Menü [6]
konnte keinen Bericht speichern.

Fix: `_preset_read_status_label()` trennt 404 (absent) von 401/403
(auth_error) von jeder anderen unklaren Antwort (unclear); `action_diagnose`
liest zusätzlich `result.get("code")` aus `query_kb` BEVOR es `hits`
interpretiert. `_write_diagnose_export()` schreibt eine rein lokale,
redigierte Textdatei aus den bereits oben erhobenen Befunden -- ohne dabei
selbst einen Request/Upload/Unlink auszulösen.

Treibt den ECHTEN Aufrufer `scripts.launcher.action_diagnose()` über einen
Fake-API-Client (gleiche Double-Grenze wie die UPD-1/2-Testdateien: nur die
äußere API-Schicht wird ersetzt). Kein echtes Netz, kein echtes Backend."""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

# `scripts/launcher.py` fuegt sich beim Import selbst via `sys.path.insert(
# 0, str(REPO / "scripts"))` vor den Repo-Root ein (s. launcher.py:70-72).
# In einem GESAMTEN `python3 -m unittest -q`-Lauf ab Repo-Root bleibt dieser
# Pfadeintrag danach fuer den REST des Prozesses stehen -- `scripts/tests/`
# hat ein eigenes `__init__.py`, also wuerde ein SPAETER entdecktes `import
# tests.mmo_sim` dann `scripts/tests` statt des echten Top-Level-`tests/`-
# Pakets finden (`ModuleNotFoundError: No module named 'tests.mmo_sim'` in
# VOELLIG unabhaengigen Testdateien). Exakt dieselbe, bereits dokumentierte
# Konvention wie `scripts/tests/test_launcher_action_update.py`: den neu
# hinzugekommenen Pfadeintrag sofort nach dem Import wieder entfernen.
_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_action_update import (  # noqa: E402
    ActionUpdateTestCase, _ScriptedPrompt,
)


class _FakeDiagClient:
    """Nur die Methoden, die `action_diagnose`/`_diagnose_has_errors`
    tatsächlich aufrufen. Zählt mutierende Aufrufe mit -- ein reiner
    Diagnose-/Export-Lauf DARF keinen einzigen davon auslösen (A6)."""

    def __init__(self, *, health=True, auth=True, model=None,
                 last_model_status=None, query_result=None,
                 list_files_result=None, last_files_complete=True,
                 get_file_content_result=None):
        self.health = health
        self.auth = auth
        self._model = model
        self.last_model_status = last_model_status
        self._query_result = query_result
        self.add_file_calls = 0
        self.delete_calls = 0
        self.unlink_calls = 0
        # U-R2-Restnachzug (UPDATE_UX_REVIEW.md R1): `_check_kb_content_binding`
        # ruft `list_files()` + `last_files_complete` auf, um den Inhalts-/
        # Bindungsabgleich der konfigurierten Wissensdateien zu lesen (reine
        # Lesung, kein Upload/Unlink). Default `[]`/`True` -- Tests, die
        # diesen Zweig nicht gezielt prüfen, landen damit in "unbestimmt"
        # ("keine Datei in der KB gefunden"), nicht in einem Crash.
        self._list_files_result = list_files_result if list_files_result is not None else []
        self.last_files_complete = last_files_complete
        # U1a (UPDATE_UX_REVIEW.md U1a, 02_RESTAUFTRAG.md §U1): bei
        # abweichendem Metadatenhash ruft `_check_kb_content_binding` jetzt
        # denselben bestehenden Content-Fallback wie der reguläre Sync
        # (`get_file_content`) auf. Default `None` ("nicht lesbar" ->
        # unbestimmt) -- Tests, die gezielt echte abweichende Bytes (Drift)
        # belegen wollen, setzen `get_file_content_result` explizit.
        self._get_file_content_result = get_file_content_result

    def get_file_content(self, file_id):
        return self._get_file_content_result

    def check_health(self):
        return self.health

    def check_auth(self):
        return self.auth

    def get_model(self, preset_id):
        return self._model

    def query_kb(self, kb_id, q, k=5):
        return self._query_result

    def list_files(self):
        return self._list_files_result

    def add_file_to_knowledge(self, *a, **kw):
        self.add_file_calls += 1
        return True

    def delete_file(self, *a, **kw):
        self.delete_calls += 1
        return True

    def remove_file_from_knowledge(self, *a, **kw):
        self.unlink_calls += 1
        return True


_LEGACY_SETUP_JSON = """{
  "project": "ZEITRISS",
  "masterprompt": "masterprompt.md",
  "params": {},
  "preset_id": "zr-preset",
  "preset_name": "ZEITRISS Preset",
  "verify": {"query": "testfrage", "top_k": 3}
}
"""


class _DiagnoseTestCase(ActionUpdateTestCase):
    """Isoliert `action_diagnose()`: echter Code, Fake-Client, kein Netz."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        (self.repo / "setup.json").write_text(_LEGACY_SETUP_JSON, encoding="utf-8")
        self._set_repo(self.repo)
        # Basisklasse patcht `_ensure_owui_env` auf False (kein Key) --
        # dieser Testfall braucht den Preset-/KB-Zweig, also ECHT überschreiben.
        self._patch(mock.patch.object(L, "_ensure_owui_env", lambda: True))
        self._patch(mock.patch.dict(L.os.environ, {"OPENWEBUI_API_KEY": "test-key-not-real"}))
        self._patch(mock.patch.object(L, "print_status_block", lambda: None))
        # Block A (ZR-PR3317-Nachzug 2026-11-23): `action_diagnose` fuehrt nach dem
        # Preset-/KB-Zweig einen ORTHOGONALEN LiteLLM-/Docker-Check aus
        # (`_litellm_ok()` + `_cmd_available("docker")`, launcher.py ~2277). Dessen
        # Ergebnis haengt vom realen Host ab: auf einem Runner MIT docker, aber OHNE
        # laufenden LiteLLM-Cache (CI ubuntu-latest) injiziert er ein autofixbares
        # Finding -> die Folgefrage "Soll ich die empfohlenen Schritte jetzt
        # ausfuehren?" erscheint, und die Preset-/KB-/Export-Faelle (die nur ihren
        # eigenen Zweig steuern) laufen aus den Prompts (reproduziert an
        # launcher.py:2330). Lokal ohne docker blieb der Check still -> die Fixtures
        # waren hostabhaengig gruen/rot. Dieser Check ist fuer die Diagnose-
        # Klassifikation/-Export-Faelle irrelevant; deshalb deterministisch auf
        # "LiteLLM aktiv" pinnen (kein Finding), damit jede Fixture hostunabhaengig
        # genau ihren Gegenstand prueft. Die strengen A6-/Mutations-/Klassifikations-
        # Asserts bleiben unberuehrt.
        self._patch(mock.patch.object(L, "_litellm_ok", lambda: (True, None)))

    def _run_diagnose(self, client, prompts: list[str]) -> tuple[str, "_ScriptedPrompt"]:
        self._patch(mock.patch.object(
            L.setup_module, "APIClient", lambda *a, **kw: client,
        ))
        scripted = self._set_prompt(prompts)
        buf = io.StringIO()
        with redirect_stdout(buf):
            L.action_diagnose()
        return buf.getvalue(), scripted


class TestPresetReadStatusLabelIsolated(unittest.TestCase):
    """Ebene 1: `_preset_read_status_label` pur, ohne `action_diagnose`."""

    def test_404_is_absent(self):
        client = _FakeDiagClient(last_model_status=404)
        self.assertEqual(L._preset_read_status_label(client), "absent")

    def test_401_and_403_are_auth_error(self):
        self.assertEqual(
            L._preset_read_status_label(_FakeDiagClient(last_model_status=401)), "auth_error",
        )
        self.assertEqual(
            L._preset_read_status_label(_FakeDiagClient(last_model_status=403)), "auth_error",
        )

    def test_everything_else_is_unclear(self):
        for status in (0, 500, None, 200):
            with self.subTest(status=status):
                client = _FakeDiagClient(last_model_status=status)
                self.assertEqual(L._preset_read_status_label(client), "unclear")


class TestActionDiagnosePresetClassification(_DiagnoseTestCase):
    def test_u3_auth_error_on_preset_read_offers_rekeys_not_install(self):
        """VORHER (Bug): `get_model() is None` bei HTTP 401 wurde als
        "Preset existiert nicht" gemeldet und schlug "install" vor --
        ein Auth-Problem wurde dadurch fälschlich als fehlende Installation
        interpretiert (Risiko: unnötiges Re-Setup statt Key-Tausch)."""
        client = _FakeDiagClient(model=None, last_model_status=401)
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("Auth-/Berechtigungsfehler", out)
        self.assertIn("API-Keys ändern", out)
        self.assertNotIn("existiert nicht", out)
        self.assertEqual(client.add_file_calls, 0)
        self.assertEqual(client.delete_calls, 0)

    def test_u3_unclear_preset_read_is_not_prüfbar_not_install(self):
        """Ein formfalscher/unbekannter Lesefehler (hier: HTTP 500) darf
        NICHT als bestätigtes "Preset fehlt" gelten -- sonst würde die
        Diagnose einen Install-Vorschlag auf Basis einer bloß unklaren
        Antwort auslösen (03 §4: "Unsichere ... Antworten als unbestimmt
        zeigen")."""
        client = _FakeDiagClient(model=None, last_model_status=500)
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("nicht sicher lesbar", out)
        self.assertIn("nicht prüfbar", out)
        self.assertNotIn("existiert nicht", out)

    def test_u3_404_preset_read_is_genuinely_absent_and_offers_install(self):
        """Gegenfall: ein bestätigtes 404 bleibt "Preset fehlt" + Install-
        Vorschlag -- die Unterscheidung darf den echten Fall nicht verdecken."""
        client = _FakeDiagClient(model=None, last_model_status=404)
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("existiert nicht", out)
        self.assertIn("Komplett-Setup", out)


class TestActionDiagnoseKbRetrievalClassification(_DiagnoseTestCase):
    def _preset_with_kb(self) -> dict:
        return {"name": "P", "meta": {"knowledge": [{"id": "kb-123"}]}}

    def test_u3_http_error_on_query_is_not_prüfbar_not_kb_leer(self):
        """VORHER (Bug): ein Backend-/Netzfehler im Query-Client liefert
        laut setup.py `query_kb`-Doku ebenfalls `hits=0` -- das wurde
        ununterscheidbar von einer tatsächlich leeren KB als "KB-Retrieval
        lieferte 0 Treffer" gemeldet und schlug automatischen Sync vor.
        NACH dem Fix trennt `result['code']` beide Fälle."""
        client = _FakeDiagClient(
            model=self._preset_with_kb(),
            query_result={"code": 500, "hits": 0},
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("nicht prüfbar", out)
        self.assertIn("Backend-/Netzfehler", out)
        self.assertNotIn("KB-Retrieval lieferte 0 Treffer", out)
        self.assertNotIn("KB ist leer", out)

    def test_u3_real_empty_kb_still_reported_as_empty(self):
        """Gegenfall: HTTP 200 mit `hits=0` ist eine ECHTE leere KB und muss
        weiterhin so gemeldet werden (sonst würde die Fehlerklassen-Trennung
        einen echten Befund verschlucken)."""
        client = _FakeDiagClient(
            model=self._preset_with_kb(),
            query_result={"code": 200, "hits": 0},
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("KB-Retrieval lieferte 0 Treffer", out)
        self.assertNotIn("nicht prüfbar", out)

    def test_u3_successful_retrieval_reported_ok(self):
        client = _FakeDiagClient(
            model=self._preset_with_kb(),
            query_result={"code": 200, "hits": 2},
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("KB-Retrieval OK", out)


class TestDiagnoseExportIsReadOnlyAndRedacted(_DiagnoseTestCase):
    def test_u9_a6_export_declined_writes_nothing(self):
        client = _FakeDiagClient(
            model={"name": "P", "meta": {"knowledge": [{"id": "kb-1"}]}},
            query_result={"code": 200, "hits": 1},
        )
        self._run_diagnose(client, prompts=["n"])  # "n" auf Exportfrage -> alles grün, keine zweite Frage
        export_dir = self.repo / "scripts" / "diagnose-export"
        self.assertFalse(export_dir.exists())

    def test_u9_a6_export_accepted_writes_local_file_without_further_requests(self):
        """A6: "Diagnose/Zurück/Bericht speichern" löst KEINEN Upload,
        Unlink, Reindex oder Modellrequest aus -- der Export formatiert nur
        bereits oben erhobene Werte."""
        client = _FakeDiagClient(
            model={"name": "P", "meta": {"knowledge": [{"id": "kb-1"}]}},
            query_result={"code": 500, "hits": 0},
        )
        out, _ = self._run_diagnose(client, prompts=["j"])
        export_dir = self.repo / "scripts" / "diagnose-export"
        files = list(export_dir.glob("diagnose-*.txt"))
        self.assertEqual(len(files), 1, f"erwartete genau eine Exportdatei, stdout={out!r}")
        text = files[0].read_text("utf-8")
        self.assertIn("Prüfzeit", text)
        self.assertIn("KB-Retrieval", text)
        self.assertIn("500", text)
        for forbidden in ("test-key-not-real", "Authorization", "sk-"):
            self.assertNotIn(forbidden, text)
        self.assertEqual(client.add_file_calls, 0)
        self.assertEqual(client.delete_calls, 0)
        self.assertEqual(client.unlink_calls, 0)
        self.assertIn("gespeichert", out)

    def test_u9_a6_legit_missing_litellm_cache_shows_product_branch_and_keeps_export_local(self):
        """Block A (ZR-PR3317-Nachzug 2026-11-23) — Gegenstueck zum gepinnten
        Normalfall: der LEGITIME fehlende LiteLLM-Cache (docker vorhanden, Cache
        aus) MUSS den Produktzweig 'Empfohlene naechste Schritte' + die
        zusaetzliche Frage 'Soll ich die empfohlenen Schritte jetzt ausfuehren?'
        zeigen. Diese Zusatzfrage wird hier BEWUSST mit 'n' beantwortet (nicht
        ausfuehren). Der redigierte lokale Export bleibt rein lokal und loest
        keinen Upload/Unlink/Modellrequest aus. Beweist, dass der Fix den
        Produktzweig NICHT entfernt, sondern nur die orthogonale Env-Abhaengigkeit
        der beiden Kern-Exportfaelle hermetisch pinnt."""
        # Env EXPLIZIT auf 'legitim fehlender Cache' setzen -- ueberschreibt den
        # setUp-Pin (_litellm_ok aktiv) fuer genau diesen Fall:
        self._patch(mock.patch.object(L, "_litellm_ok", lambda: (False, None)))
        self._patch(mock.patch.object(
            L, "_cmd_available", lambda name: True if name == "docker" else False,
        ))
        client = _FakeDiagClient(
            model={"name": "P", "meta": {"knowledge": [{"id": "kb-1"}]}},
            query_result={"code": 200, "hits": 1},
        )
        # [1] Export? -> "j"  [2] Schritte jetzt ausfuehren? -> "n" (bewusst abgelehnt)
        out, _ = self._run_diagnose(client, prompts=["j", "n"])
        export_dir = self.repo / "scripts" / "diagnose-export"
        files = list(export_dir.glob("diagnose-*.txt"))
        self.assertEqual(len(files), 1, f"Export sollte lokal geschrieben sein, stdout={out!r}")
        # Produktzweig wurde erreicht (fehlender Cache als Empfehlung, nicht entfernt):
        self.assertIn("LiteLLM-Cache", out)
        self.assertIn("Empfohlene nächste Schritte", out)
        # Bewusstes 'n' auf die Zusatzfrage -> keine Auto-Reparatur, keine Mutation:
        self.assertEqual(client.add_file_calls, 0)
        self.assertEqual(client.delete_calls, 0)
        self.assertEqual(client.unlink_calls, 0)


class TestActionDiagnoseContentAndPersistedSyncStatus(_DiagnoseTestCase):
    """U-R2 kleinster Nachzug (ZR-PR3317-Nachzug 20261123): bisher prüfte
    `action_diagnose` nur Presetexistenz/KB-ID/Retrievalhit -- weder der
    aktive Masterprompt gegen das Soll noch der persistierte Sync-Status
    beeinflussten die Entscheidung. Reproduziert am echten Aufrufer mit dem
    im U-R2-Review beschriebenen Fixture (alter Masterprompt, offener
    Syncstatus, aber erfolgreicher Retrievalhit)."""

    def _preset(self, system_text: str) -> dict:
        return {
            "name": "P",
            "meta": {"knowledge": [{"id": "kb-1"}]},
            "params": {"system": system_text},
        }

    def _write_confirmed_kb_file(self, name: str = "wissen.md", content: str = "KB-INHALT\n") -> list[dict]:
        """U-R2-Restnachzug (UPDATE_UX_REVIEW.md R1): legt genau EINE lokale
        Wissensdatei (`kb/`-Strategie von `discover_knowledge_files`) an und
        liefert das passende `list_files()`-Fixture, dessen SHA-256
        (`meta.file_hash`) dem lokalen Inhalt NACHWEISLICH entspricht -- der
        volle Positivfall für `_check_kb_content_binding` (Status "ok")."""
        kb_dir = self.repo / "kb"
        kb_dir.mkdir(exist_ok=True)
        (kb_dir / name).write_text(content, encoding="utf-8")
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return [{
            "id": "file-confirmed-1",
            "filename": name,
            "meta": {"collection_name": "kb-1", "file_hash": sha},
        }]

    def test_masterprompt_drift_blocks_alles_gruen_and_offers_sync(self):
        (self.repo / "masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        client = _FakeDiagClient(
            model=self._preset("ALTER-INHALT\n"),
            query_result={"code": 200, "hits": 1},
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("Aktiver Masterprompt unterscheidet sich vom Soll", out)
        self.assertNotIn("Alle Prüfungen grün", out)
        self.assertIn("Automatischer Sync", out)

    def test_masterprompt_match_reports_ok_and_stays_gruen(self):
        """U1 (c): mp-Match ALLEIN genügt nicht für Gesamtgrün -- erst wenn
        AUCH der persistierte Sync-Status und der tatsächliche KB-Inhalts-/
        Bindungsabgleich bestätigt sind (hier: alle drei), bleibt das
        Ergebnis grün. Reiner mp-Match bei unbestimmtem Rest wird separat in
        `test_missing_masterprompt_file_is_unbestimmt_not_ok_not_drift` /
        `test_persisted_sync_status_ok_without_failed_files_stays_gruen`
        geprüft."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "ok", "kb_confirmed": 1, "kb_total": 1, "kb_failed": [],
            "sync_at": "2026-11-22T09:00:00",
        }), encoding="utf-8")
        list_files_result = self._write_confirmed_kb_file()
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertIn("Aktiver Masterprompt entspricht dem Soll", out)
        self.assertIn("Inhalt/Bindung aller 1 konfigurierten Wissensdatei(en) per SHA-256 bestätigt", out)
        self.assertIn("Alle Prüfungen grün", out)

    def test_missing_masterprompt_file_is_unbestimmt_not_ok_not_drift(self):
        """U1 (a) Gegenfall (UPDATE_UX_REVIEW.md R1, Fixture 1: 'Lokaler
        MP-Sollpfad fehlt; kein Syncstatus vorhanden; ... Retrievalhit
        vorhanden' -> VORHER 'Alle Prüfungen grün', Re-Check False). Kein
        Soll vorhanden UND kein Sync-Status gespeichert -- beide bleiben
        unbestimmt, kein implizites Gesamtgrün und kein falscher
        Fehlerbefund. Re-Check muss dieselbe Unbestimmtheit sehen."""
        client = _FakeDiagClient(
            model=self._preset("irrelevant"),
            query_result={"code": 200, "hits": 1},
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertIn("nicht auffindbar", out)
        self.assertNotIn("unterscheidet sich vom Soll", out)
        self.assertNotIn("Alle Prüfungen grün", out)
        self.assertIn("Nicht alle Prüfungen abschließend bestätigt (unbestimmt)", out)
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertTrue(L._diagnose_has_errors(), "Re-Check muss dieselbe Unbestimmtheit wie die UI sehen")

    def test_persisted_sync_status_failed_blocks_alles_gruen(self):
        """U-R2-Witness: sync_status=failed, kb_confirmed=18/19, offene
        Datei -- durfte bisher die Diagnoseentscheidung NICHT beeinflussen."""
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "failed",
            "kb_confirmed": 18,
            "kb_total": 19,
            "kb_failed": ["sl-referenz.md"],
            "sync_failed_at": "2026-11-20T10:00:00",
        }), encoding="utf-8")
        client = _FakeDiagClient(
            model=self._preset(""),
            query_result={"code": 200, "hits": 1},
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("Wissensdateien laut letztem Sync offen", out)
        self.assertIn("sl-referenz.md", out)
        self.assertNotIn("Alle Prüfungen grün", out)

    def test_persisted_sync_status_ok_without_failed_files_stays_gruen(self):
        """U1 (c): historisch bestätigter Sync allein genügt nicht -- erst
        mit zusätzlich bestätigtem mp-Match UND tatsächlichem KB-Inhalts-/
        Bindungsabgleich (hier: alle drei bestätigt) bleibt Gesamtgrün."""
        self.repo.joinpath("masterprompt.md").write_text("", encoding="utf-8")
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "ok",
            "kb_confirmed": 19,
            "kb_total": 19,
            "kb_failed": [],
            "sync_at": "2026-11-22T09:00:00",
        }), encoding="utf-8")
        list_files_result = self._write_confirmed_kb_file()
        client = _FakeDiagClient(
            model=self._preset(""),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertIn("letzter Wissensabgleich bestätigt", out)
        self.assertIn("Alle Prüfungen grün", out)

    def test_recheck_matches_ui_on_masterprompt_drift(self):
        """UI (`action_diagnose`) und Re-Check (`_diagnose_has_errors`)
        müssen denselben belegten Status verwenden -- ein Re-Check, der auf
        Basis des alten Checks 'grün' meldet, würde den Auto-Fix-Abschluss
        fälschlich als erfolgreich darstellen."""
        (self.repo / "masterprompt.md").write_text("SOLL\n", encoding="utf-8")
        client = _FakeDiagClient(model=self._preset("ALT\n"), query_result={"code": 200, "hits": 1})
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertTrue(L._diagnose_has_errors())

    def test_recheck_matches_ui_on_persisted_sync_status_offen(self):
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "failed", "kb_failed": ["sl-referenz.md"],
        }), encoding="utf-8")
        client = _FakeDiagClient(model=self._preset(""), query_result={"code": 200, "hits": 1})
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertTrue(L._diagnose_has_errors())

    def test_u1_b_mp_match_and_historical_sync_ok_but_active_kb_content_stale_blocks_gruen(self):
        """U1 (b) — UPDATE_UX_REVIEW.md R1, Fixture 2 wörtlich: 'Aktiver MP
        passt; gespeicherter Abgleich meldet historisch 1/1 okay; derselbe
        aktive KB-Dateiname enthält inzwischen alten Inhalt, lokal liegt
        neuer Inhalt; ein Retrievalhit vorhanden.' VORHER: 'Alle Prüfungen
        grün', Re-Check ebenfalls ohne Fehler, obwohl kein Files-/Contentread
        je ausgeführt wurde. Ein Retrievalhit + historisches
        'sync_status=ok' dürfen den tatsächlich veralteten Inhalt NICHT
        überstimmen."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "ok", "kb_confirmed": 1, "kb_total": 1, "kb_failed": [],
            "sync_at": "2026-11-22T09:00:00",
        }), encoding="utf-8")
        kb_dir = self.repo / "kb"
        kb_dir.mkdir()
        (kb_dir / "wissen.md").write_text("NEUER-INHALT\n", encoding="utf-8")
        stale_sha = hashlib.sha256("ALTER-INHALT\n".encode("utf-8")).hexdigest()
        list_files_result = [{
            "id": "file-stale-1",
            "filename": "wissen.md",
            "meta": {"collection_name": "kb-1", "file_hash": stale_sha},
        }]
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
            # U1a: der Content-Fallback liest hier TATSÄCHLICH abweichenden
            # Rohinhalt (nicht nur den abweichenden Metadatenhash) -- echte
            # Drift bleibt Drift, auch mit dem neuen Fallback.
            get_file_content_result=b"ALTER-INHALT\n",
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("Aktiver Masterprompt entspricht dem Soll", out)
        self.assertIn("letzter Wissensabgleich bestätigt", out)
        self.assertIn("veraltet/abweichend: wissen.md", out)
        self.assertNotIn("Alle Prüfungen grün", out)
        self.assertIn("Automatischer Sync", out)
        self.assertEqual(client.add_file_calls, 0)
        self.assertEqual(client.delete_calls, 0)
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertTrue(L._diagnose_has_errors(), "Re-Check muss den belegten Inhaltsfehler ebenfalls sehen")

    def test_u1a_content_fallback_confirms_despite_metadata_hash_mismatch(self):
        """U1a (UPDATE_UX_REVIEW.md U1a, 02_RESTAUFTRAG.md §U1): ein
        abweichender Metadatenhash bei tatsächlich byte-identischem Inhalt
        in der aktiven KB ist KEIN Drift -- derselbe bestehende Content-
        Fallback (`_confirm_active_kb_file_by_content`, setup.py:4492-4531)
        wie der reguläre Sync bestätigt den Kandidaten über die echten
        Bytes. VORHER meldete der Checker hier pauschal 'drift'."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "ok", "kb_confirmed": 1, "kb_total": 1, "kb_failed": [],
            "sync_at": "2026-11-22T09:00:00",
        }), encoding="utf-8")
        kb_dir = self.repo / "kb"
        kb_dir.mkdir()
        (kb_dir / "wissen.md").write_text("AKTUELLER-INHALT\n", encoding="utf-8")
        list_files_result = [{
            "id": "bound-a",
            "filename": "wissen.md",
            "meta": {"collection_name": "kb-1", "file_hash": "metadata-hash-different"},
        }]
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
            get_file_content_result=b"AKTUELLER-INHALT\n",
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertIn(
            "Inhalt/Bindung aller 1 konfigurierten Wissensdatei(en) per SHA-256 bestätigt", out,
        )
        self.assertNotIn("veraltet/abweichend", out)
        self.assertIn("Alle Prüfungen grün", out)
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertFalse(L._diagnose_has_errors())

    def test_u1a_unreadable_content_fallback_stays_unbestimmt_not_drift(self):
        """Gegenfall: Metadatenhash weicht ab UND der Content-Fallback kann
        den Rohinhalt nicht lesen (`get_file_content` -> None) -- das bleibt
        'unbestimmt', kein erfundener Drift-Befund (Abgrenzung gegen
        `test_u1_b_mp_match_and_historical_sync_ok_but_active_kb_content_
        stale_blocks_gruen`, wo echte abweichende Bytes gelesen werden)."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        kb_dir = self.repo / "kb"
        kb_dir.mkdir()
        (kb_dir / "wissen.md").write_text("AKTUELLER-INHALT\n", encoding="utf-8")
        list_files_result = [{
            "id": "bound-a",
            "filename": "wissen.md",
            "meta": {"collection_name": "kb-1", "file_hash": "metadata-hash-different"},
        }]
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
            # get_file_content_result bleibt Default None -> unlesbar.
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertNotIn("veraltet/abweichend", out)
        self.assertIn("nicht abschließend möglich", out)
        self.assertNotIn("Alle Prüfungen grün", out)

    def test_u1b_missing_historical_sync_status_does_not_override_confirmed_current_content(self):
        """U1b (UPDATE_UX_REVIEW.md U1b, 02_RESTAUFTRAG.md §U1): kein
        historischer Sync-Status gespeichert (nie gesynct) -- Masterprompt
        UND aktueller KB-Inhalt sind aber tatsächlich bestätigt. VORHER
        blockte das historische 'unbestimmt' allein sowohl das Gesamtgrün
        als auch den Re-Check, bevor die aktuelle KB überhaupt geprüft
        wurde (02_RESTAUFTRAG.md:42)."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        # Bewusst KEINE .zeitriss-update-state.json -- "nie gesynct".
        list_files_result = self._write_confirmed_kb_file()
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
        )
        out, _ = self._run_diagnose(client, prompts=["n"])
        self.assertIn("noch kein Sync-Status gespeichert", out)
        self.assertIn(
            "Inhalt/Bindung aller 1 konfigurierten Wissensdatei(en) per SHA-256 bestätigt", out,
        )
        self.assertIn("Alle Prüfungen grün", out)
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertFalse(
            L._diagnose_has_errors(),
            "fehlender historischer Status darf bestätigten aktuellen Inhalt nicht überstimmen",
        )

    def test_u1b_genuinely_open_historical_sync_status_still_blocks_despite_confirmed_current_content(self):
        """Gegenfall (Scope-Grenze von U1b): ein NACHWEISLICH offener
        historischer Sync-Status (`kb_failed` nicht leer) bleibt
        blockierend, auch wenn die aktuelle Inhaltsprüfung inzwischen
        bestätigt. Nur die reine ABWESENHEIT historischer Daten wird
        entschärft -- eine wirklich offene Aufräum-/Syncoperation bleibt
        sichtbar und blockierend (keine pauschale Entschärfung)."""
        self.repo.joinpath("masterprompt.md").write_text("SOLL-INHALT\n", encoding="utf-8")
        (self.repo / ".zeitriss-update-state.json").write_text(json.dumps({
            "sync_status": "failed", "kb_failed": ["andere-datei.md"],
        }), encoding="utf-8")
        list_files_result = self._write_confirmed_kb_file()
        client = _FakeDiagClient(
            model=self._preset("SOLL-INHALT\n"),
            query_result={"code": 200, "hits": 1},
            list_files_result=list_files_result,
        )
        out, _ = self._run_diagnose(client, prompts=["n", "n"])
        self.assertIn("Wissensdateien laut letztem Sync offen", out)
        self.assertNotIn("Alle Prüfungen grün", out)
        self._patch(mock.patch.object(L.setup_module, "APIClient", lambda *a, **kw: client))
        self.assertTrue(L._diagnose_has_errors())


if __name__ == "__main__":
    unittest.main()
