#!/usr/bin/env python3
"""scripts/tests/test_launcher_update.py — ZR-ALTAIR-UPDATER-SPIELTEST-
20261118-r2 (U1-U6 aus 02_UPDATE_VERHALTEN_UND_ABNAHME.md).

Technische Tests GEGEN KONTROLLIERTE FIXTURES (lokale Git-Remotes auf der
Platte, injizierte HTTP-/Subprocess-Doubles, selbst gebaute ZIP-Archive).
Kein echtes Netz, kein echtes OpenWebUI-/Modell-Backend — das ist hier
ausdrücklich NICHT behauptet. Jede Testklasse ist einer Zeile der
Abnahme-Matrix aus 02_UPDATE_VERHALTEN_UND_ABNAHME.md zugeordnet (s.
Docstrings)."""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts import launcher_update as lu


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def _init_git_repo(path: Path, files: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    _write_files(path, files)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=path, check=True)


def _write_files(path: Path, files: dict) -> None:
    for relpath, content in files.items():
        p = path / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _commit_all(path: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", message], check=True)
    return _rev(path)


def _rev(path: Path) -> str:
    r = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _clone(remote: Path, dest: Path) -> None:
    subprocess.run(["git", "clone", "-q", str(remote), str(dest)], check=True)
    # Lokale Identitaet unabhaengig von einem evtl. fehlenden/durch andere
    # Tests im selben Prozess verschobenen globalen ~/.gitconfig setzen --
    # sonst scheitert ein `git commit` in diesem Fixture-Clone mit "Please
    # tell me who you are", je nachdem, in welcher Reihenfolge Tests laufen.
    subprocess.run(["git", "-C", str(dest), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(dest), "config", "user.name", "Test"], check=True)


class GitFixtureTestCase(unittest.TestCase):
    """Basisklasse: legt ein lokales Remote + einen Clone an (kein Netz)."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.remote = self.tmp / "remote"
        self.clone = self.tmp / "clone"
        _init_git_repo(self.remote, {"setup.json": '{"project": "ZEITRISS", "version": "4.2.6"}\n',
                                      "marker.txt": "v1\n"})
        _clone(self.remote, self.clone)


# ── U1 Check (Matrix: "Check, aktuell" / "Check, Update verfügbar" /
#    "Netz-/Quellenfehler") ──────────────────────────────────────────────

class TestCheckForUpdateGit(GitFixtureTestCase):
    def test_current_when_clone_matches_remote_head(self):
        result = lu.check_for_update(self.clone)
        self.assertEqual(result.status, "current")
        self.assertEqual(result.local.source, "git")
        self.assertEqual(result.remote_rev, _rev(self.remote))
        # reiner Check: keine Mutation, kein neuer Commit, kein Sync-Spur.
        self.assertEqual(_rev(self.clone), _rev(self.remote))
        self.assertFalse((self.clone / lu.STATE_FILENAME).exists() and
                          lu.read_state(self.clone).get("sync_status"))

    def test_update_available_when_remote_has_moved(self):
        _write_files(self.remote, {"marker.txt": "v2\n"})
        new_rev = _commit_all(self.remote, "bump")
        result = lu.check_for_update(self.clone)
        self.assertEqual(result.status, "update_available")
        self.assertEqual(result.remote_rev, new_rev)
        # Check allein darf den Clone nicht veraendert haben.
        self.assertEqual((self.clone / "marker.txt").read_text(), "v1\n")
        self.assertNotEqual(_rev(self.clone), new_rev)

    def test_unknown_when_remote_unreachable(self):
        broken_remote = self.tmp / "does-not-exist"
        subprocess.run(["git", "-C", str(self.clone), "remote", "set-url", "origin", str(broken_remote)], check=True)
        result = lu.check_for_update(self.clone)
        self.assertEqual(result.status, "unknown")
        self.assertIsNone(result.remote_rev)
        self.assertTrue(result.reason)

    def test_dirty_tracked_file_reported_without_blocking_check(self):
        (self.clone / "marker.txt").write_text("edited locally\n", encoding="utf-8")
        result = lu.check_for_update(self.clone)
        self.assertTrue(result.local.dirty)
        self.assertEqual(result.status, "current")  # Datei-Inhalt ist egal für den reinen Rev-Vergleich

    def test_local_commits_ahead_of_remote_are_not_offered_as_update(self):
        """R3-04/a: ein Dev-Stand, der der geprüften Quelle bereits voraus
        ist, darf NICHT als 'update_available' auf die ÄLTERE Revision
        gemeldet werden. Das Zielobjekt (alte Remote-Revision) liegt hier
        schon lokal vor (aus dem initialen `clone`) -- ohne zusätzliches
        `fetch` prüfbar, siehe `_git_object_present_locally`."""
        remote_rev = _rev(self.remote)  # schon im Clone-Objektspeicher vorhanden
        _write_files(self.clone, {"marker.txt": "local-only work\n"})
        _commit_all(self.clone, "local ahead commit")  # remote bewegt sich NICHT

        result = lu.check_for_update(self.clone)
        self.assertEqual(result.status, "ahead")
        self.assertEqual(result.remote_rev, remote_rev)

    def test_diverged_local_and_remote_without_fetched_objects_stays_update_available(self):
        """Dokumentierte Grenze: `check_for_update` darf laut Vertrag nie
        fetchen. Ist das entfernte Zielobjekt lokal NICHT vorhanden (z. B.
        weil die Quelle seit dem Clone neue Commits bekam), kann die
        Vorfahrenbeziehung nicht geprüft werden -- die Antwort bleibt ehrlich
        'update_available' statt eine falsche Sicherheit zu behaupten."""
        _write_files(self.clone, {"marker.txt": "local-only work\n"})
        _commit_all(self.clone, "local only commit")
        _write_files(self.remote, {"marker.txt": "remote moved\n"})
        _commit_all(self.remote, "remote only commit")  # Objekt existiert NICHT im Clone

        result = lu.check_for_update(self.clone)
        self.assertEqual(result.status, "update_available")


class TestCheckForUpdateZipAndUnmanaged(unittest.TestCase):
    """Kein Git — ZIP-/unverwaltete Installation. Die offizielle Quelle wird
    hier per injiziertem HTTP-Double simuliert (kontrollierte Fixture, kein
    echtes GitHub)."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-zip-check-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()

    def _http_get(self, sha: str):
        def getter(url, timeout):
            return json.dumps({"sha": sha}).encode("utf-8")
        return getter

    def test_unmanaged_zip_without_state_never_reports_current(self):
        """U1: eine unbestimmte ZIP-Herkunft darf NIE 'current' ergeben,
        selbst wenn die Quelle erreichbar ist."""
        result = lu.check_for_update(self.repo, http_get=self._http_get("deadbeef" * 5))
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.local.source, "unmanaged")
        self.assertIsNone(result.local.rev)

    def test_managed_zip_current_when_matching(self):
        lu.write_state(self.repo, method="zip", installed_rev="abc123", sync_status="ok")
        result = lu.check_for_update(self.repo, http_get=self._http_get("abc123"))
        self.assertEqual(result.status, "current")

    def test_managed_zip_update_available_when_source_moved(self):
        lu.write_state(self.repo, method="zip", installed_rev="abc123", sync_status="ok")
        result = lu.check_for_update(self.repo, http_get=self._http_get("deadbeef" * 5))
        self.assertEqual(result.status, "update_available")
        self.assertEqual(result.remote_rev, "deadbeef" * 5)

    def test_unreadable_source_body_yields_unknown_not_current(self):
        def bad_getter(url, timeout):
            return b"not json"
        lu.write_state(self.repo, method="zip", installed_rev="abc123")
        result = lu.check_for_update(self.repo, http_get=bad_getter)
        self.assertEqual(result.status, "unknown")

    def test_network_error_yields_unknown_with_reason(self):
        def raising_getter(url, timeout):
            raise OSError("Name or service not known")
        result = lu.check_for_update(self.repo, http_get=raising_getter)
        self.assertEqual(result.status, "unknown")
        self.assertIn("OSError", result.reason)

    def test_managed_zip_with_locally_modified_file_reports_dirty(self):
        """R3-04/d: `installed_rev` kam bisher ungeprüft aus der Statusdatei
        -- eine seither per Hand geänderte verwaltete Datei blieb unsichtbar.
        Jetzt muss der tatsächliche Dateibestand gegen das SHA-256-Manifest
        geprüft werden, genau wie der Git-Zweig schon `dirty` liefert."""
        (self.repo / "scripts.py").write_text("original\n", encoding="utf-8")
        managed_hash = lu._sha256_file(self.repo / "scripts.py")
        lu.write_state(self.repo, method="zip", installed_rev="abc123", sync_status="ok",
                        managed_files={"scripts.py": managed_hash})
        (self.repo / "scripts.py").write_text("hand-edited after install\n", encoding="utf-8")

        result = lu.check_for_update(self.repo, http_get=self._http_get("abc123"))
        self.assertEqual(result.status, "current")  # Revision stimmt weiterhin
        self.assertTrue(result.local.dirty)  # aber lokal veraendert -- sichtbar, nicht verdeckt

    def test_managed_zip_unmodified_files_report_clean(self):
        (self.repo / "scripts.py").write_text("original\n", encoding="utf-8")
        managed_hash = lu._sha256_file(self.repo / "scripts.py")
        lu.write_state(self.repo, method="zip", installed_rev="abc123", sync_status="ok",
                        managed_files={"scripts.py": managed_hash})
        result = lu.check_for_update(self.repo, http_get=self._http_get("abc123"))
        self.assertEqual(result.status, "current")
        self.assertFalse(result.local.dirty)

    def test_sync_pending_surfaced_even_when_files_current(self):
        """U5: 'Dateien aktuell, Sync offen' darf ein erneuter Check nicht
        als blankes 'current' verdecken."""
        lu.write_state(self.repo, method="zip", installed_rev="abc123", sync_status="pending")
        result = lu.check_for_update(self.repo, http_get=self._http_get("abc123"))
        self.assertEqual(result.status, "current")
        self.assertTrue(result.sync_pending)


# ── U2/U3 Git-Installation (Matrix: "Git-Update" / "Lokale Abweichung") ──

class TestPerformGitUpdate(GitFixtureTestCase):
    def test_fast_forward_to_pinned_target_even_if_remote_moves_again(self):
        _write_files(self.remote, {"marker.txt": "v2\n"})
        target = _commit_all(self.remote, "to-target")
        # Quelle wandert NACH dem Check noch weiter — der Install darf trotzdem
        # nur exakt `target` ziehen (U2: "wandert Main währenddessen weiter,
        # keinen Mix zweier Stände erzeugen").
        _write_files(self.remote, {"marker.txt": "v3\n"})
        _commit_all(self.remote, "moved-further")

        result = lu.perform_git_update(self.clone, target_rev=target)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.new_rev, target)
        self.assertEqual(_rev(self.clone), target)
        self.assertEqual((self.clone / "marker.txt").read_text(), "v2\n")

    def test_dirty_tracked_file_stops_without_changing_anything(self):
        before_rev = _rev(self.clone)
        (self.clone / "marker.txt").write_text("my own edit\n", encoding="utf-8")
        _write_files(self.remote, {"marker.txt": "v2\n"})
        target = _commit_all(self.remote, "bump")

        result = lu.perform_git_update(self.clone, target_rev=target)
        self.assertFalse(result.ok)
        self.assertIn("Lokale Änderungen", result.message)
        self.assertEqual(_rev(self.clone), before_rev)
        self.assertEqual((self.clone / "marker.txt").read_text(), "my own edit\n")

    def test_diverged_branch_stops_without_force(self):
        _write_files(self.clone, {"marker.txt": "my local commit\n"})
        local_rev = _commit_all(self.clone, "local work")
        _write_files(self.remote, {"marker.txt": "v2\n"})
        target = _commit_all(self.remote, "bump")

        result = lu.perform_git_update(self.clone, target_rev=target)
        self.assertFalse(result.ok)
        self.assertIn("Fast-forward nicht möglich", result.message)
        self.assertEqual(_rev(self.clone), local_rev)  # unveraendert, kein Reset/Force

    def test_already_on_target_is_a_noop_success(self):
        target = _rev(self.remote)
        result = lu.perform_git_update(self.clone, target_rev=target)
        self.assertTrue(result.ok)
        self.assertEqual(result.new_rev, target)

    def test_target_already_ancestor_of_head_does_not_claim_false_success(self):
        """R3-04/b: `git merge --ff-only <alte_vorfahren-revision>` kann
        exit 0 melden ('Already up to date'), OHNE HEAD zu bewegen, wenn der
        lokale Stand der angeforderten Zielrevision schon voraus ist. Die
        Funktion darf dann NICHT behaupten, `target_rev` sei jetzt installiert
        -- das war vorher der Fall (gab `rev` blind als `new_rev` zurück)."""
        old_target = _rev(self.remote)  # das ist das, was wir (veraltet) installieren wollen
        _write_files(self.clone, {"marker.txt": "ahead work\n"})
        ahead_rev = _commit_all(self.clone, "local ahead of old_target")

        result = lu.perform_git_update(self.clone, target_rev=old_target)
        self.assertFalse(result.ok)
        self.assertIn("entspricht nicht der Zielrevision", result.message)
        # Nichts zurückgesetzt -- HEAD bleibt beim voraus-Stand.
        self.assertEqual(_rev(self.clone), ahead_rev)


# ── U3/U4 ZIP-Sicherheitsprüfung (Matrix: "Download-/Archivfehler") ─────

def _build_zip(entries: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


class TestValidateAndStageZip(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-zipval-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _zip_path(self, data: bytes) -> Path:
        p = self.tmp / "archive.zip"
        p.write_bytes(data)
        return p

    def test_valid_zip_stages_successfully(self):
        data = _build_zip({"ZEITRISS-md-abc/setup.json": "{}", "ZEITRISS-md-abc/scripts/x.py": "pass\n"})
        staging = lu.validate_and_stage_zip(self._zip_path(data), staging_root=self.tmp / "stage")
        self.assertTrue((staging / "ZEITRISS-md-abc" / "setup.json").exists())

    def test_executable_bit_preserved_on_extract(self):
        # CRIT-R2-01/U3: der dokumentierte Starter muss nach der ZIP-Übernahme
        # ohne manuelles `chmod +x` ausführbar bleiben. `zipfile.extractall()`
        # verwirft die Unix-Permission-Bits -- `validate_and_stage_zip` muss die
        # im Archiv vermerkten Exec-Bits gezielt wiederherstellen (und nur die).
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            exe = zipfile.ZipInfo("ZEITRISS-md-abc/zeitriss.sh")
            exe.external_attr = (0o100755 << 16)  # reguläre Datei, +x
            zf.writestr(exe, "#!/usr/bin/env bash\necho hi\n")
            plain = zipfile.ZipInfo("ZEITRISS-md-abc/setup.json")
            plain.external_attr = (0o100644 << 16)  # reguläre Datei, kein +x
            zf.writestr(plain, "{}")
        staging = lu.validate_and_stage_zip(self._zip_path(buf.getvalue()), staging_root=self.tmp / "stage")
        sh = staging / "ZEITRISS-md-abc" / "zeitriss.sh"
        js = staging / "ZEITRISS-md-abc" / "setup.json"
        self.assertTrue(sh.stat().st_mode & 0o111, "zeitriss.sh muss nach dem Staging ausführbar sein (+x)")
        self.assertFalse(js.stat().st_mode & 0o111, "nicht-ausführbare Dateien dürfen kein +x bekommen")

    def test_corrupt_archive_rejected_before_any_write(self):
        bad = self._zip_path(b"this is not a zip file at all")
        stage_dir = self.tmp / "stage"
        with self.assertRaises(ValueError) as cm:
            lu.validate_and_stage_zip(bad, staging_root=stage_dir)
        self.assertIn("beschädigt", str(cm.exception))
        self.assertEqual(list(stage_dir.iterdir()) if stage_dir.exists() else [], [])

    def test_path_traversal_rejected(self):
        data = _build_zip({"../evil.txt": "pwned"})
        stage_dir = self.tmp / "stage"
        with self.assertRaises(ValueError) as cm:
            lu.validate_and_stage_zip(self._zip_path(data), staging_root=stage_dir)
        self.assertIn("Traversal", str(cm.exception))
        self.assertFalse((self.tmp / "evil.txt").exists())
        self.assertFalse((stage_dir / ".." / "evil.txt").resolve().exists())

    def test_absolute_path_entry_rejected(self):
        data = _build_zip({"/etc/evil.txt": "pwned"})
        with self.assertRaises(ValueError) as cm:
            lu.validate_and_stage_zip(self._zip_path(data), staging_root=self.tmp / "stage")
        self.assertIn("Unsichere Pfadangabe", str(cm.exception))

    def test_symlink_entry_rejected(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            info = zipfile.ZipInfo("link.txt")
            info.external_attr = (0o120777 << 16)  # S_IFLNK
            zf.writestr(info, "target.txt")
        with self.assertRaises(ValueError) as cm:
            lu.validate_and_stage_zip(self._zip_path(buf.getvalue()), staging_root=self.tmp / "stage")
        self.assertIn("Symlink", str(cm.exception))

    def test_oversized_entry_rejected(self):
        data = _build_zip({"big.txt": "x" * 1000})
        with mock.patch.object(lu, "MAX_ZIP_ENTRY_BYTES", 10):
            with self.assertRaises(ValueError) as cm:
                lu.validate_and_stage_zip(self._zip_path(data), staging_root=self.tmp / "stage")
        self.assertIn("zu groß", str(cm.exception))

    def test_total_size_cap_rejected(self):
        data = _build_zip({"a.txt": "x" * 50, "b.txt": "x" * 50})
        with mock.patch.object(lu, "MAX_ZIP_TOTAL_BYTES", 60):
            with self.assertRaises(ValueError) as cm:
                lu.validate_and_stage_zip(self._zip_path(data), staging_root=self.tmp / "stage")
        self.assertIn("Gesamtgröße", str(cm.exception))

    def test_too_many_entries_rejected(self):
        data = _build_zip({f"f{i}.txt": "x" for i in range(5)})
        with mock.patch.object(lu, "MAX_ZIP_ENTRIES", 3):
            with self.assertRaises(ValueError) as cm:
                lu.validate_and_stage_zip(self._zip_path(data), staging_root=self.tmp / "stage")
        self.assertIn("zu viele Einträge", str(cm.exception))


# ── U4/U5 ZIP-Übernahme: Schutz + lokale Abweichung + Resumability ──────

class TestAdoptStagedUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-adopt-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()

    def _staging(self, files: dict) -> Path:
        staging = Path(tempfile.mkdtemp(dir=self.tmp)) / "ZEITRISS-md-rev"
        _write_files(staging, files)
        return staging.parent

    def test_first_time_migration_of_unmanaged_install_establishes_manifest(self):
        """U3: eine bisher unverwaltete ZIP-Installation wird bei der ersten
        bewusst gewählten Aktualisierung in den verwalteten Stand überführt,
        statt die Fernrevision blind als 'schon installiert' zu verbuchen.
        R3-02: eine abweichende, nie verwaltete Datei wird dabei NICHT
        stillschweigend überschrieben -- das muss (wie hier) explizit per
        `allow_unverified_overwrite=True` (informierte Zustimmung, s. echter
        Caller `launcher._attempt_zip_install`) freigegeben werden."""
        (self.repo / "setup.json").write_text('{"version": "old"}', encoding="utf-8")
        staging = self._staging({"setup.json": '{"version": "new"}', "scripts/x.py": "pass\n"})

        result = lu.adopt_staged_update(self.repo, staging, "rev-new", allow_unverified_overwrite=True)
        self.assertTrue(result.ok, result.message)
        self.assertEqual((self.repo / "setup.json").read_text(), '{"version": "new"}')
        state = lu.read_state(self.repo)
        self.assertEqual(state["method"], "zip")
        self.assertEqual(state["installed_rev"], "rev-new")
        self.assertEqual(state["sync_status"], "pending")
        self.assertIn("setup.json", state["managed_files"])

    def test_unverified_existing_file_blocks_by_default_without_consent(self):
        """R3-02: 'unverwaltet' (kein `baseline_hash`) ist KEIN Beleg für
        'unverändert' oder 'zum Überschreiben freigegeben'. Ohne explizite
        Freigabe (`allow_unverified_overwrite`) muss eine abweichende,
        existierende, nie verwaltete Datei den gesamten Lauf stoppen --
        NICHTS wird geschrieben, kein Teil-Mix."""
        (self.repo / "setup.json").write_text('{"version": "old"}', encoding="utf-8")
        staging = self._staging({"setup.json": '{"version": "new"}', "scripts/x.py": "pass\n"})

        result = lu.adopt_staged_update(self.repo, staging, "rev-new")
        self.assertFalse(result.ok)
        self.assertIn("setup.json", result.unverified)
        self.assertEqual((self.repo / "setup.json").read_text(), '{"version": "old"}')
        self.assertFalse((self.repo / "scripts" / "x.py").exists())  # kein Teil-Mix
        self.assertNotIn("installed_rev", lu.read_state(self.repo))

    def test_unverified_file_already_matching_new_content_is_not_flagged(self):
        """Ein Spezialfall ohne jede Unsicherheit: der lokale Inhalt
        entspricht bereits exakt dem, was installiert würde -- das ist kein
        echter Unterschied und darf nicht blockieren."""
        (self.repo / "setup.json").write_text('{"version": "new"}', encoding="utf-8")
        staging = self._staging({"setup.json": '{"version": "new"}', "scripts/x.py": "pass\n"})

        result = lu.adopt_staged_update(self.repo, staging, "rev-new")
        self.assertTrue(result.ok, result.message)

    def test_protected_paths_never_touched(self):
        protected_file = self.repo / "internal" / "mmo_sim_data" / "states" / "player.json"
        protected_file.parent.mkdir(parents=True)
        protected_file.write_text('{"save": "precious"}', encoding="utf-8")
        sync_manifest = self.repo / ".openwebui-sync.json"
        sync_manifest.write_text('{"kb_files": {}}', encoding="utf-8")

        staging = self._staging({
            "setup.json": "{}",
            "internal/mmo_sim_data/states/player.json": '{"save": "OVERWRITTEN"}',
            ".openwebui-sync.json": '{"kb_files": {"x": 1}}',
        })
        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertTrue(result.ok, result.message)
        self.assertEqual(protected_file.read_text(), '{"save": "precious"}')
        self.assertEqual(sync_manifest.read_text(), '{"kb_files": {}}')

    def test_local_deviation_blocks_whole_adoption_no_partial_mix(self):
        staging1 = self._staging({"setup.json": "{}", "scripts/a.py": "A1\n", "scripts/b.py": "B1\n"})
        first = lu.adopt_staged_update(self.repo, staging1, "rev-1")
        self.assertTrue(first.ok, first.message)

        # Nutzer editiert eine verwaltete Datei von Hand nach der Übernahme.
        (self.repo / "scripts" / "a.py").write_text("A1-hand-edited\n", encoding="utf-8")

        staging2 = self._staging({"setup.json": "{}", "scripts/a.py": "A2\n", "scripts/b.py": "B2\n"})
        second = lu.adopt_staged_update(self.repo, staging2, "rev-2")
        self.assertFalse(second.ok)
        self.assertIn("scripts/a.py", second.deviated)
        # Nichts wurde geschrieben -- auch b.py (das NICHT abweicht) bleibt beim alten Stand.
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B1\n")
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-1")

    def test_missing_setup_json_in_staging_rejected(self):
        staging = self._staging({"scripts/a.py": "x\n"})
        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertFalse(result.ok)
        self.assertIn("setup.json", result.message)
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_interrupted_adoption_stays_incomplete_and_is_resumable(self):
        staging = self._staging({"setup.json": "{}", "scripts/a.py": "A\n", "scripts/b.py": "B\n"})
        real_copy2 = shutil.copy2
        calls = {"n": 0}

        def flaky_copy2(src, dst, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full (simulated)")
            return real_copy2(src, dst, *a, **kw)

        with mock.patch.object(lu.shutil, "copy2", side_effect=flaky_copy2):
            first = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertFalse(first.ok)
        self.assertNotIn("installed_rev", lu.read_state(self.repo))
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "failed")

        second = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertTrue(second.ok, second.message)
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-1")
        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B\n")

    def test_interrupted_FOLLOWUP_update_does_not_misread_own_partial_write_as_deviation(self):
        """R3-03: der vorhandene Unterbrechungstest oben startet mit einer
        leeren, UNVERWALTETEN Installation (kein vorheriges Manifest) -- er
        prüft NICHT den Folgeupdatefall. Hier: A ist bereits regulär
        verwaltet installiert (Manifest vorhanden); A→B bricht NACH
        mindestens einer tatsächlich kopierten Datei ab. Vorher wurde die
        schon auf B gebrachte Datei beim Wiederanlauf gegen das ALTE
        Manifest (A) verglichen und fälschlich als fremde lokale Abweichung
        geblockt, statt als eigenen, bereits erledigten Teilschritt zu
        erkennen."""
        staging_a = self._staging({"setup.json": "{}", "scripts/a.py": "A1\n", "scripts/b.py": "B1\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)

        staging_b = self._staging({"setup.json": "{}", "scripts/a.py": "A2\n", "scripts/b.py": "B2\n"})
        real_copy2 = shutil.copy2
        calls = {"n": 0}

        def flaky_copy2(src, dst, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full (simulated)")
            return real_copy2(src, dst, *a, **kw)

        with mock.patch.object(lu.shutil, "copy2", side_effect=flaky_copy2):
            interrupted = lu.adopt_staged_update(self.repo, staging_b, "rev-B")
        self.assertFalse(interrupted.ok)
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-A")  # noch nicht als fertig markiert

        resumed = lu.adopt_staged_update(self.repo, staging_b, "rev-B")
        self.assertTrue(resumed.ok, resumed.message)  # KEIN "deviated" trotz eigenem Teilschreiben
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-B")
        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A2\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B2\n")

    def test_removed_upstream_file_deleted_when_still_matching_old_manifest(self):
        """R3-03-Abnahme: der aktuelle Kopierweg entfernte bisher aus B
        entfallene, vormals verwaltete alte Code-Dateien NICHT. Eine Datei,
        die im neuen Paket fehlt UND lokal unverändert ist (Hash entspricht
        noch dem letzten Manifest), muss jetzt entfernt werden."""
        staging_a = self._staging({"setup.json": "{}", "scripts/old_module.py": "OLD\n", "scripts/keep.py": "K\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)
        self.assertTrue((self.repo / "scripts" / "old_module.py").exists())

        staging_b = self._staging({"setup.json": "{}", "scripts/keep.py": "K\n"})  # old_module.py entfaellt
        second = lu.adopt_staged_update(self.repo, staging_b, "rev-B")
        self.assertTrue(second.ok, second.message)
        self.assertFalse((self.repo / "scripts" / "old_module.py").exists())
        self.assertNotIn("scripts/old_module.py", lu.read_state(self.repo)["managed_files"])

    def test_removed_upstream_file_kept_when_locally_modified(self):
        """Gegenprobe: eine entfallene Datei, die lokal VERÄNDERT wurde,
        darf nicht einfach mitgelöscht werden (R3-03-Abnahme: 'unverwaltete
        fremde Dateien nicht mitlöschen' -- gilt analog für lokal
        angepasste, vormals verwaltete Dateien)."""
        staging_a = self._staging({"setup.json": "{}", "scripts/old_module.py": "OLD\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)
        (self.repo / "scripts" / "old_module.py").write_text("HAND-EDITED\n", encoding="utf-8")

        staging_b = self._staging({"setup.json": "{}"})
        second = lu.adopt_staged_update(self.repo, staging_b, "rev-B")
        self.assertTrue(second.ok, second.message)
        self.assertTrue((self.repo / "scripts" / "old_module.py").exists())
        self.assertEqual((self.repo / "scripts" / "old_module.py").read_text(), "HAND-EDITED\n")

    def test_concurrent_adoption_attempt_is_rejected_while_lock_held(self):
        """R3-03-Abnahme, auf die R6-02-Schutzstelle angepasst: gleichzeitige
        Updateversuche muessen denselben Installationszustand schuetzen --
        kein paralleles Kopieren. Lebendigkeit wird jetzt ueber einen
        TATSAECHLICH gehaltenen `fcntl.flock` modelliert (massgeblich), nicht
        mehr ueber einen bloss hingeschriebenen PID (`os.kill(pid,0)` ist
        durch PID-Wiederverwendung taeuschbar; der neue Mechanismus stuetzt
        sich auf den kernelverwalteten OS-Lock). Ein separater fd haelt den
        Lock real; `adopt_staged_update`s interner `acquire_update_lock`
        scheitert daran mit 'läuft bereits' und kopiert NICHTS."""
        import fcntl as _fcntl
        staging = self._staging({"setup.json": "{}", "scripts/a.py": "A\n"})
        lp = lu._lock_path(self.repo)
        holder_fd = os.open(str(lp), os.O_CREAT | os.O_WRONLY, 0o644)
        _fcntl.flock(holder_fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
        os.write(holder_fd, b"1 fremder-flock-halter\n")
        try:
            result = lu.adopt_staged_update(self.repo, staging, "rev-1")
            self.assertFalse(result.ok)
            self.assertIn("läuft bereits", result.message)
            self.assertEqual(list(self.repo.iterdir()), [lp])
        finally:
            _fcntl.flock(holder_fd, _fcntl.LOCK_UN)
            os.close(holder_fd)

    def test_stale_lock_from_dead_process_is_reclaimed(self):
        """Ein Lock einer PID, die nicht mehr existiert (z. B. nach einem
        Absturz), darf nicht dauerhaft blockieren."""
        dead_pid = 999999  # praktisch garantiert nicht belegt
        lu._lock_path(self.repo).write_text(f"{dead_pid} 2020-01-01T00:00:00Z\n", encoding="utf-8")
        staging = self._staging({"setup.json": "{}", "scripts/a.py": "A\n"})
        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertTrue(result.ok, result.message)

    def test_symlink_target_escape_is_rejected_without_following_it(self):
        """R3-02/b: `is_protected` prüft nur Pfad-STRUKTUR -- ein Ziel-
        Symlink auf eine Datei AUSSERHALB der Installation wird davon nicht
        erfasst, und `shutil.copy2` würde ihm folgen. Muss abgelehnt werden,
        BEVOR irgendetwas geschrieben wird."""
        outside = self.tmp / "outside.txt"
        outside.write_text("harmless original\n", encoding="utf-8")
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "a.py").symlink_to(outside)

        staging = self._staging({"setup.json": "{}", "scripts/a.py": "MALICIOUS OVERWRITE\n"})
        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertFalse(result.ok)
        self.assertIn("Symlink", result.message)
        self.assertEqual(outside.read_text(), "harmless original\n")


# ── U3 kompletter ZIP-Weg (Download + Stage + Adopt) ────────────────────

class _FakeResponse:
    def __init__(self, data: bytes):
        self._buf = io.BytesIO(data)

    def read(self, n=-1):
        return self._buf.read(n)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class TestPerformZipUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-zipflow-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        (self.repo / "old_untouched.txt").write_text("keep me\n", encoding="utf-8")

    def test_successful_end_to_end_zip_update(self):
        data = _build_zip({"ZEITRISS-md-rev1/setup.json": "{}", "ZEITRISS-md-rev1/scripts/x.py": "NEW\n"})
        opener = lambda url, timeout: _FakeResponse(data)  # noqa: E731
        result = lu.perform_zip_update(self.repo, zip_url="https://example.invalid/x.zip",
                                        target_rev="rev1", opener=opener)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.installed_rev, "rev1")
        self.assertEqual((self.repo / "scripts" / "x.py").read_text(), "NEW\n")
        # fremde, nicht im Paket enthaltene Datei bleibt unangetastet.
        self.assertEqual((self.repo / "old_untouched.txt").read_text(), "keep me\n")

    def test_corrupt_download_rejected_repo_untouched(self):
        opener = lambda url, timeout: _FakeResponse(b"not a real zip")  # noqa: E731
        before = sorted(p.name for p in self.repo.iterdir())
        result = lu.perform_zip_update(self.repo, zip_url="https://example.invalid/x.zip",
                                        target_rev="rev1", opener=opener)
        self.assertFalse(result.ok)
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()), before)

    def test_download_error_rejected_repo_untouched(self):
        def raising_opener(url, timeout):
            raise OSError("connection refused")
        before = sorted(p.name for p in self.repo.iterdir())
        result = lu.perform_zip_update(self.repo, zip_url="https://example.invalid/x.zip",
                                        target_rev="rev1", opener=raising_opener)
        self.assertFalse(result.ok)
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()), before)


class TestBuildArchiveUrl(unittest.TestCase):
    def test_default_points_to_official_github_source(self):
        url = lu.build_archive_url("deadbeef")
        self.assertEqual(url, "https://github.com/pchospital-lab/ZEITRISS-md/archive/deadbeef.zip")

    def test_override_env_allows_http_https_file_only(self):
        env = {lu.ARCHIVE_URL_ENV_OVERRIDE: "file:///tmp/{rev}.zip", lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG: "1"}
        with mock.patch.dict("os.environ", env):
            self.assertEqual(lu.build_archive_url("abc"), "file:///tmp/abc.zip")
        env = {lu.ARCHIVE_URL_ENV_OVERRIDE: "ftp://evil/{rev}.zip", lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG: "1"}
        with mock.patch.dict("os.environ", env):
            with self.assertRaises(ValueError):
                lu.build_archive_url("abc")

    def test_override_env_without_enable_flag_is_inert(self):
        """R3-04/e: der Override darf in einer normalen Spielerumgebung NICHT
        wirken, nur weil die Variable (z. B. aus einer alten Shell) gesetzt
        ist -- erst der explizite Dev-/Test-Freigabeschalter aktiviert ihn."""
        with mock.patch.dict("os.environ", {lu.ARCHIVE_URL_ENV_OVERRIDE: "file:///tmp/{rev}.zip"}, clear=False):
            os.environ.pop(lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG, None)
            self.assertEqual(lu.build_archive_url("abc"),
                              "https://github.com/pchospital-lab/ZEITRISS-md/archive/abc.zip")


class TestDownloadZipArchive(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-dl-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_size_cap_enforced(self):
        opener = lambda url, timeout: _FakeResponse(b"x" * 1000)  # noqa: E731
        with self.assertRaises(ValueError) as cm:
            lu.download_zip_archive("https://example.invalid/x.zip", self.tmp / "out.zip",
                                     opener=opener, max_bytes=100)
        self.assertIn("Sicherheitsgrenze", str(cm.exception))

    def test_network_error_wrapped(self):
        def raising_opener(url, timeout):
            raise OSError("boom")
        with self.assertRaises(ValueError) as cm:
            lu.download_zip_archive("https://example.invalid/x.zip", self.tmp / "out.zip", opener=raising_opener)
        self.assertIn("Download fehlgeschlagen", str(cm.exception))


# ── U5 Sync im neuen Prozess (Matrix: "Syncfehler") ──────────────────────

class _FakeCompleted:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestRunSyncSubprocess(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-sync-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()

    def test_default_argv_targets_real_setup_py_sync(self):
        captured = {}

        def fake_runner(cmd, **kwargs):
            captured["cmd"] = cmd
            return _FakeCompleted(0, stdout="Sync abgeschlossen.")

        ok, tail = lu.run_sync_subprocess(self.repo, runner=fake_runner)
        self.assertTrue(ok)
        self.assertEqual(captured["cmd"], [sys.executable, str(self.repo / "scripts" / "setup.py"), "--sync", "--yes"])
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "ok")

    def test_failure_marks_state_failed_and_keeps_tail(self):
        def fake_runner(cmd, **kwargs):
            return _FakeCompleted(1, stdout="", stderr="Preset existiert nicht.\n")

        ok, tail = lu.run_sync_subprocess(self.repo, runner=fake_runner)
        self.assertFalse(ok)
        self.assertIn("Preset existiert nicht", tail)
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "failed")

    def test_timeout_marks_state_failed(self):
        def timing_out_runner(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 1))

        ok, tail = lu.run_sync_subprocess(self.repo, runner=timing_out_runner)
        self.assertFalse(ok)
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "failed")

    def test_successful_run_binds_kb_checked_at_to_the_same_sync_result_line(self):
        """U3 (UPDATE_UX_REVIEW.md R3, ZR-PR3317-RESTNACHZUG-20261124): die
        `kb_*`-Zähler brauchen einen EIGENEN Prüfzeitpunkt (`kb_checked_at`),
        der NUR gesetzt wird, wenn dieser Lauf wirklich eine `SYNC_RESULT`-
        Zeile geliefert hat -- nicht `sync_at`/`sync_failed_at` (die den
        GESAMTLAUF datieren, unabhängig davon, ob er eine Aufschlüsselung
        lieferte)."""
        def fake_runner(cmd, **kwargs):
            return _FakeCompleted(0, stdout="SYNC_RESULT preset_ok=1 kb_total=3 kb_confirmed=3 kb_failed=")

        ok, _tail = lu.run_sync_subprocess(self.repo, runner=fake_runner)
        self.assertTrue(ok)
        state = lu.read_state(self.repo)
        self.assertEqual(state["kb_total"], 3)
        self.assertEqual(state["kb_confirmed"], 3)
        self.assertIn("kb_checked_at", state)
        self.assertEqual(state["kb_checked_at"], state["sync_at"])

    def test_timeout_after_prior_confirmed_counters_does_not_restamp_stale_counters_as_fresh(self):
        """Der belegte Fehler aus R3: ein Timeout OHNE lesbare SYNC_RESULT-
        Zeile darf die ALTEN `kb_*`-Zähler NICHT mit einem FRISCHEN
        Zeitstempel versehen -- das würde (bei `launcher._describe_kb_
        sync_status`/`_check_persisted_sync_status`, die `kb_checked_at`
        lesen) eine stehengebliebene Teilbestätigung als gerade frisch
        bestätigt ausgeben, obwohl dieser Lauf NICHTS bestätigt hat."""
        # Lauf 1: echter Teilerfolg, liefert eine auswertbare SYNC_RESULT-Zeile.
        def ok_runner(cmd, **kwargs):
            return _FakeCompleted(1, stdout="SYNC_RESULT preset_ok=1 kb_total=19 kb_confirmed=18 kb_failed=sl-referenz.md")

        lu.run_sync_subprocess(self.repo, runner=ok_runner)
        state_after_run1 = lu.read_state(self.repo)
        self.assertEqual(state_after_run1["kb_confirmed"], 18)
        kb_checked_at_run1 = state_after_run1["kb_checked_at"]
        self.assertIsNotNone(kb_checked_at_run1)

        # Lauf 2: Timeout -- keine SYNC_RESULT-Zeile, keine neuen Zähler.
        def timing_out_runner(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 1))

        ok2, _tail2 = lu.run_sync_subprocess(self.repo, runner=timing_out_runner)
        self.assertFalse(ok2)
        state_after_run2 = lu.read_state(self.repo)
        self.assertEqual(state_after_run2["sync_status"], "failed")
        # Die alten Zähler UND ihr Prüfzeitpunkt bleiben unveraendert stehen --
        # NICHT mit dem neuen Fehlerzeitpunkt des Timeouts versehen.
        self.assertEqual(state_after_run2["kb_confirmed"], 18)
        self.assertEqual(state_after_run2["kb_total"], 19)
        self.assertEqual(state_after_run2["kb_checked_at"], kb_checked_at_run1)
        # Der Gesamtlauf-Fehlerzeitpunkt ist dagegen frisch und DARF (muss
        # nicht) vom alten kb_checked_at abweichen -- er beschreibt den
        # Timeout, nicht die (unveraenderten) Zaehler.
        self.assertIn("sync_failed_at", state_after_run2)

    def test_real_new_process_is_actually_spawned(self):
        """U5: beweist den Prozesswechsel MECHANISCH -- ein echter neuer
        Python-Interpreter laeuft, nicht nur eine In-Process-Funktion."""
        fixture_script = self.tmp / "fixture_sync_entry.py"
        fixture_script.write_text(
            "import sys\nprint('fixture-sync-ok pid=' + str(__import__('os').getpid()))\nsys.exit(0)\n",
            encoding="utf-8",
        )
        ok, tail = lu.run_sync_subprocess(
            self.repo, argv_override=[sys.executable, str(fixture_script)],
        )
        self.assertTrue(ok, tail)
        self.assertIn("fixture-sync-ok", tail)

    def test_u4_output_is_visible_line_by_line_during_the_run_not_only_after(self):
        """U4 (UPDATE_UX_REVIEW.md R4): VORHER `subprocess.run(capture_
        output=True)` -- puffert JEDE Ausgabe bis Prozessende, "Datei/Phase"
        waren dem Launcher laut Review erst NACH Prozessende zugänglich.
        Beweis am echten Kindprozess (kein injizierter `runner`, der würde
        den neuen Streaming-Pfad umgehen): ein Fixture-Skript schreibt ZWEI
        durch eine Pause getrennte Zeilen; der Haupt-Thread liest den
        geteilten stdout-Puffer WÄHREND `run_sync_subprocess` noch läuft und
        muss die ERSTE Zeile schon VOR der zweiten (und vor Prozessende)
        sehen."""
        fixture_script = self.tmp / "fixture_streaming_entry.py"
        fixture_script.write_text(
            "import sys, time\n"
            "print('phase-1-datei-a.md', flush=True)\n"
            "time.sleep(1.2)\n"
            "print('phase-2-datei-b.md', flush=True)\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        buf = io.StringIO()
        result: dict = {}

        def _call():
            with mock.patch("sys.stdout", buf):
                ok, tail = lu.run_sync_subprocess(
                    self.repo, argv_override=[sys.executable, str(fixture_script)],
                )
            result["ok"] = ok
            result["tail"] = tail

        t = threading.Thread(target=_call)
        t.start()
        try:
            saw_phase1_before_phase2_or_exit = False
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                snapshot = buf.getvalue()
                if "phase-1-datei-a.md" in snapshot:
                    saw_phase1_before_phase2_or_exit = "phase-2-datei-b.md" not in snapshot
                    break
                time.sleep(0.02)
        finally:
            t.join(timeout=5.0)

        self.assertTrue(result.get("ok"), result.get("tail"))
        self.assertTrue(
            saw_phase1_before_phase2_or_exit,
            "phase-1 muss sichtbar sein, WÄHREND der Kindprozess noch auf "
            "phase-2 wartet -- nicht erst nach Prozessende (gepufferte Ausgabe).",
        )
        self.assertIn("phase-1-datei-a.md", buf.getvalue())
        self.assertIn("phase-2-datei-b.md", buf.getvalue())

    def test_u4_silent_hang_is_still_killed_at_the_outer_deadline(self):
        """Gegenfall/Robustheit: ein Kindprozess, der GAR KEINE Zeile
        schreibt (reiner Sleep), darf den äußeren `timeout` trotzdem nicht
        überschreiten -- ein reines `for line in proc.stdout` ohne eigene
        Fristprüfung würde das verpassen, weil `readline()` bis zur nächsten
        Zeile blockiert. Kurzer `timeout`, bewusst lange Sleep-Dauer, damit
        ein Fehlschlag hier nicht als 'zufällig noch durchgelaufen'
        unentdeckt bliebe."""
        fixture_script = self.tmp / "fixture_silent_hang_entry.py"
        fixture_script.write_text(
            "import time\ntime.sleep(5)\n",
            encoding="utf-8",
        )
        started = time.monotonic()
        ok, tail = lu.run_sync_subprocess(
            self.repo, argv_override=[sys.executable, str(fixture_script)], timeout=1.0,
        )
        elapsed = time.monotonic() - started
        self.assertFalse(ok)
        self.assertEqual(lu.read_state(self.repo)["sync_status"], "failed")
        self.assertLess(elapsed, 4.0, "der stille Kindprozess wurde nicht rechtzeitig gekillt")


class TestRestartLauncher(unittest.TestCase):
    def test_restart_uses_real_zeitriss_entrypoint(self):
        repo = Path(tempfile.mkdtemp(prefix="launcher-update-restart-"))
        self.addCleanup(shutil.rmtree, repo, ignore_errors=True)
        captured = {}
        lu.restart_launcher(repo, exec_fn=lambda argv: captured.setdefault("argv", argv))
        self.assertEqual(captured["argv"], [sys.executable, str(repo / "scripts" / "zeitriss.py")])


class TestStateFileRoundTrip(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-update-state-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_read_state_missing_file_is_empty_dict(self):
        self.assertEqual(lu.read_state(self.tmp), {})

    def test_write_state_merges_and_is_atomic_rename(self):
        lu.write_state(self.tmp, a=1)
        lu.write_state(self.tmp, b=2)
        state = lu.read_state(self.tmp)
        self.assertEqual(state["a"], 1)
        self.assertEqual(state["b"], 2)
        self.assertFalse((self.tmp / (lu.STATE_FILENAME + ".tmp")).exists())

    def test_read_state_corrupt_json_is_safely_empty(self):
        lu.state_path(self.tmp).write_text("{not valid json", encoding="utf-8")
        self.assertEqual(lu.read_state(self.tmp), {})


if __name__ == "__main__":
    unittest.main()
