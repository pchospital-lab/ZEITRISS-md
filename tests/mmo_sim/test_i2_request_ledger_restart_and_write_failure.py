#!/usr/bin/env python3
"""
tests/mmo_sim/test_i2_request_ledger_restart_and_write_failure.py — Auflage 5
(PLAN-CRITIC.md F8, MAIN-ENTSCHEIDUNG.md, I1-I3-Nachzug 2026-09-23):
`review_p2q_request_contract.py` Test 05 beweist nur "verlorene Antwort,
Retry mit frischen Objekten im SELBEN Prozess". Diese Datei beweist die
beiden davon NICHT abgedeckten Faelle, zusaetzlich zu den 8 unveraenderten
Q-Faellen:

  (a) ECHTER Prozess-Restart (ein neuer `python3`-Subprozess, kein neues
      Objekt im selben Interpreter) sieht die bereits committete
      Reservierung (`core.request_ledger.begin`) von der Platte und sendet
      NICHT blind erneut an denselben Loopback-Empfaenger.
  (b) Ein simulierter lokaler Schreibfehler ZWISCHEN `received` und
      `accounted` (`core.request_ledger.finish_received`s zweiter Schreib-
      schritt) verliert die bereits VOR dem Versand committete Budget-
      Reservierung nicht und hinterlaesst einen ehrlich lesbaren
      Zwischenzustand (`state=received`, NICHT `accounted`) statt eines
      korrupten/verschwundenen Datensatzes.

Pure Python, nur `assert`, echter Exitcode. Providerfrei fuer (b); (a)
startet zwei ECHTE `python3`-Subprozesse gegen einen echten Loopback-HTTP-
Server (kein externes Netzwerk, keine echte Modellinferenz)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import request_ledger, store  # noqa: E402
from mmo_sim.core.admission import read_admission_block, write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.lab.runner import LabBudget, LabRunner, read_status  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)

_CHILD_SCRIPT = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    repo_root, run_dir, url, timeout = sys.argv[1], Path(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    sys.path.insert(0, repo_root)
    from mmo_sim.core import app_service, store
    from mmo_sim.core.controller import TableController
    from mmo_sim.core.persona_state import PersonaStateStore
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy
    from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver

    class _UnreachedGm:
        def turn(self, turn_idx, user_text):
            raise AssertionError("GM darf bei geblocktem/verlorenem Persona-Request nie erreicht werden")

    schema_path = run_dir.parent / "schema.json"
    states_dir = run_dir.parent / "states"
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table = store.Table.load(run_dir, "restart-table")
    driver = PersonaApiDriver(PersonaApiConfig(url, "SYNTHETIC", "test", timeout=timeout), "solo_pk")
    controller = TableController("solo_pk", {"solo_pk": driver})
    try:
        outcome = app_service.run_play_session(
            lobby, table, _UnreachedGm(), controller, "restart-section",
            {"solo_pk": {"system": "own", "user": "Aktion?"}}, states_dir,
            "2026-09-23", "2026-09-23T00:00:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
            ps_store, zeitriss_saves.harvest_from_debrief, max_turns=1,
        )
        print(json.dumps({"reason": outcome.completion.reason}))
    except Exception as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
    """
)


def _bootstrap_solo_run_dir(root: Path) -> Path:
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    states_dir = root / "states"
    states_dir.mkdir()
    run_dir = root / "run"
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    ps_store.save_state("solo_pk", {
        "v": 2, "persona_key": "solo_pk", "rounds_played": 0,
        "plays_char": {"character_id": "chrono-restart"},
    }, states_dir=states_dir)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("solo_pk")
    table, _ = store.create_table_from_offer_log(
        lobby, "restart-table", [{"type": "offer", "id": "o1", "from": "solo_pk", "wants": []}],
        {"solo_pk": "chrono-restart"},
    )
    assert table is not None
    return run_dir


def test_i2_real_process_restart_does_not_resend_lost_request():
    """(a) Auflage 5: ECHTER `python3`-Subprozess-Neustart, kein neues
    Objekt im selben Interpreter. Subprozess 1 sendet einen echten
    Loopback-Request, dessen Antwort clientseitig durch Timeout verloren
    geht (die Serverzeit ist LAENGER als der Client-Timeout) -- die
    Reservierung wird VOR dem Versand auf Platte committet
    (`request_ledger.begin`). Ein GENUIN NEUER Subprozess 2 sieht dasselbe
    `run_dir` frisch von der Platte (max_turns=1 bereits erreicht) und darf
    KEINEN zweiten echten Request an den Server absetzen."""
    calls: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            return

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length) if length else b""
            calls.append(json.loads(body))
            time.sleep(0.3)  # laenger als der Client-Timeout unten -> Antwort geht verloren.
            try:
                payload = json.dumps({
                    "choices": [{"message": {"content": "Antwort kommt zu spaet"}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 2},
                }).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_dir = _bootstrap_solo_run_dir(root)
            write_test_profile(run_dir, max_turns=1)
            url = f"http://127.0.0.1:{server.server_port}"
            child = root / "child_restart.py"
            child.write_text(_CHILD_SCRIPT, encoding="utf-8")

            proc1 = subprocess.run(
                [sys.executable, str(child), str(_REPO_ROOT), str(run_dir), url, "0.05"],
                capture_output=True, text=True, timeout=20,
            )
            assert proc1.returncode == 0, f"Subprozess 1 stderr: {proc1.stderr}"
            status_after_1 = json.loads((run_dir / "lab.status.json").read_text())
            assert status_after_1["turns_used"] >= 1, (
                "Reservierung muss VOR dem Versand committet sein -- unabhaengig davon, ob eine "
                "Antwort je eintrifft (Case 05)."
            )
            assert len(calls) == 1, f"Subprozess 1 muss GENAU EINEN echten Request absetzen, calls={calls}"

            # ECHTER Prozess-Neustart: neuer `python3`-Interpreter, kein
            # gemeinsamer In-Memory-Zustand mit Subprozess 1.
            proc2 = subprocess.run(
                [sys.executable, str(child), str(_REPO_ROOT), str(run_dir), url, "0.05"],
                capture_output=True, text=True, timeout=20,
            )
            assert proc2.returncode == 0, f"Subprozess 2 stderr: {proc2.stderr}"
            assert len(calls) == 1, (
                f"Ein echter Prozess-Neustart darf denselben, bereits verbrauchten Request NICHT "
                f"blind erneut senden (Resume-Regel, Case 05) -- calls={calls}"
            )
            out2 = json.loads(proc2.stdout.strip().splitlines()[-1])
            assert "reason" in out2 and "Admission-Gate" in out2["reason"], (
                f"Subprozess 2 muss am Admission-Gate (max_turns bereits verbraucht) blockieren, "
                f"nicht an einem anderen Fehler: {out2}"
            )
    finally:
        server.shutdown()
        server.server_close()
        th.join()


def test_i2_write_failure_between_received_and_accounted_keeps_reservation_committed():
    """(b) Auflage 5: `request_ledger.finish_received` schreibt den
    Datensatz ZWEIMAL (state=received, dann state=accounted). Ein
    simulierter Schreibfehler GENAU zwischen diesen beiden Schritten darf
    (1) die bereits in `begin()` committete `turns_used`/`usd_spent`-
    Reservierung NICHT verlieren/doppelt anrechnen und (2) muss einen
    ehrlich lesbaren Zwischenzustand (`state=received`) hinterlassen --
    kein verschwundener/korrupter Datensatz, kein stilles Verschlucken des
    Fehlers."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=5, max_usd=1.0)

        request_id = request_ledger.begin(
            run_dir, role="persona_decision", content="Testinhalt", reserved_usd=0.01,
        )
        status_after_begin = json.loads((run_dir / "lab.status.json").read_text())
        assert status_after_begin["turns_used"] == 1
        assert abs(status_after_begin["usd_spent"] - 0.01) < 1e-9

        real_write = request_ledger._write_request
        call_count = {"n": 0}

        def _flaky_write(rd, rid, data):
            call_count["n"] += 1
            if call_count["n"] == 2:  # der ZWEITE Schreibversuch (received -> accounted) scheitert.
                raise OSError("simulierter Schreibfehler zwischen received und accounted")
            return real_write(rd, rid, data)

        with patch.object(request_ledger, "_write_request", side_effect=_flaky_write):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"prompt_tokens": 1, "completion_tokens": 1})
                raised = False
            except OSError:
                raised = True
        assert raised, "Der simulierte Schreibfehler darf nicht still verschluckt werden."

        # Reservierung bleibt UNVERAENDERT (kein Doppel-Anrechnen, kein
        # Verlust) -- `begin()` hat bereits committet, `finish_received`
        # ruehrt `turns_used`/`usd_spent` nicht mehr an.
        status_after_failure = json.loads((run_dir / "lab.status.json").read_text())
        assert status_after_failure["turns_used"] == 1
        assert abs(status_after_failure["usd_spent"] - 0.01) < 1e-9

        # Der Datensatz selbst zeigt ehrlich den unterbrochenen Zwischen-
        # zustand -- NICHT `accounted` (der zweite Schreibversuch scheiterte).
        on_disk = request_ledger.load_request(run_dir, request_id)
        assert on_disk is not None, "Requestdatensatz darf nicht verschwinden."
        assert on_disk["state"] == "received", on_disk
        assert on_disk["usage"] == {"prompt_tokens": 1, "completion_tokens": 1}

        open_reqs = request_ledger.open_requests(run_dir)
        assert any(r["id"] == request_id for r in open_reqs), (
            "Ein unterbrochener Datensatz muss als OFFEN (nicht `accounted`) sichtbar bleiben -- "
            "End-Critic-/Recovery-Sicht auf offene Verpflichtungen."
        )

        # Der naechste echte Admission-Gate-Check bleibt trotz des
        # Schreibfehlers funktionsfaehig (kein korrupter lab.status.json).
        blocked, reason = read_admission_block(run_dir)
        assert blocked is False, reason


def test_i2_labrunner_and_read_status_tolerate_open_request_records():
    """Auflage 2 (PLAN-CRITIC F4, bindend, hoechste Prioritaet): die neuen
    Pro-Request-Datensaetze leben in `run_dir/requests/` -- NICHT als neue
    Top-Level-Felder in `lab.status.json`/`LabStatus`. `lab/runner.
    read_status` baut `LabStatus(**json.loads(...))` per striktem
    Dataclass-Konstruktor -- JEDER unbekannte Top-Level-Key wuerde dort mit
    `TypeError` abbrechen. Expliziter Gegentest: `LabRunner(...)`/
    `read_status(...)` gegen einen `run_dir` mit mindestens einem offenen
    (nicht `accounted`) Requestdatensatz."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(max_turns=10, max_seconds=1000, max_usd=1.0))
        lab.start()

        # Mindestens EIN offener Requestdatensatz fuer dieses run_dir.
        request_ledger.begin(run_dir, role="persona_decision", content="x", reserved_usd=0.01)
        assert request_ledger.open_requests(run_dir), "Vorbedingung: es muss einen offenen Requestdatensatz geben."

        # `read_status` darf NICHT an einem unbekannten Top-Level-Key brechen.
        status = read_status(run_dir)
        assert status is not None
        assert status.turns_used == 1  # von `request_ledger.begin()` committet.

        # Ein NEUER `LabRunner` fuer dasselbe `run_dir` (Resume) muss
        # ebenfalls unveraendert funktionieren.
        lab.release()
        resumed = LabRunner(run_dir, LabBudget(max_turns=10, max_seconds=1000, max_usd=1.0))
        assert resumed._turns_used == 1

        # `lab.status.json` selbst traegt KEINE neuen Top-Level-Felder --
        # nur der bereits vor diesem Umbau bekannte `LabStatus`-Feldsatz
        # (+ `provider_free`, bereits vorher optional).
        raw = json.loads((run_dir / "lab.status.json").read_text())
        known_fields = {f for f in vars(status)}
        assert set(raw.keys()) <= known_fields, f"Unbekannte Top-Level-Felder in lab.status.json: {set(raw.keys()) - known_fields}"


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
