#!/usr/bin/env python3
"""
tests/mmo_sim/test_r1r2_received_settlement_obligations.py — dauerhafte
Regressionstests fuer R1/R2 (Community-Recovery 2026-09-25,
REVIEW-COMMUNITY-RECOVERY.md §3/§4). Adaptiert aus der einmaligen
Review-Probe `tests-review/review_received_obligations.py` (Ausgangsbefund
dort: 1 PASS / 4 FAIL / 0 ERROR) in einen dauerhaften In-Repo-Test, exakt
dieselben Assertions/Faelle, repo-uebliche `main()`/Exitcode-Form statt
`--output-dir`-Dump.

R1 (`request_ledger.find_durable_result`/`finish_received`/
`settle_received`, `core.creation_service.run_admitted_creation_dialog`,
`domain.zeitriss.community_creation._persona_get_reply_factory`): ein
`state=received`-Treffer (Text bereits durabel, Kosten-/Zeitbuchung noch
offen) darf NICHT als erledigte Voraussetzung fuer `completed`/
`already_ready` verwendet werden, ohne die offene Buchung GENAU EINMAL
nachzuholen. Test 01/02/03 unten.

R2 (`request_ledger._REQUIRED_RECORD_KEYS`/`_CONTROL_FIELD_TYPES`): ein
gueltiger Bestandsrecord OHNE `result_text` (vom Writer VOR C2 geschrieben)
bleibt lesbar. Test 05 unten simuliert diesen Vorwriter-Record SELBST
(derselbe aktuelle `request_ledger.begin()` plus ein manueller Nachbau des
VOR-C2-`finish_received()`-Schemas ohne `result_text`/`received_seconds`)
-- kein zweiter Interpreter/keine externe Vorversion noetig, der reale
Cross-Interpreter-Beleg lebt in der einmaligen Review-Probe (Ausgangs-
/Abnahmelauf), dieser Test haelt NUR den Lesevertrag dauerhaft in-repo fest.

R4 (`interpret_creation_pause_control`, `_persona_get_reply_factory`): Test
04 -- eine bereits durabel abgerechnete Pause-Kontrollzeile ist beim
naechsten Aufruf KEIN wiederverwendbarer Antworttext mehr, eine
ausdrueckliche Fortsetzung erhaelt GENAU EINEN neuen Entscheidungsversuch.

Testdoubles ausschliesslich an Modell-/Fehlerstellen (Response-Doubles je
Kindprozess, echte neue PIDs), keine echte Modellbinary/Anbieterroute."""
from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
import mmo_sim.adapters.base as _adapters_base  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core import request_ledger as ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_one_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PS = PersonaStateStore(schema_path=SCHEMA)
PK = "settlement_persona"
Q = "SYNTHETIC: Welche Ausruestung?"
A = "SYNTHETIC: Ich waehle leichte Ruestung."
SAVE = {"v": 7, "save_id": "SYNTHETIC-SETTLEMENT-SAVE",
        "characters": [{"char_id": "SYNTHETIC-SETTLEMENT-CHR", "name": "Synthetic", "callsign": "SETTLE", "level": 1}]}
ST = "```json\n" + json.dumps(SAVE) + "\n```"


def _setup(b: Path) -> None:
    draft = {
        "real_name": "Synthetic Settlement", "archetype": "SYNTHETIC_ARCH", "play_style": "SYNTHETIC_STYLE",
        "charwunsch": "SYNTHETIC_WISH",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
    }
    bootstrap_community(b / "run/community", "settlement-community", 1, {PK: draft}, PS, b / "states", "2026-09-25")
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


def _one(b: Path, fault: str, action: str) -> dict:
    if action == "setup":
        _setup(b)
        return {"pid": os.getpid()}
    if action == "legacy_create":
        # R2: baut einen Record im VOR-C2-Schema nach (kein `result_text`,
        # kein `received_seconds`) -- derselbe aktuelle `begin()`, dann ein
        # manueller Nachbau exakt dessen, was `finish_received()` VOR der
        # C2/R1-Erweiterung geschrieben haette. Der externe Cross-
        # Interpreter-Beleg (echte Vorversion) lebt in der einmaligen
        # Review-Probe; dieser Test haelt nur den Lesevertrag fest.
        write_test_profile(b / "run", max_turns=10)
        rid = ledger.begin(
            b / "run", role="legacy_probe", content="synthetic legacy", reserved_usd=0.01,
            table_id="legacy-table", section_id="legacy-section", turn_idx=0, participant="legacy_persona",
        )
        p = (b / "run/requests" / f"{rid}.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        data["state"] = "accounted"
        data["usage"] = {"usd": 0.01}
        data["settled_ts"] = 12345.0
        data["usd_reconciled"] = True
        data.pop("result_text", None)
        data.pop("received_seconds", None)
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return {"pid": os.getpid(), "id": rid, "raw": data}
    if action == "legacy_read":
        fp = next((b / "run/requests").glob("*.json"))
        err = None
        out = None
        try:
            out = ledger.load_request(b / "run", fp.stem)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            err = {"type": type(e).__name__, "message": str(e)}
        return {"pid": os.getpid(), "load": out, "error": err}

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
            text = _adapters_base._CREATION_PAUSE_CONTROL_LINE if fault == "pause" else A
            return ParticipantDecision(text=text, origin_source="synthetic-settlement", meta={"usage": {"usd": 0.05}})

    orig_finish = ledger.finish_received
    orig_seconds = ledger.add_seconds
    orig_money = ledger.record_usd_delta
    active_role = [None]

    def finish(run, rid, **kw):
        active_role[0] = ledger.load_request(run, rid)["role"]
        kw["seconds"] = 2.0
        return orig_finish(run, rid, **kw)

    def seconds(*args, **kw):
        target = "community_creation_persona" if fault.startswith("persona") else "community_creation_gm"
        if fault.endswith("seconds") and active_role[0] == target and not hits:
            hits.append({"seam": "ledger.add_seconds", "role": target})
            raise OSError("SYNTHETIC one-shot settlement seconds write failure")
        return orig_seconds(*args, **kw)

    def money(*args, **kw):
        target = "community_creation_persona" if fault.startswith("persona") else "community_creation_gm"
        if fault.endswith("money") and active_role[0] == target and not hits:
            hits.append({"seam": "ledger.record_usd_delta", "role": target})
            raise OSError("SYNTHETIC one-shot settlement money write failure")
        return orig_money(*args, **kw)

    with patch.object(ledger, "finish_received", finish), patch.object(ledger, "add_seconds", seconds), \
            patch.object(ledger, "record_usd_delta", money):
        try:
            r = advance_one_persona_creation(
                run_dir=b / "run", states_dir=b / "states", schema_path=SCHEMA, onboarding_dir=b / "onboarding",
                catalog_dir=b / "catalog", community_id="settlement-community", generation=1, persona_key=PK,
                gm_transport_factory=lambda cid: GM(), persona_driver_factory=lambda pk: Driver(),
                print_fn=messages.append,
            )
            result = dataclasses.asdict(r)
        except Exception as e:  # noqa: BLE001 -- roh an den Elternprozess melden
            error = {"type": type(e).__name__, "message": str(e)}
    return {
        "pid": os.getpid(), "fault": fault, "result": result, "error": error, "calls": calls,
        "hits": hits, "messages": messages, "disk": _snapshot(b),
    }


def _child(b: Path, fault: str = "none", action: str = "advance") -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--base", str(b), "--fault", fault, "--action", action]
    cp = subprocess.run(cmd, text=True, capture_output=True, timeout=40)
    if cp.returncode:
        raise RuntimeError(cp.stdout + "\n" + cp.stderr)
    return json.loads(cp.stdout)


def _healthy(d: dict) -> bool:
    return (
        abs(d["budget"]["usd_spent"] - 0.15) < 1e-9
        and abs(d["budget"]["seconds_elapsed"] - 6) < 1e-9
        and d["budget"]["turns_used"] == 3
        and all(r["state"] == "accounted" for r in d["records"])
    )


def test_01_healthy_settled_ready():
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b)
        y = _child(b)
        assert _healthy(x["disk"]), x
        assert x["disk"] == y["disk"], (x, y)
        assert not y["calls"]["gm"] and not y["calls"]["persona"], "Reentry muss requestfrei bleiben"


def _settlement_case(role: str) -> None:
    for seam in ("seconds", "money"):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            _child(b, action="setup")
            x = _child(b, role + "-" + seam)
            y = _child(b)
            assert x["hits"] and x["pid"] != y["pid"], "Fehlerinjektion und echter Neustart erforderlich"
            ready = (y["result"] or {}).get("status") in ("completed", "already_ready")
            assert not ready or _healthy(y["disk"]), (
                f"Ready gemeldet bei durablem received-Record, tatsaechliches Geld/Dauer bleibt "
                f"unverbucht (role={role}, seam={seam}): {y}"
            )
            if not ready:
                assert not y["calls"]["gm"] and not y["calls"]["persona"], (
                    f"unverbuchtes Ergebnis darf nicht still zu einer weiteren Modellanfrage "
                    f"fuehren (role={role}, seam={seam}): {y}"
                )


def test_02_gm_received_settlement():
    _settlement_case("gm")


def test_03_persona_received_settlement():
    _settlement_case("persona")


def test_04_pause_can_explicitly_continue():
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        _child(b, action="setup")
        x = _child(b, "pause")
        y = _child(b)
        assert x["result"]["status"] == "paused", x
        assert y["result"]["status"] in ("completed", "already_ready"), (
            f"eine ausdruecklich fortgesetzte Erschaffung darf die alte Pause nicht fuer immer "
            f"wiederholen, sondern muss eine neue Personaentscheidung einholen: {y}"
        )


def test_05_old_valid_record_remains_readable():
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        old = _child(b, action="legacy_create")
        fp = b / "run/requests" / f"{old['id']}.json"
        before = fp.read_bytes()
        new = _child(b, action="legacy_read")
        assert "result_text" not in old["raw"]
        assert new["error"] is None, (
            f"ein unveraenderter, gueltiger Vor-C2-Record darf nicht allein wegen des jetzt "
            f"optionalen neuen `result_text`-Feldes abgelehnt werden: {new}"
        )
        assert fp.read_bytes() == before, "der Lesevorgang darf den Bestandsrecord nicht veraendern"


def main() -> int:
    tests = [
        test_01_healthy_settled_ready, test_02_gm_received_settlement, test_03_persona_received_settlement,
        test_04_pause_can_explicitly_continue, test_05_old_valid_record_remains_readable,
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
        p.add_argument("--fault", default="none")
        p.add_argument("--action", default="advance")
        args = p.parse_args()
        print(json.dumps(_one(args.base, args.fault, args.action)))
        raise SystemExit(0)
    raise SystemExit(main())
