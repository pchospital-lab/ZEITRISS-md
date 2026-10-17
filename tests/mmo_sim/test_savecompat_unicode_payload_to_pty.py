#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_unicode_payload_to_pty.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`unicode_payload_to_pty` (03_TERMINAL_UND_BILD.md,
`mmo_sim/ui/rendering.py` + `mmo_sim/ui/tui.py:TuiSession._print`).

Deckt die SL-Antwort->Adapter-content->TUI-Kette AM SELBEN Payload:
Codepoints (Emoji, FE0F-Variationsselektor, ZWJ, Umlaute, Wuerfel-/
Kampfzeichen, Listenpunkte, Markdown, Code-/Saveblock, lange Zeilen)
werden NICHT verloren; Codebloecke (inkl. Saveblock-JSON) werden NIEMALS
markdown-geparst/inhaltlich veraendert; gefaehrliche rohe Steuerzeichen
(insb. ESC) aus Modelltext werden ENTFERNT, bevor sie als Terminal-
Escape-Sequenz wirken koennten; der explizite ASCII-Fallback verliert
NICHTS STILL (jedes Nicht-ASCII-Zeichen bleibt als `[U+XXXX]` sichtbar
rekonstruierbar). Ergaenzend (Unterstuetzungsbeleg fuer
`terminal_rendering_and_capture`, deren echte PNG-Capture NICHT Teil
dieses Tests ist, s. REPORT): reines Renderer-Unit-Verhalten
(Markdown->ANSI ausserhalb von Codebloecken, Codeblock-Unversehrtheit).

Die TUI selbst wird NICHT als Subprozess/echtes PTY gestartet (keine
echte Terminalemulation in dieser Testebene) -- `TuiSession._print` ist
derselbe interne Aufrufpunkt, den JEDE reale `print_fn`-Ausgabe
durchlaeuft (s. `TuiSession.__init__`-Verdrahtung); die tatsaechliche
PNG-Capture im echten PTY ist Main/SK-POST-C."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui import rendering  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


# Echte ZEITRISS-typische Codepoints: Emoji+FE0F, ZWJ-Sequenz, Umlaute,
# Wuerfel-/Kampfzeichen, Listenpunkt, plus ein unveraenderter JSON-Saveblock.
UNICODE_PAYLOAD = (
    "Der Wuerfel faellt: \U0001F3B2️ Kritischer Erfolg!\n"
    "Team: \U0001F9D1‍\U0001F680 bereit.\n"
    "Großschaden an der Flügeltür, ein Zwischenfall führt zum Abbruch.\n"
    "• Punkt eins\n• Punkt zwei\n"
    "**fett** und _kursiv_ und `code`.\n"
    "```json\n{\"v\": 7, \"name\": \"Flo\", \"note\": \"⚔️ Kampf\"}\n```"
)


def _tui_with_capture(**kwargs):
    captured = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="participant-unicode-01", print_fn=captured.append, **kwargs,
        )
    return session, captured


if __name__ == "__main__":
    # ── 1) Unveraenderte Weiterleitung bis in die gerenderte Anzeige -- KEIN
    #      stiller Codepoint-Verlust (Standardmodus, kein ASCII-Fallback). ─────
    session, captured = _tui_with_capture()
    session._print(UNICODE_PAYLOAD)
    rendered = captured[0]
    check("dice_emoji_with_fe0f_preserved", "\U0001F3B2️" in rendered)
    check("zwj_sequence_preserved", "\U0001F9D1‍\U0001F680" in rendered)
    check("umlaut_text_preserved", "Großschaden an der Flügeltür" in rendered)
    check("list_bullet_preserved", "• Punkt eins" in rendered)
    check("sword_emoji_in_codeblock_preserved", "⚔️" in rendered)

    # ── 2) Codeblock (Saveblock-JSON) bleibt BYTEGLEICH -- KEIN Markdown-Parsing
    #      innerhalb des fenced Blocks (kein Bold/Italic-Ersatz im JSON-Inhalt).
    fence_start = rendered.index("```json")
    fence_body = rendered[fence_start:]
    check("codeblock_json_content_untouched", '"note": "⚔️ Kampf"' in fence_body)
    check("codeblock_json_has_no_ansi_bold_injected", "\x1b[1m" not in fence_body)

    # ── 3) Prosa AUSSERHALB des Codeblocks wird zu ANSI uebersetzt (Markdown
    #      verschwindet nicht als rohe Sternchen/Unterstriche auf dem Schirm). ─
    prose_part = rendered[:fence_start]
    check("bold_marker_translated_to_ansi_outside_codeblock", "\x1b[1mfett\x1b[0m" in prose_part)
    check("raw_double_asterisk_gone_outside_codeblock", "**fett**" not in prose_part)

    # ── 4) Sicherheit: eine rohe ESC-Sequenz aus "Modelltext" darf NIE
    #      unveraendert im gerenderten Ergebnis landen (kein SL-kontrolliertes
    #      Terminal-Escape). ───────────────────────────────────────────────────
    session2, captured2 = _tui_with_capture()
    malicious = "Normal \x1b[31mROT\x1b[0m Text"
    session2._print(malicious)
    check("raw_esc_byte_stripped_from_model_text", "\x1b" not in captured2[0])
    check("visible_text_around_stripped_escape_survives", "ROT" in captured2[0] and "Normal" in captured2[0])

    # ── 5) Expliziter ASCII-Fallback: JEDES Nicht-ASCII-Zeichen bleibt sichtbar
    #      als `[U+XXXX]` -- KEIN stilles Leerzeichen/keine stille Luecke. ─────
    session3, captured3 = _tui_with_capture(ascii_fallback=True)
    session3._print("Wuerfel \U0001F3B2 Ergebnis: üöä")
    fallback_out = captured3[0]
    check("ascii_fallback_replaces_dice_emoji_visibly", "[U+1F3B2]" in fallback_out)
    check("ascii_fallback_replaces_umlauts_visibly", "[U+00FC]" in fallback_out and "[U+00F6]" in fallback_out)
    check("ascii_fallback_output_is_pure_ascii", all(ord(c) < 128 for c in fallback_out))

    # ── 6) Reine Renderer-Unit-Pruefung (Unterstuetzungsbeleg fuer
    #      `terminal_rendering_and_capture`, s. Moduldocstring): leere/None-
    #      Eingabe wird ohne Crash zu einem leeren String. ─────────────────────
    check("renderer_handles_empty_text_without_crash", rendering.render_for_terminal("") == "")
    check("renderer_handles_none_like_falsy_without_crash", rendering.render_for_terminal(None) == "")

    # NEGATIV: Inline-Code (`` `...` ``) selbst wird NICHT als Bold/Italic
    # zweitinterpretiert.
    check(
        "inline_code_content_not_double_rendered_as_italic",
        "\x1b[3m" not in rendering.render_for_terminal("ein `_wort_` im Code"),
    )

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
