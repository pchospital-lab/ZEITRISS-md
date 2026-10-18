#!/usr/bin/env python3
"""
tests/mmo_sim/test_w49_group_round_restart_2026_10_08.py — R12-Savegate,
W49-Slice: schliesst die in `W48-REPORT.md` §6 offen gemeldete Gruppenpfad-
Idempotenz-Luecke (`mmo_sim/core/save_correction.py:pursue_group_save_
correction`/`_next_round_no`). Bis W49 wurde die Rundenidentitaet
(`round_no`, als `turn_idx` in die `request_ledger`-Operationsidentitaet
eingehend) bei JEDEM rundeneroeffnenden Aufruf unbedingt weitergezaehlt --
ein Prozessabsturz GENAU zwischen "Runde eroeffnet" und "Antwort verarbeitet"
fuehrte bei einem Neustart zu einer NEUEN Runde (neue Identitaet) statt der
Wiederverwendung der bereits offenen/bereits beantworteten Reservierung --
die bereits gesendete/beantwortete Anfrage wurde dadurch in diesem engen
Fenster NICHT dedupliziert (ein zusaetzlicher realer SL-Turn war moeglich).

W49-Fix: ein `_group_rounds/<table>__<section>.open.json`-Marker (Mitglieder
+ `round_no`) wird VOR dem Versand persistiert und ERST NACH vollstaendiger
Verarbeitung der Antwort geloescht -- ein Neustart dazwischen findet den
Marker und reicht `send_correction_turn` dieselbe Operationsidentitaet
erneut ein (dieselbe Mechanik wie der bereits crash-sichere Einzelfigurpfad:
`request_ledger.find_durable_result`/`find_answered_without_text`/
`OpenReservationExistsError`), STATT eine neue Runde zu eroeffnen.

Abdeckung (Brief-Vorgabe, vier gezielte Crash-Injektionspunkte):
  W49-A -- Crash VOR Send (Runde bereits eroeffnet/Budget verbraucht, aber
           noch KEIN Transport-Call erfolgt).
  W49-B -- Crash NACH Response, VOR Checkpoint (Antwort bereits durabel im
           Ledger, aber noch nicht in `harvested`/Korrekturdatensatz
           uebernommen).
  W49-C -- Crash VOR Uebernahme bei MEHREREN Kandidaten derselben Runde (ein
           Kandidat bereits verarbeitet, der andere noch nicht -- Marker
           bleibt offen, bis BEIDE verarbeitet sind).
  W49-D -- Resume WAEHREND/NACH bestehender gueltiger Gruppenpublikation:
           kein Marker-Leck, kein weiterer Transport-Call, bestehende
           idempotente `store.complete_section`-Mechanik unangetastet.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang). Kein Netz, kein Livecall --
ausschliesslich kontrollierte, lokal geskriptete Fake-SL-Antworten."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    """Mild-pass, aber strukturell schema-ungueltig (identisches Muster zu
    `test_w48_save_correction_2026_10_07.py`'s `_wallet_as_number`)."""
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_two_member_table(run_dir: Path, states_dir: Path) -> tuple:
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-w49",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    """Wirft bei JEDEM Call -- Beleg, dass KEIN zusaetzlicher realer
    Transport-/SL-Turn fuer eine bereits offene/durabel beantwortete Runde
    ausgeloest wird."""

    def turn(self, *a, **k):
        raise AssertionError("W49: kein zusaetzlicher realer SL-Turn fuer eine bereits offene/beantwortete Runde.")


class _CountingGm:
    """Liefert der Reihe nach vorgegebene Antworten; zaehlt Aufrufe (fuer
    `store.submit_to_sl`-Aufrufe aus dem Gruppenpfad, Dreiargument-Turn-
    Vertrag reicht aus, `output_limit_tokens` ist hier nicht konfiguriert)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"_CountingGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _ledger_group_records(run_dir: Path) -> list[dict]:
    return [r for r in request_ledger._all_records(run_dir) if r.get("role") == save_correction_domain.ROLE_GROUP]


_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}


# ---------------------------------------------------------------------------
# W49-A -- Crash VOR Send: Runde bereits eroeffnet (Zaehler/Marker
# persistiert), aber noch KEIN Transport-Call erfolgt.
# ---------------------------------------------------------------------------

def test_w49a_crash_before_send_reuses_same_round_on_restart():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w49a", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        # Simulierter Crash "vor Send": EXAKT der Ablauf, den
        # `pursue_group_save_correction` beim Rundeneroeffnen selbst
        # durchlaeuft (Budget verbrauchen, Marker schreiben) -- DANACH
        # "crasht" dieser Prozess, bevor `send_correction_turn` je
        # aufgerufen wird.
        repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w49a", "chrono-guest")
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key="guest_pk", char_id="chrono-guest",
            operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id="section-w49a",
        )
        save_correction.begin_attempt(run_dir, repair_key)
        round_no = save_correction._next_round_no(run_dir, table.table_id, "section-w49a")
        save_correction._write_open_round(run_dir, table.table_id, "section-w49a", round_no, [
            {"persona_key": "guest_pk", "char_id": "chrono-guest", "original_block": guest_invalid},
        ])
        assert round_no == 1
        before = save_correction.load_record(run_dir, repair_key)
        assert before["attempts_used"] == 1 and before["state"] == "correction_pending"

        # "Neustart": frischer Aufruf mit einem funktionsfaehigen Transport
        # -- MUSS dieselbe (bereits eroeffnete) Runde fortsetzen, GENAU
        # EINEN realen Transport-Call ausloesen.
        # F-WALLET-LOSS (ZR-N2-LIVEBUNDLE-FRESH-20261018-R1): wertgleicher
        # Betrag (500) wie `guest_invalid`, nur gueltig geformt -- sonst
        # wertet der F-WALLET-LOSS-Fix das ersatzlose Verschwinden des
        # Wallets zu Recht als Drift statt als gueltige Korrektur.
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        gm = _CountingGm([f"```json\n{json.dumps(guest_valid)}\n```"])
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w49a", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_after.success, completion_after.reason
        assert len(gm.calls) == 1, f"genau EIN realer Transport-Call, kein Doppelversand -- {gm.calls}"
        assert gm.calls[0][0] == round_no, "derselbe round_no (dieselbe Operationsidentitaet) wird wiederverwendet."
        assert harvested_after["guest_pk"] == guest_valid

        after = save_correction.load_record(run_dir, repair_key)
        assert after["attempts_used"] == 1, (
            f"Budget darf durch den Restart NICHT doppelt verbraucht werden -- {after['attempts_used']}"
        )
        assert after["state"] == "adopted"

        ledger_records = _ledger_group_records(run_dir)
        assert len(ledger_records) == 1, f"genau EIN Ledger-Datensatz fuer die Runde, kein zweiter -- {ledger_records}"
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w49a").exists(), (
            "der Rundenmarker muss nach vollstaendiger Verarbeitung geloescht sein."
        )


# ---------------------------------------------------------------------------
# W49-B -- Crash NACH Response, VOR Checkpoint: Antwort bereits durabel im
# Ledger, aber noch NICHT in harvested/Korrekturdatensatz uebernommen.
# ---------------------------------------------------------------------------

def test_w49b_crash_after_response_before_checkpoint_reuses_durable_result():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w49b", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"]

        repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w49b", "chrono-guest")
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key="guest_pk", char_id="chrono-guest",
            operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id="section-w49b",
        )
        save_correction.begin_attempt(run_dir, repair_key)
        round_no = save_correction._next_round_no(run_dir, table.table_id, "section-w49b")
        save_correction._write_open_round(run_dir, table.table_id, "section-w49b", round_no, [
            {"persona_key": "guest_pk", "char_id": "chrono-guest", "original_block": guest_invalid},
        ])

        # Der tatsaechliche Versand laeuft VOLLSTAENDIG durch (Ledger bereits
        # `accounted`, Antwort durabel) -- DANACH "crasht" der Prozess, bevor
        # `record_correction_received`/die Harvest-Uebernahme je aufgerufen
        # wird (Marker bleibt bewusst offen).
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `guest_invalid`.
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        real_gm = _CountingGm([f"```json\n{json.dumps(guest_valid)}\n```"])
        message = save_correction_domain.build_group_correction_message(
            table_id=table.table_id, section_id="section-w49b", requests=[{
                "persona_key": "guest_pk", "char_id": "chrono-guest",
                "acceptance": save_correction_domain.evaluate(guest_invalid, "chrono-guest"),
                "original_block": guest_invalid, "attempt_no": 1,
            }],
        )
        first_send = save_correction.send_correction_turn(
            run_dir, role=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id="section-w49b",
            participant=table.leader, turn_idx=round_no, outgoing_text=message, gm_transport=real_gm, table=table,
        )
        assert first_send.blocked is False and len(real_gm.calls) == 1
        assert save_correction._open_round_path(run_dir, table.table_id, "section-w49b").exists(), (
            "Marker muss bis zur vollstaendigen Verarbeitung offen bleiben (simulierter Crash-Punkt)."
        )

        # "Neustart": ein Transport, der bei JEDEM Call wirft, belegt, dass
        # KEIN zweiter Versand fuer dieselbe Runde erfolgt -- die bereits
        # durabel vorliegende Antwort wird wiederverwendet.
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w49b", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_after.success, completion_after.reason
        assert harvested_after["guest_pk"] == guest_valid

        ledger_records = _ledger_group_records(run_dir)
        assert len(ledger_records) == 1, f"genau EIN Ledger-Datensatz, kein zweiter Versand -- {ledger_records}"
        after = save_correction.load_record(run_dir, repair_key)
        assert after["attempts_used"] == 1 and after["state"] == "adopted"
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w49b").exists()


# ---------------------------------------------------------------------------
# W49-C -- Crash VOR Uebernahme bei MEHREREN Kandidaten: einer bereits
# verarbeitet, der andere noch nicht -- Marker bleibt offen bis BEIDE
# verarbeitet sind, ein Neustart darf den bereits verarbeiteten Kandidaten
# gefahrlos (idempotent) erneut verarbeiten.
# ---------------------------------------------------------------------------

def test_w49c_partial_adoption_mid_round_resumes_both_members_without_resend():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        leader_invalid = _wallet_as_number("chrono-leader", name="Leader")
        guest_invalid = _wallet_as_number("chrono-guest", name="Guest")
        harvested = {"leader_pk": leader_invalid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w49c", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success
        assert set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w49c", "chrono-leader")
        guest_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w49c", "chrono-guest")
        for pk, char_id, rk in (("leader_pk", "chrono-leader", leader_repair_key), ("guest_pk", "chrono-guest", guest_repair_key)):
            save_correction.load_or_init_record(
                run_dir, rk, persona_key=pk, char_id=char_id,
                operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id="section-w49c",
            )
            save_correction.begin_attempt(run_dir, rk)
        round_no = save_correction._next_round_no(run_dir, table.table_id, "section-w49c")
        save_correction._write_open_round(run_dir, table.table_id, "section-w49c", round_no, [
            {"persona_key": "leader_pk", "char_id": "chrono-leader", "original_block": leader_invalid},
            {"persona_key": "guest_pk", "char_id": "chrono-guest", "original_block": guest_invalid},
        ])

        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `leader_invalid`/`guest_invalid`.
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        leader_valid["economy"] = {"wallets": {"chrono-leader": {"balance": 500}}}
        guest_valid = full_v7_save("chrono-guest", name="Guest")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        real_gm = _CountingGm([
            f"```json\n{json.dumps(leader_valid)}\n```\n```json\n{json.dumps(guest_valid)}\n```",
        ])
        message = save_correction_domain.build_group_correction_message(
            table_id=table.table_id, section_id="section-w49c", requests=[
                {"persona_key": "leader_pk", "char_id": "chrono-leader",
                 "acceptance": save_correction_domain.evaluate(leader_invalid, "chrono-leader"),
                 "original_block": leader_invalid, "attempt_no": 1},
                {"persona_key": "guest_pk", "char_id": "chrono-guest",
                 "acceptance": save_correction_domain.evaluate(guest_invalid, "chrono-guest"),
                 "original_block": guest_invalid, "attempt_no": 1},
            ],
        )
        sent = save_correction.send_correction_turn(
            run_dir, role=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id="section-w49c",
            participant=table.leader, turn_idx=round_no, outgoing_text=message, gm_transport=real_gm, table=table,
        )
        assert sent.blocked is False and len(real_gm.calls) == 1

        # Nur der LEADER wird vor dem simulierten Crash verarbeitet (Marker
        # bleibt bewusst offen -- die reale Schleife wuerde ihn erst nach
        # BEIDEN Kandidaten loeschen).
        save_correction.record_correction_received(run_dir, leader_repair_key, request_id=sent.request_id)
        save_correction.mark_adopted(run_dir, leader_repair_key)
        assert save_correction._open_round_path(run_dir, table.table_id, "section-w49c").exists()

        # "Neustart": frisch rekonstruiertes `harvested` (wie ein echter
        # Prozessneustart es aus dem urspruenglichen, unveraenderten
        # Debrief-Text liefern wuerde -- NOCH mit beiden urspruenglich
        # ungueltigen Bloecken), Transport wuerde bei einem echten
        # Zweitversand werfen.
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w49c", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_after.success, completion_after.reason
        assert harvested_after["leader_pk"] == leader_valid
        assert harvested_after["guest_pk"] == guest_valid

        ledger_records = _ledger_group_records(run_dir)
        assert len(ledger_records) == 1, f"genau EIN Ledger-Datensatz fuer BEIDE Kandidaten derselben Runde -- {ledger_records}"
        leader_record = save_correction.load_record(run_dir, leader_repair_key)
        guest_record = save_correction.load_record(run_dir, guest_repair_key)
        assert leader_record["attempts_used"] == 1 and leader_record["state"] == "adopted"
        assert guest_record["attempts_used"] == 1 and guest_record["state"] == "adopted"
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w49c").exists()


# ---------------------------------------------------------------------------
# W49-D -- Resume WAEHREND/NACH bestehender gueltiger Gruppenpublikation:
# kein Marker-Leck, kein weiterer Transport-Call, bestehende idempotente
# `store.complete_section`-Mechanik unangetastet (kein neuer
# Transaktionskern).
# ---------------------------------------------------------------------------

def test_w49d_resume_after_successful_publication_is_a_clean_noop():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w49d", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `guest_invalid`.
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        gm = _CountingGm([f"```json\n{json.dumps(guest_valid)}\n```"])
        harvested_done, completion_done = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w49d", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_done.success and len(gm.calls) == 1
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w49d").exists(), (
            "nach einer erfolgreichen Runde darf KEIN Marker zurueckbleiben (sonst wuerde eine "
            "spaetere, voellig neue Runde faelschlich als Wiederaufnahme gedeutet)."
        )
        assert store.open_completion_order_for_table(run_dir, table.table_id) == "section-w49d", (
            "PHASE 1 (Ernte) ist gepinnt -- die bestehende idempotente store.py-Mechanik hat uebernommen."
        )

        # "Resume" (z.B. ein Aufrufer, der die Korrekturschleife erneut
        # erreicht, obwohl die Gruppenpublikation bereits gueltig
        # abgeschlossen ist): KEIN weiterer Transport-Call, Ergebnis bleibt
        # unveraendert -- bestaetigt durch den bereits bestehenden Guard
        # (`while not harvest_completion.success`).
        harvested_again, completion_again = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w49d", harvested=dict(harvested_done),
            harvest_completion=completion_done, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_again is completion_done, "ein bereits erfolgreicher Abschluss wird unveraendert durchgereicht."
        assert harvested_again == harvested_done

        # Bestehende idempotente Produktmechanik (NICHT von W49 veraendert):
        # ein wiederholter `complete_section`-Aufruf mit denselben,
        # bereits gueltigen Bloecken bleibt idempotent (Resume-Zweig).
        repeat = store.complete_section(
            lobby, table, "section-w49d", harvested_done, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert repeat.success and repeat.members_completed == completion_done.members_completed
        ledger_records = _ledger_group_records(run_dir)
        assert len(ledger_records) == 1, "weder der Resume-Aufruf noch die wiederholte Publikation senden erneut."


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
