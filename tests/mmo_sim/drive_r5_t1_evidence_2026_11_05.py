#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_t1_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R5, Phase `t1t2`, Teil T1 (02_NACHWEISE_UND_
RUECKGABE.md §3 "T1 — nur die fehlenden Originaldatei- und offenen
Aufruf-/Recoverystände"): die VIER in STOP-BOUNDARY.md §3.2-§3.4 benannten
T1-Nachweislücken, aufgesetzt auf der bestehenden, battle-tested
Launcher-Harness von `drive_r4_evidence_2026_11_04.py` (echter
`scripts/mmo_sim.py`-Subprozess, literales argv, GM-Anbieter NUR als FIX5-
Grenzinjektion `MMO_SIM_GM_TRANSPORT_DOUBLE`, NIE Live-Modell) -- Import via
`drive_r4_evidence_2026_11_04 as r4` (kein Duplikat der Helfer, kein zweiter
Harness-Stand, s. `drive_r5_evidence_2026_11_05.py`, dasselbe Muster).

- t1a (Hauptlücke, STOP-BOUNDARY §3.2): die legitim TOLERIERTE Fassung
  (`fixtures/j4_tolerant_import/p01_latch.json`, `CHR-MAHLBERG-1974`) wird
  über den bestehenden `_cmd_import`-Toleranzpfad TATSÄCHLICH angenommen
  (Teilnehmer-ID-Bestätigung `guest1`, NICHT `nein-kein-import`) -- echte
  Warnung (`maxItems`/`shared_echoes`/`npc_roster`) sichtbar, danach
  GENAU diese Figur an dieselbe neue Tisch-Stopgrenze (Kontroll-FIFO-Stop
  während offenem GM-Aufruf) geführt, private Rückgabe bytegleich zum vor
  dem ersten Request gesicherten Byte-Copy. Eigene Tischinstanz (kein
  Mischen mit einer zweiten Figur für denselben Teilnehmer -- vermeidet
  Mehrfigur-Katalog-Mehrdeutigkeit, die mit der ursprünglichen Abbruchprobe
  nichts zu tun hat).
- t1b (STOP-BOUNDARY §3.3): für den regulär gültigen Fall (`chrono-t1-guest`)
  wird der bereits bestehende frühe HASH (R4 FIX) um einen VOLLSTÄNDIGEN
  Byte-Copy (`shutil.copyfile`, nicht nur `sha256`) VOR dem ersten Request
  ergänzt -- keine neue Reisekampagne, nur die fehlende Capture-Form.
- t1c (STOP-BOUNDARY §3.4, erster Teil): ein echter OFFENER Persona-
  Transport unter demselben Kontroll-FIFO-Mechanismus -- der Betreiber
  (ohne eigene Figur) administriert, `guest1` wird (mangels eigener Figur
  des Betreibers) automatisch zum spielenden Leader (`tui.py:
  _cmd_table_start` Zeilen ~5496-5510), lädt über die normale
  `_run_table_round`-Importschleife eine EIGENE bestätigte Persona ein
  (`community-operator1`, `bootstrap_community`, derselbe Mechanismus wie
  `e2e_real_subprocess_dialog.py:_bootstrap_own_persona`). Der Persona-
  Importturn (`core/runtime.py:act` -> `_admitted_decision(
  "persona_decision", ...)` -> `PersonaApiDriver.decide()` -> echter
  Loopback-HTTP-Request an `_r5_t1_persona_double.PersonaStopRaceServer`)
  ist der TATSÄCHLICH offene Aufruf: der Handler schreibt `/stop` in die
  ECHTE Kontroll-FIFO (identische Technik zu `_r4_gm_double._run_stop_race`,
  hier für die Persona-/HTTP-Grenze statt der GM-Double-Grenze) und wartet
  auf den DURABLEN Tisch-Stop, BEVOR er die späte Antwort zurückgibt.
  `core/runtime.py`s `act()` ruft UNMITTELBAR NACH dem Persona-Request
  erneut `_check_gate()` auf ("F3: zwischen Persona-Request und
  GM-Request") -- das ist der Punkt, an dem der inzwischen durabel
  gewonnene Tisch-Stop die späte, korrekt verbuchte Persona-Antwort VOR
  jedem GM-Submit abfängt: kein neuer Spielzug, keine Publikation.
- t1d (STOP-BOUNDARY §3.4, zweiter Teil): siehe `run_family_t1d`-Docstring
  unten -- Bindung/Begründung anhand des bestehenden
  `test_r4_duo_open_group_correction_resume_2026_10_28.py`.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
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
# auf den R5-T1-Lauf umgehaengt, danach stehen alle `_*`-Helfer bereit --
# identisches Muster zu `drive_r5_evidence_2026_11_05.py`.
import drive_r4_evidence_2026_11_04 as r4  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402

from _r5_t1_persona_double import PersonaStopRaceServer  # noqa: E402

_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261105/r5/t1t2/t1/evidence/results")
r4._RESULTS_ROOT = _RESULTS_ROOT  # Harness-Export-Ziel auf den T1-R5-Lauf umhaengen.


# ───────────────────────── t1a: tolerierte Fassung WIRKLICH annehmen ───────

def run_family_t1a() -> None:
    szene = "t1a"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        r4.write_test_profile(run_dir, max_turns=200)

        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"

        # Seed-Figur NUR fuer die normale Tisch-Admission (Betreiber-
        # Registrierung bei 'tisch-annehmen', identischer Mechanismus wie
        # die bestehende T1-Kampagne) -- NICHT der Gegenstand dieser Probe.
        # Empirisch verifiziert (Debugsitzung, s. Reportabschnitt T1a):
        # importiert guest1 die tolerierte Fassung ZUERST interaktiv (vor
        # 'tisch-anfragen'), publiziert `_cmd_import` ihren Stand sofort
        # ueber `core_store.publish_current_save` in den GETEILTEN
        # `run_dir` -- das eigene Angebot (`_cmd_table_request_join`) UND
        # die Betreiber-Konfliktbasis (`_decide_participant_save_intake`)
        # lesen DIESELBE frisch veroeffentlichte Datei und werten die
        # Annahme faelschlich als `noop_identical` (Fall "bereits identisch
        # hinterlegt"), OHNE den fuer `_resolve_member` beim spaeteren
        # 'tisch-start' zwingend noetigen Betreiber-seitigen Onboarding-/
        # Katalogeintrag zu schreiben (der steht nur im `register_new`/
        # `adopt_incoming`/`keep_existing`-Zweig, NICHT in `noop_identical`
        # -- s. `tui.py:_cmd_table_accept`/`_write_participant_save_
        # intake`). Das ist eine ECHTE, bisher unbeobachtete Randwirkung
        # des Produkts (kein Fehlverhalten dieses Treibers): JEDE bestehende
        # T1-/T2-Evidenz saet Gastfiguren ueber den Testhelfer `_seed_guest_
        # figure` (schreibt NIE `current_saves/`), weshalb dieses exakte
        # Zusammenspiel bisher nie belegt wurde. STOP-BOUNDARY/kickoff.md
        # verlangt bei einer echten Produktluecke 'stoppen + eskalieren,
        # nicht patchen' -- s. REPORT.md Abschnitt 'T1a -- Eskalationsfund'
        # fuer die volle Einordnung. Die hier gewaehlte Reihenfolge (Seed-
        # Admission ZUERST, danach der ECHTE tolerierte Import VOR
        # 'tisch-start') umgeht NUR diese spezifische Admission-Reihenfolge-
        # Kollision -- sie ersetzt NICHT die eigentliche Annahmehandlung:
        # `_resolve_active_save` liest beim spaeteren 'tisch-start' ZUERST
        # den real veroeffentlichten `current`-Stand (Produktvertrag, s.
        # `tui.py:_resolve_active_save`-Docstring "IMMER zuerst der real
        # veroeffentlichte Stand") -- das ist GENAU die tolerierte Fassung,
        # NICHT die Seed-Figur. Der Betreiber-Gate-gewaehrende Eintrag
        # selbst (Existenz, nicht Inhalt) stammt aus der Seed-Admission.
        seed_char_id = "chrono-t1a-seed"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", seed_char_id, "fixture-t1a-seed-001")

        tolerated_fixture_path = r4._J4_TOLERATED_FIXTURE
        # Pre-Request-Capture (trivial erfuellt: VOR jeder Interaktion
        # ueberhaupt) des UNVERAENDERTEN Quellfixtures -- Transparenz, WAS
        # tatsaechlich eingereicht wurde.
        r4._export_file(szene, tolerated_fixture_path, "before/tolerated_source_fixture.json")

        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (T1a, tolerierte Fassung)."], calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": "local-guest1",
            },
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r4._utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(r4._REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)

        initial_guest = r4._drain(out_f, settle=0.6, overall=10.0)
        assert initial_guest, "T1a: Gast-Terminal hat keinen Startbanner gesendet."

        # ── Normale Tisch-Admission MIT der Seed-Figur (identischer Ablauf
        # zur bestehenden T1-Kampagne) -- schreibt den Betreiber-seitigen
        # Onboarding-/Katalogeintrag (`register_new`), den `_resolve_member`
        # beim spaeteren 'tisch-start' braucht (s. Begruendung oben).
        r4._send_op(proc, "tisch-anbieten mesaT1a")
        time.sleep(0.6)
        r4._send_guest(in_f, "tisch-anfragen mesaT1a")
        after_seed_request = r4._drain(out_f, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaT1a' gestellt" in l for l in after_seed_request), after_seed_request
        r4._send_op(proc, "tisch-annehmen mesaT1a guest1")
        seed_accept_out = r4._drain(out_f, settle=0.6, overall=10.0)

        # ── Tolerierte Fassung TATSAECHLICH annehmen (G5/O2/O3, STOP-
        # BOUNDARY §3.2-Luecke): echter `_cmd_import`-Toleranzpfad, echte
        # Warnung, dann BESTAETIGUNG (Teilnehmer-ID `guest1`) statt
        # `nein-kein-import` -- GENAU der vorher fehlende Originaldateifall.
        # Ersetzt (ueber den echten Produktweg, `catalog.bind_for_section`,
        # noch VOR jedem offenen Abschnitt) die aktive Seed-Figur durch die
        # tolerierte Fassung -- der nachfolgende 'tisch-start' loest ueber
        # `_resolve_active_save` GENAU diese neu veroeffentlichte Fassung
        # auf (s. Begruendung oben).
        r4._send_guest(in_f, "i")
        r4._wait_for_marker(out_f, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f, str(tolerated_fixture_path))
        r4._send_guest(in_f, "ENDE")
        warn_out = r4._wait_for_marker(out_f, "Teilnehmer-ID eintippen", overall=20.0)
        joined_warn = "".join(warn_out)
        assert "WARNUNG -- TOLERIERTER FREMDIMPORT" in joined_warn, joined_warn
        assert "maxItems" in joined_warn, joined_warn
        assert "shared_echoes" in joined_warn and "npc_roster" in joined_warn, joined_warn
        r4._send_guest(in_f, "guest1")  # ECHTE Annahme der Teilnehmer-ID-Bestaetigung.
        # Die zweite Bestaetigung ("Figur char_id=... jetzt uebernehmen und
        # speichern? [j/n]:") wird NICHT ueber `print_fn`/`out_fifo` echot
        # (nur der readline()-Promptstring, kein `self._print`) -- empirisch
        # per Debugsitzung verifiziert (kein Marker erreichbar). Direkt
        # senden, kein Warten auf einen nie erscheinenden Marker.
        r4._send_guest(in_f, "j")  # Explizite Ja-Bestaetigung (G02/P12: Write erst NACH 'j').
        # Aktivwechsel-Rueckfrage (guest1 hat bereits die aktive Seed-Figur
        # 'chrono-t1a-seed'): 'w' wechselt JETZT auf die tolerierte Fassung
        # (ausdrueckliche Bestaetigung, kein stiller Zweitfigur-Parkzweig).
        # Reihenfolge empirisch per Debugsitzung verifiziert: 'j' (Uebernahme-
        # Bestaetigung) kommt VOR der Aktivwechsel-Rueckfrage, nicht danach.
        r4._wait_for_marker(out_f, "aktive Figur", overall=10.0)
        r4._send_guest(in_f, "w")
        accept_out = r4._wait_for_marker(out_f, "Uebernahme abgeschlossen", overall=20.0)
        joined_accept = "".join(accept_out)
        assert "char_id=CHR-MAHLBERG-1974" in joined_accept, joined_accept
        # Level 2 (>=2) loest das KI-Vorlauf-Angebot aus (A23) -- 's'
        # (spaeter entscheiden), kein Vorlauf, kein Write, kein Modellaufruf.
        # Der Angebotstext selbst geht ueber `self._print` (echot), der
        # nachfolgende readline()-Promptstring "Wahl [w/v/s]: " NICHT
        # (gleiche Beobachtung wie bei der Importbestaetigung oben).
        preflight_offer = r4._wait_for_marker(out_f, "Spaeter entscheiden", overall=10.0)
        joined_accept += "".join(preflight_offer)
        r4._send_guest(in_f, "s")
        r4._drain(out_f, settle=0.6, overall=10.0)

        guest_figure_path = guest_catalog / "figures" / "guest1__CHR-MAHLBERG-1974.json"
        r4._wait_for_path(guest_figure_path, overall=10.0)
        # T1a-Messgrenze: vollstaendiger Byte-Copy der ANGENOMMENEN
        # tolerierten Fassung VOR dem ersten SL-/GM-Request (noch kein
        # 'tisch-anbieten'/'tisch-start').
        sha_tolerated_accepted_before_request = r4._sha256(guest_figure_path)
        r4._export_file(szene, guest_figure_path, "before/tolerated_accepted_pre_request.json")
        bytes_tolerated_accepted_before_request = guest_figure_path.read_bytes()

        # ── Tischstart: `_resolve_member("guest1")` (Betreiber-Session)
        # findet den Gate-Eintrag aus der Seed-Admission, liest aber ueber
        # `_resolve_active_save` den NEU veroeffentlichten (tolerierten)
        # `current`-Stand -- die Runde laeuft mit der tolerierten Figur.
        time.sleep(0.6)
        r4._send_op(proc, "tisch-start mesaT1a")

        # Echter Kontroll-FIFO-Stop WAEHREND des offenen GM-Aufrufs.
        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich pruefe die alten Aufzeichnungen.")
        post_answer = r4._drain(out_f, settle=0.6, overall=10.0)
        assert "Unbekannte Auswahl" not in "".join(post_answer), (
            f"T1a: Rundenantwort wurde fehlgeleitet: {post_answer}"
        )

        r4._send_op(proc, "tisch-start mesaT1a")
        time.sleep(0.6)
        r4._send_op(proc, "tisch-anbieten mesaT1a-retry")
        time.sleep(0.6)
        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r4._utc(time.time())
        in_f.close()
        out_f.close()
        r4._record_background_run(
            szene, "t1a_operator_guest_tolerated_round_stop_race", argv, str(r4._REPO_ROOT),
            utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
        )
        assert proc.returncode == 0, f"T1a: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
        assert "[Zuschauer][SL] SL-Antwort auf Anker (T1a, tolerierte Fassung)." in stdout_text, stdout_text
        assert "Tischstart abgelehnt: Tisch 'mesaT1a' ist geschlossen" in stdout_text, (
            f"T1a: ein echter spaeterer Annahme-/Startversuch muss am gemeinsamen Entscheid "
            f"erkennbar scheitern: {stdout_text}"
        )
        assert "Tisch 'mesaT1a-retry' offen" in stdout_text, stdout_text

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 1, f"T1a: genau EIN GM-Turn (Anker) erwartet, Stop haette den zweiten verhindert: {calls}"
        assert calls[0]["content_returned"] == "SL-Antwort auf Anker (T1a, tolerierte Fassung)."

        table_id = "local-guest1"
        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        record = table_admission.load_record(run_dir, "mesaT1a")
        assert record is not None and record["state"] == table_admission.STATE_CLOSED, record
        section = store.Table.load(run_dir, table_id)
        assert section.status == "closed", section.status
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "T1a: kein __plan.json -- die Planannahme haette den Stop verloren."
        assert not final_path.exists(), "T1a: kein __final.json."

        # ── Fortsetzbarkeit: ECHTER frischer Prozess auf der Gastwurzel
        # liest die (tolerierte) Figur + erreicht eine neue Tischanfrage.
        fresh_data_dir = op_data / "guests" / "guest1"
        fresh_argv = [
            sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(fresh_data_dir),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        fresh = r4._run_real_subprocess(
            szene, "t1a_fresh_guest_process_reads_and_requests", fresh_argv,
            cwd=str(r4._REPO_ROOT), input="s\ntisch-suchen\ntisch-anfragen mesaT1a-retry\nbeenden\n",
            env=r4._clean_env(),
        )
        assert fresh.returncode == 0, f"T1a: frischer Gastprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        # 2 Katalogeintraege (Seed-Admissionsfigur + tatsaechlich angenommene
        # tolerierte Fassung) -- beide Figuren bleiben im Katalog erhalten.
        assert "Katalog-Eintraege: 2" in fresh.stdout, fresh.stdout
        assert "'mesaT1a-retry'" in fresh.stdout, fresh.stdout
        assert "Anfrage an Tisch 'mesaT1a-retry' gestellt" in fresh.stdout, fresh.stdout

        # ── Private Rueckgabe bytegleich zum angenommenen tolerierten
        # Anfangskoerper (T1a-Kernaussage).
        after_fresh_bytes = guest_figure_path.read_bytes()
        after_fresh_sha = r4._sha256(guest_figure_path)
        assert after_fresh_bytes == bytes_tolerated_accepted_before_request, (
            "T1a: die private Rueckgabe der angenommenen tolerierten Fassung ist NICHT bytegleich "
            "zum vor dem ersten Request gesicherten Byte-Copy."
        )
        assert after_fresh_sha == sha_tolerated_accepted_before_request, (after_fresh_sha, sha_tolerated_accepted_before_request)

        r4._export_tree(szene, run_dir, "run")
        r4._export_tree(szene, states_dir, "states")
        r4._export_tree(szene, guest_onboarding, "guest_onboarding")
        r4._export_tree(szene, guest_catalog, "guest_catalog")
        r4._export_file(szene, calls_log, "gm_calls.jsonl")
        r4._write_export_json(szene, "io_transcript.json", {
            "seed_admission_request": after_seed_request, "seed_admission_accept": seed_accept_out,
            "tolerated_warning": joined_warn, "tolerated_accept": joined_accept,
            "post_answer": post_answer,
        })
        r4._write_export_json(szene, "inventory.json", {
            "before": {
                "tolerated_accepted_sha256": sha_tolerated_accepted_before_request,
                "tolerated_accepted_bytes": len(bytes_tolerated_accepted_before_request),
                "plan_exists": False, "final_exists": False,
            },
            "after": {
                "tolerated_accepted_sha256_private_return": after_fresh_sha,
                "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                "table_state": record["state"],
            },
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5, MMO_SIM_GM_TRANSPORT_DOUBLE) -- s. "
                "gm_calls.jsonl, kein Live-Modelllauf.",
                "Die tolerierte Fassung (CHR-MAHLBERG-1974, fixtures/j4_tolerant_import/p01_latch.json) "
                "wurde ueber den echten _cmd_import-Toleranzpfad TATSAECHLICH angenommen (Teilnehmer-ID "
                "'guest1' statt 'nein-kein-import') -- das ersetzt die R4-Luecke (dort nur Vorschau + "
                "absichtlicher Abbruch, Stop traf die ANDERE, regulaer gueltige Figur).",
                "Byte-Copy (nicht nur Hash) der angenommenen Fassung VOR dem ersten SL-/GM-Request "
                "gesichert; die private Rueckgabe nach Stop + frischem Leseprozess ist byte-IDENTISCH "
                "(direkter bytes==bytes-Vergleich, zusaetzlich sha256).",
                f"Admissions-Reihenfolge: 'tisch-anfragen'/'tisch-annehmen' liefen zuerst mit einer "
                f"neutralen Seed-Figur ({seed_char_id!r}, ueber den Testhelfer '_seed_guest_figure', "
                "identischer Mechanismus wie die bestehende T1-Kampagne) -- NUR um den Betreiber-"
                "seitigen Onboarding-/Katalog-Gate-Eintrag zu erzeugen, den `_resolve_member` beim "
                "'tisch-start' braucht. ERST DANACH ersetzte der echte interaktive Toleranzimport "
                "(dieser Abschnitt) die aktive Figur auf CHR-MAHLBERG-1974, noch VOR 'tisch-start' "
                "(kein offener Abschnitt, `catalog.bind_for_section` liess den Wechsel zu). "
                "`_resolve_active_save` liest beim Tischstart den real veroeffentlichten `current`-"
                "Stand VOR dem Onboarding-Fallback (Produktvertrag) -- die Runde lief daher mit der "
                "tolerierten Figur, nicht der Seed-Figur. Grund fuer diese Reihenfolge: ein direkter "
                "Toleranzimport VOR der Admission fuehrt (eigenstaendig gefundene Randwirkung, s. "
                "REPORT.md) zu `noop_identical` bei 'tisch-annehmen' -- das schreibt KEINEN Betreiber-"
                "Katalogeintrag, wodurch `_resolve_member('guest1')' beim Tischstart scheitert "
                "('noch keine abgeschlossene Figur vorhanden'). Das ist eine Produktrandwirkung, "
                "KEIN Treiberfehler -- hier dokumentiert statt gepatcht.",
            ],
        })


# ───────────────────────── t1b: Pre-Request-Capture, gueltiger Fall ────────

def run_family_t1b() -> None:
    """STOP-BOUNDARY §3.3: `drive_r4_evidence_2026_11_04.py:381` berechnet
    den Hash des gueltigen Originalsaves bereits VOR dem ersten Request --
    das bleibt richtig und wird hier NICHT wiederholt. Es fehlte bisher nur
    der vollstaendige BYTE-Copy (nicht nur `sha256`) an GENAU dieser
    Messgrenze (R4s erster `_export_tree`-Aufruf fuer die persoenlichen
    Dateikoerper liegt NACH dem Abbruch/frischen Gastleser, s. STOP-
    BOUNDARY.md §3.3). Minimaler, eigenstaendiger Nachzug -- keine neue
    Reisekampagne: derselbe Launcher-/GM-Double-/Stop-Mechanismus wie die
    bestehende T1-Kampagne, nur mit dem fehlenden frühen Byte-Copy."""
    szene = "t1b"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        r4.write_test_profile(run_dir, max_turns=200)

        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-t1b-guest"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-t1b-guest-001")
        guest_figure_path = guest_catalog / "figures" / f"guest1__{char_id}.json"

        # T1b-Messgrenze (STOP-BOUNDARY §3.3-Fix): VOLLSTAENDIGER Byte-Copy
        # (nicht nur Hash) VOR dem ersten Request -- eigener Capture-
        # Schritt, unabhaengig von jedem spaeteren `_export_tree`.
        sha_guest_original_before_request = r4._sha256(guest_figure_path)
        r4._export_file(szene, guest_figure_path, "before/valid_original_pre_request.json")
        bytes_guest_original_before_request = guest_figure_path.read_bytes()

        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (T1b, gueltiger Fall)."], calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": "local-guest1",
            },
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r4._utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(r4._REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)

        initial_guest = r4._drain(out_f, settle=0.6, overall=10.0)
        assert initial_guest, "T1b: Gast-Terminal hat keinen Startbanner gesendet."

        r4._send_op(proc, "tisch-anbieten mesaT1b")
        time.sleep(0.6)
        r4._send_guest(in_f, "tisch-anfragen mesaT1b")
        after_request = r4._drain(out_f, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaT1b' gestellt" in l for l in after_request), after_request
        r4._send_op(proc, "tisch-annehmen mesaT1b guest1")
        time.sleep(0.6)
        r4._send_op(proc, "tisch-start mesaT1b")

        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich sichere das Lager.")
        post_answer = r4._drain(out_f, settle=0.6, overall=10.0)
        assert "Unbekannte Auswahl" not in "".join(post_answer), post_answer

        r4._send_op(proc, "tisch-start mesaT1b")
        time.sleep(0.6)
        r4._send_op(proc, "tisch-anbieten mesaT1b-retry")
        time.sleep(0.6)
        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r4._utc(time.time())
        in_f.close()
        out_f.close()
        r4._record_background_run(
            szene, "t1b_operator_guest_round_stop_race", argv, str(r4._REPO_ROOT),
            utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
        )
        assert proc.returncode == 0, f"T1b: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
        assert "[Zuschauer][SL] SL-Antwort auf Anker (T1b, gueltiger Fall)." in stdout_text, stdout_text
        assert "Tischstart abgelehnt: Tisch 'mesaT1b' ist geschlossen" in stdout_text, stdout_text
        assert "Tisch 'mesaT1b-retry' offen" in stdout_text, stdout_text

        table_id = "local-guest1"
        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)

        fresh_data_dir = op_data / "guests" / "guest1"
        fresh_argv = [
            sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(fresh_data_dir),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        fresh = r4._run_real_subprocess(
            szene, "t1b_fresh_guest_process_reads_and_requests", fresh_argv,
            cwd=str(r4._REPO_ROOT), input="s\ntisch-suchen\ntisch-anfragen mesaT1b-retry\nbeenden\n",
            env=r4._clean_env(),
        )
        assert fresh.returncode == 0, f"T1b: frischer Gastprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        assert "Anfrage an Tisch 'mesaT1b-retry' gestellt" in fresh.stdout, fresh.stdout

        after_fresh_bytes = guest_figure_path.read_bytes()
        after_fresh_sha = r4._sha256(guest_figure_path)
        assert after_fresh_bytes == bytes_guest_original_before_request, (
            "T1b: die private Rueckgabe des gueltigen Originals ist NICHT bytegleich zum vor dem "
            "ersten Request gesicherten Byte-Copy."
        )
        assert after_fresh_sha == sha_guest_original_before_request

        r4._export_tree(szene, run_dir, "run")
        r4._export_tree(szene, guest_catalog, "guest_catalog")
        r4._export_file(szene, calls_log, "gm_calls.jsonl")
        r4._write_export_json(szene, "inventory.json", {
            "before": {
                "guest_original_sha256": sha_guest_original_before_request,
                "guest_original_bytes": len(bytes_guest_original_before_request),
                "capture_form": "shutil.copyfile (voller Byte-Copy, nicht nur sha256) VOR dem ersten Request",
            },
            "after": {"guest_original_sha256_private_return": after_fresh_sha},
            "notes": [
                "Ergaenzt STOP-BOUNDARY.md §3.3: R4 sicherte an dieser Messgrenze nur den Hash "
                "(drive_r4_evidence_2026_11_04.py:381); der erste volle _export_tree-Aufruf lag "
                "danach erst nach Abbruch/frischem Gastleser. Hier: voller Byte-Copy UNMITTELBAR "
                "nach dem Seeden, VOR 'tisch-anbieten'/'tisch-start' (also vor dem ersten GM-Request).",
            ],
        })


# ───────────────────────── t1c: wirklich offener Personaaufruf ────────────

def run_family_t1c() -> None:
    """STOP-BOUNDARY §3.4 (erster Teil): `D:510-517` (R4) erreicht nur
    `read_admission_block(route="persona-route", ...)` NACH dem bereits
    gesetzten Tisch-Stop -- kein offener Aufruf, keine echte Persona-
    Antwort. Dieser Treiber baut den echten Fall: `guest1` (eigene Figur)
    wird Leader (Betreiber `operator1` ohne Figur), lädt über die normale
    `_cmd_local_round`-Importschleife die EIGENE bestätigte Persona
    `t1cpersona` ein (`community-operator1`). Die Einladungs-Annahme (Call 1
    am Persona-Double) ist sofort; der anschließende Persona-Importturn
    (Call 2, `core/runtime.py:act` -> `_admitted_decision("persona_decision",
    ...)` -> `PersonaApiDriver.decide()`) ist der TATSÄCHLICH offene Aufruf
    -- der Double schreibt während dieses offenen Calls `/stop` in die echte
    Kontroll-FIFO (identische Technik zu `_r4_gm_double._run_stop_race`,
    hier an der Persona-HTTP-Grenze) und liefert die späte Antwort erst nach
    dem durabel bestätigten Tisch-Stop. `act()` ruft UNMITTELBAR danach
    erneut `_check_gate()` auf ("F3: zwischen Persona-Request und
    GM-Request") -- das fängt die späte, korrekt verbuchte Antwort VOR dem
    GM-Submit ab: kein neuer Spielzug, keine Publikation."""
    szene = "t1c"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        r4.write_test_profile(run_dir, max_turns=200)

        # guest1: regulaer gueltige Figur, wird mangels eigener Figur des
        # Betreibers automatisch zum spielenden Leader (tui.py:_cmd_table_
        # start, "own_figure is None and guest_tokens").
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        guest_char_id = "chrono-t1c-guest"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", guest_char_id, "fixture-t1c-guest-001")

        # t1cpersona: EIGENE bestaetigte Persona von operator1 -- ZWEI
        # getrennte, beide ECHTE Produktschreibwege:
        # (1) PersonaState-Bootstrap (`community-operator1`, `bootstrap_
        #     community`) -- macht die Persona ueber `_known_ai_overview()`
        #     als EIGENEN bestaetigten Bestand sichtbar (Vorbedingung fuer
        #     `tisch-anfragen-persona`/die 'persona:'-Praefix-Erkennung in
        #     `_cmd_table_start`).
        # (2) Eine "Figur" direkt unter OPERATOR1s EIGENEN Wurzeln
        #     (op_data/onboarding, op_data/catalog -- NICHT guest1s
        #     getrennte Gastwurzel) -- `_resolve_member("t1cpersona")`
        #     (operator1-Session) braucht diesen Onboarding-Eintrag, um die
        #     Persona ueberhaupt als einladbaren Gast aufzuloesen (identische
        #     Autoritaet wie bei jedem Menschen, s. `tui.py:_resolve_member`-
        #     Docstring). KEIN Produktpatch -- derselbe Testhelfer
        #     (`_seed_guest_figure`), nur auf die Betreiberwurzel gezielt
        #     (reiner Setup-Schritt, nicht der Gegenstand der Probe).
        persona_key = "t1cpersona"
        persona_char_id = "chrono-t1c-persona"
        op_onboarding = op_data / "onboarding"
        op_catalog = op_data / "catalog"
        r4._seed_guest_figure(op_onboarding, op_catalog, persona_key, persona_char_id, "fixture-t1c-persona-001")

        from mmo_sim.core.persona_state import PersonaStateStore
        _schema_path = r4._REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
        ps_store = PersonaStateStore(schema_path=_schema_path)
        bootstrap_result = bootstrap_community(
            run_dir / "community", "community-operator1", 1,
            {persona_key: {
                "real_name": "T1c Persona", "archetype": "Test-Archetyp", "play_style": "SIMULIERT/DEMO",
                "charwunsch": "SIMULIERT/DEMO (R5-T1c-Testfixture).",
                "plays_char": {
                    "save_file": persona_char_id, "character_id": persona_char_id,
                    "name": "T1c Persona", "callsign": "T1C-PERSONA",
                },
            }},
            ps_store, states_dir, today="2026-11-05",
        )
        assert persona_key in bootstrap_result.personas_written, bootstrap_result.reason

        # GM-Double: GENAU EIN Eintrag -- der Leader-Anker (guest1), real
        # per FIFO beantwortet. KEIN Stop hier -- der Stop laeuft ueber den
        # Persona-Double (die eigentliche Probe dieser Familie).
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (T1c)."], calls_log=calls_log, stop=None,
        )
        gm_env = r4._gm_double_env(cfg_path)

        leader_id = "guest1"
        # Namensraum eines Tisches MIT eingeladenen Gaesten (tui.py:7462-
        # 7464, `_run_table_round`): `local-<leader>` wird um `-<sorted
        # invited_ids>` ergaenzt -- NICHT der Solo-`local-<leader>`-Name
        # ohne Gaeste (der bei T1a/T1b zutrifft, hier NICHT).
        table_id = f"local-{leader_id}-{persona_key}"
        invitation_offer_id = f"invite-{leader_id}-{persona_key}"
        persona_stop_cfg = {
            "after_call": 2, "kind": "table",
            "control_fifo": str(ctrl_fifo), "control_line": "/stop",
            "run_dir": str(run_dir), "table_id": table_id,
        }
        persona_responses = [
            f"ENTSCHEIDUNG offer_id={invitation_offer_id} participant_id={persona_key} "
            "decision=accept explanation=Ich bin dabei.",
            "Ich bin bereit und beobachte die Lage.",
        ]

        with PersonaStopRaceServer(persona_responses, stop_cfg=persona_stop_cfg) as persona_srv:
            env = dict(gm_env)
            env.update({
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_T1C_KEY",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-t1c",
            })

            argv = [
                sys.executable, "-B", str(r4._LAUNCHER),
                "--participant", "operator1", "--data-dir", str(op_data),
                "--run-dir", str(run_dir), "--states-dir", str(states_dir),
                "--operator-control-fifo", str(ctrl_fifo),
                "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
            ]
            utc_start = r4._utc(time.time())
            proc = subprocess.Popen(
                argv, cwd=str(r4._REPO_ROOT), env=env, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
            )
            in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
            r4._wait_for_path(ctrl_fifo)
            initial_guest = r4._drain(out_f, settle=0.6, overall=10.0)
            assert initial_guest, "T1c: Gast-Terminal hat keinen Startbanner gesendet."

            # Normale Admission: guest1 (echte Figur) UND die Persona (ueber
            # den Operator) werden beide in den Roster aufgenommen.
            r4._send_op(proc, "tisch-anbieten mesaT1c")
            time.sleep(0.6)
            r4._send_guest(in_f, "tisch-anfragen mesaT1c")
            after_guest_request = r4._drain(out_f, settle=0.6, overall=10.0)
            assert any("Anfrage an Tisch 'mesaT1c' gestellt" in l for l in after_guest_request), after_guest_request
            r4._send_op(proc, "tisch-annehmen mesaT1c guest1")
            time.sleep(0.6)
            r4._send_op(proc, f"tisch-anfragen-persona mesaT1c {persona_key}")
            time.sleep(0.6)
            r4._send_op(proc, f"tisch-annehmen mesaT1c {persona_key}")
            time.sleep(0.6)

            r4._send_op(proc, "tisch-start mesaT1c")

            # Leader-Anker (guest1, real per FIFO) -- EIN GM-Call, KEIN Stop.
            r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
            r4._deliver_guest_turn_answer(in_f, out_f, "Wir beginnen die Erkundung.")
            post_anchor = r4._drain(out_f, settle=0.8, overall=15.0)
            assert "Unbekannte Auswahl" not in "".join(post_anchor), (
                f"T1c: Leader-Ankerantwort wurde fehlgeleitet: {post_anchor}"
            )

            # Danach laeuft die Persona-Importschleife AUTOMATISCH (kein
            # weiterer Input nötig) -- Call 2 am Persona-Double loest den
            # Stop-Race aus; der Rundenaufruf kehrt ueber `_GateBlocked`
            # zurueck (kein weiterer GM-Call, keine Publikation).
            utc_end_cmd = r4._utc(time.time())
            r4._send_op(proc, "beenden")
            stdout_text, stderr_text = proc.communicate(timeout=30)
            utc_end = r4._utc(time.time())
            in_f.close()
            out_f.close()
            r4._record_background_run(
                szene, "t1c_operator_guest_persona_round_stop_race", argv, str(r4._REPO_ROOT),
                utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
            )
            assert proc.returncode == 0, f"T1c: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
            assert "Gruppe eingeladen" in stdout_text and persona_key in stdout_text, stdout_text
            assert "[Zuschauer][SL] SL-Antwort auf Anker (T1c)." in stdout_text, stdout_text

            persona_calls = list(persona_srv.calls)
            assert len(persona_calls) == 2, f"T1c: genau 2 Persona-Calls erwartet (Einladung + Importturn): {persona_calls}"

        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 1, (
            f"T1c: genau EIN GM-Call (Leader-Anker) erwartet -- der Persona-Importturn darf NIE "
            f"zum GM-Submit (zweiter GM-Call) fuehren, der Stop muss das abfangen: {gm_calls}"
        )

        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is None or decision.get("decision") != "plan_committed", decision
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "T1c: kein __plan.json -- kein neuer Spielzug/keine Publikation nach dem Stop."
        assert not final_path.exists(), "T1c: kein __final.json."

        # Request-Ledger: die SPAETE Persona-Antwort muss korrekt verbucht
        # sein (finish_received, nicht hängend/offen) -- der echte Beleg
        # für "korrekt dem Request zugeordnet und verbucht".
        requests_dir = run_dir / "requests"
        persona_decision_requests = []
        for p in sorted(requests_dir.glob("*.json")) if requests_dir.is_dir() else []:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("role") == "persona_decision" and data.get("participant") == persona_key:
                persona_decision_requests.append(data)
        assert len(persona_decision_requests) == 1, persona_decision_requests
        pdr = persona_decision_requests[0]
        assert pdr.get("state") == "accounted" and pdr.get("error") is None, pdr
        assert pdr.get("table_id") == table_id, pdr

        r4._export_tree(szene, run_dir, "run")
        r4._export_tree(szene, op_onboarding, "operator_onboarding")
        r4._export_tree(szene, op_catalog, "operator_catalog")
        r4._export_tree(szene, guest_onboarding, "guest_onboarding")
        r4._export_file(szene, calls_log, "gm_calls.jsonl")
        r4._write_export_json(szene, "persona_calls.json", persona_calls)
        r4._write_export_json(szene, "inventory.json", {
            "persona_decision_request": pdr,
            "table_stopped": stopped, "stop_reason": stop_reason,
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5, MMO_SIM_GM_TRANSPORT_DOUBLE), der "
                "Persona-Anbieter eine Grenzinjektion an der echten HTTP-Grenze "
                "(MMO_SIM_PERSONA_API_BASE_URL -> PersonaStopRaceServer) -- beide NIE Live-Modell.",
                "Call 2 am Persona-Double (persona_decision-Importturn) war WAEHREND des Stops "
                "tatsaechlich offen (Handler haengt im Stop-Race-Polling, identische Technik zu "
                "_r4_gm_double._run_stop_race) -- kein read_admission_block NACH bereits "
                "gesetztem Stop (das war die R4-Luecke).",
                "Die spaete Antwort wurde korrekt verbucht (request_ledger: state=accounted, "
                "kein error) UND fuehrte zu KEINEM GM-Submit/neuen Spielzug (gm_calls.jsonl hat "
                "genau 1 Eintrag, der Leader-Anker) UND zu KEINER Publikation (kein __plan.json/"
                "__final.json).",
            ],
        })


def main() -> int:
    run_family_t1a()
    run_family_t1b()
    run_family_t1c()
    (_RESULTS_ROOT / "MANIFEST.json").write_text(
        json.dumps(r4._MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print("=== T1a/T1b/T1c ABGESCHLOSSEN: PASS ===")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
