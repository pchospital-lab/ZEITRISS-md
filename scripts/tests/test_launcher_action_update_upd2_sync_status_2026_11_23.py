#!/usr/bin/env python3
"""scripts/tests/test_launcher_action_update_upd2_sync_status_2026_11_23.py —
ZR-UPDATE-RESUME-REPARATUR-20261123-r1, UPD-2 (03_UPDATE_UND_KB.md
Implementierungsauftrag 2+3).

Ursache (verifiziert am echten Aufrufer, VOR diesem Fix): `_finish_update_
installation()` rief `_run_update_sync_step()` auf, WARF den bool-
Rückgabewert aber weg (`_run_update_sync_step()` als reine Anweisung ohne
Zuweisung) und bot über `_offer_pending_restart_now()` UNBEDINGT den Text
„Update installiert. Bitte den Launcher neu starten." an — unabhängig
davon, ob der nachfolgende Preset-/KB-Sync tatsächlich erfolgreich war.
Ein Teilfehler (z.B. eine Wissensdatei bleibt offen) wurde dem Nutzer damit
als vollständiger Erfolg verkauft — genau das vom Auftrag benannte „Der
Abschluss ignoriert den zurückgegebenen Sync-Boolean".

Treibt den ECHTEN Aufrufer `scripts.launcher.action_update()` (nicht nur
die isolierten Helfer) — dieselbe unmanaged-ZIP-Migrationsfixture wie
`test_launcher_action_update.TestActionUpdateUnmanagedZipMigration`, hier
um eine stdout-Prüfung der tatsächlich gezeigten Abschlussmeldung
ergänzt. Kein echtes Netz, kein echtes OpenWebUI-Backend."""
from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_action_update import (  # noqa: E402
    ActionUpdateTestCase, _build_zip_bytes,
)


class _UnmanagedZipMigrationBase(ActionUpdateTestCase):
    """Dieselbe Fixture wie `TestActionUpdateUnmanagedZipMigration` (reiner
    Testcode, bestehende Duplizierungs-Konvention dieser Suite statt
    Querimport einer Setup-Methode) — ein unverwalteter Erststand, der
    über [4] auf eine geprüfte Zielrevision migriert und danach
    `_finish_update_installation()` erreicht."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        (self.repo / "setup.json").write_text('{"project": "ZEITRISS", "version": "old"}', encoding="utf-8")
        self._set_repo(self.repo)
        target_sha = "deadbeef" * 5
        self.target_sha = target_sha
        self._patch(mock.patch.object(
            L.launcher_update_module, "_default_http_get",
            lambda url, timeout: json.dumps({"sha": target_sha}).encode("utf-8"),
        ))
        zip_bytes = _build_zip_bytes({
            f"ZEITRISS-md-{target_sha}/setup.json": '{"project": "ZEITRISS", "version": "new"}',
            f"ZEITRISS-md-{target_sha}/scripts/x.py": "NEW\n",
        })

        def fake_download(url, dest, *, timeout=30.0, max_bytes=None, opener=None):
            dest.write_bytes(zip_bytes)

        self._patch(mock.patch.object(L.launcher_update_module, "download_zip_archive", fake_download))


class TestFinishUpdateInstallationReflectsRealSyncOutcome(_UnmanagedZipMigrationBase):
    def test_failed_sync_does_not_claim_unconditional_success(self):
        """UPD-2-Regression: die Basisklasse patcht `_ensure_owui_env` auf
        False (kein Key) -- `_run_update_sync_step()` scheitert also
        tatsächlich ECHT (kein gemockter Subprozess nötig). VOR dem Fix
        zeigte `_offer_pending_restart_now()` trotzdem unbedingt „Update
        installiert." NACH dem Fix muss die Meldung den offenen
        Wissensabgleich klar benennen und darf NICHT den unbedingten
        Erfolgstext zeigen."""
        prompt = self._set_prompt([
            "j",   # "Trotzdem auf den geprüften Stand übernehmen?"
            "j",   # "Diese Dateien bewusst überschreiben?" (setup.json weicht ab)
            "n",   # "Jetzt neu starten?" -- bewusst ablehnen (kein echter execv in der Testfixture)
        ])
        buf = io.StringIO()
        with redirect_stdout(buf):
            L.action_update()
        out = buf.getvalue()

        self.assertNotIn(
            "Update installiert. Bitte den Launcher neu starten.", out,
            "ein fehlgeschlagener Sync darf NICHT den unbedingten "
            "Erfolgstext zeigen (03_UPDATE_UND_KB.md Implementierungsauftrag 2)",
        )
        self.assertIn("Wissensabgleich ist noch offen", out)
        self.assertEqual(len(prompt.calls), 3)
        # Datei-Übernahme selbst bleibt vom Sync-Ausgang unabhängig erfolgreich.
        self.assertEqual((self.repo / "setup.json").read_text(), '{"project": "ZEITRISS", "version": "new"}')

    def test_successful_sync_still_shows_the_real_success_message(self):
        """Gegenprobe: ein WIRKLICH erfolgreicher Sync zeigt weiterhin den
        normalen Erfolgstext (kein Overcorrection — der Fix darf einen
        echten Erfolg nicht zu einem Fehlerbild umdeuten) und die
        UPD-2-Aufschlüsselung der Wissensdateien."""
        self._patch(mock.patch.object(L, "_ensure_owui_env", lambda: True))

        def fake_sync_subprocess(repo, **kwargs):
            lu.write_state(
                repo, sync_status="ok", kb_total=3, kb_confirmed=3, kb_failed=[], preset_ok=True,
            )
            return True, "Sync abgeschlossen."

        self._patch(mock.patch.object(
            L.launcher_update_module, "run_sync_subprocess", fake_sync_subprocess,
        ))
        prompt = self._set_prompt(["j", "j", "n"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            L.action_update()
        out = buf.getvalue()

        self.assertIn("Update installiert. Bitte den Launcher neu starten.", out)
        self.assertIn("Wissensdateien: 3 von 3 bestätigt.", out)
        self.assertEqual(len(prompt.calls), 3)


class TestDescribeKbSyncStatus(unittest.TestCase):
    """UPD-2: reine Funktionstests für die Status-Trennung "Programm
    aktuell" / "Wissensstand zuletzt bestätigt" / "aktuell nicht
    prüfbar" -- kein implizites Gesamtgrün aus fehlendem Feld."""

    def test_missing_breakdown_is_honestly_unverifiable(self):
        self.assertEqual(
            L._describe_kb_sync_status({}),
            "Wissensstand: aktuell nicht prüfbar (keine Sync-Aufschlüsselung vorhanden).",
        )

    def test_all_confirmed_reports_counts_with_geltungsstand(self):
        # U-R2: eine Vollbestätigung OHNE erkennbaren Prüfzeitpunkt wird
        # ehrlich als "Prüfzeitpunkt unbekannt" markiert, damit sie nicht
        # wie eine frische, aktuelle Vollbestätigung wirkt.
        msg = L._describe_kb_sync_status({"kb_total": 19, "kb_confirmed": 19, "kb_failed": []})
        self.assertEqual(msg, "Wissensdateien: 19 von 19 bestätigt. (Prüfzeitpunkt unbekannt)")
        # Mit bekanntem Prüfzeitpunkt trägt dieselbe Vollbestätigung den Stand.
        stamped = L._describe_kb_sync_status(
            {"kb_total": 19, "kb_confirmed": 19, "kb_failed": [], "sync_at": "2026-11-23T10:00:00+00:00"}
        )
        self.assertEqual(
            stamped, "Wissensdateien: 19 von 19 bestätigt. (Stand: 2026-11-23T10:00:00+00:00)"
        )

    def test_partial_failure_names_the_open_files_and_preserves_old_version(self):
        msg = L._describe_kb_sync_status(
            {"kb_total": 19, "kb_confirmed": 18, "kb_failed": ["sl-referenz.md"]}
        )
        self.assertIn("18 von 19 bestätigt", msg)
        self.assertIn("sl-referenz.md", msg)
        self.assertIn("bisherige Version bleibt erhalten", msg)


if __name__ == "__main__":
    unittest.main()
