"""Personal-Save-Extraktion für Architektur B (agent_mp).

NF2-Fix (Re-Critic 2026-09-15): Das neue Personal-Save-Modell verlangt, dass ein
`!save` je Spielerfigur EINEN getrennten, vollständigen v7-JSON-Block mit genau
einer Figur in `characters[]` liefert (kein Sammel-/Host-Save). Bis hierher war
das nur in DESIGN.md §6 beschrieben, aber nirgends im Code — ein echter Run, der
einen Save-Punkt erreicht, hätte diese Funktion live und ungetestet erzwungen.

Design-Entscheidung: Die pure Textlogik aus `coreops_split_merge.extract_all_saves`
wird hier DUPLIZIERT statt importiert. Grund: `agent_mp` bleibt self-contained,
und der Import würde das komplette Split/Merge-Modul (PERSONAS-Dict, Env-Reads
auf Modulebene) mitziehen, obwohl wir nur ~30 Zeilen reine JSON-Extraktion
brauchen. Keine externen Abhängigkeiten, kein Netzwerk.

NF3-Fix: Dateinamen leiten sich NICHT aus `characters[0].name` ab (das wäre der
Figuren-Namensraum), sondern aus dem stabilen, harness-internen `persona_key`
(vom Caller übergeben) bzw. ersatzweise aus der `char_id` des Save-Blocks — nie
aus geratenem Freitext.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ── Reine Extraktion (dupliziert aus coreops_split_merge, bewusst dependency-frei)

def _try_v7(blob: str) -> dict | None:
    """Parst einen String; gibt ihn nur zurück, wenn es ein v7-Save-Objekt ist."""
    try:
        obj = json.loads(blob)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(obj, dict) and obj.get("v") == 7 and "characters" in obj:
        return obj
    return None


def extract_all_saves(text: str) -> list[dict]:
    """Alle v7-Save-Blöcke aus einem SL-Antworttext ziehen (dedupliziert).

    Erkennt sowohl ```json ...```-Fences als auch (Fallback) ein einzelnes
    nacktes JSON-Objekt, wenn `"v"` im Text vorkommt und keine Fences gefunden
    wurden."""
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


# ── Personal-Save-Contract-Prüfung (die "genau 1 Figur pro Block"-Garantie) ──

def single_character_count(block: dict) -> int:
    """Anzahl Figuren im `characters[]` eines Save-Blocks (robust bei Fehlform)."""
    chars = block.get("characters")
    return len(chars) if isinstance(chars, list) else 0


def block_char_id(block: dict) -> str | None:
    """Stabile `char_id` der ersten Figur, für Dateinamen/Zuordnung. None wenn fehlt."""
    chars = block.get("characters")
    if isinstance(chars, list) and chars and isinstance(chars[0], dict):
        cid = chars[0].get("char_id") or chars[0].get("id")
        return str(cid) if cid else None
    return None


def _slug(value: str) -> str:
    """ASCII-armer Slug für Dateinamen (keine Umlaut-/Pfad-Fallen)."""
    s = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-")
    return s or "unknown"


def save_filename(turn_idx: int, block: dict, persona_key: str | None = None) -> str:
    """Dateiname für einen Personal-Save-Block.

    Priorität: expliziter `persona_key` (harness-intern, stabil) > `char_id` aus
    dem Save-JSON (ebenfalls stabil). NIE `characters[0].name` raten (NF3)."""
    tag = persona_key or block_char_id(block) or "unknown"
    return f"turn{turn_idx:02d}-{_slug(tag)}.json"


def extract_personal_saves(
    text: str,
    run_dir: str | Path,
    turn_idx: int,
    char_id_to_persona: dict[str, str] | None = None,
    write: bool = True,
) -> list[dict]:
    """Zerlegt eine SL-Antwort in N getrennte Personal-Saves und schreibt sie.

    Rückgabe: Liste von Records, je Block:
        { "path": <geschriebener Pfad oder None>,
          "char_id": <str|None>,
          "persona_key": <str|None>,
          "n_characters": <int>,
          "single_char_ok": <bool>,   # Personal-Save-Contract: genau 1 Figur
          "block": <dict> }

    `single_char_ok=False` markiert einen Vertragsbruch (Sammel-Save o.ä.), OHNE
    zu werfen — der Caller entscheidet, ob er hart abbricht. Datei wird trotzdem
    geschrieben, damit nichts still verloren geht."""
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
