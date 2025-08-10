#!/usr/bin/env python3
"""Fail if signal actions lack hardware references.

Searches Markdown files for forbidden signal terms and ensures a device
(Comlink, Jammer, Terminal, etc.) is mentioned on the same line.
"""
from pathlib import Path

# Local import works both as script and module
try:
    from scripts.lib_repo import repo_root, read_text
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from lib_repo import repo_root, read_text

FORBIDDEN = [
    "Cyberspace",
    "Signalraum",
    "Netzgeist",
    "Netzwerkgeist",
    "reiner Signalfluss",
]
DEVICES = [
    "Comlink",
    "Jammer",
    "Terminal",
    "Konsole",
    "Kabel",
    "Antenne",
    "Funkgerät",
    "Relais",
]


def main() -> int:
    root = repo_root(Path(__file__))
    ok = True
    for path in root.rglob('*.md'):
        for i, line in enumerate(read_text(path).splitlines(), start=1):
            lowered = line.lower()
            stripped = line.lstrip().lower()
            if stripped.startswith('{% set forbidden') or stripped.startswith('{% set devices'):
                continue
            if any(f.lower() in lowered for f in FORBIDDEN):
                if "ohne" in lowered:
                    continue
                if not any(d.lower() in lowered for d in DEVICES):
                    print(f"{path}:{i}: signal action without hardware")
                    ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
