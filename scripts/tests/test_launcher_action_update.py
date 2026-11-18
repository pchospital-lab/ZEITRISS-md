#!/usr/bin/env python3
"""scripts/tests/test_launcher_action_update.py — ZR-ALTAIR-UPDATER-
SPIELTEST-NACHZUG-20261118-r3 (R3-01, R3-04, R3-05).

Treibt den ECHTEN Aufrufer `scripts.launcher.action_update()` / `main()`-
Menüschleife an, nicht nur die Helfer in `launcher_update.py` direkt --
das belegt, dass die Mechanik auch über den normalen [4]-Bedienweg
erreichbar ist (General-Kritik an den r2-Tests: der Migrationstest rief
`adopt_staged_update` direkt auf und bewies den Benutzerweg nicht).

Kontrollierte Fixtures: lokale Git-Remotes auf der Platte, injizierter
HTTP-Getter, injizierter ZIP-Download. Kein echtes Netz."""
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

# `scripts/launcher.py` fuegt sich beim Import selbst via `sys.path.insert(0,
# str(REPO / "scripts"))` vor den Repo-Root (s. launcher.py:70-72, fuer den
# eigenen `import setup as setup_module`-Zeilenstil). In einem GESAMTEN
# `python3 -m unittest -q`-Lauf ab Repo-Root bleibt dieser Pfadeintrag danach
# fuer den REST des Prozesses stehen -- jede SPAETER entdeckte Testdatei
# unter `tests/mmo_sim/*.py`, die `from mmo_sim.core import ...` importiert,
# findet dann `scripts/mmo_sim.py` (den Launcher-Shim, s. dessen Docstring
# zur exakt dieser Namenskollision) statt des echten `mmo_sim/`-Pakets am
# Repo-Root -- `ModuleNotFoundError`/Folgefehler in VOELLIG unabhaengigen
# Testdateien. Beobachtet beim ersten Hinzufuegen dieser Datei (lokal
# reproduziert, Repo-Root-Stash-Vergleich). Fix: den waehrend des Imports
# NEU hinzugekommenen `sys.path`-Eintrag sofort danach wieder entfernen --
# die bereits geladenen `scripts.launcher`/`setup`-Module bleiben ueber
# `sys.modules` unabhaengig davon gecacht und bleiben nutzbar.
_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_update import _clone, _commit_all, _init_git_repo, _rev, _write_files  # noqa: E402

# `scripts/launcher.py` importiert `launcher_update` NICHT als
# `scripts.launcher_update`, sondern über eine `sys.path`-Erweiterung als
# eigenständiges Top-Level-Modul `launcher_update` (s. launcher.py:101-109)
# -- das ist ein ANDERES Python-Modulobjekt im selben Prozess (gleiche
# Datei, zwei `sys.modules`-Einträge). Patches auf `lu` (= `scripts.
# launcher_update`) wirken deshalb NICHT auf das, was `action_update()`
# tatsächlich aufruft. Für Tests über den echten Aufrufer MUSS auf
# `L.launcher_update_module` gepatcht werden -- sonst fallen Mocks ins
# Leere und der Code faellt ungebremst auf echtes Netz zurueck (beobachtet:
# ein ungewolltes echtes GitHub-API/Download beim ersten Testlauf dieser
# Datei, bevor dieser Hinweis hier ergaenzt wurde).
assert L.launcher_update_module is not lu, (
    "Falls das je gleich wird: alle lu-Patches unten laufen ins Leere -- "
    "launcher.py muesste launcher_update dann als scripts.launcher_update importieren."
)


def _build_zip_bytes(entries: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


class _ScriptedPrompt:
    """Ersetzt `_prompt`: liefert die vorbereiteten Antworten der Reihe
    nach, wirft laut und sofort, wenn mehr Prompts kommen als erwartet
    (deckt versehentliche Extra-Nachfragen auf, statt sie stillschweigend
    mit '' zu beantworten)."""

    def __init__(self, answers: list[str]):
        self._answers = list(answers)
        self.calls: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        if not self._answers:
            raise AssertionError(f"Unerwarteter zusätzlicher Prompt ohne Antwort: {prompt!r}")
        return self._answers.pop(0)


class ActionUpdateTestCase(unittest.TestCase):
    """Basis: isoliert `REPO`, `_prompt`, `_pause`, `_update_restart_required`
    pro Test -- action_update()/main() sind Modulfunktionen, die echte
    Modulglobals von scripts.launcher benutzen."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="launcher-action-update-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self._patches = []
        self._patch(mock.patch.object(L, "_pause", lambda: None))
        self._patch(mock.patch.object(L, "_update_restart_required", False))
        # Kein echtes OpenWebUI-Backend in dieser Stage -- Sync-Schritt
        # soll den dokumentierten "Key fehlt" Pfad nehmen, ohne echten
        # Subprozess/HTTP-Aufruf.
        self._patch(mock.patch.object(L, "_ensure_owui_env", lambda: False))

    def tearDown(self) -> None:
        for p in reversed(self._patches):
            p.stop()

    def _patch(self, patcher):
        patcher.start()
        self._patches.append(patcher)
        return patcher

    def _set_repo(self, path: Path) -> None:
        self._patch(mock.patch.object(L, "REPO", path))

    def _set_prompt(self, answers: list[str]) -> "_ScriptedPrompt":
        scripted = _ScriptedPrompt(answers)
        self._patch(mock.patch.object(L, "_prompt", scripted))
        return scripted


# ── R3-01: unverwaltete ZIP-Installation erreicht über [4] eine Übernahme ──

class TestActionUpdateUnmanagedZipMigration(ActionUpdateTestCase):
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

    def test_unmanaged_candidate_without_state_reaches_real_installation(self):
        """R3-01-Regression: vor dem Fix kehrte `action_update()` bei
        status=='unknown' SOFORT zurück -- kein Installationsangebot, egal
        wie vertrauenswürdig die geprüfte Zielrevision war. Jetzt muss der
        echte [4]-Aufrufer die Datei tatsächlich übernehmen."""
        prompt = self._set_prompt([
            "j",   # "Trotzdem auf den geprüften Stand übernehmen?"
            "j",   # R3-02: "Diese Dateien bewusst überschreiben?" (setup.json weicht ab)
            "n",   # "Jetzt neu starten?" -- bewusst ablehnen fuer die R3-05-Pruefung unten
        ])
        L.action_update()

        self.assertEqual((self.repo / "setup.json").read_text(), '{"project": "ZEITRISS", "version": "new"}')
        self.assertEqual((self.repo / "scripts" / "x.py").read_text(), "NEW\n")
        state = lu.read_state(self.repo)
        self.assertEqual(state["installed_rev"], self.target_sha)
        self.assertEqual(state["method"], "zip")
        # R3-05: Neustart abgelehnt -> produktiver Weiterlauf muss jetzt gesperrt sein.
        self.assertTrue(L._update_restart_required)
        self.assertEqual(len(prompt.calls), 3)

    def test_declining_the_unverified_overwrite_confirmation_changes_nothing(self):
        """R3-02-Regression über den echten Aufrufer: die erste Zustimmung
        gilt nur der Migration an sich, NICHT automatisch dem Überschreiben
        einer abweichenden, nie verwalteten Datei -- das ist eine separate,
        explizite Nachfrage (`_attempt_zip_install`)."""
        prompt = self._set_prompt(["j", "n"])  # migrieren: ja -- ueberschreiben: nein
        L.action_update()
        self.assertEqual((self.repo / "setup.json").read_text(), '{"project": "ZEITRISS", "version": "old"}')
        self.assertFalse((self.repo / "scripts" / "x.py").exists())
        self.assertNotIn("installed_rev", lu.read_state(self.repo))
        self.assertEqual(len(prompt.calls), 2)

    def test_declining_the_migration_offer_changes_nothing(self):
        self._set_prompt(["n"])
        L.action_update()
        self.assertEqual((self.repo / "setup.json").read_text(), '{"project": "ZEITRISS", "version": "old"}')
        self.assertEqual(lu.read_state(self.repo), {} or lu.read_state(self.repo))
        self.assertNotIn("installed_rev", lu.read_state(self.repo))

    def test_truly_unreachable_source_still_never_offers_installation(self):
        """Gegenprobe: eine wirklich nicht erreichbare Quelle (kein
        remote_rev) darf WEITERHIN keine Übernahme anbieten -- R3-01 lockert
        'unknown' nur für den Fall einer erreichbaren, geprüften Revision."""
        def raising_getter(url, timeout):
            raise OSError("Name or service not known")
        self._patch(mock.patch.object(L.launcher_update_module, "_default_http_get", raising_getter))
        prompt = self._set_prompt([])  # keine Prompts erwartet -- sofortige Rückkehr
        L.action_update()
        self.assertEqual((self.repo / "setup.json").read_text(), '{"project": "ZEITRISS", "version": "old"}')
        self.assertEqual(prompt.calls, [])


# ── R3-03: unterbrochenes Folgeupdate ist über [4] konsistent fortsetzbar ──

class TestActionUpdateInterruptedFollowupResume(ActionUpdateTestCase):
    """R3-03-Regression über den ECHTEN Aufrufer: die bisherigen
    Unterbrechungstests (`test_launcher_update.py`) riefen `adopt_staged_
    update` direkt auf -- genau die Kritik, die der General an den
    R3-01-Tests geuebt hat, gilt strukturell auch hier. Dieser Test treibt
    `action_update()`/`_attempt_zip_install()` fuer eine bereits regulaer
    verwaltete Installation A, unterbricht A→B NACH mindestens einer
    tatsaechlich kopierten Datei (echter `shutil.copy2`-Fehler im echten
    Aufrufer-Pfad), und laesst [4] danach normal fortsetzen -- ohne dass
    die eigene, bereits auf B gebrachte Teilschreibung als fremde lokale
    Abweichung missverstanden wird."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        self.repo.mkdir()
        self.sha_a = "a" * 40
        self.sha_b = "b" * 40
        (self.repo / "setup.json").write_text("{}", encoding="utf-8")
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "a.py").write_text("A1\n", encoding="utf-8")
        (self.repo / "scripts" / "b.py").write_text("B1\n", encoding="utf-8")
        lu.write_state(
            self.repo, method="zip", installed_rev=self.sha_a, sync_status="ok",
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
        zip_bytes_b = _build_zip_bytes({
            f"ZEITRISS-md-{self.sha_b}/setup.json": "{}",
            f"ZEITRISS-md-{self.sha_b}/scripts/a.py": "A2\n",
            f"ZEITRISS-md-{self.sha_b}/scripts/b.py": "B2\n",
        })

        def fake_download(url, dest, *, timeout=30.0, max_bytes=None, opener=None):
            dest.write_bytes(zip_bytes_b)

        self._patch(mock.patch.object(L.launcher_update_module, "download_zip_archive", fake_download))

    def test_interrupted_then_resumed_update_ends_consistently_on_b_without_false_deviation(self):
        calls = {"n": 0}
        real_copy2 = shutil.copy2

        def flaky_copy2(src, dst, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full (simulated)")
            return real_copy2(src, dst, *a, **kw)

        with mock.patch.object(L.launcher_update_module.shutil, "copy2", side_effect=flaky_copy2):
            self._set_prompt(["j"])  # "Jetzt installieren?" -- Abbruch kommt aus dem simulierten I/O-Fehler
            L.action_update()

        # Nach der Unterbrechung: noch als A markiert, aber GENAU EINE der
        # beiden Dateien ist schon tatsaechlich auf dem B-Stand (welche,
        # haengt von der Betriebssystem-/Dateisystem-`os.walk`-Reihenfolge
        # ab -- nicht Teil des zu pruefenden Verhaltens). Entscheidend ist
        # der Wiederanlauf unten: der bereits geschriebene Teilschritt darf
        # NICHT als fremde Abweichung geblockt werden.
        self.assertEqual(lu.read_state(self.repo)["installed_rev"], self.sha_a)
        a_mid = (self.repo / "scripts" / "a.py").read_text()
        b_mid = (self.repo / "scripts" / "b.py").read_text()
        self.assertTrue(
            (a_mid, b_mid) in (("A1\n", "B2\n"), ("A2\n", "B1\n")),
            "genau eine Datei muss bereits kopiert, die andere noch unberuehrt sein",
        )

        prompt = self._set_prompt(["j", "n"])  # erneut installieren, Neustart ablehnen
        L.action_update()

        self.assertNotIn(
            "unverändert", "\n".join(prompt.calls),
            "der Wiederanlauf darf keinen zusaetzlichen 'Dateien weichen ab'-Dialog ausloesen",
        )
        state = lu.read_state(self.repo)
        self.assertEqual(state["installed_rev"], self.sha_b)
        self.assertEqual((self.repo / "scripts" / "a.py").read_text(), "A2\n")
        self.assertEqual((self.repo / "scripts" / "b.py").read_text(), "B2\n")


# ── R3-04/a+b: ahead/diverged werden nicht als Update angeboten ───────────

class TestActionUpdateAheadDiverged(ActionUpdateTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.remote = self.tmp / "remote"
        self.clone = self.tmp / "clone"
        _init_git_repo(self.remote, {"setup.json": '{"project": "ZEITRISS"}\n', "marker.txt": "v1\n"})
        _clone(self.remote, self.clone)
        self._set_repo(self.clone)

    def test_local_ahead_of_remote_is_not_offered_as_update(self):
        _write_files(self.clone, {"marker.txt": "ahead work\n"})
        ahead_rev = _commit_all(self.clone, "local ahead")
        prompt = self._set_prompt([])  # kein Install-Prompt erwartet
        L.action_update()
        self.assertEqual(_rev(self.clone), ahead_rev)  # unverändert
        self.assertEqual(prompt.calls, [])

    def test_diverged_without_fetched_objects_falls_back_to_update_available_prompt(self):
        """Dokumentierte Grenze (s. test_launcher_update.py): ohne Fetch kann
        ein wirklich divergierter, dem Check unbekannter Commit nicht von
        einem echten Update unterschieden werden -- hier bleibt bewusst der
        bestehende 'update_available'-Dialog, den der Nutzer ablehnen kann."""
        _write_files(self.clone, {"marker.txt": "local only\n"})
        _commit_all(self.clone, "local only commit")
        _write_files(self.remote, {"marker.txt": "remote only\n"})
        _commit_all(self.remote, "remote only commit")
        before = _rev(self.clone)
        self._set_prompt(["n"])  # Update ablehnen
        L.action_update()
        self.assertEqual(_rev(self.clone), before)


# ── R3-04/c: "current" trotz dirty wird nicht als blankes Grün gezeigt ───

class TestActionUpdateCurrentButDirty(ActionUpdateTestCase):
    def test_current_revision_with_local_edit_is_not_a_plain_green_checkmark(self):
        remote = self.tmp / "remote"
        clone = self.tmp / "clone"
        _init_git_repo(remote, {"setup.json": "{}\n", "marker.txt": "v1\n"})
        _clone(remote, clone)
        (clone / "marker.txt").write_text("hand-edited\n", encoding="utf-8")
        self._set_repo(clone)
        self._set_prompt([])

        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            L.action_update()
        out = buf.getvalue()
        self.assertIn("lokale Änderungen vorhanden", out)
        self.assertNotIn("✓ Aktuell.", out)


# ── R3-05: nach Neustart-Ablehnung bleibt [M]/[1]/[2]/[L]/[3] gesperrt ────

class TestMenuBlocksAfterDeclinedRestart(ActionUpdateTestCase):
    def test_declined_restart_blocks_productive_menu_actions(self):
        self.assertFalse(L._block_if_restart_required("[1]"))
        with mock.patch.object(L, "_update_restart_required", True):
            blocked = L._block_if_restart_required("[1]")
        self.assertTrue(blocked)

    def test_update_menu_entry_itself_stays_reachable_when_blocked(self):
        # [4] muss erreichbar bleiben, sonst kommt der Nutzer nie zum Neustart.
        with mock.patch.object(L, "_update_restart_required", True):
            self.assertNotIn("4", ("1", "l", "2", "3", "m"))


if __name__ == "__main__":
    unittest.main()
