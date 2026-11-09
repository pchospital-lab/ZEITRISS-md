#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_b_person_b_selbst_evidence_2026_11_07.py -- ZR-
VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R6, 02_ABNAHME.md §B "zweiter Mensch am
selben Bildschirm handelt wirklich als er selbst" (= GENERAL-REVIEW.md §2
G-R6-01, 01_NACHZUG.md Arbeitsblock1 Punkt1a).

ECHTER Real-Subprozess-Treiber (EIN Subprozess, EIN geteiltes Terminal/eine
stdin-Pipe, ZWEI verschiedene registrierte Menschen mit verschiedenen
Figuren/Saves) auf dem R6-korrigierten Code. Baut strukturell auf
`drive_r5_b_shared_screen_evidence_2026_11_07.py` auf (dessen bereits
angenommener B1b/B2-/FIX2-Kern -- Export bindet an `pid`, nicht an die
aeussere Person -- wird NICHT neu aufgerollt, nur knapp bestaetigt), schliesst
aber GENAU die vorher offene Luecke:

  G-R6-01 (vorher): `_print_section_completion_card` band den Export zwar
  korrekt an `pid`, die danach angebotene Gastfolge rief aber
  `io._cmd_menu_tisch()` OHNE Identitaet -- bei `io is self` (geteilter
  Bildschirm) lief diese Folge auf `self.participant_id` (der AEUSSEREN
  Person/Host A): Host-Optionen [5]-[9] waeren sichtbar gewesen, eine
  tatsaechliche Tischanfrage waere unter As `guest_id`/Figur gelandet --
  obwohl die Karte fuer Person B galt. Kartenperson und wirkliche Folgeperson
  fielen auseinander.

  R6-FIX (jetzt): `_cmd_menu_tisch(acting_pid=pid)` + `_dispatch_completion_
  card_choice(..., speaker_pid=pid)` binden Anzeige/Hostzeile/Anfrage/'/stand'
  an die TATSAECHLICHE Kartenperson. Dieser Treiber belegt das ECHT am
  Subprozess:

  1. Export bleibt korrekt an `pid` gebunden (R5-Fix, knapp bestaetigt).
  2. An Bs Karten-Read ausdruecklich '/stand': zeigt Bs EIGENE Figur/Stand,
     KEINE fremde A-Anzeige.
  3. Bs angebotene Gastfolge (Kartennummer der Gast-Folgeaktion) wird
     TATSAECHLICH gewaehlt -- das danach sichtbare Untermenue zeigt KEINE
     fremden Hostoptionen (Betreiber/Host [5]-[9] fehlen fuer B).
  4. Aus diesem Gastfolgemenue fuehrt B eine ECHTE NEUE Tischanfrage aus
     (nicht nur Label pruefen, nicht sofort '/zurueck') -- die tatsaechliche
     `guest_id`/Figur/Save-Bindung gehoert B; A bleibt unberuehrt (weder in
     den Requests noch in den Gastangeboten dieses Tisches).
  5. Fokus-/Menuerueckgabe sichtbar bedienen: nach Bs Karte uebernimmt
     wieder A (naechstes Hauptmenue + '/stand' zeigt wieder As eigene Figur).
  6. Die echte Hostperson (A) bleibt hostfaehig (eigene Tisch-Betreiberzeile
     [5]-[9] weiterhin real erreichbar) -- KEIN globales Rollenflag wurde
     abgeschaltet.

GM NUR als Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`/`_r4_gm_double`),
NIE Live-Modell. Pure Python, nur `assert`, echter Exitcode, kein pytest.

§D Evidenz-Disziplin: vollstaendige originale stdout/stderr ab Prozessstart
(`<label>.stdout.txt`/`.stderr.txt`), reale Prozessdaten (`<label>.procmeta.
json`), tatsaechliche Sendeereignisse gekoppelt an den zuvor beobachteten
Prompt (`sends.jsonl`). `MERGED_PROTOKOLL.md` ist zusaetzlich und ausdruecklich
als ABGELEITET markiert, mit dem wirklichen Codeanker als erster Zeile."""
from __future__ import annotations

import json
import sys
import os
import subprocess
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
from mmo_sim.core import table_admission  # noqa: E402

_OUT_ROOT = Path(os.environ.get("ZR_R6_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r6_evidence" / "B")))

HUMAN_A_NAME = "R6B-Mensch-A"
HUMAN_B_NAME = "R6B-Mensch-B"
CHAR_A = "chrono-r6b-mensch-a"
CHAR_B = "chrono-r6b-mensch-b"
TABLE_KEY_B = "mesaR6B-gastfolge"
DRITTER_HOST = "dritter_host_r6b"


def _git_codeanchor() -> str:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    diffstat = subprocess.run(
        ["git", "diff", "--stat", "mmo_sim/ui/tui.py"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    return f"CODEANKER: HEAD={head} + uncommitteter Linus-Diff -- git diff --stat mmo_sim/ui/tui.py: {diffstat!r}"


def _write_procmeta(
    out_dir: Path, label: str, *, argv: list, cwd: str, pid: int, utc_start: str, utc_end: str, exit_code: int,
) -> Path:
    path = out_dir / f"{label}.procmeta.json"
    path.write_text(
        json.dumps({
            "label": label, "argv": list(argv), "cwd": str(cwd), "pid": int(pid),
            "utc_start": utc_start, "utc_end": utc_end, "exit": exit_code,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


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

        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=human_a_id, chrononaut_id=CHAR_A, persona_key=human_a_id,
        ))
        catalog.bind_for_section(catalog_dir, human_a_id, CHAR_A, has_open_section=False)
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=human_b_id, chrononaut_id=CHAR_B, persona_key=human_b_id,
        ))
        catalog.bind_for_section(catalog_dir, human_b_id, CHAR_B, has_open_section=False)

        sup.write_test_profile(run_dir, max_turns=200)

        # R6-B-Vorbedingung (G-R6-01-Gegenprobe "weder A noch B ist selbst
        # Host dieses Tisches, damit eine Anfrage eindeutig einer guest_id
        # zuzuordnen ist" -- derselbe Aufbau wie `test_r6_g01_shared_screen_
        # real_followup_and_stand_2026_11_07.py`): ECHTE Admission-Autoritaet
        # (dieselbe Funktion, die 'tisch-anbieten' intern aufruft), DIREKT
        # aufgerufen (wie `write_test_profile`/`full_v7_save` oben -- reine
        # Testvorbereitung, kein Teil des zu belegenden Subprozessverhaltens).
        table_admission.offer_table(run_dir, host_id=DRITTER_HOST, table_key=TABLE_KEY_B)

        leader_id = human_a_id
        members_sorted = sup.sorted_table_members(leader_id, [human_b_id])
        table_id = sup.compute_table_id(leader_id, [human_b_id])

        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"
        debrief_a = full_v7_save(CHAR_A, name="Avery", save_id="fixture-r6b-mensch-a-002", level=2)
        debrief_b = full_v7_save(CHAR_B, name="Blair", save_id="fixture-r6b-mensch-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet (R6-B geteilter Bildschirm), beide Standsicherungen anbei.\n"
            "```json\n" + json.dumps(debrief_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_b) + "\n```\n"
            + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path,
            responses=[
                "SL-Antwort auf den Leader-Anker (R6-B).",
                "SL-Antwort auf den Beitrag von Mensch B (R6-B).",
                debrief_text,
            ],
            calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        # ── Setup-Zeilen (gefuehrter 'g'-Weg, FIX4a/4b NICHT neu aufgerollt
        # -- bereits angenommener Kern, s. R5-B -- daher der SAUBERE Pfad
        # ohne absichtlichen Fehler/Ruecksprung):
        setup_lines = ["g", "2", "1", "j", "j", "", "", "j", "j"]

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

        _turn(leader_id, "Wir sichten gemeinsam die Lage am geteilten Terminal (R6-B).")
        _turn(human_b_id, "Ich uebernehme die rechte Flanke (R6-B).")
        _turn(leader_id, "Wir schliessen diesen Abschnitt kontrolliert ab (R6-B).")
        for m in members_sorted:
            if m == leader_id:
                _turn(leader_id, "Notiz Leader (R6-B): Uebergabe/Rueckuebergabe lief sauber.")
            elif m == human_b_id:
                _turn(human_b_id, "Notiz Mensch B (R6-B): eigener Beitrag eingebracht.")

        # ── Abschlusskarten: Leader (A) ZUERST ("1" = Export), dann Human B.
        # Bs Karte: '/stand' (G-R6-01 Punkt2, muss Bs EIGENEN Stand zeigen),
        # dann '3' (Gastfolge-Kartennummer: Export(1)/Zurueck(2)/Tischfolge
        # (3), s. Modultext), dann im echten Gastfolge-Untermenue '2'
        # (anfragen) + TABLE_KEY_B + '/zurueck' (echte NEUE Tischanfrage
        # unter Bs eigener guest_id -- G-R6-01 Punkt4). Danach uebernimmt
        # wieder A: '/stand' (muss wieder As eigene Figur zeigen, Punkt5)
        # und 'tisch' (A bleibt hostfaehig -- eigene Betreiberzeile [5]-[9]
        # real erreichbar, Punkt6) + '/zurueck', dann 'beenden'.
        card_lines = [
            "1",
            "/stand", "3", "2", TABLE_KEY_B, "/zurueck",
            "/stand", "tisch", "/zurueck",
            "beenden",
        ]

        stdin_lines = setup_lines + ["j"] + turn_lines + card_lines
        stdin_text = "\n".join(stdin_lines) + "\n"

        argv = [sys.executable, "-B", str(r4._REPO_ROOT / "scripts" / "mmo_sim.py"),
                "--data-dir", str(data_dir), "--participant", human_a_id]
        utc_start = r6.utc(time.time())
        popen = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        pid = popen.pid
        out, err = popen.communicate(input=stdin_text, timeout=90)
        utc_end = r6.utc(time.time())
        returncode = popen.returncode

        class _Proc:
            pass

        proc = _Proc()
        proc.returncode, proc.stdout, proc.stderr, proc.pid = returncode, out, err, pid
        assert proc.returncode == 0, f"R6-B: Prozess fehlgeschlagen rc={proc.returncode}\nSTDERR(tail)={proc.stderr[-2000:]}"

        assert "Lokale Runde einrichten" in out
        assert f"'{leader_id}' spielt '{CHAR_A}' -- bestaetigen?" in out
        assert f"'{human_b_id}' spielt '{CHAR_B}' -- bestaetigen?" in out
        assert f"Geteiltes Terminal wird an '{human_b_id}' (Figur '{CHAR_B}') uebergeben" in out
        assert f"[{human_b_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten?" in out, out[-2000:]
        assert "Abschnitt abgeschlossen:" in out, f"R6-B: Abschnitt nicht abgeschlossen: {out[-3000:]}"

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 3, f"R6-B: GENAU DREI reale GM-Rufe erwartet: {calls}"

        # ── Abschlusskarten-Belege (Punkt1, knapp bestaetigt -- R5-FIX2-Kern
        # NICHT neu aufgerollt): beide Karten gedruckt, Leader VOR Human B.
        assert f"-- Abschlusskarte fuer '{leader_id}' --" in out
        assert f"-- Abschlusskarte fuer '{human_b_id}' --" in out
        card_a_pos = out.index(f"-- Abschlusskarte fuer '{leader_id}' --")
        card_b_pos = out.index(f"-- Abschlusskarte fuer '{human_b_id}' --")
        assert card_a_pos < card_b_pos
        between_cards = out[card_a_pos:card_b_pos]
        after_card_b = out[card_b_pos:]

        # Punkt1 ("Richtigen eigenen Export weiter belegen ... nur
        # bestaetigen"): NUR A exportiert auf dieser Karte ("1") -- B waehlt
        # auf SEINER Karte bewusst die Gastfolge ("3", s.u., G-R6-01 Punkt3/
        # 4), ein Kartendispatch ist IMMER genau EINE Aktion. Bs eigener,
        # korrekt getrennter Stand wird unten direkt ueber `current_saves/
        # <human_b_id>.json` bestaetigt (von der Rundenfinalisierung IMMER
        # geschrieben, unabhaengig von der Kartenaktion).
        export_a_path = exports_dir / f"{leader_id}.json"
        assert export_a_path.exists(), f"R6-B Punkt1: As Export-Datei fehlt: {export_a_path}"
        export_a_block = json.loads(export_a_path.read_text(encoding="utf-8"))
        assert export_a_block["characters"][0]["id"] == CHAR_A, export_a_block

        def _first_fortsetzen_line(text: str) -> str | None:
            """Robuste Extraktion: die '/stand'-Antwort haengt OHNE eigenes
            Newline direkt an der Promptzeile ('input()' druckt den Prompt
            ohne Zeilenumbruch) -- ein `line.strip().startswith('Fortsetzen:')`
            trifft diese kombinierte Zeile deshalb NICHT. Statt zeilenweise zu
            filtern, wird die ERSTE 'Fortsetzen:'-Teilzeichenkette gesucht und
            bis zum naechsten Newline genommen (funktioniert fuer BEIDE Faelle:
            die eigenstaendige, eingerueckte Menuezeile UND die an den Prompt
            angehaengte '/stand'-Antwort)."""
            idx = text.find("Fortsetzen:")
            if idx == -1:
                return None
            end = text.find("\n", idx)
            return (text[idx:end] if end != -1 else text[idx:]).strip()

        # ═══ G-R6-01 Punkt2: '/stand' GENAU an Bs Karten-Read -- Bs EIGENE
        # Figur/Stand, KEINE fremde A-Anzeige. ═══
        stand_section = after_card_b.split(f"-- Abschlusskarte fuer '{human_b_id}' --", 1)[1]
        first_stand_b = _first_fortsetzen_line(stand_section)
        assert first_stand_b is not None, ("R6-B/G-R6-01 Punkt2: keine 'Fortsetzen:'-Stelle fuer Bs '/stand' gefunden.", out[-4000:])
        assert human_b_id in first_stand_b and CHAR_B in first_stand_b, (
            "R6-B/G-R6-01 Punkt2: Bs '/stand' haette DEREN EIGENEN Stand zeigen muessen.", first_stand_b,
        )
        assert human_a_id not in first_stand_b and CHAR_A not in first_stand_b, (
            "R6-B/G-R6-01 Punkt2: Bs '/stand' haette NICHT die fremde A-Anzeige zeigen duerfen.", first_stand_b,
        )

        # ═══ G-R6-01 Punkt3: Gastfolge-Untermenue (Wahl '3') zeigt KEINE
        # fremden Hostoptionen fuer B. Eng auf GENAU Bs eigene Gastfolge-
        # Sitzung begrenzt (vom ersten Untermenue-Kopf bis zur eigenen
        # Anfragebestaetigung) -- A bekommt SPAETER real seine eigene
        # Betreiberzeile (s. Punkt6), die darf hier nicht faelschlich
        # mitgezaehlt werden. ═══
        submenu_start = stand_section.find("Tisch -- [1] Offene Tische suchen")
        assert submenu_start != -1, (
            "R6-B/G-R6-01 Punkt3: Bs Gastfolge haette das reale Tisch-Untermenue zeigen muessen.",
            stand_section[:2000],
        )
        confirm_marker = f"Anfrage an Tisch '{TABLE_KEY_B}' gestellt"
        confirm_pos = stand_section.find(confirm_marker, submenu_start)
        assert confirm_pos != -1, (
            "R6-B/G-R6-01 Punkt4: die Tischanfrage-Bestaetigung fehlt.", stand_section[submenu_start:submenu_start + 2000],
        )
        tisch_folge_region = stand_section[submenu_start:confirm_pos + len(confirm_marker)]
        assert "Betreiber/Host -- [5]" not in tisch_folge_region, (
            "R6-B/G-R6-01 Punkt3: KEINE fremden Hostoptionen fuer B in dessen eigener Gastfolge-"
            f"Sitzung: {tisch_folge_region[:2000]}"
        )

        # ═══ G-R6-01 Punkt4: ECHTE NEUE Tischanfrage unter Bs eigener
        # guest_id/Figur/Save; A bleibt unberuehrt. ═══
        record = table_admission.load_record(run_dir, TABLE_KEY_B)
        assert record is not None
        assert human_b_id in record["requests"], (
            "R6-B/G-R6-01 Punkt4: die ECHTE Tischanfrage haette unter Bs guest_id landen muessen.", record,
        )
        assert human_a_id not in record["requests"], (
            "R6-B/G-R6-01 Punkt4: A darf durch Bs Gastfolge KEINE eigene Anfrage bekommen.", record,
        )
        offer_dir = run_dir / "table_guest_offers"
        offer_names = [p.name for p in offer_dir.glob(f"{TABLE_KEY_B}__*.json")] if offer_dir.exists() else []
        assert any(human_b_id in n for n in offer_names), (
            "R6-B/G-R6-01 Punkt4: es haette ein Gastangebot unter Bs guest_id entstehen muessen.", offer_names,
        )
        assert not any(human_a_id in n for n in offer_names), (
            "R6-B/G-R6-01 Punkt4: KEIN Gastangebot unter As guest_id.", offer_names,
        )
        offered_char = None
        for name in offer_names:
            if human_b_id in name:
                offered_block = json.loads((offer_dir / name).read_text(encoding="utf-8"))
                offered_char = offered_block.get("chrononaut_id")
                break
        assert offered_char == CHAR_B, (
            "R6-B/G-R6-01 Punkt4: das angebotene Gastangebot haette Bs EIGENE Figur tragen muessen "
            f"(nicht As): {offered_char!r}"
        )

        # ═══ G-R6-01 Punkt5: Fokus-/Menuerueckgabe real -- naechstes
        # '/stand' (jetzt wieder bei A) zeigt wieder As EIGENE Figur. ═══
        after_b_submenu = stand_section[confirm_pos + len(confirm_marker):]
        first_stand_after_return = _first_fortsetzen_line(after_b_submenu)
        assert first_stand_after_return is not None, (
            "R6-B/G-R6-01 Punkt5: keine 'Fortsetzen:'-Stelle fuer As '/stand' NACH der Fokusrueckgabe gefunden.",
            after_b_submenu[:3000],
        )
        assert human_a_id in first_stand_after_return and CHAR_A in first_stand_after_return, (
            "R6-B/G-R6-01 Punkt5: nach der Fokusrueckgabe haette As eigener Stand gezeigt werden "
            f"muessen: {first_stand_after_return!r}"
        )
        assert human_b_id not in first_stand_after_return and CHAR_B not in first_stand_after_return, (
            "R6-B/G-R6-01 Punkt5: nach der Fokusrueckgabe darf NICHT weiterhin Bs Stand gezeigt "
            f"werden: {first_stand_after_return!r}"
        )

        # ═══ G-R6-01 Punkt6: A bleibt real hostfaehig -- eigene
        # Betreiberzeile [5]-[9] erreichbar (eigener 'tisch'-Aufruf). ═══
        after_a_stand = after_b_submenu.split(first_stand_after_return, 1)[1]
        assert "Betreiber/Host -- [5]" in after_a_stand, (
            "R6-B/G-R6-01 Punkt6: As eigener 'tisch'-Aufruf haette weiterhin die Betreiberzeile "
            f"[5]-[9] zeigen muessen (A bleibt hostfaehig): {after_a_stand[:2000]}"
        )

        # ── Byte-/inhaltlicher Abgleich (Punkt1, knapp bestaetigt): As
        # Export == As tatsaechlich akzeptierter eigener Current. Bs eigener
        # Current (OHNE Export auf dieser Karte, s.o.) wird direkt gegen
        # SEINE EIGENE Figur/Level geprueft -- belegt die korrekte Trennung
        # von As Stand, unabhaengig von der Kartenaktion.
        current_a_path = run_dir / "current_saves" / f"{leader_id}.json"
        current_b_path = run_dir / "current_saves" / f"{human_b_id}.json"
        current_a_block = json.loads(current_a_path.read_text(encoding="utf-8"))
        assert current_b_path.exists(), f"R6-B: Bs eigener Current-Save fehlt: {current_b_path}"
        current_b_block = json.loads(current_b_path.read_text(encoding="utf-8"))
        export_a_match = export_a_block == current_a_block
        assert export_a_match, (export_a_block, current_a_block)
        assert current_b_block["characters"][0]["id"] == CHAR_B, current_b_block
        assert current_b_block["characters"][0]["lvl"] == 2, current_b_block

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
        _write_procmeta(
            out_dir, "shared_screen_launcher", argv=argv, cwd=str(_REPO_ROOT), pid=proc.pid,
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
        )
        mf.record_process_files(
            "shared_screen_launcher", aussage="r6b_shared_screen_full_transcript",
            run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur="beide", tisch_abschnitt=f"{table_id}-section/{TABLE_KEY_B}",
        )
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r6b_gm_double_calls", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur="beide")
        mf.export_file(export_a_path, "human_a_export.json", aussage="r6b_human_a_export_fix2_bestaetigt", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur=leader_id)
        mf.export_file(current_a_path, "human_a_current.json", aussage="r6b_human_a_current", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur=leader_id)
        mf.export_file(current_b_path, "human_b_current.json", aussage="r6b_human_b_current", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur=human_b_id)
        mf.export_tree(run_dir, "run", aussage="r6b_run_dir_after_finish", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur="beide")
        sends_path = out_dir / "sends.jsonl"
        sends_events = []
        offset = 0
        for i, line in enumerate(stdin_lines):
            sends_events.append({
                "channel": "shared_screen_single_stdin", "order": i, "sent": line,
                "note": "Reihenfolge ist die reale stdin-Zeilenreihenfolge der einzigen gemeinsamen "
                        "Pipe; jede Zeile setzt auf dem direkt davor im echten stdout beobachteten "
                        "Prompt/Zustand des Schrittautomaten auf (s. Moduldocstring/Kommentare).",
            })
        sends_path.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in sends_events) + "\n", encoding="utf-8",
        )
        mf.entries.append({
            "aussage": "r6b_sendereihenfolge_single_stdin", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-B-PERSON-B-SELBST",
            "path": str(sends_path.relative_to(out_dir)), "sha256": r6.sha256_of(sends_path),
            "bytes": sends_path.stat().st_size,
        })
        mf.write_json_body(
            "g_r6_01_kernbeleg.json",
            {
                "stand_section_bs_eigener_stand": first_stand_b,
                "gastfolge_untermenue_text": tisch_folge_region[:4000],
                "table_record_requests": record["requests"],
                "offer_names": offer_names,
                "offered_char_fuer_b": offered_char,
                "stand_nach_fokusrueckgabe_an_a": first_stand_after_return,
                "a_bleibt_hostfaehig_text": after_a_stand[:1500],
            },
            aussage="r6b_g_r6_01_kernbeleg", run_id="R6-B-PERSON-B-SELBST", teilnehmer_figur="beide",
        )
        merged_path = out_dir / "MERGED_PROTOKOLL.md"
        merged_path.write_text(
            _git_codeanchor() + "\n\n"
            "ABGELEITETES, zusammengefuegtes Protokoll (R6-B Person B selbst/G-R6-01) -- "
            "KEINE Originaldatei, reine Lesehilfe. Das Original ist "
            "shared_screen_launcher.stdout.txt (unveraendert, vollstaendig ab Prozessstart, "
            "EIN geteiltes Terminal).\n\n== Shared-Screen-Kanal ==\n" + out + "\n",
            encoding="utf-8",
        )
        mf.entries.append({
            "aussage": "r6b_abgeleitetes_merged_protokoll", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-B-PERSON-B-SELBST",
            "path": str(merged_path.relative_to(out_dir)), "sha256": r6.sha256_of(merged_path),
            "bytes": merged_path.stat().st_size,
        })
        mf.write_manifest()
        mf.write_summary({
            "szene": "R6_B_person_b_selbst_g_r6_01",
            "aussage": (
                "EIN geteiltes Terminal, zwei verschiedene registrierte Menschen. Export bleibt "
                "korrekt an pid gebunden (R5-Fix bestaetigt). An Bs Karten-Read zeigt '/stand' "
                "Bs EIGENEN Stand (nicht As). Bs Gastfolge (Kartennummer 3) zeigt KEINE fremden "
                "Hostoptionen und fuehrt eine ECHTE NEUE Tischanfrage unter Bs eigener guest_id/"
                "Figur aus; A bleibt in dieser Anfrage/dem Gastangebot unberuehrt. Fokus-/"
                "Menuerueckgabe an A ist real durchgefuehrt ('/stand' zeigt danach wieder As "
                "eigenen Stand); A bleibt hostfaehig (eigene Betreiberzeile [5]-[9] weiterhin "
                "real erreichbar)."
            ),
            "echter_subprozess": True, "ein_geteiltes_terminal": True,
            "anzahl_gm_rufe": len(calls), "leader": leader_id, "person_b": human_b_id,
            "stand_an_bs_karte_zeigt_b_nicht_a": (human_b_id in first_stand_b and human_a_id not in first_stand_b),
            "gastfolge_keine_fremden_hostoptionen": "Betreiber/Host -- [5]" not in tisch_folge_region[: tisch_folge_region.find("Anfrage an Tisch") + 200],
            "echte_neue_tischanfrage_unter_b": human_b_id in record["requests"],
            "a_unberuehrt_in_anfrage": human_a_id not in record["requests"],
            "angebotene_figur_ist_b": offered_char == CHAR_B,
            "fokusrueckgabe_an_a_real": (human_a_id in first_stand_after_return),
            "a_bleibt_hostfaehig": "Betreiber/Host -- [5]" in after_a_stand,
            "export_a_byte_match_current": export_a_match, "current_b_korrekt_eigenstaendig": current_b_block["characters"][0]["id"] == CHAR_B,
            "table_closed": table.status == "closed",
        })

        findings["returncode"] = proc.returncode
        findings["gm_calls"] = len(calls)
        findings["stand_b_korrekt"] = (human_b_id in first_stand_b and human_a_id not in first_stand_b)
        findings["neue_tischanfrage_unter_b"] = human_b_id in record["requests"]
        findings["a_bleibt_hostfaehig"] = "Betreiber/Host -- [5]" in after_a_stand
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_b()
        print(f"OK   R6_B_person_b_selbst: {findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R6_B_person_b_selbst: {e}")
        return 1
    except Exception:
        print("ERROR R6_B_person_b_selbst:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
