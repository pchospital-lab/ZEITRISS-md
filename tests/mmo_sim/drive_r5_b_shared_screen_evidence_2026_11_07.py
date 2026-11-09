#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_b_shared_screen_evidence_2026_11_07.py -- ZR-
VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5, 02_ABNAHME.md §B "derselbe
Bildschirm, unterschiedliche Menschen": ECHTER Driver (kein isolierter
Methodentest) ueber den tatsaechlichen `scripts/mmo_sim.py`-Subprozess
-- EIN Prozess, EIN geteiltes Terminal (eine stdin/stdout-Pipe), ZWEI
verschiedene registrierte Menschen mit verschiedenen persoenlichen
Figuren/Saves, ueber den gefuehrten `g`-Weg (`_cmd_local_round_setup`).

Der bereits angenommene B1b/B2-Kernbeweis (`test_a24_local_two_humans_
2026_10_01.py`) bleibt unveraendert gueltig -- dieser Driver baut auf
EXAKT demselben realen Subprozess-/Registry-/Onboarding-Muster
(`_a24_local_support.py`) auf, fuehrt aber zusaetzlich GENAU die in
02_ABNAHME.md §B noch offenen Stationen auf dem R5-korrigierten Code
real durch:

  - FIX4a (`_local_round_confirm_figure`): EINE ungueltige Figurbe-
    staetigung ('vllt') an der Figurbestaetigung des Leaders -- muss am
    SELBEN Schritt erklaert+erneut gefragt werden (kein Abbruch), danach
    bestaetigt das echte 'j' wirklich.
  - FIX4b (`_local_round_select_humans`): ein echtes '/zurueck' GENAU an
    der ERSTEN Figurbestaetigung (figure_idx=0) springt laut Schrittautomat
    (`_cmd_local_round_setup`) zurueck auf STEP_HUMANS -- die bereits
    getroffene Menschenauswahl (Leader + zweiter Mensch) muss dort SICHTBAR
    als "Aktuelle Auswahl" wieder angezeigt UND bei erneuter leerer Eingabe
    BEHALTEN werden (nicht auf "nur du" zurueckgesetzt).
  - FIX2 (`_cmd_export`/`_print_section_completion_card`): nach echtem
    Rundenabschluss bedienen BEIDE Menschen real ihre eigene Abschlusskarte
    (echter `_cmd_export`-Aufruf) am SELBEN geteilten `io` (kein eigenes
    Gastterminal) -- der Export des ZWEITEN Menschen muss dessen EIGENEN
    Stand/Dateinamen treffen, NICHT den des Leaders/der aeusseren Session.

Kein AI-Mitspieler (ai_tokens=[]) -- reduziert die Szene auf GENAU die in
§B verlangte Zwei-Menschen-Konstellation, ohne eine zweite Persona-API-
Doppel-Infrastruktur einzufuehren. GM NUR als Grenzinjektion
(`MMO_SIM_GM_TRANSPORT_DOUBLE`/`tests.mmo_sim._r4_gm_double`, identischer
Mechanismus wie `drive_u5_zweigast_figurfrei_2026_11_07.py`), NIE Live-
Modell. Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import sys
import os
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
import _a24_local_support as sup  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402

_OUT_ROOT = Path(os.environ.get("ZR_R5_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r5_evidence" / "B")))

HUMAN_A_NAME = "R5B-Mensch-A"
HUMAN_B_NAME = "R5B-Mensch-B"
CHAR_A = "chrono-r5b-mensch-a"
CHAR_B = "chrono-r5b-mensch-b"


def run_scene_b() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    findings: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        data_dir = root
        run_dir, states_dir = data_dir / "run", data_dir / "states"
        onboarding_dir, catalog_dir = data_dir / "onboarding", data_dir / "catalog"
        registry_dir = data_dir / "registry"
        exports_dir = data_dir / "exports"

        human_a = sup.register_human(registry_dir, HUMAN_A_NAME)
        human_b = sup.register_human(registry_dir, HUMAN_B_NAME)
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id
        assert human_a_id != human_b_id

        onb_a = sup.onboard_human_figure(
            registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, CHAR_A, "Avery", "AVERYOPS",
        )
        onb_b = sup.onboard_human_figure(
            registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, CHAR_B, "Blair", "BLAIROPS",
        )
        assert onb_a["participant"].record_refs and onb_b["participant"].record_refs

        # `onboard_human_figure` publiziert bereits den echten Current-
        # Save (`core_store.publish_current_save`), bindet aber KEINEN
        # Katalogeintrag -- `_build_resume_card`s `chrononaut_id = catalog.
        # last_selected(...)` (Abschlusskarten-/Export-Autoritaet) braucht
        # genau diesen Katalogeintrag, sonst bleibt die Karte "Keine eigene
        # Figur" und bietet KEINEN Export an (empirisch am echten
        # Subprozess bestaetigt). Derselbe Katalog-Registrierungsweg wie
        # `test_r5_fix2_shared_screen_card_owner_binding_2026_11_07.py`s
        # `_register_private_figure`.
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=human_a_id, chrononaut_id=CHAR_A, persona_key=human_a_id,
        ))
        catalog.bind_for_section(catalog_dir, human_a_id, CHAR_A, has_open_section=False)
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=human_b_id, chrononaut_id=CHAR_B, persona_key=human_b_id,
        ))
        catalog.bind_for_section(catalog_dir, human_b_id, CHAR_B, has_open_section=False)

        # NUR `max_turns` (wie `drive_u5_zweigast_figurfrei_2026_11_07.py`):
        # `max_usd`/`max_seconds` OHNE ein vom Transport-Double (`_r4_gm_
        # double.py`, kein Kosten-/Tokenreporting) durchsetzbares
        # Gegenstueck loest sonst das Admission-Gate (I2 Q07/A1: "kein
        # durchsetzbares Limit ermittelbar UND hartes max_usd konfiguriert
        # -- fehlende Grenze wird NICHT als 0 behandelt, Anfrage
        # abgelehnt") aus -- empirisch am echten Subprozess bestaetigt.
        sup.write_test_profile(run_dir, max_turns=200)

        leader_id = human_a_id
        members_sorted = sup.sorted_table_members(leader_id, [human_b_id])
        table_id = sup.compute_table_id(leader_id, [human_b_id])

        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"
        debrief_a = full_v7_save(CHAR_A, name="Avery", save_id="fixture-r5b-mensch-a-002", level=2)
        debrief_b = full_v7_save(CHAR_B, name="Blair", save_id="fixture-r5b-mensch-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet (R5-B geteilter Bildschirm), beide Standsicherungen anbei.\n"
            "```json\n" + json.dumps(debrief_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_b) + "\n```\n"
            + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path,
            responses=[
                "SL-Antwort auf den Leader-Anker (R5-B).",
                "SL-Antwort auf den Beitrag von Mensch B (R5-B).",
                debrief_text,
            ],
            calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        # ── Setup-Zeilen (gefuehrter 'g'-Weg) ───────────────────────────
        # 1) "g" -> _cmd_local_round_setup, STEP_MODE.
        # 2) "2" -> Modus "mehrere Menschen" -> STEP_HUMANS.
        # 3) "1" -> einzigen bekannten weiteren Menschen (Human B) waehlen
        #    -> human_ids=[leader, human_b] -> STEP_FIGURES figure_idx=0.
        # 4) "/zurueck" GENAU an der ERSTEN Figurbestaetigung (Leader) --
        #    figure_idx==0 -> Schrittautomat springt auf STEP_HUMANS zurueck
        #    (FIX4b-Kernbeleg: Ruecksprung aus STEP_FIGURES).
        # 5) STEP_HUMANS erneut: "Aktuelle Auswahl" MUSS jetzt sichtbar
        #    sein (current=[leader, human_b] != [leader]) -- leere Eingabe
        #    behaelt sie bewusst (FIX4b).
        # 6) STEP_FIGURES figure_idx=0 (Leader) erneut: "vllt" (ungueltige
        #    Antwort, FIX4a) -> muss am SELBEN Schritt erneut fragen, KEIN
        #    Abbruch -- danach "j" bestaetigt wirklich.
        # 7) STEP_FIGURES figure_idx=1 (Human B): "j" bestaetigt.
        # 8) STEP_AI: "" -> ai_tokens=[] (keine KI).
        # 9) STEP_LEADER: "" -> Leader = der Aufrufer selbst.
        # 10) STEP_SUMMARY: "j" -> Startwahl bestaetigt.
        # 11) Handoff-Schleife: EINE Uebergabe an Human B -> "j".
        setup_lines = [
            "g", "2", "1",
            "/zurueck",
            "",
            "vllt", "j",
            "j",
            "", "",
            "j",
            "j",
        ]

        # ── Runde: Leader zuerst (Fokus initial bei Human B -> Uebergabe
        # an Leader noetig), dann Human B, dann Leader-Debrief (loest
        # COMPLETION_MARKER aus), dann je eine freiwillige Abschlussnotiz
        # pro Mitglied (Reihenfolge = `members_sorted`), dann Human Bs
        # Beitritts-Consent ("j", bereits Teil des bestehenden, unveraen-
        # derten Consentwegs -- GENAU EIN 'j' nach der Setup-Handoff-Zeile).
        focus = [human_b_id]
        turn_lines: list[str] = []
        handoff_targets: list[str] = []

        def _turn(actor: str, text: str) -> None:
            switched = focus[0] is not None and focus[0] != actor
            if switched:
                turn_lines.append("j")
                handoff_targets.append(actor)
            turn_lines.append(text)
            focus[0] = actor

        _turn(leader_id, "Wir sichten gemeinsam die Lage am geteilten Terminal.")
        _turn(human_b_id, "Ich uebernehme die rechte Flanke.")
        _turn(leader_id, "Wir schliessen diesen Abschnitt kontrolliert ab.")
        for m in members_sorted:
            if m == leader_id:
                _turn(leader_id, "Notiz Leader (R5-B): Uebergabe/Rueckuebergabe lief sauber.")
            elif m == human_b_id:
                _turn(human_b_id, "Notiz Mensch B (R5-B): eigener Beitrag eingebracht.")

        # ── Nach "Abschnitt abgeschlossen": je EINE Abschlusskarte pro
        # Mensch (Reihenfolge = `drivers`-Dict-Insertion = Leader ZUERST,
        # dann Human B -- s. `mmo_sim/ui/tui.py:_cmd_local_round`). Beide
        # waehlen "1" (echter Export). Danach "beenden" am Hauptmenue.
        card_lines = ["1", "1", "beenden"]

        stdin_lines = setup_lines + ["j"] + turn_lines + card_lines
        stdin_text = "\n".join(stdin_lines) + "\n"

        argv = [sys.executable, "-B", str(r4._REPO_ROOT / "scripts" / "mmo_sim.py"),
                "--data-dir", str(data_dir), "--participant", human_a_id]
        utc_start = r6.utc(time.time())
        popen = r4.subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=r4.subprocess.PIPE,
            stdout=r4.subprocess.PIPE, stderr=r4.subprocess.PIPE, text=True,
        )
        pid = popen.pid
        out, err = popen.communicate(input=stdin_text, timeout=90)
        utc_end = r6.utc(time.time())
        returncode = popen.returncode

        class _Proc:
            pass

        proc = _Proc()
        proc.returncode, proc.stdout, proc.stderr, proc.pid = returncode, out, err, pid
        assert proc.returncode == 0, f"R5-B: Prozess fehlgeschlagen rc={proc.returncode}\nSTDERR(tail)={proc.stderr[-2000:]}"

        # ── FIX4b-Beleg: Ruecksprung STEP_FIGURES(0) -> STEP_HUMANS,
        # vorherige Auswahl sichtbar + behalten.
        assert "Aktuelle Auswahl (bleibt erhalten, bis bewusst geaendert): " + f"{leader_id}, {human_b_id}" in out, (
            "R5-B FIX4b: vorherige Menschenauswahl wurde beim Zuruecklaufen nicht sichtbar "
            f"wieder angeboten: {out[:4000]}"
        )

        # ── FIX4a-Beleg: ungueltige Antwort wird am selben Schritt erklaert,
        # KEIN Abbruch (Aufbau erreicht den Spielstart trotzdem -- der Beleg
        # unten fuer "Abschnitt abgeschlossen" bestaetigt das indirekt;
        # zusaetzlich die explizite Erklaerzeile selbst).
        assert "'vllt' ist keine erkannte Ja-/Nein-Antwort" in out, (
            f"R5-B FIX4a: Erklaerzeile zur ungueltigen Antwort fehlt: {out[:6000]}"
        )
        assert "Aufbau bleibt erhalten" in out or "kein Abbruch" in out, out[:6000]
        assert "Einrichtung abgebrochen" not in out.split("ist keine erkannte Ja-/Nein-Antwort", 1)[1][:200], (
            "R5-B FIX4a: die ungueltige Antwort darf NICHT wie eine Ablehnung zum Abbruch fuehren."
        )

        assert "Lokale Runde einrichten" in out
        assert f"'{leader_id}' spielt '{CHAR_A}' -- bestaetigen?" in out
        assert f"'{human_b_id}' spielt '{CHAR_B}' -- bestaetigen?" in out
        assert f"Geteiltes Terminal wird an '{human_b_id}' (Figur '{CHAR_B}') uebergeben" in out
        assert f"[{human_b_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten?" in out, out[-2000:]
        assert "Abschnitt abgeschlossen:" in out, f"R5-B: Abschnitt nicht abgeschlossen: {out[-3000:]}"

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 3, f"R5-B: GENAU DREI reale GM-Rufe erwartet (Leader-Anker, Beitrag B, Debrief): {calls}"

        # ── Abschlusskarten-Belege (U3c): beide Karten muessen gedruckt +
        # real exportiert worden sein.
        assert f"-- Abschlusskarte fuer '{leader_id}' --" in out
        assert f"-- Abschlusskarte fuer '{human_b_id}' --" in out
        card_a_pos = out.index(f"-- Abschlusskarte fuer '{leader_id}' --")
        card_b_pos = out.index(f"-- Abschlusskarte fuer '{human_b_id}' --")
        assert card_a_pos < card_b_pos, (
            "R5-B: Leader-Karte muss vor der Human-B-Karte erscheinen (drivers-Insertion-Reihenfolge).",
        )

        # ── FIX2-Kernbeleg: Human Bs Export ist dessen EIGENER Stand unter
        # dessen EIGENEM Dateinamen -- NICHT der des Leaders/der aeusseren
        # Session. Beide Exportdateien muessen existieren und sich klar
        # unterscheiden.
        export_a_path = exports_dir / f"{leader_id}.json"
        export_b_path = exports_dir / f"{human_b_id}.json"
        assert export_a_path.exists(), f"R5-B FIX2: Export-Datei Leader fehlt: {export_a_path}"
        assert export_b_path.exists(), f"R5-B FIX2: Export-Datei Human B fehlt: {export_b_path}"
        export_a_block = json.loads(export_a_path.read_text(encoding="utf-8"))
        export_b_block = json.loads(export_b_path.read_text(encoding="utf-8"))
        export_a_char = export_a_block["characters"][0]["id"]
        export_b_char = export_b_block["characters"][0]["id"]
        assert export_a_char == CHAR_A, (
            f"R5-B FIX2: Leader-Export traegt die FALSCHE Figur (erwartet {CHAR_A}): {export_a_char}"
        )
        assert export_b_char == CHAR_B, (
            f"R5-B FIX2: Human-B-Export traegt die FALSCHE Figur (erwartet {CHAR_B}, Datenverlust/"
            f"-leck an den Leader waere der Pre-Fix-Fehler): {export_b_char}"
        )
        assert export_a_char != export_b_char

        # ── Byte-/inhaltlicher Abgleich: jeder Export == der zugehoerige
        # tatsaechlich akzeptierte eigene Current (`run/current_saves/<pid>.
        # json`) -- derselbe Dateivergleich wie in A gefordert.
        current_a_path = run_dir / "current_saves" / f"{leader_id}.json"
        current_b_path = run_dir / "current_saves" / f"{human_b_id}.json"
        current_a_block = json.loads(current_a_path.read_text(encoding="utf-8"))
        current_b_block = json.loads(current_b_path.read_text(encoding="utf-8"))
        export_a_match = export_a_block == current_a_block
        export_b_match = export_b_block == current_b_block
        assert export_a_match, (
            f"R5-B: Leader-Export ist NICHT byte-/feldgleich zum akzeptierten eigenen Current: "
            f"export={export_a_block} current={current_a_block}"
        )
        assert export_b_match, (
            f"R5-B: Human-B-Export ist NICHT byte-/feldgleich zum akzeptierten eigenen Current: "
            f"export={export_b_block} current={current_b_block}"
        )

        from mmo_sim.core import store as core_store
        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed", table.status
        assert set(table.members) == {leader_id, human_b_id}, table.members
        assert table.leader == leader_id

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "shared_screen_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=out, stderr_text=proc.stderr, pid=proc.pid,
        )
        mf.record_process_files(
            "shared_screen_launcher", aussage="r5b_shared_screen_full_transcript",
            run_id="R5-B-SHARED-SCREEN", teilnehmer_figur="beide", tisch_abschnitt=f"{table_id}-section",
        )
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r5b_gm_double_calls", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur="beide")
        mf.export_file(export_a_path, "human_a_export.json", aussage="r5b_human_a_export", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur=leader_id)
        mf.export_file(export_b_path, "human_b_export.json", aussage="r5b_human_b_export_fix2", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur=human_b_id)
        mf.export_file(current_a_path, "human_a_current.json", aussage="r5b_human_a_current", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur=leader_id)
        mf.export_file(current_b_path, "human_b_current.json", aussage="r5b_human_b_current", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur=human_b_id)
        mf.export_tree(run_dir, "run", aussage="r5b_run_dir_after_finish", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur="beide")
        mf.write_json_body(
            "stdin_sequence.json",
            {"setup_lines": setup_lines, "turn_lines": turn_lines, "card_lines": card_lines,
             "handoff_targets": handoff_targets},
            aussage="r5b_stdin_sequence_verweis", run_id="R5-B-SHARED-SCREEN", teilnehmer_figur="beide",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "R5_B_derselbe_bildschirm_zwei_menschen_echter_subprozess",
            "aussage": (
                "EIN geteiltes Terminal (ein Subprozess), zwei verschiedene registrierte Menschen "
                f"({leader_id} Leader, {human_b_id} Nicht-Leader) ueber den gefuehrten 'g'-Weg. "
                "FIX4a (ungueltige Figurbestaetigung -> Retry, kein Abbruch) UND FIX4b (Ruecksprung "
                "STEP_FIGURES->STEP_HUMANS zeigt/behaelt vorherige Auswahl) real durchlaufen. Runde "
                "schliesst echt (3 GM-Rufe: Leader-Anker, Beitrag B, Debrief). Beide bedienen ihre "
                "eigene Abschlusskarte (echter Export); Human Bs Export ist FIX2-korrekt an SEINE "
                "eigene Figur gebunden (nicht an den Leader), byte-/feldgleich zum eigenen Current."
            ),
            "echter_subprozess": True, "ein_geteiltes_terminal": True,
            "anzahl_gm_rufe": len(calls), "leader": leader_id, "nicht_leader": human_b_id,
            "fix2_export_b_korrekt_gebunden": export_b_char == CHAR_B,
            "fix2_export_a_export_b_unterscheidbar": export_a_char != export_b_char,
            "fix4a_retry_kein_abbruch": True, "fix4b_vorherige_auswahl_sichtbar_und_behalten": True,
            "export_a_byte_match_current": export_a_match, "export_b_byte_match_current": export_b_match,
            "table_closed": table.status == "closed",
        })

        findings["returncode"] = proc.returncode
        findings["gm_calls"] = len(calls)
        findings["export_a_char"] = export_a_char
        findings["export_b_char"] = export_b_char
        findings["export_a_match_current"] = export_a_match
        findings["export_b_match_current"] = export_b_match
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_b()
        print(f"OK   R5_B_derselbe_bildschirm_zwei_menschen: {findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R5_B_derselbe_bildschirm_zwei_menschen: {e}")
        return 1
    except Exception:
        print("ERROR R5_B_derselbe_bildschirm_zwei_menschen:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
