#!/usr/bin/env python3
"""Lint German umlaut canonical forms in prose (ignores code blocks/links)."""
from __future__ import annotations

from pathlib import Path
import re

try:
    from scripts.lib_repo import repo_root, read_text
    from scripts.lib_md import strip_front_matter
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from lib_repo import repo_root, read_text
    from lib_md import strip_front_matter

CANON = {
    "Heldenwuerfel": "Heldenwürfel",
    "Wuerfelmechanik": "Würfelmechanik",
    "Ueberblick": "Überblick",
}

CBLOCK = re.compile(r"```.*?```", re.S)
URL = re.compile(r"https?://\S+")

def main() -> int:
    root = repo_root(Path(__file__))
    bad = []
    for p in root.rglob("*.md"):
        text = strip_front_matter(read_text(p))
        scrub = URL.sub("", CBLOCK.sub("", text))
        for wrong, right in CANON.items():
            for i, line in enumerate(scrub.splitlines(), 1):
                if wrong in line:
                    bad.append((str(p.relative_to(root)), i, wrong, right))
    if bad:
        for f, ln, w, r in bad:
            print(f"[FAIL] {f}:{ln} → '{w}' → '{r}'")
        print(f"Summary: FAIL ({len(bad)} occurrences)")
        return 1
    print("Summary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
