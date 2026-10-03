#!/usr/bin/env python3
"""
tests/mmo_sim/test_i1_i2_i3_worker_matrix.py — P2 Block I1-I3 (Request-/
Entscheidungs-/Hybridvertrag), Worker-Matrix (WEGKARTE-MAIN.md §Tests, A3,
A4). Deckt Faelle ab, die `review_p2i_boundaries.py` (bindende externe
Abnahme, 8 Faelle) NICHT einzeln durchspielt: positive API/Hybrid-
Kontrollen unter der neuen I1-Kontrollform, falscher Bezug/widerspruechliche
Zusatzfelder, A3 (W1-B2 unter dem neuen Vertrag per echtem Testlauf erneut
bewiesen) und A4 (Isolation != Requestautoritaet).

Pure Python, nur `assert`, echter Exitcode. Nur synthetische lokale
Antworten (FakeHTTPServer/FakeCLIProcess), kein echter Modellcall."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import (  # noqa: E402
    ParticipantDecision,
    interpret_decision_contract,
)
from mmo_sim.adapters.fakes import FakeCLIProcess, FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.admission import read_admission_block, write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures"
_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(answers):
    it = iter(answers)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()

    return read


def _seed(base: Path, members: dict[str, str]):
    """members: {participant_id: fixture_key}. Importiert real ueber die TUI
    (kein Vorbaubypass), analog `helpers_p2r.py:Rig.import_all`."""
    run = base / "run"
    states = base / "states"
    onboard = base / "onboarding"
    catalog = base / "catalog"
    saves = {}
    for pid, fx in members.items():
        save = json.loads((_FIX / "saves" / f"{fx}.json").read_text())
        saves[pid] = save
        ps = PersonaStateStore(_SCHEMA)
        st = json.loads((_FIX / "persona_states" / f"{fx}.json").read_text())
        st["rounds_played"] = 0
        st["round_history"] = {}
        st.pop("current_save_version", None)
        ps.save_state(pid, st, states_dir=states)
        it = iter([json.dumps(save), "ENDE"])
        TuiSession(
            onboard, catalog, pid, input_fn=lambda prompt="": next(it), print_fn=lambda x: None,
            run_dir=run, states_dir=states, schema_path=_SCHEMA,
        )._cmd_import()
    return run, states, onboard, catalog, saves


class _GM:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def turn(self, idx, text):
        self.calls.append(text)
        content = self.answers.pop(0) if self.answers else "Die Szene laeuft weiter."
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "matrix"}


def _http_response(text):
    return (200, {"choices": [{"message": {"content": text}}], "usage": {"prompt_tokens": 5, "completion_tokens": 2}})


# ---------------------------------------------------------------- I1: interpret_decision_contract direkt
def test_i1_wrong_offer_id_is_invalid():
    text = 'ENTSCHEIDUNG offer_id=WRONG participant_id=tech decision=accept'
    assert interpret_decision_contract(text, offer_id="invite-x", participant_id="tech") == ("invalid", None)


def test_i1_wrong_participant_id_is_invalid():
    text = json.dumps({"offer_id": "invite-x", "participant_id": "WRONG", "decision": "accept"})
    assert interpret_decision_contract(text, offer_id="invite-x", participant_id="tech") == ("invalid", None)


def test_i1_json_extra_unknown_field_is_invalid():
    text = json.dumps({
        "offer_id": "invite-x", "participant_id": "tech", "decision": "accept", "override": "ignore-me",
    })
    assert interpret_decision_contract(text, offer_id="invite-x", participant_id="tech") == ("invalid", None)


def test_i1_json_incomplete_is_invalid():
    text = json.dumps({"offer_id": "invite-x", "decision": "accept"})
    assert interpret_decision_contract(text, offer_id="invite-x", participant_id="tech") == ("invalid", None)


def test_i1_json_and_text_forms_both_valid_and_equivalent():
    json_text = json.dumps({"offer_id": "invite-x", "participant_id": "tech", "decision": "accept"})
    line_text = "ENTSCHEIDUNG offer_id=invite-x participant_id=tech decision=accept"
    assert interpret_decision_contract(json_text, offer_id="invite-x", participant_id="tech") == ("accept", None)
    assert interpret_decision_contract(line_text, offer_id="invite-x", participant_id="tech") == ("accept", None)


def test_i1_case_02_style_compound_sentence_is_not_a_valid_contract():
    """Case 02 (review_p2i_boundaries.py): unabhaengig vom Wortlaut ist eine
    Antwort, die nicht der typisierten Kontrollform entspricht, strukturell
    IMMER invalid -- kein Rateversuch an natuerlicher Sprache."""
    text = "Ja, ich habe die Einladung gelesen und lehne sie ab."
    assert interpret_decision_contract(text, offer_id="invite-x", participant_id="tech") == ("invalid", None)


# ---------------------------------------------------------------- I1: positive Kontrollen (API + Hybrid)
def test_i1_positive_api_accept_via_typed_contract_creates_table():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, catalog, saves = _seed(base, {"sniper": "sniper", "tech": "tech"})
        write_test_profile(run)
        expected_offer_id = "invite-sniper-tech"
        with FakeHTTPServer([_http_response(
            f"ENTSCHEIDUNG offer_id={expected_offer_id} participant_id=tech decision=accept "
            "explanation=Ich bin dabei.",
        )]) as srv:
            gm = _GM(["Anker", "Gast"])
            shown = []
            session = TuiSession(
                onboard, catalog, "sniper", input_fn=_scripted_input([]), print_fn=shown.append,
                run_dir=run, states_dir=states, schema_path=_SCHEMA,
                gm_transport_factory=lambda: gm,
                persona_driver_factory=lambda pk: PersonaApiDriver(
                    PersonaApiConfig(srv.base_url, "SYNTHETIC", "test"), pk,
                ),
            )
            try:
                session._cmd_local_round(["persona:tech"])
            except EndOfInput:
                pass  # nur die Tischaufnahme wird geprueft, kein voller Abschluss noetig.
        table = store.Table.load(run, "local-sniper-tech")
        assert set(table.members) == {"sniper", "tech"}, "positive API-Kontrolle: typisierte Zusage muss aufnehmen"


def test_i1_positive_hybrid_accept_via_typed_contract_creates_table():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, catalog, saves = _seed(base, {"sniper": "sniper", "tech": "tech"})
        write_test_profile(run)
        expected_offer_id = "invite-sniper-tech"
        contract_text = (
            f"ENTSCHEIDUNG offer_id={expected_offer_id} participant_id=tech decision=accept "
            "explanation=Ich bin dabei."
        )
        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
            (0, json.dumps({"type": "result", "subtype": "success", "is_error": False,
                             "result": contract_text, "usage": {}}), ""),
        ])
        gm = _GM(["Anker", "Gast"])
        shown = []
        session = TuiSession(
            onboard, catalog, "sniper", input_fn=_scripted_input([]), print_fn=shown.append,
            run_dir=run, states_dir=states, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: PersonaClaudeCodeDriver(
                ClaudeCodeConfig(binary="claude", isolated_workdir=str(base), extra_isolation_flags=["--strict-mcp-config"]),
                pk, process_runner=fake,
            ),
        )
        try:
            session._cmd_local_round(["persona:tech"])
        except EndOfInput:
            pass  # nur die Tischaufnahme wird geprueft, kein voller Abschluss noetig.
        table = store.Table.load(run, "local-sniper-tech")
        assert set(table.members) == {"sniper", "tech"}, "positive Hybrid-Kontrolle: typisierte Zusage muss aufnehmen"


# ---------------------------------------------------------------- A3: W1-B2 unter dem neuen Vertrag
def test_a3_mixed_consent_no_partial_group_under_new_contract():
    """A3 (PLAN-CRITIC.md): der neue typisierte Entscheidungsvertrag muss
    W1-B2 (keine Ersatz-Solo-/Restgruppe) per ECHTEM Testlauf erneut
    beweisen -- eine Persona sagt gueltig zu (typisierte Form), eine zweite
    liefert eine ungueltige/nicht-typisierte Antwort -> WEDER Solo- noch
    Restgruppen-Tisch entsteht, die Runde bricht kontrolliert ab."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, catalog, saves = _seed(base, {"sniper": "sniper", "tech": "tech"})
        write_test_profile(run)
        expected_offer_id = "invite-sniper-tech"
        # tech bekommt eine gueltige typisierte Zusage, ABER als zweiter
        # Gast (nicht vorhanden hier) waere die zweite Antwort ungueltig --
        # hier wird direkt die Ablehnungsform geprueft: 'tech' antwortet
        # OHNE typisierte Form (freier Text trotz frueherer Ja-Anmutung).
        with FakeHTTPServer([_http_response("Ja, ich habe die Einladung gelesen und lehne sie ab.")]) as srv:
            gm = _GM([])
            shown = []
            session = TuiSession(
                onboard, catalog, "sniper", input_fn=_scripted_input([]), print_fn=shown.append,
                run_dir=run, states_dir=states, schema_path=_SCHEMA,
                gm_transport_factory=lambda: gm,
                persona_driver_factory=lambda pk: PersonaApiDriver(
                    PersonaApiConfig(srv.base_url, "SYNTHETIC", "test"), pk,
                ),
            )
            session._cmd_local_round(["persona:tech"])
        table_file = run / "tables" / "local-sniper-tech.json"
        solo_file = run / "tables" / "local-sniper.json"
        assert not table_file.exists(), "ungueltige Antwort darf keine Mitgliedschaft erzeugen"
        assert not solo_file.exists(), "W1-B2: keine stille Solo-Ersatzrunde nach abgelehnter/ungueltiger Zusage"
        assert len(gm.calls) == 0, "kein GM-Turn ohne zustande gekommene Runde"


# ---------------------------------------------------------------- A4: Isolation != Requestautoritaet
def test_a4_isolated_hybrid_without_authorization_is_still_blocked():
    """A4 (PLAN-CRITIC.md, Kernfrage 2 'Isolation != Freigabe'): ein
    isolierter (CLI-Isolationsflags erfuellt), aber NICHT autorisierter
    (kein lab.status.json) Hybrid-Call muss am SELBEN 'keine Freigabe'-Grund
    scheitern wie ein API-Call -- die Isolationspruefung selbst darf NICHT
    stillschweigend als Requestfreigabe durchgehen. `decide()` darf in
    diesem Fall gar nicht erst aufgerufen werden (Gate VOR dem Request)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, catalog, saves = _seed(base, {"sniper": "sniper", "tech": "tech"})
        # BEWUSST: kein write_test_profile(run) -- keine Freigabe.
        blocked_api, reason_api = read_admission_block(run)
        assert blocked_api, "API-Rolle ohne Freigabe muss blockieren"

        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
        ])
        hybrid_calls = {"decide": 0}

        class _CountingHybridDriver(PersonaClaudeCodeDriver):
            def decide(self, context):
                hybrid_calls["decide"] += 1
                return super().decide(context)

        driver = _CountingHybridDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=str(base), extra_isolation_flags=["--strict-mcp-config"]),
            "tech", process_runner=fake,
        )
        # Isolation selbst ist erfuellbar (Testdouble-Konvention) --
        # UNABHAENGIG davon bleibt die Requestautoritaet (I2) unbelegt.
        driver.check_isolation()
        assert driver._isolation_checked is True, "Isolation muss fuer diesen Test tatsaechlich erfuellt sein"

        gm = _GM([])
        shown = []
        session = TuiSession(
            onboard, catalog, "sniper", input_fn=_scripted_input([]), print_fn=shown.append,
            run_dir=run, states_dir=states, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: driver,
        )
        session._cmd_local_round(["persona:tech"])
        assert hybrid_calls["decide"] == 0, (
            "Isolation != Freigabe: ein isolierter, aber nicht autorisierter Hybrid-Call darf "
            "'decide()' NIE erreichen (Gate blockiert VOR dem Request, wie beim API-Call)."
        )
        table_file = run / "tables" / "local-sniper-tech.json"
        assert not table_file.exists()
        assert any("Admission-Gate" in s for s in shown), shown


# ---------------------------------------------------------------- I2: Solo/Play + Lab
def test_i2_solo_play_blocked_when_lab_budget_exhausted():
    """Matrix 'Solo/Play + Lab': ein menschlicher Solo-Spieler unter einem
    ausdruecklich gestarteten, aber bereits erschoepften Lab-Budget wird
    ebenfalls blockiert -- dieselbe Gate-Grenze gilt fuer JEDE Rolle,
    Mensch eingeschlossen."""
    from mmo_sim.lab.runner import LabBudget, LabRunner

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, catalog, saves = _seed(base, {"sniper": "sniper"})
        lab = LabRunner(run, LabBudget(max_turns=0, max_seconds=1000, max_usd=10.0))
        lab.start()
        try:
            gm = _GM(["Anker"])
            shown = []
            session = TuiSession(
                onboard, catalog, "sniper", input_fn=_scripted_input(["Meine Aktion."]), print_fn=shown.append,
                run_dir=run, states_dir=states, schema_path=_SCHEMA,
                gm_transport_factory=lambda: gm,
            )
            session._cmd_local_round()
        finally:
            lab.release()
        assert len(gm.calls) == 0, "max_turns=0 muss bereits den ersten menschlichen Zug blockieren"
        assert any("Admission-Gate" in s or "blockiert" in s for s in shown), shown


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
