#!/usr/bin/env python3
"""
tests/mmo_sim/_r5_t1_persona_double.py -- Grenzinjektion fuer T1c (R5,
t1t2): ein echter Loopback-HTTP-Server (127.0.0.1, wie `mmo_sim.adapters.
fakes.FakeHTTPServer`/`e2e_real_subprocess_dialog.py:_persona_server`), der
NUR die aeusserste Persona-API-Grenze ersetzt (`PersonaApiDriver` selbst
laeuft real, inkl. echtem `urllib`-POST) -- NIE ein Live-Modell.

Unterschied zu `FakeHTTPServer`: GENAU EIN benannter Call-Index darf einen
"Stop-Race" ausloesen, BEVOR er antwortet -- identische Technik zu
`tests/mmo_sim/_r4_gm_double.py:_run_stop_race` (schreibt die Kontrollzeile
WAEHREND des offenen HTTP-Calls in die ECHTE Kontroll-FIFO, wartet
KONTROLLIERT/Polling auf den durablen Tisch-Stop), hier an der Persona-
HTTP-Grenze statt am GM-Transport-Double-Seam. Das ist der fuer T1c
verlangte "wirklich offene Personaaufruf" (STOP-BOUNDARY §3.4): die
Anfrage ist zum Zeitpunkt des Stops tatsaechlich unterwegs (der Handler
haengt im `_run_stop_race`-Polling), NICHT bereits abgeschlossen."""
from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _r4_gm_double import _run_stop_race  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        server = self.server
        server.calls.append(body)  # type: ignore[attr-defined]
        call_index = len(server.calls)  # type: ignore[attr-defined] 1-basiert
        stop_cfg = server.stop_cfg  # type: ignore[attr-defined]
        if stop_cfg is not None and stop_cfg.get("after_call") == call_index:
            # GENAU HIER ist der Request tatsaechlich offen (Handler haengt
            # im Stop-Race-Polling) -- die spaete Antwort kommt erst NACH
            # dem durabel bestaetigten Tisch-Stop.
            _run_stop_race(stop_cfg)
        responses = server.responses  # type: ignore[attr-defined]
        content = responses[call_index - 1] if call_index - 1 < len(responses) else ""
        payload = {"choices": [{"message": {"content": content}}], "usage": {}}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.do_POST()


class PersonaStopRaceServer(HTTPServer):
    """Echter Loopback-HTTP-Server -- ersetzt NUR die aeusserste Persona-
    API-Grenze. `responses`: Liste der Textinhalte, 1-basiert nach
    Call-Index. `stop_cfg`: dieselbe Konfigform wie `_r4_gm_double.
    _run_stop_race` (`after_call`, `kind`, `control_fifo`/`control_line`,
    `run_dir`, `table_id`)."""

    def __init__(self, responses: list[str], stop_cfg: dict | None = None):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.calls: list[dict] = []
        self.responses = list(responses)
        self.stop_cfg = stop_cfg
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "PersonaStopRaceServer":
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.shutdown()
        self.server_close()
