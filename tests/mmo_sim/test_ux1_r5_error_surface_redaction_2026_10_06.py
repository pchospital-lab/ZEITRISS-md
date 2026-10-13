#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_error_surface_redaction_2026_10_06.py — W22
(ZEITRISS Terminal UX-1, Reserve-Reparatur, F05-Klasse, 2026-10-06):
dauerhafte Regression fuer die zwei in T7 §3b / T8 Journey 4 belegten
„roher Fehler/Status an den Spieler"-Defekte, beide ausschliesslich in
`mmo_sim/ui/tui.py` redigiert (Anzeige-/Boundary-Behandlung, KEINE
Live-/Admission-/Factory-/request_ledger-Semantikaenderung).

Defekt 1 (T7 §3b, `ui/tui.py:_cmd_community`): die Sammelzeile nach
`advance_community_creation` druckte vorher den ROHEN
`dict(sorted(by_status.items()))`-Repr ("{'error': 8}") direkt in die
Spieleransicht. Jetzt eine redigierte, ehrliche Zeile je Lagebild
(`no_driver`/`error`/sonst) — getestet mit einer KONFIGURIERTEN, aber bei
jedem Aufruf synchron werfenden `gm_transport_factory` (Fabrikbau-
Fehlschlag, 0 echte Calls, identisch zur T7-Reproduktion "echte Anbindung
konfiguriert, trotzdem {'error': 8}").

Defekt 2 (T8 Journey 4, `ui/tui.py:_run_table_round`, Aufrufer
`_cmd_local_round`/`_resume_bound_table`/`_cmd_menu_fortsetzen`): der
einzige `app_service.run_play_session(...)`-Aufruf war vorher ungefangen —
ein Storage-Schreibfehler (`OSError`/`PermissionError`) WAEHREND eines
laufenden Rundenturns ODER eine bereits offene Reservierung
(`request_ledger.OpenReservationExistsError`) beim Fortsetzen erreichten
den Spieler als roher Python-Traceback. Jetzt eine redigierte Meldung mit
sicherem Rueckweg-Hinweis statt Traceback — `request_ledger`-Semantik
bleibt UNVERAENDERT (kein Auto-Resolve der offenen Reservierung, s.
W-REPORT.md fuer das offen benannte Residuum).

Isolationsdisziplin (wie `test_ux1_r4_creation_error_redaction_2026_10_05.py`):
eigenes temporaeres HOME/XDG_* fuer die Dauer dieses Testlaufs, Provider-
Env-Allowlist, ein echter Netzwerk-Guard (socket.socket-Patch) VOR jedem
Produktimport. Storage-Fehler (Test b) werden mit echten temporaeren
Dateirechten (`chmod` auf den eigenen `run/requests`-Ordner, danach
zurueckgesetzt) simuliert -- kein echter Modell-/Providercall ist in
diesem Modul erreichbar. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import http.client
import os
import socket
import stat
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="ux1-r5-w22-isolated-home-")
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

# --- Netzwerk-Guard: VOR jedem Produktimport aktiv ---
_REAL_SOCKET = socket.socket


class _NetworkBlockedInTest(RuntimeError):
    pass


def _blocked_socket(*_a, **_k):
    raise _NetworkBlockedInTest("Netzwerk-Socket in isoliertem W22-Testlauf blockiert (kein Live-/Providercall).")


socket.socket = _blocked_socket  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_MARKER = "SYNTHETIC_W22_MARKER_DO_NOT_PRINT"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _give_existing_figure(onboarding_dir, states_dir, run_dir, catalog_dir, participant_id, char_id):
    """Veroeffentlichte, lesbare Current-Autoritaet fuer `participant_id`
    (Vorbedingung von `_cmd_local_round`s `_resolve_member`, das ZUERST
    `onboarding.peek(...).final_save` prueft, s. `ui/tui.py:_resolve_member`)
    -- dieselbe Fixtur-Form wie `test_ux1_r5_redaction_hold_pair_2026_10_06.
    py:_give_existing_figure_with_profile`, zusaetzlich mit einem
    abgeschlossenen Onboarding-Datensatz (dort fuer eine PERSONA-Zusatzfigur
    nicht noetig, `catalog.list_for_participant` reicht dort)."""
    save = full_v7_save(char_id, name=char_id, level=1, save_id=f"fixture-{char_id}")
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": participant_id,
        "archetype": "W22-FIXTURE", "play_style": "W22-FIXTURE", "charwunsch": "W22-FIXTURE",
        "plays_char": {"save_file": "x", "character_id": char_id, "name": "x", "callsign": "x"},
        "rounds_played": 0,
    }, states_dir=states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id))
    catalog.store_figure_save(catalog_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


# ---------------------------------------------------------------------------
# Netzwerk-Guard-Beleg
# ---------------------------------------------------------------------------

def test_network_guard_blocks_raw_socket_creation():
    try:
        socket.socket()
    except _NetworkBlockedInTest:
        pass
    else:
        raise AssertionError("socket.socket() haette im isolierten Testprozess blockiert werden muessen")


def test_network_guard_blocks_http_client_connection():
    conn = http.client.HTTPConnection("127.0.0.1", 1, timeout=1)
    try:
        conn.connect()
    except _NetworkBlockedInTest:
        pass
    else:
        raise AssertionError("http.client-Verbindung haette ueber denselben Socket-Guard blockiert werden muessen")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# (a) Defekt 1 — KI-Community-Erstgeneration-Fehlpfad (T7 §3b)
# ---------------------------------------------------------------------------

class _RaisingFactory:
    """Konfigurierte, aber bei jedem Aufruf SYNCHRON werfende Fabrik --
    identisch zur T7-Reproduktion ('echte SL-/Persona-Anbindung
    konfiguriert', trotzdem schlaegt der tatsaechliche Aufruf technisch
    fehl). Wirft sofort, OHNE jeden Netzwerk-/Modellzugriff (0 echte
    Calls, nur ein lokaler Funktionsaufruf-Zaehler)."""

    def __init__(self):
        self.calls = 0

    def __call__(self, *_a, **_k):
        self.calls += 1
        raise RuntimeError(_MARKER)


def test_a_ki_community_erstgeneration_error_leak_redacted_no_raw_dict_zero_calls():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        gm_factory = _RaisingFactory()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human",
            input_fn=_scripted_input(["d"]),  # Herkunftsentscheidung: SIMULIERT/DEMO uebernehmen
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=gm_factory,
            persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError(
                "persona_driver_factory haette fuer diesen Fehlpfad nicht erreicht werden duerfen "
                "(gm_transport_factory scheitert fuer jede Persona bereits vorher)"
            )),
        )
        session._cmd_community()

        # Kein roher Dict-/Status-Leak ("{'error'" o.ae.) UND kein Marker/
        # Exceptiontext in der Spieleransicht.
        assert not any("{'error'" in p for p in printed), printed
        assert not any("{" in p and "}" in p and "error" in p for p in printed), printed
        assert not any(_MARKER in p for p in printed), printed
        assert not any("RuntimeError" in p or "Traceback" in p for p in printed), printed
        # Redigierte, ehrliche Zeile stattdessen (ueber _opaque_boundary_error).
        assert any(
            "Persona-getriebene Erstgeneration" in p and "technischer Fehler an der externen Anbindung" in p
            for p in printed
        ), printed
        assert any("Keine Fehlerdetails in dieser Ansicht" in p for p in printed), printed
        # 0 echte Calls: die Fabrik wirft synchron ohne Netzwerk/Modellzugriff
        # (Netzwerk-Guard oben belegt zusaetzlich, dass kein echter Socket
        # erreichbar ist) -- sie WURDE aufgerufen (Fabrikbau-Versuch), aber
        # kein einziger Aufruf kam je ueber den lokalen RuntimeError hinaus.
        assert gm_factory.calls == 8, gm_factory.calls


# ---------------------------------------------------------------------------
# (b) Defekt 2 — Storage-Schreibfehler waehrend eines laufenden Rundenturns
#     (T8 Journey 4, erste Haelfte: `chmod 555 run/`)
# ---------------------------------------------------------------------------

class _StubGm:
    def __init__(self):
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        return {"content": f"Szene {idx}: weiter."}


def test_b_round_turn_storage_write_error_redacted_no_traceback():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(onboarding_dir, states_dir, run_dir, catalog_dir, leader_id, "CHR-W22-B")

        # Storage-Schreibfehler simulieren: der Requestledger-Ordner
        # existiert bereits (sonst erzeugt ihn `request_ledger._requests_dir`
        # lazy beim ersten Schreiben) UND wird VORHER auf read-only gesetzt --
        # derselbe beobachtete Effekt wie der reale `chmod 555 run/` aus T8
        # Journey 4, nur gezielt auf den tatsaechlichen Schreibpunkt begrenzt
        # (kein Eingriff in unbeteiligte `run_dir`-Unterordner).
        requests_dir = run_dir / "requests"
        requests_dir.mkdir(parents=True, exist_ok=True)
        original_mode = stat.S_IMODE(requests_dir.stat().st_mode)
        os.chmod(requests_dir, 0o555)
        try:
            gm = _StubGm()
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
                input_fn=_scripted_input(["Erster Zug."]),
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
                gm_transport_factory=lambda: gm,
            )
            session._cmd_local_round()  # Solo-Weg (keine guest_tokens), I1/I3.

            assert not any("Traceback" in p for p in printed), printed
            assert not any("PermissionError" in p for p in printed), printed
            assert not any("OSError" in p for p in printed), printed
            assert any(
                "Speichern/Anbindung gerade nicht moeglich" in p and "kein Datenverlust" in p
                for p in printed
            ), printed
            assert any("Keine Fehlerdetails in dieser Ansicht" in p for p in printed), printed
            # Der GM-Transport selbst wurde fuer diesen Turn NIE erreicht --
            # der Schreibfehler entsteht bereits in `request_ledger.begin()`,
            # VOR jedem Transport-Call (kein stiller teilweiser Versand).
            assert gm.calls == 0, gm.calls
        finally:
            os.chmod(requests_dir, original_mode)


# ---------------------------------------------------------------------------
# (c) Defekt 2 — Resume mit bereits offener Reservierung (T8 Journey 4,
#     zweite Haelfte: `request_ledger.OpenReservationExistsError`)
# ---------------------------------------------------------------------------

def test_c_resume_with_open_reservation_redacted_no_traceback():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(onboarding_dir, states_dir, run_dir, catalog_dir, leader_id, "CHR-W22-C")

        # Phase 1: EIN echter, erfolgreich abgeschlossener Rundenturn (Solo-
        # Weg) -- danach EOF (kein weiterer Zug) -> kontrollierte Pause,
        # Tisch bleibt real gebunden/fortsetzbar (table.sl_log hat 1 Eintrag).
        gm = _StubGm()
        printed_1: list[str] = []
        session_1 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted_input(["Erster Zug."]),
            print_fn=printed_1.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        try:
            session_1._cmd_local_round()
        except EndOfInput:
            # Erwartete kontrollierte Pause-Grenze, sobald das Skript nach
            # dem einen echten Zug erschoepft ist (dieselbe Grenze, die
            # `run()` bei 'l'/'g' faengt, s. `_cmd_local_round`-Docstring) --
            # KEIN Fehlerfall, der Tisch bleibt real gebunden/fortsetzbar.
            pass
        assert gm.calls == 1, (gm.calls, printed_1)

        # Phase 2: EIN bereits offener Requestdatensatz fuer EXAKT die
        # Operationsidentitaet (table_id/section_id/role/turn_idx/participant),
        # die der naechste reale Rundenturn (turn_idx=1) gleich erneut
        # anfragen wird -- derselbe Residualzustand wie nach einem Mid-
        # Write-Crash zwischen Reservierung und Versand/Checkpoint (T8
        # Journey 4). KEIN Aufloesen dieser Reservierung hier -- genau das
        # ist das in W-REPORT.md offen benannte Residuum.
        table_id = f"local-{leader_id}"
        request_ledger.begin(
            run_dir, role="gm_turn", content="INJECTED_OPEN_RESERVATION_FIXTURE",
            reserved_usd=0.0, table_id=table_id, section_id=f"{table_id}-section",
            turn_idx=1, participant=leader_id,
        )

        # Phase 3: neuer Prozess/neue Session (wie nach einem echten
        # Neustart) versucht ECHT fortzusetzen -- derselbe Turn kollidiert
        # mit der oben erzeugten offenen Reservierung.
        printed_2: list[str] = []
        session_2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted_input(["Zweiter Zug (kollidiert)."]),
            print_fn=printed_2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        session_2._cmd_menu_fortsetzen()

        assert not any("Traceback" in p for p in printed_2), printed_2
        assert not any("OpenReservationExistsError" in p for p in printed_2), printed_2
        assert not any("REVIEW-RESERVIERUNGSABSCHLUSS" in p for p in printed_2), printed_2
        # W24b (BRIEF-W24b.md Punkt 1, geaenderter Test): die vorherige
        # pauschale "Speichern/Anbindung gerade nicht moeglich"+"kein
        # Datenverlust"-Zusage war fuer GENAU diesen Fall (bereits offene
        # Requestreservierung) falsch -- ein erneuter Versuch loest die
        # Reservierung NICHT auf, anders als beim reinen Schreibrechtefehler
        # in Test (b) oben (dort bleibt die alte Zusage unveraendert
        # korrekt). Ersetzt durch einen ehrlichen, explizit UNGELOESTEN HOLD
        # ohne falschen Retry-Rat.
        assert any(
            "Nicht aufgeloester HOLD" in p
            and "offene, nicht abgeschlossene Requestreservierung" in p
            for p in printed_2
        ), printed_2
        assert not any(
            "Speichern/Anbindung gerade nicht moeglich" in p and "kein Datenverlust" in p
            for p in printed_2
        ), printed_2
        assert any("Keine Fehlerdetails in dieser Ansicht" in p for p in printed_2), printed_2
        # Kein zweiter echter GM-Turn fuer die kollidierende Anfrage --
        # request_ledger.begin() wirft VOR jedem Transport-Call.
        assert gm.calls == 1, gm.calls


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
    socket.socket = _REAL_SOCKET  # type: ignore[assignment]
    for _k, _v in _ORIGINAL_ENV_SNAPSHOT.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v
    _ISOLATED_HOME_DIR.cleanup()
    raise SystemExit(rc)
