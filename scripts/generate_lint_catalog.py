#!/usr/bin/env python3
"""Generate a catalog of LINT anchors used in markdown files."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out = root / "docs" / "LINT-CATALOG.md"
    entries: list[tuple[str, str]] = []
    for p in root.rglob("*.md"):
        if p.name == "LINT-CATALOG.md" and p.parent.name == "docs":
            continue
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r"LINT:[A-Z0-9_\-]+", text):
            entries.append((str(PurePosixPath(p.relative_to(root))), m.group(0)))
    entries.sort()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "# LINT Anchors\n\n" +
        "\n".join(f"- `{a}` — {f}" for f, a in entries),
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
