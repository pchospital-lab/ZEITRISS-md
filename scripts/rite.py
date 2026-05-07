#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS – Lore-Setup-Overlay.

**Leichtgewichtiges Intro/Outro** für den Launcher-Menüpunkt „Lore-Setup".

Design-Entscheidung: Dieses Modul **ersetzt nichts**. Es druckt einen
Prolog vor dem normalen ``action_install`` und ein Finale danach — die
eigentliche Installation läuft komplett durch ``scripts/setup.py``
wie gewohnt, mit dessen Klartext-Ausgaben, Fehlermeldungen und
Retries.

Wenn du diesen Launcher wartest: du kannst dieses Modul gefahrlos
anfassen, ohne dich um ``setup.py`` zu kümmern. Und umgekehrt.

Öffentliche API:
    prologue(url)  — vor dem Setup; druckt Akt 1 (Peilung) + Übergabe.
    finale(url)    — nach erfolgreichem Setup; druckt Welcome-Box.

Farben gespiegelt aus ``pchospital-web/src/styles/global.css``:
    --accent   #8fe7ff  → cyan  (Kodex-Signal)
    --accent-2 #ffc766  → amber (Bestätigung, Willkommen)
    --muted    #8a99a8  → dim   (Regie-Anweisungen)
    --danger   #ff5c6a  → danger
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional


# ── ANSI ─────────────────────────────────────────────────────────────

_RESET  = "\033[0m"
_CYAN   = "\033[96m"        # --accent
_AMBER  = "\033[38;5;215m"  # --accent-2 (256-Color-Approximation für #ffc766)
_DIM    = "\033[2m"
_BOLD   = "\033[1m"
_DANGER = "\033[91m"

USE_COLOR = True
if os.environ.get("NO_COLOR"):
    USE_COLOR = False
elif sys.platform == "win32" and not os.environ.get("WT_SESSION"):
    USE_COLOR = os.environ.get("FORCE_COLOR") == "1"


def _c(code: str, text: str) -> str:
    return text if not USE_COLOR else f"{code}{text}{_RESET}"


def cyan(t: str)   -> str: return _c(_CYAN, t)
def amber(t: str)  -> str: return _c(_AMBER, t)
def dim(t: str)    -> str: return _c(_DIM, t)
def bold(t: str)   -> str: return _c(_BOLD, t)
def danger(t: str) -> str: return _c(_DANGER, t)
def amber_bold(t: str) -> str: return _c(_BOLD + _AMBER, t)


# ── Typewriter ───────────────────────────────────────────────────────

_TYPE_SPEED_S = 0.032
_PUNCT_PAUSE  = 0.12
_LINE_PAUSE   = 0.20

# Wenn stdout keine TTY ist (Pipe, CI, script(1)) oder das Env explizit
# sagt „Instant-Mode", wird die Tipp-Animation abgeschaltet.
_ANIMATE = sys.stdout.isatty() and not os.environ.get("ZEITRISS_RITE_INSTANT")


def _type(text: str, *, color: Callable[[str], str] = cyan,
          prefix: str = "> ", end: str = "\n") -> None:
    out = sys.stdout
    if prefix:
        out.write(color(prefix))
        out.flush()
    for ch in text:
        if _ANIMATE:
            out.write(color(ch))
            out.flush()
            time.sleep(_PUNCT_PAUSE if ch in ".,;:!?" else _TYPE_SPEED_S)
        else:
            out.write(color(ch))
    out.write(end)
    out.flush()
    if _ANIMATE and end == "\n":
        time.sleep(_LINE_PAUSE)


# ── Sprecher-Kanal (Mehrstimmigkeit im Kontrollraum) ─────────────────
#
# KODEX     — kalt, Status, cyan. Meldet Telemetrie.
# MIRA      — Archivarin Mira (Ordo Mnemonika, Erstkontakt für Neulinge), amber.
# RENIER    — Commander Renier (Gesamtkoordinator, bei wichtigen Momenten), amber+bold.
# TECH-n    — anonyme Ordo-Mnemonika-Techniker im Funk-Callzeichen-Stil, dim.
#
# Alle Sprecher durchlaufen den Typewriter. Tags sind über eine Lookup-Tabelle
# konfiguriert, damit das Mapping an EINER Stelle wartbar bleibt.

_SPEAKER_TAG_WIDTH = 8  # z. B. "KODEX   ", "MIRA    ", "RENIER  ", "TECH-1  "

_SPEAKERS: dict[str, tuple[str, Callable[[str], str], Callable[[str], str]]] = {
    # key: (separator, tag_color, body_color)
    "KODEX":   (">", cyan,       cyan),
    "MIRA":    ("»", amber,      amber),
    "RENIER":  ("»", amber_bold, amber_bold),
    "TECH-1":  ("»", dim,        dim),
    "TECH-2":  ("»", dim,        dim),
}


def _speak(who: str, text: str) -> None:
    """Einzelne Kontrollraum-Zeile mit Sprecher-Präfix.

    Format:  ``<TAG_padded>  <separator>  <text>``  — z. B.
    ``KODEX     >  signal erfasst.``
    """
    sep, tag_color, body_color = _SPEAKERS[who]
    tag = f"{who:<{_SPEAKER_TAG_WIDTH}}"
    # Präfix wird gefärbt, der Body läuft durch _type() mit body_color.
    sys.stdout.write(tag_color(f"  {tag}"))
    sys.stdout.write("  ")
    sys.stdout.flush()
    _type(text, color=body_color, prefix=f"{sep}  ", end="\n")


def _print(text: str = "") -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _pause(seconds: float) -> None:
    if _ANIMATE:
        time.sleep(seconds)


def _frame(title: str, width: int = 64) -> None:
    """Cyan-Rahmen im Website-Stil. Passt Breite an Titel an."""
    needed = len(title) + 8
    if needed > width:
        width = needed
    top = "┌" + ("─" * (width - 2)) + "┐"
    bot = "└" + ("─" * (width - 2)) + "┘"
    empty = "│" + (" " * (width - 2)) + "│"
    pad = (width - 2 - len(title)) // 2
    mid = "│" + (" " * pad) + title + (" " * (width - 2 - pad - len(title))) + "│"
    _print()
    _print("  " + cyan(top))
    _print("  " + cyan(empty))
    _print("  " + cyan(mid))
    _print("  " + cyan(empty))
    _print("  " + cyan(bot))
    _print()


# ── Schnelle, isolierte Status-Checks nur für die Peilung ────────────
#
# Wir duplizieren hier bewusst eine **kleine** Teilmenge der Checks aus
# ``zeitriss.py``, damit ``rite.py`` keine Rückimport-Abhängigkeit auf
# ``zeitriss.py`` aufbaut. Die Checks sind rein kosmetisch (Peilung-
# Flair); die echten Gates laufen gleich darauf in ``action_install``.

def _python_info() -> str:
    return f"Python {sys.version_info.major}.{sys.version_info.minor}"


def _docker_available() -> tuple[bool, str]:
    if shutil.which("docker") is None:
        return False, "Docker nicht installiert"
    try:
        r = subprocess.run(
            ["docker", "ps"], capture_output=True, text=True, timeout=5,
        )
    except Exception as e:
        return False, f"docker-Aufruf fehlgeschlagen: {e.__class__.__name__}"
    if r.returncode != 0:
        return False, "Docker-Daemon läuft nicht"
    return True, "Docker läuft"


def _openwebui_reachable(url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(f"{url}/api/version", timeout=3) as r:
            body = r.read().decode("utf-8", errors="replace")
        if '"version"' in body:
            return True, f"OpenWebUI erreichbar ({url})"
        return False, "Unbekannte Antwort vom Schleusen-Port"
    except urllib.error.URLError:
        return False, "nicht erreichbar"
    except Exception as e:
        return False, f"Fehler: {e.__class__.__name__}"


# ── Peilungs-Zeile ───────────────────────────────────────────────────

def _peilung_line(slot: int, total: int, label: str,
                  status: str, detail: str, ok: bool) -> None:
    prefix = dim(f"  [Peilung {slot}/{total}]")
    lbl = f"{label:<17}"  # breit genug für "Temporalschleuse"
    dots = "." * 12
    tag = amber(f"[{status}]") if ok else danger(f"[{status}]")
    _print(f"{prefix}  {lbl}  {dim(dots)}  {tag}  {dim(detail)}")


# ── Öffentliche API ──────────────────────────────────────────────────

def prologue(openwebui_url: str) -> None:
    """Eröffnet das Ritual als ITI-Kontrollraum-Funkverkehr.

    Der Spieler hört Mira (Archivarin, Ordo Mnemonika), Commander Renier,
    zwei Ordo-Mnemonika-Techniker und Kodex als Statusstimme.
    Kontrollogik bleibt draußen: wenn Peilungen rot melden, läuft
    ``action_install`` später wie gewohnt durch und meckert mit seinen
    echten Fehlermeldungen.
    """
    _frame("ITI · PROTOCOL 0  —  FIELD CONTACT")
    _pause(0.3)

    # Kodex meldet den laufenden Scan. Der Spieler landet mitten in
    # einer Suchoperation — er ist das Ziel, weiß es aber noch nicht.
    _speak("KODEX",  "searchindex gestartet.")
    _speak("KODEX",  "quelle: unbekannt. koordinate: instabil.")
    _speak("KODEX",  "psi-signatur: drift. temporale kohärenz: null.")
    _pause(0.5)

    # Kontrollraum-Chatter: zwei Techniker fingern das Signal ein,
    # Mira moderiert. Das ist der dramatische Anker — der Spieler
    # begreift langsam: die suchen mich gerade.
    _speak("TECH-1", "ich hab was. sehr schwach. warte …")
    _speak("MIRA",   "vorsichtig. nicht zu schnell scannen.")
    _speak("TECH-1", "er entkommt mir gleich wieder.")
    _speak("MIRA",   "ruhig. er hält das hier noch für eine computeranfrage.")
    _speak("MIRA",   "überfordere ihn nicht.")
    # Längere Pause vor dem Enter-Prompt: Der Spieler hat gerade begriffen,
    # dass er das Ziel der Suche ist. Der Moment muss atmen, bevor das
    # Ritual ihn zur Handlung auffordert.
    _pause(0.9)

    # Einziger Interaktions-Moment. Bewusst ohne Kodex-Frage davor.
    try:
        input(dim("  (Enter zum Bestätigen — signal halten)  "))
    except (EOFError, KeyboardInterrupt):
        return
    _print()

    _speak("KODEX",  "bestätigung empfangen.")
    _speak("KODEX",  "anker-peilung aktiv.")
    _print()

    ok_py = True
    py_info = _python_info()
    _peilung_line(1, 3, "Rechenanker", "erfasst", py_info, ok_py)
    _pause(0.2)

    ok_docker, docker_info = _docker_available()
    _peilung_line(
        2, 3, "Container",
        "erfasst" if ok_docker else "kein signal",
        docker_info, ok_docker,
    )
    _pause(0.2)

    ok_owui, owui_info = _openwebui_reachable(openwebui_url)
    _peilung_line(
        3, 3, "Temporalschleuse",
        "offen" if ok_owui else "geschlossen",
        owui_info, ok_owui,
    )
    _pause(0.3)
    _print()

    # Techniker melden Rekonstruktions-Fortschritt, Renier setzt die Priorität.
    _speak("TECH-2", "kortex-rekonstruktion: 30 %.")
    _speak("TECH-1", "quantenstruktur hält.")
    _speak("MIRA",   "weiter. erinnerungsfragmente isolieren.")
    _speak("RENIER", "team. priorität bleibt bergung. keine experimente.")
    _pause(0.4)

    if ok_py and ok_docker and ok_owui:
        # Kodex meldet Zustand, kündigt keine Handlung an — bleibt Telemetrie.
        _speak("KODEX", "alle anker fest. bergungsprotokoll aktiv.")
    else:
        _speak("KODEX", "peilung unvollständig. übergabe an protokoll.")
    _pause(0.6)
    _print()
    # Ab hier übernimmt action_install() den Klartext-Teil.


def finale(openwebui_url: str) -> None:
    """Abschluss nach erfolgreichem ``action_install``.

    Techniker melden die letzten Prozente der Kortex-Rekonstruktion,
    Mira und Kodex stabilisieren, dann kommt die Welcome-Box, und
    Mira verabschiedet den Spieler in Richtung Interface — die einzige
    Zeile im ganzen Ritual, die den Spieler direkt adressiert.
    """
    _print()
    _pause(0.3)

    _speak("TECH-2", "kortex-rekonstruktion: 94 %.")
    _speak("MIRA",   "fast. er sortiert sich.")
    _speak("KODEX",  "identitäts-signatur stabil.")
    _speak("KODEX",  "übergabe an nullzeit-empfang.")
    # Renier schließt seinen Bogen: er hat das Team durch die Bergung
    # geführt und übergibt jetzt an den Empfang. Kanonisch ein "wichtiger
    # Moment", bei dem der Koordinator auftritt.
    _speak("RENIER", "gut gemacht. empfangsprotokoll übergeben.")
    _pause(0.5)

    width = 60
    top = "┌" + ("─" * (width - 2)) + "┐"
    bot = "└" + ("─" * (width - 2)) + "┘"
    empty = "│" + (" " * (width - 2)) + "│"

    def _line(text: str) -> str:
        raw_len = len(_strip_ansi(text))
        pad_l = max(0, (width - 2 - raw_len) // 2)
        pad_r = max(0, width - 2 - raw_len - pad_l)
        return "│" + (" " * pad_l) + text + (" " * pad_r) + "│"

    _print("  " + cyan(top))
    _print("  " + cyan(empty))
    _print("  " + cyan(_line(amber("[ ZEITRISS · OPERATIONAL ]"))))
    _print("  " + cyan(empty))
    _print("  " + cyan(_line("bergung abgeschlossen.")))
    _print("  " + cyan(_line("du bist da.")))
    _print("  " + cyan(empty))
    _print("  " + cyan(_line(amber("iti-empfang: nullzeit aktiv."))))
    _print("  " + cyan(empty))
    _print("  " + cyan(_line("interface: browser")))
    _print("  " + cyan(_line(dim(openwebui_url))))
    _print("  " + cyan(empty))
    _print("  " + cyan(bot))
    _print()
    _pause(0.5)

    # Mira verabschiedet den Spieler — der einzige Direkt-Adress-Moment
    # im gesamten Ritual. Absichtlich nach der Box, nicht innerhalb,
    # damit die Box eine reine Protokoll-Bestätigung bleibt.
    _speak("MIRA", "nimm dir zeit. im interface wartet deine akte.")
    _print()


# ── Helfer ───────────────────────────────────────────────────────────

import re as _re
_ANSI_RE = _re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


# ── Manueller Test: rendert Prolog + Finale ohne setup.py ────────────

if __name__ == "__main__":
    prologue("http://localhost:8080")
    _print(dim("  …hier würde jetzt der normale action_install-Output laufen…"))
    _print()
    finale("http://localhost:8080")
