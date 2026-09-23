#!/usr/bin/env python3
"""
mmo_sim/core/completion_marker.py — Fence-Zustandsmaschine fuer maschinenlesbare
Abschluss-Marker in SL-Antworten.

Extrahiert aus `internal/qa/harness/lobby/section.py` (P1). Domaenenneutral:
der Marker-String selbst ist ein Parameter, keine Konstante — die Domaene
(ZEITRISS: "SECTION-ABSCHLUSS-BESTAETIGT") uebergibt ihn. Wird sowohl von der
QA-Fassade (section.py, unveraendert) als auch vom echten Runtime-Loop
(core/runtime.py) fuer dieselbe Aufgabe benutzt: ein Abschluss-Ereignis darf
nicht durch ein zitiertes/verschachteltes Beispiel im Fliesstext ausgeloest
werden.
"""
from __future__ import annotations

import re

_FENCE_DELIMITER_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_QUALIFIER_RE = re.compile(r"^(table_id|section_id)=(.*)$")


def _fence_delimiter(line: str) -> tuple[str, int, str] | None:
    m = _FENCE_DELIMITER_RE.match(line)
    if not m:
        return None
    run = m.group(1)
    return run[0], len(run), m.group(2)


def top_level_lines(text: str) -> list[str]:
    """Liefert die Zeilen von `text`, die NICHT innerhalb eines Fence-Blocks
    liegen — ein Marker-Token als String-Wert in einem Save oder in einem
    zitierten Beispielblock zaehlt so nicht als echtes Ereignis."""
    top_level: list[str] = []
    in_block = False
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        delim = _fence_delimiter(line)
        if not in_block:
            if delim is not None:
                fence_char, fence_len, _info = delim
                in_block = True
                continue
            top_level.append(line)
            continue
        if delim is not None:
            char, length, info = delim
            if char == fence_char and length >= fence_len and info.strip() == "":
                in_block = False
    return top_level


def completion_marker_matches(text: str, marker: str, table_id: str, section_id: str) -> bool:
    """Vollstaendige POSITIVE Ereignisgrammatik: `tokens[0]` muss exakt `marker`
    sein; jedes weitere Token muss ein gueltiger `table_id=`/`section_id=`
    Qualifier mit passendem Wert sein. Ein blanker Marker ohne Qualifier gilt
    fuer die aktuelle Session. ALLE Top-Level-Zeilen werden geprueft."""
    for line in top_level_lines(text):
        tokens = line.strip().split()
        if not tokens or tokens[0] != marker:
            continue
        valid = True
        for tok in tokens[1:]:
            m = _QUALIFIER_RE.match(tok)
            if not m:
                valid = False
                break
            key, value = m.group(1), m.group(2)
            expected = table_id if key == "table_id" else section_id
            if value != expected:
                valid = False
                break
        if valid:
            return True
    return False
