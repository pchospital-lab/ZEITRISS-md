#!/usr/bin/env python3
"""JSON anchor helpers (pointer and dot-path)."""
from __future__ import annotations


def resolve_json_anchor(obj, frag: str):
    if frag.startswith("/"):
        cur = obj
        for seg in frag.strip("/").split("/"):
            seg = seg.replace("~1", "/").replace("~0", "~")
            cur = cur[int(seg)] if isinstance(cur, list) else cur[seg]
        return cur
    cur = obj
    for seg in frag.split("."):
        if seg.isdigit() and isinstance(cur, list):
            cur = cur[int(seg)]
        else:
            cur = cur[seg]
    return cur
