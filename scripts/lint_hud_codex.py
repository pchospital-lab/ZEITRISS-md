#!/usr/bin/env python3
"""Fail if legacy bracket overlays are present.

Ensures all HUD overlays use the InlineHUD style with backticks.
"""
import pathlib
import re
import sys

pattern = re.compile(r"\[(HUD|INFO|TIP|TIPP|Paradox|PX|PRESSURE|ALERT|Codex)\s*:")
warn_pattern = re.compile(r"\[[A-Z][A-Za-z0-9_-]{1,12}\s*:")


def main() -> None:
    ok = True
    for path in pathlib.Path('.').rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for match in warn_pattern.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            if pattern.fullmatch(match.group(0)):
                print(f"{path}:{line}: legacy bracket tag")
                ok = False
            else:
                print(f"{path}:{line}: bracket tag (warn)")
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
