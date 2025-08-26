#!/usr/bin/env python3
import sys, unicodedata, pathlib

EXTS = {'.md', '.markdown', '.json', '.yml', '.yaml', '.txt'}
bad = []
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    if p.suffix.lower() not in EXTS:
        continue
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        bad.append(arg)
        continue
    if s != unicodedata.normalize('NFC', s):
        bad.append(arg)

if bad:
    print("Normalization required for:", *['- '+x for x in bad], sep='\n')
    print("\nRun: python3 tools/normalize.py  # fixes NFC normalization atomically")
    sys.exit(1)
