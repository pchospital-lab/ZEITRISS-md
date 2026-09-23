#!/usr/bin/env python3
"""
mmo_sim/adapters/persona_api.py — `openai_compatible`-Persona-Adapter
(echter Produktionspfad, LiteLLM/OpenRouter, 03_PROVIDER_UND_BETRIEB.md §1/§4).

Echter HTTP-Aufruf (urllib, kein Framework-Zwang) gegen einen konfigurierten
OpenAI-kompatiblen Endpunkt. Fehlerabbildung OHNE stillen Fallback (03 §4):
401/403 -> `ProviderAuthError`, 429 -> `ProviderQuotaError`, Timeout ->
`ProviderUnavailableError`. Preflight (`check_auth_configured`) prueft VOR
einem teuren Request, ob ueberhaupt ein Key/Base-URL konfiguriert ist (A02/A15
— fehlende Anmeldung muss sichtbar werden, bevor Kosten entstehen).
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .base import (
    ParticipantDecision,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderUnavailableError,
    interpret_decision_contract,
    interpret_yes_no_decision,
    render_public_wire_text,
)


@dataclass
class PersonaApiConfig:
    base_url: str
    api_key: str
    model: str
    timeout: int = 120
    temperature: float = 0.9
    max_tokens: int = 400


class PersonaApiDriver:
    """`ParticipantDriver`-Implementierung fuer eine API-Persona
    (LiteLLM/OpenRouter, openai-kompatibles `/chat/completions`)."""

    def __init__(self, config: PersonaApiConfig, persona_key: str):
        self.config = config
        self.persona_key = persona_key
        self.request_count = 0

    def check_auth_configured(self) -> None:
        """Preflight OHNE Netzwerkaufruf: fehlender Key ist sofort sichtbar,
        bevor ein teurer Request versucht wird (A02/A15)."""
        if not self.config.api_key:
            raise ProviderAuthError(
                f"persona_api[{self.persona_key}]: kein API-Key konfiguriert — "
                f"kein Request ohne explizite Anmeldung."
            )
        if not self.config.base_url:
            raise ProviderAuthError(
                f"persona_api[{self.persona_key}]: keine base_url konfiguriert."
            )

    def decide(self, context: dict) -> ParticipantDecision:
        """`context` traegt mindestens `system` (State+erlaubte Raumhistorie,
        s. core/controller.py) und `user` (die eingehende Aufforderung).
        Budget-Reservierung VOR dem Request ist Aufgabe des Aufrufers
        (core/runtime.py) — dieser Adapter fuehrt nur den einzelnen Turn aus."""
        self.check_auth_configured()
        body = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": context.get("system", "")},
                {"role": "user", "content": render_public_wire_text(context)},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions",
            data=data, method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as r:
                resp = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", errors="replace")[:400]
            if e.code in (401, 403):
                raise ProviderAuthError(f"persona_api[{self.persona_key}]: HTTP {e.code}: {txt}") from e
            if e.code == 429:
                raise ProviderQuotaError(f"persona_api[{self.persona_key}]: HTTP 429 (Quota): {txt}") from e
            raise ProviderUnavailableError(f"persona_api[{self.persona_key}]: HTTP {e.code}: {txt}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            raise ProviderUnavailableError(f"persona_api[{self.persona_key}]: {e}") from e
        latency = time.time() - t0
        self.request_count += 1
        try:
            content = resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderUnavailableError(
                f"persona_api[{self.persona_key}]: unerwartete Response-Struktur: {json.dumps(resp)[:300]}"
            ) from e
        # I1 (MAIN-ENTSCHEIDUNG I1-Kontrollform): traegt der Aufrufer eine
        # `decision_contract`-Bindung (offer_id/participant_id, s.
        # `ui/tui.py` invite_ctx/lead_invite_ctx) im Kontext, ist DIES eine
        # Einladungs-/Leaderentscheidung -- die vollstaendig validierbare
        # Kontrollform ersetzt die alte lose Ja/Nein-Heuristik (Case 02:
        # ein Text ohne passende Kontrollform ist strukturell IMMER
        # invalid). Ohne `decision_contract` (normale Spielzug-Antworten)
        # bleibt das Feld unveraendert per loser Heuristik gesetzt -- es
        # wird dort von niemandem gelesen (nur die Einladungspfade in
        # `ui/tui.py` werten `.decision` aus).
        decision_contract = context.get("decision_contract")
        explanation = None
        if decision_contract:
            decision, explanation = interpret_decision_contract(
                content,
                offer_id=decision_contract.get("offer_id"),
                participant_id=decision_contract.get("participant_id"),
            )
        else:
            decision = interpret_yes_no_decision(content)
        return ParticipantDecision(
            text=content,
            origin_source=f"persona_api:{self.config.model}",
            meta={"usage": resp.get("usage") or {}, "latency_s": latency, "decision_explanation": explanation},
            decision=decision,
        )
