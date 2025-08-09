#!/usr/bin/env python3
"""Fail if signal actions lack hardware references.

Searches Markdown files for forbidden signal terms and ensures a device
(Comlink, Jammer, Terminal, etc.) is mentioned on the same line.
"""
import pathlib
import sys

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


def main() -> None:
    ok = True
    for path in pathlib.Path('.').rglob('*.md'):
        for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
            lowered = line.lower()
            if any(f.lower() in lowered for f in FORBIDDEN):
                if "ohne" in lowered:
                    continue
                if not any(d.lower() in lowered for d in DEVICES):
                    print(f"{path}:{i}: signal action without hardware")
                    ok = False
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
