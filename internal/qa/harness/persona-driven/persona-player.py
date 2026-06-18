#!/usr/bin/env python3
"""
Persona-Playtest-Harness v1 für ZEITRISS.

SL-Turns: OWUI /api/chat/completions → Preset zeitriss-v426-uncut-cached
Persona-Turns: OpenRouter direkt → anthropic/claude-sonnet-4.6

Alle externen Calls: requests.Timeout(10, 180), 3 Retries mit exp. Backoff.
PID-File in ~/.openclaw/workspace-cloud/tmp/running/persona-player-<phase>.pid
JSONL-Log pro Turn in <outdir>/turns.jsonl.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import signal
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
import yaml  # type: ignore

# ---------------------------------------------------------------------------
# Konstanten / Pfade
# ---------------------------------------------------------------------------

HOME = Path(os.path.expanduser("~"))
RUNNING_DIR = HOME / ".openclaw" / "workspace-cloud" / "tmp" / "running"
RUNNING_DIR.mkdir(parents=True, exist_ok=True)

OWUI_BASE = "http://127.0.0.1:8080"
OWUI_MODEL = "zeitriss-v426-uncut-cached"
OWUI_ENV_FILE = HOME / ".openwebui_env"

OR_BASE = "https://openrouter.ai/api/v1/chat/completions"
OR_MODEL_PERSONA = "anthropic/claude-sonnet-4.6"
OR_AUTH_FILE = Path("/home/altair/.openclaw-cloud/agents/main/agent/auth-profiles.json")

TIMEOUT = (10, 180)  # connect, read
MAX_RETRIES = 3
BACKOFF_BASE = 2.0

# ---------------------------------------------------------------------------
# Helpers: Secrets laden
# ---------------------------------------------------------------------------


def load_owui_key() -> str:
    if not OWUI_ENV_FILE.exists():
        raise RuntimeError(f"{OWUI_ENV_FILE} missing")
    for line in OWUI_ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("OPENWEBUI_API_KEY="):
            v = line.split("=", 1)[1].strip().strip("'").strip('"')
            return v
    raise RuntimeError("OPENWEBUI_API_KEY missing in env file")


def load_or_key() -> str:
    data = json.loads(OR_AUTH_FILE.read_text())
    for _, prof in (data.get("profiles") or {}).items():
        k = prof.get("key", "")
        if k.startswith("sk-or-"):
            return k
    raise RuntimeError("No sk-or-* key in auth-profiles.json")


# ---------------------------------------------------------------------------
# Helpers: HTTP mit Retry
# ---------------------------------------------------------------------------


def http_post_json(url: str, headers: dict, payload: dict, label: str) -> dict:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            if r.status_code == 429:
                wait = BACKOFF_BASE ** attempt + random.uniform(0, 1)
                print(f"[{label}] 429, wait {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                wait = BACKOFF_BASE ** attempt
                print(f"[{label}] {r.status_code}, retry in {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if not r.ok:
                raise RuntimeError(f"{label} HTTP {r.status_code}: {r.text[:400]}")
            return r.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
            wait = BACKOFF_BASE ** attempt
            print(f"[{label}] {type(e).__name__}, retry in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"{label} failed after {MAX_RETRIES} retries: {last_err}")


# ---------------------------------------------------------------------------
# SL-Call (OWUI)
# ---------------------------------------------------------------------------


def call_sl(owui_key: str, messages: list[dict], max_tokens: int = 2200) -> tuple[str, dict]:
    payload = {
        "model": OWUI_MODEL,
        "max_tokens": max_tokens,
        "stream": False,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {owui_key}",
        "Content-Type": "application/json",
    }
    t0 = time.time()
    r = http_post_json(f"{OWUI_BASE}/api/chat/completions", headers, payload, "SL")
    dt = time.time() - t0
    content = r["choices"][0]["message"]["content"]
    usage = r.get("usage", {}) or {}
    ptd = usage.get("prompt_tokens_details", {}) or {}
    ctd = usage.get("completion_tokens_details", {}) or {}
    meta = {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "cached_tokens": ptd.get("cached_tokens", 0),
        "cache_write_tokens": ptd.get("cache_write_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "cost": usage.get("cost", 0.0),
        "turn_wallclock_s": round(dt, 2),
        "reasoning_tokens": ctd.get("reasoning_tokens", 0),
    }
    return content, meta


# ---------------------------------------------------------------------------
# Persona-Call (OpenRouter)
# ---------------------------------------------------------------------------


def call_persona(
    or_key: str,
    persona_system: str,
    history_for_persona: list[dict],
    max_tokens: int = 600,
) -> tuple[str, dict]:
    payload = {
        "model": OR_MODEL_PERSONA,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": persona_system}] + history_for_persona,
    }
    headers = {
        "Authorization": f"Bearer {or_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost/zeitriss-playtest",
        "X-Title": "ZEITRISS-Persona-Playtest",
    }
    t0 = time.time()
    r = http_post_json(OR_BASE, headers, payload, "PERSONA")
    dt = time.time() - t0
    content = r["choices"][0]["message"]["content"]
    usage = r.get("usage", {}) or {}
    ptd = usage.get("prompt_tokens_details", {}) or {}
    meta = {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "cached_tokens": ptd.get("cached_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "cost": usage.get("cost", 0.0),
        "turn_wallclock_s": round(dt, 2),
    }
    return content, meta


# ---------------------------------------------------------------------------
# Save-JSON-Parser (v7-Schema)
# ---------------------------------------------------------------------------


def extract_save_json(text: str) -> dict | None:
    """Versuche Save-JSON aus SL-Response zu extrahieren.

    Bevorzugt: ```json ... ``` Fenced Block.
    Fallback: letzter balancierter {...}-Block, der "save_id" oder "v" enthält.
    """
    # fenced
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # generic fenced
    m = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Fallback: letzter {...} mit "save_id" oder '"v":'
    candidates = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                candidates.append(text[start : i + 1])
                start = None
    for cand in reversed(candidates):
        if '"save_id"' in cand or '"v":' in cand:
            try:
                return json.loads(cand)
            except json.JSONDecodeError:
                continue
    return None


def validate_save_v7(save: dict | None) -> tuple[bool, list[str]]:
    if save is None:
        return False, ["no_save_found"]
    errors = []
    if save.get("v") not in (7, "7"):
        errors.append(f"v!=7 (got {save.get('v')!r})")
    if not save.get("save_id"):
        errors.append("save_id missing")
    chars = save.get("characters")
    if not isinstance(chars, list) or len(chars) == 0:
        errors.append("characters[] missing or empty")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# RAG-Modul-Heuristik
# ---------------------------------------------------------------------------


def detect_rag_hints(sl_meta: dict) -> tuple[list[str], int]:
    """
    OWUI liefert RAG-Module nicht direkt zurück. Wir schätzen aus
    prompt_tokens - ~19035 (Masterprompt-Cache-Region) = RAG+History-Payload.
    """
    prompt_tokens = sl_meta.get("prompt_tokens", 0)
    cached = sl_meta.get("cached_tokens", 0)
    # Nicht-gecachter Anteil (≈ neuer RAG-Prefix + History + User-Turn)
    uncached = max(0, prompt_tokens - cached)
    # grobe Byte-Schätzung (1 token ≈ 3.5 bytes für de)
    rag_bytes_est = uncached * 3  # konservativ
    return [], rag_bytes_est


# ---------------------------------------------------------------------------
# Persona-System-Prompt-Builder
# ---------------------------------------------------------------------------


def build_persona_system(player: dict, character: dict, phase: str, scenario_hint: str) -> str:
    attrs = character["attributes"]
    attr_str = ", ".join(f"{k}={v}" for k, v in attrs.items())
    psi_line = "Ja (Psionikerin)" if character.get("has_psi") else "Nein"
    return f"""Du spielst EINEN Spieler in einem ZEITRISS-Tabletop-Playtest. ZEITRISS ist ein Tech-Noir-Zeitreise-RPG mit expliziter harter Erwachsenen-Atmosphäre (18+).

DEIN SPIELER:
Name: {player['name']}
Spielstil: {player['style']}
Regelkenntnis: {player['rule_knowledge']}
Verbosität: {player['verbosity']}

DEIN CHARAKTER:
Name: {character['name']}
Archetyp: {character['archetype']}
Attribute: {attr_str}
Psi-Fähigkeit: {psi_line}

KONTEXT: {scenario_hint}

VERHALTENSREGELN (streng):
- Du bist NICHT der Spielleiter. Du bist SPIELER. Beschreibe nur was dein Charakter sagt, tut, denkt. Keine NSC-Dialoge, keine Würfelergebnisse, keine Szene-Beschreibungen der Umgebung außer was dein Charakter wahrnimmt.
- Bleib konsistent im Stil des Spielers (Spieler {player['name']} ist {player['verbosity']}, {player['style'][:80]}).
- Wenn die Spielleitung dich nach einer Probe fragt: Ansage knapp. Bei Psi: frag ggf. nach Kosten (PP und SYS).
- Wenn die Spielleitung eine Save-JSON ausgibt oder Metainfos: Ignorier sie in deiner Spieler-Antwort (spiel nur das, was dein Charakter gesagt/getan hätte).
- Antworte AUF DEUTSCH, im Stil eines echten Spielers am Tisch. Kein Meta-Kommentar, kein "als Spieler würde ich...". Sondern: Aktion, Absicht, evtl. In-Character-Dialog.
- Länge: ~40–150 Worte je nach verbosity-Setting. Chaoten auch mal 15 Worte. Narrator darf bis ~200.
- KEINE Regelbrüche erfinden: nutze nur, was zum Charakter passt. Keine Fähigkeiten, die nicht zu seinen Attributen passen.

Phase-Info: Phase {phase}. {"Solo-Playtest — nur dein Charakter." if phase != "B" else "Gruppen-Playtest — du spielst MIT den anderen."}
"""


# ---------------------------------------------------------------------------
# Turn-Logger
# ---------------------------------------------------------------------------


@dataclass
class TurnLog:
    outdir: Path
    total_cost: float = 0.0
    total_cache_read: int = 0
    total_cache_write: int = 0
    total_uncached: int = 0
    total_output: int = 0
    turn_count: int = 0
    save_failures_consecutive: int = 0
    save_failures_total: int = 0
    cache_hit_ratios: list[float] = field(default_factory=list)

    def log(self, record: dict) -> None:
        self.turn_count += 1
        self.total_cost += record.get("cost_usd", 0.0) or 0.0
        if record.get("role") == "sl":
            cr = record.get("cache_read_input_tokens", 0) or 0
            cw = record.get("cache_creation_input_tokens", 0) or 0
            un = record.get("input_tokens_uncached", 0) or 0
            self.total_cache_read += cr
            self.total_cache_write += cw
            self.total_uncached += un
            self.total_output += record.get("output_tokens", 0) or 0
            self.cache_hit_ratios.append(record.get("cache_hit_ratio", 0.0) or 0.0)
            if record.get("save_failed"):
                self.save_failures_consecutive += 1
                self.save_failures_total += 1
            elif record.get("save_checked") is True:
                self.save_failures_consecutive = 0
        with (self.outdir / "turns.jsonl").open("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def summary(self) -> dict:
        avg = (
            sum(self.cache_hit_ratios) / len(self.cache_hit_ratios)
            if self.cache_hit_ratios
            else 0.0
        )
        return {
            "turns": self.turn_count,
            "total_cost_usd": round(self.total_cost, 4),
            "tokens_read_total": self.total_cache_read,
            "tokens_write_total": self.total_cache_write,
            "tokens_uncached_total": self.total_uncached,
            "tokens_output_total": self.total_output,
            "avg_cache_hit_ratio": round(avg, 3),
            "save_failures_total": self.save_failures_total,
        }


# ---------------------------------------------------------------------------
# PID-File
# ---------------------------------------------------------------------------


class PIDFile:
    def __init__(self, phase: str, extra: str = ""):
        name = f"persona-player-{phase}{'-' + extra if extra else ''}.pid"
        self.path = RUNNING_DIR / name

    def __enter__(self):
        self.path.write_text(str(os.getpid()))
        return self

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# SZENARIO-SEEDS
# ---------------------------------------------------------------------------


SCENARIO_A = """PHASE A (Solo): Chargen-Schnelltest und Einstiegsszene auf Mission 1.
Start-Szene: ITI-Briefing-Raum, {char_name} erhält Auftrag: Anomalie im Berliner Hinterhof, Oktober 2019, möglicher Zeitriss. 12-Szenen-Core-Struktur. Keine Gruppen-NSCs außer Kontakt-NSC "Diana Körber". Save-JSON alle 3 Turns anbieten (v7-Schema)."""

SCENARIO_B = """PHASE B (Gruppe): Dasselbe Briefing, alle drei Chrononauten gemeinsam im ITI-Raum. Diana Körber briefet das Team. Core-Mission weiter. Kooperative Proben wo sinnvoll."""

SCENARIO_C = """PHASE C (Mini-Boss, Mission 5): Solo-Resumé. {char_name} ist allein in der Rift-Schicht und trifft auf den Mini-Boss "Silhouette-1" (invertierte Chrono-Wache). Kampf + Psi-Probe möglich. 14-Szenen-Rift-Struktur."""


def scenario_text(phase: str, char_name: str) -> str:
    if phase == "A":
        return SCENARIO_A.replace("{char_name}", char_name)
    if phase == "B":
        return SCENARIO_B
    return SCENARIO_C.replace("{char_name}", char_name)


# ---------------------------------------------------------------------------
# Core-Loop: Solo (Phase A / C)
# ---------------------------------------------------------------------------


def run_solo(
    *,
    owui_key: str,
    or_key: str,
    phase: str,
    player_key: str,
    character_key: str,
    personas_data: dict,
    turns: int,
    outdir: Path,
    session_tag: str,
    save_in: Path | None = None,
) -> dict:
    player = personas_data["players"][player_key]
    character = personas_data["characters"][character_key]
    persona_sys = build_persona_system(
        player, character, phase, scenario_text(phase, character["name"])
    )

    logger = TurnLog(outdir=outdir)

    # SL-Chat-History (nur User-Turns gehen in messages; System ist im Preset)
    sl_messages: list[dict] = []
    # Persona-History (SL sagt X als user, Persona antwortet als assistant)
    persona_history: list[dict] = []

    # Opening: Persona startet mit Chargen-Statement oder lädt Save
    if save_in and save_in.exists():
        save_text = save_in.read_text()
        opener = (
            f"Ich lade diesen Spielstand:\n\n```json\n{save_text}\n```\n\n"
            f"Dann: Wir machen weiter. {character['name']} ist bereit."
        )
    else:
        attrs = character["attributes"]
        attr_pretty = ", ".join(f"{k} {v}" for k, v in attrs.items())
        opener = (
            f"Ich spiele {character['name']} — {character['archetype']}. "
            f"Attribute: {attr_pretty}. "
            f"Psi: {'ja' if character.get('has_psi') else 'nein'}. "
            f"Spielstart bitte — Mission 1, Szene 1. "
            f"Gib bitte am Ende jedes 3.-4. Turns eine Save-JSON nach v7-Schema mit aus, "
            f"damit ich zwischendurch laden könnte."
        )

    sl_messages.append({"role": "user", "content": opener})

    for turn_idx in range(1, turns + 1):
        # --- SL Turn ---
        try:
            sl_content, sl_meta = call_sl(owui_key, sl_messages, max_tokens=2200)
        except Exception as e:
            print(f"[phase {phase}] SL turn {turn_idx} failed: {e}", file=sys.stderr)
            logger.log({
                "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                "persona": player_key, "character": character_key, "role": "sl",
                "error": str(e)[:300],
            })
            break

        rag_modules, rag_bytes_est = detect_rag_hints(sl_meta)
        cached = sl_meta["cached_tokens"]
        total_prompt = sl_meta["prompt_tokens"]
        ratio = cached / total_prompt if total_prompt else 0.0

        # Save parsing (every turn — cheap)
        save = extract_save_json(sl_content)
        save_ok, save_errs = validate_save_v7(save) if save is not None else (False, [])
        save_checked = save is not None
        record_sl = {
            "session_tag": session_tag,
            "turn": turn_idx,
            "phase": phase,
            "persona": player_key,
            "character": character_key,
            "role": "sl",
            "cache_creation_input_tokens": sl_meta["cache_write_tokens"],
            "cache_read_input_tokens": cached,
            "input_tokens_uncached": max(0, total_prompt - cached),
            "output_tokens": sl_meta["completion_tokens"],
            "cost_usd": round(sl_meta["cost"], 6),
            "rag_modules": rag_modules,
            "rag_bytes_estimate": rag_bytes_est,
            "history_tokens_estimate": max(0, total_prompt - cached - 500),
            "turn_wallclock_s": sl_meta["turn_wallclock_s"],
            "cache_hit_ratio": round(ratio, 3),
            "content_chars": len(sl_content),
            "save_checked": save_checked,
            "save_failed": save_checked and not save_ok,
            "save_errors": save_errs if save_checked and not save_ok else [],
        }
        if ratio < 0.5 and cached > 0:
            record_sl["warning_low_cache_ratio"] = True
        logger.log(record_sl)

        # Persist SL content chunk
        with (outdir / f"sl-content-{phase}-{character_key}.md").open("a") as f:
            f.write(f"\n\n--- Turn {turn_idx} SL ---\n{sl_content}\n")

        # Hard-Stop bei 2 konsekutiven Save-Failures
        if logger.save_failures_consecutive >= 2:
            print(f"[phase {phase}] Hard-stop: 2 consecutive save failures", file=sys.stderr)
            break

        # --- Persona Turn ---
        # Regelmäßige Save-Nachfrage (alle 4 Turns) an Persona-Prompt anhängen
        save_reminder = ""
        if turn_idx % 4 == 0:
            save_reminder = (
                "\n\n[INTERNER HINWEIS AN DICH: Die Session braucht eine Save. "
                "Frag die Spielleitung am Ende deiner Antwort nach einem aktuellen Speicherstand als JSON-Block "
                "nach v7-Schema. Halt’s kurz, in deinem Charakter-Ton.]"
            )
        persona_history.append({"role": "user", "content": f"Spielleitung sagt:\n{sl_content}{save_reminder}"})
        try:
            persona_content, persona_meta = call_persona(
                or_key, persona_sys, persona_history, max_tokens=600
            )
        except Exception as e:
            print(f"[phase {phase}] Persona turn {turn_idx} failed: {e}", file=sys.stderr)
            logger.log({
                "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                "persona": player_key, "character": character_key, "role": "persona",
                "error": str(e)[:300],
            })
            break

        record_p = {
            "session_tag": session_tag,
            "turn": turn_idx,
            "phase": phase,
            "persona": player_key,
            "character": character_key,
            "role": "persona",
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": persona_meta.get("cached_tokens", 0),
            "input_tokens_uncached": max(
                0, persona_meta["prompt_tokens"] - persona_meta.get("cached_tokens", 0)
            ),
            "output_tokens": persona_meta["completion_tokens"],
            "cost_usd": round(persona_meta["cost"], 6),
            "rag_modules": [],
            "rag_bytes_estimate": 0,
            "history_tokens_estimate": persona_meta["prompt_tokens"],
            "turn_wallclock_s": persona_meta["turn_wallclock_s"],
            "cache_hit_ratio": 0.0,  # Persona-Context ist anders, kein Masterprompt-Cache
            "content_chars": len(persona_content),
        }
        logger.log(record_p)

        persona_history.append({"role": "assistant", "content": persona_content})
        sl_messages.append({"role": "assistant", "content": sl_content})
        sl_messages.append({"role": "user", "content": persona_content})

        with (outdir / f"persona-content-{phase}-{character_key}.md").open("a") as f:
            f.write(f"\n\n--- Turn {turn_idx} Persona ---\n{persona_content}\n")

        # Cost-Watchdog
        if logger.total_cost > 3.5:
            print(f"[phase {phase}] Cost watchdog triggered at ${logger.total_cost:.3f}", file=sys.stderr)
            break

    summary = logger.summary()
    (outdir / f"summary-{phase}-{character_key}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    return summary


# ---------------------------------------------------------------------------
# Gruppen-Loop (Phase B) — 70% consolidated / 30% sequential
# ---------------------------------------------------------------------------


def run_group(
    *,
    owui_key: str,
    or_key: str,
    personas_data: dict,
    turns: int,
    outdir: Path,
    session_tag: str,
) -> dict:
    phase = "B"
    players = personas_data["players"]
    characters = personas_data["characters"]
    assignment = personas_data["assignment"]  # player_key -> character_key

    logger = TurnLog(outdir=outdir)
    persona_systems: dict[str, str] = {}
    for pk, ck in assignment.items():
        persona_systems[pk] = build_persona_system(
            players[pk], characters[ck], phase, scenario_text(phase, characters[ck]["name"])
        )
    persona_histories: dict[str, list[dict]] = {pk: [] for pk in assignment}
    sl_messages: list[dict] = []

    opener = (
        "Gruppen-Einstieg. Wir sind drei Chrononauten am ITI-Briefing-Tisch:\n"
        + "\n".join(
            f"- {characters[ck]['name']} ({characters[ck]['archetype']}, "
            f"Attribute: {', '.join(f'{a} {v}' for a,v in characters[ck]['attributes'].items())}, "
            f"Psi: {'ja' if characters[ck].get('has_psi') else 'nein'})"
            for _, ck in assignment.items()
        )
        + "\n\nSpielleitung: Briefing bitte, dann Szene 1."
    )
    sl_messages.append({"role": "user", "content": opener})

    rotation = list(assignment.keys())  # A_tactician, B_narrator, C_chaot
    consolidator_idx = 0

    internal_file = outdir / "B-group-merge.internal.md"
    internal_file.write_text(f"# Phase B Roundtable Internal Transcript\nSession: {session_tag}\n")

    for turn_idx in range(1, turns + 1):
        # --- SL Turn ---
        try:
            sl_content, sl_meta = call_sl(owui_key, sl_messages, max_tokens=2400)
        except Exception as e:
            print(f"[B] SL turn {turn_idx} failed: {e}", file=sys.stderr)
            logger.log({"session_tag": session_tag, "turn": turn_idx, "phase": phase,
                        "role": "sl", "error": str(e)[:300]})
            break

        cached = sl_meta["cached_tokens"]
        total_prompt = sl_meta["prompt_tokens"]
        ratio = cached / total_prompt if total_prompt else 0.0
        save = extract_save_json(sl_content)
        save_ok, save_errs = validate_save_v7(save) if save is not None else (False, [])
        save_checked = save is not None

        record_sl = {
            "session_tag": session_tag, "turn": turn_idx, "phase": phase,
            "persona": "group", "character": "group", "role": "sl",
            "cache_creation_input_tokens": sl_meta["cache_write_tokens"],
            "cache_read_input_tokens": cached,
            "input_tokens_uncached": max(0, total_prompt - cached),
            "output_tokens": sl_meta["completion_tokens"],
            "cost_usd": round(sl_meta["cost"], 6),
            "rag_modules": [], "rag_bytes_estimate": max(0, total_prompt - cached) * 3,
            "history_tokens_estimate": max(0, total_prompt - cached - 500),
            "turn_wallclock_s": sl_meta["turn_wallclock_s"],
            "cache_hit_ratio": round(ratio, 3),
            "content_chars": len(sl_content),
            "save_checked": save_checked, "save_failed": save_checked and not save_ok,
            "save_errors": save_errs if save_checked and not save_ok else [],
        }
        logger.log(record_sl)
        with (outdir / "sl-content-B.md").open("a") as f:
            f.write(f"\n\n--- Turn {turn_idx} SL ---\n{sl_content}\n")

        if logger.save_failures_consecutive >= 2:
            print(f"[B] Hard-stop: 2 consecutive save failures", file=sys.stderr)
            break

        # --- Persona-Absprache (2 Runden intern) ---
        # Runde 1: alle drei kurz, was sie machen würden
        round1_msgs: dict[str, str] = {}
        for pk in rotation:
            hist = persona_histories[pk][:]
            hist.append({"role": "user", "content":
                f"Spielleitung sagt:\n{sl_content}\n\n"
                f"INTERNE RUNDE 1 (nicht an SL!): Sag in 1-2 Sätzen, was dein Charakter machen will. "
                f"Keine Aktion ausführen, nur Absicht erklären."})
            try:
                c, m = call_persona(or_key, persona_systems[pk], hist, max_tokens=250)
            except Exception as e:
                c, m = f"[error {e}]", {"prompt_tokens":0,"completion_tokens":0,"cost":0,"turn_wallclock_s":0,"cached_tokens":0}
            round1_msgs[pk] = c
            logger.log({
                "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                "persona": pk, "character": assignment[pk], "role": "persona-internal-r1",
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": m.get("cached_tokens", 0),
                "input_tokens_uncached": max(0, m["prompt_tokens"] - m.get("cached_tokens", 0)),
                "output_tokens": m["completion_tokens"], "cost_usd": round(m["cost"], 6),
                "rag_modules": [], "rag_bytes_estimate": 0,
                "history_tokens_estimate": m["prompt_tokens"],
                "turn_wallclock_s": m["turn_wallclock_s"], "cache_hit_ratio": 0.0,
                "content_chars": len(c),
            })

        # Runde 2: alle drei reagieren auf die anderen
        others_text = "\n".join(
            f"- {players[k]['name']} ({characters[assignment[k]]['name']}): {v}"
            for k, v in round1_msgs.items()
        )
        round2_msgs: dict[str, str] = {}
        for pk in rotation:
            hist = persona_histories[pk][:]
            hist.append({"role": "user", "content":
                f"Spielleitung sagte:\n{sl_content}\n\n"
                f"INTERNE RUNDE 2: Die anderen Spieler haben gerade gesagt:\n{others_text}\n\n"
                f"Reagier kurz (1-2 Sätze): Passt dein Plan zu deren? Ändern? "
                f"Keine finale Aktion, nur kurze Absprache."})
            try:
                c, m = call_persona(or_key, persona_systems[pk], hist, max_tokens=200)
            except Exception as e:
                c, m = f"[error {e}]", {"prompt_tokens":0,"completion_tokens":0,"cost":0,"turn_wallclock_s":0,"cached_tokens":0}
            round2_msgs[pk] = c
            logger.log({
                "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                "persona": pk, "character": assignment[pk], "role": "persona-internal-r2",
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": m.get("cached_tokens", 0),
                "input_tokens_uncached": max(0, m["prompt_tokens"] - m.get("cached_tokens", 0)),
                "output_tokens": m["completion_tokens"], "cost_usd": round(m["cost"], 6),
                "rag_modules": [], "rag_bytes_estimate": 0,
                "history_tokens_estimate": m["prompt_tokens"],
                "turn_wallclock_s": m["turn_wallclock_s"], "cache_hit_ratio": 0.0,
                "content_chars": len(c),
            })

        # Transkript
        with internal_file.open("a") as f:
            f.write(f"\n\n## Turn {turn_idx}\n### Round 1\n")
            for k, v in round1_msgs.items():
                f.write(f"**{players[k]['name']}**: {v}\n\n")
            f.write("### Round 2\n")
            for k, v in round2_msgs.items():
                f.write(f"**{players[k]['name']}**: {v}\n\n")

        # Modus-Seed: 70/30
        mode = "consolidated" if random.random() < 0.7 else "sequential"

        round2_text = "\n".join(
            f"- {players[k]['name']}: {v}" for k, v in round2_msgs.items()
        )
        if mode == "consolidated":
            # Rotierender Konsolidierer
            pk = rotation[consolidator_idx % len(rotation)]
            consolidator_idx += 1
            hist = persona_histories[pk][:]
            consolidated_prompt = (
                f"Spielleitung sagte:\n{sl_content}\n\n"
                f"Eure interne Absprache R1:\n{others_text}\n\n"
                f"R2 (Reaktionen):\n{round2_text}\n\n"
                f"FINAL: Du ({players[pk]['name']}) fasst jetzt zusammen für die Spielleitung. "
                f"Was macht die Gruppe? Sprich im Namen der Gruppe (mit Einwilligung), "
                f"aber bleib in deinem Charakter-Ton."
            )
            hist.append({"role": "user", "content": consolidated_prompt})
            try:
                final_content, final_meta = call_persona(or_key, persona_systems[pk], hist, max_tokens=500)
            except Exception as e:
                print(f"[B] consolidated fail: {e}", file=sys.stderr); break
            logger.log({
                "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                "persona": pk, "character": assignment[pk], "role": "persona-final-consolidated",
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": final_meta.get("cached_tokens", 0),
                "input_tokens_uncached": max(0, final_meta["prompt_tokens"] - final_meta.get("cached_tokens", 0)),
                "output_tokens": final_meta["completion_tokens"], "cost_usd": round(final_meta["cost"], 6),
                "rag_modules": [], "rag_bytes_estimate": 0,
                "history_tokens_estimate": final_meta["prompt_tokens"],
                "turn_wallclock_s": final_meta["turn_wallclock_s"], "cache_hit_ratio": 0.0,
                "content_chars": len(final_content),
            })
            sl_user_content = final_content
        else:
            # Sequential: 2-3 Personas nacheinander
            seq_count = random.choice([2, 3])
            chosen = random.sample(rotation, seq_count)
            parts = []
            for pk in chosen:
                hist = persona_histories[pk][:]
                seq_prompt = (
                    f"Spielleitung sagte:\n{sl_content}\n\n"
                    f"Absprache R2:\n{round2_text}\n\n"
                    f"FINAL — du sprichst EINZELN zur Spielleitung. Kurze Aktion/Ansage."
                )
                hist.append({"role": "user", "content": seq_prompt})
                try:
                    c, m = call_persona(or_key, persona_systems[pk], hist, max_tokens=250)
                except Exception as e:
                    c, m = f"[error {e}]", {"prompt_tokens":0,"completion_tokens":0,"cost":0,"turn_wallclock_s":0,"cached_tokens":0}
                parts.append(f"**{players[pk]['name']} ({characters[assignment[pk]]['name']}):** {c}")
                logger.log({
                    "session_tag": session_tag, "turn": turn_idx, "phase": phase,
                    "persona": pk, "character": assignment[pk], "role": "persona-final-sequential",
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": m.get("cached_tokens", 0),
                    "input_tokens_uncached": max(0, m["prompt_tokens"] - m.get("cached_tokens", 0)),
                    "output_tokens": m["completion_tokens"], "cost_usd": round(m["cost"], 6),
                    "rag_modules": [], "rag_bytes_estimate": 0,
                    "history_tokens_estimate": m["prompt_tokens"],
                    "turn_wallclock_s": m["turn_wallclock_s"], "cache_hit_ratio": 0.0,
                    "content_chars": len(c),
                })
            sl_user_content = "\n\n".join(parts)

        # Update Histories
        for pk in rotation:
            persona_histories[pk].append({"role": "user", "content": f"Spielleitung sagte:\n{sl_content}"})
            persona_histories[pk].append({"role": "assistant", "content":
                round1_msgs.get(pk, "") + "\n[later]: " + round2_msgs.get(pk, "")})

        sl_messages.append({"role": "assistant", "content": sl_content})
        sl_messages.append({"role": "user", "content": sl_user_content})

        with (outdir / "persona-content-B.md").open("a") as f:
            f.write(f"\n\n--- Turn {turn_idx} Final [{mode}] ---\n{sl_user_content}\n")

        # Cost-Watchdog
        if logger.total_cost > 3.5:
            print(f"[B] Cost watchdog triggered at ${logger.total_cost:.3f}", file=sys.stderr)
            break

    summary = logger.summary()
    (outdir / "summary-B-group.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["A", "B", "C"])
    ap.add_argument("--player", default=None)
    ap.add_argument("--character", default=None)
    ap.add_argument("--turns", type=int, default=15)
    ap.add_argument("--save-in", type=Path, default=None)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--personas-yaml", type=Path, required=True)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    personas_data = yaml.safe_load(args.personas_yaml.read_text())

    owui_key = load_owui_key()
    or_key = load_or_key()

    session_tag = f"{args.phase}-{args.character or 'group'}-{uuid.uuid4().hex[:6]}"

    pid_extra = f"{args.character or 'group'}"
    with PIDFile(args.phase, pid_extra):
        if args.phase == "B":
            summary = run_group(
                owui_key=owui_key, or_key=or_key,
                personas_data=personas_data, turns=args.turns,
                outdir=args.outdir, session_tag=session_tag,
            )
        else:
            if not args.character:
                raise SystemExit("Phase A/C requires --character")
            # player_key aus assignment ableiten
            inverse = {v: k for k, v in personas_data["assignment"].items()}
            player_key = args.player or inverse[args.character]
            summary = run_solo(
                owui_key=owui_key, or_key=or_key,
                phase=args.phase, player_key=player_key,
                character_key=args.character,
                personas_data=personas_data, turns=args.turns,
                outdir=args.outdir, session_tag=session_tag,
                save_in=args.save_in,
            )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
