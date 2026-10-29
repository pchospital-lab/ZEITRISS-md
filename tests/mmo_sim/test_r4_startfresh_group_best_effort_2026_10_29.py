#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_startfresh_group_best_effort_2026_10_29.py -- R4-
STARTFRESH (Owner-Vertrag, 2026-10-28): der Save-Gate ist BEST-EFFORT. Pro
Chrononaut gibt die KI-SL bis zu `MAX_ADDITIONAL_REQUESTS` Nachbesserungen
aus (01_AUFTRAG_SAVEGATE.md §C). Sind danach noch Schema-Imperfektionen da,
nimmt die App den MAXIMAL-KONFORMEN Kandidaten (wenigste Strukturfehler
ueber die Versuche) und schliesst den Abschnitt ab -- ehrlich als
`best_effort=True` geflaggt (KEIN Fake-DONE). Das ueberschreibt die fruehere
§C-Formulierung "kein kuenstlicher Erfolg" (ein General-Drift). Dieser Fix
bringt den GRUPPENPFAD (`save_correction.pursue_group_save_correction` +
`core.store.complete_section`) auf denselben Vertrag wie der bereits
bestehende Einzelfigurpfad (`pursue_single_figure_correction`s
`attempt_budget_exhausted`-Zweig -> `onboarding.complete_with_save_best_
effort`).

Vier Szenarien (01_AUFTRAG_SAVEGATE-Nachtrag):
  (a) Gruppe erschoepft mit ueber-Cap (7 shared_echoes) Kandidaten fuer
      BEIDE Mitglieder -> best-effort-Abschluss: `complete_section` success,
      `__final.json` `best_effort=True`, der maximal-konforme (hier: der
      einzige je beobachtete) Kandidat wird adoptiert.
  (b) Maximal-konform-Auswahl: 3 Kandidaten mit unterschiedlicher Fehlerzahl
      -> der mit den wenigsten wird adoptiert (Gleichstand: der spaetere).
  (c) Ein per `detect_unjustified_drift` abgelehnter Kandidat bleibt
      terminal HOLD -- KEIN best-effort, selbst wenn das noch fehlende
      Mitglied danach die einzige Ursache fuer den erschoepften
      "keine Kandidaten mehr"-Zweig ist.
  (d) `best_effort=False` (Default, `store.complete_section`) -- Verhalten
      unveraendert: ein schema-ungueltiger Block bleibt `missing`, kein
      Plan wird gepinnt.
  (e)/(f) RECONCILIATION-V3 (2026-10-29, SAVECOMPAT-Vorrang, verfeinert):
      Prinzip -- SAVECOMPAT = Wert-/Form-/Typ-Reparatur (deterministisch
      ODER per SL ableitbarer korrekter Einzelwert), Best-Effort = NUR
      strukturelle Cap-Ueberlaeufe (`maxItems`/`minItems`, kein korrekter
      Einzelwert). (e): ein Wallet-als-Zahl-Kandidat (nach `project_
      wallets_in_block` schema-gueltig) -> KEIN Best-Effort. (f): ein
      Kandidat mit NUR einem typfalschen Nicht-Wallet-Feld (`lvl` als
      String, KEIN maxItems) -> ebenfalls KEIN Best-Effort (das Prinzip
      gilt generisch, nicht nur fuer Wallet-Faelle). Beide Tests fahren
      dieselbe Kontrastprobe mit einem `maxItems`-Ueberlaengen-Kandidaten
      -> Best-Effort greift dort weiterhin.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes
(`ScriptedGmTransport`/`build_two_member_table` aus
`_section_completion_resume_fixtures.py`), kein realer Transport, keine
echte CLI, keine echte GM-Route."""
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
from _r12_window_hold_fixture import open_window  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ScriptedGmTransport, build_two_member_table, make_env,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_CID_TO_PK = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk"}


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def _overlong_invalid(cid: str, name: str = "Testfigur") -> dict:
    """Sonst gueltiger v7-Save mit sieben `continuity.shared_echoes`
    (maxItems 6) -- schema-ungueltig, aber sauber extrahierbar (ein fenced
    Block, genau eine Figur, richtige char_id). Dieselbe Konstruktion wie
    `test_r4_duo_exhausted_correction_resume_no_story_2026_10_28.py`s
    `_overlong_invalid` (hier dupliziert, reiner Testcode -- kein
    Produktimport)."""
    block = full_v7_save(cid, name=name)
    block.setdefault("continuity", {})
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "shared", "text": f"nicht-leer-{i}"} for i in range(7)
    ]
    return block


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    open_window(env.run_dir)
    return env, lobby, table, ps_store


# ---------------------------------------------------------------------------
# (a) Gruppe erschoepft mit ueber-Cap Kandidaten fuer BEIDE Mitglieder ->
#     best-effort-Abschluss.
# ---------------------------------------------------------------------------

def test_group_exhausted_with_overcap_candidates_completes_best_effort():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-besteffort-a")
        section_id = "section-besteffort-a"

        harvested: dict = {}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        max_attempts = sc.MAX_ADDITIONAL_REQUESTS
        invalid_leader = _overlong_invalid(_LEADER_CID, name="Leader")
        invalid_guest = _overlong_invalid(_GUEST_CID, name="Guest")
        one_response = (
            "Technische Speicherkorrektur (bleibt ueber-Cap).\n"
            + _fenced_json(invalid_leader) + "\n" + _fenced_json(invalid_guest)
        )
        gm = ScriptedGmTransport(scripted_contents=[one_response] * max_attempts)

        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        # R4-STARTFRESH: der vormalige "ehrliche HOLD" ist jetzt ein
        # ehrlich geflaggter best-effort-ERFOLG.
        assert completion_out.success, completion_out
        assert len(gm.calls) == max_attempts, gm.calls
        assert harvested_out["leader_pk"] == invalid_leader
        assert harvested_out["guest_pk"] == invalid_guest

        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert leader_record["state"] == "adopted" and leader_record.get("best_effort") is True, leader_record
        assert guest_record["state"] == "adopted" and guest_record.get("best_effort") is True, guest_record
        assert leader_record["adopted_block"] == invalid_leader
        assert guest_record["adopted_block"] == invalid_guest
        # KEIN Counter-Reset -- die volle Versuchshistorie bleibt erhalten.
        assert leader_record["attempts_used"] == max_attempts
        assert guest_record["attempts_used"] == max_attempts

        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert plan_path.exists()
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert plan_data.get("best_effort") is True
        assert plan_data["members"]["leader_pk"].get("best_effort") is True
        assert plan_data["members"]["guest_pk"].get("best_effort") is True

        # PHASE 2 (Reflexion bereits erfolgreich angenommen, hier direkt
        # simuliert -- kein neuer Mechanismus): `__final.json` traegt
        # dieselbe ehrliche Flagge.
        finalize_result = store.finalize_section_after_reflection(lobby, table, section_id)
        assert finalize_result.success, finalize_result
        final_path = store._completion_final_path(env.run_dir, section_id)
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        assert final_data.get("best_effort") is True, final_data
        assert set(final_data.get("best_effort_members") or []) == {"leader_pk", "guest_pk"}, final_data


# ---------------------------------------------------------------------------
# (b) Maximal-konform-Auswahl: der Kandidat mit den wenigsten Strukturfehlern
#     gewinnt; bei Gleichstand der spaetere Aufruf.
# ---------------------------------------------------------------------------

def test_update_best_candidate_keeps_least_error_count_later_wins_tie():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        repair_key = "unit-best-candidate-repair-key"
        sc.load_or_init_record(
            run_dir, repair_key, persona_key="pk1", char_id="CHR-UNIT-X", operation_key=sc.ROLE_GROUP,
        )
        block_worst = {"marker": "worst", "errors": 7}
        block_best = {"marker": "best", "errors": 2}
        block_middle = {"marker": "middle", "errors": 4}

        sc.update_best_candidate(run_dir, repair_key, block=block_worst, error_count=7)
        record1 = sc.load_record(run_dir, repair_key)
        assert record1["best_candidate_block"] == block_worst and record1["best_candidate_error_count"] == 7

        sc.update_best_candidate(run_dir, repair_key, block=block_best, error_count=2)
        record2 = sc.load_record(run_dir, repair_key)
        assert record2["best_candidate_block"] == block_best and record2["best_candidate_error_count"] == 2

        # Ein schlechterer Kandidat (mehr Fehler) ueberschreibt den
        # bisherigen Bestwert NICHT.
        sc.update_best_candidate(run_dir, repair_key, block=block_middle, error_count=4)
        record3 = sc.load_record(run_dir, repair_key)
        assert record3["best_candidate_block"] == block_best and record3["best_candidate_error_count"] == 2

        # Gleichstand (gleiche Fehlerzahl wie der bisherige Bestwert) -- der
        # SPAETERE Aufruf gewinnt (<=, nicht <).
        block_tie = {"marker": "tie", "errors": 2}
        sc.update_best_candidate(run_dir, repair_key, block=block_tie, error_count=2)
        record4 = sc.load_record(run_dir, repair_key)
        assert record4["best_candidate_block"] == block_tie and record4["best_candidate_error_count"] == 2


# ---------------------------------------------------------------------------
# (c) Ein per `detect_unjustified_drift` abgelehnter Kandidat bleibt
#     terminal HOLD -- KEIN best-effort, auch wenn er danach der einzige
#     Grund fuer den "keine Kandidaten mehr"-Zweig ist.
# ---------------------------------------------------------------------------

def test_drift_candidate_stays_terminal_hold_without_best_effort():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-besteffort-c")
        section_id = "section-besteffort-c"

        # Leader ist von Anfang an gueltig (nicht Teil der Korrektur) --
        # NUR der Gast braucht eine Nachforderung.
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        guest_old_invalid = _overlong_invalid(_GUEST_CID, name="OldGuestName")
        harvested = {"leader_pk": leader_save, "guest_pk": guest_old_invalid}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        # Die SL-Antwort ist schema-valide, aendert aber den Figurennamen --
        # ein unbegruendeter inhaltlicher Wechsel ausserhalb der gemeldeten
        # Fehlerpfade (die betrafen `continuity.shared_echoes`, NICHT den
        # Namen) -- `detect_unjustified_drift` muss das als Drift werten.
        guest_drifted = full_v7_save(_GUEST_CID, name="NewGuestName")
        gm = ScriptedGmTransport(scripted_contents=[_fenced_json(guest_drifted)])

        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert not completion_out.success, completion_out
        assert completion_out.missing == ["guest_pk"], completion_out
        assert len(gm.calls) == 1, gm.calls
        # Der alte (ungueltige) Vorkorrektur-Stand bleibt unangetastet --
        # die gedriftete Antwort wurde NICHT uebernommen.
        assert harvested_out["guest_pk"] == guest_old_invalid

        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift", (
            guest_record
        )
        assert not guest_record.get("best_effort")
        assert guest_record.get("best_candidate_block") is None, (
            "ein per Drift abgelehnter Kandidat darf NIE als best-effort-Kandidat gespeichert werden."
        )

        # KEIN Plan/Final -- die Section ist nachweislich nicht abgeschlossen.
        assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None
        assert not store._completion_plan_path(env.run_dir, section_id).exists()
        assert not store._completion_final_path(env.run_dir, section_id).exists()


# ---------------------------------------------------------------------------
# (d) `best_effort=False` (Default) -- Verhalten unveraendert.
# ---------------------------------------------------------------------------

def test_complete_section_best_effort_default_false_keeps_strict_rejection():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-besteffort-d")
        section_id = "section-besteffort-d"

        invalid_leader = _overlong_invalid(_LEADER_CID, name="Leader")
        valid_guest = full_v7_save(_GUEST_CID, name="Guest")
        harvested = {"leader_pk": invalid_leader, "guest_pk": valid_guest}

        # Default (kein `best_effort`-Keyword) -- bytegleich zum
        # Vor-Fix-Verhalten: der schema-ungueltige Leader-Block bleibt
        # `missing`, kein Plan wird gepinnt.
        completion_default = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not completion_default.success
        assert completion_default.missing == ["leader_pk"], completion_default
        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert not plan_path.exists()

        # Explizit `best_effort=False` ist dasselbe wie der Default.
        completion_explicit_false = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store, best_effort=False,
        )
        assert not completion_explicit_false.success
        assert completion_explicit_false.missing == ["leader_pk"], completion_explicit_false
        assert not plan_path.exists()

        # Gegenprobe (derselbe Zustand, jetzt `best_effort=True`): NUR der
        # tatsaechlich schema-fehlerhafte Leader-Block wird toleriert UND
        # ehrlich markiert -- der bereits gueltige Gast-Eintrag bekommt
        # KEINE Markierung.
        completion_best_effort = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store, best_effort=True,
        )
        assert completion_best_effort.success, completion_best_effort
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert plan_data["members"]["leader_pk"].get("best_effort") is True
        assert "best_effort" not in plan_data["members"]["guest_pk"]


# ---------------------------------------------------------------------------
# (e) RECONCILIATION-V2: SAVECOMPAT hat Vorrang -- ein wallet-als-Zahl-
#     Kandidat ist deterministisch SAVECOMPAT-reparierbar und bekommt deshalb
#     KEIN Best-Effort; ein `maxItems`-Ueberlaengen-Kandidat ist das NICHT und
#     bekommt weiterhin Best-Effort (Kontrastprobe, gleiche Konstruktion).
# ---------------------------------------------------------------------------

def _wallet_as_number(cid: str, name: str = "Testfigur", amount: float = 240) -> dict:
    """Sonst gueltiger v7-Save mit einem bloss-zahligen (statt `{"balance":
    ...}`-objektfoermigen) Wallet -- schema-ungueltig, aber ueber die
    bestehende deterministische Wallet-Projektion (`save_compatibility.
    project_wallets_in_block`/`evaluate_with_wallet_projection`, RULE_
    NUMBER_TO_BALANCE) wertgleich reparierbar."""
    block = full_v7_save(cid, name=name)
    block["economy"] = {"wallets": {cid: amount}}
    return block


def test_savecompat_repairable_wallet_candidate_gets_no_best_effort_maxitems_still_does():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-besteffort-e")
        section_id = "section-besteffort-e"

        harvested: dict = {}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        max_attempts = sc.MAX_ADDITIONAL_REQUESTS
        invalid_leader = _wallet_as_number(_LEADER_CID, name="Leader")
        invalid_guest = _wallet_as_number(_GUEST_CID, name="Guest")
        one_response = (
            "Technische Speicherkorrektur (Wallet bleibt bloss-zahlig).\n"
            + _fenced_json(invalid_leader) + "\n" + _fenced_json(invalid_guest)
        )
        gm = ScriptedGmTransport(scripted_contents=[one_response] * max_attempts)

        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        # SAVECOMPAT (deterministische Wallet-Projektion) KOENNTE diesen
        # Kandidaten reparieren -- KEIN Best-Effort, unveraendert terminal.
        assert not completion_out.success, completion_out
        assert set(completion_out.missing) == {"leader_pk", "guest_pk"}, completion_out
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert leader_record["state"] == "validating" and not leader_record.get("best_effort"), leader_record
        assert guest_record["state"] == "validating" and not guest_record.get("best_effort"), guest_record
        # Der best-konforme Kandidat WURDE beobachtet (Tracking laeuft immer)
        # -- nur die Adoption bleibt wegen SAVECOMPAT-Vorrang aus.
        assert leader_record.get("best_candidate_block") == invalid_leader, leader_record
        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert not plan_path.exists(), "SAVECOMPAT-reparierbare Kandidaten bekommen KEINEN best-effort-Plan."

        # Kontrastprobe: identischer Aufbau, aber EIN `maxItems`-
        # Ueberlaengen-Kandidat statt Wallet-als-Zahl -- NICHT savecompat-
        # reparierbar -> best-effort greift weiterhin.
        env2, lobby2, table2, ps_store2 = _build(Path(td) / "contrast", "t-besteffort-e2")
        section_id2 = "section-besteffort-e2"
        harvested2: dict = {}
        harvest_completion2 = store.complete_section(
            lobby2, table2, section_id2, harvested2, env2.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store2,
        )
        overlong_leader = _overlong_invalid(_LEADER_CID, name="Leader")
        overlong_guest = _overlong_invalid(_GUEST_CID, name="Guest")
        one_response2 = (
            "Technische Speicherkorrektur (bleibt ueber-Cap).\n"
            + _fenced_json(overlong_leader) + "\n" + _fenced_json(overlong_guest)
        )
        gm2 = ScriptedGmTransport(scripted_contents=[one_response2] * max_attempts)
        harvested_out2, completion_out2 = sc.pursue_group_save_correction(
            lobby=lobby2, table=table2, section_id=section_id2, harvested=harvested2,
            harvest_completion=harvest_completion2, states_dir=env2.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store2,
            gm_transport=gm2, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_out2.success, completion_out2
        plan_path2 = store._completion_plan_path(env2.run_dir, section_id2)
        assert plan_path2.exists() and json.loads(plan_path2.read_text(encoding="utf-8")).get("best_effort") is True


# ---------------------------------------------------------------------------
# (f) RECONCILIATION-V3: das Prinzip gilt generisch fuer JEDEN Wert-/Form-/
#     Typfehler, NICHT nur fuer Wallet-Faelle -- ein Kandidat mit NUR einem
#     typfalschen Feld (`lvl` als String statt Ganzzahl, KEIN Wallet-Problem,
#     KEIN maxItems) bekommt KEIN Best-Effort; derselbe Aufbau mit einem
#     `maxItems`-Ueberlaengen-Kandidaten bekommt weiterhin Best-Effort.
# ---------------------------------------------------------------------------

def _lvl_type_invalid(cid: str, name: str = "Testfigur") -> dict:
    """Sonst gueltiger v7-Save mit typfalschem `lvl` (String statt
    Ganzzahl) -- KEIN Wallet-Feld (Wallet bleibt ein bereits gueltiges
    leeres Objekt), KEIN `maxItems`/`minItems`-Fehler. Die deterministische
    Wallet-Projektion kann diesen Fehler NICHT beheben -- SAVECOMPATs
    modellgestuetzte Reparaturbruecke (`core.compat_load_service.
    build_compat_repair_fn`) bleibt dafuer zustaendig, NICHT Best-Effort."""
    block = full_v7_save(cid, name=name)
    block["characters"][0]["lvl"] = "2"
    block["economy"] = {"wallets": {}}
    return block


def test_nonwallet_type_error_candidate_gets_no_best_effort_maxitems_still_does():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-besteffort-f")
        section_id = "section-besteffort-f"

        harvested: dict = {}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        max_attempts = sc.MAX_ADDITIONAL_REQUESTS
        invalid_leader = _lvl_type_invalid(_LEADER_CID, name="Leader")
        invalid_guest = _lvl_type_invalid(_GUEST_CID, name="Guest")
        one_response = (
            "Technische Speicherkorrektur (lvl bleibt typfalsch).\n"
            + _fenced_json(invalid_leader) + "\n" + _fenced_json(invalid_guest)
        )
        gm = ScriptedGmTransport(scripted_contents=[one_response] * max_attempts)

        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        # Typfehler ohne maxItems/minItems -- SAVECOMPATs modellgestuetzte
        # Reparaturbruecke bleibt zustaendig, KEIN Best-Effort.
        assert not completion_out.success, completion_out
        assert set(completion_out.missing) == {"leader_pk", "guest_pk"}, completion_out
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record["state"] == "validating" and not leader_record.get("best_effort"), leader_record
        assert leader_record.get("best_candidate_block") == invalid_leader, leader_record
        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert not plan_path.exists(), "Ein reiner Typfehler (kein maxItems) bekommt KEINEN best-effort-Plan."

        # Kontrastprobe: identischer Aufbau, aber `maxItems`-Ueberlaenge
        # statt Typfehler -- best-effort greift weiterhin.
        env2, lobby2, table2, ps_store2 = _build(Path(td) / "contrast", "t-besteffort-f2")
        section_id2 = "section-besteffort-f2"
        harvested2: dict = {}
        harvest_completion2 = store.complete_section(
            lobby2, table2, section_id2, harvested2, env2.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store2,
        )
        overlong_leader = _overlong_invalid(_LEADER_CID, name="Leader")
        overlong_guest = _overlong_invalid(_GUEST_CID, name="Guest")
        one_response2 = (
            "Technische Speicherkorrektur (bleibt ueber-Cap).\n"
            + _fenced_json(overlong_leader) + "\n" + _fenced_json(overlong_guest)
        )
        gm2 = ScriptedGmTransport(scripted_contents=[one_response2] * max_attempts)
        harvested_out2, completion_out2 = sc.pursue_group_save_correction(
            lobby=lobby2, table=table2, section_id=section_id2, harvested=harvested2,
            harvest_completion=harvest_completion2, states_dir=env2.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store2,
            gm_transport=gm2, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_out2.success, completion_out2
        plan_path2 = store._completion_plan_path(env2.run_dir, section_id2)
        assert plan_path2.exists() and json.loads(plan_path2.read_text(encoding="utf-8")).get("best_effort") is True


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
