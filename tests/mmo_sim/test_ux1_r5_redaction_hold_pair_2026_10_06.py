#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_redaction_hold_pair_2026_10_06.py -- ZEITRISS
Terminal UX1 R5-Sicherheitsnachzug (01_SICHERHEITSNACHZUG.md Nachtrag,
2026-10-06, Befund "sichtbares IA-1-HOLD erwartet",
test_ia1_p_progressed_archive_protected_on_inactive_resume brach unter R4
auf 16/17): `TuiSession._redact_creation_status_text(status)` bekam bisher
NUR `status` und mappte JEDES `"blocked"` pauschal auf den Admission-Gate-
Text -- auch einen echten IA-1-Archiv-HOLD, dessen sichtbarer Text das Wort
"Archiv" tragen MUSS. Jetzt: der Formatter bekommt zusaetzlich `reason` und
klassifiziert `status == "blocked"` NUR gegen mehrwortige, eindeutige
Ankerphrasen, die exakt den intern-authored Gruenden in
`domain/zeitriss/community_creation.py` entsprechen (nur dort gelesen, nie
geaendert) -- ein blosses Teilwort ("Archiv"/"blocked"/"Admission") reicht
NICHT. `status == "error"` wird NIE gegen diese Ankerphrasen geprueft (auch
ein mit "Archiv" praeparierter `reason`-Text bleibt neutral redigiert).

Deckt die Pflicht-Gegenproben (BRIEF-W17.md):
  T1 - echter IA-1-Archiv-HOLD am echten Persona-Resume-Druckpunkt
       (`_resume_additional_persona_creation` -> `_publication_reconcile_
       additional`): sichtbarer Text enthaelt "Archiv", kein roher `reason`-
       Durchlass, State (Archiv/Current) unveraendert, keine Modell-/
       Einladungscalls, Generation bleibt unresolved.
  T2 - echte Admission-Blockade (fail-closed, kein `write_test_profile`):
       Admission-Gate-Text, NICHT "Archiv".
  T3 - Fehler VOR jedem Factory-/Transportturn (fehlendes Persona-Profil):
       neutral redigiert, Null Fabrikaufrufe.
  T4 - Fehler NACH einem echten Fake-GM-Aufruf (echter Frischstart-
       Einladungspfad, `_invite_persona_fresh_start`): neutral redigiert,
       kein Markerleck, genau EIN GM-Aufruf.
  T5 - Validierungsfehler (ungueltiger SL-Block, Zwei-Figuren-Block) am
       selben echten Einladungspfad: neutral redigiert, kein Detaildurchlass,
       Dialog bleibt NICHT completed. W50 NEW_FLOW_SEQUENCE: terminiert seit
       dem SAVEGATE-Umbau (01_AUFTRAG_SAVEGATE.md §C) ueber bis zu drei
       Korrekturversuche mit `status="paused"`, nicht mehr sofort mit
       `status="error"` (s. `test_ux1_r4_...py` fuer dieselbe Anpassung am
       Schwesterdruckpunkt).
  T6 - erfolgreiche idempotente Rest-/Pending-Publikation (bereits
       `completed`-Onboarding-Scratch, Katalogpersistenz nur nachgeholt):
       MUSS wirklich fertigstellen (status completed), NICHT mit HOLD
       blockiert, ohne jeden neuen GM-/Persona-Aufruf.
  T7 - Formatter-Direktproben: ein synthetischer `error`-Grund, kuenstlich
       mit "Archiv" UND "blocked" praepariert, bleibt neutral (keine
       Fehlklassifikation, kein Leak); ein unbekannter `blocked`-Grund, der
       "Archiv" nur als zufaelliges Teilwort enthaelt (keine der exakten
       Ankerphrasen), faellt auf den unveraenderten Admission-Default-Text
       zurueck (kein naives Teilwort-Matching).

Isolationsdisziplin (wie `test_ux1_r4_creation_error_redaction_2026_10_05.py`):
eigenes temporaeres HOME/XDG_* VOR jedem Produktimport, Provider-Env-
Allowlist, ein Netzwerk-Guard VOR jedem Produktimport -- bewusst NUR
`socket.socket.connect`/`connect_ex`/`socket.create_connection`/
`socket.getaddrinfo` geblockt (NICHT `socket.socket` selbst ersetzt, das
wuerde `ssl` brechen, s. BRIEF-W17.md §Isolationsregel). Alle GM-/Persona-
Antworten sind Testdoubles; kein echter Modell-/Providercall ist in diesem
Modul erreichbar. Pure Python, nur `assert`, echter Exitcode."""
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
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="ux1-r5-isolated-home-")
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
    raise OSError("Netzwerk in isoliertem R5-Testlauf blockiert (kein Live-/Providercall).")


socket.socket.connect = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.socket.connect_ex = lambda *a, **k: _network_blocked()  # type: ignore[assignment]
socket.create_connection = _network_blocked  # type: ignore[assignment]
socket.getaddrinfo = _network_blocked  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    _additional_creation_pending_key,
    _additional_onboarding_key,
)
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_MARKER = "SYNTHETIC_R5_MARKER_DO_NOT_PRINT"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _assert_never_called(*_a, **_k):
    raise AssertionError("diese Fabrikfunktion haette fuer diesen Vorgang NICHT aufgerufen werden duerfen")


def _give_existing_figure_with_profile(states_dir, run_dir, catalog_dir, persona_key, char_id):
    """Persona hat bereits eine bestehende, AKTIVE Figur -- Vorbedingung
    jedes Zusatzfigur-Pfads (`catalog.list_for_participant` darf nicht leer
    sein). Legt Katalogeintrag+Figursave+Persona-State+Current an (fuer
    Szenarien, die echte Factory-/GM-Turns oder eine gueltige Current-
    Autoritaet brauchen)."""
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    ps_store.save_state(persona_key, {
        "v": 2, "persona_key": persona_key, "real_name": persona_key,
        "archetype": "R5-FIXTURE", "play_style": "R5-FIXTURE", "charwunsch": "R5-FIXTURE",
        "plays_char": {"save_file": "x", "character_id": char_id, "name": "x", "callsign": "x"},
        "rounds_played": 1,
    }, states_dir=states_dir)
    save = full_v7_save(char_id, name=char_id, level=1, save_id=f"fixture-{char_id}")
    catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=persona_key, chrononaut_id=char_id, persona_key=persona_key))
    catalog.store_figure_save(catalog_dir, persona_key, char_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    catalog.bind_for_section(catalog_dir, persona_key, char_id, has_open_section=False)
    return save


def _give_existing_figure_without_profile(catalog_dir, persona_key, char_id):
    """Persona hat bereits einen Katalogeintrag (Vorbedingung des Zusatz-
    figur-Pfads erfuellt), aber BEWUSST KEIN Persona-State und KEIN Current
    -- fuer T3 (Fehler VOR jedem Factory-/Transportturn: fehlendes Persona-
    Profil)."""
    save = full_v7_save(char_id, name=char_id, level=1, save_id=f"fixture-{char_id}")
    catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=persona_key, chrononaut_id=char_id, persona_key=persona_key))
    catalog.store_figure_save(catalog_dir, persona_key, char_id, save)


def _sess(run_dir, states_dir, catalog_dir, onboarding_dir, persona_key, gm_factory=None, persona_factory=None):
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=persona_key,
        input_fn=_scripted_input([]), print_fn=None,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
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


def _prior_module_replacement(*_a, **_k):
    raise RuntimeError("anderes Modul hat socket.socket bereits ersetzt")


socket.socket = _prior_module_replacement

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
# T1 - echter IA-1-Archiv-HOLD am echten Persona-Resume-Druckpunkt
# ---------------------------------------------------------------------------

def test_t1_persona_archive_hold_real_resume_path_shows_archiv_no_raw_reason_unresolved():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        write_test_profile(run_dir)
        persona_key = "medic_t1"
        old_id, new_id = "medic-t1-old", "medic-t1-new"
        _give_existing_figure_with_profile(states_dir, run_dir, catalog_dir, persona_key, old_id)

        pending_key = _additional_creation_pending_key(persona_key)
        generation = onboarding.bind_attempt(onboarding_dir, pending_key, seed_generation=2)

        # Zusatzfigur `new_id` ist bereits registriert+archiviert (aelterer
        # Stand) UND ihr Auftragsclaim ist bereits an GENAU diese
        # (key, generation, char_id) gebunden -- derselbe Vertrag wie ein
        # bereits einmal erfolgreich durchgelaufener Register-/Figursave-
        # Schritt, NUR die abschliessende Current-Aktivierung/zweite
        # Reentry steht noch aus.
        onboarding.record_attempt_claim(onboarding_dir, pending_key, generation=generation, char_id=new_id)
        archived_progressed = {
            "v": 7, "save_id": f"fixture-{new_id}-progressed", "characters": [
                {"char_id": new_id, "id": new_id, "name": new_id, "callsign": new_id.upper(), "level": 4},
            ],
        }
        catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=persona_key, chrononaut_id=new_id, persona_key=persona_key))
        catalog.store_figure_save(catalog_dir, persona_key, new_id, archived_progressed)

        # Der abgeschlossene Onboarding-Scratch dieser Generation liefert
        # einen VON `archived_progressed` ABWEICHENDEN `final_save` (derselbe
        # char_id, aelterer Level-1-Inhalt) -- genau der IA-1-Konflikt.
        additional_key = _additional_onboarding_key(persona_key, generation)
        stale_final_save = full_v7_save(new_id, name=new_id, level=1, save_id=f"fixture-{new_id}-stale")
        onboarding.start_or_resume(onboarding_dir, additional_key)
        onboarding.complete_with_save(
            onboarding_dir, additional_key, stale_final_save,
            ZeitrissHarvestValidator(),
            new_id,
        )

        before_archive = catalog.load_figure_save(catalog_dir, persona_key, new_id)
        before_current = core_store.load_current_save_or_raise(
            run_dir, persona_key, PersonaStateStore(schema_path=_SCHEMA_PATH), states_dir,
        )
        pending_before = json.loads((onboarding_dir / f"attempt__{pending_key}.json").read_text())
        assert pending_before["resolved"] is False

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t1",
            input_fn=_scripted_input([]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called, persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": generation}],
        )

        assert any("blocked" in p and "Archiv" in p for p in printed), printed
        # Kein roher reason-Durchlass: die internen Ankerphrasen/Reasonbau-
        # steine duerfen NICHT woertlich im Spielertext auftauchen.
        assert not any("kontrollierter Konflikt" in p for p in printed), printed
        assert not any("kein zweiter Modellaufruf" in p for p in printed), printed
        assert not any(_MARKER in p for p in printed), printed

        after_archive = catalog.load_figure_save(catalog_dir, persona_key, new_id)
        after_current = core_store.load_current_save_or_raise(
            run_dir, persona_key, PersonaStateStore(schema_path=_SCHEMA_PATH), states_dir,
        )
        assert after_archive == before_archive == archived_progressed, "Archiv darf durch den HOLD nicht veraendert werden"
        assert after_current == before_current, "Current darf durch den HOLD nicht veraendert werden"
        assert after_current["characters"][0]["id"] == old_id, "cid bleibt INAKTIV"

        pending_after = json.loads((onboarding_dir / f"attempt__{pending_key}.json").read_text())
        assert pending_after["resolved"] is False, "HOLD darf die Generation NICHT als erledigt markieren"


# ---------------------------------------------------------------------------
# T2 - echte Admission-Blockade: Admission-Text, NICHT Archiv
# ---------------------------------------------------------------------------

def test_t2_persona_admission_block_real_resume_path_shows_admission_text_not_archiv():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        # BEWUSST kein write_test_profile(run_dir) -- fail-closed Admission-
        # Gate blockiert jeden Request (I2, A1).
        persona_key = "medic_t2"
        catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=persona_key, chrononaut_id="medic-t2-old", persona_key=persona_key))

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t2",
            input_fn=_scripted_input([]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called, persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": 2}],
        )

        assert any("Admission-Gate blockiert" in p and "kein Modellaufruf" in p for p in printed), printed
        assert not any("Archiv" in p for p in printed), printed
        assert not any("lab.status.json" in p for p in printed), printed


# ---------------------------------------------------------------------------
# T3 - Fehler VOR jedem Factory-/Transportturn (fehlendes Persona-Profil)
# ---------------------------------------------------------------------------

def test_t3_persona_error_before_any_factory_call_missing_profile_neutral():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        write_test_profile(run_dir)
        persona_key = "medic_t3"
        _give_existing_figure_without_profile(catalog_dir, persona_key, "medic-t3-old")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t3",
            input_fn=_scripted_input([]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called, persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": 2}],
        )

        assert any(
            f"'{persona_key}': Fortsetzen error --" in p and "kein automatischer weiterer Versuch" in p
            for p in printed
        ), printed
        assert not any("kein Persona-Profil" in p for p in printed), printed
        assert not any("Archiv" in p for p in printed), printed


# ---------------------------------------------------------------------------
# T4 - Fehler NACH einem echten Fake-GM-Aufruf (echter Einladungspfad)
# ---------------------------------------------------------------------------

class _MarkerRaisingGm:
    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        raise RuntimeError(_MARKER)


class _AcceptingPersonaDriver:
    def __init__(self, persona_key: str):
        self.persona_key = persona_key
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        contract = context["decision_contract"]
        text = json.dumps({
            "offer_id": contract["offer_id"], "participant_id": contract["participant_id"], "decision": "accept",
        })
        return ParticipantDecision(text=text, origin_source="test-fixture:t4", meta={})


def test_t4_persona_error_after_fake_gm_call_real_invite_path_neutral_no_marker():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        write_test_profile(run_dir)
        persona_key = "medic_t4"
        _give_existing_figure_with_profile(states_dir, run_dir, catalog_dir, persona_key, "medic-t4-old")

        gm = _MarkerRaisingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t4",
            input_fn=_scripted_input([persona_key]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda *a, **k: gm,
            persona_driver_factory=lambda pk: _AcceptingPersonaDriver(pk),
        )
        session._invite_persona_fresh_start()

        assert not any(_MARKER in p for p in printed), printed
        assert not any("nicht angenommen" in p for p in printed), printed
        assert len(gm.calls) == 1, gm.calls
        assert any(
            f"'{persona_key}': Zusatzfigur-Erschaffung error --" in p and "kein automatischer weiterer Versuch" in p
            for p in printed
        ), printed
        assert not any("Archiv" in p for p in printed), printed


# ---------------------------------------------------------------------------
# T5 - Validierungsfehler (ungueltiger SL-Block) am selben Einladungspfad
# ---------------------------------------------------------------------------

class _TwoCharacterBlockGm:
    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        block = {
            "v": 7, "save_id": "t5-invalid-two-characters",
            "characters": [
                {"char_id": "CHR-T5-FIRST", "name": "A"},
                {"char_id": "CHR-T5-SECOND", "name": "B"},
            ],
        }
        return {"content": "```json\n" + json.dumps(block) + "\n```"}


def test_t5_persona_validation_error_invalid_block_real_invite_path_neutral():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        write_test_profile(run_dir)
        persona_key = "medic_t5"
        _give_existing_figure_with_profile(states_dir, run_dir, catalog_dir, persona_key, "medic-t5-old")

        gm = _TwoCharacterBlockGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t5",
            input_fn=_scripted_input([persona_key]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda *a, **k: gm,
            persona_driver_factory=lambda pk: _AcceptingPersonaDriver(pk),
        )
        session._invite_persona_fresh_start()

        # W50 NEW_FLOW_SEQUENCE (R12-Savegate, 02_TEAM_UND_QUELLRAHMEN.md
        # "Testfixtures versus Schutzassertionen"); TEST-DELTA weiter
        # ueberschrieben durch N2R5-BESTEFFORT (Flo-Design, ZR-N2R-
        # ANSCHLUSS-20261020-FINALRUN3): derselbe Druckpunkt wie
        # `test_ux1_r4_...:test_r4_...` -- seit dem SAVEGATE-Umbau
        # (01_AUFTRAG_SAVEGATE.md §C) durchlaeuft ein strukturell
        # ungueltiger Entwurf zuerst bis zu drei zusaetzliche SL-Versuche
        # (`core.save_correction.pursue_single_figure_correction`), das
        # Budget erschoepft sich deterministisch (1 initial + 3 Korrektur-
        # versuche). N2R5-BESTEFFORT: ein erschoepftes Budget (reiner
        # Schema-Imperfekt, KEINE Drift) ist KEIN `status="paused"` mehr --
        # `core.creation_service.run_admitted_creation_dialog` finalisiert
        # die Zusatzfigur jetzt best-effort und druckt dabei EHRLICH die
        # neue, redaktionssichere Hinweiszeile (statt des alten TUI-
        # Formatter-Druckpunkts fuer `status="paused"`, der fuer diesen
        # Grund nicht mehr erreicht wird).
        assert len(gm.calls) == 4, gm.calls
        best_effort_notice = (
            "SL-Korrekturbudget erschoepft -- Figur wird mit dem letzten (ggf. nicht ganz "
            "korrekten) SL-Entwurf best-effort abgeschlossen; der GM gleicht das beim "
            "naechsten Laden automatisch ab."
        )
        assert best_effort_notice in printed, printed
        # Dieselbe Redaktionsdisziplin wie zuvor fuer den Formatter-
        # Druckpunkt gilt jetzt fuer die Best-Effort-Hinweiszeile selbst:
        # keine rohen char_id-/Validator-Details.
        assert "CHR-T5-FIRST" not in best_effort_notice and "CHR-T5-SECOND" not in best_effort_notice
        assert "Save-Block" not in best_effort_notice
        assert "Archiv" not in best_effort_notice
        # Saveuebernahme erfolgt jetzt (N2R5-BESTEFFORT), aber NUR EHRLICH
        # als best-effort/imperfekt markiert -- der Zusatzfigur-Onboarding-
        # Scratch wird `completed`, nicht stillschweigend als perfekt
        # behauptet.
        generation = 2  # erste Zusatzfigur-Generation (len(entries)+1, eine bestehende Figur)
        additional_key = _additional_onboarding_key(persona_key, generation)
        state = onboarding.peek(onboarding_dir, additional_key)
        assert state is not None and state.status == "completed", state
        assert state.final_save_best_effort is True, state


# ---------------------------------------------------------------------------
# T6 - erfolgreiche idempotente Rest-/Pending-Publikation: MUSS fertigstellen
# ---------------------------------------------------------------------------

def test_t6_persona_pending_publication_really_completes_not_held():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, catalog_dir, onboarding_dir = d / "run", d / "states", d / "catalog", d / "onboarding"
        write_test_profile(run_dir)
        persona_key = "medic_t6"
        _give_existing_figure_with_profile(states_dir, run_dir, catalog_dir, persona_key, "medic-t6-old")
        generation = 2
        additional_key = _additional_onboarding_key(persona_key, generation)
        new_save = full_v7_save("medic-t6-new", name="MedicT6New", save_id="t6-fresh-new-figure")
        onboarding.start_or_resume(onboarding_dir, additional_key)
        onboarding.complete_with_save(
            onboarding_dir, additional_key, new_save,
            ZeitrissHarvestValidator(),
            "medic-t6-new",
        )

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human_t6",
            input_fn=_scripted_input([]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called, persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": generation}],
        )

        assert not any("blocked" in p for p in printed), printed
        assert any("abgeschlossen" in p or "tischbereit" in p for p in printed), printed
        assert any("medic-t6-new" in p for p in printed), printed
        entries = catalog.list_for_participant(catalog_dir, persona_key)
        assert any(e.chrononaut_id == "medic-t6-new" for e in entries), entries


# ---------------------------------------------------------------------------
# T7 - Formatter-Direktproben: kein naives Teilwort, keine Fehlklassifikation
# ---------------------------------------------------------------------------

def test_t7_formatter_error_status_with_crafted_archiv_and_blocked_words_stays_neutral():
    session = TuiSession(
        onboarding_dir=Path("/nonexistent"), catalog_dir=Path("/nonexistent"), participant_id="x",
        input_fn=_scripted_input([]), print_fn=lambda s: None,
        run_dir=None, states_dir=None, schema_path=_SCHEMA_PATH,
    )
    crafted = (
        "Fake-Exception: Figuren-Archiv korrupt, status war zuvor blocked, "
        "Admission-Gate meldet ebenfalls einen Fehler."
    )
    text = session._redact_creation_status_text("error", crafted)
    assert "Archiv" not in text, text
    assert "blocked" not in text, text
    assert "kein automatischer weiterer Versuch" in text, text


def test_t7_formatter_unknown_blocked_reason_with_archiv_substring_falls_back_to_admission_default():
    session = TuiSession(
        onboarding_dir=Path("/nonexistent"), catalog_dir=Path("/nonexistent"), participant_id="x",
        input_fn=_scripted_input([]), print_fn=lambda s: None,
        run_dir=None, states_dir=None, schema_path=_SCHEMA_PATH,
    )
    crafted = (
        "lab.status.json ohne erkennbares Autorisierungsprofil -- irgendwo in diesem Satz "
        "steht zufaellig das Wort Archiv, ist aber keine der bekannten Ankerphrasen."
    )
    text = session._redact_creation_status_text("blocked", crafted)
    assert text == (
        "Admission-Gate blockiert -- kein Modellaufruf, Fortschritt bleibt erhalten, spaeter fortsetzbar."
    ), text
    assert "Archiv" not in text, text


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
