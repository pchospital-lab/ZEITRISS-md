#!/usr/bin/env python3
"""
mmo_sim/core/admission.py — zentrales Admission-Gate (I5, PLAN-CRITIC.md A1
BLOCKER, verifiziert `review_p2_integration.py:162-169`).

Liest den persistierten Pause-/Budget-Zustand DIREKT aus dem `run_dir` —
unabhaengig davon, ob eine `LabRunner`-Instanz zur Konstruktionszeit
injiziert wurde (Test 12 baut `SectionRuntime` VOR dem `LabRunner`). Nutzt
dieselben Dateipfade wie `lab/runner.py` (`lab.stop`, `lab.status.json`) rein
lesend — keine LabRunner-Abhaengigkeit, kein Schreibzugriff auf Locks.

`record_turn_usage` ist die passende Schreibgegenseite: `core/runtime.py`
ruft sie nach JEDEM echten GM-Turn auf (unabhaengig von einer LabRunner-
Instanz), damit `lab.status.json` — falls ein Lab-Lauf fuer dieses `run_dir`
aktiv ist/war — in Echtzeit die tatsaechlich verbrauchten Turns/Sekunden
nachfuehrt. `lab/runner.LabStatus` persistiert dafuer zusaetzlich die
Budget-Obergrenzen (`max_turns`/`max_seconds`/`max_usd`) mit, damit dieses
Modul die Stop-Entscheidung komplett von der Platte treffen kann, ohne die
Budget-Objekt-Semantik zu duplizieren oder zu kennen."""
from __future__ import annotations

import ipaddress
import json
import math
import os
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

# A9/D4 (WEGKARTE §8, Plan-Critic A9, Vertrag 03 §6): SYNTHETISCHE,
# konfigurierbare Tarife fuer die Offline-Budgetreservierung -- reale
# Provider-Preise sind fuer diesen Bauauftrag ausdruecklich NICHT noetig
# (WEGKARTE §5: "Provider-konkrete Preise NICHT noetig"). Ueberschreibbar per
# Env (Testprofile/Operator), niemals stillschweigend ein anderer Tarif.
_DEFAULT_SYNTHETIC_USD_PER_1K_PROMPT = 0.003
_DEFAULT_SYNTHETIC_USD_PER_1K_COMPLETION = 0.015
# I2 (Case 05, MAIN-ENTSCHEIDUNG): konservativer Zeichen-je-Token-Umrechner
# fuer die INPUT-Reservierung (s. `reservation_for_request`) -- ueberschreibbar
# per Env wie die Preise selbst, niemals stillschweigend ein anderer Wert.
_DEFAULT_SYNTHETIC_CHARS_PER_PROMPT_TOKEN = 4.0


def _synthetic_prices() -> tuple[float, float]:
    price_in = float(os.environ.get("MMO_SIM_SYNTHETIC_USD_PER_1K_PROMPT", _DEFAULT_SYNTHETIC_USD_PER_1K_PROMPT))
    price_out = float(os.environ.get("MMO_SIM_SYNTHETIC_USD_PER_1K_COMPLETION", _DEFAULT_SYNTHETIC_USD_PER_1K_COMPLETION))
    return price_in, price_out


def _synthetic_chars_per_token() -> float:
    return float(os.environ.get(
        "MMO_SIM_SYNTHETIC_CHARS_PER_PROMPT_TOKEN", _DEFAULT_SYNTHETIC_CHARS_PER_PROMPT_TOKEN,
    ))


def compute_turn_usd(usage: dict | None) -> float | None:
    """A9/D4 (WEGKARTE §8, Plan-Critic A9, Test-Nachbarschaft V04/V09):
    `None` ("unknown", 03 §4 "Nicht beobachtbare Werte heissen unknown,
    nicht null") wenn die Adapterantwort keine auswertbaren Kosten-/Token-
    Angaben enthaelt. Meldet der Provider bereits eine ECHTE USD-Zahl
    (`usage['usd']`/`usage['cost_usd']`/`usage['total_cost_usd']`), wird
    DIESE uebernommen -- der synthetische Tarif ist nur der Offline-
    Fallback aus Prompt-/Completion-Tokens (`result['usage']` aus dem
    GM-/Persona-Transport-Vertrag, bisher ungenutzt verworfen)."""
    if not usage:
        return None
    for key in ("usd", "cost_usd", "total_cost_usd"):
        val = usage.get(key)
        if isinstance(val, (int, float)):
            return float(val)
    ptok = usage.get("prompt_tokens")
    ctok = usage.get("completion_tokens")
    if not isinstance(ptok, (int, float)) and not isinstance(ctok, (int, float)):
        return None
    price_in, price_out = _synthetic_prices()
    return (float(ptok or 0) / 1000.0) * price_in + (float(ctok or 0) / 1000.0) * price_out


def _is_finite_number(value: object) -> bool:
    """Q04 (PLAN-CRITIC/MAIN-ENTSCHEIDUNG, Test 04): strukturelle Freigabe-/
    Limitwerte muessen ECHTE endliche Zahlen sein -- `NaN`/`Infinity` (von
    Pythons `json.loads` standardmaessig AKZEPTIERT, obwohl kein gueltiges
    JSON-Zahlenliteral), `bool` (technisch eine `int`-Unterklasse, aber
    keine sinnvolle Budgetzahl) oder ein falscher Typ gelten NICHT als
    finite -- der Aufrufer behandelt das wie einen beschaedigten Zustand
    (fail-closed), nicht wie eine gueltige Freigabe/Grenze."""
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def _route_is_controlled(route: str) -> bool:
    """Q03 (PLAN-CRITIC F5/Auflage, MAIN-ENTSCHEIDUNG bestaetigt): ein
    providerfreies Testprofil (`write_test_profile`) darf NUR ausdruecklich
    kontrollierte Antwort-/Prozessdoubles an FESTGELEGTEN (Loopback-)Routen
    freigeben -- sein Boolean allein darf KEINE beliebige konfigurierte
    externe Route (auch keine `.invalid`-Adresse) freischalten. Eine echte
    Betreiber-Live-/Budgetfreigabe (`LabRunner.start()`, setzt NIE
    `provider_free=True`) ist von dieser Einschraenkung nicht betroffen --
    sie darf echte Provider-Routen ansprechen (eigener, hier nicht
    beruehrter Live-Vertrag, 03 §6)."""
    try:
        host = urlparse(route).hostname
    except ValueError:
        return False
    if not host:
        return False
    if host in _LOOPBACK_HOSTS:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _stop_flag_path(run_dir: Path) -> Path:
    return run_dir / "lab.stop"


def _status_path(run_dir: Path) -> Path:
    return run_dir / "lab.status.json"


def _atomic_write_json(path: Path, data: dict) -> None:
    """R2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall 03):
    ALLE `lab.status.json`-Schreiber in diesem Modul schreiben zuerst in eine
    temporaere Datei im selben Verzeichnis und ersetzen das eigentliche Ziel
    erst danach per `os.replace` (atomarer Rename auf POSIX/NTFS). Ein
    gewoehnlicher Teilschreib-`OSError` auf dem Temp-Pfad hinterlaesst `path`
    dadurch UNVERAENDERT -- der letzte gueltige JSON-Stand bleibt lesbar,
    statt eines halb geschriebenen/korrupten Dokuments (die alte
    `write_text`-Direktschreibung auf die Zieldatei war keine
    Ganz-Dokument-Garantie). Kein fsync-/OS-Powerloss-Haertungsprojekt (nicht
    beauftragt) -- deckt gewoehnliche Python-Ausnahmen waehrend des
    Schreibens ab. Ein Fehler wird NICHT verschluckt: die verwaiste
    Temp-Datei wird bestmoeglich aufgeraeumt, die Ausnahme propagiert an den
    Aufrufer (R1-Prinzip: ein Schreibfehler ist kein stiller Erfolg)."""
    tmp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}")
    try:
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, path)
    except OSError:
        tmp_path.unlink(missing_ok=True)
        raise


def reservation_for_max_tokens(max_output_tokens: float) -> float:
    """W2 (F..., Test 04 review_p2w_boundaries.py): rechnet eine am
    Aufrufer/Treiber tatsaechlich KONFIGURIERTE Ausgabeobergrenze (z.B.
    `PersonaApiConfig.max_tokens`) in eine konservative USD-Reservierung
    um -- DERSELBE Tarif wie `record_turn_usage`s Unknown-Schaetzung
    (`_synthetic_prices()`), damit Vor- und Nachher-Schaetzung nicht
    auseinanderdriften (A1, s. `read_admission_block`-Docstring)."""
    _, price_out = _synthetic_prices()
    return (float(max_output_tokens) / 1000.0) * price_out


def reservation_for_driver(driver: object) -> float | None:
    """W2 (F..., "anfragebezogene Reservierung ... statt Pauschalschwelle"):
    liest eine ggf. am TREIBER konfigurierte Ausgabeobergrenze (aktuell:
    `driver.config.max_tokens`, z.B. `PersonaApiConfig`) und liefert die
    daraus berechnete Reservierung. Treiber ohne erkennbare, konfigurierte
    Obergrenze (Hybrid-CLI-Profil ohne Tokenparameter, Human-Driver, ...)
    liefern `None` -- der Aufrufer faellt dann auf die unveraenderte
    Pauschalreservierung (`_synthetic_prices()`s `price_out`) zurueck, exakt
    wie vor diesem Fix. Reine Namens-/Attributpruefung (duck typing, kein
    Import der Adapter hier noetig -- admission.py bleibt providerfrei)."""
    cfg = getattr(driver, "config", None)
    max_tokens = getattr(cfg, "max_tokens", None)
    if isinstance(max_tokens, (int, float)) and max_tokens > 0:
        return reservation_for_max_tokens(max_tokens)
    return None


def _estimate_wire_chars(context: dict) -> int:
    """I2 (Case 05): dieselbe Textzusammensetzung wie `adapters.base.
    render_public_wire_text` (user + own_context + table_view) -- als
    bewusste kleine Duplikation OHNE die Adapterschicht zu importieren
    (admission.py bleibt providerfrei, `reservation_for_driver`s Docstring-
    Prinzip). Kein neuer Store/Protokollneubau, nur dieselbe Textgroesse."""
    user = context.get("user", "") or ""
    own_context = context.get("own_context")
    table_view = context.get("table_view")
    total = len(user)
    if own_context:
        total += len(str(own_context)) + 20
    if table_view:
        total += len(json.dumps(table_view, ensure_ascii=False, sort_keys=True)) + 20
    return total


def reservation_for_request(
    driver: object, context: dict | None = None,
) -> tuple[float | None, bool]:
    """I2 (Case 05, MAIN-ENTSCHEIDUNG: 'Gesamtbudget Input+Output vor
    Versand pruefen+reservieren'): Gesamtreservierung AUS Input- UND
    Output-Anteil. Output-Anteil wie zuvor (`reservation_for_driver`s
    `driver.config.max_tokens`-Logik). Input-Anteil konservativ aus der
    TATSAECHLICHEN Anfragegroesse (system + user/table_view/own_context,
    dieselbe Textmenge, die tatsaechlich beim Empfaenger ankommt) geschaetzt
    -- Case 05: ein grosser Systemkontext OHNE Beruecksichtigung des
    Inputanteils unterlief bisher die Obergrenze (0,030015 USD trotz 0,02
    Budget, weil nur die Outputobergrenze reserviert wurde). `context=None`
    (Aufrufer ohne bereits gebauten Kontext) liefert nur die reine
    Outputreservierung -- unveraendert identisch zu `reservation_for_driver`.

    Liefert (reserved_usd, output_bound_known) (Q07-Fix, PLAN-CRITIC/
    MAIN-ENTSCHEIDUNG): `output_bound_known` ist NUR dann `True`, wenn der
    Treiber eine ECHTE, konfigurierte Ausgabeobergrenze traegt (z.B.
    `PersonaApiConfig.max_tokens`, IMMER gesetzt, Default 400) ODER der
    Treiber ueberhaupt kein `.config`-Objekt hat (Human-Driver -- verursacht
    laut Vertrag KEINE Modellkosten, s. `core/runtime.py:_bill_decision`,
    wird hier NICHT als 'unbounded-kostenpflichtig' behandelt). Ein Treiber
    MIT `.config`, aber OHNE erkennbares Ausgabelimit (Hybrid-CLI-Profil,
    `ClaudeCodeConfig` hat KEIN `max_tokens`-Feld) liefert `False` -- der
    Aufrufer (`read_admission_block`) lehnt eine solche Anfrage unter einer
    hart konfigurierten `max_usd`-Obergrenze ab, STATT die fehlende
    Ausgabegrenze stillschweigend als 0 zu behandeln (Case 07: 'Ohne
    konfigurierte UND durchsetzbare Gesamt-/Ausgabegrenze muss eine
    budgetlimitierte Hybrid-Anfrage abgelehnt werden, nicht Output=0
    behandelt')."""
    cfg = getattr(driver, "config", None)
    max_tokens = getattr(cfg, "max_tokens", None)
    has_known_output_bound = isinstance(max_tokens, (int, float)) and max_tokens > 0
    output_bound_known = (cfg is None) or has_known_output_bound
    out_usd = reservation_for_max_tokens(max_tokens) if has_known_output_bound else None
    in_usd = None
    if context is not None:
        system_text = context.get("system", "") or ""
        total_chars = len(system_text) + _estimate_wire_chars(context)
        if total_chars > 0:
            price_in, _ = _synthetic_prices()
            chars_per_token = _synthetic_chars_per_token()
            est_tokens = total_chars / chars_per_token if chars_per_token > 0 else 0.0
            in_usd = (est_tokens / 1000.0) * price_in
    if out_usd is None and in_usd is None:
        return None, output_bound_known
    return (out_usd or 0.0) + (in_usd or 0.0), output_bound_known


def reservation_for_wire_text(wire_text: str, output_limit_tokens: float | None = None) -> float:
    """I2 (Case 06, PLAN-CRITIC F2/F3, Auflage 1): Reservierung AUS DEM
    TATSAECHLICH zu sendenden Text (Body-Groesse, inkl. Historie/Save/
    Huelle) -- nicht der starren 0,015-USD-Pauschale. Schliesst den Fall, in
    dem ein grosser konsolidierter Wire-Text (Human-Aktion, GM-Body ist
    VIEL groesser als der Persona-Input) die feste Pauschale unterlaeuft
    (Test 06: 63.960 Zeichen erreichen den GM ungeprueft). Verwendbar fuer
    JEDE Rolle, die Text an einen Transport sendet, OHNE dass eine
    `driver.config.max_tokens`-Grenze existiert (GM-Transport,
    Erschaffungsdialog) -- `output_limit_tokens` optional, faellt ohne
    bekannte Grenze auf dieselbe Pauschale wie bisher zurueck (NICHT auf 0,
    Q07-Prinzip)."""
    price_in, price_out = _synthetic_prices()
    chars_per_token = _synthetic_chars_per_token()
    total_chars = len(wire_text or "")
    est_tokens = total_chars / chars_per_token if chars_per_token > 0 else 0.0
    in_usd = (est_tokens / 1000.0) * price_in
    out_usd = (
        reservation_for_max_tokens(output_limit_tokens)
        if isinstance(output_limit_tokens, (int, float)) and output_limit_tokens > 0
        else price_out
    )
    return in_usd + out_usd


def _has_recognized_authorization(data: dict) -> bool:
    """I2/A1 (MAIN-ENTSCHEIDUNG A1, PLAN-CRITIC F7): erkennt EXPLIZITE
    Autorisierung in `lab.status.json` -- entweder (a) ein sichtbar
    gesetztes providerfreies Testprofil (`write_test_profile`, zentral in
    der gemeinsamen Testinfrastruktur, `regressions/helpers_p2r.py:Rig`)
    ODER (b) eine ausdruecklich eingerichtete Betreiber-Live-/
    Budgetfreigabe (`lab.runner.LabRunner.start()` schreibt IMMER
    `max_turns`/`max_seconds`/`max_usd`, alle drei Pflichtfelder von
    `LabBudget` -- ein expliziter Operator-Start ZAEHLT bereits als
    Live-/Budgetfreigabe). KEIN Typ-Sniffing auf Driver/Fake-Adapter --
    reine Namens-/Feldpruefung derselben Datei, providerfrei."""
    if data.get("provider_free") is True:
        return True
    # Q04-Fix (PLAN-CRITIC/MAIN-ENTSCHEIDUNG, Test 04): ein vorhandenes
    # Limitfeld zaehlt nur als Autorisierung, wenn es ein ECHTER endlicher
    # Zahlenwert ist -- `{"max_usd": NaN}` ist strukturell KEINE gueltige
    # Freigabe (fail-closed statt "not None" ueber `NaN` durchzuwinken).
    return any(_is_finite_number(data.get(k)) for k in ("max_turns", "max_seconds", "max_usd"))


def write_test_profile(
    run_dir: str | Path, *, max_turns: int | None = None, max_seconds: float | None = None,
    max_usd: float | None = None,
) -> None:
    """I2/A1 (MAIN-ENTSCHEIDUNG A1, PLAN-CRITIC A1): EXPLIZITER, sichtbarer
    Setup-Aufruf fuer ein kontrolliertes providerfreies Testprofil --
    zentral in der gemeinsamen Testinfrastruktur aufgerufen
    (`regressions/helpers_p2r.py:Rig.ui`), KEIN Typ-Sniffing auf
    Fake-Adapter/Loopback (verboten, hebelt die synthetic-Hintertuer-
    Invariante aus). Schreibt `lab.status.json` (dieselbe Datei, die
    `lab.runner.LabRunner` fuer eine echte Betreiberfreigabe schreibt) mit
    `provider_free=True`. Ohne Budgetobergrenzen (Default `None`) bleibt
    die Requestzahl technisch unbegrenzt -- identisch zum bisherigen
    Verhalten OHNE `lab.status.json` (nur die Autorisierung selbst wird
    jetzt explizit belegt statt implizit aus Abwesenheit gefolgert, I2
    fail-closed). Ueberschreibt bewusst NICHT bereits vorhandene
    turns_used/usd_spent-Zaehler (Resume-vertraeglich, A1-Konsistenz)."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = _status_path(run_dir)
    data: dict = {}
    if status_path.exists():
        try:
            data = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("running", True)
    data.setdefault("pid", None)
    data.setdefault("turns_used", 0)
    data.setdefault("seconds_elapsed", 0.0)
    data.setdefault("usd_spent", 0.0)
    data.setdefault("stop_requested", False)
    data.setdefault("stop_reason", None)
    data.setdefault("usd_unknown_turns", 0)
    data["provider_free"] = True
    if max_turns is not None:
        data["max_turns"] = max_turns
    if max_seconds is not None:
        data["max_seconds"] = max_seconds
    if max_usd is not None:
        data["max_usd"] = max_usd
    _atomic_write_json(status_path, data)


def read_admission_block(
    run_dir: str | Path, reserved_usd: float | None = None, *,
    output_bound_known: bool = True, route: str | None = None, dollar_billed: bool = True,
) -> tuple[bool, str | None]:
    """Vor JEDEM Modellrequest aufzurufen (I1 Plan §1 Punkt 7). Liefert
    `(blocked, reason)`.

    I2/A1-Fix (MAIN-ENTSCHEIDUNG, PLAN-CRITIC F5/F7, Case 04): FAIL-CLOSED
    -- fehlende ODER kaputte `lab.status.json` heisst ab jetzt KEINE
    Freigabe (`(True, reason)`), NICHT mehr '(False, None), keine
    Einschraenkung' (der alte Zustand liess einen echten Persona-HTTP- UND
    GM-Request durch, obwohl weder ein providerfreies Testprofil noch eine
    Betreiber-Live-/Budgetfreigabe existierte). Eine Anfrage ist nur mit
    EXPLIZITER Autorisierung zulaessig: (a) ein sichtbar gesetztes
    providerfreies Testprofil (`write_test_profile`) ODER (b) eine
    ausdruecklich eingerichtete Betreiber-Live-/Budgetfreigabe
    (`lab.runner.LabRunner.start()`) -- s. `_has_recognized_authorization`.
    Toolisolation (I3 `check_isolation`) ersetzt diese Freigabe NIE (auch
    ein isolierter CLI-Call verbraucht Kontingent).

    W2-Ergaenzung (F..., Test 04/05): `reserved_usd` ist eine optionale,
    ANFRAGEBEZOGENE Vor-Versand-Reservierung (s. `reservation_for_request`)
    -- der Aufrufer, der die konkrete Route/Konfiguration der naechsten
    Anfrage kennt, kann eine praezisere Schaetzung als die Pauschale
    liefern. Ohne Angabe (Default `None`) bleibt die Pauschalreservierung
    (ein `price_out` je unbekannter Anfrage) unveraendert erhalten.

    Q07-Fix (PLAN-CRITIC/MAIN-ENTSCHEIDUNG, bindend): `output_bound_known`
    (s. `reservation_for_request`) -- `False` heisst "dieser Treiber hat
    UEBERHAUPT KEIN Mittel, seine Ausgabemenge zu begrenzen" (Hybrid-CLI-
    Profil ohne Tokenparameter). Ist DANN zusaetzlich ein hartes `max_usd`
    konfiguriert, wird die Anfrage abgelehnt -- eine fehlende Grenze darf
    unter einer harten Dollarobergrenze NICHT stillschweigend als 0
    behandelt werden (Hybrid DARF weiterhin ueber Kontingent-/Request-/
    Zeitgrenzen ohne erfundenen API-Dollar laufen, 03 §4).

    Q03-Fix (PLAN-CRITIC F5/Auflage, MAIN-ENTSCHEIDUNG bestaetigt): `route`
    (optional, die tatsaechliche Zieladresse dieser konkreten Anfrage) wird
    NUR unter einer providerfreien Testprofil-Autorisierung (`provider_free
    =True`) geprueft -- ein solches Profil gibt NUR kontrollierte Loopback-
    Antwort-/Prozessdoubles frei, niemals eine beliebige konfigurierte
    externe Route. Eine echte Betreiber-Live-/Budgetfreigabe ist davon nicht
    betroffen (eigener, hier nicht beruehrter Live-Vertrag).

    G2b-Ergaenzung (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27,
    ANSCHLUSSPLAN-HEADLESS.md ERGAENZUNG 2): `dollar_billed` (Default `True`,
    unveraendertes Verhalten fuer alle bestehenden Aufrufer) -- `False`
    bedeutet "dieser KONKRETE Request laeuft ueber eine CLI-/Abo-Rolle mit
    eigenen Turn-/Zeit-/Kontingentgrenzen und UNBEKANNTER Quota (H-E), NICHT
    ueber ein abgerechnetes API". `turns_used`/`seconds_elapsed`/
    `wall_deadline`/`stop_requested` gaten UNVERAENDERT fuer JEDE Rolle --
    NUR der Q07-Output-Bound-Zwang UND die `usd_spent`/`max_usd`-Pruefung
    werden fuer `dollar_billed=False` uebersprungen. Ohne diese Trennung
    wuerde ein fuer die GM-Rolle (H08: "GM weiterhin Loopback-HTTP", IMMER
    dollarbegrenzt) benoetigtes hartes `max_usd` unter Hybrid JEDE
    CLI-Personaanfrage blockieren (`PersonaClaudeCodeDriver`/
    `ClaudeCodeConfig` traegt kein `max_tokens`-Feld, also
    `output_bound_known=False` -- Q07 wuerde sonst faelschlich JEDE
    Nicht-API-Rolle als 'unbegrenzt ausgebender Treiber' ablehnen, obwohl sie
    strukturell gar kein Dollarbudget verbraucht). Der Aufrufer bestimmt
    `dollar_billed` je Request aus dem TATSAECHLICH verwendeten Treiber
    (`getattr(driver, 'is_dollar_billed', True)`, s. `core.runtime.
    SectionRuntime._admitted_decision`/`core.lobby_service.
    request_admitted_decision`) -- die GM-Rolle selbst setzt es nicht
    explizit (Default `True` trifft bereits zu, `GmOwuiTransport` hat keinen
    solchen Marker und ist IMMER dollarbegrenzt)."""
    run_dir = Path(run_dir)

    stop_path = _stop_flag_path(run_dir)
    if stop_path.exists():
        try:
            data = json.loads(stop_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        return True, data.get("reason") or "Lab-Stop aktiv (persistiert)"

    status_path = _status_path(run_dir)
    if not status_path.exists():
        return True, (
            "Keine lab.status.json vorhanden -- weder providerfreies Testprofil noch "
            "Betreiber-Live-/Budgetfreigabe (I2 fail-closed, A1)."
        )
    try:
        data = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, "lab.status.json beschaedigt/nicht lesbar -- keine Freigabe (I2 fail-closed, A1)."

    if not isinstance(data, dict) or not _has_recognized_authorization(data):
        return True, (
            "lab.status.json ohne erkennbares Autorisierungsprofil (weder provider_free=True "
            "noch max_turns/max_seconds/max_usd als endliche Zahl) -- keine Freigabe "
            "(I2 fail-closed, A1)."
        )

    if route is not None and data.get("provider_free") is True and not _route_is_controlled(route):
        return True, (
            f"Providerfreies Testprofil autorisiert keine externe Route ({route!r}) -- nur "
            f"kontrollierte Test-Doubles/Loopback-Routen sind gedeckt (I2 Q03, A1)."
        )

    # Q04-Fix (PLAN-CRITIC/MAIN-ENTSCHEIDUNG, Test 04): jedes vorhandene
    # Zaehler-/Limitfeld muss ein ECHTER endlicher Zahlenwert sein -- ein
    # beschaedigter/nicht-numerischer Wert (NaN, falscher Typ, ...) gilt als
    # kaputter Zustand (fail-closed), NICHT als "keine Grenze"/gueltiger
    # Zaehler.
    for counter_key in ("turns_used", "seconds_elapsed", "usd_spent"):
        if counter_key in data and not _is_finite_number(data.get(counter_key)):
            return True, (
                f"lab.status.json: {counter_key} kein gueltiger endlicher Zahlenwert -- "
                f"beschaedigter Zustand, keine Freigabe (I2 fail-closed, Q04)."
            )
    for limit_key in ("max_turns", "max_seconds", "max_usd", "wall_deadline"):
        if data.get(limit_key) is not None and not _is_finite_number(data.get(limit_key)):
            return True, (
                f"lab.status.json: {limit_key} kein gueltiger endlicher Zahlenwert -- "
                f"beschaedigter Zustand, keine Freigabe (I2 fail-closed, Q04)."
            )

    turns_used = data.get("turns_used", 0)
    seconds_elapsed = data.get("seconds_elapsed", 0.0)
    usd_spent = data.get("usd_spent", 0.0)
    max_turns = data.get("max_turns")
    max_seconds = data.get("max_seconds")
    max_usd = data.get("max_usd")
    wall_deadline = data.get("wall_deadline")

    if max_turns is not None and turns_used >= max_turns:
        return True, f"max_turns erreicht ({max_turns}, frisch von Platte)"
    if max_seconds is not None and seconds_elapsed >= max_seconds:
        return True, f"max_seconds erreicht ({max_seconds}, frisch von Platte)"
    # G2b (Bau-GO 2026-09-27): der Q07-Output-Bound-Zwang UND die
    # `usd_spent`/`max_usd`-Pruefung gelten NUR fuer dollarbepflichtete
    # Rollen (Default `True`, unveraendert fuer alle Aufrufer ohne diesen
    # Parameter, unveraenderte relative Pruefreihenfolge zu max_turns/
    # max_seconds) -- s. Docstring oben. `wall_deadline`/`stop_requested`
    # bleiben UNVERAENDERT fuer JEDE Rolle wirksam (weiter unten).
    if dollar_billed and max_usd is not None and not output_bound_known:
        return True, (
            "Kein durchsetzbares Ausgabe-/Gesamtlimit fuer diesen Treiber ermittelbar "
            f"(z.B. Hybrid-CLI-Profil ohne Tokenparameter) UND hartes max_usd ({max_usd}) "
            "konfiguriert -- fehlende Grenze wird NICHT als 0 behandelt, Anfrage abgelehnt "
            "(I2 Q07, A1)."
        )
    if dollar_billed and max_usd is not None:
        if usd_spent >= max_usd:
            return True, f"max_usd erreicht ({max_usd}, frisch von Platte)"
        # A1 (WEGKARTE §6/§7 Plan-Critic-Auflage, R12-Restintegrationsfix):
        # Vor-Versand-Reservierung MIT DEMSELBEN `_synthetic_prices()`-Tarif
        # wie die Nachher-Verbuchung fuer unbekannte Kosten
        # (`compute_turn_usd`/`record_turn_usage`) -- sonst driften Vor- und
        # Nachher-Schaetzung auseinander. Wuerde eine konservativ geschaetzte
        # naechste Anfrage (unbekannte Kosten) die Obergrenze ueberschreiten,
        # wird SIE GAR NICHT ERST GESENDET (Test 12: `gm.calls<=1`).
        #
        # W2-Fix (F..., Test 04): eine vom Aufrufer mitgegebene
        # ANFRAGEBEZOGENE Reservierung (`reserved_usd`, s.
        # `reservation_for_driver`) ersetzt die Pauschale, wenn bekannt --
        # eine konfigurierte Ausgabeobergrenze von z.B. 10000 Tokens kostet
        # im schlimmsten Fall spuerbar mehr als die pauschale Ein-Turn-
        # Schaetzung und darf die Anfrage NICHT unter der Pauschale
        # durchrutschen lassen.
        if reserved_usd is None:
            _, price_out = _synthetic_prices()
            reserved_usd = price_out
        if usd_spent + reserved_usd > max_usd:
            return True, (
                f"Vor-Versand-Reservierung: naechste Anfrage (konservativ {reserved_usd} USD, "
                f"gleicher Tarif wie record_turn_usage) wuerde max_usd ({max_usd}) "
                f"ueberschreiten — frisch von Platte."
            )
    # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27, ANSCHLUSSPLAN-HEADLESS.md
    # Entscheidung 4: "Stop + Deadline werden vor JEDEM Request frisch
    # geprueft ... NICHT NUR ZWISCHEN ZWEI FENSTERN"): `wall_deadline`
    # (`lab.runner.LabRunner.start()` schreibt sie EINMAL als ABSOLUTEN
    # `time.time()`-Wert aus `--max-wall-seconds`, s. `LabStatus.
    # wall_deadline`-Docstring) wird HIER -- am tatsaechlichen Gate vor
    # JEDEM Persona-/GM-/Reflexions-/Initiative-/Consent-Request -- frisch
    # von der Platte geprueft. Vorher lebte diese Grenze NUR als lokale
    # `time.monotonic()`-Variable in `lab.cli._run_controller`s eigener
    # Fensterschleife und wirkte deshalb erst NACH einem bereits laufenden,
    # ggf. sehr langsamen Request des aktuellen Fensters.
    if wall_deadline is not None and time.time() >= wall_deadline:
        return True, (
            f"reale Laufzeitgrenze (Wall-Clock) erreicht (Deadline {wall_deadline}, "
            "frisch von Platte, H-E)."
        )
    if data.get("stop_requested"):
        return True, data.get("stop_reason") or "Lab-Budget erschoepft (persistiert)"
    return False, None


def record_turn_usage(
    run_dir: str | Path, seconds: float, usd: float | None, *, require_authority: bool = False,
) -> None:
    """Nach einem ECHTEN GM-Turn aufzurufen (`core/runtime.py:submit`, ueber
    `request_ledger.begin()`). Rein dateibasiert (A1-Konsistenz).

    G1-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 02): `require_authority=True` (von
    `request_ledger.begin()`, dem einzigen buchungspflichtigen
    Reservierungsweg, IMMER gesetzt) macht eine fehlende `lab.status.json`
    zu einem ECHTEN Fehler statt eines stillen No-op -- der vorgelagerte
    Gatecheck (`read_admission_block`) hat zu diesem Zeitpunkt bereits ein
    gueltiges Profil verlangt/gelesen; verschwindet die Datei GENAU an
    dieser Stelle (z.B. externe Loeschung), darf `begin()` keinen scheinbar
    versandbereiten Auftrag (`state=sent`) liefern -- der Aufrufer erreicht
    sonst den tatsaechlichen GM-/Persona-Transport, OBWOHL keine
    Reservierung gebucht wurde. `require_authority=False` (Default) bleibt
    fuer einen etwaigen zukuenftigen reinen Offline-Telemetrie-Aufrufer
    OHNE vorgelagertes Gate ein legitimer No-op -- diese Funktion hat
    aktuell aber NUR EINEN Aufrufer (`request_ledger.begin()`), der immer
    `require_authority=True` setzt.

    B-Fix (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-BUCHUNGSGRENZEN.md
    §4 Fall 04): ein Read-/Parsefehler einer VORHANDENEN `lab.status.json`
    ist KEIN No-op, sondern propagiert ungefangen an den Aufrufer
    (`request_ledger.begin()`, s. dessen Docstring) -- ein Reservierungs-
    Lesefehler darf `begin()` keinen scheinbar versandbereiten Auftrag
    (`state=sent`) liefern lassen, sonst erreicht der Aufrufer den
    tatsaechlichen GM-/Persona-Transport, OBWOHL keine Reservierung gebucht
    wurde.

    A9/D4 (WEGKARTE §8, Vertrag 03 §6 "In-flight Kosten konservativ
    beruecksichtigen"): `usd=None` ("unknown", s. `compute_turn_usd`) wird
    NICHT als 0.0 verbucht -- fuer die Budget-PRUEFUNG (`max_usd`) zaehlt
    stattdessen konservativ der synthetische Completion-Tarif fuer eine
    Referenzmenge Output-Tokens (kein Unterlaufen der Obergrenze durch
    unbeobachtbare Kosten); `usd_unknown_turns` macht die Schaetzung
    getrennt sichtbar (kein stiller "0.0 USD"-Bluff)."""
    run_dir = Path(run_dir)
    status_path = _status_path(run_dir)
    if not status_path.exists():
        if require_authority:
            raise FileNotFoundError(
                f"lab.status.json fehlt bei {status_path} -- eine buchungspflichtige "
                "Reservierung (request_ledger.begin) verlangt bereits bestehende Autoritaet "
                "(G1 fail-closed, kein stiller Offline-No-op im Requestweg, REVIEW-"
                "RESERVIERUNGSABSCHLUSS.md §4 Fall 02)."
            )
        return
    data = json.loads(status_path.read_text(encoding="utf-8"))
    data["turns_used"] = data.get("turns_used", 0) + 1
    data["seconds_elapsed"] = data.get("seconds_elapsed", 0.0) + seconds
    if usd is None:
        data["usd_unknown_turns"] = data.get("usd_unknown_turns", 0) + 1
        _, price_out = _synthetic_prices()
        data["usd_spent"] = data.get("usd_spent", 0.0) + price_out
    else:
        data["usd_spent"] = data.get("usd_spent", 0.0) + usd
    _atomic_write_json(status_path, data)


def record_usd_delta(run_dir: str | Path, request_id: str, delta: float) -> None:
    """E5 (Auflage 5, MAIN-ENTSCHEIDUNG I2-Nachzug GM-Weg) + B1 (MAIN-
    KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3): bucht eine
    NACHTRAEGLICHE Korrektur nach, wenn der real via `compute_turn_usd`
    ermittelte Betrag die VOR dem Versand committete Reservierung
    ueberschreitet (`core.request_ledger.finish_received`) -- rein additiv
    auf `usd_spent`, OHNE `turns_used` erneut zu erhoehen (der Turn wurde
    bereits in `begin()`/`record_turn_usage` gezaehlt, kein Doppel-
    Anrechnen). Nie negativ aufgerufen (Aufrufer bucht nur `real > reserved`,
    Case 05: 'Reservierung bleibt bei Antwortverlust/geringerem Verbrauch
    erhalten, kein Refund').

    No-op NUR in zwei EXPLIZIT legitimen Faellen: (1) `not delta` -- es gibt
    gar nichts zu buchen; (2) `request_id` steht bereits in
    `reconciled_request_ids` -- das Delta wurde nachweislich schon
    angewandt (Idempotenz, s.u.). Fehlende/nicht lesbare/ungueltige
    `lab.status.json` bei OFFENEM Delta ist KEIN dritter No-op-Fall mehr
    (A-Fix, MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-BUCHUNGSGRENZEN.md
    §3 Fall 02: die fehlende Buchungsautoritaet ist kein erfolgreicher
    Abschluss -- das fruehere `if not status_path.exists(): return` liess
    `finish_received` faelschlich `state=accounted` setzen, OBWOHL das reale
    Delta nie gebucht wurde). JEDER Fehler beim Lesen/Schreiben von
    `lab.status.json` (fehlende Datei, `OSError`, `json.JSONDecodeError`)
    propagiert deshalb ungefangen an den Aufrufer -- `status_path.
    read_text()` wirft von selbst `FileNotFoundError` (eine `OSError`-
    Unterklasse), kein expliziter `exists()`-Vorabcheck mehr noetig. Der
    Aufrufer (`finish_received`) faengt diese Ausnahme NICHT ab -- der
    Requestdatensatz bleibt dadurch ehrlich `received` (offen), bis ein
    Retry (frischer Prozess/erneuter Aufruf, dieselbe `request_id`) das
    Delta tatsaechlich bucht (keine Doppelzaehlung, da `reconciled_
    request_ids` den Retry bereits vor einer zweiten Buchung schuetzt).

    B1-Fix: der Aufrufer (`finish_received`) berechnet `delta` bei JEDEM
    Aufruf (auch einem Retry nach Prozessabsturz/-neustart fuer DIESELBE
    `request_id`) neu aus dem stabilen, bereits geladenen Requestdatensatz --
    OHNE selbst zu wissen, ob dieses Delta bereits angewandt wurde. DIESE
    Funktion ist deshalb die alleinige Idempotenz-Instanz: sie prueft+bucht+
    markiert `request_id` als angewandt in EINEM einzigen ATOMAREN
    Schreibvorgang auf `lab.status.json` (`LabStatus.reconciled_request_ids`,
    R2: Temp-Datei + `os.replace`, s. `_atomic_write_json`) -- ein Absturz
    VOR diesem Write (Fall 02, REVIEW-I2.md §3) hinterlaesst weder eine
    Buchung noch eine Markierung (Retry bucht real nach, da der propagierte
    Fehler `finish_received` daran hindert, `accounted` zu setzen); ein
    Absturz NACH diesem Write, aber vor dem naechsten `_write_request`-
    Aufruf in `finish_received` (Fall 03), hinterlaesst BEIDES bereits
    konsistent (Retry erkennt `request_id` bereits in
    `reconciled_request_ids` und bucht nicht doppelt). Ein gewoehnlicher
    Teilschreibfehler WAEHREND dieses Writes zerstoert dank R2 nicht mehr
    den zuletzt gueltigen Stand (`_atomic_write_json` laesst `path` bei
    einem Fehler unveraendert) -- es gibt kein Fenster, in dem eine
    Markierung ohne die zugehoerige Buchung (oder umgekehrt) bestehen
    bleiben kann, weil beides in derselben atomaren Operation passiert."""
    if not delta:
        return
    run_dir = Path(run_dir)
    status_path = _status_path(run_dir)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    reconciled = data.get("reconciled_request_ids")
    if not isinstance(reconciled, list):
        reconciled = []
    if request_id in reconciled:
        return
    data["usd_spent"] = data.get("usd_spent", 0.0) + delta
    reconciled.append(request_id)
    data["reconciled_request_ids"] = reconciled
    _atomic_write_json(status_path, data)


def add_seconds(run_dir: str | Path, request_id: str, seconds: float) -> None:
    """I2-Nachzug (`core/request_ledger.py`): reine Latenz-Nachtragung NACH
    Abschluss eines Requests, dessen Turn-/USD-Verbrauch bereits VOR dem
    Versand ueber `record_turn_usage` committet wurde (Case 05: Reservierung
    passiert VOR dem Request, nicht erst nach einer Antwort) -- vermeidet
    ein zweites `turns_used`/`usd_spent`-Anrechnen fuer DIESELBE Anfrage
    (Auflage 6, kein Doppel-Anrechnen).

    G3-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 04/05): KEIN stiller No-op mehr bei
    fehlender/nicht lesbarer/ungueltiger `lab.status.json` -- der einzige
    Aufrufer (`request_ledger.finish_received`/`finish_error`) ruft diese
    Funktion erst NACH einem bereits erfolgreich autorisierten `begin()`
    auf (das seit dem G1-Fix `require_authority=True` verlangt); eine
    anschliessend verschwundene/kaputte Datei ist deshalb kein legitimer
    Offline-Fall mehr, sondern ein Fehlerzustand -- Lese-/Parsefehler
    propagieren ungefangen an den Aufrufer (analog `record_usd_delta`,
    `status_path.read_text()` wirft von selbst `FileNotFoundError`, eine
    `OSError`-Unterklasse). `finish_received` faengt das NICHT ab: der
    Requestdatensatz bleibt ehrlich `received` (offen) statt faelschlich
    `accounted` mit `seconds_elapsed=0` (Fall 04).

    `request_id`-Deduplizierung (Fall 05): dieselbe Idempotenz-Idee wie
    `record_usd_delta`s `reconciled_request_ids`, aber in einer EIGENEN
    Liste (`reconciled_seconds_request_ids`) -- Zeit- und Geld-Wirkung
    sind unabhaengige Effekte DESSELBEN Requests und duerfen sich beim
    Dedup-Marker nicht gegenseitig blockieren (ein Retry, bei dem nur die
    Geld-Buchung bereits angewandt war, muss die Zeit trotzdem noch genau
    einmal nachtragen, und umgekehrt). Ein Retry NACH einem Fehler vor dem
    finalen Requestmarker (dieselbe `request_id`, derselbe `seconds`-Wert)
    findet die ID bereits in `reconciled_seconds_request_ids` und laesst
    `seconds_elapsed` unveraendert (Fall 05: bleibt bei 2, wird nicht 4)."""
    if not seconds:
        return
    run_dir = Path(run_dir)
    status_path = _status_path(run_dir)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    applied = data.get("reconciled_seconds_request_ids")
    if not isinstance(applied, list):
        applied = []
    if request_id in applied:
        return
    data["seconds_elapsed"] = data.get("seconds_elapsed", 0.0) + seconds
    applied.append(request_id)
    data["reconciled_seconds_request_ids"] = applied
    _atomic_write_json(status_path, data)
