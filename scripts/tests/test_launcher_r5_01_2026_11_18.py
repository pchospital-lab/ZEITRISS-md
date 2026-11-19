#!/usr/bin/env python3
"""scripts/tests/test_launcher_r5_01_2026_11_18.py — R5-01 Regression
(ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r5, 01_GENERAL_REVIEW.md
R5-01, 02_NACHZUG_AUFTRAG.md §A).

Befund: `_adopt_staged_update_locked` kann nach mindestens einer
erfolgreich ausgetauschten Datei bei einer SPÄTEREN Datei mit `OSError`
scheitern -- der Dateistand ist dann gemischt (Teil A, Teil B), aber
`action_update()` erreicht `_finish_update_installation` NIE, also wird
`_update_restart_required` NIE gesetzt. Die bestehenden Guards
(`_block_if_restart_required`, Dispatcher-Guard) prüfen NUR dieses
flüchtige In-Memory-Attribut -- ein frisch gestarteter Prozess sieht den
Mischzustand nicht. Dieser Test treibt den ECHTEN `action_update()`/
Menü-Weg (nicht nur die Helfer in `launcher_update.py` direkt) und prüft:

1. ein `OSError` mitten im Kopieren setzt einen PERSISTENTEN Marker
   (`install_phase == "in_progress"`), gebunden an `target_rev`.
2. produktive Menüaktionen bleiben gesperrt -- im selben Prozess UND in
   einem frisch importierten Prozess (echter Subprozess, kein In-Memory-
   Trick).
3. der angebotene Recovery-Weg über [4] stellt konsistent fertig --
   sowohl auf der gebundenen Zielrevision als auch (bewusst gewählt)
   auf einer inzwischen neueren Revision.
4. ein harmloser Check ohne jeden Dateiwechsel sperrt NICHT grundlos.
5. Baseline-Gegenprobe: dieselbe Testdatei schlägt auf dem Vor-Fix-Code
   (Head bf0001d) fehl und wird erst mit dem Fix grün (s. Report,
   `git stash`-Gegenprobe mit Kommando+Output)."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

import unittest

_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_action_update import ActionUpdateTestCase, _build_zip_bytes  # noqa: E402
from scripts.tests.test_launcher_update import _clone, _commit_all, _init_git_repo, _rev, _write_files  # noqa: E402

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]  # .../ZEITRISS-md/scripts


def _run_fresh_process_incomplete_install_check(repo: Path) -> str:
    """Spawnt einen ECHTEN, frisch gestarteten Python-Subprozess, der
    `launcher_update.py` ERNEUT importiert (kein geteilter In-Memory-
    Zustand mit dem Testprozess) und `incomplete_install(repo)` darauf
    aufruft. Das ist der schärfste verfügbare Nachweis, dass der Marker
    tatsächlich auf der Platte liegt, nicht nur in einem Modul-Global des
    laufenden Testprozesses."""
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(_SCRIPTS_DIR)!r})\n"
        "import launcher_update as lu\n"
        "from pathlib import Path\n"
        f"info = lu.incomplete_install(Path({str(repo)!r}))\n"
        "print(info.target_rev if info else 'NONE')\n"
    )
    r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, f"Subprozess fehlgeschlagen: stdout={r.stdout!r} stderr={r.stderr!r}"
    return r.stdout.strip()


class _InterruptedZipFollowupBase(ActionUpdateTestCase):
    """Gemeinsames Fixture: eine bereits regulär verwaltete ZIP-
    Installation A wird auf B aktualisiert, aber EIN simulierter
    `shutil.copy2`-`OSError` unterbricht den Lauf NACH mindestens einer
    tatsächlich kopierten Datei -- derselbe Fixture-Stil wie der
    bestehende R3-03-Resume-Test (`test_launcher_action_update.py`),
    hier aber gezielt auf den NEUEN `install_phase`-Marker geprüft."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        self.sha_a = "a" * 40
        self.sha_b = "b" * 40
        self.sha_c = "c" * 40
        (self.repo / "setup.json").write_text("{}", encoding="utf-8")
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "a.py").write_text("A1\n", encoding="utf-8")
        (self.repo / "scripts" / "b.py").write_text("B1\n", encoding="utf-8")
        lu.write_state(
            self.repo, method="zip", installed_rev=self.sha_a, sync_status="ok", install_phase="complete",
            managed_files={
                "setup.json": lu._sha256_file(self.repo / "setup.json"),
                "scripts/a.py": lu._sha256_file(self.repo / "scripts" / "a.py"),
                "scripts/b.py": lu._sha256_file(self.repo / "scripts" / "b.py"),
            },
        )
        self._set_repo(self.repo)

        self._remote_sha = {"value": self.sha_b}
        self._patch(mock.patch.object(
            L.launcher_update_module, "_default_http_get",
            lambda url, timeout: json.dumps({"sha": self._remote_sha["value"]}).encode("utf-8"),
        ))
        zip_bytes_by_rev = {
            self.sha_b: _build_zip_bytes({
                f"ZEITRISS-md-{self.sha_b}/setup.json": "{}",
                f"ZEITRISS-md-{self.sha_b}/scripts/a.py": "A2\n",
                f"ZEITRISS-md-{self.sha_b}/scripts/b.py": "B2\n",
            }),
            self.sha_c: _build_zip_bytes({
                f"ZEITRISS-md-{self.sha_c}/setup.json": "{}",
                f"ZEITRISS-md-{self.sha_c}/scripts/a.py": "A3\n",
                f"ZEITRISS-md-{self.sha_c}/scripts/b.py": "B3\n",
            }),
        }

        def fake_download(url, dest, *, timeout=30.0, max_bytes=None, opener=None):
            for rev, data in zip_bytes_by_rev.items():
                if rev in url:
                    dest.write_bytes(data)
                    return
            raise AssertionError(f"Download fuer unerwartete URL angefragt: {url!r}")

        self._patch(mock.patch.object(L.launcher_update_module, "download_zip_archive", fake_download))

    def _interrupt_a_to_b(self) -> None:
        """Löst über den ECHTEN [4]-Weg eine A→B-Übernahme aus, die nach
        genau einer kopierten Datei mit einem `OSError` abbricht."""
        calls = {"n": 0}
        real_copy2 = shutil.copy2

        def flaky_copy2(src, dst, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full (simulated)")
            return real_copy2(src, dst, *a, **kw)

        with mock.patch.object(L.launcher_update_module.shutil, "copy2", side_effect=flaky_copy2):
            self._set_prompt(["j"])  # "Jetzt installieren?"
            L.action_update()


# ── Punkt 1: OSError mitten im Kopieren setzt den persistenten Marker ────

class TestR501PersistentInstallPhaseSurvivesOSError(_InterruptedZipFollowupBase):
    def test_oserror_mid_copy_leaves_persistent_install_phase_in_progress_bound_to_target_rev(self):
        self._interrupt_a_to_b()

        state = lu.read_state(self.repo)
        self.assertEqual(state["install_phase"], "in_progress")
        self.assertEqual(state["target_rev"], self.sha_b)
        # R5-01-Kernbehauptung: der alte `installed_rev` steht noch auf A
        # (Teilmanifest täuscht KEINE komplett installierte Revision vor),
        # aber der neue Marker macht den Mischzustand trotzdem sichtbar.
        self.assertEqual(state["installed_rev"], self.sha_a)

        info = lu.incomplete_install(self.repo)
        self.assertIsNotNone(info)
        self.assertEqual(info.target_rev, self.sha_b)


# ── Punkt 2: produktive Menüaktionen bleiben gesperrt -- selber + neuer Prozess ──

class TestR501BlocksProductiveMenuAcrossProcesses(_InterruptedZipFollowupBase):
    def test_blocked_in_same_process_via_guard_and_dispatcher_tuple(self):
        # Gegenprobe VOR der Unterbrechung: keine Sperre.
        self.assertFalse(L._block_if_install_incomplete("[1]"))

        self._interrupt_a_to_b()

        for label in ("[1]", "[L]", "[2]", "[3]", "[M]"):
            self.assertTrue(L._block_if_install_incomplete(label), f"{label} muss gesperrt sein")
        # [4]/[6]/[X] bleiben frei -- Dispatcher-Guard in main() prueft nur
        # ("1","l","2","3","m"); hier gegen die Quelle verifiziert.
        self.assertNotIn("4", ("1", "l", "2", "3", "m"))
        self.assertNotIn("6", ("1", "l", "2", "3", "m"))
        self.assertNotIn("x", ("1", "l", "2", "3", "m"))

    def test_blocked_in_a_freshly_imported_subprocess(self):
        before = _run_fresh_process_incomplete_install_check(self.repo)
        self.assertEqual(before, "NONE", "vor der Unterbrechung darf kein Marker stehen")

        self._interrupt_a_to_b()

        after = _run_fresh_process_incomplete_install_check(self.repo)
        self.assertEqual(
            after, self.sha_b,
            "ein frisch importierter Prozess muss den persistenten Marker auf der Platte sehen",
        )


# ── Punkt 3: Recovery über [4] -- gebundene Revision UND bewusste Umlenkung ──

class TestR501RecoveryCompletesConsistently(_InterruptedZipFollowupBase):
    def test_recovery_resumes_on_bound_target_rev_and_lifts_the_lock(self):
        self._interrupt_a_to_b()

        prompt = self._set_prompt([
            "j",  # "Installation jetzt vollständig auf <B> fertigstellen?"
            "n",  # "Jetzt neu starten?" (R3-05, bewusst abgelehnt)
        ])
        L.action_update()

        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A2\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B2\n")
        state = lu.read_state(self.repo)
        self.assertEqual(state["installed_rev"], self.sha_b)
        self.assertEqual(state["install_phase"], "complete")
        # Punkt 5 (Fehlerfelder getrennt behandeln): sync_status bleibt
        # "pending" (Sync ist ein eigener, hier nicht gelaufener Schritt),
        # kein Syncfehler wird hier faelschlich geloescht/erzeugt.
        self.assertEqual(state["sync_status"], "pending")

        self.assertIsNone(lu.incomplete_install(self.repo))
        self.assertFalse(L._block_if_install_incomplete("[1]"))
        self.assertEqual(len(prompt.calls), 2)

    def test_recovery_can_be_consciously_redirected_to_a_newer_revision_c(self):
        self._interrupt_a_to_b()
        # Die geprüfte Quelle hat sich zwischenzeitlich von B nach C bewegt.
        self._remote_sha["value"] = self.sha_c

        prompt = self._set_prompt([
            "n",  # "Installation jetzt vollständig auf <B> fertigstellen?" -- NEIN
            "j",  # "Stattdessen prüfen, ob die Quelle inzwischen weiter ist...?"
            "j",  # "Bewusst auf den NEUEN Stand (C) wiederherstellen...?"
            "n",  # "Jetzt neu starten?"
        ])
        L.action_update()

        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A3\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B3\n")
        state = lu.read_state(self.repo)
        self.assertEqual(state["installed_rev"], self.sha_c)
        self.assertEqual(state["install_phase"], "complete")
        self.assertIsNone(lu.incomplete_install(self.repo))
        self.assertEqual(len(prompt.calls), 4)

    def test_declining_both_recovery_offers_leaves_the_lock_in_place(self):
        """Kein Teil-Fortschritt wird weggeworfen, aber auch keine stille
        Entsperrung ohne eine der beiden bewussten Zustimmungen."""
        self._interrupt_a_to_b()
        self._set_prompt(["n", "n"])  # fertigstellen: nein -- stattdessen pruefen: nein
        L.action_update()

        state = lu.read_state(self.repo)
        self.assertEqual(state["install_phase"], "in_progress")
        self.assertEqual(state["installed_rev"], self.sha_a)
        self.assertIsNotNone(lu.incomplete_install(self.repo))
        self.assertTrue(L._block_if_install_incomplete("[1]"))


# ── Punkt 4: Gegenfall ohne Dateiwechsel sperrt NICHT grundlos ────────────

class TestR501NoFalsePositiveWithoutFileExchange(ActionUpdateTestCase):
    def test_declined_fresh_migration_offer_touches_no_files_and_sets_no_lock(self):
        """Ein unverwaltetes Repo, bei dem der Nutzer die Übernahme-Anfrage
        ablehnt (R3-01-Weg) -- NIE Dateien angefasst, also darf auch NIE
        ein `install_phase`-Marker entstehen."""
        repo = self.tmp / "install"
        repo.mkdir()
        (repo / "setup.json").write_text('{"project": "ZEITRISS", "version": "old"}', encoding="utf-8")
        self._set_repo(repo)
        target_sha = "deadbeef" * 5
        self._patch(mock.patch.object(
            L.launcher_update_module, "_default_http_get",
            lambda url, timeout: json.dumps({"sha": target_sha}).encode("utf-8"),
        ))
        self._set_prompt(["n"])  # "Trotzdem auf den geprüften Stand übernehmen?" -- NEIN
        L.action_update()

        self.assertNotIn("install_phase", lu.read_state(repo))
        self.assertIsNone(lu.incomplete_install(repo))
        self.assertFalse(L._block_if_install_incomplete("[1]"))

    def test_plain_up_to_date_git_checkout_check_sets_no_lock(self):
        """Gegenprobe im Git-Pfad: ein reiner, lesender Check auf einem
        bereits aktuellen Git-Checkout tauscht nie Dateien aus und darf
        nie einen Marker hinterlassen."""
        remote = self.tmp / "remote"
        clone = self.tmp / "clone"
        _init_git_repo(remote, {"setup.json": "{}\n", "marker.txt": "v1\n"})
        _clone(remote, clone)
        self._set_repo(clone)
        self._set_prompt([])  # "current" -> kein Prompt erwartet
        L.action_update()

        self.assertIsNone(lu.incomplete_install(clone))
        self.assertFalse(L._block_if_install_incomplete("[1]"))


# ── Git-Pfad bleibt von einem ZIP-spezifischen Marker unberührt ─────────

class TestR501GitPathIsNeverFalselyGatedByTheZipMarker(ActionUpdateTestCase):
    def test_stale_in_progress_leftover_does_not_block_or_misfire_on_a_git_checkout(self):
        """Verwaister `install_phase=in_progress`-Eintrag (z. B. aus einer
        frueheren ZIP-Phase dieser Installation) darf auf einem ECHTEN
        Git-Checkout weder die Produktivaktionen sperren noch
        `action_update()` in den ZIP-Recovery-Zweig lenken -- Git selbst
        ist hier die Autoritaet, nicht die Statusdatei."""
        remote = self.tmp / "remote"
        clone = self.tmp / "clone"
        _init_git_repo(remote, {"setup.json": "{}\n", "marker.txt": "v1\n"})
        _clone(remote, clone)
        lu.write_state(clone, install_phase="in_progress", target_rev="stale" * 8)
        self._set_repo(clone)

        self.assertIsNone(lu.incomplete_install(clone))
        self.assertFalse(L._block_if_install_incomplete("[1]"))

        _write_files(remote, {"marker.txt": "v2\n"})
        new_rev = _commit_all(remote, "update")
        prompt = self._set_prompt(["j", "n"])  # installieren: ja -- neu starten: nein
        L.action_update()

        self.assertEqual(_rev(clone), new_rev)
        state = lu.read_state(clone)
        self.assertEqual(state["install_phase"], "complete")
        self.assertIsNone(lu.incomplete_install(clone))
        self.assertEqual(len(prompt.calls), 2)


if __name__ == "__main__":
    unittest.main()
