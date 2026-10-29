#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_recovery_extra_attempts_2026_10_28.py
-- ZR-N2R-ANSCHLUSS-20261019-R4 START-FRESH, FIX3: eine ausdruecklich
beauftragte, bounded Zusatzkorrektur eines bereits erschoepften
Korrekturdatensatzes ("begrenzte Zusatzkorrektur" ohne Counter-Reset).

`save_correction.attempts_exhausted` hebt die Erschoepfungsschwelle um ein
gedeckeltes `record["recovery_extra_attempts"]` an, OHNE `attempts_used`
anzutasten (die Versuchshistorie bleibt wahr). Ohne das Feld bleibt das
Verhalten exakt unveraendert.

Pure Python, nur assert."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import save_correction as sc  # noqa: E402

MAX = sc.MAX_ADDITIONAL_REQUESTS


def test_without_field_unchanged():
    assert sc.attempts_exhausted({"attempts_used": MAX}) is True
    assert sc.attempts_exhausted({"attempts_used": MAX - 1}) is False
    assert sc.attempts_exhausted({"attempts_used": 0}) is False


def test_bounded_extra_raises_threshold_without_resetting_counter():
    # Erschoepft (3) + 3 Zusatzkorrekturen -> wieder zulaessig, attempts_used bleibt 3.
    rec = {"attempts_used": MAX, "recovery_extra_attempts": 3}
    assert sc.attempts_exhausted(rec) is False
    assert rec["attempts_used"] == MAX, "attempts_used darf NICHT zurueckgesetzt werden"
    # Nach Aufbrauchen der Zusatzrunden wieder erschoepft.
    assert sc.attempts_exhausted({"attempts_used": MAX + 3, "recovery_extra_attempts": 3}) is True
    assert sc.attempts_exhausted({"attempts_used": MAX + 2, "recovery_extra_attempts": 3}) is False


def test_extra_is_hard_capped():
    # Ein zu grosses Feld wird hart auf MAX_RECOVERY_EXTRA_ATTEMPTS gedeckelt.
    cap = sc.MAX_RECOVERY_EXTRA_ATTEMPTS
    rec = {"attempts_used": MAX + cap, "recovery_extra_attempts": 999}
    assert sc.attempts_exhausted(rec) is True, "ueber die Deckelung hinaus keine weiteren Runden"
    assert sc.attempts_exhausted({"attempts_used": MAX + cap - 1, "recovery_extra_attempts": 999}) is False


def test_invalid_or_nonpositive_extra_is_ignored():
    for bad in (None, 0, -2, True, False, "3", 2.5, [3]):
        rec = {"attempts_used": MAX, "recovery_extra_attempts": bad}
        assert sc.attempts_exhausted(rec) is True, f"ungueltiges extra {bad!r} darf keine Zusatzrunde geben"


def main() -> int:
    tests = [
        test_without_field_unchanged,
        test_bounded_extra_raises_threshold_without_resetting_counter,
        test_extra_is_hard_capped,
        test_invalid_or_nonpositive_extra_is_ignored,
    ]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\nall {len(tests)} FIX3 recovery-extra-attempts tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
