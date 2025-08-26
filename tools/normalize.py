#!/usr/bin/env python3
import sys, unicodedata, pathlib, os

EXTS = {'.md', '.markdown', '.json', '.yml', '.yaml', '.txt'}


def norm_file(p: pathlib.Path):
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        return False
    n = unicodedata.normalize('NFC', s)
    if s == n:
        return False
    tmp = p.with_suffix(p.suffix + '.tmpnorm')
    tmp.write_text(n, encoding='utf-8')
    os.replace(tmp, p)
    return True


root = pathlib.Path('.')
changed = 0
for p in root.rglob('*'):
    if p.is_file() and p.suffix.lower() in EXTS:
        changed += norm_file(p) or 0

print(f"Normalized {changed} file(s).")
