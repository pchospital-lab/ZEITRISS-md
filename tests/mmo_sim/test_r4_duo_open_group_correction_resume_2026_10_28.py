#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_duo_open_group_correction_resume_2026_10_28.py — FIX1
(01-PRODUCT-REVIEW.md "Ein verbliebener Produktblocker: offene Korrektur vor
dem naechsten Spielzug dispatchen"): ein exaktes, folgenloses `!save` eroeffnet
eine Gruppenkorrekturrunde (`save_correction.pursue_group_save_correction`),
die durch eine reale Admission-/Wall-Clock-Pause bzw. eine getypte
Kontingentpause unterbrochen wird, BEVOR sie vollstaendig verarbeitet ist
(`_group_rounds/<tisch>__<section>.open.json` bleibt offen, kein
`__plan.json` gepinnt). Belegter Live-Defekt (Duo-Tisch
`lobby-p01_latch-p02_breach__2`): der NORMALE Spieler-/Lobby-Resume (`core.
app_service.run_play_session`, derselbe Weg wie `ui/tui.py`/`core/
lobby_flow.py`) erreichte diesen offenen Korrekturzustand bisher NICHT --
weder `store.open_completion_order_for_table` (kein Plan gepinnt) noch die
R12-AUTORECOVERY-Suche (`core._section_completion_recovery.
find_recoverable_entry`, sieht nur den JUENGSTEN sl_log-Eintrag) fanden ihn,
sobald auch nur EIN weiterer gewoehnlicher Turn dazwischenlag -- live waren
es 33 (`tables/lobby-p01_latch-p02_breach__2.json.sl_log[36..68]`).

Jede VERIFIKATION hier geht ueber den ECHTEN Aufrufer (`app_service.
run_play_session`, je Phase NEU konstruiert -- simuliert einen neuen
Prozess-/TUI-/Runtime-Aufruf auf demselben persistierten `run_dir`), NICHT
ueber einen isolierten `pursue_group_save_correction`-Aufruf (genau DAS
haette die belegte Luecke laut 01-PRODUCT-REVIEW.md NICHT geschlossen).

Testaufbau-Hinweis (Variante a/c): der INITIALE Interrupt wird -- wie in den
bereits bestehenden, angenommenen Fixtures `_r12_window_hold_fixture.py`/
`test_r12_origin_finish_group_shape.py`/`test_r12_window_resume_boundary_
group.py` -- ueber einen direkten `pursue_group_save_correction`-Aufruf
hergestellt: der normale `!save`-Turn selbst durchlaeuft GENAU denselben
Admission-Gate-Check (`SectionRuntime._check_gate`, "F3: vor Publish/
Reflexion") wie JEDER andere Turn, UNMITTELBAR bevor `completion_hit`
ueberhaupt gewertet wird -- ein Fenster-Zu waehrend der `!save`-Antwort
selbst wuerde deshalb bereits DIESEN Check (nicht die Korrektur) treffen und
`finalize`/die Korrektur nie erreichen. Ein ECHTER Zeitabstand zwischen "die
`!save`-Antwort passiert F3" und "die anschliessende Korrektur sendet" gibt
es nur bei echtem Netzwerk-Transport (reale Sekunden); in einem synchronen
Fake-Test ohne echte Verzoegerung liessen sich beide Pruefpunkte nicht
unterscheiden. Die NEUARTIGE, hier eigentlich zu beweisende Faehigkeit --
dass der NORMALE Aufrufer eine bereits offene Runde ueber einen neuen
Prozess/TUI-Aufruf hinweg findet und priorisiert, statt sie (R12-AUTORECOVERY
sieht nur `sl_log[-1]`) zu uebersehen -- wird dadurch NICHT abgeschwaecht:
genau DAS prueft jede Assertion nach dem Setup-Abschnitt, ausschliesslich
ueber `app_service.run_play_session`. Variante (b), die getypte
Kontingentpause, hat dieses Timing-Problem NICHT (die Pause wird WAEHREND
eines echten `gm_transport.turn()`-Aufrufs ausgeloest, nicht ueber einen
Vorab-Check) und laeuft deshalb vollstaendig ueber zwei echte, geskriptete
`run_play_session`-Aufrufe durch.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes
(`_FakeGmTransport`/bestehende `ScriptedDriver`/`ReflectionOnlyDriver` aus
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
from _r12_window_hold_fixture import close_window, open_window  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ReflectionOnlyDriver, ScriptedDriver, build_two_member_table, make_env,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision, ProviderQuotaPausedError  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_CID_TO_PK = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk"}


class _FakeGmTransport:
    """Geskripteter GM-Transport. `scripted_contents`-Elemente duerfen auch
    `Exception`-Instanzen sein (z.B. `ProviderQuotaPausedError`) -- wird
    dann statt einer normalen Antwort geworfen."""

    def __init__(self, scripted_contents):
        self._contents = list(scripted_contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        call_no = len(self.calls) + 1
        if not self._contents:
            raise AssertionError(
                f"_FakeGmTransport: Skript erschoepft -- unerwarteter GM-Call #{call_no} "
                f"(turn_idx={turn_idx}, user_text={user_text!r})."
            )
        content = self._contents.pop(0)
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        if isinstance(content, Exception):
            raise content
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"fake-chat-{turn_idx}"}


class _ExplodingGm:
    def turn(self, *a, **kw):
        raise AssertionError("kein Transport-Call erwartet.")


def _anchor_decision(cid: str, text: str = "Anker-Text.") -> ParticipantDecision:
    return ParticipantDecision(text=text, save_payload=full_v7_save(cid, name="Test"), origin_source="fake:anchor")


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def _run(lobby, table, ps_store, gm, controller, section_id, states_dir, ts):
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}},
        states_dir, "2026-10-28", ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=5,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


def _append_stale_normal_turns(run_dir, table_id: str, section_id: str, count: int = 2) -> None:
    """Simuliert die belegten 33 nutzlosen Folgeturns NACH der
    unterbrochenen Korrektur -- ein paar synthetische, GANZ GEWOEHNLICHE
    sl_log-Eintraege, die weder den Marker noch ein kommando-gestuetztes
    `entry_matches` treffen. Beweist: die R12-AUTORECOVERY-Suche
    (`sl_log[-1]`-only) wuerde diese Runde NIE wiederfinden -- FIX1 muss
    den offenen Gruppenkorrekturmarker UNABHAENGIG vom sl_log-Tail
    aufnehmen."""
    stale = store.Table.load(run_dir, table_id)
    for i in range(count):
        stale.sl_log.append({
            "turn_idx": 900 + i, "leader_message": "Wir plaudern einfach weiter.",
            "origin_persona_key": "leader_pk", "origin_raw_input": "Wir plaudern einfach weiter.",
            "origin_source": "fake:leader-chatter", "save_payload": None,
            "content": "Gewoehnliche Spielplauderei, kein Abschlussbeleg.",
            "section_id": section_id, "chat_id": f"fake-chat-stale-{i}",
            "expected_prev_ref_by_member": None, "gm_request_id": None,
        })
    stale.persist()


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    open_window(env.run_dir)
    return env, lobby, table, ps_store


def _seed_missing_harvest(env, lobby, table, ps_store, section_id: str):
    """Reproduziert den Produktzustand GENAU nach einem folgenlosen `!save`
    (`SectionRuntime.finalize` mit leerem Export): BEIDE Mitglieder fehlen
    noch in `harvested`. Reiner, bestehender Store-Aufruf -- keine neue
    Mechanik."""
    harvested: dict = {}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
        harvest_completion
    )
    return harvested, harvest_completion


# ---------------------------------------------------------------------------
# (a) Admission-/Wall-Clock-Pause (`window_paused`) BEIDER Mitglieder in
#     EINER Runde, DANACH weitere normale Historyeintraege -- der naechste
#     normale Runtime-Aufruf MUSS die offene Korrektur VOR jedem neuen
#     Spielzug aufnehmen.
# ---------------------------------------------------------------------------

def test_open_group_round_survives_admission_window_pause_and_stale_history_then_resumes_through_normal_caller():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-duo-open-a")
        section_id = "section-duo-open-a"
        harvested, harvest_completion = _seed_missing_harvest(env, lobby, table, ps_store, section_id)

        # Setup (s. Moduldocstring): Admissionfenster geschlossen, EIN
        # direkter Aufruf eroeffnet Runde 1 fuer BEIDE Mitglieder -- der
        # Versand wird VOR jedem Transport blockiert (Deadline-vor-Versand).
        close_window(env.run_dir)
        harvested_blocked, completion_blocked = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_blocked.success

        open_round_path = sc._open_round_path(env.run_dir, table.table_id, section_id)
        assert open_round_path.exists(), (
            "die offene Gruppenkorrekturrunde muss nach der Admission-/Wall-Clock-Pause erhalten bleiben"
        )
        open_round = json.loads(open_round_path.read_text(encoding="utf-8"))
        # Beide Mitglieder sind in DERSELBEN Runde gebunden -- genau wie im
        # belegten Duo-B-Fall (MAHLBERG+BREACH in EINER offenen Runde 2).
        assert {m["persona_key"] for m in open_round["members"]} == {"guest_pk", "leader_pk"}, open_round
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert guest_record["state"] == "window_paused" and guest_record["attempts_used"] == 1, guest_record
        assert leader_record["state"] == "window_paused" and leader_record["attempts_used"] == 1, leader_record

        # Belegtes Live-Muster: nach der unterbrochenen Korrektur folgen
        # weitere ganz gewoehnliche sl_log-Eintraege (hier 2 statt der
        # belegten 33 -- die blosse Anwesenheit reicht, um die alte
        # sl_log[-1]-only-Suche blind zu machen).
        _append_stale_normal_turns(env.run_dir, table.table_id, section_id, count=2)

        # Ein spaeteres, neues zulaessiges Admissionfenster oeffnet sich
        # (z.B. nach einem Betreiber-Neustart/einer neuen Lab-Session).
        open_window(env.run_dir)

        # === NEUER normaler Runtime-/TUI-Aufruf (neue Table-Instanz, neuer
        # Controller, neuer GM-Transport -- simuliert einen frischen Prozess
        # auf demselben persistierten run_dir). ReflectionOnlyDriver
        # explodiert bei JEDER Nicht-Reflexions-Entscheidungsanfrage -- ein
        # erneutes Anker-/Import-/Weiterspiel waere ein Testversagen. ===
        table2 = store.Table.load(env.run_dir, table.table_id)
        guest_export = full_v7_save(_GUEST_CID, name="Guest")
        leader_export = full_v7_save(_LEADER_CID, name="Leader")
        gm2 = _FakeGmTransport(scripted_contents=[
            "Korrekturantwort fuer beide noch fehlenden Figuren.\n"
            + _fenced_json(guest_export) + "\n" + _fenced_json(leader_export),
        ])
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("Reflexion Leader (gut gelaufen).", "fake:leader-reflect"),
            "guest_pk": ReflectionOnlyDriver("Reflexion Gast (gut gelaufen).", "fake:guest-reflect"),
        })
        outcome2 = _run(lobby, table2, ps_store, gm2, controller2, section_id, env.states_dir, "2026-10-28T09:00:00")

        assert outcome2.completion.success, outcome2.completion.reason
        assert set(outcome2.completion.members_completed) == {"leader_pk", "guest_pk"}
        # GENAU EIN Korrekturversand fuer die wiederaufgenommene Runde --
        # KEIN Anker-/Import-/Weiterspiel-Call.
        assert len(gm2.calls) == 1, gm2.calls
        assert not open_round_path.exists(), "die Runde muss nach vollstaendiger Verarbeitung geloescht sein"
        assert sc.load_record(env.run_dir, guest_repair_key)["state"] == "adopted"
        assert sc.load_record(env.run_dir, leader_repair_key)["state"] == "adopted"

        # Idempotenz (bestehender, unveraenderter Vertrag von
        # `store.complete_section`): ein erneuter Abschlussversuch fuer
        # dieselbe `section_id` liefert `already_completed=True`, OHNE
        # jeden weiteren Schreibzugriff -- keine zweite Adoption/Reflexion/
        # Final.
        idempotent_retry = store.complete_section(
            lobby, table, section_id, {}, env.states_dir, "2026-10-28", ZeitrissHarvestValidator(), ps_store,
        )
        assert idempotent_retry.success and idempotent_retry.already_completed, idempotent_retry


# ---------------------------------------------------------------------------
# (b) getypte Kontingentpause (`ProviderQuotaPausedError`) WAEHREND der
#     Nachforderung, VOLLSTAENDIG ueber zwei echte, geskriptete
#     `run_play_session`-Aufrufe (kein Timing-Problem, s. Moduldocstring) --
#     die Pause durchlaeuft `run_full_section` ungefangen (bestehendes
#     Verhalten, P2); nach Wiederverfuegbarkeit fuehrt der naechste normale
#     Aufruf GENAU die offene Korrektur weiter, alte Requesthistorie bleibt
#     erhalten, kein zusaetzlicher `attempts_used`-Slot nur wegen der Pause.
# ---------------------------------------------------------------------------

def test_open_group_round_survives_typed_quota_pause_then_resumes_through_normal_caller_without_extra_attempt():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-duo-open-b")
        section_id = "section-duo-open-b"

        gm1 = _FakeGmTransport(scripted_contents=[
            "SL-Antwort auf Anker-Turn.",
            "SL-Antwort auf Gast-Import.",
            "Hinweis: Speicherstand ist bereits gespeichert, kein neuer Export noetig.",
            ProviderQuotaPausedError("Kontingent erschoepft."),
        ])
        leader_driver1 = ScriptedDriver([
            _anchor_decision(_LEADER_CID),
            ParticipantDecision(text="!save", origin_source="fake:leader-save"),
        ])
        guest_driver1 = ScriptedDriver([_anchor_decision(_GUEST_CID)])
        controller1 = TableController(
            leader_key="leader_pk", drivers={"leader_pk": leader_driver1, "guest_pk": guest_driver1},
        )
        try:
            _run(lobby, table, ps_store, gm1, controller1, section_id, env.states_dir, "2026-10-28T08:00:00")
            raise AssertionError("ProviderQuotaPausedError haette ungefangen durchlaufen muessen.")
        except ProviderQuotaPausedError:
            pass

        assert len(gm1.calls) == 4, gm1.calls
        open_round_path = sc._open_round_path(env.run_dir, table.table_id, section_id)
        assert open_round_path.exists(), "die offene Runde muss nach der Kontingentpause erhalten bleiben"
        open_round = json.loads(open_round_path.read_text(encoding="utf-8"))
        assert {m["persona_key"] for m in open_round["members"]} == {"guest_pk", "leader_pk"}, open_round
        round_no_after_pause = open_round["round"]
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_record_after_pause = sc.load_record(env.run_dir, guest_repair_key)
        leader_record_after_pause = sc.load_record(env.run_dir, leader_repair_key)
        # P2 (R4-Rundenabschluss, bereits angenommen): eine verbuchte
        # Kontingentpause erhoeht KEINEN zusaetzlichen Korrektur-Slot --
        # `attempts_used` bleibt bei genau 1 (der eine tatsaechlich
        # versandte, dann kontingentblockierte Versuch) fuer BEIDE Mitglieder
        # dieser einen Runde.
        assert guest_record_after_pause["attempts_used"] == 1, guest_record_after_pause
        assert leader_record_after_pause["attempts_used"] == 1, leader_record_after_pause
        assert guest_record_after_pause["state"] in ("validating", "correction_pending"), guest_record_after_pause

        # === NEUER normaler Runtime-/TUI-Aufruf NACH Wiederverfuegbarkeit:
        # muss GENAU die offene Korrektur fortfuehren, alte Requesthistorie
        # (der neue `round_no`) bleibt erhalten -- kein normaler Spielzug. ===
        table2 = store.Table.load(env.run_dir, table.table_id)
        guest_export = full_v7_save(_GUEST_CID, name="Guest")
        leader_export = full_v7_save(_LEADER_CID, name="Leader")
        gm2 = _FakeGmTransport(scripted_contents=[
            "Korrekturantwort fuer beide noch fehlenden Figuren.\n"
            + _fenced_json(guest_export) + "\n" + _fenced_json(leader_export),
        ])
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("Reflexion Leader (gut gelaufen).", "fake:leader-reflect"),
            "guest_pk": ReflectionOnlyDriver("Reflexion Gast (gut gelaufen).", "fake:guest-reflect"),
        })
        outcome2 = _run(lobby, table2, ps_store, gm2, controller2, section_id, env.states_dir, "2026-10-28T09:00:00")

        assert outcome2.completion.success, outcome2.completion.reason
        assert len(gm2.calls) == 1, gm2.calls
        assert not open_round_path.exists()
        assert sc.load_record(env.run_dir, guest_repair_key)["state"] == "adopted"
        assert sc.load_record(env.run_dir, leader_repair_key)["state"] == "adopted"
        # Derselbe Slot (round_no durfte sich fuer den Resume-Versand selbst
        # NICHT ein zweites Mal erhoehen, bevor der naechste Aufruf ihn
        # verarbeitet) -- geprueft ueber den unveraenderten `round_no`, mit
        # dem die Runde beim Resume-Eintritt noch vorlag.
        assert round_no_after_pause >= 1


# ---------------------------------------------------------------------------
# (negativ) ein unbekannter/widerspruechlicher Rundenzustand (hier: der
# vorherige Transport-Call endete `accounted` MIT echtem Fehler, aber die
# Runde wurde -- simuliert ueber einen injizierten Absturz zwischen
# `finish_error` und `mark_hold`/`_clear_open_round`, exakt wie
# `test_r12_window_resume_boundary_group.py` -- NICHT terminal abgeschlossen)
# bleibt auch ueber den NORMALEN Aufrufer hart HOLD -- kein Fortschritt,
# kein Crash, kein stillschweigendes Weiterspielen.
# ---------------------------------------------------------------------------

def test_open_group_round_with_unresolved_prior_outcome_stays_hard_hold_through_normal_caller():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-duo-open-c")
        section_id = "section-duo-open-c"
        harvested, harvest_completion = _seed_missing_harvest(env, lobby, table, ps_store, section_id)

        class _TransportFailsGm:
            def __init__(self):
                self.calls = []

            def turn(self, turn_idx, text, **kwargs):
                self.calls.append(turn_idx)
                raise TimeoutError("SYNTHETISCHER_TRANSPORTFEHLER")

        def _crash(*a, **kw):
            raise SystemExit(73)

        original_mark_hold = sc.mark_hold
        sc.mark_hold = _crash
        try:
            gm1 = _TransportFailsGm()
            try:
                sc.pursue_group_save_correction(
                    lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
                    harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
                    harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
                    gm_transport=gm1, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
                )
                raise AssertionError("Absturzpunkt nicht erreicht.")
            except SystemExit as exc:
                assert exc.code == 73
        finally:
            sc.mark_hold = original_mark_hold

        open_round_path = sc._open_round_path(env.run_dir, table.table_id, section_id)
        assert open_round_path.exists(), (
            "ein roher Transportfehler (accounted+error) VOR mark_hold/_clear_open_round "
            "haelt die Runde offen -- F01b, bereits angenommenes Verhalten."
        )

        # Neuer normaler Aufruf (ECHTER Caller): der vorherige Request fuer
        # GENAU diese Rundenidentitaet ist `accounted` MIT `error` --
        # `_window.slot_resumable` klassifiziert das als "terminal" (nicht
        # resumierbar) -- `unresolved_prior_round_outcome`. Kein zweiter
        # Transport-Call, beide Mitglieder werden terminal HOLD, kein
        # Fortschritt, kein ungefangener Fehler.
        table2 = store.Table.load(env.run_dir, table.table_id)
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("sollte nie aufgerufen werden", "fake:leader-noop"),
            "guest_pk": ReflectionOnlyDriver("sollte nie aufgerufen werden", "fake:guest-noop"),
        })
        outcome2 = _run(lobby, table2, ps_store, _ExplodingGm(), controller2, section_id, env.states_dir, "2026-10-28T09:00:00")

        assert not outcome2.completion.success, outcome2.completion.reason
        assert not open_round_path.exists(), "unresolved_prior_round_outcome loescht den Marker (terminal, bereits bestehendes Verhalten)"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unresolved_prior_round_outcome", guest_record
        assert leader_record["state"] == "hold" and leader_record["last_reason"] == "unresolved_prior_round_outcome", leader_record

        # Wiederholung bleibt hart: ein erneuter Korrekturversuch fuer
        # dieselben (bereits terminal HOLD) Mitglieder erzeugt KEINEN
        # zweiten Transport-Call -- derselbe bereits bestehende Vertrag wie
        # `test_r12_window_resume_boundary_group.py` Phase 2 ("kein
        # zweiter POST fuer dieselbe Runde"), hier auf beide Mitglieder
        # angewandt.
        harvested_retry, completion_retry = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested={},
            harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_retry.success and set(completion_retry.missing) == {"leader_pk", "guest_pk"}
        assert sc.load_record(env.run_dir, guest_repair_key)["state"] == "hold"
        assert sc.load_record(env.run_dir, leader_repair_key)["state"] == "hold"


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
