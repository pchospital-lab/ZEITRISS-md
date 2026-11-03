#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o4_stop_nach_planpin_2026_11_03.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O4 (design.md §1c/§6).

Beweist: ist der Plan BEREITS gepinnt (`__plan.json` existiert, der
Point-of-no-Return aus `complete_section` ist bereits ueberschritten),
gewinnt O4 -- ein DANACH gesetzter Betreiber-Stop verhindert den
erstmaligen Abschluss NICHT mehr (der Resume-Zweig `plan_path.exists()`
liegt VOR dem Stop-Guard, s. A-codemap.md F1/design.md §1c-Kommentar
"ein bereits gepinnter Plan ... ist committet -> O4 gewinnt, kein
Rollback"). Ein Finish-Retry bleibt IDEMPOTENT (kein Doppel-Harvest, keine
zweite Figur, keine inhaltliche Aenderung der bereits geschriebenen
Primaersaves)."""
from __future__ import annotations

import hashlib
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

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_TODAY = "2026-11-03"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_o4_plan_bereits_gepinnt_stop_danach_kein_rollback_idempotenter_retry():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="o4-tisch")
        section_id = table.table_id
        harvested = {
            "leader_pk": full_v7_save("chrono-leader", name="Testfigur"),
            "guest_pk": full_v7_save("chrono-guest", name="Testfigur"),
        }

        # Erstabschluss: KEIN Stop aktiv -- der Plan wird real gepinnt.
        result1 = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert result1.success is True, result1
        assert result1.written is True, result1
        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        assert plan_path.exists(), "Plan haette gepinnt sein muessen (Point-of-no-Return)."

        current_saves_dir = env.run_dir / "current_saves"
        leader_save_path = current_saves_dir / "leader_pk.json"
        guest_save_path = current_saves_dir / "guest_pk.json"
        assert leader_save_path.exists() and guest_save_path.exists()
        sha_leader_1 = _sha256(leader_save_path)
        sha_guest_1 = _sha256(guest_save_path)

        # JETZT -- NACH dem Plan-Pin -- einen Betreiber-Stop setzen.
        table_admission.offer_table(env.run_dir, host_id="leader_pk", table_key="o4-key")
        table_admission.bind_section(
            env.run_dir, table_key="o4-key", host_id="leader_pk", section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key="o4-key", operator_id="leader_pk", table_id=table.table_id,
            reason="O4-Test: Stop NACH Plan-Pin.",
        )
        stopped, _reason = admission.read_table_stop(env.run_dir, table.table_id)
        assert stopped is True, "Stop-Datei haette real geschrieben sein muessen."

        # Finish-Retry (z.B. nach einem Prozessneustart) -- derselbe Aufruf,
        # dieselben bereits geernteten Bloecke. O4 gewinnt: der Resume-Zweig
        # (plan_path.exists()) liegt VOR dem Stop-Guard, der Abschluss bleibt
        # idempotent erfolgreich abgeschlossen, KEIN Rollback.
        result2 = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert result2.success is True, (
            f"O4: ein Stop NACH dem Plan-Pin darf den bereits committeten Abschluss nicht "
            f"rueckgaengig machen (kein Rollback). result={result2}"
        )
        # Idempotent: kein zweiter/abweichender Primaersave-Write (kein
        # Doppel-Harvest, keine zweite Figur) -- bytegleich zum ersten Write.
        assert _sha256(leader_save_path) == sha_leader_1, "Doppel-Harvest: leader_pk-Save wurde erneut geschrieben."
        assert _sha256(guest_save_path) == sha_guest_1, "Doppel-Harvest: guest_pk-Save wurde erneut geschrieben."
        assert plan_path.exists(), "Plan darf durch den Stop nicht entfernt werden (kein Rollback)."

        final_path = env.run_dir / "completion" / f"{section_id}__final.json"
        assert not final_path.exists(), (
            "Phase 2 (Finalrecord) ist in diesem Test nicht erreicht worden -- "
            "ein vorhandener __final.json waere ein Testaufbaufehler, kein O4-Befund."
        )


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
