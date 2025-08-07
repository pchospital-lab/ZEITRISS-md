#!/usr/bin/env python3
import pathlib, re, sys

pattern = re.compile(r"\[HUD\](?!:)")

def main():
    ok = True
    for path in pathlib.Path('.').rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for match in pattern.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            print(f"{path}:{line}: non-canonical HUD tag")
            ok = False
    if not ok:
        sys.exit(1)

if __name__ == '__main__':
    main()
