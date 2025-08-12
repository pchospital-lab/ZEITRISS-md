#!/usr/bin/env python3
from scripts.lint_hud_codex import warn_pattern, pattern


def test_warn_pattern_requires_closing_bracket():
    assert warn_pattern.search("[HUD:test]")
    assert warn_pattern.search("[HUD:test") is None


def test_warn_pattern_ignores_escaped_bracket():
    assert warn_pattern.search("\\[HUD:test]") is None


def test_pattern_specific_tags():
    assert pattern.search("[HUD:test]")
    assert pattern.search("[HUD:test") is None

