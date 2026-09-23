#!/usr/bin/env python3
"""
mmo_sim/adapters/fakes.py — Fakes an der ECHTEN Prozess-/HTTP-Grenze.

Zweck (M1/03 §7): die Offline-Tests pruefen die tatsaechlichen Adapter
(`persona_api.py`, `persona_claude_code.py`, `gm_owui.py`) — nicht einen
separaten Pfad, der Produktionscode ueberspringt. Diese Fakes ersetzen NUR
die aeusserste Grenze (die echte Binary bzw. den echten HTTP-Server), damit
der Adaptercode selbst (Argument-/Header-/Body-Aufbau, Fehlerabbildung,
Rueckgabe-Parsing) real durchlaufen wird.

- `FakeCLIProcess`: ersetzt `subprocess.run`/`Popen` fuer `persona_claude_code`.
  Zeichnet argv + stdin auf, liefert konfigurierbaren stdout/stderr/returncode.
- `FakeHTTPServer`: echter `http.server` auf 127.0.0.1 (Loopback), zeichnet
  Methode/Pfad/Header/Body jedes Requests auf, liefert konfigurierbare
  Antworten (inkl. 401/403/429 fuer Preflight-/Fallback-Tests).
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer


@dataclass
class RecordedCall:
    argv: list[str]
    stdin: str
    env: dict
    cwd: str | None = None


class FakeCLIProcess:
    """Ersetzt den echten `subprocess.run`-Aufruf fuer `persona_claude_code`.

    `responses` ist eine Liste von `(returncode, stdout, stderr)`-Tupeln, die
    der Reihe nach fuer aufeinanderfolgende `.run()`-Aufrufe geliefert werden."""

    def __init__(self, responses: list[tuple[int, str, str]]):
        self._responses = list(responses)
        self.calls: list[RecordedCall] = []

    def run(
        self, argv: list[str], stdin: str = "", env: dict | None = None, cwd: str | None = None,
    ) -> tuple[int, str, str]:
        self.calls.append(RecordedCall(argv=list(argv), stdin=stdin, env=dict(env or {}), cwd=cwd))
        if not self._responses:
            raise RuntimeError("FakeCLIProcess: keine weiteren gecannten Antworten.")
        return self._responses.pop(0)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # Test-Stille: kein stderr-Spam
        return

    def _handle(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b""
        record = {
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers.items()),
            "body": body.decode("utf-8", errors="replace"),
        }
        self.server.recorded_calls.append(record)  # type: ignore[attr-defined]
        status, payload = self.server.next_response()  # type: ignore[attr-defined]
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self._handle()

    def do_GET(self):
        self._handle()


class FakeHTTPServer:
    """Echter Loopback-HTTP-Server (127.0.0.1, zufaelliger freier Port) fuer
    `persona_api`/`gm_owui` Offline-Tests. KEIN externer Netzwerkzugriff —
    ausschliesslich 127.0.0.1, wie vom Auftrag verlangt (03 §7: 'ein lokaler
    Mock darf Netzwerk nutzen, aber nur expliziten Loopback-Testendpunkt')."""

    def __init__(self, responses: list[tuple[int, dict]]):
        self._responses = list(responses)
        self._server = HTTPServer(("127.0.0.1", 0), _Handler)
        self._server.recorded_calls = []  # type: ignore[attr-defined]
        self._server.next_response = self._next_response  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def _next_response(self) -> tuple[int, dict]:
        if not self._responses:
            return 500, {"error": "FakeHTTPServer: keine weiteren gecannten Antworten."}
        return self._responses.pop(0)

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    @property
    def calls(self) -> list[dict]:
        return self._server.recorded_calls  # type: ignore[attr-defined]

    def __enter__(self) -> "FakeHTTPServer":
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._server.shutdown()
        self._server.server_close()
