#!/usr/bin/env python3
import unittest
from pathlib import Path

from scripts.lib_md import strip_front_matter, slugify, extract_md_anchors

FM = """---
title: "Foo"
tags: [bar]
---
# Überschrift
"""

MD = """
<a id="custom-id"></a>
## Makros im Überblick
### Würfelmechanik & Regeln!
Text.

#### Ähnlich — aber anders
"""


class TestMdHelpers(unittest.TestCase):
    def test_strip_front_matter(self):
        out = strip_front_matter(FM)
        self.assertNotIn("title:", out)
        self.assertIn("# Überschrift", out)

    def test_slugify(self):
        self.assertEqual(slugify("Makros im Überblick"), "makros-im-überblick")
        self.assertEqual(slugify("Würfelmechanik & Regeln!"), "würfelmechanik-regeln")
        self.assertEqual(slugify("Über  viele   Räume"), "über-viele-räume")

    def test_extract_md_anchors(self):
        anchors = extract_md_anchors(MD)
        self.assertIn("custom-id", anchors)
        self.assertIn("makros-im-überblick", anchors)
        self.assertIn("würfelmechanik-regeln", anchors)
        self.assertIn("ähnlich-aber-anders", anchors)

    def test_heading_with_kramdown_id_and_slug(self):
        md = "## Titel mit ID {#custom-id}\n"
        anchors = extract_md_anchors(md)
        self.assertIn("custom-id", anchors)
        self.assertIn("titel-mit-id", anchors)

    def test_heading_with_punct_and_umlaut(self):
        md = "### Würfelmechanik & Regeln! (v2)\n"
        anchors = extract_md_anchors(md)
        self.assertIn("würfelmechanik-regeln-v2", anchors)

    def test_front_matter_is_ignored(self):
        fm = "---\ntitle: 'Foo'\n---\n## Sichtbar\n"
        anchors = extract_md_anchors(fm)
        self.assertIn("sichtbar", anchors)


if __name__ == "__main__":
    unittest.main()
