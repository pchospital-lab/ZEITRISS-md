#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r6_ui_truth_2026_10_06.py -- W24c (ZEITRISS Terminal
UX1, R6-Fertigstellung, letzter Baustein): dauerhafte Testdatei fuer die
drei General-Befunde R5P01/R5P02/R5P03, die W24/W24b bereits ausschliesslich
in `mmo_sim/ui/tui.py` behoben haben (keine Produktaenderung durch W24c
selbst). Abgeleitet aus dem reviewer-eigenen, assertionsfreien Beobachtungs-
skript `ledger/W24b/reviewer_probes_r5p0x.py` (druckt nur rohe JSON-Felder,
damit es unveraendert vorher/nachher lauffaehig bleibt) -- HIER werden
dieselben drei Szenarien als echte, dauerhafte `assert`-Tests gegen das
NACHHER-Verhalten festgeschrieben:

  test_r5p01_name_resolves_from_authoritative_save: ein echter, zweiturniger
    Erschaffungsdialog (Fake-SL ausschliesslich an der GM-Transportgrenze,
    `_JourneyCreationGm`) erzeugt einen gueltigen v7-Save mit echtem
    `characters[0].name`. Dieser Name wird an der Figurwahl erneut
    eingegeben und muss ueber `_effective_display_name`/
    `_resolve_character_choice` auf die bereits registrierte Figur
    AUFGELOEST werden (NICHT "Unbekannte Chrononaut-ID"), Dateien bleiben
    durch die reine Auswahl unveraendert, keine zusaetzlichen GM-Calls.

  test_r5p02_community_batch_error_truthful_attempted_no_leak: `_cmd_community`
    mit Demo-/SIMULIERT-Herkunft und einer bei JEDEM Aufruf synchron
    werfenden Fake-GM-Fabrik (8 versuchte Personas im Start-Pool) darf die
    Sammelmeldung NICHT mehr pauschal "kein Modellaufruf" behaupten, obwohl
    bereits 8 echte Aufrufversuche stattfanden -- UND darf dabei keinen
    rohen Marker/Exception-Text/Dict-Repr durchlassen. `persona_calls`
    (die zweite, unabhaengige Fabrik) bleibt bei genau 0, weil dieser
    Fehlpfad bereits beim GM-Fabrikaufruf abbricht, bevor je eine Persona-
    Entscheidung angefragt wird.

  test_r5p03_preflight_profile_help_local_no_exec: `_cmd_bounded_ai_preflight`
    liest `/hilfe` am Profil-Prompt jetzt ueber den zentralen, kontext-
    bewussten Leser (`_readline_with_controls`) -- zeigt Kontexthilfe lokal,
    verbraucht KEINEN Zug, wird NICHT als ungueltiges/fehlendes Profil
    abgelehnt, fragt dieselbe Zeile danach erneut ab (hier zweiter
    Steuerzug `/abbrechen`). Kein zusaetzlicher GM-/Persona-Call durch den
    Hilfe-Pfad selbst, Dateien unveraendert.

Die bereits VERSCHAERFTE Storage-HOLD-Regression (W24b, "Nicht aufgeloester
HOLD" statt der vorher falschen "kein Datenverlust"-Zusage fuer eine bereits
offene Requestreservierung) ist bereits dauerhaft in
`test_ux1_r5_error_surface_redaction_2026_10_06.py::test_c_resume_with_open_
reservation_redacted_no_traceback` abgedeckt -- NICHT hier erneut
geschrieben (s. W-REPORT.md).

Isolationsdisziplin (wie `test_ux1_r5_redaction_hold_pair_2026_10_06.py`/
`reviewer_probes_r5p0x.py`): eigenes temporaeres HOME/XDG_* VOR jedem
Produktimport, Provider-Env-Allowlist, ein Netzwerk-Guard VOR jedem
Produktimport -- bewusst NUR `socket.socket.connect`/`connect_ex`/
`socket.create_connection`/`socket.getaddrinfo` geblockt (NICHT
`socket.socket` selbst ersetzt, das wuerde `ssl` brechen UND unter
`unittest`-Discovery andere, bereits importierte Testmodule stoeren, s.
BRIEF-W17.md §Isolationsregel / W23-Fix). Alle GM-/Persona-Antworten sind
Testdoubles; kein echter Modell-/Providercall ist in diesem Modul
erreichbar. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import os
import socket
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="ux1-r6-w24c-isolated-home-")
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
# ersetzen (bricht sonst `ssl` UND unittest-Discovery-Import anderer
# Testmodule, s. BRIEF-W17.md §Isolationsregel / W23-Fix). ---
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
    raise OSError("Netzwerk in isoliertem W24c-Testlauf blockiert (kein Live-/Providercall).")


socket.socket.connect = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.socket.connect_ex = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.create_connection = _network_blocked  # type: ignore[assignment]
socket.getaddrinfo = _network_blocked  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

from test_ux1_r5_round_journey_new_person_recipients_2026_10_06 import (  # noqa: E402
    _JourneyCreationGm,
)

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_MARKER = "SYNTHETIC_W24C_R5P02_MARKER_DO_NOT_PRINT"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _snapshot(d: Path) -> dict[str, str]:
    import hashlib
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob("*") if p.is_file()}


def _session(d: Path, out: list, read, gm=None, pd=None) -> TuiSession:
    return TuiSession(
        d / "onboarding", d / "catalog", "review_human", input_fn=read, print_fn=out.append,
        run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm, persona_driver_factory=pd,
    )


class _RaisingGm:
    """Konfigurierte, aber bei JEDEM Aufruf SYNCHRON werfende Fake-GM-
    Fabrik -- 0 echten Netzwerk-/Modellzugriff, nur ein lokaler
    Aufrufzaehler (wie `reviewer_probes_r5p0x.py:RaisingGm`)."""

    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise RuntimeError(_MARKER)


class _DummyPersona:
    def __init__(self):
        self.calls = 0

    def decide(self, *a, **kw):
        self.calls += 1
        return ParticipantDecision(text="SYNTHETISCHE ENTSCHEIDUNG", origin_source="review")


# ---------------------------------------------------------------------------
# R5P01 -- echter Erschaffungsweg -> gespeicherter Name wird bei erneuter
# Eingabe an der Figurwahl AUFGELOEST (nicht als unbekannte ID abgelehnt).
# ---------------------------------------------------------------------------

def test_r5p01_name_resolves_from_authoritative_save():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        out: list[str] = []
        gm = _JourneyCreationGm("CHR-W24C-R5P01-NAMED")
        s = _session(d, out, _scripted_input(["leicht"]), lambda *a: gm)
        s._cmd_new_or_switch_character()

        entries = catalog.list_for_participant(d / "catalog", "review_human")
        assert len(entries) == 1, entries
        save = onboarding.peek(d / "onboarding", "review_human").final_save
        name = save["characters"][0]["name"]
        assert isinstance(name, str) and name.strip(), save

        # R5P01-Kernbeleg: der echte gespeicherte Name loest ueber
        # `_effective_display_name` auf denselben Katalogeintrag auf, OBWOHL
        # `CatalogEntry.display_name` selbst leer bleibt (keine Aufrufstelle
        # von `catalog.register` setzt ihn, s. `_effective_display_name`-
        # Docstring in `ui/tui.py`).
        assert entries[0].display_name == "", entries[0]
        assert s._effective_display_name(entries[0]) == name

        before = _snapshot(d)
        out.clear()
        calls_before = gm.calls
        s2 = _session(d, out, _scripted_input([name]), lambda *a: gm)
        s2._cmd_new_or_switch_character()
        after = _snapshot(d)

        # Fremd-/Owner-/Archivschutz erhalten: reine Auswahl veraendert
        # keine Datei, erzeugt keinen zusaetzlichen GM-Aufruf.
        assert before == after, (before, after)
        assert gm.calls == calls_before, gm.calls
        assert not any("Unbekannte Chrononaut-ID" in line for line in out), out
        assert any(entries[0].chrononaut_id in line for line in out), out


# ---------------------------------------------------------------------------
# R5P02 -- Community-Sammelmeldung nach 8 versuchten (fehlgeschlagenen)
# GM-Turns: ehrlich "bereits versuchter Aufruf", kein Leak, 0 Persona-Calls.
# ---------------------------------------------------------------------------

def test_r5p02_community_batch_error_truthful_attempted_no_leak():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        out: list[str] = []
        gm = _RaisingGm()
        pd = _DummyPersona()
        s = _session(d, out, _scripted_input(["d"]), lambda *a: gm, lambda *a: pd)
        s._cmd_community()

        # 8 versuchte (synchron fehlgeschlagene) Fake-GM-Turns -- derselbe
        # Start-Pool wie `test_ux1_r5_error_surface_redaction_2026_10_06.py`.
        assert gm.calls == 8, gm.calls
        # Die zweite, unabhaengige Persona-Fabrik wird fuer DIESEN Fehlpfad
        # nie erreicht (bricht bereits am GM-Fabrikaufruf ab).
        assert pd.calls == 0, pd.calls

        # Kein rohes Dict-/Status-Leak, kein Marker-/Exception-Text.
        assert not any("{'error'" in line for line in out), out
        assert not any(_MARKER in line for line in out), out
        assert not any("RuntimeError" in line or "Traceback" in line for line in out), out

        # Kernbeleg R5P02: NICHT mehr pauschal "kein Modellaufruf" behaupten,
        # obwohl 8 echte Aufrufversuche bereits stattfanden.
        assert not any(
            "Persona-getriebene Erstgeneration" in line and "kein Modellaufruf" in line
            for line in out
        ), out
        # Stattdessen die ehrliche "bereits versuchter Aufruf"-Formulierung.
        assert any(
            "Persona-getriebene Erstgeneration" in line
            and "technischer Fehler an der externen Anbindung NACH einem bereits versuchten Aufruf" in line
            for line in out
        ), out
        assert any("Keine Fehlerdetails in dieser Ansicht" in line for line in out), out


# ---------------------------------------------------------------------------
# R5P03 -- Preflight-Profilprompt: '/hilfe' zeigt Kontexthilfe lokal, wird
# NICHT als ungueltiges Profil abgelehnt, kein zusaetzlicher echter Call.
# ---------------------------------------------------------------------------

def test_r5p03_preflight_profile_help_local_no_exec():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        out: list[str] = []
        # Bootstrap-Roster herstellen: `_cmd_community` schreibt den
        # Community-/Personaroster (`bootstrap_community`) UNABHAENGIG vom
        # Erfolg der anschliessenden GM-gestuetzten Erschaffung -- fuer
        # diesen reinen Preflight-Hilfe-Test genuegt derselbe, bewusst
        # fehlschlagende Fake-GM wie in R5P02 (0 Netzwerk-/Modellzugriff).
        gm = _RaisingGm()
        pd = _DummyPersona()
        s = _session(d, out, _scripted_input(["d"]), lambda *a: gm, lambda *a: pd)
        s._cmd_community()
        calls_before_preflight = gm.calls
        persona_calls_before_preflight = pd.calls

        before = _snapshot(d)
        out.clear()
        s._input = _scripted_input(["/hilfe", "/abbrechen"])
        s._cmd_bounded_ai_preflight()
        after = _snapshot(d)

        # Kein zusaetzlicher echter GM-/Persona-Call durch den Hilfe-Pfad
        # selbst, Dateien durch die reine Hilfe-/Abbruchauskunft unveraendert.
        assert gm.calls == calls_before_preflight, gm.calls
        assert pd.calls == persona_calls_before_preflight, pd.calls
        assert before == after, (before, after)

        # Kernbeleg R5P03: Hilfe wird GEZEIGT, NICHT als ungueltiges/
        # fehlendes Profil abgelehnt.
        assert any(line.startswith("Hilfe (") for line in out), out
        assert not any(
            "ungueltiges/fehlendes Profil" in line and "/hilfe" in line
            for line in out
        ), out
        # Nach der Hilfe wird dieselbe Zeile erneut abgefragt -- der zweite
        # Steuerzug ('/abbrechen') wird real verarbeitet (kein Verbrauch
        # durch '/hilfe' selbst, kein EOF-Absturz).
        assert any("KI-Vorlauf abgebrochen" in line for line in out), out


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
