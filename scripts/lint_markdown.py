#!/usr/bin/env python3
"""Lightweight Markdown lint covering ZEITRISS line-length rules."""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path


def parse_line_length(config_path: Path | None) -> int:
    """Extract the configured line length (defaults to 100)."""
    limit = 100
    if not config_path or not config_path.exists():
        return limit
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("line_length:"):
            try:
                limit = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
            break
    return limit


def iter_files(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for hit in glob.glob(pattern, recursive=True):
            path = Path(hit)
            if path.is_file() and path.suffix.lower() == ".md" and path not in seen:
                files.append(path)
                seen.add(path)
    return files


def check_file(path: Path, limit: int) -> list[str]:
    errors: list[str] = []
    in_code_block = False
    in_front_matter = False
    fence_marker: str | None = None
    for idx, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if idx == 1 and stripped == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if stripped == "---":
                in_front_matter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_code_block:
                in_code_block = True
                fence_marker = marker
                continue
            if in_code_block and marker == fence_marker:
                in_code_block = False
                fence_marker = None
                continue
        if in_code_block:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("|"):
            continue
        if len(line) > limit:
            errors.append(f"{path}:{idx}: MD013 Line exceeds {limit} characters")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Markdown files for ZEITRISS rules")
    parser.add_argument("patterns", nargs="+", help="Glob patterns to lint")
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help="Optional markdownlint config"
    )
    args = parser.parse_args()

    limit = parse_line_length(args.config)
    files = iter_files(args.patterns)
    errors: list[str] = []
    for path in files:
        errors.extend(check_file(path, limit))
    if errors:
        for entry in errors:
            print(entry)
        print(f"Found {len(errors)} markdown issues.", file=sys.stderr)
        return 1
    print(f"Markdown lint passed for {len(files)} file(s) with limit {limit} characters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
