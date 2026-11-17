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
import math
import re
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


def _redact_secret_text(text: str, *secrets: str | None) -> str:
    """A5 (02_NACHARBEIT.md Gruppe A5, O1-D): entfernt bekannte Secretwerte
    (hier: `api_key`) aus einem Fehlertext, BEVOR er in eine Exception/
    Console/Save/Export uebernommen wird -- ein (ggf. absichtlich
    fehlerhaft antwortendes) Backend-Double kann einen formfalschen Body
    liefern, der den gesendeten `Authorization`-Header echot. Fehlertyp/
    HTTP-Status/Quota-Erkennung bleiben im Text UNVERAENDERT erhalten, nur
    der Geheimnisanteil wird ersetzt."""
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", redacted)


def _validate_persona_max_tokens(value: object) -> int:
    """R8-Fix (01 §"Materielle Restfehler", 02 Block D, O5-B): effektives
    `max_tokens` muss eine echte positive, endliche Ganzzahl sein -- `0`,
    negative Werte, `bool` (technisch eine `int`-Unterklasse), nicht
    endliche Werte (`inf`/`nan`) und Bruchwerte werden fail-closed
    abgelehnt, AUCH bei direkter `PersonaApiConfig`-Konstruktion (nicht nur
    ueber den Factory-Env-Parsepfad in `adapters.factories`). Identisches
    Muster zu `gm_owui._validate_gm_output_limit_tokens` (GM besitzt diesen
    Validator bereits), nur ohne dessen `None`-"unbegrenzt"-Fall -- Persona-
    `max_tokens` ist nie optional/unbegrenzt."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"PersonaApiConfig.max_tokens={value!r} ist keine gueltige Ganzzahl -- "
            "fail-closed, kein Versand mit ungueltigem Limit."
        )
    if isinstance(value, float):
        if not math.isfinite(value) or value != int(value):
            raise ValueError(
                f"PersonaApiConfig.max_tokens={value!r} ist kein endlicher Ganzzahlwert -- "
                "fail-closed, kein Versand mit ungueltigem Limit."
            )
        value = int(value)
    if value <= 0:
        raise ValueError(
            f"PersonaApiConfig.max_tokens={value!r} ist nicht positiv -- "
            "fail-closed, kein Versand mit ungueltigem Limit."
        )
    return value


@dataclass
class PersonaApiConfig:
    base_url: str
    api_key: str
    model: str
    timeout: int = 120
    temperature: float = 0.9
    max_tokens: int = 400
    # ZR-LOCAL-TOKENHOST-L1: instanz-/profilgebundener Billingmarker.
    # Clouddefault bleibt True (unveraendert); der lokale Tokenhost-Pfad
    # setzt diese EINE Config-Instanz explizit auf False (s.
    # `factories.py:default_persona_driver_factory`).
    is_dollar_billed: bool = True


class PersonaApiDriver:
    """`ParticipantDriver`-Implementierung fuer eine API-Persona
    (LiteLLM/OpenRouter, openai-kompatibles `/chat/completions`)."""

    # G2b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27): duck-typed
    # Markierung fuer `core.runtime`/`core.lobby_service` -- diese Rolle wird
    # standardmaessig ueber ein abgerechnetes API gesendet und bleibt deshalb
    # dollarbegrenzt (`admission.read_admission_block(..., dollar_billed=True)`,
    # Default). Reine Namens-/Attributpruefung, admission.py bleibt providerfrei.
    # ZR-LOCAL-TOKENHOST-L1: Klassenattribut bleibt als Fallback True; die
    # tatsaechlich wirksame Markierung ist jetzt INSTANZ-/profilgebunden
    # (s. `__init__` unten) -- `getattr(driver, "is_dollar_billed", True)`
    # (runtime.py/lobby_service.py/community_creation.py) liest zuerst die
    # Instanz, Cloud-Instanzen bleiben unveraendert True.
    is_dollar_billed = True

    def __init__(self, config: PersonaApiConfig, persona_key: str):
        # R8-Fix: validiert HIER (jeder Konstruktionsweg, auch eine direkte
        # Testkonstruktion ohne Factory), nicht erst lose in `decide()`.
        config.max_tokens = _validate_persona_max_tokens(config.max_tokens)
        self.config = config
        self.persona_key = persona_key
        self.request_count = 0
        self.is_dollar_billed = config.is_dollar_billed

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
            # R7-Fix (01 §"Materielle Restfehler", 02 Block D): zuerst
            # redigieren, DANN auf 400 Zeichen kuerzen -- die vorige
            # Reihenfolge (Kuerzung vor Redaktion) konnte einen Secretwert
            # exakt an der Kuerzungsgrenze zerschneiden; die Resttexthaelfte
            # ohne "Bearer "-Praefix matchte dann weder den exakten
            # Secretstring noch das Bearer-Regex und blieb sichtbar.
            txt = _redact_secret_text(e.read().decode("utf-8", errors="replace"), self.config.api_key)[:400]
            if e.code in (401, 403):
                raise ProviderAuthError(f"persona_api[{self.persona_key}]: HTTP {e.code}: {txt}") from None
            if e.code == 429:
                raise ProviderQuotaError(f"persona_api[{self.persona_key}]: HTTP 429 (Quota): {txt}") from None
            raise ProviderUnavailableError(f"persona_api[{self.persona_key}]: HTTP {e.code}: {txt}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            raise ProviderUnavailableError(
                f"persona_api[{self.persona_key}]: {_redact_secret_text(str(e), self.config.api_key)}"
            ) from None
        latency = time.time() - t0
        self.request_count += 1
        try:
            content = resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            # R7-Fix: dieselbe Redaktion-vor-Kuerzung-Reihenfolge wie oben --
            # vollen Responsetext redigieren, erst danach auf 300 Zeichen kuerzen.
            raise ProviderUnavailableError(
                f"persona_api[{self.persona_key}]: unerwartete Response-Struktur: "
                f"{_redact_secret_text(json.dumps(resp), self.config.api_key)[:300]}"
            ) from None
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
