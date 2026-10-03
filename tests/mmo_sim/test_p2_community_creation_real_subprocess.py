#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2_community_creation_real_subprocess.py — echter
`scripts/mmo_sim.py`-Subprozessbeleg fuer die persona-getriebene
Community-Erstgeneration (02_ABNAHME.md: "Mind. ein echter
`scripts/mmo_sim.py`-Ablauf mit Terminaleingaben und kontrollierten
Empfaengern").

Startet einen ECHTEN, EIGENSTAENDIGEN Python-Subprozess (kein In-Prozess-
`TuiSession`-Aufruf) mit Terminaleingabe `c\nx\n` -- exakt der reale Weg
ueber den Launcher-Entrypoint. Testdoubles sitzen AUSSCHLIESSLICH an der
aeussersten Prozess-/HTTP-Grenze (analog `e2e_real_subprocess_dialog.py`):
ein echter Loopback-HTTP-Server fuer die SL (`OPENWEBUI_URL`, OWUI-Vertrag)
und ein echter Loopback-HTTP-Server fuer die Persona-Antworten
(`MMO_SIM_PERSONA_API_BASE_URL`, openai-kompatibel). Der komplette
Produktionsweg (`scripts/mmo_sim.py` -> `TuiSession._cmd_community` ->
`community_creation.advance_community_creation` ->
`core/creation_service.run_admitted_creation_dialog` -> echte
`GmOwuiTransport`/`PersonaApiDriver`-Adapter -> Admission/Ledger/Store)
laeuft echt durch einen frischen Interpreterprozess.

Budget (`write_test_profile(max_turns=3)`, VOR dem Subprozess persistiert)
begrenzt die reale Erschaffung bewusst auf GENAU EINE Persona (3 admitted
Requests: GM-Frage, Persona-Antwort, GM-Save-Turn) -- die uebrigen sieben
Default-Startpersonas werden dadurch am frischen Admission-Gate OHNE
weiteren HTTP-Call kontrolliert blockiert (belegt zugleich den
Budget-/Stop-Pfad der Abnahme-Matrix im echten Subprozess)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.fakes import FakeHTTPServer  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _CreationGmHandler(BaseHTTPRequestHandler):
    """Echter Loopback-HTTP-Server, ersetzt NUR die aeussere HTTP-Grenze von
    `owui_client.OWUIChat` -- antwortet mit einer SL-Frage auf den ersten
    empfangenen Turn, mit einem gueltigen v7-Save-Block ab dem zweiten
    (Budget begrenzt die reale Erschaffung auf GENAU EINE Persona, s.
    Moduldocstring — kein Verwechslungsrisiko zwischen mehreren Chats)."""

    def log_message(self, *args):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        self.server.calls.append(body)  # type: ignore[attr-defined]
        n = len(self.server.calls)  # type: ignore[attr-defined]
        if n >= 2:
            content = (
                "```json\n"
                '{"v": 7, "characters": [{"char_id": "chrono-e2e-community", '
                '"name": "E2ECreated", "callsign": "E2E", "level": 1}]}\n'
                "```"
            )
        else:
            content = "Welche Grundausstattung waehlst du fuer deinen ersten Einsatz?"
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class _CreationGmServer(HTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), _CreationGmHandler)
        self.calls: list[dict] = []
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.shutdown()
        self.server_close()


def _run_process(data_dir: Path, participant: str, stdin_text: str, env_extra: dict) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
           "--data-dir", str(data_dir), "--participant", participant]
    return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, env=env, cwd=str(data_dir), timeout=60)


def test_real_subprocess_c_command_creates_exactly_one_persona_within_budget():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run", max_turns=3)

        with _CreationGmServer() as gm_srv, FakeHTTPServer([
            (200, {"choices": [{"message": {"content": "Ich waehle leichte Ruestung und einen Karabiner."}}], "usage": {"prompt_tokens": 4, "completion_tokens": 4}}),
        ]) as persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_E2E_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_E2E_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
            }
            # R3 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
            # §5): eine NEUE Community mit konfigurierter Live-Anbindung
            # verlangt jetzt eine explizite [d/p]-Herkunftsantwort VOR der
            # ersten Modellanfrage -- Original-Stdin war `"c\nx\n"` (ein
            # bewusst ungueltiges `x` fiel FRUEHER still auf DEMO zurueck,
            # das ist genau der behobene Bug). Derivat: `"c\nd\nx\n"`
            # (explizites `d` -- unveraendert DEMO/SIMULIERT-Herkunft, die
            # dieser Test ohnehin nie inhaltlich prueft). Diff: eine
            # zusaetzliche `d\n`-Zeile nach `c\n`.
            proc = _run_process(data_dir, "caller_human", "c\nd\nx\n", env)
            assert proc.returncode == 0, f"echter Subprozess fehlgeschlagen: {proc.stderr}\n{proc.stdout}"
            assert "Neue Spielgemeinschaft" in proc.stdout, proc.stdout
            assert "Persona-getriebene Erstgeneration" in proc.stdout, proc.stdout

            # Echter Empfaenger: GM-Server hat GENAU 2 Turns erhalten (Frage
            # + Save-Turn der EINEN Persona, fuer die das Budget reichte).
            assert len(gm_srv.calls) == 2, f"GM haette real genau 2x befragt werden muessen, war: {len(gm_srv.calls)}"
            assert len(persona_srv.calls) == 1, f"Persona-Server haette real genau 1x befragt werden muessen, war: {len(persona_srv.calls)}"

            # Genau EINE Persona wurde tatsaechlich spielbereit (Current-Save
            # + Katalog), die anderen sieben blieben Entwuerfe (Budget-Stop).
            plan_path = data_dir / "run" / "community" / "bootstrap__plan.json"
            assert plan_path.is_file()
            planned_keys = list(json.loads(plan_path.read_text(encoding="utf-8"))["personas"].keys())
            assert len(planned_keys) == 8

            ps_store = PersonaStateStore(schema_path=SCHEMA)
            ready = [
                pk for pk in planned_keys
                if store.load_current_save_or_raise(data_dir / "run", pk, ps_store, states_dir=data_dir / "states") is not None
            ]
            assert len(ready) == 1, f"Budget haette GENAU EINE spielbereite Persona erlauben duerfen, war: {ready}"
            ready_pk = ready[0]
            current = store.load_current_save_or_raise(data_dir / "run", ready_pk, ps_store, states_dir=data_dir / "states")
            assert current["characters"][0]["char_id"] == "chrono-e2e-community"

            # ECHTER NEUER Interpreterprozess (Reentry): kein zusaetzlicher
            # Request fuer die bereits fertige Persona, Fortschritt bleibt.
            gm_calls_before, persona_calls_before = len(gm_srv.calls), len(persona_srv.calls)
            proc2 = _run_process(data_dir, "caller_human", "c\nx\n", env)
            assert proc2.returncode == 0, proc2.stderr
            ready_after = [
                pk for pk in planned_keys
                if store.load_current_save_or_raise(data_dir / "run", pk, ps_store, states_dir=data_dir / "states") is not None
            ]
            assert ready_after == ready, "Reentry darf bereits fertige Personas nicht neu erschaffen/ueberschreiben"
            assert len(gm_srv.calls) == gm_calls_before, "Reentry der bereits fertigen Persona darf keinen neuen GM-Request ausloesen"
            # Budget ist bereits ausgeschoepft (max_turns=3 erreicht) -- auch
            # die naechste offene Persona bekommt KEINEN weiteren Request.
            assert len(persona_srv.calls) == persona_calls_before


def main() -> int:
    tests = [test_real_subprocess_c_command_creates_exactly_one_persona_within_budget]
    failed = 0
    for t in tests:
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
