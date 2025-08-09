#!/usr/bin/env python3
"""Check that every LINT anchor in markdown is referenced by at least one linter."""
from __future__ import annotations

from pathlib import Path
import re


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    anchors: dict[str, list[str]] = {}
    for p in root.rglob("*.md"):
        if p.name == "LINT-CATALOG.md" and p.parent.name == "docs":
            continue
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r"LINT:[A-Z0-9_\-]+", text):
            anchors.setdefault(m.group(0), []).append(str(p.relative_to(root)))
    used: set[str] = set()
    for p in (root / "scripts").glob("lint_*.py"):
        used.update(re.findall(r"LINT:[A-Z0-9_\-]+", p.read_text(encoding="utf-8")))
    ok = True
    for anchor, files in sorted(anchors.items()):
        if anchor not in used:
            for f in files:
                print(f"[WARN] Orphan LINT anchor {anchor} in {f}")
            ok = False
    if ok:
        print("All LINT anchors are referenced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
