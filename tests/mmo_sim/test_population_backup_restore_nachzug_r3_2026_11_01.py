#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_nachzug_r3_2026_11_01.py --
Gezielte Restnachweise F2/F4 des R3-Nachzugs (ZR-POPULATION-BACKUP-RESTORE-
NACHZUG-20261101-R3) auf dem PR3297-Stand.

F2: EINE hinreichende Generationsgueltigkeit bis in Publish, Status, `backup
retry` und Restore (manifest-only-Schaden; `done` bei entzogener Generation,
ueber den TATSAECHLICHEN TUI-Bedienweg sichtbar + retrybar).
F4: aufgenommenes Inventar/Capturebindung beim Restore; atomare Aktivierung mit
kontrolliertem Fallback-Abbruch (kein Teilroot).

Produktpersistenz/Status/Retry/Restore laufen ECHT; nur GM-/Persona-Treiber
sind Fakes. Bei gesetztem `ZR_R3_ARTIFACT_DIR` werden kleine nichtgeheime
Ergebnis-JSONs dort abgelegt (G1). Runner: `tests/mmo_sim/run_all.py`."""
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

_AT = "2026-11-01T00:00:00+00:00"
_ARTIFACT_DIR = os.environ.get("ZR_R3_ARTIFACT_DIR")


def _emit(name, obj):
    if not _ARTIFACT_DIR:
        return
    d = Path(_ARTIFACT_DIR)
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _tui_for(fx, participant="p_r3"):
    """TuiSession, deren abgeleitete Backup-Roots EXAKT mit dem Fixture
    uebereinstimmen (onboarding.parent == fx.root)."""
    printed: list[str] = []
    s = TuiSession(
        fx.roots.onboarding_dir, fx.roots.catalog_dir, participant,
        input_fn=lambda prompt="": "", print_fn=printed.append,
        run_dir=fx.roots.run_dir, states_dir=fx.roots.states_dir,
    )
    return s, printed


# ── F2: manifest-only-Schaden ──────────────────────────────────────────────


def test_f2r3_manifest_only_damage_target_is_not_treated_as_good():
    """F2: nur die `manifest.json` des Ziels fehlt, die Payloads sind intakt.
    `_publish_generation` darf das NICHT wegen passender Payloads als gut
    behandeln -- das frisch gepruefte Staging ersetzt das defekte Ziel; Latest
    zeigt auf tatsaechlich gueltige Bytes."""
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

        # NUR das Manifest des Ziels entfernen (Payloads bleiben intakt) + Task pending.
        (br / "generations" / gid / "manifest.json").unlink()
        assert pb._generation_already_valid(br, gid) is None, "manifest-only-Schaden muss ungueltig sein"
        pb._write_task(br, gid, {
            "generation_key": key.as_string(), "generation_id": gid, "status": "pending",
            "completion_fingerprint": comp, "completion_fingerprint_known": True,
        })

        out = pb.generate_population_backup(
            fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
            created_at_utc=_AT, capture_is_at_completion=True,
        )
        assert out.status == "created", out.status
        assert pb._generation_already_valid(br, gid) is not None, "Ziel muss nach Publish wieder gueltig sein"
        assert pb.read_latest(br)["generation_id"] == gid
        _emit("f2r3_manifest_only.json", {"status": out.status, "target_valid_after": True})


def test_f2r3_done_missing_generation_visible_and_retryable_via_tui():
    """F2: eine `done`-Generation wird entzogen. Der TATSAECHLICHE TUI-Status
    (`backup`) darf sie nicht mehr als 'letzte gute Generation' ausgeben, und
    `backup retry` muss sie ueber den angebotenen Bedienweg nachholen (keine
    bloss direkte Generatorreparatur)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        assert pf.run_backup(fx).status == "created"
        gid = key.generation_id()

        # veroeffentlichte done-Generation entziehen
        shutil.rmtree(br / "generations" / gid)

        session, printed = _tui_for(fx)
        printed.clear()
        session._cmd_backup([])  # Status
        status_text = "\n".join(printed)
        # Darf nicht faelschlich als letzte gute Generation + "keine offenen" melden
        assert gid not in status_text or "Offene" in status_text or "fehlgeschlagen" in status_text.lower() \
            or "(keine)" in status_text, status_text
        status = pb.read_backup_status(br, fx.roots)
        assert status["latest_generation_id"] is None, "entzogene Generation darf nicht 'letzte gute' sein"
        assert any(t["generation_id"] == gid for t in status["open_tasks"]), "muss als offen/retrybar erscheinen"

        printed.clear()
        session._cmd_backup(["retry"])  # Bedienweg-Retry
        retry_text = "\n".join(printed)
        assert pb._generation_already_valid(br, gid) is not None, "retry muss die Generation nachholen"
        assert pb.read_backup_status(br, fx.roots)["latest_generation_id"] == gid
        _emit("f2r3_done_missing_via_tui.json", {
            "status_output": status_text[-600:], "retry_output": retry_text[-600:],
            "generation_valid_after_retry": True,
        })


# ── F4: Inventar-/Capturebindung + atomare Aktivierung ─────────────────────


def test_f4r3_removed_inactive_figure_rejected_by_capture_fingerprint():
    """F4: eine nachweislich AUFGENOMMENE inaktive Figur (Katalog) wird samt
    ihrer Manifestzeile entfernt, der Rest bleibt. Der Bestand ist nichtleer,
    aber die Dateiliste passt nicht mehr zum gebundenen Aufnahme-Fingerprint ->
    kontrollierte Ablehnung vor Aktivierung. Die unveraenderte gute Generation
    bleibt restaurierbar."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        assert pf.run_backup(fx).status == "created"
        gid = key.generation_id()
        gen_dir = br / "generations" / gid
        manifest = json.loads((gen_dir / "manifest.json").read_text(encoding="utf-8"))

        # aufgenommene inaktive Figur im Katalog finden
        inactive = [f for f in manifest["files"]
                    if f["role"] == "catalog" and pf.INACTIVE_CHRONONAUT_ID in f["rel_path"]]
        assert inactive, "Fixtureannahme: inaktive Figur im Katalog aufgenommen"
        victim = inactive[0]

        # Datei + Manifestzeile entfernen, capture-Block unveraendert lassen
        (gen_dir / "catalog" / victim["rel_path"]).unlink()
        manifest["files"] = [f for f in manifest["files"] if f is not victim]
        (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        rejected = False
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError as exc:
            rejected = True
            assert "Aufnahme-Fingerprint" in str(exc) or "Inventar" in str(exc), str(exc)
        assert rejected, "entfernte aufgenommene Figur muss abgelehnt werden"

        # unveraenderte gute Generation (frisch) bleibt restaurierbar
        with tempfile.TemporaryDirectory() as td2:
            root2 = Path(td2) / "data"
            fx2 = pf.build_fixture(root2)
            assert pf.play_section_to_success(fx2).completion.success
            br2 = pf.backup_root_for(fx2)
            assert pf.run_backup(fx2).status == "created"
            target2 = Path(td2) / "restored"
            ro = pb.restore_population(br2, target2)
            assert (target2 / "catalog").is_dir()
            _emit("f4r3_removed_inactive_figure.json", {
                "victim_rel_path": victim["rel_path"], "rejected_tampered": True,
                "good_generation_restores": ro.generation_id is not None,
            })


def test_f4r3_identity_binding_rejected_on_mismatched_manifest():
    """F4: eine Generation, deren Manifest-run/table/section nicht die
    Generation-ID ergeben, wird vor Aktivierung abgelehnt (Identitaetsbindung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        assert pf.run_backup(fx).status == "created"
        gid = key.generation_id()
        gen_dir = br / "generations" / gid
        manifest = json.loads((gen_dir / "manifest.json").read_text(encoding="utf-8"))
        manifest["section_id"] = "ein-ganz-anderer-abschnitt"  # Identitaet verfaelschen
        (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        rejected = False
        try:
            pb.validate_generation_for_restore(br, gid)
        except pb.RestoreRejectedError as exc:
            rejected = True
            assert "Identitaetsbindung" in str(exc), str(exc)
        assert rejected
        _emit("f4r3_identity_binding.json", {"rejected": True})


def test_f4r3_atomic_activation_fallback_controlled_reject_no_partial_root():
    """F4: ohne verfuegbare `renameat2`-Operation wird KONTROLLIERT vor jeder
    Zielanlage abgelehnt -- kein sichtbarer Teilroot, kein Eingriff in ein
    fremdes Ziel. (ENOSYS-aequivalent durch fehlendes Symbol erzwungen.)"""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"
        target = Path(td) / "restored"

        class _NoRenameat2:
            def __getattr__(self, name):
                if name == "renameat2":
                    raise AttributeError("kein renameat2 (simuliert)")
                raise AttributeError(name)

        orig_cdll = pb.ctypes.CDLL
        pb.ctypes.CDLL = lambda *a, **k: _NoRenameat2()
        try:
            rejected = False
            try:
                pb.restore_population(br, target)
            except pb.RestoreRejectedError as exc:
                rejected = True
                assert "nicht atomar" in str(exc), str(exc)
            assert rejected, "ohne renameat2 muss kontrolliert abgelehnt werden"
        finally:
            pb.ctypes.CDLL = orig_cdll

        assert not target.exists(), "kein Teilroot vor der Ablehnung"
        assert [p for p in target.parent.glob(".restore-*")] == [], "eigenes Staging bereinigt"
        _emit("f4r3_atomic_fallback_reject.json", {"rejected": True, "partial_root": False})


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
