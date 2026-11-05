#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R5 (02_NACHWEISE_UND_RUECKGABE.md §3): drei neue
Beweisfamilien fuer GENAU die R5-Produktaenderungen (A/B/C), aufgesetzt auf
der ECHTEN Launcher-Harness von `drive_r4_evidence_2026_11_04.py` (literal
`scripts/mmo_sim.py` bzw. gebundene Skriptdateien, kein `-c`-Platzhalter,
GM-Anbieter nur als FIX5-Grenzinjektion, NIE Live-Modell).

- r5a (A / T4A, 01_NACHZUG.md §2, GUEST-OPERATOR.md §3): nach gewonnenem
  Betreiber-Stop sendet der innere Dialog KEINEN dritten Erschaffungsrequest
  mehr (der vom R4-Review geruegte `turn_idx=2`-Request bleibt aus). Die
  bereits offene zweite Antwort wird ehrlich verbucht, der Dialog endet
  terminal 'stopped', keine Publikation.
- r5b (B / T4B, 01_NACHZUG.md §3, GUEST-OPERATOR.md §4, STATIC-CROSSCHECK
  (a)): eine ECHTE Prozessunterbrechung GENAU zwischen Versionsdatei und
  State-Zeiger (gebundener Hardexit) hinterlaesst `0001.json` ohne Zeiger;
  der normale Retry UEBERNIMMT genau diesen Schritt (kein `0002.json`), und
  ein weiterer identischer Retry bleibt bei einer Version.
- r5c (C / G1, 01_NACHZUG.md §4, GUEST-OPERATOR.md §5): die exklusive
  Besitzuebergabe des EINEN Gast-Eingabekanals ist jetzt atomar -- eine
  deterministische Barriere belegt, dass Host-Claim-Setzen und Gast-Check+
  Konsum einander wechselseitig ausschliessen (TOCTOU geschlossen).

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Battle-tested Harness-Helfer der R4-Evidenz wiederverwenden (Import fuehrt
# NICHT main() aus -- __main__-Guard dort). Nur das Ergebnisverzeichnis wird
# auf den R5-Lauf umgehaengt, danach stehen alle `_*`-Helfer bereit.
import drive_r4_evidence_2026_11_04 as r4  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261105/r5/run/results")
r4._RESULTS_ROOT = _RESULTS_ROOT  # Harness-Export-Ziel auf R5 umhaengen
_LAUNCHER = _REPO_ROOT / "scripts" / "mmo_sim.py"
_HARDEXIT_AFTER_VERSION = _HERE / "_r5_launcher_hardexit_after_version_before_pointer.py"
_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _requests_by_turn_idx(run_dir: Path) -> dict:
    out = {}
    req_dir = run_dir / "requests"
    if not req_dir.is_dir():
        return out
    for p in sorted(req_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ti = data.get("turn_idx")
        out.setdefault(ti, []).append((p.name, data))
    return out


# ───────────────────────── r5a: A / T4A -- kein dritter Request ────────────

def run_family_r5a() -> None:
    szene = "r5a"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"
        signal_path = root / "stop_signal.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-R5A-GAST"
        final_block = full_v7_save(char_id, name="GastR5A", save_id="fixture-r5a-guest-001")
        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr praegender Ursprung?"
        final_content = "```json\n" + json.dumps(final_block, ensure_ascii=False) + "\n```"
        # Drei Antworten stehen bereit -- die DRITTE (final_content) DARF mit
        # dem R5-Fix NIE abgerufen werden (Stop blockiert den dritten Request).
        r4._write_gm_double_config(
            cfg_path, responses=[q1, q2, final_content], calls_log=calls_log,
            stop={
                "after_call": 2, "kind": "creation", "signal_file": str(signal_path),
                "run_dir": str(run_dir), "operator_id": "operator1", "guest_id": "guest1", "generation": 1,
            },
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r4._utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, "gast-erschaffung-anfragen operator1")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, "gast-erschaffung-annehmen guest1")
        time.sleep(0.6)
        grant_before = creation_grants.grant_status(run_dir, "guest1")
        assert grant_before["status"] == "approved" and grant_before["generation"] == 1, grant_before

        r4._send_guest(in_f, "gast-erschaffung-dialog operator1")
        r4._wait_for_marker(out_f, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_f, "Elena")
        # Double blockiert im Q2-Aufruf, signalisiert -> Betreiber tippt den
        # ECHTEN Stop-Befehl. Q2 kommt spaet, wird beantwortet und verbucht.
        r4._wait_for_path(signal_path, overall=15.0)
        r4._send_op(proc, "gast-erschaffung-stop guest1")
        r4._wait_for_marker(out_f, f"[SL] {q2}", overall=15.0)
        r4._send_guest(in_f, "Eine verlorene Chronoflotte.")
        final_tail = r4._drain(out_f, settle=1.0, overall=15.0)
        joined = "".join(final_tail)

        # R5-Kernaussage: der Dialog endet am Loop-Top-Stopcheck (NEUER Text
        # aus core.creation_service), NICHT erst am Finish -- und es gibt
        # keinen dritten Request.
        assert "ein adressierter Betreiber-Stop hat den gemeinsamen Entscheid" in joined, joined
        assert "kein weiterer SL-/Korrektur-Request" in joined, joined

        decision = admission.read_table_decision(
            run_dir, creation_grants._creation_decision_id("operator1", "guest1", 1),
        )
        assert decision is not None and decision.get("decision") == "stopped", decision

        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 2, (
            f"R5A: nach gewonnenem Stop darf KEIN dritter Erschaffungsrequest gesendet werden "
            f"(erwartet 2 GM-Calls, tatsaechlich {len(gm_calls)}): {gm_calls}"
        )
        by_turn = _requests_by_turn_idx(run_dir)
        assert 2 not in by_turn, (
            f"R5A: kein Request mit turn_idx=2 erwartet (der geruegte dritte Request): {sorted(by_turn)}"
        )
        # Zweite Antwort ehrlich verbucht: turn_idx=1-Request existiert und ist accounted.
        assert 1 in by_turn and any(d.get("state") == "accounted" for _n, d in by_turn[1]), by_turn.get(1)
        # Keine Publikation.
        assert not (run_dir / "current_saves" / "guest1.json").exists(), "R5A: kein Current-Write nach Stop."
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        assert catalog.list_for_participant(guest_catalog, "guest1") == [], "R5A: keine Katalogfigur nach Stop."

        r4._send_op(proc, "beenden")
        stdout, stderr = proc.communicate(timeout=30)
        utc_end = r4._utc(time.time())
        in_f.close()
        out_f.close()
        r4._record_background_run(
            szene, "r5a_stop_blocks_third_request", argv, str(_REPO_ROOT),
            utc_start, utc_end, proc.returncode, stdout, stderr,
        )
        assert proc.returncode == 0, f"R5A: Launcher-Lauf gescheitert: {stderr}"

        r4._export_tree(szene, run_dir, "r5a_run")
        r4._export_file(szene, calls_log, "r5a_gm_calls.jsonl")
        r4._write_export_json(szene, "r5a_io_transcript.json", {"final_tail": joined})
        r4._write_export_json(szene, "r5a_summary.json", {
            "gm_call_count": len(gm_calls), "request_turn_idxs": sorted(k for k in by_turn if k is not None),
            "decision": decision, "current_write": False, "catalog_entries": 0,
            "note": "A/T4A: Loop-Top-Stopcheck (core.creation_service) beendet den Dialog terminal VOR dem "
                    "dritten Request; die spaete Q2-Antwort ist als turn_idx=1/accounted verbucht.",
        })


# ───────────────────────── r5b: B / T4B -- verwaiste Version uebernehmen ───

def run_family_r5b() -> None:
    szene = "r5b"
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
        char_id = "CHR-R5B-GAST"
        final_block = full_v7_save(char_id, name="GastR5B", save_id="fixture-r5b-guest-001")
        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr Ursprung?"
        final_content = "```json\n" + json.dumps(final_block, ensure_ascii=False) + "\n```"
        r4._write_gm_double_config(cfg_path, responses=[q1, q2, final_content], calls_log=calls_log)
        env = r4._gm_double_env(cfg_path)

        guest_onboarding = op_data / "guests" / "guest2" / "onboarding"
        guest_catalog = op_data / "guests" / "guest2" / "catalog"
        onboarding_key = creation_grants.guest_onboarding_key("guest2", 1)
        versions_dir = run_dir / "current_saves" / "guest2__versions"
        current_path = run_dir / "current_saves" / "guest2.json"

        # ---- Prozess 1: echter Dialog bis Annahme, dann Hardexit GENAU
        # zwischen Versionsdatei und State-Zeiger (gebundener Hardexit-Launcher).
        in_fifo1 = fifo_dir / "guest_in_1.fifo"
        out_fifo1 = fifo_dir / "guest_out_1.fifo"
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_AFTER_VERSION),
            "--participant", "operator2", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest2:{in_fifo1}:{out_fifo1}",
        ]
        utc_start1 = r4._utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r4._open_guest_fifo_pair(in_fifo1, out_fifo1)
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_guest(in_f1, "gast-erschaffung-anfragen operator2")
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_op(proc1, "gast-erschaffung-annehmen guest2")
        time.sleep(0.6)
        r4._send_guest(in_f1, "gast-erschaffung-dialog operator2")
        r4._wait_for_marker(out_f1, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_f1, "Mira")
        r4._wait_for_marker(out_f1, f"[SL] {q2}", overall=15.0)
        r4._send_guest(in_f1, "Ein Forscherteam.")
        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r4._utc(time.time())
        in_f1.close()
        out_f1.close()
        r4._record_background_run(
            szene, "r5b_proc1_hardexit_after_version_before_pointer", argv1, str(_REPO_ROOT),
            utc_start1, utc_end1, proc1.returncode, stdout1, stderr1,
        )
        assert proc1.returncode == 94, (
            f"R5B: Prozess 1 muss ueber os._exit(94) GENAU zwischen Versionsdatei und State-Zeiger "
            f"enden -- rc={proc1.returncode} stderr={stderr1!r}"
        )
        # Orphan-Zwischenzustand: 0001.json existiert, aber KEIN Current-Zeiger.
        version_files_orphan = sorted(versions_dir.glob("*.json")) if versions_dir.exists() else []
        assert [p.name for p in version_files_orphan] == ["0001.json"], (
            f"R5B: nach Hardexit wird GENAU 0001.json erwartet: {version_files_orphan}"
        )
        orphan_version_block = json.loads((versions_dir / "0001.json").read_text(encoding="utf-8"))
        assert orphan_version_block == final_block, "R5B: 0001.json muss exakt den angenommenen Save tragen."
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        # Kein Current-Zeiger -> load_current_save liefert None (genau die Luecke).
        assert store.load_current_save(run_dir, "guest2", ps_store, states_dir=states_dir) is None, (
            "R5B: vor dem Retry darf (noch) KEIN Current-Zeiger auf 0001.json gesetzt sein (Orphan)."
        )
        sha_orphan_version = r4._sha256(versions_dir / "0001.json")
        sha_orphan_current = r4._sha256(current_path) if current_path.exists() else None

        # ---- Prozess 2: normaler (UNGEPATCHTER) Retry uebernimmt den
        # erreichten Schritt -- KEIN 0002.json.
        in_fifo2 = fifo_dir / "guest_in_2.fifo"
        out_fifo2 = fifo_dir / "guest_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest2:{in_fifo2}:{out_fifo2}",
        ]
        utc_start2 = r4._utc(time.time())
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
        assert calls_after == calls_before, "R5B: die Uebernahme braucht KEINEN neuen GM-Turn."
        assert "Gast-Erschaffung abgeschlossen" in joined_retry, joined_retry

        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r4._utc(time.time())
        in_f2.close()
        out_f2.close()
        r4._record_background_run(
            szene, "r5b_proc2_normal_retry_adopts_orphan_version", argv2, str(_REPO_ROOT),
            utc_start2, utc_end2, proc2.returncode, stdout2, stderr2,
        )
        assert proc2.returncode == 0, f"R5B: Retry-Prozess gescheitert: {stderr2}"

        version_files_after = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_after] == ["0001.json"], (
            f"R5B/B: der Retry UEBERNIMMT die verwaiste 0001.json -- KEIN 0002.json erwartet: "
            f"{[p.name for p in version_files_after]}"
        )
        assert r4._sha256(versions_dir / "0001.json") == sha_orphan_version, (
            "R5B: die uebernommene Version 0001.json wurde nicht veraendert."
        )
        published = store.load_current_save_or_raise(run_dir, "guest2", ps_store, states_dir=states_dir)
        assert published == final_block, "R5B: nach Uebernahme zeigt der Current-Zeiger auf 0001.json == Save."
        catalog_entries = len(catalog.list_for_participant(guest_catalog, "guest2"))
        assert catalog_entries == 1, f"R5B: GENAU eine Katalogfigur erwartet: {catalog_entries}"

        # ---- Prozess 3: weiterer identischer Retry bleibt bei einer Version.
        in_fifo3 = fifo_dir / "guest_in_3.fifo"
        out_fifo3 = fifo_dir / "guest_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest2:{in_fifo3}:{out_fifo3}",
        ]
        utc_start3 = r4._utc(time.time())
        proc3 = subprocess.Popen(
            argv3, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f3, out_f3 = r4._open_guest_fifo_pair(in_fifo3, out_fifo3)
        r4._drain(out_f3, settle=0.6, overall=10.0)
        r4._send_guest(in_f3, "gast-erschaffung-dialog operator2")
        r4._drain(out_f3, settle=1.0, overall=15.0)
        r4._send_op(proc3, "beenden")
        stdout3, stderr3 = proc3.communicate(timeout=30)
        utc_end3 = r4._utc(time.time())
        in_f3.close()
        out_f3.close()
        r4._record_background_run(
            szene, "r5b_proc3_identical_retry_version_count_stays_1", argv3, str(_REPO_ROOT),
            utc_start3, utc_end3, proc3.returncode, stdout3, stderr3,
        )
        assert proc3.returncode == 0, f"R5B: Prozess 3 gescheitert: {stderr3}"
        version_files_final = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_final] == ["0001.json"], (
            f"R5B: identischer Retry darf keine zweite Version erzeugen: "
            f"{[p.name for p in version_files_final]}"
        )

        r4._export_tree(szene, run_dir, "r5b_run")
        r4._export_tree(szene, guest_catalog, "r5b_guest_catalog")
        r4._export_file(szene, calls_log, "r5b_gm_calls.jsonl")
        r4._write_export_json(szene, "r5b_inventory.json", {
            "after_hardexit": {
                "version_files": [p.name for p in version_files_orphan],
                "current_pointer_present": False,
                "orphan_version_sha256": sha_orphan_version,
                "orphan_direct_current_sha256": sha_orphan_current,
            },
            "after_retry_adopt": {
                "version_files": [p.name for p in version_files_after],
                "catalog_entries": catalog_entries,
                "new_gm_calls": calls_after - calls_before,
            },
            "after_identical_retry": {"version_files": [p.name for p in version_files_final]},
            "note": "B/T4B: Prozess 1 bricht real zwischen Versionsdatei (0001.json) und State-Zeiger ab "
                    "(gebundener Monkeypatch auf core.store._write_current_save_version, kein veraenderter "
                    "Produktpfad). Der normale Retry uebernimmt genau diesen Schritt (publish_current_save "
                    "adoptiert die inhaltsgleiche verwaiste Version) -- kein 0002.json, 0 neue GM-Calls.",
        })


# ───────────────────────── r5c: C / G1 -- exklusiver Leser ─────────────────

def run_family_r5c() -> None:
    szene = "r5c"
    utc_start = r4._utc(time.time())
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # Minimale, als Gast-Terminal registrierte Session mit kontrollierbarem
        # Leser: `_input` blockiert an einem Event und protokolliert den
        # tatsaechlichen Konsum; `input_ready_fn` meldet Bereitschaft.
        consumed: list[str] = []
        enter_input = threading.Event()   # Reader hat `_input` betreten (haelt den Lock)
        release_input = threading.Event()  # Test gibt den eigentlichen Konsum frei
        ready_flag = {"v": True}

        def fake_input(prompt: str) -> str:
            enter_input.set()
            release_input.wait(5.0)
            consumed.append("guest")
            return "menue-zeile"

        def fake_ready(timeout: float) -> bool:
            # kurze Backoff-Treue zur echten Kadenz
            if not ready_flag["v"]:
                time.sleep(min(timeout, 0.05))
                return False
            return True

        sess = TuiSession(
            root / "onb", root / "cat", "guest1",
            input_fn=fake_input, print_fn=lambda s: None,
            host_capable=False, input_ready_fn=fake_ready,
        )
        sess._is_registered_guest_terminal = True

        # ===== Teil 1: Gast haelt den Lock (mitten im Konsum) -> ein Host-
        # Claim-Setzen (das denselben Lock braucht) kann NICHT dazwischen. ====
        result_box: dict = {}

        def guest_reader():
            result_box["line"] = sess._readline_guest_menu("menu> ")

        t = threading.Thread(target=guest_reader, daemon=True)
        t.start()
        assert enter_input.wait(5.0), "R5C: Gast-Leser hat `_input` nicht erreicht."
        # Der Gast haelt jetzt `_terminal_read_lock` (Check+Konsum sind atomar
        # darunter). Ein Host-Claim-Setzen wuerde den Lock brauchen -> blockiert:
        host_lock_free_during_consume = sess._terminal_read_lock.acquire(blocking=False)
        assert host_lock_free_during_consume is False, (
            "R5C: waehrend der Gast den einen Konsum unter dem Lock haelt, darf der Host den Lock "
            "(fuer das Claim-Setzen) NICHT erwerben -- sonst waere die Uebergabe nicht exklusiv."
        )
        release_input.set()
        t.join(5.0)
        assert not t.is_alive() and result_box.get("line") == "menue-zeile", result_box
        assert consumed == ["guest"], f"R5C: genau EIN Konsum durch den Gast erwartet: {consumed}"
        # Jetzt ist der Lock wieder frei:
        assert sess._terminal_read_lock.acquire(blocking=False) is True
        sess._terminal_read_lock.release()

        # ===== Teil 2: Host-Claim gesetzt -> Gast-Leser PARKT (konsumiert
        # NICHT), bis der Claim frei ist; dann genau EIN Konsum. ===============
        consumed.clear()
        enter_input.clear()
        release_input.clear()
        sess._host_terminal_claimed.set()  # Host beansprucht das Terminal
        parked_box: dict = {}

        def guest_reader2():
            parked_box["line"] = sess._readline_guest_menu("menu> ")

        t2 = threading.Thread(target=guest_reader2, daemon=True)
        t2.start()
        # Trotz bereitstehender Zeile darf der Gast waehrend des Claims NICHT
        # in `_input` gelangen (er parkt am Claim-Check oben im Loop).
        assert not enter_input.wait(1.0), (
            "R5C: bei gesetztem Host-Claim darf der Gast-Leser nicht konsumieren (er muss parken)."
        )
        assert not consumed, f"R5C: kein Gast-Konsum bei gesetztem Claim: {consumed}"
        # Claim freigeben -> Gast erreicht `_input`, dann freigeben.
        sess._host_terminal_claimed.clear()
        assert enter_input.wait(5.0), "R5C: nach Claim-Freigabe muss der Gast-Leser `_input` erreichen."
        release_input.set()
        t2.join(5.0)
        assert not t2.is_alive() and parked_box.get("line") == "menue-zeile", parked_box
        assert consumed == ["guest"], f"R5C: nach Claim-Freigabe genau EIN Konsum: {consumed}"

    utc_end = r4._utc(time.time())
    r4._MANIFEST["runs"].append({
        "szene": szene, "label": "r5c_exclusive_reader_barrier", "argv": [sys.executable, "-B", __file__],
        "cwd": str(_REPO_ROOT), "utc_start": utc_start, "utc_end": utc_end, "exit": 0,
        "stdout_path": None, "stderr_path": None,
        "note": "C/G1: in-process deterministische Barriere auf dem ECHTEN TuiSession._readline_guest_menu + "
                "_terminal_read_lock. Teil 1: Host-Claim-Lock blockiert waehrend Gast-Konsum. Teil 2: "
                "gesetzter Claim laesst den Gast parken (0 Konsum), erst nach Freigabe genau 1 Konsum.",
    })
    r4._write_export_json(szene, "r5c_summary.json", {
        "part1_host_claim_lock_blocked_during_guest_consume": True,
        "part2_guest_parks_while_claim_set_then_single_consume": True,
        "note": "TOCTOU zwischen zweitem is_set()-Check und _readline geschlossen: Check+Konsum laufen "
                "atomar unter _terminal_read_lock, das Host-Claim-Setzen braucht denselben Lock.",
    })


def main() -> int:
    import shutil
    if _RESULTS_ROOT.exists():
        shutil.rmtree(_RESULTS_ROOT)
    _RESULTS_ROOT.mkdir(parents=True)
    r4._MANIFEST["files"] = []
    r4._MANIFEST["runs"] = []
    families = [("r5a", run_family_r5a), ("r5b", run_family_r5b), ("r5c", run_family_r5c)]
    failed = 0
    for name, fn in families:
        try:
            fn()
            print(f"OK   familie_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL familie_{name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            import traceback
            print(f"ERROR familie_{name}: {e}\n{traceback.format_exc()}")
    (_RESULTS_ROOT / "MANIFEST.json").write_text(
        json.dumps(r4._MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"\n{'ALLE R5-FAMILIEN OK' if failed == 0 else str(failed) + ' FAMILIE(N) FEHLGESCHLAGEN'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
