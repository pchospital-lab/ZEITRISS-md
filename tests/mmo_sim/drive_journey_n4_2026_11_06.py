#!/usr/bin/env python3
"""
tests/mmo_sim/drive_journey_n4_2026_11_06.py -- ZR-VOLLENDUNG-OHNE-LAN-
NACHZUG-20261106-R1, Journey-Builder (N4): zusammenhaengende Referenzreise
(A1-A9) + zwei V4-Grenzfaelle (B1/B2) am ECHTEN ausgelieferten Launcher
(`scripts/mmo_sim.py`), GM NUR als Grenzinjektion
(`MMO_SIM_GM_TRANSPORT_DOUBLE`, `tests.mmo_sim._r4_gm_double`), NIE Live-
Modell. Baut auf der battle-tested Harness aus `drive_r4_evidence_2026_11_04.py`
(FIFO-/Prozess-Helfer, GM-Double-Config) und `_r6_evidence_helpers.py`
(Manifest-Export) auf -- KEIN zweiter Admission-/Transportpfad.

Szene A (EINE Reise, operator1 OHNE eigene Figur, zwei Gast-Terminals
guest1/guest2 IM SELBEN Launcher-Prozess, `--guest-terminal` zweimal):
  A1 Start/Anschluss, A2 persoenliche Figur (guest1 Import, guest2
  Erschaffungsdialog), A3 Anfrage/Aufnahme (N1 am eigenen Gastkanal), A4
  gemeinsames Spielen (realer Leader/Roster), A5 oeffentlicher SL-Verlauf
  (N2, Antwort auf guest2s Erstbeitrag erreicht guest2), A6 regulaerer
  Abschluss, A7 Mitnehmen/Wiederkommen (neue Prozesse + Folgeangebot), A8
  unangenommener Erstentwurf (guest3, separat isoliert), A9 V1-Solo eng.

Szene B1 (trägt N3): Betreiber-Kontrollkanal waehrend offenem GM-Call
(Liveness via `/zuschauer`), dann bestaetigter Verwurf VOR jeder Annahme
ueber `/abbrechen` am eigenen Spielzug-Prompt des Leiters (operator1 ruft
`tisch-start`, daher landet die EndOfInput-Behandlung in GENAU dessen
`run()`-Dispatcher) -- Meldung "bestaetigter Verwurf", NICHT "sicher
pausiert".

Szene B2: verbindliche Annahme (Plan-Pin + Primaersave), gezielte
Unterbrechung ueber die VORHANDENE Testnaht
(`_r4_launcher_hardexit_before_reflection.py`, bindet `scripts.mmo_sim`
unveraendert, `os._exit()` NACH Plan-Pin/VOR Reflexion), GETRENNTER NEUER
Launcherprozess bindet denselben offenen Abschluss ueber den normalen
`tisch-start`-Fortsetzenweg, regulaere Fertigstellung, kein Rollback/keine
Doppelwirkung, danach wirklich nutzbare persoenliche Fassung.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
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
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path("/home/altair/zr-vollendung-20261106/r3-nachzug/worker/evidence/journey-n4")


def _rewrite_gm_double_responses(cfg_path: Path, *, responses: list[str], calls_log: Path, stop=None) -> None:
    """Der GM-Double liest `MMO_SIM_R4_GMDOUBLE_CONFIG` bei JEDEM
    `factory(table_id)`-Aufruf frisch von Platte (`_r4_gm_double.build`,
    kein Cache) -- jede neue `_R4GmDoubleTransport`-Instanz (eigener
    `table_id`/`onboarding_chat_id`) startet mit einer FRISCHEN Kopie der
    `responses`-Liste. Erschaffungsdialog (eigene Chat-ID) und Tischrunde
    (`table.table_id`) sind daher ZWEI unabhaengige Instanzen -- diese
    Funktion schreibt die Konfigdatei zwischen den Phasen neu, damit jede
    Phase ihre EIGENE, bei Index 0 beginnende Antwortliste bekommt (keine
    neue Produktsemantik, reine Treiber-Choreografie auf derselben Datei)."""
    r4._write_gm_double_config(cfg_path, responses=responses, calls_log=calls_log, stop=stop)


def run_scene_a() -> dict:
    """A1-A9 (siehe Moduldocstring). Gibt ein Dict mit allen fuer den
    Report benoetigten Rohdaten zurueck (Transkripte, Pfade, Inventare)."""
    out_dir = _OUT_ROOT / "A_journey"
    mf = r6.Manifest(out_dir)
    evidence: dict = {"steps": {}}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_a, out_fifo_a = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        in_fifo_b, out_fifo_b = fifo_dir / "guest2_in.fifo", fifo_dir / "guest2_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        host_onboarding = op_data / "onboarding"
        host_catalog = op_data / "catalog"
        guest1_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest1_catalog = op_data / "guests" / "guest1" / "catalog"
        guest2_onboarding = op_data / "guests" / "guest2" / "onboarding"
        guest2_catalog = op_data / "guests" / "guest2" / "catalog"

        char_id_a = "CHR-J4-GUESTA"
        char_id_b = "CHR-J4-GUESTB"

        # ── A2 (guest2-Teil): Erschaffungsdialog braucht EIGENE
        # Antwortliste (eigene Chat-ID, s. Docstring _rewrite_gm_double_
        # responses). q1/q2 sind frei gewaehlter Double-Text -- der
        # Erschaffungsdialog endet, sobald ein gueltiger Charblock
        # zurueckkommt, unabhaengig vom Wortlaut der Fragen.
        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr praegender Ursprung?"
        guest2_creation_block = full_v7_save(char_id_b, name="GuestB", save_id="fixture-j4-guest2-001")
        final_creation_content = "```json\n" + json.dumps(guest2_creation_block, ensure_ascii=False) + "\n```"
        _rewrite_gm_double_responses(
            cfg_path, responses=[q1, q2, final_creation_content], calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_a}:{out_fifo_a}",
            "--guest-terminal", f"guest2:{in_fifo_b}:{out_fifo_b}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_fa, out_fa = r4._open_guest_fifo_pair(in_fifo_a, out_fifo_a)
        in_fb, out_fb = r4._open_guest_fifo_pair(in_fifo_b, out_fifo_b)

        # ── A1: Start/Anschluss -- je Gast eigener Startbanner, eigener
        # Ein-/Ausgabekanal.
        initial_a = r4._drain(out_fa, settle=0.6, overall=10.0)
        initial_b = r4._drain(out_fb, settle=0.6, overall=10.0)
        assert initial_a, "A1: guest1 hat keinen Startbanner erhalten."
        assert initial_b, "A1: guest2 hat keinen Startbanner erhalten."
        evidence["steps"]["A1"] = {"argv": argv, "initial_a": initial_a, "initial_b": initial_b}

        # ── A2a: guest1 importiert eine gueltige EIGENE Figur ueber den
        # normalen Import ('i', JSON-Text, 'ENDE', Bestaetigung 'j').
        guest1_own_block = full_v7_save(char_id_a, name="GuestA", save_id="fixture-j4-guest1-001")
        guest1_block_json = json.dumps(guest1_own_block, ensure_ascii=False)
        r4._send_guest(in_fa, "i")
        r4._wait_for_marker(out_fa, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_fa, guest1_block_json)
        r4._send_guest(in_fa, "ENDE")
        preview_a = r4._wait_for_marker(out_fa, f"char_id={char_id_a}", overall=20.0)
        assert "WARNUNG" not in "".join(preview_a), preview_a
        r4._send_guest(in_fa, "j")
        accept_a = r4._wait_for_marker(out_fa, "Uebernahme abgeschlossen", overall=20.0)
        assert f"action=register_new char_id={char_id_a}" in "".join(accept_a), accept_a
        after_import_a = r4._drain(out_fa, settle=0.6, overall=5.0)

        # ── A2b: guest2 hat noch keine Figur -- fragt persoenliche
        # Erschaffung an; der Betreiber gibt GENAU DIESE Anfrage frei.
        r4._send_guest(in_fb, "gast-erschaffung-anfragen operator1")
        request_b = r4._drain(out_fb, settle=0.6, overall=10.0)
        r4._send_op(proc, "gast-erschaffung-annehmen guest2")
        time.sleep(0.6)
        grant_b = creation_grants.grant_status(run_dir, "guest2")
        assert grant_b["status"] == "approved", grant_b

        r4._send_guest(in_fb, "gast-erschaffung-dialog operator1")
        r4._wait_for_marker(out_fb, f"[SL] {q1}", overall=15.0)
        r4._send_guest(in_fb, "Nadia")
        r4._wait_for_marker(out_fb, f"[SL] {q2}", overall=15.0)
        r4._send_guest(in_fb, "Eine verlorene Ausgrabungscrew.")
        creation_tail_b = r4._wait_for_marker(out_fb, "Gast-Erschaffung abgeschlossen", overall=20.0)
        joined_creation_b = "".join(creation_tail_b)
        guest2_catalog_entries = catalog.list_for_participant(guest2_catalog, "guest2")
        assert len(guest2_catalog_entries) == 1 and guest2_catalog_entries[0].chrononaut_id == char_id_b, (
            f"A2: guest2 sollte nach dem Erschaffungsdialog genau EINEN Katalogeintrag haben: "
            f"{guest2_catalog_entries}"
        )
        evidence["steps"]["A2"] = {
            "guest1": {
                "char_id": char_id_a, "preview": preview_a, "accept": accept_a,
                "after_import": after_import_a,
            },
            "guest2": {
                "char_id": char_id_b, "request": request_b, "grant": grant_b,
                "creation_tail": joined_creation_b,
            },
        }

        # ── Jetzt die Antwortliste fuer die TISCHRUNDE neu schreiben
        # (eigene, bei Index 0 beginnende Instanz fuer table.table_id).
        sl1, sl2, sl3 = "SL-Antwort auf guest1 Zug 1.", "SL-Antwort auf guest2s Erstbeitrag.", "SL-Antwort auf guest1 Zug 2."
        debrief_a = full_v7_save(char_id_a, name="GuestA", save_id="fixture-j4-guest1-002", level=2)
        debrief_b = full_v7_save(char_id_b, name="GuestB", save_id="fixture-j4-guest2-002", level=2)
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_b) + "\n```\n" + COMPLETION_MARKER
        )
        _rewrite_gm_double_responses(
            cfg_path, responses=[sl1, sl2, sl3, debrief_text], calls_log=calls_log,
        )

        # ── A3: Anfrage/Aufnahme -- beide Gaeste finden/fragen den Tisch
        # an, der Betreiber nimmt BEWUSST beide an.
        table_key = "mesaJourneyA"
        r4._send_guest(in_fa, "tisch-suchen")
        r4._drain(out_fa, settle=0.4, overall=5.0)
        r4._send_op(proc, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_fa, f"tisch-anfragen {table_key}")
        request_a = r4._drain(out_fa, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{table_key}' gestellt" in l for l in request_a), request_a
        r4._send_guest(in_fb, "tisch-suchen")
        r4._drain(out_fb, settle=0.4, overall=5.0)
        r4._send_guest(in_fb, f"tisch-anfragen {table_key}")
        request_b_table = r4._drain(out_fb, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{table_key}' gestellt" in l for l in request_b_table), request_b_table

        r4._send_op(proc, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        r4._send_op(proc, f"tisch-annehmen {table_key} guest2")
        time.sleep(0.6)
        roster_after_accept = table_admission.roster(run_dir, table_key)
        assert {"guest1", "guest2"} <= set(roster_after_accept["roster"]), roster_after_accept
        evidence["steps"]["A3"] = {
            "request_a": request_a, "request_b": request_b_table, "roster_after_accept": roster_after_accept,
        }

        # ── A4 (traegt N1): Betreiber startet den Tisch. operator1 hat
        # keine eigene Figur -> das erste angenommene Rostermitglied
        # (guest1) wird automatisch zum spielenden Leader (tui.py
        # `_cmd_table_start`, `force_operator_mode`); guest1 braucht
        # daher KEINE Rundenbeitritt-Bestaetigung (guest_id == leader_id
        # wird in der Einladungsschleife uebersprungen, tui.py ~7367). NUR
        # guest2 (echter zweiter Mensch) wird ueber `guest_io.
        # _readline_with_controls` auf IHREM EIGENEN registrierten
        # Terminal (`_table_guest_terminals["guest2"]`, NICHT die
        # Betreiber-Tastatur) nach "[j/n]" gefragt -- das ist der reale
        # N1-Beleg. `_fifo_input_fn` schreibt den Promptstring NIE in die
        # Ausgabe-FIFO (s. Moduldocstring von drive_r4), die Zustimmung
        # kann daher nur durch gezieltes, blindes Senden auf GENAU guest2s
        # eigenem FIFO (nicht auf operator1s stdin, nicht auf guest1s
        # FIFO) real erbracht werden.
        r4._send_op(proc, f"tisch-start {table_key}")
        time.sleep(1.0)
        r4._send_guest(in_fb, "j")
        consent_a = "kein Konsentprompt fuer guest1 (ist der Leader, uebersprungen in der Einladungsschleife)"
        consent_b = "blind 'j' auf guest2-FIFO gesendet (Promptstring wird nie in die Ausgabe-FIFO geschrieben)"

        # Leader (guest1, da operator1 keine eigene Figur hat) spielt
        # Zug 1 -> GM-Call 1 (sl1). Die Antwort wird NICHT sofort an sie
        # zurueckgedruckt -- der SL-Verlaufscursor pro Kanal (tui.py
        # `displayed_sl_count_by_channel`) flusht erst beim NAECHSTEN
        # `decide()`-Aufruf DIESES Kanals (empirisch verifiziert, s.
        # Report).
        r4._wait_for_marker(out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_fa, out_fa, "Ich erkunde die Ruinen.")

        # guest2 Erstbeitrag (ueber Leader an die SL) -> GM-Call 2 (sl2).
        first_b = r4._wait_for_marker(out_fb, "Empfaenger:", overall=25.0)
        r4._deliver_guest_turn_answer(in_fb, out_fb, "Ich sichere den Eingang.")
        evidence["steps"]["A4"] = {
            "consent_a": consent_a, "consent_b": consent_b, "first_b_prompt": first_b,
        }

        # Leaders NAECHSTER decide()-Aufruf (ihr Zug 2) flusht den seit
        # ihrem letzten Flush aufgelaufenen SL-Verlauf (sl1 UND sl2) auf
        # IHREN Kanal, bevor er ihren naechsten Prompt zeigt.
        leader_turn2 = r4._wait_for_marker(out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        joined_leader_turn2 = "".join(leader_turn2)
        assert f"[SL] {sl1}" in joined_leader_turn2, joined_leader_turn2
        assert f"[SL] {sl2}" in joined_leader_turn2, joined_leader_turn2
        r4._deliver_guest_turn_answer(in_fa, out_fa, "Ich rufe die Gruppe zusammen.")

        # ── A5 (N2): guest2s NAECHSTER decide()-Aufruf (ihr zweiter
        # Beitrag) flusht GENAU sl2 (die Antwort auf IHREN EIGENEN
        # Erstbeitrag) auf IHREN EIGENEN Kanal -- NICHT vom Leader
        # "verbraucht" (der Leader hat sl2 oben zusaetzlich UND
        # UNABHAENGIG auf seinem eigenen Kanal gesehen, pro-Kanal-Cursor).
        guest2_sees_own_answer = r4._wait_for_marker(out_fb, "Empfaenger:", overall=25.0)
        joined_guest2_sees = "".join(guest2_sees_own_answer)
        assert f"[SL] {sl2}" in joined_guest2_sees, joined_guest2_sees
        evidence["steps"]["A5"] = {"guest2_sees_own_answer": guest2_sees_own_answer}
        # guest2 zweiter Beitrag -> Tischabsprache (kein GM-Call).
        r4._send_guest(in_fb, "Wir ziehen weiter.")
        time.sleep(0.6)

        # Leader Zug 3 -> GM-Call 4 (Debrief/COMPLETION_MARKER).
        leader_turn3 = r4._wait_for_marker(out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert f"[SL] {sl3}" in "".join(leader_turn3), leader_turn3
        r4._deliver_guest_turn_answer(in_fa, out_fa, "Ich schliesse den Abschnitt ab.")

        # ── A6: regulaerer Abschluss -- freiwillige lokale Notiz je
        # Mitglied (Leader zuerst, dann Gast), KEINE Betreiberfigur.
        note_a = r4._wait_for_marker(out_fa, "eigene lokale Notiz", overall=25.0)
        r4._deliver_guest_turn_answer(in_fa, out_fa, "Abschlussnotiz guest1: gut gelaufen.")
        note_b = r4._wait_for_marker(out_fb, "eigene lokale Notiz", overall=25.0)
        r4._deliver_guest_turn_answer(in_fb, out_fb, "Abschlussnotiz guest2: ebenfalls gut.")

        record = table_admission.load_record(run_dir, table_key)
        section_id = record["section_id"]
        completion_section_id = f"{section_id}-section"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        r4._wait_for_path(final_path, overall=25.0)
        finish_tail_a = r4._drain(out_fa, settle=0.6, overall=8.0)
        finish_tail_b = r4._drain(out_fb, settle=0.6, overall=8.0)
        section = store.Table.load(run_dir, section_id)
        assert section.status == "closed", section.status
        assert set(section.members) == {"guest1", "guest2"}, section.members
        evidence["steps"]["A6"] = {
            "note_a": note_a, "note_b": note_b,
            "finish_tail_a": finish_tail_a, "finish_tail_b": finish_tail_b,
            "section_id": section_id, "final_exists": final_path.exists(),
        }

        # KEINE Betreiberfigur: operator1 hat keinen Katalogeintrag.
        assert catalog.list_for_participant(host_catalog, "operator1") == [], (
            "A6: der Betreiber darf KEINE eigene Figur bekommen haben."
        )

        # Privater Rueckkanal: BEIDE Gaeste bekommen ihre Endfassung in
        # die EIGENE private Ablage zurueckgeschrieben.
        guest1_private = onboarding.peek(guest1_onboarding, "guest1")
        guest2_private = onboarding.peek(guest2_onboarding, "guest2")
        assert guest1_private is not None and guest1_private.final_save is not None, "A6: guest1 kein Rueckkanal."
        assert guest2_private is not None and guest2_private.final_save is not None, "A6: guest2 kein Rueckkanal."
        reloaded_a = guest1_private.final_save["characters"][0]
        reloaded_b = guest2_private.final_save["characters"][0]
        assert reloaded_a["id"] == char_id_a and reloaded_a["lvl"] == 2, reloaded_a
        assert reloaded_b["id"] == char_id_b and reloaded_b["lvl"] == 2, reloaded_b

        # identischer Retry-Tischstart (Operator-stdout) -- keine zweite Wirkung.
        r4._send_op(proc, f"tisch-start {table_key}")
        time.sleep(0.6)

        utc_end_main = r6.utc(time.time())
        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_fa.close(); out_fa.close(); in_fb.close(); out_fb.close()
        assert proc.returncode == 0, f"A: Launcher-Lauf gescheitert: {stderr_text}"
        assert "geschlossen" in stdout_text, (
            f"A7-Vorbereitung: identischer Tischstart nach Abschluss haette 'geschlossen' melden "
            f"sollen (Operator-stdout tail): {stdout_text[-600:]!r}"
        )

        r6.write_process_result(
            out_dir, "main_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "main_launcher", aussage="a1_a6_main_launcher_transcript", run_id="A_main",
            teilnehmer_figur="guest1+guest2", tisch_abschnitt=f"{table_key}/{section_id}",
        )

        evidence["main_launcher"] = {
            "argv": argv, "cwd": str(_REPO_ROOT), "utc_start": utc_start, "utc_end": utc_end,
            "exit_code": proc.returncode, "stdout_text": stdout_text, "stderr_text": stderr_text,
        }
        evidence["identifiers"] = {
            "participant_operator": "operator1", "participant_guest1": "guest1",
            "char_id_guest1": char_id_a, "participant_guest2": "guest2", "char_id_guest2": char_id_b,
            "table_key": table_key, "section_id": section_id,
        }
        evidence["paths"] = {
            "run_dir": str(run_dir), "states_dir": str(states_dir), "op_data": str(op_data),
            "guest1_onboarding": str(guest1_onboarding), "guest1_catalog": str(guest1_catalog),
            "guest2_onboarding": str(guest2_onboarding), "guest2_catalog": str(guest2_catalog),
            "final_path": str(final_path),
        }

        # ───────────────── A7: Mitnehmen/Wiederkommen ─────────────────
        # ECHTE neue Prozesse (literaler Launcher, --no-host-capable) auf
        # den PRIVATEN Gastwurzeln -- laden+exportieren die persoenliche
        # Endfassung ueber den normalen Produktweg.
        a7_results = {}
        for guest_id, guest_root, want_char_id in (
            ("guest1", op_data / "guests" / "guest1", char_id_a),
            ("guest2", op_data / "guests" / "guest2", char_id_b),
        ):
            # 'e' ist der direkte Hauptmenue-Shortcut fuer Export (s.
            # spielerstart.md "Vorhandene Tastenkuerzel") -- schreibt OHNE
            # weitere Pfadabfrage sofort nach `<data_dir>/exports/
            # <participant_id>.json` (empirisch verifiziert). KEIN Umweg
            # ueber das 'charaktere'-Untermenue (dessen `[3]` -- nicht 'e'
            # -- Export heisst; 'e' dort waere 'Unbekannte Auswahl').
            export_path = guest_root / "exports" / f"{guest_id}.json"
            argv_reload = [
                sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
                "--participant", guest_id, "--data-dir", str(guest_root),
                "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            ]
            utc_s = r6.utc(time.time())
            res = subprocess.run(
                argv_reload, cwd=str(_REPO_ROOT), env=r4._clean_env(),
                input="fortsetzen\ne\nbeenden\n",
                capture_output=True, text=True, timeout=30,
            )
            utc_e = r6.utc(time.time())
            a7_results[guest_id] = {
                "argv": argv_reload, "utc_start": utc_s, "utc_end": utc_e,
                "exit_code": res.returncode, "stdout_text": res.stdout, "stderr_text": res.stderr,
                "export_exists": export_path.exists(),
            }
            r6.write_process_result(
                out_dir, f"a7_reload_{guest_id}", argv=argv_reload, cwd=str(_REPO_ROOT),
                utc_start=utc_s, utc_end=utc_e, exit_code=res.returncode,
                stdout_text=res.stdout, stderr_text=res.stderr,
            )
            mf.record_process_files(
                f"a7_reload_{guest_id}", aussage=f"a7_{guest_id}_cold_reload_and_export",
                run_id="A7", teilnehmer_figur=guest_id,
            )
            assert res.returncode == 0, f"A7: {guest_id}-Reload gescheitert: {res.stderr}"
            assert export_path.exists(), (
                f"A7: {guest_id}-Export wurde NICHT geschrieben (erwartet unter {export_path}): "
                f"{res.stdout[-800:]!r}"
            )
            mf.export_file(
                export_path, f"{guest_id}_export.json", aussage=f"a7_{guest_id}_export_body",
                run_id="A7", teilnehmer_figur=guest_id,
            )
            exported = json.loads(export_path.read_text(encoding="utf-8"))
            exp_char = exported["characters"][0]
            assert exp_char["id"] == want_char_id and exp_char["lvl"] == 2, exp_char

        # Folgeaktion: neues Angebot mit den aktuellen (lvl-2-)Fassungen --
        # NEUER Betreiberprozess, guest1 fragt an UND wird angenommen
        # (reicht als EINE sinnvolle Folgeaktion, kein zweiter Abschnitt).
        in_fifo_a2, out_fifo_a2 = fifo_dir / "guest12_in.fifo", fifo_dir / "guest12_out.fifo"
        argv_follow = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_a2}:{out_fifo_a2}",
        ]
        utc_s2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv_follow, cwd=str(_REPO_ROOT), env=r4._clean_env(), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_fa2, out_fa2 = r4._open_guest_fifo_pair(in_fifo_a2, out_fifo_a2)
        r4._drain(out_fa2, settle=0.6, overall=10.0)
        follow_table_key = "mesaJourneyA_folge"
        r4._send_op(proc2, f"tisch-anbieten {follow_table_key}")
        time.sleep(0.6)
        r4._send_guest(in_fa2, f"tisch-anfragen {follow_table_key}")
        follow_request = r4._drain(out_fa2, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{follow_table_key}' gestellt" in l for l in follow_request), follow_request
        r4._send_op(proc2, f"tisch-annehmen {follow_table_key} guest1")
        time.sleep(0.6)
        follow_roster = table_admission.roster(run_dir, follow_table_key)
        assert "guest1" in follow_roster["roster"], follow_roster
        follow_guest_current = json.loads(
            (run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8")
        )
        assert follow_guest_current["characters"][0]["lvl"] == 2, (
            "A7: die Folgeaktion muss die AKTUELLE (lvl-2-)Fassung tragen, nicht den alten "
            f"Erststand: {follow_guest_current['characters'][0]}"
        )
        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_e2 = r6.utc(time.time())
        in_fa2.close(); out_fa2.close()
        assert proc2.returncode == 0, f"A7: Folgeangebots-Prozess gescheitert: {stderr2}"
        r6.write_process_result(
            out_dir, "a7_follow_offer", argv=argv_follow, cwd=str(_REPO_ROOT),
            utc_start=utc_s2, utc_end=utc_e2, exit_code=proc2.returncode,
            stdout_text=stdout2, stderr_text=stderr2,
        )
        mf.record_process_files(
            "a7_follow_offer", aussage="a7_follow_up_offer_with_current_version",
            run_id="A7", teilnehmer_figur="guest1", tisch_abschnitt=follow_table_key,
        )
        evidence["steps"]["A7"] = {
            "reloads": a7_results, "follow_request": follow_request,
            "follow_roster": follow_roster, "follow_guest_current_lvl": 2,
        }

        # ───────────────── A8: unangenommener Erstentwurf ─────────────
        # Eigene isolierte Ablage -- EIN zusaetzlicher Gast (guest3) fragt
        # eine persoenliche Erschaffung an, der Betreiber lehnt die
        # Anfrage BEWUSST ab (nie angenommen) -- Vorher-/Nachherinventar
        # zeigt KEINEN gueltigen Reise-Save.
        a8_root = Path(tempfile.mkdtemp(prefix="j4-a8-"))
        a8_op_data = a8_root / "op_data"
        a8_run_dir = a8_root / "run"
        a8_states_dir = a8_root / "states"
        a8_fifo_dir = a8_root / "fifos"
        a8_fifo_dir.mkdir(parents=True)
        in_fifo_c, out_fifo_c = a8_fifo_dir / "guest3_in.fifo", a8_fifo_dir / "guest3_out.fifo"
        write_test_profile(a8_run_dir, max_turns=50)
        guest3_catalog = a8_op_data / "guests" / "guest3" / "catalog"
        guest3_current_path = a8_run_dir / "current_saves" / "guest3.json"
        argv_a8 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(a8_op_data),
            "--run-dir", str(a8_run_dir), "--states-dir", str(a8_states_dir),
            "--guest-terminal", f"guest3:{in_fifo_c}:{out_fifo_c}",
        ]
        utc_s8 = r6.utc(time.time())
        proc8 = subprocess.Popen(
            argv_a8, cwd=str(_REPO_ROOT), env=r4._clean_env(), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_fc, out_fc = r4._open_guest_fifo_pair(in_fifo_c, out_fifo_c)
        r4._drain(out_fc, settle=0.6, overall=10.0)
        before_catalog = catalog.list_for_participant(guest3_catalog, "guest3")
        assert before_catalog == [], before_catalog
        r4._send_guest(in_fc, "gast-erschaffung-anfragen operator1")
        request_c = r4._drain(out_fc, settle=0.6, overall=10.0)
        grant_before_c = creation_grants.grant_status(a8_run_dir, "guest3")
        assert grant_before_c["status"] == "requested", grant_before_c
        r4._send_op(proc8, "gast-erschaffung-ablehnen guest3")
        time.sleep(0.6)
        reject_tail_c = r4._drain(out_fc, settle=0.6, overall=8.0)
        grant_after_c = creation_grants.grant_status(a8_run_dir, "guest3")
        assert grant_after_c["status"] != "approved", grant_after_c
        after_catalog = catalog.list_for_participant(guest3_catalog, "guest3")
        assert after_catalog == [], (
            f"A8: ein unangenommener Erstentwurf darf KEINEN Katalogeintrag erzeugen: {after_catalog}"
        )
        assert not guest3_current_path.exists(), (
            "A8: ein unangenommener Erstentwurf darf KEINEN gueltigen Reise-Save (current_saves) erzeugen."
        )
        r4._send_op(proc8, "beenden")
        stdout8, stderr8 = proc8.communicate(timeout=30)
        utc_e8 = r6.utc(time.time())
        in_fc.close(); out_fc.close()
        assert proc8.returncode == 0, f"A8: Launcher-Lauf gescheitert: {stderr8}"
        r6.write_process_result(
            out_dir, "a8_rejected_creation_draft", argv=argv_a8, cwd=str(_REPO_ROOT),
            utc_start=utc_s8, utc_end=utc_e8, exit_code=proc8.returncode,
            stdout_text=stdout8, stderr_text=stderr8,
        )
        mf.record_process_files(
            "a8_rejected_creation_draft", aussage="a8_unaccepted_first_draft_no_valid_save",
            run_id="A8", teilnehmer_figur="guest3",
        )
        evidence["steps"]["A8"] = {
            "before_catalog": before_catalog, "request_c": request_c,
            "grant_before": grant_before_c, "reject_tail": reject_tail_c,
            "grant_after": grant_after_c, "after_catalog": after_catalog,
            "guest3_current_exists": guest3_current_path.exists(),
        }

        # ───────────────── A9: V1-Solo eng ─────────────────
        # Eigene isolierte Ablage -- EIN Mensch, KEIN Tisch, KEIN Gast:
        # Host/Figur(Import)/Solo-Runde/Save/Fortsetzen ueber zwei echte
        # Prozesse (kein blosser Boot-/Tischmenue-Screen).
        a9_root = Path(tempfile.mkdtemp(prefix="j4-a9-"))
        a9_data_dir = a9_root / "data"
        a9_run_dir = a9_root / "run"
        a9_states_dir = a9_root / "states"
        write_test_profile(a9_run_dir, max_turns=50)
        solo_char_id = "CHR-J4-SOLO"
        solo_save = full_v7_save(solo_char_id, name="SoloHeld", save_id="fixture-j4-solo-001")
        solo_calls_log = a9_root / "gm_calls.jsonl"
        solo_cfg = a9_root / "gmdouble_cfg.json"
        solo_sl1 = "SL-Antwort Solo Zug 1."
        solo_debrief_save = full_v7_save(solo_char_id, name="SoloHeld", save_id="fixture-j4-solo-002", level=2)
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM
        solo_debrief = "Abschnitt beendet.\n```json\n" + json.dumps(solo_debrief_save) + "\n```\n" + _CM
        r4._write_gm_double_config(solo_cfg, responses=[solo_sl1, solo_debrief], calls_log=solo_calls_log)
        solo_env = r4._gm_double_env(solo_cfg)

        argv_solo1 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "solo1", "--data-dir", str(a9_data_dir),
            "--run-dir", str(a9_run_dir), "--states-dir", str(a9_states_dir),
        ]
        utc_s9 = r6.utc(time.time())
        res9a = subprocess.run(
            argv_solo1, cwd=str(_REPO_ROOT), env=solo_env,
            input=(
                "i\n" + json.dumps(solo_save, ensure_ascii=False) + "\nENDE\nj\n"
                "l\n"
                "Ich erforsche die Umgebung.\n"
                "Ich schliesse den Abschnitt ab.\n"
                "Solo-Abschlussnotiz: alles sauber.\n"
                "beenden\n"
            ),
            capture_output=True, text=True, timeout=30,
        )
        utc_e9 = r6.utc(time.time())
        r6.write_process_result(
            out_dir, "a9_solo_proc1_create_play_save", argv=argv_solo1, cwd=str(_REPO_ROOT),
            utc_start=utc_s9, utc_end=utc_e9, exit_code=res9a.returncode,
            stdout_text=res9a.stdout, stderr_text=res9a.stderr,
        )
        mf.record_process_files(
            "a9_solo_proc1_create_play_save", aussage="a9_solo_import_play_save_real_process",
            run_id="A9", teilnehmer_figur="solo1",
        )
        assert res9a.returncode == 0, f"A9/Prozess1: {res9a.stderr}"
        assert "Unbekannte Auswahl" not in res9a.stdout, res9a.stdout

        argv_solo2 = [
            sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
            "--participant", "solo1", "--data-dir", str(a9_data_dir),
            "--run-dir", str(a9_run_dir), "--states-dir", str(a9_states_dir),
        ]
        utc_s9b = r6.utc(time.time())
        res9b = subprocess.run(
            argv_solo2, cwd=str(_REPO_ROOT), env=r4._clean_env(),
            input="fortsetzen\ns\nbeenden\n", capture_output=True, text=True, timeout=30,
        )
        utc_e9b = r6.utc(time.time())
        r6.write_process_result(
            out_dir, "a9_solo_proc2_resume", argv=argv_solo2, cwd=str(_REPO_ROOT),
            utc_start=utc_s9b, utc_end=utc_e9b, exit_code=res9b.returncode,
            stdout_text=res9b.stdout, stderr_text=res9b.stderr,
        )
        mf.record_process_files(
            "a9_solo_proc2_resume", aussage="a9_solo_real_fresh_process_resume",
            run_id="A9", teilnehmer_figur="solo1",
        )
        assert res9b.returncode == 0, f"A9/Prozess2: {res9b.stderr}"
        assert "Katalog-Eintraege: 1" in res9b.stdout, res9b.stdout
        evidence["steps"]["A9"] = {
            "proc1_stdout": res9a.stdout, "proc1_stderr": res9a.stderr,
            "proc2_stdout": res9b.stdout, "proc2_stderr": res9b.stderr,
            "solo_char_id": solo_char_id,
        }

        mf.write_json_body(
            "full_evidence.json", evidence, aussage="a_full_step_by_step_evidence_dump",
            run_id="A_full",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "A_journey", "aussage": "A1-A9 Referenzreise, siehe worker/journey-n4-report.md",
        })

    evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_b1() -> dict:
    """B1 (traegt N3): normaler Launcher + `--operator-control-fifo`
    PRAESENT und tatsaechlich genutzt (`/zuschauer`, Liveness-Beleg
    WAEHREND der Betreiber-Autoritaet aktiv ist), danach bestaetigter,
    ENDGUELTIGER Verwurf VOR jeder Abschluss-Entscheidung ueber
    '/abbrechen' am eigenen Spielzug-Prompt des Leiters. Da operator1
    (OHNE eigene Figur) selbst `tisch-start` aufruft, landet die
    `EndOfInput(reason="confirmed_discard")` GENAU in operator1s eigenem
    `run()`-Dispatcher (tui.py:9129-9147) -- Meldung "bestaetigter
    Verwurf", NICHT "sicher pausiert"."""
    out_dir = _OUT_ROOT / "B1_stop_before_commit"
    mf = r6.Manifest(out_dir)
    evidence: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo, out_fifo = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-J4-B1-GUEST"
        guest_block = full_v7_save(char_id, name="GuestB1", save_id="fixture-j4-b1-guest-001")
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (B1, bleibt offen -- keine Adoption danach)."],
            calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)
        table_key = "mesaB1"
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, "i")
        r4._wait_for_marker(out_f, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f, json.dumps(guest_block, ensure_ascii=False))
        r4._send_guest(in_f, "ENDE")
        r4._wait_for_marker(out_f, f"char_id={char_id}", overall=20.0)
        r4._send_guest(in_f, "j")
        r4._wait_for_marker(out_f, "Uebernahme abgeschlossen", overall=20.0)
        r4._drain(out_f, settle=0.5, overall=5.0)

        r4._send_op(proc, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_f, f"tisch-anfragen {table_key}")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        guest_current_before = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))

        # ── Betreiber bedient den dokumentierten tatsaechlichen
        # Kontrollkanal WAEHREND die Betreiber-Autoritaet fuer DIESE Runde
        # aktiv ist (`_OperatorControlScope` ist nur innerhalb des
        # blockierenden `_cmd_local_round`-Aufrufs aktiv) -- `/zuschauer`
        # beweist den LIVE-Kanal, OHNE den spaeteren Verwurf vorwegzunehmen.
        r4._send_op(proc, f"tisch-start {table_key}")
        time.sleep(0.8)
        ctrl_fd = os.open(str(ctrl_fifo), os.O_WRONLY)
        with os.fdopen(ctrl_fd, "w") as f:
            f.write("/zuschauer\n")
        time.sleep(0.8)

        # ── Leiter (guest1, da operator1 keine eigene Figur hat) erreicht
        # ihren Spielzug-Prompt; die GM-Antwort bleibt zunaechst offen
        # (kontrollierte Modellantwort am Rand, s. Konfigdocstring).
        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend.")
        turn1_tail = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert "SL-Antwort auf Anker" in "".join(turn1_tail), turn1_tail

        # ── VOR jeder Abschluss-Entscheidung: bestaetigter, ENDGUELTIGER
        # Verwurf ueber '/abbrechen' am eigenen Spielzug-Prompt des
        # Leiters -- dieselbe Autoritaet wie der Kontrollkanal
        # (`table_admission.request_table_stop`), hier am Leiter-Prompt
        # ausgeloest.
        r4._deliver_guest_turn_answer(in_f, out_f, "/abbrechen")
        guest_abort_lines = r4._wait_for_marker(out_f, "Abschnitt wirklich verworfen", overall=15.0)
        joined_guest_abort = "".join(guest_abort_lines)
        assert "ENDGUELTIG" in joined_guest_abort, joined_guest_abort

        tail = r4._drain(out_f, settle=0.8, overall=6.0)
        try:
            stdout_text, stderr_text = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_text, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"B1: Launcher-Lauf gescheitert (rc={proc.returncode}): {stderr_text}"

        # ── Kernbeleg N3 am realen Weg: operator1s EIGENER run()-
        # Dispatcher (sie hat 'tisch-start' selbst aufgerufen) faengt die
        # EndOfInput(reason="confirmed_discard") -- Meldung "bestaetigter
        # Verwurf", NICHT "sicher pausiert".
        assert "bestaetigter Verwurf" in stdout_text, (
            f"B1/N3: operator1s eigener run()-Dispatcher haette 'bestaetigter Verwurf' melden "
            f"muessen (NICHT EOF/Pause): {stdout_text!r}"
        )
        assert "sicher pausiert" not in stdout_text, (
            f"B1/N3: ein bestaetigter Verwurf darf NICHT als 'sicher pausiert' (EOF/Pause) "
            f"umetikettiert werden: {stdout_text!r}"
        )
        assert "Zuschauer" in stdout_text or "zuschauer" in stdout_text.lower(), (
            f"B1: der Kontrollkanal ('/zuschauer') sollte eine erkennbare Spektatoransicht gezeigt "
            f"haben: {stdout_text!r}"
        )

        decision = admission.read_table_decision(run_dir, f"local-guest1")
        assert decision is not None and decision.get("decision") == "stopped", decision
        completion_section_id = "local-guest1-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "B1: kein __plan.json -- die verspaetete Antwort darf NICHT adoptiert werden."
        assert not final_path.exists(), "B1: kein __final.json."

        # Zuvor gueltiger persoenlicher Save (der Import VOR dem
        # Tischstart) bleibt maßgeblich, UNVERAENDERT durch den Verwurf.
        guest_current_after = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))
        assert guest_current_after == guest_current_before, (
            "B1: der zuvor gueltige persoenliche Save darf durch den Verwurf NICHT veraendert worden sein."
        )

        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="b1_control_fifo_live_plus_confirmed_discard_before_commit",
            run_id="B1", teilnehmer_figur="guest1", tisch_abschnitt=f"{table_key}/local-guest1",
        )
        mf.export_tree(run_dir, "run", aussage="b1_run_dir_after_discard", run_id="B1", teilnehmer_figur="guest1")
        mf.write_json_body("io_transcript.json", {
            "guest_abort_lines": guest_abort_lines, "tail": tail, "decision": decision,
        }, aussage="b1_dialog_io_transcript", run_id="B1", teilnehmer_figur="guest1")
        mf.write_manifest()
        mf.write_summary({
            "szene": "B1_stop_before_commit", "decision": decision.get("decision"),
            "final_written": final_path.exists(), "plan_written": plan_path.exists(),
            "aussage": (
                "operator-control-fifo live genutzt (/zuschauer) WAEHREND die Betreiberautoritaet "
                "aktiv ist; danach bestaetigter, ENDGUELTIGER Verwurf VOR jeder Abschluss-Entscheidung "
                "ueber '/abbrechen' am Leiter-Spielzug-Prompt -- operator1s eigener run()-Dispatcher "
                "meldet 'bestaetigter Verwurf', NICHT 'sicher pausiert' (N3 am realen Subprozessweg)."
            ),
        })
        evidence["argv"] = argv
        evidence["utc_start"] = utc_start
        evidence["utc_end"] = utc_end
        evidence["exit_code"] = proc.returncode
        evidence["stdout_text"] = stdout_text
        evidence["stderr_text"] = stderr_text
        evidence["decision"] = decision
        evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_b2() -> dict:
    """B2: verbindliche Annahme (Plan-Pin + Primaersave real geschrieben),
    gezielte Unterbrechung ueber die VORHANDENE Testnaht
    (`_r4_launcher_hardexit_before_reflection.py`, bindet `scripts.mmo_sim`
    unveraendert, patcht NUR `SectionRuntime._collect_reflections` auf
    `os._exit(94)` -- NACH Plan-Pin/Primaersave, VOR jeder Reflexion,
    KEINE neue Produkt-Fehlerfunktion). GETRENNTER NEUER Launcherprozess
    (echter OS-Prozess, eigene PID/argv/cwd/UTC/Exit) bindet denselben
    offenen Abschluss ueber den normalen `tisch-start`-Fortsetzenweg,
    regulaere Fertigstellung (echte freiwillige Notiz), danach identischer
    Retry OHNE zweite Wirkung und ein kalter Reload der wirklich nutzbaren
    persoenlichen Fassung."""
    out_dir = _OUT_ROOT / "B2_committed_interrupt_new_process"
    mf = r6.Manifest(out_dir)
    evidence: dict = {"processes": {}}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_1, out_fifo_1 = fifo_dir / "guest1_in_1.fifo", fifo_dir / "guest1_out_1.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-J4-B2-GUEST"
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-j4-b2-guest-001")
        guest_current_path = run_dir / "current_saves" / "guest1.json"
        table_key = "mesaB2"

        debrief_save = full_v7_save(char_id, name="GuestB2", save_id="fixture-j4-b2-guest-002", level=2)
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM2
        debrief_text = "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\n" + _CM2
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        # ── Prozess 1 (gebundene Skriptdatei, ECHTER launcher.main()
        # importiert, Monkeypatch GENAU an der Abbruch-Grenze): verbindliche
        # Annahme -- Plan-Pin + Primaersave werden real geschrieben, dann
        # os._exit(94) VOR jeder Reflexion.
        argv1 = [
            sys.executable, "-B", str(r4._HARDEXIT_BEFORE_REFLECTION),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_1}:{out_fifo_1}",
        ]
        utc_start1 = r6.utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r4._open_guest_fifo_pair(in_fifo_1, out_fifo_1)
        r4._drain(out_f1, settle=0.6, overall=10.0)

        r4._send_op(proc1, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_f1, f"tisch-anfragen {table_key}")
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_op(proc1, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        r4._send_op(proc1, f"tisch-start {table_key}")

        r4._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f1, out_f1, "Ich erkunde die Gegend.")
        r4._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f1, out_f1, "Ich schliesse den Abschnitt ab.")

        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        assert proc1.returncode == 94, (
            f"B2/Prozess1: erwartete os._exit(94) NACH Plan-Pin/Primaersave, VOR Reflexion -- "
            f"rc={proc1.returncode} stderr={stderr1!r}"
        )
        evidence["processes"]["proc1_hardexit"] = {
            "argv": argv1, "pid": proc1.pid, "utc_start": utc_start1, "utc_end": utc_end1,
            "exit_code": proc1.returncode, "stdout_text": stdout1, "stderr_text": stderr1,
        }

        table_id = "local-guest1"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert plan_path.exists(), "B2: Prozess 1 haette den Plan real pinnen muessen (verbindliche Annahme)."
        assert guest_current_path.exists(), "B2: Prozess 1 haette den Primaersave real schreiben muessen."
        assert not final_path.exists(), "B2: __final.json darf von Prozess 1 NICHT erreicht worden sein."
        sha_guest_after_commit = r4._sha256(guest_current_path)
        decision_after_proc1 = admission.read_table_decision(run_dir, table_id)
        assert decision_after_proc1 is not None and decision_after_proc1.get("decision") == "plan_committed", (
            decision_after_proc1
        )
        before_state = {
            "plan_exists": True, "final_exists": False, "guest_current_sha256": sha_guest_after_commit,
            "decision": decision_after_proc1.get("decision"),
        }

        # ── Prozess 2 (literaler Launcher, GETRENNTER NEUER OS-Prozess,
        # eigene PID/argv/cwd/UTC/Exit): der normale gebundene
        # Wiedereinstieg (`tisch-start` -> `_resume_bound_table`) beendet
        # DENSELBEN offenen Abschluss -- kein Rollback, kein neuer
        # Abschnitt, echte freiwillige Notiz statt '/abbrechen'.
        in_fifo_2, out_fifo_2 = fifo_dir / "guest1_in_2.fifo", fifo_dir / "guest1_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_2}:{out_fifo_2}",
        ]
        utc_start2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv2, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f2, out_f2 = r4._open_guest_fifo_pair(in_fifo_2, out_fifo_2)
        r4._drain(out_f2, settle=0.6, overall=10.0)
        assert proc1.pid != proc2.pid, "B2: Prozess 2 muss eine ANDERE PID als Prozess 1 haben."
        r4._send_op(proc2, f"tisch-start {table_key}")
        resume_lines = r4._wait_for_marker(out_f2, "eigene lokale Notiz", overall=25.0)
        joined_resume = "".join(resume_lines)
        assert "KI-Leader" not in joined_resume, joined_resume
        r4._deliver_guest_turn_answer(in_f2, out_f2, "B2-Abschlussnotiz: regulaer fertiggestellt.")
        r4._wait_for_path(final_path, overall=25.0)
        finish_tail = r4._drain(out_f2, settle=0.6, overall=10.0)
        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r6.utc(time.time())
        in_f2.close()
        out_f2.close()
        assert proc2.returncode == 0, f"B2/Prozess2: {stderr2}"
        assert final_path.exists(), "B2: Prozess 2 haette __final.json real schreiben muessen."
        sha_final = r4._sha256(final_path)
        sha_guest_after_finish = r4._sha256(guest_current_path)
        # Kein Rollback: der VOR dem Hardexit geschriebene Plan/Primaersave
        # wird regulaer fertiggestellt -- der Primaersave-Inhalt zum
        # Commit-Zeitpunkt bleibt identisch (gleiche Figurenbindung/Save-
        # Kette), KEINE doppelte Primaersave-Wirkung (Prozess 2 schreibt
        # keinen ZWEITEN Primaersave, nur den finalen Debrief-Save).
        guest_private_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private_state is not None and guest_private_state.final_save is not None, (
            "B2: die abgeschlossene Fassung haette ueber den normalen Rueckkanal in die private "
            "Gastablage geschrieben werden muessen."
        )
        final_char = guest_private_state.final_save["characters"][0]
        assert final_char["id"] == char_id and final_char["lvl"] == 2, final_char
        evidence["processes"]["proc2_resume_new_os_process"] = {
            "argv": argv2, "pid": proc2.pid, "utc_start": utc_start2, "utc_end": utc_end2,
            "exit_code": proc2.returncode, "stdout_text": stdout2, "stderr_text": stderr2,
        }

        # ── Prozess 3 (literaler Launcher, identischer Retry): KEINE
        # zweite Wirkung -- kein Rollback, keine doppelte Save-/Figuren-/
        # Claim-/Reflexionswirkung.
        in_fifo_3, out_fifo_3 = fifo_dir / "guest1_in_3.fifo", fifo_dir / "guest1_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_3}:{out_fifo_3}",
        ]
        utc_start3 = r6.utc(time.time())
        result3 = subprocess.run(
            argv3, cwd=str(_REPO_ROOT), env=env,
            input=f"tisch-start {table_key}\nbeenden\n", capture_output=True, text=True, timeout=30,
        )
        utc_end3 = r6.utc(time.time())
        assert result3.returncode == 0, f"B2/Prozess3: {result3.stderr}"
        assert f"Tischstart abgelehnt: Tisch '{table_key}' ist geschlossen" in result3.stdout, result3.stdout
        assert r4._sha256(final_path) == sha_final, "B2: identischer Retry hat __final.json erneut geschrieben."
        assert r4._sha256(guest_current_path) == sha_guest_after_finish, (
            "B2: identischer Retry hat den Gast-Save veraendert."
        )
        evidence["processes"]["proc3_identical_retry_no_double_effect"] = {
            "argv": argv3, "utc_start": utc_start3, "utc_end": utc_end3,
            "exit_code": result3.returncode, "stdout_text": result3.stdout, "stderr_text": result3.stderr,
        }

        # ── Kalter Reload: die wirklich nutzbare persoenliche Fassung
        # ueber einen GETRENNTEN frischen Prozess laden/exportieren. 'e'
        # ist der direkte Hauptmenue-Shortcut (OHNE Pfadabfrage, schreibt
        # sofort nach `<data_dir>/exports/<participant_id>.json`).
        export_path = guest_onboarding.parent / "exports" / "guest1.json"
        argv4 = [
            sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(guest_onboarding.parent),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        utc_start4 = r6.utc(time.time())
        result4 = subprocess.run(
            argv4, cwd=str(_REPO_ROOT), env=r4._clean_env(),
            input="fortsetzen\ne\nbeenden\n",
            capture_output=True, text=True, timeout=30,
        )
        utc_end4 = r6.utc(time.time())
        assert result4.returncode == 0, f"B2/Prozess4 (kalter Reload): {result4.stderr}"
        assert export_path.exists(), (
            f"B2: der kalte Reload haette einen Export unter {export_path} schreiben muessen: "
            f"{result4.stdout[-800:]!r}"
        )
        exported = json.loads(export_path.read_text(encoding="utf-8"))
        exp_char = exported["characters"][0]
        assert exp_char["id"] == char_id and exp_char["lvl"] == 2, exp_char
        evidence["processes"]["proc4_cold_reload_usable_afterward"] = {
            "argv": argv4, "utc_start": utc_start4, "utc_end": utc_end4,
            "exit_code": result4.returncode, "stdout_text": result4.stdout, "stderr_text": result4.stderr,
            "exported_char": exp_char,
        }
        evidence["guest1_fifo_channel"] = {
            "resume_lines_proc2": resume_lines, "finish_tail_proc2": finish_tail,
        }

        for label, pr in (
            ("proc1_hardexit", evidence["processes"]["proc1_hardexit"]),
            ("proc2_resume_new_os_process", evidence["processes"]["proc2_resume_new_os_process"]),
            ("proc3_identical_retry_no_double_effect", evidence["processes"]["proc3_identical_retry_no_double_effect"]),
            ("proc4_cold_reload_usable_afterward", evidence["processes"]["proc4_cold_reload_usable_afterward"]),
        ):
            r6.write_process_result(
                out_dir, label, argv=pr["argv"], cwd=str(_REPO_ROOT),
                utc_start=pr["utc_start"], utc_end=pr["utc_end"], exit_code=pr["exit_code"],
                stdout_text=pr["stdout_text"], stderr_text=pr["stderr_text"],
            )
            mf.record_process_files(
                label, aussage=f"b2_{label}", run_id="B2", teilnehmer_figur="guest1",
                tisch_abschnitt=f"{table_key}/{table_id}",
            )
        mf.export_tree(run_dir, "run", aussage="b2_run_dir_final", run_id="B2", teilnehmer_figur="guest1")
        mf.export_tree(guest_onboarding, "guest_onboarding", aussage="b2_guest_private_final", run_id="B2", teilnehmer_figur="guest1")
        mf.export_file(export_path, "guest1_cold_reload_export.json", aussage="b2_cold_reload_export", run_id="B2", teilnehmer_figur="guest1")
        mf.write_json_body("before_after_inventory.json", {
            "before_resume": before_state,
            "after_regular_finish": {
                "final_exists": True, "final_sha256": sha_final,
                "guest_current_sha256": sha_guest_after_finish,
                "guest_private_final_lvl": final_char["lvl"],
            },
            "after_identical_retry": {"no_double_effect": True},
            "after_cold_reload": {"exported_char_lvl": exp_char["lvl"]},
        }, aussage="b2_before_after_inventory", run_id="B2", teilnehmer_figur="guest1")
        mf.write_json_body(
            "guest1_fifo_channel_transcript.json", evidence["guest1_fifo_channel"],
            aussage="b2_guest1_fifo_channel_transcript_proc2_resume", run_id="B2", teilnehmer_figur="guest1",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "B2_committed_interrupt_new_process",
            "aussage": (
                "Verbindliche Annahme (Plan-Pin+Primaersave) real geschrieben (Prozess 1), gezielte "
                "Unterbrechung ueber die vorhandene Testnaht (os._exit(94) NACH Plan-Pin/VOR Reflexion, "
                "keine neue Produkt-Fehlerfunktion), GETRENNTER NEUER OS-Prozess (Prozess 2, andere PID) "
                "bindet denselben offenen Abschluss ueber den normalen tisch-start-Fortsetzenweg und "
                "beendet ihn regulaer (echte freiwillige Notiz) -- kein Rollback, keine doppelte Save-/"
                "Figuren-/Claim-/Reflexionswirkung. Identischer Retry (Prozess 3) ohne zweite Wirkung. "
                "Kalter Reload (Prozess 4, GETRENNTER Prozess) zeigt die wirklich nutzbare persoenliche "
                "Fassung (lvl 2) danach."
            ),
            "proc1_pid": proc1.pid, "proc2_pid": proc2.pid,
            "proc_pids_distinct": proc1.pid != proc2.pid,
        })

    evidence["out_dir"] = str(out_dir)
    return evidence


def main() -> int:
    which = os.environ.get("J4_SCENES", "a,b1,b2").split(",")
    failed = 0
    if "a" in which:
        try:
            ev = run_scene_a()
            print("OK scene_a")
            print(json.dumps({"identifiers": ev.get("identifiers"), "paths": ev.get("paths")}, indent=2))
        except AssertionError as e:
            failed += 1
            print(f"FAIL scene_a: {e}")
            traceback.print_exc()
        except Exception:
            failed += 1
            traceback.print_exc()
    if "b1" in which:
        try:
            ev = run_scene_b1()
            print("OK scene_b1")
            print(json.dumps({"exit_code": ev.get("exit_code"), "decision": ev.get("decision")}, indent=2))
        except AssertionError as e:
            failed += 1
            print(f"FAIL scene_b1: {e}")
            traceback.print_exc()
        except Exception:
            failed += 1
            traceback.print_exc()
    if "b2" in which:
        try:
            ev = run_scene_b2()
            print("OK scene_b2")
            print(json.dumps({"out_dir": ev.get("out_dir")}, indent=2))
        except AssertionError as e:
            failed += 1
            print(f"FAIL scene_b2: {e}")
            traceback.print_exc()
        except Exception:
            failed += 1
            traceback.print_exc()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
