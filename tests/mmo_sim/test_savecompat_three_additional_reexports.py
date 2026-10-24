#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_three_additional_reexports.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`three_additional_reexports` (02_SAVEVERTRAG.md §A/§C).

Prueft die bestehende, durch `save_correction.py` bereits durabel
implementierte Budgetgrenze "Original + max. 3 vollstaendige
Neuausgaben" (`MAX_ADDITIONAL_REQUESTS`) GENAU im Zusammenspiel mit dem
NEUEN Save-Compat-Overlay (`evaluate_with_cu_retention_projection`): jeder
der 3 zusaetzlichen Versuche wird zuerst durch die CU-Retention-Projektion
gereicht, BEVOR das Budget als erschoepft gilt; ein Neustart (frischer
Prozess, hier simuliert durch einen zweiten, unabhaengigen `load_record`-
Aufruf auf DIESELBE Platte) setzt den Zaehler NICHT auf 0 zurueck.

Bewusst auf den NIEDRIGEN Primitiven (`load_or_init_record`/`begin_attempt`/
`attempts_exhausted`) statt der vollen Erschaffungsdialog-Orchestrierung --
die volle End-zu-End-Kette (inkl. Admission/Transport) ist bereits durch die
bestehende Suite (`test_w48_save_correction_2026_10_07.py` SC07) abgedeckt;
dieser Test deckt NUR die save_compatibility-spezifische Ueberlagerung neu
ab (02_SAVEVERTRAG.md: 'der laufende Korrekturzyklus bindet sich auf die
CU_RETAINED_ONLY-Teilmenge')."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility as scompat  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as save_correction_domain  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    CHAR_ID = "chrono-reexport-01"
    REPAIR_KEY = save_correction_domain.creation_repair_key("participant-reexport-01", CHAR_ID)

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)

        # Erster Prozess: load_or_init legt den Datensatz frisch an.
        record = save_correction.load_or_init_record(
            run_dir, REPAIR_KEY, persona_key="participant-reexport-01",
            char_id=CHAR_ID, operation_key="creation",
        )
        check("fresh_record_starts_at_zero_attempts", record["attempts_used"] == 0)
        check("not_exhausted_at_zero", not save_correction.attempts_exhausted(record))

        # Drei zusaetzliche Versuche, jeder mit einer CU-belasteten Antwort, die
        # ERST durch die Projektion gueltig wird (Save-Compat-Overlay).
        for attempt_no in range(1, 4):
            record = save_correction.begin_attempt(run_dir, REPAIR_KEY)
            check(f"attempt_{attempt_no}_counter_incremented", record["attempts_used"] == attempt_no)
            raw_reply = full_v7_save(CHAR_ID, name="Flo")
            raw_reply["economy"] = {"wallets": {CHAR_ID: {"balance": 300, "currency": "CU"}}}
            outcome = scompat.evaluate_with_cu_retention_projection(raw_reply, CHAR_ID)
            check(f"attempt_{attempt_no}_cu_reply_accepted_via_projection", outcome.accepted and outcome.used_projection)

        exhausted_record = save_correction.load_record(run_dir, REPAIR_KEY)
        check("after_three_attempts_counter_is_three", exhausted_record["attempts_used"] == 3)
        check("after_three_attempts_budget_exhausted", save_correction.attempts_exhausted(exhausted_record))

        # Negativ: ein vierter Versuch darf NICHT automatisch gezaehlt/gesendet
        # werden -- der Aufrufer (Produktweg) muss `attempts_exhausted` VOR jedem
        # weiteren `begin_attempt` pruefen; dieser Test belegt nur, dass die
        # Vorbedingung bereits erfuellt ist (kein automatischer vierter Slot).
        check(
            "fourth_attempt_would_be_rejected_by_precondition",
            save_correction.attempts_exhausted(save_correction.load_record(run_dir, REPAIR_KEY)),
        )

        # ── Neustart-Simulation: EIN UNABHAENGIGER, frischer Aufruf von
        #    load_or_init_record auf DENSELBEN run_dir (anderer "Prozess") ──────
        restarted_record = save_correction.load_or_init_record(
            run_dir, REPAIR_KEY, persona_key="participant-reexport-01",
            char_id=CHAR_ID, operation_key="creation",
        )
        check("restart_does_not_reset_attempts_used", restarted_record["attempts_used"] == 3)
        check("restart_still_exhausted", save_correction.attempts_exhausted(restarted_record))

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
