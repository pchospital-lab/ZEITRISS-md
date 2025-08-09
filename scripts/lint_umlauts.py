#!/usr/bin/env python3
"""Lint German umlaut canonical forms in prose (ignores code blocks/links)."""
from __future__ import annotations

from pathlib import Path
import re

CANON = {
    "Heldenwuerfel": "Heldenwürfel",
    "Wuerfelmechanik": "Würfelmechanik",
    "Ueberblick": "Überblick",
}

CBLOCK = re.compile(r"```.*?```", re.S)
URL = re.compile(r"https?://\S+")

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    bad = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        scrub = URL.sub("", CBLOCK.sub("", text))
        for wrong, right in CANON.items():
            for i, line in enumerate(scrub.splitlines(), 1):
                if wrong in line:
                    bad.append((str(p), i, wrong, right))
    if bad:
        for f, ln, w, r in bad:
            print(f"[FAIL] {f}:{ln} → '{w}' → '{r}'")
        print(f"Summary: FAIL ({len(bad)} occurrences)")
        return 1
    print("Summary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
