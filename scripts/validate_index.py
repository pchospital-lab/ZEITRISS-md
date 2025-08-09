#!/usr/bin/env python3
"""Validate paths and anchors referenced in master-index.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def resolve_json_anchor(obj: object, frag: str):
    """Resolve ``frag`` against ``obj`` supporting JSON Pointer and dot paths."""
    if frag.startswith("/"):
        cur = obj
        for seg in frag.strip("/").split("/"):
            seg = seg.replace("~1", "/").replace("~0", "~")
            if isinstance(cur, list):
                cur = cur[int(seg)]
            else:
                cur = cur[seg]
        return cur
    cur = obj
    for seg in frag.split("."):
        if seg.isdigit() and isinstance(cur, list):
            cur = cur[int(seg)]
        else:
            cur = cur[seg]
    return cur

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    index_path = repo_root / "master-index.json"
    with index_path.open(encoding="utf-8") as f:
        data = json.load(f)

    errors: list[str] = []
    modules = data.get("modules", [])
    for module in modules:
        module_path = module.get("path", "")
        anchor = None
        if "#" in module_path:
            module_path, anchor = module_path.split("#", 1)
        if module.get("href"):
            anchor = module["href"].lstrip("#")

        file_path = repo_root / module_path
        if not file_path.is_file():
            errors.append(
                f"Missing file: {module_path} (slug: {module.get('slug')})"
            )
            continue

        if anchor:
            if file_path.suffix == ".json":
                try:
                    json_data = json.loads(file_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    errors.append(
                        f"JSON parse error in {module_path}: {exc} (slug: {module.get('slug')})",
                    )
                else:
                    try:
                        resolve_json_anchor(json_data, anchor)
                    except Exception:
                        errors.append(
                            f"[FAIL] Missing JSON key: {module_path}#{anchor}",
                        )
            else:
                text = file_path.read_text(encoding="utf-8")
                if f"#{anchor}" not in text:
                    errors.append(
                        f"Missing anchor '#{anchor}' in {module_path} (slug: {module.get('slug')})",
                    )

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

