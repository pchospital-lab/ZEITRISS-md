#!/usr/bin/env python3
"""Check critical doc anchors exist and are referenced correctly."""
from __future__ import annotations

from pathlib import Path

CRITICAL = [
    ("characters/cyberware-und-bioware.md", "optional-hominin-bio-sheaths"),
    ("systems/gameflow/speicher-fortsetzung.md", "makros-im-ueberblick"),
]

def has_anchor(text: str, anchor: str) -> bool:
    return f'id="{anchor}"' in text or f'{{#{anchor}}}' in text

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ok = True
    for target, aid in CRITICAL:
        p = root / target
        if not p.exists():
            print(f"[FAIL] Target not found: {target}")
            ok = False
            continue
        t = p.read_text(encoding="utf-8")
        if not has_anchor(t, aid):
            print(f"[FAIL] Missing anchor in {target}: {aid}")
            ok = False
        else:
            print(f"[ OK ] Anchor present in {target}: {aid}")
    print("Summary:", "OK" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
