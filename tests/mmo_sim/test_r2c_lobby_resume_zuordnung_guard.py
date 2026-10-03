#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2c_lobby_resume_zuordnung_guard.py — neue dauerhafte
Repo-Regression fuer den Konsistenz-Guard VOR dem Resume (MAIN-QUELLENENT-
SCHEIDUNG-ZUORDNUNG.md, externe `tests-review/review_resume_authorization.py`
im Lieferpaket, NICHT Teil dieses Repos).

Original+Derivat+Diff (WORKER-REPORT.md-Konvention dieses Repos, wie
`test_r2_hauptbefund2_bound_table_recovery.py`): dieselbe Subprozess-/
Response-Double-Technik UND dieselben Fixtures aus
`test_l01_l10_lobby_initiative.py` (kein zweiter Bootstrap-Baustein).
DERIVAT hier lebt DAUERHAFT im Repo (der externe Review-Test selbst ist
Lieferpaket, nicht Teil dieses Repos) und ist ueber den Dateinamen
`test_*.py` automatisch in `run_all.py` eingebunden. Kein
`run_play_session`-Rettungscallback -- die GM-Faelle laufen ueber den
tatsaechlichen, unveraenderten Spielstart-Pfad (`ui/tui.py:_play_bound_
table` -> `app_service.run_play_session`); Assertions pruefen echte
Diskzustaende (Tabellenstatus/Locks/Currents/Log), nicht bloss Log-/
Helfererfolg.

Deckt (Fixstellen `mmo_sim/ui/tui.py`s Resume-Zweig in
`_cmd_lobby_initiative` + `mmo_sim/core/lobby_service.py:offer_resolution_
exists`):
- Erlaubte Relation: vollstaendig konsistente Snapshot-/Table-/Resolution-
  Belege -- der neue Guard darf den bereits funktionierenden Resume-Pfad
  NICHT regredieren (derselbe Tisch schliesst real, echte GM-Turns, Locks
  freigegeben, Currents veroeffentlicht, keine neuen Initiativ-/Consent-
  Requests).
- Fall 02 (source_offer_id-Widerspruch): `Table.operator_meta.
  source_offer_id` weicht von der Angebots-Kennung ab, die die Snapshot-
  Ableitung aus `operator_meta["offer_log"]` selbst liefert.
- Fall 03 (Leader-Widerspruch): das im Snapshot gespeicherte Offer-Ereignis
  wird so veraendert, dass die Ableitung einen ANDEREN Leader liefert als
  der tatsaechliche `Table.leader`.
- Fall 04 (Resolution-Tisch-Widerspruch): der vorhandene `table_bound`-
  Resolution-Eintrag derselben Angebots-Kennung verweist auf einen ANDEREN
  Tisch als den tatsaechlichen `resumable.table_id`.

Fuer 02/03/04 gilt jeweils: der naechste echte Folgeprozess muss den Tisch
`active` lassen (kein GM-Call, keine neue Resolution, Locks/Currents
unveraendert gegenueber dem Stand VOR dem Resume-Versuch), eine konkrete
Meldung mit der Tisch-ID drucken -- UND NACH Wiederherstellung exakt der
urspruenglichen Belegbytes (nur in diesem synthetischen Testverzeichnis,
kein Eingriff in das Produktrepository) muss ein weiterer echter,
eigenstaendiger Folgeprozess denselben Tisch OHNE erneute Zustimmung real
abschliessen -- das Produkt repariert keine Quellen selbst, der Test tut
es nur fuer sich selbst nach der Konfliktprobe."""
from __future__ import annotations

import argparse
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402


class _ChildDriver:
    """Markiertes Testdouble -- identische Entscheidungslogik wie
    `test_r2_hauptbefund2_bound_table_recovery.py:_ChildDriver`: im
    Erzeugungsrunde (`mode != "pause"`) schlaegt 'sniper' 'tech' vor
    (Leader wird damit 'sniper', s. dortige Assertion), 'tech' akzeptiert
    real; in jeder weiteren Runde (`mode == "pause"`, hier ausschliesslich
    fuer bereits gebundene Resume-Versuche genutzt) pausieren beide -- ein
    echter Initiativ-/Consent-Request an sie waere selbst ein
    Regressionsfund (neue Zustimmung statt Wiederaufnahme der bereits
    vorliegenden)."""

    def __init__(self, pk: str, mode: str):
        self.pk = pk
        self.mode = mode
        self.config = None
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        if "decision_contract" in ctx:
            kind = "consent"
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
        elif "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            kind = "initiative"
            if self.mode == "pause" or self.pk != "sniper":
                text = json.dumps({"action": "pause"})
            else:
                text = json.dumps({"action": "propose", "wants": ["tech"]})
        else:
            kind = "table"
            text = "SYNTHETIC: Wir beobachten und entscheiden am Tisch."
        self.calls.append({"kind": kind, "context": ctx})
        return ParticipantDecision(text=text, origin_source=f"repo-regression-zuordnung-guard:{self.pk}")


def _child_main(args: argparse.Namespace) -> None:
    """Laeuft NUR im relaunchten Subprozess (`--child`) -- echte, andere
    Betriebssystem-PID als der aufrufende Testprozess."""
    root = Path(args.root)
    schema_path, states_dir, run_dir = l01._SCHEMA, root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

    drivers = {pk: _ChildDriver(pk, args.mode) for pk in ("sniper", "tech")}
    gms: list = []
    hits: list[dict] = []

    def gm_transport_factory(tid: str):
        if args.mode == "gm-init-failure" and not hits:
            hits.append({"seam": "real gm factory construction", "error": "RuntimeError"})
            raise RuntimeError("SYNTHETIC GM constructor temporarily unavailable")
        saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        for pk, s in saves.items():
            s["save_id"] = f"repo-regression-zuordnung-guard-{tid}-{pk}"
        gm = l01._TableGM(tid, f"{tid}-section", saves, turns_before_marker=3)
        gms.append(gm)
        return gm

    printed: list[str] = []
    session = l01._session(
        "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
        gm_transport_factory=gm_transport_factory,
        persona_driver_factory=lambda pk: drivers[pk],
        printed=printed,
    )

    errors: list[dict] = []
    try:
        session._cmd_lobby_initiative()
    except Exception as e:  # ECHTER Prozessabbruch bleibt sichtbar, kein Verschlucken hier.
        errors.append({"type": type(e).__name__, "message": str(e)})

    def read(p: Path, default):
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    ps_store = PersonaStateStore(schema_path=schema_path)
    current_ids: dict[str, str | None] = {}
    for pk in ("sniper", "tech"):
        try:
            current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir)
        except core_store.CurrentSaveUnavailableError:
            current = None
        current_ids[pk] = current.get("save_id") if current else None

    row = {
        "pid": os.getpid(),
        "printed": printed,
        "errors": errors,
        "hits": hits,
        "calls": {pk: [c["kind"] for c in d.calls] for pk, d in drivers.items()},
        "gm_calls": sum(len(g.calls) for g in gms),
        "tables": [read(p, {}) for p in sorted((run_dir / "tables").glob("*.json"))],
        "locks": read(run_dir / "locks.json", {}),
        "current_ids": current_ids,
        "offers": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path, limit: int = 2) -> dict:
    """ECHTER, EIGENSTAENDIGER Python-Subprozess -- die zurueckgegebene PID
    ist von jedem weiteren Aufruf verschieden."""
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child",
        "--root", str(root), "--mode", mode, "--result", str(result_path),
    ]
    env = os.environ.copy()
    env["MMO_SIM_LOBBY_INITIATIVE_LIMIT"] = str(limit)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cp = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}: {cp.stderr[-2000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def _seed(root: Path) -> None:
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-op", ["sniper", "tech"],
    )
    write_test_profile(run_dir)
    for pk in ("sniper", "tech"):
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)


def _own_decision_calls(r: dict) -> int:
    return sum(1 for kinds in r["calls"].values() for k in kinds if k in ("initiative", "consent"))


def test_zuordnung_guard_consistent_relation_allows_real_resume():
    """Erlaubte Relation: vollstaendig konsistente Snapshot-/Table-/
    Resolution-Belege. Der neue Konsistenz-Guard darf den bereits
    funktionierenden B2-Resume-Pfad NICHT regredieren."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "gm-init-failure", root / "r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        assert '"outcome": "table_bound"' in r1["offers"]
        tid = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "pause", root / "r2.json")
        assert not r2["errors"], r2["errors"]
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid
        assert r2["tables"][0]["status"] == "closed", "konsistente Belege muessen real bis zum Abschluss fortsetzen"
        assert r2["gm_calls"] >= 3
        assert not r2["locks"]
        assert all(v is not None for v in r2["current_ids"].values())
        assert _own_decision_calls(r2) == 0, "kein neuer Initiativ-/Consent-Request bei konsistenter Wiederaufnahme"


def _conflict_case(mode_first: str, corrupt, label: str) -> dict:
    """Gemeinsames Geruest fuer die drei gesperrten Relationen (02/03/04):
    B2-Tisch anlegen (Resolution bereits geschrieben), EINE begrenzte
    widersprechende Testeingabe injizieren (Originalbytes separat
    aufbewahrt), Resume-Versuch beobachten (muss kontrolliert offen
    bleiben), Originalbytes wiederherstellen, echten Restore-Resume
    beobachten (muss danach real abschliessen, ohne erneute Zustimmung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, mode_first, root / f"{label}-r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        assert '"outcome": "table_bound"' in r1["offers"]
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        offers_path = root / "run" / "invitation_decisions.jsonl"
        original_table_bytes = table_path.read_bytes()
        original_offers_bytes = offers_path.read_bytes()
        locks_before = (root / "run" / "locks.json").read_bytes()
        currents_before = r1["current_ids"]

        corrupt(table_path, offers_path)

        r2 = _run_child(root, "pause", root / f"{label}-r2-conflict.json")
        assert not r2["errors"], "eine konkrete kontrollierte Meldung wird erwartet, keine rohe Ausnahme"
        assert r2["gm_calls"] == 0, "kein GM-/Spielstart bei widerspruechlichen Belegen"
        assert r2["tables"][0]["status"] == "active", "Tisch bleibt bei widerspruechlichen Belegen aktiv"
        assert (root / "run" / "locks.json").read_bytes() == locks_before, "Locks bleiben bei Konflikt unveraendert"
        assert r2["current_ids"] == currents_before, "Currents bleiben bei Konflikt unveraendert (keine Publikation)"
        assert any(tid in p for p in r2["printed"]), f"konkrete Tisch-ID in der Meldung erwartet: {r2['printed']}"
        assert r2["offers"].count('"outcome": "table_bound"') == original_offers_bytes.decode("utf-8").count(
            '"outcome": "table_bound"',
        ), "keine zweite Resolution beim Konflikt danebenschreiben"

        table_path.write_bytes(original_table_bytes)
        offers_path.write_bytes(original_offers_bytes)

        r3 = _run_child(root, "pause", root / f"{label}-r3-restored.json")
        assert not r3["errors"], r3["errors"]
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["tables"][0]["status"] == "closed", "nach Wiederherstellung der Originalbytes muss derselbe Tisch real abschliessen"
        assert r3["gm_calls"] >= 3
        assert not r3["locks"]
        assert all(v is not None for v in r3["current_ids"].values())
        assert _own_decision_calls(r3) == 0, "kein erneuter Initiativ-/Consent-Request nach Restore-Resume"
        return {"table_id": tid, "conflict_held_open": True, "restore_resume_completed": True}


def test_zuordnung_guard_source_offer_conflict_holds_then_restores():
    """Fall 02: `Table.operator_meta.source_offer_id` weicht von der
    Angebots-Kennung ab, die die Snapshot-Ableitung selbst liefert."""

    def corrupt(table_path: Path, offers_path: Path) -> None:
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        obj["operator_meta"]["source_offer_id"] = "synthetic-different-source-offer"
        table_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _conflict_case("gm-init-failure", corrupt, "02-source-offer")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_zuordnung_guard_leader_conflict_holds_then_restores():
    """Fall 03: das im Snapshot gespeicherte Offer-Ereignis wird so
    veraendert, dass die Ableitung 'tech' statt des tatsaechlichen
    `Table.leader` ('sniper' -- der urspruengliche Vorschlagende, s.
    `_ChildDriver`/`test_r2_hauptbefund2_bound_table_recovery.py`) liefert."""

    def corrupt(table_path: Path, offers_path: Path) -> None:
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        assert obj["leader"] == "sniper", "Testannahme verletzt: urspruenglicher Leader war nicht 'sniper'"
        ev = next(e for e in obj["operator_meta"]["offer_log"] if e["type"] == "offer")
        assert ev["from"] == "sniper", "Testannahme verletzt: Offer-Ereignis stammte nicht von 'sniper'"
        ev["from"] = "tech"
        table_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _conflict_case("gm-init-failure", corrupt, "03-leader")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_zuordnung_guard_resolution_table_conflict_holds_then_restores():
    """Fall 04: der vorhandene `table_bound`-Resolution-Eintrag derselben
    Angebots-Kennung verweist auf einen ANDEREN Tisch als den
    tatsaechlichen `resumable.table_id`."""

    def corrupt(table_path: Path, offers_path: Path) -> None:
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        source = obj["operator_meta"]["source_offer_id"]
        rows = [json.loads(line) for line in offers_path.read_text(encoding="utf-8").splitlines()]
        changed = False
        for r in rows:
            if r.get("type") == "resolution" and r.get("offer_id") == source:
                r["table_id"] = "synthetic-unrelated-table"
                changed = True
        assert changed, "Testannahme verletzt: keine passende Resolution zum Manipulieren gefunden"
        offers_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    result = _conflict_case("gm-init-failure", corrupt, "04-resolution-table")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


if __name__ == "__main__":
    if "--child" in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--root", required=True)
        ap.add_argument("--mode", required=True)
        ap.add_argument("--result", required=True)
        _child_main(ap.parse_args())
        sys.exit(0)

    import traceback

    tests = [
        test_zuordnung_guard_consistent_relation_allows_real_resume,
        test_zuordnung_guard_source_offer_conflict_holds_then_restores,
        test_zuordnung_guard_leader_conflict_holds_then_restores,
        test_zuordnung_guard_resolution_table_conflict_holds_then_restores,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
