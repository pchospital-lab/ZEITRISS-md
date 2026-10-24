#!/usr/bin/env python3
"""
tests/mmo_sim/test_s2_lobby_resume_pre_plan_completion_recovery.py -- R12-
AUTORECOVERY-Nachzug (S2, ZR-N2-STABILISIERUNG-WEITERLAUF-2026-10-17-R1).

Deckt die LUECKE, die der bestehende `test_section_completion_resume_two_
process_crash.py` (process3/process4) NICHT abdeckt: dort wird `SectionRuntime.
run_full_section` DIREKT konstruiert, OHNE den normalen Lobby-/Store-Weg
(`core/lobby_flow.py:run_lobby_window` -> `core/store.py:find_bound_active_
unplayed_table`). Vor diesem Fix lehnte `find_bound_active_unplayed_table`
JEDEN Tisch mit nicht-leerem `sl_log` pauschal als "schon gespielt" ab --
auch dann, wenn das `sl_log` NUR einen bereits durabel empfangenen, aber noch
nicht geplanten Abschluss-Beleg enthielt (Crash NACH `request_ledger.
finish_received`, VOR `complete_section`/`__plan.json`). Der bereits
vorhandene Recovery-Mechanismus in `core/runtime.py` wurde dadurch ueber den
normalen Terminal-/Headless-Lobby-Einstieg NIE erreicht.

Technik: echter Prozesswechsel (Original+Derivat+Diff-Konvention dieses
Repos) -- Prozess 1 baut ueber `session._cmd_lobby_initiative()` (genau wie
`test_r2_hauptbefund2_bound_table_recovery.py`) real einen Tisch, laesst ihn
real 2 GM-Turns spielen und killt sich hart (`os._exit`) UNMITTELBAR nach dem
3. `request_ledger.finish_received`-Aufruf (= der Marker-Turn; derselbe
Zaehlzeitpunkt wie `_TableGM(turns_before_marker=3)`), NACH dem durablen
`sl_log`-Persist UND NACH `state=accounted` (Positiv-Fenster, s. process3/4
im bestehenden Crash-Test), aber VOR `marker_hit(...)`/`complete_section`.
Prozess 2 (echte neue PID) ruft `session._cmd_lobby_initiative()` erneut auf
-- MUSS den Tisch jetzt ueber `find_bound_active_unplayed_table` + den
bestehenden Recovery-Zweig genau EINMAL abschliessen, OHNE einen neuen
GM-/Initiativ-/Consent-Request."""
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
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy  # noqa: E402


class _ChildDriver:
    """Wie `test_r2_hauptbefund2_bound_table_recovery.py:_ChildDriver` --
    entscheidet NUR anhand des tatsaechlichen Kontrollvertrags."""

    def __init__(self, pk: str, mode: str):
        self.pk = pk
        self.mode = mode
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
        return ParticipantDecision(text=text, origin_source=f"repo-regression-s2:{self.pk}")


def _child_main(args: argparse.Namespace) -> None:
    root = Path(args.root)
    schema_path, states_dir, run_dir = l01._SCHEMA, root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

    drivers = {pk: _ChildDriver(pk, args.mode) for pk in ("sniper", "tech")}
    gms: list = []
    hits: list[dict] = []

    def gm_transport_factory(tid: str):
        saves = {pk: l01._load_fixture_save(pk) for pk in ("sniper", "tech")}
        for pk, s in saves.items():
            s["save_id"] = f"repo-regression-s2-{tid}-{pk}"
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
    if args.mode == "pre-plan-crash":
        _original_finish_received = request_ledger.finish_received
        counter = {"n": 0}

        def _counting_finish_received(run_dir_arg, request_id, **kwargs):
            _original_finish_received(run_dir_arg, request_id, **kwargs)
            # NUR `role=="gm_turn"`-Requests zaehlen -- Initiativ-/Consent-/
            # persona_decision-Requests laufen UEBER DENSELBEN `request_
            # ledger.finish_received`, duerfen den Zaehler aber nicht
            # verzerren (sonst crasht der Prozess schon waehrend der
            # Lobby-Verhandlung, lange vor dem ersten echten GM-Turn).
            record = request_ledger.load_request(run_dir_arg, request_id)
            if record is None or record.get("role") != "gm_turn":
                return
            counter["n"] += 1
            # Positiv-Fenster (wie process3/4 in test_section_completion_
            # resume_two_process_crash.py): NACH state=accounted, VOR
            # marker_hit(...)/complete_section/__plan.json. counter==3
            # faellt mit `_TableGM(turns_before_marker=3)`s Marker-Turn
            # zusammen (Turn1=Leader-Anker, Turn2=Gast-Import, Turn3=erster
            # echter Rundenturn -- der den Marker trug).
            if counter["n"] == 3:
                hits.append({"seam": "request_ledger.finish_received", "role": "gm_turn", "number": 3})
                sys.stdout.flush()
                sys.stderr.flush()
                os._exit(93)

        request_ledger.finish_received = _counting_finish_received
        try:
            session._cmd_lobby_initiative()
            # Sollte wegen os._exit(93) NIE erreicht werden.
            print(json.dumps({"unexpected_normal_return": True}))
            sys.exit(0)
        except Exception as e:  # jeder ungefangene Fehler bleibt sichtbar.
            errors.append({"type": type(e).__name__, "message": str(e)})
    else:
        try:
            session._cmd_lobby_initiative()
        except Exception as e:
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
        "calls": {pk: len([c for c in d.calls if c["kind"] in ("initiative", "consent")]) for pk, d in drivers.items()},
        "table_calls": {pk: len([c for c in d.calls if c["kind"] == "table"]) for pk, d in drivers.items()},
        "gm_calls": sum(len(g.calls) for g in gms),
        "tables": [read(p, {}) for p in sorted((run_dir / "tables").glob("*.json"))],
        "locks": read(run_dir / "locks.json", {}),
        "current_ids": current_ids,
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path, limit: int = 2) -> dict:
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child",
        "--root", str(root), "--mode", mode, "--result", str(result_path),
    ]
    env = os.environ.copy()
    env["MMO_SIM_LOBBY_INITIATIVE_LIMIT"] = str(limit)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cp = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True, timeout=60)
    if mode == "pre-plan-crash":
        # `os._exit(93)` ueberspringt JEDEN Python-Cleanup (inkl. der
        # Result-JSON-Schreibung nach dem try/except) -- das IST der Zweck
        # dieses Modus (haerter Absturz, kein gefangener Exit). Der Aufrufer
        # liest den Festplattenzustand danach direkt aus `root/run`.
        if cp.returncode != 93:
            raise RuntimeError(f"child(mode={mode!r}) unerwarteter exit={cp.returncode}: {cp.stderr[-2000:]}")
        return {"returncode": cp.returncode}
    if cp.returncode != 0 or not result_path.exists():
        raise RuntimeError(
            f"child(mode={mode!r}) exit={cp.returncode} result_exists={result_path.exists()}: {cp.stderr[-2000:]}"
        )
    return json.loads(result_path.read_text(encoding="utf-8"))


def _seed(root: Path) -> None:
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-op", ["sniper", "tech"],
    )
    write_test_profile(run_dir)
    for pk in ("sniper", "tech"):
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)


def test_s2_positive_recovery_pre_plan_crash_resumes_exactly_once_no_new_model_calls():
    """POSITIVTEST (S2-Pflichtfall): Prozess 1 crasht hart NACH dem 3.
    `request_ledger.finish_received` (durabler sl_log-Eintrag MIT Marker,
    MIT `expected_prev_ref_by_member`, Request `state=accounted`), VOR
    `complete_section`/`__plan.json` -- der Tisch bleibt `active`, OHNE
    `__plan.json`. Prozess 2 (echte neue PID) MUSS diesen Tisch ueber
    `find_bound_active_unplayed_table` (jetzt mit `marker`/`marker_matches`)
    erkennen und via `core/runtime.py`s bestehendem R12-AUTORECOVERY-Zweig
    GENAU EINMAL abschliessen -- 0 neue GM-Turns (`gm_calls`), 0 neue
    Initiativ-/Consent-Requests."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        _run_child(root, "pre-plan-crash", root / "r1.json")
        table_files = sorted((root / "run" / "tables").glob("*.json"))
        assert len(table_files) == 1, table_files
        t1 = json.loads(table_files[0].read_text(encoding="utf-8"))
        assert t1["status"] == "active", f"Tisch darf nach dem Crash noch nicht geschlossen sein: {t1}"
        assert t1["sl_log"], "sl_log muss den durabel persistierten Marker-Turn tragen"
        assert t1["sl_log"][-1]["section_id"] == f"{t1['table_id']}-section"
        assert t1["sl_log"][-1].get("expected_prev_ref_by_member") is not None
        tid = t1["table_id"]
        completion_dir = root / "run" / "completion"
        plan_files = list(completion_dir.glob("*__plan.json")) if completion_dir.exists() else []
        assert not plan_files, f"VOR dem Fix-Anwendungsfall darf noch KEIN __plan.json existieren: {plan_files}"
        # Request-Ledger-Gegenbeleg: der GM-Turn-Request MUSS `accounted` sein
        # (Positivfenster, NICHT process1-artig bei bloss `sent`).
        gm_requests = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in (root / "run" / "requests").glob("*.json")
        ] if (root / "run" / "requests").exists() else []
        gm_turn_requests = [r for r in gm_requests if r.get("role") == "gm_turn"]
        assert gm_turn_requests and all(r.get("state") == "accounted" for r in gm_turn_requests), gm_turn_requests

        r2 = _run_child(root, "pause", root / "r2.json")
        assert not r2["errors"], r2["errors"]
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid, (
            f"Resume muss denselben Tisch fortsetzen, kein zweiter Tisch: {r2['tables']}"
        )
        assert r2["tables"][0]["status"] == "closed", (
            f"die bereits durabel empfangene Abschlussantwort muss jetzt real geerntet werden: {r2}"
        )
        assert r2["gm_calls"] == 0, (
            f"R12-AUTORECOVERY darf KEINEN neuen SL-/GM-Turn ausloesen: {r2['gm_calls']}"
        )
        assert r2["calls"]["sniper"] == 0 and r2["calls"]["tech"] == 0, (
            f"kein neuer Initiativ-/Consent-Request fuer einen bereits gebundenen, "
            f"durabel abgeschlossenen Tisch: {r2['calls']}"
        )
        assert not r2["locks"], "normaler Lock-Release nach dem geernteten Abschluss erwartet"
        assert all(v is not None for v in r2["current_ids"].values()), (
            f"veroeffentlichte Currents fuer beide Mitglieder erwartet: {r2['current_ids']}"
        )
        completion_dir = root / "run" / "completion"
        final_files = list(completion_dir.glob(f"{tid}-section__final.json"))
        assert len(final_files) == 1, f"genau EIN Abschluss-Final-Dokument erwartet: {final_files}"


def test_s2_negative_wrong_bound_table_generation_stays_hold():
    """NEGATIVKONTROLLE: falsche/fremde Tisch-ID im `bound`-Mapping (z.B.
    nach einer Mehrdeutigkeit) darf NIE automatisch als derselbe
    wiederaufnehmbare Tisch akzeptiert werden -- unveraendertes bestehendes
    Verhalten, hier mit `marker`/`marker_matches` zusaetzlich durchgereicht."""
    from mmo_sim.core.completion_marker import completion_marker_matches
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active",
            sl_log=[{
                "section_id": "lobby-sniper-tech-section",
                "content": f"{COMPLETION_MARKER} table_id=lobby-sniper-tech section_id=lobby-sniper-tech-section",
                "expected_prev_ref_by_member": {"sniper": None, "tech": None},
            }],
        )
        table.persist()
        # Mehrdeutig gebunden -- zwei verschiedene Tisch-IDs.
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech__2"}
        found = core_store.find_bound_active_unplayed_table(
            run_dir, ready_ids, bound, marker=COMPLETION_MARKER, marker_matches=completion_marker_matches,
        )
        assert found is None, "Mehrdeutigkeit darf NICHT durch die neue Recovery-Pruefung umgangen werden"


def test_s2_negative_real_play_without_marker_stays_rejected():
    """NEGATIVKONTROLLE: ein `sl_log` mit einem ECHTEN, nicht-markerfoermigen
    Spielzug (normales Weiterspielen, kein Abschlussbeleg) bleibt weiterhin
    als "schon gespielt" abgelehnt -- die neue Pruefung darf einen echten
    laufenden Tisch nicht faelschlich als unplayed/resumable einstufen."""
    from mmo_sim.core.completion_marker import completion_marker_matches
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active",
            sl_log=[{
                "section_id": "lobby-sniper-tech-section",
                "content": "Ihr beobachtet die Umgebung aufmerksam. Was tut ihr als naechstes?",
                "expected_prev_ref_by_member": {"sniper": None, "tech": None},
            }],
        )
        table.persist()
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"}
        found = core_store.find_bound_active_unplayed_table(
            run_dir, ready_ids, bound, marker=COMPLETION_MARKER, marker_matches=completion_marker_matches,
        )
        assert found is None, "echte laufende Dialogzuege ohne Marker duerfen nicht als unplayed gelten"


def test_s2_negative_missing_snapshot_legacy_entry_stays_rejected():
    """NEGATIVKONTROLLE: ein Marker-Treffer OHNE `expected_prev_ref_by_
    member` (Legacy-Eintrag bzw. unzureichend gebunden, AR2 Teil C) bleibt
    unzureichend gebunden -- kein automatischer Resume ueber die neue
    Pruefung, konservativ reserviert statt Teil-Vertrauen."""
    from mmo_sim.core.completion_marker import completion_marker_matches
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active",
            sl_log=[{
                "section_id": "lobby-sniper-tech-section",
                "content": f"{COMPLETION_MARKER} table_id=lobby-sniper-tech section_id=lobby-sniper-tech-section",
                # bewusst KEIN expected_prev_ref_by_member -- Legacy/unzureichend.
            }],
        )
        table.persist()
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"}
        found = core_store.find_bound_active_unplayed_table(
            run_dir, ready_ids, bound, marker=COMPLETION_MARKER, marker_matches=completion_marker_matches,
        )
        assert found is None, "fehlender Generations-Schnappschuss darf nicht automatisch geerntet werden"


def test_s2_backward_compat_without_marker_params_unchanged():
    """Rueckwirkungsfrei (A1/Backward-Compat): OHNE `marker`/`marker_matches`
    bleibt das bisherige Verhalten (jedes nicht-leere `sl_log` gilt als
    "schon gespielt") exakt erhalten -- bestehende Aufrufer ausserhalb von
    `lobby_flow.py` sind unveraendert."""
    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active", sl_log=[{"turn": 1}],
        )
        table.persist()
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound) is None


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
        test_s2_positive_recovery_pre_plan_crash_resumes_exactly_once_no_new_model_calls,
        test_s2_negative_wrong_bound_table_generation_stays_hold,
        test_s2_negative_real_play_without_marker_stays_rejected,
        test_s2_negative_missing_snapshot_legacy_entry_stays_rejected,
        test_s2_backward_compat_without_marker_params_unchanged,
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
