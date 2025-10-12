#!/usr/bin/env python3
"""Offline runtime lint for ZEITRISS guard rails."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable


RUNTIME_DIRS: tuple[str, ...] = ("core", "characters", "gameplay", "systems")
SAVE_REQUIRED_FIELDS: tuple[str, ...] = (
    "character.id",
    "character.attributes.SYS_max",
    "character.attributes.SYS_used",
    "character.stress",
    "character.psi_heat",
    "character.cooldowns",
    "campaign.px",
    "economy",
    "logs",
    "logs.artifact_log",
    "logs.market",
    "logs.offline",
    "logs.kodex",
    "logs.alias_trace",
    "logs.squad_radio",
    "logs.flags",
    "ui",
)

# Import helpers; rely on PYTHONPATH or fallback to repo root
try:
    from scripts.lib_repo import repo_root, read_text, get_logger
except ImportError:  # pragma: no cover - fallback for direct calls
    import sys
    _root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(_root))
    from scripts.lib_repo import repo_root, read_text, get_logger  # type: ignore

log = get_logger("lint_runtime")


def req(pattern: str | re.Pattern[str], text: str, msg: str, fails: list[str]) -> None:
    pat: re.Pattern[str] = re.compile(pattern, re.S) if isinstance(pattern, str) else pattern
    if not pat.search(text):
        log.error("[FAIL] %s", msg)
        fails.append(msg)
    else:
        log.info("[ OK ] %s", msg)


def check_yaml_headers(root: Path, fails: list[str]) -> None:
    for md_file in iter_runtime_markdown(root):
        rel = md_file.relative_to(root)
        try:
            text = read_text(md_file)
        except FileNotFoundError as exc:
            msg = f"{rel}: {exc}"
            log.error("[FAIL] %s", msg)
            fails.append(msg)
            continue

        header = extract_front_matter(text)
        if header is None:
            msg = f"{rel}: YAML-Header fehlt oder ist unvollständig"
            log.error("[FAIL] %s", msg)
            fails.append(msg)
            continue

        missing_keys: list[str] = []
        for key in ("title", "version", "tags"):
            value = header.get(key, "")
            if not normalize_value(value):
                missing_keys.append(key)

        tags_value = header.get("tags", "")
        tags = parse_tags(tags_value)
        if not tags:
            missing_keys.append("tags")

        if missing_keys:
            msg = f"{rel}: fehlende Pflichtfelder im YAML-Header ({', '.join(sorted(set(missing_keys)))})"
            log.error("[FAIL] %s", msg)
            fails.append(msg)
            continue

        log.info("[ OK ] %s – YAML-Header vollständig", rel)


def check_save_required_fields(text: str, fails: list[str]) -> None:
    for field in SAVE_REQUIRED_FIELDS:
        req(
            rf"\"{re.escape(field)}\"",
            text,
            f"Save-Pflichtfeld `{field}` dokumentiert",
            fails,
        )


def iter_runtime_markdown(root: Path) -> Iterable[Path]:
    for directory in RUNTIME_DIRS:
        base = root / directory
        if not base.exists():
            continue
        yield from sorted(base.rglob("*.md"))


def extract_front_matter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None

    end_index: int | None = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = idx
            break

    if end_index is None:
        return None

    header_lines = lines[1:end_index]
    header: dict[str, str] = {}
    for raw in header_lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        header[key.strip()] = value.strip()
    return header


def normalize_value(value: str) -> str:
    value = value.strip()
    if value and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value


def parse_tags(value: str) -> list[str]:
    raw = normalize_value(value)
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        tags: list[str] = []
        for part in inner.split(","):
            normalized = normalize_value(part)
            if normalized:
                tags.append(normalized)
        return tags
    return []


def main() -> int:
    root = repo_root(Path(__file__))
    fails: list[str] = []

    check_yaml_headers(root, fails)

    try:
        tk = read_text(root / "systems" / "toolkit-gpt-spielleiter.md")
    except FileNotFoundError as e:
        log.error(str(e))
        fails.append(str(e))
        tk = ""

    try:
        sv = read_text(root / "systems" / "gameflow" / "speicher-fortsetzung.md")
    except FileNotFoundError as e:
        log.error(str(e))
        fails.append(str(e))
        sv = ""

    gm_style = os.getenv("GM_STYLE", "precision")

    # Mission-Invarianten & Gates
    req(r"StartMission\([^\)]*type=\"core\"", tk, "StartMission: type core path", fails)
    req(r"scene_total\s*=\s*12", tk, "Core: 12 Szenen gesetzt", fails)
    req(r"scene_total\s*=\s*14", tk, "Rift: 14 Szenen gesetzt", fails)
    req(r"LINT:BOSS_SCENE10_RIFT", tk, "Boss-Hook vorhanden", fails)
    req(r"LINT:CORE_BOSS_M05_M10", tk, "Core-Boss nur in Mission 5/10 erlaubt", fails)

    # DelayConflict & Finale
    req(r"DelayConflict\(\s*4\s*\)", tk, "DelayConflict(4) aktiv", fails)
    req(r"Finale blockiert", tk, "Finale-Guard-Text vorhanden", fails)

    # PRECISION-Validator
    req(r"SceneHeader\(", tk, "SceneHeader-Macro vorhanden", fails)
    req(r"Decision\(", tk, "Decision-Macro vorhanden", fails)
    if gm_style == "precision":
        req(r"PRECISION fehlend", tk, "PRECISION-Warnung vorhanden", fails)

    # Px-HUD
    req(r"Px[:\s]+[▓░]{5}", tk, "Px-Balken dargestellt", fails)
    req(r"TEMP", tk, "TEMP im HUD", fails)
    req(r"ETA \+1 in\s+\d", tk, "ETA bis nächster Px-Punkt", fails)

    # Seeds & Episode-Gate
    req(r"LINT:PX5_SEED_GATE", tk, "Px5-HUD Tag", fails)
    req(r"can_launch_rift", tk, "can_launch_rift Macro vorhanden", fails)
    req(r"episode_completed\s*=\s*true", tk, "Episodenabschluss markiert", fails)
    req(r"apply_rift_mods_next_episode", tk, "Episoden-Boni werden gequeued", fails)
    req(r"launch_rift", tk, "launch_rift Gate vorhanden", fails)

    # Artefakt-Gate
    req(r"artifact_allowed", tk, "Artefakt-Gate-Flag vorhanden", fails)
    req(r"LINT:RIFT_ARTIFACT_11_13_D6", tk, "Artefakt-Gate-Block vorhanden", fails)

    # FR-Intervention
    req(r"LINT:FR_INTERVENTION", tk, "Fraktionsintervention HUD-Tag vorhanden", fails)

    # Signal & Comms
    req(r"validate_signal", tk, "Runtime Signal-Guard vorhanden", fails)
    req(
        r"CommsCheck failed: require valid device/range or relay/jammer override.",
        tk,
        "Comms einheitliche Fehlermeldung",
        fails,
    )
    req(r"macro radio_tx[\s\S]*must_comms", tk, "radio_tx nutzt must_comms", fails)
    req(r"macro radio_rx", tk, "radio_rx Macro vorhanden", fails)

    # HQ Save Guard
    if sv:
        check_save_required_fields(sv, fails)

    req(r"LINT:HQ_ONLY_SAVE", sv, "HQ-only Save Guard erwähnt", fails)
    req(r"save_version", sv, "save_version im Save-Modul", fails)
    req(r"migrate_save", sv, "migrate_save vorhanden", fails)
    req(
        r"state\.character\.attributes\.SYS_used == state\.character\.attributes\.SYS_max|SYS_used == SYS_max",
        sv,
        "Deterministik geprüft",
        fails,
    )

    # Conflict Gate Helper
    req(r"can_open_conflict", tk, "can_open_conflict Macro vorhanden", fails)

    # Preserve/Trigger Marker
    req(r"campaign\.mode", tk, "Preserve/Trigger-Flag gesetzt", fails)
    req(r"preserve_pool|trigger_pool", tk, "Seed-Pools referenziert", fails)
    req(r"Briefing:\s*kleineres Übel sichern", tk, "Trigger-Pflichtsatz im Briefing", fails)

    log.log(25, "Summary: %s", "OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
