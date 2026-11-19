#!/usr/bin/env python3
"""scripts/tests/test_launcher_action_update_r5_03_2026_11_18.py — R5-03
(ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r5, 02_NACHZUG_AUFTRAG.md
§C): belegt den echten Menü-Update-Weg end-to-end durch den REALEN
Aufrufer `scripts.launcher.action_update()` — nicht nur die Helfer in
`launcher_update.py` direkt. Erweitert die bestehende
`ActionUpdateTestCase`/`_ScriptedPrompt`-Harness aus
`test_launcher_action_update.py` (NICHT neu erfunden; identischer
Harness-Stil zu `test_launcher_action_update_r4_06_2026_11_18.py`).

Kontrollierte, AUSDRÜCKLICH GEKENNZEICHNETE Fixtures/Seams (diese
vier Kern-Seams; dazu eine temporäre, scope-begrenzte Umgebungs-Gate-
Freischaltung `_ensure_owui_env`→True NUR im `with`-Block von Stufe 3+4,
damit der separate Sync-Prozess überhaupt erreicht wird — kein Patch
eines Kern-Helfers):
  1. Netz-Download (`download_zip_archive` → `fake_download`, baut ein
     echtes lokales ZIP).
  2. Check-Quelle (`_default_http_get` → feste SHA, bzw. ein lokales
     Wegwerf-Origin-Git-Repo für den Git-Weg — kein echtes Netz, kein
     offizielles `main`).
  3. Sync-ZIEL: statt des echten `scripts/setup.py` (das echte
     OpenWebUI-Backend anfassen würde) liegt im kontrollierten Test-
     Repo ein eigener, klar gelabelter Stub unter demselben Dateinamen
     — `run_sync_subprocess()`/`_run_update_sync_step()` selbst laufen
     dabei VOLLSTÄNDIG UNGEMOCKT (echter `subprocess.run`, echter neuer
     OS-Prozess).
  4. Restart-Re-Exec (`restart_launcher` gepatcht) — ein echtes
     `os.execv` würde den Testprozess ersetzen, das ist der einzige
     legitim beobachtete Seam dafür.

ALLE anderen Helfer laufen ECHT: `perform_zip_update`/
`adopt_staged_update` (echte ZIP-Extraktion + echter Dateitausch),
`perform_git_update` (echtes `git fetch`/`merge --ff-only` gegen die
lokale Wegwerf-Origin-Testquelle), `mark_files_updated`,
`run_sync_subprocess` (echter Subprozessaufruf), `_block_if_restart_
required`. Keine Erfolgsmocks der Kern-Helfer."""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from unittest import mock

_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_action_update import ActionUpdateTestCase, _build_zip_bytes  # noqa: E402
from scripts.tests.test_launcher_update import _clone, _commit_all, _init_git_repo, _rev, _write_files  # noqa: E402


# R5-03 kontrollierter Sync-Stub (Testquelle) — KEIN echtes `setup.py`,
# KEIN echtes OpenWebUI-Backend. Läuft nur, um zu belegen, dass `run_sync_
# subprocess()` tatsächlich einen NEUEN OS-Prozess startet (andere PID als
# der Testprozess) — schreibt die eigenen Prozess-/Elternprozess-IDs und
# die empfangenen Argumente in eine Marker-Datei und beendet sich sofort.
_SYNC_STUB_SOURCE = '''#!/usr/bin/env python3
"""R5-03-KONTROLLIERTER-SYNC-STUB -- TESTQUELLE, KEIN echtes setup.py,
KEIN echtes OpenWebUI-Backend. Nur fuer scripts/tests/
test_launcher_action_update_r5_03_2026_11_18.py."""
import json
import os
import sys
from pathlib import Path

marker = Path(__file__).resolve().parent.parent / "sync_marker.json"
marker.write_text(json.dumps({
    "label": "R5-03-KONTROLLIERTER-SYNC-STUB -- kein echtes OpenWebUI-Backend",
    "argv": sys.argv[1:],
    "pid": os.getpid(),
    "ppid": os.getppid(),
}), encoding="utf-8")
sys.exit(0)
'''


class TestR503ZipSequenceThroughRealActionUpdateCaller(ActionUpdateTestCase):
    """R5-03 ZIP-Weg: treibt den echten Menü-Aufrufer `action_update()`
    durch die GANZE Sequenz — Prüfung (1) → Ablehnen (2) → bewusste
    Installation mit echtem Dateitausch (3) → separater Sync-Prozess (4)
    → abgelehnter Neustart mit wirksamer Sperre (5) → erneutes [4] mit
    genau einem `restart_launcher`-Aufruf (6) → ehrlicher Endstatus (7)."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        (self.repo / "scripts").mkdir()
        self.setup_json_content = '{"project": "ZEITRISS-R5-03-TESTQUELLE"}'
        (self.repo / "setup.json").write_text(self.setup_json_content, encoding="utf-8")
        (self.repo / "scripts" / "app.py").write_text("OLD\n", encoding="utf-8")
        # Eigener kontrollierter Sync-Stub (s. Moduldoc oben) -- liegt dort,
        # wo `run_sync_subprocess(REPO)` ihn UNGEMOCKT real aufruft.
        (self.repo / "scripts" / "setup.py").write_text(_SYNC_STUB_SOURCE, encoding="utf-8")

        self.old_sha = "a" * 40
        self.new_sha = "b" * 40
        lu.write_state(
            self.repo, method="zip", installed_rev=self.old_sha, sync_status="ok",
            managed_files={
                "setup.json": lu._sha256_file(self.repo / "setup.json"),
                "scripts/app.py": lu._sha256_file(self.repo / "scripts" / "app.py"),
            },
        )
        self._set_repo(self.repo)

        # Fixture 2: Check-Quelle -- feste Ziel-SHA statt echtem GitHub-API.
        self._patch(mock.patch.object(
            L.launcher_update_module, "_default_http_get",
            lambda url, timeout: json.dumps({"sha": self.new_sha}).encode("utf-8"),
        ))
        zip_bytes = _build_zip_bytes({
            f"ZEITRISS-md-{self.new_sha}/setup.json": self.setup_json_content,
            f"ZEITRISS-md-{self.new_sha}/scripts/app.py": "NEW\n",
        })

        # Fixture 1: Netz-Download -- schreibt ein echtes lokales ZIP statt
        # echt aus dem Netz zu laden; die Extraktion/Übernahme danach ist
        # vollständig echt (`perform_zip_update`/`adopt_staged_update`).
        def fake_download(url, dest, *, timeout=30.0, max_bytes=None, opener=None):
            dest.write_bytes(zip_bytes)

        self._patch(mock.patch.object(L.launcher_update_module, "download_zip_archive", fake_download))

    def test_full_sequence_1_to_7_through_real_action_update(self) -> None:
        app_path = self.repo / "scripts" / "app.py"
        setup_path = self.repo / "setup.json"

        # ── Stufe 1: reine Prüfung -- über denselben Helfer-Aufruf, den
        # `action_update()` intern benutzt (`launcher_update_module.
        # check_for_update`), damit die patchte Check-Quelle greift.
        # Belegt: KEINE Datei angefasst (Inhalt UND mtime), nur der
        # Check-Zeitstempel entsteht. ───────────────────────────────────
        self.assertNotIn("last_check_at", lu.read_state(self.repo))
        before_app_bytes = app_path.read_bytes()
        before_app_mtime = app_path.stat().st_mtime_ns
        before_setup_bytes = setup_path.read_bytes()
        self.assertEqual(before_app_bytes, b"OLD\n")

        check1 = L.launcher_update_module.check_for_update(self.repo)
        self.assertEqual(check1.status, "update_available")
        self.assertEqual(app_path.read_bytes(), before_app_bytes)
        self.assertEqual(app_path.stat().st_mtime_ns, before_app_mtime)
        self.assertEqual(setup_path.read_bytes(), before_setup_bytes)
        state_after_check1 = lu.read_state(self.repo)
        self.assertIn("last_check_at", state_after_check1)
        self.assertEqual(state_after_check1["installed_rev"], self.old_sha)
        self.assertEqual(state_after_check1["managed_files"], {
            "setup.json": lu._sha256_file(setup_path),
            "scripts/app.py": lu._sha256_file(app_path),
        })

        # ── Stufe 2: derselbe Check, jetzt durch den ECHTEN Aufrufer
        # `action_update()` -- Nutzer lehnt die Installation ab. Weiterhin
        # keine Datei-/Nutzdatenänderung. ────────────────────────────────
        prompt_a = self._set_prompt(["n"])
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            L.action_update()
        self.assertEqual(app_path.read_bytes(), before_app_bytes)
        self.assertEqual(app_path.stat().st_mtime_ns, before_app_mtime)
        self.assertEqual(setup_path.read_bytes(), before_setup_bytes)
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], self.old_sha)
        self.assertFalse(L._update_restart_required)
        self.assertEqual(len(prompt_a.calls), 1)
        self.assertIn("installieren", prompt_a.calls[0].lower())

        # ── Stufe 3+4: bewusste Installation ("j") -- echter ZIP-
        # Dateitausch UND echter separater Sync-Prozess (Fixture 3, s.
        # Moduldoc). `_ensure_owui_env` wird NUR für diesen einen Aufruf
        # auf True gesetzt (die Basisklasse patcht ihn sonst auf den
        # "ehrlich übersprungen"-Pfad) -- danach greift wieder der
        # Basis-Patch. Neustart wird danach bewusst abgelehnt ("n") --
        # Stufe 5. ─────────────────────────────────────────────────────
        prompt_b = self._set_prompt(["j", "n"])
        with mock.patch.object(L, "_ensure_owui_env", lambda: True):
            buf2 = io.StringIO()
            with mock.patch("sys.stdout", buf2):
                L.action_update()

        # Stufe 3: echter Dateitausch, konkret belegt vorher != nachher.
        self.assertEqual(app_path.read_bytes(), b"NEW\n")
        self.assertNotEqual(app_path.read_bytes(), before_app_bytes)
        state_after_install = lu.read_state(self.repo)
        self.assertEqual(state_after_install["installed_rev"], self.new_sha)
        self.assertEqual(state_after_install["method"], "zip")
        self.assertEqual(state_after_install["install_phase"], "complete")

        # Stufe 4: separater Prozess real (andere PID als der Testprozess),
        # kontrolliertes/gelabeltes Kommando, kein echtes OWUI-Backend.
        marker_path = self.repo / "sync_marker.json"
        self.assertTrue(marker_path.exists(), "Sync-Stub wurde nicht real ausgeführt")
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        self.assertNotEqual(marker["pid"], os.getpid())
        self.assertIn("--sync", marker["argv"])
        self.assertIn("--yes", marker["argv"])
        self.assertIn("kein echtes OpenWebUI-Backend", marker["label"])
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "ok")

        # Stufe 5: Neustart abgelehnt -> Sperre wirksam für alle
        # produktiven Menüpunkte.
        self.assertTrue(L._update_restart_required)
        self.assertEqual(len(prompt_b.calls), 2)
        self.assertIn("installieren", prompt_b.calls[0].lower())
        self.assertIn("neu starten", prompt_b.calls[1].lower())
        for label in ("[1]", "[2]", "[3]", "[M]", "[L]"):
            self.assertTrue(L._block_if_restart_required(label), f"{label} haette gesperrt sein muessen")

        # ── Stufe 6: erneutes [4] -- Pending-Restart-Fastpath, OHNE
        # erneuten `check_for_update()`-Aufruf, echter EINMALIGER Aufruf
        # von `restart_launcher()` (der eigentliche Re-Exec ist der
        # einzige legitim beobachtete weitere Seam -- `os.execv` kann im
        # Harness nicht real neu starten). ───────────────────────────────
        self._patch(mock.patch.object(
            L.launcher_update_module, "check_for_update",
            mock.Mock(side_effect=AssertionError(
                "check_for_update() haette bei pendendem Neustart NICHT erneut aufgerufen werden duerfen"
            )),
        ))
        self._patch(mock.patch.object(L.launcher_update_module, "restart_launcher"))
        restart_mock_obj = L.launcher_update_module.restart_launcher
        prompt_c = self._set_prompt(["j"])
        L.action_update()

        restart_mock_obj.assert_called_once_with(self.repo)
        self.assertEqual(len(prompt_c.calls), 1)

        # ── Stufe 7: ehrlicher Endstatus. Ein echter `os.execv`-Nachfolger
        # würde den Prozess komplett ersetzen -- `_update_restart_required`
        # bleibt deshalb bewusst weiterhin True (kein stilles Zurücksetzen
        # durch den Mock, exakt wie im echten Code: `_offer_pending_
        # restart_now()` setzt es im "ja"-Zweig nie auf False zurück). Der
        # persistierte Dateistand ist ehrlich: neue Revision installiert,
        # Sync ok, keine offene Teilinstallation. ─────────────────────────
        self.assertTrue(L._update_restart_required)
        final_state = lu.read_state(self.repo)
        self.assertEqual(final_state["installed_rev"], self.new_sha)
        self.assertEqual(final_state["sync_status"], "ok")
        self.assertIsNone(lu.incomplete_install(self.repo))


class TestR503GitSequenceThroughRealActionUpdateCaller(ActionUpdateTestCase):
    """Git-Menüweg (02_NACHZUG_AUFTRAG.md §C): derselbe echte Aufrufer
    `action_update()` für `local.source=='git'` -- echtes `perform_git_
    update` (Fast-forward) -> `mark_files_updated` -> `_finish_update_
    installation`. Begrenzte LOKALE Wegwerf-Origin-Testquelle (kein
    offizielles `main`, kein echtes Netz) -- Fixture 2 (Check-Quelle) ist
    hier das lokale Git-Remote selbst, kein HTTP-Mock nötig."""

    def setUp(self) -> None:
        super().setUp()
        self.remote = self.tmp / "git-origin-testquelle"
        self.clone = self.tmp / "install-git"
        _init_git_repo(self.remote, {
            "setup.json": '{"project": "ZEITRISS-R5-03-GIT-TESTQUELLE"}\n',
            "scripts/app.py": "OLD\n",
        })
        _clone(self.remote, self.clone)
        self._set_repo(self.clone)
        _write_files(self.remote, {"scripts/app.py": "NEW\n"})
        self.new_rev = _commit_all(self.remote, "r5-03 testquelle: neuer Stand")

    def test_git_sequence_through_real_action_update(self) -> None:
        before_rev = _rev(self.clone)
        self.assertNotEqual(before_rev, self.new_rev)
        app_path = self.clone / "scripts" / "app.py"
        self.assertEqual(app_path.read_text(), "OLD\n")

        prompt = self._set_prompt(["j", "n"])  # installieren: ja, Neustart: nein
        L.action_update()

        self.assertEqual(_rev(self.clone), self.new_rev)
        self.assertEqual(app_path.read_text(), "NEW\n")
        state = lu.read_state(self.clone)
        self.assertEqual(state["method"], "git")
        self.assertEqual(state["installed_rev"], self.new_rev)
        self.assertEqual(state["install_phase"], "complete")
        self.assertTrue(L._update_restart_required)
        self.assertTrue(L._block_if_restart_required("[1]"))
        self.assertEqual(len(prompt.calls), 2)
        self.assertIn("installieren", prompt.calls[0].lower())
        self.assertIn("neu starten", prompt.calls[1].lower())


class TestR503CurrentWithoutUpdateNeitherInstallsNorBlocks(ActionUpdateTestCase):
    """Gegenfall (02_NACHZUG_AUFTRAG.md §C): ein Check OHNE verfügbaren
    neuen Stand (`current`, kein `sync_pending`) darf NICHT grundlos
    installieren oder sperren."""

    def test_current_without_sync_pending_neither_installs_nor_blocks(self) -> None:
        remote = self.tmp / "remote"
        clone = self.tmp / "clone"
        _init_git_repo(remote, {"setup.json": '{"project": "ZEITRISS"}\n'})
        _clone(remote, clone)
        self._set_repo(clone)
        before_rev = _rev(clone)

        prompt = self._set_prompt([])  # kein Prompt erwartet
        L.action_update()

        self.assertEqual(_rev(clone), before_rev)
        self.assertEqual(prompt.calls, [])
        self.assertFalse(L._update_restart_required)
        self.assertFalse(L._block_if_restart_required("[1]"))


if __name__ == "__main__":
    unittest.main()
