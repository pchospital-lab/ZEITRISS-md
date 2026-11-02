#!/usr/bin/env python3
"""
tests/mmo_sim/test_population_backup_restore_2026_11_01.py — ZR-POPULATION-
BACKUP-RESTORE-20261101-R1.

Deckt alle acht Risiko-IDs aus `03_ABNAHME.md` ab: `closure_boundary`,
`whole_population`, `atomic_generation`, `retry_idempotence`,
`restore_fresh_process`, `restore_followup`, `privacy_and_exclusions`
(`ci_smoke` ist kein Pytest-Fall, s. `delivery/REPORT.md` fuer den rohen
`bash scripts/smoke.sh`-Lauf am Endstand).

Fakes NUR am GM-/Persona-Transportrand (`ScriptedGmTransport`/
`ScriptedDriver` aus `_section_completion_resume_fixtures.py`). Produkt-
persistenz, Abschlusslogik (`core.store`/`core.runtime`) und Restore-Leser
laufen ECHT -- kein Mock ersetzt die zu beweisende Speicherfunktion selbst.
Deterministische Fehlerfaelle (Drift, Crash vor/zwischen Publish+Latest,
beschaedigtes Manifest, belegtes Ziel, Pfadausbruch) werden am Transport/
Dateisystem simuliert (Monkeypatch einer privaten Kopierfunktion bzw.
direkte Orchestrierung derselben privaten Schritte, die `generate_
population_backup` selbst verwendet -- kein Ersatz des gemessenen
Verhaltens).

Pure Python, nur `assert`, echter Exitcode (gleiches Muster wie
`test_a04_shared_app_service.py`/`test_section_completion_resume_boundary.py`;
`tests/mmo_sim/run_all.py` fuehrt diese Datei als eigenen Subprozess aus)."""
from __future__ import annotations

import json
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
from _full_v7_fixture import full_v7_block_text, full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ScriptedDriver, ScriptedGmTransport, debrief_with_marker,
)

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import lobby_flow, store  # noqa: E402
from mmo_sim.core import population_backup as pb  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── closure_boundary ──────────────────────────────────────────────────────


def test_closure_boundary_hold_blocks_backup_hook():
    """Ein nicht final abgeschlossener Abschnitt (hier: `store.
    complete_section` mit unvollstaendiger Ernte -> `CompletionResult.
    success=False`, ECHTER Produktaufruf) darf den Backup-Hook NIE
    ausloesen -- 'Save-Rohkonflikt/unvollstaendige Ernte/SaveGuard-Ablehnung
    duerfen keine erfolgreiche Abschlussgeneration erzeugen' (01_AUFTRAG.md
    §2)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        # Unvollstaendige Ernte: 'guest_pk' fehlt im harvested-Dict.
        harvest_completion = store.complete_section(
            fx.lobby, fx.table, fx.section_id, {"leader_pk": full_v7_save("chrono-leader")},
            fx.roots.states_dir, "2026-11-01", ZeitrissHarvestValidator(), fx.ps_store,
        )
        assert not harvest_completion.success, "Testannahme verletzt: Ernte haette unvollstaendig sein muessen"

        hook_result = pb.backup_after_section_completed(
            completion_success=harvest_completion.success, run_id=fx.run_id, table_id=fx.table_id,
            section_id=fx.section_id, roots=fx.roots, backup_root=pf.backup_root_for(fx),
            producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc="2026-11-01T00:00:00+00:00",
        )
        assert hook_result is None, "Hook haette bei HOLD keinen Versuch unternehmen duerfen"
        assert not (pf.backup_root_for(fx) / "generations").exists(), "kein Backup-PASS fuer einen offenen Abschluss"


def test_closure_boundary_success_triggers_backup_via_hook():
    """Regulaerer erfolgreicher Abschnitt (Anker+Gast-Import+Debrief mit
    Marker+Pflichtreflexion je Mitglied, ECHTER `SectionRuntime.
    run_full_section`-Lauf) -> `outcome.completion.success is True` -> der
    Hook erzeugt GENAU EINE neue Generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        outcome = pf.play_section_to_success(fx)
        assert outcome.completion.success, outcome.completion.reason
        assert set(outcome.completion.members_completed) == {"leader_pk", "guest_pk"}

        hook_result = pb.backup_after_section_completed(
            completion_success=outcome.completion.success, run_id=fx.run_id, table_id=fx.table_id,
            section_id=fx.section_id, roots=fx.roots, backup_root=pf.backup_root_for(fx),
            producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc="2026-11-01T00:00:00+00:00",
        )
        assert hook_result is not None and hook_result.succeeded and hook_result.attempted
        assert not hook_result.already_done
        latest = pb.read_latest(pf.backup_root_for(fx))
        assert latest is not None and latest["generation_id"] == hook_result.generation_id


# ── whole_population ─────────────────────────────────────────────────────


def test_whole_population_manifest_covers_all_roles_and_open_table_untouched():
    """Vollstaendiges Inventar: unbeteiligte Persona (+Memory), inaktive
    Figur (+Katalogsave), Registry, nichtgeheime Prefs, Onboarding-Journal,
    Current-Saves+Versionen, Completion-Records -- UND der zweite, NICHT an
    diesem Abschluss beteiligte Tisch bleibt in seinem echten offenen
    Zustand (`status='active'`) im gesicherten Payload sichtbar, statt
    stillschweigend geschlossen oder ausgelassen zu werden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        outcome = pf.play_section_to_success(fx)
        assert outcome.completion.success

        result = pf.run_backup(fx)
        assert result.status == "created", result.error
        keys = {(f["role"], f["rel_path"]) for f in result.manifest["files"]}

        expected = {
            ("states", f"{pf.BYSTANDER_PK}.json"),
            ("states", f"{pf.LEADER_PK}.json"),
            ("states", f"{pf.GUEST_PK}.json"),
            ("states", f"{pf.OTHER_PK}.json"),
            ("catalog", f"figures/{pf.LEADER_PK}__{pf.INACTIVE_CHRONONAUT_ID}.json"),
            ("catalog", f"catalog__{pf.LEADER_PK}.json"),
            ("catalog", f"catalog__{pf.GUEST_PK}.json"),
            ("onboarding", f"onboarding__{pf.LEADER_PK}.json"),
            ("prefs", f"ui_prefs__{pf.LEADER_PK}.json"),
            ("prefs", "last_participant.json"),
            ("run", f"tables/{fx.table_id}.json"),
            ("run", f"tables/{fx.open_table_id}.json"),
            ("run", f"completion/{fx.section_id}__final.json"),
            ("run", "current_saves/leader_pk.json"),
            ("run", "current_saves/guest_pk.json"),
            ("run", "current_saves/leader_pk__versions/0001.json"),
            ("run", "current_saves/guest_pk__versions/0001.json"),
            ("run", "run_id.json"),
            ("run", "locks.json"),
        }
        missing = expected - keys
        assert not missing, f"whole_population: fehlende Dateien im Manifest: {sorted(missing)}"

        # Bystander-Memory tatsaechlich im Payload vorhanden (nicht nur der
        # Dateiname) -- vergleicht das kopierte Staging-Byte gegen die Quelle.
        gen_dir = pf.backup_root_for(fx) / "generations" / result.generation_id
        bystander_payload = json.loads((gen_dir / "states" / f"{pf.BYSTANDER_PK}.json").read_text())
        assert bystander_payload["learnings"] == [
            "Bystander-Erkenntnis: hat diesen Abschnitt nicht gesehen.",
        ]
        inactive_payload = json.loads(
            (gen_dir / "catalog" / "figures" / f"{pf.LEADER_PK}__{pf.INACTIVE_CHRONONAUT_ID}.json").read_text()
        )
        assert inactive_payload["characters"][0]["id"] == pf.INACTIVE_CHRONONAUT_ID

        # Der zweite, offene Tisch ist WIRKLICH offen (kein stilles Schliessen).
        open_table_payload = json.loads((gen_dir / "run" / "tables" / f"{fx.open_table_id}.json").read_text())
        assert open_table_payload["status"] == "active"
        live_open_table_payload = json.loads(
            (fx.roots.run_dir / "tables" / f"{fx.open_table_id}.json").read_text()
        )
        assert live_open_table_payload["status"] == "active", "Fixture-Annahme verletzt"


# ── atomic_generation ────────────────────────────────────────────────────


def test_atomic_generation_publish_is_coherent():
    """Normalfall: Staging -> Verifikation -> atomarer Rename ->
    `latest.json` zeigt NUR auf eine vollstaendig validierte Generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        gen_dir = pf.backup_root_for(fx) / "generations" / result.generation_id
        assert (gen_dir / "manifest.json").is_file()
        staging_root = pf.backup_root_for(fx) / "staging"
        assert not staging_root.exists() or not list(staging_root.iterdir()), "kein Staging-Rest nach Erfolg"
        # Selbstpruefung: validate_generation_for_restore akzeptiert exakt
        # das, was generate_population_backup veroeffentlicht hat.
        validated = pb.validate_generation_for_restore(pf.backup_root_for(fx))
        assert validated["generation_id"] == result.generation_id


def test_atomic_generation_drift_detected_and_recoverable():
    """Ein Schreibzugriff auf eine Quelldatei WAEHREND der Aufnahme (hier
    via Monkeypatch der Kopierfunktion am Transport/Dateisystem simuliert,
    `core.store`/`core.persona_state` bleiben unveraendert) fuehrt zu einem
    KONTROLLIERT fehlgeschlagenen Backup -- NIE zu einer veroeffentlichten
    Mischgeneration. Ein spaeterer Retry ohne Drift sichert danach normal."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success

        orig_copy = pb._copy_files_to_staging
        victim = fx.roots.states_dir / f"{pf.BYSTANDER_PK}.json"

        def drifting_copy(staging_dir, roots, files):
            orig_copy(staging_dir, roots, files)
            victim.write_text(victim.read_text(encoding="utf-8") + " ", encoding="utf-8")

        pb._copy_files_to_staging = drifting_copy
        try:
            result = pf.run_backup(fx)
        finally:
            pb._copy_files_to_staging = orig_copy
            victim.write_text(victim.read_text(encoding="utf-8").rstrip(), encoding="utf-8")

        assert result.status == "failed_drift", result
        assert pb.read_latest(pf.backup_root_for(fx)) is None, "kein Mischstand als 'latest' veroeffentlicht"
        gens_dir = pf.backup_root_for(fx) / "generations"
        assert not gens_dir.exists() or not list(gens_dir.iterdir())

        result2 = pf.run_backup(fx)
        assert result2.status == "created", result2.error


def test_atomic_generation_crash_before_publish_is_recoverable():
    """Schreibfehler WAEHREND des Staging-Kopierens (Platte voll/
    Berechtigung, am Transport simuliert) -- kein Teilstaging bleibt liegen,
    `latest.json` unveraendert, ein Retry ohne den Fehler sichert
    vollstaendig."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success

        orig_copy = pb._copy_files_to_staging

        def flaky_copy(staging_dir, roots, files):
            raise OSError("ENOSPC Testfixture: Platte voll (simuliert)")

        pb._copy_files_to_staging = flaky_copy
        try:
            result = pf.run_backup(fx)
        finally:
            pb._copy_files_to_staging = orig_copy
        assert result.status == "failed"
        staging_root = pf.backup_root_for(fx) / "staging"
        assert not staging_root.exists() or not list(staging_root.iterdir()), "Staging-Leiche nach Crash"
        assert pb.read_latest(pf.backup_root_for(fx)) is None

        result2 = pf.run_backup(fx)
        assert result2.status == "created", result2.error


def test_atomic_generation_crash_between_publish_and_latest_is_recoverable():
    """Haertester Fall (01_AUFTRAG.md §3: 'Abbruch... zwischen Generations-
    Publish und Latest-Zeiger'): die Generation ist bereits vollstaendig+
    hashkorrekt unter `generations/<id>` veroeffentlicht, ABER `latest.json`
    und der Taskdatensatz wurden noch nicht aktualisiert (echter Hard-Crash
    hinterlaesst GENAU diesen Dateizustand, kein Python-Exception-Pfad --
    deshalb hier direkt ueber dieselben privaten Schritte orchestriert, die
    `generate_population_backup` selbst verwendet, statt eine Exception zu
    simulieren). Der naechste normale Aufruf zieht NUR den fehlenden Rest
    nach -- kein zweites Kopieren, keine zweite Generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success

        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        gid = key.generation_id()
        backup_root = pf.backup_root_for(fx)
        pb._write_task(backup_root, gid, {
            "generation_key": key.as_string(), "generation_id": gid, "status": "pending",
        })
        files = pb.collect_population_files(fx.roots)
        manifest = pb.build_manifest(
            generation_key=key, files=files, roots=fx.roots, created_at_utc="2026-11-01T00:00:00+00:00",
            producer_code_anchor=pf.PRODUCER_ANCHOR, product_commit=None, prev_generation_id=None,
            excluded_notes=[],
        )
        staging_dir = pb._staging_dir(backup_root, gid)
        staging_dir.mkdir(parents=True)
        pb._copy_files_to_staging(staging_dir, fx.roots, files)
        (staging_dir / "manifest.json").write_bytes(json.dumps(manifest).encode("utf-8"))
        assert not pb._verify_staging(staging_dir, manifest)
        pb._publish_generation(backup_root, staging_dir, gid, manifest)

        assert pb.read_latest(backup_root) is None, "Testannahme: Crash-Fenster VOR Latest-Update"

        result = pf.run_backup(fx)
        assert result.status == "resumed_publish", result
        assert pb.read_latest(backup_root)["generation_id"] == gid
        gens = list((backup_root / "generations").iterdir())
        assert len(gens) == 1, "kein zweites Kopieren/keine zweite Generation nach Resume"


# ── retry_idempotence ─────────────────────────────────────────────────────


def test_retry_idempotence_repeated_calls_do_not_duplicate_or_touch_primary_data():
    """Wiederholter Abschluss/Backup-Auftrag (gleiche run_id/table_id/
    section_id) sichert NUR EINMAL -- unabhaengig davon, ob ueber
    `generate_population_backup` erneut oder ueber den getrennten
    `retry_population_backup`-Einstieg aufgerufen. Primaerdaten (Current-
    Save, rounds_played, Memory) bleiben dabei BYTEGLEICH -- der Retry-Pfad
    kennt kein GM/keine Persona, kann sie also auch nicht veraendern."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success

        before_current = _sha256(fx.roots.run_dir / "current_saves" / "leader_pk.json")
        before_bystander = _sha256(fx.roots.states_dir / f"{pf.BYSTANDER_PK}.json")

        result1 = pf.run_backup(fx)
        assert result1.status == "created"
        result2 = pf.run_backup(fx)
        assert result2.status == "already_done"
        assert result2.generation_id == result1.generation_id

        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        result3 = pb.retry_population_backup(
            fx.roots, key, pf.backup_root_for(fx), producer_code_anchor=pf.PRODUCER_ANCHOR,
            created_at_utc="2026-11-01T00:05:00+00:00",
        )
        assert result3.status == "already_done"

        gens = list((pf.backup_root_for(fx) / "generations").iterdir())
        assert len(gens) == 1, f"retry/Doppelaufruf hat eine zweite Generation erzeugt: {gens}"

        assert _sha256(fx.roots.run_dir / "current_saves" / "leader_pk.json") == before_current
        assert _sha256(fx.roots.states_dir / f"{pf.BYSTANDER_PK}.json") == before_bystander


def test_retry_idempotence_backup_failure_is_separate_from_primary_success():
    """01_AUFTRAG.md §4: Primaerabschluss-Erfolg und Backup-Fehler bleiben
    getrennte Ergebnisse. Ein fehlschlagender Backup-Versuch (hier: Drift)
    darf `completion.success` NICHT nachtraeglich veraendern -- der Hook
    liefert `succeeded=False`, waehrend der (hier konstante, echte)
    Primaerabschluss unberuehrt bleibt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        outcome = pf.play_section_to_success(fx)
        assert outcome.completion.success

        orig_copy = pb._copy_files_to_staging
        victim = fx.roots.states_dir / f"{pf.BYSTANDER_PK}.json"

        def drifting_copy(staging_dir, roots, files):
            orig_copy(staging_dir, roots, files)
            victim.write_text(victim.read_text(encoding="utf-8") + " ", encoding="utf-8")

        pb._copy_files_to_staging = drifting_copy
        try:
            hook_result = pb.backup_after_section_completed(
                completion_success=outcome.completion.success, run_id=fx.run_id, table_id=fx.table_id,
                section_id=fx.section_id, roots=fx.roots, backup_root=pf.backup_root_for(fx),
                producer_code_anchor=pf.PRODUCER_ANCHOR, created_at_utc="2026-11-01T00:00:00+00:00",
            )
        finally:
            pb._copy_files_to_staging = orig_copy
            victim.write_text(victim.read_text(encoding="utf-8").rstrip(), encoding="utf-8")

        assert outcome.completion.success, "Primaerabschluss-Erfolg darf durch Backup-Fehler nicht ruekwirkend geaendert werden"
        assert hook_result is not None and hook_result.attempted and not hook_result.succeeded
        assert hook_result.error


# ── restore_fresh_process ─────────────────────────────────────────────────


def test_restore_fresh_process_loads_full_population_without_old_root():
    """Guter Restore in einen NEU angelegten privaten `target_root`; ein
    ECHTER zweiter OS-Prozess (kein In-Memory-Zweitobjekt, 02_ARCHITEKTUR.md
    §3: 'Ein zweiter In-Memory-TuiSession-Konstruktor allein ist kein
    frischer Prozess') laedt darin NUR mit `target_root`-Pfaden: unbeteiligte
    Persona+Memory, inaktive Figur+Katalogzuordnung, aktiver Current -- der
    alte Root wird dem Subprozess nicht einmal mitgegeben."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"

        target = Path(td) / "restored"
        pb.restore_population(pf.backup_root_for(fx), target)

        script = f"""
import sys, json
sys.path.insert(0, {str(_REPO_ROOT)!r})
from pathlib import Path
from mmo_sim.core import store
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss import catalog

target = Path({str(target)!r})
ps_store = PersonaStateStore(schema_path=Path({str(root / "schema.json")!r}), default_states_dir=None)
bystander = ps_store.load_state({pf.BYSTANDER_PK!r}, states_dir=target / "states")
inactive_save = catalog.load_figure_save(target / "catalog", {pf.LEADER_PK!r}, {pf.INACTIVE_CHRONONAUT_ID!r})
leader_current = store.load_current_save_or_raise(
    target / "run", {pf.LEADER_PK!r}, ps_store, states_dir=target / "states",
)
print(json.dumps({{
    "bystander_learnings": bystander.get("learnings"),
    "inactive_present": inactive_save is not None,
    "inactive_char_id": (inactive_save or {{}}).get("characters", [{{}}])[0].get("id"),
    "leader_current_char_id": leader_current["characters"][0]["id"] if leader_current else None,
}}))
"""
        proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["bystander_learnings"] == ["Bystander-Erkenntnis: hat diesen Abschnitt nicht gesehen."]
        assert payload["inactive_present"] is True
        assert payload["inactive_char_id"] == pf.INACTIVE_CHRONONAUT_ID
        assert payload["leader_current_char_id"] == "chrono-leader"


def test_restore_rejects_existing_target_corrupted_generation_and_path_escape():
    """Drei kontrollierte Ablehnungen VOR jeder Aktivierung: belegtes
    Zielverzeichnis, beschaedigte Generation (Hashabweichung), Pfadausbruch
    im Manifest -- in KEINEM Fall bleibt ein teilaktivierbarer Bestand
    zurueck."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        backup_root = pf.backup_root_for(fx)
        gen_dir = backup_root / "generations" / result.generation_id

        existing_target = Path(td) / "existing"
        existing_target.mkdir()
        try:
            pb.restore_population(backup_root, existing_target)
            raise AssertionError("belegtes Zielverzeichnis haette abgelehnt werden muessen")
        except pb.RestoreRejectedError:
            pass

        victim = gen_dir / "states" / f"{pf.BYSTANDER_PK}.json"
        original_bytes = victim.read_bytes()
        victim.write_bytes(original_bytes + b"CORRUPT")
        target_corrupt = Path(td) / "restored-corrupt"
        try:
            pb.restore_population(backup_root, target_corrupt)
            raise AssertionError("beschaedigte Generation haette abgelehnt werden muessen")
        except pb.RestoreRejectedError:
            pass
        assert not target_corrupt.exists(), "kein teilaktivierbares Zielverzeichnis nach Ablehnung"
        victim.write_bytes(original_bytes)

        manifest_path = gen_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"].append({"role": "states", "rel_path": "../../etc/passwd", "size": 0, "sha256": "x" * 64})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        target_escape = Path(td) / "restored-escape"
        try:
            pb.restore_population(backup_root, target_escape)
            raise AssertionError("Pfadausbruch im Manifest haette abgelehnt werden muessen")
        except pb.RestoreRejectedError:
            pass
        assert not target_escape.exists()
        manifest["files"].pop()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        # Vierte Ablehnung: ein manipuliertes Manifest-Feld `generation_id`
        # (Dateiinhalt) darf den Kopier-Pfad in `restore_population` nicht aus
        # `generations/` herausschieben -- es muss mit dem geguardeten
        # Generationsordner uebereinstimmen, aus dem es gelesen wurde.
        for bad_manifest_gid in ("../../etc", "/etc", ".."):
            manifest["generation_id"] = bad_manifest_gid
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            target_mtamper = Path(td) / f"restored-mtamper-{abs(hash(bad_manifest_gid))}"
            try:
                pb.restore_population(backup_root, target_mtamper)
                raise AssertionError(
                    "manipuliertes Manifest-generation_id haette abgelehnt werden muessen"
                )
            except pb.RestoreRejectedError as exc:
                assert "stimmt nicht mit dem Generationsordner" in str(exc), (
                    f"Ablehnung kam nicht aus dem Manifest-ID-Check, sondern: {exc}"
                )
            assert not target_mtamper.exists(), "kein teilaktivierbares Ziel nach Ablehnung"
        manifest["generation_id"] = result.generation_id
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        # Fuenfte Ablehnung: ein unsicherer generation_id-Identifier selbst
        # (bedienbar via TUI `_cmd_restore`-Token) darf nicht in einen
        # Pfad-Join fliessen und aus `generations/` ausbrechen. Der Grund MUSS
        # aus dem Guard kommen (nicht incidentell "manifest fehlt").
        for bad_gen in ("../../etc", "..", "gen/../../etc", "/abs/path"):
            target_bad = Path(td) / f"restored-badgen-{abs(hash(bad_gen))}"
            try:
                pb.restore_population(backup_root, target_bad, generation_id=bad_gen)
                raise AssertionError(
                    f"unsichere generation_id {bad_gen!r} haette abgelehnt werden muessen"
                )
            except pb.RestoreRejectedError as exc:
                assert "unsichere Generation-ID" in str(exc), (
                    f"Ablehnung kam nicht aus dem Guard, sondern: {exc}"
                )
            assert not target_bad.exists(), "kein teilaktivierbares Ziel nach Ablehnung"

        # Original + gute Generation bleiben nach allen Ablehnungen nutzbar.
        target_ok = Path(td) / "restored-ok"
        pb.restore_population(backup_root, target_ok)
        assert (target_ok / "states" / f"{pf.BYSTANDER_PK}.json").is_file()


# ── restore_followup ──────────────────────────────────────────────────────


def test_restore_followup_real_write_and_fresh_reload():
    """Nach Restore: ein ECHTER zweiter Prozess spielt eine normale
    wirksame Folgeaktion (hier: `store.publish_current_save` mit
    veraendertem `xp`-Feld -- ein echter Schreibzugriff, kein JSON-Parsen)
    und speichert; ein DRITTER, ebenfalls frischer Prozess laedt erneut und
    sieht die Aenderung. Die urspruengliche Quellpopulation bleibt dabei
    bytegleich unveraendert."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        original_current_hash = _sha256(fx.roots.run_dir / "current_saves" / "leader_pk.json")

        target = Path(td) / "restored"
        pb.restore_population(pf.backup_root_for(fx), target)
        schema_path = root / "schema.json"

        followup_script = f"""
import sys
sys.path.insert(0, {str(_REPO_ROOT)!r})
from pathlib import Path
from mmo_sim.core import store
from mmo_sim.core.persona_state import PersonaStateStore

target = Path({str(target)!r})
ps_store = PersonaStateStore(schema_path=Path({str(schema_path)!r}), default_states_dir=None)
current = store.load_current_save_or_raise(
    target / "run", {pf.LEADER_PK!r}, ps_store, states_dir=target / "states",
)
current["characters"][0]["xp"] = 999
store.publish_current_save(target / "run", {pf.LEADER_PK!r}, current, ps_store, target / "states")
print("followup-done")
"""
        p1 = subprocess.run([sys.executable, "-c", followup_script], capture_output=True, text=True)
        assert p1.returncode == 0, p1.stderr

        reload_script = f"""
import sys, json
sys.path.insert(0, {str(_REPO_ROOT)!r})
from pathlib import Path
from mmo_sim.core import store
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss import catalog

target = Path({str(target)!r})
ps_store = PersonaStateStore(schema_path=Path({str(schema_path)!r}), default_states_dir=None)
current = store.load_current_save_or_raise(
    target / "run", {pf.LEADER_PK!r}, ps_store, states_dir=target / "states",
)
bystander = ps_store.load_state({pf.BYSTANDER_PK!r}, states_dir=target / "states")
inactive_save = catalog.load_figure_save(target / "catalog", {pf.LEADER_PK!r}, {pf.INACTIVE_CHRONONAUT_ID!r})
print(json.dumps({{
    "xp": current["characters"][0]["xp"],
    "bystander_still_present": bystander.get("persona_key") == {pf.BYSTANDER_PK!r},
    "inactive_still_present": inactive_save is not None,
}}))
"""
        p2 = subprocess.run([sys.executable, "-c", reload_script], capture_output=True, text=True)
        assert p2.returncode == 0, p2.stderr
        payload = json.loads(p2.stdout)
        assert payload["xp"] == 999, "Folgeaktion wurde im dritten frischen Prozess nicht wiedergefunden"
        assert payload["bystander_still_present"]
        assert payload["inactive_still_present"]

        assert _sha256(fx.roots.run_dir / "current_saves" / "leader_pk.json") == original_current_hash, (
            "Quellpopulation darf durch Restore+Folgeaktion NICHT veraendert werden"
        )


# ── privacy_and_exclusions ────────────────────────────────────────────────


def test_privacy_and_exclusions_locks_tmp_and_sentinels_excluded_nongeheime_prefs_included():
    """FAKE-Sentinel-Token (`FAKE_TOKEN_SENTINEL`, erkennbar NICHT echt),
    PID-OS-Lock (`lab.lock.json`) und eine transiente `*.tmp-*`-Restdatei
    fehlen im Manifest/Payload TROTZ physischer Praesenz in den gescannten
    Wurzeln; die nichtgeheimen Einstellungen (`ui_prefs*`, `last_participant.
    json`) bleiben dagegen erhalten. Zusaetzlich: ein konfiguriertes
    Backup-Ziel INNERHALB einer rekursiv gescannten Wurzel wird laut
    abgelehnt (kein rekursives Selbstbackup)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)
        assert (fx.roots.run_dir / "lab.lock.json").is_file(), "Fixture-Annahme verletzt"
        assert (fx.roots.states_dir / "ghost.json.tmp-424242").is_file(), "Fixture-Annahme verletzt"
        assert (fx.roots.prefs_root / "session_auth_sentinel.txt").read_text(encoding="utf-8") == (
            pf.FAKE_TOKEN_SENTINEL
        )

        files = pb.collect_population_files(fx.roots)
        rel_paths = {(f.role, f.rel_path) for f in files}
        assert not any(rp.endswith("lab.lock.json") for _, rp in rel_paths)
        assert not any("tmp-" in rp for _, rp in rel_paths)
        assert not any("session_auth_sentinel" in rp for _, rp in rel_paths)
        assert ("prefs", f"ui_prefs__{pf.LEADER_PK}.json") in rel_paths
        assert ("prefs", "last_participant.json") in rel_paths

        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        manifest_keys = {(f["role"], f["rel_path"]) for f in result.manifest["files"]}
        assert not any(rp.endswith("lab.lock.json") for _, rp in manifest_keys)
        assert not any("session_auth_sentinel" in rp for _, rp in manifest_keys)
        assert any("excluded" in result.manifest and result.manifest["excluded"] for _ in [0])

        key = pb.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id)
        try:
            pb.generate_population_backup(
                fx.roots, key, fx.roots.run_dir, producer_code_anchor=pf.PRODUCER_ANCHOR,
                created_at_utc="2026-11-01T00:00:00+00:00",
            )
            raise AssertionError("Backup-Ziel innerhalb von run_dir haette abgelehnt werden muessen")
        except pb.RootOverlapError:
            pass


def test_privacy_and_exclusions_symlink_never_dereferenced_regular_neighbor_kept():
    """Ein Symlink in einer rekursiv gescannten Wurzel (`states_dir`), der
    nach AUSSEN auf eine Datei AUSSERHALB der sechs Populationswurzeln
    zeigt, UND ein gleichartiger Symlink im `prefs`-Glob-Zweig werden NIE
    dereferenziert: der Linkzielinhalt (ein Fake-Geheimnis) taucht weder im
    Scan noch im Manifest/Staging/Payload auf. Ein regulaerer Nachbar
    (`leader_pk.json`) bleibt unveraendert gesichert (01_AUFTRAG.md §3,
    `03_ABNAHME.md` privacy_and_exclusions: 'Link-/Pfadausbruch ... in
    kontrollierter Fixture pruefen')."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "data"
        fx = pf.build_fixture(root)

        outside_secret = Path(td) / "outside_secret.txt"
        outside_secret.write_text("GEHEIM-AUSSERHALB-DER-SECHS-WURZELN", encoding="utf-8")

        link_in_states = fx.roots.states_dir / "evil_link.json"
        link_in_states.symlink_to(outside_secret)
        link_in_prefs = fx.roots.prefs_root / "ui_prefs_evil_link.json"
        link_in_prefs.symlink_to(outside_secret)
        assert link_in_states.is_symlink() and link_in_prefs.is_symlink(), "Fixtureannahme verletzt"

        files = pb.collect_population_files(fx.roots)
        rel_paths = {(f.role, f.rel_path) for f in files}
        assert ("states", "evil_link.json") not in rel_paths
        assert ("prefs", "ui_prefs_evil_link.json") not in rel_paths
        assert ("states", f"{pf.LEADER_PK}.json") in rel_paths, "regulaerer Nachbar fehlt im Scan"

        assert pf.play_section_to_success(fx).completion.success
        result = pf.run_backup(fx)
        assert result.status == "created"
        manifest_keys = {(f["role"], f["rel_path"]) for f in result.manifest["files"]}
        assert ("states", "evil_link.json") not in manifest_keys
        assert ("prefs", "ui_prefs_evil_link.json") not in manifest_keys
        assert ("states", f"{pf.LEADER_PK}.json") in manifest_keys, "regulaerer Nachbar fehlt"
        excluded_text = " ".join(result.manifest["excluded"])
        assert "evil_link.json" in excluded_text
        assert "ui_prefs_evil_link.json" in excluded_text

        generation_dir = pf.backup_root_for(fx) / "generations" / result.generation_id
        secret_bytes = outside_secret.read_bytes()
        for p in generation_dir.rglob("*"):
            if p.is_file():
                assert p.read_bytes() != secret_bytes, f"Linkzielinhalt in Generation gelandet: {p}"


# ── Produktionscaller-Verdrahtung (TUI + Lobby/Lab) ──────────────────────


class _MarkerGm:
    """Liefert den Abschluss-Marker SOFORT (Transportrand-Fake, wie
    `test_a04_shared_app_service.py`)."""

    def __init__(self, save_text: str = ""):
        self.calls = 0
        self.output_limit_tokens = 2000
        self._save_text = save_text

    def turn(self, turn_idx: int, user_text: str, output_limit_tokens: float | None = None) -> dict:
        self.calls += 1
        content = f"{self._save_text}\n{COMPLETION_MARKER}" if self._save_text else COMPLETION_MARKER
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def test_tui_caller_wires_population_backup_after_section_completed():
    """Beweist die ECHTE Verdrahtung in `ui/tui.py:TuiSession.
    _run_table_round` (NICHT nur die Modullogik): ein echter
    `TuiSession._cmd_local_round()`-Lauf (wie `test_a04_shared_app_service.
    py`s TUI-Pfad) erzeugt nach Abschluss tatsaechlich eine Generation unter
    `<data_dir>/population_backups/generations`."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        states_dir = root / "states"
        states_dir.mkdir()
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        catalog_dir = root / "catalog"
        participant_id = "p_tui_popbackup"

        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        ps_store.save_state(participant_id, {
            "v": 2, "persona_key": participant_id, "rounds_played": 0,
            "plays_char": {"character_id": "chrono-popbackup"},
        }, states_dir=states_dir)

        save_block = full_v7_save("chrono-popbackup", name="Test")
        onboarding.start_or_resume(onboarding_dir, participant_id)
        onboarding.complete_with_save(
            onboarding_dir, participant_id, save_block, ZeitrissHarvestValidator(), "chrono-popbackup",
        )

        gm = _MarkerGm(save_text=full_v7_block_text("chrono-popbackup", name="Test"))
        scripted = iter(["Meine Aktion.", ""])  # 2.: freiwillige lokale Reflexionsnotiz, leer

        def _input_fn(prompt: str = "") -> str:
            try:
                return next(scripted)
            except StopIteration:
                raise EOFError()

        write_test_profile(run_dir)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, participant_id,
            input_fn=_input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_local_round()
        assert any("Abschnitt abgeschlossen" in line for line in printed), printed

        backup_root = session._population_backup_root_dir()
        gens = list((backup_root / "generations").iterdir()) if (backup_root / "generations").exists() else []
        assert gens, "ui/tui.py:_run_table_round hat keine Populationsgeneration ausgeloest"

        # Bedienoberflaeche 'backup'/'backup retry' real durchspielen.
        session._cmd_backup([])
        assert any("Letzte gute Generation" in line for line in printed)


def test_lobby_flow_caller_wires_population_backup_after_section_completed():
    """Beweist die ECHTE Verdrahtung in `core/lobby_flow.py:
    play_bound_table` (von TUI-Lobby UND Lab verwendet, s. dessen
    Moduldocstring) -- ein echter Zweipersonen-Tisch ueber `play_bound_table`
    erzeugt nach Abschluss ebenfalls eine Generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        states_dir = root / "states"
        states_dir.mkdir()
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        catalog_dir = root / "catalog"

        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        for pk, cid in (("leader_pk", "chrono-leader"), ("guest_pk", "chrono-guest")):
            ps_store.save_state(pk, {
                "v": 2, "persona_key": pk, "rounds_played": 0, "plays_char": {"character_id": cid},
            }, states_dir=states_dir)

        leader_save = full_v7_save("chrono-leader", name="Testfigur")
        guest_save = full_v7_save("chrono-guest", name="Testfigur")
        debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
        gm = ScriptedGmTransport(["SL-Antwort auf Anker.", "SL-Antwort auf Gast-Import.", debrief])
        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion Leader.", origin_source="fake:leader-reflect"),
        ])
        guest_driver = ScriptedDriver([
            ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
            ParticipantDecision(text="Reflexion Gast.", origin_source="fake:guest-reflect"),
        ])
        drivers = {"leader_pk": leader_driver, "guest_pk": guest_driver}

        write_test_profile(run_dir)
        session = TuiSession(
            onboarding_dir, catalog_dir, "leader_pk",
            input_fn=lambda prompt="": "", print_fn=lambda *a, **k: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: drivers[pk],
        )

        lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        lobby.join("guest_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-lobbyflow",
            offer_log_events=[
                {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
                {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
            ],
            chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
        )
        assert table is not None, derivation

        outcome = lobby_flow.play_bound_table(
            session, lobby, table, offer_events=[], source_offer_id=None,
            active_saves={"leader_pk": None, "guest_pk": None},
        )
        assert outcome.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED

        backup_root = session.onboarding_dir.parent / "population_backups"
        gens = list((backup_root / "generations").iterdir()) if (backup_root / "generations").exists() else []
        assert gens, "core/lobby_flow.py:play_bound_table hat keine Populationsgeneration ausgeloest"


def test_tui_restore_caller_wires_restore_population_with_correct_arguments():
    """Fokus-Test analog zu den *_caller_wires-Tests (BLOCKER 2): beweist,
    dass `TuiSession._cmd_restore` existiert und `population_backup.
    restore_population` mit dem korrekten `backup_root`, dem uebergebenen
    (neuen) `target_root` und der uebergebenen `generation_id` aufruft --
    keine schwere End-to-End-TUI-Simulation noetig (der echte Restore-Weg
    selbst ist bereits ueber `test_restore_fresh_process_loads_full_
    population_without_old_root` bewiesen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        printed: list[str] = []
        session = TuiSession(
            root / "onboarding", root / "catalog", "p_restore_focus",
            input_fn=lambda prompt="": "", print_fn=printed.append,
        )

        # Ohne Ziel-Root: ehrliche Benutzungsmeldung, kein Aufruf.
        session._cmd_restore([])
        assert any("Benutzung" in line for line in printed), printed

        calls: list[tuple] = []
        orig_restore = pb.restore_population

        def _fake_restore_population(backup_root, target_root, generation_id=None):
            calls.append((backup_root, Path(target_root), generation_id))
            return pb.RestoreOutcome(
                target_root=Path(target_root), roots=None,
                generation_id="gen-fake", manifest={"generation_id": "gen-fake"},
            )

        pb.restore_population = _fake_restore_population
        try:
            target = root / "frisches_ziel"
            session._cmd_restore([str(target), "gen-abc"])
            session._cmd_restore([str(root / "frisches_ziel_2")])
        finally:
            pb.restore_population = orig_restore

        assert len(calls) == 2, "restore_population wurde nicht je einmal pro Aufruf erreicht"
        assert calls[0] == (session._population_backup_root_dir(), target, "gen-abc")
        assert calls[1][2] is None, "ohne generation-id muss None (= latest) durchgereicht werden"
        assert any("gen-fake" in line for line in printed), printed


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
