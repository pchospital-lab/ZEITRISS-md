#!/usr/bin/env python3
"""Lint German umlaut canonical forms in prose (ignores code blocks/links)."""
from __future__ import annotations

from pathlib import Path
import re

from scripts.lib_repo import repo_root, read_text
from scripts.lib_md import strip_front_matter

CANON = {
    "Heldenwuerfel": "Heldenwürfel",
    "Wuerfelmechanik": "Würfelmechanik",
    "Ueberblick": "Überblick",
}

URL = re.compile(r"https?://\S+")
INLINE_CODE = re.compile(r"`[^`]*`")


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks (``` or ~~~) from Markdown text."""
    lines: list[str] = []
    in_block = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if not in_block:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                in_block = True
            else:
                lines.append(line)
        else:
            if stripped.startswith(fence):
                in_block = False
    return "\n".join(lines)


def strip_inline_and_indent_code(text: str) -> str:
    """Remove inline ``code`` spans and 4-space indented blocks."""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("    ") or line.startswith("\t"):
            continue
        lines.append(INLINE_CODE.sub("", line))
    return "\n".join(lines)

def main() -> int:
    root = repo_root(Path(__file__))
    bad = []
    for p in root.rglob("*.md"):
        text = strip_front_matter(read_text(p))
        scrub = URL.sub("", strip_inline_and_indent_code(strip_code_blocks(text)))
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
