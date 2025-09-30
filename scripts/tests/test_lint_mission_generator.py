import unittest

from scripts import lint_mission_generator


class TestLintMissionGenerator(unittest.TestCase):
    def test_repo_data_passes_lint(self) -> None:
        rc = lint_mission_generator.main()
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
