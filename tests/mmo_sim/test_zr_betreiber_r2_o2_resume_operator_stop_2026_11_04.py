#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r2_o2_resume_operator_stop_2026_11_04.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R2, F1/O2 (Critic-Vera Auflage 2).
Regressionsschutz: `_resume_bound_table` gab beim Fortsetzen eines bereits
gebundenen BETREIBER-Tisches `operator_mode`/`operator_table_key` NICHT an
`_run_table_round` weiter -> ein resuemierter F1-Operator-Tisch verlor real
seine `/stop`-Faehigkeit waehrend eines laufenden Calls (O2-Regression NUR
im neuen F1-Pfad). R2-Fix: `_resume_bound_table` leitet jetzt
`operator_mode=bool(operator_meta.operator_id)` + den per host-id-freiem
Reverse-Lookup (`find_admission_for_section`) ermittelten
`operator_table_key` weiter -- gespiegelt am kanonischen Pfad
(`_cmd_local_round`).

Isolation (EHRLICH gekennzeichnet): die orthogonale Mitglieder-Aufloesung
(`_resolve_member`/`_local_round_list_humans`/`_lab_active_guard`) wird
gestubbt, damit der Test GENAU die Operator-Verdrahtung in
`_resume_bound_table` prueft (nicht die anderswo bereits getesteten
Resume-Aufloesungswege). `_run_table_round` wird durch einen Spy ersetzt,
der die uebergebenen Operator-Parameter festhaelt (kein echter Spielzug).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

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
from _section_completion_resume_fixtures import build_two_member_table, make_env  # noqa: E402

from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _RoundSpy:
    """Faengt GENAU die an `_run_table_round` uebergebenen Operator-Parameter
    ab -- fuehrt bewusst keinen Spielzug aus."""

    def __init__(self) -> None:
        self.calls = 0
        self.kwargs: dict | None = None

    def __call__(self, *a, **k) -> None:
        self.calls += 1
        self.kwargs = k


def _make_session(run_dir: Path, states_dir: Path, participant_id: str, members_chrono: dict):
    (run_dir.parent / "onboarding").mkdir(parents=True, exist_ok=True)
    (run_dir.parent / "catalog").mkdir(parents=True, exist_ok=True)
    session = TuiSession(
        onboarding_dir=run_dir.parent / "onboarding",
        catalog_dir=run_dir.parent / "catalog",
        participant_id=participant_id,
        print_fn=lambda *_a, **_k: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
        gm_transport_factory=lambda: None, host_capable=True,
    )
    # Orthogonale Resume-Aufloesung stubben (anderswo getestet) -- der Test
    # isoliert GENAU die Operator-Verdrahtung des R2-Fix.
    session._lab_active_guard = lambda *a, **k: False
    session._local_round_list_humans = lambda: [(pid, pid) for pid in members_chrono]
    session._resolve_member = lambda pid: (full_v7_save(members_chrono[pid]), members_chrono[pid])
    spy = _RoundSpy()
    session._run_table_round = spy
    return session, spy


def test_o2_resume_operatortisch_behaelt_stop_faehigkeit():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        _lobby, table, _ps = build_two_member_table(env, table_id="o2-resume-tisch")
        members_chrono = dict(table.chrononaut_ids)  # {leader_pk: chrono-leader, guest_pk: chrono-guest}

        # Betreibertisch: operator_meta gebunden + Admission-Record angelegt.
        op, tkey = "op_o2", "o2-resume-key"
        table.operator_meta["operator_id"] = op
        table.persist()
        table_admission.offer_table(env.run_dir, host_id=op, table_key=tkey)
        table_admission.bind_section(env.run_dir, table_key=tkey, host_id=op, section_id=table.table_id)

        session, spy = _make_session(env.run_dir, env.states_dir, table.leader, members_chrono)
        session._resume_bound_table(table)

        assert spy.calls == 1, f"_run_table_round haette genau einmal laufen muessen: {spy.calls}"
        assert spy.kwargs is not None and spy.kwargs.get("operator_mode") is True, (
            f"resuemierter Betreibertisch haette operator_mode=True weitergeben muessen: {spy.kwargs}"
        )
        assert spy.kwargs.get("operator_table_key") == tkey, (
            f"operator_table_key haette den gebundenen Schluessel tragen muessen: {spy.kwargs}"
        )


def test_o2_resume_nicht_operatortisch_bleibt_ohne_operator_mode():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        _lobby, table, _ps = build_two_member_table(env, table_id="o2-plain-tisch")
        members_chrono = dict(table.chrononaut_ids)
        # KEIN Betreibertisch -> operator_meta traegt keinen operator_id.
        table.operator_meta.pop("operator_id", None)
        table.persist()

        session, spy = _make_session(env.run_dir, env.states_dir, table.leader, members_chrono)
        session._resume_bound_table(table)

        assert spy.calls == 1, spy.calls
        assert spy.kwargs is not None and spy.kwargs.get("operator_mode") is False, spy.kwargs
        assert spy.kwargs.get("operator_table_key") is None, spy.kwargs


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
