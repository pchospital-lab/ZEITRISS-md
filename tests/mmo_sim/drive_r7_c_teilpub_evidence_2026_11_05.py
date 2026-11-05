#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r7_c_teilpub_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R7, Familie `c_teilpub` (G4/C, 01_NACHZUG.md §3,
GUEST-PUBLICATION.md §5, 02_NACHWEISE_UND_RUECKGABE.md §1 "G4/bestehendes
C"): schliesst den von GUEST-PUBLICATION.md §5 benannten Nachweisrest des
R6-Belegs `drive_r6_c_teilpub_evidence_2026_11_05.py` -- dessen `_snapshot`
erfasste an den vier Phasen NUR Substitute statt der tatsaechlich
verlangten Koerper:

  - `accepted_entscheid_grant` (`creation_grants.grant_status`, Status
    'approved') IST NICHT der atomare `accepted`-Annahmeentscheid -- der
    echte Entscheid liegt unter `run_dir/table_decisions/<decision_id>.json`
    (`core.admission.try_commit_table_decision`/`read_table_decision`,
    `decision_id` ueber `creation_service._creation_decision_id`) und wurde
    im R6-Beleg NUR im finalen Gesamtexport (`run/lab.decide.table.
    creation-operator2-guest2-gen1.json`), NICHT an den vier benannten
    Phasenschnitten gesichert.
  - `claim_chrononaut_active_binding` (`store.chrononaut_active_binding`,
    ein reiner TISCHBINDUNGS-Boolean) IST NICHT der generation-/figur-
    gebundene Versuchclaim -- der echte Claim liegt unter
    `onboarding.record_attempt_claim`/`_attempt_claim_path` (`key=
    gast-erschaffung-claim::<guest_id>`, Datei `attempt-claim__<key>.json`
    in GENAU demselben `onboarding_dir`).
  - `private_onboarding_final_save`/`pending_step` (zwei Felder aus
    `onboarding.peek`) sind NICHT der vollstaendige private Onboarding-
    Koerper (`participant_id`/`status`/`steps`/`final_save_best_effort`
    fehlten) -- dieser Treiber liest die ROHE Onboarding-Datei direkt.
  - `katalog_entries` (nur `participant_id`/`chrononaut_id`-Paare aus
    `catalog.list_for_participant`) ist NICHT der vollstaendige Katalog-
    koerper (`persona_key`/`display_name`/`last_selected_chrononaut_id`/
    `active_chrononaut_id` fehlten) -- dieser Treiber liest die ROHE
    Katalogdatei direkt.

Der konkrete B-Versionsfehler (Hardexit nach Version 0001 VOR State-
Zeiger) ist produktseitig WEITERHIN bereits behoben (R5/R6, KEINE neue
Storearbeit) -- Harness/Ablauf bleiben UNVERAENDERT identisch zum R6-Beleg
(derselbe `_r5_launcher_hardexit_after_version_before_pointer.py`, derselbe
Dreiprozessablauf: Unterbrechung -> normaler Retry uebernimmt die verwaiste
Version 0001 -> letzter identischer Retry). NUR die vier Phasenschnitte
erfassen jetzt die ECHTEN verlangten Koerper vollstaendig.

"Vorhandene Originale zuerst" (01_NACHZUG.md §3) wurde geprueft: der
vorhandene R6-Rueckgabe-Referenzexport unter `…/r6-runs/c_teilpub/` enthaelt
den echten Entscheid NUR im finalen `run/`-Gesamtexport (nicht an den vier
Phasen) und KEINEN Versuchclaim irgendwo im Paket (GUEST-PUBLICATION.md §5:
"im gesamten gelieferten Paket wurde kein Hash-/Bytegleiches Gegenstueck
gefunden") -- die damaligen PHASENGEBUNDENEN Originalkoerper fuer Entscheid/
Claim/volles Onboarding/vollen Katalog existieren NICHT rekonstruierbar aus
Enddaten. Dieser Treiber wiederholt daher GENAU diesen bekannten C-Beleg
(neuer echter Lauf) mit vollstaendiger Sicherung an allen vier Phasen.

ECHTER Launcher-Subprozess (literal `scripts/mmo_sim.py` bzw. gebundene
Hardexit-Skriptdatei), GM-Anbieter NUR als FIX5-Grenzinjektion, NIE Live-
Modell.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import subprocess  # noqa: E402

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path(os.environ.get(
    "R7_OUT_DIR",
    "/home/altair/zr-betreiber-gast-20261105/r7/run/evidence/r7-runs/c_teilpub",
))
_RUN_ID = "c_teilpub_full_real_bodies_decision_claim_onboarding_catalog_at_all_four_phases"
_HARDEXIT_AFTER_VERSION = _HERE / "_r5_launcher_hardexit_after_version_before_pointer.py"
_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _snapshot(
    *, run_dir: Path, states_dir: Path, guest_onboarding: Path, guest_catalog: Path,
    participant_id: str, char_id: str, operator_id: str, generation: int,
    versions_dir: Path, current_path: Path, states_path: Path,
) -> dict:
    """Vollstaendiger Koerpersatz EINES Zeitpunkts -- ECHTE Koerper statt
    Substitute (GUEST-PUBLICATION.md §5):
      - `accepted_decision`: der tatsaechliche atomare Annahmeentscheid
        (`admission.read_table_decision`, NICHT `grant_status`).
      - `attempt_claim`: die ROHE Claim-Datei (`onboarding.
        _attempt_claim_path`), NICHT `chrononaut_active_binding`.
      - `private_onboarding_full`: die ROHE Onboarding-Datei
        (participant_id/status/steps/final_save/final_save_best_effort),
        NICHT nur `.final_save`/`.pending_step`.
      - `catalog_full`: die ROHE Katalogdatei (entries/last_selected_
        chrononaut_id/active_chrononaut_id), NICHT nur die Entry-Paare.
    Current/Version/States bleiben wie im R6-Beleg (dort nicht beanstandet)."""
    decision_id = creation_grants._creation_decision_id(operator_id, participant_id, generation)
    accepted_decision = admission.read_table_decision(run_dir, decision_id)

    attempt_key = creation_grants.guest_attempt_claim_key(participant_id)
    claim_path = onboarding._attempt_claim_path(Path(guest_onboarding), attempt_key)
    attempt_claim = json.loads(claim_path.read_text(encoding="utf-8")) if claim_path.exists() else None

    onboarding_path = onboarding._path(Path(guest_onboarding), participant_id)
    private_onboarding_full = (
        json.loads(onboarding_path.read_text(encoding="utf-8")) if onboarding_path.exists() else None
    )

    catalog_path = catalog._path(Path(guest_catalog), participant_id)
    catalog_full = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else None

    version_files = sorted(versions_dir.glob("*.json")) if versions_dir.exists() else []
    # GUEST-PUBLICATION.md §4 Warnung: die blosse Dateiexistenz von
    # `current_saves/<id>.json` ("current_pointer_present") beweist KEINEN
    # gueltigen State-Zeiger -- `store.publish_current_save` schreibt die
    # Direktdatei ALS ERSTEN Schritt, VOR Versionsdatei UND State-Zeiger
    # (`core/store.py:publish_current_save`: "direct -> NEUE Versionsdatei
    # -> State-Zeiger"). Die AUTORITATIVE Pruefung ist `store.
    # load_current_save` (liest den State-Zeiger, nicht die Rohdatei).
    ps_store_snap = PersonaStateStore(schema_path=_SCHEMA_PATH)
    current_readable_via_state_pointer = store.load_current_save(
        run_dir, participant_id, ps_store_snap, states_dir=states_dir,
    ) is not None
    return {
        "accepted_decision": accepted_decision,
        "attempt_claim": attempt_claim,
        "private_onboarding_full": private_onboarding_full,
        "catalog_full": catalog_full,
        "current_direct_file_present": current_path.exists(),
        "current_readable_via_state_pointer": current_readable_via_state_pointer,
        "current_block": json.loads(current_path.read_text(encoding="utf-8")) if current_path.exists() else None,
        "version_files": [p.name for p in version_files],
        "version_blocks": {
            p.name: json.loads(p.read_text(encoding="utf-8")) for p in version_files
        },
        "states_present": states_path.exists(),
        "states_block": json.loads(states_path.read_text(encoding="utf-8")) if states_path.exists() else None,
    }


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        operator_id = "operator2"
        participant_id = "guest2"
        char_id = "CHR-R7C-TEILPUB-GAST"
        generation = 1
        final_block = full_v7_save(char_id, name="GastR7CTeilpub", save_id="fixture-r7c-teilpub-guest-001")
        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr Ursprung?"
        final_content = "```json\n" + json.dumps(final_block, ensure_ascii=False) + "\n```"
        r4._write_gm_double_config(cfg_path, responses=[q1, q2, final_content], calls_log=calls_log)
        env = r4._gm_double_env(cfg_path)

        guest_onboarding = op_data / "guests" / participant_id / "onboarding"
        guest_catalog = op_data / "guests" / participant_id / "catalog"
        versions_dir = run_dir / "current_saves" / f"{participant_id}__versions"
        current_path = run_dir / "current_saves" / f"{participant_id}.json"
        states_path = states_dir / f"{participant_id}.json"

        def snap() -> dict:
            return _snapshot(
                run_dir=run_dir, states_dir=states_dir, guest_onboarding=guest_onboarding,
                guest_catalog=guest_catalog, participant_id=participant_id, char_id=char_id,
                operator_id=operator_id, generation=generation,
                versions_dir=versions_dir, current_path=current_path, states_path=states_path,
            )

        # ── Vorher (vor jedem Prozessstart): weder Entscheid noch Claim
        # noch Onboarding/Katalog koennen real existieren.
        snapshot_before_any_process = snap()
        assert snapshot_before_any_process["accepted_decision"] is None, snapshot_before_any_process["accepted_decision"]
        assert snapshot_before_any_process["attempt_claim"] is None, snapshot_before_any_process["attempt_claim"]
        assert snapshot_before_any_process["private_onboarding_full"] is None
        assert snapshot_before_any_process["catalog_full"] is None

        # ── Prozess 1: echter Dialog bis Annahme, dann Hardexit GENAU
        # zwischen Versionsdatei und State-Zeiger (unveraenderter R5/R6-
        # Helper, KEINE neue Storearbeit).
        in_fifo1 = fifo_dir / "guest_in_1.fifo"
        out_fifo1 = fifo_dir / "guest_out_1.fifo"
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_AFTER_VERSION),
            "--participant", operator_id, "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{participant_id}:{in_fifo1}:{out_fifo1}",
        ]
        utc_start1 = r6.utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r4._open_guest_fifo_pair(in_fifo1, out_fifo1)
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_guest(in_f1, f"gast-erschaffung-anfragen {operator_id}")
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_op(proc1, f"gast-erschaffung-annehmen {participant_id}")
        time.sleep(0.6)
        r4._send_guest(in_f1, f"gast-erschaffung-dialog {operator_id}")
        r4._wait_for_marker(out_f1, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_f1, "Mira")
        r4._wait_for_marker(out_f1, f"[SL] {q2}", overall=15.0)
        r4._send_guest(in_f1, "Ein Forscherteam.")
        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        assert proc1.returncode == 94, (
            f"R7/c_teilpub: Prozess 1 muss ueber os._exit(94) GENAU zwischen Versionsdatei und "
            f"State-Zeiger enden -- rc={proc1.returncode} stderr={stderr1!r}"
        )
        r6.write_process_result(
            _OUT_DIR, "proc1_hardexit_after_version_before_pointer", argv=argv1, cwd=str(_REPO_ROOT),
            utc_start=utc_start1, utc_end=utc_end1, exit_code=proc1.returncode,
            stdout_text=stdout1, stderr_text=stderr1,
        )
        mf.record_process_files(
            "proc1_hardexit_after_version_before_pointer",
            aussage="c_teilpub_proc1_transcript", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )

        version_files_orphan = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_orphan] == ["0001.json"], (
            f"R7/c_teilpub: nach Hardexit wird GENAU 0001.json erwartet: {version_files_orphan}"
        )
        orphan_version_block = json.loads((versions_dir / "0001.json").read_text(encoding="utf-8"))
        assert orphan_version_block == final_block, "R7/c_teilpub: 0001.json muss exakt den angenommenen Save tragen."
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        assert store.load_current_save(run_dir, participant_id, ps_store, states_dir=states_dir) is None, (
            "R7/c_teilpub: vor dem Retry darf (noch) KEIN Current-Zeiger auf 0001.json gesetzt sein (Orphan)."
        )

        # ── Vollstaendiger ECHTER Koerpersatz AN DER UNTERBRECHUNG.
        snapshot_at_interrupt = snap()
        assert snapshot_at_interrupt["accepted_decision"] is not None and \
            snapshot_at_interrupt["accepted_decision"].get("decision") == "accepted", (
            f"R7/c_teilpub: der echte atomare Annahmeentscheid muss AN DER UNTERBRECHUNG bereits "
            f"durabel vorliegen (record_attempt_claim/catalog-Writes laufen VOR publish_current_save, "
            f"das die Hardexit-Grenze setzt): {snapshot_at_interrupt['accepted_decision']}"
        )
        assert snapshot_at_interrupt["attempt_claim"] is not None and \
            snapshot_at_interrupt["attempt_claim"].get("char_id") == char_id and \
            snapshot_at_interrupt["attempt_claim"].get("generation") == generation, (
            f"R7/c_teilpub: der generation-/figurgebundene Versuchclaim muss AN DER UNTERBRECHUNG "
            f"bereits durabel vorliegen: {snapshot_at_interrupt['attempt_claim']}"
        )
        assert snapshot_at_interrupt["private_onboarding_full"] is not None and \
            snapshot_at_interrupt["private_onboarding_full"].get("status") == "completed", (
            f"R7/c_teilpub: das volle private Onboarding muss AN DER UNTERBRECHUNG bereits "
            f"'completed' mit final_save vorliegen: {snapshot_at_interrupt['private_onboarding_full']}"
        )
        assert snapshot_at_interrupt["catalog_full"] is not None and \
            len(snapshot_at_interrupt["catalog_full"].get("entries", [])) == 1, (
            f"R7/c_teilpub: der volle Katalogkoerper muss AN DER UNTERBRECHUNG bereits die Figur "
            f"enthalten: {snapshot_at_interrupt['catalog_full']}"
        )
        mf.write_json_body(
            "snapshot_at_interrupt.json", snapshot_at_interrupt,
            aussage="c_teilpub_full_real_body_set_at_interruption_boundary", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Prozess 2: normaler (UNGEPATCHTER) Retry uebernimmt den
        # erreichten Schritt -- KEIN 0002.json, KEIN zusaetzlicher GM-Call.
        in_fifo2 = fifo_dir / "guest_in_2.fifo"
        out_fifo2 = fifo_dir / "guest_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", operator_id, "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{participant_id}:{in_fifo2}:{out_fifo2}",
        ]
        utc_start2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv2, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f2, out_f2 = r4._open_guest_fifo_pair(in_fifo2, out_fifo2)
        r4._drain(out_f2, settle=0.6, overall=10.0)
        calls_before = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        r4._send_guest(in_f2, f"gast-erschaffung-dialog {operator_id}")
        retry_out = r4._drain(out_f2, settle=1.0, overall=15.0)
        joined_retry = "".join(retry_out)
        calls_after = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        assert calls_after == calls_before, "R7/c_teilpub: die Uebernahme braucht KEINEN neuen GM-Turn."
        assert "Gast-Erschaffung abgeschlossen" in joined_retry, joined_retry

        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r6.utc(time.time())
        in_f2.close()
        out_f2.close()
        assert proc2.returncode == 0, f"R7/c_teilpub: Retry-Prozess gescheitert: {stderr2}"
        r6.write_process_result(
            _OUT_DIR, "proc2_normal_retry_adopts_orphan_version", argv=argv2, cwd=str(_REPO_ROOT),
            utc_start=utc_start2, utc_end=utc_end2, exit_code=proc2.returncode,
            stdout_text=stdout2, stderr_text=stderr2,
        )
        mf.record_process_files(
            "proc2_normal_retry_adopts_orphan_version",
            aussage="c_teilpub_proc2_transcript", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )

        version_files_after = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_after] == ["0001.json"], (
            f"R7/c_teilpub: der Retry UEBERNIMMT die verwaiste 0001.json -- KEIN 0002.json: "
            f"{[p.name for p in version_files_after]}"
        )
        published = store.load_current_save_or_raise(run_dir, participant_id, ps_store, states_dir=states_dir)
        assert published == final_block, "R7/c_teilpub: Current-Zeiger zeigt nach Uebernahme auf 0001.json == Save."
        catalog_entries_after_retry = len(catalog.list_for_participant(guest_catalog, participant_id))
        assert catalog_entries_after_retry == 1, (
            f"R7/c_teilpub: GENAU eine Katalogfigur erwartet: {catalog_entries_after_retry}"
        )

        # ── Vollstaendiger ECHTER Koerpersatz NACH FERTIGSTELLUNG.
        snapshot_after_completion = snap()
        assert snapshot_after_completion["current_readable_via_state_pointer"] is True, (
            "R7/c_teilpub: nach Fertigstellung muss der Current-Zeiger (State-Pointer, NICHT nur die "
            "Direktdatei) lesbar sein."
        )
        mf.write_json_body(
            "snapshot_after_completion.json", snapshot_after_completion,
            aussage="c_teilpub_full_real_body_set_after_completion", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Vollstaendiger ECHTER Koerpersatz UNMITTELBAR VOR dem letzten
        # identischen Retry.
        snapshot_before_last_identical_retry = snap()
        mf.write_json_body(
            "snapshot_before_last_identical_retry.json", snapshot_before_last_identical_retry,
            aussage="c_teilpub_full_real_body_set_immediately_before_last_identical_retry", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Prozess 3: weiterer identischer Retry bleibt bei einer Version,
        # KEIN zusaetzlicher GM-Call, KEINE zweite Figur-/Claimwirkung.
        in_fifo3 = fifo_dir / "guest_in_3.fifo"
        out_fifo3 = fifo_dir / "guest_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", operator_id, "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{participant_id}:{in_fifo3}:{out_fifo3}",
        ]
        utc_start3 = r6.utc(time.time())
        proc3 = subprocess.Popen(
            argv3, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f3, out_f3 = r4._open_guest_fifo_pair(in_fifo3, out_fifo3)
        r4._drain(out_f3, settle=0.6, overall=10.0)
        calls_before_3 = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        r4._send_guest(in_f3, f"gast-erschaffung-dialog {operator_id}")
        r4._drain(out_f3, settle=1.0, overall=15.0)
        calls_after_3 = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        assert calls_after_3 == calls_before_3, "R7/c_teilpub: der letzte identische Retry braucht KEINEN neuen GM-Turn."
        r4._send_op(proc3, "beenden")
        stdout3, stderr3 = proc3.communicate(timeout=30)
        utc_end3 = r6.utc(time.time())
        in_f3.close()
        out_f3.close()
        assert proc3.returncode == 0, f"R7/c_teilpub: Prozess 3 gescheitert: {stderr3}"
        r6.write_process_result(
            _OUT_DIR, "proc3_identical_retry_version_count_stays_1", argv=argv3, cwd=str(_REPO_ROOT),
            utc_start=utc_start3, utc_end=utc_end3, exit_code=proc3.returncode,
            stdout_text=stdout3, stderr_text=stderr3,
        )
        mf.record_process_files(
            "proc3_identical_retry_version_count_stays_1",
            aussage="c_teilpub_proc3_transcript", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )

        version_files_final = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_final] == ["0001.json"], (
            f"R7/c_teilpub: identischer Retry darf keine zweite Version erzeugen: "
            f"{[p.name for p in version_files_final]}"
        )

        # ── Vollstaendiger ECHTER Koerpersatz UNMITTELBAR NACH dem letzten
        # identischen Retry.
        snapshot_after_last_identical_retry = snap()
        mf.write_json_body(
            "snapshot_after_last_identical_retry.json", snapshot_after_last_identical_retry,
            aussage="c_teilpub_full_real_body_set_immediately_after_last_identical_retry", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        assert snapshot_after_last_identical_retry == snapshot_before_last_identical_retry, (
            "R7/c_teilpub: der letzte identische Retry darf GENAU NICHTS am vollen Koerpersatz veraendern "
            "(kein zweiter Entscheid/Claim/Figur/Version)."
        )
        assert snapshot_after_completion == snapshot_before_last_identical_retry, (
            "R7/c_teilpub: nach der Uebernahme der verwaisten Version bleibt der volle Koerpersatz "
            "unveraendert bis zum (und nach dem) letzten identischen Retry."
        )
        assert snapshot_at_interrupt["version_files"] == snapshot_after_completion["version_files"], (
            "R7/c_teilpub: die Versionsdatei selbst (0001.json) ist an der Unterbrechung bereits "
            "identisch zum fertiggestellten Stand -- nur der Current-Zeiger fehlt noch."
        )
        # Entscheid/Claim/Onboarding sind BEREITS an der Unterbrechung
        # vollstaendig identisch zum Fertigstellungsstand (sie werden alle
        # VOR `publish_current_save` geschrieben, s. `_finish_granted_
        # guest_creation`-Reihenfolge oben) -- explizit geprueft statt
        # behauptet.
        assert snapshot_at_interrupt["accepted_decision"] == snapshot_after_completion["accepted_decision"], (
            "R7/c_teilpub: der Annahmeentscheid ist an der Unterbrechung bereits identisch zum "
            "Fertigstellungsstand."
        )
        assert snapshot_at_interrupt["attempt_claim"] == snapshot_after_completion["attempt_claim"], (
            "R7/c_teilpub: der Versuchclaim ist an der Unterbrechung bereits identisch zum "
            "Fertigstellungsstand."
        )
        assert snapshot_at_interrupt["private_onboarding_full"] == snapshot_after_completion["private_onboarding_full"], (
            "R7/c_teilpub: das volle private Onboarding ist an der Unterbrechung bereits identisch "
            "zum Fertigstellungsstand."
        )
        # Die Katalog-FIGURENREGISTRIERUNG (`entries`) steht ebenfalls schon
        # an der Unterbrechung fest -- `catalog.register`/`store_figure_
        # save` laufen VOR `publish_current_save` (s. Reihenfolge oben).
        assert snapshot_at_interrupt["catalog_full"]["entries"] == snapshot_after_completion["catalog_full"]["entries"], (
            "R7/c_teilpub: die Katalog-Figurenregistrierung ist an der Unterbrechung bereits identisch "
            "zum Fertigstellungsstand."
        )
        # EHRLICH ANDERS (empirischer Befund, NICHT aus dem Order-Text
        # vorab angenommen): `catalog.bind_for_section` (tui.py:6705) laeuft
        # ERST NACH einem ERFOLGREICHEN `publish_current_save`-Aufruf
        # (:6700-6705) -- in Prozess 1 wird dieser Aufruf durch den
        # Hardexit NIE beendet, `bind_for_section` wird daher an der
        # Unterbrechung NIE erreicht. `active_chrononaut_id`/`last_
        # selected_chrononaut_id` bleiben an der Unterbrechung deshalb
        # ECHT `None` -- GENAU DIESELBE Vollendungsgrenze wie der Current-
        # Zeiger selbst (nicht zwei unabhaengige Luecken, sondern dieselbe
        # einzige Fertigstellungsgrenze an zwei Koerpern sichtbar).
        assert snapshot_at_interrupt["catalog_full"]["active_chrononaut_id"] is None, (
            f"R7/c_teilpub: an der Unterbrechung darf catalog.bind_for_section NOCH NICHT gelaufen "
            f"sein (erst NACH erfolgreichem publish_current_save, dasselbe NICHT erreichte "
            f"Vollendungsgate wie der Current-Zeiger): {snapshot_at_interrupt['catalog_full']}"
        )
        assert snapshot_after_completion["catalog_full"]["active_chrononaut_id"] == char_id, (
            f"R7/c_teilpub: NACH Fertigstellung muss die aktive Katalogbindung real gesetzt sein: "
            f"{snapshot_after_completion['catalog_full']}"
        )
        # GUEST-PUBLICATION.md §4 Warnung bestaetigt: die Direktdatei
        # EXISTIERT an der Unterbrechung bereits (sie ist der ERSTE
        # Schreibschritt in `publish_current_save`, VOR Versionsdatei UND
        # State-Zeiger) -- NUR die AUTORITATIVE State-Zeiger-Lesung ist
        # (noch) `None` (Orphan-Luecke).
        assert snapshot_at_interrupt["current_direct_file_present"] is True, (
            f"R7/c_teilpub: die Current-DIREKTDATEI wird bereits VOR der Versionsdatei geschrieben "
            f"(store.py:publish_current_save) -- an der Unterbrechung muss sie real existieren: "
            f"{snapshot_at_interrupt['current_direct_file_present']}"
        )
        assert snapshot_at_interrupt["current_readable_via_state_pointer"] is False, (
            "R7/c_teilpub: der State-ZEIGER (NICHT die Direktdatei) ist an der Unterbrechung (noch) "
            "nicht lesbar (Orphan-Luecke, wird erst beim Retry berechtigt ergaenzt) -- dieselbe "
            "Vollendungsgrenze wie die Katalog-Aktivbindung oben."
        )

        mf.export_tree(
            run_dir, "run", aussage="c_teilpub_run_dir_final", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )
        mf.export_tree(
            states_dir, "states", aussage="c_teilpub_states_dir_final", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.export_tree(
            guest_onboarding, "guest_onboarding", aussage="c_teilpub_guest_onboarding_final", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.export_tree(
            guest_catalog, "guest_catalog", aussage="c_teilpub_guest_catalog_final", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="c_teilpub_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "c_teilpub", "aussage": (
                "G4/C (01_NACHZUG.md §3, GUEST-PUBLICATION.md §5): derselbe bereits funktionierende "
                "Teilpublikations-/Retry-Mechanismus (KEINE neue Storearbeit) wird jetzt an allen vier "
                "Phasen mit den TATSAECHLICH verlangten Koerpern belegt: echter atomarer accepted-"
                "Entscheid (admission.read_table_decision, NICHT grant_status), echter generation-/"
                "figurgebundener Versuchclaim (onboarding-Claim-Datei, NICHT chrononaut_active_binding), "
                "vollstaendiges privates Onboarding (volle Rohdatei, NICHT nur final_save/pending_step), "
                "vollstaendiger Katalogkoerper (volle Rohdatei, NICHT nur Entry-Paare). Entscheid/Claim/"
                "Onboarding/Katalogregistrierung liegen BEREITS an der Unterbrechung identisch zum "
                "Fertigstellungsstand vor -- echte Unterschiede (empirisch gefunden, nicht aus dem "
                "Order-Text vorab angenommen) sind der (noch) nicht lesbare Current-State-Zeiger "
                "(Orphan-Luecke) UND die Katalog-Aktivbindung (active/last_selected_chrononaut_id, "
                "dieselbe Vollendungsgrenze wie der Current-Zeiger, s. tui.py:6700-6705). Genau "
                "Version 0001; kein zusaetzlicher GM-Call; letzter identischer Retry erzeugt KEINE zweite "
                "Version/Figur/Claimwirkung."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "produktcode_fundstellen": [
                "mmo_sim/ui/tui.py:6530-6700 (_finish_granted_guest_creation: Reihenfolge Entscheid -> "
                "Claim -> Katalog -> publish_current_save/Version -> State-Zeiger)",
                "mmo_sim/core/admission.py (try_commit_table_decision/read_table_decision, generischer "
                "atomarer Entscheid-Slot)",
                "mmo_sim/domain/zeitriss/creation_service.py:106-111 (guest_attempt_claim_key), "
                "200-210 (_creation_decision_id)",
                "mmo_sim/domain/zeitriss/onboarding.py:433-470 (record_attempt_claim/attempt_claim_matches/"
                "_attempt_claim_path)",
                "mmo_sim/domain/zeitriss/onboarding.py:40-60 (_path/_load: volle Onboarding-Rohdatei)",
                "mmo_sim/domain/zeitriss/catalog.py:28-45 (_path/_load: volle Katalog-Rohdatei)",
                "tests/mmo_sim/_r5_launcher_hardexit_after_version_before_pointer.py (unveraenderter "
                "Hardexit-Helper, GENAU zwischen Versionsdatei und State-Zeiger)",
            ],
            "proc1_exit": proc1.returncode, "proc2_exit": proc2.returncode, "proc3_exit": proc3.returncode,
            "version_files_final": [p.name for p in version_files_final],
            "entscheid_claim_onboarding_katalogregistrierung_bereits_an_unterbrechung_identisch": True,
            "unterschiede_an_unterbrechung_empirisch_gefunden": [
                "current_pointer_present (Orphan-Luecke)",
                "catalog_full.active_chrononaut_id/last_selected_chrononaut_id (catalog.bind_for_section "
                "laeuft erst NACH erfolgreichem publish_current_save, tui.py:6700-6705) -- DIESELBE "
                "Vollendungsgrenze wie der Current-Zeiger, nicht zwei unabhaengige Luecken.",
            ],
            "vorhandene_r6_originale_geprueft": (
                "r7/run/worker/r6-return-ref/.../evidence/r6-runs/c_teilpub/: echter Entscheid NUR im "
                "finalen run/-Gesamtexport (nicht an den vier Phasen), KEIN Versuchclaim irgendwo im "
                "Paket -- phasengebundene Originale nicht rekonstruierbar, dieser C-Beleg gezielt neu "
                "gefahren (neuer echter Lauf, kein kuenstlicher Claim)."
            ),
            "assertions_bestanden": [
                "Vorher: weder Entscheid noch Claim noch Onboarding/Katalog real existent",
                "Prozess 1 endet ueber os._exit(94) GENAU zwischen Version und State-Zeiger",
                "0001.json traegt exakt den angenommenen Save, kein lesbarer Current-Zeiger (Orphan)",
                "An der Unterbrechung: echter accepted-Entscheid, echter Versuchclaim, volles "
                "completed-Onboarding, voller Katalogkoerper bereits real vorhanden",
                "normaler Retry uebernimmt 0001.json, KEIN 0002.json, 0 neue GM-Calls, Current liest den Save",
                "alle vier Kernkoerper nach Fertigstellung identisch zur Unterbrechung (ausser Current-Zeiger)",
                "letzter identischer Retry: 0 neue GM-Calls, Versionsliste unveraendert, voller Koerpersatz "
                "vor/nach identisch",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL c_teilpub: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK c_teilpub")
    return 0


if __name__ == "__main__":
    sys.exit(main())
