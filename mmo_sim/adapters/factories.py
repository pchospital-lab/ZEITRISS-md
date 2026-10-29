#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mmo_sim/adapters/factories.py — gemeinsame Adapterfactories fuer TUI UND
Lab (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, H-B).

Aus `scripts/mmo_sim.py` extrahiert (vorher dort als
`_default_persona_driver_factory`/`_default_gm_transport_factory` lokal
definiert, NUR vom TUI-Zweig genutzt). `scripts/mmo_sim.py:main` UND
`mmo_sim/lab/cli.py` importieren jetzt DIESELBEN zwei Funktionen -- keine
zweite Anbieter-/Login-Implementierung, kein Verhaltensunterschied zwischen
TUI- und Lab-Start (ANSCHLUSSPLAN-HEADLESS.md: "vorhandene Adapterfactories
wiederverwenden")."""
from __future__ import annotations

import os
from pathlib import Path


def default_persona_driver_factory(data_dir: Path, profile: str | None = None):
    """Unveraendert aus `scripts/mmo_sim.py` uebernommen (A1, s. dortiger
    frueherer Docstring) FUER `profile=None` (TUI-Normalweg, H01 unveraendert):
    waehlt je nach Umgebungskonfiguration entweder das Hybrid-Profil
    (`claude_code_local`, `MMO_SIM_PERSONA_CLI` gesetzt) oder das API-Profil
    (`openai_compatible`, `MMO_SIM_PERSONA_API_*` gesetzt). Ohne eine der
    beiden Konfigurationen wirft die Konstruktion eine klare Fehlermeldung --
    kein stiller Fallback.

    G2a (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, REVIEW-HEADLESS-
    BETRIEBSGRENZEN.md Probe 03): `profile` ("api"/"hybrid", von `lab/cli.py`
    IMMER gesetzt) bindet das gewaehlte Profil VERBINDLICH an den
    tatsaechlich konstruierten Adapter -- die alte Env-Prioritaetslogik
    (CLI bevorzugt, sonst API, UNABHAENGIG vom gewaehlten Profil) liess einen
    `--profile hybrid`-Lauf mit nur konfiguriertem API-Env trotzdem eine
    ECHTE API-Personaanfrage senden. Mit gesetztem `profile` wird NUR NOCH
    das dazu passende Env gelesen; das jeweils andere Env wird nicht mehr
    als Fallback konsultiert (kein Env-Prioritaets-Silent-Switch, kein
    API-Fallback bei CLI-Fehler, H-E). `lab/cli.py:_run_controller` validiert
    die noetige Env-Praesenz bereits VOR jeder Bestandsmutation (LabConfigError)
    -- ein Fehlschlag HIER (fehlendes Env fuer das gewaehlte Profil) ist der
    defensive zweite Schutzring an der tatsaechlichen Konstruktionsstelle."""

    def factory(persona_key: str):
        cli_binary = os.environ.get("MMO_SIM_PERSONA_CLI")
        api_base_url = os.environ.get("MMO_SIM_PERSONA_API_BASE_URL")
        use_cli = cli_binary if profile is None else (cli_binary if profile == "hybrid" else None)
        use_api = api_base_url if profile is None else (api_base_url if profile == "api" else None)
        if profile == "hybrid" and not cli_binary:
            raise RuntimeError(
                "Profil 'hybrid' erfordert MMO_SIM_PERSONA_CLI -- kein stiller Fallback auf "
                "MMO_SIM_PERSONA_API_BASE_URL (G2a: gewaehltes Profil bindet den tatsaechlichen "
                "Adapter verbindlich)."
            )
        if profile == "api" and not api_base_url:
            raise RuntimeError(
                "Profil 'api' erfordert MMO_SIM_PERSONA_API_BASE_URL -- kein stiller Fallback "
                "auf MMO_SIM_PERSONA_CLI (G2a: gewaehltes Profil bindet den tatsaechlichen "
                "Adapter verbindlich)."
            )
        if use_cli:
            from .persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver
            isolated_workdir = os.environ.get("MMO_SIM_PERSONA_ISOLATED_WORKDIR") or str(data_dir / "persona_workdir")
            Path(isolated_workdir).mkdir(parents=True, exist_ok=True)
            extra_flags_raw = os.environ.get("MMO_SIM_PERSONA_ISOLATION_FLAGS", "")
            extra_flags = [f for f in extra_flags_raw.split(",") if f]
            # N2R5-TIMEOUTFIX (ZR-N2R-ANSCHLUSS-20261019-R4): additiv/optional,
            # identisches Muster zu `MMO_SIM_GM_TRANSPORT_MAX_RETRIES` unten --
            # Default `None`/unveraendert, ohne Angabe bleibt JEDER bestehende
            # Aufrufer beim bisherigen `ClaudeCodeConfig`-Default (120s/0
            # Retries). Schliesst den vorher offenen Fund, dass LAUNCH-SPEC
            # `timing.persona_timeout_seconds` bis hierher NIE ankam (der
            # reale Subprozess-Timeout blieb immer am hartverdrahteten
            # Default, unabhaengig vom konfigurierten Wert).
            config_kwargs: dict = {
                "binary": use_cli, "isolated_workdir": isolated_workdir,
                "extra_isolation_flags": extra_flags,
            }
            raw_timeout = os.environ.get("MMO_SIM_PERSONA_TIMEOUT_SECONDS")
            if raw_timeout is not None and raw_timeout.strip():
                try:
                    config_kwargs["process_timeout_seconds"] = int(float(raw_timeout.strip()))
                except ValueError:
                    raise ValueError(
                        f"MMO_SIM_PERSONA_TIMEOUT_SECONDS={raw_timeout!r} ist nicht als Zahl "
                        "lesbar -- fail-closed, kein stiller Fallback auf den Default."
                    ) from None
            raw_retries = os.environ.get("MMO_SIM_PERSONA_TIMEOUT_RETRIES")
            if raw_retries is not None and raw_retries.strip():
                try:
                    config_kwargs["max_timeout_retries"] = int(raw_retries.strip())
                except ValueError:
                    raise ValueError(
                        f"MMO_SIM_PERSONA_TIMEOUT_RETRIES={raw_retries!r} ist nicht als Zahl "
                        "lesbar -- fail-closed, kein stiller Fallback auf den Default."
                    ) from None
            config = ClaudeCodeConfig(**config_kwargs)
            return PersonaClaudeCodeDriver(config, persona_key)
        if use_api:
            from .persona_api import PersonaApiConfig, PersonaApiDriver
            config = PersonaApiConfig(
                base_url=use_api,
                api_key=os.environ.get("MMO_SIM_PERSONA_API_KEY", ""),
                model=os.environ.get("MMO_SIM_PERSONA_API_MODEL", ""),
            )
            return PersonaApiDriver(config, persona_key)
        raise RuntimeError(
            "Persona-Anbindung nicht konfiguriert (weder MMO_SIM_PERSONA_CLI "
            "noch MMO_SIM_PERSONA_API_BASE_URL gesetzt) -- kein stiller "
            "Fallback, kein Persona-Spielstart (03 §1/§4)."
        )

    return factory


def default_gm_transport_factory(data_dir: Path, repo_root: Path):
    """Unveraendert aus `scripts/mmo_sim.py` uebernommen (F5/K2/B2, s.
    dortiger frueherer Docstring): baut -- nur bei tatsaechlichem Aufruf --
    einen echten `GmOwuiTransport` gegen den bestehenden P1-SL-Client. Ohne
    live konfigurierte SL-Anbindung wirft die Konstruktion eine klare
    Fehlermeldung -- kein stiller Fallback, keine echte Inferenz bei blossem
    Programmstart oder Statusabfrage.

    W56 (SCOPE.json semantic_constraints.adapters "only explicit
    correction-context and per-run timeout/retry threading"; 03_LIVE3_
    FUENFER_UND_LAUFZEIT.md "hoechstens EIN Transportversuch je
    Liveaktion"): `MMO_SIM_GM_TRANSPORT_MAX_RETRIES`/`_BACKOFF`/`_TIMEOUT`
    sind additiv und OPTIONAL (Default `None`, identisches Muster zu
    `MMO_SIM_GM_OUTPUT_LIMIT_TOKENS` oben) -- ohne Angabe bleibt JEDER
    bestehende Aufrufer dieser Factory (TUI/Lab) unveraendert beim P1-Default
    des Harness-Clients (3 Versuche mit Backoff, `TIMEOUT_SL=420`). Ein
    LIVE3-Lauf setzt `MMO_SIM_GM_TRANSPORT_MAX_RETRIES=1` explizit, bevor
    diese FACTORY (nicht nur `GmOwuiTransport` isoliert) den Adapter baut --
    das schliesst die vorher offene Luecke, dass die tatsaechlich von
    TUI/Lab verwendete Default-Factory die additiven W51-Konstruktorparameter
    von `GmOwuiTransport` nie gesetzt hat."""

    def factory(table_id: str):
        from .gm_owui import GmOwuiTransport
        sl_client_path = repo_root / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"
        raw_limit = os.environ.get("MMO_SIM_GM_OUTPUT_LIMIT_TOKENS")
        gm_output_limit_tokens: float | None = None
        if raw_limit is not None and raw_limit.strip():
            try:
                gm_output_limit_tokens = float(raw_limit.strip())
            except ValueError:
                raise ValueError(
                    f"MMO_SIM_GM_OUTPUT_LIMIT_TOKENS={raw_limit!r} ist nicht als Zahl lesbar -- "
                    f"fail-closed, kein stiller Fallback auf unbegrenzt (B2)."
                ) from None

        def _optional_number(env_name: str, caster):
            raw = os.environ.get(env_name)
            if raw is None or not raw.strip():
                return None
            try:
                return caster(raw.strip())
            except ValueError:
                raise ValueError(
                    f"{env_name}={raw!r} ist nicht lesbar -- fail-closed, kein stiller "
                    f"Fallback auf den Harness-Client-Default (W56)."
                ) from None

        transport_max_retries = _optional_number("MMO_SIM_GM_TRANSPORT_MAX_RETRIES", int)
        transport_backoff = _optional_number("MMO_SIM_GM_TRANSPORT_BACKOFF", float)
        transport_timeout = _optional_number("MMO_SIM_GM_TRANSPORT_TIMEOUT", int)
        return GmOwuiTransport(
            sl_client_path, data_dir / "run", table_id=table_id,
            gm_output_limit_tokens=gm_output_limit_tokens,
            transport_max_retries=transport_max_retries,
            transport_backoff=transport_backoff,
            transport_timeout=transport_timeout,
        )

    return factory
