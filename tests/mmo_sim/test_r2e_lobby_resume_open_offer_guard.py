#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2e_lobby_resume_open_offer_guard.py — neue dauerhafte
Repo-Regression fuer den ZWEITEN, bisher ungeschuetzten Resume-Einstieg
(MAIN-QUELLENENTSCHEIDUNG-EINSTIEGSWEGE.md, extern:
`tests-review/review_open_offer_resume.py` im Lieferpaket, NICHT Teil
dieses Repos).

Ein vollstaendig bestaetigtes, aber noch NICHT resolviertes Angebot
(Anwendung/Resolution-Nachtrag unterbrochen, BEVOR die Resolution
geschrieben werden konnte) macht `confirmed_derivation` in
`ui/tui.py:_cmd_lobby_initiative` bereits VOR dem Initiativschritt-Loop
nicht-None (`pre_derivation`). Der besondere Finder-/Snapshot-Resumezweig
samt seiner R1/R2-Guards liegt unter `if confirmed_derivation is None:`
und wird dadurch NIE erreicht -- stattdessen laeuft der ALLGEMEINE
Angebotszweig (`core_store.create_table_from_offer_log` -> Resolution-
Nachtrag -> `_play_bound_table`). `create_table_from_offer_log`s frueher
Resume-Return fuer einen bereits vorhandenen OFFENEN Tisch validiert die
uebergebenen Argumente selbst NICHT erneut (s. dortiger Docstring).

Fixstelle: `ui/tui.py:_resume_consistency_hold_reason` (aus dem
Finderzweig extrahiert) wird jetzt AUCH im allgemeinen Angebotszweig
aufgerufen, sobald die von `create_table_from_offer_log` zurueckgegebene
`GroupDerivation.source_offer_id is None` ist (Resume-Return-Erkennung) --
VOR Resolution-Nachtrag und `_play_bound_table`.

Reuse (kein zweiter Bootstrap-Baustein, wie schon
`test_r2d_lobby_resume_belegkette_guard.py` fuer `test_r2c`):
`_seed`/`_ChildDriver`/`_own_decision_calls` aus
`test_r2c_lobby_resume_zuordnung_guard.py` unveraendert importiert. Ein
eigener Child-Entry-Point ist nur wegen der zusaetzlichen
`resolution-write-failure`-Fehlerinjektion noetig (identische Technik wie
im Delivery-Paket `tests-review/review_open_offer_resume.py`: EIN
markierter `OSError` genau am tatsaechlichen `write()` des JSONL-
Resolutionappends, danach normaler Dateizugriff -- keine geloeschte
Resolution, keine nachgebaute Recovery). Kein `run_play_session`-
Rettungscallback -- alle Faelle laufen ueber den tatsaechlichen,
unveraenderten Spielstart-Pfad (`ui/tui.py:_play_bound_table` ->
`app_service.run_play_session`); Assertions pruefen echte Diskzustaende
(Tabellenstatus/Locks/Currents/Log), nicht bloss Log-/Helfererfolg.

Deckt:
- Gesunder Erhalt: unresolviertes, vollstaendig bestaetigtes Angebot
  (B1 ohne Resolution) trifft ueber den allgemeinen Zweig auf den
  eigenen, bereits angelegten offenen Tisch -- Guard bleibt konsistent,
  fehlende Resolution wird idempotent nachgezogen, der Tisch schliesst
  real (kein neuer zweiter Tisch, keine erneute Zustimmung).
- Fall missing-map: `Table.chrononaut_ids['sniper']` fehlt -- muss VOR
  jeder Personaentscheidung kontrolliert offenhalten (frueher: roher
  `KeyError('sniper')` nach bereits nachgeschriebener Resolution).
- Fall missing-lock: Snipers Mitgliedslock fehlt (chrononaut_ids bleibt
  vollstaendig) -- muss ebenso kontrolliert offenhalten (frueher: Abschluss
  trotz fehlender notwendiger Bindung).
Fuer missing-map/missing-lock gilt jeweils: der Resume-Versuch darf keine
neue Resolution schreiben, keinen Lock veraendern, keinen GM-/Persona-Call
ausloesen, der Tisch bleibt `active`; nach Wiederherstellung der
Originalbytes (nur im temporaeren Testverzeichnis) muss ein weiterer
echter, eigenstaendiger Folgeprozess denselben Tisch OHNE erneute
Zustimmung real abschliessen.

Ueber den Dateinamen `test_*.py` automatisch in `run_all.py` eingebunden."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_r2c_lobby_resume_zuordnung_guard as r2c  # noqa: E402

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402


def _child_main(args: argparse.Namespace) -> None:
    """Laeuft NUR im relaunchten Subprozess (`--child`) -- echte, andere
    Betriebssystem-PID als der aufrufende Testprozess. Identisch zu
    `test_r2c`s `_child_main`, ausser dem zusaetzlichen Fehlerinjektions-
    Modus `resolution-write-failure` (patcht `Path.open` genau EINMAL fuer
    den echten JSONL-Resolutionappend, s. Moduldocstring)."""
    root = Path(args.root)
    l01 = r2c.l01
    schema_path, states_dir, run_dir = l01._SCHEMA, root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

    drivers = {pk: r2c._ChildDriver(pk, args.mode) for pk in ("sniper", "tech")}
    gms: list = []
    hits: list[dict] = []

    def gm_transport_factory(tid: str):
        saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        for pk, s in saves.items():
            s["save_id"] = f"repo-regression-open-offer-guard-{tid}-{pk}"
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
    target = run_dir / "invitation_decisions.jsonl"
    original_open = Path.open

    class _AppendFile:
        """Identische Technik wie `tests-review/review_open_offer_resume.py`s
        `AppendFile` -- faengt genau den EINEN `write()` des echten
        Resolution-Appendrecords ab, alle anderen Writes bleiben normal."""

        def __init__(self, fh):
            self._fh = fh

        def __enter__(self):
            self._fh.__enter__()
            return self

        def __exit__(self, *exc):
            return self._fh.__exit__(*exc)

        def __getattr__(self, name):
            return getattr(self._fh, name)

        def write(self, value):
            try:
                rec = json.loads(value)
            except (ValueError, TypeError):
                rec = {}
            if rec.get("type") == "resolution" and not hits:
                hits.append({"seam": "actual resolution file append write", "errno": 5})
                raise OSError(5, "SYNTHETIC one failed resolution append")
            return self._fh.write(value)

    def open_file(path, *file_args, **file_kwargs):
        mode = file_args[0] if file_args else file_kwargs.get("mode", "r")
        fh = original_open(path, *file_args, **file_kwargs)
        if args.mode == "resolution-write-failure" and path == target and "a" in mode:
            return _AppendFile(fh)
        return fh

    with patch.object(Path, "open", open_file):
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


def _protected_snapshot(root: Path) -> dict[str, str]:
    """Byte-genauer Fingerabdruck aller geschuetzten Belege (Tische, Locks,
    Angebots-/Resolutionlog, veroeffentlichte Currents, States) -- der
    Konsistenz-Guard darf beim Hold KEINE davon veraendern, auch nicht
    zusaetzlich zur bewusst gesetzten Testkorruption."""
    paths = [root / "run" / "locks.json", root / "run" / "invitation_decisions.jsonl"]
    for d in (root / "run" / "tables", root / "run" / "current_saves", root / "states"):
        if d.exists():
            paths.extend(p for p in d.rglob("*") if p.is_file())
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths if p.exists()
    }


def _seed_unresolved_open_offer(root: Path) -> dict:
    """Baut ueber den ECHTEN Handler ein vollstaendig bestaetigtes,
    UNRESOLVIERTES Angebot samt bereits angelegtem/gesperrtem offenem
    Tisch -- der genau EINMAL injizierte `OSError` trifft den echten
    JSONL-Resolutionappend, KEINE Produktquelle wird nachtraeglich vom Test
    manipuliert (nur ein markierter Fehler am vorgesehenen Schreibpfad)."""
    r2c._seed(root)
    r1 = _run_child(root, "resolution-write-failure", root / "01-initial.json")
    assert not r1["errors"], r1["errors"]
    assert r1["gm_calls"] == 0
    assert len(r1["tables"]) == 1
    table = r1["tables"][0]
    assert table["status"] == "active" and table["leader"] == "sniper"
    assert len(r1["hits"]) == 1, "genau ein injizierter Resolution-Appendfehler erwartet"
    rows = [json.loads(line) for line in r1["offers"].splitlines()] if r1["offers"] else []
    assert any(r.get("type") == "offer" for r in rows)
    assert not any(r.get("type") == "resolution" for r in rows), (
        "Testannahme verletzt: Resolution wurde trotz injiziertem Fehler geschrieben"
    )
    return r1


def test_open_offer_guard_consistent_relation_resumes_and_completes():
    """Erhalt (B1 ohne Resolution, konsistent): der allgemeine Angebotszweig
    muss ein vollstaendig bestaetigtes, unresolviertes Angebot weiterhin
    real abschliessen -- fehlende Resolution wird idempotent nachgezogen,
    kein zweiter Tisch, keine erneute Zustimmung."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r1 = _seed_unresolved_open_offer(root)
        tid = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "pause", root / "01-resume.json")
        assert not r2["errors"], r2["errors"]
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid, "Resume muss denselben Tisch nutzen"
        assert r2["tables"][0]["status"] == "closed", "konsistente Belege muessen real bis zum Abschluss fortsetzen"
        assert r2["gm_calls"] >= 3
        assert not r2["locks"]
        assert all(v is not None for v in r2["current_ids"].values())
        assert '"outcome": "table_bound"' in r2["offers"], "fehlende B1-Resolution muss idempotent nachgezogen werden"
        assert r2c._own_decision_calls(r2) == 0, "kein neuer Initiativ-/Consent-Request bei konsistenter Wiederaufnahme"


def _negative_case(corrupt, label: str) -> dict:
    """Gemeinsames Geruest fuer missing-map/missing-lock: unresolviertes
    Angebot ueber den echten Handler anlegen, EINE begrenzte wohlgeformte
    widerspruechliche Testeingabe injizieren (Originalbytes separat
    aufbewahrt), Resume-Versuch ueber den allgemeinen Angebotszweig
    beobachten (muss VOR jeder Personaentscheidung und jedem GM-Turn
    kontrolliert offen bleiben, geschuetzte Bytes exakt unveraendert),
    Originalbytes wiederherstellen, echten Restore-Resume beobachten (muss
    danach real abschliessen, ohne erneute Zustimmung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r1 = _seed_unresolved_open_offer(root)
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        locks_path = root / "run" / "locks.json"
        original_table_bytes = table_path.read_bytes()
        original_locks_bytes = locks_path.read_bytes()

        corrupt(table_path, locks_path)
        before = _protected_snapshot(root)

        r2 = _run_child(root, "pause", root / f"{label}-conflict.json")
        after = _protected_snapshot(root)

        assert not r2["errors"], (
            f"eine konkrete kontrollierte Meldung wird erwartet, keine rohe Ausnahme: {r2['errors']}"
        )
        assert r2c._own_decision_calls(r2) == 0, "kein Persona-/Consent-Call vor dem Hold"
        assert r2["gm_calls"] == 0, "kein GM-/Spielstart bei widerspruechlichen Belegen"
        assert r2["tables"][0]["status"] == "active", "Tisch bleibt bei widerspruechlichen Belegen aktiv"
        assert before == after, (
            "geschuetzte Bytes (Tables/Locks/Angebotslog/Currents/States) duerfen sich "
            "beim Hold NICHT zusaetzlich veraendern -- insbesondere KEINE neue Resolution "
            "als Scheinreparatur"
        )
        assert any(tid in p for p in r2["printed"]), f"konkrete Tisch-ID in der Meldung erwartet: {r2['printed']}"

        table_path.write_bytes(original_table_bytes)
        locks_path.write_bytes(original_locks_bytes)

        r3 = _run_child(root, "pause", root / f"{label}-restored.json")
        assert not r3["errors"], r3["errors"]
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["tables"][0]["status"] == "closed", "nach Wiederherstellung muss derselbe Tisch real abschliessen"
        assert r3["gm_calls"] >= 3
        assert not r3["locks"]
        assert all(v is not None for v in r3["current_ids"].values())
        assert r2c._own_decision_calls(r3) == 0, "kein erneuter Initiativ-/Consent-Request nach Restore-Resume"
        return {"table_id": tid, "conflict_held_open": True, "restore_resume_completed": True}


def test_open_offer_guard_missing_chrononaut_entry_holds_then_restores():
    """Fall missing-map: `Table.chrononaut_ids['sniper']` fehlt beim noch
    unresolvierten Angebot -- frueher erreichte dieser Zweig den Guard gar
    nicht, eine Personaentscheidung lief bereits, danach roher
    `KeyError('sniper')`, samt bereits nachgeschriebener Resolution."""

    def corrupt(table_path: Path, locks_path: Path) -> None:
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        assert "sniper" in obj["chrononaut_ids"], "Testannahme verletzt: 'sniper' fehlte bereits vor der Korruption"
        del obj["chrononaut_ids"]["sniper"]
        table_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _negative_case(corrupt, "02-missing-chrononaut")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_open_offer_guard_missing_member_lock_holds_then_restores():
    """Fall missing-lock: Snipers Mitgliedslock fehlt (chrononaut_ids bleibt
    vollstaendig) -- frueher schloss der gesamte Abschnitt trotz fehlender
    notwendiger Bindung ab."""

    def corrupt(table_path: Path, locks_path: Path) -> None:
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        cid = obj["chrononaut_ids"]["sniper"]
        locks = json.loads(locks_path.read_text(encoding="utf-8"))
        assert cid in locks, "Testannahme verletzt: Sniper-Lock fehlte bereits vor der Korruption"
        del locks[cid]
        locks_path.write_text(json.dumps(locks, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _negative_case(corrupt, "03-missing-lock")
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
        test_open_offer_guard_consistent_relation_resumes_and_completes,
        test_open_offer_guard_missing_chrononaut_entry_holds_then_restores,
        test_open_offer_guard_missing_member_lock_holds_then_restores,
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
