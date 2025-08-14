#!/usr/bin/env python3
import unittest

from scripts.lib_index import resolve_json_anchor

DATA = {
    "a": {"b": [{"c": 42}, {"c": 7}], "d": {"e/f": "x", "g~h": "y"}}
}


class TestJsonAnchor(unittest.TestCase):
    def test_dot_simple(self):
        self.assertEqual(resolve_json_anchor(DATA, "a.b.0.c"), 42)

    def test_dot_nested(self):
        self.assertEqual(resolve_json_anchor(DATA, "a.d"), {"e/f": "x", "g~h": "y"})

    def test_pointer_simple(self):
        self.assertEqual(resolve_json_anchor(DATA, "/a/b/1/c"), 7)

    def test_pointer_escapes(self):
        self.assertEqual(resolve_json_anchor(DATA, "/a/d/e~1f"), "x")
        self.assertEqual(resolve_json_anchor(DATA, "/a/d/g~0h"), "y")

    def test_empty_fragment(self):
        self.assertEqual(resolve_json_anchor(DATA, ""), DATA)

    def test_invalid_key_raises(self):
        with self.assertRaises(KeyError):
            resolve_json_anchor(DATA, "a.x")
        with self.assertRaises(KeyError):
            resolve_json_anchor(DATA, "/a/x")

    def test_invalid_index_raises(self):
        with self.assertRaises(IndexError):
            resolve_json_anchor(DATA, "a.b.99.c")
        with self.assertRaises(IndexError):
            resolve_json_anchor(DATA, "/a/b/99/c")


if __name__ == "__main__":
    unittest.main()
