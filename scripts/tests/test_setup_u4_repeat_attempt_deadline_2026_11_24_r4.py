#!/usr/bin/env python3
"""scripts/tests/test_setup_u4_repeat_attempt_deadline_2026_11_24_r4.py --
ZR-PR3317-RESTNACHZUG-20261124-r4, U4-Restnachzug ("Rest U4").

Ursache (verifiziert am echten Code VOR diesem Fix, s. r3-Test fuer den
vorherigen U4-Nachzug): der r3-Fix reicht den aeusseren Rest nur EINMAL pro
Caller-Aufruf bis zum jeweils EINEN HTTP-Request durch. ZWEI Luecken blieben
offen, weil beide Funktionen INNERHALB EINER EIGENEN Schleife mehrere
Requests ausloesen koennen, ohne den Rest zwischen den eigenen Versuchen neu
zu berechnen:

  A) `APIClient.do_upload_file` (vormals setup.py ~859-887): die
     Retry-Schleife reichte `outer_remaining_s` UNVERAENDERT an JEDEN
     `upload_file`-Versuch weiter (kein Abzug der bereits verstrichenen
     Request-/Backoffzeit) -- ein 2. Versuch nach einem 8s-Fehlversuch +
     2s-Backoff bekam dadurch wieder den VOLLEN aeusseren Rahmen (16s) statt
     des tatsaechlich noch verbleibenden Rests (6s). Backoffs (2s/4s) wurden
     ebenfalls nicht auf den Rest gedeckelt.

  B) `wait_for_file_ready` (vormals setup.py ~1128-1229): JEDE Iteration
     reichte das KONSTANTE `deadline_s` unveraendert als `outer_remaining_s`
     an `get_file` weiter -- die Restpruefung (`elapsed >= deadline_s`)
     passierte erst NACH dem GET, und das volle Pollintervall wurde danach
     ungedeckelt geschlafen. Ein zweiter GET nach einer bereits weit
     verstrichenen Phase bekam dadurch denselben (laengst nicht mehr
     zutreffenden) Timeout-Deckel wie der erste.

Fix (dieser Nachzug): beide Schleifen berechnen den noch verbleibenden Rest
jetzt VOR jedem eigenen Request/Backoff frisch (`outer_remaining_s -
(jetzt - start)` bzw. `deadline_s - (jetzt - start)`); ist der Rest bereits
<= 0, wird kontrolliert abgebrochen (kein weiterer Request/Backoff mit
falschem/vollem Budget). Nur wenn `outer_remaining_s`/`deadline_s`
tatsaechlich gesetzt sind -- der None-Pfad (A) bzw. das uebrige
Zustandsmodell (B) bleibt unveraendert.

Testebene -- identische Grenze wie der vorherige r3-Test (`test_setup_u4_
outer_deadline_http_timeout_2026_11_24_r3.py`): ECHTER `APIClient`/
`_request`-Pfad, NUR `urllib.request.urlopen` ist ein lokaler Antwort-Double.
Zusaetzlich eine SYNTHETISCHE UHR (fuer A: `setup_mod.time` komplett durch
ein Fake ersetzt, da `do_upload_file` kein injizierbares `now_fn`/`sleep_fn`
hat; fuer B: die bereits vorhandenen `now_fn`/`sleep_fn`-Parameter von
`wait_for_file_ready`) -- kein echtes Warten, kein echter Netzwerk-Call.
Geprueft wird der tatsaechlich an `urlopen` uebergebene `timeout`-Parameter
je Versuch/GET."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
import unittest.mock as mock
import urllib.error
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

# Dieselbe dokumentierte Konvention wie test_setup_u4_outer_deadline_http_
# timeout_2026_11_24_r3.py / test_setup_upd1_readiness_2026_11_23.py:
# `scripts/setup.py` fuegt sich beim Laden selbst vor den Repo-Root in
# sys.path ein -- den neu hinzugekommenen Pfadeintrag sofort nach dem Laden
# wieder entfernen, sonst findet ein SPAETER in DEMSELBEN Prozess entdecktes
# `import tests.mmo_sim` faelschlich `scripts/tests` statt des echten
# Top-Level-`tests/`-Pakets.
_sys_path_before_setup_exec = list(sys.path)
_spec = importlib.util.spec_from_file_location(
    "u4_r4_repeat_attempt_deadline_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)
for _p in list(sys.path):
    if _p not in _sys_path_before_setup_exec:
        sys.path.remove(_p)


class _ImmediateResponse:
    """`urlopen`-Context-Manager-Double -- identisches Muster wie im r3-Test
    (`repro/update_r4_witness.py`s `Response`)."""

    status = 200

    def __init__(self, payload):
        self.payload = payload
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


class _FakeClock:
    """Ersatz fuer das komplette `time`-Modul, wie es `setup.py` unter dem
    Namen `time` importiert -- NUR innerhalb von `do_upload_file` noetig
    (kein eigenes `now_fn`/`sleep_fn` dort). `monotonic()`/`sleep()` bilden
    eine EINZIGE gemeinsame synthetische Uhr; `time()` (Boundary-Hash in
    `upload_file`) ist reiner Passthrough auf dieselbe Uhr, ihr Wert ist
    funktional irrelevant."""

    def __init__(self):
        self.t = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.t

    def time(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("sleep length must be non-negative")
        self.sleeps.append(seconds)
        self.t += seconds

    def advance(self, dt: float) -> None:
        self.t += dt


class TestUploadRetryDeadlineShrinksEachAttempt(unittest.TestCase):
    """Fix A -- `APIClient.do_upload_file`: der Rest wird vor JEDEM Versuch
    (und vor jedem Backoff) frisch berechnet, statt unveraendert durchgereicht
    zu werden."""

    def _client(self):
        return setup_mod.APIClient("https://fixture.invalid", "SYNTHETIC-ONLY")

    def _upload_fixture(self):
        self._tmp_ctx = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_ctx.cleanup)
        fp = Path(self._tmp_ctx.name) / "a.md"
        fp.write_bytes(b"INHALT")
        return fp

    def test_second_attempt_gets_shrunk_remainder_not_full_outer_frame(self):
        """Witness-Trace (Briefing): aeusserer Rahmen 16s, 1. Fehler nach 8s,
        Backoff 2s (gedeckelt auf den Rest 16-8=8 -> bleibt 2s) -> Versuch2
        startet bei t=10 mit Rest 6 -> bekommt timeout=6 (NICHT mehr 16).
        Versuch2 verbraucht den kompletten Rest (6s) -> Rest vor dem naechsten
        Backoff ist 0 -> `return None`, KEIN Versuch3."""
        clock = _FakeClock()
        fp = self._upload_fixture()
        calls: list[dict] = []
        # Env-Hygiene (wie test_without_outer_deadline_default_path_is_unchanged
        # und der r3-Test): OWUI_UPLOAD_TIMEOUT entfernen, damit der Default 120
        # greift und die 16.0-/6.0-Assertions nicht von einer zufaellig im
        # Prozess gesetzten, kleineren Env-Var verfaelscht werden.
        saved_env = os.environ.pop("OWUI_UPLOAD_TIMEOUT", None)
        self.addCleanup(lambda: saved_env is not None and os.environ.__setitem__("OWUI_UPLOAD_TIMEOUT", saved_env))

        def fake_urlopen(request, *, timeout, context):
            calls.append({"method": request.get_method(), "timeout_s": timeout})
            if len(calls) == 1:
                clock.advance(8.0)
                raise urllib.error.URLError("synthetic-transient-1")
            if len(calls) == 2:
                clock.advance(6.0)
                raise urllib.error.URLError("synthetic-transient-2")
            raise AssertionError(f"unerwarteter dritter Request: {calls}")

        client = self._client()
        with mock.patch.object(setup_mod, "time", clock), \
             mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.do_upload_file(fp, outer_remaining_s=16.0)

        self.assertIsNone(result, "beide Versuche scheitern -> None, kein Crash")
        self.assertEqual(len(calls), 2, calls)
        self.assertEqual(calls[0]["timeout_s"], 16.0, "Versuch1: min(120, Rest 16) = 16")
        self.assertEqual(
            calls[1]["timeout_s"], 6.0,
            "Versuch2: Rest = 16 - 8(Versuch1) - 2(Backoff) = 6, NICHT erneut 16",
        )
        self.assertEqual(
            clock.sleeps, [2.0],
            "genau EIN Backoff (2s, Rest 16-8=8 -> min(2,8)=2); kein zweiter "
            "Backoff, da der Rest nach Versuch2 (6-6=0) bereits erschoepft ist",
        )

    def test_without_outer_deadline_default_path_is_unchanged(self):
        """Gegenfall (Abnahme U4): ohne `outer_remaining_s` (None) bleibt der
        Default-Pfad EXAKT unveraendert -- volle `retries`-Anzahl (3
        Versuche), Backoff 2s/4s, kein Timeout-Deckel (`None` an
        `upload_file`, also der konfigurierte 120s-Upload-Default an
        `urlopen`)."""
        clock = _FakeClock()
        fp = self._upload_fixture()
        calls: list[dict] = []

        def fake_urlopen(request, *, timeout, context):
            calls.append({"method": request.get_method(), "timeout_s": timeout})
            raise urllib.error.URLError("synthetic-always-fails")

        client = self._client()
        saved_env = os.environ.pop("OWUI_UPLOAD_TIMEOUT", None)
        self.addCleanup(lambda: saved_env is not None and os.environ.__setitem__("OWUI_UPLOAD_TIMEOUT", saved_env))
        with mock.patch.object(setup_mod, "time", clock), \
             mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = client.do_upload_file(fp, outer_remaining_s=None)

        self.assertIsNone(result)
        self.assertEqual(len(calls), 3, "retries=2 -> 3 Versuche gesamt, unveraendert")
        self.assertEqual([c["timeout_s"] for c in calls], [120.0, 120.0, 120.0])
        self.assertEqual(clock.sleeps, [2.0, 4.0], "Backoff 2s/4s bleibt unveraendert")


class TestReadinessPollDeadlineShrinksEachGet(unittest.TestCase):
    """Fix B -- `wait_for_file_ready`: vor JEDEM GET wird der Rest aus
    `deadline_s`/`start`/`now_fn` frisch berechnet, statt das konstante
    `deadline_s` unveraendert durchzureichen. ECHTER `APIClient.get_file`
    (clamped auf `min(self.timeout, outer_remaining_s)`) -> `_request` ->
    `urlopen`-Double; `now_fn`/`sleep_fn` sind die bereits vorhandenen
    Injektionspunkte der Funktion (keine Modul-Patch-Notwendigkeit hier)."""

    def _http_and_client(self):
        http = setup_mod.APIClient("https://fixture.invalid", "SYNTHETIC-ONLY")

        class _Backend:
            def get_file(self, file_id, *, outer_remaining_s=None):
                return http.get_file(file_id, outer_remaining_s=outer_remaining_s)

        return http, _Backend()

    def test_exhausted_phase_blocks_second_get_and_returns_pending_deadline(self):
        """Witness-Trace (Briefing): Readiness-Phase `deadline_s`=31s, GET1
        bekommt Rest 31 -> timeout min(30,31)=30, braucht (synthetisch) die
        vollen 30s und liefert `pending`. Rest vor der Pause = 31-30=1 ->
        Pause auf 1s gedeckelt (nicht das volle Pollintervall 3s) -> t=31.
        Naechster Eintritt: Rest = 31-31 = 0 -> KEIN GET2, `pending_deadline`
        (`attempts` bleibt bei 1 -- der nicht ausgefuehrte GET zaehlt nicht)."""
        clock = _FakeClock()
        http, client = self._http_and_client()
        calls: list[dict] = []

        def fake_urlopen(request, *, timeout, context):
            calls.append({"timeout_s": timeout})
            clock.advance(30.0)
            return _ImmediateResponse({"id": "f1", "data": {"status": "processing"}})

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            r = setup_mod.wait_for_file_ready(
                client, "f1", deadline_s=31.0, poll_interval_s=3.0,
                sleep_fn=clock.sleep, now_fn=clock.monotonic,
            )

        self.assertEqual(len(calls), 1, "KEIN zweiter GET -- die Phase ist nach der Pause erschoepft")
        self.assertEqual(calls[0]["timeout_s"], 30.0, "GET1: min(30, Rest 31) = 30")
        self.assertEqual(clock.sleeps, [1.0], "Pause gedeckelt auf Rest (31-30=1), NICHT volle 3s")
        self.assertFalse(r.ready)
        self.assertEqual(r.status, "pending_deadline")
        self.assertEqual(r.attempts, 1, "nicht ausgefuehrter GET2 zaehlt NICHT als Versuch")
        self.assertAlmostEqual(r.elapsed_s, 31.0)

    def test_positive_remainder_passes_shrunk_value_to_second_get(self):
        """Gegenfall mit noch positivem Rest nach der ersten Runde: GET2
        bekommt den GESCHRUMPFTEN Rest (17), nicht erneut den vollen
        `deadline_s` (40) -- UND nicht den vollen regulaeren 30s-Default."""
        clock = _FakeClock()
        http, client = self._http_and_client()
        calls: list[dict] = []

        def fake_urlopen(request, *, timeout, context):
            calls.append({"timeout_s": timeout})
            if len(calls) == 1:
                clock.advance(20.0)
                return _ImmediateResponse({"id": "f1", "data": {"status": "processing"}})
            clock.advance(1.0)
            return _ImmediateResponse(
                {"id": "f1", "data": {"status": "completed", "content": "fertig"}}
            )

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            r = setup_mod.wait_for_file_ready(
                client, "f1", deadline_s=40.0, poll_interval_s=3.0,
                sleep_fn=clock.sleep, now_fn=clock.monotonic,
            )

        self.assertEqual(len(calls), 2, calls)
        self.assertEqual(calls[0]["timeout_s"], 30.0, "GET1: min(30, Rest 40) = 30 (regulaerer Default greift)")
        self.assertEqual(
            calls[1]["timeout_s"], 17.0,
            "GET2: Rest = 40 - 20(GET1) - 3(Pause) = 17, NICHT erneut 40 und NICHT der 30s-Default",
        )
        self.assertTrue(r.ready, r)
        self.assertEqual(r.status, "ready")
        self.assertEqual(r.attempts, 2)


if __name__ == "__main__":
    unittest.main()
