#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import lint_doc_links


class TestLintDocLinks(unittest.TestCase):
    def run_lint(self, anchor: str) -> int:
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".lint").mkdir()
            (root / "doc.md").write_text("# Ähnlich — aber anders\n", encoding="utf-8")
            cfg = {"critical": [{"file": "doc.md", "anchor": anchor}]}
            (root / ".lint" / "doc_anchors.json").write_text(
                json.dumps(cfg), encoding="utf-8"
            )
            orig_repo_root = lint_doc_links.repo_root
            try:
                lint_doc_links.repo_root = lambda start=None: root
                return lint_doc_links.main()
            finally:
                lint_doc_links.repo_root = orig_repo_root

    def test_slugified_anchor(self):
        rc = self.run_lint("ahnlich-aber-anders")
        self.assertEqual(rc, 0)

    def test_unslugified_anchor(self):
        rc = self.run_lint("Ähnlich — aber anders")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
