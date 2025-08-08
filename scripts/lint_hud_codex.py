#!/usr/bin/env python3
"""Fail if legacy `[HUD:` tags are present.

Ensures all HUD overlays use the InlineHUD style with backticks.
"""
import pathlib
import re
import sys

pattern = re.compile(r"\[HUD:")


def main() -> None:
    ok = True
    for path in pathlib.Path('.').rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for match in pattern.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            print(f"{path}:{line}: legacy HUD tag")
            ok = False
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
