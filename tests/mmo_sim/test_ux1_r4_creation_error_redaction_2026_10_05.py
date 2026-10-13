#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r4_creation_error_redaction_2026_10_05.py -- ZEITRISS
Terminal UX1 R4 Sicherheitsnachzug (01_SICHERHEITSNACHZUG.md, 2026-10-05,
General-Review-Befund M01/R3P01/R3P02): dauerhafte Regression fuer die
engen Fehler-Druckpunkte an den bestehenden Erschaffungsgrenzen.

Vorher: `core/creation_service.py:302` (gm_transport.turn-Ausnahme) und
`:332` (verworfenes/ungueltiges Erschaffungsergebnis) druckten das rohe
`str(exception)` direkt in den Spielertext; `ui/tui.py:1723`/`:1777`
druckten das rohe `outcome.reason` einer fehlgeschlagenen Zusatzfigur-
Erschaffung/-Fortsetzung. Jetzt: beide Core-Druckpunkte zeigen eine feste,
redigierte Textzeile (interne `CreationDialogOutcome.reason=str(e)` bleibt
unveraendert bestehen); beide TUI-Druckpunkte nutzen den neuen kleinen
Formatter `TuiSession._redact_creation_status_text(status)` statt des
rohen `reason`-Felds.

Deckt genau die 5 Mindestregressionen aus 01_SICHERHEITSNACHZUG.md:
  R1 - menschlicher normaler Erschaffungsstart, synthetische GM.turn-
       Ausnahme mit Marker (identische Reproduktionsmethode wie General
       `evidence/probes_r3.py:R3P01`): TUI-Ausgabe markerfrei, genau EIN
       Fake-GM-Aufruf, offener Erschaffungsstand bleibt erhalten.
  R2 - echte `_resume_additional_persona_creation()`-UI-Methode mit
       fehlschlagender Persona-Factory (identisch General `R3P02`):
       markerfreie Ausgabe, kein GM-Turn, keine erneute Einladungs-
       entscheidung (die Resume-Callerfixture wird HIER als vorbereitete
       Fixture offengelegt, nicht als vollstaendige Bedienreise verkauft).
  R3 - unmittelbarer Zusatzfigurweg: echte `_invite_persona_fresh_start()`
       nach einer ECHTEN, ueber den realen Entscheidungsvertrag
       angenommenen Einladung, danach synthetischer GM.turn-Fehler im
       eigentlichen Erschaffungsturn -- derselbe Fehlerausgang ohne rohe
       Reasons, echter Funktions-/Printweg (kein nachgebauter Formatstring).
  R4 - Validierungsfehler nach synthetischem SL-Ergebnis (zwei Figuren in
       einem Block -> `ZeitrissHarvestValidator` lehnt ab): marker-/
       detailfreie Anzeige am realen `core/creation_service.py:332`-
       Druckpunkt, keine unzulaessige Saveuebernahme (Dialog bleibt NICHT
       `completed`). W50 NEW_FLOW_SEQUENCE: seit dem SAVEGATE-Umbau
       (01_AUFTRAG_SAVEGATE.md §C) durchlaeuft dieser Druckpunkt zuerst bis
       zu drei Korrekturversuche (`core.save_correction.pursue_single_
       figure_correction`) -- terminaler Vertrag ist jetzt
       `status="paused"`/`reason="attempt_budget_exhausted"` (derselbe
       generische Terminalcode wie jeder andere SAVEGATE-Korrekturpfad),
       nicht mehr der sofortige `status="error"`/`reason=str(e)` von vor
       R12.
  R5 - Erhaltung: ein bereits `completed`/noch nicht vollstaendig
       publizierter Zusatzfigur-Vorgang wird ueber `_resume_additional_
       persona_creation()` OHNE jeden GM-/Persona-Aufruf fertig publiziert
       (Fabrikfunktionen wuerden bei Aufruf selbst einen Testfehler werfen);
       ein separat admission-blockierter (pausierter) Vorgang bleibt
       weiterhin verstaendlich redigiert, nicht als "0 Calls" umetikettiert.

Isolationsdisziplin (wie `test_g05_error_redaction_and_guards.py`):
eigenes temporaeres HOME/XDG_* fuer die Dauer dieses Testlaufs, Provider-
Env-Allowlist (keine MMO_SIM_PERSONA_*/OPENWEBUI_*-Variablen aus der realen
Umgebung), ein echter Netzwerk-Guard (socket.socket-Patch) VOR jedem
Produktimport, zwei bewusst geblockte Negativaufrufe als Beleg. Alle GM-/
Persona-Antworten sind Testdoubles; kein echter Modell-/Providercall ist in
diesem Modul erreichbar. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import http.client
import json
import os
import socket
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="ux1-r4-isolated-home-")
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
    raise _NetworkBlockedInTest("Netzwerk-Socket in isoliertem R4-Testlauf blockiert (kein Live-/Providercall).")


socket.socket = _blocked_socket  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.creation_service import run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import _additional_onboarding_key  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_MARKER = "SYNTHETIC_SECRET_DO_NOT_PRINT"


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
# R1 - menschlicher normaler Erschaffungsstart, synthetische GM.turn-Ausnahme
# ---------------------------------------------------------------------------

class _MarkerRaisingGm:
    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        raise RuntimeError(_MARKER)


def test_r1_human_creation_start_gm_turn_exception_no_marker_single_call_progress_kept():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        gm = _MarkerRaisingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="reviewer",
            input_fn=_scripted_input([]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert not any(_MARKER in p for p in printed), printed
        assert len(gm.calls) == 1, gm.calls
        state = onboarding.peek(d / "onboarding", "reviewer")
        assert state is not None and state.status == "in_progress", state

        # Interne Diagnose (Requestledger) bleibt erhalten -- nur die
        # OEFFENTLICHE Ausgabe ist redigiert, nicht das interne Fehlerobjekt.
        request_files = list((d / "run" / "requests").glob("*.json"))
        assert request_files, "erwarteter Requestledger-Datensatz fehlt"
        ledger_payloads = [json.loads(p.read_text(encoding="utf-8")) for p in request_files]
        assert any(_MARKER in json.dumps(rec) for rec in ledger_payloads), ledger_payloads


# ---------------------------------------------------------------------------
# R2 - echte _resume_additional_persona_creation()-UI mit brechender Factory
# ---------------------------------------------------------------------------

def _broken_persona_factory(_persona_key: str):
    raise RuntimeError(_MARKER)


def test_r2_resume_additional_persona_creation_broken_factory_no_marker_no_gm_turn():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        persona_key = "medic"
        generation = 2
        # Vorbedingung: Persona hat bereits eine bestehende Figur (sonst
        # kein Zusatzfigur-Fall, s. advance_additional_persona_creation).
        catalog.register(
            d / "catalog",
            catalog.CatalogEntry(participant_id=persona_key, chrononaut_id="CHR-MEDIC-OLD", persona_key=persona_key),
        )
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        ps_store.save_state(persona_key, {
            "v": 2, "persona_key": persona_key, "real_name": "Medic",
            "archetype": "SIMULIERT", "play_style": "SIMULIERT", "charwunsch": "SIMULIERT",
            "plays_char": {"save_file": "x", "character_id": "CHR-MEDIC-OLD", "name": "x", "callsign": "x"},
            "rounds_played": 1,
        }, states_dir=d / "states")

        gm = _MarkerRaisingGm()  # darf NIE `.turn()` sehen (Factory bricht vorher ab)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="flo_human",
            input_fn=_scripted_input([]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=_broken_persona_factory,
        )
        # Echte UI-Methode, vorbereitete erlaubte Resume-Callerfixture (keine
        # vollstaendige Menue-/Consent-Reise -- s. 01 Mindestregression 2).
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": generation}],
        )

        assert not any(_MARKER in p for p in printed), printed
        assert len(gm.calls) == 0, gm.calls
        assert any(f"'{persona_key}'" in p and "Fortsetzen" in p for p in printed), printed


# ---------------------------------------------------------------------------
# R3 - unmittelbarer Zusatzfigurweg nach echter angenommener Einladung
# ---------------------------------------------------------------------------

class _AcceptingPersonaDriver:
    """Nimmt JEDE Einladung an -- liest offer_id/participant_id direkt aus
    dem echten `decision_contract` des Aufrufers (kein hartkodiertes
    Generationsformat, robust gegenueber der internen Zaehllogik)."""

    def __init__(self, persona_key: str):
        self.persona_key = persona_key
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        contract = context["decision_contract"]
        text = json.dumps({
            "offer_id": contract["offer_id"], "participant_id": contract["participant_id"], "decision": "accept",
        })
        return ParticipantDecision(text=text, origin_source="test-fixture:r3", meta={})


def test_r3_immediate_additional_figure_path_after_accepted_invite_no_marker_real_print_path():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        persona_key = "medic"
        # Einladungsvorbedingung: eingeladene Persona hat bereits eine
        # bestehende Figur (sonst kein Zusatzfigur-Fall, s.
        # `_invite_persona_fresh_start`: `entries = catalog.list_for_participant(...)`).
        catalog.register(
            d / "catalog",
            catalog.CatalogEntry(participant_id=persona_key, chrononaut_id="CHR-MEDIC-OLD", persona_key=persona_key),
        )
        # Persona-State muss vorhanden sein, sonst scheitert
        # `advance_additional_persona_creation` bereits VOR jedem GM-Turn am
        # fehlenden Profil (anderer Fehlerzweig als der hier gezielte).
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        ps_store.save_state(persona_key, {
            "v": 2, "persona_key": persona_key, "real_name": "Medic",
            "archetype": "SIMULIERT", "play_style": "SIMULIERT", "charwunsch": "SIMULIERT",
            "plays_char": {"save_file": "x", "character_id": "CHR-MEDIC-OLD", "name": "x", "callsign": "x"},
            "rounds_played": 1,
        }, states_dir=d / "states")
        gm = _MarkerRaisingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="flo_human",
            input_fn=_scripted_input([persona_key]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: _AcceptingPersonaDriver(pk),
        )
        # Echte Methode, echter Printweg (kein nachgebauter Formatstring).
        session._invite_persona_fresh_start()

        assert not any(_MARKER in p for p in printed), printed
        # Die Einladung wurde tatsaechlich angenommen (kein "nicht angenommen"-
        # Ablehnungstext) UND der anschliessende echte Erschaffungsturn
        # scheiterte an genau einem Fake-GM-Aufruf.
        assert not any("nicht angenommen" in p for p in printed), printed
        assert len(gm.calls) == 1, gm.calls
        assert any(
            f"'{persona_key}': Zusatzfigur-Erschaffung error --" in p and "kein automatischer weiterer Versuch" in p
            for p in printed
        ), printed


# ---------------------------------------------------------------------------
# R4 - Validierungsfehler nach synthetischem SL-Ergebnis (realer Druckpunkt
# core/creation_service.py:332)
# ---------------------------------------------------------------------------

class _TwoCharacterBlockGm:
    """Liefert einen strukturell UNGUELTIGEN v7-Block (zwei Figuren statt
    genau einer) -- `ZeitrissHarvestValidator.validate_block` lehnt ab,
    `onboarding.complete_with_save` wirft `ValueError`. Die SL-Antwort
    selbst traegt bewusst KEINEN Marker (das normale `[SL] ...`-Echo der
    Spielantwort ist kein Exception-/Reason-Druckpunkt und nicht
    Gegenstand dieses Nachzugs) -- der Marker steckt ausschliesslich in
    `participant_id` und erreicht die ValueError-Textzeile ueber
    `onboarding.complete_with_save`s `f"...{participant_id!r}..."`."""

    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        block = {
            "v": 7, "save_id": "r4-invalid-two-characters",
            "characters": [
                {"char_id": "CHR-R4-FIRST", "name": "A"},
                {"char_id": "CHR-R4-SECOND", "name": "B"},
            ],
        }
        return {"content": "```json\n" + json.dumps(block) + "\n```"}


def test_r4_validation_error_after_synthetic_sl_result_no_marker_no_improper_save_takeover():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, onboarding_dir = d / "run", d / "onboarding"
        write_test_profile(run_dir)
        # Marker als participant_id -- taucht in `complete_with_save`s
        # ValueError-Text auf (`f"...{participant_id!r}..."`); darf trotzdem
        # NIE im Spielertext erscheinen.
        participant_id = _MARKER
        onboarding.start_or_resume(onboarding_dir, participant_id)
        gm = _TwoCharacterBlockGm()
        printed: list[str] = []

        def _get_reply_must_not_be_called(_turn_idx, _sl_text):
            raise AssertionError("get_reply haette fuer diesen Validierungsfehler nicht erreicht werden duerfen")

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Ich moechte einen neuen Chrononauten erschaffen.",
            gm_transport=gm, get_reply=_get_reply_must_not_be_called,
            harvest_validator=ZeitrissHarvestValidator(), print_fn=printed.append,
            role="creation_dialog",
        )

        assert not any(_MARKER in p for p in printed), printed
        # W50 NEW_FLOW_SEQUENCE (R12-Savegate, 02_TEAM_UND_QUELLRAHMEN.md
        # "Testfixtures versus Schutzassertionen"): `core/creation_service.
        # py`s ValueError-Zweig bei genau diesem Druckpunkt (:332) ruft seit
        # dem SAVEGATE-Umbau (01_AUFTRAG_SAVEGATE.md §C, `core.save_
        # correction.pursue_single_figure_correction`) NICHT mehr sofort
        # `status="error"` -- ein strukturell ungueltiger Entwurf bekommt
        # jetzt bis zu `MAX_ADDITIONAL_REQUESTS` zusaetzliche SL-Versuche
        # UEBER DIESELBE Session, bevor kontrolliert HOLD gemeldet wird.
        # Der synthetische `_TwoCharacterBlockGm` liefert bei jedem Versuch
        # denselben strukturell ungueltigen Zwei-Figuren-Block zurueck --
        # das Budget erschoepft sich also deterministisch, terminaler
        # Zustand ist `status="paused"`/`reason="attempt_budget_exhausted"`
        # (derselbe generische Terminalcode wie in jedem anderen SAVEGATE-
        # Korrekturpfad, s. `core.save_correction.pursue_single_figure_
        # correction`/`pursue_group_save_correction`). Die eigentlichen
        # drei Sicherheitszusagen des Testnamens bleiben ALLE unveraendert
        # bestehen: kein Marker im Spielertext (oben), kein unzulaessiger
        # Statuswechsel auf `error` ohne Begruendung, keine Saveuebernahme
        # (unten) -- nur der konkrete Statuscode wandert von `error` auf den
        # neuen, absichtlich generischen SAVEGATE-Terminalcode.
        assert outcome.status == "paused", outcome
        assert outcome.reason == "attempt_budget_exhausted", outcome.reason
        # Jeder der (1 initial + bis zu 3 Korrektur-)Versuche ging ueber
        # denselben Fake-GM, kein stiller zusaetzlicher/ausgelassener Call.
        assert len(gm.calls) == 4, gm.calls
        # Keine unzulaessige Saveuebernahme: Dialog bleibt NICHT `completed`.
        state = onboarding.peek(onboarding_dir, participant_id)
        assert state is not None and state.status == "in_progress", state
        assert state.final_save is None, state.final_save


# ---------------------------------------------------------------------------
# R5 - Erhaltung: fertig/pending Publikation ohne Zusatz-Call; pausiert bleibt
# verstaendlich
# ---------------------------------------------------------------------------

def test_r5a_already_completed_additional_creation_publishes_without_new_gm_or_persona_call():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, onboarding_dir, catalog_dir, states_dir = d / "run", d / "onboarding", d / "catalog", d / "states"
        write_test_profile(run_dir)
        persona_key, generation = "medic", 2
        # Vorbedingung: Persona hat bereits eine bestehende (aeltere) Figur.
        catalog.register(
            catalog_dir,
            catalog.CatalogEntry(participant_id=persona_key, chrononaut_id="CHR-MEDIC-OLD", persona_key=persona_key),
        )
        # Der Zusatzfigur-Onboarding-Scratch (eigener Schluessel, s.
        # `_additional_onboarding_key`) ist bereits `completed`, aber die
        # Katalogpublikation ist noch NICHT durchgefuehrt (dieselbe
        # Reentry-Luecke, die `_resume_additional_persona_creation`
        # schliesst) -- KEIN neuer GM-/Persona-Aufruf dafuer noetig.
        additional_key = _additional_onboarding_key(persona_key, generation)
        new_save = full_v7_save("CHR-MEDIC-FRESH", name="MedicFresh", save_id="r5-fresh-new-figure")
        onboarding.start_or_resume(onboarding_dir, additional_key)
        onboarding.complete_with_save(
            onboarding_dir, additional_key, new_save, ZeitrissHarvestValidator(), "CHR-MEDIC-FRESH",
        )

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human",
            input_fn=_scripted_input([]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called,
            persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": generation}],
        )

        assert any("abgeschlossen" in p or "tischbereit" in p for p in printed), printed
        assert any("CHR-MEDIC-FRESH" in p for p in printed), printed
        entries = catalog.list_for_participant(catalog_dir, persona_key)
        assert any(e.chrononaut_id == "CHR-MEDIC-FRESH" for e in entries), entries


def test_r5b_blocked_additional_creation_stays_understandable_without_raw_admission_reason():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, onboarding_dir, catalog_dir, states_dir = d / "run", d / "onboarding", d / "catalog", d / "states"
        # BEWUSST kein write_test_profile(run_dir) -- fail-closed Admission-
        # Gate blockiert jeden Request (I2, A1); derselbe Weg wie ein echter
        # Abbruch/pausierter Vorgang muss weiterhin verstaendlich bleiben.
        persona_key, generation = "medic", 3
        catalog.register(
            catalog_dir,
            catalog.CatalogEntry(participant_id=persona_key, chrononaut_id="CHR-MEDIC-OLD", persona_key=persona_key),
        )
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="flo_human",
            input_fn=_scripted_input([]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_assert_never_called,
            persona_driver_factory=_assert_never_called,
        )
        session._resume_additional_persona_creation(
            f"fortsetzen:{persona_key}", [{"persona_key": persona_key, "generation": generation}],
        )

        assert any("Admission-Gate blockiert" in p and "kein Modellaufruf" in p for p in printed), printed
        # Die rohe interne Admission-Begruendung (lab.status.json-Text) darf
        # NICHT im Spielertext auftauchen -- nicht alles als "0 Calls"
        # umetikettieren, aber auch kein Transportdetail durchreichen.
        assert not any("lab.status.json" in p for p in printed), printed


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
