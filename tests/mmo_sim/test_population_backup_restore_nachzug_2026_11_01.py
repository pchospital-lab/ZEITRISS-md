#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_nachzug_2026_11_01.py --
Gezielte Nachzug-Nachweise F1-F6 (ZR-POPULATION-BACKUP-RESTORE-NACHZUG-
20261101-R1) zusaetzlich zu `test_population_backup_restore_2026_11_01.py`.

Jede Testfunktion bildet GENAU den in `02_NACHZUG.md`/`review/CODE-REVIEW.md`
verlangten gezielten Nachweis ab. Fakes NUR am GM-/Persona-Transportrand
(ueber `_population_backup_fixtures`); Produktpersistenz, Abschlusslogik,
Konsistenzpruefung, Backup und Restore laufen ECHT. Deterministische
Fehlerfaelle (I/O-Fehler, Race ums Restore-Ziel, Abbruch) werden am
Dateisystem/Transport simuliert -- kein Mock ersetzt die zu beweisende
Funktion selbst.

Pure Python, nur `assert`, echter Exitcode (gleiches Muster + Runner
`tests/mmo_sim/run_all.py` wie die R1-Testdatei)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _population_backup_fixtures as pf  # noqa: E402

from mmo_sim.core import population_backup as pb  # noqa: E402
from mmo_sim.core import store  # noqa: E402

_AT = "2026-11-01T00:00:00+00:00"


def _leader_ref_seq(fx) -> int:
    state = json.loads((fx.roots.states_dir / f"{pf.LEADER_PK}.json").read_text(encoding="utf-8"))
    return int(state[pb._CURRENT_SAVE_REF_FIELD]["seq"])


def _make_generation(backup_root: Path, gid: str, entries: list[tuple[str, str, bytes]],
                     *, extra_manifest_files: list[dict] | None = None) -> Path:
    """Baut eine synthetische Generation (gen_dir + manifest.json) fuer die
    gezielten Restore-Validierungs-Negativfaelle. `entries` = (role, rel_path,
    content). `extra_manifest_files` erlaubt Manifestzeilen OHNE passende
    Datei (z.B. fehlende benoetigte Referenz)."""
    gen_dir = backup_root / "generations" / gid
    files_meta: list[dict] = []
    for role, rel_path, content in entries:
        p = gen_dir / role / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        files_meta.append({
            "role": role, "rel_path": rel_path, "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    if extra_manifest_files:
        files_meta.extend(extra_manifest_files)
    manifest = {
        "schema_version": pb.SCHEMA_VERSION, "generation_id": gid,
        "run_id": "r", "table_id": "t", "section_id": "s",
        "created_at_utc": _AT, "producer_code_anchor": "test", "product_commit": "x",
        "prev_generation_id": None, "roots": sorted(pb.ROLES), "excluded": [],
        "files": files_meta,
    }
    (gen_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return gen_dir


# ── F1: konsistente Abschluss-/Snapshotgrenze ──────────────────────────────


def test_f1_paused_multifile_write_is_not_published_as_good_generation():
    """F1/C1: ein pausierter mehrteiliger Produktwrite (Versionsdatei seq+1
    geschrieben, persona-state-Ref noch nicht nachgezogen) ist hashstabil, aber
    fachlich gemischt. Die Aufnahme darf ihn NICHT als gute Generation
    veroeffentlichen -- stattdessen kontrolliert fehlgeschlagen. G0 bleibt
    letzte gute Generation, der unbeteiligte offene Tisch bleibt offen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        g0 = pf.run_backup(fx)
        assert g0.status == "created"

        # Pausierter publish_current_save: neue Versionsdatei seq+1 vorhanden,
        # Ref steht noch auf seq -> torn/paused (Schritt 2 erledigt, Schritt 3 nicht).
        seq = _leader_ref_seq(fx)
        versions = fx.roots.run_dir / "current_saves" / f"{pf.LEADER_PK}__versions"
        (versions / f"{seq + 1:04d}.json").write_text(
            json.dumps({"v": 2, "persona_key": pf.LEADER_PK, "rounds_played": 1, "paused": True}),
            encoding="utf-8",
        )

        problems = pb.verify_population_consistency(fx.roots)
        assert problems, "pausierter Mehrdateiwrite muss als inkonsistent erkannt werden"
        assert any("pausierter" in p or "seq" in p for p in problems)

        # Frischer Aufnahmeversuch (anderer Abschnitt) -> kontrolliert
        # fehlgeschlagen, kein veroeffentlichter Mischstand.
        key2 = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=f"{fx.table_id}-section-2")
        out = pb.generate_population_backup(
            fx.roots, key2, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
        )
        assert out.status == "failed_inconsistent", out.status
        assert out.manifest is None
        assert not (br / "generations" / key2.generation_id()).exists()

        # G0 bleibt die letzte gute Generation.
        latest = pb.read_latest(br)
        assert latest and latest["generation_id"] == g0.generation_id

        # Unbeteiligter offener Tisch bleibt fachlich offen.
        open_tbl = store.Table.load(fx.roots.run_dir, fx.open_table_id)
        assert open_tbl.status != "closed"


# ── F2: durabler Auftrag, ehrlicher Retry, G0-Erhalt ──────────────────────


def test_f2_reconstruct_missing_backup_task_after_crash_before_first_write():
    """F2/C2 (zweite Luecke): Abbruch NACH Primaerfinalisierung, aber VOR dem
    ersten Backup-Taskwrite -> es existiert kein Taskdatensatz. Der frische
    Prozess findet die fehlende Zusatzsicherung aus den echten Abschlussrecords
    wieder und kann sie per Retry nachholen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)

        # Abbruch vor dem ersten Taskwrite: KEIN backup_tasks-Eintrag vorhanden.
        assert not (br / "backup_tasks").exists()
        finals = list((fx.roots.run_dir / "completion").glob("*__final.json"))
        assert finals, "Abschlussrecord muss durch play_section_to_success existieren"

        rec = pb.reconstruct_missing_backup_tasks(fx.roots, br)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        assert key.generation_id() in rec

        status = pb.read_backup_status(br, fx.roots)
        assert any(t["generation_id"] == key.generation_id() for t in status["open_tasks"])

        out = pb.retry_population_backup(
            fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
        )
        assert out.status == "created", out.status
        # Keine Doppel-Rekonstruktion: erneuter Lauf findet nichts Neues.
        assert pb.reconstruct_missing_backup_tasks(fx.roots, br) == []


def test_f2_retry_captures_later_state_and_labels_it_honestly():
    """F2/C2: Sicherung A scheitert; danach echte wirksame Produktaenderung B;
    Retry A nimmt nun den SPAETEREN Stand auf. Das Manifest kennzeichnet
    maschinenlesbar, dass der aufgenommene Stand NICHT dem Abschlusszeitpunkt
    entspricht (kein stilles Umetikettieren von B als A)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)

        orig_copy = pb._copy_files_to_staging

        def boom(*a, **k):
            raise OSError("ENOSPC simuliert (Aufnahme A)")

        pb._copy_files_to_staging = boom
        try:
            out_a = pb.generate_population_backup(
                fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
            )
        finally:
            pb._copy_files_to_staging = orig_copy
        assert out_a.status == "failed"
        task_a = json.loads((br / "backup_tasks" / f"{key.generation_id()}.json").read_text(encoding="utf-8"))
        comp_fp = task_a.get("completion_fingerprint")
        assert comp_fp, "completion_fingerprint muss beim ersten Task gebunden sein"

        # Echte wirksame spaetere Produktaenderung B (regulaerer Schreibweg).
        current = store.load_current_save_or_raise(
            fx.roots.run_dir, pf.LEADER_PK, fx.ps_store, states_dir=fx.roots.states_dir,
        )
        current["characters"][0]["xp"] = 123
        store.publish_current_save(
            fx.roots.run_dir, pf.LEADER_PK, current, fx.ps_store, fx.roots.states_dir,
        )

        out_b = pb.retry_population_backup(
            fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
            created_at_utc="2026-11-01T01:00:00+00:00",
        )
        assert out_b.status == "created", out_b.status
        cap = out_b.manifest["capture"]
        assert cap["completion_fingerprint_sha256"] == comp_fp
        assert cap["capture_fingerprint_sha256"] != comp_fp
        assert cap["captured_state_matches_section_completion"] is False
        assert "note" in cap and "SPAETER" in cap["note"]


# ── F3: getrennte Backup-I/O-Fehler ───────────────────────────────────────


def test_f3_backup_io_errors_at_each_phase_are_separate_from_primary_success():
    """F3/C3: ein nativer I/O-Fehler an JEDER Persistenzphase (Task-Init,
    Kopie, Publish, Latest) darf den erfolgreichen Primaerabschluss NICHT
    umdeuten: der Hook liefert ein getrenntes `succeeded=False`, wirft NIE,
    und der Fehlerpfad haengt nicht davon ab, auf dem defekten Ziel noch
    schreiben zu koennen. Nach Beheben funktioniert der Retry ohne Doppeleffekt."""
    phases = ["_write_task", "_copy_files_to_staging", "_publish_generation", "_update_latest_pointer"]
    for phase in phases:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "data"
            fx = pf.build_fixture(root)
            assert pf.play_section_to_success(fx).completion.success
            br = pf.backup_root_for(fx)

            orig = getattr(pb, phase)

            def boom(*a, **k):
                raise OSError(f"simulierter I/O-Fehler in {phase}")

            setattr(pb, phase, boom)
            try:
                result = pb.backup_after_section_completed(
                    completion_success=True, run_id=fx.run_id, table_id=fx.table_id,
                    section_id=fx.section_id, roots=fx.roots, backup_root=br,
                    producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
                )
            finally:
                setattr(pb, phase, orig)

            assert result is not None, phase
            assert result.attempted is True, phase
            assert result.succeeded is False, f"{phase}: Backupfehler wurde nicht getrennt gemeldet"
            assert result.error, phase

            # Primaerdaten unberuehrt: Abschlussmarker + current-Save bestehen.
            assert (fx.roots.run_dir / "completion").glob("*__final.json")
            assert (fx.roots.run_dir / "current_saves" / f"{pf.LEADER_PK}.json").is_file()

            # Nach Beheben: Retry gelingt ohne neue Spiel-/Modelleffekte (die
            # Signatur von retry_population_backup kennt keine Spielzustaende).
            retry = pb.retry_population_backup(
                fx.roots, pb.GenerationKey(fx.run_id, fx.table_id, fx.section_id), br,
                producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
            )
            assert retry.status in ("created", "resumed_publish", "already_done"), (phase, retry.status)


# ── F4: Restore besitzt sein Ziel, privat, atomar ─────────────────────────


def test_f4_restore_does_not_delete_foreign_target_created_in_race():
    """F4/C4: wird zwischen Vorpruefung und Aktivierung ein FREMDES Ziel mit
    Sentinel angelegt, lehnt der Restore kontrolliert ab und laesst Ziel +
    Sentinel bytegleich erhalten (kein `rmtree` eines fremden Bestands)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"
        target = Path(td) / "restored"
        sentinel = "FREMDER-BESTAND-NICHT-LOESCHEN"

        orig_mkdtemp = pb.tempfile.mkdtemp

        def racing_mkdtemp(*a, **k):
            d = orig_mkdtemp(*a, **k)
            # Simuliert einen zweiten regulaeren Vorgang, der GENAU jetzt (nach
            # der Vorpruefung, vor der Aktivierung) das Ziel mit Daten anlegt.
            target.mkdir(parents=True, exist_ok=True)
            (target / "fremd.txt").write_text(sentinel, encoding="utf-8")
            return d

        pb.tempfile.mkdtemp = racing_mkdtemp
        try:
            rejected = False
            try:
                pb.restore_population(br, target)
            except pb.RestoreRejectedError:
                rejected = True
            assert rejected, "Restore auf ein zwischenzeitlich belegtes Ziel muss ablehnen"
        finally:
            pb.tempfile.mkdtemp = orig_mkdtemp

        assert (target / "fremd.txt").read_text(encoding="utf-8") == sentinel
        assert list(target.iterdir()) == [target / "fremd.txt"], "kein Fremdinhalt entfernt/ergaenzt"


def test_f4_restore_target_is_private_under_permissive_umask():
    """F4/C4: das Restore-Ziel wird ausdruecklich privat (0o700) angelegt,
    unabhaengig von einer permissiven geerbten Umask."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"
        target = Path(td) / "restored"
        old_umask = os.umask(0)
        try:
            pb.restore_population(br, target)
            mode = stat.S_IMODE(os.lstat(target).st_mode)
            assert mode == 0o700, f"Zielmodus {oct(mode)} ist nicht privat (0o700)"
        finally:
            os.umask(old_umask)


def test_f4_restore_abort_during_copy_leaves_no_activatable_target():
    """F4/C4: ein Abbruch waehrend der Restore-Kopie hinterlaesst KEINEN
    aktivierbaren Zielroot (das Ziel entsteht erst mit der atomaren
    Aktivierung, nicht waehrend des Kopierens; nur eigenes Staging faellt an)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"
        target = Path(td) / "restored"

        orig_copy = pb.shutil.copyfileobj

        def boom(*a, **k):
            raise OSError("Abbruch waehrend Restore-Kopie")

        pb.shutil.copyfileobj = boom
        try:
            aborted = False
            try:
                pb.restore_population(br, target)
            except OSError:
                aborted = True
            assert aborted
        finally:
            pb.shutil.copyfileobj = orig_copy

        assert not target.exists(), "kein teilaktivierbares Ziel nach Abbruch waehrend der Kopie"
        # Kein verwaistes Staging neben dem Ziel.
        leftovers = [p for p in target.parent.glob(".restore-*")]
        assert leftovers == [], f"eigenes Staging nicht bereinigt: {leftovers}"


# ── F5 (C5): vollstaendige Restore-Validierung ─────────────────────────────


def test_c5_validation_rejects_missing_reference_collision_symlink_and_extra():
    """C5: die Validierung lehnt eine fehlende benoetigte Referenz, einen
    rollenuebergreifend kollidierenden Zielpfad, einen Symlink in der Generation
    sowie eine im Manifest nicht verzeichnete Zusatzdatei kontrolliert ab -- je
    bevor irgendein Ziel entsteht."""
    with tempfile.TemporaryDirectory() as td:
        br = Path(td) / "bk"

        # (1) fehlende benoetigte Referenz: persona-state verweist auf
        # current_save_version seq 7, aber die Versionsdatei ist nicht gesichert.
        state_bytes = json.dumps(
            {"v": 2, "persona_key": "pk", "rounds_played": 1, "current_save_version": {"run_id": "r", "seq": 7}}
        ).encode("utf-8")
        _make_generation(br, "gen-missingref", [("states", "pk.json", state_bytes)])
        _assert_reject(br, "gen-missingref", "benoetigte Referenz")

        # (2) kollidierender Zielpfad: role run `x.json` und role prefs
        # `run/x.json` zeigen auf dieselbe Zieldatei (prefs hat keinen Subdir).
        _make_generation(br, "gen-collide", [
            ("run", "x.json", b"{}"),
            ("prefs", "run/x.json", b"{}"),
        ])
        _assert_reject(br, "gen-collide", "kollidierender Restore-Zielpfad")

        # (3) Symlink in der Generation (wo eine regulaere Datei erwartet wird).
        gen = _make_generation(br, "gen-symlink", [("states", "good.json", b"{}")])
        victim = gen / "states" / "good.json"
        victim.unlink()
        victim.symlink_to(Path(td) / "outside_target.txt")
        _assert_reject(br, "gen-symlink", "Symlink")

        # (4) im Manifest nicht verzeichnete Zusatzdatei (unvollstaendiges/
        # inkonsistentes Manifest).
        gen_extra = _make_generation(br, "gen-extra", [("states", "a.json", b"{}")])
        (gen_extra / "states" / "surprise.json").write_text("{}", encoding="utf-8")
        _assert_reject(br, "gen-extra", "nicht verzeichnet")


def _assert_reject(backup_root: Path, gid: str, needle: str) -> None:
    rejected = False
    try:
        pb.validate_generation_for_restore(backup_root, gid)
    except pb.RestoreRejectedError as exc:
        rejected = True
        assert needle in str(exc), f"{gid}: erwarteter Grund {needle!r} fehlt in: {exc}"
    assert rejected, f"{gid}: haette abgelehnt werden muessen ({needle})"


def test_c5_valid_generation_still_restores_after_negative_cases():
    """C5: eine unveraenderte gute Generation wird weiterhin erfolgreich
    restauriert (die neuen Pruefungen blockieren nur ungueltige Faelle)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        result = pf.run_backup(fx)
        assert result.status == "created"
        target = Path(td) / "restored"
        out = pb.restore_population(br, target)
        assert out.target_root == target
        assert (target / "states" / f"{pf.LEADER_PK}.json").is_file()
        assert (target / "run" / "current_saves" / f"{pf.LEADER_PK}.json").is_file()


# ── F6: Auth-Ausschluss + getrennt konfigurierte Roots ─────────────────────


def test_f6_auth_files_excluded_in_recursive_roles_neighbor_kept():
    """F6/C6: ein klar erkennbarer Fake-Secret-Sentinel INNERHALB rekursiver
    Rollen (states/auth.json, states/provider_token.json, run/.env) wird weder
    gesichert noch restauriert; ein notwendiger nichtgeheimer Nachbar bleibt
    erhalten. Der Ausschluss ist eine wirksame Grenze und auditierbar."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)

        (fx.roots.states_dir / "auth.json").write_text(
            json.dumps({"token": pf.FAKE_TOKEN_SENTINEL}), encoding="utf-8")
        (fx.roots.states_dir / "provider_token.json").write_text(pf.FAKE_TOKEN_SENTINEL, encoding="utf-8")
        (fx.roots.run_dir / ".env").write_text("SECRET=" + pf.FAKE_TOKEN_SENTINEL, encoding="utf-8")
        neighbor = fx.roots.registry_dir / "needed_neighbor.json"
        neighbor.write_text(json.dumps({"keep": "nichtgeheim"}), encoding="utf-8")

        files = pb.collect_population_files(fx.roots)
        keys = {(f.role, f.rel_path) for f in files}
        assert ("states", "auth.json") not in keys
        assert ("states", "provider_token.json") not in keys
        assert ("run", ".env") not in keys
        assert ("registry", "needed_neighbor.json") in keys, "nichtgeheimer Nachbar fehlt im Scan"

        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        mk = {(f["role"], f["rel_path"]) for f in result.manifest["files"]}
        assert ("states", "auth.json") not in mk
        assert ("states", "provider_token.json") not in mk
        assert ("run", ".env") not in mk
        assert ("registry", "needed_neighbor.json") in mk
        excluded_text = " ".join(result.manifest["excluded"])
        assert "auth.json" in excluded_text and "Auth" in excluded_text

        # Sentinel-Bytes tauchen nirgends in der Generation auf.
        br = pf.backup_root_for(fx)
        gen_dir = br / "generations" / result.generation_id
        for p in gen_dir.rglob("*"):
            if p.is_file():
                assert pf.FAKE_TOKEN_SENTINEL not in p.read_text(encoding="utf-8", errors="ignore"), (
                    f"Sentinel in Generation gelandet: {p}"
                )

        # Restore -> Sentinel fehlt, Nachbar vorhanden.
        target = Path(td) / "restored"
        pb.restore_population(br, target)
        assert not (target / "states" / "auth.json").exists()
        assert not (target / "run" / ".env").exists()
        assert (target / "registry" / "needed_neighbor.json").is_file()


def test_f6_separate_root_config_backup_and_restore_with_split_parents():
    """F6: mindestens eine vom Default-Elternordner GETRENNTE Rootkonfiguration
    (sechs Rollen unter verschiedenen Eltern) mit denselben Produktresolvern --
    Backup und Restore funktionieren, das Backup-Ziel liegt getrennt, der
    Restore vereinheitlicht die Rollen in einem neuen privaten Root."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        roots = pb.PopulationRoots(
            onboarding_dir=base / "pa" / "onboarding",
            catalog_dir=base / "pb" / "catalog",
            run_dir=base / "pc" / "run",
            states_dir=base / "pd" / "states",
            registry_dir=base / "pe" / "registry",
            prefs_root=base / "pfroot",
        )
        for d in roots.as_dict().values():
            d.mkdir(parents=True, exist_ok=True)
        (roots.run_dir / "run_id.json").write_text(json.dumps({"run_id": "run-split"}), encoding="utf-8")
        (roots.onboarding_dir / "journal.json").write_text(json.dumps({"done": True}), encoding="utf-8")
        (roots.catalog_dir / "entry.json").write_text(json.dumps({"c": 1}), encoding="utf-8")
        # persona-state OHNE current_save_version (keine Referenzpflicht).
        (roots.states_dir / "somebody.json").write_text(
            json.dumps({"v": 2, "persona_key": "somebody", "rounds_played": 0}), encoding="utf-8")
        (roots.registry_dir / "reg.json").write_text(json.dumps({"r": 1}), encoding="utf-8")
        (roots.prefs_root / "ui_prefs_somebody.json").write_text(json.dumps({"ui": 1}), encoding="utf-8")

        backup_root = base / "separate_backups"
        key = pb.GenerationKey(run_id="run-split", table_id="t-split", section_id="s-split")
        out = pb.generate_population_backup(
            roots, key, backup_root, producer_code_anchor="test:split", created_at_utc=_AT,
        )
        assert out.status == "created", out.status
        mk = {(f["role"], f["rel_path"]) for f in out.manifest["files"]}
        assert ("onboarding", "journal.json") in mk
        assert ("catalog", "entry.json") in mk
        assert ("registry", "reg.json") in mk
        assert ("prefs", "ui_prefs_somebody.json") in mk

        target = base / "restored_split"
        ro = pb.restore_population(backup_root, target)
        assert ro.generation_id == key.generation_id()
        assert (target / "onboarding" / "journal.json").is_file()
        assert (target / "catalog" / "entry.json").is_file()
        assert (target / "registry" / "reg.json").is_file()
        assert (target / "ui_prefs_somebody.json").is_file()  # prefs ohne Subdir


# ── Ergaenzende Nachweise aus der Critic-Runde (Vera/Specht) ───────────────


def test_f1_consistency_detects_dangling_ref_and_direct_version_mismatch():
    """F1/C1 (Invarianten a + c): die Konsistenzpruefung erkennt sowohl eine
    dangling current_save_version-Ref (Versionsdatei fehlt) als auch eine von
    der referenzierten Version abweichende direkte current-Datei -- nicht nur
    den Fall einer hoeheren Versionsnummer (b)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        assert pf.run_backup(fx).status == "created"
        assert pb.verify_population_consistency(fx.roots) == []

        cs = fx.roots.run_dir / "current_saves"
        seq = _leader_ref_seq(fx)
        vpath = cs / f"{pf.LEADER_PK}__versions" / f"{seq:04d}.json"

        # (a) dangling ref: referenzierte Versionsdatei entfernen.
        vbytes = vpath.read_bytes()
        vpath.unlink()
        probs_a = pb.verify_population_consistency(fx.roots)
        assert any("Versionsdatei fehlt" in p or "dangling" in p for p in probs_a), probs_a
        vpath.write_bytes(vbytes)
        assert pb.verify_population_consistency(fx.roots) == []

        # (c) direct-vs-version: direkte current-Datei abweichend ueberschreiben.
        direct = cs / f"{pf.LEADER_PK}.json"
        direct.write_text(
            json.dumps({"v": 2, "persona_key": pf.LEADER_PK, "rounds_played": 99, "tamper": True}),
            encoding="utf-8",
        )
        probs_c = pb.verify_population_consistency(fx.roots)
        assert any("weicht von referenzierter Version" in p for p in probs_c), probs_c


def test_f2_completion_fingerprint_survives_io_failure_at_task_or_publish():
    """F2/C2 (Critic-Blocker): auch wenn der erste `_write_task` ODER
    `_publish_generation` mit einem transienten I/O-Fehler scheitert, bleibt der
    `completion_fingerprint` gebunden. Eine spaetere echte Produktaenderung B +
    Retry weist dadurch ehrlich `captured_state_matches_section_completion=False`
    aus -- der spaetere Stand wird nicht faelschlich als Abschlussstand A
    veroeffentlicht."""
    for phase in ("_write_task", "_publish_generation"):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "data"
            fx = pf.build_fixture(root)
            assert pf.play_section_to_success(fx).completion.success
            br = pf.backup_root_for(fx)
            key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)

            orig = getattr(pb, phase)
            calls = {"n": 0}

            def boom(*a, **k):
                calls["n"] += 1
                if calls["n"] == 1:
                    raise OSError(f"transienter I/O-Fehler in {phase} (Versuch A)")
                return orig(*a, **k)

            setattr(pb, phase, boom)
            try:
                out_a = pb.generate_population_backup(
                    fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc=_AT,
                )
            finally:
                setattr(pb, phase, orig)
            assert out_a.status in ("failed", "failed_drift"), (phase, out_a.status)
            task_a = json.loads((br / "backup_tasks" / f"{key.generation_id()}.json").read_text(encoding="utf-8"))
            comp = task_a.get("completion_fingerprint")
            assert comp, f"{phase}: completion_fingerprint ging beim I/O-Fehler verloren"

            current = store.load_current_save_or_raise(
                fx.roots.run_dir, pf.LEADER_PK, fx.ps_store, states_dir=fx.roots.states_dir,
            )
            current["characters"][0]["xp"] = 321
            store.publish_current_save(
                fx.roots.run_dir, pf.LEADER_PK, current, fx.ps_store, fx.roots.states_dir,
            )

            out_b = pb.retry_population_backup(
                fx.roots, key, br, producer_code_anchor=pf.PRODUCER_ANCHOR,
                created_at_utc="2026-11-01T02:00:00+00:00",
            )
            assert out_b.status == "created", (phase, out_b.status)
            cap = out_b.manifest["capture"]
            assert cap["completion_fingerprint_sha256"] == comp, phase
            assert cap["captured_state_matches_section_completion"] is False, (
                f"{phase}: spaeterer Stand faelschlich als Abschlussstand ausgewiesen"
            )


def test_f5_real_play_continuation_after_restore_with_source_removed():
    """F5 (02_NACHZUG.md:39-47): echter spielwirksamer Fortsetzungsnachweis.
    Fertige Sicherung in neuen privaten Root restaurieren; QUELLE ENTZIEHEN
    (rmtree, nachweisbar unerreichbar); frischer Produktprozess spielt mit dem
    REGULAEREN Produktschema (nicht dem Schema des entfernten alten Roots) eine
    normale Folgeaktion ueber die regulaere Spiel-/Abschlusslogik
    (`SectionRuntime.run_full_section`, KEIN Low-Level xp=999); ein weiterer
    frischer Prozess laedt erneut und sieht die echte Aenderung samt
    unveraenderter unbeteiligter Persona und inaktiver Figur."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        br = pf.backup_root_for(fx)
        assert pf.run_backup(fx).status == "created"

        target = Path(td) / "restored"
        pb.restore_population(br, target)

        # Quelle entziehen -- nachweisbar unerreichbar (nicht nur "nicht referenziert").
        shutil.rmtree(root)
        assert not root.exists()

        schema = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
        assert schema.is_file(), "regulaeres Produktschema muss unabhaengig vom alten Root verfuegbar sein"
        helper = _HERE / "_f5_restored_followup.py"

        # Frischer Prozess #1: reale Folgeaktion ueber regulaere Spiel-/Abschlusslogik.
        p1 = subprocess.run(
            [sys.executable, str(helper), str(target), str(schema)], capture_output=True, text=True,
        )
        assert p1.returncode == 0, p1.stderr
        res = json.loads(p1.stdout)
        assert res["completion_success"] and res["final_marker_present"]
        assert res["leader_rounds_played"] == 2

        # Frischer Prozess #2: Reload mit Produktschema -- echte Aenderung sichtbar,
        # unbeteiligte Persona + inaktive Figur unveraendert.
        reload_script = f"""
import sys, json
sys.path.insert(0, {str(_REPO_ROOT)!r})
from pathlib import Path
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss import catalog
target = Path({str(target)!r})
ps = PersonaStateStore(schema_path=Path({str(schema)!r}), default_states_dir=None)
leader = ps.load_state({pf.LEADER_PK!r}, states_dir=target / "states")
bystander = ps.load_state({pf.BYSTANDER_PK!r}, states_dir=target / "states")
inactive = catalog.load_figure_save(target / "catalog", {pf.LEADER_PK!r}, {pf.INACTIVE_CHRONONAUT_ID!r})
print(json.dumps({{
    "leader_rounds": leader.get("rounds_played"),
    "has_followup": "t-restored-followup-section" in json.dumps(leader.get("round_history")),
    "bystander_learnings": bystander.get("learnings"),
    "inactive_present": inactive is not None,
}}))
"""
        p2 = subprocess.run([sys.executable, "-c", reload_script], capture_output=True, text=True)
        assert p2.returncode == 0, p2.stderr
        payload = json.loads(p2.stdout)
        assert payload["leader_rounds"] == 2, "Folgeaktion im dritten frischen Prozess nicht sichtbar"
        assert payload["has_followup"], "Folgeabschnitt fehlt in der round_history"
        assert payload["bystander_learnings"] == [
            "Bystander-Erkenntnis: hat diesen Abschnitt nicht gesehen."
        ]
        assert payload["inactive_present"] is True


def test_f6_api_key_and_bare_credentials_excluded():
    """F6/C6 (Security-Critic): die gaengigen Credential-Namen `api_key*`,
    `apikey*` und die blanke extensionslose `credentials`-Datei (AWS/gcloud-
    Default) werden in rekursiven Rollen ebenfalls zuverlaessig ausgeschlossen;
    ein nichtgeheimer Nachbar bleibt erhalten."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        (fx.roots.states_dir / "api_key.json").write_text(
            json.dumps({"k": pf.FAKE_TOKEN_SENTINEL}), encoding="utf-8")
        (fx.roots.registry_dir / "credentials").write_text(pf.FAKE_TOKEN_SENTINEL, encoding="utf-8")
        (fx.roots.catalog_dir / "aws_credentials").write_text(pf.FAKE_TOKEN_SENTINEL, encoding="utf-8")
        keep = fx.roots.registry_dir / "keep_me.json"
        keep.write_text(json.dumps({"ok": 1}), encoding="utf-8")

        keys = {(f.role, f.rel_path) for f in pb.collect_population_files(fx.roots)}
        assert ("states", "api_key.json") not in keys
        assert ("registry", "credentials") not in keys
        assert ("catalog", "aws_credentials") not in keys
        assert ("registry", "keep_me.json") in keys


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
