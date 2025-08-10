#!/usr/bin/env python3
"""JSON anchor helpers: resolve JSON Pointer (#/a/b) and dot-paths (a.b.0.c)."""
from __future__ import annotations


def resolve_json_anchor(obj, frag: str):
    """Resolve `frag` within `obj`, supporting JSON Pointer and dot paths.

    Raises KeyError/IndexError on missing segments.
    """
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
