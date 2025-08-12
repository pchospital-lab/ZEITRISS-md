#!/usr/bin/env python3
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib_repo import repo_root


class TestRepoRoot(unittest.TestCase):
    def setUp(self):
        self.base = Path(__file__)
        self.expected = self.base.resolve().parents[1]

    def test_called_process_error_fallback(self):
        with patch(
            "scripts.lib_repo.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git"),
        ), self.assertLogs("lib_repo", "WARNING") as cm:
            root = repo_root(self.base)
        self.assertEqual(root, self.expected)
        self.assertTrue(
            any("git rev-parse failed" in msg.lower() for msg in cm.output)
        )

    def test_file_not_found_error_fallback(self):
        with patch(
            "scripts.lib_repo.subprocess.run",
            side_effect=FileNotFoundError("git"),
        ), self.assertLogs("lib_repo", "WARNING") as cm:
            root = repo_root(self.base)
        self.assertEqual(root, self.expected)
        self.assertTrue(
            any("git rev-parse failed" in msg.lower() for msg in cm.output)
        )


if __name__ == "__main__":
    unittest.main()
