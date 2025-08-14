#!/usr/bin/env python3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import lint_umlauts


class TestLintUmlauts(unittest.TestCase):
    def run_lint(self, text: str) -> int:
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "doc.md").write_text(text, encoding="utf-8")
            orig_repo_root = lint_umlauts.repo_root
            try:
                lint_umlauts.repo_root = lambda start=None: root
                return lint_umlauts.main()
            finally:
                lint_umlauts.repo_root = orig_repo_root

    def test_ignored_in_code(self):
        md = "`Ueberblick`\n\n    Ueberblick\n"
        rc = self.run_lint(md)
        self.assertEqual(rc, 0)

    def test_detects_plain_text(self):
        md = "Ueberblick"
        rc = self.run_lint(md)
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
