#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_input_contract_2026_10_06.py -- ZEITRISS Terminal
UX1 F02 (W18, BRIEF-W18.md): die noch offenen ROHEN Spieler-Eingabepfade in
`mmo_sim/ui/tui.py` sind jetzt an den zentralen Steuervertrag
(`TuiSession._readline_with_controls`) gebunden. Deckt dauerhaft:

  - Figurwahl/`neu`/`fortsetzen:<id>` (`_cmd_new_or_switch_character`):
    Name+stabile-Nummer-Auflösung gegen den autoritativen Katalog-Leser
    (inkl. Namensdublette), ID bleibt Detail-/Kompatibilitätsweg, `/hilfe`
    etc. nie als ID/Name, Steuerzeile = 0 Writes (kein Figurwechsel, kein
    Erschaffungs-/Importturn).
  - Frischstart-Einladung (`_invite_persona_fresh_start`): Persona-ID-Prompt
    über den Vertrag, leere Eingabe = kein Vorgang, Steuerzeile = 0 Calls
    (Fabrikfunktionen nie aufgerufen).
  - Beide Importkonflikte in `_cmd_import` (`Wahl [a/k]`, `Wahl [w/b]`):
    Hilfe/Steuerzeile vor dem jeweils gegateten Write (`import_export.
    resolve_import`-Übernahme bzw. `catalog.register`-Aktivwechsel);
    escapeter Literaltext bleibt bewusst normaler Text (bestehender
    Escape-Vertrag, kein neues Sonderverhalten).
  - Herkunftswahl (`_ask_live_starter_origin_choice`): `/hilfe` zeigt
    echten Hilfetext statt stillem `None`; Steuerzeilen fallen auf denselben
    bestehenden `None`-Vertrag zurück wie jede andere nicht passende
    Eingabe (keine neue Sonderbedeutung, keine Calls).
  - KI-Vorlauf-Angebot (`_maybe_offer_bounded_preflight`, Brief-Punkt 5):
    Steuerzeile startet keinen Vorlauf (synthetisch, kein Call).
  - Allgemeine Randfälle: leeres stdin propagiert `EndOfInput` (kein
    Endlosloop); literales `x`/`q`/ein `?` mitten im Satz/escaped `\\/...`
    bleiben Text, wo Text erwartet wird; eine Mehrzeilen-JSON-Paste wird
    NICHT global pro Zeile als Steuerzeile gewertet (nur die ERSTE Zeile
    bleibt die bestehende Sonderprüfung, unverändert von W18).

Isolationsdisziplin (wie `test_ux1_r5_redaction_hold_pair_2026_10_06.py`):
eigenes temporaeres HOME/XDG_* VOR jedem Produktimport, ein Netzwerk-Guard
VOR jedem Produktimport -- bewusst NUR `socket.socket.connect`/`connect_ex`/
`socket.create_connection`/`socket.getaddrinfo` geblockt (NICHT `socket.
socket` selbst ersetzt, das wuerde `ssl` brechen, s. BRIEF-W17.md
§Isolationsregel). Alle GM-/Persona-Fabriken in diesem Modul sind
Testdoubles, die bei unerwartetem Aufruf sofort fehlschlagen (`_assert_
never_called`) -- kein echter Modell-/Providercall ist erreichbar. Pure
Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="ux1-r5-w18-isolated-home-")
_ORIGINAL_ENV_SNAPSHOT = {
    k: os.environ.get(k) for k in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME")
}
os.environ["HOME"] = _ISOLATED_HOME_DIR.name
os.environ["XDG_DATA_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-data")
os.environ["XDG_CONFIG_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-config")
os.environ["XDG_CACHE_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-cache")
for _leaky_key in list(os.environ):
    if _leaky_key.startswith("MMO_SIM_PERSONA_") or _leaky_key.startswith("OPENWEBUI_"):
        os.environ.pop(_leaky_key, None)

# --- Netzwerk-Guard: VOR jedem Produktimport aktiv, OHNE socket.socket zu
# ersetzen (bricht sonst `ssl`, s. BRIEF-W17.md §Isolationsregel). ---
# W26-Hinweis (BRIEF-W26.md §1, s. Negativprobe unten): `socket.SocketType`
# ist in CPython der UNVERAeNDERLICHE C-Basistyp (`_socket.socket`) -- ein
# Schreibzugriff auf sein `.connect`-Attribut wirft selbst `TypeError:
# cannot set ... of immutable type`. Der except-Zweig darf `SocketType`
# daher NUR LESEND (fuer die spaetere Restore-Referenz) verwenden, NIE als
# Patchziel. Patchziel bleibt bewusst `socket.socket` (das AKTUELLE Attribut
# -- die normale, mutable Python-Wrapperklasse im Regelfall; ist dieses
# Attribut bereits durch ein anderes Modul ersetzt worden, sonst waere der
# Lesezugriff gar nicht auf AttributeError gelaufen, blockiert bereits
# JENER Ersatz jede Socketkonstruktion ueber den oeffentlichen `socket.
# socket(...)`-Weg -- die Negativprobe unten belegt genau diese
# Gesamtwirkung end-to-end, statt nur den Importcrash zu vermeiden).
try:  # robust unter unittest-Discovery, falls ein anderes Modul socket.socket ersetzt hat
    _REAL_SOCKET_CONNECT = socket.socket.connect
    _REAL_SOCKET_CONNECT_EX = socket.socket.connect_ex
except AttributeError:
    import socket as _s_mod
    _REAL_SOCKET_CONNECT = _s_mod.SocketType.connect
    _REAL_SOCKET_CONNECT_EX = _s_mod.SocketType.connect_ex
_REAL_CREATE_CONNECTION = socket.create_connection
_REAL_GETADDRINFO = socket.getaddrinfo


def _network_blocked(*_a, **_k):
    raise OSError("Netzwerk in isoliertem W18-Testlauf blockiert (kein Live-/Providercall).")


socket.socket.connect = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.socket.connect_ex = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.create_connection = _network_blocked  # type: ignore[assignment]
socket.getaddrinfo = _network_blocked  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _assert_never_called(*_a, **_k):
    raise AssertionError("diese Fabrikfunktion/dieser Aufruf haette NICHT erreicht werden duerfen")


def _figure_save(char_id: str, level: int = 1) -> dict:
    # R12-Fix: kanonischer, gegen BEIDE v7-Schemas gueltiger Block statt
    # des alten Minimalfakes (fehlende Export-Pflichtfelder) -- genutzt
    # sowohl fuer die direkte Katalogschreibung ohne Validierung
    # (`_register_figure`) als auch fuer die via json.dumps() durch den
    # echten Import-Textpfad geschickten Instanzen; dieselbe Form auf
    # beiden Seiten haelt die Vorher/Nachher-Gleichheitsvergleiche konsistent.
    return full_v7_save(char_id, name=char_id, callsign=char_id.upper(), level=level)


def _register_figure(catalog_dir: Path, pid: str, char_id: str, *, display_name: str = "", level: int = 1, active: bool = False) -> dict:
    save = _figure_save(char_id, level=level)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=pid, chrononaut_id=char_id, persona_key=pid, display_name=display_name,
    ))
    catalog.store_figure_save(catalog_dir, pid, char_id, save)
    if active:
        catalog.bind_for_section(catalog_dir, pid, char_id, has_open_section=False)
    return save


def _sess(d: Path, pid: str, lines: list[str], printed: list[str]) -> TuiSession:
    return TuiSession(
        onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id=pid,
        input_fn=_scripted_input(lines), print_fn=printed.append,
    )


# ---------------------------------------------------------------------------
# Guard-Discovery-Negativprobe (W26-Haertung, BRIEF-W26.md §1): W23 ("letzte
# Reserve") hat NUR den AttributeError-Importcrash unter `unittest`-Discovery
# abgefangen (try/except -> Lesezugriff auf `SocketType` statt `socket.
# socket`), aber NIE per Test belegt, dass der Guard in GENAU dieser
# Reihenfolge (ein zuvor importiertes Testmodul hat `socket.socket` bereits
# komplett ersetzt, z.B. wie `test_ux1_r5_error_surface_redaction_2026_10_06.
# py`) weiterhin ECHT blockiert statt nur crash-frei durchzulaufen. Diese
# Probe bildet GENAU diese Discovery-Kollision nach und prueft die End-zu-
# End-Wirkung ueber den OEFFENTLICHEN `socket.socket(...)`-Konstruktionsweg
# (den jeder reale Aufrufer -- Produktcode, `http.client`, `requests` --
# tatsaechlich benutzt) statt ueber `socket.SocketType` direkt: `SocketType`
# ist in CPython der UNVERAeNDERLICHE C-Basistyp, ein Patch-/Verbindungs-
# versuch DURCH DIESE PROBE darauf waere selbst kein realistischer Pfad.
# Laeuft bewusst in einem echten Python-Kindprozess, NICHT im laufenden
# Testprozess -- die hier absichtlich herbeigefuehrte Vorbedingung (`socket.
# socket` global ersetzt) wuerde im eigenen Prozess jeden nachfolgenden
# Test/anderes Modul unter derselben `unittest`-Discovery vergiften; im Kind
# betrifft das nur dessen eigenen, isolierten Zustand.
# ---------------------------------------------------------------------------

_GUARD_DISCOVERY_NEGATIVE_PROBE_CHILD_SCRIPT = r'''
import json
import socket

report = {"checks": {}}

# 1) Exakte W23-Vorbedingung nachbilden: ein zuvor importiertes Testmodul hat
# socket.socket bereits durch eine blosse Funktion ersetzt (kein eigenes
# `.connect`-Attribut mehr) -- der Zustand, an dem die alte Zweizeiler-
# Erfassung mit AttributeError crashte.
def _prior_module_replacement(*_a, **_k):
    raise RuntimeError("anderes Modul hat socket.socket bereits ersetzt")


socket.socket = _prior_module_replacement

# 2) Dieselbe robuste Lese-Sequenz wie im Testfile (reine Testinfrastruktur-
# Nachbildung, kein Produktcode) -- der Lesezugriff faellt unter dieser
# Vorbedingung auf `SocketType` zurueck (nur LESEND, s. Kommentar oben zur
# Unveraenderlichkeit), der anschliessende Patchversuch bleibt bewusst auf
# `socket.socket` (das AKTUELLE Attribut) gerichtet.
setup_crashed = False
try:
    try:
        _real_connect = socket.socket.connect
        _real_connect_ex = socket.socket.connect_ex
    except AttributeError:
        _real_connect = socket.SocketType.connect
        _real_connect_ex = socket.SocketType.connect_ex

    def _network_blocked(*_a, **_k):
        raise OSError("Netzwerk in isoliertem Testlauf blockiert (kein Live-/Providercall).")

    socket.socket.connect = lambda *a, **k: _network_blocked()
    socket.socket.connect_ex = lambda *a, **k: _network_blocked()
    socket.create_connection = _network_blocked
    socket.getaddrinfo = _network_blocked
except AttributeError as exc:
    setup_crashed = True
    report["checks"]["setup_crash"] = {"ok": False, "detail": repr(exc)}

report["checks"]["setup_survives_prior_replacement"] = {
    "ok": not setup_crashed,
    "detail": "Setup-Sequenz crasht NICHT trotz bereits ersetztem socket.socket (W23-Szenario)",
}

# 3) Echter End-zu-End-Schutzbeleg ueber den OEFFENTLICHEN Konstruktionsweg:
# `socket.socket(...)` ist zu diesem Zeitpunkt die Ersatzfunktion aus
# Schritt 1 -- jeder Aufrufer, der eine Verbindung aufbauen will, MUSS durch
# sie hindurch. Sie muss weiterhin zuverlaessig blockieren (nicht nur
# "nicht crashen"); eine falsche/fehlende Blockade hier waere die stille
# Schutzluecke, die W23 NICHT geprueft hat.
try:
    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocked, detail = False, "kein Fehler ausgeloest -- Guard NICHT wirksam"
except RuntimeError as exc:
    blocked, detail = ("bereits ersetzt" in str(exc)), repr(exc)
except Exception as exc:  # noqa: BLE001 -- jeder andere Fehlertyp ist KEIN Guard-Beleg
    blocked, detail = False, f"unerwarteter Fehlertyp statt Guard-Blockade: {exc!r}"
report["checks"]["socket_construction_still_blocked"] = {"ok": blocked, "detail": detail}

try:
    socket.create_connection(("198.51.100.1", 80))
    blocked2, detail2 = False, "kein Fehler ausgeloest -- create_connection NICHT blockiert"
except OSError as exc:
    blocked2, detail2 = ("blockiert" in str(exc)), repr(exc)
except Exception as exc:  # noqa: BLE001
    blocked2, detail2 = False, f"unerwarteter Fehlertyp statt Guard-OSError: {exc!r}"
report["checks"]["create_connection_still_blocked"] = {"ok": blocked2, "detail": detail2}

try:
    socket.getaddrinfo("198.51.100.1", 80)
    blocked3, detail3 = False, "kein Fehler ausgeloest -- getaddrinfo NICHT blockiert"
except OSError as exc:
    blocked3, detail3 = ("blockiert" in str(exc)), repr(exc)
except Exception as exc:  # noqa: BLE001
    blocked3, detail3 = False, f"unerwarteter Fehlertyp statt Guard-OSError: {exc!r}"
report["checks"]["getaddrinfo_still_blocked"] = {"ok": blocked3, "detail": detail3}

print(json.dumps(report))
'''


def test_guard_discovery_survives_prior_socket_replacement_in_child():
    """W26-Haertung: ein echter Python-Kindprozess bildet GENAU die W23-
    Discovery-Vorbedingung nach (ein anderes Modul hat `socket.socket`
    bereits ersetzt) und belegt, dass die robuste Lese-Sequenz dabei NICHT
    nur crash-frei importiert (W23-Stand), sondern dass der oeffentliche
    `socket.socket(...)`-Konstruktionsweg UND `socket.create_connection`/
    `socket.getaddrinfo` in genau dieser Reihenfolge weiterhin wirklich
    blockiert bleiben. Kein In-Prozess-Monkeypatch hier -- die Vorbedingung
    lebt ausschliesslich im isolierten Kind, der laufende Testprozess/die
    `unittest`-Discovery bleibt unberuehrt."""
    proc = subprocess.run(
        [sys.executable, "-c", _GUARD_DISCOVERY_NEGATIVE_PROBE_CHILD_SCRIPT],
        capture_output=True, text=True, timeout=20,
    )
    assert proc.returncode == 0, f"Kindprozess-Negativprobe fehlgeschlagen: rc={proc.returncode} stderr={proc.stderr}"
    out_lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    assert out_lines, f"Kindprozess lieferte keine Report-Zeile: stderr={proc.stderr}"
    report = json.loads(out_lines[-1])
    for name, check in report["checks"].items():
        assert check["ok"], f"{name}: {check['detail']}"


# ---------------------------------------------------------------------------
# Fachvertrag 1 -- Figurwahl/`neu`/`fortsetzen:<id>` (_cmd_new_or_switch_character)
# ---------------------------------------------------------------------------

def test_figurwahl_control_token_zero_writes_no_switch_no_new():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B")
        printed: list[str] = []
        session = _sess(d, "p1", ["/abbrechen"], printed)
        session._cmd_new_or_switch_character()
        assert any("Lokal verarbeitet -- keine Figurauswahl" in p for p in printed), printed
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-A"


def test_figurwahl_pause_also_blocks_switch_and_creation():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        printed: list[str] = []
        session = _sess(d, "p1", ["/pause"], printed)
        session._cmd_new_or_switch_character()
        assert any("kein neuer Erschaffungs-/Importvorgang" in p for p in printed), printed
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-A"


def test_figurwahl_number_selection_resolves_correct_entry():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B")
        printed: list[str] = []
        session = _sess(d, "p1", ["2"], printed)
        session._cmd_new_or_switch_character()
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-B", printed
        assert any("'CHR-A' -> 'CHR-B'" in p for p in printed), printed


def test_figurwahl_number_out_of_range_is_rejected_without_switch():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        printed: list[str] = []
        session = _sess(d, "p1", ["9"], printed)
        session._cmd_new_or_switch_character()
        assert any("Keine Figur mit Nummer 9" in p for p in printed), printed
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-A"


def test_figurwahl_unique_display_name_resolves():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", display_name="Lumen", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B", display_name="Skarn")
        printed: list[str] = []
        session = _sess(d, "p1", ["Skarn"], printed)
        session._cmd_new_or_switch_character()
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-B", printed


def test_figurwahl_duplicate_display_name_is_ambiguous_no_guess():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", display_name="Dup", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B", display_name="Dup")
        printed: list[str] = []
        session = _sess(d, "p1", ["Dup"], printed)
        session._cmd_new_or_switch_character()
        assert any("ist nicht eindeutig" in p and "Nummer oder ID" in p for p in printed), printed
        # Keine Rateloesung -- die aktive Figur bleibt unveraendert CHR-A.
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-A"


def test_figurwahl_raw_chrononaut_id_remains_valid_detail_path():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B")
        printed: list[str] = []
        session = _sess(d, "p1", ["CHR-B"], printed)
        session._cmd_new_or_switch_character()
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-B", printed


def test_figurwahl_hilfe_not_treated_as_id_then_real_number_works():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        _register_figure(d / "catalog", "p1", "CHR-B")
        printed: list[str] = []
        session = _sess(d, "p1", ["/hilfe", "2"], printed)
        session._cmd_new_or_switch_character()
        assert any(p.startswith("Hilfe (Figurwahl)") for p in printed), printed
        assert catalog.active_chrononaut_id(d / "catalog", "p1") == "CHR-B", printed


def test_figurwahl_literal_x_and_q_stay_text_not_abort_not_neu():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for literal in ("x", "q"):
            _register_figure(d / "catalog" / literal, literal, "CHR-A", active=True)
            printed: list[str] = []
            session = _sess(d, literal, [literal], printed)
            session.catalog_dir = d / "catalog" / literal
            session._cmd_new_or_switch_character()
            assert any(f"Unbekannte Chrononaut-ID {literal!r}" in p for p in printed), (literal, printed)
            assert catalog.active_chrononaut_id(d / "catalog" / literal, literal) == "CHR-A"


def test_figurwahl_question_mark_inside_sentence_stays_text_no_help():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        printed: list[str] = []
        session = _sess(d, "p1", ["Ist das meine Figur?"], printed)
        session._cmd_new_or_switch_character()
        assert not any(p.startswith("Hilfe (Figurwahl)") for p in printed), printed
        assert any("Unbekannte Chrononaut-ID 'Ist das meine Figur?'" in p for p in printed), printed


def test_figurwahl_empty_stdin_raises_end_of_input_not_loop():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_figure(d / "catalog", "p1", "CHR-A", active=True)
        printed: list[str] = []
        session = _sess(d, "p1", [], printed)
        try:
            session._cmd_new_or_switch_character()
            raised = False
        except EndOfInput:
            raised = True
        assert raised


# ---------------------------------------------------------------------------
# Fachvertrag 2 -- Frischstart-Einladung (_invite_persona_fresh_start)
# ---------------------------------------------------------------------------

def _invite_sess(d: Path, pid: str, lines: list[str], printed: list[str]) -> TuiSession:
    return TuiSession(
        onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id=pid,
        input_fn=_scripted_input(lines), print_fn=printed.append,
        run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        gm_transport_factory=_assert_never_called, persona_driver_factory=_assert_never_called,
    )


def test_frischstart_einladung_control_token_zero_calls():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _invite_sess(d, "inviter1", ["/pause"], printed)
        session._invite_persona_fresh_start()
        assert any("keine Einladung ausgesprochen, kein Modellaufruf" in p for p in printed), printed


def test_frischstart_einladung_empty_input_is_noop_zero_calls():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _invite_sess(d, "inviter1", [""], printed)
        session._invite_persona_fresh_start()  # darf nicht auf _assert_never_called treffen


def test_frischstart_einladung_hilfe_then_empty_shows_help_then_noop():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _invite_sess(d, "inviter1", ["/hilfe", ""], printed)
        session._invite_persona_fresh_start()
        assert any(p.startswith("Hilfe (Frischstart-Einladung)") for p in printed), printed


def test_frischstart_einladung_real_id_without_own_figure_reaches_downstream_check():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _invite_sess(d, "inviter1", ["persona-ohne-figur"], printed)
        session._invite_persona_fresh_start()
        assert any("hat noch keine bestehende Figur" in p for p in printed), printed


def test_frischstart_einladung_empty_stdin_handled_without_loop_or_calls():
    """Diese Funktion faengt `EndOfInput` SELBST (unveraendert von W18, s.
    Aufrufstelle) -- kein Endlosloop, kontrollierte Abbruchmeldung, keine
    Fabrikaufrufe (sonst wuerde `_assert_never_called` sofort fehlschlagen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _invite_sess(d, "inviter1", [], printed)
        session._invite_persona_fresh_start()
        assert any("abgebrochen (EOF)" in p for p in printed), printed


# ---------------------------------------------------------------------------
# Fachvertrag 3 -- beide Importkonflikte in _cmd_import
# ---------------------------------------------------------------------------

def _setup_known_char(catalog_dir: Path, pid: str, char_id: str, level: int) -> dict:
    return _register_figure(catalog_dir, pid, char_id, level=level, active=True)


def test_import_conflict_ak_control_token_zero_write_stand_unchanged():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "ak-abort"
        old_save = _setup_known_char(d / "catalog", pid, "CHR-AK", level=1)
        new_save = _figure_save("CHR-AK", level=5)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "/abbrechen"], printed)
        session._cmd_import()
        assert any("Lokal verarbeitet -- Import bleibt geparkt (kein Write)" in p for p in printed), printed
        assert catalog.load_figure_save(d / "catalog", pid, "CHR-AK") == old_save


def test_import_conflict_ak_hilfe_then_keep_existing():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "ak-help-keep"
        old_save = _setup_known_char(d / "catalog", pid, "CHR-AK", level=1)
        new_save = _figure_save("CHR-AK", level=5)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "?", "k"], printed)
        session._cmd_import()
        assert any(p.startswith("Hilfe (Importkonflikt") for p in printed), printed
        assert catalog.load_figure_save(d / "catalog", pid, "CHR-AK") == old_save


def test_import_conflict_ak_adopt_incoming_writes_new_stand():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "ak-adopt"
        _setup_known_char(d / "catalog", pid, "CHR-AK", level=1)
        new_save = _figure_save("CHR-AK", level=5)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "a"], printed)
        session._cmd_import()
        assert catalog.load_figure_save(d / "catalog", pid, "CHR-AK") == new_save


def test_import_conflict_wb_control_token_zero_register_active_unchanged():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "wb-abort"
        _setup_known_char(d / "catalog", pid, "CHR-OLD-ACTIVE", level=1)
        new_save = _figure_save("CHR-NEW", level=1)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "j", "/pause"], printed)
        session._cmd_import()
        assert any("Lokal verarbeitet -- Import verworfen, char_id=CHR-NEW NICHT" in p for p in printed), printed
        entries = catalog.list_for_participant(d / "catalog", pid)
        assert {e.chrononaut_id for e in entries} == {"CHR-OLD-ACTIVE"}, entries
        assert catalog.active_chrononaut_id(d / "catalog", pid) == "CHR-OLD-ACTIVE"


def test_import_conflict_wb_hilfe_then_explicit_w_switches_active():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "wb-help-w"
        _setup_known_char(d / "catalog", pid, "CHR-OLD-ACTIVE", level=1)
        new_save = _figure_save("CHR-NEW", level=1)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "j", "?", "w"], printed)
        session._cmd_import()
        assert any(p.startswith("Hilfe (Importkonflikt (Aktivwechsel))") for p in printed), printed
        entries = {e.chrononaut_id for e in catalog.list_for_participant(d / "catalog", pid)}
        assert "CHR-NEW" in entries, entries


def test_import_conflict_wb_escaped_literal_slash_stays_text_and_registers_inactive():
    """UX05-Escape-Vertrag: ein ERKLAERT escapeter Literaltext ('\\/abbrechen')
    ist bewusst NORMALER Text, keine Steuerzeile -- im 'b'-Zweig dieser Wahl
    bedeutet das (wie jede andere ungueltige/nicht-'w'-Antwort, unveraendert
    seit vor W18): inaktive Zweitregistrierung, KEIN Abbruch. Unterscheidet
    sich bewusst von der echten, unescapten Steuerzeile oben (Zero-Write)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "wb-escaped"
        _setup_known_char(d / "catalog", pid, "CHR-OLD-ACTIVE", level=1)
        new_save = _figure_save("CHR-NEW", level=1)
        printed: list[str] = []
        session = _sess(d, pid, [json.dumps(new_save), "ENDE", "j", "\\/abbrechen"], printed)
        session._cmd_import()
        entries = {e.chrononaut_id for e in catalog.list_for_participant(d / "catalog", pid)}
        assert "CHR-NEW" in entries, entries
        assert catalog.active_chrononaut_id(d / "catalog", pid) == "CHR-OLD-ACTIVE"


def test_import_mid_paste_line_matching_control_token_text_is_not_global_abort():
    """W11-Matrixbefund Zeile 12 (bewusst UNVERAENDERT): nur die ERSTE Zeile
    einer Mehrzeilen-Paste wird auf exakten Abbruchbefehl geprueft. Eine
    SPAETERE Zeile, die zufaellig exakt wie eine Steuerzeile aussieht, bricht
    den Import NICHT global ab -- der Text wird weiter akkumuliert (hier
    bewusst zu ungueltigem JSON, eine klar ANDERE, spaetere Ablehnung als der
    fruehe Abbruchpfad)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "midpaste"
        lines = [
            '{"v": 7, "characters": [{"char_id": "CHR-MIDPASTE",',
            "/zurueck",
            '"id": "CHR-MIDPASTE", "name": "x", "callsign": "X", "level": 1}]}',
            "ENDE",
        ]
        printed: list[str] = []
        session = _sess(d, pid, lines, printed)
        session._cmd_import()
        assert not any("Import abgebrochen -- kein Text uebernommen, kein Write." in p for p in printed), printed
        assert any("Import abgelehnt (strukturell ungueltig" in p for p in printed), printed


def test_import_first_line_abbrechen_still_aborts_paste_immediately():
    """Gegenprobe zum vorigen Test: AN ERSTER Stelle bleibt '/abbrechen'
    weiterhin der bestehende Sofort-Abbruch (unveraendert von W18)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid = "midpaste-firstline"
        printed: list[str] = []
        session = _sess(d, pid, ["/abbrechen"], printed)
        session._cmd_import()
        assert any("Import abgebrochen -- kein Text uebernommen, kein Write." in p for p in printed), printed
        assert catalog.list_for_participant(d / "catalog", pid) == []


# ---------------------------------------------------------------------------
# Fachvertrag 4 -- Herkunftswahl (_ask_live_starter_origin_choice)
# ---------------------------------------------------------------------------

def test_herkunftswahl_control_token_returns_none_no_calls():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "origin1", ["/abbrechen"], printed)
        result = session._ask_live_starter_origin_choice("Testkontext")
        assert result is None


def test_herkunftswahl_hilfe_then_p_yields_production():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "origin1", ["?", "p"], printed)
        result = session._ask_live_starter_origin_choice("Testkontext")
        assert result == "production"
        assert any(p.startswith("Hilfe (Herkunftsentscheidung)") for p in printed), printed


def test_herkunftswahl_hilfe_then_demo_yields_demo():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "origin1", ["/hilfe", "demo"], printed)
        result = session._ask_live_starter_origin_choice("Testkontext")
        assert result == "demo"


def test_herkunftswahl_empty_stdin_raises_end_of_input_not_caught_here():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "origin1", [], printed)
        try:
            session._ask_live_starter_origin_choice("Testkontext")
            raised = False
        except EndOfInput:
            raised = True
        assert raised


# ---------------------------------------------------------------------------
# Fachvertrag 5 -- KI-Vorlauf-Angebot (_maybe_offer_bounded_preflight)
# ---------------------------------------------------------------------------

def test_ki_vorlauf_angebot_control_token_starts_no_preflight():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "preflight1", ["/zurueck"], printed)
        session.run_dir = d / "run"
        session._cmd_bounded_ai_preflight = _assert_never_called
        session._maybe_offer_bounded_preflight(imported_level=5)
        assert any("Kein KI-Vorlauf gestartet (lokal verarbeitet, keine Aenderung)." in p for p in printed), printed


def test_ki_vorlauf_angebot_default_w_also_starts_no_preflight():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = _sess(d, "preflight2", ["w"], printed)
        session.run_dir = d / "run"
        session._cmd_bounded_ai_preflight = _assert_never_called
        session._maybe_offer_bounded_preflight(imported_level=5)
        assert any("Standard: direkt weiterspielen ohne Levelangleichung" in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    rc = main()
    socket.socket.connect = _REAL_SOCKET_CONNECT  # type: ignore[assignment]
    socket.socket.connect_ex = _REAL_SOCKET_CONNECT_EX  # type: ignore[assignment]
    socket.create_connection = _REAL_CREATE_CONNECTION  # type: ignore[assignment]
    socket.getaddrinfo = _REAL_GETADDRINFO  # type: ignore[assignment]
    for _k, _v in _ORIGINAL_ENV_SNAPSHOT.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v
    _ISOLATED_HOME_DIR.cleanup()
    raise SystemExit(rc)
