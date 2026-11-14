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

import importlib
import os
from pathlib import Path


def _maybe_default_local_persona_api_env(repo_root: Path | None = None) -> None:
    """F1-N1 WP5b (PF3.persona): optionaler lokaler API-Default NUR fuer den
    TUI-Normalweg (`profile is None` -- der bewusst gewaehlte Persona-
    Einladepfad in `mmo_sim/ui/tui.py`, der diese Factory ueberhaupt erst
    aufruft; Solo ruft `factory()` nie auf und bleibt dadurch unberuehrt/
    persona-frei). Laeuft NUR, wenn WEDER `MMO_SIM_PERSONA_CLI` NOCH
    `MMO_SIM_PERSONA_API_BASE_URL` bereits gesetzt sind -- eine bewusste
    CLI/API-Wahl (frisch ODER aus einem frueheren Lauf via
    `~/.openwebui_env`/`_auto_load_owui_env()` schon ins Environment
    geladen) hat IMMER Vorrang und wird NIE ueberschrieben.

    Setzt bei Erfolg `MMO_SIM_PERSONA_API_BASE_URL/_KEY/_MODEL` auf die
    lokale LiteLLM-Route (dieselbe, die `setup.py:run_install_litellm`
    einrichtet) und persistiert sie erhaltend nach `~/.openwebui_env` ueber
    den bestehenden `setup._update_env_file_preserving`-Helfer (KEIN neuer
    Store) -- ein NEUER Prozess findet sie beim naechsten Lauf wieder.

    Ohne lokal eingerichtetes LiteLLM (keine `scripts/litellm/.env` mit
    Master-Key) oder bei nicht lesbarer `setup.json` ist dies ein stilles
    No-Op -- der bisherige klare Fehler ("Persona-Anbindung nicht
    konfiguriert") bleibt dann unveraendert. Reine Konfigurationspruefung:
    erzeugt KEINE Figur/Einladung/Zustimmung, Persoenlichkeits-/
    Einladungs-/Consent-Mechanik bleibt unberuehrt.

    `repo_root` ist NUR ein Test-Seam (Default `None` -> echter Repo-Root
    ueber `__file__` ermittelt); der Produktionsaufruf in `factory()` unten
    uebergibt nichts.

    WP-N2-2c: VOR dem Env-Check wird `setup._auto_load_owui_env()`
    aufgerufen, damit eine nur in `~/.openwebui_env` gespeicherte bewusste
    `MMO_SIM_PERSONA_CLI`/`_API_*`-Wahl sicher geladen ist, BEVOR hier
    ueber einen neuen API-Default entschieden wird -- unabhaengig davon, ob
    ein frueherer Aufruf im selben Prozess (z.B. `scripts/mmo_sim.py:
    _resolve_active_gm_route`) das schon erledigt hat. Fehlerfrei No-Op,
    wenn `setup` (noch) nicht importierbar ist (z.B. Test-Kontext ohne
    `scripts/`-sys.path)."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    try:
        import sys as _sys
        _scripts_dir = str(repo_root / "scripts")
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)
        import setup as _early_setup_module
        _early_setup_module._auto_load_owui_env()
    except Exception:
        pass

    if os.environ.get("MMO_SIM_PERSONA_CLI") or os.environ.get("MMO_SIM_PERSONA_API_BASE_URL"):
        return
    env_file = repo_root / "scripts" / "litellm" / ".env"
    if not env_file.is_file():
        return

    master_key = ""
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("LITELLM_MASTER_KEY="):
                master_key = line.split("=", 1)[1].strip()
                break
    except OSError:
        return
    if not master_key:
        return

    try:
        import json
        import sys
        scripts_dir = str(repo_root / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import setup as _setup_module
        # Bewusst NICHT `setup.load_config` (das verlangt volle setup.json-
        # Validierung inkl. `masterprompt`/`params`, die hier irrelevant
        # sind und bei Fehlen sys.exit(1) ausloesen wuerde) -- derselbe
        # schlanke Direkt-Read wie `scripts/mmo_sim.py:_resolve_active_gm_
        # route`, das aus demselben Grund ebenfalls an `load_config` vorbei
        # liest.
        cfg = json.loads((repo_root / "setup.json").read_text(encoding="utf-8"))
        routing_model = _setup_module._litellm_routing_model_id(repo_root, cfg)
        litellm_port = int((cfg.get("litellm") or {}).get("port", 4000))
    except Exception:
        return

    base_url = f"http://127.0.0.1:{litellm_port}/v1"
    os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = base_url
    os.environ["MMO_SIM_PERSONA_API_KEY"] = master_key
    os.environ["MMO_SIM_PERSONA_API_MODEL"] = routing_model

    try:
        home_env = Path.home() / ".openwebui_env"
        if not home_env.is_file():
            home_env.write_text("# Vom Launcher geschrieben - automatisch gelesen.\n", encoding="utf-8")
        _setup_module._update_env_file_preserving(home_env, {
            "MMO_SIM_PERSONA_API_BASE_URL": base_url,
            "MMO_SIM_PERSONA_API_KEY": master_key,
            "MMO_SIM_PERSONA_API_MODEL": routing_model,
        })
    except Exception:
        pass  # Persistierung ist best effort -- das Session-Env oben steht schon


def _maybe_default_local_tokenhost_persona_env(repo_root: Path | None = None) -> bool:
    """ZR-LOCAL-TOKENHOST-L1/N1-02: lokales Profil VOR dem bestehenden Cloud-/
    LiteLLM-Auto-Default (`_maybe_default_local_persona_api_env`) auflösen.
    Gibt True zurück, wenn ein bewusst gespeichertes lokales Profil
    (ZEITRISS_MODEL_PROVIDER=local) die Persona-Env gesetzt hat -- der
    Aufrufer `factory()` ueberspringt dann den alten LiteLLM-Default (keine
    doppelte profilabhängige Prioritätslogik, EIN Resolver). Bei 'hold'
    (unbekannter/inkonsistenter Provider ODER unvollstaendiges lokales
    Profil) wird sichtbar abgebrochen -- kein stiller Cloudfallback.

    N1-02-Fix: `MMO_SIM_PERSONA_CLI`/`_API_BASE_URL` koennen auf ZWEI Wegen
    schon im Prozess stehen, bevor diese Funktion laeuft:
      (a) ein echter, HIER im Prozess VOR diesem Aufruf gesetzter expliziter
          Override (z.B. Lab/CLI/Testsetup) -- der MUSS Vorrang behalten.
      (b) gespeicherter ALTBESTAND, den `setup._auto_load_owui_env()` selbst
          erst beim gleich folgenden Aufruf aus `~/.openwebui_env` in genau
          diese Variablen laedt (z.B. ein frueherer Cloud-/LiteLLM-Lauf) --
          das ist KEINE bewusste aktuelle Wahl und darf eine jetzt gespeicherte
          `provider=local`-Entscheidung NICHT still ueberstimmen.
    Nur (a) wird VOR dem Auto-Load geprueft (zu diesem Zeitpunkt kann (b)
    noch gar nicht im Environment stehen) -- widerspricht (a) einer
    aufgeloesten lokalen Wahl, haelt die Funktion sichtbar statt zu raten,
    welcher der beiden Werte gelten soll."""
    pre_existing_cli = os.environ.get("MMO_SIM_PERSONA_CLI")
    pre_existing_api = os.environ.get("MMO_SIM_PERSONA_API_BASE_URL")
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    try:
        import sys as _sys
        _scripts_dir = str(repo_root / "scripts")
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)
        import setup as _setup_module
    except Exception:
        return False
    if pre_existing_cli or pre_existing_api:
        # (a) echter Prozessoverride, bereits VOR dem Auto-Load gesetzt --
        # unveraendertes Altverhalten: hat Vorrang, kein Ueberschreiben.
        # Widerspricht er einer gleichzeitig aufgeloesten lokalen Wahl, haelt
        # die Funktion sichtbar statt den Override stillschweigend zu
        # ignorieren ODER die lokale Wahl stillschweigend zu verwerfen.
        try:
            _setup_module._auto_load_owui_env()
        except Exception:
            pass
        provider, _local_profile, hold_reason = _setup_module.resolve_model_provider()
        if provider == "hold":
            raise RuntimeError(
                f"Lokales Modell-Profil haelt: {hold_reason} -- kein automatischer "
                "Cloudfallback fuer die Persona-Anbindung."
            )
        if provider == "local":
            raise RuntimeError(
                "Lokales Modell-Profil ist 'local', aber ein bereits gesetzter expliziter "
                "Prozessoverride (MMO_SIM_PERSONA_CLI/_API_BASE_URL) widerspricht dem -- "
                "haelt sichtbar, kein automatisches Ueberschreiben in beide Richtungen."
            )
        return False
    try:
        _setup_module._auto_load_owui_env()
    except Exception:
        pass
    # (b) ab hier: KEIN echter Prozessoverride vor diesem Aufruf. Was
    # `_auto_load_owui_env()` gerade eben aus der Datei geladen haben
    # koennte (gespeicherter Altbestand), ist KEINE bewusste aktuelle Wahl
    # -- eine aufgeloeste 'local'-Entscheidung ueberschreibt es unten
    # bewusst (statt wie vorher sofort zurueckzukehren, weil die Variablen
    # schon "gesetzt" aussehen).
    provider, local_profile, hold_reason = _setup_module.resolve_model_provider()
    if provider == "hold":
        raise RuntimeError(
            f"Lokales Modell-Profil haelt: {hold_reason} -- kein automatischer "
            "Cloudfallback fuer die Persona-Anbindung."
        )
    if provider != "local":
        return False
    os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = local_profile.base_url
    os.environ["MMO_SIM_PERSONA_API_KEY"] = local_profile.api_key
    os.environ["MMO_SIM_PERSONA_API_MODEL"] = local_profile.model
    os.environ["MMO_SIM_PERSONA_API_MAX_TOKENS"] = str(local_profile.persona_max_tokens)
    os.environ["MMO_SIM_PERSONA_API_DOLLAR_BILLED"] = "0"
    return True


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
        if profile is None:
            # WP5b: nur am TUI-Normalweg, nur wenn noch keine bewusste
            # CLI/API-Wahl vorliegt (s. `_maybe_default_local_persona_api_env`-
            # Docstring). Lab (`profile` explizit gesetzt) bleibt unberuehrt --
            # dort validiert `lab/cli.py` die Env-Praesenz bereits vorab.
            # ZR-LOCAL-TOKENHOST-L1: lokales Profil hat Vorrang vor dem alten
            # LiteLLM-Auto-Default -- EIN Resolver, keine zweite Prioritaet.
            if not _maybe_default_local_tokenhost_persona_env():
                _maybe_default_local_persona_api_env()
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
            # ZR-LOCAL-TOKENHOST-L1: instanz-/profilgebundener Billingmarker
            # -- Clouddefault bleibt True (unveraendert), NUR wenn der lokale
            # Resolver oben MMO_SIM_PERSONA_API_DOLLAR_BILLED=0 gesetzt hat,
            # wird diese EINE Instanz als local_unpriced markiert.
            dollar_billed_raw = os.environ.get("MMO_SIM_PERSONA_API_DOLLAR_BILLED", "1").strip()
            config_kwargs: dict = dict(
                base_url=use_api,
                api_key=os.environ.get("MMO_SIM_PERSONA_API_KEY", ""),
                model=os.environ.get("MMO_SIM_PERSONA_API_MODEL", ""),
                is_dollar_billed=dollar_billed_raw not in ("0", "false", "False"),
            )
            raw_persona_max_tokens = os.environ.get("MMO_SIM_PERSONA_API_MAX_TOKENS")
            if raw_persona_max_tokens is not None and raw_persona_max_tokens.strip():
                try:
                    config_kwargs["max_tokens"] = int(raw_persona_max_tokens.strip())
                except ValueError:
                    raise ValueError(
                        f"MMO_SIM_PERSONA_API_MAX_TOKENS={raw_persona_max_tokens!r} ist nicht als "
                        "Zahl lesbar -- fail-closed, kein stiller Fallback auf den Default."
                    ) from None
            config = PersonaApiConfig(**config_kwargs)
            return PersonaApiDriver(config, persona_key)
        raise RuntimeError(
            "Persona-Anbindung nicht konfiguriert (weder MMO_SIM_PERSONA_CLI "
            "noch MMO_SIM_PERSONA_API_BASE_URL gesetzt) -- kein stiller "
            "Fallback, kein Persona-Spielstart (03 §1/§4)."
        )

    return factory


# F1-N1 WP5a (PF3.GM): Sentinel fuer "KB-Read versucht, aber fehlgeschlagen"
# (Auth-/Verbindungs-/Preset-Fehler TROTZ vorhandenem OWUI-Key), erzeugt von
# `scripts/mmo_sim.py:_resolve_active_gm_route` und hier als `kb_id`
# entgegengenommen. UNTERSCHEIDBAR von echtem `None` ("gar kein Key da, Read
# nie versucht") -- der echte "Key fehlt ganz"-Fall bleibt `None` und faellt
# weiterhin fail-closed in `sl_client.SLSession.__init__` (identisches
# Sentinel-Muster zu `launcher.py:KB_ID_MISSING`/`KB_ID_WEIRD`).
GM_ROUTE_KB_UNVERIFIED = "__gm_kb_unverified__"


def _load_gm_transport_double(spec: str):
    """FIX5 (R4 TEIL A, Grenzinjektions-Seam am GM-Transportrand): laedt
    die in `MMO_SIM_GM_TRANSPORT_DOUBLE` benannte `modul.pfad:callable`
    (dotted Modulpfad, per `importlib.import_module` -- das Double lebt in
    der TESTDATEI, nicht im Produkt, und muss daher ein importierbares
    Modul sein, kein `GmOwuiTransport`-interner Dateipfadtrick). Fail-closed
    bei falscher Form/fehlendem Modul/fehlendem Attribut -- kein stiller
    Fallback auf den Live-Transport."""
    module_path, sep, callable_name = spec.partition(":")
    if not sep or not module_path or not callable_name:
        raise ValueError(
            f"MMO_SIM_GM_TRANSPORT_DOUBLE={spec!r} ist nicht als 'modul.pfad:callable' lesbar -- "
            "fail-closed, kein stiller Fallback auf den Live-Transport (TEST-/GRENZINJEKTIONS-Seam)."
        )
    module = importlib.import_module(module_path)
    try:
        return getattr(module, callable_name)
    except AttributeError:
        raise ValueError(
            f"MMO_SIM_GM_TRANSPORT_DOUBLE={spec!r}: Modul {module_path!r} hat kein Attribut "
            f"{callable_name!r} -- fail-closed, kein stiller Fallback auf den Live-Transport."
        ) from None


def default_gm_transport_factory(
    data_dir: Path, repo_root: Path,
    sl_model: str | None = None, kb_id: str | None = None,
):
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
    von `GmOwuiTransport` nie gesetzt hat.

    FIX5 (R4 TEIL A, 02_NACHWEISE_UND_RUECKGABE.md §1, GUEST-OPERATOR.md
    R3-Lehre "keine direkt konstruierten Sessions"): additiv/optional
    (env-gated, Default unveraendert `None`/nicht gesetzt) -- der ECHTE
    Launcher-Subprozess (`scripts/mmo_sim.py`) hatte bisher KEINE
    sanktionierte Stelle, an der ein Evidence-Treiber einen deterministischen
    Anbieter-Double am GM-Rand einhaengen kann; R3 musste deshalb Sessions
    direkt konstruieren statt den echten Launcher zu nutzen. Ist
    `MMO_SIM_GM_TRANSPORT_DOUBLE` gesetzt, liefert `factory(table_id)` das
    Ergebnis der darin benannten lokalen Factory (s.
    `_load_gm_transport_double`) statt eines echten `GmOwuiTransport` --
    der Double selbst lebt in der TESTDATEI, nicht hier. OHNE die
    env-Variable bleibt JEDER bestehende Aufrufer (TUI/Lab, jeder
    bestehende Test) bytegleich beim Live-Transport unten.

    F1-3 (03_F1_AUFTRAG.md §F1-3 "gespeicherte Werte muessen bei den
    tatsaechlich verwendeten GM-/Persona-Factories ankommen"): `sl_model`/
    `kb_id` sind additiv und OPTIONAL (Default `None`, identisches Muster zu
    den W51/W56-Parametern oben) -- VORHER wurden beide Werte von dieser
    Factory nie an `GmOwuiTransport` durchgereicht, obwohl dessen Konstruktor
    sie bereits entgegennahm. Ohne Angabe fiel `agent_mp/sl_client.py` auf
    seine eigenen HARTKODIERTEN Werte zurueck (`SL_MODEL="zeitriss-v426-
    uncut"`, `KB_ID` einer spezifischen alten Installation) -- fuer die
    Standardvariante "sonnet" traf der Modellname zufaellig, die Knowledge-
    Base-ID NIE (jede frische `setup.py`-Installation legt eine neue, andere
    KB an). Der Aufrufer (`scripts/mmo_sim.py`) ermittelt die tatsaechlich
    konfigurierte Preset-ID/KB-ID live gegen die lokale OpenWebUI-Instanz und
    uebergibt sie hier; ohne Angabe bleibt das bisherige Altverhalten
    (sl_client.py-Defaults) unveraendert."""

    def factory(table_id: str):
        # TEST-/GRENZINJEKTIONS-Seam (02 §1): NUR aktiv, wenn
        # MMO_SIM_GM_TRANSPORT_DOUBLE gesetzt ist; fuehrt die benannte
        # lokale Factory aus; kein Live-/Netz-/Produktionspfad. MUSS vor dem
        # WP5a-Block unten bleiben -- ein Test-Double ersetzt den Live-
        # Transport vollstaendig und darf nicht am (fuer den Double
        # irrelevanten) `kb_id`-Sentinel scheitern.
        double_spec = os.environ.get("MMO_SIM_GM_TRANSPORT_DOUBLE")
        if double_spec:
            return _load_gm_transport_double(double_spec)(table_id)
        # F1-N1 WP5a (PF3.GM): bei NICHT verlaesslich aufgeloester KB (Read
        # fehlgeschlagen trotz Key) KEINEN Live-Transport mit diesem
        # Sentinel als `kb_id` bauen -- `GmOwuiTransport`/`sl_client.py`
        # wuerden sonst (`kb_id or KB_ID`) auf die hartkodierte HISTORISCHE
        # KB_ID einer alten Installation zurueckfallen. Wirft ERST hier, bei
        # tatsaechlichem produktivem Transportbau -- Programmstart/lokales
        # Menue bleiben unberuehrt (diese Factory wird nur bei echtem
        # `.turn()`-Aufruf ausgefuehrt). F1-N2 WP-N2-2a: derselbe Sentinel
        # deckt jetzt auch "setup.json fehlt/unlesbar/keine Preset-ID" ab
        # (`sl_model` dann `None`) -- die Meldung unterscheidet beide
        # Ursachen, statt pauschal "Auth/Verbindung/Preset" zu behaupten.
        if kb_id == GM_ROUTE_KB_UNVERIFIED:
            if sl_model is None:
                raise RuntimeError(
                    "GM-Route nicht verlaesslich aufgeloest: keine eigene Preset-/"
                    "Modell-Konfiguration gefunden (setup.json fehlt, ist nicht "
                    "lesbar, oder die Default-Variante hat keine Preset-ID).\n"
                    "  Naechster Schritt: Menue [1] Komplett-Setup bzw. [6] "
                    "Diagnose, dann erneut versuchen.\n"
                    "  Kein automatischer Ruckfall auf eine evtl. fremde/alte "
                    "Knowledge Base."
                )
            raise RuntimeError(
                "GM-Route nicht verlaesslich aufgeloest: Live-Pruefung von "
                f"Preset '{sl_model}' / Knowledge-Base ist fehlgeschlagen "
                "(Auth/Verbindung/Preset), obwohl ein OpenWebUI-Key vorhanden ist.\n"
                "  Naechster Schritt: Menue [6] Diagnose bzw. [5] API-Keys "
                "aendern, dann erneut versuchen.\n"
                "  Kein automatischer Ruckfall auf eine evtl. fremde/alte "
                "Knowledge Base."
            )
        from .gm_owui import GmOwuiTransport
        sl_client_path = repo_root / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"

        # ZR-LOCAL-TOKENHOST-L1: lokales Profil vor dem Billing-/Limit-
        # Default aufloesen -- EIN Resolver (`setup.resolve_model_provider`,
        # auch von `launcher.py`/`_maybe_default_local_tokenhost_persona_env`
        # genutzt). 'hold' haelt sichtbar, kein stiller Cloudfallback.
        gm_is_dollar_billed = True
        local_gm_profile = None
        try:
            import sys as _sys
            _scripts_dir = str(repo_root / "scripts")
            if _scripts_dir not in _sys.path:
                _sys.path.insert(0, _scripts_dir)
            import setup as _setup_module_gm
            _gm_provider, local_gm_profile, _gm_hold_reason = _setup_module_gm.resolve_model_provider()
        except ImportError:
            _gm_provider, _gm_hold_reason = "legacy", None
        if _gm_provider == "hold":
            raise RuntimeError(
                f"GM-Route haelt: lokales Modell-Profil ungueltig/inkonsistent ({_gm_hold_reason}) "
                "-- kein automatischer Cloudfallback."
            )
        if _gm_provider == "local":
            # N1-02 (O2 "Falsches Cloudpreset bei Localwahl darf keine
            # Completion mit dollar_billed=False freigeben"): eine lokale
            # Envwahl allein bindet den tatsaechlichen Upstream NICHT -- das
            # Preset (`sl_model`, bereits live aufgeloest/bestaetigt in
            # `scripts/mmo_sim.py:_resolve_active_gm_route`, s. Aufrufer)
            # koennte noch auf ein Cloud-/LiteLLM-Routing-Modell zeigen
            # (Rewire fehlgeschlagen/ausstehend). Nichtgenerativer GET (KEIN
            # `APIClient.test_model`) bestaetigt `base_model_id` GENAU hier,
            # unmittelbar vor dem Transportbau -- nur bei bestaetigter
            # Bindung wird der Dollargate umgangen; sonst sichtbarer Halt,
            # kein stiller Cloudversand mit lokaler Billingmarkierung.
            if sl_model is None or sl_model == GM_ROUTE_KB_UNVERIFIED:
                raise RuntimeError(
                    "GM-Route haelt: lokales Modell-Profil ist 'local', aber kein eigenes "
                    "Preset verlaesslich aufgeloest -- kein automatischer Versand mit "
                    "lokaler Billingmarkierung."
                )
            try:
                _setup_module_gm._auto_load_owui_env()
            except Exception:
                pass
            _gm_owui_url = os.environ.get("OPENWEBUI_URL") or "http://localhost:8080"
            _gm_owui_key = os.environ.get("OPENWEBUI_API_KEY", "").strip()
            if not _gm_owui_key:
                raise RuntimeError(
                    "GM-Route haelt: kein OPENWEBUI_API_KEY zur Bestaetigung des lokalen "
                    "Upstreams -- kein automatischer Versand mit lokaler Billingmarkierung."
                )
            try:
                _gm_bound_preset = _setup_module_gm.APIClient(_gm_owui_url, _gm_owui_key).get_model(sl_model)
            except Exception as _bind_exc:
                raise RuntimeError(
                    f"GM-Route haelt: lokaler Upstream von Preset '{sl_model}' nicht bestaetigbar "
                    f"({_bind_exc.__class__.__name__}: {_bind_exc})."
                ) from _bind_exc
            if not isinstance(_gm_bound_preset, dict) or _gm_bound_preset.get("base_model_id") != local_gm_profile.model:
                raise RuntimeError(
                    f"GM-Route haelt: Preset '{sl_model}' zeigt (noch) nicht bestaetigt auf den "
                    f"lokalen Upstream '{local_gm_profile.model}' -- kein automatischer Versand "
                    "mit lokaler Billingmarkierung."
                )
            gm_is_dollar_billed = False

        raw_limit = os.environ.get("MMO_SIM_GM_OUTPUT_LIMIT_TOKENS")
        gm_output_limit_tokens: float | None = None
        if raw_limit is not None and raw_limit.strip():
            # Vorhandene explizite Grenze hat IMMER Vorrang (02: "vorhandene
            # strengere explizite GM-Grenze erhalten").
            try:
                gm_output_limit_tokens = float(raw_limit.strip())
            except ValueError:
                raise ValueError(
                    f"MMO_SIM_GM_OUTPUT_LIMIT_TOKENS={raw_limit!r} ist nicht als Zahl lesbar -- "
                    f"fail-closed, kein stiller Fallback auf unbegrenzt (B2)."
                ) from None
        elif _gm_provider == "local" and local_gm_profile is not None:
            # Lokaler Startwert (02: 4096) statt stillem Fallback auf
            # unbegrenzt -- nur wirksam, wenn keine explizite Grenze gesetzt ist.
            gm_output_limit_tokens = float(local_gm_profile.gm_max_tokens)

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
            sl_model=sl_model, kb_id=kb_id,
            gm_output_limit_tokens=gm_output_limit_tokens,
            transport_max_retries=transport_max_retries,
            transport_backoff=transport_backoff,
            transport_timeout=transport_timeout,
            is_dollar_billed=gm_is_dollar_billed,
        )

    return factory
