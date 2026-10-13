#!/usr/bin/env python3
"""
tests/mmo_sim/_ux1_r6_persona_loopback_support.py — W25 (ZEITRISS Terminal
UX-1, R6): Loopback-Persona-Double-Server fuer den ECHTEN Subprozess-Pfad.

Luecke (s. BRIEF-W25.md): `manual_offline_harness.py`/die R6-Testfahrt
starten den ECHTEN `scripts/mmo_sim.py`-Subprozess. Fuer die GM-/SL-Grenze
existiert bereits ein inhaltsgebundener Loopback-HTTP-Server
(`_ux1_r5_synthetic_creation_support.CreationCapableSmartGmServer`, Muster
`e2e_real_subprocess_dialog.py:SmartGmServer`). FUER DIE PERSONA-GRENZE
(`MMO_SIM_PERSONA_API_BASE_URL`/`_API_KEY`/`_API_MODEL`,
`mmo_sim/adapters/factories.py:default_persona_driver_factory` ->
`mmo_sim/adapters/persona_api.py:PersonaApiDriver`) gab es bisher NUR einen
reinen Antwort-QUEUE-Fake (`mmo_sim/adapters/fakes.py:FakeHTTPServer`,
bereits genutzt von `e2e_real_subprocess_dialog.py`/`_a24_local_support.py`'s
`SequencedHTTPServer`) -- fuer einen Prozessneustart (separater Subprozess,
derselbe Datenroot) ist eine reine Call-Reihenfolge-Queue riskant (ein
bereits beantworteter, aber nicht mehr angefragter Request verschiebt den
Index). Dieser Server ist deshalb -- wie `CreationCapableSmartGmServer` --
INHALTSGEBUNDEN: er leitet JEDE Antwort direkt aus dem tatsaechlich
empfangenen Request-Body ab, nie aus einem lokalen, prozessgebundenen
Call-Zaehler.

HTTP-Vertrag (exakt `mmo_sim/adapters/persona_api.py:PersonaApiDriver.decide`,
openai-kompatibel): POST `<base_url>/chat/completions`, Body
`{"model", "messages":[{"role":"system","content":...},
{"role":"user","content":...}], "temperature", "max_tokens"}`. Antwort
`{"choices":[{"message":{"content": ...}}], "usage": {...}}`.

Drei inhaltsgebundene Zweige, 1:1 nach dem Muster der bereits etablierten
In-Prozess-Referenz `_AcceptAndPlayDriver`
(`test_ux1_r5_round_journey_group_sizes_2026_10_06.py`):

1. Private Reflexion (`system == "PRIVATE_REFLECTION_SENTINEL"`, s.
   `core/runtime.py:_collect_reflections`): liefert IMMER einen echten,
   NICHT-leeren synthetischen Text. `_collect_reflections` behandelt die
   KI-Reflexion als PFLICHT (anders als die freiwillige menschliche Notiz)
   -- eine leere Antwort wuerde dort als `status=pending_recovery`
   verbucht und haelt `finalize` dauerhaft offen (empirisch an diesem
   Double beobachtet, erste Fassung lieferte faelschlich "": der Tisch
   blieb nach einem vollstaendigen Abschluss-Turn `status=active` statt
   `closed`). Ein echter, unterscheidbarer Text ist daher PFLICHT, kein
   Spielzug-Fachpunkt.
2. Entscheidungsvertrag (`decision_contract_instruction`, erkannt an der
   eingebetteten `"offer_id": "..."`-JSON-Beispielzeile im `user`-Text --
   dieselbe Textform, die `ui/tui.py` tatsaechlich in den Modellprompt
   einbettet, s. `adapters/base.py:decision_contract_instruction`):
   `offer_id`/`participant_id` werden direkt aus dem WIRE-Text extrahiert
   (real vom Aufrufer eingesetzte Werte, kein Raten) und per konfigurierter
   `decisions`-Zuordnung (`persona_key -> "accept"|"reject"`, Default
   "accept") in die exakte `ENTSCHEIDUNG offer_id=... participant_id=...
   decision=...`-Kontrollform (`adapters/base.py:_DECISION_LINE_RE`)
   zurueckgeschrieben -- derselbe Vertrag wie `_a24_local_support.
   accept_text`/`reject_text`.
3. Sonst (normaler Spielzug): ein echter, unterscheidbarer, wortgebundener
   Zugtext (`persona_key` + laufende Zaehlung) -- wie `_AcceptAndPlayDriver.
   play_calls`, bewusst NICHT restart-sicher (ein Positionszaehler je
   Serverinstanz reicht hier aus: einmal admittierte Entscheidungen werden
   vom Produkt selbst durabel wiederverwendet, s. `core/lobby_service.
   request_admitted_decision`/`find_durable_result` -- ein Neustart fragt
   eine BEREITS beantwortete Entscheidung gar nicht erneut per HTTP an)."""
from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

_PRIVATE_REFLECTION_SENTINEL = "PRIVATE_REFLECTION_SENTINEL"
# Exakt die von `decision_contract_instruction` (mmo_sim/adapters/base.py)
# eingebettete JSON-Beispielzeile -- `offer_json`/`participant_json` sind
# dort `json.dumps(offer_id)`/`json.dumps(participant_id)`, also reale,
# bereits mit Anfuehrungszeichen versehene Werte, kein Platzhaltertext.
_OFFER_RE = re.compile(r'"offer_id":\s*"([^"]*)"')
_PARTICIPANT_RE = re.compile(r'"participant_id":\s*"([^"]*)"')


class _PersonaLoopbackHandler(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        self.server.calls.append(body)  # type: ignore[attr-defined]
        messages = body.get("messages") or []
        system_text = ""
        user_text = ""
        if messages and isinstance(messages[0], dict):
            system_text = messages[0].get("content") or ""
        if len(messages) > 1 and isinstance(messages[1], dict):
            user_text = messages[1].get("content") or ""
        content = self._decide(system_text, user_text)
        self._respond(content)

    def _decide(self, system_text: str, user_text: str) -> str:
        server = self.server  # type: ignore[assignment]
        if system_text.strip() == _PRIVATE_REFLECTION_SENTINEL:
            server.reflection_calls.append(user_text)  # type: ignore[attr-defined]
            server.reflection_replies += 1  # type: ignore[attr-defined]
            return f"[PersonaLoopback] Synthetische Pflichtreflexion #{server.reflection_replies}."
        offer_match = _OFFER_RE.search(user_text)
        participant_match = _PARTICIPANT_RE.search(user_text)
        if offer_match and participant_match:
            offer_id, participant_id = offer_match.group(1), participant_match.group(1)
            decision = server.decisions.get(participant_id, "accept")  # type: ignore[attr-defined]
            server.decision_calls.append({  # type: ignore[attr-defined]
                "offer_id": offer_id, "participant_id": participant_id, "decision": decision,
            })
            explanation = "Ich bin dabei." if decision == "accept" else "Ich lehne ab."
            return (
                f"ENTSCHEIDUNG offer_id={offer_id} participant_id={participant_id} "
                f"decision={decision} explanation={explanation}"
            )
        # Normaler Spielzug -- persona_key ist in diesem Double nicht aus
        # dem Wire selbst ableitbar (anders als offer_id/participant_id bei
        # einer Einladung); der Aufrufer liest `.calls`/`.play_calls_total`
        # fuer den Beleg "mindestens ein echter Zug", der Inhalt muss nur
        # real/unterscheidbar sein, keine persona_key-Bindung noetig.
        server.play_calls_total += 1  # type: ignore[attr-defined]
        return f"[PersonaLoopback] Synthetischer Spielzug #{server.play_calls_total}: Wir sichern die Lage."

    def _respond(self, content: str) -> None:
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class PersonaLoopbackServer(HTTPServer):
    """Echter Loopback-HTTP-Server (127.0.0.1, zufaelliger freier Port) an
    der Persona-/`MMO_SIM_PERSONA_API_BASE_URL`-Transportgrenze -- inhalts-
    gebunden (s. Moduldocstring), KEIN Antwort-Queue-Fake. `decisions`
    (`persona_key -> "accept"|"reject"`, Default "accept" fuer jeden nicht
    gelisteten Schluessel) macht den Entscheidungsraum des Doubles explizit
    konfigurierbar -- echte, synthetisch-deterministische accept/reject-
    Antworten ueber den realen HTTP-/Entscheidungsvertrag, kein Keyword-/
    Namensraten im Produktcode."""

    def __init__(self, decisions: dict[str, str] | None = None):
        super().__init__(("127.0.0.1", 0), _PersonaLoopbackHandler)
        self.calls: list[dict] = []
        self.decision_calls: list[dict] = []
        self.reflection_calls: list[str] = []
        self.reflection_replies = 0
        self.play_calls_total = 0
        self.decisions: dict[str, str] = dict(decisions or {})
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
