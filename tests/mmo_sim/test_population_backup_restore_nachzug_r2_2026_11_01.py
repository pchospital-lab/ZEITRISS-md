#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_nachzug_r2_2026_11_01.py --
Gezielte Restnachweise F1a/F1b/F2a/F2b/F3/F4 des R2-Nachzugs
(ZR-POPULATION-BACKUP-RESTORE-NACHZUG-20261101-R2) zusaetzlich zu den
R1-Nachzugtests.

Jede Testfunktion bildet GENAU eine der verbleibenden Vertragsluecken aus
`review/CODE-REVIEW.md`/`01_BEFUND.md` des R2-Auftrags ab. Produktpersistenz,
Konsistenz-, Publish- und Restorelogik laufen ECHT; nur GM-/Persona-Treiber
sind Fakes (Transportrand). Fehlerfaelle (I/O, pausierter Mehrdateiwrite,
Race ums Restoreziel, defekte Generation) werden am Dateisystem/Transport
simuliert.

Wenn die Umgebungsvariable `ZR_R2_ARTIFACT_DIR` gesetzt ist, legen die Tests
zusaetzlich kleine, nichtgeheime Ergebnis-JSONs dort ab (G1: Ergebnisdaten des
tatsaechlichen finalen Laufs). Ohne die Variable ist das ein No-op.

Pure Python, nur `assert`, echter Exitcode; Runner `tests/mmo_sim/run_all.py`."""
from __future__ import annotations

import json
import os
import stat
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
from mmo_sim.core import store  # noqa: E402

_AT = "2026-11-01T00:00:00+00:00"
_ARTIFACT_DIR = os.environ.get("ZR_R2_ARTIFACT_DIR")


def _emit(name: str, obj: dict) -> None:
    """G1: kleine nichtgeheime Ergebnisdaten ausserhalb des temporaeren
    Testroots ablegen, wenn `ZR_R2_ARTIFACT_DIR` gesetzt ist."""
    if not _ARTIFACT_DIR:
        return
    d = Path(_ARTIFACT_DIR)
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _leader_ref_seq(fx) -> int:
    state = json.loads((fx.roots.states_dir / f"{pf.LEADER_PK}.json").read_text(encoding="utf-8"))
    return int(state[pb._CURRENT_SAVE_REF_FIELD]["seq"])


def _sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── F1a: Konsistenz an den TATSAECHLICH kopierten Bytes ────────────────────


def test_f1a_staged_recheck_catches_inconsistency_missed_by_precheck():
    """F1a: ein pausierter Mehrdateiwriter, der ERST NACH der semantischen
    Vorpruefung einen gemischten Stand hinterlaesst, wuerde von der Vorpruefung
    nicht erkannt. Die zusaetzliche Pruefung an den kopierten Staging-Bytes muss
    ihn trotzdem fangen: kein `created`, kein veroeffentlichter Mischstand, G0
    bleibt letzte gute Generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        g0 = pf.run_backup(fx)
        assert g0.status == "created"

        # Paused publish: neue Versionsdatei seq+1, State-Ref bleibt auf seq.
        seq = _leader_ref_seq(fx)
        versions = fx.roots.run_dir / "current_saves" / f"{pf.LEADER_PK}__versions"
        (versions / f"{seq + 1:04d}.json").write_text(
            json.dumps({"v": 2, "persona_key": pf.LEADER_PK, "rounds_played": 1, "paused": True}),
            encoding="utf-8",
        )

        # Vorpruefung simuliert verpassen (Writer pausierte erst DANACH): erster
        # Aufruf von verify_population_consistency liefert [], der zweite (an den
        # Staging-Bytes) laeuft echt.
        real = pb.verify_population_consistency
        calls = {"n": 0}

        def patched(roots):
            calls["n"] += 1
            return [] if calls["n"] == 1 else real(roots)

        pb.verify_population_consistency = patched
        try:
            key2 = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=f"{fx.table_id}-sec-x")
            out = pb.generate_population_backup(
                fx.roots, key2, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                created_at_utc=_AT, capture_is_at_completion=True,
            )
        finally:
            pb.verify_population_consistency = real

        assert out.status == "failed_inconsistent", out.status
        assert calls["n"] == 2, "Staging-Recheck muss zusaetzlich zur Vorpruefung laufen"
        assert not (br / "generations" / key2.generation_id()).exists()
        latest = pb.read_latest(br)
        assert latest and latest["generation_id"] == g0.generation_id
        _emit("f1a_staged_recheck.json", {
            "precheck_then_staged_calls": calls["n"], "status": out.status,
            "mixed_state_published": (br / "generations" / key2.generation_id()).exists(),
            "latest_still_g0": latest["generation_id"] == g0.generation_id,
        })


# ── F1b: echte Abschlussgrenze (Finalmarker + persistierter closed) ────────


def test_f1b_final_marker_without_closed_table_is_not_a_completion():
    """F1b: ein Finalmarker allein (Absturz vor persistiertem Tischstatus
    `closed`) ist KEIN konsistenter Abschluss. Weder Rekonstruktion noch Hook
    duerfen daraus eine Sicherung ableiten; der unbeteiligte offene Tisch bleibt
    offen. Nach echtem `closed` funktioniert beides wieder."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)

        tfile = fx.roots.run_dir / "tables" / f"{fx.table_id}.json"
        tdata = json.loads(tfile.read_text(encoding="utf-8"))
        assert tdata["status"] == "closed", "Fixtureannahme: play schliesst den Tisch"
        # Crash-Fenster simulieren: Finalmarker da, Tischstatus noch NICHT closed.
        tdata_open = dict(tdata, status="open")
        tfile.write_text(json.dumps(tdata_open), encoding="utf-8")

        assert pb.section_completion_consistent(fx.roots.run_dir, fx.table_id, fx.section_id) is False
        assert key.generation_id() not in pb.reconstruct_missing_backup_tasks(fx.roots, br)
        res = pb.backup_after_section_completed(
            completion_success=True, run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id,
            roots=fx.roots, backup_root=br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
        )
        assert res is None, "Hook darf fuer einen unfertigen Abschluss kein Backup erzeugen"
        # unbeteiligter offener Tisch bleibt offen
        open_tbl = store.Table.load(fx.roots.run_dir, fx.open_table_id)
        assert open_tbl.status != "closed"

        # Nach echtem closed funktioniert beides.
        tfile.write_text(json.dumps(tdata), encoding="utf-8")
        assert pb.section_completion_consistent(fx.roots.run_dir, fx.table_id, fx.section_id) is True
        res2 = pb.backup_after_section_completed(
            completion_success=True, run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id,
            roots=fx.roots, backup_root=br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
        )
        assert res2 is not None and res2.succeeded
        _emit("f1b_final_before_closed.json", {
            "consistent_when_open": False, "hook_declined_when_open": res is None,
            "open_table_stays_open": open_tbl.status != "closed",
            "consistent_when_closed": True, "hook_ok_when_closed": bool(res2 and res2.succeeded),
        })


# ── F2a: unbekannter historischer Bezug bleibt unbekannt ───────────────────


def _change_b(fx) -> None:
    current = store.load_current_save_or_raise(
        fx.roots.run_dir, pf.LEADER_PK, fx.ps_store, states_dir=fx.roots.states_dir)
    current["characters"][0]["xp"] = 777
    store.publish_current_save(fx.roots.run_dir, pf.LEADER_PK, current, fx.ps_store, fx.roots.states_dir)


def test_f2a_reconstructed_retry_without_binding_reports_unknown_not_true():
    """F2a (Crash vor erstem Task): ohne dauerhaft gebundenen
    Abschlussfingerprint wird eine spaetere Aufnahme NICHT als
    `matches_section_completion=true` ausgewiesen, sondern ausdruecklich als
    unbekannter historischer Bezug."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        assert not (br / "backup_tasks").exists()  # Crash VOR erstem Taskwrite

        _change_b(fx)  # echte spaetere Produktaenderung B

        assert key.generation_id() in pb.reconstruct_missing_backup_tasks(fx.roots, br)
        out = pb.retry_population_backup(fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT)
        assert out.status == "created", out.status
        cap = out.manifest["capture"]
        assert cap["completion_binding_known"] is False
        assert cap["captured_state_matches_section_completion"] is None, cap
        assert "UNBEKANNT" in cap["note"]
        _emit("f2a_unknown_binding.json", {"capture": cap})


def test_f2a_persistent_task_target_failure_then_b_reports_unknown():
    """F2a (anhaltender Taskziel-Fehler): wenn weder Pending- noch Fehlerstatus
    dauerhaft geschrieben werden konnten, darf eine spaetere Aufnahme nach
    Aenderung B ebenfalls keinen historischen Gleichheitsbeweis behaupten."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)

        # Anhaltender Fehler des ersten Taskziels (auch im best-effort-Handler).
        orig = pb._write_task

        def boom(*a, **k):
            raise OSError("anhaltender Taskziel-Fehler")

        pb._write_task = boom
        try:
            out_a = pb.generate_population_backup(
                fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                created_at_utc=_AT, capture_is_at_completion=True,
            )
        finally:
            pb._write_task = orig
        assert out_a.status == "failed"
        assert not (br / "backup_tasks" / f"{key.generation_id()}.json").exists(), "kein dauerhafter Task"

        _change_b(fx)
        out_b = pb.retry_population_backup(fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT)
        assert out_b.status == "created", out_b.status
        cap = out_b.manifest["capture"]
        assert cap["completion_binding_known"] is False
        assert cap["captured_state_matches_section_completion"] is None, cap
        _emit("f2a_persistent_failure.json", {"attempt_a": out_a.status, "capture_b": cap})


# ── F2b: done/defekte Generation + Publish-Ersetzung ───────────────────────


def test_f2b_done_with_missing_generation_is_not_already_done():
    """F2b: ein `done`-Task bescheinigt keinen Erfolg, wenn die veroeffentlichte
    Generation entzogen/beschaedigt ist -- kein falsches `already_done`, sondern
    kontrollierte Neuaufnahme."""
    import shutil
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        g0 = pf.run_backup(fx)
        assert g0.status == "created"
        gid = key.generation_id()

        # veroeffentlichte Generation entziehen, done-Task bleibt
        shutil.rmtree(br / "generations" / gid)
        assert pb._generation_already_valid(br, gid) is None

        out = pf.run_backup(fx)
        assert out.status == "created", f"erwartet Neuaufnahme statt already_done: {out.status}"
        assert pb._generation_already_valid(br, gid) is not None, "Generation muss neu vorliegen"
        _emit("f2b_done_missing_generation.json", {"reaction": out.status, "generation_restored": True})


def test_f2b_publish_replaces_corrupt_existing_target_not_discard_good_staging():
    """F2b: ein vorhandenes, aber BESCHAEDIGTES Zielverzeichnis darf nicht als
    gueltige Sicherung behandelt werden -- das frisch gepruefte Staging ersetzt
    es, Latest zeigt auf tatsaechlich gueltige Bytes."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        g0 = pf.run_backup(fx)
        assert g0.status == "created"
        gid = key.generation_id()
        comp = json.loads((br / "backup_tasks" / f"{gid}.json").read_text(encoding="utf-8")).get("completion_fingerprint")

        # vorhandenes Ziel beschaedigen + Task auf pending (unvollstaendig)
        victim = next((br / "generations" / gid / "states").glob("*.json"))
        victim.write_text("CORRUPT-NICHT-JSON", encoding="utf-8")
        assert pb._generation_already_valid(br, gid) is None
        pb._write_task(br, gid, {
            "generation_key": key.as_string(), "generation_id": gid, "status": "pending",
            "completion_fingerprint": comp, "completion_fingerprint_known": True,
        })

        out = pb.generate_population_backup(
            fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
            created_at_utc=_AT, capture_is_at_completion=True,
        )
        assert out.status == "created", out.status
        assert pb._generation_already_valid(br, gid) is not None, "defektes Ziel muss ersetzt sein"
        assert pb.read_latest(br)["generation_id"] == gid
        _emit("f2b_publish_replaces_corrupt.json", {"status": out.status, "target_valid_after": True})


# ── F3: stiller Scanverlust wird kontrollierter Fehler ─────────────────────


def test_f3_unreadable_required_subtree_fails_controlled_and_preserves_g0():
    """F3: ein nicht traversierbarer benoetigter Unterbaum (Berechtigungsfehler)
    in einer rekursiven Rolle darf NICHT stillschweigend aus dem Snapshot
    verschwinden -- die Aufnahme scheitert kontrolliert, G0 bleibt gueltig."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        g0 = pf.run_backup(fx)
        assert g0.status == "created"

        locked = fx.roots.catalog_dir / "locked_subtree"
        locked.mkdir()
        (locked / "needed.json").write_text(json.dumps({"needed": True}), encoding="utf-8")
        os.chmod(locked, 0o000)
        try:
            if os.access(locked, os.R_OK):  # als root nicht blockierbar -> Test uebersprungen
                _emit("f3_scan_error.json", {"skipped": "running as root, perms not enforced"})
                return
            key2 = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=f"{fx.table_id}-sec-f3")
            out = pb.generate_population_backup(
                fx.roots, key2, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                created_at_utc=_AT, capture_is_at_completion=True,
            )
            assert out.status == "failed", f"stiller Scanverlust statt kontrolliertem Fehler: {out.status}"
            assert not (br / "generations" / key2.generation_id()).exists()
            latest = pb.read_latest(br)
            assert latest and latest["generation_id"] == g0.generation_id, "G0 muss erhalten bleiben"
            _emit("f3_scan_error.json", {
                "status": out.status, "partial_published": False,
                "g0_preserved": latest["generation_id"] == g0.generation_id,
            })
        finally:
            os.chmod(locked, 0o755)


# ── F4: atomare Nichtueberschreibung auch LEERER fremder Ziele ─────────────


def test_f4_empty_foreign_target_is_not_overwritten():
    """F4: ein zwischen Vorpruefung und Aktivierung fremd angelegtes LEERES
    Zielverzeichnis darf NICHT ersetzt werden (echte atomare
    Nichtueberschreibung, nicht nur der nichtleere Fall)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"
        target = Path(td) / "restored"

        orig_mkdtemp = pb.tempfile.mkdtemp

        def racing(*a, **k):
            d = orig_mkdtemp(*a, **k)
            target.mkdir(parents=True, exist_ok=True)  # fremdes LEERES Ziel
            return d

        pb.tempfile.mkdtemp = racing
        try:
            rejected = False
            try:
                pb.restore_population(br, target)
            except pb.RestoreRejectedError:
                rejected = True
            assert rejected, "leeres fremdes Ziel muss atomar abgelehnt werden"
        finally:
            pb.tempfile.mkdtemp = orig_mkdtemp

        assert target.exists() and target.is_dir()
        assert list(target.iterdir()) == [], "fremdes leeres Ziel wurde veraendert/ersetzt"
        # kein verwaistes Staging
        assert [p for p in target.parent.glob(".restore-*")] == []
        _emit("f4_empty_foreign_target.json", {"rejected": True, "foreign_target_untouched": True})


def test_f4_validation_rejects_empty_manifest_and_symlink_ancestor():
    """F4: ein leeres Manifest (leere Population) und ein Symlink-Vorfahre im
    Generationsbaum werden vor jeder Aktivierung kontrolliert abgelehnt."""
    with tempfile.TemporaryDirectory() as td:
        br = Path(td) / "bk"
        # leeres Manifest
        _make_generation(br, "gen-empty", [])
        _assert_reject(br, "gen-empty", "leere Population")

        # Symlink-Vorfahre: role-dir 'states' als Link
        gen = _make_generation(br, "gen-anc", [("states", "x.json", b"{}")])
        real = gen / "states"
        aside = gen / "states__real"
        real.rename(aside)
        (gen / "states").symlink_to(aside, target_is_directory=True)
        _assert_reject(br, "gen-anc", "Symlink-Vorfahre")
        _emit("f4_validation_rejections.json", {"empty_manifest_rejected": True, "symlink_ancestor_rejected": True})


# ── Hilfen fuer synthetische Generationen ──────────────────────────────────


def _make_generation(backup_root: Path, gid: str, entries: list[tuple[str, str, bytes]]) -> Path:
    import hashlib
    gen_dir = backup_root / "generations" / gid
    gen_dir.mkdir(parents=True, exist_ok=True)
    files_meta = []
    for role, rel_path, content in entries:
        p = gen_dir / role / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        files_meta.append({"role": role, "rel_path": rel_path, "size": len(content),
                           "sha256": hashlib.sha256(content).hexdigest()})
    manifest = {
        "schema_version": pb.SCHEMA_VERSION, "generation_id": gid,
        "run_id": "r", "table_id": "t", "section_id": "s", "created_at_utc": _AT,
        "producer_code_anchor": "test", "product_commit": "x", "prev_generation_id": None,
        "roots": sorted(pb.ROLES), "excluded": [], "files": files_meta,
    }
    (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return gen_dir


def _assert_reject(backup_root: Path, gid: str, needle: str) -> None:
    rejected = False
    try:
        pb.validate_generation_for_restore(backup_root, gid)
    except pb.RestoreRejectedError as exc:
        rejected = True
        assert needle in str(exc), f"{gid}: erwarteter Grund {needle!r} fehlt in: {exc}"
    assert rejected, f"{gid}: haette abgelehnt werden muessen ({needle})"


def main() -> int:
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
    raise SystemExit(main())
