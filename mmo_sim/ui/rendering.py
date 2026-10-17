#!/usr/bin/env python3
"""
mmo_sim/ui/rendering.py — minimaler Terminal-Renderer für bereits
vorhandene Produktanzeige (ZR-SAVECOMPAT-TERMINAL-20261016-R1,
03_TERMINAL_UND_BILD.md).

Reine, zustandslose Funktion auf einem bereits erhaltenen Textstring --
KEINE neue UI-Plattform, KEIN Browser-CSS/HTML, KEINE Protokoll-/
Speicheränderung (der an `print_fn`/`_print` übergebene String wird NUR
für die TERMINALANZEIGE umgeformt; `sl_log`/`onboarding`/Save-Dateien
sehen weiterhin den unveränderten Rohtext, s. `ui/tui.py:TuiSession.
__init__`-Verdrahtung).

Zwei getrennte Schutzziele (03: "Reine Unicode-Erhaltung, Zeilenumbruch/
Spaltenbreite und tatsaechlich sichtbare Glyphen getrennt protokollieren"):

  1. Sicherheit: rohe C0-Steuerzeichen (insb. ESC/`\\x1b`, das Terminal-
     Escape-Sequenzen einleitet) werden aus Modelltext ENTFERNT, BEVOR
     irgendeine eigene ANSI-Sequenz dieses Moduls angehängt wird -- ein
     SL-Text kann dadurch NIE eigene Escape-Sequenzen ausführen
     (03: "Terminal-Steuerzeichen nicht ungefiltert aus Modelltext
     ausführen").
  2. Darstellung: ein winziges Markdown-Subset (`**fett**`, `_kursiv_`,
     `` `code` ``) wird in ANSI-Sequenzen übersetzt, DAMIT es nicht als
     rohe Sternchen/Unterstriche auf dem Bildschirm landet. Fenced
     ```-Codeblöcke (inkl. Saveblöcke) werden NIEMALS inhaltlich
     verändert oder markdown-geparst -- nur als Block erkannt und
     unverändert durchgereicht (03: "ohne Protokolle/gespeicherte Texte
     zu verändern").

`ascii_fallback=True` ersetzt jedes Nicht-ASCII-Codepoint durch eine
SICHTBARE `[U+XXXX]`-Notation (NIE eine stille Lücke/Leerzeichen) -- 03:
"Expliziter ASCII-Fallback bleibt wählbar, kein stiller Datenverlust"."""
from __future__ import annotations

import re

#: C0-Steuerzeichen ausser Tab/Newline (CR wird ebenfalls entfernt -- ein
#: rohes '\r' kann auf manchen Terminals die aktuelle Zeile ueberschreiben,
#: dasselbe Risiko wie ESC). DEL (0x7f) zaehlt nicht zu C0, wird aber aus
#: demselben Grund (kein sichtbares Glyph, potenziell verwirrend) mit
#: entfernt.
_DANGEROUS_CONTROL_RE = re.compile(
    "[" + "".join(chr(c) for c in range(0x00, 0x20) if c not in (0x09, 0x0A)) + "\x7f]"
)

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_BOLD_RE = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
_ITALIC_RE = re.compile(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])")
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")

_ANSI_BOLD = ("\x1b[1m", "\x1b[0m")
_ANSI_ITALIC = ("\x1b[3m", "\x1b[0m")
_ANSI_DIM = ("\x1b[2m", "\x1b[0m")


def strip_dangerous_control_chars(text: str) -> str:
    """Entfernt rohe C0-Steuerzeichen (ausser Tab/Newline) + DEL aus
    `text` -- insbesondere ESC (`\\x1b`), das jede nachfolgende Sequenz
    als Teil EINER Escape-Sequenz umdeuten könnte. Reine Sicherheitsstufe,
    unabhängig von Markdown/ASCII-Fallback -- wird in `render_for_
    terminal` IMMER zuerst angewendet, auch wenn der Aufrufer keine
    Markdown-Übersetzung möchte."""
    return _DANGEROUS_CONTROL_RE.sub("", text)


def _render_prose(segment: str) -> str:
    """Markdown-Subset -> ANSI, NUR für Text AUSSERHALB fenced
    Codeblöcke (s. `render_for_terminal`). Reihenfolge wichtig: Inline-
    Code zuerst (sein Inhalt bleibt roh, KEIN Bold/Italic darin), dann
    Bold, dann Italic (verhindert, dass ein einzelnes `_` innerhalb eines
    bereits erkannten `**...**`-Bolds erneut als Italic-Marker gelesen
    wird, da `_BOLD_RE` bereits ersetzt hat)."""
    segment = _INLINE_CODE_RE.sub(lambda m: f"{_ANSI_DIM[0]}{m.group(1)}{_ANSI_DIM[1]}", segment)
    segment = _BOLD_RE.sub(lambda m: f"{_ANSI_BOLD[0]}{m.group(1)}{_ANSI_BOLD[1]}", segment)
    segment = _ITALIC_RE.sub(lambda m: f"{_ANSI_ITALIC[0]}{m.group(1)}{_ANSI_ITALIC[1]}", segment)
    return segment


def _ascii_fallback_transform(text: str) -> str:
    """Ersetzt JEDES Nicht-ASCII-Zeichen durch `[U+XXXX]` -- sichtbar,
    verlustfrei rekonstruierbar, NIE ein stilles Leerzeichen/eine stille
    Lücke (03: "kein stiller Datenverlust in der gespeicherten Quelle" --
    diese Funktion läuft NUR auf der Anzeigekopie, s. Moduldocstring)."""
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append(f"[U+{ord(ch):04X}]")
    return "".join(out)


def render_for_terminal(text: str, *, ascii_fallback: bool = False) -> str:
    """Einziger öffentlicher Einstiegspunkt. Reihenfolge:
      1. gefährliche Steuerzeichen entfernen (immer, unabhängig von
         `ascii_fallback`).
      2. Text an fenced ```-Blöcken aufteilen; NUR die Nicht-Code-
         Segmente bekommen die Markdown->ANSI-Übersetzung, Codeblöcke
         bleiben inhaltlich unverändert (03: Saveblöcke/Codeblöcke nicht
         markdown-parsen).
      3. falls `ascii_fallback`: jedes Nicht-ASCII-Zeichen im GESAMTEN
         Ergebnis (Prosa UND Codeblöcke) sichtbar durch `[U+XXXX]`
         ersetzen.

    Leere/None-ähnliche Eingaben werden unverändert als leerer String
    behandelt; kein Werfen für normale leere Statuszeilen."""
    if not text:
        return text or ""
    safe = strip_dangerous_control_chars(text)

    pieces = []
    last = 0
    for m in _FENCE_RE.finditer(safe):
        pieces.append(_render_prose(safe[last:m.start()]))
        pieces.append(m.group(0))  # Codeblock unveraendert, kein Markdown-Parsing.
        last = m.end()
    pieces.append(_render_prose(safe[last:]))
    rendered = "".join(pieces)

    if ascii_fallback:
        rendered = _ascii_fallback_transform(rendered)
    return rendered
