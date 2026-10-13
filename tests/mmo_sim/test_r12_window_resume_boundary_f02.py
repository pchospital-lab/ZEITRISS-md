#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_window_resume_boundary_f02.py — R12-W74: F02
positive Bindung VOR jeder Zustandsfreigabe
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction` +
`mmo_sim/core/_save_correction_window.py`), jeweils als ECHTER
Zweiprozess-Fall (zwei getrennte `subprocess.run`-Instanzen gegen
denselben `run_dir`).

Abdeckung:
  (d) Caller/Record-Abschnitt -- ein Pausenrecord ist an
      `table_id=community-A`/`section_id=section-A` gebunden; ein
      ZWEITER Prozess ruft mit EINEM ANDEREN `section_id` (section-B)
      auf. Ledger-Abwesenheit fuer die ALTE Recordidentitaet darf KEINEN
      Versand unter der NEUEN Calleridentitaet legitimieren -- `status=
      "hold"`, KEIN Transport-Call, KEIN neuer Ledger-Datensatz.
  (e) Entwurfs-/Original-Bindung -- Prozess 1 pausiert mit Originalentwurf
      A (Name "Original Testfigur"); Prozess 2 ruft mit einem
      AUSGETAUSCHTEN Entwurf (gleicher char_id, Name "Changed Testfigur")
      auf, UND die SL-Antwort trägt zufällig/konsistent denselben
      geänderten Namen. Die Drift-Pruefung MUSS gegen den durabel
      GEBUNDENEN Originalentwurf laufen (nicht gegen den ausgetauschten
      Caller-Entwurf dieses zweiten Aufrufs) -- `status="hold"`,
      `reason="unjustified_semantic_drift"`.
  (f) Keine spekulative Migration vor Admission -- ein Legacy-`STATE_HOLD`
      (Prozess 1, direkt ueber `mark_hold` angelegt, OHNE `window_paused`-
      Vorlauf) bleibt bei einem Resume-Versuch in Prozess 2 BYTEGLEICH
      (PRE==POST, keine einzige Datei im `run_dir` aendert sich), SOLANGE
      das Admissionfenster NACHWEISLICH weiterhin geschlossen ist.

Pure Python, nur `assert`, echter Prozess-Exitcode."""
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
"""


# ---------------------------------------------------------------------------
# (d) Caller/Record-Abschnitt -- mismatched section_id on resume stays HOLD.
# ---------------------------------------------------------------------------

def test_d_caller_section_mismatch_stays_hold_no_send():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f02d_pid", "F02D-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
reason = "admission_blocked:reale Laufzeitgrenze (Wall-Clock) erreicht (Deadline 1.0, frisch von Platte, H-E)."
write_test_profile(run_dir)
sc.load_or_init_record(
    run_dir, repair_key, persona_key=pid, char_id=cid, operation_key=sc.ROLE_CREATION,
    table_id="community-A", section_id="section-A", errors=["synthetic wallet type"],
)
sc.begin_attempt(run_dir, repair_key)
sc.mark_hold(run_dir, repair_key, reason=reason)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({"phase": 1, "state": record["state"], "section_id": record["section_id"]}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Setup) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["state"] == "hold" and j1["section_id"] == "section-A", j1

        phase2 = base + """
valid = full_v7_save(cid, name="Flo", wallet=100)
valid["economy"]["wallets"] = {cid: {"balance": 100}}
invalid = copy.deepcopy(valid)
invalid["economy"]["wallets"][cid] = 100

class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein Transport-Call erwartet -- Caller/Record-Abschnitt-Mismatch.")

before = len(ledger._all_records(run_dir))
g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g,
    table_id="community-A", section_id="section-B",
)
after = len(ledger._all_records(run_dir))
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 2, "status": o.status, "calls": g.calls,
    "before_records": before, "after_records": after,
    "stored_section_after": record["section_id"], "record_state": record["state"],
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Mismatch-Resume) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["status"] == "hold", f"F02 Bindung: Mismatch MUSS terminal bleiben -- {j2}"
        assert j2["calls"] == [], f"F02 Bindung: KEIN Versand unter der neuen Calleridentitaet -- {j2}"
        assert j2["before_records"] == 0 and j2["after_records"] == 0, j2
        assert j2["stored_section_after"] == "section-A", (
            f"der gespeicherte Record bleibt an seine URSPRUENGLICHE Identitaet gebunden -- {j2}"
        )
        assert j2["record_state"] == "hold", j2


# ---------------------------------------------------------------------------
# (e) Entwurfs-/Original-Bindung -- swapped draft on resume is caught as
#     drift against the BOUND original, not the swapped caller draft.
# ---------------------------------------------------------------------------

def test_e_changed_draft_on_resume_is_caught_as_drift_hold():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f02e_pid", "F02E-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
valid = full_v7_save(cid, name="Original Testfigur", wallet=100)
valid["economy"]["wallets"] = {cid: {"balance": 100}}
original_draft = copy.deepcopy(valid)
original_draft["economy"]["wallets"][cid] = 100  # schema-invalid wallet (number, not object)

class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein Transport-Call erwartet -- Fenster ist geschlossen.")

write_test_profile(run_dir)
status = json.loads(_status_path(run_dir).read_text())
status["wall_deadline"] = 1.0
_atomic_write_json(_status_path(run_dir), status)
g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=original_draft, gm_transport=g,
    table_id="community-A", section_id="section-A",
)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 1, "status": o.status, "calls": g.calls,
    "state": record["state"], "bound_block_name": record["bound_block"]["characters"][0]["name"],
}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Pause) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["status"] == "hold" and j1["calls"] == [], j1
        assert j1["bound_block_name"] == "Original Testfigur", j1

        phase2 = base + """
changed_draft = full_v7_save(cid, name="Changed Testfigur", wallet=100)
changed_draft["economy"]["wallets"] = {cid: 100}  # weiterhin schema-invalid
reply_with_same_swap = full_v7_save(cid, name="Changed Testfigur", wallet=100)
reply_with_same_swap["economy"]["wallets"] = {cid: {"balance": 100}}  # jetzt schema-gueltig

class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        return {"content": "```json\\n" + json.dumps(reply_with_same_swap) + "\\n```", "usage": {}}

status = json.loads(_status_path(run_dir).read_text())
status.pop("wall_deadline")
_atomic_write_json(_status_path(run_dir), status)

g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=changed_draft, gm_transport=g,
    table_id="community-A", section_id="section-A",
)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({
    "phase": 2, "status": o.status, "reason": o.reason, "drift": o.drift,
    "calls": g.calls, "record_state": record["state"],
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Resume mit ausgetauschtem Entwurf) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["status"] == "hold" and j2["reason"] == "unjustified_semantic_drift", (
            f"F02 Entwurfsbindung: der Namens-Swap MUSS als Drift gegen den GEBUNDENEN "
            f"Original erkannt werden (NICHT gegen den ausgetauschten Caller-Entwurf) -- {j2}"
        )
        assert any(d[0] == "/characters/0/name" for d in j2["drift"]), j2
        assert j2["calls"] == [1], "der Versand selbst findet weiterhin statt (Admission wieder offen)."
        assert j2["record_state"] == "hold"


# ---------------------------------------------------------------------------
# (f) Keine spekulative Migration vor Admission -- legacy HOLD PRE==POST.
# ---------------------------------------------------------------------------

def test_f_legacy_hold_byte_identical_while_window_stays_closed():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        pid, cid = "f02f_pid", "F02F-CHAR"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), pid=pid, cid=cid)

        phase1 = base + """
reason = "admission_blocked:reale Laufzeitgrenze (Wall-Clock) erreicht (Deadline 1.0, frisch von Platte, H-E)."
write_test_profile(run_dir)
sc.load_or_init_record(
    run_dir, repair_key, persona_key=pid, char_id=cid, operation_key=sc.ROLE_CREATION,
    table_id="community-A", section_id="section-A", errors=["synthetic wallet type"],
)
sc.begin_attempt(run_dir, repair_key)
sc.mark_hold(run_dir, repair_key, reason=reason)
status = json.loads(_status_path(run_dir).read_text())
status["wall_deadline"] = 1.0
_atomic_write_json(_status_path(run_dir), status)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({"phase": 1, "state": record["state"]}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Legacy-Setup) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["state"] == "hold", j1

        def _hash_tree(path: Path) -> dict:
            return {
                str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in path.rglob("*") if p.is_file()
            }

        pre = _hash_tree(run_dir)

        phase2 = base + """
valid = full_v7_save(cid, name="Flo", wallet=100)
valid["economy"]["wallets"] = {cid: {"balance": 100}}
invalid = copy.deepcopy(valid)
invalid["economy"]["wallets"][cid] = 100

class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein Transport-Call erwartet -- Fenster bleibt geschlossen.")

g = Gm()
o = sc.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=pid, expected_chrononaut_id=cid,
    candidate_block=invalid, gm_transport=g,
    table_id="community-A", section_id="section-A",
)
record = sc.load_record(run_dir, repair_key)
print(json.dumps({"phase": 2, "status": o.status, "calls": g.calls, "record_state": record["state"]}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Resume-Versuch, Fenster weiterhin zu) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        post = _hash_tree(run_dir)

        assert j2["status"] == "hold" and j2["calls"] == [], j2
        assert j2["record_state"] == "hold", (
            f"KEIN Label-Wechsel hold->window_paused rein aus Anlass der Pruefung -- {j2}"
        )
        assert pre == post, (
            f"PRE==POST verletzt -- {run_dir} aenderte sich trotz weiterhin geschlossenem Fenster: "
            f"{sorted(set(pre) ^ set(post)) or [k for k in pre if pre[k] != post.get(k)]}"
        )


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
