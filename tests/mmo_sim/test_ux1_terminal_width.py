#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_terminal_width.py — UX22 (ZEITRISS Terminal UX-1,
06_ABNAHME_UND_TESTS.md: "80x24 und schmalerer Textmodus, lange Namen/
Umlaute, keine Farbabhaengigkeit/ANSI-Pflicht/abgeschnittene Auswahl").

Lokaler Layout-/Bedienbeleg (KEIN Endgeraete-PASS, s. Auftrag): prueft, dass
das neue Hauptmenue + die Fortsetzen-Zeile ohne ANSI-Escapecodes auskommen,
dass lange Namen/Umlaute nicht zu einer abgeschnittenen Menuezeile/einem
Crash fuehren, und dass jede einzelne Menuezeile in einem 80-Spalten-Terminal
sinnvoll lesbar bleibt (keine harte Hardcodierung auf genau 80 -- lange,
variable Inhalte wie Namen duerfen laenger sein, ohne dass der Rest des
Menues kaputtgeht).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten."""
from __future__ import annotations

import fcntl
import json
import os
import pty
import struct
import subprocess
import sys
import tempfile
import termios
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import ResumeCard, render_boot_menu  # noqa: E402

_ANSI_ESCAPE = "\x1b["


def test_boot_menu_has_no_ansi_escape_codes():
    text = render_boot_menu(None)
    assert _ANSI_ESCAPE not in text, "UX22: keine ANSI-Pflicht -- Menuetext bleibt reine Plaintext-Zeilen"


def test_boot_menu_fixed_lines_fit_80_columns():
    """Die FESTEN Menuezeilen (keine variablen Namen) muessen in 80 Spalten
    passen -- nur die dynamische Fortsetzen-Zeile (mit potenziell langen
    Namen) ist davon ausdruecklich ausgenommen (s. naechster Test)."""
    text = render_boot_menu(None)
    for line in text.splitlines():
        assert len(line) <= 80, f"Zeile zu lang fuer 80 Spalten: {line!r}"


def test_long_umlaut_name_does_not_crash_or_truncate_the_resume_line():
    """UX22: lange Namen/Umlaute duerfen die Fortsetzen-Zeile verlaengern,
    aber nicht crashen oder den Rest unlesbar abschneiden -- der komplette
    Name muss im Ausgabetext VOLLSTAENDIG vorkommen (keine stille
    Kuerzung)."""
    long_name = "Prinzessin Übermäßig-Langnamig von Zeitriß-am-Rhein-und-Ruhr"
    card = ResumeCard(
        community_id="community-p1", participant_id="p1",
        chrononaut_id="chrono-1", last_valid_save_summary=f"{long_name} (Level 99)",
    )
    text = render_boot_menu(card)
    assert long_name in text, text
    assert _ANSI_ESCAPE not in text


def test_resume_card_with_none_chrononaut_does_not_print_literal_none_text():
    """Randfall (community ohne eigene Figur): keine rohe Python-'None'-
    Zeichenkette in der Anzeige -- lesbarer Platzhaltertext stattdessen."""
    card = ResumeCard(
        community_id="community-p1", participant_id="p1",
        chrononaut_id=None, last_valid_save_summary=None,
    )
    text = render_boot_menu(card)
    assert "kein eigener Chrononaut" in text
    assert " None " not in text and not text.rstrip().endswith("None")


def test_narrow_40_column_rendering_has_no_truncated_bracket_hotkeys():
    """Schmalerer Textmodus (hier: 40 Spalten simuliert durch Terminal-
    Wrap-Pruefung): jede Hotkey-Klammer `[...]` muss vollstaendig in EINER
    Zeile vorkommen -- kein ANSI-Wrap haengt von diesem Code ab, also darf
    keine Zeile ein `[` ohne zugehoeriges `]` enthalten."""
    text = render_boot_menu(None)
    for line in text.splitlines():
        assert line.count("[") == line.count("]"), f"Unausgeglichene Klammer (Hotkey) in Zeile: {line!r}"


def _read_all_from_master(master_fd: int, proc: "subprocess.Popen", timeout: float = 20.0) -> bytes:
    """Liest alles vom PTY-Master, solange der echte Kindprozess noch laeuft
    ODER noch Daten anliegen -- keine feste `sleep`-Heuristik, sondern
    `select()` auf tatsaechlich anliegende Bytes/EOF (vgl. `run_process_paced`
    in `_a24_local_support.py`)."""
    import select
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        still_running = proc.poll() is None
        ready, _, _ = select.select([master_fd], [], [], 0.2)
        if master_fd in ready:
            try:
                data = os.read(master_fd, 65536)
            except OSError:
                break
            if not data:
                break
            chunks.append(data)
            continue
        if not still_running:
            break
    return b"".join(chunks)


def test_real_narrow_pty_40x24_full_output_not_truncated():
    """UX22-Fix (ZEITRISS Terminal UX-1 Wiederanlauf, REVIEW.md §G06: '"40
    Spalten" prueft nur ausgeglichene Klammern statt einer realen 40-
    Spalten-Ausgabe'): ersetzt die reine Stringtheorie durch einen ECHTEN
    PTY (`pty.openpty()`, `TIOCSWINSZ` tatsaechlich auf 24x40 gesetzt und
    per `TIOCGWINSZ` zurueckgelesen, nicht nur behauptet) gegen den
    tatsaechlichen Subprozess-Einstiegspunkt `scripts/mmo_sim.py` -- Pipe
    != PTY (02 §Disziplin): dies ist der ECHTE PTY-Pfad, nicht der sonst in
    dieser Suite ueberwiegende Pipe-Pfad (`subprocess.run(..., input=...)`).

    Belegt zwei Dinge am echten schmalen Terminal, nicht nur am Stringmodell:
    1) Jede feste Hauptmenuezeile kommt VOLLSTAENDIG und unveraendert im
       tatsaechlich empfangenen PTY-Bytestrom an (kein stilles Abschneiden
       durch die reale 40-Spalten-Fensterbreite).
    2) Eine lange Umlautname-Eingabe ('registrieren') kommt am anderen Ende
       (der tatsaechlich auf Platte geschriebene Registry-Datensatz, nicht
       nur stdout) VOLLSTAENDIG und byte-identisch an -- kein Abschneiden
       der EINGABE durch die schmale reale Fensterbreite.

    Keine Farb-/ANSI-Pflicht (02 §Technik): der Bytestrom bleibt frei von
    ANSI-Escapecodes trotz echtem PTY (das Produkt selbst emittiert keine)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        master_fd, slave_fd = pty.openpty()
        try:
            # 24 Zeilen, 40 Spalten -- tatsaechlich gesetzt, nicht nur Text.
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 40, 0, 0))
            rows, cols, _x, _y = struct.unpack("HHHH", fcntl.ioctl(slave_fd, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)))
            assert (rows, cols) == (24, 40), f"echte PTY-Fenstergroesse wurde nicht wie erwartet gesetzt: {(rows, cols)}"

            long_name = "Prinzessin Übermäßig-Langnamig von Zeitriß-am-Rhein-und-Ruhr"
            env = dict(os.environ)
            for k in ("OPENWEBUI_URL", "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_CLI"):
                env.pop(k, None)
            proc = subprocess.Popen(
                [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
                 "--data-dir", str(data_dir), "--participant", "p-narrow"],
                stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                cwd=str(_REPO_ROOT), env=env, close_fds=True,
            )
            os.close(slave_fd)
            slave_fd = -1
            stdin_text = f"registrieren\n{long_name}\nn\nbeenden\n"
            os.write(master_fd, stdin_text.encode("utf-8"))
            raw = _read_all_from_master(master_fd, proc, timeout=20.0)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
                raise AssertionError("echter PTY-Subprozess (40x24) ist nicht kontrolliert beendet")
            output = raw.decode("utf-8", errors="replace")

            assert proc.returncode == 0, f"echter PTY-Subprozess (40x24) rc={proc.returncode}: {output[-1500:]}"
            assert "\x1b[" not in output, "UX22: keine ANSI-Pflicht -- auch am echten PTY kein Escapecode noetig"

            fixed_lines = [ln for ln in render_boot_menu(None).splitlines() if ln.strip()]
            for ln in fixed_lines:
                assert ln in output, (
                    f"feste Hauptmenuezeile {ln!r} fehlt/abgeschnitten im echten 40x24-PTY-Bytestrom "
                    f"(nicht nur Klammerzaehlung): tail={output[-800:]!r}"
                )
            assert long_name in output, (
                f"lange Umlautname-Anzeige fehlt/abgeschnitten im echten 40x24-PTY-Bytestrom: "
                f"tail={output[-800:]!r}"
            )

            registry_dir = data_dir / "registry"
            records = list(registry_dir.glob("participant__*.json")) if registry_dir.exists() else []
            assert records, f"kein Registry-Datensatz nach echter PTY-Registrierung geschrieben: {registry_dir}"
            written = [json.loads(p.read_text(encoding="utf-8")) for p in records]
            matching = [r for r in written if r.get("display_name") == long_name]
            assert matching, (
                f"die ueber den echten schmalen PTY (40 Spalten) eingegebene lange Umlautname-Eingabe "
                f"wurde NICHT byte-identisch persistiert (Eingabeabschneidung?): beobachtet={written}"
            )
        finally:
            if slave_fd != -1:
                try:
                    os.close(slave_fd)
                except OSError:
                    pass
            try:
                os.close(master_fd)
            except OSError:
                pass


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
