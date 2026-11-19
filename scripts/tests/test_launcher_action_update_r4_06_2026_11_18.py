#!/usr/bin/env python3
"""scripts/tests/test_launcher_action_update_r4_06_2026_11_18.py — R4-06
Regression (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r4,
01_GENERAL_REVIEW.md R4-06, 02_NACHZUG_AUFTRAG.md Block D).

01_GENERAL_REVIEW.md R4-06: die Sperrmeldung verspricht "[4] erneut
ausführen, um neu zu starten", aber `action_update()` fragte bei JEDEM
Aufruf zuerst frisch `check_for_update()` ab -- meldete das (GENAU WEIL
die vorherige Installation schon erfolgreich war) 'current' (ohne/mit
offenem Sync), kehrte die Funktion VORHER zurück, OHNE je wieder einen
Neustart anzubieten. Der bestehende Test `test_update_menu_entry_itself_
stays_reachable_when_blocked` (scripts/tests/test_launcher_action_update.py)
bestätigt nur, dass die Zeichenfolge '4' nicht in einem statischen Tupel
("1","l","2","3","m") steht -- er führt den echten Nutzerweg NIE aus.

Treibt den ECHTEN Aufrufer `scripts.launcher.action_update()` an (nicht
die Helfer in `launcher_update.py` direkt), identischer Harness-Stil zu
`test_launcher_action_update.py` (dessen `ActionUpdateTestCase`/
`_ScriptedPrompt` hier wiederverwendet werden)."""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_sys_path_before_launcher_import = list(sys.path)
from scripts import launcher as L  # noqa: E402
from scripts import launcher_update as lu  # noqa: E402
for _p in list(sys.path):
    if _p not in _sys_path_before_launcher_import:
        sys.path.remove(_p)

from scripts.tests.test_launcher_action_update import ActionUpdateTestCase, _ScriptedPrompt  # noqa: E402
from scripts.tests.test_launcher_update import _init_git_repo  # noqa: E402


class TestR406PendingRestartTakesPriorityOverFreshCheck(ActionUpdateTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "install"
        # Ein normales Git-Checkout, das check_for_update() ohne weiteres
        # Mocking als "current" melden WUERDE, falls es ueberhaupt
        # aufgerufen wird -- das ist hier bewusst der realistischste Fall
        # fuer R4-06 (GENAU der Zustand nach einer bereits erfolgreichen,
        # aber noch nicht neu gestarteten Installation).
        _init_git_repo(self.repo, {"setup.json": "{}\n"})
        self._set_repo(self.repo)

    def _start(self, patcher):
        """Wie `self._patch`, liefert aber den gestarteten Mock selbst
        (die Basisklasse gibt den `_patch`-Objekt zurueck, nicht den
        Rueckgabewert von `.start()`)."""
        mock_obj = patcher.start()
        self._patches.append(patcher)
        return mock_obj

    def _block_check_for_update(self):
        """check_for_update() darf in keinem der Faelle unten tatsaechlich
        aufgerufen werden -- ein pendender Neustart hat Vorrang vor jedem
        neuen Quellcheck. Wirft laut, statt stillschweigend eine Netzanfrage
        zu versuchen."""
        return self._patch(mock.patch.object(
            L.launcher_update_module, "check_for_update",
            mock.Mock(side_effect=AssertionError(
                "check_for_update() haette bei pendendem Neustart NICHT aufgerufen werden duerfen (R4-06)"
            )),
        ))

    def test_pending_restart_is_offered_immediately_without_a_fresh_source_check(self):
        """Kernfall: `_update_restart_required` steht bereits (voriger
        Aufruf, Neustart abgelehnt) -- [4] bietet SOFORT den Neustart an,
        OHNE vorher check_for_update() zu rufen, UND fuehrt ihn bei
        Zustimmung tatsaechlich aus."""
        self._patch(mock.patch.object(L, "_update_restart_required", True))
        self._block_check_for_update()
        restart_mock = self._start(mock.patch.object(L.launcher_update_module, "restart_launcher"))
        prompt = self._set_prompt(["j"])  # "Jetzt neu starten?"

        L.action_update()

        restart_mock.assert_called_once_with(self.repo)
        self.assertEqual(len(prompt.calls), 1)
        self.assertIn("neu starten", prompt.calls[0].lower())

    def test_declining_the_pending_restart_again_keeps_the_block_active(self):
        """Lehnt der Nutzer den angebotenen Neustart erneut ab, bleibt die
        Sperre (und damit `_update_restart_required`) aktiv -- kein
        stilles Zuruecksetzen, kein echter Prozesswechsel."""
        self._patch(mock.patch.object(L, "_update_restart_required", True))
        self._block_check_for_update()
        restart_mock = self._start(mock.patch.object(L.launcher_update_module, "restart_launcher"))
        self._set_prompt(["n"])

        L.action_update()

        restart_mock.assert_not_called()
        self.assertTrue(L._update_restart_required)
        # Produktive Aktionen bleiben ueber denselben Mechanismus gesperrt.
        self.assertTrue(L._block_if_restart_required("[1]"))

    def test_without_a_pending_restart_the_normal_fresh_check_still_runs(self):
        """Gegenprobe: OHNE ausstehende Neustartpflicht laeuft der normale
        `check_for_update()`-Weg unveraendert (kein Ueberspringen des
        Checks als Nebenwirkung des Fixes)."""
        self._patch(mock.patch.object(L, "_update_restart_required", False))
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            L.action_update()  # kein Prompt vorbereitet -> wuerde bei vorzeitigem Prompt-Aufruf werfen
        out = buf.getvalue()
        self.assertIn("Installierter Stand", out)  # Beleg: der normale Check-Pfad lief tatsaechlich


if __name__ == "__main__":
    unittest.main()
