#!/usr/bin/env python3
"""Check critical doc anchors exist and are referenced correctly."""
from __future__ import annotations

from pathlib import Path
import json

from scripts.lib_repo import repo_root, read_text
from scripts.lib_md import extract_md_anchors


def main() -> int:
    root = repo_root(Path(__file__))
    cfgp = root / ".lint" / "doc_anchors.json"
    if not cfgp.exists():
        print("[SKIP] No .lint/doc_anchors.json found")
        return 0
    cfg = json.loads(read_text(cfgp))
    items = cfg.get("critical", [])
    ok = True
    for item in items:
        rel = item["file"]
        aid = item["anchor"]
        p = root / rel
        if not p.exists():
            print(f"[FAIL] Target missing: {rel}")
            ok = False
            continue
        anchors = extract_md_anchors(read_text(p))
        if aid in anchors:
            print(f"[ OK ] {rel}#{aid}")
        else:
            print(f"[FAIL] Missing anchor: {rel}#{aid}")
            ok = False
    print("Summary:", "OK" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
