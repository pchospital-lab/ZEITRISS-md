#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_n2r_group_besteffort_p1_hold_p2_origin_2026_10_29.py --
ZR-N2R-ANSCHLUSS-20261019-R4 (Generalreview e59a, PRODUCT-REVIEW.md §P1/§P2,
02_ANSCHLUSSAUFTRAG.md §A): zwei eng begrenzte Korrekturen am echten
`save_correction.pursue_group_save_correction` (NICHT nur an Helper-
Aufrufen):

  P1 -- ein bereits gesetzter terminaler HOLD (`unjustified_semantic_
  drift`) darf NICHT durch den Best-Effort-Erschoepfungszweig
  ueberschrieben werden, selbst wenn ein FRUEHERER, waehrend der Schleife
  beobachteter `best_candidate_block` existiert. Fall 1 (unten, zwei
  Varianten -- Namens- und Walletbetragsdrift): ein brauchbarer
  ueberlanger Kandidat (Runde 1, unveraendert resendet, KEINE Drift) wird
  gespeichert; die FOLGENDE Antwort (Runde 2) driftet unbegruendet
  (ausserhalb der gemeldeten Fehlerpfade) -> `mark_hold` setzt einen
  terminalen HOLD. Die daraufhin erreichte "keine Kandidaten mehr"-
  Erschoepfungspruefung darf diesen HOLD NICHT mit `best_effort=True`
  uebernehmen -- GENAU das war der Fehler VOR diesem Fix (PRODUCT-
  REVIEW.md §P1, Belegstellen Zeilen 2202-2225/1833/1967-2029 am
  gepruefte Head 42a23837).

  P2 -- der bereits eindeutig gebundene, konfliktfreie Ursprungskandidat
  (die erste GM-Ausgabe VOR jeder Nachbesserung) fehlte bisher komplett in
  der Bestwertspur (`update_best_candidate` wurde nur NACH einer
  empfangenen Korrekturantwort aufgerufen, PRODUCT-REVIEW.md §P2, Zeile
  2224). Fall 2 (unten): der Ursprung ist nach derselben vollstaendigen
  Fehlermetrik BESSER als alle drei Nachbesserungen (4 Strukturfehler
  gegen 17 pro Nachbesserung, campaign:0 -> campaign:{} verliert alle neun
  Pflichtfelder) -- ohne den Fix wuerde der schlechtere Nachbesserungs-
  stand gewinnen. Nach erfolgreichem Best-Effort-Abschluss bestaetigt der
  Test zusaetzlich die BESTEHENDE Wiederaufnahme (ADOPTED-Zurueckspielen):
  Kandidat UND Versuchszaehler bleiben dabei unveraendert erhalten (kein
  Reset).

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes
(`ScriptedGmTransport`/`build_two_member_table` aus
`_section_completion_resume_fixtures.py`), kein realer Transport, keine
echte CLI, keine echte GM-Route. `evaluate(...).structure.total_error_
count` ist ueberall dieselbe Fehlermetrik, die `update_best_candidate`
selbst erwartet (keine abweichende Ad-hoc-Zaehlung)."""
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
    ExplodingGmTransport, ScriptedGmTransport, build_two_member_table, make_env,
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


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    open_window(env.run_dir)
    return env, lobby, table, ps_store


# ---------------------------------------------------------------------------
# Fall 1 (P1, PRODUCT-REVIEW.md §P1): brauchbarer ueberlanger Kandidat,
# DANACH unbegruendete Drift -> terminaler HOLD bleibt mit demselben
# Grund, KEIN neuer Plan/Final/keine Veroeffentlichung. Parametrisiert mit
# Namens- UND Walletbetragsdrift (zwei getrennte Testfunktionen, dieselbe
# Hilfsfunktion).
# ---------------------------------------------------------------------------

def _overlong_with_wallet(cid: str, name: str, wallet_balance: float) -> dict:
    """Sonst gueltiger v7-Save mit sieben `continuity.shared_echoes`
    (maxItems 6, schema-ungueltig, aber sauber extrahierbar) UND einem
    bereits schema-gueltigen `economy.wallets[cid].balance` -- letzteres
    liegt ausserhalb jedes gemeldeten Fehlerpfads (der einzige Fehler ist
    die Echo-Ueberlaenge) und ist deshalb ein scharfer Walletdrift-Hebel
    fuer die zweite Testvariante unten."""
    block = full_v7_save(cid, name=name)
    block.setdefault("continuity", {})
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "shared", "text": f"nicht-leer-{i}"} for i in range(7)
    ]
    block["economy"] = {"wallets": {cid: {"balance": wallet_balance}}}
    return block


def _run_overlong_then_drift_case(tmp_root: Path, table_id: str, section_id: str, drifted_round2: dict) -> None:
    env, lobby, table, ps_store = _build(tmp_root, table_id)

    # Leader ist von Anfang an gueltig (nicht Teil der Korrektur) -- NUR
    # der Gast braucht eine Nachforderung (gleiche Konstruktion wie der
    # bestehende Drifttest, hier UM eine erste, NICHT gedriftete
    # Korrekturrunde mit demselben ueberlangen Kandidaten erweitert --
    # GENAU der Zustand, der den P1-Fehler ueberhaupt erst erreicht, s.
    # PRODUCT-REVIEW.md §P1 Schritt 1-3).
    leader_save = full_v7_save(_LEADER_CID, name="Leader")
    guest_round0 = _overlong_with_wallet(_GUEST_CID, "Guest", 100)
    harvested = {"leader_pk": leader_save, "guest_pk": guest_round0}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

    # Runde 1: derselbe ueberlange Kandidat, UNVERAENDERT resendet -- KEINE
    # Drift (identischer Inhalt), bleibt aber weiterhin schema-ungueltig
    # (Echo-Ueberlaenge) -> `update_best_candidate` speichert ihn.
    guest_round1 = _overlong_with_wallet(_GUEST_CID, "Guest", 100)
    assert guest_round1 == guest_round0
    gm = ScriptedGmTransport(scripted_contents=[
        _fenced_json(guest_round1),
        _fenced_json(drifted_round2),
    ])

    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )

    # BEIDE Runden wurden tatsaechlich versandt (Runde 1 unveraendert
    # akzeptiert-aber-ungueltig, Runde 2 gedriftet) -- die Schleife
    # terminiert NICHT schon nach Runde 1.
    assert len(gm.calls) == 2, gm.calls
    assert not completion_out.success, completion_out
    assert completion_out.missing == ["guest_pk"], completion_out
    # Der zuletzt angenommene (nicht gedriftete) Stand bleibt in
    # `harvested` -- die gedriftete Antwort wurde NICHT uebernommen.
    assert harvested_out["guest_pk"] == guest_round1

    guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
    guest_record = sc.load_record(env.run_dir, guest_repair_key)
    # DER KERNFIX (P1): der terminale HOLD-Zustand und sein Grund sind
    # UNVERAENDERT -- der VORHANDENE `best_candidate_block` (der ueberlange
    # Runde-1-Kandidat) hat ihn NICHT best-effort ueberschrieben.
    assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift", (
        guest_record
    )
    assert not guest_record.get("best_effort"), guest_record
    assert guest_record.get("adopted_block") is None, guest_record
    # Der fruehere Kandidat ist weiterhin getrackt (Tracking selbst lief
    # bereits VOR diesem Fix) -- nur die Adoption bleibt jetzt aus.
    assert guest_record.get("best_candidate_block") == guest_round1, guest_record

    # KEIN neuer Plan/Final/keine Veroeffentlichung -- die Section ist
    # nachweislich NICHT abgeschlossen.
    assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None
    assert not store._completion_plan_path(env.run_dir, section_id).exists()
    assert not store._completion_final_path(env.run_dir, section_id).exists()


def test_overlong_candidate_then_name_drift_keeps_terminal_hold_no_best_effort():
    with tempfile.TemporaryDirectory() as td:
        name_drifted = full_v7_save(_GUEST_CID, name="NewGuestName")
        _run_overlong_then_drift_case(
            Path(td), "t-p1-name-drift", "section-p1-name-drift", name_drifted,
        )


def test_overlong_candidate_then_wallet_amount_drift_keeps_terminal_hold_no_best_effort():
    with tempfile.TemporaryDirectory() as td:
        # Schema-valide Antwort, ABER der Walletbetrag weicht vom
        # urspruenglichen `economy.wallets[cid].balance` ab -- ein Pfad,
        # der NIE gemeldeter Fehlerpfad war (die Echo-Ueberlaenge betraf
        # NUR `continuity.shared_echoes`), also unbegruendete Drift,
        # unabhaengig vom Rest des Blocks (F-WALLET-LOSS/N2L-A-R: ein
        # zahlenmaessig abweichender Walletbetrag ist NIE wertgleich).
        wallet_drifted = full_v7_save(_GUEST_CID, name="Guest")
        wallet_drifted["economy"] = {"wallets": {_GUEST_CID: {"balance": 999}}}
        _run_overlong_then_drift_case(
            Path(td), "t-p1-wallet-drift", "section-p1-wallet-drift", wallet_drifted,
        )


# ---------------------------------------------------------------------------
# Fall 2 (P2, PRODUCT-REVIEW.md §P2): der Ursprung ist nach derselben
# Fehlermetrik BESSER als alle drei Nachbesserungen -> die gewaehlten
# Save-Bytes entsprechen dem Ursprung, NICHT der schlechteren letzten
# Nachbesserung. Danach bestaetigt die bestehende Wiederaufnahme (ADOPTED-
# Zurueckspielen): Kandidat UND Zaehler bleiben erhalten.
# ---------------------------------------------------------------------------

def _origin_campaign_scalar(cid: str, name: str) -> dict:
    """Sonst gueltiger v7-Save mit `campaign: 0` (Skalar statt Objekt,
    TYPFEHLER an GENAU `/campaign`) UND sieben `continuity.shared_echoes`
    (maxItems-UEBERLAENGE) -- vier Strukturfehler insgesamt (je zwei pro
    Schema, tolerant+export). GENAU das PRODUCT-REVIEW.md §P2-Beispiel:
    eine bindbare, konfliktfreie Einzelpersonen-Ausgabe mit einem klar
    gemeldeten (aber NICHT behobenen) `/campaign`-Fehler."""
    block = full_v7_save(cid, name=name)
    block["campaign"] = 0
    block.setdefault("continuity", {})
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "shared", "text": f"nicht-leer-{i}"} for i in range(7)
    ]
    return block


def _worse_campaign_empty_object(cid: str, name: str) -> dict:
    """Ersetzt AUSSCHLIESSLICH `campaign: 0` durch `campaign: {}` (leeres
    Objekt) -- der Exportvalidator verlangt neun Pflichtfelder im
    Kampagnenobjekt, ein leeres Objekt verliert deshalb ALLE neun
    (17 Strukturfehler insgesamt gegen 4 beim Ursprung). `/campaign` bleibt
    exakt der gemeldete Fehlerpfad (ein leeres Objekt erzeugt nach
    `_flatten` KEINEN eigenen Blattpfad) -- KEINE Drift, echte GM-
    Verschlechterung, kein Konstruktfehler des Tests."""
    block = _origin_campaign_scalar(cid, name)
    block["campaign"] = {}
    return block


def test_origin_better_than_all_three_corrections_wins_then_resume_keeps_candidate_and_counter():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-p2-origin-wins")
        section_id = "section-p2-origin-wins"

        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        guest_origin = _origin_campaign_scalar(_GUEST_CID, "Guest")
        harvested = {"leader_pk": leader_save, "guest_pk": guest_origin}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        # Sanity: der Ursprung ist nach DERSELBEN Fehlermetrik
        # (`evaluate(...).structure.total_error_count`) tatsaechlich
        # BESSER als jede Nachbesserung -- sonst waere dieser Test keine
        # scharfe P2-Regression.
        worse = _worse_campaign_empty_object(_GUEST_CID, "Guest")
        origin_errors = domain.evaluate(guest_origin, _GUEST_CID).structure.total_error_count
        worse_errors = domain.evaluate(worse, _GUEST_CID).structure.total_error_count
        assert origin_errors < worse_errors, (origin_errors, worse_errors)

        max_attempts = sc.MAX_ADDITIONAL_REQUESTS
        one_response = "Technische Speicherkorrektur (campaign bleibt leer).\n" + _fenced_json(worse)
        gm = ScriptedGmTransport(scripted_contents=[one_response] * max_attempts)

        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert len(gm.calls) == max_attempts, gm.calls
        # DER KERNFIX (P2): Best-Effort greift (Cap-Ueberlauf bleibt
        # bestehen), UND die gewaehlten Save-Bytes sind der URSPRUNG --
        # NICHT die zuletzt empfangene, schlechtere Nachbesserung.
        assert completion_out.success, completion_out
        assert harvested_out["guest_pk"] == guest_origin, harvested_out["guest_pk"]
        assert harvested_out["guest_pk"] != worse

        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "adopted" and guest_record.get("best_effort") is True, guest_record
        assert guest_record["adopted_block"] == guest_origin, guest_record
        assert guest_record.get("best_candidate_block") == guest_origin, guest_record
        assert guest_record["attempts_used"] == max_attempts

        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert plan_path.exists()
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert plan_data.get("best_effort") is True
        assert plan_data["members"]["guest_pk"].get("best_effort") is True

        # Wiederaufnahme (bestehender ADOPTED-Zurueckspiel-Pfad,
        # `restored_from_adopted` in `pursue_group_save_correction`, Zeilen
        # 1871-1896): simuliert einen Neustart NACH einem Crash GENAU
        # zwischen einem frueheren `mark_adopted` und dem naechsten
        # `store.complete_section`-Aufruf -- auf einem FRISCHEN Tisch/
        # Section (die bereits oben abgeschlossene `section_id` hat jetzt
        # einen gepinnten Plan, der eine zweite Pruefung desselben
        # `complete_section`-Aufrufs idempotent VOR `pursue_group_save_
        # correction` beantworten wuerde -- hier geht es gezielt um
        # DESSEN eigene Wiederaufnahme-Verzweigung, nicht um `store`s
        # bereits an anderer Stelle getestete Plan-Idempotenz). Der
        # Korrekturdatensatz wird deshalb direkt (ohne neuen GM-Umlauf)
        # auf GENAU den Zustand nach einem erfolgreichen P2-Best-Effort-
        # Abschluss gebracht: `attempts_used==max_attempts`,
        # `best_candidate_block`/`best_candidate_error_count` wie vom
        # P2-Fix getrackt, `state=adopted`, `best_effort=True`.
        env3, lobby3, table3, ps_store3 = _build(Path(td) / "resume", "t-p2-origin-wins-resume")
        section_id3 = "section-p2-origin-wins-resume"
        guest_repair_key3 = domain.group_repair_key(table3.table_id, section_id3, _GUEST_CID)
        sc.load_or_init_record(
            env3.run_dir, guest_repair_key3, persona_key="guest_pk", char_id=_GUEST_CID,
            operation_key=sc.ROLE_GROUP, table_id=table3.table_id, section_id=section_id3,
        )
        for _ in range(max_attempts):
            sc.begin_attempt(env3.run_dir, guest_repair_key3)
        sc.update_best_candidate(env3.run_dir, guest_repair_key3, block=guest_origin, error_count=origin_errors)
        sc.mark_adopted(env3.run_dir, guest_repair_key3, adopted_block=guest_origin, best_effort=True)
        record_pre_resume = sc.load_record(env3.run_dir, guest_repair_key3)
        assert record_pre_resume["attempts_used"] == max_attempts
        assert record_pre_resume.get("best_candidate_block") == guest_origin

        leader_save3 = full_v7_save(_LEADER_CID, name="Leader")
        harvested3: dict = {"leader_pk": leader_save3}
        harvest_completion3 = store.complete_section(
            lobby3, table3, section_id3, harvested3, env3.states_dir, "2026-10-28",
            ZeitrissHarvestValidator(), ps_store3,
        )
        assert not harvest_completion3.success and harvest_completion3.missing == ["guest_pk"], harvest_completion3

        never_called_gm = ExplodingGmTransport()
        harvested_resumed_out, completion_resumed_out = sc.pursue_group_save_correction(
            lobby=lobby3, table=table3, section_id=section_id3, harvested=harvested3,
            harvest_completion=harvest_completion3, states_dir=env3.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store3,
            gm_transport=never_called_gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        # KEIN neuer GM-Call -- die Wiederaufnahme spielt den bereits
        # ADOPTED gespeicherten Ursprung zurueck, statt neu zu fragen.
        assert never_called_gm.calls == 0, never_called_gm.calls
        assert completion_resumed_out.success, completion_resumed_out
        assert harvested_resumed_out["guest_pk"] == guest_origin

        guest_record_after_resume = sc.load_record(env3.run_dir, guest_repair_key3)
        # KEIN Counter-Reset, KEIN Kandidatenverlust -- bytegleich zum
        # Stand VOR der Wiederaufnahme.
        assert guest_record_after_resume["attempts_used"] == max_attempts
        assert guest_record_after_resume["adopted_block"] == guest_origin
        assert guest_record_after_resume.get("best_candidate_block") == guest_origin
        assert guest_record_after_resume["state"] == "adopted" and guest_record_after_resume.get("best_effort") is True

        plan_path3 = store._completion_plan_path(env3.run_dir, section_id3)
        assert plan_path3.exists()
        plan_data3 = json.loads(plan_path3.read_text(encoding="utf-8"))
        assert plan_data3.get("best_effort") is True
        assert plan_data3["members"]["guest_pk"].get("best_effort") is True


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
