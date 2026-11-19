#!/usr/bin/env python3
"""scripts/tests/test_r7_03_candidate_rev_archive_binding_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7, §04 (R7-03).

Ursache (verifiziert am echten Code, `launcher_update.check_for_update`/
`build_archive_url`/`adopt_staged_update`, VOR diesem Fix): der r6-Test
tauschte NUR die Archivbytes über `ARCHIVE_URL_ENV_OVERRIDE` aus --
`check_for_update` las dabei WEITERHIN die offizielle Quelle (`main`), der
dort gelesene `remote_rev` wanderte unverändert als `target_rev` bis zu
`mark_files_updated`: der persistierte `installed_rev` nannte danach eine
ANDERE Revision (die offizielle Main-SHA) als die tatsächlich installierten
Kandidatenbytes. `adopt_staged_update`/`_effective_source_root` validieren
den ZIP-Inhalt NIE gegen `target_rev` (reiner Vertrauens-Parameter für die
Statusdatei) -- es gab VORHER keinen Weg, Zielrevision UND Archiv-Override
an denselben expliziten Kandidaten zu binden.

Kleinster kausaler Fix: `CANDIDATE_REV_ENV_OVERRIDE` (`LAUNCHER_UPDATE_
CANDIDATE_REV`) -- wirksam NUR gemeinsam mit der BEREITS bestehenden
Archiv-Override-Freischaltung (`ARCHIVE_URL_OVERRIDE_ENABLE_FLAG`), damit
ein kontrollierter Vor-Merge-Test beide Override-Variablen IMMER gemeinsam
setzt. `check_for_update` meldet dann den gepinnten Kandidaten als
`remote_rev`, ausdrücklich ALS "kontrollierter Vor-Merge-Test, KEIN
offizieller Check" gekennzeichnet (nie als "geprüfte/offizielle Quelle"
etikettiert). Der offizielle Default-Check (keine Override-Variablen)
bleibt read-only unverändert.

Reiner Testcode, keine Produktabhängigkeit hierauf. Kein echtes Netz --
`file://`-URLs für den Archiv-Download (echtes `urllib.request.urlopen`,
kein Opener-Mock nötig)."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import launcher_update as lu  # noqa: E402

_OFFICIAL_SHA = "o" * 40
_CANDIDATE_SHA = "c" * 40


def _build_zip_bytes(entries: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _official_http_get(url, timeout):
    return json.dumps({"sha": _OFFICIAL_SHA}).encode("utf-8")


class TestCandidateRevCheckBinding(unittest.TestCase):
    """Deckt `check_for_update` direkt -- der Default-Check (read-only,
    offizielle Quelle) UND der neue gepinnte Vor-Merge-Kandidatenpfad."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="r7-03-candidate-rev-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        lu.write_state(self.repo, method="zip", installed_rev="local" * 8, sync_status="ok")
        self._env_patcher = mock.patch.dict("os.environ", {}, clear=False)
        self._env_patcher.start()
        self.addCleanup(self._env_patcher.stop)
        for var in (lu.CANDIDATE_REV_ENV_OVERRIDE, lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG, lu.ARCHIVE_URL_ENV_OVERRIDE):
            import os
            os.environ.pop(var, None)

    def test_default_check_without_override_reads_official_source_unchanged(self):
        """Regressionsschutz: OHNE beide Override-Variablen bleibt
        `check_for_update` bytegleich zum Vor-Fix-Verhalten -- liest
        ausschließlich die offizielle Quelle."""
        result = lu.check_for_update(self.repo, http_get=_official_http_get)
        self.assertEqual(result.remote_rev, _OFFICIAL_SHA)
        self.assertEqual(result.status, "update_available")
        self.assertIn("geprüften Quelle", result.reason)

    def test_candidate_override_alone_without_enable_flag_is_inert(self):
        """`CANDIDATE_REV_ENV_OVERRIDE` allein (OHNE die gemeinsame
        Freischaltung) darf NICHT wirken -- dieselbe Absicherung wie der
        bestehende Archiv-Override."""
        import os
        os.environ[lu.CANDIDATE_REV_ENV_OVERRIDE] = _CANDIDATE_SHA
        result = lu.check_for_update(self.repo, http_get=_official_http_get)
        self.assertEqual(result.remote_rev, _OFFICIAL_SHA, (
            "ohne den gemeinsamen Freigabeschalter darf der Kandidaten-Override NICHT greifen"
        ))

    def test_candidate_override_with_enable_flag_pins_check_not_official_main(self):
        """Kernbeleg: mit BEIDEN Override-Variablen meldet `check_for_update`
        den gepinnten Kandidaten -- NICHT die offizielle Main-SHA -- und
        etikettiert ihn ausdrücklich als kontrollierten Vor-Merge-Test, NIE
        als geprüfte/offizielle Quelle (verhindert genau das in R7-03
        benannte Fehletikett)."""
        import os
        os.environ[lu.CANDIDATE_REV_ENV_OVERRIDE] = _CANDIDATE_SHA
        os.environ[lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG] = "1"

        def _official_that_must_not_be_trusted(url, timeout):
            raise AssertionError(
                "der offizielle HTTP-Check haette bei aktivem Kandidaten-Override gar nicht "
                "konsultiert werden duerfen."
            )

        result = lu.check_for_update(self.repo, http_get=_official_that_must_not_be_trusted)
        self.assertEqual(result.remote_rev, _CANDIDATE_SHA)
        self.assertEqual(result.status, "update_available")
        self.assertIn("Vor-Merge", result.reason)
        self.assertIn("kein offizieller check", result.reason.lower())
        self.assertNotIn("geprüfte Quelle", result.reason)

    def test_candidate_override_matching_local_rev_reports_current_not_update_available(self):
        import os
        os.environ[lu.CANDIDATE_REV_ENV_OVERRIDE] = _CANDIDATE_SHA
        os.environ[lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG] = "1"
        lu.write_state(self.repo, method="zip", installed_rev=_CANDIDATE_SHA, sync_status="ok")
        result = lu.check_for_update(self.repo, http_get=_official_http_get)
        self.assertEqual(result.status, "current")
        self.assertEqual(result.remote_rev, _CANDIDATE_SHA)


class TestCandidateRevFullZipInstallBinding(unittest.TestCase):
    """End-to-end (echte Helfer, `file://`-Archiv-Download, kein Opener-
    Mock): `check_for_update` -> `build_archive_url` -> `download_zip_
    archive` -> `validate_and_stage_zip` -> `adopt_staged_update` ->
    `mark_files_updated` -- GENAU die reale Aufrufkette aus `scripts.
    launcher._attempt_zip_install`. Belegt, dass Zielrevision UND
    installierte Bytes nach dem Fix GARANTIERT denselben gepinnten
    Kandidaten nennen -- der reale r6-Mismatch (installed_rev=offizielles
    Main bei tatsächlich installierten Kandidatenbytes) ist damit
    ausgeschlossen, solange beide Override-Variablen gemeinsam gesetzt
    werden."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="r7-03-candidate-rev-zip-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        (self.repo / "app.py").write_text("OLD\n", encoding="utf-8")
        (self.repo / "setup.json").write_text('{"project": "ZEITRISS-R7-03-TESTQUELLE"}', encoding="utf-8")
        lu.write_state(
            self.repo, method="zip", installed_rev="old" * 14, sync_status="ok",
            managed_files={
                "app.py": lu._sha256_file(self.repo / "app.py"),
                "setup.json": lu._sha256_file(self.repo / "setup.json"),
            },
        )
        self._env_patcher = mock.patch.dict("os.environ", {}, clear=False)
        self._env_patcher.start()
        self.addCleanup(self._env_patcher.stop)
        import os
        for var in (lu.CANDIDATE_REV_ENV_OVERRIDE, lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG, lu.ARCHIVE_URL_ENV_OVERRIDE):
            os.environ.pop(var, None)

        # Die tatsächliche Kandidaten-ZIP liegt lokal -- Inhalt trägt
        # erkennbar `_CANDIDATE_SHA` im Top-Level-Ordnernamen, wie ein
        # echtes GitHub-Archiv (`_effective_source_root` wickelt das aus).
        self.candidate_zip_path = self.tmp / f"{_CANDIDATE_SHA}.zip"
        self.candidate_zip_path.write_bytes(_build_zip_bytes({
            f"ZEITRISS-md-{_CANDIDATE_SHA}/app.py": "KANDIDAT-NEU\n",
            f"ZEITRISS-md-{_CANDIDATE_SHA}/setup.json": '{"project": "ZEITRISS-R7-03-TESTQUELLE"}',
        }))

    def test_pinned_candidate_check_and_archive_install_agree_on_same_rev(self):
        import os
        os.environ[lu.CANDIDATE_REV_ENV_OVERRIDE] = _CANDIDATE_SHA
        os.environ[lu.ARCHIVE_URL_OVERRIDE_ENABLE_FLAG] = "1"
        # Fixer file://-Pfad (KEIN `{rev}`-Platzhalter) -- genau die r6-
        # Konstruktion ("tauschte nur Archivbytes aus").
        os.environ[lu.ARCHIVE_URL_ENV_OVERRIDE] = f"file://{self.candidate_zip_path}"

        def _official_that_must_not_be_trusted(url, timeout):
            raise AssertionError("offizieller Check haette bei aktivem Kandidaten-Override nicht laufen duerfen.")

        check = lu.check_for_update(self.repo, http_get=_official_that_must_not_be_trusted)
        self.assertEqual(check.status, "update_available")
        self.assertEqual(check.remote_rev, _CANDIDATE_SHA)
        target_rev = check.remote_rev

        zip_url = lu.build_archive_url(target_rev)
        self.assertEqual(zip_url, f"file://{self.candidate_zip_path}")

        zres = lu.perform_zip_update(self.repo, zip_url=zip_url, target_rev=target_rev)
        self.assertTrue(zres.ok, zres.message)
        self.assertEqual(zres.installed_rev, _CANDIDATE_SHA)

        lu.mark_files_updated(self.repo, method="zip", rev=zres.installed_rev)
        final_state = lu.read_state(self.repo)
        self.assertEqual(final_state["installed_rev"], _CANDIDATE_SHA, (
            "Zielrevision und installierte Bytes muessen denselben gepinnten Kandidaten nennen -- "
            "genau der r6-Mismatch (installed_rev=offizielles Main bei Kandidatenbytes), den dieser "
            "Fix ausschliesst."
        ))
        self.assertEqual((self.repo / "app.py").read_text(encoding="utf-8"), "KANDIDAT-NEU\n", (
            "die tatsaechlich installierten Bytes muessen zum GLEICHEN Kandidaten gehoeren wie "
            "der persistierte installed_rev."
        ))


if __name__ == "__main__":
    unittest.main()
