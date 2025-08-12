#!/usr/bin/env python3
"""Repo helpers: root detection, safe text IO, and logging setup."""
from __future__ import annotations

from pathlib import Path
import subprocess, logging, os


def repo_root(start: Path | None = None) -> Path:
    """Return repository root from a starting path.

    Falls back to the parent directory even for very shallow paths where two
    parents are not available.
    """
    base = (start or Path(__file__).resolve()).resolve()
    root = base if base.is_dir() else base.parent
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return Path(out) if out else root
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        get_logger("lib_repo").warning("git rev-parse failed: %s", exc)
        return root


def read_text(path: Path) -> str:
    """Read UTF-8 text from ``path``.

    Raises ``FileNotFoundError`` with the absolute path if the file is missing
    and wraps ``UnicodeDecodeError`` to include the path when decoding fails.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing file: {p}")
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding,
            exc.object,
            exc.start,
            exc.end,
            f"{exc.reason} in file {p}",
        ) from exc


def get_logger(name: str) -> logging.Logger:
    """Create/get a repo-style logger (level from SMOKE_LOG_LEVEL, default INFO)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = os.getenv("SMOKE_LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level, logging.INFO))
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
    return logger
