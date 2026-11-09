#!/usr/bin/env python3
"""
tests/mmo_sim/drive_v_journey_vollendung_2026_11_06.py -- ZR-VOLLENDUNG-
OHNE-LAN-20261106-R1 (02_ABNAHME V3/V4): belegt am ECHTEN ausgelieferten
Launcher (`scripts/mmo_sim.py`, GM NUR als Grenzinjektion
`MMO_SIM_GM_TRANSPORT_DOUBLE`, NIE Live-Modell) die beiden Kernaussagen,
die der neue Produkt-Prosa-/Bedienabgleich dieses Auftrags berührt:

Szene A -- v3_guest_personal_save (V3, trägt auch V1-Gasteinstieg):
  Ein Gast bringt über `--guest-terminal` seine EIGENE gültige Figur mit,
  der Betreiber (ohne eigene Figur) nimmt die Anfrage bewusst an (publiziert
  den Startsave), es wird gespielt, der Abschnitt schließt regulär, und die
  persönliche Endfassung des Gasts ist über den ECHTEN Produktleser
  (`onboarding.peek`) wieder lesbar. Ein unmittelbar folgender identischer
  Tischstart hat KEINE zweite Wirkung (Tisch geschlossen).

Szene B -- v4_stop_before_commit_discard (V4, "Stop gewinnt vor Annahme"):
  Derselbe reale Weg bis zum ersten Spielzug; der Gast bestätigt dort
  `/abbrechen`. Am gebundenen Betreiber-Tisch VOR jedem Abschluss-Entscheid
  ist das ein echter, ENDGÜLTIGER Verwurf (`request_table_stop` -> decision
  'stopped'), KEINE bloße Pause -- genau die Unterscheidung, die die neue
  `_control_help_text("Spielzug")`-Hilfe jetzt ehrlich benennt. Kein Final,
  keine persönliche Publikation.

Die Launcher-/FIFO-/GM-Double-Mechanik ist bytegleich aus der bestehenden
`drive_r4_evidence_2026_11_04.py`-Harness importiert (kein zweiter Admission-/
Transportpfad). Pure Python, nur `assert`, echter Exitcode, kein pytest.
"""
from __future__ import annotations

import json
import subprocess
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

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path("/home/altair/zr-vollendung-20261106/evidence/v-journey")


# ───────────────────────── Szene A: V3 persönlicher Gast-Save ──────────────

def run_scene_v3() -> None:
    out_dir = _OUT_ROOT / "A_v3_guest_personal_save"
    mf = r6.Manifest(out_dir)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo, out_fifo = fifo_dir / "guest_in.fifo", fifo_dir / "guest_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-vollendung-guest"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-vollendung-guest-001")
        guest_current_path = run_dir / "current_saves" / "guest1.json"
        table_id = "local-guest1"
        final_path = run_dir / "completion" / f"{table_id}-section__final.json"

        debrief_save = full_v7_save(char_id, name="Gast-guest1", save_id="fixture-vollendung-guest-002", level=2)
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\n" + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_op(proc, "tisch-anbieten mesaV")
        time.sleep(0.6)
        r4._send_guest(in_f, "tisch-anfragen mesaV")
        after_request = r4._drain(out_f, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaV' gestellt" in l for l in after_request), after_request
        r4._send_op(proc, "tisch-annehmen mesaV guest1")
        time.sleep(0.6)
        assert guest_current_path.exists(), "V3: tisch-annehmen haette den Gast-Startsave publizieren muessen."

        r4._send_op(proc, "tisch-start mesaV")
        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        # '?' am echten Spielzug-Prompt zeigt die neue kontextbewusste Hilfe
        # (3 /abbrechen-Faelle) OHNE Zug-/Modellverbrauch; danach derselbe Prompt.
        r4._send_guest(in_f, "?")
        help_lines = r4._wait_for_marker(out_f, "Betreiber-Tisch", overall=15.0)
        help_joined = "".join(help_lines)
        assert "ENDGUELTIGER Verwurf" in help_joined and "Restabschluss" in help_joined, help_joined
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend.")
        second = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert "Unbekannte Auswahl" not in "".join(second), f"V3: erster Zug fehlgeleitet: {second}"
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich schliesse den Abschnitt ab.")
        # Nach dem Debrief (COMPLETION_MARKER) fragt der Abschluss die
        # freiwillige lokale Notiz ab -- erst danach wird __final.json geschrieben.
        r4._wait_for_marker(out_f, "eigene lokale Notiz", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Abschlussnotiz: Reise erfolgreich.")
        r4._wait_for_path(final_path, overall=25.0)
        finish_tail = r4._drain(out_f, settle=0.6, overall=8.0)

        # identischer Retry-Tischstart (Operator-stdout, NICHT Gast-FIFO):
        # der bereits geschlossene Tisch wird abgelehnt -- KEINE zweite Wirkung.
        r4._send_op(proc, "tisch-start mesaV")
        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_f.close(); out_f.close()
        assert proc.returncode == 0, f"V3: Launcher-Lauf gescheitert: {stderr_text}"
        assert final_path.exists(), "V3: der regulaere Abschluss haette __final.json schreiben muessen."
        assert "geschlossen" in stdout_text, (
            f"V4-Teil: identischer Tischstart nach Abschluss haette 'geschlossen' melden muessen "
            f"(Operator-stdout tail): {stdout_text[-400:]!r}"
        )

        # ECHTER Produktleser: die persönliche Endfassung des Gasts ist wieder lesbar.
        guest_private = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private is not None and guest_private.final_save is not None, (
            "V3: die abgeschlossene Fassung haette ueber den normalen Rueckkanal in die private "
            "Gastablage geschrieben werden muessen (onboarding.peek)."
        )
        reloaded_char = guest_private.final_save["characters"][0]
        assert reloaded_char["id"] == char_id, reloaded_char
        assert reloaded_char["lvl"] == 2, f"V3: die persoenliche Endfassung muss den Fortschritt (lvl 2) tragen: {reloaded_char}"

        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="v3_full_guest_journey_launcher_transcript", run_id="A_v3",
            teilnehmer_figur="guest1", tisch_abschnitt="mesaV/local-guest1-section",
        )
        mf.export_tree(run_dir, "run", aussage="v3_run_dir_after_finish", run_id="A_v3",
                       teilnehmer_figur="guest1", tisch_abschnitt="mesaV/local-guest1-section")
        mf.export_tree(guest_onboarding, "guest_onboarding", aussage="v3_guest_private_after_finish",
                       run_id="A_v3", teilnehmer_figur="guest1")
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="v3_gm_double_calls", run_id="A_v3",
                       teilnehmer_figur="guest1")
        mf.write_json_body("io_transcript.json", {
            "after_request": after_request, "finish_tail": finish_tail,
            "abbrechen_help_at_spielzug": help_joined,
            "retry_closed_in_operator_stdout": "geschlossen" in stdout_text,
            "reloaded_personal_char": {"id": reloaded_char["id"], "lvl": reloaded_char["lvl"]},
        }, aussage="v3_dialog_io_transcript", run_id="A_v3", teilnehmer_figur="guest1")
        mf.write_manifest()
        mf.write_summary({
            "szene": "A_v3_guest_personal_save",
            "aussage": (
                "Gast bringt eigene Figur mit, Betreiber (ohne Figur) nimmt bewusst an und publiziert den "
                "Startsave, regulaerer Abschnittsabschluss, persoenliche Endfassung (lvl 2) ueber "
                "onboarding.peek wieder lesbar; identischer Tischstart danach ohne zweite Wirkung."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "final_written": final_path.exists(),
            "personal_reload_lvl": reloaded_char["lvl"],
        })


# ───────────────────────── Szene B: V4 Stop gewinnt vor Annahme ────────────

def run_scene_v4_stop() -> None:
    out_dir = _OUT_ROOT / "B_v4_stop_before_commit_discard"
    mf = r6.Manifest(out_dir)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo, out_fifo = fifo_dir / "guest_in.fifo", fifo_dir / "guest_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-vollendung-stop"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-vollendung-stop-001")
        table_id = "local-guest1"
        final_path = run_dir / "completion" / f"{table_id}-section__final.json"

        r4._write_gm_double_config(cfg_path, responses=["SL-Antwort auf Anker."], calls_log=calls_log)
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_op(proc, "tisch-anbieten mesaV")
        time.sleep(0.6)
        r4._send_guest(in_f, "tisch-anfragen mesaV")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, "tisch-annehmen mesaV guest1")
        time.sleep(0.6)
        r4._send_op(proc, "tisch-start mesaV")
        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)

        # Gast bestaetigt '/abbrechen' am ersten Spielzug -- VOR jedem Abschluss-
        # Entscheid. Am gebundenen Betreiber-Tisch: echter, endgueltiger Verwurf.
        r4._deliver_guest_turn_answer(in_f, out_f, "/abbrechen")
        abort_lines = r4._wait_for_marker(out_f, "Abschnitt wirklich verworfen", overall=15.0)
        joined = "".join(abort_lines)
        assert "ENDGUELTIG" in joined, joined
        assert "Unbekannte Auswahl" not in joined, f"V4: '/abbrechen' fehlgeleitet: {abort_lines}"

        tail = r4._drain(out_f, settle=0.8, overall=6.0)
        # Nach echtem Verwurf kann der Launcher die Gast-/Betriebssession von
        # selbst beenden -- Exit robust einsammeln, 'beenden' nur best effort.
        try:
            r4._send_op(proc, "beenden")
        except BrokenPipeError:
            pass
        try:
            stdout_text, stderr_text = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_text, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        in_f.close(); out_f.close()
        assert proc.returncode == 0, f"V4: Launcher-Lauf gescheitert (rc={proc.returncode}): {stderr_text}"

        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        assert not final_path.exists(), "V4: ein echter Verwurf vor Commit darf NICHT finalisieren."
        guest_current_path = run_dir / "current_saves" / "guest1.json"
        # Der Gast-Startsave wurde bei Annahme publiziert; der Verwurf des ABSCHNITTS
        # erzeugt keinen neuen Fortschritt/Abschluss (kein Final, kein lvl-Up).
        reloaded = json.loads(guest_current_path.read_text(encoding="utf-8")) if guest_current_path.exists() else None

        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="v4_stop_before_commit_launcher_transcript", run_id="B_v4",
            teilnehmer_figur="guest1", tisch_abschnitt="mesaV/local-guest1-section",
        )
        mf.export_tree(run_dir, "run", aussage="v4_run_dir_after_discard", run_id="B_v4",
                       teilnehmer_figur="guest1", tisch_abschnitt="mesaV/local-guest1-section")
        mf.write_json_body("io_transcript.json", {
            "abort_lines": abort_lines, "tail": tail, "decision": decision,
            "guest_current_char_lvl": (reloaded["characters"][0]["lvl"] if reloaded else None),
        }, aussage="v4_dialog_io_transcript", run_id="B_v4", teilnehmer_figur="guest1")
        mf.write_manifest()
        mf.write_summary({
            "szene": "B_v4_stop_before_commit_discard",
            "aussage": (
                "Am gebundenen Betreiber-Tisch beendet ein am Spielzug bestaetigtes '/abbrechen' VOR "
                "jedem Abschluss-Entscheid den Abschnitt ENDGUELTIG (decision 'stopped'), kein Final, "
                "keine persoenliche Publikation -- genau die Unterscheidung der neuen Spielzug-Hilfe."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "decision": decision.get("decision"),
            "final_written": final_path.exists(),
        })


# ───────────────────────── Szene C: V1 Einstieg + Auffindbarkeit ───────────

def run_scene_v1_entry() -> None:
    out_dir = _OUT_ROOT / "C_v1_entry_and_table_menu"
    mf = r6.Manifest(out_dir)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        write_test_profile(run_dir, max_turns=50)
        # Host-faehige Session (Default) -- das Tisch-Untermenue zeigt die
        # Betreiber-/Hostaktionen [5]-[9] als benannte, auffindbare Optionen.
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "hostA", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        env = r4._clean_env()
        utc_start = r6.utc(time.time())
        result = subprocess.run(
            argv, cwd=str(_REPO_ROOT), env=env,
            input="tisch\n/zurueck\nbeenden\n", capture_output=True, text=True, timeout=30,
        )
        utc_end = r6.utc(time.time())
        out = result.stdout
        assert result.returncode == 0, f"V1: Launcher-Boot gescheitert: {result.stderr}"
        assert "[tisch]" in out, f"V1: Boot-Menue muss den Tisch-Einstieg zeigen: {out[:800]!r}"
        assert "Tisch -- [1] Offene Tische suchen" in out, f"V1: Gast-Tischzeile fehlt: {out[:1200]!r}"
        assert "Betreiber/Host -- [5] Tisch anbieten" in out, (
            f"V1: die auffindbare Betreiber-Tischzeile [5]-[9] fehlt (host_capable): {out!r}"
        )
        assert "Experten-/Hostaliase" not in out, (
            "V1: die alte Sackgassen-Formulierung 'Experten-/Hostaliase' darf nicht mehr erscheinen."
        )
        r6.write_process_result(
            out_dir, "launcher_boot", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=result.returncode,
            stdout_text=result.stdout, stderr_text=result.stderr,
        )
        mf.record_process_files(
            "launcher_boot", aussage="v1_boot_menu_and_findable_operator_table_actions",
            run_id="C_v1", teilnehmer_figur="hostA",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "C_v1_entry_and_table_menu",
            "aussage": (
                "Echter Launcher-Boot (host_capable): Boot-Menue zeigt den [tisch]-Einstieg; das "
                "Tisch-Untermenue macht die Gastzeile [1]-[4] UND die Betreiber-/Hostaktionen [5]-[9] "
                "auffindbar -- keine 'Experten-/Hostaliase'-Sackgasse mehr."
            ),
            "echter_neuer_os_prozess": True,
            "boot_menu_tisch_entry": True,
            "operator_table_actions_findable": True,
        })


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    scenes = [("C_v1_entry", run_scene_v1_entry), ("A_v3", run_scene_v3), ("B_v4_stop", run_scene_v4_stop)]
    failed = 0
    for name, fn in scenes:
        try:
            fn()
            print(f"OK   {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {name}:")
            traceback.print_exc()
    print(f"\n{len(scenes) - failed}/{len(scenes)} Szenen bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
