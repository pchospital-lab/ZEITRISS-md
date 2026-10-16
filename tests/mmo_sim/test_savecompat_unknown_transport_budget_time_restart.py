#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_unknown_transport_budget_time_restart.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`unknown_transport_budget_time_restart` (02_SAVEVERTRAG.md §A/§C).

Zwei getrennte Schutzziele:

  1. Ein UNBEKANNTER Transportfehler (z.B. abgebrochene Verbindung,
     unparsebare Antwort auf Transportebene) ist KEIN Schemafehler --
     `send_correction_turn` klassifiziert ihn als `transport_error:...`,
     NICHT als etwas, das automatisch neu interpretiert/resendet wird
     (02: 'unbekannter Transport != Schemafehler, kein Auto-Resend').
  2. Budget/Zeit ueberleben einen Neustart (frischer `load_or_init_record`-
     Aufruf auf DENSELBEN run_dir) UNVERAENDERT -- kein Zuruecksetzen des
     Versuchszaehlers durch einen reinen Prozess-Neustart."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as save_correction_domain  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


class _UnknownTransport:
    """Simuliert einen unbekannten/gescheiterten Transport (z.B. Netzwerk-
    Abbruch, unparsebare Rohantwort auf Transportebene) -- KEIN
    Schema-/Bindungsproblem, das die normale Korrektur-/Drift-Logik
    ueberhaupt zu Gesicht bekommt."""

    def turn(self, turn_idx, outgoing_text):
        raise ConnectionError("unknown_transport: Verbindung waehrend des Turns abgebrochen")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)

        outcome = save_correction.send_correction_turn(
            run_dir, role="gm", table_id=None, section_id=None, participant="participant-transport-01",
            turn_idx=0, outgoing_text="Testnachricht", gm_transport=_UnknownTransport(),
        )
        check("unknown_transport_result_is_blocked", outcome.blocked)
        check("unknown_transport_reason_is_transport_error_category", outcome.reason.startswith("transport_error:"))
        check(
            "unknown_transport_reason_not_misclassified_as_schema_or_drift",
            "schema" not in outcome.reason and "drift" not in outcome.reason,
        )
        public = save_correction.public_hold_reason(outcome.reason)
        check("unknown_transport_public_reason_is_safe_category_not_raw_exception_text", "ConnectionError" not in public)

    # ── Budget/Zeit ueberleben einen Neustart unveraendert ─────────────────────
    with tempfile.TemporaryDirectory() as td2:
        run_dir2 = Path(td2)
        repair_key = save_correction_domain.creation_repair_key("participant-restart-01", "chrono-restart-01")

        record = save_correction.load_or_init_record(
            run_dir2, repair_key, persona_key="participant-restart-01",
            char_id="chrono-restart-01", operation_key="creation",
        )
        for _ in range(save_correction.MAX_ADDITIONAL_REQUESTS):
            record = save_correction.begin_attempt(run_dir2, repair_key)
        check("budget_fully_consumed_before_restart", save_correction.attempts_exhausted(record))
        created_ts_before_restart = record["created_ts"]

        # "Neustart" -- unabhaengiger, frischer Aufruf auf DENSELBEN run_dir;
        # darf den Zaehler NICHT zuruecksetzen und die urspruengliche
        # Erstanlagezeit NICHT neu stempeln.
        restarted = save_correction.load_or_init_record(
            run_dir2, repair_key, persona_key="participant-restart-01",
            char_id="chrono-restart-01", operation_key="creation",
        )
        check("restart_attempts_used_unchanged", restarted["attempts_used"] == save_correction.MAX_ADDITIONAL_REQUESTS)
        check("restart_still_exhausted_after_restart", save_correction.attempts_exhausted(restarted))
        check("restart_created_ts_not_overwritten", restarted["created_ts"] == created_ts_before_restart)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
