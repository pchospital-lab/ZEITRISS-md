"""Personal-Save-Extraktion (ZEITRISS v7) — A6: verschoben von
`internal/qa/harness/agent_mp/saves.py` nach `domain/zeitriss/` (v7-Save-
Semantik ist reines ZEITRISS-Domaenenwissen, gehoert nicht in den neutralen
Kern). Inhaltlich UNVERAENDERT gegenueber P1.

NF2-Fix (Re-Critic 2026-09-15): Das Personal-Save-Modell verlangt, dass ein
`!save` je Spielerfigur EINEN getrennten, vollstaendigen v7-JSON-Block mit
genau einer Figur in `characters[]` liefert (kein Sammel-/Host-Save).

NF3-Fix: Dateinamen leiten sich NICHT aus `characters[0].name` ab, sondern aus
dem stabilen `persona_key` (vom Caller uebergeben) bzw. ersatzweise aus der
`char_id` des Save-Blocks — nie aus geratenem Freitext.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def _try_v7(blob: str) -> dict | None:
    try:
        obj = json.loads(blob)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(obj, dict) and obj.get("v") == 7 and "characters" in obj:
        return obj
    return None


def extract_all_saves(text: str) -> list[dict]:
    """Alle v7-Save-Bloecke aus einem SL-Antworttext ziehen (dedupliziert)."""
    out: list[dict] = []
    seen: set[str] = set()
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        obj = _try_v7(m.group(1))
        if obj is not None:
            key = obj.get("save_id") or json.dumps(obj, sort_keys=True)[:80]
            if key not in seen:
                seen.add(key)
                out.append(obj)
    if not out and '"v"' in text:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            obj = _try_v7(text[start:end + 1])
            if obj is not None:
                out.append(obj)
    return out


def single_character_count(block: dict) -> int:
    chars = block.get("characters")
    return len(chars) if isinstance(chars, list) else 0


def block_char_id(block: dict) -> str | None:
    chars = block.get("characters")
    if isinstance(chars, list) and chars and isinstance(chars[0], dict):
        cid = chars[0].get("char_id") or chars[0].get("id")
        return str(cid) if cid else None
    return None


def _slug(value: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-")
    return s or "unknown"


def save_filename(turn_idx: int, block: dict, persona_key: str | None = None) -> str:
    tag = persona_key or block_char_id(block) or "unknown"
    return f"turn{turn_idx:02d}-{_slug(tag)}.json"


def harvest_from_debrief(debrief_text: str, cid_to_pk: dict[str, str]) -> dict[str, dict]:
    """`core.runtime.HarvestExtractor`-Implementierung: zieht je Chrononaut-ID
    GENAU EINEN passenden v7-Save-Block aus dem Debrief-/Turn-Text. Reale
    Produktversion der in `tests/mmo_sim/test_m1_runtime_section.py.
    _harvest_extractor` gespiegelten Testhilfsfunktion (I1: die Application-
    Service-Wiring braucht eine echte, importierbare Implementierung, kein
    Test-only-Duplikat)."""
    out: dict[str, dict] = {}
    for blk in extract_all_saves(debrief_text):
        cid = block_char_id(blk)
        pk = cid_to_pk.get(cid) if cid else None
        if pk is not None and single_character_count(blk) == 1 and pk not in out:
            out[pk] = blk
    return out


def extract_personal_saves(
    text: str,
    run_dir: str | Path,
    turn_idx: int,
    char_id_to_persona: dict[str, str] | None = None,
    write: bool = True,
) -> list[dict]:
    char_id_to_persona = char_id_to_persona or {}
    saves_dir = Path(run_dir) / "saves"
    if write:
        saves_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for block in extract_all_saves(text):
        n = single_character_count(block)
        cid = block_char_id(block)
        pkey = char_id_to_persona.get(cid) if cid else None
        fname = save_filename(turn_idx, block, persona_key=pkey)
        path = None
        if write:
            path = str(saves_dir / fname)
            Path(path).write_text(
                json.dumps(block, ensure_ascii=False, indent=2), encoding="utf-8")
        records.append({
            "path": path,
            "char_id": cid,
            "persona_key": pkey,
            "n_characters": n,
            "single_char_ok": n == 1,
            "block": block,
        })
    return records
