#!/usr/bin/env python3
"""
tests/mmo_sim/test_a1rest_pending_settlement_real_subprocess.py — dauerhafte
Regressionstests fuer den A1-Rest (Altformat-Recovery-Nachzug 2026-09-26,
MAIN-DATENWEGENTSCHEIDUNG.md A1-Rest, REVIEW-COMMUNITY-PENDING.md §4).
Adaptiert aus der einmaligen Paket-Probe `tests-review/review_legacy_pending_
steps.py` (Ausgangsbefund dort: 2 PASS/3 FAIL) in dauerhafte In-Repo-Tests,
repo-uebliche `main()`/Exitcode-Form, echter Subprozessneustart (kein neues
Objekt im selben Interpreter).

Der A1-Fix in `request_ledger.settle_received` (unbekannte Originaldauer
bleibt offen) UND die A1/A2-Guards HINTER `find_durable_result()` (getestet
in `test_altformat_recovery_a1_a2_real_subprocess.py`) betreffen nur den
DIREKT aus dem Ledger gefundenen Weg. `core.creation_service.run_admitted_
creation_dialog` hat einen ZWEITEN, vorgeschalteten Wiederaufnahmeweg: einen
bereits lokal gespeicherten `onboarding.pending_step` (`sl_reply`/
`persona_answer`), der bisher NICHT auf dieselbe Settlementvoraussetzung
(`_settle_pending_or_hold`) geprueft wurde, bevor sein Text als erledigte
Voraussetzung fuer Cursorfortschritt/`complete_with_save`/`record_step`
weiterverwendet wird -- genau das ist der A1-Rest, den dieser Fix schliesst.

Test 01-03 (negativ, je eine der drei Ergebnisarten SL-Frage/Personaantwort/
Erstsave): `_setup_pending_negative` (unten) baut den Ausgangszustand nach,
den ein echter Vorversions-Writer (vor R1, `received`-Record OHNE
`received_seconds`, `onboarding.pending_step` referenziert dessen Request-ID
bereits) hinterlassen haben muss -- ausschliesslich ueber ECHTE
Produktprimitiven (`request_ledger.begin()`, `onboarding.record_pending_
reply`/`record_pending_answer`), kein amputierter aktueller Record (derselbe
Nachbauvertrag wie `test_r1r2_received_settlement_obligations.py:test_05`
fuer den Ledger-Record selbst, hier zusaetzlich auf den bereits lokal
gespeicherten `pending_step` ausgeweitet). Diese Kombination ist mit reinem
AKTUELLEM Code nicht mehr organisch reproduzierbar: der bestehende A1-Guard
hinter `find_durable_result()` blockiert eine unbekannte Dauer bereits, BEVOR
`record_pending_reply`/`record_pending_answer` je aufgerufen wird -- exakt
das war der Ausgangsbefund der Paket-Probe (2 PASS/3 FAIL, s.o.) und ist
kein Widerspruch: der lokale `pending_step` KANN diese Kombination bereits
lange VOR diesem Review-Zeitpunkt gespeichert haben (echter alter Writer,
Vorversions-Aufruferreihenfolge). Ein echter Prozessneustart MUSS danach
kontrolliert offen bleiben (kein `completed`, kein weiterer Modellaufruf,
Records/Budget unveraendert) -- nicht den gespeicherten Text blind
weiterverwenden.

Test 04-06 (positiv, alle drei Ergebnisarten): dieselbe Einfrierstelle,
aber mit einem regulaer VOLLSTAENDIG abgerechneten (`accounted`) Record --
der Dialog MUSS nach dem Fix normal weiterlaufen, ohne doppelte Anfragen.

Test 07 (positiv): ein alter, bereits `accounted`er Record OHNE `result_text`
(Nachbau via `_legacy_finish_received_no_text`, wie in `test_altformat_
recovery_a1_a2_real_subprocess.py`) bleibt nutzbar, solange der lokale
`pending_step` selbst noch den gueltigen Text traegt (test_05-Aequivalent
aus der Paket-Probe).

Test 08 (positiv): der menschliche Antwortgeber (`persona_request_id is
None`, kein eigener Modellrequest) wird von der neuen Guard-Pruefung NICHT
blockiert -- direkter Aufruf von `core.creation_service.run_admitted_
creation_dialog` mit einem menschenaehnlichen `get_reply` (analog `ui/tui.
py:_human_get_reply`), keine Community-/Persona-Schicht noetig.

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
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_one_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PS = PersonaStateStore(schema_path=SCHEMA)
PK = "a1rest_persona"
Q = "SYNTHETIC: Welche Ausruestung waehlst du?"
A = "SYNTHETIC: Ich waehle leichte Ruestung."
SAVE = {"v": 7, "save_id": "SYNTHETIC-A1REST-SAVE",
        "characters": [{"char_id": "SYNTHETIC-A1REST-CHR", "name": "Synthetic", "callsign": "A1REST", "level": 1}]}
ST = "```json\n" + json.dumps(SAVE) + "\n```"


def _setup_community(b: Path) -> None:
    draft = {
        "real_name": "Synthetic A1-Rest", "archetype": "SYNTHETIC_ARCH", "play_style": "SYNTHETIC_STYLE",
        "charwunsch": "SYNTHETIC_WISH",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
    }
    bootstrap_community(b / "run/community", "a1rest-community", 1, {PK: draft}, PS, b / "states", "2026-09-25")
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
    ob = onboarding.peek(b / "onboarding", PK)
    d["onboarding"] = dataclasses.asdict(ob) if ob else None
    return d


def _phase_for(record: dict) -> str:
    if record["role"] == "community_creation_persona":
        return "persona"
    return "gm_final" if record["turn_idx"] == 1 else "gm_question"


def _legacy_finish_received_no_text(run, rid, *, usage=None, seconds=0.0, result_text=None):
    """A2-Fixture (identisch zum Nachbau in `test_altformat_recovery_a1_a2_
    real_subprocess.py`): Nachbau des Vorversions-`finish_received()` (vor
    C2) -- schreibt KEIN `result_text`-Feld, aber `received_seconds` normal;
    die Buchung selbst laeuft vollstaendig durch (`state=accounted`)."""
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


def _setup_pending_negative(b: Path, phase: str) -> dict:
    """Baut den Ausgangszustand fuer Test 01-03 nach: ein `onboarding.
    pending_step`, der bereits eine Request-ID traegt, deren Ledger-Record
    dauerhaft bei `state=received` OHNE `received_seconds` haengt (Vor-R1-
    Schema) -- exakt die Kombination, die ein echter alter Writer
    hinterlassen haben muss. Verwendet ausschliesslich echte
    Produktprimitiven (`request_ledger.begin()`/`finish_received()`,
    `onboarding.record_pending_reply`/`record_pending_answer`); der
    unbekannte-Dauer-Record wird NICHT durch einen laufenden Dialog erzeugt
    (der bestehende A1-Guard hinter `find_durable_result()` wuerde diese
    Kombination im AKTUELLEN Code bereits VOR dem lokalen Checkpoint-Write
    verhindern, s. Moduldocstring), sondern direkt geschrieben -- derselbe
    Nachbauvertrag wie `test_r1r2_received_settlement_obligations.py:
    test_05` fuer den Ledger-Record selbst, hier zusaetzlich auf den
    lokalen `pending_step` ausgeweitet. KEIN amputierter aktueller Record:
    alle Pflichtfelder stammen aus einem echten `begin()`-Aufruf, nur die
    Vor-R1-Feldform (`received_seconds` abwesend) wird nachgebaut."""
    _setup_community(b)
    onboarding.start_or_resume(b / "onboarding", PK)
    stuck_role = "community_creation_persona" if phase == "persona" else "community_creation_gm"
    stuck_text = ST if phase == "gm_final" else (A if phase == "persona" else Q)
    stuck_rid = ledger.begin(
        b / "run", role=stuck_role, content=stuck_text, reserved_usd=0.001,
        table_id="a1rest-community", section_id="gen1", turn_idx=0, participant=PK,
    )
    p = b / "run/requests" / f"{stuck_rid}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["state"] = "received"
    data["usage"] = {"usd": 0.05}
    data["settled_ts"] = 12345.0
    data["usd_reconciled"] = True
    data["result_text"] = stuck_text
    data.pop("received_seconds", None)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    if phase == "persona":
        gm_rid = ledger.begin(
            b / "run", role="community_creation_gm", content="SYNTHETIC: initial", reserved_usd=0.001,
            table_id="a1rest-community", section_id="gen1", turn_idx=0, participant=PK,
        )
        ledger.finish_received(b / "run", gm_rid, usage={"usd": 0.05}, seconds=2.0, result_text=Q)
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=Q, sl_request_id=gm_rid)
        onboarding.record_pending_answer(b / "onboarding", PK, persona_answer=A, persona_request_id=stuck_rid)
    else:
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=stuck_text, sl_request_id=stuck_rid)
    return {"pid": os.getpid(), "stuck_id": stuck_rid, "disk": _snapshot(b)}


def _one(b: Path, action: str, *, fixture: str = "none", interrupt: bool = False, phase: str = "none") -> dict:
    """Gemeinsamer Kern fuer Test 04-07 (Community-/Persona-Antwortgeber;
    Test 01-03 nutzen `_setup_pending_negative` statt dieser Funktion, s.
    dort). `fixture`: 'none' (aktueller Code, normal accounted) | 'no_text'
    (A2-Fixture, wird `accounted` OHNE `result_text`) -- greift NUR fuer den
    Request der angegebenen `phase`. `interrupt`: friert den Dialog GENAU an
    diesem Pending-Schritt ein (Driver-Fehler fuer 'gm_question', `record_
    step`-Fehler fuer 'persona', `complete_with_save`-Fehler fuer
    'gm_final') -- derselbe reale Fehlerpfad wie in `review_legacy_pending_
    steps.py`."""
    if action == "setup":
        _setup_community(b)
        return {"pid": os.getpid()}

    if action == "setup_pending_negative":
        return _setup_pending_negative(b, phase)

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
            if interrupt and phase == "gm_question" and not hits:
                hits.append({"seam": "persona_driver.decide", "phase": "gm_question"})
                raise RuntimeError(
                    "SYNTHETIC: persona transport failed; SL-Frage bereits als pending_step "
                    "checkpointet"
                )
            return ParticipantDecision(text=A, origin_source="synthetic-a1rest", meta={"usage": {"usd": 0.05}})

    orig_finish = ledger.finish_received
    orig_step = onboarding.record_step
    orig_complete = onboarding.complete_with_save

    def finish(run, rid, **kw):
        r = ledger.load_request(run, rid)
        ph = _phase_for(r)
        kw["seconds"] = 2.0
        if fixture == "no_text" and ph == phase:
            return _legacy_finish_received_no_text(run, rid, **kw)
        return orig_finish(run, rid, **kw)

    def step(*args, **kwargs):
        if interrupt and phase == "persona" and not hits:
            hits.append({"seam": "onboarding.record_step", "phase": "persona"})
            raise OSError("SYNTHETIC: step application failed after pending answer was checkpointed")
        return orig_step(*args, **kwargs)

    def complete(*args, **kwargs):
        if interrupt and phase == "gm_final" and not hits:
            hits.append({"seam": "onboarding.complete_with_save", "phase": "gm_final"})
            raise OSError("SYNTHETIC: completion failed after pending final save was checkpointed")
        return orig_complete(*args, **kwargs)

    with patch.object(ledger, "finish_received", finish), \
            patch.object(onboarding, "record_step", step), \
            patch.object(onboarding, "complete_with_save", complete):
        try:
            r = advance_one_persona_creation(
                run_dir=b / "run", states_dir=b / "states", schema_path=SCHEMA, onboarding_dir=b / "onboarding",
                catalog_dir=b / "catalog", community_id="a1rest-community", generation=1, persona_key=PK,
                gm_transport_factory=lambda cid: GM(), persona_driver_factory=lambda pk: Driver(),
                print_fn=messages.append,
            )
            result = dataclasses.asdict(r)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            error = {"type": type(e).__name__, "message": str(e)}
    return {
        "pid": os.getpid(), "fixture": fixture, "interrupt": interrupt, "phase": phase,
        "result": result, "error": error, "calls": calls, "hits": hits, "messages": messages,
        "disk": _snapshot(b),
    }


def _child(b: Path, action: str = "advance", *, fixture: str = "none", interrupt: bool = False,
           phase: str = "none") -> dict:
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child", "--base", str(b), "--action", action,
        "--fixture", fixture, "--phase", phase,
    ]
    if interrupt:
        cmd.append("--interrupt")
    cp = subprocess.run(cmd, text=True, capture_output=True, timeout=40)
    if cp.returncode:
        raise RuntimeError(cp.stdout + "\n" + cp.stderr)
    return json.loads(cp.stdout)


# --- Test 01-03: negativ -- unbekannte Originaldauer am Pending-Schritt bleibt offen

def _neg_case(phase: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        x = _child(b, action="setup_pending_negative", phase=phase)
        y = _child(b)
        z = _child(b)
        assert x["pid"] != y["pid"] != z["pid"], "echter Prozessneustart erforderlich"
        pending = x["disk"]["onboarding"]["pending_step"]
        assert pending is not None, x
        key = "persona_request_id" if phase == "persona" else "sl_request_id"
        assert pending[key] == x["stuck_id"], pending
        legacy = next(rec for rec in x["disk"]["records"] if rec["id"] == x["stuck_id"])
        assert legacy["state"] == "received" and "received_seconds" not in legacy, (
            f"Nachbau muss einen echten Vor-R1-Record (received, keine Dauer) hinterlassen: {legacy}"
        )
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "paused", (
            f"gespeicherter Pending-Schritt mit unbekannter Originaldauer darf nicht zu "
            f"completed/already_ready fuehren (phase={phase}): {y}"
        )
        assert y["result"].get("reason") == "altformat_unresolved_pending_settlement", y
        assert not y["calls"]["gm"] and not y["calls"]["persona"], (
            f"unbekannte Originaldauer am Pending-Schritt darf keinen weiteren Modellaufruf "
            f"ausloesen (phase={phase}): {y['calls']}"
        )
        assert y["disk"].get("current") is None, y
        assert y["disk"]["records"] == x["disk"]["records"], (
            "kein stiller Buchungs-/Recordwechsel waehrend der kontrollierten Sperre"
        )
        assert y["disk"]["budget"] == x["disk"]["budget"]
        assert z["disk"].get("current") is None and not z["calls"]["gm"] and not z["calls"]["persona"], (
            f"erneuter Aufruf des geblockten Zustands darf keine neuen Requests/Buchungen ausloesen: {z}"
        )


def test_01_gm_question_pending_unknown_duration_stays_open():
    _neg_case("gm_question")


def test_02_persona_answer_pending_unknown_duration_stays_open():
    _neg_case("persona")


def test_03_final_save_pending_unknown_duration_stays_open():
    _neg_case("gm_final")


# --- Test 04-06: positiv -- vollstaendig abgerechneter Pendingtext laeuft weiter

def _healthy_case(phase: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b, fixture="none", interrupt=True, phase=phase)
        y = _child(b)
        z = _child(b)
        assert len(x["hits"]) == 1, x
        assert x["pid"] != y["pid"] != z["pid"], "echter Prozessneustart erforderlich"
        assert x["disk"]["onboarding"]["pending_step"] is not None, x
        assert y["error"] is None, y
        assert y["disk"]["current"] == SAVE, y
        assert all(v["state"] == "accounted" for v in y["disk"]["records"]), y
        expected = {"gm_question": (1, 1), "persona": (1, 0), "gm_final": (0, 0)}[phase]
        assert (len(y["calls"]["gm"]), len(y["calls"]["persona"])) == expected, (
            f"phase={phase}: erwartet {expected}, erhalten "
            f"({len(y['calls']['gm'])}, {len(y['calls']['persona'])})"
        )
        assert not z["calls"]["gm"] and not z["calls"]["persona"], (
            "requestfreier Reentry nach Abschluss"
        )


def test_04_healthy_pending_gm_question_continues_without_duplicate_calls():
    _healthy_case("gm_question")


def test_05_healthy_pending_persona_answer_continues_without_duplicate_calls():
    _healthy_case("persona")


def test_06_healthy_pending_final_save_continues_without_duplicate_calls():
    _healthy_case("gm_final")


# --- Test 07: positiv -- Alt-accounted ohne result_text + gueltiger Pendingtext bleibt nutzbar

def test_07_textless_accounted_pending_text_stays_usable():
    phase = "gm_question"
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b, fixture="no_text", interrupt=True, phase=phase)
        y = _child(b)
        assert len(x["hits"]) == 1, x
        assert x["disk"]["onboarding"]["pending_step"] is not None, x
        legacy = [rec for rec in x["disk"]["records"] if "result_text" not in rec]
        assert legacy and all(rec["state"] == "accounted" for rec in legacy), (
            f"Fixture muss einen echten Vor-C2-Record (accounted, kein result_text) hinterlassen: {x}"
        )
        assert y["error"] is None, y
        assert y["disk"]["current"] == SAVE, (
            f"ein bereits accounted Alt-Record ohne result_text darf den gueltigen lokal "
            f"gespeicherten Pendingtext nicht blockieren: {y}"
        )
        assert all(v["state"] == "accounted" for v in y["disk"]["records"]), y
        expected = {"gm_question": (1, 1), "persona": (1, 0), "gm_final": (0, 0)}[phase]
        assert (len(y["calls"]["gm"]), len(y["calls"]["persona"])) == expected, y


# --- Test 08: positiv -- menschlicher n-Pfad (kein Modellrequest) nicht blockiert

def _human_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    return ReplyResult(kind="answer", text=A)


def _one_human(b: Path, action: str, *, interrupt: bool = False) -> dict:
    if action == "setup":
        write_test_profile(b / "run", max_turns=100, max_usd=10)
        onboarding.start_or_resume(b / "onboarding", PK)
        return {"pid": os.getpid()}

    calls = {"gm": [], "human": []}
    hits = []
    messages = []
    error = None
    result = None

    class GM:
        output_limit_tokens = 50

        def turn(self, idx, text, output_limit_tokens=None):
            calls["gm"].append({"idx": idx, "text": text})
            return {"content": ST if text == A else Q, "usage": {"usd": 0.05}}

    def get_reply(turn_idx, sl_text):
        calls["human"].append({"turn_idx": turn_idx, "sl_text": sl_text})
        return _human_get_reply(turn_idx, sl_text)

    orig_step = onboarding.record_step

    def step(*args, **kwargs):
        if interrupt and not hits:
            hits.append({"seam": "onboarding.record_step", "phase": "human"})
            raise OSError("SYNTHETIC: step application failed after human answer was checkpointed")
        return orig_step(*args, **kwargs)

    with patch.object(onboarding, "record_step", step):
        try:
            out = run_admitted_creation_dialog(
                run_dir=b / "run", onboarding_dir=b / "onboarding", participant_id=PK,
                turn_idx_start=0, initial_outgoing="SYNTHETIC: Ich moechte einen Chrononauten erschaffen.",
                gm_transport=GM(), get_reply=get_reply, harvest_validator=ZeitrissHarvestValidator(),
                print_fn=messages.append, role="creation_dialog",
            )
            result = dataclasses.asdict(out)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            error = {"type": type(e).__name__, "message": str(e)}
    ob = onboarding.peek(b / "onboarding", PK)
    return {
        "pid": os.getpid(), "interrupt": interrupt, "result": result, "error": error, "calls": calls,
        "hits": hits, "messages": messages,
        "onboarding": dataclasses.asdict(ob) if ob else None,
        "records": [json.loads(f.read_text()) for f in sorted((b / "run/requests").glob("*.json"))],
    }


def _child_human(b: Path, action: str = "advance", *, interrupt: bool = False) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--base", str(b), "--human", "--action", action]
    if interrupt:
        cmd.append("--interrupt")
    cp = subprocess.run(cmd, text=True, capture_output=True, timeout=40)
    if cp.returncode:
        raise RuntimeError(cp.stdout + "\n" + cp.stderr)
    return json.loads(cp.stdout)


def test_08_human_answer_pending_not_blocked_by_settlement_guard():
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child_human(b, action="setup")
        x = _child_human(b, interrupt=True)
        y = _child_human(b)
        assert len(x["hits"]) == 1, x
        assert x["error"] is not None and x["error"]["type"] == "OSError", (
            f"echter lokaler Checkpointfehler muss ungefangen propagieren: {x}"
        )
        assert x["pid"] != y["pid"], "echter Prozessneustart erforderlich"
        pending = x["onboarding"]["pending_step"]
        assert pending is not None and pending["persona_answer"] == A, x
        assert pending["persona_request_id"] is None, (
            f"menschliche Antwort hat KEINEN eigenen Modellrequest (n-Pfad): {pending}"
        )
        sl_record = next(rec for rec in x["records"] if rec["id"] == pending["sl_request_id"])
        assert sl_record["state"] == "accounted", sl_record
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "completed", (
            f"persona_request_id=None (menschlicher n-Pfad) darf die neue Settlement-Guard-Pruefung "
            f"nicht blockieren -- der Dialog muss normal bis zum Save weiterlaufen: {y}"
        )
        assert len(y["calls"]["gm"]) == 1 and not y["calls"]["human"], (
            f"kein erneuter SL-Request fuer den bereits gespeicherten Pending-Schritt, aber der "
            f"naechste ECHTE Turn (Erstsave) muss normal stattfinden: {y}"
        )


def main() -> int:
    tests = [
        test_01_gm_question_pending_unknown_duration_stays_open,
        test_02_persona_answer_pending_unknown_duration_stays_open,
        test_03_final_save_pending_unknown_duration_stays_open,
        test_04_healthy_pending_gm_question_continues_without_duplicate_calls,
        test_05_healthy_pending_persona_answer_continues_without_duplicate_calls,
        test_06_healthy_pending_final_save_continues_without_duplicate_calls,
        test_07_textless_accounted_pending_text_stays_usable,
        test_08_human_answer_pending_not_blocked_by_settlement_guard,
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
        p.add_argument("--action", default="advance")
        p.add_argument("--fixture", default="none")
        p.add_argument("--phase", default="none")
        p.add_argument("--interrupt", action="store_true")
        p.add_argument("--human", action="store_true")
        args = p.parse_args()
        if args.human:
            print(json.dumps(_one_human(args.base, args.action, interrupt=args.interrupt)))
        else:
            print(json.dumps(_one(
                args.base, args.action, fixture=args.fixture, interrupt=args.interrupt, phase=args.phase,
            )))
        raise SystemExit(0)
    raise SystemExit(main())
