#!/usr/bin/env python3
"""Validate index references and anchors (MD + JSON anchors)."""
from __future__ import annotations

from pathlib import Path
import json

from scripts.lib_repo import repo_root, read_text, get_logger
from scripts.lib_md import extract_md_anchors
from scripts.lib_index import resolve_json_anchor

log = get_logger("validate_index")


def main() -> int:
    root = repo_root(Path(__file__))
    idx = json.loads(read_text(root / "master-index.json"))
    ok = True

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
            log.error("Missing target file: %s", path)
            ok = False
            continue

        if anchor:
            if file_path.suffix == ".json":
                try:
                    _ = resolve_json_anchor(json.loads(read_text(file_path)), anchor)
                    log.info("JSON anchor OK: %s#%s", path, anchor)
                except Exception:
                    log.error("Missing JSON key: %s#%s", path, anchor)
                    ok = False
            else:
                anchors = extract_md_anchors(read_text(file_path))
                if anchor in anchors:
                    log.info("MD anchor OK: %s#%s", path, anchor)
                else:
                    log.error("Missing MD anchor: %s#%s", path, anchor)
                    ok = False

    log.log(25, "Summary: %s", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
