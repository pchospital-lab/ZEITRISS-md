#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_b_import_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R6, Familie `b_import` (B/G5, 01_NACHZUG.md §B,
STOP-EVIDENCE.md §3, 02_NACHWEISE_UND_RUECKGABE.md §2 "Import vor erster
Admission"): schliesst den von STOP-EVIDENCE.md §3 belegten Produktgegenfall
-- ein normaler ERSTER Import der eigenen Figur VOR jeder Admission
(OHNE Seed-Ersatzfigur) fuehrte bisher zu `noop_identical` bei der
Tischannahme, OHNE die fuer `_resolve_member`/Tischstart notwendige
HOST-Projektion (Host-Onboarding/-Katalog) zu schreiben. Der R6-Fix B
(`mmo_sim/ui/tui.py:_decide_participant_save_intake`/`_write_participant_
save_intake`/`_cmd_table_accept`) stellt diese Projektion jetzt im
`noop_identical`-Zweig her, OHNE zweite Current-Version/Fortschritt.

ECHTER Launcher-Subprozess (literal `scripts/mmo_sim.py`), GM-Anbieter NUR
als FIX5-Grenzinjektion, NIE Live-Modell. Vorlage: `drive_r5_t1_evidence_
2026_11_05.py` (T1a), aber OHNE die dortige `chrono-t1a-seed`-Admission vor
dem eigentlichen Import -- genau diese Umgehung soll hier NICHT verwendet
werden (01_NACHZUG.md §B: "Keine zuvor angenommene Seed-/Ersatzfigur als
Voraussetzung").

Ablauf: figureloser Betreiber startet den Launcher mit angeschlossenem
hostlosem Gast. Gast importiert seine volle GUELTIGE eigene Figur ueber den
normalen Terminalweg (`i`), BEVOR jede Tischanfrage/-admission -- das
publiziert den Save zusaetzlich als gemeinsamen Current/State (`tui.py:
_cmd_import`). Gast fragt einen Tisch an; figureloser Betreiber nimmt an
(`noop_identical`-Zweig greift, da die Figur bereits identisch im
gemeinsamen Current steht) -> R6-Fix B stellt die fehlende Hostprojektion
her. Betreiber startet DENSELBEN Tisch regulaer -> `_resolve_member('guest1')`
loest jetzt auf, der Tischstart gelingt (vorher: 'noch keine abgeschlossene
Figur vorhanden').

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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path("/home/altair/zr-betreiber-gast-20261105/r6/run/evidence/r6-runs/b_import")
_RUN_ID = "b_import_normal_import_before_first_admission_noop_identical_host_projection"


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
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

        write_test_profile(run_dir, max_turns=200)

        host_onboarding = op_data / "onboarding"
        host_catalog = op_data / "catalog"
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"

        char_id = "CHR-R6B-IMPORT-GAST"
        own_block = full_v7_save(char_id, name="GastR6BImport", save_id="fixture-r6b-import-guest-001")
        own_block_json = json.dumps(own_block, ensure_ascii=False)

        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (B/Import, R6)."], calls_log=calls_log, stop=None,
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
        initial_guest = r4._drain(out_f, settle=0.6, overall=10.0)
        assert initial_guest, "R6/b_import: Gast-Terminal hat keinen Startbanner gesendet."

        # Vor jedem Import/jeder Admission: keine Hostprojektion, kein
        # gemeinsamer Current, keine private Gastfigur.
        host_projection_before = onboarding.peek(host_onboarding, "guest1")
        assert host_projection_before is None, (
            f"R6/b_import: VORHER darf keine Hostprojektion fuer 'guest1' existieren: {host_projection_before}"
        )
        current_path = run_dir / "current_saves" / "guest1.json"
        versions_dir = run_dir / "current_saves" / "guest1__versions"
        assert not current_path.exists(), "R6/b_import: VORHER kein gemeinsamer Current fuer 'guest1'."

        # ── Normaler Import der EIGENEN vollstaendig gueltigen Figur UEBER
        # DAS NORMALE TERMINAL, VOR jeder Tischanfrage/-admission -- KEINE
        # Seed-/Ersatzfigur.
        r4._send_guest(in_f, "i")
        r4._wait_for_marker(out_f, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f, own_block_json)
        r4._send_guest(in_f, "ENDE")
        # Die nachfolgende Bestaetigungsfrage ("Figur char_id=... jetzt
        # uebernehmen und speichern? [j/n]: ") ist ein reiner readline()-
        # Promptstring, der NICHT ueber print_fn/out_fifo echot wird
        # (empirisch verifiziert, identisch zur T1a-Beobachtung) -- direkt
        # 'j' senden, kein Warten auf einen nie erscheinenden Marker.
        preview_lines = r4._wait_for_marker(out_f, f"char_id={char_id}", overall=20.0)
        joined_preview = "".join(preview_lines)
        assert "WARNUNG" not in joined_preview, (
            f"R6/b_import: dies ist eine VOLLSTAENDIG gueltige Figur, keine Toleranzwarnung erwartet: "
            f"{preview_lines}"
        )
        r4._send_guest(in_f, "j")
        accept_lines = r4._wait_for_marker(out_f, "Uebernahme abgeschlossen", overall=20.0)
        joined_accept = "".join(accept_lines)
        assert f"action=register_new char_id={char_id}" in joined_accept, joined_accept
        r4._drain(out_f, settle=0.6, overall=5.0)

        # Import publiziert den Save ZUSAETZLICH als gemeinsamen Current/
        # State (STOP-EVIDENCE.md §3.1 Punkt 2) -- GENAU EINE Version, aber
        # weiterhin KEINE Hostprojektion.
        assert current_path.exists(), (
            "R6/b_import: der normale Import muss den Save zusaetzlich als gemeinsamen Current "
            "publizieren (tui.py:_cmd_import)."
        )
        version_files_after_import = sorted(versions_dir.glob("*.json"))
        assert len(version_files_after_import) == 1, (
            f"R6/b_import: nach dem Import wird GENAU EINE gemeinsame Version erwartet: "
            f"{version_files_after_import}"
        )
        sha_current_after_import = r6.sha256_of(current_path)
        host_projection_after_import = onboarding.peek(host_onboarding, "guest1")
        assert host_projection_after_import is None, (
            f"R6/b_import: der Import alleine darf (noch) KEINE Hostprojektion schreiben -- das ist "
            f"GENAU die vom B-Fix geschlossene Luecke, die erst bei der Tischannahme auftritt: "
            f"{host_projection_after_import}"
        )
        private_figure_path = guest_catalog / "figures" / f"guest1__{char_id}.json"
        assert private_figure_path.exists(), "R6/b_import: private Gastablage fehlt nach Import."
        sha_private_after_import = r6.sha256_of(private_figure_path)

        # ── Gast fragt einen Tisch an; figureloser Betreiber nimmt an.
        r4._send_op(proc, "tisch-anbieten mesaB")
        time.sleep(0.6)
        r4._send_guest(in_f, "tisch-anfragen mesaB")
        request_lines = r4._drain(out_f, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaB' gestellt" in l for l in request_lines), request_lines

        r4._send_op(proc, "tisch-annehmen mesaB guest1")
        time.sleep(0.6)

        # Die Betreiberausgabe ("aufgenommen (roster: ...)") geht auf
        # proc.stdout; wir lesen sie am Prozessende vollstaendig mit aus
        # (siehe stdout_text unten) -- hier zunaechst die Produktwirkung an
        # den echten Koerpern pruefen (robuster als Terminal-Timing).
        host_projection_after_accept = onboarding.peek(host_onboarding, "guest1")
        assert host_projection_after_accept is not None and host_projection_after_accept.final_save is not None, (
            "R6/b_import: NACH der Annahme (noop_identical-Zweig, R6-Fix B) muss die Hostprojektion "
            "(Host-Onboarding final_save) jetzt vorhanden sein."
        )
        host_catalog_entries_after_accept = catalog.list_for_participant(host_catalog, "guest1")
        assert len(host_catalog_entries_after_accept) == 1, (
            f"R6/b_import: GENAU EIN Host-Katalogeintrag fuer 'guest1' nach der Annahme erwartet: "
            f"{host_catalog_entries_after_accept}"
        )
        assert host_catalog_entries_after_accept[0].chrononaut_id == char_id, host_catalog_entries_after_accept

        # KEINE zweite Current-Version/kein zweiter Fortschritt durch die
        # Annahme selbst.
        version_files_after_accept = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_after_accept] == [p.name for p in version_files_after_import], (
            f"R6/b_import: die Hostprojektions-Herstellung darf KEINE zweite Current-Version erzeugen: "
            f"vorher={[p.name for p in version_files_after_import]} nachher={[p.name for p in version_files_after_accept]}"
        )
        assert r6.sha256_of(current_path) == sha_current_after_import, (
            "R6/b_import: der gemeinsame Current darf durch die Hostprojektions-Herstellung NICHT "
            "veraendert werden."
        )
        assert r6.sha256_of(private_figure_path) == sha_private_after_import, (
            "R6/b_import: die private Gastfigur darf durch die Annahme NICHT veraendert werden."
        )
        guest_catalog_entries = catalog.list_for_participant(guest_catalog, "guest1")
        assert len(guest_catalog_entries) == 1, (
            f"R6/b_import: die private Gastkatalogfigur bleibt unveraendert GENAU EIN Eintrag: "
            f"{guest_catalog_entries}"
        )

        # ── Betreiber startet DENSELBEN Tisch regulaer -- `_resolve_member`
        # muss jetzt aufloesen (vorher: 'noch keine abgeschlossene Figur').
        r4._send_op(proc, "tisch-start mesaB")
        round_lines = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        joined_round = "".join(round_lines)
        assert "noch keine abgeschlossene Figur" not in joined_round, (
            f"R6/b_import: der Tischstart durfte NICHT mehr an der fehlenden abgeschlossenen Figur "
            f"scheitern: {round_lines}"
        )
        # "Empfaenger: Spielleitung (SL)" ist die Adressierungsabfrage AN DEN
        # GAST, BEVOR die SL/der GM ueberhaupt gerufen wird -- der eigentliche
        # GM-Call erfolgt erst, NACHDEM der Gast seine Zugnachricht gesendet
        # hat (identisches Muster zu T1a/T1b).
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die neue Umgebung.")
        post_answer = r4._drain(out_f, settle=0.8, overall=10.0)
        assert "Unbekannte Auswahl" not in "".join(post_answer), post_answer

        r4._wait_for_path(calls_log, overall=15.0)
        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 1, (
            f"R6/b_import: GENAU EIN GM-Call (Ankerantwort der regulaer gestarteten Runde) erwartet: "
            f"{gm_calls}"
        )

        # R6/b_import braucht KEINE vollstaendige Abschnittsfertigstellung --
        # die Kernaussage (Tischstart/_resolve_member loest jetzt auf, echter
        # GM-Call findet statt) ist mit dem obigen Marker bereits belegt. Der
        # Rundenzug selbst bleibt (wie bei jeder echten, nicht fertiggestellten
        # Runde) offen -- der Prozess wird deshalb EHRLICH ueber SIGTERM
        # beendet statt ueber 'beenden' (das den Rueckkehrweg in den
        # Hauptmenueloop erst nach vollstaendigem Rundenabschluss erreicht);
        # dies wird im echten, nicht-gefaelschten Exitcode unten dokumentiert.
        proc.terminate()
        try:
            stdout_text, stderr_text = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_text, stderr_text = proc.communicate(timeout=15)
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert (
            f"'guest1' an Tisch 'mesaB' aufgenommen" in stdout_text
            and "fehlende Hostaufnahme (Onboarding/Katalog) vervollstaendigt" in stdout_text
            and "KEINE zweite Version/kein zweiter Fortschritt" in stdout_text
        ), (
            f"R6/b_import: die neue R6-Fix-B-Betreibermeldung muss im vollen Transkript stehen: "
            f"{stdout_text}"
        )
        assert "noch keine abgeschlossene Figur" not in stdout_text, stdout_text

        r6.write_process_result(
            _OUT_DIR, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="b_import_full_launcher_transcript", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt="mesaB",
        )
        mf.export_tree(
            run_dir, "run", aussage="b_import_run_dir_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1", tisch_abschnitt="mesaB",
        )
        mf.export_tree(
            host_onboarding, "host_onboarding", aussage="b_import_host_onboarding_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            host_catalog, "host_catalog", aussage="b_import_host_catalog_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest_onboarding, "guest_onboarding", aussage="b_import_guest_onboarding_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_tree(
            guest_catalog, "guest_catalog", aussage="b_import_guest_catalog_final", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="b_import_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "initial_guest": initial_guest, "preview_lines": preview_lines,
                "accept_lines": accept_lines, "request_lines": request_lines,
                "round_lines": round_lines, "post_answer": post_answer,
            }, aussage="b_import_dialog_io_transcript", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_json_body(
            "inventory.json", {
                "before_import": {
                    "host_projection_present": host_projection_before is not None,
                    "current_present": current_path.exists(),
                },
                "after_import_before_accept": {
                    "host_projection_present": host_projection_after_import is not None,
                    "current_sha256": sha_current_after_import,
                    "version_files": [p.name for p in version_files_after_import],
                    "private_figure_sha256": sha_private_after_import,
                },
                "after_accept": {
                    "host_projection_present": host_projection_after_accept is not None,
                    "host_catalog_entries": [
                        {"participant_id": e.participant_id, "chrononaut_id": e.chrononaut_id}
                        for e in host_catalog_entries_after_accept
                    ],
                    "version_files": [p.name for p in version_files_after_accept],
                    "current_sha256_unchanged": r6.sha256_of(current_path) == sha_current_after_import,
                    "private_figure_sha256_unchanged": r6.sha256_of(private_figure_path) == sha_private_after_import,
                },
                "after_table_start": {"gm_call_count": len(gm_calls)},
            }, aussage="b_import_before_after_inventory", run_id=_RUN_ID, teilnehmer_figur="guest1",
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "b_import", "aussage": (
                "B/G5 (01_NACHZUG.md §B, STOP-EVIDENCE.md §3): normaler ERSTER Import der eigenen "
                "gueltigen Figur VOR jeder Admission (keine Seed-Ersatzfigur) fuehrt bei der "
                "figurelosen Tischannahme zu noop_identical; R6-Fix B stellt die fehlende "
                "Hostprojektion (Host-Onboarding+Katalog) OHNE zweite Current-Version/Fortschritt "
                "her -- der anschliessende reguläre Tischstart gelingt jetzt (vorher: 'noch keine "
                "abgeschlossene Figur')."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "host_projection_before_import": False,
            "host_projection_after_import_before_accept": False,
            "host_projection_after_accept": True,
            "version_count_stable": [p.name for p in version_files_after_import] == [p.name for p in version_files_after_accept],
            "current_unchanged_by_accept": True,
            "gm_call_count": len(gm_calls),
            "prozessende": (
                "Die eigentliche Kernaussage (Tischstart/_resolve_member loest jetzt auf, echter "
                "GM-Call fuer die Ankerfrage findet statt) ist bereits mit dem Erreichen von "
                "'Empfaenger: Spielleitung (SL)' vollstaendig belegt. Der Rundenzug selbst bleibt "
                "(wie jede echte, nicht fertiggestellte Spielrunde) offen -- diese Familie verlangt "
                "KEINE Abschnittsfertigstellung. Der Prozess wurde deshalb EHRLICH per SIGTERM/SIGKILL "
                "beendet statt mit 'beenden' erzwungen zu werden (das den Hauptmenueloop erst nach "
                "vollstaendigem Rundenabschluss zurueckgegeben haette); der echte, nicht-gefaelschte "
                "Exitcode ist in launcher.run.json dokumentiert (negativer Signal-Exitcode, kein "
                "stiller 0-Vortäuschung)."
            ),
            "assertions_bestanden": [
                "keine Hostprojektion vor Import/Admission",
                "normaler Import publiziert gemeinsamen Current (genau 1 Version), KEINE Toleranzwarnung",
                "Hostprojektion bleibt nach Import (vor Admission) weiterhin fehlend",
                "tisch-annehmen (noop_identical) stellt Hostprojektion her, neue R6-Fix-B-Meldung erscheint",
                "keine zweite Current-Version/kein veraenderter Current/keine veraenderte private Figur",
                "regulaerer Tischstart gelingt (_resolve_member loest auf), kein 'noch keine "
                "abgeschlossene Figur'-Fehler, genau 1 GM-Call",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL b_import: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK b_import")
    return 0


if __name__ == "__main__":
    sys.exit(main())
