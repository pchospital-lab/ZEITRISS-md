#!/usr/bin/env python3
"""
tests/mmo_sim/test_w48_save_correction_2026_10_07.py — R12-Savegate, W48-
Slice: Zieltests fuer die persistente, request-gebundene, wiederaufnehmbare
SL-Korrekturschleife (`mmo_sim/domain/zeitriss/save_correction.py` +
`mmo_sim/core/save_correction.py`) UND den realen Gruppenabschluss, der sie
in die ECHTEN Produktpfade einhaengt (`core/creation_service.py:
run_admitted_creation_dialog`, `core/runtime.py:SectionRuntime.run_full_
section`).

Abdeckung (01_AUFTRAG_SAVEGATE.md §B/§C/§D, CASES.json -- W48-Fokus):
  SC04 -- Automatische gleiche-SL-Korrektur ueber den echten Produktweg.
  SC07 -- Max. 3 zusaetzliche Ausgaben je Figur+Operation, Restart setzt
          den Zaehler NICHT auf 0 zurueck.
  SC08 -- Admission-Gate VOR jedem Korrektur-POST (kein Transport-Call bei
          Blockade).
  SC09 -- Durables Requestergebnis: nach Antwort vor Checkpoint gecrasht ->
          received/accounted wiederverwendet, kein zweiter Versand.
  SC10 -- Unklare sent-Ausfuehrung (Crash zwischen Versand+Antwort) wird
          NIE retried/neu nummeriert -- kontrolliertes HOLD.
  SC11 -- Fuenf (hier: zwei) vor Harvest gueltig, NUR die fehlende/ungueltige
          Figur wird nachgefordert, bereits gueltige bleibt unangetastet.
  SC12 -- Marker/Ownership unveraendert: ein bereits gepinnter Abschluss-
          Auftrag (Resume) wird von der Korrekturschleife NICHT angefasst.
  SC13 -- Neustart WAEHREND einer offenen Korrekturantwort (Crash zwischen
          Versand und Auswertung) setzt KEINEN neuen Story-/SL-Zug ab und
          zaehlt den bereits begonnenen Versuch nicht doppelt.
  SC14 -- Teilpublikation/Reflexion bleibt idempotent (vorhandene, hier
          NICHT veraenderte `store.py`-Mechanik) auch nach einem durch
          Korrektur vervollstaendigten Gruppenabschluss.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile, _atomic_write_json, _status_path  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str) -> dict:
    """Mild-pass, aber strukturell schema-ungueltig (identisches Muster zu
    `test_w43_...`'s `_wallet_as_number`): `economy.wallets.<id>` ist eine
    blanke Zahl statt `{"balance": ...}`-Objekt."""
    block = full_v7_save(char_id, name="Flo")
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def _never_called_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError("get_reply sollte hier nie aufgerufen werden -- die SL liefert den Save direkt.")


class _ScriptedGm:
    """Liefert der Reihe nach vorgegebene Antworten; zaehlt Aufrufe. Wirft,
    wenn mehr Aufrufe erfolgen als Antworten vorgegeben wurden (Beleg: KEIN
    Transport-Call bei einer erwarteten Blockade/Wiederverwendung)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(
                f"_ScriptedGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}) -- "
                "keine weiteren gecannten Antworten (Beleg gegen Doppelversand/HOLD-Verletzung)."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _never_called_gm() -> _ScriptedGm:
    gm = _ScriptedGm([])
    return gm


# ---------------------------------------------------------------------------
# SC04 -- Automatische gleiche-SL-Korrektur ueber den echten Produktweg.
# ---------------------------------------------------------------------------

def test_sc04_single_figure_correction_same_session_no_manual_json():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "flo_sc04"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        invalid_block = _wallet_as_number("CHR-SC04-01")
        valid_block = full_v7_save("CHR-SC04-01", name="Flo")
        gm = _ScriptedGm([
            "```json\n" + json.dumps(invalid_block) + "\n```",
            "```json\n" + json.dumps(valid_block) + "\n```",
        ])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "completed", f"Korrektur ueber dieselbe Session muss abschliessen -- {outcome}"
        assert outcome.save_block == valid_block
        assert len(gm.calls) == 2, "genau EIN ursprunglicher + EIN Korrektur-Turn, kein manuelles JSON."

        state = onboarding.peek(onboarding_dir, participant_id)
        assert state.status == "completed"
        assert state.final_save == valid_block

        repair_key = save_correction_domain.creation_repair_key(participant_id, "CHR-SC04-01")
        record = save_correction.load_record(run_dir, repair_key)
        assert record is not None and record["attempts_used"] == 1 and record["state"] == "adopted", record

        # Beleg "dedizierte Korrekturrolle, nicht gm_turn/persona_decision":
        ledger_records = [
            r for r in request_ledger._all_records(run_dir)
            if r.get("role") == save_correction_domain.ROLE_CREATION
        ]
        assert len(ledger_records) == 1 and ledger_records[0]["participant"] == participant_id


# ---------------------------------------------------------------------------
# SC07 -- Max. 3 zusaetzliche Ausgaben, Restart setzt NICHT auf 0 zurueck.
# ---------------------------------------------------------------------------

def test_sc07_max_three_additional_requests_then_hold_restart_does_not_reset():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "flo_sc07"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        invalid_block = _wallet_as_number("CHR-SC07-01")
        always_invalid_text = "```json\n" + json.dumps(invalid_block) + "\n```"
        gm = _ScriptedGm([always_invalid_text] * 4)  # 1 Initialturn + 3 Korrekturversuche
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "paused" and outcome.reason == "attempt_budget_exhausted", outcome
        assert len(gm.calls) == 4, f"genau 1 Initialturn + 3 zusaetzliche Ausgaben, nicht mehr/weniger -- {gm.calls}"

        repair_key = save_correction_domain.creation_repair_key(participant_id, "CHR-SC07-01")
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 3 and record["state"] == "hold"

        # Neustart-Beleg: ein NEUER Kandidat (anderer Hash/Inhalt) fuer
        # DIESELBE Identitaet (participant_id, char_id) darf den Zaehler
        # NICHT auf 0 zuruecksetzen -- sofortiges HOLD, KEIN weiterer Versand.
        other_invalid_block = _wallet_as_number("CHR-SC07-01")
        other_invalid_block["campaign"]["mission"] = 99  # anderer Inhalt/Hash als zuvor
        never_called = _never_called_gm()
        restarted = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id="CHR-SC07-01",
            candidate_block=other_invalid_block, gm_transport=never_called,
        )
        assert restarted.status == "hold" and restarted.reason == "attempt_budget_exhausted"
        assert never_called.calls == [], "nach Budget-Erschoepfung darf KEIN weiterer Transport-Call erfolgen."
        record_after_restart = save_correction.load_record(run_dir, repair_key)
        assert record_after_restart["attempts_used"] == 3, "Zaehler bleibt restart-fest bei 3, kein Reset auf 0."


# ---------------------------------------------------------------------------
# SC08 -- Admission-Gate VOR jedem Korrektur-POST.
# ---------------------------------------------------------------------------

def test_sc08_admission_gate_blocks_before_any_correction_transport_call():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir, max_turns=0)  # sofort erschoepft -- blockiert VOR jedem Versand

        never_called = _never_called_gm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id="flo_sc08", expected_chrononaut_id="CHR-SC08-01",
            candidate_block=_wallet_as_number("CHR-SC08-01"), gm_transport=never_called,
        )
        assert outcome.status == "hold" and outcome.reason.startswith("admission_blocked"), outcome
        assert never_called.calls == [], "Admission-Gate muss den Transport-Call verhindern, nicht nur nachtragen."

        repair_key = save_correction_domain.creation_repair_key("flo_sc08", "CHR-SC08-01")
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 1, "der blockierte Versuch zaehlt (jede Nachricht zaehlt, auch ohne Antwort)."
        assert record["state"] == "hold"


# ---------------------------------------------------------------------------
# SC09 -- Durables Requestergebnis: Crash nach Antwort, vor Checkpoint.
# ---------------------------------------------------------------------------

def test_sc09_durable_result_reused_after_crash_before_checkpoint():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir)

        gm = _ScriptedGm(["```json\n" + json.dumps(full_v7_save("CHR-SC09-01")) + "\n```"])
        first = save_correction.send_correction_turn(
            run_dir, role="save_correction_creation", table_id=None, section_id=None,
            participant="flo_sc09", turn_idx=1, outgoing_text="Korrektur bitte.", gm_transport=gm,
        )
        assert first.blocked is False and len(gm.calls) == 1

        # "Crash nach Antwort, vor Checkpoint": eine zweite Prozessinstanz
        # (hier: ein zweiter Aufruf mit einem Transport, der bei JEDEM
        # Call wirft) ruft send_correction_turn fuer EXAKT dieselbe
        # Operationsidentitaet erneut auf -- MUSS die bereits durabel
        # empfangene Antwort wiederverwenden, OHNE den Transport nochmal
        # aufzurufen.
        class _ExplodingGm:
            def turn(self, *a, **k):
                raise AssertionError("SC09: kein zweiter Versand fuer bereits durabel empfangenes Ergebnis.")

        second = save_correction.send_correction_turn(
            run_dir, role="save_correction_creation", table_id=None, section_id=None,
            participant="flo_sc09", turn_idx=1, outgoing_text="Korrektur bitte.", gm_transport=_ExplodingGm(),
        )
        assert second.blocked is False and second.text == first.text and second.request_id == first.request_id


# ---------------------------------------------------------------------------
# SC10 -- Unklare sent-Ausfuehrung: NIE retryen/neu nummerieren.
# ---------------------------------------------------------------------------

def test_sc10_unclear_sent_in_flight_never_retried_or_renumbered():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir)

        # Simuliert einen Crash GENAU zwischen Versand (`begin()` ->
        # state=sent) und Antwort/Fehlerabschluss -- der Datensatz bleibt
        # bei state=sent haengen (weder finish_received noch finish_error
        # wurde je aufgerufen).
        request_id = request_ledger.begin(
            run_dir, role="save_correction_creation", content="Korrektur bitte.", reserved_usd=0.001,
            turn_idx=1, participant="flo_sc10",
        )
        before = request_ledger.load_request(run_dir, request_id)
        assert before["state"] == "sent"

        class _ExplodingGm:
            def turn(self, *a, **k):
                raise AssertionError("SC10: eine unklare sent-Ausfuehrung darf NIE einen neuen Versand ausloesen.")

        outcome = save_correction.send_correction_turn(
            run_dir, role="save_correction_creation", table_id=None, section_id=None,
            participant="flo_sc10", turn_idx=1, outgoing_text="Korrektur bitte.", gm_transport=_ExplodingGm(),
        )
        assert outcome.blocked is True and outcome.reason.startswith("unclear_sent_in_flight")
        after = request_ledger.load_request(run_dir, request_id)
        assert after == before, "der unklare Requestdatensatz bleibt unveraendert (kein Ueberschreiben/Neu-UUID)."


# ---------------------------------------------------------------------------
# SC11 (Gruppenvariante) / SC12 / SC14 -- Gruppenabschluss-Harness.
# ---------------------------------------------------------------------------

def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


class _ScriptedDriver:
    def __init__(self, script):
        self._script = list(script)

    def decide(self, context):
        return self._script.pop(0)


def _build_two_member_table():
    root = Path(tempfile.mkdtemp())
    run_dir, states_dir = root / "run", root / "states"
    states_dir.mkdir(parents=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-w48",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, run_dir, states_dir, ps_store


def test_sc11_group_only_missing_member_renotified_valid_untouched():
    lobby, table, run_dir, states_dir, ps_store = _build_two_member_table()
    leader_save = full_v7_save("chrono-leader", name="Leader")
    guest_invalid = _wallet_as_number("chrono-guest")
    guest_valid = full_v7_save("chrono-guest", name="Flo")  # dieselbe Identitaet wie guest_invalid (SC05: keine Namensdrift)

    debrief = (
        "Abschnitt beendet.\n"
        f"```json\n{json.dumps(leader_save)}\n```\n"
        f"```json\n{json.dumps(guest_invalid)}\n```\n"
        f"{COMPLETION_MARKER}"
    )
    correction_reply = f"```json\n{json.dumps(guest_valid)}\n```"
    gm_turns = ["SL-Antwort auf Anker-Turn.", "SL-Antwort auf Gast-Turn.", debrief, correction_reply]

    class _GroupGm:
        def __init__(self, scripted):
            self._scripted = list(scripted)
            self.calls: list[tuple[int, str]] = []

        def turn(self, turn_idx, user_text, **kwargs):
            self.calls.append((turn_idx, user_text))
            return {"content": self._scripted.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}

    gm = _GroupGm(gm_turns)
    leader_driver = _ScriptedDriver([
        ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief.", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion: ok.", origin_source="fake:leader-reflect"),
    ])
    guest_driver = _ScriptedDriver([
        ParticipantDecision(text="Turn.", save_payload=guest_invalid, origin_source="fake:guest"),
        ParticipantDecision(text="Reflexion: ok.", origin_source="fake:guest-reflect"),
    ])
    from mmo_sim.core.controller import TableController
    controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
    event_log = EventLog(run_dir)
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=event_log,
    )
    outcome = runtime.run_full_section(
        controller, "section-w48-sc11",
        contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
        states_dir=states_dir, today="2026-10-07", ts="2026-10-07T18:00:00",
    )
    assert outcome.completion.success, outcome.completion.reason
    assert store.load_current_save(run_dir, "leader_pk", ps_store, states_dir=states_dir) == leader_save, (
        "der bereits gueltige Leader-Save bleibt unveraendert -- nur die fehlende Figur wurde nachgefordert."
    )
    assert store.load_current_save(run_dir, "guest_pk", ps_store, states_dir=states_dir) == guest_valid

    group_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w48-sc11", "chrono-guest")
    record = save_correction.load_record(run_dir, group_repair_key)
    assert record is not None and record["attempts_used"] == 1 and record["state"] == "adopted"
    assert save_correction.load_record(
        run_dir, save_correction_domain.group_repair_key(table.table_id, "section-w48-sc11", "chrono-leader"),
    ) is None, "fuer die von Anfang an gueltige Leader-Figur darf NIE ein Korrekturdatensatz entstehen."

    # SC14 (Teilbeleg): Harvest+Reflexion+Finalize sind bereits abgeschlossen
    # -- ein wiederholter Aufruf der bestehenden PHASE-2-Funktion bleibt
    # idempotent (vorhandene, von W48 NICHT veraenderte Mechanik).
    repeat = store.finalize_section_after_reflection(lobby, table, "section-w48-sc11")
    assert repeat.success and repeat.already_completed, "wiederholter Finalize-Aufruf muss idempotent bleiben (SC14)."
    return lobby, table, run_dir, states_dir, ps_store


def test_sc12_pinned_plan_resume_is_not_touched_by_correction():
    """SC12/§B: ein BEREITS gepinnter Abschluss-Auftrag (Resume-Fall) ist eine
    committete Entscheidung -- die Korrekturschleife darf ihn NICHT anfassen,
    selbst wenn er (hier konstruiert) ein fehlendes Mitglied zeigen wuerde."""
    lobby, table, run_dir, states_dir, ps_store = _build_two_member_table()
    leader_save = full_v7_save("chrono-leader", name="Leader")
    guest_save = full_v7_save("chrono-guest", name="Guest")

    harvest_completion = store.complete_section(
        lobby, table, "section-w48-sc12", {"leader_pk": leader_save, "guest_pk": guest_save},
        states_dir, "2026-10-07", ZeitrissHarvestValidator(), ps_store,
    )
    assert harvest_completion.success, harvest_completion.reason
    assert store.open_completion_order_for_table(run_dir, table.table_id) == "section-w48-sc12", (
        "PHASE 1 (Ernte) ist abgeschlossen, PHASE 2 (Reflexion/Finalize) noch nicht -- der Auftrag "
        "muss jetzt als gepinnt/offen erkennbar sein."
    )

    never_called = _never_called_gm()
    harvested, resumed = save_correction.pursue_group_save_correction(
        lobby=lobby, table=table, section_id="section-w48-sc12", harvested={}, harvest_completion=harvest_completion,
        states_dir=states_dir, today="2026-10-07", harvest_validator=ZeitrissHarvestValidator(),
        persona_state_store=ps_store, gm_transport=never_called, cid_to_pk={}, harvest_extractor=lambda *a: {},
    )
    assert resumed is harvest_completion, "ein bereits erfolgreicher Abschluss wird unveraendert durchgereicht."
    assert never_called.calls == [], "KEIN Korrektur-Transport-Call fuer einen bereits gepinnten Auftrag."


# ---------------------------------------------------------------------------
# SC13 -- Neustart waehrend offener Korrekturantwort (Crash vor Auswertung).
# ---------------------------------------------------------------------------

def test_sc13_restart_mid_open_correction_response_no_double_count_no_new_turn():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir)

        valid_block = full_v7_save("CHR-SC13-01")
        gm = _ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])

        # Schritt 1: der Versand selbst laeuft vollstaendig durch (Ledger
        # bereits `accounted`), aber die Korrekturschleife "crasht" HIER --
        # es wird absichtlich NICHT weiter ausgewertet/adoptiert (simuliert
        # einen Prozessabbruch genau zwischen Antwort und Checkpoint).
        outcome1 = save_correction.send_correction_turn(
            run_dir, role=save_correction_domain.ROLE_CREATION, table_id=None, section_id=None,
            participant="flo_sc13", turn_idx=1, outgoing_text="Korrektur 1/3.", gm_transport=gm,
        )
        assert outcome1.blocked is False and len(gm.calls) == 1
        save_correction.load_or_init_record(
            run_dir, save_correction_domain.creation_repair_key("flo_sc13", "CHR-SC13-01"),
            persona_key="flo_sc13", char_id="CHR-SC13-01", operation_key=save_correction_domain.ROLE_CREATION,
            errors=["vorheriger Fehlerkatalog"],
        )
        save_correction.begin_attempt(run_dir, save_correction_domain.creation_repair_key("flo_sc13", "CHR-SC13-01"))
        # KEIN record_correction_received()/keine Auswertung hier -- genau
        # das ist der simulierte Crash-Zeitpunkt.

        # Schritt 2: "Neustart" -- ein frischer Aufruf von
        # `pursue_single_figure_correction` fuer DIESELBE Identitaet. Der
        # uebergebene gm_transport wuerde bei einem ECHTEN Neuversand
        # werfen -- der tatsaechliche Resume MUSS stattdessen den bereits
        # durabel vorliegenden Text aus Schritt 1 wiederverwenden (kein
        # neuer Story-/SL-Zug).
        class _ExplodingGm:
            def turn(self, *a, **k):
                raise AssertionError("SC13: Neustart darf KEINEN neuen SL-Zug fuer denselben Slot aussenden.")

        result = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id="flo_sc13", expected_chrononaut_id="CHR-SC13-01",
            candidate_block=_wallet_as_number("CHR-SC13-01"), gm_transport=_ExplodingGm(),
        )
        assert result.status == "accepted" and result.block == valid_block, result

        repair_key = save_correction_domain.creation_repair_key("flo_sc13", "CHR-SC13-01")
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 1, "der bereits begonnene Slot wird wiederaufgenommen, NICHT doppelt gezaehlt."


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
