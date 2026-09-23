#!/usr/bin/env python3
"""
tests/mmo_sim/test_w1_w5_blocker_regressions.py — Regressionsschutz fuer die
drei vom End-Critic gefundenen und in der Main-Nacharbeit behobenen BLOCKER
(2026-09-23):

  W1-B1  interpret_yes_no_decision: eine per Zeilenumbruch (statt Satzzeichen)
         abgetrennte, widersprechende Zweitaussage darf NICHT accept liefern.
  W1-B2  _cmd_local_round: eine Ablehnung/ungueltige Antwort (Persona UND/ODER
         Mensch) darf WEDER einen stillen Solo-Tisch NOCH eine verkleinerte
         Restgruppe erzeugen -- die Runde bricht ab, kein Tisch entsteht.
  W5-B3  Isolationspruefung: ein Tool-restriktives Flag zaehlt nur mit WIRKSAMEM
         WERT (nicht schon durch seinen Namen); ein blanker wertnehmender
         Schalter (ohne '=wert') und ein nicht-restriktiver Wert werden abgelehnt.

Pure Python, nur `assert`, echter Exitcode. Providerfrei (keine echte Binary,
keine Inferenz)."""
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

from mmo_sim.adapters.base import interpret_yes_no_decision, ParticipantDecision  # noqa: E402
from mmo_sim.adapters.persona_claude_code import (  # noqa: E402
    _parse_isolation_flag,
    _tool_flag_value_is_effective,
)
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.ui.tui import TuiSession, EndOfInput  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures"
_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


# ---------------------------------------------------------------- W1-B1
def test_w1b1_newline_separated_contradiction_is_invalid():
    # Zweiter, widersprechender Satz nur per Zeilenumbruch abgetrennt.
    assert interpret_yes_no_decision("Ja\nIch lehne ab und bleibe draussen") == "invalid"
    assert interpret_yes_no_decision("Nein\nDoch, ich bin dabei.") == "invalid"


def test_w1b1_single_clean_answers_still_decide():
    # Regressionsschutz gegen Ueber-Ablehnung einfacher Einsatz-Antworten.
    assert interpret_yes_no_decision("Ja") == "accept"
    assert interpret_yes_no_decision("Ja.") == "accept"
    assert interpret_yes_no_decision("Ja, ich nehme an.") == "accept"
    assert interpret_yes_no_decision("Nein, ich lehne ab.") == "reject"
    assert interpret_yes_no_decision("") == "invalid"


# ---------------------------------------------------------------- W1-B2
class _RejectingDriver:
    """Persona-Treiber, der die Einladung strukturell ablehnt."""

    def decide(self, ctx):
        return ParticipantDecision("Nein, ich lehne ab.", origin_source="synthetic:persona")


class _GM:
    def turn(self, idx, text):
        return {"content": "weiter", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "regr"}


def _seed_and_import(base: Path, spec: dict):
    """spec: {participant_id: fixture_key} -- ein zusaetzlicher Mensch (z.B.
    'sniper2') darf einen vorhandenen Fixture-Save wiederverwenden (wie in der
    End-Critic-Probe), es gibt keinen eigenen 'sniper2.json'-Fixture."""
    run = base / "run"
    states = base / "states"
    onboard = base / "onboarding"
    cat = base / "catalog"
    ps = PersonaStateStore(_SCHEMA)
    for pid, fx in spec.items():
        st = json.loads((_FIX / "persona_states" / f"{fx}.json").read_text())
        st["rounds_played"] = 0
        st["round_history"] = {}
        st.pop("current_save_version", None)
        ps.save_state(pid, st, states_dir=states)
    for pid, fx in spec.items():
        save = json.loads((_FIX / "saves" / f"{fx}.json").read_text())
        it = iter([json.dumps(save), "ENDE"])
        TuiSession(onboard, cat, pid, input_fn=lambda prompt="": next(it), print_fn=lambda x: None,
                   run_dir=run, states_dir=states, schema_path=_SCHEMA)._cmd_import()
    return run, states, onboard, cat


def _no_local_table(run: Path, table_id: str) -> bool:
    return not (run / "tables" / f"{table_id}.json").exists()


def test_w1b2_mixed_group_all_reject_creates_no_table():
    # 1 Persona (lehnt via decide ab) + 1 Mensch (lehnt via Eingabe 'Nein' ab).
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # sniper=Leader, sniper2=zweiter Mensch, tech=Persona
        run, states, onboard, cat = _seed_and_import(base, {"sniper":"sniper","sniper2":"tech","tech":"tech"})
        answers = iter(["Nein"])

        def human_in(prompt=""):
            try:
                return next(answers)
            except StopIteration:
                raise EOFError()

        ui = TuiSession(onboard, cat, "sniper", input_fn=human_in, print_fn=lambda x: None,
                        run_dir=run, states_dir=states, schema_path=_SCHEMA,
                        gm_transport_factory=lambda: _GM(),
                        persona_driver_factory=lambda pid: _RejectingDriver())
        try:
            ui._cmd_local_round(["persona:tech", "sniper2"])
        except EndOfInput:
            pass
        assert _no_local_table(run, "local-sniper-sniper2-tech"), "gemischte Ablehnung -> kein Tisch"
        assert _no_local_table(run, "local-sniper"), "kein stiller Solo-Tisch"


def test_w1b2_pure_human_reject_creates_no_table():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run, states, onboard, cat = _seed_and_import(base, {"sniper":"sniper","sniper2":"tech"})
        answers = iter(["Nein"])

        def human_in(prompt=""):
            try:
                return next(answers)
            except StopIteration:
                raise EOFError()

        ui = TuiSession(onboard, cat, "sniper", input_fn=human_in, print_fn=lambda x: None,
                        run_dir=run, states_dir=states, schema_path=_SCHEMA,
                        gm_transport_factory=lambda: _GM())
        try:
            ui._cmd_local_round(["sniper2"])
        except EndOfInput:
            pass
        assert _no_local_table(run, "local-sniper-sniper2"), "menschliche Ablehnung -> kein Tisch"
        assert _no_local_table(run, "local-sniper"), "kein stiller Solo-Tisch"


# ---------------------------------------------------------------- W5-B3
def test_w5b3_parse_isolation_flag():
    assert _parse_isolation_flag("--permission-mode=plan") == ("--permission-mode", True, "plan")
    assert _parse_isolation_flag("--tools=") == ("--tools", True, "")
    assert _parse_isolation_flag("--safe-mode") == ("--safe-mode", False, "")


def test_w5b3_tool_flag_value_effectiveness():
    eff = _tool_flag_value_is_effective
    # restriktive Werte -> wirksam
    assert eff(*_parse_isolation_flag("--permission-mode=plan")) is True
    assert eff(*_parse_isolation_flag("--permission-mode=manual")) is True
    assert eff(*_parse_isolation_flag("--tools=")) is True          # alle Tools aus
    assert eff(*_parse_isolation_flag("--allowed-tools=Read")) is True
    # nicht-restriktive Werte / blanke Schalter -> NICHT wirksam
    assert eff(*_parse_isolation_flag("--permission-mode=bypassPermissions")) is False
    assert eff(*_parse_isolation_flag("--permission-mode=acceptEdits")) is False
    assert eff(*_parse_isolation_flag("--tools=default")) is False
    assert eff(*_parse_isolation_flag("--tools")) is False          # blanker wertnehmender Schalter
    assert eff(*_parse_isolation_flag("--permission-mode")) is False


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in sorted(tests, key=lambda f: f.__name__):
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
