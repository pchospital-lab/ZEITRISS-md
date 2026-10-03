#!/usr/bin/env python3
"""
tests/mmo_sim/test_pending_authority_missing_record_real_subprocess.py —
dauerhafte Regressionstests fuer den P2-Community-Pending-Autoritaetsnachzug
(2026-09-26, MAIN-DATENWEGENTSCHEIDUNG.md "Pending-Autoritaetsnachzug",
REVIEW-COMMUNITY-PENDING-AUTORITAET.md §3).

Scope: GENAU der eine korrigierte Zweig in `core.creation_service.
_settle_pending_or_hold` -- vorher `if record is None: return True`, jetzt
`if record is None: return False`. Ein bereits lokal gespeicherter
`onboarding.pending_step` (`sl_reply`/`persona_answer`) traegt eine
AUSDRUECKLICH vorhandene Request-ID (`sl_request_id`/`persona_request_id`).
Ist deren verknuepfter Ledger-Datensatz gerade NICHT verfuegbar (Datei
geloescht/verschoben -- `request_ledger.load_request` liefert `None`, weil
`Path.exists()` `False` liefert), ist das etwas anderes als der ERSTE Zweig
(`request_id is None`, echter menschlicher Antwortgeber ohne eigenen
Modellrequest): ein bereits bekannter Modellauftrag, dessen Datensatz
gerade nicht erhaeltlich ist, darf NICHT wie eine erledigte menschliche
Antwort behandelt werden. Dieser Fix schliesst diese Luecke fuer BEIDE
Guard-Aufrufstellen (SL-Frage/Erstsave UND Personaantwort in
`run_admitted_creation_dialog`), da beide denselben Helfer nutzen.

Test 01-03 (negativ, je eine der drei Ergebnisarten SL-Frage/Personaantwort/
Erstsave): `_setup_known_id_missing` baut -- ausschliesslich ueber ECHTE
Produktprimitiven (`request_ledger.begin()`/`finish_received()`,
`onboarding.record_pending_reply`/`record_pending_answer`) -- einen
`pending_step`, dessen referenzierte Request-ID einen reell `accounted`en
Ledger-Record hat. Die Testfunktion selbst (NICHT die Fixture) entfernt
danach GENAU DIESE eine Datei (echtes `Path.rename()` in ein separates
Retain-Verzeichnis, bytegleich) -- ein neuer Prozess darf das nicht als
Freigabe behandeln: kein Cursorfortschritt, kein `completed`, kein weiterer
Modell-/Personaaufruf. Danach wird dieselbe Datei bytegleich zurueckgelegt
("nach Wiederherstellung derselben Datei normal erneut pruefen (kein
Dauerverbot)", MAIN-DATENWEGENTSCHEIDUNG.md §C) -- ein weiterer neuer
Prozess muss danach normal (ohne Sperre, ohne neuen Modellaufruf fuer
diesen bereits abgerechneten Schritt) weiterlaufen.

Test 04 (positiv, Erhalt): der menschliche Antwortgeber
(`persona_request_id is None`, kein eigener Modellrequest) wird vom
korrigierten Guard weiterhin NICHT blockiert -- direkter Aufruf von
`core.creation_service.run_admitted_creation_dialog` mit einem
menschenaehnlichen `get_reply` (analog `ui/tui.py:_human_get_reply` und
`test_a1rest_pending_settlement_real_subprocess.py:test_08`).

Test 05 (positiv, Erhalt): ein bereits gespeicherter Pending-Schritt mit
einer noch NICHT `accounted`en, aber vollstaendigen `received`-Autoritaet
(`received_seconds` VORHANDEN) wird beim naechsten Aufruf GENAU EINMAL
ueber `settle_received` fertig gebucht (`accounted`) und der Dialog laeuft
normal weiter -- keine Datei fehlt hier, dies ist die dritte Zeile der
MAIN-Fallunterscheidungstabelle ("`received`, `received_seconds`
vorhanden" -> True), nicht der hier gefixte Zweig selbst, aber Teil
desselben Helfers und deshalb hier als Erhalt mitgeprueft.

Testdoubles ausschliesslich an Modell-/Fehlerstellen (Response-Doubles je
Kindprozess, echte neue PIDs), keine echte Modellbinary/Anbieterroute,
kein Netzwerk, kein HTTP."""
from __future__ import annotations

import dataclasses
import hashlib
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
PK = "pending_authority_persona"
COMMUNITY_ID = "pending-authority-community"
GENERATION = 1
SECTION_ID = f"gen{GENERATION}"
Q = "SYNTHETIC: Welche Ausruestung waehlst du?"
A = "SYNTHETIC: Ich waehle leichte Ruestung."
SAVE = {"v": 7, "save_id": "SYNTHETIC-PENDAUTH-SAVE",
        "characters": [{"char_id": "SYNTHETIC-PENDAUTH-CHR", "name": "Synthetic", "callsign": "PENDAUTH", "level": 1}]}
ST = "```json\n" + json.dumps(SAVE) + "\n```"


def _setup_community(b: Path) -> None:
    draft = {
        "real_name": "Synthetic Pending-Authority", "archetype": "SYNTHETIC_ARCH", "play_style": "SYNTHETIC_STYLE",
        "charwunsch": "SYNTHETIC_WISH",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
    }
    bootstrap_community(b / "run/community", COMMUNITY_ID, GENERATION, {PK: draft}, PS, b / "states", "2026-09-26")
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


def _setup_known_id_missing(b: Path, phase: str) -> dict:
    """Baut einen `onboarding.pending_step`, dessen `sl_request_id`/
    `persona_request_id` auf einen REELL `accounted`en Ledger-Record
    verweist -- ausschliesslich ueber echte Produktprimitiven, kein
    amputierter Record. Die Datei bleibt an ihrem regulaeren Pfad; das
    ENTFERNEN passiert bewusst NICHT hier, sondern in der aufrufenden
    Testfunktion (echtes `Path.rename()` zwischen zwei Subprozessaufrufen,
    s. Moduldocstring)."""
    _setup_community(b)
    onboarding.start_or_resume(b / "onboarding", PK)
    stuck_role = "community_creation_persona" if phase == "persona" else "community_creation_gm"
    stuck_text = ST if phase == "gm_final" else (A if phase == "persona" else Q)
    stuck_rid = ledger.begin(
        b / "run", role=stuck_role, content=stuck_text, reserved_usd=0.001,
        table_id=COMMUNITY_ID, section_id=SECTION_ID, turn_idx=0, participant=PK,
    )
    ledger.finish_received(b / "run", stuck_rid, usage={"usd": 0.05}, seconds=2.0, result_text=stuck_text)
    if phase == "persona":
        gm_rid = ledger.begin(
            b / "run", role="community_creation_gm", content="SYNTHETIC: initial", reserved_usd=0.001,
            table_id=COMMUNITY_ID, section_id=SECTION_ID, turn_idx=0, participant=PK,
        )
        ledger.finish_received(b / "run", gm_rid, usage={"usd": 0.05}, seconds=2.0, result_text=Q)
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=Q, sl_request_id=gm_rid)
        onboarding.record_pending_answer(b / "onboarding", PK, persona_answer=A, persona_request_id=stuck_rid)
    else:
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=stuck_text, sl_request_id=stuck_rid)
    record = ledger.load_request(b / "run", stuck_rid)
    assert record is not None and record.get("state") == "accounted", (
        f"Fixture muss einen reell accounted Record hinterlassen, BEVOR er entfernt wird: {record}"
    )
    return {"pid": os.getpid(), "stuck_id": stuck_rid, "disk": _snapshot(b)}


def _setup_known_id_received_with_seconds(b: Path, phase: str) -> dict:
    """Wie `_setup_known_id_missing`, aber die Datei bleibt vorhanden UND
    traegt eine VOLLSTAENDIGE `received`-Autoritaet (`received_seconds`
    PRAESENT, aber `state` noch nicht `accounted` -- ein Aufrufer, der
    zwischen dem ersten `finish_received()`-Write und der nachgelagerten
    Kosten-/Latenzbuchung abgebrochen ist, s. `settle_received`-Docstring).
    Nachbau per direktem Feld-Edit auf einen echten `begin()`-Record --
    KEIN amputierter Pflichtschluessel."""
    _setup_community(b)
    onboarding.start_or_resume(b / "onboarding", PK)
    stuck_role = "community_creation_persona" if phase == "persona" else "community_creation_gm"
    stuck_text = ST if phase == "gm_final" else (A if phase == "persona" else Q)
    stuck_rid = ledger.begin(
        b / "run", role=stuck_role, content=stuck_text, reserved_usd=0.001,
        table_id=COMMUNITY_ID, section_id=SECTION_ID, turn_idx=0, participant=PK,
    )
    p = b / "run/requests" / f"{stuck_rid}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["state"] = "received"
    data["usage"] = {"usd": 0.05}
    data["settled_ts"] = time.time()
    data["usd_reconciled"] = False
    data["result_text"] = stuck_text
    data["received_seconds"] = 2.0
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    if phase == "persona":
        gm_rid = ledger.begin(
            b / "run", role="community_creation_gm", content="SYNTHETIC: initial", reserved_usd=0.001,
            table_id=COMMUNITY_ID, section_id=SECTION_ID, turn_idx=0, participant=PK,
        )
        ledger.finish_received(b / "run", gm_rid, usage={"usd": 0.05}, seconds=2.0, result_text=Q)
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=Q, sl_request_id=gm_rid)
        onboarding.record_pending_answer(b / "onboarding", PK, persona_answer=A, persona_request_id=stuck_rid)
    else:
        onboarding.record_pending_reply(b / "onboarding", PK, sl_reply=stuck_text, sl_request_id=stuck_rid)
    record = ledger.load_request(b / "run", stuck_rid)
    assert record is not None and record.get("state") == "received" and "received_seconds" in record, (
        f"Fixture muss einen echten, noch nicht abgerechneten received-Record mit bekannter "
        f"Dauer hinterlassen: {record}"
    )
    return {"pid": os.getpid(), "stuck_id": stuck_rid, "disk": _snapshot(b)}


def _one(b: Path, action: str, *, phase: str = "none") -> dict:
    if action == "setup":
        _setup_community(b)
        return {"pid": os.getpid()}
    if action == "setup_missing":
        return _setup_known_id_missing(b, phase)
    if action == "setup_received_seconds":
        return _setup_known_id_received_with_seconds(b, phase)

    calls = {"gm": [], "persona": []}
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
            return ParticipantDecision(text=A, origin_source="synthetic-pending-authority", meta={"usage": {"usd": 0.05}})

    try:
        r = advance_one_persona_creation(
            run_dir=b / "run", states_dir=b / "states", schema_path=SCHEMA, onboarding_dir=b / "onboarding",
            catalog_dir=b / "catalog", community_id=COMMUNITY_ID, generation=GENERATION, persona_key=PK,
            gm_transport_factory=lambda cid: GM(), persona_driver_factory=lambda pk: Driver(),
        )
        result = dataclasses.asdict(r)
    except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
        error = {"type": type(e).__name__, "message": str(e)}
    return {
        "pid": os.getpid(), "phase": phase, "result": result, "error": error, "calls": calls,
        "disk": _snapshot(b),
    }


def _child(b: Path, action: str = "advance", *, phase: str = "none") -> dict:
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child", "--base", str(b), "--action", action,
        "--phase", phase,
    ]
    cp = subprocess.run(cmd, text=True, capture_output=True, timeout=40)
    if cp.returncode:
        raise RuntimeError(cp.stdout + "\n" + cp.stderr)
    return json.loads(cp.stdout)


# --- Test 01-03: negativ -- bekannte Request-ID, deren Record-Datei fehlt


def _missing_case(phase: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        x = _child(b, action="setup_missing", phase=phase)
        stuck_id = x["stuck_id"]
        target = b / "run/requests" / f"{stuck_id}.json"
        original_sha = hashlib.sha256(target.read_bytes()).hexdigest()
        retain = b / "retained" / target.name
        retain.parent.mkdir()
        target.rename(retain)
        assert not target.exists(), "Fixture muss die Datei tatsaechlich entfernen"

        y = _child(b, phase=phase)
        assert y["pid"] != x["pid"], "echter Prozessneustart erforderlich"
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "paused", (
            f"eine bekannte Request-ID mit fehlender/nicht verfuegbarer Record-Datei darf "
            f"NICHT wie der menschliche n-Pfad zu completed/already_ready fuehren "
            f"(phase={phase}): {y}"
        )
        assert y["result"].get("reason") == "altformat_unresolved_pending_settlement", y
        assert not y["calls"]["gm"] and not y["calls"]["persona"], (
            f"fehlende verknuepfte Requestautoritaet darf keinen abhaengigen Modell-/"
            f"Personaaufruf ausloesen (phase={phase}): {y['calls']}"
        )
        assert y["disk"].get("current") is None, y
        # Der entfernte Record selbst ist waehrend der Unverfuegbarkeit physisch
        # nicht auf der Platte (er liegt bytegleich in `retained/`, s.u.) --
        # die Snapshots unterscheiden sich deshalb erwartbar genau um IHN. Alle
        # UEBRIGEN Records (z.B. der SL-Record im Persona-Fall) duerfen sich
        # nicht veraendern, UND es darf kein neuer Record entstanden sein.
        other_before = [r for r in x["disk"]["records"] if r["id"] != stuck_id]
        other_during = [r for r in y["disk"]["records"] if r["id"] != stuck_id]
        assert other_during == other_before, (
            "kein stiller Buchungs-/Recordwechsel an den UEBRIGEN Records waehrend der "
            f"kontrollierten Sperre: vorher={other_before} waehrend={other_during}"
        )
        assert all(r["id"] != stuck_id for r in y["disk"]["records"]), (
            f"die entfernte Datei darf waehrend der Unverfuegbarkeit nicht stillschweigend neu "
            f"entstehen: {y['disk']['records']}"
        )
        assert y["disk"]["budget"] == x["disk"]["budget"]

        # Wiederherstellung derselben Datei (bytegleich) -- kein Dauerverbot,
        # ein weiterer neuer Prozess muss den tatsaechlichen (bereits
        # accounted) Zustand wieder normal sehen.
        assert hashlib.sha256(retain.read_bytes()).hexdigest() == original_sha
        retain.rename(target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == original_sha

        z = _child(b, phase=phase)
        assert z["pid"] not in (x["pid"], y["pid"]), "echter Prozessneustart erforderlich"
        assert z["error"] is None, z
        assert (z["result"] or {}).get("status") == "completed", (
            f"nach exakter Wiederherstellung derselben Datei muss der tatsaechliche (bereits "
            f"accounted) Zustand normal weiterlaufen, kein Dauerverbot (phase={phase}): {z}"
        )
        expected = {"gm_question": (1, 1), "persona": (1, 0), "gm_final": (0, 0)}[phase]
        assert (len(z["calls"]["gm"]), len(z["calls"]["persona"])) == expected, (
            f"phase={phase}: erwartet {expected} (nur die noch fehlenden Folgecalls, kein "
            f"erneuter Request fuer den bereits accounted Schritt), erhalten "
            f"({len(z['calls']['gm'])}, {len(z['calls']['persona'])})"
        )


def test_01_gm_question_known_id_missing_file_stays_open():
    _missing_case("gm_question")


def test_02_persona_answer_known_id_missing_file_stays_open():
    _missing_case("persona")


def test_03_final_save_known_id_missing_file_stays_open():
    _missing_case("gm_final")


# --- Test 04: positiv, Erhalt -- menschlicher n-Pfad (kein Modellrequest) bleibt frei


def _human_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    return ReplyResult(kind="answer", text=A)


def _one_human(b: Path, action: str, *, interrupt: bool = False) -> dict:
    if action == "setup":
        write_test_profile(b / "run", max_turns=100, max_usd=10)
        onboarding.start_or_resume(b / "onboarding", PK)
        return {"pid": os.getpid()}

    calls = {"gm": [], "human": []}
    hits = []
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
                role="creation_dialog",
            )
            result = dataclasses.asdict(out)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            error = {"type": type(e).__name__, "message": str(e)}
    ob = onboarding.peek(b / "onboarding", PK)
    return {
        "pid": os.getpid(), "interrupt": interrupt, "result": result, "error": error, "calls": calls,
        "hits": hits, "onboarding": dataclasses.asdict(ob) if ob else None,
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


def test_04_human_answer_not_blocked_by_missing_record_guard():
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
            f"menschliche Antwort hat KEINEN eigenen Modellrequest (n-Pfad), der korrigierte "
            f"Guard darf `request_id is None` nicht mit einer fehlenden Datei verwechseln: {pending}"
        )
        sl_record = next(rec for rec in x["records"] if rec["id"] == pending["sl_request_id"])
        assert sl_record["state"] == "accounted", sl_record
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "completed", (
            f"persona_request_id=None (menschlicher n-Pfad) darf durch den korrigierten Guard "
            f"weiterhin NICHT blockiert werden -- der Dialog muss normal bis zum Save "
            f"weiterlaufen: {y}"
        )
        assert len(y["calls"]["gm"]) == 1 and not y["calls"]["human"], (
            f"kein erneuter SL-Request fuer den bereits gespeicherten Pending-Schritt, aber der "
            f"naechste ECHTE Turn (Erstsave) muss normal stattfinden: {y}"
        )


# --- Test 05: positiv, Erhalt -- vollstaendige received-Autoritaet wird einmalig fertig gebucht


def test_05_full_received_settlement_completes_normally():
    phase = "gm_question"
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        x = _child(b, action="setup_received_seconds", phase=phase)
        stuck = next(r for r in x["disk"]["records"] if r["id"] == x["stuck_id"])
        assert stuck["state"] == "received" and stuck.get("received_seconds") == 2.0, stuck

        y = _child(b, phase=phase)
        assert y["pid"] != x["pid"], "echter Prozessneustart erforderlich"
        assert y["error"] is None, y
        assert (y["result"] or {}).get("status") == "completed", (
            f"eine vollstaendige received-Autoritaet (bekannte Originaldauer) muss GENAU EINMAL "
            f"fertig gebucht werden und den Dialog normal weiterlaufen lassen: {y}"
        )
        settled = next(r for r in y["disk"]["records"] if r["id"] == x["stuck_id"])
        assert settled["state"] == "accounted", settled
        expected = {"gm_question": (1, 1), "persona": (1, 0), "gm_final": (0, 0)}[phase]
        assert (len(y["calls"]["gm"]), len(y["calls"]["persona"])) == expected, y

        z = _child(b, phase=phase)
        assert not z["calls"]["gm"] and not z["calls"]["persona"], (
            "requestfreier Reentry nach Abschluss"
        )


def main() -> int:
    tests = [
        test_01_gm_question_known_id_missing_file_stays_open,
        test_02_persona_answer_known_id_missing_file_stays_open,
        test_03_final_save_known_id_missing_file_stays_open,
        test_04_human_answer_not_blocked_by_missing_record_guard,
        test_05_full_received_settlement_completes_normally,
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
        p.add_argument("--phase", default="none")
        p.add_argument("--interrupt", action="store_true")
        p.add_argument("--human", action="store_true")
        args = p.parse_args()
        if args.human:
            print(json.dumps(_one_human(args.base, args.action, interrupt=args.interrupt)))
        else:
            print(json.dumps(_one(args.base, args.action, phase=args.phase)))
        raise SystemExit(0)
    raise SystemExit(main())
