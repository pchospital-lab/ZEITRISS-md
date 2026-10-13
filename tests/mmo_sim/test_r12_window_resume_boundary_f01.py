#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_window_resume_boundary_f01.py — R12-W74: schliesst
die drei F01-Luecken des W73-Pausenvertrags
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction` +
`mmo_sim/core/_save_correction_window.py`), jeweils als ECHTER
Zweiprozess-Fall (zwei getrennte `subprocess.run`-Instanzen gegen
denselben `run_dir`, kein In-Process-Funktionsaufruf-Fake).

Abdeckung:
  (a) F01a -- ein bereits DURABEL empfangener, fehlerfreier Korrektur-
      Request (`state in (received, accounted)`, `error is None`,
      `result_text` gesetzt) wird nach einem Crash GENAU VOR
      `record_correction_received` ueber den REGULAEREN Recoveryweg
      (`send_correction_turn`/`request_ledger.find_durable_result`)
      wiederverwendet -- `status="accepted"`, KEIN zweiter Transport-Call,
      GENAU EIN Ledger-Datensatz bleibt erhalten.
  (b) F01b -- ein bereits `accounted` Request MIT `error` (echter
      Transportfehler, `finish_error`) ist fuer `find_durable_result`/
      `find_answered_without_text` BEIDE bewusst unsichtbar (beide
      verlangen `error is None`) und faellt NIE in `open_requests`
      (nur nicht-`accounted`) -- ein Resume darf diesen Slot NICHT als
      "nie versandt" werten: `status="hold"` bleibt terminal, KEIN
      zweiter POST, weiterhin GENAU EIN Ledger-Datensatz fuer diese
      Identitaet.
  (c) F01c -- Slot 1 wird gesendet+ausgewertet (ungueltig, keine Drift)
      und oeffnet GENAU DESHALB Slot 2 (`attempts_used=2`); Slot 2 pausiert
      selbst admission-blockiert. `last_request_id` zeigt dabei weiterhin
      auf Slot 1s Request-ID. Ein Resume MUSS Slot 2 (nicht Slot 1) ueber
      die VOLLE Identitaetspruefung (`turn_idx=attempts_used=2`) fortsetzen
      -- unabhaengig von `last_request_id`s Nicht-Null-Wert.

Pure Python, nur `assert`, echter Prozess-Exitcode -- gleiches Muster wie
die bestehende Suite (`test_r12_window_hold_single_figure.py`)."""
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

from _r12_window_resume_boundary_fixture import last_json, run_phase  # noqa: E402

_COMMON_SETUP = """
import copy, json
from pathlib import Path
from _full_v7_fixture import full_v7_save
from mmo_sim.core import save_correction as sc, request_ledger as ledger
from mmo_sim.core.admission import write_test_profile, _status_path, _atomic_write_json
from mmo_sim.domain.zeitriss import save_correction as domain

run_dir = Path({run_dir!r})
pid, cid = {pid!r}, {cid!r}
repair_key = domain.creation_repair_key(pid, cid)
valid = full_v7_save(cid, name="Flo", wallet=100)
valid["economy"]["wallets"] = {{cid: {{"balance": 100}}}}
invalid = copy.deepcopy(valid)
invalid["economy"]["wallets"][cid] = 100
"""


# ---------------------------------------------------------------------------
# (a) F01a -- durable accounted-without-error result is reused, not held.
# ---------------------------------------------------------------------------

def test_a_durable_accounted_result_without_error_is_reused_not_held():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f01a_pid", "F01A-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
class Gm:
    output_limit_tokens = 1024
    base_url = "http://127.0.0.1:9"
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        return {"content": "```json\\n" + json.dumps(valid) + "\\n```", "usage": {}}

def invoke(gm):
    return sc.pursue_single_figure_correction(
        run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
        candidate_block=invalid, gm_transport=gm,
    )

write_test_profile(run_dir)
status = json.loads(_status_path(run_dir).read_text())
status["wall_deadline"] = 1.0
_atomic_write_json(_status_path(run_dir), status)
g0 = Gm()
o0 = invoke(g0)
assert o0.status == "hold" and g0.calls == [], o0

status = json.loads(_status_path(run_dir).read_text())
status.pop("wall_deadline")
_atomic_write_json(_status_path(run_dir), status)

def _crash(*a, **kw):
    raise SystemExit(74)
sc.record_correction_received = _crash
try:
    invoke(Gm())
    raise AssertionError("crash point not reached")
except SystemExit as exc:
    assert exc.code == 74

records = ledger._all_records(run_dir)
print(json.dumps({
    "phase": 1, "record_count": len(records),
    "record_states": [(r["state"], r["error"]) for r in records],
}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Crash-Setup) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["record_count"] == 1, j1
        assert j1["record_states"] == [["accounted", None]], j1

        phase2 = base + """
class ExplodingGm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein Transport-Call erwartet -- der durable Treffer muss wiederverwendet werden.")

before = len(ledger._all_records(run_dir))
g = ExplodingGm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g,
)
after = len(ledger._all_records(run_dir))
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 2, "status": o.status, "block_equals_valid": o.block == valid,
    "transport_calls": g.calls, "before_records": before, "after_records": after,
    "record_state": record["state"], "attempts_used": record["attempts_used"],
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Resume) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["status"] == "accepted", j2
        assert j2["block_equals_valid"] is True, j2
        assert j2["transport_calls"] == [], f"F01a: kein zweiter POST erwartet -- {j2}"
        assert j2["before_records"] == 1 and j2["after_records"] == 1, (
            f"F01a: KEIN neuer Ledger-Datensatz durch das Resume -- {j2}"
        )
        assert j2["record_state"] == "adopted" and j2["attempts_used"] == 1, j2


# ---------------------------------------------------------------------------
# (b) F01b -- accounted-with-error stays terminal, never re-sent.
# ---------------------------------------------------------------------------

def test_b_accounted_result_with_error_stays_terminal_no_resend():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f01b_pid", "F01B-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
class Gm:
    output_limit_tokens = 1024
    base_url = "http://127.0.0.1:9"
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise TimeoutError("SYNTHETIC_TRANSPORT_FAILURE")

def invoke(gm):
    return sc.pursue_single_figure_correction(
        run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
        candidate_block=invalid, gm_transport=gm,
    )

write_test_profile(run_dir)
status = json.loads(_status_path(run_dir).read_text())
status["wall_deadline"] = 1.0
_atomic_write_json(_status_path(run_dir), status)
o0 = invoke(Gm())
assert o0.status == "hold", o0

status = json.loads(_status_path(run_dir).read_text())
status.pop("wall_deadline")
_atomic_write_json(_status_path(run_dir), status)

def _crash(*a, **kw):
    raise SystemExit(73)
sc.mark_hold = _crash
try:
    invoke(Gm())
    raise AssertionError("crash point not reached")
except SystemExit as exc:
    assert exc.code == 73

records = ledger._all_records(run_dir)
print(json.dumps({
    "phase": 1, "record_count": len(records),
    "record_states": [(r["state"], r["error"]) for r in records],
}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Crash-Setup) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["record_count"] == 1, j1
        assert j1["record_states"] == [["accounted", "SYNTHETIC_TRANSPORT_FAILURE"]], j1

        phase2 = base + """
class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein zweiter Transport-Call erwartet -- der Slot ist terminal.")

before = len(ledger._all_records(run_dir))
g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g,
)
after = len(ledger._all_records(run_dir))
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 2, "status": o.status, "transport_calls": g.calls,
    "before_records": before, "after_records": after,
    "record_state": record["state"], "attempts_used": record["attempts_used"],
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Resume) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["status"] == "hold", f"F01b: muss terminal bleiben -- {j2}"
        assert j2["transport_calls"] == [], f"F01b: KEIN zweiter POST fuer denselben Slot -- {j2}"
        assert j2["before_records"] == 1 and j2["after_records"] == 1, (
            f"F01b: weiterhin GENAU EIN Ledger-Datensatz -- kein Doppel-Send -- {j2}"
        )
        assert j2["attempts_used"] == 1, j2


# ---------------------------------------------------------------------------
# (c) F01c -- slot 2 resumes despite a stale slot-1 last_request_id.
# ---------------------------------------------------------------------------

def test_c_second_slot_resumes_despite_stale_last_request_id_from_slot_one():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f01c_pid", "F01C-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        # Slot 1 antwortet SOFORT (weiterhin ungueltig) UND schliesst das
        # Fenster WAEHREND des Calls -- Slot 2 (direkt danach, derselbe
        # Prozess, derselbe while-Schleife) trifft auf ein bereits
        # geschlossenes Fenster.
        status = json.loads(_status_path(run_dir).read_text())
        status["wall_deadline"] = 1.0
        _atomic_write_json(_status_path(run_dir), status)
        return {"content": "```json\\n" + json.dumps(invalid) + "\\n```", "usage": {}}

write_test_profile(run_dir)
g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g, table_id="community", section_id="gen1",
)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 1, "status": o.status, "calls": g.calls,
    "state": record["state"], "attempts_used": record["attempts_used"],
    "last_request_id_present": record["last_request_id"] is not None,
    "record_count": len(ledger._all_records(run_dir)),
}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Slot1+Slot2-Pause) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["status"] == "hold" and j1["state"] == "window_paused", j1
        assert j1["attempts_used"] == 2, f"Slot 2 muss bereits begonnen worden sein -- {j1}"
        assert j1["last_request_id_present"] is True, (
            f"Vorbedingung verletzt -- last_request_id muss noch auf Slot 1 zeigen -- {j1}"
        )
        assert j1["calls"] == [1], j1
        assert j1["record_count"] == 1, j1

        phase2 = base + """
class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        return {"content": "```json\\n" + json.dumps(valid) + "\\n```", "usage": {}}

status = json.loads(_status_path(run_dir).read_text())
status.pop("wall_deadline")
_atomic_write_json(_status_path(run_dir), status)

g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g, table_id="community", section_id="gen1",
)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 2, "status": o.status, "block_equals_valid": o.block == valid,
    "calls": g.calls, "attempts_used": record["attempts_used"], "state": record["state"],
    "record_count": len(ledger._all_records(run_dir)),
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Slot2-Resume) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["status"] == "accepted", f"F01c: Slot 2 muss regulaer fortsetzbar sein -- {j2}"
        assert j2["block_equals_valid"] is True, j2
        assert j2["calls"] == [2], f"F01c: Versand MUSS turn_idx=2 (Slot 2) verwenden, kein Slot1-Resend -- {j2}"
        assert j2["attempts_used"] == 2, j2
        assert j2["record_count"] == 2, f"GENAU EIN Ledger-Datensatz je Slot (1 und 2) -- {j2}"


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
