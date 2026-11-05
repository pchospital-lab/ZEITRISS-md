#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r5_group_save_tischstop_resume_2026_11_05.py
-- ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R5, Teilauftrag `group-save-stop`
(kickoff.md Entscheidungsbaum, Ausgang B "bereits korrekt geschuetzt").

Der Tisch-/Gruppenkorrekturpfad (`core.save_correction.
pursue_group_save_correction`) hat KEINEN eigenen lokalen `stop_check` --
anders als der Einzelfigurpfad (R5a/d). Das ist KEIN Fehlerbeleg: beide
Sendewege der Gruppenfunktion (frische Runde UND Resume-Zweig) laufen auf
GENAU EINEN gemeinsamen Versandpunkt zusammen (`send_correction_turn` am
Ende der `while`-Schleife in `pursue_group_save_correction`), der bereits
VOR jedem Transport-Call `read_admission_block(..., table_id=table.
table_id)` aufruft -- und DIESE Funktion prueft seit ZR-BETREIBER O2
(2026-11-03) den tisch-adressierten Stop (`admission.read_table_stop`)
UNABHAENGIG von Live-/Budgetfreigabe (additiv wie `lab.stop`).

Dieser Test schliesst die bislang FEHLENDE direkte Evidenz fuer die
Gruppenfunktion selbst (die bestehende Regression `test_zr_betreiber_r2_
f2_tischstop_save_correction_2026_11_04.py` beweist nur `send_correction_
turn` isoliert, mit `role="save_correction_creation"`, NICHT den echten
Gruppenaufruf mit `ROLE_GROUP` und NICHT den Resume-Zweig):

 (1) Ein bereits offener `_open_round`-Marker (entstanden durch einen
     Deadline-vor-Versand-Block, `_r12_window_hold_fixture.close_window`,
     admission-seitig VOLLSTAENDIG getrennt vom Tischstop) wird beim naechsten
     Aufruf -- Fenster wieder offen, ABER jetzt ein gewonnener tisch-
     adressierter Betreiber-Stop fuer GENAU diese `table.table_id` aktiv --
     vor jedem Transport geblockt: der Resume-POST erreicht `_ExplodingGm.
     turn` NICHT. Die Runde wird terminal (`mark_hold` + `_clear_open_round`,
     admission_blocked ist KEINE Pre-Send-Deadline-Kategorie, s. `_save_
     correction_window.is_pre_send_deadline_reason`-Docstring) -- KEIN
     impliziter Doppelsend-Versuch, KEIN neuer Request.
 (2) Dieselbe gewonnene Stop-Entscheidung verhindert danach auch die
     Publikation: ein direkter `store.complete_section`-Aufruf mit
     VOLLSTAENDIG gueltigen Bloecken (simuliert eine spaet eintreffende,
     fuer sich genommen gueltige Antwort) bindet KEINEN Plan (`__plan.json`
     wird nicht geschrieben, `open_completion_order_for_table` bleibt
     `None`, kein `current_saves`-Write) -- der gemeinsame atomare
     Entscheid-Slot (`admission.try_commit_table_decision`) hat bereits
     `"stopped"` gewonnen, bevor `complete_section` um `"plan_committed"`
     konkurrieren kann.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_r12_window_hold_group.py`/`test_zr_betreiber_r2_f2_...py`."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402
from _r12_window_hold_fixture import close_window, open_window  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
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

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-r5-group-tischstop",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    def turn(self, *a, **k):
        raise AssertionError(
            "R5-group-tischstop: kein Transport-Call erwartet -- ein gewonnener tisch-adressierter "
            "Betreiber-Stop muss den Resume-POST VOR jedem Versand blockieren."
        )


def test_group_resume_post_blocked_by_table_stop_then_no_late_publication():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}

        # --- Setup: ein Deadline-vor-Versand-Block (admission-seitig VOELLIG
        # unabhaengig vom Tischstop) oeffnet eine Runde und haelt sie offen
        # (window_paused) -- derselbe, bereits bewiesene Mechanismus wie
        # test_r12_window_hold_group.py. Das ist NUR das Setup fuer den
        # eigentlich zu pruefenden Resume-Zweig unten.
        close_window(run_dir, deadline=1.0)
        harvest_completion = store.complete_section(
            lobby, table, "section-r5-tischstop", harvested, states_dir, "2026-11-05",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        harvested_blocked, completion_blocked = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-r5-tischstop", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-05",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_blocked.success and completion_blocked.missing == ["guest_pk"], completion_blocked
        open_round_path = save_correction._open_round_path(run_dir, table.table_id, "section-r5-tischstop")
        assert open_round_path.exists(), "Setup: der _open_round-Marker muss nach dem Deadline-Block offen bleiben."

        group_repair_key = save_correction_domain.group_repair_key(
            table.table_id, "section-r5-tischstop", "chrono-guest",
        )
        member_before = save_correction.load_record(run_dir, group_repair_key)
        assert member_before["state"] == "window_paused" and member_before["attempts_used"] == 1, member_before

        # --- (1) Fenster wieder offen, ABER jetzt ein gewonnener tisch-
        # adressierter Betreiber-Stop fuer GENAU diese table.table_id. Der
        # Resume-Zweig (`open_round is not None`) darf den offenen Marker
        # trotzdem NICHT einfach erneut senden -- er faellt auf DENSELBEN
        # `send_correction_turn`-Aufruf wie der Fresh-Zweig zurueck, der
        # `read_admission_block(table_id=table.table_id)` aufruft.
        open_window(run_dir)
        table_key, operator_id = "r5-tischstop-key", "operator_r5"
        table_admission.offer_table(run_dir, host_id=operator_id, table_key=table_key)
        table_admission.bind_section(
            run_dir, table_key=table_key, host_id=operator_id, section_id=table.table_id,
        )
        stop_payload = table_admission.request_table_stop(
            run_dir, table_key=table_key, operator_id=operator_id, table_id=table.table_id,
            reason="R5-group-tischstop: Betreiber stoppt waehrend offener Gruppenrunde.",
        )
        assert stop_payload.get("decision") == "stopped", stop_payload

        harvested_resumed, completion_resumed = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-r5-tischstop", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-05",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        # Unveraendert durchgereicht (Modul-Docstring: "gibt den zuletzt
        # erhaltenen CompletionResult unveraendert zurueck").
        assert completion_resumed is harvest_completion, (
            f"Resume MUSS bei gewonnenem Tischstop den unveraenderten CompletionResult zurueckgeben: "
            f"{completion_resumed}"
        )
        assert not open_round_path.exists(), (
            "Ein Tischstop-Block ist KEINE Pre-Send-Deadline-Kategorie (is_pre_send_deadline_reason "
            "prueft NUR den exakten Wall-Clock-Marker) -- die Runde muss terminal werden, der Marker "
            "geloescht (kein impliziter dritter Resume-Versuch fuer denselben offenen Marker)."
        )
        member_after = save_correction.load_record(run_dir, group_repair_key)
        assert member_after["state"] == "hold", member_after
        assert member_after["last_reason"].startswith("admission_blocked:"), member_after
        assert "Betreiber stoppt waehrend offener Gruppenrunde" in member_after["last_reason"], (
            f"der Blockgrund muss den tatsaechlichen tisch-adressierten Stopgrund tragen, nicht nur "
            f"einen generischen Text: {member_after['last_reason']!r}"
        )
        # KEIN zweiter Ledger-Request fuer denselben round_no (attempts_used
        # bleibt bei 1 -- derselbe Slot, kein Doppelzaehlen, kein neuer Send).
        assert member_after["attempts_used"] == 1, member_after

        # --- (2) Spaetpublikationssperre: dieselbe gewonnene Stop-Entscheidung
        # verhindert auch einen direkten complete_section-Aufruf mit
        # VOLLSTAENDIG gueltigen Bloecken (simuliert eine zwar gueltige, aber
        # NACH dem Stop verarbeitete Antwort) -- der atomare Entscheid-Slot
        # hat bereits "stopped" gewonnen.
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        guest_valid["economy"] = {"wallets": {"chrono-guest": {"balance": 500}}}
        late_completion = store.complete_section(
            lobby, table, "section-r5-tischstop", {"leader_pk": leader_valid, "guest_pk": guest_valid},
            states_dir, "2026-11-05", ZeitrissHarvestValidator(), ps_store,
        )
        assert not late_completion.success and not late_completion.written, late_completion
        assert "Betreiber-Stop" in late_completion.reason, late_completion.reason
        assert store.open_completion_order_for_table(run_dir, table.table_id) is None, (
            "kein Plan darf nach gewonnenem Stop gepinnt werden -- open_completion_order_for_table "
            "muss None bleiben."
        )
        assert not (run_dir / "current_saves" / "guest_pk.json").exists(), (
            "keine nachtraegliche Publikation des abgebrochenen Vorgangs."
        )


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
