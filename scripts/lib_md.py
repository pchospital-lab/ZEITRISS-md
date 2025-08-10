#!/usr/bin/env python3
"""Markdown utilities: front matter strip, anchor extraction & slugify."""
from __future__ import annotations

import re

_RE_FM = re.compile(r"^---\s*\n.*?\n---\s*(\n|$)", re.S)
_RE_HTML_ID = re.compile(r'<a\s+id="([^"]+)"', re.I)
_RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
_RE_HEADING_ID = re.compile(r"\s*\{#([^}]+)\}\s*$")


def strip_front_matter(text: str) -> str:
    return _RE_FM.sub("", text, count=1)


def slugify(md_heading: str) -> str:
    s = md_heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s


def extract_md_anchors(text: str) -> set[str]:
    txt = strip_front_matter(text)
    anchors: set[str] = set()
    anchors |= set(_RE_HTML_ID.findall(txt))
    for _, title in _RE_HEADING.findall(txt):
        m = _RE_HEADING_ID.search(title)
        if m:
            anchors.add(m.group(1))
        else:
            anchors.add(slugify(title))
    return anchors
