#!/usr/bin/env python3
"""Markdown helpers: strip front matter, slugify headings, extract anchors."""
from __future__ import annotations

import re
import unicodedata

_RE_FM = re.compile(r"^---\s*\n.*?\n---\s*(\n|$)", re.S)
_RE_HTML_ID = re.compile(r'<a\s+id="([^"]+)"', re.I)
_RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
_RE_HEADING_ID = re.compile(r"^(?P<title>.+?)\s*\{\s*#(?P<id>[-\w]+)\s*\}\s*$")


def strip_front_matter(text: str) -> str:
    """Remove leading YAML front matter (`---` block) from a Markdown string."""
    return _RE_FM.sub("", text, count=1)


def slugify(md_heading: str) -> str:
    """Convert a Markdown heading to a stable, ASCII-only anchor slug."""
    s = unicodedata.normalize("NFKD", md_heading)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s


def extract_md_anchors(text: str) -> set[str]:
    """Return all anchor IDs: explicit ``<a id="...">``, kramdown ``{#id}``, and slugs."""
    txt = strip_front_matter(text)
    anchors: set[str] = set()
    for html_id in _RE_HTML_ID.findall(txt):
        anchors.add(slugify(html_id))
    for _, head in _RE_HEADING.findall(txt):
        m = _RE_HEADING_ID.match(head)
        if m:
            anchors.add(slugify(m.group("id")))
            anchors.add(slugify(m.group("title")))
        else:
            anchors.add(slugify(head))
    return anchors
