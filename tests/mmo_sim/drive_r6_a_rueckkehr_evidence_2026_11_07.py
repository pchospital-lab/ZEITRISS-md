#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_a_rueckkehr_evidence_2026_11_07.py -- ZR-VOLLENDUNG-
OHNE-LAN-NACHZUG-20261107-R6, 02_ABNAHME.md §A "Rueckkehr"-Zeile (=
GENERAL-REVIEW.md §3 G-R6-02, 01_NACHZUG.md Arbeitsblock1 Punkt1b) PLUS die
ebenfalls in §A letzter Absatz verlangte Solo-/Persona-Ergaenzung ("keine
weiteren"/"ohne KI" bewusst abwaehlen).

ECHTER Real-Subprozess-Treiber (kein isolierter Methodentest) auf dem
R6-korrigierten Code (uncommitteter Linus-Diff auf HEAD 213d3f4f). Baut auf
EXAKT demselben realen Zwei-Gast-Normalweg wie `drive_r5_a_vollweg_evidence_
2026_11_07.py` auf (dessen FIX1-Eingabefokus -- GastB bleibt OHNE
erzwungenes Vorab-'/zurueck' im Tisch-Untermenue geparkt -- wird
UNVERAENDERT wiederverwendet, NICHT neu aufgerollt), schliesst aber GENAU
die vorher offene Luecke:

  G-R6-02 (vorher): nach der Abschlusskarte fuer den GEPARKTEN GastB druckte
  der Code PAUSCHAL `render_boot_menu` ("1 Fortsetzen"); GastBs naechste
  getippte '1' traf aber den weiterhin aktiven, geparkten Tisch-Untermenue-
  Lesezyklus (`_cmd_menu_tisch`) -- 'Hauptmenue 1' bedeutete dort VERSTECKT
  'Tische suchen'. Sichtbare Ebene != wirklicher Dispatcher.

  R6-FIX (jetzt): `_print_section_completion_card` druckt fuer einen
  weiterhin geparkten Gast (`io._tisch_submenu_depth > 0`) GENAU dieselbe
  Tisch-Untermenue-Kopfzeile (`_print_tisch_submenu_header`), NICHT mehr
  `render_boot_menu`. Dieser Treiber belegt das ECHT am Subprozess:

  1. GastB bleibt (wie bisher, FIX1) beim Rundenbeitritt OHNE erzwungenes
     Vorab-'/zurueck' im Tisch-Untermenue geparkt.
  2. Direkt NACH GastBs Abschlusskarte erscheint GENAU die Tisch-Untermenue-
     Kopfzeile ("Tisch -- [1] Offene Tische suchen ..."), NICHT "1
     Fortsetzen"/render_boot_menu.
  3. GastBs naechste getippte '1' liefert ihr ECHTES Tisch-Untermenue-
     Ergebnis ("Keine offenen Tische gefunden"/"Offene Tische (..."), nicht
     ein falsch interpretiertes Hauptmenue-Ergebnis.
  4. GastA (NICHT geparkt, verliess sein Untermenue vorher real per
     '/zurueck') bekommt nach SEINER Karte das normale volle Hauptmenue und
     bedient dort eine ECHTE sichtbare NUMMER (nicht das Wort 'tisch') --
     die reale Nummer wird aus dem tatsaechlich gedruckten Menuetext
     extrahiert, nicht geraten/hartkodiert.

Zweite, kurze Szene (`run_scene_a_solo_persona_deselect`, 02_ABNAHME.md §A
letzter Absatz): gefuehrter Solo-mit-KI-Weg bis zur NUMMERIERTEN Besetzung/
Leaderwahl -- DANACH ein echtes '/zurueck' aus STEP_LEADER zurueck auf
STEP_AI (vorherige Auswahl ['sniper'] wird sichtbar wieder angezeigt), dort
wird die vorhandene Auswahl bewusst per 'ohne ki' auf KEINE KI zurueckgesetzt
(01_NACHZUG.md Arbeitsblock2 Punkt2c) -- die Wirkung wird am tatsaechlichen
Folgezustand (leere KI-Liste in der Zusammenfassung, Leader faellt automatisch
auf den Menschen selbst zurueck) geprueft, nicht nur am Hinweistext. Danach
bewusst abgelehnt (kein KI-Zustimmungs-/Modellaufruf noetig).

GM NUR als Grenzinjektion (`_r4_gm_double.py`), NIE Live-Modell. Pure Python,
nur `assert`, echter Exitcode, kein pytest.

§D Evidenz-Disziplin: vollstaendige originale stdout/stderr je Prozess
(`<label>.stdout.txt`/`.stderr.txt`), reale Prozessdaten (`<label>.procmeta.
json`: argv/cwd/pid/utc_start/utc_end/exit), tatsaechliche Sendeereignisse
gekoppelt an den zuvor beobachteten Prompt (`<kanal>.sends.jsonl`). Ein
zusammengefuegtes Protokoll (`MERGED_PROTOKOLL.md`) ist zusaetzlich und
ausdruecklich als ABGELEITET gekennzeichnet, mit dem wirklichen Codeanker
(`git rev-parse HEAD` + `git diff --stat mmo_sim/ui/tui.py`, NUR gelesen,
kein git-Schreibkommando) als erste Zeile."""
from __future__ import annotations

import json
import re
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

_OUT_ROOT = Path(os.environ.get("ZR_R6_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r6_evidence" / "A")))
_GUEST_HELPER = _REPO_ROOT / "scripts" / "zeitriss-gast-terminal.sh"
_LAUNCHER = r4._LAUNCHER

BETREIBER_ID = "betreiber_r6a"
GAST_A_ID = "gast_a_r6a"
GAST_B_ID = "gast_b_r6a"
CHAR_A = "chrono-r6a-gast-a"
CHAR_B = "chrono-r6a-gast-b"
TABLE_KEY = "mesaR6A"
TABLE_ID = f"local-{GAST_A_ID}-{GAST_B_ID}"


def _git_codeanchor() -> str:
    """Nur LESENDE git-Aufrufe (kein git-Schreibkommando) -- der wirkliche
    Codeanker fuer jede merged/abgeleitete Evidenzdatei (02_ABNAHME.md §D)."""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    diffstat = subprocess.run(
        ["git", "diff", "--stat", "mmo_sim/ui/tui.py"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    return f"CODEANKER: HEAD={head} + uncommitteter Linus-Diff -- git diff --stat mmo_sim/ui/tui.py: {diffstat!r}"


class _SendLog:
    """Reale Sendeereignisse, gekoppelt an den zuletzt BEOBACHTETEN Prompt/
    Output je Kanal (02_ABNAHME.md §D) -- Zeitstempel sind die wirklichen
    `time.time()`-Zeiten dieses Treiberprozesses beim Beobachten/Senden,
    KEIN erfundener interner Zeitstempel des Subprozesses."""

    def __init__(self) -> None:
        self.events: list[dict] = []
        self._last_seen: dict[str, str] = {}

    def observed(self, channel: str, text: str) -> None:
        if text:
            self._last_seen[channel] = text

    def record(self, channel: str, line: str) -> None:
        self.events.append({
            "channel": channel,
            "ts_sent_utc": r6.utc(time.time()),
            "sent": line,
            "observed_prompt_before_send_tail": self._last_seen.get(channel, "")[-600:],
        })

    def write(self, out_dir: Path, rel: str = "sends.jsonl") -> Path:
        path = out_dir / rel
        path.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in self.events) + ("\n" if self.events else ""),
            encoding="utf-8",
        )
        return path


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


def _settle_after_marker(reader: "r4._LineReader", settle: float = 0.3, overall: float = 5.0) -> None:
    """Rework (Specht, 2026-11-07): generische Haertung fuer JEDEN
    kontestierten Send in diesem Treiber, nicht nur die Abschlusskarte.
    Empirisch (25x-Beweislauf) zeigte sich, dass das Timing-Race (Send
    direkt nach einem per `_wait_for_marker` gematchten Body-/Listen-Zeile,
    BEVOR der tatsaechliche naechste readline-Prompt -- OHNE Newline --
    wirklich angekommen ist) NICHT nur an der Abschlusskarte auftritt,
    sondern an mehreren Stellen (z.B. '!save' traf intermittierend
    "Unbekannte Auswahl" statt der Rundenprompt-readline). Statt an jeder
    einzelnen Stelle den exakten Prompt-Wortlaut zu kennen, wartet diese
    Funktion NACH einem Marker-Match generisch auf eine kurze Ruhephase
    (kein neues Byte mehr fuer `settle` Sekunden) -- dasselbe Prinzip wie
    `_drain`, nur OHNE die bereits gematchten Zeilen zu konsumieren. Rein
    peekender/pumpender Zusatzschritt auf demselben Reader -- keine
    Reader-Desync, kein Zeilenverlust. `overall` ist eine Obergrenze fuer
    den Normalfall (Ruhephase kommt ueblich binnen <1s); fuer bekannte
    Ausreisser (Abschlusskarten-Claim) bleibt die dedizierte, laenger
    bemessene `_wait_for_buffered_substr`-Pruefung an der jeweiligen Stelle
    zusaetzlich bestehen."""
    deadline = time.time() + overall
    last_data_at = time.time()
    while time.time() < deadline:
        ready, _, _ = select.select([reader], [], [], 0.1)
        if ready:
            if not reader.pump():
                return
            last_data_at = time.time()
        elif time.time() - last_data_at > settle:
            return


def _extract_index(list_line: str, needle: str) -> str:
    for num, val in re.findall(r"\[(\d+)\]\s*'?([^'\s]+)'?", list_line):
        if val == needle:
            return num
    raise AssertionError(f"{needle!r} nicht in Liste gefunden: {list_line!r}")


def _extract_boot_menu_number(boot_menu_text: str, choice_key: str) -> str:
    """Liest die reale sichtbare Nummer fuer `choice_key` DIREKT aus dem
    tatsaechlich gedruckten Hauptmenuetext (`boot_menu_entries`-Format
    '  N) <label>  [<key>]') -- kein Raten/Hartkodieren der Position."""
    m = re.search(rf"(\d+)\)[^\n\[]*\[{re.escape(choice_key)}\]", boot_menu_text)
    if not m:
        raise AssertionError(f"Choice-Key {choice_key!r} nicht im Hauptmenuetext gefunden: {boot_menu_text!r}")
    return m.group(1)


def run_scene_a_rueckkehr() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    sendlog = _SendLog()
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

        import_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-r6a-gast-a-001")
        fixture_a_path = root / "gast_a_import.json"
        fixture_a_path.write_text(json.dumps(import_block_a, ensure_ascii=False), encoding="utf-8")

        creation_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-r6a-gast-b-001")
        creation_response = "```json\n" + json.dumps(creation_block_b, ensure_ascii=False) + "\n```"
        debrief_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-r6a-gast-a-002", level=2)
        debrief_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-r6a-gast-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet (R6-A), beide Standsicherungen anbei.\n"
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
        sendlog.observed("gast_a", "".join(header_a))
        sendlog.observed("gast_b", "".join(header_b))
        sendlog.observed("host", "".join(host_boot))

        def send_a(line: str) -> None:
            sendlog.record("gast_a", line)
            r4._send_guest(helper_a.stdin, line)

        def send_b(line: str) -> None:
            sendlog.record("gast_b", line)
            r4._send_guest(helper_b.stdin, line)

        def send_host(line: str) -> None:
            sendlog.record("host", line)
            r4._send_op(proc, line)

        def wait_a(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(reader_a, marker, overall=overall)
            # Rework: generisch auf die Ruhephase NACH dem Marker-Match
            # warten -- laesst den tatsaechlichen (newline-losen) naechsten
            # readline-Prompt sicher im Puffer ankommen, BEVOR der Aufrufer
            # direkt danach sendet (s. _settle_after_marker-Docstring).
            _settle_after_marker(reader_a)
            transcript_a.extend(lines)
            joined = "".join(lines)
            sendlog.observed("gast_a", joined)
            return joined

        def wait_b(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(reader_b, marker, overall=overall)
            _settle_after_marker(reader_b)
            transcript_b.extend(lines)
            joined = "".join(lines)
            sendlog.observed("gast_b", joined)
            return joined

        def wait_host(marker: str, overall: float = 20.0) -> str:
            lines = r4._wait_for_marker(host_reader, marker, overall=overall)
            _settle_after_marker(host_reader)
            transcript_host.extend(lines)
            joined = "".join(lines)
            sendlog.observed("host", joined)
            return joined

        def wait_host_prompt(marker: str, overall: float = 20.0) -> str:
            return _wait_for_buffered_substr(host_reader, marker, overall=overall)

        def wait_a_prompt(marker: str, overall: float = 20.0) -> str:
            # Rework (Specht, 2026-11-07): puffer-basiert auf den tatsaechlichen
            # readline-Prompt warten (OHNE Newline, von _wait_for_marker/pop_line
            # nicht als eigene Zeile gefangen) -- derselbe reader_a, nur ein
            # lesender Peek auf dessen Puffer, kein Zeilenverbrauch, keine
            # Reader-Desync gegenueber wait_a/drain_a auf demselben Kanal.
            buf = _wait_for_buffered_substr(reader_a, marker, overall=overall)
            sendlog.observed("gast_a", buf)
            return buf

        def wait_b_prompt(marker: str, overall: float = 20.0) -> str:
            buf = _wait_for_buffered_substr(reader_b, marker, overall=overall)
            sendlog.observed("gast_b", buf)
            return buf

        def drain_a(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_a, settle=settle, overall=overall)
            transcript_a.extend(lines)
            joined = "".join(lines)
            sendlog.observed("gast_a", joined)
            return joined

        def drain_b(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_b, settle=settle, overall=overall)
            transcript_b.extend(lines)
            joined = "".join(lines)
            sendlog.observed("gast_b", joined)
            return joined

        def drain_host(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(host_reader, settle=settle, overall=overall)
            transcript_host.extend(lines)
            joined = "".join(lines)
            sendlog.observed("host", joined)
            return joined

        # ═══════════════════ Gast A: ECHTER Import ([charaktere]->[2]) ═════
        send_a("charaktere")
        wait_a("[2] Importieren")
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
                "SL-Antwort auf den Leader-Anker (R6-A).",
                "SL-Antwort auf den Gast-B-Erstbeitrag (R6-A).",
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
        # GastA verlaesst sein Untermenue real -- NICHT geparkt (Gegensatz
        # zu GastB unten). Das IST die Voraussetzung dafuer, dass GastA nach
        # seiner Karte das NORMALE volle Hauptmenue sieht (s.u.).
        send_a("/zurueck")
        drain_a(settle=0.5, overall=5.0)

        send_b("tisch")
        wait_b("[2] Tisch anfragen")
        send_b("2")
        wait_b("Welcher Tisch")
        send_b(TABLE_KEY)
        wait_b(f"Anfrage an Tisch '{TABLE_KEY}' gestellt")
        # R6-A/FIX1 (02_ABNAHME.md §A "Rueckkehr"/"Eingabefokus"): KEIN
        # erzwungenes Vorab-'/zurueck' fuer GastB -- er bleibt im Tisch-
        # Untermenue geparkt (eigener Gast-Menue-Loop-Thread im Betreiber-
        # prozess), WAEHREND der host-getriebene Rundenclaim (Consent/Zuege/
        # Abschlusskarte) auf GENAU demselben FIFO-Kanal laeuft.
        assert reader_b._buf == "" or True  # reine Doku-Markierung, kein Read hier.

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

        # ═══ Nicht-Leader-Konsens (GastB tritt der Runde ausdruecklich bei
        # -- diese Zeile erreicht GENAU den Rundenconsent-Read, NICHT den
        # geparkten Untermenue-Read, der FIX1-Claim entscheidet). ═══
        consent_b = wait_b("beitreten? [j/n]")
        assert "Dieser lokalen Runde" in consent_b, consent_b
        assert f"Leader: {GAST_A_ID}" in consent_b, consent_b
        send_b("j")

        leader_anchor = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Empfaenger: Spielleitung (SL)" in leader_anchor, leader_anchor
        send_a("Ich sichte knapp die Lage am Tisch (R6-A).")

        guest_b_first = wait_b("Empfaenger: ueber Leader an Spielleitung")
        assert "Empfaenger: ueber Leader an Spielleitung" in guest_b_first, guest_b_first
        assert "Unbekannte Auswahl" not in guest_b_first, guest_b_first
        send_b("Ich pruefe meine Ausruestung und melde mich (R6-A).")

        leader_second = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Unbekannte Auswahl" not in leader_second, leader_second
        send_a("!save")

        notiz_a = wait_a("eigene lokale Notiz")
        send_a("Abschlussnotiz Leader (GastA, R6-A): Reise erfolgreich.")
        notiz_b = wait_b("eigene lokale Notiz")
        send_b("Abschlussnotiz GastB (R6-A): Erschaffung und erster Einsatz gelungen.")

        final_path = run_dir / "completion" / f"{TABLE_ID}-section__final.json"
        r4._wait_for_path(final_path, overall=25.0)

        # ═══════════════ Abschlusskarten: GastA (nicht geparkt) ═══════════
        card_a = wait_a("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_A_ID}'" in card_a, card_a
        # Rework: wait_a() matched nur die letzte Aktionszeile (Body, MIT
        # Newline) -- der tatsaechliche Auswahl-Readline-Prompt kommt danach
        # OHNE Newline und wuerde sonst gelegentlich erst NACH diesem Send
        # real aktiv werden (Race -> Send trifft intermittierend das
        # Hauptmenue statt die Karten-readline). Puffer-basiert abwarten.
        # overall=40.0: Claim-Erwerb (_terminal_read_lock) vor diesem Read
        # kann unter Systemlast laenger als die sonst ueblichen 20s dauern
        # (konsistent mit dem bereits im selben Treiber genutzten 60.0 fuer
        # "Tisch gestartet") -- weiterhin aktiv pollend, kein blindes sleep.
        wait_a_prompt("Auswahl (Nummer, leer/zurueck = Hauptmenue):", overall=40.0)
        send_a("1")
        export_a = wait_a("Zusaetzlich als Datei gespeichert")

        # GastA ist NICHT geparkt (depth==0) -- nach der Karte MUSS jetzt
        # das NORMALE volle Hauptmenue erscheinen (bytegleiches Altverhalten
        # fuer den ungeparkten Fall, R6-Nachzug beruehrt NUR den geparkten
        # Zweig). Explizit einfangen + pruefen, DANN die reale sichtbare
        # Nummer fuer 'tisch' aus genau diesem Text extrahieren (kein
        # Raten/Hartkodieren der Position).
        boot_menu_a = drain_a(settle=0.6, overall=8.0)
        assert "Hauptmenue:" in boot_menu_a, (
            "R6-A: GastA (NICHT geparkt) haette nach der Karte das normale volle "
            f"Hauptmenue sehen muessen: {boot_menu_a!r}"
        )
        assert "Tisch -- [1] Offene Tische suchen" not in boot_menu_a, (
            "R6-A: GastA ist NICHT geparkt -- die Tisch-Untermenue-Kopfzeile darf hier "
            f"NICHT direkt erscheinen (das waere die falsche, GastB-spezifische Weiche): {boot_menu_a!r}"
        )
        tisch_num_a = _extract_boot_menu_number(boot_menu_a, "tisch")

        # GastA bedient jetzt eine ECHTE sichtbare NUMMER am Hauptmenue
        # (nicht das Wort 'tisch') -- 02_ABNAHME.md §A "Rueckkehr": "Pro
        # Gast mindestens eine danach sichtbare normale Zahl bedienen und an
        # ihrem Ergebnis pruefen."
        send_a(tisch_num_a)
        submenu_via_number_a = wait_a("Tisch -- [1] Offene Tische suchen")
        assert "Unbekannte Auswahl" not in submenu_via_number_a, submenu_via_number_a
        send_a("1")
        tischsuche_a = drain_a(settle=0.6, overall=10.0)
        assert ("Keine offenen Tische gefunden" in tischsuche_a) or ("Offene Tische (" in tischsuche_a), (
            f"R6-A: GastAs reale Nummer haette echt zur Tischsuche fuehren muessen: {tischsuche_a!r}"
        )
        send_a("/zurueck")
        drain_a(settle=0.4, overall=5.0)

        # ═══════════════ Abschlusskarte GastB (GEPARKT) -- G-R6-02-Kern ════
        card_b = wait_b("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_B_ID}'" in card_b, card_b
        # Rework: analog zu GastA oben -- echten Auswahl-Prompt abwarten,
        # nicht die Body-Zeile. overall=40.0 aus demselben Grund (s. GastA).
        wait_b_prompt("Auswahl (Nummer, leer/zurueck = Hauptmenue):", overall=40.0)
        send_b("1")
        export_b = wait_b("Zusaetzlich als Datei gespeichert")

        # G-R6-02-Kernbeleg: GENAU die Tisch-Untermenue-Kopfzeile erscheint
        # jetzt wieder (der geparkte Gast-Thread ist weiterhin der
        # tatsaechliche naechste Dispatcher) -- NICHT render_boot_menu/
        # "1 Fortsetzen". Explizit VOR dem naechsten Send einfangen.
        dispatcher_match_b = drain_b(settle=0.6, overall=8.0)
        assert "Tisch -- [1] Offene Tische suchen" in dispatcher_match_b, (
            "R6-A/G-R6-02: nach der Karte des GEPARKTEN GastB haette GENAU die Tisch-"
            f"Untermenue-Kopfzeile erneut gezeigt werden muessen: {dispatcher_match_b!r}"
        )
        assert "1 Fortsetzen" not in dispatcher_match_b, (
            "R6-A/G-R6-02: 'Hauptmenue 1 Fortsetzen' waere hier IRREFUEHREND -- der echte "
            f"naechste Konsument ist weiterhin das Tisch-Untermenue: {dispatcher_match_b!r}"
        )
        assert "Hauptmenue:" not in dispatcher_match_b, (
            f"R6-A/G-R6-02: kein pauschales Hauptmenue nach der Karte des geparkten GastB: {dispatcher_match_b!r}"
        )

        # GastBs naechste getippte '1' MUSS ihr ECHTES Tisch-Untermenue-
        # Ergebnis liefern (Tischsuche), NICHT ein falsch interpretiertes
        # Hauptmenue-Ergebnis ("Hauptmenue1 darf nicht versteckt Tischsuche
        # bedeuten" -- hier umgekehrt/zugesichert: die '1' IST jetzt
        # offiziell+sichtbar Tischsuche, kein verstecktes Hauptmenue-Label).
        menu_return_b = drain_b(settle=0.1, overall=0.1)  # sollte bereits leer sein (kein Vorablauf).
        send_b("1")
        tischsuche_b = drain_b(settle=0.6, overall=10.0)
        assert ("Keine offenen Tische gefunden" in tischsuche_b) or ("Offene Tische (" in tischsuche_b), (
            f"R6-A/G-R6-02: GastBs '1' haette die ECHTE Tischsuche ausloesen muessen: {tischsuche_b!r}"
        )
        assert "Unbekannte Auswahl" not in tischsuche_b, tischsuche_b
        send_b("/zurueck")
        drain_b(settle=0.4, overall=5.0)

        # ═══════════════ Figurfreie Betreiber-Tisch-Abschlusskarte ═════════
        operator_card = wait_host("Beenden (zurueck zum Hauptmenue)")
        assert f"Tisch-Abschlusskarte (Betreiber, figurfrei) fuer '{TABLE_ID}'" in operator_card, operator_card
        send_host("3")
        wait_host(f"Tisch '{TABLE_KEY}': Abschnitt")
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

        current_a_path = run_dir / "current_saves" / f"{GAST_A_ID}.json"
        current_b_path = run_dir / "current_saves" / f"{GAST_B_ID}.json"
        current_a_block = json.loads(current_a_path.read_text(encoding="utf-8"))
        current_b_block = json.loads(current_b_path.read_text(encoding="utf-8"))
        export_a_match_current = export_a_block == current_a_block
        export_b_match_current = export_b_block == current_b_block
        assert export_a_match_current, (export_a_block, current_a_block)
        assert export_b_match_current, (export_b_block, current_b_block)

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 4, f"R6-A: GENAU VIER reale GM-Rufe erwartet: {calls}"

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
        assert proc.returncode == 0, f"R6-A: Betreiberprozess gescheitert: {stderr_text}"
        assert final_path.exists()

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "betreiber_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text, pid=proc.pid,
        )
        _write_procmeta(
            out_dir, "betreiber_launcher", argv=argv, cwd=str(_REPO_ROOT), pid=proc.pid,
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
        )
        helper_a_argv = [str(_GUEST_HELPER), GAST_A_ID, str(in_fifo_a), str(out_fifo_a)]
        helper_b_argv = [str(_GUEST_HELPER), GAST_B_ID, str(in_fifo_b), str(out_fifo_b)]
        r6.write_process_result(
            out_dir, "gast_a_helper_process", argv=helper_a_argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_a.returncode,
            stdout_text=full_guest_a_stdout, stderr_text=stderr_a, pid=helper_a.pid,
        )
        _write_procmeta(
            out_dir, "gast_a_helper_process", argv=helper_a_argv, cwd=str(_REPO_ROOT), pid=helper_a.pid,
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_a.returncode,
        )
        r6.write_process_result(
            out_dir, "gast_b_helper_process", argv=helper_b_argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_b.returncode,
            stdout_text=full_guest_b_stdout, stderr_text=stderr_b, pid=helper_b.pid,
        )
        _write_procmeta(
            out_dir, "gast_b_helper_process", argv=helper_b_argv, cwd=str(_REPO_ROOT), pid=helper_b.pid,
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_b.returncode,
        )
        mf.record_process_files(
            "betreiber_launcher", aussage="r6a_betreiber_launcher_transcript",
            run_id="R6-A-RUECKKEHR", teilnehmer_figur=BETREIBER_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_a_helper_process", aussage="r6a_gast_a_nicht_geparkt_normales_hauptmenue_transcript",
            run_id="R6-A-RUECKKEHR", teilnehmer_figur=GAST_A_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_b_helper_process", aussage="r6a_gast_b_geparkt_dispatcher_match_g_r6_02_transcript",
            run_id="R6-A-RUECKKEHR", teilnehmer_figur=GAST_B_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.export_tree(run_dir, "run", aussage="r6a_run_dir_after_finish", run_id="R6-A-RUECKKEHR", teilnehmer_figur="beide")
        mf.export_file(export_a_path, "gast_a_export.json", aussage="r6a_gast_a_export", run_id="R6-A-RUECKKEHR", teilnehmer_figur=GAST_A_ID)
        mf.export_file(export_b_path, "gast_b_export.json", aussage="r6a_gast_b_export", run_id="R6-A-RUECKKEHR", teilnehmer_figur=GAST_B_ID)
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r6a_gm_double_calls", run_id="R6-A-RUECKKEHR", teilnehmer_figur="beide")
        sends_path = sendlog.write(out_dir)
        mf.entries.append({
            "aussage": "r6a_sendeereignisse_gekoppelt_an_beobachteten_prompt", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-A-RUECKKEHR",
            "path": str(sends_path.relative_to(out_dir)), "sha256": r6.sha256_of(sends_path),
            "bytes": sends_path.stat().st_size,
        })
        mf.write_json_body(
            "dispatcher_match_evidence.json",
            {
                "gast_a_nicht_geparkt_boot_menu_text": boot_menu_a,
                "gast_a_reale_hauptmenue_nummer_fuer_tisch": tisch_num_a,
                "gast_a_submenu_via_nummer": submenu_via_number_a,
                "gast_a_tischsuche_ergebnis": tischsuche_a,
                "gast_b_geparkt_dispatcher_match_text": dispatcher_match_b,
                "gast_b_naechste_1_tischsuche_ergebnis": tischsuche_b,
                "g_r6_02_sichtbare_ebene_gleich_wirklicher_dispatcher": True,
            },
            aussage="r6a_g_r6_02_rueckkehr_kernbeleg", run_id="R6-A-RUECKKEHR", teilnehmer_figur="beide",
        )
        merged_path = out_dir / "MERGED_PROTOKOLL.md"
        merged_path.write_text(
            _git_codeanchor() + "\n\n"
            "ABGELEITETES, zusammengefuegtes Protokoll (R6-A Rueckkehr/G-R6-02) -- "
            "KEINE Originaldatei, reine Lesehilfe. Die Originale sind "
            "betreiber_launcher.stdout.txt / gast_a_helper_process.stdout.txt / "
            "gast_b_helper_process.stdout.txt (unveraendert, vollstaendig ab Prozessstart).\n\n"
            "== Betreiberkanal ==\n" + full_host_stdout + "\n\n"
            "== GastA-Kanal (nicht geparkt) ==\n" + full_guest_a_stdout + "\n\n"
            "== GastB-Kanal (geparkt, G-R6-02) ==\n" + full_guest_b_stdout + "\n",
            encoding="utf-8",
        )
        mf.entries.append({
            "aussage": "r6a_abgeleitetes_merged_protokoll", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-A-RUECKKEHR",
            "path": str(merged_path.relative_to(out_dir)), "sha256": r6.sha256_of(merged_path),
            "bytes": merged_path.stat().st_size,
        })
        mf.write_manifest()
        mf.write_summary({
            "szene": "R6_A_rueckkehr_g_r6_02",
            "aussage": (
                "GastB bleibt (FIX1, unveraendert von R5) beim Rundenbeitritt OHNE erzwungenes "
                "Vorab-/zurueck im Tisch-Untermenue geparkt. Nach seiner Abschlusskarte erscheint "
                "jetzt GENAU die Tisch-Untermenue-Kopfzeile (nicht render_boot_menu/'1 Fortsetzen') "
                "-- sichtbare Ebene und wirklicher Dispatcher stimmen zusammen (G-R6-02 geschlossen). "
                "Seine naechste getippte '1' liefert das ECHTE Tischsuche-Ergebnis. GastA (NICHT "
                "geparkt) bekommt nach seiner Karte das normale volle Hauptmenue und bedient dort "
                "eine ECHTE, aus dem Menuetext extrahierte Nummer fuer 'tisch' -- ebenfalls real bis "
                "zur Tischsuche durchdispatcht."
            ),
            "gast_b_dispatcher_match": "Tisch -- [1] Offene Tische suchen" in dispatcher_match_b,
            "gast_b_keine_render_boot_menu_leak": "1 Fortsetzen" not in dispatcher_match_b,
            "gast_b_naechste_1_ist_echte_tischsuche": (
                "Keine offenen Tische gefunden" in tischsuche_b or "Offene Tische (" in tischsuche_b
            ),
            "gast_a_bekommt_normales_hauptmenue": "Hauptmenue:" in boot_menu_a,
            "gast_a_reale_nummer_fuer_tisch": tisch_num_a,
            "gast_a_nummer_fuehrt_zu_echter_tischsuche": (
                "Keine offenen Tische gefunden" in tischsuche_a or "Offene Tische (" in tischsuche_a
            ),
            "export_a_match_current": export_a_match_current,
            "export_b_match_current": export_b_match_current,
            "anzahl_gm_rufe": len(calls),
            "final_written": final_path.exists(),
        })

        findings["final_written"] = final_path.exists()
        findings["gm_calls"] = len(calls)
        findings["gast_b_dispatcher_match"] = "Tisch -- [1] Offene Tische suchen" in dispatcher_match_b
        findings["gast_a_reale_nummer"] = tisch_num_a
        return findings


# ═══════════════════════════════════════════════════════════════════════
# Zweite, kurze Szene (02_ABNAHME.md §A letzter Absatz, 01_NACHZUG.md
# Arbeitsblock2 Punkt2c): gefuehrter Solo-mit-KI-Weg bis zur NUMMERIERTEN
# Besetzung/Leaderwahl -- danach echtes '/zurueck' aus STEP_LEADER zurueck
# auf STEP_AI, dort die vorhandene (nichtleere) Auswahl bewusst per
# 'ohne ki' auf KEINE KI zuruecksetzen; die WIRKUNG (nicht nur der
# Hinweistext) wird am tatsaechlichen Folgezustand (Zusammenfassung zeigt
# KI=[] UND Leader faellt automatisch auf den Menschen selbst zurueck)
# geprueft. Kein KI-Zustimmungs-/Modellaufruf noetig (danach bewusst
# abgelehnt).
# ═══════════════════════════════════════════════════════════════════════

def run_scene_a_solo_persona_deselect() -> dict:
    out_dir = _OUT_ROOT / "solo-persona-deselect"
    mf = r6.Manifest(out_dir)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        host_human = sup.register_human(registry_dir, "R6A-Solo-Host")
        host_id = host_human.participant_id
        boot = sup.bootstrap_six_persona_community(root, f"community-{host_id}")
        run_dir, states_dir = boot["run_dir"], boot["states_dir"]
        onboarding_dir, catalog_dir = boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        onb = sup.onboard_human_figure(
            registry_dir, host_id, onboarding_dir, states_dir, run_dir, "CHR-R6A-SOLO", "Solo", "SOLOOPS",
        )
        from mmo_sim.domain.zeitriss import catalog as catalog_mod
        catalog_mod.register(catalog_dir, catalog_mod.CatalogEntry(
            participant_id=host_id, chrononaut_id="CHR-R6A-SOLO", persona_key=host_id,
        ))
        catalog_mod.bind_for_section(catalog_dir, host_id, "CHR-R6A-SOLO", has_open_section=False)
        sup.write_test_profile(run_dir, max_turns=200)

        # 'g'->'1' (Solo mit KI) -> Figur bestaetigen ('j') -> STEP_AI:
        # 'sniper' NUMMERIERT/namensgefuehrt waehlen -> STEP_LEADER: ECHTES
        # '/zurueck' (KEIN Leader gewaehlt) -> zurueck auf STEP_AI mit
        # current=['sniper'] (sichtbar wieder angezeigt) -> 'ohne ki'
        # (bewusste Abwahl, R6-Nachzug) -> STEP_LEADER erneut MIT ai_tokens=
        # [] (keine Leaderkandidaten-Liste mehr, Leader faellt automatisch
        # auf den Menschen zurueck, leere Eingabe) -> STEP_SUMMARY: 'n'
        # (letzte Startwahl bewusst abgelehnt, kein KI-Call).
        stdin_lines = ["g", "1", "j", "sniper", "/zurueck", "ohne ki", "", "n", "beenden"]
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
        assert proc.returncode == 0, f"R6-A-Solo-Deselect: Prozess fehlgeschlagen: {proc.stderr[-2000:]}"

        assert "Lokale Runde einrichten" in out
        assert f"'{host_id}' spielt 'CHR-R6A-SOLO' -- bestaetigen?" in out, out[:3000]
        assert "] sniper " in out, out[:3000]

        # Nach dem '/zurueck' aus STEP_LEADER: die vorherige Auswahl
        # ['sniper'] wird SICHTBAR wieder angezeigt, PLUS der neue 'ohne
        # KI'-Hinweis (nur bei nichtleerer Vorauswahl ueberhaupt sichtbar --
        # R6-Nachzug-Kernbeleg, vorher gab es dieses Wort an dieser Stelle
        # nicht).
        assert "Aktuelle Auswahl (bleibt erhalten, bis bewusst geaendert): sniper" in out, out[:6000]
        assert "'ohne KI' = bewusst alle KI-Mitspieler abwaehlen" in out, (
            "R6-A/01_NACHZUG Arbeitsblock2 Punkt2c: der Abwahl-Hinweis haette bei "
            f"nichtleerer Vorauswahl sichtbar sein muessen: {out[:6000]}"
        )

        # WIRKUNG pruefen (nicht nur der Hinweistext): nach 'ohne ki' zeigt
        # STEP_LEADER KEINE Leaderkandidaten-Liste mehr (ai_tokens==[]) und
        # die STEP_SUMMARY-Rohzeile traegt tatsaechlich 'KI=[]' sowie
        # 'Leader=<host_id>' (automatischer Rueckfall auf den Menschen
        # selbst, da keine KI mehr zur Auswahl steht).
        after_deselect = out.split("'ohne KI' = bewusst alle KI-Mitspieler abwaehlen", 1)[1]
        assert "Leaderkandidaten:" not in after_deselect.split("Zusammenfassung", 1)[0], (
            "R6-A: nach der bewussten Abwahl darf KEINE KI-Leaderkandidatenliste mehr "
            f"erscheinen (ai_tokens muss wirklich leer sein): {after_deselect[:2000]}"
        )
        assert f"Menschen=['{host_id}'] KI=[] Leader={host_id}" in out, (
            "R6-A: die bewusste 'ohne KI'-Abwahl haette WIRKLICH zu KI=[] UND zum "
            f"automatischen Ruckfall auf den Menschen als Leader fuehren muessen: {out[-3000:]}"
        )
        assert "KEINE KI-Zustimmung und keine Tischaufnahme" in out, out
        assert "Einrichtung abgebrochen: letzte Startwahl nicht bestaetigt." in out, out[-2000:]
        assert "Gruppe eingeladen" not in out, "R6-A-Solo-Deselect: abgelehnte Startwahl darf keine Einladung ausloesen."

        r6.write_process_result(
            out_dir, "solo_persona_deselect", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=out, stderr_text=proc.stderr, pid=-1,
        )
        _write_procmeta(
            out_dir, "solo_persona_deselect", argv=argv, cwd=str(_REPO_ROOT), pid=-1,
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
        )
        mf.record_process_files(
            "solo_persona_deselect", aussage="r6a_solo_ki_besetzung_leaderwahl_dann_bewusste_ohne_ki_abwahl",
            run_id="R6-A-SOLO-PERSONA-DESELECT", teilnehmer_figur=host_id,
        )
        sends_path = (out_dir / "sends.jsonl")
        sends_path.write_text(
            json.dumps({
                "channel": "solo", "ts_sent_utc": utc_start, "sent_sequence": stdin_lines,
                "note": "Subprocess.run mit vollem stdin -- Sendereihenfolge ist die reale Eingabezeile; "
                        "jeder Schritt setzt auf dem direkt davor im echten stdout beobachteten Prompt auf "
                        "(Schrittautomat STEP_MODE->...->STEP_SUMMARY, s. stdout).",
            }, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        mf.entries.append({
            "aussage": "r6a_solo_sendereihenfolge", "teilnehmer_figur": host_id,
            "tisch_abschnitt": None, "run_id": "R6-A-SOLO-PERSONA-DESELECT",
            "path": str(sends_path.relative_to(out_dir)), "sha256": r6.sha256_of(sends_path),
            "bytes": sends_path.stat().st_size,
        })
        mf.write_manifest()
        mf.write_summary({
            "szene": "R6_A_solo_persona_deselect",
            "aussage": (
                "Gefuehrter Solo-mit-KI-Weg: 'sniper' NUMMERIERT/namensgefuehrt gewaehlt, dann "
                "echtes '/zurueck' aus STEP_LEADER zurueck auf STEP_AI -- vorherige Auswahl sichtbar "
                "wieder angezeigt, dann bewusst per 'ohne ki' auf KEINE KI zurueckgesetzt. WIRKUNG "
                "(nicht nur Hinweistext) bestaetigt: Zusammenfassung zeigt KI=[] und Leader faellt "
                "automatisch auf den Menschen selbst zurueck. Danach bewusst abgelehnt ('n') -- kein "
                "KI-Zustimmungs-/Modellaufruf, kein Tisch."
            ),
            "ohne_ki_abwahl_hinweis_sichtbar": True,
            "ohne_ki_abwahl_wirkung_bestaetigt": True,
            "danach_bewusst_abgelehnt_kein_ki_call": True,
        })
        return {"returncode": proc.returncode}


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_a_rueckkehr()
        solo_findings = run_scene_a_solo_persona_deselect()
        print(f"OK   R6_A_rueckkehr: {findings}  solo_persona_deselect={solo_findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R6_A_rueckkehr: {e}")
        return 1
    except Exception:
        print("ERROR R6_A_rueckkehr:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
