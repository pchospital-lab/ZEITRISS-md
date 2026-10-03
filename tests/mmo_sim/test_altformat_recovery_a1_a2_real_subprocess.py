#!/usr/bin/env python3
"""
tests/mmo_sim/test_altformat_recovery_a1_a2_real_subprocess.py — dauerhafte
Regressionstests fuer den Altformat-Recovery-Nachzug A1/A2 (2026-09-25,
MAIN-DATENWEGENTSCHEIDUNG.md, REVIEW-COMMUNITY-ALTFORMAT.md §3/§4). Adaptiert
aus der einmaligen Paket-Probe `tests-review/review_legacy_outcome_recovery.py`
(Ausgangsbefund dort: 2 PASS/2 FAIL fuer genau diese beiden Faelle) in
dauerhafte In-Repo-Tests -- repo-uebliche `main()`/Exitcode-Form, echter
Subprozessneustart (kein neues Objekt im selben Interpreter).

A1 (`request_ledger.settle_received`, GM-Guard in `core.creation_service.
run_admitted_creation_dialog`, Persona-Guard in `domain.zeitriss.
community_creation._get_reply`): ein Alt-`received`-Record OHNE
`received_seconds` (Schluessel ABWESENT, vor R1 geschrieben) darf NICHT als
0-Dauer accounted/ready geschlossen werden -- der Dialog bleibt kontrolliert
offen (kein `completed`/`already_ready`, kein abhaengiger Modellaufruf).
Getrennt fuer alle drei Ergebnisphasen (SL-Frage, Personaantwort, SL-
Erstsave) mit je einem ECHTEN Subprozessneustart. Test 01-03 unten. Test 04
(direkter Funktionsaufruf, kein Subprozess noetig) haelt die Gegenprobe fest:
eine ECHT aufgezeichnete `0.0`-Dauer ist weiterhin eine gueltige bekannte
Dauer (PRAESENZ des Schluessels entscheidet, nicht Truthiness).

A2 (`request_ledger.find_answered_without_text`, dieselben beiden Aufrufer):
ein Alt-Record, der nachweislich bereits gesendet+verbucht wurde (`state in
("received","accounted")`, kein `error`), aber NIE einen `result_text`
persistiert hat (vor C2 geschrieben), darf NICHT zu einer neuen Reservierung/
Anfrage fuer dieselbe Operationsidentitaet fuehren -- Record-Zahl bleibt
unveraendert. Getrennt fuer alle drei Ergebnisphasen, je ein echter
Subprozessneustart. Test 05-07 unten. Test 08 (direkter Funktionsaufruf)
haelt fest: eine ANDERE Operationsidentitaet (anderer `turn_idx`) bleibt von
einem fremden textlosen Alt-Record UNBERUEHRT -- kein universelles "alle
accounted IDs sperren".

Die Legacy-Fixtures (`_legacy_finish_received_no_seconds`/
`_legacy_finish_received_no_text` unten) sind ein Nachbau des ECHTEN
Vorversions-`finish_received()` -- derselbe reale `begin()`/`add_seconds`/
`record_usd_delta`-Aufrufpfad wie die aktuelle Funktion, nur OHNE das
jeweils neue Feld im ersten Write (exakt das Schema, das der jeweilige
Vorversionswriter tatsaechlich geschrieben hat) -- keine hand-getippte
Legacy-JSON. Der externe Cross-Interpreter-Beleg mit den ECHTEN historischen
Writer-Bytes (d46a7f69/10024452) lebt weiterhin in der einmaligen Paket-
Probe; diese Datei haelt NUR den Lesevertrag/Aufrufer-Kontrollfluss
dauerhaft in-repo fest, mit echtem Prozessneustart je Fall.

Testdoubles ausschliesslich an Modell-/Fehlerstellen (Response-Doubles je
Kindprozess, echte neue PIDs), keine echte Modellbinary/Anbieterroute."""
from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core import request_ledger as ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_one_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PS = PersonaStateStore(schema_path=SCHEMA)
PK = "altformat_persona"
Q = "SYNTHETIC: Welche Ausruestung waehlst du?"
A = "SYNTHETIC: Ich waehle leichte Ruestung."
SAVE = {"v": 7, "save_id": "SYNTHETIC-ALTFORMAT-SAVE",
        "characters": [{"char_id": "SYNTHETIC-ALTFORMAT-CHR", "name": "Synthetic", "callsign": "ALTFMT", "level": 1}]}
ST = "```json\n" + json.dumps(SAVE) + "\n```"


def _setup(b: Path) -> None:
    draft = {
        "real_name": "Synthetic Altformat", "archetype": "SYNTHETIC_ARCH", "play_style": "SYNTHETIC_STYLE",
        "charwunsch": "SYNTHETIC_WISH",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
    }
    bootstrap_community(b / "run/community", "altformat-community", 1, {PK: draft}, PS, b / "states", "2026-09-25")
    write_test_profile(b / "run", max_turns=100, max_usd=10)


def _snapshot(b: Path) -> dict:
    d = {
        "budget": json.loads((b / "run/lab.status.json").read_text()),
        "records": [json.loads(f.read_text()) for f in sorted((b / "run/requests").glob("*.json"))],
    }
    try:
        d["current"] = store.load_current_save_or_raise(b / "run", PK, PS, b / "states")
    except Exception as e:  # noqa: BLE001 -- Belegfeld, kein Testverhalten
        d["current_error"] = repr(e)
    return d


def _phase_for(record: dict) -> str:
    if record["role"] == "community_creation_persona":
        return "persona"
    return "gm_final" if record["turn_idx"] == 1 else "gm_question"


def _legacy_finish_received_no_seconds(run, rid, *, usage=None, seconds=0.0, result_text=None):
    """A1-Fixture: Nachbau des Vorversions-`finish_received()` (vor R1) --
    schreibt KEIN `received_seconds`-Feld im ersten Write (dieses Feld gab
    es vor R1 noch nicht). Ruft denselben nachgelagerten `add_seconds`/
    `record_usd_delta`-Pfad wie die aktuelle Funktion auf -- ein echter
    Vorwriter-Nachbau (via `ledger`-Modulattribute, respektiert Patches auf
    `ledger.add_seconds`), keine hand-getippte Legacy-JSON."""
    data = ledger.load_request(run, rid)
    if data is None or data.get("state") == "accounted":
        return
    reserved_usd = data.get("reserved_usd")
    real_usd = ledger.compute_turn_usd(usage)
    delta = None
    if real_usd is not None and reserved_usd is not None and real_usd > reserved_usd:
        delta = real_usd - reserved_usd
    data["state"] = "received"
    data["usage"] = usage
    data["settled_ts"] = time.time()
    data["usd_reconciled"] = True
    data["result_text"] = result_text
    ledger._write_request(run, rid, data)
    ledger.add_seconds(run, rid, seconds)
    if delta is not None:
        ledger.record_usd_delta(run, rid, delta)
    data["state"] = "accounted"
    ledger._write_request(run, rid, data)


def _legacy_finish_received_no_text(run, rid, *, usage=None, seconds=0.0, result_text=None):
    """A2-Fixture: Nachbau des Vorversions-`finish_received()` (vor C2,
    10024452-Stand) -- schreibt KEIN `result_text`-Feld (dieses Feld gab es
    vor C2 noch nicht). Die Zeit-/Geldbuchung selbst laeuft normal durch --
    der reale historische Fehler bei diesem Altformat sitzt beim
    NACHGELAGERTEN lokalen Checkpoint-Write im Aufrufer (`onboarding.
    record_pending_reply`/`record_pending_answer`), nicht in dieser
    Funktion (s. REVIEW-COMMUNITY-ALTFORMAT.md §4)."""
    data = ledger.load_request(run, rid)
    if data is None or data.get("state") == "accounted":
        return
    reserved_usd = data.get("reserved_usd")
    real_usd = ledger.compute_turn_usd(usage)
    delta = None
    if real_usd is not None and reserved_usd is not None and real_usd > reserved_usd:
        delta = real_usd - reserved_usd
    data["state"] = "received"
    data["usage"] = usage
    data["settled_ts"] = time.time()
    data["usd_reconciled"] = True
    data.pop("result_text", None)
    data["received_seconds"] = seconds
    ledger._write_request(run, rid, data)
    ledger.add_seconds(run, rid, seconds)
    if delta is not None:
        ledger.record_usd_delta(run, rid, delta)
    data["state"] = "accounted"
    ledger._write_request(run, rid, data)


def _one(b: Path, mode: str, phase: str, action: str) -> dict:
    if action == "setup":
        _setup(b)
        return {"pid": os.getpid()}

    calls = {"gm": [], "persona": []}
    hits = []
    messages = []
    error = None
    result = None

    class GM:
        output_limit_tokens = 50

        def turn(self, idx, text, output_limit_tokens=None):
            calls["gm"].append({"idx": idx, "text": text})
            return {"content": ST if text == A else Q, "usage": {"usd": 0.05}}

    class Driver:
        config = None

        def decide(self, ctx):
            calls["persona"].append(ctx)
            return ParticipantDecision(text=A, origin_source="synthetic-altformat", meta={"usage": {"usd": 0.05}})

    orig_finish = ledger.finish_received
    orig_add = ledger.add_seconds
    orig_reply = onboarding.record_pending_reply
    orig_answer = onboarding.record_pending_answer
    legacy_active = [False]

    def finish(run, rid, **kw):
        r = ledger.load_request(run, rid)
        ph = _phase_for(r)
        kw["seconds"] = 2.0
        if mode == "a1" and ph == phase:
            legacy_active[0] = True
            try:
                return _legacy_finish_received_no_seconds(run, rid, **kw)
            finally:
                legacy_active[0] = False
        if mode == "a2" and ph == phase:
            return _legacy_finish_received_no_text(run, rid, **kw)
        return orig_finish(run, rid, **kw)

    def add(*args, **kwargs):
        if mode == "a1" and legacy_active[0] and not hits:
            hits.append({"seam": "ledger.add_seconds", "phase": phase})
            raise OSError("SYNTHETIC: legacy time-booking write failed once (A1 fixture)")
        return orig_add(*args, **kwargs)

    def reply(*args, **kwargs):
        ph = "gm_final" if kwargs.get("sl_reply") == ST else "gm_question"
        if mode == "a2" and ph == phase and not hits:
            hits.append({"seam": "onboarding.record_pending_reply", "phase": ph})
            raise OSError("SYNTHETIC: legacy local reply checkpoint failed once (A2 fixture)")
        return orig_reply(*args, **kwargs)

    def answer(*args, **kwargs):
        if mode == "a2" and phase == "persona" and not hits:
            hits.append({"seam": "onboarding.record_pending_answer", "phase": "persona"})
            raise OSError("SYNTHETIC: legacy local answer checkpoint failed once (A2 fixture)")
        return orig_answer(*args, **kwargs)

    with patch.object(ledger, "finish_received", finish), patch.object(ledger, "add_seconds", add), \
            patch.object(onboarding, "record_pending_reply", reply), \
            patch.object(onboarding, "record_pending_answer", answer):
        try:
            r = advance_one_persona_creation(
                run_dir=b / "run", states_dir=b / "states", schema_path=SCHEMA, onboarding_dir=b / "onboarding",
                catalog_dir=b / "catalog", community_id="altformat-community", generation=1, persona_key=PK,
                gm_transport_factory=lambda cid: GM(), persona_driver_factory=lambda pk: Driver(),
                print_fn=messages.append,
            )
            result = dataclasses.asdict(r)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            error = {"type": type(e).__name__, "message": str(e)}
    return {
        "pid": os.getpid(), "mode": mode, "phase": phase, "result": result, "error": error,
        "calls": calls, "hits": hits, "messages": messages, "disk": _snapshot(b),
    }


def _child(b: Path, mode: str = "none", phase: str = "none", action: str = "advance") -> dict:
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child", "--base", str(b),
        "--mode", mode, "--phase", phase, "--action", action,
    ]
    cp = subprocess.run(cmd, text=True, capture_output=True, timeout=40)
    if cp.returncode:
        raise RuntimeError(cp.stdout + "\n" + cp.stderr)
    return json.loads(cp.stdout)


# --- A1: unbekannte Originaldauer bleibt kontrolliert offen ----------------

def _a1_case(phase: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b, mode="a1", phase=phase)
        y = _child(b)
        assert len(x["hits"]) == 1, x
        assert x["error"] is not None, f"Legacy-Fixture muss den echten Fehler ungefangen propagieren: {x}"
        assert x["pid"] != y["pid"], "echter Prozessneustart erforderlich"
        legacy = [r for r in x["disk"]["records"] if _phase_for(r) == phase]
        assert len(legacy) == 1 and "received_seconds" not in legacy[0] and legacy[0]["state"] == "received", legacy
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "paused", (
            f"unbekannte Originaldauer darf nicht zu completed/already_ready fuehren "
            f"(phase={phase}): {y}"
        )
        assert not y["calls"]["gm"] and not y["calls"]["persona"], (
            f"unbekannte Originaldauer darf keinen abhaengigen Modellaufruf ausloesen "
            f"(phase={phase}): {y['calls']}"
        )
        after_legacy = [r for r in y["disk"]["records"] if _phase_for(r) == phase]
        assert len(after_legacy) == 1 and after_legacy[0]["state"] == "received", (
            f"der Alt-Record muss ehrlich `received` bleiben, kein erfundenes `accounted` "
            f"(phase={phase}): {after_legacy}"
        )
        assert "received_seconds" not in after_legacy[0], after_legacy


def test_a1_01_gm_question_unknown_duration_stays_open():
    _a1_case("gm_question")


def test_a1_02_persona_unknown_duration_stays_open():
    _a1_case("persona")


def test_a1_03_gm_final_unknown_duration_stays_open():
    _a1_case("gm_final")


def test_a1_04_real_zero_duration_remains_valid():
    """Gegenprobe zu Test 01-03: eine ECHT aufgezeichnete `0.0`-Dauer (PRAESENTER
    Schluessel mit Wert `0.0`, kein abwesender Schluessel) ist weiterhin eine
    gueltige bekannte Dauer -- `settle_received` muss sie normal settlen
    (Uebergang nach `accounted`), NICHT wie eine unbekannte Dauer blockieren.
    Direkter Funktionsaufruf (kein Subprozess noetig -- reiner Lese-/
    Entscheidungsvertrag von `settle_received`, echte `begin()`/
    `finish_received()`-Konstruktion, keine hand-getippte JSON)."""
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td) / "run"
        write_test_profile(rd, max_turns=10)
        rid = ledger.begin(
            rd, role="altformat_zero_probe", content="synthetic zero-duration", reserved_usd=0.01,
            table_id="zero-table", section_id="zero-section", turn_idx=0, participant="zero_persona",
        )
        # Realer erster Write mit echter Latenz 0.0 (kein Vorschaetzwert),
        # dann simulierter Fehler VOR dem zweiten Write (Uebergang nach
        # `accounted`) -- derselbe Zwischenzustand wie bei den Settlement-
        # Obligationstests, nur mit `seconds=0.0` statt `2.0`.
        orig_add = ledger.add_seconds

        def failing_add(*args, **kwargs):
            raise OSError("SYNTHETIC: one-shot booking failure right after the first write")

        with patch.object(ledger, "add_seconds", failing_add):
            try:
                ledger.finish_received(rd, rid, usage={"usd": 0.01}, seconds=0.0, result_text="SYNTHETIC zero")
                raise AssertionError("erwarteter synthetischer OSError blieb aus")
            except OSError:
                pass
        parked = ledger.load_request(rd, rid)
        assert parked["state"] == "received" and "received_seconds" in parked and parked["received_seconds"] == 0.0, parked

        settled = ledger.settle_received(rd, parked)
        assert settled["state"] == "accounted", (
            f"eine echte aufgezeichnete 0.0-Dauer ist gueltig und muss normal settlen, "
            f"nicht wie eine unbekannte Dauer blockieren: {settled}"
        )
        on_disk = ledger.load_request(rd, rid)
        assert on_disk["state"] == "accounted", on_disk


# --- A2: textloser bereits-beantworteter Alt-Record blockiert neue Anfrage -

def _a2_case(phase: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b, mode="a2", phase=phase)
        y = _child(b)
        assert len(x["hits"]) == 1, x
        assert x["error"] is not None, f"Legacy-Fixture muss den echten lokalen Checkpointfehler propagieren: {x}"
        assert x["pid"] != y["pid"], "echter Prozessneustart erforderlich"
        legacy = [r for r in x["disk"]["records"] if _phase_for(r) == phase]
        assert len(legacy) == 1 and legacy[0]["state"] == "accounted" and "result_text" not in legacy[0], legacy
        before_count = len(x["disk"]["records"])
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "paused", (
            f"textloser bereits beantworteter Alt-Record darf nicht zu completed/already_ready "
            f"fuehren (phase={phase}): {y}"
        )
        assert not y["calls"]["gm"] and not y["calls"]["persona"], (
            f"textloser bereits beantworteter Alt-Record darf keine neue Anfrage ausloesen "
            f"(phase={phase}): {y['calls']}"
        )
        after_count = len(y["disk"]["records"])
        assert after_count == before_count, (
            f"keine zweite Reservierung fuer dieselbe Operationsidentitaet -- Record-Zahl muss "
            f"unveraendert bleiben (phase={phase}): before={before_count} after={after_count}"
        )


def test_a2_01_gm_question_missing_text_blocks_new_request():
    _a2_case("gm_question")


def test_a2_02_persona_missing_text_blocks_new_request():
    _a2_case("persona")


def test_a2_03_gm_final_missing_text_blocks_new_request():
    _a2_case("gm_final")


def test_a2_04_unrelated_identity_not_blocked_by_foreign_textless_record():
    """Gegenprobe zu Test 01-03: KEIN universelles 'alle accounted IDs
    sperren' -- ein textloser Alt-Record fuer turn_idx=0 darf eine ANDERE
    Operationsidentitaet (anderer turn_idx) nicht blockieren. Direkter
    Funktionsaufruf gegen `find_answered_without_text` (echte `begin()`-
    Konstruktion, kein Subprozess noetig -- reiner Lesevertrag)."""
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td) / "run"
        write_test_profile(rd, max_turns=10)
        rid = ledger.begin(
            rd, role="altformat_foreign_probe", content="synthetic textless", reserved_usd=0.01,
            table_id="foreign-table", section_id="foreign-section", turn_idx=0, participant="foreign_persona",
        )
        p = rd / "requests" / f"{rid}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        data["state"] = "accounted"
        data["usage"] = {"usd": 0.01}
        data["settled_ts"] = 12345.0
        data["usd_reconciled"] = True
        data["received_seconds"] = 1.0
        data.pop("result_text", None)
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        same_identity = ledger.find_answered_without_text(
            rd, table_id="foreign-table", section_id="foreign-section", role="altformat_foreign_probe",
            turn_idx=0, participant="foreign_persona",
        )
        assert same_identity is not None and same_identity["id"] == rid, same_identity

        other_turn = ledger.find_answered_without_text(
            rd, table_id="foreign-table", section_id="foreign-section", role="altformat_foreign_probe",
            turn_idx=1, participant="foreign_persona",
        )
        assert other_turn is None, (
            f"ein fremder textloser Alt-Record (andere Operationsidentitaet) darf eine neue "
            f"Anfrage fuer turn_idx=1 nicht blockieren: {other_turn}"
        )
        other_participant = ledger.find_answered_without_text(
            rd, table_id="foreign-table", section_id="foreign-section", role="altformat_foreign_probe",
            turn_idx=0, participant="someone_else",
        )
        assert other_participant is None, other_participant


def main() -> int:
    tests = [
        test_a1_01_gm_question_unknown_duration_stays_open,
        test_a1_02_persona_unknown_duration_stays_open,
        test_a1_03_gm_final_unknown_duration_stays_open,
        test_a1_04_real_zero_duration_remains_valid,
        test_a2_01_gm_question_missing_text_blocks_new_request,
        test_a2_02_persona_missing_text_blocks_new_request,
        test_a2_03_gm_final_missing_text_blocks_new_request,
        test_a2_04_unrelated_identity_not_blocked_by_foreign_textless_record,
    ]
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
    if "--child" in sys.argv:
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("--child", action="store_true")
        p.add_argument("--base", type=Path, required=True)
        p.add_argument("--mode", default="none")
        p.add_argument("--phase", default="none")
        p.add_argument("--action", default="advance")
        args = p.parse_args()
        print(json.dumps(_one(args.base, args.mode, args.phase, args.action)))
        raise SystemExit(0)
    raise SystemExit(main())
