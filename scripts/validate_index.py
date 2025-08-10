#!/usr/bin/env python3
"""Validate index references and anchors (MD + JSON anchors)."""
from __future__ import annotations

from pathlib import Path
import json

try:
    from scripts.lib_repo import repo_root, read_text
    from scripts.lib_md import extract_md_anchors
    from scripts.lib_index import resolve_json_anchor
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).resolve().parents[0]))
    from lib_repo import repo_root, read_text
    from lib_md import extract_md_anchors
    from lib_index import resolve_json_anchor


def main() -> int:
    root = repo_root(Path(__file__))
    idx = json.loads(read_text(root / "master-index.json"))
    all_ok = True

    for ref in idx.get("modules", []):
        path = ref.get("path", "")
        if not path:
            continue
        anchor = ""
        if "#" in path:
            path, anchor = path.split("#", 1)
        if ref.get("href"):
            anchor = ref.get("href", "").lstrip("#")

        file_path = root / path
        if not file_path.exists():
            print(f"[FAIL] Missing target file: {path}")
            all_ok = False
            continue

        if anchor:
            if file_path.suffix == ".json":
                data = json.loads(read_text(file_path))
                try:
                    _ = resolve_json_anchor(data, anchor)
                except Exception:
                    print(f"[FAIL] Missing JSON key: {path}#{anchor}")
                    all_ok = False
                else:
                    print(f"[ OK ] JSON anchor: {path}#{anchor}")
            else:
                md = read_text(file_path)
                anchors = extract_md_anchors(md)
                if anchor not in anchors:
                    print(f"[FAIL] Missing MD anchor: {path}#{anchor}")
                    all_ok = False
                else:
                    print(f"[ OK ] MD anchor: {path}#{anchor}")

    print("Summary:", "OK" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
