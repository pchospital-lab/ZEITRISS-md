#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ATTRIBUTE_KEYS = ("STR", "GES", "INT", "CHA", "TEMP", "SYS")


@dataclass
class PresetBlock:
    name: str
    base: dict[str, int]
    mods: dict[str, int]
    final: dict[str, int]
    talents: list[str]
    sys_used: int
    sys_max: int
    sys_listed: int


def parse_attributes(value: str, *, allow_missing: bool = False) -> dict[str, int]:
    normalized = value.replace("\u00a0", " ").replace("−", "-")
    matches = re.findall(r"\b(STR|GES|INT|CHA|TEMP|SYS)\s*([+-]?\d+)", normalized)
    attrs = {key: int(amount) for key, amount in matches}
    if not allow_missing:
        missing = [key for key in ATTRIBUTE_KEYS if key not in attrs]
        if missing:
            raise ValueError(f"fehlende Attribute: {', '.join(missing)}")
    return attrs


def parse_mods(value: str) -> dict[str, int]:
    if value.strip().lower() == "keine":
        return {key: 0 for key in ATTRIBUTE_KEYS}
    mods = parse_attributes(value, allow_missing=True)
    return {key: mods.get(key, 0) for key in ATTRIBUTE_KEYS}


def extract_sys_last(line: str) -> tuple[int, int]:
    normalized = line.replace("\u00a0", " ").replace("−", "-").replace("*", "")
    match = re.search(r"SYS-Last:\s*(\d+)\s*/\s*(\d+)", normalized)
    if not match:
        raise ValueError("SYS-Last fehlt")
    return int(match.group(1)), int(match.group(2))


def extract_sys_sum(line: str) -> int:
    normalized = line.replace("\u00a0", " ").replace("−", "-")
    return sum(int(value) for value in re.findall(r"\bSYS\s*(\d+)\b", normalized))


def extract_talents(line: str) -> list[str]:
    _, value = line.split("**Talente:**", 1)
    talents = [item.strip(" .") for item in value.split(";")]
    return [talent for talent in talents if talent]


def find_preset_blocks(lines: list[str]) -> list[PresetBlock]:
    blocks: list[PresetBlock] = []
    for index, line in enumerate(lines):
        if "**Preset-Check (Editor)**" not in line:
            continue
        name = "Preset"
        for back in range(index - 1, -1, -1):
            candidate = lines[back].strip()
            if candidate.startswith("### ") or candidate.startswith("#### "):
                name = candidate.lstrip("# ").strip()
                break
        try:
            base_line = lines[index + 1].strip()
            mods_line = lines[index + 2].strip()
            final_line = lines[index + 3].strip()
            talents_line = lines[index + 4].strip()
            cyber_line = lines[index + 5].strip()
        except IndexError as exc:
            raise ValueError(f"Preset-Block unvollständig bei {name}") from exc

        if not base_line.startswith("- **Basiswerte"):
            raise ValueError(f"Basiswerte-Zeile fehlt bei {name}")
        if not mods_line.startswith("- **Rassenmods:"):
            raise ValueError(f"Rassenmods-Zeile fehlt bei {name}")
        if not final_line.startswith("- **Finale Attribute:"):
            raise ValueError(f"Finale-Attribute-Zeile fehlt bei {name}")
        if not talents_line.startswith("- **Talente:"):
            raise ValueError(f"Talente-Zeile fehlt bei {name}")
        if not cyber_line.startswith("- **Cyber-/Bioware:"):
            raise ValueError(f"Cyber-/Bioware-Zeile fehlt bei {name}")

        base = parse_attributes(base_line)
        mods = parse_mods(mods_line.split(":", 1)[1])
        final = parse_attributes(final_line)
        talents = extract_talents(talents_line)
        sys_listed, sys_max = extract_sys_last(cyber_line)
        sys_used = extract_sys_sum(cyber_line)

        blocks.append(
            PresetBlock(
                name=name,
                base=base,
                mods=mods,
                final=final,
                talents=talents,
                sys_used=sys_used,
                sys_max=sys_max,
                sys_listed=sys_listed,
            )
        )
    return blocks


def validate_blocks(blocks: list[PresetBlock]) -> list[str]:
    errors: list[str] = []
    if not blocks:
        errors.append("Keine Preset-Checks gefunden.")
        return errors

    for block in blocks:
        base_sum = sum(block.base.values())
        if base_sum != 18:
            errors.append(f"{block.name}: Basiswerte summe {base_sum} != 18")
        for key in ATTRIBUTE_KEYS:
            base_value = block.base[key]
            final_value = block.final[key]
            mod_value = block.mods[key]
            if base_value < 0:
                errors.append(f"{block.name}: {key} Basiswert < 0")
            if base_value > 5:
                errors.append(f"{block.name}: {key} Basiswert > 5")
            if final_value < 1:
                errors.append(f"{block.name}: {key} Endwert < 1")
            if final_value > 5:
                errors.append(f"{block.name}: {key} Endwert > 5")
            if base_value + mod_value != final_value:
                errors.append(
                    f"{block.name}: {key} {base_value} + {mod_value} != {final_value}"
                )
        if not block.talents:
            errors.append(f"{block.name}: Talente fehlen")
        if len(block.talents) < 2:
            errors.append(f"{block.name}: zu wenige Talente")
        if block.sys_listed != block.sys_used:
            errors.append(
                f"{block.name}: SYS-Last {block.sys_listed} != SYS-Summe {block.sys_used}"
            )
        if block.sys_max != block.final["SYS"]:
            errors.append(
                f"{block.name}: SYS-Max {block.sys_max} != SYS-Attribut {block.final['SYS']}"
            )
        if block.sys_used > block.final["SYS"]:
            errors.append(
                f"{block.name}: SYS-Last {block.sys_used} > SYS {block.final['SYS']}"
            )
    return errors


def main() -> int:
    path = Path("characters/charaktererschaffung.md")
    content = path.read_text(encoding="utf-8")
    blocks = find_preset_blocks(content.splitlines())
    errors = validate_blocks(blocks)
    if errors:
        print("Preset-Validator: FEHLER", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Preset-Validator: OK ({len(blocks)} Presets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
