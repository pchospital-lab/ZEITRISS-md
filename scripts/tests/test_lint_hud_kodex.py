#!/usr/bin/env python3
from scripts.lint_hud_kodex import fence_hud_pattern, warn_pattern, pattern


def test_warn_pattern_requires_closing_bracket():
    assert warn_pattern.search("[HUD:test]")
    assert warn_pattern.search("[HUD:test") is None


def test_warn_pattern_ignores_escaped_bracket():
    assert warn_pattern.search("\\[HUD:test]") is None


def test_pattern_specific_tags():
    assert pattern.search("[HUD:test]")
    assert pattern.search("[HUD:test") is None


def test_fence_pattern_detects_legacy_hud_in_codeblock():
    md = """```text\n[HUD: Legacy]\n```"""
    assert fence_hud_pattern.search(md)


def test_fence_pattern_ignores_normal_inline_hud():
    md = "`HUD · Nullzeit-Puffer`"
    assert fence_hud_pattern.search(md) is None
