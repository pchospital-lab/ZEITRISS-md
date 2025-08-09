#!/usr/bin/env python3
"""Fail on orphaned LINT: anchors (not covered by any lint script)."""
from __future__ import annotations

from pathlib import Path
import re


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    allow = set()
    allow_file = root / ".lint" / "anchors.allow"
    if allow_file.exists():
        allow = {
            ln.strip()
            for ln in allow_file.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        }

    # Alle LINT: Marker aus .md einsammeln
    repo_anchors = set()
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        repo_anchors |= set(re.findall(r"LINT:[A-Z0-9_\-]+", text))

    # Abdeckung in Lint-Skripten
    covered = set()
    for p in (root / "scripts").glob("lint_*.py"):
        t = p.read_text(encoding="utf-8")
        covered |= set(re.findall(r"LINT:[A-Z0-9_\-]+", t))

    orphans = sorted(a for a in repo_anchors if a not in covered and a not in allow)
    for a in orphans:
        print(f"[FAIL] Orphan LINT anchor: {a}")

    ok = len(orphans) == 0
    print("Summary:", "OK" if ok else f"FAIL ({len(orphans)} orphans)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
