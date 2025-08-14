#!/usr/bin/env python3
"""Reusable lint helpers for script checks."""
from __future__ import annotations

import re


def ok(pat: str, msg: str, text: str) -> bool:
    """Print standard lint result for ``pat`` found in ``text``."""
    if not re.search(pat, text, re.S):
        print(f"[FAIL] {msg}")
        return False
    print(f"[ OK ] {msg}")
    return True


__all__ = ["ok"]
