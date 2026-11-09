#!/usr/bin/env python3
"""
tests/mmo_sim/drive_u5_zweigast_figurfrei_2026_11_07.py -- ZR-VOLLENDUNG-
OHNE-LAN-NACHZUG-20261107-R4, Punkt U5 (und der U2-"Fertig, wenn"-Normalweg,
den U5 belegt): EIN figurfreier Betreiber fuehrt ZWEI tatsaechlich
gestartete persoenliche Gasthelfer-PROZESSE (`scripts/zeitriss-gast-
terminal.sh`, je ein echtes Betriebssystem-Programm) durch dieselbe normale
Menuefuehrung zusammen:

- Betreiber (`BETREIBER_ID`): KEINE eigene Figur geseedet, bleibt figurfrei,
  wird NICHT Leader (anders als der alte `drive_u5_normalweg_helper_
  2026_11_06.py`, dessen Betreiber eine eigene Figur mitbrachte und deshalb
  SELBST Leader wurde).
- Gast A (`GAST_A_ID`): Figur ueber ECHTEN Import (`[charaktere] -> [2]`,
  valide v7-Save-Fixturdatei als Importdatei-Pfad). Wird betreiberseitig
  ALS ERSTER angenommen -> `guest_tokens[0]` -> LEADER (empirisch aus
  `ui/tui.py:_cmd_table_start` + `core/runtime.py:run_full_section`
  hergeleitet, s. Report).
- Gast B (`GAST_B_ID`): Figur ueber ECHTE Betreiber-genehmigte Erschaffung
  (`[charaktere] -> [4]` Anfrage, Betreiber `[charaktere] -> [4] -> [1] ->
  [1]` Annahme, Gast `[charaktere] -> [5]` Dialogabschluss, GENAU EIN
  GM-Call). Wird als ZWEITER angenommen -> NICHT-Leader-Mitglied.

Beide Gaeste treten ueber die ECHTE "Tisch"-Menuefuehrung bei (`[tisch]`
-> nummerierte Unterauswahl, KEIN `tisch-anbieten`/`tisch-annehmen`-
Rohbefehl als Ersatz fuer die Menueauswahl -- diese Wortaliase bleiben nur
Experten-/Kompatibilitaetswege, der Beleg hier laeuft ausschliesslich ueber
die im `[tisch]`-Untermenue gezeigten Nummern). Ein gemeinsames Spiel mit
GENAU EINEM GM-Double bedient alle vier realen GM-Rufe dieses Normalwegs
in Reihenfolge (Gast-B-Erschaffung, Leader-Anker, Gast-B-Erstbeitrag,
Leader-Debrief mit COMPLETION_MARKER + je einem v7-Block pro Mitglied).
Beide Gaeste bedienen am Ende real ihre persoenliche Abschlusskarte
(echter `_cmd_export`-Aufruf ueber die angezeigte Nummer); der figurfreie
Betreiber bedient seine eigene, figurfreie Tisch-Abschlusskarte.

DREI vollstaendig getrennte Originalkanaele (je ein eigener `_LineReader`
auf einem eigenen rohen Dateideskriptor, s. `drive_r4_evidence_2026_11_04.
py`-Harness-Docstring): Betreiberprozess-stdout (`host_reader`),
Gast-A-Helferprozess-stdout (`reader_a`), Gast-B-Helferprozess-stdout
(`reader_b`). Jeder Kanal akkumuliert ALLES, was auf ihm gelesen wird, in
seinem eigenen Transkriptkoerper -- kein verworfenes Drainstueck, kein
Gastblock im Hoststdout-Koerper. Eine zusaetzliche Gesamtchronik
(`io_transcript.json`) verweist nur auf diese Originale mit ehrlicher
Kanalquelle + beobachteter Reihenfolge (gepufferter Empfang beweist NICHT
den exakten Schreibzeitpunkt, s. Report).

Launcher-/GM-Double-/FIFO-Mechanik bytegleich aus der bestehenden
`drive_r4_evidence_2026_11_04.py`-Harness importiert (`_LineReader`,
`_drain`, `_wait_for_marker`, `_wait_for_path`, `_send_op`, `_send_guest`,
`_write_gm_double_config`, `_gm_double_env`, `_LAUNCHER`) -- kein zweiter
Transportpfad. `--guest-terminal` ist wiederholbar (argparse
`action="append"`, `scripts/mmo_sim.py:353`/Verarbeitungsschleife `:421`);
dieser Treiber startet zwei echte Helferprozesse `scripts/zeitriss-gast-
terminal.sh <guest_id> <in_fifo> <out_fifo>` (reale OS-Prozesse, NICHT
`r4._open_guest_fifo_pair`).

GM NUR als Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`), NIE Live-
Modell. Kein Netz, keine Tokenwerte.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import select
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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path("/home/altair/zr-vollendung-20261107/r4/evidence/u5-zweigast")
_GUEST_HELPER = _REPO_ROOT / "scripts" / "zeitriss-gast-terminal.sh"

BETREIBER_ID = "betreiber_u5"
GAST_A_ID = "gast_a_u5"
GAST_B_ID = "gast_b_u5"
CHAR_A = "chrono-u5-zweigast-gast-a"
CHAR_B = "chrono-u5-zweigast-gast-b"
TABLE_KEY = "mesaU5zwei"
TABLE_ID = f"local-{GAST_A_ID}-{GAST_B_ID}"


def _wait_for_buffered_substr(reader: "r4._LineReader", marker: str, overall: float = 20.0) -> str:
    """Betreiberkanal-Sonderfall: `TuiSession._readline`/`_readline_with_
    controls` schreibt ein freies (nicht-Steuerzeilen-)Prompttext-Argument
    am OPERATOR-Terminal ueber das eingebaute `input(prompt)` -- das
    schreibt den Prompt laut Python-Doku OHNE Trailing-Newline (echtes
    Terminal-Verhalten: Cursor bleibt in derselben Zeile). `r4._LineReader.
    pop_line()`/`_wait_for_marker` liefern aber erst dann eine "Zeile",
    wenn ein '\\n' im Puffer steht -- ein solcher Prompt wuerde dort NIE als
    Zeile erscheinen (Unterschied zu den Gast-Kanaelen: `scripts/mmo_sim.
    py:_fifo_print_fn._fn` haengt beim Echo IMMER ein '\\n' an, s.
    `_FifoInputReader.read_line`). Dieser Helfer sucht den Marker daher
    direkt im (noch unverzehrten) `_buf` des Readers, OHNE eine Zeile zu
    konsumieren -- die nachfolgende `_wait_for_marker`/`pop_line`-Nutzung
    bleibt dadurch unveraendert korrekt (der Text wird spaeter Teil der
    naechsten echten Zeile)."""
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
    """Parst eine gedruckte Zeile der Form \"... [1] 'a' [2] 'b' ...\" und
    liefert die Nummer, deren Eintrag `needle` enthaelt -- echte Auswahl
    ueber die tatsaechlich gezeigte Nummer, kein Raten der Reihenfolge."""
    import re
    for num, val in re.findall(r"\[(\d+)\]\s*'?([^'\s]+)'?", list_line):
        if val == needle:
            return num
    raise AssertionError(f"{needle!r} nicht in Liste gefunden: {list_line!r}")


def run_scene_u5() -> dict:
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

        # ── Gast A: valide v7-Save-Importdatei-Fixture (echtes Save, kein
        # vorab gebundener Figur-Seed -- die Figur entsteht ERST ueber den
        # echten [charaktere]->[2]-Importweg unten).
        import_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-u5-zweigast-gast-a-001")
        fixture_a_path = root / "gast_a_import.json"
        fixture_a_path.write_text(json.dumps(import_block_a, ensure_ascii=False), encoding="utf-8")

        # ── GM-Double: GENAU VIER Antworten fuer GENAU VIER reale GM-Rufe
        # dieses Normalwegs (empirisch hergeleitet):
        #   (1) Gast-B-Erschaffung (`core/creation_service.py:run_admitted_
        #       creation_dialog` -- EIN GM-Turn liefert bereits den
        #       vollstaendigen v7-Block, s. `test_r4_u2_gast_erschaffung_
        #       menu_2026_11_07.py`-Muster).
        #   (2) Leader-Anker (`core/runtime.py:run_full_section`, Zeile
        #       ~1344f: `if not self._leader_anchored: act(leader, ...)`).
        #   (3) Gast-B-Erstbeitrag (`run_full_section` Zeile ~1350f: `for pk
        #       in [m for m in self.table.members if m != leader]: act(pk, ...)`
        #       -- GENAU EIN Nicht-Leader-Mitglied in diesem Tisch).
        #   (4) Leader-Debrief mit `COMPLETION_MARKER` (`run_full_section`
        #       Zeile ~1389: `act(leader, debrief_ctx)` in der
        #       Fortsetzungsschleife) -- traegt je EINEN v7-Block pro
        #       Mitglied (CHAR_A, CHAR_B), damit `harvest_from_debrief`
        #       BEIDEN eine fortschrittstragende Endfassung zuordnet.
        creation_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-u5-zweigast-gast-b-001")
        creation_response = "```json\n" + json.dumps(creation_block_b, ensure_ascii=False) + "\n```"
        debrief_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-u5-zweigast-gast-a-002", level=2)
        debrief_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-u5-zweigast-gast-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet, beide Standsicherungen anbei.\n"
            "```json\n" + json.dumps(debrief_block_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_block_b) + "\n```\n"
            + COMPLETION_MARKER
        )
        # TREIBER-EIGENSCHAFT (empirisch aus `tests/mmo_sim/_r4_gm_double.py:
        # build()`/`_R4GmDoubleTransport.__init__` hergeleitet, kein
        # Produktfehler): `build()` liest `MMO_SIM_R4_GMDOUBLE_CONFIG` JEDES
        # MAL FRISCH von Platte und konstruiert eine NEUE Transport-Instanz
        # mit einer EIGENEN Kopie von `responses` (`self._responses =
        # list(cfg.get("responses") or [])`), die sie unabhaengig per
        # `pop(0)` verbraucht -- NUR `_STATE["call_index"]` (fuer
        # `calls_log`/Stop-Races) ist modulglobal und damit ueber mehrere
        # Instanzen hinweg fortlaufend. `_cmd_gast_erschaffung_dialog`
        # (Grant ueber die ANBIETER-Autoritaet, s. `_creation_authority`)
        # UND `_run_table_round` rufen `self.gm_transport_factory(...)` HIER
        # je EINMAL GETRENNT auf -- zwei Instanzen, zwei unabhaengige
        # `responses`-Kopien. Eine einzige gemeinsame 4-elementige Liste
        # wuerde daher der RUNDEN-Instanz wieder bei Index 0 (dem
        # Erschaffungsblock) beginnen lassen, NICHT beim Leader-Anker.
        # Deshalb: die Konfigdatei traegt ZUERST nur die EINE Erschaffungs-
        # antwort; der Treiber SCHREIBT SIE NACH Gast Bs Erschaffung
        # (`dialog_done`-Marker unten) auf die restlichen drei Rundentexte
        # um -- derselbe Schreibweg (`r4._write_gm_double_config`), nur ein
        # zweiter Zeitpunkt, kein zweiter Mechanismus.
        r4._write_gm_double_config(cfg_path, responses=[creation_response], calls_log=calls_log)
        env = r4._gm_double_env(cfg_path)

        argv = [
            # TREIBER-EIGENSCHAFT (empirisch, kein Produktfehler, analog
            # `_LineReader`s Docstring): der Betreiber ist hier figurfrei
            # und liefert WAEHREND der laufenden Runde keine einzige eigene
            # Tastatureingabe mehr (beide Spielzuege/Reflexionen/Karten
            # laufen ueber die registrierten Gast-FIFOs) -- `input()`
            # flusht `sys.stdout` nur VOR dem naechsten eigenen
            # `input()`-Aufruf. Ohne `-u` blieben die zwischenzeitlichen
            # `self._print`-Aufrufe des Betreiberprozesses (u.a. "Tisch
            # '...' gestartet", die figurfreie Tisch-Abschlusskarte) im
            # Block-Puffer des Kindprozesses haengen, bis der Betreiber
            # selbst wieder liest -- bei einem ECHTEN Terminal (Tty, immer
            # zeilengepuffert) besteht diese Verzoegerung nicht. `-u`
            # erzwingt dasselbe zeilengepufferte Verhalten wie ein echtes
            # Terminal; reine Testharness-Eigenschaft, keine Produkt-
            # aenderung.
            sys.executable, "-u", "-B", str(r4._LAUNCHER),
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

        # ── Zwei ECHTE Helferprozesse (eigene Betriebssystem-Programme),
        # NICHT `r4._open_guest_fifo_pair`.
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
        header_a_joined = "".join(header_a)
        header_b_joined = "".join(header_b)
        assert "ZEITRISS -- lokaler Gast-Anschluss" in header_a_joined, header_a_joined
        assert "ZEITRISS -- lokaler Gast-Anschluss" in header_b_joined, header_b_joined
        assert "Auswahl:" in header_a_joined, header_a_joined
        assert "Auswahl:" in header_b_joined, header_b_joined

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
            """Fuer bare `input(prompt)`-Text ohne Trailing-Newline am
            Betreiberkanal (s. `_wait_for_buffered_substr`-Docstring)."""
            return _wait_for_buffered_substr(host_reader, marker, overall=overall)

        def drain_a(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_a, settle=settle, overall=overall)
            transcript_a.extend(lines)
            return "".join(lines)

        def drain_b(settle: float = 0.6, overall: float = 10.0) -> str:
            lines = r4._drain(reader_b, settle=settle, overall=overall)
            transcript_b.extend(lines)
            return "".join(lines)

        # ═══════════════════ Gast A: ECHTER Import ([charaktere]->[2]) ═════
        send_a("charaktere")
        charaktere_a = wait_a("[2] Importieren")
        assert "[4] Gast-Erschaffungsanfrage an Betreiber stellen" in charaktere_a, charaktere_a
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
        # (1) Gast B stellt die Anfrage ueber [charaktere]->[4].
        send_b("charaktere")
        charaktere_b_1 = wait_b("Gast-Erschaffungsanfrage an Betreiber stellen")
        assert "[5]" not in charaktere_b_1, charaktere_b_1  # [5] erscheint erst NACH der eigenen Anfrage.
        send_b("4")
        wait_b("Betreiber fuer die Erschaffungsanfrage")
        send_b(BETREIBER_ID)
        request_b = wait_b("Erschaffungsanfrage an Betreiber")

        # (2) Betreiber entscheidet nummeriert ueber [charaktere]->[4]->[1]->[1].
        send_host("charaktere")
        charaktere_host = wait_host("Gast-Erschaffungsanfragen entscheiden")
        send_host("4")
        pending_list = wait_host_prompt("Welcher Gast")
        idx_b_pending = _extract_index(pending_list, GAST_B_ID)
        send_host(idx_b_pending)
        wait_host_prompt("annehmen")
        send_host("1")
        granted = wait_host(f"Gast '{GAST_B_ID}' freigegeben")

        # (3) Gast B fuehrt ueber [charaktere]->[5] den freigegebenen Dialog
        # zu Ende -- GENAU EIN realer GM-Call (creation_response oben).
        send_b("charaktere")
        charaktere_b_2 = wait_b("Eigenen Erschaffungsdialog fortsetzen")
        send_b("5")
        dialog_done = wait_b("Erschaffung abgeschlossen")

        # Konfigdatei JETZT auf die drei verbleibenden Rundentexte umschreiben
        # (s. Begruendung oben) -- die noch zu konstruierende Runden-
        # Transport-Instanz (`_run_table_round`s `self.gm_transport_factory(
        # table.table_id)`, EIN separater `build()`-Aufruf) liest diese Datei
        # ERST SPAETER (beim Leader-Anker) frisch ein.
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
        tisch_host_1 = wait_host("[5] Tisch anbieten")
        send_host("5")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        offer_out = wait_host(f"Tisch '{TABLE_KEY}' offen")

        # ═══════════════ Beide Gaeste fragen den Tisch nummeriert an ═══════
        send_a("tisch")
        tisch_a = wait_a("[2] Tisch anfragen")
        send_a("2")
        wait_a("Welcher Tisch")
        send_a(TABLE_KEY)
        request_a = wait_a(f"Anfrage an Tisch '{TABLE_KEY}' gestellt")
        # R4 FIX6-Grenze (empirisch, kein Produktfehler): NUR der
        # Hauptmenue-Toplevel-Read nutzt `_readline_guest_menu` (Claim-
        # bewusst, s. tui.py:run()); das "Tisch"-Untermenue selbst liest
        # seine eigene "Auswahl:"-Zeile ueber den gewoehnlichen,
        # NICHT-Claim-bewussten `_readline_with_controls`. Ein Gast, der in
        # diesem Untermenue "sitzen bleibt", waere beim spaeteren
        # host-getriebenen Rundenclaim ein zweiter, unkoordinierter Leser
        # derselben FIFO. '/zurueck' fuehrt daher JEDEN Gast vor Rundenstart
        # zurueck zum claim-bewussten Hauptmenue-Prompt.
        send_a("/zurueck")
        drain_a(settle=0.5, overall=5.0)

        send_b("tisch")
        tisch_b = wait_b("[2] Tisch anfragen")
        send_b("2")
        wait_b("Welcher Tisch")
        send_b(TABLE_KEY)
        request_table_b = wait_b(f"Anfrage an Tisch '{TABLE_KEY}' gestellt")
        send_b("/zurueck")
        drain_b(settle=0.5, overall=5.0)

        # ═══ Betreiber nimmt GAST A ZUERST an -> wird Leader (guest_tokens[0],
        # s. tui.py:_cmd_table_start roster-Ableitung + Report). ═══
        wait_host("[6] Anfrage annehmen")
        send_host("6")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        open_requests_1 = wait_host_prompt("Welcher Gast")
        idx_a = _extract_index(open_requests_1, GAST_A_ID)
        send_host(idx_a)
        accept_a_table = wait_host(f"'{GAST_A_ID}' an Tisch '{TABLE_KEY}' aufgenommen")

        # ═══ Betreiber nimmt GAST B danach an -> Nicht-Leader-Mitglied. ═══
        wait_host("[6] Anfrage annehmen")
        send_host("6")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        open_requests_2 = wait_host_prompt("Welcher Gast")
        idx_b_table = _extract_index(open_requests_2, GAST_B_ID)
        send_host(idx_b_table)
        accept_b_table = wait_host(f"'{GAST_B_ID}' an Tisch '{TABLE_KEY}' aufgenommen")

        # ═══════════════ Betreiber startet den Tisch ═══════════════════════
        wait_host("[8] Tisch starten")
        send_host("8")
        wait_host_prompt("Welcher Tisch")
        send_host(TABLE_KEY)
        started = wait_host(f"Tisch '{TABLE_KEY}' gestartet", overall=60.0)

        # ═══ Nicht-Leader-Konsens (Gast B tritt der Runde ausdruecklich bei). ═══
        consent_b = wait_b("beitreten? [j/n]")
        assert "Dieser lokalen Runde" in consent_b, consent_b
        assert f"Leader: {GAST_A_ID}" in consent_b, consent_b
        send_b("j")

        # ═══ Assertion: Leader-Anker (Gast A) -- woertliche SL-Zeile. ═══
        leader_anchor = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Empfaenger: Spielleitung (SL)" in leader_anchor, leader_anchor
        send_a("Ich sichte knapp die Lage am Tisch.")

        # ═══ Assertion: Gast-B-Erstbeitrag -- strukturell verwandte,
        # woertlich ANDERE Empfaengerzeile (kein Leader). ═══
        guest_b_first = wait_b("Empfaenger: ueber Leader an Spielleitung")
        assert "Empfaenger: ueber Leader an Spielleitung" in guest_b_first, guest_b_first
        assert "Unbekannte Auswahl" not in guest_b_first, guest_b_first
        send_b("Ich pruefe meine Ausruestung und melde mich.")

        # ═══ Leader-Debrief (zweiter Leader-Zug, loest COMPLETION_MARKER
        # ueber die GM-Double-Antwort aus). ═══
        leader_second = wait_a("Empfaenger: Spielleitung (SL)")
        assert "Unbekannte Auswahl" not in leader_second, leader_second
        send_a("Ich schliesse den Abschnitt ab.")

        # ═══ Freiwillige lokale Abschlussnotiz je Mitglied -- empirisch
        # belegte `table.members`-Reihenfolge: `sorted({GAST_A_ID, GAST_B_ID})`
        # (core/store.py:158 `members = sorted({o["from"]} | o["wants"])`)
        # ergibt GAST_A_ID VOR GAST_B_ID (alphabetisch 'a' < 'b'). ═══
        notiz_a = wait_a("eigene lokale Notiz")
        send_a("Abschlussnotiz Leader (Gast A): Reise erfolgreich.")
        notiz_b = wait_b("eigene lokale Notiz")
        send_b("Abschlussnotiz Gast B: Erschaffung und erster Einsatz gelungen.")

        final_path = run_dir / "completion" / f"{TABLE_ID}-section__final.json"
        r4._wait_for_path(final_path, overall=25.0)

        # ═══════════════ Abschlusskarten: beide Gaeste bedienen real ═══════
        # `_dispatch_completion_card_choice` (tui.py:8614ff) fuehrt GENAU
        # EINEN Handler pro Nummer aus und kehrt danach zum naechsten
        # Hauptmenue zurueck -- die Export-Nummer ist daher die EINE reale
        # Aktion, deren Ausfuehrung UND automatische Rueckkehr zum
        # Hauptmenue zusammen belegt werden (s. Report, "Abschlusskarte").
        card_a = wait_a("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_A_ID}'" in card_a, card_a
        assert ") Export des eigenen Standes" in card_a, card_a
        assert ") Zurueck zum Hauptmenue" in card_a, card_a
        send_a("1")
        export_a = wait_a("Zusaetzlich als Datei gespeichert")

        card_b = wait_b("Tisch suchen/beitreten")
        assert f"Abschlusskarte fuer '{GAST_B_ID}'" in card_b, card_b
        assert ") Export des eigenen Standes" in card_b, card_b
        assert ") Zurueck zum Hauptmenue" in card_b, card_b
        send_b("1")
        export_b = wait_b("Zusaetzlich als Datei gespeichert")

        # ═══════════════ Figurfreie Betreiber-Tisch-Abschlusskarte ═════════
        operator_card = wait_host("Beenden (zurueck zum Hauptmenue)")
        assert f"Tisch-Abschlusskarte (Betreiber, figurfrei) fuer '{TABLE_ID}'" in operator_card, operator_card
        assert "Keine eigene Figur" in operator_card, operator_card
        send_host("3")
        operator_card_done = wait_host("Tisch 'mesaU5zwei': Abschnitt")

        # ═══ Betreiber verlaesst das Tisch-Untermenue (continue-Schleife
        # nach `_cmd_table_start`) und beendet den Prozess. ═══
        send_host("/zurueck")
        time.sleep(0.4)
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
        assert proc.returncode == 0, f"U5-Zweigast: Betreiberprozess gescheitert: {stderr_text}"
        assert final_path.exists(), "U5-Zweigast: regulaerer Abschluss haette __final.json schreiben muessen."

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

        # ═══════════════ Assertion: beide Reloads lvl>start (lvl 1 -> 2) ═══
        guest_a_private = onboarding.peek(op_data / "guests" / GAST_A_ID / "onboarding", GAST_A_ID)
        assert guest_a_private is not None and guest_a_private.final_save is not None, (
            "U5-Zweigast: Gast A (Leader) haette ueber den normalen Rueckkanal "
            "(_writeback_registered_guest_saves) eine abgeschlossene private Fassung bekommen muessen."
        )
        reloaded_a = guest_a_private.final_save["characters"][0]
        assert reloaded_a["id"] == CHAR_A, reloaded_a
        assert reloaded_a["lvl"] == 2 > 1, reloaded_a

        guest_b_private = onboarding.peek(op_data / "guests" / GAST_B_ID / "onboarding", GAST_B_ID)
        assert guest_b_private is not None and guest_b_private.final_save is not None, (
            "U5-Zweigast: Gast B (Nicht-Leader) haette ueber denselben Rueckkanal eine "
            "abgeschlossene private Fassung bekommen muessen."
        )
        reloaded_b = guest_b_private.final_save["characters"][0]
        assert reloaded_b["id"] == CHAR_B, reloaded_b
        assert reloaded_b["lvl"] == 2 > 1, reloaded_b

        # ═══════════════ Dritte unabhaengige Bestaetigung: ECHTER frischer
        # Prozess liest den persoenlichen Exportstand jedes Gastes erneut
        # und bestaetigt lvl>start ueber die Exportdatei selbst (nicht nur
        # onboarding.peek). ═══
        export_a_path = op_data / "guests" / GAST_A_ID / "exports" / f"{GAST_A_ID}.json"
        export_b_path = op_data / "guests" / GAST_B_ID / "exports" / f"{GAST_B_ID}.json"
        assert export_a_path.exists(), f"U5-Zweigast: Export-Datei A fehlt: {export_a_path}"
        assert export_b_path.exists(), f"U5-Zweigast: Export-Datei B fehlt: {export_b_path}"
        export_a_block = json.loads(export_a_path.read_text(encoding="utf-8"))
        export_b_block = json.loads(export_b_path.read_text(encoding="utf-8"))
        assert export_a_block["characters"][0]["lvl"] == 2, export_a_block
        assert export_b_block["characters"][0]["lvl"] == 2, export_b_block

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 4, f"U5-Zweigast: GENAU VIER reale GM-Rufe erwartet: {calls}"

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "betreiber_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text, pid=proc.pid,
        )
        helper_argv_a = [str(_GUEST_HELPER), GAST_A_ID, str(in_fifo_a), str(out_fifo_a)]
        helper_argv_b = [str(_GUEST_HELPER), GAST_B_ID, str(in_fifo_b), str(out_fifo_b)]
        r6.write_process_result(
            out_dir, "gast_a_helper_process", argv=helper_argv_a, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_a.returncode,
            stdout_text=full_guest_a_stdout, stderr_text=stderr_a, pid=helper_a.pid,
        )
        r6.write_process_result(
            out_dir, "gast_b_helper_process", argv=helper_argv_b, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper_b.returncode,
            stdout_text=full_guest_b_stdout, stderr_text=stderr_b, pid=helper_b.pid,
        )
        mf.record_process_files(
            "betreiber_launcher", aussage="u5_zweigast_figurfrei_betreiber_launcher_transcript",
            run_id="U5-ZWEIGAST", teilnehmer_figur=BETREIBER_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_a_helper_process", aussage="u5_zweigast_gast_a_import_leader_transcript",
            run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_A_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.record_process_files(
            "gast_b_helper_process", aussage="u5_zweigast_gast_b_erschaffung_nichtleader_transcript",
            run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_B_ID, tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.export_tree(
            run_dir, "run", aussage="u5_zweigast_run_dir_after_finish", run_id="U5-ZWEIGAST",
            teilnehmer_figur="beide", tisch_abschnitt=f"{TABLE_KEY}/{TABLE_ID}-section",
        )
        mf.export_tree(
            op_data / "guests" / GAST_A_ID / "onboarding", "gast_a_onboarding",
            aussage="u5_zweigast_gast_a_private_after_finish", run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_A_ID,
        )
        mf.export_tree(
            op_data / "guests" / GAST_B_ID / "onboarding", "gast_b_onboarding",
            aussage="u5_zweigast_gast_b_private_after_finish", run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_B_ID,
        )
        mf.export_file(
            export_a_path, "gast_a_export.json", aussage="u5_zweigast_gast_a_export_reload",
            run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_A_ID,
        )
        mf.export_file(
            export_b_path, "gast_b_export.json", aussage="u5_zweigast_gast_b_export_reload",
            run_id="U5-ZWEIGAST", teilnehmer_figur=GAST_B_ID,
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="u5_zweigast_gm_double_calls", run_id="U5-ZWEIGAST",
            teilnehmer_figur="beide",
        )
        mf.write_json_body(
            "io_transcript.json",
            {
                "_hinweis": (
                    "Diese Gesamtchronik VERWEIST nur auf die drei getrennten Originalkanaele "
                    "(betreiber_launcher/gast_a_helper_process/gast_b_helper_process .stdout.txt) in "
                    "der HIER beobachteten Reihenfolge -- gepufferter Empfang beweist NICHT den "
                    "exakten Schreibzeitpunkt im Zielprozess."
                ),
                "header_a": header_a_joined, "header_b": header_b_joined,
                "charaktere_a_menu": charaktere_a, "import_preview_a": preview_a, "import_accept_a": accept_a,
                "charaktere_b_request_menu": charaktere_b_1, "request_b": request_b,
                "operator_entscheiden_menu": charaktere_host, "pending_list": pending_list, "granted": granted,
                "charaktere_b_dialog_menu": charaktere_b_2, "dialog_done": dialog_done,
                "offer_out": offer_out, "request_a": request_a, "request_table_b": request_table_b,
                "accept_a_table": accept_a_table, "accept_b_table": accept_b_table, "started": started,
                "consent_b": consent_b, "leader_anchor": leader_anchor, "guest_b_first": guest_b_first,
                "leader_second": leader_second, "notiz_a": notiz_a, "notiz_b": notiz_b,
                "card_a": card_a, "export_a": export_a, "card_b": card_b, "export_b": export_b,
                "operator_card": operator_card, "operator_card_done": operator_card_done,
                "reloaded_a": {"id": reloaded_a["id"], "lvl": reloaded_a["lvl"]},
                "reloaded_b": {"id": reloaded_b["id"], "lvl": reloaded_b["lvl"]},
            },
            aussage="u5_zweigast_dialog_io_transcript_verweis", run_id="U5-ZWEIGAST", teilnehmer_figur="beide",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "U5_zweigast_figurfrei_betreiber_zwei_echte_gasthelfer_prozesse",
            "aussage": (
                f"Figurfreier Betreiber ({BETREIBER_ID}) fuehrt ZWEI echte Gasthelfer-Prozesse "
                f"durch dieselbe normale Menuefuehrung: {GAST_A_ID} (Import, wird LEADER weil als "
                f"erster angenommen) und {GAST_B_ID} (Betreiber-genehmigte Erschaffung, NICHT-Leader). "
                "Gemeinsames Spiel ueber EIN GM-Double (4 reale Rufe: Erschaffung, Leader-Anker, "
                "Gast-B-Erstbeitrag, Leader-Debrief). Beide Gaeste bedienen ihre Abschlusskarte real "
                "(echter Export, dann automatische Rueckkehr zum Hauptmenue -- "
                "_dispatch_completion_card_choice fuehrt genau EINEN Handler pro Nummer aus, s. "
                "Report). Figurfreier Betreiber bedient seine eigene figurfreie Tisch-"
                "Abschlusskarte. Beide Reloads lvl 1 -> 2 (ueber onboarding.peek UND die echte "
                "Exportdatei eines frisch gelesenen Standes bestaetigt)."
            ),
            "drei_getrennte_originalkanaele": True,
            "echter_neuer_os_prozess_gast_a": True,
            "echter_neuer_os_prozess_gast_b": True,
            "gm_anbieter_ist_grenzinjektion": "MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "anzahl_gm_rufe": len(calls),
            "leader": GAST_A_ID, "nicht_leader": GAST_B_ID,
            "betreiber_figurfrei_und_nicht_leader": True,
            "final_written": final_path.exists(),
            "gast_a_reload_lvl": reloaded_a["lvl"], "gast_b_reload_lvl": reloaded_b["lvl"],
        })

        findings["final_written"] = final_path.exists()
        findings["leader"] = GAST_A_ID
        findings["gm_calls"] = len(calls)
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        run_scene_u5()
        print("OK   U5_zweigast_figurfrei_betreiber_zwei_echte_gasthelfer_prozesse")
        return 0
    except AssertionError as e:
        print(f"FAIL U5_zweigast_figurfrei_betreiber_zwei_echte_gasthelfer_prozesse: {e}")
        return 1
    except Exception:
        print("ERROR U5_zweigast_figurfrei_betreiber_zwei_echte_gasthelfer_prozesse:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
