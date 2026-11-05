#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r2_f2_tischstop_save_correction_2026_11_04.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R2, F2 (Critic-Vera Auflage 1,
GENERAL-REVIEW.md F2). Regressionsschutz fuer den vom General bereits am
R1-Stand benannten, in R1 UNbehobenen Befund: `save_correction.send_
correction_turn` rief `read_admission_block` OHNE `table_id` auf -> ein
gewonnener tischadressierter Betreiber-Stop blockte einen laufenden
Korrektur-Versand NICHT verlaesslich. R2-Fix: `table_id=table_id` wird jetzt
an beide Gate-Aufrufstellen (`save_correction.py:527`, `:1037`) weitergegeben.

Beweist:
 (A) OHNE Stop erreicht der Korrektur-Versand den Transport (Gate laesst
     durch, authorisiertes providerfreies Testprofil).
 (B) MIT einem gewonnenen tischadressierten Stop blockt derselbe Versand VOR
     jedem Transport (`_ExplodingGm.turn` wird nie erreicht) -- exakt die
     Invariante aus 01_NACHZUG.md F2 §4 ('save_correction darf trotz
     Tischstop keine neuen ... Korrekturrequests starten').

Pure Python, nur `assert`, echter Exitcode. Modellrand: Transport-Double."""
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

from mmo_sim.core import save_correction, table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

_ROLE = "save_correction_creation"


class _OkGm:
    """Liefert einen gueltigen v7-Debrief -- der Versand passiert das Gate
    und erreicht den Transport (Baseline ohne Stop)."""

    output_limit_tokens = None

    def __init__(self) -> None:
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        return {
            "content": "```json\n" + json.dumps(full_v7_save("CHR-F2-01")) + "\n```",
            "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "f2-ok",
        }


class _ExplodingGm:
    """Darf bei aktivem Tischstop NIE aufgerufen werden -- jeder Call ist der
    Regressionsbruch."""

    output_limit_tokens = None

    def turn(self, *a, **k):
        raise AssertionError(
            "F2: Korrektur-Versand trotz aktivem tischadressiertem Stop erreicht den Transport "
            "-- read_admission_block hat table_id nicht ausgewertet (Regressionsbruch)."
        )


def test_f2_tischstop_blockt_save_correction_versand():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        tid, tkey, op = "f2-corr-tisch", "f2-corr-key", "op_f2"
        write_test_profile(run_dir, max_turns=200)

        # (A) OHNE Stop: der Versand passiert das Gate und erreicht den Transport.
        ok = _OkGm()
        baseline = save_correction.send_correction_turn(
            run_dir, role=_ROLE, table_id=tid, section_id=tid, participant="flo_f2",
            turn_idx=1, outgoing_text="Erste Korrektur.", gm_transport=ok,
        )
        assert baseline.blocked is False, baseline
        assert ok.calls == 1, f"Baseline haette den Transport erreichen muessen: calls={ok.calls}"

        # Tischadressierten Betreiber-Stop binden + setzen (O6-Autoritaet).
        table_admission.offer_table(run_dir, host_id=op, table_key=tkey)
        table_admission.bind_section(run_dir, table_key=tkey, host_id=op, section_id=tid)
        payload = table_admission.request_table_stop(
            run_dir, table_key=tkey, operator_id=op, table_id=tid,
            reason="F2-Regression: Stop blockt Korrektur.",
        )
        assert payload.get("decision") == "stopped", payload

        # (B) MIT Stop: derselbe Versand (andere Operationsidentitaet turn_idx=2)
        # wird VOR jedem Transport geblockt -- _ExplodingGm.turn nie erreicht.
        blocked = save_correction.send_correction_turn(
            run_dir, role=_ROLE, table_id=tid, section_id=tid, participant="flo_f2",
            turn_idx=2, outgoing_text="Zweite Korrektur.", gm_transport=_ExplodingGm(),
        )
        assert blocked.blocked is True, f"Tischstop haette blocken muessen: {blocked}"
        assert blocked.reason.startswith("admission_blocked"), blocked.reason


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
