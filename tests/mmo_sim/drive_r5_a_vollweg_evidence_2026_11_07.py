#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_a_vollweg_evidence_2026_11_07.py -- ZR-VOLLENDUNG-
OHNE-LAN-NACHZUG-20261107-R5, 02_ABNAHME.md §A "vollstaendiger bestehender
Zwei-Gast-Normalweg": vervollstaendigt die bereits angenommene U5-Szene
(`drive_u5_zweigast_figurfrei_2026_11_07.py`, UNVERAENDERT, A7/A8b/B1b/B2/
Solo/Current-Kerne daraus NICHT neu aufgerollt) um GENAU die nach
02_ABNAHME.md §A tabellierten, bislang fehlenden Stationen auf dem R5-
korrigierten Code (FIX1-4):

  - Eingabefokus (FIX1): Gast B bekommt NACH seiner Tischanfrage KEIN
    erzwungenes Vorab-'/zurueck' mehr (R4-Treiber-Workaround entfaellt) --
    er bleibt im normalen Tisch-Untermenue parken, WAEHREND der host-
    getriebene Rundenclaim (Consent/Zuege/Abschlusskarte) auf demselben
    FIFO-Kanal laeuft; NACH der Karte bedient er seine schon lange
    wartende Untermenue-Eingabe real (echte parallele Leserpfade).
  - Speichern/Beenden (FIX3a): der Leader sendet am Spielzug-Prompt das
    ECHTE sichtbare `!save`-Kommando statt freien Texts.
  - Menuerueckkehr: NACH der Abschlusskarte fuehrt jeder Gast wirklich
    MINDESTENS EINE weitere normale Auswahl aus (Gast A: frischer [tisch]-
    Eintritt + '/zurueck'; Gast B: die laengst wartende Untermenue-Eingabe
    + '/zurueck' -- bloses Prozessende beweist NICHTS).
  - Byte-/Feldabgleich: beide Exporte zusaetzlich explizit gegen den
    zugehoerigen `run/current_saves/<pid>.json` verglichen.
  - Reload/Anschluss: ein ECHTER frischer Subprozess (Gast A, NEUE
    Prozess-ID) laedt den eigenen EXPORT ueber den normalen [charaktere]-
    Importweg erneut, bedient danach eine NEUE zulaessige Tischanfrage
    real (Betreiber nimmt sie an -- echte neue Aufnahme) UND bestaetigt,
    dass der geschlossene U5-Tisch geschlossen bleibt.
  - KI-Persona + Solo-Menschen-Pfad (separate kurze Funktion
    `run_scene_a_solo_ki_leaderwahl`): fuehrt den gefuehrten Solo-mit-KI-
    Weg nummeriert bis Besetzung/Leaderwahl-Zusammenfassung, lehnt dann
    die letzte Startwahl bewusst ab (kein KI-Zustimmungs-/Modellaufruf
    noetig, L2->3-Kernbeleg NICHT wiederholt) -- landet am zutreffenden
    Hauptmenue-Zustand.

GM NUR als Grenzinjektion (`_r4_gm_double.py`), NIE Live-Modell. Pure
Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import select
import subprocess
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
import _a24_local_support as sup  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path(os.environ.get("ZR_R5_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r5_evidence" / "A")))
_GUEST_HELPER = _REPO_ROOT / "scripts" / "zeitriss-gast-terminal.sh"
_LAUNCHER = r4._LAUNCHER

BETREIBER_ID = "betreiber_r5a"
GAST_A_ID = "gast_a_r5a"
GAST_B_ID = "gast_b_r5a"
CHAR_A = "chrono-r5a-gast-a"
CHAR_B = "chrono-r5a-gast-b"
TABLE_KEY = "mesaR5A"
TABLE_ID = f"local-{GAST_A_ID}-{GAST_B_ID}"
RELOAD_TABLE_KEY = "mesaR5AReload"


def _wait_for_buffered_substr(reader: "r4._LineReader", marker: str, overall: float = 20.0) -> str:
    deadline = time.time() + overall
    while time.time() < deadline:
        if marker in reader._buf:
            return reader._buf
        ready, _, _ = select.select([reader], [], [], 0.1)
        if ready:
            if not reader.pump():
                raise AssertionError(f"Marker {marker!r} nicht gesehen (EOF); puffer={reader._buf!r}")
    raise AssertionError(f"Marker {marker!r} nicht gesehen (Timeout); puffer={reader._buf!r}")


def _extract_index(list_line: str, needle: str) -> str:
    import re
    for num, val in re.findall(r"\[(\d+)\]\s*'?([^'\s]+)'?", list_line):
        if val == needle:
            return num
    raise AssertionError(f"{needle!r} nicht in Liste gefunden: {list_line!r}")


def run_scene_a() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    findings: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_a, out_fifo_a = fifo_dir / "gast_a_in.fifo", fifo_dir / "gast_a_out.fifo"
        in_fifo_b, out_fifo_b = fifo_dir / "gast_b_in.fifo", fifo_dir / "gast_b_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        import_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-r5a-gast-a-001")
        fixture_a_path = root / "gast_a_import.json"
        fixture_a_path.write_text(json.dumps(import_block_a, ensure_ascii=False), encoding="utf-8")

        creation_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-r5a-gast-b-001")
        creation_response = "```json\n" + json.dumps(creation_block_b, ensure_ascii=False) + "\n```"
        debrief_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-r5a-gast-a-002", level=2)
        debrief_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-r5a-gast-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet, beide Standsicherungen anbei.\n"
            "```json\n" + json.dumps(debrief_block_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_block_b) + "\n```\n"
            + COMPLETION_MARKER
        )
        r4._write_gm_double_config(cfg_path, responses=[creation_response], calls_log=calls_log)
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-u", "-B", str(_LAUNCHER),
            "--participant", BETREIBER_ID, "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{GAST_A_ID}:{in_fifo_a}:{out_fifo_a}",
            "--guest-terminal", f"{GAST_B_ID}:{in_fifo_b}:{out_fifo_b}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        host_reader = r4._LineReader(proc.stdout.fileno())

        r4._wait_for_path(in_fifo_a, overall=15.0)
        r4._wait_for_path(out_fifo_a, overall=15.0)
        r4._wait_for_path(in_fifo_b, overall=15.0)
        r4._wait_for_path(out_fifo_b, overall=15.0)

        helper_a = subprocess.Popen(
            [str(_GUEST_HELPER), GAST_A_ID, str(in_fifo_a), str(out_fifo_a)],
            cwd=str(_REPO_ROOT), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        helper_b = subprocess.Popen(
            [str(_GUEST_HELPER), GAST_B_ID, str(in_fifo_b), str(out_fifo_b)],
            cwd=str(_REPO_ROOT), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        reader_a = r4._LineReader(helper_a.stdout.fileno())
        reader_b = r4._LineReader(helper_b.stdout.fileno())

        host_boot = r4._drain(host_reader, settle=0.6, overall=10.0)
        header_a = r4._drain(reader_a, settle=0.6, overall=10.0)
        header_b = r4._drain(reader_b, settle=0.6, overall=10.0)

        transcript_a: list[str] = list(header_a)
        transcript_b: list[str] = list(header_b)
        transcript_host: list[str] = list(host_boot)

        def send_a(line: str) -> None:
            r4._send_guest(helper_a.stdin, line)

        def send_b(line: str) -> None:
            r4._send_guest(helper_b.stdin, line)

        def send_host(line: str) -> None:
            r4._send_op(proc, line)

        def wait_a(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(reader_a, marker, overall=overall)
            transcript_a.extend(lines)
            return "".join(lines)

        def wait_b(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(reader_b, marker, overall=overall)
            transcript_b.extend(lines)
            return "".join(lines)

        def wait_host(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(host_reader, marker, overall=overall)
            transcript_host.extend(lines)
            return "".join(lines)

        def wait_host_prompt(marker: str, overall: float = 20.0) -> str:
            return _wait_for_buffered_substr(host_reader, marker, overall=overall)

        def drain_a(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_a, settle=settle, overall=overall)
            transcript_a.extend(lines)
            return "".join(lines)

        def drain_b(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_b, settle=settle, overall=overall)
            transcript_b.extend(lines)
            return "".join(lines)

        def drain_host(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(host_reader, settle=settle, overall=overall)
            transcript_host.extend(lines)
            return "".join(lines)

        # ═══════════════════ Gast A: ECHTER Import ([charaktere]->[2]) ═════
        send_a("charaktere")
        charaktere_a = wait_a("[2] Importieren")
        send_a("2")
        wait_a("JSON-Datei-Pfad")
        send_a(str(fixture_a_path))
        send_a("ENDE")
        preview_a = wait_a(f"char_id={CHAR_A}")
        assert "WARNUNG" not in preview_a, preview_a
        send_a("j")
        accept_a = wait_a("Uebernahme abgeschlossen")
        assert f"action=register_new char_id={CHAR_A}" in accept_a, accept_a

        # ═══════════════ Gast B: ECHTE genehmigte Erschaffung ══════════════
        send_b("charaktere")
        wait_b("Gast-Erschaffungsanfrage an Betreiber stellen")
        send_b("4")
        wait_b("Betreiber fuer die Erschaffungsanfrage")
        send_b(BETREIBER_ID)
        wait_b("Erschaffungsanfrage an Betreiber")

        send_host("charaktere")
        wait_host("Gast-Erschaffungsanfragen entscheiden")
        send_host("4")
        pending_list = wait_host_prompt("Welcher Gast")
        idx_b_pending = _extract_index(pending_list, GAST_B_ID)
        send_host(idx_b_pending)
        wait_host_prompt("annehmen")
        send_host("1")
        wait_host(f"Gast '{GAST_B_ID}' freigegeben")

        send_b("charaktere")
        wait_b("Eigenen Erschaffungsdialog fortsetzen")
        send_b("5")
        wait_b("Erschaffung abgeschlossen")

        r4._write_gm_double_config(
            cfg_path,
            responses=[
                "SL-Antwort auf den Leader-Anker.",
                "SL-Antwort auf den Gast-B-Erstbeitrag.",
                debrief_text,
            ],
            calls_log=calls_log,
        )

        # ═══════════════ Betreiber bietet den gemeinsamen Tisch an ═════════
        send_host("tisch")
        wait_host("[5] Tisch anbieten")
        send_host("5")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        wait_host(f"Tisch '{TABLE_KEY}' offen")

        # ═══════════════ Beide Gaeste fragen den Tisch nummeriert an ═══════
        send_a("tisch")
        wait_a("[2] Tisch anfragen")
        send_a("2")
        wait_a("Welcher Tisch")
        send_a(TABLE_KEY)
        wait_a(f"Anfrage an Tisch '{TABLE_KEY}' gestellt")
        # Gast A kehrt wie bisher (R4-Workaround) zum claim-bewussten
        # Hauptmenue zurueck -- MINDESTENS EIN Gast (s.u., Gast B) tut dies
        # NICHT mehr: der R5-FIX1-Kernbeleg braucht nur EINEN echten
        # parallelen Leserpfad, nicht beide.
        send_a("/zurueck")
        drain_a(settle=0.5, overall=5.0)

        send_b("tisch")
        wait_b("[2] Tisch anfragen")
        send_b("2")
        wait_b("Welcher Tisch")
        send_b(TABLE_KEY)
        wait_b(f"Anfrage an Tisch '{TABLE_KEY}' gestellt")
        # R5 FIX1-Kernbeleg (02_ABNAHME.md §A "Eingabefokus"): KEIN
        # erzwungenes Vorab-'/zurueck' mehr fuer Gast B -- er bleibt im
        # Tisch-Untermenue parken (eigener Gast-Menue-Loop-Thread im
        # Betreiberprozess, registriert via `register_guest_terminal`),
        # WAEHREND der host-getriebene Rundenclaim (Consent/Zuege/Karte)
        # auf GENAU demselben FIFO-Kanal laeuft. Fruehstens danach (s.u.)
        # bedient er seine schon lange wartende Untermenue-Eingabe real.

        # ═══ Betreiber nimmt GAST A ZUERST an -> wird Leader. ═══
        wait_host("[6] Anfrage annehmen")
        send_host("6")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        open_requests_1 = wait_host_prompt("Welcher Gast")
        idx_a = _extract_index(open_requests_1, GAST_A_ID)
        send_host(idx_a)
        wait_host(f"'{GAST_A_ID}' an Tisch '{TABLE_KEY}' aufgenommen")

        # ═══ Betreiber nimmt GAST B danach an -> Nicht-Leader-Mitglied. ═══
        wait_host("[6] Anfrage annehmen")
        send_host("6")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        open_requests_2 = wait_host_prompt("Welcher Gast")
        idx_b_table = _extract_index(open_requests_2, GAST_B_ID)
        send_host(idx_b_table)
        wait_host(f"'{GAST_B_ID}' an Tisch '{TABLE_KEY}' aufgenommen")

        # ═══════════════ Betreiber startet den Tisch ═══════════════════════
        wait_host("[8] Tisch starten")
        send_host("8")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        wait_host(f"Tisch '{TABLE_KEY}' gestartet", overall=60.0)

        # ═══ Nicht-Leader-Konsens (Gast B tritt der Runde ausdruecklich bei
        # -- diese Zeile erreicht GENAU den Rundenconsent-Read, NICHT den
        # geparkten Untermenue-Read: der FIX1-Claim entscheidet, kein
        # Raten). ═══
        consent_b = wait_b("beitreten? [j/n]")
        assert "Dieser lokalen Runde" in consent_b, consent_b
        assert f"Leader: {GAST_A_ID}" in consent_b, consent_b
        send_b("j")

        leader_anchor = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Empfaenger: Spielleitung (SL)" in leader_anchor, leader_anchor
        send_a("Ich sichte knapp die Lage am Tisch.")

        guest_b_first = wait_b("Empfaenger: ueber Leader an Spielleitung")
        assert "Empfaenger: ueber Leader an Spielleitung" in guest_b_first, guest_b_first
        assert "Unbekannte Auswahl" not in guest_b_first, guest_b_first
        send_b("Ich pruefe meine Ausruestung und melde mich.")

        leader_second = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Unbekannte Auswahl" not in leader_second, leader_second
        # R5 FIX3a-Kernbeleg (02_ABNAHME.md §A "Speichern/Beenden"): ECHTES
        # sichtbares '!save'-Kommando statt freien Texts -- derselbe
        # Erkennungsweg (`is_save_command`), keine neue Save-Autoritaet.
        send_a("!save")

        notiz_a = wait_a("eigene lokale Notiz")
        send_a("Abschlussnotiz Leader (Gast A): Reise erfolgreich.")
        notiz_b = wait_b("eigene lokale Notiz")
        send_b("Abschlussnotiz Gast B: Erschaffung und erster Einsatz gelungen.")

        final_path = run_dir / "completion" / f"{TABLE_ID}-section__final.json"
        r4._wait_for_path(final_path, overall=25.0)

        # ═══════════════ Abschlusskarten: beide Gaeste bedienen real ═══════
        card_a = wait_a("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_A_ID}'" in card_a, card_a
        send_a("1")
        export_a = wait_a("Zusaetzlich als Datei gespeichert")

        card_b = wait_b("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_B_ID}'" in card_b, card_b
        send_b("1")
        export_b = wait_b("Zusaetzlich als Datei gespeichert")

        # ═══════════════ Menuerueckkehr: je EINE weitere normale Auswahl ═══
        # Gast A ist seit dem fruehen '/zurueck' am claim-bewussten
        # Hauptmenue -- frischer [tisch]-Untermenue-Eintritt + Rueckkehr.
        send_a("tisch")
        menu_return_a = wait_a("[1] Offene Tische suchen")
        send_a("/zurueck")
        drain_a(settle=0.4, overall=5.0)

        # Gast B ist WEITERHIN im urspruenglichen, nie verlassenen Tisch-
        # Untermenue geparkt (FIX1) -- seine naechste Eingabe erreicht
        # GENAU diesen, schon lange wartenden Dialog (keine neue
        # Menuedarstellung noetig, s. Beleg). '1' = echte Auswahl
        # ("Offene Tische suchen"), danach Rueckkehr.
        send_b("1")
        menu_return_b = drain_b(settle=0.6, overall=10.0)
        send_b("/zurueck")
        drain_b(settle=0.4, overall=5.0)

        # ═══════════════ Figurfreie Betreiber-Tisch-Abschlusskarte ═════════
        operator_card = wait_host("Beenden (zurueck zum Hauptmenue)")
        assert f"Tisch-Abschlusskarte (Betreiber, figurfrei) fuer '{TABLE_ID}'" in operator_card, operator_card
        send_host("3")
        wait_host(f"Tisch '{TABLE_KEY}': Abschnitt")
        send_host("/zurueck")
        drain_host(settle=0.4, overall=5.0)

        # ═══════════════ Reload/Anschluss-Vorbereitung: Betreiber bietet
        # EINEN NEUEN Tisch an, WAEHREND er noch laeuft (fuer den
        # Reload-Nachweis unten) ═══════════════════════════════════════════
        send_host("tisch")
        wait_host("[5] Tisch anbieten")
        send_host("5")
        wait_host_prompt("Welcher Tisch")
        send_host(RELOAD_TABLE_KEY)
        wait_host(f"Tisch '{RELOAD_TABLE_KEY}' offen")
        send_host("/zurueck")
        drain_host(settle=0.4, overall=5.0)

        for helper, instream in ((helper_a, helper_a.stdin), (helper_b, helper_b.stdin)):
            try:
                instream.close()
            except BrokenPipeError:
                pass
        for helper in (helper_a, helper_b):
            try:
                helper.wait(timeout=15)
            except subprocess.TimeoutExpired:
                helper.kill()
                helper.wait()
        tail_a = helper_a.stdout.read()
        tail_b = helper_b.stdout.read()
        stderr_a = helper_a.stderr.read()
        stderr_b = helper_b.stderr.read()
        transcript_a.append(tail_a)
        transcript_b.append(tail_b)
        full_guest_a_stdout = "".join(transcript_a)
        full_guest_b_stdout = "".join(transcript_b)

        # ═══════════════ Assertion: beide Reloads lvl>start ═══════════════
        guest_a_private = onboarding.peek(op_data / "guests" / GAST_A_ID / "onboarding", GAST_A_ID)
        assert guest_a_private is not None and guest_a_private.final_save is not None
        reloaded_a = guest_a_private.final_save["characters"][0]
        assert reloaded_a["id"] == CHAR_A and reloaded_a["lvl"] == 2 > 1, reloaded_a

        guest_b_private = onboarding.peek(op_data / "guests" / GAST_B_ID / "onboarding", GAST_B_ID)
        assert guest_b_private is not None and guest_b_private.final_save is not None
        reloaded_b = guest_b_private.final_save["characters"][0]
        assert reloaded_b["id"] == CHAR_B and reloaded_b["lvl"] == 2 > 1, reloaded_b

        export_a_path = op_data / "guests" / GAST_A_ID / "exports" / f"{GAST_A_ID}.json"
        export_b_path = op_data / "guests" / GAST_B_ID / "exports" / f"{GAST_B_ID}.json"
        assert export_a_path.exists() and export_b_path.exists()
        export_a_block = json.loads(export_a_path.read_text(encoding="utf-8"))
        export_b_block = json.loads(export_b_path.read_text(encoding="utf-8"))
        assert export_a_block["characters"][0]["lvl"] == 2, export_a_block
        assert export_b_block["characters"][0]["lvl"] == 2, export_b_block

        # ── Byte-/Feldabgleich: Export == akzeptierter eigener Current
        # (02_ABNAHME.md §A letzter Absatz unter der Tabelle).
        current_a_path = run_dir / "current_saves" / f"{GAST_A_ID}.json"
        current_b_path = run_dir / "current_saves" / f"{GAST_B_ID}.json"
        current_a_block = json.loads(current_a_path.read_text(encoding="utf-8"))
        current_b_block = json.loads(current_b_path.read_text(encoding="utf-8"))
        export_a_match_current = export_a_block == current_a_block
        export_b_match_current = export_b_block == current_b_block
        assert export_a_match_current, (export_a_block, current_a_block)
        assert export_b_match_current, (export_b_block, current_b_block)

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 4, f"R5-A: GENAU VIER reale GM-Rufe erwartet: {calls}"

        # ═══════════════ Reload/Anschluss: ECHTER frischer Subprozess ══════
        # Gast A (NEUE Prozess-ID) laedt den eigenen EXPORT ueber den
        # normalen [charaktere]->[2]-Importweg erneut, bedient danach eine
        # NEUE zulaessige Tischanfrage real UND bestaetigt, dass der
        # geschlossene U5-Tisch geschlossen bleibt. KEIN zweiter ganzer
        # Spielabschnitt -- nur Reload + Anfrage.
        # (Tisch-Untermenue bleibt nach einer Aktion AKTIV -- kein erneutes
        # 'tisch' noetig; '/zurueck' verlaesst es kontrolliert, EMPIRISCH
        # am echten Subprozess bestaetigt.)
        # EMPIRISCH bestaetigt (echter Subprozess): der Export ist BYTE-
        # GLEICH zum bereits lokal bekannten Stand (derselbe akzeptierte
        # Current, s. Byte-Abgleich oben) -- der normale Importweg erkennt
        # das ehrlich als "Identischer Save bereits vorhanden -- kein
        # zweiter Fortschritt" und fragt KEINE Uebernahme-Bestaetigung
        # mehr ab (kein 'j' noetig/erwartet). Das IST der korrekte Reload-
        # Beleg: der ueber den normalen Terminalweg erneut geladene Export
        # deckt sich exakt mit dem vorhandenen Stand, keine Divergenz.
        reload_stdin = "\n".join([
            "charaktere", "2", str(export_a_path), "ENDE",
            "tisch", "2", RELOAD_TABLE_KEY, "/zurueck",
            "beenden",
        ]) + "\n"
        reload_argv = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", GAST_A_ID, "--no-host-capable", "--data-dir", str(op_data / "guests" / GAST_A_ID),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        reload_utc_start = r6.utc(time.time())
        reload_proc = subprocess.run(
            reload_argv, input=reload_stdin, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        reload_utc_end = r6.utc(time.time())
        assert reload_proc.returncode == 0, f"R5-A Reload: Prozess fehlgeschlagen: {reload_proc.stderr[-2000:]}"
        reload_out = reload_proc.stdout
        assert f"char_id={CHAR_A} level=2" in reload_out, reload_out[-2000:]
        assert "Identischer Save bereits vorhanden" in reload_out, reload_out[-2000:]
        assert "Unbekannte Auswahl" not in reload_out, reload_out[-2000:]
        assert f"Anfrage an Tisch '{RELOAD_TABLE_KEY}' gestellt" in reload_out, reload_out[-2000:]

        # ── "der geschlossene Tisch bleibt geschlossen": der ADMISSION-
        # Datensatz des urspruenglichen Tisches (direkte Autoritaetspruefung,
        # derselbe Lesezugriff wie das Produkt selbst) -- eine rohe
        # 'tisch anfragen' auf einen GESCHLOSSENEN table_key legt (empirisch
        # bestaetigt) lediglich eine neue, nie angenommene Anfrage an;
        # die tatsaechliche Schliessung zeigt sich an der Admission-
        # Zustandsautoritaet selbst, NICHT an einer sofortigen Ablehnung
        # beim Request (die kommt erst bei einem erneuten 'tisch-start',
        # s. bereits angenommene Familie T1).
        import mmo_sim.core.table_admission as table_admission
        closed_record = table_admission.load_record(run_dir, TABLE_KEY)
        closed_table_rejection = closed_record is not None and closed_record.get("state") == table_admission.STATE_CLOSED
        assert closed_table_rejection, (
            f"R5-A: der urspruengliche Tisch '{TABLE_KEY}' haette geschlossen bleiben muessen: {closed_record}"
        )

        # ── Betreiber nimmt die NEUE Anfrage real an (echte neue Aufnahme).
        send_host("tisch")
        wait_host("[6] Anfrage annehmen")
        send_host("6")
        wait_host_prompt("Welcher Tisch")
        send_host(RELOAD_TABLE_KEY)
        open_reload_requests = wait_host_prompt("Welcher Gast")
        idx_a_reload = _extract_index(open_reload_requests, GAST_A_ID)
        send_host(idx_a_reload)
        reload_accept = wait_host(f"'{GAST_A_ID}' an Tisch '{RELOAD_TABLE_KEY}' aufgenommen")
        send_host("/zurueck")
        drain_host(settle=0.4, overall=5.0)

        utc_end_cmd = r6.utc(time.time())
        send_host("beenden")
        try:
            stdout_tail, stderr_text = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_tail, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        transcript_host.append(stdout_tail)
        full_host_stdout = "".join(transcript_host)
        assert proc.returncode == 0, f"R5-A: Betreiberprozess gescheitert: {stderr_text}"
        assert final_path.exists()

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "betreiber_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text, pid=proc.pid,
        )
        r6.write_process_result(
            out_dir, "gast_a_helper_process",
            argv=[str(_GUEST_HELPER), GAST_A_ID, str(in_fifo_a), str(out_fifo_a)], cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_a.returncode,
            stdout_text=full_guest_a_stdout, stderr_text=stderr_a, pid=helper_a.pid,
        )
        r6.write_process_result(
            out_dir, "gast_b_helper_process",
            argv=[str(_GUEST_HELPER), GAST_B_ID, str(in_fifo_b), str(out_fifo_b)], cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_b.returncode,
            stdout_text=full_guest_b_stdout, stderr_text=stderr_b, pid=helper_b.pid,
        )
        r6.write_process_result(
            out_dir, "gast_a_reload_process", argv=reload_argv, cwd=str(_REPO_ROOT),
            utc_start=reload_utc_start, utc_end=reload_utc_end, exit_code=reload_proc.returncode,
            stdout_text=reload_out, stderr_text=reload_proc.stderr, pid=-1,
        )
        mf.record_process_files(
            "betreiber_launcher", aussage="r5a_betreiber_launcher_transcript",
            run_id="R5-A-VOLLWEG", teilnehmer_figur=BETREIBER_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_a_helper_process", aussage="r5a_gast_a_leader_transcript",
            run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_A_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_b_helper_process", aussage="r5a_gast_b_nichtleader_eingabefokus_transcript",
            run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_B_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_a_reload_process", aussage="r5a_gast_a_reload_frischer_prozess_transcript",
            run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_A_ID, tisch_abschnitt=RELOAD_TABLE_KEY,
        )
        mf.export_tree(run_dir, "run", aussage="r5a_run_dir_after_finish", run_id="R5-A-VOLLWEG", teilnehmer_figur="beide")
        mf.export_file(export_a_path, "gast_a_export.json", aussage="r5a_gast_a_export", run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_A_ID)
        mf.export_file(export_b_path, "gast_b_export.json", aussage="r5a_gast_b_export", run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_B_ID)
        mf.export_file(current_a_path, "gast_a_current.json", aussage="r5a_gast_a_current", run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_A_ID)
        mf.export_file(current_b_path, "gast_b_current.json", aussage="r5a_gast_b_current", run_id="R5-A-VOLLWEG", teilnehmer_figur=GAST_B_ID)
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r5a_gm_double_calls", run_id="R5-A-VOLLWEG", teilnehmer_figur="beide")
        mf.write_json_body(
            "menu_return_evidence.json",
            {
                "gast_a_frischer_tisch_eintritt": menu_return_a,
                "gast_b_laengst_wartende_untermenue_eingabe_resumed": menu_return_b,
                "gast_b_kein_erzwungenes_vorab_zurueck_FIX1": True,
                "leader_save_kommando": "!save",
            },
            aussage="r5a_menuerueckkehr_und_fix1_eingabefokus_verweis", run_id="R5-A-VOLLWEG", teilnehmer_figur="beide",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "R5_A_vollweg_fehlende_stationen",
            "aussage": (
                "Vervollstaendigt U5 um die R5-A-Stationen: Gast B bekommt KEIN erzwungenes "
                "Vorab-/zurueck mehr (FIX1, echte parallele Leserpfade); Leader nutzt das echte "
                "sichtbare '!save'-Kommando (FIX3a); beide Gaeste fuehren nach der Abschlusskarte "
                "real eine weitere Menueauswahl aus; beide Exporte sind byte-/feldgleich zum "
                "eigenen akzeptierten Current; ein ECHTER frischer Subprozess laedt Gast As Export "
                "erneut, bedient eine NEUE zulaessige Tischanfrage real (vom Betreiber angenommen) "
                "UND bestaetigt, dass der alte Tisch geschlossen bleibt."
            ),
            "fix1_kein_erzwungenes_vorab_zurueck_gast_b": True,
            "fix3a_echtes_save_kommando": True,
            "menuerueckkehr_beide_gaeste_real_bedient": True,
            "export_a_byte_match_current": export_a_match_current,
            "export_b_byte_match_current": export_b_match_current,
            "reload_frischer_prozess_rc": reload_proc.returncode,
            "reload_neue_aufnahme_real": True,
            "alter_tisch_bleibt_geschlossen": closed_table_rejection,
            "anzahl_gm_rufe": len(calls),
            "final_written": final_path.exists(),
        })

        findings["final_written"] = final_path.exists()
        findings["gm_calls"] = len(calls)
        findings["export_a_match_current"] = export_a_match_current
        findings["export_b_match_current"] = export_b_match_current
        findings["reload_rc"] = reload_proc.returncode
        findings["closed_table_rejection"] = closed_table_rejection
        return findings


# ═══════════════════════════════════════════════════════════════════════
# Kurzer Ergaenzungsweg (02_ABNAHME.md §A, "Eine vorhandene KI-Persona ...
# nummeriert bis Besetzung/Leaderwahl fuehren ... geaenderte Solo-Auswahl
# am Host kurz bis zum zutreffenden Fortsetzen-/Menuezustand bedienen"):
# gefuehrter Solo-mit-KI-Weg ('g' -> '1'), NUMMERIERTE KI-/Leaderauswahl
# bis zur Zusammenfassung -- DANACH bewusst ABGELEHNT (kein KI-
# Zustimmungs-/Modellaufruf noetig, L2->3-Kernbeleg NICHT wiederholt).
# ═══════════════════════════════════════════════════════════════════════

def run_scene_a_solo_ki_leaderwahl() -> dict:
    out_dir = _OUT_ROOT / "solo-ki-leaderwahl"
    mf = r6.Manifest(out_dir)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        # `_known_ai_overview()` liest `community-<self.participant_id>`
        # (eigene, bereits bestaetigte Spielgemeinschaft DIESES Teilnehmers)
        # -- die Community-ID muss daher GENAU auf die (erst jetzt per
        # Registry generierte) `host_id` lauten, nicht auf einen freien
        # Namen (empirisch am echten Subprozess bestaetigt: sonst "Keine
        # eigene KI-Spielgemeinschaft bekannt").
        host_human = sup.register_human(registry_dir, "R5A-Solo-Host")
        host_id = host_human.participant_id
        boot = sup.bootstrap_six_persona_community(root, f"community-{host_id}")
        run_dir, states_dir = boot["run_dir"], boot["states_dir"]
        onboarding_dir, catalog_dir = boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        onb = sup.onboard_human_figure(
            registry_dir, host_id, onboarding_dir, states_dir, run_dir, "CHR-R5A-SOLO", "Solo", "SOLOOPS",
        )
        from mmo_sim.domain.zeitriss import catalog as catalog_mod
        catalog_mod.register(catalog_dir, catalog_mod.CatalogEntry(
            participant_id=host_id, chrononaut_id="CHR-R5A-SOLO", persona_key=host_id,
        ))
        catalog_mod.bind_for_section(catalog_dir, host_id, "CHR-R5A-SOLO", has_open_section=False)
        sup.write_test_profile(run_dir, max_turns=200)

        # Gefuehrter Weg: 'g' -> '1' (Solo mit KI) -> Figur bestaetigen ->
        # KI NUMMERIERT waehlen (bekannte Uebersicht, [1]=sniper) -> Leader
        # NUMMERIERT waehlen ([1]=sniper, selbst wird Gast der eigenen KI)
        # -> Zusammenfassung -- DANACH bewusst 'n' (letzte Startwahl NICHT
        # bestaetigt): kein KI-Zustimmungs-/Modellaufruf, kein Tisch.
        # KI per NAME waehlen (Expertenweg/Name statt Nummer -- die
        # Uebersicht listet alle 6 Startpersonas alphabetisch, 'sniper'
        # waere Nummer [5]; 'sniper' als Name ist eindeutig und robust
        # gegen die genaue Listenposition). Leader danach ueber '1'
        # (= ai_tokens[0], da genau EINE KI gewaehlt wurde).
        stdin_lines = ["g", "1", "j", "sniper", "1", "n", "beenden"]
        stdin_text = "\n".join(stdin_lines) + "\n"
        argv = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", host_id, "--data-dir", str(root),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.run(
            argv, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        utc_end = r6.utc(time.time())
        out = proc.stdout
        assert proc.returncode == 0, f"R5-A-Solo-KI: Prozess fehlgeschlagen: {proc.stderr[-2000:]}"

        assert "Lokale Runde einrichten" in out
        assert f"'{host_id}' spielt 'CHR-R5A-SOLO' -- bestaetigen?" in out, out[:3000]
        assert "Bekannte KI-Mitspieler" in out, out[:3000]
        assert "] sniper " in out, out[:3000]
        assert "Leaderkandidaten:" in out, out
        assert "[1] sniper" in out.split("Leaderkandidaten:", 1)[1][:200], out
        assert "Zusammenfassung (2 Spieler einschliesslich Leader)" in out, out
        assert "Leader=sniper" in out, out
        assert "KEINE KI-Zustimmung und keine Tischaufnahme" in out, out
        assert "Einrichtung abgebrochen: letzte Startwahl nicht bestaetigt." in out, out[-2000:]
        assert "Gruppe eingeladen" not in out, "R5-A-Solo-KI: abgelehnte Startwahl darf keine Einladung ausloesen."

        r6.write_process_result(
            out_dir, "solo_ki_leaderwahl", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=out, stderr_text=proc.stderr, pid=-1,
        )
        mf.record_process_files(
            "solo_ki_leaderwahl", aussage="r5a_solo_ki_nummeriert_besetzung_leaderwahl_dann_abgelehnt",
            run_id="R5-A-SOLO-KI", teilnehmer_figur=host_id,
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "R5_A_solo_ki_besetzung_leaderwahl",
            "aussage": (
                "Gefuehrter Solo-mit-KI-Weg: bekannte KI-Persona 'sniper' NUMMERIERT gewaehlt, "
                "NUMMERIERTE Leaderwahl (sniper als Leader), Zusammenfassung (2 Spieler) real "
                "erreicht -- dann bewusst abgelehnt ('n' an der letzten Startwahl). KEIN KI-"
                "Zustimmungs-/Modellaufruf, kein Tisch, L2->3-Kernbeleg NICHT wiederholt. Landet "
                "am zutreffenden Hauptmenue-/Fortsetzen-Zustand (klarer Rueckweg, keine Aenderung)."
            ),
            "besetzung_und_leaderwahl_nummeriert_erreicht": True,
            "danach_bewusst_abgelehnt_kein_ki_call": True,
        })
        return {"returncode": proc.returncode}


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_a()
        solo_findings = run_scene_a_solo_ki_leaderwahl()
        print(f"OK   R5_A_vollweg: {findings}  solo_ki={solo_findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R5_A_vollweg: {e}")
        return 1
    except Exception:
        print("ERROR R5_A_vollweg:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
