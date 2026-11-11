#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS MMO-Sim — TUI-Einstiegspunkt (analog `zeitriss.py`-Shim, P2 M3).

Duenner Shim: die eigentliche Terminal-Logik liegt in `mmo_sim/ui/tui.py`.
Aufruf: `python scripts/mmo_sim.py [--participant <id>]`.

Kein Browser fuers Spielen (11 §7). Ohne `--participant` wird — sofern unter
`--data-dir` bereits ein Teilnehmer bekannt ist — DIESER wiederverwendet
(P2-Fertigstellung I3, REVIEW-P2.md Test 07: "Normaler Neustart ohne
Sonderargument darf nicht neue Identitaet erzeugen"); nur beim allerersten
Lauf fuer ein `--data-dir` wird eine neue Teilnehmer-ID erzeugt.

Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27, H-B): ein FUEHRENDES
Subkommando `lab` (`python scripts/mmo_sim.py lab start|resume|status|stop|
attach ...`) delegiert VOR jeder TUI-/Teilnehmerlogik an
`mmo_sim.lab.cli.main` -- ein Aufruf OHNE dieses Subkommando bleibt exakt
die unveraenderte TUI (H01, kein impliziter Headless-Bootstrap)."""
from __future__ import annotations

import argparse
import json
import os
import select
import stat
import sys
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
# W6-Fix: beim Direktaufruf `python scripts/mmo_sim.py` traegt Python
# `scripts/` selbst als sys.path[0] ein, BEVOR dieser Code laeuft. War
# `_REPO_ROOT` durch PYTHONPATH bereits (an spaeterer Position) im Pfad,
# uebersprang die alte Pruefung ("not in sys.path") den insert(0) -- dann
# blieb `scripts/` vor dem Repo-Root, `import mmo_sim` fand diese Shim-Datei
# statt des echten Pakets `mmo_sim/` (identische Kollision wie in
# `scripts/mmo_sim_launcher_hook.py` dokumentiert: "'mmo_sim' is not a
# package"). Fix: Repo-Root IMMER an Position 0 erzwingen (bestehendes
# Vorkommen zuerst entfernen), unabhaengig davon, ob/wo es schon im Pfad war.
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

# F1-1 (03_F1_AUFTRAG.md §F1-1): bei Direktaufruf `python scripts/mmo_sim.py`
# (ohne den Starter `zeitriss.sh`/`scripts/zeitriss.py`) dieselbe private
# Projektumgebung sicherstellen wie der Starter -- sonst scheitert der
# gleich folgende Import von `mmo_sim.ui.tui` (transitiv `jsonschema`/
# `referencing`, s. `mmo_sim/domain/zeitriss/save_validation.py`) auf einem
# frischen Download ohne vorinstallierte Pakete mit einem rohen
# `ModuleNotFoundError`. Läuft der Prozess bereits in der venv (z.B. weil
# `zeitriss.py` schon dorthin gewechselt hat, bevor `[M]` diese Datei per
# Hook im selben Prozess lädt), ist der Aufruf ein No-Op.
#
# ACHTUNG Selbst-Kollision (identisch zum W6-Fix oben): ein
# `sys.path.insert(0, scripts/)` wuerde HIER erneut `scripts/` vor den
# Repo-Root schieben und `import mmo_sim` (gleich darunter) wieder an diese
# Shim-Datei statt an das echte Paket `mmo_sim/` binden. Deshalb wird
# `venv_bootstrap.py` per EXPLIZITEM Dateipfad geladen (analog
# `scripts/mmo_sim_launcher_hook.py:launch()`), ohne `sys.path` zu aendern.
import importlib.util as _importlib_util  # noqa: E402

_venv_bootstrap_spec = _importlib_util.spec_from_file_location(
    "zeitriss_venv_bootstrap", Path(__file__).resolve().parent / "venv_bootstrap.py",
)
_venv_bootstrap = _importlib_util.module_from_spec(_venv_bootstrap_spec)
_venv_bootstrap_spec.loader.exec_module(_venv_bootstrap)
_venv_bootstrap.ensure_running_in_project_venv(_REPO_ROOT)

from mmo_sim.core import identity  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402
from mmo_sim.adapters.base import (  # noqa: E402
    ProviderQuotaPausedError, quota_pause_is_rate_limited, quota_pause_player_message,
    quota_pause_reset_hint,
)
from mmo_sim.adapters.factories import (  # noqa: E402
    default_gm_transport_factory as _default_gm_transport_factory,
    default_persona_driver_factory as _default_persona_driver_factory,
    GM_ROUTE_KB_UNVERIFIED,
)

_LAST_PARTICIPANT_FILE = "last_participant.json"


def _resolve_participant_id(data_dir: Path, explicit: str | None) -> str:
    """I3/Test 07: ohne `--participant` wird die zuletzt fuer DIESES
    `--data-dir` verwendete Teilnehmer-ID wiederverwendet (Marker-Datei) --
    nicht bei jedem Start eine neue erzeugt. Eine explizit uebergebene
    `--participant`-ID aktualisiert den Marker (bewusster Wechsel).

    Fix C (ZR-SPIEL-S1, LINUS-SPEC §Fix C): eine ungueltige ID (weder die
    explizite noch die aus dem Marker gelesene) wird VOR jeder Marker-/
    Verzeichnismutation per `identity.validate_participant_id` abgewiesen --
    `identity.InvalidParticipantId` propagiert unveraendert, kein mkdir/
    Marker-Write, keine stille Ersatz-ID, der Bestand bleibt erhalten."""
    marker = data_dir / _LAST_PARTICIPANT_FILE
    if explicit:
        identity.validate_participant_id(explicit, source="explizit --participant")
        data_dir.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"participant_id": explicit}), encoding="utf-8")
        return explicit
    if marker.exists():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            pid = data.get("participant_id")
            if pid:
                identity.validate_participant_id(pid, source="gespeicherte last_participant.json")
                return pid
        except (OSError, json.JSONDecodeError):
            pass
    pid = identity.new_participant_id()
    data_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"participant_id": pid}), encoding="utf-8")
    return pid


def _foreign_active_lab_owner(data_dir: Path) -> int | None:
    """F1 (Critic-Nacharbeit, Bau-GO 2026-09-27, REVIEW-TEILSTAND.md §3,
    Fall 05): derselbe REIN LESENDE Guard-Baustein wie
    `TuiSession._lab_active_guard` (`active_lock_pid(..., exclude_pid=
    os.getpid())`), hier VOR dem fruehen `_resolve_participant_id`-Marker-
    Write in `main()` -- der einzige verbleibende ungewachte fruehschreibende
    Einstieg lag VOR der spaeteren Kommandosperre der einzelnen `n`/`i`/`c`-
    TUI-Befehle. `run_dir` folgt derselben Konvention wie die spaetere
    `TuiSession`-Konstruktion (`data_dir / \"run\"`)."""
    from mmo_sim.lab.runner import active_lock_pid
    return active_lock_pid(data_dir / "run", exclude_pid=os.getpid())


def _resolve_host_capable(explicit: bool | None) -> bool:
    """ZR-FIGURENREISE-TISCH-20261102-R1 Teilpaket B (design.md §2):
    explizite Herleitung von `TuiSession(host_capable=...)` -- BEWUSST NICHT
    aus `gm_transport_factory is not None` (beide Factory-Closures sind
    lazy, s. `mmo_sim/adapters/factories.py`: `default_gm_transport_
    factory`/`default_persona_driver_factory` liefern IMMER ein Callable,
    unabhaengig von echter Env-Konfiguration -- `is not None` beweist also
    NIE Hostfaehigkeit).

    Stattdessen eine EXPLIZITE, am Launcher getroffene Deploy-Entscheidung
    (`--host-capable`/`--no-host-capable`, sonst `MMO_SIM_HOST_CAPABLE`
    env, sonst Default `True`): 'Gastinstall' (design.md §2 'Wurzel A,
    kein Hoststack') ist ein SEPARATER Deploy-/Startkontext, der sich
    bewusst als Gast deklariert -- kein Sniffing lazy-konfigurierbarer
    Persona-/GM-Env (das wuerde einen echten Host, der z.B. nie Personas
    einlaedt und darum MMO_SIM_PERSONA_CLI/_API_BASE_URL nie setzt,
    faelschlich als Gast einordnen). Default `True` haelt JEDEN
    bestehenden Start (kein neues Flag/Env gesetzt) bytegleich beim
    bisherigen Hostverhalten."""
    if explicit is not None:
        return explicit
    raw = os.environ.get("MMO_SIM_HOST_CAPABLE")
    if raw is None or not raw.strip():
        return True
    return raw.strip().lower() not in ("0", "false", "no", "guest")


def _resolve_active_gm_route(repo_root: Path) -> tuple[str | None, str | None]:
    """F1-3 (03_F1_AUFTRAG.md §F1-3 "gespeicherte Werte muessen bei den
    tatsaechlich verwendeten GM-Factories ankommen"): ermittelt das wirklich
    konfigurierte SL-Modell (Preset-ID der `setup.json`-Standardvariante)
    und die live damit verknuepfte Knowledge-Base-ID, statt der in
    `agent_mp/sl_client.py` hartkodierten Werte eines alten Installs
    (`SL_MODEL="zeitriss-v426-uncut"`, feste `KB_ID`). Jede frische
    `setup.py`-Installation legt eine NEUE KB mit neuer ID an -- ohne diese
    Funktion griffe das Terminalspiel weiterhin auf die alte, fuer eine
    frische Installation falsche KB-ID zurueck.

    Reiner Config-Read ueber die bestehende `setup.py`-Infrastruktur
    (`APIClient.get_model`, `_auto_load_owui_env`) -- kein zweiter HTTP-
    Client, keine generative Modellanfrage (nur `GET /api/v1/models/model`).
    `_auto_load_owui_env()` laedt bei Bedarf `~/.openwebui_env`, damit das
    normale Terminalspiel kein manuelles `set -a; . ~/.openwebui_env; set +a`
    mehr braucht (vorher nur als Handanleitung in der Fehlermeldung von
    `sl_client.SLSession.__init__` dokumentiert).

    F1-N2 WP-N2-2a (501-Carve-out-Schliessung, vorher F1-N1 Red-Line
    "kein Harness-Umbau"): ein fehlender/unlesbarer `setup.json`-Stand oder
    eine fehlende Preset-ID liefert JETZT `(None, GM_ROUTE_KB_UNVERIFIED)`
    statt `(None, None)` -- ohne zuverlaessig bestimmte eigene Modell-/KB-
    Werte darf produktive GM-Nutzung NICHT still auf die in `sl_client.py`
    hartkodierten HISTORISCHEN Defaults (`SL_MODEL`/`KB_ID` einer alten
    Installation) zurueckfallen. Lokales Menue/Figurenverwaltung/
    Gastaktionen bleiben unberuehrt bedienbar -- der Sentinel wirkt erst bei
    echtem produktivem Transportbau (`default_gm_transport_factory`, NACH
    dem Test-Double-Seam-Check, s. factories.py), nicht beim Programmstart.
    Fehlt der OWUI-Key GANZ (`owui_key` leer), bleibt das UNVERAENDERT
    `(sl_model, None)` -- die eigentliche fail-closed-Fehlermeldung bei
    WIRKLICH fehlender SL-Anbindung bleibt weiterhin
    `sl_client.SLSession.__init__` (fehlender OPENWEBUI_API_KEY).

    F1-N1 WP5a (PF3.GM): schlaegt der KB-Read TROTZ vorhandenem Key fehl
    (Auth-/Verbindungsfehler, Preset fehlt, Preset ohne KB-Verknuepfung,
    ODER -- seit F1-N2 WP-N2-2a -- HTTP 501, s.u.), liefert diese Funktion
    `(sl_model, GM_ROUTE_KB_UNVERIFIED)` statt still `(sl_model, None)` --
    VORHER war das von einem echten "kein Key"-Fall nicht unterscheidbar,
    und das Wiring reichte `None` unveraendert an `GmOwuiTransport` durch,
    das dann (`kb_id or KB_ID`) auf die in `sl_client.py` hartkodierte
    HISTORISCHE Knowledge-Base einer alten Installation zurueckfiel -- ein
    fehlgeschlagener Read sah dadurch wie eine gueltige Route aus.
    `default_gm_transport_factory` (mmo_sim/adapters/factories.py) erkennt
    diesen Sentinel als `kb_id` und wirft NACH dem Test-Double-Seam-Check,
    aber VOR dem echten `GmOwuiTransport`-Bau -- sichtbar, aber erst bei
    echtem produktivem Gebrauch (`.turn()`), nicht beim Programmstart/
    Status. F1-N2 WP-N2-2a: die vorherige EINZIGE Ausnahme (HTTP 501 auf
    `GET /api/v1/models/model` blieb beim alten `(sl_model, None)`, weil die
    schlanken Fake-OWUI-Loopback-Server der E2E-Subprozess-Tests den
    Endpunkt nicht implementierten) ist ENTFERNT -- ein HTTP-Status
    identifiziert keinen Testprozess. Die betroffenen Fakes bekommen
    stattdessen ein minimales `do_GET` fuer diesen Endpunkt oder laufen ueber
    den expliziten `MMO_SIM_GM_TRANSPORT_DOUBLE`-Seam (s. Testdateien)."""
    try:
        import setup as _setup_module  # noqa: E402  (scripts/ bereits auf sys.path, s.o.)
    except ImportError:
        # WP-N2-2a: Umgebung/Install kaputt (scripts/ nicht importierbar) ->
        # eigene Modell-/KB-Werte nicht zuverlaessig bestimmbar. Sichtbar
        # ablehnen bei produktivem Transportbau statt still auf die
        # historischen sl_client.py-Defaults zu fallen (gleiche Sentinel-
        # Logik wie ein fehlgeschlagener Live-Read weiter unten).
        return None, GM_ROUTE_KB_UNVERIFIED

    try:
        cfg = json.loads((repo_root / "setup.json").read_text(encoding="utf-8"))
        default_variant = cfg.get("default_variant")
        variant = (cfg.get("variants") or {}).get(default_variant) or {}
        sl_model = variant.get("preset_id")
    except (OSError, json.JSONDecodeError, AttributeError):
        # WP-N2-2a: setup.json fehlt/unlesbar/kaputt -> dieselbe sichtbare
        # Ablehnung statt stillem Fallback auf die historische KB.
        return None, GM_ROUTE_KB_UNVERIFIED
    if not sl_model:
        # WP-N2-2a: keine Preset-ID fuer die Default-Variante konfiguriert
        # -> ebenfalls sichtbar ablehnen statt stillem Fallback.
        return None, GM_ROUTE_KB_UNVERIFIED

    try:
        _setup_module._auto_load_owui_env()
    except Exception:
        pass
    owui_key = os.environ.get("OPENWEBUI_API_KEY", "").strip()
    if not owui_key:
        # Echter "Key fehlt ganz"-Fall -- UNVERAENDERT. sl_client.__init__
        # faengt das weiterhin eigenstaendig fail-closed ab.
        return sl_model, None
    owui_url = os.environ.get("OPENWEBUI_URL") or "http://localhost:8080"

    import urllib.parse
    try:
        client = _setup_module.APIClient(owui_url, owui_key)
        # F1-N1 WP5a (PF3.GM, Main-Verfeinerung ggue. dem ersten Exception-
        # only-Stand): STATUS-bewusst statt `get_model` (das jeden Nicht-200
        # zu None kollabiert und damit "Auth/Preset fehlgeschlagen" von
        # "Server erreichbar, Preset ohne KB" ununterscheidbar macht).
        # `APIClient.get` liefert `(code, data)`; `_request` faengt HTTP-/
        # Verbindungsfehler intern ab (kein raise), der Code bleibt sichtbar.
        code, data = client.get(
            f"/api/v1/models/model?id={urllib.parse.quote(sl_model, safe='')}"
        )
    except Exception:
        # Unerwarteter Client-/Konstruktionsfehler TROTZ vorhandenem Key ->
        # unverifiziert, sichtbar ablehnen statt still auf historische KB.
        return sl_model, GM_ROUTE_KB_UNVERIFIED

    if code != 200 or not isinstance(data, dict):
        # Erreichbar/versucht, aber Auth (401/403), Preset fehlt (404),
        # unerreichbar (code 0), Endpunkt nicht implementiert (501 -- WP-
        # N2-2a: KEINE Produktausnahme mehr, ein HTTP-Status identifiziert
        # keinen Testprozess) oder unlesbar -> NICHT still auf die
        # historische hartkodierte KB ausweichen, sondern sichtbar ablehnen
        # (PF3.GM: "fehlgeschlagener Read darf nicht auf fremde historische
        # KB ausweichen" -- voll geschlossen, nicht nur der raise-Fall).
        return sl_model, GM_ROUTE_KB_UNVERIFIED

    preset = data
    kb_list = (preset.get("meta") or {}).get("knowledge")
    kb_id: str | None = None
    if isinstance(kb_list, list) and kb_list:
        first = kb_list[0]
        if isinstance(first, dict):
            kb_id = first.get("id")
        elif isinstance(first, str):
            kb_id = first
    if not kb_id:
        # Preset lesbar, aber KEIN gueltiger KB-Link -> ebenfalls nicht auf
        # die historische KB ausweichen (PF3.GM: "fehlender KB-Link").
        return sl_model, GM_ROUTE_KB_UNVERIFIED
    return sl_model, kb_id


def _ensure_fifo(path: Path) -> None:
    """R3 G1 (GUEST-OPERATOR.md B1 "fehlendes Produkt-Wiring"): legt die
    benannte Pipe fuer `--operator-control-fifo`/`--guest-terminal` an
    (`os.mkfifo`), falls sie noch nicht existiert -- existiert der Pfad
    bereits, wird NUR geprueft, dass es tatsaechlich eine FIFO ist (ehrlicher
    Abbruch statt stillem Fehlverhalten an einer normalen Datei)."""
    if path.exists():
        if not stat.S_ISFIFO(path.stat().st_mode):
            raise SystemExit(f"'{path}' existiert bereits und ist KEINE Named Pipe (FIFO).")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    os.mkfifo(path)


def _fifo_control_line_source(fifo_path: Path):
    """R3 G1: `TuiSession.operator_control_line_source` ueber eine GETRENNTE
    lokale Named Pipe statt des mit Spielzuegen geteilten stdin (GUEST-
    OPERATOR.md B1 "Eingaberouting-Kollision") -- dieselbe nicht-blockierende
    select()-Backoff-Struktur wie das bestehende `ui/tui.py:_OperatorControl
    Scope._default_line_source` (0.2s, kein Busy-Spin), nur mit der FIFO statt
    `sys.stdin` als Quelle. Lazy geoeffnet (`O_NONBLOCK`) beim ERSTEN Aufruf
    (nicht beim Launcherstart) -- blockiert den Start nicht, falls der
    Betreiber die Schreibseite der Pipe erst spaeter oeffnet."""
    state: dict = {"file": None}

    def _source(stop_event) -> str | None:
        if stop_event.is_set():
            return None
        if state["file"] is None:
            fd = os.open(str(fifo_path), os.O_RDONLY | os.O_NONBLOCK)
            state["file"] = os.fdopen(fd, "r")
        f = state["file"]
        try:
            ready, _, _ = select.select([f], [], [], 0.2)
        except (OSError, ValueError):
            stop_event.wait(0.2)
            return None
        if not ready:
            return None
        try:
            line = f.readline()
        except (OSError, ValueError):
            return None
        if line == "":
            # Kein Schreiber (noch) angeschlossen -- derselbe EOF-Backoff
            # wie `_default_line_source` bei geschlossenem stdin, kein
            # Heisslauf.
            stop_event.wait(0.2)
            return None
        return line

    return _source


class _FifoInputReader:
    """R3 G1 + R4 FIX6 (ZR-BETREIBER-GASTERSCHAFFUNG-20261104-R4, "Keine
    konkurrierenden Leser desselben Eingabekanals"): `input_fn` (ueber
    `read_line`) fuer eine getrennte Gast-Client-`TuiSession`
    (`--guest-terminal`) -- liest Zeilen aus `<in_fifo>` BLOCKIEREND, exakt
    wie echtes Terminal-stdin dieses Gastes. Lazy geoeffnet beim ERSTEN
    Aufruf (`_ensure_open`, geteilt von `read_line` UND `ready` -- EIN
    offenes Dateiobjekt, kein zweiter Oeffnungsversuch), kein Launcher-Hang,
    falls der menschliche Gast seine Pipenseite erst spaeter oeffnet. Ein
    geschlossenes Schreibende (EOF) wird als `EOFError` gemeldet -- derselbe
    Vertrag wie das eingebaute `input()` (`TuiSession._readline` faengt das
    bereits in `EndOfInput` um).

    R4 FIX6 ergaenzt `ready(timeout)`: ein NICHT-KONSUMIERENDER
    Bereitschafts-Check (reines `select.select` auf demselben, bereits
    geoeffneten Dateiobjekt -- liest NICHTS, verschiebt die Leseposition
    NICHT) -- `TuiSession._readline_guest_menu` nutzt dies, um VOR jedem
    tatsaechlichen Konsum zu pruefen, ob eine Zeile wartet, OHNE sie dem
    parallel moeglichen host-getriebenen Round-Reader (`_HumanDriver.
    decide`) wegzuschnappen (s. dortiger Claim-Mechanismus)."""

    def __init__(self, fifo_path: Path, echo_fn=None):
        self._path = fifo_path
        self._file = None
        # N1 (ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261106-R2): optionaler
        # Ausgabe-Rueckkanal (`print_fn` des Gast-Terminals), damit
        # `read_line` den Prompt im zustaendigen Gast-ANZEIGEkanal sichtbar
        # machen kann -- exakt wie das eingebaute `input(prompt)` den Prompt
        # am Host-stdout zeigt. `None` -> kein Echo (bytegleich fuer jeden
        # Alt-Aufrufer, s. `_fifo_input_fn`).
        self._echo_fn = echo_fn

    def _ensure_open(self) -> None:
        if self._file is None:
            self._file = open(self._path, "r", encoding="utf-8")

    def ready(self, timeout: float) -> bool:
        self._ensure_open()
        try:
            readable, _, _ = select.select([self._file], [], [], timeout)
        except (OSError, ValueError):
            return False
        return bool(readable)

    def read_line(self, prompt: str = "") -> str:
        self._ensure_open()
        # N1-FIX (R2): die tatsaechliche Frage/Aufforderung VOR dem
        # blockierenden Lesen EINMAL sichtbar im Gast-Ausgabekanal
        # ausgeben + flushen. Ohne dies wartete der angeschlossene Gast auf
        # eine Antwort zu einer nie eingeblendeten Frage (Beitritt/Consent
        # TUI 7466-7468, Importbestaetigung TUI 3898-3900, Menue-/Auswahl-/
        # Bestaetigungsprompts). Leerer Prompt -> kein Echo (interne Reads
        # ohne Fragetext bleiben stumm). Kein zweiter Oeffnungsversuch der
        # out-FIFO: `echo_fn` IST das `print_fn`-Closure derselben
        # TuiSession, teilt also dasselbe lazy geoeffnete Dateiobjekt.
        if prompt and self._echo_fn is not None:
            self._echo_fn(prompt)
        line = self._file.readline()
        if line == "":
            raise EOFError(f"Gast-Terminal-FIFO '{self._path}' geschlossen (EOF).")
        return line.rstrip("\n")


def _fifo_input_fn(fifo_path: Path):
    """Rueckwaerts-kompatibler duenner Wrapper um `_FifoInputReader.
    read_line` -- unveraenderter Vertrag/Name fuer bestehende Aufrufer, die
    NUR den konsumierenden `input_fn` brauchen (z.B. `tests/mmo_sim/
    drive_r3_g5_evidence_2026_11_04.py`, kein FIX6-Claim-Szenario dort,
    daher kein `ready`-Bedarf). `main()` unten konstruiert fuer
    `--guest-terminal` stattdessen DIREKT einen `_FifoInputReader`, damit
    `read_line` UND `ready` dasselbe Dateiobjekt teilen (s. Klassen-
    Docstring)."""
    return _FifoInputReader(fifo_path).read_line


def _fifo_print_fn(fifo_path: Path):
    """R3 G1: `print_fn` fuer eine getrennte Gast-Client-`TuiSession`
    (`--guest-terminal`) -- schreibt nach `<out_fifo>`. `O_RDWR`-geoeffnet
    (POSIX-Trick fuer benannte Pipes): das Oeffnen selbst blockiert dadurch
    NICHT darauf, dass bereits ein Leser angeschlossen ist. Das eigentliche
    Schreiben bleibt unveraendert blockierend, sobald der Pipe-Puffer ohne
    Leser vollliefe -- identisch zu echtem Terminal-Output an einen (noch)
    nicht lesenden Client, kein stilles Verwerfen von Ausgaben."""
    state: dict = {"file": None}

    def _fn(text: str) -> None:
        if state["file"] is None:
            fd = os.open(str(fifo_path), os.O_RDWR)
            state["file"] = os.fdopen(fd, "w", encoding="utf-8")
        state["file"].write(text + "\n")
        state["file"].flush()

    return _fn


def _parse_guest_terminal_spec(spec: str) -> tuple[str, Path, Path]:
    """R3 G1: parst `--guest-terminal <guest_id>:<in_fifo>:<out_fifo>` --
    genau 3 durch ':' getrennte Teile, ehrlicher Abbruch bei falscher Form
    statt stillem Fehlstart."""
    parts = spec.split(":")
    if len(parts) != 3 or not all(parts):
        raise SystemExit(
            f"--guest-terminal erwartet '<guest_id>:<in_fifo>:<out_fifo>', bekommen: {spec!r}"
        )
    guest_id, in_fifo, out_fifo = parts
    return guest_id, Path(in_fifo), Path(out_fifo)


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if raw_argv and raw_argv[0] == "report":
        from mmo_sim.reports.report import main as report_main
        return report_main(raw_argv[1:], repo_root=_REPO_ROOT)
    # H-B (Bau-GO 2026-09-27): fuehrendes Subkommando 'lab' delegiert VOR
    # jeder Teilnehmerausloesung/TUI-Konstruktion -- 0 Modellcalls, keine
    # Marker-/Communitydateien fuer 'lab status'/'lab attach'/'--help'/eine
    # abgelehnte Fehlkonfiguration (H01). Ein Aufruf OHNE 'lab' bleibt exakt
    # die bisherige TUI (unveraendert ab hier).
    if raw_argv and raw_argv[0] == "lab":
        from mmo_sim.lab.cli import main as lab_main
        return lab_main(raw_argv[1:], repo_root=_REPO_ROOT)

    # R8-Nachzug (01_NACHZUG.md R8-4, PRODUKTFOCUS-LINUX-MINT.md "Spieler
    # oeffnet ZEITRISS bzw. das Terminalspiel"): sichtbare CLI-Beschreibung
    # fuer die Rolle, die dieses Skript tatsaechlich direkt aufruft (Spieler
    # per Setupguide ODER Entwickler), nicht der interne Entwicklerbegriff
    # "MMO-Sim" allein.
    parser = argparse.ArgumentParser(description="ZEITRISS — Terminalspiel (Terminaloberflaeche)")
    parser.add_argument("--participant", default=None, help="bestehende Teilnehmer-ID (sonst wird die zuletzt genutzte wiederverwendet bzw. beim allerersten Lauf eine neue erzeugt)")
    parser.add_argument("--data-dir", default=str(_REPO_ROOT / "internal" / "mmo_sim_data"),
                         help="Datenverzeichnis fuer Onboarding-/Katalog-Journale")
    # R3 G1 (GUEST-OPERATOR.md B2 "Launcher laesst alle privaten und
    # Betriebswurzeln gemeinsam aus einem einzigen --data-dir entstehen"):
    # additive, EINZELN ueberschreibbare Wurzeln -- Default `None` -> wie
    # bisher aus `--data-dir` abgeleitet (bytegleicher Start ohne diese
    # Flags). Erlaubt einem Gast einen GENUINELY getrennten privaten
    # Onboarding-/Katalogbestand (eigenes `--data-dir`) zu behalten, waehrend
    # er fuer Tischanfragen/-admission dieselbe GETEILTE `run_dir`/
    # `states_dir` des Anbieters benutzt (die Autoritaet, unter der
    # `table_admission`/`creation_grants` tatsaechlich entscheiden) -- ohne
    # dafuer das gesamte `--data-dir` (und damit auch die private
    # Onboarding-/Katalogwurzel) mit dem Anbieter teilen zu muessen.
    parser.add_argument(
        "--run-dir", default=None, metavar="PFAD",
        help="ueberschreibt die Lauf-/Admissionswurzel einzeln (Default: '<data-dir>/run') -- "
             "z.B. fuer einen Gast, der dieselbe geteilte Anbieter-run_dir benutzt wie der Host, "
             "aber eine eigene private '--data-dir' fuer Onboarding/Katalog behaelt.",
    )
    parser.add_argument(
        "--states-dir", default=None, metavar="PFAD",
        help="ueberschreibt die Persona-State-Wurzel einzeln (Default: '<data-dir>/states').",
    )
    # ZR-FIGURENREISE-TISCH-20261102-R1 Teilpaket B (design.md §2): explizite
    # Deploy-Entscheidung, s. `_resolve_host_capable`-Docstring -- Default
    # `None` (weder Flag gesetzt) faellt auf `MMO_SIM_HOST_CAPABLE`-Env,
    # sonst auf `True` zurueck (bytegleich zu jedem bestehenden Start).
    host_capable_group = parser.add_mutually_exclusive_group()
    host_capable_group.add_argument(
        "--host-capable", dest="host_capable", action="store_true", default=None,
        help="diese Installation besitzt einen echten Hoststack (Default, sofern MMO_SIM_HOST_CAPABLE nicht anders gesetzt ist)",
    )
    host_capable_group.add_argument(
        "--no-host-capable", dest="host_capable", action="store_false",
        help="Gastinstall ohne Hoststack (Wurzel A, design.md §2) -- nur eigene Figur verwalten/Tische anfragen/spielen nach Annahme",
    )
    # R3 G1 (GUEST-OPERATOR.md B1 "fehlendes Produkt-Wiring"): additive
    # Launcher-Flags fuer einen auswaehlbaren LOKALEN getrennten Terminal-/
    # Kontrollanschluss (Named Pipes, kein LAN/Browser/Scheduler) -- Default
    # `None`/leer -> der normale Start bleibt EXAKT unveraendert (bytegleiches
    # Solo-/bisheriges Verhalten, s. `_fifo_control_line_source`/
    # `_fifo_input_fn`/`_fifo_print_fn`-Docstrings).
    parser.add_argument(
        "--operator-control-fifo", default=None, metavar="PFAD",
        help=(
            "setzt 'session.operator_control_line_source' auf einen Leser, der Kontrollzeilen "
            "(/stop, /zuschauer) aus DIESER Named Pipe liest statt aus dem mit Spielzuegen "
            "geteilten stdin -- macht die Betreiberkontrolle waehrend eines offenen Calls "
            "ueber einen getrennten lokalen Weg erreichbar (G1)."
        ),
    )
    parser.add_argument(
        "--guest-terminal", dest="guest_terminal", action="append", default=[],
        metavar="GUEST_ID:IN_FIFO:OUT_FIFO",
        help=(
            "wiederholbar -- baut fuer <guest_id> eine getrennte Gast-Client-TuiSession, deren "
            "Eingabe aus <in_fifo> liest und Ausgabe nach <out_fifo> schreibt, und registriert "
            "sie via 'register_guest_terminal'. Der menschliche Gast bedient so sein EIGENES "
            "Terminal (G1)."
        ),
    )
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    run_dir = Path(args.run_dir) if args.run_dir else data_dir / "run"
    states_dir = Path(args.states_dir) if args.states_dir else data_dir / "states"
    host_capable = _resolve_host_capable(args.host_capable)
    foreign_pid = _foreign_active_lab_owner(data_dir)
    if foreign_pid is not None:
        print(
            f"TUI-Start: ein aktiver Lab-Lauf (pid={foreign_pid}) kontrolliert diese "
            "Datenablage — kein zweiter schreibender Controller (H-D/G3b, F1). Nur "
            "lesende Ansicht moeglich ('python scripts/mmo_sim.py lab status/attach')."
        )
        return 1
    try:
        participant_id = _resolve_participant_id(data_dir, args.participant)
    except identity.InvalidParticipantId as exc:
        # Fix C (ZR-SPIEL-S1, LINUS-SPEC §Fix C): fruehe, verstaendliche
        # Ablehnung VOR jedem Admission-/GM-/Transportbau -- kein stilles
        # Erfolgssignal, der Bestand (last_participant.json) bleibt wie von
        # `_resolve_participant_id` erhalten unveraendert.
        print(f"TUI-Start: {exc}")
        return 2
    schema_path = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
    # F1-3: die tatsaechlich konfigurierte Preset-/KB-Route live ermitteln
    # (s. `_resolve_active_gm_route`-Docstring) -- fail-soft, blockiert den
    # Start nicht.
    _gm_sl_model, _gm_kb_id = _resolve_active_gm_route(_REPO_ROOT)
    # WP5a/PF3.GM: `_gm_kb_id` kann der Sentinel `GM_ROUTE_KB_UNVERIFIED`
    # sein (Read fehlgeschlagen trotz Key) -- `default_gm_transport_factory`
    # selbst erkennt den Sentinel und wirft erst bei echtem produktivem
    # Zugriff (NACH dem Test-Double-Seam-Check, s. factories.py), statt
    # still auf die in sl_client.py hartkodierte historische KB
    # zurueckzufallen. Die Pruefung lebt bewusst DORT, nicht hier im
    # Wiring, damit ein gesetztes `MMO_SIM_GM_TRANSPORT_DOUBLE`
    # (Test-/Grenzinjektions-Seam) weiterhin unveraendert Vorrang hat.
    gm_transport_factory = _default_gm_transport_factory(
        data_dir, _REPO_ROOT, sl_model=_gm_sl_model, kb_id=_gm_kb_id,
    )
    session = TuiSession(
        onboarding_dir=data_dir / "onboarding",
        catalog_dir=data_dir / "catalog",
        participant_id=participant_id,
        run_dir=run_dir,
        states_dir=states_dir,
        schema_path=schema_path if schema_path.is_file() else None,
        # F5/K2: echter Adapter-Factory (nicht None) -- die tatsaechliche
        # Live-SL-Anbindung (03 §7, OPENWEBUI_API_KEY etc.) bleibt ein
        # separates Setup; ohne sie liefert der erste Aufruf eine klare
        # Fehlermeldung statt eines stillen Spielstarts.
        gm_transport_factory=gm_transport_factory,
        # A1: echte Factory statt None -- ohne MMO_SIM_PERSONA_CLI/_API_*
        # Umgebungskonfiguration liefert der erste Persona-Einladungsversuch
        # eine klare Fehlermeldung (s. `_default_persona_driver_factory`).
        persona_driver_factory=_default_persona_driver_factory(data_dir),
        host_capable=host_capable,
    )
    # R3 G1: beide Flags sind additiv und wirken NUR, wenn ausdruecklich
    # gesetzt -- ein Start ohne sie bleibt die unveraenderte Default-Session
    # von oben (Solo/bisheriges Verhalten bytegleich).
    if args.operator_control_fifo:
        operator_fifo_path = Path(args.operator_control_fifo)
        _ensure_fifo(operator_fifo_path)
        session.operator_control_line_source = _fifo_control_line_source(operator_fifo_path)
    # R4 FIX1 (B1/G3, GUEST-OPERATOR.md §4/B1 "fehlendes Produkt-Wiring"):
    # eine via `register_guest_terminal` angeschlossene `guest_session`
    # bekam bisher NIE ihren eigenen Befehlsdispatch -- ihre FIFOs wurden
    # angelegt/verdrahtet, aber nichts las je aus `in_fifo`/schrieb nach
    # `out_fifo` (nur `session.run()` des Betreibers unten lief). Jede
    # registrierte `guest_session` bekommt jetzt NEBENLAEUFIG ihren
    # eigenen `run()`-Dispatch in einem EIGENEN Thread -- derselbe
    # bestehende Menue-/Befehlsdispatch (inkl. `gast-erschaffung-*`,
    # bereits auf die Anbieter-Autoritaet verdrahtet, s. `register_guest_
    # terminal`), nur nebenlaeufig zum Betreiber-Dispatch statt gar nicht
    # gestartet. GETRENNTE FIFOs je Teilnehmer (keine konkurrierenden
    # Leser desselben Kanals) -- kein zweiter Hoststack, kein LAN/Browser/
    # Netzdienst, nur ein zusaetzlicher lokaler Thread fuer denselben
    # Prozess. `daemon=True`: ein (noch) unverbundenes/blockierend auf
    # seiner eigenen FIFO lesendes Gastterminal darf den Prozessaustritt
    # NIE aufhalten (derselbe Daemon-Stil wie `_OperatorControlScope`s
    # Kontroll-Thread).
    guest_threads: list[threading.Thread] = []
    for guest_spec in args.guest_terminal:
        guest_id, in_fifo_path, out_fifo_path = _parse_guest_terminal_spec(guest_spec)
        _ensure_fifo(in_fifo_path)
        _ensure_fifo(out_fifo_path)
        # Getrennte PRIVATE Onboarding-/Katalogwurzel je Gast (eigener
        # Figurenbestand) -- `run_dir`/`states_dir` bleiben DIESELBEN wie
        # die Host-Session (geteilte Tisch-/Admissionskoordination, exakt
        # derselbe Aufbau wie der bereits bestehende, getestete F1-Mechanismus
        # in `test_r3_f1_guest_table_service.py`, KEINE zweite Speicherwelt).
        # R4 FIX6: EIN geteilter `_FifoInputReader` liefert sowohl den
        # konsumierenden `input_fn` (`read_line`) ALS AUCH den nicht-
        # konsumierenden Bereitschafts-Check (`ready`) fuer dieselbe,
        # EINMAL geoeffnete FIFO -- `TuiSession._readline_guest_menu`
        # nutzt `ready` NUR fuer dieses per `register_guest_terminal`
        # angeschlossene Gast-Terminal, um waehrend eines aktiven
        # host-getriebenen Round-/Dialog-Claims (s. `_HumanDriver.decide`)
        # zu parken statt zu konkurrieren.
        # N1-FIX (R2): EIN gemeinsames `print_fn`-Closure fuer die out-FIFO
        # -- es dient sowohl der normalen Gast-Anzeige (`print_fn`) ALS AUCH
        # dem Prompt-Echo des Lesers (`echo_fn`). Geteiltes Closure =
        # dasselbe lazy geoeffnete out-FIFO-Dateiobjekt, kein zweiter
        # O_RDWR-Open derselben Pipe.
        guest_print_fn = _fifo_print_fn(out_fifo_path)
        in_fifo_reader = _FifoInputReader(in_fifo_path, echo_fn=guest_print_fn)
        guest_session = TuiSession(
            onboarding_dir=data_dir / "guests" / guest_id / "onboarding",
            catalog_dir=data_dir / "guests" / guest_id / "catalog",
            participant_id=guest_id,
            input_fn=in_fifo_reader.read_line,
            print_fn=guest_print_fn,
            run_dir=run_dir,
            states_dir=states_dir,
            schema_path=schema_path if schema_path.is_file() else None,
            host_capable=False,
            input_ready_fn=in_fifo_reader.ready,
        )
        session.register_guest_terminal(guest_id, guest_session)
        guest_thread = threading.Thread(
            target=guest_session.run, name=f"guest-terminal-{guest_id}", daemon=True,
        )
        guest_thread.start()
        guest_threads.append(guest_thread)
    try:
        return session.run()
    except KeyboardInterrupt:
        print("\n  Pausiert (Ctrl-C) — kein weiterer Modellaufruf.")
        return 130
    except ProviderQuotaPausedError as exc:
        # FIX5B (Review-Blocker Punkt 1, CRITIC-FIX5-REVIEW.md): Backstop
        # neben dem primaeren Fang in `mmo_sim/ui/tui.py` (um den einen
        # `app_service.run_play_session`-Aufrufpunkt) -- faengt dieselbe
        # getypte Kontingent-/Budgetpause hier ZUSAETZLICH ab, falls sie je
        # ueber einen anderen, noch nicht gewachten Pfad bis zu `session.
        # run()` durchschlagen sollte. Kein Traceback, kein Crash-Look;
        # derselbe Save-Stand bleibt die verbindliche Grenze, kein
        # erzwungenes Finalisieren -- ein Neustart setzt ueber die
        # bestehenden Resume-Pfade genau hier fort.
        print(quota_pause_player_message(
            quota_pause_reset_hint(str(exc)), rate_limited=quota_pause_is_rate_limited(str(exc)),
        ))
        return 0
    finally:
        # R4 FIX1: sauberes Shutdown/Join -- ein bereits abgeschlossenes
        # Gastterminal (z.B. EOF/`beenden`) wird hier eingesammelt; ein
        # noch blockierend auf seiner eigenen FIFO lesendes Gastterminal
        # bleibt dank `daemon=True` oben ohne Haengen beim Prozessaustritt
        # (derselbe kurze Join-Versuch wie `_OperatorControlScope.__exit__`).
        for guest_thread in guest_threads:
            guest_thread.join(timeout=0.5)


if __name__ == "__main__":
    sys.exit(main())
