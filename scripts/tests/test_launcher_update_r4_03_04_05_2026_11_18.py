#!/usr/bin/env python3
"""scripts/tests/test_launcher_update_r4_03_04_05_2026_11_18.py — R4-03/
R4-04/R4-05 Regression (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r4,
01_GENERAL_REVIEW.md, 02_NACHZUG_AUFTRAG.md Block C).

Treibt den realen ZIP-Übernahmeweg `scripts.launcher_update.
adopt_staged_update` / `acquire_update_lock` / `release_update_lock` an,
identischer Fixture-Stil zu `test_launcher_update.py::TestAdoptStagedUpdate`
(kontrollierte Staging-Verzeichnisse auf der Platte, kein echtes Netz).

- R4-03: identische Bytes dürfen fehlende `0o111`-Ausführungsbits nicht
  überspringen.
- R4-04: eine Teilkopie darf `dst` nicht in einem Teilzustand hinterlassen
  (atomarer Austausch); eine unterbrochene Installation darf bei einem
  SPÄTEREN Lauf gegen eine ANDERE (neuere) Zielrevision nicht als fremde
  Abweichung fehlgedeutet werden.
- R4-05: atomare, besitzgebundene Sperre (echter Mehrprozess-Wettlauf);
  die Löschphase wendet dieselbe Symlink-/Pfadschutzprüfung an wie geplante
  Kopien; eine bereits fehlende Altdatei wird ehrlich aus dem Manifest
  entfernt, ohne als 'entfernt' gezählt zu werden."""
from __future__ import annotations

import multiprocessing
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import launcher_update as lu  # noqa: E402


def _write_files(path: Path, files: dict) -> None:
    for relpath, content in files.items():
        p = path / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


class _AdoptFixtureBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="r4-launcher-update-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "install"
        self.repo.mkdir()

    def _staging(self, files: dict) -> Path:
        staging = Path(tempfile.mkdtemp(dir=self.tmp)) / "ZEITRISS-md-rev"
        _write_files(staging, files)
        return staging.parent


# ── R4-03: identische Bytes duerfen exec-Bits nicht ueberspringen ──────────

class TestR403ExecutableBitsOnIdenticalContent(_AdoptFixtureBase):
    def test_identical_starter_bytes_without_exec_bit_become_executable_without_manual_chmod(self):
        """Realer ZIP-Menueweg: `zeitriss.sh` ist bytegleich zum Paket, aber
        am Ziel mit Modus 0644 (ohne +x) -- z. B. aus einer unverwalteten
        ZIP-Installation oder einem Dateisystem, das Ausfuehrungsbits nicht
        erhalten hat. 01_GENERAL_REVIEW.md R4-03: der Resume-Skip (SHA256-
        Gleichheit) liess `dst` bisher KOMPLETT unberuehrt, auch dessen
        Modus -- nach dem Fix ist `./zeitriss.sh` danach direkt ausfuehrbar,
        OHNE manuelles chmod."""
        starter_content = "#!/bin/sh\necho hi\n"
        (self.repo / "setup.json").write_text("{}", encoding="utf-8")
        (self.repo / "zeitriss.sh").write_text(starter_content, encoding="utf-8")
        self.repo.joinpath("zeitriss.sh").chmod(0o644)

        staging = self._staging({"setup.json": "{}", "zeitriss.sh": starter_content})
        staging_sh = staging / "ZEITRISS-md-rev" / "zeitriss.sh"
        staging_sh.chmod(0o755)

        dst = self.repo / "zeitriss.sh"
        self.assertEqual(dst.stat().st_mode & 0o111, 0, "Vorbedingung: Ziel ist NICHT ausfuehrbar")

        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertTrue(result.ok, result.message)
        self.assertNotEqual(dst.stat().st_mode & 0o111, 0, "zeitriss.sh haette ausfuehrbar werden muessen")
        self.assertEqual(dst.read_text(), starter_content, "Inhalt darf sich nicht veraendert haben")

    def test_executable_bit_fix_does_not_grant_extra_permission_bits(self):
        """Additiv NUR die drei Ausfuehren-Bits -- kein Uebernehmen anderer
        Modusbits (z. B. Gruppen-/World-Schreibrechte) aus dem Paket."""
        starter_content = "#!/bin/sh\necho hi\n"
        (self.repo / "setup.json").write_text("{}", encoding="utf-8")
        (self.repo / "zeitriss.sh").write_text(starter_content, encoding="utf-8")
        self.repo.joinpath("zeitriss.sh").chmod(0o600)

        staging = self._staging({"setup.json": "{}", "zeitriss.sh": starter_content})
        staging_sh = staging / "ZEITRISS-md-rev" / "zeitriss.sh"
        staging_sh.chmod(0o777)  # uebertrieben freizuegig im Paket

        result = lu.adopt_staged_update(self.repo, staging, "rev-1")
        self.assertTrue(result.ok, result.message)
        mode = (self.repo / "zeitriss.sh").stat().st_mode & 0o777
        # Nur die urspruenglichen 0o600-Bits PLUS 0o111 (Ausfuehren) -- kein 0o022/0o066 uebernommen.
        self.assertEqual(mode, 0o711, f"unerwarteter Modus {oct(mode)} -- mehr als nur exec-Bits uebernommen")


# ── R4-04: atomare Teilkopie + Zielbindung ueber Revisionswechsel ──────────

class TestR404AtomicPartialCopyAndRevisionBinding(_AdoptFixtureBase):
    def test_mid_copy_failure_leaves_existing_dst_byte_identical_not_truncated(self):
        """01_GENERAL_REVIEW.md R4-04: `shutil.copy2` schrieb bisher DIREKT
        in `dst` -- ein I/O-Fehler WAEHREND des Kopierens konnte `dst`
        gekuerzt/teilweise ueberschrieben zuruecklassen. Hier wird die
        Staging-Quelldatei absichtlich GROESSER als die alte Zieldatei
        gemacht und `shutil.copy2` so gemockt, dass es einen Teil der
        neuen Bytes schreibt und DANN wirft -- mit dem Fix landet dieser
        Teilschreibvorgang in einer TEMP-Datei, `dst` bleibt unveraendert
        beim alten, vollstaendigen Inhalt."""
        old_content = "A" * 50 + "\n"
        staging_old = self._staging({"setup.json": "{}", "scripts/a.py": old_content})
        first = lu.adopt_staged_update(self.repo, staging_old, "rev-old")
        self.assertTrue(first.ok, first.message)  # a.py jetzt LEGITIM verwaltet (baseline_hash gesetzt)

        new_content = "B" * 500 + "\n"  # deutlich laenger als alt
        staging = self._staging({"setup.json": "{}", "scripts/a.py": new_content})

        real_copy2 = shutil.copy2

        def flaky_copy2(src, dst_arg, *a, **kw):
            # Schreibt absichtlich NUR einen Teil der neuen Bytes direkt in
            # das vom Aufrufer uebergebene Ziel (bei der R4-04-Fix-Version
            # ist das die TEMP-Datei, NICHT die echte Zieldatei) und wirft
            # danach -- simuliert einen Diskfehler mitten im Kopieren.
            if Path(src).name == "a.py":
                Path(dst_arg).write_text(new_content[:10])
                raise OSError("disk full (simulated, mid-copy)")
            return real_copy2(src, dst_arg, *a, **kw)

        with mock.patch.object(lu.shutil, "copy2", side_effect=flaky_copy2):
            result = lu.adopt_staged_update(self.repo, staging, "rev-new")
        self.assertFalse(result.ok)

        dst = self.repo / "scripts" / "a.py"
        self.assertEqual(
            dst.read_text(), old_content,
            "dst haette NACH einem Fehler mitten im Kopieren byteidentisch beim alten Inhalt bleiben muessen "
            "(kein Teilschreiben direkt ins Ziel)",
        )
        # Keine verwaiste Temp-Datei im Zielverzeichnis zurueckgelassen.
        leftovers = [p.name for p in (self.repo / "scripts").iterdir() if p.name != "a.py"]
        self.assertEqual(leftovers, [], f"verwaiste Temp-Datei(en) zurueckgelassen: {leftovers}")

    def test_interrupted_installation_resumed_against_a_DIFFERENT_newer_revision_is_not_misflagged(self):
        """01_GENERAL_REVIEW.md R4-04, zweiter Teil ('Zielbindung'): A ist
        regulaer verwaltet installiert. A->B wird NACH mindestens einer
        tatsaechlich kopierten Datei unterbrochen (target_rev=B bereits in
        den Zustand geschrieben, installed_rev bleibt A). Zwischen dem
        fehlgeschlagenen Lauf und dem naechsten Versuch hat sich die
        Fernquelle WEITER bewegt (C statt B) -- der naechste Aufruf
        installiert daher direkt C, NICHT B (exakt der reale Caller-Pfad
        in launcher.py:action_update, das bei jedem Aufruf die DANN
        aktuelle Fernrevision neu abfragt). Vorher wurde die bereits auf
        B gebrachte Teildatei gegen das ALTE Manifest (A) verglichen und
        faelschlich als fremde Abweichung geblockt."""
        staging_a = self._staging({"setup.json": "{}", "scripts/a.py": "A1\n", "scripts/b.py": "B1\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)

        staging_b = self._staging({"setup.json": "{}", "scripts/a.py": "A2\n", "scripts/b.py": "B2\n"})
        real_copy2 = shutil.copy2
        calls = {"n": 0}

        def flaky_copy2(src, dst_arg, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full (simulated)")
            return real_copy2(src, dst_arg, *a, **kw)

        with mock.patch.object(lu.shutil, "copy2", side_effect=flaky_copy2):
            interrupted = lu.adopt_staged_update(self.repo, staging_b, "rev-B")
        self.assertFalse(interrupted.ok)
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-A")
        self.assertEqual(lu.read_state(self.repo)["target_rev"], "rev-B")

        # Die Fernquelle hat sich WEITER bewegt: der naechste echte
        # action_update-Lauf installiert direkt C, nicht das abgebrochene B.
        staging_c = self._staging({"setup.json": "{}", "scripts/a.py": "A3\n", "scripts/b.py": "B3\n"})
        resumed_to_c = lu.adopt_staged_update(self.repo, staging_c, "rev-C")
        self.assertTrue(
            resumed_to_c.ok, f"haette NICHT als Abweichung geblockt werden duerfen: {resumed_to_c.message}",
        )
        self.assertEqual(resumed_to_c.deviated, [])
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], "rev-C")
        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A3\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B3\n")


# ── R4-05a: atomare, besitzgebundene Sperre ────────────────────────────────

def _acquire_lock_worker(repo_str: str, queue) -> None:
    from pathlib import Path as _Path  # frischer Import im Kindprozess (fork teilt zwar Speicher, explizit fuer Klarheit)
    err = lu.acquire_update_lock(_Path(repo_str))
    queue.put((os.getpid(), err))


class TestR405aAtomicOwnedLock(_AdoptFixtureBase):
    def test_two_real_processes_racing_for_a_fresh_lock_exactly_one_wins(self):
        """01_GENERAL_REVIEW.md R4-05a: vorher waren `exists()`/Lesen und
        das abschliessende `write_text()` GETRENNTE Schritte -- zwei
        Prozesse konnten beide die Sperre als frei sehen und beide
        anschliessend schreiben (TOCTOU). Echter Mehrprozess-Wettlauf
        (kein simulierter Singlethread-Ablauf): zwei UNABHAENGIGE
        Betriebssystemprozesse rufen `acquire_update_lock` auf DIESELBE,
        bisher nicht existierende Sperrdatei auf -- mit `O_CREAT|O_EXCL`
        gewinnt GENAU einer, der andere bekommt einen Fehlertext, NIEMALS
        beide Erfolg."""
        ctx = multiprocessing.get_context("fork")
        q = ctx.Queue()
        procs = [ctx.Process(target=_acquire_lock_worker, args=(str(self.repo), q)) for _ in range(2)]
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=10)
            self.assertEqual(p.exitcode, 0, "Kindprozess ist abgestuerzt/haengt")

        results = [q.get(timeout=5) for _ in range(2)]
        successes = [r for r in results if r[1] is None]
        failures = [r for r in results if r[1] is not None]
        self.assertEqual(len(successes), 1, f"genau EIN Prozess haette gewinnen muessen: {results}")
        self.assertEqual(len(failures), 1, f"genau EIN Prozess haette abgewiesen werden muessen: {results}")
        self.assertIn("läuft bereits", failures[0][1])
        # Die Sperrdatei zeigt am Ende die PID des GEWINNERS.
        held_pid = int(lu._lock_path(self.repo).read_text("utf-8").split()[0])
        self.assertEqual(held_pid, successes[0][0])

    def test_release_only_removes_own_lock_not_a_foreign_one(self):
        """01_GENERAL_REVIEW.md R4-05a: `release_update_lock` loeschte
        bisher OHNE Besitzervergleich -- ein Prozess, der (z. B. nach einer
        verwaisten Uebernahme durch einen ANDEREN, neu gestarteten Prozess)
        nicht mehr der tatsaechliche Besitzer ist, haette dessen aktive
        Sperre geloescht. Simuliert hier direkt: Sperrdatei zeigt eine
        FREMDE (lebende, PID 1) Sperre -- `release_update_lock` mit der
        EIGENEN PID darf diese NICHT entfernen."""
        lu._lock_path(self.repo).write_text(f"1 {lu._now_iso()}\n", encoding="utf-8")
        lu.release_update_lock(self.repo)
        self.assertTrue(lu._lock_path(self.repo).exists(), "fremde Sperre haette NICHT geloescht werden duerfen")

    def test_release_removes_a_lock_this_same_process_actually_holds(self):
        """Gegenprobe: die eigene, tatsaechlich selbst gehaltene Sperre
        bleibt normal loeschbar (keine Regression durch den Besitzercheck)."""
        err = lu.acquire_update_lock(self.repo)
        self.assertIsNone(err)
        self.assertTrue(lu._lock_path(self.repo).exists())
        lu.release_update_lock(self.repo)
        self.assertFalse(lu._lock_path(self.repo).exists())


# ── R4-05b/c: geschuetzte Loeschphase + ehrliches Manifest ─────────────────

class TestR405bProtectedDeletionPhase(_AdoptFixtureBase):
    def test_deletion_through_a_parent_symlink_swapped_in_after_management_is_refused(self):
        """01_GENERAL_REVIEW.md R4-05b: harmlose native Reproduktion --
        eine bisher verwaltete Datei faellt upstream weg; ihr Elternordner
        ist INZWISCHEN ein Symlink in ein externes Scratch-Verzeichnis mit
        gleich gehashtem Inhalt. `p.unlink()` ohne Schutzpruefung wuerde im
        externen Verzeichnis loeschen. Setup: `legacy/` ist beim ERSTEN
        Adopt noch ein echtes Verzeichnis (die Datei wird dadurch legitim
        verwaltet); ZWISCHEN den Laeufen wird es durch einen Symlink auf
        ein externes Scratch-Verzeichnis mit identischem Dateiinhalt
        ersetzt (keine echte Fremddatei, nur Scratch)."""
        staging_a = self._staging({"setup.json": "{}", "legacy/old_module.py": "OLD\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)
        self.assertIn("legacy/old_module.py", lu.read_state(self.repo)["managed_files"])

        outside = Path(tempfile.mkdtemp(dir=self.tmp, prefix="outside-scratch-"))
        (outside / "old_module.py").write_text("OLD\n", encoding="utf-8")  # identischer Hash wie im Manifest
        shutil.rmtree(self.repo / "legacy")
        (self.repo / "legacy").symlink_to(outside)

        staging_b = self._staging({"setup.json": "{}"})  # legacy/old_module.py entfaellt upstream
        second = lu.adopt_staged_update(self.repo, staging_b, "rev-B")

        self.assertTrue(second.ok, second.message)
        self.assertIn("legacy/old_module.py", second.deletion_skipped)
        self.assertTrue(
            (outside / "old_module.py").exists(),
            "Datei im externen Scratch-Verzeichnis haette NICHT ueber den Symlink geloescht werden duerfen",
        )
        # Bleibt bewusst als "weiterhin verwaltet" im Manifest stehen (kein falscher Loescherfolg).
        self.assertIn("legacy/old_module.py", lu.read_state(self.repo)["managed_files"])

    def test_already_missing_old_managed_file_is_cleared_from_manifest_without_being_counted_as_removed(self):
        """01_GENERAL_REVIEW.md R4-05c: eine bereits VOR dieser Uebernahme
        fehlende Altdatei (z. B. manuell geloescht) war nie 'soeben
        entfernt' -- sie wird aus dem Manifest genommen (sonst meldet ein
        spaeterer Lauf sie faelschlich als lokal abweichend/dirty), aber
        NICHT in der Erfolgsmeldung als 'entfernt' gezaehlt."""
        staging_a = self._staging({"setup.json": "{}", "scripts/gone.py": "G\n"})
        first = lu.adopt_staged_update(self.repo, staging_a, "rev-A")
        self.assertTrue(first.ok, first.message)
        self.assertIn("scripts/gone.py", lu.read_state(self.repo)["managed_files"])

        (self.repo / "scripts" / "gone.py").unlink()  # manuell/extern entfernt, NICHT durch diesen Lauf

        staging_b = self._staging({"setup.json": "{}"})  # entfaellt auch upstream
        second = lu.adopt_staged_update(self.repo, staging_b, "rev-B")

        self.assertTrue(second.ok, second.message)
        self.assertNotIn("scripts/gone.py", lu.read_state(self.repo)["managed_files"])
        self.assertNotIn(
            "entfernt", second.message,
            f"eine bereits fehlende Datei darf nicht als von DIESEM Lauf 'entfernt' gemeldet werden: {second.message}",
        )


if __name__ == "__main__":
    unittest.main()
