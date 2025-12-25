#!/usr/bin/env python3
"""Lint für Missions-Generator-Pools und Rift-Seeds."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

# Import über Modulpfad; auf Direktaufruf mit Fallback reagieren
try:  # pragma: no cover - Laufzeit-Fallback
    from scripts.lib_repo import repo_root, read_text, get_logger
except ImportError:  # pragma: no cover
    import sys
    _ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(_ROOT))
    from scripts.lib_repo import repo_root, read_text, get_logger  # type: ignore

log = get_logger("lint_mission_generator")

SEED_DOC = Path("gameplay") / "kreative-generatoren-missionen.md"
_EXPECTED_RIFT_RANGE = range(1, 25)


def _find_code_block(text: str, fence: str, marker: str) -> str | None:
    pattern = re.compile(rf"```{fence}\r?\n(.*?)\r?\n```", re.S)
    for match in pattern.finditer(text):
        block = match.group(1)
        if marker in block:
            return block
    return None


def _collect_seed_entries(block: str, prefix: str) -> list[tuple[str, str | None, str | None]]:
    id_pattern = re.compile(rf'\s*-\s*id:\s*"({prefix}-\d+)"')
    matches = list(id_pattern.finditer(block))
    entries: list[tuple[str, str | None, str | None]] = []
    for idx, match in enumerate(matches):
        entry_id = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
        body = block[start:end]
        objective_match = re.search(r'objective:\s*"([^"\n]+)"', body)
        twist_match = re.search(r'twist:\s*"([^"\n]+)"', body)
        entries.append(
            (
                entry_id,
                objective_match.group(1) if objective_match else None,
                twist_match.group(1) if twist_match else None,
            )
        )
    return entries


def _slice_pool(block: str, start_marker: str, end_marker: str | None) -> str:
    start_idx = block.find(start_marker)
    if start_idx == -1:
        return ""
    start_idx += len(start_marker)
    end_idx = block.find(end_marker, start_idx) if end_marker else -1
    if end_idx == -1:
        end_idx = len(block)
    return block[start_idx:end_idx]


def _check_seed_pool(block: str, prefix: str, label: str) -> int:
    fails = 0
    entries = _collect_seed_entries(block, prefix)
    ids = [entry[0] for entry in entries]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        fails += 1
        log.error("[FAIL] %s: doppelte IDs %s", label, ", ".join(sorted(duplicates)))
    else:
        log.info("[ OK ] %s: eindeutige IDs (%d)", label, len(ids))
    for ident, objective, twist in entries:
        if objective is None or twist is None:
            fails += 1
            log.error(
                "[FAIL] %s: Eintrag %s ohne objective/twist", label, ident
            )
            continue
        if objective.strip() == twist.strip():
            fails += 1
            log.error(
                "[FAIL] %s: objective == twist bei %s", label, ident
            )
    return fails


def _check_rift_table(text: str) -> int:
    fails = 0
    block = _find_code_block(text, "json", "RiftSeedTable")
    if block is None:
        log.error("[FAIL] RiftSeedTable nicht gefunden")
        return 1
    try:
        data = json.loads(block)
    except json.JSONDecodeError as exc:
        log.error("[FAIL] RiftSeedTable JSON fehlerhaft: %s", exc)
        return 1
    seeds = data.get("RiftSeedTable", [])
    numbers = [entry.get("d24") for entry in seeds if isinstance(entry, dict)]
    if len(seeds) != len(numbers):
        fails += 1
        log.error("[FAIL] RiftSeedTable enthält Einträge ohne d24")
    duplicates = [item for item, count in Counter(numbers).items() if count > 1]
    if duplicates:
        fails += 1
        log.error("[FAIL] RiftSeedTable doppelte d24: %s", ", ".join(map(str, duplicates)))
    missing = sorted(set(_EXPECTED_RIFT_RANGE) - set(numbers))
    extra = sorted(set(numbers) - set(_EXPECTED_RIFT_RANGE))
    if missing:
        fails += 1
        log.error("[FAIL] RiftSeedTable fehlt Würfelwert(e): %s", ", ".join(map(str, missing)))
    if extra:
        fails += 1
        log.error("[FAIL] RiftSeedTable unerwartete Würfelwert(e): %s", ", ".join(map(str, extra)))
    if not fails:
        log.info("[ OK ] RiftSeedTable deckt d24 (1-24) vollständig ab")
    return fails


def _check_twist_ids(text: str) -> int:
    block = _find_code_block(text, "jsonc", "\"twists\"")
    if block is None:
        return 0
    cleaned = re.sub(r"//.*", "", block)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        log.error("[FAIL] Twist-JSON ungültig: %s", exc)
        return 1
    twists = data.get("twists", [])
    ids = [twist.get("id") for twist in twists if isinstance(twist, dict)]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        duplicate_labels = ", ".join(sorted(filter(None, duplicates)))
        log.error("[FAIL] Twist-IDs doppelt vergeben: %s", duplicate_labels)
        return 1
    log.info("[ OK ] Twist-Pool IDs eindeutig (%d)", len(ids))
    return 0


def main() -> int:
    root = repo_root(Path(__file__))
    try:
        text = read_text(root / SEED_DOC)
    except FileNotFoundError as exc:
        log.error("[FAIL] %s", exc)
        return 1

    fails = 0
    block = _find_code_block(text, "yaml", "preserve_pool")
    if block is None:
        log.error("[FAIL] Seed-YAML-Block fehlt")
        fails += 1
    else:
        preserve_section = _slice_pool(block, "preserve_pool:", "trigger_pool:")
        trigger_section = _slice_pool(block, "trigger_pool:", None)
        fails += _check_seed_pool(preserve_section, "P", "Preserve-Pool")
        fails += _check_seed_pool(trigger_section, "T", "Trigger-Pool")

    fails += _check_rift_table(text)
    fails += _check_twist_ids(text)

    log.log(25, "Summary: %s", "OK" if fails == 0 else f"FAIL ({fails})")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
