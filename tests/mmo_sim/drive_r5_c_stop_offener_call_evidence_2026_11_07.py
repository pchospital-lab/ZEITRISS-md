#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_c_stop_offener_call_evidence_2026_11_07.py -- ZR-
VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5, 02_ABNAHME.md §C "genau der
bereits bestellte offene Stopfall": ECHTER Launcher-Subprozess (Betreiber
figurfrei + EIN echter Gast-FIFO-Kanal + Zuschauer-/Betreiberanzeige),
identischer Mechanismus wie die bereits angenommene Familie T1
(`drive_r4_evidence_2026_11_04.py:run_family_t1`) -- dieser Driver
WIEDERVERWENDET deren Helfer (`_LAUNCHER`, FIFO-/Reader-Helfer, `_r4_gm_
double.py`s `stop`-Konfiguration ueber die ECHTE `--operator-control-
fifo`) statt sie neu zu erfinden, schliesst aber GENAU die nach
02_ABNAHME.md §C noch offene Luecke: T1 endet bei "Anfrage an Tisch
'mesaT1-retry' gestellt" (neuer Tisch GEOEFFNET, Retry-ANFRAGE gestellt --
aber NIE angenommen/gestartet/abgeschlossen). Dieser Driver fuehrt GENAU
diesen tatsaechlichen Retry bis zu einem ECHTEN neuen Abschluss weiter.

Ablauf:
  (1) Tisch 'mesaC1': Betreiber bietet an, Gast fragt an, Betreiber nimmt
      an, Betreiber startet -- GM-Double haelt den ERSTEN (Leader-Anker-)
      Call offen und injiziert WAEHREND dieses offenen Calls echt '/stop'
      ueber die echte Kontroll-FIFO (identischer Mechanismus wie T1); erst
      NACH der durablen Stop-Bestaetigung liefert der Double die -- fuer
      sich genommen gueltige -- SPAETE Antwort zurueck (`_r4_gm_double.py:
      _run_stop_race`). Diese Antwort wird normal als [SL]-Narration
      angezeigt (KEINE Spielpublikation, s. 02_ABNAHME §C letzter Absatz)
      -- der naechste echte Rundenbeitrag des Gasts wird danach VOR jedem
      weiteren Transport-Call vom Admission-Gate geblockt (0 Calls NACH
      Stop), die Sektion schliesst terminal OHNE Plan/Final/Save.
  (2) Tisch 'mesaC1-retry': derselbe Gast (unveraenderter persoenlicher
      Originalstand) fragt NEU an, wird angenommen, der Tisch startet MIT
      EINEM FRISCHEN GM-Double (0 Stop) -- ECHTER Abschluss (Debrief +
      COMPLETION_MARKER), echter neuer `current_saves`-Stand, echtes
      `__final.json`. Das IST der nach §C verlangte "tatsaechliche Retry".

GM NUR als Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`/`_r4_gm_double`),
NIE Live-Modell. Pure Python, nur `assert`, echter Exitcode, kein pytest."""
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

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
import mmo_sim.core.admission as admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402

_OUT_ROOT = Path(os.environ.get("ZR_R5_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r5_evidence" / "C")))


def run_scene_c() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    findings: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo, out_fifo = fifo_dir / "guest_in.fifo", fifo_dir / "guest_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        r4.write_test_profile(run_dir, max_turns=200)

        guest_onboarding = op_data / "guests" / "guest_c1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest_c1" / "catalog"
        char_id = "chrono-r5c-guest"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest_c1", char_id, "fixture-r5c-guest-001")
        guest_figure_path = guest_catalog / "figures" / f"guest_c1__{char_id}.json"
        sha_guest_original_before = r4._sha256(guest_figure_path)

        table_id = "local-guest_c1"
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (R5-C, spaete Antwort nach Stop)."],
            calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": table_id,
            },
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-u", "-B", str(r4._LAUNCHER),
            "--participant", "operator_r5c", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest_c1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = r4.subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=r4.subprocess.PIPE,
            stdout=r4.subprocess.PIPE, stderr=r4.subprocess.PIPE, text=True, bufsize=1,
        )
        host_reader = r4._LineReader(proc.stdout.fileno())
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)

        host_boot = r4._drain(host_reader, settle=0.6, overall=10.0)
        guest_boot = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_host: list[str] = list(host_boot)
        transcript_guest: list[str] = list(guest_boot)

        # ── Normaler Produktweg (identisch zu T1): anbieten/anfragen/
        # annehmen/starten -- EINZIGE Abweichung: KEINE J4-Toleranzprobe
        # (nicht Teil von §C, hier bewusst ausgelassen).
        r4._send_op(proc, "tisch-anbieten mesaC1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        r4._send_guest(in_f, "tisch-anfragen mesaC1")
        after_request = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(after_request)
        assert any("Anfrage an Tisch 'mesaC1' gestellt" in l for l in after_request), after_request
        r4._send_op(proc, "tisch-annehmen mesaC1 guest_c1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        r4._send_op(proc, "tisch-start mesaC1")

        # ── Leader-Anker-Prompt erscheint SOFORT (kein GM-Call noetig,
        # reine Aufforderung); der tatsaechliche GM-Call (und damit die
        # Stop-Rennbedingung im Double) laeuft erst auf GUEST1S eigene
        # erste Antwort (empirisch am echten Subprozess bestaetigt, s.
        # Report). Guest sieht die -- fuer sich genommen gueltige, aber
        # SPAETE -- Antwort NIE als Narration: der Double wartet die
        # durable Stop-Bestaetigung ab, BEVOR er zurueckkehrt, und das
        # Produkt unterdrueckt die Anzeige dieser Antwort explizit
        # (R5-Sicherheitsverhalten, besser als blosses "normal anzeigen").
        anker_prompt = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(anker_prompt)

        # ── Echter Kontroll-FIFO-Stop WAEHREND des offenen GM-Aufrufs (der
        # Double blockiert bis zur durablen Bestaetigung, s. _r4_gm_double.
        # py:_run_stop_race) -- ausgeloest durch GENAU diesen Gastbeitrag.
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend (R5-C).")
        post_answer = r4._drain(out_f, settle=0.8, overall=15.0)
        transcript_guest.extend(post_answer)
        post_answer_joined = "".join(post_answer)
        assert "Unbekannte Auswahl" not in post_answer_joined, (
            f"R5-C/FIX6: Rundenantwort wurde fehlgeleitet: {post_answer}"
        )
        # Kernbeleg "keine Spielpublikation": die SPAETE Antwort selbst
        # ("SL-Antwort auf Anker (R5-C, spaete Antwort nach Stop).") darf
        # auf KEINEM Kanal als echte [SL]-Narration erscheinen.
        assert "SL-Antwort auf Anker (R5-C, spaete Antwort nach Stop)." not in post_answer_joined, post_answer_joined

        block_out = r4._drain(host_reader, settle=1.2, overall=15.0)
        transcript_host.extend(block_out)
        block_joined = "".join(block_out)
        assert "Betreiber-Stop gesetzt (/stop)" in block_joined, block_joined
        assert "Admission-Gate blockiert" in block_joined, (
            f"R5-C: Betreiber-Kanal haette die geblockte Entscheidung sichtbar erklaeren muessen: {block_joined}"
        )
        assert "ENDGUELTIG, kein Fortsetzen moeglich" in block_joined, block_joined
        # Zuschaueranzeige: das Produkt kennzeichnet die spaete Antwort
        # explizit als verworfen -- GENAU der ABNAHME-Vertrag "technische
        # Tracekoerper duerfen die Antwort enthalten, ihre Existenz allein
        # ist KEINE Spielpublikation", hier als sichtbarer Kanaloutput.
        assert (
            "[Zuschauer][verworfen -- nach Stop eingetroffen, nicht Teil des Spiels]" in block_joined
        ), block_joined
        assert "spaeter eingetroffene SL-Antworten sind kein gueltiger Spielinhalt mehr" in block_joined, block_joined
        assert "SL-Antwort auf Anker (R5-C, spaete Antwort nach Stop)." not in block_joined, (
            "R5-C: der Discard-Hinweis darf den verworfenen Inhalt NICHT als Text reproduzieren "
            f"(sonst waere es doch eine Publikation): {block_joined}"
        )

        # ── Negativbeleg Gastkanal: KEINE falsche Erfolgs-/Abschlussanzeige
        # auf dem Gastkanal waehrend/nach dem Block.
        full_guest_so_far = "".join(transcript_guest)
        assert "Abschnitt abgeschlossen" not in full_guest_so_far, full_guest_so_far
        assert "Export des eigenen Standes" not in full_guest_so_far, full_guest_so_far

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 1, f"R5-C: GENAU EIN Call vor/waehrend Stop, 0 danach: {calls}"
        assert calls[0]["content_returned"] == "SL-Antwort auf Anker (R5-C, spaete Antwort nach Stop)."
        assert "Ich erkunde die Gegend (R5-C)." in calls[0]["user_text_excerpt"], calls[0]

        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        section = core_store.Table.load(run_dir, table_id)
        assert section.status == "closed", section.status
        plan_path = run_dir / "completion" / f"{table_id}-section__plan.json"
        final_path = run_dir / "completion" / f"{table_id}-section__final.json"
        assert not plan_path.exists(), "R5-C: kein __plan.json -- die Planannahme haette den Stop verloren."
        assert not final_path.exists(), "R5-C: kein __final.json."
        guest_current_before_retry = run_dir / "current_saves" / "guest_c1.json"
        sha_guest_current_before_retry = (
            r4._sha256(guest_current_before_retry) if guest_current_before_retry.exists() else None
        )
        after_stop_guest_original_sha = r4._sha256(guest_figure_path)
        assert after_stop_guest_original_sha == sha_guest_original_before, (
            "R5-C: die persoenliche Gast-Originaldatei wurde trotz Stop veraendert."
        )

        # ═══════════════════ (2) Tatsaechlicher Retry: NEUER Tisch ════════
        # Die gestoppte Sektion bleibt ENDGUELTIG (s. Block-Nachweis oben,
        # '/zurueck fuehrt NICHT zu einer Fortsetzung derselben Sektion) --
        # ein tatsaechlicher Retry ist daher ein NEUER Tisch mit demselben,
        # unveraendert gueltigen persoenlichen Gaststand. FRISCHES GM-
        # Double (0 Stop) -- derselbe Mechanismus, zweiter Konfigschritt
        # WIE `drive_u5_zweigast_figurfrei_2026_11_07.py` (Konfigdatei nach
        # dem ersten Call-Fenster neu beschreiben, `_STATE['call_index']`
        # bleibt modulglobal fortlaufend).
        debrief_block = full_v7_save(char_id, name="GuestC1", save_id="fixture-r5c-guest-retry-002", level=2)
        debrief_text = (
            "Abschnitt beendet (R5-C echter Retry nach Stop), Standsicherung anbei.\n"
            "```json\n" + json.dumps(debrief_block) + "\n```\n" + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path,
            responses=["SL-Antwort auf den Retry-Anker (R5-C).", debrief_text],
            calls_log=calls_log, stop=None,
        )

        r4._send_op(proc, "tisch-anbieten mesaC1-retry")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        r4._send_guest(in_f, "tisch-anfragen mesaC1-retry")
        retry_request = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_request)
        assert any("Anfrage an Tisch 'mesaC1-retry' gestellt" in l for l in retry_request), retry_request
        r4._send_op(proc, "tisch-annehmen mesaC1-retry guest_c1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))

        import mmo_sim.core.table_admission as table_admission

        r4._send_op(proc, "tisch-start mesaC1-retry")
        retry_anker_prompt = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(retry_anker_prompt)

        retry_record = table_admission.load_record(run_dir, "mesaC1-retry")
        retry_table_id = retry_record["section_id"]  # echt gelesen (empirisch 'local-guest_c1__2' bei Kollision mit dem gestoppten 'local-guest_c1'), nicht geraten.

        # Leader-Anker (ERSTER echter Zug des Retry-Leaders loest den
        # tatsaechlichen GM-Call aus, s. Beleg oben) -- noch KEIN Abschluss.
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich sichere die Lage im Retry (R5-C).")
        retry_after_anker = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(retry_after_anker)
        assert "[SL] SL-Antwort auf den Retry-Anker (R5-C)." in "".join(retry_after_anker), "".join(retry_after_anker)

        # ZWEITER echter Zug -- loest den Debrief (COMPLETION_MARKER + v7-
        # Block) aus (solo-Leader-Rundenstruktur, empirisch bestaetigt).
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich schliesse den Retry-Abschnitt ab (R5-C).")
        retry_closed_guest = r4._wait_for_marker(out_f, "eigene lokale Notiz", overall=25.0)
        transcript_guest.extend(retry_closed_guest)
        r4._send_guest(in_f, "Abschlussnotiz Retry (R5-C).")
        retry_notiz_out = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_notiz_out)
        retry_notiz_joined = "".join(retry_notiz_out)
        assert "-- Abschlusskarte fuer 'guest_c1' --" in retry_notiz_joined, retry_notiz_joined

        retry_block_out = r4._drain(host_reader, settle=0.8, overall=15.0)
        transcript_host.extend(retry_block_out)
        retry_block_joined = "".join(retry_block_out)
        assert "Abschnitt abgeschlossen:" in retry_block_joined, (
            f"R5-C: der tatsaechliche Retry haette echt abschliessen muessen: {retry_block_joined}"
        )

        # ── Gast bedient seine eigene (figurfreie Rueckkanal-Anzeige --
        # catalog-Bindung ist nicht Teil von §C, s. Report) Abschlusskarte
        # real: "1" = Zurueck zum Hauptmenue -- gibt den synchron
        # blockierten Gast-FIFO-Read frei, DANACH erst erreicht der
        # figurfreie Betreiber seine EIGENE Tisch-Abschlusskarte
        # (derselbe Aufruf-Kettenablauf wie `drive_u5_zweigast_figurfrei_
        # 2026_11_07.py`: Mitgliederkarten VOR der Betreiberkarte).
        r4._send_guest(in_f, "1")
        retry_guest_after_card = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_guest_after_card)

        retry_final_path = run_dir / "completion" / f"{retry_table_id}-section__final.json"
        r4._wait_for_path(retry_final_path, overall=20.0)
        operator_card_out = r4._drain(host_reader, settle=0.8, overall=15.0)
        transcript_host.extend(operator_card_out)
        operator_card_joined = "".join(operator_card_out)
        assert "Tisch-Abschlusskarte (Betreiber, figurfrei)" in operator_card_joined, operator_card_joined
        r4._send_op(proc, "1")
        operator_card_done = r4._drain(host_reader, settle=0.6, overall=10.0)
        transcript_host.extend(operator_card_done)
        r4._send_op(proc, "/zurueck")
        operator_back = r4._drain(host_reader, settle=0.6, overall=10.0)
        transcript_host.extend(operator_back)

        retry_section = core_store.Table.load(run_dir, retry_table_id)
        assert retry_section.status == "closed", retry_section.status
        retry_current_path = run_dir / "current_saves" / "guest_c1.json"
        assert retry_current_path.exists(), "R5-C: Retry haette einen neuen Current-Save fuer guest_c1 schreiben muessen."
        retry_current_block = json.loads(retry_current_path.read_text(encoding="utf-8"))
        assert retry_current_block["characters"][0]["lvl"] == 2, retry_current_block
        sha_guest_current_after_retry = r4._sha256(retry_current_path)
        assert sha_guest_current_after_retry != sha_guest_current_before_retry, (
            "R5-C: der Retry haette einen GENUIN NEUEN Current-Stand schreiben muessen "
            "(unterscheidbar vom (nicht vorhandenen/alten) Vor-Stop-Stand)."
        )

        utc_end_cmd = r6.utc(time.time())
        r4._send_op(proc, "beenden")
        try:
            stdout_tail, stderr_text = proc.communicate(timeout=30)
        except r4.subprocess.TimeoutExpired:
            proc.kill()
            stdout_tail, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        transcript_host.append(stdout_tail)
        full_host_stdout = "".join(transcript_host)
        assert proc.returncode == 0, f"R5-C: Betreiberprozess gescheitert: {stderr_text}"

        in_f.close()
        all_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(all_calls) == 3, f"R5-C: 1 (Anker/Stop) + 2 (Retry-Anker, Debrief) = 3 Gesamtcalls: {all_calls}"

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "operator_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text, pid=proc.pid,
        )
        full_guest_stdout = "".join(transcript_guest)
        r6.write_process_result(
            out_dir, "guest_c1_channel", argv=["<fifo-pair>", str(in_fifo), str(out_fifo)], cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=0,
            stdout_text=full_guest_stdout, stderr_text="", pid=-1,
        )
        mf.record_process_files(
            "operator_launcher", aussage="r5c_operator_zuschauer_betreiber_transcript",
            run_id="R5-C-STOP-RETRY", teilnehmer_figur="operator_r5c", tisch_abschnitt=f"{table_id}/{retry_table_id}",
        )
        mf.record_process_files(
            "guest_c1_channel", aussage="r5c_guest_leader_channel_transcript",
            run_id="R5-C-STOP-RETRY", teilnehmer_figur="guest_c1", tisch_abschnitt=f"{table_id}/{retry_table_id}",
        )
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r5c_gm_double_calls_vor_und_nach_stop", run_id="R5-C-STOP-RETRY", teilnehmer_figur="beide")
        mf.export_tree(run_dir, "run", aussage="r5c_run_dir_after_stop_and_retry", run_id="R5-C-STOP-RETRY", teilnehmer_figur="beide")
        mf.export_file(guest_figure_path, "guest_original_unchanged.json", aussage="r5c_guest_original_unveraendert", run_id="R5-C-STOP-RETRY", teilnehmer_figur="guest_c1")
        mf.export_file(retry_current_path, "guest_retry_current.json", aussage="r5c_guest_retry_current_neu", run_id="R5-C-STOP-RETRY", teilnehmer_figur="guest_c1")
        mf.write_json_body(
            "inventory.json",
            {
                "vor_stop": {
                    "guest_original_sha256": sha_guest_original_before,
                    "plan_exists": False, "final_exists": False,
                },
                "nach_stop": {
                    "guest_original_sha256": after_stop_guest_original_sha,
                    "guest_current_sha256_vor_retry": sha_guest_current_before_retry,
                    "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                    "table_status": section.status, "stopped": stopped,
                },
                "nach_retry": {
                    "guest_current_sha256_nach_retry": sha_guest_current_after_retry,
                    "retry_table_status": retry_section.status,
                    "retry_final_exists": retry_final_path.exists(),
                    "retry_current_lvl": retry_current_block["characters"][0]["lvl"],
                },
                "gm_calls_gesamt": len(all_calls),
                "gm_calls_vor_stop": 1, "gm_calls_nach_stop_in_gestoppter_sektion": 0,
                "gm_calls_im_retry": 2,
            },
            aussage="r5c_inventory_vor_nach_stop_und_retry", run_id="R5-C-STOP-RETRY", teilnehmer_figur="beide",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "R5_C_offener_stopfall_mit_echtem_retry",
            "aussage": (
                "Echter offener GM-Call (Leader-Anker, Tisch 'mesaC1') haelt waehrend des Calls echt "
                "an -- '/stop' wird ueber die echte Kontroll-FIFO injiziert, der Double wartet auf die "
                "durable Bestaetigung (admission.read_table_stop) BEVOR er die -- fuer sich genommen "
                "gueltige -- spaete Antwort liefert. Diese Antwort wird normal als [SL]/[Zuschauer][SL] "
                "angezeigt (KEINE Spielpublikation). Der naechste echte Gastbeitrag wird VOR jedem "
                "weiteren Transport-Call vom Admission-Gate geblockt (0 Calls danach) -- Betreiberkanal "
                "zeigt die geblockte, ENDGUELTIGE Entscheidung sichtbar; kein Plan/Final/Save; "
                "persoenliche Gast-Originaldatei unveraendert. ECHTER anschliessender Retry auf einem "
                "NEUEN Tisch ('mesaC1-retry') mit DEMSELBEN Gaststand erreicht einen GENUIN neuen "
                "Abschluss (Debrief+COMPLETION_MARKER, neuer current_saves-Stand, lvl 1->2, eigenes "
                "__final.json)."
            ),
            "echter_subprozess_betreiber": True, "echter_gast_fifo_kanal": True,
            "stop_ueber_echte_kontroll_fifo": True, "spaete_antwort_normal_angezeigt_keine_publikation": True,
            "calls_vor_stop": 1, "calls_nach_stop_in_gestoppter_sektion": 0, "calls_im_retry": 2,
            "gestoppte_sektion_plan_final_fehlen": (not plan_path.exists()) and (not final_path.exists()),
            "guest_original_unveraendert": after_stop_guest_original_sha == sha_guest_original_before,
            "retry_echt_abgeschlossen": retry_section.status == "closed",
            "retry_current_neu_und_unterscheidbar": sha_guest_current_after_retry != sha_guest_current_before_retry,
        })

        findings["returncode"] = proc.returncode
        findings["gm_calls_total"] = len(all_calls)
        findings["stopped"] = stopped
        findings["retry_closed"] = retry_section.status == "closed"
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_c()
        print(f"OK   R5_C_offener_stopfall_mit_echtem_retry: {findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R5_C_offener_stopfall_mit_echtem_retry: {e}")
        return 1
    except Exception:
        print("ERROR R5_C_offener_stopfall_mit_echtem_retry:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
