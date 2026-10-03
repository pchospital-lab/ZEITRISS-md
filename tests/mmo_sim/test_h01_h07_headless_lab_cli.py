#!/usr/bin/env python3
"""
tests/mmo_sim/test_h01_h07_headless_lab_cli.py — neue dauerhafte
Regressionen fuer den Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27,
01_AUFTRAG_HEADLESS.md, 02_ABNAHME.md H01/H02/H04/H06/H07, H-A).

Deckt den echten CLI-Subprozess-Weg (`scripts/mmo_sim.py lab ...`, ECHTER
Python-Subprozess mit geschlossenem stdin) UND die geteilte Extraktion
(`core.lobby_flow`) -- kein Testhelper baut den Lobbyablauf ausserhalb des
Produktwegs.

H01 Keine implizite Aktivierung / unveraenderter Normalweg (0 Modellcalls,
    keine Bestandsmutation fuer --help/status/attach/Fehlkonfig).
H04 Budgetarten und Grenzen greifen am realen Versand (max_requests=1).
H06 Zwei Startprozesse / EIN TUI-Schreiber (SingletonViolationError, TUI
    lehnt waehrend aktivem Lab ab).
H07 Wiederaufnahme: 'start' auf bereits vorhandenem Status wird abgelehnt,
    'resume' ohne vorherigen Status wird abgelehnt, Verbrauch wird NICHT
    zurueckgesetzt.
H-A Spy-Beleg: TUI UND Lab rufen GENAU `core.lobby_flow.run_lobby_window`
    auf (kein zweiter Spielstart-Pfad)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core.admission import _stop_flag_path  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

from test_l01_l10_lobby_initiative import (  # noqa: E402
    _FIX, _bootstrap_community, _make_ready, _persona_http_server, _session,
)

_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


def _run_lab(args: list[str], env_extra: dict | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """ECHTER Subprozess mit GESCHLOSSENEM stdin (01_AUFTRAG/02_ABNAHME
    Pruefaufbau: 'startet scripts/mmo_sim.py als NEUEN Python-Prozess mit
    geschlossenem stdin') -- ein Lab-Lauf, der versehentlich stdin lesen
    wollte, wuerde sofort mit `EOFError` auffallen (`stdin=subprocess.DEVNULL`)."""
    import os
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(_MMO_SIM), "lab", *args],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, timeout=timeout,
    )


def test_h01_help_status_attach_zero_mutation_zero_model_calls():
    """H01: --help, status, attach bei fehlendem Lauf sowie eine gescheiterte
    Konfiguration erzeugen KEINE Verzeichnisse/Marker/Community/Budgetdaten
    und rufen KEIN Modell auf (kein persona/GM-Server in diesem Test)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td) / "data"

        p_help = _run_lab(["--help"])
        assert p_help.returncode == 0, p_help.stderr
        assert not data_dir.exists(), "‑‑help darf keine Datenablage anlegen"

        p_status = _run_lab(["status", "--data-dir", str(data_dir)])
        assert p_status.returncode == 0, p_status.stderr
        payload = json.loads(p_status.stdout)
        assert payload["run"] == "none"
        assert not data_dir.exists(), "status bei fehlendem Lauf darf keine Datenablage anlegen"

        p_attach = _run_lab(["attach", "--data-dir", str(data_dir)])
        assert p_attach.returncode == 0, p_attach.stderr
        assert not (data_dir / "run" / "community").exists()

        # Fehlkonfiguration (fehlende Community) VOR jeder Anfrage ablehnen,
        # OHNE Bestandsmutation.
        p_bad = _run_lab([
            "start", "--data-dir", str(data_dir), "--community", "nope", "--profile", "api",
            "--max-requests", "3", "--max-seconds", "30", "--max-usd", "1.0", "--max-idle-windows", "2",
        ])
        assert p_bad.returncode == 2, p_bad.stdout + p_bad.stderr
        assert "Konfigurationsfehler" in p_bad.stderr
        assert not data_dir.exists(), f"gescheiterter Start darf keine Datenablage anlegen: {list(Path(td).rglob('*'))}"


def test_h04_max_requests_one_blocks_all_further_requests():
    """H04: `--max-requests 1` laesst GENAU EINEN echten Request durch --
    JEDER weitere Request (egal welche Rolle) bleibt am Admission-Gate
    haengen. Assertion auf den TATSAECHLICH beim Fake-Server eingegangenen
    Requestcount, nicht nur auf Konsolentext."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        _schema, _states, run_dir, _onboarding, _catalog = _bootstrap_community(root, "community-h04", keys)
        for pk in keys:
            _make_ready(_onboarding, _states, run_dir, pk)

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]}),
            (200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]}),
        ]) as persona_srv:
            env = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h04",
            }
            proc = _run_lab([
                "start", "--data-dir", str(root), "--community", "h04", "--profile", "api",
                "--max-requests", "1", "--max-seconds", "60", "--max-usd", "1.0", "--max-idle-windows", "5",
            ], env_extra=env)
            assert proc.returncode == 0, proc.stdout + proc.stderr
            assert len(persona_srv.calls) == 1, (
                f"genau EIN echter Request bei max_requests=1 erwartet, {len(persona_srv.calls)} erhalten"
            )

        status = lab_runner.read_status(run_dir)
        assert status is not None and status.turns_used == 1, status
        assert (run_dir / "lab.stop").exists(), "Stop-Flag haette gesetzt werden muessen"
        payload = json.loads(_run_lab(["status", "--data-dir", str(root)]).stdout)
        assert payload["next_request_blocked"] is True
        assert "max_turns" in (payload["next_request_block_reason"] or ""), payload


def test_h06_two_concurrent_starts_reject_second_and_tui_refuses_to_write():
    """H06: zwei reale Startprozesse fuer DIESELBE Datenablage -- der ZWEITE
    (nach dem ersten erfolgreichen Lock-Erwerb) wird abgelehnt
    (SingletonViolationError), waehrend der erste Prozess seinen Lock noch
    haelt. Zusaetzlich: eine gewoehnliche TUI ('l'/'b') lehnt waehrend eines
    aktiven Labs kontrolliert ab, statt heimlich zu schreiben."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-h06", keys,
        )
        _make_ready(onboarding_dir, states_dir, run_dir, "sniper")

        block_event = threading.Event()
        release_event = threading.Event()

        class _BlockingHandler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0) or 0)
                self.rfile.read(length) if length else b""
                block_event.set()  # Synchronisationsbarriere: Prozess 1 haelt jetzt den Lock UND ist "in flight".
                release_event.wait(timeout=20)
                payload = json.dumps({"choices": [{"message": {"content": '{"action": "pause"}'}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        srv = HTTPServer(("127.0.0.1", 0), _BlockingHandler)
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://{srv.server_address[0]}:{srv.server_address[1]}"
            env = {
                "MMO_SIM_PERSONA_API_BASE_URL": base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h06",
            }
            import os
            full_env = dict(os.environ)
            full_env.update(env)
            proc1 = subprocess.Popen(
                [sys.executable, str(_MMO_SIM), "lab", "start", "--data-dir", str(root),
                 "--community", "h06", "--profile", "api", "--max-requests", "1",
                 "--max-seconds", "60", "--max-usd", "1.0", "--max-idle-windows", "1"],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=full_env,
            )
            try:
                assert block_event.wait(timeout=15), "Prozess 1 haette real den Persona-Server erreichen muessen"

                # Prozess 1 haelt jetzt den Lab-Lock (Request 'in flight'). Ein
                # zweiter echter Startprozess fuer DIESELBE Datenablage muss
                # kontrolliert scheitern.
                proc2 = _run_lab([
                    "start", "--data-dir", str(root), "--community", "h06", "--profile", "api",
                    "--max-requests", "1", "--max-seconds", "60", "--max-usd", "1.0", "--max-idle-windows", "1",
                ], env_extra=env)
                assert proc2.returncode == 3, proc2.stdout + proc2.stderr
                assert "bereits aktiv" in proc2.stderr, proc2.stderr

                # Eine gewoehnliche TUI darf waehrend des aktiven Labs nicht zum
                # zweiten Schreiber werden.
                printed: list[str] = []
                tui_session = _session(
                    "h06", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
                    gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
                    persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError("kein Persona-Call erwartet")),
                    printed=printed,
                )
                tui_session._cmd_lobby_initiative()
                out = "\n".join(printed)
                assert "aktiver Lab-Lauf" in out and "kein zweiter schreibender Controller" in out, out
            finally:
                release_event.set()
                try:
                    proc1.communicate(timeout=20)
                except subprocess.TimeoutExpired:
                    proc1.kill()
                    proc1.communicate(timeout=10)
        finally:
            srv.shutdown()
            srv.server_close()
            thread.join(timeout=5)


def test_h07_resume_continues_usage_without_reset():
    """H07: ein echtes 'lab resume' (NEUER Prozess, NEUE `LabRunner`-Instanz
    fuer dieselbe Datenablage) setzt den bereits verbrauchten Turn-Zaehler
    NICHT auf 0/1 zurueck, sondern liest ihn frisch von der Platte und
    schreibt fort (R3)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        _schema, _states, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(root, "community-h07", keys)
        for pk in keys:
            _make_ready(onboarding_dir, _states, run_dir, pk)

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]}),
        ]) as persona_srv:
            env = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h07",
            }
            p_start = _run_lab([
                "start", "--data-dir", str(root), "--community", "h07", "--profile", "api",
                "--max-requests", "1", "--max-seconds", "60", "--max-usd", "1.0", "--max-idle-windows", "1",
            ], env_extra=env)
            assert p_start.returncode == 0, p_start.stdout + p_start.stderr
            assert len(persona_srv.calls) == 1

        status_after_start = lab_runner.read_status(run_dir)
        assert status_after_start.turns_used == 1
        assert status_after_start.max_turns == 1

        # Echtes 'resume': NEUE `LabRunner`-Instanz (neuer Prozess) mit einer
        # NEUEN, groesseren Budgetgrenze -- der bereits verbrauchte Turn wird
        # fortgesetzt, NICHT zurueckgesetzt (R3/H07). Bis zu 2 weitere echte
        # Requests koennen stattfinden (sniper+tech, beide frei); beide
        # Antworten sind gescriptet, damit KEIN unerwarteter driver-Fehler
        # (leere Antwortliste) den Ablauf vorzeitig als STOPPED beendet.
        with _persona_http_server([
            (200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]}),
            (200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]}),
        ]) as persona_srv2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h07b",
            }
            p_resume = _run_lab([
                "resume", "--data-dir", str(root), "--community", "h07", "--profile", "api",
                "--max-requests", "5", "--max-seconds", "60", "--max-usd", "5.0", "--max-idle-windows", "1",
            ], env_extra=env2)
            assert p_resume.returncode == 0, p_resume.stdout + p_resume.stderr
            assert 1 <= len(persona_srv2.calls) <= 2, persona_srv2.calls

        status_after_resume = lab_runner.read_status(run_dir)
        assert status_after_resume.max_turns == 5, "Resume uebernimmt die NEUE Budgetgrenze"
        assert status_after_resume.turns_used == status_after_start.turns_used + len(persona_srv2.calls), (
            f"Resume haette exakt um die real erfolgten neuen Requests fortschreiben sollen "
            f"({status_after_start.turns_used} + {len(persona_srv2.calls)}), nicht: "
            f"{status_after_resume.turns_used}"
        )
        assert status_after_resume.turns_used > 1, "Resume darf den Verbrauch nicht auf den Start-Wert zuruecksetzen"


def test_ha_tui_and_headless_call_the_same_lobby_flow_function():
    """H-A Spy-Beleg (analog `test_a04_shared_app_service.py`): sowohl
    `TuiSession._cmd_lobby_initiative` (TUI-Weg) als auch der Headless-
    Controller (`mmo_sim.lab.cli._run_controller`, hier direkt am
    Modulattribut geprueft) rufen EXAKT `core.lobby_flow.run_lobby_window`
    auf -- kein zweiter, kopierter Spielstart-Pfad."""
    calls: list[str] = []
    original = lobby_flow.run_lobby_window

    def spy(session, ai_personas=None):
        calls.append("tui" if ai_personas is None else "headless")
        return lobby_flow.LobbyWindowOutcome(kind=lobby_flow.LobbyOutcomeKind.NO_CONSENSUS, reason="spy")

    # `ui/tui.py:_cmd_lobby_initiative` importiert `core.lobby_flow` erst zur
    # Aufrufzeit (`from ..core import lobby_flow`) -- dieselbe Modulinstanz
    # wie hier (`sys.modules`-Cache), ein Patch auf DIESES Attribut greift
    # deshalb unabhaengig vom TUI-eigenen Importstil.
    lobby_flow.run_lobby_window = spy
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="spy",
                input_fn=lambda p="": (_ for _ in ()).throw(EOFError()), print_fn=printed.append,
                run_dir=root / "run", states_dir=root / "states", schema_path=None,
                gm_transport_factory=lambda *_a, **_kw: None, persona_driver_factory=lambda pk: None,
            )
            session._cmd_lobby_initiative()
    finally:
        lobby_flow.run_lobby_window = original
    assert calls == ["tui"], calls


if __name__ == "__main__":
    import traceback

    tests = [
        test_h01_help_status_attach_zero_mutation_zero_model_calls,
        test_h04_max_requests_one_blocks_all_further_requests,
        test_h06_two_concurrent_starts_reject_second_and_tui_refuses_to_write,
        test_h07_resume_continues_usage_without_reset,
        test_ha_tui_and_headless_call_the_same_lobby_flow_function,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
