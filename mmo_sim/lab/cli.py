#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mmo_sim/lab/cli.py — expliziter Headless-Einstieg `lab start|resume|status|
stop|attach` (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, H-B/H-C/H-D).

Aufgerufen NUR ueber `scripts/mmo_sim.py lab ...` (Dispatch dort VOR jeder
TUI-/Teilnehmerlogik, s. dortiger Docstring). `status`/`attach` sind
REIN LESEND (kein `LabRunner`, kein `TuiSession`, keine Adapterfactory,
keine Community-/Personakonstruktion -- H-C). `stop` ist der enge
Kontrollwrite `lab.runner.request_stop` (kein `LabRunner`, kein Reset).
`start`/`resume` konstruieren eine `TuiSession` OHNE interaktives Terminal
(`_refuse_input` wirft bei jedem Versuch, etwas einzulesen -- ein Lab-Lauf
fragt NIE ueber stdin) und rufen `core.lobby_flow.run_lobby_window` in einer
sequenziellen Schleife auf -- DIESELBE Funktion, die `ui.tui.TuiSession.
_cmd_lobby_initiative` aufruft (H-A: kein zweiter Spielstart-Pfad)."""
from __future__ import annotations

import argparse
import json
import math
import os
import select
import signal
import sys
import time
from pathlib import Path

from . import runner as lab_runner
from .runner import LabBudget, LabRunner, LabRunnerRestartError, SingletonViolationError
from ..core import lobby_flow


class LabConfigError(ValueError):
    """Fehlkonfiguration, VOR jeder Bestandsmutation erkannt (H-B: 'Fehl-
    konfig kontrolliert VOR Anfragen und ohne Bestandsersetzung ablehnen')."""


def _sigterm_as_keyboard_interrupt(signum, frame) -> None:
    """H05 P4 (02_AUFTRAG_H05.md): der bestehende `except KeyboardInterrupt`-
    Pfad in `_run_controller` (Ctrl-C/SIGINT: `lab.stop(...)` + `lab.
    release()` im `finally`, exit_code=130) war der EINZIGE Signalpfad --
    der dortige Meldungstext nannte "Ctrl-C/SIGTERM" bereits, ohne dass ein
    echter SIGTERM-Handler existierte (H05-Repro: `test_h05_stop_lifecycle_
    2026_09_29.py::test_p4_controller_sigterm_hybrid`, ein reales SIGTERM
    toetete den Controller mit Pythons Default-Aktion -- `finally: lab.
    release()` lief NICHT, `lab.status.json.running` blieb stale `True`,
    kein wahrheitsgemaesser Stopgrund). Diese Funktion erhebt bei SIGTERM
    exakt dieselbe `KeyboardInterrupt`, die der bestehende Pfad bereits
    behandelt -- kein zweiter Codepfad, keine neue Abschluss-/Save-/
    Budgetsemantik. Nur lokal fuer die aktive Controllerphase installiert
    (s. Aufrufer), Wiederherstellung des vorherigen Handlers im `finally`."""
    raise KeyboardInterrupt()


def _positive_int(raw: str) -> int:
    try:
        val = int(raw)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"keine gueltige Ganzzahl: {raw!r}") from e
    if val <= 0:
        raise argparse.ArgumentTypeError(f"muss eine positive Ganzzahl sein (erhalten: {raw!r})")
    return val


def _finite_positive_float(raw: str) -> float:
    try:
        val = float(raw)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"keine gueltige Zahl: {raw!r}") from e
    if not math.isfinite(val) or val <= 0:
        raise argparse.ArgumentTypeError(
            f"muss eine endliche Zahl > 0 sein (kein NaN/Inf/0/negativ, erhalten: {raw!r})"
        )
    return val


def _add_data_dir_arg(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--data-dir", required=True, help="dasselbe Datenverzeichnis wie beim TUI-Aufruf")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmo_sim.py lab", description="Expliziter Headless-Lab-Betrieb")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("start", "resume"):
        p = sub.add_parser(name, help=f"Lab-Lauf {name}en")
        _add_data_dir_arg(p)
        p.add_argument("--community", required=True, help="Rohe bestaetigte Community-ID wie --participant, ohne community-Praefix")
        p.add_argument("--profile", required=True, choices=("api", "hybrid"), help="Providerprofil")
        p.add_argument("--max-requests", required=True, type=_positive_int, help="max. Requests (Turns) dieses Laufs")
        p.add_argument("--max-seconds", required=True, type=_finite_positive_float, help="max. aufsummierte Requestdauer (Sekunden)")
        p.add_argument("--max-usd", default=None, type=_finite_positive_float, help="Fuer api und hybrid Pflicht: Dollargrenze der API-Rollen; CLI-Quota bleibt getrennt")
        p.add_argument("--max-idle-windows", required=True, type=_positive_int, help="max. aufeinanderfolgende Fenster ohne Fortschritt")
        p.add_argument("--max-wall-seconds", default=None, type=_finite_positive_float, help="reale Laufzeitgrenze (Wall-Clock, getrennt von --max-seconds)")
        p.add_argument("--personas", default=None, help="Kommagetrennte Teilmenge der Community (Default: gesamte bestaetigte Community)")

    p_status = sub.add_parser("status", help="nur lesend: aktuellen Laufzustand anzeigen")
    _add_data_dir_arg(p_status)

    p_stop = sub.add_parser("stop", help="idempotenter Kontrollwrite: Stop anfordern")
    _add_data_dir_arg(p_stop)
    p_stop.add_argument("--reason", default=None, help="Grund (optional, wird persistiert)")

    p_attach = sub.add_parser("attach", help="nur lesend: passive Operatoransicht")
    _add_data_dir_arg(p_attach)
    p_attach.add_argument("--follow", action="store_true", help="periodisch aktualisieren, bis Ctrl-C/EOF (nur dieser Beobachter-Prozess endet)")
    p_attach.add_argument("--interval-seconds", type=_finite_positive_float, default=1.0, help="Aktualisierungsintervall fuer --follow")
    p_attach.add_argument("--max-updates", type=_positive_int, default=None, help="fuer --follow: harte Obergrenze an Aktualisierungen (Testdeterminismus)")

    return parser


class _RefuseInput:
    def __call__(self, prompt: str = "") -> str:
        raise EOFError(
            "Lab-Lauf ist headless -- es gibt keine stdin-Eingabe, kein Konsolentext-Parser "
            "steuert den Ablauf (01_AUFTRAG §2)."
        )


def _last_window_path(run_dir: Path) -> Path:
    return run_dir / "lab.last_window.json"


def _write_last_window(run_dir: Path, *, community_id: str, outcome) -> None:
    """Diagnose-Ergaenzung (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27,
    REVIEW-HEADLESS-BETRIEBSGRENZEN.md Probe 08/§6): der CONTROLLER (nicht
    `status`/`attach`) persistiert nach JEDEM Fenster das bereits vorhandene
    `LobbyWindowOutcome` -- `lab status`/`lab attach` lesen diese Datei NUR
    (kein Nebenwrite durch Beobachter, keine Report-KI, H-C). Ohne diese
    Persistenz kannte `lab status` NUR `open_requests` (leer, sobald alle
    Requests `accounted` sind) -- Community/Fenster/Table/Section eines
    weiterhin offenen, gespielten Tisches blieben unsichtbar, obwohl
    `LobbyWindowOutcome` sie bereits trug."""
    payload = {
        "community_id": community_id,
        "kind": outcome.kind.value,
        "reason": outcome.reason,
        "table_id": outcome.table_id,
        "section_id": outcome.section_id,
        "window_id": outcome.window_id,
        "request_id": outcome.request_id,
        "ts": time.time(),
    }
    _last_window_path(run_dir).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _status_payload(run_dir: Path) -> dict:
    stop_flag_present = (run_dir / "lab.stop").exists()
    # F1-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): H-C verlangt bei
    # BESCHAEDIGTEM Zustand konkret "kein Lauf"/"ungeklaert", KEINEN Absturz
    # -- `lab.runner.read_status` liest `lab.status.json` bewusst ungefangen
    # (dessen bestehende Schreibpfad-Aufrufer `LabRunner.__init__`/
    # `record_turn`/`_write_status` reagieren bewusst fail-closed per
    # Ausnahme, s. dortige Docstrings; deren Vertrag bleibt hier
    # unveraendert). Dieser NEUE lesende H-C-Zugriff (`lab status`/`lab
    # attach`) faengt eine Beschaedigung deshalb HIER an der Konsumgrenze ab.
    try:
        status = lab_runner.read_status(run_dir)
    except (OSError, json.JSONDecodeError, TypeError) as e:
        return {
            "run": "unklar", "stop_flag_present": stop_flag_present,
            "reason": (
                f"lab.status.json beschaedigt/nicht lesbar ({e.__class__.__name__}) -- "
                "H-C: 'ungeklaert' statt Absturz oder stillschweigender Erstlauf."
            ),
        }
    if status is None:
        return {
            "run": "none", "stop_flag_present": stop_flag_present,
            "reason": "kein Lauf/Status unter diesem data-dir bekannt (H-C: kein Erstlauf hier angelegt).",
        }
    from ..core import request_ledger
    try:
        open_reqs = [
            {
                "request_id": r.get("request_id"), "table_id": r.get("table_id"),
                "section_id": r.get("section_id"), "role": r.get("role"),
                "participant": r.get("participant"), "state": r.get("state"),
            }
            for r in request_ledger.open_requests(run_dir)
        ]
    except Exception as e:  # H-C: eine Statusabfrage darf nicht abstuerzen, meldet aber den Fund konkret.
        open_reqs = [{"error": str(e)}]
    # H-C: der GENAU DIESELBE Gate-Check, den der naechste echte Request
    # durchlaufen wuerde (frisch von der Platte, kein Cache) -- zeigt den
    # tatsaechlichen aktuellen Zustand, nicht nur das ggf. veraltete
    # `stop_requested`-Feld vom letzten `LabRunner._write_status()`-Aufruf.
    from ..core.admission import read_admission_block
    next_blocked, next_block_reason = read_admission_block(run_dir)
    # F3-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `stop_requested`/
    # `stop_reason` FRISCH ueber `compute_stop_state` berechnen, NICHT das
    # ggf. eingefrorene `LabStatus`-Feld vom letzten `_write_status()`-
    # Aufruf uebernehmen -- `LabRunner.stop()`/`request_stop()` schreiben
    # bewusst NUR die separate Stop-Flag-Datei (H-C: enger Kontrollwrite,
    # kein Reset) und lassen `lab.status.json` nach einem externen Stop
    # unveraendert. Ohne diesen Fix widersprach `lab status` sich selbst:
    # `stop_requested: false` trotz `stop_flag_present: true`.
    stop_requested, stop_reason = lab_runner.compute_stop_state(
        run_dir, turns_used=status.turns_used, seconds_elapsed=status.seconds_elapsed,
        usd_spent=status.usd_spent, max_turns=status.max_turns,
        max_seconds=status.max_seconds, max_usd=status.max_usd,
    )
    # Diagnose-Ergaenzung (Bau-GO 2026-09-27, REVIEW-HEADLESS-BETRIEBSGRENZEN.md
    # Probe 08/§6): rein lesend -- die Datei wird AUSSCHLIESSLICH vom
    # Controller in `_run_controller` geschrieben (`_write_last_window`),
    # NIE von `status`/`attach` selbst. Fehlt/ist beschaedigt (kein Fenster
    # bisher gelaufen, aelterer Lauf ohne diese Datei): `None`, kein Absturz,
    # kein erfundener Ersatzwert.
    last_window = None
    lw_path = _last_window_path(run_dir)
    if lw_path.exists():
        try:
            last_window = json.loads(lw_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            last_window = {"error": "lab.last_window.json beschaedigt/nicht lesbar."}
    return {
        "run": "known",
        "next_request_blocked": next_blocked, "next_request_block_reason": next_block_reason,
        "running": status.running, "pid": status.pid,
        "turns_used": status.turns_used, "max_turns": status.max_turns,
        "seconds_elapsed": status.seconds_elapsed, "max_seconds": status.max_seconds,
        "usd_spent": status.usd_spent, "max_usd": status.max_usd,
        "usd_unknown_turns": status.usd_unknown_turns,
        "stop_requested": stop_requested, "stop_reason": stop_reason,
        "stop_flag_present": stop_flag_present,
        "open_requests": open_reqs,
        "last_window": last_window,
    }


def _cmd_status(args) -> int:
    run_dir = Path(args.data_dir) / "run"
    print(json.dumps(_status_payload(run_dir), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _cmd_stop(args) -> int:
    run_dir = Path(args.data_dir) / "run"
    reason = args.reason or "Betreiber-Stop (lab stop)"
    lab_runner.request_stop(run_dir, reason)
    print(
        f"Stop angefordert fuer {run_dir} (reason={reason!r}) — 'angefordert' ist nicht "
        "dasselbe wie 'Controller bereits angehalten', s. 'lab status'."
    )
    return 0


def _public_offer_log_tail(run_dir: Path, limit: int = 20) -> list[dict]:
    """H-C/H09: nur die ohnehin oeffentlichen Angebots-/Antwort-/Resolution-
    Felder (keine Secrets, keine privaten Persona-Reflexionen -- die stehen
    in `states/`, nicht im Offer-Log)."""
    from ..core import lobby_service
    records = lobby_service.read_offer_log(run_dir)
    return records[-limit:]


def _cmd_attach(args) -> int:
    run_dir = Path(args.data_dir) / "run"
    updates = 0
    # H05 P3 Nacharbeit (End-Critic-Befund 2026-09-29, siehe 05_QUELLEN_UND_
    # PRUEFUNGEN.md / CRITIC-REPORT.md §5): `except KeyboardInterrupt` lag
    # zuvor NUR um `time.sleep(...)`, nicht um die Schleife als Ganzes. Trifft
    # SIGINT waehrend `print(...)`/`_status_payload(...)`/dem stdin-EOF-Check
    # ein, propagierte es unbehandelt bis zum Modulende (rc=-2, Traceback auf
    # stderr statt der vorgesehenen Meldung) -- vom Critic selbst reproduziert
    # (1 von 3 Laeufen). Fix analog zu `_run_controller`s bereits abgenommenem
    # SIGTERM-Pfad (siehe dort): der `try/except KeyboardInterrupt` umschliesst
    # jetzt den GESAMTEN Schleifenkoerper, nicht nur einen einzelnen Aufruf --
    # ein Signal kann daher an jeder Stelle eintreffen und wird trotzdem sauber
    # behandelt, unabhaengig vom Timing.
    try:
        while True:
            payload = _status_payload(run_dir)
            payload["recent_public_events"] = _public_offer_log_tail(run_dir)
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
            updates += 1
            if not args.follow:
                return 0
            if args.max_updates is not None and updates >= args.max_updates:
                return 0
            # H05 P3 (02_AUFTRAG_H05.md): ein eigener Observer-Prozess muss sich
            # ausschliesslich SELBST ueber ein echtes stdin-EOF beenden koennen
            # (z.B. wenn sein aufrufender Prozess die eigene Pipe schliesst),
            # OHNE `--max-updates` und OHNE SIGINT -- vorher wurde stdin in dieser
            # Schleife nirgends gelesen, ein geschlossenes stdin hatte also NIE
            # eine Wirkung (H05-Repro: `test_h05_stop_lifecycle_2026_09_29.py::
            # test_p3_observer_end`, Observer A lief bis zum Testtimeout durch).
            # `select` auf stdin mit Timeout 0 VOR dem Sleep: nur wenn stdin
            # bereits lesebereit ist (Daten ODER EOF), wird ueberhaupt gelesen --
            # kein Blockieren, kein veraendertes Verhalten fuer den ueblichen
            # Fall ohne angeschlossene Pipe/mit `stdin=DEVNULL`. Ein Lab-Attach
            # erwartet nie echte Eingabezeilen; jede gelesene (auch leere) Zeile
            # gilt hier als Beobachterende, analog der bestehenden Ctrl-C-Antwort.
            try:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0] and sys.stdin.readline() == "":
                    print("\nAttach beendet (stdin-EOF) — der Lab-Controller laeuft unveraendert weiter.")
                    return 0
            except (OSError, ValueError):
                pass  # kein lesbares stdin (z.B. bereits geschlossen/kein TTY) -- normales Follow unveraendert.
            time.sleep(args.interval_seconds)
    except KeyboardInterrupt:
        print("\nAttach beendet (Ctrl-C) — der Lab-Controller laeuft unveraendert weiter.")
        return 0


def _run_controller(args, repo_root: Path, *, resume: bool) -> int:
    data_dir = Path(args.data_dir)
    run_dir = data_dir / "run"

    # G2b (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, ANSCHLUSSPLAN-
    # HEADLESS.md ERGAENZUNG 2): `--max-usd` ist jetzt fuer BEIDE Profile
    # Pflicht -- die GM-/KI-SL-Rolle wird IMMER ueber ein echtes HTTP-API
    # angesprochen (`adapters/gm_owui.py`, unabhaengig vom gewaehlten
    # Personaprofil, s. dortigen Moduldocstring), bleibt also IMMER
    # dollarbegrenzt (H08: "GM weiterhin Loopback-HTTP"). Die vorherige
    # Fassung verbot `--max-usd` unter Hybrid komplett und setzte
    # `LabBudget.max_usd=None` GLOBAL -- das schaltete die Dollar-/
    # Output-Bound-Pruefung (`core.admission.read_admission_block`) damit
    # auch fuer die GM-Rolle ab (REVIEW-HEADLESS-BETRIEBSGRENZEN.md Probe 07:
    # eine echte GM-Anfrage OHNE `max_tokens` UND OHNE `max_usd` ging durch).
    # Personarollen bleiben unter Hybrid trotzdem NICHT dollarbegrenzt --
    # `core.admission.read_admission_block(..., dollar_billed=...)` scoped
    # das jetzt PRO ROLLE/TREIBER (`PersonaClaudeCodeDriver.is_dollar_billed
    # = False`), nicht mehr global ueber `LabBudget.max_usd`
    # (kein globales max_usd=None, kein Abriss von B2/Q07).
    if args.max_usd is None:
        raise LabConfigError(
            "--max-usd ist fuer BEIDE Profile Pflicht (H-E/G2b): begrenzt die tatsaechlich "
            "ueber API abgerechneten Rollen (KI-SL/GM, unter Hybrid zusaetzlich falls Personas "
            "ueber API liefen) -- CLI/Abo-Personas haben eigene Turn-/Zeit-/Kontingentgrenzen "
            "und bleiben davon unberuehrt (keine Dollarbefreiung der GM-Rolle unter Hybrid)."
        )

    # G2a (REVIEW-HEADLESS-BETRIEBSGRENZEN.md Probe 03): fruehe, VOR jeder
    # Bestandsmutation (Community-Peek/LabRunner/`lab.start()`) liegende
    # Pruefung, dass das gewaehlte Profil zur tatsaechlich vorhandenen Env-
    # Konfiguration passt -- kein Env-Prioritaets-Silent-Switch, kein
    # API-Fallback bei CLI-Fehler (H-E). `adapters.factories.
    # default_persona_driver_factory(profile=...)` ist der zweite, defensive
    # Schutzring an der tatsaechlichen Adapter-Konstruktionsstelle.
    cli_binary = os.environ.get("MMO_SIM_PERSONA_CLI")
    api_base_url = os.environ.get("MMO_SIM_PERSONA_API_BASE_URL")
    if args.profile == "hybrid" and not cli_binary:
        raise LabConfigError(
            "Profil 'hybrid' erfordert MMO_SIM_PERSONA_CLI -- kein stiller Fallback auf "
            "MMO_SIM_PERSONA_API_BASE_URL (G2a: gewaehltes Profil bindet den tatsaechlichen "
            "Adapter verbindlich, kein Env-Prioritaets-Silent-Switch)."
        )
    if args.profile == "api" and not api_base_url:
        raise LabConfigError(
            "Profil 'api' erfordert MMO_SIM_PERSONA_API_BASE_URL -- kein stiller Fallback auf "
            "MMO_SIM_PERSONA_CLI (G2a: gewaehltes Profil bindet den tatsaechlichen Adapter "
            "verbindlich)."
        )

    # H-B/H07 ("Betriebstabelle"): 'start' und 'resume' sind DERSELBE Aufruf
    # mit denselben IDs -- die einzige Arbitrierungsinstanz gegen einen
    # zweiten gleichzeitigen Controller ist der Singleton-Lock weiter unten
    # (`LabRunner.start()`), NICHT ein vorgelagerter Dateiexistenz-Check (der
    # wuerde H06s zwei GLEICHZEITIGEN Startprozessen faelschlich schon hier
    # widersprechen, sobald der erste seinen `lab.status.json` bereits
    # geschrieben hat). `resume` unterscheidet sich von `start` bewusst NUR
    # im geloggten Verb -- eine NEUE `LabRunner`-Instanz liest den vollen
    # Verbrauchsstand ohnehin immer frisch von der Platte (R3), unabhaengig
    # davon, welches Subkommando sie konstruiert hat.
    participant_id = args.community
    community_id = f"community-{participant_id}"
    community_dir = run_dir / "community"
    from ..domain.zeitriss.community_bootstrap import peek as peek_bootstrap
    bootstrap = peek_bootstrap(community_dir, community_id)
    if bootstrap is None or not bootstrap.personas_written:
        raise LabConfigError(
            f"Keine bestehende bestaetigte Community {community_id!r} unter {community_dir} "
            "gefunden -- Lab bootstrapt keine neue Community (H-B: 'kein impliziter "
            "Communitybootstrap')."
        )

    selected: set[str] = set(bootstrap.personas_written)
    if args.personas:
        requested = {p.strip() for p in args.personas.split(",") if p.strip()}
        unknown = requested - selected
        if unknown:
            raise LabConfigError(
                f"--personas enthaelt Mitglieder ausserhalb der bestaetigten Community: {sorted(unknown)}"
            )
        selected = requested
    if not selected:
        raise LabConfigError(
            "--personas ergibt eine leere KI-Auswahl -- mindestens eine ausdruecklich gewaehlte "
            "Persona ist Pflicht (H-F)."
        )

    budget = LabBudget(
        max_turns=args.max_requests, max_seconds=float(args.max_seconds), max_usd=args.max_usd,
        # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `max_wall_seconds`
        # wandert in die `LabBudget`-Autoritaet (persistiert von `LabRunner.
        # start()` als absolute Deadline), statt einer rein lokalen
        # `_run_controller`-Variable -- s. `LabBudget`/`LabStatus.
        # wall_deadline`-Docstrings.
        max_wall_seconds=float(args.max_wall_seconds) if args.max_wall_seconds else None,
    )

    # H10 T9 (02_AUFTRAG_H10.md, 2026-09-29): ein `resume` auf einem
    # `run_dir`, das bereits ECHTE Request-/Tischbezuege traegt (mindestens
    # ein Requestdatensatz unter `requests/` ODER mindestens eine Tischdatei
    # unter `tables/`), aber dessen `lab.status.json` FEHLT, ist ein
    # bekannter Lauf mit verlorener Autoritaet -- KEIN Erstlauf. Ohne diese
    # Pruefung liest `LabRunner.__init__` das fehlende `lab.status.json`
    # unconditional als Nullstand (bestehendes, unveraendertes Verhalten fuer
    # einen ECHTEN Erstlauf, s. dortigen Docstring) und `start()` persistiert
    # anschliessend einen frischen Status (turns_used=0 usw.) UEBER dem
    # bereits vorhandenen echten Verbrauch -- eine stille Erstinitialisierung
    # bei bekanntem Lauf, kein Hold (H10 T9-Vorgabe: "keine Erstinitiali-
    # sierung/Neugenerierung", "konkreter Hold/Fehler"). Eine tatsaechlich
    # NEUE, gerade erst bestaetigte Community ohne jemals gestarteten Lab-Lauf
    # hat WEDER `requests/`- NOCH `tables/`-Eintraege und bleibt von dieser
    # Pruefung unberuehrt (H10 T9: "Bootstrap-allein-Positivkontrolle bleibt
    # davon getrennt"). Nur diese eine, eng auf den Resume-Einstieg begrenzte
    # Kontrolle -- keine Aenderung an `LabRunner`/den IMMUTABLE-Symbolen.
    if resume and not (run_dir / "lab.status.json").exists():
        has_prior_requests = (run_dir / "requests").is_dir() and any((run_dir / "requests").glob("*.json"))
        has_prior_tables = (run_dir / "tables").is_dir() and any((run_dir / "tables").glob("*.json"))
        if has_prior_requests or has_prior_tables:
            raise LabConfigError(
                f"lab.status.json fehlt unter {run_dir}, obwohl dieser Lauf bereits echte "
                "Request-/Tischbezuege besitzt (H10 T9) -- kein stilles Erstinitialisieren bei "
                "bekanntem Lauf, konkreter Hold VOR jeder Bestandsmutation. Betreiber muss den "
                "Zustand pruefen (z.B. Statusdatei wiederherstellen oder bewusst einen neuen "
                "Speicherbereich waehlen), bevor hier erneut resumed wird."
            )

    schema_path = repo_root / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
    from ..adapters.factories import default_gm_transport_factory, default_persona_driver_factory
    from ..ui.tui import TuiSession
    session = TuiSession(
        onboarding_dir=data_dir / "onboarding", catalog_dir=data_dir / "catalog",
        participant_id=participant_id, input_fn=_RefuseInput(), print_fn=print,
        run_dir=run_dir, states_dir=data_dir / "states",
        schema_path=schema_path if schema_path.is_file() else None,
        gm_transport_factory=default_gm_transport_factory(data_dir, repo_root),
        persona_driver_factory=default_persona_driver_factory(data_dir, profile=args.profile),
    )

    lab = LabRunner(run_dir, budget)
    verb = "resume" if resume else "start"
    try:
        lab.start()
    except (SingletonViolationError, LabRunnerRestartError) as e:
        print(f"lab {verb}: {e}", file=sys.stderr)
        return 3

    print(
        f"Lab {verb} (pid={lab.pid}, run_dir={run_dir}, profile={args.profile}, "
        f"personas={sorted(selected)})."
    )
    exit_code = 0

    def _persist_stop(reason_text: str) -> None:
        # H-C/G1-Analogie (s. `LabRunner.record_turn()`-Docstring): NUR das
        # separate, harmlose Stop-Flag schreiben (`lab.stop()`) -- NIEMALS
        # `LabRunner._write_status()` hier aufrufen. Diese Instanz hat seit
        # ihrem Konstruktor-Read `record_turn()` nie selbst aufgerufen (der
        # echte Requestverbrauch schreibt `core.admission.record_turn_usage`
        # DIREKT auf die Platte, s. `run_section`-Docstring); ein
        # `_write_status()`-Aufruf HIER wuerde den zwischenzeitlich frisch
        # auf der Platte fortgeschriebenen `turns_used`/`usd_spent` mit dem
        # STETS VERALTETEN Konstruktor-Stand (meist 0) ueberschreiben --
        # exakt der Buchungsverlust-Fehler, den REVIEW-BUCHUNGSGRENZEN.md
        # bereits an anderer Stelle dokumentiert. `lab status` berechnet den
        # tatsaechlichen aktuellen Stop-/Blockzustand ohnehin frisch ueber
        # `core.admission.read_admission_block` (s. `_status_payload`),
        # unabhaengig von diesem Flag.
        lab.stop(reason_text)

    # H05 P4: SIGTERM lokal auf denselben, bereits vorhandenen
    # KeyboardInterrupt-Pfad umleiten -- NUR fuer die aktive Controllerphase
    # (dieser `try`/`finally`-Block), vorheriger Handler wird im `finally`
    # unbedingt wiederhergestellt (keine globale Prozess-/Signalpolitik).
    _prior_sigterm_handler = signal.signal(signal.SIGTERM, _sigterm_as_keyboard_interrupt)
    try:
        idle_windows = 0
        while True:
            # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `lab.should_stop()`
            # deckt jetzt AUCH die Wall-Clock-Deadline ab (`LabRunner.start()`
            # persistiert sie, `compute_stop_state`/`core.admission.
            # read_admission_block` pruefen sie frisch von der Platte vor
            # JEDEM Request, nicht nur hier zwischen zwei Fenstern) -- der
            # vorherige separate, rein lokale `time.monotonic()`-Vergleich an
            # dieser Stelle entfaellt, weil er dieselbe Grenze nur EINMAL PRO
            # FENSTER pruefte, nie waehrend eines laufenden Requests
            # INNERHALB eines Fensters (ANSCHLUSSPLAN-HEADLESS.md
            # Entscheidung 4).
            stop, reason = lab.should_stop()
            if stop:
                _persist_stop(reason or "Budget erschoepft")
                print(f"Lab: Stop/Budget erreicht ({reason}) — kein weiterer Request.")
                break
            outcome = lobby_flow.run_lobby_window(session, ai_personas=frozenset(selected))
            print(f"Lab-Fenster: {outcome.kind.value} — {outcome.reason}")
            # Diagnose-Ergaenzung (Bau-GO 2026-09-27, REVIEW-HEADLESS-
            # BETRIEBSGRENZEN.md §6): das bereits vorhandene `LobbyWindowOutcome`
            # (Table/Section/Window/Request-Bezug) fuer `lab status`/`lab
            # attach` persistieren -- NUR der Controller schreibt dies (kein
            # Nebenwrite durch Beobachter).
            _write_last_window(run_dir, community_id=community_id, outcome=outcome)
            if outcome.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED:
                idle_windows = 0
                continue
            if outcome.kind == lobby_flow.LobbyOutcomeKind.STOPPED:
                _persist_stop(outcome.reason)
                break
            # Diagnose-Ergaenzung (Bau-GO 2026-09-27, REVIEW-HEADLESS-
            # BETRIEBSGRENZEN.md Probe 08): ein WAEHREND dieses Fensters
            # bereits extern angeforderter Stop (z.B. `lab stop` waehrend
            # einer laufenden GM-Antwort -- der naechste Gate-Check INNERHALB
            # `run_full_section` faengt ihn ab und liefert `OPEN_WITH_REASON`,
            # NICHT `STOPPED`) muss VOR der Fenster-/Leerlaufgrenzen-Bewertung
            # unten erneut geprueft werden. Sonst wuerde die generische
            # Leerlaufgrenzen-Meldung unten denselben `lab.stop`-Datentraeger
            # (`_persist_stop`/`LabRunner.stop` schreiben dieselbe Datei) NOCH
            # IN DERSELBEN ITERATION mit einem generischen Text ueberschreiben
            # und den urspruenglichen, spezifischen Betreiber-Stopgrund
            # verdecken.
            already_stop, already_reason = lab.should_stop()
            if already_stop:
                _persist_stop(already_reason or "Budget erschoepft")
                print(f"Lab: Stop/Budget erreicht ({already_reason}) — kein weiterer Request.")
                break
            # NO_CONSENSUS / OPEN_WITH_REASON / WAITING_HUMAN: kein Fortschritt
            # in diesem Fenster -- zaehlt gegen die Fenster-/Leerlaufgrenze
            # (H-B: "endliche Fenster-/Leerlaufgrenze"; H03: "erschoepftes
            # Initiativ-/Fensterlimit bleibt ein Betriebsstopp, kein Erfolg").
            idle_windows += 1
            if idle_windows >= args.max_idle_windows:
                _persist_stop(f"Fenster-/Leerlaufgrenze erreicht ({args.max_idle_windows} Fenster ohne Fortschritt)")
                print("Lab: Fenster-/Leerlaufgrenze erreicht — geordneter Stop.")
                break
    except KeyboardInterrupt:
        lab.stop("Ctrl-C/SIGTERM — Pause angefordert, kein erfundener Abschluss (H-C).")
        print("\nLab pausiert (Ctrl-C/SIGTERM) — kein weiterer Modellaufruf, spaeteres 'lab resume' moeglich.")
        exit_code = 130
    finally:
        signal.signal(signal.SIGTERM, _prior_sigterm_handler)
        lab.release()
    return exit_code


def main(argv: list[str], repo_root: Path) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            return _run_controller(args, repo_root, resume=False)
        if args.command == "resume":
            return _run_controller(args, repo_root, resume=True)
        if args.command == "status":
            return _cmd_status(args)
        if args.command == "stop":
            return _cmd_stop(args)
        if args.command == "attach":
            return _cmd_attach(args)
    except LabConfigError as e:
        print(f"lab {args.command}: Konfigurationsfehler — {e}", file=sys.stderr)
        return 2
    parser.error(f"unbekanntes Subkommando {args.command!r}")
    return 2
