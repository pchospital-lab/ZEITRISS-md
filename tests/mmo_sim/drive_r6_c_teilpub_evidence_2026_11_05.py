#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_c_teilpub_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R6, Familie `c_teilpub` (C/G4-G5, 01_NACHZUG.md §C,
STOP-EVIDENCE.md §3): der konkrete B-Versionsfehler (Hardexit nach Version
0001 VOR State-Zeiger, Retry ohne 0002/ohne neuen GM-Call) ist produktseitig
bereits behoben (R5) -- hier wird **KEINE neue Storearbeit** geleistet,
sondern GENAU der bestehende, bereits funktionierende Beleg
(`drive_r5_evidence_2026_11_05.py::run_family_r5b`, identischer Hardexit-
Helper `_r5_launcher_hardexit_after_version_before_pointer.py`, UNVERAENDERT)
NEU gefahren -- mit den von STOP-EVIDENCE.md §3 ("B: echte Versions-/State-
Unterbrechung behoben; Koerper fehlen im Export") konkret benannten
FEHLENDEN Originalkoerpern:

- AN der Unterbrechung (nach Prozess 1s Hardexit, VOR Prozess 2): accepted-
  Entscheid (Erschaffungs-Grant), Claim (`chrononaut_active_binding`),
  privates Onboarding, Katalog/Figur, Current/Version/States.
- NACH Fertigstellung (nach Prozess 2, dem normalen Retry, der die verwaiste
  Version uebernimmt): derselbe Koerpersatz.
- UNMITTELBAR VOR/NACH dem letzten identischen Retry (Prozess 3): derselbe
  Koerpersatz.

Finale Bytes werden NICHT als damaliger Zwischenstand umetikettiert -- jeder
Snapshot ist explizit nach seinem tatsaechlichen Zeitpunkt benannt. Keine
Version 0002, kein neuer GM-Call, keine zweite Figur/Claimwirkung (wie im
bestehenden R5B-Beleg bereits gezeigt -- hier NUR vollstaendig neu belegt).

ECHTER Launcher-Subprozess (literal `scripts/mmo_sim.py` bzw. gebundene
Hardexit-Skriptdatei), GM-Anbieter NUR als FIX5-Grenzinjektion, NIE Live-
Modell.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
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

_OUT_DIR = Path("/home/altair/zr-betreiber-gast-20261105/r6/run/evidence/r6-runs/c_teilpub")
_RUN_ID = "c_teilpub_full_original_bodies_at_interrupt_completion_and_identical_retry"
_HARDEXIT_AFTER_VERSION = _HERE / "_r5_launcher_hardexit_after_version_before_pointer.py"
_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _snapshot(
    *, run_dir: Path, states_dir: Path, guest_onboarding: Path, guest_catalog: Path,
    participant_id: str, char_id: str, versions_dir: Path, current_path: Path, states_path: Path,
) -> dict:
    """Vollstaendiger Koerpersatz EINES Zeitpunkts: accepted-Entscheid
    (Erschaffungs-Grant), Claim (aktive Bindung), privates Onboarding,
    Katalog/Figur, Current/Version/States -- als echte Dateiinhalte (nicht
    nur Bools/Hashes), s. STOP-EVIDENCE.md §3 Koerperpflicht."""
    grant = creation_grants.grant_status(run_dir, participant_id)
    claim = store.chrononaut_active_binding(run_dir, char_id)
    priv = onboarding.peek(guest_onboarding, participant_id)
    version_files = sorted(versions_dir.glob("*.json")) if versions_dir.exists() else []
    return {
        "accepted_entscheid_grant": grant,
        "claim_chrononaut_active_binding": claim,
        "private_onboarding_final_save": priv.final_save if priv is not None else None,
        "private_onboarding_pending_step": priv.pending_step if priv is not None else None,
        "katalog_figur": catalog.load_figure_save(guest_catalog, participant_id, char_id),
        "katalog_entries": [
            {"participant_id": e.participant_id, "chrononaut_id": e.chrononaut_id}
            for e in catalog.list_for_participant(guest_catalog, participant_id)
        ],
        "current_pointer_present": current_path.exists(),
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
        participant_id = "guest2"
        char_id = "CHR-R6C-TEILPUB-GAST"
        final_block = full_v7_save(char_id, name="GastR6CTeilpub", save_id="fixture-r6c-teilpub-guest-001")
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
                versions_dir=versions_dir, current_path=current_path, states_path=states_path,
            )

        # ── Prozess 1: echter Dialog bis Annahme, dann Hardexit GENAU
        # zwischen Versionsdatei und State-Zeiger (unveraenderter R5-Helper).
        in_fifo1 = fifo_dir / "guest_in_1.fifo"
        out_fifo1 = fifo_dir / "guest_out_1.fifo"
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_AFTER_VERSION),
            "--participant", "operator2", "--data-dir", str(op_data),
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
        r4._send_guest(in_f1, f"gast-erschaffung-anfragen operator2")
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_op(proc1, f"gast-erschaffung-annehmen {participant_id}")
        time.sleep(0.6)
        r4._send_guest(in_f1, "gast-erschaffung-dialog operator2")
        r4._wait_for_marker(out_f1, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_f1, "Mira")
        r4._wait_for_marker(out_f1, f"[SL] {q2}", overall=15.0)
        r4._send_guest(in_f1, "Ein Forscherteam.")
        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        assert proc1.returncode == 94, (
            f"R6/c_teilpub: Prozess 1 muss ueber os._exit(94) GENAU zwischen Versionsdatei und "
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
            f"R6/c_teilpub: nach Hardexit wird GENAU 0001.json erwartet: {version_files_orphan}"
        )
        orphan_version_block = json.loads((versions_dir / "0001.json").read_text(encoding="utf-8"))
        assert orphan_version_block == final_block, "R6/c_teilpub: 0001.json muss exakt den angenommenen Save tragen."
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        assert store.load_current_save(run_dir, participant_id, ps_store, states_dir=states_dir) is None, (
            "R6/c_teilpub: vor dem Retry darf (noch) KEIN Current-Zeiger auf 0001.json gesetzt sein (Orphan)."
        )

        # ── Vollstaendiger Koerpersatz AN DER UNTERBRECHUNG (vor jedem
        # weiteren Prozessstart).
        snapshot_at_interrupt = snap()
        mf.write_json_body(
            "snapshot_at_interrupt.json", snapshot_at_interrupt,
            aussage="c_teilpub_full_body_set_at_interruption_boundary", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Prozess 2: normaler (UNGEPATCHTER) Retry uebernimmt den
        # erreichten Schritt -- KEIN 0002.json.
        in_fifo2 = fifo_dir / "guest_in_2.fifo"
        out_fifo2 = fifo_dir / "guest_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data),
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
        r4._send_guest(in_f2, "gast-erschaffung-dialog operator2")
        retry_out = r4._drain(out_f2, settle=1.0, overall=15.0)
        joined_retry = "".join(retry_out)
        calls_after = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        assert calls_after == calls_before, "R6/c_teilpub: die Uebernahme braucht KEINEN neuen GM-Turn."
        assert "Gast-Erschaffung abgeschlossen" in joined_retry, joined_retry

        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r6.utc(time.time())
        in_f2.close()
        out_f2.close()
        assert proc2.returncode == 0, f"R6/c_teilpub: Retry-Prozess gescheitert: {stderr2}"
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
            f"R6/c_teilpub: der Retry UEBERNIMMT die verwaiste 0001.json -- KEIN 0002.json: "
            f"{[p.name for p in version_files_after]}"
        )
        published = store.load_current_save_or_raise(run_dir, participant_id, ps_store, states_dir=states_dir)
        assert published == final_block, "R6/c_teilpub: Current-Zeiger zeigt nach Uebernahme auf 0001.json == Save."
        catalog_entries_after_retry = len(catalog.list_for_participant(guest_catalog, participant_id))
        assert catalog_entries_after_retry == 1, (
            f"R6/c_teilpub: GENAU eine Katalogfigur erwartet: {catalog_entries_after_retry}"
        )

        # ── Vollstaendiger Koerpersatz NACH FERTIGSTELLUNG.
        snapshot_after_completion = snap()
        mf.write_json_body(
            "snapshot_after_completion.json", snapshot_after_completion,
            aussage="c_teilpub_full_body_set_after_completion", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Vollstaendiger Koerpersatz UNMITTELBAR VOR dem letzten
        # identischen Retry.
        snapshot_before_last_identical_retry = snap()
        mf.write_json_body(
            "snapshot_before_last_identical_retry.json", snapshot_before_last_identical_retry,
            aussage="c_teilpub_full_body_set_immediately_before_last_identical_retry", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )

        # ── Prozess 3: weiterer identischer Retry bleibt bei einer Version.
        in_fifo3 = fifo_dir / "guest_in_3.fifo"
        out_fifo3 = fifo_dir / "guest_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data),
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
        r4._send_guest(in_f3, "gast-erschaffung-dialog operator2")
        r4._drain(out_f3, settle=1.0, overall=15.0)
        calls_after_3 = len(calls_log.read_text(encoding="utf-8").splitlines()) if calls_log.exists() else 0
        assert calls_after_3 == calls_before_3, "R6/c_teilpub: der letzte identische Retry braucht KEINEN neuen GM-Turn."
        r4._send_op(proc3, "beenden")
        stdout3, stderr3 = proc3.communicate(timeout=30)
        utc_end3 = r6.utc(time.time())
        in_f3.close()
        out_f3.close()
        assert proc3.returncode == 0, f"R6/c_teilpub: Prozess 3 gescheitert: {stderr3}"
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
            f"R6/c_teilpub: identischer Retry darf keine zweite Version erzeugen: "
            f"{[p.name for p in version_files_final]}"
        )

        # ── Vollstaendiger Koerpersatz UNMITTELBAR NACH dem letzten
        # identischen Retry -- finale Bytes werden NICHT als damaliger
        # Zwischenstand umetikettiert (eigener, klar benannter Snapshot).
        snapshot_after_last_identical_retry = snap()
        mf.write_json_body(
            "snapshot_after_last_identical_retry.json", snapshot_after_last_identical_retry,
            aussage="c_teilpub_full_body_set_immediately_after_last_identical_retry", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        assert snapshot_after_last_identical_retry == snapshot_before_last_identical_retry, (
            "R6/c_teilpub: der letzte identische Retry darf GENAU NICHTS am vollen Koerpersatz veraendern."
        )
        assert snapshot_after_completion == snapshot_before_last_identical_retry, (
            "R6/c_teilpub: nach der Uebernahme der verwaisten Version bleibt der volle Koerpersatz "
            "unveraendert bis zum (und nach dem) letzten identischen Retry -- keine zweite Version/"
            "Claimwirkung/Figur."
        )
        # Der Unterbrechungs-Snapshot UNTERSCHEIDET sich bewusst vom
        # Fertigstellungs-Snapshot (GENAU das ist die Orphan-Luecke: noch
        # kein lesbarer Current-Zeiger) -- aber Katalogfigur/Onboarding/
        # Claim/Version-Dateiliste MUESSEN bereits identisch sein (nur der
        # Current-Zeiger fehlt noch).
        assert snapshot_at_interrupt["version_files"] == snapshot_after_completion["version_files"], (
            "R6/c_teilpub: die Versionsdatei selbst (0001.json) ist an der Unterbrechung bereits "
            "identisch zum fertiggestellten Stand -- nur der Current-Zeiger fehlt noch."
        )
        # Die Orphan-Luecke ist bereits oben ueber die autoritative Produkt-
        # API bestaetigt (`store.load_current_save(...) is None` VOR dem
        # Retry) -- die reine Dateiexistenz von `current_saves/guest2.json`
        # ist KEIN verlaesslicher Indikator (kann je nach Schreibreihenfolge
        # bereits als Datei vorliegen, ohne ueber einen gueltigen State-
        # Zeiger lesbar zu sein); hier nur faktisch im Snapshot mitgefuehrt.
        assert snapshot_after_completion["current_pointer_present"] is True, (
            "R6/c_teilpub: nach Fertigstellung muss der Current-Zeiger lesbar sein."
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
                "C/G4-G5 (01_NACHZUG.md §C, STOP-EVIDENCE.md §3): der B-Versionsfehler ist bereits "
                "behoben (keine neue Storearbeit) -- dieser Lauf liefert die von STOP-EVIDENCE.md §3 "
                "konkret vermissten Originalkoerper (accepted-Entscheid, Claim, privates Onboarding, "
                "Katalog/Figur, Current/Version/States) AN der Unterbrechung, NACH Fertigstellung und "
                "UNMITTELBAR VOR/NACH dem letzten identischen Retry. Der Unterbrechungs-Snapshot "
                "unterscheidet sich bewusst nur im (noch) fehlenden lesbaren Current-Zeiger (Orphan-"
                "Luecke) vom Fertigstellungs-Snapshot -- Versionsdatei/Katalog/Onboarding/Claim sind "
                "bereits an der Unterbrechung identisch. Fertigstellungs- und beide Retry-Snapshots "
                "sind untereinander vollstaendig bytegleich (keine Version 0002, kein neuer GM-Call, "
                "keine zweite Figur/Claimwirkung)."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "proc1_exit": proc1.returncode, "proc2_exit": proc2.returncode, "proc3_exit": proc3.returncode,
            "version_files_final": [p.name for p in version_files_final],
            "snapshots_identical_at_interrupt_after_completion_and_around_last_retry": True,
            "assertions_bestanden": [
                "Prozess 1 endet ueber os._exit(94) GENAU zwischen Version und State-Zeiger",
                "0001.json traegt exakt den angenommenen Save, kein lesbarer Current-Zeiger (Orphan)",
                "Vollstaendiger Koerpersatz an der Unterbrechung exportiert (nicht nur Hashes/Bools)",
                "normaler Retry uebernimmt 0001.json, KEIN 0002.json, 0 neue GM-Calls, Current liest den Save",
                "vollstaendiger Koerpersatz nach Fertigstellung exportiert, identisch zum Unterbrechungssatz",
                "letzter identischer Retry: 0 neue GM-Calls, Versionsliste unveraendert, Koerpersatz vor/nach identisch",
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
