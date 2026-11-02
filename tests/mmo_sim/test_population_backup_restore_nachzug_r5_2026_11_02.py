#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_nachzug_r5_2026_11_02.py --
R5-Restnachweis F2_MANIFEST_ROOT_TYPE_REGRESSION
(ZR-POPULATION-BACKUP-RESTORE-NACHZUG-20261102-R5) auf dem PR3297-Stand.

Regression: Der gemeinsame `validate_generation_for_restore` greift nach dem
JSON-Lesen direkt mit `manifest.get(...)` zu. Ist der Dateiinhalt syntaktisch
gueltiges, aber nicht objektfoermiges JSON (`[]` oder `null`), warf das einen
ungefangenen `AttributeError`, der ueber Helper/Status/Retry propagierte und den
Bedienweg vor der Reparatur blockierte. Fix: kontrollierte Eingangsgrenze
(`isinstance(manifest, dict)`) im gemeinsamen Validator -> `RestoreRejectedError`,
die `_generation_already_valid` in "ungueltig" uebersetzt.

Vor der Korrektur (Stand 4bf5dedf) trifft dieser Test den unbehandelten Fehler
tatsaechlich. Produktpersistenz/Status/Retry/Restore laufen ECHT; nur GM-/Persona-
Treiber sind Fakes. Bei gesetztem `ZR_R5_ARTIFACT_DIR` werden kleine nichtgeheime
Ergebnis-JSONs dort abgelegt (G1). Runner: `tests/mmo_sim/run_all.py`."""
from __future__ import annotations

import json
import os
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
_ARTIFACT_DIR = os.environ.get("ZR_R5_ARTIFACT_DIR")


def _emit(name, obj):
    if not _ARTIFACT_DIR:
        return
    d = Path(_ARTIFACT_DIR); d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _tui_for(fx, participant="p_r5"):
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


def _root_type_probe(raw_json_text: str, label: str) -> dict:
    """Gemeinsame parametrisierte Probe fuer eine nicht objektfoermige
    Manifestwurzel (`[]` bzw. `null`): kontrollierte Ablehnung ueber alle
    Entscheidungswege + Reparatur ueber den echten Bedienweg."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        leader_before = fx.ps_store.load_state(pf.LEADER_PK, states_dir=fx.roots.states_dir)
        man_path = br / "generations" / gid / "manifest.json"
        # Manifestwurzel gezielt auf nicht objektfoermiges, aber gueltiges JSON setzen.
        man_path.write_text(raw_json_text, encoding="utf-8")
        assert json.loads(man_path.read_text(encoding="utf-8")) == json.loads(raw_json_text)  # syntaktisch gueltig

        # (1) direkter gemeinsamer Validator: KONTROLLIERTE Ablehnung (kein AttributeError).
        rejected = None
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError as exc:
            rejected = str(exc)
        except Exception as exc:  # pragma: no cover -- genau das ist der Vor-Fix-Fehler
            raise AssertionError(f"{label}: unkontrollierter Fehler statt RestoreRejectedError: {type(exc).__name__}: {exc}")
        assert rejected is not None, f"{label}: Validator muss nicht objektfoermiges Manifest ablehnen"

        # (2) _generation_already_valid uebersetzt in "ungueltig".
        assert pb._generation_already_valid(br, gid) is None, f"{label}: Helper muss None liefern"

        # (3) echter TUI-Status/Retry: nicht 'letzte gute'; Retry erreicht Reparatur.
        session, printed = _tui_for(fx)
        printed.clear(); session._cmd_backup([]); status_out = list(printed)
        status = pb.read_backup_status(br, fx.roots)
        assert status["latest_generation_id"] is None, f"{label}: beschaedigt != letzte gute"
        assert any(t["generation_id"] == gid for t in status["open_tasks"]), f"{label}: muss retrybar sein"
        printed.clear(); session._cmd_backup(["retry"]); retry_out = list(printed)

        # (4) nach Retry: reparierte Zielbytes mit DEMSELBEN Validator pruefen.
        repaired = pb.validate_generation_for_restore(br, gid)
        assert repaired["files"], f"{label}: reparierte Generation muss nichtleer sein"
        target = Path(td) / f"restored-{label}"
        ro = pb.restore_population(br, target)
        assert (target / "states").is_dir() and ro.generation_id == gid

        # (5) Primaersave/Spiel-/Reflexionseffekte durch reinen Retry unveraendert.
        leader_after = fx.ps_store.load_state(pf.LEADER_PK, states_dir=fx.roots.states_dir)
        primary_unchanged = (leader_before.get("rounds_played") == leader_after.get("rounds_played")
                             and leader_before.get("last_reflection") == leader_after.get("last_reflection"))
        assert primary_unchanged, f"{label}: reiner Retry darf Primaersave/Fortschritt nicht erneut anwenden"
        return {"label": label, "validator_rejection": rejected, "helper_none": True,
                "status_latest_none": True, "retried_and_restored": True,
                "primary_unchanged": primary_unchanged, "tui_status_output": status_out,
                "tui_retry_output": retry_out}


def test_f2r5_manifest_root_empty_list_controlled():
    res = _root_type_probe("[]", "empty_list")
    _emit("f2r5_root_empty_list.json", res)


def test_f2r5_manifest_root_null_controlled():
    res = _root_type_probe("null", "null")
    _emit("f2r5_root_null.json", res)


def test_f2r5_good_generation_idempotent_and_primary_unchanged():
    """Positiv-/Idempotenzkontrolle: eine echte gute Generation bleibt gueltig;
    ein erneuter done-Lauf ist idempotent und aendert den Primaersave nicht."""
    with tempfile.TemporaryDirectory() as td:
        fx = pf.build_fixture(Path(td) / "data")
        br, key, gid = _good_backup(fx)
        leader_before = fx.ps_store.load_state(pf.LEADER_PK, states_dir=fx.roots.states_dir)
        assert pb._generation_already_valid(br, gid) is not None
        pb._write_task(br, gid, {"generation_key": key.as_string(), "generation_id": gid, "status": "done",
                                 "completion_fingerprint": None, "completion_fingerprint_known": False})
        out = pb.generate_population_backup(fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                                            created_at_utc=_AT, capture_is_at_completion=True)
        assert out.status in ("already_done", "created"), out.status
        after = pb._generation_already_valid(br, gid)
        assert after is not None and after["generation_id"] == gid
        leader_after = fx.ps_store.load_state(pf.LEADER_PK, states_dir=fx.roots.states_dir)
        assert leader_before.get("rounds_played") == leader_after.get("rounds_played")
        _emit("f2r5_good_idempotent.json", {"status": out.status, "still_valid": True, "primary_unchanged": True})


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
