#!/usr/bin/env python3
"""
tests/mmo_sim/test_a10_community_bootstrap.py — A10/A3: "Crash beim Bootstrap,
Programmrestart, Update: keine zweite Roster-Erstellung; keine hochgelevelte
Zufallsstaffage." Crash-sicheres Journal-Muster (Plan/Guard/Final) analog
`complete_section`, s. PLAN-CRITIC.md A3.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402

_DUMMY_SCHEMA = '{"type":"object","required":["v","persona_key"],"properties":{"v":{"const":2}}}'

TARGET_PERSONAS = {
    "cqb": {"real_name": "Cee", "plays_char": {"character_id": "chrono-cqb"}},
    "sniper": {"real_name": "Ess", "plays_char": {"character_id": "chrono-sniper"}},
    "face": {"real_name": "Eff", "plays_char": {"character_id": "chrono-face"}},
}


def _new_env(root: Path):
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    states_dir = root / "states"
    states_dir.mkdir()
    community_dir = root / "community"
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    return ps_store, states_dir, community_dir


def test_crash_mid_bootstrap_then_resume_writes_no_duplicates():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ps_store, states_dir, community_dir = _new_env(root)

        real_save_state = ps_store.save_state
        calls = {"n": 0}

        def crash_after_two(pk, state, states_dir=None):
            calls["n"] += 1
            if calls["n"] > 2:
                raise RuntimeError("simulierter Absturz waehrend des Bootstrap-Schreibens")
            return real_save_state(pk, state, states_dir=states_dir)

        with patch.object(ps_store, "save_state", new=crash_after_two):
            try:
                bootstrap_community(community_dir, "comm-1", 1, TARGET_PERSONAS, ps_store, states_dir, today="2026-09-22")
                assert False, "haette bei simuliertem Absturz werfen muessen"
            except RuntimeError:
                pass

        # Genau 2 Personas wurden vor dem Absturz geschrieben.
        written_before = sorted(p.stem for p in states_dir.glob("*.json"))
        assert len(written_before) == 2, f"vor Resume sollten genau 2 Personas geschrieben sein, war: {written_before}"

        # Resume (frische PersonaStateStore-Instanz simuliert Programmrestart).
        ps_store2 = PersonaStateStore(schema_path=ps_store.schema_path, default_states_dir=None)
        result = bootstrap_community(community_dir, "comm-1", 1, TARGET_PERSONAS, ps_store2, states_dir, today="2026-09-22")

        assert not result.already_completed, "erster ERFOLGREICHER Abschluss ist kein already_completed"
        assert set(result.personas_written) == set(TARGET_PERSONAS.keys())
        written_after = sorted(p.stem for p in states_dir.glob("*.json"))
        assert written_after == sorted(TARGET_PERSONAS.keys()), "keine Duplikate, kein fehlendes Mitglied nach Resume"

        # Zweiter Aufruf (z.B. Programm-Restart nach vollstaendigem Erfolg) ->
        # No-op, KEINE zweite Roster-Erstellung.
        result2 = bootstrap_community(community_dir, "comm-1", 1, TARGET_PERSONAS, ps_store2, states_dir, today="2026-09-23")
        assert result2.already_completed
        assert set(result2.personas_written) == set(TARGET_PERSONAS.keys())


def test_bootstrap_plan_pins_target_list_even_if_argument_changes_on_retry():
    """Ein Retry mit einer (fehlerhaft) ABWEICHENDEN Zielliste darf die
    urspruenglich gepinnte Liste NICHT ersetzen (kein Mischen zweier
    Ernten/Rosterversionen, analog complete_section-Auflage 4)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ps_store, states_dir, community_dir = _new_env(root)

        real_save_state = ps_store.save_state
        calls = {"n": 0}

        def crash_after_one(pk, state, states_dir=None):
            calls["n"] += 1
            if calls["n"] > 1:
                raise RuntimeError("Absturz")
            return real_save_state(pk, state, states_dir=states_dir)

        with patch.object(ps_store, "save_state", new=crash_after_one):
            try:
                bootstrap_community(community_dir, "comm-2", 1, TARGET_PERSONAS, ps_store, states_dir, today="2026-09-22")
            except RuntimeError:
                pass

        drifted_target = {"cqb": TARGET_PERSONAS["cqb"], "medic": {"real_name": "Med", "plays_char": {}}}
        result = bootstrap_community(community_dir, "comm-2", 1, drifted_target, ps_store, states_dir, today="2026-09-22")
        # Die urspruengliche 3er-Liste (cqb/sniper/face) bleibt massgeblich, NICHT die abweichende 2er-Liste.
        assert set(result.personas_written) == set(TARGET_PERSONAS.keys()), (
            f"gepinnter Plan haette die Original-Zielliste behalten muessen, war: {result.personas_written}"
        )


def main() -> int:
    tests = [test_crash_mid_bootstrap_then_resume_writes_no_duplicates, test_bootstrap_plan_pins_target_list_even_if_argument_changes_on_retry]
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
