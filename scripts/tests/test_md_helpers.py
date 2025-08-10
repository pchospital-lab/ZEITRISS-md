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

    def test_extract_md_anchors(self):
        anchors = extract_md_anchors(MD)
        self.assertIn("custom-id", anchors)
        self.assertIn("makros-im-überblick", anchors)
        self.assertIn("würfelmechanik-regeln", anchors)
        self.assertIn("ähnlich-aber-anders", anchors)


if __name__ == "__main__":
    unittest.main()

