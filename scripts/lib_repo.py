#!/usr/bin/env python3
"""Shared helpers for repo-aware scripts (root detection, IO)."""
from __future__ import annotations

from pathlib import Path
import subprocess


def repo_root(start: Path | None = None) -> Path:
    base = (start or Path(__file__).resolve())
    root = base.parents[1]
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return root


def read_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")
