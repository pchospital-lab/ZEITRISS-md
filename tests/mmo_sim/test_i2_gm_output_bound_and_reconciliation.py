#!/usr/bin/env python3
"""
tests/mmo_sim/test_i2_gm_output_bound_and_reconciliation.py — I2-Nachzug
GM-Weg (MAIN-ENTSCHEIDUNG.md/PLAN-CRITIC.md, 2026-09-23), E1-E5.

END-CRITIC-VORFALL-ORIGINALDERIVAT.md Befund A: der GM-Transportpfad behandelte
eine NICHT vorhandene Ausgabegrenze als bekannt (`output_bound_known=True`
Default) und verrechnete reale gemeldete Usage nie mit der Vor-Versand-
Reservierung. Diese Datei belegt beide Fixe (E1-E4: Grenze/Route duck-typed
vom GM-Transport lesen; E5: Delta-Reconciliation in `finish_received`) an
ECHTEN Produktaufrufern (`GmOwuiTransport` -> `SLSession` -> `OWUIChat`,
NUR die aeusserste HTTP-Grenze ist `FakeHTTPServer`) UND an der reinen
Ledger-Logik (Reconciliation-Matrix).

Providerfreies Testprofil (`write_test_profile`), synthetische Testtarife
(Default `_synthetic_prices()`), Loopback-Route. Kein echter Modellcall.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.adapters.fakes import FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402
from mmo_sim.core import app_service, request_ledger, store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)

_SL_CLIENT_PATH = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"
_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)
_SYNTH_ENV = {
    "MMO_SIM_SYNTHETIC_USD_PER_1K_PROMPT": "0.003",
    "MMO_SIM_SYNTHETIC_USD_PER_1K_COMPLETION": "0.015",
}


class _FixedDriver:
    """Kein `.config`-Attribut (wie ein Human-Driver ohne Netzwerkroute) --
    die Persona-Entscheidung selbst ist NICHT Gegenstand dieser Datei (Befund
    A betrifft ausschliesslich den GM-Pfad); dieser Fake liefert nur eine
    kurze, deterministische Leader-Entscheidung, damit der eigentliche
    GM-Turn (echter Produktaufrufer) erreicht wird."""

    def __init__(self, texts):
        self._texts = list(texts)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        text = self._texts.pop(0) if self._texts else "Ich warte ab."
        return ParticipantDecision(text=text, origin_source="fake:i2-gm-output-bound")


def _bootstrap_solo_run(root: Path) -> tuple[Path, Path, PersonaStateStore, store.Lobby, store.Table]:
    """Solo-Tisch (ein Mitglied, `solo_pk`) -- genug fuer einen echten
    Leader-Anker-GM-Turn ueber `app_service.run_play_session`."""
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    states_dir = root / "states"
    states_dir.mkdir()
    run_dir = root / "run"
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    ps_store.save_state("solo_pk", {
        "v": 2, "persona_key": "solo_pk", "rounds_played": 0,
        "plays_char": {"character_id": "chrono-gm-output"},
    }, states_dir=states_dir)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("solo_pk")
    table, _ = store.create_table_from_offer_log(
        lobby, "t-gm-output", [{"type": "offer", "id": "o1", "from": "solo_pk", "wants": []}],
        {"solo_pk": "chrono-gm-output"},
    )
    assert table is not None
    return run_dir, states_dir, ps_store, lobby, table


def _run_one_leader_turn(run_dir, states_dir, ps_store, lobby, table, gm_transport, driver_texts, max_turns=1):
    driver = _FixedDriver(driver_texts)
    controller = TableController("solo_pk", {"solo_pk": driver})
    contexts = {"solo_pk": {"system": "own", "user": "Ich beginne.", "import_save_payload": {"v": 7}}}
    return app_service.run_play_session(
        lobby, table, gm_transport, controller, "gm-output-section", contexts,
        states_dir, "2026-09-23", "2026-09-23T00:00:00", COMPLETION_MARKER,
        ZeitrissHarvestValidator(), ps_store, zeitriss_saves.harvest_from_debrief,
        max_turns=max_turns,
    )


# ---------------------------------------------------------------- GM-Pfad: E1-E4 (Grenze/Route real durchgereicht)
def test_gm_missing_output_bound_rejected_under_hard_max_usd_with_small_input():
    """Befund A (Kernfix): ein GM-Transport OHNE erkennbare Ausgabegrenze
    (`gm_output_limit_tokens` nicht konfiguriert, P1-Standard) wird unter
    einem harten `max_usd` VOR Versand abgelehnt -- NICHT stillschweigend
    mit der 0,015-Pauschale durchgewinkt. Bewusst ein KLEINER Input (anders
    als `review_p2q_request_contract.py` Test 06, das die grosse INPUT-Seite
    prueft) -- diese Ablehnung muss unabhaengig von der Eingabegroesse rein
    aus der fehlenden Ausgabegrenze folgen."""
    with tempfile.TemporaryDirectory() as td, FakeHTTPServer([
        (200, {"choices": [{"message": {"content": "Kurze Antwort"}}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}),
    ]) as srv:
        root = Path(td)
        run_dir, states_dir, ps_store, lobby, table = _bootstrap_solo_run(root)
        write_test_profile(run_dir, max_turns=10, max_usd=0.01)
        env = {"OPENWEBUI_URL": srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC", **_SYNTH_ENV}
        with patch.dict(os.environ, env):
            gm = GmOwuiTransport(_SL_CLIENT_PATH, run_dir, table_id="t-gm-output", sl_model="synthetic-model", kb_id="synthetic-kb")
        assert gm.output_limit_tokens is None, "Vorbedingung: keine konfigurierte Ausgabegrenze"
        outcome = _run_one_leader_turn(run_dir, states_dir, ps_store, lobby, table, gm, ["Kurze Aktion."])
        assert len(srv.calls) == 0, (
            f"GM-Aufruf ohne durchsetzbare Ausgabegrenze darf unter hartem max_usd NIE real "
            f"gesendet werden (Befund A) -- calls={srv.calls}"
        )
        assert not outcome.completion.success
        assert "Admission-Gate" in outcome.completion.reason, outcome.completion.reason


def test_gm_configured_output_limit_positive_path_sends_max_tokens_then_reconciled_overrun_blocks_next_turn():
    """Pflicht-Positivpfad (01_AUFTRAG_I2.md §4/MAIN-ENTSCHEIDUNG 'GM-
    Positivpfad'): EIN GM-Transport MIT konfigurierter `gm_output_limit_tokens`
    (E1) macht `output_bound_known=True` (E2) -- die Anfrage passiert das
    Gate trotz hartem `max_usd`, GENAU wie der bereits funktionierende
    Persona-Q07-Pfad, UND das konfigurierte Limit erscheint real im HTTP-Body
    als `max_tokens` (E4, Beweis der vollen Kette bis zum echten Adapter).

    Zugleich E5 (Reconciliation): die reale GM-Antwort meldet eine Usage, die
    WEIT ueber der (limitbasierten) Vor-Versand-Reservierung liegt -- der
    reale Betrag wird NACH Erhalt korrekt nachgebucht (nicht bei der kleinen
    Reservierung gedeckelt), wodurch ein ZWEITER GM-Turn unter demselben
    Budget korrekt blockiert wird (kein zweiter echter Request am Server)."""
    with tempfile.TemporaryDirectory() as td, FakeHTTPServer([
        (200, {
            "choices": [{"message": {"content": "Die Szene geht weiter, kein Abschlussmarker hier."}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 2000},
        }),
    ]) as srv:
        root = Path(td)
        run_dir, states_dir, ps_store, lobby, table = _bootstrap_solo_run(root)
        # max_usd gross genug, dass der generische Vor-Publish-Gate-Check
        # (`_check_gate()` OHNE Argumente, Pauschale 0.015 USD) die erste
        # Runde nicht selbst schon blockiert -- der eigentliche Gegenstand
        # dieses Tests ist die GM-Ausgabegrenze/Reconciliation, nicht dieser
        # unveraenderten generischen Zwischenpruefung.
        write_test_profile(run_dir, max_turns=10, max_usd=0.02)
        env = {"OPENWEBUI_URL": srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC", **_SYNTH_ENV}
        with patch.dict(os.environ, env):
            gm = GmOwuiTransport(
                _SL_CLIENT_PATH, run_dir, table_id="t-gm-output",
                sl_model="synthetic-model", kb_id="synthetic-kb", gm_output_limit_tokens=50,
            )
        assert gm.output_limit_tokens == 50
        assert gm.base_url == srv.base_url, "E3: base_url muss real vom Transport durchgereicht werden"

        outcome = _run_one_leader_turn(
            run_dir, states_dir, ps_store, lobby, table, gm,
            ["Kurze Leader-Aktion.", "Noch eine Aktion."], max_turns=5,
        )

        assert len(srv.calls) == 1, f"Positivpfad: GENAU EIN echter GM-Request muss durchgehen -- calls={srv.calls}"
        body = json.loads(srv.calls[0]["body"])
        assert body.get("max_tokens") == 50, f"E4: konfiguriertes Limit muss real im HTTP-Body stehen -- body={body}"

        status_after = json.loads((run_dir / "lab.status.json").read_text())
        # real = 2000/1000*0.015 = 0.03 (E5) -- WEIT ueber der limitbasierten
        # Reservierung (50 Ausgabe-Tokens ~ 0,00075 USD + winziger Inputanteil).
        # Ohne Reconciliation bliebe usd_spent bei der winzigen Reservierung
        # haengen; hier MUSS der reale Betrag sichtbar sein.
        assert status_after["usd_spent"] >= 0.03 - 1e-6, (
            f"E5: reale GM-Usage muss nachgebucht werden, nicht bei der kleinen "
            f"Reservierung gedeckelt bleiben -- status={status_after}"
        )
        assert status_after["usd_spent"] > 0.02, "Reconciliation muss das konfigurierte max_usd real ueberschreiten"

        # Der bereits reconciled hohe Verbrauch muss den NAECHSTEN GM-Turn
        # unter demselben Budget verhindern -- kein zweiter echter Request.
        assert len(srv.calls) == 1, "Kein zweiter echter GM-Request nach reconciled Budget-Ueberschreitung"
        assert not outcome.completion.success


def test_gm_no_configured_limit_and_no_hard_budget_reconciles_real_overrun_beyond_flat_pauschale():
    """Eigener, NICHT aus Test 06 abgeleiteter Output-seitiger Test (MAIN-
    ENTSCHEIDUNG: 'reale GM-Antwort > 0,015-unterstellte Menge'). Ohne
    konfigurierte Ausgabegrenze UND ohne hartes `max_usd` (Q07 greift hier
    nicht -- das ist bewusst der Fall, in dem der GM-Turn ueberhaupt erst
    versendet wird) reserviert `reservation_for_wire_text` die flache
    0,015-USD-Pauschale VOR dem Versand. Die reale Antwort meldet eine Usage,
    deren echter Gegenwert WEIT ueber dieser Pauschale liegt -- `usd_spent`
    muss NACH Erhalt den realen Betrag zeigen, nicht bei 0,015 verharren."""
    with tempfile.TemporaryDirectory() as td, FakeHTTPServer([
        (200, {
            "choices": [{"message": {"content": "Eine sehr ausfuehrliche SL-Antwort."}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 5000},
        }),
    ]) as srv:
        root = Path(td)
        run_dir, states_dir, ps_store, lobby, table = _bootstrap_solo_run(root)
        write_test_profile(run_dir, max_turns=10)  # BEWUSST kein max_usd (Q07 wuerde sonst vor Versand ablehnen).
        env = {"OPENWEBUI_URL": srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC", **_SYNTH_ENV}
        with patch.dict(os.environ, env):
            gm = GmOwuiTransport(_SL_CLIENT_PATH, run_dir, table_id="t-gm-output", sl_model="synthetic-model", kb_id="synthetic-kb")
        assert gm.output_limit_tokens is None

        _run_one_leader_turn(run_dir, states_dir, ps_store, lobby, table, gm, ["Kurze Leader-Aktion."])

        assert len(srv.calls) == 1
        status_after = json.loads((run_dir / "lab.status.json").read_text())
        # real = 5000/1000*0.015 = 0.075 -- die flache Pauschale allein waere
        # nur ~0.015 USD gewesen (plus winziger Inputanteil).
        assert status_after["usd_spent"] >= 0.075 - 1e-6, (
            f"reale GM-Antwort > 0,015-unterstellte Menge muss reconciled werden, nicht bei der "
            f"Pauschale verharren -- status={status_after}"
        )


# ---------------------------------------------------------------- Reconciliation-Matrix (Ledger-Ebene, E5)
def _begin_with_reserved(run_dir, reserved_usd=0.01):
    write_test_profile(run_dir)
    return request_ledger.begin(run_dir, role="gm_turn", content="Testinhalt", reserved_usd=reserved_usd)


def test_reconciliation_usage_none_no_reduction():
    """Case 05: verlorene/fehlende Usage -- `compute_turn_usd(None)` liefert
    `None` (Zeile 63 in admission.py, `if not usage`) -- keine Reduktion,
    Reservierung bleibt Endstand."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage=None)
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.01) < 1e-9, status


def test_reconciliation_usage_empty_dict_no_reduction():
    """`usage={}` ist wie `None` falsy -- durchlaeuft `compute_turn_usd`
    DENSELBEN fruehen `if not usage: return None`-Zweig (Zeile 63) wie
    `usage=None`, NICHT den separaten 'kein prompt_tokens/completion_tokens
    erkennbar'-Zweig (Zeile 71, s. naechster Test) -- am realen `OWUIChat.
    say()` ist das genau der Fall einer Antwort ohne Usage-Header
    (`self.last_usage = resp.get('usage') or {}`)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage={})
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.01) < 1e-9, status


def test_reconciliation_usage_present_but_no_recognized_cost_fields_no_reduction():
    """Der ZWEITE, tatsaechlich unterschiedliche `compute_turn_usd`-Codepfad
    (Zeile 71): ein NICHT-leeres `usage`-Dict OHNE `usd`/`cost_usd`/
    `prompt_tokens`/`completion_tokens` liefert ebenfalls `None` -- keine
    Reduktion."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage={"sources": ["a", "b"]})
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.01) < 1e-9, status


def test_reconciliation_real_less_than_reserved_is_not_refunded():
    """real < reserved: KEIN Refund -- die Vor-Versand-Reservierung ist ein
    konservativer Deckel nach oben, keine exakte Nachher-Abrechnung."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.02)
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.005})
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.02) < 1e-9, status


def test_reconciliation_real_equal_reserved_is_noop():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.01})
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.01) < 1e-9, status


def test_reconciliation_real_greater_than_reserved_books_delta_exactly_once():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05})
        status = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status["usd_spent"] - 0.05) < 1e-9, status
        on_disk = request_ledger.load_request(run_dir, request_id)
        assert on_disk["usd_reconciled"] is True
        assert on_disk["state"] == "accounted"


def test_reconciliation_finish_received_called_twice_same_usage_no_double_booking():
    """'doppelte Antwort/Verrechnung' (01_AUFTRAG_I2.md §4): ein Aufrufer,
    der `finish_received` versehentlich zweimal fuer dieselbe `request_id`
    aufruft (z.B. Retry-Pfad), darf das Delta NICHT zweimal buchen -- der
    bereits bestehende `state==accounted`-Fruehausstieg deckt das bereits ab,
    hier explizit gegen die NEUE Delta-Logik bewiesen."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        request_id = _begin_with_reserved(run_dir, reserved_usd=0.01)
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05})
        status_first = json.loads((run_dir / "lab.status.json").read_text())
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05})
        status_second = json.loads((run_dir / "lab.status.json").read_text())
        assert status_first == status_second, "zweiter Aufruf (state bereits accounted) muss ein No-op sein"


def test_reconciliation_write_failure_after_delta_booked_before_accounted_is_retry_safe():
    """PLAN-CRITIC Fallstrick 1/Auflage 5 -- Erweiterung von
    `test_i2_write_failure_between_received_and_accounted_keeps_reservation_committed`
    um den NEUEN Delta-Schritt: ein simulierter Schreibfehler beim ZWEITEN
    `_write_request`-Aufruf (received -> accounted) liegt strukturell NACH
    dem Delta-Buchungsaufruf (`record_usd_delta` sitzt an derselben Stelle
    wie `add_seconds`, ZWISCHEN den beiden `_write_request`-Aufrufen) -- das
    Delta MUSS bereits committet sein, UND ein Retry mit identischer Usage
    darf es NICHT ein zweites Mal buchen (idempotent gegen dieses Fenster)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=5, max_usd=1.0)
        request_id = request_ledger.begin(run_dir, role="gm_turn", content="x", reserved_usd=0.01)

        real_write = request_ledger._write_request
        call_count = {"n": 0}

        def _flaky_write(rd, rid, data):
            call_count["n"] += 1
            if call_count["n"] == 2:  # received -> accounted (NACH der Delta-Buchung).
                raise OSError("simulierter Schreibfehler nach Delta-Buchung, vor accounted")
            return real_write(rd, rid, data)

        with patch.object(request_ledger, "_write_request", side_effect=_flaky_write):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05})
                raised = False
            except OSError:
                raised = True
        assert raised, "Der simulierte Schreibfehler darf nicht still verschluckt werden."

        status_after_failure = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status_after_failure["usd_spent"] - 0.05) < 1e-9, (
            "Das Delta (real 0.05 - reserved 0.01 = 0.04) muss bereits VOR dem gescheiterten "
            f"accounted-Write committet sein -- status={status_after_failure}"
        )
        on_disk = request_ledger.load_request(run_dir, request_id)
        assert on_disk["state"] == "received"
        assert on_disk["usd_reconciled"] is True, "Marker muss bereits im selben Write wie state=received stehen"

        # Retry (z.B. nach Prozessneustart) mit identischer Usage -- das
        # Delta darf NICHT ein zweites Mal gebucht werden (Fallstrick 1).
        request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05})
        status_after_retry = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status_after_retry["usd_spent"] - 0.05) < 1e-9, (
            f"Retry darf das bereits committete Delta nicht doppelt buchen -- status={status_after_retry}"
        )
        on_disk_2 = request_ledger.load_request(run_dir, request_id)
        assert on_disk_2["state"] == "accounted"


_FRESH_PROCESS_RETRY_CHILD = (
    "import json,sys\n"
    "from pathlib import Path\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from mmo_sim.core import request_ledger as l\n"
    "rd=Path(sys.argv[2]); rid=sys.argv[3]\n"
    "saved=l.load_request(rd, rid)\n"
    "l.finish_received(rd, rid, usage=saved['usage'], seconds=0)\n"
    "print(json.dumps({'status':json.loads((rd/'lab.status.json').read_text()),"
    "'request':l.load_request(rd, rid)}))\n"
)


def _fresh_process_retry(run_dir: Path, request_id: str) -> dict:
    """B1 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24): ECHTER `python3`-
    Subprozess (kein neues Objekt im selben Interpreter, analog
    `test_i2_request_ledger_restart_and_write_failure.py`s Subprozess-Muster)
    -- laedt die bereits gespeicherte Usage aus dem Requestdatensatz und ruft
    `finish_received` fuer DIESELBE `request_id` erneut auf. Kein erneuter
    Modellaufruf (die Usage steht bereits im Requestdatensatz, s. `begin`/
    `finish_received`-Dokstring)."""
    result = subprocess.run(
        [sys.executable, "-c", _FRESH_PROCESS_RETRY_CHILD, str(_REPO_ROOT), str(run_dir), request_id],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_reconciliation_fresh_process_retry_after_delta_write_failure_books_delta_exactly_once():
    """B1/REVIEW-I2.md §3 Fall 02, als echter Prozess-Neustart (nicht nur die
    externe `review_i2_finish.py`): ein Fehler INNERHALB der Delta-Buchung
    selbst (`admission.record_usd_delta` schlaegt fehl, BEVOR sie irgendetwas
    schreibt) darf das reale Delta nicht dauerhaft verlieren -- ein GENUIN
    NEUER `python3`-Interpreter, der dieselbe `request_id` mit der bereits
    gespeicherten Usage erneut abschliesst, muss `usd_spent` auf den vollen
    realen Betrag (0,05) bringen, nicht bei der Reservierung (0,01) haengen
    bleiben und auch nicht auf 0,09 (Doppelbuchung) landen."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=20, max_usd=1.0)
        request_id = request_ledger.begin(run_dir, role="gm_turn", content="x", reserved_usd=0.01)

        with patch("mmo_sim.core.request_ledger.record_usd_delta", side_effect=OSError("INJECT vor Delta-Buchung")):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05}, seconds=0)
                raised = False
            except OSError:
                raised = True
        assert raised, "Die injizierte Ausnahme darf nicht still verschluckt werden."

        status_after_failure = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status_after_failure["usd_spent"] - 0.01) < 1e-9, (
            "Vor dem Retry darf noch keine Buchung stattgefunden haben -- der Injektionspunkt "
            f"liegt VOR jedem Schreibzugriff von record_usd_delta -- status={status_after_failure}"
        )

        retried = _fresh_process_retry(run_dir, request_id)
        assert abs(retried["status"]["usd_spent"] - 0.05) < 1e-9, (
            f"Fresh-Process-Retry muss das reale Delta (0,05 - 0,01 = 0,04) genau einmal "
            f"nachbuchen -- status={retried['status']}"
        )
        assert retried["request"]["state"] == "accounted"


def test_reconciliation_fresh_process_retry_after_delta_booked_does_not_double_book():
    """B1/REVIEW-I2.md §3 -- Spiegelbild von oben, als echter Prozess-
    Neustart: ein Fehler NACH erfolgreicher Delta-Buchung, aber VOR dem
    Endmarker (`state=accounted`) darf beim Retry NICHT ein zweites Mal
    gebucht werden (kein 0,09 statt 0,05)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=20, max_usd=1.0)
        request_id = request_ledger.begin(run_dir, role="gm_turn", content="x", reserved_usd=0.01)

        real_write = request_ledger._write_request
        call_count = {"n": 0}

        def _flaky_write(rd, rid, data):
            call_count["n"] += 1
            if call_count["n"] == 2:  # received -> accounted, NACH der Delta-Buchung.
                raise OSError("INJECT nach Delta-Buchung, vor Endmarker")
            return real_write(rd, rid, data)

        with patch.object(request_ledger, "_write_request", side_effect=_flaky_write):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05}, seconds=0)
                raised = False
            except OSError:
                raised = True
        assert raised, "Die injizierte Ausnahme darf nicht still verschluckt werden."

        status_after_failure = json.loads((run_dir / "lab.status.json").read_text())
        assert abs(status_after_failure["usd_spent"] - 0.05) < 1e-9, (
            f"Das Delta muss bereits VOR dem gescheiterten Endmarker-Write committet sein -- "
            f"status={status_after_failure}"
        )

        retried = _fresh_process_retry(run_dir, request_id)
        assert abs(retried["status"]["usd_spent"] - 0.05) < 1e-9, (
            f"Fresh-Process-Retry darf das bereits committete Delta NICHT doppelt buchen -- "
            f"status={retried['status']}"
        )
        assert retried["request"]["state"] == "accounted"


# ---------------------------------------------------------------- R2: semantische Testkopie am echten Fehlerpunkt (Fall 03)
def test_reconciliation_partial_temp_write_preserves_last_valid_published_state():
    """B1/R2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
    03) -- DOKUMENTIERTE semantische Testkopie AM ECHTEN heutigen
    Fehlerpunkt, ausdruecklich per GO erlaubt (MAIN-KORREKTUR-B1ABSCHLUSS.md
    'Ausdruecklich erlaubt (GO)'): der URSPRUENGLICHE externe Gegentest
    (`review_i2_accounting_edges.py:test_03_partial_budget_write_preserves_
    recoverable_published_state`, dort unveraendert als Herkunft erhalten)
    patchte `Path.write_text` DIREKT auf die Zieldatei `lab.status.json`.
    Seit dem R2-Fix (`core.admission._atomic_write_json`: erst Temp-Datei,
    dann `os.replace`) trifft dieser alte Patchpunkt die reale
    Veroeffentlichung nicht mehr -- der tatsaechliche `.05`/request-id-
    Schreibvorgang landet zuerst auf einer TEMP-Datei. Das ist laut
    MAIN-KORREKTUR der Fix, kein Regress. Diese Kopie verlegt die
    Fehlerinjektion an den ECHTEN heutigen Fehlerpunkt (Teilschreib-
    `OSError` GENAU auf der TEMP-Datei des Delta-Publish-Writes) und
    beweist DIESELBE Invariante: die Zieldatei bleibt exakt im zuletzt
    veroeffentlichten, gueltigen Zustand (hier: nur die Reservierung 0,01,
    keine reconciled_request_ids) -- kein halb geschriebenes/korruptes
    Dokument, kein `accounted`-Marker ohne belegte Buchung, keine liegen
    gebliebene Temp-Datei. Ein frischer Prozess-Retry erreicht danach den
    vollen realen Betrag (0,05) genau einmal."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=20, max_usd=1.0)
        request_id = request_ledger.begin(run_dir, role="gm_turn", content="x", reserved_usd=0.01)
        target = run_dir / "lab.status.json"
        before_raw = target.read_text(encoding="utf-8")

        real_write_text = Path.write_text
        fired = {"n": 0}

        def faulty_write_text(self, data, *args, **kwargs):
            if (
                fired["n"] == 0
                and self.parent == target.parent
                and self.name.startswith(target.name + ".tmp-")
                and f'"{request_id}"' in data
                and '"reconciled_request_ids"' in data
            ):
                fired["n"] += 1
                real_write_text(self, data[: len(data) // 2], *args, **kwargs)
                raise OSError("INJECT partial temp-file write at real R2 failure point (Prepare)")
            return real_write_text(self, data, *args, **kwargs)

        with patch.object(Path, "write_text", faulty_write_text):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05}, seconds=0)
                raised = False
            except OSError:
                raised = True
        assert raised, "Der simulierte Teilschreibfehler auf der Temp-Datei darf nicht still verschluckt werden."
        assert fired["n"] == 1, "Injektion muss den echten .05/request-id-Publish-Write (Temp-Datei) treffen"

        assert target.read_text(encoding="utf-8") == before_raw, (
            "Ein Teilschreibfehler auf der Temp-Datei darf die zuletzt veroeffentlichte "
            "lab.status.json NICHT veraendern (R2-Kerninvariante)."
        )
        on_disk = json.loads(target.read_text(encoding="utf-8"))
        assert on_disk.get("reconciled_request_ids", []) == []
        assert abs(on_disk["usd_spent"] - 0.01) < 1e-9

        on_disk_request = request_ledger.load_request(run_dir, request_id)
        assert on_disk_request["state"] == "received", (
            "Kein accounted-Marker, solange die Buchung nicht real veroeffentlicht wurde (R1)."
        )

        leftovers = [p.name for p in run_dir.glob(f"{target.name}.tmp-*")]
        assert leftovers == [], f"Verwaiste Temp-Datei(en) nach fehlgeschlagenem Publish: {leftovers}"

        retried = _fresh_process_retry(run_dir, request_id)
        assert abs(retried["status"]["usd_spent"] - 0.05) < 1e-9, (
            f"Fresh-Process-Retry muss den vollen realen Betrag (0,05) erreichen -- status={retried['status']}"
        )
        assert retried["request"]["state"] == "accounted"
        assert retried["status"]["reconciled_request_ids"].count(request_id) == 1


def test_reconciliation_publish_replace_failure_preserves_last_valid_published_state():
    """B1/R2 -- Fehlerpunktmatrix-Ergaenzung zum Test oben: Fehler am
    ZWEITEN Teilschritt von `_atomic_write_json` (`os.replace` selbst, NACH
    vollstaendigem Temp-Write, z.B. ein Cross-Device-Rename-Fehler), statt
    am ersten (Temp-Write). Beweist dieselbe Invariante an der anderen
    Haelfte der atomaren Veroeffentlichung: die Zieldatei bleibt
    unveraendert, solange der Rename nicht gelingt; kein `accounted` ohne
    belegte Buchung; ein frischer Retry erreicht 0,05 genau einmal."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=20, max_usd=1.0)
        request_id = request_ledger.begin(run_dir, role="gm_turn", content="x", reserved_usd=0.01)
        target = run_dir / "lab.status.json"
        before_raw = target.read_text(encoding="utf-8")

        real_replace = os.replace
        fired = {"n": 0}

        def faulty_replace(src, dst, *args, **kwargs):
            if fired["n"] == 0 and Path(dst) == target and Path(src).name.startswith(f"{target.name}.tmp-"):
                fired["n"] += 1
                raise OSError("INJECT publish (os.replace) failure at real R2 failure point")
            return real_replace(src, dst, *args, **kwargs)

        with patch("os.replace", side_effect=faulty_replace):
            try:
                request_ledger.finish_received(run_dir, request_id, usage={"usd": 0.05}, seconds=0)
                raised = False
            except OSError:
                raised = True
        assert raised, "Der simulierte os.replace-Fehler darf nicht still verschluckt werden."
        assert fired["n"] == 1, "Injektion muss den echten Publish-Rename des Delta-Writes treffen"

        assert target.read_text(encoding="utf-8") == before_raw, (
            "Ein Fehler beim atomaren Rename darf die zuletzt veroeffentlichte lab.status.json "
            "NICHT veraendern (R2-Kerninvariante)."
        )
        leftovers = [p.name for p in run_dir.glob(f"{target.name}.tmp-*")]
        assert leftovers == [], f"Verwaiste Temp-Datei(en) nach fehlgeschlagenem Rename: {leftovers}"

        on_disk_request = request_ledger.load_request(run_dir, request_id)
        assert on_disk_request["state"] == "received"

        retried = _fresh_process_retry(run_dir, request_id)
        assert abs(retried["status"]["usd_spent"] - 0.05) < 1e-9, (
            f"Fresh-Process-Retry muss den vollen realen Betrag (0,05) erreichen -- status={retried['status']}"
        )
        assert retried["request"]["state"] == "accounted"
        assert retried["status"]["reconciled_request_ids"].count(request_id) == 1


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
    raise SystemExit(main())
