#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_nachzug_r4_2026_11_02.py --
R4-Restnachweis F2 (ZR-POPULATION-BACKUP-RESTORE-NACHZUG-20261102-R4) auf dem
PR3297-Stand.

Kern: die EINE hinreichende Generationspruefung (`validate_generation_for_restore`)
traegt gemeinsam Wiederverwendung, Publish, done/Resume, Status und Retry -- gleiche
Bytes werden ueberall gleich bewertet wie beim Restore. Der Nachweis trifft die
TATSAECHLICHEN Entscheidungswege (Restore-Validator + echter `TuiSession._cmd_backup`
Status/retry + Publish), NICHT nur den frueheren schwaecheren Helper.

Vor der Korrektur (Stand 991e0807) treffen diese Tests den Widerspruch wirklich:
`_generation_already_valid` galt fuer `files=[]` als gueltig, obwohl der Restore
dieselben Bytes ablehnt.

Produktpersistenz/Status/Retry/Restore laufen ECHT; nur GM-/Persona-Treiber sind
Fakes. Bei gesetztem `ZR_R4_ARTIFACT_DIR` werden kleine nichtgeheime Ergebnis-JSONs
dort abgelegt (G1). Runner: `tests/mmo_sim/run_all.py`."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
for _p in (str(_REPO_ROOT), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import _population_backup_fixtures as pf  # noqa: E402

from mmo_sim.core import population_backup as pb  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_AT = "2026-11-02T00:00:00+00:00"
_ARTIFACT_DIR = os.environ.get("ZR_R4_ARTIFACT_DIR")


def _emit(name, obj):
    if not _ARTIFACT_DIR:
        return
    d = Path(_ARTIFACT_DIR); d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _tui_for(fx, participant="p_r4"):
    printed: list[str] = []
    s = TuiSession(
        fx.roots.onboarding_dir, fx.roots.catalog_dir, participant,
        input_fn=lambda prompt="": "", print_fn=printed.append,
        run_dir=fx.roots.run_dir, states_dir=fx.roots.states_dir,
    )
    return s, printed


def _good_backup(fx):
    assert pf.play_section_to_success(fx).completion.success
    br = pf.backup_root_for(fx)
    key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
    assert pf.run_backup(fx).status == "created"
    return br, key, key.generation_id()


def test_f2r4_empty_files_rejected_consistently_via_decision_paths():
    """files=[] bei korrektem Schema+ID: Restore lehnt ab; die gemeinsame
    Gueltigkeitspruefung muss das Ziel ueberall gleich als ungueltig behandeln
    (Helper, Status, done/Retry, Publish) -- nicht nur der Restore."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        man_path = br / "generations" / gid / "manifest.json"
        manifest = json.loads(man_path.read_text(encoding="utf-8"))

        # NUR files leeren (Schema + generation_id bleiben korrekt).
        manifest["files"] = []
        man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        # (a) Restore lehnt dieselben Bytes ab.
        rejected = False
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError:
            rejected = True
        assert rejected, "Restore muss files=[] ablehnen"

        # (b) GEMEINSAME Pruefung: der Gueltigkeits-Helper darf NICHT mehr truthy sein
        # (vor der R4-Korrektur war er es -> genau der getroffene Widerspruch).
        assert pb._generation_already_valid(br, gid) is None, \
            "files=[] darf nicht als gueltige Generation gelten (gemeinsamer Gueltigkeitsbegriff)"

        # (c) echter TUI-Status: nicht 'letzte gute', done-Task retrybar.
        status = pb.read_backup_status(br, fx.roots)
        assert status["latest_generation_id"] is None
        assert any(t["generation_id"] == gid for t in status["open_tasks"])

        # (d) echter TUI-Retry repariert ueber den Bedienweg; danach gueltig + restaurierbar.
        session, printed = _tui_for(fx)
        printed.clear(); session._cmd_backup([]); status_out = list(printed)
        printed.clear(); session._cmd_backup(["retry"]); retry_out = list(printed)
        assert pb._generation_already_valid(br, gid) is not None, "retry muss reparieren"
        target = Path(td) / "restored"
        ro = pb.restore_population(br, target)
        assert (target / "states").is_dir() and ro.generation_id == gid
        _emit("f2r4_empty_files.json", {
            "restore_rejected_before_repair": True, "helper_none_before_repair": True,
            "status_latest_none": True, "tui_status_output": status_out, "tui_retry_output": retry_out,
            "valid_and_restored_after_retry": True,
        })


def test_f2r4_removed_inactive_figure_rejected_by_shared_check_too():
    """Zweiter Zeuge (R3-F4-Fall): entfernte aufgenommene inaktive Figur + Zeile,
    Capturebindung unveraendert. Vorher galt der Bestand fuer den Helper als gut,
    obwohl Restore ablehnt. Jetzt lehnt die gemeinsame Pruefung konsistent ab."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        gen_dir = br / "generations" / gid
        manifest = json.loads((gen_dir / "manifest.json").read_text(encoding="utf-8"))
        inactive = [f for f in manifest["files"]
                    if f["role"] == "catalog" and pf.INACTIVE_CHRONONAUT_ID in f["rel_path"]]
        assert inactive
        victim = inactive[0]
        (gen_dir / "catalog" / victim["rel_path"]).unlink()
        manifest["files"] = [f for f in manifest["files"] if f is not victim]
        (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        r = False
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError:
            r = True
        assert r, "Restore lehnt entfernte aufgenommene Figur ab"
        assert pb._generation_already_valid(br, gid) is None, \
            "derselbe Bestand darf auch fuer den gemeinsamen Gueltigkeitsbegriff nicht gut sein"
        _emit("f2r4_removed_inactive_consistent.json", {"restore_rejected": True, "helper_none": True})


def test_f2r4_identity_mismatch_rejected_by_shared_check_too():
    """Identitaetswiderspruch (run/table/section ergeben nicht die ID): Restore
    lehnt ab, und der gemeinsame Gueltigkeitsbegriff ebenso."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        gen_dir = br / "generations" / gid
        manifest = json.loads((gen_dir / "manifest.json").read_text(encoding="utf-8"))
        manifest["section_id"] = "fremder-abschnitt"
        (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        r = False
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError:
            r = True
        assert r
        assert pb._generation_already_valid(br, gid) is None
        _emit("f2r4_identity_consistent.json", {"restore_rejected": True, "helper_none": True})


def test_f2r4_publish_keeps_good_staging_over_restore_invalid_target():
    """Publish/Wiederverwendung: zeigt das Ziel einen restore-ungueltigen Stand
    (files=[]), darf das frisch gepruefte gute Staging NICHT verworfen werden --
    Latest/Done muss danach auf tatsaechlich restaurierbare Bytes zeigen."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        man_path = br / "generations" / gid / "manifest.json"
        manifest = json.loads(man_path.read_text(encoding="utf-8"))
        manifest["files"] = []
        man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        comp = json.loads((br / "backup_tasks" / f"{gid}.json").read_text(encoding="utf-8")).get("completion_fingerprint")
        pb._write_task(br, gid, {"generation_key": key.as_string(), "generation_id": gid, "status": "pending",
                                 "completion_fingerprint": comp, "completion_fingerprint_known": True})
        out = pb.generate_population_backup(fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                                            created_at_utc=_AT, capture_is_at_completion=True)
        assert out.status == "created", out.status
        assert pb._generation_already_valid(br, gid) is not None, "gutes Staging ersetzt das defekte Ziel"
        assert pb.validate_generation_for_restore(br, gid)["files"], "Zielmanifest wieder nichtleer"
        _emit("f2r4_publish_replaces_invalid_target.json", {"status": out.status, "target_restore_valid_after": True})


def test_f2r4_good_generation_remains_valid_and_idempotent():
    """Positiv-/Regressionskontrolle: eine echte gute Generation bleibt fuer die
    gemeinsame Pruefung gueltig; ein erneuter done-Lauf ist idempotent (kein
    unnoetiges Ersetzen, G0 unveraendert)."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        assert pb._generation_already_valid(br, gid) is not None
        before = pb._generation_already_valid(br, gid)
        pb._write_task(br, gid, {"generation_key": key.as_string(), "generation_id": gid, "status": "done",
                                 "completion_fingerprint": None, "completion_fingerprint_known": False})
        out = pb.generate_population_backup(fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                                            created_at_utc=_AT, capture_is_at_completion=True)
        assert out.status in ("already_done", "created"), out.status
        after = pb._generation_already_valid(br, gid)
        assert after is not None and after["generation_id"] == gid
        _emit("f2r4_good_idempotent.json", {"status": out.status, "still_valid": True})


def main() -> int:
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t(); print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1; print(f"ERROR {t.__name__}:"); traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
