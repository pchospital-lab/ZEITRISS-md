#!/usr/bin/env python3
"""Fail if legacy bracket overlays are present.

Ensures all HUD overlays use the InlineHUD style with backticks.
"""
from pathlib import Path
import re

from scripts.lib_repo import repo_root, read_text

pattern = re.compile(
    r"(?<!\\)\[(HUD|INFO|TIP|TIPP|Paradoxon|PX|PRESSURE|ALERT|Kodex)\s*:[^\]]*\]"
)
warn_pattern = re.compile(
    r"(?<!\\)\[[A-Z][A-Za-z0-9_-]{1,12}\s*:[^\]]*\]"
)
dollar_pattern = re.compile(r"\$[^$]+\$")

whitelist = [
    re.compile(r"\[Exploding [^\]]+\]"),
    re.compile(r"☆"),
    re.compile(r"[👾💀🌀]"),
]


def is_whitelisted(text: str) -> bool:
    return any(w.search(text) for w in whitelist)


def main() -> int:
    root = repo_root(Path(__file__))
    ok = True
    for path in root.rglob('*.md'):
        text = read_text(path)
        for match in warn_pattern.finditer(text):
            if is_whitelisted(match.group(0)):
                continue
            line = text.count('\n', 0, match.start()) + 1
            if pattern.fullmatch(match.group(0)):
                print(f"{path}:{line}: legacy bracket tag")
                ok = False
            else:
                print(f"{path}:{line}: bracket tag (warn)")

        for match in dollar_pattern.finditer(text):
            if is_whitelisted(match.group(0)):
                continue
            line = text.count('\n', 0, match.start()) + 1
            print(f"{path}:{line}: dollar wrapper (warn)")
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
