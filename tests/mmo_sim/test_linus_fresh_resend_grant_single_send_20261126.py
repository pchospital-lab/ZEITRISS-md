#!/usr/bin/env python3
"""
tests/mmo_sim/test_linus_fresh_resend_grant_single_send_20261126.py --
ZR-PLAYTEST-ANSCHLUSS-20261125 (Linus-Fix), G1/U1-Nachzug (PR #3320,
ZEITRISS-ALTAIR-G1-U1-20261126-r1).

Belegter Defekt am Ausgangshead (`6d6b49ae5803863746d3ab09fbca499cd443a8a3`,
historische Gegenprobe `sources/pr3320/evidence/repro_one_authorization.py`):
nach GENAU EINER Freigabe (`authorize_transport_error_fresh_resend`) mit
einer Antwort OHNE persoenlichen Save entstehen ZWEI neue physische
Fake-Transportaufrufe (`observed_new_transport_calls=2`, attempts 1->3)
INNERHALB EINES EINZIGEN regulaeren Folgeaufrufs von `pursue_group_save_
correction` -- die besondere Freigabe setzt nur `state` von `hold` auf
`validating` zurueck, begrenzt aber NICHT, wie oft die bestehende
`while not harvest_completion.success and harvest_completion.missing`-
Schleife denselben, weiterhin fehlenden Kandidaten erneut aufgreift.

G1-Fix (`mmo_sim/core/save_correction.py`): ein neues, durabel an den
Korrekturdatensatz gebundenes Markierungspaar -- `fresh_resend_grant_
pending` (gesetzt von `authorize_transport_error_fresh_resend`) und
`fresh_resend_grant_consumed` (geklappt von `begin_attempt(consume_fresh_
resend_grant=True)`, GENAU beim naechsten physischen Sendeversuch fuer
diesen Datensatz) -- begrenzt die Freigabe auf GENAU EINEN physischen
Versand. Jeder Nicht-Erfolg aus diesem EINEN Versand (weiterhin fehlend,
HQ-Verstoss, nicht akzeptiert) HOLDet den Datensatz jetzt terminal
(`FRESH_RESEND_GRANT_EXHAUSTED_REASON`) statt automatisch erneut
anzufragen. `authorize_transport_error_fresh_resend` lehnt zusaetzlich
JEDEN zweiten Freigabeversuch auf einem bereits verbrauchten Datensatz ab
-- unabhaengig davon, ob der aktuelle `last_reason` erneut mit
`TRANSPORT_ERROR_REASON_PREFIX` beginnt (G1-C: "keine implizite
Neufreigabe").

U1-Fix (`mmo_sim/ui/tui.py:10411-10415`): der Erfolgshinweis nennt jetzt
den tatsaechlichen Fortsetzen-Einstieg (Wortkommando `fortsetzen` bzw.
Menuepunkt Fortsetzen) statt des falschen `'n'`-Shortcuts (Dispatcher
`:12760-12761` fuehrt `n` zu `_cmd_new_or_switch_character`, NICHT zu
`_cmd_menu_fortsetzen`).

Deckt ab (01/02 der Abnahme): G1-A..I + U1-A. Misst AUSSCHLIESSLICH
physische Fake-Transportaufrufe (`len(gm.calls)`) als "physischer
Versand" -- NICHT Freigabeaufrufe, Recordwrites oder Attemptinkremente.
Reine isolierte Fixtures + Fake-/Scripted-Transporte (kein echter Netz-/
Modellaufruf, keine nativen Spieldaten). Pure Python, nur `assert`, echter
Exitcode -- gleiches Muster wie die bestehende Suite."""
from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ExplodingGmTransport, ScriptedGmTransport, build_two_member_table, debrief_with_marker, make_env,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ProviderQuotaPausedError  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

# Reuse des bereits bestehenden, belegten Ausgangsfixtures (kein zweiter
# Fixture-Bausatz fuer denselben historischen Fall, s. Briefing "nutze
# vorhandene Fixtures/Runner-Einbindung analog").
import test_linus_transport_error_no_candidate_fresh_resend_20261125 as _case1  # noqa: E402

_LEADER_CID = _case1._LEADER_CID
_GUEST_CID = _case1._GUEST_CID
_CID_TO_PK = _case1._CID_TO_PK

_NO_SAVE_TEXT = "Kein persoenlicher Save enthalten."


def _setup_one_authorized_grant(root: Path, table_id: str):
    """Baut denselben belegten Ausgangszustand wie Case 1 (Gast komplett
    abwesend, Transport-Timeout -> transport_error-HOLD OHNE Kandidat) UND
    autorisiert GENAU EINE Freigabe darauf -- gemeinsamer Startpunkt fuer
    G1-A..D."""
    env, lobby, table, ps_store = _case1._build(root, table_id)
    leader_save = full_v7_save(_LEADER_CID, name="Leader")
    section_id = f"{table.table_id}-section"
    _case1._run_guest_entirely_missing_with_transport_error(env, lobby, table, ps_store, section_id, leader_save)
    repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
    before = sc.load_record(env.run_dir, repair_key)
    assert before["state"] == sc.STATE_HOLD and before["attempts_used"] == 1
    resumed = sc.authorize_transport_error_fresh_resend(
        env.run_dir, repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
    )
    assert resumed is not None and resumed["state"] == sc.STATE_VALIDATING
    assert resumed.get("fresh_resend_grant_pending") is True, resumed
    assert not resumed.get("fresh_resend_grant_consumed")
    return env, lobby, table, ps_store, section_id, repair_key, leader_save


def _complete_section(lobby, table, section_id, harvested, env, ps_store):
    return store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-11-25",
        ZeitrissHarvestValidator(), ps_store,
    )


def _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm):
    return sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=completion, states_dir=env.states_dir, today="2026-11-25",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )


# ---------------------------------------------------------------------------
# G1-A -- eine Freigabe, Antwort ohne persoenlichen Save: <=1 physischer
# Versand, Abschluss kontrolliert offen, Originalrequest/Verpflichtung
# bleiben erhalten (der belegte Kernfall, historische Gegenprobe gruen).
# ---------------------------------------------------------------------------


def test_g1_a_single_grant_missing_personal_save_caps_at_one_send_and_holds_open():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1a",
        )
        original_requests = {p.name: p.read_bytes() for p in (env.run_dir / "requests").glob("*.json")}
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        gm = ScriptedGmTransport([_NO_SAVE_TEXT] * 3)  # >1 gescriptet -- ein zweiter Call waere sonst stumm, nicht sichtbar falsch

        harvested_out, outcome = _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)

        assert len(gm.calls) == 1, f"hoechstens EIN zusaetzlicher physischer Versand erlaubt: {gm.calls}"
        assert outcome.success is False
        after = sc.load_record(env.run_dir, repair_key)
        assert after["state"] == sc.STATE_HOLD, after
        assert after["last_reason"] == sc.FRESH_RESEND_GRANT_EXHAUSTED_REASON, after
        assert after["attempts_used"] == 2, after  # 1 (Timeout) + 1 (der eine Grant-Versand)
        assert after.get("fresh_resend_grant_consumed") is True
        assert after.get("fresh_resend_grant_pending") is False
        assert after["bound_prev_ref_by_member"] is not None  # Originalvorgang bleibt gebunden
        new_request_names = {
            p.name for p in (env.run_dir / "requests").glob("*.json") if p.name not in original_requests
        }
        assert len(new_request_names) == 1, new_request_names
        for name, data in original_requests.items():
            assert (env.run_dir / "requests" / name).read_bytes() == data, "Originalrequest darf unveraendert bleiben."


# ---------------------------------------------------------------------------
# G1-B -- nach Freigabe sofort geeigneter Save: EIN Versand, reguläre
# Uebernahme/Abschluss funktionieren unveraendert.
# ---------------------------------------------------------------------------


def test_g1_b_single_grant_suitable_save_adopts_with_exactly_one_send():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1b",
        )
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        guest_new = full_v7_save(_GUEST_CID, name="Guest")
        gm = ScriptedGmTransport([debrief_with_marker({"guest": guest_new})])

        harvested_out, outcome = _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)

        assert len(gm.calls) == 1, gm.calls
        assert outcome.success is True, outcome
        assert harvested_out["guest_pk"] == guest_new
        after = sc.load_record(env.run_dir, repair_key)
        assert after["state"] == sc.STATE_ADOPTED, after
        assert after["attempts_used"] == 2, after
        assert after.get("fresh_resend_grant_consumed") is True


# ---------------------------------------------------------------------------
# G1-C -- weiterhin fehlend/ungeeignet: nochmals Fortsetzen + Menue oeffnen
# loest KEINE weitere Sendung aus dem verbrauchten Grant aus, kein
# erfundener Erfolg, keine implizite Neufreigabe.
# ---------------------------------------------------------------------------


def test_g1_c_reopening_menu_and_continuing_after_exhausted_grant_sends_nothing_new():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1c",
        )
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        gm1 = ScriptedGmTransport([_NO_SAVE_TEXT])
        _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm1)
        held = sc.load_record(env.run_dir, repair_key)
        assert held["state"] == sc.STATE_HOLD and held["last_reason"] == sc.FRESH_RESEND_GRANT_EXHAUSTED_REASON

        # "nochmals Menue oeffnen": ein zweiter Freigabeversuch ist wirkungslos
        # (keine implizite Neufreigabe) -- GENAU der vom Core-Guard abgedeckte
        # Fall, unabhaengig davon, dass `last_reason` jetzt NICHT mehr mit
        # `TRANSPORT_ERROR_REASON_PREFIX` beginnt.
        reauth = sc.authorize_transport_error_fresh_resend(
            env.run_dir, repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert reauth is None
        assert sc.load_record(env.run_dir, repair_key) == held, "ein No-op-Freigabeversuch darf NICHT schreiben."

        # "nochmals Fortsetzen": ein regulaerer Folgeaufruf darf den Transport
        # GAR NICHT erreichen (terminal HOLD, kein Kandidat mehr).
        never = ExplodingGmTransport()
        harvested2 = {"leader_pk": leader_save}
        completion2 = _complete_section(lobby, table, section_id, harvested2, env, ps_store)
        _h, outcome2 = _pursue(lobby, table, section_id, harvested2, completion2, env, ps_store, never)
        assert never.calls == 0, "kein automatischer Versand aus einem bereits verbrauchten Grant."
        assert outcome2.success is False
        assert sc.load_record(env.run_dir, repair_key) == held


# ---------------------------------------------------------------------------
# G1-D -- neuer Prozess mit demselben persistenten Testzustand: der Verbrauch
# bleibt wirksam (echter zweiter OS-Prozess, andere PID, frischer
# Interpreterlauf -- kein blosser Objektneubau im selben Prozess).
# ---------------------------------------------------------------------------

_G1D_CHILD_SCRIPT = textwrap.dedent("""
    import json
    import os
    import sys
    sys.path.insert(0, sys.argv[5])
    sys.path.insert(0, os.path.join(sys.argv[5], "tests", "mmo_sim"))
    import mmo_sim.core.save_correction as sc
    import mmo_sim.core.store as store
    from _full_v7_fixture import full_v7_save
    from mmo_sim.core.persona_state import PersonaStateStore
    from mmo_sim.domain.zeitriss import save_correction as domain
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves
    from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy

    run_dir, char_id, table_id, section_id = sys.argv[1:5]
    repair_key = domain.group_repair_key(table_id, section_id, char_id)
    before = sc.load_record(run_dir, repair_key)
    reauthorized = sc.authorize_transport_error_fresh_resend(
        run_dir, repair_key, char_id=char_id, table_id=table_id, section_id=section_id,
    )
    after_reauth = sc.load_record(run_dir, repair_key)

    # Minimales Re-Hydrat (reiner Testcode, kein Produktpfad): Lobby/Tisch/
    # Personastore aus dem bereits persistierten `run_dir` DESSELBEN Laufs
    # wiederherstellen. `Lobby.join`/`create_table_from_offer_log` sind
    # idempotent (Resume des bereits offenen Tisches, s. store.py-Docstring
    # "F5/K12/A6") -- es entsteht hier KEIN neuer Lobby-/Tischzustand.
    _LEADER_CID = "chrono-leader"
    schema_path = os.path.join(os.path.dirname(run_dir), "schema.json")
    states_dir = os.path.join(os.path.dirname(run_dir), "states")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, _derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": _LEADER_CID, "guest_pk": char_id},
    )
    assert table is not None and table.table_id == table_id, (
        "Resume des bestehenden, bereits offenen Tisches erwartet -- kein Neuanlegen."
    )

    class _ExplodingGmTransport:
        \"\"\"Zaehlender UND explodierender Fake-Transport: jeder Aufruf
        waere bereits der belegte Defekt -- die Ausnahme macht eine
        Verletzung im Kindprozess sofort sichtbar statt stumm durchzureichen.\"\"\"

        def __init__(self):
            self.calls = 0

        def turn(self, turn_idx, user_text, **kwargs):
            self.calls += 1
            raise AssertionError(
                "kein neuer physischer Versand erwartet -- der Grant ist bereits verbraucht."
            )

    leader_save = full_v7_save(_LEADER_CID, name="Leader")
    harvested = {"leader_pk": leader_save}
    completion = store.complete_section(
        lobby, table, section_id, harvested, states_dir, "2026-11-25",
        ZeitrissHarvestValidator(), ps_store,
    )
    exploding = _ExplodingGmTransport()
    harvested_out, outcome = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=completion, states_dir=states_dir, today="2026-11-25",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=exploding, cid_to_pk={_LEADER_CID: "leader_pk", char_id: "guest_pk"},
        harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    after_pursue = sc.load_record(run_dir, repair_key)
    print(json.dumps({
        "pid": os.getpid(),
        "before_state": before["state"],
        "before_consumed": bool(before.get("fresh_resend_grant_consumed")),
        "reauthorized_is_none": reauthorized is None,
        "record_unchanged_after_reauth": after_reauth == before,
        "pursue_exploding_calls": exploding.calls,
        "pursue_outcome_success": outcome.success,
        "record_unchanged_after_pursue": after_pursue == before,
        "has_open_round": sc.has_open_group_round(run_dir, table_id, section_id),
    }))
""")


def test_g1_d_new_process_same_persisted_state_grant_consumption_stays_effective():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1d",
        )
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        gm1 = ScriptedGmTransport([_NO_SAVE_TEXT])
        _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm1)
        held_before_child = sc.load_record(env.run_dir, repair_key)
        assert held_before_child["state"] == sc.STATE_HOLD

        child_script = Path(td) / "g1d_child.py"
        child_script.write_text(_G1D_CHILD_SCRIPT, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-B", str(child_script), str(env.run_dir), _GUEST_CID, table.table_id, section_id,
             str(_REPO_ROOT)],
            capture_output=True, text=True, timeout=60,
        )
        assert proc.returncode == 0, f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
        result = json.loads(proc.stdout.strip())
        assert result["before_state"] == "hold"
        assert result["before_consumed"] is True
        assert result["reauthorized_is_none"] is True, "ein echter zweiter Prozess darf den Grant nicht erneuern."
        assert result["record_unchanged_after_reauth"] is True
        # Der ECHTE gebundene Korrektur-/Fortsetzenpfad (`pursue_group_save_
        # correction`) laeuft im echten zweiten Prozess mit einem
        # zaehlenden/explodierenden Fake-Transport -- GAR KEIN physischer
        # Versand, Zustand bleibt terminal HOLD (G1-KONFLIKT-Nachzug, Beleg
        # des bisher nur indirekt (ueber die Freigabe allein) gepruefte
        # Pfad).
        assert result["pursue_exploding_calls"] == 0, (
            "der echte Korrekturcaller darf im zweiten Prozess GAR KEINEN physischen Versand ausloesen."
        )
        assert result["pursue_outcome_success"] is False
        assert result["record_unchanged_after_pursue"] is True
        assert result["has_open_round"] is False, "kein dauerhaft offener Rundenmarker nach dem verbrauchten Grant."
        assert isinstance(result["pid"], int) and result["pid"] != os.getpid(), (
            "echte Prozessidentitaet (os.getpid() im Kind), nicht nur der Scriptpfad -- "
            "und verschieden von der Eltern-PID."
        )

        # Der Elternprozess sieht denselben, unveraenderten Datensatz wieder.
        assert sc.load_record(env.run_dir, repair_key) == held_before_child


# ---------------------------------------------------------------------------
# G1-E -- Antwort dauerhaft vorhanden, Verarbeitung/Checkpoint ausstehend:
# vorhandene Antwort ohne neuen physischen Versand verwerten; Identitaet/
# Adoption/Abschluss bleiben nutzbar. Simuliert den Crash GENAU zwischen
# durabler Antwortannahme (`send_correction_turn`s `finish_received`) und
# der Verarbeitung in `pursue_group_save_correction`, indem `send_
# correction_turn` fuer GENAU einen Aufruf transparent durchgereicht, aber
# danach (nach der durablen Persistenz) ein simulierter Absturz ausgeloest
# wird -- derselbe reale Produktpfad (`request_ledger.find_durable_result`),
# kein Sonder-Testcode im Produkt.
# ---------------------------------------------------------------------------


def test_g1_e_durable_response_is_reused_without_a_second_physical_send():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1e",
        )
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        guest_new = full_v7_save(_GUEST_CID, name="Guest")
        gm = ScriptedGmTransport([debrief_with_marker({"guest": guest_new})])

        original_send = sc.send_correction_turn

        def _crash_right_after_durable_receive(*args, **kwargs):
            outcome = original_send(*args, **kwargs)
            raise RuntimeError("simulated crash: durably received, NOT yet checkpointed")

        sc.send_correction_turn = _crash_right_after_durable_receive
        try:
            try:
                _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)
                raise AssertionError("der simulierte Absturz haette propagieren muessen.")
            except RuntimeError as exc:
                assert "simulated crash" in str(exc)
        finally:
            sc.send_correction_turn = original_send

        assert len(gm.calls) == 1, "die durable Antwort entstand ueber GENAU den einen physischen Versand."
        # Direkt NACH dem Absturz ist der Datensatz NOCH NICHT auf `adopted`
        # checkpointed -- genau die Luecke, die `find_durable_result` schliesst.
        mid_crash = sc.load_record(env.run_dir, repair_key)
        assert mid_crash["state"] != sc.STATE_ADOPTED

        never = ExplodingGmTransport()
        harvested2 = {"leader_pk": leader_save}
        completion2 = _complete_section(lobby, table, section_id, harvested2, env, ps_store)
        harvested_out2, outcome2 = _pursue(lobby, table, section_id, harvested2, completion2, env, ps_store, never)

        assert never.calls == 0, "Resume nach durablem Empfang darf GAR KEINEN neuen Transport-Call ausloesen."
        assert outcome2.success is True, outcome2
        assert harvested_out2["guest_pk"] == guest_new
        after = sc.load_record(env.run_dir, repair_key)
        assert after["state"] == sc.STATE_ADOPTED, after


# ---------------------------------------------------------------------------
# G1-F -- engere Admission-/Budgetgrenze (hier: `quota_paused`) an der vom
# Grant gebundenen Sendestelle: bestehende Stopwirkung bleibt (Exception
# propagiert weiterhin); derselbe verbrauchte Grant wird durch die neue
# `round_no` NICHT wieder sendefaehig.
# ---------------------------------------------------------------------------


class _QuotaPausedOnceGmTransport:
    """Wirft beim ERSTEN Aufruf eine getypte Kontingentpause (wie ein
    echter Provider-Budget-Stop); jeder WEITERE Aufruf waere ein Testfehler
    (hier soll nach dem verbrauchten Grant GAR KEIN zweiter Call mehr
    passieren)."""

    def __init__(self):
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        raise ProviderQuotaPausedError("Kontingent erschoepft (Testfixture).")


def test_g1_f_quota_paused_on_the_granted_send_keeps_stop_and_does_not_rearm_via_new_round_no():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1f",
        )
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        gm = _QuotaPausedOnceGmTransport()

        try:
            _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)
            raise AssertionError("ProviderQuotaPausedError haette propagieren muessen (bestehende Stopwirkung).")
        except ProviderQuotaPausedError:
            pass

        assert len(gm.calls) == 1, "die Kontingentpause selbst ist bereits der eine verbrauchte physische Versuch."
        after = sc.load_record(env.run_dir, repair_key)
        assert after["state"] == sc.STATE_HOLD, after
        assert after["last_reason"] == sc.FRESH_RESEND_GRANT_EXHAUSTED_REASON, after
        assert after.get("fresh_resend_grant_consumed") is True
        assert sc.has_open_group_round(env.run_dir, table.table_id, section_id) is False, (
            "kein dauerhaft offener Rundenmarker mehr fuer einen bereits terminal gehaltenen Grant-Kandidaten."
        )

        # Ein regulaerer Folgeaufruf (die Kontingentpause ist "vorbei") darf
        # GAR KEINEN zweiten physischen Versand mehr ausloesen -- derselbe
        # verbrauchte Grant wurde durch die zwischenzeitliche neue `round_no`
        # NICHT wieder sendefaehig.
        never = ExplodingGmTransport()
        harvested2 = {"leader_pk": leader_save}
        completion2 = _complete_section(lobby, table, section_id, harvested2, env, ps_store)
        _h, outcome2 = _pursue(lobby, table, section_id, harvested2, completion2, env, ps_store, never)
        assert never.calls == 0, never.calls
        assert outcome2.success is False


# ---------------------------------------------------------------------------
# G1-G -- Nein/Zurueck, bereits adoptiertes fremdes Mitglied: kein
# unerlaubter Grant/Versand; bestehende Guards bleiben unveraendert wirksam
# (gezielte Wiederverwendung der bestehenden Guard-Faelle, keine neue
# Vollkampagne).
# ---------------------------------------------------------------------------


class _FakeTuiSessionForMenu:
    def __init__(self, run_dir: Path, answers: list):
        self.run_dir = run_dir
        self._answers = list(answers)
        self.printed: list[str] = []

    def _print(self, text: str) -> None:
        self.printed.append(text)

    def _readline_with_controls(self, prompt: str, *, context: str):
        if not self._answers:
            raise AssertionError("keine weitere Antwort gecannt.")
        return self._answers.pop(0)


def _snapshot(run_dir: Path) -> dict:
    return {str(p.relative_to(run_dir)): p.read_bytes() for p in sorted(run_dir.rglob("*")) if p.is_file()}


def test_g1_g_explicit_no_and_foreign_adopted_member_cause_no_grant_or_send():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _case1._build(Path(td), "t-g1g")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = f"{table.table_id}-section"
        _case1._run_guest_entirely_missing_with_transport_error(env, lobby, table, ps_store, section_id, leader_save)
        repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)

        # 'nein' am bedienbaren Menueweg: byte-identischer Run, kein Write.
        before = _snapshot(env.run_dir)
        fake = _FakeTuiSessionForMenu(env.run_dir, answers=[("n", None)])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])
        assert _snapshot(env.run_dir) == before
        assert sc.load_record(env.run_dir, repair_key)["state"] == sc.STATE_HOLD
        assert "fresh_resend_grant_pending" not in sc.load_record(env.run_dir, repair_key)

        # bereits adoptiertes fremdes Mitglied: die Freigabe fuer den Gast
        # darf diesen fremden, bereits abgeschlossenen Datensatz nicht anfassen.
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, leader_repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        leader_adopted = sc.mark_adopted(env.run_dir, leader_repair_key, adopted_block=leader_save)

        sc.authorize_transport_error_fresh_resend(
            env.run_dir, repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert sc.load_record(env.run_dir, leader_repair_key) == leader_adopted, (
            "die Freigabe fuer das Gast-Mitglied darf den fremden, bereits adoptierten Leader-Datensatz nicht anfassen."
        )

        # Ein bereits adoptiertes Mitglied selbst lehnt eine Freigabe ab.
        self_reauth = sc.authorize_transport_error_fresh_resend(
            env.run_dir, leader_repair_key, char_id=_LEADER_CID, table_id=table.table_id, section_id=section_id,
        )
        assert self_reauth is None


# ---------------------------------------------------------------------------
# G1-H -- ein bestaetigter Gruppenentscheid, ZWEI fehlende Mitglieder,
# adoptierter Host: der gemeinsam gebundene Versand bleibt insgesamt
# hoechstens einmal, auch bei nur teilweise geeigneter Antwort kein
# Zusatzversand aus demselben Grant; Hostzustand unveraendert.
# ---------------------------------------------------------------------------

_HOST_PK, _MISS1_PK, _MISS2_PK = "leader_pk", "marek_pk", "dronov_pk"
_HOST_CID, _MISS1_CID, _MISS2_CID = "chrono-leader", "chrono-marek", "chrono-dronov"
_G1H_CID_TO_PK = {_HOST_CID: _HOST_PK, _MISS1_CID: _MISS1_PK, _MISS2_CID: _MISS2_PK}
_G1H_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _build_three_member_table(root: Path, table_id: str):
    env = make_env(root)
    schema_path = env.run_dir.parent / "schema.json"
    schema_path.write_text(_G1H_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    for pk, char_id in ((_HOST_PK, _HOST_CID), (_MISS1_PK, _MISS1_CID), (_MISS2_PK, _MISS2_CID)):
        ps_store.save_state(pk, {
            "v": 2, "persona_key": pk, "rounds_played": 0,
            "plays_char": {"character_id": char_id, "name": "Testfigur"},
        }, states_dir=env.states_dir)
    write_test_profile(env.run_dir)
    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for pk in (_HOST_PK, _MISS1_PK, _MISS2_PK):
        lobby.join(pk)
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": _HOST_PK, "wants": [_MISS1_PK, _MISS2_PK]},
            {"type": "consent", "offer_id": "o1", "from": _MISS1_PK, "accept": True},
            {"type": "consent", "offer_id": "o1", "from": _MISS2_PK, "accept": True},
        ],
        chrononaut_ids={_HOST_PK: _HOST_CID, _MISS1_PK: _MISS1_CID, _MISS2_PK: _MISS2_CID},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return env, lobby, table, ps_store


def test_g1_h_two_members_granted_together_share_exactly_one_physical_send_host_untouched():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_three_member_table(Path(td), "t-g1h")
        host_save = full_v7_save(_HOST_CID, name="Host")

        # Fremder, bereits adoptierter Hostdatensatz (Palimpsest-Analogon) --
        # entsteht NICHT durch diesen Grant-Fluss, muss unberuehrt bleiben.
        host_repair_key = domain.group_repair_key(table.table_id, f"{table.table_id}-section", _HOST_CID)
        section_id = f"{table.table_id}-section"
        sc.load_or_init_record(
            env.run_dir, host_repair_key, persona_key=_HOST_PK, char_id=_HOST_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        host_adopted = sc.mark_adopted(env.run_dir, host_repair_key, adopted_block=host_save)

        # Beide Gaeste fehlen von Anfang an komplett -> ein Transport-Timeout
        # setzt beide auf transport_error-HOLD ohne Kandidat (derselbe belegte
        # Ausgangsfall wie Case 1, hier fuer zwei Mitglieder gleichzeitig).
        harvested0 = {"leader_pk": host_save}
        completion0 = _complete_section(lobby, table, section_id, harvested0, env, ps_store)
        assert not completion0.success and sorted(completion0.missing) == sorted([_MISS1_PK, _MISS2_PK])
        gm0 = _case1.RaisingGmTransport()
        try:
            sc.pursue_group_save_correction(
                lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested0),
                harvest_completion=completion0, states_dir=env.states_dir, today="2026-11-25",
                harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
                gm_transport=gm0, cid_to_pk=_G1H_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            )
        except Exception:
            pass  # RaisingGmTransport wirft TimeoutError, das Produkt faengt das intern (mark_hold) -- nur hier defensiv.
        miss1_key = domain.group_repair_key(table.table_id, section_id, _MISS1_CID)
        miss2_key = domain.group_repair_key(table.table_id, section_id, _MISS2_CID)
        for key in (miss1_key, miss2_key):
            rec = sc.load_record(env.run_dir, key)
            assert rec["state"] == sc.STATE_HOLD and rec["last_reason"].startswith(sc.TRANSPORT_ERROR_REASON_PREFIX)
            assert rec.get("best_candidate_block") is None

        # EIN bestaetigter Gruppenentscheid -> beide Gaeste gemeinsam freigeben.
        for key, cid in ((miss1_key, _MISS1_CID), (miss2_key, _MISS2_CID)):
            resumed = sc.authorize_transport_error_fresh_resend(
                env.run_dir, key, char_id=cid, table_id=table.table_id, section_id=section_id,
            )
            assert resumed is not None and resumed["state"] == sc.STATE_VALIDATING

        # Nur EINER der beiden liefert diesmal einen gueltigen persoenlichen
        # Save -- der andere bleibt weiterhin ohne (teilweise geeignete Antwort).
        miss1_new = full_v7_save(_MISS1_CID, name="Marek")
        harvested1 = {"leader_pk": host_save}
        completion1 = _complete_section(lobby, table, section_id, harvested1, env, ps_store)
        gm1 = ScriptedGmTransport([debrief_with_marker({"marek": miss1_new})])
        harvested_out1, outcome1 = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested1),
            harvest_completion=completion1, states_dir=env.states_dir, today="2026-11-25",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm1, cid_to_pk=_G1H_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert len(gm1.calls) == 1, (
            f"der gemeinsam gebundene Versand fuer beide freigegebenen Mitglieder bleibt insgesamt EINMAL: {gm1.calls}"
        )
        assert outcome1.success is False  # miss2_pk bleibt fehlend -> Abschluss weiterhin offen
        miss1_after = sc.load_record(env.run_dir, miss1_key)
        assert miss1_after["state"] == sc.STATE_ADOPTED, miss1_after
        miss2_after = sc.load_record(env.run_dir, miss2_key)
        assert miss2_after["state"] == sc.STATE_HOLD, miss2_after
        assert miss2_after["last_reason"] == sc.FRESH_RESEND_GRANT_EXHAUSTED_REASON, miss2_after

        # Host bleibt wirklich unberuehrt.
        assert sc.load_record(env.run_dir, host_repair_key) == host_adopted

        # Kein Zusatzversand aus demselben Grant, selbst bei nochmaligem Versuch.
        never = ExplodingGmTransport()
        harvested2 = {"leader_pk": host_save}
        completion2 = _complete_section(lobby, table, section_id, harvested2, env, ps_store)
        sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested2),
            harvest_completion=completion2, states_dir=env.states_dir, today="2026-11-25",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=never, cid_to_pk=_G1H_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert never.calls == 0


# ---------------------------------------------------------------------------
# G1-I -- reguläre Korrektur OHNE besonderen Grant: das normale
# Korrekturbudget bleibt ueber MEHRERE Versuche nutzbar -- keine globale
# Ein-Versuch-Kappe (der Fix betrifft AUSSCHLIESSLICH `fresh_resend_grant`-
# gebundene Kandidaten).
# ---------------------------------------------------------------------------


def test_g1_i_regular_correction_without_any_grant_keeps_normal_multi_attempt_budget():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-g1i")
        write_test_profile(env.run_dir)
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = f"{table.table_id}-section"
        repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)

        # Ohne jeden Grant laeuft die bestehende `while`-Schleife innerhalb
        # EINES Aufrufs automatisch ueber das VOLLE Korrekturbudget, solange
        # der GM keinen gueltigen persoenlichen Save liefert -- das ist das
        # bereits bestehende, unveraenderte Normalverhalten (01_AUFTRAG_
        # SAVEGATE.md §B/§C), KEINE neue Ein-Versuch-Kappe durch diesen Fix.
        guest_new = full_v7_save(_GUEST_CID, name="Guest")
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        gm = ScriptedGmTransport([_NO_SAVE_TEXT, _NO_SAVE_TEXT, debrief_with_marker({"guest": guest_new})])

        harvested_out, outcome = _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)

        assert len(gm.calls) == 3, (
            f"ohne Grant bleibt das volle normale Korrekturbudget (MAX_ADDITIONAL_REQUESTS=3) nutzbar -- "
            f"keine globale Ein-Versuch-Kappe durch den G1-Fix: {gm.calls}"
        )
        assert outcome.success is True, outcome
        assert harvested_out["guest_pk"] == guest_new
        rec = sc.load_record(env.run_dir, repair_key)
        assert rec["state"] == sc.STATE_ADOPTED and rec["attempts_used"] == 3, rec
        assert not rec.get("fresh_resend_grant_consumed")


# ---------------------------------------------------------------------------
# G1-KONFLIKT -- eine Freigabe, Antwort mit ZWEI widersprechenden Rohbloecken
# fuer GENAU diese char_id (gleiche save_id, abweichender Inhalt): derselbe
# Einmalvertrag wie bei "weiterhin fehlend"/HQ-Verstoss/nicht akzeptiert --
# hoechstens EIN physischer Versand, terminaler HOLD, KEIN Save still
# adoptiert/geharvestet (ZEITRISS-ALTAIR-G1-KONFLIKT-NACHZUG-20261126-r1,
# Vorbild `tools/repro_g1_conflicting_saves.py`).
# ---------------------------------------------------------------------------


def test_g1_conflicting_saves_single_authorized_send_holds_without_second_transport():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store, section_id, repair_key, leader_save = _setup_one_authorized_grant(
            Path(td), "t-g1konflikt",
        )
        before = sc.load_record(env.run_dir, repair_key)
        original_requests = {p.name: p.read_bytes() for p in (env.run_dir / "requests").glob("*.json")}
        harvested = {"leader_pk": leader_save}
        completion = _complete_section(lobby, table, section_id, harvested, env, ps_store)
        response = debrief_with_marker({
            "first": full_v7_save(_GUEST_CID, wallet=0),
            "conflicting": full_v7_save(_GUEST_CID, wallet=1),
        })
        blocks = zeitriss_saves.extract_all_saves_raw(response)
        conflicts = domain.find_duplicate_save_ids(blocks)
        assert len(blocks) == 2 and conflicts, (
            "Vorbedingung: zwei widersprechende Rohbloecke mit gleicher save_id/char_id."
        )
        gm = ScriptedGmTransport([response, _NO_SAVE_TEXT, _NO_SAVE_TEXT])  # >1 gescriptet -- ein zweiter Call waere sonst stumm, nicht sichtbar falsch

        harvested_out, outcome = _pursue(lobby, table, section_id, harvested, completion, env, ps_store, gm)

        assert len(gm.calls) == 1, f"hoechstens EIN physischer Versand aus dem einen autorisierten Grant erlaubt: {gm.calls}"
        assert outcome.success is False
        after = sc.load_record(env.run_dir, repair_key)
        assert after["state"] == sc.STATE_HOLD, after
        assert after["last_reason"] == sc.FRESH_RESEND_GRANT_EXHAUSTED_REASON, after
        assert after["attempts_used"] == 2, after  # 1 (Timeout) + 1 (der eine Grant-Versand), NICHT 1->3
        assert after.get("fresh_resend_grant_consumed") is True
        assert after.get("fresh_resend_grant_pending") is False
        assert after["bound_prev_ref_by_member"] == before["bound_prev_ref_by_member"], (
            "Originalvorgang bleibt gebunden -- unveraendert gegenueber dem Stand vor dem Konfliktversand."
        )
        assert "guest_pk" not in harvested_out, (
            "keiner der widersprechenden Rohbloecke darf still adoptiert/geharvestet werden."
        )
        new_request_names = {
            p.name for p in (env.run_dir / "requests").glob("*.json") if p.name not in original_requests
        }
        assert len(new_request_names) == 1, new_request_names
        for name, data in original_requests.items():
            assert (env.run_dir / "requests" / name).read_bytes() == data, "Originalrequest darf unveraendert bleiben."


# ---------------------------------------------------------------------------
# U1-A -- neuer Erfolgshinweis + echter Dispatcher: der sichtbare Hinweis
# nennt den vorhandenen Fortsetzen-Einstieg, NIEMALS `n` dafuer; keine
# fremde Menueaenderung.
# ---------------------------------------------------------------------------


def test_u1_a_success_hint_names_real_resume_entry_never_n():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _case1._build(Path(td), "t-u1a")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = f"{table.table_id}-section"
        _case1._run_guest_entirely_missing_with_transport_error(env, lobby, table, ps_store, section_id, leader_save)

        fake = _FakeTuiSessionForMenu(env.run_dir, answers=[("j", None)])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])

        success_lines = [line for line in fake.printed if "autorisiert" in line]
        assert len(success_lines) == 1, fake.printed
        hint = success_lines[0]
        assert "'n'" not in hint and "[fortsetzen]" not in hint, (
            f"der Hinweis darf NICHT mehr den falschen 'n'-Shortcut nennen: {hint!r}"
        )
        assert "fortsetzen" in hint.lower(), f"der Hinweis muss den tatsaechlichen Fortsetzen-Einstieg nennen: {hint!r}"

        # Gegen den ECHTEN, unveraenderten Dispatcher pruefen (keine
        # hartcodierte Annahme): 'n' fuehrt zur Figurenwahl, NICHT zu
        # Fortsetzen; 'fortsetzen'/'resume' fuehren zu `_cmd_menu_fortsetzen`.
        dispatcher_source = Path(inspect.getsourcefile(TuiSession)).read_text(encoding="utf-8")
        assert 'if choice == "n":\n                    self._cmd_new_or_switch_character()' in dispatcher_source
        assert (
            'elif choice in ("fortsetzen", "resume"):\n                    self._cmd_menu_fortsetzen()'
            in dispatcher_source
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
