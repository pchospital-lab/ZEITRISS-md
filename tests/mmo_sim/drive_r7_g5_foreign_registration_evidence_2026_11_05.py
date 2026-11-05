#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r7_g5_foreign_registration_evidence_2026_11_05.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R7, Familie `g5_foreign_registration`
(G5, 01_NACHZUG.md §1, STOP-EVIDENCE.md §3.2/§3.3, 02_NACHWEISE_UND_
RUECKGABE.md §1 "G5 / bestehender B-Fremdfall"): belegt den von R6
STOP-EVIDENCE.md §3 beschriebenen, bisher UEBERSPRUNGENEN
Fremdzuordnungsschutz der neuen R6-`noop_identical`-Hostprojektion.

Der R7-Produktfix (bereits committet, `e34ee6a7`, NICHT Teil dieses
Treibers) stellt in `mmo_sim/ui/tui.py:_decide_participant_save_intake`
sicher, dass `catalog.find_registration(catalog_dir, preview.char_id)`
(`tui.py:419-427`) UNABHAENGIG vom `known_char_ids`-Gate laeuft -- der
Fremdcheck greift jetzt auch dann, wenn der GEMEINSAME Gast-Current
dieselbe Char-ID bereits "bekannt" gemacht hat (`tui.py:385-391` ergaenzt
`baseline_char_id` in `known_char_ids`, VOR dem Fremdcheck). Vorher haette
der R6-`noop_identical`-Hostprojektions-Write (`tui.py:_cmd_table_accept`,
No-op-Zweig ca. `5319-5345`, Schreibhelfer `catalog.register`/`store_
figure_save` in `catalog.py:47-56,126-137`) eine bereits einem ANDEREN
Teilnehmer zugeordnete Figur zusaetzlich fuer den Gast registriert.

Ablauf (zwei Teilnehmer IM SELBEN Launcher-Prozess, `--guest-terminal`
`action="append"` erlaubt mehrere Gastanschluesse):

1. Fixture-Setup (VOR Prozessstart, direkt ueber die vom Produkt selbst
   genutzten Katalogfunktionen `catalog.register`/`catalog.store_figure_
   save` -- KEINE neue Schreibsemantik, reine Vorbedingung): Char-ID `C`
   ist im HOSTKATALOG bereits Teilnehmer `other` zugeordnet, OHNE aktive
   Bindung/offenen Abschluss/Tischlock (genau der in STOP-EVIDENCE.md §3.2
   beschriebene Ausgangsfall).
2. `guest1` importiert ueber den NORMALEN privaten Terminalweg (`i`) eine
   VOLLSTAENDIG eigene gueltige Figur MIT DERSELBEN Char-ID `C` (getrennter
   eigener Gastkatalog, s. STOP-EVIDENCE.md §3.2 Punkt 1) -- publiziert
   dabei den gemeinsamen Current (macht `C` fuer die Hostentscheidung
   "bekannt").
3. `guest1` fragt einen Tisch an, der Betreiber versucht `tisch-annehmen`
   -- am gefixten Head MUSS die Hostaufnahme JETZT VOR Roster/
   Hostprojektion halten: Anfrage bleibt offen (pending), KEIN Roster-
   Write, KEINE Host-Figur-/Onboarding-/Katalogprojektion fuer `guest1`,
   `other`/`C`-Koerper UNVERAENDERT.
4. Gegenprobe/Erhaltung (`guest2`, eigene Char-ID `D`, NIE irgendwo
   registriert): derselbe Ablauf bleibt fuer eine NICHT fremd registrierte
   ID funktionsfaehig -- Aufnahme gelingt, R6-Fix-B-Hostprojektion wird
   hergestellt (identisch zu `drive_r6_b_import_evidence_2026_11_05.py`).

ECHTER Launcher-Subprozess (literal `scripts/mmo_sim.py`), GM-Anbieter NUR
als FIX5-Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`), NIE Live-Modell --
hier sogar OHNE jeden GM-Call (die Kernaussage liegt vollstaendig an der
Admission-/Katalogebene, kein Rundenzug noetig).

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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path(os.environ.get(
    "R7_OUT_DIR",
    "/home/altair/zr-betreiber-gast-20261105/r7/run/evidence/r7-runs/g5_foreign_registration",
))
_RUN_ID = "g5_foreign_registration_protected_before_admission_write_plus_preserved_conflict_free_b"


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_1, out_fifo_1 = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        in_fifo_2, out_fifo_2 = fifo_dir / "guest2_in.fifo", fifo_dir / "guest2_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        host_onboarding = op_data / "onboarding"
        host_catalog = op_data / "catalog"
        guest1_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest1_catalog = op_data / "guests" / "guest1" / "catalog"
        guest2_onboarding = op_data / "guests" / "guest2" / "onboarding"
        guest2_catalog = op_data / "guests" / "guest2" / "catalog"

        # ── Fixture-Setup: `other`/`C` ist bereits im HOSTKATALOG
        # registriert, OHNE aktive Bindung/offenen Abschluss/Tischlock --
        # dieselben Produktfunktionen (`catalog.register`/`store_figure_
        # save`), die auch der echte Importpfad fuer eine erfolgreiche
        # Registrierung benutzt (`tui.py:_write_participant_save_intake`,
        # `catalog.py:47-56,126-137`). Reine Vorbedingung, KEIN Produktlauf.
        foreign_char_id = "C"
        other_block = full_v7_save(foreign_char_id, name="OtherHostFigure", save_id="fixture-r7g5-other-001")
        catalog.store_figure_save(host_catalog, "other", foreign_char_id, other_block)
        catalog.register(host_catalog, catalog.CatalogEntry(
            participant_id="other", chrononaut_id=foreign_char_id, persona_key="other",
        ))
        other_catalog_path = host_catalog / "catalog__other.json"
        other_figure_path = host_catalog / "figures" / f"other__{foreign_char_id}.json"
        assert other_catalog_path.exists() and other_figure_path.exists(), (
            "R7/g5: Fixture-Vorbedingung (other/C im Hostkatalog) nicht hergestellt."
        )
        sha_other_catalog_before = r6.sha256_of(other_catalog_path)
        sha_other_figure_before = r6.sha256_of(other_figure_path)

        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (G5/R7, unbenutzt -- kein Rundenzug)."],
            calls_log=calls_log, stop=None,
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_1}:{out_fifo_1}",
            "--guest-terminal", f"guest2:{in_fifo_2}:{out_fifo_2}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r4._open_guest_fifo_pair(in_fifo_1, out_fifo_1)
        in_f2, out_f2 = r4._open_guest_fifo_pair(in_fifo_2, out_fifo_2)
        initial_guest1 = r4._drain(out_f1, settle=0.6, overall=10.0)
        initial_guest2 = r4._drain(out_f2, settle=0.6, overall=10.0)
        assert initial_guest1 and initial_guest2, "R7/g5: beide Gast-Terminals muessen Startbanner senden."

        # ── Konflikt-Zweig: guest1 importiert privat dieselbe Char-ID `C`
        # (eigener, getrennter Katalog -- der Hostkatalog mit other/C ist
        # dort NICHT sichtbar, STOP-EVIDENCE.md §3.2 Punkt 1).
        guest1_char_id = foreign_char_id
        guest1_own_block = full_v7_save(
            guest1_char_id, name="GastR7G5Konflikt", save_id="fixture-r7g5-guest1-001",
        )
        guest1_own_block_json = json.dumps(guest1_own_block, ensure_ascii=False)

        r4._send_guest(in_f1, "i")
        r4._wait_for_marker(out_f1, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f1, guest1_own_block_json)
        r4._send_guest(in_f1, "ENDE")
        preview_lines_1 = r4._wait_for_marker(out_f1, f"char_id={guest1_char_id}", overall=20.0)
        assert "WARNUNG" not in "".join(preview_lines_1), preview_lines_1
        r4._send_guest(in_f1, "j")
        accept_lines_1 = r4._wait_for_marker(out_f1, "Uebernahme abgeschlossen", overall=20.0)
        assert f"action=register_new char_id={guest1_char_id}" in "".join(accept_lines_1), accept_lines_1
        r4._drain(out_f1, settle=0.6, overall=5.0)

        guest1_current_path = run_dir / "current_saves" / "guest1.json"
        assert guest1_current_path.exists(), (
            "R7/g5: der normale private Import muss den Save als GEMEINSAMEN Current publizieren "
            "(macht char_id=C fuer die Hostentscheidung 'bekannt')."
        )
        guest1_private_figure_path = guest1_catalog / "figures" / f"guest1__{guest1_char_id}.json"
        assert guest1_private_figure_path.exists(), "R7/g5: private Gastablage (guest1) fehlt nach Import."

        r4._send_op(proc, "tisch-anbieten mesaG5Konflikt")
        time.sleep(0.6)
        r4._send_guest(in_f1, "tisch-anfragen mesaG5Konflikt")
        request_lines_1 = r4._drain(out_f1, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaG5Konflikt' gestellt" in l for l in request_lines_1), request_lines_1

        roster_before_accept = table_admission.roster(run_dir, "mesaG5Konflikt")
        assert "guest1" in roster_before_accept["requests"] and "guest1" not in roster_before_accept["roster"], (
            f"R7/g5: VORHER muss die Anfrage von guest1 offen (pending) sein: {roster_before_accept}"
        )
        host_projection_guest1_before = onboarding.peek(host_onboarding, "guest1")
        assert host_projection_guest1_before is None, (
            f"R7/g5: VORHER darf keine Hostprojektion fuer guest1 existieren: {host_projection_guest1_before}"
        )

        # ── Die eigentliche Produktentscheidung: der Betreiber versucht,
        # die Anfrage anzunehmen -- die (gefixte) Host-Intakeentscheidung
        # MUSS den Fremdkonflikt (other/C) jetzt VOR jedem Roster-/
        # Hostprojektionswrite erkennen, AUCH WENN der gemeinsame Current
        # char_id=C bereits als "bekannt" fuehrt.
        r4._send_op(proc, "tisch-annehmen mesaG5Konflikt guest1")
        time.sleep(0.8)

        roster_after_reject = table_admission.roster(run_dir, "mesaG5Konflikt")
        assert "guest1" not in roster_after_reject["roster"], (
            f"R7/g5: guest1 darf NICHT ins Roster aufgenommen werden (Fremdkonflikt): {roster_after_reject}"
        )
        assert "guest1" in roster_after_reject["requests"], (
            f"R7/g5: die Anfrage von guest1 muss OFFEN (pending) bleiben: {roster_after_reject}"
        )
        host_projection_guest1_after = onboarding.peek(host_onboarding, "guest1")
        assert host_projection_guest1_after is None, (
            f"R7/g5: KEINE Hostprojektion fuer guest1 nach dem abgelehnten Annahmeversuch: "
            f"{host_projection_guest1_after}"
        )
        host_catalog_entries_guest1 = catalog.list_for_participant(host_catalog, "guest1")
        assert host_catalog_entries_guest1 == [], (
            f"R7/g5: KEINE Host-Katalogregistrierung fuer guest1 (keine zusaetzliche Gast-"
            f"Hostregistrierung derselben fremden ID): {host_catalog_entries_guest1}"
        )
        # Fremde Koerper (other/C) bleiben BYTE-UNVERAENDERT.
        assert r6.sha256_of(other_catalog_path) == sha_other_catalog_before, (
            "R7/g5: other/C-Katalogdatei darf durch den abgelehnten Annahmeversuch NICHT veraendert werden."
        )
        assert r6.sha256_of(other_figure_path) == sha_other_figure_before, (
            "R7/g5: other/C-Figurdatei darf durch den abgelehnten Annahmeversuch NICHT veraendert werden."
        )
        # Der private Gastimport selbst bleibt unangetastet (kein
        # rueckwirkendes Zurueckrollen).
        guest1_catalog_entries = catalog.list_for_participant(guest1_catalog, "guest1")
        assert len(guest1_catalog_entries) == 1 and guest1_catalog_entries[0].chrononaut_id == guest1_char_id, (
            f"R7/g5: der private Gastimport (eigener Katalog) bleibt unveraendert erhalten: "
            f"{guest1_catalog_entries}"
        )

        reject_lines = r4._drain(out_f1, settle=0.6, overall=5.0)

        # ── Gegenprobe/Erhaltung: guest2 mit einer NIE fremd registrierten
        # Char-ID `D` -- derselbe Ablauf bleibt funktionsfaehig (R6-Fix-B,
        # konfliktfreier B-Normalweg).
        guest2_char_id = "D"
        guest2_own_block = full_v7_save(
            guest2_char_id, name="GastR7G5Kontrolle", save_id="fixture-r7g5-guest2-001",
        )
        guest2_own_block_json = json.dumps(guest2_own_block, ensure_ascii=False)

        host_projection_guest2_before = onboarding.peek(host_onboarding, "guest2")
        assert host_projection_guest2_before is None, (
            f"R7/g5: VORHER darf keine Hostprojektion fuer guest2 existieren: {host_projection_guest2_before}"
        )

        r4._send_guest(in_f2, "i")
        r4._wait_for_marker(out_f2, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f2, guest2_own_block_json)
        r4._send_guest(in_f2, "ENDE")
        preview_lines_2 = r4._wait_for_marker(out_f2, f"char_id={guest2_char_id}", overall=20.0)
        assert "WARNUNG" not in "".join(preview_lines_2), preview_lines_2
        r4._send_guest(in_f2, "j")
        accept_lines_2 = r4._wait_for_marker(out_f2, "Uebernahme abgeschlossen", overall=20.0)
        assert f"action=register_new char_id={guest2_char_id}" in "".join(accept_lines_2), accept_lines_2
        r4._drain(out_f2, settle=0.6, overall=5.0)

        r4._send_op(proc, "tisch-anbieten mesaG5Kontrolle")
        time.sleep(0.6)
        r4._send_guest(in_f2, "tisch-anfragen mesaG5Kontrolle")
        request_lines_2 = r4._drain(out_f2, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaG5Kontrolle' gestellt" in l for l in request_lines_2), request_lines_2

        r4._send_op(proc, "tisch-annehmen mesaG5Kontrolle guest2")
        time.sleep(0.8)

        roster_after_accept_control = table_admission.roster(run_dir, "mesaG5Kontrolle")
        assert "guest2" in roster_after_accept_control["roster"], (
            f"R7/g5: die konfliktfreie B-Annahme (guest2) muss weiterhin gelingen: {roster_after_accept_control}"
        )
        host_projection_guest2_after = onboarding.peek(host_onboarding, "guest2")
        assert host_projection_guest2_after is not None and host_projection_guest2_after.final_save is not None, (
            "R7/g5: die R6-Fix-B-Hostprojektion fuer guest2 muss hergestellt werden (konfliktfrei)."
        )
        host_catalog_entries_guest2 = catalog.list_for_participant(host_catalog, "guest2")
        assert len(host_catalog_entries_guest2) == 1 and host_catalog_entries_guest2[0].chrononaut_id == guest2_char_id, (
            f"R7/g5: GENAU EIN Host-Katalogeintrag fuer guest2 nach der Annahme erwartet: "
            f"{host_catalog_entries_guest2}"
        )
        accept_control_lines = r4._drain(out_f2, settle=0.6, overall=5.0)

        # Kein Rundenzug/Abschnitt offen (weder guest1 noch guest2 sind in
        # einer laufenden Runde) -- regulaerer Abschluss ueber den echten
        # Betreiberbefehl statt SIGTERM (ehrlicher Exitcode 0 statt
        # Signal-Exitcode, da hier tatsaechlich nichts offen bleibt).
        r4._send_op(proc, "beenden")
        try:
            stdout_text, stderr_text = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_text, stderr_text = proc.communicate(timeout=15)
        utc_end = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        in_f2.close()
        out_f2.close()

        assert (
            f"Anfrage von 'guest1' nicht angenommen" in stdout_text
            and "ist bereits einem anderen Teilnehmer" in stdout_text
            and "'other'" in stdout_text
            and "Anfrage bleibt OFFEN" in stdout_text
        ), (
            f"R7/g5: die Betreiberausgabe muss die Fremdzuordnungs-Ablehnung fuer guest1 zeigen: {stdout_text}"
        )
        assert (
            f"'guest2' an Tisch 'mesaG5Kontrolle' aufgenommen" in stdout_text
            and "fehlende Hostaufnahme (Onboarding/Katalog) vervollstaendigt" in stdout_text
        ), (
            f"R7/g5: die Betreiberausgabe muss die ERHALTENE konfliktfreie B-Annahme fuer guest2 zeigen: "
            f"{stdout_text}"
        )
        gm_calls = (
            [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
            if calls_log.exists() else []
        )
        assert gm_calls == [], (
            f"R7/g5: diese Familie braucht KEINEN Rundenzug/GM-Call -- die Kernaussage liegt vollstaendig "
            f"an der Admission-/Katalogebene: {gm_calls}"
        )

        r6.write_process_result(
            _OUT_DIR, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="g5_full_launcher_transcript", run_id=_RUN_ID,
            teilnehmer_figur="guest1+guest2", tisch_abschnitt="mesaG5Konflikt+mesaG5Kontrolle",
        )
        mf.export_tree(
            run_dir, "run", aussage="g5_run_dir_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1+guest2",
        )
        mf.export_tree(
            host_onboarding, "host_onboarding", aussage="g5_host_onboarding_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1+guest2",
        )
        mf.export_tree(
            host_catalog, "host_catalog_after", aussage="g5_host_catalog_final_includes_unchanged_other",
            run_id=_RUN_ID, teilnehmer_figur="other+guest1+guest2",
        )
        mf.export_tree(
            guest1_onboarding, "guest1_onboarding", aussage="g5_guest1_private_onboarding", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest1_catalog, "guest1_catalog", aussage="g5_guest1_private_catalog_unchanged", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest2_onboarding, "guest2_onboarding", aussage="g5_guest2_private_onboarding", run_id=_RUN_ID,
            teilnehmer_figur="guest2",
        )
        mf.export_tree(
            guest2_catalog, "guest2_catalog", aussage="g5_guest2_private_catalog", run_id=_RUN_ID,
            teilnehmer_figur="guest2",
        )
        if calls_log.exists():
            mf.export_file(
                calls_log, "gm_calls.jsonl", aussage="g5_gm_double_calls_log_empty", run_id=_RUN_ID,
                teilnehmer_figur="guest1+guest2",
            )
        mf.write_json_body(
            "other_before_fixture.json", {
                "catalog_sha256": sha_other_catalog_before, "figure_sha256": sha_other_figure_before,
                "block": other_block,
            }, aussage="g5_other_c_pre_existing_foreign_registration_fixture", run_id=_RUN_ID,
            teilnehmer_figur="other",
        )
        mf.write_json_body(
            "other_after.json", {
                "catalog_sha256": r6.sha256_of(other_catalog_path), "figure_sha256": r6.sha256_of(other_figure_path),
                "catalog_unchanged": r6.sha256_of(other_catalog_path) == sha_other_catalog_before,
                "figure_unchanged": r6.sha256_of(other_figure_path) == sha_other_figure_before,
            }, aussage="g5_other_c_unchanged_after_rejected_accept_attempt", run_id=_RUN_ID,
            teilnehmer_figur="other",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "initial_guest1": initial_guest1, "initial_guest2": initial_guest2,
                "preview_lines_1": preview_lines_1, "accept_lines_1": accept_lines_1,
                "request_lines_1": request_lines_1, "reject_lines": reject_lines,
                "preview_lines_2": preview_lines_2, "accept_lines_2": accept_lines_2,
                "request_lines_2": request_lines_2, "accept_control_lines": accept_control_lines,
            }, aussage="g5_dialog_io_transcript", run_id=_RUN_ID, teilnehmer_figur="guest1+guest2",
        )
        mf.write_json_body(
            "admission_states.json", {
                "mesaG5Konflikt_before_accept": roster_before_accept,
                "mesaG5Konflikt_after_rejected_accept": roster_after_reject,
                "mesaG5Kontrolle_after_accept": roster_after_accept_control,
            }, aussage="g5_table_admission_roster_states", run_id=_RUN_ID, teilnehmer_figur="guest1+guest2",
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "g5_foreign_registration", "aussage": (
                "G5 (01_NACHZUG.md §1, STOP-EVIDENCE.md §3.2/§3.3): der R7-Produktfix "
                "(tui.py:_decide_participant_save_intake, catalog.find_registration jetzt UNABHAENGIG "
                "vom known_char_ids-Gate) schuetzt eine bereits anderweitig im Hostkatalog registrierte, "
                "inaktive Char-ID auch dann, wenn der gemeinsame Gast-Current dieselbe ID bereits als "
                "'bekannt' fuehrt -- der Annahmeversuch wird VOR jedem Roster-/Hostprojektionswrite "
                "abgelehnt (parked), die Anfrage bleibt offen, fremde Koerper (other/C) bleiben "
                "byte-unveraendert. Der konfliktfreie B-Normalweg (R6-Fix B, nicht fremd registrierte "
                "ID) bleibt in DERSELBEN Lauffamilie erhalten funktionsfaehig."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell (hier ungenutzt, kein Rundenzug)",
            "produktfix_commit": "e34ee6a7 (bereits von Main committet, NICHT Teil dieses Treibers)",
            "produktcode_fundstellen": [
                "mmo_sim/ui/tui.py:302-480 (_decide_participant_save_intake)",
                "mmo_sim/ui/tui.py:385-391 (known_char_ids wird um baseline_char_id des gemeinsamen Current ergaenzt)",
                "mmo_sim/ui/tui.py:418-427 (R7-Fix: catalog.find_registration unabhaengig von known_char_ids -> parked bei Fremdtreffer)",
                "mmo_sim/ui/tui.py:5134-5380 (_cmd_table_accept, Entscheidung VOR accept_request, s. Docstring R4/R5-Nachzug)",
                "mmo_sim/ui/tui.py:5319-5345 (R6-Fix-B No-op-Hostprojektions-Write, jetzt durch den R7-Fremdcheck VORHER geschuetzt)",
                "mmo_sim/domain/zeitriss/catalog.py:150-171 (find_registration, Cross-Teilnehmer-Lesefunktion)",
                "mmo_sim/domain/zeitriss/catalog.py:47-56 (register), 126-137 (store_figure_save)",
            ],
            "konflikt_mesaG5Konflikt": {
                "roster_vorher": roster_before_accept["roster"], "requests_vorher": roster_before_accept["requests"],
                "roster_nachher": roster_after_reject["roster"], "requests_nachher": roster_after_reject["requests"],
                "host_projektion_guest1_vorher": host_projection_guest1_before is not None,
                "host_projektion_guest1_nachher": host_projection_guest1_after is not None,
                "host_katalog_guest1": host_catalog_entries_guest1,
                "other_c_catalog_unveraendert": r6.sha256_of(other_catalog_path) == sha_other_catalog_before,
                "other_c_figure_unveraendert": r6.sha256_of(other_figure_path) == sha_other_figure_before,
            },
            "kontrolle_mesaG5Kontrolle": {
                "roster_nachher": roster_after_accept_control["roster"],
                "host_projektion_guest2_vorher": host_projection_guest2_before is not None,
                "host_projektion_guest2_nachher": host_projection_guest2_after is not None,
                "host_katalog_guest2": [
                    {"participant_id": e.participant_id, "chrononaut_id": e.chrononaut_id}
                    for e in host_catalog_entries_guest2
                ],
            },
            "gm_call_count": len(gm_calls),
            "assertions_bestanden": [
                "Fixture: other/C im Hostkatalog registriert, inaktiv, ohne Lock",
                "guest1: normaler privater Import derselben Char-ID C gelingt, publiziert eigenen Current",
                "guest1-Anfrage bleibt VOR Annahmeversuch offen (pending), keine Hostprojektion",
                "tisch-annehmen fuer guest1 wird abgelehnt (Fremdzuordnungs-Konflikt), KEIN Roster-Write",
                "Anfrage bleibt NACH dem abgelehnten Versuch weiterhin offen (pending)",
                "keine Hostprojektion/Host-Katalogregistrierung fuer guest1 entstanden",
                "other/C-Katalog- und Figurdatei byte-unveraendert vor/nach dem Annahmeversuch",
                "privater Gastimport (guest1) bleibt unveraendert erhalten (kein Rollback)",
                "Gegenprobe guest2 (nicht fremd registrierte ID D): Annahme gelingt, R6-Fix-B-Hostprojektion entsteht",
                "kein GM-Call in dieser Familie noetig",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL g5_foreign_registration: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK g5_foreign_registration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
