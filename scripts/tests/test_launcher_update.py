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
import shutil
import subprocess
import sys
import tempfile
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
        statt die Fernrevision blind als 'schon installiert' zu verbuchen."""
        (self.repo / "setup.json").write_text('{"version": "old"}', encoding="utf-8")
        staging = self._staging({"setup.json": '{"version": "new"}', "scripts/x.py": "pass\n"})

        result = lu.adopt_staged_update(self.repo, staging, "rev-new")
        self.assertTrue(result.ok, result.message)
        self.assertEqual((self.repo / "setup.json").read_text(), '{"version": "new"}')
        state = lu.read_state(self.repo)
        self.assertEqual(state["method"], "zip")
        self.assertEqual(state["installed_rev"], "rev-new")
        self.assertEqual(state["sync_status"], "pending")
        self.assertIn("setup.json", state["managed_files"])

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
        with mock.patch.dict("os.environ", {lu.ARCHIVE_URL_ENV_OVERRIDE: "file:///tmp/{rev}.zip"}):
            self.assertEqual(lu.build_archive_url("abc"), "file:///tmp/abc.zip")
        with mock.patch.dict("os.environ", {lu.ARCHIVE_URL_ENV_OVERRIDE: "ftp://evil/{rev}.zip"}):
            with self.assertRaises(ValueError):
                lu.build_archive_url("abc")


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
