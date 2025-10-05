#!/usr/bin/env python3
"""Einfacher Link-Linter für Markdown-Dateien.

Der Linter prüft, ob lokale Links (Dateien, Bilder) existieren. Externe
HTTP(S)-, Mailto- und Anchor-Links werden übersprungen.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import urllib.parse
from dataclasses import dataclass
from typing import Iterable, Iterator, Mapping

INLINE_LINK_RE = re.compile(r"(!)?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"(!)?\[[^\]]*\]\[([^\]]+)\]")
REFERENCE_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(<[^>]+>|\S+)", re.MULTILINE)

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


@dataclass(frozen=True)
class LinkIssue:
    path: pathlib.Path
    line: int
    target: str
    message: str

    def format(self) -> str:
        rel_path = self.path.as_posix()
        return f"{rel_path}:{self.line}: {self.message} → {self.target}"


def iter_markdown_files(paths: Iterable[str]) -> Iterator[pathlib.Path]:
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            yield from sorted(path.rglob("*.md"))
        elif path.suffix.lower() in {".md", ".markdown"}:
            yield path
        else:
            continue


def parse_reference_definitions(text: str) -> Mapping[str, str]:
    refs: dict[str, str] = {}
    for match in REFERENCE_DEF_RE.finditer(text):
        label = match.group(1).strip().lower()
        target = match.group(2).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        refs[label] = target
    return refs


def should_skip(target: str) -> bool:
    if not target:
        return True
    lower = target.lower()
    return lower.startswith(SKIP_PREFIXES)


def normalise_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if "#" in target:
        target = target.split("#", 1)[0]
    target = target.strip()
    if not target:
        return target
    target = urllib.parse.unquote(target)
    return target


def resolve_path(base: pathlib.Path, target: str) -> pathlib.Path:
    # Normalisiere einfache ./ und ../ Sequenzen über Path.resolve
    return (base.parent / target).resolve()


def check_target(base: pathlib.Path, line_no: int, target: str) -> Iterator[LinkIssue]:
    target = normalise_target(target)
    if not target or should_skip(target):
        return
    # Daten-URIs oder Anker bereits entfernt. Falls immer noch Schema enthält, überspringen.
    if "://" in target and not target.startswith(("./", "../")):
        return
    candidate = resolve_path(base, target)
    if not candidate.exists():
        yield LinkIssue(path=base, line=line_no, target=target, message="Datei nicht gefunden")


def lint_file(path: pathlib.Path) -> list[LinkIssue]:
    text = path.read_text(encoding="utf-8")
    refs = parse_reference_definitions(text)
    issues: list[LinkIssue] = []

    for idx, line in enumerate(text.splitlines(), start=1):
        for match in INLINE_LINK_RE.finditer(line):
            target = match.group(2)
            issues.extend(check_target(path, idx, target) or [])
        for match in REFERENCE_LINK_RE.finditer(line):
            label = match.group(2).strip().lower()
            target = refs.get(label)
            if target is None:
                issues.append(
                    LinkIssue(
                        path=path,
                        line=idx,
                        target=label,
                        message="Referenzdefinition fehlt",
                    )
                )
                continue
            issues.extend(check_target(path, idx, target) or [])
    return issues


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Lint Markdown-Links auf lokale Dateien")
    parser.add_argument("paths", nargs="+", help="Dateien oder Verzeichnisse mit Markdown-Inhalten")
    args = parser.parse_args(argv)

    all_issues: list[LinkIssue] = []
    for md_file in iter_markdown_files(args.paths):
        all_issues.extend(lint_file(md_file))

    if all_issues:
        for issue in all_issues:
            print(issue.format())
        print(f"\n{len(all_issues)} Link-Fehler gefunden.", file=sys.stderr)
        return 1

    print("Alle geprüften Links verweisen auf existierende Dateien.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
