#!/usr/bin/env python3
"""
tests/mmo_sim/test_g05_error_redaction_and_guards.py — ZEITRISS Terminal
UX-1 Wiederanlauf 2026-10-05, W4/G05, dauerhafte Regressionen fuer die drei
General-Generalbefunde P06/P07/P08 (reference/review/REVIEW.md §G05,
FINDINGS.json "G05", CASE-REVIEW.json UX07/UX18/UX21).

P06 (UX18): eine fehlerhafte Persona-/SL-Factory (synthetisch wirft) darf
  KEINE rohen Exception-Details/Secrets im Spielertext zeigen -- das
  bestehende `test_ux1_persona_factory_guard.py` prueft nur Abwesenheit des
  woertlichen Strings "Traceback", NICHT Abwesenheit des tatsaechlichen
  Exception-Inhalts. Dieser Test ergaenzt genau die Luecke, die General mit
  `RuntimeError('SYNTHETIC_SECRET_DO_NOT_PRINT')` belegt hat, UND deckt
  zusaetzlich den frueher komplett UNGEWACHTEN `persona_driver_factory`-
  Aufruf in `_invite_persona_fresh_start` ab (stand vorher vor jedem `try`).

P07 (UX21/UX07): ein waehrend einer bereits offenen TUI aktiv werdender
  FREMDER Lab-Lock (lebender anderer Prozess) muss den NEUEN
  Registrierungs-Write ('registrieren') blockieren -- der fruehe
  Skript-Guard (`scripts/mmo_sim.py:_foreign_active_lab_owner`) allein
  schuetzt diesen spaeteren Schreibweg nicht.

P08: `ParticipantRegistry.find_by_display_name` darf bei einem strukturell
  falschen (aber JSON-gueltigen) Registry-Eintrag (`[]`) NICHT mit
  `AttributeError` abstuerzen -- rein lesende Degradierung, kein
  Reparatur-/Ueberschreibwrite.

Isolationsdisziplin (02_TEAM_LAUFPLAN_UND_ROUTENGRENZE.md, Testumgebung):
- Eigenes temporaeres HOME/XDG_* fuer die Dauer dieses Testlaufs (kein
  Rueckfall auf echtes HOME/Secrets), am Ende wiederhergestellt.
- Ein Netzwerk-Guard (echter `socket.socket`-Patch) ist VOR jedem
  Produktimport aktiv und bleibt fuer den gesamten Lauf dieses Prozesses
  bestehen -- zwei bewusst herbeigefuehrte, GEBLOCKTE Negativaufrufe
  (`test_network_guard_blocks_raw_socket_creation`,
  `test_network_guard_blocks_http_client_connection`) belegen, dass der
  Guard tatsaechlich wirkt (dieselbe Belegmethode wie General: "zwei
  absichtlich blockierte Negativaufrufe pro Prozess").
- Alle GM-/Persona-Antworten sind Testdoubles (Fake-GM/kaputte
  Fabrikfunktionen); kein echter Modell-/Providercall ist in diesem Modul
  ueberhaupt erreichbar. Die EINZIGE in diesem Modul gestartete Subprocess
  (`test_registration_write_blocked_by_foreign_lab_lock`) ist ein rein
  lokaler `python -c 'time.sleep(...)'`-Prozess OHNE Netzwerk-/Provider-
  zugriff -- er dient ausschliesslich dazu, eine ECHTE, lebende Fremd-PID
  fuer den Lock-Datei-Test bereitzustellen (dieselbe Testmethode, die
  General fuer P07 selbst verwendet hat: "synthetischer Lablock eines
  tatsaechlich lebenden anderen Prozesses"). Kein Netzwerk-Socket wird dabei
  jemals geoeffnet (der Netzwerk-Guard bleibt fuer den Subprozess irrelevant,
  da der Subprozess ein eigener Interpreter ohne diesen Patch ist, aber
  selbst nichts als `time.sleep` tut).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="g05-isolated-home-")
_ORIGINAL_ENV_SNAPSHOT = {
    k: os.environ.get(k) for k in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME")
}
os.environ["HOME"] = _ISOLATED_HOME_DIR.name
os.environ["XDG_DATA_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-data")
os.environ["XDG_CONFIG_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-config")
os.environ["XDG_CACHE_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-cache")
# Explizite Provider-Env-Allowlist: KEINE MMO_SIM_PERSONA_*/OPENWEBUI_*-Variablen
# duerfen aus der realen Umgebung durchsickern (fail-closed, kein stiller
# Fallback auf eine echte Anbindung).
for _leaky_key in list(os.environ):
    if _leaky_key.startswith("MMO_SIM_PERSONA_") or _leaky_key.startswith("OPENWEBUI_"):
        os.environ.pop(_leaky_key, None)

# --- Netzwerk-Guard: VOR jedem Produktimport aktiv ---
_REAL_SOCKET = socket.socket


class _NetworkBlockedInTest(RuntimeError):
    pass


def _blocked_socket(*_a, **_k):
    raise _NetworkBlockedInTest("Netzwerk-Socket in isoliertem G05-Testlauf blockiert (kein Live-/Providercall).")


socket.socket = _blocked_socket  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.catalog import CatalogEntry, register as catalog_register  # noqa: E402
from mmo_sim.registry.participants import ParticipantRegistry  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_SECRET_MARKER = "SYNTHETIC_SECRET_DO_NOT_PRINT"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _FakeCreationGm:
    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        return {"content": "Wie beginnt deine Zeitreise?"}


def _synthetic_save(char_id: str, name: str) -> dict:
    return full_v7_save(char_id, name=name, save_id=f"fixture-{char_id.lower()}-initial-001")


def _make_ready(onboarding_dir: Path, states_dir: Path, run_dir: Path, participant_id: str) -> None:
    """Dieselbe Produktwegfolge wie in `test_ux1_persona_factory_guard.py:
    _make_ready` -- publiziert eine ECHTE abgeschlossene Figur fuer
    `participant_id`, OHNE den SL-Erschaffungsdialog scripten zu muessen
    (die Erschaffung selbst ist nicht G05-Gegenstand; nur der Zustand
    "Figur bereits vorhanden" wird hier benoetigt, damit der Testlauf bis
    zum eigentlichen Factory-Aufruf vordringt)."""
    save = _synthetic_save(f"CHR-{participant_id.upper()}", participant_id)
    chrono_id = save["characters"][0]["id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, chrono_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)


def _broken_persona_factory(_persona_key: str):
    """Entspricht General-Probe P06: wirft beim AUFRUF selbst (nicht erst
    beim Benutzen des Treibers) mit einem Marker, der in KEINEM Spielertext
    je auftauchen darf."""
    raise RuntimeError(_SECRET_MARKER)


def _broken_gm_transport_factory(*_a, **_k):
    raise RuntimeError(_SECRET_MARKER)


# ---------------------------------------------------------------------------
# Netzwerk-Guard-Beleg (zwei bewusst geblockte Negativaufrufe)
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
# P06 / UX18 — keine rohen Exception-Details/Secrets im Spielertext
# ---------------------------------------------------------------------------

def test_ai_leader_invite_broken_persona_factory_no_secret_leak():
    """Erweitert `test_ux1_persona_factory_guard.py`: nicht nur 'kein
    Traceback', sondern explizit 'kein Secret-Marker aus der Exception'."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        _make_ready(d / "onboarding", d / "states", d / "run", "broken_leader")
        printed: list[str] = []
        gm = _FakeCreationGm()
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "l lead:persona:broken_leader",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=_broken_persona_factory,
        )
        rc = session.run()
        assert rc == 0
        assert not any(_SECRET_MARKER in p for p in printed), printed
        assert not any("RuntimeError" in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed
        assert any("KI-Leader 'broken_leader' nicht moeglich" in p for p in printed), printed


def test_guest_invite_broken_persona_factory_no_secret_leak():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        _make_ready(d / "onboarding", d / "states", d / "run", "p1")
        _make_ready(d / "onboarding", d / "states", d / "run", "broken_guest")
        printed: list[str] = []
        gm = _FakeCreationGm()
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "l persona:broken_guest",
                "/pause",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=_broken_persona_factory,
        )
        rc = session.run()
        assert rc == 0
        assert not any(_SECRET_MARKER in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed
        assert any("Einladung an Persona 'broken_guest' nicht moeglich" in p for p in printed), printed


def test_creation_dialog_broken_gm_transport_factory_no_secret_leak():
    """P06 Leaderweg 'SL-Anbindung' (Erschaffungsdialog): dieselbe
    Factory-Grenze, aber `gm_transport_factory` statt `persona_driver_factory`."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["n"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=_broken_gm_transport_factory,
        )
        session._cmd_new_or_switch_character()
        assert not any(_SECRET_MARKER in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed
        assert any("SL-Anbindung nicht verfuegbar" in p for p in printed), printed


def test_fresh_start_invite_previously_unguarded_factory_call_no_crash_no_secret_leak():
    """Die wichtigste P06-Regression: `driver = self.persona_driver_factory(
    persona_key)` in `_invite_persona_fresh_start` stand VOR diesem Fix vor
    GAR KEINEM `try` -- ein brechender Factory-Aufruf propagierte als echte
    Python-Exception bis zum Aufrufer (`session.run()` haette ohne Fix hier
    gecrasht, da `run()`s Dispatch-Schleife nur `EndOfInput` faengt, s.
    `mmo_sim/ui/tui.py:run`). Dieser Test ruft die Methode direkt (die
    eigentliche Vorbedingung -- bereits bestehende Katalogfigur der Persona
    -- wird minimal, aber ECHT ueber `catalog.register` hergestellt, kein
    Mock des Produktpfads selbst)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        catalog_register(
            d / "catalog",
            CatalogEntry(participant_id="broken_fresh", chrononaut_id="CHR-BROKEN-FRESH", persona_key="broken_fresh"),
        )
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["broken_fresh"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _FakeCreationGm(),
            persona_driver_factory=_broken_persona_factory,
        )
        # Darf NICHT raisen (vorher: ungefangene RuntimeError moeglich).
        session._invite_persona_fresh_start()
        assert not any(_SECRET_MARKER in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed


# ---------------------------------------------------------------------------
# P07 / UX21 / UX07 — Foreign-Owner-Guard vor neuem Registrierungs-Write
# ---------------------------------------------------------------------------

def test_registration_write_blocked_by_foreign_lab_lock():
    """General-Probe P07: ein waehrend einer bereits offenen TUI aktiv
    werdender fremder Lab-Lock (lebender anderer Prozess) blockiert den
    NEUEN Registrierungsweg ('registrieren') -- vorher schrieb dieser Weg
    trotzdem eine Person. Verifiziert zusaetzlich: KEINE Teilnehmerdatei
    wird angelegt (kein Teil-Write vor dem Abbruch)."""
    foreign = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        # Kurze Wartezeit, bis der Kindprozess sicher laeuft (eigene lokale
        # PID, kein Netzwerk-/Providerzugriff -- reiner `time.sleep`).
        deadline = time.monotonic() + 5.0
        while foreign.poll() is not None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert foreign.poll() is None, "Fremdprozess fuer den Lock-Test ist nicht am Leben"

        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir = d / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            # Dasselbe Lockdateiformat wie `mmo_sim/lab/runner.py:_lock_path`
            # (`run_dir / "lab.lock.json"`), gelesen von `active_lock_pid`.
            (run_dir / "lab.lock.json").write_text(
                json.dumps({"pid": foreign.pid}), encoding="utf-8",
            )
            registry_dir = d / "registry"
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
                input_fn=_scripted_input(["Fremdgesperrte Person"]),
                print_fn=printed.append,
                run_dir=run_dir, states_dir=d / "states", schema_path=_SCHEMA_PATH,
            )
            session._cmd_register_new_person()
            assert any("aktiver Lab-Lauf" in p and f"pid={foreign.pid}" in p for p in printed), printed
            assert not any("Neu registriert" in p for p in printed), printed
            # Kein Teil-Write: die Registry wurde gar nicht erst beschrieben.
            written = list(registry_dir.glob("participant__*.json")) if registry_dir.exists() else []
            assert written == [], f"Registrierungswrite trotz fremdem Lock erfolgt: {written}"
    finally:
        foreign.terminate()
        try:
            foreign.wait(timeout=5)
        except subprocess.TimeoutExpired:
            foreign.kill()
            foreign.wait(timeout=5)


def test_registration_write_proceeds_without_foreign_lock_existing_regression_guard():
    """Gegenprobe: OHNE fremden Lock bleibt 'registrieren' unveraendert
    funktionsfaehig (der neue Guard darf den bestehenden gruenen Weg nicht
    beschaedigen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Unbedenkliche Person", "n"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _FakeCreationGm(),
        )
        session._cmd_register_new_person()
        assert any("Neu registriert" in p for p in printed), printed
        registry = ParticipantRegistry(d / "registry")
        assert len(registry.find_by_display_name("Unbedenkliche Person")) == 1


# ---------------------------------------------------------------------------
# P08 — struktureller Namensreader, kein AttributeError
# ---------------------------------------------------------------------------

def test_find_by_display_name_skips_structurally_invalid_entry_no_crash():
    """General-Probe P08: ein Registry-Eintrag mit gueltigem JSON `[]`
    (kein Objekt) darf den rein lesenden Namens-Scan nicht mit
    `AttributeError` abbrechen."""
    with tempfile.TemporaryDirectory() as td:
        registry_dir = Path(td) / "registry"
        registry = ParticipantRegistry(registry_dir)
        registry.register_participant(kind="human", display_name="Valide Person")
        corrupt_path = registry_dir / "participant__zz-corrupt.json"
        corrupt_path.write_text("[]", encoding="utf-8")
        before = corrupt_path.read_bytes()

        # Darf NICHT raisen (vorher: AttributeError auf `list.get`).
        matches = registry.find_by_display_name("Valide Person")
        assert len(matches) == 1
        assert matches[0].display_name == "Valide Person"

        # Der kaputte Eintrag selbst matcht nichts und bleibt unangetastet
        # (kein Auto-Repair/Ueberschreiben).
        no_match = registry.find_by_display_name("irgendwer")
        assert no_match == []
        after = corrupt_path.read_bytes()
        assert before == after, "P08-Reader darf die defekte Datei nicht veraendern (rein lesend)"


def test_find_by_display_name_other_malformed_json_shapes_still_degrade_gracefully():
    """Ergaenzende Regressionsabsicherung (nicht nur `[]`): weitere
    JSON-gueltige, aber nicht-Objekt-Formen (`null`, Zahl, String) duerfen
    ebenfalls nicht crashen."""
    with tempfile.TemporaryDirectory() as td:
        registry_dir = Path(td) / "registry"
        registry_dir.mkdir(parents=True, exist_ok=True)
        for i, payload in enumerate(["null", "42", '"nur ein string"', "[]"]):
            (registry_dir / f"participant__shape{i}.json").write_text(payload, encoding="utf-8")
        registry = ParticipantRegistry(registry_dir)
        matches = registry.find_by_display_name("beliebig")
        assert matches == []


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
